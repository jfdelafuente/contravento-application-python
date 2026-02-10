"""
NotificationService for Activity Stream Feed (Feature 018).

Handles notification creation, retrieval, and read status management.
Task: T009
"""

from uuid import uuid4
from datetime import UTC, datetime
from typing import List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification, NotificationType
from src.models.user import User


class NotificationService:
    """
    Service for managing user notifications.

    Methods:
        - create_notification(): Create new notification for user
        - get_user_notifications(): Retrieve user's notifications with pagination
        - get_unread_count(): Count unread notifications for user
        - mark_as_read(): Mark specific notification as read
        - mark_all_read(): Mark all notifications as read for user
    """

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: str,
        notification_type: NotificationType,
        actor_id: str,
        trip_id: str,
        content: str | None = None,
    ) -> Notification:
        """
        Create a new notification for a user.

        Args:
            db: Database session
            user_id: ID of user receiving notification
            notification_type: Type of notification (LIKE, COMMENT, SHARE)
            actor_id: ID of user who triggered the notification
            trip_id: ID of related trip
            content: Optional content (e.g., comment excerpt)

        Returns:
            Created Notification object

        Raises:
            ValueError: If user_id == actor_id (users don't notify themselves)
        """
        # Don't create notification if user is notifying themselves
        if user_id == actor_id:
            raise ValueError("Cannot create self-notification")

        notification = Notification(
            id=str(uuid4()),
            user_id=user_id,
            type=notification_type,
            actor_id=actor_id,
            trip_id=trip_id,
            content=content,
            is_read=False,
            created_at=datetime.now(UTC),
        )

        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        return notification

    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Notification]:
        """
        Retrieve notifications for a user with pagination.

        Args:
            db: Database session
            user_id: ID of user
            limit: Maximum number of notifications to return (default: 20)
            offset: Number of notifications to skip (default: 0)

        Returns:
            List of Notification objects, ordered by created_at DESC
        """
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(stmt)
        notifications = result.scalars().all()

        return list(notifications)

    @staticmethod
    async def get_unread_count(
        db: AsyncSession,
        user_id: str,
    ) -> int:
        """
        Get count of unread notifications for a user.

        Args:
            db: Database session
            user_id: ID of user

        Returns:
            Count of unread notifications
        """
        stmt = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )

        result = await db.execute(stmt)
        count = result.scalar()

        return count or 0

    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: str,
        user_id: str,
    ) -> Notification | None:
        """
        Mark a specific notification as read.

        Args:
            db: Database session
            notification_id: ID of notification to mark as read
            user_id: ID of user (for authorization check)

        Returns:
            Updated Notification object, or None if not found

        Raises:
            PermissionError: If notification doesn't belong to user
        """
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await db.execute(stmt)
        notification = result.scalar_one_or_none()

        if not notification:
            return None

        # Authorization check
        if notification.user_id != user_id:
            raise PermissionError("Notification does not belong to user")

        notification.is_read = True
        await db.commit()
        await db.refresh(notification)

        return notification

    @staticmethod
    async def mark_all_read(
        db: AsyncSession,
        user_id: str,
    ) -> int:
        """
        Mark all notifications as read for a user.

        Args:
            db: Database session
            user_id: ID of user

        Returns:
            Number of notifications marked as read
        """
        stmt = (
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False,  # noqa: E712
            )
        )

        result = await db.execute(stmt)
        unread_notifications = result.scalars().all()

        count = 0
        for notification in unread_notifications:
            notification.is_read = True
            count += 1

        if count > 0:
            await db.commit()

        return count
