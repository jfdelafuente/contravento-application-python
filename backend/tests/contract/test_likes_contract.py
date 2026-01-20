"""
Contract tests for Likes API (Feature 004 - T009).

Validates that like endpoints responses match the OpenAPI specification
defined in specs/004-social-network/contracts/social-api.yaml
"""

import pytest
from httpx import AsyncClient
from pathlib import Path
import yaml

from src.models.trip import Trip


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
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return spec


@pytest.mark.contract
@pytest.mark.asyncio
async def test_like_trip_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test POST /trips/{trip_id}/like response matches OpenAPI schema (FR-009).

    Contract validation for LikeResponse schema:
    - success: boolean
    - message: string
    - likes_count: integer
    - is_liked: boolean
    """
    trip_id = published_trip_public_user.trip_id

    response = await client.post(f"/trips/{trip_id}/like", headers=auth_headers)

    # Should be 200 (successful like)
    assert response.status_code == 200

    data = response.json()

    # Validate response structure
    assert "success" in data
    assert "message" in data
    assert "likes_count" in data
    assert "is_liked" in data

    # Validate field types
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    assert isinstance(data["likes_count"], int)
    assert isinstance(data["is_liked"], bool)

    # Validate values
    assert data["success"] is True
    assert data["likes_count"] >= 1
    assert data["is_liked"] is True


@pytest.mark.contract
@pytest.mark.asyncio
async def test_unlike_trip_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test DELETE /trips/{trip_id}/like response matches OpenAPI schema (FR-012).

    Contract validation for LikeResponse schema on unlike.
    """
    trip_id = published_trip_public_user.trip_id

    # Like first
    await client.post(f"/trips/{trip_id}/like", headers=auth_headers)

    # Then unlike
    response = await client.delete(f"/trips/{trip_id}/like", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate response structure (same as like)
    assert "success" in data
    assert "message" in data
    assert "likes_count" in data
    assert "is_liked" in data

    # Validate field types
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    assert isinstance(data["likes_count"], int)
    assert isinstance(data["is_liked"], bool)

    # Validate values
    assert data["success"] is True
    assert data["is_liked"] is False


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_likes_response_schema(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """
    Test GET /trips/{trip_id}/likes response matches OpenAPI schema (FR-013).

    Contract validation for LikesListResponse schema:
    - likes: array of LikeSummary objects
    - total_count: integer
    - page: integer
    - limit: integer
    - has_more: boolean
    """
    trip_id = published_trip_public_user.trip_id

    response = await client.get(f"/trips/{trip_id}/likes")

    assert response.status_code == 200

    data = response.json()

    # Validate top-level response structure
    assert "likes" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Validate field types
    assert isinstance(data["likes"], list)
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
async def test_get_trip_likes_item_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test LikeSummary schema in likes list (FR-013).

    Each LikeSummary must include:
    - user: UserSummary object
    - created_at: ISO 8601 datetime
    """
    trip_id = published_trip_public_user.trip_id

    # Add a like first
    await client.post(f"/trips/{trip_id}/like", headers=auth_headers)

    # Get likes list
    response = await client.get(f"/trips/{trip_id}/likes")

    assert response.status_code == 200
    data = response.json()

    # If likes exist, validate first item
    if len(data["likes"]) > 0:
        like = data["likes"][0]

        # Required fields
        assert "user" in like
        assert "created_at" in like

        # Type validation
        assert isinstance(like["user"], dict)
        assert isinstance(like["created_at"], str)

        # Validate user (UserSummary)
        user = like["user"]
        assert "username" in user
        assert "full_name" in user
        assert "profile_photo_url" in user

        assert isinstance(user["username"], str)
        assert user["full_name"] is None or isinstance(user["full_name"], str)
        assert user["profile_photo_url"] is None or isinstance(user["profile_photo_url"], str)

        # Validate created_at format (ISO 8601)
        created_at = like["created_at"]
        assert "T" in created_at  # Date-time separator


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_likes_pagination_params(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """
    Test likes list pagination query parameters.

    Valid params:
    - page: min 1, default 1
    - limit: min 1, max 50, default 20
    """
    trip_id = published_trip_public_user.trip_id

    # Valid pagination
    response = await client.get(f"/trips/{trip_id}/likes?page=1&limit=20")
    assert response.status_code == 200

    # Default values
    response = await client.get(f"/trips/{trip_id}/likes")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_likes_pagination_validation(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test invalid pagination parameters return 422."""
    trip_id = published_trip_public_user.trip_id

    # Invalid page (too small)
    response = await client.get(f"/trips/{trip_id}/likes?page=0")
    assert response.status_code == 422

    # Invalid limit (too small)
    response = await client.get(f"/trips/{trip_id}/likes?limit=0")
    assert response.status_code == 422

    # Invalid limit (too large)
    response = await client.get(f"/trips/{trip_id}/likes?limit=51")
    assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_like_trip_requires_authentication(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test like endpoint requires authentication (401)."""
    trip_id = published_trip_public_user.trip_id

    # No auth headers
    response = await client.post(f"/trips/{trip_id}/like")
    assert response.status_code == 401

    data = response.json()
    assert "error" in data or "detail" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_unlike_trip_requires_authentication(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test unlike endpoint requires authentication (401)."""
    trip_id = published_trip_public_user.trip_id

    # No auth headers
    response = await client.delete(f"/trips/{trip_id}/like")
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_like_nonexistent_trip_returns_404(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test liking non-existent trip returns 404 with ErrorResponse schema."""
    fake_trip_id = "00000000-0000-0000-0000-000000000000"

    response = await client.post(f"/trips/{fake_trip_id}/like", headers=auth_headers)

    assert response.status_code == 404

    data = response.json()

    # Validate ErrorResponse schema
    assert "success" in data or "error" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_unlike_nonexistent_like_returns_404(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test unliking a trip that wasn't liked returns 404."""
    trip_id = published_trip_public_user.trip_id

    # Try to unlike without liking first
    response = await client.delete(f"/trips/{trip_id}/like", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_like_own_trip_returns_400(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test liking own trip returns 400 (FR-011)."""
    # This test assumes we can create a trip as the authenticated user
    # If trip creation isn't implemented yet, skip this test
    pytest.skip("Requires trip creation endpoint")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_duplicate_like_returns_400(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test liking the same trip twice returns 400."""
    trip_id = published_trip_public_user.trip_id

    # First like should succeed
    response = await client.post(f"/trips/{trip_id}/like", headers=auth_headers)
    assert response.status_code == 200

    # Second like should fail
    response = await client.post(f"/trips/{trip_id}/like", headers=auth_headers)
    assert response.status_code == 400

    data = response.json()
    assert "error" in data or "message" in data


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_likes_empty_list_schema(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test empty likes list still matches schema."""
    trip_id = published_trip_public_user.trip_id

    response = await client.get(f"/trips/{trip_id}/likes")

    assert response.status_code == 200
    data = response.json()

    # Should have required fields even if empty
    assert "likes" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Empty likes should be valid list
    if data["total_count"] == 0:
        assert data["likes"] == []
        assert data["has_more"] is False


@pytest.mark.contract
@pytest.mark.asyncio
async def test_like_draft_trip_returns_400(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test liking draft trip returns 400 (only published trips can be liked)."""
    # This test requires draft trip fixture
    pytest.skip("Requires draft trip fixture")
