"""
Route Statistics Service (User Story 5 - Advanced Statistics).

Provides algorithms for calculating advanced route analytics including:
- Speed metrics (average, maximum)
- Time analysis (total time, moving time with stop detection)
- Climb detection (identify top 3 hardest climbs)
- Gradient classification (distribute route into gradient categories)

Functional Requirements: FR-030 to FR-034
Success Criteria: SC-021 to SC-024
"""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession


class RouteStatsService:
    """
    Service for calculating advanced route statistics.

    Methods:
    - calculate_speed_metrics: Calculate speed and time metrics from timestamps
    - detect_climbs: Identify top 3 hardest climbs
    - classify_gradients: Classify route segments by gradient category
    """

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def calculate_speed_metrics(
        self, trackpoints: List[Dict[str, Any]]
    ) -> Dict[str, float | None]:
        """
        Calculate speed and time metrics from GPS trackpoints with timestamps.

        Calculates:
        - Average speed (km/h)
        - Maximum speed (km/h)
        - Total elapsed time (minutes)
        - Moving time (minutes, excluding stops >2 minutes with speed <3 km/h)

        Args:
            trackpoints: List of trackpoint dicts with lat, lon, distance_km, timestamp (optional)

        Returns:
            Dict with keys: avg_speed_kmh, max_speed_kmh, total_time_minutes, moving_time_minutes
            All values are None if trackpoints lack timestamps.

        Requirements:
        - FR-030: Calculate avg/max speed, total/moving time
        - SC-021: Speed calculations within ±5% accuracy

        Examples:
            >>> trackpoints = [
            ...     {"distance_km": 0.0, "timestamp": datetime(2024, 1, 1, 10, 0)},
            ...     {"distance_km": 10.0, "timestamp": datetime(2024, 1, 1, 10, 30)}
            ... ]
            >>> result = await service.calculate_speed_metrics(trackpoints)
            >>> result["avg_speed_kmh"]  # 10km / 0.5h = 20 km/h
            20.0
        """
        # Check if timestamps are available
        if not trackpoints or "timestamp" not in trackpoints[0]:
            return {
                "avg_speed_kmh": None,
                "max_speed_kmh": None,
                "total_time_minutes": None,
                "moving_time_minutes": None,
            }

        # Calculate total time
        start_time: datetime = trackpoints[0]["timestamp"]
        end_time: datetime = trackpoints[-1]["timestamp"]
        total_time_delta = end_time - start_time
        total_time_minutes = total_time_delta.total_seconds() / 60.0

        # Calculate moving time (exclude stops: speed <3 km/h for >2 minutes)
        STOP_SPEED_THRESHOLD_KMH = 3.0  # Speed below this is considered stopped
        STOP_DURATION_THRESHOLD_MINUTES = 2.0  # Stops longer than this are excluded (FR-030 revised)
        moving_time_minutes = 0.0
        max_speed_kmh = 0.0
        total_distance_km = trackpoints[-1]["distance_km"]

        for i in range(len(trackpoints) - 1):
            p1 = trackpoints[i]
            p2 = trackpoints[i + 1]

            time_delta = p2["timestamp"] - p1["timestamp"]
            segment_time_minutes = time_delta.total_seconds() / 60.0
            segment_distance_km = p2["distance_km"] - p1["distance_km"]

            # Calculate instantaneous speed for this segment
            segment_speed_kmh = 0.0
            if segment_time_minutes > 0:
                segment_speed_kmh = (segment_distance_km / segment_time_minutes) * 60.0
                max_speed_kmh = max(max_speed_kmh, segment_speed_kmh)

            # Detect if this segment is a stop (low speed for extended duration)
            is_stop = (
                segment_speed_kmh < STOP_SPEED_THRESHOLD_KMH
                and segment_time_minutes > STOP_DURATION_THRESHOLD_MINUTES
            )

            # Only count segment as moving time if not a stop
            if not is_stop:
                moving_time_minutes += segment_time_minutes

        # Calculate average speed (based on total distance and moving time)
        avg_speed_kmh = None
        if moving_time_minutes > 0:
            avg_speed_kmh = (total_distance_km / moving_time_minutes) * 60.0

        return {
            "avg_speed_kmh": avg_speed_kmh,
            "max_speed_kmh": max_speed_kmh if max_speed_kmh > 0 else None,
            "total_time_minutes": total_time_minutes,
            "moving_time_minutes": moving_time_minutes,
        }

    async def detect_climbs(
        self, trackpoints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect and rank the top 3 hardest climbs on the route.

        Algorithm:
        1. Segment route into continuous climbs (elevation gain without significant descent)
        2. Calculate metrics for each climb (elevation gain, distance, avg gradient)
        3. Score climbs by difficulty (weighted combination of gain and gradient)
        4. Return top 3 hardest climbs

        Args:
            trackpoints: List of trackpoint dicts with elevation, distance_km, sequence

        Returns:
            List of top 3 climbs, each with:
            - start_km: Distance where climb starts
            - end_km: Distance where climb ends
            - elevation_gain_m: Total elevation gain
            - avg_gradient: Average gradient as percentage

        Requirements:
        - FR-031: Identify top 3 hardest climbs
        - SC-022: Algorithm correctly identifies hardest climbs

        Notes:
        - Climbs must have minimum elevation gain (50m) to be considered
        - Difficulty score = elevation_gain * (1 + avg_gradient/10)
        - This prioritizes both long climbs and steep climbs
        """
        if not trackpoints or len(trackpoints) < 2:
            return []

        # Check if elevation data is available
        if "elevation" not in trackpoints[0] or trackpoints[0]["elevation"] is None:
            return []

        # Segment route into continuous climbs
        climbs: List[Dict[str, Any]] = []
        DESCENT_THRESHOLD_M = 10.0  # If elevation drops >10m from max, climb ends
        FLAT_THRESHOLD_M = 2.0  # Elevation change <2m is considered flat
        FLAT_SECTION_COUNT = 3  # If 3+ flat points in a row, climb ends
        MIN_CLIMB_GAIN_M = 50.0  # Minimum gain to qualify as a climb

        climb_start_idx = None
        climb_start_elevation = None
        climb_max_elevation = None  # Track maximum elevation reached during climb
        climb_max_idx = None  # Track index where maximum was reached
        flat_count = 0  # Count consecutive flat/descending points

        for i in range(len(trackpoints)):
            current_elevation = trackpoints[i]["elevation"]

            if current_elevation is None:
                continue

            # Start a new climb if not already climbing
            if climb_start_idx is None:
                climb_start_idx = i
                climb_start_elevation = current_elevation
                climb_max_elevation = current_elevation
                climb_max_idx = i
                flat_count = 0
                continue

            # Check elevation change from previous maximum
            if current_elevation > climb_max_elevation:
                # Still climbing - update maximum and reset flat counter
                climb_max_elevation = current_elevation
                climb_max_idx = i
                flat_count = 0
            else:
                # Not climbing (flat or descending)
                flat_count += 1

            # Check if climb ends
            descent_from_max = climb_max_elevation - current_elevation
            should_end_climb = False

            # Condition 1: Significant descent from maximum elevation
            if descent_from_max > DESCENT_THRESHOLD_M:
                should_end_climb = True

            # Condition 2: Prolonged flat/descending section (indicates climb has ended)
            if flat_count >= FLAT_SECTION_COUNT:
                should_end_climb = True

            if should_end_climb:
                # Save climb (from start to max elevation point)
                if climb_max_idx > climb_start_idx:
                    climb_gain = climb_max_elevation - climb_start_elevation

                    if climb_gain >= MIN_CLIMB_GAIN_M:
                        start_km = trackpoints[climb_start_idx]["distance_km"]
                        end_km = trackpoints[climb_max_idx]["distance_km"]
                        distance_km = end_km - start_km

                        if distance_km > 0:
                            avg_gradient = (climb_gain / (distance_km * 1000)) * 100

                            climbs.append(
                                {
                                    "start_km": start_km,
                                    "end_km": end_km,
                                    "elevation_gain_m": climb_gain,
                                    "avg_gradient": avg_gradient,
                                }
                            )

                # Start new climb at current point
                climb_start_idx = i
                climb_start_elevation = current_elevation
                climb_max_elevation = current_elevation
                climb_max_idx = i
                flat_count = 0  # Reset flat counter for new climb

        # Save final climb if exists (from start to max elevation point)
        if climb_start_idx is not None and climb_max_idx is not None:
            if climb_max_idx > climb_start_idx:
                climb_gain = climb_max_elevation - climb_start_elevation

                if climb_gain >= MIN_CLIMB_GAIN_M:
                    start_km = trackpoints[climb_start_idx]["distance_km"]
                    end_km = trackpoints[climb_max_idx]["distance_km"]
                    distance_km = end_km - start_km

                    if distance_km > 0:
                        avg_gradient = (climb_gain / (distance_km * 1000)) * 100

                        climbs.append(
                            {
                                "start_km": start_km,
                                "end_km": end_km,
                                "elevation_gain_m": climb_gain,
                                "avg_gradient": avg_gradient,
                            }
                        )

        # Score and rank climbs by difficulty
        # Score = elevation_gain * (1 + avg_gradient/10)
        # This balances long climbs (high gain) with steep climbs (high gradient)
        for climb in climbs:
            climb["difficulty_score"] = climb["elevation_gain_m"] * (
                1 + climb["avg_gradient"] / 10.0
            )

        # Sort by difficulty score (descending)
        climbs.sort(key=lambda c: c["difficulty_score"], reverse=True)

        # Return top 3 climbs (remove difficulty_score from output)
        top_climbs = climbs[:3]
        for climb in top_climbs:
            climb.pop("difficulty_score", None)

        return top_climbs

    async def classify_gradients(
        self, trackpoints: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Classify route segments by gradient category.

        Categories (FR-032):
        - Llano (flat): 0-3% gradient
        - Moderado (moderate): 3-6% gradient
        - Empinado (steep): 6-10% gradient
        - Muy empinado (very steep): >10% gradient

        Args:
            trackpoints: List of trackpoint dicts with elevation, distance_km, sequence

        Returns:
            Dict with keys: llano, moderado, empinado, muy_empinado
            Each value is a dict with:
            - distance_km: Total distance in this category
            - percentage: Percentage of total route distance

        Requirements:
        - FR-032: Gradient distribution visualization

        Example:
            >>> result = await service.classify_gradients(trackpoints)
            >>> result["empinado"]["percentage"]  # % of route with 6-10% gradient
            25.3
        """
        if not trackpoints or len(trackpoints) < 2:
            return self._empty_gradient_distribution()

        # Check if elevation data is available
        if "elevation" not in trackpoints[0] or trackpoints[0]["elevation"] is None:
            return self._empty_gradient_distribution()

        # Initialize category distances
        category_distances = {
            "llano": 0.0,  # 0-3%
            "moderado": 0.0,  # 3-6%
            "empinado": 0.0,  # 6-10%
            "muy_empinado": 0.0,  # >10%
        }

        total_distance_km = trackpoints[-1]["distance_km"]

        # Classify each segment
        for i in range(len(trackpoints) - 1):
            p1 = trackpoints[i]
            p2 = trackpoints[i + 1]

            # Skip if elevation missing
            if p1["elevation"] is None or p2["elevation"] is None:
                continue

            # Calculate segment gradient
            elevation_change = p2["elevation"] - p1["elevation"]
            distance_km = p2["distance_km"] - p1["distance_km"]

            if distance_km <= 0:
                continue

            # Calculate gradient as percentage
            gradient = abs((elevation_change / (distance_km * 1000)) * 100)

            # Classify segment
            if gradient <= 3.0:
                category_distances["llano"] += distance_km
            elif gradient <= 6.0:
                category_distances["moderado"] += distance_km
            elif gradient <= 10.0:
                category_distances["empinado"] += distance_km
            else:
                category_distances["muy_empinado"] += distance_km

        # Calculate percentages
        result = {}
        for category, distance_km in category_distances.items():
            percentage = (distance_km / total_distance_km) * 100 if total_distance_km > 0 else 0.0
            result[category] = {
                "distance_km": distance_km,
                "percentage": percentage,
            }

        return result

    def _empty_gradient_distribution(self) -> Dict[str, Dict[str, float]]:
        """Return empty gradient distribution (all zeros)."""
        return {
            "llano": {"distance_km": 0.0, "percentage": 0.0},
            "moderado": {"distance_km": 0.0, "percentage": 0.0},
            "empinado": {"distance_km": 0.0, "percentage": 0.0},
            "muy_empinado": {"distance_km": 0.0, "percentage": 0.0},
        }
