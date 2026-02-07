# GPS Routes Manual Testing

Manual QA testing procedures for GPS route management and GPX file processing.

**Consolidated from**: `specs/003-gps-routes/MANUAL_TESTING.md` (Phase 3)

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [GPX Upload Testing](#gpx-upload-testing)
- [GPX Download Testing](#gpx-download-testing)
- [Map Visualization Testing](#map-visualization-testing)
- [Cascade Deletion Testing](#cascade-deletion-testing)
- [Error Handling Testing](#error-handling-testing)

---

## Overview

This guide consolidates manual testing procedures for GPS Routes features:

- **GPX Upload** - Upload small (<1MB) and large (>1MB) GPX files
- **GPX Download** - Download original GPX files (owner only)
- **Map Visualization** - Interactive map with route polyline and markers
- **Cascade Deletion** - Verify trackpoints deleted when trip deleted
- **Statistics Display** - Distance, elevation, altitude metrics

**Test Environment**: Local development (`http://localhost:5173`)

---

## Prerequisites

### 1. Start Backend Server

```bash
cd backend
./run-local-dev.sh              # Linux/Mac
.\run-local-dev.ps1             # Windows PowerShell

# Verify: http://localhost:8000/health
# Should return: {"success": true, "data": {"status": "healthy"}}
```

### 2. Start Frontend Server

```bash
cd frontend
npm run dev

# Frontend must be running at: http://localhost:5173
```

### 3. Create Test User and Trip

1. **Register test user**:
   - Navigate to: `http://localhost:5173/register`
   - Username: `testgpx`
   - Email: `testgpx@example.com`
   - Password: `TestGPX123!`

2. **Verify email** (development):
   ```bash
   cd backend
   poetry run python scripts/user-mgmt/create_verified_user.py --verify-email testgpx@example.com
   ```

3. **Create and publish trip**:
   - Login with test user
   - Create new trip: "Test Ruta GPS"
   - Description: "Viaje para probar funcionalidad de upload GPX"
   - **Important**: Publish the trip (GPX upload requires published trips)

4. **Prepare GPX test files**:
   ```bash
   mkdir test-gpx-files
   cp backend/tests/fixtures/gpx/short_route.gpx test-gpx-files/
   cp backend/tests/fixtures/gpx/camino_del_cid.gpx test-gpx-files/
   cp backend/tests/fixtures/gpx/long_route_5mb.gpx test-gpx-files/
   ```

---

## GPX Upload Testing

### Test Case: GPU-TC001 - Upload Small GPX File (<1MB)

**Objective**: Verify small GPX files process synchronously in <3 seconds (SC-002)

**Prerequisites**: Published trip without GPX file

**Steps**:
1. Navigate to trip detail page
2. Scroll to "Subir Archivo GPX" section
3. Upload file using one of these methods:
   - **Drag & Drop**: Drag `short_route.gpx` (2.8 KB) to dropzone
   - **Click**: Click dropzone, select file in dialog
4. Observe processing:
   - Start timer
   - Watch progress bar (0% → 100%)
   - Note "Procesando archivo GPX..." message
5. Wait for completion toast

**Expected Result**:
- ✅ Total processing time: **<3 seconds**
- ✅ Progress bar visible and functional
- ✅ Toast success: "Archivo GPX procesado correctamente"
- ✅ "Ruta GPS" section appears automatically
- ✅ Upload section disappears (only one GPX per trip)
- ✅ Statistics displayed:
  - **Distancia Total**: X.XX km (blue card)
  - **Desnivel Positivo**: X m (green card)
  - **Desnivel Negativo**: X m (orange card)
  - **Altitud Máxima**: X m (purple card)
  - **Altitud Mínima**: X m (teal card)

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPU-TC002 - Upload Large GPX File (>1MB)

**Objective**: Verify large file handling returns appropriate error

**Prerequisites**: Published trip without GPX file

**Steps**:
1. Create new test trip (or use trip without GPX)
2. Attempt to upload `long_route_5mb.gpx` (5.1 MB)
3. Observe error response

**Expected Result**:
- ✅ Error handled gracefully (no crash)
- ✅ Toast error: "Procesamiento asíncrono de archivos grandes aún no implementado"
- ✅ HTTP 501 "Not Implemented" status
- ✅ "Reintentar" button available
- ✅ Application remains functional

**Actual Result**: _[To be filled during test execution]_

**Note**: Asynchronous processing for files >1MB is not implemented in current MVP. This is expected behavior and documented for future implementation.

---

### Test Case: GPU-TC003 - Upload Validation (File Too Large)

**Objective**: Verify client-side validation for oversized files

**Prerequisites**: Published trip without GPX file

**Steps**:
1. Create test file >10MB:
   ```bash
   dd if=/dev/zero of=test-gpx-files/oversized.gpx bs=1M count=11
   ```
2. Attempt to upload `oversized.gpx`
3. Observe validation error

**Expected Result**:
- ✅ Error shown **before** backend request
- ✅ Message: "El archivo excede el tamaño máximo permitido (10 MB)"
- ✅ No network request to backend
- ✅ User can select different file

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPU-TC004 - Upload Validation (Invalid Format)

**Objective**: Verify backend validates GPX file format

**Prerequisites**: Published trip without GPX file

**Steps**:
1. Create fake GPX file:
   ```bash
   echo "Esto no es XML" > test-gpx-files/fake.gpx
   ```
2. Upload `fake.gpx`
3. Observe error from backend

**Expected Result**:
- ✅ Backend returns error (400 Bad Request)
- ✅ Toast error: "Error al procesar archivo GPX: formato inválido"
- ✅ Error message in Spanish
- ✅ Upload section remains visible (can retry)

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPU-TC005 - Prevent Duplicate GPX Upload

**Objective**: Verify only one GPX file allowed per trip

**Prerequisites**: Trip with GPX already uploaded

**Steps**:
1. Navigate to trip with GPX file
2. Verify upload section is hidden
3. Verify "Ruta GPS" section with statistics is visible
4. Attempt API call to upload second GPX (optional):
   ```bash
   curl -X POST http://localhost:8000/trips/{TRIP_ID}/gpx \
     -H "Authorization: Bearer {TOKEN}" \
     -F "file=@test-gpx-files/short_route.gpx"
   ```

**Expected Result**:
- ✅ Upload dropzone not visible
- ✅ Only "Ruta GPS" statistics section shown
- ✅ API call returns 400 Bad Request
- ✅ Error message: "Este viaje ya tiene un archivo GPX asociado"

**Actual Result**: _[To be filled during test execution]_

---

## GPX Download Testing

### Test Case: GPD-TC001 - Download GPX File (Owner)

**Objective**: Verify trip owner can download original GPX file (FR-039)

**Prerequisites**: Trip with GPX file, logged in as owner

**Steps**:
1. Navigate to trip detail page
2. Scroll to "Ruta GPS" section
3. Locate "Descargar GPX Original" button:
   - Blue button with download icon (⬇)
   - Centered horizontally below statistics
4. Open browser DevTools → Network tab (optional)
5. Click "Descargar GPX Original"
6. Observe download process
7. Verify file in Downloads folder
8. Compare with original file:
   ```bash
   # Windows PowerShell
   Compare-Object (Get-Content backend\tests\fixtures\gpx\short_route.gpx) `
                  (Get-Content $env:USERPROFILE\Downloads\Test_Ruta_GPS.gpx)

   # Linux/Mac
   diff backend/tests/fixtures/gpx/short_route.gpx ~/Downloads/Test_Ruta_GPS.gpx
   ```

**Expected Result**:
- ✅ Button visible only to trip owner
- ✅ Button has download icon and proper styling
- ✅ Click initiates download immediately
- ✅ Toast success: "Descargando archivo GPX original..."
- ✅ Network request: `GET /gpx/{gpx_file_id}/download` → 200 OK
- ✅ Filename: `{trip_title}.gpx` (sanitized, e.g., "Test_Ruta_GPS.gpx")
- ✅ File size matches original
- ✅ Content identical to uploaded file (diff shows no differences)
- ✅ File is valid XML (starts with `<?xml version="1.0"`)

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPD-TC002 - Download Button Hidden (Non-Owner)

**Objective**: Verify download button not visible to non-owners

**Prerequisites**: Trip with GPX file

**Steps**:
1. Logout from owner account
2. Login with different user (e.g., `maria_garcia`)
3. Navigate to same trip URL
4. Scroll to "Ruta GPS" section

**Expected Result**:
- ✅ Statistics cards visible
- ✅ "Descargar GPX Original" button **NOT** visible
- ✅ Owner-only restriction enforced

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPD-TC003 - Download via API

**Objective**: Verify GPX download endpoint directly

**Steps**:

**PowerShell (Windows)**:
```powershell
# Get GPX file ID
$tripId = "YOUR_TRIP_ID"
$response = Invoke-RestMethod -Uri "http://localhost:8000/trips/$tripId/gpx"
$gpxFileId = $response.data.gpx_file_id

# Download file
Invoke-WebRequest -Uri "http://localhost:8000/gpx/$gpxFileId/download" `
                  -OutFile "$env:USERPROFILE\Downloads\original.gpx"

# Verify file
Get-Content "$env:USERPROFILE\Downloads\original.gpx" -Head 5
```

**Bash (Linux/Mac)**:
```bash
# Get GPX file ID
TRIP_ID="YOUR_TRIP_ID"
GPX_FILE_ID=$(curl -s http://localhost:8000/trips/$TRIP_ID/gpx | jq -r '.data.gpx_file_id')

# Download file
curl -o ~/Downloads/original.gpx "http://localhost:8000/gpx/$GPX_FILE_ID/download"

# Verify file
head -n 5 ~/Downloads/original.gpx
```

**Expected Result**:
- ✅ Status: 200 OK
- ✅ Content-Type: `application/gpx+xml` or `application/octet-stream`
- ✅ Content-Disposition: `attachment; filename={trip_title}.gpx`
- ✅ File downloaded successfully
- ✅ Content matches original upload

**Actual Result**: _[To be filled during test execution]_

---

## Map Visualization Testing

### Test Case: GPM-TC001 - Interactive Map Display

**Objective**: Verify map shows GPS route with markers and auto-fit (FR-011, FR-012)

**Prerequisites**: Trip with uploaded GPX file

**Steps**:
1. Navigate to trip detail page
2. Scroll to "Ruta GPS" section
3. Observe map rendering
4. Verify map elements:
   - **Polyline** (route line):
     - Color: Red (#dc2626)
     - Weight: 3px
     - Opacity: 0.8
   - **Start Marker** (green):
     - Location: First trackpoint
     - Popup: "Inicio de ruta" + coordinates
   - **End Marker** (red):
     - Location: Last trackpoint
     - Popup: "Fin de ruta" + coordinates
5. Test map interactions:
   - Zoom in/out with buttons or mouse wheel
   - Pan by dragging map
   - Click start and end markers

**Expected Result**:
- ✅ Map loads with OpenStreetMap tiles
- ✅ Polyline connects all trackpoints correctly
- ✅ Start marker (green) at first point
- ✅ End marker (red) at last point
- ✅ Auto-fit: Entire route visible on load (padding: 50px)
- ✅ Zoom controls work smoothly
- ✅ Pan/drag works smoothly
- ✅ Marker popups show coordinates (5 decimal precision)
- ✅ Map loads in <3 seconds (SC-007)
- ✅ Zoom/pan response <200ms (SC-011)

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPM-TC002 - Map Responsive Design

**Objective**: Verify map displays correctly on mobile devices

**Steps**:
1. Open DevTools → Toggle device toolbar (Ctrl+Shift+M)
2. Select mobile device (iPhone 12 Pro, Pixel 5, etc.)
3. Navigate to trip with GPX
4. Scroll to map
5. Test touch interactions (if possible)

**Expected Result**:
- ✅ Map is responsive (100% width)
- ✅ Polyline and markers visible on mobile
- ✅ Touch drag for pan works
- ✅ Auto-fit bounds works same as desktop
- ✅ No horizontal scroll
- ✅ Controls accessible on small screens

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPM-TC003 - GPX vs Location Maps

**Objective**: Verify GPX map visually distinct from Location map

**Prerequisites**: Trip with both GPX file AND manual locations

**Steps**:
1. Navigate to trip detail page
2. Scroll to "Ruta GPS" section (GPX map)
3. Note visual appearance:
   - Polyline: **Red, solid**
   - Markers: **Green (start), Red (end)**
4. Scroll to "Ruta y Ubicaciones" section (Location map)
5. Note visual appearance:
   - Polyline: **Blue, dashed**
   - Markers: **Blue, numbered**

**Expected Result**:
- ✅ GPX route: Red solid polyline, green/red markers
- ✅ Location route: Blue dashed polyline, blue numbered markers
- ✅ Maps are visually distinct and independent
- ✅ No visual conflict between routes

**Actual Result**: _[To be filled during test execution]_

**Note**: If trip has no manual locations, only GPX map will appear.

---

## Cascade Deletion Testing

### Test Case: GCD-TC001 - Delete Trip with GPX

**Objective**: Verify GPX file and trackpoints deleted when trip deleted (FR-036)

**Prerequisites**: Trip with GPX file uploaded

**Steps**:

1. **Before deletion** - Count database records:
   ```bash
   cd backend
   poetry run python -c "
   from src.database import get_sync_db
   db = next(get_sync_db())

   gpx_count = db.execute('SELECT COUNT(*) FROM gpx_files').scalar()
   points_count = db.execute('SELECT COUNT(*) FROM track_points').scalar()

   print(f'GPX files: {gpx_count}')
   print(f'Track points: {points_count}')
   "
   ```

2. **Delete trip**:
   - Navigate to trip detail page
   - Click "Eliminar viaje" button (owner only)
   - Confirm deletion in modal
   - Verify toast: "Viaje eliminado correctamente"
   - Verify redirect to trips list

3. **After deletion** - Verify cascade:
   ```bash
   poetry run python -c "
   from src.database import get_sync_db
   db = next(get_sync_db())

   gpx_count = db.execute('SELECT COUNT(*) FROM gpx_files').scalar()
   points_count = db.execute('SELECT COUNT(*) FROM track_points').scalar()

   print(f'GPX files after: {gpx_count}')
   print(f'Track points after: {points_count}')
   "
   ```

4. **Verify file deletion**:
   ```bash
   # Physical file should be deleted
   ls -la backend/storage/gpx_files/
   # Trip folder should not exist
   ```

**Expected Result**:
- ✅ Trip deleted successfully
- ✅ GPX file deleted from database
- ✅ All trackpoints deleted from database (cascade)
- ✅ Physical GPX file deleted from `storage/gpx_files/`
- ✅ Toast confirmation shown
- ✅ Redirect to trips list
- ✅ User stats updated (trip count, distance)

**Actual Result**: _[To be filled during test execution]_

---

## Error Handling Testing

### Test Case: GPEH-TC001 - Network Tab Verification

**Objective**: Verify API requests and responses

**Steps**:
1. Open DevTools → Network tab
2. Upload GPX file
3. Monitor requests:
   - `POST /trips/{trip_id}/gpx` → 201 Created
   - `GET /gpx/{gpx_file_id}/track` → 200 OK
4. Inspect responses for correct structure

**Expected Result**:
- ✅ POST returns GPX metadata (distance, elevation, etc.)
- ✅ GET returns trackpoints array with sequence, lat, lng
- ✅ No 4xx or 5xx errors
- ✅ Response times <3s

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPEH-TC002 - Console Error Check

**Objective**: Verify no JavaScript errors during GPX operations

**Steps**:
1. Open DevTools → Console
2. Perform all GPX operations:
   - Upload file
   - View statistics
   - View map
   - Download file
   - Delete trip
3. Check for errors

**Expected Result**:
- ✅ No red errors in console
- ✅ Only informational logs (if any)
- ✅ No React warnings
- ✅ Leaflet tiles load successfully

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: GPEH-TC003 - API Error Handling

**Objective**: Verify graceful handling of API errors

**Steps**:

**Test 404 Error**:
```bash
curl http://localhost:8000/gpx/00000000-0000-0000-0000-000000000000/download
```

**Test Permission Error** (download as non-owner):
- Login as different user
- Try to download GPX via API with wrong user token

**Expected Result**:
- ✅ 404: Toast error "Archivo GPX no encontrado"
- ✅ 403: Toast error "No tienes permiso"
- ✅ 500: Toast error "Error del servidor. Intenta de nuevo."
- ✅ All errors in Spanish
- ✅ Application remains functional

**Actual Result**: _[To be filled during test execution]_

---

## Quality Checklist

### Functionality
- [ ] Upload small GPX (<1MB) completes in <3 seconds
- [ ] Upload large GPX (>1MB) returns 501 error as expected
- [ ] Download GPX original works (owner only)
- [ ] Map visualization displays route correctly
- [ ] Cascade deletion removes GPX and trackpoints
- [ ] Statistics cards show correct values
- [ ] Only one GPX per trip enforced

### UX
- [ ] Drag & drop works smoothly
- [ ] Progress bar visible during upload
- [ ] Toast notifications clear and helpful
- [ ] Button states update correctly (loading, disabled)
- [ ] Map is responsive on mobile
- [ ] All text in Spanish

### Performance
- [ ] Upload processing <3 seconds (SC-002)
- [ ] Map loads <3 seconds (SC-007)
- [ ] Zoom/pan response <200ms (SC-011)
- [ ] No memory leaks or performance degradation

### Data Integrity
- [ ] Statistics match GPX file data
- [ ] Trackpoints simplified (Douglas-Peucker algorithm)
- [ ] Original file preserved for download
- [ ] Cascade delete works correctly
- [ ] Database foreign key constraints enforced

---

## Known Issues

### ✅ Fixed Issues

1. **Download filename using trip title** (Fixed 2026-01-22)
   - Symptom: Downloaded file had original filename instead of trip title
   - Fix: Sanitize trip title and use as filename in FileResponse
   - Commit: 4353960

2. **Photo gallery lazy loading** (Fixed 2026-01-22)
   - Symptom: Gallery showed placeholders instead of images
   - Fix: Load first 6 images immediately, lazy load rest
   - Commit: d05124d

3. **Blank screen after publishing** (Fixed 2026-01-22)
   - Symptom: TripDetailPage blank after publish, required F5
   - Fix: Refetch complete trip data after publish
   - Commit: 2b429ad

### ⚠️ Known Limitations

1. **Async Processing**: Files >1MB return 501 Not Implemented
   - Expected behavior, documented for future implementation
   - Workaround: Use files <1MB for testing

2. **Tooltip on Polyline Hover**: Not implemented (deferred)
   - Future enhancement (T060)

3. **Map Layer Selector**: Not implemented (deferred)
   - Future enhancement (T061)

---

## Test Files Reference

**Recommended test files** (in `backend/tests/fixtures/gpx/`):

| File | Size | Points | Use Case |
|------|------|--------|----------|
| `short_route.gpx` | 2.8 KB | 10 | Basic upload/download testing |
| `camino_del_cid.gpx` | ~50 KB | 2000+ | Performance testing |
| `long_route_5mb.gpx` | 5.1 MB | 5000+ | Large file error testing |

---

## Related Documentation

- **[API Reference: GPX](../../api/endpoints/gpx.md)** - GPX endpoints specification
- **[E2E Tests](../frontend/e2e-tests.md)** - Automated Playwright tests for GPS features
- **[User Guide: Uploading GPX](../../user-guides/trips/uploading-gpx.md)** - End-user guide
- **[Feature: GPS Routes](../../features/gps-routes.md)** - Feature overview

---

**Last Updated**: 2026-02-07 (Consolidated from specs/003-gps-routes/)
**Features Tested**: GPX Upload, Download, Map Visualization, Cascade Deletion
**Test Environment**: Local development (SQLite backend, React frontend)
