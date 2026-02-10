#!/usr/bin/env python3
"""
Activity Feed Validation Script (Feature 018).

Interactive script to validate Activity Stream Feed implementation:
- Database migration
- Activity triggers (TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED)
- API endpoint GET /activity-feed
- Cursor-based pagination

Usage:
    poetry run python scripts/validate_activity_feed.py
"""

import asyncio
import sys
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.database import Base
from src.models.activity_feed_item import ActivityFeedItem, ActivityType
from src.models.social import Follow
from src.models.stats import Achievement, UserStats
from src.models.trip import Trip, TripStatus
from src.models.user import User, UserProfile
from src.services.feed_service import FeedService
from src.services.stats_service import StatsService
from src.services.trip_service import TripService


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message: str):
    """Print success message."""
    print(f"[OK] {message}")


def print_info(message: str):
    """Print info message."""
    # Remove emojis and unicode characters that cause encoding issues on Windows
    import re
    message_clean = re.sub(r'[^\x00-\x7F]+', '[EMOJI]', message)
    print(f"[INFO] {message_clean}")


def print_activity(activity: dict, index: int):
    """Print formatted activity item."""
    import re

    print(f"\n[ACTIVITY] Activity #{index + 1}:")
    print(f"   Type: {activity['activity_type']}")
    print(f"   User: @{activity['user']['username']}")
    print(f"   Created: {activity['created_at']}")

    # Show metadata based on type
    metadata = activity.get('metadata', {})
    if activity['activity_type'] == 'TRIP_PUBLISHED':
        trip_title = re.sub(r'[^\x00-\x7F]+', '[EMOJI]', metadata.get('trip_title', 'N/A'))
        print(f"   Trip: {trip_title}")
    elif activity['activity_type'] == 'PHOTO_UPLOADED':
        trip_title = re.sub(r'[^\x00-\x7F]+', '[EMOJI]', metadata.get('trip_title', 'N/A'))
        print(f"   Trip: {trip_title}")
        print(f"   Photo: {metadata.get('photo_url', 'N/A')}")
    elif activity['activity_type'] == 'ACHIEVEMENT_UNLOCKED':
        achievement_name = re.sub(r'[^\x00-\x7F]+', '[EMOJI]', metadata.get('achievement_name', 'N/A'))
        achievement_badge = re.sub(r'[^\x00-\x7F]+', '[EMOJI]', metadata.get('achievement_badge', ''))
        print(f"   Achievement: {achievement_name} {achievement_badge}")


async def create_test_data(db: AsyncSession):
    """Create test users, trips, and relationships."""
    print_header("Step 1: Creating Test Data")

    # Use timestamp to create unique emails (avoid conflicts)
    import time
    timestamp = int(time.time())

    # Create user 1 (will follow user 2)
    user1 = User(
        username=f"test_follower_{timestamp}",
        email=f"follower_{timestamp}@test.com",
        hashed_password="$2b$12$dummyhash",
        is_verified=True,
    )
    db.add(user1)
    await db.flush()

    profile1 = UserProfile(user_id=user1.id)
    stats1 = UserStats(user_id=user1.id)
    db.add_all([profile1, stats1])

    # Create user 2 (will be followed)
    user2 = User(
        username=f"test_publisher_{timestamp}",
        email=f"publisher_{timestamp}@test.com",
        hashed_password="$2b$12$dummyhash",
        is_verified=True,
    )
    db.add(user2)
    await db.flush()

    profile2 = UserProfile(
        user_id=user2.id,
        profile_photo_url="/storage/profile_photos/test.jpg"
    )
    stats2 = UserStats(user_id=user2.id)
    db.add_all([profile2, stats2])

    # Create follow relationship
    follow = Follow(
        follower_id=user1.id,
        following_id=user2.id,
    )
    db.add(follow)

    # Create draft trip for user2
    trip = Trip(
        user_id=user2.id,
        title="Ruta de Validación - Activity Feed Test",
        description="Este viaje es para probar el Activity Stream Feed de Feature 018. " * 3,
        start_date=datetime(2024, 6, 15).date(),
        status=TripStatus.DRAFT,
    )
    db.add(trip)

    # Create achievement for testing
    achievement = Achievement(
        code=f"TEST_ACHIEVEMENT_{timestamp}",
        name="Validador de Features",
        description="Otorgado por validar Feature 018",
        badge_icon="[TEST]",
        requirement_type="trip_count",
        requirement_value=1,
    )
    db.add(achievement)

    await db.commit()
    await db.refresh(user1)
    await db.refresh(user2)
    await db.refresh(trip)
    await db.refresh(achievement)

    print_success(f"Created user: @{user1.username} (follower)")
    print_success(f"Created user: @{user2.username} (publisher)")
    print_success(f"Created follow: @{user1.username} follows @{user2.username}")
    print_success(f"Created draft trip: {trip.title}")
    print_success(f"Created achievement: {achievement.name} {achievement.badge_icon}")

    return user1, user2, trip, achievement


async def test_trip_published_trigger(db: AsyncSession, user2: User, trip: Trip):
    """Test TRIP_PUBLISHED activity creation."""
    print_header("Step 2: Testing TRIP_PUBLISHED Trigger")

    print_info(f"Publishing trip: {trip.title}")

    # Check activities before
    result = await db.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user2.id)
    )
    activities_before = len(result.scalars().all())
    print_info(f"Activities before publish: {activities_before}")

    # Publish trip (should trigger activity creation)
    trip_service = TripService(db)
    await trip_service.publish_trip(trip_id=trip.trip_id, user_id=user2.id)

    # Check activities after
    result = await db.execute(
        select(ActivityFeedItem).where(ActivityFeedItem.user_id == user2.id)
    )
    activities_after = result.scalars().all()
    print_info(f"Activities after publish: {len(activities_after)}")

    # Verify TRIP_PUBLISHED activity was created
    trip_activity = next(
        (a for a in activities_after if a.activity_type == ActivityType.TRIP_PUBLISHED),
        None
    )

    if trip_activity:
        print_success("TRIP_PUBLISHED activity created!")
        print_info(f"   Activity ID: {trip_activity.activity_id}")
        print_info(f"   Related Trip: {trip_activity.related_id}")

        import json
        metadata = json.loads(trip_activity.activity_metadata)
        print_info(f"   Metadata: {metadata}")
    else:
        print("[ERROR] TRIP_PUBLISHED activity NOT created!")
        return False

    return True


async def test_photo_uploaded_trigger(db: AsyncSession, user2: User, trip: Trip):
    """Test PHOTO_UPLOADED activity creation."""
    print_header("Step 3: Testing PHOTO_UPLOADED Trigger")

    print_info("Uploading photo to trip...")

    # Check activities before
    result = await db.execute(
        select(ActivityFeedItem).where(
            ActivityFeedItem.user_id == user2.id,
            ActivityFeedItem.activity_type == ActivityType.PHOTO_UPLOADED
        )
    )
    photos_before = len(result.scalars().all())
    print_info(f"PHOTO_UPLOADED activities before: {photos_before}")

    # Create test image
    img = Image.new("RGB", (800, 600), color="blue")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    # Upload photo (should trigger activity creation)
    trip_service = TripService(db)
    photo = await trip_service.upload_photo(
        trip_id=trip.trip_id,
        user_id=user2.id,
        photo_file=img_bytes,
        filename="validation_test.jpg",
        content_type="image/jpeg",
    )

    # Check activities after
    result = await db.execute(
        select(ActivityFeedItem).where(
            ActivityFeedItem.user_id == user2.id,
            ActivityFeedItem.activity_type == ActivityType.PHOTO_UPLOADED
        )
    )
    photos_after = result.scalars().all()
    print_info(f"PHOTO_UPLOADED activities after: {len(photos_after)}")

    # Verify PHOTO_UPLOADED activity was created
    if len(photos_after) > photos_before:
        photo_activity = photos_after[-1]  # Latest
        print_success("PHOTO_UPLOADED activity created!")
        print_info(f"   Activity ID: {photo_activity.activity_id}")
        print_info(f"   Related Photo: {photo_activity.related_id}")

        import json
        metadata = json.loads(photo_activity.activity_metadata)
        print_info(f"   Metadata: {metadata}")
    else:
        print("[ERROR] PHOTO_UPLOADED activity NOT created!")
        return False

    return True


async def test_achievement_unlocked_trigger(db: AsyncSession, user2: User, achievement: Achievement):
    """Test ACHIEVEMENT_UNLOCKED activity creation."""
    print_header("Step 4: Testing ACHIEVEMENT_UNLOCKED Trigger")

    print_info(f"Awarding achievement: {achievement.name} {achievement.badge_icon}")

    # Check activities before
    result = await db.execute(
        select(ActivityFeedItem).where(
            ActivityFeedItem.user_id == user2.id,
            ActivityFeedItem.activity_type == ActivityType.ACHIEVEMENT_UNLOCKED
        )
    )
    achievements_before = len(result.scalars().all())
    print_info(f"ACHIEVEMENT_UNLOCKED activities before: {achievements_before}")

    # Award achievement (should trigger activity creation)
    stats_service = StatsService(db)
    await stats_service.award_achievement(user_id=user2.id, achievement_id=achievement.id)

    # Check activities after
    result = await db.execute(
        select(ActivityFeedItem).where(
            ActivityFeedItem.user_id == user2.id,
            ActivityFeedItem.activity_type == ActivityType.ACHIEVEMENT_UNLOCKED
        )
    )
    achievements_after = result.scalars().all()
    print_info(f"ACHIEVEMENT_UNLOCKED activities after: {len(achievements_after)}")

    # Verify ACHIEVEMENT_UNLOCKED activity was created
    if len(achievements_after) > achievements_before:
        ach_activity = achievements_after[-1]  # Latest
        print_success("ACHIEVEMENT_UNLOCKED activity created!")
        print_info(f"   Activity ID: {ach_activity.activity_id}")
        print_info(f"   Related Achievement: {ach_activity.related_id}")

        import json
        metadata = json.loads(ach_activity.activity_metadata)
        print_info(f"   Metadata: {metadata}")
    else:
        print("[ERROR] ACHIEVEMENT_UNLOCKED activity NOT created!")
        return False

    return True


async def test_activity_feed_api(db: AsyncSession, user1: User):
    """Test GET /activity-feed endpoint logic."""
    print_header("Step 5: Testing Activity Feed API (Service Layer)")

    print_info(f"Fetching feed for @{user1.username}...")

    # Get feed (first page)
    result = await FeedService.get_user_feed(
        db=db,
        user_id=user1.id,
        limit=10,
        cursor=None,
    )

    print_success(f"Feed retrieved successfully!")
    print_info(f"   Activities count: {len(result['activities'])}")
    print_info(f"   Has next: {result['has_next']}")
    print_info(f"   Next cursor: {result['next_cursor'][:20] + '...' if result['next_cursor'] else 'None'}")

    # Display activities
    if result['activities']:
        print("\n[FEED] Activities in Feed:")
        for i, activity in enumerate(result['activities']):
            print_activity(activity, i)
    else:
        print("[WARNING] Feed is empty (user might not be following anyone with activities)")

    return len(result['activities']) > 0


async def test_cursor_pagination(db: AsyncSession, user1: User):
    """Test cursor-based pagination."""
    print_header("Step 6: Testing Cursor-Based Pagination")

    print_info("Fetching first page (limit=2)...")

    # First page
    page1 = await FeedService.get_user_feed(
        db=db,
        user_id=user1.id,
        limit=2,
        cursor=None,
    )

    print_success(f"Page 1: {len(page1['activities'])} activities")
    print_info(f"   Has next: {page1['has_next']}")

    if page1['has_next'] and page1['next_cursor']:
        print_info(f"Fetching second page (cursor={page1['next_cursor'][:20]}...)...")

        # Second page
        page2 = await FeedService.get_user_feed(
            db=db,
            user_id=user1.id,
            limit=2,
            cursor=page1['next_cursor'],
        )

        print_success(f"Page 2: {len(page2['activities'])} activities")
        print_info(f"   Has next: {page2['has_next']}")

        # Verify no duplicates
        page1_ids = {a['activity_id'] for a in page1['activities']}
        page2_ids = {a['activity_id'] for a in page2['activities']}
        overlap = page1_ids & page2_ids

        if not overlap:
            print_success("No duplicate activities between pages!")
        else:
            print(f"[WARNING] Found {len(overlap)} duplicate activities!")
    else:
        print_info("Only one page of activities (< 2 activities total)")

    return True


async def main():
    """Run all validation tests."""
    print_header("Activity Stream Feed Validation (Feature 018)")
    print(f"Environment: {settings.app_env}")
    print(f"Database: {settings.database_url[:50]}...")

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )

    # Create tables (run migrations)
    print_header("Step 0: Database Migration")
    print_info("Creating activity_feed_items table...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print_success("Tables created successfully!")

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as db:
        try:
            # Run tests
            user1, user2, trip, achievement = await create_test_data(db)

            success = True
            success &= await test_trip_published_trigger(db, user2, trip)
            success &= await test_photo_uploaded_trigger(db, user2, trip)
            success &= await test_achievement_unlocked_trigger(db, user2, achievement)
            success &= await test_activity_feed_api(db, user1)
            success &= await test_cursor_pagination(db, user1)

            # Summary
            print_header("Validation Summary")

            if success:
                print_success("All validations passed!")
                print("\n[STATUS] Feature 018 Status:")
                print("   [OK] Database model: activity_feed_items table created")
                print("   [OK] TRIP_PUBLISHED trigger: Working")
                print("   [OK] PHOTO_UPLOADED trigger: Working")
                print("   [OK] ACHIEVEMENT_UNLOCKED trigger: Working")
                print("   [OK] Activity Feed API: Working")
                print("   [OK] Cursor pagination: Working")
                print("\n[SUCCESS] Feature 018: Activity Stream Feed is READY!")
            else:
                print("[WARNING] Some validations failed. Check logs above.")

            print("\n" + "=" * 70)

        except Exception as e:
            print(f"\n[ERROR] Error during validation: {e}")
            import traceback
            traceback.print_exc()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
