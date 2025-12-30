"""
Unit tests for TripService business logic.

Tests trip service methods in isolation with mocked dependencies.
Functional Requirements: FR-001, FR-002, FR-003, FR-007
"""

import pytest
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.trip import Trip, TripStatus, TripDifficulty, Tag, TripLocation, TripPhoto
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


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServicePhotoUpload:
    """
    T052: Unit tests for TripService.upload_photo() method.

    Tests business logic for uploading photos to trips.
    Functional Requirements: FR-010, FR-011
    """

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user for trip ownership."""
        user = User(
            username="photouser",
            email="photo@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def draft_trip(self, db_session: AsyncSession, test_user: User) -> Trip:
        """Create a draft trip for photo upload tests."""
        trip = Trip(
            user_id=test_user.id,
            title="Trip for Photo Upload",
            description="Testing photo upload functionality",
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    async def test_upload_photo_success(
        self, db_session: AsyncSession, test_user: User, draft_trip: Trip
    ):
        """Test uploading photo to trip creates TripPhoto record."""
        # Arrange
        from src.services.trip_service import TripService
        from io import BytesIO
        from PIL import Image

        service = TripService(db_session)

        # Create test image
        img = Image.new("RGB", (800, 600), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act
        photo = await service.upload_photo(
            trip_id=draft_trip.trip_id,
            user_id=test_user.id,
            photo_file=img_bytes,
            filename="test.jpg",
            content_type="image/jpeg",
        )

        # Assert
        assert photo.trip_id == draft_trip.trip_id
        assert photo.order == 0  # First photo
        assert photo.file_size > 0
        assert photo.width == 800
        assert photo.height == 600
        assert photo.photo_url is not None
        assert photo.thumb_url is not None
        assert photo.uploaded_at is not None

    async def test_upload_photo_sets_correct_order(
        self, db_session: AsyncSession, test_user: User, draft_trip: Trip
    ):
        """Test uploading multiple photos sets correct order."""
        # Arrange
        from src.services.trip_service import TripService
        from io import BytesIO
        from PIL import Image

        service = TripService(db_session)

        # Act - Upload 3 photos
        photo_ids = []
        for i in range(3):
            img = Image.new("RGB", (200, 200), color="white")
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            photo = await service.upload_photo(
                trip_id=draft_trip.trip_id,
                user_id=test_user.id,
                photo_file=img_bytes,
                filename=f"photo_{i}.jpg",
                content_type="image/jpeg",
            )
            photo_ids.append(photo.id)

            # Assert order
            assert photo.order == i

    async def test_upload_photo_exceeds_max_limit(
        self, db_session: AsyncSession, test_user: User, draft_trip: Trip
    ):
        """Test uploading more than 20 photos raises error."""
        # Arrange
        from src.services.trip_service import TripService
        from io import BytesIO
        from PIL import Image

        service = TripService(db_session)

        # Upload 20 photos (max limit)
        for i in range(20):
            img = Image.new("RGB", (100, 100), color="white")
            img_bytes = BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            await service.upload_photo(
                trip_id=draft_trip.trip_id,
                user_id=test_user.id,
                photo_file=img_bytes,
                filename=f"photo_{i}.jpg",
                content_type="image/jpeg",
            )

        # Act & Assert - 21st photo should fail
        img = Image.new("RGB", (100, 100), color="white")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        with pytest.raises(ValueError) as exc_info:
            await service.upload_photo(
                trip_id=draft_trip.trip_id,
                user_id=test_user.id,
                photo_file=img_bytes,
                filename="photo_21.jpg",
                content_type="image/jpeg",
            )

        assert "límite" in str(exc_info.value).lower()
        assert "20" in str(exc_info.value)

    async def test_upload_photo_invalid_file_type(
        self, db_session: AsyncSession, test_user: User, draft_trip: Trip
    ):
        """Test uploading invalid file type raises error."""
        # Arrange
        from src.services.trip_service import TripService
        from io import BytesIO

        service = TripService(db_session)

        # Create non-image file
        text_file = BytesIO(b"This is not an image")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.upload_photo(
                trip_id=draft_trip.trip_id,
                user_id=test_user.id,
                photo_file=text_file,
                filename="test.txt",
                content_type="text/plain",
            )

        assert "formato" in str(exc_info.value).lower()

    async def test_upload_photo_updates_stats_on_published_trip(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test uploading photo to published trip updates user stats."""
        # Arrange
        from src.services.trip_service import TripService
        from io import BytesIO
        from PIL import Image

        # Create published trip
        trip = Trip(
            user_id=test_user.id,
            title="Published Trip",
            description="A" * 60,
            start_date=date(2024, 5, 15),
            status=TripStatus.PUBLISHED,
        )
        db_session.add(trip)
        await db_session.commit()

        service = TripService(db_session)

        # Get initial stats
        from src.models.user import UserStats

        result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == test_user.id)
        )
        stats = result.scalar_one_or_none()
        if not stats:
            stats = UserStats(user_id=test_user.id)
            db_session.add(stats)
            await db_session.commit()

        initial_photo_count = stats.total_trip_photos

        # Act - Upload photo
        img = Image.new("RGB", (200, 200), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        await service.upload_photo(
            trip_id=trip.trip_id,
            user_id=test_user.id,
            photo_file=img_bytes,
            filename="stats_test.jpg",
            content_type="image/jpeg",
        )

        # Assert - Stats updated
        await db_session.refresh(stats)
        assert stats.total_trip_photos == initial_photo_count + 1


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServicePhotoDelete:
    """
    T053: Unit tests for TripService.delete_photo() method.

    Tests business logic for deleting photos from trips.
    Functional Requirement: FR-013
    """

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user for trip ownership."""
        user = User(
            username="deleteuser",
            email="delete@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def trip_with_photo(
        self, db_session: AsyncSession, test_user: User
    ) -> tuple[Trip, TripPhoto]:
        """Create a trip with one photo for deletion tests."""
        trip = Trip(
            user_id=test_user.id,
            title="Trip with Photo",
            description="Testing photo deletion",
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.flush()

        photo = TripPhoto(
            trip_id=trip.trip_id,
            photo_url="/storage/test.jpg",
            thumb_url="/storage/test_thumb.jpg",
            order=0,
            file_size=1024,
            width=800,
            height=600,
        )
        db_session.add(photo)
        await db_session.commit()
        await db_session.refresh(trip)
        await db_session.refresh(photo)

        return trip, photo

    async def test_delete_photo_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        trip_with_photo: tuple[Trip, TripPhoto],
    ):
        """Test deleting photo removes it from database."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photo = trip_with_photo
        service = TripService(db_session)
        photo_id = photo.id

        # Act
        result = await service.delete_photo(
            trip_id=trip.trip_id, photo_id=photo_id, user_id=test_user.id
        )

        # Assert
        assert result["success"] is True
        assert "eliminada" in result["message"].lower()

        # Verify photo deleted from database
        result = await db_session.execute(
            select(TripPhoto).where(TripPhoto.id == photo_id)
        )
        deleted_photo = result.scalar_one_or_none()
        assert deleted_photo is None

    async def test_delete_photo_reorders_remaining_photos(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test deleting middle photo reorders remaining photos."""
        # Arrange
        from src.services.trip_service import TripService

        # Create trip with 3 photos
        trip = Trip(
            user_id=test_user.id,
            title="Multi-Photo Trip",
            description="Testing reordering after delete",
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.flush()

        photos = []
        for i in range(3):
            photo = TripPhoto(
                trip_id=trip.trip_id,
                photo_url=f"/storage/photo_{i}.jpg",
                thumb_url=f"/storage/photo_{i}_thumb.jpg",
                order=i,
                file_size=1024,
                width=800,
                height=600,
            )
            db_session.add(photo)
            photos.append(photo)

        await db_session.commit()
        for photo in photos:
            await db_session.refresh(photo)

        service = TripService(db_session)

        # Act - Delete middle photo (order=1)
        await service.delete_photo(
            trip_id=trip.trip_id, photo_id=photos[1].id, user_id=test_user.id
        )

        # Assert - Remaining photos reordered
        result = await db_session.execute(
            select(TripPhoto)
            .where(TripPhoto.trip_id == trip.trip_id)
            .order_by(TripPhoto.order)
        )
        remaining_photos = result.scalars().all()

        assert len(remaining_photos) == 2
        assert remaining_photos[0].id == photos[0].id
        assert remaining_photos[0].order == 0
        assert remaining_photos[1].id == photos[2].id
        assert remaining_photos[1].order == 1  # Reordered from 2 to 1

    async def test_delete_photo_not_found(
        self, db_session: AsyncSession, test_user: User, trip_with_photo
    ):
        """Test deleting non-existent photo raises error."""
        # Arrange
        from src.services.trip_service import TripService

        trip, _ = trip_with_photo
        service = TripService(db_session)
        fake_photo_id = "00000000-0000-0000-0000-000000000000"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.delete_photo(
                trip_id=trip.trip_id, photo_id=fake_photo_id, user_id=test_user.id
            )

        assert "no encontrada" in str(exc_info.value).lower() or "not found" in str(
            exc_info.value
        ).lower()

    async def test_delete_photo_unauthorized(
        self, db_session: AsyncSession, test_user: User, trip_with_photo
    ):
        """Test deleting photo by non-owner raises error."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photo = trip_with_photo

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
            await service.delete_photo(
                trip_id=trip.trip_id, photo_id=photo.id, user_id=other_user.id
            )

        assert "permiso" in str(exc_info.value).lower() or "permission" in str(
            exc_info.value
        ).lower()

    async def test_delete_photo_updates_stats_on_published_trip(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test deleting photo from published trip updates user stats."""
        # Arrange
        from src.services.trip_service import TripService

        # Create published trip with photo
        trip = Trip(
            user_id=test_user.id,
            title="Published Trip",
            description="A" * 60,
            start_date=date(2024, 5, 15),
            status=TripStatus.PUBLISHED,
        )
        db_session.add(trip)
        await db_session.flush()

        photo = TripPhoto(
            trip_id=trip.trip_id,
            photo_url="/storage/delete_stats.jpg",
            thumb_url="/storage/delete_stats_thumb.jpg",
            order=0,
            file_size=1024,
            width=800,
            height=600,
        )
        db_session.add(photo)
        await db_session.commit()

        # Create or get user stats
        from src.models.user import UserStats

        result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == test_user.id)
        )
        stats = result.scalar_one_or_none()
        if not stats:
            stats = UserStats(user_id=test_user.id, total_trip_photos=1)
            db_session.add(stats)
            await db_session.commit()

        initial_photo_count = stats.total_trip_photos

        service = TripService(db_session)

        # Act - Delete photo
        await service.delete_photo(
            trip_id=trip.trip_id, photo_id=photo.id, user_id=test_user.id
        )

        # Assert - Stats updated
        await db_session.refresh(stats)
        assert stats.total_trip_photos == initial_photo_count - 1


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServicePhotoReorder:
    """
    T054: Unit tests for TripService.reorder_photos() method.

    Tests business logic for reordering photos in trip gallery.
    Functional Requirement: FR-012
    """

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user for trip ownership."""
        user = User(
            username="reorderuser",
            email="reorder@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def trip_with_photos(
        self, db_session: AsyncSession, test_user: User
    ) -> tuple[Trip, list[TripPhoto]]:
        """Create a trip with 4 photos for reordering tests."""
        trip = Trip(
            user_id=test_user.id,
            title="Trip for Reordering",
            description="Testing photo reordering",
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.flush()

        photos = []
        for i in range(4):
            photo = TripPhoto(
                trip_id=trip.trip_id,
                photo_url=f"/storage/photo_{i}.jpg",
                thumb_url=f"/storage/photo_{i}_thumb.jpg",
                order=i,
                file_size=1024,
                width=800,
                height=600,
            )
            db_session.add(photo)
            photos.append(photo)

        await db_session.commit()
        await db_session.refresh(trip)
        for photo in photos:
            await db_session.refresh(photo)

        return trip, photos

    async def test_reorder_photos_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        trip_with_photos: tuple[Trip, list[TripPhoto]],
    ):
        """Test reordering photos updates order correctly."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photos = trip_with_photos
        service = TripService(db_session)

        # Original order: [0, 1, 2, 3]
        # New order: [3, 0, 2, 1]
        new_order = [photos[3].id, photos[0].id, photos[2].id, photos[1].id]

        # Act
        result = await service.reorder_photos(
            trip_id=trip.trip_id, photo_order=new_order, user_id=test_user.id
        )

        # Assert
        assert result["success"] is True

        # Verify database order
        result = await db_session.execute(
            select(TripPhoto)
            .where(TripPhoto.trip_id == trip.trip_id)
            .order_by(TripPhoto.order)
        )
        reordered_photos = result.scalars().all()

        assert len(reordered_photos) == 4
        for i, photo in enumerate(reordered_photos):
            assert photo.id == new_order[i]
            assert photo.order == i

    async def test_reorder_photos_invalid_photo_ids(
        self,
        db_session: AsyncSession,
        test_user: User,
        trip_with_photos: tuple[Trip, list[TripPhoto]],
    ):
        """Test reordering with invalid photo IDs raises error."""
        # Arrange
        from src.services.trip_service import TripService

        trip, _ = trip_with_photos
        service = TripService(db_session)

        fake_ids = [
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
        ]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.reorder_photos(
                trip_id=trip.trip_id, photo_order=fake_ids, user_id=test_user.id
            )

        assert "inválido" in str(exc_info.value).lower() or "invalid" in str(
            exc_info.value
        ).lower()

    async def test_reorder_photos_missing_photo_ids(
        self,
        db_session: AsyncSession,
        test_user: User,
        trip_with_photos: tuple[Trip, list[TripPhoto]],
    ):
        """Test reordering with incomplete photo list raises error."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photos = trip_with_photos
        service = TripService(db_session)

        # Only include 2 of 4 photos
        incomplete_order = [photos[0].id, photos[1].id]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.reorder_photos(
                trip_id=trip.trip_id, photo_order=incomplete_order, user_id=test_user.id
            )

        assert "todas" in str(exc_info.value).lower() or "all" in str(
            exc_info.value
        ).lower()

    async def test_reorder_photos_unauthorized(
        self,
        db_session: AsyncSession,
        test_user: User,
        trip_with_photos: tuple[Trip, list[TripPhoto]],
    ):
        """Test reordering photos by non-owner raises error."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photos = trip_with_photos

        # Create another user
        other_user = User(
            username="otheruser2",
            email="other2@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        service = TripService(db_session)
        new_order = [p.id for p in photos]

        # Act & Assert
        with pytest.raises(PermissionError) as exc_info:
            await service.reorder_photos(
                trip_id=trip.trip_id, photo_order=new_order, user_id=other_user.id
            )

        assert "permiso" in str(exc_info.value).lower() or "permission" in str(
            exc_info.value
        ).lower()
