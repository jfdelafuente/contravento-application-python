# Frontend Testing Guide - GPS Coordinates (Phases 4 & 5)

**Feature**: 009-gps-coordinates

- **Phase 4**: Frontend UI (LocationInput component)
- **Phase 5**: Map Visualization Enhancements

**Date**: 2026-01-11
**Branch**: `009-gps-coordinates-frontend`

---

## Overview

This guide provides manual testing steps for the GPS Coordinates frontend UI implementation (Phase 4).

### What Was Implemented

1. **LocationInput Component** (`frontend/src/components/trips/TripForm/LocationInput.tsx`)
   - Location name input (required)
   - Latitude input (optional, -90 to 90°, 6 decimal precision)
   - Longitude input (optional, -180 to 180°, 6 decimal precision)
   - Remove location button
   - Real-time validation and error display

2. **Step1BasicInfo Updates** (`frontend/src/components/trips/TripForm/Step1BasicInfo.tsx`)
   - Locations section with "Add Location" button
   - State management for locations array
   - Support for up to 50 locations per trip
   - Custom validation for location names and coordinate pairs

3. **Step4Review Updates** (`frontend/src/components/trips/TripForm/Step4Review.tsx`)
   - Display locations with GPS coordinates in review step
   - Visual formatting with numbered location list

4. **Trip Helpers** (`frontend/src/utils/tripHelpers.ts`)
   - `formatCoordinate()` - Format single coordinate with degree symbol
   - `formatCoordinatePair()` - Format latitude/longitude pair
   - `validateCoordinates()` - Client-side coordinate validation

---

## Validation Rules

**Location Name**:
- ✅ **REQUIRED** - Cannot be empty
- ❌ **Form will not advance** if any location name is empty
- Error: "El nombre de la ubicación es obligatorio"

**GPS Coordinates**:
- ✅ **OPTIONAL** - Both latitude and longitude can be left empty
- ✅ **Both filled** - Valid (latitude: -90 to 90, longitude: -180 to 180)
- ❌ **Only latitude filled** - Invalid, shows error: "Debes proporcionar la longitud si ingresas latitud"
- ❌ **Only longitude filled** - Invalid, shows error: "Debes proporcionar la latitud si ingresas longitud"

**Key Behaviors**:
1. **Location name is always required** to proceed to next step
2. **Coordinates are optional** - you can create locations without GPS data
3. **If you enter coordinates**, both latitude AND longitude must be provided
4. **Custom JavaScript validation** enforces coordinate ranges (-90/90, -180/180)

**Note on Validation Approach**:

- The form uses React Hook Form with custom validation functions
- HTML5 attributes (`min`, `max`) are present but not actively enforced
- Custom JavaScript validation in `validateLocations()` checks ranges before form advancement
- This approach provides consistent validation across all browsers and better error messages

---

## Prerequisites

### 1. Backend Running

```bash
cd backend
./run-local-dev.sh  # or .\run-local-dev.ps1 on Windows
```

Backend should be accessible at: http://localhost:8000

### 2. Frontend Running

```bash
cd frontend
npm run dev
```

Frontend should be accessible at: http://localhost:3001

### 3. Test User Exists

Ensure you have a verified test user:

```bash
cd backend
poetry run python scripts/create_verified_user.py
```

**Default credentials**:
- Username: `testuser`
- Password: `TestPass123!`

---

## Manual Testing Checklist

### Test Suite 1: Location Input Component ✅ COMPLETED

#### T1.1 - Location Name Required ✅ BLOCKS ADVANCEMENT
- [x] **Navigate** to trip creation form (Step 1)
- [x] **Leave** location name field empty
- [x] **Attempt** to move to next step
- [x] **Expected**: Toast error appears: "Por favor completa el nombre de todas las ubicaciones"
- [x] **Expected**: Red error message appears below field: "El nombre de la ubicación es obligatorio"
- [x] **Expected**: Form does NOT advance to Step 2

#### T1.2 - Add Location Button
- [x] **Click** "Añadir Ubicación" button
- [x] **Verify** new location input appears
- [x] **Verify** each location has a number (Ubicación 1, Ubicación 2, etc.)
- [x] **Add** locations until you reach 10
- [x] **Verify** "Añadir Ubicación" button still enabled (max is 50)

#### T1.3 - Remove Location Button
- [x] **Add** 3 locations
- [x] **Click** "Eliminar" on the 2nd location
- [x] **Verify** location is removed
- [x] **Verify** remaining locations renumbered (Ubicación 1, Ubicación 2)
- [x] **Reduce** to 1 location
- [x] **Verify** "Eliminar" button is hidden (minimum 1 location required)

---

### Test Suite 2: GPS Coordinate Input ✅ COMPLETED

#### T2.1 - Valid Coordinates (Madrid)
- [x] **Enter** location name: "Madrid"
- [x] **Enter** latitude: `40.416775`
- [x] **Enter** longitude: `-3.703790`
- [x] **Verify** no error messages appear
- [x] **Proceed** to Step 4 (Review)
- [x] **Verify** coordinates display: "📍 Lat: 40.416775°, Lon: -3.703790°"

#### T2.2 - Valid Coordinates (Barcelona)
- [x] **Enter** location name: "Barcelona"
- [x] **Enter** latitude: `41.385064`
- [x] **Enter** longitude: `2.173404`
- [x] **Verify** coordinates accepted
- [x] **Check** Step 4 shows both Madrid and Barcelona with coordinates

#### T2.3 - Coordinates Without Name (Should Fail)
- [x] **Add** new location
- [x] **Leave** name empty
- [x] **Enter** latitude: `40.0`
- [x] **Enter** longitude: `-3.0`
- [x] **Attempt** to proceed
- [x] **Verify** error: "El nombre de la ubicación es obligatorio"

---

### Test Suite 3: Multiple Locations Management ✅ COMPLETED

#### T3.1 - Add Multiple Locations
- [x] **Add** 5 locations with different names
- [x] **Verify** each location numbered correctly (Ubicación 1, 2, 3, 4, 5)
- [x] **Verify** all "Eliminar" buttons visible (minimum is 1 location)
- [x] **Verify** locations maintain their data when adding new ones

#### T3.2 - Remove Middle Location
- [x] **With** 5 locations present
- [x] **Click** "Eliminar" on location 3
- [x] **Verify** location 3 removed
- [x] **Verify** locations renumbered (former location 4 becomes location 3)
- [x] **Verify** remaining locations keep their data

#### T3.3 - Cannot Remove Last Location
- [x] **Remove** locations until only 1 remains
- [x] **Verify** "Eliminar" button is hidden or disabled
- [x] **Note**: Minimum 1 location required per trip

---

### Test Suite 4: GPS Coordinate Validation ✅ COMPLETED

#### T4.1 - Location Without GPS Coordinates ✅ ALLOWS ADVANCEMENT
- [x] **Enter** location name: "Camino de Santiago"
- [x] **Leave** latitude empty
- [x] **Leave** longitude empty
- [x] **Proceed** to Step 4
- [x] **Expected**: Form advances successfully (coordinates are OPTIONAL)
- [x] **Expected**: Step 4 shows location with: "Sin coordenadas GPS"

#### T4.2 - Mix of Locations (With and Without GPS) ✅ ALLOWS ADVANCEMENT
- [x] **Create** trip with 3 locations:
  1. Madrid (with GPS: 40.416775, -3.703790)
  2. Camino de Santiago (no GPS - both fields empty)
  3. Barcelona (with GPS: 41.385064, 2.173404)
- [x] **Proceed** to Step 4
- [x] **Expected**: Form advances successfully
- [x] **Expected**: Step 4 shows:
  - Location 1: Madrid with coordinates "📍 Lat: 40.416775°, Lon: -3.703790°"
  - Location 2: Camino de Santiago - "Sin coordenadas GPS"
  - Location 3: Barcelona with coordinates "📍 Lat: 41.385064°, Lon: 2.173404°"

#### T4.3 - Partial Coordinates - Only Latitude ❌ BLOCKS ADVANCEMENT
- [x] **Enter** location name: "Test Location"
- [x] **Enter** latitude: `40.0`
- [x] **Leave** longitude empty
- [x] **Attempt** to proceed to next step
- [x] **Expected**: Toast error appears: "Por favor completa el nombre de todas las ubicaciones"
- [x] **Expected**: Red error message appears below longitude field: "Debes proporcionar la longitud si ingresas latitud"
- [x] **Expected**: Form does NOT advance to Step 2

#### T4.4 - Partial Coordinates - Only Longitude ❌ BLOCKS ADVANCEMENT
- [x] **Clear** previous test
- [x] **Enter** location name: "Test Location"
- [x] **Leave** latitude empty
- [x] **Enter** longitude: `-3.0`
- [x] **Attempt** to proceed to next step
- [x] **Expected**: Toast error appears: "Por favor completa el nombre de todas las ubicaciones"
- [x] **Expected**: Red error message appears below latitude field: "Debes proporcionar la latitud si ingresas longitud"
- [x] **Expected**: Form does NOT advance to Step 2

---

### Test Suite 5: Coordinate Range Validation ✅ COMPLETED

#### T5.1 - Latitude Out of Range (Too High)

- [x] **Enter** location name: "Invalid North"
- [x] **Enter** latitude: `100`
- [x] **Enter** longitude: `0`
- [x] **Attempt** to proceed to next step
- [x] **Expected**: Toast error appears: "Por favor completa el nombre de todas las ubicaciones"
- [x] **Expected**: Red error message appears below latitude field: "La latitud debe estar entre -90 y 90 grados"
- [x] **Expected**: Form does NOT advance to Step 2

#### T5.2 - Latitude Out of Range (Too Low)

- [x] **Enter** location name: "Invalid South"
- [x] **Enter** latitude: `-100`
- [x] **Enter** longitude: `0`
- [x] **Attempt** to proceed to next step
- [x] **Expected**: Error message: "La latitud debe estar entre -90 y 90 grados"
- [x] **Expected**: Form does NOT advance to Step 2

#### T5.3 - Longitude Out of Range (Too High)

- [x] **Enter** location name: "Invalid East"
- [x] **Enter** latitude: `0`
- [x] **Enter** longitude: `200`
- [x] **Attempt** to proceed to next step
- [x] **Expected**: Error message: "La longitud debe estar entre -180 y 180 grados"
- [x] **Expected**: Form does NOT advance to Step 2

#### T5.4 - Longitude Out of Range (Too Low)

- [x] **Enter** location name: "Invalid West"
- [x] **Enter** latitude: `0`
- [x] **Enter** longitude: `-200`
- [x] **Attempt** to proceed to next step
- [x] **Expected**: Error message: "La longitud debe estar entre -180 y 180 grados"
- [x] **Expected**: Form does NOT advance to Step 2

#### T5.5 - High Precision Coordinates

- [x] **Enter** location name: "Jaca"
- [x] **Enter** latitude: `42.5700841234567` (13 decimals)
- [x] **Enter** longitude: `-0.5499411234567`
- [x] **Proceed** to Step 4
- [x] **Expected**: Coordinates displayed with 6 decimal precision:
  - Lat: `42.570084°` (rounded)
  - Lon: `-0.549941°` (rounded)

---

### Test Suite 6: Step 4 Review Display ✅ COMPLETED

#### T6.1 - Review Locations Section Exists

- [x] **Create** trip with 2 locations (both with GPS)
- [x] **Navigate** to Step 4 (Review)
- [x] **Verify** "Ubicaciones" section appears after "Información Básica"
- [x] **Verify** section displays before "Descripción"

#### T6.2 - Review Location Numbering

- [x] **Verify** locations numbered with blue circles (1, 2, 3...)
- [x] **Verify** location names displayed prominently
- [x] **Verify** coordinates in monospace font with 📍 icon

#### T6.3 - Review Locations Without GPS

- [x] **Remove** all locations except one
- [x] **Enter** only name: "Test"
- [x] **Navigate** to Step 4
- [x] **Verify** shows: "Test - Sin coordenadas GPS"

---

### Test Suite 7: End-to-End Trip Creation ✅ COMPLETED

#### T7.1 - Create Trip with GPS Coordinates

- [x] **Login** as testuser
- [x] **Navigate** to "Crear Viaje"
- [x] **Step 1 - Basic Info**:
  - Title: "Ruta GPS Test - Madrid a Toledo"
  - Start Date: (today's date)
  - Distance: `130`
  - Difficulty: Moderada
  - Locations:
    1. Madrid - Lat: `40.416775`, Lon: `-3.703790`
    2. Toledo - Lat: `39.862832`, Lon: `-4.027323`
- [x] **Step 2 - Story & Tags**:
  - Description: "Ruta de prueba con coordenadas GPS para validar la integración con el backend."
  - Tags: `gps`, `prueba`
- [x] **Step 3 - Photos**: Skip (no photos)
- [x] **Step 4 - Review**:
  - Verify all locations display with coordinates
  - Click "Publicar Viaje"
- [x] **Verify** trip created successfully
- [x] **Open** browser DevTools → Network tab
- [x] **Inspect** POST request to `/trips`
- [x] **Verify** payload includes:

  ```json
  {
    "locations": [
      {
        "name": "Madrid",
        "latitude": 40.416775,
        "longitude": -3.703790
      },
      {
        "name": "Toledo",
        "latitude": 39.862832,
        "longitude": -4.027323
      }
    ]
  }
  ```

#### T7.2 - Create Trip Without GPS Coordinates

- [x] **Create** new trip
- [x] **Add** 2 locations with names only (no coordinates)
- [x] **Complete** all steps
- [x] **Publish** trip
- [x] **Verify** trip created successfully
- [x] **Verify** locations saved with null coordinates

#### T7.3 - Backend Response Validation

- [x] **After** creating trip with GPS
- [x] **Check** browser DevTools → Network → Response
- [x] **Verify** response includes locations with coordinates:

  ```json
  {
    "success": true,
    "data": {
      "trip_id": "...",
      "locations": [
        {
          "location_id": "...",
          "name": "Madrid",
          "latitude": 40.416775,
          "longitude": -3.703790,
          "sequence": 0
        }
      ]
    }
  }
  ```

---

### Test Suite 8: Accessibility

#### T8.1 - Keyboard Navigation

- [ ] **Use** Tab key to navigate through location inputs
- [ ] **Verify** focus indicators visible on all fields
- [ ] **Tab** to "Añadir Ubicación" button
- [ ] **Press** Enter to add location
- [ ] **Verify** new location input receives focus

#### T8.2 - Screen Reader Labels

- [ ] **Enable** screen reader (NVDA/JAWS on Windows, VoiceOver on Mac)
- [ ] **Navigate** to latitude input
- [ ] **Verify** reads: "Latitud de la ubicación 1, -90 a 90 grados"
- [ ] **Navigate** to longitude input
- [ ] **Verify** reads: "Longitud de la ubicación 1, -180 a 180 grados"

#### T8.3 - Error Announcements

- [ ] **Enter** invalid latitude: `100`
- [ ] **Tab** away from field
- [ ] **Verify** error message announced by screen reader
- [ ] **Verify** aria-invalid="true" on input

---

### Test Suite 9: Responsive Design

#### T9.1 - Mobile View (< 640px)

- [ ] **Resize** browser to 375px width (mobile phone)
- [ ] **Verify** coordinate inputs stack vertically (not side-by-side)
- [ ] **Verify** "Eliminar" button full width
- [ ] **Verify** all text readable without horizontal scroll

#### T9.2 - Tablet View (640px - 1024px)

- [ ] **Resize** to 768px width (tablet)
- [ ] **Verify** coordinate inputs side-by-side in grid
- [ ] **Verify** proper spacing and alignment

---

## Expected Results Summary

### ✅ All Tests Passing Means:

1. **Input Validation**:
   - ✅ Location names **REQUIRED** - form blocks advancement if empty
   - ✅ GPS coordinates **OPTIONAL** - can leave both empty
   - ❌ **Partial coordinates blocked** - if latitude provided, longitude required (and vice versa)
   - ✅ Coordinate range validation (-90/90 latitude, -180/180 longitude)
   - ✅ High precision rounded to 6 decimals for display

2. **Validation Error Messages** (Spanish):
   - "El nombre de la ubicación es obligatorio" - when name empty
   - "Debes proporcionar la longitud si ingresas latitud" - when only latitude filled
   - "Debes proporcionar la latitud si ingresas longitud" - when only longitude filled
   - "La latitud debe estar entre -90 y 90 grados" - when latitude out of range
   - "La longitud debe estar entre -180 y 180 grados" - when longitude out of range
   - Toast: "Por favor completa el nombre de todas las ubicaciones" - when attempting to advance with errors

3. **User Experience**:
   - Add/remove locations seamlessly (minimum 1, maximum 50)
   - Clear error messages in Spanish
   - Coordinates display properly in review step
   - Accessible keyboard navigation
   - "Sin coordenadas GPS" shown for locations without coordinates

4. **Backend Integration**:
   - Coordinates sent in API payload as numbers (or null)
   - Backend accepts and stores coordinates
   - Response includes coordinates in locations array
   - Partial coordinates rejected by validation before reaching backend

5. **Visual Design**:
   - Clean, modern UI with ContraVento colors
   - Responsive on mobile/tablet/desktop
   - Consistent with existing form design
   - Monospace font for coordinates with 📍 icon

---

## Troubleshooting

### Issue: "Añadir Ubicación" button disabled

**Cause**: Reached maximum 50 locations
**Solution**: Remove some locations before adding more

### Issue: Coordinates not appearing in Step 4

**Cause**: Values not persisted in form state
**Solution**: Check browser console for React Hook Form errors

### Issue: Form won't submit with coordinates

**Cause**: Backend validation error
**Solution**: Check Network tab for API error response

### Issue: Coordinates show wrong precision

**Cause**: Backend rounding to 6 decimals
**Solution**: Expected behavior - coordinates rounded server-side

---

## Success Criteria (from PHASE4_PLAN.md)

- [x] SC-F01: Coordinate input fields functional
- [ ] SC-F02: Add/remove locations working
- [ ] SC-F03: Validation displays Spanish errors
- [ ] SC-F04: Review step shows coordinates
- [ ] SC-F05: API payload includes coordinates
- [ ] SC-F06: Backend accepts and returns coordinates
- [ ] SC-F07: Accessible keyboard navigation
- [ ] SC-F08: Mobile responsive design

---

---

## Phase 5: Map Visualization Enhancements Testing

### Test Suite 10: Numbered Markers (Subphase 5.1)

#### T10.1 - Marker Numbering Display

- [ ] **Navigate** to trip detail page with 3+ GPS locations
- [ ] **Verify** map displays with numbered markers (1, 2, 3...)
- [ ] **Check** markers display in sequence order (not creation order)
- [ ] **Verify** marker numbers match location list order below map

#### T10.2 - Marker Popup Content

- [ ] **Click** on marker #1
- [ ] **Verify** popup shows: "1. [Location Name]"
- [ ] **Click** on marker #2
- [ ] **Verify** popup shows: "2. [Location Name]"
- [ ] **Close** popup by clicking map background

#### T10.3 - Single Location Marker

- [ ] **Create** trip with only 1 GPS location
- [ ] **View** trip detail page
- [ ] **Verify** marker shows "1" (numbered even for single location)

---

### Test Suite 11: Error Handling (Subphase 5.2)

#### T11.1 - Tile Loading Error Display

- [ ] **Open** trip detail page with GPS coordinates
- [ ] **Simulate** network failure (DevTools → Network → Offline mode)
- [ ] **Reload** page
- [ ] **Verify** error message displays: "Error al cargar el mapa"
- [ ] **Verify** message shows: "No se pudieron cargar las imágenes del mapa. Verifica tu conexión a internet."
- [ ] **Verify** "Reintentar" button visible

#### T11.2 - Retry Functionality

- [ ] **With** network still offline, click "Reintentar"
- [ ] **Verify** error persists (network still unavailable)
- [ ] **Enable** network (DevTools → Network → Online mode)
- [ ] **Click** "Reintentar" button
- [ ] **Verify** map loads successfully
- [ ] **Verify** markers and polyline display correctly

#### T11.3 - Fallback Location List

- [ ] **When** map error displays
- [ ] **Verify** location list still visible below error message
- [ ] **Verify** list shows all locations with "Sin coordenadas GPS" for text-only entries
- [ ] **Verify** locations with coordinates show formatted lat/lng

#### T11.4 - Error State - No Fullscreen Button

- [ ] **With** map in error state
- [ ] **Verify** fullscreen toggle button NOT visible
- [ ] **After** clicking "Reintentar" and map loads
- [ ] **Verify** fullscreen button appears in top-right corner

---

### Test Suite 12: Fullscreen Mode (Subphase 5.3)

#### T12.1 - Enter Fullscreen Mode

- [ ] **Navigate** to trip detail page with GPS map
- [ ] **Locate** fullscreen button (top-right corner, expand arrows icon)
- [ ] **Verify** button tooltip: "Pantalla completa"
- [ ] **Click** fullscreen button
- [ ] **Verify** map expands to fill entire viewport
- [ ] **Verify** location list hidden in fullscreen
- [ ] **Verify** button icon changes to X (exit fullscreen)

#### T12.2 - Exit Fullscreen Mode

- [ ] **While** in fullscreen mode
- [ ] **Verify** button tooltip now shows: "Salir de pantalla completa (Esc)"
- [ ] **Click** exit fullscreen button (X icon)
- [ ] **Verify** map returns to normal size
- [ ] **Verify** location list reappears below map
- [ ] **Verify** button icon returns to expand arrows

#### T12.3 - Keyboard Shortcut (Escape)

- [ ] **Enter** fullscreen mode
- [ ] **Press** Escape key
- [ ] **Verify** map exits fullscreen
- [ ] **Verify** layout returns to normal

#### T12.4 - Fullscreen State Persistence

- [ ] **Enter** fullscreen mode
- [ ] **Zoom** in on map (mouse wheel or +/- buttons)
- [ ] **Pan** map to different area
- [ ] **Exit** fullscreen
- [ ] **Verify** zoom level maintained
- [ ] **Verify** map center position preserved

#### T12.5 - Dark Mode Support (if enabled)

- [ ] **Enable** browser/OS dark mode
- [ ] **Verify** fullscreen button adapts to dark theme
- [ ] **Enter** fullscreen
- [ ] **Verify** background color appropriate for dark mode

---

### Test Suite 13: Accessibility (Phase 5)

#### T13.1 - Fullscreen Button Accessibility

- [ ] **Use** Tab key to navigate page
- [ ] **Verify** fullscreen button receives focus with visible outline
- [ ] **Press** Enter or Space to activate button
- [ ] **Verify** fullscreen mode toggles
- [ ] **With** screen reader, verify button label announces correctly

#### T13.2 - Marker Keyboard Navigation

- [ ] **Tab** to map container
- [ ] **Use** arrow keys to pan map
- [ ] **Use** +/- keys to zoom
- [ ] **Verify** keyboard navigation works in both normal and fullscreen modes

#### T13.3 - ARIA Labels for Markers

- [ ] **Enable** screen reader
- [ ] **Navigate** to map markers
- [ ] **Verify** each marker announces: "Marcador [number]: [Location Name]"
- [ ] **Verify** popup content announced when opened

#### T13.4 - Error Message Accessibility

- [ ] **Trigger** map error state
- [ ] **With** screen reader, verify error message announced
- [ ] **Verify** "Reintentar" button has clear label
- [ ] **Verify** error region has aria-live="polite" for dynamic updates

---

### Test Suite 14: Responsive Design (Phase 5)

#### T14.1 - Mobile View (< 640px) - Map Display

- [ ] **Resize** browser to 375px width
- [ ] **View** trip with GPS map
- [ ] **Verify** map container responsive (no horizontal scroll)
- [ ] **Verify** fullscreen button sized appropriately (40x40px)
- [ ] **Verify** location list stacks vertically below map

#### T14.2 - Tablet View (640px - 1024px)

- [ ] **Resize** to 768px width
- [ ] **Verify** map displays with proper aspect ratio
- [ ] **Enter** fullscreen mode
- [ ] **Verify** map fills viewport correctly on tablet size

#### T14.3 - Desktop View (>1024px)

- [ ] **Resize** to 1920px width
- [ ] **Verify** map container max-width appropriate
- [ ] **Verify** markers and polylines render crisply
- [ ] **Test** fullscreen on large monitor

#### T14.4 - Touch Support (if available)

- [ ] **On** touch device or DevTools device emulation
- [ ] **Tap** fullscreen button
- [ ] **Verify** button responds to touch
- [ ] **Pinch** to zoom map (in fullscreen)
- [ ] **Swipe** to pan map

---

### Test Suite 15: Performance (Phase 5)

#### T15.1 - Map Load Time (SC-009)

- [ ] **Open** trip detail page with 3 GPS locations
- [ ] **Measure** time from page load to map fully rendered
- [ ] **Verify** map renders in <2 seconds (SC-009 requirement)
- [ ] **Check** browser DevTools → Network → Timing

#### T15.2 - Map with Many Locations (20+)

- [ ] **Create** trip with 20 GPS locations
- [ ] **View** trip detail page
- [ ] **Verify** map loads without lag
- [ ] **Verify** all 20 numbered markers display
- [ ] **Verify** polyline connects all locations smoothly
- [ ] **Zoom/pan** map, verify smooth performance

#### T15.3 - Fullscreen Transition Performance

- [ ] **Toggle** fullscreen mode rapidly (5 times)
- [ ] **Verify** no visual glitches or lag
- [ ] **Verify** smooth CSS transitions (0.3s duration)
- [ ] **Check** browser DevTools → Performance → no frame drops

#### T15.4 - Memory Usage

- [ ] **Open** trip with map
- [ ] **Check** DevTools → Memory → Take heap snapshot
- [ ] **Enter/exit** fullscreen 10 times
- [ ] **Take** another heap snapshot
- [ ] **Verify** no significant memory leaks (should be similar sizes)

---

### Test Suite 16: Integration (Phase 5)

#### T16.1 - End-to-End: Create Trip with GPS → View Map

- [ ] **Navigate** to Create Trip page (`/trips/create`)
- [ ] **Fill** trip details (title, dates, distance, difficulty)
- [ ] **Add** 3 locations with GPS coordinates:
  - Location 1: "Madrid" (40.416775, -3.703790)
  - Location 2: "Valencia" (39.469907, -0.376288)
  - Location 3: "Barcelona" (41.385064, 2.173404)
- [ ] **Submit** trip (publish or save as draft)
- [ ] **Navigate** to trip detail page
- [ ] **Verify** map displays with 3 numbered markers
- [ ] **Verify** polyline connects markers in sequence order
- [ ] **Test** fullscreen mode works
- [ ] **Test** error handling (simulate offline, retry)

#### T16.2 - Edit Trip: Add GPS to Existing Location

- [ ] **Create** trip with location "Sevilla" (no coordinates)
- [ ] **View** trip detail → no map shown
- [ ] **Edit** trip
- [ ] **Add** coordinates to "Sevilla" (37.389092, -5.984459)
- [ ] **Save** trip
- [ ] **Verify** map now displays on detail page
- [ ] **Verify** marker shows "1. Sevilla"

#### T16.3 - Mixed Locations (Some with GPS, Some without)

- [ ] **Create** trip with:
  - Location 1: "Granada" (37.177336, -3.598557) ✅ GPS
  - Location 2: "Córdoba" (no coordinates) ❌ No GPS
  - Location 3: "Málaga" (36.721261, -4.421408) ✅ GPS
- [ ] **View** trip detail page
- [ ] **Verify** map displays only locations 1 and 3
- [ ] **Verify** markers numbered 1, 2 (skipping location without GPS)
- [ ] **Verify** location list shows all 3 locations
- [ ] **Verify** "Córdoba" shows "Sin coordenadas GPS"

---

### Test Suite 17: Edge Cases (Phase 5)

#### T17.1 - Single Location (No Polyline)

- [ ] **Create** trip with 1 GPS location
- [ ] **View** trip detail
- [ ] **Verify** map displays with single numbered marker
- [ ] **Verify** NO polyline rendered (only 1 point)
- [ ] **Verify** map centered on single location
- [ ] **Verify** zoom level appropriate (12 for city-level)

#### T17.2 - Two Locations (Single Polyline Segment)

- [ ] **Create** trip with 2 GPS locations
- [ ] **Verify** map shows 2 numbered markers
- [ ] **Verify** single polyline segment connects them
- [ ] **Verify** polyline style: blue (#2563eb), dashed (10, 10)

#### T17.3 - Locations in Close Proximity

- [ ] **Create** trip with 3 locations within 1km radius
- [ ] **Verify** map auto-zooms to show all markers
- [ ] **Verify** markers don't overlap (proper spacing)
- [ ] **Verify** polyline visible between close points

#### T17.4 - Locations Spanning Long Distance

- [ ] **Create** trip with locations across Spain:
  - "A Coruña" (43.362343, -8.411540)
  - "Cádiz" (36.529461, -6.292337)
- [ ] **Verify** map zoom level adjusts to fit both points
- [ ] **Verify** polyline spans entire distance
- [ ] **Enter** fullscreen for better view

#### T17.5 - Zero Locations with GPS

- [ ] **Create** trip with only text-based locations (no coordinates)
- [ ] **View** trip detail page
- [ ] **Verify** map section NOT displayed
- [ ] **Verify** message shown: "No hay ubicaciones con coordenadas GPS en este viaje"
- [ ] **Verify** location list still shows text-based locations

---

### Test Suite 18: Browser Compatibility (Phase 5)

#### T18.1 - Fullscreen API Support

- [ ] **Test** in Chrome/Edge (Chromium)
  - Fullscreen API: ✅ Supported
  - Verify fullscreen works
- [ ] **Test** in Firefox
  - Fullscreen API: ✅ Supported
  - Verify fullscreen works
- [ ] **Test** in Safari
  - Fullscreen API: ✅ Supported (webkit prefix)
  - Verify fullscreen works
- [ ] **If** browser doesn't support Fullscreen API:
  - Verify graceful degradation (button hidden or disabled)

#### T18.2 - Leaflet Map Rendering

- [ ] **Test** map tiles load in all browsers
- [ ] **Verify** marker icons render correctly
- [ ] **Verify** polyline renders smoothly
- [ ] **Test** zoom/pan interactions

---

## Known Limitations (Phase 5)

### Browser Support

- **Fullscreen API**: Requires modern browser (Chrome 71+, Firefox 64+, Safari 16.4+, Edge 79+)
  - Older browsers: Fullscreen button hidden or non-functional
- **Offline Maps**: Not supported - requires internet connection for tile loading
- **iOS Safari**: Fullscreen may behave differently due to Safari's unique fullscreen implementation

### Performance

- **Large Number of Locations**: Maps with >50 locations may experience slight lag
  - Recommendation: Keep trips under 50 locations for optimal performance
- **Slow Network**: Tile loading depends on network speed
  - Users on slow connections may see tiles load progressively

### Accessibility

- **Map Navigation**: Keyboard navigation limited by Leaflet.js capabilities
  - Tab navigation works for fullscreen button and retry button
  - Arrow key map panning may not work in all screen readers
- **Marker Click**: Screen reader support for map markers varies by browser

### Known Issues

- **Tile Loading Error**: Occasionally tiles fail to load due to OpenStreetMap rate limiting
  - Workaround: Click "Reintentar" button
- **Fullscreen Exit**: On some browsers, Escape key may not exit fullscreen consistently
  - Workaround: Click exit fullscreen button (X icon)

---

## Next Steps After Testing

1. **Fix any bugs** found during manual testing
2. **Update** this checklist with actual results
3. **Commit** Phase 5 changes to `009-gps-coordinates-frontend` branch
4. **Create PR** to merge to `main`
5. **Deploy** to production

---

## Success Criteria Summary

### Phase 4 (Frontend UI)

- [x] SC-F01: Coordinate input fields functional
- [x] SC-F02: Add/remove locations working
- [x] SC-F03: Validation displays Spanish errors
- [x] SC-F04: Review step shows coordinates
- [x] SC-F05: API payload includes coordinates
- [x] SC-F06: Backend accepts and returns coordinates
- [ ] SC-F07: Accessible keyboard navigation
- [ ] SC-F08: Mobile responsive design

### Phase 5 (Map Enhancements)

- [x] SC-M01: Numbered markers display in sequence order
- [x] SC-M02: Polyline connects locations with dashed line
- [x] SC-M03: Error handling with retry functionality
- [x] SC-M04: Fullscreen mode with smooth transitions
- [x] SC-M05: Unit tests achieve ≥90% coverage (97.82%)
- [ ] SC-M06: Map loads in <2 seconds (SC-009)
- [ ] SC-M07: Accessible marker navigation
- [ ] SC-M08: Responsive on mobile/tablet/desktop

---

**Testing Completed By**: _______________
**Date**: _______________
**Phase 4 Tests Passed**: ☐ Yes ☐ No
**Phase 5 Tests Passed**: ☐ Yes ☐ No

**Notes**:
