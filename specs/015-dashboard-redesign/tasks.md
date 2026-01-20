# Tasks: Dashboard Principal Mejorado

**Input**: Design documents from `/specs/015-dashboard-redesign/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md, tailwind-setup.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Tests**: TDD approach requested in constitution - tests MUST be written BEFORE implementation for each user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Web app structure**: `frontend/src/` for React components, `backend/src/` for Python/FastAPI (backend already implemented)

---

## Phase 1: Setup (Tailwind CSS Integration)

**Purpose**: Install and configure Tailwind CSS v4 with @tailwindcss/vite for Feature 015 components

- [X] T001 Install Tailwind CSS v4 dependencies: `npm install -D tailwindcss@4.1.18 @tailwindcss/vite@4.1.18`
- [X] T002 [P] Install class utility dependencies: `npm install clsx tailwind-merge`
- [X] T003 [P] Configure Vite to use Tailwind plugin in frontend/vite.config.ts
- [X] T004 [P] Create Tailwind CSS entry point in frontend/src/index.css with @import and @theme directives
- [X] T005 [P] Create cn() utility function in frontend/src/lib/cn.ts combining clsx + tailwind-merge
- [X] T006 [P] Add TypeScript path alias for @/lib in frontend/tsconfig.json
- [X] T007 [P] Configure content paths for Tailwind purge in frontend/src/index.css (@source directive)
- [X] T008 Verify Tailwind setup with `npm run dev` - HMR should work without errors

**Checkpoint**: ✅ Tailwind CSS v4 configured - utility classes should render correctly in new components

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core types, services, and utilities that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 [P] Create TypeScript interfaces in frontend/src/types/dashboard.ts (DashboardStats, FeedItem, Route, Challenge)
- [X] T010 [P] Create TypeScript interfaces in frontend/src/types/notifications.ts (Notification, NotificationPanel)
- [X] T011 [P] Create API service module frontend/src/services/dashboardService.ts with axios client
- [X] T012 [P] Add responsive breakpoint constants in frontend/src/utils/constants.ts (MOBILE: 320px, TABLET: 768px, DESKTOP: 1024px)
- [X] T013 [P] Create useResponsiveLayout hook in frontend/src/hooks/useResponsiveLayout.ts using window.matchMedia
- [X] T014 [P] Create useDebounce hook in frontend/src/hooks/useDebounce.ts for search functionality
- [X] T015 Update existing SkeletonLoader component to use Tailwind classes (animate-pulse, bg-gray-200)

**Checkpoint**: ✅ Foundation ready - all user stories can now proceed in parallel

---

## Phase 3: User Story 1 - Vista Rápida de Estadísticas y Progreso Personal (Priority: P1) 🎯 MVP

**Goal**: Display personal cycling statistics (km traveled, towns visited, local economic impact) immediately upon dashboard access

**Independent Test**: Authenticate as user with registered trips, verify personal stats display with updated values from profile

### Tests for User Story 1 (TDD - Write FIRST) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T016 [P] [US1] E2E test for dashboard stats display in frontend/tests/e2e/dashboard-stats.spec.ts (verify stats load <1s, values match API)
- [ ] T017 [P] [US1] Unit test for useDashboardStats hook in frontend/tests/unit/hooks/useDashboardStats.test.ts (loading, error, success states)
- [ ] T018 [P] [US1] Component test for StatsOverview in frontend/tests/unit/components/StatsOverview.test.tsx (render stats, handle errors, skeleton loading)

### Implementation for User Story 1

- [X] T019 [P] [US1] Create useDashboardStats hook in frontend/src/hooks/useDashboardStats.ts (fetch stats from API, handle loading/error states)
- [X] T020 [US1] Implement getDashboardStats API call in frontend/src/services/dashboardService.ts (GET /api/v1/dashboard/stats)
- [X] T021 [US1] Create StatsOverview component in frontend/src/components/dashboard/StatsOverview.tsx using Tailwind CSS
- [X] T022 [US1] Create StatCard subcomponent in frontend/src/components/dashboard/StatCard.tsx for individual stat display
- [X] T023 [US1] Add Spanish labels and motivational messages for new users (zero stats) in StatsOverview
- [X] T024 [US1] Implement skeleton loading state for StatsOverview using SkeletonLoader with Tailwind
- [X] T025 [US1] Add error handling with retry button in StatsOverview component
- [X] T026 [US1] Create responsive grid layout (grid-cols-1 md:grid-cols-3) for stats cards

**Checkpoint**: ✅ User Story 1 implementation complete - stats display with responsive grid, loading states, and error handling

---

## Phase 4: User Story 2 - Navegación y Búsqueda Rápida (Priority: P1)

**Goal**: Provide sticky header with global search (users, routes, towns) visible during scroll

**Independent Test**: Load dashboard, scroll down, verify header stays visible and search autocomplete works from any section

### Tests for User Story 2 (TDD - Write FIRST) ⚠️

- [ ] T027 [P] [US2] E2E test for sticky header in frontend/tests/e2e/dashboard-navigation.spec.ts (header visible on scroll, logo click returns to dashboard)
- [ ] T028 [P] [US2] E2E test for global search in frontend/tests/e2e/dashboard-navigation.spec.ts (autocomplete, debounce 300ms, navigate to results)
- [ ] T029 [P] [US2] Unit test for useGlobalSearch hook in frontend/tests/unit/hooks/useGlobalSearch.test.ts (debounce, API calls, results update)
- [ ] T030 [P] [US2] Component test for GlobalSearch in frontend/tests/unit/components/GlobalSearch.test.tsx (input change, dropdown display, result click)

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create useGlobalSearch hook in frontend/src/hooks/useGlobalSearch.ts with lodash.debounce (300ms)
- [ ] T032 [US2] Implement searchGlobal API call in frontend/src/services/dashboardService.ts (GET /api/v1/dashboard/search)
- [ ] T033 [US2] Create DashboardHeader component in frontend/src/components/dashboard/DashboardHeader.tsx using Tailwind (sticky top-0 z-50)
- [ ] T034 [US2] Create GlobalSearch component in frontend/src/components/dashboard/GlobalSearch.tsx with autocomplete dropdown
- [ ] T035 [US2] Create SearchResultItem component in frontend/src/components/dashboard/SearchResultItem.tsx for individual results
- [ ] T036 [US2] Implement dropdown positioning with Tailwind (absolute, right-0, mt-2) and outside-click handling
- [ ] T037 [US2] Add Spanish placeholders and empty state messages ("Buscar rutas, usuarios, pueblos...")
- [ ] T038 [US2] Implement keyboard navigation (Arrow keys, Enter, Esc) for search results
- [ ] T039 [US2] Add logo click handler to navigate to dashboard root path
- [ ] T040 [US2] Ensure header ARIA labels and accessibility (role="banner", aria-label for search input)

**Checkpoint**: User Story 2 complete - header sticky works, search autocomplete functional, tests pass

---

## Phase 5: User Story 3 - Feed de Actividad de la Comunidad (Priority: P2)

**Goal**: Display activity feed of followed users (new trips, achievements, comments) in central dashboard section

**Independent Test**: Authenticate as user following others, verify recent activities display chronologically in feed

### Tests for User Story 3 (TDD - Write FIRST) ⚠️

- [ ] T041 [P] [US3] E2E test for activity feed in frontend/tests/e2e/dashboard-feed.spec.ts (activities load <2s, chronological order, pagination)
- [ ] T042 [P] [US3] Unit test for useActivityFeed hook in frontend/tests/unit/hooks/useActivityFeed.test.ts (pagination, loading states, refetch)
- [ ] T043 [P] [US3] Component test for ActivityFeed in frontend/tests/unit/components/ActivityFeed.test.tsx (render items, empty state, virtualization >100 items)

### Implementation for User Story 3

- [ ] T044 [P] [US3] Create useActivityFeed hook in frontend/src/hooks/useActivityFeed.ts with pagination support
- [ ] T045 [US3] Implement getActivityFeed API call in frontend/src/services/dashboardService.ts (GET /api/v1/dashboard/feed?page=1&limit=50)
- [ ] T046 [US3] Create ActivityFeed component in frontend/src/components/dashboard/ActivityFeed.tsx
- [ ] T047 [US3] Create ActivityFeedItem component in frontend/src/components/dashboard/ActivityFeedItem.tsx for individual activity entries
- [ ] T048 [US3] Add date-fns formatting for timestamps (formatDistanceToNow with Spanish locale: "hace 5 minutos")
- [ ] T049 [US3] Implement conditional virtualization using react-window for lists >100 items
- [ ] T050 [US3] Add empty state message and follow suggestions for users following nobody
- [ ] T051 [US3] Implement infinite scroll or "Load More" button for pagination
- [ ] T052 [US3] Add activity type icons and contextual info (who, what, when) using Tailwind classes
- [ ] T053 [US3] Ensure activity links navigate to correct pages (trip detail, user profile)

**Checkpoint**: User Story 3 complete - feed displays activities, pagination works, <2s load time for 50 items verified

---

## Phase 6: User Story 8 - Métricas Sociales (Priority: P2)

**Goal**: Display follower/following counts in dashboard, update in real-time when user follows/unfollows

**Independent Test**: Verify follower/following counts match profile, follow a user, confirm metrics update immediately

### Tests for User Story 8 (TDD - Write FIRST) ⚠️

- [ ] T054 [P] [US8] E2E test for social metrics in frontend/tests/e2e/dashboard-stats.spec.ts (counters display, click navigates to follower/following lists)
- [ ] T055 [P] [US8] Unit test for social metrics in StatsOverview.test.tsx (verify metrics render from DashboardStats)

### Implementation for User Story 8

- [ ] T056 [US8] Add follower_count and following_count to DashboardStats interface in frontend/src/types/dashboard.ts
- [ ] T057 [US8] Create SocialMetrics component in frontend/src/components/dashboard/SocialMetrics.tsx displaying follower/following counts
- [ ] T058 [US8] Integrate SocialMetrics into StatsOverview component with Tailwind styling
- [ ] T059 [US8] Add click handlers to navigate to follower/following list pages
- [ ] T060 [US8] Ensure Spanish labels ("Seguidores", "Siguiendo") with accessibility attributes

**Checkpoint**: User Story 8 complete - social metrics display, click navigation works, counts accurate

---

## Phase 7: User Story 4 - Rutas Sugeridas y Descubrimiento (Priority: P2)

**Goal**: Suggest personalized routes based on location, cycling preferences, and unvisited towns

**Independent Test**: Authenticate as user with location and cycling type set, verify at least 3 relevant route suggestions appear

### Tests for User Story 4 (TDD - Write FIRST) ⚠️

- [ ] T061 [P] [US4] E2E test for suggested routes in frontend/tests/e2e/dashboard-routes.spec.ts (routes display, click navigates to route detail)
- [ ] T062 [P] [US4] Unit test for useSuggestedRoutes hook in frontend/tests/unit/hooks/useSuggestedRoutes.test.ts (loading, error, routes data)
- [ ] T063 [P] [US4] Component test for SuggestedRoutes in frontend/tests/unit/components/SuggestedRoutes.test.tsx (render route cards, empty state)

### Implementation for User Story 4

- [ ] T064 [P] [US4] Create useSuggestedRoutes hook in frontend/src/hooks/useSuggestedRoutes.ts
- [ ] T065 [US4] Implement getSuggestedRoutes API call in frontend/src/services/dashboardService.ts (GET /api/v1/dashboard/suggested-routes?limit=5)
- [ ] T066 [US4] Create SuggestedRoutes component in frontend/src/components/dashboard/SuggestedRoutes.tsx
- [ ] T067 [US4] Create RouteCard component in frontend/src/components/dashboard/RouteCard.tsx displaying route details (distance, difficulty, rating)
- [ ] T068 [US4] Add route cover photo with lazy loading (loading="lazy" attribute)
- [ ] T069 [US4] Display personalization reason ("Incluye 3 pueblos que no has visitado") in RouteCard
- [ ] T070 [US4] Add Spanish difficulty labels ("Fácil", "Moderado", "Difícil", "Experto") with Tailwind badges
- [ ] T071 [US4] Handle empty state when no routes available (show popular routes as fallback)
- [ ] T072 [US4] Ensure route cards link to route detail page

**Checkpoint**: User Story 4 complete - route suggestions display, personalization works, empty state handled

---

## Phase 8: User Story 5 - Desafíos Activos y Progreso (Priority: P3)

**Goal**: Display active challenges with visual progress bars and completion status

**Independent Test**: Authenticate as user enrolled in challenges, verify progress bars show accurate completion (e.g., "3/5 comercios visitados")

### Tests for User Story 5 (TDD - Write FIRST) ⚠️

- [ ] T073 [P] [US5] E2E test for active challenges in frontend/tests/e2e/dashboard-challenges.spec.ts (challenges display, progress accurate, completion notification)
- [ ] T074 [P] [US5] Unit test for useActiveChallenges hook in frontend/tests/unit/hooks/useActiveChallenges.test.ts
- [ ] T075 [P] [US5] Component test for ActiveChallenges in frontend/tests/unit/components/ActiveChallenges.test.tsx

### Implementation for User Story 5

- [ ] T076 [P] [US5] Create useActiveChallenges hook in frontend/src/hooks/useActiveChallenges.ts
- [ ] T077 [US5] Implement getActiveChallenges API call in frontend/src/services/dashboardService.ts (GET /api/v1/dashboard/challenges)
- [ ] T078 [US5] Create ActiveChallenges component in frontend/src/components/dashboard/ActiveChallenges.tsx
- [ ] T079 [US5] Create ChallengeProgressBar component in frontend/src/components/dashboard/ChallengeProgressBar.tsx with Tailwind progress styling
- [ ] T080 [US5] Add challenge icons and status badges ("En Progreso", "Completado", "Expirado") with Tailwind
- [ ] T081 [US5] Display reward achievement preview (badge name and icon) for incomplete challenges
- [ ] T082 [US5] Add empty state for users with no active challenges ("Explora desafíos disponibles")
- [ ] T083 [US5] Implement lazy loading for ActiveChallenges component (React.lazy + Suspense)

**Checkpoint**: User Story 5 complete - challenges display, progress bars accurate, lazy loading works

---

## Phase 9: User Story 6 - Notificaciones y Alertas (Priority: P3)

**Goal**: Display notification counter in header, show dropdown panel with recent notifications

**Independent Test**: Generate notification event (like, comment), verify counter increments and notification appears in panel

### Tests for User Story 6 (TDD - Write FIRST) ⚠️

- [ ] T084 [P] [US6] E2E test for notifications in frontend/tests/e2e/dashboard-notifications.spec.ts (counter updates, panel opens, mark as read)
- [ ] T085 [P] [US6] Unit test for useNotifications hook in frontend/tests/unit/hooks/useNotifications.test.ts (fetch, mark read, unread count)
- [ ] T086 [P] [US6] Component test for NotificationPanel in frontend/tests/unit/components/NotificationPanel.test.tsx (render notifications, dropdown behavior)

### Implementation for User Story 6

- [ ] T087 [P] [US6] Create useNotifications hook in frontend/src/hooks/useNotifications.ts (fetch notifications, mark as read)
- [ ] T088 [US6] Implement getNotifications API call in frontend/src/services/dashboardService.ts (GET /api/v1/dashboard/notifications?unread=true)
- [ ] T089 [US6] Implement markNotificationAsRead API call in frontend/src/services/dashboardService.ts (PATCH /api/v1/dashboard/notifications/{id}/read)
- [ ] T090 [US6] Create NotificationPanel component in frontend/src/components/dashboard/NotificationPanel.tsx with dropdown behavior
- [ ] T091 [US6] Create NotificationItem component in frontend/src/components/dashboard/NotificationItem.tsx for individual notifications
- [ ] T092 [US6] Add notification counter badge in DashboardHeader (show "99+" if >99 unread)
- [ ] T093 [US6] Implement outside-click to close panel using useEffect + ref
- [ ] T094 [US6] Add notification type icons (like, comment, follower, security) with Tailwind conditional colors
- [ ] T095 [US6] Highlight security alerts with different background color (bg-red-50)
- [ ] T096 [US6] Implement lazy loading for NotificationPanel component (React.lazy + Suspense)

**Checkpoint**: User Story 6 complete - notifications display, counter accurate, mark as read works

---

## Phase 10: User Story 7 - Acciones Rápidas (Priority: P3)

**Goal**: Provide quick access buttons for frequent actions (create trip, view profile, explore routes)

**Independent Test**: Click "Crear Viaje" button, verify navigation to trip creation form

### Tests for User Story 7 (TDD - Write FIRST) ⚠️

- [ ] T097 [P] [US7] E2E test for quick actions in frontend/tests/e2e/dashboard-navigation.spec.ts (buttons navigate to correct pages)

### Implementation for User Story 7

- [ ] T098 [US7] Create QuickActions component in frontend/src/components/dashboard/QuickActions.tsx with action buttons
- [ ] T099 [US7] Add Spanish labels for actions ("Crear Viaje", "Ver Perfil", "Explorar Rutas") with icons
- [ ] T100 [US7] Implement navigation handlers using React Router (navigate to /trips/new, /profile, /routes)
- [ ] T101 [US7] Style action buttons with Tailwind (hover states, responsive sizing)
- [ ] T102 [US7] Ensure accessibility with ARIA labels for screen readers

**Checkpoint**: User Story 7 complete - quick actions navigate correctly, all buttons functional

---

## Phase 11: Dashboard Layout Integration

**Goal**: Integrate all user story components into responsive 3-column dashboard layout

- [ ] T103 Create DashboardLayout component in frontend/src/components/dashboard/DashboardLayout.tsx with responsive grid (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
- [ ] T104 Create DashboardPage in frontend/src/pages/DashboardPage.tsx integrating DashboardHeader, DashboardLayout, and all user story components
- [ ] T105 Configure React Router path for /dashboard in frontend/src/App.tsx
- [ ] T106 Add protected route wrapper ensuring authentication before dashboard access
- [ ] T107 Implement responsive column distribution: Left (StatsOverview, SocialMetrics, QuickActions), Center (ActivityFeed), Right (SuggestedRoutes, ActiveChallenges, Notifications)
- [ ] T108 Add mobile layout adaptation (stack all sections vertically on <768px)
- [ ] T109 Ensure sticky header z-index (z-50) is higher than all dashboard content
- [ ] T110 Add scroll restoration when navigating back to dashboard from other pages

**Checkpoint**: Dashboard layout complete - all components render in responsive grid, navigation works

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [ ] T111 [P] Add Spanish error messages for all API failures with retry buttons
- [ ] T112 [P] Ensure all components use semantic HTML and ARIA attributes for screen readers
- [ ] T113 [P] Add focus-visible ring styles for keyboard navigation (focus:ring-2 focus:ring-primary)
- [ ] T114 [P] Implement screen reader only utility class (sr-only) for hidden labels
- [ ] T115 [P] Verify Tailwind bundle size <100KB gzipped using `npm run build` + bundle analyzer
- [ ] T116 [P] Add loading skeletons for all components during initial render
- [ ] T117 [P] Ensure all timestamps use date-fns with Spanish locale (es)
- [ ] T118 [P] Add hardware acceleration to sticky header (will-change: transform)
- [ ] T119 [P] Verify scroll performance >30 FPS on mid-range devices (Chrome DevTools Performance tab)
- [ ] T120 [P] Add DOMPurify sanitization for HTML content in activity feed (XSS prevention)
- [ ] T121 [P] Update CLAUDE.md with dashboard redesign patterns and Tailwind usage
- [ ] T122 [P] Add Lighthouse performance audit targeting FCP <1.5s, TTI <3.5s
- [ ] T123 Run quickstart.md validation steps (E2E tests, accessibility checks, bundle analysis)
- [ ] T124 Create PR with screenshots (desktop, tablet, mobile) following conventional commits (`feat(dashboard):`)

**Checkpoint**: Polish complete - all success criteria met, documentation updated, PR ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Dashboard Layout (Phase 11)**: Depends on US1, US2 (critical), US3-US8 (optional)
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Stats**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1) - Header/Search**: Can start after Foundational (Phase 2) - Independent from US1
- **User Story 3 (P2) - Activity Feed**: Can start after Foundational (Phase 2) - Independent from US1/US2
- **User Story 8 (P2) - Social Metrics**: Depends on US1 (StatsOverview component) for integration
- **User Story 4 (P2) - Suggested Routes**: Can start after Foundational (Phase 2) - Independent from other stories
- **User Story 5 (P3) - Challenges**: Can start after Foundational (Phase 2) - Independent from other stories
- **User Story 6 (P3) - Notifications**: Depends on US2 (DashboardHeader component) for counter badge
- **User Story 7 (P3) - Quick Actions**: Can start after Foundational (Phase 2) - Independent from other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Hooks before components
- API service calls before hooks
- Core components before integration into layout
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T007)
- All Foundational tasks marked [P] can run in parallel (T009-T014)
- Once Foundational phase completes, all user stories can start in parallel:
  - **US1 Tests**: T016, T017, T018 in parallel
  - **US1 Implementation**: T019, T020 in parallel
  - **US2 Tests**: T027, T028, T029, T030 in parallel
  - **US2 Implementation**: T031, T032 in parallel
  - **US3 Tests**: T041, T042, T043 in parallel
  - **US3 Implementation**: T044, T045 in parallel
  - **US4-US7**: Similar parallel patterns within each story
- All Polish tasks marked [P] can run in parallel (T111-T122)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - FIRST):
Task T016: "E2E test for dashboard stats display in frontend/tests/e2e/dashboard-stats.spec.ts"
Task T017: "Unit test for useDashboardStats hook in frontend/tests/unit/hooks/useDashboardStats.test.ts"
Task T018: "Component test for StatsOverview in frontend/tests/unit/components/StatsOverview.test.tsx"

# Launch parallel implementation tasks:
Task T019: "Create useDashboardStats hook in frontend/src/hooks/useDashboardStats.ts"
Task T020: "Implement getDashboardStats API call in frontend/src/services/dashboardService.ts"
```

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together (TDD - FIRST):
Task T027: "E2E test for sticky header in frontend/tests/e2e/dashboard-navigation.spec.ts"
Task T028: "E2E test for global search in frontend/tests/e2e/dashboard-navigation.spec.ts"
Task T029: "Unit test for useGlobalSearch hook in frontend/tests/unit/hooks/useGlobalSearch.test.ts"
Task T030: "Component test for GlobalSearch in frontend/tests/unit/components/GlobalSearch.test.tsx"

# Launch parallel implementation tasks:
Task T031: "Create useGlobalSearch hook in frontend/src/hooks/useGlobalSearch.ts"
Task T032: "Implement searchGlobal API call in frontend/src/services/dashboardService.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (Tailwind CSS)
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Stats)
4. Complete Phase 4: User Story 2 (Header/Search)
5. Complete Phase 11: Dashboard Layout Integration (basic)
6. **STOP and VALIDATE**: Test US1 + US2 independently
7. Deploy/demo if ready - **This is the MVP!**

**MVP Success Criteria**:
- User can see personal stats <1s after login
- Sticky header works with global search
- Dashboard loads <2s
- All P1 tests pass

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Stats only)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP with header!)
4. Add User Story 3 → Test independently → Deploy/Demo (Social engagement)
5. Add User Story 8 → Test independently → Deploy/Demo (Social metrics)
6. Add User Story 4 → Test independently → Deploy/Demo (Route discovery)
7. Add User Story 5 → Test independently → Deploy/Demo (Gamification)
8. Add User Story 6 → Test independently → Deploy/Demo (Notifications)
9. Add User Story 7 → Test independently → Deploy/Demo (Complete dashboard)
10. Polish → Final release

**Each story adds value without breaking previous stories**

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Stats)
   - **Developer B**: User Story 2 (Header/Search)
   - **Developer C**: User Story 3 (Feed)
3. After P1 stories complete:
   - **Developer A**: User Story 8 (Social Metrics)
   - **Developer B**: User Story 4 (Suggested Routes)
   - **Developer C**: User Story 5 (Challenges)
4. After P2 stories complete:
   - **Developer A**: User Story 6 (Notifications)
   - **Developer B**: User Story 7 (Quick Actions)
   - **Developer C**: Dashboard Layout Integration
5. All together: Polish phase

**Stories complete and integrate independently**

---

## Success Criteria Verification

**SC-001**: Dashboard stats load <1s (US1) → Verify with E2E test T016 + Lighthouse audit
**SC-002**: 90% find content via search first try (US2) → Verify with UX testing + analytics
**SC-003**: Feed loads 50 items <2s (US3) → Verify with E2E test T041 + performance audit
**SC-004**: 3+ relevant route suggestions for 80% users (US4) → Verify with backend analytics
**SC-005**: Users spend 5+ min exploring (US1-US8) → Verify with analytics tracking
**SC-006**: Notifications delivered <3s delay (US6) → Verify with E2E test T084
**SC-007**: Tablet fully functional 768px-1024px (All) → Verify with responsive testing
**SC-008**: 85% complete quick action first visit (US7) → Verify with analytics
**SC-009**: Discover user/route <2 min via feed (US3) → Verify with UX testing
**SC-010**: Scroll performance >30 FPS (All) → Verify with T119 Chrome DevTools

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD MANDATORY**: Verify tests fail before implementing (constitution requirement)
- Commit after each task or logical group following conventional commits (`feat(dashboard):`, `test(dashboard):`, `style(dashboard):`)
- Stop at any checkpoint to validate story independently
- Tailwind classes replace CSS Modules for all new components (Feature 015)
- Coexistence: Existing components keep CSS Modules, new components use Tailwind
- Reference [tailwind-setup.md](tailwind-setup.md) for component patterns and troubleshooting
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

**Total Tasks**: 124
**P1 Tasks (MVP)**: 40 (Setup + Foundational + US1 + US2 + Layout Integration)
**P2 Tasks**: 29 (US3 + US4 + US8)
**P3 Tasks**: 31 (US5 + US6 + US7)
**Polish Tasks**: 14 (Cross-cutting concerns)

**Estimated MVP Delivery**: Setup (1 day) + Foundational (1 day) + US1 (2 days) + US2 (2 days) + Integration (1 day) = ~7 days
