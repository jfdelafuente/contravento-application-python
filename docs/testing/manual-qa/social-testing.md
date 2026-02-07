# Social Network Manual Testing

Manual QA testing procedures for social network features.

**Consolidated from**: `specs/004-social-network/MANUAL_TESTING_GUIDE.md` + 10 related files (Phase 3)

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Follow/Unfollow Testing](#followunfollow-testing)
- [Comments Testing](#comments-testing)
- [Likes Testing](#likes-testing)
- [Public Feed Testing](#public-feed-testing)
- [Test Scenarios](#test-scenarios)

---

## Overview

This guide consolidates manual testing procedures for all social network features:

- **Follow/Unfollow** (User Story 1 & 2)
- **Comments** (User Story 3)
- **Likes** (User Story 4)
- **Public Feed** (User Story 5)

**Test Environment**: Local development (`http://localhost:5173`)

---

## Prerequisites

### 1. Create Test Users

```bash
cd backend

# Create user 1 (testuser)
poetry run python scripts/user-mgmt/create_verified_user.py

# Create user 2 (maria_garcia)
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username maria_garcia \
  --email maria@example.com \
  --password SecurePass456!
```

**Test Credentials**:
- User 1: `test@example.com` / `TestPass123!` (testuser)
- User 2: `maria@example.com` / `SecurePass456!` (maria_garcia)

### 2. Create Published Trips

```bash
# Login as User 1
# Create 2-3 published trips with photos

# Login as User 2
# Create 2-3 published trips with photos
```

---

## Follow/Unfollow Testing

### Test Case: US1-TC001 - Follow User

**Objective**: Verify user can follow another user

**Steps**:
1. Login as User 1 (`testuser`)
2. Navigate to User 2's profile (`maria_garcia`)
3. Click "Seguir" button
4. Verify button changes to "Siguiendo"
5. Verify follow count increases by 1
6. Navigate to "Siguiendo" tab
7. Verify User 2 appears in following list

**Expected Result**:
- ✅ Button text changes to "Siguiendo"
- ✅ Button style changes (filled, green check icon)
- ✅ Follow count updates immediately
- ✅ User appears in following list

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US1-TC002 - Unfollow User

**Objective**: Verify user can unfollow a followed user

**Steps**:
1. Login as User 1 (following User 2 from previous test)
2. Navigate to User 2's profile
3. Click "Siguiendo" button
4. Verify confirmation modal appears
5. Click "Dejar de seguir" in modal
6. Verify button changes back to "Seguir"
7. Verify follow count decreases by 1

**Expected Result**:
- ✅ Confirmation modal displayed
- ✅ Button text changes to "Seguir"
- ✅ Button style reverts (outline, no check icon)
- ✅ Follow count updates immediately
- ✅ User removed from following list

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US1-TC003 - Cannot Follow Yourself

**Objective**: Verify user cannot follow their own profile

**Steps**:
1. Login as User 1
2. Navigate to own profile page
3. Verify "Seguir" button does not appear

**Expected Result**:
- ✅ No "Seguir" button displayed on own profile
- ✅ Only "Editar perfil" button visible

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US1-TC004 - Following List Pagination

**Objective**: Verify following list supports pagination

**Prerequisites**: User 1 following 15+ users

**Steps**:
1. Login as User 1
2. Navigate to "Siguiendo" tab
3. Scroll to bottom of list
4. Verify "Cargar más" button appears
5. Click "Cargar más"
6. Verify additional users loaded

**Expected Result**:
- ✅ First 20 users displayed initially
- ✅ "Cargar más" button visible if >20 following
- ✅ Next 20 users load on button click
- ✅ Smooth loading animation

**Actual Result**: _[To be filled during test execution]_

---

## Comments Testing

### Test Case: US3-TC001 - Add Comment

**Objective**: Verify user can add comment to published trip

**Steps**:
1. Login as User 1
2. Navigate to User 2's published trip
3. Scroll to comments section
4. Type comment in textarea: "¡Qué ruta tan espectacular!"
5. Click "Comentar" button
6. Verify comment appears immediately below textarea
7. Verify comment shows author name, avatar, and timestamp

**Expected Result**:
- ✅ Comment posted successfully
- ✅ Comment displayed with author info
- ✅ "Hace unos segundos" timestamp
- ✅ Textarea cleared after posting
- ✅ Comment count increases by 1

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US3-TC002 - Delete Own Comment

**Objective**: Verify user can delete their own comment

**Steps**:
1. Login as User 1 (with existing comment from TC001)
2. Navigate to trip with comment
3. Hover over own comment
4. Click delete icon (trash)
5. Verify confirmation modal appears
6. Click "Eliminar" in modal
7. Verify comment removed from list
8. Verify comment count decreases by 1

**Expected Result**:
- ✅ Delete icon visible on own comments only
- ✅ Confirmation modal displayed
- ✅ Comment removed immediately
- ✅ Smooth fade-out animation
- ✅ Comment count updates

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US3-TC003 - Cannot Comment on Draft

**Objective**: Verify comments disabled on draft trips

**Steps**:
1. Login as User 1
2. Create draft trip (do not publish)
3. Navigate to draft trip detail page
4. Verify comments section not displayed

**Expected Result**:
- ✅ Comments section hidden for draft trips
- ✅ Message: "Los comentarios estarán disponibles cuando publiques el viaje"

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US3-TC004 - Comment Validation

**Objective**: Verify comment length validation

**Steps**:
1. Login as User 1
2. Navigate to published trip
3. Try to post empty comment
4. Verify error: "El comentario no puede estar vacío"
5. Type comment with 1001 characters
6. Verify error: "El comentario no puede superar 1000 caracteres"
7. Verify character counter shows "1001/1000"

**Expected Result**:
- ✅ Empty comments rejected
- ✅ Comments >1000 chars rejected
- ✅ Real-time character counter
- ✅ "Comentar" button disabled when invalid

**Actual Result**: _[To be filled during test execution]_

---

## Likes Testing

### Test Case: US4-TC001 - Like Trip

**Objective**: Verify user can like a published trip

**Steps**:
1. Login as User 1
2. Navigate to User 2's published trip
3. Click heart icon (outline state)
4. Verify icon fills with color (solid state)
5. Verify like count increases by 1
6. Verify like animation plays (heart bounce)

**Expected Result**:
- ✅ Heart icon changes to filled state
- ✅ Like count updates immediately
- ✅ Smooth animation on like
- ✅ Like persists on page reload

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US4-TC002 - Unlike Trip

**Objective**: Verify user can unlike a liked trip

**Steps**:
1. Login as User 1 (with existing like from TC001)
2. Navigate to same trip
3. Click heart icon (filled state)
4. Verify icon changes to outline state
5. Verify like count decreases by 1

**Expected Result**:
- ✅ Heart icon changes to outline state
- ✅ Like count updates immediately
- ✅ Like removed from database

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US4-TC003 - Like from Public Feed

**Objective**: Verify user can like trips from public feed

**Steps**:
1. Login as User 1
2. Navigate to public feed (`/feed`)
3. Find User 2's trip in feed
4. Click heart icon on trip card
5. Verify like count updates on card
6. Navigate to trip detail page
7. Verify like persisted (heart filled)

**Expected Result**:
- ✅ Like works from feed card
- ✅ Like count updates on card
- ✅ Like persists to detail page

**Actual Result**: _[To be filled during test execution]_

---

## Public Feed Testing

### Test Case: US5-TC001 - View Public Feed

**Objective**: Verify public feed displays all published trips

**Steps**:
1. Login as User 1
2. Navigate to `/feed`
3. Verify trips from multiple users displayed
4. Verify trips sorted by published_at (newest first)
5. Verify each card shows:
   - Cover photo
   - Title
   - Author name and avatar
   - Distance, date
   - Like and comment counts
   - Tags

**Expected Result**:
- ✅ All published trips visible
- ✅ Newest trips first
- ✅ Draft trips excluded
- ✅ Cards display complete info
- ✅ Clicking card navigates to trip detail

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US5-TC002 - Filter by Tag

**Objective**: Verify feed can be filtered by tag

**Steps**:
1. Navigate to public feed
2. Click tag "bikepacking" on a trip card
3. Verify feed filters to show only trips with "bikepacking" tag
4. Verify URL updates to `/feed?tag=bikepacking`
5. Verify filter badge appears above feed
6. Click "×" on filter badge to clear
7. Verify all trips displayed again

**Expected Result**:
- ✅ Feed filters correctly
- ✅ URL parameter updated
- ✅ Filter badge displayed
- ✅ Easy to clear filter
- ✅ No trips message if tag has 0 trips

**Actual Result**: _[To be filled during test execution]_

---

### Test Case: US5-TC003 - Feed Pagination

**Objective**: Verify feed supports infinite scroll pagination

**Steps**:
1. Navigate to public feed (with 25+ published trips)
2. Scroll to bottom of feed
3. Verify "Cargar más" button appears
4. Click button
5. Verify next 20 trips loaded
6. Verify smooth loading animation

**Expected Result**:
- ✅ First 20 trips displayed
- ✅ "Cargar más" button appears if >20 trips
- ✅ Next 20 trips load on click
- ✅ Loading spinner during fetch
- ✅ Button disappears when all trips loaded

**Actual Result**: _[To be filled during test execution]_

---

## Test Scenarios

### Scenario 1: Complete Social Interaction Flow

**Objective**: Test complete user journey from follow to comment to like

**Steps**:
1. User 1 discovers User 2's profile from feed
2. User 1 follows User 2
3. User 1 views User 2's latest trip
4. User 1 likes the trip
5. User 1 adds comment: "¡Increíble ruta!"
6. User 2 logs in and sees notification (future feature)
7. User 2 replies to comment (future feature)

**Expected Result**: Smooth, intuitive social interaction flow

---

### Scenario 2: Negative Testing - Unauthorized Actions

**Objective**: Verify proper permission checks

**Steps**:
1. User 1 tries to delete User 2's comment
2. Verify delete icon not visible
3. User 1 tries API call to delete comment (manual curl)
4. Verify 403 Forbidden error
5. User 1 tries to like same trip twice
6. Verify second like request returns 409 Conflict

**Expected Result**: All unauthorized actions properly rejected

---

## Related Documentation

- **[API Reference: Social](../../../api/endpoints/social.md)** - Social API endpoints
- **[E2E Tests](../../frontend/e2e-tests.md)** - Automated E2E tests
- **[User Guide: Social Features](../../../user-guides/social/)** - End-user guide

---

**Last Updated**: 2026-02-06 (Consolidated from specs/004-social-network/)
**Features Tested**: Follow/Unfollow, Comments, Likes, Public Feed
**Test Environment**: Local development
