# Trip Management Manual Testing

Manual QA testing procedures for Travel Diary trip management features.

**Consolidated from**: `specs/008-travel-diary-frontend/TESTING_GUIDE.md` (Phase 3)

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Trip List Testing](#trip-list-testing)
- [Trip Details Testing](#trip-details-testing)
- [Trip Actions Testing](#trip-actions-testing)
- [Gallery and Map Testing](#gallery-and-map-testing)
- [Error Handling Testing](#error-handling-testing)
- [Responsive Design Testing](#responsive-design-testing)
- [Integration Workflows](#integration-workflows)

---

## Overview

This guide consolidates manual testing procedures for the Travel Diary frontend feature:

- **Trip List** - Browse, filter, and search trips
- **Trip Details** - View full trip information with gallery and map
- **Trip Actions** - Publish and delete trips (owner only)
- **Media Display** - Photo gallery with lightbox and interactive maps
- **Responsive Design** - Mobile, tablet, and desktop layouts

**Test Environment**: Local development (`http://localhost:5173`)

---

## Prerequisites

### 1. Start Backend Server

```bash
# Option A: LOCAL-DEV (SQLite - Recommended)
cd backend
./run-local-dev.sh              # Linux/Mac
.\run-local-dev.ps1             # Windows PowerShell

# Backend must be running at: http://localhost:8000
```

### 2. Start Frontend Server

```bash
cd frontend
npm run dev

# Frontend must be running at: http://localhost:5173
```

### 3. Test User Credentials

**Default test user** (auto-created during setup):
- Username: `testuser`
- Password: `TestPass123!`

**Admin user**:
- Username: `admin`
- Password: `AdminPass123!`

---

## Trip List Testing

### Test Case: TL-TC001 - View Trip List

**Objective**: Verify trips display in responsive grid layout

**Steps**:
1. Navigate to `http://localhost:5173/trips`
2. Login with test credentials if prompted
3. Verify page loads with "Mis Viajes" title
4. Verify subtitle: "Explora, organiza y comparte tus aventuras en bicicleta"

**Expected Result**:
- ✅ Trips display in grid (3 columns desktop, 2 tablet, 1 mobile)
- ✅ Each card shows: thumbnail, title, date range, distance, tags, difficulty badge
- ✅ Draft trips show "BORRADOR" badge (owner only)
- ✅ Loading state shows skeleton cards with pulse animation
- ✅ Pagination appears if more than 12 trips

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TL-TC002 - Trip Card Elements

**Objective**: Verify trip card displays all metadata correctly

**Steps**:
1. On trips list page, inspect a single trip card
2. Verify thumbnail image (or placeholder if no photo)
3. Check date range format (Spanish: "1-5 jun 2024")
4. Check distance display (e.g., "320.5 km")
5. Check tags (max 3 visible, "+N más" if more)
6. Verify difficulty badge color matches level

**Expected Result**:
- ✅ Thumbnail: 280×200px, cropped correctly
- ✅ Title: Truncated with ellipsis if too long
- ✅ Dates: Spanish month abbreviations
- ✅ Distance: With "km" unit
- ✅ Tags: Clickable links (max 3 shown)
- ✅ Difficulty: Green (Fácil), Yellow (Moderado), Orange (Difícil), Red (Extremo)
- ✅ Hover effect: Card elevates with shadow
- ✅ Click: Navigates to `/trips/{trip_id}`

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TL-TC003 - Search Filter

**Objective**: Verify text search filters trips in real-time

**Steps**:
1. On trips list, type "pirineos" in search field
2. Wait 300ms for debounce
3. Verify only trips containing "pirineos" in title/description appear
4. Clear search field
5. Verify all trips reappear

**Expected Result**:
- ✅ Search debounces (300ms delay)
- ✅ Results filter by title and description
- ✅ Counter updates: "Mostrando X de Y viajes"
- ✅ Empty state if no matches: "No se encontraron viajes"
- ✅ Clear button resets filter

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TL-TC004 - Tag Filter

**Objective**: Verify trips filter by selected tag

**Steps**:
1. Click "Todas las etiquetas" dropdown
2. Select a tag (e.g., "bikepacking")
3. Verify only trips with that tag appear
4. Verify trip counter updates
5. Select "Todas las etiquetas" to clear

**Expected Result**:
- ✅ Dropdown shows all available tags
- ✅ Filter applies immediately on selection
- ✅ Counter updates correctly
- ✅ URL updates with `?tag=bikepacking`
- ✅ Clearing filter shows all trips again

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TL-TC005 - Status Filter (Owner Only)

**Objective**: Verify trips filter by draft/published status

**Prerequisites**: User must own trips

**Steps**:
1. Click "Todos los estados" dropdown
2. Verify options: "Todos", "Borrador", "Publicado"
3. Select "Borrador"
4. Verify only draft trips appear with "BORRADOR" badge
5. Select "Publicado"
6. Verify only published trips appear (no badges)

**Expected Result**:
- ✅ Status filter only visible for own trips
- ✅ Draft filter shows only drafts
- ✅ Published filter shows only published trips
- ✅ URL updates with `?status=draft` or `?status=published`

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TL-TC006 - Combined Filters

**Objective**: Verify multiple filters work together (AND logic)

**Steps**:
1. Enter search: "montaña"
2. Select tag: "bikepacking"
3. Select status: "Publicado"
4. Verify only trips matching ALL criteria appear
5. Verify counter reflects combined results

**Expected Result**:
- ✅ Filters combine with AND logic
- ✅ URL contains all query params: `?search=montaña&tag=bikepacking&status=published`
- ✅ Counter accurate
- ✅ Empty state if no matches

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TL-TC007 - Pagination

**Objective**: Verify pagination controls for large trip lists

**Prerequisites**: User must have more than 12 trips

**Steps**:
1. Verify pagination appears at bottom
2. Check "Página 1 de N" display
3. Click "Siguiente" button
4. Verify page 2 loads with next 12 trips
5. Click page number directly
6. Click "Anterior" to go back

**Expected Result**:
- ✅ Pagination shows if >12 trips
- ✅ Page numbers are clickable
- ✅ "Anterior" disabled on page 1
- ✅ "Siguiente" disabled on last page
- ✅ URL updates with `?offset=12`
- ✅ Pagination resets to page 1 when filters change

**Actual Result**: _[To be filled during test execution]_

---

## Trip Details Testing

### Test Case: TD-TC001 - View Trip Details

**Objective**: Verify trip detail page displays all information

**Steps**:
1. From trips list, click any trip card
2. Verify URL: `http://localhost:5173/trips/{trip_id}`
3. Verify page loads with all sections

**Expected Result**:
- ✅ Hero image: First photo (500px height) or placeholder
- ✅ Title: Large and prominent
- ✅ Metadata: Date range, distance, difficulty badge
- ✅ Description: HTML rendered correctly
- ✅ Tags: Clickable links (if exists)
- ✅ Gallery: Photo grid with lightbox (if photos exist)
- ✅ Map: Interactive map with markers (if locations exist)
- ✅ "Volver a Mis Viajes" button at bottom

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TD-TC002 - Draft Trip Badge (Owner Only)

**Objective**: Verify draft badge appears for unpublished trips

**Prerequisites**: User must own a draft trip

**Steps**:
1. Navigate to a draft trip detail page
2. Verify "BORRADOR" badge in top-left of hero image
3. Logout and attempt to view same trip URL
4. Verify badge does not appear (or trip is not accessible)

**Expected Result**:
- ✅ Badge visible to owner on draft trips
- ✅ Badge not visible on published trips
- ✅ Badge styled with yellow background
- ✅ Non-owners cannot see draft trips (403 or 404)

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TD-TC003 - Owner Action Buttons

**Objective**: Verify owner-only buttons appear correctly

**Prerequisites**: User must own a trip

**Steps**:
1. Navigate to own trip (draft)
2. Verify "Publicar" button appears (green)
3. Verify "Eliminar" button appears (red)
4. Navigate to own published trip
5. Verify "Publicar" button does NOT appear
6. Verify "Eliminar" button still appears
7. Navigate to another user's trip
8. Verify NO action buttons appear

**Expected Result**:
- ✅ "Publicar" only visible for own drafts
- ✅ "Eliminar" only visible for own trips
- ✅ No buttons for trips owned by others
- ✅ Buttons stacked vertically on mobile

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TD-TC004 - Description HTML Rendering

**Objective**: Verify trip description renders HTML safely

**Steps**:
1. View trip with formatted description (paragraphs, lists, links)
2. Verify HTML elements render correctly
3. Verify links are clickable
4. Verify no XSS vulnerabilities (script tags sanitized)

**Expected Result**:
- ✅ Paragraphs (`<p>`) render with spacing
- ✅ Lists (`<ul>`, `<ol>`) render with bullets/numbers
- ✅ Links (`<a>`) are clickable
- ✅ Script tags are sanitized (not executed)

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TD-TC005 - Tags Navigation

**Objective**: Verify clicking tags filters trips list

**Steps**:
1. On trip detail page, click a tag (e.g., "bikepacking")
2. Verify navigation to `/trips?tag=bikepacking`
3. Verify trips list shows only trips with that tag

**Expected Result**:
- ✅ Click navigates to filtered trips list
- ✅ Filter persists in URL
- ✅ Tag appears as active filter

**Actual Result**: _[To be filled during test execution]_

---

## Trip Actions Testing

### Test Case: TA-TC001 - Publish Trip (Validation Error)

**Objective**: Verify publish validation for minimum description length

**Prerequisites**: Own a draft trip with description <50 characters

**Steps**:
1. Navigate to draft trip with short description
2. Click "Publicar" button
3. Verify error toast appears

**Expected Result**:
- ✅ Toast error: "La descripción debe tener al menos 50 caracteres para publicar"
- ✅ Trip remains in draft status
- ✅ Button returns to "Publicar" state

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TA-TC002 - Publish Trip (Success)

**Objective**: Verify successful trip publication

**Prerequisites**: Own a draft trip with description ≥50 characters

**Steps**:
1. Navigate to valid draft trip
2. Click "Publicar" button
3. Wait for API call to complete
4. Verify UI updates

**Expected Result**:
- ✅ Button changes to "Publicando..." (disabled)
- ✅ Toast success: "Viaje publicado correctamente"
- ✅ "BORRADOR" badge disappears
- ✅ "Publicar" button disappears
- ✅ Trip now visible in "Publicado" filter
- ✅ Trip visible to other users

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TA-TC003 - Delete Trip (Cancel)

**Objective**: Verify delete confirmation can be cancelled

**Prerequisites**: Own any trip

**Steps**:
1. On trip detail page, click "Eliminar" button
2. Verify browser confirmation dialog appears
3. Click "Cancelar" in dialog

**Expected Result**:
- ✅ Confirmation message: "¿Estás seguro de que quieres eliminar este viaje? Esta acción no se puede deshacer."
- ✅ Trip is NOT deleted
- ✅ User remains on trip detail page

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: TA-TC004 - Delete Trip (Confirm)

**Objective**: Verify trip deletion and cascading deletes

**Prerequisites**: Own a trip (preferably with photos)

**Steps**:
1. Note trip ID and photo count
2. Click "Eliminar" button
3. Click "Aceptar" in confirmation dialog
4. Wait for deletion to complete

**Expected Result**:
- ✅ Button changes to "Eliminando..." (disabled)
- ✅ Toast success: "Viaje eliminado correctamente"
- ✅ Redirect to `/trips`
- ✅ Trip no longer appears in list
- ✅ Photos deleted from storage (cascade)
- ✅ Locations deleted from database (cascade)
- ✅ User stats updated (trip count, total distance)

**Actual Result**: _[To be filled during test execution]_

---

## Gallery and Map Testing

### Test Case: GM-TC001 - Photo Gallery Grid

**Objective**: Verify photo gallery displays correctly

**Prerequisites**: Trip must have photos

**Steps**:
1. Navigate to trip with photos
2. Scroll to gallery section
3. Verify grid layout
4. Count visible thumbnails

**Expected Result**:
- ✅ Section title: "Galería de Fotos (N)"
- ✅ Grid: 3 columns (desktop), 2 (tablet), 1 (mobile)
- ✅ Thumbnails: Square aspect ratio (object-fit: cover)
- ✅ Max 12 photos shown initially
- ✅ "Ver todas las fotos (N)" button if >12 photos
- ✅ Hover effect on thumbnails

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GM-TC002 - Lightbox Navigation

**Objective**: Verify lightbox photo viewer functionality

**Prerequisites**: Trip must have multiple photos

**Steps**:
1. In gallery, click any thumbnail (e.g., photo #3)
2. Verify lightbox opens in fullscreen
3. Use navigation controls:
   - Click right arrow → next photo
   - Click left arrow → previous photo
   - Click thumbnail strip → jump to photo
4. Press ESC key
5. Verify lightbox closes

**Expected Result**:
- ✅ Lightbox opens with clicked photo
- ✅ Navigation arrows work
- ✅ Thumbnail strip shows all photos
- ✅ Keyboard arrows work (left/right)
- ✅ Zoom controls work (mouse wheel)
- ✅ Fullscreen button works
- ✅ Close button (X) works
- ✅ ESC key closes lightbox
- ✅ Captions display if present

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GM-TC003 - Interactive Map

**Objective**: Verify map displays locations and route

**Prerequisites**: Trip must have locations with GPS coordinates

**Steps**:
1. Scroll to "Ruta y Ubicaciones" section
2. Verify map loads (OpenStreetMap tiles)
3. Test map interactions:
   - Zoom in/out with buttons
   - Zoom with mouse wheel
   - Pan by dragging
4. Click on a marker
5. Verify popup appears

**Expected Result**:
- ✅ Map loads with OpenStreetMap tiles
- ✅ Zoom controls work
- ✅ Pan/drag works
- ✅ Markers: Numbered, one per location
- ✅ Popup shows: Number + location name + trip title
- ✅ Polyline: Blue dashed line connecting locations (if ≥2)
- ✅ Auto-zoom: Fits all markers in view

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GM-TC004 - Location List

**Objective**: Verify locations list below map

**Prerequisites**: Trip must have locations

**Steps**:
1. Below map, verify "Ubicaciones (N)" section
2. Check that each location has:
   - Numbered circle (blue)
   - Location name
3. Verify order matches map markers

**Expected Result**:
- ✅ Section title shows count
- ✅ Locations ordered by sequence
- ✅ Numbers match map markers
- ✅ Names display correctly

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GM-TC005 - No Media Fallbacks

**Objective**: Verify appropriate messages when media is missing

**Steps**:
1. Navigate to trip with NO photos
2. Verify gallery section does not appear
3. Navigate to trip with NO locations
4. Verify map section does not appear

**Expected Result**:
- ✅ No "Galería de Fotos" section if no photos
- ✅ No "Ruta y Ubicaciones" section if no locations
- ✅ Sections are conditionally rendered

**Actual Result**: _[To be filled during test execution]_

---

## Error Handling Testing

### Test Case: EH-TC001 - Session Expired (401)

**Objective**: Verify redirect on expired session

**Steps**:
1. Open DevTools → Application → Cookies
2. Delete authentication cookie
3. Navigate to any trip detail page

**Expected Result**:
- ✅ Toast error: "Tu sesión ha expirado. Por favor inicia sesión nuevamente."
- ✅ Redirect to `/login`
- ✅ Return URL preserved for post-login redirect

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: EH-TC002 - Trip Not Found (404)

**Objective**: Verify error page for invalid trip ID

**Steps**:
1. Navigate to: `http://localhost:5173/trips/00000000-0000-0000-0000-000000000000`
2. Wait for page to load

**Expected Result**:
- ✅ Error page with warning icon
- ✅ Title: "Viaje no encontrado"
- ✅ Message: "El viaje que buscas no existe o fue eliminado"
- ✅ "Volver a Mis Viajes" button
- ✅ Button navigates to `/trips`

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: EH-TC003 - Permission Denied (403)

**Objective**: Verify error for accessing other user's draft

**Prerequisites**: Another user's draft trip ID

**Steps**:
1. Attempt to navigate to another user's draft trip
2. Verify access denied

**Expected Result**:
- ✅ Toast error: "No tienes permiso para ver este viaje"
- ✅ Error page or redirect to trips list

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: EH-TC004 - Loading States

**Objective**: Verify loading skeletons during data fetch

**Steps**:
1. Navigate to trips list (throttle network in DevTools to "Slow 3G")
2. Observe loading state
3. Navigate to trip detail page
4. Observe loading state

**Expected Result**:
- ✅ **Trips List**: 12 skeleton cards in grid with pulse animation
- ✅ **Trip Detail**: Skeleton for hero, title, metadata, description
- ✅ No content flash (skeleton appears immediately)
- ✅ Smooth transition to actual content

**Actual Result**: _[To be filled during test execution]_

---

## Responsive Design Testing

### Test Case: RD-TC001 - Desktop Layout (>1024px)

**Objective**: Verify optimal desktop experience

**Steps**:
1. Set browser width to 1440px
2. Navigate through trips list and detail pages

**Expected Result**:
- ✅ Trips grid: 3 columns
- ✅ Hero image: 500px height
- ✅ Gallery: 3 columns
- ✅ Map: 400px height
- ✅ Action buttons: Horizontal layout

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: RD-TC002 - Tablet Layout (768px - 1023px)

**Objective**: Verify tablet-optimized layout

**Steps**:
1. Set browser width to 768px (DevTools → iPad)
2. Navigate through trips list and detail pages

**Expected Result**:
- ✅ Trips grid: 2 columns
- ✅ Hero image: 400px height
- ✅ Gallery: 2 columns
- ✅ Map: 350px height
- ✅ Metadata: Still horizontal

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: RD-TC003 - Mobile Layout (<768px)

**Objective**: Verify mobile-optimized layout

**Steps**:
1. Set browser width to 375px (DevTools → iPhone)
2. Navigate through trips list and detail pages
3. Test all interactions with touch

**Expected Result**:
- ✅ Trips grid: 1 column
- ✅ Hero image: 300px height
- ✅ Gallery: 1 column
- ✅ Map: 300px height
- ✅ Action buttons: Stacked vertically (100% width)
- ✅ Metadata: Stacked vertically
- ✅ Touch targets: ≥44px (iOS guidelines)
- ✅ No horizontal scroll

**Actual Result**: _[To be filled during test execution]_

---

## Integration Workflows

### Workflow 1: Browse → Filter → View → Return

**Objective**: Test complete navigation flow with filter persistence

**Steps**:
1. Go to `/trips`
2. Enter search: "montaña"
3. Select tag: "bikepacking"
4. Verify filtered results
5. Click a trip from results
6. View trip details
7. Scroll through gallery and map
8. Click "Volver a Mis Viajes"

**Expected Result**:
- ✅ Returns to `/trips` with filters preserved in URL
- ✅ Search and tag filter still active
- ✅ Same filtered results displayed

**Actual Result**: _[To be filled during test execution]_

---

### Workflow 2: View Gallery → Lightbox → Map

**Objective**: Test media interaction flow

**Steps**:
1. On trip detail page, scroll to gallery
2. Click photo #3
3. Navigate to photo #5 with arrows
4. Zoom in/out
5. Close lightbox (ESC)
6. Scroll down to map
7. Click marker #2
8. Verify popup displays

**Expected Result**:
- ✅ Smooth transitions between states
- ✅ No layout shifts
- ✅ All interactions work correctly
- ✅ Lightbox closes cleanly
- ✅ Map remains interactive after gallery use

**Actual Result**: _[To be filled during test execution]_

---

### Workflow 3: Draft → Publish → Delete

**Objective**: Test complete trip lifecycle

**Prerequisites**: Own a draft trip with valid data

**Steps**:
1. Navigate to draft trip
2. Verify "BORRADOR" badge and "Publicar" button
3. Click "Publicar"
4. Verify success and badge removal
5. Verify trip now in "Publicado" filter
6. Click "Eliminar"
7. Confirm deletion
8. Verify redirect and removal from list

**Expected Result**:
- ✅ Publish updates UI immediately
- ✅ Status filter reflects change
- ✅ Delete cascades to photos and locations
- ✅ Stats update correctly
- ✅ All toasts display appropriate messages

**Actual Result**: _[To be filled during test execution]_

---

## Quality Checklist

### Accessibility
- [ ] All buttons have `aria-label` attributes
- [ ] Images have descriptive `alt` text
- [ ] Keyboard navigation works (Tab, Enter, ESC)
- [ ] Focus indicators are visible
- [ ] Screen reader announces state changes

### Performance
- [ ] Trips list loads in <2 seconds
- [ ] Trip detail page loads in <1 second
- [ ] Map lazy-loads (only when scrolled into view)
- [ ] Images use `object-fit` to prevent layout shift
- [ ] No unnecessary re-renders

### UX
- [ ] All text in Spanish
- [ ] Error messages are clear and actionable
- [ ] Toasts auto-dismiss (3-5 seconds)
- [ ] Buttons show loading states ("Publicando...", "Eliminando...")
- [ ] Empty states have helpful messages and illustrations

---

## Known Issues (Fixed)

### ✅ Issue #1: TripCard - tag_names undefined
**Symptom**: `Uncaught TypeError: Cannot read properties of undefined (reading 'length')`
**Cause**: Backend returned `tag_names: undefined` instead of `tag_names: []`
**Fix**: Added null check in TripCard component

### ✅ Issue #2: Error 401 shows "Viaje no encontrado"
**Symptom**: Session expired showed generic message
**Cause**: Error handling didn't distinguish between 401 and 404
**Fix**: Added specific 401 handling with redirect to login

---

## Related Documentation

- **[API Reference: Trips](../../api/endpoints/trips.md)** - Trip endpoints specification
- **[E2E Tests](../frontend/e2e-tests.md)** - Automated Playwright tests
- **[Accessibility Testing](../frontend/accessibility.md)** - WCAG 2.1 AA compliance
- **[User Guide: Creating Trips](../../user-guides/trips/creating-trips.md)** - End-user guide

---

**Last Updated**: 2026-02-07 (Consolidated from specs/008-travel-diary-frontend/)
**Features Tested**: Trip List, Trip Details, Publish/Delete, Gallery, Interactive Maps
**Test Environment**: Local development (SQLite backend, React frontend)
