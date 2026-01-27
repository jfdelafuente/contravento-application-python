"""
Route Statistics Service for User Story 5 - Advanced Statistics.

Calculates advanced route statistics from GPX files with timestamps:
- Speed metrics (average, maximum)
- Time analysis (total time, moving time)
- Gradient analysis (average, maximum)
- Top climbs detection (top 3 hardest climbs)
"""

import logging
from datetime import datetime
from typing import Any

import gpxpy.gpx

logger = logging.getLogger(__name__)

# Constants for calculations
MIN_SPEED_KMPH = 3.0  # Minimum speed to consider "moving" (vs stopped)
MAX_REALISTIC_SPEED_KMPH = 100.0  # Maximum realistic cycling speed (validation)


class RouteStatisticsService:
    """
    Service for calculating advanced route statistics from GPX data.

    Requirements:
    - GPX file must have timestamps (has_timestamps=True)
    - Calculates speed/time metrics from timestamp deltas
    - Detects top 3 hardest climbs based on elevation gain and gradient
    """

    @staticmethod
    def calculate_statistics(
        points: list[gpxpy.gpx.GPXTrackPoint],
    ) -> dict[str, Any] | None:
        """
        Calculate route statistics from GPX trackpoints with timestamps.

        Args:
            points: List of GPX trackpoints with timestamps and elevation data

        Returns:
            Dictionary with statistics:
            - avg_speed_kmh: Average speed in km/h
            - max_speed_kmh: Maximum speed in km/h
            - total_time_minutes: Total elapsed time in minutes
            - moving_time_minutes: Time in motion (excluding stops) in minutes
            - avg_gradient: Average gradient in percentage
            - max_gradient: Maximum gradient in percentage
            - top_climbs: List of top 3 climbs with details

            Returns None if insufficient data for calculation

        Raises:
            ValueError: If data is invalid or calculations fail
        """
        if not points or len(points) < 2:
            logger.warning("Insufficient trackpoints for statistics calculation")
            return None

        # Verify timestamps are present
        has_timestamps = any(p.time is not None for p in points[:100])
        if not has_timestamps:
            logger.warning("GPX file does not have timestamps - cannot calculate statistics")
            return None

        try:
            # Calculate speed and time metrics
            speed_stats = RouteStatisticsService._calculate_speed_metrics(points)

            # Calculate gradient metrics
            gradient_stats = RouteStatisticsService._calculate_gradient_metrics(points)

            # Detect top climbs
            top_climbs = RouteStatisticsService._detect_top_climbs(points)

            # Combine all statistics
            statistics = {
                **speed_stats,
                **gradient_stats,
                "top_climbs": top_climbs if top_climbs else None,
            }

            logger.info(
                f"Route statistics calculated: "
                f"avg_speed={statistics.get('avg_speed_kmh'):.1f} km/h, "
                f"max_speed={statistics.get('max_speed_kmh'):.1f} km/h, "
                f"climbs={len(top_climbs) if top_climbs else 0}"
            )

            return statistics

        except Exception as e:
            logger.error(f"Failed to calculate route statistics: {e}")
            raise ValueError(f"Error al calcular estadísticas de ruta: {str(e)}")

    @staticmethod
    def _calculate_speed_metrics(points: list[gpxpy.gpx.GPXTrackPoint]) -> dict[str, float]:
        """
        Calculate speed and time metrics from timestamped trackpoints.

        Args:
            points: List of GPX trackpoints with timestamps

        Returns:
            Dictionary with:
            - avg_speed_kmh: Average speed in km/h
            - max_speed_kmh: Maximum speed in km/h
            - total_time_minutes: Total elapsed time in minutes
            - moving_time_minutes: Time in motion (speed >= MIN_SPEED_KMPH) in minutes
        """
        total_distance_km = 0.0
        total_time_seconds = 0.0
        moving_time_seconds = 0.0
        max_speed_kmh = 0.0
        speed_sum_kmh = 0.0
        speed_count = 0

        for i in range(1, len(points)):
            prev_point = points[i - 1]
            curr_point = points[i]

            # Skip if timestamps missing
            if not prev_point.time or not curr_point.time:
                continue

            # Calculate time delta
            time_delta_seconds = (curr_point.time - prev_point.time).total_seconds()
            if time_delta_seconds <= 0:
                continue

            # Calculate distance (meters)
            distance_m = prev_point.distance_3d(curr_point) or 0.0

            # Calculate speed (km/h)
            speed_kmh = (distance_m / 1000) / (time_delta_seconds / 3600)

            # Validate speed (filter GPS errors)
            if speed_kmh > MAX_REALISTIC_SPEED_KMPH:
                logger.warning(
                    f"Unrealistic speed detected: {speed_kmh:.1f} km/h at point {i}, skipping"
                )
                continue

            # Accumulate metrics
            total_distance_km += distance_m / 1000
            total_time_seconds += time_delta_seconds

            # Update max speed
            if speed_kmh > max_speed_kmh:
                max_speed_kmh = speed_kmh

            # Accumulate moving time (speed >= MIN_SPEED_KMPH)
            if speed_kmh >= MIN_SPEED_KMPH:
                moving_time_seconds += time_delta_seconds
                speed_sum_kmh += speed_kmh
                speed_count += 1

        # Calculate averages
        avg_speed_kmh = speed_sum_kmh / speed_count if speed_count > 0 else 0.0
        total_time_minutes = total_time_seconds / 60
        moving_time_minutes = moving_time_seconds / 60

        return {
            "avg_speed_kmh": round(avg_speed_kmh, 1),
            "max_speed_kmh": round(max_speed_kmh, 1),
            "total_time_minutes": round(total_time_minutes, 1),
            "moving_time_minutes": round(moving_time_minutes, 1),
        }

    @staticmethod
    def _calculate_gradient_metrics(
        points: list[gpxpy.gpx.GPXTrackPoint],
    ) -> dict[str, float | None]:
        """
        Calculate gradient metrics from trackpoints with elevation data.

        Args:
            points: List of GPX trackpoints with elevation data

        Returns:
            Dictionary with:
            - avg_gradient: Average gradient in percentage (None if no elevation data)
            - max_gradient: Maximum gradient in percentage (None if no elevation data)
        """
        gradients = []

        for i in range(1, len(points)):
            prev_point = points[i - 1]
            curr_point = points[i]

            # Skip if elevation missing
            if prev_point.elevation is None or curr_point.elevation is None:
                continue

            # Calculate HORIZONTAL distance (2D, not 3D) for accurate gradient
            # Using distance_2d() excludes vertical component
            distance_m = prev_point.distance_2d(curr_point) or 0.0
            if distance_m <= 0:
                continue

            # Calculate elevation change (meters)
            elevation_diff_m = curr_point.elevation - prev_point.elevation

            # Calculate gradient (percentage) = rise / run * 100
            # This gives accurate slope percentage
            gradient = (elevation_diff_m / distance_m) * 100

            # Filter unrealistic gradients (GPS errors can cause spikes)
            # Realistic cycling gradients: -35% to +35%
            if -35 <= gradient <= 35:
                gradients.append(gradient)

        if not gradients:
            return {
                "avg_gradient": None,
                "max_gradient": None,
            }

        # Calculate averages (only uphill gradients for average)
        uphill_gradients = [g for g in gradients if g > 0]
        avg_gradient = sum(uphill_gradients) / len(uphill_gradients) if uphill_gradients else 0.0
        max_gradient = max(gradients)

        return {
            "avg_gradient": round(avg_gradient, 1),
            "max_gradient": round(max_gradient, 1),
        }

    @staticmethod
    def _detect_top_climbs(
        points: list[gpxpy.gpx.GPXTrackPoint], max_climbs: int = 3
    ) -> list[dict[str, Any]]:
        """
        Detect top 3 hardest climbs from trackpoints.

        A climb is defined as a continuous uphill segment where:
        - Elevation consistently increases (minor dips <5m ignored)
        - Minimum elevation gain: 30 meters
        - Minimum distance: 0.5 km

        Climbs are ranked by a "difficulty score":
        - Score = elevation_gain_m * avg_gradient
        - Higher score = harder climb

        Args:
            points: List of GPX trackpoints with elevation data
            max_climbs: Maximum number of climbs to return (default: 3)

        Returns:
            List of climb dictionaries (max 3), each with:
            - start_km: Distance from start where climb begins
            - end_km: Distance from start where climb ends
            - elevation_gain_m: Total elevation gain in meters
            - avg_gradient: Average gradient in percentage
            - description: Human-readable description (e.g., "Climb 1: 150m gain at 8.5%")
        """
        if len(points) < 2:
            return []

        # Detect climb segments
        climbs = []
        in_climb = False
        climb_start_idx = 0
        climb_start_elevation = 0.0
        climb_start_distance_km = 0.0

        # Accumulate cumulative distance
        cumulative_distance_km = 0.0

        for i in range(1, len(points)):
            prev_point = points[i - 1]
            curr_point = points[i]

            # Skip if elevation missing
            if prev_point.elevation is None or curr_point.elevation is None:
                continue

            # Calculate HORIZONTAL distance (2D) for accurate gradient calculation
            distance_m = prev_point.distance_2d(curr_point) or 0.0
            cumulative_distance_km += distance_m / 1000

            elevation_diff = curr_point.elevation - prev_point.elevation

            # Detect climb start (uphill)
            if not in_climb and elevation_diff > 0:
                in_climb = True
                climb_start_idx = i - 1
                climb_start_elevation = prev_point.elevation
                climb_start_distance_km = cumulative_distance_km - (distance_m / 1000)

            # Detect climb end (downhill or flat)
            elif in_climb and elevation_diff < -5:  # Allow minor dips up to 5m
                climb_end_elevation = prev_point.elevation
                climb_end_distance_km = cumulative_distance_km - (distance_m / 1000)

                # Calculate climb metrics
                elevation_gain_m = climb_end_elevation - climb_start_elevation
                distance_km = climb_end_distance_km - climb_start_distance_km

                # Validate climb (min 30m gain, min 0.5km distance)
                if elevation_gain_m >= 30 and distance_km >= 0.5:
                    avg_gradient = (elevation_gain_m / (distance_km * 1000)) * 100
                    difficulty_score = elevation_gain_m * avg_gradient

                    climbs.append(
                        {
                            "start_km": round(climb_start_distance_km, 2),
                            "end_km": round(climb_end_distance_km, 2),
                            "elevation_gain_m": round(elevation_gain_m, 1),
                            "avg_gradient": round(avg_gradient, 1),
                            "difficulty_score": difficulty_score,  # For sorting
                        }
                    )

                # Reset climb state
                in_climb = False

        # Sort climbs by difficulty score (hardest first)
        climbs.sort(key=lambda c: c["difficulty_score"], reverse=True)

        # Return top N climbs with descriptions
        top_climbs = []
        for i, climb in enumerate(climbs[:max_climbs]):
            # Remove difficulty_score from output (internal use only)
            climb_output = {
                "start_km": climb["start_km"],
                "end_km": climb["end_km"],
                "elevation_gain_m": climb["elevation_gain_m"],
                "avg_gradient": climb["avg_gradient"],
                "description": f"Subida {i + 1}: {climb['elevation_gain_m']:.0f}m de desnivel con {climb['avg_gradient']:.1f}% de pendiente media",
            }
            top_climbs.append(climb_output)

        return top_climbs
