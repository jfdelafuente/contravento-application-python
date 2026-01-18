# Manual Testing Guide - User Stories 1 & 2

**Feature**: 004 Social Network
**User Stories**: US1 (Feed Personalizado) + US2 (Likes/Me Gusta)
**Date**: 2026-01-17
**Branch**: `004-social-network`
**Status**: Ready for Manual Testing

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Test Environment Setup](#test-environment-setup)
3. [US1: Feed Personalizado - Test Cases](#us1-feed-personalizado)
4. [US2: Likes/Me Gusta - Test Cases](#us2-likes-me-gusta)
5. [Integration Tests (US1 + US2)](#integration-tests)
6. [Performance Validation](#performance-validation)
7. [Accessibility Testing](#accessibility-testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Test Data

Before starting manual tests, ensure you have:

1. **Multiple users** (minimum 3):
   - User A (trip owner)
   - User B (follower)
   - User C (non-follower)

2. **Published trips** (minimum 10):
   - User A has 5+ published trips
   - User B has 3+ published trips
   - User C has 2+ published trips

3. **Follow relationships**:
   - User B follows User A
   - User C does NOT follow anyone

### Creating Test Data

```bash
cd backend

# Create test users (if not already created during setup)
poetry run python scripts/create_verified_user.py --username user_a --email usera@test.com --password "Test123!"
poetry run python scripts/create_verified_user.py --username user_b --email userb@test.com --password "Test123!"
poetry run python scripts/create_verified_user.py --username user_c --email userc@test.com --password "Test123!"

# Seed trips (creates multiple trips for testing)
poetry run python scripts/seed_trips.py
```

---

## Test Environment Setup

### 1. Start Backend Server

**Option A - PowerShell** (Windows):
```powershell
cd "c:\My Program Files\workspace-claude\contravento-application-python"
.\run_backend.ps1 start
```

**Option B - Bash** (Linux/Mac):
```bash
cd /path/to/contravento-application-python
./run_backend.sh start
```

**Verify**:
- Backend running at: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2. Start Frontend Server

**PowerShell**:
```powershell
.\run_frontend.ps1 start
```

**Bash**:
```bash
./run_frontend.sh start
```

**Verify**:
- Frontend running at: http://localhost:5173

### 3. Database Verification

Check that social network tables exist:

```bash
cd backend
poetry run python -c "
import sqlite3
conn = sqlite3.connect('contravento_dev.db')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('likes', 'comments', 'shares', 'notifications') ORDER BY name\")
print('Social tables:', [row[0] for row in cursor.fetchall()])
"
```

**Expected output**: `['comments', 'likes', 'notifications', 'shares']`

---

## US1: Feed Personalizado

### TC-US1-001: Access Feed (Authenticated User)

**Objective**: Verify authenticated users can access the feed

**Steps**:
1. Open browser: http://localhost:5173
2. Log in with User B credentials:
   - Username: `user_b`
   - Password: `Test123!`
3. Navigate to **Feed** (click "Feed" in navigation menu or go to `/feed`)

**Expected Results**:
- ✅ Feed page loads successfully
- ✅ URL is `/feed`
- ✅ Navigation highlights "Feed" menu item
- ✅ Feed shows trips (hybrid algorithm: followed users + popular)

**Success Criteria**: **SC-001** - Feed loads in **<1 second** (measured with browser DevTools Network tab)

---

### TC-US1-002: Feed Content (Followed Users)

**Objective**: Verify feed shows trips from followed users

**Precondition**: User B follows User A

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Scroll through feed items

**Expected Results**:
- ✅ Feed shows trips from User A (followed user)
- ✅ Trips are in **chronological order** (newest first)
- ✅ Each trip card displays:
  - Trip title
  - Author username + profile photo
  - Trip dates (formatted in Spanish: "1 de junio de 2024")
  - Distance (e.g., "150 km")
  - First trip photo (if available)
  - Trip locations (if available)
  - Like counter (e.g., "5 likes")

---

### TC-US1-003: Feed Content (Popular Backfill)

**Objective**: Verify feed backfills with popular trips when followed users have no content

**Precondition**: User C follows NOBODY

**Steps**:
1. Log in as User C
2. Navigate to `/feed`

**Expected Results**:
- ✅ Feed shows popular trips from the community
- ✅ Trips are ordered by popularity (likes + comments + shares DESC)
- ✅ User C's own trips are **NOT** shown in feed
- ✅ Only **published** trips are shown (no drafts)

---

### TC-US1-004: Infinite Scroll Pagination

**Objective**: Verify infinite scroll loads next pages seamlessly

**Precondition**: Database has 15+ published trips

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Scroll to bottom of page (10 trips loaded)
4. Continue scrolling past the 10th trip
5. Observe loading skeleton
6. Wait for next page to load

**Expected Results**:
- ✅ First 10 trips load immediately
- ✅ Skeleton loader appears when scrolling to bottom
- ✅ Next 10 trips load automatically
- ✅ No page refresh or manual "Load More" button needed
- ✅ Scroll position maintains (no jump)

**Success Criteria**: **SC-002** - Next page loads in **<500ms** (DevTools Network tab)

---

### TC-US1-005: Feed Skeleton Loading State

**Objective**: Verify skeleton loaders during initial load

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Observe initial loading state (may need slow network throttling in DevTools)

**Expected Results**:
- ✅ Skeleton placeholders shown while loading
- ✅ Skeletons match feed card layout (image, title, metadata)
- ✅ No "white flash" or empty state
- ✅ Smooth transition from skeleton → real content

---

### TC-US1-006: Feed - Unauthorized Access

**Objective**: Verify unauthenticated users cannot access feed

**Steps**:
1. Log out (or use incognito window)
2. Try to navigate to `/feed`

**Expected Results**:
- ✅ Redirect to `/login` page
- ✅ Toast message: "Debes iniciar sesión para ver el feed"
- ✅ After login, redirect back to `/feed`

---

### TC-US1-007: Feed - Empty State

**Objective**: Verify empty state when no trips exist

**Precondition**: Database has NO published trips, or user follows nobody and no popular trips exist

**Steps**:
1. Log in as User C (follows nobody)
2. Navigate to `/feed`

**Expected Results**:
- ✅ Empty state message displayed
- ✅ Message suggests following users or creating trips
- ✅ No error or loading spinner stuck

---

### TC-US1-008: Feed - Trip Card Click

**Objective**: Verify clicking a trip card navigates to trip detail

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Click on any trip card

**Expected Results**:
- ✅ Navigates to `/trips/{trip_id}` (TripDetailPage)
- ✅ Trip detail page loads with full trip information

---

### TC-US1-009: Follow Button Display

**Objective**: Verify FollowButton appears correctly in trip cards

**Precondition**: User B is viewing feed with trips from users they don't follow

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Observe trip cards from other users

**Expected Results**:
- ✅ FollowButton appears next to author name on each trip card
- ✅ Button shows "Seguir" text with User Plus icon
- ✅ Button is small size with secondary variant (outline style)
- ✅ Button does NOT appear on own trips (if any)

---

### TC-US1-010: Follow User from Feed

**Objective**: Verify user can follow another user from trip card

**Precondition**:
- User B is NOT following User A
- User A has published trips in feed

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Find a trip card from User A
4. Click "Seguir" button next to User A's name

**Expected Results**:
- ✅ Button immediately changes to "Siguiendo" with User Check icon (optimistic UI)
- ✅ Button style changes from filled to outline
- ✅ Brief loading spinner appears
- ✅ No page refresh or navigation
- ✅ Button remains in "Siguiendo" state after API completes
- ✅ If page is refreshed, button still shows "Siguiendo"

---

### TC-US1-011: Unfollow User from Feed

**Objective**: Verify user can unfollow a user from trip card

**Precondition**: User B is already following User A

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Find a trip card from User A
4. Observe "Siguiendo" button next to User A's name
5. Click "Siguiendo" button

**Expected Results**:
- ✅ Button immediately changes to "Seguir" with User Plus icon (optimistic UI)
- ✅ Button style changes from outline to filled
- ✅ Brief loading spinner appears
- ✅ Button remains in "Seguir" state after API completes
- ✅ If page is refreshed, button still shows "Seguir"

---

### TC-US1-012: Follow Button - Optimistic UI

**Objective**: Verify optimistic UI updates (instant feedback)

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. **Throttle network** in DevTools (Slow 3G)
4. Click "Seguir" button on a user

**Expected Results**:
- ✅ Button changes to "Siguiendo" **immediately** (before API response)
- ✅ Loading spinner appears
- ✅ If API succeeds → changes persist
- ✅ If API fails → reverts to "Seguir" state + error toast

---

### TC-US1-013: Follow Button - Error Rollback

**Objective**: Verify UI rollback on API error

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. **Stop backend server** (simulate network failure)
4. Click "Seguir" button

**Expected Results**:
- ✅ Button changes to "Siguiendo" immediately (optimistic)
- ✅ After ~10s timeout: button reverts to "Seguir"
- ✅ Error toast: "Error al procesar la acción. Intenta de nuevo."

---

### TC-US1-014: Feed Updates After Follow

**Objective**: Verify feed content updates after following a user

**Setup**:
1. Create User A with 3 published trips
2. Create User B who follows nobody
3. User B's feed shows popular community trips (not User A's trips)

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Verify User A's trips are NOT in feed (User B follows nobody)
4. Navigate to User A's profile or find a trip by User A
5. Click "Seguir" button for User A
6. Navigate back to `/feed` and refresh

**Expected Results**:
- ✅ Feed now shows User A's 3 trips at the top (chronological order)
- ✅ Feed algorithm prioritizes followed users over popular backfill
- ✅ Previous popular trips are pushed down or removed from first page

**Note**: This test validates FR-002 (feed from followed users) + integration with Follow functionality

---

### TC-US1-015: Follow Button - Prevent Self-Follow

**Objective**: Verify users cannot follow themselves

**Steps**:
1. Log in as User A
2. Navigate to `/feed`
3. Observe own trips (if any)

**Expected Results**:
- ✅ FollowButton is **hidden** on own trips
- ✅ No "Seguir" or "Siguiendo" button appears next to own username
- ✅ Other users' trips still show FollowButton normally

**Note**: Backend also prevents self-follow (API validation), but frontend hides button proactively

---

### TC-US1-016: Follow Button - Loading State

**Objective**: Verify loading state prevents double-clicks

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Throttle network (Slow 3G)
4. Click "Seguir" button
5. While loading, try clicking button again multiple times

**Expected Results**:
- ✅ Button shows loading spinner
- ✅ Button is **disabled** during loading (cursor: not-allowed)
- ✅ Multiple clicks do NOT trigger multiple API calls
- ✅ Only ONE follow action is executed

---

### TC-US1-017: Follow Button - Accessibility

**Objective**: Verify keyboard navigation and screen reader support

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Use **Tab** key to navigate to FollowButton
4. Press **Enter** or **Space** to activate button
5. Use screen reader (NVDA/VoiceOver) to read button

**Expected Results**:
- ✅ FollowButton is focusable with Tab key
- ✅ Focus indicator visible (outline)
- ✅ Enter/Space keys activate button (same as click)
- ✅ Screen reader announces:
  - "Seguir, botón" (when not following)
  - "Siguiendo, botón presionado" (when following)
- ✅ aria-label updates dynamically: "Seguir" / "Dejar de seguir"
- ✅ aria-pressed attribute: false / true

---

## US2: Likes/Me Gusta

### TC-US2-001: Like a Trip (First Time)

**Objective**: Verify user can like a trip

**Precondition**: User B has NOT liked Trip A

**Steps**:
1. Log in as User B
2. Navigate to `/feed` or `/trips/{trip_id}`
3. Locate a trip (Trip A) with the like button
4. Click the **heart icon** (outline state)

**Expected Results**:
- ✅ Heart icon changes to **filled/red** immediately (optimistic update)
- ✅ Like counter increments by 1 (e.g., 5 → 6)
- ✅ Button shows brief loading spinner
- ✅ Toast notification: NO notification (silent success)
- ✅ After refresh, like persists (heart still filled)

**Success Criteria**: **SC-006** - Like request completes in **<200ms** (Network tab)

---

### TC-US2-002: Unlike a Trip

**Objective**: Verify user can unlike a trip

**Precondition**: User B has already liked Trip A

**Steps**:
1. Log in as User B
2. Navigate to Trip A (with filled heart icon)
3. Click the **heart icon** (filled state)

**Expected Results**:
- ✅ Heart icon changes to **outline** immediately
- ✅ Like counter decrements by 1 (e.g., 6 → 5)
- ✅ Button shows brief loading spinner
- ✅ After refresh, unlike persists (heart is outline)

**Success Criteria**: **SC-007** - Unlike request completes in **<100ms**

---

### TC-US2-003: Like Button - Optimistic UI

**Objective**: Verify optimistic UI updates (instant feedback)

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. **Throttle network** in DevTools (Slow 3G)
4. Click like button on a trip

**Expected Results**:
- ✅ Heart icon fills **immediately** (before API response)
- ✅ Counter increments **immediately**
- ✅ Loading spinner appears
- ✅ If API succeeds → changes persist
- ✅ If API fails → reverts to previous state + error toast

---

### TC-US2-004: Like Button - Error Rollback

**Objective**: Verify UI rollback on API error

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. **Stop backend server** (simulate network failure)
4. Click like button

**Expected Results**:
- ✅ Heart fills immediately (optimistic)
- ✅ After ~10s timeout: heart reverts to outline
- ✅ Counter reverts to original value
- ✅ Error toast: "Error al procesar la acción. Intenta de nuevo."

---

### TC-US2-005: Prevent Self-Like (Frontend)

**Objective**: Verify users cannot like their own trips

**Precondition**: User A owns Trip A

**Steps**:
1. Log in as User A (trip owner)
2. Navigate to own trip `/trips/{trip_id}`
3. Observe like button

**Expected Results**:
- ✅ Like button is **hidden** or **disabled**
- ✅ No heart icon shown on own trips
- ✅ Like counter still visible (shows other users' likes)

**Note**: Backend prevents self-likes (FR-011), frontend should hide button proactively.

---

### TC-US2-006: Prevent Duplicate Like (Backend)

**Objective**: Verify backend prevents duplicate likes

**Precondition**: User B has already liked Trip A

**Steps**:
1. Log in as User B
2. Open browser DevTools → Console
3. Manually call API:
   ```javascript
   fetch('http://localhost:8000/trips/{trip_id}/like', {
     method: 'POST',
     headers: {
       'Authorization': 'Bearer ' + localStorage.getItem('access_token')
     }
   }).then(r => r.json()).then(console.log)
   ```

**Expected Results**:
- ✅ API returns **400 Bad Request**
- ✅ Error message: "Ya has dado like a este viaje"
- ✅ UI does not update (duplicate prevented)

---

### TC-US2-007: Like Button - Loading State

**Objective**: Verify loading state disables button during API call

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Click like button rapidly (multiple times)

**Expected Results**:
- ✅ Button becomes **disabled** after first click
- ✅ Loading spinner appears
- ✅ Subsequent clicks are **ignored** (no double requests)
- ✅ Button re-enables after API response

---

### TC-US2-008: Get Trip Likes List

**Objective**: Verify viewing users who liked a trip

**Precondition**: Trip A has 5+ likes from different users

**Steps**:
1. Navigate to `/trips/{trip_id}` (no auth required for this)
2. Scroll to "Likes" section (if implemented)
3. Click "Ver quién dio like" (if modal/list exists)

**Expected Results**:
- ✅ List shows users who liked the trip
- ✅ Each user shows: username + profile photo
- ✅ List is ordered by like timestamp (most recent first)
- ✅ Pagination works if >20 likes

**Success Criteria**: **SC-008** - List loads in **<300ms** with 50 likes

**Note**: This UI may not be implemented yet. Backend endpoint `/trips/{trip_id}/likes` is ready.

---

### TC-US2-009: Like Counter Accuracy

**Objective**: Verify like counter matches actual likes

**Steps**:
1. Note like counter on Trip A (e.g., 5 likes)
2. Open API docs: http://localhost:8000/docs
3. Execute `GET /trips/{trip_id}/likes`
4. Count likes in response

**Expected Results**:
- ✅ Counter on UI matches `total_count` from API
- ✅ Counter updates in real-time when likes change

---

### TC-US2-010: Like Button - Accessibility

**Objective**: Verify like button is keyboard accessible

**Steps**:
1. Navigate to `/feed`
2. Use **Tab key** to focus like button
3. Press **Enter** or **Space** to toggle like

**Expected Results**:
- ✅ Like button receives focus (visible outline)
- ✅ ARIA label: "Dar like" (outline) or "Quitar like" (filled)
- ✅ `aria-pressed` attribute: `false` (outline) or `true` (filled)
- ✅ Keyboard triggers like/unlike action
- ✅ Screen reader announces state change

---

## Integration Tests (US1 + US2)

### TC-INT-001: Like from Feed

**Objective**: Verify liking trips directly from feed

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Locate a trip in feed (Trip A)
4. Click like button on feed card
5. Refresh page

**Expected Results**:
- ✅ Like persists on feed card after refresh
- ✅ Like counter matches
- ✅ Clicking trip → detail page also shows like

---

### TC-INT-002: Like Affects Feed Ordering

**Objective**: Verify liked trips affect popularity in community feed

**Precondition**: User C follows nobody (sees popular feed)

**Steps**:
1. Log in as User B
2. Like Trip A multiple times (from different users)
3. Log out, log in as User C
4. Navigate to `/feed`

**Expected Results**:
- ✅ Trip A appears higher in feed (popular backfill uses like count)
- ✅ Feed re-orders based on likes + comments + shares

---

### TC-INT-003: Feed Updates After Like

**Objective**: Verify feed shows updated like count without refresh

**Steps**:
1. Log in as User B
2. Navigate to `/feed`
3. Like a trip (Trip A) from feed
4. Do NOT refresh page
5. Scroll away and scroll back to Trip A

**Expected Results**:
- ✅ Like counter still shows updated value (no stale data)
- ✅ Heart icon still filled

---

## Performance Validation

### PV-001: Feed Load Time (SC-001)

**Objective**: Verify feed loads in <1 second

**Tools**: Chrome DevTools → Network tab

**Steps**:
1. Open DevTools (F12) → Network tab
2. Check "Disable cache"
3. Log in as User B
4. Navigate to `/feed`
5. Measure time from request to DOMContentLoaded

**Expected Results**:
- ✅ **Total load time <1000ms** (SC-001)
- ✅ API request `/feed?page=1&limit=10` completes in <500ms
- ✅ First contentful paint (FCP) <800ms

**Pass Criteria**:
- p95 load time <1s (test 10 times, 95th percentile <1s)

---

### PV-002: Infinite Scroll Pagination (SC-002)

**Objective**: Verify pagination loads in <500ms

**Steps**:
1. Open DevTools → Network tab
2. Navigate to `/feed`
3. Scroll to bottom (trigger pagination)
4. Measure API request `/feed?page=2&limit=10`

**Expected Results**:
- ✅ **API response time <500ms** (SC-002)
- ✅ No UI freeze during load
- ✅ Smooth scroll (no jank)

---

### PV-003: Like Request Performance (SC-006)

**Objective**: Verify like API completes in <200ms

**Steps**:
1. Open DevTools → Network tab
2. Click like button
3. Find `POST /trips/{trip_id}/like` request
4. Check response time

**Expected Results**:
- ✅ **Request completes in <200ms** (SC-006)
- ✅ p95 latency <200ms (test 10 likes)

---

### PV-004: Unlike Request Performance (SC-007)

**Objective**: Verify unlike API completes in <100ms

**Steps**:
1. Open DevTools → Network tab
2. Click unlike button
3. Find `DELETE /trips/{trip_id}/like` request

**Expected Results**:
- ✅ **Request completes in <100ms** (SC-007)
- ✅ p95 latency <100ms

---

## Accessibility Testing

### A11Y-001: Keyboard Navigation

**Steps**:
1. Navigate to `/feed`
2. Use **Tab** to navigate between elements
3. Use **Enter**/**Space** to activate buttons

**Expected Results**:
- ✅ All interactive elements focusable (like button, trip cards)
- ✅ Focus indicator visible (outline)
- ✅ Logical tab order (top to bottom)

---

### A11Y-002: Screen Reader Support

**Tools**: NVDA (Windows), VoiceOver (Mac), JAWS

**Steps**:
1. Enable screen reader
2. Navigate to `/feed`
3. Navigate through feed items

**Expected Results**:
- ✅ Feed items announced as "Trip card: {title}"
- ✅ Like button announces state: "Like button, not pressed" or "pressed"
- ✅ Like counter announced: "5 likes"
- ✅ ARIA live regions announce updates

---

### A11Y-003: Color Contrast

**Tools**: Chrome DevTools → Lighthouse → Accessibility

**Steps**:
1. Open DevTools → Lighthouse
2. Run accessibility audit on `/feed`

**Expected Results**:
- ✅ Color contrast ratio ≥4.5:1 (WCAG AA)
- ✅ Like button text readable against background
- ✅ No accessibility violations

---

## Troubleshooting

### Issue: Feed returns 401 Unauthorized

**Cause**: Missing or expired access token

**Solution**:
1. Check localStorage: `localStorage.getItem('access_token')`
2. If null → log in again
3. If expired → refresh token via `/auth/refresh`

---

### Issue: Feed shows empty (no trips)

**Cause**: No published trips in database

**Solution**:
```bash
cd backend
poetry run python scripts/seed_trips.py
```

---

### Issue: Like button doesn't respond

**Cause**: Backend not running or CORS error

**Solution**:
1. Check backend: http://localhost:8000/health
2. Check browser console for CORS errors
3. Verify `.env` has `CORS_ORIGINS=http://localhost:5173`

---

### Issue: Infinite scroll doesn't trigger

**Cause**: Not enough trips (need >10)

**Solution**:
- Seed more trips: `poetry run python scripts/seed_trips.py`
- Lower `limit` parameter in feed API call (for testing)

---

### Issue: Optimistic UI doesn't rollback on error

**Cause**: Error handling not catching network errors

**Solution**:
- Check browser console for errors
- Verify `useLike` hook has try/catch block

---

## Testing Checklist

### US1: Feed Personalizado

**Core Feed Tests**:

- [x] TC-US1-001: Access Feed (Authenticated) ✅ Passed (2026-01-18)
- [ ] TC-US1-002: Feed Content (Followed Users) 🆕 DESBLOQUEADO - Follow UI implementada
- [x] TC-US1-003: Feed Content (Popular Backfill) ✅ Passed (2026-01-18)
- [x] TC-US1-004: Infinite Scroll Pagination ⚠️ Passed with Bug Found (2026-01-18) - Backend duplicate trips issue, frontend workaround applied (see BUGS_FOUND_TESTING.md)
- [ ] TC-US1-005: Skeleton Loading State
- [x] TC-US1-006: Unauthorized Access ✅ Passed (2026-01-18)
- [x] TC-US1-007: Empty State ✅ Passed (2026-01-18)
- [x] TC-US1-008: Trip Card Click ✅ Passed (2026-01-18)

**Follow/Unfollow Tests** (NEW - Feature 004 Follow UI):

- [x] TC-US1-009: Follow Button Display ✅ Passed (2026-01-18) - Button displays correctly in both feeds with appropriate size
- [x] TC-US1-010: Follow User from Feed ✅ Passed (2026-01-18) - Optimistic UI + auto-refetch working perfectly
- [x] TC-US1-011: Unfollow User from Feed ✅ Passed (2026-01-18) - State persists correctly across page reloads
- [x] TC-US1-012: Follow Button - Optimistic UI ✅ Passed (2026-01-18) - Instant state change before API response
- [ ] TC-US1-013: Follow Button - Error Rollback ⚠️ Not tested (requires network failure simulation)
- [x] TC-US1-014: Feed Updates After Follow ✅ Passed (2026-01-18) - Auto-refetch updates all buttons (~500ms delay)
- [x] TC-US1-015: Follow Button - Prevent Self-Follow ✅ Passed (2026-01-18) - Button hidden on own trips (verified in PublicFeedPage)
- [x] TC-US1-016: Follow Button - Loading State ✅ Passed (2026-01-18) - Button disabled during API call, prevents double-clicks
- [ ] TC-US1-017: Follow Button - Accessibility ⚠️ Partially tested (keyboard navigation works, screen reader not tested)

### US2: Likes/Me Gusta

- [x] TC-US2-001: Like a Trip ✅ Passed (2026-01-18)
- [x] TC-US2-002: Unlike a Trip ✅ Passed (2026-01-18)
- [x] TC-US2-003: Optimistic UI ✅ Passed (2026-01-18)
- [x] TC-US2-004: Error Rollback ✅ Passed (2026-01-18)
- [x] TC-US2-005: Prevent Self-Like ✅ Passed (2026-01-18)
- [ ] TC-US2-006: Prevent Duplicate Like
- [x] TC-US2-007: Loading State ✅ Passed (2026-01-18)
- [ ] TC-US2-008: Get Likes List (⚠️ UI not implemented)
- [x] TC-US2-009: Counter Accuracy ✅ Passed (2026-01-18)
- [x] TC-US2-010: Accessibility ✅ Passed (2026-01-18)

### Integration Tests

- [x] TC-INT-001: Like from Feed ✅ Passed (2026-01-18)
- [x] TC-INT-002: Like Affects Feed Ordering ✅ Passed (2026-01-18)
- [x] TC-INT-003: Feed Updates After Like ✅ Passed (2026-01-18)

### Performance Validation

- [ ] PV-001: Feed Load <1s (SC-001)
- [ ] PV-002: Pagination <500ms (SC-002)
- [ ] PV-003: Like <200ms (SC-006)
- [ ] PV-004: Unlike <100ms (SC-007)

### Accessibility

- [ ] A11Y-001: Keyboard Navigation
- [ ] A11Y-002: Screen Reader Support
- [ ] A11Y-003: Color Contrast

---

## Success Criteria Summary

| ID | Criterion | Target | Status |
|----|-----------|--------|--------|
| **SC-001** | Feed load time | <1s (p95) | ✅ Passed (T039) |
| **SC-002** | Infinite scroll | <500ms (p95) | ✅ Passed (T040) |
| **SC-006** | Like request | <200ms (p95) | 🧪 Pending |
| **SC-007** | Unlike request | <100ms (p95) | 🧪 Pending |

---

## Test Report Template

After completing tests, fill out:

```markdown
## Test Execution Report

**Tester**: [Your Name]
**Date**: [YYYY-MM-DD]
**Environment**: Local Development / Staging / Production
**Browser**: Chrome [version] / Firefox [version]
**OS**: Windows / macOS / Linux

### Results Summary

- Total Test Cases: 30
- Passed: __
- Failed: __
- Blocked: __
- Not Tested: __

### Failed Test Cases

| ID | Test Case | Issue Description | Severity |
|----|-----------|-------------------|----------|
| TC-US1-004 | Infinite Scroll | Pagination doesn't trigger | High |

### Performance Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Feed Load (SC-001) | <1s | 850ms | ✅ Pass |
| Pagination (SC-002) | <500ms | 320ms | ✅ Pass |
| Like (SC-006) | <200ms | 180ms | ✅ Pass |
| Unlike (SC-007) | <100ms | 75ms | ✅ Pass |

### Notes

[Any additional observations, bugs found, or recommendations]
```

---

**Document Version**: 1.1
**Last Updated**: 2026-01-18
**Next Review**: After Phase 5 (Comments) implementation

---

## Test Execution Notes (2026-01-18)

### Follow/Unfollow UI Testing Completed ✅

**Tests Executed**: TC-US1-009 through TC-US1-016 (7/9 completed)

**Results**: See detailed test results in [TEST_RESULTS_FOLLOW_UI.md](TEST_RESULTS_FOLLOW_UI.md)

**Summary**:
- ✅ All core follow/unfollow functionality working correctly
- ✅ Optimistic UI provides instant feedback
- ✅ Auto-refetch keeps all buttons in sync across feeds
- ✅ State persists across page reloads
- ✅ Performance meets targets (<500ms API, <1s refetch)

**Issues Fixed During Testing**:
1. Button size too large - reduced via CSS adjustments
2. Feed endpoint missing `is_following` field - added to backend schema
3. Frontend calling wrong API routes - corrected to `/users/{username}/follow`
4. User not persisting in localStorage - fixed in AuthContext

**Commits**: 8 commits (9c3e4f8...33fff9c) - See TEST_RESULTS_FOLLOW_UI.md for details

**Not Tested**:
- TC-US1-013 (Error Rollback) - Requires network failure simulation
- TC-US1-017 (Full Accessibility) - Screen reader testing pending

---

## Bugs Found During Testing

See [BUGS_FOUND_TESTING.md](BUGS_FOUND_TESTING.md) for complete bug reports.

### Bug #1: Duplicate Trips in Infinite Scroll Pagination

**Discovered During**: TC-US1-004
**Severity**: Medium
**Status**: ⚠️ Workaround Applied

**Summary**: Backend hybrid feed algorithm returns duplicate trips across pagination boundaries when transitioning from "followed users" content to "community backfill" content.

**Root Cause**: `backend/src/services/feed_service.py` - Backfill logic only excludes trips from current page, not ALL previous pages.

**Workaround**: Frontend deduplication in `useFeed.ts` hook filters out duplicate `trip_id` values during infinite scroll append.

**Action Required**: Fix backend `FeedService.get_personalized_feed()` hybrid algorithm to ensure no trip appears in multiple pages.

**Test Result**: ⚠️ PASS (with workaround) - Feature works correctly for users, but backend needs refactoring.

**Commit**: c315c67
