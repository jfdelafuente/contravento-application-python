"""
Integration tests for statistics calculation and achievement awarding.

Tests the complete workflow of stats updates when trips are published, edited,
or deleted, and automatic achievement awarding when milestones are reached.

These tests simulate real-world scenarios:
- User publishes trip → stats update → achievements check
- User edits trip → stats recalculate
- User deletes trip → stats decrease
- Multiple trips trigger multiple achievements
"""

import pytest
from datetime import datetime, date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User, UserProfile
from src.models.stats import UserStats, Achievement, UserAchievement
from src.utils.security import hash_password


@pytest.mark.asyncio
class TestStatsCalculationOnTripPublish:
    """
    T140: Integration test for stats calculation on trip publish.

    Simulates publishing a trip and verifies stats are automatically updated.
    """

    async def test_complete_stats_update_on_trip_publish(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """
        Test complete workflow:
        1. Create user
        2. Simulate trip publish event (100km, Spain, 5 photos)
        3. Verify stats are updated correctly
        4. Check FIRST_TRIP achievement is awarded
        """
        # 1. Create test user
        user = User(
            username="stats_user",
            email="stats@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)

        # Create initial stats (zero state)
        stats = UserStats(user_id=user.id)
        db_session.add(stats)

        # Create FIRST_TRIP achievement definition
        first_trip_achievement = Achievement(
            code="FIRST_TRIP",
            name="Primer Viaje",
            description="Publicaste tu primer viaje",
            badge_icon="🚴",
            requirement_type="trips",
            requirement_value=1,
        )
        db_session.add(first_trip_achievement)
        await db_session.commit()
        await db_session.refresh(user)
        await db_session.refresh(stats)

        # 2. Simulate trip publish (this would come from trips service)
        # In real implementation, this would be triggered by an event
        from src.services.stats_service import StatsService
        stats_service = StatsService(db_session)

        trip_data = {
            "distance_km": 100.5,
            "country_code": "ES",
            "photos_count": 5,
            "trip_date": date(2025, 12, 15),
        }

        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            **trip_data
        )

        # 3. Verify stats were updated
        await db_session.refresh(stats)
        assert stats.total_trips == 1
        assert stats.total_kilometers == 100.5
        assert "ES" in stats.countries_visited
        assert stats.total_photos == 5
        assert stats.last_trip_date == date(2025, 12, 15)

        # 4. Verify FIRST_TRIP achievement was awarded
        result = await db_session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == first_trip_achievement.id
            )
        )
        user_achievement = result.scalar_one_or_none()
        assert user_achievement is not None
        assert user_achievement.awarded_at is not None

        # Verify achievements_count was incremented
        assert stats.achievements_count == 1

    async def test_stats_accumulate_on_multiple_trips(
        self,
        db_session: AsyncSession,
    ):
        """
        Test stats accumulate correctly across multiple trips:
        - Kilometers add up
        - Countries list grows (unique)
        - Photos count increases
        - Trip count increments
        """
        # Create user with stats
        user = User(
            username="frequent_traveler",
            email="traveler@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        stats = UserStats(user_id=user.id)
        db_session.add(stats)
        await db_session.commit()

        from src.services.stats_service import StatsService
        stats_service = StatsService(db_session)

        # Publish trip 1: Spain, 50km, 3 photos
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=50.0,
            country_code="ES",
            photos_count=3,
            trip_date=date(2025, 11, 1),
        )

        # Publish trip 2: France, 75km, 5 photos
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=75.0,
            country_code="FR",
            photos_count=5,
            trip_date=date(2025, 11, 15),
        )

        # Publish trip 3: Spain again, 25km, 2 photos
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=25.0,
            country_code="ES",  # Duplicate country
            photos_count=2,
            trip_date=date(2025, 12, 1),
        )

        # Verify accumulated stats
        await db_session.refresh(stats)
        assert stats.total_trips == 3
        assert stats.total_kilometers == 150.0  # 50 + 75 + 25
        assert set(stats.countries_visited) == {"ES", "FR"}  # Unique countries
        assert stats.total_photos == 10  # 3 + 5 + 2
        assert stats.last_trip_date == date(2025, 12, 1)  # Most recent


@pytest.mark.asyncio
class TestStatsUpdateOnTripEdit:
    """
    T141: Integration test for stats update on trip edit.

    Verifies stats are recalculated when a trip is edited.
    """

    async def test_stats_update_when_trip_distance_changes(
        self,
        db_session: AsyncSession,
    ):
        """
        Test stats update when trip distance is edited:
        1. Publish trip with 100km
        2. Edit trip to 150km
        3. Verify stats reflect new distance
        """
        # Setup user with initial trip
        user = User(
            username="editor",
            email="editor@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        stats = UserStats(user_id=user.id)
        db_session.add(stats)
        await db_session.commit()

        from src.services.stats_service import StatsService
        stats_service = StatsService(db_session)

        # Initial trip
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=100.0,
            country_code="ES",
            photos_count=3,
            trip_date=date(2025, 12, 1),
        )

        await db_session.refresh(stats)
        assert stats.total_kilometers == 100.0

        # Edit trip (distance increased)
        await stats_service.update_stats_on_trip_edit(
            user_id=user.id,
            old_distance_km=100.0,
            new_distance_km=150.0,
            old_country_code="ES",
            new_country_code="ES",
            old_photos_count=3,
            new_photos_count=5,
        )

        # Verify updated stats
        await db_session.refresh(stats)
        assert stats.total_kilometers == 150.0  # Updated
        assert stats.total_photos == 5  # Updated
        assert stats.total_trips == 1  # Still 1 trip


@pytest.mark.asyncio
class TestStatsUpdateOnTripDelete:
    """
    T142: Integration test for stats update on trip delete.

    Verifies stats decrease when a trip is deleted.
    """

    async def test_stats_decrease_on_trip_delete(
        self,
        db_session: AsyncSession,
    ):
        """
        Test stats decrease when trip is deleted:
        1. Publish 2 trips
        2. Delete 1 trip
        3. Verify stats reflect the deletion
        """
        # Setup user with 2 trips
        user = User(
            username="deleter",
            email="deleter@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        stats = UserStats(user_id=user.id)
        db_session.add(stats)
        await db_session.commit()

        from src.services.stats_service import StatsService
        stats_service = StatsService(db_session)

        # Publish 2 trips
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=100.0,
            country_code="ES",
            photos_count=5,
            trip_date=date(2025, 11, 1),
        )

        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=75.0,
            country_code="FR",
            photos_count=3,
            trip_date=date(2025, 12, 1),
        )

        await db_session.refresh(stats)
        assert stats.total_trips == 2
        assert stats.total_kilometers == 175.0
        assert stats.total_photos == 8

        # Delete first trip
        await stats_service.update_stats_on_trip_delete(
            user_id=user.id,
            distance_km=100.0,
            country_code="ES",
            photos_count=5,
        )

        # Verify stats decreased
        await db_session.refresh(stats)
        assert stats.total_trips == 1
        assert stats.total_kilometers == 75.0
        assert stats.total_photos == 3


@pytest.mark.asyncio
class TestAchievementAwardOnMilestone:
    """
    T143: Integration test for achievement award on milestone.

    Verifies achievements are automatically awarded when user reaches milestones.
    """

    async def test_century_achievement_awarded_at_100km(
        self,
        db_session: AsyncSession,
    ):
        """
        Test CENTURY achievement (100km) is awarded when milestone is reached.
        """
        # Setup user and achievement
        user = User(
            username="century_rider",
            email="century@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        stats = UserStats(user_id=user.id)
        db_session.add(stats)

        century = Achievement(
            code="CENTURY",
            name="Centurión",
            description="Recorriste 100 km en total",
            badge_icon="💯",
            requirement_type="distance",
            requirement_value=100,
        )
        db_session.add(century)
        await db_session.commit()

        from src.services.stats_service import StatsService
        stats_service = StatsService(db_session)

        # Publish trip that reaches 100km
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=100.5,
            country_code="ES",
            photos_count=5,
            trip_date=date(2025, 12, 15),
        )

        # Verify CENTURY was awarded
        result = await db_session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == century.id
            )
        )
        user_achievement = result.scalar_one_or_none()
        assert user_achievement is not None

        # Verify achievements_count increased
        await db_session.refresh(stats)
        assert stats.achievements_count == 1


@pytest.mark.asyncio
class TestMultipleAchievementsInSingleEvent:
    """
    T144: Integration test for multiple achievements in single event.

    Verifies multiple achievements can be awarded in a single trip publish event.
    """

    async def test_multiple_achievements_awarded_simultaneously(
        self,
        db_session: AsyncSession,
    ):
        """
        Test that publishing a 100km trip triggers both FIRST_TRIP and CENTURY.
        """
        # Setup user
        user = User(
            username="overachiever",
            email="overachiever@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        stats = UserStats(user_id=user.id)
        db_session.add(stats)

        # Create both achievements
        first_trip = Achievement(
            code="FIRST_TRIP",
            name="Primer Viaje",
            description="Publicaste tu primer viaje",
            badge_icon="🚴",
            requirement_type="trips",
            requirement_value=1,
        )
        db_session.add(first_trip)

        century = Achievement(
            code="CENTURY",
            name="Centurión",
            description="Recorriste 100 km en total",
            badge_icon="💯",
            requirement_type="distance",
            requirement_value=100,
        )
        db_session.add(century)
        await db_session.commit()

        from src.services.stats_service import StatsService
        stats_service = StatsService(db_session)

        # Publish a 100km trip (first trip)
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=100.5,
            country_code="ES",
            photos_count=5,
            trip_date=date(2025, 12, 15),
        )

        # Verify BOTH achievements were awarded
        result = await db_session.execute(
            select(UserAchievement).where(UserAchievement.user_id == user.id)
        )
        user_achievements = result.scalars().all()
        assert len(user_achievements) == 2

        # Verify achievements_count is 2
        await db_session.refresh(stats)
        assert stats.achievements_count == 2

        # Verify both specific achievements are present
        achievement_ids = {ua.achievement_id for ua in user_achievements}
        assert first_trip.id in achievement_ids
        assert century.id in achievement_ids
