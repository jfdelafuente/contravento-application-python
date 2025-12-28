"""
Contract tests for Trip API endpoints.

Tests validate that responses conform to the OpenAPI schema in trips-api.yaml.
Follows TDD approach - these tests should FAIL until implementation is complete.
"""

import pytest
from httpx import AsyncClient
from pathlib import Path
import yaml
from datetime import date, datetime


@pytest.fixture(scope="module")
def openapi_spec():
    """Load the OpenAPI specification for trip endpoints."""
    spec_path = (
        Path(__file__).parents[3]
        / "specs"
        / "002-travel-diary"
        / "contracts"
        / "trips-api.yaml"
    )
    with open(spec_path, "r", encoding="utf-8") as f:
        spec_dict = yaml.safe_load(f)
    return spec_dict


@pytest.mark.contract
@pytest.mark.asyncio
class TestTripCreateContract:
    """
    T026: Contract tests for POST /trips.

    Validates trip creation endpoint against OpenAPI spec.
    Functional Requirements: FR-001, FR-002, FR-003
    """

    async def test_create_trip_minimal_success_schema(
        self, client: AsyncClient, auth_headers: dict, openapi_spec
    ):
        """Test creating minimal trip matches success response schema."""
        # Arrange
        payload = {
            "title": "Vía Verde del Aceite",
            "description": "Un recorrido precioso entre olivos centenarios...",
            "start_date": "2024-05-15",
        }

        # Act
        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert - Response structure
        assert response.status_code == 201
        data = response.json()

        # Validate standardized API response format
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

        # Validate trip data structure
        trip = data["data"]
        assert "trip_id" in trip
        assert trip["user_id"] is not None
        assert trip["title"] == payload["title"]
        assert trip["description"] == payload["description"]
        assert trip["start_date"] == payload["start_date"]
        assert trip["status"] == "draft"

        # Optional fields should be null
        assert trip["end_date"] is None
        assert trip["distance_km"] is None
        assert trip["difficulty"] is None

        # Metadata fields
        assert "created_at" in trip
        assert "updated_at" in trip
        assert trip["published_at"] is None

        # Related entities
        assert trip["photos"] == []
        assert trip["locations"] == []
        assert trip["tags"] == []

    async def test_create_trip_complete_success_schema(
        self, client: AsyncClient, auth_headers: dict, openapi_spec
    ):
        """Test creating complete trip with all fields matches schema."""
        # Arrange
        payload = {
            "title": "Transpirenaica en bikepacking",
            "description": "<p>Increíble aventura cruzando los Pirineos...</p>",
            "start_date": "2024-07-01",
            "end_date": "2024-07-15",
            "distance_km": 850.5,
            "difficulty": "very_difficult",
            "locations": [
                {"name": "Hendaya", "country": "Francia"},
                {"name": "Llansa", "country": "España"},
            ],
            "tags": ["bikepacking", "pirineos", "larga distancia"],
        }

        # Act
        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        trip = data["data"]

        # Validate all provided fields
        assert trip["title"] == payload["title"]
        assert trip["description"] == payload["description"]
        assert trip["start_date"] == payload["start_date"]
        assert trip["end_date"] == payload["end_date"]
        assert trip["distance_km"] == payload["distance_km"]
        assert trip["difficulty"] == payload["difficulty"]

        # Locations should be created
        assert len(trip["locations"]) == 2
        assert trip["locations"][0]["name"] == "Hendaya"
        assert trip["locations"][0]["sequence"] == 0
        assert trip["locations"][1]["name"] == "Llansa"
        assert trip["locations"][1]["sequence"] == 1

        # Tags should be created
        assert len(trip["tags"]) == 3
        tag_names = [tag["name"] for tag in trip["tags"]]
        assert "bikepacking" in tag_names
        assert "pirineos" in tag_names

    async def test_create_trip_unauthorized_schema(self, client: AsyncClient):
        """Test creating trip without auth returns 401 with error schema."""
        # Arrange
        payload = {
            "title": "Test Trip",
            "description": "Test description",
            "start_date": "2024-05-15",
        }

        # Act - No auth_headers
        response = await client.post("/trips", json=payload)

        # Assert
        assert response.status_code == 401
        data = response.json()

        # Validate error response structure
        assert data["success"] is False
        assert data["data"] is None
        assert data["error"] is not None

        error = data["error"]
        assert error["code"] == "UNAUTHORIZED"
        assert "autenticación" in error["message"].lower()

    async def test_create_trip_validation_error_missing_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating trip without title returns 400 validation error."""
        # Arrange
        payload = {
            "description": "Test description",
            "start_date": "2024-05-15",
        }

        # Act
        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"] is not None
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_create_trip_validation_error_future_date(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating trip with future start_date returns 400."""
        # Arrange
        from datetime import timedelta
        future_date = (date.today() + timedelta(days=30)).isoformat()

        payload = {
            "title": "Future Trip",
            "description": "This should fail",
            "start_date": future_date,
        }

        # Act
        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "futura" in data["error"]["message"].lower()

    async def test_create_trip_validation_error_end_before_start(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating trip with end_date before start_date returns 400."""
        # Arrange
        payload = {
            "title": "Invalid Dates",
            "description": "End date is before start date",
            "start_date": "2024-05-15",
            "end_date": "2024-05-10",  # Before start_date
        }

        # Act
        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert "fin" in data["error"]["message"].lower()

    async def test_create_trip_validation_error_invalid_difficulty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating trip with invalid difficulty returns 400."""
        # Arrange
        payload = {
            "title": "Test Trip",
            "description": "Test description",
            "start_date": "2024-05-15",
            "difficulty": "super_extreme",  # Invalid value
        }

        # Act
        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_create_trip_validation_error_too_many_tags(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test creating trip with more than 10 tags returns 400."""
        # Arrange
        payload = {
            "title": "Test Trip",
            "description": "Test description",
            "start_date": "2024-05-15",
            "tags": [f"tag{i}" for i in range(15)],  # 15 tags > max 10
        }

        # Act
        response = await client.post("/trips", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.contract
@pytest.mark.asyncio
class TestTripPublishContract:
    """
    T027: Contract tests for POST /trips/{trip_id}/publish.

    Validates trip publication endpoint against OpenAPI spec.
    Functional Requirements: FR-007
    """

    async def test_publish_trip_success_schema(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test publishing valid draft trip returns 200 with published status."""
        # Arrange - Create a draft trip first
        create_payload = {
            "title": "Test Trip for Publishing",
            "description": "A" * 60,  # >=50 chars required for publishing
            "start_date": "2024-05-15",
        }
        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Act - Publish the trip
        response = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

        # Validate published trip data
        trip = data["data"]
        assert trip["trip_id"] == trip_id
        assert trip["status"] == "published"
        assert trip["published_at"] is not None

    async def test_publish_trip_validation_error_short_description(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test publishing trip with short description returns 400."""
        # Arrange - Create trip with short description
        create_payload = {
            "title": "Test Trip",
            "description": "Too short",  # < 50 chars
            "start_date": "2024-05-15",
        }
        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Act - Try to publish
        response = await client.post(
            f"/trips/{trip_id}/publish", headers=auth_headers
        )

        # Assert
        assert response.status_code == 400
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "descripción" in data["error"]["message"].lower()
        assert "50" in data["error"]["message"]

    async def test_publish_trip_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test publishing non-existent trip returns 404."""
        # Arrange
        fake_trip_id = "00000000-0000-0000-0000-000000000000"

        # Act
        response = await client.post(
            f"/trips/{fake_trip_id}/publish", headers=auth_headers
        )

        # Assert
        assert response.status_code == 404
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"

    async def test_publish_trip_unauthorized(self, client: AsyncClient):
        """Test publishing trip without auth returns 401."""
        # Arrange
        fake_trip_id = "00000000-0000-0000-0000-000000000000"

        # Act - No auth_headers
        response = await client.post(f"/trips/{fake_trip_id}/publish")

        # Assert
        assert response.status_code == 401
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.contract
@pytest.mark.asyncio
class TestTripGetContract:
    """
    T028: Contract tests for GET /trips/{trip_id}.

    Validates trip retrieval endpoint against OpenAPI spec.
    Functional Requirements: FR-007, FR-008
    """

    async def test_get_trip_success_schema(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting trip by ID returns 200 with complete trip data."""
        # Arrange - Create a trip first
        create_payload = {
            "title": "Vía Verde del Aceite",
            "description": "<p>Ruta espectacular...</p>",
            "start_date": "2024-05-15",
            "end_date": "2024-05-17",
            "distance_km": 127.3,
            "difficulty": "moderate",
            "locations": [
                {"name": "Jaén", "country": "España"},
                {"name": "Baeza", "country": "España"},
            ],
            "tags": ["vías verdes", "andalucía"],
        }
        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Act
        response = await client.get(f"/trips/{trip_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert data["success"] is True
        assert data["data"] is not None
        assert data["error"] is None

        # Validate trip data matches creation
        trip = data["data"]
        assert trip["trip_id"] == trip_id
        assert trip["title"] == create_payload["title"]
        assert trip["description"] == create_payload["description"]
        assert trip["start_date"] == create_payload["start_date"]
        assert trip["end_date"] == create_payload["end_date"]
        assert trip["distance_km"] == create_payload["distance_km"]
        assert trip["difficulty"] == create_payload["difficulty"]

        # Validate nested entities
        assert len(trip["locations"]) == 2
        assert len(trip["tags"]) == 2

    async def test_get_trip_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test getting non-existent trip returns 404."""
        # Arrange
        fake_trip_id = "00000000-0000-0000-0000-000000000000"

        # Act
        response = await client.get(f"/trips/{fake_trip_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 404
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"
        assert "viaje" in data["error"]["message"].lower()

    async def test_get_draft_trip_as_owner(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test owner can view their own draft trip."""
        # Arrange - Create draft trip
        create_payload = {
            "title": "My Draft Trip",
            "description": "This is a draft",
            "start_date": "2024-05-15",
        }
        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Act
        response = await client.get(f"/trips/{trip_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "draft"

    async def test_get_published_trip_public_access(self, client: AsyncClient, auth_headers: dict):
        """Test published trip can be viewed without authentication (future feature)."""
        # Arrange - Create and publish trip
        create_payload = {
            "title": "Public Trip",
            "description": "A" * 60,
            "start_date": "2024-05-15",
        }
        create_response = await client.post(
            "/trips", json=create_payload, headers=auth_headers
        )
        trip_id = create_response.json()["data"]["trip_id"]

        # Publish it
        await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)

        # Act - Get without auth (this test documents future public access)
        # For now, we expect this to work with auth (implementation will determine behavior)
        response = await client.get(f"/trips/{trip_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "published"
