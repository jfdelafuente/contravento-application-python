"""
Unit tests for trip_visibility feature in ProfileService.

Feature 013 - Public Trips Feed: Tests for trip visibility configuration.
"""

import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.profile import ProfileUpdateRequest
from src.services.profile_service import ProfileService


@pytest.mark.unit
@pytest.mark.asyncio
class TestProfileServiceTripVisibility:
    """Feature 013: Unit tests for trip_visibility updates via ProfileService.update_profile()."""

    async def test_update_trip_visibility_to_private(self, db_session: AsyncSession, test_user):
        """Test updating trip_visibility from public to private."""
        profile_service = ProfileService(db_session)
        assert test_user.trip_visibility == 'public'  # Default

        # Act
        update_data = ProfileUpdateRequest(trip_visibility='private')
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert
        assert result.trip_visibility == 'private'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.trip_visibility == 'private'

    async def test_update_trip_visibility_to_followers(self, db_session: AsyncSession, test_user):
        """Test updating trip_visibility from public to followers."""
        profile_service = ProfileService(db_session)
        assert test_user.trip_visibility == 'public'  # Default

        # Act
        update_data = ProfileUpdateRequest(trip_visibility='followers')
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert
        assert result.trip_visibility == 'followers'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.trip_visibility == 'followers'

    async def test_update_trip_visibility_to_public(self, db_session: AsyncSession, test_user):
        """Test updating trip_visibility from private back to public."""
        profile_service = ProfileService(db_session)

        # Arrange - first set to private
        test_user.trip_visibility = 'private'
        await db_session.commit()
        assert test_user.trip_visibility == 'private'

        # Act - update to public
        update_data = ProfileUpdateRequest(trip_visibility='public')
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert
        assert result.trip_visibility == 'public'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.trip_visibility == 'public'

    async def test_update_trip_visibility_invalid_value_raises_error(self, db_session: AsyncSession, test_user):
        """Test that invalid trip_visibility value raises ValidationError."""
        # Act & Assert - Pydantic should catch this during schema validation
        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdateRequest(trip_visibility='invalid')

        # Verify error message mentions trip_visibility or pattern
        error_str = str(exc_info.value)
        assert "trip_visibility" in error_str.lower() or "pattern" in error_str.lower()

    async def test_update_trip_visibility_with_other_fields(self, db_session: AsyncSession, test_user):
        """Test updating trip_visibility along with other profile fields."""
        profile_service = ProfileService(db_session)

        # Act - update multiple fields including trip_visibility
        update_data = ProfileUpdateRequest(
            bio="Updated bio with trip visibility",
            location="Madrid, España",
            trip_visibility='followers'
        )
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert - all fields should be updated
        assert result.bio == "Updated bio with trip visibility"
        assert result.location == "Madrid, España"
        assert result.trip_visibility == 'followers'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.trip_visibility == 'followers'

    async def test_update_trip_visibility_without_trip_visibility_keeps_current(self, db_session: AsyncSession, test_user):
        """Test that omitting trip_visibility in update preserves current value."""
        profile_service = ProfileService(db_session)

        # Arrange - set to followers
        test_user.trip_visibility = 'followers'
        await db_session.commit()

        # Act - update other fields without trip_visibility
        update_data = ProfileUpdateRequest(bio="Just updating bio")
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert - visibility should remain followers
        assert result.trip_visibility == 'followers'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.trip_visibility == 'followers'

    async def test_update_both_visibilities_together(self, db_session: AsyncSession, test_user):
        """Test updating both profile_visibility and trip_visibility simultaneously."""
        profile_service = ProfileService(db_session)

        # Act - update both visibility fields
        update_data = ProfileUpdateRequest(
            profile_visibility='private',
            trip_visibility='followers'
        )
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert - both should be updated
        assert result.profile_visibility == 'private'
        assert result.trip_visibility == 'followers'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.profile_visibility == 'private'
        assert test_user.trip_visibility == 'followers'
