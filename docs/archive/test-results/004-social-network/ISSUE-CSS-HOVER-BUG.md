# GitHub Issue: CSS Hover Bug on Like Counter

## Issue Details

**Title**: CSS: Like counter shows hover effects when like_count = 0

**Type**: Bug - Cosmetic (Low Priority)

**Feature**: 004-social-network

**Component**: LikeButton

**File**: [frontend/src/components/likes/LikeButton.css](../../frontend/src/components/likes/LikeButton.css#L82-L93)

---

## Description

The like counter displays clickable hover effects (pointer cursor, pink background) when `like_count = 0`, even though it is correctly **not clickable** in this state.

**JavaScript Behavior**: ✅ Correct - Counter does NOT open modal when clicked
**CSS Behavior**: ❌ Incorrect - Shows hover effects suggesting it's clickable

---

## Steps to Reproduce

1. Navigate to Public Feed (`/trips/public`)
2. Find a trip with `like_count = 0`
3. Hover over the like counter (shows "0")
4. Observe visual feedback

---

## Expected Behavior

When `like_count = 0`:
- Counter should have default cursor (`cursor: default`)
- No background color change on hover
- No visual feedback suggesting clickability

---

## Actual Behavior

When `like_count = 0`:
- Counter shows `cursor: pointer` on hover
- Background changes to pink/highlight on hover
- Visual appearance suggests it's clickable (but click does nothing)

---

## Root Cause

CSS class `.like-button__count--clickable:hover` is applying hover effects incorrectly.

**File**: `frontend/src/components/likes/LikeButton.css`

```css
/* Lines 82-93 */
.like-button__count--clickable:hover {
  background-color: rgba(219, 39, 119, 0.1);
  border-color: var(--color-pink);
  cursor: pointer;
  transform: scale(1.05);
}
```

The class `.like-button__count--clickable` is being applied even when `like_count = 0`.

---

## Proposed Fix

Add conditional class application based on `like_count`:

```typescript
// In LikeButton.tsx or PublicTripCard.tsx
<span
  className={`like-button__count ${like_count > 0 ? 'like-button__count--clickable' : ''}`}
  onClick={like_count > 0 ? handleCountClick : undefined}
>
  {like_count}
</span>
```

**OR** update CSS to only apply hover effects when count > 0:

```css
.like-button__count--clickable:not([data-count="0"]):hover {
  background-color: rgba(219, 39, 119, 0.1);
  border-color: var(--color-pink);
  cursor: pointer;
  transform: scale(1.05);
}
```

---

## Severity

**Low** - Cosmetic only, does not affect functionality

- Users cannot accidentally click (JavaScript prevents action)
- Only visual inconsistency between appearance and behavior
- Non-blocking for MVP release

---

## Testing Evidence

**Source**: TC-US2-008 Test Results
**Scenario**: Scenario 2 - Empty State (0 Likes)
**Status**: PARTIAL PASS

**Results**:
- ✅ JavaScript Behavior: Counter does NOT open modal (CORRECT)
- ❌ CSS Behavior: Shows hover effects (BUG)
- ✅ Functionality: Works as expected despite visual bug

**Test Date**: 2026-01-19
**Tester**: Manual Testing Session

---

## Related Files

- `frontend/src/components/likes/LikeButton.tsx` (component logic)
- `frontend/src/components/likes/LikeButton.css` (styles - **lines 82-93**)
- `frontend/src/components/trips/PublicTripCard.tsx` (usage in public feed)
- `specs/004-social-network/TC-US2-008_TEST_RESULTS.md` (test documentation)

---

## Acceptance Criteria

- [x] Like counter with `like_count = 0` shows NO hover effects
- [x] Like counter with `like_count > 0` shows hover effects (pointer, pink background)
- [x] Visual appearance matches clickability state
- [x] Regression testing: verify modal opens for `like_count > 0`

---

## Priority

**P3 - Low Priority** (cosmetic fix for next sprint)

**Recommendation**: Address in next sprint after completing remaining TC-US2-008 scenarios (5-16)

---

## Labels

- `bug`
- `css`
- `cosmetic`
- `low-priority`
- `feature-004-social-network`
- `good-first-issue`

---

## Assignee

Unassigned

---

## Milestone

Feature 004 - Social Network (Phase 2: Like Button & Likes List)

---

## Related Issues

None

---

## Screenshots

*(Add screenshots showing hover effect on 0-count like counter)*

---

**Created**: 2026-01-19
**Last Updated**: 2026-01-19
**Status**: ✅ FIXED & VERIFIED

---

## Fix Applied

**Date**: 2026-01-19
**File**: `frontend/src/components/likes/LikeButton.css` (lines 75-86)

**Solution Implemented**: Opción A - `pointer-events: none` for non-clickable counters

**CSS Changes**:
```css
/* Count */
.like-button__count {
  font-weight: 500;
  min-width: 1.5rem;
  text-align: center;
  color: inherit; /* Asegurar herencia por defecto */
}

/* Non-clickable count (when likeCount = 0) - Fix for CSS hover bug */
.like-button__count:not(.like-button__count--clickable) {
  color: currentColor; /* Mantener color heredado del padre */
  pointer-events: none; /* Prevenir cualquier interacción visual */
}
```

**How it works**:
- Selector targets counters WITHOUT `--clickable` class (i.e., `likeCount = 0`)
- `pointer-events: none` disables ALL mouse interactions (hover, click, cursor change)
- Does NOT affect counters WITH `--clickable` class (`likeCount > 0`)

**Testing**: See `CSS-HOVER-BUG-FIX-TESTING.md` for manual testing guide
