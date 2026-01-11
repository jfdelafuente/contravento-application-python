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

3. **Step4Review Updates** (`frontend/src/components/trips/TripForm/Step4Review.tsx`)
   - Display locations with GPS coordinates in review step
   - Visual formatting with numbered location list

4. **Trip Helpers** (`frontend/src/utils/tripHelpers.ts`)
   - `formatCoordinate()` - Format single coordinate with degree symbol
   - `formatCoordinatePair()` - Format latitude/longitude pair
   - `validateCoordinates()` - Client-side coordinate validation

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

### Test Suite 1: Location Input Component

#### T1.1 - Location Name Required
- [ ] **Navigate** to trip creation form (Step 1)
- [ ] **Leave** location name field empty
- [ ] **Attempt** to move to next step
- [ ] **Verify** error message appears: "El nombre de la ubicación es obligatorio"

#### T1.2 - Add Location Button
- [ ] **Click** "Añadir Ubicación" button
- [ ] **Verify** new location input appears
- [ ] **Verify** each location has a number (Ubicación 1, Ubicación 2, etc.)
- [ ] **Add** locations until you reach 10
- [ ] **Verify** "Añadir Ubicación" button still enabled (max is 50)

#### T1.3 - Remove Location Button
- [ ] **Add** 3 locations
- [ ] **Click** "Eliminar" on the 2nd location
- [ ] **Verify** location is removed
- [ ] **Verify** remaining locations renumbered (Ubicación 1, Ubicación 2)
- [ ] **Reduce** to 1 location
- [ ] **Verify** "Eliminar" button is hidden (minimum 1 location required)

---

### Test Suite 2: GPS Coordinate Input

#### T2.1 - Valid Coordinates (Madrid)
- [ ] **Enter** location name: "Madrid"
- [ ] **Enter** latitude: `40.416775`
- [ ] **Enter** longitude: `-3.703790`
- [ ] **Verify** no error messages appear
- [ ] **Proceed** to Step 4 (Review)
- [ ] **Verify** coordinates display: "📍 Lat: 40.416775°, Lon: -3.703790°"

#### T2.2 - Valid Coordinates (Barcelona)
- [ ] **Enter** location name: "Barcelona"
- [ ] **Enter** latitude: `41.385064`
- [ ] **Enter** longitude: `2.173404`
- [ ] **Verify** coordinates accepted
- [ ] **Check** Step 4 shows both Madrid and Barcelona with coordinates

#### T2.3 - Coordinates Without Name (Should Fail)
- [ ] **Add** new location
- [ ] **Leave** name empty
- [ ] **Enter** latitude: `40.0`
- [ ] **Enter** longitude: `-3.0`
- [ ] **Attempt** to proceed
- [ ] **Verify** error: "El nombre de la ubicación es obligatorio"

---

### Test Suite 3: Coordinate Validation

#### T3.1 - Latitude Out of Range (Too High)
- [ ] **Enter** location name: "Invalid North"
- [ ] **Enter** latitude: `100`
- [ ] **Enter** longitude: `0`
- [ ] **Verify** browser validation prevents submission (min="-90" max="90" on input)
- [ ] **Verify** form cannot proceed with invalid value

#### T3.2 - Latitude Out of Range (Too Low)
- [ ] **Enter** latitude: `-100`
- [ ] **Verify** browser validation blocks value below -90

#### T3.3 - Longitude Out of Range (Too High)
- [ ] **Enter** longitude: `200`
- [ ] **Verify** browser validation blocks value above 180

#### T3.4 - Longitude Out of Range (Too Low)
- [ ] **Enter** longitude: `-200`
- [ ] **Verify** browser validation blocks value below -180

#### T3.5 - High Precision Coordinates
- [ ] **Enter** location name: "Jaca"
- [ ] **Enter** latitude: `42.5700841234567` (13 decimals)
- [ ] **Enter** longitude: `-0.5499411234567`
- [ ] **Proceed** to Step 4
- [ ] **Verify** coordinates displayed with 6 decimal precision:
  - Lat: `42.570084°` (rounded)
  - Lon: `-0.549941°` (rounded)

---

### Test Suite 4: Optional Coordinates

#### T4.1 - Location Without GPS Coordinates
- [ ] **Enter** location name: "Camino de Santiago"
- [ ] **Leave** latitude empty
- [ ] **Leave** longitude empty
- [ ] **Proceed** to Step 4
- [ ] **Verify** location shows: "Sin coordenadas GPS"

#### T4.2 - Mix of Locations (With and Without GPS)
- [ ] **Create** trip with 3 locations:
  1. Madrid (with GPS: 40.416775, -3.703790)
  2. Camino de Santiago (no GPS)
  3. Barcelona (with GPS: 41.385064, 2.173404)
- [ ] **Verify** Step 4 shows:
  - Location 1: Madrid with coordinates
  - Location 2: Camino de Santiago - "Sin coordenadas GPS"
  - Location 3: Barcelona with coordinates

#### T4.3 - Partial Coordinates (Should Not Submit)
- [ ] **Enter** location name: "Test"
- [ ] **Enter** latitude: `40.0`
- [ ] **Leave** longitude empty
- [ ] **Attempt** to proceed
- [ ] **Verify** HTML5 validation requires longitude (or backend returns error)

---

### Test Suite 5: Step 4 Review Display

#### T5.1 - Review Locations Section Exists
- [ ] **Create** trip with 2 locations (both with GPS)
- [ ] **Navigate** to Step 4 (Review)
- [ ] **Verify** "Ubicaciones" section appears after "Información Básica"
- [ ] **Verify** section displays before "Descripción"

#### T5.2 - Review Location Numbering
- [ ] **Verify** locations numbered with blue circles (1, 2, 3...)
- [ ] **Verify** location names displayed prominently
- [ ] **Verify** coordinates in monospace font with 📍 icon

#### T5.3 - Review Empty Locations
- [ ] **Remove** all locations except one
- [ ] **Enter** only name: "Test"
- [ ] **Navigate** to Step 4
- [ ] **Verify** shows: "Test - Sin coordenadas GPS"

---

### Test Suite 6: End-to-End Trip Creation

#### T6.1 - Create Trip with GPS Coordinates
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

#### T6.2 - Create Trip Without GPS Coordinates
- [ ] **Create** new trip
- [ ] **Add** 2 locations with names only (no coordinates)
- [ ] **Complete** all steps
- [ ] **Publish** trip
- [ ] **Verify** trip created successfully
- [ ] **Verify** locations saved with null coordinates

#### T6.3 - Backend Response Validation
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

### Test Suite 7: Accessibility

#### T7.1 - Keyboard Navigation
- [ ] **Use** Tab key to navigate through location inputs
- [ ] **Verify** focus indicators visible on all fields
- [ ] **Tab** to "Añadir Ubicación" button
- [ ] **Press** Enter to add location
- [ ] **Verify** new location input receives focus

#### T7.2 - Screen Reader Labels
- [ ] **Enable** screen reader (NVDA/JAWS on Windows, VoiceOver on Mac)
- [ ] **Navigate** to latitude input
- [ ] **Verify** reads: "Latitud de la ubicación 1, -90 a 90 grados"
- [ ] **Navigate** to longitude input
- [ ] **Verify** reads: "Longitud de la ubicación 1, -180 a 180 grados"

#### T7.3 - Error Announcements
- [ ] **Enter** invalid latitude: `100`
- [ ] **Tab** away from field
- [ ] **Verify** error message announced by screen reader
- [ ] **Verify** aria-invalid="true" on input

---

### Test Suite 8: Responsive Design

#### T8.1 - Mobile View (< 640px)
- [ ] **Resize** browser to 375px width (mobile phone)
- [ ] **Verify** coordinate inputs stack vertically (not side-by-side)
- [ ] **Verify** "Eliminar" button full width
- [ ] **Verify** all text readable without horizontal scroll

#### T8.2 - Tablet View (640px - 1024px)
- [ ] **Resize** to 768px width (tablet)
- [ ] **Verify** coordinate inputs side-by-side in grid
- [ ] **Verify** proper spacing and alignment

---

## Expected Results Summary

### ✅ All Tests Passing Means:

1. **Input Validation**:
   - Location names required
   - GPS coordinates optional
   - Coordinates validated in range (-90/90, -180/180)
   - High precision rounded to 6 decimals

2. **User Experience**:
   - Add/remove locations seamlessly
   - Clear error messages in Spanish
   - Coordinates display properly in review
   - Accessible keyboard navigation

3. **Backend Integration**:
   - Coordinates sent in API payload
   - Backend accepts and stores coordinates
   - Response includes coordinates in locations array

4. **Visual Design**:
   - Clean, modern UI with ContraVento colors
   - Responsive on mobile/tablet/desktop
   - Consistent with existing form design

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
