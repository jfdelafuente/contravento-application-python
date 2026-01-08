"""
Cycling Types API endpoints.

Handles cycling type management (public and admin endpoints).

Public endpoints:
- GET /cycling-types: List all active cycling types

Admin endpoints:
- GET /admin/cycling-types: List all cycling types (including inactive)
- POST /admin/cycling-types: Create new cycling type
- GET /admin/cycling-types/{code}: Get cycling type by code
- PUT /admin/cycling-types/{code}: Update cycling type
- DELETE /admin/cycling-types/{code}: Delete cycling type (soft delete)
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_admin, get_db
from src.models.user import User
from src.schemas.cycling_type import (
    CyclingTypeCreateRequest,
    CyclingTypePublicResponse,
    CyclingTypeResponse,
    CyclingTypeUpdateRequest,
)
from src.services.cycling_type_service import CyclingTypeService

logger = logging.getLogger(__name__)

# Public router
router = APIRouter(tags=["cycling-types"])

# Admin router
admin_router = APIRouter(prefix="/admin", tags=["admin", "cycling-types"])


def create_response(
    success: bool, data: Any = None, error: dict = None, message: str = None
) -> dict:
    """
    Create standardized JSON response.

    Args:
        success: Success flag
        data: Response data
        error: Error details
        message: Optional success message

    Returns:
        Standardized response dict
    """
    response = {"success": success, "data": data, "error": error}
    if message:
        response["message"] = message
    return response


# ===== PUBLIC ENDPOINTS =====


@router.get("/cycling-types", response_model=list[CyclingTypePublicResponse])
async def get_cycling_types_public(
    db: AsyncSession = Depends(get_db),
) -> list[CyclingTypePublicResponse]:
    """
    Get all active cycling types (public endpoint).

    Returns only active cycling types available for user selection.
    No authentication required.

    Args:
        db: Database session

    Returns:
        List of active cycling types
    """
    try:
        service = CyclingTypeService(db)
        cycling_types = await service.get_all_public()

        return cycling_types

    except Exception as e:
        logger.error(f"Error retrieving public cycling types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al obtener los tipos de ciclismo",
            },
        )


# ===== ADMIN ENDPOINTS =====


@admin_router.get("/cycling-types", response_model=list[CyclingTypeResponse])
async def get_all_cycling_types_admin(
    active_only: bool = Query(False, description="Filter to only active types"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> list[CyclingTypeResponse]:
    """
    Get all cycling types (admin endpoint).

    Returns all cycling types including inactive ones.
    Requires admin role.

    Args:
        active_only: If True, only return active types
        db: Database session
        admin: Current admin user

    Returns:
        List of cycling types
    """
    try:
        service = CyclingTypeService(db)
        cycling_types = await service.get_all(active_only=active_only)

        return cycling_types

    except Exception as e:
        logger.error(f"Error retrieving cycling types (admin): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al obtener los tipos de ciclismo",
            },
        )


@admin_router.get("/cycling-types/{code}", response_model=CyclingTypeResponse)
async def get_cycling_type_by_code_admin(
    code: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> CyclingTypeResponse:
    """
    Get cycling type by code (admin endpoint).

    Requires admin role.

    Args:
        code: Cycling type code
        db: Database session
        admin: Current admin user

    Returns:
        Cycling type details

    Raises:
        HTTPException 404: If cycling type not found
    """
    try:
        service = CyclingTypeService(db)
        cycling_type = await service.get_by_code(code)

        if not cycling_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "NOT_FOUND",
                    "message": f"No se encontró el tipo de ciclismo '{code}'",
                },
            )

        return cycling_type

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving cycling type {code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al obtener el tipo de ciclismo",
            },
        )


@admin_router.post("/cycling-types", status_code=status.HTTP_201_CREATED)
async def create_cycling_type_admin(
    data: CyclingTypeCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    """
    Create a new cycling type (admin endpoint).

    Requires admin role.

    Args:
        data: Cycling type creation data
        db: Database session
        admin: Current admin user

    Returns:
        Created cycling type

    Raises:
        HTTPException 400: If validation fails or code already exists
    """
    try:
        service = CyclingTypeService(db)
        cycling_type = await service.create(data)

        return create_response(
            success=True,
            data=cycling_type.model_dump(),
            message="Tipo de ciclismo creado correctamente",
        )

    except ValueError as e:
        # Code already exists or validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(f"Error creating cycling type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al crear el tipo de ciclismo",
            },
        )


@admin_router.put("/cycling-types/{code}")
async def update_cycling_type_admin(
    code: str,
    data: CyclingTypeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    """
    Update an existing cycling type (admin endpoint).

    Requires admin role.

    Args:
        code: Cycling type code to update
        data: Update data
        db: Database session
        admin: Current admin user

    Returns:
        Updated cycling type

    Raises:
        HTTPException 404: If cycling type not found
        HTTPException 400: If validation fails
    """
    try:
        service = CyclingTypeService(db)
        cycling_type = await service.update(code, data)

        return create_response(
            success=True,
            data=cycling_type.model_dump(),
            message="Tipo de ciclismo actualizado correctamente",
        )

    except ValueError as e:
        # Not found or validation error
        error_msg = str(e)

        if "no se encontró" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "NOT_FOUND",
                    "message": error_msg,
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "VALIDATION_ERROR",
                    "message": error_msg,
                },
            )

    except Exception as e:
        logger.error(f"Error updating cycling type {code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al actualizar el tipo de ciclismo",
            },
        )


@admin_router.delete("/cycling-types/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycling_type_admin(
    code: str,
    hard: bool = Query(False, description="If True, hard delete; if False, soft delete"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> None:
    """
    Delete a cycling type (admin endpoint).

    By default, performs soft delete (sets is_active=False).
    Use hard=True for permanent deletion.

    Requires admin role.

    Args:
        code: Cycling type code to delete
        hard: If True, hard delete; if False, soft delete
        db: Database session
        admin: Current admin user

    Raises:
        HTTPException 404: If cycling type not found
    """
    try:
        service = CyclingTypeService(db)
        await service.delete(code, soft=not hard)

        # No content response
        return None

    except ValueError as e:
        # Not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "NOT_FOUND",
                "message": str(e),
            },
        )
    except Exception as e:
        logger.error(f"Error deleting cycling type {code}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al eliminar el tipo de ciclismo",
            },
        )
