# Data Model: Dashboard Followers/Following Tooltips

**Feature**: 019-followers-tooltip
**Date**: 2026-02-13
**Type**: Frontend-only (TypeScript interfaces)

## Overview

This feature is **frontend-only** and does not introduce any backend database changes. All types are TypeScript interfaces used for tooltip rendering and data transformation. The backend endpoints `/users/{username}/followers` and `/users/{username}/following` already exist and return the required data structure.

## Frontend Types (TypeScript)

### 1. UserSummaryForFollow (EXISTING - No Changes)

**Location**: `frontend/src/types/follow.ts` (already defined)

**Purpose**: Represents a single user in the follower/following list.

**Interface**:
```typescript
interface UserSummaryForFollow {
  user_id: string;
  username: string;
  profile_photo_url: string | null;
}
```

**Fields**:
- `user_id` (string): Unique identifier for the user (UUID format)
- `username` (string): User's display username
- `profile_photo_url` (string | null): URL to profile photo, or null if no photo uploaded

**Source**: Returned by backend endpoints `/users/{username}/followers` and `/users/{username}/following`

**Used By**: Tooltip component to render user avatars and usernames

---

### 2. FollowersListResponse (EXISTING - No Changes)

**Location**: `frontend/src/types/follow.ts` (already defined)

**Purpose**: Response structure from `/users/{username}/followers` endpoint.

**Interface**:
```typescript
interface FollowersListResponse {
  followers: UserSummaryForFollow[];
  total_count: number;
}
```

**Fields**:
- `followers` (UserSummaryForFollow[]): Array of follower users
- `total_count` (number): Total number of followers (may exceed array length due to pagination)

**Backend Behavior**: Returns up to 50 followers by default (no pagination parameter)

**Tooltip Usage**: Frontend slices first 8 users from `followers` array for tooltip preview

---

### 3. FollowingListResponse (EXISTING - No Changes)

**Location**: `frontend/src/types/follow.ts` (already defined)

**Purpose**: Response structure from `/users/{username}/following` endpoint.

**Interface**:
```typescript
interface FollowingListResponse {
  following: UserSummaryForFollow[];
  total_count: number;
}
```

**Fields**:
- `following` (UserSummaryForFollow[]): Array of users being followed
- `total_count` (number): Total number of users being followed

**Backend Behavior**: Returns up to 50 following users by default

**Tooltip Usage**: Frontend slices first 8 users from `following` array for tooltip preview

---

### 4. UseFollowersTooltipReturn (NEW)

**Location**: `frontend/src/hooks/useFollowersTooltip.ts` (new file)

**Purpose**: Return type for the `useFollowersTooltip` custom hook.

**Interface**:
```typescript
interface UseFollowersTooltipReturn {
  users: UserSummaryForFollow[];
  totalCount: number;
  isLoading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
}
```

**Fields**:
- `users` (UserSummaryForFollow[]): First 5-8 users for tooltip display (sliced from API response)
- `totalCount` (number): Total count of followers/following (from API response)
- `isLoading` (boolean): True while fetching data, false when complete or error
- `error` (string | null): User-friendly error message in Spanish, or null if no error
- `fetchUsers` (() => Promise<void>): Function to trigger data fetch (called on hover)

**Computed Properties**:
- `hasMore`: Derived as `totalCount > users.length` (not returned directly, computed in component)

**State Management**: Hook uses React useState internally for all fields

---

### 5. SocialStatTooltipProps (NEW)

**Location**: `frontend/src/components/dashboard/SocialStatTooltip.tsx` (new file)

**Purpose**: Props interface for the `SocialStatTooltip` component.

**Interface**:
```typescript
interface SocialStatTooltipProps {
  users: UserSummaryForFollow[];
  totalCount: number;
  type: 'followers' | 'following';
  username: string;
  isLoading: boolean;
  error: string | null;
  visible: boolean;
}
```

**Fields**:
- `users` (UserSummaryForFollow[]): List of users to display in tooltip
- `totalCount` (number): Total count for calculating "Ver todos" link text (e.g., "+ 7 más")
- `type` ('followers' | 'following'): Determines link destination and title text
- `username` (string): Current user's username for building navigation URLs
- `isLoading` (boolean): Show loading spinner when true
- `error` (string | null): Show error message when not null
- `visible` (boolean): Control tooltip visibility (CSS display: none when false)

**Computed in Component**:
- `remaining`: Calculated as `totalCount - users.length` (number of users not shown in preview)
- `title`: Conditional text ("Seguidores" or "Siguiendo") based on `type`
- `viewAllUrl`: Conditional URL (`/users/${username}/followers` or `/users/${username}/following`)

**Rendering Logic**:
- If `!visible`: Return null (early exit, component not rendered)
- If `isLoading`: Show spinner with "Cargando..." message
- If `error`: Show error message with red border (future enhancement)
- If `users.length === 0`: Show empty state message ("No tienes seguidores aún" or "No sigues a nadie aún")
- If `users.length > 0`: Render user list + "Ver todos" link (if `remaining > 0`)

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ SocialStatsSection Component                                │
│                                                              │
│  [Hover "Seguidores" card for 500ms]                        │
│          ↓                                                   │
│  useFollowersTooltip('maria_garcia', 'followers')            │
│          ↓                                                   │
│  fetchUsers() called                                         │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ useFollowersTooltip Hook (Data Fetching)                    │
│                                                              │
│  1. setIsLoading(true)                                       │
│  2. Call followService.getFollowers('maria_garcia')          │
│          ↓                                                   │
│  3. API Request: GET /users/maria_garcia/followers           │
│          ↓                                                   │
│  4. Backend Response:                                        │
│     {                                                        │
│       followers: [                                           │
│         { user_id: "1", username: "juan", photo_url: "..." },│
│         { user_id: "2", username: "ana", photo_url: null }, │
│         ... (up to 50 users)                                 │
│       ],                                                     │
│       total_count: 12                                        │
│     }                                                        │
│          ↓                                                   │
│  5. Slice first 8: users = response.followers.slice(0, 8)   │
│  6. Store totalCount = 12                                    │
│  7. setIsLoading(false)                                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ SocialStatTooltip Component (Presentation)                   │
│                                                              │
│  Props received:                                             │
│  - users: [juan, ana, carlos, laura, miguel, sofia, pedro, │
│            carmen] (8 users)                                 │
│  - totalCount: 12                                            │
│  - type: 'followers'                                         │
│  - visible: true                                             │
│                                                              │
│  Computed:                                                   │
│  - remaining = 12 - 8 = 4                                    │
│  - title = "Seguidores"                                      │
│  - viewAllUrl = "/users/maria_garcia/followers"              │
│                                                              │
│  Rendered:                                                   │
│  ┌────────────────────────┐                                 │
│  │ 👤 juan                │                                 │
│  │ 👤 ana                 │                                 │
│  │ 👤 carlos              │                                 │
│  │ ... (8 users)          │                                 │
│  │ ──────────────────     │                                 │
│  │ + 4 más · Ver todos    │ → Link to /users/.../followers  │
│  └────────────────────────┘                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Validation Rules

### Frontend Validation

**UserSummaryForFollow** (from backend):
- `user_id`: Required, non-empty string (UUID format assumed)
- `username`: Required, non-empty string (3-30 chars, alphanumeric + underscore)
- `profile_photo_url`: Nullable string (valid URL or null)

**Tooltip Display**:
- Maximum users shown: 8 (hardcoded, not configurable)
- Empty state: Show message when `users.length === 0`
- Error state: Show message when `error !== null`
- Loading state: Show spinner when `isLoading === true`

**Text Truncation**:
- Usernames longer than ~18 characters: Truncate with ellipsis (`text-overflow: ellipsis`)
- No character limit validation (backend already enforces max 30 chars)

---

## State Transitions

### Tooltip Visibility States

```
┌─────────┐
│ Hidden  │ (initial state)
└─────────┘
     │
     │ Hover card for 500ms
     ↓
┌─────────┐
│ Loading │ (isLoading=true, visible=true)
└─────────┘
     │
     │ API response received
     ↓
┌─────────┐
│ Visible │ (users populated, visible=true)
└─────────┘
     │
     │ Mouse leave for 200ms
     ↓
┌─────────┐
│ Hidden  │ (visible=false, data cleared)
└─────────┘
```

### Error State Transition

```
┌─────────┐
│ Loading │
└─────────┘
     │
     │ API error (network failure, 404, 500, etc.)
     ↓
┌─────────┐
│ Error   │ (error="Error al cargar usuarios", visible=true)
└─────────┘
     │
     │ Mouse leave for 200ms
     ↓
┌─────────┐
│ Hidden  │ (error cleared)
└─────────┘
```

---

## Performance Considerations

### Data Fetching Optimization

**Lazy Loading**:
- Data NOT fetched on dashboard mount (avoids unnecessary API calls)
- Data fetched ONLY when tooltip is triggered by hover (500ms delay)
- Empty state: No API call if user has 0 followers/following (check `stats.followers_count` first)

**Caching** (Future Enhancement - Not in MVP):
- Consider React Query or SWR for 60s cache TTL
- Avoid re-fetch on successive hovers within cache window
- Invalidate cache on follow/unfollow actions

**Memory Management**:
- Tooltip data cleared on component unmount (no memory leaks)
- Event listeners (hover, keydown) cleaned up in useEffect return
- Timeout references cleared to prevent dangling timers

**Pagination**:
- Backend returns up to 50 users (no pagination parameter)
- Frontend slices to 8 users (sufficient for tooltip preview)
- Full list accessed via separate `/users/{username}/followers` page with pagination

---

## Edge Cases

### Empty States

**0 Followers**:
```typescript
// Hook returns
{
  users: [],
  totalCount: 0,
  isLoading: false,
  error: null
}

// Component shows
"No tienes seguidores aún"
```

**0 Following**:
```typescript
{
  users: [],
  totalCount: 0,
  isLoading: false,
  error: null
}

// Component shows
"No sigues a nadie aún"
```

### Partial Data

**Exactly 8 Followers** (no "Ver todos" link):
```typescript
{
  users: [8 users],
  totalCount: 8,
  isLoading: false,
  error: null
}

// Component shows user list WITHOUT "Ver todos" link
// (remaining = 8 - 8 = 0, hasMore = false)
```

**Fewer Than 8 Followers**:
```typescript
{
  users: [3 users],
  totalCount: 3,
  isLoading: false,
  error: null
}

// Component shows all 3 users WITHOUT "Ver todos" link
```

### Error Cases

**Network Failure**:
```typescript
{
  users: [],
  totalCount: 0,
  isLoading: false,
  error: "Error al cargar usuarios"
}

// Component shows error message (red border, error icon - future)
```

**User Not Found (404)**:
```typescript
// Backend returns 404 - unlikely on dashboard (own username)
// Hook catches error, sets error: "Error al cargar usuarios"
```

**Unauthorized (401)**:
```typescript
// Backend returns 401 - user not authenticated
// Dashboard already requires auth, so this shouldn't occur
// Hook catches error, sets error: "Error al cargar usuarios"
```

---

## Migration Notes

**No Database Migration Required**: This feature is frontend-only.

**No Backend Changes Required**: Uses existing endpoints and data structures.

**Frontend Type Additions**:
1. Add `UseFollowersTooltipReturn` interface to `useFollowersTooltip.ts`
2. Add `SocialStatTooltipProps` interface to `SocialStatTooltip.tsx`
3. No changes to existing `follow.ts` types

**Backward Compatibility**: 100% compatible. Existing follow endpoints unchanged.

---

## Testing Considerations

### Unit Test Data

**Mock UserSummaryForFollow**:
```typescript
const mockUser: UserSummaryForFollow = {
  user_id: '123e4567-e89b-12d3-a456-426614174000',
  username: 'maria_garcia',
  profile_photo_url: 'https://example.com/photos/maria.jpg'
};

const mockUserNoPhoto: UserSummaryForFollow = {
  user_id: '123e4567-e89b-12d3-a456-426614174001',
  username: 'juan_perez',
  profile_photo_url: null
};
```

**Mock FollowersListResponse**:
```typescript
const mockFollowersResponse: FollowersListResponse = {
  followers: [mockUser, mockUserNoPhoto, /* ... 6 more */],
  total_count: 12
};
```

### Integration Test Scenarios

1. **Hover trigger**: Hover card for 500ms → API called → tooltip shows 8 users
2. **Empty state**: API returns 0 followers → tooltip shows "No tienes seguidores aún"
3. **Error handling**: API returns 500 → tooltip shows "Error al cargar usuarios"
4. **Navigation**: Click username → navigate to `/users/{username}`
5. **View all**: Click "Ver todos" → navigate to `/users/{username}/followers`
6. **Quick hover**: Hover for <500ms → no API call, no tooltip
7. **Mouse to tooltip**: Move from card to tooltip → tooltip stays visible (200ms delay)

---

**Last Updated**: 2026-02-13
**Related Files**:
- Spec: `specs/019-followers-tooltip/spec.md`
- Plan: `specs/019-followers-tooltip/plan.md`
- Research: `specs/019-followers-tooltip/research.md`
