"""
Integration tests for follow/unfollow workflows.

Tests complete user flows for social features including
following, unfollowing, listing followers/following, and counter updates.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.social import Follow
from src.models.user import User, UserProfile
from src.utils.security import create_access_token, hash_password


@pytest.mark.asyncio
class TestFollowWorkflow:
    """
    T186: Integration test for full follow workflow.

    Tests: follow → verify lists → unfollow → verify lists updated
    """

    async def test_complete_follow_unfollow_workflow(
        self,
        db_session: AsyncSession,
        client: AsyncClient,
    ):
        """
        Test complete workflow:
        1. User A follows User B
        2. Verify User B appears in A's following list
        3. Verify User A appears in B's followers list
        4. User A unfollows User B
        5. Verify lists are empty
        """
        # 1. Create two users
        user_a = User(
            username="user_a",
            email="user_a@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user_b = User(
            username="user_b",
            email="user_b@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user_a)
        db_session.add(user_b)

        profile_a = UserProfile(user_id=user_a.id)
        profile_b = UserProfile(user_id=user_b.id)
        db_session.add(profile_a)
        db_session.add(profile_b)
        await db_session.commit()

        token_a = create_access_token({"sub": user_a.id, "type": "access"})

        # 2. User A follows User B
        follow_response = await client.post(
            f"/users/{user_b.username}/follow", headers={"Authorization": f"Bearer {token_a}"}
        )
        assert follow_response.status_code == 200

        # 3. Verify User B in A's following list
        following_response = await client.get(f"/users/{user_a.username}/following")
        assert following_response.status_code == 200
        following_data = following_response.json()["data"]
        assert following_data["total_count"] == 1
        assert following_data["following"][0]["username"] == user_b.username

        # 4. Verify User A in B's followers list
        followers_response = await client.get(f"/users/{user_b.username}/followers")
        assert followers_response.status_code == 200
        followers_data = followers_response.json()["data"]
        assert followers_data["total_count"] == 1
        assert followers_data["followers"][0]["username"] == user_a.username

        # 5. User A unfollows User B
        unfollow_response = await client.delete(
            f"/users/{user_b.username}/follow", headers={"Authorization": f"Bearer {token_a}"}
        )
        assert unfollow_response.status_code == 200

        # 6. Verify lists are now empty
        following_response2 = await client.get(f"/users/{user_a.username}/following")
        assert following_response2.json()["data"]["total_count"] == 0

        followers_response2 = await client.get(f"/users/{user_b.username}/followers")
        assert followers_response2.json()["data"]["total_count"] == 0


@pytest.mark.asyncio
class TestFollowerCounterUpdates:
    """
    T187: Integration test for follower/following counter updates.

    Verifies counters in UserProfile are updated correctly.
    """

    async def test_counters_update_on_follow_unfollow(
        self,
        db_session: AsyncSession,
        client: AsyncClient,
    ):
        """Test that followers_count and following_count update correctly."""
        # Create users
        user1 = User(
            username="counter_user1",
            email="counter1@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            username="counter_user2",
            email="counter2@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user1)
        db_session.add(user2)

        profile1 = UserProfile(user_id=user1.id)
        profile2 = UserProfile(user_id=user2.id)
        db_session.add(profile1)
        db_session.add(profile2)
        await db_session.commit()

        # Initial counters should be 0
        assert profile1.following_count == 0
        assert profile2.followers_count == 0

        # User1 follows User2
        token = create_access_token({"sub": user1.id, "type": "access"})
        await client.post(
            f"/users/{user2.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Refresh and verify counters
        await db_session.refresh(profile1)
        await db_session.refresh(profile2)
        assert profile1.following_count == 1  # User1 follows 1 person
        assert profile2.followers_count == 1  # User2 has 1 follower

        # User1 unfollows User2
        await client.delete(
            f"/users/{user2.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Refresh and verify counters back to 0
        await db_session.refresh(profile1)
        await db_session.refresh(profile2)
        assert profile1.following_count == 0
        assert profile2.followers_count == 0


@pytest.mark.asyncio
class TestFollowersPagination:
    """
    T188: Integration test for pagination of followers list.

    Tests pagination with 50+ users.
    """

    async def test_followers_pagination_with_50_plus_users(
        self,
        db_session: AsyncSession,
        client: AsyncClient,
    ):
        """Test followers list pagination with more than 50 followers."""
        # Create target user
        target = User(
            username="celebrity",
            email="celebrity@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(target)
        target_profile = UserProfile(user_id=target.id)
        db_session.add(target_profile)
        await db_session.flush()

        # Create 60 followers
        for i in range(60):
            follower = User(
                username=f"follower_{i}",
                email=f"follower{i}@test.com",
                hashed_password=hash_password("password123"),
                is_active=True,
                is_verified=True,
            )
            db_session.add(follower)
            await db_session.flush()

            profile = UserProfile(user_id=follower.id)
            db_session.add(profile)

            follow = Follow(follower_id=follower.id, following_id=target.id)
            db_session.add(follow)

        await db_session.commit()

        # Get first page (default limit is 50)
        response1 = await client.get(f"/users/{target.username}/followers")
        assert response1.status_code == 200
        data1 = response1.json()["data"]

        assert data1["total_count"] == 60
        assert len(data1["followers"]) == 50  # Max 50 per page
        assert data1["has_more"] is True
        assert data1["page"] == 1

        # Get second page
        response2 = await client.get(f"/users/{target.username}/followers?page=2")
        assert response2.status_code == 200
        data2 = response2.json()["data"]

        assert data2["total_count"] == 60
        assert len(data2["followers"]) == 10  # Remaining 10
        assert data2["has_more"] is False
        assert data2["page"] == 2


@pytest.mark.asyncio
class TestSelfFollowPrevention:
    """
    T189: Integration test for self-follow prevention.

    Verifies users cannot follow themselves.
    """

    async def test_cannot_follow_self(
        self,
        db_session: AsyncSession,
        client: AsyncClient,
    ):
        """Test that self-follow is prevented."""
        user = User(
            username="self_user",
            email="self@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)
        await db_session.commit()

        token = create_access_token({"sub": user.id, "type": "access"})

        # Try to follow self
        response = await client.post(
            f"/users/{user.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Should return 400 error
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "CANNOT_FOLLOW_SELF"

        # Verify no follow relationship created
        result = await db_session.execute(select(Follow).where(Follow.follower_id == user.id))
        follows = result.scalars().all()
        assert len(follows) == 0


@pytest.mark.asyncio
class TestUnauthenticatedFollowRedirect:
    """
    T190: Integration test for unauthenticated follow redirect.

    Verifies unauthenticated users get 401 error.
    """

    async def test_unauthenticated_follow_returns_401(
        self,
        db_session: AsyncSession,
        client: AsyncClient,
    ):
        """Test that unauthenticated follow attempts return 401."""
        user = User(
            username="target_user",
            email="target@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)
        await db_session.commit()

        # Try to follow without auth
        response = await client.post(f"/users/{user.username}/follow")

        # Should return 401
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
