"""
Integration tests for Activity Feed API (Feature 018 - T031 to T032).

Tests the complete request/response cycle for GET /activity-feed endpoint.
"""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.activity_feed_item import ActivityFeedItem, ActivityType
from src.models.social import Follow
from src.models.user import User, UserProfile


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_activity_feed_authenticated(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T031: Test GET /activity-feed returns 200 for authenticated user.

    Integration test for FR-001 (Feature 018):
    - Authenticated user can access activity feed
    - Returns valid ActivityFeedResponseSchema structure
    - Status code 200
    """
    response = await client.get("/activity-feed", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate response structure (cursor-based pagination)
    assert "activities" in data
    assert "next_cursor" in data
    assert "has_next" in data

    # Validate types
    assert isinstance(data["activities"], list)
    assert data["next_cursor"] is None or isinstance(data["next_cursor"], str)
    assert isinstance(data["has_next"], bool)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_activity_feed_unauthorized(client: AsyncClient):
    """
    T031: Test GET /activity-feed returns 401 for unauthenticated user.

    Integration test for security:
    - Activity feed requires authentication
    - Returns 401 without valid JWT token
    """
    # No auth headers
    response = await client.get("/activity-feed")

    assert response.status_code == 401

    data = response.json()
    assert not data.get("success", True)  # Standardized error format
    assert "error" in data or "detail" in data  # FastAPI might return detail


@pytest.mark.integration
@pytest.mark.asyncio
async def test_activity_feed_returns_followed_users_activities(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T031: Test activity feed returns activities from followed users only.

    Integration test for FR-001:
    - Feed shows activities from users that current user follows
    - Ordered chronologically DESC (most recent first)
    - Includes all activity types (TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED)
    """
    from sqlalchemy import select

    # Get the authenticated user (created by auth_headers fixture)
    result = await db_session.execute(select(User).where(User.username == "admin_user"))
    current_user = result.scalar_one()

    # Create followed user
    followed_user = User(
        id="user_followed",
        username="maria_test",
        email="maria@test.com",
        hashed_password="hash",
    )

    followed_user_profile = UserProfile(
        user_id=followed_user.id,
        profile_photo_url="/storage/profile_photos/maria.jpg",
    )

    # Current user follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Maria has activities
    activity1 = ActivityFeedItem(
        activity_id="act1",
        user_id=followed_user.id,
        activity_type=ActivityType.TRIP_PUBLISHED,
        related_id="trip1",
        activity_metadata='{"trip_title": "Ruta Pirineos"}',
        created_at=datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC),
    )

    activity2 = ActivityFeedItem(
        activity_id="act2",
        user_id=followed_user.id,
        activity_type=ActivityType.PHOTO_UPLOADED,
        related_id="photo1",
        activity_metadata='{"photo_url": "/storage/photos/pic.jpg", "trip_title": "Ruta Costa"}',
        created_at=datetime(2024, 6, 16, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all(
        [current_user, followed_user, followed_user_profile, follow, activity1, activity2]
    )
    await db_session.commit()

    response = await client.get("/activity-feed?limit=10", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Should have activities from followed user
    assert len(data["activities"]) >= 2

    # Verify activities are ordered DESC (most recent first)
    activities = data["activities"]
    for i in range(len(activities) - 1):
        current_time = datetime.fromisoformat(activities[i]["created_at"].replace("Z", "+00:00"))
        next_time = datetime.fromisoformat(activities[i + 1]["created_at"].replace("Z", "+00:00"))
        assert current_time >= next_time, "Activities should be ordered DESC by created_at"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_activity_feed_cursor_pagination(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T032: Test activity feed cursor-based pagination.

    Integration test for FR-003:
    - First page returns activities + next_cursor
    - Next page uses cursor to fetch more activities
    - Last page has next_cursor = null and has_next = false
    """
    from sqlalchemy import select

    # Get the authenticated user (created by auth_headers fixture)
    result = await db_session.execute(select(User).where(User.username == "admin_user"))
    current_user = result.scalar_one()

    # Create followed user
    followed_user = User(
        id="user_followed_paginate",
        username="maria_paginate",
        email="maria_paginate@test.com",
        hashed_password="hash",
    )

    # Current user follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Create 5 activities for pagination test
    activities = []
    for i in range(5):
        activity = ActivityFeedItem(
            activity_id=f"act_page_{i}",
            user_id=followed_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id=f"trip_{i}",
            activity_metadata=f'{{"trip_title": "Trip {i}"}}',
            created_at=datetime(2024, 6, 15 + i, 10, 0, 0, tzinfo=UTC),
        )
        activities.append(activity)

    db_session.add_all([current_user, followed_user, follow] + activities)
    await db_session.commit()

    # Test first page (limit=2)
    response = await client.get("/activity-feed?limit=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert len(data["activities"]) == 2
    assert data["has_next"] is True
    assert data["next_cursor"] is not None

    # Test second page (using cursor)
    next_cursor = data["next_cursor"]
    response2 = await client.get(
        f"/activity-feed?limit=2&cursor={next_cursor}", headers=auth_headers
    )

    assert response2.status_code == 200
    data2 = response2.json()

    assert len(data2["activities"]) == 2
    assert data2["has_next"] is True

    # Test last page
    next_cursor2 = data2["next_cursor"]
    response3 = await client.get(
        f"/activity-feed?limit=2&cursor={next_cursor2}", headers=auth_headers
    )

    assert response3.status_code == 200
    data3 = response3.json()

    assert len(data3["activities"]) == 1  # Only 1 activity left
    assert data3["has_next"] is False
    assert data3["next_cursor"] is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_activity_feed_includes_user_metadata(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T032: Test activity feed includes user metadata (username, photo_url).

    Integration test for FR-004:
    - Each activity includes user information
    - User photo_url comes from UserProfile
    - Activity metadata is included (trip_title, etc.)
    """
    from sqlalchemy import select

    # Get the authenticated user (created by auth_headers fixture)
    result = await db_session.execute(select(User).where(User.username == "admin_user"))
    current_user = result.scalar_one()

    # Create followed user
    followed_user = User(
        id="user_followed_metadata",
        username="maria_metadata",
        email="maria_metadata@test.com",
        hashed_password="hash",
    )

    followed_user_profile = UserProfile(
        user_id=followed_user.id,
        profile_photo_url="/storage/profile_photos/maria_meta.jpg",
    )

    # Current user follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Maria has an activity
    activity = ActivityFeedItem(
        activity_id="act_meta",
        user_id=followed_user.id,
        activity_type=ActivityType.TRIP_PUBLISHED,
        related_id="trip_meta",
        activity_metadata='{"trip_title": "Ruta Metadata Test"}',
        created_at=datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([current_user, followed_user, followed_user_profile, follow, activity])
    await db_session.commit()

    response = await client.get("/activity-feed?limit=10", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert len(data["activities"]) >= 1

    # Verify first activity has user metadata
    activity_item = data["activities"][0]

    assert "user" in activity_item
    user_info = activity_item["user"]

    assert user_info["user_id"] == followed_user.id
    assert user_info["username"] == "maria_metadata"
    assert user_info["photo_url"] == "/storage/profile_photos/maria_meta.jpg"

    # Verify activity metadata is included
    assert activity_item["activity_type"] == "TRIP_PUBLISHED"
    assert "trip_title" in activity_item["metadata"]
    assert activity_item["metadata"]["trip_title"] == "Ruta Metadata Test"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_activity_feed_empty_when_following_nobody(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T032: Test activity feed returns empty list when user follows nobody.

    Integration test for edge case:
    - User follows nobody
    - Feed returns empty activities list
    - Valid response structure
    """
    # The authenticated user (admin_user from auth_headers) doesn't follow anyone by default
    # No need to create additional data

    response = await client.get("/activity-feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["activities"] == []
    assert data["has_next"] is False
    assert data["next_cursor"] is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_activity_feed_pagination_limit_validation(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    T032: Test activity feed validates limit parameter (1-50).

    Integration test for FR-003:
    - Invalid limit (< 1) returns 400 or 422 Validation Error
    - Invalid limit (> 50) returns 400 or 422 Validation Error
    - Valid limits (1-50) work correctly
    """
    # Invalid limit (too small)
    response = await client.get("/activity-feed?limit=0", headers=auth_headers)
    assert response.status_code in [400, 422]  # Validation error

    # Invalid limit (too large)
    response = await client.get("/activity-feed?limit=51", headers=auth_headers)
    assert response.status_code in [400, 422]  # Validation error

    # Valid limit (boundary values)
    response = await client.get("/activity-feed?limit=1", headers=auth_headers)
    assert response.status_code == 200

    response = await client.get("/activity-feed?limit=50", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_activity_feed_invalid_cursor_ignored(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    T032: Test activity feed handles invalid cursor gracefully.

    Integration test for error handling:
    - Invalid cursor is ignored (treated as null)
    - Returns first page of results
    - Does not crash with 500 error
    """
    # Invalid cursor (garbage string)
    response = await client.get("/activity-feed?cursor=invalid_base64", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Should return first page (cursor ignored)
    assert "activities" in data
    assert isinstance(data["activities"], list)
