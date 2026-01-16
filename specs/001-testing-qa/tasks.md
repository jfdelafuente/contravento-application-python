# Implementation Tasks: Testing & QA Suite

**Feature**: Testing & QA Suite (001-testing-qa)
**Branch**: `001-testing-qa`
**Generated**: 2026-01-16

## Task Summary

- **Total Tasks**: 73
- **Setup**: 10 tasks
- **Foundational**: 12 tasks
- **User Story 1** (Smoke Tests): 8 tasks
- **User Story 2** (Integration Tests): 15 tasks
- **User Story 3** (E2E Tests): 12 tasks
- **User Story 4** (CI/CD Pipeline): 10 tasks
- **User Story 5** (Performance Tests): 6 tasks

**Estimated Effort**:
- Setup + Foundational: 3-4 days
- User Story 1 (P1): 2-3 days
- User Story 2 (P1): 4-5 days
- User Story 3 (P2): 3-4 days
- User Story 4 (P2): 2-3 days
- User Story 5 (P3): 2-3 days

## Dependency Graph

```text
Phase 1: Setup (blocking all other phases)
  ↓
Phase 2: Foundational (blocking all user stories)
  ↓
Phase 3: User Story 1 - Smoke Tests (P1) ────┐
  ↓                                            │
Phase 4: User Story 2 - Integration Tests (P1)│
  ↓                                            │ Can run in parallel
Phase 5: User Story 3 - E2E Tests (P2) ───────┤ (independent stories)
  ↓                                            │
Phase 6: User Story 4 - CI/CD Pipeline (P2) ──┘
  ↓
Phase 7: User Story 5 - Performance Tests (P3)
```

**Critical Path**: Setup → Foundational → US1 (Smoke) → US2 (Integration) → US4 (CI/CD)
**Parallel Opportunities**: US3 (E2E) can run in parallel with US1/US2 if frontend is stable
**MVP Scope**: Setup + Foundational + US1 (Smoke Tests) - Delivers basic environment validation

---

# Phase 1: Setup (Project Initialization)

**Goal**: Initialize test infrastructure with required dependencies, configuration files, and directory structure.

**Duration**: 1-2 days

**Deliverables**:
- Backend test dependencies installed (pytest, pytest-asyncio, pytest-cov, httpx)
- Frontend E2E dependencies installed (Playwright, @playwright/test)
- Test directory structure created
- Test fixtures directory with sample data
- Pytest and Playwright configuration files

**Tasks**:

- [ ] T001 Add pytest dependencies to backend/pyproject.toml (pytest 7.4+, pytest-asyncio 0.21+, pytest-cov 4.1+, pytest-benchmark 4.0+, httpx, pytest-docker-compose)
- [ ] T002 Create backend pytest configuration in backend/pytest.ini with asyncio mode, coverage settings, and test markers
- [ ] T003 Create backend test directory structure: backend/tests/{unit,integration,contract,performance,fixtures}
- [ ] T004 [P] Add Playwright dependencies to frontend/package.json (@playwright/test 1.40+)
- [ ] T005 [P] Create Playwright configuration in frontend/playwright.config.ts with browser matrix (chromium, firefox, webkit)
- [ ] T006 [P] Create frontend test directory structure: frontend/tests/{e2e,fixtures,helpers}
- [ ] T007 Install Playwright browsers locally with `npx playwright install --with-deps`
- [ ] T008 Create test fixtures directory structure: backend/tests/fixtures/{photos,users.json,trips.json,tags.json}
- [ ] T009 Add sample photos to backend/tests/fixtures/photos/ (sample_1.jpg 500KB, sample_2.jpg 400KB, sample_large.jpg 5MB)
- [ ] T010 Create docker-compose.test.yml for PostgreSQL test container with health checks

**Validation**:
- [ ] `poetry install` completes successfully in backend/
- [ ] `npm install` completes successfully in frontend/
- [ ] `npx playwright --version` shows v1.40+
- [ ] All test directories exist with correct structure
- [ ] Sample photos are present in fixtures/photos/

---

# Phase 2: Foundational (Shared Test Infrastructure)

**Goal**: Create reusable test fixtures, helpers, and base configuration that all user stories will use.

**Duration**: 2-3 days

**Deliverables**:
- Pytest conftest.py with async fixtures for database and HTTP client
- Test fixtures JSON files with sample users, trips, tags
- Base test helpers for authentication and data creation
- Docker test environment configuration

**Tasks**:

- [ ] T011 Create backend/tests/conftest.py with async db_session fixture (SQLite in-memory)
- [ ] T012 Add async client fixture to conftest.py using httpx.AsyncClient with base_url="http://test"
- [ ] T013 Add auth_headers fixture to conftest.py that creates verified user and returns JWT Bearer token
- [ ] T014 Create backend/tests/fixtures/users.json with sample users (admin_user, verified_user, unverified_user)
- [ ] T015 Create backend/tests/fixtures/trips.json with sample trips (draft_trip, published_trip, minimal_trip)
- [ ] T016 Create backend/tests/fixtures/tags.json with sample tags (bikepacking, montaña, road, pirineos)
- [ ] T017 Add fixture loader helper in conftest.py to load JSON fixtures and create database records
- [ ] T018 [P] Add PostgreSQL session fixture to conftest.py using pytest-docker-compose
- [ ] T019 [P] Create test helpers in backend/tests/helpers.py for common operations (create_user, create_trip, upload_photo)
- [ ] T020 [P] Add pytest markers in pytest.ini (unit, integration, e2e, performance, slow)
- [ ] T021 Create .coveragerc configuration file with exclusions for migrations and test files
- [ ] T022 Document test fixture usage in backend/tests/README.md with examples

**Validation**:
- [ ] `pytest --collect-only` shows fixtures are discovered
- [ ] conftest.py fixtures can be imported in test files
- [ ] JSON fixtures load successfully with valid schema
- [ ] PostgreSQL container starts via pytest-docker-compose

---

# Phase 3: User Story 1 - Smoke Tests (Priority: P1)

**Goal**: As a developer, I want to run smoke tests on all 4 deployment modes to verify application starts correctly and critical endpoints respond.

**Why P1**: First line of defense against broken deployments. Catches environment-specific issues that unit tests can't detect.

**Independent Test Criteria**: Run `./scripts/run_smoke_tests.sh <mode>` against each deployment mode and verify all health checks pass within 30 seconds.

**Acceptance Criteria**:
1. Local-dev SQLite mode passes all health checks in <10s
2. Local-minimal PostgreSQL mode validates PostgreSQL-specific features
3. Local-full mode verifies all services (backend, PostgreSQL, Redis, MailHog) are reachable
4. Staging mode validates HTTPS endpoints and production configurations
5. Smoke test failures include specific service, endpoint, and error details

**Tasks**:

- [ ] T023 [US1] Create scripts/run_smoke_tests.sh shell script with mode argument validation (local-dev, local-minimal, local-full, staging)
- [ ] T024 [US1] Implement health check test in run_smoke_tests.sh using curl to GET /health endpoint (expect 200)
- [ ] T025 [US1] Implement auth endpoint test in run_smoke_tests.sh to verify POST /auth/login returns 401 for invalid credentials
- [ ] T026 [US1] Implement auth/me endpoint test in run_smoke_tests.sh to verify GET /auth/me returns 401 without token
- [ ] T027 [US1] Create scripts/check_db.py Python script to test database connectivity (SQLite or PostgreSQL based on mode)
- [ ] T028 [US1] Add database connectivity test to run_smoke_tests.sh calling check_db.py
- [ ] T029 [US1] Add static file serving test to run_smoke_tests.sh (curl frontend index.html, expect 200)
- [ ] T030 [US1] Add exit code handling and colored output (✅ PASS, ❌ FAIL) to run_smoke_tests.sh

**Testing US1**:
```bash
# Run smoke tests for each mode
./scripts/run_smoke_tests.sh local-dev
./scripts/run_smoke_tests.sh local-minimal
./scripts/run_smoke_tests.sh local-full
./scripts/run_smoke_tests.sh staging

# Verify all tests pass in <30 seconds
# Verify failure messages are clear and actionable
```

**Deliverables**:
- scripts/run_smoke_tests.sh (executable shell script)
- scripts/check_db.py (database connectivity checker)
- Documentation in specs/001-testing-qa/quickstart.md updated with smoke test usage

---

# Phase 4: User Story 2 - Integration Tests (Priority: P1)

**Goal**: As a developer, I want integration tests that validate end-to-end user workflows to ensure features work together correctly.

**Why P1**: Catches issues at layer boundaries that unit tests miss. Validates features developed independently still work together.

**Independent Test Criteria**: Run `pytest tests/integration/` against test database and verify all critical paths complete with correct data persistence.

**Acceptance Criteria**:
1. User registration flow creates account, sends verification email, updates status on verification, and login succeeds
2. Trip creation flow creates draft, uploads photos, publishes, and updates stats
3. Concurrent trip updates test optimistic locking and returns 409 on conflicts
4. Access control test verifies authenticated users see all trips, non-authenticated only see public trips
5. Integration test failures include request/response details, database state, and specific assertion

**Tasks**:

- [ ] T031 [US2] Create backend/tests/integration/test_auth_api.py for authentication integration tests
- [ ] T032 [US2] Implement test_register_user_flow in test_auth_api.py (register → verify email → login → get JWT)
- [ ] T033 [US2] Implement test_login_valid_credentials in test_auth_api.py (login with verified user → JWT tokens)
- [ ] T034 [US2] Implement test_login_invalid_credentials in test_auth_api.py (login with wrong password → 401)
- [ ] T035 [US2] Implement test_token_refresh in test_auth_api.py (refresh token → new access token)
- [ ] T036 [P] [US2] Create backend/tests/integration/test_trips_api.py for trip integration tests
- [ ] T037 [P] [US2] Implement test_create_trip_flow in test_trips_api.py (create draft → upload photo → publish → verify stats)
- [ ] T038 [P] [US2] Implement test_concurrent_trip_updates in test_trips_api.py (parallel updates → 409 conflict)
- [ ] T039 [P] [US2] Implement test_trip_photo_upload in test_trips_api.py (upload 3 photos → verify processing → check thumbnails)
- [ ] T040 [P] [US2] Implement test_trip_location_add in test_trips_api.py (add location → verify geocoding → check map data)
- [ ] T041 [P] [US2] Create backend/tests/integration/test_public_feed.py for public feed integration tests
- [ ] T042 [P] [US2] Implement test_anonymous_access in test_public_feed.py (GET /trips/public without auth → published trips only)
- [ ] T043 [P] [US2] Implement test_authenticated_access in test_public_feed.py (GET /trips with auth → includes drafts)
- [ ] T044 [P] [US2] Implement test_access_control in test_public_feed.py (owner can edit/delete, non-owner cannot)
- [ ] T045 [P] [US2] Add SQLAlchemy query logging to detect N+1 queries in integration tests

**Testing US2**:
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_trips_api.py -v

# Run with PostgreSQL (requires Docker)
docker-compose -f docker-compose.test.yml up -d postgres
pytest tests/integration/ --postgresql
docker-compose -f docker-compose.test.yml down

# Verify all tests pass in <5 minutes
# Verify test output includes request/response details on failure
```

**Deliverables**:
- backend/tests/integration/test_auth_api.py (5 tests)
- backend/tests/integration/test_trips_api.py (5 tests)
- backend/tests/integration/test_public_feed.py (3 tests)
- Updated conftest.py with integration test fixtures

---

# Phase 5: User Story 3 - E2E Browser Tests (Priority: P2)

**Goal**: As a QA engineer, I want automated browser tests using Playwright to catch UI bugs and browser-specific issues.

**Why P2**: Validates entire stack from user's perspective. Catches JavaScript errors, CSS issues, and browser compatibility problems.

**Independent Test Criteria**: Run `npm run test:e2e` against running application and verify all user journeys complete in all browsers.

**Acceptance Criteria**:
1. User registration E2E test navigates to /register, fills form, submits, and sees success message
2. Trip creation E2E test completes 4-step wizard, uploads photos via drag-and-drop, and publishes
3. Public feed browsing test views feed, clicks trip card, sees details, views lightbox gallery
4. Location editing test clicks map, sees geocoding modal, edits name, confirms, sees marker
5. E2E test failures include screenshot, browser console logs, and network requests

**Tasks**:

- [ ] T046 [US3] Create frontend/tests/e2e/auth.spec.ts for authentication E2E tests
- [ ] T047 [US3] Implement "User can register" test in auth.spec.ts (navigate /register → fill form → submit → verify success)
- [ ] T048 [US3] Implement "User can login" test in auth.spec.ts (navigate /login → fill credentials → submit → verify dashboard)
- [ ] T049 [P] [US3] Create frontend/tests/e2e/trips.spec.ts for trip management E2E tests
- [ ] T050 [P] [US3] Implement "User can create trip" test in trips.spec.ts (navigate /trips/new → complete wizard → upload photos → publish)
- [ ] T051 [P] [US3] Implement "User can view trip details" test in trips.spec.ts (click trip card → verify title, photos, locations)
- [ ] T052 [P] [US3] Create frontend/tests/e2e/public-feed.spec.ts for public feed E2E tests
- [ ] T053 [P] [US3] Implement "Anonymous user can browse feed" test in public-feed.spec.ts (navigate / → verify trips → click card)
- [ ] T054 [P] [US3] Implement "User can view photo gallery" test in public-feed.spec.ts (click photo → lightbox opens → navigate photos)
- [ ] T055 [P] [US3] Create frontend/tests/e2e/locations.spec.ts for location editing E2E tests
- [ ] T056 [P] [US3] Implement "User can add location via map" test in locations.spec.ts (click map → geocoding modal → edit name → confirm)
- [ ] T057 [US3] Add screenshot capture on failure in playwright.config.ts (screenshot: 'only-on-failure', video: 'retain-on-failure')

**Testing US3**:
```bash
# Run all E2E tests
npm run test:e2e

# Run in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Run in headed mode (see browser)
npx playwright test --headed

# Run with UI mode (interactive debugging)
npx playwright test --ui

# Verify all tests pass in <10 minutes across 3 browsers
# Verify screenshots saved on failure
```

**Deliverables**:
- frontend/tests/e2e/auth.spec.ts (2 tests)
- frontend/tests/e2e/trips.spec.ts (2 tests)
- frontend/tests/e2e/public-feed.spec.ts (2 tests)
- frontend/tests/e2e/locations.spec.ts (1 test)
- Updated playwright.config.ts with retry and screenshot settings

---

# Phase 6: User Story 4 - CI/CD Pipeline (Priority: P2)

**Goal**: As a project maintainer, I want a CI/CD pipeline that automatically runs all tests on every PR and blocks merge if tests fail.

**Why P2**: Enforces quality gates and prevents broken code from reaching main branch. Runs tests in clean environments.

**Independent Test Criteria**: Create test PR, verify GitHub Actions runs all test suites, and confirm merge is blocked if tests fail.

**Acceptance Criteria**:
1. PR opened triggers GitHub Actions workflow that runs unit tests in <5 minutes with coverage report
2. PR with failing tests shows red X, merge button disabled, and failure details in logs
3. PR with <90% coverage fails workflow with message indicating which modules need tests
4. PR with passing tests and ≥90% coverage triggers automated deployment to staging
5. Staging deployment success posts comment to PR with deployment URL and test results

**Tasks**:

- [ ] T058 [US4] Create .github/workflows/test.yml for CI/CD test workflow
- [ ] T059 [US4] Add backend unit tests job to test.yml (setup Python, cache Poetry, install deps, run pytest)
- [ ] T060 [US4] Add backend integration tests job to test.yml (start PostgreSQL container, run integration tests)
- [ ] T061 [US4] Add coverage check to test.yml (pytest --cov=src --cov-report=term --cov-fail-under=90)
- [ ] T062 [US4] Add frontend E2E tests job to test.yml (setup Node, cache npm, install Playwright, run tests)
- [ ] T063 [P] [US4] Add caching for Poetry dependencies in test.yml (actions/cache with poetry.lock hash key)
- [ ] T064 [P] [US4] Add caching for npm dependencies in test.yml (actions/cache with package-lock.json hash key)
- [ ] T065 [P] [US4] Add caching for Playwright browsers in test.yml (actions/cache with ms-playwright path)
- [ ] T066 [US4] Create .github/workflows/deploy-staging.yml for automated staging deployment
- [ ] T067 [US4] Add smoke tests post-deployment step to deploy-staging.yml (run scripts/run_smoke_tests.sh staging)

**Testing US4**:
```bash
# Create test PR with intentionally failing test
git checkout -b test-ci-failure
# Add failing test to backend/tests/unit/test_sample.py
git commit -m "test: add failing test for CI validation"
git push origin test-ci-failure
# Open PR on GitHub

# Verify:
# - GitHub Actions workflow runs automatically
# - Red X appears on PR
# - Merge button is disabled
# - Workflow logs show test failure details

# Fix test and push
# Verify:
# - Green checkmark appears
# - Merge button is enabled
# - Coverage report shows ≥90%
```

**Deliverables**:
- .github/workflows/test.yml (main CI pipeline)
- .github/workflows/deploy-staging.yml (staging deployment)
- Updated README with CI/CD badge and workflow documentation

---

# Phase 7: User Story 5 - Performance Tests (Priority: P3)

**Goal**: As a developer, I want automated performance tests that measure response times and fail if latency exceeds thresholds.

**Why P3**: Catches code changes that degrade response times. Ensures SLAs are met.

**Independent Test Criteria**: Run `pytest tests/performance/` with load simulation and verify all endpoint latencies meet thresholds.

**Acceptance Criteria**:
1. Performance tests execute 100 concurrent requests to GET /trips/public with p95 <200ms
2. Performance test fails if code change increases p95 latency by >20%
3. Photo upload test validates 5MB file processing completes in <2s
4. Auth endpoint test simulates 1000 login attempts with rate limiting and <500ms p95
5. Performance test failures include detailed latency percentiles, SQL query times, resource utilization

**Tasks**:

- [ ] T068 [P] [US5] Create backend/tests/performance/test_latency.py for endpoint latency tests
- [ ] T069 [P] [US5] Implement test_trips_public_latency in test_latency.py using pytest-benchmark (p95 <200ms)
- [ ] T070 [P] [US5] Implement test_auth_login_latency in test_latency.py using pytest-benchmark (p95 <500ms)
- [ ] T071 [P] [US5] Implement test_photo_upload_latency in test_latency.py (5MB file upload <2s)
- [ ] T072 [P] [US5] Create backend/tests/performance/locustfile.py for load testing with 100 concurrent users
- [ ] T073 [US5] Add performance baseline storage in backend/tests/performance/baselines/ with JSON format

**Testing US5**:
```bash
# Run performance tests with baseline comparison
pytest tests/performance/ --benchmark-compare=baseline_v1

# Save new baseline (after stable release)
pytest tests/performance/ --benchmark-autosave --benchmark-save=baseline_v1

# Run load tests with Locust
locust -f tests/performance/locustfile.py --headless -u 100 -r 10 --run-time 2m

# Verify:
# - All latency tests pass thresholds
# - No >20% regression from baseline
# - Load test completes without errors
```

**Deliverables**:
- backend/tests/performance/test_latency.py (3 tests)
- backend/tests/performance/locustfile.py (Locust load test)
- backend/tests/performance/baselines/baseline_v1.json
- Updated quickstart.md with performance testing guide

---

# Implementation Strategy

## MVP Scope (Minimum Viable Product)

**Goal**: Deliver smoke tests (US1) as MVP to enable basic environment validation before committing code.

**Included**:
- Phase 1: Setup (all tasks)
- Phase 2: Foundational (all tasks)
- Phase 3: User Story 1 - Smoke Tests (all tasks)

**Excluded** (Future iterations):
- Integration tests (US2)
- E2E tests (US3)
- CI/CD pipeline (US4)
- Performance tests (US5)

**Rationale**: Smoke tests provide immediate value by catching deployment issues quickly (<30s) without requiring complex test infrastructure. Developers can run smoke tests locally before pushing, preventing broken commits.

**Timeline**: ~5 days (2 days setup + 3 days smoke tests)

---

## Parallel Execution Opportunities

### Phase 3-5 (User Stories 1-3)

**Can run in parallel**:
- US1 (Smoke Tests) - Backend-focused, shell scripts
- US3 (E2E Tests) - Frontend-focused, Playwright

**Sequential dependency**:
- US2 (Integration Tests) - Requires US1 smoke tests to validate environment first

**Team Assignment Example**:
- Developer A: US1 (Smoke Tests) + US2 (Integration Tests)
- Developer B: US3 (E2E Tests)
- QA Engineer: Test validation and documentation

**Time Savings**: ~4 days (US3 runs in parallel with US1/US2)

---

## Incremental Delivery Plan

**Iteration 1** (MVP):
- Setup + Foundational + US1 (Smoke Tests)
- Deliverable: `./scripts/run_smoke_tests.sh` working for all 4 modes
- Value: Fast environment validation (<30s)

**Iteration 2**:
- US2 (Integration Tests)
- Deliverable: `pytest tests/integration/` covering auth, trips, public feed
- Value: Automated regression testing for critical workflows

**Iteration 3**:
- US3 (E2E Tests)
- Deliverable: `npm run test:e2e` covering registration, trips, feed
- Value: Browser compatibility validation across Chrome/Firefox/Safari

**Iteration 4**:
- US4 (CI/CD Pipeline)
- Deliverable: GitHub Actions workflows for automated testing on PRs
- Value: Automated quality gates preventing broken code in main branch

**Iteration 5**:
- US5 (Performance Tests)
- Deliverable: `pytest tests/performance/` with baseline comparison
- Value: Performance regression detection

---

## Success Metrics

**After MVP (Iteration 1)**:
- [ ] Smoke tests pass for all 4 deployment modes in <30s
- [ ] Developers can run smoke tests locally before commits
- [ ] Smoke test failures provide clear error messages

**After Iteration 2**:
- [ ] Integration tests achieve ≥90% coverage
- [ ] Integration tests complete in <5 minutes
- [ ] Integration tests catch layer boundary issues

**After Iteration 3**:
- [ ] E2E tests pass across Chrome, Firefox, Safari
- [ ] E2E tests complete in <10 minutes
- [ ] Flaky test rate <5%

**After Iteration 4**:
- [ ] CI/CD pipeline runs on every PR
- [ ] PRs with failing tests are blocked from merge
- [ ] Staging deploys automatically on main branch merge

**After Iteration 5**:
- [ ] Performance tests detect >20% latency regressions
- [ ] Performance baselines stored in version control
- [ ] Load tests simulate 100 concurrent users

---

## Next Steps

1. **Review this task breakdown** with team and approve approach
2. **Start with Phase 1 (Setup)** - Complete T001-T010 first
3. **Validate setup** - Ensure all dependencies install correctly
4. **Begin Phase 2 (Foundational)** - Create reusable fixtures and helpers
5. **Implement MVP** - Focus on US1 (Smoke Tests) for quick wins
6. **Iterate** - Add integration tests, E2E tests, CI/CD, performance tests

**Ready to start?** Begin with T001: Add pytest dependencies to backend/pyproject.toml
