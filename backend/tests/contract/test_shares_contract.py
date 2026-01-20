"""
Contract tests for Shares API (Feature 004 - T011).

Validates that share endpoints responses match the OpenAPI specification
defined in specs/004-social-network/contracts/social-api.yaml
"""

from pathlib import Path

import pytest
import yaml
from httpx import AsyncClient

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
    with open(SPEC_PATH, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return spec


@pytest.mark.contract
@pytest.mark.asyncio
async def test_share_trip_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test POST /trips/{trip_id}/share response matches OpenAPI schema (FR-023).

    Contract validation for ShareResponse schema:
    - success: boolean
    - message: string
    - share_id: string (UUID)
    - shares_count: integer
    """
    trip_id = published_trip_public_user.trip_id

    share_data = {"comment": "Esta ruta es perfecta para iniciarse en bikepacking"}

    response = await client.post(
        f"/trips/{trip_id}/share",
        headers=auth_headers,
        json=share_data,
    )

    assert response.status_code == 201

    data = response.json()

    # Validate response structure
    assert "success" in data
    assert "message" in data
    assert "share_id" in data
    assert "shares_count" in data

    # Validate field types
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    assert isinstance(data["share_id"], str)
    assert isinstance(data["shares_count"], int)

    # Validate values
    assert data["success"] is True
    assert data["shares_count"] >= 1


@pytest.mark.contract
@pytest.mark.asyncio
async def test_share_trip_without_comment_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test sharing trip without optional comment (FR-023).

    Comment is optional (0-200 chars).
    """
    trip_id = published_trip_public_user.trip_id

    # No comment in request body
    response = await client.post(
        f"/trips/{trip_id}/share",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 201

    data = response.json()

    # Should still return valid ShareResponse
    assert "success" in data
    assert "share_id" in data
    assert data["success"] is True


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_shares_response_schema(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """
    Test GET /trips/{trip_id}/shares response matches OpenAPI schema (FR-025).

    Contract validation for SharesListResponse schema:
    - shares: array of ShareSummary objects
    - total_count: integer
    - page: integer
    - limit: integer
    - has_more: boolean
    """
    trip_id = published_trip_public_user.trip_id

    response = await client.get(f"/trips/{trip_id}/shares")

    assert response.status_code == 200

    data = response.json()

    # Validate top-level response structure
    assert "shares" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Validate field types
    assert isinstance(data["shares"], list)
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
async def test_get_trip_shares_item_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test ShareSummary schema in shares list (FR-025).

    Each ShareSummary must include:
    - user: UserSummary object
    - comment: string (nullable)
    - created_at: ISO 8601 datetime
    """
    trip_id = published_trip_public_user.trip_id

    # Add a share first
    share_data = {"comment": "Test share comment"}
    await client.post(
        f"/trips/{trip_id}/share",
        headers=auth_headers,
        json=share_data,
    )

    # Get shares list
    response = await client.get(f"/trips/{trip_id}/shares")

    assert response.status_code == 200
    data = response.json()

    # If shares exist, validate first item
    if len(data["shares"]) > 0:
        share = data["shares"][0]

        # Required fields
        assert "user" in share
        assert "comment" in share
        assert "created_at" in share

        # Type validation
        assert isinstance(share["user"], dict)
        assert share["comment"] is None or isinstance(share["comment"], str)
        assert isinstance(share["created_at"], str)

        # Validate user (UserSummary)
        user = share["user"]
        assert "username" in user
        assert "full_name" in user
        assert "profile_photo_url" in user

        assert isinstance(user["username"], str)
        assert user["full_name"] is None or isinstance(user["full_name"], str)
        assert user["profile_photo_url"] is None or isinstance(user["profile_photo_url"], str)

        # Validate created_at format (ISO 8601)
        created_at = share["created_at"]
        assert "T" in created_at  # Date-time separator


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_shares_pagination_params(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """
    Test shares list pagination query parameters.

    Valid params:
    - page: min 1, default 1
    - limit: min 1, max 50, default 20
    """
    trip_id = published_trip_public_user.trip_id

    # Valid pagination
    response = await client.get(f"/trips/{trip_id}/shares?page=1&limit=20")
    assert response.status_code == 200

    # Default values
    response = await client.get(f"/trips/{trip_id}/shares")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_shares_pagination_validation(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test invalid pagination parameters return 422."""
    trip_id = published_trip_public_user.trip_id

    # Invalid page
    response = await client.get(f"/trips/{trip_id}/shares?page=0")
    assert response.status_code == 422

    # Invalid limit (too small)
    response = await client.get(f"/trips/{trip_id}/shares?limit=0")
    assert response.status_code == 422

    # Invalid limit (too large)
    response = await client.get(f"/trips/{trip_id}/shares?limit=51")
    assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_share_trip_requires_authentication(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test share endpoint requires authentication (401)."""
    trip_id = published_trip_public_user.trip_id

    # No auth headers
    response = await client.post(
        f"/trips/{trip_id}/share",
        json={"comment": "Test"},
    )
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_share_trip_validation_comment_too_long(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test share with comment over 200 chars returns 400 (FR-024)."""
    trip_id = published_trip_public_user.trip_id

    # 201 characters
    long_comment = "a" * 201

    response = await client.post(
        f"/trips/{trip_id}/share",
        headers=auth_headers,
        json={"comment": long_comment},
    )
    assert response.status_code == 400


@pytest.mark.contract
@pytest.mark.asyncio
async def test_share_nonexistent_trip_returns_404(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test sharing non-existent trip returns 404."""
    fake_trip_id = "00000000-0000-0000-0000-000000000000"

    response = await client.post(
        f"/trips/{fake_trip_id}/share",
        headers=auth_headers,
        json={"comment": "Test"},
    )

    assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_shares_empty_list_schema(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test empty shares list still matches schema."""
    trip_id = published_trip_public_user.trip_id

    response = await client.get(f"/trips/{trip_id}/shares")

    assert response.status_code == 200
    data = response.json()

    # Should have required fields even if empty
    assert "shares" in data
    assert "total_count" in data

    # Empty shares should be valid list
    if data["total_count"] == 0:
        assert data["shares"] == []
        assert data["has_more"] is False


@pytest.mark.contract
@pytest.mark.asyncio
async def test_share_draft_trip_returns_400(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test sharing draft trip returns 400 (only published trips can be shared)."""
    # This test requires draft trip fixture
    pytest.skip("Requires draft trip fixture")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_nonexistent_trip_shares_returns_404(
    client: AsyncClient,
):
    """Test getting shares for non-existent trip returns 404."""
    fake_trip_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(f"/trips/{fake_trip_id}/shares")

    assert response.status_code == 404
