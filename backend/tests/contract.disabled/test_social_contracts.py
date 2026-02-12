"""
Contract tests for Social Features API endpoints.

Validates that API responses match the OpenAPI specification in
specs/001-user-profiles/contracts/social.yaml.

Tests verify:
- Response structure matches schema
- Required fields are present
- Data types are correct
- Success/error response format
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.social import Follow
from src.models.user import User, UserProfile
from src.utils.security import create_access_token, hash_password


@pytest.mark.asyncio
class TestFollowUserContract:
    """
    T181: Contract test for POST /users/{username}/follow.

    Validates response structure against OpenAPI schema.
    """

    async def test_follow_user_success_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test POST /users/{username}/follow returns correct schema on success."""
        # Create two users
        user1 = User(
            username="follower_user",
            email="follower@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            username="followed_user",
            email="followed@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user1)
        db_session.add(user2)

        profile1 = UserProfile(user_id=user1.id, full_name="Follower User")
        profile2 = UserProfile(user_id=user2.id, full_name="Followed User")
        db_session.add(profile1)
        db_session.add(profile2)
        await db_session.commit()

        # Get auth token for user1
        token = create_access_token({"sub": user1.id, "type": "access"})

        # Make request
        response = await async_client.post(
            f"/users/{user2.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Verify status code
        assert response.status_code == 200

        # Verify standardized response format
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert data["success"] is True

        # Verify follow response structure
        follow_data = data["data"]
        assert "follower" in follow_data
        assert "following" in follow_data
        assert "created_at" in follow_data

        # Verify follower structure
        assert "username" in follow_data["follower"]
        assert "full_name" in follow_data["follower"]
        assert "photo_url" in follow_data["follower"]
        assert follow_data["follower"]["username"] == user1.username

        # Verify following structure
        assert "username" in follow_data["following"]
        assert "full_name" in follow_data["following"]
        assert "photo_url" in follow_data["following"]
        assert follow_data["following"]["username"] == user2.username

        # Verify message
        assert isinstance(data["message"], str)
        assert user2.username in data["message"]

    async def test_follow_self_error_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test POST /users/{username}/follow returns correct error for self-follow."""
        user = User(
            username="self_follower",
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
        response = await async_client.post(
            f"/users/{user.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Verify status code
        assert response.status_code == 400

        # Verify error response format
        data = response.json()
        assert data["success"] is False
        assert data["data"] is None

        # Verify error structure
        error = data["error"]
        assert error["code"] == "CANNOT_FOLLOW_SELF"
        assert isinstance(error["message"], str)

    async def test_follow_already_following_error_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test POST /users/{username}/follow returns correct error for duplicate follow."""
        user1 = User(
            username="user1",
            email="user1@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            username="user2",
            email="user2@test.com",
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

        # Create existing follow
        follow = Follow(follower_id=user1.id, following_id=user2.id)
        db_session.add(follow)
        await db_session.commit()

        token = create_access_token({"sub": user1.id, "type": "access"})

        # Try to follow again
        response = await async_client.post(
            f"/users/{user2.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Verify status code
        assert response.status_code == 400

        # Verify error
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "ALREADY_FOLLOWING"


@pytest.mark.asyncio
class TestUnfollowUserContract:
    """
    T182: Contract test for DELETE /users/{username}/follow.

    Validates response structure against OpenAPI schema.
    """

    async def test_unfollow_user_success_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test DELETE /users/{username}/follow returns correct schema on success."""
        user1 = User(
            username="unfollower",
            email="unfollower@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            username="unfollowed",
            email="unfollowed@test.com",
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

        # Create follow relationship
        follow = Follow(follower_id=user1.id, following_id=user2.id)
        db_session.add(follow)
        await db_session.commit()

        token = create_access_token({"sub": user1.id, "type": "access"})

        # Unfollow
        response = await async_client.delete(
            f"/users/{user2.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Verify status code
        assert response.status_code == 200

        # Verify response format
        data = response.json()
        assert data["success"] is True
        assert "message" in data
        assert isinstance(data["message"], str)
        assert user2.username in data["message"]

    async def test_unfollow_not_following_error_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test DELETE /users/{username}/follow returns correct error when not following."""
        user1 = User(
            username="user_a",
            email="usera@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            username="user_b",
            email="userb@test.com",
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

        token = create_access_token({"sub": user1.id, "type": "access"})

        # Try to unfollow when not following
        response = await async_client.delete(
            f"/users/{user2.username}/follow", headers={"Authorization": f"Bearer {token}"}
        )

        # Verify status code
        assert response.status_code == 400

        # Verify error
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOLLOWING"


@pytest.mark.asyncio
class TestGetFollowersContract:
    """
    T183: Contract test for GET /users/{username}/followers.

    Validates response structure against OpenAPI schema.
    """

    async def test_get_followers_success_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/followers returns correct schema."""
        # Create target user
        target_user = User(
            username="popular_user",
            email="popular@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(target_user)

        target_profile = UserProfile(user_id=target_user.id)
        db_session.add(target_profile)

        # Create 2 followers
        follower1 = User(
            username="follower1",
            email="follower1@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        follower2 = User(
            username="follower2",
            email="follower2@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(follower1)
        db_session.add(follower2)

        profile1 = UserProfile(user_id=follower1.id, bio="Follower 1 bio", cycling_type="road")
        profile2 = UserProfile(user_id=follower2.id, bio="Follower 2 bio", cycling_type="mountain")
        db_session.add(profile1)
        db_session.add(profile2)

        # Create follows
        follow1 = Follow(follower_id=follower1.id, following_id=target_user.id)
        follow2 = Follow(follower_id=follower2.id, following_id=target_user.id)
        db_session.add(follow1)
        db_session.add(follow2)
        await db_session.commit()

        # Make request
        response = await async_client.get(f"/users/{target_user.username}/followers")

        # Verify status code
        assert response.status_code == 200

        # Verify response format
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None

        # Verify followers list structure
        followers_data = data["data"]
        assert "followers" in followers_data
        assert "total_count" in followers_data
        assert "page" in followers_data
        assert "limit" in followers_data
        assert "has_more" in followers_data

        # Verify data types
        assert isinstance(followers_data["followers"], list)
        assert isinstance(followers_data["total_count"], int)
        assert isinstance(followers_data["page"], int)
        assert isinstance(followers_data["limit"], int)
        assert isinstance(followers_data["has_more"], bool)

        # Verify follower item structure
        if followers_data["followers"]:
            follower_item = followers_data["followers"][0]
            assert "username" in follower_item
            assert "full_name" in follower_item
            assert "photo_url" in follower_item
            assert "bio" in follower_item
            assert "cycling_type" in follower_item
            assert "followed_at" in follower_item


@pytest.mark.asyncio
class TestGetFollowingContract:
    """
    T184: Contract test for GET /users/{username}/following.

    Validates response structure against OpenAPI schema.
    """

    async def test_get_following_success_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/following returns correct schema."""
        # Create user who follows others
        user = User(
            username="active_follower",
            email="active@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)

        # Create 2 users to follow
        followed1 = User(
            username="followed1",
            email="followed1@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        followed2 = User(
            username="followed2",
            email="followed2@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(followed1)
        db_session.add(followed2)

        profile1 = UserProfile(user_id=followed1.id, bio="Followed 1 bio", cycling_type="gravel")
        profile2 = UserProfile(user_id=followed2.id, bio="Followed 2 bio", cycling_type="touring")
        db_session.add(profile1)
        db_session.add(profile2)

        # Create follows
        follow1 = Follow(follower_id=user.id, following_id=followed1.id)
        follow2 = Follow(follower_id=user.id, following_id=followed2.id)
        db_session.add(follow1)
        db_session.add(follow2)
        await db_session.commit()

        # Make request
        response = await async_client.get(f"/users/{user.username}/following")

        # Verify status code
        assert response.status_code == 200

        # Verify response format
        data = response.json()
        assert data["success"] is True

        # Verify following list structure
        following_data = data["data"]
        assert "following" in following_data
        assert "total_count" in following_data
        assert "page" in following_data
        assert "limit" in following_data
        assert "has_more" in following_data

        # Verify following item structure
        if following_data["following"]:
            following_item = following_data["following"][0]
            assert "username" in following_item
            assert "full_name" in following_item
            assert "photo_url" in following_item
            assert "bio" in following_item
            assert "cycling_type" in following_item
            assert "followed_at" in following_item


@pytest.mark.asyncio
class TestGetFollowStatusContract:
    """
    T185: Contract test for GET /users/{username}/follow-status.

    Validates response structure against OpenAPI schema.
    """

    async def test_get_follow_status_following_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/follow-status returns correct schema when following."""
        user1 = User(
            username="checker",
            email="checker@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            username="checked",
            email="checked@test.com",
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

        # Create follow
        follow = Follow(follower_id=user1.id, following_id=user2.id)
        db_session.add(follow)
        await db_session.commit()

        token = create_access_token({"sub": user1.id, "type": "access"})

        # Make request
        response = await async_client.get(
            f"/users/{user2.username}/follow-status", headers={"Authorization": f"Bearer {token}"}
        )

        # Verify status code
        assert response.status_code == 200

        # Verify response format
        data = response.json()
        assert data["success"] is True

        # Verify follow status structure
        status_data = data["data"]
        assert "is_following" in status_data
        assert "followed_at" in status_data

        # Verify data types
        assert isinstance(status_data["is_following"], bool)
        assert status_data["is_following"] is True
        assert status_data["followed_at"] is not None

    async def test_get_follow_status_not_following_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/follow-status returns correct schema when not following."""
        user1 = User(
            username="checker2",
            email="checker2@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        user2 = User(
            username="checked2",
            email="checked2@test.com",
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

        token = create_access_token({"sub": user1.id, "type": "access"})

        # Make request
        response = await async_client.get(
            f"/users/{user2.username}/follow-status", headers={"Authorization": f"Bearer {token}"}
        )

        # Verify status code
        assert response.status_code == 200

        # Verify response
        data = response.json()
        status_data = data["data"]
        assert status_data["is_following"] is False
        assert status_data["followed_at"] is None
