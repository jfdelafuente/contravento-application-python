# Data Model: Travel Diary Frontend

**Feature**: 008-travel-diary-frontend
**Date**: 2026-01-10
**Status**: Phase 1 - Design & Contracts

## Overview

This document defines TypeScript interfaces for the Travel Diary frontend feature. These interfaces match the backend API response schemas from Feature 002 (Travel Diary Backend) and provide type safety for all trip-related data.

**Backend Reference**: [specs/002-travel-diary/data-model.md](../002-travel-diary/data-model.md)

---

## Entity Overview

```
┌──────────────────────────────────────────────────────┐
│ Trip (TripResponse)                                   │
│ ───────────────────────────────────────────────────── │
│ • trip_id: string                                     │
│ • user_id: string                                     │
│ • title: string                                       │
│ • description: string (HTML)                          │
│ • status: 'draft' | 'published'                       │
│ • start_date: string (ISO 8601)                       │
│ • end_date: string | null                             │
│ • distance_km: number | null                          │
│ • difficulty: Difficulty | null                       │
│ • created_at: string (ISO 8601)                       │
│ • updated_at: string (ISO 8601)                       │
│ • published_at: string | null                         │
└──┬───────────────────┬──────────────────┬─────────────┘
   │                   │                  │
   │ photos[]         │ locations[]     │ tags[]
   │                   │                  │
   ▼                   ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│ TripPhoto   │  │ Trip        │  │ Tag          │
│             │  │ Location    │  │              │
│ • photo_id  │  │ • location_ │  │ • tag_id     │
│ • photo_url │  │   id        │  │ • name       │
│ • thumb_url │  │ • name      │  │ • normalized │
│ • caption   │  │ • latitude  │  │ • usage_     │
│ • order     │  │ • longitude │  │   count      │
│ • width     │  │ • sequence  │  └──────────────┘
│ • height    │  └─────────────┘
└─────────────┘
```

---

## Core Entities

### Trip (Full Response)

**Interface**: `Trip`

Complete trip data returned by `GET /api/trips/{trip_id}` and `POST/PUT /api/trips`.

```typescript
/**
 * Complete trip data from backend API
 *
 * Used in:
 * - TripDetailPage (view full trip)
 * - TripEditPage (edit existing trip)
 * - After creating/updating a trip
 */
interface Trip {
  /** Unique trip identifier (UUID) */
  trip_id: string;

  /** Trip owner's user ID (UUID) */
  user_id: string;

  /** Trip title (1-200 characters) */
  title: string;

  /** Trip description (HTML, sanitized by backend, max 50000 chars) */
  description: string;

  /** Publication status */
  status: 'draft' | 'published';

  /** Trip start date (ISO 8601: YYYY-MM-DD) */
  start_date: string;

  /** Trip end date (ISO 8601: YYYY-MM-DD, null if single-day trip) */
  end_date: string | null;

  /** Distance in kilometers (0.1-10000, null if not provided) */
  distance_km: number | null;

  /** Difficulty level (null if not provided) */
  difficulty: 'easy' | 'moderate' | 'difficult' | 'very_difficult' | null;

  /** Trip creation timestamp (ISO 8601: YYYY-MM-DDTHH:mm:ssZ) */
  created_at: string;

  /** Last update timestamp (ISO 8601: YYYY-MM-DDTHH:mm:ssZ) */
  updated_at: string;

  /** Publication timestamp (ISO 8601, null if draft) */
  published_at: string | null;

  /** Trip photos (ordered by display_order) */
  photos: TripPhoto[];

  /** Trip locations/waypoints (ordered by sequence) */
  locations: TripLocation[];

  /** Trip tags for categorization */
  tags: Tag[];
}
```

**Example**:
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Vía Verde del Aceite",
  "description": "<p>Ruta espectacular entre olivos centenarios desde Jaén hasta Baeza...</p>",
  "status": "published",
  "start_date": "2024-05-15",
  "end_date": "2024-05-17",
  "distance_km": 127.3,
  "difficulty": "moderate",
  "created_at": "2024-12-20T10:30:00Z",
  "updated_at": "2024-12-22T15:45:00Z",
  "published_at": "2024-12-22T15:45:00Z",
  "photos": [...],
  "locations": [...],
  "tags": [...]
}
```

---

### TripListItem (Summary Response)

**Interface**: `TripListItem`

Lightweight trip summary for list views with pagination. Returned by `GET /api/users/{username}/trips`.

```typescript
/**
 * Trip summary for list/grid views
 *
 * Used in:
 * - TripsListPage (browse all trips)
 * - ProfilePage (user's recent trips)
 * - Search results
 */
interface TripListItem {
  /** Unique trip identifier (UUID) */
  trip_id: string;

  /** Trip owner's user ID (UUID) */
  user_id: string;

  /** Trip title */
  title: string;

  /** Trip start date (ISO 8601: YYYY-MM-DD) */
  start_date: string;

  /** Distance in kilometers (null if not provided) */
  distance_km: number | null;

  /** Publication status */
  status: 'draft' | 'published';

  /** Number of photos attached to trip */
  photo_count: number;

  /** Tag names only (for filtering, lighter payload) */
  tag_names: string[];

  /** First photo thumbnail URL (null if no photos) */
  thumbnail_url: string | null;

  /** Trip creation timestamp (ISO 8601: YYYY-MM-DDTHH:mm:ssZ) */
  created_at: string;
}
```

**Example**:
```json
{
  "trip_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Vía Verde del Aceite",
  "start_date": "2024-05-15",
  "distance_km": 127.3,
  "status": "published",
  "photo_count": 12,
  "tag_names": ["vías verdes", "andalucía", "olivos"],
  "thumbnail_url": "/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
  "created_at": "2024-12-20T10:30:00Z"
}
```

**Why Two Interfaces?**
- **TripListItem**: Lighter payload for browsing (12 trips per page = 12 KB vs 120 KB)
- **Trip**: Full data for detail view and editing

---

### TripPhoto

**Interface**: `TripPhoto`

Photo metadata for trip gallery display.

```typescript
/**
 * Trip photo data
 *
 * Used in:
 * - TripGallery (photo grid with lightbox)
 * - PhotoUploader (uploaded photo preview)
 */
interface TripPhoto {
  /** Unique photo identifier (UUID) */
  photo_id: string;

  /** URL to optimized photo (max 2000px width) */
  photo_url: string;

  /** URL to thumbnail (400x400px) */
  thumbnail_url: string;

  /** Optional photo caption (max 500 chars) */
  caption: string | null;

  /** Display order in gallery (0-based, reorderable) */
  display_order: number;

  /** Optimized photo width in pixels */
  width: number;

  /** Optimized photo height in pixels */
  height: number;
}
```

**Example**:
```json
{
  "photo_id": "770e8400-e29b-41d4-a716-446655440002",
  "photo_url": "http://localhost:8000/storage/trip_photos/2024/12/550e.../abc123_optimized.jpg",
  "thumbnail_url": "http://localhost:8000/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
  "caption": "Vista desde el viaducto sobre el valle del Guadalquivir",
  "display_order": 0,
  "width": 2000,
  "height": 1500
}
```

**Notes**:
- Backend returns **absolute URLs** with domain (configured in `.env`)
- `display_order` is reorderable via drag-and-drop (PUT /api/trips/{id}/photos/reorder)
- Max 20 photos per trip (enforced by backend)

---

### Tag

**Interface**: `Tag`

Tag data for categorization and filtering.

```typescript
/**
 * Trip tag for categorization
 *
 * Used in:
 * - TagInput (autocomplete suggestions)
 * - TripFilters (clickable tag chips)
 * - Trip detail view (tag chips)
 */
interface Tag {
  /** Unique tag identifier (UUID) */
  tag_id: string;

  /** Display name (preserves original casing, e.g., "Vías Verdes") */
  name: string;

  /** Normalized name for matching (lowercase, e.g., "vias verdes") */
  normalized: string;

  /** Number of trips using this tag (for popularity sorting) */
  usage_count: number;
}
```

**Example**:
```json
{
  "tag_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Vías Verdes",
  "normalized": "vias verdes",
  "usage_count": 125
}
```

**Tag Matching**:
- User types: "vias" → matches "Vías Verdes" (via normalized)
- User types: "VÍAS" → matches "Vías Verdes" (case-insensitive)
- Display always uses `name` (preserves casing)

---

### TripLocation

**Interface**: `TripLocation`

Location/waypoint data for trip route display.

```typescript
/**
 * Trip location/waypoint
 *
 * Used in:
 * - TripMap (display markers on map)
 * - Location list in trip details
 *
 * Note: Optional feature for MVP - most trips won't have locations initially
 */
interface TripLocation {
  /** Unique location identifier (UUID) */
  location_id: string;

  /** Location name (e.g., "Baeza", "Camino de Santiago") */
  name: string;

  /** Latitude coordinate (decimal degrees, null if not geocoded) */
  latitude: number | null;

  /** Longitude coordinate (decimal degrees, null if not geocoded) */
  longitude: number | null;

  /** Order in route (0 = start, 1 = next waypoint, etc.) */
  sequence: number;
}
```

**Example**:
```json
{
  "location_id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Baeza",
  "latitude": 37.9963,
  "longitude": -3.4669,
  "sequence": 0
}
```

**Notes**:
- `latitude`/`longitude` are optional (backend geocodes if not provided)
- If coordinates exist, display marker on map (react-leaflet)
- If no coordinates, display name only (text list)

---

## Request/Input Schemas

### TripCreateInput

**Interface**: `TripCreateInput`

Data sent when creating a new trip via `POST /api/trips`.

```typescript
/**
 * Input data for creating a new trip
 *
 * Used in:
 * - TripFormWizard (multi-step form submission)
 * - Step 4 (Review & Publish)
 */
interface TripCreateInput {
  /** Trip title (1-200 characters, required) */
  title: string;

  /** Trip description (1-50000 characters, required, HTML allowed) */
  description: string;

  /** Trip start date (ISO 8601: YYYY-MM-DD, cannot be future) */
  start_date: string;

  /** Trip end date (ISO 8601: YYYY-MM-DD, must be >= start_date) */
  end_date: string | null;

  /** Distance in kilometers (0.1-10000, optional) */
  distance_km: number | null;

  /** Difficulty level (optional) */
  difficulty: 'easy' | 'moderate' | 'difficult' | 'very_difficult' | null;

  /** Locations visited during trip (max 50) */
  locations: LocationInput[];

  /** Tags for categorization (max 10 tags, max 50 chars each) */
  tags: string[];
}
```

**Validation Rules** (enforced by Zod schema):
- `title`: Required, 1-200 characters
- `description`: Required, 1-50000 characters (drafts: no minimum, published: 50 minimum)
- `start_date`: Required, cannot be in future
- `end_date`: Optional, must be >= start_date
- `distance_km`: Optional, 0.1-10000
- `tags`: Max 10, each max 50 characters, no empty strings

**Example**:
```json
{
  "title": "Vía Verde del Aceite",
  "description": "<p>Un recorrido espectacular entre olivos centenarios...</p>",
  "start_date": "2024-05-15",
  "end_date": "2024-05-17",
  "distance_km": 127.3,
  "difficulty": "moderate",
  "locations": [
    {"name": "Jaén", "country": "España"},
    {"name": "Baeza", "country": "España"}
  ],
  "tags": ["vías verdes", "andalucía", "olivos"]
}
```

---

### TripUpdateInput

**Interface**: `TripUpdateInput`

Data sent when updating an existing trip via `PUT /api/trips/{trip_id}`.

```typescript
/**
 * Input data for updating an existing trip
 *
 * All fields are optional - only provided fields will be updated.
 *
 * Used in:
 * - TripFormWizard (edit mode)
 * - Step 4 (Review & Publish)
 */
interface TripUpdateInput {
  /** Trip title (1-200 characters) */
  title?: string;

  /** Trip description (1-50000 characters, HTML allowed) */
  description?: string;

  /** Trip start date (ISO 8601: YYYY-MM-DD) */
  start_date?: string;

  /** Trip end date (ISO 8601: YYYY-MM-DD, must be >= start_date) */
  end_date?: string | null;

  /** Distance in kilometers (0.1-10000) */
  distance_km?: number | null;

  /** Difficulty level */
  difficulty?: 'easy' | 'moderate' | 'difficult' | 'very_difficult' | null;

  /** Locations (replaces existing) */
  locations?: LocationInput[];

  /** Tags (replaces existing, max 10) */
  tags?: string[];

  /** Timestamp when client loaded the trip (optimistic locking) */
  client_updated_at?: string;
}
```

**Notes**:
- All fields optional (PATCH-style semantics)
- `locations` and `tags` replace existing (not incremental)
- `client_updated_at` for optimistic locking (prevents concurrent edits)

---

### LocationInput

**Interface**: `LocationInput`

Location data for trip creation/update.

```typescript
/**
 * Location input for trip forms
 *
 * Used in:
 * - Step 1 (Basic Info) - location input field
 * - Trip creation/update requests
 */
interface LocationInput {
  /** Location name (1-200 characters, required) */
  name: string;

  /** Country name (max 100 characters, optional) */
  country?: string;
}
```

**Example**:
```json
{
  "name": "Baeza",
  "country": "España"
}
```

**Notes**:
- Backend geocodes name → lat/lng (optional feature)
- Frontend only collects name + country (simple text inputs)

---

## Paginated Response

### TripListResponse

**Interface**: `TripListResponse`

Paginated list of trips returned by `GET /api/users/{username}/trips`.

```typescript
/**
 * Paginated trip list response
 *
 * Used in:
 * - TripsListPage (browse trips with filters)
 * - useTripList hook (pagination logic)
 */
interface TripListResponse {
  /** List of trip summaries for current page */
  trips: TripListItem[];

  /** Total number of trips matching filter (for pagination UI) */
  total: number;

  /** Page size used for this request */
  limit: number;

  /** Pagination offset used for this request */
  offset: number;
}
```

**Example**:
```json
{
  "trips": [
    {
      "trip_id": "550e8400-...",
      "title": "Vía Verde del Aceite",
      ...
    }
  ],
  "total": 15,
  "limit": 12,
  "offset": 0
}
```

**Pagination Calculation**:
- Page 1: `offset=0, limit=12` → trips 1-12
- Page 2: `offset=12, limit=12` → trips 13-24
- Total pages: `Math.ceil(total / limit)` = `Math.ceil(15 / 12)` = 2

---

## API Error Response

### ApiError

**Interface**: `ApiError`

Standard error response from backend (used across all features).

```typescript
/**
 * Standard API error response
 *
 * Used in:
 * - All API service error handlers
 * - Error toast notifications
 */
interface ApiError {
  /** Always false for errors */
  success: false;

  /** Null data payload */
  data: null;

  /** Error details */
  error: {
    /** Error code (e.g., "VALIDATION_ERROR", "NOT_FOUND") */
    code: string;

    /** User-friendly error message in Spanish */
    message: string;

    /** Optional field name for validation errors */
    field?: string;
  };
}
```

**Example**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La descripción debe tener al menos 50 caracteres para publicar",
    "field": "description"
  }
}
```

---

## Form State (Client-Only)

### TripFormData

**Interface**: `TripFormData`

React Hook Form state for multi-step trip wizard (client-only, not sent to API).

```typescript
/**
 * Form state for TripFormWizard (all 4 steps combined)
 *
 * Used in:
 * - TripFormWizard (parent component state)
 * - All step components (Step1-4)
 * - Zod validation schema
 */
interface TripFormData {
  // Step 1: Basic Info
  title: string;
  start_date: string; // HTML date input format: YYYY-MM-DD
  end_date: string;
  distance_km: string; // String in form, parsed to number on submit
  difficulty: 'easy' | 'moderate' | 'difficult' | 'very_difficult' | '';

  // Step 2: Story & Tags
  description: string;
  tags: string[]; // Array of tag names

  // Step 3: Photos
  // Photos handled separately via PhotoUploader (file uploads)

  // Step 4: Review
  // Read-only summary of all fields above
}
```

**Notes**:
- Form uses string types (HTML inputs) → convert to numbers on submit
- `difficulty` uses empty string for "not selected" (easier for select element)
- Photos not stored in form state (uploaded separately via multipart/form-data)

---

## Photo Upload State (Client-Only)

### PhotoUploadState

**Interface**: `PhotoUploadState`

State for managing photo uploads in Step 3 (client-only).

```typescript
/**
 * Photo upload state for PhotoUploader component
 *
 * Used in:
 * - PhotoUploader (Step 3)
 * - useTripPhotos hook
 */
interface PhotoUploadState {
  /** Selected files for upload */
  files: File[];

  /** Upload progress per file (0-100) */
  progress: Record<string, number>; // key: file.name, value: percentage

  /** Upload status per file */
  status: Record<string, 'pending' | 'uploading' | 'success' | 'error'>;

  /** Uploaded photo responses from backend */
  uploadedPhotos: TripPhoto[];

  /** Error messages per file */
  errors: Record<string, string>;
}
```

**Example**:
```typescript
{
  files: [File, File, File],
  progress: {
    "photo1.jpg": 100,
    "photo2.jpg": 65,
    "photo3.jpg": 0
  },
  status: {
    "photo1.jpg": "success",
    "photo2.jpg": "uploading",
    "photo3.jpg": "pending"
  },
  uploadedPhotos: [
    { photo_id: "...", photo_url: "...", ... }
  ],
  errors: {
    "photo4.jpg": "El archivo excede 10MB. Intenta comprimir la imagen."
  }
}
```

---

## Type Exports

```typescript
// src/types/trip.ts

// Core entities
export type { Trip, TripListItem, TripPhoto, Tag, TripLocation };

// Request/input schemas
export type { TripCreateInput, TripUpdateInput, LocationInput };

// Response schemas
export type { TripListResponse, ApiError };

// Form state (client-only)
export type { TripFormData, PhotoUploadState };

// Enums
export type TripStatus = 'draft' | 'published';
export type TripDifficulty = 'easy' | 'moderate' | 'difficult' | 'very_difficult';
```

---

## Validation Schemas (Zod)

### tripFormSchema

**File**: `src/utils/tripValidators.ts`

Zod schema for client-side validation before API submission.

```typescript
import { z } from 'zod';

/**
 * Zod schema for trip form validation
 *
 * Used in:
 * - TripFormWizard (React Hook Form resolver)
 * - Step-by-step validation
 */
export const tripFormSchema = z.object({
  // Step 1: Basic Info
  title: z.string()
    .min(1, 'El título es obligatorio')
    .max(200, 'El título no puede superar 200 caracteres'),

  start_date: z.string()
    .refine(
      (date) => new Date(date) <= new Date(),
      'La fecha de inicio no puede ser futura'
    ),

  end_date: z.string().optional().nullable(),

  distance_km: z.string()
    .optional()
    .transform((val) => val ? parseFloat(val) : null)
    .refine(
      (val) => val === null || (val >= 0.1 && val <= 10000),
      'La distancia debe estar entre 0.1 y 10000 km'
    ),

  difficulty: z.enum(['easy', 'moderate', 'difficult', 'very_difficult', '']),

  // Step 2: Story & Tags
  description: z.string()
    .min(1, 'La descripción es obligatoria'),
    // Note: 50 char minimum enforced only on publish, not on save draft

  tags: z.array(z.string().max(50, 'Etiqueta demasiado larga (máx 50 caracteres)'))
    .max(10, 'Máximo 10 etiquetas permitidas'),

}).refine(
  (data) => {
    // Validate end_date >= start_date
    if (data.end_date && data.start_date) {
      return new Date(data.end_date) >= new Date(data.start_date);
    }
    return true;
  },
  {
    message: 'La fecha de fin debe ser posterior o igual a la fecha de inicio',
    path: ['end_date'],
  }
);

/**
 * Publish-specific validation (enforces 50 char description minimum)
 */
export const tripPublishSchema = tripFormSchema.extend({
  description: z.string()
    .min(50, 'La descripción debe tener al menos 50 caracteres para publicar')
    .max(50000, 'La descripción no puede superar 50000 caracteres'),
});
```

---

## Difficulty Labels (Spanish)

**File**: `src/utils/tripHelpers.ts`

Helper function to translate difficulty enum to Spanish display text.

```typescript
/**
 * Translate difficulty enum to Spanish label
 */
export const getDifficultyLabel = (difficulty: TripDifficulty | null): string => {
  if (!difficulty) return 'No especificada';

  const labels: Record<TripDifficulty, string> = {
    easy: 'Fácil',
    moderate: 'Moderada',
    difficult: 'Difícil',
    very_difficult: 'Muy Difícil',
  };

  return labels[difficulty];
};

/**
 * Get difficulty badge CSS class for styling
 */
export const getDifficultyClass = (difficulty: TripDifficulty | null): string => {
  if (!difficulty) return 'difficulty-badge--none';

  const classes: Record<TripDifficulty, string> = {
    easy: 'difficulty-badge--easy',
    moderate: 'difficulty-badge--moderate',
    difficult: 'difficulty-badge--difficult',
    very_difficult: 'difficulty-badge--very-difficult',
  };

  return classes[difficulty];
};
```

---

## Backend API Compatibility

### Field Name Mappings

Some backend fields have property aliases for schema compatibility:

| Backend Model Field | API Response Field | Frontend Interface Field |
|--------------------|--------------------|--------------------------|
| `thumb_url` | `thumbnail_url` | `thumbnail_url` |
| `order` | `display_order` | `display_order` |
| `trip_id` | `trip_id` | `trip_id` |
| `tag_id` | `tag_id` | `tag_id` |
| `photo_id` | `photo_id` | `photo_id` |
| `location_id` | `location_id` | `location_id` |

**Note**: Backend model has property mappings (`@property`) to ensure API responses match frontend expectations.

---

## Date/Time Handling

### ISO 8601 Format

All dates and timestamps use ISO 8601 format:

- **Dates**: `YYYY-MM-DD` (e.g., `"2024-05-15"`)
- **Timestamps**: `YYYY-MM-DDTHH:mm:ssZ` (e.g., `"2024-12-20T10:30:00Z"`)

### Frontend Utilities

```typescript
/**
 * Format ISO date string to Spanish locale
 * @param isoDate - ISO 8601 date string (YYYY-MM-DD)
 * @returns Formatted date (e.g., "15 de mayo de 2024")
 */
export const formatDate = (isoDate: string): string => {
  return new Date(isoDate).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Format ISO timestamp to Spanish locale with time
 * @param isoTimestamp - ISO 8601 timestamp (YYYY-MM-DDTHH:mm:ssZ)
 * @returns Formatted datetime (e.g., "20 de diciembre de 2024, 10:30")
 */
export const formatDateTime = (isoTimestamp: string): string => {
  return new Date(isoTimestamp).toLocaleString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Convert HTML date input value (YYYY-MM-DD) to ISO date string
 * @param dateInput - Value from <input type="date">
 * @returns ISO 8601 date string
 */
export const toISODate = (dateInput: string): string => {
  return dateInput; // Already in YYYY-MM-DD format
};
```

---

## Next Steps

- ✅ Data model defined (this document)
- ⏳ API contracts documentation ([contracts/trips-frontend-api.md](contracts/trips-frontend-api.md))
- ⏳ Developer quickstart guide ([quickstart.md](quickstart.md))

**After Phase 1**: Implement TypeScript interfaces in `frontend/src/types/trip.ts` and validation schemas in `frontend/src/utils/tripValidators.ts`.
