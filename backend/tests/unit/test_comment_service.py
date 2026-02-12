"""
Unit tests for CommentService (Feature 004 - US3: Comentarios).

Tests cover:
- T071: create_comment() basic functionality
- T072: update_comment() with is_edited marker
- T073: delete_comment() basic functionality
- T074: get_trip_comments() pagination
- T075: Comment rate limiting (10/hour)

Following TDD: These tests are written BEFORE implementation.
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.comment import Comment
from src.models.trip import Trip
from src.models.user import User
from src.services.comment_service import CommentService


@pytest.fixture
async def trip_owner(db_session: AsyncSession) -> User:
    """Create a trip owner user for testing."""
    user = User(
        id=str(uuid4()),
        username="trip_owner",
        email="owner@test.com",
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
    """Create a user who will comment on trips."""
    user = User(
        id=str(uuid4()),
        username="commenter_user",
        email="commenter@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_trip(db_session: AsyncSession, trip_owner: User) -> Trip:
    """Create a test trip for commenting."""
    trip = Trip(
        trip_id=str(uuid4()),
        user_id=trip_owner.id,
        title="Test Trip for Comments",
        description="This is a test trip for comment functionality",
        start_date=datetime.now(UTC).date(),
        distance_km=50.0,
        status="published",
        created_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


# ============================================================
# T071: Test create_comment() basic functionality
# ============================================================


@pytest.mark.asyncio
async def test_create_comment_success(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T071: CommentService.create_comment() creates comment successfully.

    Verifies:
    - Comment is created in database
    - Content is stored correctly (FR-016, FR-017)
    - User and trip associations are correct
    - Timestamps are set
    - is_edited is False by default
    """
    # Arrange
    content = "Great trip! I loved the route."

    # Act
    comment = await CommentService.create_comment(
        db_session, trip_id=test_trip.trip_id, user_id=commenter_user.id, content=content
    )

    # Assert
    assert comment.id is not None
    assert comment.content == content
    assert comment.user_id == commenter_user.id
    assert comment.trip_id == test_trip.trip_id
    assert comment.is_edited is False
    assert comment.created_at is not None
    assert comment.updated_at is None

    # Verify in database
    result = await db_session.execute(select(Comment).where(Comment.id == comment.id))
    db_comment = result.scalar_one_or_none()
    assert db_comment is not None
    assert db_comment.content == content


@pytest.mark.asyncio
async def test_create_comment_content_validation(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T071: CommentService.create_comment() validates content length (FR-017).

    Verifies:
    - Content must be 1-500 characters
    - Empty strings are rejected
    - Content >500 chars is rejected
    """
    # Test empty content
    with pytest.raises(ValueError, match="entre 1 y 500 caracteres"):
        await CommentService.create_comment(
            db_session, trip_id=test_trip.trip_id, user_id=commenter_user.id, content=""
        )

    # Test whitespace-only content
    with pytest.raises(ValueError, match="entre 1 y 500 caracteres"):
        await CommentService.create_comment(
            db_session, trip_id=test_trip.trip_id, user_id=commenter_user.id, content="   "
        )

    # Test content too long (>500 chars)
    long_content = "a" * 501
    with pytest.raises(ValueError, match="entre 1 y 500 caracteres"):
        await CommentService.create_comment(
            db_session,
            trip_id=test_trip.trip_id,
            user_id=commenter_user.id,
            content=long_content,
        )


@pytest.mark.asyncio
async def test_create_comment_on_draft_trip_fails(
    db_session: AsyncSession, trip_owner: User, commenter_user: User
):
    """
    Test T071: Cannot comment on draft trips (only published trips).

    Verifies:
    - Comments are only allowed on published trips
    - Proper error message in Spanish
    """
    # Create draft trip
    draft_trip = Trip(
        trip_id=str(uuid4()),
        user_id=trip_owner.id,
        title="Draft Trip",
        description="Draft trip should not allow comments",
        start_date=datetime.now(UTC).date(),
        distance_km=30.0,
        status="draft",
        created_at=datetime.now(UTC),
    )
    db_session.add(draft_trip)
    await db_session.commit()

    # Try to comment
    with pytest.raises(ValueError, match="solo puede comentarse en viajes publicados"):
        await CommentService.create_comment(
            db_session,
            trip_id=draft_trip.trip_id,
            user_id=commenter_user.id,
            content="This should fail",
        )


# ============================================================
# T072: Test update_comment() with is_edited marker
# ============================================================


@pytest.mark.asyncio
async def test_update_comment_success(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T072: CommentService.update_comment() updates content and sets is_edited (FR-020).

    Verifies:
    - Content is updated
    - is_edited is set to True
    - updated_at timestamp is set
    - User can only edit own comments
    """
    # Create comment
    comment = await CommentService.create_comment(
        db_session,
        trip_id=test_trip.trip_id,
        user_id=commenter_user.id,
        content="Original content",
    )

    # Wait a moment to ensure updated_at differs
    import asyncio

    await asyncio.sleep(0.1)

    # Update comment
    new_content = "Updated content after editing"
    updated_comment = await CommentService.update_comment(
        db_session,
        comment_id=comment.id,
        user_id=commenter_user.id,
        content=new_content,
    )

    # Assert
    assert updated_comment.id == comment.id
    assert updated_comment.content == new_content
    assert updated_comment.is_edited is True
    assert updated_comment.updated_at is not None
    assert updated_comment.updated_at > updated_comment.created_at


@pytest.mark.asyncio
async def test_update_comment_only_owner_can_edit(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User, trip_owner: User
):
    """
    Test T072: Only comment author can edit their own comment.

    Verifies:
    - Other users cannot edit someone else's comment
    - Proper error message in Spanish
    """
    # Create comment
    comment = await CommentService.create_comment(
        db_session,
        trip_id=test_trip.trip_id,
        user_id=commenter_user.id,
        content="Original content",
    )

    # Try to edit as different user
    with pytest.raises(ValueError, match="Solo puedes editar tus propios comentarios"):
        await CommentService.update_comment(
            db_session,
            comment_id=comment.id,
            user_id=trip_owner.id,  # Different user
            content="Trying to edit someone else's comment",
        )


# ============================================================
# T073: Test delete_comment() basic functionality
# ============================================================


@pytest.mark.asyncio
async def test_delete_comment_by_author(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T073: CommentService.delete_comment() allows author to delete (FR-021).

    Verifies:
    - Comment author can delete their own comment
    - Comment is removed from database
    """
    # Create comment
    comment = await CommentService.create_comment(
        db_session,
        trip_id=test_trip.trip_id,
        user_id=commenter_user.id,
        content="This will be deleted",
    )

    # Delete comment
    await CommentService.delete_comment(
        db_session, comment_id=comment.id, user_id=commenter_user.id
    )

    # Verify deletion
    result = await db_session.execute(select(Comment).where(Comment.id == comment.id))
    db_comment = result.scalar_one_or_none()
    assert db_comment is None


@pytest.mark.asyncio
async def test_delete_comment_by_trip_owner(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User, trip_owner: User
):
    """
    Test T073: CommentService.delete_comment() allows trip owner to delete (FR-022).

    Verifies:
    - Trip owner can delete any comment on their trip (moderation)
    - Comment is removed from database
    """
    # Create comment
    comment = await CommentService.create_comment(
        db_session,
        trip_id=test_trip.trip_id,
        user_id=commenter_user.id,
        content="Comment on trip",
    )

    # Trip owner deletes comment (moderation)
    await CommentService.delete_comment(
        db_session,
        comment_id=comment.id,
        user_id=trip_owner.id,
        trip_id=test_trip.trip_id,  # Pass trip_id to verify ownership
    )

    # Verify deletion
    result = await db_session.execute(select(Comment).where(Comment.id == comment.id))
    db_comment = result.scalar_one_or_none()
    assert db_comment is None


@pytest.mark.asyncio
async def test_delete_comment_unauthorized(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T073: Only comment author or trip owner can delete comment.

    Verifies:
    - Other users cannot delete someone else's comment
    - Proper error message in Spanish
    """
    # Create another user
    other_user = User(
        id=str(uuid4()),
        username="other_user",
        email="other@test.com",
        hashed_password="hashed_password",
        is_verified=True,
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.commit()

    # Create comment
    comment = await CommentService.create_comment(
        db_session,
        trip_id=test_trip.trip_id,
        user_id=commenter_user.id,
        content="Protected comment",
    )

    # Try to delete as unauthorized user
    with pytest.raises(ValueError, match="No tienes permiso para eliminar este comentario"):
        await CommentService.delete_comment(
            db_session, comment_id=comment.id, user_id=other_user.id
        )


# ============================================================
# T074: Test get_trip_comments() pagination
# ============================================================


@pytest.mark.asyncio
async def test_get_trip_comments_pagination(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T074: CommentService.get_trip_comments() returns paginated comments (FR-024).

    Verifies:
    - Comments are returned in chronological order (oldest first - FR-018)
    - Pagination works correctly (limit, offset)
    - Total count is accurate
    """
    # Create 8 comments (stay under rate limit of 10/hour)
    comments = []
    for i in range(8):
        comment = await CommentService.create_comment(
            db_session,
            trip_id=test_trip.trip_id,
            user_id=commenter_user.id,
            content=f"Comment {i + 1}",
        )
        comments.append(comment)

    # Get first page (5 items)
    result = await CommentService.get_trip_comments(
        db_session, trip_id=test_trip.trip_id, limit=5, offset=0
    )

    assert result["total"] == 8
    assert len(result["items"]) == 5
    # Verify chronological order (oldest first)
    assert result["items"][0].content == "Comment 1"
    assert result["items"][4].content == "Comment 5"

    # Get second page (3 items)
    result_page2 = await CommentService.get_trip_comments(
        db_session, trip_id=test_trip.trip_id, limit=5, offset=5
    )

    assert result_page2["total"] == 8
    assert len(result_page2["items"]) == 3
    assert result_page2["items"][0].content == "Comment 6"
    assert result_page2["items"][2].content == "Comment 8"


# ============================================================
# T075: Test comment rate limiting (10/hour)
# ============================================================


@pytest.mark.asyncio
async def test_comment_rate_limiting(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T075: CommentService enforces rate limit of 10 comments/hour per user.

    Verifies:
    - User can post up to 10 comments in an hour
    - 11th comment within the hour is rejected with 429 error
    - Rate limit resets after 1 hour
    """
    # Create 10 comments (should succeed)
    for i in range(10):
        comment = await CommentService.create_comment(
            db_session,
            trip_id=test_trip.trip_id,
            user_id=commenter_user.id,
            content=f"Rate limit test comment {i + 1}",
        )
        assert comment is not None

    # 11th comment should be rate limited
    with pytest.raises(ValueError, match="límite de 10 comentarios por hora"):
        await CommentService.create_comment(
            db_session,
            trip_id=test_trip.trip_id,
            user_id=commenter_user.id,
            content="This should be rate limited",
        )


@pytest.mark.asyncio
async def test_comment_rate_limit_resets_after_hour(
    db_session: AsyncSession, test_trip: Trip, commenter_user: User
):
    """
    Test T075: Rate limit resets after 1 hour.

    Verifies:
    - Comments older than 1 hour don't count toward limit
    - User can post again after 1 hour
    """
    # Create 10 comments with old timestamp (>1 hour ago)
    old_timestamp = datetime.now(UTC) - timedelta(hours=2)
    for i in range(10):
        comment = Comment(
            id=str(uuid4()),
            user_id=commenter_user.id,
            trip_id=test_trip.trip_id,
            content=f"Old comment {i + 1}",
            created_at=old_timestamp,
            is_edited=False,
        )
        db_session.add(comment)
    await db_session.commit()

    # New comment should succeed (old comments don't count)
    new_comment = await CommentService.create_comment(
        db_session,
        trip_id=test_trip.trip_id,
        user_id=commenter_user.id,
        content="New comment after rate limit reset",
    )
    assert new_comment is not None
    assert new_comment.content == "New comment after rate limit reset"
