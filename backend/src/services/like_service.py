"""
LikeService for managing trip likes (Feature 004 - US2: Likes/Me Gusta).

Provides business logic for:
- FR-009: Like/unlike trips
- FR-010: Prevent duplicate likes (unique constraint)
- FR-011: Prevent self-likes
- FR-012: Fast like count queries (indexed)
- FR-013: Track like timestamps
- FR-014: List users who liked (with pagination)

Performance:
- SC-006: like_trip() <200ms p95
- SC-007: unlike_trip() <100ms p95
- SC-008: get_trip_likes() <300ms p95 with 50 likes
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.like import Like
from src.models.trip import Trip
from src.models.user import User


class LikeService:
    """Service for managing trip likes."""

    @staticmethod
    async def like_trip(db: AsyncSession, user_id: str, trip_id: str) -> dict[str, Any]:
        """
        Like a trip (FR-009).

        Creates a new Like record with validations:
        - Trip must exist and be published
        - User cannot like own trip (FR-011)
        - User cannot like same trip twice (FR-010)

        Args:
            db: Database session
            user_id: ID of user liking the trip
            trip_id: ID of trip to like

        Returns:
            Dict with like details:
            {
                "like_id": str,
                "user_id": str,
                "trip_id": str,
                "created_at": str (ISO 8601)
            }

        Raises:
            ValueError: If trip not found, trip is draft, self-like, or duplicate like

        Performance: SC-006 (<200ms p95)
        """
        # Verify trip exists and is published
        stmt = select(Trip).where(Trip.trip_id == trip_id)
        result = await db.execute(stmt)
        trip = result.scalar_one_or_none()

        if not trip:
            raise ValueError("Viaje no encontrado")

        if trip.status != "published":
            raise ValueError("Solo puedes dar like a viajes publicados")

        # Prevent self-like (FR-011)
        if trip.user_id == user_id:
            raise ValueError("No puedes dar like a tu propio viaje")

        # Check for existing like (FR-010)
        stmt = select(Like).where(Like.user_id == user_id, Like.trip_id == trip_id)
        existing_like = (await db.execute(stmt)).scalar_one_or_none()

        if existing_like:
            raise ValueError("Ya has dado like a este viaje")

        # Create like
        like = Like(
            id=str(uuid4()),
            user_id=user_id,
            trip_id=trip_id,
            created_at=datetime.now(UTC),
        )

        db.add(like)
        await db.commit()
        await db.refresh(like)

        return {
            "like_id": like.id,
            "user_id": like.user_id,
            "trip_id": like.trip_id,
            "created_at": like.created_at.isoformat() + "Z",
        }

    @staticmethod
    async def unlike_trip(db: AsyncSession, user_id: str, trip_id: str) -> dict[str, Any]:
        """
        Unlike a trip (FR-009).

        Removes an existing Like record.

        Args:
            db: Database session
            user_id: ID of user unliking the trip
            trip_id: ID of trip to unlike

        Returns:
            Dict with success message:
            {
                "success": bool,
                "message": str
            }

        Raises:
            ValueError: If like doesn't exist

        Performance: SC-007 (<100ms p95)
        """
        # Find existing like
        stmt = select(Like).where(Like.user_id == user_id, Like.trip_id == trip_id)
        like = (await db.execute(stmt)).scalar_one_or_none()

        if not like:
            raise ValueError("No has dado like a este viaje")

        # Delete like
        await db.delete(like)
        await db.commit()

        return {"success": True, "message": "Like eliminado correctamente"}

    @staticmethod
    async def get_trip_likes(
        db: AsyncSession, trip_id: str, page: int = 1, limit: int = 20
    ) -> dict[str, Any]:
        """
        Get users who liked a trip (FR-014).

        Returns paginated list of users who liked the trip with their details.

        Args:
            db: Database session
            trip_id: ID of trip
            page: Page number (min 1)
            limit: Items per page (max 50)

        Returns:
            Dict with pagination:
            {
                "likes": [
                    {
                        "user": {
                            "username": str,
                            "profile_photo_url": str | None
                        },
                        "created_at": str (ISO 8601)
                    }
                ],
                "total_count": int,
                "page": int,
                "limit": int,
                "has_more": bool
            }

        Performance: SC-008 (<300ms p95 with 50 likes)
        """
        # Validate pagination
        page = max(1, page)
        limit = min(50, max(1, limit))
        offset = (page - 1) * limit

        # Count total likes
        count_stmt = select(func.count(Like.id)).where(Like.trip_id == trip_id)
        total_count = (await db.execute(count_stmt)).scalar()

        # Get paginated likes with user details (eager load to prevent N+1)
        stmt = (
            select(Like)
            .where(Like.trip_id == trip_id)
            .options(selectinload(Like.user).selectinload(User.profile))
            .order_by(Like.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(stmt)
        likes = result.scalars().all()

        # Format response
        likes_data = [
            {
                "user": {
                    "username": like.user.username,
                    "profile_photo_url": (
                        like.user.profile.profile_photo_url if like.user.profile else None
                    ),
                },
                "created_at": like.created_at.isoformat() + "Z",
            }
            for like in likes
        ]

        return {
            "likes": likes_data,
            "total_count": total_count or 0,
            "page": page,
            "limit": limit,
            "has_more": offset + len(likes) < (total_count or 0),
        }

    @staticmethod
    async def has_user_liked_trip(db: AsyncSession, user_id: str, trip_id: str) -> bool:
        """
        Check if a user has liked a trip.

        Utility method for UI state (e.g., showing filled vs outline heart icon).

        Args:
            db: Database session
            user_id: ID of user
            trip_id: ID of trip

        Returns:
            True if user has liked the trip, False otherwise
        """
        stmt = select(Like).where(Like.user_id == user_id, Like.trip_id == trip_id)
        like = (await db.execute(stmt)).scalar_one_or_none()
        return like is not None

    @staticmethod
    async def get_trip_like_count(db: AsyncSession, trip_id: str) -> int:
        """
        Get total likes count for a trip (FR-012).

        Fast indexed query for displaying like counters.

        Args:
            db: Database session
            trip_id: ID of trip

        Returns:
            Total number of likes

        Performance: <50ms p95 (indexed query)
        """
        stmt = select(func.count(Like.id)).where(Like.trip_id == trip_id)
        count = (await db.execute(stmt)).scalar()
        return count or 0
