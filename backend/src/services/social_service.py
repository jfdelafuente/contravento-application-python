"""
Social service for managing follow relationships.

Business logic for social features including:
- Follow/unfollow operations
- Followers and following lists
- Follow status checking
- Counter management
"""

import logging
from datetime import datetime
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.social import Follow
from src.models.user import User, UserProfile
from src.schemas.social import (
    FollowersListResponse,
    FollowingListResponse,
    FollowResponse,
    FollowStatusResponse,
    UserSummary,
)

logger = logging.getLogger(__name__)


class SocialService:
    """
    Social service for managing follow relationships.

    Handles follow/unfollow operations, listing followers/following,
    and checking follow status.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize social service.

        Args:
            db: Database session
        """
        self.db = db

    async def follow_user(self, follower_username: str, following_username: str) -> FollowResponse:
        """
        T206: Follow a user.

        Creates a follow relationship and updates counters.

        Args:
            follower_username: Username of the follower
            following_username: Username to follow

        Returns:
            FollowResponse with updated counters

        Raises:
            ValueError: If users not found, self-follow, or already following
        """
        # Prevent self-follow
        if follower_username == following_username:
            raise ValueError("No puedes seguirte a ti mismo")

        # Get both users
        result = await self.db.execute(select(User).where(User.username == follower_username))
        follower_user = result.scalar_one_or_none()
        if not follower_user:
            raise ValueError(f"El usuario '{follower_username}' no existe")

        result = await self.db.execute(select(User).where(User.username == following_username))
        following_user = result.scalar_one_or_none()
        if not following_user:
            raise ValueError(f"El usuario '{following_username}' no existe")

        # Check if already following
        result = await self.db.execute(
            select(Follow).where(
                Follow.follower_id == follower_user.id, Follow.following_id == following_user.id
            )
        )
        existing_follow = result.scalar_one_or_none()
        if existing_follow:
            raise ValueError(f"Ya sigues a {following_username}")

        # Create follow relationship
        follow = Follow(
            id=str(uuid4()),
            follower_id=follower_user.id,
            following_id=following_user.id,
            created_at=datetime.utcnow(),
        )
        self.db.add(follow)

        # Update counters (T222)
        follower_profile = await self._get_or_create_profile(follower_user.id)
        following_profile = await self._get_or_create_profile(following_user.id)

        follower_profile.following_count += 1
        following_profile.followers_count += 1

        await self.db.commit()

        logger.info(f"User {follower_username} followed {following_username}")

        return FollowResponse(
            success=True,
            message=f"Ahora sigues a {following_username}",
            follower_username=follower_username,
            following_username=following_username,
            is_following=True,
            follower_following_count=follower_profile.following_count,
            following_followers_count=following_profile.followers_count,
        )

    async def unfollow_user(
        self, follower_username: str, following_username: str
    ) -> FollowResponse:
        """
        T207: Unfollow a user.

        Removes follow relationship and updates counters.

        Args:
            follower_username: Username of the follower
            following_username: Username to unfollow

        Returns:
            FollowResponse with updated counters

        Raises:
            ValueError: If users not found or not following
        """
        # Get both users
        result = await self.db.execute(select(User).where(User.username == follower_username))
        follower_user = result.scalar_one_or_none()
        if not follower_user:
            raise ValueError(f"El usuario '{follower_username}' no existe")

        result = await self.db.execute(select(User).where(User.username == following_username))
        following_user = result.scalar_one_or_none()
        if not following_user:
            raise ValueError(f"El usuario '{following_username}' no existe")

        # Check if following
        result = await self.db.execute(
            select(Follow).where(
                Follow.follower_id == follower_user.id, Follow.following_id == following_user.id
            )
        )
        follow = result.scalar_one_or_none()
        if not follow:
            raise ValueError(f"No sigues a {following_username}")

        # Delete follow relationship
        await self.db.delete(follow)

        # Update counters (T223)
        follower_profile = await self._get_or_create_profile(follower_user.id)
        following_profile = await self._get_or_create_profile(following_user.id)

        follower_profile.following_count = max(0, follower_profile.following_count - 1)
        following_profile.followers_count = max(0, following_profile.followers_count - 1)

        await self.db.commit()

        logger.info(f"User {follower_username} unfollowed {following_username}")

        return FollowResponse(
            success=True,
            message=f"Has dejado de seguir a {following_username}",
            follower_username=follower_username,
            following_username=following_username,
            is_following=False,
            follower_following_count=follower_profile.following_count,
            following_followers_count=following_profile.followers_count,
        )

    async def get_followers(
        self, username: str, page: int = 1, limit: int = 50
    ) -> FollowersListResponse:
        """
        T208: Get paginated list of followers.

        Args:
            username: Username to get followers for
            page: Page number (1-indexed)
            limit: Results per page (max 50)

        Returns:
            FollowersListResponse with paginated followers

        Raises:
            ValueError: If user not found
        """
        # Validate pagination
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 50

        # Get user
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        # Get total count
        result = await self.db.execute(
            select(func.count(Follow.id)).where(Follow.following_id == user.id)
        )
        total_count = result.scalar() or 0

        # Get paginated followers
        offset = (page - 1) * limit
        result = await self.db.execute(
            select(User, UserProfile)
            .join(Follow, Follow.follower_id == User.id)
            .outerjoin(UserProfile, UserProfile.user_id == User.id)
            .where(Follow.following_id == user.id)
            .order_by(Follow.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = result.all()

        # Build UserSummary list
        followers = []
        for user_row, profile_row in rows:
            followers.append(
                UserSummary(
                    username=user_row.username,
                    full_name=profile_row.full_name if profile_row else None,
                    profile_photo_url=profile_row.profile_photo_url if profile_row else None,
                    bio=profile_row.bio if profile_row else None,
                    followers_count=profile_row.followers_count if profile_row else 0,
                    following_count=profile_row.following_count if profile_row else 0,
                )
            )

        has_more = (offset + len(followers)) < total_count

        return FollowersListResponse(
            followers=followers,
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=has_more,
        )

    async def get_following(
        self, username: str, page: int = 1, limit: int = 50
    ) -> FollowingListResponse:
        """
        T209: Get paginated list of users being followed.

        Args:
            username: Username to get following list for
            page: Page number (1-indexed)
            limit: Results per page (max 50)

        Returns:
            FollowingListResponse with paginated following

        Raises:
            ValueError: If user not found
        """
        # Validate pagination
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 50

        # Get user
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        # Get total count
        result = await self.db.execute(
            select(func.count(Follow.id)).where(Follow.follower_id == user.id)
        )
        total_count = result.scalar() or 0

        # Get paginated following
        offset = (page - 1) * limit
        result = await self.db.execute(
            select(User, UserProfile)
            .join(Follow, Follow.following_id == User.id)
            .outerjoin(UserProfile, UserProfile.user_id == User.id)
            .where(Follow.follower_id == user.id)
            .order_by(Follow.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = result.all()

        # Build UserSummary list
        following = []
        for user_row, profile_row in rows:
            following.append(
                UserSummary(
                    username=user_row.username,
                    full_name=profile_row.full_name if profile_row else None,
                    profile_photo_url=profile_row.profile_photo_url if profile_row else None,
                    bio=profile_row.bio if profile_row else None,
                    followers_count=profile_row.followers_count if profile_row else 0,
                    following_count=profile_row.following_count if profile_row else 0,
                )
            )

        has_more = (offset + len(following)) < total_count

        return FollowingListResponse(
            following=following,
            total_count=total_count,
            page=page,
            limit=limit,
            has_more=has_more,
        )

    async def get_follow_status(
        self, follower_username: str, following_username: str
    ) -> FollowStatusResponse:
        """
        T210: Check if follower follows following.

        Args:
            follower_username: Username of potential follower
            following_username: Username of potential following

        Returns:
            FollowStatusResponse with follow status

        Raises:
            ValueError: If either user not found
        """
        # Get both users
        result = await self.db.execute(select(User).where(User.username == follower_username))
        follower_user = result.scalar_one_or_none()
        if not follower_user:
            raise ValueError(f"El usuario '{follower_username}' no existe")

        result = await self.db.execute(select(User).where(User.username == following_username))
        following_user = result.scalar_one_or_none()
        if not following_user:
            raise ValueError(f"El usuario '{following_username}' no existe")

        # Check follow status
        result = await self.db.execute(
            select(Follow).where(
                Follow.follower_id == follower_user.id, Follow.following_id == following_user.id
            )
        )
        follow = result.scalar_one_or_none()

        if follow:
            return FollowStatusResponse(
                is_following=True,
                followed_at=follow.created_at,
            )
        else:
            return FollowStatusResponse(
                is_following=False,
                followed_at=None,
            )

    async def _get_or_create_profile(self, user_id: str) -> UserProfile:
        """
        Get or create user profile.

        Args:
            user_id: User ID

        Returns:
            UserProfile instance
        """
        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        profile = result.scalar_one_or_none()

        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            await self.db.flush()

        return profile
