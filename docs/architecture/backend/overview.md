# Backend Architecture - ContraVento

Complete backend architecture documentation for the ContraVento cycling social platform.

**Audience**: Backend developers, technical architects, senior engineers

---

## Table of Contents

- [System Overview](#system-overview)
- [Layered Architecture](#layered-architecture)
- [Data Flow](#data-flow)
- [Module Architecture](#module-architecture)
- [Design Patterns](#design-patterns)
- [Database Schema](#database-schema)
- [Travel Diary Architecture](#travel-diary-architecture)
- [Authentication & Authorization](#authentication--authorization)
- [Performance Optimizations](#performance-optimizations)
- [Security](#security)
- [Testing Strategy](#testing-strategy)
- [File Organization](#file-organization)
- [Key Principles](#key-principles)
- [Future Enhancements](#future-enhancements)

---

## System Overview

ContraVento es una plataforma social de cicloturismo con una arquitectura de 3 capas que sigue principios de **Clean Architecture** y **Domain-Driven Design**.

**Technology Stack**:
- **Framework**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: SQLite (dev/test), PostgreSQL 16 (production)
- **Authentication**: JWT tokens (access + refresh)
- **File Storage**: Local filesystem (future: S3)

**Core Principles**:
1. Separation of Concerns
2. Dependency Injection
3. Type Safety
4. Security First
5. Performance
6. Testability
7. Maintainability

---

## Layered Architecture

The backend follows a strict 3-layer architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        API Layer                                         │
│  (FastAPI Routers - HTTP Interface)                                     │
│                                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │  auth.py │ │profile.py│ │ stats.py │ │social.py │ │ trips.py │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│       ↓             ↓            ↓            ↓            ↓             │
└─────────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      Service Layer                                       │
│  (Business Logic & Domain Rules)                                        │
│                                                                          │
│  ┌──────────────┐ ┌───────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │AuthService   │ │ProfileService │ │StatsService  │ │ TripService │ │
│  └──────────────┘ └───────────────┘ └──────────────┘ └─────────────┘ │
│  ┌──────────────┐                                                      │
│  │SocialService │                                                      │
│  └──────────────┘                                                      │
│       ↓                   ↓                ↓               ↓            │
└─────────────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       Data Layer                                         │
│  (ORM Models & Database Access)                                         │
│                                                                          │
│  ┌──────┐ ┌───────────┐ ┌──────┐ ┌──────────┐ ┌────────┐ ┌────────┐  │
│  │ User │ │UserProfile│ │Stats │ │Achievement│ │ Follow │ │  Trip  │  │
│  └──────┘ └───────────┘ └──────┘ └──────────┘ └────────┘ └────────┘  │
│                                                            ┌──────────┐  │
│                                                            │TripPhoto │  │
│                                                            └──────────┘  │
│                                                            ┌──────────┐  │
│                                                            │   Tag    │  │
│                                                            └──────────┘  │
│       ↓          ↓           ↓         ↓           ↓           ↓         │
└─────────────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌────────────────┐
                    │   PostgreSQL   │
                    │   / SQLite     │
                    └────────────────┘
```

**Critical Rule**: Layers can only call downward. APIs call Services, Services use Models. Never skip layers.

---

## Data Flow

### Request Flow (Example: Get User Profile)

```
1. HTTP Request
   GET /users/johndoe
   ↓
2. API Router (profile.py)
   @router.get("/{username}")
   async def get_user_profile(...)
   ↓
3. Service Layer (ProfileService)
   await profile_service.get_profile(username)
   - Business logic
   - Privacy rules
   - Data aggregation
   ↓
4. ORM Layer (SQLAlchemy)
   select(User).options(
       joinedload(User.profile),
       joinedload(User.stats)
   )
   ↓
5. Database (PostgreSQL/SQLite)
   SELECT users.*, user_profiles.*, user_stats.*
   FROM users
   LEFT JOIN user_profiles ...
   ↓
6. Response (Pydantic Schema)
   ProfileResponse(
       username="johndoe",
       stats=ProfileStatsPreview(...)
   )
   ↓
7. HTTP Response (JSON)
   {
     "success": true,
     "data": { ... }
   }
```

---

## Module Architecture

### API Layer (`src/api/`)

**Purpose**: HTTP interface, request/response handling

**Responsibilities**:
- Define HTTP endpoints
- Validate request data (Pydantic)
- Handle authentication/authorization (via dependencies)
- Call appropriate service methods
- Format responses
- Error handling (HTTP status codes)

**Files**:
- [src/api/auth.py](../../../backend/src/api/auth.py) - Registration, login, verification
- [src/api/profile.py](../../../backend/src/api/profile.py) - Profile CRUD, photo upload
- [src/api/stats.py](../../../backend/src/api/stats.py) - User statistics and achievements
- [src/api/social.py](../../../backend/src/api/social.py) - Follow/unfollow, followers/following lists
- [src/api/trips.py](../../../backend/src/api/trips.py) - Trip CRUD, photos, tags, draft/publish workflow
- [src/api/deps.py](../../../backend/src/api/deps.py) - Shared dependencies (auth, DB session)

**Key Pattern**: Thin controllers - minimal logic, delegate to services

---

### Service Layer (`src/services/`)

**Purpose**: Business logic and domain rules

**Responsibilities**:
- Implement business rules
- Validate domain constraints
- Coordinate between multiple models
- Transaction management
- Complex queries and aggregations
- Event-driven updates (e.g., stats on trip publish)

**Files**:
- [src/services/auth_service.py](../../../backend/src/services/auth_service.py) - Authentication logic, password reset
- [src/services/profile_service.py](../../../backend/src/services/profile_service.py) - Profile management, privacy rules
- [src/services/stats_service.py](../../../backend/src/services/stats_service.py) - Stats calculation, achievement awarding
- [src/services/social_service.py](../../../backend/src/services/social_service.py) - Follow logic, counter management
- [src/services/trip_service.py](../../../backend/src/services/trip_service.py) - Trip management, draft workflow, tag normalization, photo handling

**Key Pattern**: Rich domain services - all business logic lives here

---

### Data Layer (`src/models/`)

**Purpose**: Data persistence and ORM mapping

**Responsibilities**:
- Define database schema
- Relationships between entities
- Constraints and indexes
- Database migrations (Alembic)

**Files**:
- [src/models/user.py](../../../backend/src/models/user.py) - User, UserProfile models
- [src/models/auth.py](../../../backend/src/models/auth.py) - PasswordReset model
- [src/models/stats.py](../../../backend/src/models/stats.py) - UserStats, Achievement, UserAchievement models
- [src/models/social.py](../../../backend/src/models/social.py) - Follow model
- [src/models/trip.py](../../../backend/src/models/trip.py) - Trip, TripPhoto, TripLocation, Tag, trip_tags (association table) models

**Key Pattern**: Anemic models - minimal logic, pure data structures

---

### Schemas Layer (`src/schemas/`)

**Purpose**: Request/response validation and serialization

**Responsibilities**:
- Validate incoming data
- Serialize outgoing data
- Type safety
- API contract definition

**Files**:
- [src/schemas/auth.py](../../../backend/src/schemas/auth.py) - Login, registration, token schemas
- [src/schemas/profile.py](../../../backend/src/schemas/profile.py) - Profile update, response schemas
- [src/schemas/stats.py](../../../backend/src/schemas/stats.py) - Stats and achievement schemas
- [src/schemas/social.py](../../../backend/src/schemas/social.py) - Follow, followers, following schemas
- [src/schemas/trip.py](../../../backend/src/schemas/trip.py) - Trip create/update, photo upload, tag schemas, TripStatus enum
- [src/schemas/api_response.py](../../../backend/src/schemas/api_response.py) - Standard response envelope

**Key Pattern**: DTO (Data Transfer Objects) for API boundary

---

### Utils Layer (`src/utils/`)

**Purpose**: Reusable utilities and helpers

**Files**:
- [src/utils/security.py](../../../backend/src/utils/security.py) - Password hashing, JWT creation/validation
- [src/utils/file_storage.py](../../../backend/src/utils/file_storage.py) - Photo validation, resize, storage
- [src/utils/auth.py](../../../backend/src/utils/auth.py) - get_current_user dependency

---

## Design Patterns

### Dependency Injection

```python
# Service receives DB session via constructor
class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

# Injected via FastAPI dependency
@router.get("/{username}")
async def get_profile(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    service = ProfileService(db)
    return await service.get_profile(username)
```

**Benefits**:
- Easier testing (mock dependencies)
- Loose coupling
- Explicit dependencies
- Thread-safe (no global state)

---

### Repository Pattern

All database access goes through SQLAlchemy ORM - no raw SQL.

```python
# ✅ GOOD - Using ORM
result = await db.execute(
    select(User).where(User.username == username)
)
user = result.scalar_one_or_none()

# ❌ BAD - Raw SQL (not used in this project)
result = await db.execute("SELECT * FROM users WHERE username = ?", username)
```

**Benefits**:
- SQL injection protection
- Database portability (SQLite ↔ PostgreSQL)
- Type safety
- Query builder API

---

### Service Layer Pattern

Business logic centralized in services, not in routers or models.

```python
# Router (thin):
@router.post("/{username}/follow")
async def follow_user(username: str, current_user: User, db: AsyncSession):
    service = SocialService(db)
    return await service.follow_user(current_user.username, username)

# Service (thick):
async def follow_user(self, follower_username: str, following_username: str):
    # 1. Validate users exist
    # 2. Check not self-follow
    # 3. Check not already following
    # 4. Create Follow relationship
    # 5. Update denormalized counters (transactional)
    # 6. Return response
```

**Benefits**:
- Testable business logic
- Reusable across endpoints
- Clear separation of concerns
- Transaction management

---

### Eager Loading for Performance

```python
# Load related data in single query
result = await db.execute(
    select(User)
    .options(
        joinedload(User.profile),
        joinedload(User.stats)
    )
    .where(User.username == username)
)
```

**Benefits**:
- Prevents N+1 queries
- Single database round-trip
- Reduced latency (<200ms target)

---

## Database Schema

### Entity Relationships

```
User (1) ──── (1) UserProfile
  │
  ├─── (1) UserStats
  │
  ├─── (N) UserAchievement ──── (1) Achievement
  │
  ├─── (N) PasswordReset
  │
  ├─── (N) Follow (as follower)
  │
  ├─── (N) Follow (as following)
  │
  └─── (N) Trip
         │
         ├─── (N) TripPhoto
         │
         ├─── (0..1) TripLocation
         │
         └─── (N) trip_tags ──── (N) Tag (many-to-many)
```

**Trip Domain Relationships**:

- Each **User** can have many **Trips** (1:N)
- Each **Trip** can have up to 20 **TripPhotos** (1:N, max 20)
- Each **Trip** can have one optional **TripLocation** (1:0..1)
- **Trips** and **Tags** have a many-to-many relationship via **trip_tags** table
- **Tags** are normalized (lowercase) for case-insensitive matching
- **Trip status**: DRAFT (owner-only) or PUBLISHED (public)

### Key Constraints

**Unique constraints**:
- User: username, email
- Follow: (follower_id, following_id)
- Tag: normalized (case-insensitive uniqueness)
- trip_tags: (trip_id, tag_id)

**Foreign keys**: All with CASCADE delete

**Check constraints**:
- Follow: follower_id != following_id (prevent self-follow)
- Trip: start_date <= end_date
- TripPhoto: order >= 0

**Indexes**:
- User: username, email
- Trip: user_id, status, created_at
- TripPhoto: trip_id, order
- Tag: normalized, usage_count (for popular tags)
- Foreign keys (auto-indexed)

---

## Travel Diary Architecture

See [specs/002-travel-diary](../../../specs/002-travel-diary/) for complete feature specification.

### Draft Workflow System

Travel Diary implements a **draft-to-published workflow** for content creation:

```
┌─────────────────────────────────────────────────────────┐
│                  Trip Creation Flow                      │
└─────────────────────────────────────────────────────────┘

1. CREATE TRIP (Default: DRAFT)
   POST /trips
   ↓
   - Minimal validation (title + description required)
   - No stats update
   - Owner-only visibility
   - Can attach photos, tags, location

2. DRAFT STATE
   ↓
   - Edit freely (PUT /trips/{trip_id})
   - Upload photos (POST /trips/{trip_id}/photos)
   - Add/remove tags
   - Update location
   - Only visible to owner (403 for others)

3. PUBLISH TRIP
   POST /trips/{trip_id}/publish
   ↓
   - Full validation (description ≥50 chars, valid dates)
   - Update UserStats (trip_count++, distance_km+=)
   - Check achievements (milestones)
   - Become publicly visible
   - Status: DRAFT → PUBLISHED (irreversible)

4. PUBLISHED STATE
   ↓
   - Public visibility (anyone can view)
   - Stats integrated
   - Can still edit/delete (stats adjusted)
   - Photos contribute to photo_count
```

### Tag Normalization System

**Case-Insensitive Tag Matching**:

```python
# User submits: ["Bikepacking", "MONTAÑA", "MoNtAñA"]
# System stores:
Tag(name="Bikepacking", normalized="bikepacking")  # New tag
Tag(name="MONTAÑA", normalized="montaña")          # New tag
# "MoNtAñA" matches existing "montaña" → reuse same tag

# Result: Trip has 2 unique tags (not 3)
```

**Tag Usage Tracking**:

- Each tag has `usage_count` field
- Incremented when tag added to trip
- Decremented when tag removed or trip deleted
- Used for "popular tags" endpoint (GET /tags)

### Photo Storage Strategy

```
storage/
└── trip_photos/
    └── {year}/          # e.g., 2024
        └── {month}/     # e.g., 05
            └── {trip_id}/
                ├── {uuid}_0.jpg  # order=0
                ├── {uuid}_1.jpg  # order=1
                └── {uuid}_2.jpg  # order=2

Constraints:
- Max 20 photos per trip
- Max 10MB per photo
- Formats: JPEG, PNG
- Metadata: file_size, width, height, caption (max 500 chars)
- Order field for sorting (drag-and-drop reordering)
```

### Stats Integration

**Automatic Stats Updates on Trip Publish**:

```python
# On trip publish:
UserStats.trip_count += 1
UserStats.distance_km += trip.distance_km
UserStats.countries = set(UserStats.countries) | {trip.location.country}
UserStats.longest_trip_km = max(UserStats.longest_trip_km, trip.distance_km)

# Check achievements:
if UserStats.trip_count >= 1:
    award_achievement("FIRST_TRIP")
if UserStats.distance_km >= 1000:
    award_achievement("1000_KM")
# ... etc.

# On trip edit (if published):
recalculate_stats()  # Recompute from all published trips

# On trip delete (if published):
UserStats.trip_count -= 1
UserStats.distance_km -= trip.distance_km
recalculate_stats()  # Recompute longest_trip_km, countries
```

### Access Control Rules

| Action | Draft | Published |
|--------|-------|-----------|
| **View trip** | Owner only (403) | Public |
| **Edit trip** | Owner only | Owner only |
| **Delete trip** | Owner only | Owner only |
| **Upload photo** | Owner only | Owner only |
| **Publish trip** | Owner only | N/A (already published) |
| **List in /users/{username}/trips** | Owner only (with ?status=draft) | Public |

### Query Performance Optimizations

**Eager Loading**:

```python
# Load trip with all related data in single query
select(Trip).options(
    joinedload(Trip.photos),
    joinedload(Trip.location),
    selectinload(Trip.tags)
).where(Trip.id == trip_id)
```

**Filtering & Pagination**:

```python
# GET /users/{username}/trips?tag=bikepacking&status=published&page=1&limit=20
# - Index on (user_id, status, created_at)
# - Tags filtered via join
# - Max 50 items per page
# - Ordered by created_at DESC
```

---

## Authentication & Authorization

### JWT Token Flow

```
1. User Login
   POST /auth/login
   ↓
2. Verify credentials (bcrypt)
   ↓
3. Generate JWT tokens
   - Access token (15min)
   - Refresh token (30 days)
   ↓
4. Return tokens
   {
     "access_token": "eyJ...",
     "refresh_token": "eyJ...",
     "token_type": "bearer"
   }
   ↓
5. Client stores tokens
   ↓
6. Subsequent requests include header:
   Authorization: Bearer eyJ...
   ↓
7. get_current_user dependency validates token
   - Verify signature
   - Check expiration
   - Load user from DB
   - Verify user is active
```

### Authorization Levels

1. **Public**: No auth required (GET /users/{username})
2. **Authenticated**: Valid JWT (POST /users/{username}/follow)
3. **Owner**: User can only modify their own data (PATCH /users/{username})

---

## Performance Optimizations

### Database

- **Indexes**: On frequently queried columns (username, email, foreign keys)
- **Eager loading**: Load related data in single query with joinedload()
- **Pagination**: Max 50 items per page to prevent large result sets
- **Denormalized counters**: followers_count, following_count for fast reads

### API

- **Async I/O**: All operations are async (FastAPI + SQLAlchemy 2.0)
- **Connection pooling**: Database connections reused
- **Background tasks**: Photo processing uses asyncio.to_thread()

### Caching (Future)

- Redis for:
  - Session tokens
  - Frequently accessed profiles
  - API rate limiting

---

## Security

### Defense Layers

1. **Input Validation**: Pydantic schemas validate all input
2. **SQL Injection**: Only ORM used, no raw SQL
3. **XSS**: JSON API (frontend responsibility to escape HTML)
4. **CSRF**: Not vulnerable (JWT in headers, not cookies)
5. **Rate Limiting**: Login attempts limited (5 attempts, 15min lock)
6. **Password Security**: Bcrypt with 12 rounds
7. **Token Security**: JWT with short expiration (15min access)

### Security Checklist

- ✅ Passwords hashed with bcrypt (12 rounds)
- ✅ JWT tokens with expiration
- ✅ HTTPS enforced in production
- ✅ CORS restricted to known origins
- ✅ Input validation on all endpoints
- ✅ No raw SQL (ORM only)
- ✅ Rate limiting on auth endpoints

**See**: [Security Documentation](security.md) for complete security guide (coming soon)

---

## Testing Strategy

### Test Pyramid

```
         ╱╲
        ╱  ╲
       ╱ E2E ╲          Few (5%) - Full workflows
      ╱────────╲
     ╱          ╲
    ╱Integration╲       Some (25%) - Service + DB
   ╱──────────────╲
  ╱                ╲
 ╱    Unit Tests    ╲   Many (70%) - Individual functions
╱────────────────────╲
```

### Test Types

1. **Unit Tests** ([tests/unit/](../../../backend/tests/unit/)):
   - Test services in isolation
   - Mock database
   - Fast execution

2. **Integration Tests** ([tests/integration/](../../../backend/tests/integration/)):
   - Test complete workflows
   - Real database (SQLite in-memory)
   - HTTP requests via TestClient

3. **Contract Tests** ([tests/contract/](../../../backend/tests/contract/)):
   - Validate API responses match OpenAPI spec
   - Schema validation
   - Required fields, types, formats

### Coverage Target

- Overall: ≥90%
- Services: 100%
- API routers: ≥95%

**See**: [Testing Documentation](../../testing/README.md) for complete testing guide

---

## File Organization

```
backend/
├── src/
│   ├── api/              # HTTP endpoints (routers)
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── stats.py
│   │   ├── social.py
│   │   ├── trips.py      # Travel Diary endpoints
│   │   └── deps.py       # Shared dependencies
│   │
│   ├── services/         # Business logic
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── stats_service.py
│   │   ├── social_service.py
│   │   └── trip_service.py  # Travel Diary service
│   │
│   ├── models/           # ORM models
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── stats.py
│   │   ├── social.py
│   │   └── trip.py       # Trip, TripPhoto, Tag, TripLocation
│   │
│   ├── schemas/          # Pydantic schemas
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── stats.py
│   │   ├── social.py
│   │   ├── trip.py       # Trip schemas, TripStatus enum
│   │   └── api_response.py
│   │
│   ├── utils/            # Utilities
│   │   ├── security.py
│   │   ├── file_storage.py
│   │   ├── validators.py # HTML sanitization, etc.
│   │   └── auth.py
│   │
│   ├── migrations/       # Alembic migrations
│   │   └── versions/
│   │       ├── 001_*.py  # User profiles migrations
│   │       └── 002_*.py  # Travel Diary migrations
│   │
│   ├── config.py         # Configuration
│   ├── database.py       # DB setup
│   └── main.py           # FastAPI app
│
├── tests/
│   ├── contract/         # API contract tests
│   ├── integration/      # Integration tests
│   ├── unit/             # Unit tests
│   └── performance/      # Load tests (Locust)
│
├── scripts/              # Utility scripts
│   ├── seed_achievements.py
│   ├── create_verified_user.py
│   └── test_tags.sh      # Manual testing for tags
│
├── storage/              # File storage
│   ├── profile_photos/
│   └── trip_photos/
│
├── pyproject.toml        # Dependencies
├── alembic.ini          # Alembic config
└── .env.example         # Environment template
```

---

## Key Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Dependency Injection**: Services receive dependencies (easier testing)
3. **Type Safety**: Type hints everywhere, validated at runtime
4. **Security First**: Input validation, no raw SQL, password hashing
5. **Performance**: Async I/O, eager loading, indexing, pagination
6. **Testability**: TDD approach, high coverage, fast tests
7. **Maintainability**: Clear structure, consistent patterns, documentation

---

## Future Enhancements

- [ ] GraphQL API (alternative to REST)
- [ ] WebSockets for real-time notifications
- [ ] Redis caching layer
- [ ] Event sourcing for audit trail
- [ ] Message queue (Celery/RabbitMQ) for async tasks
- [ ] Multi-tenancy support
- [ ] API versioning (v1, v2)
- [ ] Rate limiting per-user quotas

---

## Related Documentation

- **[API Reference](../../api/README.md)** - API endpoints and contracts
- **[Testing](../../testing/README.md)** - Test strategies and guides
- **[Deployment](../../deployment/README.md)** - Deployment modes and configurations
- **[User Guides](../../user-guides/README.md)** - End-user documentation
- **[Data Model](../data-model/schemas.md)** - Database schemas and migrations (coming soon)
- **[Security](security.md)** - Security patterns and best practices (coming soon)

---

**Last Updated**: 2026-02-07
**Source**: Migrated from backend/docs/ARCHITECTURE.md (761 lines)
**Status**: ✅ Complete
