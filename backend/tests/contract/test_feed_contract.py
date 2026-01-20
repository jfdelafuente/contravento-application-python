"""
Contract tests for Feed API (Feature 004 - T008).

Validates that feed endpoint responses match the OpenAPI specification
defined in specs/004-social-network/contracts/social-api.yaml
"""

from pathlib import Path

import pytest
import yaml
from httpx import AsyncClient

# Load OpenAPI spec
SPEC_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "specs"
    / "004-social-network"
    / "contracts"
    / "social-api.yaml"
)


@pytest.fixture(scope="module")
def openapi_spec():
    """Load the OpenAPI specification for social network endpoints."""
    with open(SPEC_PATH, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return spec


def get_schema_from_spec(spec: dict, path: str, method: str, response_code: str = "200"):
    """
    Extract response schema from OpenAPI spec.

    Args:
        spec: OpenAPI specification dict
        path: API path (e.g., "/feed")
        method: HTTP method (e.g., "get")
        response_code: Response status code (default "200")

    Returns:
        Schema dict or None if not found
    """
    try:
        response_schema = spec["paths"][path][method]["responses"][response_code]["content"][
            "application/json"
        ]["schema"]

        # Resolve $ref if present
        if "$ref" in response_schema:
            ref_path = response_schema["$ref"].split("/")
            schema = spec
            for part in ref_path[1:]:  # Skip "#"
                schema = schema[part]
            return schema

        return response_schema
    except (KeyError, TypeError):
        return None


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    openapi_spec: dict,
):
    """
    Test GET /feed response matches OpenAPI schema (FR-001).

    Contract validation for FeedResponse schema:
    - trips: array of FeedItem objects
    - total_count: integer
    - page: integer
    - limit: integer
    - has_more: boolean
    """
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate top-level response structure
    assert "trips" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Validate field types
    assert isinstance(data["trips"], list)
    assert isinstance(data["total_count"], int)
    assert isinstance(data["page"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["has_more"], bool)

    # Validate values
    assert data["total_count"] >= 0
    assert data["page"] >= 1
    assert data["limit"] >= 1
    assert data["limit"] <= 50


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_item_schema(
    client: AsyncClient,
    auth_headers: dict,
    openapi_spec: dict,
):
    """
    Test FeedItem schema in feed response (FR-001).

    Each FeedItem must include:
    - trip_id, title, description, author
    - photos, distance_km, start_date, end_date
    - locations, tags
    - likes_count, comments_count, shares_count
    - is_liked_by_me
    - created_at
    """
    response = await client.get("/feed?limit=10", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # If feed has items, validate first item structure
    if len(data["trips"]) > 0:
        item = data["trips"][0]

        # Required fields
        required_fields = [
            "trip_id",
            "title",
            "description",
            "author",
            "photos",
            "distance_km",
            "start_date",
            "end_date",
            "locations",
            "tags",
            "likes_count",
            "comments_count",
            "shares_count",
            "is_liked_by_me",
            "created_at",
        ]

        for field in required_fields:
            assert field in item, f"Missing required field: {field}"

        # Type validation
        assert isinstance(item["trip_id"], str)
        assert isinstance(item["title"], str)
        assert isinstance(item["description"], str)
        assert isinstance(item["author"], dict)
        assert isinstance(item["photos"], list)
        assert item["distance_km"] is None or isinstance(item["distance_km"], int | float)
        assert isinstance(item["start_date"], str)
        assert item["end_date"] is None or isinstance(item["end_date"], str)
        assert isinstance(item["locations"], list)
        assert isinstance(item["tags"], list)
        assert isinstance(item["likes_count"], int)
        assert isinstance(item["comments_count"], int)
        assert isinstance(item["shares_count"], int)
        assert isinstance(item["is_liked_by_me"], bool)
        assert isinstance(item["created_at"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_author_structure(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test author (UserSummary) structure in feed items."""
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    if len(data["trips"]) > 0:
        author = data["trips"][0]["author"]

        # Required fields
        assert "username" in author
        assert "full_name" in author
        assert "profile_photo_url" in author

        # Type validation
        assert isinstance(author["username"], str)
        assert author["full_name"] is None or isinstance(author["full_name"], str)
        assert author["profile_photo_url"] is None or isinstance(author["profile_photo_url"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_photo_structure(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test photo (PhotoSummary) structure in feed items."""
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Find item with photos
    item_with_photos = next(
        (item for item in data["trips"] if len(item["photos"]) > 0),
        None,
    )

    if item_with_photos:
        photo = item_with_photos["photos"][0]

        # Required fields
        assert "photo_url" in photo
        assert "caption" in photo

        # Type validation
        assert isinstance(photo["photo_url"], str)
        assert photo["caption"] is None or isinstance(photo["caption"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_location_structure(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test location (LocationSummary) structure in feed items."""
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Find item with locations
    item_with_locations = next(
        (item for item in data["trips"] if len(item["locations"]) > 0),
        None,
    )

    if item_with_locations:
        location = item_with_locations["locations"][0]

        # Required fields
        assert "name" in location
        assert "latitude" in location
        assert "longitude" in location

        # Type validation
        assert isinstance(location["name"], str)
        assert location["latitude"] is None or isinstance(location["latitude"], int | float)
        assert location["longitude"] is None or isinstance(location["longitude"], int | float)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_tag_structure(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test tag (TagSummary) structure in feed items."""
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Find item with tags
    item_with_tags = next(
        (item for item in data["trips"] if len(item["tags"]) > 0),
        None,
    )

    if item_with_tags:
        tag = item_with_tags["tags"][0]

        # Required fields
        assert "name" in tag
        assert "normalized" in tag

        # Type validation
        assert isinstance(tag["name"], str)
        assert isinstance(tag["normalized"], str)


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_pagination_params(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test feed pagination query parameters (FR-003).

    Valid params:
    - page: min 1, default 1
    - limit: min 1, max 50, default 10
    """
    # Valid pagination
    response = await client.get("/feed?page=1&limit=10", headers=auth_headers)
    assert response.status_code == 200

    # Default values
    response = await client.get("/feed", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 10

    # Custom values
    response = await client.get("/feed?page=2&limit=20", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 20


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_pagination_validation(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test invalid pagination parameters return 422."""
    # Invalid page (too small)
    response = await client.get("/feed?page=0", headers=auth_headers)
    assert response.status_code == 422

    # Invalid limit (too small)
    response = await client.get("/feed?limit=0", headers=auth_headers)
    assert response.status_code == 422

    # Invalid limit (too large)
    response = await client.get("/feed?limit=51", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_empty_response_schema(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test empty feed response still matches schema."""
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Should have required fields even if empty
    assert "trips" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Empty trips should be valid list
    if data["total_count"] == 0:
        assert data["trips"] == []
        assert data["has_more"] is False


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_requires_authentication(client: AsyncClient):
    """Test feed endpoint requires authentication (401)."""
    # No auth headers
    response = await client.get("/feed")
    assert response.status_code == 401

    data = response.json()
    assert "error" in data or "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_feed_date_formats(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test date formats in feed items follow ISO 8601."""
    response = await client.get("/feed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    if len(data["trips"]) > 0:
        item = data["trips"][0]

        # start_date should be YYYY-MM-DD
        start_date = item["start_date"]
        assert len(start_date) == 10
        assert start_date[4] == "-"
        assert start_date[7] == "-"

        # end_date (if present) should be YYYY-MM-DD
        if item["end_date"]:
            end_date = item["end_date"]
            assert len(end_date) == 10
            assert end_date[4] == "-"
            assert end_date[7] == "-"

        # created_at should be ISO 8601 with timezone
        created_at = item["created_at"]
        assert "T" in created_at  # Date-time separator
