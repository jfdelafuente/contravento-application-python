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


# ============================================================================
# Phase 6: User Story 4 - Tags & Categorization Unit Tests (T084-T085)
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceGetUserTrips:
    """
    T084: Unit tests for TripService.get_user_trips() method.

    Tests tag filtering, status filtering, and pagination logic.
    Functional Requirements: FR-025 (Trip listing with filters)
    """

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user for trip ownership."""
        user = User(
            username="filteruser",
            email="filter@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_trips_with_tags(
        self, db_session: AsyncSession, test_user: User
    ) -> list[Trip]:
        """Create multiple trips with different tags for testing."""
        from src.services.trip_service import TripService

        service = TripService(db_session)

        trip_data = [
            {
                "title": "Ruta Bikepacking",
                "description": "Descripción mínima de 50 caracteres para ruta bikepacking de prueba...",
                "start_date": date(2024, 6, 1),
                "tags": ["bikepacking", "montaña"],
            },
            {
                "title": "Ruta Gravel",
                "description": "Descripción mínima de 50 caracteres para ruta gravel de prueba rural...",
                "start_date": date(2024, 7, 1),
                "tags": ["gravel", "costa"],
            },
            {
                "title": "Ruta Montaña",
                "description": "Descripción mínima de 50 caracteres para ruta montaña puerto alto...",
                "start_date": date(2024, 8, 1),
                "tags": ["montaña", "puerto"],
            },
        ]

        trips = []
        for data in trip_data:
            from src.schemas.trip import TripCreateRequest

            request = TripCreateRequest(**data)
            trip = await service.create_trip(user_id=test_user.id, trip_data=request)
            trips.append(trip)

        return trips

    async def test_get_user_trips_no_filters(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test getting all user trips without filters."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act
        trips = await service.get_user_trips(user_id=test_user.id)

        # Assert
        assert len(trips) == 3
        for trip in trips:
            assert trip.user_id == test_user.id

    async def test_get_user_trips_filter_by_tag(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test filtering trips by tag."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act - Filter by "montaña" tag (should match 2 trips)
        trips = await service.get_user_trips(user_id=test_user.id, tag="montaña")

        # Assert
        assert len(trips) == 2
        for trip in trips:
            tag_names = [tag_rel.tag.name for tag_rel in trip.tags]
            assert "montaña" in tag_names

    async def test_get_user_trips_filter_by_tag_case_insensitive(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test that tag filtering is case-insensitive."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act - Filter with UPPERCASE tag
        trips = await service.get_user_trips(user_id=test_user.id, tag="MONTAÑA")

        # Assert - Should match same trips as lowercase
        assert len(trips) == 2

    async def test_get_user_trips_filter_by_status(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test filtering trips by status."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Publish one trip
        trip_to_publish = test_trips_with_tags[0]
        await service.publish_trip(trip_id=trip_to_publish.trip_id, user_id=test_user.id)

        # Act - Filter by PUBLISHED status
        published_trips = await service.get_user_trips(
            user_id=test_user.id, status=TripStatus.PUBLISHED
        )

        # Assert
        assert len(published_trips) == 1
        assert published_trips[0].status == TripStatus.PUBLISHED

        # Act - Filter by DRAFT status
        draft_trips = await service.get_user_trips(
            user_id=test_user.id, status=TripStatus.DRAFT
        )

        # Assert
        assert len(draft_trips) == 2
        for trip in draft_trips:
            assert trip.status == TripStatus.DRAFT

    async def test_get_user_trips_combined_filters(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test combining tag and status filters."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Publish first trip (has "montaña" tag)
        await service.publish_trip(
            trip_id=test_trips_with_tags[0].trip_id, user_id=test_user.id
        )

        # Act - Filter by tag AND status
        trips = await service.get_user_trips(
            user_id=test_user.id, tag="montaña", status=TripStatus.PUBLISHED
        )

        # Assert
        assert len(trips) == 1
        assert trips[0].status == TripStatus.PUBLISHED

        tag_names = [tag_rel.tag.name for tag_rel in trips[0].tags]
        assert "montaña" in tag_names

    async def test_get_user_trips_pagination(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test pagination with limit and offset."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act - Get first page (limit=2, offset=0)
        page1 = await service.get_user_trips(user_id=test_user.id, limit=2, offset=0)

        # Assert
        assert len(page1) == 2

        # Act - Get second page (limit=2, offset=2)
        page2 = await service.get_user_trips(user_id=test_user.id, limit=2, offset=2)

        # Assert
        assert len(page2) == 1  # Only 1 trip left

        # Verify no overlap
        page1_ids = {trip.trip_id for trip in page1}
        page2_ids = {trip.trip_id for trip in page2}
        assert len(page1_ids & page2_ids) == 0

    async def test_get_user_trips_nonexistent_tag(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test filtering by non-existent tag returns empty list."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act
        trips = await service.get_user_trips(
            user_id=test_user.id, tag="nonexistent_tag"
        )

        # Assert
        assert len(trips) == 0

    async def test_get_user_trips_ordered_by_created_at_desc(
        self, db_session: AsyncSession, test_user: User, test_trips_with_tags: list[Trip]
    ):
        """Test trips are ordered by created_at descending (newest first)."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act
        trips = await service.get_user_trips(user_id=test_user.id)

        # Assert
        for i in range(len(trips) - 1):
            assert trips[i].created_at >= trips[i + 1].created_at


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceTagLimit:
    """
    T085: Unit tests for tag count validation.

    Tests that trips cannot exceed 10 tags.
    Functional Requirements: FR-023 (Tag count limit)
    """

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user for trip ownership."""
        user = User(
            username="taglimituser",
            email="taglimit@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def test_create_trip_with_max_tags(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test creating trip with exactly 10 tags (max allowed)."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripCreateRequest

        service = TripService(db_session)

        # Create trip with 10 tags
        trip_data = TripCreateRequest(
            title="Trip with Max Tags",
            description="Descripción de al menos 50 caracteres para trip con máximo de tags permitidos...",
            start_date=date(2024, 6, 1),
            tags=["tag1", "tag2", "tag3", "tag4", "tag5", "tag6", "tag7", "tag8", "tag9", "tag10"],
        )

        # Act
        trip = await service.create_trip(user_id=test_user.id, trip_data=trip_data)

        # Assert
        assert len(trip.tags) == 10

    async def test_create_trip_exceeds_max_tags(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test creating trip with more than 10 tags raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripCreateRequest

        service = TripService(db_session)

        # Create trip with 11 tags (exceeds limit)
        trip_data = TripCreateRequest(
            title="Trip with Too Many Tags",
            description="Descripción de al menos 50 caracteres para trip con exceso de tags...",
            start_date=date(2024, 6, 1),
            tags=[
                "tag1",
                "tag2",
                "tag3",
                "tag4",
                "tag5",
                "tag6",
                "tag7",
                "tag8",
                "tag9",
                "tag10",
                "tag11",  # 11th tag - exceeds limit
            ],
        )

        # Act & Assert
        with pytest.raises(ValueError, match="máximo.*10 tags"):
            await service.create_trip(user_id=test_user.id, trip_data=trip_data)

    async def test_update_trip_exceeds_max_tags(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test updating trip to exceed 10 tags raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripCreateRequest, TripUpdateRequest

        service = TripService(db_session)

        # Create trip with 5 tags
        create_data = TripCreateRequest(
            title="Trip to Update",
            description="Descripción de al menos 50 caracteres para trip que se actualizará luego...",
            start_date=date(2024, 6, 1),
            tags=["tag1", "tag2", "tag3", "tag4", "tag5"],
        )
        trip = await service.create_trip(user_id=test_user.id, trip_data=create_data)

        # Prepare update with 11 tags
        update_data = TripUpdateRequest(
            tags=[
                "tag1",
                "tag2",
                "tag3",
                "tag4",
                "tag5",
                "tag6",
                "tag7",
                "tag8",
                "tag9",
                "tag10",
                "tag11",  # 11th tag - exceeds limit
            ],
            client_updated_at=datetime.utcnow(),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="máximo.*10 tags"):
            await service.update_trip(
                trip_id=trip.trip_id, user_id=test_user.id, trip_data=update_data
            )

    async def test_get_all_tags_returns_all(self, db_session: AsyncSession, test_user: User):
        """Test TripService.get_all_tags() returns all tags ordered by usage."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripCreateRequest

        service = TripService(db_session)

        # Create trips with different tags
        trip_data_list = [
            {
                "title": "Trip 1",
                "description": "Descripción de al menos 50 caracteres para trip número uno con tags...",
                "start_date": date(2024, 6, 1),
                "tags": ["popular", "tag2"],
            },
            {
                "title": "Trip 2",
                "description": "Descripción de al menos 50 caracteres para trip número dos con tags...",
                "start_date": date(2024, 6, 2),
                "tags": ["popular", "tag3"],
            },
            {
                "title": "Trip 3",
                "description": "Descripción de al menos 50 caracteres para trip número tres con tags...",
                "start_date": date(2024, 6, 3),
                "tags": ["rare"],
            },
        ]

        for data in trip_data_list:
            request = TripCreateRequest(**data)
            await service.create_trip(user_id=test_user.id, trip_data=request)

        # Act
        tags = await service.get_all_tags()

        # Assert
        assert len(tags) >= 4  # At least our 4 tags (popular, tag2, tag3, rare)

        # Verify ordering by usage_count (descending)
        for i in range(len(tags) - 1):
            assert tags[i].usage_count >= tags[i + 1].usage_count

        # Find our tags
        tag_map = {tag.name: tag for tag in tags}

        assert "popular" in tag_map
        assert tag_map["popular"].usage_count == 2  # Used in 2 trips

        assert "rare" in tag_map
        assert tag_map["rare"].usage_count == 1  # Used in 1 trip


# ============================================================================
# Phase 5: User Story 3 - Edit/Delete Trips Unit Tests (T069-T071)
# ============================================================================


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceUpdateTrip:
    """
    T069: Unit tests for TripService.update_trip() method.

    Tests business logic for updating trips with optimistic locking.
    Functional Requirements: FR-016, FR-020 (Trip editing with conflict detection)
    """

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user for trip ownership."""
        user = User(
            username="updateuser",
            email="update@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def test_trip(
        self, db_session: AsyncSession, test_user: User
    ) -> Trip:
        """Create a test trip for updating."""
        from src.services.trip_service import TripService
        from src.schemas.trip import TripCreateRequest

        service = TripService(db_session)

        trip_data = TripCreateRequest(
            title="Viaje Original",
            description="Descripción original de al menos 50 caracteres para el viaje inicial...",
            start_date=date(2024, 6, 1),
            distance_km=100.0,
        )

        trip = await service.create_trip(user_id=test_user.id, trip_data=trip_data)
        return trip

    async def test_update_trip_basic_fields(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test updating basic trip fields."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripUpdateRequest

        service = TripService(db_session)

        update_data = TripUpdateRequest(
            title="Viaje Actualizado",
            description="Descripción completamente nueva con muchos más detalles sobre el viaje...",
            distance_km=150.5,
            client_updated_at=test_trip.updated_at,
        )

        # Act
        updated_trip = await service.update_trip(
            trip_id=test_trip.trip_id,
            user_id=test_user.id,
            trip_data=update_data,
        )

        # Assert
        assert updated_trip.title == "Viaje Actualizado"
        assert "completamente nueva" in updated_trip.description
        assert updated_trip.distance_km == 150.5
        assert updated_trip.updated_at != test_trip.updated_at

    async def test_update_trip_partial_fields(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test partial update (only some fields provided)."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripUpdateRequest

        service = TripService(db_session)

        # Only update title
        update_data = TripUpdateRequest(
            title="Solo Título",
            client_updated_at=test_trip.updated_at,
        )

        original_description = test_trip.description
        original_distance = test_trip.distance_km

        # Act
        updated_trip = await service.update_trip(
            trip_id=test_trip.trip_id,
            user_id=test_user.id,
            trip_data=update_data,
        )

        # Assert - Title updated
        assert updated_trip.title == "Solo Título"

        # Assert - Other fields unchanged
        assert updated_trip.description == original_description
        assert updated_trip.distance_km == original_distance

    async def test_update_trip_optimistic_lock_conflict(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test optimistic locking prevents stale updates."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripUpdateRequest

        service = TripService(db_session)

        old_updated_at = test_trip.updated_at

        # Make first update
        update_1 = TripUpdateRequest(
            title="Primera Actualización",
            client_updated_at=old_updated_at,
        )

        await service.update_trip(
            trip_id=test_trip.trip_id,
            user_id=test_user.id,
            trip_data=update_1,
        )

        # Try to update with stale timestamp
        update_2 = TripUpdateRequest(
            title="Intento con Timestamp Antiguo",
            client_updated_at=old_updated_at,  # Stale!
        )

        # Act & Assert
        with pytest.raises(ValueError, match="modificado"):
            await service.update_trip(
                trip_id=test_trip.trip_id,
                user_id=test_user.id,
                trip_data=update_2,
            )

    async def test_update_trip_unauthorized_user(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test updating trip as non-owner raises PermissionError."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripUpdateRequest

        service = TripService(db_session)

        # Create different user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        update_data = TripUpdateRequest(
            title="Intento No Autorizado",
            client_updated_at=test_trip.updated_at,
        )

        # Act & Assert
        with pytest.raises(PermissionError, match="permiso"):
            await service.update_trip(
                trip_id=test_trip.trip_id,
                user_id=other_user.id,
                trip_data=update_data,
            )

    async def test_update_trip_not_found(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test updating non-existent trip raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripUpdateRequest

        service = TripService(db_session)

        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        update_data = TripUpdateRequest(
            title="No Existe",
            client_updated_at=datetime.utcnow(),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="no encontrado"):
            await service.update_trip(
                trip_id=fake_trip_id,
                user_id=test_user.id,
                trip_data=update_data,
            )

    async def test_update_trip_with_tags(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test updating trip tags replaces old tags."""
        # Arrange
        from src.services.trip_service import TripService
        from src.schemas.trip import TripUpdateRequest

        service = TripService(db_session)

        # Add initial tags
        initial_update = TripUpdateRequest(
            tags=["original", "inicial"],
            client_updated_at=test_trip.updated_at,
        )

        trip_with_tags = await service.update_trip(
            trip_id=test_trip.trip_id,
            user_id=test_user.id,
            trip_data=initial_update,
        )

        # Update with new tags
        new_update = TripUpdateRequest(
            tags=["nuevo", "actualizado"],
            client_updated_at=trip_with_tags.updated_at,
        )

        updated_trip = await service.update_trip(
            trip_id=test_trip.trip_id,
            user_id=test_user.id,
            trip_data=new_update,
        )

        # Assert - New tags present
        tag_names = [tag_rel.tag.name for tag_rel in updated_trip.tags]
        assert "nuevo" in tag_names
        assert "actualizado" in tag_names

        # Old tags removed
        assert "original" not in tag_names
        assert "inicial" not in tag_names


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceDeleteTrip:
    """
    T070: Unit tests for TripService.delete_trip() method.

    Tests business logic for deleting trips with cascade and stats update.
    Functional Requirements: FR-017, FR-018 (Trip deletion)
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
    async def test_trip(
        self, db_session: AsyncSession, test_user: User
    ) -> Trip:
        """Create a test trip for deletion."""
        from src.services.trip_service import TripService
        from src.schemas.trip import TripCreateRequest

        service = TripService(db_session)

        trip_data = TripCreateRequest(
            title="Viaje a Eliminar",
            description="Descripción de al menos 50 caracteres para el viaje que será eliminado...",
            start_date=date(2024, 6, 1),
            distance_km=75.0,
        )

        trip = await service.create_trip(user_id=test_user.id, trip_data=trip_data)
        return trip

    async def test_delete_trip_success(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test deleting trip removes it from database."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        trip_id = test_trip.trip_id

        # Act
        result = await service.delete_trip(trip_id=trip_id, user_id=test_user.id)

        # Assert
        assert "message" in result
        assert result["trip_id"] == trip_id

        # Verify trip is deleted
        deleted_trip_result = await db_session.execute(
            select(Trip).where(Trip.trip_id == trip_id)
        )
        deleted_trip = deleted_trip_result.scalar_one_or_none()

        assert deleted_trip is None

    async def test_delete_trip_unauthorized_user(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test deleting trip as non-owner raises PermissionError."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Create different user
        other_user = User(
            username="otheruser2",
            email="other2@example.com",
            hashed_password="hashed",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Act & Assert
        with pytest.raises(PermissionError, match="permiso"):
            await service.delete_trip(
                trip_id=test_trip.trip_id,
                user_id=other_user.id,
            )

    async def test_delete_trip_not_found(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test deleting non-existent trip raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        fake_trip_id = "00000000-0000-0000-0000-000000000000"

        # Act & Assert
        with pytest.raises(ValueError, match="no encontrado"):
            await service.delete_trip(
                trip_id=fake_trip_id,
                user_id=test_user.id,
            )

    async def test_delete_published_trip_updates_stats(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test deleting published trip decrements user stats."""
        # Arrange
        from src.services.trip_service import TripService
        from src.models.stats import UserStats

        service = TripService(db_session)

        # Publish trip first (to update stats)
        await service.publish_trip(trip_id=test_trip.trip_id, user_id=test_user.id)

        # Get stats before deletion
        stats_result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == test_user.id)
        )
        stats = stats_result.scalar_one()
        trips_before = stats.total_trips
        km_before = stats.total_kilometers

        # Act - Delete trip
        await service.delete_trip(trip_id=test_trip.trip_id, user_id=test_user.id)

        # Assert - Stats decremented
        await db_session.refresh(stats)

        assert stats.total_trips == max(0, trips_before - 1)
        assert stats.total_kilometers == max(0.0, km_before - 75.0)


@pytest.mark.unit
@pytest.mark.asyncio
class TestStatsServiceDeletionHelper:
    """
    T071: Unit tests for StatsService.update_stats_on_trip_delete().

    Tests business logic for stats rollback on trip deletion.
    Functional Requirements: FR-018 (Stats update on deletion)
    """

    @pytest.fixture
    async def test_user(self, db_session: AsyncSession) -> User:
        """Create a test user with stats."""
        from src.models.stats import UserStats

        user = User(
            username="statsuser",
            email="stats@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create user stats
        stats = UserStats(
            user_id=user.id,
            total_trips=5,
            total_kilometers=500.0,
            total_photos=10,
            countries_visited=["ES"],
        )
        db_session.add(stats)
        await db_session.commit()

        return user

    async def test_update_stats_on_trip_delete_decrements_correctly(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test stats are decremented correctly on trip deletion."""
        # Arrange
        from src.services.stats_service import StatsService
        from src.models.stats import UserStats

        service = StatsService(db_session)

        # Get initial stats
        stats_result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == test_user.id)
        )
        stats = stats_result.scalar_one()

        initial_trips = stats.total_trips
        initial_km = stats.total_kilometers
        initial_photos = stats.total_photos

        # Act - Delete trip (75km, 3 photos)
        await service.update_stats_on_trip_delete(
            user_id=test_user.id,
            distance_km=75.0,
            country_code="ES",
            photos_count=3,
        )

        # Assert
        await db_session.refresh(stats)

        assert stats.total_trips == initial_trips - 1
        assert stats.total_kilometers == initial_km - 75.0
        assert stats.total_photos == initial_photos - 3

    async def test_update_stats_on_trip_delete_never_negative(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test stats never go negative on deletion."""
        # Arrange
        from src.services.stats_service import StatsService
        from src.models.stats import UserStats

        service = StatsService(db_session)

        # Set stats to low values
        stats_result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == test_user.id)
        )
        stats = stats_result.scalar_one()

        stats.total_trips = 1
        stats.total_kilometers = 10.0
        stats.total_photos = 1
        await db_session.commit()

        # Act - Delete trip with more than current values
        await service.update_stats_on_trip_delete(
            user_id=test_user.id,
            distance_km=50.0,  # More than current 10.0
            country_code="ES",
            photos_count=5,  # More than current 1
        )

        # Assert - Stats at 0, not negative
        await db_session.refresh(stats)

        assert stats.total_trips >= 0
        assert stats.total_kilometers >= 0.0
        assert stats.total_photos >= 0

    async def test_update_stats_preserves_countries(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test that countries_visited is preserved on deletion."""
        # Arrange
        from src.services.stats_service import StatsService
        from src.models.stats import UserStats

        service = StatsService(db_session)

        # Get initial countries
        stats_result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == test_user.id)
        )
        stats = stats_result.scalar_one()

        initial_countries = stats.countries_visited.copy()

        # Act - Delete trip
        await service.update_stats_on_trip_delete(
            user_id=test_user.id,
            distance_km=100.0,
            country_code="ES",
            photos_count=2,
        )

        # Assert - Countries unchanged (historical data preserved)
        await db_session.refresh(stats)

        assert stats.countries_visited == initial_countries
