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
        profile_visibility: Profile visibility ('public' or 'private')
        show_email: Privacy setting for email visibility
        show_location: Privacy setting for location visibility
        followers_count: Number of followers
        following_count: Number of users followed
        is_following: Whether current user follows this user (Feature 004 - US1, None if not authenticated)
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
    profile_visibility: str = Field(..., description="Profile visibility: 'public' or 'private'")
    trip_visibility: str = Field(
        ..., description="Trip visibility: 'public', 'followers', or 'private'"
    )
    show_email: bool = Field(..., description="Email visibility in public profile")
    show_location: bool = Field(..., description="Location visibility in public profile")
    followers_count: int = Field(default=0, description="Number of followers")
    following_count: int = Field(default=0, description="Number of users followed")
    is_following: Optional[bool] = Field(
        None,
        description="Whether current user follows this user (Feature 004 - US1, None if not authenticated)",
    )
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
                "profile_visibility": "public",
                "trip_visibility": "public",
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
        profile_visibility: Profile visibility (optional, 'public' or 'private')
        trip_visibility: Trip visibility (optional, 'public', 'followers', or 'private')
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

    profile_visibility: Optional[str] = Field(
        None,
        description="Profile visibility: 'public' (visible to all) or 'private' (hidden from public feed)",
        pattern="^(public|private)$",
    )

    trip_visibility: Optional[str] = Field(
        None,
        description="Trip visibility: 'public' (all), 'followers' (followers only), or 'private' (owner only)",
        pattern="^(public|followers|private)$",
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
                "profile_visibility": "public",
                "trip_visibility": "public",
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


class PasswordChangeRequest(BaseModel):
    """
    Schema for password change request.

    Validates password change data requiring current password verification.

    **Functional Requirements**: FR-009, FR-010

    Attributes:
        current_password: User's current password for verification
        new_password: New password (min 8 chars, uppercase, lowercase, number)
    """

    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (min 8 chars with uppercase, lowercase, and number)",
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength (FR-010)."""
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")

        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una mayúscula")

        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una minúscula")

        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")

        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {"current_password": "OldPass123!", "new_password": "NewSecurePass456!"}
        }
