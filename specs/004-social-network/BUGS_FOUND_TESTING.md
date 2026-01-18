# Bugs Found During Manual Testing - Feature 004

**Testing Date**: 2026-01-18
**Tester**: Claude Code Assistant
**Branch**: `004-social-network`
**Environment**: Local Development (SQLite)

---

## Bug #1: Duplicate Trips in Infinite Scroll Pagination

**Status**: ⚠️ **WORKAROUND APPLIED** (Frontend fix in place, backend fix needed)
**Severity**: Medium
**Found During**: TC-US1-004 (Infinite Scroll Pagination)
**Commit**: c315c67

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

### Files Affected

**Frontend** (✅ Fixed):
- `frontend/src/hooks/useFeed.ts` - Deduplication workaround applied

**Backend** (⚠️ Needs fix):
- `backend/src/services/feed_service.py` - Hybrid algorithm logic
- `backend/tests/integration/test_feed_service.py` - Add pagination duplicate test

### Testing Impact

**Test Result**: TC-US1-004 = ⚠️ **PASS (with workaround)**

- ✅ Infinite scroll loads more trips
- ✅ No visual duplicates shown to user
- ✅ Loading spinner appears correctly
- ⚠️ Backend pagination has bug (workaround applied)

**Next Steps**:
1. Create backend issue to fix hybrid feed algorithm
2. Add integration test for pagination without duplicates
3. Remove frontend workaround after backend fix
4. Re-test TC-US1-004 to verify end-to-end fix

---

## Summary

| Bug ID | Severity | Status | Workaround | Backend Fix Needed |
|--------|----------|--------|------------|-------------------|
| #1 - Duplicate Trips | Medium | ⚠️ Mitigated | ✅ Frontend dedup | ⚠️ Yes - feed_service.py |

**Total Bugs Found**: 1
**Critical Bugs**: 0
**Blocking Bugs**: 0 (workaround in place)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-18
**Maintained by**: Claude Code
