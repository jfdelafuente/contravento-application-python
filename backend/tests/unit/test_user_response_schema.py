"""
Unit tests for UserResponse schema (Feature 013).

Tests that UserResponse includes privacy and profile fields when serializing User models.
"""

from datetime import datetime

from src.schemas.user import UserResponse


class TestUserResponseSchema:
    """Test UserResponse schema serialization."""

    async def test_user_response_includes_privacy_fields(self, db_session, test_user):
        """Test that UserResponse includes profile_visibility and trip_visibility."""
        # Arrange
        test_user.profile_visibility = "private"
        test_user.trip_visibility = "followers"
        await db_session.commit()
        await db_session.refresh(test_user)

        # Act
        response = UserResponse.from_user_model(test_user)

        # Assert
        assert response.profile_visibility == "private"
        assert response.trip_visibility == "followers"

    async def test_user_response_includes_profile_fields_when_profile_exists(
        self, db_session, test_user
    ):
        """Test that UserResponse includes profile fields when user has a profile."""
        # Arrange - Create a mock profile object (not saved to DB)
        from unittest.mock import MagicMock

        profile = MagicMock()
        profile.bio = "Test bio content"
        profile.location = "Madrid, España"
        profile.cycling_type = "mountain"
        profile.profile_photo_url = "https://example.com/photo.jpg"

        # Manually set the profile on the user object (simulating eager load)
        test_user.__dict__["profile"] = profile

        # Act
        response = UserResponse.from_user_model(test_user)

        # Assert
        assert response.bio == "Test bio content"
        assert response.location == "Madrid, España"
        assert response.cycling_type == "mountain"
        assert response.photo_url == "https://example.com/photo.jpg"

    async def test_user_response_profile_fields_are_none_when_no_profile(
        self, db_session, test_user
    ):
        """Test that UserResponse profile fields are None when user has no profile."""
        # Arrange - Ensure test_user has no profile
        # test_user fixture already has no profile

        # Act
        response = UserResponse.from_user_model(test_user)

        # Assert
        assert response.bio is None
        assert response.location is None
        assert response.cycling_type is None
        assert response.photo_url is None

    async def test_user_response_includes_all_required_fields(self, db_session, test_user):
        """Test that UserResponse includes all required fields."""
        # Act
        response = UserResponse.from_user_model(test_user)

        # Assert - Required fields
        assert response.user_id == test_user.id
        assert response.username == test_user.username
        assert response.email == test_user.email
        assert response.is_verified == test_user.is_verified
        assert response.profile_visibility == test_user.profile_visibility
        assert response.trip_visibility == test_user.trip_visibility
        assert isinstance(response.created_at, datetime)

    async def test_user_response_serializes_to_dict(self, db_session, test_user):
        """Test that UserResponse can be serialized to dict."""
        # Arrange - Mock profile
        from unittest.mock import MagicMock

        profile = MagicMock()
        profile.bio = "Test bio"
        profile.location = "Barcelona"
        profile.cycling_type = "road"
        profile.profile_photo_url = "https://example.com/pic.jpg"

        # Manually set the profile on the user object
        test_user.__dict__["profile"] = profile

        # Act
        response = UserResponse.from_user_model(test_user)
        data = response.model_dump()

        # Assert
        assert data["user_id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["profile_visibility"] == "public"  # Default
        assert data["trip_visibility"] == "public"  # Default
        assert data["bio"] == "Test bio"
        assert data["location"] == "Barcelona"
        assert data["cycling_type"] == "road"
        assert data["photo_url"] == "https://example.com/pic.jpg"

    async def test_user_response_json_serialization(self, db_session, test_user):
        """Test that UserResponse can be serialized to JSON."""
        # Arrange
        test_user.profile_visibility = "private"
        test_user.trip_visibility = "followers"
        await db_session.commit()
        await db_session.refresh(test_user)

        # Act
        response = UserResponse.from_user_model(test_user)
        json_str = response.model_dump_json()

        # Assert
        assert '"profile_visibility":"private"' in json_str.replace(" ", "")
        assert '"trip_visibility":"followers"' in json_str.replace(" ", "")
        assert f'"user_id":"{test_user.id}"' in json_str.replace(" ", "")
