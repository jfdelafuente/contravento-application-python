"""
Activity Feed API endpoints (Feature 018 - US1).

Provides chronological activity stream from followed users.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.feed import ActivityFeedResponseSchema
from src.services.feed_service import FeedService

router = APIRouter(prefix="/activity-feed", tags=["Activity Feed"])


@router.get("", response_model=ActivityFeedResponseSchema)
async def get_activity_feed(
    limit: int = Query(default=20, ge=1, le=50, description="Items per page (min 1, max 50)"),
    cursor: str | None = Query(default=None, description="Cursor for pagination (null for first page)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ActivityFeedResponseSchema:
    """
    Get activity feed from followed users (Feature 018 - US1, T027, T028).

    Returns chronological activity stream with cursor-based pagination.

    **Activity Types**:
    - TRIP_PUBLISHED: User published a new trip
    - PHOTO_UPLOADED: User uploaded photos to a trip
    - ACHIEVEMENT_UNLOCKED: User earned an achievement badge

    **Pagination**:
    - limit: min 1, max 50, default 20
    - cursor: Opaque cursor string from previous response (null for first page)

    **Returns**:
    - activities: Array of ActivityFeedItemSchema objects
    - next_cursor: Cursor for next page (null if last page)
    - has_next: True if more activities exist

    **Performance**: <2s for 20 activities (SC-001)

    **Authentication**: Required (JWT Bearer token)
    """
    result = await FeedService.get_user_feed(
        db=db,
        user_id=current_user.user_id,
        limit=limit,
        cursor=cursor,
    )

    return ActivityFeedResponseSchema(**result)
