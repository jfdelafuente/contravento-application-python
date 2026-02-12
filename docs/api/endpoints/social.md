# Social Network Endpoints

API endpoints for social features (follow, comments, likes, public feed).

**OpenAPI Contracts**:
- [social.yaml](../contracts/social.yaml)
- [social-network.yaml](../contracts/social-network.yaml)
- [public-feed-api.yaml](../contracts/public-feed-api.yaml)

---

## Table of Contents

- [POST /users/{username}/follow](#post-usersusernamef follow)
- [DELETE /users/{username}/follow](#delete-usersusernamefollow)
- [GET /users/{username}/following](#get-usersusernamefollowing)
- [GET /users/{username}/followers](#get-usersusernamefollowers)
- [POST /trips/{trip_id}/comments](#post-tripstrip_idcomments)
- [DELETE /trips/{trip_id}/comments/{comment_id}](#delete-tripstrip_idcommentscomment_id)
- [POST /trips/{trip_id}/like](#post-tripstrip_idlike)
- [DELETE /trips/{trip_id}/like](#delete-tripstrip_idlike)
- [GET /feed/public](#get-feedpublic)

---

## POST /users/{username}/follow

Follow a user.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `username` (string): Username to follow

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "follower_id": "123e4567-e89b-12d3-a456-426614174000",
    "following_id": "987fcdeb-51a2-43f7-9abc-123456789012",
    "created_at": "2024-06-01T12:00:00Z"
  },
  "error": null
}
```

**Validation**:
- Cannot follow yourself
- Cannot follow the same user twice

**Errors**:
- `400` - Cannot follow yourself
- `401` - Unauthorized
- `404` - User not found
- `409` - Already following

---

## DELETE /users/{username}/follow

Unfollow a user.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `username` (string): Username to unfollow

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Dejaste de seguir a {username}"
  },
  "error": null
}
```

**Errors**:
- `401` - Unauthorized
- `404` - User not found or not following

---

## GET /users/{username}/following

Get list of users that this user follows.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `username` (string): Username

**Query Parameters**:
- `limit` (int, optional, default: 50): Max users per page
- `offset` (int, optional, default: 0): Pagination offset

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "following": [
      {
        "user_id": "...",
        "username": "maria_garcia",
        "full_name": "María García",
        "photo_url": "/storage/profile_photos/...",
        "location": "Barcelona, España",
        "cycling_type": "gravel"
      }
    ],
    "total": 15,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Errors**:
- `401` - Unauthorized
- `404` - User not found

---

## GET /users/{username}/followers

Get list of users following this user.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `username` (string): Username

**Query Parameters**:
- `limit` (int, optional, default: 50): Max users per page
- `offset` (int, optional, default: 0): Pagination offset

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "followers": [
      {
        "user_id": "...",
        "username": "johndoe",
        "full_name": "John Doe",
        "photo_url": "/storage/profile_photos/...",
        "location": "Madrid, España",
        "cycling_type": "road"
      }
    ],
    "total": 42,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Errors**:
- `401` - Unauthorized
- `404` - User not found

---

## POST /trips/{trip_id}/comments

Add comment to a trip.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Request Body**:
```json
{
  "content": "¡Qué ruta tan espectacular! Me encantaría hacerla algún día."
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "comment_id": "abc123-456def-789ghi",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "user": {
      "user_id": "...",
      "username": "johndoe",
      "photo_url": "/storage/profile_photos/..."
    },
    "content": "¡Qué ruta tan espectacular! Me encantaría hacerla algún día.",
    "created_at": "2024-06-01T15:30:00Z"
  },
  "error": null
}
```

**Validation**:
- Content: Required, max 1000 chars
- Trip must be published (cannot comment on drafts)

**Errors**:
- `400` - Validation error
- `401` - Unauthorized
- `403` - Trip is draft
- `404` - Trip not found

---

## DELETE /trips/{trip_id}/comments/{comment_id}

Delete a comment (owner only).

**Authentication**: Required (Bearer token, must be comment author)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier
- `comment_id` (UUID): Comment identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Comentario eliminado correctamente"
  },
  "error": null
}
```

**Authorization**:
- Only comment author can delete
- Trip owner can delete any comment on their trip (moderation)

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (not comment author or trip owner)
- `404` - Comment not found

---

## POST /trips/{trip_id}/like

Like a trip.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "like_id": "def456-789ghi-012jkl",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2024-06-01T16:00:00Z"
  },
  "error": null
}
```

**Validation**:
- Cannot like the same trip twice
- Trip must be published

**Errors**:
- `401` - Unauthorized
- `403` - Trip is draft
- `404` - Trip not found
- `409` - Already liked

---

## DELETE /trips/{trip_id}/like

Unlike a trip.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Like eliminado correctamente"
  },
  "error": null
}
```

**Errors**:
- `401` - Unauthorized
- `404` - Trip not found or not liked

---

## GET /feed/public

Get public feed of trips (all users).

**Authentication**: Required (Bearer token)

**Query Parameters**:
- `tag` (string, optional): Filter by tag
- `cycling_type` (string, optional): Filter by cycling type
- `limit` (int, optional, default: 20): Max trips per page
- `offset` (int, optional, default: 0): Pagination offset
- `sort_by` (string, optional, default: recent): Sort order (recent, popular)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "...",
        "title": "Vía Verde del Aceite",
        "description": "...",
        "user": {
          "user_id": "...",
          "username": "johndoe",
          "photo_url": "/storage/profile_photos/..."
        },
        "cover_photo": {
          "photo_url": "/storage/trip_photos/.../optimized.jpg",
          "thumb_url": "/storage/trip_photos/.../thumb.jpg"
        },
        "distance_km": 127.3,
        "start_date": "2024-05-15",
        "published_at": "2024-05-20T10:00:00Z",
        "tags": ["vías verdes", "andalucía"],
        "like_count": 15,
        "comment_count": 3
      }
    ],
    "total": 1243,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

**Sorting**:
- `recent`: Published date descending (newest first)
- `popular`: Like count + comment count (most popular first)

**Visibility**:
- Only published trips shown
- Drafts excluded

**Errors**:
- `401` - Unauthorized
- `400` - Invalid sort_by or cycling_type

---

## Related Documentation

- **[OpenAPI Contracts](../contracts/)** - social.yaml, public-feed-api.yaml
- **[User Guide: Following Users](../../user-guides/social/following-users.md)** - End-user guide
- **[User Guide: Public Feed](../../user-guides/social/public-feed.md)** - Feed guide
- **[Feature: Social Network](../../features/social-network.md)** - Feature overview
- **[Manual Testing](../testing/manual-testing.md)** - curl examples

---

**Last Updated**: 2026-02-06
**API Version**: 1.0.0
