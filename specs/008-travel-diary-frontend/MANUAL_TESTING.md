# Manual Testing Guide - Travel Diary Frontend

**Feature**: 008 - Travel Diary Frontend
**Version**: 1.0
**Last Updated**: 2026-01-10

## Purpose

This guide provides step-by-step manual testing procedures for all user stories in the Travel Diary Frontend feature. Use this guide to verify that the implementation meets all functional requirements and success criteria defined in [spec.md](spec.md).

## Prerequisites

Before starting testing:

1. **Backend running**: Ensure Feature 002 backend is running at `http://localhost:8000`
2. **Frontend running**: Start frontend dev server at `http://localhost:5173`
3. **Test users created**: Have at least 2 verified users for testing ownership/permissions
4. **Test data**: Create sample trips with various states (draft, published) and content

### Test User Accounts

```bash
# User 1 (testuser)
Username: testuser
Email: test@example.com
Password: TestPass123!

# User 2 (maria_garcia)
Username: maria_garcia
Email: maria@example.com
Password: SecurePass456!
```

---

## User Story 1: View Trip List with Filters (Priority: P1)

**Goal**: Browse trips with tag filters, keyword search, and pagination

### Test Case 1.1: View Trip List

**Steps**:
1. Navigate to `http://localhost:5173/trips`
2. Verify grid of trip cards displays (12 per page max)
3. Check each card shows:
   - Thumbnail image (or placeholder if no photos)
   - Trip title
   - Date range (formatted)
   - Distance (if available)
   - Difficulty badge with color:
     - Easy: green (#d1fae5)
     - Moderate: orange (#fed7aa)
     - Difficult: red (#fecaca)
     - Very Difficult: dark red (#fee2e2)
   - Tags as clickable chips

**Expected Result**: ✅ All trips display with complete metadata

**Success Criteria**: SC-001 (Trip list loads in <2s)

---

### Test Case 1.2: Filter Trips by Tag

**Steps**:
1. On trips list page, click a tag chip (e.g., "bikepacking")
2. Verify:
   - URL updates to `/trips?tag=bikepacking`
   - Only trips with that tag display
   - Filter updates in <500ms (SC-008)
   - Tag chip shows active state

**Expected Result**: ✅ List filters to matching trips instantly

---

### Test Case 1.3: Keyword Search

**Steps**:
1. Type "Pirineos" in search input
2. Press Enter or click Search
3. Verify:
   - Only trips with "Pirineos" in title or description display
   - Search persists when navigating back/forward
   - Empty state shows if no matches

**Expected Result**: ✅ Search finds relevant trips

---

### Test Case 1.4: Pagination

**Steps**:
1. Navigate to trips list with >12 trips
2. Verify pagination controls appear at bottom
3. Click "Next" button
4. Verify:
   - Second page of trips loads
   - URL updates with page parameter
   - "Previous" button becomes enabled
   - Page number indicator updates

**Expected Result**: ✅ Pagination works smoothly

---

### Test Case 1.5: Empty State

**Steps**:
1. Apply filters that match no trips
2. Verify:
   - Empty state message displays
   - Helpful text suggests clearing filters
   - Illustration or icon shown

**Expected Result**: ✅ User-friendly empty state

---

## User Story 2: View Trip Details (Priority: P1)

**Goal**: Display complete trip information with gallery and map

### Test Case 2.1: View Trip Details

**Steps**:
1. Click any trip card from list
2. Verify trip detail page shows:
   - Hero image (first photo or placeholder)
   - Trip title
   - Metadata: date range, distance, difficulty badge
   - Full HTML description (line breaks preserved)
   - Tags as clickable chips
   - Photo gallery (if photos exist)
   - Map (if locations exist)

**Expected Result**: ✅ Complete trip details display

**Success Criteria**: SC-002 (Detail page loads in <1.5s)

---

### Test Case 2.2: Photo Gallery Lightbox

**Steps**:
1. On trip detail page, click a photo in gallery
2. Verify lightbox opens with:
   - Current photo at full resolution
   - Previous/Next navigation arrows
   - Thumbnail strip at bottom
   - Close button (X) in corner
   - Keyboard navigation works (←/→ arrows)
3. Navigate through photos with arrows
4. Press ESC to close

**Expected Result**: ✅ Lightbox works smoothly

**Success Criteria**: SC-010 (Lightbox transitions in <300ms)

---

### Test Case 2.3: Owner-Only Actions

**Test as Owner**:
1. View your own published trip
2. Verify buttons appear:
   - "Editar" (Edit)
   - "Eliminar" (Delete)

**Test as Owner with Draft**:
1. View your own draft trip
2. Verify buttons appear:
   - "Publicar" (Publish)
   - "Editar" (Edit)
   - "Eliminar" (Delete)
3. Verify draft badge shows on hero image

**Test as Non-Owner**:
1. View someone else's trip
2. Verify NO action buttons appear

**Expected Result**: ✅ Ownership controls work correctly

---

### Test Case 2.4: Map Display

**Prerequisites**: Trip with location data

**Steps**:
1. View trip with locations
2. Verify:
   - Map section appears
   - OpenStreetMap tiles load
   - Markers show for each location
   - Map is interactive (zoom, pan)

**Expected Result**: ✅ Map displays correctly

---

## User Story 3: Create Trip (Multi-Step Form) (Priority: P1)

**Goal**: Create trips using guided 4-step wizard

### Test Case 3.1: Wizard Navigation

**Steps**:
1. Click "Create Trip" button
2. Verify Step 1/4 (Basic Info) displays
3. Fill required fields:
   - Title: "Test Bikepacking Trip"
   - Start Date: Today
   - End Date: Tomorrow
4. Click "Next"
5. Verify Step 2/4 (Story & Tags) displays
6. Fill description (at least 50 chars for publishing)
7. Add tags: "bikepacking", "mountain"
8. Click "Next"
9. Verify Step 3/4 (Photos) displays
10. Click "Next" (skip photos)
11. Verify Step 4/4 (Review) displays summary

**Expected Result**: ✅ Wizard progresses through all steps

**Success Criteria**: SC-009 (Step transitions in <200ms)

---

### Test Case 3.2: Form Validation

**Test Required Fields**:
1. On Step 1, leave title blank
2. Click "Next"
3. Verify error message: "El título es obligatorio"

**Test Date Validation**:
1. Set end_date before start_date
2. Click "Next"
3. Verify error: "La fecha de fin debe ser posterior a la fecha de inicio"

**Test Description Length (for Publishing)**:
1. Complete steps 1-3
2. On Step 4, click "Publish"
3. If description <50 chars, verify error:
   "La descripción debe tener al menos 50 caracteres para publicar"

**Expected Result**: ✅ Validation prevents invalid data

---

### Test Case 3.3: Save as Draft

**Steps**:
1. Complete Step 1 (title + start_date)
2. Navigate to Step 4 (Review)
3. Click "Guardar como Borrador"
4. Verify:
   - Success toast: "Viaje guardado como borrador"
   - Redirect to trips list
   - Draft appears with draft badge
   - Can edit draft later

**Expected Result**: ✅ Draft saves without full validation

---

### Test Case 3.4: Publish Trip

**Prerequisites**: Description ≥50 characters

**Steps**:
1. Complete all 4 steps with valid data
2. Click "Publicar" on Step 4
3. Verify:
   - Success toast: "Viaje publicado correctamente"
   - Redirect to trip detail page
   - Trip status is "published"
   - Photos upload in background (if selected)

**Expected Result**: ✅ Trip publishes successfully

**Success Criteria**: SC-003 (Trip creation completes in <8 minutes)

---

### Test Case 3.5: Unsaved Changes Warning

**Steps**:
1. Start creating a trip
2. Fill some fields
3. Try to navigate away (e.g., click browser back)
4. Verify warning dialog:
   "¿Estás seguro de que quieres salir? Los cambios no guardados se perderán."

**Expected Result**: ✅ Warning prevents accidental data loss

---

### Test Case 3.6: Photo Selection

**Steps**:
1. Navigate to Step 3 (Photos)
2. Click "Seleccionar Fotos" button
3. Select 3 valid JPG/PNG files (<10MB each)
4. Verify:
   - Photos appear as thumbnails with filenames
   - Counter shows "3 / 20 seleccionadas"
   - Can remove photos with X button

**Test Invalid Files**:
1. Try to select .txt file
2. Verify error toast: "[filename] no es una imagen válida"
3. Try to select 15MB file
4. Verify error toast: "[filename] excede el tamaño máximo de 10MB"

**Expected Result**: ✅ Photo validation works

---

## User Story 4: Upload and Manage Trip Photos (Priority: P2)

**Goal**: Upload, reorder, and delete photos

### Test Case 4.1: Photo Upload with Progress

**Steps**:
1. Create or edit a trip
2. On photo step, drag 5 photos (5MB total) into drop zone
3. Verify:
   - Individual progress bars for each photo
   - Chunked upload (3 concurrent)
   - All photos upload in <30s (SC-007)
   - Success checkmarks appear when done

**Expected Result**: ✅ Photos upload with progress tracking

---

### Test Case 4.2: Drag-and-Drop Reordering

**Prerequisites**: Trip with at least 3 uploaded photos

**Steps**:
1. Hover over a photo thumbnail
2. Verify drag handle icon appears (three horizontal lines)
3. Click and drag photo to new position
4. Release mouse
5. Verify:
   - Photo moves to new position instantly
   - Backend API call persists order
   - Order maintained on page reload

**Expected Result**: ✅ Photo reordering works smoothly

---

### Test Case 4.3: Delete Photo with Confirmation

**Steps**:
1. Click X button on a photo thumbnail
2. Verify modal dialog appears:
   - Title: "¿Eliminar foto?"
   - Text: "Esta acción no se puede deshacer..."
   - Buttons: "Cancelar" and "Eliminar"
3. Click "Cancelar"
4. Verify dialog closes, photo remains
5. Click X again, click "Eliminar"
6. Verify:
   - Photo removes from grid
   - Backend API call deletes photo
   - Success indication

**Expected Result**: ✅ Delete confirmation prevents accidents

---

### Test Case 4.4: Failed Upload Retry

**Test Upload Failure**:
1. Simulate network error (disconnect briefly)
2. Try to upload photo
3. Verify:
   - Error icon appears on thumbnail
   - "Retry" button shows
4. Reconnect network
5. Click "Retry"
6. Verify photo uploads successfully

**Expected Result**: ✅ Retry recovers from errors

---

## User Story 5: Edit Existing Trip (Priority: P2)

**Goal**: Edit trip details with optimistic locking

### Test Case 5.1: Edit Trip Form Pre-Fill

**Steps**:
1. View a trip you own
2. Click "Editar" button
3. Verify edit page loads with:
   - All 4 wizard steps
   - Step 1 pre-filled with title, dates, distance, difficulty
   - Step 2 pre-filled with description and tags
   - Step 3 shows existing photos
   - Can navigate between steps with data preserved

**Expected Result**: ✅ Form pre-fills with existing data

---

### Test Case 5.2: Update and Save

**Steps**:
1. Edit trip (e.g., change title to "Updated Title")
2. Navigate to Step 4 (Review)
3. Click "Guardar Cambios"
4. Verify:
   - Success toast: "Viaje actualizado correctamente"
   - Redirect to trip detail page
   - Changes reflect immediately

**Expected Result**: ✅ Updates save successfully

---

### Test Case 5.3: Optimistic Locking Conflict

**Prerequisites**: Need 2 browser windows with same user logged in

**Steps**:
1. Open trip edit page in Window 1
2. Open SAME trip edit page in Window 2
3. In Window 2, make a change and save
4. In Window 1 (now stale), make a different change and try to save
5. Verify 409 Conflict error:
   - Toast error: "El viaje fue modificado por otra sesión. Recarga la página para ver los cambios más recientes."
   - Changes don't save
   - User can refresh to get latest version

**Expected Result**: ✅ Concurrent edits detected

---

### Test Case 5.4: Draft to Published

**Steps**:
1. Edit a draft trip
2. Complete description (≥50 chars)
3. On Step 4, click "Publicar"
4. Verify:
   - Trip status changes to "published"
   - published_at timestamp set
   - Photos upload if not already done

**Expected Result**: ✅ Can publish from edit mode

---

## User Story 6: Delete Trip (Priority: P3)

**Goal**: Delete trips with confirmation

### Test Case 6.1: Delete with Confirmation

**Steps**:
1. View a trip you own
2. Click "Eliminar" button
3. Verify modal dialog appears:
   - Warning icon (red triangle)
   - Title: "¿Eliminar viaje?"
   - Text: "¿Estás seguro de que quieres eliminar este viaje? Esta acción es permanente y eliminará el viaje junto con todas sus fotos. No se puede deshacer."
   - Buttons: "Cancelar" and "Eliminar"
4. Click "Cancelar"
5. Verify dialog closes, trip remains
6. Click "Eliminar" again, click "Eliminar" in dialog
7. Verify:
   - Success toast: "Viaje eliminado correctamente"
   - Redirect to trips list
   - Trip no longer appears

**Expected Result**: ✅ Delete with confirmation works

---

### Test Case 6.2: Cascading Photo Deletion

**Prerequisites**: Trip with 5 photos

**Steps**:
1. Note photo URLs from trip
2. Delete the trip (confirm in dialog)
3. Verify:
   - All 5 photos deleted from backend
   - Photo URLs return 404
   - Storage freed

**Expected Result**: ✅ Photos cascade delete

**Note**: Backend handles this automatically

---

### Test Case 6.3: Permission Check

**Test as Non-Owner**:
1. Try to access `/trips/{someone_else_trip_id}/edit` directly in URL
2. Verify redirect to trip detail page
3. Toast error: "No tienes permiso para editar este viaje"

**Expected Result**: ✅ Non-owners cannot delete

---

## Cross-Cutting Tests

### Test Case X.1: Responsive Design

**Test Mobile (<640px)**:
1. Resize browser to 375px width (iPhone size)
2. Navigate through all pages
3. Verify:
   - Trip cards stack in 1 column
   - Wizard fits on screen
   - Photo grid adjusts to 2 columns
   - Buttons are thumb-friendly (44px min)
   - Text is readable (16px min)

**Test Tablet (640-1023px)**:
1. Resize to 768px width (iPad size)
2. Verify:
   - Trip cards in 2 columns
   - Form layouts adapt gracefully

**Test Desktop (≥1024px)**:
1. Resize to 1440px width
2. Verify:
   - Trip cards in 3 columns
   - Maximum content width (800px for forms)

**Expected Result**: ✅ Responsive on all devices

**Success Criteria**: SC-011 (Responsive at 3 breakpoints)

---

### Test Case X.2: Loading States

**Test List Loading**:
1. Navigate to trips list
2. Verify loading skeleton shows before data loads

**Test Detail Loading**:
1. Navigate to trip detail
2. Verify:
   - Hero skeleton
   - Content placeholders
   - Smooth transition to real data

**Test Form Submitting**:
1. Submit create/edit form
2. Verify "Publicando..." or "Guardando..." button state
3. Button disabled during submission

**Expected Result**: ✅ Loading states prevent confusion

---

### Test Case X.3: Error Handling

**Test Network Error**:
1. Disconnect network
2. Try to load trips list
3. Verify error message in Spanish
4. Reconnect, retry works

**Test 404 Not Found**:
1. Navigate to `/trips/invalid-uuid`
2. Verify:
   - Error page with message
   - "Volver a Mis Viajes" button

**Test 401 Unauthorized**:
1. Let session expire
2. Try to create trip
3. Verify:
   - Redirect to login
   - Toast: "Tu sesión ha expirado..."

**Expected Result**: ✅ Errors handled gracefully

---

### Test Case X.4: Accessibility

**Test Keyboard Navigation**:
1. Use Tab key to navigate trip list
2. Verify:
   - All interactive elements focusable
   - Focus indicators visible
   - Can open lightbox with Enter
   - Can navigate lightbox with arrow keys
   - Can close with Esc

**Test Screen Reader** (if available):
1. Enable screen reader (NVDA/JAWS/VoiceOver)
2. Navigate trip card
3. Verify:
   - Image alt text read correctly
   - Button labels descriptive
   - Form fields have labels

**Expected Result**: ✅ Accessible to all users

**Success Criteria**: SC-012 (Lighthouse Accessibility ≥90)

---

## Performance Benchmarks

Use these tests to validate success criteria:

### SC-001: Trip List Load Time

**Test**:
1. Open DevTools Network tab
2. Clear cache (Ctrl+Shift+Delete)
3. Navigate to `/trips`
4. Measure time from navigation to "DOMContentLoaded"

**Target**: <2 seconds

---

### SC-002: Trip Detail Load Time

**Test**:
1. Open DevTools Network tab
2. Clear cache
3. Click a trip card
4. Measure time to full page render

**Target**: <1.5 seconds

---

### SC-007: Photo Upload Performance

**Test**:
1. Enable Network throttling to "Fast 3G" in DevTools
2. Upload 5 photos (total 5MB)
3. Measure time from first upload start to last completion

**Target**: <30 seconds on 3G

---

### SC-008: Tag Filter Performance

**Test**:
1. On trips list with 50+ trips
2. Click a tag filter
3. Measure time from click to UI update

**Target**: <500ms

---

### SC-009: Form Step Transition

**Test**:
1. Fill Step 1 fields
2. Click "Next"
3. Measure time to Step 2 render

**Target**: <200ms

---

### SC-010: Lightbox Photo Transition

**Test**:
1. Open lightbox
2. Click "Next" arrow
3. Measure time to next photo display

**Target**: <300ms

---

## Test Execution Checklist

Use this checklist to track testing progress:

### User Stories
- [ ] US1: View Trip List (5 test cases)
- [ ] US2: View Trip Details (4 test cases)
- [ ] US3: Create Trip (6 test cases)
- [ ] US4: Upload Photos (4 test cases)
- [ ] US5: Edit Trip (4 test cases)
- [ ] US6: Delete Trip (3 test cases)

### Cross-Cutting
- [ ] Responsive Design (3 breakpoints)
- [ ] Loading States (3 scenarios)
- [ ] Error Handling (3 scenarios)
- [ ] Accessibility (keyboard + screen reader)

### Performance
- [ ] SC-001: List load <2s
- [ ] SC-002: Detail load <1.5s
- [ ] SC-007: Photo upload <30s (3G)
- [ ] SC-008: Filter update <500ms
- [ ] SC-009: Step transition <200ms
- [ ] SC-010: Lightbox transition <300ms

---

## Reporting Issues

When you find a bug during testing:

1. **Document**:
   - Test case number (e.g., "Test Case 3.2")
   - Steps to reproduce
   - Expected vs actual result
   - Screenshots/video if applicable
   - Browser/device info

2. **Severity**:
   - **Critical**: Feature completely broken
   - **High**: Major functionality impaired
   - **Medium**: Minor functionality issue
   - **Low**: Cosmetic or edge case

3. **File issue** in project tracker with `[Bug]` prefix

---

## Notes

- Test on multiple browsers: Chrome, Firefox, Safari, Edge
- Test with real backend data, not mocks
- Verify both happy paths and error scenarios
- Check console for errors/warnings during testing
- Validate against success criteria (SC-001 to SC-012)

**Happy Testing!** 🧪
