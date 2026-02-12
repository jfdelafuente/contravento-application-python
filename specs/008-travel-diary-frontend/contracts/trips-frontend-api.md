# API Contracts: Travel Diary Frontend

**Feature**: 008-travel-diary-frontend
**Date**: 2026-01-10
**Status**: Phase 1 - Design & Contracts

## Overview

This document defines the HTTP API endpoints used by the Travel Diary frontend. All endpoints are provided by the backend (Feature 002: Travel Diary Backend).

**Base URL**: `http://localhost:8000/api` (development)

**Authentication**: All endpoints except `GET /tags` require authentication via JWT token in `Authorization` header.

**Response Format**: All endpoints return standardized JSON:

```json
{
  "success": true | false,
  "data": { ... } | null,
  "error": { "code": "...", "message": "..." } | null
}
```

---

## Authentication Header

```http
Authorization: Bearer {access_token}
```

**How to get token**: See Feature 005 (Frontend User Authentication)

```typescript
// src/services/api.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // Include HttpOnly cookies
});

// Token automatically sent via HttpOnly cookie (set by backend on login)
```

---

## Endpoints Summary

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `GET` | `/users/{username}/trips` | List user's trips with filters | No (public trips only) |
| `GET` | `/trips/{trip_id}` | Get trip details | No (public trips only) |
| `POST` | `/trips` | Create new trip | Yes |
| `PUT` | `/trips/{trip_id}` | Update existing trip | Yes (owner only) |
| `DELETE` | `/trips/{trip_id}` | Delete trip | Yes (owner only) |
| `POST` | `/trips/{trip_id}/publish` | Publish draft trip | Yes (owner only) |
| `POST` | `/trips/{trip_id}/photos` | Upload photo to trip | Yes (owner only) |
| `DELETE` | `/trips/{trip_id}/photos/{photo_id}` | Delete photo from trip | Yes (owner only) |
| `PUT` | `/trips/{trip_id}/photos/reorder` | Reorder photos in gallery | Yes (owner only) |
| `GET` | `/tags` | Get all tags | No |

---

## 1. List User Trips

### `GET /api/users/{username}/trips`

Get a user's trips with optional filtering and pagination.

**Path Parameters**:
- `username` (string, required): Username of the profile owner

**Query Parameters**:
- `tag` (string, optional): Filter by tag name (case-insensitive)
- `status` (enum, optional): Filter by status (`draft` or `published`)
  - Default: Show only `published` trips for others
  - For own profile: Show both unless filtered
- `limit` (integer, optional): Max trips to return (1-100, default: 50)
- `offset` (integer, optional): Pagination offset (default: 0)

**Example Request**:

```http
GET /api/users/maria_garcia/trips?tag=bikepacking&status=published&limit=12&offset=0
Authorization: Bearer eyJhbGciOiJI...
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Vía Verde del Aceite",
        "start_date": "2024-05-15",
        "distance_km": 127.3,
        "status": "published",
        "photo_count": 12,
        "tag_names": ["vías verdes", "andalucía", "olivos"],
        "thumbnail_url": "http://localhost:8000/storage/trip_photos/2024/12/550e.../thumb.jpg",
        "created_at": "2024-12-20T10:30:00Z"
      }
    ],
    "total": 15,
    "limit": 12,
    "offset": 0
  },
  "error": null
}
```

**Error Responses**:

```json
// 404 Not Found - User doesn't exist
{
  "success": false,
  "data": null,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Usuario 'invalid_user' no encontrado"
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripService.ts
import { api } from './api';
import { TripListItem, TripListResponse } from '../types/trip';

export const getUserTrips = async (
  username: string,
  params?: {
    tag?: string;
    status?: 'draft' | 'published';
    limit?: number;
    offset?: number;
  }
): Promise<TripListResponse> => {
  const queryParams = new URLSearchParams();
  if (params?.tag) queryParams.append('tag', params.tag);
  if (params?.status) queryParams.append('status', params.status);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const url = `/users/${username}/trips${queryParams.toString() ? `?${queryParams}` : ''}`;
  const response = await api.get(url);

  return {
    trips: response.data.data.trips,
    total: response.data.data.total,
    limit: response.data.data.limit,
    offset: response.data.data.offset,
  };
};
```

---

## 2. Get Trip Details

### `GET /api/trips/{trip_id}`

Get full trip details including photos, tags, and locations.

**Path Parameters**:
- `trip_id` (string, required): UUID of the trip

**Example Request**:

```http
GET /api/trips/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer eyJhbGciOiJI...
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "trip": {
      "trip_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Vía Verde del Aceite",
      "description": "<p>Ruta espectacular entre olivos centenarios...</p>",
      "status": "published",
      "start_date": "2024-05-15",
      "end_date": "2024-05-17",
      "distance_km": 127.3,
      "difficulty": "moderate",
      "created_at": "2024-12-20T10:30:00Z",
      "updated_at": "2024-12-22T15:45:00Z",
      "published_at": "2024-12-22T15:45:00Z",
      "photos": [
        {
          "photo_id": "770e8400-e29b-41d4-a716-446655440002",
          "photo_url": "http://localhost:8000/storage/trip_photos/2024/12/550e.../abc123_optimized.jpg",
          "thumbnail_url": "http://localhost:8000/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
          "caption": "Vista desde el viaducto",
          "display_order": 0,
          "width": 2000,
          "height": 1500
        }
      ],
      "locations": [
        {
          "location_id": "660e8400-e29b-41d4-a716-446655440001",
          "name": "Baeza",
          "latitude": 37.9963,
          "longitude": -3.4669,
          "sequence": 0
        }
      ],
      "tags": [
        {
          "tag_id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "Vías Verdes",
          "normalized": "vias verdes",
          "usage_count": 125
        }
      ]
    }
  },
  "error": null
}
```

**Error Responses**:

```json
// 404 Not Found - Trip doesn't exist
{
  "success": false,
  "data": null,
  "error": {
    "code": "TRIP_NOT_FOUND",
    "message": "Viaje no encontrado"
  }
}

// 403 Forbidden - Trying to view someone else's draft
{
  "success": false,
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "No tienes permiso para ver este viaje"
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripService.ts
export const getTripById = async (tripId: string): Promise<Trip> => {
  const response = await api.get(`/trips/${tripId}`);
  return response.data.data.trip;
};
```

---

## 3. Create Trip

### `POST /api/trips`

Create a new trip (defaults to `draft` status).

**Request Body**:

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

**Required Fields**:
- `title` (1-200 characters)
- `description` (1-50000 characters, no minimum for drafts)
- `start_date` (ISO 8601: YYYY-MM-DD, cannot be future)

**Optional Fields**:
- `end_date` (ISO 8601: YYYY-MM-DD, must be >= start_date)
- `distance_km` (0.1-10000)
- `difficulty` (`easy`, `moderate`, `difficult`, `very_difficult`)
- `locations` (array, max 50 items)
- `tags` (array of strings, max 10 tags, max 50 chars each)

**Success Response** (201 Created):

```json
{
  "success": true,
  "data": {
    "trip": {
      "trip_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "draft",
      ...
    }
  },
  "error": null
}
```

**Error Responses**:

```json
// 400 Bad Request - Validation error
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La fecha de inicio no puede ser futura",
    "field": "start_date"
  }
}

// 401 Unauthorized - Not authenticated
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Autenticación requerida"
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripService.ts
export const createTrip = async (tripData: TripCreateInput): Promise<Trip> => {
  const response = await api.post('/trips', tripData);
  return response.data.data.trip;
};
```

---

## 4. Update Trip

### `PUT /api/trips/{trip_id}`

Update an existing trip (partial updates supported).

**Path Parameters**:
- `trip_id` (string, required): UUID of the trip

**Request Body** (all fields optional):

```json
{
  "title": "Vía Verde del Aceite - ACTUALIZADO",
  "description": "<p>Actualización con más detalles...</p>",
  "distance_km": 130.5,
  "client_updated_at": "2024-12-24T10:30:00Z"
}
```

**Optimistic Locking**:
- Include `client_updated_at` (timestamp when client loaded the trip)
- Backend compares with `updated_at` to detect concurrent edits
- If mismatch, returns 409 Conflict

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "trip": {
      "trip_id": "550e8400-e29b-41d4-a716-446655440000",
      "updated_at": "2024-12-24T11:00:00Z",
      ...
    }
  },
  "error": null
}
```

**Error Responses**:

```json
// 403 Forbidden - Not the owner
{
  "success": false,
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "No tienes permiso para editar este viaje"
  }
}

// 409 Conflict - Concurrent edit detected
{
  "success": false,
  "data": null,
  "error": {
    "code": "CONCURRENT_EDIT",
    "message": "El viaje fue modificado por otra sesión. Recarga la página."
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripService.ts
export const updateTrip = async (
  tripId: string,
  updates: TripUpdateInput
): Promise<Trip> => {
  const response = await api.put(`/trips/${tripId}`, updates);
  return response.data.data.trip;
};
```

---

## 5. Delete Trip

### `DELETE /api/trips/{trip_id}`

Permanently delete a trip and all associated data (photos, tags, locations).

**Path Parameters**:
- `trip_id` (string, required): UUID of the trip

**Example Request**:

```http
DELETE /api/trips/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer eyJhbGciOiJI...
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "message": "Viaje eliminado correctamente"
  },
  "error": null
}
```

**Error Responses**:

```json
// 403 Forbidden - Not the owner
{
  "success": false,
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "No tienes permiso para eliminar este viaje"
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripService.ts
export const deleteTrip = async (tripId: string): Promise<void> => {
  await api.delete(`/trips/${tripId}`);
};
```

---

## 6. Publish Trip

### `POST /api/trips/{trip_id}/publish`

Change trip status from `draft` to `published`. Enforces publication requirements.

**Path Parameters**:
- `trip_id` (string, required): UUID of the trip

**Publish Requirements** (enforced by backend):
- Description must be at least 50 characters
- All other required fields must be valid

**Example Request**:

```http
POST /api/trips/550e8400-e29b-41d4-a716-446655440000/publish
Authorization: Bearer eyJhbGciOiJI...
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "trip": {
      "trip_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "published",
      "published_at": "2024-12-24T11:00:00Z",
      ...
    }
  },
  "error": null
}
```

**Error Responses**:

```json
// 400 Bad Request - Validation failed
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La descripción debe tener al menos 50 caracteres para publicar",
    "field": "description"
  }
}

// 409 Conflict - Trip already published
{
  "success": false,
  "data": null,
  "error": {
    "code": "ALREADY_PUBLISHED",
    "message": "El viaje ya está publicado"
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripService.ts
export const publishTrip = async (tripId: string): Promise<Trip> => {
  const response = await api.post(`/trips/${tripId}/publish`);
  return response.data.data.trip;
};
```

---

## 7. Upload Photo

### `POST /api/trips/{trip_id}/photos`

Upload a photo to trip gallery.

**Path Parameters**:
- `trip_id` (string, required): UUID of the trip

**Request Body** (multipart/form-data):
- `photo` (file, required): Image file (JPG/PNG, max 10MB)
- `caption` (string, optional): Photo caption (max 500 characters)

**Constraints**:
- Max 20 photos per trip
- Max 10MB per photo
- Allowed formats: JPG, PNG

**Example Request**:

```http
POST /api/trips/550e8400-e29b-41d4-a716-446655440000/photos
Content-Type: multipart/form-data
Authorization: Bearer eyJhbGciOiJI...

------WebKitFormBoundary
Content-Disposition: form-data; name="photo"; filename="sunset.jpg"
Content-Type: image/jpeg

[binary data]
------WebKitFormBoundary
Content-Disposition: form-data; name="caption"

Vista desde el viaducto sobre el valle
------WebKitFormBoundary--
```

**Success Response** (201 Created):

```json
{
  "success": true,
  "data": {
    "photo": {
      "photo_id": "770e8400-e29b-41d4-a716-446655440002",
      "photo_url": "http://localhost:8000/storage/trip_photos/2024/12/550e.../abc123_optimized.jpg",
      "thumbnail_url": "http://localhost:8000/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
      "caption": "Vista desde el viaducto sobre el valle",
      "display_order": 5,
      "width": 2000,
      "height": 1500
    }
  },
  "error": null
}
```

**Error Responses**:

```json
// 400 Bad Request - Invalid file
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_FILE",
    "message": "Solo se permiten imágenes JPG y PNG (máx 10MB)"
  }
}

// 400 Bad Request - Photo limit exceeded
{
  "success": false,
  "data": null,
  "error": {
    "code": "PHOTO_LIMIT_EXCEEDED",
    "message": "Máximo 20 fotos permitidas por viaje"
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripPhotoService.ts
export const uploadTripPhoto = async (
  tripId: string,
  file: File,
  caption?: string,
  onProgress?: (progress: number) => void
): Promise<TripPhoto> => {
  const formData = new FormData();
  formData.append('photo', file);
  if (caption) formData.append('caption', caption);

  const response = await api.post(`/trips/${tripId}/photos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });

  return response.data.data.photo;
};
```

---

## 8. Delete Photo

### `DELETE /api/trips/{trip_id}/photos/{photo_id}`

Delete a photo from trip gallery.

**Path Parameters**:
- `trip_id` (string, required): UUID of the trip
- `photo_id` (string, required): UUID of the photo

**Example Request**:

```http
DELETE /api/trips/550e8400-e29b-41d4-a716-446655440000/photos/770e8400-e29b-41d4-a716-446655440002
Authorization: Bearer eyJhbGciOiJI...
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "message": "Foto eliminada correctamente"
  },
  "error": null
}
```

**Error Responses**:

```json
// 404 Not Found - Photo doesn't exist
{
  "success": false,
  "data": null,
  "error": {
    "code": "PHOTO_NOT_FOUND",
    "message": "Foto no encontrada"
  }
}
```

**Frontend Usage**:

```typescript
// src/services/tripPhotoService.ts
export const deleteTripPhoto = async (
  tripId: string,
  photoId: string
): Promise<void> => {
  await api.delete(`/trips/${tripId}/photos/${photoId}`);
};
```

---

## 9. Reorder Photos

### `PUT /api/trips/{trip_id}/photos/reorder`

Update the display order of photos in trip gallery.

**Path Parameters**:
- `trip_id` (string, required): UUID of the trip

**Request Body**:

```json
{
  "photo_order": [
    "photo_id_3",
    "photo_id_1",
    "photo_id_2"
  ]
}
```

**Example Request**:

```http
PUT /api/trips/550e8400-e29b-41d4-a716-446655440000/photos/reorder
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJI...

{
  "photo_order": [
    "770e8400-e29b-41d4-a716-446655440003",
    "770e8400-e29b-41d4-a716-446655440001",
    "770e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "message": "Orden de fotos actualizado correctamente"
  },
  "error": null
}
```

**Frontend Usage**:

```typescript
// src/services/tripPhotoService.ts
export const reorderTripPhotos = async (
  tripId: string,
  photoOrder: string[]
): Promise<void> => {
  await api.put(`/trips/${tripId}/photos/reorder`, {
    photo_order: photoOrder,
  });
};
```

---

## 10. Get All Tags

### `GET /api/tags`

Get all available tags ordered by popularity.

**Authentication**: Not required (public endpoint)

**Example Request**:

```http
GET /api/tags
```

**Success Response** (200 OK):

```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "tag_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Vías Verdes",
        "normalized": "vias verdes",
        "usage_count": 125,
        "created_at": "2024-01-15T08:00:00Z"
      },
      {
        "tag_id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Bikepacking",
        "normalized": "bikepacking",
        "usage_count": 98,
        "created_at": "2024-01-20T10:00:00Z"
      }
    ],
    "count": 2
  },
  "error": null
}
```

**Frontend Usage**:

```typescript
// src/services/tripService.ts
export const getAllTags = async (): Promise<Tag[]> => {
  const response = await api.get('/tags');
  return response.data.data.tags;
};
```

**Usage Pattern**:
- Fetch once on component mount (Decision #3 from research.md)
- Store in local state
- Filter client-side as user types

---

## Error Handling Pattern

### Standard Error Handler

```typescript
// src/services/tripService.ts
import toast from 'react-hot-toast';

const handleApiError = (error: any): void => {
  console.error('API Error:', error);

  const errorMessage =
    error.response?.data?.error?.message ||
    'Error de conexión. Intenta nuevamente.';

  toast.error(errorMessage, {
    duration: 5000,
    position: 'top-center',
    style: {
      background: '#dc2626',
      color: '#f5f1e8',
      fontFamily: 'var(--font-sans)',
      fontSize: '0.875rem',
      fontWeight: '600',
    },
  });
};

// Usage
try {
  const trip = await createTrip(tripData);
  return trip;
} catch (error) {
  handleApiError(error);
  throw error; // Re-throw for component-level handling
}
```

---

## Performance Considerations

### Chunked Photo Uploads

For uploading multiple photos (Decision #2 from research.md):

```typescript
// src/hooks/useTripPhotos.ts
const uploadPhotosChunked = async (tripId: string, files: File[]) => {
  const CHUNK_SIZE = 3;
  const results = [];

  for (let i = 0; i < files.length; i += CHUNK_SIZE) {
    const chunk = files.slice(i, i + CHUNK_SIZE);

    // Upload chunk in parallel
    const chunkResults = await Promise.allSettled(
      chunk.map((file, index) =>
        uploadTripPhoto(tripId, file, undefined, (progress) => {
          setUploadProgress((prev) => ({ ...prev, [i + index]: progress }));
        })
      )
    );

    results.push(...chunkResults);
  }

  return results;
};
```

**Performance**:
- Sequential: 5 photos × 6s = 30s ✅
- Chunked (3): 5 photos ÷ 2 chunks × 6s = ~12s ✅ (2x faster)

---

## Response Caching

### No Caching for Mutations

- `POST`, `PUT`, `DELETE` endpoints: No caching
- Always fetch fresh data after mutations

### Conditional Caching for Reads

```typescript
// src/hooks/useTripList.ts
import { useState, useEffect } from 'react';

const useTripList = (username: string) => {
  const [trips, setTrips] = useState<TripListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTrips = async () => {
      setIsLoading(true);
      try {
        const data = await getUserTrips(username, { limit: 12, offset: 0 });
        setTrips(data.trips);
      } catch (error) {
        handleApiError(error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrips();
  }, [username]);

  return { trips, isLoading };
};
```

**No SWR/React Query for MVP**: Keep it simple with `useState` + `useEffect`.

---

## CORS Configuration

**Backend CORS Settings** (`.env`):

```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Frontend Development Server**:

```bash
# Vite (default)
npm run dev
# Runs on http://localhost:5173
```

---

## Next Steps

- ✅ API contracts documented (this file)
- ⏳ Developer quickstart guide ([../quickstart.md](../quickstart.md))
- ⏳ Implement services in `frontend/src/services/tripService.ts` and `tripPhotoService.ts`

**After Phase 1**: Use these contracts to implement API services with proper error handling and type safety.
