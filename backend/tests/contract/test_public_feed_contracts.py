"""
Contract tests for Public Trips Feed API (Feature 013 - T024).

Validates that API responses match the OpenAPI specification.
"""

from pathlib import Path

import pytest
import yaml
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import Trip

# Load OpenAPI spec
SPEC_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "specs"
    / "013-public-trips-feed"
    / "contracts"
    / "public-feed-api.yaml"
)


@pytest.fixture(scope="module")
def openapi_spec():
    """Load the OpenAPI specification for public feed endpoints."""
    with open(SPEC_PATH, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return spec


def validate_response_schema(response_data: dict, schema: dict):
    """
    Validate response data against OpenAPI schema.

    Args:
        response_data: Actual API response
        schema: Expected schema from OpenAPI spec

    Raises:
        AssertionError: If response doesn't match schema
    """
    # Get schema properties
    properties = schema.get("properties", {})
    required_fields = schema.get("required", [])

    # Check required fields exist
    for field in required_fields:
        assert field in response_data, f"Missing required field: {field}"

    # Check field types
    for field, field_schema in properties.items():
        if field in response_data:
            value = response_data[field]
            expected_type = field_schema.get("type")

            # Handle nullable fields
            if value is None:
                nullable = (
                    field_schema.get("nullable", False) or field_schema.get("anyOf") is not None
                )
                assert nullable, f"Field {field} is null but not marked as nullable"
                continue

            # Validate type
            if expected_type == "string":
                assert isinstance(value, str), f"Field {field} should be string, got {type(value)}"
            elif expected_type == "integer":
                assert isinstance(value, int), f"Field {field} should be integer, got {type(value)}"
            elif expected_type == "number":
                assert isinstance(
                    value, int | float
                ), f"Field {field} should be number, got {type(value)}"
            elif expected_type == "boolean":
                assert isinstance(
                    value, bool
                ), f"Field {field} should be boolean, got {type(value)}"
            elif expected_type == "array":
                assert isinstance(value, list), f"Field {field} should be array, got {type(value)}"
            elif expected_type == "object":
                assert isinstance(value, dict), f"Field {field} should be object, got {type(value)}"


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_response_schema(
    client: AsyncClient,
    openapi_spec: dict,
    published_trip_public_user: Trip,
):
    """Test that GET /trips/public response matches OpenAPI schema."""
    response = await client.get("/trips/public?page=1&limit=20")

    assert response.status_code == 200

    data = response.json()

    # Validate top-level response structure
    assert "trips" in data
    assert "pagination" in data
    assert isinstance(data["trips"], list)
    assert isinstance(data["pagination"], dict)

    # Validate pagination structure
    pagination = data["pagination"]
    assert "page" in pagination
    assert "limit" in pagination
    assert "total" in pagination
    assert "total_pages" in pagination

    # Validate trips array (if not empty)
    if len(data["trips"]) > 0:
        trip = data["trips"][0]

        # Required trip fields
        assert "trip_id" in trip
        assert "title" in trip
        assert "start_date" in trip
        assert "distance_km" in trip
        assert "author" in trip
        assert "published_at" in trip
        assert "photo" in trip  # Can be null
        assert "location" in trip  # Can be null

        # Validate author structure
        author = trip["author"]
        assert "user_id" in author
        assert "username" in author
        assert "profile_photo_url" in author

        # Validate photo structure (if present)
        if trip["photo"] is not None:
            photo = trip["photo"]
            assert "photo_url" in photo
            assert "thumbnail_url" in photo

        # Validate location structure (if present)
        if trip["location"] is not None:
            location = trip["location"]
            assert "name" in location


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_pagination_info_structure(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test pagination info contains all required fields with correct types."""
    response = await client.get("/trips/public?page=1&limit=20")

    assert response.status_code == 200
    data = response.json()

    pagination = data["pagination"]

    # Required fields
    assert "total" in pagination
    assert "page" in pagination
    assert "limit" in pagination
    assert "total_pages" in pagination

    # Correct types
    assert isinstance(pagination["total"], int)
    assert isinstance(pagination["page"], int)
    assert isinstance(pagination["limit"], int)
    assert isinstance(pagination["total_pages"], int)

    # Valid values
    assert pagination["total"] >= 0
    assert pagination["page"] >= 1
    assert pagination["limit"] >= 1
    assert pagination["total_pages"] >= 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_trip_summary_structure(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test trip summary contains all required fields with correct types."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Should have at least one trip
    assert len(data["trips"]) > 0

    trip = data["trips"][0]

    # Required fields
    assert "trip_id" in trip
    assert "title" in trip
    assert "start_date" in trip
    assert "distance_km" in trip
    assert "photo" in trip  # Can be null
    assert "location" in trip  # Can be null
    assert "author" in trip
    assert "published_at" in trip

    # Correct types
    assert isinstance(trip["trip_id"], str)
    assert isinstance(trip["title"], str)
    assert isinstance(trip["start_date"], str)
    assert trip["distance_km"] is None or isinstance(trip["distance_km"], int | float)
    assert trip["photo"] is None or isinstance(trip["photo"], dict)
    assert trip["location"] is None or isinstance(trip["location"], dict)
    assert isinstance(trip["author"], dict)
    assert isinstance(trip["published_at"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_author_structure(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test author info contains all required fields with correct types."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Should have at least one trip
    assert len(data["trips"]) > 0

    author = data["trips"][0]["author"]

    # Required fields
    assert "user_id" in author
    assert "username" in author
    assert "profile_photo_url" in author  # Can be null

    # Correct types
    assert isinstance(author["user_id"], str)
    assert isinstance(author["username"], str)
    assert author["profile_photo_url"] is None or isinstance(author["profile_photo_url"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_photo_structure(
    client: AsyncClient,
    published_trip_with_photos: Trip,
):
    """Test photo info contains all required fields with correct types."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Find trip with photos
    trip_with_photo = next(
        (t for t in data["trips"] if t["photo"] is not None),
        None,
    )

    assert trip_with_photo is not None, "No trip with photo found in response"

    photo = trip_with_photo["photo"]

    # Required fields
    assert "photo_url" in photo
    assert "thumbnail_url" in photo

    # Correct types
    assert isinstance(photo["photo_url"], str)
    assert isinstance(photo["thumbnail_url"], str)

    # URL format (should start with /)
    assert photo["photo_url"].startswith("/")
    assert photo["thumbnail_url"].startswith("/")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_location_structure(
    client: AsyncClient,
    published_trip_with_location: Trip,
):
    """Test location info contains all required fields with correct types."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Find trip with location
    trip_with_location = next(
        (t for t in data["trips"] if t["location"] is not None),
        None,
    )

    assert trip_with_location is not None, "No trip with location found in response"

    location = trip_with_location["location"]

    # Required fields
    assert "name" in location

    # Correct types
    assert isinstance(location["name"], str)
    assert len(location["name"]) > 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_date_format(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test that dates follow ISO 8601 format."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    assert len(data["trips"]) > 0

    trip = data["trips"][0]

    # start_date should be YYYY-MM-DD
    start_date = trip["start_date"]
    assert len(start_date) == 10
    assert start_date[4] == "-"
    assert start_date[7] == "-"

    # published_at should be ISO 8601 with timezone
    published_at = trip["published_at"]
    assert "T" in published_at  # Date-time separator
    # Should contain timezone info (Z or +/-)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_query_params_validation(client: AsyncClient):
    """Test that invalid query params return proper error response."""
    # Invalid page (too small)
    response = await client.get("/trips/public?page=0&limit=20")
    assert response.status_code in [400, 422]

    # Invalid limit (too large)
    response = await client.get("/trips/public?page=1&limit=51")
    assert response.status_code in [400, 422]

    # Invalid limit (too small)
    response = await client.get("/trips/public?page=1&limit=0")
    assert response.status_code in [400, 422]


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_public_trips_empty_response_schema(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """Test that empty feed response still matches schema."""
    # Delete all trips
    from sqlalchemy import delete

    await db_session.execute(delete(Trip))
    await db_session.commit()

    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Should still have trips and pagination
    assert "trips" in data
    assert "pagination" in data

    # Trips should be empty list
    assert data["trips"] == []
    assert isinstance(data["trips"], list)

    # Pagination should still be valid
    pagination = data["pagination"]
    assert pagination["total"] == 0
    assert pagination["page"] == 1
    assert pagination["total_pages"] == 0
