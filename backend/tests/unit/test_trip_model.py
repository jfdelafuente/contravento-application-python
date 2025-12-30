"""
Unit tests for Trip SQLAlchemy models.

Tests model creation, validation, relationships, and database operations.
"""

from datetime import date, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import (
    Tag,
    Trip,
    TripDifficulty,
    TripLocation,
    TripPhoto,
    TripStatus,
    TripTag,
)
from src.models.user import User


class TestTripModel:
    """Test Trip model creation and validation."""

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user for trip ownership."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def test_create_trip_minimal(self, db_session: AsyncSession, test_user: User) -> None:
        """Test creating a trip with only required fields."""
        trip = Trip(
            user_id=test_user.id,
            title="Vía Verde del Aceite",
            description="<p>Un recorrido precioso...</p>",
            start_date=date(2024, 5, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        assert trip.trip_id is not None
        assert trip.user_id == test_user.id
        assert trip.title == "Vía Verde del Aceite"
        assert trip.description == "<p>Un recorrido precioso...</p>"
        assert trip.start_date == date(2024, 5, 15)
        assert trip.end_date is None
        assert trip.distance_km is None
        assert trip.difficulty is None
        assert trip.status == TripStatus.DRAFT
        assert trip.created_at is not None
        assert trip.updated_at is not None
        assert trip.published_at is None

    async def test_create_trip_complete(self, db_session: AsyncSession, test_user: User) -> None:
        """Test creating a trip with all fields."""
        trip = Trip(
            user_id=test_user.id,
            title="Transpirenaica",
            description="<p>Cruzando los Pirineos...</p>",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
            distance_km=850.5,
            difficulty=TripDifficulty.VERY_DIFFICULT,
            status=TripStatus.PUBLISHED,
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        assert trip.end_date == date(2024, 7, 15)
        assert trip.distance_km == 850.5
        assert trip.difficulty == TripDifficulty.VERY_DIFFICULT
        assert trip.status == TripStatus.PUBLISHED

    async def test_trip_status_enum(self, db_session: AsyncSession, test_user: User) -> None:
        """Test TripStatus enum values."""
        # Draft trip
        draft_trip = Trip(
            user_id=test_user.id,
            title="Draft Trip",
            description="Test",
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(draft_trip)

        # Published trip
        published_trip = Trip(
            user_id=test_user.id,
            title="Published Trip",
            description="Test",
            start_date=date(2024, 5, 15),
            status=TripStatus.PUBLISHED,
            published_at=datetime.utcnow(),
        )
        db_session.add(published_trip)

        await db_session.commit()
        await db_session.refresh(draft_trip)
        await db_session.refresh(published_trip)

        assert draft_trip.status == TripStatus.DRAFT
        assert published_trip.status == TripStatus.PUBLISHED
        assert published_trip.published_at is not None

    async def test_trip_difficulty_enum(self, db_session: AsyncSession, test_user: User) -> None:
        """Test TripDifficulty enum values."""
        difficulties = [
            TripDifficulty.EASY,
            TripDifficulty.MODERATE,
            TripDifficulty.DIFFICULT,
            TripDifficulty.VERY_DIFFICULT,
        ]

        for difficulty in difficulties:
            trip = Trip(
                user_id=test_user.id,
                title=f"Trip {difficulty.value}",
                description="Test",
                start_date=date(2024, 5, 15),
                difficulty=difficulty,
            )
            db_session.add(trip)

        await db_session.commit()

        # Query all trips
        result = await db_session.execute(select(Trip))
        trips = result.scalars().all()

        assert len(trips) == 4
        assert all(trip.difficulty in difficulties for trip in trips)

    async def test_trip_user_relationship(self, db_session: AsyncSession, test_user: User) -> None:
        """Test Trip -> User relationship."""
        trip = Trip(
            user_id=test_user.id,
            title="Test Trip",
            description="Test",
            start_date=date(2024, 5, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)

        # Load relationship
        await db_session.refresh(trip, ["user"])
        assert trip.user is not None
        assert trip.user.id == test_user.id
        assert trip.user.username == "testuser"

    async def test_user_trips_relationship(self, db_session: AsyncSession, test_user: User) -> None:
        """Test User -> Trip relationship (back_populates)."""
        # Create multiple trips
        trip1 = Trip(
            user_id=test_user.id,
            title="Trip 1",
            description="First trip",
            start_date=date(2024, 5, 15),
        )
        trip2 = Trip(
            user_id=test_user.id,
            title="Trip 2",
            description="Second trip",
            start_date=date(2024, 6, 1),
        )
        db_session.add_all([trip1, trip2])
        await db_session.commit()

        # Refresh user with trips
        await db_session.refresh(test_user, ["trips"])
        assert len(test_user.trips) == 2
        assert trip1 in test_user.trips
        assert trip2 in test_user.trips

    async def test_trip_cascade_delete(self, db_session: AsyncSession, test_user: User) -> None:
        """Test that deleting a user cascades to trips."""
        trip = Trip(
            user_id=test_user.id,
            title="Test Trip",
            description="Test",
            start_date=date(2024, 5, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        trip_id = trip.trip_id

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Trip should be deleted
        result = await db_session.execute(select(Trip).where(Trip.trip_id == trip_id))
        deleted_trip = result.scalar_one_or_none()
        assert deleted_trip is None


class TestTripPhotoModel:
    """Test TripPhoto model."""

    @pytest.fixture
    async def test_trip(self, db_session: AsyncSession) -> Trip:
        """Create a test trip."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.flush()

        trip = Trip(
            user_id=user.id,
            title="Test Trip",
            description="Test",
            start_date=date(2024, 5, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    async def test_create_trip_photo(self, db_session: AsyncSession, test_trip: Trip) -> None:
        """Test creating a trip photo."""
        photo = TripPhoto(
            trip_id=test_trip.trip_id,
            photo_url="/storage/trip_photos/2024/05/abc123.jpg",
            thumbnail_url="/storage/trip_photos/2024/05/abc123_thumb.jpg",
            caption="Beautiful landscape",
            display_order=0,
        )
        db_session.add(photo)
        await db_session.commit()
        await db_session.refresh(photo)

        assert photo.photo_id is not None
        assert photo.trip_id == test_trip.trip_id
        assert photo.photo_url == "/storage/trip_photos/2024/05/abc123.jpg"
        assert photo.thumbnail_url == "/storage/trip_photos/2024/05/abc123_thumb.jpg"
        assert photo.caption == "Beautiful landscape"
        assert photo.display_order == 0
        assert photo.uploaded_at is not None

    async def test_trip_photos_relationship(
        self, db_session: AsyncSession, test_trip: Trip
    ) -> None:
        """Test Trip -> TripPhoto relationship."""
        photo1 = TripPhoto(
            trip_id=test_trip.trip_id,
            photo_url="/storage/photo1.jpg",
            thumbnail_url="/storage/thumb1.jpg",
            display_order=0,
        )
        photo2 = TripPhoto(
            trip_id=test_trip.trip_id,
            photo_url="/storage/photo2.jpg",
            thumbnail_url="/storage/thumb2.jpg",
            display_order=1,
        )
        db_session.add_all([photo1, photo2])
        await db_session.commit()

        # Refresh trip with photos
        await db_session.refresh(test_trip, ["photos"])
        assert len(test_trip.photos) == 2
        # Photos should be ordered by display_order
        assert test_trip.photos[0].display_order == 0
        assert test_trip.photos[1].display_order == 1

    async def test_photo_cascade_delete(self, db_session: AsyncSession, test_trip: Trip) -> None:
        """Test that deleting a trip cascades to photos."""
        photo = TripPhoto(
            trip_id=test_trip.trip_id,
            photo_url="/storage/photo.jpg",
            thumbnail_url="/storage/thumb.jpg",
            display_order=0,
        )
        db_session.add(photo)
        await db_session.commit()
        photo_id = photo.photo_id

        # Delete trip
        await db_session.delete(test_trip)
        await db_session.commit()

        # Photo should be deleted
        result = await db_session.execute(select(TripPhoto).where(TripPhoto.photo_id == photo_id))
        deleted_photo = result.scalar_one_or_none()
        assert deleted_photo is None


class TestTagModel:
    """Test Tag model."""

    async def test_create_tag(self, db_session: AsyncSession) -> None:
        """Test creating a tag."""
        tag = Tag(
            name="Bikepacking",
            normalized="bikepacking",
        )
        db_session.add(tag)
        await db_session.commit()
        await db_session.refresh(tag)

        assert tag.tag_id is not None
        assert tag.name == "Bikepacking"
        assert tag.normalized == "bikepacking"
        assert tag.usage_count == 0
        assert tag.created_at is not None

    async def test_tag_unique_name(self, db_session: AsyncSession) -> None:
        """Test that tag names are unique."""
        tag1 = Tag(name="Vías Verdes", normalized="vias verdes")
        db_session.add(tag1)
        await db_session.commit()

        # Try to create duplicate tag
        tag2 = Tag(name="Vías Verdes", normalized="vias verdes")
        db_session.add(tag2)

        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()

    async def test_tag_unique_normalized(self, db_session: AsyncSession) -> None:
        """Test that normalized tag names are unique."""
        tag1 = Tag(name="Vías Verdes", normalized="vias verdes")
        db_session.add(tag1)
        await db_session.commit()

        # Try to create tag with same normalized name but different display name
        tag2 = Tag(name="VÍAS VERDES", normalized="vias verdes")
        db_session.add(tag2)

        with pytest.raises(Exception):  # IntegrityError
            await db_session.commit()

    async def test_tag_usage_count_increment(self, db_session: AsyncSession) -> None:
        """Test incrementing tag usage count."""
        tag = Tag(name="Camino", normalized="camino", usage_count=0)
        db_session.add(tag)
        await db_session.commit()
        await db_session.refresh(tag)

        # Increment usage
        tag.usage_count += 1
        await db_session.commit()
        await db_session.refresh(tag)

        assert tag.usage_count == 1


class TestTripTagModel:
    """Test TripTag association model."""

    @pytest.fixture
    async def test_trip(self, db_session: AsyncSession) -> Trip:
        """Create a test trip."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.flush()

        trip = Trip(
            user_id=user.id,
            title="Test Trip",
            description="Test",
            start_date=date(2024, 5, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    @pytest.fixture
    async def test_tag(self, db_session: AsyncSession) -> Tag:
        """Create a test tag."""
        tag = Tag(name="Bikepacking", normalized="bikepacking")
        db_session.add(tag)
        await db_session.commit()
        await db_session.refresh(tag)
        return tag

    async def test_create_trip_tag(
        self, db_session: AsyncSession, test_trip: Trip, test_tag: Tag
    ) -> None:
        """Test creating trip-tag association."""
        trip_tag = TripTag(
            trip_id=test_trip.trip_id,
            tag_id=test_tag.tag_id,
        )
        db_session.add(trip_tag)
        await db_session.commit()

        # Verify association
        result = await db_session.execute(
            select(TripTag)
            .where(TripTag.trip_id == test_trip.trip_id)
            .where(TripTag.tag_id == test_tag.tag_id)
        )
        saved_trip_tag = result.scalar_one()
        assert saved_trip_tag.trip_id == test_trip.trip_id
        assert saved_trip_tag.tag_id == test_tag.tag_id
        assert saved_trip_tag.created_at is not None

    async def test_trip_tags_relationship(self, db_session: AsyncSession, test_trip: Trip) -> None:
        """Test Trip -> TripTag -> Tag relationship."""
        # Create multiple tags
        tag1 = Tag(name="Bikepacking", normalized="bikepacking")
        tag2 = Tag(name="Montaña", normalized="montana")
        db_session.add_all([tag1, tag2])
        await db_session.flush()

        # Associate tags with trip
        trip_tag1 = TripTag(trip_id=test_trip.trip_id, tag_id=tag1.tag_id)
        trip_tag2 = TripTag(trip_id=test_trip.trip_id, tag_id=tag2.tag_id)
        db_session.add_all([trip_tag1, trip_tag2])
        await db_session.commit()

        # Refresh trip with trip_tags
        await db_session.refresh(test_trip, ["trip_tags"])
        assert len(test_trip.trip_tags) == 2

    async def test_trip_tag_cascade_delete(
        self, db_session: AsyncSession, test_trip: Trip, test_tag: Tag
    ) -> None:
        """Test that deleting a trip cascades to trip_tags."""
        trip_tag = TripTag(trip_id=test_trip.trip_id, tag_id=test_tag.tag_id)
        db_session.add(trip_tag)
        await db_session.commit()

        # Delete trip
        await db_session.delete(test_trip)
        await db_session.commit()

        # TripTag should be deleted
        result = await db_session.execute(
            select(TripTag).where(TripTag.trip_id == test_trip.trip_id)
        )
        deleted_trip_tag = result.scalar_one_or_none()
        assert deleted_trip_tag is None

        # Tag should still exist
        result = await db_session.execute(select(Tag).where(Tag.tag_id == test_tag.tag_id))
        tag_still_exists = result.scalar_one_or_none()
        assert tag_still_exists is not None


class TestTripLocationModel:
    """Test TripLocation model."""

    @pytest.fixture
    async def test_trip(self, db_session: AsyncSession) -> Trip:
        """Create a test trip."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.flush()

        trip = Trip(
            user_id=user.id,
            title="Test Trip",
            description="Test",
            start_date=date(2024, 5, 15),
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    async def test_create_location_without_coordinates(
        self, db_session: AsyncSession, test_trip: Trip
    ) -> None:
        """Test creating location without geocoding."""
        location = TripLocation(
            trip_id=test_trip.trip_id,
            name="Camino de Santiago",
            latitude=None,
            longitude=None,
            sequence=0,
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)

        assert location.location_id is not None
        assert location.trip_id == test_trip.trip_id
        assert location.name == "Camino de Santiago"
        assert location.latitude is None
        assert location.longitude is None
        assert location.sequence == 0
        assert location.created_at is not None

    async def test_create_location_with_coordinates(
        self, db_session: AsyncSession, test_trip: Trip
    ) -> None:
        """Test creating location with geocoding."""
        location = TripLocation(
            trip_id=test_trip.trip_id,
            name="Baeza",
            latitude=37.9963,
            longitude=-3.4669,
            sequence=0,
        )
        db_session.add(location)
        await db_session.commit()
        await db_session.refresh(location)

        assert location.latitude == 37.9963
        assert location.longitude == -3.4669

    async def test_trip_locations_relationship(
        self, db_session: AsyncSession, test_trip: Trip
    ) -> None:
        """Test Trip -> TripLocation relationship."""
        loc1 = TripLocation(
            trip_id=test_trip.trip_id,
            name="Jaén",
            sequence=0,
        )
        loc2 = TripLocation(
            trip_id=test_trip.trip_id,
            name="Baeza",
            sequence=1,
        )
        loc3 = TripLocation(
            trip_id=test_trip.trip_id,
            name="Úbeda",
            sequence=2,
        )
        db_session.add_all([loc1, loc2, loc3])
        await db_session.commit()

        # Refresh trip with locations
        await db_session.refresh(test_trip, ["locations"])
        assert len(test_trip.locations) == 3
        # Locations should be ordered by sequence
        assert test_trip.locations[0].name == "Jaén"
        assert test_trip.locations[1].name == "Baeza"
        assert test_trip.locations[2].name == "Úbeda"

    async def test_location_cascade_delete(self, db_session: AsyncSession, test_trip: Trip) -> None:
        """Test that deleting a trip cascades to locations."""
        location = TripLocation(
            trip_id=test_trip.trip_id,
            name="Test Location",
            sequence=0,
        )
        db_session.add(location)
        await db_session.commit()
        location_id = location.location_id

        # Delete trip
        await db_session.delete(test_trip)
        await db_session.commit()

        # Location should be deleted
        result = await db_session.execute(
            select(TripLocation).where(TripLocation.location_id == location_id)
        )
        deleted_location = result.scalar_one_or_none()
        assert deleted_location is None


class TestTripCompleteRelationships:
    """Test complete trip with all relationships."""

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user."""
        user = User(
            username="maria_garcia",
            email="maria@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def test_complete_trip_with_all_relationships(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test trip with photos, tags, and locations."""
        # Create trip
        trip = Trip(
            user_id=test_user.id,
            title="Vía Verde del Aceite",
            description="<p>Espectacular ruta...</p>",
            start_date=date(2024, 5, 15),
            end_date=date(2024, 5, 17),
            distance_km=127.3,
            difficulty=TripDifficulty.MODERATE,
            status=TripStatus.PUBLISHED,
            published_at=datetime.utcnow(),
        )
        db_session.add(trip)
        await db_session.flush()

        # Add photos
        photo1 = TripPhoto(
            trip_id=trip.trip_id,
            photo_url="/storage/photo1.jpg",
            thumbnail_url="/storage/thumb1.jpg",
            caption="Olivares",
            display_order=0,
        )
        photo2 = TripPhoto(
            trip_id=trip.trip_id,
            photo_url="/storage/photo2.jpg",
            thumbnail_url="/storage/thumb2.jpg",
            caption="Viaducto",
            display_order=1,
        )
        db_session.add_all([photo1, photo2])

        # Add tags
        tag1 = Tag(name="Vías Verdes", normalized="vias verdes")
        tag2 = Tag(name="Andalucía", normalized="andalucia")
        db_session.add_all([tag1, tag2])
        await db_session.flush()

        trip_tag1 = TripTag(trip_id=trip.trip_id, tag_id=tag1.tag_id)
        trip_tag2 = TripTag(trip_id=trip.trip_id, tag_id=tag2.tag_id)
        db_session.add_all([trip_tag1, trip_tag2])

        # Add locations
        loc1 = TripLocation(
            trip_id=trip.trip_id,
            name="Jaén",
            latitude=37.7792,
            longitude=-3.7849,
            sequence=0,
        )
        loc2 = TripLocation(
            trip_id=trip.trip_id,
            name="Baeza",
            latitude=37.9963,
            longitude=-3.4669,
            sequence=1,
        )
        db_session.add_all([loc1, loc2])

        await db_session.commit()

        # Refresh trip with all relationships
        await db_session.refresh(trip, ["photos", "trip_tags", "locations", "user"])

        # Verify all relationships loaded correctly
        assert len(trip.photos) == 2
        assert len(trip.trip_tags) == 2
        assert len(trip.locations) == 2
        assert trip.user.username == "maria_garcia"

        # Verify ordering
        assert trip.photos[0].caption == "Olivares"
        assert trip.photos[1].caption == "Viaducto"
        assert trip.locations[0].name == "Jaén"
        assert trip.locations[1].name == "Baeza"
