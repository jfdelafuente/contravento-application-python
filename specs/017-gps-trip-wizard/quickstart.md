# GPS Trip Creation Wizard - Developer Quickstart

**Feature**: 017-gps-trip-wizard
**Date**: 2026-01-28
**Status**: Phase 1 Design Complete

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Manual Testing](#manual-testing)
6. [Performance Validation](#performance-validation)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Backend**: Python 3.12 + Poetry
- **Frontend**: Node.js 18+ + npm
- **Database**: PostgreSQL 14+ (production) or SQLite 3.35+ (development)
- **Git**: For version control

### Required Features

The GPS Trip Creation Wizard builds on existing features. Ensure these are implemented:

- ✅ **Feature 002**: Travel Diary (Trip model, API endpoints)
- ✅ **Feature 003**: GPS Routes (GPXFile model, GPXService, POI management)
- ✅ **Feature 008**: Travel Diary Frontend (TripFormWizard pattern, React Hook Form)
- ✅ **Feature 009**: GPS Coordinates (TripLocation, map integration)
- ✅ **Feature 010**: Reverse Geocoding (Leaflet map, click handlers)

**Verification**:
```bash
# Check existing GPX processing
cd backend
poetry run python -c "from src.services.gpx_service import GPXService; print('✓ GPXService exists')"

# Check existing wizard component
cd frontend
grep -r "TripFormWizard" src/components/trips/
```

---

## Setup

### Backend Setup

#### 1. Install Dependencies

All dependencies are already installed from previous features (Feature 003):

```bash
cd backend
poetry install

# Verify GPX libraries
poetry show gpxpy  # Should show version 1.6.2
poetry show rdp    # Should show version 0.8 (Douglas-Peucker)
```

**No new dependencies required!**

#### 2. Run Database Migration

Add `EXTREME` difficulty level to `TripDifficulty` enum:

```bash
cd backend

# Generate migration (if not exists)
poetry run alembic revision --autogenerate -m "Add EXTREME difficulty level"

# Apply migration
poetry run alembic upgrade head

# Verify migration
poetry run alembic current
# Should show: "XXX_add_extreme_difficulty.py"
```

**Manual Verification**:
```bash
poetry run python -c "
from src.models.trip import TripDifficulty
assert hasattr(TripDifficulty, 'EXTREME'), 'EXTREME not found in enum'
print('✓ EXTREME difficulty level added')
"
```

#### 3. Update POI Constant

Change max POIs from 20 to 6 (align with spec FR-011):

**File**: `backend/src/services/poi_service.py` (or `backend/src/utils/constants.py`)

```python
# OLD:
MAX_POIS_PER_TRIP = 20

# NEW:
MAX_POIS_PER_TRIP = 6  # Spec FR-011: Max 6 POIs for focused UX
```

**Verification**:
```bash
poetry run python -c "
from src.services.poi_service import MAX_POIS_PER_TRIP
assert MAX_POIS_PER_TRIP == 6, f'Expected 6, got {MAX_POIS_PER_TRIP}'
print('✓ MAX_POIS_PER_TRIP = 6')
"
```

---

### Frontend Setup

#### 1. Install Dependencies

All dependencies are already installed from previous features:

```bash
cd frontend
npm install

# Verify wizard dependencies
npm list react-hook-form    # Should show 7.70.x
npm list react-dropzone     # Should show 14.3.x
npm list react-leaflet      # Should show 4.2.x
```

**No new dependencies required!**

#### 2. Add Routes

Update `frontend/src/App.tsx` to add wizard routes:

```typescript
// Add imports
import { TripCreateModePage } from './pages/TripCreateModePage';
import { GPXTripCreatePage } from './pages/GPXTripCreatePage';

// Update routes (inside <Routes>)
<Route path="/trips/new" element={<TripCreateModePage />} />
<Route path="/trips/new/manual" element={<TripCreatePage />} />
<Route path="/trips/new/gpx" element={<GPXTripCreatePage />} />
```

**Verification**:
```bash
# Check route exists
grep -A 3 'path="/trips/new"' frontend/src/App.tsx
```

---

## Development Workflow

### Implementation Order (TDD Required)

Follow this sequence to implement the wizard. **Write tests FIRST** for each component before implementation.

#### Phase 1: Backend Core (Days 1-2)

**1.1. Difficulty Calculator Service**

- **File**: `backend/src/services/difficulty_calculator.py`
- **Test**: `backend/tests/unit/test_difficulty_calculator.py`

```bash
# Write tests FIRST
cd backend
poetry run pytest tests/unit/test_difficulty_calculator.py --create-missing

# Implement service
# ... write difficulty_calculator.py

# Run tests (should pass)
poetry run pytest tests/unit/test_difficulty_calculator.py -v
```

**1.2. GPX Analysis Endpoint**

- **File**: `backend/src/api/gpx_wizard.py`
- **Test**: `backend/tests/integration/test_gpx_wizard_api.py`

```bash
# Write integration tests FIRST
poetry run pytest tests/integration/test_gpx_wizard_api.py --create-missing

# Implement endpoint
# ... write gpx_wizard.py API endpoint

# Run tests
poetry run pytest tests/integration/test_gpx_wizard_api.py -v
```

**1.3. GPXService Modification**

- **File**: `backend/src/services/gpx_service.py` (add `extract_telemetry_quick()`)
- **Test**: `backend/tests/unit/test_gpx_service.py` (add test for new method)

```bash
# Add test for extract_telemetry_quick()
# Run tests
poetry run pytest tests/unit/test_gpx_service.py::test_extract_telemetry_quick -v
```

#### Phase 2: Frontend Core (Days 3-5)

**2.1. Mode Selection Modal**

- **File**: `frontend/src/pages/TripCreateModePage.tsx`
- **Test**: `frontend/tests/unit/TripCreateModePage.test.tsx`

```bash
cd frontend

# Write tests FIRST
npm run test TripCreateModePage.test.tsx -- --watch

# Implement component
# ... write TripCreateModePage.tsx

# Run tests (should pass)
npm run test TripCreateModePage.test.tsx
```

**2.2. Wizard Structure (4 Steps)**

- **Files**: `frontend/src/components/trips/GPXWizard/*.tsx`
- **Test**: `frontend/tests/integration/gpx-wizard-flow.test.tsx`

```bash
# Write E2E test FIRST (describes full wizard flow)
npm run test gpx-wizard-flow.test.tsx -- --watch

# Implement wizard components one by one
# Step 1: GPXWizard.tsx (container)
# Step 2: Step1Upload.tsx
# Step 3: Step2Details.tsx
# Step 4: Step3POIs.tsx
# Step 5: Step4Review.tsx

# Run E2E test (should pass after all steps complete)
npm run test gpx-wizard-flow.test.tsx
```

**2.3. Integration & Polish (Day 6)**

- Update `TripMap.tsx` for POI click handler
- Update `tripService.ts` for `createTripWithGPX()`
- Error handling, loading states, Spanish translations

---

## Testing

### Backend Tests

#### Unit Tests

```bash
cd backend

# Test difficulty calculator (TDD - write FIRST)
poetry run pytest tests/unit/test_difficulty_calculator.py -v

# Test GPX telemetry extraction
poetry run pytest tests/unit/test_gpx_service.py::test_extract_telemetry_quick -v

# All unit tests
poetry run pytest tests/unit/ -v
```

**Coverage Target**: ≥90%

```bash
# Generate coverage report
poetry run pytest tests/unit/ --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

#### Integration Tests

```bash
# Test GPX analysis endpoint
poetry run pytest tests/integration/test_gpx_wizard_api.py -v

# Test full wizard flow (create trip + GPX + POIs)
poetry run pytest tests/integration/test_trip_gpx_workflow.py -v

# All integration tests
poetry run pytest tests/integration/ -v
```

#### Contract Tests (OpenAPI Validation)

```bash
# Validate request/response schemas against OpenAPI spec
poetry run pytest tests/contract/test_gpx_wizard_contracts.py -v
```

**What Contract Tests Verify**:
- Request schemas match `contracts/gpx-wizard.yaml`
- Response schemas match OpenAPI definitions
- Error responses (400, 401, 408, 413) return correct structure
- All required fields present, no extra fields

---

### Frontend Tests

#### Unit Tests

```bash
cd frontend

# Test wizard components
npm run test GPXWizard.test.tsx
npm run test Step1Upload.test.tsx
npm run test useGPXWizard.test.ts

# Test mode selection modal
npm run test TripCreateModePage.test.tsx

# All unit tests
npm run test -- --coverage
```

#### Integration Tests (E2E)

```bash
# Full wizard flow (Step 1 → Step 4 → Publish)
npm run test gpx-wizard-flow.test.tsx
```

**What E2E Test Validates**:
1. User uploads GPX file → sees telemetry preview
2. User fills details → difficulty auto-populated (read-only)
3. User adds 3 POIs on map
4. User clicks "Publicar" → trip created with GPX + POIs
5. User redirected to trip detail page

---

## Manual Testing

### Test Case 1: GPX Upload (Happy Path)

**Goal**: Verify complete wizard flow from GPX upload to trip publish.

**Steps**:

1. **Navigate to mode selection**
   ```
   URL: http://localhost:5173/trips/new
   Expected: Modal with two options ("Con GPS" / "Sin GPS")
   ```

2. **Select "Con archivo GPX"**
   ```
   Click: "Con archivo GPX" button
   Expected: Navigate to /trips/new/gpx
   ```

3. **Upload GPX file**
   ```
   File: backend/tests/fixtures/test-route.gpx
   Method: Drag-and-drop to upload area
   Expected: Telemetry preview displays:
     - Distance: 42.5 km
     - Elevation gain: 1250 m
     - Difficulty badge: "Difícil" (orange)
   ```

4. **Click "Siguiente" (Step 1 → Step 2)**
   ```
   Expected: Form auto-populated with:
     - Title: "test-route" (from filename)
     - Difficulty: "Difícil" (read-only, gray badge)
     - All other fields empty
   ```

5. **Fill trip details**
   ```
   Title: "Ruta Bikepacking Pirineos"
   Description: "Viaje de 5 días por los Pirineos con más de 300km recorridos..." (min 50 chars)
   Start date: 2024-06-01
   End date: 2024-06-05
   Privacy: Public (default)
   ```

6. **Click "Siguiente" (Step 2 → Step 3)**
   ```
   Expected: Map shows GPX track (red line)
             POI counter: "0 / 6 POIs añadidos"
   ```

7. **Add POIs on map**
   ```
   - Click map at 3 different points
   - For each POI:
     * Name: "Refugio de montaña" / "Ibón" / "Mirador"
     * Description: Optional (max 500 chars)
     * Click "Guardar POI"
   Expected: POI markers appear on map (blue pins)
             POI counter: "3 / 6 POIs añadidos"
   ```

8. **Click "Siguiente" (Step 3 → Step 4)**
   ```
   Expected: Review summary shows:
     - Title, description, dates
     - Difficulty badge
     - Distance, elevation gain
     - Map with track + 3 POI markers
     - "Publicar" button enabled
   ```

9. **Click "Publicar"**
   ```
   Expected:
     - Loading spinner appears (~2-5s)
     - Success toast: "Viaje publicado correctamente"
     - Redirect to: /trips/{trip_id}
   ```

10. **Verify trip detail page**
    ```
    Expected:
      - Title: "Ruta Bikepacking Pirineos"
      - Difficulty badge: "Difícil"
      - Map shows GPX track + 3 POI markers
      - Elevation profile chart (if elevation data exists)
      - POIs listed in sidebar with descriptions
    ```

**Total Time**: <3 minutes (meets SC-001: <5min)

---

### Test Case 2: GPX Without Elevation Data

**Goal**: Verify wizard handles GPX files without elevation data gracefully.

**Steps**:

1. Navigate to wizard: `/trips/new/gpx`
2. Upload: `backend/tests/fixtures/no-elevation.gpx`
3. **Expected telemetry preview**:
   ```
   Distance: 28.3 km
   Elevation gain: No disponible
   Elevation loss: No disponible
   Max elevation: No disponible
   Difficulty: Fácil (calculated from distance only)
   ```
4. **Expected info message**: "El archivo GPX no contiene datos de altitud. La dificultad se calculó solo basándose en distancia."
5. Continue wizard normally (Steps 2-4)
6. **Expected trip detail page**: No elevation profile chart, only distance stats

---

### Test Case 3: Edge Cases

#### 3.1. Upload Non-GPX File

```
File: test-image.jpg
Expected Error: "Formato no válido. Solo se aceptan archivos .gpx"
Toast color: Red
User remains on Step 1
```

#### 3.2. Upload GPX >10MB

```
File: large-route.gpx (15MB)
Expected Error: "El archivo es demasiado grande. Tamaño máximo: 10MB"
HTTP Status: 413 (Payload Too Large)
```

#### 3.3. Add 7th POI

```
- Add 6 POIs successfully
- Click map for 7th POI
Expected: "Añadir POI" button disabled
Toast: "Máximo 6 POIs por viaje"
```

#### 3.4. Cancel Wizard (Data Loss Warning)

```
- Fill wizard Steps 1-3
- Click "Cancelar" button
Expected: Confirm dialog:
  Title: "¿Descartar viaje?"
  Message: "Todos los datos se perderán. Esta acción no se puede deshacer."
  Buttons: "Cancelar" (gray) | "Descartar" (red)
- Click "Descartar"
Expected: Navigate back to /trips, all wizard data lost
```

#### 3.5. Description Too Short

```
- Fill title, dates
- Description: "Viaje" (5 chars)
- Click "Siguiente"
Expected: Validation error below description field:
  "La descripción debe tener al menos 50 caracteres (5/50)"
  "Siguiente" button disabled
```

---

## Performance Validation

### SC-002: GPX Processing <30s (10MB/100k points)

```bash
cd backend

# Upload large GPX file via wizard API
time curl -X POST http://localhost:8000/gpx/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@tests/fixtures/large-route.gpx"  # 10MB file

# Expected: <2s for telemetry extraction (quick mode)
# Note: Full GPX processing happens asynchronously on publish (~25s)
```

**Performance Breakdown**:
- **Telemetry extraction**: <2s (Step 1 preview)
- **Full GPX processing**: <30s (async after publish)
- **POI creation**: <100ms (6 sequential INSERTs)
- **Total wizard publish time**: <5s (SC-001 target)

---

### SC-001: Wizard Completion <5min

**Manual Timing Test**:

```
1. Select mode: <10s
2. Upload GPX (drag-and-drop): <15s
3. Fill details (title, description, dates): <60s
4. Add POIs (3 POIs with descriptions): <90s
5. Review + Publish: <20s

Total: <195s (~3min) ✓ Meets <5min target
```

**Optimization Tips**:
- Use keyboard navigation (Tab, Enter) to speed up form filling
- Copy-paste description from prepared text
- Pre-select POI locations before opening wizard

---

## Troubleshooting

### Issue: "Cannot find module 'react-dropzone'"

**Symptom**: Frontend build fails with import error.

**Solution**:
```bash
cd frontend
npm install react-dropzone@14.3.8
npm run dev
```

**Prevention**: Run `npm install` after pulling latest changes.

---

### Issue: "TripDifficulty has no member 'EXTREME'"

**Symptom**: Backend fails with AttributeError when calculating difficulty.

**Solution**:
```bash
cd backend

# Check migration status
poetry run alembic current

# If migration not applied:
poetry run alembic upgrade head

# Verify EXTREME exists
poetry run python -c "from src.models.trip import TripDifficulty; print(TripDifficulty.EXTREME)"
```

**Prevention**: Always run migrations after pulling code changes.

---

### Issue: POI Creation Fails with "Trip is not published"

**Symptom**: Wizard publish succeeds, but POIs not created (FR-029 constraint).

**Root Cause**: POIs can only be added to `PUBLISHED` trips (Feature 003 requirement).

**Solution**: Ensure wizard sets `trip.status = "published"` BEFORE creating POIs.

**Code Fix** (`backend/src/api/trips.py`):
```python
# WRONG ORDER:
trip = create_trip(data)  # status=DRAFT by default
create_pois(trip.trip_id, pois)  # FAILS: trip not published

# CORRECT ORDER:
trip = create_trip(data)
trip.status = TripStatus.PUBLISHED  # Set PUBLISHED first
await db.flush()  # Commit status change
create_pois(trip.trip_id, pois)  # SUCCESS
```

---

### Issue: Map Click Handler Not Working in Edit Mode

**Symptom**: Clicking map in Step 3 (POI management) doesn't open POI form.

**Root Cause**: `isEditMode` flag not set to `true` for `TripMap` component.

**Solution** (`frontend/src/components/trips/GPXWizard/Step3POIs.tsx`):
```typescript
<TripMap
  isEditMode={true}  // Enable click-to-add POI
  onMapClick={handleMapClick}
  pois={pois}
  gpxTrackPoints={gpxData.trackpoints}
/>
```

**Verification**: Click map → POIForm modal should open with coordinates pre-filled.

---

### Issue: Difficulty Badge Shows "undefined"

**Symptom**: Step 2 displays difficulty badge as "undefined" instead of difficulty level.

**Root Cause**: Frontend expects English difficulty values (`"difficult"`), but backend returns Spanish (`"difícil"`).

**Solution**: Use backend's English enum values:
```typescript
// backend/src/models/trip.py
class TripDifficulty(str, enum.Enum):
    EASY = "easy"  # NOT "fácil"
    MODERATE = "moderate"  # NOT "moderada"
    # ...
```

**Frontend Translation** (`frontend/src/utils/tripHelpers.ts`):
```typescript
export const translateDifficulty = (difficulty: TripDifficulty): string => {
  const translations = {
    easy: "Fácil",
    moderate: "Moderada",
    difficult: "Difícil",
    very_difficult: "Muy Difícil",
    extreme: "Extrema"
  };
  return translations[difficulty] || difficulty;
};
```

---

### Issue: GPX Processing Timeout (>60s)

**Symptom**: Large GPX files fail with 408 timeout error (spec clarification #4).

**Root Cause**: Synchronous processing takes >60s for files >10MB or >100k points.

**Solution**: Use async processing pattern from Feature 003:
```python
# backend/src/api/gpx_wizard.py

if file_size > 1 * 1024 * 1024:  # >1MB
    # Process asynchronously (background task)
    task_id = process_gpx_background(file_content)
    return {
        "status": "processing",
        "task_id": task_id,
        "poll_url": f"/gpx/{task_id}/status"
    }
else:
    # Process synchronously (<1MB)
    telemetry = await gpx_service.extract_telemetry_quick(file_content)
    return telemetry
```

**Frontend Handling**: Poll `/gpx/{task_id}/status` every 2s until status = "completed".

---

## Next Steps After Setup

1. ✅ **Verify Setup**: Run all tests (backend + frontend) to ensure green baseline
2. ✅ **Read Spec**: Review [spec.md](spec.md) for user stories and requirements
3. ✅ **Read Plan**: Review [plan.md](plan.md) for implementation strategy
4. ✅ **Read Data Model**: Review [data-model.md](data-model.md) for schema details
5. ✅ **Read Contracts**: Review [contracts/gpx-wizard.yaml](contracts/gpx-wizard.yaml) for API definitions
6. ⏳ **Start Implementation**: Follow TDD workflow (write tests FIRST, then implement)

---

## Useful Commands Reference

### Backend

```bash
cd backend

# Run development server
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
poetry run pytest -v
poetry run pytest --cov=src --cov-report=html

# Database migrations
poetry run alembic revision --autogenerate -m "Description"
poetry run alembic upgrade head
poetry run alembic downgrade -1

# Code quality
poetry run black src/ tests/
poetry run ruff check src/ tests/
poetry run mypy src/
```

### Frontend

```bash
cd frontend

# Run development server
npm run dev

# Run tests
npm run test
npm run test -- --coverage
npm run test -- --watch

# Code quality
npm run lint
npm run type-check

# Build for production
npm run build:prod
```

---

**Last Updated**: 2026-01-28
**Feature**: 017-gps-trip-wizard
**Status**: Phase 1 Design Complete
**Next Phase**: `/speckit.tasks` to generate task breakdown
