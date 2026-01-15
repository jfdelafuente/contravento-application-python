"""
File storage utilities for photo uploads.

Handles profile photo upload, validation, resizing, and storage path management.
"""

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO, Optional

import aiofiles
from fastapi import UploadFile
from PIL import Image

from src.config import settings

logger = logging.getLogger(__name__)


# Allowed MIME types for photos
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Allowed file extensions
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def get_storage_path(user_id: str, filename: str) -> str:
    """
    Generate storage path for a user's photo.

    Path structure: storage/profile_photos/{year}/{month}/{user_id}_{uuid}.jpg

    Args:
        user_id: User's ID
        filename: Original filename (extension will be extracted)

    Returns:
        Relative path for storing the file

    Example:
        >>> get_storage_path("user123", "photo.jpg")
        'profile_photos/2025/12/user123_a1b2c3d4.jpg'
    """
    now = datetime.now(UTC)
    year = now.strftime("%Y")
    month = now.strftime("%m")

    # Generate unique filename
    file_ext = Path(filename).suffix or ".jpg"
    unique_id = uuid.uuid4().hex[:8]
    new_filename = f"{user_id}_{unique_id}{file_ext}"

    # Create path: profile_photos/YYYY/MM/user_id_uuid.ext
    relative_path = f"profile_photos/{year}/{month}/{new_filename}"

    return relative_path


def get_full_path(relative_path: str) -> Path:
    """
    Get full filesystem path from relative path.

    Args:
        relative_path: Relative path from storage root

    Returns:
        Full Path object

    Example:
        >>> get_full_path("profile_photos/2025/12/photo.jpg")
        Path('/app/storage/profile_photos/2025/12/photo.jpg')
    """
    return Path(settings.storage_path) / relative_path


def generate_photo_filename(user_id: str, extension: str) -> str:
    """
    Generate unique filename for profile photo.

    Args:
        user_id: User's ID
        extension: File extension (without dot, e.g., 'jpg')

    Returns:
        Unique filename

    Example:
        >>> generate_photo_filename("user123", "jpg")
        'user123_a1b2c3d4.jpg'
    """
    unique_id = uuid.uuid4().hex[:8]
    # Ensure extension doesn't have a leading dot
    ext = extension.lstrip(".")
    return f"{user_id}_{unique_id}.{ext}"


def validate_photo(photo_bytes: BinaryIO, content_type: str, max_size_mb: int = 5) -> None:
    """
    Validate photo file (sync version for BytesIO).

    Checks:
    - MIME type (JPEG, PNG, WebP)
    - File size (configurable, default 5MB)
    - Content is actually an image

    Args:
        photo_bytes: Photo content as BytesIO
        content_type: MIME type from upload
        max_size_mb: Maximum file size in MB

    Raises:
        ValueError: If validation fails with Spanish error message

    Example:
        >>> from io import BytesIO
        >>> photo_bytes = BytesIO(photo_content)
        >>> validate_photo(photo_bytes, "image/jpeg", max_size_mb=5)
    """
    # Check MIME type
    if content_type not in ALLOWED_PHOTO_TYPES:
        raise ValueError("Solo se permiten archivos JPEG, PNG y WebP")

    # Check file size
    photo_bytes.seek(0, 2)  # Seek to end
    file_size = photo_bytes.tell()
    photo_bytes.seek(0)  # Reset to beginning

    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise ValueError(f"El archivo no puede superar {max_size_mb}MB")

    if file_size == 0:
        raise ValueError("El archivo está vacío")

    # Validate image content
    try:
        image = Image.open(photo_bytes)
        image.verify()
        photo_bytes.seek(0)  # Reset after verify
    except Exception as e:
        logger.warning(f"Invalid image file: {str(e)}")
        raise ValueError("El archivo no es una imagen válida")


def resize_photo(file_path: Path, target_size: int = 400) -> Path:
    """
    Resize photo to square dimensions (sync version).

    Per FR-013: Profile photos are resized to 400x400px.

    Args:
        file_path: Path to original photo
        target_size: Target dimension (square)

    Returns:
        Path to resized photo (same location, replaces original)

    Example:
        >>> resized = resize_photo(Path("photo.jpg"), 400)
        >>> # Photo is now 400x400px
    """
    try:
        # Open image
        image = Image.open(file_path)

        # Convert to RGB if needed (handles PNG with transparency)
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Calculate crop box to make square (center crop)
        width, height = image.size
        if width != height:
            # Crop to square
            min_dimension = min(width, height)
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension
            image = image.crop((left, top, right, bottom))

        # Resize to target size
        image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)

        # Save optimized JPEG
        output_path = file_path.with_suffix(".jpg")
        image.save(output_path, "JPEG", quality=85, optimize=True)

        # If original was PNG/WebP, delete it
        if file_path != output_path and file_path.exists():
            file_path.unlink()

        logger.info(f"Resized photo to {target_size}x{target_size}: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to resize photo {file_path}: {str(e)}")
        raise


async def validate_photo_async(file: UploadFile) -> tuple[bool, Optional[str]]:
    """
    Validate uploaded photo file (async version for FastAPI UploadFile).

    Checks:
    - File size (max 5MB per FR-012)
    - MIME type (JPEG, PNG, WebP)
    - Content is actually an image

    Args:
        file: Uploaded file object

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> valid, error = await validate_photo_async(upload_file)
        >>> if not valid:
        ...     raise ValueError(error)
    """
    # Check MIME type
    if file.content_type not in ALLOWED_PHOTO_TYPES:
        return False, "Solo se permiten archivos JPEG, PNG y WebP"

    # Read file to check size
    content = await file.read()
    file_size = len(content)

    # Reset file pointer for later use
    await file.seek(0)

    max_size_bytes = settings.upload_max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        max_mb = settings.upload_max_size_mb
        return False, f"El archivo no puede superar {max_mb}MB"

    if file_size == 0:
        return False, "El archivo está vacío"

    # Try to open as image to validate content
    try:
        image = Image.open(file.file)
        image.verify()
        await file.seek(0)  # Reset after verify
        return True, None
    except Exception as e:
        logger.warning(f"Invalid image file: {str(e)}")
        return False, "El archivo no es una imagen válida"


async def save_profile_photo(user_id: str, file: UploadFile) -> str:
    """
    Save and process a profile photo.

    Process:
    1. Validate file (FR-012)
    2. Generate storage path
    3. Save original
    4. Resize to 400x400 (FR-013)
    5. Delete original if different format

    Args:
        user_id: User's ID
        file: Uploaded file object

    Returns:
        Relative path to saved photo (for storing in database)

    Raises:
        ValueError: If file validation fails
        IOError: If file save fails

    Example:
        >>> photo_url = await save_profile_photo("user123", upload_file)
        >>> # photo_url: "profile_photos/2025/12/user123_a1b2c3d4.jpg"
    """
    # Validate photo
    is_valid, error_message = await validate_photo_async(file)
    if not is_valid:
        raise ValueError(error_message)

    # Generate storage path
    relative_path = get_storage_path(user_id, file.filename)
    full_path = get_full_path(relative_path)

    # Create directory if not exists
    full_path.parent.mkdir(parents=True, exist_ok=True)

    # Save original file
    try:
        async with aiofiles.open(full_path, "wb") as f:
            content = await file.read()
            await f.write(content)

        logger.info(f"Saved original photo: {full_path}")

        # Resize photo (this replaces the original)
        resized_path = resize_photo(full_path, settings.profile_photo_size)

        # Update relative path if extension changed
        relative_path = str(resized_path.relative_to(settings.storage_path))

        return relative_path

    except Exception as e:
        logger.error(f"Failed to save photo: {str(e)}")
        # Clean up on error
        if full_path.exists():
            full_path.unlink()
        raise OSError(f"Error al guardar la foto: {str(e)}")


async def delete_profile_photo(relative_path: str) -> bool:
    """
    Delete a profile photo from storage.

    Args:
        relative_path: Relative path to photo

    Returns:
        True if deleted successfully, False otherwise

    Example:
        >>> await delete_profile_photo("profile_photos/2025/12/user123_a1b2c3d4.jpg")
        True
    """
    try:
        full_path = get_full_path(relative_path)

        if full_path.exists():
            full_path.unlink()
            logger.info(f"Deleted photo: {full_path}")
            return True
        else:
            logger.warning(f"Photo not found for deletion: {full_path}")
            return False

    except Exception as e:
        logger.error(f"Failed to delete photo {relative_path}: {str(e)}")
        return False
