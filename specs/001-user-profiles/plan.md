# Implementation Plan: User Profiles & Authentication

**Branch**: `001-user-profiles` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)

## Summary

This feature implements the foundational authentication and user profile system for ContraVento, a cycling social platform. It includes secure user registration with email verification, JWT-based authentication, comprehensive profile management with photo uploads, auto-calculated cycling statistics, achievement gamification, and social follow/follower relationships.

**Technical Approach**: FastAPI backend with async SQLAlchemy 2.0 (SQLite for dev/test, PostgreSQL for production), bcrypt password hashing, JWT tokens with refresh mechanism, Pydantic validation, local file storage for profile photos, background tasks for email and statistics, and pytest-based TDD workflow.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**:
- FastAPI 0.104+ (async web framework)
- SQLAlchemy 2.0+ (async ORM)
- Pydantic 2.0+ (validation)
- python-jose (JWT)
- passlib[bcrypt] (password hashing)
- aiofiles (async file I/O)
- python-multipart (file uploads)
- aiosqlite (SQLite async driver for dev/test)
- asyncpg (PostgreSQL async driver for production)

**Storage**:
- **Development/Testing**: SQLite 3.37+ (file-based, no Docker required)
- **Production**: PostgreSQL 15+ (managed service or Docker)
- **Files**: Local filesystem initially (S3-ready structure for production migration)

**Testing**: pytest with pytest-asyncio, pytest-cov, httpx (async client), Faker (test data)

**Target Platform**: Linux server (Docker containerized for production), Python async ASGI (uvicorn)

**Project Type**: Web application (backend API + frontend)

**Performance Goals**:
- <500ms p95 for authentication endpoints (SC-003)
- <200ms p95 for simple profile queries
- <2s for photo uploads up to 5MB (SC-006)
- Support 100+ concurrent registrations (SC-004)

**Constraints**:
- Bcrypt rounds ≥12 for security (Constitution + SC-019)
- JWT expiration: 30 days with refresh tokens (FR-010)
- Profile photo max 5MB, auto-resize to 400x400px (FR-012, FR-013)
- Session management must support hundreds of concurrent users

**Scale/Scope**:
- Initial deployment: hundreds of concurrent users
- Database: 7 primary tables
- 32 functional requirements across 4 user stories
- API: ~25 endpoints across 4 contracts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability ✅

- **PEP 8 Compliance**: All Python code uses `black` formatter (line length 100) and `ruff` linter
- **Type Hints**: Mandatory for all function signatures using Python 3.11+ syntax
- **Docstrings**: Google-style docstrings for all public functions, classes, modules
- **Single Responsibility**: Each service handles one domain (AuthService, ProfileService, StatsService, SocialService)
- **No Magic Numbers**: Constants in `config.py` (PASSWORD_MIN_LENGTH=8, BCRYPT_ROUNDS=12, etc.)
- **No Code Duplication**: Shared logic in utils/, DRY principles enforced

**PASS** - All requirements met

### II. Testing Standards (Non-Negotiable) ✅

- **TDD Workflow**: Tests written first for each FR before implementation
- **Coverage Target**: ≥90% across all modules
- **Test Structure**:
  - Unit tests: Business logic in services/, models/, validation
  - Integration tests: Database operations, API endpoints, auth flow
  - Contract tests: OpenAPI schema validation
- **Test Independence**: Fresh SQLite database per test (pytest fixtures with transaction rollback)
- **Edge Cases**: Explicit tests for rate limiting (FR-009), duplicates, invalid uploads

**PASS** - TDD workflow defined, pytest infrastructure planned

### III. User Experience Consistency ✅

- **Primary Language**: All responses, errors, validation in Spanish
- **API Response Structure**: Standardized JSON
  ```json
  {
    "success": true,
    "data": {...},
    "error": null
  }
  ```
- **Error Handling**: Field-specific validation with actionable Spanish messages
- **HTTP Status Codes**: Proper usage (200, 201, 400, 401, 404, 500)
- **Timezone Awareness**: All timestamps UTC with timezone info

**PASS** - API contract defines Spanish responses

### IV. Performance Requirements ✅

- **Database Indexing**: Unique on email/username, indexes on foreign keys
- **Query Optimization**: Eager loading for related entities
- **Pagination**: Max 50 items for followers/following lists
- **Image Processing**: Async background task with Pillow
- **Connection Pooling**:
  - SQLite: Single connection in dev/test (thread-safe mode)
  - PostgreSQL: pool_size=20, max_overflow=10 in production

**PASS** - Performance targets aligned with success criteria

### Security & Data Protection ✅

- **Password Hashing**: bcrypt 12 rounds (SC-019)
- **JWT Security**: 15min access tokens, 30-day refresh tokens (FR-010)
- **SQL Injection Prevention**: SQLAlchemy ORM only, no raw SQL
- **File Upload Validation**: MIME type check, 5MB limit, content scanning
- **Input Sanitization**: Pydantic validates all inputs
- **Rate Limiting**: 5 login attempts, 15min lockout (FR-009)

**PASS** - Security requirements met

**VERDICT**: All gates PASS. No constitution violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/001-user-profiles/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Database schema
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: OpenAPI schemas
│   ├── auth.yaml        # Authentication endpoints
│   ├── profile.yaml     # Profile CRUD endpoints
│   ├── stats.yaml       # Statistics and achievements
│   └── social.yaml      # Follow/followers endpoints
└── tasks.md             # Phase 2: NOT created by plan command
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                      # FastAPI app entry
│   ├── config.py                    # Configuration & env vars
│   ├── database.py                  # SQLAlchemy async setup
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                  # User, UserProfile
│   │   ├── stats.py                 # UserStats, Achievement, UserAchievement
│   │   ├── social.py                # Follow relationship
│   │   └── auth.py                  # PasswordReset tokens
│   │
│   ├── schemas/                     # Pydantic validation/serialization
│   │   ├── __init__.py
│   │   ├── user.py                  # UserCreate, UserResponse, UserUpdate
│   │   ├── auth.py                  # LoginRequest, TokenResponse
│   │   ├── profile.py               # ProfileUpdate, ProfileResponse
│   │   ├── stats.py                 # StatsResponse, AchievementResponse
│   │   └── social.py                # FollowResponse, FollowersList
│   │
│   ├── services/                    # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Registration, login, JWT, password reset
│   │   ├── profile_service.py       # Profile CRUD, photo upload
│   │   ├── stats_service.py         # Statistics calculation, achievements
│   │   └── social_service.py        # Follow/unfollow operations
│   │
│   ├── api/                         # FastAPI routers (thin layer)
│   │   ├── __init__.py
│   │   ├── deps.py                  # Dependency injection (get_db, get_current_user)
│   │   ├── auth.py                  # POST /auth/register, /auth/login
│   │   ├── profile.py               # GET/PUT /users/{username}/profile
│   │   ├── stats.py                 # GET /users/{username}/stats
│   │   └── social.py                # POST /users/{username}/follow
│   │
│   ├── utils/                       # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py              # Password hashing, JWT encode/decode
│   │   ├── email.py                 # Email sending (verification, password reset)
│   │   ├── file_storage.py          # Photo upload, resize, storage
│   │   └── validators.py            # Custom Pydantic validators
│   │
│   └── migrations/                  # Alembic database migrations
│       ├── env.py
│       ├── versions/
│       │   └── 001_initial_schema.py
│       └── alembic.ini
│
├── tests/
│   ├── conftest.py                  # Pytest fixtures (SQLite db, client, auth)
│   ├── contract/
│   │   ├── test_auth_contracts.py   # OpenAPI schema validation
│   │   ├── test_profile_contracts.py
│   │   ├── test_stats_contracts.py
│   │   └── test_social_contracts.py
│   │
│   ├── integration/
│   │   ├── test_auth_flow.py        # Registration → login → logout
│   │   ├── test_profile_management.py
│   │   ├── test_photo_upload.py
│   │   ├── test_stats_calculation.py
│   │   └── test_follow_workflow.py
│   │
│   └── unit/
│       ├── test_auth_service.py     # Business logic unit tests
│       ├── test_profile_service.py
│       ├── test_stats_service.py
│       ├── test_social_service.py
│       ├── test_security_utils.py
│       └── test_validators.py
│
├── pyproject.toml                   # Poetry dependencies
├── .env.example                     # Environment template
├── .env.test                        # Test environment (SQLite)
├── Dockerfile
└── docker-compose.yml               # PostgreSQL + Redis (production)

frontend/
├── src/
│   ├── components/                  # React components (future)
│   ├── pages/
│   │   ├── auth/                    # Login, Register pages
│   │   ├── profile/                 # Profile view, edit
│   │   └── social/                  # Followers, Following lists
│   └── services/
│       └── api.ts                   # API client
└── tests/
```

**Structure Decision**: Selected **Web application** structure because:
1. Spec requires both API and UI ("plataforma social")
2. Separation allows independent scaling (API for mobile, frontend on CDN)
3. Backend follows Clean Architecture (models → schemas → services → api)
4. SQLite for dev/test eliminates Docker dependency during development

## Complexity Tracking

**No violations** - Constitution check passed. All requirements align with established principles.

## Database Strategy: SQLite vs PostgreSQL

### Development & Testing: SQLite

**Why SQLite for dev/test**:
- ✅ Zero configuration (no Docker/services required)
- ✅ Fast test execution (in-memory mode)
- ✅ Perfect for CI/CD (GitHub Actions, etc.)
- ✅ Simplified developer onboarding
- ✅ Identical SQLAlchemy code works for both

**SQLite Configuration**:
```python
# Development
DATABASE_URL = "sqlite+aiosqlite:///./contravento_dev.db"

# Testing (in-memory)
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

**SQLite Limitations** (handled gracefully):
- No built-in UUID type → Use TEXT with UUID strings
- Arrays stored as JSON → `countries_visited` as JSON array
- Check constraints supported → All validations work
- Foreign keys enabled explicitly → `PRAGMA foreign_keys=ON`

### Production: PostgreSQL

**Why PostgreSQL for production**:
- ✅ Native UUID support (`gen_random_uuid()`)
- ✅ Array columns (TEXT[])
- ✅ Better concurrency (hundreds of users)
- ✅ Advanced indexing (GIN, BRIN)
- ✅ Full-text search (future feature)

**PostgreSQL Configuration**:
```python
# Production
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/contravento"
```

**Migration Path**: SQLAlchemy abstracts differences. Same models work for both databases with minor dialect-specific adjustments in migrations.

## Implementation Strategy

### Phase 0: Research & Foundation (Week 1)

**Research topics** (documented in research.md):
1. SQLite vs PostgreSQL for development
2. JWT vs Session-based auth
3. bcrypt rounds (12 vs 14 performance)
4. Email verification patterns
5. File upload handling strategies
6. Follow/follower SQL patterns
7. Statistics calculation (real-time vs cached)

**Foundation tasks**:
- Set up project structure (backend/, frontend/)
- Configure Poetry with dependencies
- Initialize FastAPI app with health check
- Set up pytest with SQLite fixtures
- Create Alembic migrations (7 tables)
- Implement core utilities (password, JWT, email)

### Phase 1: Authentication (Week 2)

**TDD Cycle**:
1. Write tests for AuthService (FR-001 to FR-010)
2. Implement AuthService business logic
3. Build FastAPI auth routes
4. Integration tests: Full registration → login → logout flow
5. Contract tests: OpenAPI schema validation

**Deliverables**:
- User registration with email verification
- Login with JWT access + refresh tokens
- Password reset workflow
- Rate limiting (5 attempts, 15min lockout)

### Phase 2: Profile Management (Week 3)

**TDD Cycle**:
1. Write tests for ProfileService (FR-011 to FR-018)
2. Implement profile CRUD operations
3. Build photo upload with Pillow resize
4. Integration tests: Profile update, photo workflow

**Deliverables**:
- Profile editing (bio, location, cycling type)
- Photo upload (5MB max, 400x400 resize)
- Public profile view
- Privacy settings (show_email, show_location)

### Phase 3: Statistics & Achievements (Week 4)

**TDD Cycle**:
1. Write tests for StatsService (FR-019 to FR-024)
2. Implement stats calculation logic
3. Build background task for updates
4. Seed achievements in database
5. Integration tests with mocked trip events

**Deliverables**:
- Auto-calculated stats (km, trips, countries)
- Achievement system (9 predefined badges)
- Stats update on trip publish/edit/delete
- Display on profile

### Phase 5: Social Features (Week 5)

**TDD Cycle**:
1. Write tests for SocialService (FR-025 to FR-032)
2. Implement follow/unfollow logic
3. Build paginated follower lists
4. Optimize queries for large lists
5. Integration tests: Full follow workflow

**Deliverables**:
- Follow/unfollow functionality
- Followers and following lists (paginated)
- Prevent self-follow
- Update denormalized counters

### Phase 6: Integration & Polish (Week 6)

- End-to-end testing across all 4 user stories
- Performance testing (Locust load tests)
- Security audit (OWASP top 10)
- API documentation
- Frontend scaffold (React login/register)

## Next Steps

1. **Create research.md** - Document all technology decisions
2. **Create data-model.md** - Full database schema with SQLite/PostgreSQL differences
3. **Create contracts/** - OpenAPI specs for all 25 endpoints
4. **Create quickstart.md** - Developer guide with SQLite setup
5. **Run `/speckit.tasks`** - Generate implementation task list

---

**Plan Status**: ✅ Complete - Ready for task generation
**Agent ID**: a44769d (can be resumed for follow-up work)
