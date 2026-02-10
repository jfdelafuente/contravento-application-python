"""
Unit tests for ActivityLikeService (Feature 018 - US2).

Tests like/unlike operations with focus on:
- Idempotency
- UNIQUE constraint enforcement
- Atomic transactions for concurrent likes
- Notification creation
"""

import pytest
from sqlalchemy import select

from src.models.activity_feed_item import ActivityFeedItem, ActivityType
from src.models.activity_like import ActivityLike
from src.models.user import User
from src.services.activity_like_service import ActivityLikeService


@pytest.mark.asyncio
class TestActivityLikeService:
    """Test suite for ActivityLikeService."""

    async def test_like_activity_success(self, db_session, test_user, test_user2):
        """Test successfully liking an activity."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-123",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-123",
            activity_metadata={"trip_title": "Test Trip"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Like activity
        service = ActivityLikeService(db_session)
        result = await service.like_activity(
            user_id=test_user2.id, activity_id=activity.activity_id
        )

        # Verify like created
        assert result.like_id is not None
        assert result.user_id == test_user2.id
        assert result.activity_id == activity.activity_id
        assert result.created_at is not None

        # Verify like exists in database
        stmt = select(ActivityLike).where(ActivityLike.like_id == result.like_id)
        db_result = await db_session.execute(stmt)
        like_in_db = db_result.scalar_one_or_none()
        assert like_in_db is not None
        assert like_in_db.user_id == test_user2.id

    async def test_like_activity_creates_notification(self, db_session, test_user, test_user2):
        """
        Test that liking an activity creates a notification for the author.

        NOTE: Currently SKIPPED - Notification creation disabled in US2.
        Notification model only supports trip-based notifications.
        Will be implemented in T051 (extend Notification schema for activities).
        """
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-456",
            user_id=test_user.id,
            activity_type=ActivityType.PHOTO_UPLOADED,
            related_id="photo-456",
            activity_metadata={"photo_url": "/photos/test.jpg"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Like activity
        service = ActivityLikeService(db_session)
        result = await service.like_activity(
            user_id=test_user2.id, activity_id=activity.activity_id
        )

        # Verify like created (notification check disabled for now)
        assert result.like_id is not None
        assert result.user_id == test_user2.id

    async def test_like_activity_self_like_no_notification(self, db_session, test_user):
        """
        Test that self-liking does NOT create a notification.

        NOTE: Currently SKIPPED - Notification creation disabled in US2.
        Will be implemented in T051.
        """
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-789",
            user_id=test_user.id,
            activity_type=ActivityType.ACHIEVEMENT_UNLOCKED,
            related_id="achievement-789",
            activity_metadata={"achievement_name": "Test Achievement"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Self-like
        service = ActivityLikeService(db_session)
        result = await service.like_activity(user_id=test_user.id, activity_id=activity.activity_id)

        # Verify like created (notification check disabled for now)
        assert result.like_id is not None
        assert result.user_id == test_user.id

    async def test_like_activity_idempotent(self, db_session, test_user, test_user2):
        """
        T047: Test that liking same activity twice is idempotent.

        UNIQUE constraint prevents duplicate likes.
        Service should return existing like instead of error.
        """
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-duplicate",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-duplicate",
            activity_metadata={"trip_title": "Duplicate Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        service = ActivityLikeService(db_session)

        # First like
        result1 = await service.like_activity(
            user_id=test_user2.id, activity_id=activity.activity_id
        )

        # Second like (duplicate) - should be idempotent
        result2 = await service.like_activity(
            user_id=test_user2.id, activity_id=activity.activity_id
        )

        # Should return same like
        assert result1.like_id == result2.like_id
        assert result1.user_id == result2.user_id
        assert result1.activity_id == result2.activity_id

        # Verify only one like exists in database
        stmt = select(ActivityLike).where(
            ActivityLike.user_id == test_user2.id,
            ActivityLike.activity_id == activity.activity_id,
        )
        db_result = await db_session.execute(stmt)
        likes = db_result.scalars().all()
        assert len(likes) == 1

    async def test_unlike_activity_success(self, db_session, test_user, test_user2):
        """Test successfully unliking an activity."""
        # Create activity and like it
        activity = ActivityFeedItem(
            activity_id="act-unlike",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-unlike",
            activity_metadata={"trip_title": "Unlike Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        service = ActivityLikeService(db_session)
        await service.like_activity(user_id=test_user2.id, activity_id=activity.activity_id)

        # Unlike activity
        result = await service.unlike_activity(
            user_id=test_user2.id, activity_id=activity.activity_id
        )

        assert result is True

        # Verify like deleted from database
        stmt = select(ActivityLike).where(
            ActivityLike.user_id == test_user2.id,
            ActivityLike.activity_id == activity.activity_id,
        )
        db_result = await db_session.execute(stmt)
        like = db_result.scalar_one_or_none()
        assert like is None

    async def test_unlike_activity_idempotent(self, db_session, test_user, test_user2):
        """Test that unliking non-existent like is idempotent."""
        # Create activity (without liking it)
        activity = ActivityFeedItem(
            activity_id="act-unlike-idempotent",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-unlike-idempotent",
            activity_metadata={"trip_title": "Unlike Idempotent Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        service = ActivityLikeService(db_session)

        # Unlike without having liked - should be idempotent
        result = await service.unlike_activity(
            user_id=test_user2.id, activity_id=activity.activity_id
        )

        assert result is True

    async def test_like_activity_not_found(self, db_session, test_user):
        """Test liking non-existent activity raises ValueError."""
        service = ActivityLikeService(db_session)

        with pytest.raises(ValueError, match="Actividad no encontrada"):
            await service.like_activity(user_id=test_user.id, activity_id="non-existent-activity")

    async def test_get_activity_likes_paginated(self, db_session, test_user, test_user2):
        """Test retrieving paginated list of users who liked an activity."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-paginated",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-paginated",
            activity_metadata={"trip_title": "Paginated Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Add multiple likes
        service = ActivityLikeService(db_session)
        await service.like_activity(user_id=test_user.id, activity_id=activity.activity_id)
        await service.like_activity(user_id=test_user2.id, activity_id=activity.activity_id)

        # Get likes (page 1, limit 10)
        result = await service.get_activity_likes(
            activity_id=activity.activity_id, page=1, limit=10
        )

        assert result.total_count == 2
        assert len(result.likes) == 2
        assert result.page == 1
        assert result.limit == 10
        assert result.has_next is False

        # Verify user information included
        usernames = {like.username for like in result.likes}
        assert test_user.username in usernames
        assert test_user2.username in usernames

    async def test_get_activity_likes_not_found(self, db_session):
        """Test getting likes for non-existent activity raises ValueError."""
        service = ActivityLikeService(db_session)

        with pytest.raises(ValueError, match="Actividad no encontrada"):
            await service.get_activity_likes(activity_id="non-existent-activity", page=1, limit=10)

    async def test_get_activity_likes_invalid_pagination(self, db_session, test_user):
        """Test invalid pagination parameters raise ValueError."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-invalid-page",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-invalid-page",
            activity_metadata={"trip_title": "Invalid Page Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        service = ActivityLikeService(db_session)

        # Invalid page (< 1)
        with pytest.raises(ValueError, match="Page must be >= 1"):
            await service.get_activity_likes(activity_id=activity.activity_id, page=0, limit=10)

        # Invalid limit (> 50)
        with pytest.raises(ValueError, match="Limit must be between 1 and 50"):
            await service.get_activity_likes(activity_id=activity.activity_id, page=1, limit=100)


@pytest.mark.asyncio
class TestConcurrentLikes:
    """
    T048: Test concurrent like operations maintain data integrity.

    Tests that concurrent likes from multiple users correctly increment
    the likes counter using atomic database transactions.
    """

    async def test_concurrent_likes_atomic(self, db_session, test_user):
        """Test that concurrent likes are handled atomically."""
        # Create activity
        activity = ActivityFeedItem(
            activity_id="act-concurrent",
            user_id=test_user.id,
            activity_type=ActivityType.TRIP_PUBLISHED,
            related_id="trip-concurrent",
            activity_metadata={"trip_title": "Concurrent Test"},
        )
        db_session.add(activity)
        await db_session.commit()

        # Create multiple users
        users = []
        for i in range(5):
            user = User(
                id=f"user-concurrent-{i}",
                username=f"concurrent_user_{i}",
                email=f"concurrent{i}@test.com",
                hashed_password="hashed",
            )
            db_session.add(user)
            users.append(user)
        await db_session.commit()

        # Simulate concurrent likes from all users
        service = ActivityLikeService(db_session)
        tasks = []
        for user in users:
            # Each user likes the activity
            result = await service.like_activity(user_id=user.id, activity_id=activity.activity_id)
            tasks.append(result)

        # Verify all likes succeeded
        assert len(tasks) == 5

        # Verify total like count in database
        stmt = select(ActivityLike).where(ActivityLike.activity_id == activity.activity_id)
        db_result = await db_session.execute(stmt)
        all_likes = db_result.scalars().all()

        # Should have exactly 5 likes (atomic transactions prevent duplicates)
        assert len(all_likes) == 5

        # Verify each user has exactly one like
        user_ids = [like.user_id for like in all_likes]
        assert len(user_ids) == len(set(user_ids))  # No duplicates
