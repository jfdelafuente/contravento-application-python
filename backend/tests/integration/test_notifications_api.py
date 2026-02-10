"""
Integration tests for Notification API endpoints (Feature 018).

Tests notification retrieval, unread count, and mark-as-read operations.
Task: T017
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.notification import Notification, NotificationType
from src.models.trip import Trip
from src.models.user import User


@pytest.mark.asyncio
async def test_get_notifications_authenticated(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
):
    """Test GET /notifications returns user's notifications."""
    # Create a second user (actor)
    actor = User(
        user_id=str(uuid4()),
        username="actor_user",
        email="actor@example.com",
        password_hash="hashed",
        is_verified=True,
    )
    db_session.add(actor)

    # Create a trip for notification context
    trip = Trip(
        trip_id=str(uuid4()),
        user_id=test_user.user_id,
        title="Test Trip",
        description="Test description",
        start_date="2024-06-01",
        status="published",
    )
    db_session.add(trip)

    # Create test notifications
    notification1 = Notification(
        id=str(uuid4()),
        user_id=test_user.user_id,
        type=NotificationType.LIKE,
        actor_id=actor.user_id,
        trip_id=trip.trip_id,
        is_read=False,
        created_at=datetime.now(UTC),
    )
    notification2 = Notification(
        id=str(uuid4()),
        user_id=test_user.user_id,
        type=NotificationType.COMMENT,
        actor_id=actor.user_id,
        trip_id=trip.trip_id,
        content="Great trip!",
        is_read=True,
        created_at=datetime.now(UTC),
    )

    db_session.add(notification1)
    db_session.add(notification2)
    await db_session.commit()

    # Test GET /notifications
    response = await client.get(
        "/notifications",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "notifications" in data
    assert "unread_count" in data
    assert len(data["notifications"]) == 2
    assert data["unread_count"] == 1


@pytest.mark.asyncio
async def test_get_unread_count(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
):
    """Test GET /notifications/unread-count returns correct count."""
    # Create actor and trip
    actor = User(
        user_id=str(uuid4()),
        username="actor_user",
        email="actor@example.com",
        password_hash="hashed",
        is_verified=True,
    )
    db_session.add(actor)

    trip = Trip(
        trip_id=str(uuid4()),
        user_id=test_user.user_id,
        title="Test Trip",
        description="Test description",
        start_date="2024-06-01",
        status="published",
    )
    db_session.add(trip)

    # Create 3 unread notifications
    for _ in range(3):
        notification = Notification(
            id=str(uuid4()),
            user_id=test_user.user_id,
            type=NotificationType.LIKE,
            actor_id=actor.user_id,
            trip_id=trip.trip_id,
            is_read=False,
            created_at=datetime.now(UTC),
        )
        db_session.add(notification)

    await db_session.commit()

    # Test GET /notifications/unread-count
    response = await client.get(
        "/notifications/unread-count",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "unread_count" in data
    assert data["unread_count"] == 3


@pytest.mark.asyncio
async def test_mark_notification_read(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
):
    """Test POST /notifications/{id}/mark-read marks notification as read."""
    # Create actor and trip
    actor = User(
        user_id=str(uuid4()),
        username="actor_user",
        email="actor@example.com",
        password_hash="hashed",
        is_verified=True,
    )
    db_session.add(actor)

    trip = Trip(
        trip_id=str(uuid4()),
        user_id=test_user.user_id,
        title="Test Trip",
        description="Test description",
        start_date="2024-06-01",
        status="published",
    )
    db_session.add(trip)

    # Create unread notification
    notification = Notification(
        id=str(uuid4()),
        user_id=test_user.user_id,
        type=NotificationType.LIKE,
        actor_id=actor.user_id,
        trip_id=trip.trip_id,
        is_read=False,
        created_at=datetime.now(UTC),
    )
    db_session.add(notification)
    await db_session.commit()

    # Test POST /notifications/{id}/mark-read
    response = await client.post(
        f"/notifications/{notification.id}/mark-read",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["marked_count"] == 1

    # Verify notification is now read
    await db_session.refresh(notification)
    assert notification.is_read is True


@pytest.mark.asyncio
async def test_mark_all_notifications_read(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
):
    """Test POST /notifications/mark-all-read marks all notifications as read."""
    # Create actor and trip
    actor = User(
        user_id=str(uuid4()),
        username="actor_user",
        email="actor@example.com",
        password_hash="hashed",
        is_verified=True,
    )
    db_session.add(actor)

    trip = Trip(
        trip_id=str(uuid4()),
        user_id=test_user.user_id,
        title="Test Trip",
        description="Test description",
        start_date="2024-06-01",
        status="published",
    )
    db_session.add(trip)

    # Create 5 unread notifications
    notifications = []
    for _ in range(5):
        notification = Notification(
            id=str(uuid4()),
            user_id=test_user.user_id,
            type=NotificationType.LIKE,
            actor_id=actor.user_id,
            trip_id=trip.trip_id,
            is_read=False,
            created_at=datetime.now(UTC),
        )
        db_session.add(notification)
        notifications.append(notification)

    await db_session.commit()

    # Test POST /notifications/mark-all-read
    response = await client.post(
        "/notifications/mark-all-read",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["marked_count"] == 5

    # Verify all notifications are now read
    for notification in notifications:
        await db_session.refresh(notification)
        assert notification.is_read is True


@pytest.mark.asyncio
async def test_get_notifications_requires_auth(client: AsyncClient):
    """Test GET /notifications requires authentication."""
    response = await client.get("/notifications")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_mark_notification_read_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    """Test POST /notifications/{id}/mark-read returns 404 for non-existent notification."""
    fake_id = str(uuid4())

    response = await client.post(
        f"/notifications/{fake_id}/mark-read",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()

    assert data["success"] is False
    assert data["error"]["code"] == "NOTIFICATION_NOT_FOUND"
