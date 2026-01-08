"""
CyclingType request/response schemas.

Pydantic models for validating cycling type API requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class CyclingTypeResponse(BaseModel):
    """
    Schema for cycling type data in API responses.

    Returns cycling type information.

    Attributes:
        id: Unique identifier
        code: Unique code (e.g., 'bikepacking')
        display_name: Name to display in UI
        description: Detailed description
        is_active: Whether this type is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: str = Field(..., description="Unique identifier (UUID)")
    code: str = Field(..., description="Unique code (e.g., 'bikepacking')")
    display_name: str = Field(..., description="Display name for UI")
    description: Optional[str] = Field(None, description="Detailed description")
    is_active: bool = Field(..., description="Whether this type is active")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "code": "bikepacking",
                "display_name": "Bikepacking",
                "description": "Viajes de varios días en bicicleta con equipaje completo",
                "is_active": True,
                "created_at": "2025-01-08T10:30:00Z",
                "updated_at": "2025-01-08T10:30:00Z",
            }
        }


class CyclingTypePublicResponse(BaseModel):
    """
    Schema for public cycling type data (simplified).

    Returns only essential fields for public consumption.

    Attributes:
        code: Unique code
        display_name: Name to display in UI
        description: Detailed description
    """

    code: str = Field(..., description="Unique code (e.g., 'bikepacking')")
    display_name: str = Field(..., description="Display name for UI")
    description: Optional[str] = Field(None, description="Detailed description")

    class Config:
        """Pydantic config."""

        from_attributes = True
        json_schema_extra = {
            "example": {
                "code": "bikepacking",
                "display_name": "Bikepacking",
                "description": "Viajes de varios días en bicicleta con equipaje completo",
            }
        }


class CyclingTypeCreateRequest(BaseModel):
    """
    Schema for creating a new cycling type.

    Attributes:
        code: Unique code (lowercase, no spaces)
        display_name: Name to display in UI
        description: Detailed description (optional)
        is_active: Whether this type should be active (default: True)
    """

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique code (lowercase, no spaces, e.g., 'bikepacking')",
    )
    display_name: str = Field(
        ..., min_length=2, max_length=100, description="Display name for UI"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Detailed description (optional)"
    )
    is_active: bool = Field(True, description="Whether this type is active")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate code format: lowercase, alphanumeric and underscores only."""
        if not v:
            raise ValueError("El código es requerido")

        # Convert to lowercase
        v = v.lower().strip()

        # Check for valid characters (alphanumeric + underscores, no spaces)
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "El código solo puede contener letras, números, guiones y guiones bajos"
            )

        # No leading/trailing special chars
        if v.startswith(("_", "-")) or v.endswith(("_", "-")):
            raise ValueError("El código no puede empezar o terminar con guiones o guiones bajos")

        return v

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        """Validate display name."""
        if not v or not v.strip():
            raise ValueError("El nombre es requerido")

        return v.strip()

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "code": "bikepacking",
                "display_name": "Bikepacking",
                "description": "Viajes de varios días en bicicleta con equipaje completo",
                "is_active": True,
            }
        }


class CyclingTypeUpdateRequest(BaseModel):
    """
    Schema for updating an existing cycling type.

    All fields are optional - only provided fields will be updated.

    Attributes:
        display_name: New display name (optional)
        description: New description (optional)
        is_active: New active status (optional)
    """

    display_name: Optional[str] = Field(
        None, min_length=2, max_length=100, description="Display name for UI"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="Detailed description"
    )
    is_active: Optional[bool] = Field(None, description="Whether this type is active")

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate display name if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío")
        return v

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "display_name": "Bikepacking Aventura",
                "description": "Viajes de aventura de varios días con equipaje",
                "is_active": True,
            }
        }
