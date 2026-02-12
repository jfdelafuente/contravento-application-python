"""
Difficulty calculator service for GPS Trip Creation Wizard.

Feature: 017-gps-trip-wizard
Business Logic: Auto-calculate trip difficulty from GPX telemetry
Functional Requirements: FR-003

This service implements the difficulty calculation algorithm specified in
specs/017-gps-trip-wizard/data-model.md (lines 325-356).
"""

import logging

from src.models.trip import TripDifficulty

logger = logging.getLogger(__name__)


class DifficultyCalculator:
    """
    Service for calculating trip difficulty from telemetry data.

    Difficulty is calculated automatically from:
    - Distance (km)
    - Elevation gain (m)

    The algorithm uses whichever metric is higher (distance OR elevation).
    """

    @staticmethod
    def calculate(distance_km: float, elevation_gain: float | None) -> TripDifficulty:
        """
        Calculate trip difficulty from GPX telemetry.

        Uses a threshold-based algorithm where either distance OR elevation
        can trigger a higher difficulty level (whichever metric is greater).

        Algorithm (from spec assumption #1):
        - EASY: <30km and <500m elevation gain
        - MODERATE: 30-60km or 500-1000m gain
        - DIFFICULT: 60-100km or 1000-1500m gain
        - VERY_DIFFICULT: 100-150km or 1500-2500m gain
        - EXTREME: ≥150km or ≥2500m gain

        Args:
            distance_km: Total route distance in kilometers
            elevation_gain: Cumulative uphill elevation in meters (None if no elevation data)

        Returns:
            TripDifficulty enum value (EASY, MODERATE, DIFFICULT, VERY_DIFFICULT, EXTREME)

        Examples:
            >>> DifficultyCalculator.calculate(40.0, 1200.0)
            TripDifficulty.DIFFICULT  # Elevation dominates

            >>> DifficultyCalculator.calculate(120.0, 800.0)
            TripDifficulty.VERY_DIFFICULT  # Distance dominates

            >>> DifficultyCalculator.calculate(180.0, 3000.0)
            TripDifficulty.EXTREME  # Both metrics exceed thresholds

            >>> DifficultyCalculator.calculate(25.0, None)
            TripDifficulty.EASY  # No elevation data, distance-only
        """
        # Sanitize inputs: treat negative values as zero (data quality issue)
        distance_km = max(0.0, float(distance_km))
        if elevation_gain is not None:
            elevation_gain = max(0.0, float(elevation_gain))

        # EXTREME: ≥150km or ≥2500m gain
        if distance_km >= 150 or (elevation_gain is not None and elevation_gain >= 2500):
            return TripDifficulty.EXTREME

        # VERY_DIFFICULT: ≥100km or ≥1500m gain (and not extreme)
        if distance_km >= 100 or (elevation_gain is not None and elevation_gain >= 1500):
            return TripDifficulty.VERY_DIFFICULT

        # DIFFICULT: ≥60km or ≥1000m gain (and not very difficult)
        if distance_km >= 60 or (elevation_gain is not None and elevation_gain >= 1000):
            return TripDifficulty.DIFFICULT

        # MODERATE: ≥30km or ≥500m gain (and not difficult)
        if distance_km >= 30 or (elevation_gain is not None and elevation_gain >= 500):
            return TripDifficulty.MODERATE

        # EASY: <30km and <500m gain (default)
        return TripDifficulty.EASY

    @staticmethod
    def get_difficulty_label(difficulty: TripDifficulty) -> str:
        """
        Get Spanish display label for difficulty level.

        Args:
            difficulty: TripDifficulty enum value

        Returns:
            Spanish label for display (e.g., "Fácil", "Extrema")

        Examples:
            >>> DifficultyCalculator.get_difficulty_label(TripDifficulty.EASY)
            "Fácil"

            >>> DifficultyCalculator.get_difficulty_label(TripDifficulty.EXTREME)
            "Extrema"
        """
        labels = {
            TripDifficulty.EASY: "Fácil",
            TripDifficulty.MODERATE: "Moderada",
            TripDifficulty.DIFFICULT: "Difícil",
            TripDifficulty.VERY_DIFFICULT: "Muy Difícil",
            TripDifficulty.EXTREME: "Extrema",
        }
        return labels.get(difficulty, "Desconocida")

    @staticmethod
    def get_difficulty_description(difficulty: TripDifficulty) -> str:
        """
        Get detailed description of difficulty level requirements.

        Args:
            difficulty: TripDifficulty enum value

        Returns:
            Spanish description explaining the thresholds

        Examples:
            >>> DifficultyCalculator.get_difficulty_description(TripDifficulty.MODERATE)
            "Entre 30-60 km o 500-1000 m de desnivel positivo"
        """
        descriptions = {
            TripDifficulty.EASY: "Menos de 30 km y menos de 500 m de desnivel positivo",
            TripDifficulty.MODERATE: "Entre 30-60 km o 500-1000 m de desnivel positivo",
            TripDifficulty.DIFFICULT: "Entre 60-100 km o 1000-1500 m de desnivel positivo",
            TripDifficulty.VERY_DIFFICULT: "Entre 100-150 km o 1500-2500 m de desnivel positivo",
            TripDifficulty.EXTREME: "Más de 150 km o más de 2500 m de desnivel positivo",
        }
        return descriptions.get(difficulty, "Descripción no disponible")
