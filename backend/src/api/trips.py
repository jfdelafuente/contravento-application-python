"""
Trip API endpoints for Travel Diary feature.

Provides REST API for creating, reading, updating, and publishing trips.
Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.trip import TripStatus
from src.models.user import User
from src.schemas.trip import TripCreateRequest, TripResponse
from src.services.trip_service import TripService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["trips"])
# Separate router for user-facing endpoints (no prefix needed)
user_router = APIRouter(tags=["trips"])


@router.post(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create new trip",
    description="Create a new trip entry. Trip is created as 'draft' by default.",
)
async def create_trip(
    data: TripCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
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
    response_model=dict[str, Any],
    summary="Get trip by ID",
    description="Retrieve detailed trip information. Published trips visible to all, drafts only to owner.",
)
async def get_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
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
    response_model=dict[str, Any],
    summary="Publish trip",
    description="Change trip status from 'draft' to 'published'. Validates publication requirements.",
)
async def publish_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
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


# Pydantic schema for photo reorder request
class PhotoReorderRequest(BaseModel):
    """Request schema for reordering photos."""

    photo_order: list[str]


@router.post(
    "/{trip_id}/photos",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Upload photo to trip",
    description="Upload a photo to trip gallery. Max 20 photos per trip, max 10MB per photo.",
)
async def upload_photo(
    trip_id: str,
    photo: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Upload photo to trip (FR-009, FR-010, FR-011).

    Validates photo format (JPG, PNG, WebP), checks limit (max 20),
    processes image (resize, thumbnail generation), and saves to storage.

    Args:
        trip_id: Trip identifier
        photo: Photo file
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        Standardized API response with photo data

    Raises:
        400: Invalid photo format or limit exceeded
        404: Trip not found
        403: Permission denied (not trip owner)
        401: Unauthorized
    """
    try:
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB in bytes
        photo.file.seek(0, 2)  # Seek to end
        file_size = photo.file.tell()
        photo.file.seek(0)  # Reset to beginning

        if file_size > max_size:
            raise ValueError("La foto excede el tamaño máximo de 10MB")

        # Upload photo
        service = TripService(db)
        photo_record = await service.upload_photo(
            trip_id=trip_id,
            user_id=current_user.id,
            photo_file=photo.file,
            filename=photo.filename,
            content_type=photo.content_type,
        )

        return {
            "success": True,
            "data": {
                "id": photo_record.photo_id,
                "trip_id": photo_record.trip_id,
                "photo_url": photo_record.photo_url,
                "thumb_url": photo_record.thumb_url,
                "order": photo_record.order,
                "file_size": photo_record.file_size,
                "width": photo_record.width,
                "height": photo_record.height,
                "uploaded_at": photo_record.uploaded_at.isoformat() + "Z"
                if photo_record.uploaded_at
                else None,
            },
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied uploading photo to trip {trip_id}: {e}")
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
        # Check if it's a not found error or validation error
        if "no encontrado" in error_msg.lower() or "not found" in error_msg.lower():
            status_code = status.HTTP_404_NOT_FOUND
            error_code = "NOT_FOUND"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            error_code = "VALIDATION_ERROR"

        logger.warning(f"Error uploading photo to trip {trip_id}: {e}")
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": error_code,
                    "message": error_msg,
                },
            },
        )
    except Exception as e:
        logger.error(f"Error uploading photo to trip {trip_id}: {e}", exc_info=True)
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


@router.delete(
    "/{trip_id}/photos/{photo_id}",
    response_model=dict[str, Any],
    summary="Delete photo from trip",
    description="Remove a photo from trip gallery and delete files from storage.",
)
async def delete_photo(
    trip_id: str,
    photo_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Delete photo from trip (FR-013).

    Removes photo from database and deletes files from storage.

    Args:
        trip_id: Trip identifier
        photo_id: Photo identifier
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        Standardized API response with success message

    Raises:
        404: Trip or photo not found
        403: Permission denied (not trip owner)
        401: Unauthorized
    """
    try:
        service = TripService(db)
        result = await service.delete_photo(
            trip_id=trip_id,
            photo_id=photo_id,
            user_id=current_user.id,
        )

        return {
            "success": True,
            "data": result,
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied deleting photo {photo_id} from trip {trip_id}: {e}")
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
        logger.warning(f"Error deleting photo {photo_id} from trip {trip_id}: {e}")
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
        logger.error(f"Error deleting photo {photo_id} from trip {trip_id}: {e}", exc_info=True)
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


@router.put(
    "/{trip_id}/photos/reorder",
    response_model=dict[str, Any],
    summary="Reorder photos in trip gallery",
    description="Update the order of photos in trip gallery.",
)
async def reorder_photos(
    trip_id: str,
    request: PhotoReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Reorder photos in trip gallery (FR-012).

    Updates the order field for each photo based on provided photo_ids list.

    Args:
        trip_id: Trip identifier
        request: Photo reorder request with photo_order list
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        Standardized API response with success message

    Raises:
        400: Invalid photo IDs (don't match trip's photos)
        404: Trip not found
        403: Permission denied (not trip owner)
        401: Unauthorized
    """
    try:
        service = TripService(db)
        result = await service.reorder_photos(
            trip_id=trip_id,
            user_id=current_user.id,
            photo_order=request.photo_order,
        )

        return {
            "success": True,
            "data": result,
            "error": None,
        }

    except PermissionError as e:
        logger.warning(f"Permission denied reordering photos for trip {trip_id}: {e}")
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
        # Check if it's a not found error or validation error
        if "no encontrado" in error_msg.lower() or "not found" in error_msg.lower():
            status_code = status.HTTP_404_NOT_FOUND
            error_code = "NOT_FOUND"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            error_code = "VALIDATION_ERROR"

        logger.warning(f"Error reordering photos for trip {trip_id}: {e}")
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": error_code,
                    "message": error_msg,
                },
            },
        )
    except Exception as e:
        logger.error(f"Error reordering photos for trip {trip_id}: {e}", exc_info=True)
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


@router.put(
    "/{trip_id}",
    response_model=dict[str, Any],
    summary="Update trip",
    description="Update existing trip. Supports partial updates with optimistic locking.",
)
async def update_trip(
    trip_id: str,
    data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update trip (FR-016, FR-020)."""
    try:
        service = TripService(db)
        trip = await service.update_trip(trip_id=trip_id, user_id=current_user.id, data=data)
        trip_response = TripResponse.model_validate(trip)
        return {"success": True, "data": trip_response.model_dump(), "error": None}
    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "data": None,
                "error": {"code": "FORBIDDEN", "message": str(e)},
            },
        )
    except ValueError as e:
        status_code = (
            404
            if "no encontrado" in str(e).lower()
            else 409
            if "modificado" in str(e).lower()
            else 400
        )
        error_code = (
            "NOT_FOUND"
            if status_code == 404
            else "CONFLICT"
            if status_code == 409
            else "VALIDATION_ERROR"
        )
        raise HTTPException(
            status_code=status_code,
            detail={
                "success": False,
                "data": None,
                "error": {"code": error_code, "message": str(e)},
            },
        )
    except Exception as e:
        logger.error(f"Error updating trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": {"code": "INTERNAL_ERROR", "message": "Error interno del servidor"},
            },
        )


@router.delete(
    "/{trip_id}",
    response_model=dict[str, Any],
    summary="Delete trip",
    description="Permanently delete trip and all associated data.",
)
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Delete trip (FR-017, FR-018)."""
    try:
        service = TripService(db)
        result = await service.delete_trip(trip_id=trip_id, user_id=current_user.id)
        return {"success": True, "data": result, "error": None}
    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "data": None,
                "error": {"code": "FORBIDDEN", "message": str(e)},
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "data": None,
                "error": {"code": "NOT_FOUND", "message": str(e)},
            },
        )
    except Exception as e:
        logger.error(f"Error deleting trip {trip_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": {"code": "INTERNAL_ERROR", "message": "Error interno del servidor"},
            },
        )


# ============================================================================
# Phase 6: Tags & Categorization (User Story 4)
# ============================================================================


@user_router.get(
    "/users/{username}/trips",
    response_model=dict[str, Any],
    summary="Get user trips with filters",
    description="FR-025: List user's trips with optional tag and status filtering",
)
async def get_user_trips(
    username: str,
    tag: Optional[str] = Query(None, description="Filter by tag name (case-insensitive)"),
    status: Optional[TripStatus] = Query(None, description="Filter by trip status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum trips to return"),
    offset: int = Query(0, ge=0, description="Number of trips to skip"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get user's trips with optional filtering (T088, FR-025).

    **Filters:**
    - tag: Filter by tag name (case-insensitive)
    - status: Filter by trip status (DRAFT or PUBLISHED)
    - limit: Max trips to return (1-100, default 50)
    - offset: Pagination offset (default 0)

    **Returns:**
    - List of trips with photos, tags, and locations
    - Ordered by created_at descending (newest first)
    """
    try:
        from sqlalchemy import select

        from src.models.user import User

        # Get user by username
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "USER_NOT_FOUND",
                        "message": f"Usuario '{username}' no encontrado",
                    },
                },
            )

        service = TripService(db)
        trips = await service.get_user_trips(
            user_id=user.id,
            tag=tag,
            status=status,
            limit=limit,
            offset=offset,
        )

        # Convert to response format
        trips_data = [
            {
                "trip_id": trip.trip_id,
                "user_id": trip.user_id,
                "title": trip.title,
                "description": trip.description,
                "start_date": trip.start_date.isoformat() if trip.start_date else None,
                "end_date": trip.end_date.isoformat() if trip.end_date else None,
                "distance_km": trip.distance_km,
                "status": trip.status.value,
                "photos_count": len(trip.photos),
                "tags": [tag_rel.tag.name for tag_rel in trip.tags],
                "created_at": trip.created_at.isoformat(),
                "updated_at": trip.updated_at.isoformat(),
            }
            for trip in trips
        ]

        return {
            "success": True,
            "data": {
                "trips": trips_data,
                "count": len(trips_data),
                "limit": limit,
                "offset": offset,
            },
            "error": None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trips for user {username}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )


@user_router.get(
    "/tags",
    response_model=dict[str, Any],
    summary="Get all tags",
    description="FR-027: List all available tags ordered by popularity",
)
async def get_all_tags(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get all tags ordered by usage count (T089, FR-027).

    **Returns:**
    - List of tags with usage counts
    - Ordered by usage_count descending (most popular first)
    """
    try:
        service = TripService(db)
        tags = await service.get_all_tags()

        tags_data = [
            {
                "tag_id": tag.tag_id,
                "name": tag.name,
                "normalized": tag.normalized,
                "usage_count": tag.usage_count,
                "created_at": tag.created_at.isoformat(),
            }
            for tag in tags
        ]

        return {
            "success": True,
            "data": {"tags": tags_data, "count": len(tags_data)},
            "error": None,
        }

    except Exception as e:
        logger.error(f"Error getting tags: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )
