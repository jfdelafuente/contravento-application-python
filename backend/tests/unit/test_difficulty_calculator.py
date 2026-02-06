"""
Unit tests for DifficultyCalculator service.

Feature: 017-gps-trip-wizard
Tests: Difficulty calculation algorithm (FR-003)

TDD Approach: These tests are written BEFORE implementation (RED phase).
"""

import pytest

from src.models.trip import TripDifficulty
from src.services.difficulty_calculator import DifficultyCalculator


class TestDifficultyCalculation:
    """Test difficulty calculation from distance and elevation gain."""

    @pytest.mark.parametrize(
        "distance_km,elevation_gain,expected,description",
        [
            # EASY: <30km and <500m elevation gain
            (20.0, 300.0, TripDifficulty.EASY, "Short route, low elevation"),
            (25.0, 450.0, TripDifficulty.EASY, "Boundary case for easy"),
            (29.9, 499.0, TripDifficulty.EASY, "Just below easy thresholds"),
            (15.0, None, TripDifficulty.EASY, "Short route, no elevation data"),
            # MODERATE: 30-60km or 500-1000m gain
            (30.0, 300.0, TripDifficulty.MODERATE, "Distance at moderate threshold"),
            (50.0, 800.0, TripDifficulty.MODERATE, "Mid-range moderate"),
            (25.0, 600.0, TripDifficulty.MODERATE, "Elevation dominates (moderate)"),
            (
                59.9,
                999.0,
                TripDifficulty.MODERATE,
                "Just below moderate upper bounds",
            ),
            (35.0, None, TripDifficulty.MODERATE, "Moderate distance, no elevation"),
            # DIFFICULT: 60-100km or 1000-1500m gain
            (60.0, 500.0, TripDifficulty.DIFFICULT, "Distance at difficult threshold"),
            (80.0, 1200.0, TripDifficulty.DIFFICULT, "Mid-range difficult"),
            (40.0, 1300.0, TripDifficulty.DIFFICULT, "Elevation dominates (difficult)"),
            (
                99.9,
                1499.0,
                TripDifficulty.DIFFICULT,
                "Just below difficult upper bounds",
            ),
            (75.0, None, TripDifficulty.DIFFICULT, "Difficult distance, no elevation"),
            # VERY_DIFFICULT: 100-150km or 1500-2500m gain
            (
                100.0,
                800.0,
                TripDifficulty.VERY_DIFFICULT,
                "Distance at very difficult threshold",
            ),
            (
                130.0,
                2000.0,
                TripDifficulty.VERY_DIFFICULT,
                "Mid-range very difficult",
            ),
            (
                80.0,
                1800.0,
                TripDifficulty.VERY_DIFFICULT,
                "Elevation dominates (very difficult)",
            ),
            (
                149.9,
                2499.0,
                TripDifficulty.VERY_DIFFICULT,
                "Just below extreme thresholds",
            ),
            (
                120.0,
                None,
                TripDifficulty.VERY_DIFFICULT,
                "Very difficult distance, no elevation",
            ),
            # EXTREME: >150km or >2500m gain
            (150.0, 1000.0, TripDifficulty.EXTREME, "Distance at extreme threshold"),
            (180.0, 3000.0, TripDifficulty.EXTREME, "Both metrics extreme"),
            (160.0, 800.0, TripDifficulty.EXTREME, "Distance dominates (extreme)"),
            (80.0, 2700.0, TripDifficulty.EXTREME, "Elevation dominates (extreme)"),
            (200.0, 500.0, TripDifficulty.EXTREME, "Very long distance"),
            (50.0, 3500.0, TripDifficulty.EXTREME, "Very high elevation gain"),
            (170.0, None, TripDifficulty.EXTREME, "Extreme distance, no elevation"),
        ],
    )
    def test_calculate_difficulty_all_cases(
        self,
        distance_km: float,
        elevation_gain: float | None,
        expected: TripDifficulty,
        description: str,
    ):
        """Test difficulty calculation covers all 5 levels with distance/elevation combinations."""
        result = DifficultyCalculator.calculate(distance_km, elevation_gain)
        assert result == expected, f"Failed: {description}"

    def test_calculate_difficulty_boundary_cases(self):
        """Test exact threshold boundaries."""
        # Exact thresholds should go to NEXT difficulty level
        assert DifficultyCalculator.calculate(30.0, 0.0) == TripDifficulty.MODERATE
        assert DifficultyCalculator.calculate(0.0, 500.0) == TripDifficulty.MODERATE
        assert DifficultyCalculator.calculate(60.0, 0.0) == TripDifficulty.DIFFICULT
        assert DifficultyCalculator.calculate(0.0, 1000.0) == TripDifficulty.DIFFICULT
        assert DifficultyCalculator.calculate(100.0, 0.0) == TripDifficulty.VERY_DIFFICULT
        assert DifficultyCalculator.calculate(0.0, 1500.0) == TripDifficulty.VERY_DIFFICULT
        assert DifficultyCalculator.calculate(150.0, 0.0) == TripDifficulty.EXTREME
        assert DifficultyCalculator.calculate(0.0, 2500.0) == TripDifficulty.EXTREME

    def test_calculate_difficulty_zero_values(self):
        """Test edge case: zero distance or elevation."""
        # Zero distance should be EASY
        assert DifficultyCalculator.calculate(0.0, 0.0) == TripDifficulty.EASY
        assert DifficultyCalculator.calculate(0.0, None) == TripDifficulty.EASY

        # Zero elevation with distance
        assert DifficultyCalculator.calculate(20.0, 0.0) == TripDifficulty.EASY
        assert DifficultyCalculator.calculate(40.0, 0.0) == TripDifficulty.MODERATE
        assert DifficultyCalculator.calculate(70.0, 0.0) == TripDifficulty.DIFFICULT

    def test_calculate_difficulty_no_elevation_data(self):
        """Test calculation when GPX has no elevation data (elevation_gain=None)."""
        # Should fall back to distance-only calculation
        assert DifficultyCalculator.calculate(10.0, None) == TripDifficulty.EASY
        assert DifficultyCalculator.calculate(45.0, None) == TripDifficulty.MODERATE
        assert DifficultyCalculator.calculate(85.0, None) == TripDifficulty.DIFFICULT
        assert DifficultyCalculator.calculate(125.0, None) == TripDifficulty.VERY_DIFFICULT
        assert DifficultyCalculator.calculate(175.0, None) == TripDifficulty.EXTREME

    def test_calculate_difficulty_invalid_inputs(self):
        """Test behavior with invalid/negative inputs."""
        # Negative values should be treated as zero (data quality issue)
        assert DifficultyCalculator.calculate(-10.0, 100.0) == TripDifficulty.EASY
        assert DifficultyCalculator.calculate(50.0, -200.0) == TripDifficulty.MODERATE

    def test_calculate_difficulty_type_validation(self):
        """Test that calculator handles various numeric types."""
        # Should work with int and float
        assert DifficultyCalculator.calculate(100, 1500) == TripDifficulty.VERY_DIFFICULT
        assert DifficultyCalculator.calculate(100.0, 1500.0) == TripDifficulty.VERY_DIFFICULT
        assert DifficultyCalculator.calculate(100, None) == TripDifficulty.VERY_DIFFICULT
