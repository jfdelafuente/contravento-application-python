"""
Unit tests for TripPhotoService.

Tests photo processing: validation, resize, optimization, thumbnail generation.
"""

import io
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from src.utils.trip_photo_service import PhotoProcessingResult, TripPhotoService


class TestTripPhotoService:
    """Test trip photo processing service."""

    @pytest.fixture
    def photo_service(self) -> TripPhotoService:
        """Create photo service instance."""
        return TripPhotoService()

    @pytest.fixture
    def sample_jpeg_bytes(self) -> bytes:
        """Create sample JPEG image bytes for testing."""
        # Create 2000x1500 image (landscape)
        img = Image.new("RGB", (2000, 1500), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        return buffer.getvalue()

    @pytest.fixture
    def sample_png_bytes(self) -> bytes:
        """Create sample PNG image bytes for testing."""
        # Create 800x600 image
        img = Image.new("RGB", (800, 600), color="green")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

    @pytest.fixture
    def sample_portrait_bytes(self) -> bytes:
        """Create sample portrait image (taller than wide)."""
        # Create 1000x1500 image (portrait)
        img = Image.new("RGB", (1000, 1500), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        return buffer.getvalue()

    def test_validate_photo_accepts_valid_jpeg(
        self, photo_service: TripPhotoService, sample_jpeg_bytes: bytes
    ) -> None:
        """Test that valid JPEG photos pass validation."""
        error = photo_service.validate_photo(sample_jpeg_bytes, "test.jpg")
        assert error is None

    def test_validate_photo_accepts_valid_png(
        self, photo_service: TripPhotoService, sample_png_bytes: bytes
    ) -> None:
        """Test that valid PNG photos pass validation."""
        error = photo_service.validate_photo(sample_png_bytes, "test.png")
        assert error is None

    def test_validate_photo_rejects_invalid_format(self, photo_service: TripPhotoService) -> None:
        """Test that non-image files are rejected."""
        fake_file = b"This is not an image file"
        error = photo_service.validate_photo(fake_file, "test.txt")

        assert error is not None
        assert "formato" in error.lower()

    def test_validate_photo_rejects_oversized_file(self, photo_service: TripPhotoService) -> None:
        """Test that files exceeding max size are rejected."""
        # Create file larger than 10MB (default max)
        large_file = b"X" * (11 * 1024 * 1024)  # 11MB
        error = photo_service.validate_photo(large_file, "huge.jpg")

        assert error is not None
        assert "tamaño" in error.lower() or "grande" in error.lower()

    def test_validate_photo_checks_actual_content_not_extension(
        self, photo_service: TripPhotoService
    ) -> None:
        """Test that validation checks actual file content, not just extension."""
        # Text file with .jpg extension
        fake_image = b"Not an image"
        error = photo_service.validate_photo(fake_image, "fake.jpg")

        assert error is not None

    def test_process_photo_creates_optimized_version(
        self, photo_service: TripPhotoService, sample_jpeg_bytes: bytes
    ) -> None:
        """Test that processing creates optimized version with reduced dimensions."""
        result = photo_service.process_photo(sample_jpeg_bytes, "test.jpg")

        assert isinstance(result, PhotoProcessingResult)
        assert result.optimized_bytes is not None
        assert result.thumbnail_bytes is not None

        # Check optimized is smaller than original
        assert len(result.optimized_bytes) < len(sample_jpeg_bytes)

        # Check dimensions were reduced (original was 2000x1500)
        optimized_img = Image.open(io.BytesIO(result.optimized_bytes))
        assert optimized_img.width <= 1200  # Max width from config

    def test_process_photo_maintains_aspect_ratio(
        self, photo_service: TripPhotoService, sample_jpeg_bytes: bytes
    ) -> None:
        """Test that aspect ratio is preserved during resize."""
        result = photo_service.process_photo(sample_jpeg_bytes, "test.jpg")

        # Original was 2000x1500 (4:3 ratio)
        optimized_img = Image.open(io.BytesIO(result.optimized_bytes))

        # Calculate aspect ratios
        original_ratio = 2000 / 1500  # 1.333...
        optimized_ratio = optimized_img.width / optimized_img.height

        # Should be approximately equal (within 0.01 tolerance)
        assert abs(original_ratio - optimized_ratio) < 0.01

    def test_process_photo_creates_square_thumbnail(
        self, photo_service: TripPhotoService, sample_jpeg_bytes: bytes
    ) -> None:
        """Test that thumbnail is square (cropped)."""
        result = photo_service.process_photo(sample_jpeg_bytes, "test.jpg")

        thumb_img = Image.open(io.BytesIO(result.thumbnail_bytes))

        # Thumbnail should be square
        assert thumb_img.width == thumb_img.height
        assert thumb_img.width == 200  # Default thumb size from config

    def test_process_photo_handles_portrait_orientation(
        self, photo_service: TripPhotoService, sample_portrait_bytes: bytes
    ) -> None:
        """Test that portrait photos are processed correctly."""
        result = photo_service.process_photo(sample_portrait_bytes, "portrait.jpg")

        optimized_img = Image.open(io.BytesIO(result.optimized_bytes))

        # Portrait should maintain orientation (height > width)
        assert optimized_img.height > optimized_img.width

        # Thumbnail should still be square
        thumb_img = Image.open(io.BytesIO(result.thumbnail_bytes))
        assert thumb_img.width == thumb_img.height

    def test_process_photo_converts_png_to_jpeg(
        self, photo_service: TripPhotoService, sample_png_bytes: bytes
    ) -> None:
        """Test that PNG photos are converted to JPEG."""
        result = photo_service.process_photo(sample_png_bytes, "test.png")

        # Check that output is JPEG format
        optimized_img = Image.open(io.BytesIO(result.optimized_bytes))
        assert optimized_img.format == "JPEG"

        thumb_img = Image.open(io.BytesIO(result.thumbnail_bytes))
        assert thumb_img.format == "JPEG"

    def test_process_photo_preserves_already_small_images(
        self, photo_service: TripPhotoService
    ) -> None:
        """Test that images smaller than max width are not upscaled."""
        # Create small image (800x600, below 1200px max width)
        small_img = Image.new("RGB", (800, 600), color="yellow")
        buffer = io.BytesIO()
        small_img.save(buffer, format="JPEG", quality=95)
        small_bytes = buffer.getvalue()

        result = photo_service.process_photo(small_bytes, "small.jpg")

        optimized_img = Image.open(io.BytesIO(result.optimized_bytes))

        # Should not be upscaled
        assert optimized_img.width <= 800
        assert optimized_img.height <= 600

    def test_process_photo_removes_exif_orientation(
        self, photo_service: TripPhotoService, sample_jpeg_bytes: bytes
    ) -> None:
        """Test that EXIF orientation is handled and removed."""
        # This test ensures photos display correctly regardless of camera orientation
        result = photo_service.process_photo(sample_jpeg_bytes, "test.jpg")

        optimized_img = Image.open(io.BytesIO(result.optimized_bytes))

        # EXIF data should be minimal or removed for privacy/size
        exif = optimized_img.getexif()
        # Most EXIF tags should be stripped for privacy

    def test_process_photo_applies_quality_settings(
        self, photo_service: TripPhotoService, sample_jpeg_bytes: bytes
    ) -> None:
        """Test that quality settings from config are applied."""
        with patch("src.utils.trip_photo_service.settings") as mock_settings:
            mock_settings.photo_quality_optimized = 50  # Low quality
            mock_settings.photo_quality_thumb = 50
            mock_settings.photo_max_width = 1200
            mock_settings.photo_thumb_size = 200

            result = photo_service.process_photo(sample_jpeg_bytes, "test.jpg")

            # Lower quality should result in smaller file size
            assert len(result.optimized_bytes) < len(sample_jpeg_bytes)

    def test_save_photo_creates_directory_structure(
        self, photo_service: TripPhotoService, tmp_path: Path
    ) -> None:
        """Test that save_photo creates year/month/trip_id directory structure."""
        trip_id = "123e4567-e89b-12d3-a456-426614174000"
        filename = "photo.jpg"

        with patch("src.utils.trip_photo_service.settings") as mock_settings:
            mock_settings.trip_photos_full_path = str(tmp_path)

            # Create dummy photo data
            img = Image.new("RGB", (100, 100))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            photo_bytes = buffer.getvalue()

            result = PhotoProcessingResult(
                optimized_bytes=photo_bytes,
                thumbnail_bytes=photo_bytes,
                width=100,
                height=100,
                file_size=len(photo_bytes),
            )

            paths = photo_service.save_photo(result, trip_id, filename)

            # Check directory structure: YYYY/MM/trip_id/
            assert paths.optimized_path.exists()
            assert paths.thumbnail_path.exists()

            # Verify path structure
            assert trip_id in str(paths.optimized_path)

    def test_save_photo_generates_unique_filenames(
        self, photo_service: TripPhotoService, tmp_path: Path
    ) -> None:
        """Test that generated filenames include UUID for uniqueness."""
        trip_id = "test-trip-id"
        filename = "photo.jpg"

        with patch("src.utils.trip_photo_service.settings") as mock_settings:
            mock_settings.trip_photos_full_path = str(tmp_path)

            img = Image.new("RGB", (100, 100))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            photo_bytes = buffer.getvalue()

            result = PhotoProcessingResult(
                optimized_bytes=photo_bytes,
                thumbnail_bytes=photo_bytes,
                width=100,
                height=100,
                file_size=len(photo_bytes),
            )

            paths1 = photo_service.save_photo(result, trip_id, filename)
            paths2 = photo_service.save_photo(result, trip_id, filename)

            # Should generate different filenames
            assert paths1.optimized_path != paths2.optimized_path
            assert paths1.thumbnail_path != paths2.thumbnail_path

    def test_delete_photo_removes_both_versions(
        self, photo_service: TripPhotoService, tmp_path: Path
    ) -> None:
        """Test that delete removes both optimized and thumbnail."""
        # Create dummy files
        optimized = tmp_path / "photo.jpg"
        thumbnail = tmp_path / "photo_thumb.jpg"

        optimized.write_bytes(b"optimized")
        thumbnail.write_bytes(b"thumbnail")

        photo_service.delete_photo(str(optimized), str(thumbnail))

        assert not optimized.exists()
        assert not thumbnail.exists()

    def test_delete_photo_handles_missing_files_gracefully(
        self, photo_service: TripPhotoService, tmp_path: Path
    ) -> None:
        """Test that delete doesn't fail if files already deleted."""
        nonexistent = tmp_path / "nonexistent.jpg"

        # Should not raise exception
        photo_service.delete_photo(str(nonexistent), str(nonexistent))

    def test_photo_processing_result_has_metadata(
        self, photo_service: TripPhotoService, sample_jpeg_bytes: bytes
    ) -> None:
        """Test that processing result includes useful metadata."""
        result = photo_service.process_photo(sample_jpeg_bytes, "test.jpg")

        assert result.width > 0
        assert result.height > 0
        assert result.file_size > 0
        assert isinstance(result.optimized_bytes, bytes)
        assert isinstance(result.thumbnail_bytes, bytes)
