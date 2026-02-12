"""
Pydantic schemas for social features.

Schemas for follow/unfollow operations, followers/following lists,
and social relationships.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserSummary(BaseModel):
    """
    T201: User summary for follower/following lists.

    Lightweight user representation with profile photo and stats.
    Used in followers/following paginated lists.
    """

    username: str = Field(..., description="Username", min_length=3, max_length=30)
    full_name: str | None = Field(None, description="Full name")
    profile_photo_url: str | None = Field(None, description="Profile photo URL")
    bio: str | None = Field(None, description="User bio", max_length=500)
    followers_count: int = Field(default=0, description="Number of followers", ge=0)
    following_count: int = Field(default=0, description="Number of users being followed", ge=0)

    class Config:
        from_attributes = True


class FollowResponse(BaseModel):
    """
    T202: Response for follow/unfollow operations.

    Returned after successful follow or unfollow action.
    Includes updated counters for both users.
    """

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message in Spanish")
    follower_username: str = Field(..., description="Username of the follower")
    following_username: str = Field(..., description="Username being followed/unfollowed")
    is_following: bool = Field(..., description="Current follow status after operation")
    follower_following_count: int = Field(
        ..., description="Updated following count for follower", ge=0
    )
    following_followers_count: int = Field(
        ..., description="Updated followers count for followed user", ge=0
    )

    class Config:
        from_attributes = True


class FollowersListResponse(BaseModel):
    """
    T203: Paginated list of followers.

    Returns users who follow the target user.
    Supports pagination with max 50 results per page.
    """

    followers: list[UserSummary] = Field(..., description="List of followers")
    total_count: int = Field(..., description="Total number of followers", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    limit: int = Field(..., description="Results per page", ge=1, le=50)
    has_more: bool = Field(..., description="Whether more results are available")

    class Config:
        from_attributes = True


class FollowingListResponse(BaseModel):
    """
    T204: Paginated list of users being followed.

    Returns users that the target user follows.
    Supports pagination with max 50 results per page.
    """

    following: list[UserSummary] = Field(..., description="List of users being followed")
    total_count: int = Field(..., description="Total number of users being followed", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    limit: int = Field(..., description="Results per page", ge=1, le=50)
    has_more: bool = Field(..., description="Whether more results are available")

    class Config:
        from_attributes = True


class FollowStatusResponse(BaseModel):
    """
    T205: Follow status between two users.

    Returns whether the current user follows the target user.
    Includes the timestamp of when the follow relationship was created.
    """

    is_following: bool = Field(..., description="Whether current user follows target user")
    followed_at: datetime | None = Field(
        None, description="When the follow relationship was created (UTC)"
    )

    class Config:
        from_attributes = True
