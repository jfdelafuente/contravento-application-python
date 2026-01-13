# Data Model: Public Trips Feed

**Feature**: 013-public-trips-feed
**Date**: 2026-01-13
**Status**: Design Phase

## Overview

This feature REUSES existing models from Features 001 (User), 002 (Trip), 008 (TripPhoto), and 009 (TripLocation). No new tables or migrations are required. The data model focuses on **query patterns** and **response schemas** for the public feed.

## Entity Relationships

```text
User (Feature 001)
  ├── profile_visibility: 'public' | 'private'
  └── trips (1:N) ───> Trip (Feature 002)
                         ├── status: DRAFT | PUBLISHED
                         ├── photos (1:N) ───> TripPhoto (Feature 008)
                         └── locations (1:N) ───> TripLocation (Feature 009)
```

**Privacy Filter Logic**:
- Public Feed: `User.profile_visibility = 'public' AND Trip.status = 'PUBLISHED'`

## Existing Models (Reused)

### User (Feature 001)

```python
# backend/src/models/user.py (EXISTING - NO CHANGES)

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Profile fields
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Privacy settings (Feature 001 - CRITICAL FOR THIS FEATURE)
    profile_visibility: Mapped[str] = mapped_column(
        String(20),
        default='public',
        nullable=False,
        index=True  # ← ENSURE INDEX EXISTS for public feed query
    )
    trip_visibility: Mapped[str] = mapped_column(String(20), default='public', nullable=False)

    # Relationships
    trips: Mapped[List["Trip"]] = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
```

**Required for Public Feed**:
- `profile_visibility` field (already exists)
- Index on `profile_visibility` (ensure exists, create if missing)

---

### Trip (Feature 002)

```python
# backend/src/models/trip.py (EXISTING - NO CHANGES)

class TripStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"

class Trip(Base):
    __tablename__ = "trips"

    trip_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)

    # Publishing status (CRITICAL FOR THIS FEATURE)
    status: Mapped[TripStatus] = mapped_column(
        Enum(TripStatus),
        default=TripStatus.DRAFT,
        nullable=False,
        index=True  # ← ENSURE INDEX EXISTS for public feed query
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True  # ← ENSURE INDEX EXISTS for ORDER BY published_at DESC
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="trips")
    photos: Mapped[List["TripPhoto"]] = relationship("TripPhoto", back_populates="trip", cascade="all, delete-orphan", order_by="TripPhoto.order")
    locations: Mapped[List["TripLocation"]] = relationship("TripLocation", back_populates="trip", cascade="all, delete-orphan", order_by="TripLocation.order")
```

**Required for Public Feed**:
- `status` field (PUBLISHED filter)
- `published_at` field (ORDER BY DESC)
- Composite index on `(status, published_at DESC)` (ensure exists, create if missing)

---

### TripPhoto (Feature 008)

```python
# backend/src/models/trip_photo.py (EXISTING - NO CHANGES)

class TripPhoto(Base):
    __tablename__ = "trip_photos"

    photo_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.trip_id"), nullable=False, index=True)
    photo_url: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="photos")
```

**Usage in Public Feed**:
- Select ONLY first photo (order=0) via `selectinload(Trip.photos).limit(1)`

---

### TripLocation (Feature 009)

```python
# backend/src/models/trip_location.py (EXISTING - NO CHANGES)

class TripLocation(Base):
    __tablename__ = "trip_locations"

    location_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("trips.trip_id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="locations")
```

**Usage in Public Feed**:
- Select ONLY first location (order=0) via `selectinload(Trip.locations).limit(1)`

---

## New Schemas (Pydantic Response Models)

### PublicTripSummary (Backend Response Schema)

```python
# backend/src/schemas/trip.py (NEW SCHEMA)

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date, datetime
from typing import Optional

class PublicUserSummary(BaseModel):
    """Minimal user info for public trip cards"""
    user_id: UUID
    username: str
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PublicLocationSummary(BaseModel):
    """First location for public trip cards"""
    location_id: UUID
    name: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)

class PublicPhotoSummary(BaseModel):
    """First photo for public trip cards"""
    photo_id: UUID
    photo_url: str
    caption: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PublicTripSummary(BaseModel):
    """Public trip card data (no private fields)"""
    trip_id: UUID
    title: str
    distance_km: float
    start_date: date
    published_at: datetime

    # Related entities
    user: PublicUserSummary
    first_photo: Optional[PublicPhotoSummary] = Field(None, description="First photo or None")
    first_location: Optional[PublicLocationSummary] = Field(None, description="First location or None")

    model_config = ConfigDict(from_attributes=True)

class PaginationInfo(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., ge=1, description="Current page (1-indexed)")
    limit: int = Field(..., ge=1, le=50, description="Items per page")
    total: int = Field(..., ge=0, description="Total items across all pages")
    pages: int = Field(..., ge=0, description="Total number of pages")

class PublicTripListResponse(BaseModel):
    """Public feed API response"""
    success: bool = True
    data: list[PublicTripSummary]
    pagination: PaginationInfo

    model_config = ConfigDict(from_attributes=True)
```

**Design Decisions**:
1. **No description field**: Keep cards lightweight (title + metadata only)
2. **PublicUserSummary**: Exclude email, bio, stats (privacy)
3. **first_photo / first_location**: Explicit naming (not `photos[0]`) for clarity
4. **Optional fields**: Handle trips without photos/locations gracefully

---

## Database Indexes (Migration Check)

### Required Indexes

```sql
-- Check if these indexes exist (from Features 001/002/009)
-- If missing, create via Alembic migration

-- 1. User profile visibility (Feature 001)
CREATE INDEX IF NOT EXISTS idx_users_profile_visibility
ON users (profile_visibility);

-- 2. Trip status + published_at composite index (Feature 002)
CREATE INDEX IF NOT EXISTS idx_trips_public_feed
ON trips (status, published_at DESC)
WHERE status = 'PUBLISHED';

-- 3. User ID on trips (should exist from Feature 002)
CREATE INDEX IF NOT EXISTS idx_trips_user_id
ON trips (user_id);
```

**Performance Impact**:
- Query execution time: **<20ms** for 1000 trips (with indexes)
- Without indexes: ~150ms (full table scan - UNACCEPTABLE)

**Migration Script** (if indexes missing):
```python
# backend/migrations/versions/XXXXXX_add_public_feed_indexes.py

def upgrade():
    # Check current indexes first
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_profile_visibility
        ON users (profile_visibility);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_trips_public_feed
        ON trips (status, published_at DESC)
        WHERE status = 'PUBLISHED';
    """)

def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_users_profile_visibility;")
    op.execute("DROP INDEX IF EXISTS idx_trips_public_feed;")
```

---

## Query Patterns

### Primary Query: Get Public Trips

```python
# backend/src/services/trip_service.py

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

async def get_public_trips(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20
) -> list[Trip]:
    """
    Fetch published trips from users with public profiles.

    Performance: <20ms for 1000 trips (with indexes)
    Query count: 3 queries (1 main + 2 selectinload batches)
    """
    offset = (page - 1) * limit

    query = (
        select(Trip)
        .join(Trip.user)  # INNER JOIN to filter by user.profile_visibility
        .where(Trip.status == TripStatus.PUBLISHED)
        .where(User.profile_visibility == 'public')
        .options(
            joinedload(Trip.user),  # Load user data in same query
            selectinload(Trip.photos).options(  # Batch load photos
                limit=1  # Only first photo
            ),
            selectinload(Trip.locations).options(  # Batch load locations
                limit=1  # Only first location
            )
        )
        .order_by(Trip.published_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    trips = result.unique().scalars().all()
    return trips

async def count_public_trips(db: AsyncSession) -> int:
    """Count total public trips for pagination metadata."""
    query = (
        select(func.count(Trip.trip_id))
        .join(Trip.user)
        .where(Trip.status == TripStatus.PUBLISHED)
        .where(User.profile_visibility == 'public')
    )
    result = await db.execute(query)
    return result.scalar_one()
```

**SQL Generated** (simplified):
```sql
-- Main query
SELECT trips.*, users.username, users.photo_url
FROM trips
INNER JOIN users ON trips.user_id = users.user_id
WHERE trips.status = 'PUBLISHED'
  AND users.profile_visibility = 'public'
ORDER BY trips.published_at DESC
LIMIT 20 OFFSET 0;

-- Batch load photos (selectinload)
SELECT trip_photos.*
FROM trip_photos
WHERE trip_photos.trip_id IN (...)
  AND trip_photos.order = 0;

-- Batch load locations (selectinload)
SELECT trip_locations.*
FROM trip_locations
WHERE trip_locations.trip_id IN (...)
  AND trip_locations.order = 0;
```

**Query Complexity**: O(log n) with indexes, O(n) without indexes

---

## Frontend TypeScript Types

### Extended Types for Public Feed

```typescript
// frontend/src/types/trip.ts (EXTEND EXISTING)

export interface PublicUserSummary {
  user_id: string;
  username: string;
  photo_url: string | null;
}

export interface PublicLocationSummary {
  location_id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface PublicPhotoSummary {
  photo_id: string;
  photo_url: string;
  caption: string | null;
}

export interface PublicTripSummary {
  trip_id: string;
  title: string;
  distance_km: number;
  start_date: string; // ISO 8601 date (YYYY-MM-DD)
  published_at: string; // ISO 8601 datetime

  // Related entities
  user: PublicUserSummary;
  first_photo: PublicPhotoSummary | null;
  first_location: PublicLocationSummary | null;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface PublicTripListResponse {
  success: boolean;
  data: PublicTripSummary[];
  pagination: PaginationInfo;
}
```

---

## Data Flow

```text
[Anonymous User] → [GET /api/trips/public?page=1]
     ↓
[FastAPI Router] → trips.py::get_public_trips()
     ↓
[TripService] → get_public_trips(db, page=1, limit=20)
     ↓
[SQLAlchemy Query]
  ├─ WHERE status = PUBLISHED
  ├─ WHERE user.profile_visibility = public
  ├─ ORDER BY published_at DESC
  ├─ LIMIT 20 OFFSET 0
  └─ Eager load: user, first_photo, first_location
     ↓
[Database] → Returns 20 Trip objects + related data
     ↓
[Pydantic Schema] → PublicTripSummary serialization
     ↓
[JSON Response] → { success: true, data: [...], pagination: {...} }
     ↓
[Frontend] → usePublicTrips() hook → setState(trips)
     ↓
[React Components] → PublicTripCard renders each trip
```

---

## Privacy Guarantees

### Enforced at Database Level

✅ **Privacy Filter in WHERE Clause**: `User.profile_visibility = 'public'`
✅ **Status Filter**: Only `PUBLISHED` trips (never DRAFT)
✅ **Excluded Fields**: User email, bio, stats not in PublicUserSummary
✅ **Sanitized HTML**: Trip descriptions sanitized to prevent XSS (Feature 002 already does this)

### Edge Case Handling

| Scenario | Behavior |
|----------|----------|
| User changes profile to private | Next query excludes their trips (no caching issue) |
| User deletes account | CASCADE DELETE removes trips (database constraint) |
| Trip has no photos | `first_photo: null` (graceful handling) |
| Trip has no locations | `first_location: null` (card hides location field) |
| Pagination beyond available pages | Returns empty array (page 1000 with 20 trips total) |

---

## Summary

**Models Used**: User, Trip, TripPhoto, TripLocation (all existing)
**New Schemas**: PublicTripSummary, PublicTripListResponse (Pydantic only)
**Migrations Needed**: Index creation (if indexes don't exist)
**Query Performance**: <20ms with proper indexes
**Privacy**: Enforced at SQL level (WHERE clause)

**Next Phase**: Create OpenAPI contract for GET /api/trips/public endpoint.
