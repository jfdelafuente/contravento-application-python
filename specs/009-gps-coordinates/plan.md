# Implementation Plan: GPS Coordinates for Trip Locations

**Branch**: `009-gps-coordinates` | **Date**: 2026-01-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-gps-coordinates/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add GPS coordinate support (latitude/longitude) to trip locations to enable interactive map visualization of cycling routes. Backend will support optional decimal coordinate storage (6 decimal places precision) with validation. Frontend will provide numeric input fields for manual coordinate entry during trip creation/editing. The existing TripMap component will display routes with markers and polylines connecting locations in sequence order. Coordinates are optional (backwards compatible) - trips without coordinates continue to work normally without map display.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic (backend), React 18, react-leaflet, Leaflet.js (frontend)
**Storage**: PostgreSQL (production), SQLite (development) - TripLocation model already has latitude/longitude Float columns
**Testing**: pytest (backend), Vitest + React Testing Library (frontend)
**Target Platform**: Linux server (backend API), Modern browsers (frontend SPA)
**Project Type**: Web application (FastAPI backend + React frontend)
**Performance Goals**: Map load <2s for 20 markers (SC-009), coordinate validation <200ms p95
**Constraints**: Coordinate precision 6 decimal places (~0.11m accuracy), latitude -90 to 90, longitude -180 to 180
**Scale/Scope**: 50 max locations per trip, support 1-50 location trips on map, manual coordinate entry only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability - PASS ✅

- SQLAlchemy models follow single responsibility (TripLocation handles location data only)
- Pydantic schemas provide clear validation boundaries
- Type hints required on all functions (backend: mypy, frontend: TypeScript strict mode)
- Black formatter enforced on backend, Prettier on frontend
- No magic numbers: validation ranges defined as constants

**Justification**: Existing codebase already follows these patterns. New coordinate validation will use named constants (`MIN_LATITUDE = -90`, `MAX_LATITUDE = 90`) and follow established schema patterns.

### II. Testing Standards (Non-Negotiable) - PASS ✅

**TDD Workflow Enforced**:
- Unit tests for coordinate validation (test validators first)
- Unit tests for location service coordinate processing
- Integration tests for trip creation/update with coordinates
- Contract tests for API schema compliance (OpenAPI)
- Frontend unit tests for coordinate input components
- Frontend integration tests for TripMap rendering with coordinates

**Coverage Target**: ≥90% for new code
- Backend: `backend/src/schemas/trip.py` (coordinate validation)
- Backend: `backend/src/services/trip_service.py` (coordinate processing)
- Frontend: `frontend/src/components/trips/TripForm/LocationInput.tsx` (new component)
- Frontend: `frontend/src/utils/tripValidators.ts` (coordinate validation)

**Rationale**: Trip location data is user-precious (documenting cycling journeys). Invalid coordinates would render maps useless or misleading. TDD ensures validation works before implementation.

### III. User Experience Consistency - PASS ✅

- All user-facing text in Spanish: "Latitud", "Longitud", error messages in Spanish
- Validation errors field-specific: "Latitud debe estar entre -90 y 90 grados"
- Consistent JSON API responses (success/data/error structure)
- Loading states for map rendering (skeleton loader while tiles load)
- Empty state for trips without coordinates ("No hay coordenadas GPS para mostrar el mapa")
- Error state for map load failures (per FR-015: "Retry" button + fallback to text list)
- Form inputs use number type with step="0.000001" for 6 decimal precision
- Visual feedback on coordinate input (validation icons, error messages)

**Rationale**: Spanish-speaking cyclists documenting trips. Technical coordinate terminology must be clear. Map errors must be recoverable (retry button).

### IV. Performance Requirements - PASS ✅

**API Performance**:
- Coordinate validation: in-memory numeric range checks (<1ms)
- Trip creation with coordinates: Same as current trip creation (<500ms p95)
- No additional queries (coordinates stored in existing TripLocation table)

**Frontend Performance**:
- TripMap already implemented and optimized (lazy-loaded component)
- Map rendering: <2s for 20 markers (SC-009, Leaflet.js performance)
- Coordinate input: Controlled components with debounced validation
- No network calls for validation (client-side numeric validation)

**Database**:
- No new indexes needed (latitude/longitude are Float columns, not queried for filtering)
- Existing TripLocation table supports coordinates (nullable Float columns)
- No N+1 queries (locations eager-loaded with trip via existing relationship)

**Rationale**: Coordinates are simple numeric data. Validation is lightweight. Map component already optimized. No performance regressions expected.

### Security & Data Protection - PASS ✅

- Coordinate input validated server-side (Pydantic schema range validation)
- No SQL injection risk (SQLAlchemy ORM parameterized queries)
- No XSS risk (numeric float values only, validated ranges)
- No file uploads (coordinates are numeric input only)
- Authentication/authorization already enforced on trip endpoints
- No sensitive data (GPS coordinates are public trip data, not personal location tracking)

**Rationale**: Coordinate data is less sensitive than photos/descriptions (already public on published trips). Numeric validation prevents injection attacks.

### Development Workflow - PASS ✅

- Feature branch: `009-gps-coordinates` (already created)
- Conventional commits: "feat: add GPS coordinate validation", "test: coordinate input validation"
- PR will include:
  - Backend: coordinate validation tests, schema updates
  - Frontend: coordinate input component, validation logic
  - Contract tests: OpenAPI schema updates
  - Screenshots: trip creation form with coordinate inputs, map display
- CI/CD: pytest (backend), Vitest (frontend), mypy, black, ruff (backend), eslint, prettier (frontend)
- Database migration: NOT NEEDED (columns already exist in TripLocation model)

**Rationale**: Standard workflow applies. No special exceptions needed.

---

**GATE RESULT**: ✅ **PASS** - All constitutional requirements met. No complexity justifications required.

## Project Structure

### Documentation (this feature)

```text
specs/009-gps-coordinates/
├── spec.md              # Feature specification (already exists)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - Technology decisions
├── data-model.md        # Phase 1 output - TripLocation schema updates
├── quickstart.md        # Phase 1 output - Developer setup guide
├── contracts/           # Phase 1 output - OpenAPI schemas
│   └── trips-api.yaml   # Updated trip endpoints with coordinate validation
├── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
└── checklists/
    └── requirements.md  # Spec quality checklist (already exists)
```

### Source Code (repository root)

```text
# Web application structure (FastAPI backend + React frontend)
backend/
├── src/
│   ├── models/
│   │   └── trip.py                      # TripLocation model (latitude/longitude already exist)
│   ├── schemas/
│   │   └── trip.py                      # LocationInput schema (ADD coordinate fields)
│   ├── services/
│   │   └── trip_service.py              # _process_locations (UPDATE to store coordinates)
│   ├── api/
│   │   └── trips.py                     # Trip CRUD endpoints (NO CHANGES - schemas handle validation)
│   └── utils/
│       └── validators.py                # Coordinate validation functions (NEW)
└── tests/
    ├── unit/
    │   ├── test_coordinate_validation.py  # NEW: Coordinate range validation tests
    │   └── test_trip_service.py           # UPDATE: Test coordinate storage
    ├── integration/
    │   └── test_trips_api.py              # UPDATE: Test trip creation with coordinates
    └── contract/
        └── test_trips_openapi.py          # UPDATE: OpenAPI schema validation

frontend/
├── src/
│   ├── components/trips/
│   │   ├── TripMap.tsx                    # NO CHANGES (already handles null coordinates)
│   │   └── TripForm/
│   │       ├── Step1BasicInfo.tsx         # UPDATE: Add LocationInput fields
│   │       ├── LocationInput.tsx          # NEW: Coordinate input component
│   │       └── Step4Review.tsx            # UPDATE: Display coordinates in review
│   ├── types/
│   │   └── trip.ts                        # UPDATE: LocationInput interface (add lat/lng)
│   ├── utils/
│   │   ├── tripValidators.ts              # UPDATE: Add coordinate validation
│   │   └── tripHelpers.ts                 # UPDATE: Include coordinates in form payload
│   └── services/
│       └── tripService.ts                 # NO CHANGES (API accepts LocationInput already)
└── tests/
    ├── unit/
    │   ├── LocationInput.test.tsx         # NEW: Coordinate input component tests
    │   └── tripValidators.test.ts         # UPDATE: Coordinate validation tests
    └── integration/
        └── TripForm.test.tsx              # UPDATE: Test coordinate input in form flow
```

**Structure Decision**: Existing web application structure (backend + frontend). TripLocation model already has coordinate columns (nullable Float), so no database migration needed. Frontend TripMap component already exists and handles coordinate display. Implementation focuses on:
1. **Backend**: Update LocationInput schema to accept coordinates, add validation
2. **Frontend**: Add coordinate input fields to trip creation/editing form
3. **Validation**: Client-side (TypeScript) and server-side (Pydantic) coordinate validation
4. **Testing**: Unit tests for validation, integration tests for trip creation flow

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**NO VIOLATIONS** - Constitution Check passed all requirements. No complexity justifications needed.

---

## Phase 0: Research & Technology Decisions

**Status**: ✅ COMPLETE

See [research.md](research.md) for detailed research findings on:
1. Coordinate validation patterns (Pydantic vs custom validators)
2. Frontend coordinate input UX (separate fields vs combined, decimal precision)
3. Map error handling strategies (retry button, fallback to text list)
4. Backwards compatibility approach (nullable coordinates, graceful degradation)

---

## Phase 1: Design & Contracts

**Status**: ⏳ IN PROGRESS

### Data Model

See [data-model.md](data-model.md) for:
- TripLocation schema updates (LocationInput with optional latitude/longitude)
- Validation rules (latitude: -90 to 90, longitude: -180 to 180, 6 decimal places)
- Database DDL (SQLite + PostgreSQL - NO MIGRATION NEEDED, columns exist)
- State transitions (N/A - coordinates are static data)

### API Contracts

See [contracts/trips-api.yaml](contracts/trips-api.yaml) for:
- `POST /trips` - Create trip with optional coordinates
- `PUT /trips/{trip_id}` - Update trip coordinates
- Response schemas: TripLocationResponse with latitude/longitude (nullable)
- Request validation: LocationInput with coordinate range validation

### Developer Quickstart

See [quickstart.md](quickstart.md) for:
- Backend setup: Update LocationInput schema, add validation
- Frontend setup: Create LocationInput component, update Step1BasicInfo
- Testing: Run coordinate validation tests
- Manual testing: Create trip with coordinates, verify map display

---

## Phase 2: Task Breakdown

**Status**: ✅ COMPLETE

Generated by `/speckit.tasks` command (separate from this plan).

See [tasks.md](tasks.md) for detailed task breakdown.

---

## Phase 3: Backend Implementation (GPS Coordinate Storage)

**Status**: ✅ COMPLETE

**Summary**: Implemented GPS coordinate storage and validation in backend. Added latitude/longitude fields to LocationInput schema with Pydantic validators for range checking (-90/90, -180/180) and decimal precision (6 places). Updated TripService to store coordinates when processing locations.

**Key Deliverables**:

- Updated `backend/src/schemas/trip.py` - LocationInput with latitude/longitude fields
- Updated `backend/src/services/trip_service.py` - _process_locations() stores coordinates
- Added coordinate validation with Spanish error messages
- 41 passing tests (32 unit + 9 integration), 83.24% coverage

---

## Phase 4: Frontend Implementation (GPS Coordinate Input)

**Status**: ✅ COMPLETE (2026-01-11)

**Summary**: Implemented GPS coordinate input UI in trip creation/editing forms. Added LocationInput component with separate latitude/longitude numeric fields, client-side validation, and visual feedback for errors. Updated trip detail page to display coordinates and conditionally render TripMap component.

**Key Deliverables**:

- Created `frontend/src/components/trips/TripForm/LocationInput.tsx` - Coordinate input component
- Updated `frontend/src/components/trips/TripForm/Step1BasicInfo.tsx` - Integrated LocationInput
- Updated `frontend/src/pages/TripDetailPage.tsx` - Display coordinates and conditional map rendering
- Updated `frontend/src/utils/tripValidators.ts` - Client-side coordinate validation
- Manual testing completed (7/9 test suites, MVP achieved)
- Fixed 7 bugs found during testing (defensive checks, enum values, empty field handling)

---

## Phase 5: Map Visualization Enhancements

**Status**: ⏸️ PENDING

**Goal**: Enhance TripMap component with error handling, numbered markers, fullscreen mode, and comprehensive unit testing to complete the map visualization feature.

### Objectives

1. **Error Handling & Resilience** (FR-015, FR-017, FR-018)
   - Detect network errors when loading map tiles
   - Display user-friendly error message with "Retry" button
   - Preserve map state (zoom, center) when retrying
   - Provide fallback to location text list

2. **Numbered Markers** (FR-016, FR-020)
   - Replace generic Leaflet markers with custom numbered icons
   - Show location sequence (1, 2, 3...) on each marker
   - Improve visual clarity for route understanding

3. **Fullscreen Mode** (FR-019)
   - Add fullscreen toggle button to map component
   - Expand map to fill viewport for better route visualization
   - Maintain map state when entering/exiting fullscreen

4. **Unit Testing** (SC-015)
   - Write unit tests for TripMap component (deferred T020-T023)
   - Test error handling, marker rendering, zoom calculations
   - Achieve ≥90% code coverage for TripMap.tsx

### Technical Approach

**Error Handling Strategy**:

- Use `<MapContainer>` error boundary to catch tile loading failures
- Implement custom error state with React useState
- Add retry mechanism that re-mounts MapContainer component
- Display location list as fallback when map fails

**Numbered Marker Implementation**:

- Create custom Leaflet DivIcon with CSS-styled numbered badges
- Use location.sequence to determine marker number
- Apply ContraVento primary color (#2563eb) for consistency
- Ensure markers are accessible (aria-labels for screen readers)

**Fullscreen Mode**:

- Use browser Fullscreen API (requestFullscreen/exitFullscreen)
- Add toggle button to map UI (top-right corner)
- CSS transitions for smooth fullscreen entry/exit
- Responsive layout adjustments in fullscreen

**Testing Strategy**:

- Vitest + React Testing Library for unit tests
- Mock Leaflet components (MapContainer, Marker, Polyline)
- Test error states, marker rendering, zoom calculation logic
- Snapshot tests for visual regression detection

### Files to Modify

```text
frontend/
├── src/
│   ├── components/trips/
│   │   ├── TripMap.tsx                    # UPDATE: Error handling, numbered markers, fullscreen
│   │   ├── TripMap.css                    # UPDATE: Numbered marker styles, fullscreen styles
│   │   └── TripMapError.tsx               # NEW: Error boundary component (optional)
│   └── utils/
│       └── mapHelpers.ts                  # NEW: Create numbered marker icon utility
└── tests/
    └── unit/
        └── TripMap.test.tsx               # NEW: Unit tests (T020-T023)
```

### Implementation Tasks (High-Level)

1. **Error Handling** (1-2 days)
   - Add error state to TripMap component
   - Implement tile load error detection
   - Create error UI with retry button
   - Test error recovery flow

2. **Numbered Markers** (1 day)
   - Create createNumberedMarkerIcon() utility
   - Replace default Icon with custom DivIcon
   - Style numbered badges with CSS
   - Test marker rendering

3. **Fullscreen Mode** (1 day)
   - Add fullscreen state management
   - Implement toggle button UI
   - Handle browser Fullscreen API
   - Test fullscreen transitions

4. **Unit Testing** (1-2 days)
   - Write tests for error handling (T020)
   - Write tests for marker rendering (T021)
   - Write tests for polyline rendering (T022)
   - Write tests for zoom calculation (T023)
   - Achieve ≥90% coverage

### Success Criteria (Phase 5 Complete When...)

- ✅ Map displays numbered markers (1, 2, 3...) corresponding to location sequence
- ✅ Network errors trigger error message with "Retry" button
- ✅ Clicking "Retry" successfully reloads map without page refresh
- ✅ Fullscreen mode expands map to fill viewport
- ✅ TripMap unit tests achieve ≥90% code coverage
- ✅ All 4 deferred tests (T020-T023) passing
- ✅ No regressions in existing map functionality

### Dependencies

- **Leaflet.js**: Already installed (react-leaflet dependency)
- **Browser Fullscreen API**: No additional dependencies
- **Vitest**: Already configured in frontend project

---

## Phase 6: Future Enhancements (Deferred)

**Status**: Not Planned

**Potential Features** (not in current scope):

- Elevation profile visualization
- Export map as image/PDF
- Marker clustering for trips with many locations
- Offline map tile caching
- Route editing (drag-and-drop markers to adjust route)
- Turn-by-turn directions integration
- GPX file import/export
