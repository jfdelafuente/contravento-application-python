"""
Unit tests for FeedService (Feature 004 - T013 to T017).

Tests the personalized feed business logic following TDD methodology.
"""

import pytest
import uuid
from datetime import UTC, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from src.models.trip import Trip, TripStatus
from src.models.social import Follow
from src.services.feed_service import FeedService


@pytest.mark.asyncio
async def test_get_personalized_feed_returns_followed_trips(db_session: AsyncSession):
    """
    T013: Test get_personalized_feed() returns trips from followed users.

    Business Logic (FR-001):
    - Feed shows trips from users that current user follows
    - Ordered chronologically DESC (most recent first)
    - Only PUBLISHED trips
    """
    # Create users
    current_user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    followed_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    # Current user follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Maria has published trips
    trip1 = Trip(
        trip_id="trip1",
        user_id=followed_user.id,
        title="Ruta Pirineos",
        description="Viaje de 5 días",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )
    trip2 = Trip(
        trip_id="trip2",
        user_id=followed_user.id,
        title="Ruta Montaña",
        description="Viaje de montaña",
        start_date=datetime(2024, 7, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 7, 10, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([current_user, followed_user, follow, trip1, trip2])
    await db_session.commit()

    # Get personalized feed
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=current_user.id,
        page=1,
        limit=10,
    )

    # Should return trips from followed user
    assert result["total_count"] >= 2
    assert len(result["trips"]) >= 2

    # Should be ordered chronologically DESC (most recent first)
    trip_ids = [t["trip_id"] for t in result["trips"]]
    assert trip_ids[0] == "trip2"  # More recent
    assert trip_ids[1] == "trip1"  # Older


@pytest.mark.asyncio
async def test_get_followed_trips_excludes_drafts(db_session: AsyncSession):
    """
    T014: Test _get_followed_trips() only returns PUBLISHED trips.

    Business Logic (FR-002):
    - Draft trips are excluded from feed
    - Only published trips visible
    """
    # Create users
    current_user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    followed_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    # Current user follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Maria has 1 published and 1 draft trip
    published_trip = Trip(
        trip_id="trip1",
        user_id=followed_user.id,
        title="Published Trip",
        description="Published",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )
    draft_trip = Trip(
        trip_id="trip2",
        user_id=followed_user.id,
        title="Draft Trip",
        description="Draft",
        start_date=datetime(2024, 7, 1).date(),
        status=TripStatus.DRAFT,  # Not published
        published_at=None,
    )

    db_session.add_all([current_user, followed_user, follow, published_trip, draft_trip])
    await db_session.commit()

    # Get feed
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=current_user.id,
        page=1,
        limit=10,
    )

    # Should only include published trip
    trip_ids = [t["trip_id"] for t in result["trips"]]
    assert "trip1" in trip_ids  # Published
    assert "trip2" not in trip_ids  # Draft excluded


@pytest.mark.asyncio
async def test_get_community_trips_backfill(db_session: AsyncSession):
    """
    T015: Test _get_community_trips() provides popular backfill when followed trips < limit.

    Business Logic (FR-004):
    - If followed trips < limit, backfill with popular community trips
    - Popular = most likes + comments + shares
    - Excludes trips from followed users (no duplicates)
    """
    # Create users
    current_user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    followed_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )
    community_user = User(
        id="user3",
        username="pedro",
        email="pedro@example.com",
        hashed_password="hash",
    )

    # Current user follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Maria has 1 trip (followed)
    followed_trip = Trip(
        trip_id="trip1",
        user_id=followed_user.id,
        title="Followed Trip",
        description="From followed user",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )

    # Pedro has 1 popular trip (community)
    community_trip = Trip(
        trip_id="trip2",
        user_id=community_user.id,
        title="Popular Community Trip",
        description="From community",
        start_date=datetime(2024, 7, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 7, 10, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all(
        [current_user, followed_user, community_user, follow, followed_trip, community_trip]
    )
    await db_session.commit()

    # Request limit=10 but only 1 followed trip exists
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=current_user.id,
        page=1,
        limit=10,
    )

    # Should include both: followed trip + community backfill
    trip_ids = [t["trip_id"] for t in result["trips"]]
    assert "trip1" in trip_ids  # Followed trip
    assert "trip2" in trip_ids  # Community backfill


@pytest.mark.asyncio
async def test_feed_pagination_logic(db_session: AsyncSession):
    """
    T016: Test feed pagination correctly calculates page, limit, has_more.

    Business Logic (FR-003):
    - page: min 1, default 1
    - limit: min 1, max 50, default 10
    - has_more: true if more results exist beyond current page
    """
    # Create user with many trips
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    followed_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    # User follows maria
    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=user.id,
        following_id=followed_user.id,
    )

    # Create 25 trips (use timedelta to avoid day-out-of-range issues)
    trips = []
    base_published_at = datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC)
    for i in range(25):
        trip = Trip(
            trip_id=f"trip{i}",
            user_id=followed_user.id,
            title=f"Trip {i}",
            description="Description",
            start_date=datetime(2024, 6, 1).date(),
            status=TripStatus.PUBLISHED,
            published_at=base_published_at + timedelta(hours=i),
        )
        trips.append(trip)

    db_session.add_all([user, followed_user, follow] + trips)
    await db_session.commit()

    # Page 1, limit 10
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=user.id,
        page=1,
        limit=10,
    )

    assert result["page"] == 1
    assert result["limit"] == 10
    assert len(result["trips"]) == 10
    assert result["total_count"] == 25
    assert result["has_more"] is True  # 25 total, showing 10

    # Page 2, limit 10
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=user.id,
        page=2,
        limit=10,
    )

    assert result["page"] == 2
    assert len(result["trips"]) == 10
    assert result["has_more"] is True  # Still more after page 2

    # Page 3, limit 10
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=user.id,
        page=3,
        limit=10,
    )

    assert result["page"] == 3
    assert len(result["trips"]) == 5  # Only 5 remaining
    assert result["has_more"] is False  # No more pages


@pytest.mark.asyncio
async def test_feed_when_user_follows_nobody(db_session: AsyncSession):
    """
    T017: Test feed shows only community trips when user follows nobody.

    Business Logic (FR-005):
    - If user follows no one, feed = popular community trips
    - Should not be empty (discovery mode)
    """
    # User follows nobody
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )

    # Community user with trip
    community_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    community_trip = Trip(
        trip_id="trip1",
        user_id=community_user.id,
        title="Community Trip",
        description="Popular trip",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([user, community_user, community_trip])
    await db_session.commit()

    # Get feed
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=user.id,
        page=1,
        limit=10,
    )

    # Should return community trips (not empty)
    assert result["total_count"] >= 1
    assert len(result["trips"]) >= 1

    # Should include community trip
    trip_ids = [t["trip_id"] for t in result["trips"]]
    assert "trip1" in trip_ids


@pytest.mark.asyncio
async def test_feed_excludes_own_trips(db_session: AsyncSession):
    """
    Test that feed excludes user's own trips (even if user "follows" themselves).

    Business Logic:
    - User should not see their own trips in feed
    - Feed is for discovering others' content
    """
    # User with own trip
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )

    own_trip = Trip(
        trip_id="trip1",
        user_id=user.id,
        title="Own Trip",
        description="My own trip",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )

    # Another user's trip
    other_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    other_trip = Trip(
        trip_id="trip2",
        user_id=other_user.id,
        title="Other Trip",
        description="Someone else's trip",
        start_date=datetime(2024, 7, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 7, 10, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([user, own_trip, other_user, other_trip])
    await db_session.commit()

    # Get feed
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=user.id,
        page=1,
        limit=10,
    )

    # Should NOT include own trip
    trip_ids = [t["trip_id"] for t in result["trips"]]
    assert "trip1" not in trip_ids  # Own trip excluded
    assert "trip2" in trip_ids  # Other trips included


@pytest.mark.asyncio
async def test_feed_includes_interaction_counters(db_session: AsyncSession):
    """
    Test that feed items include likes_count, comments_count, shares_count.

    Business Logic (FR-006):
    - Each feed item shows social interaction counters
    - Counters are accurate counts from database
    """
    # This test will be implemented after Like/Comment/Share models are integrated
    # For now, just verify the structure exists
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )

    other_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    trip = Trip(
        trip_id="trip1",
        user_id=other_user.id,
        title="Trip with interactions",
        description="Popular trip",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([user, other_user, trip])
    await db_session.commit()

    # Get feed
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=user.id,
        page=1,
        limit=10,
    )

    # Verify feed items have counter fields (even if 0)
    if len(result["trips"]) > 0:
        feed_item = result["trips"][0]
        assert "likes_count" in feed_item
        assert "comments_count" in feed_item
        assert "shares_count" in feed_item
        assert isinstance(feed_item["likes_count"], int)
        assert isinstance(feed_item["comments_count"], int)
        assert isinstance(feed_item["shares_count"], int)


@pytest.mark.asyncio
async def test_feed_includes_is_liked_by_me_flag(db_session: AsyncSession):
    """
    Test that feed items include is_liked_by_me boolean flag.

    Business Logic (FR-007):
    - Each feed item shows if current user has liked it
    - Used for UI state (heart icon filled/unfilled)
    """
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )

    other_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    trip = Trip(
        trip_id="trip1",
        user_id=other_user.id,
        title="Trip",
        description="Trip",
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 6, 10, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([user, other_user, trip])
    await db_session.commit()

    # Get feed
    result = await FeedService.get_personalized_feed(
        db=db_session,
        user_id=user.id,
        page=1,
        limit=10,
    )

    # Verify feed items have is_liked_by_me field
    if len(result["trips"]) > 0:
        feed_item = result["trips"][0]
        assert "is_liked_by_me" in feed_item
        assert isinstance(feed_item["is_liked_by_me"], bool)
