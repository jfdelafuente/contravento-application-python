"""
Unit tests for Activity Feed Triggers (Feature 018 - T033 to T035).

Tests automatic creation of feed activities when users:
- Publish trips (TRIP_PUBLISHED)
- Upload photos (PHOTO_UPLOADED)
- Unlock achievements (ACHIEVEMENT_UNLOCKED)
"""

from datetime import UTC, datetime
from io import BytesIO

import pytest
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.activity_feed_item import ActivityFeedItem, ActivityType
from src.models.stats import Achievement, UserStats
from src.models.trip import Trip, TripStatus
from src.models.user import User, UserProfile
from src.services.stats_service import StatsService
from src.services.trip_service import TripService


@pytest.mark.asyncio
async def test_publish_trip_creates_activity(db_session: AsyncSession):
    """
    T033: Test publishing a trip creates TRIP_PUBLISHED activity.

    Verifies:
    - Activity is created when trip is published
    - Activity has correct type (TRIP_PUBLISHED)
    - Metadata includes trip_title
    - Only created on first publication (idempotent)
    """
    # Create user
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    db_session.add(user)
    await db_session.flush()

    # Create user profile (required for stats)
    profile = UserProfile(user_id=user.id)
    db_session.add(profile)

    # Create user stats
    stats = UserStats(user_id=user.id)
    db_session.add(stats)

    # Create draft trip
    trip = Trip(
        trip_id="trip1",
        user_id=user.id,
        title="Ruta Pirineos",
        description="A" * 60,  # Minimum 50 chars required
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.DRAFT,
    )
    db_session.add(trip)
    await db_session.commit()

    # Verify no activity exists yet
    result = await db_session.execute(select(ActivityFeedItem))
    activities_before = result.scalars().all()
    assert len(activities_before) == 0

    # Publish trip
    trip_service = TripService(db_session)
    await trip_service.publish_trip(trip_id=trip.trip_id, user_id=user.id)

    # Verify activity was created
    result = await db_session.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user.id)
    )
    activities = result.scalars().all()

    assert len(activities) == 1
    activity = activities[0]

    assert activity.activity_type == ActivityType.TRIP_PUBLISHED
    assert activity.related_id == trip.trip_id
    assert activity.user_id == user.id

    # Verify metadata
    import json

    metadata = json.loads(activity.activity_metadata)
    assert metadata["trip_title"] == "Ruta Pirineos"

    # Test idempotency: publish again (should not create duplicate activity)
    await trip_service.publish_trip(trip_id=trip.trip_id, user_id=user.id)

    result = await db_session.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user.id)
    )
    activities_after = result.scalars().all()

    # Still only 1 activity (not duplicated)
    assert len(activities_after) == 1


@pytest.mark.asyncio
async def test_upload_photo_creates_activity_only_if_published(db_session: AsyncSession):
    """
    T034: Test uploading photo creates PHOTO_UPLOADED activity (only for published trips).

    Verifies:
    - Activity is created when photo is uploaded to PUBLISHED trip
    - NO activity created for photos uploaded to DRAFT trips
    - Metadata includes photo_url and trip_title
    """
    # Create user
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    db_session.add(user)
    await db_session.flush()

    # Create user profile and stats
    profile = UserProfile(user_id=user.id)
    stats = UserStats(user_id=user.id)
    db_session.add_all([profile, stats])

    # Create PUBLISHED trip
    trip = Trip(
        trip_id="trip1",
        user_id=user.id,
        title="Ruta Costa",
        description="Beautiful coastal route" * 10,
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.commit()

    # Create test image
    img = Image.new("RGB", (800, 600), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Upload photo
    trip_service = TripService(db_session)
    photo = await trip_service.upload_photo(
        trip_id=trip.trip_id,
        user_id=user.id,
        photo_file=img_bytes,
        filename="test.jpg",
        content_type="image/jpeg",
    )

    # Verify activity was created
    result = await db_session.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user.id)
    )
    activities = result.scalars().all()

    assert len(activities) == 1
    activity = activities[0]

    assert activity.activity_type == ActivityType.PHOTO_UPLOADED
    assert activity.related_id == photo.photo_id
    assert activity.user_id == user.id

    # Verify metadata
    import json

    metadata = json.loads(activity.activity_metadata)
    assert metadata["trip_title"] == "Ruta Costa"
    assert "photo_url" in metadata


@pytest.mark.asyncio
async def test_upload_photo_no_activity_for_draft_trip(db_session: AsyncSession):
    """
    T034: Test uploading photo to DRAFT trip does NOT create activity.

    Verifies:
    - NO activity is created for photos uploaded to draft trips
    - Privacy: draft trips are not visible in feed
    """
    # Create user
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    db_session.add(user)
    await db_session.flush()

    # Create user profile and stats
    profile = UserProfile(user_id=user.id)
    stats = UserStats(user_id=user.id)
    db_session.add_all([profile, stats])

    # Create DRAFT trip (not published)
    trip = Trip(
        trip_id="trip1",
        user_id=user.id,
        title="Draft Trip",
        description="Work in progress" * 10,
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.DRAFT,  # DRAFT status
    )
    db_session.add(trip)
    await db_session.commit()

    # Create test image
    img = Image.new("RGB", (800, 600), color="blue")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Upload photo to draft trip
    trip_service = TripService(db_session)
    await trip_service.upload_photo(
        trip_id=trip.trip_id,
        user_id=user.id,
        photo_file=img_bytes,
        filename="draft.jpg",
        content_type="image/jpeg",
    )

    # Verify NO activity was created
    result = await db_session.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user.id)
    )
    activities = result.scalars().all()

    assert len(activities) == 0  # No activity for draft trip photos


@pytest.mark.asyncio
async def test_award_achievement_creates_activity(db_session: AsyncSession):
    """
    T035: Test awarding achievement creates ACHIEVEMENT_UNLOCKED activity.

    Verifies:
    - Activity is created when achievement is awarded
    - Activity has correct type (ACHIEVEMENT_UNLOCKED)
    - Metadata includes achievement_name and badge_icon
    - Only created once (idempotent)
    """
    # Create user
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    db_session.add(user)
    await db_session.flush()

    # Create user stats
    stats = UserStats(user_id=user.id, achievements_count=0)
    db_session.add(stats)

    # Create achievement
    achievement = Achievement(
        code="FIRST_TRIP",
        name="First Trip",
        description="Complete your first trip",
        badge_icon="🚴",
        requirement_type="trip_count",
        requirement_value=1,
    )
    db_session.add(achievement)
    await db_session.commit()
    await db_session.refresh(achievement)

    # Award achievement
    stats_service = StatsService(db_session)
    await stats_service.award_achievement(user_id=user.id, achievement_id=achievement.id)

    # Verify activity was created
    result = await db_session.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user.id)
    )
    activities = result.scalars().all()

    assert len(activities) == 1
    activity = activities[0]

    assert activity.activity_type == ActivityType.ACHIEVEMENT_UNLOCKED
    assert activity.user_id == user.id

    # Verify metadata
    import json

    metadata = json.loads(activity.activity_metadata)
    assert metadata["achievement_name"] == "First Trip"
    assert metadata["achievement_badge"] == "🚴"

    # Test idempotency: award again (should not create duplicate activity)
    await stats_service.award_achievement(user_id=user.id, achievement_id=achievement.id)

    result = await db_session.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user.id)
    )
    activities_after = result.scalars().all()

    # Still only 1 activity (not duplicated)
    assert len(activities_after) == 1


@pytest.mark.asyncio
async def test_multiple_activities_ordered_chronologically(db_session: AsyncSession):
    """
    T033-T035: Test multiple activities are created in correct chronological order.

    Verifies:
    - Multiple different activity types can coexist
    - Activities are ordered DESC by created_at
    """
    # Create user
    user = User(
        id="user1",
        username="john",
        email="john@example.com",
        hashed_password="hash",
    )
    db_session.add(user)
    await db_session.flush()

    # Create user profile and stats
    profile = UserProfile(user_id=user.id)
    stats = UserStats(user_id=user.id, achievements_count=0)
    db_session.add_all([profile, stats])

    # Create achievement
    achievement = Achievement(
        code="EXPLORER",
        name="Explorer",
        description="Explore new places",
        badge_icon="🗺️",
        requirement_type="trip_count",
        requirement_value=1,
    )
    db_session.add(achievement)

    # Create published trip
    trip = Trip(
        trip_id="trip1",
        user_id=user.id,
        title="Multi-Activity Test",
        description="Testing multiple activity types" * 5,
        start_date=datetime(2024, 6, 1).date(),
        status=TripStatus.DRAFT,
    )
    db_session.add(trip)
    await db_session.commit()

    # 1. Publish trip (creates TRIP_PUBLISHED activity)
    trip_service = TripService(db_session)
    await trip_service.publish_trip(trip_id=trip.trip_id, user_id=user.id)

    # 2. Upload photo (creates PHOTO_UPLOADED activity)
    img = Image.new("RGB", (800, 600), color="green")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    await trip_service.upload_photo(
        trip_id=trip.trip_id,
        user_id=user.id,
        photo_file=img_bytes,
        filename="multi.jpg",
        content_type="image/jpeg",
    )

    # 3. Award achievement (creates ACHIEVEMENT_UNLOCKED activity)
    stats_service = StatsService(db_session)
    await stats_service.award_achievement(user_id=user.id, achievement_id=achievement.id)

    # Verify all 3 activities were created
    result = await db_session.execute(
        select(ActivityFeedItem)
        .where(ActivityFeedItem.user_id == user.id)
        .order_by(ActivityFeedItem.created_at.desc())
    )
    activities = result.scalars().all()

    assert len(activities) == 3

    # Verify types (ordered DESC by created_at - most recent first)
    activity_types = [act.activity_type for act in activities]
    assert ActivityType.ACHIEVEMENT_UNLOCKED in activity_types
    assert ActivityType.PHOTO_UPLOADED in activity_types
    assert ActivityType.TRIP_PUBLISHED in activity_types

    # Verify chronological order (most recent first)
    for i in range(len(activities) - 1):
        assert activities[i].created_at >= activities[i + 1].created_at
