"""
Statistics service for managing user stats and achievements.

Business logic for:
- Calculating and updating user statistics
- Checking and awarding achievements
- Retrieving stats and achievements
"""

import logging
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.stats import Achievement, UserAchievement, UserStats
from src.models.user import User
from src.schemas.stats import (
    AchievementDefinition,
    AchievementDefinitionList,
    AchievementResponse,
    CountryInfo,
    StatsResponse,
    UserAchievementResponse,
)

logger = logging.getLogger(__name__)

# Country code to Spanish name mapping
COUNTRY_NAMES = {
    "ES": "España",
    "FR": "Francia",
    "IT": "Italia",
    "PT": "Portugal",
    "DE": "Alemania",
    "GB": "Reino Unido",
    "NL": "Países Bajos",
    "BE": "Bélgica",
    "CH": "Suiza",
    "AT": "Austria",
    "US": "Estados Unidos",
    "CA": "Canadá",
    "MX": "México",
    "AR": "Argentina",
    "CL": "Chile",
    "BR": "Brasil",
    "CO": "Colombia",
    "PE": "Perú",
    # Add more as needed
}


class StatsService:
    """
    Statistics service for managing user stats and achievements.

    Handles stats calculation, achievement checking, and data retrieval.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize stats service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_user_stats(self, username: str) -> StatsResponse:
        """
        T159: Get user statistics.

        Retrieves and formats user cycling statistics with country names.

        Args:
            username: Username to get stats for

        Returns:
            StatsResponse with formatted statistics

        Raises:
            ValueError: If user not found
        """
        # Get user
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        # Get or create stats
        result = await self.db.execute(select(UserStats).where(UserStats.user_id == user.id))
        stats = result.scalar_one_or_none()

        if not stats:
            # Create empty stats for new user
            stats = UserStats(
                user_id=user.id,
                countries_visited=[],  # Explicitly set empty list
            )
            self.db.add(stats)
            await self.db.commit()
            await self.db.refresh(stats)

        # Convert country codes to CountryInfo objects
        # Handle None case for countries_visited (SQLite/JSON quirk)
        countries_list = stats.countries_visited if stats.countries_visited is not None else []
        countries = [
            CountryInfo(
                code=code, name=COUNTRY_NAMES.get(code, code)  # Fallback to code if name not found
            )
            for code in countries_list
        ]

        return StatsResponse(
            total_trips=stats.total_trips,
            total_kilometers=stats.total_kilometers,
            countries_visited=countries,
            total_photos=stats.total_photos,
            achievements_count=stats.achievements_count,
            last_trip_date=stats.last_trip_date,
            updated_at=stats.updated_at,
        )

    async def get_user_achievements(self, username: str) -> UserAchievementResponse:
        """
        T160: Get user's earned achievements.

        Retrieves all achievements earned by the user, ordered by most recent first.

        Args:
            username: Username to get achievements for

        Returns:
            UserAchievementResponse with list of earned achievements

        Raises:
            ValueError: If user not found
        """
        # T226: Optimized query with eager loading for user achievements
        result = await self.db.execute(
            select(User)
            .options(joinedload(User.user_achievements).joinedload(UserAchievement.achievement))
            .where(User.username == username)
        )
        user = result.unique().scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        # Sort achievements by awarded_at (most recent first)
        user_achievements = sorted(
            user.user_achievements, key=lambda ua: ua.awarded_at, reverse=True
        )

        # Format response
        achievements = [
            AchievementResponse(
                code=ua.achievement.code,
                name=ua.achievement.name,
                description=ua.achievement.description,
                badge_icon=ua.achievement.badge_icon,
                requirement_type=ua.achievement.requirement_type,
                requirement_value=ua.achievement.requirement_value,
                awarded_at=ua.awarded_at,
            )
            for ua in user_achievements
        ]

        return UserAchievementResponse(
            achievements=achievements,
            total_count=len(achievements),
        )

    async def list_all_achievements(self) -> AchievementDefinitionList:
        """
        List all available achievements.

        Returns all achievement definitions in the system.

        Returns:
            AchievementDefinitionList with all achievements
        """
        result = await self.db.execute(select(Achievement).order_by(Achievement.requirement_value))
        achievements = result.scalars().all()

        achievement_defs = [
            AchievementDefinition(
                code=achievement.code,
                name=achievement.name,
                description=achievement.description,
                badge_icon=achievement.badge_icon,
                requirement_type=achievement.requirement_type,
                requirement_value=achievement.requirement_value,
            )
            for achievement in achievements
        ]

        return AchievementDefinitionList(
            achievements=achievement_defs,
            total_count=len(achievement_defs),
        )

    async def update_stats_on_trip_publish(
        self,
        user_id: str,
        distance_km: float,
        country_code: str,
        photos_count: int,
        trip_date: date,
    ) -> None:
        """
        T161: Update stats when a trip is published.

        Increments statistics and checks for newly earned achievements.

        Args:
            user_id: User ID
            distance_km: Trip distance in kilometers
            country_code: ISO country code (e.g., 'ES')
            photos_count: Number of photos in trip
            trip_date: Date of the trip
        """
        # Get or create stats
        result = await self.db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = result.scalar_one_or_none()

        if not stats:
            stats = UserStats(
                user_id=user_id,
                total_trips=0,
                total_kilometers=0.0,
                total_photos=0,
                achievements_count=0,
                countries_visited=[],
            )
            self.db.add(stats)

        # Update stats
        stats.total_trips += 1
        stats.total_kilometers += distance_km
        stats.total_photos += photos_count

        # Add country if not already visited (unique)
        if country_code not in stats.countries_visited:
            countries = list(stats.countries_visited)  # Convert from JSON
            countries.append(country_code)
            stats.countries_visited = countries

        # Update last trip date if this is more recent
        if stats.last_trip_date is None or trip_date > stats.last_trip_date:
            stats.last_trip_date = trip_date

        stats.updated_at = datetime.now(UTC)

        await self.db.commit()

        # Check and award achievements
        await self.check_and_award_achievements(user_id)

        logger.info(f"Updated stats for user {user_id}: +{distance_km}km, +{photos_count} photos")

    async def update_stats_on_trip_edit(
        self,
        user_id: str,
        old_distance_km: float,
        new_distance_km: float,
        old_country_code: str,
        new_country_code: str,
        old_photos_count: int,
        new_photos_count: int,
    ) -> None:
        """
        T162: Update stats when a trip is edited.

        Recalculates statistics based on the changes.

        Args:
            user_id: User ID
            old_distance_km: Previous trip distance
            new_distance_km: New trip distance
            old_country_code: Previous country code
            new_country_code: New country code
            old_photos_count: Previous photos count
            new_photos_count: New photos count
        """
        result = await self.db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = result.scalar_one_or_none()

        if not stats:
            logger.warning(f"Stats not found for user {user_id} during trip edit")
            return

        # Update distance (remove old, add new)
        stats.total_kilometers = stats.total_kilometers - old_distance_km + new_distance_km

        # Update photos (remove old, add new)
        stats.total_photos = stats.total_photos - old_photos_count + new_photos_count

        # Update country if changed
        if old_country_code != new_country_code:
            # Note: We don't remove old country as user may have other trips there
            # Only add new country if not already present
            if new_country_code not in stats.countries_visited:
                countries = list(stats.countries_visited)
                countries.append(new_country_code)
                stats.countries_visited = countries

        stats.updated_at = datetime.now(UTC)

        await self.db.commit()

        logger.info(f"Updated stats for user {user_id} after trip edit")

    async def update_stats_on_trip_delete(
        self,
        user_id: str,
        distance_km: float,
        country_code: str,
        photos_count: int,
    ) -> None:
        """
        T163: Update stats when a trip is deleted.

        Decrements statistics. Ensures values don't go below zero.
        Also removes achievements that are no longer met.

        Args:
            user_id: User ID
            distance_km: Trip distance to subtract
            country_code: Country code (informational, we don't remove countries)
            photos_count: Photos count to subtract
        """
        result = await self.db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = result.scalar_one_or_none()

        if not stats:
            logger.warning(f"Stats not found for user {user_id} during trip delete")
            return

        # Decrement stats (ensure non-negative)
        stats.total_trips = max(0, stats.total_trips - 1)
        stats.total_kilometers = max(0.0, stats.total_kilometers - distance_km)
        stats.total_photos = max(0, stats.total_photos - photos_count)

        # Note: We don't remove countries as determining if they should be removed
        # would require querying all other trips

        stats.updated_at = datetime.now(UTC)

        await self.db.commit()

        # Remove achievements that are no longer met
        await self._remove_unmet_achievements(user_id, stats)

        logger.info(f"Updated stats for user {user_id} after trip delete")

    async def check_achievements(self, user_id: str) -> list[Achievement]:
        """
        T164: Check which achievements the user has newly earned.

        Compares current stats against achievement requirements and returns
        achievements that are earned but not yet awarded.

        Args:
            user_id: User ID

        Returns:
            List of newly earned achievements
        """
        # Get user stats
        result = await self.db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = result.scalar_one_or_none()

        if not stats:
            return []

        # Get all achievements
        result = await self.db.execute(select(Achievement))
        all_achievements = result.scalars().all()

        # Get already awarded achievements
        result = await self.db.execute(
            select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
        )
        awarded_ids = {row[0] for row in result.all()}

        # Check which achievements are earned but not awarded
        newly_earned = []

        for achievement in all_achievements:
            # Skip if already awarded
            if achievement.id in awarded_ids:
                continue

            # T175-T178: Check achievement criteria
            earned = self._check_achievement_criteria(
                achievement,
                stats.total_kilometers,
                stats.total_trips,
                len(stats.countries_visited),
                stats.total_photos,
                0,  # followers_count (not implemented yet)
            )

            if earned:
                newly_earned.append(achievement)

        return newly_earned

    def _check_achievement_criteria(
        self,
        achievement: Achievement,
        total_km: float,
        total_trips: int,
        countries_count: int,
        photos_count: int,
        followers_count: int,
    ) -> bool:
        """
        Check if achievement criteria is met.

        T175-T178: Achievement criteria validation.

        Args:
            achievement: Achievement to check
            total_km: User's total kilometers
            total_trips: User's total trips
            countries_count: User's countries count
            photos_count: User's total photos
            followers_count: User's followers count

        Returns:
            True if achievement criteria is met
        """
        req_type = achievement.requirement_type
        req_value = achievement.requirement_value

        if req_type == "distance":
            # T175: Distance milestones (100km, 1000km, 5000km)
            return total_km >= req_value
        elif req_type == "trips":
            # T176: Trip count milestones (1, 10, 25)
            return total_trips >= req_value
        elif req_type == "countries":
            # T177: Countries milestones (5, 10)
            return countries_count >= req_value
        elif req_type == "photos":
            # T178: Photos milestone (50)
            return photos_count >= req_value
        elif req_type == "followers":
            # Followers milestone (100) - not implemented yet
            return followers_count >= req_value
        else:
            logger.warning(f"Unknown achievement requirement type: {req_type}")
            return False

    async def award_achievement(self, user_id: str, achievement_id: str) -> None:
        """
        T165: Award an achievement to a user.

        Creates UserAchievement record and increments achievements_count.
        Idempotent - won't create duplicates.

        Args:
            user_id: User ID
            achievement_id: Achievement ID to award
        """
        # Check if already awarded (idempotency)
        result = await self.db.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user_id, UserAchievement.achievement_id == achievement_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.info(f"Achievement {achievement_id} already awarded to user {user_id}")
            return

        # Create user achievement
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
        )
        self.db.add(user_achievement)

        # Increment achievements count
        result = await self.db.execute(select(UserStats).where(UserStats.user_id == user_id))
        stats = result.scalar_one_or_none()

        if stats:
            stats.achievements_count += 1

        await self.db.commit()

        logger.info(f"Awarded achievement {achievement_id} to user {user_id}")

    async def check_and_award_achievements(self, user_id: str) -> list[Achievement]:
        """
        Check and automatically award newly earned achievements.

        Convenience method that checks achievements and awards them.

        Args:
            user_id: User ID

        Returns:
            List of newly awarded achievements
        """
        newly_earned = await self.check_achievements(user_id)

        for achievement in newly_earned:
            await self.award_achievement(user_id, achievement.id)

        if newly_earned:
            logger.info(f"Awarded {len(newly_earned)} new achievements to user {user_id}")

        return newly_earned

    async def _remove_unmet_achievements(self, user_id: str, stats: UserStats) -> None:
        """
        Remove achievements that are no longer met after stats decrease.

        Checks all user achievements and removes those that no longer meet the requirements.
        Updates the achievements_count accordingly.

        Args:
            user_id: User ID
            stats: User's current stats
        """
        # Get all user achievements with achievement details
        result = await self.db.execute(
            select(UserAchievement)
            .options(joinedload(UserAchievement.achievement))
            .where(UserAchievement.user_id == user_id)
        )
        user_achievements = result.scalars().all()

        if not user_achievements:
            return

        # Check which achievements are no longer met
        achievements_to_remove = []
        for user_achievement in user_achievements:
            achievement = user_achievement.achievement
            still_earned = self._check_achievement_criteria(
                achievement,
                stats.total_kilometers,
                stats.total_trips,
                len(stats.countries_visited) if stats.countries_visited else 0,
                stats.total_photos,
                0,  # followers_count (not implemented yet)
            )

            if not still_earned:
                achievements_to_remove.append(user_achievement)

        # Remove unmet achievements
        if achievements_to_remove:
            for user_achievement in achievements_to_remove:
                await self.db.delete(user_achievement)
                stats.achievements_count = max(0, stats.achievements_count - 1)
                logger.info(
                    f"Removed achievement {user_achievement.achievement.code} from user {user_id} (no longer met)"
                )

            await self.db.commit()
            logger.info(
                f"Removed {len(achievements_to_remove)} unmet achievements from user {user_id}"
            )
