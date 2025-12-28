"""
Trip API endpoints for Travel Diary feature.

Provides REST API for creating, reading, updating, and publishing trips.
Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-008
"""

from typing import Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_current_user
from src.models.user import User
from src.schemas.trip import TripCreateRequest, TripResponse
from src.services.trip_service import TripService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create new trip",
    description="Create a new trip entry. Trip is created as 'draft' by default.",
)
async def create_trip(
    data: TripCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Create a new trip (FR-001, FR-002, FR-003).

    Creates trip with status=DRAFT. Supports tags, locations, and all optional fields.

    Args:
        data: Trip creation data
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        Standardized API response with created trip data

    Raises:
        400: Validation error
        401: Unauthorized (no valid token)
    """
    try:
        service = TripService(db)
        trip = await service.create_trip(user_id=current_user.id, data=data)

        # Convert to response schema
        trip_response = TripResponse.model_validate(trip)

        return {
            "success": True,
            "data": trip_response.model_dump(),
            "error": None,
        }

    except ValueError as e:
        logger.warning(f"Validation error creating trip: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e),
                },
            },
        )
    except Exception as e:
        logger.error(f"Error creating trip: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


@router.get(
    "/{trip_id}",
    response_model=Dict[str, Any],
    summary="Get trip by ID",
    description="Retrieve detailed trip information. Published trips visible to all, drafts only to owner.",
)
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get trip by ID (FR-007, FR-008).

    Visibility rules:
    - Published trips: visible to everyone
    - Draft trips: only visible to owner

    Args:
        trip_id: Trip identifier
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        Standardized API response with trip data

    Raises:
        404: Trip not found
        403: Access denied (draft trip, not owner)
        401: Unauthorized
    """
    try:
        service = TripService(db)
        trip = await service.get_trip(trip_id=trip_id, current_user_id=current_user.id)

        # Convert to response schema
        trip_response = TripResponse.model_validate(trip)

        return {
            "success": True,
            "data": trip_response.model_dump(),
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied accessing trip {trip_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "FORBIDDEN",
                    "message": str(e),
                },
            },
        )
    except ValueError as e:
        logger.warning(f"Trip {trip_id} not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "NOT_FOUND",
                    "message": str(e),
                },
            },
        )
    except Exception as e:
        logger.error(f"Error retrieving trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


@router.post(
    "/{trip_id}/publish",
    response_model=Dict[str, Any],
    summary="Publish trip",
    description="Change trip status from 'draft' to 'published'. Validates publication requirements.",
)
async def publish_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Publish a trip (FR-007).

    Validates that trip meets publication requirements:
    - Title present
    - Description >= 50 characters
    - Start date present

    Args:
        trip_id: Trip identifier
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        Standardized API response with published trip data

    Raises:
        400: Validation error (trip doesn't meet requirements)
        403: Permission denied (not trip owner)
        404: Trip not found
        401: Unauthorized
    """
    try:
        service = TripService(db)
        trip = await service.publish_trip(trip_id=trip_id, user_id=current_user.id)

        # Return minimal response with status and published_at
        return {
            "success": True,
            "data": {
                "trip_id": trip.trip_id,
                "status": trip.status.value,
                "published_at": trip.published_at.isoformat() + "Z" if trip.published_at else None,
            },
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied publishing trip {trip_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "FORBIDDEN",
                    "message": str(e),
                },
            },
        )
    except ValueError as e:
        error_msg = str(e)
        # Distinguish between not found and validation errors
        if "no encontrado" in error_msg.lower() or "not found" in error_msg.lower():
            status_code = status.HTTP_404_NOT_FOUND
            error_code = "NOT_FOUND"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            error_code = "VALIDATION_ERROR"

        logger.warning(f"Error publishing trip {trip_id}: {e}")
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": error_code,
                    "message": error_msg,
                    "field": "description" if "descripción" in error_msg.lower() else None,
                },
            },
        )
    except Exception as e:
        logger.error(f"Error publishing trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )
