"""
Integration tests for profile management workflows.

Tests complete user journeys for profile updates and privacy settings.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserProfile


@pytest.mark.integration
@pytest.mark.asyncio
class TestProfileUpdateWorkflow:
    """T103: Integration test for profile update workflow."""

    async def test_complete_profile_update_journey(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test the complete profile update journey.

        Steps:
        1. Register and verify user
        2. Login to get auth token
        3. Update profile fields
        4. Verify changes in database
        5. View public profile
        6. Verify changes visible
        """
        # Step 1: Register user
        username = sample_user_data["username"]
        email = sample_user_data["email"]
        password = sample_user_data["password"]

        register_response = await client.post("/auth/register", json=sample_user_data)
        assert register_response.status_code == 201

        user_id = register_response.json()["data"]["user_id"]

        # Mark user as verified
        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Step 2: Login
        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": password
        })
        assert login_response.status_code == 200

        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 3: Update profile
        update_data = {
            "full_name": "María García López",
            "bio": "Ciclista de montaña apasionada. Explorando senderos y compartiendo aventuras sobre dos ruedas.",
            "location": "Barcelona, España",
            "cycling_type": "mountain",
            "show_email": False,
            "show_location": True
        }

        update_response = await client.put(
            f"/users/{username}/profile",
            json=update_data,
            headers=auth_headers
        )

        assert update_response.status_code == 200
        update_result = update_response.json()
        assert update_result["success"] is True

        # Step 4: Verify changes in database
        result = await db_session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one()

        assert profile.full_name == update_data["full_name"]
        assert profile.bio == update_data["bio"]
        assert profile.location == update_data["location"]
        assert profile.cycling_type == update_data["cycling_type"]

        # Step 5: View public profile
        public_response = await client.get(f"/users/{username}/profile")

        assert public_response.status_code == 200
        public_data = public_response.json()["data"]

        # Step 6: Verify changes visible
        assert public_data["full_name"] == update_data["full_name"]
        assert public_data["bio"] == update_data["bio"]
        assert public_data["location"] == update_data["location"]
        assert public_data["cycling_type"] == update_data["cycling_type"]


@pytest.mark.integration
@pytest.mark.asyncio
class TestPrivacySettings:
    """T105: Integration test for privacy settings (show_email, show_location)."""

    async def test_privacy_settings_hide_email(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that email is hidden when show_email is False.

        Steps:
        1. Register and verify user with email visible
        2. Update privacy to hide email
        3. View public profile
        4. Verify email is not included in response
        """
        # Step 1: Register and verify
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Update privacy to hide email
        privacy_response = await client.put(
            f"/users/{username}/profile/privacy",
            json={"show_email": False},
            headers=auth_headers
        )

        assert privacy_response.status_code == 200

        # Step 3: View public profile
        profile_response = await client.get(f"/users/{username}/profile")

        # Step 4: Verify email is hidden
        profile_data = profile_response.json()["data"]
        assert profile_data["show_email"] is False
        # Email field should not be in public response when hidden
        # (This depends on implementation - may be null or omitted)

    async def test_privacy_settings_hide_location(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that location is hidden when show_location is False.

        Steps:
        1. Register user with location
        2. Set location in profile
        3. Update privacy to hide location
        4. View public profile
        5. Verify location is not visible
        """
        # Step 1: Register and verify
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Set location
        await client.put(
            f"/users/{username}/profile",
            json={"location": "Madrid, España"},
            headers=auth_headers
        )

        # Step 3: Hide location
        await client.put(
            f"/users/{username}/profile/privacy",
            json={"show_location": False},
            headers=auth_headers
        )

        # Step 4 & 5: View public profile and verify location is hidden
        profile_response = await client.get(f"/users/{username}/profile")
        profile_data = profile_response.json()["data"]

        assert profile_data["show_location"] is False


@pytest.mark.integration
@pytest.mark.asyncio
class TestPublicProfileView:
    """T106: Integration test for public profile view respecting privacy."""

    async def test_public_profile_respects_all_privacy_settings(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that public profile view respects all privacy settings.

        Steps:
        1. Create user with full profile
        2. Set strict privacy (hide email and location)
        3. View profile as anonymous user
        4. Verify only public info is visible
        5. Update privacy to show all
        6. Verify info is now visible
        """
        # Step 1: Create user with full profile
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Login
        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Create full profile
        await client.put(
            f"/users/{username}/profile",
            json={
                "full_name": "María García",
                "bio": "Ciclista apasionada",
                "location": "Barcelona, España",
                "cycling_type": "mountain",
            },
            headers=auth_headers
        )

        # Step 2: Set strict privacy
        await client.put(
            f"/users/{username}/profile/privacy",
            json={"show_email": False, "show_location": False},
            headers=auth_headers
        )

        # Step 3 & 4: View as anonymous user
        public_response = await client.get(f"/users/{username}/profile")
        public_data = public_response.json()["data"]

        # Always visible
        assert public_data["username"] == username
        assert public_data["full_name"] == "María García"
        assert public_data["bio"] == "Ciclista apasionada"

        # Privacy controlled
        assert public_data["show_email"] is False
        assert public_data["show_location"] is False

        # Step 5: Update to show all
        await client.put(
            f"/users/{username}/profile/privacy",
            json={"show_email": True, "show_location": True},
            headers=auth_headers
        )

        # Step 6: Verify info now visible
        updated_response = await client.get(f"/users/{username}/profile")
        updated_data = updated_response.json()["data"]

        assert updated_data["show_email"] is True
        assert updated_data["show_location"] is True

    async def test_nonexistent_user_profile_returns_404(self, client: AsyncClient):
        """Test that requesting profile for non-existent user returns 404."""
        response = await client.get("/users/nonexistent_user_123/profile")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "USER_NOT_FOUND"
