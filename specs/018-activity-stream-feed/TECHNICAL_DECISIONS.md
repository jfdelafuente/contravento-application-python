# Technical Decisions - Feature 018: Activity Stream Feed

**Date**: 2026-02-11
**Status**: US1 ✅ Complete, US2 ✅ Complete (with Travel Diary integration)

---

## Decision Log

### Decision 1: Travel Diary Integration Strategy

**Context**: Likes in Activity Feed (Feature 018) needed to appear in Travel Diary (Feature 002/008)

**Options Considered**:
- **Opción A**: Full integration - likes appear in `/trips?user=...`, `/trips/{id}`, `/trips/public`
- **Opción B**: Partial integration - likes only in activity feed
- **Opción C**: Use existing Feature 004 approach

**Decision**: ✅ **Opción A - Full Integration**

**Rationale**:
- Provides best user experience (likes visible everywhere)
- Consistent with existing Feature 004 (Social Network) patterns
- Minimal code duplication (shared `_calculate_likes_for_trips()` helper)

**Implementation**:

**Backend Changes**:
```python
# backend/src/services/trip_service.py
async def _calculate_likes_for_trips(
    self, trips: list[Trip], current_user_id: str | None = None
) -> None:
    """Calculate like_count and is_liked for trips (Feature 018 integration)."""
    # Fetch likes in bulk, group by trip_id, calculate counts
```

- Modified: `get_user_trips()`, `get_public_trips()`, `get_trip_by_id()`
- All methods now call `_calculate_likes_for_trips()` before returning

**Frontend Changes**:
```typescript
// frontend/src/types/trip.ts
export interface TripListItem {
  // ... existing fields
  like_count?: number;
  is_liked?: boolean | null;
}

// frontend/src/components/trips/TripCard.tsx
{trip.like_count !== undefined && trip.like_count > 0 && (
  <div className="trip-card__like-count">
    <svg>...</svg>
    <span>{trip.like_count}</span>
  </div>
)}
```

**Outcome**: ✅ Likes now visible in all Travel Diary views

---

### Decision 2: Trip Title Synchronization in Activity Feed

**Problem**: When users edit trip titles, the updated title doesn't appear in activity feed

**Root Cause**: Activity feed stores `trip_title` in `activity_metadata` JSON field at creation time

**Options Considered**:

1. **Update metadata on every trip edit**
   - Pros: Simple to implement
   - Cons: Only works for new edits, old activities show stale titles

2. **Enrich metadata at response time from Trip table**
   - Pros: Always shows current title, works for all trips (old and new)
   - Cons: Extra database queries

3. **Store trip_id and fetch title on frontend**
   - Pros: Always fresh data
   - Cons: N+1 query problem, slower UX

**Decision**: ✅ **Option 2 - Enrich at response time**

**Implementation**:

```python
# backend/src/services/feed_service.py (lines 622-642)

# Collect trip IDs for TRIP_PUBLISHED activities
trip_ids_to_enrich = []
for activity_item, _ in activities_data:
    if activity_type == "TRIP_PUBLISHED" and activity_item.related_id:
        trip_ids_to_enrich.append(activity_item.related_id)

# Fetch trips in bulk (1 query for all trips)
trips_query = select(Trip).where(Trip.trip_id.in_(trip_ids_to_enrich))
trips_result = await db.execute(trips_query)
trips = trips_result.scalars().all()
trips_by_id = {trip.trip_id: trip for trip in trips}

# Enrich metadata with current trip title
trip = trips_by_id.get(activity_item.related_id)
if trip:
    metadata["trip_title"] = trip.title
    if trip.distance_km is not None:
        metadata["trip_distance_km"] = trip.distance_km
```

**Outcome**: ✅ Trip titles always current in feed, works for all trips

**Performance**: Single bulk query per feed page (O(1) instead of O(n))

---

### Decision 3: Like Persistence Bug Fix Strategy

**Problem**: Likes in activity feed don't persist after page refresh

**Root Cause**: `feed_service.py` had hardcoded values:
```python
# ❌ WRONG (before fix)
likes_count = 0
is_liked_by_me = False
```

**Options Considered**:

1. **Subquery in main feed query**
   - Pros: Single query
   - Cons: Complex SQL, harder to maintain

2. **Eager loading with SQLAlchemy relationships**
   - Pros: Simple, leverages ORM, easy to debug
   - Cons: Two queries (feed + likes)

**Decision**: ✅ **Option 2 - SQLAlchemy eager loading**

**Implementation**:

```python
# backend/src/services/feed_service.py (line 587)
activities_query = (
    select(ActivityFeedItem, User)
    .join(User, ActivityFeedItem.user_id == User.id)
    .options(selectinload(ActivityFeedItem.likes))  # ✅ Eager load likes
    .where(ActivityFeedItem.user_id.in_(followed_user_ids))
    .order_by(desc(ActivityFeedItem.created_at))
    .limit(limit + 1)
)

# Calculate likes_count and is_liked_by_me (lines 626-630)
likes_count = len(activity_item.likes)  # ✅ From loaded relationship
is_liked_by_me = any(
    like.user_id == current_user_id for like in activity_item.likes
)
```

**Outcome**: ✅ Likes persist correctly, no extra queries

**Performance**: `selectinload` = 1 additional query for all activities (efficient)

---

### Decision 4: Cross-Tab Synchronization Approach

**Problem**: Likes in one browser tab don't update other tabs immediately

**Goal**: When user likes activity in Tab 1, Tab 2 should update automatically

**Options Considered**:

1. **CustomEvent API (same-tab only)**
   - Pros: Simple, native browser API
   - Cons: Only works within same tab

2. **BroadcastChannel API (cross-tab)**
   - Pros: Native browser API, no server needed, works across tabs
   - Cons: Not supported in older browsers (IE, Safari <15.4)

3. **WebSocket / Server-Sent Events (SSE)**
   - Pros: Real-time, works everywhere
   - Cons: Complex, requires backend infrastructure

4. **LocalStorage events**
   - Pros: Works cross-tab
   - Cons: Hacky, race conditions, storage limits

**Decision**: ✅ **Attempted Option 2 (BroadcastChannel), then ⛔ ABANDONED**

**Implementation Attempted**:

```typescript
// frontend/src/utils/likeEvents.ts

// Initialize BroadcastChannel
let broadcastChannel: BroadcastChannel | null = null;
if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
  broadcastChannel = new BroadcastChannel('contravento-likes');
}

export function emitLikeChanged(detail: LikeChangedEvent): void {
  // Emit to other tabs via BroadcastChannel
  if (broadcastChannel) {
    broadcastChannel.postMessage(detail);
  }

  // Also emit locally via CustomEvent (same-tab)
  window.dispatchEvent(new CustomEvent('likeChanged', { detail }));
}

export function subscribeLikeChanged(callback: (event: LikeChangedEvent) => void) {
  // Handler for BroadcastChannel (cross-tab)
  const broadcastHandler = (event: MessageEvent<LikeChangedEvent>) => {
    callback(event.data);
  };

  if (broadcastChannel) {
    broadcastChannel.addEventListener('message', broadcastHandler);
  }

  // Handler for CustomEvent (same-tab)
  window.addEventListener('likeChanged', customEventHandler);

  return cleanup;
}
```

**Testing Results**:
- ✅ Same-tab synchronization works correctly
- ❌ Cross-tab synchronization does NOT work
  - Console logs show BroadcastChannel initialized
  - `postMessage()` succeeds without errors
  - Other tabs never receive messages (no console logs)

**User Feedback**: "no conseguimos solventar este problema"

**Final Decision**: ⛔ **ABANDON cross-tab synchronization**

**Rationale**:
1. Same-tab sync works correctly (most common use case)
2. Cross-tab sync debugging would take significant time
3. Feature 004 has simpler approach that works
4. Can revisit with WebSocket/SSE in future iteration

**Outcome**:
- ✅ Same-tab synchronization working
- ⛔ Cross-tab synchronization deferred to future
- Code remains in place for potential future fixes

**Alternative**: Use simpler Feature 004 approach (manual refresh in other tabs)

---

### Decision 5: Event Listener Stability with useRef

**Problem**: Event listeners in `useTripList.ts` constantly unsubscribe/re-subscribe

**Root Cause**: `fetchTrips` function reference changes on every render, causing `useEffect` to re-run

**Console Logs**:
```
[likeEvents] Subscribing to likeChanged events
[likeEvents] Unsubscribing from likeChanged events  // ❌ Immediately after!
[likeEvents] Subscribing to likeChanged events
[likeEvents] Unsubscribing from likeChanged events
... (repeats constantly)
```

**Decision**: ✅ **Use useRef to maintain stable function reference**

**Implementation**:

```typescript
// frontend/src/hooks/useTripList.ts

// Fetch trips function (changes on every render due to dependencies)
const fetchTrips = useCallback(async () => {
  // ... fetch logic
}, [username, searchQuery, selectedTag, /* many dependencies */]);

// ❌ WRONG: Direct usage causes re-subscribe on every render
useEffect(() => {
  const unsubscribe = subscribeLikeChanged((event) => {
    fetchTrips();  // ❌ Reference changes every render
  });
  return unsubscribe;
}, [fetchTrips]);  // ❌ fetchTrips changes = re-subscribe

// ✅ CORRECT: Use ref for stable reference (lines 165-181)
const fetchTripsRef = useRef(fetchTrips);
useEffect(() => {
  fetchTripsRef.current = fetchTrips;
}, [fetchTrips]);

useEffect(() => {
  const unsubscribe = subscribeLikeChanged((event) => {
    fetchTripsRef.current();  // ✅ Stable reference
  });
  return unsubscribe;
}, [username]);  // ✅ Only re-subscribe when username changes
```

**Outcome**: ✅ Event listener stable, no thrashing

**Performance**: Reduces event listener churn from hundreds per minute to zero

---

## Implementation Summary

### ✅ Completed Features

1. **Activity Feed Display (US1)**
   - Chronological feed from followed users
   - Cursor-based pagination with infinite scroll
   - Route: `/activities`

2. **Like Functionality (US2)**
   - Like/unlike with optimistic updates
   - Persistence after page refresh
   - Integration with Travel Diary (Feature 002/008)

3. **Travel Diary Integration**
   - Like badges in TripCard component
   - Like counts in `/trips?user=...`, `/trips/{id}`, `/trips/public`
   - Trip owners see read-only count (no self-like)

4. **Event Synchronization**
   - Same-tab synchronization working
   - Custom event system with `likeEvents.ts`
   - TanStack Query cache invalidation

### ⛔ Deferred Features

1. **Cross-Tab Synchronization**
   - BroadcastChannel attempted but not working
   - Deferred to future iteration (WebSocket/SSE)
   - User decision: Use simpler Feature 004 approach

2. **Notifications for Likes**
   - Backend: Notification model needs extension for activity_id
   - Currently disabled in `ActivityLikeService.like_activity()`

3. **Comments (US3)**
   - Not started

4. **Achievements in Feed (US4)**
   - Not started

5. **Feed Filters (US5)**
   - Not started

---

## Key Learnings

1. **Metadata Enrichment**: Always enrich from source tables at response time, not from stored JSON
2. **SQLAlchemy Eager Loading**: `selectinload()` is efficient for 1-to-many relationships
3. **React useRef**: Use for stable function references in event listeners
4. **BroadcastChannel**: Native API exists but may have reliability issues (needs deeper investigation)
5. **Travel Diary Integration**: Small helper methods (`_calculate_likes_for_trips()`) better than duplicating logic

---

## Future Considerations

### Cross-Tab Synchronization Options

If revisiting cross-tab sync in future:

1. **WebSocket with Socket.io**
   - Pros: Reliable, bi-directional, works everywhere
   - Cons: Backend infrastructure, connection overhead

2. **Server-Sent Events (SSE)**
   - Pros: Simpler than WebSocket, one-way push
   - Cons: Still requires backend endpoint

3. **Polling with TanStack Query**
   - Pros: Simple, built-in to React Query (`refetchInterval`)
   - Cons: Not real-time, unnecessary requests

4. **Debug BroadcastChannel further**
   - Check browser compatibility (Safari <15.4)
   - Test with different origins (localhost vs production)
   - Add error handling for `postMessage()` failures

**Recommendation**: Start with WebSocket (Socket.io) in future iteration for production reliability

---

## References

- Spec: [spec.md](spec.md)
- Tasks: [tasks.md](tasks.md)
- Manual Testing: [MANUAL_TESTING_FEED.md](MANUAL_TESTING_FEED.md), [MANUAL_TESTING_LIKES.md](MANUAL_TESTING_LIKES.md)
- Data Model: [data-model.md](data-model.md)
- API Contracts: [contracts/](contracts/)

**Last Updated**: 2026-02-11
