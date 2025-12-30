"""
Trip service for Travel Diary feature.

Business logic for trip creation, publication, and management.
Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013
"""

import io
import logging
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO, List, Optional

from PIL import Image
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.trip import Tag, Trip, TripDifficulty, TripLocation, TripPhoto, TripStatus, TripTag
from src.schemas.trip import LocationInput, TripCreateRequest
from src.services.stats_service import StatsService
from src.utils.html_sanitizer import sanitize_html

logger = logging.getLogger(__name__)


class TripService:
    """
    Trip service for managing travel diary entries.

    Handles trip CRUD operations, tag management, and publication workflow.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize trip service.

        Args:
            db: Database session
        """
        self.db = db

    async def create_trip(self, user_id: str, data: TripCreateRequest) -> Trip:
        """
        Create a new trip.

        Creates trip with status=DRAFT, processes tags, locations, and sanitizes HTML.

        Args:
            user_id: ID of user creating the trip
            data: Trip creation request data

        Returns:
            Created Trip instance

        Raises:
            ValueError: If validation fails
        """
        # Sanitize HTML content in description
        sanitized_description = sanitize_html(data.description)

        # Map difficulty string to enum (if provided)
        difficulty_enum = TripDifficulty(data.difficulty) if data.difficulty else None

        # Create trip entity
        trip = Trip(
            user_id=user_id,
            title=data.title,
            description=sanitized_description,
            status=TripStatus.DRAFT,
            start_date=data.start_date,
            end_date=data.end_date,
            distance_km=data.distance_km,
            difficulty=difficulty_enum,
        )

        self.db.add(trip)
        await self.db.flush()  # Get trip_id

        # Process tags
        if data.tags:
            await self._process_tags(trip, data.tags)

        # Process locations
        if data.locations:
            await self._process_locations(trip, data.locations)

        await self.db.commit()
        await self.db.refresh(trip)

        # Load relationships for response
        await self._load_trip_relationships(trip)

        logger.info(f"Created trip {trip.trip_id} for user {user_id}")
        return trip

    async def get_trip(self, trip_id: str, current_user_id: Optional[str] = None) -> Trip:
        """
        Get trip by ID.

        Enforces visibility rules:
        - Published trips: visible to everyone
        - Draft trips: only visible to owner

        Args:
            trip_id: Trip identifier
            current_user_id: ID of user requesting the trip (None for public access)

        Returns:
            Trip instance

        Raises:
            ValueError: If trip not found or access denied
        """
        # Query trip with relationships
        result = await self.db.execute(
            select(Trip)
            .where(Trip.trip_id == trip_id)
            .options(
                selectinload(Trip.photos),
                selectinload(Trip.locations),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
            )
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        # Check visibility
        if trip.status == TripStatus.DRAFT:
            # Draft trips only visible to owner
            if not current_user_id or trip.user_id != current_user_id:
                raise PermissionError("No tienes permiso para ver este viaje en borrador")

        logger.info(f"Retrieved trip {trip_id}")
        return trip

    async def publish_trip(self, trip_id: str, user_id: str) -> Trip:
        """
        Publish a draft trip.

        Validates trip meets publication requirements:
        - Title present and non-empty
        - Description >= 50 characters
        - Start date present

        Updates user statistics on first publication.

        Args:
            trip_id: Trip identifier
            user_id: ID of user publishing the trip (must be owner)

        Returns:
            Published Trip instance

        Raises:
            ValueError: If trip not found or validation fails
            PermissionError: If user is not the trip owner
        """
        # Get trip with photos for stats update
        result = await self.db.execute(
            select(Trip)
            .where(Trip.trip_id == trip_id)
            .options(selectinload(Trip.photos), selectinload(Trip.locations))
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        # Check ownership
        if trip.user_id != user_id:
            raise PermissionError("No tienes permiso para publicar este viaje")

        # Validate publication requirements
        if not trip.title or len(trip.title.strip()) == 0:
            raise ValueError("El título es requerido para publicar el viaje")

        if not trip.description or len(trip.description.strip()) < 50:
            raise ValueError(
                "La descripción debe tener al menos 50 caracteres para publicar el viaje"
            )

        if not trip.start_date:
            raise ValueError("La fecha de inicio es requerida para publicar el viaje")

        # Publish trip (idempotent - if already published, keep original published_at)
        was_draft = trip.status == TripStatus.DRAFT

        if was_draft:
            # Capture data for stats update BEFORE committing (while relationships are loaded)
            distance_km = trip.distance_km or 0.0
            photos_count = len(trip.photos)
            trip_date = trip.start_date

            # Extract country code from first location if available
            country_code = "ES"  # Default to Spain
            if trip.locations and len(trip.locations) > 0:
                # TODO: In future, extract actual country code from geocoded location
                # For now, we use a default value
                country_code = "ES"

            # Update trip status
            trip.status = TripStatus.PUBLISHED
            trip.published_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(trip)

            # T036: Update user statistics on first publication
            stats_service = StatsService(self.db)
            await stats_service.update_stats_on_trip_publish(
                user_id=user_id,
                distance_km=distance_km,
                country_code=country_code,
                photos_count=photos_count,
                trip_date=trip_date,
            )

            logger.info(f"Published trip {trip_id} and updated user stats")
        else:
            logger.info(f"Trip {trip_id} already published (idempotent)")

        return trip

    async def _process_tags(self, trip: Trip, tag_names: list[str]) -> None:
        """
        Process tags for trip.

        Creates new tags or reuses existing ones (case-insensitive).
        Updates tag usage_count.

        Args:
            trip: Trip instance
            tag_names: List of tag names
        """
        # Deduplicate tags (case-insensitive)
        unique_tags = {}
        for tag_name in tag_names:
            normalized = tag_name.lower().strip()
            if normalized not in unique_tags:
                unique_tags[normalized] = tag_name.strip()

        # Process each unique tag
        for normalized, display_name in unique_tags.items():
            # Check if tag exists
            result = await self.db.execute(select(Tag).where(Tag.normalized == normalized))
            tag = result.scalar_one_or_none()

            if tag:
                # Tag exists - increment usage count
                tag.usage_count += 1
            else:
                # Create new tag
                tag = Tag(name=display_name, normalized=normalized, usage_count=1)
                self.db.add(tag)
                await self.db.flush()  # Get tag_id

            # Create trip-tag association
            trip_tag = TripTag(trip_id=trip.trip_id, tag_id=tag.tag_id)
            self.db.add(trip_tag)

        logger.debug(f"Processed {len(unique_tags)} tags for trip {trip.trip_id}")

    async def _process_locations(self, trip: Trip, locations: list[LocationInput]) -> None:
        """
        Process locations for trip.

        Creates TripLocation entities with sequence ordering.

        Args:
            trip: Trip instance
            locations: List of location inputs
        """
        for sequence, location_data in enumerate(locations):
            location = TripLocation(
                trip_id=trip.trip_id,
                name=location_data.name,
                # Note: country field is not in TripLocation model (only name)
                # Geocoding will be added in future phases
                sequence=sequence,
            )
            self.db.add(location)

        logger.debug(f"Processed {len(locations)} locations for trip {trip.trip_id}")

    async def _load_trip_relationships(self, trip: Trip) -> None:
        """
        Load trip relationships for response serialization.

        Uses selectinload to eagerly load all relationships in a single query,
        preventing N+1 query issues.

        Args:
            trip: Trip instance
        """
        # Re-query trip with eager loading of all relationships
        result = await self.db.execute(
            select(Trip)
            .where(Trip.trip_id == trip.trip_id)
            .options(
                selectinload(Trip.photos),
                selectinload(Trip.locations),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
            )
        )
        loaded_trip = result.scalar_one()

        # Update current trip instance with loaded relationships
        trip.photos = loaded_trip.photos
        trip.locations = loaded_trip.locations
        trip.trip_tags = loaded_trip.trip_tags

    async def upload_photo(
        self,
        trip_id: str,
        user_id: str,
        photo_file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> TripPhoto:
        """
        Upload a photo to trip.

        Validates photo format, checks photo limit (max 20), processes image
        (resize, thumbnail generation), and saves to storage.

        Args:
            trip_id: Trip identifier
            user_id: User uploading the photo (must be trip owner)
            photo_file: Photo file binary data
            filename: Original filename
            content_type: MIME type (image/jpeg, image/png, image/webp)

        Returns:
            TripPhoto instance

        Raises:
            ValueError: If trip not found, photo limit exceeded, or invalid format
            PermissionError: If user is not trip owner

        Functional Requirements: FR-009, FR-010, FR-011
        """
        # Get trip and verify ownership
        result = await self.db.execute(
            select(Trip).where(Trip.trip_id == trip_id).options(selectinload(Trip.photos))
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        if trip.user_id != user_id:
            raise PermissionError("No tienes permiso para subir fotos a este viaje")

        # Check photo limit (max 20)
        photo_count = len(trip.photos)
        if photo_count >= 20:
            raise ValueError("Has alcanzado el límite de 20 fotos por viaje")

        # Validate content type
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if content_type not in allowed_types:
            raise ValueError("Formato de archivo no soportado. Usa JPG, PNG o WebP")

        # Read image and validate
        try:
            img = Image.open(photo_file)
            img.verify()  # Verify it's actually an image
            photo_file.seek(0)  # Reset file pointer after verify
            img = Image.open(photo_file)  # Re-open after verify
        except Exception:
            raise ValueError("El archivo no es una imagen válida")

        # Convert RGBA to RGB if needed (for JPEG)
        if img.mode == "RGBA":
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = rgb_img

        # Generate unique filename
        file_uuid = str(uuid.uuid4())
        ext = "jpg"  # Always save as JPEG for consistency

        # Create storage directory: storage/trip_photos/{year}/{month}/{trip_id}/
        now = datetime.now(UTC)
        year = now.strftime("%Y")
        month = now.strftime("%m")
        storage_dir = Path("storage/trip_photos") / year / month / trip_id
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Resize and save optimized version (max 1200px width)
        optimized_img = img.copy()
        if optimized_img.width > 1200:
            ratio = 1200 / optimized_img.width
            new_height = int(optimized_img.height * ratio)
            optimized_img = optimized_img.resize((1200, new_height), Image.Resampling.LANCZOS)

        optimized_path = storage_dir / f"{file_uuid}_optimized.{ext}"
        optimized_img.save(optimized_path, format="JPEG", quality=85, optimize=True)

        # Create thumbnail (400x400px)
        thumb_img = img.copy()
        thumb_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        thumb_path = storage_dir / f"{file_uuid}_thumb.{ext}"
        thumb_img.save(thumb_path, format="JPEG", quality=80, optimize=True)

        # Get file size from optimized version
        file_size = optimized_path.stat().st_size

        # Calculate next order value (last photo's order + 1)
        # Use a query to get the current max order (avoid cached relationship issues)
        result = await self.db.execute(
            select(func.max(TripPhoto.order)).where(TripPhoto.trip_id == trip_id)
        )
        max_order = result.scalar()
        next_order = (max_order + 1) if max_order is not None else 0

        # Create database record
        photo = TripPhoto(
            trip_id=trip_id,
            photo_url=f"/storage/trip_photos/{year}/{month}/{trip_id}/{file_uuid}_optimized.{ext}",
            thumb_url=f"/storage/trip_photos/{year}/{month}/{trip_id}/{file_uuid}_thumb.{ext}",
            order=next_order,
            file_size=file_size,
            width=optimized_img.width,
            height=optimized_img.height,
        )

        self.db.add(photo)
        await self.db.commit()
        await self.db.refresh(photo)

        # Update user stats if trip is published (increment photo count)
        if trip.status == TripStatus.PUBLISHED:
            await self._update_photo_count_in_stats(user_id, increment=1)
            logger.info(f"Incremented photo count in stats for user {user_id}")

        logger.info(f"Uploaded photo {photo.photo_id} to trip {trip_id}")
        return photo

    async def delete_photo(self, trip_id: str, photo_id: str, user_id: str) -> dict:
        """
        Delete a photo from trip.

        Removes photo from database and deletes files from storage.
        Reorders remaining photos to maintain sequential order.

        Args:
            trip_id: Trip identifier
            photo_id: Photo identifier
            user_id: User deleting the photo (must be trip owner)

        Returns:
            Dict with success message

        Raises:
            ValueError: If trip or photo not found
            PermissionError: If user is not trip owner

        Functional Requirement: FR-013
        """
        # Get trip and verify ownership
        result = await self.db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        if trip.user_id != user_id:
            raise PermissionError("No tienes permiso para eliminar fotos de este viaje")

        # Get photo
        result = await self.db.execute(select(TripPhoto).where(TripPhoto.photo_id == photo_id))
        photo = result.scalar_one_or_none()

        if not photo:
            raise ValueError("Foto no encontrada")

        if photo.trip_id != trip_id:
            raise ValueError("La foto no pertenece a este viaje")

        # Delete physical files
        try:
            # Convert URL to filesystem path
            photo_path = Path(photo.photo_url.lstrip("/"))
            thumb_path = Path(photo.thumb_url.lstrip("/"))

            if photo_path.exists():
                photo_path.unlink()
            if thumb_path.exists():
                thumb_path.unlink()

            logger.info(f"Deleted photo files for {photo_id}")
        except Exception as e:
            logger.warning(f"Failed to delete photo files for {photo_id}: {e}")
            # Continue with database deletion even if file deletion fails

        # Remember the order of deleted photo
        deleted_order = photo.order

        # Delete from database
        await self.db.delete(photo)
        await self.db.flush()

        # Reorder remaining photos to maintain sequential order (no gaps)
        result = await self.db.execute(
            select(TripPhoto)
            .where(TripPhoto.trip_id == trip_id, TripPhoto.order > deleted_order)
            .order_by(TripPhoto.order)
        )
        remaining_photos = result.scalars().all()

        for remaining_photo in remaining_photos:
            remaining_photo.order -= 1

        await self.db.commit()

        # Update user stats if trip is published (decrement photo count)
        if trip.status == TripStatus.PUBLISHED:
            await self._update_photo_count_in_stats(user_id, increment=-1)
            logger.info(f"Decremented photo count in stats for user {user_id}")

        logger.info(f"Deleted photo {photo_id} from trip {trip_id}, reordered {len(remaining_photos)} remaining photos")
        return {"message": "Foto eliminada correctamente"}

    async def reorder_photos(
        self, trip_id: str, user_id: str, photo_order: List[str]
    ) -> dict:
        """
        Reorder photos in trip gallery.

        Updates the order field for each photo based on provided photo_ids list.

        Args:
            trip_id: Trip identifier
            user_id: User reordering photos (must be trip owner)
            photo_order: List of photo_ids in desired order

        Returns:
            Dict with success message

        Raises:
            ValueError: If trip not found or photo_ids don't match trip's photos
            PermissionError: If user is not trip owner

        Functional Requirement: FR-012
        """
        # Get trip and verify ownership
        result = await self.db.execute(
            select(Trip).where(Trip.trip_id == trip_id).options(selectinload(Trip.photos))
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        if trip.user_id != user_id:
            raise PermissionError("No tienes permiso para reordenar fotos de este viaje")

        # Validate photo_order contains all trip's photos
        trip_photo_ids = {photo.photo_id for photo in trip.photos}
        provided_photo_ids = set(photo_order)

        # Check if counts match first
        if len(provided_photo_ids) != len(trip_photo_ids):
            raise ValueError(
                f"Cantidad inválida de fotos. El viaje tiene {len(trip_photo_ids)} fotos pero se proporcionaron {len(provided_photo_ids)}"
            )

        # Check if all IDs are valid
        if trip_photo_ids != provided_photo_ids:
            raise ValueError(
                "ID de foto inválido: la lista contiene fotos que no pertenecen a este viaje"
            )

        # Update order for each photo
        for new_order, photo_id in enumerate(photo_order):
            result = await self.db.execute(
                select(TripPhoto).where(TripPhoto.photo_id == photo_id)
            )
            photo = result.scalar_one()
            photo.order = new_order

        await self.db.commit()

        logger.info(f"Reordered {len(photo_order)} photos for trip {trip_id}")
        return {"message": "Fotos reordenadas correctamente"}

    async def update_trip(
        self, trip_id: str, user_id: str, update_data: dict
    ) -> Trip:
        """
        Update an existing trip.

        T073: Supports partial updates with HTML sanitization.
        Updates user stats if published trip's distance, country, or photo count changes.

        Args:
            trip_id: Trip identifier
            user_id: User updating the trip (must be owner)
            update_data: Dictionary with fields to update

        Returns:
            Updated Trip instance

        Raises:
            ValueError: If trip not found or validation fails
            PermissionError: If user is not the trip owner
        """
        # Get trip with relationships for stats calculation
        result = await self.db.execute(
            select(Trip)
            .where(Trip.trip_id == trip_id)
            .options(selectinload(Trip.photos), selectinload(Trip.locations))
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        if trip.user_id != user_id:
            raise PermissionError("No tienes permiso para editar este viaje")

        # Store old values for stats update
        was_published = trip.status == TripStatus.PUBLISHED
        old_distance_km = trip.distance_km or 0.0
        old_photos_count = len(trip.photos)
        old_country_code = "ES"  # TODO: Extract from locations when geocoding is implemented

        # Apply updates with sanitization
        if "title" in update_data:
            trip.title = update_data["title"]

        if "description" in update_data:
            trip.description = sanitize_html(update_data["description"])

        if "start_date" in update_data:
            trip.start_date = update_data["start_date"]

        if "end_date" in update_data:
            trip.end_date = update_data["end_date"]

        if "distance_km" in update_data:
            trip.distance_km = update_data["distance_km"]

        if "difficulty" in update_data:
            trip.difficulty = (
                TripDifficulty(update_data["difficulty"])
                if update_data["difficulty"]
                else None
            )

        # Update tags if provided
        if "tags" in update_data:
            # Remove old tag associations
            await self.db.execute(
                select(TripTag).where(TripTag.trip_id == trip_id)
            )
            # Process new tags
            await self._process_tags(trip, update_data["tags"])

        # Update locations if provided
        if "locations" in update_data:
            # Remove old locations
            await self.db.execute(
                select(TripLocation).where(TripLocation.trip_id == trip_id)
            )
            # Process new locations
            await self._process_locations(trip, update_data["locations"])

        trip.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(trip)

        # T162: Update stats if published trip was edited
        if was_published:
            # Reload to get updated photos count
            result = await self.db.execute(
                select(Trip)
                .where(Trip.trip_id == trip_id)
                .options(selectinload(Trip.photos), selectinload(Trip.locations))
            )
            updated_trip = result.scalar_one()

            new_distance_km = updated_trip.distance_km or 0.0
            new_photos_count = len(updated_trip.photos)
            new_country_code = "ES"  # TODO: Extract from locations

            stats_service = StatsService(self.db)
            await stats_service.update_stats_on_trip_edit(
                user_id=user_id,
                old_distance_km=old_distance_km,
                new_distance_km=new_distance_km,
                old_country_code=old_country_code,
                new_country_code=new_country_code,
                old_photos_count=old_photos_count,
                new_photos_count=new_photos_count,
            )
            logger.info(f"Updated trip {trip_id} and user stats")

        await self._load_trip_relationships(trip)
        logger.info(f"Updated trip {trip_id}")
        return trip

    async def delete_trip(self, trip_id: str, user_id: str) -> dict:
        """
        Delete a trip.

        T074-T075: Cascade deletes photos, tags, locations. Updates user stats if published.

        Args:
            trip_id: Trip identifier
            user_id: User deleting the trip (must be owner)

        Returns:
            Dict with success message

        Raises:
            ValueError: If trip not found
            PermissionError: If user is not the trip owner
        """
        # Get trip with all relationships for cleanup
        result = await self.db.execute(
            select(Trip)
            .where(Trip.trip_id == trip_id)
            .options(selectinload(Trip.photos), selectinload(Trip.locations))
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        if trip.user_id != user_id:
            raise PermissionError("No tienes permiso para eliminar este viaje")

        # Store data for stats update before deletion
        was_published = trip.status == TripStatus.PUBLISHED
        distance_km = trip.distance_km or 0.0
        photos_count = len(trip.photos)
        country_code = "ES"  # TODO: Extract from locations

        # Delete physical photo files
        for photo in trip.photos:
            try:
                photo_path = Path(photo.photo_url.lstrip("/"))
                thumb_path = Path(photo.thumb_url.lstrip("/"))

                if photo_path.exists():
                    photo_path.unlink()
                if thumb_path.exists():
                    thumb_path.unlink()

                logger.debug(f"Deleted photo files for {photo.photo_id}")
            except Exception as e:
                logger.warning(f"Failed to delete photo files for {photo.photo_id}: {e}")
                # Continue with deletion even if file cleanup fails

        # Delete trip (cascade will handle photos, tags, locations via SQLAlchemy)
        await self.db.delete(trip)
        await self.db.commit()

        # T163: Update stats if published trip was deleted
        if was_published:
            stats_service = StatsService(self.db)
            await stats_service.update_stats_on_trip_delete(
                user_id=user_id,
                distance_km=distance_km,
                country_code=country_code,
                photos_count=photos_count,
            )
            logger.info(f"Deleted trip {trip_id} and updated user stats")

        logger.info(f"Deleted trip {trip_id}")
        return {"message": "Viaje eliminado correctamente"}

    async def _update_photo_count_in_stats(self, user_id: str, increment: int) -> None:
        """
        Update total_photos count in user stats.

        Helper method to increment/decrement photo count when photos are added/removed
        from published trips.

        Args:
            user_id: User ID
            increment: Number to add (positive) or subtract (negative) from total_photos
        """
        from src.models.stats import UserStats

        # Get user stats
        result = await self.db.execute(
            select(UserStats).where(UserStats.user_id == user_id)
        )
        stats = result.scalar_one_or_none()

        if stats:
            # Update photo count (ensure non-negative)
            stats.total_photos = max(0, stats.total_photos + increment)
            stats.updated_at = datetime.now(UTC)
            await self.db.commit()
            logger.debug(f"Updated photo count for user {user_id}: {increment:+d}")
        else:
            logger.warning(f"Stats not found for user {user_id}, cannot update photo count")
