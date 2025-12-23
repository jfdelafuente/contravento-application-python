# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ContraVento** is a cycling social platform built with FastAPI (backend) and React (frontend planned). The platform enables cyclists to document trips, share routes, track statistics, and connect with the cycling community.

## Commands

### Setup & Installation

```bash
# Navigate to backend
cd backend

# Install dependencies with Poetry
poetry install

# Generate SECRET_KEY for .env
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy and configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY and other settings
```

### Database Migrations

```bash
# Apply all migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Rollback last migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

### Development Server

```bash
# Run development server with hot reload
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# API docs at: http://localhost:8000/docs
```

### Testing

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage (required ≥90%)
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Run specific test types
poetry run pytest tests/unit/ -v              # Unit tests only
poetry run pytest tests/integration/ -v       # Integration tests only
poetry run pytest tests/contract/ -v          # Contract tests only

# Run single test file
poetry run pytest tests/unit/test_auth_service.py -v

# Run single test function
poetry run pytest tests/unit/test_auth_service.py::test_register_user -v
```

### Code Quality

```bash
cd backend

# Format code (required before commit)
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/

# Run all quality checks
poetry run black src/ tests/ && \
poetry run ruff check src/ tests/ && \
poetry run mypy src/ && \
poetry run pytest --cov=src
```

## Architecture

### Layer Structure (Clean Architecture)

The backend follows a strict layered architecture with clear separation of concerns:

```
API Layer (FastAPI Routers)
    ↓ calls
Service Layer (Business Logic)
    ↓ uses
Model Layer (SQLAlchemy ORM)
    ↓ persists to
Database (SQLite dev/test, PostgreSQL prod)
```

**Critical Rule**: Layers can only call downward. APIs call Services, Services use Models. Never skip layers.

### Key Architectural Patterns

1. **Dependency Injection**: All database sessions and current user passed via FastAPI `Depends()`
2. **Schema Separation**: Pydantic schemas for validation (in `schemas/`) are distinct from SQLAlchemy models (in `models/`)
3. **Service Layer Pattern**: All business logic lives in `services/`, never in API routes or models
4. **Repository Pattern**: Services interact with database through async SQLAlchemy session, not direct SQL

### Module Organization

- **`src/models/`**: SQLAlchemy ORM models (User, UserProfile, UserStats, etc.)
- **`src/schemas/`**: Pydantic models for request/response validation
- **`src/services/`**: Business logic (AuthService, ProfileService, StatsService, SocialService)
- **`src/api/`**: FastAPI routers - thin layer that calls services
- **`src/utils/`**: Shared utilities (security, email, file storage, validators)
- **`src/config.py`**: Environment variable management with Pydantic Settings
- **`src/database.py`**: Async SQLAlchemy engine and session management

## Database Strategy

**Dual Database Approach** - Same codebase runs on both:

- **Development/Testing**: SQLite with aiosqlite (file-based or in-memory)
  - Zero configuration, fast tests, no Docker required
  - In-memory mode for test isolation

- **Production**: PostgreSQL with asyncpg
  - Native UUID support, array columns, better concurrency
  - Connection pooling (pool_size=20)

**Important Differences**:
- UUIDs: PostgreSQL uses native UUID type, SQLite stores as TEXT
- Arrays: PostgreSQL uses ARRAY[], SQLite uses JSON
- Foreign Keys: Must enable explicitly in SQLite with `PRAGMA foreign_keys=ON`

Alembic migrations detect the dialect and apply appropriate DDL for each database type.

## Constitution Requirements (Non-Negotiable)

### I. Code Quality
- PEP 8 with black formatter (100 char line length)
- Type hints required on ALL functions
- Google-style docstrings for public functions
- Single Responsibility Principle strictly enforced
- No magic numbers - use constants in config.py

### II. Testing (TDD Mandatory)
- **Write tests FIRST** before any implementation
- Coverage requirement: ≥90% across all modules
- Test structure:
  - Unit tests: Business logic in services/
  - Integration tests: API endpoints, database operations
  - Contract tests: OpenAPI schema validation
- All tests must pass before PR merge

### III. User Experience
- All user-facing text in Spanish (primary language)
- Standardized JSON API responses:
  ```json
  {
    "success": true,
    "data": {...},
    "error": null
  }
  ```
- Field-specific validation errors with Spanish messages
- UTC timestamps with timezone awareness

### IV. Performance
- Simple queries: <200ms p95
- Auth endpoints: <500ms p95
- Photo uploads: <2s for 5MB files
- Use eager loading to prevent N+1 queries
- Pagination: max 50 items per page

### V. Security
- Bcrypt password hashing with 12 rounds (production)
- JWT: 15min access tokens, 30-day refresh tokens
- Rate limiting: 5 login attempts, 15min lockout
- Only use SQLAlchemy ORM - never raw SQL
- Validate all file uploads (MIME type, size, content)

## Authentication & Authorization

**JWT Token Flow**:
1. User logs in → receives access token (15min) + refresh token (30 days)
2. Access token in Authorization header: `Bearer {token}`
3. When access token expires → use refresh token to get new pair
4. On logout → invalidate refresh token

**Dependency Injection Pattern**:
```python
from src.api.deps import get_current_user, get_db

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # current_user is automatically validated from JWT
    # db is async database session
    pass
```

## Specification-Driven Development

This project uses a structured specification workflow in `specs/`:

1. **spec.md**: User stories, functional requirements (FR-###), success criteria (SC-###)
2. **plan.md**: Technical implementation plan, architecture decisions
3. **data-model.md**: Database schema with DDL for SQLite and PostgreSQL
4. **contracts/**: OpenAPI YAML files defining all API endpoints
5. **tasks.md**: Step-by-step implementation tasks

**Always reference**:
- Functional requirements as FR-### in code comments
- Success criteria as SC-### for performance targets
- OpenAPI contracts for exact request/response schemas

## File Upload Handling

Profile photos follow this pattern:
1. Validate: Check MIME type, size (max 5MB)
2. Store original temporarily
3. **Background task**: Resize to 400x400px with Pillow
4. Save to: `storage/profile_photos/{year}/{month}/{user_id}_{uuid}.jpg`
5. Update database with photo_url
6. Delete original

**Security**: Never trust client-provided filenames or MIME types - validate content.

## Testing Patterns

### TDD Workflow (Strictly Enforced)
1. Write test for feature (Red - test fails)
2. Implement minimal code to pass (Green - test passes)
3. Refactor while keeping tests passing
4. Never write production code without a failing test first

### Test Fixtures (conftest.py)
- `db_session`: Fresh SQLite in-memory database per test
- `client`: AsyncClient for API testing
- `auth_headers`: Pre-authenticated user headers for protected endpoints
- `faker`: Faker instance for generating test data

### Example Test Structure
```python
# tests/unit/test_auth_service.py
async def test_register_user(db_session):
    """Test user registration creates user and sends verification email."""
    # Arrange
    user_data = {...}

    # Act
    result = await AuthService.register(db_session, user_data)

    # Assert
    assert result.email == user_data["email"]
    assert result.is_verified is False
```

## Error Handling

All errors must return standardized JSON with Spanish messages:

```python
from fastapi import HTTPException

# Bad request with field-specific error
raise HTTPException(
    status_code=400,
    detail={
        "code": "VALIDATION_ERROR",
        "message": "El email ya está registrado",
        "field": "email"
    }
)

# Unauthorized
raise HTTPException(
    status_code=401,
    detail={
        "code": "UNAUTHORIZED",
        "message": "Token de autenticación inválido"
    }
)
```

## Environment Variables

Critical variables (see `.env.example` for complete list):
- `DATABASE_URL`: Database connection string (SQLite or PostgreSQL)
- `SECRET_KEY`: JWT secret (min 32 chars) - generate with `secrets.token_urlsafe(32)`
- `BCRYPT_ROUNDS`: 12 for production, 4 for tests (faster)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 15
- `REFRESH_TOKEN_EXPIRE_DAYS`: 30
- `UPLOAD_MAX_SIZE_MB`: 5
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Common Pitfalls to Avoid

1. **Don't skip TDD**: Tests must be written before implementation
2. **Don't mix layers**: API routes should only call services, never access models directly
3. **Don't use raw SQL**: Always use SQLAlchemy ORM for query safety
4. **Don't forget async**: All database operations and file I/O must be async
5. **Don't hardcode Spanish text**: Use constants or configuration for i18n readiness
6. **Don't skip foreign key pragma**: SQLite requires explicit `PRAGMA foreign_keys=ON`
7. **Don't trust user input**: Validate everything with Pydantic schemas
8. **Don't forget indexes**: Add indexes for frequently queried columns
9. **Don't return stack traces to users**: Catch exceptions and return friendly Spanish errors
10. **Don't skip coverage**: ≥90% is mandatory before PR approval

## Specification Commands

This project uses `/speckit.*` commands for specification-driven development:

- `/speckit.specify`: Create feature specifications
- `/speckit.plan`: Generate implementation plans
- `/speckit.tasks`: Break down features into tasks
- `/speckit.implement`: Execute implementation phases

See `.specify/` directory for templates and workflows.
