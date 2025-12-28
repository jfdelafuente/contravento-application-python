"""
Trip service for Travel Diary feature.

Business logic for trip creation, publication, and management.
Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-008
"""

import logging
from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.trip import Tag, Trip, TripDifficulty, TripLocation, TripStatus, TripTag
from src.schemas.trip import LocationInput, TripCreateRequest
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

        Args:
            trip_id: Trip identifier
            user_id: ID of user publishing the trip (must be owner)

        Returns:
            Published Trip instance

        Raises:
            ValueError: If trip not found or validation fails
            PermissionError: If user is not the trip owner
        """
        # Get trip
        result = await self.db.execute(select(Trip).where(Trip.trip_id == trip_id))
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
        if trip.status != TripStatus.PUBLISHED:
            trip.status = TripStatus.PUBLISHED
            trip.published_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(trip)
            logger.info(f"Published trip {trip_id}")
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
