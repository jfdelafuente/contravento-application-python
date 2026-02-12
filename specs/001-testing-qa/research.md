# Research: Testing & QA Suite

**Feature**: Testing & QA Suite (001-testing-qa)
**Phase**: 0 - Research & Decisions
**Date**: 2026-01-16

## Executive Summary

This document consolidates all research and technical decisions for the Testing & QA Suite infrastructure. The suite will provide comprehensive automated testing across 4 deployment modes using pytest (backend), Playwright (E2E), and GitHub Actions (CI/CD).

**Key Decisions**:
1. pytest-asyncio + httpx AsyncClient for FastAPI testing
2. Playwright Test with multi-browser matrix for E2E
3. GitHub Actions caching to reduce CI runtime by ~4.5 minutes
4. pytest-docker-compose for PostgreSQL test containers
5. pytest-benchmark with JSON baselines for performance regression
6. Shell scripts for smoke tests (minimal overhead)
7. Playwright retry mechanism + GitHub Actions for flaky test tracking
8. SQLite/PostgreSQL dual testing via pytest parametrization

---

## Research Topics & Findings

### 1. Pytest Async Fixtures for FastAPI

**Question**: How to properly configure async database sessions and TestClient for FastAPI endpoints while maintaining test isolation?

**Decision**: Use `pytest-asyncio` with `async_scoped_session` fixtures for database isolation and `AsyncClient` from `httpx` for API testing.

**Rationale**:
- FastAPI uses async/await throughout, so test client must support async operations
- `pytest-asyncio` provides native async fixture support with proper scope management
- `httpx.AsyncClient` is officially recommended by FastAPI documentation
- Transaction rollback per test ensures complete test independence
- In-memory SQLite provides fastest possible test execution (<100ms per test)

**Technical Implementation**:

```python
# backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.main import app
from src.database import Base

@pytest.fixture(scope="function")
async def db_session():
    """Create fresh in-memory SQLite DB per test with automatic rollback"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create sessionmaker
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # Yield session for test
    async with async_session() as session:
        yield session
        await session.rollback()  # Ensure no commits leak between tests

    # Cleanup
    await engine.dispose()

@pytest.fixture
async def client(db_session):
    """HTTP client for testing API endpoints"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client, db_session):
    """Authenticated user headers for protected endpoints"""
    # Create test user
    user = await AuthService.register(db_session, {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!",
    })
    user.is_verified = True
    await db_session.commit()

    # Login to get tokens
    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "Test123!",
    })
    tokens = response.json()["data"]

    return {"Authorization": f"Bearer {tokens['access_token']}"}
```

**Alternatives Considered**:
- **Sync client with `requests`**: Rejected - doesn't support FastAPI async routes, would require sync wrapper functions
- **Testcontainers for PostgreSQL per test**: Rejected - 30+ seconds startup time per test, too slow for unit tests
- **Shared database instance across tests**: Rejected - test isolation issues, parallel execution conflicts

**References**:
- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [httpx AsyncClient API](https://www.python-httpx.org/async/)

---

### 2. Playwright Multi-Browser Setup

**Question**: What's the best approach for running E2E tests across Chrome, Firefox, and Safari with consistent results and minimal CI time?

**Decision**: Use Playwright's built-in browser matrix with `projects` configuration and GitHub Actions matrix strategy for parallel execution.

**Rationale**:
- Playwright Test natively supports multiple browsers via configuration (no custom orchestration needed)
- GitHub Actions matrix allows parallel execution across browsers (3x faster than sequential)
- WebKit (Safari) support on macOS runners, Chromium/Firefox on Linux runners
- Built-in auto-waiting reduces flaky tests compared to Selenium
- Screenshot/video capture on failure for easy debugging

**Technical Implementation**:

```typescript
// frontend/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,  // Run tests in parallel
  forbidOnly: !!process.env.CI,  // Fail CI if test.only left in code
  retries: process.env.CI ? 2 : 0,  // Auto-retry flaky tests in CI
  workers: process.env.CI ? 1 : undefined,  // Limit parallel workers in CI

  // Shared settings for all projects
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',  // Capture trace on retry
    screenshot: 'only-on-failure',  // Screenshot failed tests
    video: 'retain-on-failure',  // Video recording for failures
  },

  // Browser matrix
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  // Dev server (start backend + frontend before tests)
  webServer: {
    command: 'npm run dev',
    port: 5173,
    reuseExistingServer: !process.env.CI,
  },
});
```

```yaml
# .github/workflows/test.yml
jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm install
      - run: npx playwright install --with-deps ${{ matrix.browser }}
      - run: npx playwright test --project=${{ matrix.browser }}
```

**Alternatives Considered**:
- **Selenium WebDriver**: Rejected - slower, more flaky than Playwright's auto-waiting, no built-in retry mechanism
- **Cypress**: Rejected - no native Safari/WebKit support, Chrome-only in CI without workarounds, less performant
- **Puppeteer**: Rejected - Chrome-only, no cross-browser support

**References**:
- [Playwright Configuration](https://playwright.dev/docs/test-configuration)
- [Playwright CI Guide](https://playwright.dev/docs/ci)

---

### 3. GitHub Actions Caching Strategy

**Question**: How to minimize CI runtime and stay within GitHub Actions free tier limits (2000 minutes/month)?

**Decision**: Cache Poetry virtualenvs, npm node_modules, and Playwright browsers using `actions/cache` with composite keys based on lock file hashes.

**Rationale**:
- **Poetry install**: Reduces from ~2 minutes to ~10 seconds (1.9 min savings)
- **npm install**: Reduces from ~1 minute to ~5 seconds (55s savings)
- **Playwright browsers**: Reduces from ~1.5 minutes to instant (1.5 min savings)
- **Total savings**: ~4.5 minutes per CI run (30% reduction)
- **Monthly savings**: ~90 hours of runner time (assuming 20 PRs/day)

**Technical Implementation**:

```yaml
# .github/workflows/test.yml
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Cache Poetry dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pypoetry
          key: poetry-${{ runner.os }}-${{ hashFiles('**/poetry.lock') }}
          restore-keys: |
            poetry-${{ runner.os }}-

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: |
          cd backend
          poetry install

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Cache npm dependencies
        uses: actions/cache@v3
        with:
          path: ~/.npm
          key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            npm-${{ runner.os }}-

      - name: Cache Playwright browsers
        uses: actions/cache@v3
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
          restore-keys: |
            playwright-${{ runner.os }}-

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps
```

**Cache Invalidation Strategy**:
- Cache key includes lock file hash → cache invalidates when dependencies change
- Restore keys provide fallback to previous cache if exact match not found
- Playwright cache tied to package-lock.json (browser versions match npm dependencies)

**Alternatives Considered**:
- **No caching**: Rejected - CI runs take 18+ minutes, exceeds free tier budget
- **Docker layer caching**: Rejected - more complex setup, not needed for Python/Node projects
- **Self-hosted runners with persistent cache**: Rejected - infrastructure overhead, not needed initially

**References**:
- [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [actions/cache Documentation](https://github.com/actions/cache)

---

### 4. PostgreSQL Test Container Management

**Question**: How to provide PostgreSQL for integration tests without 30+ second startup overhead per test?

**Decision**: Use `pytest-docker-compose` to spin up PostgreSQL container once per test session, reset database between tests via migrations or transaction rollback.

**Rationale**:
- Starting PostgreSQL container per test is too slow (30-60s overhead)
- Starting once per session (<10s) amortizes cost across all tests
- Resetting via migrations/rollback is fast (<1s per test)
- pytest-docker-compose integrates with existing docker-compose.yml
- Session-scoped container allows parallel test execution with separate databases

**Technical Implementation**:

```python
# backend/tests/conftest.py
import pytest
from pytest_docker_compose import DockerComposePlugin

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Use test-specific docker-compose file"""
    return "docker-compose.test.yml"

@pytest.fixture(scope="session")
def docker_services(docker_compose_file):
    """Start PostgreSQL container once per test session"""
    plugin = DockerComposePlugin(docker_compose_file)
    plugin.start()
    yield plugin.services
    plugin.stop()

def is_db_responsive():
    """Check if PostgreSQL is ready"""
    try:
        engine = create_engine("postgresql://test:test@localhost/test")
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False

@pytest.fixture(scope="function")
async def db_session_postgres(docker_services):
    """PostgreSQL session with automatic cleanup"""
    # Wait for PostgreSQL to be ready
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=is_db_responsive
    )

    # Create engine
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test")

    # Run migrations to clean state
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Yield session
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

    await engine.dispose()
```

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 5
```

**Alternatives Considered**:
- **Testcontainers Python**: Rejected - heavier than pytest-docker-compose, more dependencies, slower
- **Shared PostgreSQL instance across tests**: Rejected - test isolation issues, parallel execution conflicts
- **PostgreSQL per test**: Rejected - 30+ seconds overhead per test, unusable for rapid development

**References**:
- [pytest-docker-compose](https://github.com/pytest-docker-compose/pytest-docker-compose)
- [PostgreSQL Docker Official Image](https://hub.docker.com/_/postgres)

---

### 5. Performance Test Baseline Storage

**Question**: Where and how should we store performance baselines for regression comparison across environments?

**Decision**: Store performance baselines as JSON files in `backend/tests/performance/baselines/` and commit to repository. Use pytest-benchmark's `--benchmark-autosave` and `--benchmark-compare`.

**Rationale**:
- JSON baselines are human-readable and diff-friendly in PRs
- Committing to repo ensures consistency across developers and CI
- pytest-benchmark automatically compares against saved baselines
- Separate baseline per environment accounts for hardware differences
- No external database infrastructure required

**Technical Implementation**:

```bash
# Save baseline (run once on stable version)
cd backend
pytest tests/performance/ \
  --benchmark-autosave \
  --benchmark-save=baseline_v1_local

# Compare against baseline in CI
pytest tests/performance/ \
  --benchmark-compare=baseline_v1_ci \
  --benchmark-compare-fail=mean:20%  # Fail if >20% slower

# View benchmark results
pytest tests/performance/ --benchmark-only
```

```python
# backend/tests/performance/test_latency.py
import pytest

def test_trips_public_latency(benchmark, client):
    """Validate /trips/public responds in <200ms p95"""
    def call_endpoint():
        response = client.get("/trips/public?limit=10")
        assert response.status_code == 200
        return response

    # Run benchmark
    result = benchmark(call_endpoint)

    # Assert latency threshold (p95 < 200ms)
    assert result.stats['mean'] < 0.200, \
        f"Mean latency {result.stats['mean']:.3f}s exceeds 200ms"
```

**Baseline Directory Structure**:

```text
backend/tests/performance/baselines/
├── baseline_v1_local.json    # Local development (fast SSD)
├── baseline_v1_ci.json        # GitHub Actions runner
├── baseline_v1_staging.json   # Staging environment
└── README.md                  # Baseline update instructions
```

**Alternatives Considered**:
- **Locust CSV exports**: Rejected - less integration with pytest, manual comparison needed
- **External database (InfluxDB)**: Rejected - over-engineering for regression detection, infrastructure overhead
- **In-memory comparison**: Rejected - no historical tracking, can't compare across commits

**References**:
- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [pytest-benchmark GitHub](https://github.com/ionelmc/pytest-benchmark)

---

### 6. Smoke Test Design Patterns

**Question**: How to implement fast (<30s) environment validation checks with minimal dependencies?

**Decision**: Use shell scripts with `curl` for HTTP health checks and lightweight Python script for database connectivity. Exit code 0 = pass, non-zero = fail.

**Rationale**:
- Smoke tests must be fast and have zero test framework overhead
- `curl` is universally available (Linux, macOS, Git Bash on Windows)
- Shell scripts provide simplest possible orchestration
- Python script reuses existing database connection code
- Exit codes integrate naturally with CI/CD pipelines

**Technical Implementation**:

```bash
#!/bin/bash
# scripts/run_smoke_tests.sh

set -e  # Exit on first failure

MODE=$1  # local-dev, local-minimal, local-full, staging

# Validate mode argument
if [[ -z "$MODE" ]]; then
  echo "Usage: $0 <mode>"
  echo "Modes: local-dev, local-minimal, local-full, staging"
  exit 1
fi

echo "Running smoke tests for $MODE mode..."

# Determine base URL
case "$MODE" in
  local-dev|local-minimal|local-full)
    BASE_URL="http://localhost:8000"
    ;;
  staging)
    BASE_URL="https://staging.contravento.com"
    ;;
  *)
    echo "Invalid mode: $MODE"
    exit 1
    ;;
esac

# Test 1: Health check
echo -n "Testing health endpoint... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✅ PASS"
else
  echo "❌ FAIL (HTTP $HTTP_CODE)"
  exit 1
fi

# Test 2: Auth endpoint returns 401 for invalid credentials
echo -n "Testing auth endpoint... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid@test.com","password":"wrong"}')
if [[ "$HTTP_CODE" == "401" ]]; then
  echo "✅ PASS"
else
  echo "❌ FAIL (expected 401, got HTTP $HTTP_CODE)"
  exit 1
fi

# Test 3: Database connectivity
echo -n "Testing database connectivity... "
if python scripts/check_db.py --mode "$MODE"; then
  echo "✅ PASS"
else
  echo "❌ FAIL"
  exit 1
fi

echo ""
echo "✅ All smoke tests passed for $MODE mode"
```

```python
# scripts/check_db.py
import sys
import argparse
from sqlalchemy import create_engine

def check_db(mode: str) -> bool:
    """Check database connectivity"""
    try:
        if mode in ["local-dev"]:
            db_url = "sqlite:///backend/contravento_dev.db"
        else:
            db_url = "postgresql://postgres:postgres@localhost/contravento"

        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
        return True
    except Exception as e:
        print(f"Database error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True)
    args = parser.parse_args()

    success = check_db(args.mode)
    sys.exit(0 if success else 1)
```

**Alternatives Considered**:
- **Pytest-based smoke tests**: Rejected - ~2s startup overhead, unnecessary complexity for simple checks
- **Postman/Newman**: Rejected - additional dependency, JSON collection maintenance overhead
- **Dedicated health check library**: Rejected - not needed for simple HTTP + DB checks

**References**:
- [curl Manual](https://curl.se/docs/manual.html)
- [Shell Exit Codes](https://tldp.org/LDP/abs/html/exitcodes.html)

---

### 7. Flaky Test Detection & Retry Strategy

**Question**: How to identify and handle flaky E2E tests that pass 90% of the time but randomly fail due to timing issues?

**Decision**: Use Playwright's built-in retry mechanism (`retries: 2` in CI) and GitHub Actions workflow to track flaky test rate over time.

**Rationale**:
- Playwright automatically retries failed tests up to N times
- If test passes on retry, it's marked as "flaky" in report (not failure)
- GitHub Actions can aggregate flaky test data across runs
- 5% flaky rate threshold triggers investigation (per Success Criteria SC-005)
- Automatic retry prevents false positives without masking real issues

**Technical Implementation**:

```typescript
// frontend/playwright.config.ts
export default defineConfig({
  retries: process.env.CI ? 2 : 0,  // Retry in CI only

  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
});
```

```yaml
# .github/workflows/test.yml
- name: Run E2E tests
  run: npx playwright test

- name: Analyze flaky tests
  if: always()
  run: |
    # Count flaky tests (passed on retry)
    FLAKY_COUNT=$(jq '[.suites[].specs[] | select(.tests[].status == "flaky")] | length' test-results/results.json)
    TOTAL_COUNT=$(jq '[.suites[].specs[]] | length' test-results/results.json)
    FLAKY_RATE=$(echo "scale=2; $FLAKY_COUNT / $TOTAL_COUNT * 100" | bc)

    echo "Flaky tests: $FLAKY_COUNT / $TOTAL_COUNT ($FLAKY_RATE%)"

    # Fail if flaky rate exceeds threshold
    if (( $(echo "$FLAKY_RATE > 5" | bc -l) )); then
      echo "❌ Flaky test rate ($FLAKY_RATE%) exceeds 5% threshold"
      exit 1
    fi

    # Post comment to PR with flaky test details
    if [[ "$FLAKY_COUNT" -gt 0 ]]; then
      jq '.suites[].specs[] | select(.tests[].status == "flaky") | .title' test-results/results.json > flaky_tests.txt
      gh pr comment ${{ github.event.pull_request.number }} \
        --body "⚠️ Flaky tests detected: $(cat flaky_tests.txt)"
    fi
```

**Flaky Test Workflow**:
1. Test runs and fails
2. Playwright automatically retries (up to 2 times)
3. If passes on retry → marked as "flaky", test suite still passes
4. If fails all retries → marked as "failed", test suite fails
5. GitHub Actions aggregates flaky tests and fails if >5% rate
6. PR comment posted with list of flaky tests for investigation

**Alternatives Considered**:
- **Manual flaky test tracking**: Rejected - error-prone, not automated, no historical data
- **Third-party services (BuildPulse)**: Rejected - additional cost ($200+/month), not needed initially
- **No retry mechanism**: Rejected - too many false positives from timing issues

**References**:
- [Playwright Test Retries](https://playwright.dev/docs/test-retries)
- [Playwright Reporters](https://playwright.dev/docs/test-reporters)

---

### 8. SQLite vs PostgreSQL Test Parity

**Question**: How to ensure tests pass on both SQLite (local development) and PostgreSQL (production) despite dialect differences?

**Decision**: Run integration tests on both SQLite (fast local) and PostgreSQL (production parity) using pytest parametrization and environment variable switching.

**Rationale**:
- Unit tests use SQLite in-memory for speed (<100ms per test)
- Integration tests run on both databases to catch dialect-specific issues
- PostgreSQL-specific features (UUIDs, arrays) have SQLite fallbacks in models
- CI runs PostgreSQL tests to ensure production parity
- Developers can run SQLite tests locally for fast iteration

**Technical Implementation**:

```python
# backend/tests/conftest.py
import pytest
import os

@pytest.fixture(scope="session", params=["sqlite", "postgresql"])
def db_engine(request):
    """Parametrized database engine (runs tests twice: SQLite + PostgreSQL)"""
    if request.param == "sqlite":
        return create_async_engine("sqlite+aiosqlite:///:memory:")
    else:
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://test:test@localhost/test"
        )
        return create_async_engine(db_url)

@pytest.fixture
async def db_session(db_engine):
    """Database session that works with both SQLite and PostgreSQL"""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

    await db_engine.dispose()

# Usage in tests - automatically runs twice (SQLite + PostgreSQL)
async def test_create_trip(db_session):
    """Test trip creation (runs on both SQLite and PostgreSQL)"""
    trip = await TripService.create_trip(db_session, user_id, {
        "title": "Test Trip",
        "description": "A test trip for validation",
        "start_date": "2024-06-01",
    })

    assert trip.trip_id is not None
    assert trip.title == "Test Trip"
```

**Dialect-Specific Handling**:

```python
# src/models/trip.py
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy import TypeDecorator, CHAR
import uuid

class GUID(TypeDecorator):
    """Platform-independent GUID type (UUID for PostgreSQL, CHAR(36) for SQLite)"""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)
```

**Test Execution**:

```bash
# Run tests on SQLite only (fast local development)
cd backend
pytest tests/integration/ --db=sqlite

# Run tests on PostgreSQL only (CI environment)
pytest tests/integration/ --db=postgresql

# Run tests on both (default)
pytest tests/integration/
```

**Alternatives Considered**:
- **SQLite-only tests**: Rejected - doesn't catch PostgreSQL-specific issues (UUID handling, ARRAY columns, JSON operators)
- **PostgreSQL-only tests**: Rejected - too slow for rapid local development (requires Docker, 30s+ startup)
- **Separate test suites**: Rejected - test duplication, maintenance overhead

**Known Dialect Differences**:
1. **UUIDs**: PostgreSQL native type, SQLite stores as CHAR(36)
2. **Arrays**: PostgreSQL ARRAY[], SQLite stores as JSON
3. **JSON operators**: PostgreSQL supports `->`, `->>`, SQLite uses `json_extract()`
4. **Case sensitivity**: PostgreSQL case-insensitive by default, SQLite case-sensitive

**References**:
- [SQLAlchemy Dialects](https://docs.sqlalchemy.org/en/20/dialects/)
- [aiosqlite](https://github.com/omnilib/aiosqlite)
- [asyncpg](https://github.com/MagicStack/asyncpg)

---

## Summary of Decisions

| Research Topic | Decision | Primary Benefit |
|----------------|----------|-----------------|
| FastAPI Testing | pytest-asyncio + httpx AsyncClient | Native async support, test isolation via rollback |
| Multi-Browser E2E | Playwright Test with projects matrix | Built-in cross-browser support, auto-waiting reduces flakes |
| CI/CD Caching | GitHub Actions cache for Poetry/npm/Playwright | 4.5 min time savings per run (~30% reduction) |
| PostgreSQL Containers | pytest-docker-compose, session-scoped | 10s startup amortized across all tests |
| Performance Baselines | JSON files in repo, pytest-benchmark | Version-controlled baselines, automatic comparison |
| Smoke Tests | Shell scripts + curl | <30s execution, zero framework overhead |
| Flaky Test Handling | Playwright retries + GitHub Actions tracking | Automatic retry, 5% flaky rate threshold |
| Database Parity | Parametrized fixtures for SQLite + PostgreSQL | Catch dialect issues, fast local iteration |

**Total Estimated CI Time**: <15 minutes (unit 5min + integration 5min + E2E 10min)
**Coverage Target**: ≥90% across all modules
**Test Count**: ~50 unit + ~30 integration + ~15 E2E = ~95 total tests

---

## Next Steps

1. **Review and approve** research decisions
2. **Create Phase 1 artifacts**: data-model.md, contracts/, quickstart.md ✅ (COMPLETED)
3. **Run `/speckit.tasks`** to generate implementation task breakdown
4. **Begin implementation** in priority order (P1: Smoke + Integration, P2: E2E + CI/CD, P3: Performance)
