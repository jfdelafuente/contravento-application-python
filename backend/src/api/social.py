"""
Social API endpoints.

Endpoints for follow/unfollow operations and social lists.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.services.social_service import SocialService
from src.schemas.social import (
    FollowResponse,
    FollowersListResponse,
    FollowingListResponse,
    FollowStatusResponse,
)
from src.schemas.api_response import ApiResponse, ErrorResponse, ErrorDetail
from src.api.deps import get_current_user
from src.models.user import User


router = APIRouter(prefix="/users", tags=["social"])


@router.post(
    "/{username}/follow",
    status_code=status.HTTP_200_OK,
    summary="T211: Follow a user",
    description="Follow a user. Requires authentication. Cannot follow yourself or follow someone you already follow.",
)
async def follow_user(
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Follow a user.

    Args:
        username: Username to follow
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        ApiResponse with FollowResponse data

    Raises:
        400: Self-follow or already following
        404: User not found
        401: Not authenticated
    """
    social_service = SocialService(db)

    try:
        result = await social_service.follow_user(
            follower_username=current_user.username,
            following_username=username,
        )

        return ApiResponse(
            success=True,
            message=result.message,
            data=result,
        )

    except ValueError as e:
        error_msg = str(e)

        # Determine error code
        if "No puedes seguirte" in error_msg:
            error_code = "CANNOT_FOLLOW_SELF"
            status_code = status.HTTP_400_BAD_REQUEST
        elif "Ya sigues" in error_msg:
            error_code = "ALREADY_FOLLOWING"
            status_code = status.HTTP_400_BAD_REQUEST
        elif "no existe" in error_msg:
            error_code = "USER_NOT_FOUND"
            status_code = status.HTTP_404_NOT_FOUND
        else:
            error_code = "FOLLOW_ERROR"
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=ErrorResponse(
                success=False,
                error=ErrorDetail(
                    code=error_code,
                    message=error_msg,
                ),
            ).model_dump(),
        )


@router.delete(
    "/{username}/follow",
    status_code=status.HTTP_200_OK,
    summary="T212: Unfollow a user",
    description="Unfollow a user. Requires authentication. Must be currently following the user.",
)
async def unfollow_user(
    username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Unfollow a user.

    Args:
        username: Username to unfollow
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        ApiResponse with FollowResponse data

    Raises:
        400: Not following user
        404: User not found
        401: Not authenticated
    """
    social_service = SocialService(db)

    try:
        result = await social_service.unfollow_user(
            follower_username=current_user.username,
            following_username=username,
        )

        return ApiResponse(
            success=True,
            message=result.message,
            data=result,
        )

    except ValueError as e:
        error_msg = str(e)

        # Determine error code
        if "No sigues" in error_msg:
            error_code = "NOT_FOLLOWING"
            status_code = status.HTTP_400_BAD_REQUEST
        elif "no existe" in error_msg:
            error_code = "USER_NOT_FOUND"
            status_code = status.HTTP_404_NOT_FOUND
        else:
            error_code = "UNFOLLOW_ERROR"
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(
            status_code=status_code,
            detail=ErrorResponse(
                success=False,
                error=ErrorDetail(
                    code=error_code,
                    message=error_msg,
                ),
            ).model_dump(),
        )


@router.get(
    "/{username}/followers",
    status_code=status.HTTP_200_OK,
    summary="T213: Get followers list",
    description="Get paginated list of users who follow the target user. Public endpoint.",
)
async def get_followers(
    username: str,
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    limit: Annotated[int, Query(ge=1, le=50, description="Results per page (max 50)")] = 50,
    db: AsyncSession = Depends(get_db),
):
    """
    Get followers list.

    Args:
        username: Username to get followers for
        page: Page number (default 1)
        limit: Results per page (default 50, max 50)
        db: Database session

    Returns:
        ApiResponse with FollowersListResponse data

    Raises:
        404: User not found
    """
    social_service = SocialService(db)

    try:
        result = await social_service.get_followers(
            username=username,
            page=page,
            limit=limit,
        )

        return ApiResponse(
            success=True,
            message="Seguidores obtenidos correctamente",
            data=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                success=False,
                error=ErrorDetail(
                    code="USER_NOT_FOUND",
                    message=str(e),
                ),
            ).model_dump(),
        )


@router.get(
    "/{username}/following",
    status_code=status.HTTP_200_OK,
    summary="T214: Get following list",
    description="Get paginated list of users that the target user follows. Public endpoint.",
)
async def get_following(
    username: str,
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    limit: Annotated[int, Query(ge=1, le=50, description="Results per page (max 50)")] = 50,
    db: AsyncSession = Depends(get_db),
):
    """
    Get following list.

    Args:
        username: Username to get following list for
        page: Page number (default 1)
        limit: Results per page (default 50, max 50)
        db: Database session

    Returns:
        ApiResponse with FollowingListResponse data

    Raises:
        404: User not found
    """
    social_service = SocialService(db)

    try:
        result = await social_service.get_following(
            username=username,
            page=page,
            limit=limit,
        )

        return ApiResponse(
            success=True,
            message="Seguidos obtenidos correctamente",
            data=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                success=False,
                error=ErrorDetail(
                    code="USER_NOT_FOUND",
                    message=str(e),
                ),
            ).model_dump(),
        )


@router.get(
    "/{target_username}/follow-status",
    status_code=status.HTTP_200_OK,
    summary="T215: Get follow status",
    description="Check if current user follows target user. Requires authentication.",
)
async def get_follow_status(
    target_username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Get follow status between current user and target user.

    Args:
        target_username: Username to check follow status for
        current_user: Authenticated user (from JWT)
        db: Database session

    Returns:
        ApiResponse with FollowStatusResponse data

    Raises:
        404: User not found
        401: Not authenticated
    """
    social_service = SocialService(db)

    try:
        result = await social_service.get_follow_status(
            follower_username=current_user.username,
            following_username=target_username,
        )

        return ApiResponse(
            success=True,
            message="Estado de seguimiento obtenido",
            data=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                success=False,
                error=ErrorDetail(
                    code="USER_NOT_FOUND",
                    message=str(e),
                ),
            ).model_dump(),
        )
