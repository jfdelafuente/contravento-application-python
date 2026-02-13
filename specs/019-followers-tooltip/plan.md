# Implementation Plan: Dashboard Followers/Following Tooltips

**Branch**: `019-followers-tooltip` | **Date**: 2026-02-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/019-followers-tooltip/spec.md`

## Summary

Add interactive tooltips to the dashboard's SocialStatsSection component that display a preview of followers/following user lists on hover. The feature implements progressive disclosure: show 5-8 users in a tooltip, with "Ver todos" link to full list page. Lazy loading ensures data fetches only on hover (not on dashboard load). Full keyboard navigation and WCAG 2.1 AA accessibility support included. Frontend-only implementation using existing `/users/{username}/followers` and `/users/{username}/following` API endpoints.

**Technical Approach**: Create reusable `useFollowersTooltip` hook for data fetching, `SocialStatTooltip` component for presentation, and integrate into existing `SocialStatsSection` with 500ms hover delay and 200ms leave delay to prevent accidental triggers while allowing mouse movement to tooltip.

## Technical Context

**Language/Version**: TypeScript 5 (frontend), Python 3.12 (backend - no changes)
**Primary Dependencies**: React 18, React Router 6, axios (existing), CSS custom properties (existing design system)
**Storage**: N/A (frontend-only feature, uses existing backend endpoints)
**Testing**: Vitest (unit tests), Playwright (E2E tests), axe-core (accessibility validation)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) with graceful degradation for mobile touch devices
**Project Type**: Web application (frontend changes only)
**Performance Goals**: Tooltip display <1s total (500ms hover delay + <500ms API response), smooth animations (150ms fade-in/out)
**Constraints**: <200ms API response for follower/following lists (p95), no layout shift or jank on tooltip appearance, WCAG 2.1 AA compliance
**Scale/Scope**: 3 new files (hook, component, CSS), 1 modified file (SocialStatsSection.tsx), ~400 LOC total

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability
- ✅ **TypeScript type hints**: All components and hooks use strict TypeScript with explicit types
- ✅ **Single Responsibility**: `useFollowersTooltip` handles data fetching only, `SocialStatTooltip` handles presentation only
- ✅ **No magic numbers**: All timing constants (500ms hover, 200ms leave, 150ms animation) documented with rationale
- ✅ **Clear naming**: Components/hooks follow existing patterns (use* prefix for hooks, PascalCase for components)
- ✅ **Reusable abstractions**: Tooltip component works for both followers and following (type parameter)

### II. Testing Standards (TDD Workflow)
- ✅ **TDD workflow enforced**: Tests written before implementation (Phase 2)
- ✅ **Unit tests required**:
  - `useFollowersTooltip.test.ts`: Hook behavior (data fetching, loading states, error handling)
  - `SocialStatTooltip.test.tsx`: Component rendering (empty states, user list, "Ver todos" link)
- ✅ **Integration tests required**:
  - E2E test: Hover followers card → tooltip appears with user list
  - E2E test: Click username → navigate to `/users/{username}`
  - E2E test: Click "Ver todos" → navigate to `/users/{username}/followers`
- ✅ **Contract tests**: Existing endpoints `/users/{username}/followers` and `/users/{username}/following` already have OpenAPI contracts
- ✅ **Edge cases tested**: 0 followers, network errors, long usernames, quick hover/leave
- ✅ **Coverage target**: ≥90% for new components (hook, SocialStatTooltip)

### III. User Experience Consistency
- ✅ **Spanish language**: All text ("Cargando...", "Error al cargar usuarios", "No tienes seguidores aún", "Ver todos")
- ✅ **Error handling**: Network errors show user-friendly message "Error al cargar usuarios" (no stack traces)
- ✅ **Loading states**: Spinner with "Cargando..." message during API calls
- ✅ **Empty states**: "No tienes seguidores aún" / "No sigues a nadie aún" when count is 0
- ✅ **Visual feedback**: Hover effects on username links, smooth fade-in/out animations
- ✅ **Accessibility**: Alt text on avatars, ARIA attributes (role="tooltip", aria-live="polite", aria-describedby)
- ✅ **Consistent styling**: Uses existing CSS custom properties (--surface-elevated, --border-emphasis, --accent-amber, --space-*)

### IV. Performance Requirements
- ✅ **API response time**: <500ms for follower/following lists (existing endpoints already meet this, backend returns first 50 by default)
- ✅ **Lazy loading**: Data NOT fetched on dashboard load, only on hover trigger (avoids unnecessary API calls)
- ✅ **Pagination**: Tooltip shows limited preview (5-8 users), full list accessed via separate page
- ✅ **No layout shift**: Tooltip uses `position: absolute` with `z-index: 1000`, does not affect dashboard layout
- ✅ **Optimized queries**: Backend endpoints already use eager loading for user data (no N+1 queries)
- ✅ **Memory efficiency**: Tooltip data cleared on unmount, no memory leaks from hover handlers

### Security & Data Protection
- ✅ **Authentication**: Tooltips only visible to authenticated users (dashboard requires auth)
- ✅ **Authorization**: Users can only view their own followers/following on dashboard (username from useAuth hook)
- ✅ **Input sanitization**: Usernames already sanitized by backend (no XSS risk)
- ✅ **No sensitive data**: Tooltip displays public user data only (username, profile photo URL)

### Development Workflow
- ✅ **Feature branch**: Work on `019-followers-tooltip` branch
- ✅ **Conventional commits**: Use format "feat: add followers tooltip to dashboard"
- ✅ **Documentation**: Update CLAUDE.md Active Technologies section with tooltip implementation patterns
- ✅ **Testing before merge**: All unit + E2E tests must pass

**GATE STATUS**: ✅ **PASSED** - No constitution violations, all requirements met

## Project Structure

### Documentation (this feature)

```text
specs/019-followers-tooltip/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (hover timing, accessibility patterns)
├── data-model.md        # Phase 1 output (frontend types only, no backend changes)
├── quickstart.md        # Phase 1 output (local testing instructions)
├── contracts/           # Phase 1 output (references to existing backend contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend changes only)

frontend/
├── src/
│   ├── components/
│   │   └── dashboard/
│   │       ├── SocialStatsSection.tsx          # MODIFIED: Add tooltip integration
│   │       ├── SocialStatTooltip.tsx           # NEW: Tooltip presentation component
│   │       └── SocialStatTooltip.css           # NEW: Tooltip styling
│   ├── hooks/
│   │   └── useFollowersTooltip.ts              # NEW: Data fetching hook
│   ├── services/
│   │   └── followService.ts                    # EXISTING: No changes (already has getFollowers, getFollowing)
│   └── types/
│       └── follow.ts                            # EXISTING: No changes (UserSummaryForFollow already defined)
└── tests/
    ├── unit/
    │   ├── useFollowersTooltip.test.ts         # NEW: Hook tests
    │   └── SocialStatTooltip.test.tsx          # NEW: Component tests
    └── e2e/
        └── dashboard-tooltips.spec.ts          # NEW: E2E tests for tooltip behavior

backend/
└── [NO CHANGES - uses existing endpoints]
```

**Structure Decision**: Web application (Option 2) with frontend-only changes. Backend endpoints `/users/{username}/followers` and `/users/{username}/following` already exist and return required data structure (`UserSummaryForFollow[]` with user_id, username, profile_photo_url). No database schema changes, no new API endpoints, no backend service modifications required.

## Complexity Tracking

**No violations to justify** - All constitution requirements met without exceptions.

---

## Phase 0: Research & Technical Decisions

**Objective**: Resolve unknowns and establish best practices for tooltip implementation, hover timing, accessibility, and mobile fallback.

### Research Tasks

1. **Hover Timing Best Practices**
   - Question: What is the optimal hover delay to prevent accidental tooltip triggers while maintaining responsiveness?
   - Research: Industry standards (Material Design, Bootstrap, Tailwind), UX research on tooltip timing
   - Decision target: Confirm 500ms hover delay and 200ms leave delay are appropriate

2. **Tooltip Positioning Strategy**
   - Question: How to handle tooltip overflow on small viewports and prevent layout shifts?
   - Research: CSS positioning patterns (absolute vs fixed), viewport detection, responsive breakpoints
   - Decision target: Positioning approach (centered below card with arrow, max-width constraints)

3. **Accessibility Patterns for Tooltips**
   - Question: What ARIA attributes and keyboard interactions are required for WCAG 2.1 AA compliance?
   - Research: WAI-ARIA Authoring Practices Guide (APG) for tooltips, axe-core validation rules
   - Decision target: Required ARIA attributes (role="tooltip", aria-describedby, aria-live), keyboard navigation (focus trigger, Tab through links, Escape to close)

4. **Mobile Touch Device Fallback**
   - Question: How to provide equivalent functionality on touch devices where hover doesn't exist?
   - Research: Progressive enhancement patterns, touch detection (`window.matchMedia('(hover: none)')`), mobile UX best practices
   - Decision target: Click behavior on touch devices (direct navigation to full list page vs modal)

5. **React Hook Performance Patterns**
   - Question: How to prevent memory leaks from hover handlers and optimize re-renders?
   - Research: React useCallback/useMemo patterns, cleanup in useEffect, debouncing hover events
   - Decision target: Hook implementation pattern (useCallback for fetchUsers, cleanup for timeouts)

**Output**: `research.md` with documented decisions, rationale, and alternatives considered for each research task.

---

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete

### 1. Data Model (Frontend Types)

**File**: `data-model.md`

**Entities** (TypeScript interfaces, frontend-only):

1. **FollowerPreview**
   - Purpose: Represents a preview of followers for the tooltip
   - Fields:
     - `users: UserSummaryForFollow[]` - First 5-8 followers
     - `totalCount: number` - Total follower count
     - `hasMore: boolean` - Whether "Ver todos" link should appear (totalCount > users.length)
   - Source: Derived from backend `FollowersListResponse` (slice first 8 users)

2. **FollowingPreview**
   - Purpose: Represents a preview of users being followed
   - Fields:
     - `users: UserSummaryForFollow[]` - First 5-8 following
     - `totalCount: number` - Total following count
     - `hasMore: boolean` - Whether "Ver todos" link should appear
   - Source: Derived from backend `FollowingListResponse` (slice first 8 users)

3. **UserSummaryForFollow** (EXISTING - no changes)
   - Already defined in `frontend/src/types/follow.ts`
   - Fields: `user_id`, `username`, `profile_photo_url` (nullable)

**No backend data model changes** - Feature uses existing database schema.

### 2. API Contracts

**File**: `contracts/existing-endpoints.md`

**Endpoints Used** (existing, no new contracts):

1. **GET /users/{username}/followers**
   - Existing OpenAPI contract: `specs/004-social-network/contracts/follow-api.yaml`
   - Response: `FollowersListResponse { followers: UserSummaryForFollow[], total_count: number }`
   - Tooltip usage: Fetch first 8 users only (backend returns up to 50 by default, frontend slices to 8)

2. **GET /users/{username}/following**
   - Existing OpenAPI contract: `specs/004-social-network/contracts/follow-api.yaml`
   - Response: `FollowingListResponse { following: UserSummaryForFollow[], total_count: number }`
   - Tooltip usage: Fetch first 8 users only

**No new endpoints required** - Frontend reuses existing follow endpoints.

### 3. Quickstart Guide

**File**: `quickstart.md`

**Local Development Setup**:

1. Start backend: `./run_backend.sh` (existing)
2. Start frontend: `./run_frontend.sh` (existing)
3. Create test data:
   ```bash
   # Create test users with followers
   cd backend
   poetry run python scripts/user-mgmt/create_verified_user.py --username user1 --email user1@test.com --password Test123!
   poetry run python scripts/user-mgmt/create_verified_user.py --username user2 --email user2@test.com --password Test123!
   # Follow users manually via UI or API
   ```
4. Test tooltip:
   - Navigate to http://localhost:5173/dashboard (must be logged in)
   - Hover over "Seguidores" or "Siguiendo" card for 500ms
   - Verify tooltip appears with user list

**Testing Instructions**:
- Unit tests: `cd frontend && npm run test:unit`
- E2E tests: `cd frontend && npm run test:e2e`
- Accessibility: `npm run test:a11y` (using axe-core)

### 4. Agent Context Update

Run script to update CLAUDE.md:

```bash
powershell.exe -ExecutionPolicy Bypass -File .specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

**Technologies to Add**:
- No new frameworks or libraries (uses existing React 18, TypeScript 5, axios)
- Implementation patterns to document:
  - Tooltip hover timing (500ms delay, 200ms leave)
  - Progressive disclosure pattern (preview → full list)
  - Lazy loading on hover (not on mount)
  - ARIA accessibility for tooltips

**Manual Additions to Preserve** (between markers in CLAUDE.md):
- Existing authentication patterns
- Dashboard component structure
- React Router navigation patterns

---

## Phase 2: Implementation Planning (Tasks)

**Note**: This phase is executed by `/speckit.tasks` command, NOT by `/speckit.plan`.

The tasks.md file will break down implementation into:

1. **Setup Phase**: Create new files (hook, component, CSS)
2. **Core Implementation**: Implement data fetching hook, tooltip component
3. **Integration**: Modify SocialStatsSection with hover handlers
4. **Testing**: Unit tests, E2E tests, accessibility validation
5. **Documentation**: Update CLAUDE.md with tooltip patterns

**Expected Task Count**: ~12-15 tasks (based on similar frontend features)

---

## Next Steps

1. ✅ **Phase 0 Complete**: Execute research tasks in `research.md`
2. ✅ **Phase 1 Complete**: Generate `data-model.md`, `contracts/existing-endpoints.md`, `quickstart.md`
3. ⏳ **Phase 2 Pending**: Run `/speckit.tasks` to generate task breakdown
4. ⏳ **Implementation**: Execute tasks following TDD workflow

**Command Execution Summary**:
- Branch: `019-followers-tooltip`
- Implementation Plan: `C:\My Program Files\workspace-claude\contravento-application-python\specs\019-followers-tooltip\plan.md`
- Artifacts to Generate:
  - `research.md` (Phase 0)
  - `data-model.md` (Phase 1)
  - `contracts/existing-endpoints.md` (Phase 1)
  - `quickstart.md` (Phase 1)
