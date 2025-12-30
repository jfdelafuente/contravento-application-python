"""
Contract tests for Trip Photo API endpoints.

Tests validate that responses conform to the OpenAPI schema in trips-api.yaml.
Follows TDD approach - these tests should FAIL until implementation is complete.

T046-T048: Photo upload, delete, reorder contract tests
Functional Requirements: FR-009, FR-010, FR-011, FR-012, FR-013
"""

import io

import pytest
from httpx import AsyncClient
from PIL import Image


@pytest.mark.contract
@pytest.mark.asyncio
class TestTripPhotoUploadContract:
    """
    T046: Contract tests for POST /trips/{id}/photos.

    Validates photo upload endpoint against OpenAPI spec.
    Functional Requirements: FR-009, FR-010, FR-011
    """

    async def test_upload_photo_success_schema(self, client: AsyncClient, auth_headers: dict):
        """Test uploading photo to trip matches success response schema."""
        # Arrange - Create a trip first
        trip_payload = {
            "title": "Test Trip for Photos",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post("/trips", json=trip_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Create a fake image file
        img = Image.new("RGB", (800, 600), color="red")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act - Upload photo
        response = await client.post(
            f"/trips/{trip_id}/photos",
            files={"photo": ("test.jpg", img_bytes, "image/jpeg")},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 201
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

        # Validate photo data (matches OpenAPI spec: trips-api.yaml lines 354-363)
        photo_data = data["data"]
        assert "id" in photo_data  # Contract uses 'id', not 'photo_id'
        assert "trip_id" in photo_data
        assert photo_data["trip_id"] == trip_id
        assert "photo_url" in photo_data
        assert ".jpg" in photo_data["photo_url"]
        assert "thumb_url" in photo_data
        assert "order" in photo_data

    async def test_upload_photo_invalid_format(self, client: AsyncClient, auth_headers: dict):
        """Test uploading non-image file returns 400 validation error."""
        # Arrange - Create a trip
        trip_payload = {
            "title": "Test Trip",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post("/trips", json=trip_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Create a fake text file
        fake_file = io.BytesIO(b"This is not an image")

        # Act - Try to upload non-image
        response = await client.post(
            f"/trips/{trip_id}/photos",
            files={"photo": ("test.txt", fake_file, "text/plain")},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_upload_photo_trip_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test uploading photo to non-existent trip returns 404."""
        # Arrange
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        img = Image.new("RGB", (800, 600), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act
        response = await client.post(
            f"/trips/{fake_trip_id}/photos",
            files={"photo": ("test.jpg", img_bytes, "image/jpeg")},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    async def test_upload_photo_unauthorized(self, client: AsyncClient):
        """Test uploading photo without auth returns 401."""
        # Arrange
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        img = Image.new("RGB", (800, 600), color="green")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # Act - No auth headers
        response = await client.post(
            f"/trips/{fake_trip_id}/photos",
            files={"photo": ("test.jpg", img_bytes, "image/jpeg")},
        )

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"

    async def test_upload_photo_exceeds_limit(self, client: AsyncClient, auth_headers: dict):
        """Test uploading more than 20 photos returns 400 error."""
        # Arrange - Create trip
        trip_payload = {
            "title": "Test Trip",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post("/trips", json=trip_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Upload 20 photos (max limit)
        for i in range(20):
            img = Image.new("RGB", (800, 600), color="red")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            await client.post(
                f"/trips/{trip_id}/photos",
                files={"photo": (f"test{i}.jpg", img_bytes, "image/jpeg")},
                headers=auth_headers,
            )

        # Act - Try to upload 21st photo
        img = Image.new("RGB", (800, 600), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        response = await client.post(
            f"/trips/{trip_id}/photos",
            files={"photo": ("test21.jpg", img_bytes, "image/jpeg")},
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "20" in data["error"]["message"]


@pytest.mark.contract
@pytest.mark.asyncio
class TestTripPhotoDeleteContract:
    """
    T047: Contract tests for DELETE /trips/{id}/photos/{photo_id}.

    Validates photo deletion endpoint against OpenAPI spec.
    Functional Requirement: FR-013
    """

    async def test_delete_photo_success_schema(self, client: AsyncClient, auth_headers: dict):
        """Test deleting photo from trip matches success response schema."""
        # Arrange - Create trip and upload photo
        trip_payload = {
            "title": "Test Trip",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post("/trips", json=trip_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Upload a photo first
        img = Image.new("RGB", (800, 600), color="blue")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        upload_response = await client.post(
            f"/trips/{trip_id}/photos",
            files={"photo": ("test.jpg", img_bytes, "image/jpeg")},
            headers=auth_headers,
        )
        photo_data = upload_response.json()["data"]
        photo_id = photo_data["id"]  # Contract uses 'id', not 'photo_id'

        # Act - Delete photo
        response = await client.delete(f"/trips/{trip_id}/photos/{photo_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

    async def test_delete_photo_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent photo returns 404."""
        # Arrange - Create trip
        trip_payload = {
            "title": "Test Trip",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post("/trips", json=trip_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]
        fake_photo_id = "00000000-0000-0000-0000-000000000000"

        # Act
        response = await client.delete(
            f"/trips/{trip_id}/photos/{fake_photo_id}", headers=auth_headers
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    async def test_delete_photo_unauthorized(self, client: AsyncClient):
        """Test deleting photo without auth returns 401."""
        # Arrange
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        fake_photo_id = "00000000-0000-0000-0000-000000000000"

        # Act - No auth headers
        response = await client.delete(f"/trips/{fake_trip_id}/photos/{fake_photo_id}")

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.contract
@pytest.mark.asyncio
class TestTripPhotoReorderContract:
    """
    T048: Contract tests for PUT /trips/{id}/photos/reorder.

    Validates photo reordering endpoint against OpenAPI spec.
    Functional Requirement: FR-012
    """

    async def test_reorder_photos_success_schema(self, client: AsyncClient, auth_headers: dict):
        """Test reordering photos matches success response schema."""
        # Arrange - Create trip and upload 3 photos
        trip_payload = {
            "title": "Test Trip",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post("/trips", json=trip_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        photo_ids = []
        for i in range(3):
            img = Image.new("RGB", (800, 600), color=["red", "green", "blue"][i])
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            upload_response = await client.post(
                f"/trips/{trip_id}/photos",
                files={"photo": (f"test{i}.jpg", img_bytes, "image/jpeg")},
                headers=auth_headers,
            )
            photo_ids.append(upload_response.json()["data"]["id"])  # Contract uses 'id'

        # Act - Reorder photos (reverse order)
        reorder_payload = {"photo_order": [photo_ids[2], photo_ids[1], photo_ids[0]]}
        response = await client.put(
            f"/trips/{trip_id}/photos/reorder",
            json=reorder_payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

    async def test_reorder_photos_invalid_photo_ids(self, client: AsyncClient, auth_headers: dict):
        """Test reordering with invalid photo IDs returns 400."""
        # Arrange - Create trip
        trip_payload = {
            "title": "Test Trip",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post("/trips", json=trip_payload, headers=auth_headers)
        trip_id = create_response.json()["data"]["trip_id"]

        # Act - Try to reorder with fake photo IDs
        reorder_payload = {
            "photo_order": [
                "00000000-0000-0000-0000-000000000001",
                "00000000-0000-0000-0000-000000000002",
            ]
        }
        response = await client.put(
            f"/trips/{trip_id}/photos/reorder",
            json=reorder_payload,
            headers=auth_headers,
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_reorder_photos_unauthorized(self, client: AsyncClient):
        """Test reordering photos without auth returns 401."""
        # Arrange
        fake_trip_id = "00000000-0000-0000-0000-000000000000"
        reorder_payload = {"photo_order": []}

        # Act - No auth headers
        response = await client.put(f"/trips/{fake_trip_id}/photos/reorder", json=reorder_payload)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"
