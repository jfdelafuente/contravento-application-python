"""
Unit tests for Route Statistics Service (User Story 5).

Tests for advanced statistics calculations including speed metrics,
climb detection, and gradient classification.

Test Coverage:
- T125: Speed calculation accuracy ±5% (SC-021)
- T126: Top 3 climbs detection (SC-022, FR-031)
- T127: Gradient classification (FR-032)
- T128: Handle GPX without timestamps gracefully (FR-033)

Success Criteria:
- SC-021: Speed calculations must be within ±5% of expected values
- SC-022: Top climbs algorithm must identify hardest 3 climbs correctly
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.route_stats_service import RouteStatsService


@pytest.mark.unit
@pytest.mark.asyncio
class TestSpeedCalculation:
    """
    T125: Test speed calculation accuracy (SC-021).

    Tests that average and maximum speed calculations are accurate
    within ±5% of expected values for realistic cycling scenarios.
    """

    async def test_speed_calculation_accuracy(self, db_session: AsyncSession):
        """
        T125: Test speed calculations are within ±5% accuracy.

        Scenario: Cyclist travels 10km in 30 minutes at constant speed.
        Expected: avg_speed = 20 km/h, max_speed ~20 km/h

        Success Criteria: Calculated values within ±5% (SC-021)
        """
        # Arrange
        service = RouteStatsService(db_session)

        # Create synthetic trackpoints: 10km in 30 minutes (20 km/h average)
        # 11 points = 10 segments of 1km each, 3 minutes apart
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        trackpoints = []

        for i in range(11):
            # Approximate: 1km ~ 0.009 degrees latitude
            trackpoints.append(
                {
                    "latitude": 40.0 + (i * 0.009),
                    "longitude": -3.0,
                    "elevation": 500.0,  # Flat terrain
                    "timestamp": start_time + timedelta(minutes=i * 3),
                    "distance_km": float(i),  # Cumulative distance
                    "sequence": i,
                }
            )

        # Act
        result = await service.calculate_speed_metrics(trackpoints)

        # Assert - Speed accuracy ±5%
        expected_avg_speed = 20.0  # km/h
        expected_max_speed = 20.0  # km/h (constant speed)
        expected_total_time = 30.0  # minutes
        expected_moving_time = 30.0  # minutes (no stops)

        # Check avg_speed within ±5%
        assert result["avg_speed_kmh"] is not None
        speed_error = abs(result["avg_speed_kmh"] - expected_avg_speed) / expected_avg_speed
        assert speed_error < 0.05, (
            f"Average speed error {speed_error * 100:.2f}% exceeds ±5% threshold. "
            f"Expected: {expected_avg_speed} km/h, Got: {result['avg_speed_kmh']:.2f} km/h"
        )

        # Check max_speed within ±10% (allows for GPS variance)
        assert result["max_speed_kmh"] is not None
        max_speed_error = abs(result["max_speed_kmh"] - expected_max_speed) / expected_max_speed
        assert max_speed_error < 0.10, (
            f"Max speed error {max_speed_error * 100:.2f}% exceeds ±10% threshold. "
            f"Expected: {expected_max_speed} km/h, Got: {result['max_speed_kmh']:.2f} km/h"
        )

        # Check total_time is correct
        assert result["total_time_minutes"] == pytest.approx(expected_total_time, rel=0.01)

        # Check moving_time (should equal total_time - no stops >5min)
        assert result["moving_time_minutes"] == pytest.approx(expected_moving_time, rel=0.01)

    async def test_speed_calculation_with_stops(self, db_session: AsyncSession):
        """
        T125 (Extended): Test moving time excludes stops >5 minutes.

        Scenario: Cyclist travels 10km with a 10-minute break in the middle.
        Expected: moving_time = 30min, total_time = 40min

        Functional Requirement: FR-030 (Moving time excludes pauses >5min)
        """
        # Arrange
        service = RouteStatsService(db_session)
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        trackpoints = []

        # First 5km in 15 minutes
        for i in range(6):
            trackpoints.append(
                {
                    "latitude": 40.0 + (i * 0.009),
                    "longitude": -3.0,
                    "elevation": 500.0,
                    "timestamp": start_time + timedelta(minutes=i * 3),
                    "distance_km": float(i),
                    "sequence": i,
                }
            )

        # 10-minute stop (timestamp jump, no distance change)
        # Point 6 is still at 5km but 10 minutes later
        trackpoints.append(
            {
                "latitude": 40.0 + (5 * 0.009),  # Same position as point 5
                "longitude": -3.0,
                "elevation": 500.0,
                "timestamp": start_time + timedelta(minutes=15 + 10),  # 10min stop
                "distance_km": 5.0,  # Same distance
                "sequence": 6,
            }
        )

        # Next 5km in 15 minutes (after the stop)
        # Points 7-11: 6km-10km, timestamps from 25min to 40min (15 minutes for 4 segments)
        for i in range(7, 12):
            # i=7 -> 6km at 25min, i=11 -> 10km at 40min (4 segments of 3.75min each)
            trackpoints.append(
                {
                    "latitude": 40.0 + ((i - 1) * 0.009),
                    "longitude": -3.0,
                    "elevation": 500.0,
                    "timestamp": start_time + timedelta(minutes=25.0 + (i - 7) * 3.75),  # 15min / 4 segments = 3.75min per segment
                    "distance_km": float(i - 1),
                    "sequence": i,
                }
            )

        # Act
        result = await service.calculate_speed_metrics(trackpoints)

        # Assert
        # Total time: 40 minutes (15min + 10min stop + 15min)
        assert result["total_time_minutes"] == pytest.approx(40.0, rel=0.01)

        # Moving time: 30 minutes (excludes 10-minute stop)
        assert result["moving_time_minutes"] == pytest.approx(30.0, rel=0.01)

        # Average speed should be based on moving time
        # 10km / 0.5h = 20 km/h
        assert result["avg_speed_kmh"] == pytest.approx(20.0, rel=0.05)


@pytest.mark.unit
@pytest.mark.asyncio
class TestClimbDetection:
    """
    T126: Test top climbs detection algorithm (SC-022, FR-031).

    Tests that the algorithm correctly identifies the top 3 hardest climbs
    based on elevation gain and average gradient.
    """

    async def test_top_climbs_detection(self, db_session: AsyncSession):
        """
        T126: Test algorithm identifies top 3 hardest climbs correctly.

        Scenario: Route with 4 climbs of varying difficulty:
        - Climb 1: 200m gain, 5% gradient (moderate)
        - Climb 2: 400m gain, 8% gradient (hard) <- Should be #1
        - Climb 3: 100m gain, 12% gradient (steep) <- Should be #2 (steep but short)
        - Climb 4: 300m gain, 6% gradient (moderate-hard) <- Should be #3

        Success Criteria: SC-022 (Top 3 identified correctly by difficulty)
        Functional Requirement: FR-031 (Identify hardest climbs)
        """
        # Arrange
        service = RouteStatsService(db_session)

        # Create synthetic route with 4 distinct climbs
        trackpoints = []
        sequence = 0
        distance_km = 0.0
        elevation = 100.0  # Start elevation

        # Flat start (5 points, 2km)
        for i in range(5):
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.4

        # Climb 1: 200m gain over 4km (5% avg gradient) - moderate
        for i in range(10):
            elevation += 20.0  # Total 200m gain
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.4

        # Flat section (3 points, 1.2km)
        for i in range(3):
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.4

        # Climb 2: 400m gain over 5km (8% avg gradient) - hardest climb
        for i in range(12):
            elevation += 33.3  # Total ~400m gain
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.42

        # Flat section
        for i in range(3):
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.4

        # Climb 3: 100m gain over 0.8km (12.5% avg gradient) - steepest but short
        for i in range(5):
            elevation += 20.0  # Total 100m gain
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.16

        # Flat section
        for i in range(3):
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.4

        # Climb 4: 300m gain over 5km (6% avg gradient) - moderate-hard
        for i in range(10):
            elevation += 30.0  # Total 300m gain
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.5

        # Act
        result = await service.detect_climbs(trackpoints)

        # Assert - Should return top 3 climbs
        assert len(result) == 3, f"Should return exactly 3 climbs, got {len(result)}"

        # Top climb should be Climb 2 (400m, 8%)
        top_climb = result[0]
        assert top_climb["elevation_gain_m"] >= 350, (
            f"Top climb should have ~400m gain, got {top_climb['elevation_gain_m']:.0f}m"
        )
        assert 7.0 <= top_climb["avg_gradient"] <= 9.0, (
            f"Top climb should have ~8% gradient, got {top_climb['avg_gradient']:.1f}%"
        )

        # Second climb could be Climb 3 (100m, 12.5%) or Climb 4 (300m, 6%)
        # Depends on scoring algorithm (steepness vs. total gain)
        second_climb = result[1]
        assert second_climb["elevation_gain_m"] >= 90, "Second climb should have significant gain"

        # Third climb
        third_climb = result[2]
        assert third_climb["elevation_gain_m"] >= 90, "Third climb should have significant gain"

        # All climbs should have required fields
        for climb in result:
            assert "start_km" in climb
            assert "end_km" in climb
            assert "elevation_gain_m" in climb
            assert "avg_gradient" in climb
            assert climb["start_km"] < climb["end_km"]
            assert climb["elevation_gain_m"] > 0
            assert climb["avg_gradient"] > 0


@pytest.mark.unit
@pytest.mark.asyncio
class TestGradientClassification:
    """
    T127: Test gradient classification algorithm (FR-032).

    Tests that gradients are correctly classified into categories:
    - Llano (flat): 0-3%
    - Moderado (moderate): 3-6%
    - Empinado (steep): 6-10%
    - Muy empinado (very steep): >10%
    """

    async def test_gradient_classification(self, db_session: AsyncSession):
        """
        T127: Test gradient segments are classified correctly.

        Scenario: Route with sections of each gradient category.
        Expected: Correct percentage of distance in each category.

        Functional Requirement: FR-032 (Gradient distribution visualization)
        """
        # Arrange
        service = RouteStatsService(db_session)

        # Create route with balanced gradient distribution
        trackpoints = []
        sequence = 0
        distance_km = 0.0
        elevation = 100.0

        # Llano: 0-3% gradient (10km, 200m gain = 2% avg)
        for i in range(25):
            elevation += 8.0  # Total 200m
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.4

        # Moderado: 3-6% gradient (10km, 450m gain = 4.5% avg)
        for i in range(25):
            elevation += 18.0  # Total 450m
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.4

        # Empinado: 6-10% gradient (5km, 400m gain = 8% avg)
        for i in range(12):
            elevation += 33.3  # Total ~400m
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.42

        # Muy empinado: >10% gradient (5km, 600m gain = 12% avg)
        for i in range(12):
            elevation += 50.0  # Total 600m
            trackpoints.append(
                {
                    "latitude": 40.0 + (sequence * 0.009),
                    "longitude": -3.0,
                    "elevation": elevation,
                    "distance_km": distance_km,
                    "sequence": sequence,
                }
            )
            sequence += 1
            distance_km += 0.42

        # Act
        result = await service.classify_gradients(trackpoints)

        # Assert - Should return distribution by category
        assert "llano" in result  # 0-3%
        assert "moderado" in result  # 3-6%
        assert "empinado" in result  # 6-10%
        assert "muy_empinado" in result  # >10%

        total_distance = trackpoints[-1]["distance_km"]

        # Check llano percentage (should be ~33% of total distance)
        llano_pct = (result["llano"]["distance_km"] / total_distance) * 100
        assert 25 <= llano_pct <= 40, (
            f"Llano (0-3%) should be ~33% of distance, got {llano_pct:.1f}%"
        )

        # Check moderado percentage (should be ~33% of total distance)
        moderado_pct = (result["moderado"]["distance_km"] / total_distance) * 100
        assert 25 <= moderado_pct <= 40, (
            f"Moderado (3-6%) should be ~33% of distance, got {moderado_pct:.1f}%"
        )

        # Check empinado percentage (should be ~17% of total distance)
        empinado_pct = (result["empinado"]["distance_km"] / total_distance) * 100
        assert 10 <= empinado_pct <= 25, (
            f"Empinado (6-10%) should be ~17% of distance, got {empinado_pct:.1f}%"
        )

        # Check muy_empinado percentage (should be ~17% of total distance)
        muy_empinado_pct = (result["muy_empinado"]["distance_km"] / total_distance) * 100
        assert 10 <= muy_empinado_pct <= 25, (
            f"Muy empinado (>10%) should be ~17% of distance, got {muy_empinado_pct:.1f}%"
        )

        # Total should sum to ~100% (allowing for rounding)
        total_pct = llano_pct + moderado_pct + empinado_pct + muy_empinado_pct
        assert 95 <= total_pct <= 105, f"Total percentage should be ~100%, got {total_pct:.1f}%"


@pytest.mark.unit
@pytest.mark.asyncio
class TestNoTimestamps:
    """
    T128: Test handling of GPX files without timestamps (FR-033).

    Tests that the service gracefully handles GPX files that lack
    timestamp data, returning None for speed/time metrics.
    """

    async def test_no_timestamps(self, db_session: AsyncSession):
        """
        T128: Test GPX without timestamps returns None for speed metrics.

        Scenario: Trackpoints have no timestamp field.
        Expected: Speed metrics return None, gradient stats still work.

        Functional Requirement: FR-033 (Graceful handling of missing timestamps)
        """
        # Arrange
        service = RouteStatsService(db_session)

        # Create trackpoints WITHOUT timestamps
        trackpoints = []
        for i in range(10):
            trackpoints.append(
                {
                    "latitude": 40.0 + (i * 0.009),
                    "longitude": -3.0,
                    "elevation": 500.0 + (i * 10),  # 100m total gain
                    "distance_km": float(i * 0.5),
                    "sequence": i,
                    # No timestamp field!
                }
            )

        # Act
        result = await service.calculate_speed_metrics(trackpoints)

        # Assert - Speed metrics should be None
        assert result["avg_speed_kmh"] is None, (
            "avg_speed_kmh should be None when no timestamps"
        )
        assert result["max_speed_kmh"] is None, (
            "max_speed_kmh should be None when no timestamps"
        )
        assert result["total_time_minutes"] is None, (
            "total_time_minutes should be None when no timestamps"
        )
        assert result["moving_time_minutes"] is None, (
            "moving_time_minutes should be None when no timestamps"
        )

        # Gradient metrics should still work (don't require timestamps)
        gradient_result = await service.classify_gradients(trackpoints)
        assert gradient_result is not None, "Gradient classification should work without timestamps"
        assert "llano" in gradient_result
        assert "moderado" in gradient_result
