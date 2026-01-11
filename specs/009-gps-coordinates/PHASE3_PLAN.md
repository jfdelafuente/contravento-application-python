# Phase 3: User Story 1 - View Trip Route on Map (TDD Tests)

**Branch**: `009-gps-coordinates-tests`
**Goal**: Write automated tests (pytest + Jest) for GPS coordinates feature following TDD methodology
**Status**: 🚧 In Progress

---

## Overview

Phase 3 focuses on writing **automated tests** for User Story 1 (View Trip Route on Map). This phase follows **Test-Driven Development (TDD)**:

1. ✅ **Red Phase**: Write tests that FAIL (feature not yet implemented)
2. ✅ **Green Phase**: Implement minimal code to make tests PASS
3. ✅ **Refactor Phase**: Improve code while keeping tests passing

**Important**: Phases 1-2 already implemented the backend validation and manual testing. Phase 3 adds **automated test coverage** to ensure ≥90% code coverage requirement.

---

## Tasks Breakdown

### Backend Tests (8 tasks)

#### Unit Tests - Coordinate Validation
- [ ] **T012**: Test valid coordinate ranges (lat: -90 to 90, lng: -180 to 180)
- [ ] **T013**: Test out-of-range rejection (lat: 100, lng: 200)
- [ ] **T014**: Test precision rounding to 6 decimals
- [ ] **T015**: Test nullable coordinates (backwards compatibility)

**File**: `backend/tests/unit/test_coordinate_validation.py`

#### Integration Tests - API Endpoints
- [ ] **T016**: Test POST /trips with GPS coordinates
- [ ] **T017**: Test GET /trips/{trip_id} retrieves coordinates

**File**: `backend/tests/integration/test_trips_api.py`

#### Contract Tests - OpenAPI Schema
- [ ] **T018**: Test POST /trips request schema validation
- [ ] **T019**: Test GET /trips/{trip_id} response schema

**File**: `backend/tests/contract/test_trips_openapi.py`

---

### Frontend Tests (4 tasks)

#### Unit Tests - TripMap Component
- [ ] **T020**: Test filtering null coordinates
- [ ] **T021**: Test marker rendering
- [ ] **T022**: Test polyline rendering
- [ ] **T023**: Test zoom calculation

**File**: `frontend/tests/unit/TripMap.test.tsx`

---

### Implementation Verification (9 tasks)

**Note**: Backend implementation already exists from Phases 1-2. These tasks verify existing code passes new tests.

#### Backend Verification
- [ ] **T024**: Run unit tests (should fail initially)
- [ ] **T025-T028**: Verify existing validation logic
- [ ] **T029-T032**: Run all test suites and verify ≥90% coverage

#### Frontend Verification
- [ ] **T033-T035**: Verify TripMap component works with new tests

---

## Test Structure

### Backend Test Files

```
backend/tests/
├── unit/
│   └── test_coordinate_validation.py        # T012-T015 (NEW)
├── integration/
│   └── test_trips_api.py                     # T016-T017 (EXTEND)
└── contract/
    └── test_trips_openapi.py                 # T018-T019 (EXTEND)
```

### Frontend Test Files

```
frontend/tests/
└── unit/
    └── TripMap.test.tsx                      # T020-T023 (NEW)
```

---

## Testing Scenarios

### Backend Unit Tests

**Test Suite 1: Valid Coordinates**
```python
def test_valid_coordinates():
    """Test coordinates within valid ranges pass validation."""
    # Madrid: 40.416775, -3.703790
    # Tokyo: 35.689487, 139.691711
    # Sydney: -33.868820, 151.209290
```

**Test Suite 2: Invalid Coordinates**
```python
def test_invalid_latitude():
    """Test latitude > 90 or < -90 raises ValidationError."""
    # lat: 100 → Error: "Latitud debe estar entre -90 y 90 grados"

def test_invalid_longitude():
    """Test longitude > 180 or < -180 raises ValidationError."""
    # lng: 200 → Error: "Longitud debe estar entre -180 y 180 grados"
```

**Test Suite 3: Precision**
```python
def test_coordinate_precision():
    """Test coordinates rounded to 6 decimals."""
    # Input: 40.4167751234567
    # Expected: 40.416775
```

**Test Suite 4: Nullable Coordinates**
```python
def test_optional_coordinates():
    """Test location without coordinates is valid."""
    # name: "Madrid", latitude: null, longitude: null → Valid
```

---

### Backend Integration Tests

**Test Suite 5: Trip Creation with GPS**
```python
async def test_create_trip_with_coordinates():
    """Test POST /trips creates trip with GPS coordinates."""
    payload = {
        "title": "Ruta Test GPS",
        "locations": [
            {"name": "Madrid", "latitude": 40.416775, "longitude": -3.703790}
        ]
    }
    # Assert: 201 Created, coordinates stored in DB
```

**Test Suite 6: Trip Retrieval with GPS**
```python
async def test_get_trip_with_coordinates():
    """Test GET /trips/{trip_id} returns coordinates."""
    # Assert: Response includes latitude/longitude in locations array
```

---

### Backend Contract Tests

**Test Suite 7: Request Schema Validation**
```python
def test_post_trips_schema_validation():
    """Test POST /trips request matches OpenAPI schema."""
    # Validate against contracts/trips-api.yaml
```

**Test Suite 8: Response Schema Validation**
```python
def test_get_trip_response_schema():
    """Test GET /trips/{trip_id} response matches OpenAPI schema."""
    # Validate LocationResponse includes latitude/longitude
```

---

### Frontend Unit Tests

**Test Suite 9: TripMap Component**
```typescript
describe('TripMap', () => {
  test('filters out locations without coordinates', () => {
    // Input: 3 locations (1 with coords, 2 without)
    // Expected: Map renders 1 marker
  });

  test('renders markers for each location with coordinates', () => {
    // Input: 3 locations with coords
    // Expected: 3 markers on map
  });

  test('renders polyline connecting locations in sequence', () => {
    // Input: 3 locations with coords
    // Expected: Polyline with 3 points in order
  });

  test('calculates zoom to fit all markers', () => {
    // Input: 2 locations 100km apart
    // Expected: Map zooms out to show both
  });
});
```

---

## Success Criteria

### Code Coverage
- ✅ Backend: ≥90% coverage for `backend/src/schemas/trip.py`
- ✅ Backend: ≥90% coverage for `backend/src/services/trip_service.py`
- ✅ Frontend: ≥90% coverage for `frontend/src/components/trips/TripMap.tsx`

### Test Execution
- ✅ All unit tests pass: `pytest backend/tests/unit/ -v`
- ✅ All integration tests pass: `pytest backend/tests/integration/ -v`
- ✅ All contract tests pass: `pytest backend/tests/contract/ -v`
- ✅ All frontend tests pass: `npm test TripMap.test.tsx`

### TDD Workflow
- ✅ Tests written FIRST (Red phase)
- ✅ Tests FAIL before implementation verification (Green phase)
- ✅ All tests PASS after verification (Refactor phase)

---

## Commands

### Backend Testing

```bash
cd backend

# Run specific test suites
poetry run pytest tests/unit/test_coordinate_validation.py -v
poetry run pytest tests/integration/test_trips_api.py::test_create_trip_with_coordinates -v
poetry run pytest tests/contract/test_trips_openapi.py -v

# Run all tests with coverage
poetry run pytest --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

### Frontend Testing

```bash
cd frontend

# Run specific test suite
npm test TripMap.test.tsx

# Run all tests with coverage
npm test -- --coverage

# Watch mode (re-run on file changes)
npm test -- --watch
```

---

## Dependencies

### Backend Testing Dependencies (Already Installed)
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - Async HTTP client for API tests

### Frontend Testing Dependencies (Need Installation)
- `@testing-library/react` - React component testing
- `@testing-library/jest-dom` - DOM assertions
- `@testing-library/user-event` - User interaction simulation
- `vitest` - Test runner (Vite-compatible)

**Installation**:
```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event vitest
```

---

## Checkpoints

### Checkpoint 1: All Tests Written (Red Phase)
- ✅ 8 backend tests created (unit, integration, contract)
- ✅ 4 frontend tests created (unit)
- ✅ All tests FAIL (feature not yet implemented)

### Checkpoint 2: Tests Pass (Green Phase)
- ✅ Existing backend validation verified
- ✅ Existing frontend TripMap verified
- ✅ All tests PASS

### Checkpoint 3: Coverage Verified (Refactor Phase)
- ✅ Backend coverage ≥90%
- ✅ Frontend coverage ≥90%
- ✅ No code smells or duplication

---

## Next Steps After Phase 3

Once Phase 3 is complete:

1. **Commit and push** test files to `009-gps-coordinates-tests` branch
2. **Create PR** to merge tests into `develop`
3. **Move to Phase 4**: User Story 2 - Add GPS Coordinates When Creating Trips (Frontend UI)

---

**Created**: 2026-01-11
**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
