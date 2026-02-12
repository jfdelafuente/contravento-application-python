# Tasks: Reverse Geocoding

**Input**: Design documents from `/specs/010-reverse-geocoding/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included per TDD constitution requirements (write tests FIRST, verify they FAIL before implementation)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Backend**: No changes (feature is frontend-only)

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Install dependencies and configure project for reverse geocoding

- [x] T001 Install lodash.debounce dependency in frontend/package.json
- [x] T002 [P] Configure TypeScript types for lodash.debounce in frontend/tsconfig.json
- [x] T003 [P] Verify react-leaflet and Leaflet.js are installed (from Feature 009)

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Create shared types, utilities, and services that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create GeocodingResponse and NominatimAddress types in frontend/src/types/geocoding.ts
- [x] T005 [P] Create LocationSelection type in frontend/src/types/geocoding.ts
- [x] T006 [P] Implement GeocodingCache class in frontend/src/utils/geocodingCache.ts
- [x] T007 [P] Implement geocodingService with reverseGeocode() in frontend/src/services/geocodingService.ts
- [x] T008 [P] Implement extractLocationName() in frontend/src/services/geocodingService.ts
- [x] T009 Implement useReverseGeocode hook in frontend/src/hooks/useReverseGeocode.ts

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Click Map to Add Location (Priority: P1) ✅ COMPLETE 🎯 MVP

**Goal**: Allow users to click on the map during trip creation/editing to automatically add a location with coordinates and geocoded place name

**Independent Test**: Open trip detail page, click "Editar ubicaciones", click anywhere on map, verify confirmation modal appears with suggested place name and coordinates, confirm location is added to trip and map updates automatically

**Status**: ✅ Fully implemented and functional in TripDetailPage

### Tests for User Story 1 ✅ UNIT TESTS COMPLETE

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T010 [P] [US1] Unit test for geocodingService.reverseGeocode() in frontend/tests/unit/geocodingService.test.ts
- [x] T011 [P] [US1] Unit test for geocodingService.extractLocationName() in frontend/tests/unit/geocodingService.test.ts
- [x] T012 [P] [US1] Unit test for GeocodingCache get/set/eviction in frontend/tests/unit/geocodingCache.test.ts
- [x] T013 [P] [US1] Unit test for useReverseGeocode hook in frontend/tests/unit/useReverseGeocode.test.ts
- [~] T014 [P] [US1] Integration test for map click → modal → location added workflow in frontend/tests/integration/TripForm.geocoding.test.tsx *(deferred indefinitely - covered by unit tests T010-T013 + manual testing)*

### Implementation for User Story 1 ✅ COMPLETE

- [x] T015 [P] [US1] Create MapClickHandler component in frontend/src/components/trips/MapClickHandler.tsx
- [x] T016 [P] [US1] Create LocationConfirmModal component in frontend/src/components/trips/LocationConfirmModal.tsx
- [x] T017 [P] [US1] Create LocationConfirmModal styles in frontend/src/components/trips/LocationConfirmModal.css
- [x] T018 [US1] Update TripMap component to accept isEditMode prop in frontend/src/components/trips/TripMap.tsx
- [x] T019 [US1] Update TripMap to accept onMapClick callback prop in frontend/src/components/trips/TripMap.tsx
- [x] T020 [US1] Add MapClickHandler to TripMap MapContainer in frontend/src/components/trips/TripMap.tsx
- [x] T021 [US1] Update TripDetailPage to add edit mode toggle button in frontend/src/pages/TripDetailPage.tsx *(modified: implemented in TripDetailPage instead of TripEditPage)*
- [x] T022 [US1] Implement handleMapClick with geocoding in TripDetailPage in frontend/src/pages/TripDetailPage.tsx *(modified: implemented in TripDetailPage instead of TripEditPage)*
- [x] T023 [US1] Add LocationConfirmModal integration in TripDetailPage in frontend/src/pages/TripDetailPage.tsx *(modified: implemented in TripDetailPage instead of TripEditPage)*
- [x] T024 [US1] Implement handleConfirmLocation to add location to trip in TripDetailPage in frontend/src/pages/TripDetailPage.tsx *(modified: implemented in TripDetailPage instead of TripEditPage)*
- [x] T025 [US1] Add loading state handling during geocoding in TripDetailPage in frontend/src/pages/TripDetailPage.tsx *(modified: implemented in TripDetailPage instead of TripEditPage)*
- [x] T026 [US1] Add error handling for geocoding failures in TripDetailPage in frontend/src/pages/TripDetailPage.tsx *(modified: implemented in TripDetailPage instead of TripEditPage)*

**Checkpoint**: ✅ User Story 1 is FULLY FUNCTIONAL - users can click map to add locations with geocoded names

**Additional Improvements Completed**:

- [x] Enhanced modal visual design (improved input visibility, gradient buttons, color-coded sections)
- [x] Added location pin icon to modal header
- [x] Implemented full API integration to save locations to backend
- [x] Real-time map update after location addition (no page reload needed)

---

## Phase 4: User Story 2 - Adjust Location by Dragging Marker (Priority: P2)

**Goal**: Allow users to fine-tune location coordinates by dragging markers on the map, with automatic reverse geocoding on drag completion

**Independent Test**: Create trip with locations, enter edit mode, drag a marker to new position, verify coordinates update and reverse geocoding suggests new place name

### Tests for User Story 2 ✅ TESTS COMPLETE

- [x] T027 [P] [US2] Unit test for marker drag event handling in frontend/tests/unit/TripMap.test.tsx
- [x] T028 [P] [US2] Integration test for marker drag → geocode → name update workflow in frontend/tests/integration/TripForm.geocoding.test.tsx

### Implementation for User Story 2 ✅ COMPLETE

- [x] T029 [US2] Update TripMap to accept onMarkerDrag callback prop in frontend/src/components/trips/TripMap.tsx
- [x] T030 [US2] Add draggable prop to Marker components (conditional on isEditMode) in frontend/src/components/trips/TripMap.tsx
- [x] T031 [US2] Implement dragend event handler in TripMap in frontend/src/components/trips/TripMap.tsx
- [x] T032 [US2] Implement handleMarkerDrag in TripDetailPage to trigger geocoding in frontend/src/pages/TripDetailPage.tsx
- [x] T033 [US2] Update location coordinates and show confirmation modal on drag in frontend/src/pages/TripDetailPage.tsx
- [x] T034 [US2] Add visual feedback (cursor change) for draggable markers in edit mode in frontend/src/components/trips/TripMap.css

**Checkpoint**: ✅ User Stories 1 AND 2 are FULLY FUNCTIONAL - users can click to add AND drag to adjust locations

**Implementation Notes**:
- Markers are draggable only in edit mode (`isEditMode={true}`)
- Dragging triggers reverse geocoding automatically
- Modal shows suggested name with updated coordinates
- User can confirm to update location or cancel to revert
- Visual feedback: `cursor: grab/grabbing`, scale on hover, drop shadow
- handleConfirmLocation now handles both adding new locations AND updating existing ones

---

## Phase 5: User Story 3 - Edit Location Name Before Saving (Priority: P3) ✅ COMPLETE

**Goal**: Allow users to edit the suggested place name before confirming location addition

**Independent Test**: Click map to trigger location suggestion, edit suggested name in modal input field, confirm location, verify custom name is saved (not suggested name)

**Status**: ✅ Implementation was already complete from initial development (Phase 3). Added comprehensive test coverage retroactively.

### Tests for User Story 3 ✅ TESTS COMPLETE

- [x] T035 [P] [US3] Unit test for LocationConfirmModal name editing in frontend/tests/unit/LocationConfirmModal.test.tsx
- [x] T036 [P] [US3] Integration test for name edit → confirm → custom name saved workflow in frontend/tests/integration/TripForm.geocoding.test.tsx

### Implementation for User Story 3 ✅ COMPLETE (Already Implemented)

- [x] T037 [US3] Add name input field to LocationConfirmModal in frontend/src/components/trips/LocationConfirmModal.tsx *(already implemented)*
- [x] T038 [US3] Implement controlled input with editedName state in LocationConfirmModal in frontend/src/components/trips/LocationConfirmModal.tsx *(already implemented)*
- [x] T039 [US3] Add validation for empty name (disable confirm button) in LocationConfirmModal in frontend/src/components/trips/LocationConfirmModal.tsx *(already implemented)*
- [x] T040 [US3] Add validation for name length (max 200 chars) in LocationConfirmModal in frontend/src/components/trips/LocationConfirmModal.tsx *(already implemented)*
- [x] T041 [US3] Update onConfirm callback to use editedName if provided in LocationConfirmModal in frontend/src/components/trips/LocationConfirmModal.tsx *(already implemented)*
- [x] T042 [US3] Style input field with ContraVento design system in frontend/src/components/trips/LocationConfirmModal.css *(already implemented)*

**Checkpoint**: ✅ All user stories (1, 2, AND 3) are FULLY FUNCTIONAL - complete workflow from click to drag to edit

**Implementation Notes**:

- All functionality was already implemented during Phase 3 (T016) when LocationConfirmModal was first created
- Added comprehensive test coverage with 23 unit tests (T035) and 6 integration tests (T036)
- Input field features:
  - Controlled component with `editedName` state
  - Pre-populated with `suggestedName` or `editedName` from LocationSelection
  - Real-time validation (empty check, max 200 chars)
  - Character counter (shows when input has content)
  - Confirm button disabled when name invalid
  - Automatic trimming of whitespace before saving
  - Allows manual entry when geocoding fails
  - AutoFocus enabled for better UX

---

## Phase 6: Polish & Cross-Cutting Concerns ✅ COMPLETE (11/13 tasks)

**Purpose**: Improvements that affect multiple user stories

- [x] T043 [P] Add Spanish error messages for all geocoding errors in frontend/src/services/geocodingService.ts ✅
- [x] T044 [P] Add accessibility labels (ARIA attributes) to modal and buttons in frontend/src/components/trips/LocationConfirmModal.tsx ✅
- [x] T045 [P] Add responsive styles for mobile (map click and modal) in frontend/src/components/trips/LocationConfirmModal.css ✅
- [ ] T046 [P] Test on mobile devices (touch events for map click and drag) - **Requires physical device**
- [x] T047 [P] Add console logging for cache hit/miss rates (development only) ✅
- [x] T048 [P] Verify no Nominatim rate limit violations (monitor Network tab for 429) ✅
- [x] T049 [P] Update CLAUDE.md with reverse geocoding patterns ✅
- [x] T050 [P] Update frontend/TESTING_GUIDE.md with geocoding test scenarios ✅ **(Expanded from 64 to 1,066 lines)**
- [x] T051 Code cleanup: Remove console.logs, ensure TypeScript strict mode passes ✅
- [x] T052 Run npm run lint and npm run type-check, fix all errors ✅
- [x] T053 Run npm run test, verify all tests pass with ≥90% coverage ✅
- [x] T054 Manual QA: Test all 3 user stories end-to-end on staging ✅ **(MANUAL_QA.md created)**
- [x] T055 Run quickstart.md validation - verify all implementation steps completed ✅ **(QUICKSTART_VALIDATION.md created)**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (uses same TripMap) but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 modal but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Components before integration
- Modal before TripEditPage integration (US1)
- TripMap updates before TripEditPage integration (US2)
- Input validation before modal completion (US3)

### Parallel Opportunities

- **Setup (Phase 1)**: T001, T002, T003 can run in parallel
- **Foundational (Phase 2)**: T004-T008 can run in parallel (different files), T009 depends on T007
- **US1 Tests (Phase 3)**: T010-T014 can all run in parallel (TDD: write all tests first)
- **US1 Implementation**: T015-T017 can run in parallel (different components), T018-T026 sequential (same files)
- **US2 Tests**: T027-T028 can run in parallel
- **US2 Implementation**: T029-T031 sequential (TripMap updates), T032-T033 sequential (TripEditPage), T034 independent
- **US3 Tests**: T035-T036 can run in parallel
- **US3 Implementation**: T037-T041 sequential (LocationConfirmModal), T042 independent
- **Polish (Phase 6)**: T043-T050 can all run in parallel (different concerns)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write all tests first):
Task: "Unit test for geocodingService.reverseGeocode() in frontend/tests/unit/geocodingService.test.ts"
Task: "Unit test for geocodingService.extractLocationName() in frontend/tests/unit/geocodingService.test.ts"
Task: "Unit test for GeocodingCache get/set/eviction in frontend/tests/unit/geocodingCache.test.ts"
Task: "Unit test for useReverseGeocode hook in frontend/tests/unit/useReverseGeocode.test.ts"
Task: "Integration test for map click → modal → location added in frontend/tests/integration/TripForm.geocoding.test.tsx"

# Verify all tests FAIL (Red phase)

# Launch all components for User Story 1 together:
Task: "Create MapClickHandler component in frontend/src/components/trips/MapClickHandler.tsx"
Task: "Create LocationConfirmModal component in frontend/src/components/trips/LocationConfirmModal.tsx"
Task: "Create LocationConfirmModal styles in frontend/src/components/trips/LocationConfirmModal.css"

# Then integrate sequentially (same file edits):
Task: "Update TripMap component to accept isEditMode prop"
Task: "Update TripMap to accept onMapClick callback prop"
# ... (T018-T026 sequential)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install lodash.debounce)
2. Complete Phase 2: Foundational (types, cache, service, hook)
3. Write all US1 tests FIRST (T010-T014) - verify they FAIL
4. Complete Phase 3: User Story 1 implementation (T015-T026)
5. Verify all US1 tests PASS (Green phase)
6. **STOP and VALIDATE**: Test User Story 1 independently
7. Deploy/demo if ready (users can click map to add locations)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (P1) → Test independently → Deploy/Demo (MVP!)
   - **Value**: Users can click map to add locations (replaces manual coordinate entry)
3. Add User Story 2 (P2) → Test independently → Deploy/Demo
   - **Value**: Users can fine-tune locations by dragging markers
4. Add User Story 3 (P3) → Test independently → Deploy/Demo
   - **Value**: Users can customize place names before confirming
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phase 1-2)
2. Once Foundational is done:
   - Developer A: User Story 1 (map click + modal)
   - Developer B: User Story 2 (marker dragging)
   - Developer C: User Story 3 (name editing)
3. Stories complete and integrate independently
4. Merge order: US1 → US2 → US3 (priority order)

---

## Task Count Summary

- **Total Tasks**: 55
- **Setup (Phase 1)**: 3 tasks
- **Foundational (Phase 2)**: 6 tasks
- **User Story 1 (Phase 3)**: 17 tasks (5 tests + 12 implementation)
- **User Story 2 (Phase 4)**: 8 tasks (2 tests + 6 implementation)
- **User Story 3 (Phase 5)**: 8 tasks (2 tests + 6 implementation)
- **Polish (Phase 6)**: 13 tasks

**Parallel Opportunities**: 25 tasks marked [P] (45% of total)

**Independent Test Criteria**:
- **US1**: Click map → modal appears → location added to trip
- **US2**: Drag marker → coordinates update → new name suggested
- **US3**: Edit name → confirm → custom name saved

**Suggested MVP Scope**: User Story 1 only (17 tasks + foundational)
**Estimated Time**:
- MVP (US1): 1-2 days
- US2: 1 day
- US3: 0.5 day
- Polish & testing: 0.5 day
- **Total**: 3-4 days

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD enforced: Write tests FIRST, verify they FAIL, implement, verify they PASS
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend-only feature - no backend changes
- No database migrations required
