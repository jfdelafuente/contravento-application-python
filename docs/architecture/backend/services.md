# Service Layer - ContraVento Backend

Comprehensive documentation of the Service Layer pattern and implementation in ContraVento.

**Audience**: Backend developers, technical architects

---

## Table of Contents

- [Overview](#overview)
- [Service Layer Pattern](#service-layer-pattern)
- [Service Catalog](#service-catalog)
- [Service Structure](#service-structure)
- [Common Patterns](#common-patterns)
- [Transaction Management](#transaction-management)
- [Error Handling](#error-handling)
- [Testing Services](#testing-services)
- [Best Practices](#best-practices)
- [Anti-Patterns](#anti-patterns)

---

## Overview

The **Service Layer** encapsulates all business logic in ContraVento, sitting between the API layer (FastAPI routers) and the Data layer (SQLAlchemy models).

**Key Principle**: **"Fat services, thin controllers"**

- **API Routers**: Minimal logic, delegate to services
- **Services**: Rich business logic, orchestration, validation
- **Models**: Pure data structures, no business logic

### Why Service Layer?

**Benefits**:
- ✅ **Testability**: Business logic isolated from HTTP
- ✅ **Reusability**: Services can be called from multiple endpoints
- ✅ **Maintainability**: Single place for domain rules
- ✅ **Transaction Management**: Clear boundaries for DB transactions
- ✅ **Separation of Concerns**: API ≠ Business Logic

**Trade-offs**:
- ⚠️ More files and classes
- ⚠️ Requires discipline to keep routers thin

---

## Service Layer Pattern

### Architecture Position

```
┌─────────────────────────────────────────┐
│         API Layer (Routers)             │
│  - HTTP request/response                │
│  - Validation (Pydantic)                │
│  - Auth checks (dependencies)           │
│  - Call services                        │
└─────────────────────────────────────────┘
              ↓ calls
┌─────────────────────────────────────────┐
│       Service Layer (THIS LAYER)        │
│  - Business logic                       │
│  - Domain rules                         │
│  - Orchestration                        │
│  - Transaction management               │
└─────────────────────────────────────────┘
              ↓ uses
┌─────────────────────────────────────────┐
│         Data Layer (Models)             │
│  - ORM entities                         │
│  - Relationships                        │
│  - Constraints                          │
└─────────────────────────────────────────┘
```

### Responsibilities

**Services MUST**:
- Implement business rules
- Validate domain constraints
- Coordinate multiple models
- Manage transactions
- Calculate aggregations
- Trigger side effects (stats updates, emails)

**Services MUST NOT**:
- Handle HTTP concerns (status codes, headers)
- Parse request bodies (Pydantic does this)
- Return FastAPI Response objects
- Access request/response objects directly

---

## Service Catalog

ContraVento currently has **15 services**:

| Service | Purpose | Key Methods |
|---------|---------|-------------|
| **[AuthService](../../../backend/src/services/auth_service.py)** | Authentication & registration | register(), login(), refresh_token(), reset_password() |
| **[ProfileService](../../../backend/src/services/profile_service.py)** | User profile management | get_profile(), update_profile(), upload_photo() |
| **[StatsService](../../../backend/src/services/stats_service.py)** | User statistics calculation | update_stats(), award_achievement() |
| **[SocialService](../../../backend/src/services/social_service.py)** | Follow/unfollow logic | follow_user(), unfollow_user(), get_followers() |
| **[TripService](../../../backend/src/services/trip_service.py)** | Trip CRUD & publication | create_trip(), publish_trip(), upload_photo() |
| **[CommentService](../../../backend/src/services/comment_service.py)** | Comment CRUD | create_comment(), delete_comment() |
| **[LikeService](../../../backend/src/services/like_service.py)** | Like/unlike trips | like_trip(), unlike_trip() |
| **[FeedService](../../../backend/src/services/feed_service.py)** | Public feed queries | get_public_feed(), filter_by_tags() |
| **[GPXService](../../../backend/src/services/gpx_service.py)** | GPX file processing | parse_gpx(), simplify_route(), extract_metadata() |
| **[POIService](../../../backend/src/services/poi_service.py)** | Points of interest | create_poi(), get_trip_pois() |
| **[RouteStatsService](../../../backend/src/services/route_stats_service.py)** | Route statistics | calculate_elevation_gain(), calculate_gradients() |
| **[RouteStatisticsService](../../../backend/src/services/route_statistics_service.py)** | Legacy route stats | (deprecated, use RouteStatsService) |
| **[CyclingTypeService](../../../backend/src/services/cycling_type_service.py)** | Cycling type management | get_active_types(), create_type() |
| **[DifficultyCalculator](../../../backend/src/services/difficulty_calculator.py)** | Trip difficulty scoring | calculate_difficulty() |

---

## Service Structure

### Standard Service Template

```python
"""
<Service name> for <feature area>.

Business logic for <domain operations>.
Functional Requirements: FR-###, FR-###
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.<domain> import <Model>
from src.schemas.<domain> import <Schema>

logger = logging.getLogger(__name__)


class <ServiceName>:
    """
    <Service description>.

    Handles <domain operations>.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    async def <operation>(self, data: <Schema>) -> <Model>:
        """
        <Operation description>.

        Args:
            data: <Input description>

        Returns:
            <Output description>

        Raises:
            ValueError: If <validation fails>
            PermissionError: If <access denied>
        """
        # 1. Validate business rules
        # 2. Query database
        # 3. Apply logic
        # 4. Commit transaction
        # 5. Return result
        pass
```

### Example: TripService.create_trip()

```python
# src/services/trip_service.py
async def create_trip(self, user_id: str, data: TripCreateRequest) -> Trip:
    """
    Create a new trip.

    Creates trip with status=DRAFT, processes tags, locations, and sanitizes HTML.

    Args:
        user_id: ID of user creating the trip
        data: Trip creation request data

    Returns:
        Created Trip instance

    Raises:
        ValueError: If validation fails
    """
    # 1. Sanitize HTML content in description
    sanitized_description = sanitize_html(data.description)

    # 2. Map difficulty string to enum (if provided)
    difficulty_enum = TripDifficulty(data.difficulty) if data.difficulty else None

    # 3. Create trip entity
    trip = Trip(
        user_id=user_id,
        title=data.title,
        description=sanitized_description,
        status=TripStatus.DRAFT,  # Always start as DRAFT
        start_date=data.start_date,
        end_date=data.end_date,
        distance_km=data.distance_km,
        difficulty=difficulty_enum,
    )

    self.db.add(trip)
    await self.db.flush()  # Get trip_id before processing relationships

    # 4. Process tags (create new or link existing)
    if data.tags:
        await self._process_tags(trip, data.tags)

    # 5. Process locations
    if data.locations:
        await self._process_locations(trip, data.locations)

    # 6. Commit transaction
    await self.db.commit()
    await self.db.refresh(trip)

    # 7. Eager load relationships for response
    await self._load_trip_relationships(trip)

    logger.info(f"Created trip {trip.trip_id} for user {user_id}")
    return trip
```

---

## Common Patterns

### Pattern 1: Dependency Injection

Services receive database session via constructor (not global state).

```python
# ✅ GOOD - Dependency injection
class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

# API router injects dependency
@router.get("/{username}")
async def get_profile(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    service = ProfileService(db)
    return await service.get_profile(username)
```

**Benefits**:
- ✅ Testable (mock db in tests)
- ✅ Thread-safe (no global state)
- ✅ Explicit dependencies

---

### Pattern 2: Private Helper Methods

Complex operations split into private methods prefixed with `_`.

```python
class TripService:
    async def create_trip(self, user_id: str, data: TripCreateRequest) -> Trip:
        """Public method."""
        trip = Trip(...)
        self.db.add(trip)
        await self.db.flush()

        # Delegate to private helpers
        await self._process_tags(trip, data.tags)
        await self._process_locations(trip, data.locations)

        await self.db.commit()
        return trip

    async def _process_tags(self, trip: Trip, tag_names: list[str]):
        """Private helper: Process and normalize tags."""
        for tag_name in tag_names:
            normalized = tag_name.lower().strip()
            # Find or create tag...

    async def _process_locations(self, trip: Trip, locations: list[LocationInput]):
        """Private helper: Create trip locations."""
        for loc_data in locations:
            location = TripLocation(...)
            # Process location...
```

**Benefits**:
- ✅ Single Responsibility Principle
- ✅ Reusable logic
- ✅ Easier to test

---

### Pattern 3: Service Orchestration

Services can call other services to coordinate complex workflows.

```python
class TripService:
    async def publish_trip(self, trip_id: str, user_id: str) -> Trip:
        """
        Publish a draft trip.

        Coordinates:
        1. Trip validation
        2. Stats update (via StatsService)
        3. Achievement checking (via StatsService)
        """
        # 1. Get trip and validate ownership
        trip = await self.get_trip(trip_id, user_id)
        if trip.user_id != user_id:
            raise PermissionError("No tienes permiso para publicar este viaje")

        # 2. Validate publication requirements
        if len(trip.description) < 50:
            raise ValueError("La descripción debe tener al menos 50 caracteres")

        # 3. Update trip status
        trip.status = TripStatus.PUBLISHED
        trip.published_at = datetime.now(UTC)

        # 4. Coordinate with StatsService to update user stats
        stats_service = StatsService(self.db)
        await stats_service.update_stats_on_trip_publish(trip)

        await self.db.commit()
        return trip
```

**Benefits**:
- ✅ Clear boundaries between domains
- ✅ Services remain focused
- ✅ Reusable orchestration

---

### Pattern 4: Eager Loading

Services use `joinedload()` and `selectinload()` to prevent N+1 queries.

```python
# ✅ GOOD - Eager load relationships
async def get_trip(self, trip_id: str) -> Trip:
    result = await self.db.execute(
        select(Trip)
        .options(
            joinedload(Trip.user),           # 1:1
            joinedload(Trip.location),       # 1:1
            selectinload(Trip.photos),       # 1:N
            selectinload(Trip.tags)          # N:N
        )
        .where(Trip.trip_id == trip_id)
    )
    trip = result.unique().scalar_one_or_none()
    if not trip:
        raise ValueError(f"Viaje {trip_id} no encontrado")
    return trip

# ❌ BAD - N+1 queries
async def get_trip(self, trip_id: str) -> Trip:
    trip = await self.db.get(Trip, trip_id)  # 1 query
    # Accessing relationships triggers additional queries:
    photos = trip.photos  # +1 query
    tags = trip.tags      # +1 query
    # Total: 3 queries instead of 1
```

**Benefits**:
- ✅ Single database round-trip
- ✅ Predictable performance
- ✅ Meets p95 latency targets (<200ms)

---

### Pattern 5: Validation in Services

Services validate business rules, not just data types (Pydantic handles types).

```python
async def follow_user(self, follower_id: str, following_id: str):
    """
    Create follow relationship.

    Business rules:
    - Users must exist
    - Cannot follow yourself
    - Cannot follow same user twice
    """
    # 1. Validate both users exist
    follower = await self.db.get(User, follower_id)
    following = await self.db.get(User, following_id)

    if not follower or not following:
        raise ValueError("Usuario no encontrado")

    # 2. Validate business rule: Cannot follow yourself
    if follower_id == following_id:
        raise ValueError("No puedes seguirte a ti mismo")

    # 3. Validate business rule: Cannot follow twice
    existing = await self.db.execute(
        select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.following_id == following_id
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Ya sigues a este usuario")

    # 4. Create follow relationship
    follow = Follow(follower_id=follower_id, following_id=following_id)
    self.db.add(follow)

    # 5. Update denormalized counters (transactional)
    follower.following_count += 1
    following.followers_count += 1

    await self.db.commit()
```

**Benefits**:
- ✅ Domain rules enforced at business layer
- ✅ Consistent validation across endpoints
- ✅ Clear error messages in Spanish

---

## Transaction Management

### Pattern: Flush vs Commit

- **`flush()`**: Sync changes to DB, get IDs, but don't commit
- **`commit()`**: Persist transaction permanently

```python
async def create_trip(self, user_id: str, data: TripCreateRequest) -> Trip:
    # 1. Create trip
    trip = Trip(...)
    self.db.add(trip)
    await self.db.flush()  # ← Get trip_id without committing

    # 2. Use trip_id for related entities
    for tag_name in data.tags:
        tag = await self._find_or_create_tag(tag_name)
        trip_tag = TripTag(trip_id=trip.trip_id, tag_id=tag.tag_id)
        self.db.add(trip_tag)

    # 3. Commit entire transaction atomically
    await self.db.commit()

    return trip
```

**Why flush()?**
- Need to get auto-generated IDs (trip_id) before processing relationships
- Ensures data consistency (all-or-nothing commit)

---

### Pattern: Rollback on Error

FastAPI's dependency injection handles rollback automatically, but you can do it explicitly:

```python
async def complex_operation(self, data):
    try:
        # Step 1
        trip = Trip(...)
        self.db.add(trip)

        # Step 2
        stats = await self._update_stats(trip)

        # Step 3
        await self._send_notification(trip)

        # All steps succeeded → commit
        await self.db.commit()

    except Exception as e:
        # Any step failed → rollback
        await self.db.rollback()
        logger.error(f"Operation failed: {e}")
        raise
```

---

## Error Handling

### Standard Exceptions

Services raise domain exceptions (not HTTP exceptions):

```python
# ✅ GOOD - Domain exception
async def get_trip(self, trip_id: str) -> Trip:
    trip = await self.db.get(Trip, trip_id)
    if not trip:
        raise ValueError(f"Viaje {trip_id} no encontrado")
    return trip

# ❌ BAD - HTTP exception (belongs in router)
async def get_trip(self, trip_id: str) -> Trip:
    trip = await self.db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip
```

**Why?**
- Services should be HTTP-agnostic
- Routers handle HTTP status codes
- Services can be reused in non-HTTP contexts (CLI, background jobs)

### Exception Mapping (in Router)

```python
# API router translates service exceptions to HTTP
@router.get("/{trip_id}")
async def get_trip(trip_id: str, db: AsyncSession = Depends(get_db)):
    try:
        service = TripService(db)
        trip = await service.get_trip(trip_id)
        return {"success": True, "data": trip}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
```

---

## Testing Services

### Unit Testing Services

```python
# tests/unit/test_trip_service.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.trip_service import TripService
from src.schemas.trip import TripCreateRequest


@pytest.mark.asyncio
async def test_create_trip(db_session: AsyncSession, sample_user):
    """Test trip creation with draft status."""
    # Arrange
    service = TripService(db_session)
    data = TripCreateRequest(
        title="Ruta Test",
        description="Descripción de prueba con al menos 50 caracteres para validar",
        start_date="2024-06-01",
        end_date="2024-06-05",
        distance_km=120.5,
        tags=["test", "bikepacking"]
    )

    # Act
    trip = await service.create_trip(sample_user.id, data)

    # Assert
    assert trip.trip_id is not None
    assert trip.title == "Ruta Test"
    assert trip.status == TripStatus.DRAFT
    assert len(trip.tags) == 2
```

### Mocking Database

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_follow_user_already_following():
    """Test that following same user twice raises ValueError."""
    # Arrange
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: True))

    service = SocialService(mock_db)

    # Act & Assert
    with pytest.raises(ValueError, match="Ya sigues a este usuario"):
        await service.follow_user(follower_id="user1", following_id="user2")
```

---

## Best Practices

### 1. Single Responsibility

Each service focuses on one domain area:

```python
# ✅ GOOD - Focused services
class TripService:
    """Handles trips only."""
    async def create_trip(self, ...): ...
    async def publish_trip(self, ...): ...

class CommentService:
    """Handles comments only."""
    async def create_comment(self, ...): ...

# ❌ BAD - God service
class ContentService:
    """Handles trips, comments, likes, everything!"""
    async def create_trip(self, ...): ...
    async def create_comment(self, ...): ...
    async def like_trip(self, ...): ...
```

---

### 2. Async All the Way

All service methods are async (SQLAlchemy 2.0 async):

```python
# ✅ GOOD - Async method
async def get_trip(self, trip_id: str) -> Trip:
    result = await self.db.execute(select(Trip)...)
    return result.scalar_one_or_none()

# ❌ BAD - Sync method (blocks event loop)
def get_trip(self, trip_id: str) -> Trip:
    return self.db.query(Trip).filter_by(trip_id=trip_id).first()
```

---

### 3. Use Type Hints

All methods have complete type annotations:

```python
# ✅ GOOD - Full type hints
async def create_trip(
    self,
    user_id: str,
    data: TripCreateRequest
) -> Trip:
    ...

# ❌ BAD - Missing types
async def create_trip(self, user_id, data):
    ...
```

---

### 4. Document Business Rules

Link to functional requirements in docstrings:

```python
async def publish_trip(self, trip_id: str, user_id: str) -> Trip:
    """
    Publish a draft trip.

    Functional Requirements: FR-007 (Publish Trip)
    Success Criteria: SC-010 (Description ≥50 chars)

    Business Rules:
    - Only owner can publish
    - Description must be ≥50 characters
    - Status changes from DRAFT → PUBLISHED (irreversible)
    - UserStats updated automatically

    Args:
        trip_id: Trip identifier
        user_id: User attempting to publish

    Returns:
        Published Trip instance

    Raises:
        ValueError: If validation fails
        PermissionError: If not owner
    """
    ...
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Logic in Routers

```python
# ❌ BAD - Business logic in router
@router.post("/trips/{trip_id}/publish")
async def publish_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Don't do this! Logic belongs in service
    trip = await db.get(Trip, trip_id)
    if len(trip.description) < 50:
        raise HTTPException(400, "Description too short")
    trip.status = TripStatus.PUBLISHED
    await db.commit()
    return trip

# ✅ GOOD - Delegate to service
@router.post("/trips/{trip_id}/publish")
async def publish_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TripService(db)
    trip = await service.publish_trip(trip_id, current_user.id)
    return {"success": True, "data": trip}
```

---

### ❌ Anti-Pattern 2: Returning HTTP Responses

```python
# ❌ BAD - Service returns FastAPI Response
from fastapi.responses import JSONResponse

async def get_trip(self, trip_id: str) -> JSONResponse:
    trip = await self.db.get(Trip, trip_id)
    return JSONResponse({"success": True, "data": trip})

# ✅ GOOD - Service returns domain object
async def get_trip(self, trip_id: str) -> Trip:
    trip = await self.db.get(Trip, trip_id)
    if not trip:
        raise ValueError(f"Trip {trip_id} not found")
    return trip
```

---

### ❌ Anti-Pattern 3: Global Database Session

```python
# ❌ BAD - Global session
from src.database import SessionLocal

class TripService:
    async def create_trip(self, data):
        db = SessionLocal()  # Don't create session here!
        trip = Trip(...)
        db.add(trip)
        await db.commit()

# ✅ GOOD - Inject session via constructor
class TripService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trip(self, data):
        trip = Trip(...)
        self.db.add(trip)
        await self.db.commit()
```

---

## Related Documentation

- **[Backend Architecture](overview.md)** - Complete backend architecture guide
- **[Database Strategy](database.md)** - Dual DB approach (SQLite/PostgreSQL)
- **[Security](security.md)** - Security patterns and authentication
- **[Testing](../../testing/README.md)** - Testing services
- **[API Reference](../../api/README.md)** - API endpoints that use services

---

**Last Updated**: 2026-02-07
**Status**: ✅ Complete
**Coverage**: 15 services documented
