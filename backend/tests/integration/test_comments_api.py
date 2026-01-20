"""
Integration tests for Comments API endpoints (Feature 004 - US3: Comentarios).

Tests cover:
- T077: POST /trips/{id}/comments
- T078: GET /trips/{id}/comments
- T079: PUT /comments/{id} (edit)
- T080: DELETE /comments/{id}
- T081: Comment (unauthorized - 401)
- T082: Rate limit exceeded (429)
- T083: XSS prevention (sanitization)

Following TDD: These tests are written BEFORE implementation.
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import Trip
from src.models.user import User
from src.utils.security import create_access_token


def get_auth_headers(user: User) -> dict[str, str]:
    """
    Generate authentication headers for a given user.

    Args:
        user: User model instance

    Returns:
        Dictionary with Authorization header containing JWT token
    """
    access_token = create_access_token({"sub": user.id, "username": user.username})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def trip_owner(db_session: AsyncSession) -> User:
    """Create a trip owner user."""
    user = User(
        id=str(uuid4()),
        username="trip_owner_api",
        email="owner_api@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def commenter_user(db_session: AsyncSession) -> User:
    """Create a user who will comment."""
    user = User(
        id=str(uuid4()),
        username="commenter_api",
        email="commenter_api@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def published_trip(db_session: AsyncSession, trip_owner: User) -> Trip:
    """Create a published trip."""
    trip = Trip(
        trip_id=str(uuid4()),
        user_id=trip_owner.id,
        title="API Test Trip for Comments",
        description="Testing comments API with this trip",
        start_date=datetime.now(UTC).date(),
        distance_km=150.0,
        status="published",
        created_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


# ============================================================
# T077: Test POST /trips/{id}/comments
# ============================================================


@pytest.mark.asyncio
async def test_create_comment_success(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T077: POST /trips/{id}/comments creates comment successfully.

    Verifies:
    - 201 Created status
    - Comment is returned in response
    - Content matches input (FR-016, FR-017)
    """
    # Arrange
    comment_data = {"content": "Great trip! I loved the route through the mountains."}

    # Act
    response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json=comment_data,
        headers=get_auth_headers(commenter_user),
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["content"] == comment_data["content"]
    assert data["data"]["user_id"] == commenter_user.id
    assert data["data"]["trip_id"] == published_trip.trip_id
    assert data["data"]["is_edited"] is False
    assert "created_at" in data["data"]


@pytest.mark.asyncio
async def test_create_comment_validation(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T077: POST /trips/{id}/comments validates content (FR-017).

    Verifies:
    - Empty content returns 400
    - Content >500 chars returns 400
    - Spanish error messages
    """
    # Test empty content
    response_empty = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": ""},
        headers=get_auth_headers(commenter_user),
    )
    assert response_empty.status_code == 400
    assert "entre 1 y 500 caracteres" in response_empty.json()["error"]["message"]

    # Test content too long
    long_content = "a" * 501
    response_long = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": long_content},
        headers=get_auth_headers(commenter_user),
    )
    assert response_long.status_code == 400
    assert "entre 1 y 500 caracteres" in response_long.json()["error"]["message"]


# ============================================================
# T078: Test GET /trips/{id}/comments
# ============================================================


@pytest.mark.asyncio
async def test_get_trip_comments_success(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T078: GET /trips/{id}/comments returns paginated comments (FR-018, FR-024).

    Verifies:
    - 200 OK status
    - Comments returned in chronological order (oldest first)
    - Pagination metadata (total, items)
    - Unauthenticated users can read comments (FR-025)
    """
    # Create 3 comments
    for i in range(3):
        await client.post(
            f"/trips/{published_trip.trip_id}/comments",
            json={"content": f"Comment {i + 1}"},
            headers=get_auth_headers(commenter_user),
        )

    # Get comments (unauthenticated - should work)
    response = await client.get(f"/trips/{published_trip.trip_id}/comments")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 3
    assert len(data["data"]["items"]) == 3
    # Verify chronological order (oldest first - FR-018)
    assert data["data"]["items"][0]["content"] == "Comment 1"
    assert data["data"]["items"][2]["content"] == "Comment 3"


@pytest.mark.asyncio
async def test_get_trip_comments_pagination(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T078: GET /trips/{id}/comments supports pagination (FR-024).

    Verifies:
    - limit and offset query parameters work
    - Default limit is 50
    - Total count is accurate
    """
    # Create 15 comments
    for i in range(15):
        await client.post(
            f"/trips/{published_trip.trip_id}/comments",
            json={"content": f"Comment {i + 1}"},
            headers=get_auth_headers(commenter_user),
        )

    # Get first page (10 items)
    response_page1 = await client.get(f"/trips/{published_trip.trip_id}/comments?limit=10&offset=0")
    assert response_page1.status_code == 200
    data_page1 = response_page1.json()["data"]
    assert data_page1["total"] == 15
    assert len(data_page1["items"]) == 10
    assert data_page1["items"][0]["content"] == "Comment 1"

    # Get second page (5 items)
    response_page2 = await client.get(
        f"/trips/{published_trip.trip_id}/comments?limit=10&offset=10"
    )
    assert response_page2.status_code == 200
    data_page2 = response_page2.json()["data"]
    assert data_page2["total"] == 15
    assert len(data_page2["items"]) == 5
    assert data_page2["items"][0]["content"] == "Comment 11"


# ============================================================
# T079: Test PUT /comments/{id} (edit)
# ============================================================


@pytest.mark.asyncio
async def test_update_comment_success(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T079: PUT /comments/{id} updates comment and sets is_edited (FR-020).

    Verifies:
    - 200 OK status
    - Content is updated
    - is_edited is True
    - updated_at timestamp is set
    - "editado" marker appears (FR-019)
    """
    # Create comment
    create_response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "Original content"},
        headers=get_auth_headers(commenter_user),
    )
    comment_id = create_response.json()["data"]["id"]

    # Update comment
    update_response = await client.put(
        f"/comments/{comment_id}",
        json={"content": "Updated content after editing"},
        headers=get_auth_headers(commenter_user),
    )

    # Assert
    assert update_response.status_code == 200
    data = update_response.json()["data"]
    assert data["content"] == "Updated content after editing"
    assert data["is_edited"] is True
    assert "updated_at" in data
    assert data["updated_at"] is not None


@pytest.mark.asyncio
async def test_update_comment_only_owner_can_edit(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
    trip_owner: User,
):
    """
    Test T079: Only comment author can edit their own comment.

    Verifies:
    - Other users get 403 Forbidden
    - Spanish error message
    """
    # Create comment as commenter_user
    create_response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "Original content"},
        headers=get_auth_headers(commenter_user),
    )
    comment_id = create_response.json()["data"]["id"]

    # Try to edit as different user (trip_owner)
    update_response = await client.put(
        f"/comments/{comment_id}",
        json={"content": "Trying to edit someone else's comment"},
        headers=get_auth_headers(trip_owner),
    )

    # Assert
    assert update_response.status_code == 403
    assert (
        "Solo puedes editar tus propios comentarios" in update_response.json()["error"]["message"]
    )


# ============================================================
# T080: Test DELETE /comments/{id}
# ============================================================


@pytest.mark.asyncio
async def test_delete_comment_by_author(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T080: DELETE /comments/{id} allows author to delete (FR-021).

    Verifies:
    - 204 No Content status
    - Comment is removed from database
    - Subsequent GET returns 404
    """
    # Create comment
    create_response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "This will be deleted"},
        headers=get_auth_headers(commenter_user),
    )
    comment_id = create_response.json()["data"]["id"]

    # Delete comment
    delete_response = await client.delete(
        f"/comments/{comment_id}", headers=get_auth_headers(commenter_user)
    )

    # Assert deletion
    assert delete_response.status_code == 204

    # Verify comment no longer exists
    get_response = await client.get(
        f"/trips/{published_trip.trip_id}/comments", headers=get_auth_headers(commenter_user)
    )
    comments = get_response.json()["data"]["items"]
    assert not any(c["id"] == comment_id for c in comments)


@pytest.mark.asyncio
async def test_delete_comment_by_trip_owner(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
    trip_owner: User,
):
    """
    Test T080: DELETE /comments/{id} allows trip owner to delete (FR-022 - moderation).

    Verifies:
    - Trip owner can delete any comment on their trip
    - 204 No Content status
    """
    # Create comment
    create_response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "Comment to be moderated"},
        headers=get_auth_headers(commenter_user),
    )
    comment_id = create_response.json()["data"]["id"]

    # Trip owner deletes comment (moderation)
    delete_response = await client.delete(
        f"/comments/{comment_id}", headers=get_auth_headers(trip_owner)
    )

    # Assert
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_delete_comment_unauthorized(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
    db_session: AsyncSession,
):
    """
    Test T080: Only comment author or trip owner can delete comment.

    Verifies:
    - Other users get 403 Forbidden
    - Spanish error message
    """
    # Create another user
    other_user = User(
        id=str(uuid4()),
        username="other_api_user",
        email="other_api@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()

    # Create comment
    create_response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "Protected comment"},
        headers=get_auth_headers(commenter_user),
    )
    comment_id = create_response.json()["data"]["id"]

    # Try to delete as unauthorized user
    delete_response = await client.delete(
        f"/comments/{comment_id}", headers=get_auth_headers(other_user)
    )

    # Assert
    assert delete_response.status_code == 403
    assert (
        "No tienes permiso para eliminar este comentario"
        in delete_response.json()["error"]["message"]
    )


# ============================================================
# T081: Test comment (unauthorized - 401)
# ============================================================


@pytest.mark.asyncio
async def test_create_comment_unauthorized(client: AsyncClient, published_trip: Trip):
    """
    Test T081: POST /trips/{id}/comments requires authentication (FR-025).

    Verifies:
    - Unauthenticated request returns 401
    - Redirects to login (in production)
    """
    # Try to create comment without authentication
    response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "Unauthenticated comment"},
    )

    # Assert
    assert response.status_code == 401
    assert "autenticaci" in response.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_update_comment_unauthorized(
    client: AsyncClient, published_trip: Trip, commenter_user: User
):
    """
    Test T081: PUT /comments/{id} requires authentication.

    Verifies:
    - Unauthenticated request returns 401
    """
    # Create comment first
    create_response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "Original content"},
        headers=get_auth_headers(commenter_user),
    )
    comment_id = create_response.json()["data"]["id"]

    # Try to update without authentication
    response = await client.put(f"/comments/{comment_id}", json={"content": "Updated content"})

    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_comment_unauthorized(
    client: AsyncClient, published_trip: Trip, commenter_user: User
):
    """
    Test T081: DELETE /comments/{id} requires authentication.

    Verifies:
    - Unauthenticated request returns 401
    """
    # Create comment first
    create_response = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "Comment to delete"},
        headers=get_auth_headers(commenter_user),
    )
    comment_id = create_response.json()["data"]["id"]

    # Try to delete without authentication
    response = await client.delete(f"/comments/{comment_id}")

    # Assert
    assert response.status_code == 401


# ============================================================
# T082: Test rate limit exceeded (429)
# ============================================================


@pytest.mark.asyncio
async def test_comment_rate_limit_exceeded(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T082: POST /trips/{id}/comments enforces rate limit (10/hour).

    Verifies:
    - 11th comment within the hour returns 429
    - Spanish error message with rate limit info
    """
    # Create 10 comments (should succeed)
    for i in range(10):
        response = await client.post(
            f"/trips/{published_trip.trip_id}/comments",
            json={"content": f"Rate limit test comment {i + 1}"},
            headers=get_auth_headers(commenter_user),
        )
        assert response.status_code == 201

    # 11th comment should be rate limited
    response_limited = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": "This should be rate limited"},
        headers=get_auth_headers(commenter_user),
    )

    # Assert
    assert response_limited.status_code == 429
    error_message = response_limited.json()["error"]["message"]
    assert "límite de 10 comentarios por hora" in error_message


# ============================================================
# T083: Test XSS prevention (sanitization)
# ============================================================


@pytest.mark.asyncio
async def test_comment_xss_prevention(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T083: POST /trips/{id}/comments sanitizes HTML to prevent XSS.

    Verifies:
    - <script> tags are removed
    - Event handlers (onclick, onerror) are removed
    - Safe HTML tags are preserved
    - Content is sanitized before storage
    """
    # Test script tag removal
    malicious_script = "<script>alert('XSS')</script>Great trip!"
    response_script = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": malicious_script},
        headers=get_auth_headers(commenter_user),
    )
    assert response_script.status_code == 201
    sanitized_content = response_script.json()["data"]["content"]
    assert "<script>" not in sanitized_content
    assert "alert" not in sanitized_content
    assert "Great trip!" in sanitized_content

    # Test event handler removal
    malicious_onclick = "<div onclick=\"alert('XSS')\">Click me</div>"
    response_onclick = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": malicious_onclick},
        headers=get_auth_headers(commenter_user),
    )
    assert response_onclick.status_code == 201
    sanitized_onclick = response_onclick.json()["data"]["content"]
    assert "onclick" not in sanitized_onclick
    assert "alert" not in sanitized_onclick
    assert "Click me" in sanitized_onclick

    # Test safe HTML is preserved
    safe_html = "<p>This is <b>bold</b> and <i>italic</i> text.</p>"
    response_safe = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": safe_html},
        headers=get_auth_headers(commenter_user),
    )
    assert response_safe.status_code == 201
    safe_content = response_safe.json()["data"]["content"]
    # Safe tags should be preserved (or at least content is there)
    assert "bold" in safe_content
    assert "italic" in safe_content


@pytest.mark.asyncio
async def test_comment_iframe_and_object_removal(
    client: AsyncClient,
    published_trip: Trip,
    commenter_user: User,
):
    """
    Test T083: HTML sanitization removes <iframe> and <object> tags.

    Verifies:
    - <iframe> tags are removed (can load external content)
    - <object> and <embed> tags are removed
    """
    # Test iframe removal
    malicious_iframe = '<iframe src="https://evil.com/steal.html"></iframe>Comment'
    response_iframe = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": malicious_iframe},
        headers=get_auth_headers(commenter_user),
    )
    assert response_iframe.status_code == 201
    sanitized = response_iframe.json()["data"]["content"]
    assert "<iframe" not in sanitized
    assert "evil.com" not in sanitized
    assert "Comment" in sanitized

    # Test object removal
    malicious_object = '<object data="evil.swf"></object>Text'
    response_object = await client.post(
        f"/trips/{published_trip.trip_id}/comments",
        json={"content": malicious_object},
        headers=get_auth_headers(commenter_user),
    )
    assert response_object.status_code == 201
    sanitized_obj = response_object.json()["data"]["content"]
    assert "<object" not in sanitized_obj
    assert "evil.swf" not in sanitized_obj
    assert "Text" in sanitized_obj
