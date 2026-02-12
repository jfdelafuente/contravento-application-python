"""
Authentication request/response schemas.

Pydantic models for validating authentication API requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.utils.validators import validate_password, validate_username


class RegisterRequest(BaseModel):
    """
    Schema for user registration request.

    Validates username, email, and password strength.

    Attributes:
        username: Unique username (3-30 alphanumeric + underscores)
        email: Valid email address
        password: Strong password (min 8 chars, with uppercase, lowercase, digit, special char)
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Unique username (3-30 alphanumeric + underscores)",
        examples=["maria_garcia"],
    )

    email: EmailStr = Field(..., description="Valid email address", examples=["maria@example.com"])

    password: str = Field(
        ...,
        min_length=8,
        description="Strong password (min 8 chars with complexity requirements)",
        examples=["SecurePass123!"],
    )

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, v: str) -> str:
        """Validate username format and characters."""
        return validate_username(v)

    @field_validator("password")
    @classmethod
    def validate_password_field(cls, v: str) -> str:
        """Validate password strength."""
        return validate_password(v)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "username": "maria_garcia",
                "email": "maria@example.com",
                "password": "SecurePass123!",
            }
        }


class RegisterResponse(BaseModel):
    """
    Schema for user registration response.

    Returns user data after successful registration.

    Attributes:
        user_id: Unique user identifier (UUID)
        username: Username
        email: Email address
        is_verified: Email verification status (always False on registration)
        is_active: Account active status (always True on registration)
        created_at: Account creation timestamp
    """

    user_id: str = Field(..., description="Unique user identifier (UUID)")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    is_verified: bool = Field(..., description="Email verification status")
    is_active: bool = Field(default=True, description="Account active status")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC)")

    @property
    def id(self) -> str:
        """Alias for user_id for backward compatibility."""
        return self.user_id

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "maria_garcia",
                "email": "maria@example.com",
                "is_verified": False,
                "is_active": True,
                "created_at": "2025-12-23T10:30:00Z",
            }
        }


class LoginRequest(BaseModel):
    """
    Schema for user login request.

    Accepts either username or email for login field.

    Attributes:
        login: Username or email
        password: User password
    """

    login: str = Field(
        ..., description="Username or email", examples=["maria_garcia", "maria@example.com"]
    )

    password: str = Field(..., description="User password", examples=["SecurePass123!"])

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"login": "maria_garcia", "password": "SecurePass123!"}}


class TokenResponse(BaseModel):
    """
    Schema for JWT token pair.

    Contains access token and refresh token.

    Attributes:
        access_token: JWT access token (15 min expiration)
        refresh_token: JWT refresh token (30 day expiration)
        token_type: Token type (always "bearer")
        expires_in: Access token expiration in seconds
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
            }
        }


class LoginResponse(BaseModel):
    """
    Schema for login response.

    Contains tokens and user information.

    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Token type (always "bearer")
        expires_in: Access token expiration in seconds
        user: User information
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: "UserResponse" = Field(..., description="User information")

    class Config:
        """Pydantic config."""

        from_attributes = True


class PasswordResetRequest(BaseModel):
    """
    Schema for password reset request.

    Requests a password reset token to be sent to email.

    Attributes:
        email: Email address to send reset link to
    """

    email: EmailStr = Field(
        ..., description="Email address to send reset link to", examples=["maria@example.com"]
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {"example": {"email": "maria@example.com"}}


class PasswordResetConfirm(BaseModel):
    """
    Schema for password reset confirmation.

    Confirms password reset with token and new password.

    Attributes:
        token: Password reset token from email
        new_password: New password
    """

    token: str = Field(
        ...,
        description="Password reset token from email",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )

    new_password: str = Field(
        ..., min_length=8, description="New password", examples=["NewSecurePass456!"]
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password strength."""
        return validate_password(v)

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "new_password": "NewSecurePass456!",
            }
        }


# Forward reference resolution
from src.schemas.user import UserResponse

LoginResponse.model_rebuild()
