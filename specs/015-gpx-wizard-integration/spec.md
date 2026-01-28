# Feature 015: GPX Wizard Integration

**Status**: Planned (Not Started)
**Priority**: High (UX Enhancement)
**Estimated Effort**: 0.5-1 day
**Related Features**: 003-gps-routes, 008-travel-diary-frontend
**Branch**: `015-gpx-wizard-integration`

---

## Overview

Enable users to upload GPX files immediately after creating a trip through a post-creation modal, improving discoverability and streamlining the trip creation workflow without lengthening the existing 4-step wizard.

### Problem Statement

Current workflow requires two separate steps to create a trip with GPS data:
1. Complete 4-step wizard → create trip
2. Navigate to TripDetailPage → manually find and use GPXUploader

**Pain points**:
- ❌ Fragmented experience (two-step process)
- ❌ Low discoverability (users may not know GPX upload exists)
- ❌ Requires navigation to detail page before uploading
- ❌ Inconsistent with user expectation (photos are also uploaded after wizard)

### Proposed Solution

**Alternativa A: Post-Creation Modal** (Selected after analysis in `specs/003-gps-routes/GPX_WIZARD_INTEGRATION_ANALYSIS.md`)

Show a modal dialog immediately after trip creation asking if the user wants to upload a GPX file now:
- ✅ No wizard extension (keeps 4 steps)
- ✅ Low implementation risk (minimal changes)
- ✅ Optional but visible (improves discoverability)
- ✅ Maintains architectural separation (trip creation vs file uploads)

**Why not other alternatives**:
- **New Step 4 (GPX step)**: Would extend wizard to 5 steps, risk user abandonment (6-8h effort)
- **Combine with Step 3 (Photos + GPX)**: Would overload existing step, confusing UX (4-5h effort)
- **No changes**: Doesn't address discoverability issue (1h effort)

---

## User Stories

### US1: Post-Creation GPX Upload Prompt
**As a** cyclist creating a new trip
**I want** to be prompted to upload a GPX file immediately after creating the trip
**So that** I can complete my trip setup in one continuous workflow

**Acceptance Criteria**:
- AC1: Modal appears automatically after successful trip creation (DRAFT or PUBLISHED)
- AC2: Modal shows clear message: "¿Deseas agregar una ruta GPX a tu viaje?"
- AC3: Two clear options: "Sí, subir ahora" and "No, lo haré después"
- AC4: Modal can be closed with ESC key or clicking overlay
- AC5: Modal is accessible (ARIA labels, keyboard navigation)

### US2: In-Modal GPX Upload
**As a** cyclist who chooses to upload GPX immediately
**I want** to use the familiar GPXUploader interface within the modal
**So that** I don't have to learn a different upload process

**Acceptance Criteria**:
- AC1: Clicking "Sí, subir ahora" shows GPXUploader component inside modal
- AC2: GPXUploader works identically to TripDetailPage version (drag-drop, validation)
- AC3: Upload progress is visible (loading spinner, progress bar)
- AC4: Success message shown: "Archivo GPX procesado correctamente"
- AC5: Modal closes automatically on successful upload
- AC6: User redirected to TripDetailPage with GPX data loaded

### US3: Graceful Error Handling
**As a** cyclist whose GPX upload fails
**I want** to see a clear error message and have the option to try again or skip
**So that** the failed upload doesn't block my trip creation

**Acceptance Criteria**:
- AC1: Upload errors show Spanish error message (file too large, invalid format, etc.)
- AC2: Modal remains open on error (user can retry or cancel)
- AC3: User can select different file after error
- AC4: Clicking "No, lo haré después" or close button navigates to TripDetailPage
- AC5: Trip is NOT deleted if GPX upload fails (upload is truly optional)

### US4: Skip GPX Upload
**As a** cyclist who doesn't have a GPX file ready
**I want** to easily skip the GPX upload prompt
**So that** I can complete trip creation without unnecessary delays

**Acceptance Criteria**:
- AC1: Clicking "No, lo haré después" immediately navigates to TripDetailPage
- AC2: Clicking overlay background closes modal and navigates
- AC3: ESC key closes modal and navigates
- AC4: GPXUploader remains available on TripDetailPage for later upload
- AC5: No negative impact on trip (trip is fully created and valid)

---

## Functional Requirements

### FR-001: Post-Creation Modal Component
**Description**: Create reusable modal component for GPX upload prompt

**Details**:
- Component: `frontend/src/components/trips/PostCreationGPXModal.tsx`
- Props: `{ tripId: string, isOpen: boolean, onClose: () => void, onComplete: () => void }`
- Two states: Initial prompt (buttons) → Upload UI (GPXUploader)
- Modal overlay with backdrop blur
- Centered on screen, mobile-responsive
- Spanish text throughout

### FR-002: State Management Integration
**Description**: Integrate modal into trip creation flow

**Details**:
- Modify `frontend/src/hooks/useTripForm.ts`
- Add state: `showGPXModal` (boolean), `createdTripId` (string | null)
- Modify `handleSubmit`: Show modal instead of immediate navigation
- Add `handleGPXModalClose`: Navigate to TripDetailPage on close

### FR-003: GPXUploader Reuse
**Description**: Reuse existing GPXUploader component without modifications

**Details**:
- Import existing `frontend/src/components/trips/GPXUploader.tsx`
- Pass `tripId` prop (from just-created trip)
- Pass `onUploadComplete` callback (close modal + navigate)
- No changes to GPXUploader internals (maintains consistency)

### FR-004: Navigation Handling
**Description**: Ensure proper navigation after modal interactions

**Details**:
- Success: Close modal → navigate to `/trips/${tripId}`
- Skip: Close modal → navigate to `/trips/${tripId}`
- Error: Keep modal open (allow retry or skip)
- ESC/Overlay: Close modal → navigate to `/trips/${tripId}`

### FR-005: Accessibility Requirements
**Description**: Ensure modal is fully accessible

**Details**:
- ARIA attributes: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`
- Focus trap: Modal captures focus when open
- ESC key: Closes modal
- Screen reader announcements: Modal title and description
- Keyboard navigation: Tab through buttons, Enter to activate

### FR-006: Mobile Responsiveness
**Description**: Optimize modal for mobile devices

**Details**:
- Bottom-aligned on mobile (easier thumb reach)
- Full-width buttons on mobile (stacked vertically)
- Touch-friendly targets (≥44px)
- Viewport-relative sizing (max 90vw, 85vh)

---

## Non-Functional Requirements

### NFR-001: Performance
- **Modal render time**: <100ms (instant appearance)
- **Upload processing**: Same as current GPXUploader (<3s for files <1MB)
- **Navigation after modal**: <200ms to TripDetailPage

### NFR-002: Usability
- **Discoverability**: 100% of users see GPX upload option after trip creation
- **Clarity**: Modal text clear and action-oriented (Spanish)
- **Optionality**: Zero friction to skip GPX upload (1 click)

### NFR-003: Reliability
- **Error handling**: All GPX upload errors gracefully handled
- **Trip integrity**: Trip always created successfully regardless of GPX outcome
- **State consistency**: Modal state properly cleaned up on close

### NFR-004: Maintainability
- **Component reuse**: GPXUploader used as-is (no duplication)
- **Separation of concerns**: Modal handles UI, GPXUploader handles upload logic
- **Type safety**: Full TypeScript types for all props and state

### NFR-005: Backward Compatibility
- **Existing workflow**: TripDetailPage GPX upload still works identically
- **API unchanged**: No backend changes required
- **URL structure**: Navigation paths unchanged

---

## Success Criteria

### SC-001: Implementation Complete
- ✅ PostCreationGPXModal component created with tests
- ✅ useTripForm hook modified with modal state
- ✅ TripCreatePage/TripFormWizard renders modal
- ✅ All 4 user stories acceptance criteria met

### SC-002: User Experience
- ✅ Modal appears within 100ms after trip creation
- ✅ Users can upload GPX without navigating away
- ✅ Users can skip GPX with 1 click
- ✅ Error messages clear and actionable (Spanish)

### SC-003: Technical Quality
- ✅ TypeScript: Zero type errors in new code
- ✅ Accessibility: WCAG 2.1 AA compliant (focus trap, ARIA)
- ✅ Mobile: Works on devices down to 375px width
- ✅ Code review: Approved by at least 1 reviewer

### SC-004: Testing
- ✅ Unit tests: PostCreationGPXModal component (≥90% coverage)
- ✅ Integration test: Full trip creation flow with GPX upload
- ✅ Manual testing: 4 scenarios (upload success, upload error, skip, ESC key)

### SC-005: Documentation
- ✅ CLAUDE.md updated with GPX wizard integration pattern
- ✅ Code comments: Clear explanation of modal state flow
- ✅ No new user documentation needed (feature is self-explanatory)

---

## Out of Scope

**Not included in this feature**:
- ❌ GPX upload during wizard (before trip creation) - blocked by backend constraint (trip_id required)
- ❌ Multiple GPX files per trip - existing limitation (1 GPX per trip)
- ❌ GPX file preview in modal - would add complexity, defer to TripDetailPage
- ❌ Async processing changes - handled by Feature 004 (Celery + Redis)
- ❌ Photo upload in modal - photos already uploaded during wizard
- ❌ Trip editing flow - modal only for creation, not editing

---

## Technical Constraints

### TC-001: Backend Dependency
**Constraint**: GPX upload requires existing `trip_id` (foreign key to trips table)

**Implication**: Cannot upload GPX before trip is created. Modal must appear AFTER successful trip creation.

**Reference**: `backend/src/models/gpx.py` line 40-45

### TC-002: GPXUploader Component Contract
**Constraint**: GPXUploader expects `tripId` prop and `onUploadComplete` callback

**Implication**: Modal must pass valid trip_id from just-created trip.

**Reference**: `frontend/src/components/trips/GPXUploader.tsx`

### TC-003: Existing Upload Endpoint
**Constraint**: No backend changes allowed (use existing `POST /trips/{trip_id}/gpx`)

**Implication**: Modal upload uses same endpoint as TripDetailPage GPXUploader.

**Reference**: `backend/src/api/trips.py` line 1323-1900

---

## Dependencies

### Required Features (Must be Complete)
- ✅ **Feature 003**: GPS Routes Interactive (GPXUploader component exists)
- ✅ **Feature 008**: Travel Diary Frontend (Trip creation wizard exists)

### Optional Features (Nice to Have)
- ⚠️ **Feature 004**: Celery + Redis (improves large file processing)
- ⚠️ **Feature 011**: Frontend Deployment (for production deployment)

---

## Risks and Mitigations

### Risk 1: Modal Perceived as Intrusive
**Likelihood**: Medium
**Impact**: Medium (user frustration)

**Mitigation**:
- Make skip option very visible and 1-click
- Allow ESC key and overlay click to close
- Clear, friendly Spanish text (not pushy)

### Risk 2: GPX Upload Fails but Trip Created
**Likelihood**: Low
**Impact**: Low (trip still valid, can retry later)

**Mitigation**:
- Clear error message: "Puedes intentar de nuevo o subirlo después desde la página del viaje"
- GPXUploader remains available on TripDetailPage
- No data loss (trip persisted successfully)

### Risk 3: State Management Bug
**Likelihood**: Low
**Impact**: Medium (modal doesn't close, navigation broken)

**Mitigation**:
- Thorough testing of all modal close paths
- ESC and overlay click as fallback close mechanisms
- Clear state cleanup in useEffect cleanup function

---

## Metrics for Success

### User Engagement
- **Metric**: % of trips created with GPX uploaded via modal (vs TripDetailPage)
- **Target**: ≥30% of users upload GPX via modal within first week

### Completion Rate
- **Metric**: % of users who click "Sí, subir ahora" and complete upload
- **Target**: ≥80% success rate (exclude user cancellations)

### Discoverability
- **Metric**: % of users aware GPX upload exists (qualitative feedback)
- **Target**: Increase from ~50% (current) to ≥90% (with modal)

### Error Rate
- **Metric**: % of modal GPX uploads that fail
- **Target**: <5% failure rate (same as TripDetailPage)

---

## Alternative Approaches Considered

See `specs/003-gps-routes/GPX_WIZARD_INTEGRATION_ANALYSIS.md` for full analysis.

### Alternative B: Nuevo Step 4 en Wizard
**Rejected**: Would extend wizard to 5 steps, risk user abandonment
**Effort**: 6-8 hours

### Alternative C: GPX en Step 3 (con Fotos)
**Rejected**: Would overload existing step, confusing UX
**Effort**: 4-5 hours

### Alternative D: Sin Cambios
**Rejected**: Doesn't address discoverability issue
**Effort**: 1 hour (banner only)

---

## References

- **GPX Wizard Integration Analysis**: `specs/003-gps-routes/GPX_WIZARD_INTEGRATION_ANALYSIS.md`
- **GPX Upload Implementation**: `specs/003-gps-routes/spec.md` (User Story 1)
- **Trip Creation Wizard**: `specs/008-travel-diary-frontend/spec.md`
- **Backend GPX Endpoints**: `backend/src/api/trips.py` (lines 1323-1900)
- **GPXUploader Component**: `frontend/src/components/trips/GPXUploader.tsx`
- **Trip Form Hook**: `frontend/src/hooks/useTripForm.ts`
