"""
Integration tests for Likes API endpoints (Feature 004 - US2: Likes/Me Gusta).

Tests cover:
- T046: POST /trips/{id}/like
- T047: DELETE /trips/{id}/like
- T048: GET /trips/{id}/likes
- T049: Like (unauthorized - 401)
- T050: Duplicate like (400)
- T051: Self-like (400)

Following TDD: These tests are written BEFORE implementation.
"""

from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import Trip
from src.models.user import User, UserProfile


@pytest.fixture
async def trip_owner(db_session: AsyncSession) -> User:
    """Create a trip owner user."""
    user = User(
        id=str(uuid4()),
        username="trip_owner_api",
        email="owner_api@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()  # Get user.id

    profile = UserProfile(user_id=user.id)
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def liker_user(db_session: AsyncSession) -> User:
    """Create a user who will like trips."""
    user = User(
        id=str(uuid4()),
        username="liker_api",
        email="liker_api@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()  # Get user.id

    profile = UserProfile(user_id=user.id)
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def published_trip(db_session: AsyncSession, trip_owner: User) -> Trip:
    """Create a published trip."""
    trip = Trip(
        trip_id=str(uuid4()),
        user_id=trip_owner.id,
        title="API Test Trip",
        description="Testing likes API",
        start_date=date(2024, 6, 1),
        end_date=date(2024, 6, 5),
        distance_km=200.0,
        status="published",
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


class TestPostLike:
    """Tests for POST /trips/{id}/like - T046, T049, T050, T051."""

    async def test_like_trip_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        published_trip: Trip,
    ):
        """
        T046: Test successful like creation via API.

        Given an authenticated user
        When POST /trips/{id}/like is called
        Then 201 status is returned
        And response includes like details
        And success=true
        """
        # Act
        response = await client.post(
            f"/trips/{published_trip.trip_id}/like",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["like_id"] is not None
        assert data["data"]["trip_id"] == published_trip.trip_id
        assert data["data"]["created_at"] is not None

    async def test_like_trip_unauthorized(
        self,
        client: AsyncClient,
        published_trip: Trip,
    ):
        """
        T049: Test like without authentication returns 401.

        Given no authentication token
        When POST /trips/{id}/like is called
        Then 401 status is returned
        And error code is UNAUTHORIZED
        """
        # Act
        response = await client.post(f"/trips/{published_trip.trip_id}/like")

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"

    async def test_like_trip_duplicate(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        published_trip: Trip,
    ):
        """
        T050: Test duplicate like returns 400.

        Given a user has already liked a trip
        When POST /trips/{id}/like is called again
        Then 400 status is returned
        And error code is DUPLICATE_LIKE
        """
        # Arrange: Create first like
        await client.post(
            f"/trips/{published_trip.trip_id}/like",
            headers=auth_headers,
        )

        # Act: Try to like again
        response = await client.post(
            f"/trips/{published_trip.trip_id}/like",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Ya has dado like" in data["error"]["message"]

    async def test_like_own_trip(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        trip_owner: User,
    ):
        """
        T051: Test self-like returns 400.

        Given a user owns a trip
        When the user tries to like their own trip
        Then 400 status is returned
        And error code is SELF_LIKE
        """
        # Arrange: Create trip owned by authenticated user
        trip = Trip(
            trip_id=str(uuid4()),
            user_id=trip_owner.id,
            title="My Own Trip",
            description="Testing self-like",
            start_date=date(2024, 6, 1),
            distance_km=100.0,
            status="published",
            published_at=datetime.now(UTC),
        )
        db_session.add(trip)
        await db_session.commit()

        # Create auth headers for trip owner
        from src.utils.security import create_access_token

        token = create_access_token(subject=trip_owner.id, token_type="access")
        owner_headers = {"Authorization": f"Bearer {token}"}

        # Act
        response = await client.post(
            f"/trips/{trip.trip_id}/like",
            headers=owner_headers,
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "No puedes dar like a tu propio viaje" in data["error"]["message"]

    async def test_like_nonexistent_trip(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test liking a non-existent trip returns 404."""
        fake_trip_id = str(uuid4())

        # Act
        response = await client.post(
            f"/trips/{fake_trip_id}/like",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False


class TestDeleteLike:
    """Tests for DELETE /trips/{id}/like - T047."""

    async def test_unlike_trip_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        published_trip: Trip,
    ):
        """
        T047: Test successful unlike via API.

        Given a user has liked a trip
        When DELETE /trips/{id}/like is called
        Then 200 status is returned
        And success=true
        And message confirms deletion
        """
        # Arrange: Create like
        await client.post(
            f"/trips/{published_trip.trip_id}/like",
            headers=auth_headers,
        )

        # Act
        response = await client.delete(
            f"/trips/{published_trip.trip_id}/like",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "eliminado" in data["data"]["message"]

    async def test_unlike_trip_not_liked(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        published_trip: Trip,
    ):
        """
        Test unliking a trip that wasn't liked returns 400.

        Given a user has NOT liked a trip
        When DELETE /trips/{id}/like is called
        Then 400 status is returned
        """
        # Act
        response = await client.delete(
            f"/trips/{published_trip.trip_id}/like",
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "No has dado like" in data["error"]["message"]

    async def test_unlike_trip_unauthorized(
        self,
        client: AsyncClient,
        published_trip: Trip,
    ):
        """Test unlike without authentication returns 401."""
        # Act
        response = await client.delete(f"/trips/{published_trip.trip_id}/like")

        # Assert
        assert response.status_code == 401


class TestGetTripLikes:
    """Tests for GET /trips/{id}/likes - T048."""

    async def test_get_trip_likes_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        published_trip: Trip,
    ):
        """
        T048: Test fetching trip likes via API.

        Given a trip has 3 likes
        When GET /trips/{id}/likes is called
        Then 200 status is returned
        And response includes 3 likes with user details
        And pagination metadata is included
        """
        # Arrange: Create 3 users who like the trip
        for i in range(3):
            user = User(
                id=str(uuid4()),
                username=f"api_liker_{i}",
                email=f"api_liker{i}@test.com",
                hashed_password="hashed",
                is_verified=True,
                is_active=True,
            )
            db_session.add(user)
            await db_session.flush()

            from src.utils.security import create_access_token

            token = create_access_token(subject=user.id, token_type="access")
            headers = {"Authorization": f"Bearer {token}"}

            await client.post(
                f"/trips/{published_trip.trip_id}/like",
                headers=headers,
            )

        await db_session.commit()

        # Act
        response = await client.get(f"/trips/{published_trip.trip_id}/likes")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["likes"]) == 3
        assert data["data"]["total_count"] == 3
        assert data["data"]["page"] == 1
        assert data["data"]["has_more"] is False

        # Verify user details are included
        like = data["data"]["likes"][0]
        assert "user" in like
        assert "username" in like["user"]
        assert "profile_photo_url" in like["user"]
        assert "created_at" in like

    async def test_get_trip_likes_pagination(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        published_trip: Trip,
    ):
        """
        Test pagination for GET /trips/{id}/likes.

        Given a trip has 15 likes
        When GET /trips/{id}/likes?page=1&limit=10 is called
        Then 10 likes are returned
        And has_more is true
        """
        # Arrange: Create 15 users who like the trip
        for i in range(15):
            user = User(
                id=str(uuid4()),
                username=f"paginated_liker_{i}",
                email=f"paginated{i}@test.com",
                hashed_password="hashed",
                is_verified=True,
                is_active=True,
            )
            db_session.add(user)
            await db_session.flush()

            from src.utils.security import create_access_token

            token = create_access_token(subject=user.id, token_type="access")
            headers = {"Authorization": f"Bearer {token}"}

            await client.post(
                f"/trips/{published_trip.trip_id}/like",
                headers=headers,
            )

        await db_session.commit()

        # Act: Get first page
        response = await client.get(f"/trips/{published_trip.trip_id}/likes?page=1&limit=10")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["likes"]) == 10
        assert data["data"]["total_count"] == 15
        assert data["data"]["has_more"] is True

        # Act: Get second page
        response_page2 = await client.get(f"/trips/{published_trip.trip_id}/likes?page=2&limit=10")

        # Assert
        assert response_page2.status_code == 200
        data_page2 = response_page2.json()
        assert len(data_page2["data"]["likes"]) == 5
        assert data_page2["data"]["has_more"] is False

    async def test_get_trip_likes_empty(
        self,
        client: AsyncClient,
        published_trip: Trip,
    ):
        """Test fetching likes for a trip with no likes."""
        # Act
        response = await client.get(f"/trips/{published_trip.trip_id}/likes")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["likes"] == []
        assert data["data"]["total_count"] == 0

    async def test_get_trip_likes_nonexistent_trip(
        self,
        client: AsyncClient,
    ):
        """Test fetching likes for a non-existent trip returns 404."""
        fake_trip_id = str(uuid4())

        # Act
        response = await client.get(f"/trips/{fake_trip_id}/likes")

        # Assert
        assert response.status_code == 404
