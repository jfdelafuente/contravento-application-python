"""
Test helper functions for ContraVento tests.

Provides utilities for creating test data, making API requests,
and common test operations.

Usage:
    from tests.helpers import create_user, create_trip, upload_photo

    async def test_something(db_session):
        user = await create_user(db_session, username="testuser")
        trip = await create_trip(db_session, user_id=user.id)
"""

from datetime import date, datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.user import User, UserProfile, UserRole
from src.models.trip import Trip, TripStatus, TripDifficulty
from src.models.tag import Tag
from src.utils.security import hash_password


async def create_user(
    db: AsyncSession,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "TestPass123!",
    role: UserRole = UserRole.USER,
    is_verified: bool = True,
    is_active: bool = True,
    **profile_fields,
) -> User:
    """
    Create a test user with profile.

    Args:
        db: Database session
        username: Username (must be unique)
        email: Email (must be unique)
        password: Plain text password (will be hashed)
        role: User role (USER or ADMIN)
        is_verified: Email verification status
        is_active: Account active status
        **profile_fields: Additional profile fields (full_name, bio, location, cycling_type)

    Returns:
        User: Created user instance with profile

    Example:
        user = await create_user(
            db,
            username="maria",
            email="maria@example.com",
            full_name="María García",
            bio="Ciclista de montaña",
            cycling_type="mountain"
        )
    """
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_verified=is_verified,
        is_active=is_active,
    )
    db.add(user)
    await db.flush()

    # Create profile
    profile = UserProfile(user_id=user.id, **profile_fields)
    db.add(profile)

    await db.commit()
    await db.refresh(user)

    return user


async def create_trip(
    db: AsyncSession,
    user_id: UUID,
    title: str = "Test Trip",
    description: str = "Test trip description with at least 50 characters for validation.",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    distance_km: float = 100.0,
    difficulty: TripDifficulty = TripDifficulty.MODERATE,
    status: TripStatus = TripStatus.DRAFT,
    tags: Optional[List[str]] = None,
) -> Trip:
    """
    Create a test trip.

    Args:
        db: Database session
        user_id: User who owns the trip
        title: Trip title
        description: Trip description (must be ≥50 chars for published trips)
        start_date: Start date (defaults to 2025-06-01)
        end_date: End date (defaults to None)
        distance_km: Distance in kilometers
        difficulty: Trip difficulty (easy/moderate/hard)
        status: Trip status (DRAFT/PUBLISHED)
        tags: List of tag names to assign

    Returns:
        Trip: Created trip instance

    Example:
        trip = await create_trip(
            db,
            user_id=user.id,
            title="Bikepacking Pirineos",
            description="Ruta de 5 días por los Pirineos con más de 50 caracteres.",
            distance_km=320.5,
            difficulty=TripDifficulty.HARD,
            status=TripStatus.PUBLISHED,
            tags=["bikepacking", "montaña"]
        )
    """
    if start_date is None:
        start_date = date(2025, 6, 1)

    trip = Trip(
        user_id=user_id,
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        distance_km=distance_km,
        difficulty=difficulty,
        status=status,
    )
    db.add(trip)
    await db.flush()

    # Add tags if provided
    if tags:
        for tag_name in tags:
            tag = await get_or_create_tag(db, tag_name)
            trip.tags.append(tag)

    await db.commit()
    await db.refresh(trip)

    return trip


async def get_or_create_tag(db: AsyncSession, tag_name: str) -> Tag:
    """
    Get existing tag or create new one.

    Args:
        db: Database session
        tag_name: Tag name (will be normalized to lowercase)

    Returns:
        Tag: Existing or newly created tag

    Example:
        tag = await get_or_create_tag(db, "bikepacking")
    """
    normalized = tag_name.lower()

    # Try to find existing tag
    result = await db.execute(select(Tag).where(Tag.normalized == normalized))
    tag = result.scalar_one_or_none()

    if tag:
        return tag

    # Create new tag
    tag = Tag(name=tag_name, normalized=normalized, usage_count=0)
    db.add(tag)
    await db.flush()

    return tag


async def create_trip_with_photos(
    db: AsyncSession,
    user_id: UUID,
    num_photos: int = 3,
    **trip_kwargs,
) -> Trip:
    """
    Create a test trip with photo metadata.

    Note: This creates photo records in the database, but does not
    upload actual files. Use upload_photo() for file upload tests.

    Args:
        db: Database session
        user_id: User who owns the trip
        num_photos: Number of photos to create (default: 3)
        **trip_kwargs: Additional trip fields (passed to create_trip)

    Returns:
        Trip: Created trip with photos

    Example:
        trip = await create_trip_with_photos(
            db,
            user_id=user.id,
            num_photos=5,
            title="Trip with Photos"
        )
    """
    from src.models.trip_photo import TripPhoto

    trip = await create_trip(db, user_id=user_id, **trip_kwargs)

    # Create photo records
    for i in range(num_photos):
        photo = TripPhoto(
            trip_id=trip.trip_id,
            photo_url=f"/storage/trip_photos/test/sample_{i+1}.jpg",
            file_size=500000,  # 500KB
            width=1200,
            height=800,
            order=i,
            caption=f"Test photo {i+1}",
        )
        db.add(photo)

    await db.commit()
    await db.refresh(trip)

    return trip


def get_sample_photo_path(filename: str = "sample_1.jpg") -> Path:
    """
    Get path to sample photo in fixtures.

    Args:
        filename: Photo filename (sample_1.jpg, sample_2.jpg, sample_large.jpg)

    Returns:
        Path: Absolute path to sample photo

    Example:
        photo_path = get_sample_photo_path("sample_large.jpg")
        with open(photo_path, "rb") as f:
            response = await client.post("/trips/123/photos", files={"file": f})
    """
    return Path(__file__).parent / "fixtures" / "photos" / filename


async def load_fixture_users(db: AsyncSession, fixture_data: Dict[str, Any]) -> List[User]:
    """
    Load users from fixture data.

    Args:
        db: Database session
        fixture_data: Parsed JSON from users.json

    Returns:
        List[User]: Created users

    Example:
        from tests.conftest import load_json_fixture

        async def test_something(db_session, load_json_fixture):
            users_data = load_json_fixture("users.json")
            users = await load_fixture_users(db_session, users_data)
            assert len(users) == 4
    """
    users = []

    for user_data in fixture_data.get("users", []):
        profile_data = user_data.pop("profile", {})

        user = await create_user(
            db,
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            role=UserRole[user_data["role"]],
            is_verified=user_data["is_verified"],
            is_active=user_data["is_active"],
            **profile_data,
        )
        users.append(user)

    return users


async def load_fixture_trips(
    db: AsyncSession, fixture_data: Dict[str, Any], default_user_id: UUID
) -> List[Trip]:
    """
    Load trips from fixture data.

    Args:
        db: Database session
        fixture_data: Parsed JSON from trips.json
        default_user_id: User ID to assign trips to

    Returns:
        List[Trip]: Created trips

    Example:
        from tests.conftest import load_json_fixture

        async def test_something(db_session, test_user, load_json_fixture):
            trips_data = load_json_fixture("trips.json")
            trips = await load_fixture_trips(db_session, trips_data, test_user.id)
            assert len(trips) == 5
    """
    trips = []

    for trip_data in fixture_data.get("trips", []):
        # Remove nested objects (will be added separately)
        trip_data.pop("locations", None)
        trip_data.pop("photos", None)
        trip_data.pop("id", None)  # Remove fixture ID

        # Convert string dates to date objects
        if "start_date" in trip_data and trip_data["start_date"]:
            trip_data["start_date"] = datetime.strptime(trip_data["start_date"], "%Y-%m-%d").date()
        if "end_date" in trip_data and trip_data["end_date"]:
            trip_data["end_date"] = datetime.strptime(trip_data["end_date"], "%Y-%m-%d").date()

        # Convert status and difficulty to enums
        trip_data["status"] = TripStatus[trip_data["status"]]
        trip_data["difficulty"] = TripDifficulty[trip_data["difficulty"]]

        trip = await create_trip(db, user_id=default_user_id, **trip_data)
        trips.append(trip)

    return trips


# Export commonly used helpers
__all__ = [
    "create_user",
    "create_trip",
    "create_trip_with_photos",
    "get_or_create_tag",
    "get_sample_photo_path",
    "load_fixture_users",
    "load_fixture_trips",
]
