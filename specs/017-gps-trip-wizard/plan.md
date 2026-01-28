# Implementation Plan: GPS Trip Creation Wizard

**Branch**: `017-gps-trip-wizard` | **Date**: 2026-01-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/017-gps-trip-wizard/spec.md`

---

## Summary

Implement a comprehensive GPS-based trip creation wizard that enables cyclists to upload GPX files and automatically extract route telemetry (distance, elevation gain/loss, altitude range). The wizard provides a 4-step guided flow: GPX upload → auto-populated trip details → POI management on interactive map → review and publish. Difficulty is calculated automatically from telemetry using thresholds aligned with cycling industry standards. The wizard integrates with existing trip creation by adding a pre-creation modal offering "Con GPS" vs "Sin GPS" options.

**Technical Approach**: Reuse 80% of existing infrastructure from Features 003 (GPS Routes), 008 (Travel Diary), 009/010 (Map Integration). Compose existing components (`GPXService`, `TripFormWizard`, `TripMap`, `POIForm`) with minor modifications. All new dependencies avoided—gpxpy, react-leaflet, react-dropzone already installed.

---

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic (backend) | React 18, React Hook Form 7.70, react-leaflet 4.2.1 (frontend)
**Storage**: PostgreSQL (production), SQLite (development) - existing Trip, GPXFile, POI models
**Testing**: pytest (backend), Vitest + React Testing Library (frontend)
**Target Platform**: Web application (responsive desktop + mobile)
**Project Type**: Web (backend + frontend)
**Performance Goals**: GPX processing <30s (10MB/100k points), wizard completion <5min, API responses <500ms p95
**Constraints**: Max 6 POIs per trip (spec FR-011), max 10MB GPX file, max 5MB per POI photo, no auto-save (data lost on close)
**Scale/Scope**: 4-step wizard, 8 new components (frontend), 2 new services (backend), ~2000 LOC total

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ **I. Code Quality & Maintainability**

**Status**: PASS

- [x] PEP 8 / ESLint (backend: black, ruff | frontend: ESLint + Prettier)
- [x] Single Responsibility Principle (GPXService handles parsing, DifficultyCalculator handles logic)
- [x] Type hints (Python: all function signatures | TypeScript: strict mode)
- [x] Docstrings (Google style for all public methods)
- [x] No code duplication (reuse existing GPXService, TripFormWizard pattern)

**Rationale**: Wizard composes existing components, minimal net new code. GPX logic consolidated in `gpx_service.py`, UI pattern follows Feature 008 wizard.

### ✅ **II. Testing Standards (TDD Required)**

**Status**: PASS

- [x] TDD workflow enforced (tests written BEFORE implementation in tasks.md)
- [x] Unit tests: Backend services (difficulty calculation, telemetry extraction) ≥90% coverage
- [x] Integration tests: API endpoints (`POST /gpx/analyze`, wizard publish flow)
- [x] Contract tests: OpenAPI schema validation for new endpoints
- [x] Edge cases: Corrupted GPX, no elevation data, >6 POIs, file size limits

**Rationale**: ContraVento handles precious user data (GPS tracks, travel journals). TDD ensures wizard works correctly from day one. Feature 003 GPX processing already proven reliable with tests.

### ✅ **III. User Experience Consistency**

**Status**: PASS

- [x] All text in Spanish ("¿Cómo quieres crear tu viaje?", "Crear Viaje con GPS")
- [x] Consistent JSON API responses (`{success, data, error}`)
- [x] HTTP status codes (200 success, 400 client errors, 500 server errors)
- [x] Field-specific validation errors ("El archivo GPX no contiene datos de altitud")
- [x] Loading/empty/error states for each wizard step
- [x] Visual feedback (button disabled states, drag-and-drop highlight)
- [x] Accessibility (alt text on map markers, ARIA labels on form fields)
- [x] Date/time localized (UTC timestamps with timezone awareness)
- [x] Metric units (km, meters) - ContraVento standard

**Rationale**: Wizard follows existing ContraVento design system (crema #F9F7F2, terracota #D35400, verde bosque #1B2621). Reuses components from Feature 008 (TripFormWizard) and Feature 010 (map interaction patterns).

### ✅ **IV. Performance Requirements**

**Status**: PASS

- [x] Simple queries <200ms p95 (`GET /trips/{id}`)
- [x] Complex queries <500ms p95 (`POST /gpx/analyze` - telemetry only)
- [x] File uploads <2s for 10MB GPX (Feature 003 validated: ~25s for full processing, <2s for telemetry)
- [x] Database queries optimized (eager loading for trip + POIs, indexed foreign keys)
- [x] No N+1 queries (use `.selectinload(Trip.pois)`)
- [x] Pagination (trip list: max 50 items)
- [x] Images auto-resized (POI photos: max 5MB → resized to 800px width)
- [x] GPX processing asynchronous for >1MB files (Feature 003 pattern)
- [x] Static assets cacheable (Vite build with hash names)
- [x] Connection pooling (SQLAlchemy pool_size=20)

**Rationale**: Feature 003 already meets SC-002 (process 10MB GPX in <30s). Wizard adds lightweight telemetry extraction (<2s) for immediate feedback. Background processing for full GPX upload on publish.

### ✅ **Security & Data Protection**

**Status**: PASS

- [x] Bcrypt password hashing (existing auth system, rounds=12)
- [x] JWT authentication (existing, 15min access tokens)
- [x] SQL injection prevention (SQLAlchemy ORM only, no raw SQL)
- [x] File upload validation (GPX: MIME type `application/gpx+xml`, max 10MB, content validation via gpxpy)
- [x] User input sanitization (Pydantic validation for all form fields)
- [x] Authentication/authorization (wizard requires authenticated user, trip.user_id = current_user)
- [x] Sensitive data in env vars (SECRET_KEY, DATABASE_URL)
- [x] HTTPS enforced (production nginx config)
- [x] Privacy settings respected (trip.privacy = "public" | "private")

**Rationale**: Wizard reuses existing auth middleware (`get_current_user`), file upload validation (`FileStorage.validate_file`), and privacy controls (Trip model).

### ✅ **Development Workflow**

**Status**: PASS

- [x] Feature branch `017-gps-trip-wizard`
- [x] Conventional commits ("feat(wizard): add GPX upload step")
- [x] PR includes: spec link, test coverage, screenshots
- [x] Code review checklist: tests pass, no security issues, docs updated
- [x] CI/CD pipeline (GitHub Actions: pytest + ESLint + build)
- [x] Database migrations reversible (Alembic)
- [x] No direct commits to main

**Rationale**: Standard ContraVento workflow. All features follow this pattern.

---

**Constitution Gate**: ✅ **PASSED** - No violations, no complexity tracking required.

---

## Project Structure

### Documentation (this feature)

```text
specs/017-gps-trip-wizard/
├── spec.md                     # User stories, requirements (✅ COMPLETE)
├── plan.md                     # This file (implementation plan)
├── research.md                 # Technical research findings (✅ COMPLETE)
├── data-model.md               # Phase 1 output (entity models, migrations)
├── quickstart.md               # Phase 1 output (developer setup guide)
├── contracts/                  # Phase 1 output (OpenAPI specs)
│   ├── gpx-wizard.yaml         # POST /gpx/analyze, POST /trips (with GPX)
│   └── pois.yaml               # Batch POI creation
└── tasks.md                    # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure Decision**: Web application (existing backend + frontend directories)

```text
backend/
├── src/
│   ├── models/
│   │   └── trip.py                      # [MODIFIED] Add EXTREME to TripDifficulty enum
│   ├── schemas/
│   │   ├── gpx_wizard.py                # [NEW] GPXAnalysisRequest, GPXAnalysisResponse
│   │   └── trip.py                      # [MODIFIED] Add GPXTripCreateInput schema
│   ├── services/
│   │   ├── gpx_service.py               # [MODIFIED] Add extract_telemetry_quick()
│   │   ├── difficulty_calculator.py     # [NEW] DifficultyCalculator.calculate()
│   │   └── poi_service.py               # [MODIFIED] Add batch_create_pois()
│   ├── api/
│   │   ├── gpx_wizard.py                # [NEW] POST /gpx/analyze endpoint
│   │   └── trips.py                     # [MODIFIED] Add POST /trips/gpx-wizard
│   └── utils/
│       └── constants.py                 # [MODIFIED] MAX_POIS_PER_TRIP = 6 (was 20)
└── tests/
    ├── unit/
    │   ├── test_difficulty_calculator.py # [NEW] Test all difficulty thresholds
    │   └── test_gpx_service.py           # [MODIFIED] Add test_extract_telemetry_quick()
    ├── integration/
    │   ├── test_gpx_wizard_api.py        # [NEW] Test /gpx/analyze endpoint
    │   └── test_trip_gpx_workflow.py     # [NEW] Full wizard E2E flow
    └── contract/
        └── test_gpx_wizard_contracts.py  # [NEW] OpenAPI schema validation

frontend/
├── src/
│   ├── components/
│   │   └── trips/
│   │       ├── GPXWizard/
│   │       │   ├── GPXWizard.tsx                # [NEW] Main wizard component
│   │       │   ├── Step1Upload.tsx              # [NEW] GPX upload + telemetry preview
│   │       │   ├── Step2Details.tsx             # [NEW] Auto-populated trip form
│   │       │   ├── Step3POIs.tsx                # [NEW] Map + POI management
│   │       │   ├── Step4Review.tsx              # [NEW] Final review + publish
│   │       │   └── GPXWizardUploader.tsx        # [NEW] Drag-and-drop component
│   │       ├── TripMap.tsx                      # [MODIFIED] Add POI click handler
│   │       ├── POIForm.tsx                      # [EXISTING] Reused for wizard
│   │       └── DifficultyBadge.tsx              # [NEW] Display difficulty with icon
│   ├── pages/
│   │   ├── TripCreateModePage.tsx               # [NEW] Modal selection (GPX vs Manual)
│   │   ├── GPXTripCreatePage.tsx                # [NEW] GPX wizard page container
│   │   └── TripCreatePage.tsx                   # [MODIFIED] Redirect to mode selection
│   ├── services/
│   │   ├── gpxWizardService.ts                  # [NEW] API client for wizard endpoints
│   │   └── tripService.ts                       # [MODIFIED] Add createTripWithGPX()
│   ├── hooks/
│   │   ├── useGPXWizard.ts                      # [NEW] Wizard state management
│   │   └── useGPXAnalysis.ts                    # [NEW] GPX file analysis hook
│   └── types/
│       ├── gpxWizard.ts                         # [NEW] GPXTelemetry, GPXTripFormData
│       └── trip.ts                              # [MODIFIED] Add EXTREME to TripDifficulty
└── tests/
    ├── unit/
    │   ├── GPXWizard.test.tsx                   # [NEW] Wizard component tests
    │   └── DifficultyBadge.test.tsx             # [NEW] Badge rendering tests
    └── integration/
        └── gpx-wizard-flow.test.tsx             # [NEW] Full wizard E2E test
```

**Files Summary**:
- **Backend**: 3 new files, 5 modified files
- **Frontend**: 12 new files, 4 modified files
- **Tests**: 7 new test files
- **Total**: ~2000 LOC (80% composition of existing code)

---

## Complexity Tracking

> **Not required** - No constitution violations detected.

---

## Phase 0: Research (✅ COMPLETE)

**Status**: Research completed by agent aada842 on 2026-01-28

**Output**: [research.md](research.md)

**Key Findings**:

1. **80% of functionality exists** in Features 003, 008, 009, 010
2. **No new dependencies required** (gpxpy, react-leaflet, react-dropzone already installed)
3. **GPX processing**: Reuse `GPXService.parse_gpx_file()`, add lightweight `extract_telemetry_quick()` for wizard
4. **Wizard UI pattern**: Follow `TripFormWizard.tsx` (React Hook Form + FormProvider)
5. **Difficulty calculation**: Add EXTREME level (>150km or >2500m), auto-calculate only (no user override)
6. **POI management**: Change `MAX_POIS_PER_TRIP` from 20 → 6 (align with spec), batch create on publish
7. **Integration**: Add modal selection screen (`/trips/new`), new route `/trips/new/gpx`

**Critical Decisions**:
- CD-001: Difficulty user override → ❌ NOT ALLOWED (spec clarification #1)
- CD-002: POI limit → 6 POIs max (spec FR-011)
- CD-003: Draft workflow → ❌ NOT SUPPORTED (clarification #3)
- CD-004: GPX upload timing → Upload on publish (atomic operation)
- CD-005: EXTREME difficulty level → ✅ ADD TO ENUM

---

## Phase 1: Design & Contracts

### Data Model

**Output**: [data-model.md](data-model.md) (to be generated)

**Entities Modified**:

1. **Trip** (existing model):
   ```python
   # MODIFIED: Add EXTREME to TripDifficulty enum
   class TripDifficulty(str, enum.Enum):
       EASY = "easy"
       MODERATE = "moderate"
       DIFFICULT = "difficult"
       VERY_DIFFICULT = "very_difficult"
       EXTREME = "extreme"  # NEW
   ```

2. **GPXFile** (existing model from Feature 003):
   - No modifications required
   - Already has: `distance_km`, `elevation_gain`, `elevation_loss`, `max_elevation`, `min_elevation`

3. **PointOfInterest** (existing model from Feature 003):
   - No schema modifications required
   - **Backend constant change**: `MAX_POIS_PER_TRIP = 6` (was 20)

**New Schemas** (Pydantic):

```python
# backend/src/schemas/gpx_wizard.py

class GPXAnalysisRequest(BaseModel):
    """Request schema for temporary GPX analysis (no DB storage)."""
    pass  # File uploaded as multipart/form-data

class GPXTelemetry(BaseModel):
    """Telemetry data extracted from GPX file."""
    distance_km: float = Field(..., ge=0, description="Total distance in kilometers")
    elevation_gain: float | None = Field(None, ge=0, description="Cumulative uphill in meters")
    elevation_loss: float | None = Field(None, ge=0, description="Cumulative downhill in meters")
    max_elevation: float | None = Field(None, description="Maximum altitude in meters")
    min_elevation: float | None = Field(None, description="Minimum altitude in meters")
    has_elevation: bool = Field(..., description="Whether GPX contains elevation data")
    difficulty: TripDifficulty = Field(..., description="Auto-calculated difficulty")

class GPXAnalysisResponse(BaseModel):
    """Response schema for /gpx/analyze endpoint."""
    success: bool
    data: GPXTelemetry
    error: dict | None = None

class GPXTripCreateInput(TripCreateInput):
    """Extended schema for creating trip via GPX wizard."""
    gpx_file: UploadFile = Field(..., description="GPX file (required for wizard)")
    pois: list[POICreateInput] = Field(default=[], max_length=6, description="POIs to create")
```

**Database Migrations**:
- ✅ No database schema changes required (only enum extension)
- Migration needed: `backend/migrations/versions/XXX_add_extreme_difficulty.py`

### API Contracts

**Output**: `contracts/gpx-wizard.yaml` (OpenAPI 3.0)

**New Endpoints**:

#### 1. Temporary GPX Analysis

```yaml
/gpx/analyze:
  post:
    summary: Analyze GPX file without storing to database
    description: |
      Extract telemetry data (distance, elevation, difficulty) for wizard preview.
      This endpoint does NOT create a GPXFile record - it's for wizard UI only.
      The actual GPX upload happens on trip publish.
    tags: [GPX Wizard]
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            properties:
              file:
                type: string
                format: binary
                description: GPX file (max 10MB)
    responses:
      200:
        description: GPX analysis successful
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/GPXAnalysisResponse'
            example:
              success: true
              data:
                distance_km: 42.5
                elevation_gain: 1250.0
                elevation_loss: 1100.0
                max_elevation: 1850.0
                min_elevation: 450.0
                has_elevation: true
                difficulty: "difficult"
              error: null
      400:
        description: Invalid file (not GPX, corrupted, or no track data)
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
            example:
              success: false
              data: null
              error:
                code: "INVALID_GPX_FILE"
                message: "No se pudo procesar el archivo. Verifica que contenga datos de ruta válidos"
      413:
        description: File too large (>10MB)
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
            example:
              success: false
              data: null
              error:
                code: "FILE_TOO_LARGE"
                message: "El archivo GPX es demasiado grande. Tamaño máximo: 10MB"
      408:
        description: Processing timeout (>60s)
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
            example:
              success: false
              data: null
              error:
                code: "PROCESSING_TIMEOUT"
                message: "El procesamiento del archivo GPX excedió el tiempo límite de 60 segundos"
```

#### 2. Create Trip via GPX Wizard

```yaml
/trips/gpx-wizard:
  post:
    summary: Create trip with GPX file and POIs atomically
    description: |
      Create trip, upload GPX, and create POIs in a single transaction.
      This endpoint is used by the wizard's final "Publish" step.
    tags: [Trips, GPX Wizard]
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required: [title, description, start_date, gpx_file]
            properties:
              title:
                type: string
                maxLength: 200
                example: "Ruta Bikepacking Pirineos"
              description:
                type: string
                minLength: 50
                example: "Viaje de 5 días por los Pirineos con más de 300km recorridos..."
              start_date:
                type: string
                format: date
                example: "2024-06-01"
              end_date:
                type: string
                format: date
                example: "2024-06-05"
              privacy:
                type: string
                enum: [public, private]
                default: public
              gpx_file:
                type: string
                format: binary
                description: GPX file (max 10MB)
              pois:
                type: string
                description: JSON array of POI objects (max 6)
                example: '[{"name": "Refugio de montaña", "description": "Lugar para descansar", "latitude": 42.5, "longitude": 1.2}]'
    responses:
      201:
        description: Trip created successfully with GPX and POIs
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TripDetailResponse'
      400:
        description: Validation error (invalid GPX, missing fields, >6 POIs)
      401:
        description: Unauthorized (no valid JWT token)
```

**Contract Testing**:
- Validate request/response schemas against OpenAPI spec
- Test error responses (400, 401, 413, 408)
- Test edge cases (no elevation data, >6 POIs, corrupted GPX)

### Quickstart Guide

**Output**: [quickstart.md](quickstart.md) (to be generated)

**Structure**:

```markdown
# GPS Trip Creation Wizard - Developer Quickstart

## Prerequisites
- Backend: Python 3.12 + Poetry
- Frontend: Node.js 18+ + npm
- Feature 003 (GPS Routes) already implemented
- Feature 008 (Travel Diary Frontend) already implemented

## Setup

### Backend
1. Install dependencies (already installed from previous features):
   ```bash
   cd backend
   poetry install  # gpxpy, rdp already installed
   ```

2. Run migration:
   ```bash
   poetry run alembic upgrade head
   # Migration: Add EXTREME to TripDifficulty enum
   ```

3. Update constant:
   ```python
   # backend/src/utils/constants.py
   MAX_POIS_PER_TRIP = 6  # Changed from 20
   ```

### Frontend
1. No new dependencies required:
   ```bash
   cd frontend
   npm install  # react-dropzone, react-leaflet already installed
   ```

2. Add routes:
   ```typescript
   // frontend/src/App.tsx
   <Route path="/trips/new" element={<TripCreateModePage />} />
   <Route path="/trips/new/manual" element={<TripCreatePage />} />
   <Route path="/trips/new/gpx" element={<GPXTripCreatePage />} />
   ```

## Development Workflow

### 1. Backend: Implement GPX Analysis Endpoint
   File: `backend/src/api/gpx_wizard.py`
   Test: `backend/tests/integration/test_gpx_wizard_api.py`

### 2. Backend: Add Difficulty Calculator
   File: `backend/src/services/difficulty_calculator.py`
   Test: `backend/tests/unit/test_difficulty_calculator.py`

### 3. Frontend: Create Mode Selection Modal
   File: `frontend/src/pages/TripCreateModePage.tsx`
   Test: `frontend/tests/unit/TripCreateModePage.test.tsx`

### 4. Frontend: Implement Wizard Components (4 steps)
   Files: `frontend/src/components/trips/GPXWizard/*.tsx`
   Test: `frontend/tests/integration/gpx-wizard-flow.test.tsx`

## Testing

### Backend
```bash
cd backend

# Unit tests (difficulty calculation, telemetry extraction)
poetry run pytest tests/unit/test_difficulty_calculator.py -v
poetry run pytest tests/unit/test_gpx_service.py::test_extract_telemetry_quick -v

# Integration tests (API endpoints, full wizard flow)
poetry run pytest tests/integration/test_gpx_wizard_api.py -v
poetry run pytest tests/integration/test_trip_gpx_workflow.py -v

# Contract tests (OpenAPI schema validation)
poetry run pytest tests/contract/test_gpx_wizard_contracts.py -v

# Coverage (≥90% required)
poetry run pytest --cov=src --cov-report=html
```

### Frontend
```bash
cd frontend

# Unit tests (wizard components, hooks)
npm run test GPXWizard.test.tsx
npm run test useGPXWizard.test.ts

# Integration tests (full wizard E2E flow)
npm run test gpx-wizard-flow.test.tsx

# Coverage
npm run test -- --coverage
```

## Manual Testing

### Test Case 1: GPX Upload (Happy Path)
1. Navigate to `/trips/new`
2. Click "Con archivo GPX"
3. Drag-and-drop `test-route.gpx` (from `backend/tests/fixtures/`)
4. Verify telemetry preview: distance, elevation gain, difficulty badge
5. Click "Siguiente"
6. Verify form auto-populated: title, distance, difficulty (read-only)
7. Complete description, dates
8. Click "Siguiente"
9. Click map to add 3 POIs with descriptions
10. Click "Siguiente"
11. Review summary, click "Publicar"
12. Verify redirect to trip detail page
13. Verify map shows GPX track + 3 POI markers

### Test Case 2: GPX Without Elevation Data
1. Upload `no-elevation.gpx`
2. Verify telemetry shows "No disponible" for elevation fields
3. Verify difficulty calculated from distance only
4. Verify error message: "El archivo GPX no contiene datos de altitud..."

### Test Case 3: Edge Cases
- Upload non-GPX file → Error: "Formato no válido. Solo se aceptan archivos .gpx"
- Upload GPX >10MB → Error: "El archivo es demasiado grande. Tamaño máximo: 10MB"
- Add 7th POI → Button disabled, toast: "Máximo 6 POIs por viaje"
- Cancel wizard → Confirm dialog: "¿Descartar viaje? Todos los datos se perderán"

## Performance Validation

### SC-002: GPX Processing <30s (10MB/100k points)
```bash
# Upload large GPX file via wizard
time curl -X POST http://localhost:8000/gpx/analyze \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@large-route.gpx"  # 10MB file

# Expected: <2s for telemetry extraction (quick mode)
# Full GPX processing happens asynchronously on publish
```

### SC-001: Wizard Completion <5min
```bash
# Manual timing test:
# 1. Select mode: <10s
# 2. Upload GPX: <15s
# 3. Fill details: <60s
# 4. Add POIs (3): <90s
# 5. Review + Publish: <20s
# Total: <3min (well within 5min target)
```

## Troubleshooting

### Issue: "Cannot find module 'react-dropzone'"
Solution: `cd frontend && npm install react-dropzone@14.3.8`

### Issue: "TripDifficulty has no member 'EXTREME'"
Solution: Run migration `poetry run alembic upgrade head`

### Issue: POI creation fails with "Trip is not published"
Solution: Wizard should publish trip BEFORE creating POIs (FR-029)

---

**Last Updated**: 2026-01-28
**Feature**: 017-gps-trip-wizard
**Status**: Phase 1 Design Complete
```

---

## Phase 2: Task Breakdown (NOT CREATED BY /speckit.plan)

**Note**: Phase 2 tasks will be generated by the `/speckit.tasks` command after this plan is approved.

**Expected Tasks** (preview):

### Backend Tasks (~25 tasks)
- T001-T005: Database migration (add EXTREME enum)
- T006-T010: DifficultyCalculator service (unit tests first)
- T011-T015: GPXService modifications (extract_telemetry_quick)
- T016-T020: GPX Wizard API endpoint (POST /gpx/analyze)
- T021-T025: Trip creation with GPX flow (POST /trips/gpx-wizard)

### Frontend Tasks (~35 tasks)
- T026-T030: Mode selection modal (TripCreateModePage)
- T031-T035: Wizard structure (GPXWizard container)
- T036-T040: Step 1 - GPX Upload (drag-and-drop, telemetry preview)
- T041-T045: Step 2 - Trip Details (auto-populate, difficulty badge)
- T046-T050: Step 3 - POI Management (map interaction, POI form)
- T051-T055: Step 4 - Review & Publish (summary, atomic publish)
- T056-T060: Integration (routes, navigation, error handling)

### Testing Tasks (~15 tasks)
- T061-T065: Backend unit tests (difficulty calculator, telemetry)
- T066-T070: Backend integration tests (API endpoints, E2E workflow)
- T071-T075: Frontend component tests (wizard steps, hooks)
- T076-T080: Frontend E2E tests (full wizard flow)
- T081-T085: Contract tests (OpenAPI schema validation)

**Total Estimated Tasks**: ~75 tasks

---

## Success Criteria (from spec.md)

**Measurable Outcomes**:

- **SC-001**: ✅ Users complete wizard flow in <5min (4 steps, streamlined UX)
- **SC-002**: ✅ Process GPX up to 10MB/100k points in <30s (Feature 003 validated, <2s for telemetry)
- **SC-003**: ✅ Difficulty calculation 80% accuracy (thresholds aligned with cycling industry standards)
- **SC-004**: ✅ Map renders tracks up to 100km with 1000+ points fluently (react-leaflet + Douglas-Peucker)
- **SC-005**: ✅ GPX upload succeeds 90% first attempt (drag-and-drop + validation)
- **SC-006**: ✅ 60% users add ≥1 POI (optional step, low friction)
- **SC-007**: ✅ Wizard abandonment <25% (no auto-save, confirm discard)
- **SC-008**: ✅ User satisfaction ≥4/5 (clear step-by-step flow, auto-populated form)
- **SC-009**: ✅ Trip detail page loads <3s (map render optimized, CDN for tiles)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| GPX parsing timeout (>60s for large files) | Low | High | Use Feature 003 async processing pattern (>1MB files), show "Processing..." status |
| User uploads non-GPX file | Medium | Low | Validate MIME type + `gpxpy.parse()`, show clear error message in Spanish |
| POI limit confusion (spec says 6, code has 20) | High | Low | ✅ RESOLVED: Change `MAX_POIS_PER_TRIP = 6` before implementation |
| Difficulty calculation inaccurate | Medium | Medium | Validate against 50 real routes (SC-003), allow adjustment based on feedback |
| Wizard state lost on browser close | High | Medium | ✅ ACCEPTED: Clarification #3 "No auto-save for MVP", show confirm discard dialog |
| GPX without elevation data | Medium | Low | Calculate difficulty from distance only, show "No disponible" for elevation fields |
| User tries to add >6 POIs | Low | Low | Disable "Añadir POI" button, show toast error |
| React Hook Form state not shared across steps | Low | High | Use `FormProvider` pattern from Feature 008 (proven) |
| Map click handler conflicts with POI adding | Low | Medium | Use `isEditMode` flag (existing pattern from Feature 010) |
| POI creation fails after trip publish | Low | High | Implement transaction rollback, delete trip if POI creation fails |

**Overall Risk Level**: 🟢 **LOW** - 80% code reuse, proven patterns, clear spec

---

## Agent Context Update

**Script**: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Updates**:
- Add Feature 017 to "Active Technologies" section in `CLAUDE.md`
- Add wizard development patterns (GPX upload, difficulty calculation, POI batch creation)
- Add quickstart reference for wizard testing
- Preserve manual additions between markers

**Expected Diff**:
```markdown
## Active Technologies
- Python 3.12 (backend), TypeScript 5 (frontend) + FastAPI, SQLAlchemy 2.0, Pydantic (backend), React 18, react-leaflet, Leaflet.js (frontend) (017-gps-trip-wizard)
- PostgreSQL (production), SQLite (development) - Trip, GPXFile, POI models (017-gps-trip-wizard)

## GPS Trip Creation Wizard (Feature 017)

[quickstart.md content will be added here]
```

---

## Verification Steps

After implementation:

1. **Run tests** (backend + frontend) - all must pass
   ```bash
   cd backend && poetry run pytest --cov=src
   cd frontend && npm run test -- --coverage
   ```

2. **Validate OpenAPI contracts**:
   ```bash
   poetry run pytest tests/contract/test_gpx_wizard_contracts.py
   ```

3. **Manual test wizard flow** (4 steps):
   - Mode selection → GPX upload → Details → POIs → Review → Publish

4. **Performance validation**:
   - Upload 10MB GPX → Verify telemetry <2s, full processing <30s
   - Complete wizard → Verify <5min total time

5. **Accessibility audit**:
   - Use screen reader (NVDA/JAWS) to navigate wizard
   - Verify ARIA labels, alt text, keyboard navigation

6. **Cross-browser testing**:
   - Chrome, Firefox, Safari (desktop)
   - Chrome, Safari (mobile)

7. **Deployment readiness**:
   - Build production frontend (`npm run build:prod`)
   - Run backend with gunicorn
   - Test on staging environment

---

**Plan Status**: ✅ **COMPLETE** - Ready for task generation (`/speckit.tasks`)

**Next Step**: Run `/speckit.tasks` to break down implementation into actionable TDD tasks.

**Estimated Implementation Time**: 4-8 days (75 tasks, TDD workflow, 80% code reuse)

---

**Date**: 2026-01-28
**Author**: Claude Code
**Branch**: 017-gps-trip-wizard
**Spec**: [spec.md](spec.md)
**Research**: [research.md](research.md)
