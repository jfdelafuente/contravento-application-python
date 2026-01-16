# Implementation Plan: Testing & QA Suite

**Branch**: `001-testing-qa` | **Date**: 2026-01-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-testing-qa/spec.md`

## Summary

Create comprehensive automated testing infrastructure to validate all 12 completed features across 4 deployment modes (local-dev SQLite, local-minimal PostgreSQL, local-full Docker, staging). The suite includes smoke tests for environment validation, integration tests for critical workflows, E2E browser tests with Playwright, CI/CD pipeline with GitHub Actions, and performance regression tests.

**Primary Technical Approach**:
- Smoke tests: Shell scripts + curl for health checks across deployment modes
- Integration tests: Pytest with async fixtures for FastAPI endpoints + PostgreSQL/SQLite
- E2E tests: Playwright Test for browser automation (Chrome, Firefox, Safari)
- CI/CD: GitHub Actions workflows with parallel execution and coverage reporting
- Performance tests: Pytest-benchmark with Locust for load simulation

## Technical Context

**Language/Version**: Python 3.12 (backend tests), TypeScript 5.x (frontend E2E tests)
**Primary Dependencies**:
- Backend: pytest 7.4+, pytest-asyncio 0.21+, pytest-cov 4.1+, pytest-benchmark 4.0+, httpx (async client)
- Frontend: @playwright/test 1.40+, Playwright 1.40+ (browser drivers)
- CI/CD: GitHub Actions (built-in), Locust 2.17+ (performance)

**Storage**:
- Test databases: SQLite in-memory for unit tests, PostgreSQL test container for integration tests
- Test fixtures: JSON files in `tests/fixtures/` for sample data (users, trips, photos)
- Coverage data: `.coverage` file, HTML reports in `htmlcov/`

**Testing**:
- Unit: pytest with fixtures for FastAPI TestClient and async database sessions
- Integration: pytest with Docker Compose for service dependencies (PostgreSQL, Redis, MailHog)
- E2E: Playwright Test with browser contexts and screenshot capture
- Performance: pytest-benchmark + Locust for load testing

**Target Platform**:
- Development: Windows/Linux/macOS (cross-platform test execution)
- CI/CD: GitHub-hosted runners (Ubuntu 22.04 for Linux, Windows Server 2022, macOS 13)
- Staging: Docker containers (PostgreSQL, Nginx, Redis)

**Project Type**: Web application (backend FastAPI + frontend React/Vite)

**Performance Goals**:
- Smoke tests: <30 seconds per deployment mode
- Unit tests: <5 minutes total, <100ms per test
- Integration tests: <5 minutes total with parallel execution
- E2E tests: <10 minutes across 3 browsers
- CI/CD pipeline: <15 minutes total (unit + integration + E2E)
- Coverage reporting: <2 minutes to generate HTML report

**Constraints**:
- GitHub Actions free tier: 2000 minutes/month (optimize test execution time)
- Test database must reset to clean state between tests (transaction isolation or migrations)
- E2E tests must handle flaky tests (<5% failure rate on retries)
- Performance tests must not impact production (run on dedicated staging environment)
- All tests must pass on both SQLite (local) and PostgreSQL (production parity)

**Scale/Scope**:
- 12 existing features to cover (user profiles, travel diary, stats, social, GPS, geocoding, public feed)
- ~50 unit tests, ~30 integration tests, ~15 E2E tests (estimated based on features)
- 4 deployment modes to validate (local-dev, local-minimal, local-full, staging)
- 3 browsers for E2E testing (Chrome, Firefox, Safari/WebKit)
- 100 concurrent users for performance baseline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability ✅

**Compliance**:
- Test code follows PEP 8 (enforced by black/ruff in CI)
- Test fixtures have single responsibility (user fixtures, trip fixtures, photo fixtures)
- Pytest configuration documented in `pyproject.toml` and `pytest.ini`
- Type hints used in test helper functions
- No magic numbers in assertions (use named constants for expected values)

**Justification**: Test infrastructure requires same quality standards as production code for maintainability.

---

### II. Testing Standards (Non-Negotiable) ✅

**Compliance**:
- Meta-testing: Tests for the test infrastructure itself (e.g., fixture validation, test data generation)
- TDD workflow: Write smoke test → run → fail → implement health check → pass
- Coverage target: ≥90% for test utilities and fixtures
- Test independence: Each test creates its own data (UUID-based usernames)
- Fast execution: Unit tests <100ms via in-memory SQLite

**Justification**: Testing infrastructure must be self-validating to ensure reliability.

---

### III. User Experience Consistency ✅

**Compliance**:
- E2E tests validate Spanish error messages in UI
- Integration tests verify consistent JSON API structure (`success`, `data`, `error`)
- E2E tests check accessibility (ARIA labels, keyboard navigation)
- Performance tests enforce <200ms p95 for simple queries

**Justification**: Tests enforce UX consistency requirements from constitution.

---

### IV. Performance Requirements ✅

**Compliance**:
- Performance tests validate <200ms p95 for simple queries
- Performance tests check <500ms p95 for auth endpoints
- Performance tests verify <2s for photo uploads
- Integration tests detect N+1 queries using SQLAlchemy query logging
- Load tests simulate 100 concurrent users

**Justification**: Tests validate performance requirements are met across features.

---

### Security & Data Protection ✅

**Compliance**:
- Integration tests verify bcrypt password hashing
- Integration tests validate JWT token expiration and refresh
- E2E tests check HTTPS enforcement in staging
- Integration tests verify SQL injection prevention (parameterized queries)
- Integration tests validate file upload restrictions (type, size)

**Justification**: Tests ensure security controls are effective.

---

### Development Workflow ✅

**Compliance**:
- CI/CD pipeline runs all tests before merge
- GitHub Actions enforces ≥90% coverage
- Breaking test failures block PR merge
- Test results published as GitHub Actions artifacts

**Justification**: Testing infrastructure is core to development workflow.

---

**GATE STATUS**: ✅ PASS - No violations. Testing infrastructure aligns with all constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-testing-qa/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - testing framework decisions
├── data-model.md        # Phase 1 output - test fixtures schema
├── quickstart.md        # Phase 1 output - developer setup guide
├── contracts/           # Phase 1 output - test API contracts
│   └── smoke-tests.yaml # Smoke test endpoint schema
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
# Web application structure (existing)
backend/
├── src/
│   ├── models/          # Existing models (User, Trip, etc.)
│   ├── services/        # Existing services
│   └── api/             # Existing API endpoints
├── tests/               # ← NEW: Test infrastructure
│   ├── conftest.py      # Pytest fixtures (db, client, auth)
│   ├── fixtures/        # Test data (JSON files)
│   │   ├── users.json
│   │   ├── trips.json
│   │   └── photos/      # Sample images
│   ├── unit/            # Unit tests
│   │   ├── test_auth_service.py
│   │   ├── test_trip_service.py
│   │   └── test_stats_service.py
│   ├── integration/     # Integration tests
│   │   ├── test_auth_api.py
│   │   ├── test_trips_api.py
│   │   └── test_public_feed.py
│   ├── contract/        # Contract tests (OpenAPI validation)
│   │   └── test_api_contracts.py
│   └── performance/     # Performance tests
│       ├── test_latency.py
│       └── locustfile.py
├── scripts/             # Existing scripts
│   └── smoke_tests.sh   # ← NEW: Smoke test runner
└── pyproject.toml       # ← UPDATE: Add test dependencies

frontend/
├── src/
│   ├── components/      # Existing components
│   ├── pages/           # Existing pages
│   └── services/        # Existing services
└── tests/               # ← NEW: E2E test infrastructure
    ├── e2e/             # Playwright tests
    │   ├── auth.spec.ts
    │   ├── trips.spec.ts
    │   ├── public-feed.spec.ts
    │   └── helpers/     # Test utilities
    ├── fixtures/        # Test data for E2E
    └── playwright.config.ts  # ← NEW: Playwright configuration

.github/
└── workflows/           # ← NEW: CI/CD workflows
    ├── test.yml         # Run all tests on PR
    ├── deploy-staging.yml  # Deploy + smoke tests
    └── performance.yml  # Weekly performance baseline

scripts/                 # ← NEW: Root-level test scripts
├── run_smoke_tests.sh   # Cross-mode smoke tests
└── run_all_tests.sh     # Local test runner
```

**Structure Decision**:
- Backend tests follow pytest standard structure (`tests/unit/`, `tests/integration/`, `tests/contract/`)
- Frontend E2E tests use Playwright Test structure (`tests/e2e/`)
- Smoke tests are shell scripts (cross-platform) for simplicity and speed
- GitHub Actions workflows define CI/CD orchestration

**Rationale**:
- Separation of unit/integration/contract tests enables selective execution (faster CI feedback)
- E2E tests in frontend directory keep browser-specific code close to UI components
- Smoke tests as scripts (not pytest) avoid Python overhead for simple health checks
- Root-level `scripts/` for orchestration across backend + frontend tests

## Complexity Tracking

**No violations** - Testing infrastructure aligns with all constitution principles. No complexity justification required.

---

# Phase 0: Research & Decisions

## Research Topics

Based on Technical Context unknowns and feature requirements, the following research is needed:

1. **Pytest Async Fixtures for FastAPI** - How to properly configure async database sessions and TestClient for FastAPI endpoints
2. **Playwright Multi-Browser Setup** - Best practices for running tests across Chrome, Firefox, Safari with consistent results
3. **GitHub Actions Caching** - Strategies to cache Poetry dependencies, npm modules, and Playwright browsers to reduce CI runtime
4. **PostgreSQL Test Container Management** - How to spin up/teardown PostgreSQL containers for integration tests without conflicts
5. **Performance Test Baseline Storage** - Where and how to store performance baselines for regression comparison
6. **Smoke Test Design Patterns** - Best practices for fast environment validation (database, API, static files)
7. **Flaky Test Detection** - Tools and strategies to identify and retry flaky E2E tests automatically
8. **SQLite vs PostgreSQL Test Parity** - How to write tests that pass on both databases despite dialect differences

---

## Research Findings

### Decision 1: Pytest Async Fixtures for FastAPI

**Decision**: Use `pytest-asyncio` with `async_scoped_session` fixtures for database isolation and `AsyncClient` from `httpx` for API testing.

**Rationale**:
- FastAPI uses async/await, so test client must support async
- `pytest-asyncio` provides `@pytest.fixture(scope="function")` with async support
- `httpx.AsyncClient` is recommended by FastAPI docs for async testing
- Transaction rollback per test ensures test independence

**Pattern**:
```python
# conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture(scope="function")
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

**Alternatives Considered**:
- Sync client with `requests` - Rejected: Doesn't support FastAPI async routes
- Testcontainers for PostgreSQL per test - Rejected: Too slow for unit tests (30s+ startup)

---

### Decision 2: Playwright Multi-Browser Setup

**Decision**: Use Playwright's built-in browser matrix with `projects` configuration and GitHub Actions matrix strategy.

**Rationale**:
- Playwright Test natively supports multiple browsers via `projects` in config
- GitHub Actions matrix allows parallel execution across browsers (3x faster than sequential)
- WebKit (Safari) support on macOS runners, Chromium/Firefox on Linux runners

**Pattern**:
```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  retries: process.env.CI ? 2 : 0,  // Auto-retry flaky tests in CI
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});
```

```yaml
# .github/workflows/test.yml
jobs:
  e2e:
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    steps:
      - run: npx playwright test --project=${{ matrix.browser }}
```

**Alternatives Considered**:
- Selenium WebDriver - Rejected: Slower, more flaky than Playwright's auto-waiting
- Cypress - Rejected: No native Safari/WebKit support, less performant

---

### Decision 3: GitHub Actions Caching

**Decision**: Cache Poetry virtualenvs, npm node_modules, and Playwright browsers using `actions/cache` with composite keys.

**Rationale**:
- Poetry install: ~2 minutes without cache, ~10 seconds with cache
- npm install: ~1 minute without cache, ~5 seconds with cache
- Playwright browsers: ~1.5 minutes without cache, instant with cache
- Total CI time reduction: ~4.5 minutes per run

**Pattern**:
```yaml
# .github/workflows/test.yml
- name: Cache Poetry dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pypoetry
    key: poetry-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}

- name: Cache npm dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}

- name: Cache Playwright browsers
  uses: actions/cache@v3
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
```

**Alternatives Considered**:
- No caching - Rejected: CI runs take 18+ minutes, exceeds budget
- Docker layer caching - Rejected: More complex, not needed for Python/Node

---

### Decision 4: PostgreSQL Test Container Management

**Decision**: Use `pytest-docker-compose` to spin up PostgreSQL container once per test session, reset database between tests via migrations.

**Rationale**:
- Starting PostgreSQL container per test is too slow (30s+ overhead)
- Starting once per session (<10s) and resetting via migrations is fast (<1s per test)
- `pytest-docker-compose` integrates with existing `docker-compose.yml`

**Pattern**:
```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return "docker-compose.test.yml"

@pytest.fixture(scope="function")
async def db_session(docker_services):
    # Wait for PostgreSQL to be ready
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1,
        check=lambda: is_db_responsive()
    )

    # Run migrations to clean state
    await run_migrations()

    # Yield session
    async_session = async_sessionmaker(engine)
    async with async_session() as session:
        yield session
        await session.rollback()
```

**Alternatives Considered**:
- Testcontainers Python - Rejected: Heavier than pytest-docker-compose, more dependencies
- Shared PostgreSQL instance - Rejected: Test isolation issues (parallel execution conflicts)

---

### Decision 5: Performance Test Baseline Storage

**Decision**: Store performance baselines as JSON files in `tests/performance/baselines/` and commit to repository. Use pytest-benchmark's `--benchmark-autosave` and `--benchmark-compare`.

**Rationale**:
- JSON baselines are human-readable and diffable in PRs
- Committing baselines to repo ensures consistency across developers and CI
- pytest-benchmark automatically compares against saved baselines and fails on regressions
- Separate baseline per environment (local, CI, staging) to account for hardware differences

**Pattern**:
```bash
# Save baseline (run once on stable version)
pytest tests/performance/ --benchmark-autosave --benchmark-save=baseline_v1

# Compare against baseline (CI/PR)
pytest tests/performance/ --benchmark-compare=baseline_v1 --benchmark-compare-fail=mean:20%
```

**Alternatives Considered**:
- Locust CSV exports - Rejected: Less integration with pytest, manual comparison
- External database (InfluxDB) - Rejected: Over-engineering for regression detection

---

### Decision 6: Smoke Test Design Patterns

**Decision**: Use shell scripts with `curl` for HTTP health checks and lightweight Python script for database connectivity checks. Exit code 0 = pass, non-zero = fail.

**Rationale**:
- Smoke tests must be fast (<30s) and have minimal dependencies
- `curl` is universally available and sufficient for HTTP endpoint validation
- Python script for database checks reuses existing database connection code
- Shell scripts are cross-platform (bash on Linux/macOS, Git Bash on Windows)

**Pattern**:
```bash
#!/bin/bash
# scripts/smoke_tests.sh

set -e  # Exit on first failure

MODE=$1  # local-dev, local-minimal, local-full, staging

echo "Running smoke tests for $MODE mode..."

# Health check
curl -f http://localhost:8000/health || exit 1

# Auth endpoint (should return 401 without token)
curl -f -s http://localhost:8000/auth/me -w "%{http_code}" | grep 401 || exit 1

# Database connectivity
python scripts/check_db.py || exit 1

echo "✅ All smoke tests passed for $MODE"
```

**Alternatives Considered**:
- Pytest-based smoke tests - Rejected: Slower startup time (~2s overhead)
- Postman/Newman - Rejected: Additional dependency, not needed for simple checks

---

### Decision 7: Flaky Test Detection

**Decision**: Use Playwright's built-in retry mechanism (`retries: 2` in CI) and GitHub Actions workflow to track flaky test rate over time.

**Rationale**:
- Playwright automatically retries failed tests up to 2 times
- If test passes on retry, it's marked as "flaky" in report
- GitHub Actions can aggregate flaky test data across runs
- 5% flaky rate threshold triggers investigation (per constitution SC-005)

**Pattern**:
```typescript
// playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,  // Retry in CI only
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
});
```

```yaml
# .github/workflows/test.yml
- name: Analyze flaky tests
  run: |
    FLAKY_COUNT=$(jq '.suites[].specs[] | select(.tests[].status == "flaky") | .title' test-results/results.json | wc -l)
    TOTAL_COUNT=$(jq '.suites[].specs[] | .title' test-results/results.json | wc -l)
    FLAKY_RATE=$(echo "scale=2; $FLAKY_COUNT / $TOTAL_COUNT * 100" | bc)

    if (( $(echo "$FLAKY_RATE > 5" | bc -l) )); then
      echo "❌ Flaky test rate: $FLAKY_RATE% (threshold: 5%)"
      exit 1
    fi
```

**Alternatives Considered**:
- Manual flaky test tracking - Rejected: Error-prone, not automated
- Third-party services (BuildPulse) - Rejected: Additional cost, not needed initially

---

### Decision 8: SQLite vs PostgreSQL Test Parity

**Decision**: Run integration tests on both SQLite (fast local) and PostgreSQL (production parity) using pytest parametrization and environment variable switching.

**Rationale**:
- Unit tests use SQLite in-memory for speed (<100ms per test)
- Integration tests run on both databases to catch dialect-specific issues
- PostgreSQL-specific features (UUIDs, arrays) have SQLite fallbacks in models
- CI runs PostgreSQL tests, developers can run SQLite tests locally for fast iteration

**Pattern**:
```python
# conftest.py
import pytest
import os

@pytest.fixture(scope="session", params=["sqlite", "postgresql"])
def db_engine(request):
    if request.param == "sqlite":
        return create_async_engine("sqlite+aiosqlite:///:memory:")
    else:
        db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
        return create_async_engine(db_url)

# Usage in tests
async def test_create_trip(db_session):  # Runs twice: SQLite + PostgreSQL
    trip = await TripService.create_trip(...)
    assert trip.trip_id is not None
```

**Alternatives Considered**:
- SQLite-only tests - Rejected: Doesn't catch PostgreSQL-specific issues (UUID handling, array columns)
- PostgreSQL-only tests - Rejected: Too slow for rapid local development (30s+ startup)

---

# Phase 1: Design & Contracts

## Data Model

See [data-model.md](data-model.md) for complete test fixtures schema.

**Summary**: Test fixtures define reusable sample data for users, trips, photos, and tags. Fixtures use JSON format for easy editing and version control.

## API Contracts

See [contracts/smoke-tests.yaml](contracts/smoke-tests.yaml) for smoke test endpoint specifications.

**Summary**: Smoke tests validate health check endpoint (`GET /health`) and authentication endpoints (`POST /auth/login`, `GET /auth/me`) return expected status codes and response structures.

## Quick Start Guide

See [quickstart.md](quickstart.md) for developer setup and test execution instructions.

**Summary**: Developers can run smoke tests locally with `./scripts/run_smoke_tests.sh <mode>`, unit tests with `pytest tests/unit/`, and E2E tests with `npm run test:e2e`.

---

# Phase 2: Task Breakdown

**Status**: NOT STARTED - Use `/speckit.tasks` command to generate task breakdown.

**Next Steps**:
1. Review this plan and approve technical decisions
2. Run `/speckit.tasks` to generate implementation tasks
3. Begin implementation in phases (P1: Smoke + Integration, P2: E2E + CI/CD, P3: Performance)
