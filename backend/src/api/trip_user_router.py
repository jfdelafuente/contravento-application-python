"""
Trip User & Tags API endpoints for Travel Diary feature.

Provides REST API for user-specific trip queries and tag management.

Functional Requirements: FR-025, FR-027
Feature 013: Trip visibility filtering
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_optional_current_user
from src.models.trip import TripStatus
from src.models.user import User
from src.services.trip_service import TripService

logger = logging.getLogger(__name__)

# No prefix - these are top-level endpoints
router = APIRouter(tags=["trips"])


@router.get(
    "/users/{username}/trips",
    response_model=dict[str, Any],
    summary="Get user trips with filters",
    description="FR-025: List user's trips with optional tag and status filtering",
)
async def get_user_trips(
    username: str,
    tag: str | None = Query(None, description="Filter by tag name (case-insensitive)"),
    status: TripStatus | None = Query(None, description="Filter by trip status"),
    visibility: str | None = Query(None, description="Filter by visibility (public or private)"),
    sort_by: str
    | None = Query(
        None,
        description="Sort order (date-desc, date-asc, distance-desc, distance-asc, popularity-desc)",
    ),
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
    - visibility: Filter by visibility (public or private)
    - sort_by: Sort order (default: date-desc)
        - date-desc: Most recent trips first (by trip start_date)
        - date-asc: Oldest trips first (by trip start_date)
        - distance-desc: Longest trips first
        - distance-asc: Shortest trips first
        - popularity-desc: Most popular trips first (not yet implemented, uses date-desc)
    - limit: Max trips to return (1-100, default 50)
    - offset: Pagination offset (default 0)

    **Visibility (Feature 013):**
    - Owner: sees all trips (drafts and published, any visibility)
    - Followers: see published trips with visibility='public' or 'followers'
    - Public: see only published trips with visibility='public'
    - visibility parameter: filters by is_private field (public=False, private=True)

    **Returns:**
    - List of trips with photos, tags, and locations
    - Ordered by sort_by parameter (default: start_date descending)
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

        # Convert visibility string to is_private boolean
        is_private = None
        if visibility:
            if visibility == "private":
                is_private = True
            elif visibility == "public":
                is_private = False

        service = TripService(db)
        trips = await service.get_user_trips(
            user_id=user.id,
            tag=tag,
            status=status,
            is_private=is_private,
            sort_by=sort_by,
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
                "is_private": trip.is_private,
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


@router.get(
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
