# Users & Profiles Endpoints

API endpoints for user profiles and statistics.

**OpenAPI Contracts**:
- [profile.yaml](../contracts/profile.yaml)
- [stats.yaml](../contracts/stats.yaml)

---

## Table of Contents

- [GET /users/me](#get-usersme)
- [GET /users/{username}](#get-usersusername)
- [PUT /users/me](#put-usersme)
- [POST /users/me/photo](#post-usersmephoto)
- [DELETE /users/me/photo](#delete-usersmephoto)
- [GET /users/me/stats](#get-usersmestats)
- [GET /users/{username}/stats](#get-usersusernamestats)

---

## GET /users/me

Get current authenticated user's profile.

**Authentication**: Required (Bearer token)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "bio": "Passionate cyclist from Madrid",
    "location": "Madrid, España",
    "cycling_type": "road",
    "photo_url": "/storage/profile_photos/2024/06/john_123.jpg",
    "is_verified": true,
    "created_at": "2024-01-15T10:00:00Z"
  },
  "error": null
}
```

**Errors**:
- `401` - Unauthorized

---

## GET /users/{username}

Get public profile of any user.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `username` (string): Username to lookup

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user_id": "...",
    "username": "johndoe",
    "full_name": "John Doe",
    "bio": "Passionate cyclist from Madrid",
    "location": "Madrid, España",
    "cycling_type": "road",
    "photo_url": "/storage/profile_photos/...",
    "created_at": "2024-01-15T10:00:00Z"
  },
  "error": null
}
```

**Privacy**:
- Email address not included in public profiles
- Only published trips visible via related endpoints

**Errors**:
- `401` - Unauthorized
- `404` - User not found

---

## PUT /users/me

Update current user's profile.

**Authentication**: Required (Bearer token)

**Request Body** (partial updates supported):
```json
{
  "full_name": "John Doe Updated",
  "bio": "Passionate cyclist and bikepacker from Madrid",
  "location": "Barcelona, España",
  "cycling_type": "gravel"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user_id": "...",
    "username": "johndoe",
    "full_name": "John Doe Updated",
    "bio": "Passionate cyclist and bikepacker from Madrid",
    "location": "Barcelona, España",
    "cycling_type": "gravel",
    ...
  },
  "error": null
}
```

**Validation**:
- Full name: Max 100 chars
- Bio: Max 500 chars
- Location: Max 100 chars
- Cycling type: One of: road, mountain, gravel, bikepacking, touring, commuting, BMX, track

**Errors**:
- `400` - Validation error
- `401` - Unauthorized

---

## POST /users/me/photo

Upload profile photo.

**Authentication**: Required (Bearer token)

**Request Body** (multipart/form-data):
- `photo` (file): Image file (JPG, PNG, WebP)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "photo_url": "/storage/profile_photos/2024/06/john_123.jpg"
  },
  "error": null
}
```

**Validation**:
- Max 5MB per photo
- Supported formats: JPG, PNG, WebP

**Processing**:
- Resize to 400x400px (square crop)
- Replaces existing photo (old deleted from storage)

**Errors**:
- `400` - Validation error (format, size)
- `401` - Unauthorized

---

## DELETE /users/me/photo

Delete profile photo (revert to default).

**Authentication**: Required (Bearer token)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Foto de perfil eliminada correctamente",
    "photo_url": null
  },
  "error": null
}
```

**Errors**:
- `401` - Unauthorized

---

## GET /users/me/stats

Get current user's statistics.

**Authentication**: Required (Bearer token)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "total_trips": 42,
    "published_trips": 38,
    "draft_trips": 4,
    "total_distance_km": 3248.5,
    "longest_trip_km": 325.0,
    "total_photos": 156,
    "countries_visited": ["España", "Francia", "Italia"],
    "achievements": [
      {
        "achievement_id": "first_trip",
        "name": "Primer Viaje",
        "description": "Crea tu primer viaje",
        "icon": "🚴",
        "unlocked_at": "2024-01-20T15:30:00Z"
      }
    ]
  },
  "error": null
}
```

**Auto-Update Triggers**:
- Trip creation/deletion
- Trip publishing
- Photo uploads
- Distance updates

**Errors**:
- `401` - Unauthorized

---

## GET /users/{username}/stats

Get public statistics for any user.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `username` (string): Username to lookup

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "total_trips": 42,
    "published_trips": 38,
    "total_distance_km": 3248.5,
    "longest_trip_km": 325.0,
    "total_photos": 156,
    "countries_visited": ["España", "Francia", "Italia"],
    "achievements": [...]
  },
  "error": null
}
```

**Privacy**:
- Only published trips count toward public stats
- Draft trips excluded from counts

**Errors**:
- `401` - Unauthorized
- `404` - User not found

---

## Related Documentation

- **[OpenAPI Contracts](../contracts/)** - profile.yaml, stats.yaml
- **[User Guide: Profile Management](../../user-guides/profile/editing-profile.md)** - End-user guide
- **[User Guide: Stats Explained](../../user-guides/profile/stats-explained.md)** - Stats guide
- **[Feature: Stats Integration](../../features/stats-integration.md)** - Auto-update logic
- **[Manual Testing](../testing/manual-testing.md)** - curl examples

---

**Last Updated**: 2026-02-06
**API Version**: 1.0.0
