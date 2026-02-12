# GPS Routes & Maps - ContraVento

Learn how to visualize and interact with GPS routes on interactive maps.

**Audience**: End-users, cyclists exploring routes
**Difficulty**: 🟢 Basic

---

## Table of Contents

- [Overview](#overview)
- [Map Features](#map-features)
- [Route Visualization](#route-visualization)
- [Interactive Controls](#interactive-controls)
- [Location Markers](#location-markers)
- [Map Layers](#map-layers)
- [Mobile Maps](#mobile-maps)
- [Troubleshooting](#troubleshooting)

---

## Overview

ContraVento displays GPS routes from uploaded GPX files on **interactive maps** powered by Leaflet.js and OpenStreetMap.

**Key Features**:
- 🗺️ **Interactive maps** with zoom, pan, full-screen
- 📍 **Route polylines** showing exact path
- 📌 **Location markers** with clickable popups
- 🎨 **Multiple map layers** (street, satellite, terrain)
- 📈 **Elevation profile sync** (click chart → map centers)
- 📱 **Mobile-responsive** with touch controls
- ⚡ **Optimized performance** with simplified trackpoints

**Map Provider**: OpenStreetMap (free, open-source mapping)

---

## Map Features

### Map Components

When you view a trip with GPX data, the map displays:

```
┌──────────────────────────────────────────┐
│  [−]  [+]  [⛶]          Map Controls     │ ← Top-right controls
├──────────────────────────────────────────┤
│                                           │
│    ┌─ Start marker (green)               │
│    │                                      │
│    🟢─────────────────────────────┐      │
│    │  Route polyline (blue)       │      │
│    │                               │      │
│    │         📍 Location marker    │      │
│    │                               │      │
│    │                               │      │
│    └───────────────────────────────🔴    │
│                             End marker    │
│                                  (red)    │
│                                           │
│  © OpenStreetMap contributors             │ ← Attribution
└──────────────────────────────────────────┘
```

**Visual Elements**:
- **Start marker (green)**: First trackpoint of route
- **End marker (red)**: Last trackpoint of route
- **Route polyline (blue)**: Continuous line connecting trackpoints
- **Location markers (purple)**: Points of interest you added
- **Active profile point (orange)**: Synced with elevation chart hover

---

### Map Controls (Top-Right)

```
┌─────┐
│  −  │  Zoom out
├─────┤
│  +  │  Zoom in
├─────┤
│  ⛶  │  Full-screen mode
└─────┘
```

**Keyboard Shortcuts**:
- **+** or **=**: Zoom in
- **-** or **_**: Zoom out
- **Esc**: Exit full-screen
- **Arrow keys**: Pan map

---

## Route Visualization

### Route Polyline

The **blue line** shows your exact GPS track from the GPX file.

**Polyline Properties**:
- **Color**: Blue (#3b82f6)
- **Width**: 3px (desktop), 4px (mobile)
- **Opacity**: 90%
- **Smoothing**: Simplified for performance (~200-500 points)

**Example Route**:

```
Original GPX: 5,234 trackpoints (every 1-2 seconds)
Displayed:    287 trackpoints (Douglas-Peucker simplified)
Shape:        99.8% identical to original
Performance:  ~10x faster rendering
```

**Why Simplification?**:
- Faster map loading (<2s vs >10s for 5,000 points)
- Smoother panning and zooming
- Lower memory usage
- Better mobile performance

---

### Start and End Markers

**Start Marker (Green)**:

```
🟢 ← Green circle with white border
Located at: First trackpoint of GPX
Popup: "Inicio" (click to show)
```

**End Marker (Red)**:

```
🔴 ← Red circle with white border
Located at: Last trackpoint of GPX
Popup: "Fin" (click to show)
```

**Click Marker**:

```
Popup appears:
┌──────────────────────────────┐
│  Inicio                       │
│  43.2951°N, 0.3708°W          │
│  Elevación: 183 m             │
└──────────────────────────────┘
```

---

### Auto-Zoom to Fit Route

When trip loads, map automatically:

1. Calculates bounding box of entire route
2. Zooms to fit all trackpoints in viewport
3. Adds padding for visual comfort

**Example**:

```
Route bounds:
- North: 43.2951°N
- South: 42.8456°N
- East: 0.3708°W
- West: 1.2345°W

Map zooms to show all trackpoints with 10% padding
```

---

## Interactive Controls

### Zoom Controls

**Method 1: Zoom Buttons**

```
Click [+] to zoom in (1 level)
Click [−] to zoom out (1 level)

Zoom levels: 1 (world) to 18 (street level)
```

**Method 2: Mouse Wheel**

```
Scroll up: Zoom in
Scroll down: Zoom out

Smooth zoom animation
```

**Method 3: Double-Click**

```
Double-click on map: Zoom in 1 level centered on click point
```

**Method 4: Pinch Zoom (Mobile)**

```
Pinch out: Zoom in
Pinch in: Zoom out

Multi-touch gesture
```

---

### Pan Controls

**Method 1: Click and Drag**

```
1. Click on map (hold mouse button)
2. Drag in any direction
3. Release to stop panning

Inertia: Map continues moving briefly after release
```

**Method 2: Keyboard Arrows**

```
↑: Pan north
↓: Pan south
←: Pan west
→: Pan east

Hold key for continuous pan
```

---

### Full-Screen Mode

**Activate Full-Screen**:

```
1. Click [⛶] button (top-right)

2. Map expands to fill entire browser window:
   ┌────────────────────────────────────┐
   │  Full-screen map                   │
   │                                     │
   │    🟢─────────────────────┐        │
   │    │                      │        │
   │    │                      🔴       │
   │                                     │
   │  Press ESC to exit                  │
   └────────────────────────────────────┘
```

**Exit Full-Screen**:
- Press **Esc** key
- Click **✕** button (top-right)

**Benefits**:
- Better route visibility
- More screen real estate
- Immersive exploration

---

## Location Markers

### Adding Location Markers

If trip has **locations** (added via reverse geocoding or manually), they appear as **purple markers**.

**Location Marker**:

```
📍 ← Purple location pin
Positioned at: Latitude/Longitude coordinates
Popup: Location name + coordinates
```

**Click Location Marker**:

```
Popup shows:
┌──────────────────────────────────┐
│  Col d'Aubisque                   │
│  42.9732°N, 0.3896°W              │
│  Elevación: 2,115 m               │
└──────────────────────────────────┘
```

**See**: [Locations Guide](locations.md) for adding/editing location markers (future guide).

---

### Location Marker Features

**Clickable**:
- Click to open popup with location details
- Click again to close popup

**Draggable** (edit mode only):
- Drag marker to adjust coordinates
- Triggers reverse geocoding to update name

**Deletable** (edit mode only):
- Click "✕" in popup to delete marker

---

## Map Layers

ContraVento offers multiple map layers from different providers.

### Available Layers

**1. OpenStreetMap (Default)**:
- **Style**: Street map with roads, cities, landmarks
- **Data**: OpenStreetMap contributors
- **Best for**: Urban routes, road cycling, navigation

**2. OpenTopoMap** (Future):
- **Style**: Topographic map with contour lines
- **Data**: SRTM elevation data + OpenStreetMap
- **Best for**: Mountain biking, hiking, elevation awareness

**3. Satellite** (Future):
- **Style**: Satellite imagery (Esri WorldImagery)
- **Data**: Recent satellite photos
- **Best for**: Terrain visualization, off-road routes

---

### Switching Layers (Future Feature)

**Planned UI**:

```
Layer Control (top-right):
┌──────────────────────┐
│  Base Maps:           │
│  ◉ OpenStreetMap      │ ← Selected
│  ○ OpenTopoMap        │
│  ○ Satellite          │
└──────────────────────┘

Click to switch layer
```

---

## Mobile Maps

### Touch Controls

**Zoom**:
- **Pinch out**: Zoom in
- **Pinch in**: Zoom out
- **Double-tap**: Zoom in 1 level

**Pan**:
- **Swipe**: Pan in any direction
- **Inertia**: Map continues moving after swipe

**Full-Screen**:
- Tap [⛶] button to enter full-screen
- Tap [✕] or swipe down to exit

---

### Mobile Optimizations

**Performance**:
- Route polyline width increased to 4px (easier to see)
- Markers have larger touch targets (44×44px minimum)
- Simplified trackpoints for faster rendering

**Layout**:
- Map height: 400px (portrait), 300px (landscape)
- Full-screen mode recommended for exploration
- Elevation profile below map (can scroll)

**Responsive Design**:
- Map adapts to screen size automatically
- Controls scale appropriately
- Touch gestures optimized

---

## Troubleshooting

### Map Doesn't Load

**Possible Causes**:

1. **Network error**:
   - Check internet connection
   - Refresh page (Ctrl+R or Cmd+R)

2. **Ad blocker**:
   - Some ad blockers block map tiles
   - Whitelist contravento.com

3. **GPX file missing**:
   - Trip has no GPX uploaded
   - Map shows placeholder message

**Solution**:

```
1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Disable ad blocker for ContraVento
3. Try different browser (Chrome, Firefox, Safari)
```

---

### Map Shows Blank Gray Tiles

**Cause**: OpenStreetMap tile server not responding

**Solution**:

1. **Wait 30 seconds**: Tiles may be loading slowly

2. **Zoom in/out**: Triggers tile reload

3. **Pan slightly**: Forces tile refresh

4. **Check OpenStreetMap status**:
   - Visit: status.openstreetmap.org
   - If down, wait for recovery (usually <1 hour)

---

### Route Polyline Not Visible

**Possible Causes**:

1. **Zoomed out too far**:
   - Zoom in to see route details
   - Auto-zoom may have failed

2. **Route outside viewport**:
   - Pan to find route
   - Click "Centrar en ruta" button (if available)

3. **Transparent polyline** (CSS issue):
   - Hard refresh: Ctrl+Shift+R

**Solution**:

```
1. Click "Centrar en ruta" button
2. Or zoom out to level 8-10 to see entire route
```

---

### Map Stutters When Panning

**Cause**: Too many trackpoints or slow device

**Solution**:

1. **Simplify GPX** before upload:
   - Use online tool (gotoes.org/strava/GPX_Simplify.php)
   - Reduce from 5,000 → 500 trackpoints

2. **Use lower zoom level**:
   - Zoom out to reduce rendering load

3. **Close other browser tabs**:
   - Free up memory

4. **Update browser**:
   - Ensure latest version of Chrome/Firefox/Safari

---

### Full-Screen Mode Not Working

**Cause**: Browser restriction or pop-up blocker

**Solution**:

1. **Allow full-screen** in browser settings:
   - Chrome: Site settings → Permissions → Full-screen

2. **Disable pop-up blocker**:
   - Some blockers prevent full-screen

3. **Use F11** (Windows) or Cmd+Ctrl+F (Mac):
   - Browser full-screen (alternative)

---

### Location Markers Not Clickable

**Cause**: Z-index issue or JavaScript error

**Solution**:

1. **Hard refresh**: Ctrl+Shift+R

2. **Disable browser extensions**:
   - Some extensions interfere with maps

3. **Try different browser**:
   - Chrome, Firefox, Safari, Edge

---

### Map Doesn't Resize on Mobile

**Cause**: CSS or viewport issue

**Solution**:

1. **Rotate device**:
   - Trigger resize event

2. **Reload page**:
   - Ctrl+R or pull down to refresh

3. **Clear browser cache**:
   - Settings → Clear data

---

## Related Guides

- **[Uploading GPX](../trips/uploading-gpx.md)** - How to add GPS routes
- **[Elevation Profile](elevation-profile.md)** - Interactive elevation charts (future guide)
- **[Locations](locations.md)** - Adding location markers (future guide)
- **[Creating Trips](../trips/creating-trips.md)** - Trip creation basics

---

## Related Documentation

- **[API: GPX Endpoints](../../api/endpoints/gpx.md)** - GPX API for developers
- **[Architecture: GPX Processing](../../architecture/integrations/gpx-processing.md)** - Technical details
- **[Manual Testing: GPS Testing](../../testing/manual-qa/gps-testing.md)** - QA for maps

---

**Last Updated**: 2026-02-07
**Difficulty**: 🟢 Basic
**Estimated Reading Time**: 8 minutes
