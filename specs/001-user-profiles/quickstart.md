# Developer Quickstart Guide: User Profiles & Authentication

**Feature**: 001-user-profiles | **Updated**: 2025-12-23

## Purpose

This guide helps developers set up the authentication and user profile system for local development and testing. It covers both SQLite (recommended for development) and PostgreSQL (production) configurations.

---

## Prerequisites

### Required Tools

- **Python**: 3.11 or higher
- **Poetry**: 1.6+ (dependency management)
- **Git**: For version control

### Optional Tools (Production)

- **Docker**: For PostgreSQL in production
- **PostgreSQL**: 15+ (if not using Docker)

### Verify Installation

```bash
python --version   # Should show 3.11+
poetry --version   # Should show 1.6+
git --version
```

---

## Quick Start (SQLite - Recommended for Dev/Test)

### 1. Clone Repository

```bash
git clone https://github.com/contravento/contravento-application-python.git
cd contravento-application-python
```

### 2. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install all dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell
```

**Dependencies installed**:
- FastAPI 0.104+ (web framework)
- SQLAlchemy 2.0+ with aiosqlite (async ORM + SQLite driver)
- Pydantic 2.0+ (validation)
- python-jose (JWT tokens)
- passlib[bcrypt] (password hashing)
- pytest + pytest-asyncio (testing)

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env.dev

# Edit .env.dev
nano .env.dev
```

**`.env.dev` (SQLite configuration)**:
```bash
# Application
APP_NAME=ContraVento
APP_ENV=development
DEBUG=true

# Database - SQLite (file-based)
DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Password Hashing
BCRYPT_ROUNDS=12

# Email (development - logs to console)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@contravento.com

# Storage
STORAGE_PATH=./storage
UPLOAD_MAX_SIZE_MB=5
PROFILE_PHOTO_SIZE=400

# CORS (for frontend dev server)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Initialize Database

```bash
# Run Alembic migrations
alembic upgrade head

# Seed achievements data
python scripts/seed_achievements.py
```

### 5. Run Development Server

```bash
# Start FastAPI with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**API is now running at**: `http://localhost:8000`

**Interactive API docs**: `http://localhost:8000/docs`

### 6. Run Tests

```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_auth_service.py -v

# Run integration tests
pytest tests/integration/ -v

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Expected coverage**: ≥90% (constitution requirement)

---

## Alternative: PostgreSQL Setup (Production-Like)

### Option A: Docker Compose (Recommended)

**1. Create `docker-compose.yml`**:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: contravento_db
    environment:
      POSTGRES_DB: contravento
      POSTGRES_USER: contravento
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U contravento"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: contravento_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**2. Start services**:

```bash
docker-compose up -d
```

**3. Configure environment**:

**`.env.dev` (PostgreSQL configuration)**:
```bash
# Database - PostgreSQL
DATABASE_URL=postgresql+asyncpg://contravento:devpassword@localhost:5432/contravento

# Rest of configuration same as SQLite version
# ...
```

**4. Run migrations**:

```bash
alembic upgrade head
python scripts/seed_achievements.py
```

### Option B: Local PostgreSQL Installation

**1. Install PostgreSQL** (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install postgresql-15 postgresql-contrib
```

**2. Create database and user**:

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE contravento;
CREATE USER contravento WITH PASSWORD 'devpassword';
GRANT ALL PRIVILEGES ON DATABASE contravento TO contravento;

# Enable UUID extension
\c contravento
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\q
```

**3. Configure `.env.dev`** (same as Docker option above)

**4. Run migrations** (same as Docker option above)

---

## Project Structure

```
backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration from environment
│   ├── database.py             # SQLAlchemy async setup
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py             # User, UserProfile
│   │   ├── stats.py            # UserStats, Achievement, UserAchievement
│   │   ├── social.py           # Follow
│   │   └── auth.py             # PasswordReset
│   │
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py             # UserCreate, UserResponse
│   │   ├── auth.py             # LoginRequest, TokenResponse
│   │   ├── profile.py          # ProfileUpdate, ProfileResponse
│   │   ├── stats.py            # StatsResponse, AchievementResponse
│   │   └── social.py           # FollowResponse, FollowersList
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Registration, login, JWT
│   │   ├── profile_service.py  # Profile CRUD, photo upload
│   │   ├── stats_service.py    # Statistics calculation
│   │   └── social_service.py   # Follow/unfollow operations
│   │
│   ├── api/                    # FastAPI routers
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependency injection
│   │   ├── auth.py             # /auth/* endpoints
│   │   ├── profile.py          # /users/{username}/profile
│   │   ├── stats.py            # /users/{username}/stats
│   │   └── social.py           # /users/{username}/follow
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── security.py         # Password hashing, JWT
│   │   ├── email.py            # Email sending
│   │   ├── file_storage.py     # Photo upload/resize
│   │   └── validators.py       # Custom validators
│   │
│   └── migrations/             # Alembic migrations
│       ├── env.py
│       ├── alembic.ini
│       └── versions/
│           └── 001_initial_schema.py
│
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── contract/               # OpenAPI validation tests
│   ├── integration/            # Integration tests
│   └── unit/                   # Unit tests
│
├── scripts/
│   └── seed_achievements.py    # Seed achievement data
│
├── storage/
│   └── profile_photos/         # Uploaded photos (local)
│
├── pyproject.toml              # Poetry dependencies
├── .env.example                # Environment template
├── .env.dev                    # Development environment
├── .env.test                   # Test environment
└── README.md
```

---

## Common Development Tasks

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new field to user_profile"

# Review generated migration
cat migrations/versions/002_*.py

# Apply migration
alembic upgrade head
```

### Rollback Migration

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# Rollback all
alembic downgrade base
```

### Reset Database (Development Only)

**SQLite**:
```bash
rm contravento_dev.db
alembic upgrade head
python scripts/seed_achievements.py
```

**PostgreSQL**:
```bash
psql -U contravento -d postgres -c "DROP DATABASE contravento;"
psql -U contravento -d postgres -c "CREATE DATABASE contravento;"
alembic upgrade head
python scripts/seed_achievements.py
```

### Run Linters and Formatters

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type checking with mypy
mypy src/

# All checks (as in CI)
./scripts/check_quality.sh
```

### Interactive API Testing

**1. Start server**:
```bash
uvicorn src.main:app --reload
```

**2. Open Swagger UI**: `http://localhost:8000/docs`

**3. Test authentication flow**:

1. **POST /auth/register**:
   ```json
   {
     "username": "test_user",
     "email": "test@example.com",
     "password": "SecurePass123!"
   }
   ```

2. **Check console** for verification email (development mode logs emails)

3. **POST /auth/verify-email** (copy token from console):
   ```json
   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI..."
   }
   ```

4. **POST /auth/login**:
   ```json
   {
     "login": "test_user",
     "password": "SecurePass123!"
   }
   ```

5. **Copy `access_token` from response**

6. **Click "Authorize"** button in Swagger UI, enter: `Bearer {access_token}`

7. **Test authenticated endpoints** (e.g., PUT /users/test_user/profile)

---

## Environment-Specific Configurations

### Development (`.env.dev`)
- SQLite database (fast, no setup)
- Email logs to console
- DEBUG=true
- CORS allows localhost origins

### Testing (`.env.test`)
```bash
# Test environment (used by pytest)
APP_ENV=testing
DEBUG=false

# In-memory SQLite (fresh database per test)
DATABASE_URL=sqlite+aiosqlite:///:memory:

# Fast bcrypt for tests (4 rounds instead of 12)
BCRYPT_ROUNDS=4

# Disable email sending
SMTP_HOST=localhost
SMTP_PORT=1025

# Shorter token expiration for testing
ACCESS_TOKEN_EXPIRE_MINUTES=5
```

### Production (`.env.prod`)
```bash
APP_ENV=production
DEBUG=false

# PostgreSQL with connection pooling
DATABASE_URL=postgresql+asyncpg://user:password@db.contravento.com:5432/contravento

# Strong secret (use secrets manager in real production)
SECRET_KEY=${SECRET_KEY_FROM_VAULT}

# Production bcrypt (12 rounds)
BCRYPT_ROUNDS=12

# Real SMTP service
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=${SENDGRID_USER}
SMTP_PASSWORD=${SENDGRID_API_KEY}
SMTP_FROM=noreply@contravento.com

# S3 storage (future)
STORAGE_BACKEND=s3
S3_BUCKET=contravento-uploads
S3_REGION=eu-west-1

# CORS for production frontend
CORS_ORIGINS=https://contravento.com,https://www.contravento.com
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'aiosqlite'`

**Solution**:
```bash
poetry install
poetry shell
```

### Issue: `alembic.util.exc.CommandError: Can't locate revision identified by 'head'`

**Solution**:
```bash
# Initialize Alembic (first time only)
alembic init migrations

# Or delete and recreate database
rm contravento_dev.db
alembic upgrade head
```

### Issue: `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users`

**Solution**:
```bash
# Run migrations
alembic upgrade head
```

### Issue: `FOREIGN KEY constraint failed` (SQLite)

**Solution**: Foreign keys are disabled by default in SQLite. Enable them:

```python
# In src/database.py
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if 'sqlite' in str(dbapi_conn):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

### Issue: Tests fail with `asyncio.run() cannot be called from a running event loop`

**Solution**: Use `pytest-asyncio` fixtures:

```python
# tests/conftest.py
import pytest

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

### Issue: PostgreSQL connection refused

**Solution**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Or with Docker
docker ps | grep postgres

# Check connection
psql -U contravento -d contravento -c "SELECT 1;"
```

### Issue: Permission denied on `/storage/profile_photos/`

**Solution**:
```bash
# Create directory and set permissions
mkdir -p backend/storage/profile_photos
chmod -R 755 backend/storage
```

---

## Performance Testing

### Load Testing with Locust

**1. Install Locust**:
```bash
pip install locust
```

**2. Create `locustfile.py`**:
```python
from locust import HttpUser, task, between

class ContraVentoUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Register and login
        response = self.client.post("/v1/auth/register", json={
            "username": f"user_{self.environment.runner.user_count}",
            "email": f"user{self.environment.runner.user_count}@example.com",
            "password": "TestPass123!"
        })

        # Login to get token
        response = self.client.post("/v1/auth/login", json={
            "login": f"user_{self.environment.runner.user_count}",
            "password": "TestPass123!"
        })
        self.token = response.json()["data"]["access_token"]

    @task(3)
    def get_profile(self):
        self.client.get(
            f"/v1/users/user_{self.environment.runner.user_count}/profile",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def get_stats(self):
        self.client.get(
            f"/v1/users/user_{self.environment.runner.user_count}/stats"
        )
```

**3. Run load test**:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

**4. Open Locust UI**: `http://localhost:8089`

**Success Criteria**:
- Authentication endpoints: <500ms p95 (SC-003)
- Profile queries: <200ms p95
- 100+ concurrent registrations without errors (SC-004)

---

## Next Steps

1. ✅ **Development environment set up** (SQLite or PostgreSQL)
2. ✅ **Tests running** (≥90% coverage)
3. ✅ **API accessible** (http://localhost:8000)

**Now you can**:
- Start implementing features following TDD workflow
- Read API contracts in `specs/001-user-profiles/contracts/`
- Review data model in `specs/001-user-profiles/data-model.md`
- Check implementation plan in `specs/001-user-profiles/plan.md`

**For questions or issues**:
- Check [plan.md](./plan.md) for architecture decisions
- Check [research.md](./research.md) for technology rationale
- Check [data-model.md](./data-model.md) for database schema

---

## Quick Reference

### Useful Commands

```bash
# Development
poetry shell                      # Activate virtual environment
uvicorn src.main:app --reload    # Start dev server
pytest --cov=src                  # Run tests with coverage

# Database
alembic upgrade head              # Apply migrations
alembic downgrade -1              # Rollback one migration
alembic revision --autogenerate   # Create new migration

# Code Quality
black src/ tests/                 # Format code
ruff check src/ tests/            # Lint code
mypy src/                         # Type checking

# Docker (PostgreSQL)
docker-compose up -d              # Start PostgreSQL
docker-compose down               # Stop PostgreSQL
docker-compose logs postgres      # View PostgreSQL logs
```

### Important URLs

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

### Database Files

- **SQLite Dev**: `backend/contravento_dev.db`
- **SQLite Test**: In-memory (`:memory:`)
- **PostgreSQL**: `postgresql://localhost:5432/contravento`

---

**Quickstart Status**: ✅ Complete - Ready for development
