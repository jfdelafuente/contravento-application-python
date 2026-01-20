"""
Comments API endpoints (Feature 004 - US3: Comentarios).

Endpoints:
- POST /trips/{trip_id}/comments: Create a comment on a trip
- GET /trips/{trip_id}/comments: Get all comments for a trip (paginated)
- PUT /comments/{comment_id}: Update a comment
- DELETE /comments/{comment_id}: Delete a comment

Authentication:
- POST, PUT, DELETE require JWT authentication (FR-025)
- GET allows unauthenticated access (public reading, FR-025)
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.comment import Comment
from src.models.user import User
from src.schemas.comment import (
    CommentCreateInput,
    CommentResponse,
    CommentsListResponse,
    CommentUpdateInput,
)
from src.services.comment_service import CommentService

router = APIRouter(tags=["Comments"])


@router.post(
    "/trips/{trip_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    trip_id: str = Path(..., description="Trip ID to comment on"),
    comment_input: CommentCreateInput = ...,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    try:
        comment = await CommentService.create_comment(
            db=db,
            trip_id=trip_id,
            user_id=current_user.id,
            content=comment_input.content,
        )
        return CommentResponse.model_validate(comment)
    except ValueError as e:
        error_message = str(e)
        if "límite" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message,
            )
        if "no existe" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )


@router.get(
    "/trips/{trip_id}/comments",
    response_model=CommentsListResponse,
)
async def get_trip_comments(
    trip_id: str = Path(..., description="Trip ID to get comments for"),
    limit: int = Query(50, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> CommentsListResponse:
    result = await CommentService.get_trip_comments(
        db=db,
        trip_id=trip_id,
        limit=limit,
        offset=offset,
    )

    comments_with_authors = []
    for comment in result["items"]:
        comment_dict = {
            "id": comment.id,
            "user_id": comment.user_id,
            "trip_id": comment.trip_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "is_edited": comment.is_edited,
        }

        if comment.user:
            author_data = {
                "user_id": comment.user.id,
                "username": comment.user.username,
                "full_name": comment.user.profile.full_name if comment.user.profile else None,
                "profile_photo_url": comment.user.profile.profile_photo_url
                if comment.user.profile
                else None,
            }
            comment_dict["author"] = author_data

        comments_with_authors.append(CommentResponse(**comment_dict))

    return CommentsListResponse(
        items=comments_with_authors,
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
    )


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: str = Path(..., description="Comment ID to update"),
    comment_input: CommentUpdateInput = ...,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CommentResponse:
    try:
        comment = await CommentService.update_comment(
            db=db,
            comment_id=comment_id,
            user_id=current_user.id,
            content=comment_input.content,
        )
        return CommentResponse.model_validate(comment)
    except ValueError as e:
        error_message = str(e)
        if "solo puedes editar" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message,
            )
        if "no existe" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: str = Path(..., description="Comment ID to delete"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        comment = result.scalar_one_or_none()

        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El comentario no existe",
            )

        await CommentService.delete_comment(
            db=db,
            comment_id=comment_id,
            user_id=current_user.id,
            trip_id=comment.trip_id,
        )
    except ValueError as e:
        error_message = str(e)
        if "no tienes permiso" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message,
            )
        if "no existe" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )
