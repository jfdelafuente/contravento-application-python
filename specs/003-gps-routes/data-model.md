# Data Model: Feature 003 - GPS Routes Interactive

**Feature Branch**: `003-gps-routes`
**Database**: Dual-compatible (SQLite development, PostgreSQL production)
**Date**: 2026-01-21

This document defines the database schema for GPS Routes Interactive feature, supporting GPX file uploads, track visualization, elevation profiles, and points of interest.

---

## Entity Relationship Diagram

```text
┌──────────────┐
│    trips     │ (existing table)
└──────┬───────┘
       │ 1
       │
       │ N
┌──────┴───────┐       ┌────────────────┐
│  gpx_files   │───N───│  track_points  │
└──────┬───────┘       └────────────────┘
       │
       │ 0..1
┌──────┴────────────┐
│ route_statistics  │ (Phase 2 - Advanced Stats)
└───────────────────┘

┌──────────────┐
│    trips     │
└──────┬───────┘
       │ 1
       │
       │ N
┌──────┴─────────────┐
│ points_of_interest │ (Phase 2 - POI)
└────────────────────┘
```

---

## Phase 1 Tables (MVP - GPX Upload & Visualization)

### 1. `gpx_files` Table

**Purpose**: Stores metadata about uploaded GPX files and processing results.

**Relationships**:
- **1:1 with Trip**: Each trip can have at most one GPX file (FR-038)
- **1:N with TrackPoint**: One GPX file contains many simplified trackpoints

**DDL (SQLite - Development)**:
```sql
CREATE TABLE gpx_files (
    gpx_file_id TEXT PRIMARY KEY,                    -- UUID
    trip_id TEXT UNIQUE NOT NULL,                    -- FK to trips (1:1 relationship)
    file_url TEXT NOT NULL,                          -- Original GPX file path
    file_size INTEGER NOT NULL,                      -- File size in bytes
    file_name TEXT NOT NULL,                         -- Original filename
    distance_km REAL NOT NULL,                       -- Total distance (calculated)
    elevation_gain REAL,                             -- Total elevation gain in meters
    elevation_loss REAL,                             -- Total elevation loss in meters
    max_elevation REAL,                              -- Maximum altitude in meters
    min_elevation REAL,                              -- Minimum altitude in meters
    start_lat REAL NOT NULL,                         -- Start point latitude
    start_lon REAL NOT NULL,                         -- Start point longitude
    end_lat REAL NOT NULL,                           -- End point latitude
    end_lon REAL NOT NULL,                           -- End point longitude
    total_points INTEGER NOT NULL,                   -- Original point count before simplification
    simplified_points INTEGER NOT NULL,              -- Reduced point count after Douglas-Peucker
    has_elevation BOOLEAN NOT NULL,                  -- True if GPX contains elevation data
    has_timestamps BOOLEAN NOT NULL,                 -- True if GPX contains timestamp data
    processing_status TEXT NOT NULL DEFAULT 'pending', -- pending|processing|completed|error
    error_message TEXT,                              -- Error details if processing_status = error
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,                          -- When processing completed

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
);

CREATE INDEX idx_gpx_files_trip ON gpx_files(trip_id);
CREATE INDEX idx_gpx_files_status ON gpx_files(processing_status);
```

**DDL (PostgreSQL - Production)**:
```sql
CREATE TABLE gpx_files (
    gpx_file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID UNIQUE NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    distance_km DOUBLE PRECISION NOT NULL,
    elevation_gain DOUBLE PRECISION,
    elevation_loss DOUBLE PRECISION,
    max_elevation DOUBLE PRECISION,
    min_elevation DOUBLE PRECISION,
    start_lat DOUBLE PRECISION NOT NULL,
    start_lon DOUBLE PRECISION NOT NULL,
    end_lat DOUBLE PRECISION NOT NULL,
    end_lon DOUBLE PRECISION NOT NULL,
    total_points INTEGER NOT NULL,
    simplified_points INTEGER NOT NULL,
    has_elevation BOOLEAN NOT NULL,
    has_timestamps BOOLEAN NOT NULL,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
);

CREATE INDEX idx_gpx_files_trip ON gpx_files(trip_id);
CREATE INDEX idx_gpx_files_status ON gpx_files(processing_status);
```

**Validation Rules** (from spec):
- `file_size`: Maximum 10 MB (10,485,760 bytes) - FR-001
- `file_name`: Must end with `.gpx` extension - FR-002
- `processing_status`: ENUM('pending', 'processing', 'completed', 'error')
- `distance_km`: Must be > 0
- `elevation_gain`, `elevation_loss`: NULL if `has_elevation` = FALSE
- `start_lat`, `end_lat`: Range -90 to 90 (WGS84)
- `start_lon`, `end_lon`: Range -180 to 180 (WGS84)

---

### 2. `track_points` Table

**Purpose**: Stores simplified GPS trackpoints for efficient map rendering (Douglas-Peucker algorithm applied).

**Relationships**:
- **N:1 with GPXFile**: Many trackpoints belong to one GPX file

**DDL (SQLite - Development)**:
```sql
CREATE TABLE track_points (
    point_id TEXT PRIMARY KEY,                       -- UUID
    gpx_file_id TEXT NOT NULL,                       -- FK to gpx_files
    latitude REAL NOT NULL,                          -- WGS84 latitude
    longitude REAL NOT NULL,                         -- WGS84 longitude
    elevation REAL,                                  -- Altitude in meters (NULL if not available)
    distance_km REAL NOT NULL,                       -- Cumulative distance from start
    sequence INTEGER NOT NULL,                       -- Order in track (0, 1, 2, ...)
    gradient REAL,                                   -- % gradient at this point

    FOREIGN KEY (gpx_file_id) REFERENCES gpx_files(gpx_file_id) ON DELETE CASCADE
);

CREATE INDEX idx_track_points_gpx ON track_points(gpx_file_id);
CREATE INDEX idx_track_points_seq ON track_points(gpx_file_id, sequence);
```

**DDL (PostgreSQL - Production)**:
```sql
CREATE TABLE track_points (
    point_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gpx_file_id UUID NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    elevation DOUBLE PRECISION,
    distance_km DOUBLE PRECISION NOT NULL,
    sequence INTEGER NOT NULL,
    gradient DOUBLE PRECISION,

    FOREIGN KEY (gpx_file_id) REFERENCES gpx_files(gpx_file_id) ON DELETE CASCADE
);

CREATE INDEX idx_track_points_gpx ON track_points(gpx_file_id);
CREATE INDEX idx_track_points_seq ON track_points(gpx_file_id, sequence);
CREATE UNIQUE INDEX idx_track_points_unique_seq ON track_points(gpx_file_id, sequence);
```

**Validation Rules**:
- `latitude`: Range -90 to 90 (WGS84 standard)
- `longitude`: Range -180 to 180 (WGS84 standard)
- `elevation`: Range -420 to 8850 meters (Dead Sea to Everest) - FR-034
- `distance_km`: Must be >= 0 and <= parent `gpx_files.distance_km`
- `sequence`: Must be unique per `gpx_file_id`, starting from 0
- `gradient`: Percentage slope (e.g., 5.2 = 5.2% uphill)

**Simplification Strategy**:
- Original GPX may have 10,000+ points
- Douglas-Peucker algorithm (epsilon=0.0001°) reduces to ~500-1000 points
- Achieves 80-90% storage reduction (SC-026)
- Maintains visual accuracy (<5% distortion)

---

## Phase 2 Tables (Advanced Features)

### 3. `points_of_interest` Table

**Purpose**: User-defined points of interest along the route (US4).

**Relationships**:
- **N:1 with Trip**: Many POIs belong to one trip

**DDL (SQLite - Development)**:
```sql
CREATE TABLE points_of_interest (
    poi_id TEXT PRIMARY KEY,                         -- UUID
    trip_id TEXT NOT NULL,                           -- FK to trips
    name TEXT NOT NULL,                              -- POI name (max 100 chars)
    description TEXT,                                -- Optional description (max 500 chars)
    poi_type TEXT NOT NULL,                          -- viewpoint|town|water|accommodation|restaurant|other
    latitude REAL NOT NULL,                          -- WGS84 latitude
    longitude REAL NOT NULL,                         -- WGS84 longitude
    distance_from_start_km REAL,                     -- Calculated from GPX track
    photo_url TEXT,                                  -- Optional photo
    sequence INTEGER NOT NULL,                       -- Display order
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    CHECK (length(name) <= 100),
    CHECK (description IS NULL OR length(description) <= 500)
);

CREATE INDEX idx_poi_trip ON points_of_interest(trip_id);
CREATE INDEX idx_poi_type ON points_of_interest(trip_id, poi_type);
```

**DDL (PostgreSQL - Production)**:
```sql
CREATE TYPE poi_type_enum AS ENUM (
    'viewpoint',
    'town',
    'water',
    'accommodation',
    'restaurant',
    'other'
);

CREATE TABLE points_of_interest (
    poi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    poi_type poi_type_enum NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    distance_from_start_km DOUBLE PRECISION,
    photo_url VARCHAR(500),
    sequence INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
);

CREATE INDEX idx_poi_trip ON points_of_interest(trip_id);
CREATE INDEX idx_poi_type ON points_of_interest(trip_id, poi_type);
```

**Validation Rules** (FR-024, FR-029):
- `name`: Required, 1-100 characters
- `description`: Optional, max 500 characters
- `poi_type`: ENUM (viewpoint, town, water, accommodation, restaurant, other)
- `latitude`: Range -90 to 90
- `longitude`: Range -180 to 180
- **Maximum 20 POIs per trip** (enforced at service layer - FR-029)

---

### 4. `route_statistics` Table

**Purpose**: Advanced statistics calculated from GPX with timestamps (US5).

**Relationships**:
- **1:1 with GPXFile**: One statistics record per GPX file (only if timestamps available)

**DDL (SQLite - Development)**:
```sql
CREATE TABLE route_statistics (
    stats_id TEXT PRIMARY KEY,                       -- UUID
    gpx_file_id TEXT UNIQUE NOT NULL,                -- FK to gpx_files (1:1 relationship)
    avg_speed_kmh REAL,                              -- Average speed (NULL if no timestamps)
    max_speed_kmh REAL,                              -- Maximum speed
    total_time_minutes REAL,                         -- Total elapsed time
    moving_time_minutes REAL,                        -- Time in motion (excludes stops >5min)
    avg_gradient REAL,                               -- Average gradient %
    max_gradient REAL,                               -- Steepest gradient %
    top_climbs TEXT,                                 -- JSON array of top 3 climbs
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (gpx_file_id) REFERENCES gpx_files(gpx_file_id) ON DELETE CASCADE
);

CREATE INDEX idx_route_stats_gpx ON route_statistics(gpx_file_id);
```

**DDL (PostgreSQL - Production)**:
```sql
CREATE TABLE route_statistics (
    stats_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    gpx_file_id UUID UNIQUE NOT NULL,
    avg_speed_kmh DOUBLE PRECISION,
    max_speed_kmh DOUBLE PRECISION,
    total_time_minutes DOUBLE PRECISION,
    moving_time_minutes DOUBLE PRECISION,
    avg_gradient DOUBLE PRECISION,
    max_gradient DOUBLE PRECISION,
    top_climbs JSONB,                                 -- [{start_km, end_km, gain_m, avg_gradient}]
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    FOREIGN KEY (gpx_file_id) REFERENCES gpx_files(gpx_file_id) ON DELETE CASCADE
);

CREATE INDEX idx_route_stats_gpx ON route_statistics(gpx_file_id);
```

**Validation Rules** (FR-030, FR-032):
- All speed/time fields: NULL if GPX has no timestamps
- `avg_speed_kmh`, `max_speed_kmh`: Must be > 0 and < 100 km/h (reasonable for cycling)
- `total_time_minutes`: Must be >= `moving_time_minutes`
- `top_climbs`: JSON array with max 3 elements

**top_climbs JSON Structure**:
```json
[
  {
    "start_km": 15.2,
    "end_km": 18.7,
    "elevation_gain_m": 320,
    "avg_gradient": 9.1,
    "description": "Puerto de los Leones"
  }
]
```

---

## SQLAlchemy Models (Python ORM)

### Phase 1 Models

**File**: `backend/src/models/gpx.py`

```python
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime

from src.database import Base
from src.utils.id_generator import generate_uuid


class GPXFile(Base):
    """GPX file metadata and processing results."""

    __tablename__ = "gpx_files"

    gpx_file_id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.trip_id", ondelete="CASCADE"), unique=True, nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    distance_km = Column(Float, nullable=False)
    elevation_gain = Column(Float, nullable=True)
    elevation_loss = Column(Float, nullable=True)
    max_elevation = Column(Float, nullable=True)
    min_elevation = Column(Float, nullable=True)
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    total_points = Column(Integer, nullable=False)
    simplified_points = Column(Integer, nullable=False)
    has_elevation = Column(Boolean, nullable=False)
    has_timestamps = Column(Boolean, nullable=False)
    processing_status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    processed_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="gpx_file")
    track_points: Mapped[List["TrackPoint"]] = relationship(
        "TrackPoint",
        back_populates="gpx_file",
        order_by="TrackPoint.sequence",
        cascade="all, delete-orphan"
    )


class TrackPoint(Base):
    """Simplified GPS trackpoint for map rendering."""

    __tablename__ = "track_points"

    point_id = Column(String(36), primary_key=True, default=generate_uuid)
    gpx_file_id = Column(String(36), ForeignKey("gpx_files.gpx_file_id", ondelete="CASCADE"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=False)
    sequence = Column(Integer, nullable=False)
    gradient = Column(Float, nullable=True)

    # Relationships
    gpx_file: Mapped["GPXFile"] = relationship("GPXFile", back_populates="track_points")

    __table_args__ = (
        Index("idx_track_points_gpx", "gpx_file_id"),
        Index("idx_track_points_seq", "gpx_file_id", "sequence"),
    )
```

### Extension to Existing Trip Model

**File**: `backend/src/models/trip.py` (EXTEND)

```python
# Add to Trip class:
gpx_file: Mapped[Optional["GPXFile"]] = relationship(
    "GPXFile",
    back_populates="trip",
    uselist=False,  # 1:1 relationship
    cascade="all, delete-orphan"
)
```

---

## Migration Strategy

### Migration File: `backend/migrations/versions/xxx_create_gpx_tables.py`

```python
"""Create GPX tables for Feature 003 - GPS Routes Interactive

Revision ID: xxx_create_gpx_tables
Revises: [previous_revision]
Create Date: 2026-01-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers
revision = 'xxx_create_gpx_tables'
down_revision = '[previous_revision]'
branch_labels = None
depends_on = None


def upgrade():
    """Create gpx_files and track_points tables."""
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Detect database dialect
    is_postgresql = conn.dialect.name == 'postgresql'

    # Create gpx_files table
    op.create_table(
        'gpx_files',
        sa.Column('gpx_file_id', sa.String(36) if not is_postgresql else sa.UUID(), primary_key=True),
        sa.Column('trip_id', sa.String(36) if not is_postgresql else sa.UUID(), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('distance_km', sa.Float(), nullable=False),
        sa.Column('elevation_gain', sa.Float(), nullable=True),
        sa.Column('elevation_loss', sa.Float(), nullable=True),
        sa.Column('max_elevation', sa.Float(), nullable=True),
        sa.Column('min_elevation', sa.Float(), nullable=True),
        sa.Column('start_lat', sa.Float(), nullable=False),
        sa.Column('start_lon', sa.Float(), nullable=False),
        sa.Column('end_lat', sa.Float(), nullable=False),
        sa.Column('end_lon', sa.Float(), nullable=False),
        sa.Column('total_points', sa.Integer(), nullable=False),
        sa.Column('simplified_points', sa.Integer(), nullable=False),
        sa.Column('has_elevation', sa.Boolean(), nullable=False),
        sa.Column('has_timestamps', sa.Boolean(), nullable=False),
        sa.Column('processing_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.TIMESTAMP(timezone=is_postgresql), nullable=False, server_default=sa.func.now()),
        sa.Column('processed_at', sa.TIMESTAMP(timezone=is_postgresql), nullable=True),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.trip_id'], ondelete='CASCADE'),
        sa.UniqueConstraint('trip_id', name='uq_gpx_files_trip_id')
    )

    op.create_index('idx_gpx_files_trip', 'gpx_files', ['trip_id'])
    op.create_index('idx_gpx_files_status', 'gpx_files', ['processing_status'])

    # Create track_points table
    op.create_table(
        'track_points',
        sa.Column('point_id', sa.String(36) if not is_postgresql else sa.UUID(), primary_key=True),
        sa.Column('gpx_file_id', sa.String(36) if not is_postgresql else sa.UUID(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('elevation', sa.Float(), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('gradient', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['gpx_file_id'], ['gpx_files.gpx_file_id'], ondelete='CASCADE')
    )

    op.create_index('idx_track_points_gpx', 'track_points', ['gpx_file_id'])
    op.create_index('idx_track_points_seq', 'track_points', ['gpx_file_id', 'sequence'])

    if is_postgresql:
        op.create_index(
            'idx_track_points_unique_seq',
            'track_points',
            ['gpx_file_id', 'sequence'],
            unique=True
        )


def downgrade():
    """Drop GPX tables."""
    op.drop_table('track_points')
    op.drop_table('gpx_files')
```

---

## Storage Optimization

### Douglas-Peucker Simplification Impact

| Original Points | Simplified Points | Reduction | Storage Saved | Visual Quality |
|----------------|------------------|-----------|---------------|----------------|
| 10,000 | ~1,000 | 90% | ~900 KB → ~100 KB | <5% distortion |
| 5,000 | ~500 | 90% | ~450 KB → ~50 KB | <5% distortion |
| 1,000 | ~200 | 80% | ~100 KB → ~20 KB | <2% distortion |

**Epsilon Tuning** (research.md):
- **0.0001°**: ~10 meters precision (recommended)
- **0.00005°**: ~5 meters precision (higher fidelity, less reduction)
- **0.0002°**: ~20 meters precision (more aggressive, suitable for long routes)

---

## Database Indexes

Critical indexes for performance (SC-007: <3s map load):

```sql
-- Fast GPX lookup by trip
CREATE INDEX idx_gpx_files_trip ON gpx_files(trip_id);

-- Filter GPX by processing status
CREATE INDEX idx_gpx_files_status ON gpx_files(processing_status);

-- Ordered trackpoint retrieval (for map polyline)
CREATE INDEX idx_track_points_seq ON track_points(gpx_file_id, sequence);

-- Fast POI type filtering (Phase 2)
CREATE INDEX idx_poi_type ON points_of_interest(trip_id, poi_type);
```

---

## Cascade Deletion Behavior

**When a Trip is deleted**:
1. `gpx_files` record is deleted (ON DELETE CASCADE)
2. All associated `track_points` are deleted (ON DELETE CASCADE via gpx_file_id)
3. All associated `points_of_interest` are deleted (ON DELETE CASCADE)
4. All associated `route_statistics` are deleted (ON DELETE CASCADE)
5. Original GPX file is removed from storage (handled by service layer)

This ensures no orphaned GPS data remains in the system (FR-036).

---

## Data Validation Summary

| Field | Rule | Enforced By |
|-------|------|-------------|
| GPX file size | ≤10 MB | API layer (FastAPI UploadFile validation) |
| GPX format | .gpx extension, valid XML | Service layer (gpxpy parsing) |
| Latitude | -90 to 90 | Database CHECK constraint + Pydantic schema |
| Longitude | -180 to 180 | Database CHECK constraint + Pydantic schema |
| Elevation | -420 to 8850 m | Service layer (FR-034 anomaly detection) |
| POI count | ≤20 per trip | Service layer (FR-029) |
| POI name | 1-100 chars | Database CHECK + Pydantic schema |
| POI description | ≤500 chars | Database CHECK + Pydantic schema |

---

## Next Steps

1. Create Alembic migration script
2. Generate Pydantic schemas for API validation
3. Implement GPXService for parsing and track simplification
4. Create API contracts (OpenAPI spec)
5. Update Trip API to include GPX endpoints

**Data model complete**. Ready for contract generation (Phase 1).
