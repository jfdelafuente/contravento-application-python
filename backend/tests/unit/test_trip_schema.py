"""
Unit tests for Trip-related Pydantic schemas.

Tests schema validation, difficulty read-only enforcement, and field constraints.

Feature: 017-gps-trip-wizard
Task: T049
"""

import pytest
from pydantic import ValidationError

from src.models.trip import TripDifficulty
from src.schemas.gpx_wizard import GPXTelemetry, GPXTripCreateInput


class TestGPXTelemetrySchema:
    """Test GPXTelemetry schema validation and difficulty display."""

    def test_telemetry_with_full_elevation_data(self):
        """Test telemetry schema with complete elevation data."""
        data = {
            "distance_km": 42.5,
            "elevation_gain": 1250.0,
            "elevation_loss": 1100.0,
            "max_elevation": 1850.0,
            "min_elevation": 450.0,
            "has_elevation": True,
            "difficulty": "difficult",
        }

        telemetry = GPXTelemetry(**data)

        assert telemetry.distance_km == 42.5
        assert telemetry.elevation_gain == 1250.0
        assert telemetry.elevation_loss == 1100.0
        assert telemetry.max_elevation == 1850.0
        assert telemetry.min_elevation == 450.0
        assert telemetry.has_elevation is True
        assert telemetry.difficulty == TripDifficulty.DIFFICULT

    def test_telemetry_without_elevation_data(self):
        """Test telemetry schema when GPX has no elevation data."""
        data = {
            "distance_km": 15.3,
            "elevation_gain": None,
            "elevation_loss": None,
            "max_elevation": None,
            "min_elevation": None,
            "has_elevation": False,
            "difficulty": "easy",
        }

        telemetry = GPXTelemetry(**data)

        assert telemetry.distance_km == 15.3
        assert telemetry.elevation_gain is None
        assert telemetry.elevation_loss is None
        assert telemetry.max_elevation is None
        assert telemetry.min_elevation is None
        assert telemetry.has_elevation is False
        assert telemetry.difficulty == TripDifficulty.EASY

    def test_difficulty_accepts_all_valid_levels(self):
        """Test that difficulty field accepts all TripDifficulty enum values."""
        valid_difficulties = ["easy", "moderate", "difficult", "very_difficult", "extreme"]

        for diff in valid_difficulties:
            data = {
                "distance_km": 20.0,
                "elevation_gain": None,
                "elevation_loss": None,
                "max_elevation": None,
                "min_elevation": None,
                "has_elevation": False,
                "difficulty": diff,
            }
            telemetry = GPXTelemetry(**data)
            assert telemetry.difficulty.value == diff

    def test_difficulty_rejects_invalid_value(self):
        """Test that difficulty field rejects invalid enum values."""
        data = {
            "distance_km": 20.0,
            "elevation_gain": None,
            "elevation_loss": None,
            "max_elevation": None,
            "min_elevation": None,
            "has_elevation": False,
            "difficulty": "super_hard",  # Invalid
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTelemetry(**data)

        assert "difficulty" in str(exc_info.value)

    def test_distance_must_be_non_negative(self):
        """Test that distance_km must be >= 0."""
        data = {
            "distance_km": -10.0,  # Invalid
            "elevation_gain": None,
            "elevation_loss": None,
            "max_elevation": None,
            "min_elevation": None,
            "has_elevation": False,
            "difficulty": "easy",
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTelemetry(**data)

        assert "distance_km" in str(exc_info.value)

    def test_elevation_gain_must_be_non_negative_when_present(self):
        """Test that elevation_gain must be >= 0 when not None."""
        data = {
            "distance_km": 20.0,
            "elevation_gain": -500.0,  # Invalid
            "elevation_loss": None,
            "max_elevation": None,
            "min_elevation": None,
            "has_elevation": False,
            "difficulty": "easy",
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTelemetry(**data)

        assert "elevation_gain" in str(exc_info.value)

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raise ValidationError."""
        # Missing difficulty
        data = {
            "distance_km": 20.0,
            "elevation_gain": None,
            "elevation_loss": None,
            "max_elevation": None,
            "min_elevation": None,
            "has_elevation": False,
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTelemetry(**data)

        assert "difficulty" in str(exc_info.value)


class TestGPXTripCreateInputSchema:
    """Test GPXTripCreateInput schema validation and difficulty read-only enforcement."""

    def test_trip_create_input_with_valid_data(self):
        """Test trip creation schema with all valid fields."""
        data = {
            "title": "Ruta Bikepacking Pirineos",
            "description": "Viaje de 5 días por los Pirineos con más de 300km recorridos y 5000m de desnivel acumulado.",
            "start_date": "2024-06-01",
            "end_date": "2024-06-05",
            "privacy": "public",
        }

        trip_input = GPXTripCreateInput(**data)

        assert trip_input.title == "Ruta Bikepacking Pirineos"
        assert "300km" in trip_input.description
        assert trip_input.start_date == "2024-06-01"
        assert trip_input.end_date == "2024-06-05"
        assert trip_input.privacy == "public"

    def test_difficulty_field_not_present_in_schema(self):
        """
        Test that difficulty field is NOT present in GPXTripCreateInput.

        This is CRITICAL: Difficulty must be read-only, calculated from telemetry,
        and never user-editable. The schema should not accept a difficulty field.

        See: spec.md Functional Requirements (FR-008)
        """
        data = {
            "title": "Test Route",
            "description": "This is a test description with at least 50 characters to pass validation.",
            "start_date": "2024-06-01",
            "end_date": "2024-06-05",
            "privacy": "public",
            "difficulty": "difficult",  # Should be ignored/not accepted
        }

        # Create instance - difficulty should be ignored
        trip_input = GPXTripCreateInput(**data)

        # Verify difficulty field does not exist on the model
        assert not hasattr(trip_input, "difficulty")

    def test_title_max_length_enforced(self):
        """Test that title cannot exceed 200 characters."""
        data = {
            "title": "A" * 201,  # Too long
            "description": "Valid description with at least 50 characters for validation purposes.",
            "start_date": "2024-06-01",
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTripCreateInput(**data)

        assert "title" in str(exc_info.value)

    def test_description_min_length_enforced(self):
        """Test that description must have at least 50 characters."""
        data = {
            "title": "Valid Title",
            "description": "Too short",  # Less than 50 chars
            "start_date": "2024-06-01",
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTripCreateInput(**data)

        assert "description" in str(exc_info.value)

    def test_privacy_defaults_to_public(self):
        """Test that privacy defaults to 'public' when not provided."""
        data = {
            "title": "Test Route",
            "description": "This is a valid description with at least 50 characters for the test.",
            "start_date": "2024-06-01",
        }

        trip_input = GPXTripCreateInput(**data)

        assert trip_input.privacy == "public"

    def test_end_date_optional(self):
        """Test that end_date is optional (can be None)."""
        data = {
            "title": "Test Route",
            "description": "This is a valid description with at least 50 characters for the test.",
            "start_date": "2024-06-01",
            # end_date omitted
        }

        trip_input = GPXTripCreateInput(**data)

        assert trip_input.end_date is None

    def test_missing_required_title_raises_error(self):
        """Test that missing title raises ValidationError."""
        data = {
            # title missing
            "description": "This is a valid description with at least 50 characters for the test.",
            "start_date": "2024-06-01",
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTripCreateInput(**data)

        assert "title" in str(exc_info.value)

    def test_missing_required_start_date_raises_error(self):
        """Test that missing start_date raises ValidationError."""
        data = {
            "title": "Test Route",
            "description": "This is a valid description with at least 50 characters for the test.",
            # start_date missing
        }

        with pytest.raises(ValidationError) as exc_info:
            GPXTripCreateInput(**data)

        assert "start_date" in str(exc_info.value)
