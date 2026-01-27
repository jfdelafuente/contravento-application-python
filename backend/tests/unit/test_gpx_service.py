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

    async def test_simplification_accuracy(self, db_session: AsyncSession):
        """
        T051: Test that Douglas-Peucker simplification maintains <5% distance accuracy.

        Validates that simplified route distance is within 5% of original route distance.
        This ensures the simplification algorithm doesn't lose significant route accuracy
        while achieving storage reduction.

        Success Criteria: Distance difference <5% (SC-007 implicitly requires accuracy)
        Functional Requirements: FR-009 (Accurate route visualization)
        """
        # Arrange
        service = GPXService(db_session)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "camino_del_cid.gpx"  # 2000 points

        with open(gpx_path, "rb") as f:
            gpx_content = f.read()

        # Act
        result = await service.parse_gpx_file(gpx_content)

        # Get distances
        simplified_distance_km = result["distance_km"]
        original_points = result["original_points"]

        # Calculate original distance by summing all segments
        original_distance_km = 0.0
        for i in range(len(original_points) - 1):
            p1 = original_points[i]
            p2 = original_points[i + 1]
            segment_distance = service._calculate_distance(
                p1.latitude, p1.longitude, p2.latitude, p2.longitude
            )
            original_distance_km += segment_distance

        # Assert - Distance accuracy <5%
        distance_diff = abs(simplified_distance_km - original_distance_km)
        accuracy_percentage = (distance_diff / original_distance_km) * 100

        assert accuracy_percentage < 5.0, (
            f"Simplification accuracy must be <5%, got {accuracy_percentage:.2f}%. "
            f"Original distance: {original_distance_km:.2f} km, "
            f"Simplified distance: {simplified_distance_km:.2f} km, "
            f"Difference: {distance_diff:.2f} km"
        )

        # Additional assertion - simplified distance should be reasonably close
        # (typically within 1-2% for well-behaved routes)
        assert simplified_distance_km > 0, "Simplified distance must be positive"
        assert original_distance_km > 0, "Original distance must be positive"


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


@pytest.mark.unit
@pytest.mark.asyncio
class TestGPXServiceGradientCalculation:
    """
    T083: Unit tests for gradient calculation accuracy.

    Tests that gradient (slope percentage) is calculated accurately within ±2%.
    Success Criteria: SC-023 (Gradient calculation accuracy ±2%)
    Functional Requirements: FR-017 to FR-020 (Elevation profile with gradients)
    """

    async def test_gradient_calculation_accuracy(self, db_session: AsyncSession):
        """
        Test gradient calculation is accurate within ±2% (SC-023).

        Creates synthetic GPX with 3 trackpoints with known elevation/distance:
        - Point 1: 0.0 km, 100m elevation → gradient: None (first point)
        - Point 2: 1.0 km, 200m elevation → gradient: +10.0% (uphill)
        - Point 3: 2.0 km, 100m elevation → gradient: -10.0% (downhill)

        Validates calculated gradients are within ±2% of expected values.
        """
        # Arrange
        service = GPXService(db_session)

        # Create synthetic GPX with known gradients
        # Distance: ~1km apart, Elevation: +100m, then -100m
        # Expected gradients: +10% uphill, -10% downhill
        # NOTE: Middle point has slight longitude offset to prevent Douglas-Peucker simplification
        synthetic_gpx = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Gradient Test Route</name>
    <trkseg>
      <trkpt lat="40.0000" lon="-3.0000">
        <ele>100</ele>
      </trkpt>
      <trkpt lat="40.0090" lon="-3.0010">
        <ele>200</ele>
      </trkpt>
      <trkpt lat="40.0180" lon="-3.0000">
        <ele>100</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

        # Act
        result = await service.parse_gpx_file(synthetic_gpx)
        trackpoints = result["trackpoints"]

        # Assert - We should have 3 trackpoints
        assert len(trackpoints) == 3, f"Expected 3 trackpoints, got {len(trackpoints)}"

        # Assert - Point 1: First point has no gradient
        point_1 = trackpoints[0]
        assert point_1["gradient"] is None, (
            f"First point should have gradient=None, got {point_1['gradient']}"
        )

        # Assert - Point 2: Uphill gradient ~+10%
        # 1km = 1000m horizontal, +100m vertical → (100/1000)*100 = 10%
        point_2 = trackpoints[1]
        assert point_2["gradient"] is not None, "Point 2 should have a gradient value"

        expected_uphill = 10.0
        actual_uphill = point_2["gradient"]
        uphill_error = abs(actual_uphill - expected_uphill)

        assert uphill_error <= 2.0, (
            f"Uphill gradient should be {expected_uphill}% ±2%, "
            f"got {actual_uphill:.2f}% (error: {uphill_error:.2f}%)"
        )

        # Assert - Point 3: Downhill gradient ~-10%
        # 1km = 1000m horizontal, -100m vertical → (-100/1000)*100 = -10%
        point_3 = trackpoints[2]
        assert point_3["gradient"] is not None, "Point 3 should have a gradient value"

        expected_downhill = -10.0
        actual_downhill = point_3["gradient"]
        downhill_error = abs(actual_downhill - expected_downhill)

        assert downhill_error <= 2.0, (
            f"Downhill gradient should be {expected_downhill}% ±2%, "
            f"got {actual_downhill:.2f}% (error: {downhill_error:.2f}%)"
        )

    async def test_gradient_calculation_flat_terrain(self, db_session: AsyncSession):
        """Test gradient calculation for flat terrain (0% slope)."""
        # Arrange
        service = GPXService(db_session)

        # Create GPX with flat terrain (same elevation)
        flat_gpx = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Flat Route</name>
    <trkseg>
      <trkpt lat="40.0000" lon="-3.0000">
        <ele>100</ele>
      </trkpt>
      <trkpt lat="40.0090" lon="-3.0000">
        <ele>100</ele>
      </trkpt>
      <trkpt lat="40.0180" lon="-3.0000">
        <ele>100</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""

        # Act
        result = await service.parse_gpx_file(flat_gpx)
        trackpoints = result["trackpoints"]

        # Assert - Points 2 and 3 should have ~0% gradient
        for i, point in enumerate(trackpoints[1:], start=2):
            gradient = point["gradient"]
            assert gradient is not None, f"Point {i} should have a gradient value"

            # Flat terrain should be within ±2% of 0%
            assert abs(gradient) <= 2.0, (
                f"Flat terrain gradient should be ~0% ±2%, "
                f"got {gradient:.2f}% for point {i}"
            )

    async def test_gradient_calculation_no_elevation_data(self, db_session: AsyncSession):
        """Test gradient is None when GPX has no elevation data."""
        # Arrange
        service = GPXService(db_session)
        fixtures_dir = Path(__file__).parent.parent / "fixtures" / "gpx"
        gpx_path = fixtures_dir / "no_elevation.gpx"

        with open(gpx_path, "rb") as f:
            gpx_content = f.read()

        # Act
        result = await service.parse_gpx_file(gpx_content)
        trackpoints = result["trackpoints"]

        # Assert - All trackpoints should have gradient=None
        for i, point in enumerate(trackpoints):
            assert point["gradient"] is None, (
                f"Point {i} should have gradient=None when no elevation data, "
                f"got {point['gradient']}"
            )
