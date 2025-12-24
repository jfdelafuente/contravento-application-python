"""
Contract tests for profile API endpoints.

Tests validate that responses conform to the OpenAPI schema in profile.yaml.
"""

import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.contract
@pytest.mark.asyncio
class TestGetUserProfileContract:
    """T098: Contract test for GET /users/{username}/profile."""

    async def test_get_profile_success_schema(
        self, client: AsyncClient, sample_user_data, faker_instance
    ):
        """Verify that profile response matches OpenAPI schema."""
        # Arrange - Register and verify a user
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Act
        response = await client.get(f"/users/{username}/profile")

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

        # Validate profile data
        profile = data["data"]
        assert profile["username"] == username
        assert "full_name" in profile  # Can be None
        assert "bio" in profile  # Can be None
        assert "photo_url" in profile  # Can be None
        assert "location" in profile  # Can be None
        assert "cycling_type" in profile  # Can be None
        assert isinstance(profile["show_email"], bool)
        assert isinstance(profile["show_location"], bool)
        assert isinstance(profile["followers_count"], int)
        assert isinstance(profile["following_count"], int)
        assert "created_at" in profile

    async def test_get_profile_not_found_schema(self, client: AsyncClient):
        """Verify that 404 response for non-existent user matches schema."""
        # Act
        response = await client.get("/users/nonexistent_user/profile")

        # Assert
        assert response.status_code == 404
        data = response.json()

        assert data["success"] is False
        assert data["data"] is None
        assert data["error"] is not None
        assert data["error"]["code"] == "USER_NOT_FOUND"

    async def test_get_profile_respects_privacy_settings(
        self, client: AsyncClient, sample_user_data
    ):
        """Verify that privacy settings affect public profile visibility."""
        # Arrange - Register user
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Act
        response = await client.get(f"/users/{username}/profile")

        # Assert
        profile = response.json()["data"]

        # Privacy fields should be present
        assert "show_email" in profile
        assert "show_location" in profile


@pytest.mark.contract
@pytest.mark.asyncio
class TestUpdateUserProfileContract:
    """T099: Contract test for PUT /users/{username}/profile."""

    async def test_update_profile_success_schema(
        self, client: AsyncClient, sample_user_data, auth_headers
    ):
        """Verify that profile update success response matches OpenAPI schema."""
        # Arrange - Register user
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        update_data = {
            "full_name": "María García López",
            "bio": "Ciclista de montaña apasionada",
            "location": "Barcelona, España",
            "cycling_type": "mountain",
            "show_email": False,
            "show_location": True,
        }

        # Act
        response = await client.put(
            f"/users/{username}/profile",
            json=update_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert "message" in data

        # Validate updated profile
        profile = data["data"]
        assert profile["full_name"] == update_data["full_name"]
        assert profile["bio"] == update_data["bio"]
        assert profile["location"] == update_data["location"]
        assert profile["cycling_type"] == update_data["cycling_type"]
        assert profile["show_email"] == update_data["show_email"]
        assert profile["show_location"] == update_data["show_location"]

    async def test_update_profile_validation_error_schema(
        self, client: AsyncClient, sample_user_data, auth_headers
    ):
        """Verify that validation error response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Bio too long (>500 chars)
        update_data = {
            "bio": "a" * 501
        }

        # Act
        response = await client.put(
            f"/users/{username}/profile",
            json=update_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "bio" in data["error"].get("field", "")

    async def test_update_profile_unauthorized_schema(
        self, client: AsyncClient, sample_user_data
    ):
        """Verify that unauthorized error response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        update_data = {"bio": "New bio"}

        # Act - No auth headers
        response = await client.put(
            f"/users/{username}/profile",
            json=update_data
        )

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "UNAUTHORIZED"

    async def test_update_profile_forbidden_schema(
        self, client: AsyncClient, sample_user_data, auth_headers, faker_instance
    ):
        """Verify that forbidden error response matches OpenAPI schema."""
        # Arrange - Register two users
        user1_data = sample_user_data
        user2_username = faker_instance.user_name().lower().replace(".", "_")

        await client.post("/auth/register", json=user1_data)
        await client.post("/auth/register", json={
            "username": user2_username,
            "email": faker_instance.email(),
            "password": "SecurePass123!"
        })

        update_data = {"bio": "Trying to update someone else's profile"}

        # Act - Try to update user2's profile with user1's token
        response = await client.put(
            f"/users/{user2_username}/profile",
            json=update_data,
            headers=auth_headers  # This is user1's token (from test_user in auth_headers fixture)
        )

        # Assert
        assert response.status_code == 403
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "FORBIDDEN"


@pytest.mark.contract
@pytest.mark.asyncio
class TestUploadProfilePhotoContract:
    """T100: Contract test for POST /users/{username}/profile/photo."""

    async def test_upload_photo_success_schema(
        self, client: AsyncClient, sample_user_data, auth_headers
    ):
        """Verify that photo upload success response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Create a simple 1x1 PNG image
        photo_data = BytesIO(
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00'
            b'\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4'
            b'\x00\x00\x00\x00IEND\xaeB`\x82'
        )

        files = {"photo": ("profile.png", photo_data, "image/png")}

        # Act
        response = await client.post(
            f"/users/{username}/profile/photo",
            files=files,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert "message" in data

        # Validate photo data
        photo_info = data["data"]
        assert "photo_url" in photo_info
        assert "photo_width" in photo_info
        assert "photo_height" in photo_info
        assert photo_info["photo_width"] == 400  # Should be resized
        assert photo_info["photo_height"] == 400

    async def test_upload_photo_invalid_format_schema(
        self, client: AsyncClient, sample_user_data, auth_headers
    ):
        """Verify that invalid format error response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Create a text file instead of image
        invalid_file = BytesIO(b"This is not an image")
        files = {"photo": ("profile.txt", invalid_file, "text/plain")}

        # Act
        response = await client.post(
            f"/users/{username}/profile/photo",
            files=files,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "INVALID_FILE_FORMAT"

    async def test_upload_photo_too_large_schema(
        self, client: AsyncClient, sample_user_data, auth_headers
    ):
        """Verify that file too large error response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Create a file larger than 5MB
        large_file = BytesIO(b"x" * (6 * 1024 * 1024))  # 6MB
        files = {"photo": ("profile.jpg", large_file, "image/jpeg")}

        # Act
        response = await client.post(
            f"/users/{username}/profile/photo",
            files=files,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "FILE_TOO_LARGE"


@pytest.mark.contract
@pytest.mark.asyncio
class TestDeleteProfilePhotoContract:
    """T101: Contract test for DELETE /users/{username}/profile/photo."""

    async def test_delete_photo_success_schema(
        self, client: AsyncClient, sample_user_data, auth_headers
    ):
        """Verify that photo delete success response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Act
        response = await client.delete(
            f"/users/{username}/profile/photo",
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert "message" in data

    async def test_delete_photo_unauthorized_schema(
        self, client: AsyncClient, sample_user_data
    ):
        """Verify that unauthorized error response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        # Act - No auth headers
        response = await client.delete(f"/users/{username}/profile/photo")

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.contract
@pytest.mark.asyncio
class TestUpdatePrivacySettingsContract:
    """T102: Contract test for PUT /users/{username}/profile/privacy."""

    async def test_update_privacy_success_schema(
        self, client: AsyncClient, sample_user_data, auth_headers
    ):
        """Verify that privacy update success response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        privacy_data = {
            "show_email": True,
            "show_location": False
        }

        # Act
        response = await client.put(
            f"/users/{username}/profile/privacy",
            json=privacy_data,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert "message" in data

        # Validate privacy settings
        privacy = data["data"]
        assert privacy["show_email"] == privacy_data["show_email"]
        assert privacy["show_location"] == privacy_data["show_location"]

    async def test_update_privacy_unauthorized_schema(
        self, client: AsyncClient, sample_user_data
    ):
        """Verify that unauthorized error response matches OpenAPI schema."""
        # Arrange
        username = sample_user_data["username"]
        await client.post("/auth/register", json=sample_user_data)

        privacy_data = {"show_email": True}

        # Act - No auth headers
        response = await client.put(
            f"/users/{username}/profile/privacy",
            json=privacy_data
        )

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "UNAUTHORIZED"
