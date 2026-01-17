"""
Likes API endpoints (Feature 004 - US2: Likes/Me Gusta).

Endpoints:
- POST /trips/{trip_id}/like: Like a trip
- DELETE /trips/{trip_id}/like: Unlike a trip
- GET /trips/{trip_id}/likes: Get users who liked a trip (paginated)

Authentication: All endpoints require JWT authentication
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.like import LikeResponse, LikesListResponse, UnlikeResponse
from src.services.like_service import LikeService

router = APIRouter(prefix="/trips", tags=["Likes"])


@router.post(
    "/{trip_id}/like",
    response_model=LikeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def like_trip(
    trip_id: str = Path(..., description="Trip ID to like"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LikeResponse:
    """
    Like a trip (FR-009) - T055, T046.

    **Validations**:
    - Trip must exist and be published
    - User cannot like own trip (FR-011)
    - User cannot like same trip twice (FR-010)

    **Returns**:
    - 201: Like created successfully
    - 400: Validation error (duplicate like, self-like, draft trip)
    - 401: Unauthorized (no auth token)
    - 404: Trip not found

    **Performance**: SC-006 (<200ms p95)
    """
    try:
        result = await LikeService.like_trip(
            db=db, user_id=current_user.id, trip_id=trip_id
        )
        return result
    except ValueError as e:
        error_message = str(e)

        # Determine appropriate error code
        if "no encontrado" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )


@router.delete("/{trip_id}/like", response_model=UnlikeResponse)
async def unlike_trip(
    trip_id: str = Path(..., description="Trip ID to unlike"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UnlikeResponse:
    """
    Unlike a trip (FR-009) - T056, T047.

    Removes like from trip. Requires user to have previously liked the trip.

    **Returns**:
    - 200: Unlike successful
    - 400: Like not found (user hasn't liked this trip)
    - 401: Unauthorized

    **Performance**: SC-007 (<100ms p95)
    """
    try:
        result = await LikeService.unlike_trip(
            db=db, user_id=current_user.id, trip_id=trip_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{trip_id}/likes", response_model=LikesListResponse)
async def get_trip_likes(
    trip_id: str = Path(..., description="Trip ID"),
    page: int = Query(default=1, ge=1, description="Page number (min 1)"),
    limit: int = Query(
        default=20, ge=1, le=50, description="Items per page (min 1, max 50)"
    ),
    db: AsyncSession = Depends(get_db),
) -> LikesListResponse:
    """
    Get users who liked a trip (FR-014) - T057, T048.

    Returns paginated list of users who liked the trip with timestamps.

    **Public endpoint** (no authentication required).

    **Pagination**:
    - page: min 1, default 1
    - limit: min 1, max 50, default 20

    **Returns**:
    - 200: List of likes with user details
    - 404: Trip not found

    **Performance**: SC-008 (<300ms p95 with 50 likes)
    """
    result = await LikeService.get_trip_likes(
        db=db, trip_id=trip_id, page=page, limit=limit
    )

    return result
