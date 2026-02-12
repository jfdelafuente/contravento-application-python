# Feature Specification: Testing & QA Suite

**Feature Branch**: `001-testing-qa`
**Created**: 2026-01-16
**Status**: Draft
**Input**: User description: "Testing & QA Suite - Create comprehensive automated testing infrastructure including smoke tests, integration tests, E2E tests, and CI/CD pipeline for validating all 12 completed features across 4 deployment modes"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Smoke Tests for All Deployment Modes (Priority: P1)

As a developer, I want to run smoke tests on all 4 deployment modes (local-dev SQLite, local-minimal PostgreSQL, local-full, staging) to verify that the application starts correctly and critical endpoints respond before I commit code changes.

**Why this priority**: Smoke tests are the first line of defense against broken deployments. They catch environment-specific issues (database connectivity, missing env vars, service dependencies) that unit tests can't detect. This is P1 because deployments failing to start causes complete service outages.

**Independent Test**: Can be fully tested by running `./run_smoke_tests.sh <mode>` against each deployment mode and verifying all health checks pass, delivering immediate confidence that the environment is operational.

**Acceptance Scenarios**:

1. **Given** local-dev SQLite mode is running, **When** smoke tests execute, **Then** all health checks (database connection, auth endpoints, static file serving) pass within 10 seconds
2. **Given** local-minimal PostgreSQL mode is running, **When** smoke tests execute, **Then** PostgreSQL-specific features (UUID types, array columns) work correctly
3. **Given** local-full mode is running, **When** smoke tests execute, **Then** all services (backend, PostgreSQL, Redis, MailHog) are reachable and functional
4. **Given** staging mode is deployed, **When** smoke tests execute, **Then** HTTPS endpoints, email delivery, and production configurations are validated
5. **Given** any smoke test fails, **When** developer views results, **Then** failure details include specific service, endpoint, and error message for quick debugging

---

### User Story 2 - Integration Tests for Critical User Journeys (Priority: P1)

As a developer, I want integration tests that validate end-to-end user workflows (registration → verification → login → create trip → upload photos) to ensure that all features work together correctly and database transactions maintain data integrity.

**Why this priority**: Integration tests catch issues at layer boundaries (API ↔ Service ↔ Database) that unit tests miss. They validate that features developed independently still work together. This is P1 because broken integration causes user-facing failures even when individual components pass unit tests.

**Independent Test**: Can be fully tested by running `pytest tests/integration/` against a test database and verifying all critical paths complete successfully with correct data persistence, delivering confidence that user workflows function correctly.

**Acceptance Scenarios**:

1. **Given** a fresh test database, **When** running the "user registration flow" integration test, **Then** user account is created, verification email is sent, email verification updates user status, and login succeeds with valid JWT tokens
2. **Given** an authenticated test user, **When** running the "trip creation flow" integration test, **Then** trip is created as draft, photos are uploaded and processed, trip is published, and stats are updated (trip_count, distance_km, photo_count)
3. **Given** multiple concurrent requests, **When** running the "concurrent trip updates" integration test, **Then** optimistic locking prevents data corruption and correct conflict errors (409) are returned
4. **Given** public and private trips, **When** running the "access control" integration test, **Then** authenticated users see all their trips, non-authenticated users only see published public trips, and draft trips remain private
5. **Given** any integration test fails, **When** developer views results, **Then** failure includes request/response details, database state, and specific assertion that failed

---

### User Story 3 - End-to-End Browser Tests with Playwright (Priority: P2)

As a QA engineer, I want automated browser tests using Playwright that simulate real user interactions (click buttons, fill forms, upload files) across Chrome, Firefox, and Safari to catch UI bugs and browser-specific issues before production deployment.

**Why this priority**: E2E tests validate the entire stack (frontend React → Axios → backend API → PostgreSQL) from a user's perspective. They catch JavaScript errors, CSS layout issues, and browser compatibility problems. This is P2 because manual testing can catch these issues, but automation saves time and prevents regressions.

**Independent Test**: Can be fully tested by running `npm run test:e2e` against a running application instance and verifying all user journeys complete in all browsers, delivering confidence that the UI works correctly for real users.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** running the "user registration E2E test" in Chrome, **Then** user can navigate to /register, fill form with valid data, submit, receive success message, and see verification prompt
2. **Given** a verified test user, **When** running the "trip creation E2E test" in Firefox, **Then** user can navigate to /trips/new, complete the wizard (4 steps), upload 3 photos via drag-and-drop, publish trip, and see trip in dashboard
3. **Given** public trips exist, **When** running the "public feed browsing E2E test" in Safari, **Then** non-authenticated user can view feed, click trip card, see trip details, view photos in lightbox gallery, and click map markers
4. **Given** trip detail page with map, **When** running the "location editing E2E test", **Then** user can click map, see reverse geocoding modal, edit location name, confirm, and see location marker on map
5. **Given** any E2E test fails, **When** developer views results, **Then** failure includes screenshot of page at failure point, browser console logs, and network requests for debugging

---

### User Story 4 - CI/CD Pipeline with GitHub Actions (Priority: P2)

As a project maintainer, I want a CI/CD pipeline that automatically runs all tests (unit, integration, E2E) on every pull request and blocks merge if tests fail or coverage drops below 90%, ensuring code quality and preventing regressions.

**Why this priority**: Automated CI/CD enforces quality gates and prevents broken code from reaching main branch. It runs tests in clean environments (not developer machines) and provides consistent feedback. This is P2 because manual testing can still catch issues, but automation scales better and reduces human error.

**Independent Test**: Can be fully tested by creating a test pull request, verifying GitHub Actions workflow runs all test suites, and confirming merge is blocked if tests fail, delivering confidence that quality gates are enforced.

**Acceptance Scenarios**:

1. **Given** a pull request is opened, **When** GitHub Actions workflow runs, **Then** all unit tests execute in under 5 minutes with coverage report generated
2. **Given** a pull request with failing tests, **When** developer views CI status, **Then** PR shows red X, merge button is disabled, and test failure details are visible in workflow logs
3. **Given** a pull request with coverage below 90%, **When** GitHub Actions workflow runs, **Then** workflow fails with clear message indicating which modules need more tests
4. **Given** a pull request with passing tests and ≥90% coverage, **When** developer merges PR, **Then** automated deployment to staging environment begins with smoke tests running post-deployment
5. **Given** staging deployment succeeds, **When** smoke tests pass, **Then** GitHub Actions posts success comment to PR with deployment URL and test results summary

---

### User Story 5 - Performance Regression Testing (Priority: P3)

As a developer, I want automated performance tests that measure response times for critical endpoints (GET /trips/public, POST /auth/login, POST /trips) and fail if p95 latency exceeds thresholds (200ms for simple queries, 500ms for auth, 2s for photo uploads), preventing performance regressions.

**Why this priority**: Performance tests catch code changes that degrade response times (N+1 queries, missing indexes, inefficient algorithms). They ensure SLAs are met. This is P3 because performance issues often manifest gradually and can be caught in staging, but automation prevents them from reaching production.

**Independent Test**: Can be fully tested by running `pytest tests/performance/` with load simulation and verifying all endpoint latencies meet thresholds, delivering confidence that performance requirements are maintained.

**Acceptance Scenarios**:

1. **Given** the backend is running, **When** performance tests execute 100 concurrent requests to GET /trips/public, **Then** p95 response time is under 200ms and no database connection pool exhaustion occurs
2. **Given** performance baseline is established, **When** a code change increases p95 latency by >20%, **Then** performance test fails with detailed metrics comparison (before/after)
3. **Given** photo upload endpoint is tested, **When** uploading 5MB file, **Then** total processing time (upload + resize + save) is under 2 seconds and background tasks complete within 5 seconds
4. **Given** authentication endpoints are tested, **When** simulating 1000 login attempts, **Then** rate limiting prevents brute force (5 attempts per 15 min), legitimate requests complete under 500ms, and JWT token generation scales linearly
5. **Given** any performance test fails, **When** developer views results, **Then** report includes detailed latency percentiles (p50, p75, p95, p99), SQL query execution times, and resource utilization (CPU, memory, DB connections)

---

### Edge Cases

- What happens when smoke tests run against a deployment mode where services fail to start (e.g., PostgreSQL container crashes)? → Test framework should detect service unavailability within timeout (30s), fail fast with clear error message, and exit with non-zero code
- How does the CI/CD pipeline handle flaky E2E tests that pass 90% of the time but randomly fail due to timing issues? → Implement automatic retry mechanism (up to 3 retries) with exponential backoff and mark test as "flaky" if it passes on retry
- What happens when integration tests run in parallel and two tests try to create the same test user? → Use unique test data per test (UUID-based usernames/emails) and database isolation (transactions rolled back after each test)
- How does performance testing avoid false negatives when CI/CD runner is under heavy load? → Run performance tests on dedicated runner with guaranteed resources or use relative thresholds (compare against baseline on same hardware)
- What happens when GitHub Actions workflow fails mid-deployment to staging? → Implement rollback mechanism to previous version and send notification to team with failure details
- How does the test suite handle timezone differences between developer machines and CI/CD runners? → All timestamps use UTC (`datetime.now(UTC)`) and tests assert on UTC values to ensure consistency
- What happens when E2E tests need to upload photos but test fixtures are missing? → Test setup validates fixture availability before running and fails early with clear error if files are missing
- How does the system handle testing email delivery when SMTP server is not available in local-dev mode? → Use MailHog in local-full mode for email testing or mock email service in unit/integration tests

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide smoke test scripts for all 4 deployment modes (local-dev, local-minimal, local-full, staging) that validate critical services are running and accessible
- **FR-002**: Smoke tests MUST verify database connectivity (SQLite or PostgreSQL depending on mode), test data creation, and basic CRUD operations within 30 seconds
- **FR-003**: Smoke tests MUST validate authentication endpoints (register, login, refresh token) return expected status codes (200, 401, 422) with valid response schemas
- **FR-004**: Smoke tests MUST verify static file serving (frontend build files, uploaded photos) returns correct MIME types and status codes
- **FR-005**: Integration tests MUST cover all 12 completed features (user profiles, travel diary, stats, social, public feed, GPS coordinates, reverse geocoding, etc.) with end-to-end workflows
- **FR-006**: Integration tests MUST validate database transaction integrity (commits on success, rollbacks on error) and foreign key constraints
- **FR-007**: Integration tests MUST test authentication and authorization (JWT token validation, role-based access control, owner-only actions)
- **FR-008**: Integration tests MUST verify photo upload and processing workflow (file validation, storage, thumbnail generation, metadata extraction)
- **FR-009**: Integration tests MUST test optimistic locking for concurrent trip updates (version conflicts return 409 status)
- **FR-010**: E2E tests MUST use Playwright to automate browser interactions across Chrome, Firefox, and Safari (minimum 3 browsers)
- **FR-011**: E2E tests MUST cover critical user journeys: registration → verification → login → dashboard → create trip → upload photos → publish → view in public feed
- **FR-012**: E2E tests MUST capture screenshots on failure and save browser console logs for debugging
- **FR-013**: E2E tests MUST test responsive design breakpoints (mobile 375px, tablet 768px, desktop 1024px)
- **FR-014**: E2E tests MUST validate accessibility features (ARIA labels, keyboard navigation, screen reader compatibility)
- **FR-015**: CI/CD pipeline MUST run on GitHub Actions with workflows triggered on pull requests and pushes to main/develop branches
- **FR-016**: CI/CD pipeline MUST execute all test suites (unit, integration, E2E) in parallel where possible to minimize total runtime
- **FR-017**: CI/CD pipeline MUST block merge if any test fails or code coverage drops below 90%
- **FR-018**: CI/CD pipeline MUST generate and publish coverage reports with file-level and function-level breakdowns
- **FR-019**: CI/CD pipeline MUST deploy to staging environment on successful merge to develop branch and run post-deployment smoke tests
- **FR-020**: CI/CD pipeline MUST send notifications (GitHub comments, Slack messages) on build failures with links to logs and failure details
- **FR-021**: Performance tests MUST measure p95 latency for critical endpoints and fail if thresholds are exceeded (200ms simple queries, 500ms auth, 2s photo uploads)
- **FR-022**: Performance tests MUST simulate realistic load (100 concurrent users) and measure database connection pool utilization
- **FR-023**: Performance tests MUST identify N+1 query problems by counting SQL queries per request and failing if unexpected queries occur
- **FR-024**: Test framework MUST use pytest for backend tests with fixtures for database setup/teardown and authentication
- **FR-025**: Test framework MUST use Playwright Test for E2E tests with built-in test runners and reporters
- **FR-026**: Test data MUST be isolated per test using unique identifiers (UUIDs) to prevent conflicts in parallel execution
- **FR-027**: Test database MUST reset to clean state before each test using transactions or database migrations
- **FR-028**: All tests MUST run in both SQLite (fast local development) and PostgreSQL (production parity) modes to catch dialect-specific issues
- **FR-029**: Test results MUST include execution time per test to identify slow tests and optimization opportunities
- **FR-030**: Documentation MUST include setup instructions for running tests locally, CI/CD pipeline configuration, and troubleshooting guide

### Key Entities

- **Smoke Test Suite**: Collection of quick health checks (10-30 seconds) that validate deployment environment is operational (database, API, static files)
- **Integration Test Suite**: Collection of tests that validate multi-layer interactions (API → Service → Database) with real database transactions
- **E2E Test Suite**: Collection of Playwright tests that simulate user interactions in real browsers (click, type, navigate)
- **CI/CD Workflow**: GitHub Actions YAML configuration defining test execution, coverage reporting, and deployment steps
- **Performance Test Suite**: Collection of tests that measure response times under load and validate against SLA thresholds
- **Test Fixture**: Reusable test data (users, trips, photos) created before tests and cleaned up after
- **Coverage Report**: HTML and JSON reports showing code coverage percentages per file/function with line-by-line annotations

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can run smoke tests locally in under 30 seconds per deployment mode and get pass/fail result with specific failure details
- **SC-002**: CI/CD pipeline completes all test suites (unit + integration + E2E) in under 15 minutes on pull requests
- **SC-003**: Code coverage remains at or above 90% for all modules with coverage report accessible in GitHub Actions artifacts
- **SC-004**: E2E tests catch 95% of UI regressions before they reach production (measured by comparing E2E failures to production bug reports)
- **SC-005**: Flaky test rate is below 5% (tests that fail randomly without code changes) measured over 30-day rolling window
- **SC-006**: Zero false positives in smoke tests (tests never fail when services are actually healthy)
- **SC-007**: Performance tests detect 100% of regressions where p95 latency increases by >20% compared to baseline
- **SC-008**: Developers can run full integration test suite locally in under 5 minutes with clear test output and failure details
- **SC-009**: All 12 completed features have integration test coverage with at least one test per critical path
- **SC-010**: E2E tests run successfully on all 3 browsers (Chrome, Firefox, Safari) with consistent results
- **SC-011**: CI/CD pipeline automatically deploys to staging within 10 minutes of merge to develop branch with zero manual steps
- **SC-012**: Test documentation is comprehensive enough that new developers can set up and run tests within 30 minutes without assistance
- **SC-013**: GitHub Actions provides clear pass/fail status on PRs within 15 minutes with links to detailed test reports
- **SC-014**: Performance regression tests prevent deployment of changes that would violate SLAs (>200ms simple queries, >500ms auth, >2s photo uploads)
- **SC-015**: Test suite identifies and reports specific SQL queries causing N+1 problems or missing indexes

## Assumptions

1. **GitHub Actions Availability**: GitHub Actions is available for private repositories with sufficient runner minutes quota (assumption: paid plan or enterprise account)
2. **Playwright Browser Binaries**: CI/CD runners have permissions to download Playwright browser binaries (Chromium, Firefox, WebKit) during setup phase
3. **Staging Environment**: Dedicated staging environment exists with separate PostgreSQL database, domain name, and SSL certificates
4. **Test Data Retention**: Staging database can be reset periodically (weekly) to clean up test data without affecting production
5. **Email Testing**: MailHog is available in local-full mode for testing email delivery; staging uses real SMTP with test accounts
6. **Photo Storage**: Test photo fixtures (5MB sample images) are committed to repository under `tests/fixtures/photos/` for E2E upload tests
7. **Network Bandwidth**: CI/CD runners have sufficient bandwidth to download dependencies (Poetry packages, npm modules, Playwright browsers) within 5 minutes
8. **PostgreSQL Version**: Staging PostgreSQL version matches production (PostgreSQL 14+) to ensure migration compatibility
9. **Timezone Consistency**: All tests assume UTC timezone for timestamps to avoid daylight saving time issues
10. **Parallel Execution**: Integration tests are designed for parallel execution with database isolation (separate schemas or transactions)
11. **Browser Support**: E2E tests target modern browsers (Chrome/Edge 90+, Firefox 88+, Safari 14+) and do not test legacy browsers (IE11, Opera Mini)
12. **Performance Baseline**: Initial baseline for performance tests is established on dedicated hardware before enabling regression detection
13. **Secrets Management**: GitHub Actions has access to secrets (DATABASE_URL, SECRET_KEY, SMTP credentials) via repository secrets
14. **SQLite Limitations**: Some PostgreSQL-specific features (ARRAY columns, native UUIDs) may have different behavior in SQLite tests; tests account for dialect differences

## Dependencies

### External Dependencies

- **Pytest Framework** (v7.4+): Backend testing framework with fixtures, parametrization, and coverage integration
- **Pytest-Asyncio** (v0.21+): Async test support for FastAPI async endpoints
- **Pytest-Cov** (v4.1+): Code coverage measurement and reporting
- **Playwright** (v1.40+): Browser automation for E2E tests with built-in test runner
- **Playwright Test** (@playwright/test v1.40+): Test runner and assertions for E2E tests
- **GitHub Actions**: CI/CD platform for automated test execution and deployment
- **MailHog** (v1.0+): Email testing server for local-full mode (already in docker-compose.yml)
- **Locust** (v2.17+): Optional load testing tool for performance tests with realistic user simulation

### Internal Dependencies

- **All 12 Completed Features**: Testing infrastructure must cover user profiles (001), travel diary (002), stats (003-004), social (005-007), frontend (008), GPS (009), reverse geocoding (010), profile frontend (011), TypeScript fixes (012), public feed (013)
- **Deployment Scripts**: Smoke tests rely on `deploy.sh` and `run-local-dev.sh` scripts to start environments
- **Environment Configurations**: Tests use `.env.example`, `.env.local-minimal.example`, `.env.local-full.example` for configuration
- **Database Migrations**: Integration tests require all Alembic migrations to run successfully
- **Test User Scripts**: Integration tests use `create_admin.py` and `create_verified_user.py` scripts for test data setup

## Out of Scope

1. **Load Testing at Scale**: Simulating thousands of concurrent users (beyond 100) for capacity planning is not included; focus is on regression detection
2. **Security Penetration Testing**: Automated vulnerability scanning (SQL injection, XSS, CSRF) is not included; manual security audits remain separate
3. **Visual Regression Testing**: Pixel-perfect screenshot comparison to detect CSS changes is not included; E2E tests validate functionality, not visual design
4. **Chaos Engineering**: Random failure injection (database crashes, network partitions) to test resilience is not included
5. **Mobile App Testing**: Testing native mobile apps (iOS/Android) is out of scope; responsive design testing in browsers is included
6. **Third-Party API Mocking**: Mocking external services (Nominatim geocoding, Cloudflare Turnstile) is not included; tests use real APIs or skip if unavailable
7. **Multi-Region Deployment**: Testing across multiple geographic regions (US, EU, Asia) is not included; focus is on single-region staging
8. **Backward Compatibility Testing**: Testing upgrades from previous versions (v1.0 → v2.0) is not included; only current version is tested
9. **Accessibility Audit Tools**: Automated accessibility scanning (Axe, Lighthouse) beyond basic ARIA validation is not included
10. **Contract Testing**: Testing API contracts between frontend and backend independently (Pact, Spring Cloud Contract) is not included; integration tests cover both layers together

## Risks and Mitigations

### Risk 1: Flaky E2E Tests Due to Timing Issues

**Description**: E2E tests may fail intermittently due to race conditions (clicking buttons before they're enabled, asserting on elements before they render).

**Mitigation**:
- Use Playwright's built-in auto-waiting (waits for elements to be visible, enabled, stable before interacting)
- Set explicit timeout for slow operations (file uploads, API calls) with `page.waitForTimeout()`
- Implement retry mechanism in CI/CD (up to 3 retries for flaky tests)
- Track flaky test rate and investigate tests that fail >5% of the time

---

### Risk 2: Test Suite Runtime Exceeds CI/CD Budget

**Description**: Running all tests (unit + integration + E2E) on every PR may exceed GitHub Actions free tier minutes or delay developer feedback.

**Mitigation**:
- Run smoke tests and unit tests on every PR (fast, <5 min)
- Run integration tests only on PRs targeting main/develop branches
- Run E2E tests only on merge to develop or manually triggered
- Use matrix strategy to parallelize E2E tests across browsers
- Cache dependencies (Poetry, npm, Playwright browsers) to reduce setup time

---

### Risk 3: Test Database Conflicts in Parallel Execution

**Description**: Integration tests running in parallel may create conflicting data (same usernames, overlapping trip IDs) causing failures.

**Mitigation**:
- Use UUID-based unique identifiers for all test data (usernames like `testuser_{uuid}`)
- Use pytest-xdist with separate database schemas per worker
- Implement database isolation via transactions (rollback after each test)
- Add unique constraints to database schema to fail fast on conflicts

---

### Risk 4: Staging Environment Drift from Production

**Description**: Staging environment may diverge from production (different PostgreSQL version, outdated migrations) causing tests to pass in staging but fail in production.

**Mitigation**:
- Use Infrastructure as Code (Docker Compose, deploy scripts) to ensure staging mirrors production
- Run same smoke tests on both staging and production post-deployment
- Monitor production metrics (latency, error rates) and compare to staging baselines
- Implement automated staging refresh (weekly reset to production snapshot)

---

### Risk 5: Performance Tests Give False Negatives on Shared CI Runners

**Description**: Performance tests may report failures when CI runner is under heavy load from other jobs, not due to actual code regressions.

**Mitigation**:
- Use relative thresholds (compare to baseline on same hardware, not absolute values)
- Run performance tests on dedicated runners with guaranteed resources
- Implement warmup period before measurements to stabilize CPU/memory
- Track long-term trends (30-day average) instead of single-run results

## Notes

- **Test Pyramid Philosophy**: The test suite follows the test pyramid (many unit tests, fewer integration tests, even fewer E2E tests) to balance coverage with speed
- **Shift-Left Testing**: Developers run smoke tests and unit tests locally before pushing to catch issues early
- **Continuous Integration**: Every commit triggers automated tests to provide fast feedback on code quality
- **Continuous Deployment**: Successful merges to develop automatically deploy to staging for validation before production
- **Test Data Fixtures**: Reusable fixtures in `tests/fixtures/` include sample users, trips, and photos for consistent test data
- **Spanish Error Messages**: E2E tests validate that all user-facing errors are in Spanish, not English
- **PostgreSQL vs SQLite**: Integration tests run in both SQLite (fast local) and PostgreSQL (production parity) to catch dialect-specific issues
- **Coverage Enforcement**: Pre-commit hook or CI check prevents merging code that drops coverage below 90%
- **Test Documentation**: README in `tests/` directory explains how to run tests, interpret results, and add new tests
- **Future Enhancements**: Future features (user notifications, trip recommendations, mobile app) will require expanding test suite coverage
