# Phase 0 Research: Travel Diary Frontend

**Feature**: Travel Diary Frontend
**Branch**: `008-travel-diary-frontend`
**Date**: 2026-01-10
**Status**: Complete

## Overview

This document captures research decisions for implementing the Travel Diary frontend feature. All decisions are based on:

1. **Existing codebase patterns** from Features 005 and 007
2. **Performance requirements** from spec.md (SC-001 to SC-012)
3. **Constitutional requirements** from constitution.md
4. **Technical constraints** from plan.md

## Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **1. Multi-Step Form** | React Hook Form with persistent state | Already in use, proven pattern, no extra dependencies |
| **2. Photo Upload** | Chunked uploads (3 at a time) | Balances performance and user feedback |
| **3. Tag Autocomplete** | Fetch all on mount | Simple, fast, matches existing patterns |
| **4. Map Integration** | react-leaflet + OpenStreetMap | Free, lightweight, constitutional performance requirement |
| **5. Lightbox Library** | yet-another-react-lightbox | Modern, lightweight, best mobile support |
| **6. Draft Persistence** | No persistence (session-only) | Simplest for MVP, backend draft API handles published state |

---

## Decision 1: Multi-Step Form Pattern

### Question
How to preserve form data across steps without losing unsaved changes in the 4-step trip creation wizard?

### Decision: React Hook Form with Persistent State

**Implementation Approach**:
- Use React Hook Form (already in `package.json` v7.70.0) with a single form instance managing all 4 steps
- Store entire form state in parent component (`TripFormWizard`)
- Each step component receives form methods via props (no Context needed for 4 steps)
- Use `useUnsavedChanges` hook (already exists) to warn on navigation
- Track current step with local state (`currentStep: 1-4`)

**Code Pattern** (based on Feature 007 `BasicInfoSection.tsx`):
```typescript
// TripFormWizard.tsx
const { register, handleSubmit, watch, formState: { errors, isDirty } } = useForm<TripFormData>({
  resolver: zodResolver(tripFormSchema),
  defaultValues: { /* initial values */ }
});

const [currentStep, setCurrentStep] = useState(1);
useUnsavedChanges(isDirty); // Existing hook from Feature 007

const allFormData = watch(); // Access full form state for review step

return (
  <>
    {currentStep === 1 && <Step1BasicInfo register={register} errors={errors} />}
    {currentStep === 2 && <Step2StoryTags register={register} errors={errors} />}
    {currentStep === 3 && <Step3Photos formData={allFormData} />}
    {currentStep === 4 && <Step4Review formData={allFormData} />}
  </>
);
```

**Alternatives Considered**:

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| **State management (Redux/Zustand)** | Centralized state, dev tools | Extra dependency (10-30kb), overkill for 4 steps | Constitutional simplicity requirement, existing pattern works |
| **LocalStorage persistence** | Survives refresh | Sync complexity, stale data issues, privacy concerns | Backend draft API handles persistence (FR-028) |
| **React Hook Form Context** | Cleaner prop drilling | Unnecessary for 4 steps, adds complexity | Props are sufficient for small wizard |

**Constitutional Alignment**:
- ✅ **Code Quality**: Leverages existing dependency (React Hook Form 7.x)
- ✅ **Performance**: No extra bundle size, `watch()` is efficient for small forms
- ✅ **UX Consistency**: Matches Feature 007 profile editing pattern
- ✅ **Testing**: Proven pattern from Feature 007 (already tested)

**Success Criteria Mapping**:
- **SC-006**: Form preserves data across navigation with 100% accuracy (React Hook Form state persistence)
- **SC-008**: Users publish on first attempt 90% of the time (validation per step reduces errors)

---

## Decision 2: Photo Upload Strategy

### Question
How to handle bulk photo uploads (up to 20 photos, 10MB each) with progress tracking while maintaining responsiveness?

### Decision: Chunked Uploads (3 photos at a time)

**Implementation Approach**:
- Upload photos in batches of 3 using `Promise.allSettled()` (prevents one failure from blocking others)
- Display individual progress bars for each photo in current chunk
- Queue remaining photos until current chunk completes
- Use existing `photoService.uploadPhoto()` pattern with `onUploadProgress` callback

**Code Pattern** (extends Feature 007 `usePhotoUpload.ts`):
```typescript
const uploadPhotosChunked = async (files: File[]) => {
  const CHUNK_SIZE = 3;
  const results = [];

  for (let i = 0; i < files.length; i += CHUNK_SIZE) {
    const chunk = files.slice(i, i + CHUNK_SIZE);

    // Upload chunk in parallel
    const chunkResults = await Promise.allSettled(
      chunk.map((file, index) =>
        uploadTripPhoto(tripId, file, (progress) => {
          setUploadProgress(prev => ({ ...prev, [i + index]: progress }));
        })
      )
    );

    results.push(...chunkResults);
  }

  return results;
};
```

**Alternatives Considered**:

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| **Sequential uploads** | Simple, easy to debug | 5 photos × 6s = 30s (violates SC-003) | Too slow, poor UX |
| **Parallel uploads (all at once)** | Fastest for small batches | Browser connection limit (6-8), network congestion, poor progress feedback for 20 photos | Exceeds browser limits, violates SC-003 for large batches |
| **Chunked (5 at a time)** | More parallelism | More network contention, harder to show progress | 3 is optimal for 10MB files on standard broadband |

**Performance Analysis**:
- **Sequential**: 5 photos × 6s = 30s ✅ (meets SC-003: <30s for 5MB total)
- **Chunked (3)**: 5 photos ÷ 3 chunks × 6s = ~12s ✅ (2x faster)
- **Chunked (3)**: 20 photos ÷ 7 chunks × 6s = ~42s for max load (acceptable)

**Constitutional Alignment**:
- ✅ **Performance**: Meets SC-003 (<30s for 5 photos, 5MB total)
- ✅ **UX Consistency**: Individual progress bars with error retry (FR-041)
- ✅ **Code Quality**: Extends existing `photoService.ts` pattern

**Success Criteria Mapping**:
- **SC-003**: Photo upload completes in <30s for 5 photos (5MB total) - ✅ ~12s
- **SC-007**: Drag-and-drop accepts valid files, rejects invalid with clear errors
- **FR-041**: Handle upload failures with retry option per file

---

## Decision 3: Tag Autocomplete Implementation

### Question
How to provide tag suggestions as users type without complex debouncing or excessive API calls?

### Decision: Fetch All Tags on Mount

**Implementation Approach**:
- Fetch all tags once when `TagInput` component mounts: `GET /api/tags`
- Store tags in local state (expected <1000 tags, ~20kb payload)
- Filter client-side as user types (no debouncing needed)
- Display top 10 matches sorted by `usage_count`

**Code Pattern**:
```typescript
const TagInput: React.FC = () => {
  const [allTags, setAllTags] = useState<Tag[]>([]);
  const [suggestions, setSuggestions] = useState<Tag[]>([]);

  useEffect(() => {
    // Fetch all tags once on mount
    const fetchTags = async () => {
      const tags = await getAllTags(); // GET /api/tags
      setAllTags(tags.sort((a, b) => b.usage_count - a.usage_count));
    };
    fetchTags();
  }, []);

  const handleInputChange = (value: string) => {
    if (!value.trim()) {
      setSuggestions([]);
      return;
    }

    // Client-side filtering (instant)
    const filtered = allTags
      .filter(tag => tag.normalized.includes(value.toLowerCase()))
      .slice(0, 10);

    setSuggestions(filtered);
  };

  return (
    <div>
      <input onChange={(e) => handleInputChange(e.target.value)} />
      {suggestions.map(tag => <TagSuggestion key={tag.id} tag={tag} />)}
    </div>
  );
};
```

**Alternatives Considered**:

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| **Debounced API search** | Works for millions of tags | Network latency (200-500ms), complexity, extra API load | <1000 tags expected, unnecessary complexity |
| **Hybrid (cache + API)** | Best for large datasets | Complex cache invalidation, staleness issues | Over-engineering for <1000 tags |

**Performance Analysis**:
- Tag payload: ~20kb for 1000 tags (name + usage_count)
- Client-side filtering: <10ms for 1000 items (instant)
- Network fetch: ~200ms (once on mount, then cached)
- **Total**: 200ms initial load, then instant filtering

**Constitutional Alignment**:
- ✅ **Performance**: SC-005 requires <500ms tag filtering - ✅ ~10ms
- ✅ **Code Quality**: Simple, no debouncing complexity
- ✅ **UX Consistency**: Instant feedback (matches existing input patterns)

**Success Criteria Mapping**:
- **SC-005**: Tag filtering updates trip list in <500ms - ✅ <10ms client-side
- **FR-020**: Autocomplete suggestions based on existing tags

---

## Decision 4: Map Integration

### Question
Which mapping library balances features, bundle size, and cost for displaying trip locations?

### Decision: react-leaflet 4.x + OpenStreetMap

**Implementation Approach**:
- Install `react-leaflet@4.x` and `leaflet@1.9.x` (~50kb gzipped)
- Use OpenStreetMap tiles (free, no API key required)
- Display trip location marker if `TripLocation` exists (FR-014)
- Lazy load map component (only render when trip has location)

**Code Pattern**:
```typescript
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const TripMap: React.FC<{ location: TripLocation }> = ({ location }) => {
  const position: [number, number] = [location.latitude, location.longitude];

  return (
    <MapContainer center={position} zoom={10} style={{ height: '400px' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      <Marker position={position}>
        <Popup>{location.address || 'Ubicación del viaje'}</Popup>
      </Marker>
    </MapContainer>
  );
};

// Lazy load map (only when trip has location)
const TripDetailPage = () => {
  return trip.location ? <TripMap location={trip.location} /> : null;
};
```

**Alternatives Considered**:

| Option | Bundle Size | Cost | Features | Rejected Because |
|--------|-------------|------|----------|------------------|
| **react-map-gl + Mapbox** | ~100kb | Free tier (50k loads/month) | Better UX, vector tiles, 3D | Requires API key, exceeds constitutional performance requirement |
| **Google Maps** | ~150kb | $200/month for 10k users | Familiar, street view | Paid API (cost), large bundle, violates performance requirement |
| **react-leaflet + OpenStreetMap** | ~50kb | Free (unlimited) | Good UX, sufficient features | ✅ **SELECTED** |

**Constitutional Alignment**:
- ✅ **Performance**: 50kb gzipped (minimal impact on SC-004: <2s page load)
- ✅ **Code Quality**: Well-maintained library (4M+ downloads/week)
- ✅ **Security**: No API keys to manage, no sensitive data exposure
- ✅ **Cost**: Free (OpenStreetMap), no vendor lock-in

**Success Criteria Mapping**:
- **SC-004**: Trip list page loads in <2s (50kb map library has minimal impact)
- **FR-014**: Display trip location on interactive map

**Implementation Notes**:
- Map component is **optional** (only shown if trip has location)
- Most trips won't have location initially (out of scope for MVP per spec.md)
- Can enhance with route display in future (Feature 003 integration)

---

## Decision 5: Lightbox Library Selection

### Question
Best photo viewer library for mobile + desktop with keyboard navigation and zoom?

### Decision: yet-another-react-lightbox 2.x

**Implementation Approach**:
- Install `yet-another-react-lightbox@2.x` (~30kb gzipped)
- Use plugins for thumbnails, zoom, and keyboard navigation
- Integrate with `TripGallery` component for photo viewing

**Code Pattern**:
```typescript
import Lightbox from 'yet-another-react-lightbox';
import Thumbnails from 'yet-another-react-lightbox/plugins/thumbnails';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
import 'yet-another-react-lightbox/styles.css';
import 'yet-another-react-lightbox/plugins/thumbnails.css';

const TripGallery: React.FC<{ photos: TripPhoto[] }> = ({ photos }) => {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [photoIndex, setPhotoIndex] = useState(0);

  const slides = photos.map(photo => ({
    src: photo.url,
    alt: photo.caption || 'Foto del viaje',
    width: photo.width,
    height: photo.height,
  }));

  return (
    <>
      <div className="photo-grid">
        {photos.map((photo, index) => (
          <img
            key={photo.id}
            src={photo.thumbnail_url}
            alt={photo.caption || 'Foto del viaje'}
            onClick={() => { setPhotoIndex(index); setLightboxOpen(true); }}
          />
        ))}
      </div>

      <Lightbox
        open={lightboxOpen}
        close={() => setLightboxOpen(false)}
        slides={slides}
        index={photoIndex}
        plugins={[Thumbnails, Zoom]}
      />
    </>
  );
};
```

**Alternatives Considered**:

| Option | Bundle Size | Mobile Support | Features | Rejected Because |
|--------|-------------|----------------|----------|------------------|
| **react-image-lightbox** | ~40kb | Good | Mature, stable | No longer maintained (last update 2020) |
| **react-photoswipe** | ~60kb | Excellent | Feature-rich, gestures | Complex setup, large bundle |
| **yet-another-react-lightbox** | ~30kb | Excellent | Modern, TypeScript, plugins | ✅ **SELECTED** |

**Feature Comparison**:

| Feature | react-image-lightbox | react-photoswipe | yet-another-react-lightbox |
|---------|---------------------|------------------|---------------------------|
| Keyboard nav | ✅ | ✅ | ✅ |
| Touch gestures | ⚠️ Basic | ✅ Advanced | ✅ Advanced |
| Thumbnails | ❌ | ✅ | ✅ (plugin) |
| Zoom | ✅ | ✅ | ✅ (plugin) |
| TypeScript | ❌ | ⚠️ Types only | ✅ Native |
| Active maintenance | ❌ | ✅ | ✅ |
| Bundle size | 40kb | 60kb | 30kb |

**Constitutional Alignment**:
- ✅ **Performance**: 30kb gzipped (minimal impact on SC-004)
- ✅ **UX Consistency**: Touch gestures for mobile (SC-010)
- ✅ **Code Quality**: TypeScript native, active maintenance
- ✅ **Accessibility**: Keyboard navigation, ARIA labels

**Success Criteria Mapping**:
- **SC-009**: Lightbox transitions in <300ms (hardware-accelerated CSS)
- **SC-010**: Mobile users can complete all interactions (touch gestures)
- **FR-011**: Lightbox with prev/next navigation

---

## Decision 6: Draft Persistence Strategy

### Question
Should in-progress trip forms persist across browser sessions (survive page refresh)?

### Decision: No Persistence (Session-Only with Warning)

**Implementation Approach**:
- Form state lives in React Hook Form (decision #1) - **session-only**
- Use `useUnsavedChanges` hook to warn on navigation/refresh (already exists)
- Users must explicitly save as draft (FR-028: "Save as Draft" button)
- Backend `/api/trips` with `status=draft` handles persistent drafts

**User Flow**:
```
User fills form (Step 1-3) → Clicks "Save as Draft" → Backend saves trip
User refreshes page → Form resets (data not lost, saved in backend)
User navigates to "My Drafts" → Sees saved draft → Clicks "Edit" → Loads draft into form
```

**Code Pattern** (reuses existing patterns):
```typescript
const TripFormWizard = () => {
  const { isDirty } = useForm<TripFormData>();
  useUnsavedChanges(isDirty); // Warns: "You have unsaved changes. Are you sure you want to leave?"

  const handleSaveDraft = async () => {
    const draftData = { ...formData, status: 'draft' };
    await createTrip(draftData); // POST /api/trips (FR-028)
    toast.success('Borrador guardado');
    navigate('/trips'); // Safe navigation (isDirty now false)
  };

  return (
    <>
      {/* Steps 1-4 */}
      <button onClick={handleSaveDraft}>Guardar como Borrador</button>
    </>
  );
};
```

**Alternatives Considered**:

| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| **LocalStorage persistence** | Survives refresh | Sync complexity with backend drafts, data staleness, privacy issues, doesn't survive device change | Backend draft API (FR-028) is source of truth, LocalStorage creates dual state |
| **Backend draft API** | Survives device change, single source of truth | Already implemented (FR-028), requires explicit save | ✅ **SELECTED** (not rejected - this is the solution) |
| **Auto-save to backend** | Seamless UX | API spam, network latency, partial drafts clutter database | Constitutional performance requirement (avoid unnecessary API calls) |

**Why This Decision**:

1. **Backend draft API already exists** (FR-028, FR-032): POST /api/trips with `status=draft`
2. **LocalStorage creates dual state problems**:
   - User saves draft in backend → closes tab → reopens → LocalStorage overrides backend data
   - User edits draft on mobile → switches to desktop → LocalStorage out of sync
3. **Explicit save is clearer UX**:
   - User knows exactly when data is persisted
   - "Save as Draft" button makes action explicit (SC-008: 90% publish on first attempt means clear expectations)
4. **`useUnsavedChanges` prevents accidental loss**:
   - Browser shows: "You have unsaved changes. Are you sure you want to leave?"
   - User can return to form or explicitly save draft

**Constitutional Alignment**:
- ✅ **Code Quality**: Reuses existing hook (`useUnsavedChanges`), no new dependencies
- ✅ **UX Consistency**: Matches backend draft pattern (explicit save)
- ✅ **Performance**: No LocalStorage sync overhead, no auto-save API spam
- ✅ **Security**: No sensitive data in LocalStorage (privacy risk)

**Success Criteria Mapping**:
- **SC-006**: Form preserves data across step navigation (React Hook Form state)
- **SC-008**: 90% publish on first attempt (explicit save reduces confusion)
- **FR-028**: "Save as Draft" option (backend API)
- **FR-036**: Unsaved changes warning (existing `useUnsavedChanges` hook)

---

## Implementation Impact

### New Dependencies to Install

```bash
cd frontend
npm install react-dropzone@14.x        # Drag-and-drop file uploads (~15kb)
npm install yet-another-react-lightbox@2.x  # Photo lightbox (~30kb)
npm install react-leaflet@4.x leaflet@1.9.x # Map display (~50kb)
```

**Total bundle size impact**: ~95kb gzipped (acceptable per SC-004: <2s page load)

### Existing Dependencies Leveraged

- ✅ `react-hook-form@7.70.0` (Decision #1: multi-step form)
- ✅ `zod@3.25.76` (form validation schemas)
- ✅ `axios@1.6.5` (photo upload with progress tracking)
- ✅ `react-hot-toast@2.6.0` (error/success notifications)

### Existing Hooks/Services Reused

- ✅ `useUnsavedChanges` (Decision #1, #6)
- ✅ `photoService.ts` pattern (Decision #2)
- ✅ `tripsService.ts` (Decision #6: draft API calls)

---

## Risk Assessment

| Risk | Mitigation | Status |
|------|------------|--------|
| **Bundle size exceeds 2s load** | Lazy load map component, code splitting for lightbox | ✅ Mitigated |
| **Photo upload failures** | Chunked uploads with individual retry (FR-041) | ✅ Mitigated |
| **Form data loss on refresh** | `useUnsavedChanges` warning + explicit draft save | ✅ Mitigated |
| **Tag API grows beyond 1000 items** | Client-side pagination or debounced API search | ⚠️ Monitor (unlikely in MVP) |
| **Map API rate limiting** | OpenStreetMap is free and unlimited | ✅ No risk |

---

## Next Steps

**Phase 1: Design & Contracts** (create these files):

1. **data-model.md**: TypeScript interfaces for Trip, TripPhoto, Tag, TripLocation
2. **contracts/trips-frontend-api.md**: API integration specs (endpoints, request/response examples)
3. **quickstart.md**: Developer setup guide (install deps, run dev server, test endpoints)

**Phase 2: Implementation** (based on research decisions):

1. Install new dependencies (react-dropzone, yet-another-react-lightbox, react-leaflet)
2. Create `TripFormWizard` with React Hook Form (Decision #1)
3. Implement `PhotoUploader` with chunked uploads (Decision #2)
4. Build `TagInput` with client-side filtering (Decision #3)
5. Add `TripMap` component (Decision #4, lazy loaded)
6. Integrate lightbox in `TripGallery` (Decision #5)
7. Wire up draft save with backend API (Decision #6)

---

## Approval Status

**Research Complete**: ✅ All 6 decisions documented with rationale
**Constitutional Check**: ✅ All decisions align with constitution requirements
**Ready for Phase 1**: ✅ Proceed to Design & Contracts

**Reviewers**: (to be added after review)

**Date Completed**: 2026-01-10
