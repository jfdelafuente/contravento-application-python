# Scenario 1: Display Likes List Modal - Step-by-Step Walkthrough

**Test Case**: TC-US2-008
**Scenario**: 1 - Display Likes List Modal
**Date**: 2026-01-18

---

## Setup (One-Time)

### 1. Ensure Test Data Exists

We need trips with likes to test the modal. Let's verify:

```bash
# Check if trips with likes exist
curl http://localhost:8000/trips/public?page=1&limit=10

# Look for trips with "like_count" > 0
```

### 2. Create Test Likes (If Needed)

**Option A: Via Frontend (Recommended)**
1. Login as `testuser` (TestPass123!)
2. Go to Public Feed: http://localhost:5173/
3. Find trips from other users (maria_garcia, lolo)
4. Click the heart button to like 3-5 trips
5. Logout

**Option B: Via API (Advanced)**
```bash
# Login as testuser
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}' \
  -c cookies.txt

# Get a trip ID from public feed
TRIP_ID="<paste-trip-id-here>"

# Like the trip
curl -X POST "http://localhost:8000/trips/$TRIP_ID/like" \
  -b cookies.txt
```

**Option C: Login as Multiple Users**
1. Login as `maria_garcia` (SecurePass456!)
2. Like 2-3 trips from `testuser`
3. Logout, login as `lolo` (TestPass123!)
4. Like the same trips
5. Now testuser's trips will have multiple likes

---

## Test Execution

### Step 1: Login to Application

1. Open browser: http://localhost:5173
2. Click "Iniciar sesión"
3. Enter credentials:
   - Email: `test@example.com`
   - Password: `TestPass123!`
4. Click "Iniciar sesión"

**Expected**: Redirect to Dashboard

---

### Step 2: Navigate to Public Feed

1. Click "Explorar" in navigation (or go to http://localhost:5173/)
2. Wait for feed to load

**Expected**: Grid of trip cards displayed

---

### Step 3: Find Trip with Likes

1. Look at each trip card
2. Find the like button/counter area (bottom of card)
3. Identify a trip with `like_count > 0` (e.g., "5" next to heart icon)

**What to look for**:
- Heart icon (outline or filled)
- Number next to heart
- If number is **clickable** (cursor changes to pointer on hover)

**Example**:
```
┌─────────────────────────┐
│  [Trip Photo]           │
│                         │
│  Trip Title Here        │
│  by maria_garcia  [Seguir] │
│                         │
│  📍 Barcelona • 50km    │
│  📅 15 de enero         │
│                         │
│  ❤️ 5  💬 3  📤 1      │ <- Like counter here
└─────────────────────────┘
```

---

### Step 4: Click Like Counter

1. **Hover** over the like count number
   - Verify cursor changes to **pointer** (hand icon)
   - Verify **background highlight** appears (subtle pink)
   - Verify number **scales slightly** larger (1.05x)

2. **Click** on the like count number
   - Click directly on the number, not the heart icon
   - Heart icon = toggle like
   - Number = open modal

**Expected**: Modal opens immediately

---

### Step 5: Verify Modal Display

Check all visual elements are present:

#### ✅ Modal Structure
- [ ] **Overlay**: Dark background behind modal (rgba(34, 34, 34, 0.85))
- [ ] **Modal Container**: White/cream box centered on screen
- [ ] **Modal Border**: 2px solid border (#8b7355 - brown)
- [ ] **Box Shadow**: Visible shadow around modal
- [ ] **Animation**: Modal slides up/fades in (300ms duration)

#### ✅ Header Section
- [ ] **Heart Icon**: Pink heart icon (20px) next to title
- [ ] **Title**: "Me gusta" in Playfair Display font
- [ ] **Subtitle**: Trip title displayed below (truncated if long)
- [ ] **Close Button**: X icon in top-right corner
- [ ] **Background**: Subtle gradient (cream to white)

#### ✅ Content Area
- [ ] **User Count**: "X personas dieron like" (or "1 persona dio like")
- [ ] **List of Users**: Scrollable list with avatars and usernames
- [ ] **Scrollbar**: Visible if >10 users (custom styled)

#### ✅ Body Scroll Lock
- [ ] **Page Behind**: Try scrolling page with mouse wheel
- [ ] **Expected**: Page should NOT scroll (body locked)
- [ ] **Modal Scrolls**: Only the modal content scrolls

---

### Step 6: Inspect Individual Elements

#### Header Details
```
┌────────────────────────────────────────┐
│  ❤️ Me gusta                        ✕  │ <- Header
│  Trip Title Here (truncated...)        │ <- Subtitle
├────────────────────────────────────────┤
│  5 personas dieron like                │ <- Count
│                                        │
│  👤 maria_garcia                       │
│     Hace 2 horas                       │
│                                        │
│  👤 lolo                               │
│     Hace 1 día                         │
│                                        │
│  ...                                   │
└────────────────────────────────────────┘
```

**Verify**:
- [ ] Heart icon is **pink** (#c1666b)
- [ ] Title is **large** (1.25rem, bold, Playfair Display)
- [ ] Subtitle is **smaller** (0.875rem, gray)
- [ ] Subtitle **truncates** with "..." if >300px wide
- [ ] Close button has **hover effect** (background on hover)

---

### Step 7: Check Responsive Behavior

#### Desktop (>640px)
- [ ] Modal **centered** on screen
- [ ] Max width: **500px**
- [ ] Max height: **80vh**
- [ ] Rounded corners: **8px**

#### Mobile (Open DevTools, toggle device mode, select iPhone)
- [ ] Modal **bottom-aligned** (not centered)
- [ ] Full width: **100%**
- [ ] Max height: **85vh**
- [ ] Rounded **top** corners only: **12px**
- [ ] No rounded bottom corners

---

### Step 8: Test Interactions

1. **Hover over Close Button (X)**
   - [ ] Background changes (subtle gray)
   - [ ] Cursor is pointer

2. **Click Close Button**
   - [ ] Modal closes immediately
   - [ ] Fade-out animation
   - [ ] Overlay disappears
   - [ ] Body scroll **unlocks**
   - [ ] Can scroll page again

3. **Re-open Modal** (click like count again)

4. **Click Overlay** (dark background outside modal)
   - [ ] Modal closes
   - [ ] Same behavior as X button

5. **Re-open Modal**

6. **Press ESC Key**
   - [ ] Modal closes
   - [ ] Same cleanup as other methods

---

### Step 9: Verify No Errors

1. Open **DevTools** (F12)
2. Go to **Console** tab
3. Check for errors

**Expected**:
- [ ] **No red errors** in console
- [ ] No warnings about missing props
- [ ] No "Failed to fetch" errors

---

### Step 10: Test Edge Cases

#### Case 1: Trip with 0 Likes
1. Find a trip with `like_count = 0`
2. Try clicking the counter

**Expected**:
- [ ] Counter is **not clickable** (no pointer cursor)
- [ ] No hover effect
- [ ] Modal does NOT open

#### Case 2: Very Long Trip Title
1. Find a trip with long title (>50 characters)
2. Open likes modal

**Expected**:
- [ ] Title truncates with "..."
- [ ] Max width respected (~300px)
- [ ] No text overflow outside modal

---

## Test Results

### Scenario 1 Results

**Date**: _____________
**Browser**: Chrome / Firefox / Safari
**Screen Size**: 1920x1080 (Desktop) / 390x844 (Mobile)

| Check | Status | Notes |
|-------|--------|-------|
| Modal opens on click | ✅ / ❌ | |
| All UI elements present | ✅ / ❌ | |
| Animations smooth | ✅ / ❌ | |
| Body scroll locked | ✅ / ❌ | |
| Close button works | ✅ / ❌ | |
| Overlay click works | ✅ / ❌ | |
| ESC key works | ✅ / ❌ | |
| Mobile responsive | ✅ / ❌ | |
| No console errors | ✅ / ❌ | |
| Edge cases handled | ✅ / ❌ | |

**Overall Result**: ✅ PASS / ❌ FAIL

**Issues Found**:
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

---

## Screenshots (Optional)

Capture screenshots of:
1. Modal on desktop (centered)
2. Modal on mobile (bottom-aligned)
3. Hover state on like counter
4. Empty state (if trip has 0 likes)

Save to: `specs/004-social-network/screenshots/TC-US2-008/`

---

## Next Steps

- [ ] Mark Scenario 1 as PASS/FAIL in TC-US2-008_TESTING_GUIDE.md
- [ ] If PASS, proceed to Scenario 2 (Empty State)
- [ ] If FAIL, document bugs and create issue

---

**Tester**: _____________
**Signature**: _____________
**Date**: _____________
