"""
Profile service for managing user profiles and photos.

Business logic for profile management including:
- Profile updates
- Photo upload and processing
- Privacy settings
- Public profile views
"""

import asyncio
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.config import settings
from src.models.user import User, UserProfile
from src.schemas.profile import (
    PrivacySettings,
    ProfileResponse,
    ProfileStatsPreview,
    ProfileUpdateRequest,
)
from src.utils.file_storage import generate_photo_filename, resize_photo, validate_photo
from src.utils.security import hash_password, verify_password

logger = logging.getLogger(__name__)


class ProfileService:
    """
    Profile service for managing user profiles.

    Handles profile retrieval, updates, photo management, and privacy settings.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize profile service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_profile(
        self, username: str, viewer_username: Optional[str] = None
    ) -> ProfileResponse:
        """
        T118: Get user profile respecting privacy settings.

        Args:
            username: Username of profile to retrieve
            viewer_username: Username of viewer (None for anonymous)

        Returns:
            ProfileResponse with public profile data

        Raises:
            ValueError: If user not found
        """
        # T226: Optimized query with eager loading for profile and stats
        result = await self.db.execute(
            select(User)
            .options(joinedload(User.profile), joinedload(User.stats))
            .where(User.username == username)
        )
        user = result.unique().scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        # Get or create profile
        profile = user.profile
        if not profile:
            # Create empty profile if doesn't exist
            profile = UserProfile(user_id=user.id)
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)

        # Get stats (already loaded via eager loading)
        stats = user.stats

        stats_preview = None
        if stats:
            stats_preview = ProfileStatsPreview(
                total_trips=stats.total_trips,
                total_kilometers=stats.total_kilometers,
                achievements_count=stats.achievements_count,
            )

        # Build response respecting privacy
        is_owner = viewer_username == username

        # Convert relative photo URLs to absolute URLs for backward compatibility
        photo_url = profile.profile_photo_url
        if photo_url and photo_url.startswith("/storage/"):
            photo_url = f"{settings.backend_url}{photo_url}"

        return ProfileResponse(
            username=user.username,
            full_name=profile.full_name,
            bio=profile.bio,
            photo_url=photo_url,
            location=profile.location if (profile.show_location or is_owner) else None,
            cycling_type=profile.cycling_type,
            profile_visibility=user.profile_visibility,
            trip_visibility=user.trip_visibility,
            show_email=profile.show_email,
            show_location=profile.show_location,
            followers_count=profile.followers_count,
            following_count=profile.following_count,
            stats=stats_preview,
            created_at=user.created_at,
        )

    async def update_profile(
        self, username: str, update_data: ProfileUpdateRequest
    ) -> ProfileResponse:
        """
        T119: Update user profile.

        Updates profile fields. Validates bio length and cycling_type.

        Args:
            username: Username of profile to update
            update_data: Profile update data

        Returns:
            Updated ProfileResponse

        Raises:
            ValueError: If user not found or validation fails
        """
        # Get user and profile
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
        profile = result.scalar_one_or_none()

        if not profile:
            # Create profile if doesn't exist
            profile = UserProfile(user_id=user.id)
            self.db.add(profile)

        # Update fields (only if provided)
        if update_data.full_name is not None:
            profile.full_name = update_data.full_name.strip() if update_data.full_name else None

        if update_data.bio is not None:
            # Bio is already validated in schema
            profile.bio = update_data.bio.strip() if update_data.bio else None

        if update_data.location is not None:
            profile.location = update_data.location.strip() if update_data.location else None

        if update_data.cycling_type is not None:
            # Validate cycling type against database (dynamic validation)
            from src.utils.validators import validate_cycling_type_async

            validated_type = await validate_cycling_type_async(update_data.cycling_type, self.db)
            profile.cycling_type = validated_type

        # Update profile_visibility in User model (Feature 013)
        if update_data.profile_visibility is not None:
            if update_data.profile_visibility not in ['public', 'private']:
                raise ValueError("profile_visibility debe ser 'public' o 'private'")
            user.profile_visibility = update_data.profile_visibility
            logger.info(f"Profile visibility updated to '{update_data.profile_visibility}' for user: {username}")

        # Update trip_visibility in User model (Feature 013)
        if update_data.trip_visibility is not None:
            if update_data.trip_visibility not in ['public', 'followers', 'private']:
                raise ValueError("trip_visibility debe ser 'public', 'followers' o 'private'")
            user.trip_visibility = update_data.trip_visibility
            logger.info(f"Trip visibility updated to '{update_data.trip_visibility}' for user: {username}")

        if update_data.show_email is not None:
            profile.show_email = update_data.show_email

        if update_data.show_location is not None:
            profile.show_location = update_data.show_location

        # Update timestamp
        profile.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Profile updated for user: {username}")

        # Return updated profile
        return await self.get_profile(username, viewer_username=username)

    async def upload_photo(self, username: str, photo_file: UploadFile) -> dict:
        """
        T120: Upload and process profile photo.

        Validates, resizes to 400x400, and stores photo.

        Args:
            username: Username of profile
            photo_file: Uploaded photo file

        Returns:
            Dict with photo_url, photo_width, photo_height

        Raises:
            ValueError: If validation fails or user not found
        """
        # Get user and profile
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
        profile = result.scalar_one()

        # Read file content
        content = await photo_file.read()

        # Validate photo (size, format)
        from io import BytesIO

        photo_bytes = BytesIO(content)

        try:
            validate_photo(photo_bytes, photo_file.content_type, max_size_mb=5)
        except ValueError as e:
            raise ValueError(str(e))

        # Generate filename
        file_ext = photo_file.filename.split(".")[-1].lower()
        if file_ext not in ["jpg", "jpeg", "png", "webp"]:
            file_ext = "jpg"

        filename = generate_photo_filename(user.id, file_ext)

        # Create storage directory
        storage_dir = (
            Path(settings.storage_path) / "profile_photos" / datetime.now(UTC).strftime("%Y/%m")
        )
        storage_dir.mkdir(parents=True, exist_ok=True)

        # T227: Async photo processing to avoid blocking event loop
        # Save file in thread pool and resize
        file_path = storage_dir / filename

        def write_and_resize():
            """Write file and resize - runs in thread pool."""
            with open(file_path, "wb") as f:
                f.write(content)
            return resize_photo(file_path, target_size=400)

        try:
            # Run I/O-bound operation in thread pool
            final_path = await asyncio.to_thread(write_and_resize)
        except Exception as e:
            # Clean up file on error
            if file_path.exists():
                file_path.unlink()
            raise ValueError(f"Error al procesar la imagen: {str(e)}")

        # Delete old photo if exists
        if profile.profile_photo_url:
            await self._delete_photo_file(profile.profile_photo_url)

        # Generate absolute URL with backend base URL
        photo_url = (
            f"{settings.backend_url}/storage/profile_photos/{datetime.now(UTC).strftime('%Y/%m')}/{final_path.name}"
        )

        # Update profile
        profile.profile_photo_url = photo_url
        profile.updated_at = datetime.now(UTC)

        await self.db.commit()

        logger.info(f"Photo uploaded for user: {username}")

        return {
            "photo_url": photo_url,
            "photo_width": 400,
            "photo_height": 400,
        }

    async def delete_photo(self, username: str) -> bool:
        """
        T121: Delete profile photo.

        Removes photo URL from profile and deletes file from storage.

        Args:
            username: Username of profile

        Returns:
            True if deletion successful

        Raises:
            ValueError: If user not found
        """
        # Get user and profile
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
        profile = result.scalar_one()

        # Delete file if exists
        if profile.profile_photo_url:
            await self._delete_photo_file(profile.profile_photo_url)

        # Remove URL from profile
        profile.profile_photo_url = None
        profile.updated_at = datetime.now(UTC)

        await self.db.commit()

        logger.info(f"Photo deleted for user: {username}")

        return True

    async def update_privacy(self, username: str, privacy_settings: PrivacySettings) -> dict:
        """
        T122: Update privacy settings.

        Updates show_email and show_location preferences.

        Args:
            username: Username of profile
            privacy_settings: Privacy settings to update

        Returns:
            Dict with updated privacy settings

        Raises:
            ValueError: If user not found
        """
        # Get user and profile
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        result = await self.db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
        profile = result.scalar_one()

        # Update privacy settings (only if provided)
        if privacy_settings.show_email is not None:
            profile.show_email = privacy_settings.show_email

        if privacy_settings.show_location is not None:
            profile.show_location = privacy_settings.show_location

        profile.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Privacy settings updated for user: {username}")

        return {
            "show_email": profile.show_email,
            "show_location": profile.show_location,
        }

    async def change_password(
        self, username: str, current_password: str, new_password: str
    ) -> bool:
        """
        T128: Change user password.

        Verifies current password and updates to new password.

        **Functional Requirements**: FR-009, FR-010

        Args:
            username: Username of user
            current_password: Current password for verification
            new_password: New password (already validated by schema)

        Returns:
            True if password changed successfully

        Raises:
            ValueError: If user not found or current password incorrect
        """
        # Get user
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"El usuario '{username}' no existe")

        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("La contraseña actual es incorrecta")

        # Update password
        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.now(UTC)

        await self.db.commit()

        logger.info(f"Password changed for user: {username}")

        return True

    async def _delete_photo_file(self, photo_url: str) -> None:
        """
        Delete photo file from filesystem.

        Args:
            photo_url: URL or path to photo file (can be relative or absolute URL)
        """
        try:
            # Extract path from URL (handle both relative and absolute URLs)
            if photo_url.startswith("/storage/"):
                # Relative URL: /storage/profile_photos/...
                file_path = Path(settings.storage_path) / photo_url.replace("/storage/", "")
            elif "/storage/" in photo_url:
                # Absolute URL: http://localhost:8000/storage/profile_photos/...
                path_part = photo_url.split("/storage/", 1)[1]
                file_path = Path(settings.storage_path) / path_part
            else:
                file_path = Path(photo_url)

            # Delete file if exists
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted photo file: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting photo file: {e}")
            # Don't raise - deletion failure shouldn't block profile update
