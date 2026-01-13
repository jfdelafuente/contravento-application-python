# Task Breakdown: Public Trips Feed

**Feature**: 013-public-trips-feed
**Branch**: `013-public-trips-feed`
**Date**: 2026-01-13
**Status**: Ready for implementation

## Overview

This task breakdown organizes work by **user story** to enable independent, incremental delivery. Each user story can be implemented, tested, and potentially deployed separately.

**Total Tasks**: 42 tasks
**Estimated Time**: 4-6 hours total
**Parallel Opportunities**: 15 tasks can run in parallel within phases

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**User Story 1 (P1)**: Browse Public Trips Without Authentication

**Why**: This is the core value proposition - allowing anonymous users to discover cycling content. Delivers immediate value.

**Estimated**: 2-3 hours

---

### Incremental Delivery Path

1. **MVP**: User Story 1 (P1) - Public trip browsing
2. **Enhancement 1**: User Story 2 (P1) - Auth-aware header
3. **Enhancement 2**: User Story 3 (P2) - Privacy filtering (backend validation)
4. **Enhancement 3**: User Story 4 (P3) - Trip details navigation

Each increment is independently deployable and testable.

---

## Phase 1: Setup & Prerequisites

**Goal**: Initialize project structure and verify dependencies

**Duration**: 15 minutes

### Tasks

- [x] T001 Verify Feature 001, 002, 005, 008, 009 are completed and merged to develop
- [x] T002 Check database schema for `profile_visibility` field in users table (ADDED: field was missing, added to User model)
- [x] T003 Check database schema for `status` and `published_at` fields in trips table (VERIFIED: fields exist)
- [x] T004 Verify TripPhoto and TripLocation models exist from Features 008/009 (VERIFIED: models exist in trip.py)
- [x] T005 Check if database indexes exist: `idx_users_profile_visibility`, `idx_trips_public_feed` (CHECKED: created in migration)
- [x] T006 Create Alembic migration for missing indexes (if needed) in backend/migrations/versions/ (CREATED: 287f9f5c0f3a)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Set up shared infrastructure needed by all user stories

**Duration**: 30 minutes

**Test Criteria**: Database queries execute with proper indexes (<50ms)

### Backend Foundation

- [x] T007 [P] Add PublicUserSummary schema to backend/src/schemas/trip.py
- [x] T008 [P] Add PublicPhotoSummary schema to backend/src/schemas/trip.py
- [x] T009 [P] Add PublicLocationSummary schema to backend/src/schemas/trip.py
- [x] T010 Add PublicTripSummary schema to backend/src/schemas/trip.py
- [x] T011 Add PaginationInfo schema to backend/src/schemas/trip.py
- [x] T012 Add PublicTripListResponse schema to backend/src/schemas/trip.py

### Frontend Foundation

- [x] T013 [P] Add PublicUserSummary interface to frontend/src/types/trip.ts
- [x] T014 [P] Add PublicPhotoSummary interface to frontend/src/types/trip.ts
- [x] T015 [P] Add PublicLocationSummary interface to frontend/src/types/trip.ts
- [x] T016 Add PublicTripSummary interface to frontend/src/types/trip.ts
- [x] T017 Add PaginationInfo interface to frontend/src/types/trip.ts
- [x] T018 Add PublicTripListResponse interface to frontend/src/types/trip.ts

---

## Phase 3: User Story 1 - Browse Public Trips (P1) 🎯 MVP

**Priority**: P1 (Highest)
**Goal**: Anonymous users can browse published trips from public profiles
**Duration**: 2-3 hours

### Independent Test Criteria

✅ **Can test independently**: Access root URL without authentication → see list of public trips
✅ **Delivers value**: Users can discover cycling content without registration
✅ **Complete slice**: Backend API + Frontend UI + Data display

### Acceptance Scenarios

1. Anonymous user accesses homepage → sees list of published trips from public profiles
2. Each trip card shows: title, photo, location (if exists), distance, date, author
3. Page 1 shows max 20 trips, pagination works for 20+ trips
4. Empty state shows friendly message when no public trips available

### Backend Tasks (User Story 1)

- [ ] T019 [US1] Implement get_public_trips() method in backend/src/services/trip_service.py with privacy filters and eager loading
- [ ] T020 [US1] Implement count_public_trips() method in backend/src/services/trip_service.py
- [ ] T021 [US1] Add GET /trips/public endpoint to backend/src/api/trips.py with pagination parameters
- [ ] T022 [US1] Write unit tests for get_public_trips() privacy filters in backend/tests/unit/test_trip_service_public.py
- [ ] T023 [US1] Write integration tests for GET /trips/public endpoint in backend/tests/integration/test_public_feed_api.py
- [ ] T024 [US1] Write contract tests for OpenAPI schema validation in backend/tests/contract/test_public_feed_contract.py

### Frontend Tasks (User Story 1)

- [ ] T025 [P] [US1] Add getPublicTrips() method to frontend/src/services/tripService.ts
- [ ] T026 [P] [US1] Create usePublicTrips custom hook in frontend/src/hooks/usePublicTrips.ts
- [ ] T027 [P] [US1] Create PublicTripCard component in frontend/src/components/trips/PublicTripCard.tsx
- [ ] T028 [P] [US1] Create PublicTripCard CSS in frontend/src/components/trips/PublicTripCard.css
- [ ] T029 [US1] Create PublicFeedPage component in frontend/src/pages/PublicFeedPage.tsx with loading/error/empty states
- [ ] T030 [US1] Create PublicFeedPage CSS in frontend/src/pages/PublicFeedPage.css
- [ ] T031 [US1] Add route "/" to frontend/src/App.tsx for PublicFeedPage
- [ ] T032 [US1] Write unit tests for PublicTripCard in frontend/tests/unit/PublicTripCard.test.tsx
- [ ] T033 [US1] Write unit tests for usePublicTrips hook in frontend/tests/unit/usePublicTrips.test.ts
- [ ] T034 [US1] Write integration tests for PublicFeedPage in frontend/tests/integration/PublicFeedPage.test.tsx

**Dependencies**: None (uses existing models)
**Parallel Opportunities**: T025-T028 can run in parallel (different files)

---

## Phase 4: User Story 2 - Authentication Header Navigation (P1)

**Priority**: P1 (Highest)
**Goal**: Header shows login button or user profile based on auth state
**Duration**: 1 hour

### Independent Test Criteria

✅ **Can test independently**: Navigate to homepage → verify header shows correct state
✅ **Delivers value**: Users can login/logout directly from homepage
✅ **Complete slice**: Frontend component + Auth integration

### Acceptance Scenarios

1. Anonymous user sees: logo + "Iniciar sesión" button
2. Authenticated user sees: logo + photo + username + "Cerrar sesión" button
3. Click "Iniciar sesión" → redirects to /login
4. Click "Cerrar sesión" → logs out and reloads page
5. Click username/photo → redirects to user profile

### Frontend Tasks (User Story 2)

- [ ] T035 [P] [US2] Create PublicHeader component in frontend/src/components/layout/PublicHeader.tsx
- [ ] T036 [P] [US2] Create PublicHeader CSS in frontend/src/components/layout/PublicHeader.css
- [ ] T037 [US2] Integrate PublicHeader into PublicFeedPage in frontend/src/pages/PublicFeedPage.tsx
- [ ] T038 [US2] Write unit tests for PublicHeader auth states in frontend/tests/unit/PublicHeader.test.tsx

**Dependencies**: Requires User Story 1 (PublicFeedPage exists)
**Parallel Opportunities**: T035-T036 can run in parallel

---

## Phase 5: User Story 3 - Filter Trips by Privacy Settings (P2)

**Priority**: P2 (Medium)
**Goal**: Backend validates privacy filters (already implemented in US1, this adds validation)
**Duration**: 30 minutes

### Independent Test Criteria

✅ **Can test independently**: Create users with different privacy settings → verify only public trips appear
✅ **Delivers value**: Ensures privacy compliance
✅ **Complete slice**: Backend tests + Edge case validation

### Acceptance Scenarios

1. User with public profile + PUBLISHED trip → appears in feed
2. User with private profile + PUBLISHED trip → does NOT appear in feed
3. User changes profile public→private → trips disappear from feed on reload
4. DRAFT trips never appear regardless of profile visibility

### Backend Tasks (User Story 3)

- [ ] T039 [US3] Write edge case tests for privacy transitions in backend/tests/unit/test_trip_service_public.py
- [ ] T040 [US3] Write tests for DRAFT trip exclusion in backend/tests/unit/test_trip_service_public.py

**Dependencies**: Requires User Story 1 (get_public_trips exists)
**Parallel Opportunities**: None (tests only)

---

## Phase 6: User Story 4 - View Trip Details (P3)

**Priority**: P3 (Lower - Progressive Enhancement)
**Goal**: Click trip card → navigate to trip detail page
**Duration**: 15 minutes

### Independent Test Criteria

✅ **Can test independently**: Click trip card → verify navigation to detail page
✅ **Delivers value**: Users can see full trip information
✅ **Complete slice**: Frontend navigation + Event handling

### Acceptance Scenarios

1. Click trip card → navigate to /trips/{trip_id}
2. Detail page shows all trip information (description, photos, locations, tags)
3. Anonymous users see read-only view (no edit buttons)

### Frontend Tasks (User Story 4)

- [ ] T041 [US4] Add onClick navigation to PublicTripCard in frontend/src/components/trips/PublicTripCard.tsx
- [ ] T042 [US4] Write navigation tests in frontend/tests/unit/PublicTripCard.test.tsx

**Dependencies**: Requires User Story 1 (PublicTripCard exists)
**Parallel Opportunities**: None (modification of existing component)

---

## Dependencies Between User Stories

```text
Setup Phase (T001-T006)
    ↓
Foundational Phase (T007-T018)
    ↓
User Story 1 (P1) [T019-T034] ← MVP - NO DEPENDENCIES
    ↓
User Story 2 (P1) [T035-T038] ← Depends on US1 (PublicFeedPage)
    ↓
User Story 3 (P2) [T039-T040] ← Depends on US1 (get_public_trips)
    ↓
User Story 4 (P3) [T041-T042] ← Depends on US1 (PublicTripCard)
```

**Critical Path**: Setup → Foundation → US1 → US2 → US3 → US4

**Parallel Execution**: Most tasks within each user story can run in parallel (marked with [P])

---

## Parallel Execution Examples

### Foundational Phase (All parallel)

```bash
# Backend schemas (can all run simultaneously)
T007, T008, T009 → PublicUserSummary, PublicPhotoSummary, PublicLocationSummary

# Frontend types (can all run simultaneously)
T013, T014, T015 → TypeScript interfaces
```

### User Story 1 - Frontend (Parallel)

```bash
# These can all start simultaneously after T024 (backend complete)
T025 → tripService.ts (API method)
T026 → usePublicTrips.ts (hook)
T027 → PublicTripCard.tsx (component)
T028 → PublicTripCard.css (styles)

# Then T029 integrates them into PublicFeedPage
```

### User Story 2 - Frontend (Parallel)

```bash
# Component + styles in parallel
T035 → PublicHeader.tsx
T036 → PublicHeader.css
```

---

## Task Summary by Phase

| Phase | Tasks | Parallelizable | Duration |
|-------|-------|----------------|----------|
| Setup | 6 | 0 | 15 min |
| Foundation | 12 | 10 | 30 min |
| US1 (P1) | 16 | 5 | 2-3 hours |
| US2 (P1) | 4 | 2 | 1 hour |
| US3 (P2) | 2 | 0 | 30 min |
| US4 (P3) | 2 | 0 | 15 min |
| **Total** | **42** | **17** | **4-6 hours** |

---

## Verification Checklist (Per User Story)

### User Story 1 Verification

- [ ] Backend: GET /api/trips/public returns 200 with valid PublicTripListResponse
- [ ] Backend: Privacy filters work (only public profiles + PUBLISHED trips)
- [ ] Backend: Pagination works (page, limit, total, pages metadata)
- [ ] Backend: Query performance <200ms for 1000 trips
- [ ] Backend: Unit tests pass with ≥90% coverage
- [ ] Backend: Integration tests pass (API contract validation)
- [ ] Frontend: Public feed page renders at "/"
- [ ] Frontend: Trip cards display all fields (title, photo, location, distance, date, author)
- [ ] Frontend: Pagination buttons work correctly
- [ ] Frontend: Loading/error/empty states display correctly
- [ ] Frontend: Component tests pass

### User Story 2 Verification

- [ ] Frontend: Header shows "Iniciar sesión" when not authenticated
- [ ] Frontend: Header shows username + logout when authenticated
- [ ] Frontend: Login button redirects to /login
- [ ] Frontend: Logout button calls logout() and reloads page
- [ ] Frontend: Username/photo click redirects to profile
- [ ] Frontend: Component tests pass for both auth states

### User Story 3 Verification

- [ ] Backend: Private user trips do NOT appear in feed
- [ ] Backend: DRAFT trips do NOT appear in feed
- [ ] Backend: Privacy transition tests pass (public→private)
- [ ] Backend: Edge case tests pass

### User Story 4 Verification

- [ ] Frontend: Clicking trip card navigates to /trips/{trip_id}
- [ ] Frontend: Navigation tests pass

---

## Notes

### TDD Workflow Reminder

For each task:
1. Write test first (Red - test fails)
2. Implement minimal code to pass (Green - test passes)
3. Refactor while keeping tests passing

### File Path Conventions

- **Backend**: `backend/src/{layer}/{module}.py`
- **Frontend**: `frontend/src/{layer}/{component}.tsx`
- **Tests**: Mirror source structure in `tests/` directory

### Coverage Requirements

- **Backend**: ≥90% coverage required before PR merge
- **Frontend**: ≥90% coverage required before PR merge

### Commit Strategy

Commit after each user story phase completes:
- Commit 1: Setup + Foundation
- Commit 2: User Story 1 (MVP)
- Commit 3: User Story 2 (Header)
- Commit 4: User Story 3 (Privacy validation)
- Commit 5: User Story 4 (Navigation)

Use conventional commit format: `feat(public-feed): implement user story 1 - browse trips`

---

## Ready to Start

✅ All prerequisites verified
✅ Tasks organized by user story
✅ Independent test criteria defined
✅ Parallel opportunities identified
✅ MVP scope clear (User Story 1)

**Next Step**: Begin with Setup phase (T001-T006), then proceed to User Story 1 for MVP delivery.
