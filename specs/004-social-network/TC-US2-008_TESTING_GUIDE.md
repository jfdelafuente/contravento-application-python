# TC-US2-008: Get Likes List - Manual Testing Guide

**Feature**: 004 - Social Network (US2 - Likes)
**Test Case**: TC-US2-008
**Component**: LikesListModal
**Date**: 2026-01-18

---

## Prerequisites

**Backend**: Running at http://localhost:8000
**Frontend**: Running at http://localhost:5173
**Database**: SQLite with test data (users with likes on trips)

**Test Users**:
- `testuser` / `TestPass123!` (main test user)
- `maria_garcia` / `SecurePass456!`
- `lolo` / `TestPass123!`

---

## Test Scenarios

### Scenario 1: Display Likes List Modal

**Objective**: Verify modal opens correctly when clicking like counter

**Steps**:
1. Login as `testuser`
2. Navigate to Public Feed (`/`)
3. Find a trip with `like_count > 0`
4. Click on the like counter number

**Expected Results**:
- ✅ Modal opens with fade-in animation
- ✅ Modal header shows "Me gusta" title
- ✅ Modal subtitle shows trip title (truncated if long)
- ✅ Heart icon displayed next to title (pink color)
- ✅ Close button (X) visible in top-right
- ✅ Background overlay darkens page content
- ✅ Body scroll is locked (page doesn't scroll behind modal)

**Pass Criteria**: Modal displays correctly with all UI elements

---

### Scenario 2: Empty State Display

**Objective**: Verify empty state when trip has 0 likes

**Steps**:
1. Login as `testuser`
2. Create a new trip (publish it)
3. Navigate to trip detail page
4. Click on like counter (should show "0 likes")

**Expected Results**:
- ✅ Modal opens successfully
- ✅ Empty state icon displayed (large heart, gray color)
- ✅ Message: "Aún no hay likes en este viaje"
- ✅ Hint: "Sé el primero en darle me gusta"
- ✅ No loading spinner
- ✅ No error message

**Pass Criteria**: Empty state displays correctly

---

### Scenario 3: Loading State Display

**Objective**: Verify loading state during API call

**Steps**:
1. Login as `testuser`
2. Navigate to Public Feed
3. Find a trip with many likes (>20)
4. Click like counter
5. Observe initial loading state (should be brief)

**Expected Results**:
- ✅ Loading spinner displayed
- ✅ Message: "Cargando likes..."
- ✅ Spinner animation runs smoothly
- ✅ Loading state transitions to likes list quickly (<500ms)

**Pass Criteria**: Loading state appears and disappears correctly

---

### Scenario 4: Likes List Display

**Objective**: Verify list of users who liked the trip

**Steps**:
1. Login as `testuser`
2. Navigate to a trip with multiple likes
3. Click like counter to open modal

**Expected Results**:
- ✅ List displays all users who liked
- ✅ Each item shows:
  - User avatar (or placeholder if no photo)
  - Username
  - Relative timestamp ("hace 2 horas", "hace 3 días")
- ✅ Count label: "X personas dieron like" (or "1 persona dio like")
- ✅ Avatars are circular (40px × 40px)
- ✅ Placeholder avatars show user icon
- ✅ List is scrollable if >10 users

**Pass Criteria**: All users displayed with correct info

---

### Scenario 5: Infinite Scroll Pagination

**Objective**: Verify infinite scroll loads more users

**Setup**: Need a trip with >20 likes to test pagination

**Steps**:
1. Login as `testuser`
2. Open likes modal for trip with >20 likes
3. Scroll to bottom of list
4. Observe pagination behavior

**Expected Results**:
- ✅ Initial load shows 20 users
- ✅ Scroll sentinel appears at bottom
- ✅ Loading spinner appears when scrolling near bottom
- ✅ Next page (20 more users) loads automatically
- ✅ No duplicate users in list
- ✅ Smooth scrolling (no jank)
- ✅ When all users loaded, no more sentinel

**Pass Criteria**: Pagination works without duplicates or errors

---

### Scenario 6: User Navigation

**Objective**: Verify clicking user navigates to profile

**Steps**:
1. Open likes modal
2. Click on any user in the list

**Expected Results**:
- ✅ Modal closes immediately
- ✅ Navigation to `/users/{username}` occurs
- ✅ User profile page loads

**Pass Criteria**: Navigation works and modal closes

---

### Scenario 7: Close Modal (X Button)

**Objective**: Verify close button works

**Steps**:
1. Open likes modal
2. Click X button in top-right

**Expected Results**:
- ✅ Modal closes immediately
- ✅ Background overlay disappears
- ✅ Body scroll unlocks
- ✅ No console errors

**Pass Criteria**: Modal closes cleanly

---

### Scenario 8: Close Modal (Overlay Click)

**Objective**: Verify clicking overlay closes modal

**Steps**:
1. Open likes modal
2. Click on darkened background outside modal

**Expected Results**:
- ✅ Modal closes
- ✅ Same cleanup as X button

**Pass Criteria**: Overlay click closes modal

---

### Scenario 9: Close Modal (ESC Key)

**Objective**: Verify ESC key closes modal

**Steps**:
1. Open likes modal
2. Press ESC key

**Expected Results**:
- ✅ Modal closes
- ✅ Keyboard focus returns to page

**Pass Criteria**: ESC key works

---

### Scenario 10: Multiple Integrations

**Objective**: Verify modal works in all locations

**Steps**:
1. Test modal from **PublicTripCard** (Public Feed)
2. Test modal from **TripDetailPage** (non-owner view)
3. Test modal from **TripDetailPage** (owner view - readonly counter)
4. Test modal from **FeedItem** (Personalized Feed)

**Expected Results**:
- ✅ Modal opens from all 4 locations
- ✅ Same UI/behavior in all cases
- ✅ Trip title displayed correctly in each case

**Pass Criteria**: Modal works consistently everywhere

---

### Scenario 11: Clickable Counter Visual Feedback

**Objective**: Verify hover/focus states on clickable counters

**Steps**:
1. Navigate to Public Feed
2. Hover over like counter (if `like_count > 0`)
3. Tab to like counter with keyboard
4. Click like counter

**Expected Results**:
- ✅ Cursor changes to pointer on hover
- ✅ Background highlight appears (pink translucent)
- ✅ Counter scales slightly (1.05x) on hover
- ✅ Focus outline appears (2px red) when tabbed
- ✅ Active state (scale 0.95x) on click

**Pass Criteria**: Visual feedback clear and responsive

---

### Scenario 12: Mobile Responsiveness

**Objective**: Verify modal works on mobile devices

**Steps**:
1. Open DevTools (F12)
2. Toggle device toolbar (mobile view)
3. Select iPhone 12 Pro (390px width)
4. Open likes modal

**Expected Results**:
- ✅ Modal slides up from bottom (not centered)
- ✅ Modal max height: 85vh
- ✅ Full width modal
- ✅ Rounded top corners (12px radius)
- ✅ Touch-friendly close button (44px tap target)
- ✅ Scrollable list
- ✅ No horizontal scroll

**Pass Criteria**: Mobile UX is optimized

---

### Scenario 13: Accessibility (Keyboard Navigation)

**Objective**: Verify keyboard accessibility

**Steps**:
1. Open likes modal
2. Press Tab key repeatedly
3. Navigate through users
4. Press Enter on a user

**Expected Results**:
- ✅ Focus moves to close button first
- ✅ Focus moves through user list items
- ✅ Focus indicator visible (outline)
- ✅ Enter key on user navigates to profile
- ✅ Enter key on close button closes modal
- ✅ ESC key works from anywhere

**Pass Criteria**: Full keyboard navigation works

---

### Scenario 14: Accessibility (Screen Reader - Optional)

**Objective**: Verify screen reader support

**Tools**: NVDA (Windows) or VoiceOver (Mac)

**Steps**:
1. Enable screen reader
2. Open likes modal
3. Listen to announcements

**Expected Results**:
- ✅ Dialog role announced
- ✅ Title "Me gusta" announced
- ✅ Loading state announced ("Cargando likes...")
- ✅ User count announced ("X personas dieron like")
- ✅ Each user announced with username
- ✅ Close button labeled correctly

**Pass Criteria**: All content accessible to screen readers

---

### Scenario 15: Error Handling

**Objective**: Verify error state when API fails

**Steps** (requires backend manipulation):
1. Stop backend server temporarily
2. Open likes modal
3. Observe error state
4. Click "Reintentar" button

**Expected Results**:
- ✅ Error message displayed (Spanish)
- ✅ Retry button appears
- ✅ Error icon or visual indicator
- ✅ No crash or blank screen

**Pass Criteria**: Errors handled gracefully

---

### Scenario 16: Performance

**Objective**: Verify performance meets targets

**Steps**:
1. Open DevTools → Network tab
2. Open likes modal (trip with 50 likes)
3. Measure API response time

**Expected Results**:
- ✅ API response <300ms (SC-008 target)
- ✅ Modal animation smooth (60fps)
- ✅ Infinite scroll smooth (no lag)
- ✅ No memory leaks (check with Performance tab)

**Pass Criteria**: Performance targets met

---

## Test Summary Checklist

- [ ] Scenario 1: Display Likes List Modal
- [ ] Scenario 2: Empty State Display
- [ ] Scenario 3: Loading State Display
- [ ] Scenario 4: Likes List Display
- [ ] Scenario 5: Infinite Scroll Pagination
- [ ] Scenario 6: User Navigation
- [ ] Scenario 7: Close Modal (X Button)
- [ ] Scenario 8: Close Modal (Overlay Click)
- [ ] Scenario 9: Close Modal (ESC Key)
- [ ] Scenario 10: Multiple Integrations
- [ ] Scenario 11: Clickable Counter Visual Feedback
- [ ] Scenario 12: Mobile Responsiveness
- [ ] Scenario 13: Accessibility (Keyboard Navigation)
- [ ] Scenario 14: Accessibility (Screen Reader)
- [ ] Scenario 15: Error Handling
- [ ] Scenario 16: Performance

---

## Test Execution Notes

**Date**: _____________
**Tester**: _____________
**Browser**: Chrome / Firefox / Safari / Edge
**OS**: Windows / macOS / Linux

**Scenarios Passed**: _____ / 16
**Scenarios Failed**: _____ / 16
**Blockers Found**: _____________

---

## Known Issues / Limitations

1. **Infinite scroll testing**: Requires creating test data with >20 likes on a trip
2. **Screen reader testing**: Optional but recommended for full accessibility validation
3. **Error state testing**: Requires temporarily stopping backend server

---

## Post-Testing Actions

- [ ] Document any bugs found
- [ ] Update TESTING_MANUAL_US1_US2.md with results
- [ ] Create issues for failed scenarios (if any)
- [ ] Mark TC-US2-008 as PASS/FAIL

---

**Test Guide Version**: 1.0
**Last Updated**: 2026-01-18
