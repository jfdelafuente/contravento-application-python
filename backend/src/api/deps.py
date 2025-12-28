"""
Dependency injection functions for FastAPI routes.

Provides reusable dependencies for database sessions, authentication, etc.
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.utils.security import decode_token


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Dependency to provide database session.

    Yields async database session and ensures proper cleanup.

    Example:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        AsyncSession: Database session for the request
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency to get current authenticated user from JWT token.

    Validates JWT token and returns User model instance.

    Args:
        credentials: HTTP bearer credentials from request header
        db: Database session

    Returns:
        User model instance

    Raises:
        HTTPException: If token is invalid or user not found

    Example:
        @router.get("/protected")
        async def protected_route(
            current_user: User = Depends(get_current_user)
        ):
            # current_user is User model instance
            pass
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "success": False,
            "data": None,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Token de autenticación inválido o expirado",
            },
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        token = credentials.credentials
        payload = decode_token(token)

        # Extract user ID from token subject
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Verify token type (access token)
        token_type: str = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "INVALID_TOKEN_TYPE",
                        "message": "Token inválido. Use un token de acceso.",
                    },
                },
            )

        # Load user from database
        from src.models.user import User
        from sqlalchemy import select

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            raise credentials_exception

        # Return User model instance
        return user

    except Exception:
        raise credentials_exception


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency to optionally get current user.

    Returns User model if authenticated, None if not.
    Useful for endpoints that work differently for authenticated vs anonymous users.

    Args:
        credentials: Optional HTTP bearer credentials
        db: Database session

    Returns:
        User model instance if authenticated, None otherwise

    Example:
        @router.get("/public")
        async def public_route(
            current_user: Optional[User] = Depends(get_optional_current_user)
        ):
            if current_user:
                # Show personalized content
                pass
            else:
                # Show public content
                pass
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
