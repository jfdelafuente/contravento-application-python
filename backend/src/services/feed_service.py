"""
Feed Service - Business logic for personalized feed (Feature 004 - T025 to T027).

Implements hybrid feed algorithm:
1. Chronological trips from followed users
2. Popular community backfill if needed

Success Criteria: SC-001 (<1s p95)
"""

import json
from typing import Any

from sqlalchemy import and_, desc, func, not_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.comment import Comment
from src.models.like import Like
from src.models.share import Share
from src.models.social import Follow
from src.models.trip import Trip, TripStatus, TripTag
from src.models.user import User


class FeedService:
    """Service for personalized feed operations."""

    @staticmethod
    async def get_personalized_feed(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        limit: int = 10,
    ) -> dict[str, Any]:
        """
        T025: Get personalized feed with sequential algorithm.

        Sequential Algorithm (Updated):
        1. Show ALL own trips first (pages 1...M) - both public and private
        2. Show ALL trips from followed users next (pages M+1...N)
        3. When followed trips exhausted, show community backfill (pages N+1...)
        4. No duplicates possible due to sequential ordering

        Args:
            db: Database session
            user_id: Current user ID
            page: Page number (min 1)
            limit: Items per page (min 1, max 50)

        Returns:
            Dict with:
            - trips: List of FeedItem dicts
            - total_count: Total trips available
            - page: Current page
            - limit: Items per page
            - has_more: True if more pages exist

        Success Criteria: SC-001 (<1s p95)
        """
        # Validate pagination
        page = max(1, page)
        limit = max(1, min(50, limit))
        offset = (page - 1) * limit

        # Get total count of own trips (needed for sequential algorithm)
        _, own_count = await FeedService._get_own_trips(
            db=db,
            user_id=user_id,
            limit=0,  # Just get count
            offset=0,
        )

        # Get total count of followed trips (needed for sequential algorithm)
        _, followed_count = await FeedService._get_followed_trips(
            db=db,
            user_id=user_id,
            limit=0,  # Just get count
            offset=0,
        )

        # Sequential Algorithm: Determine which source to use
        if offset < own_count:
            # Still showing own trips
            own_trips, _ = await FeedService._get_own_trips(
                db=db,
                user_id=user_id,
                limit=limit,
                offset=offset,
            )

            trips = own_trips
            remaining_in_page = limit - len(own_trips)

            # If this page contains the last own trips AND there's space remaining,
            # backfill with first followed trips
            if remaining_in_page > 0:
                followed_trips, _ = await FeedService._get_followed_trips(
                    db=db,
                    user_id=user_id,
                    limit=remaining_in_page,
                    offset=0,  # Start from first followed trip
                )

                trips.extend(followed_trips)
                remaining_in_page -= len(followed_trips)

                # If still space remaining, backfill with community trips
                if remaining_in_page > 0:
                    community_trips, community_count = await FeedService._get_community_trips(
                        db=db,
                        user_id=user_id,
                        limit=remaining_in_page,
                        offset=0,  # Start from first community trip
                        exclude_trip_ids=set(),  # No exclusion needed (sequential)
                    )
                    trips.extend(community_trips)
                    total_count = own_count + followed_count + community_count
                else:
                    total_count = own_count + followed_count
            else:
                # Still within own trips pages
                total_count = own_count + followed_count
        elif offset < own_count + followed_count:
            # Exhausted own trips, now showing followed trips
            followed_offset = offset - own_count
            followed_trips, _ = await FeedService._get_followed_trips(
                db=db,
                user_id=user_id,
                limit=limit,
                offset=followed_offset,
            )

            trips = followed_trips
            remaining_in_page = limit - len(followed_trips)

            # If this page contains the last followed trips AND there's space remaining,
            # backfill with first community trips
            if remaining_in_page > 0:
                community_trips, community_count = await FeedService._get_community_trips(
                    db=db,
                    user_id=user_id,
                    limit=remaining_in_page,
                    offset=0,  # Start from first community trip
                    exclude_trip_ids=set(),  # No exclusion needed (sequential)
                )

                trips.extend(community_trips)
                total_count = own_count + followed_count + community_count
            else:
                # Still within followed trips pages
                total_count = own_count + followed_count
        else:
            # Exhausted all own and followed trips, now showing community backfill
            community_offset = offset - own_count - followed_count
            community_trips, community_count = await FeedService._get_community_trips(
                db=db,
                user_id=user_id,
                limit=limit,
                offset=community_offset,
                exclude_trip_ids=set(),  # No exclusion needed (sequential)
            )

            trips = community_trips
            total_count = own_count + followed_count + community_count

        # Calculate has_more
        has_more = (offset + len(trips)) < total_count

        return {
            "trips": trips,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "has_more": has_more,
        }

    @staticmethod
    async def _get_own_trips(
        db: AsyncSession,
        user_id: str,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Get user's own trips (both public and private).

        Args:
            db: Database session
            user_id: Current user ID
            limit: Number of trips to fetch (0 = count only, no trip loading)
            offset: Pagination offset

        Returns:
            Tuple of (trips list, total count)
        """
        # Build base query for count
        count_base_query = select(Trip.trip_id).where(
            and_(
                Trip.user_id == user_id,
                Trip.status == TripStatus.PUBLISHED,
                # Include both public and private trips (user can see their own private trips)
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(count_base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # If limit=0, return count only (optimization for sequential algorithm)
        if limit == 0:
            return [], total_count

        # Get published trips from current user (both public and private)
        trips_query = (
            select(Trip)
            .where(
                and_(
                    Trip.user_id == user_id,
                    Trip.status == TripStatus.PUBLISHED,
                )
            )
            .options(
                selectinload(Trip.user).selectinload(User.profile),
                selectinload(Trip.photos),
                selectinload(Trip.locations),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
                selectinload(Trip.likes),
                selectinload(Trip.comments),
                selectinload(Trip.shares),
            )
            .order_by(desc(Trip.published_at))
            .limit(limit)
            .offset(offset)
        )

        trips_result = await db.execute(trips_query)
        trips = trips_result.scalars().all()

        # Convert to FeedItem dicts
        feed_items = []
        for trip in trips:
            feed_item = await FeedService._trip_to_feed_item(
                trip=trip,
                current_user_id=user_id,
                db=db,
            )
            feed_items.append(feed_item)

        return feed_items, total_count

    @staticmethod
    async def _get_followed_trips(
        db: AsyncSession,
        user_id: str,
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        T026: Get trips from users that current user follows.

        Args:
            db: Database session
            user_id: Current user ID
            limit: Number of trips to fetch (0 = count only, no trip loading)
            offset: Pagination offset

        Returns:
            Tuple of (trips list, total count)
        """
        # Get IDs of users that current user follows
        following_query = select(Follow.following_id).where(Follow.follower_id == user_id)

        following_result = await db.execute(following_query)
        following_ids = [row[0] for row in following_result.fetchall()]

        if not following_ids:
            return [], 0

        # Build base query for count
        count_base_query = select(Trip.trip_id).where(
            and_(
                Trip.user_id.in_(following_ids),
                Trip.user_id != user_id,  # Exclude own trips
                Trip.status == TripStatus.PUBLISHED,
                Trip.is_private.is_(False),  # Exclude private trips
            )
        )

        # Get total count
        count_query = select(func.count()).select_from(count_base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # If limit=0, return count only (optimization for sequential algorithm)
        if limit == 0:
            return [], total_count

        # Get published trips from followed users (exclude own trips)
        trips_query = (
            select(Trip)
            .where(
                and_(
                    Trip.user_id.in_(following_ids),
                    Trip.user_id != user_id,  # Exclude own trips
                    Trip.status == TripStatus.PUBLISHED,
                    Trip.is_private.is_(False),  # Exclude private trips
                )
            )
            .options(
                selectinload(Trip.user).selectinload(User.profile),
                selectinload(Trip.photos),
                selectinload(Trip.locations),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
                selectinload(Trip.likes),
                selectinload(Trip.comments),
                selectinload(Trip.shares),
            )
            .order_by(desc(Trip.published_at))
            .limit(limit)
            .offset(offset)
        )

        trips_result = await db.execute(trips_query)
        trips = trips_result.scalars().all()

        # Convert to FeedItem dicts
        feed_items = []
        for trip in trips:
            feed_item = await FeedService._trip_to_feed_item(
                trip=trip,
                current_user_id=user_id,
                db=db,
            )
            feed_items.append(feed_item)

        return feed_items, total_count

    @staticmethod
    async def _get_community_trips(
        db: AsyncSession,
        user_id: str,
        limit: int,
        offset: int,
        exclude_trip_ids: set[str] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        T027: Get popular community trips for backfill.

        Popular = trips with most interactions (likes + comments + shares).
        Excludes trips already shown from followed users.

        Args:
            db: Database session
            user_id: Current user ID
            limit: Number of trips to fetch
            offset: Pagination offset
            exclude_trip_ids: Trip IDs to exclude (already shown)

        Returns:
            Tuple of (trips list, total count)
        """
        exclude_trip_ids = exclude_trip_ids or set()

        # Subquery for popularity score (likes + comments + shares)
        popularity_score = (
            func.count(Like.id).label("likes")
            + func.count(Comment.id).label("comments")
            + func.count(Share.id).label("shares")
        )

        # Get list of followed user IDs (to exclude from community)
        followed_users_query = select(Follow.following_id).where(Follow.follower_id == user_id)
        followed_users_result = await db.execute(followed_users_query)
        followed_user_ids = [row[0] for row in followed_users_result.fetchall()]

        # Get published trips from community (exclude own trips, followed users' trips, and already shown)
        base_query = (
            select(Trip)
            .outerjoin(Like, Trip.trip_id == Like.trip_id)
            .outerjoin(Comment, Trip.trip_id == Comment.trip_id)
            .outerjoin(Share, Trip.trip_id == Share.trip_id)
            .where(
                and_(
                    Trip.user_id != user_id,  # Exclude own trips
                    not_(Trip.user_id.in_(followed_user_ids))
                    if followed_user_ids
                    else True,  # Exclude followed users
                    Trip.status == TripStatus.PUBLISHED,
                    Trip.is_private.is_(False),  # Exclude private trips
                    not_(Trip.trip_id.in_(exclude_trip_ids)) if exclude_trip_ids else True,
                )
            )
            .group_by(Trip.trip_id)
            .options(
                selectinload(Trip.user).selectinload(User.profile),
                selectinload(Trip.photos),
                selectinload(Trip.locations),
                selectinload(Trip.trip_tags).selectinload(TripTag.tag),
                selectinload(Trip.likes),
                selectinload(Trip.comments),
                selectinload(Trip.shares),
            )
            .order_by(desc(popularity_score), desc(Trip.published_at))
        )

        # Get total count
        count_query = select(func.count()).select_from(
            select(Trip.trip_id)
            .where(
                and_(
                    Trip.user_id != user_id,
                    not_(Trip.user_id.in_(followed_user_ids))
                    if followed_user_ids
                    else True,  # Exclude followed users
                    Trip.status == TripStatus.PUBLISHED,
                    Trip.is_private.is_(False),  # Exclude private trips
                    not_(Trip.trip_id.in_(exclude_trip_ids)) if exclude_trip_ids else True,
                )
            )
            .subquery()
        )
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get paginated trips
        trips_query = base_query.limit(limit).offset(offset)
        trips_result = await db.execute(trips_query)
        trips = trips_result.scalars().all()

        # Convert to FeedItem dicts
        feed_items = []
        for trip in trips:
            feed_item = await FeedService._trip_to_feed_item(
                trip=trip,
                current_user_id=user_id,
                db=db,
            )
            feed_items.append(feed_item)

        return feed_items, total_count

    @staticmethod
    async def _trip_to_feed_item(
        trip: Trip,
        current_user_id: str,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        Convert Trip model to FeedItem dict.

        Includes author info, photos, locations, tags, and interaction counters.

        Args:
            trip: Trip model instance
            current_user_id: Current user ID (for is_liked_by_me and is_following flags)
            db: Database session

        Returns:
            FeedItem dict matching schema
        """
        # Check if current user follows trip author (Feature 004 - US1)
        is_following = None
        if current_user_id and trip.user.id != current_user_id:
            follow_result = await db.execute(
                select(Follow).where(
                    Follow.follower_id == current_user_id, Follow.following_id == trip.user.id
                )
            )
            is_following = follow_result.scalar_one_or_none() is not None

        # Author (UserSummary)
        author = {
            "user_id": trip.user.id,  # Feature 004 - US1
            "username": trip.user.username,
            "full_name": trip.user.profile.full_name if trip.user.profile else None,
            "profile_photo_url": (
                trip.user.profile.profile_photo_url if trip.user.profile else None
            ),
            "is_following": is_following,  # Feature 004 - US1
        }

        # Photos (PhotoSummary array)
        photos = [{"photo_url": photo.photo_url, "caption": photo.caption} for photo in trip.photos]

        # Locations (LocationSummary array)
        locations = [
            {
                "name": loc.name,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
            }
            for loc in trip.locations
        ]

        # Tags (TagSummary array)
        tags = [{"name": tt.tag.name, "normalized": tt.tag.normalized} for tt in trip.trip_tags]

        # Interaction counters
        likes_count = len(trip.likes)
        comments_count = len(trip.comments)
        shares_count = len(trip.shares)

        # is_liked_by_me flag
        is_liked_by_me = any(like.user_id == current_user_id for like in trip.likes)

        return {
            "trip_id": trip.trip_id,
            "title": trip.title,
            "description": trip.description,
            "author": author,
            "photos": photos,
            "distance_km": trip.distance_km,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "locations": locations,
            "tags": tags,
            "likes_count": likes_count,
            "comments_count": comments_count,
            "shares_count": shares_count,
            "is_liked_by_me": is_liked_by_me,
            "created_at": trip.created_at,
        }

    # ============================================================
    # ACTIVITY STREAM METHODS (Feature 018)
    # ============================================================

    @staticmethod
    async def get_user_feed(
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        T022, T023: Get activity feed from followed users with cursor pagination.

        Returns chronological feed of activities (trip published, photo uploaded, achievements)
        from users that current user follows.

        Args:
            db: Database session
            user_id: Current user ID
            limit: Max activities per page (default: 20)
            cursor: Cursor for pagination (None for first page)

        Returns:
            Dict with:
            - activities: List of ActivityFeedItemSchema dicts
            - next_cursor: Cursor for next page (None if last page)
            - has_next: True if more activities exist

        Performance: <2s for 20 activities (SC-001)
        """
        from src.models.activity_feed_item import ActivityFeedItem

        # Import here to avoid circular dependency
        from src.models.user import User
        from src.utils.pagination import decode_cursor, encode_cursor

        # Get list of followed users
        followed_users_stmt = select(Follow.following_id).where(Follow.follower_id == user_id)
        followed_users_result = await db.execute(followed_users_stmt)
        followed_user_ids = [row[0] for row in followed_users_result.fetchall()]

        if not followed_user_ids:
            # User follows nobody - return empty feed
            return {
                "activities": [],
                "next_cursor": None,
                "has_next": False,
            }

        # Build base query for activities from followed users
        query = (
            select(ActivityFeedItem, User)
            .join(User, ActivityFeedItem.user_id == User.id)
            .options(
                joinedload(User.profile),
                selectinload(ActivityFeedItem.likes),  # Load likes for counting
            )
            .where(ActivityFeedItem.user_id.in_(followed_user_ids))
        )

        # Apply cursor filtering
        if cursor:
            try:
                cursor_data = decode_cursor(cursor)
                cursor_created_at = cursor_data["created_at"]
                cursor_activity_id = cursor_data["activity_id"]

                query = query.where(
                    (ActivityFeedItem.created_at < cursor_created_at)
                    | (
                        and_(
                            ActivityFeedItem.created_at == cursor_created_at,
                            ActivityFeedItem.activity_id < cursor_activity_id,
                        )
                    )
                )
            except ValueError:
                # Invalid cursor - ignore and start from beginning
                pass

        # Order by created_at DESC, activity_id DESC (for stable pagination)
        query = query.order_by(
            desc(ActivityFeedItem.created_at), desc(ActivityFeedItem.activity_id)
        )

        # Fetch limit + 1 to detect if there are more pages
        query = query.limit(limit + 1)

        result = await db.execute(query)
        rows = result.all()

        # Check if there are more pages
        has_next = len(rows) > limit
        activities_data = rows[:limit]  # Take only requested limit

        # Build activity list
        activities = []
        for activity_item, user in activities_data:
            # Get counts for likes and comments
            likes_count = len(activity_item.likes)
            comments_count = 0  # TODO: Implement in Phase 5 (Comments)

            # is_liked_by_me flag - check if current user liked this activity
            is_liked_by_me = any(like.user_id == user_id for like in activity_item.likes)

            # Parse metadata from JSON
            metadata = (
                json.loads(activity_item.activity_metadata)
                if isinstance(activity_item.activity_metadata, str)
                else activity_item.activity_metadata
                if isinstance(activity_item.activity_metadata, dict)
                else {}
            )

            # Enrich metadata with trip_id from related_id for TRIP_PUBLISHED activities
            activity_type = (
                activity_item.activity_type.value
                if hasattr(activity_item.activity_type, "value")
                else activity_item.activity_type
            )
            if activity_type == "TRIP_PUBLISHED" and activity_item.related_id:
                metadata["trip_id"] = activity_item.related_id

            activities.append(
                {
                    "activity_id": activity_item.activity_id,
                    "user": {
                        "user_id": user.id,
                        "username": user.username,
                        "photo_url": user.profile.profile_photo_url if user.profile else None,
                    },
                    "activity_type": activity_type,
                    "metadata": metadata,
                    "created_at": activity_item.created_at,
                    "likes_count": likes_count,
                    "comments_count": comments_count,
                    "is_liked_by_me": is_liked_by_me,
                }
            )

        # Generate next cursor
        next_cursor = None
        if has_next and activities:
            last_activity = activities_data[-1][0]
            next_cursor = encode_cursor(last_activity.created_at, last_activity.activity_id)

        return {
            "activities": activities,
            "next_cursor": next_cursor,
            "has_next": has_next,
        }

    @staticmethod
    async def create_feed_activity(
        db: AsyncSession,
        user_id: str,
        activity_type: str,
        related_id: str,
        metadata: dict,
    ) -> None:
        """
        T024: Create feed activity with privacy check.

        Creates an activity feed item if user's profile is public.
        Private users don't generate feed activities.

        Args:
            db: Database session
            user_id: User who performed the activity
            activity_type: Type (TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED)
            related_id: Related entity ID (trip_id, photo_id, achievement_id)
            metadata: Activity metadata (JSON)

        Returns:
            None (activity created silently)
        """
        from datetime import UTC, datetime
        from uuid import uuid4

        from src.models.activity_feed_item import ActivityFeedItem, ActivityType
        from src.models.user import User

        # Check if user profile is public
        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            return  # User not found - skip activity creation

        # TODO: Check profile visibility when UserProfile model is available
        # For now, create activity for all users
        # Future: if user.profile.profile_visibility != 'public': return

        # Create activity feed item
        activity = ActivityFeedItem(
            activity_id=str(uuid4()),
            user_id=user_id,
            activity_type=ActivityType(activity_type),
            related_id=related_id,
            activity_metadata=metadata,  # Pass dict directly - SQLAlchemy JSON handles it
            created_at=datetime.now(UTC),
        )

        db.add(activity)
        await db.commit()
