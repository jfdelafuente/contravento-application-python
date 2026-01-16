# Test Fixtures Data Model

**Feature**: Testing & QA Suite (001-testing-qa)
**Purpose**: Define reusable test data fixtures for unit, integration, and E2E tests

## Overview

Test fixtures provide consistent, version-controlled sample data for automated tests. Fixtures are stored as JSON files in `backend/tests/fixtures/` and loaded dynamically during test execution. This approach ensures:

1. **Reproducibility**: Same test data across all environments (local, CI, staging)
2. **Maintainability**: Easy to update test data without modifying test code
3. **Readability**: Human-readable JSON format for quick inspection
4. **Isolation**: Each test creates unique instances (UUID-based IDs) to prevent conflicts

## Fixture Files

```text
backend/tests/fixtures/
├── users.json          # Sample users (admin, verified, unverified)
├── trips.json          # Sample trips (draft, published, with locations/photos)
├── tags.json           # Sample tags (bikepacking, montaña, etc.)
└── photos/             # Sample images for photo upload tests
    ├── sample_1.jpg    # 800x600 landscape photo (500KB)
    ├── sample_2.jpg    # 600x800 portrait photo (400KB)
    └── sample_large.jpg # 5MB photo for upload limits testing
```

## User Fixtures

**File**: `backend/tests/fixtures/users.json`

**Schema**:

```json
{
  "users": [
    {
      "fixture_id": "admin_user",
      "email": "admin@test.com",
      "username": "test_admin",
      "password_plain": "AdminTest123!",
      "role": "ADMIN",
      "is_verified": true,
      "bio": "Test admin user for integration tests",
      "cycling_type": "road"
    },
    {
      "fixture_id": "verified_user",
      "email": "verified@test.com",
      "username": "test_verified",
      "password_plain": "UserTest123!",
      "role": "USER",
      "is_verified": true,
      "bio": "Test verified user for integration tests",
      "cycling_type": "bikepacking"
    },
    {
      "fixture_id": "unverified_user",
      "email": "unverified@test.com",
      "username": "test_unverified",
      "password_plain": "UserTest123!",
      "role": "USER",
      "is_verified": false,
      "bio": null,
      "cycling_type": null
    }
  ]
}
```

**Field Descriptions**:

- `fixture_id`: Unique identifier for referencing fixture in tests (not database ID)
- `email`: Valid email address for authentication tests
- `username`: Unique username for profile tests
- `password_plain`: Plaintext password (will be bcrypt-hashed when creating user)
- `role`: User role (USER, ADMIN)
- `is_verified`: Email verification status
- `bio`: Optional user bio (max 500 chars)
- `cycling_type`: Optional cycling type (road, mountain, bikepacking, etc.)

**Usage in Tests**:

```python
# conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture
def user_fixtures():
    fixtures_path = Path(__file__).parent / "fixtures" / "users.json"
    with open(fixtures_path) as f:
        return json.load(f)["users"]

@pytest.fixture
async def admin_user(db_session, user_fixtures):
    admin_data = next(u for u in user_fixtures if u["fixture_id"] == "admin_user")
    user = await AuthService.register(db_session, {
        "email": admin_data["email"],
        "username": admin_data["username"],
        "password": admin_data["password_plain"],
    })
    # Set admin role and verify
    user.role = admin_data["role"]
    user.is_verified = admin_data["is_verified"]
    await db_session.commit()
    return user
```

---

## Trip Fixtures

**File**: `backend/tests/fixtures/trips.json`

**Schema**:

```json
{
  "trips": [
    {
      "fixture_id": "draft_trip",
      "title": "Viaje de Prueba (Borrador)",
      "description": "Este es un viaje de prueba en estado borrador para tests de integración.",
      "start_date": "2024-06-01",
      "end_date": "2024-06-05",
      "distance_km": 250.5,
      "difficulty": "moderate",
      "status": "draft",
      "tags": ["bikepacking", "montaña"],
      "locations": [
        {
          "name": "Punto de Inicio",
          "latitude": 42.5063,
          "longitude": 1.5218
        }
      ],
      "photos": []
    },
    {
      "fixture_id": "published_trip",
      "title": "Ruta Bikepacking Pirineos",
      "description": "Viaje de 5 días por los Pirineos con paisajes impresionantes y rutas técnicas. Atravesamos varios puertos de montaña y acampamos en refugios remotos.",
      "start_date": "2024-07-10",
      "end_date": "2024-07-14",
      "distance_km": 320.8,
      "difficulty": "hard",
      "status": "published",
      "tags": ["bikepacking", "montaña", "pirineos"],
      "locations": [
        {
          "name": "Puigcerdà (Inicio)",
          "latitude": 42.4316,
          "longitude": 1.9277
        },
        {
          "name": "Refugio de Colomers",
          "latitude": 42.6667,
          "longitude": 0.9833
        },
        {
          "name": "Vielha (Final)",
          "latitude": 42.7,
          "longitude": 0.8
        }
      ],
      "photos": [
        {
          "filename": "sample_1.jpg",
          "caption": "Vista desde el puerto de montaña",
          "order": 1
        },
        {
          "filename": "sample_2.jpg",
          "caption": "Campamento en el refugio",
          "order": 2
        }
      ]
    },
    {
      "fixture_id": "minimal_trip",
      "title": "Viaje Mínimo",
      "description": "Viaje con campos mínimos requeridos para tests de validación.",
      "start_date": "2024-08-01",
      "end_date": null,
      "distance_km": null,
      "difficulty": null,
      "status": "published",
      "tags": [],
      "locations": [],
      "photos": []
    }
  ]
}
```

**Field Descriptions**:

- `fixture_id`: Unique identifier for referencing fixture in tests
- `title`: Trip title (max 200 chars)
- `description`: Trip description (min 50 chars for published, optional for draft)
- `start_date`: Trip start date (YYYY-MM-DD format)
- `end_date`: Trip end date (optional, YYYY-MM-DD format)
- `distance_km`: Total distance in kilometers (optional)
- `difficulty`: Difficulty level (easy, moderate, hard, extreme) or null
- `status`: Trip status (draft, published)
- `tags`: Array of tag names (lowercase, normalized)
- `locations`: Array of location objects with name, latitude, longitude
- `photos`: Array of photo objects with filename, caption, order

**Usage in Tests**:

```python
@pytest.fixture
async def published_trip(db_session, verified_user, trip_fixtures):
    trip_data = next(t for t in trip_fixtures if t["fixture_id"] == "published_trip")

    # Create trip
    trip = await TripService.create_trip(db_session, verified_user.id, {
        "title": trip_data["title"],
        "description": trip_data["description"],
        "start_date": trip_data["start_date"],
        "end_date": trip_data["end_date"],
        "distance_km": trip_data["distance_km"],
        "difficulty": trip_data["difficulty"],
    })

    # Add tags
    for tag_name in trip_data["tags"]:
        await TripService.add_tag(db_session, trip.trip_id, tag_name)

    # Publish
    await TripService.publish_trip(db_session, trip.trip_id, verified_user.id)

    return trip
```

---

## Tag Fixtures

**File**: `backend/tests/fixtures/tags.json`

**Schema**:

```json
{
  "tags": [
    {
      "name": "bikepacking",
      "normalized": "bikepacking",
      "usage_count": 15
    },
    {
      "name": "Montaña",
      "normalized": "montaña",
      "usage_count": 12
    },
    {
      "name": "Road",
      "normalized": "road",
      "usage_count": 8
    },
    {
      "name": "Pirineos",
      "normalized": "pirineos",
      "usage_count": 5
    }
  ]
}
```

**Field Descriptions**:

- `name`: Display name (preserves capitalization)
- `normalized`: Lowercase version for matching
- `usage_count`: Initial usage count (incremented when tag is used)

---

## Photo Fixtures

**Directory**: `backend/tests/fixtures/photos/`

**Files**:

1. **sample_1.jpg** (800x600, 500KB)
   - Landscape orientation
   - Used for standard photo upload tests
   - Will be resized to 400x400 thumbnail

2. **sample_2.jpg** (600x800, 400KB)
   - Portrait orientation
   - Used for photo orientation tests
   - Will be resized to 400x400 thumbnail

3. **sample_large.jpg** (3000x2000, 5MB)
   - Large photo for upload limits testing
   - Tests photo size validation (max 5MB)
   - Tests resize/optimization workflow

**Usage in Tests**:

```python
@pytest.fixture
def photo_file():
    fixtures_path = Path(__file__).parent / "fixtures" / "photos" / "sample_1.jpg"
    with open(fixtures_path, "rb") as f:
        return f.read()

async def test_upload_trip_photo(client, published_trip, photo_file):
    response = await client.post(
        f"/trips/{published_trip.trip_id}/photos",
        files={"file": ("photo.jpg", photo_file, "image/jpeg")}
    )
    assert response.status_code == 200
```

---

## Fixture Generation Strategy

### UUID-Based Isolation

To prevent test conflicts during parallel execution, tests should generate unique IDs for users/trips:

```python
import uuid

@pytest.fixture
async def unique_user(db_session, user_fixtures):
    """Create user with unique UUID-based username/email"""
    admin_data = next(u for u in user_fixtures if u["fixture_id"] == "admin_user")
    unique_suffix = uuid.uuid4().hex[:8]

    user = await AuthService.register(db_session, {
        "email": f"admin_{unique_suffix}@test.com",
        "username": f"test_admin_{unique_suffix}",
        "password": admin_data["password_plain"],
    })

    return user
```

### Database Reset Between Tests

Each test should start with a clean database state:

```python
@pytest.fixture(scope="function")
async def db_session():
    """Create fresh in-memory SQLite DB per test"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback any uncommitted changes

    await engine.dispose()
```

---

## Fixture Maintenance

### Adding New Fixtures

1. Add fixture data to appropriate JSON file (users.json, trips.json, tags.json)
2. Assign unique `fixture_id` for easy reference
3. Update this documentation with field descriptions
4. Create pytest fixture helper in `conftest.py`
5. Use fixture in tests via dependency injection

### Updating Fixtures

1. Modify JSON file with new data
2. Run tests to ensure no regressions
3. Update documentation if fields change
4. Commit changes to version control

### Fixture Validation

Create meta-tests to validate fixture integrity:

```python
def test_user_fixtures_valid(user_fixtures):
    """Validate user fixtures schema"""
    for user in user_fixtures:
        assert "fixture_id" in user
        assert "email" in user
        assert "@" in user["email"]
        assert "username" in user
        assert "password_plain" in user
        assert user["role"] in ["USER", "ADMIN"]
```

---

## Summary

Test fixtures provide:

- **Consistency**: Same test data across all environments
- **Speed**: Fast test execution with in-memory SQLite
- **Isolation**: UUID-based IDs prevent parallel execution conflicts
- **Maintainability**: JSON format for easy updates without code changes
- **Documentation**: Self-documenting test scenarios via fixture names
