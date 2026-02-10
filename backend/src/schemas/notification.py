"""
Pydantic schemas for Notification API (Feature 018).

Task: T010
"""

from datetime import datetime

from pydantic import BaseModel, Field

from src.models.notification import NotificationType


class PublicUserSummary(BaseModel):
    """
    Minimal user information for notification actors.
    """

    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    photo_url: str | None = Field(None, description="Profile photo URL")

    class Config:
        from_attributes = True


class TripSummary(BaseModel):
    """
    Minimal trip information for notifications.
    """

    trip_id: str = Field(..., description="Trip ID")
    title: str = Field(..., description="Trip title")

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """
    Single notification response.
    """

    notification_id: str = Field(..., alias="id", description="Notification ID")
    type: NotificationType = Field(..., description="Notification type (LIKE, COMMENT, SHARE)")
    actor: PublicUserSummary = Field(..., description="User who triggered the notification")
    trip: TripSummary = Field(..., description="Related trip")
    content: str | None = Field(None, description="Optional content (e.g., comment excerpt)")
    is_read: bool = Field(..., description="Whether notification has been read")
    created_at: datetime = Field(..., description="Notification creation timestamp")

    class Config:
        from_attributes = True
        populate_by_name = True


class NotificationsListResponse(BaseModel):
    """
    Paginated list of notifications.
    """

    notifications: list[NotificationResponse] = Field(..., description="List of notifications")
    total_count: int = Field(..., description="Total number of notifications")
    unread_count: int = Field(..., description="Number of unread notifications")
    has_more: bool = Field(..., description="Whether there are more notifications to fetch")

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    """
    Unread notification count response.
    """

    unread_count: int = Field(..., description="Number of unread notifications")

    class Config:
        from_attributes = True


class MarkReadResponse(BaseModel):
    """
    Response after marking notification(s) as read.
    """

    success: bool = Field(..., description="Whether operation succeeded")
    marked_count: int = Field(..., description="Number of notifications marked as read")

    class Config:
        from_attributes = True
