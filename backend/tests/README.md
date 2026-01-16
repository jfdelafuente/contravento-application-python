# ContraVento Backend Tests

This directory contains automated tests for the ContraVento backend API.

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration and shared fixtures
├── helpers.py           # Test helper functions
├── fixtures/            # Test data fixtures
│   ├── users.json       # Sample user accounts
│   ├── trips.json       # Sample trip data
│   ├── tags.json        # Sample tags
│   └── photos/          # Sample photos for upload tests
├── unit/                # Unit tests (fast, isolated)
├── integration/         # Integration tests (API + database)
├── contract/            # Contract tests (OpenAPI validation)
└── performance/         # Performance tests (latency, load)
```

## Running Tests

### All Tests

```bash
cd backend
poetry run pytest
```

### By Test Type

```bash
# Unit tests only (fast)
poetry run pytest -m unit

# Integration tests only
poetry run pytest -m integration

# Contract tests only
poetry run pytest -m contract

# Performance tests only
poetry run pytest -m performance

# Exclude slow tests
poetry run pytest -m "not slow"
```

### With Coverage

```bash
# Run tests with coverage report
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Specific Test File

```bash
poetry run pytest tests/integration/test_auth_api.py -v
```

### Specific Test Function

```bash
poetry run pytest tests/integration/test_auth_api.py::test_register_user_flow -v
```

## Using Test Fixtures

### Database and HTTP Client

```python
import pytest

@pytest.mark.integration
async def test_api_endpoint(client, db_session):
    """
    client: httpx.AsyncClient for API requests
    db_session: AsyncSession for database operations
    """
    response = await client.get("/health")
    assert response.status_code == 200
```

### Authentication

```python
@pytest.mark.integration
async def test_protected_endpoint(client, auth_headers):
    """
    auth_headers: dict with {"Authorization": "Bearer <token>"}
    """
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### Test Users

```python
@pytest.mark.integration
async def test_user_trip(client, auth_headers, test_user):
    """
    test_user: User instance (regular USER role)
    """
    response = await client.get(
        f"/users/{test_user.username}/trips",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### JSON Fixtures

```python
@pytest.mark.unit
async def test_load_users(db_session, load_json_fixture):
    """
    load_json_fixture: Callable that loads JSON files
    """
    users_data = load_json_fixture("users.json")
    assert len(users_data["users"]) == 4
    assert users_data["users"][0]["username"] == "admin_test"
```

### Helper Functions

```python
from tests.helpers import create_user, create_trip

@pytest.mark.integration
async def test_create_trip(db_session):
    # Create test user
    user = await create_user(
        db_session,
        username="testuser",
        email="test@example.com"
    )

    # Create test trip
    trip = await create_trip(
        db_session,
        user_id=user.id,
        title="Test Trip",
        description="Test trip with at least 50 characters for validation.",
        distance_km=100.0,
        tags=["bikepacking", "montaña"]
    )

    assert trip.trip_id is not None
    assert len(trip.tags) == 2
```

### Sample Photos

```python
from tests.helpers import get_sample_photo_path

@pytest.mark.integration
async def test_photo_upload(client, auth_headers, test_user):
    # Create trip first
    trip = await create_trip(db_session, user_id=test_user.id)

    # Upload photo
    photo_path = get_sample_photo_path("sample_1.jpg")
    with open(photo_path, "rb") as f:
        response = await client.post(
            f"/trips/{trip.trip_id}/photos",
            headers=auth_headers,
            files={"file": f}
        )

    assert response.status_code == 201
```

## Test Markers

Tests can be marked with categories for selective execution:

```python
import pytest

@pytest.mark.unit
async def test_business_logic():
    """Unit test for business logic"""
    pass

@pytest.mark.integration
async def test_api_endpoint(client):
    """Integration test for API endpoint"""
    pass

@pytest.mark.contract
async def test_openapi_schema():
    """Contract test for OpenAPI validation"""
    pass

@pytest.mark.performance
async def test_endpoint_latency():
    """Performance test for latency"""
    pass

@pytest.mark.slow
async def test_long_running():
    """Test that takes >1 second"""
    pass
```

## Fixture Data

### users.json

Contains 4 test users:

- `admin_test`: Admin user (ADMIN role, verified)
- `maria_test`: Regular user (USER role, verified, mountain cycling)
- `juan_test`: Unverified user (USER role, not verified)
- `carlos_test`: Regular user (USER role, verified, bikepacking)

All users have password: `TestPass123!`

### trips.json

Contains 5 test trips:

- `draft_trip`: Draft trip (not published)
- `published_trip`: Published trip with photos and locations (Pirineos)
- `minimal_trip`: Minimal trip with required fields only
- `short_trip`: Short coastal trip (Valencia)
- `long_trip`: Long tour (Camino de Santiago)

### tags.json

Contains 10 test tags:

- `bikepacking`, `montaña`, `road`, `pirineos`, `gravel`, `touring`, `costa`, `camino`, `pilgrimage`, `urbano`

Tags include usage counts for popularity testing.

## Writing New Tests

### 1. Choose Test Type

- **Unit**: Test business logic in isolation (services, utils)
- **Integration**: Test API endpoints with database
- **Contract**: Test OpenAPI schema compliance
- **Performance**: Test response times and load handling

### 2. Use Appropriate Fixtures

```python
# For unit tests (no HTTP client needed)
@pytest.mark.unit
async def test_service(db_session):
    pass

# For integration tests (API + database)
@pytest.mark.integration
async def test_api(client, db_session, auth_headers):
    pass
```

### 3. Follow TDD Workflow

1. Write failing test first (Red)
2. Implement minimal code to pass (Green)
3. Refactor while keeping tests passing
4. Never skip writing tests

### 4. Test Naming Convention

```python
# Good names (describe what is being tested)
async def test_register_user_creates_account_and_sends_verification_email():
    pass

async def test_login_with_invalid_credentials_returns_401():
    pass

# Bad names (too vague)
async def test_register():
    pass

async def test_login_failure():
    pass
```

### 5. Arrange-Act-Assert Pattern

```python
@pytest.mark.integration
async def test_create_trip(client, auth_headers, test_user):
    # Arrange
    trip_data = {
        "title": "Test Trip",
        "description": "This is a test trip with at least 50 characters.",
        "start_date": "2025-06-01",
        "distance_km": 100.0
    }

    # Act
    response = await client.post(
        "/trips",
        headers=auth_headers,
        json=trip_data
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Test Trip"
```

## Coverage Requirements

- **Minimum coverage**: 90%
- **Branch coverage**: Enabled (measures if/else branches)
- **Excluded files**: migrations, tests, __init__.py

To check coverage:

```bash
poetry run pytest --cov=src --cov-report=term --cov-fail-under=90
```

## Troubleshooting

### Tests fail with "RuntimeError: Event loop is closed"

Make sure you're using `async def` for async tests:

```python
# Correct
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_operation()
    assert result is not None

# Wrong (missing async)
def test_async_function():  # Will fail
    result = await some_async_operation()
```

### Import errors for src modules

Make sure you're running tests from the `backend/` directory:

```bash
cd backend
poetry run pytest
```

### Database errors in tests

Each test gets a fresh in-memory SQLite database. If you see database errors:

1. Check that models are properly imported in `src/database.py`
2. Verify foreign key relationships are correct
3. Ensure you're using `await db_session.commit()` after changes

### Photo upload tests fail

Make sure sample photos exist in `tests/fixtures/photos/`:

```bash
ls -la backend/tests/fixtures/photos/
# Should show: sample_1.jpg, sample_2.jpg, sample_large.jpg
```

If placeholders exist, replace them with real images (see fixtures/README.md).

## CI/CD Integration

Tests run automatically on every PR via GitHub Actions:

- Unit tests: <5 minutes
- Integration tests: <5 minutes (with PostgreSQL container)
- Coverage check: ≥90% required
- PRs with failing tests are blocked from merge

See `.github/workflows/test.yml` for CI configuration.

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [httpx AsyncClient](https://www.python-httpx.org/async/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
