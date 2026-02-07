# Backend Integration Tests

Integration testing guide for ContraVento backend API.

**Migrated from**: `backend/docs/TESTING_GUIDE.md` (Phase 3 consolidation)

---

## Table of Contents

- [Overview](#overview)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Test by Feature](#test-by-feature)
- [Coverage Requirements](#coverage-requirements)
- [Writing Integration Tests](#writing-integration-tests)
- [Common Patterns](#common-patterns)

---

## Overview

Backend tests use **pytest** with async support (`pytest-asyncio`) and cover three layers:

```
Contract Tests (116 tests)  ← Validate API responses against OpenAPI specs
       ↓
Integration Tests          ← Full workflows with real database
       ↓
Unit Tests                 ← Isolated service logic
```

**Test Database**: SQLite in-memory (`:memory:`) for speed and isolation

**Coverage Requirement**: ≥90% for all modules

---

## Running Tests

### Complete Test Suite

```bash
cd backend

# Run all tests with coverage
poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term -v

# View HTML coverage report
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

### By Test Category

**Contract Tests** (validate responses against OpenAPI):
```bash
# All contract tests (116 tests)
poetry run pytest tests/contract/ -v

# By module
poetry run pytest tests/contract/test_auth_contracts.py -v       # 22 tests
poetry run pytest tests/contract/test_profile_contracts.py -v    # 14 tests
poetry run pytest tests/contract/test_social_contracts.py -v     # 22 tests
poetry run pytest tests/contract/test_stats_contracts.py -v      # 14 tests
poetry run pytest tests/contract/test_trip_contracts.py -v       # 35 tests
poetry run pytest tests/contract/test_trip_photo_contracts.py -v # 9 tests
```

**Integration Tests** (full workflows with database):
```bash
poetry run pytest tests/integration/ -v
```

**Unit Tests** (isolated service logic):
```bash
poetry run pytest tests/unit/ -v
```

---

## Test Categories

### 1. Contract Tests

**Purpose**: Validate API responses match OpenAPI specifications

**Example**:
```python
# tests/contract/test_trip_contracts.py
async def test_create_trip_contract(client, auth_headers):
    """Verify POST /trips returns schema-compliant response"""
    response = await client.post(
        "/trips",
        json={
            "title": "Test Trip",
            "description": "A test trip",
            "start_date": "2024-06-01"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()

    # Validate response structure
    assert data["success"] is True
    assert "trip_id" in data["data"]
    assert data["data"]["title"] == "Test Trip"
    assert data["data"]["status"] == "draft"
    assert data["error"] is None
```

**When to use**:
- After changing API endpoints
- Before deploying to staging/production
- When updating OpenAPI contracts

---

### 2. Integration Tests

**Purpose**: Test complete user workflows with database

**Example**:
```python
# tests/integration/test_trips_api.py
async def test_trip_workflow(client, db_session, auth_headers):
    """Test complete trip creation → publish → edit flow"""
    # 1. Create draft trip
    response = await client.post(
        "/trips",
        json={"title": "My Trip", "description": "...", "start_date": "2024-06-01"},
        headers=auth_headers
    )
    assert response.status_code == 201
    trip_id = response.json()["data"]["trip_id"]

    # 2. Publish trip
    response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "published"

    # 3. Edit trip (optimistic locking)
    response = await client.put(
        f"/trips/{trip_id}",
        json={"title": "Updated Title", "client_updated_at": "..."},
        headers=auth_headers
    )
    assert response.status_code == 200
```

**When to use**:
- Testing multi-step user journeys
- Validating database state changes
- Ensuring cascading deletes work
- Testing permission/authorization logic

---

### 3. Unit Tests

**Purpose**: Test service layer logic in isolation

**Example**:
```python
# tests/unit/test_trip_service.py
async def test_calculate_trip_stats(db_session):
    """Test stats calculation for published trip"""
    user = await create_test_user(db_session)

    trip = await TripService.create_trip(
        db_session,
        user,
        TripCreateInput(
            title="Test Trip",
            description="...",
            start_date="2024-06-01",
            distance_km=127.5
        )
    )

    await TripService.publish_trip(db_session, trip.trip_id, user)

    # Verify stats updated
    stats = await StatsService.get_user_stats(db_session, user.user_id)
    assert stats.trip_count == 1
    assert stats.total_distance_km == 127.5
```

**When to use**:
- Testing business logic in services
- Validating calculations (stats, distances)
- Testing edge cases and error conditions

---

## Test by Feature

### User Profile Features (001-user-profiles)

**User Story 1: Authentication**
```bash
poetry run pytest tests/contract/test_auth_contracts.py -v
poetry run pytest tests/integration/test_auth_workflow.py -v
```

**User Story 2: Profiles**
```bash
poetry run pytest tests/contract/test_profile_contracts.py -v
poetry run pytest tests/integration/test_profile_management.py -v
```

**User Story 3: Stats & Achievements**
```bash
poetry run pytest tests/contract/test_stats_contracts.py -v
poetry run pytest tests/integration/test_stats_calculation.py -v
```

**User Story 4: Social Features**
```bash
poetry run pytest tests/contract/test_social_contracts.py -v
poetry run pytest tests/integration/test_follow_workflow.py -v
```

---

### Travel Diary Features (002-travel-diary)

**User Story 1: Create Trips**
```bash
# Contract tests
poetry run pytest tests/contract/test_trip_contracts.py::TestCreateTripContract -v

# Integration tests
poetry run pytest tests/integration/test_trips_api.py::TestCreateTrip -v

# Unit tests
poetry run pytest tests/unit/test_trip_service.py::TestCreateTrip -v
```

**User Story 2: Upload Trip Photos**
```bash
# Contract tests
poetry run pytest tests/contract/test_trip_photo_contracts.py -v

# Integration tests
poetry run pytest tests/integration/test_trips_api.py -k "photo" -v

# Unit tests
poetry run pytest tests/unit/test_trip_service.py -k "photo" -v
```

**User Story 3: Edit/Delete Trips**
```bash
poetry run pytest tests/integration/test_trips_api.py -k "edit or delete" -v
```

**User Story 4: Tags & Categorization**
```bash
poetry run pytest tests/integration/test_trips_api.py -k "tag" -v
```

---

## Coverage Requirements

**Minimum Coverage**: ≥90% for all modules

**Check Coverage**:
```bash
cd backend
poetry run pytest --cov=src --cov-fail-under=90 --cov-report=term
```

**Coverage Report**:
```
----------- coverage: platform linux, python 3.12.1 -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/__init__.py                   0      0   100%
src/api/auth.py                  85      2    98%
src/api/trips.py                142      5    96%
src/services/trip_service.py    256     12    95%
src/services/auth_service.py    134      4    97%
-------------------------------------------------
TOTAL                          3542    152    96%
```

**Failing Coverage** (example):
```bash
# Will exit with error if coverage < 90%
poetry run pytest --cov=src --cov-fail-under=90
```

---

## Writing Integration Tests

### Test Structure

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_feature_name(
    client: AsyncClient,        # HTTP client fixture
    db_session: AsyncSession,   # Database session fixture
    auth_headers: dict          # Authenticated user headers
):
    """Test description following Given-When-Then pattern"""
    # GIVEN: Setup initial state
    trip_data = {
        "title": "Test Trip",
        "description": "Test description",
        "start_date": "2024-06-01"
    }

    # WHEN: Execute action
    response = await client.post("/trips", json=trip_data, headers=auth_headers)

    # THEN: Verify outcome
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Test Trip"
```

### Common Fixtures

**Available in `conftest.py`**:
- `client` - AsyncClient for API requests
- `db_session` - Fresh SQLite in-memory database
- `auth_headers` - Pre-authenticated user headers
- `test_user` - Created test user
- `faker` - Faker instance for test data

**Example Usage**:
```python
async def test_with_fixtures(client, db_session, test_user, faker):
    # test_user is automatically created and available
    assert test_user.email == "test@example.com"

    # faker generates realistic test data
    trip_title = faker.sentence(nb_words=5)
    location_name = faker.city()
```

---

## Common Patterns

### 1. Testing Authentication

```python
async def test_login_flow(client):
    """Test complete login → refresh → logout flow"""
    # Login
    response = await client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    # Use access token
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    # Refresh token
    response = await client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 200
    new_access_token = response.json()["data"]["access_token"]

    # Logout
    response = await client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert response.status_code == 200
```

### 2. Testing Permissions

```python
async def test_owner_only_actions(client, db_session):
    """Test that only trip owner can edit/delete"""
    # User 1 creates trip
    headers1 = await create_auth_headers(client, "user1@example.com")
    response = await client.post("/trips", json={...}, headers=headers1)
    trip_id = response.json()["data"]["trip_id"]

    # User 2 tries to edit (should fail)
    headers2 = await create_auth_headers(client, "user2@example.com")
    response = await client.put(f"/trips/{trip_id}", json={...}, headers=headers2)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
```

### 3. Testing Validation

```python
async def test_validation_errors(client, auth_headers):
    """Test field validation and error messages"""
    # Missing required field
    response = await client.post(
        "/trips",
        json={"description": "Missing title"},
        headers=auth_headers
    )
    assert response.status_code == 422
    assert "title" in response.json()["error"]["message"].lower()

    # Invalid field value
    response = await client.post(
        "/trips",
        json={
            "title": "Test",
            "description": "Short",  # Too short for publishing
            "start_date": "invalid-date"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
```

### 4. Testing Database State

```python
async def test_cascading_delete(client, db_session, auth_headers):
    """Test that deleting trip cascades to photos and locations"""
    # Create trip with photos and locations
    response = await client.post("/trips", json={...}, headers=auth_headers)
    trip_id = response.json()["data"]["trip_id"]

    # Upload photo
    response = await client.post(
        f"/trips/{trip_id}/photos",
        files={"photo": ("test.jpg", photo_bytes, "image/jpeg")},
        headers=auth_headers
    )
    photo_id = response.json()["data"]["photo_id"]

    # Delete trip
    response = await client.delete(f"/trips/{trip_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify photo is also deleted
    from src.models import TripPhoto
    result = await db_session.execute(
        select(TripPhoto).where(TripPhoto.photo_id == photo_id)
    )
    assert result.scalar_one_or_none() is None
```

---

## Related Documentation

- **[Test Configuration](fixtures.md)** - Fixtures and conftest.py setup
- **[Unit Tests](unit-tests.md)** - Service layer testing
- **[Performance Tests](performance-tests.md)** - Load testing with Locust
- **[CI/CD](../ci-cd/github-actions.md)** - Automated testing in CI
- **[API Reference](../../api/README.md)** - API documentation

---

**Last Updated**: 2026-02-06 (Migrated from backend/docs/)
**Test Framework**: pytest + pytest-asyncio
**Coverage Target**: ≥90%
