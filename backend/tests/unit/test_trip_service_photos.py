"""
Unit tests for TripService photo management methods.

Tests photo upload, delete, and reorder business logic in isolation.
Functional Requirements: FR-009, FR-010, FR-011, FR-012, FR-013

T052-T054: Photo service unit tests
"""

import io
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image

from src.models.trip import Trip, TripStatus, TripPhoto
from src.models.user import User


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceUploadPhoto:
    """
    T052: Unit tests for TripService.upload_photo() method.

    Tests business logic for uploading photos to trips.
    Functional Requirements: FR-009, FR-010, FR-011
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
    async def test_trip(self, db_session: AsyncSession, test_user: User) -> Trip:
        """Create a test trip for photo upload."""
        trip = Trip(
            user_id=test_user.id,
            title="Test Trip",
            description="A" * 60,
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    async def test_upload_photo_success(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test uploading valid photo creates TripPhoto record."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Create a fake image
        img = Image.new("RGB", (1200, 800), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act
        photo = await service.upload_photo(
            trip_id=test_trip.trip_id,
            user_id=test_user.id,
            photo_file=img_bytes,
            filename="test.jpg",
            content_type="image/jpeg",
        )

        # Assert - Photo created
        assert photo.photo_id is not None
        assert photo.trip_id == test_trip.trip_id
        assert photo.photo_url is not None
        assert photo.thumb_url is not None
        assert photo.order == 0  # First photo

        # Assert - Files created (will be tested in integration)
        assert ".jpg" in photo.photo_url
        assert ".jpg" in photo.thumb_url

    async def test_upload_photo_invalid_format(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test uploading invalid format raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Create a fake text file
        fake_file = io.BytesIO(b"This is not an image")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.upload_photo(
                trip_id=test_trip.trip_id,
                user_id=test_user.id,
                photo_file=fake_file,
                filename="test.txt",
                content_type="text/plain",
            )

        assert "formato" in str(exc_info.value).lower() or "format" in str(
            exc_info.value
        ).lower()

    async def test_upload_photo_exceeds_limit(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test uploading photo when trip has 20 photos raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Create 20 photos (max limit)
        for i in range(20):
            photo = TripPhoto(
                trip_id=test_trip.trip_id,
                photo_url=f"/storage/trip_photos/2024/12/test{i}.jpg",
                thumb_url=f"/storage/trip_photos/2024/12/test{i}_thumb.jpg",
                order=i,
            )
            db_session.add(photo)
        await db_session.commit()

        # Create a valid image
        img = Image.new("RGB", (800, 600), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.upload_photo(
                trip_id=test_trip.trip_id,
                user_id=test_user.id,
                photo_file=img_bytes,
                filename="test21.jpg",
                content_type="image/jpeg",
            )

        assert "20" in str(exc_info.value)

    async def test_upload_photo_trip_not_found(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test uploading photo to non-existent trip raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        fake_trip_id = "00000000-0000-0000-0000-000000000000"

        img = Image.new("RGB", (800, 600), color="green")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.upload_photo(
                trip_id=fake_trip_id,
                user_id=test_user.id,
                photo_file=img_bytes,
                filename="test.jpg",
                content_type="image/jpeg",
            )

        assert "no encontrado" in str(exc_info.value).lower() or "not found" in str(
            exc_info.value
        ).lower()

    async def test_upload_photo_unauthorized(
        self, db_session: AsyncSession, test_trip: Trip
    ):
        """Test uploading photo by non-owner raises PermissionError."""
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

        img = Image.new("RGB", (800, 600), color="yellow")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act & Assert
        with pytest.raises(PermissionError) as exc_info:
            await service.upload_photo(
                trip_id=test_trip.trip_id,
                user_id=other_user.id,
                photo_file=img_bytes,
                filename="test.jpg",
                content_type="image/jpeg",
            )

        assert "permiso" in str(exc_info.value).lower() or "permission" in str(
            exc_info.value
        ).lower()

    async def test_upload_photo_assigns_order_correctly(
        self, db_session: AsyncSession, test_user: User, test_trip: Trip
    ):
        """Test uploading multiple photos assigns correct order sequence."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)

        # Act - Upload 3 photos
        photos = []
        for i in range(3):
            img = Image.new("RGB", (800, 600), color=["red", "green", "blue"][i])
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            photo = await service.upload_photo(
                trip_id=test_trip.trip_id,
                user_id=test_user.id,
                photo_file=img_bytes,
                filename=f"test{i}.jpg",
                content_type="image/jpeg",
            )
            photos.append(photo)

        # Assert - Photos have sequential order
        assert photos[0].order == 0
        assert photos[1].order == 1
        assert photos[2].order == 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceDeletePhoto:
    """
    T053: Unit tests for TripService.delete_photo() method.

    Tests business logic for deleting photos from trips.
    Functional Requirement: FR-013
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
    async def test_trip_with_photos(
        self, db_session: AsyncSession, test_user: User
    ) -> Trip:
        """Create a test trip with 3 photos."""
        trip = Trip(
            user_id=test_user.id,
            title="Test Trip",
            description="A" * 60,
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.flush()

        # Add 3 photos
        for i in range(3):
            photo = TripPhoto(
                trip_id=trip.trip_id,
                photo_url=f"/storage/trip_photos/2024/12/test{i}.jpg",
                thumb_url=f"/storage/trip_photos/2024/12/test{i}_thumb.jpg",
                order=i,
            )
            db_session.add(photo)

        await db_session.commit()
        await db_session.refresh(trip)
        return trip

    async def test_delete_photo_success(
        self, db_session: AsyncSession, test_user: User, test_trip_with_photos: Trip
    ):
        """Test deleting photo removes it from database."""
        # Arrange
        from src.services.trip_service import TripService
        from sqlalchemy import select

        service = TripService(db_session)

        # Get first photo
        result = await db_session.execute(
            select(TripPhoto)
            .where(TripPhoto.trip_id == test_trip_with_photos.trip_id)
            .order_by(TripPhoto.order)
        )
        photos = result.scalars().all()
        assert len(photos) == 3
        photo_to_delete = photos[0]

        # Act
        await service.delete_photo(
            trip_id=test_trip_with_photos.trip_id,
            photo_id=photo_to_delete.photo_id,
            user_id=test_user.id,
        )

        # Assert - Photo deleted from database
        result = await db_session.execute(
            select(TripPhoto).where(TripPhoto.trip_id == test_trip_with_photos.trip_id)
        )
        remaining_photos = result.scalars().all()
        assert len(remaining_photos) == 2

    async def test_delete_photo_reorders_remaining(
        self, db_session: AsyncSession, test_user: User, test_trip_with_photos: Trip
    ):
        """Test deleting middle photo reorders remaining photos."""
        # Arrange
        from src.services.trip_service import TripService
        from sqlalchemy import select

        service = TripService(db_session)

        # Get photos
        result = await db_session.execute(
            select(TripPhoto)
            .where(TripPhoto.trip_id == test_trip_with_photos.trip_id)
            .order_by(TripPhoto.order)
        )
        photos = result.scalars().all()
        middle_photo = photos[1]  # Photo at order=1

        # Act - Delete middle photo
        await service.delete_photo(
            trip_id=test_trip_with_photos.trip_id,
            photo_id=middle_photo.photo_id,
            user_id=test_user.id,
        )

        # Assert - Remaining photos have sequential order
        result = await db_session.execute(
            select(TripPhoto)
            .where(TripPhoto.trip_id == test_trip_with_photos.trip_id)
            .order_by(TripPhoto.order)
        )
        remaining = result.scalars().all()
        assert len(remaining) == 2
        assert remaining[0].order == 0
        assert remaining[1].order == 1

    async def test_delete_photo_not_found(
        self, db_session: AsyncSession, test_user: User, test_trip_with_photos: Trip
    ):
        """Test deleting non-existent photo raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService

        service = TripService(db_session)
        fake_photo_id = "00000000-0000-0000-0000-000000000000"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.delete_photo(
                trip_id=test_trip_with_photos.trip_id,
                photo_id=fake_photo_id,
                user_id=test_user.id,
            )

        assert "no encontrada" in str(exc_info.value).lower() or "not found" in str(
            exc_info.value
        ).lower()

    async def test_delete_photo_unauthorized(
        self, db_session: AsyncSession, test_trip_with_photos: Trip
    ):
        """Test deleting photo by non-owner raises PermissionError."""
        # Arrange
        from src.services.trip_service import TripService
        from sqlalchemy import select

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

        # Get a photo
        result = await db_session.execute(
            select(TripPhoto).where(TripPhoto.trip_id == test_trip_with_photos.trip_id)
        )
        photo = result.scalars().first()

        # Act & Assert
        with pytest.raises(PermissionError) as exc_info:
            await service.delete_photo(
                trip_id=test_trip_with_photos.trip_id,
                photo_id=photo.photo_id,
                user_id=other_user.id,
            )

        assert "permiso" in str(exc_info.value).lower() or "permission" in str(
            exc_info.value
        ).lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestTripServiceReorderPhotos:
    """
    T054: Unit tests for TripService.reorder_photos() method.

    Tests business logic for reordering trip photos.
    Functional Requirement: FR-012
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
    async def test_trip_with_photos(
        self, db_session: AsyncSession, test_user: User
    ) -> tuple[Trip, list[TripPhoto]]:
        """Create a test trip with 3 photos in order."""
        trip = Trip(
            user_id=test_user.id,
            title="Test Trip",
            description="A" * 60,
            start_date=date(2024, 5, 15),
            status=TripStatus.DRAFT,
        )
        db_session.add(trip)
        await db_session.flush()

        # Add 3 photos
        photos = []
        for i in range(3):
            photo = TripPhoto(
                trip_id=trip.trip_id,
                photo_url=f"/storage/trip_photos/2024/12/test{i}.jpg",
                thumb_url=f"/storage/trip_photos/2024/12/test{i}_thumb.jpg",
                order=i,
            )
            db_session.add(photo)
            photos.append(photo)

        await db_session.commit()
        await db_session.refresh(trip)
        for photo in photos:
            await db_session.refresh(photo)

        return trip, photos

    async def test_reorder_photos_success(
        self, db_session: AsyncSession, test_user: User, test_trip_with_photos
    ):
        """Test reordering photos updates order field correctly."""
        # Arrange
        from src.services.trip_service import TripService
        from sqlalchemy import select

        trip, photos = test_trip_with_photos
        service = TripService(db_session)

        # Original order: [photo0, photo1, photo2]
        # New order: [photo2, photo0, photo1]
        new_order = [photos[2].photo_id, photos[0].photo_id, photos[1].photo_id]

        # Act
        await service.reorder_photos(
            trip_id=trip.trip_id, user_id=test_user.id, photo_order=new_order
        )

        # Assert - Photos have new order
        result = await db_session.execute(
            select(TripPhoto)
            .where(TripPhoto.trip_id == trip.trip_id)
            .order_by(TripPhoto.order)
        )
        reordered = result.scalars().all()

        assert reordered[0].photo_id == photos[2].photo_id  # Was order=2, now order=0
        assert reordered[1].photo_id == photos[0].photo_id  # Was order=0, now order=1
        assert reordered[2].photo_id == photos[1].photo_id  # Was order=1, now order=2

    async def test_reorder_photos_invalid_photo_id(
        self, db_session: AsyncSession, test_user: User, test_trip_with_photos
    ):
        """Test reordering with invalid photo ID raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photos = test_trip_with_photos
        service = TripService(db_session)

        # Include a fake photo ID
        fake_id = "00000000-0000-0000-0000-000000000000"
        invalid_order = [photos[0].photo_id, fake_id, photos[1].photo_id]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.reorder_photos(
                trip_id=trip.trip_id, user_id=test_user.id, photo_order=invalid_order
            )

        assert "inválido" in str(exc_info.value).lower() or "invalid" in str(
            exc_info.value
        ).lower()

    async def test_reorder_photos_wrong_count(
        self, db_session: AsyncSession, test_user: User, test_trip_with_photos
    ):
        """Test reordering with wrong number of photos raises ValueError."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photos = test_trip_with_photos
        service = TripService(db_session)

        # Only provide 2 photo IDs when trip has 3
        partial_order = [photos[0].photo_id, photos[1].photo_id]

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.reorder_photos(
                trip_id=trip.trip_id, user_id=test_user.id, photo_order=partial_order
            )

        assert "cantidad" in str(exc_info.value).lower() or "count" in str(
            exc_info.value
        ).lower()

    async def test_reorder_photos_unauthorized(
        self, db_session: AsyncSession, test_trip_with_photos
    ):
        """Test reordering photos by non-owner raises PermissionError."""
        # Arrange
        from src.services.trip_service import TripService

        trip, photos = test_trip_with_photos

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
        new_order = [p.photo_id for p in photos]

        # Act & Assert
        with pytest.raises(PermissionError) as exc_info:
            await service.reorder_photos(
                trip_id=trip.trip_id, user_id=other_user.id, photo_order=new_order
            )

        assert "permiso" in str(exc_info.value).lower() or "permission" in str(
            exc_info.value
        ).lower()
