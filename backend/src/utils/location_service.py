"""
Location geocoding service using Google Places API.

Converts location names to coordinates (latitude, longitude) for trip locations.
"""

import logging
from dataclasses import dataclass
from typing import Optional

try:
    import googlemaps
except ImportError:
    googlemaps = None  # type: ignore

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass
class GeocodingResult:
    """Result of geocoding operation."""

    latitude: float  # Decimal degrees
    longitude: float  # Decimal degrees
    formatted_address: str  # Full address from Google


class LocationService:
    """Service for geocoding trip locations."""

    def __init__(self) -> None:
        """Initialize location service."""
        self._gmaps_client: Optional[googlemaps.Client] = None  # type: ignore

    def geocode_location(self, location_name: str) -> Optional[GeocodingResult]:
        """
        Geocode location name to coordinates.

        Args:
            location_name: Location name (e.g., "Madrid, Spain", "Camino de Santiago")

        Returns:
            GeocodingResult with coordinates, or None if:
            - Geocoding is disabled in config
            - API key not configured
            - Location not found
            - API error occurs

        Examples:
            >>> service = LocationService()
            >>> result = service.geocode_location("Madrid, Spain")
            >>> result.latitude
            40.4168
            >>> result.longitude
            -3.7038
        """
        # Check if geocoding is enabled
        if not settings.geocoding_enabled:
            return None

        # Check if API key is configured
        if not settings.google_places_api_key:
            logger.debug("Google Places API key not configured")
            return None

        # Skip empty strings
        if not location_name or not location_name.strip():
            return None

        # Get or create Google Maps client
        if self._gmaps_client is None:
            try:
                if googlemaps is None:
                    logger.error("googlemaps library not installed")
                    return None

                self._gmaps_client = googlemaps.Client(key=settings.google_places_api_key)
            except Exception as e:
                logger.error(f"Error creating Google Maps client: {e}")
                return None

        # Geocode the location
        try:
            results = self._gmaps_client.geocode(location_name)

            if not results:
                logger.info(f"No geocoding results for: {location_name}")
                return None

            # Use first (most relevant) result
            first_result = results[0]
            location = first_result["geometry"]["location"]

            return GeocodingResult(
                latitude=location["lat"],
                longitude=location["lng"],
                formatted_address=first_result["formatted_address"],
            )

        except Exception as e:
            logger.error(f"Error geocoding location '{location_name}': {e}")
            return None


# Global singleton instance
location_service = LocationService()
