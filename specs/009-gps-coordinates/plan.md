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

**Status**: ⏸️ PENDING

Generated by `/speckit.tasks` command (separate from this plan).

See [tasks.md](tasks.md) once generated.
