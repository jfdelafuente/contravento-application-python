"""
Unit tests for SocialService.

Tests individual methods of SocialService in isolation.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.services.social_service import SocialService
from src.models.user import User, UserProfile
from src.models.social import Follow
from src.utils.security import hash_password


@pytest.mark.asyncio
class TestSocialServiceFollowUser:
    """
    T191: Unit tests for SocialService.follow_user().
    """

    async def test_follow_user_creates_relationship(
        self,
        db_session: AsyncSession,
    ):
        """Test follow_user() creates Follow relationship."""
        # Setup
        user1 = User(username="follower", email="follower@test.com", hashed_password=hash_password("pass"), is_active=True)
        user2 = User(username="followed", email="followed@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        profile1 = UserProfile(user_id=user1.id)
        profile2 = UserProfile(user_id=user2.id)
        db_session.add(profile1)
        db_session.add(profile2)
        await db_session.commit()

        # Test
        social_service = SocialService(db_session)
        await social_service.follow_user(user1.username, user2.username)

        # Verify
        result = await db_session.execute(
            select(Follow).where(
                Follow.follower_id == user1.id,
                Follow.following_id == user2.id
            )
        )
        follow = result.scalar_one_or_none()
        assert follow is not None


@pytest.mark.asyncio
class TestSocialServiceUnfollowUser:
    """
    T192: Unit tests for SocialService.unfollow_user().
    """

    async def test_unfollow_user_removes_relationship(
        self,
        db_session: AsyncSession,
    ):
        """Test unfollow_user() removes Follow relationship."""
        # Setup with existing follow
        user1 = User(username="unfollower", email="unfollower@test.com", hashed_password=hash_password("pass"), is_active=True)
        user2 = User(username="unfollowed", email="unfollowed@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        profile1 = UserProfile(user_id=user1.id)
        profile2 = UserProfile(user_id=user2.id)
        db_session.add(profile1)
        db_session.add(profile2)
        follow = Follow(follower_id=user1.id, following_id=user2.id)
        db_session.add(follow)
        await db_session.commit()

        # Test
        social_service = SocialService(db_session)
        await social_service.unfollow_user(user1.username, user2.username)

        # Verify
        result = await db_session.execute(
            select(Follow).where(
                Follow.follower_id == user1.id,
                Follow.following_id == user2.id
            )
        )
        follow = result.scalar_one_or_none()
        assert follow is None


@pytest.mark.asyncio
class TestSocialServiceGetFollowers:
    """
    T193: Unit tests for SocialService.get_followers().
    """

    async def test_get_followers_returns_paginated_list(
        self,
        db_session: AsyncSession,
    ):
        """Test get_followers() returns paginated list."""
        # Setup: target user with 2 followers
        target = User(username="target", email="target@test.com", hashed_password=hash_password("pass"), is_active=True)
        follower1 = User(username="f1", email="f1@test.com", hashed_password=hash_password("pass"), is_active=True)
        follower2 = User(username="f2", email="f2@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(target)
        db_session.add(follower1)
        db_session.add(follower2)

        p_target = UserProfile(user_id=target.id)
        p1 = UserProfile(user_id=follower1.id, full_name="Follower 1")
        p2 = UserProfile(user_id=follower2.id, full_name="Follower 2")
        db_session.add(p_target)
        db_session.add(p1)
        db_session.add(p2)

        follow1 = Follow(follower_id=follower1.id, following_id=target.id)
        follow2 = Follow(follower_id=follower2.id, following_id=target.id)
        db_session.add(follow1)
        db_session.add(follow2)
        await db_session.commit()

        # Test
        social_service = SocialService(db_session)
        result = await social_service.get_followers("target", page=1, limit=50)

        # Verify
        assert result.total_count == 2
        assert len(result.followers) == 2
        assert result.page == 1
        assert result.has_more is False


@pytest.mark.asyncio
class TestSocialServiceGetFollowing:
    """
    T194: Unit tests for SocialService.get_following().
    """

    async def test_get_following_returns_paginated_list(
        self,
        db_session: AsyncSession,
    ):
        """Test get_following() returns paginated list."""
        # Setup: user following 2 others
        user = User(username="user", email="user@test.com", hashed_password=hash_password("pass"), is_active=True)
        followed1 = User(username="fw1", email="fw1@test.com", hashed_password=hash_password("pass"), is_active=True)
        followed2 = User(username="fw2", email="fw2@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(user)
        db_session.add(followed1)
        db_session.add(followed2)

        p_user = UserProfile(user_id=user.id)
        p1 = UserProfile(user_id=followed1.id, full_name="Followed 1")
        p2 = UserProfile(user_id=followed2.id, full_name="Followed 2")
        db_session.add(p_user)
        db_session.add(p1)
        db_session.add(p2)

        follow1 = Follow(follower_id=user.id, following_id=followed1.id)
        follow2 = Follow(follower_id=user.id, following_id=followed2.id)
        db_session.add(follow1)
        db_session.add(follow2)
        await db_session.commit()

        # Test
        social_service = SocialService(db_session)
        result = await social_service.get_following("user", page=1, limit=50)

        # Verify
        assert result.total_count == 2
        assert len(result.following) == 2


@pytest.mark.asyncio
class TestSocialServiceGetFollowStatus:
    """
    T195: Unit tests for SocialService.get_follow_status().
    """

    async def test_get_follow_status_returns_true_when_following(
        self,
        db_session: AsyncSession,
    ):
        """Test get_follow_status() returns True when following."""
        # Setup
        user1 = User(username="u1", email="u1@test.com", hashed_password=hash_password("pass"), is_active=True)
        user2 = User(username="u2", email="u2@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        p1 = UserProfile(user_id=user1.id)
        p2 = UserProfile(user_id=user2.id)
        db_session.add(p1)
        db_session.add(p2)
        follow = Follow(follower_id=user1.id, following_id=user2.id)
        db_session.add(follow)
        await db_session.commit()

        # Test
        social_service = SocialService(db_session)
        status = await social_service.get_follow_status("u1", "u2")

        # Verify
        assert status.is_following is True
        assert status.followed_at is not None


@pytest.mark.asyncio
class TestDuplicateFollowPrevention:
    """
    T196: Unit tests for duplicate follow prevention.
    """

    async def test_follow_user_prevents_duplicate(
        self,
        db_session: AsyncSession,
    ):
        """Test that following twice raises error."""
        # Setup
        user1 = User(username="dup1", email="dup1@test.com", hashed_password=hash_password("pass"), is_active=True)
        user2 = User(username="dup2", email="dup2@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        p1 = UserProfile(user_id=user1.id)
        p2 = UserProfile(user_id=user2.id)
        db_session.add(p1)
        db_session.add(p2)
        follow = Follow(follower_id=user1.id, following_id=user2.id)
        db_session.add(follow)
        await db_session.commit()

        # Test - should raise ValueError
        social_service = SocialService(db_session)
        with pytest.raises(ValueError, match="Ya sigues"):
            await social_service.follow_user("dup1", "dup2")


@pytest.mark.asyncio
class TestCounterUpdateOnFollowUnfollow:
    """
    T197: Unit tests for counter update on follow/unfollow.
    """

    async def test_counters_increment_on_follow(
        self,
        db_session: AsyncSession,
    ):
        """Test that counters increment correctly on follow."""
        # Setup
        user1 = User(username="cnt1", email="cnt1@test.com", hashed_password=hash_password("pass"), is_active=True)
        user2 = User(username="cnt2", email="cnt2@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        p1 = UserProfile(user_id=user1.id, following_count=0)
        p2 = UserProfile(user_id=user2.id, followers_count=0)
        db_session.add(p1)
        db_session.add(p2)
        await db_session.commit()

        # Test
        social_service = SocialService(db_session)
        await social_service.follow_user("cnt1", "cnt2")

        # Verify
        await db_session.refresh(p1)
        await db_session.refresh(p2)
        assert p1.following_count == 1
        assert p2.followers_count == 1

    async def test_counters_decrement_on_unfollow(
        self,
        db_session: AsyncSession,
    ):
        """Test that counters decrement correctly on unfollow."""
        # Setup with existing follow
        user1 = User(username="dcnt1", email="dcnt1@test.com", hashed_password=hash_password("pass"), is_active=True)
        user2 = User(username="dcnt2", email="dcnt2@test.com", hashed_password=hash_password("pass"), is_active=True)
        db_session.add(user1)
        db_session.add(user2)
        p1 = UserProfile(user_id=user1.id, following_count=1)
        p2 = UserProfile(user_id=user2.id, followers_count=1)
        db_session.add(p1)
        db_session.add(p2)
        follow = Follow(follower_id=user1.id, following_id=user2.id)
        db_session.add(follow)
        await db_session.commit()

        # Test
        social_service = SocialService(db_session)
        await social_service.unfollow_user("dcnt1", "dcnt2")

        # Verify
        await db_session.refresh(p1)
        await db_session.refresh(p2)
        assert p1.following_count == 0
        assert p2.followers_count == 0
