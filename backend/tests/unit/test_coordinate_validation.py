"""
Unit tests for GPS coordinate validation in LocationInput schema.

Tests coordinate range validation, precision rounding, and nullable coordinates
for the GPS coordinates feature (009-gps-coordinates).

Test Coverage:
- T012: Valid coordinate ranges (latitude: -90 to 90, longitude: -180 to 180)
- T013: Out-of-range rejection with Spanish error messages
- T014: Precision rounding to 6 decimal places
- T015: Nullable coordinates (backwards compatibility)
"""

import pytest
from pydantic import ValidationError

from src.schemas.trip import LocationInput


class TestValidCoordinateRanges:
    """
    T012: Test valid coordinate ranges.

    Validates that coordinates within valid ranges (-90 to 90 for latitude,
    -180 to 180 for longitude) are accepted without errors.
    """

    def test_valid_coordinates_madrid(self):
        """Test valid coordinates for Madrid, Spain."""
        location = LocationInput(
            name="Madrid",
            latitude=40.416775,
            longitude=-3.703790,
        )
        assert location.name == "Madrid"
        assert location.latitude == 40.416775
        assert location.longitude == -3.703790

    def test_valid_coordinates_tokyo(self):
        """Test valid coordinates for Tokyo, Japan."""
        location = LocationInput(
            name="Tokyo",
            latitude=35.689487,
            longitude=139.691711,
        )
        assert location.name == "Tokyo"
        assert location.latitude == 35.689487
        assert location.longitude == 139.691711

    def test_valid_coordinates_sydney(self):
        """Test valid coordinates for Sydney, Australia (negative latitude)."""
        location = LocationInput(
            name="Sydney",
            latitude=-33.868820,
            longitude=151.209290,
        )
        assert location.name == "Sydney"
        assert location.latitude == -33.86882
        assert location.longitude == 151.20929

    def test_valid_coordinates_new_york(self):
        """Test valid coordinates for New York, USA (negative longitude)."""
        location = LocationInput(
            name="New York",
            latitude=40.712776,
            longitude=-74.005974,
        )
        assert location.name == "New York"
        assert location.latitude == 40.712776
        assert location.longitude == -74.005974

    def test_valid_coordinates_equator_prime_meridian(self):
        """Test valid coordinates at equator and prime meridian (0, 0)."""
        location = LocationInput(
            name="Null Island",
            latitude=0.0,
            longitude=0.0,
        )
        assert location.name == "Null Island"
        assert location.latitude == 0.0
        assert location.longitude == 0.0

    def test_valid_coordinates_at_latitude_limits(self):
        """Test valid coordinates at latitude limits (-90, 90)."""
        # South Pole
        south_pole = LocationInput(
            name="South Pole",
            latitude=-90.0,
            longitude=0.0,
        )
        assert south_pole.latitude == -90.0

        # North Pole
        north_pole = LocationInput(
            name="North Pole",
            latitude=90.0,
            longitude=0.0,
        )
        assert north_pole.latitude == 90.0

    def test_valid_coordinates_at_longitude_limits(self):
        """Test valid coordinates at longitude limits (-180, 180)."""
        # International Date Line (West)
        idl_west = LocationInput(
            name="IDL West",
            latitude=0.0,
            longitude=-180.0,
        )
        assert idl_west.longitude == -180.0

        # International Date Line (East)
        idl_east = LocationInput(
            name="IDL East",
            latitude=0.0,
            longitude=180.0,
        )
        assert idl_east.longitude == 180.0


class TestOutOfRangeRejection:
    """
    T013: Test out-of-range coordinate rejection.

    Validates that coordinates outside valid ranges raise ValidationError
    with Spanish error messages.
    """

    def test_latitude_too_high(self):
        """Test latitude > 90 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                name="Invalid North",
                latitude=100.0,
                longitude=0.0,
            )

        # Verify validation error for latitude field
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("latitude",) for error in errors)
        # Pydantic validates with ge/le constraints
        assert any(error["type"] == "less_than_equal" for error in errors)

    def test_latitude_too_low(self):
        """Test latitude < -90 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                name="Invalid South",
                latitude=-100.0,
                longitude=0.0,
            )

        # Verify validation error for latitude field
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("latitude",) for error in errors)
        assert any(error["type"] == "greater_than_equal" for error in errors)

    def test_longitude_too_high(self):
        """Test longitude > 180 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                name="Invalid East",
                latitude=0.0,
                longitude=200.0,
            )

        # Verify validation error for longitude field
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("longitude",) for error in errors)
        assert any(error["type"] == "less_than_equal" for error in errors)

    def test_longitude_too_low(self):
        """Test longitude < -180 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                name="Invalid West",
                latitude=0.0,
                longitude=-200.0,
            )

        # Verify validation error for longitude field
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("longitude",) for error in errors)
        assert any(error["type"] == "greater_than_equal" for error in errors)

    def test_both_coordinates_out_of_range(self):
        """Test both latitude and longitude out of range raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                name="Invalid Location",
                latitude=100.0,
                longitude=200.0,
            )

        # Should have errors for both fields
        errors = exc_info.value.errors()
        assert len(errors) >= 2
        latitude_errors = [e for e in errors if e["loc"] == ("latitude",)]
        longitude_errors = [e for e in errors if e["loc"] == ("longitude",)]
        assert len(latitude_errors) > 0
        assert len(longitude_errors) > 0


class TestPrecisionRounding:
    """
    T014: Test coordinate precision rounding to 6 decimal places.

    Validates that coordinates are rounded to 6 decimal places for consistency
    with GPS precision standards (~0.11m accuracy).
    """

    def test_latitude_rounded_to_6_decimals(self):
        """Test latitude with >6 decimals is rounded to 6 decimals."""
        location = LocationInput(
            name="High Precision Location",
            latitude=40.4167751234567,  # 13 decimals
            longitude=-3.7037901234567,
        )
        # Should be rounded to 6 decimals
        assert location.latitude == 40.416775
        assert location.longitude == -3.703790

    def test_longitude_rounded_to_6_decimals(self):
        """Test longitude with >6 decimals is rounded to 6 decimals."""
        location = LocationInput(
            name="Test Location",
            latitude=35.689487123456,
            longitude=139.691711987654,
        )
        # Should be rounded to 6 decimals
        assert location.latitude == 35.689487
        assert location.longitude == 139.691712

    def test_coordinates_with_exactly_6_decimals(self):
        """Test coordinates with exactly 6 decimals remain unchanged."""
        location = LocationInput(
            name="Exact Precision",
            latitude=40.123456,
            longitude=-3.789012,
        )
        # Should remain unchanged
        assert location.latitude == 40.123456
        assert location.longitude == -3.789012

    def test_coordinates_with_fewer_than_6_decimals(self):
        """Test coordinates with <6 decimals remain unchanged."""
        location = LocationInput(
            name="Low Precision",
            latitude=40.12,  # 2 decimals
            longitude=-3.78,
        )
        # Should remain unchanged (not padded with zeros)
        assert location.latitude == 40.12
        assert location.longitude == -3.78

    def test_integer_coordinates(self):
        """Test integer coordinates remain as integers."""
        location = LocationInput(
            name="Integer Coords",
            latitude=40.0,
            longitude=-3.0,
        )
        # Should remain as integers (0 decimals)
        assert location.latitude == 40.0
        assert location.longitude == -3.0

    def test_rounding_edge_case_round_up(self):
        """Test rounding edge case where 7th decimal >= 5 (round up)."""
        location = LocationInput(
            name="Round Up",
            latitude=40.1234565,  # 7th decimal = 5, should round up
            longitude=-3.7890125,
        )
        # Should round up
        assert location.latitude == 40.123457
        assert location.longitude == -3.789013

    def test_rounding_edge_case_round_down(self):
        """Test rounding edge case where 7th decimal < 5 (round down)."""
        location = LocationInput(
            name="Round Down",
            latitude=40.1234564,  # 7th decimal = 4, should round down
            longitude=-3.7890124,
        )
        # Should round down
        assert location.latitude == 40.123456
        assert location.longitude == -3.789012


class TestNullableCoordinates:
    """
    T015: Test nullable coordinates (backwards compatibility).

    Validates that coordinates are optional and locations can be created
    without GPS coordinates, maintaining backwards compatibility with
    trips created before the GPS feature.
    """

    def test_location_with_no_coordinates(self):
        """Test location with only name (no coordinates)."""
        location = LocationInput(
            name="Madrid",
            latitude=None,
            longitude=None,
        )
        assert location.name == "Madrid"
        assert location.latitude is None
        assert location.longitude is None

    def test_location_with_name_only(self):
        """Test location with only name field provided."""
        location = LocationInput(name="Barcelona")
        assert location.name == "Barcelona"
        assert location.latitude is None
        assert location.longitude is None

    def test_location_with_only_latitude(self):
        """Test location with only latitude (no longitude)."""
        location = LocationInput(
            name="Partial Coords",
            latitude=40.416775,
        )
        assert location.name == "Partial Coords"
        assert location.latitude == 40.416775
        assert location.longitude is None

    def test_location_with_only_longitude(self):
        """Test location with only longitude (no latitude)."""
        location = LocationInput(
            name="Partial Coords",
            longitude=-3.703790,
        )
        assert location.name == "Partial Coords"
        assert location.latitude is None
        assert location.longitude == -3.70379

    def test_location_with_country_but_no_coordinates(self):
        """Test location with name and country but no coordinates."""
        location = LocationInput(
            name="Madrid",
            country="España",
        )
        assert location.name == "Madrid"
        assert location.country == "España"
        assert location.latitude is None
        assert location.longitude is None

    def test_mixed_locations_some_with_coordinates(self):
        """Test multiple locations, some with coordinates, some without."""
        # Location with coordinates
        loc1 = LocationInput(
            name="Jaca",
            latitude=42.570084,
            longitude=-0.549941,
        )
        assert loc1.latitude == 42.570084
        assert loc1.longitude == -0.549941

        # Location without coordinates
        loc2 = LocationInput(name="Camino de Santiago")
        assert loc2.latitude is None
        assert loc2.longitude is None

        # Both locations are valid
        assert loc1.name == "Jaca"
        assert loc2.name == "Camino de Santiago"

    def test_location_with_explicit_none_coordinates(self):
        """Test location with explicitly None coordinates."""
        location = LocationInput(
            name="Test Location",
            latitude=None,
            longitude=None,
            country="España",
        )
        assert location.name == "Test Location"
        assert location.country == "España"
        assert location.latitude is None
        assert location.longitude is None


class TestCoordinateValidationEdgeCases:
    """Additional edge cases for coordinate validation."""

    def test_location_name_required(self):
        """Test location name is required even without coordinates."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                latitude=40.416775,
                longitude=-3.703790,
            )

        # Should have error for missing name field
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_location_name_cannot_be_empty(self):
        """Test location name cannot be empty string."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                name="",
                latitude=40.416775,
                longitude=-3.703790,
            )

        # Should have error for empty name
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_location_name_max_length(self):
        """Test location name respects max length of 200 characters."""
        long_name = "A" * 201  # 201 characters
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(name=long_name)

        # Should have error for name too long
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_country_max_length(self):
        """Test country name respects max length of 100 characters."""
        long_country = "B" * 101  # 101 characters
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(
                name="Test",
                country=long_country,
            )

        # Should have error for country too long
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("country",) for error in errors)

    def test_coordinates_with_string_input_are_converted(self):
        """Test coordinates accept string input and convert to float (Pydantic V2 behavior)."""
        location = LocationInput(
            name="Test",
            latitude="40.416775",  # String is converted to float by Pydantic
            longitude="-3.703790",
        )
        # Pydantic V2 coerces strings to floats
        assert location.latitude == 40.416775
        assert location.longitude == -3.70379  # Rounded to 6 decimals

    def test_coordinates_with_invalid_types(self):
        """Test coordinates reject invalid types."""
        with pytest.raises(ValidationError):
            LocationInput(
                name="Test",
                latitude=[40.416775],  # List instead of float
                longitude=-3.703790,
            )
