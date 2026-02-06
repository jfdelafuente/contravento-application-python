"""
Trip service for Travel Diary feature.

Business logic for trip creation, publication, and management.
Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013
"""

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

from PIL import Image
from sqlalchemy import case, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.trip import Tag, Trip, TripDifficulty, TripLocation, TripPhoto, TripStatus, TripTag
from src.models.user import User
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

    async def get_trip(self, trip_id: str, current_user_id: str | None = None) -> Trip:
        """
        Get trip by ID.

        Enforces visibility rules (Feature 013):
        - Draft trips: only visible to owner
        - Published trips with trip_visibility='public': visible to everyone
        - Published trips with trip_visibility='followers': visible to followers and owner
        - Published trips with trip_visibility='private': only visible to owner

        Args:
            trip_id: Trip identifier
            current_user_id: ID of user requesting the trip (None for public access)

        Returns:
            Trip instance

        Raises:
            ValueError: If trip not found
            PermissionError: If access denied due to visibility settings
        """
        # Query trip with relationships (eager load user for visibility check)

        result = await self.db.execute(
            select(Trip)
            .where(Trip.trip_id == trip_id)
            .options(
                selectinload(Trip.photos),
                selectinload(Trip.locations),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
                selectinload(Trip.user).selectinload(
                    User.profile
                ),  # Need user + profile for author info (Feature 004)
                selectinload(Trip.gpx_file),  # Feature 003 - GPS Routes Interactive
            )
        )
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        # Check if user is the owner
        is_owner = current_user_id and trip.user_id == current_user_id

        # Check visibility - Draft trips
        if trip.status == TripStatus.DRAFT:
            if not is_owner:
                raise PermissionError("No tienes permiso para ver este viaje en borrador")
            logger.info(f"Retrieved draft trip {trip_id} (owner access)")

            # Add like_count and is_liked for drafts (Feature 004 - US2)
            # Drafts have 0 likes since they're not published
            trip.like_count = 0
            trip.is_liked = None

            # Add is_following to user object (Feature 004)
            # Owner viewing their own draft, so is_following is None
            trip.user.is_following = None

            return trip

        # Check visibility - Published trips with trip_visibility
        if trip.user.trip_visibility == "private":
            # Private trips: only owner can see
            if not is_owner:
                raise PermissionError("Este viaje es privado y solo el propietario puede verlo")

        elif trip.user.trip_visibility == "followers":
            # Followers-only trips: check if current user follows the owner
            if not is_owner:
                if not current_user_id:
                    raise PermissionError("Debes iniciar sesión para ver este viaje")

                # Check if current user follows trip owner
                from src.models.social import Follow

                follow_result = await self.db.execute(
                    select(Follow).where(
                        Follow.follower_id == current_user_id, Follow.following_id == trip.user_id
                    )
                )
                is_follower = follow_result.scalar_one_or_none() is not None

                if not is_follower:
                    raise PermissionError("Este viaje solo es visible para seguidores del usuario")

        # If we reach here, trip is visible (public, or followers/private with permission)
        logger.info(f"Retrieved published trip {trip_id} (visibility={trip.user.trip_visibility})")

        # Calculate like_count and is_liked (Feature 004 - US2)
        from src.models.like import Like

        # Count likes for this trip
        like_count_result = await self.db.execute(
            select(func.count(Like.id)).where(Like.trip_id == trip_id)
        )
        like_count = like_count_result.scalar() or 0

        # Check if current user has liked this trip
        is_liked = None
        if current_user_id:
            like_result = await self.db.execute(
                select(Like).where(Like.trip_id == trip_id, Like.user_id == current_user_id)
            )
            is_liked = like_result.scalar_one_or_none() is not None

        # Add dynamic attributes to trip object
        trip.like_count = like_count
        trip.is_liked = is_liked

        # Calculate is_following status for trip author (Feature 004)
        # Owner never "follows" themselves
        is_following = None
        if current_user_id and not is_owner:
            from src.models.social import Follow

            follow_result = await self.db.execute(
                select(Follow).where(
                    Follow.follower_id == current_user_id, Follow.following_id == trip.user_id
                )
            )
            is_following = follow_result.scalar_one_or_none() is not None

        # Add is_following to user object (will be used by TripResponse.model_validate)
        trip.user.is_following = is_following

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
        Process locations for trip with optional GPS coordinates.

        Creates TripLocation entities with sequence ordering and coordinates.

        Args:
            trip: Trip instance
            locations: List of location inputs with optional GPS coordinates
        """
        for sequence, location_data in enumerate(locations):
            # Handle both Pydantic objects and dicts
            if isinstance(location_data, dict):
                name = location_data.get("name")
                latitude = location_data.get("latitude")
                longitude = location_data.get("longitude")
            else:
                name = location_data.name
                latitude = location_data.latitude
                longitude = location_data.longitude

            location = TripLocation(
                trip_id=trip.trip_id,
                name=name,
                latitude=latitude,  # Store latitude (nullable)
                longitude=longitude,  # Store longitude (nullable)
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
                selectinload(Trip.user).selectinload(User.profile),
                selectinload(Trip.photos),
                selectinload(Trip.locations),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
                selectinload(Trip.gpx_file),  # Feature 003 - GPS Routes Interactive
            )
        )
        loaded_trip = result.scalar_one()

        # Update current trip instance with loaded relationships
        trip.user = loaded_trip.user
        trip.photos = loaded_trip.photos
        trip.locations = loaded_trip.locations
        trip.trip_tags = loaded_trip.trip_tags
        trip.gpx_file = loaded_trip.gpx_file

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

        # Check photo limit (max 6)
        photo_count = len(trip.photos)
        if photo_count >= 6:
            raise ValueError("Has alcanzado el límite de 6 fotos por viaje")

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

        logger.info(
            f"Deleted photo {photo_id} from trip {trip_id}, reordered {len(remaining_photos)} remaining photos"
        )
        return {"message": "Foto eliminada correctamente"}

    async def reorder_photos(self, trip_id: str, user_id: str, photo_order: list[str]) -> dict:
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
            result = await self.db.execute(select(TripPhoto).where(TripPhoto.photo_id == photo_id))
            photo = result.scalar_one()
            photo.order = new_order

        await self.db.commit()

        logger.info(f"Reordered {len(photo_order)} photos for trip {trip_id}")
        return {"message": "Fotos reordenadas correctamente"}

    async def update_trip(self, trip_id: str, user_id: str, update_data: dict) -> Trip:
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
                TripDifficulty(update_data["difficulty"]) if update_data["difficulty"] else None
            )

        if "is_private" in update_data:
            trip.is_private = update_data["is_private"]

        # Update tags if provided
        if "tags" in update_data:
            # Remove old tag associations
            await self.db.execute(delete(TripTag).where(TripTag.trip_id == trip_id))
            # Process new tags
            await self._process_tags(trip, update_data["tags"])

        # Update locations if provided
        if "locations" in update_data:
            # Remove old locations
            await self.db.execute(delete(TripLocation).where(TripLocation.trip_id == trip_id))
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
        result = await self.db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = result.scalar_one_or_none()

        if stats:
            # Update photo count (ensure non-negative)
            stats.total_photos = max(0, stats.total_photos + increment)
            stats.updated_at = datetime.now(UTC)
            await self.db.commit()
            logger.debug(f"Updated photo count for user {user_id}: {increment:+d}")
        else:
            logger.warning(f"Stats not found for user {user_id}, cannot update photo count")

    async def get_user_trips(
        self,
        user_id: str,
        tag: str | None = None,
        status: TripStatus | None = None,
        is_private: bool | None = None,
        sort_by: str | None = None,
        limit: int = 50,
        offset: int = 0,
        current_user_id: str | None = None,
    ) -> list[Trip]:
        """
        T087: Get user's trips with optional filtering (Feature 013: respects trip_visibility).

        Visibility rules:
        - Owner: can see all their trips (drafts and published, any visibility)
        - Followers: can see published trips with visibility='public' or 'followers'
        - Public: can only see published trips with visibility='public'
        - Draft trips: always filtered unless viewer is owner

        Args:
            user_id: User ID to filter by
            tag: Optional tag name to filter by (case-insensitive)
            status: Optional status to filter by (DRAFT, PUBLISHED)
            is_private: Optional visibility filter (True=private, False=public, None=all)
            sort_by: Optional sort order (default: date-desc)
                - date-desc: Most recent trips first (by start_date, or created_at if no start_date)
                - date-asc: Oldest trips first (by start_date, or created_at if no start_date)
                - distance-desc: Longest trips first
                - distance-asc: Shortest trips first
                - popularity-desc: Most popular trips first (TODO: not yet implemented, uses date-desc)
            limit: Maximum number of results (default 50)
            offset: Number of results to skip (default 0)
            current_user_id: ID of user viewing the trips (None for public access)

        Returns:
            List of Trip objects matching the criteria (filtered by visibility)

        Examples:
            # Get all published trips (as owner)
            trips = await service.get_user_trips(user_id, status=TripStatus.PUBLISHED, current_user_id=user_id)

            # Get trips with tag "camino" (as public viewer)
            trips = await service.get_user_trips(user_id, tag="camino")

            # Pagination
            trips = await service.get_user_trips(user_id, limit=10, offset=20)
        """
        # Check if current user is the owner
        is_owner = current_user_id and current_user_id == user_id

        # Build base query
        query = (
            select(Trip)
            .join(User, Trip.user_id == User.id)  # Join User for trip_visibility check
            .where(Trip.user_id == user_id)
            .options(
                selectinload(Trip.photos),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
                selectinload(Trip.locations),
                selectinload(Trip.user),  # Eager load user for visibility
            )
        )

        # Apply visibility filters (Feature 013)
        if not is_owner:
            # Non-owners can only see PUBLISHED trips
            query = query.where(Trip.status == TripStatus.PUBLISHED)

            # Exclude private trips (only owner can see private trips)
            query = query.where(Trip.is_private.is_(False))

            # Check if viewer is a follower
            is_follower = False
            if current_user_id:
                from src.models.social import Follow

                follow_result = await self.db.execute(
                    select(Follow).where(
                        Follow.follower_id == current_user_id, Follow.following_id == user_id
                    )
                )
                is_follower = follow_result.scalar_one_or_none() is not None

            # Apply trip_visibility filters
            if is_follower:
                # Followers can see 'public' and 'followers' trips
                query = query.where(User.trip_visibility.in_(["public", "followers"]))
            else:
                # Public can only see 'public' trips
                query = query.where(User.trip_visibility == "public")

        # Filter by status if provided (only applies if owner, since non-owners already filtered)
        if is_owner and status is not None:
            query = query.where(Trip.status == status)

        # Filter by is_private if provided (only for owners, non-owners already filtered)
        if is_owner and is_private is not None:
            query = query.where(Trip.is_private == is_private)

        # Filter by tag if provided (case-insensitive)
        if tag:
            tag_normalized = tag.lower().strip()
            # Join with TripTag and Tag to filter
            query = (
                query.join(TripTag, Trip.trip_id == TripTag.trip_id)
                .join(Tag, TripTag.tag_id == Tag.tag_id)
                .where(Tag.normalized == tag_normalized)
            )

        # Apply sorting
        # For date sorting, use start_date (when trip occurred) with fallback to created_at
        # This shows trips in order of when they happened, not when they were created
        if sort_by == "date-asc":
            # Oldest trips first (by start_date, or created_at if no start_date)
            query = query.order_by(
                case(
                    (Trip.start_date.isnot(None), Trip.start_date), else_=func.date(Trip.created_at)
                ).asc()
            )
        elif sort_by == "distance-desc":
            query = query.order_by(Trip.distance_km.desc())
        elif sort_by == "distance-asc":
            query = query.order_by(Trip.distance_km.asc())
        elif sort_by == "popularity-desc":
            # TODO: Add popularity metric (likes, views, etc.)
            # For now, fall back to date descending
            query = query.order_by(
                case(
                    (Trip.start_date.isnot(None), Trip.start_date), else_=func.date(Trip.created_at)
                ).desc()
            )
        else:
            # Default: date-desc (most recent trips first by start_date, or created_at if no start_date)
            query = query.order_by(
                case(
                    (Trip.start_date.isnot(None), Trip.start_date), else_=func.date(Trip.created_at)
                ).desc()
            )

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        result = await self.db.execute(query)
        trips = result.scalars().unique().all()

        logger.debug(
            f"Retrieved {len(trips)} trips for user {user_id} "
            f"(tag={tag}, status={status}, sort_by={sort_by}, limit={limit}, offset={offset})"
        )

        return list(trips)

    async def get_all_tags(self) -> list[Tag]:
        """
        T089: Get all tags ordered by usage count.

        Returns tags sorted by usage_count descending (most popular first).

        Returns:
            List of Tag objects

        Examples:
            tags = await service.get_all_tags()
            # Returns: [Tag(name="camino", usage_count=50), Tag(name="costa", usage_count=30), ...]
        """
        query = select(Tag).order_by(Tag.usage_count.desc(), Tag.name)

        result = await self.db.execute(query)
        tags = result.scalars().all()

        logger.debug(f"Retrieved {len(tags)} tags ordered by usage count")

        return list(tags)

    async def get_public_trips(self, page: int = 1, limit: int = 20) -> tuple[list[Trip], int]:
        """
        T019: Get published trips with public visibility for homepage feed (Feature 013).

        Privacy filtering (FR-003, FR-016):
        - Only trips with status=PUBLISHED
        - Only trips from users with profile_visibility='public' (Feature 013)
        - Users with private profiles have ALL their trips excluded from public feed

        Performance optimization (SC-004):
        - Eager loads user, first photo (display_order=0), first location (sequence=0)
        - Uses composite index idx_trips_public_feed on (status, published_at DESC)
        - Uses index idx_users_profile_visibility on profile_visibility

        Args:
            page: Page number (1-indexed, default 1)
            limit: Items per page (1-50, default 20)

        Returns:
            Tuple of (trips list, total count)

        Examples:
            trips, total = await service.get_public_trips(page=1, limit=20)
            # Returns: ([Trip(...), Trip(...)], 127)
        """
        # Calculate offset from page number
        offset = (page - 1) * limit

        # Main query with privacy filters and eager loading
        # Note: We eager load all photos/locations but will only use first in response
        # This is simpler than conditional loading and still performant for pagination
        query = (
            select(Trip)
            .join(User, Trip.user_id == User.id)
            .where(
                Trip.status == TripStatus.PUBLISHED,  # Only published trips
                Trip.is_private.is_(False),  # Exclude private trips
                User.profile_visibility
                == "public",  # Only trips from public profiles (Feature 013 FR-003, FR-016)
            )
            .options(
                selectinload(Trip.user).selectinload(User.profile),  # Eager load user with profile
                selectinload(Trip.photos),  # Eager load photos
                selectinload(Trip.locations),  # Eager load locations
            )
            .order_by(Trip.published_at.desc())  # Newest first (uses index)
            .limit(limit)
            .offset(offset)
        )

        # Execute query
        result = await self.db.execute(query)
        trips = result.scalars().unique().all()

        # Count total (with same privacy filters)
        total = await self.count_public_trips()

        logger.debug(
            f"Retrieved {len(trips)} public trips (page={page}, limit={limit}, total={total})"
        )

        return list(trips), total

    async def count_public_trips(self) -> int:
        """
        T020: Count published trips with public visibility (Feature 013).

        Uses same privacy filters as get_public_trips() (FR-003, FR-016).
        Only counts trips from users with public profiles.

        Returns:
            Total count of public trips

        Examples:
            total = await service.count_public_trips()
            # Returns: 127
        """
        query = (
            select(func.count(Trip.trip_id))
            .join(User, Trip.user_id == User.id)
            .where(
                Trip.status == TripStatus.PUBLISHED,
                Trip.is_private.is_(False),  # Exclude private trips
                User.profile_visibility == "public",  # Feature 013 FR-003, FR-016
            )
        )

        result = await self.db.execute(query)
        count = result.scalar() or 0

        logger.debug(f"Counted {count} public trips")

        return count
