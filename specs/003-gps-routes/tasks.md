# Tasks: GPS Routes Interactive

**Feature Branch**: `003-gps-routes`
**Input**: Design documents from `/specs/003-gps-routes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Tests**: Test tasks are included based on TDD requirements in CLAUDE.md (≥90% coverage mandatory).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Create branch `003-gps-routes` from `develop`
- [X] T002 Install backend dependencies: `gpxpy@^1.6.2` and `rdp@^0.8` via poetry (see [research.md:11-31](research.md#L11-L31))
- [X] T003 [P] Install frontend dependency: `recharts@^2.10.0` via npm (see [research.md:178-211](research.md#L178-L211))
- [X] T004 [P] Create GPX test fixtures directory `backend/tests/fixtures/gpx/`
- [X] T005 [P] Add sample GPX files to fixtures: `short_route.gpx` (50KB), `camino_del_cid.gpx` (500KB), `long_route_5mb.gpx` (5MB), `no_elevation.gpx`, `invalid_gpx.xml` (see [plan.md:376-383](plan.md#L376-L383))

**Checkpoint**: Dependencies installed, test fixtures ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema and core models that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema

- [X] T006 Create Alembic migration script `backend/migrations/versions/xxx_create_gpx_tables.py` with dual-database DDL (see [data-model.md:428-520](data-model.md#L428-L520))
- [X] T007 Apply migration to create `gpx_files` and `track_points` tables: `poetry run alembic upgrade head`
- [X] T008 Verify tables exist in database with correct schema (indexes, foreign keys, constraints)

### Core Models

- [X] T009 [P] Create `backend/src/models/gpx.py` with GPXFile model (see [data-model.md:333-384](data-model.md#L333-L384), [quickstart.md:132-168](quickstart.md#L132-L168))
- [X] T010 [P] Add TrackPoint model to `backend/src/models/gpx.py` (see [data-model.md:387-408](data-model.md#L387-L408), [quickstart.md:170-185](quickstart.md#L170-L185))
- [X] T011 Extend Trip model in `backend/src/models/trip.py` with gpx_file relationship (see [data-model.md:410-422](data-model.md#L410-L422))

### Shared Types (Frontend)

- [X] T012 [P] Create `frontend/src/types/gpx.ts` with TypeScript interfaces: GPXTrack, TrackPoint, GPXUploadResponse, GPXStatusResponse

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Subir y Procesar Archivo GPX (Priority: P1) 🎯 MVP

**Goal**: Enable cyclists to upload GPX files and automatically extract route statistics (distance, elevation, trackpoints)

**Independent Test**: Create a trip, upload a valid GPX file, verify processing completes and displays basic statistics

**Success Criteria**: FR-001 to FR-008, SC-001 to SC-006

### Tests for User Story 1 (TDD - Write First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Unit test: Parse valid GPX file in `backend/tests/unit/test_gpx_service.py::test_parse_valid_gpx` (see [quickstart.md:429-437](quickstart.md#L429-L437))
- [X] T014 [P] [US1] Unit test: Douglas-Peucker simplification reduces points 80-90% in `backend/tests/unit/test_gpx_service.py::test_simplification_reduces_points` (SC-026)
- [X] T015 [P] [US1] Unit test: Elevation calculation accuracy >90% in `backend/tests/unit/test_gpx_service.py::test_elevation_calculation_accuracy` (SC-005, see [data-model.md:175-182](data-model.md#L175-L182))
- [X] T016 [P] [US1] Unit test: Handle GPX without elevation data in `backend/tests/unit/test_gpx_service.py::test_gpx_without_elevation` (FR-021)
- [X] T017 [P] [US1] Unit test: Reject malformed GPX with clear Spanish error in `backend/tests/unit/test_gpx_service.py::test_invalid_gpx_error` (FR-007)
- [X] T018 [P] [US1] Integration test: Upload small file (<1MB) with sync processing in `backend/tests/integration/test_gpx_api.py::test_upload_small_file_sync` (SC-002, see [contracts/gpx-api.yaml:86-111](contracts/gpx-api.yaml#L86-L111))
- [X] T019 [P] [US1] Integration test: Upload large file (>1MB) with async processing in `backend/tests/integration/test_gpx_api.py::test_upload_large_file_async` (SC-003, see [contracts/gpx-api.yaml:112-128](contracts/gpx-api.yaml#L112-L128))
- [X] T020 [P] [US1] Integration test: Download original GPX file in `backend/tests/integration/test_gpx_api.py::test_download_original_gpx` (FR-039, see [contracts/gpx-api.yaml:390-431](contracts/gpx-api.yaml#L390-L431))
- [X] T021 [P] [US1] Integration test: Delete GPX file cascades deletion in `backend/tests/integration/test_gpx_api.py::test_delete_gpx_cascade` (FR-036, see [data-model.md:561-570](data-model.md#L561-L570))
- [X] T022 [P] [US1] Integration test: Validate file size ≤10MB in `backend/tests/integration/test_gpx_api.py::test_validate_file_size` (FR-001, see [contracts/gpx-api.yaml:136-142](contracts/gpx-api.yaml#L136-L142))

### Implementation for User Story 1

**Backend Services**

- [ ] T023 [US1] Implement `parse_gpx_file()` in `backend/src/services/gpx_service.py` using gpxpy library (see [quickstart.md:189-254](quickstart.md#L189-L254), [research.md:11-31](research.md#L11-L31))
- [ ] T024 [US1] Implement `simplify_track()` in `backend/src/services/gpx_service.py` using rdp library with epsilon=0.0001° (see [quickstart.md:256-298](quickstart.md#L256-L298), [research.md:116-140](research.md#L116-L140))
- [ ] T025 [US1] Implement `calculate_distance()` helper (Haversine formula) in `backend/src/services/gpx_service.py` (see [quickstart.md:301-313](quickstart.md#L301-L313))
- [ ] T026 [US1] Implement `save_gpx_to_storage()` in `backend/src/services/gpx_service.py` for filesystem storage at `storage/gpx_files/{year}/{month}/{trip_id}/original.gpx` (see [plan.md:98](plan.md#L98))
- [ ] T027 [US1] Add elevation anomaly detection (range -420m to 8850m) in `backend/src/services/gpx_service.py` (FR-034, see [data-model.md:175-179](data-model.md#L175-L179))

**Backend Schemas**

- [ ] T028 [P] [US1] Create Pydantic schemas in `backend/src/schemas/gpx.py`: GPXUploadResponse, GPXStatusResponse, GPXFileMetadata, TrackDataResponse, TrackPoint (see [contracts/gpx-api.yaml:442-733](contracts/gpx-api.yaml#L442-L733))

**Backend API**

- [ ] T029 [US1] Implement POST `/trips/{trip_id}/gpx` endpoint in `backend/src/api/trips.py` with sync/async processing logic (see [quickstart.md:316-369](quickstart.md#L316-L369), [contracts/gpx-api.yaml:37-178](contracts/gpx-api.yaml#L37-L178))
- [ ] T030 [US1] Implement GET `/gpx/{gpx_file_id}/status` endpoint for polling in `backend/src/api/trips.py` (see [contracts/gpx-api.yaml:255-318](contracts/gpx-api.yaml#L255-L318))
- [ ] T031 [US1] Implement GET `/trips/{trip_id}/gpx` endpoint for metadata in `backend/src/api/trips.py` (see [contracts/gpx-api.yaml:179-214](contracts/gpx-api.yaml#L179-L214))
- [ ] T032 [US1] Implement GET `/gpx/{gpx_file_id}/download` endpoint for original file in `backend/src/api/trips.py` (see [contracts/gpx-api.yaml:390-431](contracts/gpx-api.yaml#L390-L431))
- [ ] T033 [US1] Implement DELETE `/trips/{trip_id}/gpx` endpoint with cascade deletion in `backend/src/api/trips.py` (see [contracts/gpx-api.yaml:216-254](contracts/gpx-api.yaml#L216-L254))
- [ ] T034 [US1] Add file validation: max 10MB, .gpx extension, valid XML structure (FR-001, FR-002, FR-003)
- [ ] T035 [US1] Add Spanish error messages for all GPX validation failures (see [contracts/gpx-api.yaml:130-156](contracts/gpx-api.yaml#L130-L156))

**Frontend Services**

- [ ] T036 [P] [US1] Create `frontend/src/services/gpxService.ts` with API client methods: uploadGPX, pollGPXStatus, getGPXTrack, downloadGPX, deleteGPX

**Frontend Components**

- [ ] T037 [P] [US1] Create `frontend/src/hooks/useGPXUpload.ts` custom hook with polling logic for async uploads (see [quickstart.md:373-421](quickstart.md#L373-L421))
- [ ] T038 [US1] Create `frontend/src/components/trips/GPXUploader.tsx` with drag-drop file upload component (see [quickstart.md:373-421](quickstart.md#L373-L421))
- [ ] T039 [US1] Create `frontend/src/components/trips/GPXStats.tsx` to display distance, elevation gain/loss, max/min altitude
- [ ] T040 [US1] Integrate GPXUploader and GPXStats into `frontend/src/pages/TripDetailPage.tsx` (owner-only section)

**Frontend Tests**

- [ ] T041 [P] [US1] Unit test: GPXUploader file validation (>10MB shows error, .kml rejected) in `frontend/tests/unit/GPXUploader.test.tsx` (see [quickstart.md:426-437](quickstart.md#L426-L437))
- [ ] T042 [P] [US1] Unit test: GPXUploader loading state during upload in `frontend/tests/unit/GPXUploader.test.tsx`

**Verification**

- [ ] T043 [US1] Run all Unit tests for US1: `poetry run pytest tests/unit/test_gpx_service.py -v`
- [ ] T044 [US1] Run all Integration tests for US1: `poetry run pytest tests/integration/test_gpx_api.py -v`
- [ ] T045 [US1] Verify test coverage ≥90% for gpx_service.py: `poetry run pytest --cov=src/services/gpx_service.py --cov-report=term`
- [ ] T046 [US1] Manual test: Upload sample_route.gpx (<1MB) via frontend, verify <3s processing (SC-002)
- [ ] T047 [US1] Manual test: Upload long_route_5mb.gpx, verify async processing completes <15s (SC-003)
- [ ] T048 [US1] Manual test: Download original GPX file from trip detail page (FR-039)
- [ ] T049 [US1] Manual test: Delete GPX file, verify cascade deletion of trackpoints (FR-036)

**Checkpoint**: User Story 1 fully functional - GPX upload, processing, and basic statistics working independently

---

## Phase 4: User Story 2 - Visualización en Mapa Interactivo (Priority: P2)

**Goal**: Display GPS routes on interactive map with zoom, pan, and start/end markers

**Independent Test**: Upload a GPX file, view published trip, verify map shows route with interactive controls and markers

**Success Criteria**: FR-009 to FR-015, SC-007 to SC-011

**Dependencies**: Requires User Story 1 (GPX processing must be complete)

### Tests for User Story 2 (TDD - Write First) ⚠️

- [ ] T050 [P] [US2] Integration test: GET `/gpx/{gpx_file_id}/track` returns simplified trackpoints in `backend/tests/integration/test_gpx_api.py::test_get_track_points` (see [contracts/gpx-api.yaml:319-389](contracts/gpx-api.yaml#L319-L389))
- [ ] T051 [P] [US2] Unit test: Track simplification maintains visual accuracy <5% distortion in `backend/tests/unit/test_gpx_service.py::test_simplification_accuracy` (see [data-model.md:525-537](data-model.md#L525-L537))
- [ ] T052 [P] [US2] Performance test: Map loads with 1000 points in <3s in `frontend/tests/performance/map-render.test.tsx` (SC-007)
- [ ] T053 [P] [US2] Integration test: Map interaction (zoom, pan, click) responds <200ms in `frontend/tests/integration/TripMap.test.tsx` (SC-011)

### Implementation for User Story 2

**Backend API**

- [ ] T054 [US2] Implement GET `/gpx/{gpx_file_id}/track` endpoint to return simplified trackpoints in `backend/src/api/trips.py` (see [contracts/gpx-api.yaml:319-389](contracts/gpx-api.yaml#L319-L389))
- [ ] T055 [US2] Ensure trackpoints are returned ordered by sequence field (see [data-model.md:145-153](data-model.md#L145-L153))

**Frontend Hooks**

- [ ] T056 [P] [US2] Create `frontend/src/hooks/useGPXTrack.ts` custom hook to fetch simplified trackpoints

**Frontend Components**

- [ ] T057 [US2] Modify `frontend/src/components/trips/TripMap.tsx` to render GPX polyline using react-leaflet (see [research.md:143-175](research.md#L143-L175))
- [ ] T058 [US2] Add start marker (green) and end marker (red) to TripMap (FR-011)
- [ ] T059 [US2] Implement auto-fit bounds to show entire route on load (FR-012)
- [ ] T060 [US2] Add click handler to polyline showing tooltip with coordinates, elevation, distance (FR-013)
- [ ] T061 [US2] Add map layer selector (terrain, satellite, cycling) using Leaflet controls (FR-010)
- [ ] T062 [US2] Ensure touch gestures work on mobile (pinch zoom, drag pan) (FR-014, SC-008)

**Verification**

- [ ] T063 [US2] Run Integration test: `poetry run pytest tests/integration/test_gpx_api.py::test_get_track_points -v`
- [ ] T064 [US2] Run Performance test: `npm run test:performance -- tests/performance/map-render.test.tsx` (verify SC-007)
- [ ] T065 [US2] Manual test: Upload GPX, verify map displays route with correct start/end markers
- [ ] T066 [US2] Manual test: Test zoom in/out, pan, click on route line shows information
- [ ] T067 [US2] Manual test: Test on mobile device (iOS/Android) - touch gestures work (SC-008)
- [ ] T068 [US2] Manual test: Load route with 1000+ points, verify <3s load time (SC-007)

**Checkpoint**: User Story 2 fully functional - Interactive map visualization working independently with US1

---

## Phase 5: User Story 3 - Perfil de Elevación Interactivo (Priority: P3)

**Goal**: Display interactive elevation profile chart with sync to map on click

**Independent Test**: Upload a GPX with elevation data, view trip, verify elevation chart appears with hover tooltips and click-to-map sync

**Success Criteria**: FR-016 to FR-022, SC-012 to SC-016

**Dependencies**: Requires User Story 1 (GPX with elevation data), optionally integrates with User Story 2 (map sync)

### Tests for User Story 3 (TDD - Write First) ⚠️

- [ ] T069 [P] [US3] Unit test: Gradient calculation accuracy ±2% in `backend/tests/unit/test_gpx_service.py::test_gradient_calculation_accuracy` (SC-023)
- [ ] T070 [P] [US3] Integration test: Elevation profile loads <2s for 1000 points in `frontend/tests/performance/elevation-profile.test.tsx` (SC-013)
- [ ] T071 [P] [US3] Integration test: Profile-to-map click sync <300ms in `frontend/tests/integration/ElevationProfile.test.tsx` (SC-016)

### Implementation for User Story 3

**Backend Services**

- [ ] T072 [US3] Add gradient calculation to `simplify_track()` in `backend/src/services/gpx_service.py` (calculate % slope between consecutive points) (see [data-model.md:147](data-model.md#L147))
- [ ] T073 [US3] Update TrackPoint response schema to include gradient field in `backend/src/schemas/gpx.py` (see [contracts/gpx-api.yaml:708-713](contracts/gpx-api.yaml#L708-L713))

**Frontend Components**

- [ ] T074 [P] [US3] Create `frontend/src/components/trips/ElevationProfile.tsx` using Recharts LineChart (see [research.md:178-211](research.md#L178-L211))
- [ ] T075 [US3] Add hover tooltip showing elevation, distance, gradient to ElevationProfile
- [ ] T076 [US3] Add click handler emitting `onPointClick(point)` event to ElevationProfile (FR-019)
- [ ] T077 [US3] Add gradient color coding: green (uphill), blue (downhill) to chart (FR-020)
- [ ] T078 [US3] Make ElevationProfile responsive for mobile in CSS (FR-022)
- [ ] T079 [US3] Show "No elevation data available" message when GPX lacks elevation (FR-021)

**Frontend Hooks**

- [ ] T080 [P] [US3] Create `frontend/src/hooks/useMapProfileSync.ts` for state management between map and profile

**Frontend Integration**

- [ ] T081 [US3] Integrate ElevationProfile into `frontend/src/pages/TripDetailPage.tsx` below TripMap
- [ ] T082 [US3] Wire `onPointClick` event to center map on selected point (FR-019, SC-016)

**Verification**

- [ ] T083 [US3] Run Unit test: `poetry run pytest tests/unit/test_gpx_service.py::test_gradient_calculation_accuracy -v`
- [ ] T084 [US3] Run Performance test: `npm run test:performance -- tests/performance/elevation-profile.test.tsx` (verify SC-013)
- [ ] T085 [US3] Manual test: Upload GPX with elevation, verify chart displays correctly
- [ ] T086 [US3] Manual test: Hover over chart, verify tooltip shows elevation/distance/gradient
- [ ] T087 [US3] Manual test: Click chart point, verify map centers on that location <300ms (SC-016)
- [ ] T088 [US3] Manual test: Upload GPX without elevation, verify "No data" message (FR-021)
- [ ] T089 [US3] Manual test: View elevation profile on mobile, verify responsive layout (FR-022)

**Checkpoint**: User Story 3 fully functional - Elevation profile with map sync working independently

---

## Phase 6: User Story 4 - Puntos de Interés en la Ruta (Priority: P4)

**Goal**: Allow users to manually add Points of Interest (POI) along the route with icons and popups

**Independent Test**: Upload a GPX, add multiple POIs with different types, verify they display on map with correct icons and information popups

**Success Criteria**: FR-023 to FR-029, SC-017 to SC-020

**Dependencies**: Requires User Story 2 (interactive map must exist)

### Database Schema for User Story 4

- [ ] T090 [US4] Create Alembic migration for `points_of_interest` table in `backend/migrations/versions/xxx_create_poi_table.py` (see [data-model.md:194-253](data-model.md#L194-L253))
- [ ] T091 [US4] Apply migration: `poetry run alembic upgrade head`

### Tests for User Story 4 (TDD - Write First) ⚠️

- [ ] T092 [P] [US4] Integration test: POST `/trips/{trip_id}/poi` creates POI in `backend/tests/integration/test_poi_api.py::test_create_poi` (FR-023)
- [ ] T093 [P] [US4] Integration test: Validate max 20 POIs per trip in `backend/tests/integration/test_poi_api.py::test_max_poi_limit` (FR-029, SC-020)
- [ ] T094 [P] [US4] Integration test: GET `/trips/{trip_id}/poi` returns all POIs in `backend/tests/integration/test_poi_api.py::test_get_pois`
- [ ] T095 [P] [US4] Integration test: PUT `/trips/{trip_id}/poi/{poi_id}` updates POI in `backend/tests/integration/test_poi_api.py::test_update_poi` (FR-028)
- [ ] T096 [P] [US4] Integration test: DELETE `/trips/{trip_id}/poi/{poi_id}` removes POI in `backend/tests/integration/test_poi_api.py::test_delete_poi` (FR-028)

### Implementation for User Story 4

**Backend Models**

- [ ] T097 [P] [US4] Create PointOfInterest model in `backend/src/models/poi.py` (see [data-model.md:194-253](data-model.md#L194-L253))

**Backend Schemas**

- [ ] T098 [P] [US4] Create Pydantic schemas in `backend/src/schemas/poi.py`: POICreateInput, POIUpdateInput, POIResponse

**Backend Services**

- [ ] T099 [US4] Implement POI CRUD operations in `backend/src/services/poi_service.py`: create_poi, get_pois, update_poi, delete_poi
- [ ] T100 [US4] Add validation: max 20 POIs per trip, name 1-100 chars, description ≤500 chars (FR-029, see [data-model.md:255-262](data-model.md#L255-L262))
- [ ] T101 [US4] Calculate distance_from_start_km based on GPX track in poi_service.py

**Backend API**

- [ ] T102 [US4] Implement POST `/trips/{trip_id}/poi` endpoint in `backend/src/api/poi.py`
- [ ] T103 [US4] Implement GET `/trips/{trip_id}/poi` endpoint with optional type filter in `backend/src/api/poi.py` (FR-027)
- [ ] T104 [US4] Implement PUT `/trips/{trip_id}/poi/{poi_id}` endpoint in `backend/src/api/poi.py`
- [ ] T105 [US4] Implement DELETE `/trips/{trip_id}/poi/{poi_id}` endpoint in `backend/src/api/poi.py`
- [ ] T106 [US4] Add owner-only authorization to POI endpoints (FR-028)

**Frontend Types**

- [ ] T107 [P] [US4] Add POI interfaces to `frontend/src/types/gpx.ts`: PointOfInterest, POIType enum

**Frontend Services**

- [ ] T108 [P] [US4] Create `frontend/src/services/poiService.ts` with API client methods: createPOI, getPOIs, updatePOI, deletePOI

**Frontend Components**

- [ ] T109 [P] [US4] Create `frontend/src/components/trips/POIManager.tsx` for POI list management
- [ ] T110 [P] [US4] Create `frontend/src/components/trips/AddPOIModal.tsx` modal form component (FR-024)
- [ ] T111 [P] [US4] Create `frontend/src/components/trips/POIMarker.tsx` custom Leaflet marker component with type-specific icons (FR-025)
- [ ] T112 [US4] Modify `frontend/src/components/trips/TripMap.tsx` to render POI markers with popups (FR-026)
- [ ] T113 [US4] Add POI type filter controls to TripMap (FR-027)
- [ ] T114 [US4] Add click-to-add POI mode to TripMap (FR-023)

**Verification**

- [ ] T115 [US4] Run Integration tests: `poetry run pytest tests/integration/test_poi_api.py -v`
- [ ] T116 [US4] Manual test: Add POI by clicking map, verify form appears with lat/lon prefilled
- [ ] T117 [US4] Manual test: Create POI of each type, verify distinct icons appear (SC-019)
- [ ] T118 [US4] Manual test: Click POI marker, verify popup shows name, description, photo, distance (FR-026)
- [ ] T119 [US4] Manual test: Filter POIs by type, verify show/hide works (FR-027)
- [ ] T120 [US4] Manual test: Try to add 21st POI, verify error message (FR-029)
- [ ] T121 [US4] Manual test: Edit and delete POI, verify changes persist (FR-028)
- [ ] T122 [US4] Manual test: Add POI takes <1 minute (SC-017)

**Checkpoint**: User Story 4 fully functional - POI management working independently

---

## Phase 7: User Story 5 - Estadísticas Avanzadas y Análisis (Priority: P5)

**Goal**: Calculate and display advanced statistics (speed, time, top climbs, gradient distribution) for routes with timestamp data

**Independent Test**: Upload a GPX with timestamps, verify advanced stats display (avg/max speed, moving time, top climbs)

**Success Criteria**: FR-030 to FR-034, SC-021 to SC-024

**Dependencies**: Requires User Story 1 (GPX processing), optionally enhances User Story 3 (gradient visualization)

### Database Schema for User Story 5

- [ ] T123 [US5] Create Alembic migration for `route_statistics` table in `backend/migrations/versions/xxx_create_route_statistics.py` (see [data-model.md:265-330](data-model.md#L265-L330))
- [ ] T124 [US5] Apply migration: `poetry run alembic upgrade head`

### Tests for User Story 5 (TDD - Write First) ⚠️

- [ ] T125 [P] [US5] Unit test: Speed calculation accuracy ±5% in `backend/tests/unit/test_route_stats_service.py::test_speed_calculation_accuracy` (SC-021)
- [ ] T126 [P] [US5] Unit test: Identify top 3 climbs correctly in `backend/tests/unit/test_route_stats_service.py::test_top_climbs_detection` (SC-022, FR-031)
- [ ] T127 [P] [US5] Unit test: Gradient classification (llano, moderado, empinado) in `backend/tests/unit/test_route_stats_service.py::test_gradient_classification` (FR-032)
- [ ] T128 [P] [US5] Unit test: Handle GPX without timestamps gracefully in `backend/tests/unit/test_route_stats_service.py::test_no_timestamps` (FR-033)

### Implementation for User Story 5

**Backend Models**

- [ ] T129 [P] [US5] Create RouteStatistics model in `backend/src/models/route_statistics.py` (see [data-model.md:265-330](data-model.md#L265-L330))

**Backend Schemas**

- [ ] T130 [P] [US5] Create Pydantic schemas in `backend/src/schemas/route_statistics.py`: RouteStatisticsResponse, TopClimb

**Backend Services**

- [ ] T131 [US5] Implement `calculate_speed_metrics()` in `backend/src/services/route_stats_service.py` (avg, max speed, total/moving time) (FR-030)
- [ ] T132 [US5] Implement `detect_climbs()` in `backend/src/services/route_stats_service.py` to identify top 3 hardest climbs (FR-031)
- [ ] T133 [US5] Implement `classify_gradients()` in `backend/src/services/route_stats_service.py` (0-3%, 3-6%, 6-10%, >10%) (FR-032)
- [ ] T134 [US5] Extend `parse_gpx_file()` to create RouteStatistics record if timestamps present

**Backend API**

- [ ] T135 [US5] Add route_statistics to GPXTrackResponse schema in `backend/src/schemas/gpx.py` (optional field)
- [ ] T136 [US5] Modify GET `/gpx/{gpx_file_id}/track` to include route_statistics in response

**Frontend Components**

- [ ] T137 [P] [US5] Create `frontend/src/components/trips/AdvancedStats.tsx` to display speed, time, climbs stats
- [ ] T138 [P] [US5] Create `frontend/src/components/trips/GradientDistribution.tsx` chart showing gradient categories
- [ ] T139 [P] [US5] Create `frontend/src/components/trips/TopClimbsTable.tsx` table component listing top 3 climbs
- [ ] T140 [US5] Integrate AdvancedStats, GradientDistribution, TopClimbsTable into `frontend/src/pages/TripDetailPage.tsx`
- [ ] T141 [US5] Show "Statistics not available (no timestamps)" message when appropriate (FR-033)

**Verification**

- [ ] T142 [US5] Run Unit tests: `poetry run pytest tests/unit/test_route_stats_service.py -v`
- [ ] T143 [US5] Manual test: Upload GPX with timestamps, verify avg/max speed displayed
- [ ] T144 [US5] Manual test: Verify moving time excludes pauses >5min (FR-030)
- [ ] T145 [US5] Manual test: Verify top 3 climbs identified correctly (SC-022)
- [ ] T146 [US5] Manual test: Verify gradient distribution chart shows categories (FR-032)
- [ ] T147 [US5] Manual test: Upload GPX without timestamps, verify "not available" message (FR-033)

**Checkpoint**: User Story 5 fully functional - Advanced statistics complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T148 [P] Update CLAUDE.md with GPS Routes feature documentation (add to "Active Technologies" section)
- [ ] T149 [P] Update frontend README with Recharts usage patterns
- [ ] T150 [P] Add Spanish error messages for all edge cases (GPX corrupted, coordinates invalid, etc.)
- [ ] T151 Code review: Verify all functions have type hints and Google-style docstrings (Constitution requirement)
- [ ] T152 Code review: Verify ≥90% test coverage across all modules: `poetry run pytest --cov=src --cov-report=html --cov-report=term`
- [ ] T153 [P] Performance optimization: Add database indexes for frequent queries (see [data-model.md:540-557](data-model.md#L540-557))
- [ ] T154 [P] Security audit: Verify file upload validation prevents code injection
- [ ] T155 [P] Security audit: Verify all API endpoints enforce owner-only authorization
- [ ] T156 Run full test suite: `poetry run pytest` (backend) and `npm test` (frontend)
- [ ] T157 Run linting and formatting: `poetry run black src/ tests/` and `poetry run ruff check src/ tests/`
- [ ] T158 Validate quickstart.md guide by following it step-by-step (see [quickstart.md:495-506](quickstart.md#L495-L506))
- [ ] T159 Create pull request from `003-gps-routes` to `develop` with comprehensive description
- [ ] T160 Update project roadmap with completed Feature 003

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Requires US1 completion for GPX data
  - User Story 3 (P3): Can start after Foundational - Requires US1 completion, optionally integrates with US2
  - User Story 4 (P4): Can start after Foundational - Requires US2 completion for map
  - User Story 5 (P5): Can start after Foundational - Requires US1 completion, enhances US3
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 → US2**: US2 requires GPX trackpoints from US1
- **US1 → US3**: US3 requires GPX elevation data from US1
- **US2 → US4**: US4 requires interactive map from US2
- **US1 → US5**: US5 requires GPX timestamp data from US1
- **US3 ← US5**: US5 enhances US3 gradient visualization (optional)

### Recommended Execution Sequence

**MVP (Minimum Viable Product)**:
1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: User Story 1 (GPX Upload & Processing)
4. Phase 4: User Story 2 (Map Visualization)
5. Deploy/Demo ✅

**Full Feature**:
1. MVP (above)
2. Phase 5: User Story 3 (Elevation Profile)
3. Phase 6: User Story 4 (Points of Interest)
4. Phase 7: User Story 5 (Advanced Statistics)
5. Phase 8: Polish
6. Final Release ✅

### Parallel Opportunities

**Within Setup (Phase 1)**:
- T002 (backend deps) ∥ T003 (frontend deps) ∥ T004 (fixtures dir) ∥ T005 (sample files)

**Within Foundational (Phase 2)**:
- T009 (GPXFile model) ∥ T010 (TrackPoint model) ∥ T012 (frontend types)

**Within User Story 1 Tests**:
- T013-T022 (all unit/integration tests can run in parallel)

**Within User Story 1 Implementation**:
- T028 (schemas) ∥ T036 (frontend service) ∥ T037 (hooks) ∥ T041-T042 (frontend tests)

**Between User Stories** (if team capacity allows):
- After Foundational: US1, US2, US3, US4, US5 can be worked on by different developers in parallel
- However, US2-US5 may need to wait for US1 completion to integrate properly

**Within Polish (Phase 8)**:
- T148-T150 (docs) ∥ T153-T155 (performance/security audits)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task T013: "Unit test: Parse valid GPX file"
Task T014: "Unit test: Douglas-Peucker simplification"
Task T015: "Unit test: Elevation calculation accuracy"
Task T016: "Unit test: Handle GPX without elevation"
Task T017: "Unit test: Reject malformed GPX"
Task T018: "Integration test: Upload small file sync"
Task T019: "Integration test: Upload large file async"
Task T020: "Integration test: Download original GPX"
Task T021: "Integration test: Delete GPX cascade"
Task T022: "Integration test: Validate file size"

# Launch all backend models for US1 together (after tests written):
# (Already parallel in Foundational phase)

# Launch all schemas and frontend services together:
Task T028: "Create Pydantic schemas in backend/src/schemas/gpx.py"
Task T036: "Create gpxService.ts API client"
Task T037: "Create useGPXUpload.ts hook"
Task T041: "Unit test: GPXUploader file validation"
Task T042: "Unit test: GPXUploader loading state"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

**Why**: US1 (Upload & Process) + US2 (Map Visualization) deliver the core value proposition - cyclists can share GPS routes visually.

**Steps**:
1. Complete Phase 1: Setup (5 tasks)
2. Complete Phase 2: Foundational (7 tasks)
3. Complete Phase 3: User Story 1 (37 tasks)
4. **STOP and VALIDATE**: Test US1 independently - upload, process, view stats
5. Complete Phase 4: User Story 2 (19 tasks)
6. **STOP and VALIDATE**: Test US1+US2 together - upload GPX, view on interactive map
7. Deploy/Demo MVP ✅

**Estimated**: ~2-3 days (16 hours coding + 8 hours testing)

### Incremental Delivery

**Week 1**: MVP (US1 + US2)
- ✅ Cyclists can upload GPX files
- ✅ Routes display on interactive maps
- ✅ Basic stats (distance, elevation) shown
- **Deploy to staging for user feedback**

**Week 2**: Enhanced Experience (US3)
- ✅ Elevation profiles with interactive sync
- **Deploy update**

**Week 3**: Enrichment (US4 + US5)
- ✅ Points of interest management
- ✅ Advanced statistics for data enthusiasts
- **Final deployment**

### Parallel Team Strategy

With 3 developers:

**Phase 1-2** (Together):
- All team: Setup + Foundational (2-4 hours)

**Phase 3-7** (Parallel after Foundational):
- Developer A: User Story 1 (2 days)
- Developer B: User Story 2 (waits for US1 data, then 1.5 days)
- Developer C: User Story 3 (waits for US1 data, then 1 day)

**Phase 3-7** (Sequential alternative):
- All team: User Story 1 together (1 day)
- Developer A: User Story 2 (1 day)
- Developer B: User Story 3 (1 day)
- Developer C: User Story 4 (1 day)
- Developer A: User Story 5 (1 day)

**Phase 8** (Together):
- All team: Polish, testing, documentation (0.5 day)

---

## Notes

- **[P] marker**: Tasks can run in parallel (different files, no sequential dependencies)
- **[Story] label**: Maps task to specific user story for traceability and independent testing
- **TDD mandatory**: All tests marked "Write First" MUST be written before implementation (Constitution requirement)
- **Coverage requirement**: ≥90% test coverage across all modules (verify with T152)
- **Spanish errors**: All user-facing error messages MUST be in Spanish (Constitution requirement)
- **File references**: See cross-references to implementation details throughout (research.md, data-model.md, contracts/, quickstart.md)
- **Performance targets**: Verify all SC-### success criteria during verification tasks
- **Each user story is independently testable**: Complete checkpoint validation before moving to next priority

**Total Tasks**: 160 tasks across 8 phases
**MVP Tasks**: 68 tasks (Phases 1-4)
**Full Feature Tasks**: 160 tasks (all phases)
