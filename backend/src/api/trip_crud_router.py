"""
Trip CRUD API endpoints for Travel Diary feature.

Provides REST API for creating, reading, updating, deleting, and publishing trips,
plus public feed functionality.

Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-008, FR-016, FR-017, FR-018, FR-020
Feature 013: Public trips feed
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db, get_optional_current_user
from src.config import settings
from src.models.user import User
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
from src.services.trip_service import TripService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["trips"])


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
        trips, total = await service.get_public_trips(
            page=page, limit=limit, current_user_id=current_user.id if current_user else None
        )

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
            "data": trip_response.model_dump(by_alias=True),
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
            "data": trip_response.model_dump(by_alias=True),
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
