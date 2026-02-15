# Quickstart Guide: Dashboard Followers/Following Tooltips

**Feature**: 019-followers-tooltip
**Date**: 2026-02-13
**Target Audience**: Developers implementing/testing Feature 019

## Overview

This guide provides step-by-step instructions for setting up a local development environment to implement and test the Dashboard Followers/Following Tooltips feature.

---

## Prerequisites

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ PostgreSQL or SQLite database configured
- ✅ At least 2 test users created with follow relationships
- ✅ Authenticated user with followers/following for testing

---

## Quick Setup (5 Minutes)

### 1. Start Backend Server

```bash
# Navigate to project root
cd /path/to/contravento-application-python

# Start backend (choose one method):

# Option A: Using run script (recommended)
./run_backend.sh                    # Linux/Mac
.\run_backend.ps1                   # Windows PowerShell

# Option B: Manual startup
cd backend
poetry install
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Open http://localhost:8000/docs (FastAPI Swagger UI should load)

---

### 2. Start Frontend Server

```bash
# Open NEW terminal (keep backend running)

# Navigate to project root
cd /path/to/contravento-application-python

# Start frontend (choose one method):

# Option A: Using run script (recommended)
./run_frontend.sh                   # Linux/Mac
.\run_frontend.ps1                  # Windows PowerShell

# Option B: Manual startup
cd frontend
npm install
npm run dev
```

**Verify**: Open http://localhost:5173 (ContraVento homepage should load)

---

### 3. Create Test Users with Followers

```bash
# Open NEW terminal (keep backend + frontend running)

cd backend

# Create test user 1 (who will have followers)
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username maria_garcia \
  --email maria@test.com \
  --password TestPass123!

# Create test user 2 (follower)
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username juan_perez \
  --email juan@test.com \
  --password TestPass123!

# Create test user 3 (follower)
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username ana_lopez \
  --email ana@test.com \
  --password TestPass123!

# Create test user 4 (follower)
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username carlos_ruiz \
  --email carlos@test.com \
  --password TestPass123!

# Create test user 5 (follower)
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username laura_martin \
  --email laura@test.com \
  --password TestPass123!
```

---

### 4. Create Follow Relationships

**Option A: Via Frontend UI** (recommended for realistic testing)

1. Open http://localhost:5173
2. Login as `juan_perez` (password: `TestPass123!`)
3. Navigate to `/users/maria_garcia` profile
4. Click "Seguir" button
5. Logout
6. Repeat for `ana_lopez`, `carlos_ruiz`, `laura_martin` (all follow `maria_garcia`)

**Option B: Via API** (faster for bulk creation)

```bash
# Get JWT tokens for users
# (Login via UI or use scripts to obtain tokens)

# Follow maria_garcia from juan_perez account
curl -X POST http://localhost:8000/users/maria_garcia/follow \
  -H "Authorization: Bearer <juan_token>" \
  -H "Content-Type: application/json"

# Follow maria_garcia from ana_lopez account
curl -X POST http://localhost:8000/users/maria_garcia/follow \
  -H "Authorization: Bearer <ana_token>" \
  -H "Content-Type: application/json"

# Repeat for carlos_ruiz and laura_martin...
```

**Verify**:
- Login as `maria_garcia`
- Navigate to http://localhost:5173/dashboard
- Dashboard should show "Seguidores: 4" and "Siguiendo: 0"

---

## Test Tooltip Feature

### 5. Verify Followers Tooltip

1. **Login** as `maria_garcia` (http://localhost:5173/login)
2. **Navigate** to Dashboard (http://localhost:5173/dashboard)
3. **Hover** over "Seguidores" card (4 followers) for 500ms
4. **Expected Behavior**:
   - ✅ Tooltip appears below card with smooth fade-in (150ms)
   - ✅ Shows first 4 followers: juan_perez, ana_lopez, carlos_ruiz, laura_martin
   - ✅ Each user shows avatar (or placeholder if no photo) + username
   - ✅ NO "Ver todos" link (total_count = 4, shown = 4, no remaining)
5. **Move mouse away** from card
6. **Expected Behavior**:
   - ✅ Tooltip disappears after 200ms delay with fade-out (150ms)

---

### 6. Verify Following Tooltip

1. **Still logged in** as `maria_garcia`
2. **Follow another user** (e.g., follow `juan_perez` back)
   - Navigate to `/users/juan_perez`
   - Click "Seguir" button
3. **Return to Dashboard** (http://localhost:5173/dashboard)
4. **Hover** over "Siguiendo" card (1 following) for 500ms
5. **Expected Behavior**:
   - ✅ Tooltip appears with "Siguiendo" title
   - ✅ Shows 1 user: juan_perez
   - ✅ NO "Ver todos" link (total_count = 1, shown = 1)

---

### 7. Test "Ver todos" Link (Requires 9+ Followers)

**Create More Test Users**:

```bash
cd backend

# Create users 6-10
for i in {6..10}; do
  poetry run python scripts/user-mgmt/create_verified_user.py \
    --username "user${i}" \
    --email "user${i}@test.com" \
    --password "TestPass123!"
done
```

**Make Them Follow maria_garcia** (via UI or API)

**Test Tooltip**:
1. Refresh Dashboard (http://localhost:5173/dashboard)
2. Hover over "Seguidores" card (9+ followers)
3. **Expected Behavior**:
   - ✅ Tooltip shows first 8 users only
   - ✅ Shows "+ 1 más · Ver todos" link (if 9 total: 9 - 8 = 1)
   - ✅ Link navigates to `/users/maria_garcia/followers` when clicked

---

## Test Edge Cases

### 8. Empty State (0 Followers)

1. **Create fresh test user**:
   ```bash
   cd backend
   poetry run python scripts/user-mgmt/create_verified_user.py \
     --username lonely_user \
     --email lonely@test.com \
     --password TestPass123!
   ```
2. **Login** as `lonely_user`
3. **Navigate** to Dashboard
4. **Hover** over "Seguidores" card (0 followers)
5. **Expected Behavior**:
   - ✅ Tooltip appears with "No tienes seguidores aún" message
   - ✅ NO user list
   - ✅ NO "Ver todos" link

---

### 9. Loading State

1. **Throttle network** in browser DevTools (Slow 3G)
   - Open DevTools → Network tab → Throttling dropdown → Slow 3G
2. **Hover** over "Seguidores" card
3. **Expected Behavior** (within 500ms):
   - ✅ Tooltip appears immediately after 500ms hover delay
   - ✅ Shows loading spinner with "Cargando..." message
   - ✅ After API response (1-2s on Slow 3G), loading state replaced with user list

---

### 10. Error State (Network Failure)

1. **Stop backend server** (Ctrl+C in backend terminal)
2. **Hover** over "Seguidores" card on dashboard
3. **Expected Behavior**:
   - ✅ Tooltip appears after 500ms
   - ✅ Shows "Cargando..." briefly
   - ✅ Shows "Error al cargar usuarios" message after network failure
   - ✅ NO crash, graceful error handling

**Restart backend** after test:
```bash
./run_backend.sh  # or .\run_backend.ps1 on Windows
```

---

## Test Accessibility

### 11. Keyboard Navigation

1. **Close all tooltips** (move mouse away)
2. **Press Tab** key repeatedly to navigate through dashboard
3. **Expected Behavior**:
   - ✅ Focus moves to "Seguidores" card (visible focus indicator)
   - ✅ Tooltip appears after 500ms (same as hover)
   - ✅ Press Tab again → focus moves to first username link in tooltip
   - ✅ Press Tab again → focus moves to second username link
   - ✅ Press Escape → tooltip closes immediately
4. **Verify ARIA attributes** in browser DevTools:
   - ✅ Tooltip has `role="tooltip"`
   - ✅ Card has `aria-describedby` pointing to tooltip ID
   - ✅ Loading state has `aria-live="polite"`

---

### 12. Screen Reader Testing (Optional)

**Tools**: NVDA (Windows), JAWS (Windows), VoiceOver (Mac)

1. **Enable screen reader**
2. **Tab to "Seguidores" card**
3. **Expected Announcements**:
   - ✅ "Seguidores, 4, tarjeta" (card role and count)
   - ✅ "Cargando..." (when tooltip loading)
   - ✅ "Juan Perez, enlace" (first user in tooltip)
   - ✅ "Ver todos, enlace" (if "Ver todos" link present)

---

## Test Mobile Touch Devices

### 13. Touch Device Fallback

**Simulate Touch Device** in Chrome DevTools:
1. Open DevTools → Toggle device toolbar (Ctrl+Shift+M)
2. Select "iPhone 12 Pro" or "iPad Air"
3. Refresh page

**Test Tap Behavior**:
1. **Tap** on "Seguidores" card (single tap)
2. **Expected Behavior**:
   - ✅ NO tooltip appears (hover doesn't exist on touch devices)
   - ✅ Navigates directly to `/users/maria_garcia/followers` page
   - ✅ Shows full list with pagination

**Implementation**: Detected via `window.matchMedia('(hover: none)')` in React component

---

## Test Performance

### 14. Verify Lazy Loading

1. **Open DevTools** → Network tab
2. **Navigate** to Dashboard (http://localhost:5173/dashboard)
3. **Do NOT hover** over social stat cards
4. **Expected Behavior**:
   - ✅ NO API calls to `/users/maria_garcia/followers` on page load
   - ✅ NO API calls to `/users/maria_garcia/following` on page load
5. **Hover** over "Seguidores" card
6. **Expected Behavior**:
   - ✅ API call to `/users/maria_garcia/followers` appears in Network tab
   - ✅ Request sent AFTER 500ms hover delay
   - ✅ Response time < 200ms (p95 target)

---

### 15. Verify No Layout Shift

1. **Open DevTools** → Performance tab
2. **Start recording**
3. **Hover** over "Seguidores" card
4. **Stop recording** after tooltip appears
5. **Check Layout Shifts** in Performance timeline:
   - ✅ CLS (Cumulative Layout Shift) = 0
   - ✅ NO elements on page shift position when tooltip appears
   - ✅ Tooltip uses `position: absolute` (does not affect layout)

---

## Run Automated Tests

### 16. Unit Tests (Vitest)

```bash
cd frontend

# Run all unit tests
npm run test:unit

# Run specific test file
npm run test:unit -- useFollowersTooltip.test.ts

# Run with coverage
npm run test:coverage

# Expected: ≥90% coverage for new files
#   - useFollowersTooltip.ts
#   - SocialStatTooltip.tsx
```

**Test Files** (to be created in implementation):
- `frontend/tests/unit/useFollowersTooltip.test.ts`
- `frontend/tests/unit/SocialStatTooltip.test.tsx`

---

### 17. E2E Tests (Playwright)

```bash
cd frontend

# Run E2E tests
npm run test:e2e

# Run specific test file
npm run test:e2e -- dashboard-tooltips.spec.ts

# Run with UI mode (visual debugging)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed
```

**Test File** (to be created in implementation):
- `frontend/tests/e2e/dashboard-tooltips.spec.ts`

**Test Scenarios**:
1. ✅ Hover followers card → tooltip appears with user list
2. ✅ Click username → navigate to user profile
3. ✅ Click "Ver todos" → navigate to full list page
4. ✅ Quick hover → no tooltip (< 500ms)
5. ✅ Mouse leave → tooltip disappears after 200ms

---

### 18. Accessibility Tests (axe-core)

```bash
cd frontend

# Run accessibility tests (if configured)
npm run test:a11y

# Or use browser extension
# - Install axe DevTools extension in Chrome
# - Navigate to http://localhost:5173/dashboard
# - Hover over tooltip
# - Run axe scan
# - Expected: 0 violations, WCAG 2.1 AA compliant
```

**Manual Checks**:
- ✅ Tooltip has `role="tooltip"`
- ✅ Card has `aria-describedby="followers-tooltip"` when tooltip visible
- ✅ Loading state has `aria-live="polite"`
- ✅ All links have accessible names (username text)
- ✅ Color contrast ≥4.5:1 (text), ≥3:1 (UI components)
- ✅ Focus indicators visible (2px outline)

---

## Troubleshooting

### Tooltip Not Appearing

**Symptoms**: Hover over card, tooltip doesn't show

**Checks**:
1. ✅ Are you hovering for at least 500ms? (move slowly)
2. ✅ Is JavaScript running? (check browser console for errors)
3. ✅ Is backend running? (verify http://localhost:8000/docs loads)
4. ✅ Are you logged in? (dashboard requires authentication)
5. ✅ Does user have followers? (check dashboard counter)

**Solution**: Check browser console for errors, verify network requests in DevTools

---

### Tooltip Shows "Error al cargar usuarios"

**Symptoms**: Tooltip appears but shows error message

**Checks**:
1. ✅ Is backend running on http://localhost:8000?
2. ✅ Is user authenticated? (valid JWT token)
3. ✅ Does endpoint exist? (test in Swagger: http://localhost:8000/docs)
4. ✅ Is database accessible? (check backend logs)

**Solution**:
```bash
# Test endpoint manually
curl http://localhost:8000/users/maria_garcia/followers \
  -H "Authorization: Bearer <token>"

# Check backend logs
# (backend terminal should show request logs)
```

---

### Tooltip Triggers Too Easily

**Symptoms**: Tooltip appears when just moving mouse across dashboard

**Cause**: Hover delay < 500ms (implementation bug)

**Solution**: Verify `setTimeout` delay is exactly 500ms in `SocialStatsSection.tsx`:
```typescript
const timeout = setTimeout(() => {
  setActiveTooltip(type);
  // ...
}, 500); // Must be 500ms, not 0 or 100
```

---

### Tooltip Doesn't Stay Open When Moving Mouse to It

**Symptoms**: Tooltip disappears when trying to click username links

**Cause**: Leave delay < 200ms or missing pointer-events CSS

**Solution**:
1. Verify leave delay is 200ms:
   ```typescript
   const timeout = setTimeout(() => {
     setActiveTooltip(null);
   }, 200); // Must be 200ms
   ```
2. Verify tooltip CSS allows pointer events:
   ```css
   .social-stat-tooltip {
     pointer-events: auto; /* NOT 'none' */
   }
   ```

---

### Follow Relationships Not Saving

**Symptoms**: User follows someone, but follower count stays 0

**Checks**:
1. ✅ Is backend database persisting data? (SQLite file exists, PostgreSQL running)
2. ✅ Is follow API returning 200 OK? (check Network tab)
3. ✅ Is dashboard refreshing after follow? (may need manual refresh)

**Solution**:
```bash
# Check database directly
cd backend
poetry run python -c "from src.database import SessionLocal; from src.models import Follow; db = SessionLocal(); print(db.query(Follow).count()); db.close()"

# Should return > 0 if follows exist
```

---

## Development Workflow

### Iterative Development Loop

1. **Write test** (TDD - test first):
   ```bash
   cd frontend
   npm run test:unit -- useFollowersTooltip.test.ts
   # Test fails (RED)
   ```

2. **Implement feature**:
   - Create `useFollowersTooltip.ts`
   - Add data fetching logic

3. **Run test again**:
   ```bash
   npm run test:unit -- useFollowersTooltip.test.ts
   # Test passes (GREEN)
   ```

4. **Refactor**:
   - Optimize with useCallback
   - Add cleanup in useEffect

5. **Manual test** in browser:
   - Navigate to http://localhost:5173/dashboard
   - Hover over card
   - Verify tooltip works

6. **Commit** with conventional commit format:
   ```bash
   git add frontend/src/hooks/useFollowersTooltip.ts
   git commit -m "feat: add useFollowersTooltip hook for lazy data fetching

   - Implements 500ms hover delay before fetch
   - Slices first 8 users for tooltip preview
   - Handles loading, error, and empty states
   - Includes cleanup to prevent memory leaks

   Refs: FR-003, FR-012, FR-013, FR-014

   Co-Authored-By: Claude (claude-sonnet-4-5) <noreply@anthropic.com>"
   ```

---

## Next Steps After Quickstart

1. ✅ **Read Spec**: [specs/019-followers-tooltip/spec.md](spec.md) - User stories and requirements
2. ✅ **Read Plan**: [specs/019-followers-tooltip/plan.md](plan.md) - Implementation approach
3. ✅ **Read Research**: [specs/019-followers-tooltip/research.md](research.md) - Technical decisions
4. ✅ **Read Data Model**: [specs/019-followers-tooltip/data-model.md](data-model.md) - TypeScript types
5. ✅ **Generate Tasks**: Run `/speckit.tasks` to create task breakdown
6. ✅ **Start Implementation**: Follow TDD workflow (test → implement → refactor → commit)

---

## Useful Commands Reference

### Backend

```bash
# Start server
./run_backend.sh                           # Linux/Mac
.\run_backend.ps1                          # Windows

# Create test user
cd backend
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username testuser --email test@test.com --password Pass123!

# Run backend tests
poetry run pytest

# Run specific test
poetry run pytest tests/unit/test_follow_service.py
```

### Frontend

```bash
# Start server
./run_frontend.sh                          # Linux/Mac
.\run_frontend.ps1                         # Windows

# Install dependencies
cd frontend
npm install

# Run unit tests
npm run test:unit

# Run E2E tests
npm run test:e2e

# Run accessibility tests
npm run test:a11y

# Type check
npm run type-check

# Lint
npm run lint
```

---

**Last Updated**: 2026-02-13
**Time to Complete Quickstart**: ~15 minutes (including test user creation)
**Prerequisites**: Backend + Frontend running, ≥2 test users with follow relationships
