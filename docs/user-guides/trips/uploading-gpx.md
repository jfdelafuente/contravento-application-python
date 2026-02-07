# Uploading GPX Files - ContraVento

Learn how to upload GPS routes to your cycling trips with GPX files.

**Audience**: End-users, cyclists documenting routes
**Difficulty**: 🟢 Basic

---

## Table of Contents

- [Overview](#overview)
- [What is a GPX File?](#what-is-a-gpx-file)
- [How to Upload GPX](#how-to-upload-gpx)
- [Map Visualization](#map-visualization)
- [Elevation Profile](#elevation-profile)
- [GPX Statistics](#gpx-statistics)
- [Downloading GPX](#downloading-gpx)
- [Troubleshooting](#troubleshooting)

---

## Overview

ContraVento allows you to upload GPX (GPS Exchange Format) files to your trips to display:

- 🗺️ **Interactive route map** with polyline
- 📈 **Elevation profile** with gradient visualization
- 📊 **Automatic statistics** (distance, elevation gain/loss)
- 📍 **Trackpoints** showing your exact path
- ⬇️ **Download original file** to share routes

**Key Features**:
- Supports GPX 1.0 and 1.1 formats
- Handles files up to 10MB
- Automatic simplification for performance (Douglas-Peucker algorithm)
- Works with or without elevation data

---

## What is a GPX File?

**GPX (GPS Exchange Format)** is an XML-based file format for storing GPS data.

### Where to Get GPX Files

**1. GPS Devices**:
- Garmin Edge, Wahoo ELEMNT, Hammerhead Karoo
- Export route after ride from device

**2. Mobile Apps**:
- Strava (export activity as GPX)
- Komoot (download route as GPX)
- Ride with GPS (export GPX)

**3. Route Planning Tools**:
- komoot.com
- ridewithgps.com
- brouter.de

**4. Your Own Recording**:
- Use ContraVento mobile app (future feature)
- Use any GPS tracker app on your phone

### GPX File Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1">
  <metadata>
    <name>Bikepacking Pirineos</name>
  </metadata>
  <trk>
    <name>Day 1: Pau to Lourdes</name>
    <trkseg>
      <trkpt lat="43.2951" lon="-0.3708">
        <ele>183.5</ele>
        <time>2024-06-01T08:00:00Z</time>
      </trkpt>
      <!-- More trackpoints... -->
    </trkseg>
  </trk>
</gpx>
```

**Key Elements**:
- `<trkpt>`: Individual GPS point (latitude, longitude)
- `<ele>`: Elevation in meters (optional)
- `<time>`: Timestamp (optional)

---

## How to Upload GPX

### Option 1: During Trip Creation (Wizard)

**Step 1: Create Trip**

```
1. Click "Crear Viaje" from dashboard
2. Fill basic information (Step 1)
3. Add story and tags (Step 2)
4. Upload photos (Step 3) - optional
5. Continue to Step 4 (Review)
```

**Step 2: Upload GPX in Wizard**

```
On Step 4 (Review):
1. Click "Añadir Ruta GPS" or drag GPX file to dropzone
2. Wait for processing (usually <5 seconds)
3. Verify route appears on map preview
4. Review auto-calculated statistics
5. Click "Guardar" or "Publicar"
```

---

### Option 2: Add GPX to Existing Trip

**Step 1: Navigate to Trip**

```
1. Go to "Mis Viajes"
2. Click on trip (must be owner)
3. Click "Editar" button
```

**Step 2: Upload GPX**

```
In Edit Mode:
1. Scroll to "Ruta GPS" section
2. Click "Subir GPX" or drag file
3. Wait for processing
4. Click "Guardar Cambios"
```

**Result**: Route map and elevation profile appear on trip detail page.

---

### Upload Progress States

**1. Uploading**:
```
┌─────────────────────────────┐
│  Subiendo archivo GPX...    │
│  ████████░░░░░░░░░░░  45%   │
└─────────────────────────────┘
```

**2. Processing**:
```
┌─────────────────────────────┐
│  Procesando ruta GPS...     │
│  Calculando estadísticas... │
└─────────────────────────────┘
```

**3. Success**:
```
┌─────────────────────────────┐
│  ✓ Ruta GPS cargada         │
│  285.5 km • 3,420m D+       │
└─────────────────────────────┘
```

**4. Error**:
```
┌─────────────────────────────┐
│  ✗ Error al procesar GPX    │
│  Archivo no válido o        │
│  demasiado grande (>10MB)   │
└─────────────────────────────┘
```

---

## Map Visualization

After uploading GPX, the trip detail page displays an **interactive map** with your route.

### Map Features

**Route Polyline**:
- Blue line showing your exact path
- Automatically zooms to fit entire route
- Clickable for details

**Trackpoints** (simplified):
- ~200-500 points for performance
- Original GPX may have 5,000+ points
- Douglas-Peucker algorithm preserves shape

**Map Controls**:
- **Zoom**: +/- buttons or mouse wheel
- **Pan**: Click and drag
- **Full Screen**: Expand to full viewport
- **Layers**: Switch between street/satellite/terrain

### Map Interaction

**Click on Route**:
- Shows nearest trackpoint details
- Displays elevation (if available)
- Shows distance from start

**Hover on Route**:
- Highlights section
- Shows gradient (uphill/downhill/flat)

---

## Elevation Profile

If your GPX file includes elevation data, ContraVento displays an **interactive elevation chart**.

### Chart Features

**Visual Elements**:
- X-axis: Distance (km)
- Y-axis: Elevation (meters)
- Color coding by gradient:
  - 🟢 **Green**: Uphill (0-3% gentle, 3-6% moderate, 6-10% steep, >10% very steep)
  - 🔵 **Blue**: Downhill (0 to -3% gentle, -3 to -6% moderate, -6 to -10% steep, <-10% very steep)
  - ⚫ **Gray**: Flat (±0.5%)

**Interactive Tooltip**:
```
Hover over chart:
┌─────────────────────────────┐
│  Distancia: 42.3 km         │
│  Elevación: 1,245 m         │
│  Pendiente: 5.2% (subida)   │
└─────────────────────────────┘
```

**Click on Chart**:
- Map centers on that point (<300ms)
- Shows location marker
- Syncs with route polyline

**Hover on Chart**:
- Orange pulsating marker follows cursor on map
- Real-time sync between chart and map

### Example Elevation Profile

```
Elevation (m)
2000 │            ╱╲
     │          ╱    ╲
1500 │        ╱        ╲
     │      ╱            ╲
1000 │    ╱                ╲___
     │  ╱                      ╲
 500 │╱                          ╲
     └─────────────────────────────
     0   50  100  150  200  250  300  Distance (km)
```

**Colors**:
- Green sections: Climbs (uphill)
- Blue sections: Descents (downhill)
- Gray sections: Flat terrain

---

## GPX Statistics

ContraVento automatically calculates statistics from your GPX file.

### Auto-Populated Fields

**1. Distance (km)**:
```
Calculated from: Sum of distances between consecutive trackpoints
Formula: Haversine distance (great-circle distance)
Example: 285.5 km
```

**2. Elevation Gain (m)**:
```
Calculated from: Sum of positive elevation changes
Only if GPX has <ele> tags
Example: 3,420 m D+ (meters of climbing)
```

**3. Elevation Loss (m)**:
```
Calculated from: Sum of negative elevation changes
Only if GPX has <ele> tags
Example: 3,380 m D- (meters of descent)
```

**4. Max Elevation (m)**:
```
Highest point on route
Example: 2,115 m (Col d'Aubisque)
```

**5. Min Elevation (m)**:
```
Lowest point on route
Example: 183 m (Pau valley)
```

**6. Average Gradient (%)**:
```
Calculated from: (Total Elevation Gain / Distance) × 100
Example: 1.2% average
```

### Statistics Display

**On Trip Detail Page**:
```
┌───────────────────────────────────────┐
│  📏 Distancia: 285.5 km               │
│  ⛰️  Desnivel: 3,420m D+ / 3,380m D-  │
│  📈 Elevación máx: 2,115 m            │
│  📉 Elevación mín: 183 m              │
│  📊 Pendiente media: 1.2%             │
└───────────────────────────────────────┘
```

**Important**: If you manually enter distance in trip form, **GPX distance overrides** it when uploaded.

---

## Downloading GPX

You can download the **original GPX file** to share routes or use in other apps.

### How to Download

**On Trip Detail Page**:
```
1. Scroll to "Ruta GPS" section
2. Click "Descargar GPX Original" button
3. File downloads as: trip_title_original.gpx
```

**Uses**:
- Import into Garmin/Wahoo device
- Share with friends
- Edit in route planning tools
- Backup of original data

**Important**: Downloaded file is the **original** you uploaded, not the simplified version displayed on map.

---

## Troubleshooting

### "Invalid GPX file" Error

**Possible Causes**:
1. **Not a GPX file**: File is KML, KMZ, TCX, or other format
   - **Solution**: Convert to GPX using online tool (e.g., gpsvisualizer.com)

2. **Corrupted XML**: File has syntax errors
   - **Solution**: Validate GPX at gpx-validator.com

3. **Empty file**: GPX has no trackpoints
   - **Solution**: Ensure GPX has `<trk>` → `<trkseg>` → `<trkpt>` elements

4. **Wrong GPX version**: Unsupported GPX version
   - **Solution**: ContraVento supports GPX 1.0 and 1.1 only

---

### "File too large" Error (>10MB)

**Cause**: GPX file exceeds 10MB limit

**Solution**:
1. **Simplify GPX** using online tool:
   - gotoes.org/strava/GPX_Simplify.php
   - mapstogpx.com/gpx-simplify
2. **Reduce trackpoint density** from 5,000 → 500 points
3. **Remove timestamps** if not needed (reduces file size)

**Example**:
```bash
# Original GPX: 15MB, 8,000 trackpoints
# Simplified GPX: 2MB, 800 trackpoints (same route shape)
```

---

### "No elevation data" Message

**Cause**: GPX file lacks `<ele>` tags in trackpoints

**Result**:
- Map displays route correctly ✅
- Elevation profile shows "No elevation data available" ⚠️
- Statistics show distance but no elevation gain/loss

**Solution** (optional):
1. **Add elevation** using online tool:
   - gpsvisualizer.com (DEM lookup)
   - ridewithgps.com (add elevation from SRTM data)
2. **Re-upload** GPX with elevation data

**Example**:
```xml
<!-- Before (no elevation) -->
<trkpt lat="43.2951" lon="-0.3708" />

<!-- After (with elevation) -->
<trkpt lat="43.2951" lon="-0.3708">
  <ele>183.5</ele>
</trkpt>
```

---

### Map Shows Different Route than Expected

**Possible Causes**:
1. **Wrong GPX file uploaded**: Check filename
   - **Solution**: Delete GPX and upload correct file

2. **Route simplified too much**: Douglas-Peucker removed details
   - **Solution**: Route shape is preserved, but <1% of points shown

3. **Coordinates out of bounds**: Lat/lng errors in GPX
   - **Solution**: Validate GPX coordinates (lat: -90 to 90, lng: -180 to 180)

---

### Upload Stuck at "Processing..."

**Cause**: Large GPX file (>5MB) or slow connection

**Solution**:
1. **Wait**: Processing can take up to 30 seconds for large files
2. **Check console**: Open browser DevTools (F12) → Console for errors
3. **Reload page**: If stuck >1 minute, refresh and try again
4. **Simplify GPX**: Reduce file size if >5MB

---

### Downloaded GPX Different from Map

**Expected Behavior**: Downloaded file is **original GPX**, not simplified version.

**Explanation**:
- **Map display**: Uses simplified GPX (~200-500 points) for performance
- **Download**: Returns original GPX (all trackpoints, elevation, timestamps)

**Why?**:
- Original GPX: Full fidelity for GPS devices
- Simplified GPX: Faster web rendering

---

## Related Guides

- **[Creating Trips](creating-trips.md)** - Trip creation wizard
- **[Adding Photos](adding-photos.md)** - Photo upload workflow
- **[GPS Routes](../maps/gps-routes.md)** - Map visualization details
- **[Elevation Profile](../maps/elevation-profile.md)** - Interactive chart usage

---

## Related Documentation

- **[API: GPX Endpoints](../../api/endpoints/gpx.md)** - For developers
- **[Architecture: GPX Processing](../../architecture/integrations/gpx-processing.md)** - Technical details
- **[Manual Testing: GPS Testing](../../testing/manual-qa/gps-testing.md)** - QA procedures

---

**Last Updated**: 2026-02-07
**Difficulty**: 🟢 Basic
**Estimated Reading Time**: 8 minutes
