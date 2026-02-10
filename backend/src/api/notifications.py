"""
Notification API endpoints for Activity Stream Feed (Feature 018).

Endpoints:
    - GET /notifications: Get user's notifications with pagination
    - GET /notifications/unread-count: Get unread notification count
    - POST /notifications/{id}/mark-read: Mark notification as read
    - POST /notifications/mark-all-read: Mark all notifications as read

Task: T011
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.services.notification_service import NotificationService
from src.schemas.notification import (
    NotificationsListResponse,
    NotificationResponse,
    UnreadCountResponse,
    MarkReadResponse,
    PublicUserSummary,
    TripSummary,
)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get("", response_model=NotificationsListResponse)
async def get_notifications(
    limit: int = Query(20, ge=1, le=50, description="Number of notifications per page"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user's notifications with pagination (T011).

    Returns chronological list of notifications (most recent first).

    Args:
        limit: Number of notifications to return (1-50, default: 20)
        offset: Number of notifications to skip (default: 0)
        current_user: Authenticated user
        db: Database session

    Returns:
        NotificationsListResponse with notifications, counts, and pagination info
    """
    # Get notifications
    notifications = await NotificationService.get_user_notifications(
        db=db,
        user_id=current_user.user_id,
        limit=limit,
        offset=offset,
    )

    # Get unread count
    unread_count = await NotificationService.get_unread_count(
        db=db,
        user_id=current_user.user_id,
    )

    # Map notifications to response schema
    notification_responses = []
    for notification in notifications:
        # Eager load relationships if needed
        await db.refresh(notification, ["actor", "trip"])

        notification_responses.append(
            NotificationResponse(
                id=notification.id,
                type=notification.type,
                actor=PublicUserSummary(
                    user_id=notification.actor.user_id,
                    username=notification.actor.username,
                    photo_url=notification.actor.photo_url,
                ),
                trip=TripSummary(
                    trip_id=notification.trip.trip_id,
                    title=notification.trip.title,
                ),
                content=notification.content,
                is_read=notification.is_read,
                created_at=notification.created_at,
            )
        )

    # Check if there are more notifications
    has_more = len(notifications) == limit

    return NotificationsListResponse(
        notifications=notification_responses,
        total_count=len(notifications) + offset,
        unread_count=unread_count,
        has_more=has_more,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get count of unread notifications (T011).

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        UnreadCountResponse with unread notification count
    """
    unread_count = await NotificationService.get_unread_count(
        db=db,
        user_id=current_user.user_id,
    )

    return UnreadCountResponse(unread_count=unread_count)


@router.post("/{notification_id}/mark-read", response_model=MarkReadResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark a specific notification as read (T011).

    Args:
        notification_id: ID of notification to mark as read
        current_user: Authenticated user
        db: Database session

    Returns:
        MarkReadResponse with success status

    Raises:
        HTTPException 404: Notification not found
        HTTPException 403: Notification doesn't belong to user
    """
    try:
        notification = await NotificationService.mark_as_read(
            db=db,
            notification_id=notification_id,
            user_id=current_user.user_id,
        )

        if not notification:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "NOTIFICATION_NOT_FOUND",
                    "message": "Notificación no encontrada",
                },
            )

        return MarkReadResponse(success=True, marked_count=1)

    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "No tienes permiso para modificar esta notificación",
            },
        )


@router.post("/mark-all-read", response_model=MarkReadResponse)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark all notifications as read for current user (T011).

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        MarkReadResponse with count of notifications marked as read
    """
    marked_count = await NotificationService.mark_all_read(
        db=db,
        user_id=current_user.user_id,
    )

    return MarkReadResponse(success=True, marked_count=marked_count)
