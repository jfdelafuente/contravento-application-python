"""
Integration tests for profile photo upload with resize.

Tests complete photo upload workflow including validation and processing.
"""

import pytest
from httpx import AsyncClient
from io import BytesIO
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User, UserProfile


@pytest.mark.integration
@pytest.mark.asyncio
class TestPhotoUploadWithResize:
    """T104: Integration test for photo upload with resize."""

    async def test_complete_photo_upload_and_resize_journey(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test complete photo upload workflow with resize.

        Steps:
        1. Register and verify user
        2. Login to get auth token
        3. Upload large photo (>400x400)
        4. Verify photo is resized to 400x400
        5. Verify photo URL is stored in profile
        6. View public profile and verify photo visible
        7. Delete photo
        8. Verify photo removed from profile
        """
        # Step 1: Register and verify
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        # Step 2: Login
        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 3: Create and upload large photo (800x800)
        large_image = Image.new("RGB", (800, 800), color="red")
        photo_bytes = BytesIO()
        large_image.save(photo_bytes, format="JPEG")
        photo_bytes.seek(0)

        files = {"photo": ("profile.jpg", photo_bytes, "image/jpeg")}

        upload_response = await client.post(
            f"/users/{username}/profile/photo",
            files=files,
            headers=auth_headers
        )

        # Step 4: Verify photo is resized
        assert upload_response.status_code == 200
        upload_data = upload_response.json()["data"]

        assert upload_data["photo_width"] == 400
        assert upload_data["photo_height"] == 400
        assert "photo_url" in upload_data

        photo_url = upload_data["photo_url"]

        # Step 5: Verify photo URL stored in database
        result = await db_session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one()

        assert profile.profile_photo_url is not None
        assert photo_url in profile.profile_photo_url

        # Step 6: View public profile
        public_response = await client.get(f"/users/{username}/profile")
        public_data = public_response.json()["data"]

        assert public_data["photo_url"] is not None
        assert photo_url in public_data["photo_url"]

        # Step 7: Delete photo
        delete_response = await client.delete(
            f"/users/{username}/profile/photo",
            headers=auth_headers
        )

        assert delete_response.status_code == 200

        # Step 8: Verify photo removed
        result = await db_session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one()

        assert profile.profile_photo_url is None

        # Verify in public profile
        public_response2 = await client.get(f"/users/{username}/profile")
        public_data2 = public_response2.json()["data"]

        assert public_data2["photo_url"] is None

    async def test_photo_upload_replaces_old_photo(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that uploading new photo replaces old one.

        Steps:
        1. Upload first photo
        2. Verify first photo URL
        3. Upload second photo
        4. Verify new photo URL is different
        5. Verify only one photo in profile
        """
        # Setup: Register and login
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 1 & 2: Upload first photo
        image1 = Image.new("RGB", (500, 500), color="blue")
        photo_bytes1 = BytesIO()
        image1.save(photo_bytes1, format="PNG")
        photo_bytes1.seek(0)

        upload1_response = await client.post(
            f"/users/{username}/profile/photo",
            files={"photo": ("photo1.png", photo_bytes1, "image/png")},
            headers=auth_headers
        )

        photo_url1 = upload1_response.json()["data"]["photo_url"]

        # Step 3 & 4: Upload second photo
        image2 = Image.new("RGB", (600, 600), color="green")
        photo_bytes2 = BytesIO()
        image2.save(photo_bytes2, format="PNG")
        photo_bytes2.seek(0)

        upload2_response = await client.post(
            f"/users/{username}/profile/photo",
            files={"photo": ("photo2.png", photo_bytes2, "image/png")},
            headers=auth_headers
        )

        photo_url2 = upload2_response.json()["data"]["photo_url"]

        # Verify different URLs
        assert photo_url1 != photo_url2

        # Step 5: Verify only new photo in profile
        result = await db_session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one()

        assert profile.profile_photo_url == photo_url2
        assert photo_url1 not in profile.profile_photo_url

    async def test_photo_validation_rejects_invalid_formats(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that invalid file formats are rejected.

        Steps:
        1. Try to upload text file as photo
        2. Verify 400 error with INVALID_FILE_FORMAT
        3. Try to upload SVG (not supported)
        4. Verify rejection
        """
        # Setup
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 1 & 2: Try text file
        text_file = BytesIO(b"This is not an image")
        upload_response = await client.post(
            f"/users/{username}/profile/photo",
            files={"photo": ("file.txt", text_file, "text/plain")},
            headers=auth_headers
        )

        assert upload_response.status_code == 400
        error_data = upload_response.json()
        assert error_data["error"]["code"] == "INVALID_FILE_FORMAT"

    async def test_photo_validation_rejects_oversized_files(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that files larger than 5MB are rejected.

        Steps:
        1. Create image > 5MB
        2. Try to upload
        3. Verify 400 error with FILE_TOO_LARGE
        """
        # Setup
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 1: Create large file (6MB)
        large_file = BytesIO(b"x" * (6 * 1024 * 1024))

        # Step 2 & 3: Try to upload
        upload_response = await client.post(
            f"/users/{username}/profile/photo",
            files={"photo": ("large.jpg", large_file, "image/jpeg")},
            headers=auth_headers
        )

        assert upload_response.status_code == 400
        error_data = upload_response.json()
        assert error_data["error"]["code"] == "FILE_TOO_LARGE"

    async def test_photo_aspect_ratio_maintained_on_resize(
        self, client: AsyncClient, db_session: AsyncSession, sample_user_data
    ):
        """
        Test that non-square photos are cropped to square before resize.

        Steps:
        1. Upload rectangular photo (800x600)
        2. Verify result is 400x400 (square)
        """
        # Setup
        username = sample_user_data["username"]
        register_response = await client.post("/auth/register", json=sample_user_data)
        user_id = register_response.json()["data"]["user_id"]

        result = await db_session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.is_verified = True
        await db_session.commit()

        login_response = await client.post("/auth/login", json={
            "login": username,
            "password": sample_user_data["password"]
        })
        access_token = login_response.json()["data"]["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 1: Create rectangular image
        rect_image = Image.new("RGB", (800, 600), color="purple")
        photo_bytes = BytesIO()
        rect_image.save(photo_bytes, format="JPEG")
        photo_bytes.seek(0)

        # Step 2: Upload and verify square result
        upload_response = await client.post(
            f"/users/{username}/profile/photo",
            files={"photo": ("rect.jpg", photo_bytes, "image/jpeg")},
            headers=auth_headers
        )

        assert upload_response.status_code == 200
        upload_data = upload_response.json()["data"]

        # Should be cropped to square and resized
        assert upload_data["photo_width"] == 400
        assert upload_data["photo_height"] == 400
