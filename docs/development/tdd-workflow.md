# TDD Workflow - Test-Driven Development

Complete guide to Test-Driven Development (TDD) process at ContraVento.

**Audience**: All developers

---

## Table of Contents

- [What is TDD](#what-is-tdd)
- [The TDD Cycle](#the-tdd-cycle)
- [Example Walkthrough](#example-walkthrough)
- [Testing Pyramid](#testing-pyramid)
- [Best Practices](#best-practices)
- [Common Mistakes](#common-mistakes)

---

## What is TDD

**Test-Driven Development (TDD)** is a software development process where you write tests **before** writing production code.

### Core Principles

1. **Test First**: Write failing test before implementation
2. **Minimal Code**: Write only enough code to pass the test
3. **Refactor**: Improve code while keeping tests passing
4. **High Coverage**: TDD naturally achieves ≥90% coverage

### Benefits

- ✅ **Design First**: Tests force you to think about API design
- ✅ **Catch Bugs Early**: Tests fail before bugs reach production
- ✅ **Regression Safety**: Changes don't break existing functionality
- ✅ **Documentation**: Tests document expected behavior
- ✅ **Confidence**: Refactor fearlessly with passing tests

### Why TDD at ContraVento

**Constitution Requirement**: TDD is mandatory (not optional)

> "Write tests FIRST before any implementation. Coverage requirement: ≥90% across all modules."
> — ContraVento Constitution, Section II: Testing

---

## The TDD Cycle

### Red-Green-Refactor

```
┌─────────────────────────────────────────────┐
│  🔴 RED: Write failing test                │
│  (Defines what the code should do)          │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  🟢 GREEN: Make test pass                  │
│  (Write minimal implementation)             │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│  🔵 REFACTOR: Improve code                 │
│  (Keep tests passing)                       │
└──────────────────┬──────────────────────────┘
                   ▼
               (Repeat)
```

### Detailed Steps

**🔴 RED - Write Failing Test**:
1. Write test for new feature/behavior
2. Run test → verify it fails
3. Failure confirms test is actually testing something

**🟢 GREEN - Make It Pass**:
1. Write **minimum** code to pass test
2. Don't worry about perfection yet
3. Run test → verify it passes

**🔵 REFACTOR - Improve Code**:
1. Clean up code (remove duplication, improve names)
2. Run tests after each change
3. Tests must stay green during refactoring

---

## Example Walkthrough

### Scenario: Add "Like Trip" Feature

We want users to like trips. Let's build it with TDD.

---

### Step 1: 🔴 RED - Write Failing Test

**File**: `tests/unit/test_like_service.py`

```python
import pytest
from src.services.like_service import LikeService
from src.models.like import Like

async def test_like_trip_creates_like_record(db_session):
    """Test that liking a trip creates a Like record."""
    # Arrange
    service = LikeService(db_session)
    user_id = "user123"
    trip_id = "trip456"

    # Act
    like = await service.like_trip(user_id=user_id, trip_id=trip_id)

    # Assert
    assert like.user_id == user_id
    assert like.trip_id == trip_id
    assert like.created_at is not None
```

**Run test**:
```bash
poetry run pytest tests/unit/test_like_service.py::test_like_trip_creates_like_record
```

**Expected Result**: ❌ **FAIL** (LikeService doesn't exist yet)

```
ImportError: cannot import name 'LikeService' from 'src.services'
```

**Why fail is good**: Confirms test is working. If it passed without code, the test wouldn't be testing anything!

---

### Step 2: 🟢 GREEN - Make Test Pass (Minimal)

**File**: `src/services/like_service.py`

```python
from datetime import UTC, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.like import Like

class LikeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def like_trip(self, user_id: str, trip_id: str) -> Like:
        """Like a trip."""
        like = Like(
            user_id=user_id,
            trip_id=trip_id,
            created_at=datetime.now(UTC),
        )
        self.db.add(like)
        await self.db.commit()
        await self.db.refresh(like)
        return like
```

**Run test again**:
```bash
poetry run pytest tests/unit/test_like_service.py::test_like_trip_creates_like_record
```

**Expected Result**: ✅ **PASS**

```
tests/unit/test_like_service.py::test_like_trip_creates_like_record PASSED [100%]
```

---

### Step 3: 🔴 RED - Add Constraint Test

**Add test for duplicate like** (user can't like twice):

```python
async def test_like_trip_twice_raises_error(db_session):
    """Test that liking a trip twice raises error."""
    # Arrange
    service = LikeService(db_session)
    user_id = "user123"
    trip_id = "trip456"

    # Act - First like succeeds
    await service.like_trip(user_id=user_id, trip_id=trip_id)

    # Act - Second like should fail
    with pytest.raises(ValueError, match="Ya has dado like a este viaje"):
        await service.like_trip(user_id=user_id, trip_id=trip_id)
```

**Run test**:
```bash
poetry run pytest tests/unit/test_like_service.py::test_like_trip_twice_raises_error
```

**Expected Result**: ❌ **FAIL** (no duplicate check yet)

```
AssertionError: ValueError not raised
```

---

### Step 4: 🟢 GREEN - Add Duplicate Check

**Update** `src/services/like_service.py`:

```python
from sqlalchemy import select

async def like_trip(self, user_id: str, trip_id: str) -> Like:
    """Like a trip."""
    # Check if already liked
    result = await self.db.execute(
        select(Like).where(
            Like.user_id == user_id,
            Like.trip_id == trip_id
        )
    )
    existing_like = result.scalar_one_or_none()

    if existing_like:
        raise ValueError("Ya has dado like a este viaje")

    # Create like
    like = Like(
        user_id=user_id,
        trip_id=trip_id,
        created_at=datetime.now(UTC),
    )
    self.db.add(like)
    await self.db.commit()
    await self.db.refresh(like)
    return like
```

**Run all tests**:
```bash
poetry run pytest tests/unit/test_like_service.py
```

**Expected Result**: ✅ **PASS** (both tests)

```
tests/unit/test_like_service.py::test_like_trip_creates_like_record PASSED
tests/unit/test_like_service.py::test_like_trip_twice_raises_error PASSED
```

---

### Step 5: 🔵 REFACTOR - Extract Duplicate Check

**Before** (inline check):
```python
async def like_trip(self, user_id: str, trip_id: str) -> Like:
    # Check if already liked (inline)
    result = await self.db.execute(...)
    existing_like = result.scalar_one_or_none()
    if existing_like:
        raise ValueError("Ya has dado like a este viaje")
    # ...
```

**After** (extracted method):
```python
async def _check_already_liked(self, user_id: str, trip_id: str) -> bool:
    """Check if user already liked trip."""
    result = await self.db.execute(
        select(Like).where(
            Like.user_id == user_id,
            Like.trip_id == trip_id
        )
    )
    return result.scalar_one_or_none() is not None

async def like_trip(self, user_id: str, trip_id: str) -> Like:
    """Like a trip."""
    if await self._check_already_liked(user_id, trip_id):
        raise ValueError("Ya has dado like a este viaje")

    like = Like(
        user_id=user_id,
        trip_id=trip_id,
        created_at=datetime.now(UTC),
    )
    self.db.add(like)
    await self.db.commit()
    await self.db.refresh(like)
    return like
```

**Run tests** (verify refactor didn't break anything):
```bash
poetry run pytest tests/unit/test_like_service.py
```

**Expected Result**: ✅ **PASS** (tests still pass after refactor)

---

### Step 6: Continue Cycle

Repeat for `unlike_trip`, `get_trip_likes`, etc.

**Next test**:
```python
async def test_unlike_trip_removes_like_record(db_session):
    """Test that unliking a trip removes the Like record."""
    # ... test implementation
```

---

## Testing Pyramid

ContraVento follows the Testing Pyramid strategy:

```
     ┌───────┐
     │  E2E  │  ← Few (Playwright) - Full user journeys
     ├───────┤
     │ Integ │  ← Some (pytest + FastAPI TestClient) - API endpoints
     ├───────┤
     │ Unit  │  ← Many (pytest + Vitest) - Service/util logic
     └───────┘
```

### Unit Tests (Many)

**Purpose**: Test individual functions/methods in isolation

**Characteristics**:
- Fast (<10ms per test)
- No external dependencies (mock database, APIs)
- Test single unit of code

**Example**:
```python
async def test_calculate_distance_between_points():
    """Test Haversine distance calculation."""
    # Arrange
    lat1, lon1 = 40.7128, -74.0060  # New York
    lat2, lon2 = 51.5074, -0.1278   # London

    # Act
    distance = haversine_distance(lat1, lon1, lat2, lon2)

    # Assert
    assert abs(distance - 5585.0) < 1.0  # ~5585 km
```

**When to write**: For all service methods, utilities, validators

---

### Integration Tests (Some)

**Purpose**: Test how components work together (API + Service + Database)

**Characteristics**:
- Moderate speed (~50-200ms per test)
- Real database (in-memory SQLite for tests)
- Test entire request-response cycle

**Example**:
```python
async def test_like_trip_api_endpoint(client, auth_headers):
    """Test POST /trips/{id}/like endpoint."""
    # Arrange
    trip_id = "trip123"

    # Act
    response = await client.post(
        f"/trips/{trip_id}/like",
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

**When to write**: For all API endpoints, complex service interactions

---

### E2E Tests (Few)

**Purpose**: Test full user journeys through UI

**Characteristics**:
- Slow (~2-10s per test)
- Real browser (Playwright)
- Test critical user paths

**Example**:
```typescript
test('user can like a trip', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="password"]', 'TestPass123!');
  await page.click('button[type="submit"]');

  // Navigate to trip
  await page.goto('/trips/trip123');

  // Click like button
  await page.click('button[aria-label="Like trip"]');

  // Verify like count increased
  await expect(page.locator('.like-count')).toContainText('1');
});
```

**When to write**: For critical user journeys (login, create trip, publish trip)

---

## Best Practices

### 1. Write Test First (Always)

```python
# ✅ GOOD - Test first
async def test_feature():
    result = await my_function()
    assert result == expected

# ❌ BAD - Code first, test later
async def my_function():
    return "result"
# (No test written - breaks TDD)
```

---

### 2. One Assertion Per Test (Preferred)

```python
# ✅ GOOD - Single assertion
async def test_like_creates_record():
    like = await service.like_trip(user_id, trip_id)
    assert like.user_id == user_id

async def test_like_has_timestamp():
    like = await service.like_trip(user_id, trip_id)
    assert like.created_at is not None

# ❌ ACCEPTABLE - Multiple related assertions
async def test_like_trip():
    like = await service.like_trip(user_id, trip_id)
    assert like.user_id == user_id
    assert like.trip_id == trip_id
    assert like.created_at is not None
    # OK if testing same concept
```

---

### 3. Descriptive Test Names

```python
# ✅ GOOD - Describes behavior
async def test_like_trip_twice_raises_value_error()

# ❌ BAD - Vague
async def test_like()
async def test_error()
```

**Pattern**: `test_<method>_<condition>_<expected_result>`

---

### 4. Arrange-Act-Assert (AAA) Pattern

```python
async def test_like_trip_creates_like_record():
    # Arrange - Setup test data
    service = LikeService(db_session)
    user_id = "user123"
    trip_id = "trip456"

    # Act - Execute the code under test
    like = await service.like_trip(user_id, trip_id)

    # Assert - Verify results
    assert like.user_id == user_id
    assert like.trip_id == trip_id
```

---

### 5. Test Edge Cases

```python
# Test normal case
async def test_like_trip_success()

# Test error cases
async def test_like_trip_with_invalid_user_id()
async def test_like_trip_with_invalid_trip_id()
async def test_like_trip_twice_raises_error()
async def test_like_trip_with_deleted_trip()
```

---

### 6. Use Fixtures for Common Setup

```python
# conftest.py
@pytest.fixture
async def like_service(db_session):
    return LikeService(db_session)

@pytest.fixture
async def sample_trip(db_session):
    trip = Trip(title="Test Trip", ...)
    db_session.add(trip)
    await db_session.commit()
    return trip

# test_like_service.py
async def test_like_trip(like_service, sample_trip):
    like = await like_service.like_trip(user_id, sample_trip.trip_id)
    assert like.trip_id == sample_trip.trip_id
```

---

## Common Mistakes

### Mistake 1: Writing Code Before Test

```python
# ❌ WRONG - Wrote function first
def calculate_total(items):
    return sum(item.price for item in items)

# Then wrote test
def test_calculate_total():
    assert calculate_total([...]) == 100
```

**Why wrong**: Misses design thinking phase. Test should drive design.

**Fix**: Delete function, write test first, re-implement.

---

### Mistake 2: Testing Implementation (Not Behavior)

```python
# ❌ BAD - Testing internal implementation
async def test_like_trip_calls_db_add():
    service = LikeService(db_session)
    await service.like_trip(user_id, trip_id)

    # Checking internal method call
    assert db_session.add.called

# ✅ GOOD - Testing behavior
async def test_like_trip_creates_like_record():
    service = LikeService(db_session)
    like = await service.like_trip(user_id, trip_id)

    # Checking output/result
    assert like.user_id == user_id
```

---

### Mistake 3: Tests Depend on Each Other

```python
# ❌ BAD - Tests depend on order
async def test_create_like():
    global like_id
    like = await service.like_trip(user_id, trip_id)
    like_id = like.id  # Store for next test

async def test_unlike_trip():
    await service.unlike_trip(user_id, like_id)  # Uses global
```

**Why wrong**: If `test_create_like` fails, `test_unlike_trip` also fails.

**Fix**: Each test creates own data:
```python
# ✅ GOOD - Independent tests
async def test_unlike_trip():
    # Setup (independent)
    like = await service.like_trip(user_id, trip_id)

    # Test unlike
    await service.unlike_trip(user_id, like.id)
```

---

### Mistake 4: Skipping Refactor Step

```python
# 🟢 GREEN - Test passes
async def like_trip(self, user_id, trip_id):
    result = await self.db.execute(select(Like).where(Like.user_id == user_id, Like.trip_id == trip_id))
    existing = result.scalar_one_or_none()
    if existing: raise ValueError("Already liked")
    like = Like(user_id=user_id, trip_id=trip_id)
    self.db.add(like)
    await self.db.commit()
    return like

# Developer: "It works!" ❌ SKIPS REFACTOR
```

**Why wrong**: Code gets messy over time.

**Fix**: Refactor after green:
```python
# 🔵 REFACTOR - Extract method
async def _check_already_liked(self, user_id, trip_id):
    result = await self.db.execute(...)
    return result.scalar_one_or_none() is not None

async def like_trip(self, user_id, trip_id):
    if await self._check_already_liked(user_id, trip_id):
        raise ValueError("Already liked")

    like = Like(user_id=user_id, trip_id=trip_id)
    self.db.add(like)
    await self.db.commit()
    return like
```

---

## Coverage Requirements

**ContraVento Standard**: ≥90% coverage for all modules

**Check coverage**:
```bash
poetry run pytest --cov=src --cov-report=html --cov-fail-under=90
```

**View detailed report**:
```bash
open htmlcov/index.html
```

**Uncovered lines**: Write tests for them!

---

## Related Documentation

- **[Getting Started](getting-started.md)** - Developer onboarding
- **[Code Quality](code-quality.md)** - Linting, formatting, type checking
- **[Testing Strategies](../testing/README.md)** - Complete testing guide
- **[Backend Architecture](../architecture/backend/overview.md)** - Service Layer patterns

---

**Last Updated**: 2026-02-07
**Coverage Requirement**: ≥90%
**Process**: Red-Green-Refactor (mandatory)
