"""
POI (Point of Interest) service for GPS Routes feature.

Feature 003 - User Story 4: Points of Interest along routes

Business logic for POI creation, management, and filtering.
Functional Requirements: FR-029
Success Criteria: SC-029, SC-030, SC-031
"""

import logging

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.poi import PointOfInterest
from src.models.trip import Trip, TripStatus
from src.schemas.poi import POICreateInput, POITypeEnum, POIUpdateInput

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
        trip = await self._get_trip_with_ownership_check(trip_id, user_id)

        # FR-029: POIs can only be added to published trips
        if trip.status != TripStatus.PUBLISHED:
            raise ValueError("Solo se pueden añadir POIs a viajes publicados")

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
        if data.name is not None:
            poi.name = data.name
        if data.description is not None:
            poi.description = data.description
        if data.poi_type is not None:
            poi.poi_type = data.poi_type
        if data.latitude is not None:
            poi.latitude = data.latitude
        if data.longitude is not None:
            poi.longitude = data.longitude
        if data.distance_from_start_km is not None:
            poi.distance_from_start_km = data.distance_from_start_km
        if data.photo_url is not None:
            poi.photo_url = data.photo_url
        if data.sequence is not None:
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
        current_poi_ids = {poi.poi_id for poi in current_pois}

        # Validate: Must include all POIs (no additions or omissions)
        provided_poi_ids = set(poi_ids)
        if provided_poi_ids != current_poi_ids:
            missing = current_poi_ids - provided_poi_ids
            extra = provided_poi_ids - current_poi_ids
            error_parts = []
            if missing:
                error_parts.append(f"faltan: {missing}")
            if extra:
                error_parts.append(f"sobran: {extra}")
            raise ValueError(
                f"La lista de POIs no coincide con los POIs del viaje. {', '.join(error_parts)}"
            )

        # Update sequence for each POI
        poi_map = {poi.poi_id: poi for poi in current_pois}
        for new_sequence, poi_id in enumerate(poi_ids):
            poi = poi_map[poi_id]
            poi.sequence = new_sequence

        await self.db.commit()

        # Fetch reordered POIs
        reordered_pois = await self.get_trip_pois(trip_id)

        logger.info(f"Reordered {len(reordered_pois)} POIs for trip {trip_id} by user {user_id}")
        return reordered_pois

    # ========================================================================
    # Helper methods
    # ========================================================================

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
