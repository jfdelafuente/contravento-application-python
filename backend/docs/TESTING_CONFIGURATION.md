# Testing Configuration Guide

This document explains how test configuration works in the ContraVento backend, including the `.env.test` file and `conftest.py` setup.

---

## Table of Contents

1. [Overview](#overview)
2. [Configuration Files](#configuration-files)
3. [How It Works](#how-it-works)
4. [Test Environment Variables](#test-environment-variables)
5. [Running Tests](#running-tests)
6. [Customizing Test Configuration](#customizing-test-configuration)
7. [Troubleshooting](#troubleshooting)

---

## Overview

Tests in ContraVento use a **dedicated test configuration** loaded from `backend/.env.test`. This ensures:

- ✅ **Isolated environment**: Tests don't interfere with development database
- ✅ **Fast execution**: Optimized settings (fast bcrypt, in-memory DB)
- ✅ **Consistency**: All developers use the same test configuration
- ✅ **Maintainability**: Configuration centralized in one file

---

## Configuration Files

### `.env.test` (Test Configuration)

**Location**: `backend/.env.test`

**Purpose**: Defines environment variables specifically for tests

**Key Settings**:
```bash
# Test Environment
APP_ENV=testing
DEBUG=false

# In-memory SQLite database (fresh for each test)
DATABASE_URL=sqlite+aiosqlite:///:memory:

# Fast bcrypt for quick tests (4 rounds instead of 12)
BCRYPT_ROUNDS=4

# Test-specific secret key
SECRET_KEY=test-secret-key-for-testing-only-not-for-production

# Reduced logging (WARNING level to reduce noise)
LOG_LEVEL=WARNING

# Permissive rate limiting for tests
LOGIN_MAX_ATTEMPTS=10
LOGIN_LOCKOUT_MINUTES=1
```

### `conftest.py` (Pytest Configuration)

**Location**: `backend/tests/conftest.py`

**Purpose**: Loads `.env.test` automatically before tests run

**Key Fixture**:
```python
@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Load test environment variables from .env.test"""
    env_file = Path(__file__).parent.parent / ".env.test"

    if env_file.exists():
        load_dotenv(env_file, override=True)
        os.environ["APP_ENV"] = "testing"
    else:
        # Fallback to minimal defaults
        os.environ.setdefault("APP_ENV", "testing")
        os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
        os.environ.setdefault("SECRET_KEY", "test-secret-key")
        os.environ.setdefault("BCRYPT_ROUNDS", "4")
```

---

## How It Works

### Execution Flow

```
1. pytest backend/tests/
   ↓
2. conftest.py loads
   ↓
3. load_test_env fixture executes (autouse=True, scope="session")
   ↓
4. Reads backend/.env.test
   ↓
5. Sets environment variables
   ↓
6. Forces APP_ENV=testing
   ↓
7. Tests execute with test configuration
```

### Why `autouse=True`?

The `load_test_env` fixture has `autouse=True`, meaning it runs automatically without being explicitly requested by tests:

```python
@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    # Runs once per test session, before any tests
    # All tests inherit these environment variables
```

### Scope: `session`

The fixture has `scope="session"`, so it runs **once** at the start of the entire test session, not per test:

- ✅ **Fast**: Configuration loaded only once
- ✅ **Consistent**: All tests use same environment
- ✅ **Efficient**: No overhead per test

---

## Test Environment Variables

### Database Configuration

```bash
# In-memory SQLite for speed and isolation
DATABASE_URL=sqlite+aiosqlite:///:memory:
```

**Why in-memory?**
- Each test gets a fresh, empty database
- No cleanup required (database disappears after test)
- Fast (no disk I/O)
- Parallel-safe (each test process has its own DB)

### Performance Optimization

```bash
# Fast password hashing (4 rounds vs 12 in production)
BCRYPT_ROUNDS=4
```

**Why 4 rounds?**
- Production uses 12-14 rounds for security
- Tests don't need strong hashing (fake passwords)
- 4 rounds = ~10ms vs 12 rounds = ~300ms
- Saves ~290ms per password hash in tests

### Authentication

```bash
# Test-specific JWT settings
SECRET_KEY=test-secret-key-for-testing-only-not-for-production
ACCESS_TOKEN_EXPIRE_MINUTES=5
REFRESH_TOKEN_EXPIRE_DAYS=1
```

**Why short expiration?**
- Tests run quickly (5 minutes is enough)
- Forces testing of token refresh logic

### Email Configuration

```bash
# Email disabled for tests (no SMTP server needed)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=test@contravento.com
SMTP_TLS=false
```

**Email handling in tests**:
- Email functions are mocked in tests
- No real emails sent
- Verification emails simulated

### Logging

```bash
# Reduce test output noise
LOG_LEVEL=WARNING
LOG_FORMAT=text
```

**Why WARNING level?**
- Tests only show warnings and errors
- Reduces console clutter
- Makes test failures easier to spot

### Rate Limiting

```bash
# More permissive for tests
LOGIN_MAX_ATTEMPTS=10
LOGIN_LOCKOUT_MINUTES=1
```

**Why permissive?**
- Tests may trigger multiple login attempts
- Faster lockout reset (1 minute vs 15 in production)

---

## Running Tests

### Basic Test Execution

```bash
cd backend

# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/unit/test_auth_service.py

# Run specific test function
poetry run pytest tests/unit/test_auth_service.py::test_register_user

# Run with verbose output
poetry run pytest -v

# Run with coverage
poetry run pytest --cov=src --cov-report=html
```

### Test Categories

```bash
# Unit tests only (fast)
poetry run pytest tests/unit/ -v

# Integration tests only
poetry run pytest tests/integration/ -v

# Contract tests only
poetry run pytest tests/contract/ -v

# Run with markers
poetry run pytest -m unit
poetry run pytest -m integration
```

### Useful Flags

```bash
# Stop on first failure
poetry run pytest -x

# Show local variables on failure
poetry run pytest -l

# Run last failed tests
poetry run pytest --lf

# Run tests in parallel (requires pytest-xdist)
poetry run pytest -n auto
```

---

## Customizing Test Configuration

### Local Overrides

You can override test configuration for local debugging:

**Option 1: Environment Variables**
```bash
# Override specific settings
BCRYPT_ROUNDS=12 poetry run pytest tests/unit/test_auth_service.py
LOG_LEVEL=DEBUG poetry run pytest -v
```

**Option 2: Temporary `.env.test` Changes**
```bash
# Edit backend/.env.test
LOG_LEVEL=DEBUG  # Change for debugging
BCRYPT_ROUNDS=12 # Test with production-like hashing

# Run tests
poetry run pytest

# Revert changes after debugging
git restore backend/.env.test
```

### Custom Test Fixtures

You can create test-specific fixtures that override configuration:

```python
# tests/conftest.py or specific test file

@pytest.fixture
def slow_bcrypt_config(monkeypatch):
    """Override BCRYPT_ROUNDS for specific tests"""
    monkeypatch.setenv("BCRYPT_ROUNDS", "12")

# Usage in test
def test_production_bcrypt_performance(slow_bcrypt_config):
    # This test runs with BCRYPT_ROUNDS=12
    pass
```

---

## Troubleshooting

### Tests Using Wrong Database

**Problem**: Tests modifying development database instead of in-memory

**Solution**: Verify `.env.test` is loaded:
```python
# Add to test to debug
import os
print(os.environ.get("DATABASE_URL"))
# Should print: sqlite+aiosqlite:///:memory:
```

**Fix**: Ensure `conftest.py` has `load_test_env` fixture with `autouse=True`

### Slow Test Execution

**Problem**: Tests taking too long

**Check**:
```bash
# Verify fast bcrypt
grep BCRYPT_ROUNDS backend/.env.test
# Should be: BCRYPT_ROUNDS=4
```

**Check test database**:
```bash
# Verify in-memory database
grep DATABASE_URL backend/.env.test
# Should be: DATABASE_URL=sqlite+aiosqlite:///:memory:
```

### Configuration Not Loading

**Problem**: Changes to `.env.test` not taking effect

**Solutions**:

1. **Clear pytest cache**:
```bash
cd backend
rm -rf .pytest_cache __pycache__ tests/__pycache__
poetry run pytest --cache-clear
```

2. **Verify file path**:
```python
# Add debug print in conftest.py
env_file = Path(__file__).parent.parent / ".env.test"
print(f"Loading env from: {env_file}")
print(f"File exists: {env_file.exists()}")
```

3. **Check for conflicting environment variables**:
```bash
# Unset any conflicting vars
unset DATABASE_URL
unset APP_ENV
poetry run pytest
```

### Missing `.env.test`

**Problem**: `.env.test` file not found

**Solution**: The `load_test_env` fixture has a fallback:

```python
# Fallback sets minimal defaults
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("BCRYPT_ROUNDS", "4")
```

**To restore `.env.test`**:
```bash
# Copy from example if available
cp backend/.env.test.example backend/.env.test

# Or create new one with defaults (see Configuration Files section)
```

---

## Best Practices

### 1. Never Commit Real Secrets to `.env.test`

```bash
# ✅ Good (test-specific, fake secret)
SECRET_KEY=test-secret-key-for-testing-only

# ❌ Bad (real production secret)
SECRET_KEY=aBc123RealProductionSecretXyZ
```

### 2. Keep `.env.test` Simple

Only include settings that differ from defaults or need explicit values for tests.

### 3. Use Mocks for External Services

```python
# ✅ Good - Mock email service
with patch("src.services.auth_service.send_verification_email") as mock:
    mock.return_value = True
    await auth_service.register(user_data)

# ❌ Bad - Rely on real SMTP server
await auth_service.register(user_data)  # Sends real email
```

### 4. Document Custom Settings

If you add custom settings to `.env.test`, document why:

```bash
# Custom setting for feature X testing
FEATURE_X_TIMEOUT=1  # Reduced from 30s for faster tests
```

### 5. Test with Production-like Config Occasionally

```bash
# Occasionally test with production bcrypt to catch timing issues
BCRYPT_ROUNDS=12 poetry run pytest tests/integration/
```

---

## Comparison: Development vs Testing Configuration

| Setting | Development (`.env.dev.example`) | Testing (`.env.test`) |
|---------|----------------------------------|----------------------|
| **Database** | SQLite file (`contravento_dev.db`) | SQLite in-memory |
| **APP_ENV** | `development` | `testing` |
| **DEBUG** | `true` | `false` |
| **BCRYPT_ROUNDS** | `4` | `4` |
| **LOG_LEVEL** | `DEBUG` | `WARNING` |
| **SECRET_KEY** | Generated on setup | Fixed test key |
| **Email** | Logged to console | Mocked |
| **Persistence** | Data persists between runs | Fresh DB per test |

---

## Related Documentation

- [Testing Patterns](../docs/TESTING.md) - General testing approach and patterns
- [Environment Configuration](../../ENVIRONMENTS.md) - All environment configurations
- [Quick Start Guide](../../QUICK_START.md) - Development setup options

---

**Last Updated**: 2026-01-07
