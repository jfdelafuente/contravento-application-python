"""
Shared fixtures for Feature 013 - Public Trips Feed tests.

These fixtures are used by both unit and integration tests.
"""

from datetime import UTC, date, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.trip import Trip, TripLocation, TripPhoto, TripStatus
from src.models.user import User, UserProfile


@pytest.fixture
async def public_user(db_session: AsyncSession) -> User:
    """Create a user with public profile visibility."""
    user = User(
        username="public_user",
        email="public@example.com",
        hashed_password="hashedpass",
        is_verified=True,
        profile_visibility="public",
    )
    db_session.add(user)
    await db_session.flush()

    # Add profile
    profile = UserProfile(user_id=user.id)
    db_session.add(profile)

    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def private_user(db_session: AsyncSession) -> User:
    """Create a user with private profile visibility."""
    user = User(
        username="private_user",
        email="private@example.com",
        hashed_password="hashedpass",
        is_verified=True,
        profile_visibility="private",
    )
    db_session.add(user)
    await db_session.flush()

    # Add profile
    profile = UserProfile(user_id=user.id)
    db_session.add(profile)

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
    await db_session.flush()

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
async def published_trip_public_user_2(db_session: AsyncSession, public_user: User) -> Trip:
    """Create a second published trip for public user (for pagination tests)."""
    trip = Trip(
        user_id=public_user.id,
        title="Public Trip 2",
        description="Second trip for pagination",
        start_date=date(2024, 6, 15),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
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


@pytest.fixture
async def published_trip_with_photos(db_session: AsyncSession, public_user: User) -> Trip:
    """Create a published trip with multiple photos."""
    trip = Trip(
        user_id=public_user.id,
        title="Trip With Photos",
        description="Trip with photo gallery",
        start_date=date(2024, 9, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.flush()

    # Add photos (use actual column names: thumb_url, order)
    photo1 = TripPhoto(
        trip_id=trip.trip_id,
        photo_url="/storage/trip_photos/2024/09/trip1_photo1.jpg",
        thumb_url="/storage/trip_photos/2024/09/trip1_photo1_thumb.jpg",
        order=0,  # First photo
    )
    photo2 = TripPhoto(
        trip_id=trip.trip_id,
        photo_url="/storage/trip_photos/2024/09/trip1_photo2.jpg",
        thumb_url="/storage/trip_photos/2024/09/trip1_photo2_thumb.jpg",
        order=1,  # Second photo
    )
    db_session.add(photo1)
    db_session.add(photo2)

    await db_session.commit()
    await db_session.refresh(trip)
    return trip


@pytest.fixture
async def published_trip_with_location(db_session: AsyncSession, public_user: User) -> Trip:
    """Create a published trip with location."""
    trip = Trip(
        user_id=public_user.id,
        title="Trip With Location",
        description="Trip with GPS coordinates",
        start_date=date(2024, 10, 1),
        status=TripStatus.PUBLISHED,
        published_at=datetime.now(UTC),
    )
    db_session.add(trip)
    await db_session.flush()

    # Add location
    location = TripLocation(
        trip_id=trip.trip_id,
        name="Barcelona, Spain",
        latitude=41.3851,
        longitude=2.1734,
        sequence=0,
    )
    db_session.add(location)

    await db_session.commit()
    await db_session.refresh(trip)
    return trip
