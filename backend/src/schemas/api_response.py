"""
Standardized API response schemas.

Provides consistent response structure for all API endpoints
according to ContraVento constitution requirements.
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# Generic type for data payload
T = TypeVar("T")


class ErrorDetail(BaseModel):
    """
    Error detail schema for validation and field-specific errors.

    Attributes:
        code: Error code (e.g., VALIDATION_ERROR, UNAUTHORIZED)
        message: Human-readable error message in Spanish
        field: Optional field name for field-specific errors
    """

    code: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message (Spanish)")
    field: Optional[str] = Field(None, description="Field name for field-specific errors")

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "El email ya está registrado",
                "field": "email",
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Error response schema for failed requests.

    Attributes:
        success: Always False for errors
        data: Always None for errors
        error: Error details
    """

    success: bool = Field(default=False, description="Always False for errors")
    data: None = Field(default=None, description="Always None for errors")
    error: ErrorDetail = Field(..., description="Error details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "El email ya está registrado",
                    "field": "email",
                },
            }
        }
    }


class ApiResponse(BaseModel, Generic[T]):
    """
    Generic successful API response wrapper.

    Provides standardized structure for all successful API responses
    as defined in ContraVento constitution (Section III: User Experience).

    Format:
    {
        "success": true,
        "data": {...},
        "error": null
    }

    Attributes:
        success: Always True for successful responses
        data: Response payload (generic type)
        error: Always None for successful responses
    """

    success: bool = Field(default=True, description="Always True for successful responses")
    data: T = Field(..., description="Response payload")
    error: None = Field(default=None, description="Always None for successful responses")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "username": "ciclista",
                    "email": "usuario@ejemplo.com",
                },
                "error": None,
            }
        }
    }
