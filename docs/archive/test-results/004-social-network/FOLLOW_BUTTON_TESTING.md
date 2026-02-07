# Follow/Unfollow Button - Manual Testing Report

**Feature**: 004-social-network
**Component**: FollowButton
**Test Date**: 2026-01-19
**Tester**: Claude Code
**Environment**: Local Development (SQLite)
**Branch**: `004-social-network`

---

## Test Setup

**Servers Status**:
- ✅ Backend: `http://localhost:8000` (Running - PID 26284)
- ✅ Frontend: `http://localhost:5173` (Running - PID 34984)

**Test Users**:
- **Primary User**: `testuser` / `TestPass123!`
- **Target User**: User profiles to follow/unfollow

**Pre-Test API Verification**:
```bash
# Unauthenticated request shows is_following: null
curl http://localhost:8000/users/testuser/profile | jq '.is_following'
# Output: null ✓
```

---

## Test Case 1: Verify `is_following` Field in API Response (Backend)

**Objective**: Confirm backend returns `is_following` field correctly

**Steps**:
1. Make unauthenticated request to `/users/testuser/profile`
2. Verify `is_following` is `null`

**Expected Result**:
```json
{
  "is_following": null
}
```

**Actual Result**: ✅ **PASS**
```json
{
  "username": "testuser",
  "followers_count": 1,
  "following_count": 1,
  "is_following": null,  ← Present and null when not authenticated
  "stats": { ... }
}
```

---

## Test Case 2: Initial State - Not Following (Frontend)

**Objective**: Verify FollowButton shows correct initial state when not following

**URL**: `http://localhost:5173/users/{other_user}`

**Steps**:
1. Login as `testuser`
2. Navigate to another user's profile (not currently followed)
3. Observe FollowButton state

**Expected Result**:
- Button text: "Seguir"
- Button icon: User Plus icon (not following)
- Button is enabled and clickable

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

**Notes**:
- Backend implementation complete
- Frontend type updated to include `is_following`
- UserProfilePage now passes `profile.is_following || false` to FollowButton
- Ready for browser testing

---

## Test Case 3: Follow Action - Optimistic Update

**Objective**: Verify follow action works with optimistic UI update

**Steps**:
1. Click "Seguir" button
2. Observe immediate UI change (optimistic update)
3. Wait for API response
4. Verify final state

**Expected Result**:
- **Immediate**: Button changes to "Siguiendo" with User Check icon
- **After API**: Button remains "Siguiendo" (no revert)
- **Toast**: No error message appears
- **Event**: `followStatusChanged` event dispatched

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

---

## Test Case 4: State Persistence After Refresh

**Objective**: Verify follow state persists after page reload

**Steps**:
1. Follow a user (button shows "Siguiendo")
2. Refresh the page (F5)
3. Observe button state after reload

**Expected Result**:
- Button immediately shows "Siguiendo" on page load
- `initialFollowing` prop received `true` from API

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

**Critical Check**:
- Backend must return `is_following: true` for authenticated user
- Frontend must pass this value to FollowButton

---

## Test Case 5: Unfollow Action

**Objective**: Verify unfollow action works correctly

**Steps**:
1. Ensure user is following target (button shows "Siguiendo")
2. Click "Siguiendo" button
3. Observe immediate UI change
4. Wait for API response
5. Verify final state

**Expected Result**:
- **Immediate**: Button changes to "Seguir"
- **After API**: Button remains "Seguir"
- **Toast**: No error message
- **Event**: `followStatusChanged` event dispatched

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

---

## Test Case 6: Feed Integration

**Objective**: Verify following a user updates the feed

**Steps**:
1. Note current feed content at `/feed`
2. Follow a new user who has published trips
3. Return to `/feed`
4. Verify feed shows trips from newly followed user

**Expected Result**:
- Feed automatically refetches on `followStatusChanged` event
- Newly followed user's trips appear in feed (chronological order)
- Previously visible community trips may be pushed down

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

**Related**: This test unblocks TC-US1-002 (Feed Content - Followed Users)

---

## Test Case 7: Unauthenticated User

**Objective**: Verify button doesn't appear when not logged in

**Steps**:
1. Logout from application
2. Navigate to `/users/{username}` (any public profile)
3. Observe button visibility

**Expected Result**:
- FollowButton component does NOT render
- Profile page shows public information only
- No authentication error

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

**Implementation Note**:
```typescript
// FollowButton.tsx:47-49
if (!currentUsername || currentUsername === username) {
  return null;  // Don't show button
}
```

---

## Test Case 8: Own Profile

**Objective**: Verify button doesn't appear on own profile

**Steps**:
1. Login as `testuser`
2. Navigate to `/profile` or `/users/testuser`
3. Observe button visibility

**Expected Result**:
- FollowButton component does NOT render
- UserProfilePage redirects `/users/testuser` → `/profile` for owner

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

**Implementation Note**:
```typescript
// UserProfilePage.tsx:32-36
if (user && username === user.username) {
  navigate('/profile', { replace: true });
}
```

---

## Test Case 9: API Error Handling

**Objective**: Verify graceful error handling on API failure

**Steps**:
1. (Simulate) Stop backend server temporarily
2. Click "Seguir" button
3. Observe error handling

**Expected Result**:
- Optimistic update initially shows "Siguiendo"
- API call fails
- Button reverts to "Seguir" (rollback)
- Toast shows Spanish error message: "Error al procesar la acción. Intenta de nuevo."

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

**Implementation Note**: `useFollow` hook handles rollback on error

---

## Test Case 10: Loading State

**Objective**: Verify loading state during API call

**Steps**:
1. Click "Seguir" button
2. Observe button during API call (brief moment)

**Expected Result**:
- Button shows spinner icon
- Button is disabled (`disabled` attribute set)
- Prevents double-click during request

**Actual Result**: ⏳ **PENDING MANUAL VERIFICATION**

**Implementation Note**:
```typescript
// FollowButton.tsx:67-68
{isLoading ? (
  <span className="follow-button__spinner" aria-hidden="true"></span>
```

---

## API Contract Verification

**Backend Changes**:
- ✅ `ProfileResponse` schema includes `is_following: Optional[bool]`
- ✅ `ProfileService.get_profile()` queries `Follow` table when authenticated
- ✅ Returns `null` when not authenticated
- ✅ Returns `true`/`false` when authenticated

**Frontend Changes**:
- ✅ `UserProfile` type includes `is_following?: boolean | null`
- ✅ `UserProfilePage` passes `profile.is_following || false` to FollowButton
- ✅ Handles `null` case gracefully (defaults to `false`)

**API Response Example** (Authenticated):
```bash
# Login first, then:
curl -H "Authorization: Bearer {token}" http://localhost:8000/users/other_user/profile

# Expected:
{
  "is_following": true,  ← or false, depending on current state
  ...
}
```

---

## Code Coverage

**Files Modified**:
1. ✅ `backend/src/schemas/profile.py` - Added `is_following` field
2. ✅ `backend/src/services/profile_service.py` - Query follow status
3. ✅ `frontend/src/types/profile.ts` - Added `is_following` to interface
4. ✅ `frontend/src/pages/UserProfilePage.tsx` - Pass real value to FollowButton

**Files Already Implemented** (Feature 004):
5. ✅ `frontend/src/components/social/FollowButton.tsx` - Component logic
6. ✅ `frontend/src/hooks/useFollow.ts` - Follow/unfollow hook
7. ✅ `frontend/src/services/followService.ts` - API integration

---

## Next Steps

1. **Manual Browser Testing** (In Progress):
   - [ ] TC2: Initial state verification
   - [ ] TC3: Follow action
   - [ ] TC4: State persistence
   - [ ] TC5: Unfollow action
   - [ ] TC6: Feed integration
   - [ ] TC7: Unauthenticated behavior
   - [ ] TC8: Own profile behavior
   - [ ] TC9: Error handling
   - [ ] TC10: Loading state

2. **Documentation Update**:
   - [ ] Update NEXT_STEPS.md with test results
   - [ ] Update TC-US1-002 status (unblock)
   - [ ] Update US1 coverage percentage

3. **Commit Changes**:
   - [ ] Create commit with follow button integration
   - [ ] Push to `004-social-network` branch

---

## Browser Testing Instructions

**URL to Test**: `http://localhost:5173`

1. Login as `testuser` / `TestPass123!`
2. Navigate to Feed (`/feed`)
3. Click on a trip card's author to open their profile
4. Observe FollowButton behavior
5. Test follow/unfollow actions
6. Verify state persistence with page refresh
7. Test feed integration

**Validation Checklist**:
- [ ] Button shows correct initial state (Following vs Seguir)
- [ ] Button responds to clicks with optimistic updates
- [ ] State persists after page reload
- [ ] Feed updates when following/unfollowing users
- [ ] No button appears when not authenticated
- [ ] No button appears on own profile

---

**Status**: ⏳ **READY FOR MANUAL BROWSER TESTING**

**Backend**: ✅ **COMPLETE**
**Frontend**: ✅ **COMPLETE**
**Integration**: ⏳ **PENDING VERIFICATION**
