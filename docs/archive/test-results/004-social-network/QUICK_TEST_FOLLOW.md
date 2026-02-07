# Quick Test Guide - Follow/Unfollow UI

**Feature**: 004-social-network (US1: Feed Personalizado + Follow)
**Created**: 2026-01-18
**Branch**: `004-social-network`

---

## Prerequisites

### 1. Start Backend and Frontend

**Terminal 1 - Backend**:
```bash
cd "c:\My Program Files\workspace-claude\contravento-application-python"
.\run_backend.ps1 start
```

**Terminal 2 - Frontend**:
```bash
cd "c:\My Program Files\workspace-claude\contravento-application-python"
.\run_frontend.ps1 start
```

### 2. Create Test Users (if not exist)

```bash
cd backend

# Create users
poetry run python scripts/create_verified_user.py --username testuser --email test@example.com --password "Test123!"
poetry run python scripts/create_verified_user.py --username maria_garcia --email maria@example.com --password "Test123!"
poetry run python scripts/create_verified_user.py --username admin --email admin@example.com --password "Admin123!"
```

### 3. Seed Trips

```bash
# Seed trips for testuser
poetry run python scripts/seed_trips.py --user testuser

# Seed trips for maria_garcia
poetry run python scripts/seed_trips.py --user maria_garcia

# Seed trips for admin
poetry run python scripts/seed_trips.py --user admin
```

---

## Quick Test Scenarios

### Scenario 1: Follow Button Display ✅

**Objective**: Verify FollowButton appears on trip cards

**Steps**:
1. Open browser: http://localhost:5173
2. Login as `testuser` / `Test123!`
3. Navigate to `/feed`
4. Observe trip cards from other users

**Expected**:
- ✅ "Seguir" button appears next to author names (maria_garcia, admin)
- ✅ Button has User Plus icon
- ✅ Button does NOT appear on own trips (testuser)

---

### Scenario 2: Follow User ✅

**Objective**: Follow another user from feed

**Steps**:
1. Still logged in as `testuser`
2. On `/feed`, find a trip by `maria_garcia`
3. Click "Seguir" button next to maria_garcia's name

**Expected**:
- ✅ Button immediately changes to "Siguiendo" (optimistic UI)
- ✅ Icon changes to User Check
- ✅ Brief spinner appears
- ✅ Button stays "Siguiendo" after API completes

**Verify in Backend** (optional):
```bash
cd backend
poetry run python scripts/manage_follows.py --follower testuser --list
# Should show: testuser sigue a maria_garcia
```

---

### Scenario 3: Unfollow User ✅

**Objective**: Unfollow a user

**Steps**:
1. Still logged in as `testuser`
2. Find a trip by `maria_garcia` (should show "Siguiendo")
3. Click "Siguiendo" button

**Expected**:
- ✅ Button immediately changes to "Seguir" (optimistic UI)
- ✅ Icon changes to User Plus
- ✅ Button stays "Seguir" after API completes

---

### Scenario 4: Feed Updates After Follow ✅

**Objective**: Verify feed shows trips from followed users

**Setup**:
1. Logout (if logged in)
2. Using CLI, make testuser unfollow everyone:
   ```bash
   cd backend
   poetry run python scripts/manage_follows.py --follower testuser --list
   # For each user shown, unfollow:
   poetry run python scripts/manage_follows.py --follower testuser --following maria_garcia --unfollow
   poetry run python scripts/manage_follows.py --follower testuser --following admin --unfollow
   ```

**Steps**:
1. Login as `testuser`
2. Navigate to `/feed`
3. Observe feed content (should show popular backfill - trips from all users)
4. Click "Seguir" on a trip by `maria_garcia`
5. Refresh page (F5)

**Expected**:
- ✅ Before follow: Feed shows popular trips (mixed users)
- ✅ After follow: Feed prioritizes maria_garcia's trips at top
- ✅ Feed algorithm: followed users first, then popular backfill

---

### Scenario 5: Optimistic UI with Slow Network ✅

**Objective**: Test optimistic updates with network delay

**Steps**:
1. Open DevTools (F12) → Network tab
2. Enable throttling: "Slow 3G"
3. Login as `testuser`
4. Navigate to `/feed`
5. Click "Seguir" on a user

**Expected**:
- ✅ Button changes to "Siguiendo" INSTANTLY (before API response)
- ✅ Spinner shows during API call
- ✅ Button remains "Siguiendo" after API completes (2-3 seconds)
- ✅ No page freeze or jank

---

### Scenario 6: Error Rollback ✅

**Objective**: Test UI rollback on API failure

**Steps**:
1. Login as `testuser`
2. Navigate to `/feed`
3. **Stop backend server** (Terminal 1: Ctrl+C)
4. Click "Seguir" on a user
5. Wait 10 seconds

**Expected**:
- ✅ Button changes to "Siguiendo" immediately (optimistic)
- ✅ After timeout (~10s): button reverts to "Seguir"
- ✅ Error toast: "Error al procesar la acción. Intenta de nuevo."

**Cleanup**: Restart backend server (`.\run_backend.ps1 start`)

---

### Scenario 7: Prevent Self-Follow ✅

**Objective**: Verify users cannot follow themselves

**Steps**:
1. Login as `testuser`
2. Navigate to `/feed`
3. Observe own trips (testuser's trips)

**Expected**:
- ✅ No "Seguir" button on own trips
- ✅ Other users' trips still show "Seguir" button

---

### Scenario 8: Accessibility - Keyboard Navigation ✅

**Objective**: Test keyboard navigation

**Steps**:
1. Login as `testuser`
2. Navigate to `/feed`
3. Press **Tab** key repeatedly
4. When FollowButton is focused, press **Enter** or **Space**

**Expected**:
- ✅ Tab key moves focus to FollowButton
- ✅ Visible focus outline appears
- ✅ Enter/Space activates button (same as click)
- ✅ Button toggles follow/unfollow

---

### Scenario 9: Loading State Prevents Double-Click ✅

**Objective**: Verify button is disabled during loading

**Steps**:
1. Open DevTools → Network tab → Throttle to "Slow 3G"
2. Login as `testuser`
3. Navigate to `/feed`
4. Click "Seguir" button
5. While loading, try clicking button again multiple times

**Expected**:
- ✅ Button shows spinner
- ✅ Button is disabled (cursor: not-allowed)
- ✅ Multiple clicks do NOT trigger multiple API calls
- ✅ Only ONE follow action executes

---

## CLI Tools for Testing

### Create Follow Relationships

```bash
cd backend

# Make testuser follow maria_garcia
poetry run python scripts/manage_follows.py --follower testuser --following maria_garcia

# Make testuser follow admin
poetry run python scripts/manage_follows.py --follower testuser --following admin
```

### Remove Follow Relationships

```bash
# Unfollow
poetry run python scripts/manage_follows.py --follower testuser --following maria_garcia --unfollow
```

### List Relationships

```bash
# List who testuser follows
poetry run python scripts/manage_follows.py --follower testuser --list

# List testuser's followers
poetry run python scripts/manage_follows.py --following testuser --list
```

---

## Common Issues

### Issue: FollowButton not appearing

**Cause**: Frontend not using latest code or backend not returning `is_following`

**Fix**:
1. Hard refresh frontend: Ctrl+Shift+R
2. Check backend logs for errors
3. Verify `/trips/public` endpoint returns `is_following` field

### Issue: Follow/Unfollow not persisting

**Cause**: Backend API error or database issue

**Fix**:
1. Check backend logs for errors
2. Verify social table exists:
   ```bash
   cd backend
   poetry run alembic current
   # Should show migration with social table
   ```

### Issue: Button shows "Seguir" but user is already following

**Cause**: Frontend state out of sync with backend

**Fix**:
1. Refresh page (F5)
2. Check backend state with CLI:
   ```bash
   poetry run python scripts/manage_follows.py --follower testuser --list
   ```

---

## Success Criteria Checklist

After testing, verify:

- [ ] FollowButton appears on all trip cards (except own trips)
- [ ] Click "Seguir" → changes to "Siguiendo" instantly
- [ ] Click "Siguiendo" → changes to "Seguir" instantly
- [ ] Follow/unfollow persists after page refresh
- [ ] Feed shows trips from followed users first
- [ ] Optimistic UI works with slow network
- [ ] Error rollback works when backend is down
- [ ] Button is disabled during loading (prevents double-click)
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Self-follow is prevented (button hidden on own trips)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-18
**Next Review**: After completing all test scenarios
