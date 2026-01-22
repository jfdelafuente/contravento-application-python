"""
Trip API endpoints for Travel Diary feature.

Provides REST API for creating, reading, updating, and publishing trips.
Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-008, FR-009, FR-010, FR-011, FR-012, FR-013
"""

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.deps import get_current_user, get_db, get_optional_current_user
from src.config import settings
from src.models.gpx import GPXFile, TrackPoint
from src.models.trip import Trip, TripStatus
from src.models.user import User
from src.schemas.gpx import (
    GPXMetadataSuccessResponse,
    GPXStatusSuccessResponse,
    GPXUploadSuccessResponse,
    TrackDataSuccessResponse,
)
from src.schemas.trip import (
    PaginationInfo,
    PublicLocationSummary,
    PublicPhotoSummary,
    PublicTripListResponse,
    PublicTripSummary,
    PublicUserSummary,
    TripCreateRequest,
    TripResponse,
    TripUpdateRequest,
)
from src.services.gpx_service import GPXService
from src.services.trip_service import TripService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["trips"])
# Separate router for user-facing endpoints (no prefix needed)
user_router = APIRouter(tags=["trips"])


@router.get(
    "/public",
    response_model=PublicTripListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get public trips feed",
    description="Get paginated list of published trips with public visibility (Feature 013).",
)
async def get_public_trips(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(
        default=None,
        ge=1,
        le=None,
        description=f"Items per page (default: {settings.public_feed_page_size}, max: {settings.public_feed_max_page_size})",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> PublicTripListResponse:
    """
    T021: Get public trips feed for homepage (Feature 013).

    Returns published trips with public trip visibility.
    No authentication required - fully public endpoint.

    Privacy filtering (FR-003):
    - Only trips with status=PUBLISHED
    - Only trips with trip_visibility='public'
    - Note: profile_visibility does NOT affect trip visibility (only controls profile info)

    Pagination:
    - Default: Configurable via PUBLIC_FEED_PAGE_SIZE (default 8)
    - Max: Configurable via PUBLIC_FEED_MAX_PAGE_SIZE (default 50)

    Args:
        page: Page number (1-indexed, default 1)
        limit: Items per page (configurable, default 8, max 50)
        db: Database session

    Returns:
        PublicTripListResponse with trips list and pagination metadata

    Examples:
        GET /trips/public?page=1&limit=20
        Response:
        {
            "trips": [
                {
                    "trip_id": "550e8400-...",
                    "title": "Vía Verde del Aceite",
                    "start_date": "2024-05-15",
                    "distance_km": 127.3,
                    "photo": {"photo_url": "...", "thumbnail_url": "..."},
                    "location": {"name": "Baeza, España"},
                    "author": {"user_id": "123e...", "username": "maria_ciclista", ...},
                    "published_at": "2024-12-22T15:45:00Z"
                }
            ],
            "pagination": {
                "total": 127,
                "page": 1,
                "limit": 20,
                "total_pages": 7
            }
        }
    """
    # Apply default limit and validate max
    if limit is None:
        limit = settings.public_feed_page_size
    elif limit > settings.public_feed_max_page_size:
        limit = settings.public_feed_max_page_size

    try:
        service = TripService(db)
        trips, total = await service.get_public_trips(page=page, limit=limit)

        # Calculate total pages
        total_pages = (total + limit - 1) // limit if total > 0 else 0

        # Map Trip entities to PublicTripSummary schema
        public_trips = []
        for trip in trips:
            # Extract first photo (order=0)
            first_photo = None
            if trip.photos:
                # Photos are already sorted by order in the model
                photo = trip.photos[0]
                first_photo = PublicPhotoSummary(
                    photo_url=photo.photo_url,
                    thumbnail_url=photo.thumbnail_url,
                )

            # Extract first location (sequence=0)
            first_location = None
            if trip.locations:
                # Locations are already sorted by sequence in the model
                location = trip.locations[0]
                first_location = PublicLocationSummary(name=location.name)

            # Count likes for this trip (Feature 004 - US2)
            from src.models.like import Like

            like_count_result = await db.execute(
                select(func.count(Like.id)).where(Like.trip_id == trip.trip_id)
            )
            like_count = like_count_result.scalar() or 0

            # Check if current user has liked this trip (Feature 004 - US2)
            is_liked = None
            if current_user:
                like_result = await db.execute(
                    select(Like).where(
                        Like.trip_id == trip.trip_id, Like.user_id == current_user.id
                    )
                )
                is_liked = like_result.scalar_one_or_none() is not None

            # Check if current user follows this trip's author (Feature 004 - US1)
            from src.models.social import Follow

            is_following = None
            if current_user:
                follow_result = await db.execute(
                    select(Follow).where(
                        Follow.follower_id == current_user.id, Follow.following_id == trip.user.id
                    )
                )
                is_following = follow_result.scalar_one_or_none() is not None

            # Map user to PublicUserSummary
            author = PublicUserSummary(
                user_id=trip.user.id,
                username=trip.user.username,
                profile_photo_url=trip.user.profile.profile_photo_url
                if trip.user.profile
                else None,
                is_following=is_following,  # Feature 004 - US1 (None if not authenticated, True/False if authenticated)
            )

            # Create PublicTripSummary
            public_trip = PublicTripSummary(
                trip_id=trip.trip_id,
                title=trip.title,
                start_date=trip.start_date,
                distance_km=trip.distance_km,
                photo=first_photo,
                location=first_location,
                author=author,
                published_at=trip.published_at,
                like_count=like_count,  # Feature 004 - US2
                is_liked=is_liked,  # Feature 004 - US2 (None if not authenticated, True/False if authenticated)
            )
            public_trips.append(public_trip)

        # Build pagination metadata
        pagination = PaginationInfo(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )

        logger.info(f"Public feed: page={page}, limit={limit}, total={total}")

        return PublicTripListResponse(
            trips=public_trips,
            pagination=pagination,
        )

    except Exception as e:
        logger.error(f"Error fetching public trips: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "PUBLIC_FEED_ERROR",
                "message": "Error al obtener viajes públicos",
            },
        )


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
    description="Retrieve detailed trip information. Published trips visible to all (no auth required), drafts only to owner.",
)
async def get_trip(
    trip_id: str,
    current_user: User | None = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get trip by ID (FR-007, FR-008, Feature 013).

    Visibility rules (Feature 013):
    - Published trips with trip_visibility='public': visible to everyone (no auth required)
    - Published trips with trip_visibility='followers': visible to followers and owner
    - Published trips with trip_visibility='private': only visible to owner
    - Draft trips: only visible to owner

    Args:
        trip_id: Trip identifier
        current_user: Optional authenticated user (from JWT, None if not authenticated)
        db: Database session

    Returns:
        Standardized API response with trip data

    Raises:
        404: Trip not found
        403: Access denied (insufficient permissions based on visibility settings)
    """
    try:
        service = TripService(db)
        trip = await service.get_trip(
            trip_id=trip_id, current_user_id=current_user.id if current_user else None
        )

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
    data: TripUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update trip (FR-016, FR-020)."""
    try:
        service = TripService(db)
        # Convert Pydantic model to dict, excluding None values
        update_data = data.model_dump(exclude_none=True)
        trip = await service.update_trip(
            trip_id=trip_id, user_id=current_user.id, update_data=update_data
        )
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
    tag: str | None = Query(None, description="Filter by tag name (case-insensitive)"),
    status: TripStatus | None = Query(None, description="Filter by trip status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum trips to return"),
    offset: int = Query(0, ge=0, description="Number of trips to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """
    Get user's trips with optional filtering (T088, FR-025, Feature 013).

    **Filters:**
    - tag: Filter by tag name (case-insensitive)
    - status: Filter by trip status (DRAFT or PUBLISHED)
    - limit: Max trips to return (1-100, default 50)
    - offset: Pagination offset (default 0)

    **Visibility (Feature 013):**
    - Owner: sees all trips (drafts and published, any visibility)
    - Followers: see published trips with visibility='public' or 'followers'
    - Public: see only published trips with visibility='public'

    **Returns:**
    - List of trips with photos, tags, and locations
    - Ordered by created_at descending (newest first)
    - Filtered by trip_visibility settings
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
            current_user_id=current_user.id if current_user else None,
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
                "photo_count": len(trip.photos),
                "tag_names": [tag_rel.tag.name for tag_rel in trip.trip_tags],
                "thumbnail_url": trip.photos[0].thumbnail_url if trip.photos else None,
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


# ============================================================================
# Feature 003 - GPS Routes Interactive (GPX Endpoints)
# ============================================================================


@router.post(
    "/{trip_id}/gpx",
    response_model=GPXUploadSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload GPX file to trip",
    description="Upload a GPX file to a trip. Files <1MB processed sync, >1MB async.",
)
async def upload_gpx_file(
    trip_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GPXUploadSuccessResponse:
    """
    T029: Upload GPX file to trip (FR-001, FR-002, SC-002, SC-003).

    Processing modes:
    - Files <1MB: Synchronous (201 Created with full data)
    - Files >1MB: Asynchronous (202 Accepted, poll /gpx/{gpx_id}/status)

    Requirements:
    - User must be trip owner
    - File must be .gpx format
    - File size ≤10MB (FR-001)
    - Trip can have at most 1 GPX file

    Performance:
    - SC-002: <3s for files <1MB
    - SC-003: <15s for files 5-10MB

    Args:
        trip_id: Trip identifier
        file: GPX file upload
        background_tasks: FastAPI background tasks
        current_user: Authenticated user
        db: Database session

    Returns:
        GPXUploadSuccessResponse with upload status and data

    Raises:
        400: Validation error (file too large, invalid format, trip already has GPX)
        401: Unauthorized
        403: Forbidden (not trip owner)
        404: Trip not found
    """
    try:
        # Validate file extension (T034)
        if not file.filename or not file.filename.lower().endswith(".gpx"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": "Solo se permiten archivos .gpx",
                    },
                },
            )

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Validate file size (max 10MB) - T034, FR-001
        MAX_SIZE_MB = 10
        max_size_bytes = MAX_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": f"El archivo GPX no puede exceder {MAX_SIZE_MB}MB. Tamaño actual: {file_size / (1024 * 1024):.1f}MB",
                    },
                },
            )

        # Verify trip exists
        trip_result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Viaje no encontrado",
                    },
                },
            )

        # Check ownership
        if trip.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Solo el propietario del viaje puede subir archivos GPX",
                    },
                },
            )

        # Check if trip already has GPX file - T034
        existing_gpx = await db.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        if existing_gpx.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "TRIP_ALREADY_HAS_GPX",
                        "message": "Este viaje ya tiene un archivo GPX. Elimínalo primero si deseas subir uno nuevo.",
                    },
                },
            )

        # Initialize GPX service
        gpx_service = GPXService(db)

        # Determine processing mode based on file size
        ASYNC_THRESHOLD_MB = 1
        async_threshold_bytes = ASYNC_THRESHOLD_MB * 1024 * 1024

        if file_size <= async_threshold_bytes:
            # Synchronous processing (<1MB files) - SC-002
            try:
                # Parse GPX file (T023)
                parsed_data = await gpx_service.parse_gpx_file(file_content)

                # Save original file to storage (T026)
                file_url = await gpx_service.save_gpx_to_storage(
                    trip_id=trip_id, file_content=file_content, filename=file.filename
                )

                # Create GPX file record
                from datetime import UTC, datetime

                gpx_file = GPXFile(
                    trip_id=trip_id,
                    file_url=file_url,
                    file_size=file_size,
                    file_name=file.filename,
                    distance_km=parsed_data["distance_km"],
                    elevation_gain=parsed_data["elevation_gain"],
                    elevation_loss=parsed_data["elevation_loss"],
                    max_elevation=parsed_data["max_elevation"],
                    min_elevation=parsed_data["min_elevation"],
                    start_lat=parsed_data["start_lat"],
                    start_lon=parsed_data["start_lon"],
                    end_lat=parsed_data["end_lat"],
                    end_lon=parsed_data["end_lon"],
                    total_points=parsed_data["total_points"],
                    simplified_points=parsed_data["simplified_points_count"],
                    has_elevation=parsed_data["has_elevation"],
                    has_timestamps=parsed_data["has_timestamps"],
                    processing_status="completed",
                    processed_at=datetime.now(UTC),
                )

                db.add(gpx_file)
                await db.commit()
                await db.refresh(gpx_file)

                # Save trackpoints
                from src.schemas.gpx import TrackPointResponse

                trackpoints = []
                for point_data in parsed_data["trackpoints"]:
                    track_point = TrackPoint(
                        gpx_file_id=gpx_file.gpx_file_id,
                        latitude=point_data["latitude"],
                        longitude=point_data["longitude"],
                        elevation=point_data["elevation"],
                        distance_km=point_data["distance_km"],
                        sequence=point_data["sequence"],
                        gradient=point_data["gradient"],
                    )
                    trackpoints.append(track_point)

                db.add_all(trackpoints)
                await db.commit()

                # Return full response (201 Created)
                from src.schemas.gpx import GPXUploadResponse

                response_data = GPXUploadResponse(
                    gpx_file_id=gpx_file.gpx_file_id,
                    trip_id=gpx_file.trip_id,
                    processing_status=gpx_file.processing_status,
                    distance_km=gpx_file.distance_km,
                    elevation_gain=gpx_file.elevation_gain,
                    elevation_loss=gpx_file.elevation_loss,
                    max_elevation=gpx_file.max_elevation,
                    min_elevation=gpx_file.min_elevation,
                    has_elevation=gpx_file.has_elevation,
                    has_timestamps=gpx_file.has_timestamps,
                    total_points=gpx_file.total_points,
                    simplified_points=gpx_file.simplified_points,
                    uploaded_at=gpx_file.uploaded_at,
                    processed_at=gpx_file.processed_at,
                )

                return GPXUploadSuccessResponse(success=True, data=response_data)

            except ValueError as e:
                # GPX parsing error (T035 - Spanish error messages)
                logger.warning(f"GPX parsing error for trip {trip_id}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "data": None,
                        "error": {
                            "code": "INVALID_GPX_FORMAT",
                            "message": str(e),
                        },
                    },
                )

        else:
            # Asynchronous processing (>1MB files) - SC-003
            # TODO: Implement async processing with BackgroundTasks
            # For now, return 501 Not Implemented
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_IMPLEMENTED",
                        "message": "Procesamiento asíncrono de archivos grandes aún no implementado",
                    },
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading GPX file to trip {trip_id}: {e}", exc_info=True)
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
    "/{trip_id}/gpx",
    response_model=GPXMetadataSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get GPX file metadata for trip",
    description="Retrieve metadata about the GPX file associated with a trip.",
)
async def get_gpx_metadata(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
) -> GPXMetadataSuccessResponse:
    """
    T031: Get GPX file metadata for trip.

    Public endpoint - No authentication required.

    Args:
        trip_id: Trip identifier
        db: Database session

    Returns:
        GPXMetadataSuccessResponse with GPX file metadata

    Raises:
        404: Trip not found or trip has no GPX file
    """
    try:
        # Get GPX file for trip
        result = await db.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "No se encontró archivo GPX para este viaje",
                    },
                },
            )

        # Convert to response schema
        from src.schemas.gpx import GPXFileMetadata

        metadata = GPXFileMetadata.model_validate(gpx_file)

        return GPXMetadataSuccessResponse(success=True, data=metadata)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving GPX metadata for trip {trip_id}: {e}", exc_info=True)
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
    "/{trip_id}/gpx",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete GPX file from trip",
    description="Remove GPX file and all associated trackpoints from a trip.",
)
async def delete_gpx_file(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    T033: Delete GPX file from trip (FR-036).

    Cascade deletes:
    - Trackpoints
    - Original GPX file from storage

    Args:
        trip_id: Trip identifier
        current_user: Authenticated user (must be trip owner)
        db: Database session

    Returns:
        204 No Content on success

    Raises:
        401: Unauthorized
        403: Forbidden (not trip owner)
        404: Trip not found or trip has no GPX file
    """
    try:
        # Verify trip exists
        trip_result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = trip_result.scalar_one_or_none()

        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Viaje no encontrado",
                    },
                },
            )

        # Check ownership
        if trip.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "Solo el propietario del viaje puede eliminar archivos GPX",
                    },
                },
            )

        # Get GPX file
        gpx_result = await db.execute(select(GPXFile).where(GPXFile.trip_id == trip_id))
        gpx_file = gpx_result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "No se encontró archivo GPX para este viaje",
                    },
                },
            )

        # Delete physical file from storage
        try:
            file_path = Path(gpx_file.file_url)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted GPX file from storage: {gpx_file.file_url}")
        except Exception as e:
            logger.warning(f"Failed to delete GPX file from storage: {e}")

        # Delete from database (cascade will delete trackpoints)
        await db.delete(gpx_file)
        await db.commit()

        logger.info(f"Deleted GPX file {gpx_file.gpx_file_id} from trip {trip_id}")

        # Return 204 No Content
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting GPX file from trip {trip_id}: {e}", exc_info=True)
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


# GPX status and track endpoints (separate router for cleaner paths)
gpx_router = APIRouter(prefix="/gpx", tags=["gpx"])


@gpx_router.get(
    "/{gpx_file_id}/status",
    response_model=GPXStatusSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get GPX processing status",
    description="Poll processing status of uploaded GPX file (for async uploads).",
)
async def get_gpx_status(
    gpx_file_id: str,
    db: AsyncSession = Depends(get_db),
) -> GPXStatusSuccessResponse:
    """
    T030: Get GPX processing status.

    Used for polling async uploads (files >1MB).

    Args:
        gpx_file_id: GPX file identifier
        db: Database session

    Returns:
        GPXStatusSuccessResponse with processing status

    Raises:
        404: GPX file not found
    """
    try:
        # Get GPX file
        result = await db.execute(select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id))
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Archivo GPX no encontrado",
                    },
                },
            )

        # Convert to response schema
        from src.schemas.gpx import GPXStatusResponse

        status_data = GPXStatusResponse(
            gpx_file_id=gpx_file.gpx_file_id,
            processing_status=gpx_file.processing_status,
            distance_km=gpx_file.distance_km if gpx_file.processing_status == "completed" else None,
            elevation_gain=gpx_file.elevation_gain
            if gpx_file.processing_status == "completed"
            else None,
            simplified_points=gpx_file.simplified_points
            if gpx_file.processing_status == "completed"
            else None,
            uploaded_at=gpx_file.uploaded_at,
            processed_at=gpx_file.processed_at,
            error_message=gpx_file.error_message,
        )

        return GPXStatusSuccessResponse(success=True, data=status_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving GPX status {gpx_file_id}: {e}", exc_info=True)
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


@gpx_router.get(
    "/{gpx_file_id}/track",
    response_model=TrackDataSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get simplified trackpoints for map rendering",
    description="Retrieve simplified GPS trackpoints for route visualization.",
)
async def get_track_data(
    gpx_file_id: str,
    db: AsyncSession = Depends(get_db),
) -> TrackDataSuccessResponse:
    """
    Get trackpoints for map rendering (FR-009, SC-007).

    Returns simplified trackpoints (Douglas-Peucker algorithm).

    Public endpoint - No authentication required.

    Args:
        gpx_file_id: GPX file identifier
        db: Database session

    Returns:
        TrackDataSuccessResponse with simplified trackpoints

    Raises:
        404: GPX file not found or not yet processed
    """
    try:
        # Get GPX file
        result = await db.execute(select(GPXFile).where(GPXFile.gpx_file_id == gpx_file_id))
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Archivo GPX no encontrado",
                    },
                },
            )

        # Check processing status
        if gpx_file.processing_status != "completed":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_PROCESSED",
                        "message": f"Archivo GPX aún no procesado. Estado: {gpx_file.processing_status}",
                    },
                },
            )

        # Get trackpoints
        trackpoints_result = await db.execute(
            select(TrackPoint)
            .where(TrackPoint.gpx_file_id == gpx_file_id)
            .order_by(TrackPoint.sequence)
        )
        trackpoints = trackpoints_result.scalars().all()

        # Convert to response schema
        from src.schemas.gpx import CoordinateResponse, TrackDataResponse, TrackPointResponse

        track_data = TrackDataResponse(
            gpx_file_id=gpx_file.gpx_file_id,
            trip_id=gpx_file.trip_id,
            distance_km=gpx_file.distance_km,
            elevation_gain=gpx_file.elevation_gain,
            simplified_points_count=len(trackpoints),
            has_elevation=gpx_file.has_elevation,
            start_point=CoordinateResponse(
                latitude=gpx_file.start_lat, longitude=gpx_file.start_lon
            ),
            end_point=CoordinateResponse(latitude=gpx_file.end_lat, longitude=gpx_file.end_lon),
            trackpoints=[TrackPointResponse.model_validate(tp) for tp in trackpoints],
        )

        return TrackDataSuccessResponse(success=True, data=track_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving track data {gpx_file_id}: {e}", exc_info=True)
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


@gpx_router.get(
    "/{gpx_file_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download original GPX file",
    description="Download the original unmodified GPX file.",
)
async def download_gpx_file(
    gpx_file_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    T032: Download original GPX file (FR-039, SC-028).

    Public endpoint - Anyone can download GPX files.

    Args:
        gpx_file_id: GPX file identifier
        db: Database session

    Returns:
        FileResponse with GPX file

    Raises:
        404: GPX file not found
    """
    try:
        # Get GPX file with associated trip (eager loading)
        result = await db.execute(
            select(GPXFile)
            .options(selectinload(GPXFile.trip))
            .where(GPXFile.gpx_file_id == gpx_file_id)
        )
        gpx_file = result.scalar_one_or_none()

        if not gpx_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Archivo GPX no encontrado",
                    },
                },
            )

        # Check if file exists
        file_path = Path(gpx_file.file_url)
        if not file_path.exists():
            logger.error(f"GPX file not found in storage: {gpx_file.file_url}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "FILE_NOT_FOUND",
                        "message": "Archivo GPX no encontrado en almacenamiento",
                    },
                },
            )

        # Generate filename from trip title (T048: Download as {trip_title}.gpx)
        # Sanitize trip title for filename (remove special characters)
        import re
        sanitized_title = re.sub(r'[^\w\s-]', '', gpx_file.trip.title)
        sanitized_title = re.sub(r'[-\s]+', '-', sanitized_title).strip('-')
        download_filename = f"{sanitized_title}.gpx"

        # Return file
        return FileResponse(
            path=str(file_path),
            media_type="application/gpx+xml",
            filename=download_filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading GPX file {gpx_file_id}: {e}", exc_info=True)
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
