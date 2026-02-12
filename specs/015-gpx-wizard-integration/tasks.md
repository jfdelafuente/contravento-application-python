# Tasks: GPX Wizard Integration

**Feature Branch**: `015-gpx-wizard-integration`
**Input**: Design documents from `/specs/015-gpx-wizard-integration/`
**Prerequisites**: spec.md, plan.md
**Related Features**: 003-gps-routes, 008-travel-diary-frontend

**Organization**: Tasks are organized by phase for sequential implementation (no parallel user stories).

**Tests**: TDD approach - write tests before implementation where applicable.

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`, `frontend/tests/`
- **No backend changes** required for this feature

---

## Phase 1: Setup (Infrastructure)

**Purpose**: Branch creation and prerequisite verification

- [ ] T001 Create branch `015-gpx-wizard-integration` from `develop`
- [ ] T002 Verify Feature 003 (GPS Routes) is complete and merged to develop
- [ ] T003 Verify Feature 008 (Travel Diary Frontend) exists with TripFormWizard component
- [ ] T004 Verify GPXUploader component exists at `frontend/src/components/trips/GPXUploader.tsx`

**Checkpoint**: Prerequisites verified, ready to begin implementation

---

## Phase 2: Component Creation (Modal UI)

**Purpose**: Create PostCreationGPXModal component with all UI states

### Tests for Modal Component (TDD - Write First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T005 [P] Unit test: Modal renders nothing when isOpen=false in `frontend/tests/unit/PostCreationGPXModal.test.tsx`
- [ ] T006 [P] Unit test: Modal renders prompt state initially (title, description, buttons) in `frontend/tests/unit/PostCreationGPXModal.test.tsx`
- [ ] T007 [P] Unit test: Shows GPXUploader when "Sí, subir ahora" clicked in `frontend/tests/unit/PostCreationGPXModal.test.tsx`
- [ ] T008 [P] Unit test: Calls onClose when "No, lo haré después" clicked in `frontend/tests/unit/PostCreationGPXModal.test.tsx`
- [ ] T009 [P] Unit test: Calls onClose when overlay clicked in `frontend/tests/unit/PostCreationGPXModal.test.tsx`
- [ ] T010 [P] Unit test: Calls onClose when ESC key pressed in `frontend/tests/unit/PostCreationGPXModal.test.tsx`
- [ ] T011 [P] Unit test: Does not close when modal content clicked in `frontend/tests/unit/PostCreationGPXModal.test.tsx`
- [ ] T012 [P] Unit test: Has correct ARIA attributes (role="dialog", aria-modal="true") in `frontend/tests/unit/PostCreationGPXModal.test.tsx`

### Implementation for Modal Component

- [ ] T013 Create TypeScript interface `PostCreationGPXModalProps` in `frontend/src/components/trips/PostCreationGPXModal.tsx`
  - Props: tripId, isOpen, onClose, onComplete
  - Add JSDoc comments for each prop
- [ ] T014 Implement PostCreationGPXModal component structure in `frontend/src/components/trips/PostCreationGPXModal.tsx`
  - State: uploadStarted (boolean)
  - Conditional rendering: prompt state vs upload state
  - ESC key handler with cleanup
  - Focus trap implementation
- [ ] T015 Implement prompt state UI (initial view) in `frontend/src/components/trips/PostCreationGPXModal.tsx`
  - Title: "¿Agregar ruta GPX?"
  - Description paragraph (Spanish)
  - Two buttons: "Sí, subir ahora" and "No, lo haré después"
  - Close button (X) in top-right corner
- [ ] T016 Implement upload state UI in `frontend/src/components/trips/PostCreationGPXModal.tsx`
  - Title: "Subir archivo GPX"
  - Embed GPXUploader component with tripId prop
  - Pass onUploadComplete callback (calls onComplete + onClose)
  - Back button to return to prompt state
- [ ] T017 Add modal overlay with click-to-close in `frontend/src/components/trips/PostCreationGPXModal.tsx`
  - Overlay background with backdrop blur
  - stopPropagation on modal content click
  - Proper z-index (1000)
- [ ] T018 Add ARIA attributes for accessibility in `frontend/src/components/trips/PostCreationGPXModal.tsx`
  - role="dialog", aria-modal="true"
  - aria-labelledby pointing to title ID
  - Focus management (focus modal on open)
  - Tab key navigation within modal

### Styling

- [ ] T019 Create CSS file `frontend/src/components/trips/PostCreationGPXModal.css`
  - Modal overlay styles (fixed position, backdrop blur)
  - Modal content styles (centered, max-width 600px)
  - Button styles (primary, secondary)
  - Close button (X) styles
  - Animations (fadeIn, slideUp)
- [ ] T020 Add mobile-responsive styles in `frontend/src/components/trips/PostCreationGPXModal.css`
  - Media query @media (max-width: 640px)
  - Bottom-aligned modal on mobile
  - Full-width stacked buttons
  - Touch-friendly targets (≥44px)
  - Viewport-relative sizing (90vw, 85vh)

### Verification

- [ ] T021 Run unit tests for PostCreationGPXModal: `npm test PostCreationGPXModal.test.tsx`
  - Verify 8/8 tests passing
  - Verify ≥90% coverage for component
- [ ] T022 Manual test: Render modal in isolation via Storybook or standalone page
  - Verify prompt state renders correctly
  - Verify buttons trigger state changes
  - Verify ESC key closes modal
  - Verify overlay click closes modal

**Checkpoint**: PostCreationGPXModal component complete and tested in isolation

---

## Phase 3: State Management Integration

**Purpose**: Integrate modal into trip creation flow via useTripForm hook

- [ ] T023 Add GPX modal state to `frontend/src/hooks/useTripForm.ts`
  - Add state: showGPXModal (boolean, default false)
  - Add state: createdTripId (string | null, default null)
- [ ] T024 Modify handleSubmit in `frontend/src/hooks/useTripForm.ts` to show modal instead of immediate navigation
  - After successful trip creation: setCreatedTripId(trip.trip_id)
  - After photos upload: setShowGPXModal(true)
  - Remove direct navigate() call for create mode
  - Keep direct navigate() for edit mode (no modal)
- [ ] T025 Add handleGPXModalClose function to `frontend/src/hooks/useTripForm.ts`
  - setShowGPXModal(false)
  - navigate(`/trips/${createdTripId}`)
- [ ] T026 Add handleGPXUploadComplete function to `frontend/src/hooks/useTripForm.ts`
  - toast.success('Archivo GPX procesado correctamente')
  - Modal close handled by onClose callback
- [ ] T027 Export new state and handlers from `frontend/src/hooks/useTripForm.ts`
  - Return: { showGPXModal, createdTripId, handleGPXModalClose, handleGPXUploadComplete, ...existing }

**Checkpoint**: useTripForm hook modified, modal state managed correctly

---

## Phase 4: UI Integration

**Purpose**: Integrate modal into TripCreatePage/TripFormWizard

- [ ] T028 Import PostCreationGPXModal in `frontend/src/pages/TripCreatePage.tsx` (or wherever TripFormWizard is rendered)
- [ ] T029 Destructure new state from useTripForm in `frontend/src/pages/TripCreatePage.tsx`
  - const { showGPXModal, createdTripId, handleGPXModalClose, handleGPXUploadComplete } = useTripForm(...)
- [ ] T030 Render PostCreationGPXModal component in `frontend/src/pages/TripCreatePage.tsx`
  - Conditionally render: {createdTripId && <PostCreationGPXModal ... />}
  - Pass props: tripId={createdTripId}, isOpen={showGPXModal}, onClose={handleGPXModalClose}, onComplete={handleGPXUploadComplete}
  - Place after TripFormWizard in JSX

**Checkpoint**: Modal integrated into trip creation page, ready for end-to-end testing

---

## Phase 5: End-to-End Testing

**Purpose**: Manual testing of complete trip creation flow with modal

### Manual Test Scenarios

- [ ] T031 Manual test: Test Case 1 - Successful GPX Upload via Modal
  1. Navigate to /trips/create
  2. Complete 4-step wizard (title, description, dates, etc.)
  3. Click "Publicar" (or "Guardar Borrador")
  4. ✅ Verify modal appears with "¿Agregar ruta GPX?"
  5. Click "Sí, subir ahora"
  6. ✅ Verify GPXUploader appears in modal
  7. Drag-drop valid GPX file (e.g., `backend/tests/fixtures/gpx/short_route.gpx`)
  8. ✅ Verify upload progress shown (spinner or progress bar)
  9. ✅ Verify success toast: "Archivo GPX procesado correctamente"
  10. ✅ Verify modal closes automatically after success
  11. ✅ Verify navigated to `/trips/{trip_id}`
  12. ✅ Verify GPX data visible on TripDetailPage (map, stats)

- [ ] T032 Manual test: Test Case 2 - Skip GPX Upload
  1. Navigate to /trips/create
  2. Complete 4-step wizard
  3. Click "Publicar"
  4. ✅ Verify modal appears
  5. Click "No, lo haré después"
  6. ✅ Verify modal closes immediately
  7. ✅ Verify navigated to `/trips/{trip_id}`
  8. ✅ Verify GPXUploader still visible on TripDetailPage (can upload later)
  9. ✅ Verify trip created successfully (has title, description, etc.)

- [ ] T033 Manual test: Test Case 3 - GPX Upload Error Handling
  1. Navigate to /trips/create
  2. Complete wizard → modal appears
  3. Click "Sí, subir ahora"
  4. Upload invalid file (e.g., file >10MB, exceeds limit)
  5. ✅ Verify error toast with Spanish message
  6. ✅ Verify modal stays open (allows retry)
  7. Click "No, lo haré después"
  8. ✅ Verify navigated to detail page
  9. ✅ Verify trip exists and is NOT deleted
  10. ✅ Verify can upload GPX from TripDetailPage

- [ ] T034 Manual test: Test Case 4 - ESC Key and Overlay Click
  1. Complete wizard → modal appears
  2. Press ESC key
  3. ✅ Verify modal closes
  4. ✅ Verify navigated to `/trips/{trip_id}`
  5. Create another trip → modal appears
  6. Click overlay background (outside modal content)
  7. ✅ Verify modal closes
  8. ✅ Verify navigated to detail page

- [ ] T035 Manual test: Test Case 5 - Mobile Responsiveness
  1. Open browser DevTools (Chrome or Firefox)
  2. Switch to mobile viewport (375px width, e.g., iPhone SE)
  3. Navigate to /trips/create
  4. Complete wizard → modal appears
  5. ✅ Verify modal bottom-aligned on mobile
  6. ✅ Verify buttons full-width and stacked vertically
  7. ✅ Verify button touch targets ≥44px height
  8. Click "Sí, subir ahora"
  9. ✅ Verify GPXUploader usable on mobile (drag-drop or file input)

- [ ] T036 Manual test: Test Case 6 - Edit Mode (No Modal)
  1. Navigate to existing trip detail page
  2. Click "Editar" button
  3. Modify trip (e.g., change title)
  4. Click "Guardar Cambios"
  5. ✅ Verify modal does NOT appear (edit mode skips modal)
  6. ✅ Verify navigated directly to detail page

**Checkpoint**: All 6 manual test cases pass successfully

---

## Phase 6: Accessibility & Cross-Browser Testing

**Purpose**: Ensure modal works across browsers and assistive technologies

- [ ] T037 Test keyboard navigation
  - Tab key: Cycles through modal buttons
  - Enter key: Activates focused button
  - ESC key: Closes modal
  - ✅ Verify focus returns to page after modal closes
- [ ] T038 Test screen reader compatibility
  - macOS VoiceOver or Windows Narrator
  - ✅ Verify modal title announced
  - ✅ Verify button labels clear ("Subir archivo GPX ahora" not just "Sí")
  - ✅ Verify modal close announced
- [ ] T039 Test browser compatibility
  - Chrome: ✅ Modal renders and functions correctly
  - Firefox: ✅ Modal renders and functions correctly
  - Safari (macOS/iOS): ✅ Modal renders and functions correctly
  - Edge: ✅ Modal renders and functions correctly
- [ ] T040 Test mobile device touch gestures
  - iOS Safari: ✅ Tap buttons work, overlay tap closes
  - Android Chrome: ✅ Tap buttons work, overlay tap closes
  - ✅ No accidental closures when scrolling modal content

**Checkpoint**: Modal accessible and cross-browser compatible

---

## Phase 7: Documentation & Polish

**Purpose**: Update documentation and finalize implementation

- [ ] T041 Update `CLAUDE.md` with GPX Wizard Integration section
  - Add to "Travel Diary Frontend (Feature 008)" section
  - Document post-creation modal pattern
  - Include code example of useTripForm modifications
  - Add common pitfalls section
- [ ] T042 Add JSDoc comments to PostCreationGPXModal component
  - Component description
  - Prop descriptions
  - Usage example in JSDoc
- [ ] T043 Add JSDoc comments to useTripForm hook modifications
  - Document showGPXModal state
  - Document handleGPXModalClose function
  - Document handleGPXUploadComplete function
- [ ] T044 Create README section in feature spec
  - Add quick start guide for developers
  - Document how to disable modal (if needed for debugging)
  - Add screenshot of modal (optional)
- [ ] T045 Code review: Self-review checklist
  - ✅ No console.log statements left in code
  - ✅ All TODOs resolved
  - ✅ Spanish text throughout (no English)
  - ✅ TypeScript: Zero errors, zero warnings
  - ✅ ESLint: No violations
  - ✅ Prettier: Code formatted
  - ✅ No commented-out code blocks

**Checkpoint**: Documentation complete, code clean and ready for PR

---

## Phase 8: Pull Request & Deployment

**Purpose**: Submit code for review and merge to develop

- [ ] T046 Run full test suite before PR
  - `npm test` → All tests passing
  - `npm run lint` → No ESLint errors
  - `npm run type-check` → No TypeScript errors
  - `npm run build` → Build succeeds
- [ ] T047 Create pull request from `015-gpx-wizard-integration` to `develop`
  - Title: "Feature 015: GPX Wizard Integration (Post-Creation Modal)"
  - Description: Link to spec.md, summary of changes
  - Screenshots: Before/after flow, modal appearance
  - Testing: Document manual test results
  - Checklist: All acceptance criteria met
- [ ] T048 Address PR review feedback
  - Respond to reviewer comments
  - Make requested changes
  - Update tests if needed
- [ ] T049 Merge PR to develop after approval
  - Squash commits or merge (per project convention)
  - Delete branch after merge
- [ ] T050 Verify feature works on develop branch
  - Pull develop locally
  - Run `npm install` (if package.json changed)
  - Test trip creation flow with modal
  - ✅ Confirm no regressions

**Checkpoint**: Feature 015 merged to develop successfully

---

## Dependencies & Execution Order

### Phase Dependencies

All phases are sequential (no parallel work):

1. **Phase 1 (Setup)**: Must complete first
2. **Phase 2 (Component)**: Depends on Phase 1
3. **Phase 3 (State)**: Depends on Phase 2
4. **Phase 4 (Integration)**: Depends on Phase 3
5. **Phase 5 (E2E Testing)**: Depends on Phase 4
6. **Phase 6 (Accessibility)**: Depends on Phase 5
7. **Phase 7 (Documentation)**: Depends on Phase 6
8. **Phase 8 (PR)**: Depends on Phase 7

### Critical Path

**Minimal MVP** (fastest path to working feature):
1. Phase 1: Setup (15 min)
2. Phase 2: Component (skip tests initially) (1.5 hours)
3. Phase 3: State (30 min)
4. Phase 4: Integration (15 min)
5. Phase 5: Manual Test Case 1 only (15 min)
6. Phase 7: Minimal docs (30 min)
7. Phase 8: PR (30 min)

**Total MVP**: ~4 hours (then add tests, accessibility, full testing)

---

## Parallel Opportunities

**Within Phase 2** (after component structure defined):
- T019 (CSS file) ∥ T013-T018 (component logic)

**Within Phase 5** (manual tests):
- T031-T036 can be executed in any order (independent test cases)

**Within Phase 6** (cross-browser tests):
- T039 (browsers) can test in parallel across devices

---

## Notes

- **TDD**: Write tests (T005-T012) BEFORE implementing component (T013-T018)
- **No backend changes**: This is frontend-only, reuses existing API endpoints
- **Component reuse**: GPXUploader used as-is (zero modifications)
- **Backward compatibility**: Editing trips skips modal (uses direct navigation)
- **Accessibility**: WCAG 2.1 AA compliance mandatory (focus trap, ARIA, keyboard nav)
- **Spanish text**: All user-facing messages must be in Spanish
- **Mobile-first**: Test on 375px width viewport (iPhone SE)
- **Error handling**: Trip creation never fails due to GPX upload errors

---

## Success Criteria Summary

**Implementation**:
- ✅ 50/50 tasks complete
- ✅ All acceptance criteria met (4 user stories)
- ✅ All manual tests passing (6 test cases)
- ✅ TypeScript: Zero errors
- ✅ Unit tests: ≥90% coverage

**Deployment**:
- ✅ PR merged to develop
- ✅ No regressions on develop branch
- ✅ Feature documented in CLAUDE.md

**User Impact** (measure after 1 week in production):
- Target: ≥30% of trips created with GPX via modal
- Target: ≥80% upload completion rate
- Target: <5% error rate on modal uploads
- Target: Positive user feedback

---

## Total Tasks: 50 tasks across 8 phases

**Estimated Effort**: 0.5-1 day (4-8 hours)

**Breakdown**:
- Phase 1: Setup (15 min)
- Phase 2: Component (3 hours)
- Phase 3: State (1 hour)
- Phase 4: Integration (30 min)
- Phase 5: E2E Testing (1.5 hours)
- Phase 6: Accessibility (1 hour)
- Phase 7: Documentation (30 min)
- Phase 8: PR (30 min)

**Status**: ⏸️ NOT STARTED - Ready for implementation
