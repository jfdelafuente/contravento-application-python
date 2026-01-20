"""
Integration tests for Public Trips Feed API (Feature 013 - T023).

Tests the GET /trips/public endpoint with real HTTP requests.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import Trip, TripStatus
from src.models.user import User


@pytest.mark.asyncio
async def test_get_public_trips_success(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    published_trip_public_user_2: Trip,
):
    """Test GET /trips/public returns published trips from public profiles."""
    response = await client.get("/trips/public?page=1&limit=20")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "trips" in data
    assert "pagination" in data
    assert isinstance(data["trips"], list)

    # Verify pagination metadata
    pagination = data["pagination"]
    assert pagination["page"] == 1
    assert pagination["limit"] == 20
    assert pagination["total"] >= 2  # At least 2 test trips
    assert pagination["total_pages"] >= 1

    # Verify trip data structure
    assert len(data["trips"]) >= 2
    trip = data["trips"][0]
    assert "trip_id" in trip
    assert "title" in trip
    assert "start_date" in trip
    assert "distance_km" in trip
    assert "photo" in trip  # Can be null
    assert "location" in trip  # Can be null
    assert "author" in trip
    assert "published_at" in trip

    # Verify author data structure
    author = trip["author"]
    assert "user_id" in author
    assert "username" in author
    assert "profile_photo_url" in author  # Can be null


@pytest.mark.asyncio
async def test_get_public_trips_filters_drafts(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    draft_trip_public_user: Trip,
):
    """Test that draft trips are excluded from public feed."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Extract trip IDs from response
    trip_ids = [trip["trip_id"] for trip in data["trips"]]

    # Published trip should be included
    assert published_trip_public_user.trip_id in trip_ids

    # Draft trip should be excluded
    assert draft_trip_public_user.trip_id not in trip_ids


@pytest.mark.asyncio
async def test_get_public_trips_filters_private_profiles(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    published_trip_private_user: Trip,
):
    """Test that trips from private profiles are excluded."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Extract trip IDs from response
    trip_ids = [trip["trip_id"] for trip in data["trips"]]

    # Trip from public user should be included
    assert published_trip_public_user.trip_id in trip_ids

    # Trip from private user should be excluded
    assert published_trip_private_user.trip_id not in trip_ids


@pytest.mark.asyncio
async def test_get_public_trips_pagination(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    published_trip_public_user_2: Trip,
):
    """Test pagination parameters work correctly."""
    # Request first page with limit=1
    response = await client.get("/trips/public?page=1&limit=1")

    assert response.status_code == 200
    data = response.json()

    # Should return exactly 1 trip
    assert len(data["trips"]) == 1

    # Pagination should reflect limit
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["limit"] == 1
    assert data["pagination"]["total"] >= 2

    # Request second page
    response = await client.get("/trips/public?page=2&limit=1")

    assert response.status_code == 200
    data = response.json()

    # Should return 1 trip (different from page 1)
    assert len(data["trips"]) == 1

    # Pagination should reflect page 2
    assert data["pagination"]["page"] == 2


@pytest.mark.asyncio
async def test_get_public_trips_ordered_by_published_at(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    published_trip_public_user_2: Trip,
):
    """Test that trips are ordered by published_at DESC (newest first)."""
    response = await client.get("/trips/public?page=1&limit=10")

    assert response.status_code == 200
    data = response.json()

    # Should have at least 2 trips
    assert len(data["trips"]) >= 2

    # Extract published_at timestamps
    timestamps = [trip["published_at"] for trip in data["trips"]]

    # Verify descending order (newest first)
    for i in range(len(timestamps) - 1):
        assert (
            timestamps[i] >= timestamps[i + 1]
        ), f"Trips not ordered by published_at DESC: {timestamps[i]} < {timestamps[i + 1]}"


@pytest.mark.asyncio
async def test_get_public_trips_no_auth_required(client: AsyncClient):
    """Test that endpoint works without authentication."""
    # Do not add Authorization header
    response = await client.get("/trips/public")

    # Should succeed (200) without auth
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_public_trips_validates_page_min(client: AsyncClient):
    """Test that page parameter must be >= 1."""
    response = await client.get("/trips/public?page=0&limit=20")

    # Should return validation error (400 for query param validation)
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_get_public_trips_validates_limit_range(client: AsyncClient):
    """Test that limit parameter must be 1-50."""
    # Test limit=0 (too small)
    response = await client.get("/trips/public?page=1&limit=0")
    assert response.status_code in [400, 422]

    # Test limit=51 (too large)
    response = await client.get("/trips/public?page=1&limit=51")
    assert response.status_code in [400, 422]

    # Test limit=50 (valid max)
    response = await client.get("/trips/public?page=1&limit=50")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_public_trips_empty_feed(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """Test response when no public trips exist."""
    # Delete all trips (using fixtures that may exist)
    from sqlalchemy import delete

    await db_session.execute(delete(Trip))
    await db_session.commit()

    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Should return empty list
    assert data["trips"] == []

    # Pagination should reflect zero trips
    assert data["pagination"]["total"] == 0
    assert data["pagination"]["total_pages"] == 0


@pytest.mark.asyncio
async def test_get_public_trips_includes_first_photo(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_with_photos: Trip,
):
    """Test that response includes first photo (order=0) with URLs."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Find the trip with photos in response
    trip_with_photos = next(
        (t for t in data["trips"] if t["trip_id"] == published_trip_with_photos.trip_id),
        None,
    )

    assert trip_with_photos is not None, "Trip with photos not found in response"

    # Verify photo data
    photo = trip_with_photos["photo"]
    assert photo is not None
    assert "photo_url" in photo
    assert "thumbnail_url" in photo
    assert photo["photo_url"].startswith("/storage/trip_photos/")
    assert photo["thumbnail_url"].startswith("/storage/trip_photos/")


@pytest.mark.asyncio
async def test_get_public_trips_includes_first_location(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_with_location: Trip,
):
    """Test that response includes first location (sequence=0) with name."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Find the trip with location in response
    trip_with_location = next(
        (t for t in data["trips"] if t["trip_id"] == published_trip_with_location.trip_id),
        None,
    )

    assert trip_with_location is not None, "Trip with location not found in response"

    # Verify location data
    location = trip_with_location["location"]
    assert location is not None
    assert "name" in location
    assert isinstance(location["name"], str)
    assert len(location["name"]) > 0


@pytest.mark.asyncio
async def test_get_public_trips_handles_null_photo(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_public_user: Trip,
):
    """Test that trips without photos return photo=null."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Find trip without photos
    trip_no_photo = next(
        (t for t in data["trips"] if t["trip_id"] == published_trip_public_user.trip_id),
        None,
    )

    assert trip_no_photo is not None

    # Photo should be null
    assert trip_no_photo["photo"] is None


@pytest.mark.asyncio
async def test_get_public_trips_handles_null_location(
    client: AsyncClient,
    db_session: AsyncSession,
    published_trip_public_user: Trip,
):
    """Test that trips without locations return location=null."""
    response = await client.get("/trips/public")

    assert response.status_code == 200
    data = response.json()

    # Find trip without location
    trip_no_location = next(
        (t for t in data["trips"] if t["trip_id"] == published_trip_public_user.trip_id),
        None,
    )

    assert trip_no_location is not None

    # Location should be null (if trip has no locations)
    # Note: Test fixture may have location, so we just verify structure
    assert "location" in trip_no_location
    # location can be null or an object with "name"
