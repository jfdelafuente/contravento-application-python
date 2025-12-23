"""
Contract tests for Statistics and Achievements API endpoints.

Validates that API responses match the OpenAPI specification in
specs/001-user-profiles/contracts/stats.yaml.

Tests verify:
- Response structure matches schema
- Required fields are present
- Data types are correct
- Success/error response format
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models.user import User, UserProfile
from src.models.stats import UserStats, Achievement, UserAchievement
from src.utils.security import hash_password


@pytest.mark.asyncio
class TestGetUserStatsContract:
    """
    T137: Contract test for GET /users/{username}/stats.

    Validates response structure against OpenAPI schema.
    """

    async def test_get_stats_success_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/stats returns correct schema on success."""
        # Create test user with stats
        user = User(
            username="test_cyclist",
            email="cyclist@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)

        stats = UserStats(
            user_id=user.id,
            total_trips=5,
            total_kilometers=523.45,
            countries_visited=["ES", "FR"],
            total_photos=12,
            achievements_count=2,
        )
        db_session.add(stats)
        await db_session.commit()

        # Make request
        response = await async_client.get(f"/users/{user.username}/stats")

        # Verify status code
        assert response.status_code == 200

        # Verify standardized response format
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert data["success"] is True
        assert data["error"] is None

        # Verify stats data structure
        stats_data = data["data"]
        assert "total_trips" in stats_data
        assert "total_kilometers" in stats_data
        assert "countries_visited" in stats_data
        assert "total_photos" in stats_data
        assert "achievements_count" in stats_data
        assert "last_trip_date" in stats_data
        assert "updated_at" in stats_data

        # Verify data types
        assert isinstance(stats_data["total_trips"], int)
        assert isinstance(stats_data["total_kilometers"], (int, float))
        assert isinstance(stats_data["countries_visited"], list)
        assert isinstance(stats_data["total_photos"], int)
        assert isinstance(stats_data["achievements_count"], int)

        # Verify countries structure
        for country in stats_data["countries_visited"]:
            assert "code" in country
            assert "name" in country
            assert isinstance(country["code"], str)
            assert isinstance(country["name"], str)

    async def test_get_stats_user_not_found_schema(
        self,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/stats returns correct error schema for non-existent user."""
        response = await async_client.get("/users/nonexistent_user/stats")

        # Verify status code
        assert response.status_code == 404

        # Verify error response format
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "error" in data
        assert data["success"] is False
        assert data["data"] is None

        # Verify error structure
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "USER_NOT_FOUND"
        assert isinstance(error["message"], str)

    async def test_get_stats_zero_state_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/stats for user with no trips (zero state)."""
        # Create user with no stats (new user)
        user = User(
            username="new_cyclist",
            email="new@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)
        await db_session.commit()

        response = await async_client.get(f"/users/{user.username}/stats")

        # Should still return 200 with zero values
        assert response.status_code == 200

        data = response.json()
        stats_data = data["data"]

        # Verify zero state
        assert stats_data["total_trips"] == 0
        assert stats_data["total_kilometers"] == 0.0
        assert stats_data["countries_visited"] == []
        assert stats_data["total_photos"] == 0
        assert stats_data["achievements_count"] == 0
        assert stats_data["last_trip_date"] is None


@pytest.mark.asyncio
class TestGetUserAchievementsContract:
    """
    T138: Contract test for GET /users/{username}/achievements.

    Validates response structure against OpenAPI schema.
    """

    async def test_get_achievements_success_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/achievements returns correct schema."""
        # Create test user
        user = User(
            username="achiever",
            email="achiever@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)

        # Create achievement definition
        achievement = Achievement(
            code="FIRST_TRIP",
            name="Primer Viaje",
            description="Publicaste tu primer viaje",
            badge_icon="🚴",
            requirement_type="trips",
            requirement_value=1,
        )
        db_session.add(achievement)
        await db_session.flush()

        # Award achievement to user
        user_achievement = UserAchievement(
            user_id=user.id,
            achievement_id=achievement.id,
        )
        db_session.add(user_achievement)
        await db_session.commit()

        # Make request
        response = await async_client.get(f"/users/{user.username}/achievements")

        # Verify status code
        assert response.status_code == 200

        # Verify standardized response format
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None

        # Verify achievements data structure
        achievements_data = data["data"]
        assert "achievements" in achievements_data
        assert "total_count" in achievements_data
        assert isinstance(achievements_data["achievements"], list)
        assert isinstance(achievements_data["total_count"], int)
        assert achievements_data["total_count"] >= 0

        # Verify individual achievement structure
        if achievements_data["achievements"]:
            achievement_item = achievements_data["achievements"][0]
            assert "code" in achievement_item
            assert "name" in achievement_item
            assert "description" in achievement_item
            assert "badge_icon" in achievement_item
            assert "requirement_type" in achievement_item
            assert "requirement_value" in achievement_item
            assert "awarded_at" in achievement_item

            # Verify data types
            assert isinstance(achievement_item["code"], str)
            assert isinstance(achievement_item["name"], str)
            assert isinstance(achievement_item["description"], str)
            assert isinstance(achievement_item["badge_icon"], str)
            assert isinstance(achievement_item["requirement_type"], str)
            assert isinstance(achievement_item["requirement_value"], (int, float))
            assert isinstance(achievement_item["awarded_at"], str)

            # Verify requirement_type is valid enum
            assert achievement_item["requirement_type"] in [
                "distance", "trips", "countries", "photos", "followers"
            ]

    async def test_get_achievements_empty_list_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/achievements for user with no achievements."""
        # Create user with no achievements
        user = User(
            username="newbie",
            email="newbie@test.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)

        profile = UserProfile(user_id=user.id)
        db_session.add(profile)
        await db_session.commit()

        response = await async_client.get(f"/users/{user.username}/achievements")

        # Should still return 200 with empty list
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["achievements"] == []
        assert data["data"]["total_count"] == 0

    async def test_get_achievements_user_not_found_schema(
        self,
        async_client: AsyncClient,
    ):
        """Test GET /users/{username}/achievements for non-existent user."""
        response = await async_client.get("/users/ghost_rider/achievements")

        assert response.status_code == 404

        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "USER_NOT_FOUND"


@pytest.mark.asyncio
class TestListAchievementsContract:
    """
    T139: Contract test for GET /achievements.

    Validates response structure against OpenAPI schema.
    """

    async def test_list_achievements_success_schema(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /achievements returns all available achievements."""
        # Seed some achievements
        achievements = [
            Achievement(
                code="FIRST_TRIP",
                name="Primer Viaje",
                description="Publicaste tu primer viaje",
                badge_icon="🚴",
                requirement_type="trips",
                requirement_value=1,
            ),
            Achievement(
                code="CENTURY",
                name="Centurión",
                description="Recorriste 100 km en total",
                badge_icon="💯",
                requirement_type="distance",
                requirement_value=100,
            ),
            Achievement(
                code="VOYAGER",
                name="Viajero",
                description="Acumulaste 1000 km",
                badge_icon="🌍",
                requirement_type="distance",
                requirement_value=1000,
            ),
        ]
        for ach in achievements:
            db_session.add(ach)
        await db_session.commit()

        # Make request (no authentication required)
        response = await async_client.get("/achievements")

        # Verify status code
        assert response.status_code == 200

        # Verify standardized response format
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None

        # Verify achievements list structure
        achievements_data = data["data"]
        assert "achievements" in achievements_data
        assert "total_count" in achievements_data
        assert isinstance(achievements_data["achievements"], list)
        assert isinstance(achievements_data["total_count"], int)
        assert achievements_data["total_count"] >= 3  # At least the 3 we seeded

        # Verify achievement definition structure (no awarded_at)
        achievement_def = achievements_data["achievements"][0]
        assert "code" in achievement_def
        assert "name" in achievement_def
        assert "description" in achievement_def
        assert "badge_icon" in achievement_def
        assert "requirement_type" in achievement_def
        assert "requirement_value" in achievement_def
        assert "awarded_at" not in achievement_def  # Definitions don't have awarded_at

        # Verify data types
        assert isinstance(achievement_def["code"], str)
        assert isinstance(achievement_def["name"], str)
        assert isinstance(achievement_def["description"], str)
        assert isinstance(achievement_def["badge_icon"], str)
        assert isinstance(achievement_def["requirement_type"], str)
        assert isinstance(achievement_def["requirement_value"], (int, float))

        # Verify requirement_type is valid enum
        assert achievement_def["requirement_type"] in [
            "distance", "trips", "countries", "photos", "followers"
        ]

    async def test_list_achievements_all_9_achievements(
        self,
        db_session: AsyncSession,
        async_client: AsyncClient,
    ):
        """Test GET /achievements returns all 9 predefined achievements."""
        # Seed all 9 achievements per spec
        all_achievements = [
            ("FIRST_TRIP", "Primer Viaje", "Publicaste tu primer viaje", "🚴", "trips", 1),
            ("CENTURY", "Centurión", "Recorriste 100 km en total", "💯", "distance", 100),
            ("VOYAGER", "Viajero", "Acumulaste 1000 km", "🌍", "distance", 1000),
            ("EXPLORER", "Explorador", "Visitaste 5 países", "🗺️", "countries", 5),
            ("PHOTOGRAPHER", "Fotógrafo", "Subiste 50 fotos", "📷", "photos", 50),
            ("GLOBETROTTER", "Trotamundos", "Visitaste 10 países", "✈️", "countries", 10),
            ("MARATHONER", "Maratonista", "Recorriste 5000 km", "🏃", "distance", 5000),
            ("INFLUENCER", "Influencer", "Tienes 100 seguidores", "⭐", "followers", 100),
            ("PROLIFIC", "Prolífico", "Publicaste 25 viajes", "📝", "trips", 25),
        ]

        for code, name, desc, icon, req_type, req_val in all_achievements:
            achievement = Achievement(
                code=code,
                name=name,
                description=desc,
                badge_icon=icon,
                requirement_type=req_type,
                requirement_value=req_val,
            )
            db_session.add(achievement)
        await db_session.commit()

        response = await async_client.get("/achievements")

        assert response.status_code == 200
        data = response.json()

        # Verify all 9 achievements are returned
        assert data["data"]["total_count"] == 9
        assert len(data["data"]["achievements"]) == 9

        # Verify specific achievement codes are present
        codes = [ach["code"] for ach in data["data"]["achievements"]]
        expected_codes = [
            "FIRST_TRIP", "CENTURY", "VOYAGER", "EXPLORER", "PHOTOGRAPHER",
            "GLOBETROTTER", "MARATHONER", "INFLUENCER", "PROLIFIC"
        ]
        for expected_code in expected_codes:
            assert expected_code in codes
