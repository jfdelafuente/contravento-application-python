# Database Strategy - ContraVento Backend

Comprehensive documentation of the dual database strategy (SQLite + PostgreSQL) and database architecture.

**Audience**: Backend developers, DBAs, DevOps engineers

---

## Table of Contents

- [Overview](#overview)
- [Dual Database Strategy](#dual-database-strategy)
- [Database Configuration](#database-configuration)
- [Connection Management](#connection-management)
- [Migrations with Alembic](#migrations-with-alembic)
- [Dialect Differences](#dialect-differences)
- [Performance Optimizations](#performance-optimizations)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

ContraVento uses a **dual database strategy** where the **same codebase** runs on both **SQLite** (development/testing) and **PostgreSQL** (production).

### Why Dual Database?

**Benefits**:
- ✅ **Fast Development**: SQLite requires zero setup
- ✅ **Fast Tests**: In-memory SQLite for test isolation (<100ms per test)
- ✅ **Production-Ready**: PostgreSQL for scalability and concurrency
- ✅ **Same Codebase**: No environment-specific code branches
- ✅ **Portable**: Run anywhere (laptop, CI, production)

**Trade-offs**:
- ⚠️ Must test on both databases (CI runs PostgreSQL tests)
- ⚠️ Some PostgreSQL features unavailable (native UUID, arrays)
- ⚠️ Alembic migrations must support both dialects

**Verdict**: Excellent developer experience with production scalability.

---

## Dual Database Strategy

### Database Selection Matrix

| Environment | Database | URL Format | Use Case |
|-------------|----------|------------|----------|
| **Local Dev** | SQLite (file) | `sqlite+aiosqlite:///./contravento_dev.db` | Fast iteration |
| **Testing** | SQLite (memory) | `sqlite+aiosqlite:///:memory:` | Test isolation |
| **CI/CD** | SQLite (memory) | `sqlite+aiosqlite:///:memory:` | Fast CI runs |
| **Staging** | PostgreSQL 16 | `postgresql+asyncpg://user:pass@host/db` | Pre-production |
| **Production** | PostgreSQL 16 | `postgresql+asyncpg://user:pass@host/db` | High availability |

### Database Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  Development Phase                                           │
│  ────────────────                                            │
│  1. Write code on SQLite (fast, no Docker)                  │
│  2. Run tests on SQLite (in-memory, isolated)               │
│  3. Create Alembic migration (auto-generated)               │
│  4. Test migration on SQLite                                │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│  Pre-Production Phase                                        │
│  ───────────────────                                         │
│  5. Test on PostgreSQL (staging environment)                │
│  6. Run migration on PostgreSQL                             │
│  7. Validate schema matches SQLite                          │
└─────────────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────────────┐
│  Production Phase                                            │
│  ───────────────                                             │
│  8. Deploy to production PostgreSQL                         │
│  9. Run migrations with zero-downtime strategy              │
│  10. Monitor query performance                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Configuration

### Configuration via Environment Variables

```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite+aiosqlite:///./contravento_dev.db",
        description="Database connection URL"
    )

    @property
    def database_is_sqlite(self) -> bool:
        """Check if database is SQLite."""
        return self.database_url.startswith("sqlite")

    @property
    def database_is_postgresql(self) -> bool:
        """Check if database is PostgreSQL."""
        return self.database_url.startswith("postgresql")

settings = Settings()
```

### Environment-Specific URLs

**Local Development** (`.env`):
```bash
DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db
```

**Testing** (`pytest.ini`):
```bash
DATABASE_URL=sqlite+aiosqlite:///:memory:
```

**Production** (`.env.production`):
```bash
DATABASE_URL=postgresql+asyncpg://contravento:password@localhost:5432/contravento_prod
```

---

## Connection Management

### Engine Configuration

Connection settings adapt based on database type:

```python
# src/database.py
from sqlalchemy.ext.asyncio import create_async_engine

def _get_engine_kwargs() -> dict:
    """Get engine configuration based on database type."""
    if settings.database_is_sqlite:
        # SQLite configuration
        if ":memory:" in settings.database_url:
            # In-memory database (testing)
            return {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,  # Single connection, no pooling
                "echo": settings.debug,
            }
        else:
            # File-based database (development)
            return {
                "connect_args": {"check_same_thread": False},
                "poolclass": NullPool,  # No pooling for SQLite
                "echo": settings.debug,
            }
    else:
        # PostgreSQL configuration (production)
        return {
            "pool_size": 20,         # Base connections
            "max_overflow": 10,      # Additional under load
            "pool_pre_ping": True,   # Verify connections
            "pool_recycle": 3600,    # Recycle after 1 hour
            "echo": settings.debug,
        }

# Create async engine
engine = create_async_engine(settings.database_url, **_get_engine_kwargs())
```

### Session Management

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autocommit=False,        # Manual transaction control
    autoflush=False,         # Manual flush control
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide database session.

    Yields an async database session and ensures proper cleanup.
    Use with FastAPI Depends() for automatic session management.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Auto-rollback on error
            raise
        finally:
            await session.close()
```

### Usage in API

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db

@router.get("/trips")
async def get_trips(db: AsyncSession = Depends(get_db)):
    """
    Database session injected automatically.
    Committed on success, rolled back on error.
    """
    result = await db.execute(select(Trip))
    return result.scalars().all()
```

---

## Migrations with Alembic

### Alembic Setup

```ini
# alembic.ini
[alembic]
script_location = migrations
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s
sqlalchemy.url = driver://user:pass@localhost/dbname  # Overridden by env.py
```

### Creating Migrations

**Auto-generate migration**:
```bash
cd backend
poetry run alembic revision --autogenerate -m "Add trip_photos table"
```

**Alembic detects changes**:
- New models → CREATE TABLE
- Modified columns → ALTER TABLE
- New indexes → CREATE INDEX
- Renamed columns → (manual review required)

**Generated migration** (`migrations/versions/20240601_1430_add_trip_photos.py`):
```python
"""Add trip_photos table

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2024-06-01 14:30:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    """Apply migration."""
    # ✅ Works on both SQLite and PostgreSQL
    op.create_table(
        'trip_photos',
        sa.Column('photo_id', sa.String(length=36), nullable=False),
        sa.Column('trip_id', sa.String(length=36), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['trip_id'], ['trips.trip_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('photo_id')
    )

def downgrade():
    """Rollback migration."""
    op.drop_table('trip_photos')
```

### Running Migrations

**Apply all pending migrations**:
```bash
poetry run alembic upgrade head
```

**Rollback last migration**:
```bash
poetry run alembic downgrade -1
```

**View migration history**:
```bash
poetry run alembic history
```

**Check current revision**:
```bash
poetry run alembic current
```

---

## Dialect Differences

### UUID Handling

**PostgreSQL**: Native UUID type
**SQLite**: Store as TEXT (VARCHAR(36))

```python
# src/models/trip.py
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Trip(Base):
    __tablename__ = 'trips'

    # ✅ GOOD - Works on both databases
    trip_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    # ❌ BAD - PostgreSQL-only
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
```

### Array Columns

**PostgreSQL**: Native ARRAY type
**SQLite**: Store as JSON

```python
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import ARRAY

# ✅ GOOD - Portable
countries: Mapped[list[str]] = mapped_column(
    JSON,
    default=list
)

# ❌ BAD - PostgreSQL-only
countries: Mapped[list[str]] = mapped_column(
    ARRAY(String),
    default=list
)
```

### Foreign Key Constraints

**Critical**: SQLite has foreign keys **disabled by default**.

```python
# src/database.py
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record) -> None:
    """
    Enable foreign key constraints for SQLite.

    SQLite has foreign keys disabled by default. This handler enables them
    for every new connection to ensure referential integrity.
    """
    if "sqlite" in str(type(dbapi_conn)).lower():
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

**Verification**:
```python
# Check if foreign keys are enabled
result = await db.execute(text("PRAGMA foreign_keys"))
print(result.scalar())  # Should be 1 (enabled)
```

### Auto-Increment Behavior

**PostgreSQL**: SERIAL or IDENTITY
**SQLite**: AUTOINCREMENT

```python
# ✅ GOOD - Portable
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

# Database handles auto-increment automatically:
# - PostgreSQL: SERIAL
# - SQLite: INTEGER PRIMARY KEY AUTOINCREMENT
```

---

## Performance Optimizations

### Connection Pooling

**SQLite** (development):
- No pooling (`NullPool`)
- Single connection per file
- In-memory: `StaticPool` (single persistent connection)

**PostgreSQL** (production):
- Pool size: 20 base connections
- Max overflow: 10 additional connections
- Pre-ping: Verify connection health
- Recycle: Refresh connections after 1 hour

### Query Optimization

**Use eager loading** to prevent N+1 queries:

```python
# ✅ GOOD - Single query with joins
result = await db.execute(
    select(Trip)
    .options(
        joinedload(Trip.user),
        selectinload(Trip.photos),
        selectinload(Trip.tags)
    )
    .where(Trip.trip_id == trip_id)
)
trip = result.unique().scalar_one()

# ❌ BAD - N+1 queries
trip = await db.get(Trip, trip_id)
photos = trip.photos  # +1 query
tags = trip.tags      # +1 query
user = trip.user      # +1 query
```

### Indexes

**Automatic indexes** (SQLAlchemy creates these):
- Primary keys
- Foreign keys
- Unique constraints

**Manual indexes** for frequently queried columns:

```python
from sqlalchemy import Index

class Trip(Base):
    __tablename__ = 'trips'

    # Columns...
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id'))
    status: Mapped[TripStatus] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Composite index for common query
    __table_args__ = (
        Index('ix_trips_user_status_created', 'user_id', 'status', 'created_at'),
    )
```

**Query benefits**:
```python
# Fast query with composite index
result = await db.execute(
    select(Trip)
    .where(Trip.user_id == user_id)
    .where(Trip.status == TripStatus.PUBLISHED)
    .order_by(Trip.created_at.desc())
)
```

---

## Best Practices

### 1. Always Use Async

All database operations must be async:

```python
# ✅ GOOD - Async query
result = await db.execute(select(User))
users = result.scalars().all()

# ❌ BAD - Sync query (blocks event loop)
users = db.query(User).all()
```

### 2. Use ORM, Not Raw SQL

Avoid raw SQL to maintain database portability:

```python
# ✅ GOOD - ORM query
result = await db.execute(
    select(User).where(User.username == username)
)

# ❌ BAD - Raw SQL (dialect-specific)
result = await db.execute(
    text("SELECT * FROM users WHERE username = :username"),
    {"username": username}
)
```

### 3. Test on Both Databases

CI should run tests on PostgreSQL:

```yaml
# .github/workflows/tests.yml
jobs:
  test-sqlite:
    runs-on: ubuntu-latest
    env:
      DATABASE_URL: sqlite+aiosqlite:///:memory:
    steps:
      - run: poetry run pytest

  test-postgresql:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
    env:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost/test
    steps:
      - run: poetry run pytest
```

### 4. Use Transactions Wisely

Commit or rollback explicitly for complex operations:

```python
async def create_trip_with_stats(db: AsyncSession, user_id: str, data):
    try:
        # Step 1: Create trip
        trip = Trip(...)
        db.add(trip)
        await db.flush()

        # Step 2: Update stats
        stats = await StatsService(db).update_stats(user_id)

        # Both steps succeeded → commit
        await db.commit()
        return trip

    except Exception as e:
        # Any step failed → rollback
        await db.rollback()
        raise
```

### 5. Enable SQLite Foreign Keys

Always enable foreign keys for SQLite to match PostgreSQL behavior:

```python
# src/database.py
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if "sqlite" in str(type(dbapi_conn)).lower():
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

---

## Troubleshooting

### Issue: "FOREIGN KEY constraint failed" (SQLite)

**Cause**: Foreign keys not enabled.

**Solution**:
```python
# Verify foreign keys are enabled
result = await db.execute(text("PRAGMA foreign_keys"))
print(result.scalar())  # Should be 1

# If 0, check that event listener is registered
# See src/database.py: set_sqlite_pragma()
```

### Issue: "relation does not exist" (PostgreSQL)

**Cause**: Migrations not run.

**Solution**:
```bash
# Apply migrations
poetry run alembic upgrade head

# Check current revision
poetry run alembic current
```

### Issue: "database is locked" (SQLite)

**Cause**: Multiple processes accessing same SQLite file.

**Solution**:
```bash
# Option 1: Use PostgreSQL for multi-process scenarios
DATABASE_URL=postgresql+asyncpg://...

# Option 2: Increase SQLite timeout
SQLALCHEMY_POOL_TIMEOUT=30

# Option 3: Use in-memory database for tests
DATABASE_URL=sqlite+aiosqlite:///:memory:
```

### Issue: Slow queries

**Diagnostic**:
```python
# Enable SQL logging
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Check query execution time
import time
start = time.time()
result = await db.execute(query)
print(f"Query took {time.time() - start:.2f}s")
```

**Solutions**:
1. Add indexes for frequently queried columns
2. Use eager loading (joinedload, selectinload)
3. Paginate results (LIMIT/OFFSET)
4. Use denormalized counters for aggregates

---

## Related Documentation

- **[Backend Architecture](overview.md)** - Complete backend architecture guide
- **[Service Layer](services.md)** - Business logic patterns
- **[Security](security.md)** - Database security and SQL injection prevention
- **[Testing](../../testing/README.md)** - Testing with dual databases
- **[Deployment](../../deployment/README.md)** - Database deployment strategies

---

**Last Updated**: 2026-02-07
**Status**: ✅ Complete
**Databases Supported**: SQLite 3.x, PostgreSQL 16
