"""
Contract tests for authentication API endpoints.

Tests validate that responses conform to the expected API schema structure.
Manual validation approach - each test asserts response structure matches expectations.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthRegisterContract:
    """Contract tests for POST /auth/register."""

    async def test_register_success_schema(self, client: AsyncClient, faker_instance):
        """T037: Validate successful registration response matches expected schema."""
        # Arrange
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        payload = {
            "username": username,
            "email": email,
            "password": "SecurePass123!",
        }

        # Act
        response = await client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None
        assert "message" in data

        # Validate user data
        user_data = data["data"]
        assert "user_id" in user_data
        assert user_data["username"] == username
        assert user_data["email"] == email
        assert user_data["is_verified"] is False
        assert "created_at" in user_data

    async def test_register_duplicate_username_schema(self, client: AsyncClient, faker_instance):
        """T037: Validate duplicate username error matches expected schema."""
        # Arrange
        username = faker_instance.user_name().lower().replace(".", "_")
        email1 = faker_instance.email()
        email2 = faker_instance.email()

        await client.post("/auth/register", json={
            "username": username,
            "email": email1,
            "password": "SecurePass123!",
        })

        # Act - Try to register with same username
        response = await client.post("/auth/register", json={
            "username": username,
            "email": email2,
            "password": "SecurePass123!",
        })

        # Assert
        assert response.status_code == 400
        data = response.json()

        # Validate error response structure
        assert data["success"] is False
        assert data["data"] is None
        assert data["error"] is not None

        # Validate error details
        error = data["error"]
        assert error["code"] == "USERNAME_TAKEN"
        assert username in error["message"]
        assert error.get("field") == "username"

    async def test_register_duplicate_email_schema(self, client: AsyncClient, faker_instance):
        """T037: Validate duplicate email error matches expected schema."""
        # Arrange
        username1 = faker_instance.user_name().lower().replace(".", "_")
        username2 = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()

        await client.post("/auth/register", json={
            "username": username1,
            "email": email,
            "password": "SecurePass123!",
        })

        # Act - Try to register with same email
        response = await client.post("/auth/register", json={
            "username": username2,
            "email": email,
            "password": "SecurePass123!",
        })

        # Assert
        assert response.status_code == 400
        data = response.json()

        # Validate error response structure
        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "EMAIL_TAKEN"
        assert email in data["error"]["message"]
        assert data["error"].get("field") == "email"

    async def test_register_weak_password_schema(self, client: AsyncClient, faker_instance):
        """T037: Validate weak password error matches expected schema."""
        # Arrange
        payload = {
            "username": faker_instance.user_name().lower().replace(".", "_"),
            "email": faker_instance.email(),
            "password": "weak",
        }

        # Act
        response = await client.post("/auth/register", json=payload)

        # Assert
        assert response.status_code == 400
        data = response.json()

        # Validate error response structure
        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "WEAK_PASSWORD"
        assert data["error"].get("field") == "password"


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthVerifyEmailContract:
    """Contract tests for POST /auth/verify-email."""

    async def test_verify_email_success_schema(self, client: AsyncClient, faker_instance):
        """T038: Validate email verification success response matches expected schema."""
        # Arrange - Register a user first
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        await client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": "SecurePass123!",
        })

        # TODO: Extract verification token from email/database
        # For now, this is a placeholder that will fail until implementation
        verification_token = "valid_token_placeholder"

        # Act
        response = await client.post("/auth/verify-email", json={"token": verification_token})

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data

    async def test_verify_email_invalid_token_schema(self, client: AsyncClient):
        """T038: Validate invalid token error matches expected schema."""
        # Act
        response = await client.post("/auth/verify-email", json={"token": "invalid_token"})

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "INVALID_TOKEN"


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthResendVerificationContract:
    """Contract tests for POST /auth/resend-verification."""

    async def test_resend_verification_success_schema(self, client: AsyncClient, faker_instance):
        """T039: Validate resend verification success response matches expected schema."""
        # Arrange - Register a user first
        email = faker_instance.email()
        await client.post("/auth/register", json={
            "username": faker_instance.user_name().lower().replace(".", "_"),
            "email": email,
            "password": "SecurePass123!",
        })

        # Act
        response = await client.post("/auth/resend-verification", json={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data

    async def test_resend_verification_rate_limit_schema(self, client: AsyncClient, faker_instance):
        """T039: Validate rate limit error matches expected schema."""
        # Arrange
        email = faker_instance.email()
        await client.post("/auth/register", json={
            "username": faker_instance.user_name().lower().replace(".", "_"),
            "email": email,
            "password": "SecurePass123!",
        })

        # Act - Send 4 requests to trigger rate limit (3 allowed per hour)
        for _ in range(4):
            response = await client.post("/auth/resend-verification", json={"email": email})

        # Assert
        assert response.status_code == 429
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthLoginContract:
    """Contract tests for POST /auth/login."""

    async def test_login_success_schema(self, client: AsyncClient, faker_instance):
        """T040: Validate successful login response matches expected schema."""
        # Arrange - Register and verify a user
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        await client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
        })

        # TODO: Verify email programmatically
        # For now, this test will fail until email verification is implemented

        # Act
        response = await client.post("/auth/login", json={
            "login": username,
            "password": password,
        })

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

        # Validate token data
        token_data = data["data"]
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert token_data["expires_in"] == 900  # 15 minutes

        # Validate user data
        user_data = token_data["user"]
        assert user_data["username"] == username
        assert user_data["email"] == email
        assert user_data["is_verified"] is True

    async def test_login_invalid_credentials_schema(self, client: AsyncClient):
        """T040: Validate invalid credentials error matches expected schema."""
        # Act
        response = await client.post("/auth/login", json={
            "login": "nonexistent@example.com",
            "password": "WrongPassword123!",
        })

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "INVALID_CREDENTIALS"

    async def test_login_unverified_email_schema(self, client: AsyncClient, faker_instance):
        """T040: Validate unverified email error matches expected schema."""
        # Arrange - Register but don't verify
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        await client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
        })

        # Act
        response = await client.post("/auth/login", json={
            "login": username,
            "password": password,
        })

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "EMAIL_NOT_VERIFIED"

    async def test_login_account_locked_schema(self, client: AsyncClient, faker_instance):
        """T040: Validate account locked error matches expected schema."""
        # Arrange - Register and verify a user
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        await client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
        })

        # Act - Try to login with wrong password 5 times
        for _ in range(5):
            response = await client.post("/auth/login", json={
                "login": username,
                "password": "WrongPassword123!",
            })

        # Assert
        assert response.status_code == 429
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "ACCOUNT_LOCKED"


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthRefreshContract:
    """Contract tests for POST /auth/refresh."""

    async def test_refresh_token_success_schema(self, client: AsyncClient, faker_instance):
        """T041: Validate token refresh success response matches expected schema."""
        # Arrange - Login to get tokens
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        await client.post("/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
        })

        # TODO: Verify email and login to get refresh token
        refresh_token = "valid_refresh_token_placeholder"

        # Act
        response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"

    async def test_refresh_token_invalid_schema(self, client: AsyncClient):
        """T041: Validate invalid refresh token error matches expected schema."""
        # Act
        response = await client.post("/auth/refresh", json={"refresh_token": "invalid_token"})

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthLogoutContract:
    """Contract tests for POST /auth/logout."""

    async def test_logout_success_schema(self, client: AsyncClient, auth_headers):
        """T042: Validate logout success response matches expected schema."""
        # Arrange
        # TODO: Get actual refresh token from login
        refresh_token = "valid_refresh_token_placeholder"

        # Act
        response = await client.post(
            "/auth/logout",
            json={"refresh_token": refresh_token},
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data

    async def test_logout_unauthorized_schema(self, client: AsyncClient):
        """T042: Validate unauthorized error matches expected schema."""
        # Act
        response = await client.post("/auth/logout", json={"refresh_token": "some_token"})

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthPasswordResetRequestContract:
    """Contract tests for POST /auth/password-reset/request."""

    async def test_password_reset_request_success_schema(self, client: AsyncClient, faker_instance):
        """T043: Validate password reset request success response matches expected schema."""
        # Arrange
        email = faker_instance.email()
        await client.post("/auth/register", json={
            "username": faker_instance.user_name().lower().replace(".", "_"),
            "email": email,
            "password": "SecurePass123!",
        })

        # Act
        response = await client.post("/auth/password-reset/request", json={"email": email})

        # Assert - Always returns 200 for security
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data

    async def test_password_reset_request_nonexistent_email_schema(self, client: AsyncClient):
        """T043: Validate password reset request for nonexistent email (still 200)."""
        # Act
        response = await client.post(
            "/auth/password-reset/request",
            json={"email": "nonexistent@example.com"}
        )

        # Assert - Should still return 200 to not leak user existence
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthPasswordResetConfirmContract:
    """Contract tests for POST /auth/password-reset/confirm."""

    async def test_password_reset_confirm_success_schema(self, client: AsyncClient):
        """T044: Validate password reset confirm success response matches expected schema."""
        # Arrange
        # TODO: Request password reset and get token
        reset_token = "valid_reset_token_placeholder"

        # Act
        response = await client.post("/auth/password-reset/confirm", json={
            "token": reset_token,
            "new_password": "NewSecurePass456!"
        })

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "message" in data

    async def test_password_reset_confirm_invalid_token_schema(self, client: AsyncClient):
        """T044: Validate invalid token error matches expected schema."""
        # Act
        response = await client.post("/auth/password-reset/confirm", json={
            "token": "invalid_token",
            "new_password": "NewSecurePass456!"
        })

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] in ["INVALID_TOKEN", "TOKEN_EXPIRED"]

    async def test_password_reset_confirm_weak_password_schema(self, client: AsyncClient):
        """T044: Validate weak password error matches expected schema."""
        # Arrange
        # TODO: Get valid reset token
        reset_token = "valid_reset_token_placeholder"

        # Act
        response = await client.post("/auth/password-reset/confirm", json={
            "token": reset_token,
            "new_password": "weak"
        })

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "WEAK_PASSWORD"


@pytest.mark.contract
@pytest.mark.asyncio
class TestAuthGetCurrentUserContract:
    """Contract tests for GET /auth/me."""

    async def test_get_current_user_success_schema(self, client: AsyncClient, auth_headers):
        """T045: Validate get current user success response matches expected schema."""
        # Act
        response = await client.get("/auth/me", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None

        # Validate user data
        user_data = data["data"]
        assert "user_id" in user_data
        assert "username" in user_data
        assert "email" in user_data
        assert "is_verified" in user_data
        assert "created_at" in user_data

    async def test_get_current_user_unauthorized_schema(self, client: AsyncClient):
        """T045: Validate unauthorized error matches expected schema."""
        # Act
        response = await client.get("/auth/me")

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "UNAUTHORIZED"

    async def test_get_current_user_invalid_token_schema(self, client: AsyncClient):
        """T045: Validate invalid token error matches expected schema."""
        # Act
        response = await client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "UNAUTHORIZED"
