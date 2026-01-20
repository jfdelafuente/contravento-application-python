"""
Contract tests for Notifications API (Feature 004 - T012).

Validates that notification endpoints responses match the OpenAPI specification
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


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_notifications_response_schema(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test GET /notifications response matches OpenAPI schema (FR-028).

    Contract validation for NotificationsListResponse schema:
    - notifications: array of NotificationResponse objects
    - total_count: integer
    - page: integer
    - limit: integer
    - has_more: boolean
    """
    response = await client.get("/notifications", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate top-level response structure
    assert "notifications" in data
    assert "total_count" in data
    assert "page" in data
    assert "limit" in data
    assert "has_more" in data

    # Validate field types
    assert isinstance(data["notifications"], list)
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
async def test_get_notifications_item_schema(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test NotificationResponse schema in notifications list (FR-028).

    Each NotificationResponse must include:
    - notification_id: string (UUID)
    - type: enum (like, comment, share)
    - actor: UserSummary object
    - trip: TripSummary object
    - content: string (nullable - comment excerpt)
    - is_read: boolean
    - created_at: ISO 8601 datetime
    """
    response = await client.get("/notifications", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # If notifications exist, validate first item
    if len(data["notifications"]) > 0:
        notification = data["notifications"][0]

        # Required fields
        assert "notification_id" in notification
        assert "type" in notification
        assert "actor" in notification
        assert "trip" in notification
        assert "content" in notification
        assert "is_read" in notification
        assert "created_at" in notification

        # Type validation
        assert isinstance(notification["notification_id"], str)
        assert isinstance(notification["type"], str)
        assert notification["type"] in ["like", "comment", "share"]
        assert isinstance(notification["actor"], dict)
        assert isinstance(notification["trip"], dict)
        assert notification["content"] is None or isinstance(notification["content"], str)
        assert isinstance(notification["is_read"], bool)
        assert isinstance(notification["created_at"], str)

        # Validate actor (UserSummary)
        actor = notification["actor"]
        assert "username" in actor
        assert "full_name" in actor
        assert "profile_photo_url" in actor

        # Validate trip (TripSummary)
        trip = notification["trip"]
        assert "trip_id" in trip
        assert "title" in trip
        assert "photo_url" in trip


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_notifications_pagination_params(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test notifications pagination query parameters.

    Valid params:
    - page: min 1, default 1
    - limit: min 1, max 50, default 20
    - is_read: boolean (optional filter)
    """
    # Valid pagination
    response = await client.get("/notifications?page=1&limit=20", headers=auth_headers)
    assert response.status_code == 200

    # Default values
    response = await client.get("/notifications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 20

    # Filter by read status
    response = await client.get("/notifications?is_read=false", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_notifications_pagination_validation(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test invalid pagination parameters return 422."""
    # Invalid page
    response = await client.get("/notifications?page=0", headers=auth_headers)
    assert response.status_code == 422

    # Invalid limit (too small)
    response = await client.get("/notifications?limit=0", headers=auth_headers)
    assert response.status_code == 422

    # Invalid limit (too large)
    response = await client.get("/notifications?limit=51", headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_unread_count_response_schema(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test GET /notifications/unread-count response matches schema (FR-030).

    Response should have:
    - unread_count: integer
    """
    response = await client.get("/notifications/unread-count", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate response structure
    assert "unread_count" in data

    # Validate field type
    assert isinstance(data["unread_count"], int)

    # Validate value
    assert data["unread_count"] >= 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_mark_notification_read_response_schema(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test POST /notifications/{notification_id}/mark-read response matches schema (FR-031).

    Should return NotificationResponse with is_read=true.
    """
    # This test requires a notification fixture
    # For now, test the contract shape with a fake ID
    fake_notification_id = "00000000-0000-0000-0000-000000000000"

    response = await client.post(
        f"/notifications/{fake_notification_id}/mark-read",
        headers=auth_headers,
    )

    # Should be 404 (notification not found) or 200 (if fixture exists)
    # Contract validation happens when fixture is available
    if response.status_code == 200:
        data = response.json()

        # Validate NotificationResponse structure
        assert "notification_id" in data
        assert "is_read" in data
        assert data["is_read"] is True


@pytest.mark.contract
@pytest.mark.asyncio
async def test_mark_all_notifications_read_response_schema(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test POST /notifications/mark-all-read response matches schema (FR-032).

    Response should have:
    - success: boolean
    - message: string
    - marked_count: integer
    """
    response = await client.post("/notifications/mark-all-read", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Validate response structure
    assert "success" in data
    assert "message" in data
    assert "marked_count" in data

    # Validate field types
    assert isinstance(data["success"], bool)
    assert isinstance(data["message"], str)
    assert isinstance(data["marked_count"], int)

    # Validate values
    assert data["success"] is True
    assert data["marked_count"] >= 0


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_notifications_requires_authentication(client: AsyncClient):
    """Test notifications endpoint requires authentication (401)."""
    # No auth headers
    response = await client.get("/notifications")
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_unread_count_requires_authentication(client: AsyncClient):
    """Test unread count endpoint requires authentication (401)."""
    # No auth headers
    response = await client.get("/notifications/unread-count")
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_mark_notification_read_requires_authentication(client: AsyncClient):
    """Test mark read endpoint requires authentication (401)."""
    fake_notification_id = "00000000-0000-0000-0000-000000000000"

    # No auth headers
    response = await client.post(f"/notifications/{fake_notification_id}/mark-read")
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_mark_all_read_requires_authentication(client: AsyncClient):
    """Test mark all read endpoint requires authentication (401)."""
    # No auth headers
    response = await client.post("/notifications/mark-all-read")
    assert response.status_code == 401


@pytest.mark.contract
@pytest.mark.asyncio
async def test_mark_nonexistent_notification_read_returns_404(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test marking non-existent notification as read returns 404."""
    fake_notification_id = "00000000-0000-0000-0000-000000000000"

    response = await client.post(
        f"/notifications/{fake_notification_id}/mark-read",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.contract
@pytest.mark.asyncio
async def test_get_notifications_empty_list_schema(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test empty notifications list still matches schema."""
    response = await client.get("/notifications", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Should have required fields even if empty
    assert "notifications" in data
    assert "total_count" in data

    # Empty notifications should be valid list
    if data["total_count"] == 0:
        assert data["notifications"] == []
        assert data["has_more"] is False


@pytest.mark.contract
@pytest.mark.asyncio
async def test_notification_content_excerpt_for_comments(
    client: AsyncClient,
    auth_headers: dict,
):
    """
    Test that comment notifications include content excerpt (FR-035).

    For type=comment, content should contain comment excerpt.
    For type=like/share, content should be null.
    """
    response = await client.get("/notifications", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Find comment notification
    comment_notification = next(
        (n for n in data["notifications"] if n["type"] == "comment"),
        None,
    )

    if comment_notification:
        # Comment notifications should have content excerpt
        assert comment_notification["content"] is not None
        assert isinstance(comment_notification["content"], str)

    # Find like/share notification
    like_or_share_notification = next(
        (n for n in data["notifications"] if n["type"] in ["like", "share"]),
        None,
    )

    if like_or_share_notification:
        # Like/share notifications should have null content
        assert like_or_share_notification["content"] is None


@pytest.mark.contract
@pytest.mark.asyncio
async def test_notifications_ordered_chronologically_desc(
    client: AsyncClient,
    auth_headers: dict,
):
    """Test notifications are ordered by created_at DESC (FR-037)."""
    response = await client.get("/notifications?limit=50", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # If we have multiple notifications, verify DESC order
    if len(data["notifications"]) >= 2:
        first = data["notifications"][0]["created_at"]
        second = data["notifications"][1]["created_at"]

        # First should be more recent (greater timestamp) than second
        assert first >= second
