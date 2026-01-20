"""
Integration tests for authentication user journeys.

Tests complete user flows from registration through authentication.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
@pytest.mark.asyncio
class TestRegistrationToLoginFlow:
    """T046: Integration test for registration → email verification → login flow."""

    async def test_complete_registration_and_login_journey(
        self, client: AsyncClient, db_session: AsyncSession, faker_instance
    ):
        """
        Test the complete user journey: register → verify email → login.

        Steps:
        1. Register a new user
        2. Extract verification token from database
        3. Verify email with token
        4. Login with credentials
        5. Access protected endpoint
        """
        # Step 1: Register new user
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        register_response = await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

        assert register_response.status_code == 201
        register_data = register_response.json()
        assert register_data["success"] is True
        assert register_data["data"]["is_verified"] is False

        user_id = register_data["data"]["user_id"]

        # Step 2: Extract verification token from database
        # TODO: Query PasswordReset table for verification token
        # For now, this is a placeholder
        from src.models.auth import PasswordReset
        from src.models.user import User

        result = await db_session.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.token_type == "email_verification",
                PasswordReset.used_at.is_(None),
            )
        )
        token_record = result.scalar_one_or_none()
        assert token_record is not None, "Verification token should be created"

        # Generate JWT token from the token_hash
        # TODO: This depends on how we store/generate verification tokens
        verification_token = "extracted_verification_token"

        # Step 3: Verify email
        verify_response = await client.post(
            "/auth/verify-email", json={"token": verification_token}
        )

        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["success"] is True

        # Verify user is now verified in database
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        assert user.is_verified is True

        # Step 4: Login with credentials
        login_response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": password,
            },
        )

        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["success"] is True

        # Validate tokens
        assert "access_token" in login_data["data"]
        assert "refresh_token" in login_data["data"]
        assert login_data["data"]["token_type"] == "bearer"

        access_token = login_data["data"]["access_token"]

        # Step 5: Access protected endpoint
        me_response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["success"] is True
        assert me_data["data"]["username"] == username
        assert me_data["data"]["is_verified"] is True

    async def test_login_before_verification_fails(self, client: AsyncClient, faker_instance):
        """
        Test that login fails for unverified users.

        Steps:
        1. Register a new user
        2. Attempt to login without verifying email
        3. Verify login fails with EMAIL_NOT_VERIFIED error
        """
        # Step 1: Register
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

        # Step 2: Try to login without verification
        login_response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": password,
            },
        )

        # Step 3: Verify error
        assert login_response.status_code == 400
        login_data = login_response.json()
        assert login_data["success"] is False
        assert login_data["error"]["code"] == "EMAIL_NOT_VERIFIED"

    async def test_resend_verification_email(self, client: AsyncClient, faker_instance):
        """
        Test resending verification email.

        Steps:
        1. Register a new user
        2. Resend verification email
        3. Verify new token invalidates old one
        """
        # Step 1: Register
        email = faker_instance.email()
        await client.post(
            "/auth/register",
            json={
                "username": faker_instance.user_name().lower().replace(".", "_"),
                "email": email,
                "password": "SecurePass123!",
            },
        )

        # Step 2: Resend verification
        resend_response = await client.post("/auth/resend-verification", json={"email": email})

        assert resend_response.status_code == 200
        resend_data = resend_response.json()
        assert resend_data["success"] is True


@pytest.mark.integration
@pytest.mark.asyncio
class TestPasswordResetFlow:
    """T047: Integration test for forgot password → reset → login flow."""

    async def test_complete_password_reset_journey(
        self, client: AsyncClient, db_session: AsyncSession, faker_instance
    ):
        """
        Test the complete password reset journey.

        Steps:
        1. Register and verify a user
        2. Request password reset
        3. Extract reset token from database
        4. Confirm password reset with new password
        5. Verify old password no longer works
        6. Login with new password
        """
        # Step 1: Register and verify user
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"

        register_response = await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": old_password,
            },
        )

        user_id = register_response.json()["data"]["user_id"]

        # TODO: Verify email programmatically
        # For now, manually set user as verified
        from src.models.user import User

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Step 2: Request password reset
        reset_request_response = await client.post(
            "/auth/password-reset/request", json={"email": email}
        )

        assert reset_request_response.status_code == 200
        assert reset_request_response.json()["success"] is True

        # Step 3: Extract reset token from database
        from src.models.auth import PasswordReset

        result = await db_session.execute(
            select(PasswordReset).where(
                PasswordReset.user_id == user_id,
                PasswordReset.token_type == "password_reset",
                PasswordReset.used_at.is_(None),
            )
        )
        token_record = result.scalar_one_or_none()
        assert token_record is not None, "Reset token should be created"

        # TODO: Generate JWT from token_hash
        reset_token = "extracted_reset_token"

        # Step 4: Confirm password reset
        reset_confirm_response = await client.post(
            "/auth/password-reset/confirm",
            json={"token": reset_token, "new_password": new_password},
        )

        assert reset_confirm_response.status_code == 200
        assert reset_confirm_response.json()["success"] is True

        # Step 5: Verify old password no longer works
        old_login_response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": old_password,
            },
        )

        assert old_login_response.status_code == 401
        assert old_login_response.json()["error"]["code"] == "INVALID_CREDENTIALS"

        # Step 6: Login with new password
        new_login_response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": new_password,
            },
        )

        assert new_login_response.status_code == 200
        assert new_login_response.json()["success"] is True

    async def test_password_reset_token_expires(
        self, client: AsyncClient, db_session: AsyncSession, faker_instance
    ):
        """
        Test that password reset tokens expire after 1 hour.

        Steps:
        1. Register and verify user
        2. Request password reset
        3. Manually expire the token
        4. Attempt to use expired token
        5. Verify error
        """
        # Step 1: Register and verify
        email = faker_instance.email()
        await client.post(
            "/auth/register",
            json={
                "username": faker_instance.user_name().lower().replace(".", "_"),
                "email": email,
                "password": "SecurePass123!",
            },
        )

        # Step 2: Request reset
        await client.post("/auth/password-reset/request", json={"email": email})

        # Step 3: TODO: Manually expire token in database
        # Step 4: TODO: Try to use expired token
        # Step 5: Verify TOKEN_EXPIRED error


@pytest.mark.integration
@pytest.mark.asyncio
class TestTokenRefreshFlow:
    """T048: Integration test for token refresh mechanism."""

    async def test_refresh_token_mechanism(self, client: AsyncClient, faker_instance):
        """
        Test the token refresh flow.

        Steps:
        1. Register, verify, and login
        2. Use refresh token to get new access token
        3. Verify old access token still works (until expiration)
        4. Verify new access token works
        5. Verify new refresh token works
        """
        # Step 1: Register, verify, and login
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

        # TODO: Verify email
        # TODO: Login to get tokens

        login_response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": password,
            },
        )

        old_access_token = login_response.json()["data"]["access_token"]
        old_refresh_token = login_response.json()["data"]["refresh_token"]

        # Step 2: Refresh tokens
        refresh_response = await client.post(
            "/auth/refresh", json={"refresh_token": old_refresh_token}
        )

        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        assert refresh_data["success"] is True

        new_access_token = refresh_data["data"]["access_token"]
        new_refresh_token = refresh_data["data"]["refresh_token"]

        # Step 3: Verify old access token still works
        old_me_response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {old_access_token}"}
        )
        # Old access token should still work until it expires
        assert old_me_response.status_code == 200

        # Step 4: Verify new access token works
        new_me_response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {new_access_token}"}
        )
        assert new_me_response.status_code == 200

        # Step 5: Verify new refresh token works
        second_refresh_response = await client.post(
            "/auth/refresh", json={"refresh_token": new_refresh_token}
        )
        assert second_refresh_response.status_code == 200

        # Step 6: Verify old refresh token no longer works
        old_refresh_response = await client.post(
            "/auth/refresh", json={"refresh_token": old_refresh_token}
        )
        assert old_refresh_response.status_code == 401
        assert old_refresh_response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"

    async def test_logout_invalidates_refresh_token(self, client: AsyncClient, faker_instance):
        """
        Test that logout invalidates refresh token.

        Steps:
        1. Login to get tokens
        2. Logout
        3. Verify refresh token no longer works
        4. Verify access token still works (until expiration)
        """
        # Step 1: Login
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "SecurePass123!"

        await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

        # TODO: Verify and login

        login_response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": password,
            },
        )

        access_token = login_response.json()["data"]["access_token"]
        refresh_token = login_response.json()["data"]["refresh_token"]

        # Step 2: Logout
        logout_response = await client.post(
            "/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert logout_response.status_code == 200

        # Step 3: Verify refresh token no longer works
        refresh_response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

        assert refresh_response.status_code == 401
        assert refresh_response.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"

        # Step 4: Verify access token still works
        me_response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
class TestRateLimiting:
    """T049: Integration test for rate limiting (5 failed login attempts)."""

    async def test_account_lockout_after_five_failed_attempts(
        self, client: AsyncClient, faker_instance
    ):
        """
        Test account lockout after 5 failed login attempts.

        Steps:
        1. Register and verify a user
        2. Attempt 5 failed logins
        3. Verify account is locked
        4. Wait 15 minutes (or mock time)
        5. Verify account is unlocked
        """
        # Step 1: Register and verify
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "CorrectPass123!"

        await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

        # TODO: Verify email

        # Step 2: Attempt 5 failed logins
        for i in range(5):
            response = await client.post(
                "/auth/login",
                json={
                    "login": username,
                    "password": "WrongPassword123!",
                },
            )

            if i < 4:
                # First 4 attempts should return 401
                assert response.status_code == 401
                assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
            else:
                # 5th attempt should lock account
                assert response.status_code == 429
                assert response.json()["error"]["code"] == "ACCOUNT_LOCKED"

        # Step 3: Verify account is locked even with correct password
        response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": password,
            },
        )

        assert response.status_code == 429
        assert response.json()["error"]["code"] == "ACCOUNT_LOCKED"

        # Step 4: TODO: Mock time to advance 15 minutes
        # Step 5: TODO: Verify account is unlocked and can login

    async def test_successful_login_resets_failed_attempts(
        self, client: AsyncClient, faker_instance
    ):
        """
        Test that successful login resets failed attempt counter.

        Steps:
        1. Register and verify user
        2. Make 3 failed login attempts
        3. Make 1 successful login
        4. Make 3 more failed attempts
        5. Verify account is not locked (counter was reset)
        """
        # Step 1: Register and verify
        username = faker_instance.user_name().lower().replace(".", "_")
        email = faker_instance.email()
        password = "CorrectPass123!"

        await client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
        )

        # TODO: Verify email

        # Step 2: 3 failed attempts
        for _ in range(3):
            await client.post(
                "/auth/login",
                json={
                    "login": username,
                    "password": "WrongPassword123!",
                },
            )

        # Step 3: Successful login
        success_response = await client.post(
            "/auth/login",
            json={
                "login": username,
                "password": password,
            },
        )
        assert success_response.status_code == 200

        # Step 4: 3 more failed attempts
        for _i in range(3):
            response = await client.post(
                "/auth/login",
                json={
                    "login": username,
                    "password": "WrongPassword123!",
                },
            )
            # Should return 401, not 429 (account locked)
            assert response.status_code == 401

    async def test_verification_email_rate_limiting(self, client: AsyncClient, faker_instance):
        """
        Test rate limiting for verification email resends (3 per hour).

        Steps:
        1. Register user
        2. Resend verification 3 times (should succeed)
        3. 4th resend should fail with RATE_LIMIT_EXCEEDED
        """
        # Step 1: Register
        email = faker_instance.email()
        await client.post(
            "/auth/register",
            json={
                "username": faker_instance.user_name().lower().replace(".", "_"),
                "email": email,
                "password": "SecurePass123!",
            },
        )

        # Step 2: Resend 3 times
        for i in range(4):
            response = await client.post("/auth/resend-verification", json={"email": email})

            if i < 3:
                # First 3 should succeed
                assert response.status_code == 200
            else:
                # 4th should fail
                assert response.status_code == 429
                assert response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"
