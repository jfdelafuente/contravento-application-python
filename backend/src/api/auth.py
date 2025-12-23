"""
Authentication API endpoints.

Handles user registration, email verification, login, logout, and password reset.

Endpoints:
- POST /auth/register: Register new user
- POST /auth/verify-email: Verify email with token
- POST /auth/resend-verification: Resend verification email
- POST /auth/login: Login with credentials
- POST /auth/refresh: Refresh access token
- POST /auth/logout: Logout and invalidate refresh token
- POST /auth/password-reset/request: Request password reset
- POST /auth/password-reset/confirm: Confirm password reset
- GET /auth/me: Get current user info
"""

from typing import Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_current_user
from src.services.auth_service import AuthService
from src.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from src.schemas.user import UserResponse
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Register a new user.

    Creates user account and sends verification email.

    **Functional Requirements**: FR-001, FR-002

    Args:
        data: Registration request data
        db: Database session

    Returns:
        User data with verification status

    Raises:
        HTTPException 400: Username or email already exists
        HTTPException 400: Validation errors
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.register(data)

        return create_response(
            success=True,
            data=user.model_dump(),
            message="Usuario registrado. Revisa tu email para verificar tu cuenta."
        )

    except ValueError as e:
        # Duplicate username/email or validation error
        error_msg = str(e)

        if "nombre de usuario" in error_msg.lower():
            error_code = "USERNAME_TAKEN"
            field = "username"
        elif "email" in error_msg.lower():
            error_code = "EMAIL_TAKEN"
            field = "email"
        else:
            error_code = "VALIDATION_ERROR"
            field = None

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                success=False,
                error={"code": error_code, "message": error_msg, "field": field}
            )
        )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Verify user email with token.

    **Functional Requirements**: FR-002

    Args:
        token: Verification token from email
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: Invalid or expired token
    """
    try:
        auth_service = AuthService(db)
        await auth_service.verify_email(token)

        return create_response(
            success=True,
            message="Tu cuenta ha sido verificada correctamente"
        )

    except ValueError as e:
        error_msg = str(e)

        if "expirado" in error_msg.lower():
            error_code = "TOKEN_EXPIRED"
        else:
            error_code = "INVALID_TOKEN"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                success=False,
                error={"code": error_code, "message": error_msg}
            )
        )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    email: str,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Resend verification email.

    Rate limited to 3 requests per hour.

    **Functional Requirements**: FR-002

    Args:
        email: Email address
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 429: Rate limit exceeded
    """
    try:
        auth_service = AuthService(db)
        await auth_service.resend_verification(email)

        return create_response(
            success=True,
            message="Email de verificación enviado"
        )

    except ValueError as e:
        error_msg = str(e)

        if "demasiados" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=create_response(
                    success=False,
                    error={"code": "RATE_LIMIT_EXCEEDED", "message": error_msg}
                )
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                success=False,
                error={"code": "VALIDATION_ERROR", "message": error_msg}
            )
        )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Login with username/email and password.

    Returns access token (15 min) and refresh token (30 days).

    **Functional Requirements**: FR-003, FR-004, FR-009, FR-010

    Args:
        data: Login credentials
        db: Database session

    Returns:
        Tokens and user data

    Raises:
        HTTPException 400: Email not verified
        HTTPException 401: Invalid credentials
        HTTPException 429: Account locked (too many failed attempts)
    """
    try:
        auth_service = AuthService(db)
        response = await auth_service.login(data)

        return create_response(
            success=True,
            data=response.model_dump()
        )

    except ValueError as e:
        error_msg = str(e)

        if "verificar tu email" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_response(
                    success=False,
                    error={"code": "EMAIL_NOT_VERIFIED", "message": error_msg}
                )
            )

        elif "cuenta bloqueada" in error_msg.lower() or "demasiados intentos" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=create_response(
                    success=False,
                    error={"code": "ACCOUNT_LOCKED", "message": error_msg}
                )
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=create_response(
                    success=False,
                    error={"code": "INVALID_CREDENTIALS", "message": error_msg}
                )
            )


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Refresh access token using refresh token.

    Invalidates old refresh token and returns new token pair.

    **Functional Requirements**: FR-010

    Args:
        refresh_token: Refresh token from login
        db: Database session

    Returns:
        New token pair

    Raises:
        HTTPException 401: Invalid or expired refresh token
    """
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_token(refresh_token)

        return create_response(
            success=True,
            data=tokens.model_dump()
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_response(
                success=False,
                error={"code": "INVALID_REFRESH_TOKEN", "message": str(e)}
            )
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_token: str,
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Logout and invalidate refresh token.

    Access token remains valid until expiration (15 min).

    **Functional Requirements**: FR-005

    Args:
        refresh_token: Refresh token to invalidate
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 401: Not authenticated
    """
    try:
        auth_service = AuthService(db)
        await auth_service.logout(refresh_token)

        return create_response(
            success=True,
            message="Sesión cerrada correctamente"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_response(
                success=False,
                error={"code": "INVALID_REFRESH_TOKEN", "message": str(e)}
            )
        )


@router.post("/password-reset/request", status_code=status.HTTP_200_OK)
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Request password reset email.

    Always returns 200 to not leak user existence.

    **Functional Requirements**: FR-006

    Args:
        data: Password reset request data
        db: Database session

    Returns:
        Success message (always, for security)
    """
    auth_service = AuthService(db)
    await auth_service.request_password_reset(data.email)

    return create_response(
        success=True,
        message="Si el email existe, recibirás un enlace de restablecimiento"
    )


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Confirm password reset with token.

    **Functional Requirements**: FR-007

    Args:
        data: Password reset confirmation data
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: Invalid or expired token
        HTTPException 400: Weak password
    """
    try:
        auth_service = AuthService(db)
        await auth_service.confirm_password_reset(data.token, data.new_password)

        return create_response(
            success=True,
            message="Contraseña actualizada correctamente"
        )

    except ValueError as e:
        error_msg = str(e)

        if "contraseña" in error_msg.lower() and "caracteres" in error_msg.lower():
            error_code = "WEAK_PASSWORD"
            field = "password"
        elif "expirado" in error_msg.lower():
            error_code = "TOKEN_EXPIRED"
            field = None
        else:
            error_code = "INVALID_TOKEN"
            field = None

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=create_response(
                success=False,
                error={"code": error_code, "message": error_msg, "field": field}
            )
        )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Get current authenticated user information.

    **Functional Requirements**: FR-004

    Args:
        current_user: Current authenticated user from token
        db: Database session

    Returns:
        User information

    Raises:
        HTTPException 401: Not authenticated
    """
    from sqlalchemy import select

    # Get full user data from database
    result = await db.execute(
        select(User).where(User.id == current_user["id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=create_response(
                success=False,
                error={"code": "UNAUTHORIZED", "message": "Usuario no encontrado"}
            )
        )

    return create_response(
        success=True,
        data=UserResponse.from_user_model(user).model_dump()
    )
