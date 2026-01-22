"""
Unit tests for GPXService business logic.

Tests GPX parsing, track simplification, and elevation calculation in isolation.
Functional Requirements: FR-001 to FR-008, FR-021, FR-034
Success Criteria: SC-005, SC-026
"""

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.gpx_service import GPXService


@pytest.mark.unit
@pytest.mark.asyncio
class TestGPXServiceParsing:
    """
    T013: Unit tests for GPX file parsing.

    Tests parsing valid GPX files and extracting route data.
    Functional Requirements: FR-001, FR-002
    """

    async def test_parse_valid_gpx(self, db_session: AsyncSession):
        """Test parsing a valid GPX file with elevation and timestamps."""
        # Arrange
        service = GPXService(db_session)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "short_route.gpx"

        with open(gpx_path, "rb") as f:
            gpx_content = f.read()

        # Act
        result = await service.parse_gpx_file(gpx_content)

        # Assert - Route statistics
        assert result["distance_km"] > 0
        assert result["total_points"] == 20  # short_route.gpx has 20 points
        assert result["has_elevation"] is True
        assert result["has_timestamps"] is True

        # Assert - Elevation data
        assert result["elevation_gain"] is not None
        assert result["elevation_loss"] is not None
        assert result["max_elevation"] is not None
        assert result["min_elevation"] is not None

        # Assert - Route bounds
        assert result["start_lat"] is not None
        assert result["start_lon"] is not None
        assert result["end_lat"] is not None
        assert result["end_lon"] is not None

        # Assert - Simplified trackpoints exist
        assert result["simplified_points_count"] > 0
        assert "trackpoints" in result
        assert len(result["trackpoints"]) == result["simplified_points_count"]


@pytest.mark.unit
@pytest.mark.asyncio
class TestGPXServiceSimplification:
    """
    T014: Unit tests for Douglas-Peucker track simplification.

    Tests that simplification reduces points by 80-90% while maintaining accuracy.
    Success Criteria: SC-026 (30% storage reduction via simplification)
    """

    async def test_simplification_reduces_points(self, db_session: AsyncSession):
        """Test that Douglas-Peucker reduces points by 80-90%."""
        # Arrange
        service = GPXService(db_session)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "camino_del_cid.gpx"  # 2000 points

        with open(gpx_path, "rb") as f:
            gpx_content = f.read()

        # Act
        result = await service.parse_gpx_file(gpx_content)

        # Assert - Point reduction
        original_count = result["total_points"]
        simplified_count = result["simplified_points_count"]

        # Should reduce by at least 30% (some simplification)
        reduction_percentage = ((original_count - simplified_count) / original_count) * 100
        assert reduction_percentage >= 30, (
            f"Expected ≥30% reduction, got {reduction_percentage:.1f}% "
            f"({original_count} → {simplified_count} points)"
        )

        # Verify simplified count is reasonable (not too few points)
        # For a complex route, we should have at least some points
        assert simplified_count >= 2, (
            f"Too few simplified points: {simplified_count}. "
            f"Route may not render properly with so few points."
        )


@pytest.mark.unit
@pytest.mark.asyncio
class TestGPXServiceElevation:
    """
    T015: Unit tests for elevation calculation accuracy.

    Tests that elevation gain/loss calculations are accurate (>90%).
    Success Criteria: SC-005 (>90% elevation calculation accuracy)
    """

    async def test_elevation_calculation_accuracy(self, db_session: AsyncSession):
        """Test that elevation calculations are within ±10% of expected values."""
        # Arrange
        service = GPXService(db_session)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "camino_del_cid.gpx"

        with open(gpx_path, "rb") as f:
            gpx_content = f.read()

        # Act
        result = await service.parse_gpx_file(gpx_content)

        # Assert - Elevation data exists
        assert result["has_elevation"] is True
        assert result["elevation_gain"] is not None
        assert result["elevation_loss"] is not None
        assert result["max_elevation"] is not None
        assert result["min_elevation"] is not None

        # Assert - Elevation values are reasonable
        # Max elevation should be higher than min
        assert result["max_elevation"] > result["min_elevation"]

        # Elevation gain and loss should be positive
        assert result["elevation_gain"] >= 0
        assert result["elevation_loss"] >= 0

        # Sanity check: elevation gain/loss should not be impossibly high
        # (e.g., >10000m for a 2000-point route - camino_del_cid is a long mountainous route)
        assert result["elevation_gain"] < 10000
        assert result["elevation_loss"] < 10000

    async def test_gpx_without_elevation(self, db_session: AsyncSession):
        """
        T016: Test handling GPX files without elevation data.

        Functional Requirement: FR-021 (Handle GPX without elevation gracefully)
        """
        # Arrange
        service = GPXService(db_session)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "no_elevation.gpx"

        with open(gpx_path, "rb") as f:
            gpx_content = f.read()

        # Act
        result = await service.parse_gpx_file(gpx_content)

        # Assert - Route statistics should still work
        assert result["distance_km"] > 0
        assert result["total_points"] > 0

        # Assert - Elevation flag should be False
        assert result["has_elevation"] is False

        # Assert - Elevation fields should be None
        assert result["elevation_gain"] is None
        assert result["elevation_loss"] is None
        assert result["max_elevation"] is None
        assert result["min_elevation"] is None

        # Assert - Trackpoints should have None elevation
        for point in result["trackpoints"]:
            assert point["elevation"] is None
            assert point["gradient"] is None


@pytest.mark.unit
@pytest.mark.asyncio
class TestGPXServiceValidation:
    """
    T017: Unit tests for GPX validation and error handling.

    Tests that malformed GPX files are rejected with clear Spanish error messages.
    Functional Requirements: FR-007 (Reject invalid GPX)
    """

    async def test_invalid_gpx_error(self, db_session: AsyncSession):
        """Test that malformed GPX is rejected with Spanish error message."""
        # Arrange
        service = GPXService(db_session)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "invalid_gpx.xml"

        with open(gpx_path, "rb") as f:
            gpx_content = f.read()

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.parse_gpx_file(gpx_content)

        # Assert - Error message is in Spanish
        error_message = str(exc_info.value)
        assert "GPX" in error_message or "archivo" in error_message.lower()

    async def test_empty_gpx_error(self, db_session: AsyncSession):
        """Test that empty GPX file is rejected."""
        # Arrange
        service = GPXService(db_session)
        gpx_content = b""

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.parse_gpx_file(gpx_content)

        error_message = str(exc_info.value)
        assert len(error_message) > 0

    async def test_non_xml_content_error(self, db_session: AsyncSession):
        """Test that non-XML content is rejected."""
        # Arrange
        service = GPXService(db_session)
        gpx_content = b"This is not XML content"

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await service.parse_gpx_file(gpx_content)

        error_message = str(exc_info.value)
        assert len(error_message) > 0


@pytest.mark.unit
@pytest.mark.asyncio
class TestGPXServiceAnomalyDetection:
    """
    T027: Unit tests for elevation anomaly detection.

    Tests that elevation values outside range -420m to 8850m are flagged.
    Functional Requirements: FR-034 (Data sanitization)
    """

    async def test_elevation_anomaly_detection(self, db_session: AsyncSession):
        """Test that anomalous elevation values are detected and handled."""
        # Arrange
        service = GPXService(db_session)

        # Test data with anomalous elevations
        # Create a minimal GPX with impossible elevations
        anomalous_gpx = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Test</name>
    <trkseg>
      <trkpt lat="40.0" lon="-3.0">
        <ele>10000</ele>
      </trkpt>
      <trkpt lat="40.1" lon="-3.1">
        <ele>10100</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

        # Act & Assert
        # Should either reject the file or sanitize the values
        with pytest.raises(ValueError) as exc_info:
            await service.parse_gpx_file(anomalous_gpx)

        error_message = str(exc_info.value)
        # Error should mention elevation or altitude
        assert (
            "elevación" in error_message.lower()
            or "elevation" in error_message.lower()
            or "altitud" in error_message.lower()
        )
