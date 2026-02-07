# Bugs Found During Manual Testing - Feature 004

**Testing Date**: 2026-01-18
**Tester**: Claude Code Assistant
**Branch**: `004-social-network`
**Environment**: Local Development (SQLite)

---

## Bug #1: Duplicate Trips in Infinite Scroll Pagination

**Status**: ✅ **FIXED** (Backend Sequential Algorithm + Frontend workaround removed)
**Severity**: Medium
**Found During**: TC-US1-004 (Infinite Scroll Pagination)
**Found in Commit**: c315c67
**Fixed**: 2026-01-19

### Description

When scrolling through the personalized feed (`/feed`), duplicate trips appear across multiple pages. Specifically, trips that appear in page 1 can also appear in page 2.

### Steps to Reproduce

1. Login as `testuser`
2. Navigate to `/feed` (personalized feed)
3. Scroll to bottom to trigger infinite scroll (page 2 load)
4. Observe React console warning:
   ```
   Warning: Encountered two children with the same key, `<trip_id>`.
   Keys should be unique so that components maintain their identity across updates.
   ```
5. Inspect feed items - same trip appears multiple times

### Root Cause

**Backend Issue**: `backend/src/services/feed_service.py` - Hybrid feed algorithm bug

The personalized feed uses a hybrid algorithm:
1. Show trips from followed users (chronological)
2. Backfill with popular community trips if needed

**Problem**: When transitioning from "followed users" trips to "community backfill" trips across pagination boundaries, the same trip can appear in both segments.

**Example scenario**:
- Page 1: 7 trips from followed users + 3 community backfill trips (total: 10)
- Page 2: 4 trips from followed users + 6 community backfill trips (total: 10)
- **Issue**: One of the "followed user" trips in page 2 was already shown as a "community trip" in page 1

**Code reference**:
[`backend/src/services/feed_service.py:77-96`](../../backend/src/services/feed_service.py#L77-L96)

```python
# Backfill logic only excludes trips from CURRENT page
should_backfill = (
    followed_count == 0
    or (offset == 0 and followed_count < limit)  # Only page 1!
)

if len(followed_trips) < limit and should_backfill:
    # Problem: exclude_trip_ids only contains trips from current page
    followed_trip_ids = {t["trip_id"] for t in followed_trips}

    community_trips, community_count = await FeedService._get_community_trips(
        exclude_trip_ids=followed_trip_ids,  # Should exclude ALL previous pages
    )
```

### Current Workaround (Frontend)

**Temporary fix applied**: `frontend/src/hooks/useFeed.ts`

```typescript
// Deduplicate trips by trip_id during infinite scroll append
const existingIds = new Set(prev.map(t => t.trip_id));
const newTrips = response.trips.filter(t => !existingIds.has(t.trip_id));
return [...prev, ...newTrips];
```

**Impact**:
- ✅ Users no longer see duplicate trips
- ✅ React warnings eliminated
- ⚠️ `total_count` from backend may be inaccurate (counts duplicates)
- ⚠️ Performance: O(n) deduplication on every page load

### Recommended Backend Fix

**Option 1 - Sequential Algorithm** (Simplest):
1. Show ALL trips from followed users first (all pages)
2. AFTER followed users are exhausted, show community backfill
3. Track cumulative `followed_count` across all pages

**Option 2 - Global Exclusion Set** (More complex):
1. Track all `trip_ids` shown in previous pages (session-based)
2. Pass cumulative `exclude_trip_ids` to both `_get_followed_trips()` and `_get_community_trips()`
3. Requires stateful pagination or client-side tracking

**Option 3 - Hybrid with Deterministic Ordering** (Best UX):
1. Assign each trip a "score" (timestamp for followed, popularity for community)
2. Merge both sources with single ORDER BY score
3. Paginate the merged result set
4. No duplicates possible due to deterministic ordering

### Fix Applied ✅

**Date**: 2026-01-19
**Solution**: Option 1 - Sequential Algorithm (simplest and most robust)

**Backend Changes** (`backend/src/services/feed_service.py`):

1. **Refactored `get_personalized_feed()`** (lines 28-124):
   - Implemented Sequential Algorithm:
     - Show ALL trips from followed users first (pages 1...N)
     - When followed trips exhausted, show community backfill (pages N+1...)
   - Added count-only optimization: `_get_followed_trips(limit=0)` to get total count
   - Calculate phase transition point: `offset < followed_count`
   - Handle page boundaries correctly (backfill remaining space on last followed page)

2. **Enhanced `_get_community_trips()`** (lines 249-252, 287):
   - Added query to get `followed_user_ids` from `Follow` table
   - Filter out trips from followed users: `not_(Trip.user_id.in_(followed_user_ids))`
   - Applied filter to both main query and count query
   - Ensures community trips ONLY show unfollowed users

**Frontend Changes** (`frontend/src/hooks/useFeed.ts`):
- **Removed deduplication workaround** (lines 248-258):
  - Changed from: `const newTrips = response.trips.filter(t => !existingIds.has(t.trip_id))`
  - Changed to: `setTrips((prev) => [...prev, ...response.trips])`
  - Simple append now works correctly (no duplicates from backend)

**Testing** (`backend/tests/integration/test_feed_api.py`):
- ✅ Added `test_feed_pagination_no_duplicates` (lines 318-466):
  - Creates testuser following user1 (7 trips)
  - Creates user2 not followed (5 trips)
  - Fetches all 3 pages (limit=5 per page)
  - Verifies NO duplicates: `len(all_trip_ids) == len(unique_trip_ids)`
  - Verifies sequential ordering: followed trips appear before community trips
  - **Result**: Test PASSED ✅

**New Fixture** (`backend/tests/fixtures/feature_013_fixtures.py`):
- Added `current_user` fixture for feed pagination tests (lines 201-227)

### Files Affected

**Backend** (✅ FIXED):
- `backend/src/services/feed_service.py` - Sequential Algorithm implemented
- `backend/tests/integration/test_feed_api.py` - Integration test added
- `backend/tests/fixtures/feature_013_fixtures.py` - New fixture added

**Frontend** (✅ FIXED):
- `frontend/src/hooks/useFeed.ts` - Deduplication workaround removed

### Testing Impact

**Test Result**: TC-US1-004 = ✅ **PASS (Backend fix verified)**

- ✅ Infinite scroll loads more trips (no duplicates)
- ✅ Backend Sequential Algorithm working correctly
- ✅ Integration test passing (12 unique trips across 3 pages)
- ✅ Frontend workaround removed (clean code)
- ✅ Loading spinner appears correctly

---

## Summary

| Bug ID | Severity | Status | Backend Fix | Frontend Fix | Integration Test |
|--------|----------|--------|-------------|--------------|------------------|
| #1 - Duplicate Trips | Medium | ✅ FIXED | ✅ Sequential Algorithm | ✅ Workaround removed | ✅ test_feed_pagination_no_duplicates |

**Total Bugs Found**: 1
**Critical Bugs**: 0
**Blocking Bugs**: 0
**Fixed Bugs**: 1 ✅

---

**Document Version**: 2.0
**Last Updated**: 2026-01-19
**Maintained by**: Claude Code
