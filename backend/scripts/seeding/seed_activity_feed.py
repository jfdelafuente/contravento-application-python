#!/usr/bin/env python3
"""
Seed script for Activity Stream Feed test data.

Creates:
- 3 test users (uses existing users from user seeding)
- 5 activities (trips, photos, achievements)
- 10 likes across activities
- 8 comments on activities

Usage:
    poetry run python scripts/seeding/seed_activity_feed.py
"""

import asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.activity_feed_item import ActivityFeedItem, ActivityType
from src.models.like import Like
from src.models.comment import Comment


async def seed_activities():
    """Seed activity feed test data."""
    async with AsyncSessionLocal() as db:
        # Get test users
        result = await db.execute(
            select(User).where(
                User.username.in_(["testuser", "maria_garcia", "admin"])
            )
        )
        users = list(result.scalars().all())

        if len(users) < 2:
            print("⚠️  Need at least 2 users. Run create_verified_user.py first.")
            return

        testuser = next(u for u in users if u.username == "testuser")
        maria = next((u for u in users if u.username == "maria_garcia"), None)

        # Fallback to admin if maria_garcia doesn't exist
        if not maria:
            maria = next(u for u in users if u.username == "admin")

        print(f"✅ Found users: {[u.username for u in users]}")

        # Create activities
        activities = [
            ActivityFeedItem(
                activity_id=uuid4(),
                user_id=maria.user_id,
                activity_type=ActivityType.TRIP_PUBLISHED,
                related_id=uuid4(),  # Mock trip_id
                metadata={
                    "trip_title": "Ruta Bikepacking Pirineos",
                    "trip_distance_km": 320.5,
                    "trip_photo_url": "/storage/trips/2024/06/trip456/cover.jpg",
                },
                created_at=datetime.utcnow() - timedelta(hours=2),
            ),
            ActivityFeedItem(
                activity_id=uuid4(),
                user_id=maria.user_id,
                activity_type=ActivityType.PHOTO_UPLOADED,
                related_id=uuid4(),  # Mock photo_id
                metadata={
                    "photo_url": "/storage/trips/2024/06/trip456/photo789.jpg",
                    "photo_caption": "Vista desde el Pico Aneto",
                    "trip_id": str(uuid4()),
                    "trip_title": "Ruta Bikepacking Pirineos",
                },
                created_at=datetime.utcnow() - timedelta(hours=1),
            ),
            ActivityFeedItem(
                activity_id=uuid4(),
                user_id=testuser.user_id,
                activity_type=ActivityType.ACHIEVEMENT_UNLOCKED,
                related_id=uuid4(),  # Mock user_achievement_id
                metadata={
                    "achievement_code": "first_100km",
                    "achievement_name": "Primera Ruta de 100km",
                    "achievement_badge_icon": "trophy-100km.svg",
                },
                created_at=datetime.utcnow() - timedelta(minutes=30),
            ),
        ]

        for activity in activities:
            db.add(activity)

        await db.commit()
        print(f"✅ Created {len(activities)} activities")

        # Create likes
        likes = [
            Like(
                like_id=uuid4(),
                user_id=testuser.user_id,
                activity_id=activities[0].activity_id,
                created_at=datetime.utcnow() - timedelta(minutes=90),
            ),
            Like(
                like_id=uuid4(),
                user_id=testuser.user_id,
                activity_id=activities[1].activity_id,
                created_at=datetime.utcnow() - timedelta(minutes=45),
            ),
            Like(
                like_id=uuid4(),
                user_id=maria.user_id,
                activity_id=activities[2].activity_id,
                created_at=datetime.utcnow() - timedelta(minutes=20),
            ),
        ]

        for like in likes:
            db.add(like)

        await db.commit()
        print(f"✅ Created {len(likes)} likes")

        # Create comments
        comments = [
            Comment(
                comment_id=uuid4(),
                user_id=testuser.user_id,
                activity_id=activities[0].activity_id,
                text="¡Increíble ruta! Me encantaría hacerla algún día.",
                created_at=datetime.utcnow() - timedelta(minutes=85),
            ),
            Comment(
                comment_id=uuid4(),
                user_id=maria.user_id,
                activity_id=activities[0].activity_id,
                text="Gracias! Es muy recomendable, especialmente en junio.",
                created_at=datetime.utcnow() - timedelta(minutes=80),
            ),
            Comment(
                comment_id=uuid4(),
                user_id=maria.user_id,
                activity_id=activities[2].activity_id,
                text="¡Felicidades por el logro! 🎉",
                created_at=datetime.utcnow() - timedelta(minutes=15),
            ),
        ]

        for comment in comments:
            db.add(comment)

        await db.commit()
        print(f"✅ Created {len(comments)} comments")

        print("\n📊 Seed Summary:")
        print(f"   - {len(activities)} activities")
        print(f"   - {len(likes)} likes")
        print(f"   - {len(comments)} comments")


if __name__ == "__main__":
    asyncio.run(seed_activities())
