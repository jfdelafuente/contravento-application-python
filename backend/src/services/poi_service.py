"""
POI (Point of Interest) service for GPS Routes feature.

Feature 003 - User Story 4: Points of Interest along routes

Business logic for POI creation, management, and filtering.
Functional Requirements: FR-029
Success Criteria: SC-029, SC-030, SC-031
"""

import logging
import uuid
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import aiofiles
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.models.poi import PointOfInterest
from src.models.trip import Trip
from src.schemas.poi import POICreateInput, POITypeEnum, POIUpdateInput
from src.utils.file_storage import validate_photo

logger = logging.getLogger(__name__)

# Business rule: Maximum POIs per trip (FR-011 from Feature 017)
MAX_POIS_PER_TRIP = 6


class POIService:
    """
    POI service for managing Points of Interest along routes.

    Handles POI CRUD operations, validation, and filtering.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize POI service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_poi(
        self,
        trip_id: str,
        user_id: str,
        data: POICreateInput,
    ) -> PointOfInterest:
        """
        Create a new POI for a trip.

        FR-029: Users can add POIs to published trips
        SC-029: Maximum 20 POIs per trip

        Args:
            trip_id: ID of parent trip
            user_id: ID of user creating the POI (must be trip owner)
            data: POI creation data

        Returns:
            Created PointOfInterest instance

        Raises:
            ValueError: If validation fails
            PermissionError: If user is not trip owner
        """
        # Verify trip exists and user is owner
        await self._get_trip_with_ownership_check(trip_id, user_id)

        # FR-029: POIs can be added to trips by their owners
        # - PUBLISHED trips: Normal flow (trip is public)
        # - DRAFT trips: Wizard flow (owner can add POIs before publishing)
        # Ownership already verified by _get_trip_with_ownership_check above
        # Note: Removed status check to support wizard workflow (Feature 017)

        # SC-029: Enforce maximum 20 POIs per trip
        current_poi_count = await self._get_trip_poi_count(trip_id)
        if current_poi_count >= MAX_POIS_PER_TRIP:
            raise ValueError(f"Máximo {MAX_POIS_PER_TRIP} POIs permitidos por viaje")

        # Create POI entity
        poi = PointOfInterest(
            trip_id=trip_id,
            name=data.name,
            description=data.description,
            poi_type=data.poi_type,
            latitude=data.latitude,
            longitude=data.longitude,
            distance_from_start_km=data.distance_from_start_km,
            photo_url=data.photo_url,
            sequence=data.sequence,
        )

        self.db.add(poi)
        await self.db.commit()
        await self.db.refresh(poi)

        logger.info(
            f"Created POI {poi.poi_id} ({poi.poi_type.value}) "
            f"for trip {trip_id} by user {user_id}"
        )
        return poi

    async def get_poi(self, poi_id: str) -> PointOfInterest:
        """
        Get POI by ID.

        Args:
            poi_id: POI identifier

        Returns:
            PointOfInterest instance

        Raises:
            ValueError: If POI not found
        """
        result = await self.db.execute(
            select(PointOfInterest)
            .where(PointOfInterest.poi_id == poi_id)
            .options(selectinload(PointOfInterest.trip))
        )
        poi = result.scalar_one_or_none()

        if not poi:
            raise ValueError("Punto de interés no encontrado")

        return poi

    async def get_trip_pois(
        self,
        trip_id: str,
        poi_type: POITypeEnum | None = None,
    ) -> list[PointOfInterest]:
        """
        Get all POIs for a trip, optionally filtered by type.

        SC-030: POIs can be filtered by type

        Args:
            trip_id: Trip identifier
            poi_type: Optional type filter (viewpoint, town, water, etc.)

        Returns:
            List of POI instances ordered by sequence
        """
        query = select(PointOfInterest).where(PointOfInterest.trip_id == trip_id)

        # Apply type filter if provided
        if poi_type:
            query = query.where(PointOfInterest.poi_type == poi_type)

        # Order by sequence
        query = query.order_by(PointOfInterest.sequence)

        result = await self.db.execute(query)
        pois = result.scalars().all()

        logger.info(
            f"Retrieved {len(pois)} POIs for trip {trip_id}"
            + (f" (type={poi_type.value})" if poi_type else "")
        )
        return list(pois)

    async def update_poi(
        self,
        poi_id: str,
        user_id: str,
        data: POIUpdateInput,
    ) -> PointOfInterest:
        """
        Update an existing POI.

        Args:
            poi_id: POI identifier
            user_id: ID of user updating the POI (must be trip owner)
            data: POI update data (only provided fields will be updated)

        Returns:
            Updated PointOfInterest instance

        Raises:
            ValueError: If POI not found
            PermissionError: If user is not trip owner
        """
        # Get POI with trip for ownership check
        poi = await self.get_poi(poi_id)

        # Verify user is trip owner
        await self._get_trip_with_ownership_check(poi.trip_id, user_id)

        # Update only provided fields
        # Use model_fields_set to detect fields that were explicitly provided (including null values)
        fields_set = data.model_fields_set

        if "name" in fields_set:
            poi.name = data.name
        if "description" in fields_set:
            poi.description = data.description
        if "poi_type" in fields_set:
            poi.poi_type = data.poi_type
        if "latitude" in fields_set:
            poi.latitude = data.latitude
        if "longitude" in fields_set:
            poi.longitude = data.longitude
        if "distance_from_start_km" in fields_set:
            poi.distance_from_start_km = data.distance_from_start_km
        if "photo_url" in fields_set:
            # Explicitly provided (can be null to delete, or a new URL)
            if data.photo_url is None:
                poi.photo_url = None  # Delete photo
            elif not data.photo_url.startswith("/storage/"):
                poi.photo_url = f"/storage/{data.photo_url.lstrip('/')}"
            else:
                poi.photo_url = data.photo_url
        if "sequence" in fields_set:
            poi.sequence = data.sequence

        await self.db.commit()
        await self.db.refresh(poi)

        logger.info(f"Updated POI {poi_id} by user {user_id}")
        return poi

    async def delete_poi(self, poi_id: str, user_id: str) -> None:
        """
        Delete a POI.

        Args:
            poi_id: POI identifier
            user_id: ID of user deleting the POI (must be trip owner)

        Raises:
            ValueError: If POI not found
            PermissionError: If user is not trip owner
        """
        # Get POI with trip for ownership check
        poi = await self.get_poi(poi_id)

        # Verify user is trip owner
        await self._get_trip_with_ownership_check(poi.trip_id, user_id)

        # Delete POI
        await self.db.execute(delete(PointOfInterest).where(PointOfInterest.poi_id == poi_id))
        await self.db.commit()

        logger.info(f"Deleted POI {poi_id} from trip {poi.trip_id} by user {user_id}")

    async def reorder_pois(
        self,
        trip_id: str,
        user_id: str,
        poi_ids: list[str],
    ) -> list[PointOfInterest]:
        """
        Reorder POIs for a trip.

        FR-029: Users can reorder POIs without affecting GPX route

        Args:
            trip_id: Trip identifier
            user_id: ID of user reordering POIs (must be trip owner)
            poi_ids: Ordered list of POI IDs (must include all trip POIs)

        Returns:
            List of reordered POI instances

        Raises:
            ValueError: If validation fails (missing/extra POIs)
            PermissionError: If user is not trip owner
        """
        # Verify user is trip owner
        await self._get_trip_with_ownership_check(trip_id, user_id)

        # Get all POIs for the trip
        current_pois = await self.get_trip_pois(trip_id)
        current_poi_ids: set[str] = {poi.poi_id for poi in current_pois}

        # Validate: Must include all POIs (no additions or omissions)
        provided_poi_ids: set[str] = set(poi_ids)
        if provided_poi_ids != current_poi_ids:
            missing: set[str] = current_poi_ids - provided_poi_ids
            extra: set[str] = provided_poi_ids - current_poi_ids
            error_parts = []
            if missing:
                error_parts.append(f"faltan: {missing}")
            if extra:
                error_parts.append(f"sobran: {extra}")
            raise ValueError(
                f"La lista de POIs no coincide con los POIs del viaje. {', '.join(error_parts)}"
            )

        # Update sequence for each POI
        poi_map: dict[str, PointOfInterest] = {poi.poi_id: poi for poi in current_pois}
        for new_sequence, poi_id in enumerate(poi_ids):
            poi = poi_map[poi_id]
            poi.sequence = new_sequence

        await self.db.commit()

        # Fetch reordered POIs
        reordered_pois = await self.get_trip_pois(trip_id)

        logger.info(f"Reordered {len(reordered_pois)} POIs for trip {trip_id} by user {user_id}")
        return reordered_pois

    async def upload_photo(
        self,
        poi_id: str,
        user_id: str,
        photo_file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> PointOfInterest:
        """
        Upload a photo for a POI.

        FR-010 (Feature 017): POIs can have photos (max 5MB per photo)

        Args:
            poi_id: POI identifier
            user_id: ID of user uploading the photo (must be trip owner)
            photo_file: Photo file content
            filename: Original filename
            content_type: MIME type of the photo

        Returns:
            Updated PointOfInterest instance with photo_url

        Raises:
            ValueError: If validation fails
            PermissionError: If user is not trip owner
        """
        # Get POI with trip for ownership check
        poi = await self.get_poi(poi_id)

        # Verify user is trip owner
        await self._get_trip_with_ownership_check(poi.trip_id, user_id)

        # Validate photo (max 5MB for POIs)
        photo_bytes = BytesIO(photo_file.read())
        validate_photo(photo_bytes, content_type, max_size_mb=5)

        # Generate storage path
        storage_path = self._get_poi_photo_storage_path(poi_id, filename)
        full_path = Path(settings.storage_path) / storage_path

        # Create directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Save photo to disk
        photo_bytes.seek(0)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(photo_bytes.read())

        # Update POI with photo URL (include /storage prefix for static file serving)
        poi.photo_url = f"/storage/{storage_path}"

        await self.db.commit()
        await self.db.refresh(poi)

        logger.info(f"Uploaded photo for POI {poi_id} by user {user_id}: {storage_path}")
        return poi

    # ========================================================================
    # Helper methods
    # ========================================================================

    def _get_poi_photo_storage_path(self, poi_id: str, filename: str) -> str:
        """
        Generate storage path for a POI's photo.

        Path structure: poi_photos/{year}/{month}/{poi_id}_{uuid}.{ext}

        Args:
            poi_id: POI identifier
            filename: Original filename (extension will be extracted)

        Returns:
            Relative path for storing the file

        Example:
            >>> _get_poi_photo_storage_path("poi123", "photo.jpg")
            'poi_photos/2026/01/poi123_a1b2c3d4.jpg'
        """
        now = datetime.now(UTC)
        year = now.strftime("%Y")
        month = now.strftime("%m")

        # Generate unique filename
        file_ext = Path(filename).suffix or ".jpg"
        unique_id = uuid.uuid4().hex[:8]
        new_filename = f"{poi_id}_{unique_id}{file_ext}"

        # Create path: poi_photos/YYYY/MM/poi_id_uuid.ext
        relative_path = f"poi_photos/{year}/{month}/{new_filename}"

        return relative_path

    async def _get_trip_with_ownership_check(self, trip_id: str, user_id: str) -> Trip:
        """
        Get trip and verify user is the owner.

        Args:
            trip_id: Trip identifier
            user_id: User identifier

        Returns:
            Trip instance

        Raises:
            ValueError: If trip not found
            PermissionError: If user is not trip owner
        """
        result = await self.db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        if trip.user_id != user_id:
            raise PermissionError("Solo el autor del viaje puede gestionar sus POIs")

        return trip

    async def _get_trip_poi_count(self, trip_id: str) -> int:
        """
        Get count of POIs for a trip.

        Args:
            trip_id: Trip identifier

        Returns:
            Number of POIs
        """
        result = await self.db.execute(
            select(func.count())
            .select_from(PointOfInterest)
            .where(PointOfInterest.trip_id == trip_id)
        )
        count = result.scalar() or 0
        return int(count)
