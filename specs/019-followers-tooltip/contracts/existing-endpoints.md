# API Contracts: Dashboard Followers/Following Tooltips

**Feature**: 019-followers-tooltip
**Date**: 2026-02-13
**Contract Type**: Reference to existing backend endpoints (no new endpoints)

## Overview

This feature uses **existing backend API endpoints** from Feature 004 (Social Network). No new endpoints are created. This document references the existing OpenAPI contracts and explains how the tooltip feature consumes them.

---

## Existing Endpoints Used

### 1. GET /users/{username}/followers

**Purpose**: Retrieve list of users who follow the specified user

**OpenAPI Contract**: `specs/004-social-network/contracts/follow-api.yaml`

**Endpoint**: `/users/{username}/followers`

**Method**: GET

**Authentication**: Required (Bearer token in Authorization header)

**Path Parameters**:
- `username` (string, required): Username of the user whose followers to retrieve

**Query Parameters**: None (pagination not implemented in current backend)

**Request Headers**:
```http
GET /users/maria_garcia/followers HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Response**: 200 OK

**Response Schema**:
```json
{
  "success": true,
  "data": {
    "followers": [
      {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "juan_perez",
        "profile_photo_url": "https://example.com/storage/profile_photos/2024/01/juan.jpg"
      },
      {
        "user_id": "123e4567-e89b-12d3-a456-426614174001",
        "username": "ana_lopez",
        "profile_photo_url": null
      }
      // ... up to 50 followers (backend default limit)
    ],
    "total_count": 12
  },
  "error": null
}
```

**Response Fields**:
- `success` (boolean): Always true for 2xx responses
- `data.followers` (array): List of UserSummaryForFollow objects (up to 50)
- `data.total_count` (number): Total number of followers (may exceed array length)
- `error` (null): Always null on success

**Error Responses**:

- **401 Unauthorized** (not authenticated):
  ```json
  {
    "success": false,
    "data": null,
    "error": {
      "code": "UNAUTHORIZED",
      "message": "Token de autenticación inválido"
    }
  }
  ```

- **404 Not Found** (user doesn't exist):
  ```json
  {
    "success": false,
    "data": null,
    "error": {
      "code": "USER_NOT_FOUND",
      "message": "Usuario no encontrado"
    }
  }
  ```

- **500 Internal Server Error** (database error):
  ```json
  {
    "success": false,
    "data": null,
    "error": {
      "code": "INTERNAL_ERROR",
      "message": "Error interno del servidor"
    }
  }
  ```

**Backend Implementation**:
- File: `backend/src/api/follow.py` (endpoint handler)
- Service: `backend/src/services/follow_service.py` (business logic)
- Returns up to 50 followers by default (no pagination parameter)
- Results ordered by follow creation date DESC (most recent first)

**Tooltip Usage**:
- Frontend calls this endpoint when user hovers over "Seguidores" card
- Frontend slices first 8 users from `data.followers` array
- Uses `data.total_count` to calculate "Ver todos" text (e.g., "+ 7 más")

---

### 2. GET /users/{username}/following

**Purpose**: Retrieve list of users that the specified user is following

**OpenAPI Contract**: `specs/004-social-network/contracts/follow-api.yaml`

**Endpoint**: `/users/{username}/following`

**Method**: GET

**Authentication**: Required (Bearer token in Authorization header)

**Path Parameters**:
- `username` (string, required): Username of the user whose following list to retrieve

**Query Parameters**: None (pagination not implemented in current backend)

**Request Headers**:
```http
GET /users/maria_garcia/following HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**Response**: 200 OK

**Response Schema**:
```json
{
  "success": true,
  "data": {
    "following": [
      {
        "user_id": "123e4567-e89b-12d3-a456-426614174002",
        "username": "carlos_ruiz",
        "profile_photo_url": "https://example.com/storage/profile_photos/2024/02/carlos.jpg"
      },
      {
        "user_id": "123e4567-e89b-12d3-a456-426614174003",
        "username": "laura_martin",
        "profile_photo_url": null
      }
      // ... up to 50 following (backend default limit)
    ],
    "total_count": 15
  },
  "error": null
}
```

**Response Fields**:
- `success` (boolean): Always true for 2xx responses
- `data.following` (array): List of UserSummaryForFollow objects (up to 50)
- `data.total_count` (number): Total number of users being followed
- `error` (null): Always null on success

**Error Responses**: Same as `/followers` endpoint (401, 404, 500)

**Backend Implementation**:
- File: `backend/src/api/follow.py` (endpoint handler)
- Service: `backend/src/services/follow_service.py` (business logic)
- Returns up to 50 following users by default
- Results ordered by follow creation date DESC

**Tooltip Usage**:
- Frontend calls this endpoint when user hovers over "Siguiendo" card
- Frontend slices first 8 users from `data.following` array
- Uses `data.total_count` to calculate "Ver todos" text (e.g., "+ 10 más")

---

## Frontend Service Integration

### followService.ts (EXISTING - No Changes)

**Location**: `frontend/src/services/followService.ts`

**Functions Used**:

```typescript
// Get followers list
export async function getFollowers(username: string): Promise<FollowersListResponse> {
  const response = await apiClient.get(`/users/${username}/followers`);
  return response.data.data; // Unwrap { success, data, error } structure
}

// Get following list
export async function getFollowing(username: string): Promise<FollowingListResponse> {
  const response = await apiClient.get(`/users/${username}/following`);
  return response.data.data;
}
```

**Error Handling** (already implemented):
- Axios interceptors handle 401 (redirect to login)
- Network errors caught and thrown with user-friendly messages
- 404 errors return `{ followers: [], total_count: 0 }` (graceful degradation)

**Response Types**:

```typescript
// Already defined in frontend/src/types/follow.ts
interface UserSummaryForFollow {
  user_id: string;
  username: string;
  profile_photo_url: string | null;
}

interface FollowersListResponse {
  followers: UserSummaryForFollow[];
  total_count: number;
}

interface FollowingListResponse {
  following: UserSummaryForFollow[];
  total_count: number;
}
```

---

## Tooltip Data Transformation

### Backend Response → Tooltip Display

**Example: User has 12 followers**

1. **API Response** (from `/users/maria_garcia/followers`):
   ```json
   {
     "followers": [
       { "user_id": "1", "username": "juan", "profile_photo_url": "..." },
       { "user_id": "2", "username": "ana", "profile_photo_url": null },
       { "user_id": "3", "username": "carlos", "profile_photo_url": "..." },
       { "user_id": "4", "username": "laura", "profile_photo_url": "..." },
       { "user_id": "5", "username": "miguel", "profile_photo_url": "..." },
       { "user_id": "6", "username": "sofia", "profile_photo_url": "..." },
       { "user_id": "7", "username": "pedro", "profile_photo_url": null },
       { "user_id": "8", "username": "carmen", "profile_photo_url": "..." },
       { "user_id": "9", "username": "diego", "profile_photo_url": "..." },
       { "user_id": "10", "username": "isabel", "profile_photo_url": "..." },
       { "user_id": "11", "username": "fernando", "profile_photo_url": "..." },
       { "user_id": "12", "username": "elena", "profile_photo_url": "..." }
     ],
     "total_count": 12
   }
   ```

2. **Frontend Transformation** (in `useFollowersTooltip.ts`):
   ```typescript
   const response = await getFollowers(username);
   const topUsers = response.followers.slice(0, 8); // First 8 only
   const totalCount = response.total_count; // 12

   // Computed in component
   const remaining = totalCount - topUsers.length; // 12 - 8 = 4
   const hasMore = remaining > 0; // true
   ```

3. **Tooltip Display**:
   ```
   ┌────────────────────────┐
   │ 👤 juan                │
   │ 👤 ana                 │
   │ 👤 carlos              │
   │ 👤 laura               │
   │ 👤 miguel              │
   │ 👤 sofia               │
   │ 👤 pedro               │
   │ 👤 carmen              │
   │ ──────────────────     │
   │ + 4 más · Ver todos    │ → /users/maria_garcia/followers
   └────────────────────────┘
   ```

---

## Performance Characteristics

### Response Times (Existing Backend)

- **Simple query** (user with <50 followers): <100ms p95
- **Database query**: Single query with JOIN on users table (no N+1)
- **Response size**: ~200 bytes per user × 50 users = ~10KB max

### Tooltip Optimization

**Lazy Loading**:
- Endpoint NOT called on dashboard mount
- Endpoint called ONLY on hover (500ms delay)
- Avoids unnecessary API calls for users who don't hover

**Network Savings**:
- Without tooltip: 0 API calls (users navigate to separate page to see followers)
- With tooltip: 1 API call per hover (only if user hovers, cached for 200ms leave delay)
- Estimated reduction: 60% fewer full-list page navigations (SC-005)

**Bandwidth**:
- Tooltip uses same endpoint as full list page (no additional bandwidth)
- Frontend slices to 8 users client-side (no backend filtering needed)
- No pagination parameter (backend already limits to 50 users)

---

## Contract Validation

### OpenAPI Schema Validation

**Contract File**: `specs/004-social-network/contracts/follow-api.yaml`

**Validation Rules**:
- `user_id`: string, format: uuid
- `username`: string, minLength: 3, maxLength: 30, pattern: ^[a-zA-Z0-9_]+$
- `profile_photo_url`: string (URL) or null
- `total_count`: integer, minimum: 0

**Frontend Type Safety**:
- TypeScript interfaces enforce compile-time type checking
- Zod schemas (future enhancement) for runtime validation
- Axios interceptors validate response structure

---

## Testing Contracts

### Contract Tests (Existing - Feature 004)

**File**: `backend/tests/contract/test_follow_api.py`

**Tests**:
1. ✅ GET /users/{username}/followers returns 200 with valid schema
2. ✅ Response includes all required fields (user_id, username, profile_photo_url, total_count)
3. ✅ Returns 401 when not authenticated
4. ✅ Returns 404 when user doesn't exist
5. ✅ profile_photo_url is nullable (null when user has no photo)

**No new contract tests required** - Feature 019 reuses existing contracts

### Frontend Integration Tests (NEW)

**File**: `frontend/tests/e2e/dashboard-tooltips.spec.ts` (to be created)

**Tests**:
1. ✅ Tooltip calls correct endpoint when hovering "Seguidores" card
2. ✅ Tooltip displays first 8 users from API response
3. ✅ Tooltip shows "Ver todos" link when total_count > 8
4. ✅ Tooltip handles 0 followers gracefully (empty state)
5. ✅ Tooltip handles network errors gracefully (error message)

---

## Migration Notes

**No Backend Migration Required**: Endpoints already exist since Feature 004 (Social Network)

**No Database Changes Required**: Uses existing `follows` table and `users` table

**Frontend Changes**:
- Add `useFollowersTooltip` hook to call existing `followService.getFollowers()` and `followService.getFollowing()`
- Add `SocialStatTooltip` component to render response data
- No changes to existing `followService.ts` or `follow.ts` types

**Backward Compatibility**: 100% compatible. No breaking changes to existing endpoints.

---

## Security Considerations

### Authentication

**Required**: All requests must include valid JWT token in Authorization header

**Validation**:
- Backend validates token signature and expiration
- Backend checks user has permission to view follower/following lists
- Currently, follower lists are public (any authenticated user can view)

### Authorization

**Current Behavior**:
- Any authenticated user can view any other user's followers/following lists
- Tooltip on dashboard only shows current user's own followers/following (username from `useAuth` hook)
- No privacy settings for followers/following (all public)

**Future Enhancement** (Out of Scope):
- Add privacy settings to hide follower/following lists
- Endpoint would return 403 Forbidden if privacy settings block access

### Rate Limiting

**Current Behavior**: No rate limiting implemented (backend TODO)

**Tooltip Impact**: Minimal risk (1 request per 500ms hover delay max)

**Future Enhancement** (Out of Scope):
- Add rate limiting: 60 requests per minute per user
- Tooltip would show error message if rate limit exceeded

---

## Related Documentation

- **Feature Spec**: [specs/019-followers-tooltip/spec.md](../spec.md)
- **Implementation Plan**: [specs/019-followers-tooltip/plan.md](../plan.md)
- **Data Model**: [specs/019-followers-tooltip/data-model.md](../data-model.md)
- **Existing Contracts**: [specs/004-social-network/contracts/follow-api.yaml](../../004-social-network/contracts/follow-api.yaml)
- **Backend Service**: [backend/src/services/follow_service.py](../../../backend/src/services/follow_service.py)
- **Frontend Service**: [frontend/src/services/followService.ts](../../../frontend/src/services/followService.ts)

---

**Last Updated**: 2026-02-13
**Contract Version**: 1.0.0 (unchanged from Feature 004)
