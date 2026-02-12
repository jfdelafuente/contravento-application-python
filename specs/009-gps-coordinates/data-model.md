# Data Model: GPS Coordinates for Trip Locations

**Feature**: 009-gps-coordinates
**Date**: 2026-01-11
**Status**: Design Complete

## Overview

This document defines the data model updates required to support GPS coordinates for trip locations. The TripLocation model already has `latitude` and `longitude` columns (nullable Float), so **NO DATABASE MIGRATION IS NEEDED**. This feature only requires:
1. Backend schema updates to accept coordinate input
2. Validation logic for coordinate ranges
3. Frontend type updates to support coordinate input

---

## Entity Updates

### TripLocation (Backend Model)

**File**: `backend/src/models/trip.py`

**Current Model** (NO CHANGES NEEDED):
```python
class TripLocation(Base):
    """Represents a location visited during a trip."""
    __tablename__ = "trip_locations"

    location_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id: Mapped[str] = mapped_column(String(36), ForeignKey("trips.trip_id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)  # Location name (e.g., "Madrid")
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)   # Decimal degrees -90 to 90
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Decimal degrees -180 to 180
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)  # Order along route (0-based)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationship
    trip: Mapped["Trip"] = relationship("Trip", back_populates="locations")
```

**Key Points**:
- `latitude` and `longitude` already exist as nullable Float columns
- No migration needed (columns created in previous feature)
- Precision: Float supports 6 decimal places (~0.11m accuracy)
- Range validation handled in Pydantic schema (not database constraints)

---

## Schema Updates

### LocationInput (Backend Pydantic Schema)

**File**: `backend/src/schemas/trip.py`

**Current Schema**:
```python
class LocationInput(BaseModel):
    """Schema for location input (trip creation/update)."""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre de la ubicación")
    country: Optional[str] = Field(None, max_length=100, description="País (opcional)")
```

**Updated Schema** (ADD coordinate fields):
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class LocationInput(BaseModel):
    """Schema for location input with optional GPS coordinates."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre de la ubicación"
    )

    country: Optional[str] = Field(
        None,
        max_length=100,
        description="País (opcional, no se almacena actualmente)"
    )

    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Latitud en grados decimales (opcional, -90 a 90)"
    )

    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Longitud en grados decimales (opcional, -180 a 180)"
    )

    @field_validator('latitude', 'longitude')
    @classmethod
    def round_coordinates(cls, v: Optional[float]) -> Optional[float]:
        """Enforce 6 decimal places precision for coordinates."""
        if v is None:
            return v
        return round(v, 6)

    @field_validator('latitude')
    @classmethod
    def validate_latitude_range(cls, v: Optional[float]) -> Optional[float]:
        """Validate latitude range with Spanish error message."""
        if v is not None and not -90 <= v <= 90:
            raise ValueError('Latitud debe estar entre -90 y 90 grados')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude_range(cls, v: Optional[float]) -> Optional[float]:
        """Validate longitude range with Spanish error message."""
        if v is not None and not -180 <= v <= 180:
            raise ValueError('Longitud debe estar entre -180 y 180 grados')
        return v
```

**Changes**:
- ✅ Added `latitude` field (optional Float, -90 to 90 range)
- ✅ Added `longitude` field (optional Float, -180 to 180 range)
- ✅ Pydantic `Field()` constraints for basic validation
- ✅ Custom validators for decimal precision (6 places) and Spanish error messages
- ⚠️ `country` field still accepted but NOT stored (noted in description)

---

### TripLocationResponse (Backend Response Schema)

**File**: `backend/src/schemas/trip.py`

**Current Schema** (NO CHANGES NEEDED):
```python
class TripLocationResponse(BaseModel):
    """Schema for location response (trip details)."""
    location_id: str
    name: str
    latitude: Optional[float]  # Already supports null coordinates
    longitude: Optional[float]  # Already supports null coordinates
    sequence: int

    model_config = ConfigDict(from_attributes=True)
```

**Key Points**:
- Schema already returns `latitude` and `longitude` (nullable)
- Frontend already expects these fields (TypeScript `TripLocation` interface)
- No changes needed

---

## Frontend Type Updates

### TripLocation Interface

**File**: `frontend/src/types/trip.ts`

**Current Interface** (NO CHANGES NEEDED):
```typescript
export interface TripLocation {
  location_id: string;
  name: string;
  latitude: number | null;   // Already supports null
  longitude: number | null;  // Already supports null
  sequence: number;
}
```

---

### LocationInput Interface

**File**: `frontend/src/types/trip.ts`

**Current Interface**:
```typescript
export interface LocationInput {
  name: string;        // 1-200 characters
  country?: string;    // Max 100 characters (optional)
}
```

**Updated Interface** (ADD coordinate fields):
```typescript
export interface LocationInput {
  name: string;              // 1-200 characters (required)
  country?: string;          // Max 100 characters (optional, not stored)
  latitude?: number | null;  // Decimal degrees -90 to 90 (optional)
  longitude?: number | null; // Decimal degrees -180 to 180 (optional)
}
```

**Changes**:
- ✅ Added `latitude` field (optional number or null)
- ✅ Added `longitude` field (optional number or null)
- ⚠️ `country` still accepted but backend doesn't store it

---

## Validation Rules

### Backend Validation (Pydantic)

| Field      | Type           | Required | Constraints                          | Error Message (Spanish)                      |
|------------|----------------|----------|--------------------------------------|---------------------------------------------|
| `name`     | `str`          | ✅ Yes   | 1-200 chars                          | "Nombre de ubicación requerido"             |
| `country`  | `str`          | ❌ No    | Max 100 chars                        | -                                           |
| `latitude` | `float`        | ❌ No    | -90 ≤ value ≤ 90, 6 decimals         | "Latitud debe estar entre -90 y 90 grados"  |
| `longitude`| `float`        | ❌ No    | -180 ≤ value ≤ 180, 6 decimals       | "Longitud debe estar entre -180 y 180 grados"|

**Precision Enforcement**:
- All coordinates rounded to 6 decimal places via `round_coordinates` validator
- Example: `40.4167754` → `40.416775` (6 decimals = ~0.11m accuracy at equator)

---

### Frontend Validation (Zod)

**File**: `frontend/src/utils/tripValidators.ts`

**New Validation Schema**:
```typescript
import { z } from 'zod';

export const locationInputSchema = z.object({
  name: z.string()
    .min(1, 'Nombre de ubicación requerido')
    .max(200, 'Nombre debe tener máximo 200 caracteres'),

  country: z.string()
    .max(100, 'País debe tener máximo 100 caracteres')
    .optional(),

  latitude: z.number()
    .min(-90, 'Latitud debe estar entre -90 y 90 grados')
    .max(90, 'Latitud debe estar entre -90 y 90 grados')
    .nullable()
    .optional()
    .refine(
      (val) => val === null || val === undefined || Number(val.toFixed(6)) === val,
      { message: 'Latitud debe tener máximo 6 decimales' }
    ),

  longitude: z.number()
    .min(-180, 'Longitud debe estar entre -180 y 180 grados')
    .max(180, 'Longitud debe estar entre -180 y 180 grados')
    .nullable()
    .optional()
    .refine(
      (val) => val === null || val === undefined || Number(val.toFixed(6)) === val,
      { message: 'Longitud debe tener máximo 6 decimales' }
    ),
});

export type LocationInputFormData = z.infer<typeof locationInputSchema>;
```

---

## Database DDL

### SQLite (Development)

**NO MIGRATION NEEDED** - Columns already exist:

```sql
-- Existing schema (from previous feature migration)
CREATE TABLE trip_locations (
    location_id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    name TEXT NOT NULL,
    latitude REAL NULL,           -- Already exists (REAL = Float in SQLite)
    longitude REAL NULL,          -- Already exists
    sequence INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
);

-- No new indexes needed (coordinates not queried for filtering)
```

---

### PostgreSQL (Production)

**NO MIGRATION NEEDED** - Columns already exist:

```sql
-- Existing schema (from previous feature migration)
CREATE TABLE trip_locations (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL REFERENCES trips(trip_id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    latitude DOUBLE PRECISION NULL,    -- Already exists (supports 15 decimal digits)
    longitude DOUBLE PRECISION NULL,   -- Already exists
    sequence INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- No new indexes needed
```

**Key Points**:
- PostgreSQL `DOUBLE PRECISION` supports 15-17 significant digits (more than enough for 6 decimal places)
- Nullable columns (`NULL`) support backwards compatibility
- Existing trips have `latitude = NULL` and `longitude = NULL`

---

## Service Layer Updates

### TripService._process_locations()

**File**: `backend/src/services/trip_service.py`

**Current Implementation**:
```python
async def _process_locations(self, trip: Trip, locations: list[LocationInput]) -> None:
    """Creates TripLocation entities with sequence ordering."""
    for sequence, location_data in enumerate(locations):
        location = TripLocation(
            trip_id=trip.trip_id,
            name=location_data.name,
            # Note: country field is not stored (TripLocation model has no country column)
            # Geocoding will be added in future phases
            sequence=sequence,
        )
        self.db.add(location)
```

**Updated Implementation** (ADD coordinate storage):
```python
async def _process_locations(self, trip: Trip, locations: list[LocationInput]) -> None:
    """Creates TripLocation entities with sequence ordering and optional coordinates."""
    for sequence, location_data in enumerate(locations):
        location = TripLocation(
            trip_id=trip.trip_id,
            name=location_data.name,
            latitude=location_data.latitude,   # NEW: Store latitude (nullable)
            longitude=location_data.longitude, # NEW: Store longitude (nullable)
            # Note: country field is not stored (TripLocation model has no country column)
            sequence=sequence,
        )
        self.db.add(location)
```

**Changes**:
- ✅ Added `latitude=location_data.latitude` (passes through from input, can be None)
- ✅ Added `longitude=location_data.longitude` (passes through from input, can be None)
- ⚠️ `country` still not stored (TripLocation model has no `country` column)

---

## State Transitions

**N/A** - GPS coordinates are static data, not state-based.

**Coordinate Lifecycle**:
1. **Input**: User enters coordinates in trip creation/edit form (optional)
2. **Validation**: Pydantic validates ranges and precision (server-side)
3. **Storage**: Coordinates stored in `trip_locations` table (nullable)
4. **Retrieval**: Coordinates returned in `TripLocationResponse` (can be null)
5. **Display**: TripMap component filters locations with non-null coordinates

**No State Machine** - Coordinates don't transition between states (DRAFT/PUBLISHED applies to Trip, not coordinates).

---

## Edge Cases

### 1. Mix of Locations With and Without Coordinates

**Scenario**: Trip has 3 locations:
- Location 1: "Madrid" (lat: 40.416775, lng: -3.703790)
- Location 2: "Toledo" (lat: null, lng: null)
- Location 3: "Segovia" (lat: 40.948882, lng: -4.118268)

**Behavior**:
- Backend: Stores all 3 locations (coordinates nullable)
- Frontend: TripMap filters to valid locations (Madrid, Segovia only)
- Map displays 2 markers with polyline connecting them
- Toledo excluded from map but visible in location list

**Code Reference**: `frontend/src/components/trips/TripMap.tsx:43-45`
```typescript
const validLocations = locations.filter(
  loc => loc.latitude !== null && loc.longitude !== null
);
```

---

### 2. Coordinates Outside Valid Range

**Scenario**: User enters latitude = 100 (invalid, must be -90 to 90)

**Behavior**:
- Frontend validation (Zod): Prevents form submission, shows error: "Latitud debe estar entre -90 y 90 grados"
- Backend validation (Pydantic): If frontend bypassed, returns 422 Unprocessable Entity with field-specific error
- Database: Rejects invalid data before reaching database

**Test Case**:
```python
# backend/tests/unit/test_coordinate_validation.py
def test_latitude_out_of_range():
    with pytest.raises(ValidationError) as exc_info:
        LocationInput(name="Madrid", latitude=100.0, longitude=-3.703790)
    assert "Latitud debe estar entre -90 y 90 grados" in str(exc_info.value)
```

---

### 3. Coordinates with Too Many Decimals

**Scenario**: User enters latitude = 40.123456789 (9 decimals, max allowed is 6)

**Behavior**:
- Frontend: `<input step="0.000001">` limits precision in UI
- Backend: `round_coordinates` validator rounds to 6 decimals
- Stored value: 40.123457 (rounded to 6 decimals)

**Rationale**: 6 decimal places = ~0.11m accuracy at equator (sufficient for cycling trip visualization)

---

### 4. Null vs 0 Coordinates

**Scenario**: What if user enters latitude = 0, longitude = 0 (valid coordinates, but rare for cycling trips)?

**Behavior**:
- (0, 0) is valid (Gulf of Guinea off Africa coast)
- Map displays marker at that location
- Different from `null` (no coordinates)

**Validation**: System accepts (0, 0) as valid coordinates (no special handling).

---

## Summary

**Schema Changes**:
- ✅ Backend `LocationInput` schema: Added `latitude` and `longitude` (optional Float)
- ✅ Frontend `LocationInput` interface: Added `latitude` and `longitude` (optional number)
- ❌ No database migration needed (columns already exist)
- ❌ No model changes (TripLocation already has coordinate columns)

**Validation**:
- ✅ Pydantic validators: Range validation (-90 to 90, -180 to 180) + precision (6 decimals)
- ✅ Zod schema: Client-side validation matching backend rules
- ✅ Spanish error messages for UX consistency

**Backwards Compatibility**:
- ✅ Coordinates optional (nullable)
- ✅ Existing trips work without coordinates
- ✅ TripMap already handles null coordinates gracefully

---

**Phase 1 Data Model Status**: ✅ COMPLETE

Ready for contracts generation and quickstart guide.
