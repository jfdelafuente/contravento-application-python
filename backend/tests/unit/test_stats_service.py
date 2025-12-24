"""
Unit tests for StatsService.

Tests individual methods of StatsService in isolation, using mocks where necessary.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.stats_service import StatsService
from src.models.user import User
from src.models.stats import UserStats, Achievement, UserAchievement


@pytest.mark.asyncio
class TestStatsServiceGetUserStats:
    """
    T145: Unit tests for StatsService.get_user_stats().

    Tests retrieving user statistics with proper formatting.
    """

    async def test_get_user_stats_returns_formatted_stats(
        self,
        db_session: AsyncSession,
    ):
        """Test get_user_stats() returns properly formatted statistics."""
        # Create test user with stats
        user = User(
            id="test-user-id",
            username="test_user",
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            total_trips=5,
            total_kilometers=523.45,
            countries_visited=["ES", "FR", "IT"],
            total_photos=12,
            achievements_count=2,
            last_trip_date=date(2025, 12, 15),
        )
        db_session.add(stats)
        await db_session.commit()

        # Test
        stats_service = StatsService(db_session)
        result = await stats_service.get_user_stats("test_user")

        # Verify
        assert result.total_trips == 5
        assert result.total_kilometers == 523.45
        assert len(result.countries_visited) == 3
        assert result.total_photos == 12
        assert result.achievements_count == 2
        assert result.last_trip_date == date(2025, 12, 15)

    async def test_get_user_stats_converts_country_codes_to_names(
        self,
        db_session: AsyncSession,
    ):
        """Test that country codes are converted to full names."""
        user = User(
            id="test-user-id",
            username="traveler",
            email="traveler@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            countries_visited=["ES", "FR"],
        )
        db_session.add(stats)
        await db_session.commit()

        stats_service = StatsService(db_session)
        result = await stats_service.get_user_stats("traveler")

        # Verify countries have both code and name
        assert len(result.countries_visited) == 2

        # Check structure
        for country in result.countries_visited:
            assert "code" in country
            assert "name" in country
            assert country["code"] in ["ES", "FR"]
            # Name should be in Spanish
            if country["code"] == "ES":
                assert country["name"] == "España"
            elif country["code"] == "FR":
                assert country["name"] == "Francia"

    async def test_get_user_stats_raises_error_for_nonexistent_user(
        self,
        db_session: AsyncSession,
    ):
        """Test get_user_stats() raises ValueError for non-existent user."""
        stats_service = StatsService(db_session)

        with pytest.raises(ValueError, match="no existe"):
            await stats_service.get_user_stats("ghost_user")


@pytest.mark.asyncio
class TestStatsServiceUpdateStatsOnTripPublish:
    """
    T146: Unit tests for StatsService.update_stats_on_trip_publish().

    Tests stats updates when a new trip is published.
    """

    async def test_update_stats_on_trip_publish_increments_values(
        self,
        db_session: AsyncSession,
    ):
        """Test that publishing a trip increments all stat values correctly."""
        user = User(
            id="test-user-id",
            username="publisher",
            email="publisher@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            total_trips=2,
            total_kilometers=150.0,
            countries_visited=["ES"],
            total_photos=10,
        )
        db_session.add(stats)
        await db_session.commit()

        # Publish new trip
        stats_service = StatsService(db_session)
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=75.5,
            country_code="FR",
            photos_count=5,
            trip_date=date(2025, 12, 20),
        )

        # Verify stats updated
        await db_session.refresh(stats)
        assert stats.total_trips == 3  # Incremented
        assert stats.total_kilometers == 225.5  # 150 + 75.5
        assert set(stats.countries_visited) == {"ES", "FR"}  # New country added
        assert stats.total_photos == 15  # 10 + 5
        assert stats.last_trip_date == date(2025, 12, 20)

    async def test_update_stats_creates_stats_if_not_exists(
        self,
        db_session: AsyncSession,
    ):
        """Test that stats record is created if it doesn't exist."""
        user = User(
            id="new-user-id",
            username="newuser",
            email="newuser@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()

        # No stats record exists yet
        stats_service = StatsService(db_session)
        await stats_service.update_stats_on_trip_publish(
            user_id=user.id,
            distance_km=50.0,
            country_code="ES",
            photos_count=3,
            trip_date=date(2025, 12, 1),
        )

        # Verify stats were created
        from sqlalchemy import select
        result = await db_session.execute(
            select(UserStats).where(UserStats.user_id == user.id)
        )
        stats = result.scalar_one()

        assert stats is not None
        assert stats.total_trips == 1
        assert stats.total_kilometers == 50.0


@pytest.mark.asyncio
class TestStatsServiceUpdateStatsOnTripDelete:
    """
    T147: Unit tests for StatsService.update_stats_on_trip_delete().

    Tests stats updates when a trip is deleted.
    """

    async def test_update_stats_on_trip_delete_decrements_values(
        self,
        db_session: AsyncSession,
    ):
        """Test that deleting a trip decrements stat values correctly."""
        user = User(
            id="test-user-id",
            username="deleter",
            email="deleter@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            total_trips=3,
            total_kilometers=225.5,
            countries_visited=["ES", "FR"],
            total_photos=15,
        )
        db_session.add(stats)
        await db_session.commit()

        # Delete a trip
        stats_service = StatsService(db_session)
        await stats_service.update_stats_on_trip_delete(
            user_id=user.id,
            distance_km=75.5,
            country_code="FR",
            photos_count=5,
        )

        # Verify stats decreased
        await db_session.refresh(stats)
        assert stats.total_trips == 2  # Decremented
        assert stats.total_kilometers == 150.0  # 225.5 - 75.5
        assert stats.total_photos == 10  # 15 - 5

    async def test_delete_does_not_go_below_zero(
        self,
        db_session: AsyncSession,
    ):
        """Test that stats never go below zero when deleting."""
        user = User(
            id="test-user-id",
            username="edge_case",
            email="edge@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            total_trips=1,
            total_kilometers=50.0,
            total_photos=2,
        )
        db_session.add(stats)
        await db_session.commit()

        # Try to delete more than exists
        stats_service = StatsService(db_session)
        await stats_service.update_stats_on_trip_delete(
            user_id=user.id,
            distance_km=100.0,  # More than current
            country_code="ES",
            photos_count=5,  # More than current
        )

        # Verify stats don't go negative
        await db_session.refresh(stats)
        assert stats.total_trips >= 0
        assert stats.total_kilometers >= 0.0
        assert stats.total_photos >= 0


@pytest.mark.asyncio
class TestStatsServiceCheckAchievements:
    """
    T148: Unit tests for StatsService.check_achievements().

    Tests achievement checking logic.
    """

    async def test_check_achievements_identifies_newly_earned(
        self,
        db_session: AsyncSession,
    ):
        """Test that check_achievements identifies newly earned achievements."""
        user = User(
            id="test-user-id",
            username="achiever",
            email="achiever@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            total_trips=1,
            total_kilometers=100.5,
        )
        db_session.add(stats)

        # Create achievement definitions
        century = Achievement(
            code="CENTURY",
            name="Centurión",
            description="Recorriste 100 km",
            badge_icon="💯",
            requirement_type="distance",
            requirement_value=100,
        )
        db_session.add(century)
        await db_session.commit()

        # Check achievements
        stats_service = StatsService(db_session)
        newly_earned = await stats_service.check_achievements(user.id)

        # Verify CENTURY was identified
        assert len(newly_earned) == 1
        assert newly_earned[0].code == "CENTURY"

    async def test_check_achievements_ignores_already_earned(
        self,
        db_session: AsyncSession,
    ):
        """Test that already-earned achievements are not returned."""
        user = User(
            id="test-user-id",
            username="veteran",
            email="veteran@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            total_kilometers=100.5,
        )
        db_session.add(stats)

        century = Achievement(
            code="CENTURY",
            name="Centurión",
            description="Recorriste 100 km",
            badge_icon="💯",
            requirement_type="distance",
            requirement_value=100,
        )
        db_session.add(century)
        await db_session.flush()

        # Already earned
        user_achievement = UserAchievement(
            user_id=user.id,
            achievement_id=century.id,
        )
        db_session.add(user_achievement)
        await db_session.commit()

        # Check achievements
        stats_service = StatsService(db_session)
        newly_earned = await stats_service.check_achievements(user.id)

        # Should be empty (already earned)
        assert len(newly_earned) == 0


@pytest.mark.asyncio
class TestStatsServiceAwardAchievement:
    """
    T149: Unit tests for StatsService.award_achievement().

    Tests awarding achievements to users.
    """

    async def test_award_achievement_creates_user_achievement(
        self,
        db_session: AsyncSession,
    ):
        """Test that awarding creates a UserAchievement record."""
        user = User(
            id="test-user-id",
            username="winner",
            email="winner@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(user_id=user.id, achievements_count=0)
        db_session.add(stats)

        achievement = Achievement(
            code="TEST_ACH",
            name="Test",
            description="Test achievement",
            badge_icon="🏆",
            requirement_type="distance",
            requirement_value=100,
        )
        db_session.add(achievement)
        await db_session.commit()

        # Award achievement
        stats_service = StatsService(db_session)
        await stats_service.award_achievement(user.id, achievement.id)

        # Verify UserAchievement was created
        from sqlalchemy import select
        result = await db_session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user.id,
                UserAchievement.achievement_id == achievement.id
            )
        )
        user_achievement = result.scalar_one()

        assert user_achievement is not None
        assert user_achievement.awarded_at is not None

        # Verify achievements_count incremented
        await db_session.refresh(stats)
        assert stats.achievements_count == 1

    async def test_award_achievement_is_idempotent(
        self,
        db_session: AsyncSession,
    ):
        """Test that awarding the same achievement twice doesn't create duplicates."""
        user = User(
            id="test-user-id",
            username="idempotent",
            email="idempotent@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(user_id=user.id)
        db_session.add(stats)

        achievement = Achievement(
            code="IDEMPOTENT",
            name="Idempotent",
            description="Test",
            badge_icon="🔁",
            requirement_type="distance",
            requirement_value=100,
        )
        db_session.add(achievement)
        await db_session.commit()

        stats_service = StatsService(db_session)

        # Award once
        await stats_service.award_achievement(user.id, achievement.id)

        # Award again (should not error)
        await stats_service.award_achievement(user.id, achievement.id)

        # Verify only one record exists
        from sqlalchemy import select
        result = await db_session.execute(
            select(UserAchievement).where(
                UserAchievement.user_id == user.id
            )
        )
        user_achievements = result.scalars().all()

        assert len(user_achievements) == 1


@pytest.mark.asyncio
class TestAchievementCriteriaValidation:
    """
    T150: Unit tests for achievement criteria validation.

    Tests that different achievement types are validated correctly.
    """

    async def test_distance_milestone_validation(
        self,
        db_session: AsyncSession,
    ):
        """Test distance-based achievement validation."""
        user = User(
            id="test-user-id",
            username="distance_user",
            email="distance@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        # Stats with 99.9km (just under 100)
        stats = UserStats(
            user_id=user.id,
            total_kilometers=99.9,
        )
        db_session.add(stats)

        century = Achievement(
            code="CENTURY",
            name="Centurión",
            description="100 km",
            badge_icon="💯",
            requirement_type="distance",
            requirement_value=100,
        )
        db_session.add(century)
        await db_session.commit()

        stats_service = StatsService(db_session)

        # Should not award yet (99.9 < 100)
        newly_earned = await stats_service.check_achievements(user.id)
        assert len(newly_earned) == 0

        # Update to 100.1km
        stats.total_kilometers = 100.1
        await db_session.commit()

        # Should award now (100.1 >= 100)
        newly_earned = await stats_service.check_achievements(user.id)
        assert len(newly_earned) == 1
        assert newly_earned[0].code == "CENTURY"

    async def test_trips_milestone_validation(
        self,
        db_session: AsyncSession,
    ):
        """Test trips-based achievement validation."""
        user = User(
            id="test-user-id",
            username="trips_user",
            email="trips@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            total_trips=10,
        )
        db_session.add(stats)

        prolific = Achievement(
            code="PROLIFIC",
            name="Prolífico",
            description="25 viajes",
            badge_icon="📝",
            requirement_type="trips",
            requirement_value=25,
        )
        db_session.add(prolific)
        await db_session.commit()

        stats_service = StatsService(db_session)

        # Should not award yet (10 < 25)
        newly_earned = await stats_service.check_achievements(user.id)
        assert len(newly_earned) == 0

    async def test_countries_milestone_validation(
        self,
        db_session: AsyncSession,
    ):
        """Test countries-based achievement validation."""
        user = User(
            id="test-user-id",
            username="explorer_user",
            email="explorer@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        db_session.add(user)

        stats = UserStats(
            user_id=user.id,
            countries_visited=["ES", "FR", "IT", "PT", "DE"],  # 5 countries
        )
        db_session.add(stats)

        explorer = Achievement(
            code="EXPLORER",
            name="Explorador",
            description="5 países",
            badge_icon="🗺️",
            requirement_type="countries",
            requirement_value=5,
        )
        db_session.add(explorer)
        await db_session.commit()

        stats_service = StatsService(db_session)

        # Should award (5 >= 5)
        newly_earned = await stats_service.check_achievements(user.id)
        assert len(newly_earned) == 1
        assert newly_earned[0].code == "EXPLORER"
