# Implementation Tasks: GPS Trip Creation Wizard

**Feature**: 017-gps-trip-wizard
**Branch**: `017-gps-trip-wizard`
**Date**: 2026-01-28
**Workflow**: Test-Driven Development (TDD) - Write tests FIRST, then implement

---

## Overview

**Total Estimated Tasks**: 85 tasks (setup + 6 user stories + polish)

**Implementation Strategy**: Incremental delivery by user story priority

**TDD Workflow (MANDATORY)**:
1. ✅ **RED**: Write failing test
2. ✅ **GREEN**: Implement minimum code to pass
3. ✅ **REFACTOR**: Clean up while keeping tests green

**Parallel Opportunities**: Tasks marked with `[P]` can run in parallel

---

## Task Summary by User Story

| Phase | User Story | Priority | Tasks | Estimated Time |
|-------|------------|----------|-------|----------------|
| Phase 1 | Setup & Prerequisites | - | 8 tasks | 2 hours |
| Phase 2 | Foundational (Blocking) | - | 12 tasks | 6 hours |
| Phase 3 | **US1**: Mode Selection Modal | P1 | 10 tasks | 4 hours |
| Phase 4 | **US2**: GPX Upload & Processing | P2 | 18 tasks | 8 hours |
| Phase 5 | **US3**: Trip Details + Difficulty | P3 | 12 tasks | 6 hours |
| Phase 6 | **US6**: Publish Trip (Atomic) | P2 | 10 tasks | 5 hours |
| Phase 7 | **US4**: Map Visualization | P4 | 8 tasks | 4 hours |
| Phase 8 | **US5**: POI Management | P5 | 10 tasks | 5 hours |
| Phase 9 | Polish & Cross-Cutting | - | 7 tasks | 3 hours |
| **Total** | | | **85 tasks** | **43 hours (~5-6 days)** |

---

## User Story Dependencies

```
US1 (P1) → [BLOCKS] → US2, US3, US4, US5, US6
    ↓
US2 (P2) → [BLOCKS] → US3, US4, US6
    ↓
US3 (P3) → [BLOCKS] → US6
    ↓
US6 (P2) ← [NEEDS] ← US2, US3 (MVP: US1+US2+US3+US6)
    ↓
US4 (P4) ← [OPTIONAL] ← US2
    ↓
US5 (P5) ← [OPTIONAL] ← US2, US4
```

**MVP Scope** (Minimum Viable Product):
- ✅ US1: Mode Selection (entry point)
- ✅ US2: GPX Upload (core functionality)
- ✅ US3: Trip Details (required fields)
- ✅ US6: Publish Trip (complete flow)
- ❌ US4: Map Visualization (nice-to-have)
- ❌ US5: POI Management (enhancement)

**Incremental Delivery**:
1. **Week 1**: MVP (US1+US2+US3+US6) → 48 tasks, ~23 hours
2. **Week 2**: Enhancements (US4+US5+Polish) → 25 tasks, ~12 hours

---

## Phase 1: Setup & Prerequisites

**Goal**: Initialize project structure, install dependencies, run migrations

**Duration**: 2 hours

**Independent Test**: Run backend server + frontend dev server, verify no errors

### Tasks

- [ ] T001 Verify Feature 003 (GPS Routes) implemented and working
- [ ] T002 Verify Feature 008 (Travel Diary Frontend) wizard pattern exists in frontend/src/components/trips/TripFormWizard.tsx
- [ ] T003 [P] Create feature branch 017-gps-trip-wizard from develop
- [ ] T004 [P] Verify backend dependencies: gpxpy==1.6.2, rdp==0.8 in backend/pyproject.toml
- [ ] T005 [P] Verify frontend dependencies: react-hook-form@7.70, react-dropzone@14.3, react-leaflet@4.2 in frontend/package.json
- [ ] T006 Create database migration for EXTREME difficulty level in backend/migrations/versions/XXX_add_extreme_difficulty.py
- [ ] T007 Apply migration: poetry run alembic upgrade head
- [ ] T008 Update MAX_POIS_PER_TRIP from 20 to 6 in backend/src/services/poi_service.py (line 24)

**Verification**:
```bash
# Backend
cd backend && poetry run alembic current  # Should show add_extreme_difficulty
poetry run python -c "from src.models.trip import TripDifficulty; assert TripDifficulty.EXTREME"

# Frontend
cd frontend && npm run dev  # Should start without errors
```

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Implement core services that all user stories depend on

**Duration**: 6 hours

**Independent Test**: Run unit tests for DifficultyCalculator and GPX telemetry extraction

### Backend Foundation

#### Difficulty Calculator Service (TDD)

- [ ] T009 Write unit tests for DifficultyCalculator in backend/tests/unit/test_difficulty_calculator.py (12 test cases for all thresholds)
- [ ] T010 Implement DifficultyCalculator.calculate() in backend/src/services/difficulty_calculator.py (see data-model.md line 144)
- [ ] T011 Run tests: poetry run pytest tests/unit/test_difficulty_calculator.py -v (should pass)

#### GPX Service Extension (TDD)

- [ ] T012 Write unit test for extract_telemetry_quick() in backend/tests/unit/test_gpx_service.py
- [ ] T013 Implement extract_telemetry_quick() method in backend/src/services/gpx_service.py (lightweight telemetry extraction)
- [ ] T014 Run tests: poetry run pytest tests/unit/test_gpx_service.py::test_extract_telemetry_quick -v

#### Pydantic Schemas

- [ ] T015 [P] Create GPXTelemetry schema in backend/src/schemas/gpx_wizard.py (see data-model.md line 285)
- [ ] T016 [P] Create GPXAnalysisResponse schema in backend/src/schemas/gpx_wizard.py
- [ ] T017 [P] Create GPXTripCreateInput schema in backend/src/schemas/gpx_wizard.py

### Frontend Foundation

#### TypeScript Types

- [ ] T018 [P] Add EXTREME to TripDifficulty enum in frontend/src/types/trip.ts
- [ ] T019 [P] Create GPXTelemetry interface in frontend/src/types/gpxWizard.ts
- [ ] T020 [P] Create GPXTripFormData interface in frontend/src/types/gpxWizard.ts

**Verification**:
```bash
cd backend && poetry run pytest tests/unit/ --cov=src/services/difficulty_calculator.py --cov=src/services/gpx_service.py
# Coverage: ≥90%
```

---

## Phase 3: US1 - Mode Selection Modal (Priority P1)

**User Story**: Como ciclista que quiere crear un nuevo viaje, quiero poder elegir si crear el viaje con o sin datos GPS desde el principio

**Goal**: Implement modal selection screen for GPS vs Manual trip creation

**Duration**: 4 hours

**Independent Test**: Navigate to /trips/new, verify modal displays with 2 options, click each option verifies correct navigation

### Frontend Components (TDD)

#### Mode Selection Modal Component

- [ ] T021 [US1] Write component tests for TripCreateModePage in frontend/tests/unit/TripCreateModePage.test.tsx
- [ ] T022 [US1] Create TripCreateModePage component in frontend/src/pages/TripCreateModePage.tsx
- [ ] T023 [US1] Add TripCreateModePage styles in frontend/src/pages/TripCreateModePage.css

#### Navigation Integration

- [ ] T024 [US1] Write tests for route configuration in frontend/tests/unit/App.test.tsx
- [ ] T025 [US1] Add routes to frontend/src/App.tsx: /trips/new → TripCreateModePage, /trips/new/manual → TripCreatePage, /trips/new/gpx → GPXTripCreatePage
- [ ] T026 [US1] Update TripCreatePage to redirect to /trips/new/manual if accessed directly

#### UI Components

- [ ] T027 [P] [US1] Create ModeCard component in frontend/src/components/trips/ModeCard.tsx (reusable card for each mode)
- [ ] T028 [P] [US1] Add icons: MapIcon, PencilIcon in frontend/src/components/icons/

#### Integration Tests

- [ ] T029 [US1] Write E2E test for mode selection flow in frontend/tests/integration/mode-selection.test.tsx
- [ ] T030 [US1] Run tests: npm run test TripCreateModePage.test.tsx mode-selection.test.tsx

**Verification** (Manual):
```
1. Navigate to http://localhost:5173/trips/new
2. Verify modal displays with:
   - "Crear Viaje con GPS" button
   - "Crear Viaje sin GPS" button
3. Click "Con GPS" → Navigate to /trips/new/gpx
4. Click "Sin GPS" → Navigate to /trips/new/manual
5. Press ESC → Modal closes, navigate back
```

**Acceptance Criteria**:
- [x] Modal displays two clear options (AS1.1)
- [x] "Con GPS" navigates to wizard (AS1.2)
- [x] "Sin GPS" navigates to manual form (AS1.3)
- [x] ESC/overlay click closes modal (AS1.4)

---

## Phase 4: US2 - GPX Upload & Processing (Priority P2)

**User Story**: Como ciclista con un archivo GPX de mi ruta, quiero poder cargar el archivo y ver que el sistema extrae automáticamente la telemetría básica

**Goal**: Implement GPX file upload with drag-and-drop and automatic telemetry extraction

**Duration**: 8 hours

**Independent Test**: Upload test-route.gpx, verify telemetry displayed (distance, elevation gain, difficulty badge)

### Backend API (TDD)

#### GPX Analysis Endpoint

- [ ] T031 [US2] Write integration tests for POST /gpx/analyze in backend/tests/integration/test_gpx_wizard_api.py (see contracts/gpx-wizard.yaml)
- [ ] T032 [US2] Implement POST /gpx/analyze endpoint in backend/src/api/gpx_wizard.py (uses extract_telemetry_quick)
- [ ] T033 [US2] Add error handling: 400 (invalid GPX), 408 (timeout), 413 (too large) in backend/src/api/gpx_wizard.py
- [ ] T034 [US2] Run integration tests: poetry run pytest tests/integration/test_gpx_wizard_api.py -v

#### Contract Tests

- [ ] T035 [P] [US2] Write contract tests for GPX wizard endpoints in backend/tests/contract/test_gpx_wizard_contracts.py (validate against contracts/gpx-wizard.yaml)
- [ ] T036 [P] [US2] Run contract tests: poetry run pytest tests/contract/test_gpx_wizard_contracts.py -v

### Frontend Components (TDD)

#### GPX Upload Component

- [ ] T037 [US2] Write tests for GPXWizardUploader in frontend/tests/unit/GPXWizardUploader.test.tsx
- [ ] T038 [US2] Create GPXWizardUploader component in frontend/src/components/trips/GPXWizard/GPXWizardUploader.tsx (based on existing GPXUploader)
- [ ] T039 [US2] Add drag-and-drop styling and validation (max 10MB, .gpx only)

#### Wizard Container

- [ ] T040 [US2] Write tests for GPXWizard container in frontend/tests/unit/GPXWizard.test.tsx
- [ ] T041 [US2] Create GPXWizard container in frontend/src/components/trips/GPXWizard/GPXWizard.tsx (React Hook Form + FormProvider)
- [ ] T042 [US2] Add wizard state management: currentStep, gpxData, formData

#### Step 1: Upload Component

- [ ] T043 [US2] Write tests for Step1Upload in frontend/tests/unit/Step1Upload.test.tsx
- [ ] T044 [US2] Create Step1Upload component in frontend/src/components/trips/GPXWizard/Step1Upload.tsx
- [ ] T045 [US2] Add telemetry preview display (distance, elevation, difficulty badge)

#### Hooks & Services

- [ ] T046 [P] [US2] Create useGPXAnalysis hook in frontend/src/hooks/useGPXAnalysis.ts (handles POST /gpx/analyze)
- [ ] T047 [P] [US2] Create gpxWizardService in frontend/src/services/gpxWizardService.ts (API client)
- [ ] T048 [P] [US2] Create useGPXWizard hook in frontend/src/hooks/useGPXWizard.ts (wizard state management)

**Verification** (Manual):
```
1. Navigate to /trips/new/gpx
2. Drag test-route.gpx (backend/tests/fixtures/) to upload area
3. Verify telemetry preview displays:
   - Distance: 42.5 km
   - Elevation gain: 1250 m
   - Difficulty: Difícil (orange badge)
4. Test edge cases:
   - Upload .jpg file → Error: "Formato no válido"
   - Upload 15MB GPX → Error: "Archivo demasiado grande"
   - Upload corrupted GPX → Error: "No se pudo procesar"
```

**Acceptance Criteria**:
- [x] Drag-and-drop GPX file uploads (AS2.1)
- [x] Invalid file format shows error (AS2.2)
- [x] Corrupted GPX shows error (AS2.3)
- [x] Success shows telemetry preview (AS2.1)
- [x] "Siguiente" button navigates to Step 2 (AS2.4)

---

## Phase 5: US3 - Trip Details with Difficulty Calculation (Priority P3)

**User Story**: Como ciclista que ha cargado un archivo GPX, quiero completar los detalles de mi viaje y ver la dificultad calculada automáticamente

**Goal**: Implement trip details form with auto-populated difficulty (read-only)

**Duration**: 6 hours

**Independent Test**: Upload GPX, navigate to Step 2, verify difficulty badge displays and is read-only, fill form and validate fields

### Backend Tests

- [ ] T049 [US3] Write unit tests for difficulty display in trip schema in backend/tests/unit/test_trip_schema.py
- [ ] T050 [US3] Verify difficulty is read-only in GPXTripCreateInput schema (no setter)

### Frontend Components (TDD)

#### Step 2: Details Component

- [ ] T051 [US3] Write tests for Step2Details in frontend/tests/unit/Step2Details.test.tsx
- [ ] T052 [US3] Create Step2Details component in frontend/src/components/trips/GPXWizard/Step2Details.tsx
- [ ] T053 [US3] Add form fields: title (max 200), description (min 50), start_date, end_date, privacy (public/private)
- [ ] T054 [US3] Auto-populate title from GPX filename, distance from telemetry

#### Difficulty Badge Component

- [ ] T055 [P] [US3] Write tests for DifficultyBadge in frontend/tests/unit/DifficultyBadge.test.tsx
- [ ] T056 [P] [US3] Create DifficultyBadge component in frontend/src/components/trips/DifficultyBadge.tsx (5 levels with colors)
- [ ] T057 [P] [US3] Add translateDifficulty() helper in frontend/src/utils/tripHelpers.ts (English enum → Spanish display)

#### Validation

- [ ] T058 [US3] Add Zod schema for trip details validation in frontend/src/schemas/tripFormSchema.ts
- [ ] T059 [US3] Add validation error messages in Spanish (title required, description min 50 chars)

#### Navigation & State

- [ ] T060 [US3] Implement "Siguiente" button with validation (trigger form validation before advancing)
- [ ] T061 [US3] Implement "Cancelar" button with confirm dialog ("¿Descartar viaje? Todos los datos se perderán")
- [ ] T062 [US3] Implement "Eliminar" button (discard GPX, return to Step 1)

**Verification** (Manual):
```
1. Upload GPX, navigate to Step 2
2. Verify form auto-populated:
   - Title: "test-route" (from filename)
   - Difficulty badge: "Difícil" (read-only, gray)
3. Fill details:
   - Title: "Ruta Bikepacking"
   - Description: (type 50+ chars)
   - Dates: 2024-06-01 to 2024-06-05
4. Verify validation:
   - Empty title → Error
   - Description <50 chars → Error "Mínimo 50 caracteres (X/50)"
5. Click "Siguiente" → Navigate to Step 3
6. Click "Cancelar" → Confirm dialog → Close wizard
```

**Acceptance Criteria**:
- [x] Difficulty badge displays dynamically (AS3.1)
- [x] Privacy selector works (AS3.2)
- [x] "Eliminar" discards GPX with confirm (AS3.3)
- [x] "Siguiente" validates and advances (AS3.4)
- [x] "Cancelar" shows confirm dialog (AS3.5)

---

## Phase 6: US6 - Publish Trip (Atomic Transaction) (Priority P2)

**User Story**: Como ciclista que ha completado todos los pasos del wizard GPS, quiero poder publicar mi viaje con un solo clic, consolidando todos los datos

**Goal**: Implement atomic trip creation with GPX upload and POI batch creation

**Duration**: 5 hours

**Independent Test**: Complete wizard Steps 1-4, click "Publicar", verify trip created with GPX linked

### Backend API (TDD)

#### Atomic Trip Creation Endpoint

- [ ] T063 [US6] Write integration tests for POST /trips/gpx-wizard in backend/tests/integration/test_trip_gpx_workflow.py (full wizard flow)
- [ ] T064 [US6] Implement POST /trips/gpx-wizard endpoint in backend/src/api/trips.py (atomic transaction)
- [ ] T065 [US6] Add transaction logic: create trip → upload GPX → batch create POIs in backend/src/api/trips.py
- [ ] T066 [US6] Add rollback on error (if POI creation fails, delete trip) in backend/src/api/trips.py
- [ ] T067 [US6] Run integration tests: poetry run pytest tests/integration/test_trip_gpx_workflow.py -v

### Frontend Components (TDD)

#### Step 4: Review & Publish Component

- [ ] T068 [US6] Write tests for Step4Review in frontend/tests/unit/Step4Review.test.tsx
- [ ] T069 [US6] Create Step4Review component in frontend/src/components/trips/GPXWizard/Step4Review.tsx
- [ ] T070 [US6] Add summary display: title, description, dates, difficulty, distance, elevation, POI count
- [ ] T071 [US6] Add "Publicar" button with loading state (disable during API call)
- [ ] T072 [US6] Implement publish handler: createTripWithGPX() → navigate to /trips/{id} on success

#### Service Integration

- [ ] T073 [P] [US6] Add createTripWithGPX() method in frontend/src/services/tripService.ts (POST /trips/gpx-wizard)
- [ ] T074 [P] [US6] Add error handling: show toast on failure, keep wizard open with error message

#### E2E Tests

- [ ] T075 [US6] Write E2E test for full wizard publish flow in frontend/tests/integration/gpx-wizard-publish.test.tsx
- [ ] T076 [US6] Run E2E tests: npm run test gpx-wizard-publish.test.tsx

**Verification** (Manual):
```
1. Complete Steps 1-3 of wizard
2. Navigate to Step 4 (Review)
3. Verify summary shows all data:
   - Title, description, dates
   - Difficulty badge
   - Distance, elevation gain
   - "0 POIs" (if none added)
4. Click "Publicar"
5. Verify:
   - Loading spinner appears
   - Success toast: "Viaje publicado correctamente"
   - Redirect to /trips/{trip_id}
6. Verify trip detail page shows:
   - GPX track on map
   - Telemetry data
   - All form fields
```

**Acceptance Criteria**:
- [x] "Publicar" creates trip with all data (AS6.1)
- [x] Redirect to trip detail page (AS6.2)
- [x] "Cancelar" shows confirm dialog (AS6.3)
- [x] Error handling shows Spanish message (AS6.4)

---

## Phase 7: US4 - Map Visualization (Priority P4)

**User Story**: Como ciclista que ha cargado un archivo GPX, quiero ver mi ruta visualizada en un mapa interactivo junto con un panel de datos de telemetría

**Goal**: Implement map visualization with GPX track and telemetry panel

**Duration**: 4 hours

**Independent Test**: Upload GPX, navigate to Step 3, verify map shows track line and telemetry panel displays all metrics

### Frontend Components (TDD)

#### Step 3: Map Visualization Component

- [ ] T077 [US4] Write tests for Step3Map in frontend/tests/unit/Step3Map.test.tsx
- [ ] T078 [US4] Create Step3Map component in frontend/src/components/trips/GPXWizard/Step3Map.tsx
- [ ] T079 [US4] Integrate TripMap component (reuse from Feature 009) with GPX trackpoints
- [ ] T080 [US4] Add telemetry panel: distance, elevation gain/loss, max/min altitude

#### Map Integration

- [ ] T081 [US4] Add GPX track polyline rendering in TripMap component (red line)
- [ ] T082 [US4] Add auto-centering: map.fitBounds(trackBounds) on load
- [ ] T083 [US4] Test map interactivity: zoom, pan, track remains visible

#### Navigation

- [ ] T084 [US4] Add "Siguiente" button: navigate to Step 3.1 (POI) or Step 4 (Review)

**Verification** (Manual):
```
1. Upload GPX, navigate to Step 3
2. Verify map displays:
   - GPX track as red polyline
   - Map auto-centered on route
3. Verify telemetry panel shows:
   - Distancia: 42.5 km
   - Desnivel positivo: 1250 m
   - Desnivel negativo: 1100 m
   - Altitud máxima: 1850 m
   - Altitud mínima: 450 m
4. Test map interaction:
   - Zoom in/out → Track remains visible
   - Pan → Track stays in view
5. Click "Siguiente" → Navigate to Step 3.1 (POI) or Step 4 (Review)
```

**Acceptance Criteria**:
- [x] Map renders GPX track as polyline (AS4.1)
- [x] Telemetry panel shows all metrics (AS4.2)
- [x] Map is interactive (zoom, pan) (AS4.3)
- [x] "Siguiente" advances to next step (AS4.4)

---

## Phase 8: US5 - POI Management (Priority P5)

**User Story**: Como ciclista que quiere compartir lugares destacados de mi ruta, quiero poder marcar hasta 6 puntos de interés en el mapa

**Goal**: Implement POI management with map click, descriptions, and photo upload

**Duration**: 5 hours

**Independent Test**: Click map to add POI, verify POI form opens, add description, verify max 6 POI limit enforced

### Backend Tests

- [ ] T085 [US5] Write unit tests for POI batch creation in backend/tests/unit/test_poi_service.py
- [ ] T086 [US5] Verify MAX_POIS_PER_TRIP = 6 enforced in poi_service.py

### Frontend Components (TDD)

#### Step 3.1: POI Management Component

- [ ] T087 [US5] Write tests for Step3POIs in frontend/tests/unit/Step3POIs.test.tsx
- [ ] T088 [US5] Create Step3POIs component in frontend/src/components/trips/GPXWizard/Step3POIs.tsx
- [ ] T089 [US5] Add "Añadir POI" button with counter ("X / 6 POIs añadidos")

#### Map Click Handler

- [ ] T090 [US5] Implement handleMapClick() in Step3POIs: open POIForm modal with coordinates
- [ ] T091 [US5] Add POI markers to map (blue pins) with sequence numbers (1-6)
- [ ] T092 [US5] Disable "Añadir POI" button after 6 POIs, show toast: "Máximo 6 POIs por viaje"

#### POI Form Integration

- [ ] T093 [US5] Integrate existing POIForm component (reuse from Feature 003) in Step3POIs
- [ ] T094 [US5] Add POI state management: add, edit, delete POI in wizard state

**Verification** (Manual):
```
1. Navigate to Step 3.1 (POI Management)
2. Click "Añadir POI" → Cursor changes to crosshair
3. Click map at 3 different locations
4. For each POI:
   - POIForm modal opens with coordinates
   - Enter name: "Refugio"
   - Enter description (optional, max 500 chars)
   - Click "Guardar POI"
5. Verify:
   - POI markers appear on map (blue pins)
   - Counter: "3 / 6 POIs añadidos"
6. Add 3 more POIs → Counter: "6 / 6"
7. Try to add 7th POI:
   - "Añadir POI" button disabled
   - Toast: "Máximo 6 POIs por viaje"
8. Click existing POI → Edit form opens
9. Delete POI → Marker removed, counter: "5 / 6"
10. Click "Siguiente" → Navigate to Step 4 (Review)
```

**Acceptance Criteria**:
- [x] "Añadir POI" enables map click mode (AS5.1)
- [x] Click POI marker opens edit panel (AS5.2)
- [x] Max 6 POIs enforced (AS5.3)
- [x] Delete POI removes marker (AS5.4)
- [x] "Siguiente" advances to Review (AS5.5)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Finalize wizard with error handling, loading states, accessibility, and performance optimizations

**Duration**: 3 hours

### Error Handling

- [ ] T095 [P] Add global error boundary in GPXWizard component (catch React errors)
- [ ] T096 [P] Add retry logic for failed API calls (POST /gpx/analyze, POST /trips/gpx-wizard)

### Loading States

- [ ] T097 [P] Add loading spinners: GPX upload, telemetry extraction, trip publish
- [ ] T098 [P] Add skeleton screens for Step 1 (while analyzing GPX)

### Accessibility

- [ ] T099 Add ARIA labels to all wizard steps, buttons, form fields
- [ ] T100 Add keyboard navigation: Tab, Enter (next), ESC (close modal/wizard)

### Performance

- [ ] T101 [P] Test GPX processing performance: 10MB file should extract telemetry <2s (SC-002)
- [ ] T102 [P] Test wizard completion time: full flow should take <5min (SC-001)

**Verification**:
```bash
# Performance test
cd backend
time curl -X POST http://localhost:8000/gpx/analyze \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@tests/fixtures/large-route.gpx"
# Expected: <2s

# Accessibility test
cd frontend
npm run test -- --coverage
# Coverage: ≥90%

# Full wizard manual test
# Time yourself completing Steps 1-4
# Target: <5min total
```

---

## Parallel Execution Examples

### Backend Parallel Tasks (Can Run Simultaneously)

**Phase 2 - Foundational**:
```bash
# Terminal 1: Difficulty Calculator
cd backend/tests/unit && vim test_difficulty_calculator.py  # T009
cd backend/src/services && vim difficulty_calculator.py     # T010

# Terminal 2: GPX Service Extension
cd backend/tests/unit && vim test_gpx_service.py            # T012
cd backend/src/services && vim gpx_service.py               # T013

# Terminal 3: Pydantic Schemas
cd backend/src/schemas && vim gpx_wizard.py                 # T015-T017
```

**Phase 4 - US2 (GPX Upload)**:
```bash
# Terminal 1: Integration Tests
cd backend/tests/integration && vim test_gpx_wizard_api.py  # T031

# Terminal 2: Contract Tests
cd backend/tests/contract && vim test_gpx_wizard_contracts.py  # T035
```

### Frontend Parallel Tasks (Can Run Simultaneously)

**Phase 3 - US1 (Mode Selection)**:
```bash
# Terminal 1: Mode Selection Page
cd frontend/tests/unit && vim TripCreateModePage.test.tsx   # T021
cd frontend/src/pages && vim TripCreateModePage.tsx         # T022

# Terminal 2: Reusable Components
cd frontend/src/components/trips && vim ModeCard.tsx        # T027
cd frontend/src/components/icons && vim index.ts            # T028
```

**Phase 4 - US2 (GPX Upload)**:
```bash
# Terminal 1: Upload Component
cd frontend/tests/unit && vim GPXWizardUploader.test.tsx    # T037
cd frontend/src/components/trips/GPXWizard && vim GPXWizardUploader.tsx  # T038

# Terminal 2: Hooks & Services
cd frontend/src/hooks && vim useGPXAnalysis.ts              # T046
cd frontend/src/services && vim gpxWizardService.ts         # T047
cd frontend/src/hooks && vim useGPXWizard.ts                # T048
```

### Full-Stack Parallel Opportunities

**Phase 5 - US3 (Trip Details)**:
- **Backend** (T049-T050): Difficulty schema tests
- **Frontend** (T051-T062): Step2Details component + DifficultyBadge

**Phase 9 - Polish**:
- **Backend** (T101): Performance tests
- **Frontend** (T095-T100): Error handling, loading states, accessibility

---

## Task Completion Checklist

Before marking a task as complete, verify:

- [ ] **Tests pass**: Unit/integration/contract tests all green
- [ ] **Code quality**: Black formatted (backend), ESLint passed (frontend)
- [ ] **Type safety**: Mypy passed (backend), TypeScript strict mode (frontend)
- [ ] **Coverage**: ≥90% for new code (backend + frontend)
- [ ] **Manual test**: Acceptance criteria verified
- [ ] **Documentation**: Docstrings added (backend), JSDoc comments (frontend)
- [ ] **Commit**: Conventional commit message ("feat(wizard): add GPX upload step")

**Example Workflow** (TDD):
```bash
# Task T009: Write difficulty calculator tests
cd backend/tests/unit
vim test_difficulty_calculator.py  # Write 12 test cases
poetry run pytest test_difficulty_calculator.py  # FAILS (RED)

# Task T010: Implement difficulty calculator
cd backend/src/services
vim difficulty_calculator.py  # Implement calculate() method
poetry run pytest ../tests/unit/test_difficulty_calculator.py  # PASSES (GREEN)

# Task T011: Refactor
vim difficulty_calculator.py  # Clean up, add docstrings
poetry run pytest ../tests/unit/test_difficulty_calculator.py  # STILL PASSES

# Commit
git add .
git commit -m "feat(wizard): implement difficulty calculator with 5 thresholds"
```

---

## Success Criteria Validation

After completing all tasks, verify spec.md success criteria:

- [ ] **SC-001**: Wizard completion <5min (manual test with timer)
- [ ] **SC-002**: GPX processing <30s for 10MB files (backend performance test)
- [ ] **SC-003**: Difficulty calculation 80% accuracy (validate with 50 real routes)
- [ ] **SC-004**: Map renders 100km tracks fluently (frontend performance test)
- [ ] **SC-005**: GPX upload 90% first-attempt success (error handling tests)
- [ ] **SC-006**: 60% users add ≥1 POI (analytics after launch, not testable pre-launch)
- [ ] **SC-007**: Wizard abandonment <25% (analytics after launch)
- [ ] **SC-008**: User satisfaction ≥4/5 (user testing after launch)
- [ ] **SC-009**: Trip detail page <3s load (frontend performance test)

---

## Implementation Strategy

### MVP First (Week 1): US1 + US2 + US3 + US6

**Goal**: Complete end-to-end wizard flow (mode selection → GPX upload → details → publish)

**Tasks**: T001-T076 (48 tasks, ~23 hours)

**Deliverable**: Users can create trips via GPX wizard, published trips show on detail page

**Verification**:
```
1. Navigate to /trips/new
2. Select "Crear Viaje con GPS"
3. Upload test-route.gpx
4. Fill trip details
5. Skip map visualization (Step 3)
6. Skip POI management (Step 3.1)
7. Click "Publicar"
8. Verify trip created with GPX linked
```

### Enhancements (Week 2): US4 + US5 + Polish

**Goal**: Add map visualization, POI management, and polish

**Tasks**: T077-T102 (25 tasks, ~12 hours)

**Deliverable**: Full-featured wizard with map preview and POI enrichment

**Verification**:
```
1. Complete MVP flow
2. Add map visualization (Step 3)
3. Add 3 POIs (Step 3.1)
4. Verify all features work end-to-end
```

---

## Final Verification Steps

Before merging to `develop`:

1. **Run all tests**:
   ```bash
   # Backend
   cd backend
   poetry run pytest --cov=src --cov-report=html
   poetry run black src/ tests/
   poetry run ruff check src/ tests/
   poetry run mypy src/

   # Frontend
   cd frontend
   npm run test -- --coverage
   npm run lint
   npm run type-check
   npm run build:prod  # Verify production build passes
   ```

2. **Manual testing** (follow quickstart.md test cases):
   - Test Case 1: GPX Upload (Happy Path)
   - Test Case 2: GPX Without Elevation Data
   - Test Case 3: Edge Cases (7th POI, file too large, cancel wizard)

3. **Performance validation**:
   - SC-001: Complete wizard in <5min (manual timer)
   - SC-002: Upload 10MB GPX, verify telemetry <2s

4. **Accessibility audit**:
   - Use screen reader (NVDA/JAWS) to navigate wizard
   - Verify keyboard navigation (Tab, Enter, ESC)

5. **Cross-browser testing**:
   - Chrome, Firefox, Safari (desktop)
   - Chrome, Safari (mobile)

6. **Create PR**:
   - Title: "feat(wizard): GPS Trip Creation Wizard (US1-US6)"
   - Description: Link to spec.md, plan.md, test coverage report
   - Screenshots: Mode selection, GPX upload, map visualization, published trip

---

**Date**: 2026-01-28
**Feature**: 017-gps-trip-wizard
**Branch**: `017-gps-trip-wizard`
**Status**: Ready for implementation
**Estimated Time**: 43 hours (~5-6 days with TDD workflow)
