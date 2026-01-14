"""
Unit tests for ProfileService business logic.

Tests profile management service methods.
"""


import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.profile import ProfileUpdateRequest
from src.services.profile_service import ProfileService


@pytest.mark.unit
@pytest.mark.asyncio
class TestProfileServiceGetProfile:
    """T110: Unit tests for ProfileService.get_profile()."""

    async def test_get_profile_returns_public_data(self, db_session: AsyncSession):
        """Verify that get_profile returns public profile data."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_get_profile_respects_show_email_privacy(self, db_session: AsyncSession):
        """Verify that email is hidden when show_email is False."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_get_profile_respects_show_location_privacy(self, db_session: AsyncSession):
        """Verify that location is hidden when show_location is False."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_get_profile_nonexistent_user_raises_error(self, db_session: AsyncSession):
        """Verify that getting non-existent user profile raises ValueError."""
        # Arrange
        profile_service = ProfileService(db_session)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await profile_service.get_profile("nonexistent_user")

        assert (
            "no existe" in str(exc_info.value).lower() or "not found" in str(exc_info.value).lower()
        )


@pytest.mark.unit
@pytest.mark.asyncio
class TestProfileServiceUpdateProfile:
    """T111: Unit tests for ProfileService.update_profile()."""

    async def test_update_profile_updates_all_fields(self, db_session: AsyncSession):
        """Verify that update_profile updates all provided fields."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_update_profile_partial_update(self, db_session: AsyncSession):
        """Verify that partial updates only change specified fields."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_update_profile_validates_bio_length(self, db_session: AsyncSession):
        """Verify that bio longer than 500 chars is rejected."""
        # Arrange
        profile_service = ProfileService(db_session)
        long_bio = "a" * 501

        update_data = ProfileUpdateRequest(bio=long_bio)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await profile_service.update_profile("user123", update_data)

        assert "500" in str(exc_info.value) or "caracteres" in str(exc_info.value).lower()

    async def test_update_profile_validates_cycling_type(self, db_session: AsyncSession):
        """Verify that invalid cycling_type is rejected."""
        # Arrange
        profile_service = ProfileService(db_session)

        update_data = ProfileUpdateRequest(cycling_type="invalid_type")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await profile_service.update_profile("user123", update_data)

        assert (
            "ciclismo" in str(exc_info.value).lower()
            or "cycling_type" in str(exc_info.value).lower()
        )

    async def test_update_profile_strips_whitespace_from_bio(self, db_session: AsyncSession):
        """Verify that bio whitespace is stripped."""
        pytest.skip("TODO: Implement after ProfileService is created")


@pytest.mark.unit
@pytest.mark.asyncio
class TestProfileServiceUploadPhoto:
    """T112: Unit tests for ProfileService.upload_photo()."""

    async def test_upload_photo_stores_url(self, db_session: AsyncSession):
        """Verify that upload_photo stores photo URL in profile."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_upload_photo_deletes_old_photo(self, db_session: AsyncSession):
        """Verify that uploading new photo removes old one."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_upload_photo_validates_file_format(self, db_session: AsyncSession):
        """Verify that invalid file formats are rejected."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_upload_photo_validates_file_size(self, db_session: AsyncSession):
        """Verify that files over 5MB are rejected."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_upload_photo_resizes_to_400x400(self, db_session: AsyncSession):
        """Verify that photos are resized to 400x400."""
        pytest.skip("TODO: Implement after ProfileService is created")


@pytest.mark.unit
@pytest.mark.asyncio
class TestProfileServiceDeletePhoto:
    """T113: Unit tests for ProfileService.delete_photo()."""

    async def test_delete_photo_removes_url_from_profile(self, db_session: AsyncSession):
        """Verify that delete_photo sets photo_url to None."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_delete_photo_removes_file_from_storage(self, db_session: AsyncSession):
        """Verify that delete_photo removes file from filesystem."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_delete_photo_when_no_photo_exists(self, db_session: AsyncSession):
        """Verify that deleting when no photo exists doesn't error."""
        pytest.skip("TODO: Implement after ProfileService is created")


@pytest.mark.unit
@pytest.mark.asyncio
class TestProfileServiceUpdatePrivacy:
    """T114: Unit tests for ProfileService.update_privacy()."""

    async def test_update_privacy_sets_show_email(self, db_session: AsyncSession):
        """Verify that update_privacy correctly sets show_email."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_update_privacy_sets_show_location(self, db_session: AsyncSession):
        """Verify that update_privacy correctly sets show_location."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_update_privacy_partial_update(self, db_session: AsyncSession):
        """Verify that updating only one privacy setting works."""
        pytest.skip("TODO: Implement after ProfileService is created")

    async def test_update_privacy_returns_updated_settings(self, db_session: AsyncSession):
        """Verify that update_privacy returns the new privacy settings."""
        pytest.skip("TODO: Implement after ProfileService is created")


@pytest.mark.unit
@pytest.mark.asyncio
class TestProfileServiceVisibility:
    """Feature 013: Unit tests for profile_visibility updates via ProfileService.update_profile()."""

    async def test_update_profile_visibility_to_private(self, db_session: AsyncSession, test_user):
        """Test updating profile_visibility from public to private."""
        # Arrange
        profile_service = ProfileService(db_session)
        assert test_user.profile_visibility == 'public'  # Default

        # Act
        update_data = ProfileUpdateRequest(profile_visibility='private')
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert
        assert result.profile_visibility == 'private'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.profile_visibility == 'private'

    async def test_update_profile_visibility_to_public(self, db_session: AsyncSession, test_user):
        """Test updating profile_visibility from private to public."""
        # Arrange
        profile_service = ProfileService(db_session)
        test_user.profile_visibility = 'private'
        await db_session.commit()

        # Act
        update_data = ProfileUpdateRequest(profile_visibility='public')
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert
        assert result.profile_visibility == 'public'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.profile_visibility == 'public'

    async def test_update_profile_visibility_invalid_value_raises_error(self, db_session: AsyncSession, test_user):
        """Test that invalid profile_visibility value raises ValidationError."""
        from pydantic import ValidationError

        # Arrange & Act & Assert
        # Pydantic validates the pattern before reaching the service
        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdateRequest(profile_visibility='invalid')

        # Verify error message mentions pattern validation
        error_str = str(exc_info.value)
        assert "profile_visibility" in error_str.lower() or "pattern" in error_str.lower()

    async def test_update_profile_visibility_with_other_fields(self, db_session: AsyncSession, test_user):
        """Test updating profile_visibility along with other profile fields."""
        # Arrange
        profile_service = ProfileService(db_session)

        # Act
        update_data = ProfileUpdateRequest(
            bio="New bio for testing",
            location="Test City",
            profile_visibility='private'
        )
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert
        assert result.profile_visibility == 'private'
        assert result.bio == "New bio for testing"
        assert result.location == "Test City"

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.profile_visibility == 'private'

    async def test_update_profile_without_visibility_keeps_current(self, db_session: AsyncSession, test_user):
        """Test that not providing profile_visibility keeps the current value."""
        # Arrange
        profile_service = ProfileService(db_session)
        test_user.profile_visibility = 'private'
        await db_session.commit()

        # Act - update other fields without profile_visibility
        update_data = ProfileUpdateRequest(bio="Just updating bio")
        result = await profile_service.update_profile(test_user.username, update_data)

        # Assert - visibility should remain private
        assert result.profile_visibility == 'private'

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.profile_visibility == 'private'
