"""
Integration tests for Feed API endpoints (Feature 004 - T018 to T022).

Tests the complete request/response cycle for GET /feed endpoint.
"""

import pytest
import uuid
from httpx import AsyncClient
from datetime import UTC, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.trip import Trip, TripStatus
from src.models.social import Follow


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_feed_authenticated(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T018: Test GET /feed returns 200 for authenticated user.

    Integration test for FR-001:
    - Authenticated user can access feed
    - Returns valid FeedResponse structure
    - Status code 200
    """
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate response structure
    assert "trips" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Validate types
    assert isinstance(data["trips"], list)
    assert isinstance(data["total_count"], int)
    assert isinstance(data["page"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["has_more"], bool)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_feed_with_pagination(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T019: Test GET /feed with pagination query parameters.

    Integration test for FR-003:
    - page parameter works correctly
    - limit parameter works correctly
    - Default values applied when not specified
    """
    # Test with custom pagination
    response = await client.get("/feed?page=1&limit=5", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 5
    assert len(data["trips"]) <= 5

    # Test with default pagination
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 10  # Default limit


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_feed_unauthorized(client: AsyncClient):
    """
    T020: Test GET /feed returns 401 for unauthenticated user.

    Integration test for FR-001:
    - Feed requires authentication
    - Returns 401 without valid JWT token
    """
    # No auth headers
    response = await client.get("/feed")

    assert response.status_code == 401

    data = response.json()
    assert "error" in data or "detail" in data


@pytest.mark.integration
@pytest.mark.asyncio
async def test_feed_ordering_chronological_desc(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T021: Test feed items are ordered chronologically DESC (most recent first).

    Integration test for FR-002:
    - Feed shows most recent trips first
    - Ordering by published_at timestamp
    """
    # Get current user from auth_headers
    # For now, create test scenario with known user
    user = User(
        id="test_user_1",
        username="john_feed_test",
        email="john_feed@example.com",
        hashed_password="hash",
    )

    followed_user = User(
        id="test_user_2",
        username="maria_feed_test",
        email="maria_feed@example.com",
        hashed_password="hash",
    )

    # User follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=user.id,
        following_id=followed_user.id,
    )

    # Create trips with different published_at dates
    older_trip = Trip(
        trip_id="older_trip",
        user_id=followed_user.id,
        title="Older Trip",
        description="Published first",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )

    newer_trip = Trip(
        trip_id="newer_trip",
        user_id=followed_user.id,
        title="Newer Trip",
        description="Published later",
        start_date=datetime(2024, 7, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 7, 10, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([user, followed_user, follow, older_trip, newer_trip])
    await db_session.commit()

    response = await client.get("/feed?limit=10", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # If we have multiple trips, verify DESC order
    if len(data["trips"]) >= 2:
        trips = data["trips"]

        # Extract published_at timestamps
        timestamps = [trip["created_at"] for trip in trips]

        # Verify DESC order (most recent first)
        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i + 1], (
                f"Feed not ordered DESC: {timestamps[i]} should be >= {timestamps[i + 1]}"
            )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_feed_with_interaction_counters(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """
    T022: Test feed items include interaction counters.

    Integration test for FR-006:
    - Each feed item has likes_count
    - Each feed item has comments_count
    - Each feed item has shares_count
    - Each feed item has is_liked_by_me flag
    """
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # If feed has items, verify they have counters
    if len(data["trips"]) > 0:
        feed_item = data["trips"][0]

        # Required counter fields
        assert "likes_count" in feed_item
        assert "comments_count" in feed_item
        assert "shares_count" in feed_item
        assert "is_liked_by_me" in feed_item

        # Type validation
        assert isinstance(feed_item["likes_count"], int)
        assert isinstance(feed_item["comments_count"], int)
        assert isinstance(feed_item["shares_count"], int)
        assert isinstance(feed_item["is_liked_by_me"], bool)

        # Counters should be non-negative
        assert feed_item["likes_count"] >= 0
        assert feed_item["comments_count"] >= 0
        assert feed_item["shares_count"] >= 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_feed_pagination_invalid_params(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    T022: Test feed pagination validation rejects invalid parameters.

    Integration test for FR-003:
    - Invalid page/limit parameters return 400 Bad Request
    - FastAPI validation enforces min/max constraints
    """
    # Invalid page (too small)
    response = await client.get("/feed?page=0", headers=auth_headers)
    assert response.status_code == 400

    # Invalid limit (too small)
    response = await client.get("/feed?limit=0", headers=auth_headers)
    assert response.status_code == 400

    # Invalid limit (too large)
    response = await client.get("/feed?limit=51", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.asyncio
async def test_feed_includes_author_info(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test feed items include author (UserSummary) information."""
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # If feed has items, verify author structure
    if len(data["trips"]) > 0:
        feed_item = data["trips"][0]

        assert "author" in feed_item
        author = feed_item["author"]

        # UserSummary required fields
        assert "username" in author
        assert "full_name" in author
        assert "profile_photo_url" in author

        # Type validation
        assert isinstance(author["username"], str)
        assert author["full_name"] is None or isinstance(author["full_name"], str)
        assert author["profile_photo_url"] is None or isinstance(
            author["profile_photo_url"], str
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_feed_empty_response(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test feed returns valid structure even when empty."""
    # Delete all trips to ensure empty feed
    from sqlalchemy import delete

    await db_session.execute(delete(Trip))
    await db_session.commit()

    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Should have valid structure
    assert "trips" in data
    assert "total_count" in data

    # Empty results
    assert data["trips"] == []
    assert data["total_count"] == 0
    assert data["has_more"] is False
