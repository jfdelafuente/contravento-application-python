"""
Unit tests for AuthService business logic.

Tests the authentication service layer methods.
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.auth import LoginRequest, RegisterRequest
from src.services.auth_service import AuthService


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthServiceRegister:
    """T054: Unit tests for AuthService.register()."""

    async def test_register_creates_user_successfully(self, db_session: AsyncSession):
        """Verify that register creates a new user and sends verification email."""
        # Arrange
        auth_service = AuthService(db_session)
        register_data = RegisterRequest(
            username="new_user", email="new@example.com", password="SecurePass123!"
        )

        # Act
        with patch("src.services.auth_service.send_verification_email") as mock_email:
            mock_email.return_value = True
            result = await auth_service.register(register_data)

        # Assert
        assert result is not None
        assert result.username == "new_user"
        assert result.email == "new@example.com"
        assert result.is_verified is False
        assert result.is_active is True
        assert hasattr(result, "created_at")

        # Verify email was sent
        mock_email.assert_called_once()

    async def test_register_duplicate_username_raises_error(
        self, db_session: AsyncSession, sample_user_data
    ):
        """Verify that registering with duplicate username raises ValueError."""
        # Arrange
        auth_service = AuthService(db_session)

        # Create first user
        first_user = RegisterRequest(**sample_user_data)
        with patch("src.services.auth_service.send_verification_email", return_value=True):
            await auth_service.register(first_user)

        # Act & Assert - Try to create second user with same username
        duplicate_user = RegisterRequest(
            username=sample_user_data["username"],
            email="different@example.com",
            password="SecurePass123!",
        )

        with pytest.raises(ValueError) as exc_info:
            await auth_service.register(duplicate_user)

        assert "nombre de usuario" in str(exc_info.value).lower()
        assert "en uso" in str(exc_info.value).lower()

    async def test_register_duplicate_email_raises_error(
        self, db_session: AsyncSession, sample_user_data
    ):
        """Verify that registering with duplicate email raises ValueError."""
        # Arrange
        auth_service = AuthService(db_session)

        # Create first user
        first_user = RegisterRequest(**sample_user_data)
        with patch("src.services.auth_service.send_verification_email", return_value=True):
            await auth_service.register(first_user)

        # Act & Assert - Try to create second user with same email
        duplicate_user = RegisterRequest(
            username="different_user", email=sample_user_data["email"], password="SecurePass123!"
        )

        with pytest.raises(ValueError) as exc_info:
            await auth_service.register(duplicate_user)

        assert "email" in str(exc_info.value).lower()
        assert "registrado" in str(exc_info.value).lower()

    async def test_register_hashes_password(self, db_session: AsyncSession):
        """Verify that register hashes the password before storing."""
        # Arrange
        auth_service = AuthService(db_session)
        plain_password = "SecurePass123!"
        register_data = RegisterRequest(
            username="test_user", email="test@example.com", password=plain_password
        )

        # Act
        with patch("src.services.auth_service.send_verification_email", return_value=True):
            result = await auth_service.register(register_data)

        # Assert
        from sqlalchemy import select

        from src.models.user import User

        user_result = await db_session.execute(select(User).where(User.id == result.id))
        user = user_result.scalar_one()

        # Password should be hashed, not stored in plain text
        assert user.hashed_password != plain_password
        assert len(user.hashed_password) > 50  # Bcrypt hashes are long

    async def test_register_creates_verification_token(self, db_session: AsyncSession):
        """Verify that register creates a verification token."""
        # Arrange
        auth_service = AuthService(db_session)
        register_data = RegisterRequest(
            username="test_user", email="test@example.com", password="SecurePass123!"
        )

        # Act
        with patch("src.services.auth_service.send_verification_email", return_value=True):
            result = await auth_service.register(register_data)

        # Assert
        from sqlalchemy import select

        from src.models.auth import PasswordReset

        token_result = await db_session.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == result.id, PasswordReset.token_type == "email_verification"
            )
        )
        token = token_result.scalar_one_or_none()

        assert token is not None
        assert token.used_at is None
        assert token.expires_at > datetime.utcnow()


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthServiceVerifyEmail:
    """T055: Unit tests for AuthService.verify_email()."""

    async def test_verify_email_with_valid_token(self, db_session: AsyncSession):
        """Verify that valid token successfully verifies email."""
        # Arrange
        AuthService(db_session)

        # Create user and verification token
        # TODO: Setup test data

        # Act
        # result = await auth_service.verify_email(token)

        # Assert
        # assert result is True
        pytest.skip("TODO: Implement after user/token creation helpers")

    async def test_verify_email_with_expired_token(self, db_session: AsyncSession):
        """Verify that expired token raises ValueError."""
        # Arrange
        AuthService(db_session)

        # TODO: Create expired token

        # Act & Assert
        # with pytest.raises(ValueError) as exc_info:
        #     await auth_service.verify_email(expired_token)
        # assert "expirado" in str(exc_info.value).lower()

        pytest.skip("TODO: Implement after user/token creation helpers")

    async def test_verify_email_with_invalid_token(self, db_session: AsyncSession):
        """Verify that invalid token raises ValueError."""
        # Arrange
        auth_service = AuthService(db_session)
        invalid_token = "invalid_token_string"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await auth_service.verify_email(invalid_token)

        assert "inválido" in str(exc_info.value).lower()

    async def test_verify_email_marks_user_as_verified(self, db_session: AsyncSession):
        """Verify that successful verification marks user as verified."""
        pytest.skip("TODO: Implement after user/token creation helpers")


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthServiceLogin:
    """T056: Unit tests for AuthService.login()."""

    async def test_login_with_valid_credentials_returns_tokens(self, db_session: AsyncSession):
        """Verify that valid credentials return access and refresh tokens."""
        pytest.skip("TODO: Implement after user creation helpers")

    async def test_login_with_username(self, db_session: AsyncSession):
        """Verify that login works with username."""
        pytest.skip("TODO: Implement after user creation helpers")

    async def test_login_with_email(self, db_session: AsyncSession):
        """Verify that login works with email."""
        pytest.skip("TODO: Implement after user creation helpers")

    async def test_login_with_invalid_credentials_raises_error(self, db_session: AsyncSession):
        """Verify that invalid credentials raise ValueError."""
        # Arrange
        auth_service = AuthService(db_session)
        login_data = LoginRequest(login="nonexistent@example.com", password="WrongPass123!")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await auth_service.login(login_data)

        assert "incorrectos" in str(exc_info.value).lower()

    async def test_login_with_unverified_email_raises_error(self, db_session: AsyncSession):
        """Verify that unverified users cannot login."""
        pytest.skip("TODO: Implement after user creation helpers")

    async def test_login_increments_failed_attempts(self, db_session: AsyncSession):
        """Verify that failed login increments failed_attempts counter."""
        pytest.skip("TODO: Implement after user creation helpers")

    async def test_login_resets_failed_attempts_on_success(self, db_session: AsyncSession):
        """Verify that successful login resets failed_attempts to 0."""
        pytest.skip("TODO: Implement after user creation helpers")


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthServiceRefreshToken:
    """T057: Unit tests for AuthService.refresh_token()."""

    async def test_refresh_token_with_valid_token(self, db_session: AsyncSession):
        """Verify that valid refresh token returns new tokens."""
        pytest.skip("TODO: Implement after token creation helpers")

    async def test_refresh_token_with_invalid_token(self, db_session: AsyncSession):
        """Verify that invalid refresh token raises ValueError."""
        # Arrange
        auth_service = AuthService(db_session)
        invalid_token = "invalid_refresh_token"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await auth_service.refresh_token(invalid_token)

        assert (
            "inválido" in str(exc_info.value).lower() or "expirado" in str(exc_info.value).lower()
        )

    async def test_refresh_token_invalidates_old_token(self, db_session: AsyncSession):
        """Verify that using refresh token invalidates the old one."""
        pytest.skip("TODO: Implement after token creation helpers")


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthServiceLogout:
    """T058: Unit tests for AuthService.logout()."""

    async def test_logout_invalidates_refresh_token(self, db_session: AsyncSession):
        """Verify that logout invalidates the refresh token."""
        pytest.skip("TODO: Implement after token creation helpers")

    async def test_logout_with_invalid_token(self, db_session: AsyncSession):
        """Verify that logout with invalid token raises ValueError."""
        # Arrange
        auth_service = AuthService(db_session)
        invalid_token = "invalid_token"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await auth_service.logout(invalid_token)

        assert "inválido" in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthServiceRequestPasswordReset:
    """T059: Unit tests for AuthService.request_password_reset()."""

    async def test_request_password_reset_creates_token(self, db_session: AsyncSession):
        """Verify that password reset request creates a reset token."""
        pytest.skip("TODO: Implement after user creation helpers")

    async def test_request_password_reset_sends_email(self, db_session: AsyncSession):
        """Verify that password reset request sends email."""
        pytest.skip("TODO: Implement after user creation helpers")

    async def test_request_password_reset_for_nonexistent_email(self, db_session: AsyncSession):
        """Verify that nonexistent email doesn't leak user existence (returns success)."""
        # Arrange
        auth_service = AuthService(db_session)
        email = "nonexistent@example.com"

        # Act
        result = await auth_service.request_password_reset(email)

        # Assert - Should return success to not leak user existence
        assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
class TestAuthServiceConfirmPasswordReset:
    """T060: Unit tests for AuthService.confirm_password_reset()."""

    async def test_confirm_password_reset_with_valid_token(self, db_session: AsyncSession):
        """Verify that valid token successfully resets password."""
        pytest.skip("TODO: Implement after token creation helpers")

    async def test_confirm_password_reset_with_invalid_token(self, db_session: AsyncSession):
        """Verify that invalid token raises ValueError."""
        # Arrange
        auth_service = AuthService(db_session)
        invalid_token = "invalid_token"
        new_password = "NewPass123!"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await auth_service.confirm_password_reset(invalid_token, new_password)

        assert (
            "inválido" in str(exc_info.value).lower() or "expirado" in str(exc_info.value).lower()
        )

    async def test_confirm_password_reset_with_expired_token(self, db_session: AsyncSession):
        """Verify that expired token raises ValueError."""
        pytest.skip("TODO: Implement after token creation helpers")

    async def test_confirm_password_reset_hashes_new_password(self, db_session: AsyncSession):
        """Verify that new password is hashed before storing."""
        pytest.skip("TODO: Implement after token creation helpers")

    async def test_confirm_password_reset_marks_token_as_used(self, db_session: AsyncSession):
        """Verify that used token is marked as used and cannot be reused."""
        pytest.skip("TODO: Implement after token creation helpers")
