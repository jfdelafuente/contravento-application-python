# Tasks: Enlaces Sociales con Control de Privacidad Granular

**Branch**: `015-social-links-privacy` | **Feature**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

**Input**: Design documents from `/specs/015-social-links-privacy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/social-links-api.yaml

**Tests**: Tests are REQUIRED as per TDD constitution (≥90% coverage mandatory)

**Organization**: Tasks grouped by user story (US1-US5 in priority order) for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

Web app structure (from plan.md):
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, database migration, and basic configuration

- [ ] T001 Create Alembic migration for social_links table in backend/migrations/versions/
- [ ] T002 Create PrivacyLevel enum in backend/src/models/enums.py
- [ ] T003 Create PlatformType enum in backend/src/models/enums.py
- [ ] T004 [P] Install validators library (validators==0.22.0) in backend/pyproject.toml
- [ ] T005 [P] Configure domain allowlist constants in backend/src/config.py

**Checkpoint**: Database schema ready, enums defined, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create SocialLink SQLAlchemy model in backend/src/models/social_link.py
- [ ] T007 Create URL validator utility in backend/src/utils/url_validator.py (sanitize_url, validate_domain)
- [ ] T008 [P] Create SocialLinkCreate Pydantic schema in backend/src/schemas/social_link.py
- [ ] T009 [P] Create SocialLinkUpdate Pydantic schema in backend/src/schemas/social_link.py
- [ ] T010 [P] Create SocialLinkResponse Pydantic schema in backend/src/schemas/social_link.py
- [ ] T011 Apply Alembic migration (alembic upgrade head) to create social_links table
- [ ] T012 Verify database schema with SQLite/PostgreSQL compatibility

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Añadir Enlaces Sociales con Visibilidad Pública (Priority: P1) 🎯 MVP

**Goal**: Allow users to add social links (Instagram, Strava, Blog, Portfolio) with PUBLIC privacy level

**Independent Test**: User creates Instagram link → link appears on profile for anonymous visitors

**User Stories Covered**: US1 (FR-001, FR-002 PUBLIC only, FR-003, FR-004)

### Tests for User Story 1 (TDD - RED phase)

> **CRITICAL: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T013 [P] [US1] Unit test for URL validation in backend/tests/unit/test_url_validator.py
- [ ] T014 [P] [US1] Unit test for domain allowlist validation in backend/tests/unit/test_url_validator.py
- [ ] T015 [P] [US1] Unit test for XSS attempt blocking in backend/tests/unit/test_url_validator.py
- [ ] T016 [P] [US1] Unit test for SocialLinkService.create_link() in backend/tests/unit/test_social_link_service.py
- [ ] T017 [P] [US1] Contract test for POST /social-links in backend/tests/contract/test_social_links_contract.py
- [ ] T018 [P] [US1] Integration test for creating PUBLIC Instagram link in backend/tests/integration/test_social_links_api.py

### Implementation for User Story 1 (TDD - GREEN phase)

- [ ] T019 [US1] Implement SocialLinkService.create_link() in backend/src/services/social_link_service.py
- [ ] T020 [US1] Implement SocialLinkService.get_user_links() (PUBLIC only) in backend/src/services/social_link_service.py
- [ ] T021 [US1] Implement POST /social-links endpoint in backend/src/api/social_links.py
- [ ] T022 [US1] Implement GET /users/{username}/social-links (anonymous access) in backend/src/api/social_links.py
- [ ] T023 [US1] Add XSS sanitization with rel="me nofollow" in response serialization
- [ ] T024 [US1] Add unique constraint validation for (user_id, platform_type) in service layer
- [ ] T025 [US1] Add error handling with Spanish messages ("URL inválida...", "Máximo 6 enlaces...")

**Checkpoint**: US1 complete - users can add PUBLIC social links, anonymous users can view them

---

## Phase 4: User Story 5 - Editar y Eliminar Enlaces (Priority: P1) 🎯 MVP

**Goal**: Allow users to edit or delete their own social links (owner-only actions)

**Independent Test**: User edits Instagram URL → change persists, user deletes link → link removed from profile

**User Stories Covered**: US5 (FR-006, FR-007)

### Tests for User Story 5 (TDD - RED phase)

- [ ] T026 [P] [US5] Unit test for SocialLinkService.update_link() in backend/tests/unit/test_social_link_service.py
- [ ] T027 [P] [US5] Unit test for SocialLinkService.delete_link() in backend/tests/unit/test_social_link_service.py
- [ ] T028 [P] [US5] Unit test for owner authorization in backend/tests/unit/test_social_link_service.py
- [ ] T029 [P] [US5] Contract test for PUT /social-links/{link_id} in backend/tests/contract/test_social_links_contract.py
- [ ] T030 [P] [US5] Contract test for DELETE /social-links/{link_id} in backend/tests/contract/test_social_links_contract.py
- [ ] T031 [P] [US5] Integration test for editing link (owner only) in backend/tests/integration/test_social_links_api.py
- [ ] T032 [P] [US5] Integration test for deleting link (403 for non-owner) in backend/tests/integration/test_social_links_api.py

### Implementation for User Story 5 (TDD - GREEN phase)

- [ ] T033 [US5] Implement SocialLinkService.update_link() with owner verification in backend/src/services/social_link_service.py
- [ ] T034 [US5] Implement SocialLinkService.delete_link() with owner verification in backend/src/services/social_link_service.py
- [ ] T035 [US5] Implement PUT /social-links/{link_id} endpoint in backend/src/api/social_links.py
- [ ] T036 [US5] Implement DELETE /social-links/{link_id} endpoint in backend/src/api/social_links.py
- [ ] T037 [US5] Add 403 Forbidden error handling for non-owners
- [ ] T038 [US5] Add 404 Not Found error handling for invalid link_id

**Checkpoint**: US1 + US5 complete - users can create, edit, delete PUBLIC social links (MVP functional)

---

## Phase 5: User Story 2 - Privacidad "Solo Comunidad" (Priority: P2)

**Goal**: Users can set links to COMMUNITY privacy (visible only to authenticated users, not anonymous)

**Independent Test**: User sets Instagram to COMMUNITY → anonymous user doesn't see it, authenticated user sees it

**User Stories Covered**: US2 (FR-002 COMMUNITY level, FR-008)

### Tests for User Story 2 (TDD - RED phase)

- [ ] T039 [P] [US2] Unit test for privacy_level=COMMUNITY filtering in backend/tests/unit/test_social_link_service.py
- [ ] T040 [P] [US2] Integration test for anonymous user (no COMMUNITY links) in backend/tests/integration/test_social_links_api.py
- [ ] T041 [P] [US2] Integration test for authenticated user (sees COMMUNITY) in backend/tests/integration/test_social_links_api.py
- [ ] T042 [P] [US2] Contract test for privacy filtering in GET /users/{username}/social-links in backend/tests/contract/test_social_links_contract.py

### Implementation for User Story 2 (TDD - GREEN phase)

- [ ] T043 [US2] Update SocialLinkService.get_visible_links() to filter by authentication status in backend/src/services/social_link_service.py
- [ ] T044 [US2] Add privacy filtering logic for COMMUNITY level in backend/src/services/social_link_service.py
- [ ] T045 [US2] Update GET /users/{username}/social-links to pass viewer authentication status to service
- [ ] T046 [US2] Add logging for privacy filtering decisions (development debugging)

**Checkpoint**: US2 complete - COMMUNITY privacy level works correctly (anonymous vs authenticated filtering)

---

## Phase 6: User Story 4 - Nivel de Privacidad "Oculto" (Priority: P2)

**Goal**: Users can hide links completely (HIDDEN privacy level) - only visible to owner

**Independent Test**: User sets Portfolio to HIDDEN → only owner sees it in their own profile, no one else

**User Stories Covered**: US4 (FR-002 HIDDEN level, FR-010)

### Tests for User Story 4 (TDD - RED phase)

- [ ] T047 [P] [US4] Unit test for privacy_level=HIDDEN filtering in backend/tests/unit/test_social_link_service.py
- [ ] T048 [P] [US4] Integration test for owner viewing HIDDEN links in backend/tests/integration/test_social_links_api.py
- [ ] T049 [P] [US4] Integration test for non-owner not seeing HIDDEN links in backend/tests/integration/test_social_links_api.py
- [ ] T050 [P] [US4] Contract test for GET /social-links (owner-only endpoint) in backend/tests/contract/test_social_links_contract.py

### Implementation for User Story 4 (TDD - GREEN phase)

- [ ] T051 [US4] Update SocialLinkService.get_visible_links() to exclude HIDDEN from non-owners in backend/src/services/social_link_service.py
- [ ] T052 [US4] Implement GET /social-links endpoint (owner-only, includes HIDDEN) in backend/src/api/social_links.py
- [ ] T053 [US4] Add owner check in privacy filtering logic (viewer_user_id == profile_user_id)
- [ ] T054 [US4] Add documentation comment explaining HIDDEN vs owner-only GET difference

**Checkpoint**: US4 complete - HIDDEN privacy level works (owner sees all, others see PUBLIC/COMMUNITY only)

---

## Phase 7: User Story 3 - "Círculo de Confianza" (MUTUAL_FOLLOWERS) (Priority: P3)

**Goal**: Users can set links to MUTUAL_FOLLOWERS privacy (visible only to users they follow AND who follow them back)

**Independent Test**: Juan and Maria are mutual followers, Juan sets Blog to MUTUAL_FOLLOWERS → Maria sees it, Carlos (not mutual) doesn't

**User Stories Covered**: US3 (FR-002 MUTUAL_FOLLOWERS level, FR-009)

**⚠️ BLOCKER**: Requires Feature 011 (Follows) to be implemented first

### Tests for User Story 3 (TDD - RED phase)

- [ ] T055 [P] [US3] Unit test for check_mutual_follow() in backend/tests/unit/test_social_link_service.py
- [ ] T056 [P] [US3] Unit test for privacy_level=MUTUAL_FOLLOWERS filtering in backend/tests/unit/test_social_link_service.py
- [ ] T057 [P] [US3] Integration test for mutual follower viewing link in backend/tests/integration/test_social_links_api.py
- [ ] T058 [P] [US3] Integration test for non-mutual follower not seeing link in backend/tests/integration/test_social_links_api.py
- [ ] T059 [P] [US3] Integration test for performance (<200ms with 100 followers) in backend/tests/integration/test_social_links_api.py

### Implementation for User Story 3 (TDD - GREEN phase)

- [ ] T060 [US3] Implement check_mutual_follow() helper in backend/src/services/social_link_service.py
- [ ] T061 [US3] Update SocialLinkService.get_visible_links() to query Follows table for mutual check
- [ ] T062 [US3] Add eager loading for Follows relationship to prevent N+1 queries
- [ ] T063 [US3] Add privacy filtering logic for MUTUAL_FOLLOWERS level
- [ ] T064 [US3] Add performance logging for mutual follow check query (development debugging)
- [ ] T065 [US3] Verify database index on Follows table (follower_id, following_id) for performance

**Checkpoint**: US3 complete - MUTUAL_FOLLOWERS privacy level works with mutual follow verification

---

## Phase 8: Frontend - Social Links Display Components (Priority: P1) 🎯 MVP

**Goal**: Display social links on user profiles with privacy indicators (icons)

**Independent Test**: Visit profile → see Instagram icon with "Público" indicator, click → opens Instagram in new tab

**Frontend User Stories**: US1 (display), US2 (privacy icons)

### Tests for Frontend Display (TDD - RED phase)

- [ ] T066 [P] [US1] Unit test for SocialLinksDisplay component in frontend/tests/unit/profile/SocialLinksDisplay.test.tsx
- [ ] T067 [P] [US1] Unit test for PrivacyIndicator component in frontend/tests/unit/profile/PrivacyIndicator.test.tsx
- [ ] T068 [P] [US1] Unit test for social platform icon rendering in frontend/tests/unit/profile/SocialLinksDisplay.test.tsx
- [ ] T069 [P] [US1] E2E test for viewing social links in frontend/tests/e2e/social-links.spec.ts

### Implementation for Frontend Display (TDD - GREEN phase)

- [ ] T070 [P] [US1] Create SocialLink TypeScript interface in frontend/src/types/socialLink.ts
- [ ] T071 [P] [US1] Create PrivacyLevel TypeScript enum in frontend/src/types/socialLink.ts
- [ ] T072 [US1] Implement SocialLinksDisplay component in frontend/src/components/profile/SocialLinksDisplay.tsx
- [ ] T073 [US1] Implement PrivacyIndicator component in frontend/src/components/profile/PrivacyIndicator.tsx
- [ ] T074 [P] [US1] Add HeroIcons imports (LockOpenIcon, LockClosedIcon, UserGroupIcon, EyeSlashIcon)
- [ ] T075 [P] [US1] Create custom SVG icons for social platforms in frontend/src/assets/icons/ (instagram.svg, strava.svg, blog.svg, portfolio.svg)
- [ ] T076 [US1] Implement socialLinksService.ts API client in frontend/src/services/socialLinksService.ts
- [ ] T077 [US1] Integrate SocialLinksDisplay into ProfilePage component
- [ ] T078 [US1] Add rel="me nofollow" and target="_blank" to external links
- [ ] T079 [US1] Add CSS styling with ContraVento palette (terracota #D35400, verde bosque #1B2621, crema #F9F7F2)

**Checkpoint**: Frontend displays social links with privacy indicators, external links open correctly

---

## Phase 9: Frontend - Social Links Editor (Priority: P1) 🎯 MVP

**Goal**: Allow users to add, edit, delete social links from profile edit page

**Independent Test**: Click "Editar perfil" → add Instagram link → select privacy "Público" → save → link appears on profile

**Frontend User Stories**: US1 (create), US5 (edit/delete), US2/US4 (privacy dropdown)

### Tests for Frontend Editor (TDD - RED phase)

- [ ] T080 [P] [US5] Unit test for SocialLinksEditor component in frontend/tests/unit/profile/SocialLinksEditor.test.tsx
- [ ] T081 [P] [US5] Unit test for form validation (URL format, domain check) in frontend/tests/unit/profile/SocialLinksEditor.test.tsx
- [ ] T082 [P] [US5] Unit test for 6-link limit enforcement in frontend/tests/unit/profile/SocialLinksEditor.test.tsx
- [ ] T083 [P] [US5] E2E test for adding/editing/deleting links in frontend/tests/e2e/social-links.spec.ts

### Implementation for Frontend Editor (TDD - GREEN phase)

- [ ] T084 [US5] Implement SocialLinksEditor component in frontend/src/components/profile/SocialLinksEditor.tsx
- [ ] T085 [US5] Add React Hook Form with Zod validation for social link form
- [ ] T086 [US5] Implement platform type dropdown (Instagram, Strava, Blog, Portfolio, Custom 1/2)
- [ ] T087 [US5] Implement privacy level dropdown (Público, Solo Comunidad, Círculo de Confianza, Oculto)
- [ ] T088 [US5] Implement URL input with client-side validation (format check)
- [ ] T089 [US5] Add edit/delete buttons for existing links (owner-only)
- [ ] T090 [US5] Add confirmation dialog for delete action (modal with "¿Eliminar enlace?" prompt)
- [ ] T091 [US5] Implement API calls (createSocialLink, updateSocialLink, deleteSocialLink)
- [ ] T092 [US5] Add error handling with Spanish toast messages ("URL no válida...", "Máximo 6 enlaces...")
- [ ] T093 [US5] Add loading states during API calls (spinner on save button)
- [ ] T094 [US5] Integrate SocialLinksEditor into ProfileEditPage component

**Checkpoint**: Frontend editor allows full CRUD operations on social links with validation and error handling

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, performance, and final validation

- [ ] T095 [P] Add comprehensive docstrings to SocialLinkService in backend/src/services/social_link_service.py
- [ ] T096 [P] Add inline comments explaining privacy filtering logic in backend/src/services/social_link_service.py
- [ ] T097 [P] Run black formatter on all Python files (backend/src/, backend/tests/)
- [ ] T098 [P] Run ruff linter and fix warnings (backend/src/, backend/tests/)
- [ ] T099 [P] Run TypeScript compiler and fix errors (frontend/src/)
- [ ] T100 Performance profiling: Verify profile view <200ms p95 with 6 links + 100 followers
- [ ] T101 Performance profiling: Verify mutual follow check <10ms (indexed query)
- [ ] T102 Security audit: Test XSS attempts from quickstart.md Scenario 5
- [ ] T103 Security audit: Verify domain validation rejects javascript: and data: schemes
- [ ] T104 Manual testing: Test all 4 privacy levels with 3 users (anonymous, authenticated, mutual follower)
- [ ] T105 Manual testing: Verify tooltips and ARIA labels for accessibility
- [ ] T106 [P] Update CLAUDE.md to reflect Feature 015 implementation
- [ ] T107 [P] Update backend/docs/ with social links feature documentation
- [ ] T108 Run quickstart.md validation: Execute all cURL scenarios and verify responses
- [ ] T109 Verify OpenAPI docs at /docs show new /social-links endpoints
- [ ] T110 Final test coverage check: Verify ≥90% coverage across all modules

**Checkpoint**: All quality checks passed, documentation updated, feature ready for PR

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational (Phase 2) completion
  - US1 + US5 (P1): Can proceed in parallel after Phase 2
  - US2 + US4 (P2): Can proceed in parallel after Phase 2
  - US3 (P3): **BLOCKED by Feature 011 (Follows)** - implement last
- **Frontend (Phase 8-9)**: Can start after US1 + US5 backend complete
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US5 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US3 (P3)**: **BLOCKED by Feature 011 (Follows)** - requires Follow model and relationship queries

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD workflow)
- Unit tests before integration tests
- Service layer before API layer
- Backend endpoints before frontend components
- Core implementation before integration

### Parallel Opportunities

**Phase 1 (Setup)**:
- T004 (validators install) || T005 (domain allowlist config)

**Phase 2 (Foundational)**:
- T008 (SocialLinkCreate schema) || T009 (SocialLinkUpdate schema) || T010 (SocialLinkResponse schema)

**Phase 3 (US1 Tests)**:
- T013 || T014 || T015 || T016 || T017 || T018 (all unit/contract/integration tests can run in parallel)

**Phase 4 (US5 Tests)**:
- T026 || T027 || T028 || T029 || T030 || T031 || T032 (all tests can run in parallel)

**Phase 5 (US2 Tests)**:
- T039 || T040 || T041 || T042 (all tests can run in parallel)

**Phase 6 (US4 Tests)**:
- T047 || T048 || T049 || T050 (all tests can run in parallel)

**Phase 7 (US3 Tests)**:
- T055 || T056 || T057 || T058 || T059 (all tests can run in parallel)

**Phase 8 (Frontend Display Tests)**:
- T066 || T067 || T068 || T069 (all tests can run in parallel)
- T070 (types) || T071 (enum) || T074 (icons) || T075 (SVG icons)

**Phase 9 (Frontend Editor Tests)**:
- T080 || T081 || T082 || T083 (all tests can run in parallel)

**Phase 10 (Polish)**:
- T095 || T096 || T097 || T098 || T099 || T106 || T107 (documentation and linting tasks)

**User Story Parallelization** (if team has multiple developers):
- Developer A: US1 (Phase 3)
- Developer B: US5 (Phase 4)
- Developer C: US2 (Phase 5)
- Developer D: US4 (Phase 6)
- After Feature 011 available: Developer E: US3 (Phase 7)

---

## Parallel Example: User Story 1 (MVP)

```bash
# Launch all US1 tests together (TDD - RED phase):
Task: "Unit test for URL validation in backend/tests/unit/test_url_validator.py"
Task: "Unit test for domain allowlist validation in backend/tests/unit/test_url_validator.py"
Task: "Unit test for XSS attempt blocking in backend/tests/unit/test_url_validator.py"
Task: "Unit test for SocialLinkService.create_link() in backend/tests/unit/test_social_link_service.py"
Task: "Contract test for POST /social-links in backend/tests/contract/test_social_links_contract.py"
Task: "Integration test for creating PUBLIC Instagram link in backend/tests/integration/test_social_links_api.py"

# After tests FAIL, implement in sequence:
Task: "Implement SocialLinkService.create_link() in backend/src/services/social_link_service.py"
Task: "Implement SocialLinkService.get_user_links() in backend/src/services/social_link_service.py"
Task: "Implement POST /social-links endpoint in backend/src/api/social_links.py"
# ... etc.

# Verify tests now PASS (TDD - GREEN phase)
```

---

## Implementation Strategy

### MVP First (US1 + US5 Only)

**Goal**: Deliver functional social links feature with PUBLIC privacy level only

1. Complete Phase 1: Setup → Database ready
2. Complete Phase 2: Foundational → Foundation ready (CRITICAL blocker)
3. Complete Phase 3: US1 → Users can add PUBLIC links
4. Complete Phase 4: US5 → Users can edit/delete links
5. Complete Phase 8: Frontend Display → Links show on profiles
6. Complete Phase 9: Frontend Editor → Users can manage links via UI
7. **STOP and VALIDATE**: Test US1+US5 independently with manual testing
8. Deploy/demo MVP (PUBLIC privacy only, no COMMUNITY/MUTUAL_FOLLOWERS/HIDDEN yet)

**MVP Scope** (US1 + US5):
- ✅ Add social links (Instagram, Strava, Blog, Portfolio, Custom 1/2)
- ✅ PUBLIC privacy level only
- ✅ URL validation and XSS protection
- ✅ Edit and delete links (owner-only)
- ✅ Frontend display with icons
- ✅ Frontend editor integrated into profile edit page
- ❌ COMMUNITY privacy (Phase 5)
- ❌ HIDDEN privacy (Phase 6)
- ❌ MUTUAL_FOLLOWERS privacy (Phase 7 - blocked by Feature 011)

### Incremental Delivery (All User Stories)

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Phase 3) → Test independently → **MVP Checkpoint 1**
3. Add US5 (Phase 4) → Test independently → **MVP Checkpoint 2** (CREATE + EDIT/DELETE)
4. Add Frontend Display (Phase 8) + Editor (Phase 9) → **MVP Complete** (deploy to staging)
5. Add US2 (Phase 5) → Test independently → **Feature Update 1** (COMMUNITY privacy)
6. Add US4 (Phase 6) → Test independently → **Feature Update 2** (HIDDEN privacy)
7. **WAIT for Feature 011 (Follows)** → Then add US3 (Phase 7) → **Feature Complete** (MUTUAL_FOLLOWERS)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy (4+ Developers)

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. Once Foundational is done:
   - **Developer A**: US1 backend (Phase 3)
   - **Developer B**: US5 backend (Phase 4)
   - **Developer C**: US2 backend (Phase 5)
   - **Developer D**: US4 backend (Phase 6)
3. After backend stories complete:
   - **Developer A**: Frontend Display (Phase 8)
   - **Developer B**: Frontend Editor (Phase 9)
4. When Feature 011 available:
   - **Developer C**: US3 backend (Phase 7)
5. Stories complete and integrate independently

---

## Notes

- **[P] tasks** = different files, no dependencies, can run in parallel
- **[Story] label** = maps task to specific user story for traceability (US1-US5)
- Each user story should be independently completable and testable
- **TDD workflow**: Write tests FIRST → Tests FAIL (RED) → Implement → Tests PASS (GREEN) → Refactor
- Verify tests fail before implementing (RED phase mandatory)
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence
- **US3 BLOCKER**: Feature 011 (Follows) must be implemented before US3 can start
- **MVP Scope**: US1 + US5 + Frontend (Phases 3, 4, 8, 9) is sufficient for initial release
- **Performance Target**: <200ms p95 for profile view with privacy filtering (verify in T100)
- **Security Focus**: XSS sanitization (T015, T102), domain validation (T014, T103)
- **Coverage Requirement**: ≥90% across all modules (verify in T110)

---

**Total Tasks**: 110 tasks across 10 phases
**MVP Tasks**: 48 tasks (Phases 1-4, 8-9)
**Full Feature Tasks**: 110 tasks (all phases)

**Task Breakdown by User Story**:
- US1 (P1): 13 tests + 7 implementation = 20 tasks
- US5 (P1): 7 tests + 6 implementation = 13 tasks
- US2 (P2): 4 tests + 4 implementation = 8 tasks
- US4 (P2): 4 tests + 4 implementation = 8 tasks
- US3 (P3): 5 tests + 6 implementation = 11 tasks
- Frontend Display: 4 tests + 10 implementation = 14 tasks
- Frontend Editor: 4 tests + 11 implementation = 15 tasks
- Setup: 5 tasks
- Foundational: 7 tasks
- Polish: 16 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phases

**Suggested First Sprint (MVP)**: Phases 1-4, 8-9 (48 tasks, ~2-3 weeks with TDD)
