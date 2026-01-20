"""
Authentication service for user registration, login, and password management.

Business logic for authentication flows including:
- User registration with email verification
- Login with rate limiting
- Token refresh and logout
- Password reset flows
"""

import logging
from datetime import UTC, datetime, timedelta

from jose import JWTError
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.auth import PasswordReset
from src.models.user import User, UserProfile
from src.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from src.schemas.user import UserResponse
from src.utils.email import send_password_reset_email, send_verification_email
from src.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service for managing user accounts and sessions.

    Handles registration, email verification, login, logout, and password reset.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize authentication service.

        Args:
            db: Database session
        """
        self.db = db

    async def register(self, data: RegisterRequest) -> RegisterResponse:
        """
        Register a new user.

        Creates user account, sends verification email.

        Args:
            data: Registration request data

        Returns:
            RegisterResponse with user data

        Raises:
            ValueError: If username or email already exists
        """
        # Check for duplicate username
        result = await self.db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise ValueError(f"El nombre de usuario '{data.username}' ya está en uso")

        # Check for duplicate email
        result = await self.db.execute(select(User).where(User.email == data.email.lower()))
        if result.scalar_one_or_none():
            raise ValueError(f"El email '{data.email}' ya está registrado")

        # Create user
        user = User(
            username=data.username,
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.flush()  # Get user ID

        # Create empty profile
        profile = UserProfile(user_id=user.id)
        self.db.add(profile)

        # Create verification token
        token = create_access_token(
            {"sub": user.id, "type": "email_verification"}, expires_delta=timedelta(hours=24)
        )

        # Store verification token
        token_hash = hash_password(token)  # Hash token for security
        password_reset = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            token_type="email_verification",
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        self.db.add(password_reset)

        await self.db.commit()
        await self.db.refresh(user)

        # Send verification email
        await send_verification_email(user.email, user.username, token)

        logger.info(f"User registered: {user.username} (ID: {user.id})")

        return RegisterResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )

    async def verify_email(self, token: str) -> bool:
        """
        Verify user email with token.

        Args:
            token: Verification token from email

        Returns:
            True if verification successful

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            payload = decode_token(token)
        except JWTError:
            raise ValueError("Enlace de verificación inválido")

        if payload.get("type") != "email_verification":
            raise ValueError("Enlace de verificación inválido")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Enlace de verificación inválido")

        # Get user
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Usuario no encontrado")

        if user.is_verified:
            # Already verified, return success
            return True

        # Mark user as verified
        user.is_verified = True

        # Mark token as used
        hash_password(token)
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.token_type == "email_verification",
                PasswordReset.used_at.is_(None),
            )
        )
        token_record = result.scalar_one_or_none()

        if token_record:
            token_record.used_at = datetime.now(UTC)

        await self.db.commit()

        logger.info(f"Email verified for user: {user.username} (ID: {user.id})")

        return True

    async def resend_verification(self, email: str) -> bool:
        """
        Resend verification email.

        Rate limited to 3 requests per hour.

        Args:
            email: Email address to resend verification to

        Returns:
            True if email sent

        Raises:
            ValueError: If rate limit exceeded
        """
        # Get user
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        user = result.scalar_one_or_none()

        if not user:
            # Don't leak user existence, return success
            return True

        if user.is_verified:
            # Already verified, return success
            return True

        # Check rate limit: 3 verification emails per hour
        one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user.id,
                PasswordReset.token_type == "email_verification",
                PasswordReset.created_at >= one_hour_ago,
            )
        )
        recent_tokens = result.scalars().all()

        if len(recent_tokens) >= 3:
            raise ValueError("Demasiados intentos. Intenta de nuevo en 45 minutos.")

        # Create new verification token
        token = create_access_token(
            {"sub": user.id, "type": "email_verification"}, expires_delta=timedelta(hours=24)
        )

        # Store token
        token_hash = hash_password(token)
        password_reset = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            token_type="email_verification",
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        self.db.add(password_reset)
        await self.db.commit()

        # Send email
        await send_verification_email(user.email, user.username, token)

        logger.info(f"Verification email resent for user: {user.username} (ID: {user.id})")

        return True

    async def login(self, data: LoginRequest) -> LoginResponse:
        """
        Authenticate user and create session tokens.

        Args:
            data: Login request data

        Returns:
            LoginResponse with tokens and user data

        Raises:
            ValueError: If credentials are invalid, email not verified, or account locked
        """
        # Find user by email or username
        result = await self.db.execute(
            select(User).where(or_(User.email == data.login.lower(), User.username == data.login))
        )
        user = result.scalar_one_or_none()

        # Check account lockout
        if user and user.locked_until and user.locked_until > datetime.now(UTC):
            raise ValueError("Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos.")

        # Verify credentials
        if not user or not verify_password(data.password, user.hashed_password):
            # Increment failed attempts
            if user:
                user.failed_login_attempts += 1

                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
                    await self.db.commit()
                    raise ValueError(
                        "Demasiados intentos fallidos. Cuenta bloqueada por 15 minutos."
                    )

                await self.db.commit()

            raise ValueError("Email/usuario o contraseña incorrectos")

        # Check if email is verified
        if not user.is_verified:
            raise ValueError("Debes verificar tu email antes de iniciar sesión")

        # Check if account is active
        if not user.is_active:
            raise ValueError("Tu cuenta ha sido desactivada")

        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(UTC)

        # Create tokens
        access_token = create_access_token({"sub": user.id, "username": user.username})
        refresh_token = create_refresh_token({"sub": user.id})

        # Store refresh token
        token_hash = hash_password(refresh_token)
        refresh_token_record = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            token_type="refresh_token",
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
        self.db.add(refresh_token_record)

        await self.db.commit()

        logger.info(f"User logged in: {user.username} (ID: {user.id})")

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.from_user_model(user),
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token using refresh token.

        Invalidates old refresh token and creates new token pair.

        Args:
            refresh_token: Refresh token from login

        Returns:
            TokenResponse with new tokens

        Raises:
            ValueError: If refresh token is invalid or expired
        """
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise ValueError("Token de refresco inválido o expirado")

        if payload.get("type") != "refresh":
            raise ValueError("Token de refresco inválido")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token de refresco inválido")

        # Get all unused refresh tokens for this user
        # We can't filter by token_hash directly because bcrypt hashes are different each time
        result = await self.db.execute(
            select(PasswordReset)
            .where(
                PasswordReset.user_id == user_id,
                PasswordReset.token_type == "refresh_token",
                PasswordReset.used_at.is_(None),
                PasswordReset.expires_at > datetime.now(UTC),
            )
            .order_by(PasswordReset.created_at.desc())
        )
        token_records = result.scalars().all()

        # Find the token that matches the provided refresh token
        token_record = None
        for record in token_records:
            if verify_password(refresh_token, record.token_hash):
                token_record = record
                break

        if not token_record:
            raise ValueError("Token de refresco inválido o expirado")

        # Get user
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("Usuario no encontrado o cuenta desactivada")

        # Mark old refresh token as used
        token_record.used_at = datetime.now(UTC)

        # Create new tokens
        new_access_token = create_access_token({"sub": user.id, "username": user.username})
        new_refresh_token = create_refresh_token({"sub": user.id})

        # Store new refresh token
        new_token_hash = hash_password(new_refresh_token)
        new_refresh_record = PasswordReset(
            user_id=user.id,
            token_hash=new_token_hash,
            token_type="refresh_token",
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
        self.db.add(new_refresh_record)

        await self.db.commit()

        logger.info(f"Token refreshed for user: {user.username} (ID: {user.id})")

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def logout(self, refresh_token: str) -> bool:
        """
        Logout user by invalidating refresh token.

        Access token remains valid until expiration (15 min).

        Args:
            refresh_token: Refresh token to invalidate

        Returns:
            True if logout successful

        Raises:
            ValueError: If refresh token is invalid
        """
        try:
            payload = decode_token(refresh_token)
        except JWTError:
            raise ValueError("Token de refresco inválido")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Token de refresco inválido")

        # Find and mark token as used
        hash_password(refresh_token)
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.token_type == "refresh_token",
                PasswordReset.used_at.is_(None),
            )
        )
        token_record = result.scalar_one_or_none()

        if token_record:
            token_record.used_at = datetime.now(UTC)
            await self.db.commit()

        logger.info(f"User logged out (ID: {user_id})")

        return True

    async def request_password_reset(self, email: str) -> bool:
        """
        Request password reset email.

        Always returns success to not leak user existence.

        Args:
            email: Email address to send reset link to

        Returns:
            True (always, for security)
        """
        # Get user
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        user = result.scalar_one_or_none()

        if not user:
            # Don't leak user existence, return success
            return True

        # Create reset token
        token = create_access_token(
            {"sub": user.id, "type": "password_reset"}, expires_delta=timedelta(hours=1)
        )

        # Store token
        token_hash = hash_password(token)
        password_reset = PasswordReset(
            user_id=user.id,
            token_hash=token_hash,
            token_type="password_reset",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        self.db.add(password_reset)
        await self.db.commit()

        # Send email
        await send_password_reset_email(user.email, user.username, token)

        logger.info(f"Password reset requested for user: {user.username} (ID: {user.id})")

        return True

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """
        Confirm password reset with token.

        Args:
            token: Password reset token from email
            new_password: New password

        Returns:
            True if password reset successful

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            payload = decode_token(token)
        except JWTError:
            raise ValueError("Enlace de restablecimiento inválido o expirado")

        if payload.get("type") != "password_reset":
            raise ValueError("Enlace de restablecimiento inválido")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Enlace de restablecimiento inválido")

        # Get user
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Usuario no encontrado")

        # Verify token exists and is not used
        hash_password(token)
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.token_type == "password_reset",
                PasswordReset.used_at.is_(None),
                PasswordReset.expires_at > datetime.now(UTC),
            )
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise ValueError("Enlace de restablecimiento inválido o expirado")

        # Update password
        user.hashed_password = hash_password(new_password)

        # Mark token as used
        token_record.used_at = datetime.now(UTC)

        # Reset failed login attempts
        user.failed_login_attempts = 0
        user.locked_until = None

        # Invalidate all refresh tokens (force re-login)
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.token_type == "refresh_token",
                PasswordReset.used_at.is_(None),
            )
        )
        refresh_tokens = result.scalars().all()

        for refresh_token in refresh_tokens:
            refresh_token.used_at = datetime.now(UTC)

        await self.db.commit()

        logger.info(f"Password reset for user: {user.username} (ID: {user.id})")

        return True
