"""
ActivityLikeService for managing likes on activity feed items (Feature 018 - US2).

Handles like/unlike operations with atomic transactions and notifications.
"""

import logging
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.activity_feed_item import ActivityFeedItem
from src.models.activity_like import ActivityLike
from src.models.user import User
from src.schemas.activity_like import (
    ActivityLikeResponse,
    ActivityLikesListResponse,
    ActivityLikeWithUser,
)

logger = logging.getLogger(__name__)


class ActivityLikeService:
    """Service for managing likes on activity feed items."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def like_activity(self, user_id: str, activity_id: str) -> ActivityLikeResponse:
        """
        T045: Like an activity feed item.

        Atomic operation with notification creation (if not self-like).
        Idempotent: Returns success if already liked.

        Args:
            user_id: User who is liking
            activity_id: Activity being liked

        Returns:
            ActivityLikeResponse with like details

        Raises:
            ValueError: If activity not found
        """
        # Check if activity exists
        result = await self.db.execute(
            select(ActivityFeedItem).where(ActivityFeedItem.activity_id == activity_id)
        )
        activity = result.scalar_one_or_none()

        if not activity:
            raise ValueError("Actividad no encontrada")

        # Check if already liked (idempotent)
        result = await self.db.execute(
            select(ActivityLike).where(
                ActivityLike.user_id == user_id,
                ActivityLike.activity_id == activity_id,
            )
        )
        existing_like = result.scalar_one_or_none()

        if existing_like:
            # Already liked - return existing like (idempotent)
            logger.info(f"User {user_id} already liked activity {activity_id} - idempotent")
            return ActivityLikeResponse.model_validate(existing_like)

        # Create new like
        new_like = ActivityLike(
            like_id=str(uuid4()),
            user_id=user_id,
            activity_id=activity_id,
        )
        self.db.add(new_like)

        try:
            await self.db.flush()

            # TODO (Feature 018 - US2): Create notification for activity likes
            # Currently disabled because Notification model only supports trip-based notifications
            # Need to extend Notification schema to support activity_id (separate from trip_id)
            # See task T051
            # if user_id != activity.user_id:
            #     notification = Notification(...)
            #     self.db.add(notification)

            await self.db.commit()
            await self.db.refresh(new_like)

            logger.info(f"User {user_id} liked activity {activity_id}")
            return ActivityLikeResponse.model_validate(new_like)

        except IntegrityError as e:
            await self.db.rollback()
            # Race condition: Another transaction created like between check and insert
            # Retry once to get the existing like
            logger.warning(
                f"Integrity error when liking activity {activity_id} by user {user_id}: {e}"
            )
            result = await self.db.execute(
                select(ActivityLike).where(
                    ActivityLike.user_id == user_id,
                    ActivityLike.activity_id == activity_id,
                )
            )
            existing_like = result.scalar_one_or_none()
            if existing_like:
                return ActivityLikeResponse.model_validate(existing_like)
            raise  # Re-raise if it's a different integrity error

    async def unlike_activity(self, user_id: str, activity_id: str) -> bool:
        """
        T046: Remove a like from an activity feed item.

        Idempotent: Returns True even if like doesn't exist.

        Args:
            user_id: User who is unliking
            activity_id: Activity being unliked

        Returns:
            True if like was removed or didn't exist
        """
        # Find and delete like
        result = await self.db.execute(
            select(ActivityLike).where(
                ActivityLike.user_id == user_id,
                ActivityLike.activity_id == activity_id,
            )
        )
        like = result.scalar_one_or_none()

        if not like:
            # Not liked - return success (idempotent)
            logger.info(
                f"User {user_id} tried to unlike activity {activity_id} but wasn't liked - idempotent"
            )
            return True

        await self.db.delete(like)
        await self.db.commit()

        logger.info(f"User {user_id} unliked activity {activity_id}")
        return True

    async def get_activity_likes(
        self, activity_id: str, page: int = 1, limit: int = 20
    ) -> ActivityLikesListResponse:
        """
        Get paginated list of users who liked an activity.

        Args:
            activity_id: Activity ID
            page: Page number (1-indexed)
            limit: Number of items per page (max 50)

        Returns:
            ActivityLikesListResponse with likes and pagination info

        Raises:
            ValueError: If activity not found or invalid page/limit
        """
        if page < 1:
            raise ValueError("Page must be >= 1")
        if limit < 1 or limit > 50:
            raise ValueError("Limit must be between 1 and 50")

        # Check if activity exists
        result = await self.db.execute(
            select(ActivityFeedItem).where(ActivityFeedItem.activity_id == activity_id)
        )
        activity = result.scalar_one_or_none()

        if not activity:
            raise ValueError("Actividad no encontrada")

        # Get total count
        count_stmt = select(func.count(ActivityLike.like_id)).where(
            ActivityLike.activity_id == activity_id
        )
        total_count_result = await self.db.execute(count_stmt)
        total_count = total_count_result.scalar() or 0

        # Get paginated likes with user information
        offset = (page - 1) * limit
        likes_stmt = (
            select(ActivityLike)
            .where(ActivityLike.activity_id == activity_id)
            .options(joinedload(ActivityLike.user).joinedload(User.profile))
            .order_by(ActivityLike.created_at.desc())
            .offset(offset)
            .limit(limit + 1)  # Get one extra to check if there are more pages
        )

        result = await self.db.execute(likes_stmt)
        likes = result.scalars().unique().all()

        # Check if there are more pages
        has_next = len(likes) > limit
        if has_next:
            likes = likes[:limit]  # Remove the extra item

        # Build response with user information
        likes_with_users = [
            ActivityLikeWithUser(
                like_id=like.like_id,
                user_id=like.user_id,
                username=like.user.username,
                user_photo_url=like.user.profile.profile_photo_url if like.user.profile else None,
                created_at=like.created_at,
            )
            for like in likes
        ]

        return ActivityLikesListResponse(
            likes=likes_with_users,
            total_count=total_count,
            page=page,
            limit=limit,
            has_next=has_next,
        )
