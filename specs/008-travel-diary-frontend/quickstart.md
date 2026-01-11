# Developer Quickstart: Travel Diary Frontend

**Feature**: 008-travel-diary-frontend
**Date**: 2026-01-10
**Status**: Phase 1 - Design & Contracts

## Overview

This guide provides step-by-step instructions for setting up and developing the Travel Diary frontend feature. Follow these steps to get up and running quickly.

**Prerequisites**:
- Node.js 18+ installed
- Backend running (Feature 002: Travel Diary Backend)
- Authenticated user session (Feature 005: Frontend User Authentication)

---

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
cd frontend

# Install new dependencies for Travel Diary
npm install react-dropzone@14.x                  # Drag-and-drop file uploads
npm install yet-another-react-lightbox@2.x       # Photo lightbox viewer
npm install react-leaflet@4.x leaflet@1.9.x      # Map display (optional)

# Verify installation
npm list | grep -E "react-dropzone|yet-another-react-lightbox|react-leaflet|leaflet"
```

**Expected Output**:
```
├── react-dropzone@14.2.10
├── yet-another-react-lightbox@2.6.2
├── react-leaflet@4.2.1
└── leaflet@1.9.4
```

**Total Bundle Impact**: ~95kb gzipped (acceptable per SC-004: <2s page load)

---

### 2. Start Development Server

```bash
# Terminal 1: Backend (if not already running)
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

**Expected Output**:
```
  VITE v5.0.8  ready in 1245 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.10:5173/
```

---

### 3. Verify Backend APIs

Test that all required endpoints are available:

```bash
# Get all tags (public endpoint)
curl http://localhost:8000/api/tags

# Expected: {"success": true, "data": {"tags": [...], "count": N}, "error": null}

# Get user trips (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/users/testuser/trips

# Expected: {"success": true, "data": {"trips": [...], "total": N}, "error": null}
```

**Authentication Note**: Use Feature 005 login flow to get JWT token.

---

## Project Structure

### New Files to Create

```
frontend/
├── src/
│   ├── components/trips/              # NEW: Trip components
│   │   ├── TripCard.tsx               # Trip preview card (list view)
│   │   ├── TripCard.css
│   │   ├── TripFilters.tsx            # Search + tag filters
│   │   ├── TripFilters.css
│   │   ├── TripGallery.tsx            # Photo grid with lightbox
│   │   ├── TripGallery.css
│   │   ├── TripForm/                  # Multi-step form wizard
│   │   │   ├── TripFormWizard.tsx     # Main wizard controller
│   │   │   ├── TripFormWizard.css
│   │   │   ├── Step1BasicInfo.tsx     # Step 1: Title, dates, distance, difficulty
│   │   │   ├── Step2StoryTags.tsx     # Step 2: Description, tags
│   │   │   ├── Step3Photos.tsx        # Step 3: Photo upload
│   │   │   ├── Step4Review.tsx        # Step 4: Summary + publish
│   │   │   └── FormStepIndicator.tsx  # Visual step progress
│   │   ├── PhotoUploader.tsx          # Drag-and-drop upload component
│   │   ├── PhotoUploader.css
│   │   ├── TagInput.tsx               # Tag input with autocomplete
│   │   └── TripMap.tsx                # Map display (optional)
│   │
│   ├── pages/                         # NEW: Trip pages
│   │   ├── TripsListPage.tsx          # Browse trips with filters
│   │   ├── TripsListPage.css
│   │   ├── TripDetailPage.tsx         # Full trip view
│   │   ├── TripDetailPage.css
│   │   ├── TripCreatePage.tsx         # Create new trip (wizard)
│   │   ├── TripCreatePage.css
│   │   ├── TripEditPage.tsx           # Edit existing trip (wizard)
│   │   └── TripEditPage.css
│   │
│   ├── hooks/                         # NEW: Trip hooks
│   │   ├── useTripForm.ts             # Multi-step form state management
│   │   ├── useTripPhotos.ts           # Photo upload/delete/reorder logic
│   │   ├── useTripFilters.ts          # Search + tag filtering state
│   │   └── useTripList.ts             # Paginated trip list with caching
│   │
│   ├── services/                      # NEW: Trip services
│   │   ├── tripService.ts             # Trip CRUD API calls
│   │   └── tripPhotoService.ts        # Photo upload/delete API calls
│   │
│   ├── types/                         # NEW: Trip types
│   │   └── trip.ts                    # TypeScript interfaces (Trip, TripPhoto, Tag)
│   │
│   └── utils/                         # NEW: Trip utilities
│       ├── tripValidators.ts          # Zod schemas for trip forms
│       └── tripHelpers.ts             # Utility functions (date formatting, difficulty badges)
│
└── public/images/trips/placeholders/  # NEW: Empty state images
    └── no-trips-empty-state.svg
```

---

## Development Workflow

### Phase 2: Implementation (Current Phase)

Follow this order for best results:

#### **2.1. Foundation (Day 1-2)**

1. **Create TypeScript types** (`src/types/trip.ts`):
   - Copy interfaces from [data-model.md](data-model.md)
   - Export all types

2. **Create API services** (`src/services/tripService.ts`, `tripPhotoService.ts`):
   - Implement all 10 endpoints from [contracts/trips-frontend-api.md](contracts/trips-frontend-api.md)
   - Add error handling with toast notifications

3. **Create Zod validation schemas** (`src/utils/tripValidators.ts`):
   - `tripFormSchema` (for form validation)
   - `tripPublishSchema` (for publish validation)

4. **Create utility helpers** (`src/utils/tripHelpers.ts`):
   - `formatDate()`, `formatDateTime()`
   - `getDifficultyLabel()`, `getDifficultyClass()`

**Verification**:
```bash
npm run type-check  # Should pass with no errors
```

---

#### **2.2. User Story P1: View Trip List (Day 3-4)**

Implement trip browsing with filters (SC-001, SC-004, SC-005).

**Components**:
1. `TripCard.tsx` - Trip preview card
2. `TripFilters.tsx` - Search + tag filters
3. `TripsListPage.tsx` - Main list page with pagination

**Hooks**:
1. `useTripList.ts` - Fetch trips with filters
2. `useTripFilters.ts` - Manage filter state

**Test Checklist**:
- [ ] Trips load in <2s (SC-004)
- [ ] Tag filtering updates in <500ms (SC-005)
- [ ] Pagination works (12 trips per page)
- [ ] Empty state displays when no trips

**Manual Testing**:
```bash
# Navigate to http://localhost:5173/trips
# Expected: See grid of trip cards
# Click tag chip → trips filter by tag
# Search for "Pirineos" → trips filter by keyword
```

---

#### **2.3. User Story P1: View Trip Details (Day 5)**

Implement trip detail view with photo gallery (SC-009).

**Components**:
1. `TripGallery.tsx` - Photo grid with lightbox
2. `TripDetailPage.tsx` - Full trip view

**Dependencies**:
```typescript
// src/components/trips/TripGallery.tsx
import Lightbox from 'yet-another-react-lightbox';
import Thumbnails from 'yet-another-react-lightbox/plugins/thumbnails';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
import 'yet-another-react-lightbox/styles.css';
```

**Test Checklist**:
- [ ] Full trip data displays
- [ ] Photos open in lightbox
- [ ] Lightbox transitions in <300ms (SC-009)
- [ ] Keyboard navigation works (arrows, ESC)
- [ ] Mobile touch gestures work (SC-010)

---

#### **2.4. User Story P1: Create Trip (Day 6-8)**

Implement multi-step form wizard (SC-002, SC-006, SC-008).

**Components**:
1. `TripFormWizard.tsx` - Main wizard controller
2. `Step1BasicInfo.tsx` - Title, dates, distance, difficulty
3. `Step2StoryTags.tsx` - Description, tags
4. `Step3Photos.tsx` - Photo upload
5. `Step4Review.tsx` - Summary + publish
6. `FormStepIndicator.tsx` - Visual step progress
7. `TagInput.tsx` - Tag autocomplete
8. `PhotoUploader.tsx` - Drag-and-drop upload
9. `TripCreatePage.tsx` - Page wrapper

**Hooks**:
1. `useTripForm.ts` - Form state across steps
2. `useTripPhotos.ts` - Photo upload logic

**Key Pattern** (from research.md Decision #1):
```typescript
// TripFormWizard.tsx
const { register, handleSubmit, watch, formState: { errors, isDirty } } = useForm<TripFormData>({
  resolver: zodResolver(tripFormSchema),
});

const [currentStep, setCurrentStep] = useState(1);
useUnsavedChanges(isDirty); // Existing hook from Feature 007

const allFormData = watch();

return (
  <>
    {currentStep === 1 && <Step1BasicInfo register={register} errors={errors} />}
    {currentStep === 2 && <Step2StoryTags register={register} errors={errors} />}
    {currentStep === 3 && <Step3Photos tripId={tripId} />}
    {currentStep === 4 && <Step4Review formData={allFormData} />}
  </>
);
```

**Test Checklist**:
- [ ] Form preserves data across steps (SC-006)
- [ ] Unsaved changes warning on navigation
- [ ] Validation errors display per step
- [ ] Tags autocomplete from existing tags
- [ ] Photos upload with progress bars (SC-003)
- [ ] Draft saves without validation
- [ ] Publish enforces 50-char description (SC-008)

**Manual Testing**:
```bash
# Navigate to http://localhost:5173/trips/new
# Fill Step 1 → Next → Data preserved
# Fill Step 2 → Add tags → Autocomplete works
# Upload 5 photos → Progress bars display
# Review → Publish → Trip created
```

---

#### **2.5. User Story P2: Upload Photos (Day 9)**

Implement drag-and-drop photo upload (SC-003, SC-007).

**Components**:
1. `PhotoUploader.tsx` - Drag-and-drop with progress

**Key Pattern** (from research.md Decision #2):
```typescript
// src/hooks/useTripPhotos.ts
const uploadPhotosChunked = async (files: File[]) => {
  const CHUNK_SIZE = 3;

  for (let i = 0; i < files.length; i += CHUNK_SIZE) {
    const chunk = files.slice(i, i + CHUNK_SIZE);

    await Promise.allSettled(
      chunk.map((file, index) =>
        uploadTripPhoto(tripId, file, undefined, (progress) => {
          setUploadProgress(prev => ({ ...prev, [i + index]: progress }));
        })
      )
    );
  }
};
```

**Test Checklist**:
- [ ] Drag-and-drop accepts JPG/PNG (SC-007)
- [ ] Rejects invalid files with error message
- [ ] 5 photos upload in <30s (SC-003)
- [ ] Individual progress bars display
- [ ] Failed uploads show retry button

---

#### **2.6. User Story P2: Edit Trip (Day 10)**

Implement trip editing (reuses wizard).

**Components**:
1. `TripEditPage.tsx` - Page wrapper (loads existing trip data)

**Test Checklist**:
- [ ] Form pre-fills with existing data
- [ ] Updates save correctly
- [ ] Optimistic locking prevents concurrent edits

---

#### **2.7. User Story P3: Delete Trip (Day 11)**

Implement trip deletion.

**Test Checklist**:
- [ ] Confirmation dialog displays
- [ ] Trip and photos deleted
- [ ] Redirects to trips list

---

#### **2.8. Polish & Testing (Day 12-14)**

1. **Responsive design**: Test on mobile, tablet, desktop
2. **Loading states**: Add skeletons for trip cards
3. **Error states**: Handle API failures gracefully
4. **Accessibility**: Keyboard navigation, ARIA labels
5. **Performance**: Verify SC-001 to SC-012

**Accessibility Checklist**:
- [ ] All images have alt text
- [ ] Forms have proper labels
- [ ] Keyboard navigation works
- [ ] ARIA labels for dynamic content

---

## Testing Strategy

### Manual Acceptance Testing

**Why Manual Testing?** (from constitution.md):
- UI components are hard to unit test
- Feature 007 proved manual testing effective
- TDD for services/utilities, manual for UI

**Test Scenarios** (from spec.md):

1. **View List**:
   - Navigate to `/trips`
   - Click tag filter → trips update
   - Search for keyword → trips filter
   - Pagination works

2. **View Details**:
   - Click trip card → detail page loads
   - Photos open in lightbox
   - Tags are clickable

3. **Create Trip**:
   - Fill 4-step form
   - Upload photos (drag-and-drop)
   - Publish trip
   - Verify trip appears in list

4. **Edit Trip**:
   - Click Edit on own trip
   - Modify fields
   - Save changes
   - Verify updates

5. **Delete Trip**:
   - Click Delete on own trip
   - Confirm deletion
   - Verify trip removed

---

### Service Layer Tests (Optional)

```typescript
// src/services/__tests__/tripService.test.ts
import { describe, it, expect, vi } from 'vitest';
import { getUserTrips } from '../tripService';

describe('tripService', () => {
  it('fetches user trips with filters', async () => {
    // Mock API response
    global.fetch = vi.fn(() =>
      Promise.resolve({
        json: () => Promise.resolve({
          success: true,
          data: { trips: [...], total: 5 }
        })
      })
    );

    const result = await getUserTrips('testuser', { status: 'published' });
    expect(result.trips).toHaveLength(5);
  });
});
```

**Run Tests**:
```bash
npm test
```

---

## Configuration

### Environment Variables

```bash
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000/api
VITE_MAX_PHOTO_SIZE_MB=10
VITE_MAX_PHOTOS_PER_TRIP=20
```

**Usage**:
```typescript
const MAX_PHOTO_SIZE = parseInt(import.meta.env.VITE_MAX_PHOTO_SIZE_MB) * 1024 * 1024;
```

---

### Routing

Add trip routes to `src/App.tsx`:

```typescript
import TripsListPage from './pages/TripsListPage';
import TripDetailPage from './pages/TripDetailPage';
import TripCreatePage from './pages/TripCreatePage';
import TripEditPage from './pages/TripEditPage';

// In <Routes>
<Route path="/trips" element={<TripsListPage />} />
<Route path="/trips/:tripId" element={<TripDetailPage />} />
<Route path="/trips/new" element={<TripCreatePage />} />
<Route path="/trips/:tripId/edit" element={<TripEditPage />} />
```

---

## CSS Styling

### Existing CSS Variables

Reuse from Feature 007:

```css
/* src/index.css (already defined) */
:root {
  --color-primary: #6b723b;      /* Sage green */
  --color-text: #333333;          /* Dark gray */
  --color-background: #f5f1e8;    /* Cream */
  --color-error: #dc2626;         /* Red */
  --color-success: #6b723b;       /* Sage green */
  --font-sans: 'Poppins', sans-serif;
}
```

### New CSS Patterns

**Difficulty Badges**:
```css
/* src/components/trips/TripCard.css */
.difficulty-badge--easy {
  background: #10b981;
  color: white;
}

.difficulty-badge--moderate {
  background: #f59e0b;
  color: white;
}

.difficulty-badge--difficult {
  background: #ef4444;
  color: white;
}

.difficulty-badge--very-difficult {
  background: #7c2d12;
  color: white;
}
```

**Photo Grid**:
```css
/* src/components/trips/TripGallery.css */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

@media (max-width: 640px) {
  .photo-grid {
    grid-template-columns: 1fr; /* Single column on mobile */
  }
}
```

---

## Common Pitfalls

### 1. Photo URLs Are Absolute

Backend returns **absolute URLs** (configured in `.env`):

```typescript
// ✅ Correct: Use URL directly
<img src={photo.photo_url} alt={photo.caption} />

// ❌ Wrong: Don't prepend base URL
<img src={`${baseURL}${photo.photo_url}`} alt={photo.caption} />
```

### 2. Tags Are Normalized

Tag matching is case-insensitive via `normalized` field:

```typescript
// ✅ Correct: Filter by normalized
const matches = allTags.filter(tag =>
  tag.normalized.includes(query.toLowerCase())
);

// ❌ Wrong: Case-sensitive match
const matches = allTags.filter(tag =>
  tag.name.includes(query)
);
```

### 3. Date Format for HTML Inputs

HTML `<input type="date">` uses `YYYY-MM-DD` format:

```typescript
// ✅ Correct: ISO date string
<input type="date" value="2024-05-15" />

// ❌ Wrong: Formatted date string
<input type="date" value="15 de mayo de 2024" />
```

### 4. Form State vs API Payload

Form uses strings, API expects numbers:

```typescript
// ✅ Correct: Convert on submit
const onSubmit = (data: TripFormData) => {
  const payload: TripCreateInput = {
    ...data,
    distance_km: data.distance_km ? parseFloat(data.distance_km) : null,
  };
  createTrip(payload);
};
```

---

## Performance Optimization

### Lazy Load Components

```typescript
// src/App.tsx
import { lazy, Suspense } from 'react';

const TripMap = lazy(() => import('./components/trips/TripMap'));

// In component
<Suspense fallback={<div>Cargando mapa...</div>}>
  {trip.locations.length > 0 && <TripMap locations={trip.locations} />}
</Suspense>
```

### Image Optimization

Backend already optimizes photos:
- Original → 2000px max width
- Thumbnail → 400x400px

Frontend just displays:
```typescript
// Use thumbnail for lists, full size for lightbox
<img src={photo.thumbnail_url} alt={photo.caption} />
```

---

## Debugging

### Backend Logs

```bash
cd backend
tail -f logs/app.log | grep -E "trips|photos"
```

### Frontend Console

```typescript
// src/services/tripService.ts
console.log('Creating trip:', tripData);
const response = await api.post('/trips', tripData);
console.log('Trip created:', response.data);
```

### Network Tab

Open DevTools → Network:
- Filter by `trips`, `photos`, `tags`
- Check request payload and response
- Verify status codes (201, 200, 400, 403, 404)

---

## Success Criteria Validation

After implementation, verify all 12 success criteria:

| ID | Criterion | How to Verify |
|----|-----------|---------------|
| **SC-001** | Browse & click in <5s | Manual timing |
| **SC-002** | Complete form in <8min | Manual timing (5 photos, 200 words) |
| **SC-003** | Upload 5 photos in <30s | Network throttling (3G) + timing |
| **SC-004** | Page load <2s | Lighthouse performance score |
| **SC-005** | Tag filtering <500ms | DevTools performance profiler |
| **SC-006** | Form preserves data 100% | Navigate between steps, verify data |
| **SC-007** | Drag-and-drop validates files | Upload JPG (✅), TXT (❌ error) |
| **SC-008** | 90% publish first attempt | Test with 10 trips (≥9 should publish) |
| **SC-009** | Lightbox transitions <300ms | DevTools performance profiler |
| **SC-010** | Mobile touch interactions | Test on phone/tablet |
| **SC-011** | Discover via tags in 2-3 clicks | Manual navigation (click tag → filtered) |
| **SC-012** | Photo reorder in <200ms | DevTools performance profiler |

**Lighthouse Test**:
```bash
npm run build
npm run preview
# Open http://localhost:4173/trips
# DevTools → Lighthouse → Run audit
# Target: Performance ≥90
```

---

## Next Steps

**After Phase 1 (Design & Contracts)**: ✅ Complete

**Phase 2 (Implementation)**: Follow the development workflow above

**Phase 3 (Testing & Polish)**: Verify all success criteria

**Phase 4 (Documentation)**: Update CLAUDE.md with trip feature patterns

---

## Resources

- **Data Model**: [data-model.md](data-model.md)
- **API Contracts**: [contracts/trips-frontend-api.md](contracts/trips-frontend-api.md)
- **Research Decisions**: [research.md](research.md)
- **Implementation Plan**: [plan.md](plan.md)
- **Backend Docs**: `backend/docs/api/TRIPS_API.md`

**External Libraries**:
- [react-dropzone docs](https://react-dropzone.js.org/)
- [yet-another-react-lightbox docs](https://yet-another-react-lightbox.com/)
- [react-leaflet docs](https://react-leaflet.js.org/)

---

## Support

**Questions?**
1. Check existing patterns in Feature 007 (Profile Management)
2. Review constitution.md for coding standards
3. Consult backend API docs for endpoint behavior

**Happy coding!** 🚴‍♂️
