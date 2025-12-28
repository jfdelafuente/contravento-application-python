"""
Unit tests for Trip Pydantic schemas.

Tests request/response validation for Travel Diary API.
"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError
from src.schemas.trip import (
    LocationInput,
    TripCreateRequest,
    TripUpdateRequest,
    TagResponse,
    TripLocationResponse,
    TripPhotoResponse,
    TripResponse,
    TripListItemResponse,
    TripListResponse,
)


class TestLocationInput:
    """Test LocationInput schema."""

    def test_valid_location_with_country(self) -> None:
        """Test valid location with country."""
        loc = LocationInput(name="Baeza", country="España")
        assert loc.name == "Baeza"
        assert loc.country == "España"

    def test_valid_location_without_country(self) -> None:
        """Test valid location without country."""
        loc = LocationInput(name="Camino de Santiago")
        assert loc.name == "Camino de Santiago"
        assert loc.country is None

    def test_location_name_required(self) -> None:
        """Test that location name is required."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput()
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_location_name_max_length(self) -> None:
        """Test location name max length (200 chars)."""
        long_name = "A" * 201
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(name=long_name)
        errors = exc_info.value.errors()
        assert any("200" in str(e) for e in errors)

    def test_location_country_max_length(self) -> None:
        """Test country name max length (100 chars)."""
        long_country = "B" * 101
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(name="Test", country=long_country)
        errors = exc_info.value.errors()
        assert any("100" in str(e) for e in errors)


class TestTripCreateRequest:
    """Test TripCreateRequest schema."""

    def test_valid_minimal_trip(self) -> None:
        """Test valid trip with only required fields."""
        trip = TripCreateRequest(
            title="Vía Verde del Aceite",
            description="<p>Un recorrido precioso...</p>",
            start_date=date(2024, 5, 15),
        )
        assert trip.title == "Vía Verde del Aceite"
        assert trip.description == "<p>Un recorrido precioso...</p>"
        assert trip.start_date == date(2024, 5, 15)
        assert trip.end_date is None
        assert trip.distance_km is None
        assert trip.difficulty is None
        assert trip.locations == []
        assert trip.tags == []

    def test_valid_complete_trip(self) -> None:
        """Test valid trip with all fields."""
        trip = TripCreateRequest(
            title="Transpirenaica",
            description="<p>Cruzando los Pirineos...</p>",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 15),
            distance_km=850.5,
            difficulty="very_difficult",
            locations=[
                LocationInput(name="Hendaya", country="Francia"),
                LocationInput(name="Llansa", country="España"),
            ],
            tags=["bikepacking", "pirineos", "larga distancia"],
        )
        assert trip.end_date == date(2024, 7, 15)
        assert trip.distance_km == 850.5
        assert trip.difficulty == "very_difficult"
        assert len(trip.locations) == 2
        assert len(trip.tags) == 3

    def test_title_required(self) -> None:
        """Test that title is required."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                description="Test",
                start_date=date(2024, 5, 15),
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("title",) for e in errors)

    def test_title_min_length(self) -> None:
        """Test title minimum length (1 char)."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="",
                description="Test",
                start_date=date(2024, 5, 15),
            )
        errors = exc_info.value.errors()
        assert any("title" in str(e) for e in errors)

    def test_title_max_length(self) -> None:
        """Test title max length (200 chars)."""
        long_title = "A" * 201
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title=long_title,
                description="Test",
                start_date=date(2024, 5, 15),
            )
        errors = exc_info.value.errors()
        assert any("200" in str(e) for e in errors)

    def test_description_required(self) -> None:
        """Test that description is required."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                start_date=date(2024, 5, 15),
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("description",) for e in errors)

    def test_description_max_length(self) -> None:
        """Test description max length (50000 chars)."""
        long_desc = "A" * 50001
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description=long_desc,
                start_date=date(2024, 5, 15),
            )
        errors = exc_info.value.errors()
        assert any("50000" in str(e) for e in errors)

    def test_start_date_required(self) -> None:
        """Test that start_date is required."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test description",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("start_date",) for e in errors)

    def test_start_date_cannot_be_future(self) -> None:
        """Test that start_date cannot be in the future."""
        from datetime import timedelta
        future_date = date.today() + timedelta(days=30)

        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=future_date,
            )
        errors = exc_info.value.errors()
        assert any("futura" in str(e.get("msg", "")).lower() for e in errors)

    def test_end_date_must_be_after_start_date(self) -> None:
        """Test that end_date must be >= start_date."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                end_date=date(2024, 5, 10),  # Before start_date
            )
        errors = exc_info.value.errors()
        assert any("fin" in str(e.get("msg", "")).lower() for e in errors)

    def test_end_date_can_equal_start_date(self) -> None:
        """Test that end_date can equal start_date (single day trip)."""
        trip = TripCreateRequest(
            title="Test",
            description="Test",
            start_date=date(2024, 5, 15),
            end_date=date(2024, 5, 15),
        )
        assert trip.start_date == trip.end_date

    def test_distance_km_min_value(self) -> None:
        """Test distance_km minimum value (0.1)."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                distance_km=0.0,  # Below minimum
            )
        errors = exc_info.value.errors()
        assert any("0.1" in str(e) for e in errors)

    def test_distance_km_max_value(self) -> None:
        """Test distance_km maximum value (10000)."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                distance_km=10001.0,  # Above maximum
            )
        errors = exc_info.value.errors()
        assert any("10000" in str(e) for e in errors)

    def test_difficulty_valid_values(self) -> None:
        """Test valid difficulty values."""
        valid_difficulties = ["easy", "moderate", "difficult", "very_difficult"]

        for difficulty in valid_difficulties:
            trip = TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                difficulty=difficulty,
            )
            assert trip.difficulty == difficulty

    def test_difficulty_invalid_value(self) -> None:
        """Test invalid difficulty value."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                difficulty="ultra_hard",  # Invalid
            )
        errors = exc_info.value.errors()
        assert any("dificultad" in str(e.get("msg", "")).lower() for e in errors)

    def test_tags_max_count(self) -> None:
        """Test tags maximum count (10)."""
        too_many_tags = [f"tag{i}" for i in range(11)]
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                tags=too_many_tags,
            )
        errors = exc_info.value.errors()
        assert any("10" in str(e) for e in errors)

    def test_tag_max_length(self) -> None:
        """Test individual tag max length (50 chars)."""
        long_tag = "A" * 51
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                tags=[long_tag],
            )
        errors = exc_info.value.errors()
        assert any("50" in str(e.get("msg", "")) for e in errors)

    def test_tag_cannot_be_empty(self) -> None:
        """Test that tags cannot be empty strings."""
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                tags=["valid", "   ", "another"],  # Empty tag (whitespace)
            )
        errors = exc_info.value.errors()
        assert any("vacías" in str(e.get("msg", "")).lower() for e in errors)

    def test_locations_max_count(self) -> None:
        """Test locations maximum count (50)."""
        too_many_locations = [LocationInput(name=f"Loc{i}") for i in range(51)]
        with pytest.raises(ValidationError) as exc_info:
            TripCreateRequest(
                title="Test",
                description="Test",
                start_date=date(2024, 5, 15),
                locations=too_many_locations,
            )
        errors = exc_info.value.errors()
        assert any("50" in str(e) for e in errors)


class TestTripUpdateRequest:
    """Test TripUpdateRequest schema."""

    def test_all_fields_optional(self) -> None:
        """Test that all fields are optional."""
        # Should not raise ValidationError
        update = TripUpdateRequest()
        assert update.title is None
        assert update.description is None
        assert update.start_date is None

    def test_partial_update_title_only(self) -> None:
        """Test updating only title."""
        update = TripUpdateRequest(title="Updated Title")
        assert update.title == "Updated Title"
        assert update.description is None

    def test_partial_update_multiple_fields(self) -> None:
        """Test updating multiple fields."""
        update = TripUpdateRequest(
            title="New Title",
            distance_km=150.5,
            difficulty="difficult",
        )
        assert update.title == "New Title"
        assert update.distance_km == 150.5
        assert update.difficulty == "difficult"

    def test_difficulty_validation(self) -> None:
        """Test difficulty validation in updates."""
        with pytest.raises(ValidationError) as exc_info:
            TripUpdateRequest(difficulty="impossible")
        errors = exc_info.value.errors()
        assert any("dificultad" in str(e.get("msg", "")).lower() for e in errors)

    def test_tags_validation(self) -> None:
        """Test tags validation in updates."""
        long_tag = "A" * 51
        with pytest.raises(ValidationError) as exc_info:
            TripUpdateRequest(tags=[long_tag])
        errors = exc_info.value.errors()
        assert any("50" in str(e.get("msg", "")) for e in errors)

    def test_client_updated_at(self) -> None:
        """Test client_updated_at for optimistic locking."""
        timestamp = datetime(2024, 12, 24, 10, 30, 0)
        update = TripUpdateRequest(
            title="Test",
            client_updated_at=timestamp,
        )
        assert update.client_updated_at == timestamp


class TestTripResponse:
    """Test TripResponse schema."""

    def test_trip_response_structure(self) -> None:
        """Test TripResponse has all required fields."""
        trip = TripResponse(
            trip_id="550e8400-e29b-41d4-a716-446655440000",
            user_id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Trip",
            description="<p>Test description</p>",
            status="published",
            start_date=date(2024, 5, 15),
            end_date=None,
            distance_km=None,
            difficulty=None,
            created_at=datetime(2024, 12, 20, 10, 30),
            updated_at=datetime(2024, 12, 22, 15, 45),
            published_at=datetime(2024, 12, 22, 15, 45),
            photos=[],
            locations=[],
            tags=[],
        )
        assert trip.trip_id == "550e8400-e29b-41d4-a716-446655440000"
        assert trip.status == "published"
        assert trip.photos == []
        assert trip.locations == []
        assert trip.tags == []

    def test_trip_response_with_nested_data(self) -> None:
        """Test TripResponse with photos, locations, and tags."""
        trip = TripResponse(
            trip_id="550e8400-e29b-41d4-a716-446655440000",
            user_id="123e4567-e89b-12d3-a456-426614174000",
            title="Test Trip",
            description="Test",
            status="published",
            start_date=date(2024, 5, 15),
            created_at=datetime(2024, 12, 20, 10, 30),
            updated_at=datetime(2024, 12, 22, 15, 45),
            photos=[
                TripPhotoResponse(
                    photo_id="photo-1",
                    photo_url="/storage/photo.jpg",
                    thumbnail_url="/storage/thumb.jpg",
                    caption="Test photo",
                    display_order=0,
                    width=1200,
                    height=800,
                )
            ],
            locations=[
                TripLocationResponse(
                    location_id="loc-1",
                    name="Baeza",
                    latitude=37.9963,
                    longitude=-3.4669,
                    sequence=0,
                )
            ],
            tags=[
                TagResponse(
                    tag_id="tag-1",
                    name="Vías Verdes",
                    normalized="vias verdes",
                    usage_count=125,
                )
            ],
        )
        assert len(trip.photos) == 1
        assert len(trip.locations) == 1
        assert len(trip.tags) == 1
        assert trip.photos[0].photo_id == "photo-1"
        assert trip.locations[0].name == "Baeza"
        assert trip.tags[0].name == "Vías Verdes"


class TestTripPhotoResponse:
    """Test TripPhotoResponse schema."""

    def test_photo_response_required_fields(self) -> None:
        """Test photo response with required fields."""
        photo = TripPhotoResponse(
            photo_id="photo-123",
            photo_url="/storage/photo.jpg",
            thumbnail_url="/storage/thumb.jpg",
            caption=None,
            display_order=0,
            width=None,
            height=None,
        )
        assert photo.photo_id == "photo-123"
        assert photo.caption is None
        assert photo.width is None

    def test_photo_response_with_optional_fields(self) -> None:
        """Test photo response with all fields."""
        photo = TripPhotoResponse(
            photo_id="photo-123",
            photo_url="/storage/photo.jpg",
            thumbnail_url="/storage/thumb.jpg",
            caption="Beautiful landscape",
            display_order=2,
            width=2000,
            height=1500,
        )
        assert photo.caption == "Beautiful landscape"
        assert photo.width == 2000
        assert photo.height == 1500
        assert photo.display_order == 2


class TestTripLocationResponse:
    """Test TripLocationResponse schema."""

    def test_location_response_without_coordinates(self) -> None:
        """Test location without geocoding."""
        loc = TripLocationResponse(
            location_id="loc-1",
            name="Camino de Santiago",
            latitude=None,
            longitude=None,
            sequence=0,
        )
        assert loc.name == "Camino de Santiago"
        assert loc.latitude is None
        assert loc.longitude is None

    def test_location_response_with_coordinates(self) -> None:
        """Test location with geocoding."""
        loc = TripLocationResponse(
            location_id="loc-1",
            name="Baeza",
            latitude=37.9963,
            longitude=-3.4669,
            sequence=1,
        )
        assert loc.latitude == 37.9963
        assert loc.longitude == -3.4669
        assert loc.sequence == 1


class TestTagResponse:
    """Test TagResponse schema."""

    def test_tag_response_structure(self) -> None:
        """Test tag response structure."""
        tag = TagResponse(
            tag_id="tag-123",
            name="Bikepacking",
            normalized="bikepacking",
            usage_count=342,
        )
        assert tag.tag_id == "tag-123"
        assert tag.name == "Bikepacking"
        assert tag.normalized == "bikepacking"
        assert tag.usage_count == 342


class TestTripListItemResponse:
    """Test TripListItemResponse schema."""

    def test_list_item_minimal(self) -> None:
        """Test trip list item with minimal data."""
        item = TripListItemResponse(
            trip_id="trip-123",
            user_id="user-456",
            title="Test Trip",
            start_date=date(2024, 5, 15),
            distance_km=None,
            status="draft",
            photo_count=0,
            tag_names=[],
            thumbnail_url=None,
            created_at=datetime(2024, 12, 20, 10, 30),
        )
        assert item.trip_id == "trip-123"
        assert item.photo_count == 0
        assert item.tag_names == []
        assert item.thumbnail_url is None

    def test_list_item_with_data(self) -> None:
        """Test trip list item with full data."""
        item = TripListItemResponse(
            trip_id="trip-123",
            user_id="user-456",
            title="Vía Verde del Aceite",
            start_date=date(2024, 5, 15),
            distance_km=127.3,
            status="published",
            photo_count=12,
            tag_names=["vías verdes", "andalucía"],
            thumbnail_url="/storage/thumb.jpg",
            created_at=datetime(2024, 12, 20, 10, 30),
        )
        assert item.distance_km == 127.3
        assert item.photo_count == 12
        assert len(item.tag_names) == 2
        assert item.thumbnail_url == "/storage/thumb.jpg"


class TestTripListResponse:
    """Test TripListResponse schema."""

    def test_trip_list_response(self) -> None:
        """Test trip list response with pagination."""
        trip_list = TripListResponse(
            trips=[
                TripListItemResponse(
                    trip_id="trip-1",
                    user_id="user-1",
                    title="Trip 1",
                    start_date=date(2024, 5, 15),
                    status="published",
                    photo_count=5,
                    created_at=datetime(2024, 12, 20, 10, 30),
                ),
                TripListItemResponse(
                    trip_id="trip-2",
                    user_id="user-1",
                    title="Trip 2",
                    start_date=date(2024, 6, 1),
                    status="published",
                    photo_count=8,
                    created_at=datetime(2024, 12, 21, 14, 0),
                ),
            ],
            total=15,
            limit=20,
            offset=0,
        )
        assert len(trip_list.trips) == 2
        assert trip_list.total == 15
        assert trip_list.limit == 20
        assert trip_list.offset == 0

    def test_empty_trip_list(self) -> None:
        """Test empty trip list."""
        trip_list = TripListResponse(
            trips=[],
            total=0,
            limit=20,
            offset=0,
        )
        assert trip_list.trips == []
        assert trip_list.total == 0
