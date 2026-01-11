# Tasks: GPS Coordinates for Trip Locations

**Input**: Design documents from `/specs/009-gps-coordinates/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: This feature follows TDD (Test-Driven Development) as per ContraVento Constitution. All test tasks MUST be completed before implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend tests: `backend/tests/unit/`, `backend/tests/integration/`, `backend/tests/contract/`
- Frontend tests: `frontend/tests/unit/`, `frontend/tests/integration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

**Note**: Feature branch `009-gps-coordinates` already created, no migration needed (TripLocation columns already exist)

- [x] T001 Verify backend dependencies include Pydantic validators in backend/pyproject.toml
- [x] T002 [P] Verify frontend dependencies include Zod validation in frontend/package.json
- [x] T003 [P] Verify react-leaflet and Leaflet.js installed in frontend/package.json (already exists per plan)

**Checkpoint**: Dependencies verified, ready for foundational work

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schema and validation infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundational Tasks

- [x] T004 Update LocationInput schema to include latitude/longitude fields in backend/src/schemas/trip.py
- [x] T005 Add Pydantic Field validators for coordinate ranges in backend/src/schemas/trip.py
- [x] T006 Add custom @field_validator for decimal precision (6 places) in backend/src/schemas/trip.py
- [x] T007 Add custom @field_validator for Spanish error messages in backend/src/schemas/trip.py
- [x] T008 Update TripService._process_locations() to store coordinates in backend/src/services/trip_service.py

### Frontend Foundational Tasks

- [x] T009 [P] Update LocationInput interface to include latitude/longitude in frontend/src/types/trip.ts
- [x] T010 [P] Add locationInputSchema Zod validation in frontend/src/utils/tripValidators.ts
- [x] T011 [P] Update tripHelpers.ts to include coordinates in form payload in frontend/src/utils/tripHelpers.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Trip Route on Map (Priority: P1) 🎯 MVP

**Goal**: Enable cyclists to see the geographical route of their trips visualized on an interactive map with markers showing each location they visited during their journey.

**Independent Test**: Create a trip with 3 locations that have GPS coordinates, view trip detail page, verify map displays with 3 markers at correct locations and route line connecting them in sequence order.

**Why MVP**: This is the core value proposition - without map visualization, GPS coordinates have no user-facing benefit. Delivers immediate value by transforming text-based location lists into visual geographic context.

### Tests for User Story 1 (TDD - Write Tests FIRST)

**⚠️ CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation

#### Backend Tests

- [ ] T012 [P] [US1] Write unit test for coordinate validation (valid ranges) in backend/tests/unit/test_coordinate_validation.py
- [ ] T013 [P] [US1] Write unit test for coordinate validation (out of range rejection) in backend/tests/unit/test_coordinate_validation.py
- [ ] T014 [P] [US1] Write unit test for coordinate precision rounding (6 decimals) in backend/tests/unit/test_coordinate_validation.py
- [ ] T015 [P] [US1] Write unit test for nullable coordinates (backwards compatibility) in backend/tests/unit/test_coordinate_validation.py
- [ ] T016 [P] [US1] Write integration test for trip creation with coordinates in backend/tests/integration/test_trips_api.py
- [ ] T017 [P] [US1] Write integration test for trip retrieval with coordinates in backend/tests/integration/test_trips_api.py
- [ ] T018 [P] [US1] Write contract test for POST /trips with coordinates in backend/tests/contract/test_trips_openapi.py
- [ ] T019 [P] [US1] Write contract test for GET /trips/{trip_id} response schema in backend/tests/contract/test_trips_openapi.py

#### Frontend Tests

- [ ] T020 [P] [US1] Write unit test for TripMap filtering null coordinates in frontend/tests/unit/TripMap.test.tsx
- [ ] T021 [P] [US1] Write unit test for TripMap rendering markers in frontend/tests/unit/TripMap.test.tsx
- [ ] T022 [P] [US1] Write unit test for TripMap polyline rendering in frontend/tests/unit/TripMap.test.tsx
- [ ] T023 [P] [US1] Write unit test for TripMap zoom calculation in frontend/tests/unit/TripMap.test.tsx

**Checkpoint**: All tests written and FAILING (Red phase of TDD)

### Implementation for User Story 1

**Note**: TripMap component already exists and handles coordinate display (no changes needed per plan.md)

#### Backend Implementation

- [ ] T024 [US1] Run backend unit tests to verify they fail (pytest backend/tests/unit/test_coordinate_validation.py)
- [ ] T025 [US1] Implement coordinate range validation in LocationInput schema (backend/src/schemas/trip.py)
- [ ] T026 [US1] Implement decimal precision validator in LocationInput schema (backend/src/schemas/trip.py)
- [ ] T027 [US1] Implement Spanish error messages in LocationInput validators (backend/src/schemas/trip.py)
- [ ] T028 [US1] Update TripService._process_locations to store latitude/longitude (backend/src/services/trip_service.py)
- [ ] T029 [US1] Run backend unit tests to verify they pass (pytest backend/tests/unit/test_coordinate_validation.py --cov)
- [ ] T030 [US1] Run backend integration tests to verify they pass (pytest backend/tests/integration/test_trips_api.py --cov)
- [ ] T031 [US1] Run backend contract tests to verify they pass (pytest backend/tests/contract/test_trips_openapi.py)
- [ ] T032 [US1] Verify backend test coverage ≥90% for modified files (pytest --cov-report=term)

#### Frontend Implementation (Verification Only - No Changes Needed)

- [ ] T033 [US1] Run frontend TripMap tests to verify existing component works (npm test TripMap.test.tsx)
- [ ] T034 [US1] Verify TripMap handles null coordinates gracefully (line 43-45 in TripMap.tsx)
- [ ] T035 [US1] Verify TripMap renders markers and polylines correctly (visual inspection)

**Checkpoint**: At this point, User Story 1 backend is fully functional. TripMap already works - trips with coordinates will automatically display on map when coordinates are provided from backend.

**Manual Test for US1**:
1. Use API to create trip with coordinates: `POST /trips` with locations containing latitude/longitude
2. Retrieve trip: `GET /trips/{trip_id}` → verify coordinates in response
3. View trip detail page in frontend → verify map displays with markers and route line
4. Test with 1 location (single marker, no route line)
5. Test with 3 locations (3 markers, route line connecting them in sequence)
6. Test mixed locations (some with coordinates, some without) → verify only locations with coordinates show on map

---

## Phase 4: User Story 2 - Add GPS Coordinates When Creating Trips (Priority: P2)

**Goal**: Enable cyclists to add GPS coordinates (latitude/longitude) to trip locations during trip creation so their routes can be visualized on maps.

**Independent Test**: Create a new trip, add 3 locations with GPS coordinates through the trip creation form, save the trip, verify coordinates are stored correctly and map displays on trip detail page.

**Why P2**: This enables data input for the visualization feature (US1). While important, it's P2 because trips can still be created without coordinates (backwards compatible), and coordinates can be added later via editing (US3).

### Tests for User Story 2 (TDD - Write Tests FIRST)

**⚠️ CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation

#### Frontend Tests

- [ ] T036 [P] [US2] Write unit test for LocationInput component rendering in frontend/tests/unit/LocationInput.test.tsx
- [ ] T037 [P] [US2] Write unit test for LocationInput coordinate validation in frontend/tests/unit/LocationInput.test.tsx
- [ ] T038 [P] [US2] Write unit test for LocationInput onChange handlers in frontend/tests/unit/LocationInput.test.tsx
- [ ] T039 [P] [US2] Write unit test for coordinate validators (Zod schema) in frontend/tests/unit/tripValidators.test.ts
- [ ] T040 [P] [US2] Write integration test for trip creation form with coordinates in frontend/tests/integration/TripForm.test.tsx
- [ ] T041 [P] [US2] Write integration test for form submission with coordinates in frontend/tests/integration/TripForm.test.tsx

**Checkpoint**: All tests written and FAILING (Red phase of TDD)

### Implementation for User Story 2

#### Frontend Implementation

- [ ] T042 [US2] Run frontend unit tests to verify they fail (npm test LocationInput.test.tsx)
- [ ] T043 [US2] Create LocationInput component with coordinate fields in frontend/src/components/trips/TripForm/LocationInput.tsx
- [ ] T044 [US2] Create LocationInput.css with styling in frontend/src/components/trips/TripForm/LocationInput.css
- [ ] T045 [US2] Update Step1BasicInfo to include location input section in frontend/src/components/trips/TripForm/Step1BasicInfo.tsx
- [ ] T046 [US2] Add location state management (useState) in Step1BasicInfo in frontend/src/components/trips/TripForm/Step1BasicInfo.tsx
- [ ] T047 [US2] Implement handleLocationChange handler in Step1BasicInfo in frontend/src/components/trips/TripForm/Step1BasicInfo.tsx
- [ ] T048 [US2] Implement handleAddLocation handler in Step1BasicInfo in frontend/src/components/trips/TripForm/Step1BasicInfo.tsx
- [ ] T049 [US2] Implement handleRemoveLocation handler in Step1BasicInfo in frontend/src/components/trips/TripForm/Step1BasicInfo.tsx
- [ ] T050 [US2] Update Step4Review to display coordinates in review in frontend/src/components/trips/TripForm/Step4Review.tsx
- [ ] T051 [US2] Update tripHelpers.ts formDataToApiPayload to include locations in frontend/src/utils/tripHelpers.ts
- [ ] T052 [US2] Run frontend unit tests to verify they pass (npm test LocationInput.test.tsx)
- [ ] T053 [US2] Run frontend integration tests to verify they pass (npm test TripForm.test.tsx)
- [ ] T054 [US2] Verify frontend test coverage ≥90% for new components (npm test -- --coverage)

**Checkpoint**: At this point, User Story 2 is fully functional. Users can create trips with GPS coordinates through the trip creation form.

**Manual Test for US2**:
1. Navigate to `/trips/create`
2. Fill trip details (title, dates, distance, difficulty)
3. Click "Añadir Ubicación"
4. Enter location name: "Jaca"
5. Enter latitude: `42.570084` (valid)
6. Enter longitude: `-0.549941` (valid)
7. Add second location: "Somport" (lat: `42.791667`, lng: `-0.526944`)
8. Review step shows coordinates
9. Submit form → trip created
10. View trip detail page → map displays with 2 markers and route line
11. Test validation: Enter latitude `100` (invalid) → error message: "Latitud debe estar entre -90 y 90 grados"
12. Test optional coordinates: Create trip with location name only (no coordinates) → trip saved successfully, no map shown

---

## Phase 5: User Story 3 - Edit GPS Coordinates for Existing Trips (Priority: P3)

**Goal**: Enable cyclists to add or update GPS coordinates for locations in their existing trips so they can visualize routes for trips created before this feature existed.

**Independent Test**: Open an existing trip for editing, add/update GPS coordinates for its locations, save changes, verify map displays correctly with new coordinates on trip detail page.

**Why P3**: This is primarily for backfilling data on old trips. New trips will use US2 functionality. Still valuable for making historical trip data map-compatible.

### Tests for User Story 3 (TDD - Write Tests FIRST)

**⚠️ CRITICAL**: Write these tests FIRST, ensure they FAIL before implementation

#### Backend Tests

- [ ] T055 [P] [US3] Write integration test for PUT /trips/{trip_id} with coordinate updates in backend/tests/integration/test_trips_api.py
- [ ] T056 [P] [US3] Write contract test for PUT /trips/{trip_id} request schema in backend/tests/contract/test_trips_openapi.py

#### Frontend Tests

- [ ] T057 [P] [US3] Write integration test for trip edit form with coordinate updates in frontend/tests/integration/TripForm.test.tsx
- [ ] T058 [P] [US3] Write integration test for removing coordinates from locations in frontend/tests/integration/TripForm.test.tsx

**Checkpoint**: All tests written and FAILING (Red phase of TDD)

### Implementation for User Story 3

**Note**: Most implementation already complete from US2 (LocationInput component reused for editing)

#### Frontend Implementation

- [ ] T059 [US3] Run frontend integration tests to verify they fail (npm test TripForm.test.tsx)
- [ ] T060 [US3] Update TripEditPage to load existing coordinates into form in frontend/src/pages/TripEditPage.tsx
- [ ] T061 [US3] Ensure LocationInput component supports editing mode (pre-filled values) in frontend/src/components/trips/TripForm/LocationInput.tsx
- [ ] T062 [US3] Update tripHelpers.ts to include coordinates in update payload in frontend/src/utils/tripHelpers.ts
- [ ] T063 [US3] Run backend integration tests to verify they pass (pytest backend/tests/integration/test_trips_api.py)
- [ ] T064 [US3] Run frontend integration tests to verify they pass (npm test TripForm.test.tsx)

**Checkpoint**: At this point, User Story 3 is fully functional. Users can edit existing trips to add/update/remove GPS coordinates.

**Manual Test for US3**:
1. Open existing trip for editing: `/trips/{trip_id}/edit`
2. Existing locations load in form (with or without coordinates)
3. Add coordinates to location that had none: Enter lat/lng
4. Update existing coordinates: Change values
5. Remove coordinates: Clear lat/lng fields
6. Save trip → updates persisted
7. View trip detail page → map updates to reflect new coordinate positions
8. Test removing all coordinates → map section no longer displays (backwards compatible)

---

## Phase 6: Map Error Handling (Cross-Cutting - Affects US1)

**Goal**: Implement graceful degradation when map fails to load due to network issues or tile server unavailability.

**Related Requirement**: FR-015 - System MUST display user-friendly error message with "Retry" button when map fails to load, and show location data in text format as fallback.

### Tests for Map Error Handling (TDD - Write Tests FIRST)

- [ ] T065 [P] Write unit test for TripMap error state rendering in frontend/tests/unit/TripMap.test.tsx
- [ ] T066 [P] Write unit test for TripMap retry button functionality in frontend/tests/unit/TripMap.test.tsx
- [ ] T067 [P] Write unit test for TripMap fallback location list in frontend/tests/unit/TripMap.test.tsx

### Implementation for Map Error Handling

- [ ] T068 Run frontend unit tests to verify they fail (npm test TripMap.test.tsx)
- [ ] T069 Add error state management to TripMap component in frontend/src/components/trips/TripMap.tsx
- [ ] T070 Add error boundary or try/catch for map loading in frontend/src/components/trips/TripMap.tsx
- [ ] T071 Implement error message UI with retry button in frontend/src/components/trips/TripMap.tsx
- [ ] T072 Implement fallback location list (text format) in frontend/src/components/trips/TripMap.tsx
- [ ] T073 Add retry handler to reload map on button click in frontend/src/components/trips/TripMap.tsx
- [ ] T074 Update TripMap.css with error state styling in frontend/src/components/trips/TripMap.css
- [ ] T075 Run frontend unit tests to verify they pass (npm test TripMap.test.tsx)

**Checkpoint**: Map error handling complete - users can retry map loading and see location data even when map fails.

**Manual Test for Map Error Handling**:
1. Simulate network failure (disable internet or block OpenStreetMap tiles)
2. View trip detail page with coordinates
3. **Expected**: Error message displays: "No se pudo cargar el mapa. Verifica tu conexión a internet."
4. **Expected**: "Reintentar" button visible
5. **Expected**: Fallback location list shows below error (location names with coordinates)
6. Click "Reintentar" → map loading re-attempted
7. Restore network → map loads successfully

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, documentation, and final validation

- [ ] T076 [P] Update CLAUDE.md with GPS coordinates feature documentation in CLAUDE.md
- [ ] T077 [P] Update backend OpenAPI schema in backend/src/main.py (if auto-generated)
- [ ] T078 [P] Add coordinate input examples to API documentation in backend/docs/
- [ ] T079 [P] Run full backend test suite (pytest backend/tests/ --cov --cov-report=html)
- [ ] T080 [P] Run full frontend test suite (npm test -- --coverage --run)
- [ ] T081 [P] Verify backend coverage ≥90% (open htmlcov/index.html)
- [ ] T082 [P] Verify frontend coverage ≥90% (open coverage/index.html)
- [ ] T083 Run black formatter on backend code (cd backend && poetry run black src/ tests/)
- [ ] T084 [P] Run ruff linter on backend code (cd backend && poetry run ruff check src/ tests/)
- [ ] T085 [P] Run mypy type checker on backend code (cd backend && poetry run mypy src/)
- [ ] T086 [P] Run prettier formatter on frontend code (cd frontend && npm run format)
- [ ] T087 [P] Run eslint on frontend code (cd frontend && npm run lint)
- [ ] T088 Manual test all three user stories end-to-end (follow quickstart.md test scenarios)
- [ ] T089 Verify backwards compatibility (create trip without coordinates → no map shown, no errors)
- [ ] T090 Verify edge cases (mixed coordinates, out of range, decimal precision)
- [ ] T091 Take screenshots for PR (trip creation form, map display, coordinate validation errors)
- [ ] T092 Update feature status in spec.md (mark as implemented)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational → INDEPENDENT
  - User Story 2 (P2): Can start after Foundational → INDEPENDENT (reuses US1 backend)
  - User Story 3 (P3): Can start after Foundational → Depends on US2 (reuses LocationInput component)
- **Map Error Handling (Phase 6)**: Depends on US1 completion (affects TripMap component)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: ✅ INDEPENDENT - Can start after Foundational (Phase 2)
  - Backend validation ready
  - TripMap component already exists (no changes needed)
  - Can test immediately after backend implementation

- **User Story 2 (P2)**: ⚠️ Reuses US1 Backend - Can start after Foundational (Phase 2)
  - Uses same LocationInput schema from US1
  - Adds frontend coordinate input (LocationInput component)
  - INDEPENDENT from US1 frontend (different components)
  - Can test trip creation without needing US1 map visualization

- **User Story 3 (P3)**: ⚠️ Depends on US2 Frontend - Can start after US2 completion
  - Reuses LocationInput component from US2
  - Adds editing workflow (load existing coordinates into form)
  - DEPENDENT on US2 component implementation

### Within Each User Story

- **Tests BEFORE Implementation**: TDD workflow strictly enforced
- **Unit tests before integration tests**: Test smaller units first
- **Backend before frontend** (for US1): Validation must exist before frontend can test
- **Frontend component before integration** (for US2/US3): LocationInput before form integration
- **Story complete before moving to next priority**: Validate US1 independently before US2

### Parallel Opportunities

#### Setup Phase (Phase 1)
- T002, T003 can run in parallel (different package files)

#### Foundational Phase (Phase 2)
- Backend tasks (T004-T008) sequential (same file: trip.py, trip_service.py)
- Frontend tasks (T009-T011) can run in parallel (different files: trip.ts, tripValidators.ts, tripHelpers.ts)

#### User Story 1 Tests (Phase 3)
- Backend unit tests (T012-T015) can run in parallel (same file, different test functions)
- Backend integration/contract tests (T016-T019) can run in parallel (different test files)
- Frontend unit tests (T020-T023) can run in parallel (different test functions)

#### User Story 1 Implementation (Phase 3)
- T024-T032 sequential (TDD workflow: run test → implement → run test)
- T033-T035 can run in parallel (verification only, no code changes)

#### User Story 2 Tests (Phase 4)
- All test tasks (T036-T041) can run in parallel (different test files)

#### User Story 2 Implementation (Phase 4)
- T043-T044 can run in parallel (component + CSS)
- T045-T051 sequential (form integration depends on component existing)

#### User Story 3 Tests (Phase 5)
- All test tasks (T055-T058) can run in parallel (different test files)

#### Map Error Handling Tests (Phase 6)
- All test tasks (T065-T067) can run in parallel (different test functions)

#### Polish Phase (Phase 7)
- Most tasks marked [P] can run in parallel (different files, independent validation)

---

## Parallel Example: User Story 2

```bash
# Phase 1: Write all tests in parallel (TDD - Red phase)
Task: "Write unit test for LocationInput component rendering in frontend/tests/unit/LocationInput.test.tsx"
Task: "Write unit test for LocationInput coordinate validation in frontend/tests/unit/LocationInput.test.tsx"
Task: "Write unit test for LocationInput onChange handlers in frontend/tests/unit/LocationInput.test.tsx"
Task: "Write unit test for coordinate validators (Zod schema) in frontend/tests/unit/tripValidators.test.ts"
Task: "Write integration test for trip creation form with coordinates in frontend/tests/integration/TripForm.test.tsx"
Task: "Write integration test for form submission with coordinates in frontend/tests/integration/TripForm.test.tsx"

# Phase 2: Run tests (all fail) → then implement sequentially → run tests (all pass)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Complete Phase 1: Setup (verify dependencies)
2. ✅ Complete Phase 2: Foundational (schema + validation infrastructure)
3. ✅ Complete Phase 3: User Story 1 (backend validation + map display)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Create trip with coordinates via API
   - Verify map displays with markers and route line
   - Test backwards compatibility (trip without coordinates)
5. Deploy/demo if ready

**MVP Value**: Cyclists can see trip routes on interactive maps when coordinates are provided (via API or manual entry). This is the core value - visual representation of cycling journeys.

### Incremental Delivery (Recommended)

1. **Foundation** (Setup + Foundational) → Schema and validation ready
2. **MVP** (User Story 1) → Test independently → Deploy/Demo
   - Value: Map visualization works (coordinates entered via API)
3. **Enhancement 1** (User Story 2) → Test independently → Deploy/Demo
   - Value: Users can add coordinates during trip creation (frontend input)
4. **Enhancement 2** (User Story 3) → Test independently → Deploy/Demo
   - Value: Users can backfill coordinates for historical trips
5. **Robustness** (Map Error Handling) → Test independently → Deploy/Demo
   - Value: Graceful degradation when map fails to load

Each phase adds incremental value without breaking previous functionality.

### Parallel Team Strategy

With 2-3 developers:

1. **Team** completes Setup + Foundational together (critical path)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (backend validation + tests)
   - **Developer B**: User Story 2 (LocationInput component + tests)
   - **Developer C**: User Story 3 (editing workflow + tests)
3. Stories complete and integrate independently
4. **Note**: US3 must wait for US2 component (LocationInput) to complete

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD enforced**: Verify tests fail before implementing, verify tests pass after implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Coverage requirement**: ≥90% for all modified files (constitution requirement)
- **No database migration needed**: TripLocation columns already exist
- **Backwards compatibility**: Trips without coordinates continue to work (coordinates nullable)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Summary

- **Total Tasks**: 92
- **Setup**: 3 tasks
- **Foundational**: 8 tasks (BLOCKS all user stories)
- **User Story 1 (P1)**: 21 tasks (8 tests + 13 implementation)
- **User Story 2 (P2)**: 19 tasks (6 tests + 13 implementation)
- **User Story 3 (P3)**: 10 tasks (4 tests + 6 implementation)
- **Map Error Handling**: 11 tasks (3 tests + 8 implementation)
- **Polish**: 17 tasks
- **Parallel Opportunities**: 42 tasks marked [P] (45% parallelizable)
- **Independent Test Criteria**: Defined for each user story
- **Suggested MVP Scope**: User Story 1 only (map visualization)
- **Format Validation**: ✅ All tasks follow checklist format (checkbox, ID, labels, file paths)

**Estimated Effort**:
- MVP (US1 only): ~8-10 hours (setup + foundational + US1)
- Full Feature (US1-US3 + Error Handling): ~20-25 hours
- With Polish: ~25-30 hours

**Ready for Implementation**: Tasks are specific, testable, and executable. Follow TDD workflow strictly (tests first, then implementation).
