"""
Unit tests for file storage utilities.

Tests photo validation, resizing, and storage functions.
"""

from io import BytesIO

import pytest
from PIL import Image

from src.utils.file_storage import (
    generate_photo_filename,
    resize_photo,
    validate_photo,
)


@pytest.mark.unit
class TestPhotoResize:
    """T107: Unit test for photo resize to 400x400."""

    def test_resize_large_photo_to_400x400(self, tmp_path):
        """Verify that large photos are resized to 400x400."""
        # Arrange: Create 800x800 image
        large_image = Image.new("RGB", (800, 800), color="red")
        input_path = tmp_path / "large.jpg"
        large_image.save(input_path, "JPEG")

        # Act: Resize photo
        output_path = resize_photo(input_path, target_size=400)

        # Assert: Check dimensions
        resized_image = Image.open(output_path)
        assert resized_image.size == (400, 400)
        assert output_path.exists()

    def test_resize_small_photo_to_400x400(self, tmp_path):
        """Verify that small photos are upscaled to 400x400."""
        # Arrange: Create 200x200 image
        small_image = Image.new("RGB", (200, 200), color="blue")
        input_path = tmp_path / "small.jpg"
        small_image.save(input_path, "JPEG")

        # Act: Resize photo
        output_path = resize_photo(input_path, target_size=400)

        # Assert: Check dimensions
        resized_image = Image.open(output_path)
        assert resized_image.size == (400, 400)

    def test_resize_rectangular_photo_crops_to_square(self, tmp_path):
        """Verify that rectangular photos are cropped to square before resize."""
        # Arrange: Create 800x600 image (4:3 aspect ratio)
        rect_image = Image.new("RGB", (800, 600), color="green")
        input_path = tmp_path / "rect.jpg"
        rect_image.save(input_path, "JPEG")

        # Act: Resize photo
        output_path = resize_photo(input_path, target_size=400)

        # Assert: Result should be square
        resized_image = Image.open(output_path)
        assert resized_image.size == (400, 400)

    def test_resize_maintains_image_quality(self, tmp_path):
        """Verify that resize maintains good image quality."""
        # Arrange: Create detailed image
        image = Image.new("RGB", (1000, 1000), color="yellow")
        input_path = tmp_path / "quality.jpg"
        image.save(input_path, "JPEG", quality=95)

        # Act: Resize
        output_path = resize_photo(input_path, target_size=400)

        # Assert: Output should exist and be readable
        resized_image = Image.open(output_path)
        assert resized_image.format == "JPEG"
        assert resized_image.size == (400, 400)

    def test_resize_converts_rgba_to_rgb(self, tmp_path):
        """Verify that RGBA images (PNG with alpha) are converted to RGB."""
        # Arrange: Create RGBA image
        rgba_image = Image.new("RGBA", (500, 500), color=(255, 0, 0, 128))
        input_path = tmp_path / "alpha.png"
        rgba_image.save(input_path, "PNG")

        # Act: Resize
        output_path = resize_photo(input_path, target_size=400)

        # Assert: Output should be RGB JPEG
        resized_image = Image.open(output_path)
        assert resized_image.mode == "RGB"
        assert resized_image.size == (400, 400)


@pytest.mark.unit
class TestPhotoMimeTypeValidation:
    """T108: Unit test for photo MIME type validation."""

    def test_validate_jpeg_photo(self):
        """Verify that JPEG photos pass validation."""
        # Arrange: Create JPEG image bytes
        image = Image.new("RGB", (100, 100), color="red")
        photo_bytes = BytesIO()
        image.save(photo_bytes, format="JPEG")
        photo_bytes.seek(0)

        # Act & Assert: Should not raise
        result = validate_photo(photo_bytes, "image/jpeg")
        assert result is True

    def test_validate_png_photo(self):
        """Verify that PNG photos pass validation."""
        # Arrange: Create PNG image bytes
        image = Image.new("RGB", (100, 100), color="blue")
        photo_bytes = BytesIO()
        image.save(photo_bytes, format="PNG")
        photo_bytes.seek(0)

        # Act & Assert: Should not raise
        result = validate_photo(photo_bytes, "image/png")
        assert result is True

    def test_validate_webp_photo(self):
        """Verify that WebP photos pass validation."""
        # Arrange: Create WebP image bytes
        image = Image.new("RGB", (100, 100), color="green")
        photo_bytes = BytesIO()
        image.save(photo_bytes, format="WEBP")
        photo_bytes.seek(0)

        # Act & Assert: Should not raise
        result = validate_photo(photo_bytes, "image/webp")
        assert result is True

    def test_reject_text_file(self):
        """Verify that text files are rejected."""
        # Arrange: Create text file
        text_bytes = BytesIO(b"This is not an image")

        # Act & Assert: Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            validate_photo(text_bytes, "text/plain")

        assert "formato" in str(exc_info.value).lower() or "mime" in str(exc_info.value).lower()

    def test_reject_svg(self):
        """Verify that SVG files are rejected (not raster images)."""
        # Arrange: SVG content
        svg_bytes = BytesIO(b'<svg><circle r="10"/></svg>')

        # Act & Assert: Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            validate_photo(svg_bytes, "image/svg+xml")

        assert "formato" in str(exc_info.value).lower()

    def test_reject_gif(self):
        """Verify that GIF files are rejected (only JPEG, PNG, WebP allowed)."""
        # Arrange: Create GIF
        image = Image.new("RGB", (100, 100), color="yellow")
        gif_bytes = BytesIO()
        image.save(gif_bytes, format="GIF")
        gif_bytes.seek(0)

        # Act & Assert: Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            validate_photo(gif_bytes, "image/gif")

        assert "formato" in str(exc_info.value).lower()


@pytest.mark.unit
class TestPhotoSizeLimitValidation:
    """T109: Unit test for photo size limit (5MB) validation."""

    def test_validate_photo_under_5mb(self):
        """Verify that photos under 5MB pass validation."""
        # Arrange: Create 1MB file
        small_bytes = BytesIO(b"x" * (1 * 1024 * 1024))

        # Act & Assert: Should not raise
        result = validate_photo(small_bytes, "image/jpeg", max_size_mb=5)
        assert result is True

    def test_validate_photo_exactly_5mb(self):
        """Verify that photos exactly 5MB pass validation."""
        # Arrange: Create exactly 5MB file
        exact_bytes = BytesIO(b"x" * (5 * 1024 * 1024))

        # Act & Assert: Should not raise
        result = validate_photo(exact_bytes, "image/jpeg", max_size_mb=5)
        assert result is True

    def test_reject_photo_over_5mb(self):
        """Verify that photos over 5MB are rejected."""
        # Arrange: Create 6MB file
        large_bytes = BytesIO(b"x" * (6 * 1024 * 1024))

        # Act & Assert: Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            validate_photo(large_bytes, "image/jpeg", max_size_mb=5)

        assert "5mb" in str(exc_info.value).lower() or "tamaño" in str(exc_info.value).lower()

    def test_validate_empty_file_rejected(self):
        """Verify that empty files are rejected."""
        # Arrange: Empty file
        empty_bytes = BytesIO(b"")

        # Act & Assert: Should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            validate_photo(empty_bytes, "image/jpeg")

        assert "vacío" in str(exc_info.value).lower() or "tamaño" in str(exc_info.value).lower()


@pytest.mark.unit
class TestPhotoFilenameGeneration:
    """Test filename generation for photos."""

    def test_generate_unique_filenames(self):
        """Verify that generated filenames are unique."""
        # Act: Generate multiple filenames
        filename1 = generate_photo_filename("user123", "jpg")
        filename2 = generate_photo_filename("user123", "jpg")
        filename3 = generate_photo_filename("user123", "png")

        # Assert: All should be different
        assert filename1 != filename2
        assert filename2 != filename3
        assert filename1 != filename3

    def test_filename_includes_user_id(self):
        """Verify that filename includes user ID."""
        # Act
        filename = generate_photo_filename("user456", "jpg")

        # Assert
        assert "user456" in filename

    def test_filename_has_correct_extension(self):
        """Verify that filename has correct extension."""
        # Act
        jpg_filename = generate_photo_filename("user789", "jpg")
        png_filename = generate_photo_filename("user789", "png")

        # Assert
        assert jpg_filename.endswith(".jpg")
        assert png_filename.endswith(".png")

    def test_filename_is_filesystem_safe(self):
        """Verify that filename doesn't contain unsafe characters."""
        # Act
        filename = generate_photo_filename("user_with/special\\chars", "jpg")

        # Assert: Should not contain / or \
        assert "/" not in filename
        assert "\\" not in filename
        assert ".." not in filename
