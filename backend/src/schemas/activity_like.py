"""
Pydantic schemas for ActivityLike (Feature 018 - US2).

Schemas for like/unlike operations on activity feed items.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class ActivityLikeResponse(BaseModel):
    """
    Response schema for a single activity like.

    Used when creating or retrieving a like.
    """

    like_id: str = Field(..., description="Unique like identifier (UUID)")
    user_id: str = Field(..., description="User who liked (UUID)")
    activity_id: str = Field(..., description="Activity being liked (UUID)")
    created_at: datetime = Field(..., description="Timestamp when like was created")

    class Config:
        from_attributes = True


class ActivityLikeWithUser(BaseModel):
    """
    Like response with user information.

    Used when listing users who liked an activity.
    """

    like_id: str = Field(..., description="Unique like identifier (UUID)")
    user_id: str = Field(..., description="User who liked (UUID)")
    username: str = Field(..., description="Username of user who liked")
    user_photo_url: str | None = Field(None, description="Profile photo URL of user")
    created_at: datetime = Field(..., description="Timestamp when like was created")

    class Config:
        from_attributes = True


class ActivityLikesListResponse(BaseModel):
    """
    Paginated list of users who liked an activity.

    Used for GET /activities/{activity_id}/likes endpoint.
    """

    likes: list[ActivityLikeWithUser] = Field(
        ..., description="List of likes with user information"
    )
    total_count: int = Field(..., description="Total number of likes for this activity")
    page: int = Field(..., description="Current page number (1-indexed)")
    limit: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")

    class Config:
        from_attributes = True
