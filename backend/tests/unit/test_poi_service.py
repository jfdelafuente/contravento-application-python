"""
Unit tests for POI Service - Feature 017 Phase 8 (T085-T086)

Tests POI creation limits and PUBLISHED trip requirements.

Coverage:
- T085: MAX_POIS_PER_TRIP = 6 enforcement
- T086: PUBLISHED trip requirement
"""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.poi import POIType
from src.models.trip import Trip, TripDifficulty, TripStatus
from src.schemas.poi import POICreateInput
from src.services.poi_service import MAX_POIS_PER_TRIP, POIService


@pytest.fixture
def mock_db_session():
    """Mock async database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def poi_service(mock_db_session):
    """POI service instance with mock session."""
    return POIService(db=mock_db_session)


@pytest.fixture
def published_trip():
    """Mock published trip."""
    return Trip(
        trip_id="trip-123",
        user_id="user-456",
        title="Test Route",
        description="Test Description" * 10,  # Min 50 chars
        start_date="2024-01-01",
        end_date="2024-01-05",
        distance_km=100.5,
        difficulty=TripDifficulty.MODERATE,
        status=TripStatus.PUBLISHED,
    )


@pytest.fixture
def draft_trip():
    """Mock draft trip."""
    return Trip(
        trip_id="trip-456",
        user_id="user-789",
        title="Draft Route",
        description="Draft Description" * 10,
        start_date="2024-02-01",
        distance_km=50.0,
        difficulty=TripDifficulty.EASY,
        status=TripStatus.DRAFT,
    )


@pytest.fixture
def poi_create_input():
    """Valid POI creation data."""
    return POICreateInput(
        name="Mirador del Valle",
        description="Vista panorámica del valle",
        poi_type=POIType.VIEWPOINT,
        latitude=40.4165,
        longitude=-3.7026,
        sequence=1,
    )


class TestPOILimitEnforcement:
    """Tests for MAX_POIS_PER_TRIP limit enforcement (T085)."""

    @pytest.mark.asyncio
    async def test_max_pois_constant_is_6(self):
        """T085: Verify MAX_POIS_PER_TRIP constant is set to 6."""
        assert MAX_POIS_PER_TRIP == 6, "MAX_POIS_PER_TRIP should be 6 (not 20)"

    @pytest.mark.asyncio
    async def test_create_poi_success_under_limit(
        self, poi_service, published_trip, poi_create_input
    ):
        """T085: POI creation succeeds when below MAX_POIS_PER_TRIP limit."""
        # Mock trip retrieval (owner check)
        with patch.object(
            poi_service, "_get_trip_with_ownership_check", return_value=published_trip
        ):
            # Mock current POI count = 5 (below limit of 6)
            with patch.object(poi_service, "_get_trip_poi_count", return_value=5):
                # Mock POI creation
                with patch.object(poi_service.db, "add"), patch.object(
                    poi_service.db, "commit"
                ), patch.object(poi_service.db, "refresh"):
                    # Should succeed
                    result = await poi_service.create_poi(
                        trip_id=published_trip.trip_id,
                        user_id=published_trip.user_id,
                        data=poi_create_input,
                    )

                    assert result is not None

    @pytest.mark.asyncio
    async def test_create_poi_fails_at_limit(self, poi_service, published_trip, poi_create_input):
        """T085: POI creation fails when MAX_POIS_PER_TRIP limit reached."""
        # Mock trip retrieval (owner check)
        with patch.object(
            poi_service, "_get_trip_with_ownership_check", return_value=published_trip
        ):
            # Mock current POI count = 6 (at limit)
            with patch.object(poi_service, "_get_trip_poi_count", return_value=MAX_POIS_PER_TRIP):
                # Should raise ValueError
                with pytest.raises(ValueError) as exc_info:
                    await poi_service.create_poi(
                        trip_id=published_trip.trip_id,
                        user_id=published_trip.user_id,
                        data=poi_create_input,
                    )

                # Verify error message in Spanish
                assert f"Máximo {MAX_POIS_PER_TRIP} POIs permitidos" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_poi_fails_above_limit(
        self, poi_service, published_trip, poi_create_input
    ):
        """T085: POI creation fails when exceeding MAX_POIS_PER_TRIP limit."""
        # Mock trip retrieval
        with patch.object(
            poi_service, "_get_trip_with_ownership_check", return_value=published_trip
        ):
            # Mock current POI count = 7 (above limit, shouldn't happen but test defensive code)
            with patch.object(poi_service, "_get_trip_poi_count", return_value=7):
                # Should raise ValueError
                with pytest.raises(ValueError) as exc_info:
                    await poi_service.create_poi(
                        trip_id=published_trip.trip_id,
                        user_id=published_trip.user_id,
                        data=poi_create_input,
                    )

                assert f"Máximo {MAX_POIS_PER_TRIP} POIs permitidos" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_sixth_poi_succeeds(self, poi_service, published_trip, poi_create_input):
        """T085: Creating the 6th POI (exactly at limit) succeeds."""
        # Mock trip retrieval
        with patch.object(
            poi_service, "_get_trip_with_ownership_check", return_value=published_trip
        ):
            # Mock current POI count = 5
            with patch.object(poi_service, "_get_trip_poi_count", return_value=5):
                # Mock database operations
                with patch.object(poi_service.db, "add"), patch.object(
                    poi_service.db, "commit"
                ), patch.object(poi_service.db, "refresh"):
                    # Should succeed (6th POI)
                    result = await poi_service.create_poi(
                        trip_id=published_trip.trip_id,
                        user_id=published_trip.user_id,
                        data=poi_create_input,
                    )

                    assert result is not None


class TestPublishedTripRequirement:
    """Tests for PUBLISHED trip requirement (T086)."""

    @pytest.mark.asyncio
    async def test_create_poi_requires_published_trip(
        self, poi_service, published_trip, poi_create_input
    ):
        """T086: POI creation requires trip status to be PUBLISHED."""
        # Mock trip retrieval with published trip
        with patch.object(
            poi_service, "_get_trip_with_ownership_check", return_value=published_trip
        ):
            # Mock current POI count = 0
            with patch.object(poi_service, "_get_trip_poi_count", return_value=0):
                # Mock database operations
                with patch.object(poi_service.db, "add"), patch.object(
                    poi_service.db, "commit"
                ), patch.object(poi_service.db, "refresh"):
                    # Should succeed with PUBLISHED trip
                    result = await poi_service.create_poi(
                        trip_id=published_trip.trip_id,
                        user_id=published_trip.user_id,
                        data=poi_create_input,
                    )

                    assert result is not None

    @pytest.mark.asyncio
    async def test_create_poi_fails_on_draft_trip(self, poi_service, draft_trip, poi_create_input):
        """T086: POI creation fails when trip status is DRAFT."""
        # Mock trip retrieval with DRAFT trip
        with patch.object(poi_service, "_get_trip_with_ownership_check", return_value=draft_trip):
            # Should raise ValueError before checking POI count
            with pytest.raises(ValueError) as exc_info:
                await poi_service.create_poi(
                    trip_id=draft_trip.trip_id,
                    user_id=draft_trip.user_id,
                    data=poi_create_input,
                )

            # Verify error message in Spanish
            assert "Solo se pueden añadir POIs a viajes publicados" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_published_check_before_limit_check(
        self, poi_service, draft_trip, poi_create_input
    ):
        """T086: PUBLISHED status check occurs before POI limit check."""
        # Mock trip retrieval with DRAFT trip
        with patch.object(poi_service, "_get_trip_with_ownership_check", return_value=draft_trip):
            # Mock POI count would be at limit, but should fail on status first
            with patch.object(
                poi_service, "_get_trip_poi_count", return_value=MAX_POIS_PER_TRIP
            ) as mock_count:
                # Should raise ValueError on status check
                with pytest.raises(ValueError) as exc_info:
                    await poi_service.create_poi(
                        trip_id=draft_trip.trip_id,
                        user_id=draft_trip.user_id,
                        data=poi_create_input,
                    )

                # Verify status error, not limit error
                assert "Solo se pueden añadir POIs a viajes publicados" in str(exc_info.value)
                # Verify POI count was not called (status check failed first)
                mock_count.assert_not_called()


class TestPOIServiceIntegration:
    """Integration tests for POI service validations."""

    @pytest.mark.asyncio
    async def test_validation_order(self, poi_service, draft_trip, poi_create_input):
        """Verify validation order: ownership → status → limit."""
        # Mock trip retrieval with DRAFT trip (fails status check)
        with patch.object(poi_service, "_get_trip_with_ownership_check", return_value=draft_trip):
            # Mock POI count (should not be called)
            with patch.object(poi_service, "_get_trip_poi_count") as mock_count:
                with pytest.raises(ValueError) as exc_info:
                    await poi_service.create_poi(
                        trip_id=draft_trip.trip_id,
                        user_id=draft_trip.user_id,
                        data=poi_create_input,
                    )

                # Status error message
                assert "publicados" in str(exc_info.value)
                # POI count never called (failed earlier)
                mock_count.assert_not_called()

    @pytest.mark.asyncio
    async def test_limit_error_message_includes_count(
        self, poi_service, published_trip, poi_create_input
    ):
        """Verify limit error message includes MAX_POIS_PER_TRIP value."""
        with patch.object(
            poi_service, "_get_trip_with_ownership_check", return_value=published_trip
        ):
            with patch.object(poi_service, "_get_trip_poi_count", return_value=MAX_POIS_PER_TRIP):
                with pytest.raises(ValueError) as exc_info:
                    await poi_service.create_poi(
                        trip_id=published_trip.trip_id,
                        user_id=published_trip.user_id,
                        data=poi_create_input,
                    )

                error_message = str(exc_info.value)
                # Verify message includes the exact limit
                assert "6" in error_message
                assert "Máximo" in error_message
                assert "POIs permitidos" in error_message
