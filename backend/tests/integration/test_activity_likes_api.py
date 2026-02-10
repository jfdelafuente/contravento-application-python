"""
Integration tests for Activity Likes API endpoints (Feature 018 - US2).

Tests:
- POST /activities/{id}/like
- DELETE /activities/{id}/like
- GET /activities/{id}/likes
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models.activity_feed_item import ActivityFeedItem, ActivityType
from src.models.activity_like import ActivityLike


@pytest.mark.asyncio
class TestActivityLikesAPI:
    """Integration tests for activity likes endpoints."""

    async def test_like_activity_success(
        self, async_client: AsyncClient, auth_headers, test_user, test_user2, db_session
    ):
        """
        T053: Test POST /activities/{id}/like creates like and returns 201.

        Verifies:
        - Like created in database
        - Returns 201 with LikeResponse
        - Notification created for activity author
        """
        # Create activity by test_user
        activity = ActivityFeedItem(
            activity_id="act-api-test",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-api-test",
            activity_metadata={"trip_title": "API Test Trip"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Get auth headers for test_user2
        headers_user2 = await auth_headers(test_user2)

        # Like activity as test_user2
        response = await async_client.post(
            f"/activities/{activity.activity_id}/like", headers=headers_user2
        )

        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["like_id"] is not None
        assert data["user_id"] == test_user2.id
        assert data["activity_id"] == activity.activity_id
        assert "created_at" in data

        # Verify like in database
        stmt = select(ActivityLike).where(
            ActivityLike.user_id == test_user2.id,
            ActivityLike.activity_id == activity.activity_id,
        )
        result = await db_session.execute(stmt)
        like_in_db = result.scalar_one_or_none()
        assert like_in_db is not None

        # NOTE: Notification creation disabled in US2 (see T051)
        # Will be re-enabled when Notification schema supports activity_id

    async def test_like_activity_idempotent(
        self, async_client: AsyncClient, auth_headers, test_user, test_user2, db_session
    ):
        """Test liking same activity twice returns existing like (idempotent)."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-idempotent-api",
            user_id=test_user.id,
            activity_type=ActivityType.PHOTO_UPLOADED,
            related_id="photo-idempotent-api",
            activity_metadata={"photo_url": "/photos/test.jpg"},
        )
        db_session.add(activity)
        await db_session.commit()

        headers_user2 = await auth_headers(test_user2)

        # First like
        response1 = await async_client.post(
            f"/activities/{activity.activity_id}/like", headers=headers_user2
        )
        assert response1.status_code == 201
        like_id_1 = response1.json()["like_id"]

        # Second like (duplicate)
        response2 = await async_client.post(
            f"/activities/{activity.activity_id}/like", headers=headers_user2
        )
        assert response2.status_code == 201
        like_id_2 = response2.json()["like_id"]

        # Should return same like ID
        assert like_id_1 == like_id_2

        # Verify only one like in database
        stmt = select(ActivityLike).where(
            ActivityLike.user_id == test_user2.id,
            ActivityLike.activity_id == activity.activity_id,
        )
        result = await db_session.execute(stmt)
        likes = result.scalars().all()
        assert len(likes) == 1

    async def test_like_activity_not_found(
        self, async_client: AsyncClient, auth_headers, test_user
    ):
        """Test liking non-existent activity returns 404."""
        headers = await auth_headers(test_user)

        response = await async_client.post(
            "/activities/non-existent-activity/like", headers=headers
        )

        assert response.status_code == 404

    async def test_like_activity_unauthorized(
        self, async_client: AsyncClient, test_user, db_session
    ):
        """Test liking activity without authentication returns 401."""
        # Create activity (using test_user to satisfy foreign key)
        activity = ActivityFeedItem(
            activity_id="act-unauth",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-unauth",
            activity_metadata={"trip_title": "Unauthorized Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Like without auth headers
        response = await async_client.post(f"/activities/{activity.activity_id}/like")

        assert response.status_code == 401

    async def test_unlike_activity_success(
        self, async_client: AsyncClient, auth_headers, test_user, test_user2, db_session
    ):
        """Test DELETE /activities/{id}/like removes like and returns 204."""
        # Create activity and like it
        activity = ActivityFeedItem(
            activity_id="act-unlike-api",
            user_id=test_user.id,
            activity_type=ActivityType.ACHIEVEMENT_UNLOCKED,
            related_id="achievement-unlike-api",
            activity_metadata={"achievement_name": "Test Achievement"},
        )
        db_session.add(activity)
        await db_session.commit()

        headers_user2 = await auth_headers(test_user2)

        # Like activity
        await async_client.post(f"/activities/{activity.activity_id}/like", headers=headers_user2)

        # Unlike activity
        response = await async_client.delete(
            f"/activities/{activity.activity_id}/like", headers=headers_user2
        )

        assert response.status_code == 204

        # Verify like deleted from database
        stmt = select(ActivityLike).where(
            ActivityLike.user_id == test_user2.id,
            ActivityLike.activity_id == activity.activity_id,
        )
        result = await db_session.execute(stmt)
        like = result.scalar_one_or_none()
        assert like is None

    async def test_unlike_activity_idempotent(
        self, async_client: AsyncClient, auth_headers, test_user, db_session
    ):
        """Test unliking non-existent like returns 204 (idempotent)."""
        # Create activity without liking it
        activity = ActivityFeedItem(
            activity_id="act-unlike-idempotent-api",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-unlike-idempotent-api",
            activity_metadata={"trip_title": "Unlike Idempotent Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        headers = await auth_headers(test_user)

        # Unlike without having liked
        response = await async_client.delete(
            f"/activities/{activity.activity_id}/like", headers=headers
        )

        assert response.status_code == 204

    async def test_get_activity_likes_success(
        self, async_client: AsyncClient, auth_headers, test_user, test_user2, db_session
    ):
        """Test GET /activities/{id}/likes returns paginated list of likes."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-get-likes",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-get-likes",
            activity_metadata={"trip_title": "Get Likes Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        headers_user2 = await auth_headers(test_user2)

        # Add likes from both users
        await async_client.post(
            f"/activities/{activity.activity_id}/like", headers=await auth_headers(test_user)
        )
        await async_client.post(f"/activities/{activity.activity_id}/like", headers=headers_user2)

        # Get likes (public endpoint - no auth required)
        response = await async_client.get(
            f"/activities/{activity.activity_id}/likes?page=1&limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert len(data["likes"]) == 2
        assert data["page"] == 1
        assert data["limit"] == 10
        assert data["has_next"] is False

        # Verify user information included
        usernames = {like["username"] for like in data["likes"]}
        assert test_user.username in usernames
        assert test_user2.username in usernames

    async def test_get_activity_likes_pagination(
        self, async_client: AsyncClient, auth_headers, test_user, db_session
    ):
        """Test GET /activities/{id}/likes pagination works correctly."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-pagination",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-pagination",
            activity_metadata={"trip_title": "Pagination Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Create 5 users and have them all like the activity
        from src.models.user import User

        for i in range(5):
            user = User(
                id=f"pagination-user-{i}",
                username=f"pagination_user_{i}",
                email=f"pagination{i}@test.com",
                hashed_password="hashed",
            )
            db_session.add(user)
            await db_session.flush()

            headers = await auth_headers(user)
            await async_client.post(f"/activities/{activity.activity_id}/like", headers=headers)

        await db_session.commit()

        # Get page 1 (limit 2)
        response = await async_client.get(
            f"/activities/{activity.activity_id}/likes?page=1&limit=2"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 5
        assert len(data["likes"]) == 2
        assert data["page"] == 1
        assert data["has_next"] is True

        # Get page 2 (limit 2)
        response = await async_client.get(
            f"/activities/{activity.activity_id}/likes?page=2&limit=2"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["likes"]) == 2
        assert data["page"] == 2
        assert data["has_next"] is True

        # Get page 3 (last page, only 1 item)
        response = await async_client.get(
            f"/activities/{activity.activity_id}/likes?page=3&limit=2"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["likes"]) == 1
        assert data["page"] == 3
        assert data["has_next"] is False

    async def test_get_activity_likes_not_found(self, async_client: AsyncClient):
        """Test getting likes for non-existent activity returns 404."""
        response = await async_client.get("/activities/non-existent/likes")

        assert response.status_code == 404

    async def test_get_activity_likes_invalid_pagination(
        self, async_client: AsyncClient, test_user, db_session
    ):
        """Test invalid pagination parameters return 400."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-invalid-pagination",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-invalid-pagination",
            activity_metadata={"trip_title": "Invalid Pagination Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Invalid page (< 1) - Service layer validation returns 400
        response = await async_client.get(
            f"/activities/{activity.activity_id}/likes?page=0&limit=10"
        )
        assert response.status_code == 400

        # Invalid limit (> 50) - Service layer validation returns 400
        response = await async_client.get(
            f"/activities/{activity.activity_id}/likes?page=1&limit=100"
        )
        assert response.status_code == 400
