# Quick Start Guide: Testing & QA Suite

**Feature**: Testing & QA Suite (001-testing-qa)
**Audience**: Developers setting up and running tests locally

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [First-Time Setup](#first-time-setup)
3. [Running Tests Locally](#running-tests-locally)
4. [Smoke Tests](#smoke-tests)
5. [Unit Tests](#unit-tests)
6. [Integration Tests](#integration-tests)
7. [E2E Tests](#e2e-tests)
8. [Performance Tests](#performance-tests)
9. [Coverage Reports](#coverage-reports)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before running tests, ensure you have:

- **Python 3.12+** (for backend tests)
- **Node.js 18+** and npm (for E2E tests)
- **Poetry** (Python dependency management)
- **Git** (for cloning repository)
- **Docker** (optional, for integration tests with PostgreSQL)

---

## First-Time Setup

### 1. Clone Repository and Install Dependencies

```bash
# Clone repository
git clone https://github.com/jfdelafuente/contravento-application-python.git
cd contravento-application-python

# Install backend dependencies
cd backend
poetry install

# Install frontend dependencies
cd ../frontend
npm install

# Install Playwright browsers (for E2E tests)
npx playwright install
```

### 2. Configure Environment Variables

```bash
# Backend test environment (use SQLite in-memory by default)
cd backend
cp .env.example .env.test

# Edit .env.test (optional - defaults work for tests)
# DATABASE_URL=sqlite+aiosqlite:///:memory:
# SECRET_KEY=test-secret-key-not-for-production
# BCRYPT_ROUNDS=4  # Faster password hashing for tests
```

### 3. Verify Setup

```bash
# Run quick smoke test to verify installation
cd backend
poetry run pytest --version  # Should show pytest version

cd ../frontend
npx playwright --version  # Should show Playwright version
```

---

## Running Tests Locally

### Quick Commands (TL;DR)

```bash
# Run ALL tests (backend + frontend)
./scripts/run_all_tests.sh

# Backend only
cd backend
poetry run pytest

# Frontend E2E only
cd frontend
npm run test:e2e

# Smoke tests for local-dev mode
./scripts/run_smoke_tests.sh local-dev
```

---

## Smoke Tests

**Purpose**: Validate deployment environment is operational (database, API, static files)

**Duration**: <30 seconds per mode

### Run Smoke Tests

```bash
# Test local-dev mode (SQLite)
./scripts/run_smoke_tests.sh local-dev

# Test local-minimal mode (PostgreSQL via Docker)
./scripts/run_smoke_tests.sh local-minimal

# Test local-full mode (Docker with all services)
./scripts/run_smoke_tests.sh local-full

# Test staging mode
./scripts/run_smoke_tests.sh staging
```

### What Smoke Tests Validate

1. **Health Check** (`GET /health`)
   - API server is running
   - Responds within 5 seconds

2. **Auth Endpoints** (`POST /auth/login`, `GET /auth/me`)
   - Returns 401 for invalid credentials
   - Returns 401 for missing token

3. **Database Connectivity**
   - Can connect to database (SQLite or PostgreSQL)
   - Can execute simple query

4. **Static Files** (if applicable)
   - Frontend build files are served
   - Returns correct MIME types

### Example Output

```bash
$ ./scripts/run_smoke_tests.sh local-dev

Running smoke tests for local-dev mode...
✅ Health check passed (120ms)
✅ Auth endpoints responding (401 as expected)
✅ Database connectivity OK
✅ All smoke tests passed for local-dev

Total time: 8 seconds
```

---

## Unit Tests

**Purpose**: Test individual functions and classes in isolation

**Duration**: <5 minutes, <100ms per test

### Run Unit Tests

```bash
cd backend

# Run all unit tests
poetry run pytest tests/unit/

# Run specific test file
poetry run pytest tests/unit/test_auth_service.py

# Run specific test function
poetry run pytest tests/unit/test_auth_service.py::test_register_user

# Run tests matching pattern
poetry run pytest tests/unit/ -k "auth"

# Run with verbose output
poetry run pytest tests/unit/ -v
```

### Unit Test Coverage

```bash
# Run with coverage report
poetry run pytest tests/unit/ --cov=src --cov-report=term

# Generate HTML coverage report
poetry run pytest tests/unit/ --cov=src --cov-report=html

# Open coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Example Output

```bash
$ poetry run pytest tests/unit/ -v

========================= test session starts ==========================
platform linux -- Python 3.12.0, pytest-7.4.3, pluggy-1.3.0
collected 42 items

tests/unit/test_auth_service.py::test_register_user PASSED       [  2%]
tests/unit/test_auth_service.py::test_login_valid PASSED         [  4%]
tests/unit/test_auth_service.py::test_login_invalid PASSED       [  7%]
tests/unit/test_trip_service.py::test_create_trip PASSED         [  9%]
...

======================== 42 passed in 3.21s ============================
```

---

## Integration Tests

**Purpose**: Test API endpoints with real database transactions

**Duration**: <5 minutes with parallel execution

### Run Integration Tests

```bash
cd backend

# Run all integration tests
poetry run pytest tests/integration/

# Run with PostgreSQL (requires Docker)
docker-compose -f docker-compose.test.yml up -d postgres
poetry run pytest tests/integration/ --postgresql
docker-compose -f docker-compose.test.yml down

# Run specific integration test
poetry run pytest tests/integration/test_trips_api.py

# Run tests in parallel (4 workers)
poetry run pytest tests/integration/ -n 4
```

### Integration Test Scenarios

1. **User Registration Flow**
   - Create account → Verify email → Login → Get JWT token

2. **Trip Creation Flow**
   - Create draft → Upload photos → Add locations → Publish → Verify stats updated

3. **Public Feed Access**
   - Non-authenticated user views public trips
   - Authenticated user views all trips (including drafts)

4. **Access Control**
   - Owner can edit/delete their trips
   - Non-owner cannot edit/delete others' trips

### Example Output

```bash
$ poetry run pytest tests/integration/ -v

========================= test session starts ==========================
collected 28 items

tests/integration/test_auth_api.py::test_register_user_flow PASSED   [  3%]
tests/integration/test_trips_api.py::test_create_trip_flow PASSED    [  7%]
tests/integration/test_public_feed.py::test_anonymous_access PASSED [10%]
...

======================== 28 passed in 12.45s ===========================
```

---

## E2E Tests

**Purpose**: Test complete user workflows in real browsers

**Duration**: <10 minutes across 3 browsers

### Run E2E Tests

```bash
cd frontend

# Run all E2E tests (all browsers)
npm run test:e2e

# Run in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test tests/e2e/auth.spec.ts

# Run with UI mode (interactive debugging)
npx playwright test --ui
```

### E2E Test Scenarios

1. **User Registration & Login**
   - Navigate to /register
   - Fill form with valid data
   - Submit and verify success message
   - Login with credentials

2. **Trip Creation Wizard**
   - Navigate to /trips/new
   - Complete 4-step wizard (Basic Info → Story → Photos → Review)
   - Upload 3 photos via drag-and-drop
   - Publish trip
   - Verify trip appears in dashboard

3. **Public Feed Browsing**
   - Navigate to / (public feed)
   - Click trip card
   - View photos in lightbox gallery
   - Click map markers

4. **Location Editing with Reverse Geocoding**
   - Click map to add location
   - Wait for geocoding modal
   - Edit location name
   - Confirm and verify marker on map

### View E2E Test Reports

```bash
# Open HTML report
npx playwright show-report

# View screenshots and videos
ls -la test-results/
```

### Example Output

```bash
$ npm run test:e2e

Running 15 tests using 3 workers

  ✓  [chromium] › auth.spec.ts:8:5 › User can register (2.3s)
  ✓  [firefox]  › auth.spec.ts:8:5 › User can register (2.1s)
  ✓  [webkit]   › auth.spec.ts:8:5 › User can register (2.5s)
  ✓  [chromium] › trips.spec.ts:12:5 › User can create trip (4.2s)
  ...

  15 passed (42.8s)
```

---

## Performance Tests

**Purpose**: Measure response times and detect performance regressions

**Duration**: <3 minutes for baseline, <10 minutes for load tests

### Run Performance Tests

```bash
cd backend

# Run performance tests with baseline comparison
poetry run pytest tests/performance/ --benchmark-compare=baseline_v1

# Save new baseline (after stable release)
poetry run pytest tests/performance/ --benchmark-autosave --benchmark-save=baseline_v1

# Run load tests with Locust (100 concurrent users)
poetry run locust -f tests/performance/locustfile.py --headless -u 100 -r 10 --run-time 2m
```

### Performance Metrics

1. **Endpoint Latency**
   - GET /trips/public: <200ms p95
   - POST /auth/login: <500ms p95
   - POST /trips/{id}/photos: <2s p95

2. **Database Performance**
   - N+1 query detection
   - Connection pool utilization
   - Query execution time

3. **Load Testing**
   - 100 concurrent users
   - Request success rate
   - Error rate under load

### Example Output

```bash
$ poetry run pytest tests/performance/test_latency.py

--------------------------------- benchmark: 3 tests ---------------------------------
Name (time in ms)                 Min       Max      Mean    StdDev    p95    p99
--------------------------------------------------------------------------------------
test_trips_public_latency       45.23     78.12    52.34      8.21   68.45  75.23
test_auth_login_latency        102.45    187.34   125.67     15.34  158.23 175.12
test_photo_upload_latency     1234.56   1987.23  1456.78    123.45 1765.34 1892.45
--------------------------------------------------------------------------------------

All tests passed performance thresholds! ✅
```

---

## Coverage Reports

### Generate Coverage Report

```bash
cd backend

# Run all tests with coverage
poetry run pytest --cov=src --cov-report=html --cov-report=term

# View coverage summary in terminal
poetry run pytest --cov=src --cov-report=term-missing

# Generate HTML report
poetry run pytest --cov=src --cov-report=html

# Open HTML report
open htmlcov/index.html
```

### Coverage Requirements

- **Minimum**: ≥90% coverage across all modules
- **Target**: ≥95% coverage for critical paths
- **Exclusions**: Generated migrations, config files

### Example Coverage Report

```
---------- coverage: platform linux, python 3.12.0 -----------
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/models/user.py                   45      2    96%   78-79
src/services/auth_service.py         89      4    95%   145, 178-180
src/services/trip_service.py        134      8    94%   201, 267-273
src/api/trips.py                     67      3    96%   89, 145-146
---------------------------------------------------------------
TOTAL                              1245     58    95%

Required test coverage of 90% reached. Total coverage: 95.34%
```

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" Error

```bash
# Solution: Reinstall dependencies
cd backend
poetry install

cd ../frontend
npm install
```

#### 2. Playwright Browsers Not Found

```bash
# Solution: Install browsers
cd frontend
npx playwright install
```

#### 3. PostgreSQL Connection Error (Integration Tests)

```bash
# Solution: Start PostgreSQL container
docker-compose -f docker-compose.test.yml up -d postgres

# Verify container is running
docker ps | grep postgres

# Check logs
docker-compose -f docker-compose.test.yml logs postgres
```

#### 4. Tests Fail with "Port Already in Use"

```bash
# Solution: Kill process using port 8000
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 5. Coverage Below 90%

```bash
# Solution: Check which files need tests
poetry run pytest --cov=src --cov-report=term-missing

# Look for "Missing" column to see uncovered lines
# Write tests for those lines
```

#### 6. E2E Tests Timeout

```bash
# Solution 1: Increase timeout in playwright.config.ts
# timeout: 60000  // 60 seconds

# Solution 2: Run in headed mode to see what's happening
npx playwright test --headed

# Solution 3: Check backend is running
curl http://localhost:8000/health
```

---

## CI/CD Integration

Tests run automatically on GitHub Actions for every pull request:

1. **Unit Tests** (5 min) - Run on every commit
2. **Integration Tests** (5 min) - Run on PRs to main/develop
3. **E2E Tests** (10 min) - Run on PRs to main/develop
4. **Performance Tests** (weekly) - Run on schedule

View CI results:
- Go to GitHub repository
- Click "Actions" tab
- Select workflow run
- View test results and coverage reports

---

## Next Steps

1. **Run your first test**: `cd backend && poetry run pytest tests/unit/ -v`
2. **Add a new test**: See [data-model.md](data-model.md) for fixture examples
3. **Run E2E tests**: `cd frontend && npm run test:e2e`
4. **Check coverage**: `poetry run pytest --cov=src --cov-report=html`
5. **Read full plan**: See [plan.md](plan.md) for technical decisions

---

## Support

- **Issues**: [GitHub Issues](https://github.com/jfdelafuente/contravento-application-python/issues)
- **Documentation**: See `specs/001-testing-qa/` directory
- **CI/CD**: [GitHub Actions](https://github.com/jfdelafuente/contravento-application-python/actions)
