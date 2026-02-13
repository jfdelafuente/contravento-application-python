# Tasks: Dashboard Followers/Following Tooltips

**Input**: Design documents from `/specs/019-followers-tooltip/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, IMPLEMENTATION_GUIDE.md

**Tests**: Tests are REQUIRED for this feature per TDD workflow (Constitution Check)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new files and project structure

- [X] T001 [P] Create hook file `frontend/src/hooks/useFollowersTooltip.ts` with basic TypeScript exports
- [X] T002 [P] Create component file `frontend/src/components/dashboard/SocialStatTooltip.tsx` with placeholder component
- [X] T003 [P] Create CSS file `frontend/src/components/dashboard/SocialStatTooltip.css` with empty ruleset
- [X] T004 [P] Create unit test file `frontend/tests/unit/useFollowersTooltip.test.ts` with test suite setup
- [X] T005 [P] Create unit test file `frontend/tests/unit/SocialStatTooltip.test.tsx` with test suite setup
- [X] T006 [P] Create E2E test file `frontend/tests/e2e/dashboard-tooltips.spec.ts` with test suite setup

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data fetching hook and tooltip presentation component that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Components (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [P] [Foundation] Unit test: useFollowersTooltip returns correct initial state in `frontend/tests/unit/useFollowersTooltip.test.ts`
- [X] T008 [P] [Foundation] Unit test: useFollowersTooltip fetchUsers() calls getFollowers API in `frontend/tests/unit/useFollowersTooltip.test.ts`
- [X] T009 [P] [Foundation] Unit test: useFollowersTooltip slices response to 8 users in `frontend/tests/unit/useFollowersTooltip.test.ts`
- [X] T010 [P] [Foundation] Unit test: useFollowersTooltip handles loading state correctly in `frontend/tests/unit/useFollowersTooltip.test.ts`
- [X] T011 [P] [Foundation] Unit test: useFollowersTooltip handles errors with Spanish message in `frontend/tests/unit/useFollowersTooltip.test.ts`
- [X] T012 [P] [Foundation] Unit test: useFollowersTooltip handles empty followers (0 count) in `frontend/tests/unit/useFollowersTooltip.test.ts`
- [X] T013 [P] [Foundation] Unit test: SocialStatTooltip renders loading state with spinner in `frontend/tests/unit/SocialStatTooltip.test.tsx`
- [X] T014 [P] [Foundation] Unit test: SocialStatTooltip renders user list with 8 users in `frontend/tests/unit/SocialStatTooltip.test.tsx`
- [X] T015 [P] [Foundation] Unit test: SocialStatTooltip renders empty state message in `frontend/tests/unit/SocialStatTooltip.test.tsx`
- [X] T016 [P] [Foundation] Unit test: SocialStatTooltip renders "Ver todos" link when remaining > 0 in `frontend/tests/unit/SocialStatTooltip.test.tsx`
- [X] T017 [P] [Foundation] Unit test: SocialStatTooltip does not render "Ver todos" when totalCount ≤ 8 in `frontend/tests/unit/SocialStatTooltip.test.tsx`
- [X] T018 [P] [Foundation] Unit test: SocialStatTooltip hides when visible=false in `frontend/tests/unit/SocialStatTooltip.test.tsx`

### Implementation for Foundational Components

- [X] T019 [Foundation] Implement useFollowersTooltip hook in `frontend/src/hooks/useFollowersTooltip.ts` (see IMPLEMENTATION_GUIDE.md § Task 2.1, research.md § 5, data-model.md § 4 lines 88-115)
  - Initial state: users=[], totalCount=0, isLoading=false, error=null
  - fetchUsers() function using followService.getFollowers() or getFollowing()
  - Slice to 8 users: response.followers.slice(0, 8)
  - Error handling with Spanish message: "Error al cargar usuarios"
  - useCallback for fetchUsers to prevent re-renders
- [X] T020 [Foundation] Implement SocialStatTooltip component in `frontend/src/components/dashboard/SocialStatTooltip.tsx` (see IMPLEMENTATION_GUIDE.md § Task 2.2, data-model.md § 5 lines 119-157, ANALISIS lines 203-291)
  - Props interface: users, totalCount, type, username, isLoading, error, visible
  - Conditional rendering: !visible → return null
  - Loading state: spinner + "Cargando..." message
  - Error state: error message display
  - Empty state: "No tienes seguidores aún" or "No sigues a nadie aún"
  - User list: map over users, display avatar + username
  - "Ver todos" link: show when remaining > 0, calculate "+ X más · Ver todos"
- [X] T021 [Foundation] Implement tooltip CSS in `frontend/src/components/dashboard/SocialStatTooltip.css` (see IMPLEMENTATION_GUIDE.md § Task 3.1, research.md § 2, ANALISIS lines 447-622)
  - Absolute positioning below card with 8px gap
  - Max-width: 280px for desktop, 200px for mobile
  - Arrow pointing to card (CSS triangle)
  - Fade-in/fade-out animations (150ms)
  - Hover effects on username rows
  - Loading spinner keyframe animation
  - Responsive breakpoints (@media max-width: 768px)
  - Z-index: 1000 to overlay dashboard content

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Quick Follower Preview (Priority: P1) 🎯 MVP

**Goal**: Allow users to preview their followers by hovering over the "Seguidores" card on dashboard

**Independent Test**: Hover over followers card for 500ms → tooltip appears with 5-8 user avatars → delivers social discovery without navigation

### Tests for User Story 1 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T022 [P] [US1] E2E test: Hover "Seguidores" card for 500ms → tooltip appears in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T023 [P] [US1] E2E test: Tooltip shows correct number of followers (max 8) in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T024 [P] [US1] E2E test: Mouse leave for 200ms → tooltip disappears in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T025 [P] [US1] E2E test: Quick hover (<500ms) → no tooltip appears in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T026 [P] [US1] E2E test: Move mouse from card to tooltip → tooltip stays visible in `frontend/tests/e2e/dashboard-tooltips.spec.ts`

### Implementation for User Story 1

- [X] T027 [US1] Modify SocialStatsSection in `frontend/src/components/dashboard/SocialStatsSection.tsx` to add hover handlers for "Seguidores" card (see IMPLEMENTATION_GUIDE.md § Task 4.1)
  - Import useFollowersTooltip and SocialStatTooltip
  - State: activeTooltip ('followers' | 'following' | null), hoverTimeout (useRef)
  - handleMouseEnter('followers'): Set 500ms timeout, call followersTooltip.fetchUsers()
  - handleMouseLeave: Set 200ms timeout, clear activeTooltip
  - Render SocialStatTooltip with followers data, visible when activeTooltip === 'followers'
  - Position tooltip below followers card using CSS
- [X] T028 [US1] Add follower count check to prevent unnecessary API calls when count is 0 in `frontend/src/components/dashboard/SocialStatsSection.tsx`
  - Check stats.followers_count > 0 before calling fetchUsers()
  - Show tooltip immediately with empty state if count === 0

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can hover to see follower preview!

---

## Phase 4: User Story 2 - Quick Following Preview (Priority: P1)

**Goal**: Allow users to preview who they're following by hovering over the "Siguiendo" card on dashboard

**Independent Test**: Hover over following card for 500ms → tooltip appears with 5-8 users being followed → delivers value without navigation

### Tests for User Story 2 (TDD - Write FIRST)

- [X] T029 [P] [US2] E2E test: Hover "Siguiendo" card for 500ms → tooltip appears in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T030 [P] [US2] E2E test: Tooltip shows correct number of following (max 8) in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T031 [P] [US2] E2E test: Following tooltip shows "No sigues a nadie aún" when count is 0 in `frontend/tests/e2e/dashboard-tooltips.spec.ts`

### Implementation for User Story 2

- [X] T032 [US2] Add hover handlers for "Siguiendo" card in `frontend/src/components/dashboard/SocialStatsSection.tsx` (see IMPLEMENTATION_GUIDE.md § Task 4.1)
  - Initialize useFollowersTooltip('username', 'following')
  - handleMouseEnter('following'): Set 500ms timeout, call followingTooltip.fetchUsers()
  - Render second SocialStatTooltip with following data, visible when activeTooltip === 'following'
  - Position tooltip below following card
- [X] T033 [US2] Add following count check to prevent unnecessary API calls when count is 0 in `frontend/src/components/dashboard/SocialStatsSection.tsx`
  - Check stats.following_count > 0 before calling fetchUsers()

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Dashboard has both follower and following tooltips!

---

## Phase 5: User Story 3 - Navigate to User Profiles (Priority: P2)

**Goal**: Enable clicking on usernames in tooltip to navigate to user profiles

**Independent Test**: Hover to show tooltip → click on any username → navigate to `/users/{username}` profile page

### Tests for User Story 3 (TDD - Write FIRST)

- [X] T034 [P] [US3] E2E test: Click username in tooltip → navigate to `/users/{username}` in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T035 [P] [US3] E2E test: Hover over username → row highlights with background color in `frontend/tests/e2e/dashboard-tooltips.spec.ts`

### Implementation for User Story 3

- [X] T036 [US3] Add username links to SocialStatTooltip component in `frontend/src/components/dashboard/SocialStatTooltip.tsx`
  - Wrap username with React Router Link to `/users/${user.username}`
  - Style links with hover effects (see CSS)
- [X] T037 [US3] Add hover effects to username rows in `frontend/src/components/dashboard/SocialStatTooltip.css`
  - Background color change on hover (--surface-hover or rgba)
  - Cursor: pointer
  - Smooth transition (150ms)

**Checkpoint**: Users can now navigate from tooltip to profiles. Tooltip enables social discovery AND action!

---

## Phase 6: User Story 4 - View Complete List (Priority: P2)

**Goal**: Provide "Ver todos" link to navigate to full follower/following list when preview isn't enough

**Independent Test**: Hover tooltip with "+ X más · Ver todos" → click link → navigate to `/users/{username}/followers` or `/users/{username}/following`

### Tests for User Story 4 (TDD - Write FIRST)

- [X] T038 [P] [US4] E2E test: Click "Ver todos" in followers tooltip → navigate to `/users/{username}/followers` in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T039 [P] [US4] E2E test: Click "Ver todos" in following tooltip → navigate to `/users/{username}/following` in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [X] T040 [P] [US4] E2E test: "Ver todos" link does not appear when totalCount ≤ 8 in `frontend/tests/e2e/dashboard-tooltips.spec.ts`

### Implementation for User Story 4

- [X] T041 [US4] Verify "Ver todos" link is correctly implemented in SocialStatTooltip component (already done in T020)
  - Conditional render: only show when remaining > 0
  - Calculate remaining: totalCount - users.length
  - Link text: "+ {remaining} más · Ver todos"
  - Link destination: `/users/${username}/followers` or `/users/${username}/following` based on type
  - Style link with accent color, hover underline

**Checkpoint**: Progressive disclosure complete. Users can access full list from tooltip preview!

---

## Phase 7: User Story 5 - Mobile Touch Interaction (Priority: P3)

**Goal**: Provide appropriate mobile UX since hover doesn't exist on touch devices

**Independent Test**: Tap followers/following card on mobile device → navigate directly to full list page

### Tests for User Story 5 (TDD - Write FIRST)

- [ ] T042 [P] [US5] E2E test: On touch device, tap "Seguidores" card → navigate to `/users/{username}/followers` in `frontend/tests/e2e/dashboard-tooltips.spec.ts` (use Playwright mobile viewport)
- [ ] T043 [P] [US5] E2E test: On touch device, tap "Siguiendo" card → navigate to `/users/{username}/following` in `frontend/tests/e2e/dashboard-tooltips.spec.ts` (use Playwright mobile viewport)

### Implementation for User Story 5

- [ ] T044 [US5] Add touch device detection in `frontend/src/components/dashboard/SocialStatsSection.tsx` (see research.md § 4)
  - Detect touch device: `window.matchMedia('(hover: none)').matches`
  - On touch devices: onClick handler navigates directly to full list page
  - On hover devices: Use hover handlers (existing implementation)
  - Alternative: Use CSS `@media (hover: none)` to hide tooltip, make card clickable
- [ ] T045 [US5] Add responsive CSS for touch devices in `frontend/src/components/dashboard/SocialStatTooltip.css`
  - `@media (hover: none)`: Hide tooltip entirely
  - Make cards clickable on touch devices with visual feedback

**Checkpoint**: Mobile users can access follower/following lists via direct navigation. Feature gracefully degrades!

---

## Phase 8: User Story 6 - Keyboard Navigation (Priority: P3)

**Goal**: Support full keyboard navigation for accessibility (WCAG 2.1 AA compliance)

**Independent Test**: Use only keyboard (Tab, Enter, Escape) → navigate to card, trigger tooltip, navigate links, close tooltip

### Tests for User Story 6 (TDD - Write FIRST)

- [ ] T046 [P] [US6] E2E test: Tab to followers card + focus → tooltip appears after 500ms in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [ ] T047 [P] [US6] E2E test: Tab through tooltip → focus moves to username links in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [ ] T048 [P] [US6] E2E test: Press Escape → tooltip closes immediately in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
- [ ] T049 [P] [US6] E2E test: Press Enter on username link → navigate to profile in `frontend/tests/e2e/dashboard-tooltips.spec.ts`

### Implementation for User Story 6

- [ ] T050 [US6] Add keyboard event handlers in `frontend/src/components/dashboard/SocialStatsSection.tsx` (see research.md § 3)
  - onFocus handler on cards: Trigger tooltip after 500ms (same as hover)
  - onBlur handler: Close tooltip after 200ms
  - onKeyDown (Escape key): Close tooltip immediately
  - Make cards focusable: tabIndex={0}
- [ ] T051 [US6] Add ARIA attributes to SocialStatTooltip component in `frontend/src/components/dashboard/SocialStatTooltip.tsx` (see research.md § 3)
  - role="tooltip"
  - aria-live="polite" (announces loading/error states)
  - aria-describedby on trigger card (references tooltip ID)
  - aria-label on "Ver todos" link with descriptive text
- [ ] T052 [US6] Add keyboard focus styles in `frontend/src/components/dashboard/SocialStatTooltip.css`
  - Visible focus ring on cards (outline: 2px solid --accent-amber)
  - Focus visible on username links
  - Skip-link for screen readers (optional enhancement)

**Checkpoint**: All user stories should now be independently functional. Feature is fully accessible!

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, final validation

- [ ] T053 [P] Update CLAUDE.md Active Technologies section with Feature 019 in `CLAUDE.md` (see IMPLEMENTATION_GUIDE.md § Task 8.1)
  - Add: TypeScript 5 (frontend-only, no backend changes)
  - Add: React 18 + React Router 6 + Axios (existing)
  - Add: Uses existing /users/{username}/followers endpoints
  - Add tooltip implementation patterns section (already done in planning)
- [ ] T054 [P] Run axe-core accessibility validation in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
  - Install @axe-core/playwright if not present
  - Add accessibility scan to E2E test: await new AxeBuilder({ page }).analyze()
  - Assert: No violations with WCAG 2.1 AA rules
  - Fix any accessibility issues found
- [ ] T055 [P] Performance validation: Verify tooltip display <1s in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
  - Measure time from hover to tooltip visible
  - Assert: <1000ms total (500ms delay + <500ms API)
  - Use Playwright performance timing API
- [ ] T056 [P] Performance validation: Verify no layout shift (CLS = 0) in `frontend/tests/e2e/dashboard-tooltips.spec.ts`
  - Measure Cumulative Layout Shift during tooltip appearance
  - Assert: CLS = 0 (tooltip uses absolute positioning)
- [ ] T057 Code cleanup: Remove console.log statements and debug code from all new files
- [ ] T058 Code cleanup: Run ESLint and fix any warnings in `frontend/src/hooks/useFollowersTooltip.ts`, `frontend/src/components/dashboard/SocialStatTooltip.tsx`, `frontend/src/components/dashboard/SocialStatsSection.tsx`
- [ ] T059 Code cleanup: Run TypeScript compiler (tsc --noEmit) and fix any type errors
- [ ] T060 [P] Run quickstart.md validation: Manual testing of all 18 test scenarios (see `specs/019-followers-tooltip/quickstart.md`)
  - Verify Followers Tooltip (hover, display, timing)
  - Verify Following Tooltip
  - Test "Ver todos" Link (requires 9+ followers)
  - Empty State (0 followers)
  - Loading State (with network throttling)
  - Error State (network failure)
  - Keyboard Navigation (Tab, Enter, Escape)
  - Screen Reader Testing (NVDA/JAWS/VoiceOver)
  - Touch Device Fallback (mobile simulation)
  - Verify Lazy Loading (no API calls on mount)
  - Verify No Layout Shift (CLS = 0)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Reuses components from US1 but is independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Enhances US1/US2 with navigation but doesn't block them
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Enhances US1/US2 with "Ver todos" link but doesn't block them
- **User Story 5 (P3)**: Can start after US1/US2 complete - Adds mobile fallback
- **User Story 6 (P3)**: Can start after US1/US2 complete - Adds keyboard accessibility

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD workflow)
- Foundation components (hook, tooltip) before integration (SocialStatsSection modification)
- Core implementation before enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup (Phase 1)**: All 6 tasks marked [P] can run in parallel (T001-T006)
- **Foundational Tests (Phase 2)**: All 12 test tasks marked [P] can run in parallel (T007-T018)
- **Foundational Implementation**: T019 (hook), T020 (component), T021 (CSS) can run in parallel
- **Once Foundational completes**: US1 and US2 can start in parallel (both P1 priority)
- **US3 and US4**: Can run in parallel after US1/US2 complete (both P2 priority)
- **Polish (Phase 9)**: All tasks marked [P] can run in parallel (T053-T056, T060)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write FIRST):
Task T022: "E2E test: Hover 'Seguidores' card for 500ms → tooltip appears"
Task T023: "E2E test: Tooltip shows correct number of followers (max 8)"
Task T024: "E2E test: Mouse leave for 200ms → tooltip disappears"
Task T025: "E2E test: Quick hover (<500ms) → no tooltip appears"
Task T026: "E2E test: Move mouse from card to tooltip → tooltip stays visible"

# Then implement (after tests fail):
Task T027: "Modify SocialStatsSection to add hover handlers for followers card"
Task T028: "Add follower count check to prevent unnecessary API calls"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T021) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T022-T028) - Quick Follower Preview
4. Complete Phase 4: User Story 2 (T029-T033) - Quick Following Preview
5. **STOP and VALIDATE**: Test US1 and US2 independently using quickstart.md
6. Deploy/demo if ready - Core value delivered!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - Followers!)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP++ - Following!)
4. Add User Story 3 → Test independently → Deploy/Demo (Profile navigation!)
5. Add User Story 4 → Test independently → Deploy/Demo (Full list access!)
6. Add User Story 5 → Test mobile → Deploy/Demo (Mobile support!)
7. Add User Story 6 → Test accessibility → Deploy/Demo (Full accessibility!)
8. Polish (Phase 9) → Final validation → Production ready!

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Followers tooltip)
   - Developer B: User Story 2 (Following tooltip) - mostly reuses US1 components
   - Developer C: Tests (T007-T018, T022-T026, T029-T031)
3. Once US1/US2 complete:
   - Developer A: User Story 3 (Profile navigation)
   - Developer B: User Story 4 ("Ver todos" link)
   - Developer C: User Story 5 (Mobile fallback)
4. Once US3/US4/US5 complete:
   - Any developer: User Story 6 (Keyboard navigation)
   - Any developer: Polish tasks (T053-T060)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Should be independently completable and testable
- **TDD workflow**: Verify tests FAIL before implementing (RED → GREEN → refactor)
- **Commit strategy**: Commit after each task or logical group (e.g., all tests for a story)
- **Validation checkpoints**: Stop at each checkpoint to validate story independently
- **Avoid**: Vague tasks, same file conflicts, cross-story dependencies that break independence
- **Reference docs**: See IMPLEMENTATION_GUIDE.md for detailed code examples and cross-references
- **Timeline estimate**: 7-8 hours total per IMPLEMENTATION_GUIDE.md (assuming solo developer, sequential execution)

---

**Total Tasks**: 60 tasks
- Phase 1 (Setup): 6 tasks (parallel)
- Phase 2 (Foundational): 15 tasks (12 tests parallel, 3 implementation parallel)
- Phase 3 (US1): 7 tasks (5 tests parallel, 2 implementation sequential)
- Phase 4 (US2): 5 tasks (3 tests parallel, 2 implementation sequential)
- Phase 5 (US3): 4 tasks (2 tests parallel, 2 implementation sequential)
- Phase 6 (US4): 4 tasks (3 tests parallel, 1 implementation)
- Phase 7 (US5): 4 tasks (2 tests parallel, 2 implementation sequential)
- Phase 8 (US6): 7 tasks (4 tests parallel, 3 implementation sequential)
- Phase 9 (Polish): 8 tasks (5 parallel, 3 sequential)

**Parallel Opportunities**: Up to 12 tasks can run in parallel during Foundational tests phase. US1 and US2 can run in parallel after Foundational completes.

**MVP Milestone**: Complete T001-T033 (39 tasks) for quick follower/following preview - delivers core value!
