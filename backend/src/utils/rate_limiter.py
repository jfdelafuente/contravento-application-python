"""
Rate limiting decorator for preventing spam and abuse.

Implements time-based rate limiting for user actions like commenting and liking.
Tracks action counts per user within configurable time windows.
"""

from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Callable, TypeVar

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Type variable for generic function decoration
F = TypeVar("F", bound=Callable)


def rate_limit(
    model_class: type,
    max_actions: int,
    period_hours: int,
    user_id_field: str = "user_id",
    created_at_field: str = "created_at",
) -> Callable[[F], F]:
    """
    Decorator to rate limit user actions.

    Args:
        model_class: SQLAlchemy model to count actions (e.g., Comment, Like)
        max_actions: Maximum allowed actions in the time period
        period_hours: Time window in hours for counting actions
        user_id_field: Name of the user ID field in the model (default: "user_id")
        created_at_field: Name of the timestamp field in the model (default: "created_at")

    Returns:
        Decorated async function with rate limiting

    Raises:
        HTTPException: 429 Too Many Requests if rate limit exceeded

    Example:
        ```python
        @rate_limit(Comment, max_actions=10, period_hours=1)
        async def create_comment(db: AsyncSession, user_id: str, ...):
            # This function can only be called 10 times per hour per user
            pass
        ```

    Rate Limit Implementation (FR-044):
        - Comments: 10 per hour per user
        - Likes/Unlikes: 100 per hour per user
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract db and user_id from function arguments
            # Convention: db is first arg, user_id is in kwargs or second positional arg
            db: AsyncSession | None = None
            user_id: str | None = None

            # Find db session
            for arg in args:
                if isinstance(arg, AsyncSession):
                    db = arg
                    break

            # Find user_id
            if "user_id" in kwargs:
                user_id = kwargs["user_id"]
            elif len(args) >= 2 and isinstance(args[1], str):
                # Assume second arg is user_id if it's a string
                user_id = args[1]

            if not db or not user_id:
                raise ValueError(
                    "rate_limit decorator requires AsyncSession (db) and user_id in function arguments"
                )

            # Calculate cutoff time for rate limiting window
            cutoff_time = datetime.now(UTC) - timedelta(hours=period_hours)

            # Count actions by this user within the time window
            result = await db.execute(
                select(func.count())
                .select_from(model_class)
                .where(getattr(model_class, user_id_field) == user_id)
                .where(getattr(model_class, created_at_field) >= cutoff_time)
            )
            action_count = result.scalar() or 0

            # Check if rate limit exceeded
            if action_count >= max_actions:
                period_text = "hora" if period_hours == 1 else f"{period_hours} horas"
                raise HTTPException(
                    status_code=429,
                    detail={
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Has superado el límite de {max_actions} acciones por {period_text}. "
                        f"Intenta de nuevo más tarde.",
                        "retry_after_seconds": period_hours * 3600,
                    },
                )

            # Rate limit passed, execute the original function
            return await func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


# Specific rate limiters for common use cases


def rate_limit_comments(func: F) -> F:
    """
    Rate limit for comment creation: 10 comments per hour (FR-044).

    Example:
        ```python
        @rate_limit_comments
        async def create_comment(db: AsyncSession, user_id: str, ...):
            pass
        ```
    """
    # Import here to avoid circular dependency
    from src.models.comment import Comment

    return rate_limit(Comment, max_actions=10, period_hours=1)(func)


def rate_limit_likes(func: F) -> F:
    """
    Rate limit for like/unlike actions: 100 actions per hour (FR-045).

    Example:
        ```python
        @rate_limit_likes
        async def toggle_like(db: AsyncSession, user_id: str, ...):
            pass
        ```
    """
    # Import here to avoid circular dependency
    from src.models.like import Like

    return rate_limit(Like, max_actions=100, period_hours=1)(func)
