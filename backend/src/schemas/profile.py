"""
Profile request/response schemas.

Pydantic models for validating profile API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.utils.validators import validate_bio


class ProfileStatsPreview(BaseModel):
    """
    T180: Preview of user stats for profile display.

    Lightweight stats summary shown on profile page.

    Attributes:
        total_trips: Number of trips
        total_kilometers: Total distance
        achievements_count: Number of achievements
    """

    total_trips: int = Field(default=0, description="Total trips")
    total_kilometers: float = Field(default=0.0, description="Total kilometers")
    achievements_count: int = Field(default=0, description="Achievements earned")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {"total_trips": 12, "total_kilometers": 1547.85, "achievements_count": 5}
        }


class ProfileResponse(BaseModel):
    """
    T115: Schema for profile data in API responses.

    Returns user profile information respecting privacy settings.

    Attributes:
        username: Unique username
        full_name: User's full name (optional)
        bio: Profile biography (optional, max 500 chars)
        photo_url: URL to profile photo (optional)
        location: User's location (optional)
        cycling_type: Type of cycling (optional enum)
        show_email: Privacy setting for email visibility
        show_location: Privacy setting for location visibility
        followers_count: Number of followers
        following_count: Number of users followed
        stats: Stats preview (T180)
        created_at: Account creation timestamp
    """

    username: str = Field(..., description="Unique username")
    full_name: Optional[str] = Field(None, description="User's full name")
    bio: Optional[str] = Field(None, description="Profile biography")
    photo_url: Optional[str] = Field(None, description="URL to profile photo")
    location: Optional[str] = Field(None, description="User's location")
    cycling_type: Optional[str] = Field(
        None, description="Type of cycling: bikepacking, commuting, gravel, mountain, road, touring"
    )
    show_email: bool = Field(..., description="Email visibility in public profile")
    show_location: bool = Field(..., description="Location visibility in public profile")
    followers_count: int = Field(default=0, description="Number of followers")
    following_count: int = Field(default=0, description="Number of users followed")
    stats: Optional[ProfileStatsPreview] = Field(None, description="Stats preview")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC)")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "username": "maria_garcia",
                "full_name": "María García",
                "bio": "Ciclista de montaña apasionada 🚵‍♀️",
                "photo_url": "https://api.contravento.com/storage/profile_photos/2025/12/user123.jpg",
                "location": "Barcelona, España",
                "cycling_type": "mountain",
                "show_email": False,
                "show_location": True,
                "followers_count": 42,
                "following_count": 58,
                "created_at": "2025-01-15T10:30:00Z",
            }
        }


class ProfileUpdateRequest(BaseModel):
    """
    T116: Schema for profile update request.

    Validates profile update data including bio length and cycling_type enum.

    Attributes:
        full_name: User's full name (optional, max 100 chars)
        bio: Profile biography (optional, max 500 chars)
        location: User's location (optional, max 100 chars)
        cycling_type: Type of cycling (optional, must be valid enum)
        show_email: Email visibility setting (optional)
        show_location: Location visibility setting (optional)
    """

    full_name: Optional[str] = Field(
        None, max_length=100, description="User's full name (max 100 characters)"
    )

    bio: Optional[str] = Field(
        None, max_length=500, description="Profile biography (max 500 characters)"
    )

    location: Optional[str] = Field(
        None, max_length=100, description="User's location (max 100 characters)"
    )

    cycling_type: Optional[str] = Field(
        None, description="Type of cycling: bikepacking, commuting, gravel, mountain, road, touring"
    )

    show_email: Optional[bool] = Field(None, description="Show email in public profile")

    show_location: Optional[bool] = Field(None, description="Show location in public profile")

    @field_validator("bio")
    @classmethod
    def validate_bio_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate bio format and length."""
        if v is not None:
            return validate_bio(v)
        return v

    # NOTE: cycling_type validation is done in ProfileService.update_profile()
    # using validate_cycling_type_async() to check against active types in database

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "full_name": "María García López",
                "bio": "Ciclista de montaña. Explorando senderos y compartiendo aventuras.",
                "location": "Barcelona, España",
                "cycling_type": "mountain",
                "show_email": False,
                "show_location": True,
            }
        }


class PrivacySettings(BaseModel):
    """
    T117: Schema for privacy settings.

    Manages visibility of personal information in public profile.

    Attributes:
        show_email: Whether to show email in public profile
        show_location: Whether to show location in public profile
    """

    show_email: Optional[bool] = Field(None, description="Show email in public profile")

    show_location: Optional[bool] = Field(None, description="Show location in public profile")

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"show_email": False, "show_location": True}}


class PhotoUploadResponse(BaseModel):
    """
    Schema for photo upload response.

    Returns information about uploaded photo.

    Attributes:
        photo_url: URL to the uploaded photo
        photo_width: Photo width in pixels (should be 400)
        photo_height: Photo height in pixels (should be 400)
    """

    photo_url: str = Field(..., description="URL to uploaded photo")
    photo_width: int = Field(..., description="Photo width in pixels")
    photo_height: int = Field(..., description="Photo height in pixels")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "photo_url": "https://api.contravento.com/storage/profile_photos/2025/12/user123.jpg",
                "photo_width": 400,
                "photo_height": 400,
            }
        }
