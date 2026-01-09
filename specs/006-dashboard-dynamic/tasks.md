---

description: "Task list for Feature 006: Dashboard Dinámico implementation"
---

# Tasks: Feature 006 - Dashboard Dinámico

**Input**: Design documents from `/specs/006-dashboard-dynamic/`
**Prerequisites**: plan.md, spec.md

**Tests**: Not explicitly requested in specification - focusing on implementation

**Organization**: Tasks are grouped by functional requirement (user story) to enable independent implementation and testing of each feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which functional requirement this task belongs to (e.g., FR1, FR2, FR3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `frontend/src/` for React/TypeScript frontend
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for dashboard feature

- [ ] T001 [P] Create types directory structure in frontend/src/types/ (stats.ts, trip.ts, activity.ts)
- [ ] T002 [P] Create services directory structure in frontend/src/services/ (statsService.ts, tripsService.ts, activityService.ts)
- [ ] T003 [P] Create dashboard components directory in frontend/src/components/dashboard/
- [ ] T004 [P] Create common components directory in frontend/src/components/common/
- [ ] T005 [P] Create utils directory with formatters in frontend/src/utils/formatters.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core types, services, and utilities that multiple features depend on

**⚠️ CRITICAL**: No feature work can begin until this phase is complete

- [ ] T006 [P] Define UserStats interface in frontend/src/types/stats.ts
- [ ] T007 [P] Define Trip interface in frontend/src/types/trip.ts
- [ ] T008 [P] Define Activity interface in frontend/src/types/activity.ts
- [ ] T009 [P] Implement number formatter (formatStatNumber) in frontend/src/utils/formatters.ts
- [ ] T010 [P] Implement distance formatter (formatDistance) in frontend/src/utils/formatters.ts
- [ ] T011 [P] Implement date formatter (formatRelativeTime) in frontend/src/utils/formatters.ts
- [ ] T012 [P] Implement countries formatter (formatCountries) in frontend/src/utils/formatters.ts
- [ ] T013 Create SkeletonLoader component in frontend/src/components/common/SkeletonLoader.tsx
- [ ] T014 Create SkeletonLoader styles in frontend/src/components/common/SkeletonLoader.css

**Checkpoint**: Foundation ready - feature implementation can now begin in parallel

---

## Phase 3: FR-001 Stats Cards (Priority: High) 🎯 MVP

**Goal**: Display 4 stats cards (trips, distance, countries, followers) with real backend data

**Independent Test**:
1. Login to dashboard
2. Verify 4 stats cards display with correct data from /api/stats/me
3. Verify loading skeletons appear during data fetch
4. Verify error state if API fails
5. Verify responsive layout (2x2 desktop, 1 column mobile)

### Implementation for FR-001

- [ ] T015 [P] [FR1] Create StatCardData interface in frontend/src/types/stats.ts
- [ ] T016 [P] [FR1] Implement getMyStats API call in frontend/src/services/statsService.ts
- [ ] T017 [P] [FR1] Create useStats custom hook in frontend/src/hooks/useStats.ts
- [ ] T018 [FR1] Create StatsCard component in frontend/src/components/dashboard/StatsCard.tsx
- [ ] T019 [FR1] Create StatsCard styles with rustic design in frontend/src/components/dashboard/StatsCard.css
- [ ] T020 [FR1] Add loading skeleton state to StatsCard component
- [ ] T021 [FR1] Add error state to StatsCard component
- [ ] T022 [FR1] Create StatsSection component in frontend/src/components/dashboard/StatsSection.tsx
- [ ] T023 [FR1] Create StatsSection styles with responsive grid in frontend/src/components/dashboard/StatsSection.css
- [ ] T024 [FR1] Integrate StatsSection into DashboardPage in frontend/src/pages/DashboardPage.tsx
- [ ] T025 [FR1] Update DashboardPage styles in frontend/src/pages/DashboardPage.css

**Checkpoint**: Stats cards fully functional with real data, loading states, error handling, and responsive design

---

## Phase 4: FR-002 Recent Trips Section (Priority: High)

**Goal**: Display last 3-5 published trips with photos, titles, dates, distances, tags

**Independent Test**:
1. Login to dashboard
2. Verify recent trips section shows up to 5 trips
3. Verify each trip card shows photo, title, date, distance, tags
4. Verify "Ver todos los viajes" button navigates correctly
5. Verify empty state if no trips: "Aún no has publicado viajes"
6. Verify skeleton loader during data fetch

### Implementation for FR-002

- [ ] T026 [P] [FR2] Create TripSummary interface in frontend/src/types/trip.ts
- [ ] T027 [P] [FR2] Implement getUserTrips API call in frontend/src/services/tripsService.ts
- [ ] T028 [P] [FR2] Create useRecentTrips custom hook in frontend/src/hooks/useRecentTrips.ts
- [ ] T029 [FR2] Create RecentTripCard component in frontend/src/components/dashboard/RecentTripCard.tsx
- [ ] T030 [FR2] Create RecentTripCard styles with rustic design in frontend/src/components/dashboard/RecentTripCard.css
- [ ] T031 [FR2] Add lazy loading for trip images in RecentTripCard component
- [ ] T032 [FR2] Add photo placeholder for trips without photos
- [ ] T033 [FR2] Create RecentTripsSection component in frontend/src/components/dashboard/RecentTripsSection.tsx
- [ ] T034 [FR2] Create RecentTripsSection styles in frontend/src/components/dashboard/RecentTripsSection.css
- [ ] T035 [FR2] Add empty state component for no trips in RecentTripsSection
- [ ] T036 [FR2] Add skeleton loader for trip cards in RecentTripsSection
- [ ] T037 [FR2] Integrate RecentTripsSection into DashboardPage in frontend/src/pages/DashboardPage.tsx

**Checkpoint**: Recent trips section fully functional with photo loading, empty states, and navigation

---

## Phase 5: FR-004 Quick Actions (Priority: High)

**Goal**: Provide 3-4 quick action buttons for common user tasks

**Independent Test**:
1. Login to dashboard
2. Verify 4 quick action buttons display
3. Verify "Crear Viaje" navigates to /trips/new
4. Verify "Ver Perfil" navigates to /profile
5. Verify "Explorar Viajes" navigates to /explore
6. Verify "Editar Perfil" navigates to /profile/edit
7. Verify responsive layout (2x2 grid on mobile)

### Implementation for FR-004

- [ ] T038 [P] [FR4] Create QuickActionButtonProps interface in frontend/src/components/dashboard/QuickActionButton.tsx
- [ ] T039 [FR4] Create QuickActionButton component in frontend/src/components/dashboard/QuickActionButton.tsx
- [ ] T040 [FR4] Create QuickActionButton styles with rustic design in frontend/src/components/dashboard/QuickActionButton.css
- [ ] T041 [FR4] Create QuickActionsSection component in frontend/src/components/dashboard/QuickActionsSection.tsx
- [ ] T042 [FR4] Create QuickActionsSection styles with responsive grid in frontend/src/components/dashboard/QuickActionsSection.css
- [ ] T043 [FR4] Define 4 quick actions with icons and navigation targets in QuickActionsSection
- [ ] T044 [FR4] Integrate QuickActionsSection into DashboardPage in frontend/src/pages/DashboardPage.tsx

**Checkpoint**: Quick actions fully functional with proper navigation and responsive design

---

## Phase 6: FR-005 Welcome Banner (Priority: Low)

**Goal**: Display personalized welcome banner with contextual greeting and user info

**Independent Test**:
1. Login to dashboard at different times of day
2. Verify contextual greeting: "Buenos días", "Buenas tardes", "Buenas noches"
3. Verify personalized message: "¡Bienvenido de vuelta, {username}!"
4. Verify user avatar or initial displays
5. Verify verified badge if user is verified
6. Verify slideDown animation on page load

### Implementation for FR-005

- [ ] T045 [P] [FR5] Create getTimeOfDayGreeting utility in frontend/src/utils/formatters.ts
- [ ] T046 [FR5] Create WelcomeBanner component in frontend/src/components/dashboard/WelcomeBanner.tsx
- [ ] T047 [FR5] Create WelcomeBanner styles with rustic design and slideDown animation in frontend/src/components/dashboard/WelcomeBanner.css
- [ ] T048 [FR5] Add user avatar with fallback to initial in WelcomeBanner
- [ ] T049 [FR5] Add verified badge display logic in WelcomeBanner
- [ ] T050 [FR5] Integrate WelcomeBanner into DashboardPage in frontend/src/pages/DashboardPage.tsx

**Checkpoint**: Welcome banner fully functional with contextual greetings and user personalization

---

## Phase 7: FR-003 Activity Feed (Priority: Medium) - OPTIONAL

**Goal**: Display timeline of recent activities (trips published, photos uploaded, new followers, badges)

**Independent Test**:
1. Login to dashboard
2. Verify activity feed shows last 5-10 activities
3. Verify different activity types display with appropriate icons
4. Verify relative timestamps ("hace 2 horas")
5. Verify activity items link to relevant content
6. Verify empty state: "No hay actividad reciente"

**NOTE**: This phase requires new backend API endpoint /api/activity/me - marked as optional for MVP

### Implementation for FR-003 (OPTIONAL)

- [ ] T051 [P] [FR3] Define Activity interface in frontend/src/types/activity.ts
- [ ] T052 [P] [FR3] Implement getMyActivity API call in frontend/src/services/activityService.ts
- [ ] T053 [P] [FR3] Create useActivity custom hook in frontend/src/hooks/useActivity.ts
- [ ] T054 [FR3] Create ActivityItem component in frontend/src/components/dashboard/ActivityItem.tsx
- [ ] T055 [FR3] Create ActivityItem styles in frontend/src/components/dashboard/ActivityItem.css
- [ ] T056 [FR3] Create ActivityFeed component in frontend/src/components/dashboard/ActivityFeed.tsx
- [ ] T057 [FR3] Create ActivityFeed styles in frontend/src/components/dashboard/ActivityFeed.css
- [ ] T058 [FR3] Add empty state for no activities in ActivityFeed
- [ ] T059 [FR3] Integrate ActivityFeed into DashboardPage in frontend/src/pages/DashboardPage.tsx

**Checkpoint**: Activity feed fully functional (requires backend API implementation)

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple dashboard features

- [ ] T060 [P] Add responsive design testing for all breakpoints (640px, 768px, 1024px)
- [ ] T061 [P] Add ARIA labels for accessibility on all stats cards
- [ ] T062 [P] Add focus states for keyboard navigation on all interactive elements
- [ ] T063 [P] Verify WCAG AA color contrast across all components
- [ ] T064 [P] Add semantic HTML structure (section, article, h2-h6) to DashboardPage
- [ ] T065 [P] Optimize image loading with lazy loading and srcset
- [ ] T066 [P] Implement stats caching (5 minutes) in useStats hook
- [ ] T067 [P] Add error boundary for dashboard components
- [ ] T068 Performance testing: verify dashboard loads < 1s with cached stats
- [ ] T069 Performance testing: verify no layout shift with skeletons
- [ ] T070 [P] Document dashboard components in frontend/docs/COMPONENTS.md
- [ ] T071 Code cleanup: remove placeholder content from original DashboardPage
- [ ] T072 Code cleanup: ensure all components follow rustic design system

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all feature implementations
- **Features (Phase 3-7)**: All depend on Foundational phase completion
  - FR-001 Stats Cards (Phase 3) can start after Phase 2
  - FR-002 Recent Trips (Phase 4) can start after Phase 2
  - FR-004 Quick Actions (Phase 5) can start after Phase 2
  - FR-005 Welcome Banner (Phase 6) can start after Phase 2
  - FR-003 Activity Feed (Phase 7) can start after Phase 2 (requires backend API)
- **Polish (Phase 8)**: Depends on desired features being complete

### Functional Requirement Dependencies

- **FR-001 Stats Cards**: Can start after Foundational (Phase 2) - No dependencies on other features
- **FR-002 Recent Trips**: Can start after Foundational (Phase 2) - No dependencies on other features
- **FR-004 Quick Actions**: Can start after Foundational (Phase 2) - No dependencies on other features
- **FR-005 Welcome Banner**: Can start after Foundational (Phase 2) - Uses AuthContext (already available)
- **FR-003 Activity Feed**: Can start after Foundational (Phase 2) - REQUIRES backend API implementation

### Within Each Feature

- Types before services
- Services before hooks
- Hooks before components
- Components before integration
- Basic component before loading/error states
- Styles alongside components
- Feature complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T005) can run in parallel
- All Foundational tasks (T006-T014) can run in parallel
- Once Foundational phase completes, all features (FR-001, FR-002, FR-004, FR-005) can start in parallel
- Within each feature:
  - Types, services, hooks can be created in parallel (marked [P])
  - Component and styles can be created together
  - Different features can be worked on in parallel by different team members

---

## Parallel Example: FR-001 Stats Cards

```bash
# Launch all foundational pieces for Stats Cards together:
Task: "Create StatCardData interface in frontend/src/types/stats.ts"
Task: "Implement getMyStats API call in frontend/src/services/statsService.ts"
Task: "Create useStats custom hook in frontend/src/hooks/useStats.ts"

# Then create component and styles together:
Task: "Create StatsCard component in frontend/src/components/dashboard/StatsCard.tsx"
Task: "Create StatsCard styles in frontend/src/components/dashboard/StatsCard.css"
```

---

## Parallel Example: Multiple Features

```bash
# After Phase 2 completes, launch multiple features in parallel:
Task: "Create StatsCard component (FR-001)"
Task: "Create RecentTripCard component (FR-002)"
Task: "Create QuickActionButton component (FR-004)"
Task: "Create WelcomeBanner component (FR-005)"
```

---

## Implementation Strategy

### MVP First (FR-001 + FR-002 + FR-004)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all features)
3. Complete Phase 3: FR-001 Stats Cards (HIGHEST VALUE)
4. Complete Phase 4: FR-002 Recent Trips (HIGHEST VALUE)
5. Complete Phase 5: FR-004 Quick Actions (HIGHEST VALUE)
6. **STOP and VALIDATE**: Test core dashboard functionality
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add FR-001 Stats Cards → Test independently → Deploy/Demo (First increment!)
3. Add FR-002 Recent Trips → Test independently → Deploy/Demo
4. Add FR-004 Quick Actions → Test independently → Deploy/Demo
5. Add FR-005 Welcome Banner → Test independently → Deploy/Demo (Polish increment)
6. Add FR-003 Activity Feed → Test independently → Deploy/Demo (Optional - requires backend)
7. Each feature adds value without breaking previous features

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: FR-001 Stats Cards
   - Developer B: FR-002 Recent Trips
   - Developer C: FR-004 Quick Actions
   - Developer D: FR-005 Welcome Banner
3. Features complete and integrate independently into DashboardPage

---

## Recommended MVP Scope

**Include in MVP**:
- ✅ FR-001 Stats Cards (High priority, high value, backend ready)
- ✅ FR-002 Recent Trips (High priority, high value, backend ready)
- ✅ FR-004 Quick Actions (High priority, navigation critical)

**Add after MVP validation**:
- ⏳ FR-005 Welcome Banner (Low priority, polish feature)
- ⏳ FR-003 Activity Feed (Medium priority, requires backend API)

**Total MVP Tasks**: T001-T044 (44 tasks)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific functional requirement for traceability
- Each feature should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate feature independently
- FR-003 Activity Feed is optional and requires backend API implementation
- All components must follow rustic design system (see frontend/docs/DESIGN_SYSTEM.md)
- Backend APIs already available: /api/stats/me, /api/users/{username}/trips
- Avoid: vague tasks, same file conflicts, cross-feature dependencies that break independence
