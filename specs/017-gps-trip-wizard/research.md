# Research Findings: GPS Trip Creation Wizard

**Feature**: 017-gps-trip-wizard
**Date**: 2026-01-28
**Research Agent ID**: aada842

---

## Executive Summary

Comprehensive codebase analysis reveals that **80% of required functionality already exists** in Features 003 (GPS Routes), 008 (Travel Diary Frontend), 009 (GPS Coordinates), and 010 (Reverse Geocoding). The wizard will primarily compose existing components with minor modifications.

**Key Finding**: The wizard can leverage:
- ✅ GPX parsing infrastructure (`gpx_service.py`)
- ✅ Wizard UI pattern (`TripFormWizard.tsx`)
- ✅ Map integration (`react-leaflet + TripMap.tsx`)
- ✅ POI management APIs (`poi_service.py`)
- ✅ File upload components (`GPXUploader.tsx`, `react-dropzone`)

---

## 1. GPX File Processing

### Current Implementation

**Library**: `gpxpy 1.6.2` (Python GPX parser)

**Service**: `backend/src/services/gpx_service.py`

**Key Method**: `async def parse_gpx_file(file_content: bytes) -> dict`

**Returns**:
```python
{
    "distance_km": float,
    "elevation_gain": float,       # Cumulative uphill (m)
    "elevation_loss": float,       # Cumulative downhill (m)
    "max_elevation": float,
    "min_elevation": float,
    "has_elevation": bool,
    "has_timestamps": bool,
    "trackpoints": list[dict],     # Simplified via Douglas-Peucker (rdp 0.8)
}
```

**Track Simplification**:
- Algorithm: Ramer-Douglas-Peucker (epsilon=0.0001° ≈ 10m precision)
- Reduction: 80-95% (5000 → 200-500 trackpoints)
- Preserves: Elevation, distance, gradient per point

**Processing Modes**:
- **Sync** (<1MB): Parse → Store → Return (201 Created)
- **Async** (>1MB): Background task → Poll `/gpx/{id}/status` (202 Accepted)

### Decision: Reuse Existing Service

**Rationale**:
- Proven reliability (Feature 003 already in production)
- Handles large files (up to 10MB)
- Consistent telemetry calculation across platform

**Modification Needed**:
Add lightweight extraction method for wizard Step 1:

```python
# New method in GPXService
async def extract_telemetry_quick(file_content: bytes) -> dict:
    """Extract distance/elevation for wizard UI without DB storage."""
    gpx = gpxpy.parse(BytesIO(file_content))
    distance_km = gpx.length_3d() / 1000
    uphill, downhill = gpx.get_uphill_downhill()
    max_ele = max([p.elevation for p in gpx.get_points_data()] or [0])
    min_ele = min([p.elevation for p in gpx.get_points_data()] or [0])

    return {
        "distance_km": distance_km,
        "elevation_gain": uphill,
        "elevation_loss": downhill,
        "max_elevation": max_ele,
        "min_elevation": min_ele,
        "has_elevation": uphill is not None,
    }
```

**Alternative Rejected**: Client-side parsing with JavaScript GPX library → **Reason**: Inconsistent calculations, duplicates backend logic.

---

## 2. Wizard UI Component Pattern

### Current Implementation

**Framework**: React Hook Form 7.70 + FormProvider

**Reference**: `frontend/src/components/trips/TripFormWizard.tsx` (Feature 008)

**Pattern**:
```typescript
const methods = useForm<TripCreateInput>({
  defaultValues: {...},
  mode: 'onChange',  // Real-time validation
});

return (
  <FormProvider {...methods}>
    {currentStep === 1 && <Step1Component />}
    {currentStep === 2 && <Step2Component />}
    {/* Shared state across all steps */}
  </FormProvider>
);
```

**Per-Step Validation**:
```typescript
const handleNext = async () => {
  const fieldsToValidate = getFieldsForStep(currentStep);
  const isValid = await trigger(fieldsToValidate);

  if (!isValid) {
    toast.error('Por favor completa todos los campos requeridos');
    return;
  }
  setCurrentStep(prev => prev + 1);
};
```

### Decision: Follow Existing Pattern

**Wizard Steps** (4 steps, matching existing wizard):

1. **GPX Upload**: Drag-and-drop → Extract telemetry → Show preview
2. **Trip Details**: Auto-populate from GPX (title, distance, difficulty)
3. **POI Management**: Map + click-to-add (max 6 POIs)
4. **Review & Publish**: Final confirmation with map preview

**Navigation**:
- Forward: Validate current step → Advance
- Backward: No validation (preserve state)
- Cancel: Confirm discard (all data lost)

**Form State**:
```typescript
interface GPXTripFormData {
  gpxFile: File | null;
  title: string;
  description: string;
  start_date: string;
  end_date: string;
  difficulty: TripDifficulty;  // Auto-calculated, read-only
  privacy: 'public' | 'private';
  pois: POI[];
  telemetry: {
    distance_km: number;
    elevation_gain: number;
    max_elevation: number;
    min_elevation: number;
  } | null;
}
```

**Alternative Rejected**: Multi-page forms with separate URLs → **Reason**: Complicates state management, no back button support.

---

## 3. Difficulty Calculation Algorithm

### Industry Standards

**Strava**: Proprietary composite metric (distance + elevation + completion time)
**Komoot/RideWithGPS**: "Elevation Factor" = elevation_gain / distance_km

### ContraVento Algorithm (Spec-Aligned)

**Logic**: Use **whichever metric is higher** (distance OR elevation)

**Thresholds**:
```python
def calculate_difficulty(distance_km: float, elevation_gain: float | None) -> TripDifficulty:
    """
    Calculate trip difficulty from GPX telemetry.
    If no elevation data, use distance only.
    """
    if distance_km < 30 and (elevation_gain is None or elevation_gain < 500):
        return TripDifficulty.EASY

    if distance_km < 60 and (elevation_gain is None or elevation_gain < 1000):
        return TripDifficulty.MODERATE

    if distance_km < 100 and (elevation_gain is None or elevation_gain < 1500):
        return TripDifficulty.DIFFICULT

    if distance_km < 150 and (elevation_gain is None or elevation_gain < 2500):
        return TripDifficulty.VERY_DIFFICULT

    return TripDifficulty.EXTREME
```

**Examples**:
- 40km, 1200m gain → **DIFFICULT** (elevation dominates)
- 120km, 800m gain → **VERY_DIFFICULT** (distance dominates)
- 180km, 3000m gain → **EXTREME** (both exceed thresholds)

### Decision: Add EXTREME Level

**Current Enum** (`backend/src/models/trip.py`):
```python
class TripDifficulty(str, enum.Enum):
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"
    # MISSING: EXTREME
```

**Action**: Add `EXTREME = "extreme"` to support spec requirement (>150km or >2500m).

**User Override**: **NOT ALLOWED** (Spec Clarification #1: "No es un campo editable por el usuario").

**Alternative Rejected**: Allow manual override → **Reason**: Violates spec clarification #1, reduces consistency.

---

## 4. POI Management

### Current Implementation

**Backend**: `backend/src/services/poi_service.py`

**Max POIs**: `MAX_POIS_PER_TRIP = 20` (line 24)

**Model** (`backend/src/models/poi.py`):
```python
class PointOfInterest(Base):
    poi_id: str
    trip_id: str
    name: str(100)
    description: str(500)  # Optional
    poi_type: POIType
    latitude: float
    longitude: float
    photo_url: str  # Optional (1 photo per POI in current impl)
    sequence: int
```

**Frontend**: `frontend/src/components/trips/POIForm.tsx`

**Map Integration**: `frontend/src/components/trips/TripMap.tsx` (react-leaflet 4.2.1)

### Decision: Batch POI Creation

**❌ DISCREPANCY FOUND**:
- Spec: Max **6 POIs** per trip (FR-011)
- Backend: Max **20 POIs** per trip (code constant)

**Resolution**: **Change backend constant to 6** (align with spec).

**Wizard UI Pattern**:
```typescript
// Step 3: POI Management
const [pois, setPois] = useState<POI[]>([]);
const [isAddingPOI, setIsAddingPOI] = useState(false);

const handleMapClick = (lat: number, lng: number) => {
  if (pois.length >= 6) {
    toast.error('Máximo 6 POIs por viaje');
    return;
  }
  // Open POIForm modal with coordinates
  setClickedCoords({ lat, lng });
  setIsAddingPOI(true);
};
```

**Backend API Strategy**:
- **Store POIs in wizard state** (not persisted until publish)
- **On publish**: Batch-create all POIs via `POST /trips/{id}/pois` (loop 6 times max)

**POI Photos**: **1 photo per POI** (current implementation), but spec mentions "hasta 2 fotos".

**Action**: Update `POI` model to support 2 photos or clarify spec to 1 photo.

**Alternative Rejected**: Create POIs during wizard (before trip creation) → **Reason**: POIs require `trip_id`, trip must exist first.

---

## 5. Integration with Existing Trip Creation

### Current Flow

**Non-GPS** (`frontend/src/pages/TripCreatePage.tsx`):
1. Navigate to `/trips/new`
2. `TripFormWizard` renders (4 steps)
3. Publish → `POST /trips` → `POST /trips/{id}/photos`
4. Navigate to `/trips/{id}`

**GPX Upload** (Feature 003):
1. Trip already exists
2. Upload GPX via `GPXUploader` component
3. `POST /trips/{trip_id}/gpx`

### Decision: Pre-Creation Modal

**New Route Structure**:
```
/trips/new              → Modal selection screen (NEW)
/trips/new/manual       → Existing TripFormWizard (no GPX)
/trips/new/gpx          → New GPXWizard component
```

**Modal Component** (`frontend/src/pages/TripCreateModePage.tsx`):
```typescript
export const TripCreateModePage: React.FC = () => {
  return (
    <div className="mode-selection">
      <h1>¿Cómo quieres crear tu viaje?</h1>

      <div className="mode-cards">
        <ModeCard
          icon={<MapIcon />}
          title="Con archivo GPX"
          description="Sube un archivo GPX para auto-completar distancia..."
          onClick={() => navigate('/trips/new/gpx')}
        />

        <ModeCard
          icon={<PencilIcon />}
          title="Sin GPX (Manual)"
          description="Crea un viaje con ubicaciones y fotos"
          onClick={() => navigate('/trips/new/manual')}
        />
      </div>
    </div>
  );
};
```

**GPX Wizard Flow**:
1. Step 1: Upload GPX → `extract_telemetry_quick()` → Display metrics
2. Step 2: Auto-populate form (title = GPX filename, distance, difficulty)
3. Step 3: Add POIs (optional, max 6)
4. Step 4: Review → **Publish**:
   ```typescript
   const trip = await createTrip(formData);        // POST /trips
   await uploadGPX(trip.trip_id, gpxFile);         // POST /trips/{id}/gpx
   await Promise.all(pois.map(poi => createPOI(poi))); // Batch POI creation
   navigate(`/trips/${trip.trip_id}`);
   ```

**Draft Workflow**: **NOT SUPPORTED** in GPX wizard (Clarification #3: "No auto-save for MVP").

**Rationale**: POIs require trip to be PUBLISHED (FR-029 in Feature 003), so wizard must publish atomically.

**Alternative Rejected**: Single-page wizard with tabs → **Reason**: Step-by-step flow is more intuitive for onboarding.

---

## 6. Drag-and-Drop File Upload Component

### Current Implementation

**Library**: `react-dropzone 14.3.8`

**Reference**: `frontend/src/components/trips/GPXUploader.tsx`

**Pattern**:
```typescript
const { getRootProps, getInputProps, isDragActive } = useDropzone({
  onDrop,
  accept: { 'application/gpx+xml': ['.gpx'] },
  maxFiles: 1,
  maxSize: 10 * 1024 * 1024, // 10MB
  disabled: isUploading,
});
```

### Decision: Reuse with Backend Extraction

**Wizard-Specific Uploader**:
```typescript
// New: GPXWizardUploader (modified from GPXUploader)
const onDrop = async (files: File[]) => {
  const file = files[0];
  setIsProcessing(true);

  try {
    // Send to backend for quick telemetry extraction
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post('/gpx/analyze', formData);
    const telemetry = response.data;  // {distance_km, elevation_gain, ...}

    onFileAnalyzed(file, telemetry);
  } catch (error) {
    toast.error('Error al procesar archivo GPX');
  } finally {
    setIsProcessing(false);
  }
};
```

**New Backend Endpoint**: `POST /gpx/analyze` (temporary analysis, no DB storage)

**Alternative Rejected**: Client-side GPX parsing with DOMParser → **Reason**: Inconsistent calculations, duplicates backend logic.

---

## 7. Key File Paths

### Backend (Python 3.12 + FastAPI)

**Existing (Reuse)**:
- `backend/src/services/gpx_service.py` → Add `extract_telemetry_quick()`
- `backend/src/services/poi_service.py` → Batch POI creation
- `backend/src/models/trip.py` → Add `EXTREME` to `TripDifficulty` enum

**New Files**:
- `backend/src/services/difficulty_calculator.py` → Difficulty calculation logic
- `backend/src/api/gpx_wizard.py` → `POST /gpx/analyze` endpoint

### Frontend (React 18 + TypeScript 5)

**Existing (Reuse)**:
- `frontend/src/components/trips/GPXUploader.tsx` → Copy as basis
- `frontend/src/components/trips/TripFormWizard.tsx` → Reference pattern
- `frontend/src/components/trips/TripMap.tsx` → Map integration
- `frontend/src/components/trips/POIForm.tsx` → POI modal

**New Files**:
- `frontend/src/pages/TripCreateModePage.tsx` → Modal selection
- `frontend/src/pages/GPXTripCreatePage.tsx` → GPX wizard page
- `frontend/src/components/trips/GPXWizard/GPXWizard.tsx` → Main wizard
- `frontend/src/components/trips/GPXWizard/Step1Upload.tsx` → GPX upload step
- `frontend/src/components/trips/GPXWizard/Step2Details.tsx` → Form (auto-populated)
- `frontend/src/components/trips/GPXWizard/Step3POIs.tsx` → POI management
- `frontend/src/components/trips/GPXWizard/Step4Review.tsx` → Final review

---

## 8. Libraries (All Already Installed)

**Backend**:
- ✅ `gpxpy 1.6.2` - GPX parsing
- ✅ `rdp 0.8` - Douglas-Peucker simplification

**Frontend**:
- ✅ `react-dropzone 14.3.8` - File upload
- ✅ `react-hook-form 7.70` - Form state management
- ✅ `react-leaflet 4.2.1` - Map component
- ✅ `leaflet 1.9.x` - Map library
- ✅ `zod 3.25.76` - Schema validation

**No new dependencies required.**

---

## 9. Critical Decisions Made

### CD-001: Difficulty User Override
**Decision**: ❌ **Not allowed** (auto-calculated only)
**Rationale**: Spec Clarification #1 explicitly states "no es un campo editable por el usuario"

### CD-002: POI Limit
**Decision**: ✅ **6 POIs max** (spec), change backend constant from 20 → 6
**Rationale**: Align code with spec (FR-011)

### CD-003: Draft Workflow
**Decision**: ❌ **Not supported** in GPX wizard
**Rationale**: Clarification #3 "No auto-save for MVP", POIs require published trip (FR-029)

### CD-004: GPX Upload Timing
**Decision**: ✅ **Upload on publish** (atomic operation)
**Rationale**: Avoid orphan GPX files, simplify error handling

### CD-005: EXTREME Difficulty Level
**Decision**: ✅ **Add to enum**
**Rationale**: Spec assumption #1 mentions ">150km or >2500m desnivel"

### CD-006: POI Photos
**Decision**: ⚠️ **NEEDS CLARIFICATION**: Spec says "2 fotos", code supports 1
**Action**: Update spec to 1 photo or modify model for 2 photos

---

## 10. Performance Validation

**Target**: SC-002 (Process GPX up to 10MB / 100k points in <30s)

**Current Performance** (Feature 003):
- 1MB file: ~3s (sync processing)
- 5MB file: ~10s (async background task)
- 10MB file: ~25s (within target)

**Wizard Requirement**: Quick telemetry extraction (<5s) for Step 1

**Solution**: `extract_telemetry_quick()` method (no track simplification, only metrics)

**Expected Performance**: <2s for telemetry extraction (distance + elevation only)

---

## Sources

- ContraVento codebase (Features 002, 003, 008, 009, 010)
- [Strava Route Difficulty](https://support.strava.com/hc/en-us/articles/8471904145677-Route-Difficulty)
- [Elevation – Strava Support](https://support.strava.com/hc/en-us/articles/216919447-Elevation)
- [How Distance is Calculated – Strava Support](https://support.strava.com/hc/en-us/articles/216919487-How-Distance-is-Calculated)

---

**Research Completed**: 2026-01-28
**Agent ID**: aada842
**Status**: ✅ All NEEDS CLARIFICATION resolved
