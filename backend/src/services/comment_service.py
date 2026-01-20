"""
CommentService for managing trip comments (Feature 004 - US3: Comentarios).

Business logic for:
- Creating comments with rate limiting (T091)
- Updating comments with is_edited marker (T092)
- Deleting comments with moderation support (T093)
- Retrieving paginated comments (T094)

All methods follow TDD - tests written first in test_comment_service.py
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.comment import Comment
from src.models.trip import Trip
from src.models.user import User
from src.utils.html_sanitizer import sanitize_html
from src.utils.rate_limiter import check_comment_rate_limit


class CommentService:
    @staticmethod
    async def create_comment(
        db: AsyncSession,
        *,
        trip_id: str,
        user_id: str,
        content: str,
    ) -> Comment:
        # Validate content
        content_trimmed = content.strip()
        if not content_trimmed or len(content_trimmed) < 1:
            raise ValueError("El contenido del comentario debe tener entre 1 y 500 caracteres")
        if len(content_trimmed) > 500:
            raise ValueError("El contenido del comentario debe tener entre 1 y 500 caracteres")

        # Check rate limit
        await check_comment_rate_limit(db, user_id, limit=10, hours=1)

        # Verify trip exists and is published
        result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = result.scalar_one_or_none()
        if not trip:
            raise ValueError("El viaje no existe")
        if trip.status != "published":
            raise ValueError("El comentario solo puede comentarse en viajes publicados")

        # Sanitize HTML
        sanitized_content = sanitize_html(content_trimmed)

        # Create comment
        comment = Comment(
            id=str(uuid4()),
            user_id=user_id,
            trip_id=trip_id,
            content=sanitized_content,
            created_at=datetime.now(UTC),
            is_edited=False,
        )

        db.add(comment)
        await db.commit()
        await db.refresh(comment)

        return comment

    @staticmethod
    async def update_comment(
        db: AsyncSession,
        *,
        comment_id: str,
        user_id: str,
        content: str,
    ) -> Comment:
        # Validate content
        content_trimmed = content.strip()
        if not content_trimmed or len(content_trimmed) < 1:
            raise ValueError("El contenido del comentario debe tener entre 1 y 500 caracteres")
        if len(content_trimmed) > 500:
            raise ValueError("El contenido del comentario debe tener entre 1 y 500 caracteres")

        # Fetch comment
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        comment = result.scalar_one_or_none()
        if not comment:
            raise ValueError("El comentario no existe")

        # Check authorization
        if comment.user_id != user_id:
            raise ValueError("Solo puedes editar tus propios comentarios")

        # Sanitize HTML
        sanitized_content = sanitize_html(content_trimmed)

        # Update comment
        comment.content = sanitized_content
        comment.is_edited = True
        comment.updated_at = datetime.now(UTC)

        await db.commit()
        await db.refresh(comment)

        return comment

    @staticmethod
    async def delete_comment(
        db: AsyncSession,
        *,
        comment_id: str,
        user_id: str,
        trip_id: str | None = None,
    ) -> None:
        # Fetch comment with trip relationship
        result = await db.execute(
            select(Comment).options(selectinload(Comment.trip)).where(Comment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            raise ValueError("El comentario no existe")

        # Check authorization
        is_author = comment.user_id == user_id
        is_trip_owner = trip_id and comment.trip.user_id == user_id

        if not (is_author or is_trip_owner):
            raise ValueError("No tienes permiso para eliminar este comentario")

        # Delete comment
        await db.delete(comment)
        await db.commit()

    @staticmethod
    async def get_trip_comments(
        db: AsyncSession,
        *,
        trip_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        # Validate pagination
        if limit > 50:
            limit = 50
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0

        # Get total count
        count_result = await db.execute(
            select(func.count(Comment.id)).where(Comment.trip_id == trip_id)
        )
        total = count_result.scalar_one()

        # Get comments (oldest first)
        result = await db.execute(
            select(Comment)
            .options(selectinload(Comment.user).selectinload(User.profile))
            .where(Comment.trip_id == trip_id)
            .order_by(Comment.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        comments = result.scalars().all()

        return {
            "items": list(comments),
            "total": total,
            "limit": limit,
            "offset": offset,
        }
