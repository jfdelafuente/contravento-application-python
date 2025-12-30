"""
Pydantic schemas for request/response validation.

Exports all schemas for API endpoints.
"""

from src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.schemas.trip import (
    LocationInput,
    TagResponse,
    TripCreateRequest,
    TripListItemResponse,
    TripListResponse,
    TripLocationResponse,
    TripPhotoResponse,
    TripResponse,
    TripUpdateRequest,
)
from src.schemas.user import UserResponse

__all__ = [
    "RegisterRequest",
    "RegisterResponse",
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "UserResponse",
    "LocationInput",
    "TripCreateRequest",
    "TripUpdateRequest",
    "TagResponse",
    "TripLocationResponse",
    "TripPhotoResponse",
    "TripResponse",
    "TripListItemResponse",
    "TripListResponse",
]
