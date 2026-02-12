# Data Model: Diario de Viajes Digital

**Feature**: 002-travel-diary
**Date**: 2025-12-24
**Database**: PostgreSQL 15+ (production) / SQLite 3.40+ (development/test)

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ users (existing from 001-user-profiles)                     │
│ ────────────────────────────────────────────────────────────│
│ • id                  UUID/TEXT PRIMARY KEY                  │
│ • username            VARCHAR UNIQUE NOT NULL                │
│ • email               VARCHAR UNIQUE NOT NULL                │
│ • ...                                                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ 1:N (one user has many trips)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ trips (NEW)                                                  │
│ ────────────────────────────────────────────────────────────│
│ • id                  UUID/TEXT PRIMARY KEY                  │
│ • user_id             UUID/TEXT FOREIGN KEY → users.id       │
│ • title               VARCHAR(100) NOT NULL                  │
│ • description         TEXT NOT NULL                          │
│ • start_date          DATE NOT NULL                          │
│ • end_date            DATE NULL                              │
│ • distance_km         DECIMAL(7,2) NULL                      │
│ • difficulty          ENUM/TEXT NULL                         │
│ • status              ENUM/TEXT NOT NULL DEFAULT 'draft'     │
│ • created_at          TIMESTAMP NOT NULL                     │
│ • updated_at          TIMESTAMP NOT NULL                     │
│ • published_at        TIMESTAMP NULL                         │
└───┬───────────────────┬───────────────────┬─────────────────┘
    │                   │                   │
    │ 1:N              │ 1:N              │ N:M (via trip_tags)
    │                   │                   │
    ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│ trip_photos  │  │ trip_        │  │ trip_tags (join)     │
│              │  │ locations    │  │                      │
│ • id         │  │ • id         │  │ • trip_id FK         │
│ • trip_id FK │  │ • trip_id FK │  │ • tag_id FK          │
│ • photo_url  │  │ • name       │  │ • created_at         │
│ • thumb_url  │  │ • country    │  └──────────┬───────────┘
│ • order      │  │ • order      │             │
│ • file_size  │  │ • created_at │             │ N:1
│ • width      │  └──────────────┘             │
│ • height     │                               ▼
│ • uploaded_at│                       ┌──────────────────┐
└──────────────┘                       │ tags (NEW)        │
                                       │                  │
                                       │ • id             │
                                       │ • name           │
                                       │ • normalized     │
                                       │ • first_used_at  │
                                       │ • usage_count    │
                                       └──────────────────┘
```

---

## Entity Specifications

### 1. Trip (Core Entity)

**Purpose**: Represents a single cycling trip/journey documented by a user.

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID (PG) / TEXT (SQLite) | PRIMARY KEY | Unique trip identifier |
| `user_id` | UUID/TEXT | FOREIGN KEY → users.id, NOT NULL, ON DELETE CASCADE | Owner of the trip |
| `title` | VARCHAR(100) | NOT NULL | Trip title (e.g., "Vía Verde del Aceite") |
| `description` | TEXT | NOT NULL | Rich text HTML (sanitized), max 50,000 chars |
| `start_date` | DATE | NOT NULL | Trip start date (cannot be future per FR-006) |
| `end_date` | DATE | NULL | Trip end date (optional, must be >= start_date) |
| `distance_km` | DECIMAL(7,2) | NULL, CHECK (distance_km BETWEEN 0.1 AND 10000) | Distance in kilometers |
| `difficulty` | ENUM/TEXT | NULL, CHECK IN ('easy', 'moderate', 'hard', 'very_hard') | Difficulty level |
| `status` | ENUM/TEXT | NOT NULL, DEFAULT 'draft', CHECK IN ('draft', 'published') | Publication status |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification time |
| `published_at` | TIMESTAMP | NULL | When status changed to 'published' |

**Indexes**:
```sql
CREATE INDEX idx_trip_user_status ON trips(user_id, status, published_at DESC);
CREATE INDEX idx_trip_user_created ON trips(user_id, created_at DESC);
CREATE INDEX idx_trip_start_date ON trips(start_date);
```

**Validation Rules** (enforced in application layer):
- Title: 1-100 characters
- Description:
  - Minimum 50 characters for published trips (FR-002)
  - No minimum for drafts (allows gradual writing)
  - Maximum 50,000 characters (FR-032)
- Start date: Cannot be in future (FR-006)
- End date: If provided, must be >= start_date (FR-006)
- Distance: 0.1 - 10,000 km if provided (FR-005)

**State Transitions**:
```
draft ──────> published (via publish action)
  ↑               │
  └───────────────┘ (via un-publish - future feature)
```

---

### 2. TripPhoto

**Purpose**: Store metadata for photos associated with a trip.

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID/TEXT | PRIMARY KEY | Unique photo identifier |
| `trip_id` | UUID/TEXT | FOREIGN KEY → trips.id, NOT NULL, ON DELETE CASCADE | Parent trip |
| `photo_url` | TEXT | NOT NULL | Path to optimized photo file |
| `thumb_url` | TEXT | NOT NULL | Path to thumbnail file |
| `order` | INTEGER | NOT NULL, DEFAULT 0 | Display order in gallery |
| `file_size` | INTEGER | NOT NULL | Optimized file size in bytes |
| `width` | INTEGER | NOT NULL | Optimized image width in pixels |
| `height` | INTEGER | NOT NULL | Optimized image height in pixels |
| `uploaded_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Upload timestamp |

**Indexes**:
```sql
CREATE INDEX idx_photo_trip_order ON trip_photos(trip_id, "order");
```

**Constraints**:
```sql
ALTER TABLE trip_photos ADD CONSTRAINT max_photos_per_trip
  CHECK ((SELECT COUNT(*) FROM trip_photos WHERE trip_id = trip_photos.trip_id) <= 20);
```

**File Path Convention**:
```
photo_url: /storage/trip_photos/2025/01/{trip_id}/{uuid}_optimized.jpg
thumb_url: /storage/trip_photos/2025/01/{trip_id}/{uuid}_thumb.jpg
```

**Notes**:
- Original uploaded file is deleted after processing (not stored permanently)
- Max 20 photos per trip enforced at application layer (FR-009)
- Order is 0-indexed, allows manual reordering (FR-012)

---

### 3. Tag

**Purpose**: Reusable tags for categorizing trips.

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID/TEXT | PRIMARY KEY | Unique tag identifier |
| `name` | VARCHAR(30) | NOT NULL | Original capitalization (display) |
| `normalized` | VARCHAR(30) | NOT NULL, UNIQUE | Lowercase for matching (FR-025) |
| `first_used_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When tag was first created |
| `usage_count` | INTEGER | NOT NULL, DEFAULT 1 | Number of trips using this tag |

**Indexes**:
```sql
CREATE UNIQUE INDEX idx_tag_normalized ON tags(normalized);
CREATE INDEX idx_tag_usage ON tags(usage_count DESC);
```

**Normalization Logic** (application layer):
```python
def normalize_tag(tag: str) -> str:
    """Normalize tag for case-insensitive matching."""
    return tag.strip().lower()[:30]  # Trim whitespace, lowercase, max 30 chars
```

**Examples**:
- User enters: "Bikepacking" → `name='Bikepacking'`, `normalized='bikepacking'`
- User enters: "CAMINO DE SANTIAGO" → `name='CAMINO DE SANTIAGO'`, `normalized='camino de santiago'`
- Later user enters: "bikepacking" → Matches existing tag, reuses same ID

---

### 4. TripTag (Join Table)

**Purpose**: Many-to-many relationship between trips and tags.

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `trip_id` | UUID/TEXT | FOREIGN KEY → trips.id, NOT NULL, ON DELETE CASCADE | Trip reference |
| `tag_id` | UUID/TEXT | FOREIGN KEY → tags.id, NOT NULL, ON DELETE CASCADE | Tag reference |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When tag was added to trip |

**Primary Key**: Composite `(trip_id, tag_id)`

**Indexes**:
```sql
CREATE INDEX idx_trip_tags_trip ON trip_tags(trip_id);
CREATE INDEX idx_trip_tags_tag ON trip_tags(tag_id);
```

**Constraints**:
```sql
ALTER TABLE trip_tags ADD CONSTRAINT max_tags_per_trip
  CHECK ((SELECT COUNT(*) FROM trip_tags WHERE trip_id = trip_tags.trip_id) <= 10);
```

**Notes**:
- Max 10 tags per trip enforced at application layer (FR-021)
- ON DELETE CASCADE: Removing trip removes all its tag associations
- ON DELETE CASCADE: Removing tag removes all trip associations (rare - only if tag cleanup job runs)

---

### 5. TripLocation

**Purpose**: Store locations/places visited during a trip.

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID/TEXT | PRIMARY KEY | Unique location identifier |
| `trip_id` | UUID/TEXT | FOREIGN KEY → trips.id, NOT NULL, ON DELETE CASCADE | Parent trip |
| `name` | VARCHAR(100) | NOT NULL | Location name (e.g., "Córdoba", "Baeza") |
| `country` | VARCHAR(100) | NULL | Country name (optional) |
| `order` | INTEGER | NOT NULL, DEFAULT 0 | Order in route (0 = start, N = end) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When location was added |

**Indexes**:
```sql
CREATE INDEX idx_location_trip_order ON trip_locations(trip_id, "order");
```

**Notes**:
- Locations are free-text fields (no geocoding in this phase - see spec assumptions #6)
- Order represents sequence along the route
- Future feature (003-gps-routes) will add lat/lng coordinates

---

## Database Schema DDL

### PostgreSQL (Production)

```sql
-- ============================================================================
-- TRIP DIARY FEATURE - PostgreSQL DDL
-- ============================================================================

-- Enums
CREATE TYPE trip_status AS ENUM ('draft', 'published');
CREATE TYPE difficulty_level AS ENUM ('easy', 'moderate', 'hard', 'very_hard');

-- Trips table
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    distance_km DECIMAL(7,2) NULL CHECK (distance_km >= 0.1 AND distance_km <= 10000),
    difficulty difficulty_level NULL,
    status trip_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP NULL,

    CONSTRAINT end_after_start CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Indexes for trips
CREATE INDEX idx_trip_user_status ON trips(user_id, status, published_at DESC);
CREATE INDEX idx_trip_user_created ON trips(user_id, created_at DESC);
CREATE INDEX idx_trip_start_date ON trips(start_date);

-- Photos table
CREATE TABLE trip_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    photo_url TEXT NOT NULL,
    thumb_url TEXT NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 0,
    file_size INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_photo_trip_order ON trip_photos(trip_id, "order");

-- Tags table
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(30) NOT NULL,
    normalized VARCHAR(30) NOT NULL UNIQUE,
    first_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX idx_tag_normalized ON tags(normalized);
CREATE INDEX idx_tag_usage ON tags(usage_count DESC);

-- Trip-Tag join table
CREATE TABLE trip_tags (
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trip_id, tag_id)
);

CREATE INDEX idx_trip_tags_trip ON trip_tags(trip_id);
CREATE INDEX idx_trip_tags_tag ON trip_tags(tag_id);

-- Locations table
CREATE TABLE trip_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NULL,
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_location_trip_order ON trip_locations(trip_id, "order");

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_trip_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trip_updated_at
    BEFORE UPDATE ON trips
    FOR EACH ROW
    EXECUTE FUNCTION update_trip_timestamp();

-- Trigger to set published_at when status changes to published
CREATE OR REPLACE FUNCTION set_published_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'published' AND OLD.status != 'published' THEN
        NEW.published_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trip_published_at
    BEFORE UPDATE ON trips
    FOR EACH ROW
    EXECUTE FUNCTION set_published_at();
```

### SQLite (Development/Test)

```sql
-- ============================================================================
-- TRIP DIARY FEATURE - SQLite DDL
-- ============================================================================

-- Trips table
CREATE TABLE trips (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL CHECK(length(title) <= 100),
    description TEXT NOT NULL,
    start_date TEXT NOT NULL,  -- ISO8601 format: YYYY-MM-DD
    end_date TEXT NULL,
    distance_km REAL NULL CHECK (distance_km >= 0.1 AND distance_km <= 10000),
    difficulty TEXT NULL CHECK (difficulty IN ('easy', 'moderate', 'hard', 'very_hard')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    published_at TEXT NULL,

    CHECK (end_date IS NULL OR end_date >= start_date)
);

-- Indexes for trips
CREATE INDEX idx_trip_user_status ON trips(user_id, status, published_at DESC);
CREATE INDEX idx_trip_user_created ON trips(user_id, created_at DESC);
CREATE INDEX idx_trip_start_date ON trips(start_date);

-- Photos table
CREATE TABLE trip_photos (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    photo_url TEXT NOT NULL,
    thumb_url TEXT NOT NULL,
    "order" INTEGER NOT NULL DEFAULT 0,
    file_size INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_photo_trip_order ON trip_photos(trip_id, "order");

-- Tags table
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(name) <= 30),
    normalized TEXT NOT NULL UNIQUE CHECK(length(normalized) <= 30),
    first_used_at TEXT NOT NULL DEFAULT (datetime('now')),
    usage_count INTEGER NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX idx_tag_normalized ON tags(normalized);
CREATE INDEX idx_tag_usage ON tags(usage_count DESC);

-- Trip-Tag join table
CREATE TABLE trip_tags (
    trip_id TEXT NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    tag_id TEXT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (trip_id, tag_id)
);

CREATE INDEX idx_trip_tags_trip ON trip_tags(trip_id);
CREATE INDEX idx_trip_tags_tag ON trip_tags(tag_id);

-- Locations table
CREATE TABLE trip_locations (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    name TEXT NOT NULL CHECK(length(name) <= 100),
    country TEXT NULL CHECK(country IS NULL OR length(country) <= 100),
    "order" INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_location_trip_order ON trip_locations(trip_id, "order");

-- Trigger to update updated_at
CREATE TRIGGER trip_updated_at
    AFTER UPDATE ON trips
    FOR EACH ROW
    BEGIN
        UPDATE trips SET updated_at = datetime('now') WHERE id = NEW.id;
    END;

-- Trigger to set published_at
CREATE TRIGGER trip_published_at
    AFTER UPDATE ON trips
    FOR EACH ROW
    WHEN NEW.status = 'published' AND OLD.status != 'published'
    BEGIN
        UPDATE trips SET published_at = datetime('now') WHERE id = NEW.id;
    END;

-- Enable foreign keys in SQLite
PRAGMA foreign_keys = ON;
```

---

## Sample Queries

### Query 1: Get all published trips for a user

```sql
SELECT
    t.id,
    t.title,
    t.start_date,
    t.end_date,
    t.distance_km,
    t.difficulty,
    t.published_at,
    COUNT(DISTINCT tp.id) as photo_count,
    STRING_AGG(DISTINCT tag.name, ', ') as tags
FROM trips t
LEFT JOIN trip_photos tp ON t.id = tp.trip_id
LEFT JOIN trip_tags tt ON t.id = tt.trip_id
LEFT JOIN tags tag ON tt.tag_id = tag.id
WHERE t.user_id = :user_id
  AND t.status = 'published'
GROUP BY t.id
ORDER BY t.published_at DESC
LIMIT 50 OFFSET :offset;
```

### Query 2: Get trip detail with all related data

```sql
-- Using SQLAlchemy eager loading (recommended)
SELECT
    t.*,
    tp.*,  -- Photos
    tl.*,  -- Locations
    tag.*  -- Tags
FROM trips t
LEFT JOIN trip_photos tp ON t.id = tp.trip_id
LEFT JOIN trip_locations tl ON t.id = tl.trip_id
LEFT JOIN trip_tags tt ON t.id = tt.trip_id
LEFT JOIN tags tag ON tt.tag_id = tag.id
WHERE t.id = :trip_id
  AND (t.status = 'published' OR t.user_id = :current_user_id)
ORDER BY tp."order", tl."order";
```

### Query 3: Filter trips by tag

```sql
SELECT DISTINCT t.*
FROM trips t
JOIN trip_tags tt ON t.id = tt.trip_id
JOIN tags tag ON tt.tag_id = tag.id
WHERE tag.normalized = LOWER(:tag_name)
  AND t.user_id = :user_id
  AND t.status = 'published'
ORDER BY t.published_at DESC;
```

### Query 4: Update user stats after trip deletion

```sql
-- Calculate total distance from remaining trips
UPDATE user_stats
SET
    total_trips = (
        SELECT COUNT(*) FROM trips
        WHERE user_id = :user_id AND status = 'published'
    ),
    total_kilometers = COALESCE((
        SELECT SUM(distance_km) FROM trips
        WHERE user_id = :user_id AND status = 'published' AND distance_km IS NOT NULL
    ), 0),
    last_trip_date = (
        SELECT MAX(start_date) FROM trips
        WHERE user_id = :user_id AND status = 'published'
    )
WHERE user_id = :user_id;
```

---

## Data Migration Plan

### From v0.1.0 (User Profiles) to v0.2.0 (Travel Diary)

**Alembic Migration Steps**:

1. Create new tables (trips, trip_photos, tags, trip_tags, trip_locations)
2. Create indexes
3. Create triggers (PostgreSQL) / Triggers (SQLite)
4. No data migration needed (new feature, no existing data)

**Rollback Plan**:

1. Drop triggers
2. Drop indexes
3. Drop tables in reverse dependency order:
   - trip_locations
   - trip_tags
   - trip_photos
   - trips
   - tags

**Migration File Template**:
```python
"""add_travel_diary_tables

Revision ID: YYYYMMDD_HHMM
Revises: <previous_revision>
Create Date: 2025-12-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'YYYYMMDD_HHMM'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None

def upgrade():
    # Create enums (PostgreSQL only)
    if op.get_bind().dialect.name == 'postgresql':
        sa.Enum('draft', 'published', name='trip_status').create(op.get_bind())
        sa.Enum('easy', 'moderate', 'hard', 'very_hard', name='difficulty_level').create(op.get_bind())

    # Create tables
    # ... (DDL from above)

def downgrade():
    # Drop tables
    op.drop_table('trip_locations')
    op.drop_table('trip_tags')
    op.drop_table('trip_photos')
    op.drop_table('trips')
    op.drop_table('tags')

    # Drop enums (PostgreSQL only)
    if op.get_bind().dialect.name == 'postgresql':
        sa.Enum(name='trip_status').drop(op.get_bind())
        sa.Enum(name='difficulty_level').drop(op.get_bind())
```

---

## Data Integrity & Constraints Summary

| Constraint Type | Rule | Enforced By |
|-----------------|------|-------------|
| Primary Keys | All tables have UUID/TEXT primary keys | Database |
| Foreign Keys | Cascading deletes for all child records | Database |
| Uniqueness | Tag.normalized unique | Database |
| Check Constraints | Distance 0.1-10000, end_date >= start_date | Database |
| Length Limits | Title ≤100, Description ≤50k, Tag ≤30 | Application + Database |
| Required Fields | Title, description, start_date for trips | Database NOT NULL |
| Status Values | Only 'draft' or 'published' | Database ENUM/CHECK |
| Difficulty Values | Only 4 predefined values | Database ENUM/CHECK |
| Max Photos | ≤20 per trip | Application (enforced before insert) |
| Max Tags | ≤10 per trip | Application (enforced before insert) |
| Timestamps | Auto-updated on modification | Database Triggers |

---

## Storage Estimates

### Per Trip (Average)

- Trip record: ~1 KB
- 5 photos (avg): 5 × 1.6 MB = 8 MB
- 3 locations: 3 × 0.1 KB = 0.3 KB
- 5 tags: 5 × 0.05 KB = 0.25 KB
- **Total per trip**: ~8 MB

### Scale Projections

| Users | Trips per User | Total Trips | Storage (Photos) | Database Size |
|-------|----------------|-------------|------------------|---------------|
| 100 | 10 | 1,000 | 8 GB | 10 MB |
| 1,000 | 20 | 20,000 | 160 GB | 200 MB |
| 10,000 | 30 | 300,000 | 2.4 TB | 3 GB |

**Recommendation**: Migrate to cloud storage (S3) when approaching 100GB (>12,500 trips).

---

## Appendix: SQLAlchemy Model Reference

```python
# backend/src/models/trip.py
from sqlalchemy import Column, String, Text, Integer, Numeric, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base
import enum as python_enum

class TripStatus(str, python_enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class DifficultyLevel(str, python_enum.Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"

class Trip(Base):
    __tablename__ = "trips"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    distance_km = Column(Numeric(7, 2), nullable=True)
    difficulty = Column(Enum(DifficultyLevel), nullable=True)
    status = Column(Enum(TripStatus), nullable=False, default=TripStatus.DRAFT)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    published_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="trips")
    photos = relationship("TripPhoto", back_populates="trip", cascade="all, delete-orphan")
    locations = relationship("TripLocation", back_populates="trip", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="trip_tags", back_populates="trips")

class TripPhoto(Base):
    __tablename__ = "trip_photos"

    id = Column(String, primary_key=True)
    trip_id = Column(String, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    photo_url = Column(Text, nullable=False)
    thumb_url = Column(Text, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

    trip = relationship("Trip", back_populates="photos")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True)
    name = Column(String(30), nullable=False)
    normalized = Column(String(30), nullable=False, unique=True)
    first_used_at = Column(DateTime, nullable=False)
    usage_count = Column(Integer, nullable=False, default=1)

    trips = relationship("Trip", secondary="trip_tags", back_populates="tags")

class TripTag(Base):
    __tablename__ = "trip_tags"

    trip_id = Column(String, ForeignKey("trips.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, nullable=False)

class TripLocation(Base):
    __tablename__ = "trip_locations"

    id = Column(String, primary_key=True)
    trip_id = Column(String, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False)

    trip = relationship("Trip", back_populates="locations")
```

---

**Data Model Version**: 1.0
**Last Updated**: 2025-12-24
**Status**: ✅ Ready for Implementation
