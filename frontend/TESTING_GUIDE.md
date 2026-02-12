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

---

# Reverse Geocoding Testing (Feature 010) - T050

**Feature**: 010-reverse-geocoding
**Date**: 2026-01-11
**Branch**: `010-reverse-geocoding`

---

## Visión General

Pruebas manuales exhaustivas para la funcionalidad de geocodificación inversa que permite a los usuarios:

1. **Hacer clic en el mapa** para añadir ubicaciones automáticamente con nombre y coordenadas GPS
2. **Arrastrar marcadores** para ajustar coordenadas con precisión
3. **Editar nombres de lugares** antes de guardar las ubicaciones

**Tecnologías Utilizadas**:
- **API de Nominatim** (OpenStreetMap) para geocodificación inversa
- **Caché LRU** para optimizar rendimiento y respetar límites de tasa (1 req/seg)
- **Debouncing** (1000ms) para evitar llamadas excesivas a la API
- **Componente Modal** con validación en tiempo real

---

## Requisitos Previos

### 1. Backend Ejecutándose

```bash
cd backend
./run-local-dev.sh  # Linux/Mac
.\run-local-dev.ps1  # Windows PowerShell
```

Backend accesible en: http://localhost:8000

### 2. Frontend Ejecutándose

```bash
cd frontend
npm run dev
```

Frontend accesible en: http://localhost:5173

### 3. Usuario de Prueba Verificado

```bash
cd backend
poetry run python scripts/create_verified_user.py
```

**Credenciales por defecto**:
- Usuario: `testuser`
- Contraseña: `TestPass123!`

### 4. Viaje de Prueba con Ubicaciones GPS

Necesitas un viaje existente con al menos una ubicación que tenga coordenadas GPS para probar las funcionalidades.

**Opción A - Usar script de prueba**:
```bash
cd backend
poetry run python scripts/add_test_trip_with_coordinates.py
```

**Opción B - Crear manualmente**:
1. Login como testuser
2. Ir a "Crear Viaje"
3. Añadir título: "Viaje de Prueba Geocoding"
4. Añadir ubicación con coordenadas: Madrid (40.416775, -3.703790)
5. Publicar viaje

---

## Suite de Pruebas 19: Historia de Usuario 1 - Clic en Mapa para Añadir Ubicación

### T19.1 - Activar Modo de Edición del Mapa

**Objetivo**: Verificar que el modo de edición se activa correctamente

**Pasos**:
1. **Navegar** a la página de detalle de un viaje con ubicaciones GPS
2. **Localizar** el botón "Editar ubicaciones" (esquina superior derecha del mapa)
3. **Hacer clic** en "Editar ubicaciones"

**Resultados Esperados**:
- ✅ Botón cambia a "Guardar cambios" o "Cancelar"
- ✅ Cursor sobre el mapa cambia a cursor de cruz (indica que se puede hacer clic)
- ✅ Marcadores existentes se vuelven arrastrables (cursor: grab al pasar el ratón)
- ✅ Mensaje informativo aparece: "Haz clic en el mapa para añadir una ubicación"

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T19.2 - Hacer Clic en el Mapa (Geocodificación Exitosa)

**Objetivo**: Verificar que al hacer clic en el mapa se obtiene el nombre del lugar

**Pasos**:
1. **Con el modo de edición activado**
2. **Hacer clic** en cualquier punto del mapa dentro de España (ej: centro de Madrid)
3. **Esperar** que aparezca el modal de confirmación

**Resultados Esperados**:
- ✅ **Modal aparece en <2 segundos** después del clic
- ✅ **Spinner de carga** visible inicialmente con texto "Obteniendo nombre del lugar..."
- ✅ **Spinner desaparece** cuando se completa la geocodificación (~1-2 segundos)
- ✅ **Nombre sugerido** aparece en español (ej: "Madrid, España")
- ✅ **Dirección completa** mostrada debajo (ej: "Madrid, Comunidad de Madrid, España")
- ✅ **Coordenadas** mostradas con 6 decimales de precisión (ej: "40.416800, -3.703800")
- ✅ **Campo de entrada** contiene el nombre sugerido y es editable
- ✅ **Contador de caracteres** muestra "X/200" (ej: "6/200" para "Madrid")
- ✅ **Botón "Confirmar ubicación"** está habilitado
- ✅ **Botón "Cancelar"** está presente
- ✅ **Sin errores** en la consola del navegador (F12 → Console)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T19.3 - Confirmar Ubicación y Guardar

**Objetivo**: Verificar que la ubicación se guarda correctamente

**Pasos**:
1. **Desde el modal de confirmación** (del test anterior)
2. **Sin editar el nombre**, hacer clic en "Confirmar ubicación"

**Resultados Esperados**:
- ✅ **Modal se cierra** inmediatamente
- ✅ **Nuevo marcador aparece** en el mapa en la posición donde se hizo clic
- ✅ **Marcador numerado** correctamente (si hay 2 ubicaciones previas, aparece "3")
- ✅ **Ubicación aparece** en la lista de ubicaciones del panel lateral derecho
- ✅ **Nombre coincide** con el nombre sugerido (no editado)
- ✅ **Coordenadas coinciden** con el punto clicado
- ✅ **Sin errores** en consola del navegador

**Pasos Adicionales - Verificar Persistencia**:
4. **Refrescar la página** (F5)

**Resultados Esperados (Persistencia)**:
- ✅ **Ubicación sigue visible** en el mapa (marcador permanente)
- ✅ **Ubicación sigue en la lista** del panel lateral
- ✅ **Datos correctos** (nombre y coordenadas se mantienen)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T19.4 - Cancelar Selección de Ubicación

**Objetivo**: Verificar que cancelar no añade la ubicación

**Pasos**:
1. **Hacer clic** en el mapa para abrir el modal
2. **Esperar** que aparezca el nombre sugerido
3. **Hacer clic** en el botón "Cancelar"

**Resultados Esperados**:
- ✅ **Modal se cierra** inmediatamente
- ✅ **NO se añade** ningún marcador nuevo al mapa
- ✅ **Lista de ubicaciones** permanece sin cambios
- ✅ **Modo de edición** sigue activo (puedes hacer clic de nuevo)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T19.5 - Clic Fuera del Modal (Cerrar por Overlay)

**Objetivo**: Verificar que hacer clic en el fondo oscuro cierra el modal

**Pasos**:
1. **Hacer clic** en el mapa para abrir el modal
2. **Hacer clic** en el fondo oscuro (overlay) fuera del cuadro del modal

**Resultados Esperados**:
- ✅ **Modal se cierra** (igual que botón "Cancelar")
- ✅ **NO se añade** ubicación
- ✅ **Modo de edición** permanece activo

**Pasos Adicionales**:
3. **Abrir el modal** de nuevo
4. **Hacer clic** dentro del contenido del modal (pero no en botones)

**Resultados Esperados (Clic Dentro)**:
- ✅ **Modal permanece abierto** (clic absorbido por el contenido del modal)
- ✅ **NO se cierra** accidentalmente

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T19.6 - Geocodificación de Lugares Específicos

**Objetivo**: Probar varios tipos de lugares para verificar la calidad de las sugerencias

**Prueba A - Parque (Parque del Retiro, Madrid)**:
1. **Hacer clic** en coordenadas aproximadas: 40.4153, -3.6844
2. **Verificar** nombre sugerido: "Parque del Retiro" o "El Retiro"

**Prueba B - Calle (Gran Vía, Madrid)**:
1. **Hacer clic** en coordenadas aproximadas: 40.4200, -3.7058
2. **Verificar** nombre sugerido: "Gran Vía" o "Calle Gran Vía"

**Prueba C - Monumento (Sagrada Familia, Barcelona)**:
1. **Hacer clic** en coordenadas aproximadas: 41.4036, 2.1744
2. **Verificar** nombre sugerido: "Sagrada Família" o "Basílica de la Sagrada Familia"

**Prueba D - Ciudad/Pueblo Pequeño**:
1. **Hacer clic** en un pueblo pequeño (ej: Jaca, Huesca: 42.5700, -0.5500)
2. **Verificar** nombre sugerido: "Jaca" (nombre del pueblo)

**Resultados Esperados (General)**:
- ✅ **Nombres en español** cuando sea posible (API configurada con `Accept-Language: es`)
- ✅ **Nombres legibles** y apropiados para el tipo de lugar
- ✅ **Dirección completa** proporcionada en todos los casos

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 20: Historia de Usuario 2 - Arrastrar Marcador para Ajustar Coordenadas

### T20.1 - Marcador Arrastrable en Modo de Edición

**Objetivo**: Verificar que los marcadores se pueden arrastrar solo en modo de edición

**Pasos (Sin Modo de Edición)**:
1. **Ir a página de detalle** de viaje con ubicaciones GPS
2. **SIN activar** modo de edición
3. **Intentar arrastrar** un marcador

**Resultados Esperados**:
- ✅ **Marcador NO se mueve** (arrastrabilidad desactivada)
- ✅ **Cursor normal** (no muestra grab/grabbing)

**Pasos (Con Modo de Edición)**:
4. **Activar** modo de edición ("Editar ubicaciones")
5. **Pasar el ratón** sobre un marcador

**Resultados Esperados**:
- ✅ **Cursor cambia a "grab"** (mano abierta)
- ✅ **Marcador resalta** visualmente (opcional, según implementación)

6. **Hacer clic y mantener** en el marcador

**Resultados Esperados**:
- ✅ **Cursor cambia a "grabbing"** (mano cerrada)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T20.2 - Arrastrar Marcador a Nueva Posición

**Objetivo**: Verificar que arrastrar actualiza coordenadas y geocodifica

**Pasos**:
1. **Con modo de edición activado**
2. **Arrastrar** un marcador existente ~100-200 metros a una nueva posición
3. **Soltar** el marcador (mouseup)
4. **Esperar 1 segundo** sin mover (debounce de 1000ms)

**Resultados Esperados**:
- ✅ **Marcador se mueve suavemente** durante el arrastre (sin saltos)
- ✅ **NO aparece modal** inmediatamente (debounce activo)
- ✅ **Después de 1 segundo** de quietud, se activa la geocodificación
- ✅ **Modal aparece** con nombre sugerido para la nueva posición
- ✅ **Coordenadas actualizadas** en el modal (diferentes a las originales)
- ✅ **Nombre del lugar** puede cambiar si se movió a un lugar diferente

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T20.3 - Arrastrar Múltiples Veces Rápidamente (Debounce)

**Objetivo**: Verificar que el debounce evita geocodificaciones múltiples

**Pasos**:
1. **Arrastrar** un marcador ~50 metros → Soltar
2. **Inmediatamente** (< 1 segundo) arrastrar de nuevo ~50 metros → Soltar
3. **Repetir** 2-3 veces rápidamente
4. **Esperar** 1 segundo sin tocar nada

**Resultados Esperados**:
- ✅ **Solo la posición final** dispara la geocodificación
- ✅ **NO se hacen** múltiples llamadas a la API (verificar en Network tab)
- ✅ **Sin errores 429** (rate limit) en consola
- ✅ **Modal aparece** solo UNA vez al final

**Pasos Adicionales - Verificar Caché**:
5. **Abrir consola del navegador** (F12)
6. **Buscar logs** de caché: `[GeoCoding Cache] HIT` o `MISS`
7. **Si se arrastra** a posiciones similares (~100m), debería aparecer `HIT`

**Resultados Esperados (Caché)**:
- ✅ **Cache HIT** si se arrastra a coordenadas redondeadas similares (3 decimales ~111m)
- ✅ **Tiempo de respuesta** 0ms en cache HIT (instantáneo)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T20.4 - Arrastrar Fuera de los Límites del Mapa

**Objetivo**: Verificar el comportamiento al arrastrar a los bordes

**Pasos**:
1. **Arrastrar** marcador hacia el borde del contenedor del mapa
2. **Intentar** arrastrar más allá del borde visible

**Resultados Esperados**:
- ✅ **Marcador se detiene** en el borde o el mapa se desplaza automáticamente (comportamiento de Leaflet)
- ✅ **Coordenadas válidas** al soltar (dentro de -90/90 lat, -180/180 lng)
- ✅ **Sin errores** de validación

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 21: Historia de Usuario 3 - Editar Nombre de Ubicación

### T21.1 - Editar Nombre Sugerido por Geocodificación

**Objetivo**: Verificar que se puede personalizar el nombre antes de guardar

**Pasos**:
1. **Hacer clic** en el mapa → Modal aparece con nombre sugerido "Madrid"
2. **Editar** el campo de entrada a "Mi lugar favorito en Madrid"
3. **Verificar** contador de caracteres actualizado: "30/200"
4. **Hacer clic** en "Confirmar ubicación"

**Resultados Esperados**:
- ✅ **Nombre personalizado** "Mi lugar favorito en Madrid" aparece en la lista lateral (NO "Madrid")
- ✅ **Popup del marcador** muestra el nombre personalizado al hacer clic
- ✅ **Persistencia**: Refrescar página (F5) → nombre personalizado se mantiene

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T21.2 - Validación de Nombre Vacío

**Objetivo**: Verificar que no se puede guardar sin nombre

**Pasos**:
1. **Hacer clic** en el mapa → Modal aparece
2. **Seleccionar todo** el texto del campo de entrada (Ctrl+A / Cmd+A)
3. **Eliminar** todo el texto (tecla Delete)

**Resultados Esperados**:
- ✅ **Botón "Confirmar ubicación" se deshabilita** (opacity: 0.6, cursor: not-allowed)
- ✅ **Mensaje de error aparece** en rojo: "El nombre no puede estar vacío"
- ✅ **Campo de entrada** tiene borde rojo (clase CSS `invalid`)
- ✅ **Hacer clic** en el botón deshabilitado no hace nada (no cierra el modal)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T21.3 - Validación de Solo Espacios en Blanco

**Objetivo**: Verificar que no se aceptan nombres con solo espacios

**Pasos**:
1. **Hacer clic** en el mapa → Modal aparece
2. **Limpiar** el campo de entrada
3. **Escribir** solo espacios: "   " (3-5 espacios)

**Resultados Esperados**:
- ✅ **Botón "Confirmar ubicación" permanece deshabilitado**
- ✅ **Mensaje de error visible**: "El nombre no puede estar vacío"
- ✅ **Campo con borde rojo** (clase `invalid`)

**Pasos Adicionales**:
4. **Escribir** un nombre válido: "Test Location"

**Resultados Esperados (Nombre Válido)**:
- ✅ **Botón se habilita** automáticamente
- ✅ **Mensaje de error desaparece**
- ✅ **Borde rojo desaparece**
- ✅ **Contador actualizado**: "13/200"

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T21.4 - Contador de Caracteres y Límite Máximo

**Objetivo**: Verificar el límite de 200 caracteres

**Pasos**:
1. **Hacer clic** en el mapa → Modal aparece
2. **Escribir** exactamente 200 caracteres (usar texto de prueba):
   ```
   AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA AAAAAAAAAA
   ```

**Resultados Esperados**:
- ✅ **Todos los 200 caracteres aceptados**
- ✅ **Contador muestra**: "200/200"
- ✅ **Botón "Confirmar" habilitado** (200 es válido)

**Pasos Adicionales**:
3. **Intentar escribir** el carácter 201

**Resultados Esperados (Límite Máximo)**:
- ✅ **Carácter 201 NO se añade** (atributo maxLength previene entrada)
- ✅ **Contador permanece**: "200/200"

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T21.5 - Caracteres Especiales y Acentos

**Objetivo**: Verificar que se aceptan caracteres especiales españoles

**Pasos**:
1. **Hacer clic** en el mapa → Modal aparece
2. **Escribir** nombre con acentos y caracteres especiales:
   ```
   Café París (España) - año 2024 ñ á é í ó ú ü
   ```
3. **Confirmar** ubicación

**Resultados Esperados**:
- ✅ **Todos los caracteres aceptados** (sin corrupción)
- ✅ **Se guarda correctamente** en el backend
- ✅ **Se muestra correctamente** en la lista lateral
- ✅ **Refrescar página** → sin corrupción de caracteres

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T21.6 - Recorte de Espacios (Trim)

**Objetivo**: Verificar que se eliminan espacios al inicio/final

**Pasos**:
1. **Hacer clic** en el mapa → Modal aparece
2. **Escribir** nombre con espacios: "  Nombre con espacios  "
3. **Confirmar** ubicación
4. **Verificar** nombre guardado en la lista

**Resultados Esperados**:
- ✅ **Nombre guardado**: "Nombre con espacios" (sin espacios extras)
- ✅ **Trimming automático** antes de guardar

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 22: Manejo de Errores

### T22.1 - Error de Red (Modo Offline)

**Objetivo**: Verificar degradación elegante cuando no hay conexión

**Pasos**:
1. **Abrir** DevTools (F12) → Pestaña "Network"
2. **Activar** modo offline (desplegable "Throttling" → "Offline")
3. **Hacer clic** en el mapa

**Resultados Esperados**:
- ✅ **Modal aparece**
- ✅ **Spinner de carga** se muestra brevemente
- ✅ **Estado de error** aparece con mensaje:
  - "El servidor de mapas no responde. Verifica tu conexión."
- ✅ **Icono de error** visible (SVG de advertencia/error)
- ✅ **Campo de entrada habilitado** (vacío o con coordenadas de respaldo)
- ✅ **Mensaje adicional**: "Puedes ingresar un nombre manualmente"
- ✅ **Usuario puede escribir** nombre manual
- ✅ **Botón "Confirmar"** funciona con nombre manual

**Pasos Adicionales**:
4. **Escribir** nombre manual: "Ubicación sin conexión"
5. **Confirmar**

**Resultados Esperados (Nombre Manual)**:
- ✅ **Ubicación se guarda** con nombre manual y coordenadas
- ✅ **NO se muestra** nombre geocodificado (porque falló)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T22.2 - Coordenadas Inválidas (Fuera de Rango)

**Objetivo**: Verificar validación de coordenadas

**Pasos**:
1. **Abrir consola** del navegador (F12)
2. **Ejecutar** JavaScript para simular coordenadas inválidas:
   ```javascript
   // Intentar geocodificar latitud inválida (>90)
   // Nota: Esto requiere acceso a la función geocode del hook
   // En práctica, el mapa de Leaflet NO permite clics fuera de rango
   // Este test valida la lógica defensiva del servicio
   ```

**Nota**: Este test es más teórico porque Leaflet restringe clics a coordenadas válidas. La validación existe como medida defensiva.

**Resultados Esperados (Si se pudiera forzar)**:
- ✅ **Error lanzado** con mensaje en español
- ✅ **Mensaje contiene**: "Las coordenadas deben estar entre -90 y 90 (latitud), -180 y 180 (longitud)"

**Estado**: [ ] Pasa [ ] Falla (N/A - Leaflet previene este caso)
**Notas**: _____________________

---

### T22.3 - Ubicación Remota (Océano/Desierto)

**Objetivo**: Verificar manejo de lugares sin nombres

**Pasos**:
1. **Hacer zoom out** en el mapa para ver océanos
2. **Hacer clic** en medio del Océano Atlántico (lejos de tierra)
   - Coordenadas ejemplo: 30.0, -40.0

**Resultados Esperados**:
- ✅ **Modal aparece**
- ✅ **Geocodificación se completa** (puede tardar más)
- ✅ **Nombre sugerido genérico**: "Ocean", "Atlantic Ocean", o vacío
- ✅ **Usuario puede editar** el nombre a algo más significativo
- ✅ **Confirmación funciona** normalmente

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T22.4 - Cancelar Durante Geocodificación

**Objetivo**: Verificar que cancelar rápidamente no causa errores

**Pasos**:
1. **Hacer clic** en el mapa
2. **Inmediatamente** (< 1 segundo) hacer clic en "Cancelar" antes de que aparezca el nombre

**Resultados Esperados**:
- ✅ **Modal se cierra**
- ✅ **NO se añade ubicación**
- ✅ **Sin errores** en consola
- ✅ **Request de geocodificación** puede seguir en curso pero se ignora el resultado

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 23: Accesibilidad (WCAG 2.1 AA)

### T23.1 - Navegación por Teclado

**Objetivo**: Verificar accesibilidad completa con teclado

**Pasos**:
1. **Hacer clic** en "Editar ubicaciones"
2. **Usar tecla Tab** para navegar
3. **Hacer clic** en el mapa para abrir modal

**Resultados Esperados (Navegación en Modal)**:
- ✅ **Puede tabular** al campo de entrada (recibe foco automático - autofocus)
- ✅ **Puede tabular** al botón "Cancelar"
- ✅ **Puede tabular** al botón "Confirmar ubicación"
- ✅ **Indicador de foco visible** en todos los elementos (outline azul)
- ✅ **Tecla Enter** en botón "Confirmar" envía el formulario
- ✅ **Tecla Esc** cierra el modal

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T23.2 - Lector de Pantalla (Screen Reader)

**Objetivo**: Verificar anuncios de ARIA para usuarios ciegos

**Herramientas**: NVDA (Windows), JAWS (Windows), VoiceOver (Mac)

**Pasos**:
1. **Activar** lector de pantalla
2. **Hacer clic** en el mapa → Modal se abre
3. **Tabular** a través de los elementos del modal

**Anuncios Esperados**:
- ✅ **Al abrir modal**: "Confirmar ubicación, dialog" (role="dialog")
- ✅ **Durante carga**: "Obteniendo nombre del lugar..." (aria-live="polite")
- ✅ **Si hay error**: "Alert: [mensaje de error]" (role="alert", aria-live="assertive")
- ✅ **Campo de entrada**: "Nombre de la ubicación, edit, has text: Madrid"
- ✅ **Botón confirmar (válido)**: "Confirmar y guardar la ubicación, button"
- ✅ **Botón confirmar (inválido)**: "Confirmar ubicación, deshabilitado: nombre inválido, button disabled"
- ✅ **Botón cancelar**: "Cancelar y cerrar el modal, button"
- ✅ **Botón cerrar (×)**: "Cerrar, button"

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T23.3 - Atributos ARIA

**Objetivo**: Verificar presencia de atributos ARIA en el HTML

**Pasos**:
1. **Abrir** DevTools (F12) → Pestaña "Elements"
2. **Inspeccionar** el modal (LocationConfirmModal)

**Atributos Esperados**:
- ✅ `role="dialog"` en overlay del modal
- ✅ `aria-modal="true"` en overlay
- ✅ `aria-labelledby="location-modal-title"` apunta al h3
- ✅ `aria-describedby="location-modal-description"` apunta al contenido
- ✅ `role="status" aria-live="polite"` en spinner de carga
- ✅ `role="alert" aria-live="assertive"` en estado de error
- ✅ `aria-label` dinámico en botón confirmar (cambia según validación)
- ✅ `aria-disabled` en botón confirmar cuando está deshabilitado

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 24: Diseño Responsivo Mobile

### T24.1 - Vista Mobile (<640px) - Layout del Modal

**Objetivo**: Verificar diseño adaptado para móviles

**Pasos**:
1. **Abrir** Chrome DevTools (F12) → Toggle Device Toolbar (Ctrl+Shift+M)
2. **Seleccionar** iPhone 12 (390×844px)
3. **Navegar** a viaje → Activar modo edición
4. **Hacer clic** en el mapa

**Resultados Esperados**:
- ✅ **Modal aparece desde abajo** (animación slide-up)
- ✅ **Modal max-height: 85vh** (deja espacio arriba para ver parte del mapa)
- ✅ **Botones apilados verticalmente** (no horizontales)
- ✅ **Botón "Confirmar" aparece ARRIBA** del botón "Cancelar" (orden inverso a desktop)
- ✅ **Botones ancho completo** (width: 100%)
- ✅ **Botón cerrar (×)** grande: 40×40px (fácil de tocar)
- ✅ **Todos los botones** altura mínima 44px (iOS Human Interface Guidelines)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T24.2 - Vista Mobile - Input de Texto

**Objetivo**: Verificar que el teclado no oculta el modal

**Pasos**:
1. **En vista mobile** (iPhone 12)
2. **Modal abierto** → Tocar el campo de entrada

**Resultados Esperados**:
- ✅ **Teclado virtual aparece**
- ✅ **Modal NO se encoge** demasiado (sigue usable)
- ✅ **Input NO hace zoom** en iOS (font-size: 16px previene auto-zoom)
- ✅ **Puede ver** el campo de entrada mientras escribe
- ✅ **Contador de caracteres** visible incluso con teclado abierto

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T24.3 - Vista Mobile - Rotación Landscape

**Objetivo**: Verificar adaptación en modo horizontal

**Pasos**:
1. **En DevTools**, cambiar orientación a landscape (844×390px)
2. **Abrir modal**

**Resultados Esperados**:
- ✅ **Modal sigue usable** (no se sale de pantalla)
- ✅ **Layout se adapta** apropiadamente
- ✅ **Scroll funciona** si el contenido es largo

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T24.4 - Vista Tablet (640px - 1024px)

**Objetivo**: Verificar layout de tablet (intermedio)

**Pasos**:
1. **Seleccionar** iPad (1024×768px) en DevTools
2. **Hacer clic** en el mapa

**Resultados Esperados**:
- ✅ **Modal usa layout de desktop** (centrado, no alineado abajo)
- ✅ **Botones horizontales** (lado a lado)
- ✅ **Ancho del modal** ~500px (no ancho completo)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 25: Rendimiento y Caché

### T25.1 - Tiempo de Respuesta de Geocodificación

**Objetivo**: Verificar que la API responde en <2 segundos (SC-003)

**Pasos**:
1. **Abrir** DevTools (F12) → Pestaña "Network"
2. **Limpiar** caché del navegador (Ctrl+Shift+R)
3. **Hacer clic** en el mapa en coordenadas: 40.4168, -3.7038 (Madrid)
4. **Observar** request a `nominatim.openstreetmap.org/reverse`
5. **Anotar** tiempo de respuesta en columna "Time"

**Resultados Esperados**:
- ✅ **Request se completa en <2 segundos** (SC-003 requirement)
- ✅ **Modal aparece** inmediatamente (sin demora adicional)

**Estado**: [ ] Pasa [ ] Falla
**Tiempo Medido**: _____ ms
**Notas**: _____________________

---

### T25.2 - Funcionamiento del Caché LRU

**Objetivo**: Verificar que el caché reduce llamadas a la API

**Pasos**:
1. **Limpiar** caché (recargar página)
2. **Hacer clic** en mapa en: 40.416, -3.704 (Madrid centro)
3. **Anotar** request en Network tab
4. **Cancelar** modal
5. **Hacer clic de nuevo** en coordenadas cercanas: 40.417, -3.703 (dentro de ~111m)

**Resultados Esperados**:
- ✅ **NO hay nuevo request** en Network tab (cache HIT)
- ✅ **Modal aparece instantáneamente** (0ms)
- ✅ **Consola muestra**: `[GeoCoding Cache] HIT (50.0% hit rate)...`

**Pasos Adicionales - Verificar Estadísticas**:
6. **Abrir consola** → Escribir:
   ```javascript
   geocodingCache.getStats()
   ```

**Resultados Esperados (Stats)**:
- ✅ **Retorna objeto** con `hits`, `misses`, `hitRate`
- ✅ **hitRate > 0%** (después de al menos un cache hit)
- ✅ **size <= 100** (tamaño máximo del caché)

**Estado**: [ ] Pasa [ ] Falla
**Hit Rate Medido**: _____ %
**Notas**: _____________________

---

### T25.3 - Debouncing de Arrastre

**Objetivo**: Verificar que el debounce previene llamadas excesivas

**Pasos**:
1. **Limpiar** Network tab
2. **Arrastrar** marcador continuamente por 5 segundos (movimiento constante)
3. **Soltar** y esperar 1 segundo

**Resultados Esperados**:
- ✅ **Durante arrastre**: NO hay requests a Nominatim
- ✅ **Después de soltar + 1 seg**: SOLO 1 request aparece
- ✅ **Sin errores 429** (Too Many Requests)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 26: Integración con Backend

### T26.1 - Persistencia en Servidor (No LocalStorage)

**Objetivo**: Verificar que las ubicaciones se guardan en el backend

**Pasos**:
1. **Añadir** ubicación "Integration Test Location" con geocodificación
2. **Confirmar** y verificar que aparece
3. **Abrir** DevTools → Pestaña "Application"
4. **Verificar** IndexedDB, LocalStorage, SessionStorage

**Resultados Esperados**:
- ✅ **NO hay datos de ubicación** en almacenamiento del cliente (todo server-side)

**Pasos Adicionales - Verificar Persistencia**:
5. **Refrescar página** (F5)

**Resultados Esperados**:
- ✅ **"Integration Test Location" sigue visible**
- ✅ **Marcador en misma posición**

**Pasos Adicionales - Nueva Sesión**:
6. **Abrir nueva ventana de incógnito**
7. **Login** con mismas credenciales (testuser)
8. **Navegar** al mismo viaje

**Resultados Esperados (Cross-Session)**:
- ✅ **"Integration Test Location" es visible**
- ✅ **Confirma persistencia del servidor** (no caché local)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

### T26.2 - Payload de Request al Backend

**Objetivo**: Verificar que los datos se envían correctamente

**Pasos**:
1. **Añadir** ubicación con geocodificación
2. **Confirmar** ubicación
3. **Abrir** DevTools → Network → Buscar request POST/PUT a `/trips/.../locations`
4. **Inspeccionar** payload (Request Payload)

**Payload Esperado**:
```json
{
  "name": "Madrid",
  "latitude": 40.416800,
  "longitude": -3.703800,
  "sequence": <número>
}
```

**Resultados Esperados**:
- ✅ **name**: Nombre geocodificado o editado (string)
- ✅ **latitude**: Número con hasta 6 decimales
- ✅ **longitude**: Número con hasta 6 decimales
- ✅ **sequence**: Entero (orden de la ubicación)

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 27: Casos Extremos (Edge Cases)

### T27.1 - Nombre con Longitud Máxima (200 caracteres)

**Objetivo**: Ver test T21.4 (ya cubierto arriba)

**Estado**: [ ] Pasa [ ] Falla (referirse a T21.4)

---

### T27.2 - Caracteres Especiales

**Objetivo**: Ver test T21.5 (ya cubierto arriba)

**Estado**: [ ] Pasa [ ] Falla (referirse a T21.5)

---

### T27.3 - Múltiples Ubicaciones Añadidas Rápidamente

**Objetivo**: Verificar estabilidad con acciones rápidas

**Pasos**:
1. **Hacer clic** en el mapa → Confirmar inmediatamente
2. **Repetir** 5 veces seguidas lo más rápido posible

**Resultados Esperados**:
- ✅ **5 ubicaciones añadidas** correctamente
- ✅ **Todas con nombres** geocodificados
- ✅ **Numeración correcta** (1, 2, 3, 4, 5)
- ✅ **Sin errores** en consola
- ✅ **Sin pérdida** de datos

**Estado**: [ ] Pasa [ ] Falla
**Notas**: _____________________

---

## Suite de Pruebas 28: Compatibilidad de Navegadores

### T28.1 - Chrome (Última Versión)

**Pasos**: Probar flujos críticos (US1, US2, US3)

- [ ] US1: Clic para añadir
- [ ] US2: Arrastrar para ajustar
- [ ] US3: Editar nombre
- [ ] Accesibilidad
- [ ] Responsive mobile

**Notas**: _____________________

---

### T28.2 - Firefox (Última Versión)

**Pasos**: Probar flujos críticos

- [ ] US1: Clic para añadir
- [ ] US2: Arrastrar para ajustar
- [ ] US3: Editar nombre
- [ ] Accesibilidad
- [ ] Responsive mobile

**Notas**: _____________________

---

### T28.3 - Safari (si está disponible)

**Pasos**: Probar flujos críticos + VoiceOver

- [ ] US1: Clic para añadir
- [ ] US2: Arrastrar para ajustar
- [ ] US3: Editar nombre
- [ ] Accesibilidad (VoiceOver)
- [ ] Responsive mobile (iOS)

**Notas**: _____________________

---

### T28.4 - Edge (si está disponible)

**Pasos**: Probar flujos críticos

- [ ] US1: Clic para añadir
- [ ] US2: Arrastrar para ajustar
- [ ] US3: Editar nombre

**Notas**: _____________________

---

## Checklist de Resumen - Feature 010

### Funcionalidad ✓

- [ ] Clic en mapa activa geocodificación
- [ ] Modal muestra nombre sugerido del lugar
- [ ] Edición de nombre funciona
- [ ] Validación previene nombres vacíos
- [ ] Ubicación se guarda en backend
- [ ] Arrastre de marcador actualiza coordenadas
- [ ] Debouncing previene límites de tasa
- [ ] Caché reduce llamadas a API

### Experiencia de Usuario ✓

- [ ] Estados de carga visibles
- [ ] Mensajes de error en español
- [ ] Degradación elegante (modo offline)
- [ ] Tiempos de respuesta <2s
- [ ] Sin errores en consola

### Accesibilidad ✓

- [ ] Navegación por teclado funciona
- [ ] Lector de pantalla anuncia estados
- [ ] Indicadores de foco visibles
- [ ] Atributos ARIA presentes

### Mobile ✓

- [ ] Modal alineado abajo en mobile
- [ ] Touch targets ≥44px
- [ ] Sin zoom en iOS al enfocar input
- [ ] Teclado no oculta el modal

### Rendimiento ✓

- [ ] Tasa de acierto de caché >70% después de uso repetido
- [ ] Debounce previene requests duplicados
- [ ] Requests de red <2s

### Integración ✓

- [ ] Backend persiste datos
- [ ] Refresh mantiene estado
- [ ] Consistencia cross-session

---

## Criterios de Éxito - Feature 010

**Basado en spec.md (Success Criteria SC-001 a SC-008)**:

- [ ] **SC-001**: Usuarios pueden añadir ubicación en <10 segundos con clic en mapa
- [ ] **SC-002**: 90% de adiciones usan clic en mapa (medido después de 2 semanas)
- [ ] **SC-003**: API de geocodificación responde en <2 segundos (95% de requests)
- [ ] **SC-004**: Sistema recupera nombre de lugar para ≥85% de clics en mapa
- [ ] **SC-005**: Arrastre de marcador actualiza coordenadas sin lag (<100ms)
- [ ] **SC-006**: Cero violaciones del límite de tasa de Nominatim API (1 req/seg)
- [ ] **SC-007**: Usuarios reportan mayor satisfacción con entrada de ubicaciones
- [ ] **SC-008**: Tickets de soporte sobre "cómo añadir GPS" disminuyen ≥50%

---

## Plantilla de Reporte de Bugs

Si encuentras bugs durante las pruebas, documéntalos aquí:

### Bug #1

**Severidad**: [ ] Crítico [ ] Alto [ ] Medio [ ] Bajo
**Test ID**: _____________________
**Navegador**: _____________________
**Dispositivo**: _____________________

**Pasos para Reproducir**:
1.
2.
3.

**Esperado**: _____________________

**Actual**: _____________________

**Captura de pantalla**: (adjuntar si es necesario)

**Errores de consola**: (copiar/pegar)

---

## Sign-off

**Tester**: _____________________
**Fecha**: _____________________
**Resultado General**: [ ] Pasa [ ] Falla (con bugs documentados)

**Notas**:
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________
