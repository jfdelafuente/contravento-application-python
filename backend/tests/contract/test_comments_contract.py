"""
Contract tests for Comments API (Feature 004 - T010).

Validates that comment endpoints responses match the OpenAPI specification
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
async def test_add_comment_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test POST /trips/{trip_id}/comments response matches OpenAPI schema (FR-016).

    Contract validation for CommentResponse schema:
    - comment_id: string (UUID)
    - trip_id: string (UUID)
    - author: UserSummary object
    - content: string
    - created_at: ISO 8601 datetime
    - updated_at: ISO 8601 datetime (nullable)
    - is_edited: boolean
    """
    trip_id = published_trip_public_user.trip_id

    comment_data = {"content": "¡Increíble ruta! Me encantaría hacerla algún día."}

    response = await client.post(
        f"/trips/{trip_id}/comments",
        headers=auth_headers,
        json=comment_data,
    )

    assert response.status_code == 201

    data = response.json()

    # Validate response structure
    assert "comment_id" in data
    assert "trip_id" in data
    assert "author" in data
    assert "content" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "is_edited" in data

    # Validate field types
    assert isinstance(data["comment_id"], str)
    assert isinstance(data["trip_id"], str)
    assert isinstance(data["author"], dict)
    assert isinstance(data["content"], str)
    assert isinstance(data["created_at"], str)
    assert data["updated_at"] is None or isinstance(data["updated_at"], str)
    assert isinstance(data["is_edited"], bool)

    # Validate values
    assert data["trip_id"] == trip_id
    assert data["content"] == comment_data["content"]
    assert data["is_edited"] is False  # New comment not edited


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_comments_response_schema(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """
    Test GET /trips/{trip_id}/comments response matches OpenAPI schema (FR-017).

    Contract validation for CommentsListResponse schema:
    - comments: array of CommentResponse objects
    - total_count: integer
    - page: integer
    - limit: integer
    - has_more: boolean
    """
    trip_id = published_trip_public_user.trip_id

    response = await client.get(f"/trips/{trip_id}/comments")

    assert response.status_code == 200

    data = response.json()

    # Validate top-level response structure
    assert "comments" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Validate field types
    assert isinstance(data["comments"], list)
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
async def test_get_trip_comments_item_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test CommentResponse schema in comments list (FR-017)."""
    trip_id = published_trip_public_user.trip_id

    # Add a comment first
    comment_data = {"content": "Test comment for schema validation"}
    await client.post(
        f"/trips/{trip_id}/comments",
        headers=auth_headers,
        json=comment_data,
    )

    # Get comments list
    response = await client.get(f"/trips/{trip_id}/comments")

    assert response.status_code == 200
    data = response.json()

    # If comments exist, validate first item
    if len(data["comments"]) > 0:
        comment = data["comments"][0]

        # Required fields
        assert "comment_id" in comment
        assert "trip_id" in comment
        assert "author" in comment
        assert "content" in comment
        assert "created_at" in comment
        assert "updated_at" in comment
        assert "is_edited" in comment

        # Type validation
        assert isinstance(comment["comment_id"], str)
        assert isinstance(comment["trip_id"], str)
        assert isinstance(comment["author"], dict)
        assert isinstance(comment["content"], str)
        assert isinstance(comment["created_at"], str)
        assert comment["updated_at"] is None or isinstance(comment["updated_at"], str)
        assert isinstance(comment["is_edited"], bool)

        # Validate author (UserSummary)
        author = comment["author"]
        assert "username" in author
        assert "full_name" in author
        assert "profile_photo_url" in author


@pytest.mark.contract
@pytest.mark.asyncio
async def test_edit_comment_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test PUT /trips/{trip_id}/comments/{comment_id} response matches schema (FR-019).

    Should return CommentResponse with is_edited=true and updated_at set.
    """
    trip_id = published_trip_public_user.trip_id

    # Create comment
    create_response = await client.post(
        f"/trips/{trip_id}/comments",
        headers=auth_headers,
        json={"content": "Original comment"},
    )
    comment_id = create_response.json()["comment_id"]

    # Edit comment
    edit_data = {"content": "Edited comment content"}
    response = await client.put(
        f"/trips/{trip_id}/comments/{comment_id}",
        headers=auth_headers,
        json=edit_data,
    )

    assert response.status_code == 200

    data = response.json()

    # Validate response structure (same as create)
    assert "comment_id" in data
    assert "content" in data
    assert "is_edited" in data
    assert "updated_at" in data

    # Validate values
    assert data["comment_id"] == comment_id
    assert data["content"] == edit_data["content"]
    assert data["is_edited"] is True  # Should be marked as edited
    assert data["updated_at"] is not None  # Should have timestamp


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_comment_response_schema(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """
    Test DELETE /trips/{trip_id}/comments/{comment_id} response matches schema (FR-020).

    Should return success message.
    """
    trip_id = published_trip_public_user.trip_id

    # Create comment
    create_response = await client.post(
        f"/trips/{trip_id}/comments",
        headers=auth_headers,
        json={"content": "Comment to delete"},
    )
    comment_id = create_response.json()["comment_id"]

    # Delete comment
    response = await client.delete(
        f"/trips/{trip_id}/comments/{comment_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    # Validate response structure
    assert "success" in data
    assert "message" in data

    # Validate field types
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)

    # Validate values
    assert data["success"] is True


@pytest.mark.contract
@pytest.mark.asyncio
async def test_add_comment_pagination_params(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """
    Test comments list pagination query parameters.

    Valid params:
    - page: min 1, default 1
    - limit: min 1, max 50, default 20
    """
    trip_id = published_trip_public_user.trip_id

    # Valid pagination
    response = await client.get(f"/trips/{trip_id}/comments?page=1&limit=20")
    assert response.status_code == 200

    # Default values
    response = await client.get(f"/trips/{trip_id}/comments")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 20


@pytest.mark.contract
@pytest.mark.asyncio
async def test_add_comment_pagination_validation(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test invalid pagination parameters return 422."""
    trip_id = published_trip_public_user.trip_id

    # Invalid page
    response = await client.get(f"/trips/{trip_id}/comments?page=0")
    assert response.status_code == 422

    # Invalid limit (too small)
    response = await client.get(f"/trips/{trip_id}/comments?limit=0")
    assert response.status_code == 422

    # Invalid limit (too large)
    response = await client.get(f"/trips/{trip_id}/comments?limit=51")
    assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_add_comment_requires_authentication(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test add comment endpoint requires authentication (401)."""
    trip_id = published_trip_public_user.trip_id

    # No auth headers
    response = await client.post(
        f"/trips/{trip_id}/comments",
        json={"content": "Test comment"},
    )
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_edit_comment_requires_authentication(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test edit comment endpoint requires authentication (401)."""
    trip_id = published_trip_public_user.trip_id
    fake_comment_id = "00000000-0000-0000-0000-000000000000"

    # No auth headers
    response = await client.put(
        f"/trips/{trip_id}/comments/{fake_comment_id}",
        json={"content": "Edited"},
    )
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_comment_requires_authentication(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test delete comment endpoint requires authentication (401)."""
    trip_id = published_trip_public_user.trip_id
    fake_comment_id = "00000000-0000-0000-0000-000000000000"

    # No auth headers
    response = await client.delete(
        f"/trips/{trip_id}/comments/{fake_comment_id}",
    )
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_add_comment_validation_empty_content(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test adding comment with empty content returns 400 (FR-017)."""
    trip_id = published_trip_public_user.trip_id

    # Empty content
    response = await client.post(
        f"/trips/{trip_id}/comments",
        headers=auth_headers,
        json={"content": ""},
    )
    assert response.status_code == 400


@pytest.mark.contract
@pytest.mark.asyncio
async def test_add_comment_validation_too_long(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test adding comment over 500 chars returns 400 (FR-017)."""
    trip_id = published_trip_public_user.trip_id

    # 501 characters
    long_content = "a" * 501

    response = await client.post(
        f"/trips/{trip_id}/comments",
        headers=auth_headers,
        json={"content": long_content},
    )
    assert response.status_code == 400


@pytest.mark.contract
@pytest.mark.asyncio
async def test_edit_comment_not_author_returns_403(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test editing another user's comment returns 403."""
    # This test requires fixture for comment created by another user
    pytest.skip("Requires multi-user comment fixture")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_delete_comment_not_author_returns_403(
    client: AsyncClient,
    auth_headers: dict,
    published_trip_public_user: Trip,
):
    """Test deleting another user's comment returns 403."""
    # This test requires fixture for comment created by another user
    pytest.skip("Requires multi-user comment fixture")


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_trip_comments_empty_list_schema(
    client: AsyncClient,
    published_trip_public_user: Trip,
):
    """Test empty comments list still matches schema."""
    trip_id = published_trip_public_user.trip_id

    response = await client.get(f"/trips/{trip_id}/comments")

    assert response.status_code == 200
    data = response.json()

    # Should have required fields even if empty
    assert "comments" in data
    assert "total_count" in data

    # Empty comments should be valid list
    if data["total_count"] == 0:
        assert data["comments"] == []
        assert data["has_more"] is False


@pytest.mark.contract
@pytest.mark.asyncio
async def test_comment_nonexistent_trip_returns_404(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test commenting on non-existent trip returns 404."""
    fake_trip_id = "00000000-0000-0000-0000-000000000000"

    response = await client.post(
        f"/trips/{fake_trip_id}/comments",
        headers=auth_headers,
        json={"content": "Test"},
    )

    assert response.status_code == 404
