# Quick Start Guide: Travel Diary Feature

**Feature**: 002-travel-diary
**For**: Developers implementing the Travel Diary functionality
**Last Updated**: 2025-12-24

## Overview

This guide provides a step-by-step walkthrough for implementing and testing the Travel Diary feature. Follow this guide to understand the complete development workflow from database setup to API testing.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Completed 001-user-profiles feature (authentication system)
- ✅ Python 3.11+ installed
- ✅ Poetry dependency manager
- ✅ PostgreSQL 15+ (production) or SQLite 3.40+ (development)
- ✅ Git repository cloned and on branch `002-travel-diary`

---

## Phase 1: Environment Setup

### 1.1 Install New Dependencies

```bash
cd backend

# Add new dependencies
poetry add Pillow==10.1.0
poetry add bleach==6.1.0

# Verify installation
poetry show | grep -E "(Pillow|bleach)"
```

### 1.2 Update Environment Variables

Add to `.env` file:

```bash
# Travel Diary Configuration
UPLOAD_MAX_SIZE_MB=10
MAX_PHOTOS_PER_TRIP=20
MAX_TAGS_PER_TRIP=10
PHOTO_QUALITY_OPTIMIZED=85
PHOTO_QUALITY_THUMB=80
PHOTO_MAX_WIDTH=1200
PHOTO_THUMB_SIZE=200

# Storage paths
STORAGE_ROOT=./storage
TRIP_PHOTOS_PATH=trip_photos
```

### 1.3 Create Storage Directory

```bash
cd backend
mkdir -p storage/trip_photos
chmod 755 storage
```

---

## Phase 2: Database Migration

### 2.1 Create Migration

```bash
# Auto-generate migration from models
poetry run alembic revision --autogenerate -m "add_travel_diary_tables"

# Review generated migration file
ls -lt src/migrations/versions/ | head -5
```

### 2.2 Review Migration

Open the generated migration file and verify:

- ✅ Creates `trips` table with all columns
- ✅ Creates `trip_photos` table
- ✅ Creates `tags` table with unique normalized column
- ✅ Creates `trip_tags` join table
- ✅ Creates `trip_locations` table
- ✅ Creates all indexes
- ✅ Creates triggers (PostgreSQL) for updated_at and published_at
- ✅ Includes downgrade() function

### 2.3 Apply Migration

```bash
# Apply migration
poetry run alembic upgrade head

# Verify tables created
poetry run python -c "
from src.database import AsyncSessionLocal, engine
from src.models.trip import Trip
import asyncio

async def check():
    async with engine.begin() as conn:
        result = await conn.run_sync(lambda sync_conn: sync_conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'))
        print('Tables:', [row[0] for row in result])

asyncio.run(check())
"
```

Expected output:
```
Tables: ['users', 'user_profiles', 'user_stats', 'achievements', 'user_achievements', 'follows', 'trips', 'trip_photos', 'tags', 'trip_tags', 'trip_locations']
```

---

## Phase 3: Implementation Checklist

Implement components in this order (TDD - write tests first!):

### 3.1 Core Models

**File**: `backend/src/models/trip.py`

- [ ] Create `Trip` model with all fields
- [ ] Create `TripPhoto` model
- [ ] Create `Tag` model with normalized field
- [ ] Create `TripTag` join model
- [ ] Create `TripLocation` model
- [ ] Define relationships between models
- [ ] Add `to_dict()` methods for JSON serialization

**Test**: `backend/tests/unit/test_trip_model.py`

```python
async def test_create_trip(db_session):
    """Test creating a trip with required fields."""
    trip = Trip(
        id=str(uuid.uuid4()),
        user_id=test_user_id,
        title="Test Trip",
        description="<p>Description</p>",
        start_date=date.today(),
        status=TripStatus.DRAFT
    )
    db_session.add(trip)
    await db_session.commit()
    assert trip.id is not None
```

### 3.2 Utilities

#### HTML Sanitizer

**File**: `backend/src/utils/html_sanitizer.py`

- [ ] Implement `sanitize_html()` function using Bleach
- [ ] Configure allowed tags whitelist
- [ ] Configure allowed attributes
- [ ] Add length validation (max 50,000 chars)

**Test**: `backend/tests/unit/test_html_sanitizer.py`

```python
def test_sanitize_removes_script_tags():
    """Test XSS prevention."""
    dirty = '<p>Hello</p><script>alert("XSS")</script>'
    clean = sanitize_html(dirty)
    assert '<script>' not in clean
    assert '<p>Hello</p>' in clean
```

#### Photo Processor

**File**: `backend/src/utils/photo_processor.py`

- [ ] Implement `create_optimized()` - resize to max width
- [ ] Implement `create_thumbnail()` - 200x200 center crop
- [ ] Handle EXIF orientation correction
- [ ] Return metadata (width, height, file_size)

**Test**: `backend/tests/unit/test_photo_processor.py`

```python
async def test_create_optimized_reduces_size():
    """Test photo optimization."""
    input_path = Path("tests/fixtures/sample_photo.jpg")
    output_path = tmp_path / "optimized.jpg"

    metadata = await create_optimized(input_path, output_path, max_width=1200)

    assert output_path.exists()
    assert metadata["width"] <= 1200
    assert output_path.stat().st_size < input_path.stat().st_size
```

#### File Storage

**File**: `backend/src/utils/file_storage.py`

- [ ] Implement `save_photo()` - save to filesystem
- [ ] Implement `delete_photo()` - remove from filesystem
- [ ] Implement `generate_photo_path()` - year/month/trip_id structure
- [ ] Handle directory creation

**Test**: `backend/tests/unit/test_file_storage.py`

```python
async def test_save_photo_creates_directory_structure():
    """Test file storage creates correct path."""
    trip_id = "test-trip-123"
    file_data = b"fake image data"

    path = await save_photo(trip_id, file_data, "photo.jpg")

    assert f"{date.today().year}" in str(path)
    assert f"{date.today().month:02d}" in str(path)
    assert trip_id in str(path)
```

### 3.3 Schemas

**File**: `backend/src/schemas/trip.py`

- [ ] `TripCreateRequest` - validation for trip creation
- [ ] `TripUpdateRequest` - partial update schema
- [ ] `TripResponse` - serialized trip data
- [ ] `PhotoUploadRequest` - photo upload validation
- [ ] `LocationInput` - location data validation
- [ ] Field validators (date ranges, distance limits, etc.)

**Test**: `backend/tests/unit/test_trip_schemas.py`

```python
def test_trip_create_validates_date_range():
    """Test that end_date must be >= start_date."""
    with pytest.raises(ValidationError):
        TripCreateRequest(
            title="Trip",
            description="Desc" * 20,
            start_date=date(2024, 5, 15),
            end_date=date(2024, 5, 10)  # Before start_date!
        )
```

### 3.4 Service Layer

**File**: `backend/src/services/trip_service.py`

Implement methods in TDD order (test first!):

- [ ] `create_trip()` - Create new trip, sanitize HTML, process tags
- [ ] `get_trip()` - Fetch with eager loading (photos, tags, locations)
- [ ] `update_trip()` - Partial update with optimistic locking
- [ ] `delete_trip()` - Cascade delete, update user stats
- [ ] `publish_trip()` - Validate and change status
- [ ] `get_user_trips()` - Paginated list with filters
- [ ] `upload_photo()` - Validate, save, process in background
- [ ] `delete_photo()` - Remove from DB and filesystem
- [ ] `reorder_photos()` - Update photo order

**Test**: `backend/tests/unit/test_trip_service.py`

```python
async def test_create_trip_sanitizes_html(db_session):
    """Test HTML sanitization on trip creation."""
    service = TripService(db_session)
    data = TripCreateRequest(
        title="Trip",
        description='<p>Hello</p><script>alert("XSS")</script>',
        start_date=date.today()
    )

    trip = await service.create_trip(user_id="test-user", data=data)

    assert '<script>' not in trip.description
    assert '<p>Hello</p>' in trip.description
```

### 3.5 API Endpoints

**File**: `backend/src/api/trips.py`

- [ ] `POST /trips` - Create trip
- [ ] `GET /trips/{id}` - Get trip detail
- [ ] `PUT /trips/{id}` - Update trip
- [ ] `DELETE /trips/{id}` - Delete trip
- [ ] `POST /trips/{id}/publish` - Publish trip
- [ ] `POST /trips/{id}/photos` - Upload photo
- [ ] `DELETE /trips/{id}/photos/{photo_id}` - Delete photo
- [ ] `PUT /trips/{id}/photos/reorder` - Reorder photos
- [ ] `GET /users/{username}/trips` - List user trips
- [ ] `GET /tags` - List all tags

**Test**: `backend/tests/integration/test_trips_api.py`

```python
async def test_create_trip_returns_201(client, auth_headers):
    """Test trip creation endpoint."""
    response = await client.post(
        "/trips",
        json={
            "title": "Test Trip",
            "description": "<p>Description</p>",
            "start_date": "2024-05-15"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Test Trip"
    assert data["data"]["status"] == "draft"
```

### 3.6 Register Routes

**File**: `backend/src/main.py`

```python
from src.api import trips

app.include_router(trips.router, prefix="/api")
app.include_router(trips.achievements_router, prefix="/api")
```

---

## Phase 4: Manual Testing

### 4.1 Start Development Server

```bash
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.2 Create Test User

```bash
poetry run python scripts/create_verified_user.py \
  --username cyclist1 \
  --email cyclist1@example.com \
  --password "CyclePass123!"
```

### 4.3 Get Auth Token

```bash
# Login to get JWT token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "cyclist1",
    "password": "CyclePass123!"
  }'

# Save the access_token from response
export TOKEN="<your_access_token_here>"
```

### 4.4 Test Trip Creation

```bash
# Create a trip
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Vía Verde del Aceite",
    "description": "<p>Espectacular ruta entre <b>Jaén</b> y <b>Córdoba</b> siguiendo antiguas vías de tren.</p><ul><li>Paisajes de olivos</li><li>Pueblos con encanto</li></ul>",
    "start_date": "2024-05-15",
    "end_date": "2024-05-17",
    "distance_km": 127.3,
    "difficulty": "moderate",
    "locations": [
      {"name": "Jaén", "country": "España"},
      {"name": "Baeza", "country": "España"},
      {"name": "Córdoba", "country": "España"}
    ],
    "tags": ["vías verdes", "andalucía", "olivos"]
  }'

# Save trip_id from response
export TRIP_ID="<trip_id_from_response>"
```

### 4.5 Test Photo Upload

```bash
# Upload a photo
curl -X POST http://localhost:8000/trips/$TRIP_ID/photos \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@/path/to/your/photo.jpg"

# Check photo was created
ls -lah backend/storage/trip_photos/$(date +%Y)/$(date +%m)/$TRIP_ID/
```

### 4.6 Test Trip Publishing

```bash
# Publish the trip
curl -X POST http://localhost:8000/trips/$TRIP_ID/publish \
  -H "Authorization: Bearer $TOKEN"

# Verify it's visible in user's public profile
curl http://localhost:8000/users/cyclist1/trips
```

### 4.7 Test Filtering by Tag

```bash
# Get trips with specific tag
curl "http://localhost:8000/users/cyclist1/trips?tag=vías%20verdes"
```

---

## Phase 5: Automated Testing

### 5.1 Run All Tests

```bash
cd backend

# Run unit tests
poetry run pytest tests/unit/ -v

# Run integration tests
poetry run pytest tests/integration/ -v

# Run contract tests
poetry run pytest tests/contract/ -v

# Run all tests with coverage
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Check coverage meets ≥90% requirement
poetry run coverage report
```

### 5.2 Code Quality Checks

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/

# All checks must pass before committing
```

---

## Phase 6: API Documentation

### 6.1 View Interactive Docs

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 6.2 Verify OpenAPI Contract

```bash
# Export OpenAPI spec
curl http://localhost:8000/openapi.json > openapi-actual.json

# Compare with contract
# Should match specs/002-travel-diary/contracts/trips-api.yaml
```

---

## Common Issues & Solutions

### Issue: Photo Upload Fails with 413 (Payload Too Large)

**Solution**: Increase Uvicorn max body size:
```bash
poetry run uvicorn src.main:app --reload --limit-max-form-memory-size 20000000
```

### Issue: Migration Fails - Table Already Exists

**Solution**: Rollback and re-apply:
```bash
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

### Issue: Photos Not Processing

**Solution**: Check background task logs:
```python
# Add logging to photo_processor.py
logger.info(f"Processing photo: {photo_path}")
```

### Issue: HTML Sanitization Too Strict

**Solution**: Check allowed tags in `html_sanitizer.py`:
```python
ALLOWED_TAGS = ['p', 'br', 'b', 'strong', 'i', 'em', 'ul', 'ol', 'li', 'a']
# Add more if needed, but carefully!
```

### Issue: Tags Not Case-Insensitive

**Solution**: Verify normalized column is being used:
```sql
-- In SQLite/PostgreSQL
SELECT * FROM tags WHERE normalized = 'bikepacking';
-- Should match 'Bikepacking', 'BIKEPACKING', etc.
```

---

## Performance Testing

### Load Test with Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class TripUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/auth/login", json={
            "login": "cyclist1",
            "password": "CyclePass123!"
        })
        self.token = response.json()["data"]["access_token"]

    @task(10)
    def list_trips(self):
        self.client.get("/users/cyclist1/trips")

    @task(5)
    def get_trip_detail(self):
        self.client.get(f"/trips/{self.trip_id}")

    @task(1)
    def create_trip(self):
        self.client.post("/trips", json={
            "title": "Load Test Trip",
            "description": "<p>Test</p>" * 20,
            "start_date": "2024-05-15"
        }, headers={"Authorization": f"Bearer {self.token}"})
```

Run load test:
```bash
poetry run locust -f locustfile.py --headless -u 50 -r 5 -t 60s
```

**Target**: SC-021 - 50 concurrent users without degradation

---

## Next Steps

After completing this quickstart:

1. ✅ Run `/speckit.tasks` to generate detailed implementation tasks
2. ✅ Implement Phase 1 (Create/Publish trips) completely before moving to Phase 2
3. ✅ Get code review after each major component
4. ✅ Update CLAUDE.md with new features and commands
5. ✅ Create pull request when feature is complete

---

## Reference Links

- **Spec**: [spec.md](./spec.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Research**: [research.md](./research.md)
- **API Contract**: [contracts/trips-api.yaml](./contracts/trips-api.yaml)
- **Constitution**: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

**Version**: 1.0
**Last Updated**: 2025-12-24
**Status**: ✅ Ready for Development
