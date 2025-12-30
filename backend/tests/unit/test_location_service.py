"""
Unit tests for LocationService.

Tests geocoding with Google Places API for trip locations.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.utils.location_service import GeocodingResult, LocationService


class TestLocationService:
    """Test location geocoding service."""

    @pytest.fixture
    def location_service(self) -> LocationService:
        """Create location service instance."""
        return LocationService()

    def test_geocode_disabled_returns_none(self, location_service: LocationService) -> None:
        """Test that geocoding returns None when disabled in config."""
        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = False

            result = location_service.geocode_location("Madrid, Spain")

            assert result is None

    def test_geocode_without_api_key_returns_none(self, location_service: LocationService) -> None:
        """Test that geocoding returns None when API key not configured."""
        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = ""  # Empty key

            result = location_service.geocode_location("Madrid, Spain")

            assert result is None

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_location_success(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test successful location geocoding."""
        # Mock Google Maps API response
        mock_client = MagicMock()
        mock_gmaps.return_value = mock_client
        mock_client.geocode.return_value = [
            {
                "geometry": {"location": {"lat": 40.4168, "lng": -3.7038}},
                "formatted_address": "Madrid, Spain",
            }
        ]

        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            result = location_service.geocode_location("Madrid")

            assert result is not None
            assert isinstance(result, GeocodingResult)
            assert result.latitude == 40.4168
            assert result.longitude == -3.7038
            assert result.formatted_address == "Madrid, Spain"

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_location_no_results(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test geocoding when no results found."""
        mock_client = MagicMock()
        mock_gmaps.return_value = mock_client
        mock_client.geocode.return_value = []  # No results

        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            result = location_service.geocode_location("XYZ Invalid Location 12345")

            assert result is None

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_location_api_error(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test handling of API errors gracefully."""
        mock_client = MagicMock()
        mock_gmaps.return_value = mock_client
        mock_client.geocode.side_effect = Exception("API Error")

        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            # Should not raise exception, return None instead
            result = location_service.geocode_location("Madrid")

            assert result is None

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_location_returns_first_result(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test that geocoding returns first (most relevant) result."""
        mock_client = MagicMock()
        mock_gmaps.return_value = mock_client
        mock_client.geocode.return_value = [
            {
                "geometry": {"location": {"lat": 40.4168, "lng": -3.7038}},
                "formatted_address": "Madrid, Spain",
            },
            {
                "geometry": {"location": {"lat": 41.0, "lng": -4.0}},
                "formatted_address": "Other Madrid",
            },
        ]

        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            result = location_service.geocode_location("Madrid")

            assert result is not None
            # Should use first result
            assert result.latitude == 40.4168
            assert result.formatted_address == "Madrid, Spain"

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_handles_unicode_characters(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test geocoding with Spanish characters."""
        mock_client = MagicMock()
        mock_gmaps.return_value = mock_client
        mock_client.geocode.return_value = [
            {
                "geometry": {"location": {"lat": 37.3891, "lng": -5.9845}},
                "formatted_address": "Sevilla, España",
            }
        ]

        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            result = location_service.geocode_location("Sevilla, España")

            assert result is not None
            assert result.formatted_address == "Sevilla, España"

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_caches_client_instance(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test that Google Maps client is created only once (cached)."""
        mock_client = MagicMock()
        mock_gmaps.return_value = mock_client
        mock_client.geocode.return_value = [
            {
                "geometry": {"location": {"lat": 40.0, "lng": -3.0}},
                "formatted_address": "Test Location",
            }
        ]

        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            # Call multiple times
            location_service.geocode_location("Location 1")
            location_service.geocode_location("Location 2")
            location_service.geocode_location("Location 3")

            # Client should be created only once
            assert mock_gmaps.call_count == 1

    def test_geocoding_result_dataclass(self) -> None:
        """Test GeocodingResult dataclass structure."""
        result = GeocodingResult(
            latitude=40.4168, longitude=-3.7038, formatted_address="Madrid, Spain"
        )

        assert result.latitude == 40.4168
        assert result.longitude == -3.7038
        assert result.formatted_address == "Madrid, Spain"

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_realistic_spanish_locations(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test with realistic Spanish cycling destinations."""
        mock_client = MagicMock()
        mock_gmaps.return_value = mock_client

        test_locations = [
            ("Camino de Santiago", 42.8805, -8.5457),
            ("Vía Verde del Aceite", 37.7736, -4.1390),
            ("Barcelona", 41.3851, 2.1734),
        ]

        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            for location_name, lat, lng in test_locations:
                mock_client.geocode.return_value = [
                    {
                        "geometry": {"location": {"lat": lat, "lng": lng}},
                        "formatted_address": location_name,
                    }
                ]

                result = location_service.geocode_location(location_name)

                assert result is not None
                assert result.latitude == lat
                assert result.longitude == lng

    @patch("src.utils.location_service.googlemaps.Client")
    def test_geocode_empty_string_returns_none(
        self, mock_gmaps: MagicMock, location_service: LocationService
    ) -> None:
        """Test that empty location name returns None."""
        with patch("src.utils.location_service.settings") as mock_settings:
            mock_settings.geocoding_enabled = True
            mock_settings.google_places_api_key = "test-api-key"

            result = location_service.geocode_location("")
            assert result is None

            result = location_service.geocode_location("   ")
            assert result is None
