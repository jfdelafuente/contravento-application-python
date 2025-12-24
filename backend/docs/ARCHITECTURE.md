# ContraVento Backend - Architecture Documentation

## System Overview

ContraVento es una plataforma social de cicloturismo con una arquitectura de 3 capas que sigue principios de Clean Architecture y Domain-Driven Design.

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  (FastAPI Routers - HTTP Interface)                         │
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  auth.py │ │profile.py│ │ stats.py │ │social.py │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│       ↓             ↓            ↓            ↓             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  (Business Logic & Domain Rules)                            │
│                                                              │
│  ┌──────────────┐ ┌───────────────┐ ┌──────────────┐      │
│  │AuthService   │ │ProfileService │ │StatsService  │      │
│  └──────────────┘ └───────────────┘ └──────────────┘      │
│  ┌──────────────┐                                          │
│  │SocialService │                                          │
│  └──────────────┘                                          │
│       ↓                   ↓                ↓                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
│  (ORM Models & Database Access)                             │
│                                                              │
│  ┌──────┐ ┌───────────┐ ┌──────┐ ┌──────────┐ ┌────────┐ │
│  │ User │ │UserProfile│ │Stats │ │Achievement│ │ Follow │ │
│  └──────┘ └───────────┘ └──────┘ └──────────┘ └────────┘ │
│       ↓          ↓           ↓         ↓           ↓        │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌────────────────┐
                    │   PostgreSQL   │
                    │   / SQLite     │
                    └────────────────┘
```

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
- `auth.py` - Registration, login, verification
- `profile.py` - Profile CRUD, photo upload
- `stats.py` - User statistics and achievements
- `social.py` - Follow/unfollow, followers/following lists
- `deps.py` - Shared dependencies (auth, DB session)

**Key Pattern**: Thin controllers - minimal logic, delegate to services

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
- `auth_service.py` - Authentication logic, password reset
- `profile_service.py` - Profile management, privacy rules
- `stats_service.py` - Stats calculation, achievement awarding
- `social_service.py` - Follow logic, counter management

**Key Pattern**: Rich domain services - all business logic lives here

### Data Layer (`src/models/`)

**Purpose**: Data persistence and ORM mapping

**Responsibilities**:
- Define database schema
- Relationships between entities
- Constraints and indexes
- Database migrations (Alembic)

**Files**:
- `user.py` - User, UserProfile models
- `auth.py` - PasswordReset model
- `stats.py` - UserStats, Achievement, UserAchievement models
- `social.py` - Follow model

**Key Pattern**: Anemic models - minimal logic, pure data structures

### Schemas Layer (`src/schemas/`)

**Purpose**: Request/response validation and serialization

**Responsibilities**:
- Validate incoming data
- Serialize outgoing data
- Type safety
- API contract definition

**Files**:
- `auth.py` - Login, registration, token schemas
- `profile.py` - Profile update, response schemas
- `stats.py` - Stats and achievement schemas
- `social.py` - Follow, followers, following schemas
- `api_response.py` - Standard response envelope

**Key Pattern**: DTO (Data Transfer Objects) for API boundary

### Utils Layer (`src/utils/`)

**Purpose**: Reusable utilities and helpers

**Files**:
- `security.py` - Password hashing, JWT creation/validation
- `file_storage.py` - Photo validation, resize, storage
- `auth.py` - get_current_user dependency

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
  └─── (N) Follow (as following)
```

### Key Constraints

- **Unique constraints**: username, email, (follower_id, following_id)
- **Foreign keys**: All with CASCADE delete
- **Check constraints**: follower_id != following_id (prevent self-follow)
- **Indexes**: On username, email, foreign keys, created_at

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

1. **Unit Tests** (`tests/unit/`):
   - Test services in isolation
   - Mock database
   - Fast execution

2. **Integration Tests** (`tests/integration/`):
   - Test complete workflows
   - Real database (SQLite in-memory)
   - HTTP requests via TestClient

3. **Contract Tests** (`tests/contract/`):
   - Validate API responses match OpenAPI spec
   - Schema validation
   - Required fields, types, formats

### Coverage Target

- Overall: ≥90%
- Services: 100%
- API routers: ≥95%

## Deployment

### Development

```bash
poetry run uvicorn src.main:app --reload
```

### Production (Docker)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY src/ ./src/
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Config

- Development: SQLite, debug mode, auto-reload
- Testing: In-memory SQLite, fast tests
- Production: PostgreSQL, optimized, HTTPS

## Monitoring & Logging

### Logging

- **Structured logs**: JSON format for production
- **Levels**: DEBUG (dev), INFO (prod), ERROR (critical)
- **Logged events**:
  - Authentication attempts
  - API errors
  - Performance issues
  - Security events

### Future Monitoring

- Application Performance Monitoring (APM): Sentry, DataDog
- Metrics: Prometheus + Grafana
- Alerts: Failed login spikes, error rates, slow queries

## File Organization

```
backend/
├── src/
│   ├── api/              # HTTP endpoints (routers)
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── stats.py
│   │   ├── social.py
│   │   └── deps.py       # Shared dependencies
│   │
│   ├── services/         # Business logic
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── stats_service.py
│   │   └── social_service.py
│   │
│   ├── models/           # ORM models
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── stats.py
│   │   └── social.py
│   │
│   ├── schemas/          # Pydantic schemas
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── stats.py
│   │   ├── social.py
│   │   └── api_response.py
│   │
│   ├── utils/            # Utilities
│   │   ├── security.py
│   │   ├── file_storage.py
│   │   └── auth.py
│   │
│   ├── migrations/       # Alembic migrations
│   │   └── versions/
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
│   └── seed_achievements.py
│
├── storage/              # File storage
│   └── profile_photos/
│
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md   # This file
│   └── API.md           # API documentation
│
├── pyproject.toml        # Dependencies
├── alembic.ini          # Alembic config
├── .env.example         # Environment template
└── README.md            # Quick start guide
```

## Key Principles

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Dependency Injection**: Services receive dependencies (easier testing)
3. **Type Safety**: Type hints everywhere, validated at runtime
4. **Security First**: Input validation, no raw SQL, password hashing
5. **Performance**: Async I/O, eager loading, indexing, pagination
6. **Testability**: TDD approach, high coverage, fast tests
7. **Maintainability**: Clear structure, consistent patterns, documentation

## Future Enhancements

- [ ] GraphQL API (alternative to REST)
- [ ] WebSockets for real-time notifications
- [ ] Redis caching layer
- [ ] Event sourcing for audit trail
- [ ] Message queue (Celery/RabbitMQ) for async tasks
- [ ] Multi-tenancy support
- [ ] API versioning (v1, v2)
- [ ] Rate limiting per-user quotas
