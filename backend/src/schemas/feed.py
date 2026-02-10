"""
Pydantic schemas for Feed API (Feature 004 - T023, T024).

Defines request/response models for personalized feed endpoints.
"""

from datetime import date, datetime

from pydantic import BaseModel, Field

# ============================================================
# SHARED SCHEMAS (used by multiple features)
# ============================================================


class UserSummary(BaseModel):
    """
    User summary for feed items (author info).

    Minimal user data needed for displaying feed item authors.
    """

    user_id: str = Field(..., description="User UUID (Feature 004 - US1)")
    username: str = Field(..., description="Username")
    full_name: str | None = Field(None, description="Full display name (nullable)")
    profile_photo_url: str | None = Field(None, description="Profile photo URL (nullable)")
    is_following: bool | None = Field(
        None, description="Whether current user follows this user (Feature 004 - US1)"
    )

    class Config:
        from_attributes = True


class PhotoSummary(BaseModel):
    """
    Photo summary for feed items.

    Minimal photo data for feed item display (first photo or thumbnail).
    """

    photo_url: str = Field(..., description="Photo URL")
    caption: str | None = Field(None, description="Photo caption (nullable)")

    class Config:
        from_attributes = True


class LocationSummary(BaseModel):
    """
    Location summary for feed items.

    Minimal location data for feed item display.
    """

    name: str = Field(..., description="Location name")
    latitude: float | None = Field(None, description="Latitude (nullable)")
    longitude: float | None = Field(None, description="Longitude (nullable)")

    class Config:
        from_attributes = True


class TagSummary(BaseModel):
    """
    Tag summary for feed items.

    Tag data for displaying trip categories.
    """

    name: str = Field(..., description="Tag display name (original case)")
    normalized: str = Field(..., description="Tag normalized name (lowercase)")

    class Config:
        from_attributes = True


# ============================================================
# FEED SCHEMAS
# ============================================================


class FeedItem(BaseModel):
    """
    T023: Feed item schema (single trip in feed).

    Represents one trip in the personalized feed with all metadata
    needed for UI display including social interaction counters.

    Based on OpenAPI spec: specs/004-social-network/contracts/social-api.yaml
    """

    trip_id: str = Field(..., description="Trip UUID")
    title: str = Field(..., description="Trip title")
    description: str = Field(..., description="Trip description (HTML)")

    # Author info
    author: UserSummary = Field(..., description="Trip author (UserSummary)")

    # Trip metadata
    photos: list[PhotoSummary] = Field(
        default_factory=list, description="Trip photos (array of PhotoSummary)"
    )
    distance_km: float | None = Field(None, description="Distance in km (nullable)")
    start_date: date = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: date | None = Field(None, description="Trip end date (nullable)")

    # Route data
    locations: list[LocationSummary] = Field(
        default_factory=list, description="Trip locations (array of LocationSummary)"
    )
    tags: list[TagSummary] = Field(
        default_factory=list, description="Trip tags (array of TagSummary)"
    )

    # Social interaction counters (FR-006)
    likes_count: int = Field(default=0, ge=0, description="Number of likes on this trip")
    comments_count: int = Field(default=0, ge=0, description="Number of comments on this trip")
    shares_count: int = Field(default=0, ge=0, description="Number of shares on this trip")

    # User interaction state (FR-007)
    is_liked_by_me: bool = Field(
        default=False, description="True if current user has liked this trip"
    )

    # Timestamps
    created_at: datetime = Field(..., description="Trip creation timestamp (ISO 8601)")

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    """
    T024: Feed response schema (paginated list of feed items).

    Response for GET /feed endpoint with pagination metadata.

    Based on OpenAPI spec: specs/004-social-network/contracts/social-api.yaml
    """

    trips: list[FeedItem] = Field(default_factory=list, description="Array of feed items")
    total_count: int = Field(..., ge=0, description="Total number of trips in feed")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=50, description="Items per page")
    has_more: bool = Field(..., description="True if more pages exist beyond current page")

    class Config:
        from_attributes = True


# ============================================================
# ACTIVITY STREAM SCHEMAS (Feature 018)
# ============================================================


class PublicUserSummary(BaseModel):
    """
    Public user information for activity feed items (Feature 018 - T021).

    Minimal user data for displaying activity authors in the feed.
    """

    user_id: str = Field(..., description="User UUID")
    username: str = Field(..., description="Username")
    photo_url: str | None = Field(None, description="Profile photo URL (nullable)")

    class Config:
        from_attributes = True


class ActivityFeedItemSchema(BaseModel):
    """
    Activity feed item schema (Feature 018 - T021).

    Represents a single activity in the feed (trip published, photo uploaded, achievement).
    """

    activity_id: str = Field(..., description="Activity UUID")
    user: PublicUserSummary = Field(..., description="Activity author")
    activity_type: str = Field(
        ..., description="Activity type (TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED)"
    )
    metadata: dict = Field(default_factory=dict, description="Activity metadata (JSON)")
    created_at: datetime = Field(..., description="Activity creation timestamp (ISO 8601)")

    # Social interaction counters (Feature 018 - US2, US3)
    likes_count: int = Field(default=0, ge=0, description="Number of likes on this activity")
    comments_count: int = Field(default=0, ge=0, description="Number of comments on this activity")

    # User interaction state (Feature 018 - US2)
    is_liked_by_me: bool = Field(
        default=False, description="True if current user has liked this activity"
    )

    class Config:
        from_attributes = True


class ActivityFeedResponseSchema(BaseModel):
    """
    Activity feed response schema with cursor-based pagination (Feature 018 - T021).

    Response for GET /activity-feed endpoint.
    """

    activities: list[ActivityFeedItemSchema] = Field(
        default_factory=list, description="Array of activity feed items"
    )
    next_cursor: str | None = Field(None, description="Cursor for next page (null if last page)")
    has_next: bool = Field(..., description="True if more activities exist beyond current page")

    class Config:
        from_attributes = True
