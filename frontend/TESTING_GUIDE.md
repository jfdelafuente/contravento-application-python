# Frontend Testing Guide - GPS Coordinates (Phase 4)

**Feature**: 009-gps-coordinates (Phase 4 - Frontend UI)
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

- [ ] **Enter** location name: "Jaca"
- [ ] **Enter** latitude: `42.5700841234567` (13 decimals)
- [ ] **Enter** longitude: `-0.5499411234567`
- [ ] **Proceed** to Step 4
- [ ] **Expected**: Coordinates displayed with 6 decimal precision:
  - Lat: `42.570084°` (rounded)
  - Lon: `-0.549941°` (rounded)

---

### Test Suite 6: Step 4 Review Display

#### T6.1 - Review Locations Section Exists

- [ ] **Create** trip with 2 locations (both with GPS)
- [ ] **Navigate** to Step 4 (Review)
- [ ] **Verify** "Ubicaciones" section appears after "Información Básica"
- [ ] **Verify** section displays before "Descripción"

#### T6.2 - Review Location Numbering

- [ ] **Verify** locations numbered with blue circles (1, 2, 3...)
- [ ] **Verify** location names displayed prominently
- [ ] **Verify** coordinates in monospace font with 📍 icon

#### T6.3 - Review Locations Without GPS

- [ ] **Remove** all locations except one
- [ ] **Enter** only name: "Test"
- [ ] **Navigate** to Step 4
- [ ] **Verify** shows: "Test - Sin coordenadas GPS"

---

### Test Suite 7: End-to-End Trip Creation

#### T7.1 - Create Trip with GPS Coordinates

- [ ] **Login** as testuser
- [ ] **Navigate** to "Crear Viaje"
- [ ] **Step 1 - Basic Info**:
  - Title: "Ruta GPS Test - Madrid a Toledo"
  - Start Date: (today's date)
  - Distance: `130`
  - Difficulty: Moderada
  - Locations:
    1. Madrid - Lat: `40.416775`, Lon: `-3.703790`
    2. Toledo - Lat: `39.862832`, Lon: `-4.027323`
- [ ] **Step 2 - Story & Tags**:
  - Description: "Ruta de prueba con coordenadas GPS para validar la integración con el backend."
  - Tags: `gps`, `prueba`
- [ ] **Step 3 - Photos**: Skip (no photos)
- [ ] **Step 4 - Review**:
  - Verify all locations display with coordinates
  - Click "Publicar Viaje"
- [ ] **Verify** trip created successfully
- [ ] **Open** browser DevTools → Network tab
- [ ] **Inspect** POST request to `/trips`
- [ ] **Verify** payload includes:

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

- [ ] **Create** new trip
- [ ] **Add** 2 locations with names only (no coordinates)
- [ ] **Complete** all steps
- [ ] **Publish** trip
- [ ] **Verify** trip created successfully
- [ ] **Verify** locations saved with null coordinates

#### T7.3 - Backend Response Validation

- [ ] **After** creating trip with GPS
- [ ] **Check** browser DevTools → Network → Response
- [ ] **Verify** response includes locations with coordinates:

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

## Next Steps After Testing

1. **Fix any bugs** found during manual testing
2. **Update** this checklist with actual results
3. **Commit** Phase 4 changes to `009-gps-coordinates-frontend` branch
4. **Create PR** to merge to `develop`
5. **Plan Phase 5** (Map Visualization - Future Enhancement)

---

**Testing Completed By**: _______________
**Date**: _______________
**All Tests Passed**: ☐ Yes ☐ No (see notes below)

**Notes**:
