"""
GPX service for GPS Routes feature.

Business logic for GPX file parsing, track simplification, and route statistics.
Functional Requirements: FR-001 to FR-008, FR-021, FR-034, FR-036, FR-039
Success Criteria: SC-002, SC-003, SC-005, SC-026
"""

import logging
import re
from datetime import UTC, datetime
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any

import gpxpy
import gpxpy.gpx
from rdp import rdp
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Elevation anomaly detection range (FR-034)
MIN_ELEVATION = -420  # Dead Sea depth
MAX_ELEVATION = 8850  # Mount Everest height


def clean_filename_for_title(filename: str) -> str:
    """
    Clean GPX filename to generate user-friendly title.

    Transformations applied:
    1. Remove .gpx extension
    2. Remove timestamps FIRST (YYYY-MM-DD, YYYYMMDD)
    3. Replace underscores and hyphens with spaces
    4. Remove version numbers (v1, v2, final, etc.)
    5. Remove common suffixes (export, copia, backup, temp)
    6. Remove GPS-specific prefixes (only if >2 words remain)
    7. Title case capitalization (preserving acronyms)
    8. Remove multiple spaces

    Args:
        filename: Original filename (e.g., "ruta_pirineos_v2_final.gpx")

    Returns:
        Cleaned title (e.g., "Ruta Pirineos")

    Examples:
        >>> clean_filename_for_title("ruta_pirineos_v2_final.gpx")
        "Ruta Pirineos"
        >>> clean_filename_for_title("track-2024-01-15_export.gpx")
        "Track"
        >>> clean_filename_for_title("camino_santiago_etapa_03_v1.gpx")
        "Camino Santiago Etapa 03"
    """
    # Remove .gpx extension
    title = Path(filename).stem

    # Handle edge case: empty or dot-only filenames
    if not title or title.startswith("."):
        return "Nueva Ruta"

    # Remove timestamps FIRST (before replacing hyphens)
    # Handles: 2024-01-15, 20240115, 2024-06-30, etc.
    title = re.sub(r"\b\d{4}-?\d{2}-?\d{2}\b", "", title)

    # Replace underscores and hyphens with spaces
    title = title.replace("_", " ").replace("-", " ")

    # Remove version numbers: v1, v2, v3, etc.
    title = re.sub(r"\bv\d+\b", "", title, flags=re.IGNORECASE)

    # Remove common suffixes: final, definitivo, export, copia, backup, temp
    title = re.sub(
        r"\b(final|definitivo|export|copia|copy|backup|temp|tmp)\b", "", title, flags=re.IGNORECASE
    )

    # Remove GPS-specific prefixes: track, gps, route, ruta
    # ONLY if the title has MORE THAN 2 words after removal (to be conservative)
    words = title.split()
    if len(words) > 2:
        # Try removing prefix
        test_title = re.sub(r"^\b(track|gps|route|ruta)\b\s*", "", title, flags=re.IGNORECASE)
        # Only use it if we still have at least 2 words
        if len(test_title.split()) >= 2:
            title = test_title

    # Remove multiple spaces
    title = re.sub(r"\s+", " ", title).strip()

    # Title case capitalization (preserving acronyms)
    def title_case_word(word: str) -> str:
        """Apply title case to word, preserving acronyms."""
        # Keep acronyms uppercase
        if word.upper() in ["GPS", "POI", "GPX", "MTB", "BTT"]:
            return word.upper()
        # Keep roman numerals uppercase
        if re.match(r"^[IVX]+$", word.upper()):
            return word.upper()
        # Regular title case
        return word.capitalize()

    title = " ".join(title_case_word(w) for w in title.split())

    # Fallback: if title is empty or very short, return "Nueva Ruta"
    if not title or len(title.strip()) < 3:
        return "Nueva Ruta"

    return title


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

    async def parse_gpx_file(self, file_content: bytes) -> dict[str, Any]:
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
            has_timestamps = any(
                p.time is not None for p in points[:100]
            )  # Sample first 100 points

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
                "original_points": points,  # Include original points for statistics calculation
            }

        except gpxpy.gpx.GPXException as e:
            raise ValueError(f"Error al procesar archivo GPX: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error al procesar archivo GPX: {str(e)}")

    def _simplify_track_optimized(
        self, points: list[gpxpy.gpx.GPXTrackPoint], epsilon: float = 0.0001
    ) -> list[dict[str, Any]]:
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
        simplified: list[dict[str, Any]] = []
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

            simplified.append(self._point_to_dict(original, i, cumulative_distance, gradient))

            # Calculate cumulative distance for next point
            if i < len(simplified_coords) - 1:
                next_lat, next_lon = simplified_coords[i + 1]
                segment_distance = self._calculate_distance(lat, lon, next_lat, next_lon)
                cumulative_distance += segment_distance

        return simplified

    def _simplify_track(
        self, points: list[gpxpy.gpx.GPXTrackPoint], epsilon: float = 0.0001
    ) -> list[dict[str, Any]]:
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
        simplified: list[dict[str, Any]] = []
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

            simplified.append(self._point_to_dict(original, i, cumulative_distance, gradient))

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
    ) -> dict[str, Any]:
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

    def convert_points_for_stats(
        self, points: list[gpxpy.gpx.GPXTrackPoint]
    ) -> list[dict[str, Any]]:
        """
        Convert GPX trackpoints to dictionary format for RouteStatsService.

        This method converts original GPX trackpoints (gpxpy objects) to the
        dictionary format expected by RouteStatsService for statistics calculation.

        Args:
            points: List of original GPX trackpoint objects

        Returns:
            List of trackpoint dictionaries with fields:
            - latitude, longitude: GPS coordinates
            - elevation: Elevation in meters (None if missing)
            - distance_km: Cumulative distance from start
            - timestamp: Timestamp (datetime object, None if missing)
            - sequence: Point order in sequence

        Note:
            Distance is calculated cumulatively using Haversine formula.
        """
        if not points:
            return []

        trackpoints = []
        cumulative_distance_km = 0.0

        for i, point in enumerate(points):
            # Calculate cumulative distance (Haversine formula)
            if i > 0:
                prev_point = points[i - 1]
                segment_distance = self._calculate_distance(
                    prev_point.latitude,
                    prev_point.longitude,
                    point.latitude,
                    point.longitude,
                )
                cumulative_distance_km += segment_distance

            trackpoints.append(
                {
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                    "elevation": point.elevation if point.elevation is not None else None,
                    "distance_km": round(cumulative_distance_km, 3),
                    "timestamp": point.time if point.time is not None else None,
                    "sequence": i,
                }
            )

        return trackpoints

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
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

    async def extract_telemetry_quick(
        self, file_content: bytes, include_trackpoints: bool = False
    ) -> dict[str, Any]:
        """
        Extract lightweight telemetry data from GPX file for wizard preview.

        This method provides QUICK GPX analysis for the wizard's upload step.
        Unlike parse_gpx_file(), this method does NOT:
        - Save data to database

        It extracts essential telemetry for difficulty preview:
        - Distance (using Haversine formula)
        - Elevation gain/loss (if elevation data exists)
        - Auto-calculated difficulty level
        - Optionally, simplified trackpoints for map visualization

        Feature: 017-gps-trip-wizard
        Endpoint: POST /gpx/analyze
        Performance Goal: <2s for files up to 10MB (SC-002)

        Args:
            file_content: Raw GPX file bytes
            include_trackpoints: If True, include simplified trackpoints for map visualization

        Returns:
            Dict with telemetry data:
            - distance_km: Total distance in kilometers
            - elevation_gain: Cumulative uphill in meters (None if no elevation)
            - elevation_loss: Cumulative downhill in meters (None if no elevation)
            - max_elevation: Maximum altitude in meters (None if no elevation)
            - min_elevation: Minimum altitude in meters (None if no elevation)
            - has_elevation: Whether GPX contains elevation data
            - has_timestamps: Whether GPX contains timestamp data
            - start_date: Start date from GPS timestamps (YYYY-MM-DD, None if no timestamps)
            - end_date: End date from GPS timestamps (YYYY-MM-DD, None if same day or no timestamps)
            - difficulty: TripDifficulty enum value (auto-calculated)
            - trackpoints: Simplified trackpoints (only if include_trackpoints=True)

        Raises:
            ValueError: If GPX is invalid or corrupted

        Examples:
            >>> result = await service.extract_telemetry_quick(gpx_content)
            >>> result["distance_km"]
            42.5
            >>> result["elevation_gain"]
            1250.0
            >>> result["difficulty"]
            TripDifficulty.DIFFICULT
            >>> result = await service.extract_telemetry_quick(gpx_content, include_trackpoints=True)
            >>> len(result["trackpoints"])
            250
        """
        try:
            # Parse GPX XML
            gpx = gpxpy.parse(file_content)

            # Extract all trackpoints
            points = []
            for track in gpx.tracks:
                for segment in track.segments:
                    points.extend(segment.points)

            if not points:
                raise ValueError("El archivo GPX no contiene puntos de track")

            # Calculate total distance using Haversine formula
            total_distance_km = 0.0
            for i in range(1, len(points)):
                prev_point = points[i - 1]
                curr_point = points[i]
                segment_distance = self._calculate_distance(
                    prev_point.latitude,
                    prev_point.longitude,
                    curr_point.latitude,
                    curr_point.longitude,
                )
                total_distance_km += segment_distance

            # Check for elevation data
            has_elevation = any(p.elevation is not None for p in points)

            # Check for timestamps and extract dates if available
            has_timestamps = any(p.time is not None for p in points)
            start_date = None
            end_date = None

            if has_timestamps:
                # Extract timestamps from points that have them
                timestamps = [p.time for p in points if p.time is not None]
                if timestamps:
                    # Get earliest and latest timestamps
                    min_time = min(timestamps)
                    max_time = max(timestamps)
                    # Convert to date-only format (YYYY-MM-DD)
                    start_date = min_time.date().isoformat()
                    end_date = max_time.date().isoformat()

            # Calculate elevation statistics if data exists
            elevation_gain = None
            elevation_loss = None
            max_elevation = None
            min_elevation = None

            if has_elevation:
                elevations = [p.elevation for p in points if p.elevation is not None]

                # Detect anomalous elevations (FR-034)
                for ele in elevations:
                    if ele < MIN_ELEVATION or ele > MAX_ELEVATION:
                        raise ValueError(
                            f"Elevación anómala detectada: {ele}m. "
                            f"Los valores deben estar entre {MIN_ELEVATION}m y {MAX_ELEVATION}m"
                        )

                max_elevation = max(elevations)
                min_elevation = min(elevations)

                # Calculate cumulative elevation gain/loss
                gain = 0.0
                loss = 0.0
                for i in range(1, len(points)):
                    prev_ele = points[i - 1].elevation
                    curr_ele = points[i].elevation
                    if prev_ele is not None and curr_ele is not None:
                        diff = curr_ele - prev_ele
                        if diff > 0:
                            gain += diff
                        else:
                            loss += abs(diff)

                elevation_gain = round(gain, 1)
                elevation_loss = round(loss, 1)

            # Calculate difficulty using DifficultyCalculator
            from src.services.difficulty_calculator import DifficultyCalculator

            difficulty = DifficultyCalculator.calculate(total_distance_km, elevation_gain)

            # Build base result
            result = {
                "distance_km": round(total_distance_km, 2),
                "elevation_gain": elevation_gain,
                "elevation_loss": elevation_loss,
                "max_elevation": max_elevation,
                "min_elevation": min_elevation,
                "has_elevation": has_elevation,
                "has_timestamps": has_timestamps,
                "start_date": start_date,
                "end_date": end_date,
                "difficulty": difficulty,
            }

            # Optionally include simplified trackpoints for wizard map visualization
            if include_trackpoints:
                simplified_trackpoints = self._simplify_track_optimized(points, epsilon=0.0001)
                # Convert to simple dict format for JSON serialization
                result["trackpoints"] = [
                    {
                        "latitude": tp["latitude"],
                        "longitude": tp["longitude"],
                        "elevation": tp.get("elevation"),
                        "distance_km": tp["distance_km"],
                    }
                    for tp in simplified_trackpoints
                ]
            else:
                result["trackpoints"] = None

            return result

        except Exception as e:
            if isinstance(e, ValueError):
                # Re-raise ValueError with original message
                raise
            # Wrap other exceptions with Spanish error message
            logger.error(f"Error al procesar archivo GPX: {e}")
            raise ValueError(
                "No se pudo procesar el archivo GPX. "
                "Verifica que sea un archivo válido con datos de ruta."
            )

    async def save_gpx_to_storage(self, trip_id: str, file_content: bytes, filename: str) -> str:
        """
        Save original GPX file to filesystem storage.

        Implements T026: Filesystem storage.

        Args:
            trip_id: Trip ID for organizing storage
            file_content: Raw GPX file bytes
            filename: Original filename (IGNORED for security - prevents path traversal attacks)

        Returns:
            Absolute file path (e.g., "/path/to/storage/gpx_files/2024/06/trip_id/original.gpx")

        File structure: storage/gpx_files/{year}/{month}/{trip_id}/original.gpx

        Security:
            Always saves as 'original.gpx' to prevent malicious filenames like
            '../../etc/passwd' or '../../../root/.ssh/id_rsa' from escaping the
            storage directory. The original filename is logged for auditing but
            never used in the file path construction.
        """
        # Log original filename for auditing (but don't use in path)
        logger.info(
            f"Saving GPX file for trip {trip_id} "
            f"(original filename: {filename}, size: {len(file_content)} bytes)"
        )

        # Get current date for organizing files
        now = datetime.now(UTC)
        year = now.strftime("%Y")
        month = now.strftime("%m")

        # Create directory structure (absolute path)
        storage_root = Path.cwd() / "storage" / "gpx_files" / year / month / trip_id
        storage_root.mkdir(parents=True, exist_ok=True)

        # Save file with standardized name (SECURITY: fixed name prevents path traversal)
        file_path = storage_root / "original.gpx"
        file_path.write_bytes(file_content)

        logger.debug(f"GPX file saved successfully at: {file_path}")

        # Return absolute path for database storage
        return str(file_path)
