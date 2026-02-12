"""
Feed API endpoints (Feature 004 - T028).

Provides personalized trip feed for authenticated users.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.schemas.feed import FeedResponse
from src.services.feed_service import FeedService

router = APIRouter(prefix="", tags=["Feed"])


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    page: int = Query(default=1, ge=1, description="Page number (min 1)"),
    limit: int = Query(default=10, ge=1, le=50, description="Items per page (min 1, max 50)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FeedResponse:
    """
    Get personalized feed (FR-001).

    Returns personalized trip feed for authenticated user with hybrid algorithm:
    1. Trips from followed users (chronological DESC)
    2. Popular community trips backfill if needed

    **Algorithm** (from research.md):
    - Chronological from followed users
    - Backfill with popular community trips
    - Excludes own trips, draft trips

    **Success Criteria**: SC-001 (<1s p95)

    **Pagination**:
    - page: min 1, default 1
    - limit: min 1, max 50, default 10

    **Returns**:
    - trips: Array of FeedItem objects
    - total_count: Total trips available
    - page: Current page number
    - limit: Items per page
    - has_more: True if more pages exist

    **Authentication**: Required (JWT Bearer token)
    """
    result = await FeedService.get_personalized_feed(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
    )

    return FeedResponse(**result)
