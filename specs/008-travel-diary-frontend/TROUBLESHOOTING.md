# Troubleshooting Guide - Travel Diary Frontend

**Feature**: 008 - Travel Diary Frontend
**Version**: 1.0
**Last Updated**: 2026-01-10

## Purpose

This guide documents common issues, their root causes, and solutions when working with the Travel Diary Frontend. Use this as a reference when debugging unexpected behavior.

---

## Table of Contents

1. [Photo Display Issues](#photo-display-issues)
2. [Form State Problems](#form-state-problems)
3. [API Integration Issues](#api-integration-issues)
4. [Tag Filtering Problems](#tag-filtering-problems)
5. [Date Handling Issues](#date-handling-issues)
6. [Performance Issues](#performance-issues)
7. [Authentication Errors](#authentication-errors)
8. [Deployment Issues](#deployment-issues)

---

## Photo Display Issues

### Problem: Photos Not Displaying (Broken Image Icons)

**Symptoms**:
- Broken image icons instead of thumbnails
- 404 errors in browser console for photo URLs
- Photos uploaded successfully but don't show

**Root Cause**: Photo URLs from backend are **absolute URLs**, not relative paths

The backend returns:
```json
{
  "photo_url": "http://localhost:8000/storage/trip_photos/2024/01/abc123.jpg"
}
```

NOT:
```json
{
  "photo_url": "/storage/trip_photos/2024/01/abc123.jpg"
}
```

**Solution**:

Use `getPhotoUrl()` helper from `tripHelpers.ts`:

```typescript
import { getPhotoUrl } from '../utils/tripHelpers';

// ✅ CORRECT
<img src={getPhotoUrl(photo.photo_url)} alt={trip.title} />

// ❌ WRONG
<img src={photo.photo_url} alt={trip.title} />
```

The helper handles:
- Absolute URLs from production backend
- Relative URLs from development
- Missing/null URLs with fallback placeholder

**Files to Check**:
- `frontend/src/pages/TripDetailPage.tsx`
- `frontend/src/components/trips/TripGallery.tsx`
- `frontend/src/components/trips/TripCard.tsx`

---

### Problem: Photo Upload Fails with "Network Error"

**Symptoms**:
- Progress bar starts but then shows error
- Console error: `ERR_CONNECTION_REFUSED` or `CORS error`
- Photos never reach backend

**Root Cause 1**: Backend not running

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# If not running, start it
cd backend
./run-local-dev.sh  # Or poetry run uvicorn...
```

**Root Cause 2**: CORS not configured for localhost:5173

**Solution**:

Check `backend/src/config.py`:
```python
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")
```

Verify frontend dev server uses port 5173 (Vite default).

**Root Cause 3**: File size exceeds backend limit (10MB)

**Solution**:

Frontend validates max 10MB per photo, but check backend also allows:

`backend/src/config.py`:
```python
UPLOAD_MAX_SIZE_MB = int(os.getenv("UPLOAD_MAX_SIZE_MB", "10"))
```

---

### Problem: Photo Reordering Doesn't Persist

**Symptoms**:
- Drag photos to new order
- UI updates immediately
- On page reload, photos return to old order

**Root Cause**: `onReorder` prop not wired to backend API

**Solution**:

Verify PhotoUploader has `onReorder` callback:

```typescript
<PhotoUploader
  photos={photos}
  onChange={setPhotos}
  onUpload={uploadPhoto}
  onDelete={deletePhoto}
  onReorder={reorderPhotos}  // ✅ Must be provided!
  maxPhotos={20}
/>
```

And hook calls backend:

```typescript
// frontend/src/hooks/useTripPhotos.ts
const reorderPhotos = useCallback(
  async (photoIds: string[]): Promise<void> => {
    await reorderTripPhotos(tripId, photoIds);  // ✅ API call
  },
  [tripId]
);
```

**Files to Check**:
- `frontend/src/hooks/useTripPhotos.ts`
- `frontend/src/services/tripPhotoService.ts`

---

## Form State Problems

### Problem: Form Data Lost When Navigating Between Steps

**Symptoms**:
- Fill Step 1, click Next to Step 2
- Click Back to Step 1
- Fields are empty

**Root Cause**: React Hook Form not preserving state across steps

**Solution**:

Ensure `FormProvider` wraps all steps:

```typescript
// TripFormWizard.tsx
<FormProvider {...methods}>
  <form onSubmit={methods.handleSubmit(handleSubmitWrapper)}>
    {currentStep === 0 && <Step1BasicInfo />}
    {currentStep === 1 && <Step2StoryTags />}
    {currentStep === 2 && <Step3Photos />}
    {currentStep === 3 && <Step4Review />}
  </form>
</FormProvider>
```

Each step must use `useFormContext()`, not separate `useForm()`:

```typescript
// ✅ CORRECT
import { useFormContext } from 'react-hook-form';

export const Step1BasicInfo: React.FC = () => {
  const { register, formState } = useFormContext<TripCreateInput>();
  // ...
};

// ❌ WRONG
import { useForm } from 'react-hook-form';

export const Step1BasicInfo: React.FC = () => {
  const { register } = useForm();  // Separate instance!
  // ...
};
```

**Files to Check**:
- `frontend/src/components/trips/TripForm/TripFormWizard.tsx`
- `frontend/src/components/trips/TripForm/Step*.tsx`

---

### Problem: Draft Saves with Validation Errors

**Symptoms**:
- Can save draft even with invalid data
- Missing required fields don't block draft save

**Root Cause**: **This is intentional behavior!**

Drafts should allow partial data. Only publishing enforces full validation.

**Expected Behavior**:
- **Save Draft**: Minimal validation (title + start_date only)
- **Publish**: Full validation (description ≥50 chars, valid dates, etc.)

**Implementation**:

```typescript
// frontend/src/hooks/useTripForm.ts
const handleSubmit = async (data: TripCreateInput, isDraft: boolean) => {
  if (!isDraft) {
    // Validate for publishing
    if (data.description.length < 50) {
      toast.error('La descripción debe tener al menos 50 caracteres para publicar');
      return;
    }
  }

  // Save draft or publish
  const trip = await createTrip(data);
  if (!isDraft) {
    await publishTrip(trip.trip_id);
  }
};
```

**Not a Bug**: Drafts intentionally skip validation

---

### Problem: Form Submission Triggers Twice

**Symptoms**:
- Click "Publish" button
- Two identical trips created in database
- Console shows duplicate API calls

**Root Cause**: Multiple submit handlers or missing `preventDefault()`

**Solution**:

Ensure form uses `onSubmit` handler correctly:

```typescript
// ✅ CORRECT
<form onSubmit={methods.handleSubmit(onSubmit)}>
  <button type="submit">Publish</button>
</form>

// ❌ WRONG
<form onSubmit={methods.handleSubmit(onSubmit)} onClick={onSubmit}>
  <button type="button" onClick={onSubmit}>Publish</button>
</form>
```

Only ONE submit trigger per form!

**Files to Check**:
- `frontend/src/components/trips/TripForm/TripFormWizard.tsx`
- `frontend/src/components/trips/TripForm/Step4Review.tsx`

---

## API Integration Issues

### Problem: 409 Conflict Error When Editing Trip

**Symptoms**:
- Edit trip, click Save
- Error toast: "El viaje fue modificado por otra sesión..."
- Changes don't save

**Root Cause**: **Optimistic locking detected concurrent edit**

This is intentional to prevent data loss!

**Scenario**:
1. User A opens edit page
2. User B opens same edit page
3. User B saves changes
4. User A tries to save (stale data) → 409 Conflict

**Solution**:

User must refresh page to get latest version:

```typescript
// frontend/src/hooks/useTripForm.ts
catch (error: any) {
  if (error.response?.status === 409) {
    toast.error(
      'El viaje fue modificado por otra sesión. Recarga la página para ver los cambios más recientes.',
      { duration: 6000 }
    );
    // User should refresh page manually
  }
}
```

**Not a Bug**: This protects data integrity

**Prevention**:
- Add `updated_at` timestamp to UI to show staleness
- Auto-refresh on focus/visibility change
- WebSocket for real-time updates (future enhancement)

---

### Problem: 403 Forbidden When Accessing Own Trip

**Symptoms**:
- Can create trip as User A
- Log out, log back in as same User A
- Get 403 error viewing own trip

**Root Cause**: Draft trips require ownership check

**Solution**:

Check backend logs for ownership mismatch:

```python
# backend/src/services/trip_service.py
if trip.status == "draft" and trip.user_id != current_user.user_id:
    raise HTTPException(status_code=403, detail="No puedes ver borradores de otros usuarios")
```

Verify:
1. JWT token has correct `user_id` claim
2. Trip `user_id` matches token `user_id`
3. Frontend sends `Authorization: Bearer {token}` header

**Debug Steps**:
```bash
# Check JWT payload
jwt.io  # Paste access token, verify user_id

# Check trip ownership in database
sqlite3 backend/contravento_dev.db
SELECT user_id, owner_id FROM trips WHERE trip_id = 'UUID';
```

**Files to Check**:
- `frontend/src/services/api.ts` (axios interceptor adds auth header)
- `backend/src/services/trip_service.py`

---

## Tag Filtering Problems

### Problem: Tag Filter Case-Sensitive

**Symptoms**:
- Searching for "Bikepacking" shows no results
- But "bikepacking" (lowercase) works
- Tags display with capital letters

**Root Cause**: Tag normalization not applied in frontend filter

**Solution**:

Backend normalizes tags to lowercase for matching:

```python
# backend/src/models/tag.py
class Tag(Base):
    name = Column(String(50), nullable=False)  # Display name
    normalized = Column(String(50), nullable=False, unique=True, index=True)  # Lowercase for matching
```

Frontend must query with lowercase:

```typescript
// ✅ CORRECT
const params = {
  tag: selectedTag.toLowerCase()  // Always lowercase!
};

// ❌ WRONG
const params = {
  tag: selectedTag  // Might be "Bikepacking" (capital)
};
```

**Files to Check**:
- `frontend/src/hooks/useTripFilters.ts`
- `frontend/src/services/tripService.ts`

---

### Problem: Duplicate Tags Appear in Autocomplete

**Symptoms**:
- Type "bike" in tag input
- Suggestions show: "bikepacking", "bikepacking", "Bike touring"
- Selecting adds duplicate tags

**Root Cause**: Tag normalization creates duplicates if not handled

**Solution**:

Use `tag.normalized` for matching, `tag.name` for display:

```typescript
// Get unique tags from backend
const tags = await getAllTags();  // Returns [{name: "Bikepacking", normalized: "bikepacking"}, ...]

// Filter by normalized (lowercase)
const filtered = tags.filter(tag =>
  tag.normalized.includes(searchTerm.toLowerCase())
);

// Display using tag.name (preserves capitalization)
filtered.map(tag => tag.name)
```

**Files to Check**:
- `frontend/src/components/trips/TripForm/Step2StoryTags.tsx`
- `frontend/src/services/tripService.ts`

---

## Date Handling Issues

### Problem: Dates Display One Day Off

**Symptoms**:
- Set trip date to "2024-06-15"
- Page shows "June 14, 2024"
- Off by one day

**Root Cause**: Timezone conversion issues with date-only strings

**Solution**:

Backend stores dates as `YYYY-MM-DD` strings (no timezone).

Frontend must parse as **local date**, not UTC:

```typescript
// ✅ CORRECT (local date)
const date = new Date(trip.start_date + 'T00:00:00');  // Force local time

// ❌ WRONG (UTC date, causes off-by-one)
const date = new Date(trip.start_date);  // Interprets as UTC
```

Use helper from `tripHelpers.ts`:

```typescript
import { formatDate, formatDateRange } from '../utils/tripHelpers';

// ✅ CORRECT
<span>{formatDate(trip.start_date)}</span>
<span>{formatDateRange(trip.start_date, trip.end_date)}</span>
```

**Files to Check**:
- `frontend/src/utils/tripHelpers.ts`
- `frontend/src/components/trips/TripCard.tsx`
- `frontend/src/pages/TripDetailPage.tsx`

---

### Problem: Date Picker Validation Fails

**Symptoms**:
- Set end_date before start_date
- Form allows submission
- Backend returns 400 error

**Root Cause**: Frontend validation not checking date order

**Solution**:

Add custom validation in Step1BasicInfo:

```typescript
// frontend/src/components/trips/TripForm/Step1BasicInfo.tsx
<input
  type="date"
  {...register('end_date', {
    validate: (value) => {
      if (!value) return true;  // Optional field
      const startDate = watch('start_date');
      if (startDate && new Date(value) < new Date(startDate)) {
        return 'La fecha de fin debe ser posterior a la fecha de inicio';
      }
      return true;
    }
  })}
/>
```

**Files to Check**:
- `frontend/src/components/trips/TripForm/Step1BasicInfo.tsx`
- `frontend/src/utils/tripValidators.ts`

---

## Performance Issues

### Problem: Trip List Loads Slowly (>5 seconds)

**Symptoms**:
- Navigating to `/trips` takes 5+ seconds
- Backend logs show slow query
- Many trips in database (500+)

**Root Cause**: Missing pagination or inefficient query

**Solution**:

Verify pagination is enabled:

```typescript
// frontend/src/hooks/useTripList.ts
const fetchTrips = async () => {
  const response = await getUserTrips(username, {
    page: currentPage,  // ✅ Pagination enabled
    limit: 12,
    ...filters
  });
};
```

Backend must use pagination:

```python
# backend/src/services/trip_service.py
query = query.limit(limit).offset((page - 1) * limit)
```

**Performance Target**: <2s for list load (SC-001)

**Files to Check**:
- `frontend/src/hooks/useTripList.ts`
- `backend/src/services/trip_service.py`

---

### Problem: Photo Gallery Lags on Mobile

**Symptoms**:
- Opening lightbox on mobile (iPhone/Android) lags 2-3 seconds
- Scrolling through photos stutters
- High memory usage

**Root Cause**: Large images not optimized for mobile

**Solution**:

Backend should generate thumbnails (not implemented yet):

```python
# Future: backend/src/services/trip_photo_service.py
def create_thumbnail(image_path, size=(400, 400)):
    img = Image.open(image_path)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    # Save thumbnail...
```

Frontend can use lazy loading:

```typescript
// frontend/src/components/trips/TripGallery.tsx
<img
  src={photo.photo_url}
  loading="lazy"  // Browser-native lazy load
  alt={tripTitle}
/>
```

**Future Enhancement**: Implement thumbnail generation in backend

**Files to Check**:
- `frontend/src/components/trips/TripGallery.tsx`
- `backend/src/services/trip_photo_service.py`

---

## Authentication Errors

### Problem: "Tu sesión ha expirado" on Every Page Reload

**Symptoms**:
- Log in successfully
- Refresh page
- Immediately logged out with "Tu sesión ha expirado" toast

**Root Cause**: Access token not persisted to localStorage

**Solution**:

Verify `AuthContext` saves token:

```typescript
// frontend/src/contexts/AuthContext.tsx
const login = async (credentials) => {
  const data = await authService.login(credentials);

  // ✅ MUST save to localStorage
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);

  setUser(data.user);
};
```

And loads on mount:

```typescript
useEffect(() => {
  const token = localStorage.getItem('access_token');
  if (token) {
    // Validate token and restore user
    setUser(decodedUser);
  }
}, []);
```

**Files to Check**:
- `frontend/src/contexts/AuthContext.tsx`
- `frontend/src/services/authService.ts`

---

### Problem: 401 Errors After 15 Minutes

**Symptoms**:
- Working fine for 15 minutes
- Suddenly all API calls return 401
- Must log in again

**Root Cause**: **This is expected behavior!**

Access tokens expire after 15 minutes (backend config).

**Solution**:

Implement token refresh using refresh token:

```typescript
// frontend/src/services/api.ts
axios.interceptors.response.use(
  response => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        const newTokens = await authService.refresh(refreshToken);
        localStorage.setItem('access_token', newTokens.access_token);
        // Retry original request
        return axios.request(error.config);
      }
    }
    return Promise.reject(error);
  }
);
```

**Not a Bug**: 15-minute expiry is intentional security measure

**Files to Check**:
- `frontend/src/services/api.ts`
- `backend/src/config.py` (ACCESS_TOKEN_EXPIRE_MINUTES)

---

## Deployment Issues

### Problem: Photos Work Locally But Not in Production

**Symptoms**:
- Photos display fine on localhost
- After deploying, photos return 404
- Backend logs show file not found

**Root Cause**: Photo storage path not configured for production

**Solution**:

Check backend storage configuration:

```python
# backend/src/config.py
STORAGE_PATH = os.getenv(
    "STORAGE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "storage")  # Default: relative path
)
```

For production, set absolute path:

```bash
# .env.production
STORAGE_PATH=/var/www/contravento/storage
```

Ensure directory is writable:

```bash
chmod -R 755 /var/www/contravento/storage
chown -R www-data:www-data /var/www/contravento/storage
```

**Files to Check**:
- `backend/src/config.py`
- `.env.production`
- Production server directory permissions

---

### Problem: Frontend Build Fails with "Module not found"

**Symptoms**:
- `npm run build` fails
- Error: "Module not found: Can't resolve '@/components/...'"
- Works fine in dev mode

**Root Cause**: Path aliases not configured for production build

**Solution**:

Verify `vite.config.ts` has path resolution:

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')  // ✅ Enable @ alias
    }
  }
});
```

And `tsconfig.json` matches:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**Files to Check**:
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`

---

## Getting Help

If you encounter an issue not covered in this guide:

1. **Check console logs**: Browser DevTools Console tab for frontend errors
2. **Check backend logs**: Terminal running backend server for API errors
3. **Search codebase**: Use `grep` or IDE search for error message
4. **Check network tab**: DevTools Network tab to see actual API requests/responses
5. **Review spec.md**: Verify expected behavior matches implementation
6. **Create issue**: File bug report with reproduction steps

---

## Quick Reference: Common Error Messages

| Error Message | Likely Cause | Solution |
|--------------|-------------|----------|
| "No tienes permiso para editar este viaje" | Not the trip owner | Only owner can edit/delete |
| "La descripción debe tener al menos 50 caracteres..." | Publishing with short description | Add more content to description |
| "El viaje fue modificado por otra sesión..." | Concurrent edit detected (409) | Refresh page to get latest |
| "Token de autenticación inválido" | Expired or malformed JWT | Re-login to get new token |
| "Error al cargar el viaje" | 404 or network error | Check trip exists, backend running |
| "[filename] no es una imagen válida" | Wrong file type uploaded | Only JPG/PNG/WEBP allowed |
| "[filename] excede el tamaño máximo de 10MB" | File too large | Compress image before upload |

---

## Related Documentation

- [MANUAL_TESTING.md](MANUAL_TESTING.md) - Manual testing procedures
- [spec.md](spec.md) - Feature requirements and success criteria
- [plan.md](plan.md) - Technical architecture and design decisions
- [tasks.md](tasks.md) - Implementation task breakdown

**Last Updated**: 2026-01-10
