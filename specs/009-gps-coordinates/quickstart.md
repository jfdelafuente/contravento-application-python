# Developer Quickstart: GPS Coordinates for Trip Locations

**Feature**: 009-gps-coordinates
**Date**: 2026-01-11
**Estimated Setup Time**: 15 minutes

## Overview

This guide helps you implement GPS coordinate support for trip locations. The feature allows users to manually enter latitude/longitude coordinates during trip creation/editing, enabling interactive map visualization of cycling routes.

**Key Deliverables**:
- Backend: Update `LocationInput` schema to accept optional coordinates
- Backend: Add coordinate validation (ranges, precision)
- Backend: Update `TripService._process_locations()` to store coordinates
- Frontend: Create `LocationInput` component with coordinate fields
- Frontend: Update trip creation form to include location coordinates
- Testing: Coordinate validation tests (unit + integration)

---

## Prerequisites

### Backend
- Python 3.12 installed
- Poetry dependency manager
- Backend server running locally (`./run-local-dev.sh` or `cd backend && poetry run uvicorn src.main:app --reload`)

### Frontend
- Node.js 18+ and npm installed
- Frontend dev server running (`cd frontend && npm run dev`)

### Database
- **NO MIGRATION NEEDED** - TripLocation model already has `latitude` and `longitude` columns (nullable Float)
- Existing trips have `latitude = NULL` and `longitude = NULL` (backwards compatible)

---

## Backend Setup (15 minutes)

### Step 1: Update LocationInput Schema (5 min)

**File**: `backend/src/schemas/trip.py`

**Add coordinate fields to LocationInput**:

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

    # NEW: GPS coordinate fields
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

**What this does**:
- Adds optional `latitude` and `longitude` fields to location input
- Validates coordinate ranges (-90 to 90, -180 to 180)
- Rounds coordinates to 6 decimal places (~0.11m precision)
- Returns Spanish error messages for validation failures

---

### Step 2: Update TripService to Store Coordinates (2 min)

**File**: `backend/src/services/trip_service.py`

**Find the `_process_locations` method (around line 265)** and update it:

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

**What this does**:
- Passes through `latitude` and `longitude` from input to model
- Coordinates can be `None` (backwards compatible)
- No geocoding logic needed (manual entry only)

---

### Step 3: Write Backend Tests (8 min)

**Create**: `backend/tests/unit/test_coordinate_validation.py`

```python
"""Unit tests for GPS coordinate validation."""
import pytest
from pydantic import ValidationError
from src.schemas.trip import LocationInput


class TestCoordinateValidation:
    """Test GPS coordinate range and precision validation."""

    def test_valid_coordinates(self):
        """Test valid latitude/longitude within ranges."""
        location = LocationInput(
            name="Madrid",
            latitude=40.416775,
            longitude=-3.703790
        )
        assert location.latitude == 40.416775
        assert location.longitude == -3.703790

    def test_coordinates_optional(self):
        """Test coordinates are optional (nullable)."""
        location = LocationInput(name="Toledo")
        assert location.latitude is None
        assert location.longitude is None

    def test_latitude_out_of_range_positive(self):
        """Test latitude > 90 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(name="Invalid", latitude=100.0, longitude=0.0)
        assert "Latitud debe estar entre -90 y 90 grados" in str(exc_info.value)

    def test_latitude_out_of_range_negative(self):
        """Test latitude < -90 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(name="Invalid", latitude=-100.0, longitude=0.0)
        assert "Latitud debe estar entre -90 y 90 grados" in str(exc_info.value)

    def test_longitude_out_of_range_positive(self):
        """Test longitude > 180 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(name="Invalid", latitude=0.0, longitude=200.0)
        assert "Longitud debe estar entre -180 y 180 grados" in str(exc_info.value)

    def test_longitude_out_of_range_negative(self):
        """Test longitude < -180 is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            LocationInput(name="Invalid", latitude=0.0, longitude=-200.0)
        assert "Longitud debe estar entre -180 y 180 grados" in str(exc_info.value)

    def test_coordinate_precision_rounded(self):
        """Test coordinates are rounded to 6 decimal places."""
        location = LocationInput(
            name="Test",
            latitude=40.123456789,  # 9 decimals
            longitude=-3.987654321  # 9 decimals
        )
        assert location.latitude == 40.123457  # Rounded to 6 decimals
        assert location.longitude == -3.987654  # Rounded to 6 decimals

    def test_null_latitude_with_valid_longitude(self):
        """Test one coordinate can be null while other is valid."""
        location = LocationInput(
            name="Test",
            latitude=None,
            longitude=-3.703790
        )
        assert location.latitude is None
        assert location.longitude == -3.703790

    def test_edge_case_zero_coordinates(self):
        """Test (0, 0) is valid (Gulf of Guinea)."""
        location = LocationInput(name="Ocean", latitude=0.0, longitude=0.0)
        assert location.latitude == 0.0
        assert location.longitude == 0.0

    def test_edge_case_max_latitude(self):
        """Test latitude = 90 (North Pole) is valid."""
        location = LocationInput(name="North Pole", latitude=90.0, longitude=0.0)
        assert location.latitude == 90.0

    def test_edge_case_min_latitude(self):
        """Test latitude = -90 (South Pole) is valid."""
        location = LocationInput(name="South Pole", latitude=-90.0, longitude=0.0)
        assert location.latitude == -90.0

    def test_edge_case_max_longitude(self):
        """Test longitude = 180 (International Date Line) is valid."""
        location = LocationInput(name="Dateline", latitude=0.0, longitude=180.0)
        assert location.longitude == 180.0

    def test_edge_case_min_longitude(self):
        """Test longitude = -180 (International Date Line) is valid."""
        location = LocationInput(name="Dateline", latitude=0.0, longitude=-180.0)
        assert location.longitude == -180.0
```

**Run tests**:
```bash
cd backend
poetry run pytest tests/unit/test_coordinate_validation.py -v
```

**Expected**: All 13 tests pass ✅

---

## Frontend Setup (15 minutes)

### Step 1: Update LocationInput TypeScript Interface (2 min)

**File**: `frontend/src/types/trip.ts`

**Find the `LocationInput` interface and update it**:

```typescript
export interface LocationInput {
  name: string;              // 1-200 characters (required)
  country?: string;          // Max 100 characters (optional, not stored)
  latitude?: number | null;  // NEW: Decimal degrees -90 to 90 (optional)
  longitude?: number | null; // NEW: Decimal degrees -180 to 180 (optional)
}
```

---

### Step 2: Add Coordinate Validation (Zod Schema) (3 min)

**File**: `frontend/src/utils/tripValidators.ts`

**Add location validation schema**:

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
    .optional(),

  longitude: z.number()
    .min(-180, 'Longitud debe estar entre -180 y 180 grados')
    .max(180, 'Longitud debe estar entre -180 y 180 grados')
    .nullable()
    .optional(),
});

export type LocationInputFormData = z.infer<typeof locationInputSchema>;
```

---

### Step 3: Create LocationInput Component (5 min)

**Create**: `frontend/src/components/trips/TripForm/LocationInput.tsx`

```typescript
import React from 'react';
import './LocationInput.css';

interface LocationInputProps {
  /** Location index in array */
  index: number;

  /** Current location data */
  value: {
    name: string;
    latitude?: number | null;
    longitude?: number | null;
  };

  /** Callback when location data changes */
  onChange: (index: number, field: string, value: string | number | null) => void;

  /** Callback when location is removed */
  onRemove: (index: number) => void;

  /** Validation errors for this location */
  errors?: {
    name?: string;
    latitude?: string;
    longitude?: string;
  };
}

export const LocationInput: React.FC<LocationInputProps> = ({
  index,
  value,
  onChange,
  onRemove,
  errors,
}) => {
  return (
    <div className="location-input">
      <div className="location-input__header">
        <h4 className="location-input__title">Ubicación {index + 1}</h4>
        <button
          type="button"
          onClick={() => onRemove(index)}
          className="location-input__remove-button"
          aria-label="Eliminar ubicación"
        >
          ✕
        </button>
      </div>

      {/* Location Name */}
      <div className="location-input__field">
        <label htmlFor={`location-name-${index}`} className="location-input__label">
          Nombre <span className="location-input__required">*</span>
        </label>
        <input
          id={`location-name-${index}`}
          type="text"
          value={value.name}
          onChange={(e) => onChange(index, 'name', e.target.value)}
          placeholder="Ej: Madrid, Barcelona, Pirineos..."
          className={`location-input__input ${errors?.name ? 'location-input__input--error' : ''}`}
          maxLength={200}
        />
        {errors?.name && (
          <p className="location-input__error">{errors.name}</p>
        )}
      </div>

      {/* GPS Coordinates */}
      <div className="location-input__coordinates">
        <p className="location-input__coordinates-hint">
          Coordenadas GPS (opcionales) - Obtén las coordenadas desde Google Maps o tu dispositivo GPS
        </p>

        <div className="location-input__coordinates-grid">
          {/* Latitude */}
          <div className="location-input__field">
            <label htmlFor={`location-latitude-${index}`} className="location-input__label">
              Latitud
            </label>
            <input
              id={`location-latitude-${index}`}
              type="number"
              step="0.000001"
              min="-90"
              max="90"
              value={value.latitude ?? ''}
              onChange={(e) =>
                onChange(index, 'latitude', e.target.value ? parseFloat(e.target.value) : null)
              }
              placeholder="40.416775"
              className={`location-input__input ${errors?.latitude ? 'location-input__input--error' : ''}`}
            />
            {errors?.latitude && (
              <p className="location-input__error">{errors.latitude}</p>
            )}
          </div>

          {/* Longitude */}
          <div className="location-input__field">
            <label htmlFor={`location-longitude-${index}`} className="location-input__label">
              Longitud
            </label>
            <input
              id={`location-longitude-${index}`}
              type="number"
              step="0.000001"
              min="-180"
              max="180"
              value={value.longitude ?? ''}
              onChange={(e) =>
                onChange(index, 'longitude', e.target.value ? parseFloat(e.target.value) : null)
              }
              placeholder="-3.703790"
              className={`location-input__input ${errors?.longitude ? 'location-input__input--error' : ''}`}
            />
            {errors?.longitude && (
              <p className="location-input__error">{errors.longitude}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
```

**Create CSS**: `frontend/src/components/trips/TripForm/LocationInput.css`

```css
.location-input {
  border: 1px solid var(--border-color, #e5e7eb);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  background-color: var(--bg-secondary, #f9fafb);
}

.location-input__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.location-input__title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary, #111827);
  margin: 0;
}

.location-input__remove-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-secondary, #6b7280);
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.location-input__remove-button:hover {
  color: var(--danger, #ef4444);
}

.location-input__field {
  margin-bottom: 12px;
}

.location-input__label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary, #111827);
  margin-bottom: 4px;
}

.location-input__required {
  color: var(--danger, #ef4444);
}

.location-input__input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 6px;
  font-size: 0.9375rem;
  transition: border-color 0.2s;
}

.location-input__input:focus {
  outline: none;
  border-color: var(--primary, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.location-input__input--error {
  border-color: var(--danger, #ef4444);
}

.location-input__error {
  color: var(--danger, #ef4444);
  font-size: 0.8125rem;
  margin-top: 4px;
  margin-bottom: 0;
}

.location-input__coordinates {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #e5e7eb);
}

.location-input__coordinates-hint {
  font-size: 0.8125rem;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 8px;
}

.location-input__coordinates-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 640px) {
  .location-input__coordinates-grid {
    grid-template-columns: 1fr;
  }
}
```

---

### Step 4: Update Trip Form to Include Locations (5 min)

**File**: `frontend/src/components/trips/TripForm/Step1BasicInfo.tsx`

**Add location input section** (after distance/difficulty fields):

```typescript
import { LocationInput } from './LocationInput';

// ... existing code ...

// In the component:
const [locations, setLocations] = useState<LocationInput[]>([]);

const handleLocationChange = (index: number, field: string, value: string | number | null) => {
  const updated = [...locations];
  updated[index] = { ...updated[index], [field]: value };
  setLocations(updated);
};

const handleAddLocation = () => {
  if (locations.length < 50) {
    setLocations([...locations, { name: '', latitude: null, longitude: null }]);
  }
};

const handleRemoveLocation = (index: number) => {
  setLocations(locations.filter((_, i) => i !== index));
};

// In the JSX:
<div className="trip-form__section">
  <h3 className="trip-form__section-title">Ubicaciones del Viaje (Opcional)</h3>
  <p className="trip-form__section-hint">
    Añade las ubicaciones que visitaste durante el viaje. Las coordenadas GPS son opcionales.
  </p>

  {locations.map((location, index) => (
    <LocationInput
      key={index}
      index={index}
      value={location}
      onChange={handleLocationChange}
      onRemove={handleRemoveLocation}
      errors={validationErrors?.locations?.[index]}
    />
  ))}

  {locations.length < 50 && (
    <button
      type="button"
      onClick={handleAddLocation}
      className="trip-form__add-location-button"
    >
      + Añadir Ubicación
    </button>
  )}
</div>
```

---

## Manual Testing

### Test Case 1: Create Trip with Coordinates

1. Start backend and frontend servers
2. Navigate to `/trips/create`
3. Fill in trip details (title, dates, distance, difficulty)
4. Click "Añadir Ubicación"
5. Enter location name: "Jaca"
6. Enter latitude: `42.570084`
7. Enter longitude: `-0.549941`
8. Add another location: "Somport" (lat: `42.791667`, lng: `-0.526944`)
9. Submit form
10. **Expected**: Trip created successfully, redirects to trip detail page
11. **Expected**: Map displays with 2 markers and connecting polyline

---

### Test Case 2: Coordinate Validation

1. Create trip, add location
2. Enter latitude: `100` (invalid, > 90)
3. Try to submit
4. **Expected**: Error message: "Latitud debe estar entre -90 y 90 grados"
5. Correct to valid value (e.g., `40.416775`)
6. **Expected**: Error clears, form submits successfully

---

### Test Case 3: Backwards Compatibility

1. Create trip without entering any coordinates
2. Submit form
3. **Expected**: Trip created successfully (coordinates = null)
4. **Expected**: Trip detail page shows location names in list, NO map section displayed

---

## Troubleshooting

### Backend Tests Fail: "ValidationError not raised"

**Cause**: Pydantic `Field()` constraints may not throw ValueError
**Fix**: Ensure `@field_validator` methods are defined for custom Spanish error messages

---

### Frontend: Coordinates Not Sent to API

**Cause**: `tripHelpers.ts` may still have `locations: []` hardcoded
**Fix**: Update `formDataToApiPayload()` to include `locations` from form state

---

### Map Doesn't Display

**Cause**: All locations have `null` coordinates
**Fix**: TripMap component filters out locations without coordinates (expected behavior). Ensure at least one location has valid coordinates for map to display.

---

## Next Steps

1. ✅ Complete backend schema updates and validation
2. ✅ Complete frontend coordinate input component
3. ⏳ Write integration tests for trip creation with coordinates
4. ⏳ Run `/speckit.tasks` to generate detailed task breakdown
5. ⏳ Implement features following TDD workflow (tests first, then implementation)
6. ⏳ Add map error handling (retry button, fallback to text list per FR-015)

---

## References

- **Feature Spec**: [spec.md](spec.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Research**: [research.md](research.md)
- **Data Model**: [data-model.md](data-model.md)
- **API Contracts**: [contracts/trips-api.yaml](contracts/trips-api.yaml)
- **Constitution**: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

**Quickstart Status**: ✅ COMPLETE

Ready for implementation! Run `/speckit.tasks` to generate task breakdown and begin development.
