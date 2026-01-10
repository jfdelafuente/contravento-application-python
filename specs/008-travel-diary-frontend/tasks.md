# Tasks: Travel Diary Frontend

**Input**: Design documents from `/specs/008-travel-diary-frontend/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅), quickstart.md (✅)

**Tests**: Manual acceptance testing following Feature 007 pattern. No automated UI tests (per constitution - UI components tested manually).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for all TypeScript/React code
- **Backend APIs**: Already exist from Feature 002 (Travel Diary Backend)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure project for Travel Diary feature

- [x] T001 Install react-dropzone@14.x for drag-and-drop file uploads
- [x] T002 Install yet-another-react-lightbox@2.x for photo gallery viewer
- [x] T003 [P] Install react-leaflet@4.x and leaflet@1.9.x for map display
- [x] T004 [P] Verify all dependencies installed successfully with npm list

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core type definitions, services, and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create Trip TypeScript interfaces in frontend/src/types/trip.ts (Trip, TripListItem, TripPhoto, Tag, TripLocation) ✅
- [x] T006 [P] Create Trip form interfaces in frontend/src/types/trip.ts (TripCreateInput, TripUpdateInput, TripFormData, PhotoUploadState) ✅
- [x] T007 [P] Create Zod validation schema for trip forms in frontend/src/utils/tripValidators.ts (tripFormSchema) ✅
- [x] T008 [P] Create Zod validation schema for publishing in frontend/src/utils/tripValidators.ts (tripPublishSchema with 50-char description minimum) ✅
- [x] T009 [P] Create trip helper utilities in frontend/src/utils/tripHelpers.ts (getDifficultyLabel, getDifficultyClass, formatDate, formatDateTime) ✅
- [x] T010 Implement getTripById service in frontend/src/services/tripService.ts ✅
- [x] T011 [P] Implement getUserTrips service in frontend/src/services/tripService.ts ✅
- [x] T012 [P] Implement createTrip service in frontend/src/services/tripService.ts ✅
- [x] T013 [P] Implement updateTrip service in frontend/src/services/tripService.ts ✅
- [x] T014 [P] Implement deleteTrip service in frontend/src/services/tripService.ts ✅
- [x] T015 [P] Implement publishTrip service in frontend/src/services/tripService.ts ✅
- [x] T016 [P] Implement getAllTags service in frontend/src/services/tripService.ts ✅
- [x] T017 [P] Implement uploadTripPhoto service in frontend/src/services/tripPhotoService.ts (with chunked upload support) ✅
- [x] T018 [P] Implement deleteTripPhoto service in frontend/src/services/tripPhotoService.ts ✅
- [x] T019 [P] Implement reorderTripPhotos service in frontend/src/services/tripPhotoService.ts ✅
- [x] T020 Add React Router routes in frontend/src/App.tsx (/trips, /trips/:tripId, /trips/new, /trips/:tripId/edit) ✅

**Checkpoint**: Foundation ready - all API services available, types defined, validation schemas created. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - View Trip List with Filters (Priority: P1) 🎯 MVP

**Goal**: Allow users to browse trips with tag filters, keyword search, and pagination

**Independent Test**: Navigate to http://localhost:5173/trips and verify:
1. Grid of trip cards displays (12 per page)
2. Clicking tag chip filters trips by that tag (updates in <500ms)
3. Searching for "Pirineos" shows only matching trips
4. Pagination works (Next/Previous buttons)
5. Empty state displays when no trips found

### Implementation for User Story 1

- [X] T021 [P] [US1] Create TripCard component in frontend/src/components/trips/TripCard.tsx
- [X] T022 [P] [US1] Style TripCard component in frontend/src/components/trips/TripCard.css (difficulty badges, thumbnail, responsive grid)
- [X] T023 [P] [US1] Create TripFilters component in frontend/src/components/trips/TripFilters.tsx (search input, tag chips, status toggle)
- [X] T024 [P] [US1] Style TripFilters component in frontend/src/components/trips/TripFilters.css
- [X] T025 [US1] Create useTripList hook in frontend/src/hooks/useTripList.ts (fetch trips with pagination)
- [X] T026 [US1] Create useTripFilters hook in frontend/src/hooks/useTripFilters.ts (manage search, tags, status state)
- [X] T027 [US1] Create TripsListPage in frontend/src/pages/TripsListPage.tsx (integrate TripCard, TripFilters, useTripList, useTripFilters)
- [X] T028 [US1] Style TripsListPage in frontend/src/pages/TripsListPage.css (responsive grid: 3 cols desktop, 2 cols tablet, 1 col mobile)
- [X] T029 [US1] Add empty state illustration to frontend/public/images/trips/placeholders/no-trips-empty-state.svg
- [X] T030 [US1] Add loading skeleton for trip cards in TripsListPage

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can browse, filter, and search trips.

---

## Phase 4: User Story 2 - View Trip Details (Priority: P1)

**Goal**: Display complete trip information with photo gallery, tags, and location map

**Independent Test**: Click any trip card from the list and verify:
1. Trip detail page loads with hero image, title, dates, distance, difficulty badge
2. Full HTML description displays (sanitized by backend)
3. Photo gallery shows all photos in responsive grid
4. Clicking photo opens lightbox with prev/next navigation
5. Tags display as clickable chips
6. If trip has locations, map displays with markers
7. Owner sees "Edit" and "Delete" buttons (non-owners don't)
8. Draft trips show "Draft" badge and "Publish" button (owner only)

### Implementation for User Story 2

- [X] T031 [P] [US2] Create TripGallery component in frontend/src/components/trips/TripGallery.tsx (photo grid with lightbox integration)
- [X] T032 [P] [US2] Style TripGallery component in frontend/src/components/trips/TripGallery.css (3 cols desktop, 2 cols tablet, 1 col mobile)
- [X] T033 [P] [US2] Create TripMap component in frontend/src/components/trips/TripMap.tsx (react-leaflet with OpenStreetMap, lazy loaded)
- [X] T034 [P] [US2] Style TripMap component in frontend/src/components/trips/TripMap.css
- [X] T035 [US2] Create TripDetailPage in frontend/src/pages/TripDetailPage.tsx (integrate TripGallery, TripMap, display all trip data)
- [X] T036 [US2] Style TripDetailPage in frontend/src/pages/TripDetailPage.css (hero image, difficulty badges, tag chips, responsive layout)
- [X] T037 [US2] Integrate yet-another-react-lightbox in TripGallery (plugins: Thumbnails, Zoom, keyboard navigation)
- [X] T038 [US2] Add conditional rendering for map (only show if trip.locations exists)
- [X] T039 [US2] Add owner-only action buttons (Edit, Delete, Publish for drafts)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can browse trips AND view full trip details with photos.

---

## Phase 5: User Story 3 - Create Trip (Multi-Step Form) (Priority: P1)

**Goal**: Allow users to create trips using a guided 4-step wizard with validation and draft/publish workflow

**Independent Test**: Click "Create Trip" button and verify:
1. Step 1/4 (Basic Info) displays with title, dates, distance, difficulty fields
2. Clicking "Next" advances to Step 2/4 (Story & Tags) with description editor and tag input
3. Tag autocomplete suggests existing tags as user types
4. Step 3/4 (Photos) shows drag-and-drop upload area
5. Dragging images triggers validation (JPG/PNG, max 10MB) and upload with progress bars
6. Step 4/4 (Review) shows summary of all entered data
7. "Save as Draft" saves trip without validation and redirects to trips list
8. "Publish" validates description ≥50 chars and publishes trip
9. Form preserves data when navigating between steps
10. Browser warns about unsaved changes when navigating away

### Implementation for User Story 3

- [X] T040 [P] [US3] Create TripFormWizard component in frontend/src/components/trips/TripForm/TripFormWizard.tsx (main wizard controller with React Hook Form)
- [X] T041 [P] [US3] Style TripFormWizard component in frontend/src/components/trips/TripForm/TripFormWizard.css
- [X] T042 [P] [US3] Create FormStepIndicator component in frontend/src/components/trips/TripForm/FormStepIndicator.tsx (visual progress: 1/4, 2/4, 3/4, 4/4)
- [X] T043 [P] [US3] Create Step1BasicInfo component in frontend/src/components/trips/TripForm/Step1BasicInfo.tsx (title, dates, distance, difficulty)
- [X] T044 [P] [US3] Create Step2StoryTags component in frontend/src/components/trips/TripForm/Step2StoryTags.tsx (description textarea, tag input with autocomplete) - **Note**: Basic tag input implemented, autocomplete pending
- [X] T045 [P] [US3] Create Step3Photos component in frontend/src/components/trips/TripForm/Step3Photos.tsx (integrate PhotoUploader) - **Note**: Photo selection with file input implemented, drag-and-drop pending
- [X] T046 [P] [US3] Create Step4Review component in frontend/src/components/trips/TripForm/Step4Review.tsx (summary of all form data, save draft vs publish)
- [x] T047 [P] [US3] Create TagInput component in frontend/src/components/trips/TagInput.tsx (autocomplete from getAllTags, max 10 tags, client-side filtering) ✅ (Implemented in Step2StoryTags)
- [x] T048 [P] [US3] Create PhotoUploader component in frontend/src/components/trips/PhotoUploader.tsx (react-dropzone, chunked upload 3 at a time, progress bars) ✅
- [x] T049 [P] [US3] Style PhotoUploader component in frontend/src/components/trips/PhotoUploader.css (drop zone, thumbnail grid, progress bars) ✅
- [X] T050 [US3] Create useTripForm hook in frontend/src/hooks/useTripForm.ts (manage wizard state, current step, form data persistence)
- [x] T051 [US3] Create useTripPhotos hook in frontend/src/hooks/useTripPhotos.ts (chunked upload logic, progress tracking, error handling with retry) ✅
- [X] T052 [US3] Create TripCreatePage in frontend/src/pages/TripCreatePage.tsx (wrapper for TripFormWizard)
- [X] T053 [US3] Style TripCreatePage in frontend/src/pages/TripCreatePage.css
- [X] T054 [US3] Integrate useUnsavedChanges hook (from Feature 007) in TripFormWizard to warn on navigation
- [X] T055 [US3] Add form validation per step (Step 1: required fields, Step 2: tag limit, Step 4: publish validation)
- [X] T056 [US3] Add error handling for API failures (createTrip, uploadTripPhoto) with Spanish toast messages
- [X] T057 [US3] Add success handling for trip creation (redirect to trips list with success toast)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can browse trips, view details, AND create new trips with photos.

---

## Phase 6: User Story 4 - Upload and Manage Trip Photos (Priority: P2)

**Goal**: Allow users to upload multiple photos with drag-and-drop, reorder photos, and delete photos

**Independent Test**: Edit an existing trip and navigate to photos step, then verify:
1. Existing photos display with thumbnails
2. Drop zone accepts new photo uploads
3. Dragging 5 images uploads them in chunks of 3 with individual progress bars
4. Upload completes in <30 seconds for 5 images (5MB total)
5. Thumbnails appear in gallery with reorder handles (drag icon)
6. Dragging photo to new position updates order immediately
7. Clicking delete icon shows confirmation dialog
8. Confirming deletion removes photo and updates gallery
9. Invalid files (.txt, >10MB) show error message "Only JPG and PNG images allowed (max 10MB)"
10. Failed uploads show retry button

### Implementation for User Story 4

- [X] T058 [US4] Add drag-and-drop reordering to PhotoUploader component (HTML5 drag API or react-beautiful-dnd)
- [X] T059 [US4] Implement handlePhotoReorder function in useTripPhotos hook (calls reorderTripPhotos service)
- [X] T060 [US4] Implement handlePhotoDelete function in useTripPhotos hook (calls deleteTripPhoto service with confirmation)
- [X] T061 [US4] Add photo reorder visual feedback in PhotoUploader (dragging state, drop target highlight)
- [X] T062 [US4] Add delete confirmation dialog in PhotoUploader
- [X] T063 [US4] Add retry button for failed uploads in PhotoUploader - **Already implemented in Phase 5**
- [X] T064 [US4] Add file validation error messages in PhotoUploader (Spanish: "Solo se permiten imágenes JPG y PNG (máx 10MB)") - **Already implemented in Phase 5**

**Checkpoint**: At this point, User Story 4 enhances User Story 3 (Create Trip) with advanced photo management. All photo operations work independently.

---

## Phase 7: User Story 5 - Edit Existing Trip (Priority: P2)

**Goal**: Allow trip owners to edit trip details using the same multi-step wizard

**Independent Test**: View any owned trip and click "Edit", then verify:
1. Multi-step form loads pre-filled with current trip data
2. All 4 steps show existing values (title, dates, description, tags, photos)
3. Modifying fields in any step preserves changes
4. Saving updates the trip (PUT /trips/{id})
5. Published trips remain published after edit
6. Draft trips can be published after completing all required fields
7. Validation prevents invalid date ranges (end_date < start_date)
8. Optimistic locking prevents concurrent edits (409 Conflict error shows warning)

### Implementation for User Story 5

- [X] T065 [US5] Create TripEditPage in frontend/src/pages/TripEditPage.tsx (wrapper for TripFormWizard in edit mode)
- [X] T066 [US5] Style TripEditPage in frontend/src/pages/TripEditPage.css
- [X] T067 [US5] Add edit mode support to TripFormWizard (detect tripId param, fetch existing trip, pre-fill form) - **Already implemented in Phase 5**
- [X] T068 [US5] Add edit mode support to useTripForm hook (load existing trip data, track original updated_at for optimistic locking)
- [X] T069 [US5] Modify form submission to use updateTrip service when in edit mode
- [X] T070 [US5] Add optimistic locking error handling (409 Conflict → show warning: "El viaje fue modificado por otra sesión. Recarga la página.")
- [X] T071 [US5] Add edit button to TripDetailPage (owner-only, routes to /trips/{id}/edit)

**Checkpoint**: At this point, User Story 5 allows editing existing trips. All CRUD operations complete (Create, Read, Update). Only Delete remains.

---

## Phase 8: User Story 6 - Delete Trip (Priority: P3)

**Goal**: Allow trip owners to permanently delete trips with confirmation

**Independent Test**: View any owned trip and click "Delete", then verify:
1. Confirmation dialog displays with warning: "¿Estás seguro de que quieres eliminar este viaje? Esta acción es permanente."
2. Clicking "Cancel" closes dialog without deleting
3. Clicking "Confirm" deletes trip and all photos
4. After deletion, user is redirected to trips list
5. Deleted trip no longer appears in list
6. User stats are recalculated automatically (backend handles this)

### Implementation for User Story 6

- [x] T072 [US6] Implement handleDeleteTrip function in TripDetailPage (calls deleteTrip service) ✅
- [x] T073 [US6] Add delete confirmation dialog in TripDetailPage ✅
- [x] T074 [US6] Add delete button to TripDetailPage (owner-only, danger style) ✅ (Already existed, enhanced with confirmation dialog)
- [x] T075 [US6] Add error handling for delete failures (403 Forbidden, 404 Not Found) with Spanish toast messages ✅
- [x] T076 [US6] Add success handling for deletion (redirect to /trips with success toast: "Viaje eliminado correctamente") ✅

**Checkpoint**: All user stories complete! Users can browse (US1), view (US2), create (US3), manage photos (US4), edit (US5), and delete (US6) trips.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, responsive design, accessibility, and performance optimization

- [x] T077 [P] Add loading skeletons for TripCard in TripsListPage (shimmer effect while loading) ✅ (Already implemented)
- [x] T078 [P] Add loading spinner for TripDetailPage (while fetching trip data) ✅ (Already implemented)
- [x] T079 [P] Add loading spinner for TripFormWizard (while submitting) ✅
- [x] T080 [P] Optimize image lazy loading in TripGallery (use Intersection Observer) ✅
- [ ] T081 [P] Add responsive design testing (mobile <640px, tablet 640-1023px, desktop ≥1024px)
- [x] T082 [P] Add accessibility features (alt text for all images, ARIA labels for form fields, keyboard navigation for lightbox) ✅
- [x] T083 [P] Add difficulty badge CSS classes in TripCard.css (easy: green, moderate: orange, difficult: red, very_difficult: dark red) ✅
- [x] T084 [P] Add Spanish error messages for all API failures (network errors, validation errors, authorization errors) ✅ (Already implemented)
- [ ] T085 [P] Verify all success criteria from spec.md (SC-001 to SC-012)
- [ ] T086 [P] Run Lighthouse performance audit (target: Performance ≥90, Accessibility ≥90)
- [ ] T087 [P] Test photo upload performance (verify 5 photos upload in <30s on 3G throttling)
- [ ] T088 [P] Test tag filtering performance (verify filters update in <500ms)
- [ ] T089 [P] Test form navigation performance (verify step transitions in <200ms)
- [ ] T090 [P] Test lightbox transitions (verify photo transitions in <300ms)
- [x] T091 Create manual acceptance testing guide in specs/008-travel-diary-frontend/MANUAL_TESTING.md ✅
- [x] T092 Document common pitfalls in specs/008-travel-diary-frontend/TROUBLESHOOTING.md (photo URLs are absolute, tag normalization, date formats, form state vs API payload) ✅
- [x] T093 Update CLAUDE.md with Travel Diary frontend patterns and examples ✅

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel if staffed (US1, US2, US3 are independent)
  - OR sequentially in priority order (P1 → P1 → P1 → P2 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Enhances US3 but independently testable
- **User Story 5 (P2)**: Depends on User Story 3 completion (reuses TripFormWizard in edit mode)
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Components marked [P] can be created in parallel (different files)
- Hooks depend on services being available (Phase 2 Foundational)
- Pages integrate components and hooks (created last within each story)
- Each story completes before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: All 4 tasks can run in parallel
- **Foundational (Phase 2)**:
  - T005-T009 (types, validators, utilities) can run in parallel
  - T010-T019 (all API services) can run in parallel after types are defined
- **User Story 1**: T021-T024 (components and styles) can run in parallel
- **User Story 2**: T031-T034 (components and styles) can run in parallel
- **User Story 3**: T040-T049 (all wizard components, TagInput, PhotoUploader) can run in parallel
- **User Story 4-6**: Most tasks can run in parallel within each story
- **Polish (Phase 9)**: T077-T090 can all run in parallel

---

## Parallel Example: User Story 3 (Create Trip)

```bash
# Launch all wizard components in parallel (T040-T049):
Task 1: "Create TripFormWizard component in frontend/src/components/trips/TripForm/TripFormWizard.tsx"
Task 2: "Style TripFormWizard component in frontend/src/components/trips/TripForm/TripFormWizard.css"
Task 3: "Create FormStepIndicator component in frontend/src/components/trips/TripForm/FormStepIndicator.tsx"
Task 4: "Create Step1BasicInfo component in frontend/src/components/trips/TripForm/Step1BasicInfo.tsx"
Task 5: "Create Step2StoryTags component in frontend/src/components/trips/TripForm/Step2StoryTags.tsx"
Task 6: "Create Step3Photos component in frontend/src/components/trips/TripForm/Step3Photos.tsx"
Task 7: "Create Step4Review component in frontend/src/components/trips/TripForm/Step4Review.tsx"
Task 8: "Create TagInput component in frontend/src/components/trips/TagInput.tsx"
Task 9: "Create PhotoUploader component in frontend/src/components/trips/PhotoUploader.tsx"
Task 10: "Style PhotoUploader component in frontend/src/components/trips/PhotoUploader.css"

# After components complete, create hooks sequentially:
Task 11: "Create useTripForm hook in frontend/src/hooks/useTripForm.ts"
Task 12: "Create useTripPhotos hook in frontend/src/hooks/useTripPhotos.ts"

# Finally, integrate in page:
Task 13: "Create TripCreatePage in frontend/src/pages/TripCreatePage.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only)

1. Complete Phase 1: Setup (4 tasks)
2. Complete Phase 2: Foundational (16 tasks) - CRITICAL foundation
3. Complete Phase 3: User Story 1 - View Trip List (10 tasks)
4. **VALIDATE**: Test US1 independently (browse, filter, search, pagination)
5. Complete Phase 4: User Story 2 - View Trip Details (9 tasks)
6. **VALIDATE**: Test US2 independently (view details, gallery, map)
7. Complete Phase 5: User Story 3 - Create Trip (18 tasks)
8. **VALIDATE**: Test US3 independently (create trip, upload photos, publish)
9. **STOP and DEMO**: MVP is complete! Users can browse, view, and create trips.

### Incremental Delivery (Add P2 and P3 Stories)

10. Complete Phase 6: User Story 4 - Upload and Manage Photos (7 tasks)
11. **VALIDATE**: Test US4 independently (reorder, delete photos)
12. Complete Phase 7: User Story 5 - Edit Trip (7 tasks)
13. **VALIDATE**: Test US5 independently (edit all fields, optimistic locking)
14. Complete Phase 8: User Story 6 - Delete Trip (5 tasks)
15. **VALIDATE**: Test US6 independently (delete with confirmation)
16. Complete Phase 9: Polish (17 tasks)
17. **FINAL VALIDATION**: Run all success criteria tests (SC-001 to SC-012)

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2: 20 tasks)
2. **Once Foundational is done, split work**:
   - Developer A: User Story 1 - View List (Phase 3: 10 tasks)
   - Developer B: User Story 2 - View Details (Phase 4: 9 tasks)
   - Developer C: User Story 3 - Create Trip (Phase 5: 18 tasks)
3. **After P1 stories complete, continue**:
   - Developer A: User Story 4 - Manage Photos (Phase 6: 7 tasks)
   - Developer B: User Story 5 - Edit Trip (Phase 7: 7 tasks)
   - Developer C: User Story 6 - Delete Trip (Phase 8: 5 tasks)
4. **All developers: Polish together** (Phase 9: 17 tasks)

---

## Task Summary

**Total Tasks**: 93 tasks

**Tasks per Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 16 tasks
- Phase 3 (US1 - View List): 10 tasks
- Phase 4 (US2 - View Details): 9 tasks
- Phase 5 (US3 - Create Trip): 18 tasks
- Phase 6 (US4 - Manage Photos): 7 tasks
- Phase 7 (US5 - Edit Trip): 7 tasks
- Phase 8 (US6 - Delete Trip): 5 tasks
- Phase 9 (Polish): 17 tasks

**Parallel Opportunities**: 62 tasks marked [P] can run in parallel within their phase

**MVP Scope** (P1 stories only): 57 tasks (Phases 1-5)

**Estimated Timeline**:
- MVP (P1 only): 8-10 days
- Full Feature (P1+P2+P3): 14-16 days
- With 3 developers in parallel: 6-8 days

---

## Notes

- [P] tasks = different files, no dependencies within the same phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual acceptance testing guide will be created in T091
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend patterns follow Feature 007 (Profile Management) conventions
- Backend APIs already exist from Feature 002 (no backend work needed)
