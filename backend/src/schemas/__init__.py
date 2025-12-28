"""
Pydantic schemas for request/response validation.

Exports all schemas for API endpoints.
"""

from src.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from src.schemas.user import UserResponse
from src.schemas.trip import (
    LocationInput,
    TripCreateRequest,
    TripUpdateRequest,
    TagResponse,
    TripLocationResponse,
    TripPhotoResponse,
    TripResponse,
    TripListItemResponse,
    TripListResponse,
)

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
