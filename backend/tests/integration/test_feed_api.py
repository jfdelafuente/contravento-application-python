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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_feed_pagination_no_duplicates(
    client: AsyncClient,
    db_session: AsyncSession,
    current_user: User,  # testuser_pagination from fixture
):
    """
    Bug #1 Fix Verification: Test that pagination doesn't return duplicate trips.

    Sequential Algorithm:
    1. Show ALL trips from followed users first (pages 1...N)
    2. When exhausted, show community backfill (pages N+1...)
    3. No duplicates possible due to sequential ordering

    Test Scenario:
    - testuser_pagination (current_user) follows user1 (has 7 trips)
    - testuser_pagination doesn't follow user2 (has 5 trips)
    - Pagination: limit=5 per page
    - Page 1: 5 followed trips (user1)
    - Page 2: 2 followed trips + 3 community trips
    - Page 3: 2 community trips
    - No trip should appear more than once
    """
    from src.models.user import UserProfile
    from src.utils.security import create_access_token

    testuser_id = current_user.id

    # Create user1 (followed) with 7 trips
    user1 = User(
        username="user1_followed",
        email="user1@example.com",
        hashed_password="$2b$12$dummyhash",
        is_verified=True,
    )
    db_session.add(user1)
    await db_session.flush()

    # Create profile for user1
    profile1 = UserProfile(user_id=user1.id)
    db_session.add(profile1)

    # Create user2 (not followed) with 5 trips
    user2 = User(
        username="user2_community",
        email="user2@example.com",
        hashed_password="$2b$12$dummyhash",
        is_verified=True,
    )
    db_session.add(user2)
    await db_session.flush()

    # Create profile for user2
    profile2 = UserProfile(user_id=user2.id)
    db_session.add(profile2)

    # testuser follows user1
    follow = Follow(id=str(uuid.uuid4()), follower_id=testuser_id, following_id=user1.id)
    db_session.add(follow)

    # Create 7 trips for user1 (followed)
    user1_trip_ids = []
    for i in range(7):
        trip = Trip(
            trip_id=str(uuid.uuid4()),
            user_id=user1.id,
            title=f"User1 Trip {i+1}",
            description="Published trip from followed user",
            start_date=datetime.now(UTC).date(),
            status=TripStatus.PUBLISHED,
            published_at=datetime.now(UTC),
        )
        db_session.add(trip)
        user1_trip_ids.append(trip.trip_id)

    # Create 5 trips for user2 (community)
    user2_trip_ids = []
    for i in range(5):
        trip = Trip(
            trip_id=str(uuid.uuid4()),
            user_id=user2.id,
            title=f"User2 Trip {i+1}",
            description="Published trip from community",
            start_date=datetime.now(UTC).date(),
            status=TripStatus.PUBLISHED,
            published_at=datetime.now(UTC),
        )
        db_session.add(trip)
        user2_trip_ids.append(trip.trip_id)

    await db_session.commit()

    # Create auth headers for testuser_pagination
    token = create_access_token({"sub": current_user.id, "username": current_user.username})
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch all pages and collect all trip IDs
    all_trip_ids = []
    page = 1
    limit = 5

    while True:
        response = await client.get(
            f"/feed?page={page}&limit={limit}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Collect trip IDs from this page
        page_trip_ids = [trip["trip_id"] for trip in data["trips"]]
        all_trip_ids.extend(page_trip_ids)

        # Check for duplicates within this page
        assert len(page_trip_ids) == len(set(page_trip_ids)), (
            f"Page {page} contains duplicate trips"
        )

        if not data["has_more"]:
            break

        page += 1

    # Verify NO duplicates across ALL pages
    unique_trip_ids = set(all_trip_ids)
    assert len(all_trip_ids) == len(unique_trip_ids), (
        f"Found {len(all_trip_ids) - len(unique_trip_ids)} duplicate trips across pages. "
        f"Total trips: {len(all_trip_ids)}, Unique: {len(unique_trip_ids)}"
    )

    # Verify total count matches
    assert len(all_trip_ids) == 12, (
        f"Expected 12 total trips (7 followed + 5 community), got {len(all_trip_ids)}"
    )

    # Verify sequential ordering: all user1 trips should appear before user2 trips
    user1_indices = [i for i, tid in enumerate(all_trip_ids) if tid in user1_trip_ids]
    user2_indices = [i for i, tid in enumerate(all_trip_ids) if tid in user2_trip_ids]

    # All user1 trips (followed) should appear before any user2 trip (community)
    if user1_indices and user2_indices:
        last_user1_index = max(user1_indices)
        first_user2_index = min(user2_indices)
        assert last_user1_index < first_user2_index, (
            f"Sequential algorithm violated: followed trips should appear before community trips. "
            f"Last user1 at index {last_user1_index}, first user2 at index {first_user2_index}"
        )
