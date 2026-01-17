"""
Pydantic schemas for Like API endpoints (Feature 004 - US2: Likes/Me Gusta).

Schemas:
- LikeResponse: Response for like_trip()
- UserSummaryForLike: Minimal user details in likes list
- LikeItem: Single like in list
- LikesListResponse: Paginated list of likes
"""

from pydantic import BaseModel, Field


class LikeResponse(BaseModel):
    """Response schema for POST /trips/{id}/like (T053)."""

    like_id: str = Field(..., description="Unique like identifier (UUID)")
    user_id: str = Field(..., description="ID of user who liked")
    trip_id: str = Field(..., description="ID of trip that was liked")
    created_at: str = Field(..., description="Like creation timestamp (ISO 8601)")

    model_config = {"from_attributes": True}


class UserSummaryForLike(BaseModel):
    """Minimal user details for likes list."""

    username: str = Field(..., description="Username")
    profile_photo_url: str | None = Field(
        None, description="Profile photo URL (nullable)"
    )


class LikeItem(BaseModel):
    """Single like in likes list (T054)."""

    user: UserSummaryForLike = Field(..., description="User who liked the trip")
    created_at: str = Field(..., description="Like timestamp (ISO 8601)")


class LikesListResponse(BaseModel):
    """Response schema for GET /trips/{id}/likes (T054)."""

    likes: list[LikeItem] = Field(..., description="List of likes")
    total_count: int = Field(..., ge=0, description="Total number of likes")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=50, description="Items per page")
    has_more: bool = Field(..., description="True if more pages exist")

    model_config = {"from_attributes": True}


class UnlikeResponse(BaseModel):
    """Response schema for DELETE /trips/{id}/like."""

    success: bool = Field(..., description="Operation success flag")
    message: str = Field(..., description="Success message")
