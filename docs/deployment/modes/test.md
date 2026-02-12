# Test Deployment Mode - Automated Testing Environment

**Purpose**: Isolated environment for running automated tests (pytest, frontend tests, E2E)

**Target Users**: Developers, QA engineers, CI/CD pipelines

**Difficulty**: Beginner

**Estimated Setup Time**: 10-15 minutes

**Prerequisites**:
- Docker 24.0+ and Docker Compose 2.0+
- Basic understanding of testing (pytest, Jest, Playwright)

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Testing Workflows](#testing-workflows)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Related Modes](#related-modes)

---

## Overview

### What is Test Mode?

The **Test** deployment mode provides an isolated, ephemeral environment specifically for running automated tests. It uses lightweight PostgreSQL and Redis containers that start quickly and clean up automatically after tests complete.

**Key Characteristics**:
- ✅ Fastest startup (~15 seconds)
- ✅ Ephemeral (no persistent data - fresh state every run)
- ✅ Isolated from local development environment
- ✅ PostgreSQL test database (port 5433 to avoid conflicts)
- ✅ Redis test instance (port 6380 to avoid conflicts)
- ✅ Automatic cleanup after tests
- ✅ Ideal for CI/CD integration tests
- ❌ No backend/frontend containers (tests run against local code)
- ❌ No monitoring or observability
- ❌ No SSL/TLS

### When to Use Test Mode

**Perfect For**:
- ✅ Running integration tests locally
- ✅ Testing database migrations
- ✅ Testing Redis cache functionality
- ✅ CI/CD automated test runs
- ✅ Avoiding conflicts with local PostgreSQL/Redis
- ✅ Clean database state for each test run

**Not Suitable For**:
- ❌ Feature development (use [local-dev](./local-dev.md))
- ❌ Manual testing (use [staging](./staging.md))
- ❌ Full-stack validation (use [preproduction](./preproduction.md))

### Comparison with Other Modes

| Feature | Test | Local-Dev | Preproduction |
|---------|:----:|:---------:|:-------------:|
| **Startup Time** | ~15s | Instant | ~20s |
| **Database** | PostgreSQL (5433) | SQLite | PostgreSQL (5432) |
| **Backend** | ❌ (local code) | ✅ | ✅ (Docker image) |
| **Frontend** | ❌ (local code) | ✅ | ✅ (Docker image) |
| **Redis** | ✅ (6380) | ❌ | ❌ |
| **Persistence** | ❌ Ephemeral | ✅ | ❌ Ephemeral |
| **Primary Use** | Integration tests | Daily development | CI/CD validation |

---

## Quick Start

### 1. Start Test Environment

**Simple command**:
```bash
# Start PostgreSQL and Redis test containers
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be healthy (~10 seconds)
sleep 10
```

### 2. Verify Services

```bash
# Check container status
docker-compose -f docker-compose.test.yml ps

# Expected output:
# NAME                       STATUS
# contravento-test-db        Up (healthy)
# contravento-test-redis     Up (healthy)

# Test PostgreSQL connection
docker-compose -f docker-compose.test.yml exec postgres-test \
  psql -U testuser -d contravento_test -c "SELECT 1;"

# Test Redis connection
docker-compose -f docker-compose.test.yml exec redis-test \
  redis-cli ping
# Expected: PONG
```

### 3. Run Tests

**Backend tests (pytest)**:
```bash
cd backend

# Run all tests with PostgreSQL
pytest tests/integration/ --postgresql

# Run with coverage
pytest tests/ --cov=src --cov-report=html --postgresql
```

**Frontend tests (Jest/Vitest)**:
```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests (Playwright)
npm run test:e2e
```

### 4. Cleanup

```bash
# Stop and remove test containers
docker-compose -f docker-compose.test.yml down

# Remove volumes (reset database)
docker-compose -f docker-compose.test.yml down -v
```

---

## Architecture

### Service Stack

```
┌─────────────────────────────────────────────────────────┐
│                   LOCAL DEVELOPMENT                      │
│                   (Backend/Frontend Code)                │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ (connects to test database)
                 ▼
      ┌──────────────────────┐
      │  Test Environment     │
      │  (Docker Compose)     │
      └──────────┬───────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
┌──────────────────┐  ┌──────────────────┐
│  PostgreSQL Test │  │   Redis Test     │
│  Port 5433       │  │   Port 6380      │
│  (isolated)      │  │   (isolated)     │
└──────────────────┘  └──────────────────┘
         │                │
         │                │
         ▼                ▼
┌──────────────────┐  ┌──────────────────┐
│  test_db_data    │  │  (no persistence)│
│  (ephemeral)     │  │  In-memory only  │
└──────────────────┘  └──────────────────┘
```

### Network Configuration

**Network**: `test-network` (bridge driver)

**Port Mappings** (non-conflicting):
- `5433:5432` - PostgreSQL (avoids conflict with local PostgreSQL on 5432)
- `6380:6379` - Redis (avoids conflict with local Redis on 6379)

**Connection Strings**:
```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://testuser:testpass@localhost:5433/contravento_test

# Redis
REDIS_URL=redis://localhost:6380/0
```

---

## Testing Workflows

### Backend Integration Tests

**Configure pytest** (`backend/pytest.ini`):

```ini
[pytest]
addopts = -v -s
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Markers
markers =
    unit: Unit tests (no external dependencies)
    integration: Integration tests (require database)
    slow: Slow tests (>1s)
```

**Run integration tests**:

```bash
cd backend

# Start test database
docker-compose -f ../docker-compose.test.yml up -d postgres-test
sleep 10

# Run integration tests only
pytest tests/integration/ -v

# Run with database-specific flag
pytest tests/integration/ --postgresql

# Run slow tests
pytest -m slow

# Run everything except slow tests
pytest -m "not slow"

# Cleanup
docker-compose -f ../docker-compose.test.yml down -v
```

### Database Migration Testing

**Test migrations in isolation**:

```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d postgres-test

# Wait for healthy
sleep 10

# Apply migrations
cd backend
export DATABASE_URL=postgresql+asyncpg://testuser:testpass@localhost:5433/contravento_test
poetry run alembic upgrade head

# Verify migrations
docker-compose -f ../docker-compose.test.yml exec postgres-test \
  psql -U testuser -d contravento_test -c "\dt"

# Test rollback
poetry run alembic downgrade -1
poetry run alembic upgrade head

# Cleanup
docker-compose -f ../docker-compose.test.yml down -v
```

### Redis Cache Testing

**Test Redis cache functionality**:

```python
# tests/integration/test_redis_cache.py
import pytest
import redis.asyncio as redis

@pytest.fixture
async def redis_client():
    """Redis client connected to test instance."""
    client = redis.from_url("redis://localhost:6380/0", encoding="utf-8", decode_responses=True)
    yield client
    await client.flushdb()  # Clean after each test
    await client.close()

async def test_cache_set_get(redis_client):
    """Test basic cache operations."""
    await redis_client.set("test_key", "test_value")
    value = await redis_client.get("test_key")
    assert value == "test_value"

async def test_cache_expiry(redis_client):
    """Test key expiration."""
    await redis_client.set("expiring_key", "value", ex=1)  # 1 second TTL
    assert await redis_client.get("expiring_key") == "value"

    await asyncio.sleep(2)
    assert await redis_client.get("expiring_key") is None
```

**Run Redis tests**:

```bash
# Start Redis test container
docker-compose -f docker-compose.test.yml up -d redis-test

# Run Redis-specific tests
cd backend
pytest tests/integration/test_redis_cache.py -v

# Cleanup
docker-compose -f ../docker-compose.test.yml down
```

### Frontend E2E Tests

**Playwright E2E tests** (`frontend/tests/e2e/`):

```typescript
// frontend/tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeAll(async () => {
    // Start test database
    // (usually handled by CI/CD or manual setup)
  });

  test('user can register', async ({ page }) => {
    await page.goto('http://localhost:5173/register');

    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'TestPass123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/\/email-verification/);
  });

  test('user can login', async ({ page }) => {
    await page.goto('http://localhost:5173/login');

    await page.fill('input[name="email"]', 'admin@contravento.com');
    await page.fill('input[name="password"]', 'AdminPass123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/');
    await expect(page.locator('.user-menu')).toBeVisible();
  });
});
```

**Run E2E tests**:

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d
sleep 10

# Start backend locally (for E2E)
cd backend
export DATABASE_URL=postgresql+asyncpg://testuser:testpass@localhost:5433/contravento_test
poetry run uvicorn src.main:app --reload &

# Start frontend
cd ../frontend
npm run dev &

# Run E2E tests
npm run test:e2e

# Cleanup
kill %1 %2  # Stop backend and frontend
docker-compose -f ../docker-compose.test.yml down -v
```

---

## Configuration

### Test Database Configuration

**Default settings** (`docker-compose.test.yml`):

```yaml
services:
  postgres-test:
    image: postgres:16-alpine
    container_name: contravento-test-db
    environment:
      POSTGRES_DB: contravento_test
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    ports:
      - "5433:5432"  # Non-conflicting port
    volumes:
      - test_db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testuser -d contravento_test"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s
    networks:
      - test-network
```

**Connection Details**:
```
Host:      localhost
Port:      5433 (not 5432!)
Database:  contravento_test
User:      testuser
Password:  testpass
```

### Redis Configuration

**Default settings** (`docker-compose.test.yml`):

```yaml
services:
  redis-test:
    image: redis:7-alpine
    container_name: contravento-test-redis
    ports:
      - "6380:6379"  # Non-conflicting port
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - test-network
```

**Connection String**:
```
redis://localhost:6380/0
```

### Environment Variables for Tests

**Backend test configuration** (`backend/.env.test`):

```bash
# Test database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://testuser:testpass@localhost:5433/contravento_test

# Redis (test instance)
REDIS_URL=redis://localhost:6380/0

# Fast password hashing for tests
BCRYPT_ROUNDS=4

# Test secrets (not secure, only for testing)
SECRET_KEY=test_secret_key_not_secure_for_testing_only

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=plain
```

**Load in tests** (`conftest.py`):

```python
# backend/tests/conftest.py
import pytest
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Load test environment variables."""
    load_dotenv(".env.test")
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start test database
        run: docker-compose -f docker-compose.test.yml up -d

      - name: Wait for services
        run: sleep 10

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install

      - name: Run tests
        run: |
          cd backend
          poetry run pytest --cov=src --cov-report=xml
        env:
          DATABASE_URL: postgresql+asyncpg://testuser:testpass@localhost:5433/contravento_test
          REDIS_URL: redis://localhost:6380/0

      - name: Upload coverage
        uses: codecov/codecov-action@v3

      - name: Cleanup
        if: always()
        run: docker-compose -f docker-compose.test.yml down -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm install

      - name: Run tests
        run: |
          cd frontend
          npm test -- --run
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Port Already in Use

**Symptoms**: `Error: bind: address already in use (5433 or 6380)`

**Fix**: Stop conflicting services
```bash
# Check what's using port 5433
lsof -i :5433              # Linux/Mac
netstat -ano | findstr :5433  # Windows

# If test containers still running
docker-compose -f docker-compose.test.yml down

# If local PostgreSQL on 5433, change port in docker-compose.test.yml
ports:
  - "5434:5432"  # Use different port
```

#### Issue 2: Tests Can't Connect to Database

**Symptoms**: `psycopg.OperationalError: connection refused`

**Fix**: Verify database is healthy
```bash
# Check container status
docker-compose -f docker-compose.test.yml ps

# If not healthy, check logs
docker-compose -f docker-compose.test.yml logs postgres-test

# Restart if needed
docker-compose -f docker-compose.test.yml restart postgres-test
sleep 10

# Test connection manually
docker-compose -f docker-compose.test.yml exec postgres-test \
  psql -U testuser -d contravento_test -c "SELECT 1;"
```

#### Issue 3: Stale Test Data

**Symptoms**: Tests fail due to existing data from previous runs

**Fix**: Always cleanup between runs
```bash
# Remove volumes (reset database)
docker-compose -f docker-compose.test.yml down -v

# Restart fresh
docker-compose -f docker-compose.test.yml up -d
sleep 10
```

#### Issue 4: Slow Test Startup

**Symptoms**: Tests take >30s to start

**Optimization**:
```bash
# Use in-memory database for faster tests
# Edit docker-compose.test.yml:
postgres-test:
  tmpfs:
    - /var/lib/postgresql/data  # In-memory database

# Or use SQLite for unit tests (much faster)
# In conftest.py:
@pytest.fixture
def db_url():
    return "sqlite+aiosqlite:///:memory:"  # In-memory SQLite
```

---

## Best Practices

### Test Isolation

**Always cleanup after tests**:

```python
# conftest.py
@pytest.fixture(autouse=True)
async def cleanup_database(db_session):
    """Clean database after each test."""
    yield
    # Cleanup logic
    await db_session.rollback()
    await db_session.close()
```

### Fast Test Execution

**Optimize test speed**:

1. **Use transactions** (rollback instead of delete):
   ```python
   @pytest.fixture
   async def db_transaction(db_session):
       async with db_session.begin():
           yield db_session
           # Auto-rollback on exit
   ```

2. **Parallel execution**:
   ```bash
   pytest -n auto  # Use all CPU cores
   ```

3. **Mark slow tests**:
   ```python
   @pytest.mark.slow
   def test_expensive_operation():
       pass
   ```

   ```bash
   # Run fast tests only
   pytest -m "not slow"
   ```

### CI/CD Optimization

**Cache dependencies**:

```yaml
# .github/workflows/tests.yml
- name: Cache Poetry dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pypoetry
    key: ${{ runner.os }}-poetry-${{ hashFiles('**/poetry.lock') }}

- name: Cache npm dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

---

## Related Modes

### Progression Path

```
Test → Local-Dev → Preproduction → Staging
```

**Typical Workflow**:
1. **Test Mode** - Run integration tests (YOU ARE HERE)
2. **Local-Dev** - Daily feature development
3. **Preproduction** - CI/CD validation
4. **Staging** - Manual QA testing

### Comparison with Similar Modes

**Test vs Preproduction**:

| Aspect | Test Mode | Preproduction Mode |
|--------|:---------:|:------------------:|
| **Containers** | DB + Redis only | Full stack (backend, frontend, db) |
| **Startup** | ~15s | ~20s |
| **Image Source** | N/A (local code) | Docker Hub |
| **Use Case** | Integration tests | Full-stack validation |

**When to Use Each**:
- **Test Mode**: Unit and integration tests during development
- **Preproduction Mode**: CI/CD validation before staging

### Related Documentation

- **[Local-Dev Mode](./local-dev.md)** - Daily development environment
- **[Preproduction Mode](./preproduction.md)** - CI/CD validation
- **[Troubleshooting Guide](../guides/troubleshooting.md)** - Common issues

---

## Resource Requirements

**Minimum**:
- **CPU**: 1 core
- **RAM**: 512 MB
- **Disk**: 2 GB
- **Startup Time**: ~15 seconds

**Estimated Costs**: Free (runs locally)

---

## Summary

**Test Mode** is designed for:
- ✅ **Fast** integration test execution (~15s startup)
- ✅ **Isolated** from local development environment
- ✅ **Ephemeral** (clean state every run)
- ✅ **CI/CD friendly** (non-conflicting ports)

**Use when**: You need to run integration tests with PostgreSQL and Redis without affecting your local development environment.

---

**Last Updated**: 2026-02-06
**Document Version**: 1.0
**Feedback**: Report issues or suggest improvements via GitHub Issues
