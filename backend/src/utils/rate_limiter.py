"""
Rate Limiter utility for comment creation (Feature 004 - US3: Comentarios).

Implements rate limiting decorator to prevent comment spam.
Task: T089
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment

# Rate limit constants
COMMENT_RATE_LIMIT = 10  # Maximum comments per hour
RATE_LIMIT_WINDOW_HOURS = 1  # Time window in hours


async def check_comment_rate_limit(
    db: AsyncSession,
    user_id: str,
    limit: int = COMMENT_RATE_LIMIT,
    hours: int = RATE_LIMIT_WINDOW_HOURS,
) -> tuple[bool, int]:
    """
    Check if user has exceeded comment rate limit (T089).

    Args:
        db: Database session
        user_id: ID of user to check
        limit: Maximum comments allowed in time window (default: 10)
        hours: Time window in hours (default: 1)

    Returns:
        Tuple of (is_allowed, comment_count):
        - is_allowed: True if user can post another comment
        - comment_count: Number of comments in time window

    Raises:
        ValueError: If rate limit is exceeded (429 error)
    """
    # Calculate time window (last N hours)
    time_threshold = datetime.now(UTC) - timedelta(hours=hours)

    # Count user's comments in time window
    result = await db.execute(
        select(func.count(Comment.id))
        .where(Comment.user_id == user_id)
        .where(Comment.created_at >= time_threshold)
    )
    comment_count = result.scalar_one()

    # Check if limit exceeded
    if comment_count >= limit:
        raise ValueError(
            f"Has alcanzado el límite de {limit} comentarios por hora. "
            f"Por favor, espera un momento antes de comentar de nuevo."
        )

    return True, comment_count


def rate_limit(limit: int = COMMENT_RATE_LIMIT, hours: int = RATE_LIMIT_WINDOW_HOURS) -> Callable:
    """
    Decorator to enforce rate limiting on comment creation (T089).

    Usage:
        @rate_limit(limit=10, hours=1)
        async def create_comment(db, user_id, content):
            ...

    Args:
        limit: Maximum comments allowed in time window
        hours: Time window in hours

    Returns:
        Decorator function

    Raises:
        ValueError: If rate limit is exceeded
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract db and user_id from function arguments
            # Assumes function signature: func(db: AsyncSession, *, user_id: str, ...)
            db = args[0] if args else kwargs.get("db")
            user_id = kwargs.get("user_id")

            if not db or not user_id:
                raise ValueError("rate_limit decorator requires db and user_id arguments")

            # Check rate limit before calling function
            await check_comment_rate_limit(db, user_id, limit, hours)

            # Call original function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
