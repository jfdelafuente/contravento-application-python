"""
User response schemas.

Pydantic models for user data in API responses.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.

    Returns user information without sensitive data (no password).

    Attributes:
        user_id: Unique user identifier (UUID)
        username: Username
        email: Email address
        is_verified: Email verification status
        profile_visibility: Profile visibility setting (Feature 013)
        trip_visibility: Trip visibility setting (Feature 013)
        created_at: Account creation timestamp
        photo_url: Profile photo URL (optional)
        bio: Profile biography (optional)
        location: User location (optional)
        cycling_type: Type of cycling (optional)
    """

    user_id: str = Field(..., description="Unique user identifier (UUID)")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    is_verified: bool = Field(..., description="Email verification status")
    profile_visibility: str = Field(..., description="Profile visibility: 'public' or 'private'")
    trip_visibility: str = Field(
        ..., description="Trip visibility: 'public', 'followers', or 'private'"
    )
    created_at: datetime = Field(..., description="Account creation timestamp (UTC)")

    # Optional profile fields
    photo_url: str | None = Field(None, description="Profile photo URL")
    bio: str | None = Field(None, description="Profile biography")
    location: str | None = Field(None, description="User location")
    cycling_type: str | None = Field(None, description="Type of cycling")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "maria_garcia",
                "email": "maria@example.com",
                "is_verified": True,
                "profile_visibility": "public",
                "trip_visibility": "public",
                "created_at": "2025-12-23T10:30:00Z",
                "photo_url": "https://storage.example.com/photos/user123.jpg",
                "bio": "Ciclista apasionada de las rutas de montaña",
                "location": "Madrid, España",
                "cycling_type": "mountain",
            }
        }

    @classmethod
    def from_user_model(cls, user):
        """
        Create UserResponse from User model.

        Args:
            user: User model instance

        Returns:
            UserResponse instance
        """
        # Check if profile is already loaded to avoid triggering lazy load
        # Use hasattr to check if the relationship is loaded in the instance
        profile = None
        if hasattr(user, "__dict__") and "profile" in user.__dict__:
            profile = user.profile

        return cls(
            user_id=user.id,
            username=user.username,
            email=user.email,
            is_verified=user.is_verified,
            profile_visibility=user.profile_visibility,
            trip_visibility=user.trip_visibility,
            created_at=user.created_at,
            photo_url=profile.profile_photo_url if profile else None,
            bio=profile.bio if profile else None,
            location=profile.location if profile else None,
            cycling_type=profile.cycling_type if profile else None,
        )


class UserProfileResponse(BaseModel):
    """
    Schema for user profile data in API responses.

    Returns extended profile information.

    Attributes:
        full_name: User's full name (optional)
        bio: Profile biography (optional)
        location: User's location (optional)
        cycling_type: Type of cycling (optional)
        profile_photo_url: URL to profile photo (optional)
        updated_at: Last profile update timestamp
    """

    full_name: str | None = Field(None, description="User's full name")
    bio: str | None = Field(None, description="Profile biography")
    location: str | None = Field(None, description="User's location")
    cycling_type: str | None = Field(None, description="Type of cycling")
    profile_photo_url: str | None = Field(None, description="URL to profile photo")
    updated_at: datetime = Field(..., description="Last profile update timestamp (UTC)")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "full_name": "María García",
                "bio": "Ciclista apasionada de las rutas de montaña",
                "location": "Madrid, España",
                "cycling_type": "mountain",
                "profile_photo_url": "https://storage.example.com/photos/user123.jpg",
                "updated_at": "2025-12-23T10:30:00Z",
            }
        }


class UserWithProfileResponse(UserResponse):
    """
    Schema for user data with profile information.

    Extends UserResponse with profile data.

    Attributes:
        profile: User profile information (optional)
    """

    profile: UserProfileResponse | None = Field(None, description="User profile information")

    class Config:
        """Pydantic config."""

        from_attributes = True
