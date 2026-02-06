# Data Model: GPS Trip Creation Wizard

**Feature**: 017-gps-trip-wizard
**Date**: 2026-01-28
**Status**: Phase 1 Design

---

## Overview

The GPS Trip Creation Wizard reuses 95% of existing database schema from Features 002 (Travel Diary), 003 (GPS Routes), and 009 (GPS Coordinates). Only minimal modifications are required: adding the `EXTREME` difficulty level to the enum and changing a constant for POI limits.

**Database Compatibility**: PostgreSQL (production), SQLite (development)

---

## Modified Entities

### 1. Trip (Existing Model)

**File**: `backend/src/models/trip.py`

**Modification**: Add `EXTREME` to `TripDifficulty` enum

```python
class TripDifficulty(str, enum.Enum):
    """Trip difficulty levels based on distance and elevation gain."""
    EASY = "easy"                    # <30km and <500m elevation gain
    MODERATE = "moderate"            # 30-60km or 500-1000m gain
    DIFFICULT = "difficult"          # 60-100km or 1000-1500m gain
    VERY_DIFFICULT = "very_difficult"  # 100-150km or 1500-2500m gain
    EXTREME = "extreme"              # >150km or >2500m gain (NEW)
```

**Rationale**: Spec assumption #1 mentions ">150km or >2500m desnivel" which requires the EXTREME level that doesn't currently exist in the enum.

**Impact**:
- No database column changes (enum stored as string)
- Requires Alembic migration to update enum constraint
- Backward compatible (existing trips remain valid)

---

### 2. GPXFile (Existing Model - No Changes)

**File**: `backend/src/models/gpx_file.py` (from Feature 003)

**Schema** (reference only, no modifications):
```python
class GPXFile(Base):
    __tablename__ = "gpx_files"

    gpx_file_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.trip_id"))
    file_url: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[int]

    # Telemetry data (extracted during processing)
    total_distance_km: Mapped[float]
    elevation_gain: Mapped[float | None]
    elevation_loss: Mapped[float | None]
    max_elevation: Mapped[float | None]
    min_elevation: Mapped[float | None]
    has_elevation: Mapped[bool] = mapped_column(default=False)
    has_timestamps: Mapped[bool] = mapped_column(default=False)

    # Processing status
    processing_status: Mapped[str] = mapped_column(
        String(20),
        default="pending"  # pending, processing, completed, failed
    )

    # Timestamps
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

**Wizard Usage**: The wizard will create a GPXFile record on publish (Step 4), reusing the existing upload flow from Feature 003.

---

### 3. PointOfInterest (Existing Model - Constant Change Only)

**File**: `backend/src/models/poi.py` (from Feature 003)

**Schema** (reference only, no modifications):
```python
class PointOfInterest(Base):
    __tablename__ = "points_of_interest"

    poi_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.trip_id"))

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))  # Max 500 chars (spec clarification #2)
    poi_type: Mapped[POIType]  # VIEWPOINT, TOWN, WATER, FOOD, etc.

    latitude: Mapped[float]
    longitude: Mapped[float]
    distance_from_start_km: Mapped[float | None]

    photo_url: Mapped[str | None] = mapped_column(String(500))
    sequence: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime]
```

**Constant Change** (file: `backend/src/utils/constants.py` or `backend/src/services/poi_service.py`):
```python
# OLD:
MAX_POIS_PER_TRIP = 20

# NEW:
MAX_POIS_PER_TRIP = 6  # Aligned with spec FR-011
```

**Validation**:
- Backend: Enforce max 6 POIs in `poi_service.create_poi()` (already exists, just change constant)
- Frontend: Disable "Añadir POI" button after 6 POIs in wizard Step 3

---

## New Pydantic Schemas

### GPX Wizard Schemas

**File**: `backend/src/schemas/gpx_wizard.py` (NEW)

```python
from pydantic import BaseModel, Field
from fastapi import UploadFile
from src.models.trip import TripDifficulty
from src.schemas.trip import TripCreateInput
from src.schemas.poi import POICreateInput

class GPXAnalysisRequest(BaseModel):
    """
    Request schema for temporary GPX analysis endpoint.

    Note: The GPX file is uploaded as multipart/form-data,
    not as part of this schema. This exists for documentation only.
    """
    pass


class GPXTelemetry(BaseModel):
    """
    Telemetry data extracted from GPX file for wizard preview.

    This is returned by POST /gpx/analyze without storing to database.
    """
    distance_km: float = Field(
        ...,
        ge=0,
        description="Total distance in kilometers",
        example=42.5
    )
    elevation_gain: float | None = Field(
        None,
        ge=0,
        description="Cumulative uphill in meters",
        example=1250.0
    )
    elevation_loss: float | None = Field(
        None,
        ge=0,
        description="Cumulative downhill in meters",
        example=1100.0
    )
    max_elevation: float | None = Field(
        None,
        description="Maximum altitude in meters",
        example=1850.0
    )
    min_elevation: float | None = Field(
        None,
        description="Minimum altitude in meters",
        example=450.0
    )
    has_elevation: bool = Field(
        ...,
        description="Whether GPX contains elevation data"
    )
    difficulty: TripDifficulty = Field(
        ...,
        description="Auto-calculated difficulty from distance + elevation"
    )

    class Config:
        schema_extra = {
            "example": {
                "distance_km": 42.5,
                "elevation_gain": 1250.0,
                "elevation_loss": 1100.0,
                "max_elevation": 1850.0,
                "min_elevation": 450.0,
                "has_elevation": True,
                "difficulty": "difficult"
            }
        }


class GPXAnalysisResponse(BaseModel):
    """Standard API response for /gpx/analyze endpoint."""
    success: bool
    data: GPXTelemetry | None = None
    error: dict | None = None


class GPXTripCreateInput(TripCreateInput):
    """
    Extended schema for creating trip via GPX wizard.

    Extends the standard TripCreateInput with GPX file and POIs.
    Used by POST /trips/gpx-wizard endpoint.
    """
    gpx_file: UploadFile = Field(
        ...,
        description="GPX file (required for wizard, max 10MB)"
    )
    pois: list[POICreateInput] = Field(
        default=[],
        max_length=6,
        description="POIs to create atomically with trip"
    )

    class Config:
        arbitrary_types_allowed = True  # Required for UploadFile
```

---

## Database Migrations

### Migration: Add EXTREME Difficulty Level

**File**: `backend/migrations/versions/XXX_add_extreme_difficulty.py` (to be generated)

**Type**: Enum extension (backward compatible)

**SQL** (PostgreSQL):
```sql
-- Up migration
ALTER TYPE tripdifficulty ADD VALUE IF NOT EXISTS 'extreme';

-- Down migration
-- Note: PostgreSQL doesn't support removing enum values directly
-- Workaround: Create new enum without 'extreme', migrate data, drop old enum
-- For this case, rollback is not critical since 'extreme' is additive
```

**SQL** (SQLite - development only):
```sql
-- SQLite stores enums as TEXT with CHECK constraint
-- No migration needed (constraint is application-level)
-- Existing trips remain valid
```

**Alembic Revision**:
```python
"""Add EXTREME difficulty level

Revision ID: XXX
Revises: YYY
Create Date: 2026-01-28

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'XXX'
down_revision = 'YYY'  # Previous migration
branch_labels = None
depends_on = None


def upgrade():
    # PostgreSQL: Add EXTREME to enum
    op.execute("ALTER TYPE tripdifficulty ADD VALUE IF NOT EXISTS 'extreme'")

    # SQLite: No action needed (enums stored as TEXT)


def downgrade():
    # Rollback not supported for enum extension
    # Existing 'extreme' trips would become invalid
    pass
```

**Testing**:
```python
# backend/tests/unit/test_migrations.py

async def test_extreme_difficulty_migration():
    """Verify EXTREME difficulty level is added to enum."""
    # Apply migration
    alembic_upgrade()

    # Create trip with EXTREME difficulty
    trip = Trip(
        title="Ultra Endurance Route",
        difficulty=TripDifficulty.EXTREME,
        # ... other fields
    )
    db.add(trip)
    db.commit()

    # Verify trip saved correctly
    assert trip.difficulty == TripDifficulty.EXTREME

    # Verify existing trips unaffected
    old_trip = db.query(Trip).filter_by(difficulty="difficult").first()
    assert old_trip is not None
```

---

## Validation Rules

### Trip Difficulty Calculation

**Business Rule** (from spec clarification #1):
```python
def calculate_difficulty(
    distance_km: float,
    elevation_gain: float | None
) -> TripDifficulty:
    """
    Calculate trip difficulty from GPX telemetry.

    Logic: Use WHICHEVER metric is higher (distance OR elevation).
    If no elevation data, use distance only.

    Thresholds (from spec assumption #1):
    - EASY: <30km and <500m elevation gain
    - MODERATE: 30-60km or 500-1000m gain
    - DIFFICULT: 60-100km or 1000-1500m gain
    - VERY_DIFFICULT: 100-150km or 1500-2500m gain
    - EXTREME: >150km or >2500m gain

    Examples:
    - 40km, 1200m gain → DIFFICULT (elevation dominates)
    - 120km, 800m gain → VERY_DIFFICULT (distance dominates)
    - 180km, 3000m gain → EXTREME (both exceed thresholds)
    """
    if distance_km < 30 and (elevation_gain is None or elevation_gain < 500):
        return TripDifficulty.EASY

    if distance_km < 60 and (elevation_gain is None or elevation_gain < 1000):
        return TripDifficulty.MODERATE

    if distance_km < 100 and (elevation_gain is None or elevation_gain < 1500):
        return TripDifficulty.DIFFICULT

    if distance_km < 150 and (elevation_gain is None or elevation_gain < 2500):
        return TripDifficulty.VERY_DIFFICULT

    return TripDifficulty.EXTREME
```

**Implementation File**: `backend/src/services/difficulty_calculator.py` (NEW)

**Validation**:
- Unit tests: Test all 5 difficulty levels with edge cases
- Integration tests: Verify calculation matches spec SC-003 (80% accuracy)
- User cannot override (read-only in wizard Step 2)

---

### POI Validation

**Existing Validation** (from Feature 003):
- Max POIs per trip: 20 → Change to **6** (spec FR-011)
- Name: Required, max 100 chars
- Description: Optional, max 500 chars (spec clarification #2)
- Coordinates: Required (latitude: -90 to 90, longitude: -180 to 180)
- Photo: Optional, max 5MB (spec assumption #7)

**Wizard-Specific Validation**:
- Frontend: Disable "Añadir POI" button after 6 POIs (Step 3)
- Backend: Reject batch creation if `len(pois) > 6`

---

## Entity Relationships

```
User (existing)
  ↓ 1:N
Trip (existing)
  ↓ 1:1 (optional)
GPXFile (existing from Feature 003)

Trip
  ↓ 1:N
PointOfInterest (existing from Feature 003)
  ↓ 1:N (future: change to 1:2 for 2 photos per POI)
POIPhoto (not implemented yet)
```

**Notes**:
- Spec mentions "hasta 2 fotos" per POI (FR-010), but current implementation supports 1 photo via `photo_url` field
- **Decision Required**: Update POI model to support 2 photos or clarify spec to 1 photo
- Recommendation: Keep 1 photo for MVP, add 2nd photo in future enhancement

---

## Data Flow: Wizard to Database

**Step 1** (GPX Upload):
- User uploads GPX file
- `POST /gpx/analyze` extracts telemetry (no DB storage)
- Returns `GPXTelemetry` for wizard preview

**Step 2-3** (Details + POIs):
- Data stored in wizard state (React Hook Form)
- No database writes yet

**Step 4** (Publish):
- **Atomic transaction**:
  1. `POST /trips/gpx-wizard` creates Trip record
  2. Upload GPX file to storage → Create GPXFile record
  3. Batch create POIs (loop up to 6 times)
  4. Commit transaction or rollback on error

**Error Handling**:
```python
async def create_trip_with_gpx_wizard(
    trip_data: GPXTripCreateInput,
    current_user: User,
    db: AsyncSession
) -> Trip:
    """Atomic trip creation with GPX and POIs."""
    async with db.begin():  # Transaction
        try:
            # 1. Create trip
            trip = Trip(...)
            db.add(trip)
            await db.flush()  # Get trip_id

            # 2. Upload GPX
            gpx_file = await gpx_service.upload_gpx(
                trip_id=trip.trip_id,
                file_content=trip_data.gpx_file
            )

            # 3. Create POIs
            for poi_data in trip_data.pois:
                poi = PointOfInterest(trip_id=trip.trip_id, ...)
                db.add(poi)

            await db.commit()
            return trip

        except Exception as e:
            await db.rollback()
            logger.error(f"Wizard publish failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error al publicar viaje. Intenta de nuevo."
            )
```

---

## Performance Considerations

**Telemetry Extraction** (Step 1):
- Target: <2s for files up to 10MB (SC-002 allows <30s for full processing)
- Optimization: Extract only distance + elevation, skip track simplification
- Implementation: `GPXService.extract_telemetry_quick()` (NEW method)

**Batch POI Creation** (Step 4):
- Max 6 POIs → 6 sequential INSERT statements
- Total time: <100ms (negligible compared to GPX upload)
- Alternative rejected: Single bulk insert → More complex, minimal performance gain

**Full GPX Processing** (Step 4):
- Async background task for files >1MB (Feature 003 pattern)
- User sees trip immediately, map renders progressively as GPX processes

---

## Testing Strategy

### Unit Tests

**File**: `backend/tests/unit/test_difficulty_calculator.py`
```python
@pytest.mark.parametrize("distance,elevation,expected", [
    (20, 300, TripDifficulty.EASY),
    (50, 800, TripDifficulty.MODERATE),
    (80, 1200, TripDifficulty.DIFFICULT),
    (130, 2000, TripDifficulty.VERY_DIFFICULT),
    (180, 3000, TripDifficulty.EXTREME),
    (160, 800, TripDifficulty.EXTREME),  # Distance dominates
    (80, 2700, TripDifficulty.EXTREME),  # Elevation dominates
])
async def test_difficulty_calculation(distance, elevation, expected):
    result = calculate_difficulty(distance, elevation)
    assert result == expected
```

### Integration Tests

**File**: `backend/tests/integration/test_trip_gpx_workflow.py`
```python
async def test_wizard_publish_creates_trip_gpx_pois(client, auth_headers, test_gpx):
    """Test full wizard flow: upload GPX + create trip + POIs."""
    # Step 1: Analyze GPX
    response = await client.post(
        "/gpx/analyze",
        headers=auth_headers,
        files={"file": test_gpx}
    )
    assert response.status_code == 200
    telemetry = response.json()["data"]

    # Step 4: Publish with 3 POIs
    response = await client.post(
        "/trips/gpx-wizard",
        headers=auth_headers,
        files={"gpx_file": test_gpx},
        data={
            "title": "Test Route",
            "description": "A" * 50,  # Min 50 chars
            "pois": json.dumps([
                {"name": "POI 1", "latitude": 42.5, "longitude": 1.2},
                {"name": "POI 2", "latitude": 42.6, "longitude": 1.3},
                {"name": "POI 3", "latitude": 42.7, "longitude": 1.4},
            ])
        }
    )

    assert response.status_code == 201
    trip = response.json()["data"]

    # Verify trip created
    assert trip["title"] == "Test Route"
    assert trip["difficulty"] == telemetry["difficulty"]

    # Verify GPX linked
    assert trip["gpx_file"] is not None
    assert trip["gpx_file"]["total_distance_km"] == telemetry["distance_km"]

    # Verify POIs created
    assert len(trip["pois"]) == 3
```

---

## Summary

**Database Changes**: Minimal (1 enum extension, 1 constant change)

**New Entities**: 0 (reuse existing Trip, GPXFile, POI)

**New Schemas**: 4 Pydantic schemas (GPXAnalysisRequest, GPXTelemetry, GPXAnalysisResponse, GPXTripCreateInput)

**Migrations**: 1 Alembic migration (add EXTREME to TripDifficulty enum)

**Backward Compatibility**: ✅ Full (additive changes only)

**Risk**: 🟢 LOW (95% schema reuse, proven patterns)

---

**Date**: 2026-01-28
**Feature**: 017-gps-trip-wizard
**Status**: Phase 1 Design Complete
**Next**: Generate API contracts (contracts/gpx-wizard.yaml)
