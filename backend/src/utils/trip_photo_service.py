"""
Trip photo processing service.

Handles photo validation, resizing, optimization, and thumbnail generation
for travel diary photos using Pillow.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import io
import uuid
from datetime import datetime
import logging

from PIL import Image, ImageOps
from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PhotoProcessingResult:
    """Result of photo processing operation."""

    optimized_bytes: bytes  # Optimized full-size photo
    thumbnail_bytes: bytes  # Square thumbnail
    width: int  # Original width
    height: int  # Original height
    file_size: int  # Original file size in bytes


@dataclass
class PhotoPaths:
    """File paths for saved photo versions."""

    optimized_path: Path  # Path to optimized version
    thumbnail_path: Path  # Path to thumbnail version


class TripPhotoService:
    """Service for processing trip photos."""

    # Supported image formats
    SUPPORTED_FORMATS = {'JPEG', 'PNG', 'WEBP'}

    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(self) -> None:
        """Initialize photo service."""
        pass

    def validate_photo(self, photo_bytes: bytes, filename: str) -> Optional[str]:
        """
        Validate photo file.

        Args:
            photo_bytes: Raw photo file bytes
            filename: Original filename (for error messages)

        Returns:
            Error message (Spanish) if validation fails, None if valid

        Examples:
            >>> service = TripPhotoService()
            >>> service.validate_photo(valid_jpeg_bytes, "photo.jpg")
            None

            >>> service.validate_photo(text_bytes, "not-image.txt")
            "El archivo no es una imagen válida..."
        """
        # Check file size
        if len(photo_bytes) > self.MAX_FILE_SIZE:
            size_mb = len(photo_bytes) / (1024 * 1024)
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            return (
                f"La foto es demasiado grande ({size_mb:.1f}MB). "
                f"El tamaño máximo permitido es {max_mb:.0f}MB."
            )

        # Try to open as image
        try:
            img = Image.open(io.BytesIO(photo_bytes))
            img.verify()  # Verify it's actually an image

            # Re-open after verify (verify() closes the file)
            img = Image.open(io.BytesIO(photo_bytes))

            # Check format is supported
            if img.format not in self.SUPPORTED_FORMATS:
                return (
                    f"Formato de imagen no soportado: {img.format}. "
                    f"Formatos permitidos: JPEG, PNG, WebP."
                )

        except Exception as e:
            logger.warning(f"Invalid image file {filename}: {e}")
            return (
                "El archivo no es una imagen válida. "
                "Por favor, sube una foto en formato JPEG, PNG o WebP."
            )

        return None

    def process_photo(self, photo_bytes: bytes, filename: str) -> PhotoProcessingResult:
        """
        Process photo: resize, optimize, create thumbnail.

        Args:
            photo_bytes: Raw photo file bytes
            filename: Original filename

        Returns:
            PhotoProcessingResult with optimized and thumbnail versions

        Raises:
            ValueError: If photo cannot be processed
        """
        try:
            # Open image
            img = Image.open(io.BytesIO(photo_bytes))

            # Handle EXIF orientation (rotate if needed)
            img = ImageOps.exif_transpose(img)

            # Convert to RGB if needed (handles PNG with transparency, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Store original dimensions
            original_width, original_height = img.size

            # Create optimized version (resize if needed)
            optimized_img = self._resize_photo(img, settings.photo_max_width)

            # Create thumbnail (square crop)
            thumbnail_img = self._create_thumbnail(img, settings.photo_thumb_size)

            # Convert to bytes
            optimized_bytes = self._image_to_bytes(
                optimized_img,
                quality=settings.photo_quality_optimized
            )
            thumbnail_bytes = self._image_to_bytes(
                thumbnail_img,
                quality=settings.photo_quality_thumb
            )

            return PhotoProcessingResult(
                optimized_bytes=optimized_bytes,
                thumbnail_bytes=thumbnail_bytes,
                width=original_width,
                height=original_height,
                file_size=len(photo_bytes)
            )

        except Exception as e:
            logger.error(f"Error processing photo {filename}: {e}")
            raise ValueError(f"Error al procesar la foto: {str(e)}")

    def _resize_photo(self, img: Image.Image, max_width: int) -> Image.Image:
        """
        Resize photo to max width while maintaining aspect ratio.

        Does not upscale images smaller than max_width.
        """
        width, height = img.size

        # Don't upscale small images
        if width <= max_width:
            return img.copy()

        # Calculate new dimensions maintaining aspect ratio
        ratio = max_width / width
        new_width = max_width
        new_height = int(height * ratio)

        # Use LANCZOS for high-quality downsampling
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _create_thumbnail(self, img: Image.Image, size: int) -> Image.Image:
        """
        Create square thumbnail by cropping center.

        Args:
            img: Source image
            size: Thumbnail size (width and height)

        Returns:
            Square thumbnail image
        """
        # Calculate crop box for center square
        width, height = img.size

        if width > height:
            # Landscape: crop sides
            left = (width - height) // 2
            top = 0
            right = left + height
            bottom = height
        else:
            # Portrait: crop top/bottom
            left = 0
            top = (height - width) // 2
            right = width
            bottom = top + width

        # Crop to square
        square = img.crop((left, top, right, bottom))

        # Resize to thumbnail size
        return square.resize((size, size), Image.Resampling.LANCZOS)

    def _image_to_bytes(self, img: Image.Image, quality: int) -> bytes:
        """
        Convert PIL Image to JPEG bytes.

        Args:
            img: PIL Image
            quality: JPEG quality (1-100)

        Returns:
            JPEG bytes
        """
        buffer = io.BytesIO()
        img.save(
            buffer,
            format='JPEG',
            quality=quality,
            optimize=True,  # Enable optimization
            progressive=True  # Progressive JPEG (loads incrementally)
        )
        return buffer.getvalue()

    def save_photo(
        self,
        result: PhotoProcessingResult,
        trip_id: str,
        original_filename: str
    ) -> PhotoPaths:
        """
        Save processed photo to filesystem.

        Directory structure: {storage_path}/trip_photos/YYYY/MM/{trip_id}/

        Args:
            result: Photo processing result
            trip_id: Trip UUID
            original_filename: Original filename (for extension)

        Returns:
            PhotoPaths with saved file paths
        """
        # Generate unique filename with UUID
        file_uuid = uuid.uuid4().hex[:12]
        filename_base = f"{file_uuid}.jpg"  # Always save as JPEG

        # Build directory path: YYYY/MM/trip_id/
        now = datetime.utcnow()
        dir_path = Path(settings.trip_photos_full_path) / str(now.year) / f"{now.month:02d}" / trip_id

        # Create directories if needed
        dir_path.mkdir(parents=True, exist_ok=True)

        # File paths
        optimized_path = dir_path / filename_base
        thumbnail_path = dir_path / f"{file_uuid}_thumb.jpg"

        # Write files
        optimized_path.write_bytes(result.optimized_bytes)
        thumbnail_path.write_bytes(result.thumbnail_bytes)

        logger.info(f"Saved trip photo: {optimized_path}")

        return PhotoPaths(
            optimized_path=optimized_path,
            thumbnail_path=thumbnail_path
        )

    def delete_photo(self, optimized_path: str, thumbnail_path: str) -> None:
        """
        Delete photo files from filesystem.

        Args:
            optimized_path: Path to optimized version
            thumbnail_path: Path to thumbnail version
        """
        try:
            opt_file = Path(optimized_path)
            if opt_file.exists():
                opt_file.unlink()
                logger.info(f"Deleted photo: {optimized_path}")
        except Exception as e:
            logger.warning(f"Error deleting optimized photo {optimized_path}: {e}")

        try:
            thumb_file = Path(thumbnail_path)
            if thumb_file.exists():
                thumb_file.unlink()
        except Exception as e:
            logger.warning(f"Error deleting thumbnail {thumbnail_path}: {e}")


# Global singleton instance
trip_photo_service = TripPhotoService()
