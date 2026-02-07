# Manual QA Guide - Feature 010: Reverse Geocoding

**Feature**: 010-reverse-geocoding
**Date Created**: 2026-01-11
**Phase**: 6 - Final Polish & Validation
**Task**: T054 - Manual QA

## Overview

This document provides a comprehensive manual testing checklist for the Reverse Geocoding feature. Complete all sections to ensure the feature meets quality standards before release.

## Prerequisites

### Environment Setup

1. **Start Backend** (if needed):
   ```bash
   cd backend
   ./run-local-dev.sh  # Linux/Mac
   .\run-local-dev.ps1  # Windows
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   # Access at http://localhost:5173
   ```

3. **Test User Credentials**:
   - **Username**: `testuser`
   - **Password**: `TestPass123!`
   - **Email**: `test@example.com`

4. **Create Test Trip** (if none exists):
   - Login → Dashboard → "Crear viaje"
   - Title: "QA Test Trip"
   - Add basic info → Publish

---

## Test Scenarios

### 1. User Story 1: Click to Add Location

**Test ID**: QA-US1-001
**Priority**: High
**Objective**: Verify map click triggers geocoding and location confirmation

#### Steps:

1. Navigate to `http://localhost:5173`
2. Login with test credentials
3. Go to "Viajes" → Select "QA Test Trip"
4. Click "Editar ubicaciones" button (top right)
5. Click any point on the map (e.g., center of Madrid)

#### Expected Results:

✓ Modal appears within 2 seconds
✓ Loading spinner visible with text "Obteniendo nombre del lugar..."
✓ Spinner disappears after geocoding completes (~1-2 seconds)
✓ Suggested place name appears in Spanish (e.g., "Madrid, España")
✓ Full address displayed (e.g., "Madrid, Comunidad de Madrid, España")
✓ Coordinates shown with 6 decimal precision (e.g., "40.416800", "-3.703800")
✓ Input field is editable and contains suggested name
✓ Character counter shows "X/200" (e.g., "6/200" for "Madrid")
✓ "Confirmar ubicación" button is enabled
✓ "Cancelar" button is present

6. Click "Confirmar ubicación"

✓ Modal closes immediately
✓ New marker appears on map at clicked location
✓ Location appears in sidebar list (right side)
✓ No errors in browser console (F12 → Console)

7. Refresh page (F5)

✓ Location persists (marker still visible)
✓ Location still in sidebar list

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 2. User Story 2: Drag to Adjust Coordinates

**Test ID**: QA-US2-001
**Priority**: High
**Objective**: Verify marker drag updates coordinates with debouncing

#### Steps:

1. In "Editar ubicaciones" mode (from previous test)
2. Drag existing marker to a new position (move ~100-200 meters)
3. Wait 1 second without moving

#### Expected Results:

✓ Marker moves smoothly during drag
✓ NO modal appears immediately (debounce active)
✓ After 1 second of no movement, geocoding occurs
✓ Coordinates in sidebar list update (different lat/lng)
✓ Location name may update if moved to different place

4. Rapidly drag marker multiple times in succession

✓ Only the final position triggers geocoding
✓ No rate limit errors (429) in console
✓ Cache may show HIT logs if dragging to similar positions

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 3. User Story 3: Edit Location Name

**Test ID**: QA-US3-001
**Priority**: High
**Objective**: Verify name editing and validation

#### Steps:

1. Click on map → modal appears with suggested name "Madrid"
2. Edit input to "Mi lugar favorito en Madrid"
3. Click "Confirmar ubicación"

#### Expected Results:

✓ Custom name "Mi lugar favorito en Madrid" appears in sidebar (NOT "Madrid")
✓ Marker popup shows custom name when clicked
✓ Refresh page → custom name persists

4. Click map again → modal appears
5. Clear all text in input (delete everything)

✓ "Confirmar ubicación" button becomes disabled
✓ Error message appears: "El nombre no puede estar vacío"
✓ Input has red border (CSS class `invalid`)
✓ Clicking disabled button does nothing

6. Type "   " (only spaces)

✓ Button remains disabled
✓ Error message still visible

7. Type valid name "Test Location"

✓ Button becomes enabled
✓ Error message disappears
✓ Character counter updates

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 4. Error Handling

#### Test 4.1: Network Failure

**Test ID**: QA-ERR-001
**Priority**: Medium
**Objective**: Verify graceful degradation when network unavailable

**Steps**:

1. Open Chrome DevTools (F12) → Network tab
2. Enable "Offline" mode (throttling dropdown)
3. Click on map

**Expected**:

✓ Modal appears
✓ Loading spinner shows briefly
✓ Error state appears with message "El servidor de mapas no responde. Verifica tu conexión."
✓ Input field is enabled (empty or with fallback)
✓ Message says "Puedes ingresar un nombre manualmente"
✓ User can type manual name
✓ "Confirmar ubicación" works with manual name

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

#### Test 4.2: Invalid Coordinates

**Test ID**: QA-ERR-002
**Priority**: Low
**Objective**: Verify validation of coordinate ranges

**Steps**:

1. Open browser console
2. Execute:
   ```javascript
   // Simulate click with invalid latitude
   const { geocode } = useReverseGeocode();
   await geocode(100, -3.7); // Invalid: lat must be -90 to 90
   ```

**Expected**:

✓ Error thrown with Spanish message
✓ Message contains "Las coordenadas deben estar entre -90 y 90 (latitud), -180 y 180 (longitud)"

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

#### Test 4.3: Ocean/Remote Location

**Test ID**: QA-ERR-003
**Priority**: Low
**Objective**: Verify handling of locations without named places

**Steps**:

1. Click in middle of Atlantic Ocean (far from land)

**Expected**:

✓ Modal appears
✓ Geocoding completes (may take longer)
✓ Suggested name is generic (e.g., "Ocean", "Atlantic Ocean") OR empty
✓ User can enter manual name
✓ Confirmation works

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 5. Accessibility Testing

**Test ID**: QA-A11Y-001
**Priority**: High
**Objective**: Verify WCAG 2.1 AA compliance

#### Test 5.1: Keyboard Navigation

**Steps**:

1. Click "Editar ubicaciones"
2. Use **Tab** key to navigate
3. Press **Enter** when focused on map area (simulate click)

**Expected**:

✓ Can Tab to input field
✓ Can Tab to "Cancelar" button
✓ Can Tab to "Confirmar ubicación" button
✓ Focus outline visible on all elements
✓ **Enter** key on "Confirmar ubicación" submits form
✓ **Esc** key closes modal

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

#### Test 5.2: Screen Reader

**Test ID**: QA-A11Y-002
**Tools**: NVDA (Windows), JAWS, or VoiceOver (Mac)

**Steps**:

1. Enable screen reader
2. Click map → modal opens
3. Tab through modal elements

**Expected Announcements**:

✓ "Confirmar ubicación, dialog" (on modal open)
✓ "Obteniendo nombre del lugar..." (during loading)
✓ "Alert: [error message]" (on error)
✓ "Nombre de la ubicación, edit, has text: Madrid" (input)
✓ "Confirmar y guardar la ubicación, button" (when valid)
✓ "Confirmar ubicación, deshabilitado: nombre inválido, button disabled" (when invalid)
✓ "Cancelar y cerrar el modal, button"

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 6. Mobile Responsiveness

**Test ID**: QA-MOBILE-001
**Priority**: High
**Devices**: iPhone 12, Android phone, or Chrome DevTools device emulation

#### Test 6.1: Mobile Layout

**Steps**:

1. Open site on mobile (or Chrome DevTools → Toggle device toolbar)
2. Select iPhone 12 (390×844)
3. Navigate to trip → "Editar ubicaciones"
4. Click map

**Expected**:

✓ Modal appears from bottom (slides up)
✓ Modal max-height: 85vh (leaves space at top)
✓ Buttons are full-width and stacked vertically
✓ Confirm button appears ABOVE cancel (reverse order from desktop)
✓ Close button (×) is large enough to tap easily (40×40px)
✓ All buttons have minimum 44px touch target height

5. Tap input field

✓ Keyboard appears
✓ Modal doesn't shrink too much (still usable)
✓ Input does NOT zoom in iOS (font-size: 16px)
✓ Can see input while typing

6. Rotate to landscape

✓ Modal still usable
✓ Layout adapts appropriately

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

#### Test 6.2: Tablet Layout

**Test ID**: QA-MOBILE-002
**Device**: iPad (1024×768)

**Steps**:

1. Open on tablet (or DevTools → iPad)
2. Click map

**Expected**:

✓ Modal uses desktop layout (centered, not bottom-aligned)
✓ Buttons are horizontal (side-by-side)
✓ Modal width ~500px (not full width)

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 7. Performance Testing

**Test ID**: QA-PERF-001
**Priority**: Medium
**Objective**: Validate response times and caching

#### Steps:

1. Open Chrome DevTools → Network tab
2. Clear cache (Ctrl+Shift+R)
3. Click on map at coordinates: 40.4168, -3.7038 (Madrid)
4. Note response time in Network tab (look for Nominatim request)

**Expected**:

✓ Request to `nominatim.openstreetmap.org/reverse` completes in <2s
✓ Modal appears immediately (no delay)

5. Cancel modal
6. Click map at nearby coordinates: 40.417, -3.704 (within ~111m)

**Expected**:

✓ NO new network request (cache HIT)
✓ Modal appears instantly (0ms)
✓ Console shows: `[GeoCoding Cache] HIT (50.0% hit rate)...`

7. Open Console → type:
   ```javascript
   geocodingCache.getStats()
   ```

**Expected**:

✓ Returns object with `hits`, `misses`, `hitRate`
✓ `hitRate` > 0% (after at least one cache hit)
✓ `size` <= 100 (cache max size)

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 8. Integration Testing

**Test ID**: QA-INT-001
**Priority**: High
**Objective**: Verify backend persistence

#### Steps:

1. Add location "Integration Test Location"
2. Confirm and verify it appears
3. Open DevTools → Application tab → Storage
4. Check IndexedDB, LocalStorage, SessionStorage

**Expected**:

✓ NO location data in client storage (all server-side)

5. Refresh page (F5)

✓ "Integration Test Location" still visible
✓ Marker in same position

6. Open **new incognito window**
7. Login with same credentials
8. Navigate to same trip

✓ "Integration Test Location" is visible
✓ Confirms server persistence (not local caching)

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 9. Edge Cases

#### Test 9.1: Maximum Name Length

**Test ID**: QA-EDGE-001

**Steps**:

1. Click map → modal opens
2. Type exactly 200 characters in input:
   ```
   AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA
   ```

**Expected**:

✓ All 200 characters accepted
✓ Counter shows "200/200"
✓ Button is enabled

3. Try to type 201st character

✓ Character is NOT added (maxLength enforced)
✓ Counter stays "200/200"

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

#### Test 9.2: Special Characters

**Test ID**: QA-EDGE-002

**Steps**:

1. Enter name: `Café París (España) - año 2024 ñ á é í ó ú ü`
2. Confirm

**Expected**:

✓ All characters accepted
✓ Saves correctly
✓ Displays correctly in sidebar
✓ Refresh → no corruption

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

#### Test 9.3: Rapid Cancel

**Test ID**: QA-EDGE-003

**Steps**:

1. Click map
2. Immediately click "Cancelar" (before geocoding completes)

**Expected**:

✓ Modal closes
✓ NO location added
✓ NO errors in console
✓ Geocoding request may still be in-flight but is ignored

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

#### Test 9.4: Click Outside Modal

**Test ID**: QA-EDGE-004

**Steps**:

1. Click map → modal opens
2. Click on dark overlay (outside modal box)

**Expected**:

✓ Modal closes (same as "Cancelar")
✓ NO location added

3. Click map again
4. Click inside modal content area (but not on buttons)

✓ Modal stays open
✓ Click is absorbed by modal content

**Status**: [ ] Pass [ ] Fail
**Notes**: _____________________

---

### 10. Browser Compatibility

**Test ID**: QA-BROWSER-001
**Priority**: Medium

Test all critical flows (US1, US2, US3) in each browser:

#### Chrome (Latest)

- [ ] US1: Click to Add
- [ ] US2: Drag to Adjust
- [ ] US3: Edit Name
- [ ] Accessibility
- [ ] Mobile Responsive

**Notes**: _____________________

---

#### Firefox (Latest)

- [ ] US1: Click to Add
- [ ] US2: Drag to Adjust
- [ ] US3: Edit Name
- [ ] Accessibility
- [ ] Mobile Responsive

**Notes**: _____________________

---

#### Safari (if available)

- [ ] US1: Click to Add
- [ ] US2: Drag to Adjust
- [ ] US3: Edit Name
- [ ] Accessibility (VoiceOver)
- [ ] Mobile Responsive (iOS)

**Notes**: _____________________

---

#### Edge (if available)

- [ ] US1: Click to Add
- [ ] US2: Drag to Adjust
- [ ] US3: Edit Name

**Notes**: _____________________

---

## Summary Checklist

### Functionality ✓

- [ ] Map click triggers geocoding
- [ ] Modal shows suggested place name
- [ ] Name editing works
- [ ] Validation prevents empty names
- [ ] Location saves to backend
- [ ] Marker drag updates coordinates
- [ ] Debouncing prevents rate limits
- [ ] Cache reduces API calls

### User Experience ✓

- [ ] Loading states visible
- [ ] Error messages in Spanish
- [ ] Graceful degradation (offline mode)
- [ ] Response times <2s
- [ ] No console errors

### Accessibility ✓

- [ ] Keyboard navigation works
- [ ] Screen reader announces states
- [ ] Focus indicators visible
- [ ] ARIA attributes present

### Mobile ✓

- [ ] Bottom-aligned on mobile
- [ ] Touch targets ≥44px
- [ ] No iOS zoom on input focus
- [ ] Keyboard doesn't hide modal

### Performance ✓

- [ ] Cache hit rate >70% after repeated use
- [ ] Debounce prevents duplicate requests
- [ ] Network requests <2s

### Integration ✓

- [ ] Backend persists data
- [ ] Refresh maintains state
- [ ] Cross-session consistency

---

## Bug Template

If you find bugs, document them here:

### Bug #1

**Severity**: [ ] Critical [ ] High [ ] Medium [ ] Low
**Test ID**: QA-XXX-XXX
**Browser**: _____________________
**Device**: _____________________

**Steps to Reproduce**:
1.
2.
3.

**Expected**: _____________________

**Actual**: _____________________

**Screenshot**: (attach if needed)

**Console Errors**: (copy/paste)

---

## Sign-off

**Tester Name**: _____________________
**Date**: _____________________
**Overall Result**: [ ] Pass [ ] Fail (with bugs documented)

**Notes**:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
