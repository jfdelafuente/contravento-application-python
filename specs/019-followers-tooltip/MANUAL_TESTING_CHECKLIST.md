# Manual Testing Checklist - Feature 019

**Purpose**: Validate all user-facing functionality before merging to develop
**Created**: 2026-02-13
**Tester**: _____________________
**Date**: _____________________

## Prerequisites

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:5173
- [ ] Logged in as `testuser` (password: `TestPass123!`)
- [ ] Test user has at least 9 followers (for "Ver todos" link testing)
- [ ] Test user has at least 1 following

## Test Scenarios (18 Total)

### 1. Followers Tooltip - Basic Functionality

- [ ] **Hover over "Seguidores" card for 500ms** → Tooltip appears
- [ ] **Tooltip shows max 8 users** with avatars and usernames
- [ ] **Tooltip shows header** "SEGUIDORES" in uppercase
- [ ] **Quick hover (<500ms)** → NO tooltip appears (prevents accidental triggers)
- [ ] **Mouse leave for 200ms** → Tooltip disappears

### 2. Following Tooltip - Basic Functionality

- [ ] **Hover over "Siguiendo" card for 500ms** → Tooltip appears
- [ ] **Tooltip shows max 8 users** with avatars and usernames
- [ ] **Tooltip shows header** "SIGUIENDO" in uppercase
- [ ] **Mouse leave for 200ms** → Tooltip disappears

### 3. "Ver todos" Link

**Prerequisite**: Test user must have 9+ followers

- [ ] **Hover followers card** → "Ver todos" link visible at bottom
- [ ] **Click "Ver todos"** → Navigate to `/users/testuser/followers`
- [ ] **Back to dashboard** → Hover following card → Click "Ver todos" → Navigate to `/users/testuser/following`

**If user has ≤8 followers**:
- [ ] **"Ver todos" link does NOT appear** (expected behavior)

### 4. Empty State

**Prerequisite**: Use a test user with 0 followers

- [ ] **Hover followers card (0 followers)** → Tooltip shows "No tienes seguidores aún"
- [ ] **No user list shown**, only empty message
- [ ] **"Ver todos" link NOT visible**

### 5. Loading State

**Use browser DevTools Network throttling**:

1. Open DevTools → Network tab → Throttling: "Slow 3G"
2. Hover over "Seguidores" card
3. [ ] **Spinner visible** immediately after 500ms delay
4. [ ] **"Cargando..." text** displayed
5. [ ] **After API response** → User list replaces spinner

### 6. Error State

**Simulate network failure**:

1. Open DevTools → Network tab → Check "Offline"
2. Hover over "Seguidores" card
3. [ ] **Error message displayed** in Spanish: "Error al cargar usuarios"
4. [ ] **No user list shown**
5. Re-enable network → Hover again → Verify tooltip loads correctly

### 7. Keyboard Navigation

- [ ] **Tab to "Seguidores" card** → Card gets amber focus ring (2px outline)
- [ ] **Wait 500ms** → Tooltip appears (same as hover)
- [ ] **Tab again** → Focus moves to first username link (amber focus ring)
- [ ] **Tab again** → Focus moves to second username link
- [ ] **Press Escape** → Tooltip closes immediately (no delay)
- [ ] **Tab to card again, focus** → Tooltip reappears
- [ ] **Tab to username link, press Enter** → Navigate to user profile

### 8. Screen Reader Testing

**Use NVDA (Windows) / VoiceOver (Mac)**:

- [ ] **Focus on "Seguidores" card** → Screen reader announces "Ver seguidores, button"
- [ ] **Tooltip appears** → Screen reader announces "polite" region
- [ ] **Focus on username link** → Screen reader announces username
- [ ] **Focus on "Ver todos" link** → Screen reader announces full text with count (e.g., "Ver todos los seguidores (15 total)")

### 9. Touch Device Fallback (Mobile Simulation)

**Use browser DevTools Device Toolbar** (F12 → Toggle device toolbar):

1. Select device: "iPhone SE" (375×667)
2. [ ] **Tap "Seguidores" card** → Navigate directly to `/users/testuser/followers` (NO tooltip)
3. [ ] **Back to dashboard** → Tap "Siguiendo" card → Navigate to `/users/testuser/following`
4. [ ] **NO tooltip appears on tap** (expected - progressive enhancement)

### 10. Lazy Loading Validation

**Use DevTools Network tab**:

1. Clear network log
2. Navigate to dashboard
3. [ ] **NO API calls** to `/users/testuser/followers` or `/following` on page load
4. Hover over "Seguidores" card
5. [ ] **API call triggered** only after 500ms hover delay
6. [ ] **Only 1 API call** per hover (no duplicate requests)

### 11. No Layout Shift (CLS = 0)

**Use DevTools Performance tab**:

1. Open DevTools → Performance → Record
2. Hover over "Seguidores" card → Tooltip appears
3. Stop recording
4. [ ] **Check "Experience" lane** → No Layout Shift events
5. [ ] **Card position doesn't move** when tooltip appears
6. [ ] **Tooltip uses absolute positioning** (doesn't push content down)

### 12. Tooltip Positioning

- [ ] **Tooltip appears centered below card** (8px gap)
- [ ] **Arrow points up to card** (CSS triangle)
- [ ] **Tooltip within viewport** (doesn't overflow off-screen)
- [ ] **On narrow screens** → Tooltip shrinks to fit (min-width: 200px)

### 13. Username Link Navigation

- [ ] **Click username in tooltip** → Navigate to `/users/{username}` profile page
- [ ] **Profile page loads correctly**
- [ ] **Back button** → Return to dashboard

### 14. Hover from Card to Tooltip

- [ ] **Hover over "Seguidores" card** → Tooltip appears
- [ ] **Move mouse from card into tooltip** → Tooltip stays visible (200ms leave delay)
- [ ] **Hover over username link** → Background changes to light gray
- [ ] **Move mouse out of tooltip** → After 200ms, tooltip disappears

### 15. Contrast & Readability

- [ ] **Tooltip background** is solid white (not transparent)
- [ ] **Border is dark** (2px solid #2d3748) for clear definition
- [ ] **Text color is dark** (#1f2937) on white background
- [ ] **Focus ring is amber** (#ea580c) - high contrast
- [ ] **All text readable** without zooming

### 16. Animations & Transitions

- [ ] **Tooltip fade-in** is smooth (150ms)
- [ ] **Tooltip slides up slightly** during fade-in (4px translateY)
- [ ] **Username link hover** has smooth background transition (150ms)
- [ ] **No janky animations** or flickering

### 17. Concurrent Tooltips

- [ ] **Hover "Seguidores" card** → Tooltip appears
- [ ] **Move to "Siguiendo" card** → First tooltip disappears, second appears
- [ ] **Only 1 tooltip visible at a time** (expected behavior)

### 18. Responsive Design (Desktop → Mobile)

**Desktop (>768px)**:
- [ ] **Tooltip min-width: 220px, max-width: 280px**
- [ ] **Font sizes readable** (13px username, 12px header)

**Mobile (<768px)** - Use DevTools responsive mode:
- [ ] **Tooltip min-width: 200px, max-width: 240px**
- [ ] **Tooltip still centered** below card
- [ ] **Touch navigation works** (tap card → navigate directly)

---

## Summary

**Total Scenarios**: 18
**Passed**: ___ / 18
**Failed**: ___
**Blocked**: ___

## Issues Found

_List any bugs, UX issues, or unexpected behavior below:_

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

## Sign-off

- [ ] **All critical scenarios passed** (1-6, 7-11)
- [ ] **Accessibility validated** (8)
- [ ] **Performance validated** (10-11)
- [ ] **Ready for merge to develop**

**Tester Signature**: _____________________
**Date**: _____________________
