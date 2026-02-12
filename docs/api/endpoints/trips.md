# Trips Endpoints

API endpoints for managing cycling trips (Travel Diary feature).

**OpenAPI Contract**: [trips.yaml](../contracts/trips.yaml)

---

## Table of Contents

- [POST /trips](#post-trips)
- [GET /trips/{trip_id}](#get-tripstrip_id)
- [PUT /trips/{trip_id}](#put-tripstrip_id)
- [DELETE /trips/{trip_id}](#delete-tripstrip_id)
- [POST /trips/{trip_id}/publish](#post-tripstrip_idpublish)
- [GET /users/{username}/trips](#get-usersusernametrips)
- [POST /trips/{trip_id}/photos](#post-tripstrip_idphotos)
- [DELETE /trips/{trip_id}/photos/{photo_id}](#delete-tripstrip_idphotosphoto_id)
- [PUT /trips/{trip_id}/photos/reorder](#put-tripstrip_idphotosreorder)
- [GET /tags](#get-tags)

---

## POST /trips

Create a new trip (draft by default).

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "title": "Vía Verde del Aceite",
  "description": "Un recorrido espectacular de 127 kilómetros entre Jaén y Córdoba, atravesando olivares centenarios y pueblos con encanto. Perfecto para cicloturismo.",
  "start_date": "2024-05-15",
  "end_date": "2024-05-17",
  "distance_km": 127.3,
  "difficulty": "moderate",
  "locations": [
    {"name": "Jaén"},
    {"name": "Baeza"},
    {"name": "Córdoba"}
  ],
  "tags": ["vías verdes", "andalucía", "olivares"]
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Vía Verde del Aceite",
    "description": "Un recorrido espectacular...",
    "status": "draft",
    "start_date": "2024-05-15",
    "end_date": "2024-05-17",
    "distance_km": 127.3,
    "difficulty": "moderate",
    "created_at": "2024-12-28T12:00:00Z",
    "updated_at": "2024-12-28T12:00:00Z",
    "published_at": null,
    "photos": [],
    "locations": [...],
    "tags": [...]
  },
  "error": null
}
```

**Validation**:
- Title: Required, max 200 chars
- Description: Optional for draft, ≥50 chars for publishing
- Dates: start_date ≤ end_date
- Distance: Optional, ≥0
- Difficulty: One of: easy, moderate, hard
- Tags: Max 10 per trip, case-insensitive matching
- Photos: Max 20 per trip

**Errors**:
- `400` - Validation error
- `401` - Unauthorized

---

## GET /trips/{trip_id}

Get trip details by ID.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Vía Verde del Aceite",
    "status": "published",
    "photos": [
      {
        "photo_id": "abc123",
        "photo_url": "/storage/trip_photos/.../optimized.jpg",
        "thumb_url": "/storage/trip_photos/.../thumb.jpg",
        "order": 0
      }
    ],
    "locations": [...],
    "tags": [...]
  },
  "error": null
}
```

**Visibility**:
- Draft trips: Only visible to owner
- Published trips: Visible to all authenticated users

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (trying to view someone else's draft)
- `404` - Trip not found

---

## PUT /trips/{trip_id}

Update trip details (owner only).

**Authentication**: Required (Bearer token, must be owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Request Body** (partial updates supported):
```json
{
  "title": "Vía Verde del Aceite - Actualizado",
  "distance_km": 135.5,
  "client_updated_at": "2024-12-28T12:00:00Z"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Vía Verde del Aceite - Actualizado",
    "distance_km": 135.5,
    "updated_at": "2024-12-28T12:10:00Z",
    ...
  },
  "error": null
}
```

**Optimistic Locking**:
- Include `client_updated_at` with last known `updated_at` timestamp
- Prevents concurrent edit conflicts

**Errors**:
- `400` - Validation error
- `401` - Unauthorized
- `403` - Forbidden (not owner)
- `404` - Trip not found
- `409` - Conflict (trip modified by another session)

---

## DELETE /trips/{trip_id}

Delete trip and all associated data (owner only).

**Authentication**: Required (Bearer token, must be owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Viaje eliminado correctamente",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "error": null
}
```

**Cascading Deletes**:
- All trip photos deleted from storage
- All trip locations deleted
- All trip tags associations removed
- User stats updated (trip_count, distance_km)

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (not owner)
- `404` - Trip not found

---

## POST /trips/{trip_id}/publish

Publish a draft trip (makes it visible to all users).

**Authentication**: Required (Bearer token, must be owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "published",
    "published_at": "2024-12-28T12:05:00Z"
  },
  "error": null
}
```

**Validation**:
- Description must be ≥50 chars
- Dates must be valid (start ≤ end)
- Trip must be in draft status

**Stats Update**:
- User `trip_count` incremented
- User `total_distance_km` updated

**Errors**:
- `400` - Validation error (description too short)
- `401` - Unauthorized
- `403` - Forbidden (not owner)
- `404` - Trip not found

---

## GET /users/{username}/trips

List trips for a user (with filtering and pagination).

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `username` (string): Username

**Query Parameters**:
- `tag` (string, optional): Filter by tag (case-insensitive)
- `status` (string, optional): Filter by status (draft/published)
- `limit` (int, optional, default: 50): Max trips per page
- `offset` (int, optional, default: 0): Pagination offset

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "...",
        "title": "...",
        "status": "published",
        ...
      }
    ],
    "total": 42,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Visibility**:
- Own trips: All trips (draft + published)
- Other users' trips: Only published trips

**Errors**:
- `401` - Unauthorized
- `404` - User not found

---

## POST /trips/{trip_id}/photos

Upload photo to trip.

**Authentication**: Required (Bearer token, must be owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Request Body** (multipart/form-data):
- `photo` (file): Image file (JPG, PNG, WebP)

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "photo_id": "abc123-456def-789ghi",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "photo_url": "/storage/trip_photos/2024/12/.../optimized.jpg",
    "thumb_url": "/storage/trip_photos/2024/12/.../thumb.jpg",
    "order": 0
  },
  "error": null
}
```

**Validation**:
- Max 20 photos per trip
- Max 10MB per photo
- Supported formats: JPG, PNG, WebP

**Processing**:
- Resize to max 1200px width (optimized)
- Generate 400x400px thumbnail
- Extract EXIF metadata (GPS, timestamp)

**Errors**:
- `400` - Validation error (format, size, limit)
- `401` - Unauthorized
- `403` - Forbidden (not owner)
- `404` - Trip not found

---

## DELETE /trips/{trip_id}/photos/{photo_id}

Delete photo from trip.

**Authentication**: Required (Bearer token, must be owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier
- `photo_id` (UUID): Photo identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Foto eliminada correctamente"
  },
  "error": null
}
```

**Auto-Reordering**:
- Remaining photos reordered to fill gap (0, 1, 2, ...)

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (not owner)
- `404` - Photo not found

---

## PUT /trips/{trip_id}/photos/reorder

Reorder trip photos.

**Authentication**: Required (Bearer token, must be owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Request Body**:
```json
{
  "photo_order": [
    "ghi789-012jkl-345mno",
    "abc123-456def-789ghi",
    "def456-789ghi-012jkl"
  ]
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Fotos reordenadas correctamente"
  },
  "error": null
}
```

**Validation**:
- All photo IDs must belong to the trip
- Count must match current photo count

**Errors**:
- `400` - Validation error (invalid IDs, wrong count)
- `401` - Unauthorized
- `403` - Forbidden (not owner)
- `404` - Trip not found

---

## GET /tags

Get all available tags (ordered by popularity).

**Authentication**: Required (Bearer token)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "tag_id": "tag-1",
        "name": "bikepacking",
        "normalized": "bikepacking",
        "usage_count": 42
      },
      {
        "tag_id": "tag-2",
        "name": "Montaña",
        "normalized": "montaña",
        "usage_count": 38
      }
    ]
  },
  "error": null
}
```

**Ordering**:
- Tags sorted by `usage_count` (descending)
- Most popular tags first

**Case-Insensitive Matching**:
- Tags stored with original capitalization (`name`)
- Matching uses lowercase (`normalized`)

**Errors**:
- `401` - Unauthorized

---

## Related Documentation

- **[OpenAPI Contract](../contracts/trips.yaml)** - Full trips API schema
- **[Manual Testing](../testing/manual-testing.md)** - curl examples
- **[Postman Guide](../testing/postman-guide.md)** - Postman collection
- **[User Guide: Creating Trips](../../user-guides/trips/creating-trips.md)** - End-user guide
- **[Feature: Travel Diary](../../features/travel-diary.md)** - Feature overview

---

**Last Updated**: 2026-02-06
**API Version**: 0.4.0 (Tags & Categorization)
