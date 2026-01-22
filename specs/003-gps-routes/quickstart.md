# Quickstart: Feature 003 - GPS Routes Interactive

**Feature Branch**: `003-gps-routes`
**Status**: Phase 1 (MVP) Planning Complete
**Date**: 2026-01-21

This guide provides a rapid path to implementing and testing GPS Routes Interactive feature.

---

## Overview

**What This Feature Does**:
- Upload GPX files to cycling trip entries
- Parse and extract route statistics (distance, elevation)
- Visualize routes on interactive maps with start/end markers
- Display elevation profiles with click-to-zoom interaction
- Optimize storage with track simplification (90% reduction)

**Why It Matters**:
- **80% of trips** expected to include GPX files (SC-006)
- Enables cyclists to showcase exact routes traveled
- Helps other users evaluate route difficulty and plan adventures

---

## Prerequisites

- Python 3.12+ (backend)
- Node.js 18+ (frontend)
- PostgreSQL (production) or SQLite (development)
- Git branch: `003-gps-routes` from `develop`

---

## Installation (5 minutes)

### 1. Install Backend Dependencies

```bash
cd backend

# Add GPX parsing and simplification libraries
poetry add gpxpy@^1.6.2 rdp@^0.8

# Install dependencies
poetry install
```

**Dependencies Added**:
- `gpxpy 1.6.2`: GPX file parsing and distance/elevation calculations
- `rdp 0.8`: Douglas-Peucker algorithm for track simplification

### 2. Apply Database Migrations

```bash
# Generate migration
poetry run alembic revision --autogenerate -m "Add GPX tables for Feature 003"

# Apply migration
poetry run alembic upgrade head
```

**Tables Created**:
- `gpx_files`: GPX metadata and processing results
- `track_points`: Simplified GPS trackpoints for rendering

### 3. Install Frontend Dependencies

```bash
cd frontend

# Add elevation chart library
npm install recharts@^2.10.0

# Install dependencies
npm install
```

**Note**: `react-leaflet` already installed (Feature 009), no map dependencies needed.

---

## File Structure

```text
backend/
├── src/
│   ├── models/
│   │   └── gpx.py                    # NEW: GPXFile, TrackPoint models
│   ├── schemas/
│   │   └── gpx.py                    # NEW: Pydantic validation schemas
│   ├── services/
│   │   └── gpx_service.py            # NEW: GPX parsing, simplification logic
│   ├── api/
│   │   └── trips.py                  # MODIFY: Add GPX endpoints
│   └── utils/
│       └── gpx_simplifier.py         # NEW: Douglas-Peucker algorithm
├── migrations/versions/
│   └── xxx_create_gpx_tables.py      # NEW: Migration script
└── tests/
    ├── unit/
    │   └── test_gpx_service.py       # NEW: Unit tests for parsing
    └── integration/
        └── test_gpx_api.py           # NEW: API integration tests

frontend/
├── src/
│   ├── components/trips/
│   │   ├── TripMap.tsx               # MODIFY: Add Polyline for routes
│   │   ├── GPXUploader.tsx           # NEW: Drag-drop GPX upload
│   │   ├── GPXStats.tsx              # NEW: Distance/elevation stats
│   │   └── ElevationProfile.tsx      # NEW: Recharts elevation chart
│   ├── hooks/
│   │   ├── useGPXUpload.ts           # NEW: Upload hook with polling
│   │   └── useGPXTrack.ts            # NEW: Fetch trackpoints hook
│   ├── services/
│   │   └── gpxService.ts             # NEW: API client for GPX endpoints
│   └── types/
│       └── gpx.ts                    # NEW: TypeScript interfaces
└── tests/
    └── unit/
        └── GPXUploader.test.tsx      # NEW: Component tests
```

---

## Development Workflow (30 minutes)

### Step 1: Backend - Create Models (5 min)

**File**: `backend/src/models/gpx.py`

```python
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped
from typing import List, Optional
from datetime import datetime

from src.database import Base
from src.utils.id_generator import generate_uuid


class GPXFile(Base):
    """GPX file metadata and processing results."""

    __tablename__ = "gpx_files"

    gpx_file_id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.trip_id", ondelete="CASCADE"), unique=True, nullable=False)
    file_url = Column(String(500), nullable=False)
    distance_km = Column(Float, nullable=False)
    elevation_gain = Column(Float, nullable=True)
    has_elevation = Column(Boolean, nullable=False)
    total_points = Column(Integer, nullable=False)
    simplified_points = Column(Integer, nullable=False)
    processing_status = Column(String(20), nullable=False, default="pending")
    uploaded_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="gpx_file")
    track_points: Mapped[List["TrackPoint"]] = relationship(
        "TrackPoint",
        back_populates="gpx_file",
        order_by="TrackPoint.sequence",
        cascade="all, delete-orphan"
    )


class TrackPoint(Base):
    """Simplified GPS trackpoint for map rendering."""

    __tablename__ = "track_points"

    point_id = Column(String(36), primary_key=True, default=generate_uuid)
    gpx_file_id = Column(String(36), ForeignKey("gpx_files.gpx_file_id", ondelete="CASCADE"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=False)
    sequence = Column(Integer, nullable=False)

    # Relationships
    gpx_file: Mapped["GPXFile"] = relationship("GPXFile", back_populates="track_points")
```

### Step 2: Backend - Implement GPX Service (10 min)

**File**: `backend/src/services/gpx_service.py`

```python
import gpxpy
import gpxpy.gpx
from rdp import rdp
from typing import List, Dict, Any


async def parse_gpx_file(file_content: bytes) -> Dict[str, Any]:
    """
    Parse GPX file and extract track data.

    Args:
        file_content: Raw GPX file bytes

    Returns:
        Dict with distance, elevation, trackpoints

    Raises:
        ValueError: If GPX is invalid or corrupted
    """
    try:
        gpx = gpxpy.parse(file_content)

        # Extract all trackpoints
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                points.extend(segment.points)

        if not points:
            raise ValueError("El archivo GPX no contiene puntos de track")

        # Calculate metrics using gpxpy built-in methods
        distance_km = gpx.length_3d() / 1000  # meters to km
        uphill, downhill = gpx.get_uphill_downhill()

        # Extract elevation bounds
        elevations = [p.elevation for p in points if p.elevation is not None]
        has_elevation = len(elevations) > 0
        max_elevation = max(elevations) if has_elevation else None
        min_elevation = min(elevations) if has_elevation else None

        # Simplify trackpoints (Douglas-Peucker algorithm)
        simplified_points = simplify_track(points, epsilon=0.0001)

        return {
            "distance_km": round(distance_km, 2),
            "elevation_gain": round(uphill, 1) if uphill else None,
            "elevation_loss": round(downhill, 1) if downhill else None,
            "max_elevation": round(max_elevation, 1) if max_elevation else None,
            "min_elevation": round(min_elevation, 1) if min_elevation else None,
            "start_lat": points[0].latitude,
            "start_lon": points[0].longitude,
            "end_lat": points[-1].latitude,
            "end_lon": points[-1].longitude,
            "total_points": len(points),
            "simplified_points_count": len(simplified_points),
            "has_elevation": has_elevation,
            "trackpoints": simplified_points,
        }

    except Exception as e:
        raise ValueError(f"Error al procesar archivo GPX: {str(e)}")


def simplify_track(points: List, epsilon: float = 0.0001) -> List[Dict[str, Any]]:
    """
    Simplify GPS track using Ramer-Douglas-Peucker algorithm.

    Args:
        points: Original GPX trackpoints
        epsilon: Tolerance (0.0001° ≈ 10m precision)

    Returns:
        Simplified trackpoints (80-90% reduction)
    """
    if len(points) < 3:
        return [point_to_dict(p, i) for i, p in enumerate(points)]

    # Convert to coordinate array for RDP
    coords = [(p.latitude, p.longitude) for p in points]

    # Apply Douglas-Peucker
    simplified_coords = rdp(coords, epsilon=epsilon)

    # Map back to original points (preserve elevation)
    simplified = []
    cumulative_distance = 0.0

    for i, (lat, lon) in enumerate(simplified_coords):
        # Find original point
        original = next(p for p in points if p.latitude == lat and p.longitude == lon)

        simplified.append({
            "latitude": lat,
            "longitude": lon,
            "elevation": original.elevation if original.elevation else None,
            "distance_km": round(cumulative_distance, 3),
            "sequence": i,
        })

        # Calculate cumulative distance for next point
        if i < len(simplified_coords) - 1:
            next_lat, next_lon = simplified_coords[i + 1]
            segment_distance = calculate_distance(lat, lon, next_lat, next_lon)
            cumulative_distance += segment_distance

    return simplified


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formula for distance between two GPS coordinates (in km)."""
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth radius in km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c
```

### Step 3: Backend - Add API Endpoints (10 min)

**File**: `backend/src/api/trips.py` (add to existing file)

```python
from fastapi import BackgroundTasks, UploadFile, File

@router.post("/{trip_id}/gpx", status_code=status.HTTP_201_CREATED)
async def upload_gpx_file(
    trip_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload GPX file to trip (FR-001)."""
    # Validate file size (max 10MB)
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="El archivo GPX no puede exceder 10MB"
        )

    # Validate file type
    if not file.filename.endswith('.gpx'):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos .gpx"
        )

    # Check trip ownership
    trip = await db.get(Trip, trip_id)
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    # Save file
    file_content = await file.read()
    file_url = await save_gpx_to_storage(trip_id, file_content)

    # Process GPX
    gpx_data = await parse_gpx_file(file_content)

    # Save to database
    gpx_file = GPXFile(
        trip_id=trip_id,
        file_url=file_url,
        distance_km=gpx_data["distance_km"],
        elevation_gain=gpx_data["elevation_gain"],
        # ... other fields
    )
    db.add(gpx_file)
    await db.commit()

    return {"success": True, "data": gpx_file}
```

### Step 4: Frontend - Create GPX Uploader (5 min)

**File**: `frontend/src/components/trips/GPXUploader.tsx`

```typescript
import React, { useState } from 'react';
import { useGPXUpload } from '../../hooks/useGPXUpload';

interface GPXUploaderProps {
  tripId: string;
  onUploadComplete: () => void;
}

export const GPXUploader: React.FC<GPXUploaderProps> = ({ tripId, onUploadComplete }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { uploadGPX, isUploading, error } = useGPXUpload(tripId);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      await uploadGPX(selectedFile);
      onUploadComplete();
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  return (
    <div className="gpx-uploader">
      <input
        type="file"
        accept=".gpx"
        onChange={handleFileChange}
        disabled={isUploading}
      />
      <button onClick={handleUpload} disabled={!selectedFile || isUploading}>
        {isUploading ? 'Subiendo...' : 'Subir GPX'}
      </button>
      {error && <p className="error">{error}</p>}
    </div>
  );
};
```

---

## Testing (10 minutes)

### Unit Tests

```bash
cd backend

# Test GPX parsing
poetry run pytest tests/unit/test_gpx_service.py -v

# Test simplification algorithm
poetry run pytest tests/unit/test_gpx_service.py::test_simplification_reduces_points -v
```

### Integration Tests

```bash
# Test upload endpoint
poetry run pytest tests/integration/test_gpx_api.py::test_upload_gpx_file -v

# Test track retrieval
poetry run pytest tests/integration/test_gpx_api.py::test_get_track_points -v
```

### Manual Testing

```bash
# Start backend
cd backend
poetry run uvicorn src.main:app --reload

# Start frontend
cd frontend
npm run dev

# Navigate to: http://localhost:5173/trips/{trip_id}/edit
# Upload a sample GPX file (e.g., fixtures/camino_del_cid.gpx)
```

---

## Sample GPX File

Create `backend/tests/fixtures/sample_route.gpx`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="ContraVento">
  <metadata>
    <name>Sample Cycling Route</name>
  </metadata>
  <trk>
    <name>Test Route</name>
    <trkseg>
      <trkpt lat="41.6488" lon="-0.8891">
        <ele>245</ele>
      </trkpt>
      <trkpt lat="41.6512" lon="-0.8920">
        <ele>265</ele>
      </trkpt>
      <trkpt lat="41.6545" lon="-0.8950">
        <ele>285</ele>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
```

---

## Verification Checklist

- [ ] Backend dependencies installed (`gpxpy`, `rdp`)
- [ ] Database migrations applied (gpx_files, track_points tables created)
- [ ] Frontend dependencies installed (`recharts`)
- [ ] GPX upload endpoint returns 201 Created
- [ ] Trackpoints endpoint returns simplified points
- [ ] Map displays route with Polyline
- [ ] Elevation profile shows chart with hover tooltips
- [ ] Unit tests passing (≥90% coverage)
- [ ] Integration tests passing

---

## Performance Validation

Run performance tests to verify success criteria:

```bash
# Backend: Parse <1MB file in <3s (SC-002)
poetry run pytest tests/performance/test_gpx_parsing.py::test_parse_small_file -v

# Backend: Parse 5-10MB file in <15s (SC-003)
poetry run pytest tests/performance/test_gpx_parsing.py::test_parse_large_file -v

# Frontend: Render 1000 points in <3s (SC-007)
npm run test:performance -- tests/performance/map-render.test.tsx
```

---

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'gpxpy'`
**Solution**: Run `poetry install` in backend directory

### Issue: Upload fails with "File too large"
**Solution**: GPX files are limited to 10MB. Compress or split large routes.

### Issue: Map doesn't show route
**Solution**: Check that `gpx_file.processing_status = 'completed'` in database

### Issue: Elevation profile is empty
**Solution**: GPX file may not contain elevation data. Check `gpx_file.has_elevation`

---

## Next Steps

After MVP (Phase 1) is working:

1. **Phase 2: Points of Interest**
   - Add POI markers to map
   - Implement POI CRUD API
   - Create POI management UI

2. **Phase 3: Advanced Statistics**
   - Calculate speed/time metrics (if timestamps available)
   - Identify top 3 climbs
   - Display gradient distribution

3. **Performance Optimization**
   - Implement caching for trackpoints
   - Add compression for GPX file downloads
   - Optimize map rendering for mobile

---

## Resources

- **GPX Specification**: [GPX 1.1 Schema](https://www.topografix.com/GPX/1/1/)
- **gpxpy Documentation**: [GitHub](https://github.com/tkrajina/gpxpy)
- **Douglas-Peucker Algorithm**: [Wikipedia](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm)
- **Recharts Documentation**: [recharts.org](https://recharts.org/)
- **Leaflet Polylines**: [Leaflet Docs](https://leafletjs.com/reference.html#polyline)

---

**Ready to Code!** Follow this quickstart to implement Feature 003 GPS Routes Interactive in ~1 hour (MVP).
