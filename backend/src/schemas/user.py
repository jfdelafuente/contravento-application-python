"""
User response schemas.

Pydantic models for user data in API responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.

    Returns user information without sensitive data (no password).

    Attributes:
        user_id: Unique user identifier (UUID)
        username: Username
        email: Email address
        is_verified: Email verification status
        created_at: Account creation timestamp
    """

    user_id: str = Field(..., description="Unique user identifier (UUID)")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC)")

    class Config:
        """Pydantic config."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "maria_garcia",
                "email": "maria@example.com",
                "is_verified": True,
                "created_at": "2025-12-23T10:30:00Z"
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
        return cls(
            user_id=user.id,
            username=user.username,
            email=user.email,
            is_verified=user.is_verified,
            created_at=user.created_at,
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

    full_name: Optional[str] = Field(None, description="User's full name")
    bio: Optional[str] = Field(None, description="Profile biography")
    location: Optional[str] = Field(None, description="User's location")
    cycling_type: Optional[str] = Field(None, description="Type of cycling")
    profile_photo_url: Optional[str] = Field(None, description="URL to profile photo")
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
                "updated_at": "2025-12-23T10:30:00Z"
            }
        }


class UserWithProfileResponse(UserResponse):
    """
    Schema for user data with profile information.

    Extends UserResponse with profile data.

    Attributes:
        profile: User profile information (optional)
    """

    profile: Optional[UserProfileResponse] = Field(None, description="User profile information")

    class Config:
        """Pydantic config."""
        from_attributes = True
