"""
Feed Service - Business logic for personalized feed (Feature 004 - T025 to T027).

Implements hybrid feed algorithm:
1. Chronological trips from followed users
2. Popular community backfill if needed

Success Criteria: SC-001 (<1s p95)
"""

from datetime import UTC, datetime
from typing import Any
from sqlalchemy import and_, desc, func, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.trip import Trip, TripStatus, TripTag
from src.models.user import User, UserProfile
from src.models.like import Like
from src.models.comment import Comment
from src.models.share import Share
from src.models.social import Follow


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

        Sequential Algorithm (Bug #1 Fix):
        1. Show ALL trips from followed users first (pages 1...N)
        2. When followed trips exhausted, show community backfill (pages N+1...)
        3. No duplicates possible due to sequential ordering

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

        # Get total count of followed trips (needed for sequential algorithm)
        _, followed_count = await FeedService._get_followed_trips(
            db=db,
            user_id=user_id,
            limit=0,  # Just get count
            offset=0,
        )

        # Sequential Algorithm: Determine which source to use
        if offset < followed_count:
            # Still showing trips from followed users
            followed_trips, _ = await FeedService._get_followed_trips(
                db=db,
                user_id=user_id,
                limit=limit,
                offset=offset,
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
                total_count = followed_count + community_count
            else:
                # Still within followed trips pages
                total_count = followed_count
        else:
            # Exhausted all followed trips, now showing community backfill
            community_offset = offset - followed_count
            community_trips, community_count = await FeedService._get_community_trips(
                db=db,
                user_id=user_id,
                limit=limit,
                offset=community_offset,
                exclude_trip_ids=set(),  # No exclusion needed (sequential)
            )

            trips = community_trips
            total_count = followed_count + community_count

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
