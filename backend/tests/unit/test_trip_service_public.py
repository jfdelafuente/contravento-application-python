"""
Unit tests for TripService public feed methods (Feature 013).

Tests privacy filtering, eager loading, and pagination logic.
"""

from datetime import UTC, date, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import Trip, TripLocation, TripPhoto, TripStatus
from src.models.user import User
from src.services.trip_service import TripService


@pytest.fixture
async def public_user(db_session: AsyncSession) -> User:
    """Create a user with public profile visibility."""
    user = User(
        username="public_user",
        email="public@example.com",
        hashed_password="dummy",
        profile_visibility="public",
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def private_user(db_session: AsyncSession) -> User:
    """Create a user with private profile visibility."""
    user = User(
        username="private_user",
        email="private@example.com",
        hashed_password="dummy",
        profile_visibility="private",
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def published_trip_public_user(db_session: AsyncSession, public_user: User) -> Trip:
    """Create a published trip for public user."""
    trip = Trip(
        user_id=public_user.id,
        title="Public Trip Published",
        description="This should appear in public feed",
        start_date=date(2024, 6, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.flush()  # Get trip_id

    # Add photo (use actual column names: thumb_url, order)
    photo = TripPhoto(
        trip_id=trip.trip_id,
        photo_url="/storage/photos/public_trip.jpg",
        thumb_url="/storage/photos/public_trip_thumb.jpg",
        order=0,
    )
    db_session.add(photo)

    # Add location
    location = TripLocation(
        trip_id=trip.trip_id,
        name="Madrid, Spain",
        sequence=0,
    )
    db_session.add(location)

    await db_session.commit()
    await db_session.refresh(trip)
    return trip


@pytest.fixture
async def draft_trip_public_user(db_session: AsyncSession, public_user: User) -> Trip:
    """Create a draft trip for public user."""
    trip = Trip(
        user_id=public_user.id,
        title="Public User Draft",
        description="This should NOT appear (draft)",
        start_date=date(2024, 7, 1),
        status=TripStatus.DRAFT,
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


@pytest.fixture
async def published_trip_private_user(db_session: AsyncSession, private_user: User) -> Trip:
    """Create a published trip for private user."""
    trip = Trip(
        user_id=private_user.id,
        title="Private User Published",
        description="This should NOT appear (private profile)",
        start_date=date(2024, 8, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.commit()
    await db_session.refresh(trip)
    return trip


@pytest.mark.asyncio
async def test_get_public_trips_filters_by_privacy(
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    draft_trip_public_user: Trip,
    published_trip_private_user: Trip,
):
    """
    Test get_public_trips() only returns PUBLISHED trips from PUBLIC profiles.

    Privacy filtering requirements (FR-003):
    - Only trips from users with profile_visibility='public'
    - Only trips with status=PUBLISHED
    """
    service = TripService(db_session)

    trips, total = await service.get_public_trips(page=1, limit=20)

    # Should only return the published trip from public user
    assert total == 1, f"Expected 1 trip, got {total}"
    assert len(trips) == 1
    assert trips[0].trip_id == published_trip_public_user.trip_id
    assert trips[0].title == "Public Trip Published"


@pytest.mark.asyncio
async def test_get_public_trips_excludes_drafts(
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    draft_trip_public_user: Trip,
):
    """Test get_public_trips() excludes DRAFT trips even from public users."""
    service = TripService(db_session)

    trips, total = await service.get_public_trips(page=1, limit=20)

    assert total == 1
    assert all(trip.status == TripStatus.PUBLISHED for trip in trips)


@pytest.mark.asyncio
async def test_get_public_trips_excludes_private_profiles(
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    published_trip_private_user: Trip,
):
    """Test get_public_trips() excludes trips from private profiles."""
    service = TripService(db_session)

    trips, total = await service.get_public_trips(page=1, limit=20)

    assert total == 1
    # Verify user visibility is public (via join filter)
    assert trips[0].user_id == published_trip_public_user.user_id


@pytest.mark.asyncio
async def test_get_public_trips_pagination(
    db_session: AsyncSession,
    public_user: User,
):
    """Test get_public_trips() pagination works correctly."""
    # Create 25 published trips for public user
    for i in range(25):
        trip = Trip(
            user_id=public_user.id,
            title=f"Trip {i+1:02d}",
            description=f"Description {i+1}",
            start_date=date(2024, 6, i + 1 if i < 30 else 30),
            status=TripStatus.PUBLISHED,
            published_at=datetime(2024, 6, 1, 12, i),  # Different timestamps for sorting
        )
        db_session.add(trip)
    await db_session.commit()

    service = TripService(db_session)

    # Page 1 should have 20 trips
    trips_page1, total = await service.get_public_trips(page=1, limit=20)
    assert total == 25
    assert len(trips_page1) == 20

    # Page 2 should have 5 trips
    trips_page2, total = await service.get_public_trips(page=2, limit=20)
    assert total == 25
    assert len(trips_page2) == 5

    # Verify no overlap between pages
    page1_ids = {trip.trip_id for trip in trips_page1}
    page2_ids = {trip.trip_id for trip in trips_page2}
    assert len(page1_ids & page2_ids) == 0, "Pages should not overlap"


@pytest.mark.asyncio
async def test_get_public_trips_sorted_by_published_at_desc(
    db_session: AsyncSession,
    public_user: User,
):
    """Test get_public_trips() returns trips sorted by published_at DESC (newest first)."""
    trip1 = Trip(
        user_id=public_user.id,
        title="Oldest Trip",
        description="Published first",
        start_date=date(2024, 1, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 1, 1, 10, 0, 0),
    )
    trip2 = Trip(
        user_id=public_user.id,
        title="Newest Trip",
        description="Published last",
        start_date=date(2024, 3, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 3, 1, 15, 0, 0),
    )
    trip3 = Trip(
        user_id=public_user.id,
        title="Middle Trip",
        description="Published middle",
        start_date=date(2024, 2, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime(2024, 2, 1, 12, 0, 0),
    )

    db_session.add_all([trip1, trip2, trip3])
    await db_session.commit()

    service = TripService(db_session)
    trips, total = await service.get_public_trips(page=1, limit=20)

    assert total == 3
    assert trips[0].title == "Newest Trip", "First trip should be newest"
    assert trips[1].title == "Middle Trip"
    assert trips[2].title == "Oldest Trip", "Last trip should be oldest"


@pytest.mark.asyncio
async def test_get_public_trips_eager_loads_relationships(
    db_session: AsyncSession,
    published_trip_public_user: Trip,
):
    """
    Test get_public_trips() eager loads user, photos, locations to prevent N+1 queries.

    Performance requirement (SC-004): Query should use eager loading.
    """
    service = TripService(db_session)

    trips, total = await service.get_public_trips(page=1, limit=20)

    assert len(trips) == 1
    trip = trips[0]

    # Access relationships without triggering new queries
    # (if not eager loaded, this would raise DetachedInstanceError in strict mode)
    assert trip.user is not None, "User should be eager loaded"
    assert trip.user.username == "public_user"

    assert len(trip.photos) > 0, "Photos should be eager loaded"
    assert trip.photos[0].photo_url == "/storage/photos/public_trip.jpg"

    assert len(trip.locations) > 0, "Locations should be eager loaded"
    assert trip.locations[0].name == "Madrid, Spain"


@pytest.mark.asyncio
async def test_get_public_trips_empty_result(db_session: AsyncSession):
    """Test get_public_trips() handles empty database gracefully."""
    service = TripService(db_session)

    trips, total = await service.get_public_trips(page=1, limit=20)

    assert total == 0
    assert trips == []


@pytest.mark.asyncio
async def test_count_public_trips(
    db_session: AsyncSession,
    published_trip_public_user: Trip,
    draft_trip_public_user: Trip,
    published_trip_private_user: Trip,
):
    """Test count_public_trips() returns accurate count with privacy filters."""
    service = TripService(db_session)

    count = await service.count_public_trips()

    # Should only count published trips from public users
    assert count == 1


@pytest.mark.asyncio
async def test_get_public_trips_profile_visibility_transition(
    db_session: AsyncSession,
    public_user: User,
    published_trip_public_user: Trip,
):
    """
    Test privacy transition: user changes profile public→private.

    Edge case (EC-002): Trips should disappear from feed when user changes to private.
    """
    service = TripService(db_session)

    # Initially visible (public user)
    trips, total = await service.get_public_trips(page=1, limit=20)
    assert total == 1

    # Change user to private
    public_user.profile_visibility = "private"
    await db_session.commit()

    # Trip should no longer appear
    trips, total = await service.get_public_trips(page=1, limit=20)
    assert total == 0, "Trip should disappear when user changes to private"


@pytest.mark.asyncio
async def test_get_public_trips_loads_all_photos(
    db_session: AsyncSession,
    public_user: User,
):
    """Test get_public_trips() eager loads all photos (will use first in API response)."""
    trip = Trip(
        user_id=public_user.id,
        title="Multi-Photo Trip",
        description="Has multiple photos",
        start_date=date(2024, 6, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.flush()

    # Add 3 photos (use actual column names)
    photo1 = TripPhoto(
        trip_id=trip.trip_id,
        photo_url="/storage/photo1.jpg",
        thumb_url="/storage/photo1_thumb.jpg",
        order=0,  # First photo
    )
    photo2 = TripPhoto(
        trip_id=trip.trip_id,
        photo_url="/storage/photo2.jpg",
        thumb_url="/storage/photo2_thumb.jpg",
        order=1,
    )
    photo3 = TripPhoto(
        trip_id=trip.trip_id,
        photo_url="/storage/photo3.jpg",
        thumb_url="/storage/photo3_thumb.jpg",
        order=2,
    )
    db_session.add_all([photo1, photo2, photo3])
    await db_session.commit()

    service = TripService(db_session)
    trips, total = await service.get_public_trips(page=1, limit=20)

    assert len(trips) == 1
    # All photos are loaded (API response will only use first)
    assert len(trips[0].photos) == 3, "All photos should be eager loaded"
    # Photos should be ordered by order field
    assert trips[0].photos[0].display_order == 0
    assert trips[0].photos[0].photo_url == "/storage/photo1.jpg"


@pytest.mark.asyncio
async def test_get_public_trips_loads_all_locations(
    db_session: AsyncSession,
    public_user: User,
):
    """Test get_public_trips() eager loads all locations (will use first in API response)."""
    trip = Trip(
        user_id=public_user.id,
        title="Multi-Location Trip",
        description="Has multiple locations",
        start_date=date(2024, 6, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.flush()

    # Add 3 locations
    loc1 = TripLocation(
        trip_id=trip.trip_id,
        name="Start Point",
        sequence=0,  # First location
    )
    loc2 = TripLocation(
        trip_id=trip.trip_id,
        name="Waypoint",
        sequence=1,
    )
    loc3 = TripLocation(
        trip_id=trip.trip_id,
        name="End Point",
        sequence=2,
    )
    db_session.add_all([loc1, loc2, loc3])
    await db_session.commit()

    service = TripService(db_session)
    trips, total = await service.get_public_trips(page=1, limit=20)

    assert len(trips) == 1
    # All locations are loaded (API response will only use first)
    assert len(trips[0].locations) == 3, "All locations should be eager loaded"
    # Locations should be ordered by sequence
    assert trips[0].locations[0].sequence == 0
    assert trips[0].locations[0].name == "Start Point"
