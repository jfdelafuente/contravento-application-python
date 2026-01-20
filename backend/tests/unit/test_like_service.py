"""
Unit tests for LikeService (Feature 004 - US2: Likes/Me Gusta).

Tests cover:
- T041: like_trip() basic functionality
- T042: unlike_trip() basic functionality
- T043: get_trip_likes() pagination
- T044: Preventing duplicate likes (FR-010)
- T045: Preventing self-likes (FR-011)

Following TDD: These tests are written BEFORE implementation.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.like import Like
from src.models.trip import Trip
from src.models.user import User
from src.services.like_service import LikeService


@pytest.fixture
async def trip_owner(db_session: AsyncSession) -> User:
    """Create a trip owner user for testing."""
    user = User(
        id=str(uuid4()),
        username="trip_owner",
        email="owner@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def liker_user(db_session: AsyncSession) -> User:
    """Create a user who will like trips."""
    user = User(
        id=str(uuid4()),
        username="liker_user",
        email="liker@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def published_trip(db_session: AsyncSession, trip_owner: User) -> Trip:
    """Create a published trip for testing."""
    trip = Trip(
        trip_id=str(uuid4()),
        user_id=trip_owner.id,
        title="Test Trip for Likes",
        description="A trip to test like functionality",
        start_date="2024-06-01",
        end_date="2024-06-05",
        distance_km=150.0,
        status="published",
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


class TestLikeTrip:
    """Tests for LikeService.like_trip() - T041, T044, T045."""

    async def test_like_trip_success(
        self, db_session: AsyncSession, liker_user: User, published_trip: Trip
    ):
        """
        T041: Test successful like creation.

        Given a published trip
        When a user likes the trip
        Then a Like record is created
        And the response includes user and trip details
        """
        # Act
        result = await LikeService.like_trip(
            db=db_session, user_id=liker_user.id, trip_id=published_trip.trip_id
        )

        # Assert
        assert result["like_id"] is not None
        assert result["user_id"] == liker_user.id
        assert result["trip_id"] == published_trip.trip_id
        assert result["created_at"] is not None

        # Verify Like was created in database
        stmt = select(Like).where(
            Like.user_id == liker_user.id, Like.trip_id == published_trip.trip_id
        )
        db_like = (await db_session.execute(stmt)).scalar_one_or_none()
        assert db_like is not None
        assert db_like.user_id == liker_user.id
        assert db_like.trip_id == published_trip.trip_id

    async def test_like_trip_duplicate_fails(
        self, db_session: AsyncSession, liker_user: User, published_trip: Trip
    ):
        """
        T044: Test preventing duplicate likes (FR-010).

        Given a user has already liked a trip
        When the user tries to like the same trip again
        Then a ValueError is raised with error code DUPLICATE_LIKE
        """
        # Arrange: Create initial like
        await LikeService.like_trip(
            db=db_session, user_id=liker_user.id, trip_id=published_trip.trip_id
        )

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await LikeService.like_trip(
                db=db_session, user_id=liker_user.id, trip_id=published_trip.trip_id
            )

        assert "Ya has dado like a este viaje" in str(exc_info.value)

    async def test_like_own_trip_fails(
        self, db_session: AsyncSession, trip_owner: User, published_trip: Trip
    ):
        """
        T045: Test preventing self-likes (FR-011).

        Given a user owns a trip
        When the user tries to like their own trip
        Then a ValueError is raised with error code SELF_LIKE
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await LikeService.like_trip(
                db=db_session, user_id=trip_owner.id, trip_id=published_trip.trip_id
            )

        assert "No puedes dar like a tu propio viaje" in str(exc_info.value)

    async def test_like_nonexistent_trip_fails(self, db_session: AsyncSession, liker_user: User):
        """Test liking a non-existent trip raises ValueError."""
        fake_trip_id = str(uuid4())

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await LikeService.like_trip(db=db_session, user_id=liker_user.id, trip_id=fake_trip_id)

        assert "Viaje no encontrado" in str(exc_info.value)

    async def test_like_draft_trip_fails(
        self, db_session: AsyncSession, liker_user: User, trip_owner: User
    ):
        """Test liking a draft trip raises ValueError."""
        # Arrange: Create draft trip
        draft_trip = Trip(
            trip_id=str(uuid4()),
            user_id=trip_owner.id,
            title="Draft Trip",
            description="This is a draft",
            start_date="2024-06-01",
            distance_km=100.0,
            status="draft",
        )
        db_session.add(draft_trip)
        await db_session.commit()

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await LikeService.like_trip(
                db=db_session, user_id=liker_user.id, trip_id=draft_trip.trip_id
            )

        assert "Solo puedes dar like a viajes publicados" in str(exc_info.value)


class TestUnlikeTrip:
    """Tests for LikeService.unlike_trip() - T042."""

    async def test_unlike_trip_success(
        self, db_session: AsyncSession, liker_user: User, published_trip: Trip
    ):
        """
        T042: Test successful unlike.

        Given a user has liked a trip
        When the user unlikes the trip
        Then the Like record is deleted
        And success response is returned
        """
        # Arrange: Create like
        await LikeService.like_trip(
            db=db_session, user_id=liker_user.id, trip_id=published_trip.trip_id
        )

        # Act
        result = await LikeService.unlike_trip(
            db=db_session, user_id=liker_user.id, trip_id=published_trip.trip_id
        )

        # Assert
        assert result["success"] is True
        assert result["message"] == "Like eliminado correctamente"

        # Verify Like was deleted from database
        stmt = select(Like).where(
            Like.user_id == liker_user.id, Like.trip_id == published_trip.trip_id
        )
        db_like = (await db_session.execute(stmt)).scalar_one_or_none()
        assert db_like is None

    async def test_unlike_trip_not_liked_fails(
        self, db_session: AsyncSession, liker_user: User, published_trip: Trip
    ):
        """
        Test unliking a trip that wasn't liked raises ValueError.

        Given a user has NOT liked a trip
        When the user tries to unlike it
        Then a ValueError is raised
        """
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await LikeService.unlike_trip(
                db=db_session, user_id=liker_user.id, trip_id=published_trip.trip_id
            )

        assert "No has dado like a este viaje" in str(exc_info.value)


class TestGetTripLikes:
    """Tests for LikeService.get_trip_likes() - T043."""

    async def test_get_trip_likes_pagination(self, db_session: AsyncSession, published_trip: Trip):
        """
        T043: Test pagination for trip likes.

        Given a trip has 15 likes
        When fetching likes with page=1, limit=10
        Then 10 likes are returned
        And has_more is True
        And total_count is 15
        """
        # Arrange: Create 15 users who like the trip
        for i in range(15):
            user = User(
                id=str(uuid4()),
                username=f"liker_{i}",
                email=f"liker{i}@test.com",
                hashed_password="hashed",
                is_verified=True,
                is_active=True,
            )
            db_session.add(user)
            await db_session.flush()

            await LikeService.like_trip(
                db=db_session, user_id=user.id, trip_id=published_trip.trip_id
            )

        await db_session.commit()

        # Act: Get first page
        result = await LikeService.get_trip_likes(
            db=db_session, trip_id=published_trip.trip_id, page=1, limit=10
        )

        # Assert
        assert len(result["likes"]) == 10
        assert result["total_count"] == 15
        assert result["page"] == 1
        assert result["limit"] == 10
        assert result["has_more"] is True

        # Act: Get second page
        result_page2 = await LikeService.get_trip_likes(
            db=db_session, trip_id=published_trip.trip_id, page=2, limit=10
        )

        # Assert
        assert len(result_page2["likes"]) == 5
        assert result_page2["total_count"] == 15
        assert result_page2["page"] == 2
        assert result_page2["has_more"] is False

    async def test_get_trip_likes_empty(self, db_session: AsyncSession, published_trip: Trip):
        """
        Test fetching likes for a trip with no likes.

        Given a trip has no likes
        When fetching likes
        Then empty list is returned
        And total_count is 0
        """
        # Act
        result = await LikeService.get_trip_likes(
            db=db_session, trip_id=published_trip.trip_id, page=1, limit=10
        )

        # Assert
        assert result["likes"] == []
        assert result["total_count"] == 0
        assert result["has_more"] is False

    async def test_get_trip_likes_includes_user_details(
        self, db_session: AsyncSession, liker_user: User, published_trip: Trip
    ):
        """
        Test that likes include user details (username, profile photo).

        Given a trip has likes
        When fetching likes
        Then each like includes user details
        """
        # Arrange
        await LikeService.like_trip(
            db=db_session, user_id=liker_user.id, trip_id=published_trip.trip_id
        )

        # Act
        result = await LikeService.get_trip_likes(
            db=db_session, trip_id=published_trip.trip_id, page=1, limit=10
        )

        # Assert
        assert len(result["likes"]) == 1
        like = result["likes"][0]
        assert like["user"]["username"] == liker_user.username
        assert "profile_photo_url" in like["user"]
        assert like["created_at"] is not None
