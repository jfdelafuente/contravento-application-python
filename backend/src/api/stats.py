"""
Statistics and Achievements API endpoints.

Handles user statistics and achievements retrieval.

Endpoints:
- GET /users/{username}/stats: Get user statistics (public)
- GET /users/{username}/achievements: Get user achievements (public)
- GET /achievements: List all available achievements (public)
"""

from typing import Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.services.stats_service import StatsService
from src.schemas.stats import (
    StatsResponse,
    UserAchievementResponse,
    AchievementDefinitionList,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["stats"])
achievements_router = APIRouter(tags=["achievements"])


def create_response(success: bool, data: Any = None, error: Dict = None, message: str = None) -> Dict:
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


@router.get("/{username}/stats")
async def get_user_stats(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    T166: Get user statistics (public endpoint).

    Returns aggregated user cycling statistics:
    - Total trips published
    - Total kilometers
    - Countries visited with names
    - Total photos
    - Achievements count
    - Last trip date

    **Functional Requirements**: FR-019

    Args:
        username: Username to get stats for
        db: Database session

    Returns:
        StatsResponse with user statistics

    Raises:
        HTTPException 404: If user not found
    """
    try:
        stats_service = StatsService(db)
        stats = await stats_service.get_user_stats(username)

        return create_response(
            success=True,
            data=stats.model_dump(),
        )

    except ValueError as e:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Error retrieving stats for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al obtener las estadísticas",
            },
        )


@router.get("/{username}/achievements")
async def get_user_achievements(
    username: str,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    T167: Get user's earned achievements (public endpoint).

    Returns all achievements earned by the user, ordered by most recent first.

    **Functional Requirements**: FR-020, FR-021, FR-022

    Args:
        username: Username to get achievements for
        db: Database session

    Returns:
        UserAchievementResponse with list of earned achievements

    Raises:
        HTTPException 404: If user not found
    """
    try:
        stats_service = StatsService(db)
        achievements = await stats_service.get_user_achievements(username)

        return create_response(
            success=True,
            data=achievements.model_dump(),
        )

    except ValueError as e:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Error retrieving achievements for {username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al obtener los logros",
            },
        )


@achievements_router.get("/achievements")
async def list_all_achievements(
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    T168: List all available achievements (public endpoint).

    Returns all achievement definitions in the system.
    Useful for showing users what goals they can achieve.

    **Functional Requirements**: FR-024

    Args:
        db: Database session

    Returns:
        AchievementDefinitionList with all available achievements
    """
    try:
        stats_service = StatsService(db)
        achievements = await stats_service.list_all_achievements()

        return create_response(
            success=True,
            data=achievements.model_dump(),
        )

    except Exception as e:
        logger.error(f"Error listing achievements: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al listar los logros",
            },
        )
