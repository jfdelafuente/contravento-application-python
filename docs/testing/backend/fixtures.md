# Test Configuration & Fixtures

Test configuration and pytest fixtures for backend testing.

**Migrated from**: `backend/docs/TESTING_CONFIGURATION.md` (Phase 3 consolidation)

---

## Table of Contents

- [Overview](#overview)
- [Test Environment Configuration](#test-environment-configuration)
- [How It Works](#how-it-works)
- [Available Fixtures](#available-fixtures)
- [Custom Fixtures](#custom-fixtures)
- [Troubleshooting](#troubleshooting)

---

## Overview

Tests use a **dedicated test configuration** loaded from `backend/.env.test` ensuring:

- ✅ **Isolated environment** - Tests don't interfere with development database
- ✅ **Fast execution** - Optimized settings (fast bcrypt, in-memory DB)
- ✅ **Consistency** - All developers use same test configuration
- ✅ **Maintainability** - Configuration centralized in one file

---

## Test Environment Configuration

### `.env.test` File

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

### `conftest.py` - Pytest Configuration

**Location**: `backend/tests/conftest.py`

**Purpose**: Loads `.env.test` automatically and provides shared fixtures

**Auto-Loading Fixture**:
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
6. src/config.py reads test environment
   ↓
7. Tests run with test configuration
```

### Configuration Priority

```
.env.test (highest priority)
   ↓
Environment variables
   ↓
.env (development - ignored during tests)
   ↓
Default values in config.py
```

**Important**: `.env.test` overrides all other configuration sources during testing.

---

## Available Fixtures

### Core Fixtures

#### `db_session` - Database Session

**Scope**: Function (fresh database per test)

**Type**: `AsyncSession`

**Usage**:
```python
async def test_create_user(db_session):
    """Test with fresh in-memory database"""
    user = User(username="testuser", email="test@example.com")
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.username == "testuser"))
    assert result.scalar_one().email == "test@example.com"
```

**Implementation**:
```python
@pytest.fixture
async def db_session():
    """Provide a clean database session for each test"""
    # Create in-memory SQLite database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    await engine.dispose()
```

---

#### `client` - HTTP Client

**Scope**: Function

**Type**: `httpx.AsyncClient`

**Usage**:
```python
async def test_api_endpoint(client):
    """Test API endpoint with HTTP client"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

**Implementation**:
```python
@pytest.fixture
async def client(db_session):
    """Provide AsyncClient for API testing"""
    from src.main import app

    # Override DB dependency for tests
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

---

#### `test_user` - Test User

**Scope**: Function

**Type**: `User` model instance

**Usage**:
```python
async def test_with_user(client, test_user):
    """Test with pre-created test user"""
    assert test_user.username == "testuser"
    assert test_user.email == "test@example.com"
    assert test_user.is_verified is True
```

**Implementation**:
```python
@pytest.fixture
async def test_user(db_session):
    """Create a verified test user"""
    from src.services.auth_service import AuthService

    user = await AuthService.register(
        db_session,
        UserRegisterInput(
            username="testuser",
            email="test@example.com",
            password="TestPass123!",
            cycling_type="road"
        )
    )

    # Auto-verify for tests
    user.is_verified = True
    await db_session.commit()
    await db_session.refresh(user)

    return user
```

---

#### `auth_headers` - Authenticated Headers

**Scope**: Function

**Type**: `dict`

**Usage**:
```python
async def test_protected_endpoint(client, auth_headers):
    """Test endpoint requiring authentication"""
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["username"] == "testuser"
```

**Implementation**:
```python
@pytest.fixture
async def auth_headers(client, test_user):
    """Provide authentication headers for protected endpoints"""
    # Login to get access token
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123!"
        }
    )

    assert response.status_code == 200
    access_token = response.json()["data"]["access_token"]

    return {"Authorization": f"Bearer {access_token}"}
```

---

#### `faker` - Test Data Generator

**Scope**: Session (reused across tests)

**Type**: `Faker` instance

**Usage**:
```python
async def test_with_fake_data(client, auth_headers, faker):
    """Test with realistic fake data"""
    trip_data = {
        "title": faker.sentence(nb_words=5),
        "description": faker.text(max_nb_chars=200),
        "start_date": faker.date_between(start_date="-30d", end_date="today").isoformat(),
        "distance_km": faker.pyfloat(min_value=1.0, max_value=500.0, right_digits=1)
    }

    response = await client.post("/trips", json=trip_data, headers=auth_headers)
    assert response.status_code == 201
```

**Implementation**:
```python
@pytest.fixture(scope="session")
def faker():
    """Provide Faker instance for generating test data"""
    from faker import Faker
    return Faker("es_ES")  # Spanish locale
```

---

## Custom Fixtures

### Creating Custom Fixtures

**Example: Admin User Fixture**
```python
@pytest.fixture
async def admin_user(db_session):
    """Create an admin user for testing admin endpoints"""
    from src.models import User, Role

    user = User(
        username="admin",
        email="admin@example.com",
        password_hash="hashed",
        role=Role.ADMIN,
        is_verified=True
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user
```

**Example: Trip with Photos Fixture**
```python
@pytest.fixture
async def trip_with_photos(db_session, test_user):
    """Create a trip with 3 test photos"""
    trip = Trip(
        user_id=test_user.user_id,
        title="Test Trip with Photos",
        description="A trip with multiple photos",
        start_date="2024-06-01",
        status=TripStatus.PUBLISHED
    )
    db_session.add(trip)
    await db_session.commit()

    # Add 3 photos
    for i in range(3):
        photo = TripPhoto(
            trip_id=trip.trip_id,
            photo_url=f"/storage/test_photo_{i}.jpg",
            order=i
        )
        db_session.add(photo)

    await db_session.commit()
    await db_session.refresh(trip)

    return trip
```

**Usage**:
```python
async def test_delete_trip_with_photos(client, auth_headers, trip_with_photos):
    """Test cascading delete of trip with photos"""
    trip_id = trip_with_photos.trip_id

    response = await client.delete(f"/trips/{trip_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify photos were also deleted
    # ... verification logic
```

---

### Fixture Scopes

**Function** (default) - New instance per test:
```python
@pytest.fixture  # scope="function" is default
async def db_session():
    # Fresh database for each test
    ...
```

**Class** - Shared across tests in a class:
```python
@pytest.fixture(scope="class")
async def shared_user():
    # One user for all tests in TestClass
    ...
```

**Module** - Shared across tests in a file:
```python
@pytest.fixture(scope="module")
async def shared_config():
    # One config for all tests in module
    ...
```

**Session** - Shared across entire test run:
```python
@pytest.fixture(scope="session")
def faker():
    # One Faker instance for all tests
    ...
```

---

## Troubleshooting

### Issue: Tests Using Development Database

**Symptom**: Tests modify development data

**Cause**: `.env.test` not loaded

**Solution**:
```bash
# Verify .env.test exists
ls backend/.env.test

# Check DATABASE_URL in tests
pytest -s -k "test_name" --verbose
# Should see: DATABASE_URL=sqlite+aiosqlite:///:memory:
```

---

### Issue: Slow Test Execution

**Symptom**: Tests take >30 seconds

**Cause**: Using production bcrypt rounds (12) instead of test rounds (4)

**Solution**:
```bash
# Check .env.test has:
BCRYPT_ROUNDS=4

# Verify in tests
pytest -s -k "test_login" --verbose
```

---

### Issue: Test Database Not Isolated

**Symptom**: Tests affect each other

**Cause**: Using `scope="session"` for `db_session`

**Solution**:
```python
# Use function scope (default) for db_session
@pytest.fixture  # NOT scope="session"
async def db_session():
    ...
```

---

### Issue: Foreign Key Constraints Not Enforced

**Symptom**: Orphan records created in tests

**Cause**: SQLite foreign keys not enabled

**Solution**:
```python
# In db_session fixture, enable foreign keys
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

# Enable foreign keys
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
```

---

## Related Documentation

- **[Integration Tests](integration-tests.md)** - Full workflow testing
- **[Unit Tests](unit-tests.md)** - Service layer testing
- **[API Reference](../../api/README.md)** - API documentation
- **[CI/CD](../ci-cd/github-actions.md)** - Automated testing

---

**Last Updated**: 2026-02-06 (Migrated from backend/docs/)
**Test Framework**: pytest + pytest-asyncio
**Database**: SQLite in-memory
