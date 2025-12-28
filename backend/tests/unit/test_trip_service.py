"""
Unit tests for TripService business logic.

Tests trip service methods in isolation with mocked dependencies.
Functional Requirements: FR-001, FR-002, FR-003, FR-007
"""

import pytest
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.trip import Trip, TripStatus, TripDifficulty, Tag, TripLocation
from src.models.user import User
from src.schemas.trip import TripCreateRequest, LocationInput


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceCreateTrip:
    """
    T031: Unit tests for TripService.create_trip() method.

    Tests business logic for creating trips with various configurations.
    """

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

    async def test_create_trip_minimal(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test creating trip with only required fields."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        trip_data = TripCreateRequest(
            title="Vía Verde del Aceite",
            description="Un recorrido precioso entre olivos centenarios...",
            start_date=date(2024, 5, 15),
        )

        # Act
        trip = await service.create_trip(user_id=test_user.id, data=trip_data)

        # Assert - Basic trip fields
        assert trip.trip_id is not None
        assert trip.user_id == test_user.id
        assert trip.title == trip_data.title
        assert trip.description == trip_data.description
        assert trip.start_date == trip_data.start_date
        assert trip.status == TripStatus.DRAFT

        # Assert - Optional fields are None
        assert trip.end_date is None
        assert trip.distance_km is None
        assert trip.difficulty is None

        # Assert - Metadata
        assert trip.created_at is not None
        assert trip.updated_at is not None
        assert trip.published_at is None

        # Assert - Database persistence
        result = await db_session.execute(
            select(Trip).where(Trip.trip_id == trip.trip_id)
        )
        db_trip = result.scalar_one()
        assert db_trip.title == trip_data.title

    async def test_create_trip_with_all_fields(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test creating trip with all optional fields populated."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        trip_data = TripCreateRequest(
            title="Transpirenaica",
            description="<p>Cruce completo de los Pirineos</p>",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
            distance_km=850.5,
            difficulty="very_difficult",
            locations=[
                LocationInput(name="Hendaya", country="Francia"),
                LocationInput(name="Llansa", country="España"),
            ],
            tags=["bikepacking", "pirineos"],
        )

        # Act
        trip = await service.create_trip(user_id=test_user.id, data=trip_data)

        # Assert
        assert trip.title == trip_data.title
        assert trip.start_date == trip_data.start_date
        assert trip.end_date == trip_data.end_date
        assert trip.distance_km == trip_data.distance_km
        assert trip.difficulty == TripDifficulty.VERY_DIFFICULT

    async def test_create_trip_sanitizes_html(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test that HTML in description is sanitized."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        trip_data = TripCreateRequest(
            title="Test Trip",
            description='<p>Safe content</p><script>alert("XSS")</script>',
            start_date=date(2024, 5, 15),
        )

        # Act
        trip = await service.create_trip(user_id=test_user.id, data=trip_data)

        # Assert - Script tag should be removed
        assert "<script>" not in trip.description
        assert "alert" not in trip.description
        assert "<p>Safe content</p>" in trip.description

    async def test_create_trip_with_tags(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test creating trip with tags creates/associates tags correctly."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        trip_data = TripCreateRequest(
            title="Camino de Santiago",
            description="Peregrinación en bicicleta",
            start_date=date(2024, 6, 1),
            tags=["camino", "peregrinación", "bikepacking"],
        )

        # Act
        trip = await service.create_trip(user_id=test_user.id, data=trip_data)

        # Assert - Tags are created and associated
        await db_session.refresh(trip, ["trip_tags"])
        assert len(trip.trip_tags) == 3

        # Verify tags exist in database
        result = await db_session.execute(select(Tag))
        tags = result.scalars().all()
        tag_names = [tag.name for tag in tags]

        assert "camino" in tag_names
        assert "peregrinación" in tag_names
        assert "bikepacking" in tag_names

    async def test_create_trip_with_duplicate_tags_case_insensitive(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test that duplicate tags (different case) are merged."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        trip_data = TripCreateRequest(
            title="Test Trip",
            description="Testing tag deduplication",
            start_date=date(2024, 5, 15),
            tags=["Bikepacking", "BIKEPACKING", "bikepacking"],
        )

        # Act
        trip = await service.create_trip(user_id=test_user.id, data=trip_data)

        # Assert - Only one tag should be created
        await db_session.refresh(trip, ["trip_tags"])
        assert len(trip.trip_tags) == 1

        # Verify only one tag in database
        result = await db_session.execute(
            select(Tag).where(Tag.normalized == "bikepacking")
        )
        tags = result.scalars().all()
        assert len(tags) == 1

    async def test_create_trip_with_existing_tags(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test that existing tags are reused and usage_count is incremented."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Create first trip with tag
        trip_data_1 = TripCreateRequest(
            title="First Trip",
            description="First trip with tag",
            start_date=date(2024, 5, 1),
            tags=["andalucía"],
        )
        await service.create_trip(user_id=test_user.id, data=trip_data_1)

        # Get initial usage count
        result = await db_session.execute(
            select(Tag).where(Tag.normalized == "andalucía")
        )
        tag_before = result.scalar_one()
        usage_before = tag_before.usage_count

        # Act - Create second trip with same tag
        trip_data_2 = TripCreateRequest(
            title="Second Trip",
            description="Second trip with same tag",
            start_date=date(2024, 5, 15),
            tags=["andalucía"],
        )
        await service.create_trip(user_id=test_user.id, data=trip_data_2)

        # Assert - Tag is reused, usage_count incremented
        result = await db_session.execute(
            select(Tag).where(Tag.normalized == "andalucía")
        )
        tags = result.scalars().all()
        assert len(tags) == 1  # Only one tag exists

        tag_after = tags[0]
        assert tag_after.usage_count == usage_before + 1

    async def test_create_trip_with_locations(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test creating trip with locations sets correct sequence."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        trip_data = TripCreateRequest(
            title="Test Route",
            description="Testing location sequence",
            start_date=date(2024, 5, 15),
            locations=[
                LocationInput(name="Madrid", country="España"),
                LocationInput(name="Toledo", country="España"),
                LocationInput(name="Córdoba", country="España"),
            ],
        )

        # Act
        trip = await service.create_trip(user_id=test_user.id, data=trip_data)

        # Assert - Locations created with correct sequence
        result = await db_session.execute(
            select(TripLocation)
            .where(TripLocation.trip_id == trip.trip_id)
            .order_by(TripLocation.sequence)
        )
        locations = result.scalars().all()

        assert len(locations) == 3
        assert locations[0].name == "Madrid"
        assert locations[0].sequence == 0
        assert locations[1].name == "Toledo"
        assert locations[1].sequence == 1
        assert locations[2].name == "Córdoba"
        assert locations[2].sequence == 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServicePublishTrip:
    """
    T032: Unit tests for TripService.publish_trip() method.

    Tests business logic for publishing trips with validation.
    Functional Requirement: FR-007
    """

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

    @pytest.fixture
    async def draft_trip_valid(
        self, db_session: AsyncSession, test_user: User
    ) -> Trip:
        """Create a valid draft trip ready for publication."""
        trip = Trip(
            user_id=test_user.id,
            title="Valid Trip for Publishing",
            description="A" * 60,  # Exactly 60 chars (>= 50 required)
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    @pytest.fixture
    async def draft_trip_short_description(
        self, db_session: AsyncSession, test_user: User
    ) -> Trip:
        """Create a draft trip with short description (invalid for publishing)."""
        trip = Trip(
            user_id=test_user.id,
            title="Invalid Trip",
            description="Too short",  # Only ~9 chars
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    async def test_publish_trip_success(
        self, db_session: AsyncSession, test_user: User, draft_trip_valid: Trip
    ):
        """Test successfully publishing a valid draft trip."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act
        published_trip = await service.publish_trip(
            trip_id=draft_trip_valid.trip_id, user_id=test_user.id
        )

        # Assert - Status changed to published
        assert published_trip.status == TripStatus.PUBLISHED
        assert published_trip.published_at is not None
        assert isinstance(published_trip.published_at, datetime)

        # Assert - Database persistence
        result = await db_session.execute(
            select(Trip).where(Trip.trip_id == draft_trip_valid.trip_id)
        )
        db_trip = result.scalar_one()
        assert db_trip.status == TripStatus.PUBLISHED
        assert db_trip.published_at is not None

    async def test_publish_trip_validation_error_short_description(
        self,
        db_session: AsyncSession,
        test_user: User,
        draft_trip_short_description: Trip,
    ):
        """Test publishing trip with short description fails validation."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.publish_trip(
                trip_id=draft_trip_short_description.trip_id, user_id=test_user.id
            )

        # Assert error message
        error_msg = str(exc_info.value)
        assert "descripción" in error_msg.lower()
        assert "50" in error_msg

    async def test_publish_trip_validation_requires_title(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test publishing trip without title fails validation."""
        # Arrange
        from src.services.trip_service import TripService

        # Create trip with empty title (bypass schema validation for unit test)
        trip = Trip(
            user_id=test_user.id,
            title="",  # Empty title
            description="A" * 60,
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.commit()

        service = TripService(db_session)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.publish_trip(trip_id=trip.trip_id, user_id=test_user.id)

        assert "título" in str(exc_info.value).lower()

    async def test_publish_trip_with_minimal_valid_data(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test publishing trip with minimal valid data succeeds."""
        # Arrange
        from src.services.trip_service import TripService

        # Create trip with minimal valid data for publication
        trip = Trip(
            user_id=test_user.id,
            title="Valid Minimal Trip",
            description="A" * 60,  # Exactly 60 chars (>= 50 required)
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.commit()

        service = TripService(db_session)

        # Act
        published = await service.publish_trip(trip_id=trip.trip_id, user_id=test_user.id)

        # Assert
        assert published.status == TripStatus.PUBLISHED
        assert published.published_at is not None

    async def test_publish_trip_not_found(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test publishing non-existent trip raises error."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        fake_trip_id = "00000000-0000-0000-0000-000000000000"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.publish_trip(trip_id=fake_trip_id, user_id=test_user.id)

        assert "no encontrado" in str(exc_info.value).lower() or "not found" in str(
            exc_info.value
        ).lower()

    async def test_publish_trip_unauthorized_different_user(
        self, db_session: AsyncSession, test_user: User, draft_trip_valid: Trip
    ):
        """Test publishing trip by non-owner raises error."""
        # Arrange
        from src.services.trip_service import TripService

        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        service = TripService(db_session)

        # Act & Assert
        with pytest.raises(PermissionError) as exc_info:
            await service.publish_trip(
                trip_id=draft_trip_valid.trip_id, user_id=other_user.id
            )

        assert "permiso" in str(exc_info.value).lower() or "permission" in str(
            exc_info.value
        ).lower()

    async def test_publish_trip_idempotent(
        self, db_session: AsyncSession, test_user: User, draft_trip_valid: Trip
    ):
        """Test publishing already-published trip is idempotent."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # First publish
        first_publish = await service.publish_trip(
            trip_id=draft_trip_valid.trip_id, user_id=test_user.id
        )
        first_published_at = first_publish.published_at

        # Act - Publish again
        second_publish = await service.publish_trip(
            trip_id=draft_trip_valid.trip_id, user_id=test_user.id
        )

        # Assert - published_at should not change
        assert second_publish.published_at == first_published_at
        assert second_publish.status == TripStatus.PUBLISHED
