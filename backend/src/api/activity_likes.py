"""
Activity Likes API endpoints (Feature 018 - US2).

Endpoints for liking/unliking activity feed items.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.activity_like import ActivityLikeResponse, ActivityLikesListResponse
from src.services.activity_like_service import ActivityLikeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/activities", tags=["activity-likes"])


@router.post(
    "/{activity_id}/like",
    response_model=ActivityLikeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Like an activity",
    description="""
    Like an activity feed item (trip published, photo uploaded, achievement unlocked).

    **Idempotent**: If already liked, returns existing like with 201 status.

    **Notifications**: Creates a LIKE notification for activity author (unless self-like).

    **Authentication**: Required
    """,
)
async def like_activity(
    activity_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ActivityLikeResponse:
    """
    T050: Like an activity feed item.

    Args:
        activity_id: Activity to like (UUID)
        db: Database session
        current_user: Authenticated user

    Returns:
        ActivityLikeResponse with like details

    Raises:
        404: Activity not found
        500: Server error
    """
    try:
        service = ActivityLikeService(db)
        result = await service.like_activity(user_id=current_user.id, activity_id=activity_id)
        return result

    except ValueError as e:
        logger.warning(f"Activity not found for like: {activity_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Error liking activity {activity_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ERROR",
                "message": "Error al dar like a la actividad",
            },
        )


@router.delete(
    "/{activity_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlike an activity",
    description="""
    Remove a like from an activity feed item.

    **Idempotent**: Returns 204 even if activity wasn't liked.

    **Authentication**: Required
    """,
)
async def unlike_activity(
    activity_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    T051: Remove like from activity feed item.

    Args:
        activity_id: Activity to unlike (UUID)
        db: Database session
        current_user: Authenticated user

    Returns:
        204 No Content

    Raises:
        500: Server error
    """
    try:
        service = ActivityLikeService(db)
        await service.unlike_activity(user_id=current_user.id, activity_id=activity_id)
        return None

    except Exception as e:
        logger.error(f"Error unliking activity {activity_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ERROR",
                "message": "Error al quitar like de la actividad",
            },
        )


@router.get(
    "/{activity_id}/likes",
    response_model=ActivityLikesListResponse,
    summary="Get users who liked an activity",
    description="""
    Get paginated list of users who liked an activity.

    **Pagination**: Use page and limit query parameters.

    **Authentication**: Not required (public endpoint)
    """,
)
async def get_activity_likes(
    activity_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1, le=100)] = 1,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
) -> ActivityLikesListResponse:
    """
    Get users who liked an activity (paginated).

    Args:
        activity_id: Activity ID (UUID)
        db: Database session
        page: Page number (1-indexed, max 100)
        limit: Items per page (1-50, default 20)

    Returns:
        ActivityLikesListResponse with likes and pagination

    Raises:
        404: Activity not found
        400: Invalid pagination parameters
        500: Server error
    """
    try:
        service = ActivityLikeService(db)
        result = await service.get_activity_likes(activity_id=activity_id, page=page, limit=limit)
        return result

    except ValueError as e:
        error_msg = str(e)
        if "no encontrada" in error_msg.lower():
            logger.warning(f"Activity not found for likes: {activity_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NOT_FOUND", "message": error_msg},
            )
        else:
            logger.warning(f"Invalid pagination parameters: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "VALIDATION_ERROR", "message": error_msg},
            )
    except Exception as e:
        logger.error(f"Error getting likes for activity {activity_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "SERVER_ERROR",
                "message": "Error al obtener likes de la actividad",
            },
        )
