"""
Unit tests for FeedService (Feature 004 - T013 to T017).

Tests the personalized feed business logic following TDD methodology.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.social import Follow
from src.models.trip import Trip, TripStatus
from src.models.user import User
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
        follower_id=current_user.id,
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
        follower_id=current_user.id,
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
        follower_id=current_user.id,
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
async def test_feed_includes_own_trips(db_session: AsyncSession):
    """
    Test that feed includes user's own trips at the highest priority.

    Business Logic:
    - User should see their own trips first in the personalized feed
    - Own trips appear before followed users' trips
    - Both public and private trips are included (user can see their own private trips)
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

    # Should include own trip at the highest priority
    trip_ids = [t["trip_id"] for t in result["trips"]]
    assert "trip1" in trip_ids  # Own trip included
    assert "trip2" in trip_ids  # Other trips also included
    # Own trip should appear first (highest priority)
    assert trip_ids[0] == "trip1"


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


# ============================================================================
# Feature 018 - Activity Stream Feed Tests (T025-T026)
# ============================================================================


@pytest.mark.asyncio
async def test_get_user_feed_returns_activities_from_followed_users(db_session: AsyncSession):
    """
    T025: Test get_user_feed() returns activities from followed users.

    Business Logic (Feature 018 - FR-001):
    - Activity stream shows TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED
    - Only from users that current user follows
    - Ordered chronologically DESC (most recent first)
    """
    from src.models.activity_feed_item import ActivityFeedItem, ActivityType

    # Create users
    current_user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    followed_user1 = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )
    followed_user2 = User(
        id="user3",
        username="pedro",
        email="pedro@example.com",
        hashed_password="hash",
    )
    unfollowed_user = User(
        id="user4",
        username="ana",
        email="ana@example.com",
        hashed_password="hash",
    )

    # Current user follows maria and pedro
    follow1 = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user1.id,
    )
    follow2 = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user2.id,
    )

    # Create activities
    activity1 = ActivityFeedItem(
        activity_id="act1",
        user_id=followed_user1.id,
        activity_type=ActivityType.TRIP_PUBLISHED,
        related_id="trip1",
        activity_metadata='{"trip_title": "Ruta Pirineos"}',
        created_at=datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC),
    )
    activity2 = ActivityFeedItem(
        activity_id="act2",
        user_id=followed_user2.id,
        activity_type=ActivityType.PHOTO_UPLOADED,
        related_id="photo1",
        activity_metadata='{"photo_count": 5}',
        created_at=datetime(2024, 6, 16, 10, 0, 0, tzinfo=UTC),
    )
    # Activity from unfollowed user (should NOT appear)
    activity3 = ActivityFeedItem(
        activity_id="act3",
        user_id=unfollowed_user.id,
        activity_type=ActivityType.TRIP_PUBLISHED,
        related_id="trip3",
        activity_metadata='{"trip_title": "Should not appear"}',
        created_at=datetime(2024, 6, 17, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all(
        [
            current_user,
            followed_user1,
            followed_user2,
            unfollowed_user,
            follow1,
            follow2,
            activity1,
            activity2,
            activity3,
        ]
    )
    await db_session.commit()

    # Get activity feed
    result = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=20,
        cursor=None,
    )

    # Should return activities from followed users only
    assert len(result["activities"]) == 2
    activity_ids = [act["activity_id"] for act in result["activities"]]
    assert "act1" in activity_ids  # From followed user maria
    assert "act2" in activity_ids  # From followed user pedro
    assert "act3" not in activity_ids  # From unfollowed user (excluded)

    # Should be ordered chronologically DESC (most recent first)
    assert result["activities"][0]["activity_id"] == "act2"  # Most recent
    assert result["activities"][1]["activity_id"] == "act1"  # Older


@pytest.mark.asyncio
async def test_get_user_feed_returns_empty_when_following_nobody(db_session: AsyncSession):
    """
    T025: Test get_user_feed() returns empty feed when user follows nobody.

    Business Logic (Feature 018):
    - If user follows no one, feed should be empty
    - Different from Feature 004 personalized feed (which shows community trips)
    """
    from src.models.activity_feed_item import ActivityFeedItem, ActivityType

    # User follows nobody
    current_user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )

    # Other user with activity
    other_user = User(
        id="user2",
        username="maria",
        email="maria@example.com",
        hashed_password="hash",
    )

    activity = ActivityFeedItem(
        activity_id="act1",
        user_id=other_user.id,
        activity_type=ActivityType.TRIP_PUBLISHED,
        related_id="trip1",
        activity_metadata='{"trip_title": "Should not appear"}',
        created_at=datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([current_user, other_user, activity])
    await db_session.commit()

    # Get feed
    result = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=20,
        cursor=None,
    )

    # Should return empty feed
    assert len(result["activities"]) == 0
    assert result["has_next"] is False
    assert result["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_user_feed_cursor_pagination_first_page(db_session: AsyncSession):
    """
    T026: Test cursor-based pagination (first page).

    Business Logic (Feature 018 - FR-002):
    - First page: cursor=None
    - Returns up to limit activities
    - Provides next_cursor for next page
    - has_next=True if more activities exist
    """
    from src.models.activity_feed_item import ActivityFeedItem, ActivityType

    # Create user and followed user
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

    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Create 25 activities
    activities = []
    base_time = datetime(2024, 6, 1, 10, 0, 0, tzinfo=UTC)
    for i in range(25):
        activity = ActivityFeedItem(
            activity_id=f"act{i}",
            user_id=followed_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id=f"trip{i}",
            activity_metadata=f'{{"trip_title": "Trip {i}"}}',
            created_at=base_time + timedelta(hours=i),
        )
        activities.append(activity)

    db_session.add_all([current_user, followed_user, follow] + activities)
    await db_session.commit()

    # Get first page (limit=10, cursor=None)
    result = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=10,
        cursor=None,
    )

    # Should return 10 activities
    assert len(result["activities"]) == 10

    # Should have next_cursor (more activities exist)
    assert result["next_cursor"] is not None
    assert result["has_next"] is True

    # Should be ordered DESC (most recent first)
    assert result["activities"][0]["activity_id"] == "act24"  # Most recent
    assert result["activities"][9]["activity_id"] == "act15"  # 10th item


@pytest.mark.asyncio
async def test_get_user_feed_cursor_pagination_second_page(db_session: AsyncSession):
    """
    T026: Test cursor-based pagination (second page).

    Business Logic (Feature 018 - FR-003):
    - Second page: use next_cursor from first page
    - Returns next batch of activities
    - Cursor contains (created_at, activity_id) for stable sorting
    """
    from src.models.activity_feed_item import ActivityFeedItem, ActivityType

    # Create user and followed user
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

    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Create 25 activities
    activities = []
    base_time = datetime(2024, 6, 1, 10, 0, 0, tzinfo=UTC)
    for i in range(25):
        activity = ActivityFeedItem(
            activity_id=f"act{i}",
            user_id=followed_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id=f"trip{i}",
            activity_metadata=f'{{"trip_title": "Trip {i}"}}',
            created_at=base_time + timedelta(hours=i),
        )
        activities.append(activity)

    db_session.add_all([current_user, followed_user, follow] + activities)
    await db_session.commit()

    # Get first page to get cursor
    result_page1 = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=10,
        cursor=None,
    )

    # Get second page using cursor from first page
    result_page2 = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=10,
        cursor=result_page1["next_cursor"],
    )

    # Should return next 10 activities
    assert len(result_page2["activities"]) == 10

    # Should NOT overlap with first page
    page1_ids = {act["activity_id"] for act in result_page1["activities"]}
    page2_ids = {act["activity_id"] for act in result_page2["activities"]}
    assert len(page1_ids & page2_ids) == 0  # No overlap

    # Second page should have older activities
    assert result_page2["activities"][0]["activity_id"] == "act14"
    assert result_page2["activities"][9]["activity_id"] == "act5"


@pytest.mark.asyncio
async def test_get_user_feed_cursor_pagination_last_page(db_session: AsyncSession):
    """
    T026: Test cursor pagination (last page).

    Business Logic (Feature 018):
    - Last page: has_next=False
    - next_cursor=None (no more pages)
    - Returns remaining activities (< limit)
    """
    from src.models.activity_feed_item import ActivityFeedItem, ActivityType

    # Create user and followed user
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

    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    # Create only 5 activities
    activities = []
    base_time = datetime(2024, 6, 1, 10, 0, 0, tzinfo=UTC)
    for i in range(5):
        activity = ActivityFeedItem(
            activity_id=f"act{i}",
            user_id=followed_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id=f"trip{i}",
            activity_metadata=f'{{"trip_title": "Trip {i}"}}',
            created_at=base_time + timedelta(hours=i),
        )
        activities.append(activity)

    db_session.add_all([current_user, followed_user, follow] + activities)
    await db_session.commit()

    # Get feed with limit=10 (more than available)
    result = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=10,
        cursor=None,
    )

    # Should return all 5 activities
    assert len(result["activities"]) == 5

    # Should indicate no more pages
    assert result["has_next"] is False
    assert result["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_user_feed_invalid_cursor_ignored(db_session: AsyncSession):
    """
    T026: Test invalid cursor is gracefully ignored.

    Business Logic (Feature 018 - FR-005):
    - Invalid cursor → fallback to first page (cursor=None)
    - No exception raised (graceful degradation)
    """
    from src.models.activity_feed_item import ActivityFeedItem, ActivityType

    # Create user and followed user
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

    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    activity = ActivityFeedItem(
        activity_id="act1",
        user_id=followed_user.id,
        activity_type=ActivityType.TRIP_PUBLISHED,
        related_id="trip1",
        activity_metadata='{"trip_title": "Trip 1"}',
        created_at=datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([current_user, followed_user, follow, activity])
    await db_session.commit()

    # Try with invalid cursor
    result = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=10,
        cursor="invalid_cursor_12345",  # Malformed cursor
    )

    # Should return activities (fallback to first page)
    assert len(result["activities"]) >= 1
    assert "act1" in [act["activity_id"] for act in result["activities"]]


@pytest.mark.asyncio
async def test_get_user_feed_includes_user_metadata(db_session: AsyncSession):
    """
    T025: Test activity feed includes user metadata (username, photo_url).

    Business Logic (Feature 018 - FR-006):
    - Each activity includes minimal user data (PublicUserSummary)
    - username, photo_url for displaying activity author
    """
    from src.models.activity_feed_item import ActivityFeedItem, ActivityType

    # Create users with profile photos
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
        photo_url="/storage/profile_photos/maria.jpg",
    )

    follow = Follow(
        id=str(uuid.uuid4()),
        follower_id=current_user.id,
        following_id=followed_user.id,
    )

    activity = ActivityFeedItem(
        activity_id="act1",
        user_id=followed_user.id,
        activity_type=ActivityType.TRIP_PUBLISHED,
        related_id="trip1",
        activity_metadata='{"trip_title": "Ruta Pirineos"}',
        created_at=datetime(2024, 6, 15, 10, 0, 0, tzinfo=UTC),
    )

    db_session.add_all([current_user, followed_user, follow, activity])
    await db_session.commit()

    # Get feed
    result = await FeedService.get_user_feed(
        db=db_session,
        user_id=current_user.id,

        limit=10,
        cursor=None,
    )

    # Verify user metadata included
    assert len(result["activities"]) == 1
    activity_data = result["activities"][0]

    assert "user" in activity_data
    assert activity_data["user"]["user_id"] == followed_user.id
    assert activity_data["user"]["username"] == "maria"
    assert activity_data["user"]["photo_url"] == "/storage/profile_photos/maria.jpg"
