"""
GPX service for GPS Routes feature.

Business logic for GPX file parsing, track simplification, and route statistics.
Functional Requirements: FR-001 to FR-008, FR-021, FR-034, FR-036, FR-039
Success Criteria: SC-002, SC-003, SC-005, SC-026
"""

import logging
import uuid
from datetime import UTC, datetime
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any, Dict, List

import gpxpy
import gpxpy.gpx
from rdp import rdp
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.gpx import GPXFile, TrackPoint

logger = logging.getLogger(__name__)

# Elevation anomaly detection range (FR-034)
MIN_ELEVATION = -420  # Dead Sea depth
MAX_ELEVATION = 8850  # Mount Everest height


class GPXService:
    """
    GPX service for managing GPS route data.

    Handles GPX file parsing, track simplification, and route statistics calculation.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize GPX service.

        Args:
            db: Database session
        """
        self.db = db

    async def parse_gpx_file(self, file_content: bytes) -> Dict[str, Any]:
        """
        Parse GPX file and extract track data.

        Implements:
        - T023: GPX parsing using gpxpy library
        - T024: Track simplification using Douglas-Peucker
        - T025: Distance calculation using Haversine formula
        - T027: Elevation anomaly detection

        Args:
            file_content: Raw GPX file bytes

        Returns:
            Dict with route statistics and simplified trackpoints:
            - distance_km: Total distance in kilometers
            - elevation_gain: Total elevation gain in meters
            - elevation_loss: Total elevation loss in meters
            - max_elevation: Maximum altitude in meters
            - min_elevation: Minimum altitude in meters
            - start_lat, start_lon: Starting coordinates
            - end_lat, end_lon: Ending coordinates
            - total_points: Original trackpoint count
            - simplified_points_count: Reduced trackpoint count
            - has_elevation: Whether GPX contains elevation data
            - has_timestamps: Whether GPX contains timestamp data
            - trackpoints: List of simplified trackpoints

        Raises:
            ValueError: If GPX is invalid, corrupted, or contains anomalous data

        Functional Requirements: FR-001, FR-002, FR-003, FR-007, FR-021, FR-034
        Success Criteria: SC-005 (>90% elevation accuracy), SC-026 (30% storage reduction)
        """
        try:
            import time
            start_time = time.perf_counter()

            # Parse GPX XML
            gpx = gpxpy.parse(file_content)
            parse_time = time.perf_counter() - start_time
            logger.info(f"GPX parse time: {parse_time:.3f}s")

            # Extract all trackpoints
            extract_start = time.perf_counter()
            points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    points.extend(segment.points)

            if not points:
                raise ValueError("El archivo GPX no contiene puntos de track")

            extract_time = time.perf_counter() - extract_start
            logger.info(f"Point extraction time: {extract_time:.3f}s, {len(points)} points")

            # Detect timestamps
            has_timestamps = any(p.time is not None for p in points[:100])  # Sample first 100 points

            # Calculate metrics using gpxpy built-in methods
            stats_start = time.perf_counter()
            distance_km = gpx.length_3d() / 1000  # meters to km
            uphill, downhill = gpx.get_uphill_downhill()
            stats_time = time.perf_counter() - stats_start
            logger.info(f"GPX stats calculation time: {stats_time:.3f}s")

            # Extract and validate elevation data (FR-034)
            elev_start = time.perf_counter()
            elevations = [p.elevation for p in points if p.elevation is not None]
            has_elevation = len(elevations) > 0

            if has_elevation:
                # Anomaly detection (FR-034) - optimized with min/max before loop
                min_elev = min(elevations)
                max_elev = max(elevations)

                if min_elev < MIN_ELEVATION or max_elev > MAX_ELEVATION:
                    raise ValueError(
                        f"Elevación anómala detectada: {min_elev}m a {max_elev}m. "
                        f"Rango válido: {MIN_ELEVATION}m a {MAX_ELEVATION}m"
                    )

                max_elevation = max_elev
                min_elevation = min_elev

                # Ensure uphill/downhill are not None (gpxpy may return None)
                uphill = uphill if uphill is not None else 0.0
                downhill = downhill if downhill is not None else 0.0
            else:
                max_elevation = None
                min_elevation = None
                uphill = None
                downhill = None

            elev_time = time.perf_counter() - elev_start
            logger.info(f"Elevation processing time: {elev_time:.3f}s")

            # Simplify trackpoints (Douglas-Peucker algorithm) - T024
            # epsilon=0.0001° ≈ 10 meter precision (more aggressive reduction)
            simplify_start = time.perf_counter()
            simplified_points = self._simplify_track_optimized(points, epsilon=0.0001)
            simplify_time = time.perf_counter() - simplify_start
            logger.info(
                f"Simplification time: {simplify_time:.3f}s, "
                f"{len(points)} -> {len(simplified_points)} points "
                f"({100 * (1 - len(simplified_points) / len(points)):.1f}% reduction)"
            )

            return {
                "distance_km": round(distance_km, 2),
                "elevation_gain": round(uphill, 1) if uphill is not None else None,
                "elevation_loss": round(downhill, 1) if downhill is not None else None,
                "max_elevation": round(max_elevation, 1) if max_elevation is not None else None,
                "min_elevation": round(min_elevation, 1) if min_elevation is not None else None,
                "start_lat": points[0].latitude,
                "start_lon": points[0].longitude,
                "end_lat": points[-1].latitude,
                "end_lon": points[-1].longitude,
                "total_points": len(points),
                "simplified_points_count": len(simplified_points),
                "has_elevation": has_elevation,
                "has_timestamps": has_timestamps,
                "trackpoints": simplified_points,
            }

        except gpxpy.gpx.GPXException as e:
            raise ValueError(f"Error al procesar archivo GPX: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error al procesar archivo GPX: {str(e)}")

    def _simplify_track_optimized(
        self, points: List[gpxpy.gpx.GPXTrackPoint], epsilon: float = 0.0001
    ) -> List[Dict[str, Any]]:
        """
        OPTIMIZED: Simplify GPS track using Ramer-Douglas-Peucker algorithm.

        Optimizations:
        - Use dict lookup instead of linear search (O(1) vs O(n))
        - Pre-calculate point index mapping
        - Single pass for distance and gradient calculation

        Args:
            points: Original GPX trackpoints
            epsilon: Tolerance (0.0001° ≈ 10m precision)

        Returns:
            Simplified trackpoints (typically 80-95% reduction)
        """
        if len(points) < 3:
            return [self._point_to_dict(p, i, 0.0) for i, p in enumerate(points)]

        # Convert to coordinate array for RDP
        coords = [(p.latitude, p.longitude) for p in points]

        # Apply Douglas-Peucker algorithm
        simplified_coords = rdp(coords, epsilon=epsilon)

        # Create point lookup dict (OPTIMIZATION: O(1) lookup instead of O(n))
        point_map = {(p.latitude, p.longitude): p for p in points}

        # Build simplified trackpoints in single pass
        simplified = []
        cumulative_distance = 0.0

        for i, (lat, lon) in enumerate(simplified_coords):
            # O(1) lookup
            original = point_map[(lat, lon)]

            # Calculate gradient if elevation data available
            gradient = None
            if i > 0 and original.elevation is not None and simplified:
                prev_point = simplified[-1]
                if prev_point["elevation"] is not None:
                    distance_m = (cumulative_distance - prev_point["distance_km"]) * 1000
                    elevation_diff = original.elevation - prev_point["elevation"]
                    if distance_m > 0:
                        gradient = (elevation_diff / distance_m) * 100  # Percentage

            simplified.append(
                self._point_to_dict(original, i, cumulative_distance, gradient)
            )

            # Calculate cumulative distance for next point
            if i < len(simplified_coords) - 1:
                next_lat, next_lon = simplified_coords[i + 1]
                segment_distance = self._calculate_distance(lat, lon, next_lat, next_lon)
                cumulative_distance += segment_distance

        return simplified

    def _simplify_track(
        self, points: List[gpxpy.gpx.GPXTrackPoint], epsilon: float = 0.0001
    ) -> List[Dict[str, Any]]:
        """
        Simplify GPS track using Ramer-Douglas-Peucker algorithm.

        Implements T024: Douglas-Peucker simplification.

        Args:
            points: Original GPX trackpoints
            epsilon: Tolerance (0.0001° ≈ 10m precision)

        Returns:
            Simplified trackpoints (typically 80-90% reduction)

        Success Criteria: SC-026 (30% storage reduction via simplification)
        """
        if len(points) < 3:
            return [self._point_to_dict(p, i, 0.0) for i, p in enumerate(points)]

        # Convert to coordinate array for RDP
        coords = [(p.latitude, p.longitude) for p in points]

        # Apply Douglas-Peucker algorithm
        simplified_coords = rdp(coords, epsilon=epsilon)

        # Map back to original points (preserve elevation)
        simplified = []
        cumulative_distance = 0.0

        for i, (lat, lon) in enumerate(simplified_coords):
            # Find original point
            original = next(p for p in points if p.latitude == lat and p.longitude == lon)

            # Calculate gradient if elevation data available
            gradient = None
            if i > 0 and original.elevation is not None and simplified:
                prev_point = simplified[-1]
                if prev_point["elevation"] is not None:
                    distance_m = (cumulative_distance - prev_point["distance_km"]) * 1000
                    elevation_diff = original.elevation - prev_point["elevation"]
                    if distance_m > 0:
                        gradient = (elevation_diff / distance_m) * 100  # Percentage

            simplified.append(
                self._point_to_dict(original, i, cumulative_distance, gradient)
            )

            # Calculate cumulative distance for next point (T025: Haversine)
            if i < len(simplified_coords) - 1:
                next_lat, next_lon = simplified_coords[i + 1]
                segment_distance = self._calculate_distance(lat, lon, next_lat, next_lon)
                cumulative_distance += segment_distance

        return simplified

    def _point_to_dict(
        self,
        point: gpxpy.gpx.GPXTrackPoint,
        sequence: int,
        distance_km: float,
        gradient: float = None,
    ) -> Dict[str, Any]:
        """
        Convert GPX trackpoint to dictionary format.

        Args:
            point: GPX trackpoint object
            sequence: Point order in sequence
            distance_km: Cumulative distance from start
            gradient: Percentage slope (optional)

        Returns:
            Dictionary with point data
        """
        return {
            "latitude": point.latitude,
            "longitude": point.longitude,
            "elevation": point.elevation if point.elevation else None,
            "distance_km": round(distance_km, 3),
            "sequence": sequence,
            "gradient": round(gradient, 2) if gradient is not None else None,
        }

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.

        Implements T025: Distance calculation.

        Args:
            lat1: Starting latitude
            lon1: Starting longitude
            lat2: Ending latitude
            lon2: Ending longitude

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth radius in km

        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c

    async def save_gpx_to_storage(
        self, trip_id: str, file_content: bytes, filename: str
    ) -> str:
        """
        Save original GPX file to filesystem storage.

        Implements T026: Filesystem storage.

        Args:
            trip_id: Trip ID for organizing storage
            file_content: Raw GPX file bytes
            filename: Original filename

        Returns:
            Absolute file path (e.g., "/path/to/storage/gpx_files/2024/06/trip_id/original.gpx")

        File structure: storage/gpx_files/{year}/{month}/{trip_id}/original.gpx
        """
        # Get current date for organizing files
        now = datetime.now(UTC)
        year = now.strftime("%Y")
        month = now.strftime("%m")

        # Create directory structure (absolute path)
        storage_root = Path.cwd() / "storage" / "gpx_files" / year / month / trip_id
        storage_root.mkdir(parents=True, exist_ok=True)

        # Save file with standardized name
        file_path = storage_root / "original.gpx"
        file_path.write_bytes(file_content)

        # Return absolute path for database storage
        return str(file_path)
