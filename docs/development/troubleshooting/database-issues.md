# Database Issues - Troubleshooting Guide

Comprehensive troubleshooting for database-related issues in ContraVento (SQLite and PostgreSQL).

**Audience**: Developers, DevOps engineers

---

## Table of Contents

- [SQLite Issues](#sqlite-issues)
- [PostgreSQL Issues](#postgresql-issues)
- [Migration Issues](#migration-issues)
- [Connection Issues](#connection-issues)
- [Data Integrity Issues](#data-integrity-issues)
- [Performance Issues](#performance-issues)

---

## SQLite Issues

### Database Locked Error

**Error**:
```
sqlite3.OperationalError: database is locked
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked
```

**Cause**: Another process has exclusive write lock on database file.

**Solution**:

**1. Stop all backend instances**:
```bash
# Kill all uvicorn processes
pkill -f uvicorn

# Verify no processes using database
lsof backend/contravento_dev.db
```

**2. Check for zombie connections**:
```python
# In Python shell
import sqlite3
conn = sqlite3.connect('backend/contravento_dev.db')
conn.execute('PRAGMA busy_timeout = 5000')  # Wait 5s instead of failing immediately
conn.close()
```

**3. Reset database** (if persists):
```bash
./run-local-dev.sh --reset
```

**Prevention**:
- Use connection pooling (already configured in `database.py`)
- Always close database sessions properly:
  ```python
  async with AsyncSessionLocal() as db:
      # Operations
      pass  # Session auto-closed
  ```
- Don't run multiple backend instances on same SQLite database

---

### Foreign Key Constraint Violations

**Error**:
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) FOREIGN KEY constraint failed
```

**Cause**: Foreign key constraint violated (referencing non-existent row).

**Solution**:

**1. Verify foreign keys are enabled**:
```python
# Should be automatic in database.py
async def get_async_session():
    async with AsyncSessionLocal() as session:
        # Enable foreign keys (SQLite specific)
        if "sqlite" in settings.database_url:
            await session.execute(text("PRAGMA foreign_keys=ON"))
        yield session
```

**2. Check relationship exists**:
```bash
cd backend

# Example: Verify trip exists before adding photo
poetry run python -c "
from src.database import AsyncSessionLocal
from src.models.trip import Trip
from sqlalchemy import select
import asyncio

async def check_trip(trip_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Trip).where(Trip.trip_id == trip_id))
        trip = result.scalar_one_or_none()
        print(f'Trip exists: {trip is not None}')

asyncio.run(check_trip('YOUR_TRIP_ID'))
"
```

**3. Common scenarios**:

**Deleting user with trips**:
```python
# ❌ WRONG - Violates FK constraint
await db.delete(user)  # User has trips → FK violation

# ✅ CORRECT - Cascade delete or delete trips first
user = await db.get(User, user_id)
for trip in user.trips:
    await db.delete(trip)
await db.delete(user)
```

**Creating trip photo for non-existent trip**:
```python
# ❌ WRONG
photo = TripPhoto(trip_id="invalid-id", url="...")
db.add(photo)  # FK violation

# ✅ CORRECT - Verify trip exists
trip = await db.get(Trip, trip_id)
if not trip:
    raise HTTPException(404, "Trip not found")
photo = TripPhoto(trip_id=trip.trip_id, url="...")
```

---

### SQLite File Corrupted

**Error**:
```
sqlite3.DatabaseError: database disk image is malformed
sqlite3.DatabaseError: file is not a database
```

**Cause**: Database file corrupted (power loss, disk full, forced shutdown).

**Solution**:

**1. Try to recover**:
```bash
cd backend

# Backup corrupted database
cp contravento_dev.db contravento_dev.db.corrupted

# Try SQLite recovery
sqlite3 contravento_dev.db ".recover" | sqlite3 contravento_dev_recovered.db

# If successful, replace
mv contravento_dev_recovered.db contravento_dev.db
```

**2. Reset database** (if recovery fails):
```bash
# Delete corrupted database
rm backend/contravento_dev.db

# Recreate
./run-local-dev.sh --setup
```

**Prevention**:
- Use SQLite WAL mode (already enabled in `database.py`)
- Regular backups during development
- Don't kill processes forcefully (`kill -9`) - use `Ctrl+C`

---

### SQLite Performance Degradation

**Symptoms**:
- Queries slow down over time
- INSERT/UPDATE operations take seconds
- Database file size grows excessively

**Cause**: Database fragmentation or lack of indexes.

**Solution**:

**1. Vacuum database** (defragment):
```bash
cd backend

# Compact and optimize
sqlite3 contravento_dev.db "VACUUM;"

# Analyze query planner statistics
sqlite3 contravento_dev.db "ANALYZE;"
```

**2. Check indexes**:
```bash
# List indexes
sqlite3 contravento_dev.db ".indexes"

# Check if specific index exists
sqlite3 contravento_dev.db "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_trips_user_id';"
```

**3. Add missing indexes** (via migration):
```python
# migrations/versions/add_indexes.py
def upgrade():
    op.create_index('idx_trips_user_id', 'trips', ['user_id'])
    op.create_index('idx_trips_status', 'trips', ['status'])
```

---

## PostgreSQL Issues

### Connection Refused

**Error**:
```
psycopg2.OperationalError: could not connect to server: Connection refused
sqlalchemy.exc.OperationalError: could not connect to server
```

**Cause**: PostgreSQL not running or wrong connection parameters.

**Solution**:

**1. Check PostgreSQL is running** (Docker):
```bash
# List running containers
docker ps | grep postgres

# Should show:
# postgres:5432->5432/tcp

# If not running, start Docker environment
./deploy.sh local-minimal
```

**2. Test connection**:
```bash
# PostgreSQL client (if installed)
psql -h localhost -U contravento -d contravento_dev

# Or via Docker
docker exec -it contravento-postgres-1 psql -U contravento -d contravento_dev
```

**3. Verify connection string** (in `.env`):
```bash
# PostgreSQL (Docker)
DATABASE_URL=postgresql+asyncpg://contravento:password@localhost:5432/contravento_dev

# Components:
# - Driver: postgresql+asyncpg (async driver)
# - User: contravento
# - Password: password
# - Host: localhost (or container name if running in Docker network)
# - Port: 5432
# - Database: contravento_dev
```

**4. Check firewall/ports**:
```bash
# Verify port 5432 is accessible
telnet localhost 5432

# Or with netcat
nc -zv localhost 5432
```

---

### Authentication Failed for User

**Error**:
```
psycopg2.OperationalError: FATAL:  password authentication failed for user "contravento"
```

**Cause**: Wrong password or user doesn't exist.

**Solution**:

**1. Check Docker Compose environment**:
```yaml
# docker-compose.yml
services:
  postgres:
    environment:
      POSTGRES_USER: contravento
      POSTGRES_PASSWORD: password
      POSTGRES_DB: contravento_dev
```

**2. Verify credentials match `.env`**:
```bash
# backend/.env.local-minimal
DATABASE_URL=postgresql+asyncpg://contravento:password@localhost:5432/contravento_dev
#                                  ↑         ↑
#                                  User      Password (must match docker-compose.yml)
```

**3. Recreate PostgreSQL user**:
```bash
# Connect as postgres superuser
docker exec -it contravento-postgres-1 psql -U postgres

# Drop and recreate user
DROP USER IF EXISTS contravento;
CREATE USER contravento WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE contravento_dev TO contravento;
```

---

### PostgreSQL Container Won't Start

**Error**:
```
ERROR: for postgres  Cannot start service postgres: driver failed programming external connectivity
```

**Cause**: Port 5432 already in use (another PostgreSQL instance running).

**Solution**:

**1. Find process using port 5432**:
```bash
# Linux/Mac
lsof -i:5432

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5432).OwningProcess
```

**2. Stop conflicting PostgreSQL**:
```bash
# Stop system PostgreSQL (if running)
sudo systemctl stop postgresql  # Linux
brew services stop postgresql   # Mac

# Or kill process
kill -9 <PID>
```

**3. Use alternative port** (if needed):
```yaml
# docker-compose.yml
services:
  postgres:
    ports:
      - "5433:5432"  # Host:Container (use 5433 on host)
```

Then update `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://contravento:password@localhost:5433/contravento_dev
```

---

### PostgreSQL Disk Full

**Error**:
```
ERROR:  could not write block 12345 of temporary file: No space left on device
```

**Cause**: Docker volume or host disk full.

**Solution**:

**1. Check Docker disk usage**:
```bash
docker system df

# Example output:
# Images          15        1.2GB
# Containers      5         500MB
# Local Volumes   10        8.5GB  ← Large volumes
# Build Cache     20        3.2GB
```

**2. Clean up Docker**:
```bash
# Remove unused containers, images, volumes
docker system prune --volumes

# Or clean specific volume
docker volume rm contravento_postgres_data
```

**3. Check host disk**:
```bash
df -h
```

**4. Recreate PostgreSQL container**:
```bash
./deploy.sh local-minimal --restart
```

---

## Migration Issues

### Migration Already Applied

**Error**:
```
alembic.util.exc.CommandError: Target database is not up to date
ERROR: Can't locate revision identified by 'abc123'
```

**Cause**: Migration history out of sync.

**Solution**:

**1. Check current migration**:
```bash
cd backend
poetry run alembic current

# Example output:
# abc123def456 (head)
```

**2. Check migration history**:
```bash
poetry run alembic history

# Should show linear history:
# abc123 -> def456 -> ghi789 (head)
```

**3. Stamp to specific revision** (if out of sync):
```bash
# Force alembic to think migration is at specific revision
poetry run alembic stamp head

# Or specific revision
poetry run alembic stamp abc123def456
```

**4. Reset migrations** (development only):
```bash
# SQLite - delete database and recreate
rm backend/contravento_dev.db
poetry run alembic upgrade head

# PostgreSQL - drop all tables
docker exec -it contravento-postgres-1 psql -U contravento -d contravento_dev -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
poetry run alembic upgrade head
```

---

### Migration Fails: Column Already Exists

**Error**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) duplicate column name: created_at
psycopg2.errors.DuplicateColumn: column "created_at" of relation "users" already exists
```

**Cause**: Migration trying to add column that already exists.

**Solution**:

**1. Check if column exists**:
```bash
# SQLite
sqlite3 backend/contravento_dev.db ".schema users"

# PostgreSQL
docker exec -it contravento-postgres-1 psql -U contravento -d contravento_dev -c "\d users"
```

**2. Make migration idempotent**:
```python
# migrations/versions/add_created_at.py
def upgrade():
    # Check if column exists before adding (PostgreSQL)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='users' AND column_name='created_at'
            ) THEN
                ALTER TABLE users ADD COLUMN created_at TIMESTAMP;
            END IF;
        END $$;
    """)

    # SQLite - more complex, use try/except in Python
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.exc import OperationalError

    try:
        op.add_column('users', sa.Column('created_at', sa.DateTime))
    except OperationalError as e:
        if "duplicate column" not in str(e).lower():
            raise
```

**3. Skip failing migration** (development):
```bash
# Downgrade one revision
poetry run alembic downgrade -1

# Edit migration file to fix issue

# Retry upgrade
poetry run alembic upgrade head
```

---

### Migration Fails: Table Doesn't Exist

**Error**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
```

**Cause**: Migration references table not yet created or wrong order.

**Solution**:

**1. Check migration order**:
```bash
poetry run alembic history

# Ensure migrations in correct order:
# 001_create_users.py (creates users table)
# 002_add_email_to_users.py (depends on users existing)
```

**2. Fix migration dependency**:
```python
# migrations/versions/002_add_email_to_users.py
"""Add email to users

Revision ID: def456
Revises: abc123  ← Must reference previous migration (001_create_users.py)
"""

# Alembic uses "Revises" to determine order
revision = 'def456'
down_revision = 'abc123'  # ← Must be correct
```

**3. Recreate migration with correct order**:
```bash
# Delete incorrect migration file
rm backend/migrations/versions/002_add_email_to_users.py

# Recreate with autogenerate (ensures correct order)
poetry run alembic revision --autogenerate -m "Add email to users"
```

---

### Autogenerate Doesn't Detect Changes

**Symptoms**:
- Changed model but `alembic revision --autogenerate` creates empty migration
- Migration doesn't include expected column changes

**Cause**: Models not imported or Alembic can't see changes.

**Solution**:

**1. Verify models imported** (in `src/database.py` or `migrations/env.py`):
```python
# migrations/env.py
from src.models.user import User
from src.models.trip import Trip, TripPhoto, TripLocation
from src.models.stats import UserStats
from src.models.gpx import GPXFile
# Import ALL models

target_metadata = Base.metadata
```

**2. Check model changes**:
```python
# Example: Adding column to User model
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    new_column = Column(String)  # ← New column
```

**3. Regenerate migration**:
```bash
# Clear Python cache (sometimes caches old models)
find . -type d -name __pycache__ -exec rm -r {} +

# Regenerate
poetry run alembic revision --autogenerate -m "Add new_column to users"

# Review generated migration
cat backend/migrations/versions/REVISION_ID_add_new_column_to_users.py
```

**4. Manual migration** (if autogenerate fails):
```bash
poetry run alembic revision -m "Add new_column to users"

# Edit generated file manually
# migrations/versions/REVISION_ID_add_new_column_to_users.py
def upgrade():
    op.add_column('users', sa.Column('new_column', sa.String()))

def downgrade():
    op.drop_column('users', 'new_column')
```

---

## Connection Issues

### Connection Pool Timeout

**Error**:
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 20 overflow 10 reached, connection timed out
```

**Cause**: Too many concurrent connections, pool exhausted.

**Solution**:

**1. Check pool configuration**:
```python
# src/database.py
engine = create_async_engine(
    settings.database_url,
    echo=settings.sql_echo,
    pool_size=20,  # Base pool size
    max_overflow=10,  # Additional connections beyond pool_size
    pool_timeout=30,  # Seconds to wait before timeout
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Total max connections = pool_size + max_overflow = 30
```

**2. Increase pool size** (if needed):
```python
# For high-traffic scenarios
engine = create_async_engine(
    settings.database_url,
    pool_size=50,  # Increase from 20
    max_overflow=20,  # Increase from 10
)
```

**3. Find connection leaks**:
```python
# Add logging to track connections
import logging
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)

# Look for unclosed sessions in code
# ❌ WRONG - Session never closed
async def bad_function():
    db = AsyncSessionLocal()
    result = await db.execute(select(User))
    return result  # Session leaked!

# ✅ CORRECT - Auto-close with context manager
async def good_function():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        return result  # Session closed
```

**4. Restart to clear pool**:
```bash
./run_backend.sh restart
```

---

### SSL Connection Error (PostgreSQL)

**Error**:
```
psycopg2.OperationalError: SSL error: certificate verify failed
asyncpg.exceptions.InvalidPasswordError: SSL connection has been closed unexpectedly
```

**Cause**: PostgreSQL requires SSL but client not configured.

**Solution**:

**Development (disable SSL)**:
```bash
# .env
DATABASE_URL=postgresql+asyncpg://contravento:password@localhost:5432/contravento_dev?ssl=disable
```

**Production (enable SSL)**:
```bash
# .env
DATABASE_URL=postgresql+asyncpg://contravento:password@db.example.com:5432/contravento?ssl=require

# With custom CA certificate
DATABASE_URL=postgresql+asyncpg://contravento:password@db.example.com:5432/contravento?ssl=require&sslmode=verify-ca&sslrootcert=/path/to/ca.crt
```

---

## Data Integrity Issues

### Duplicate Key Violation

**Error**:
```
sqlite3.IntegrityError: UNIQUE constraint failed: users.username
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "users_username_key"
```

**Cause**: Trying to insert row with duplicate unique column value.

**Solution**:

**1. Check existing data**:
```bash
cd backend

# SQLite
sqlite3 contravento_dev.db "SELECT username FROM users WHERE username='testuser';"

# PostgreSQL
docker exec -it contravento-postgres-1 psql -U contravento -d contravento_dev -c "SELECT username FROM users WHERE username='testuser';"
```

**2. Handle duplicates in code**:
```python
# ❌ WRONG - No duplicate check
user = User(username="testuser", email="test@example.com")
db.add(user)
await db.commit()  # May raise IntegrityError

# ✅ CORRECT - Check first
result = await db.execute(select(User).where(User.username == "testuser"))
existing = result.scalar_one_or_none()
if existing:
    raise HTTPException(400, "Username already exists")

user = User(username="testuser", email="test@example.com")
db.add(user)
await db.commit()
```

**3. Handle race conditions**:
```python
# Use try/except for concurrent inserts
from sqlalchemy.exc import IntegrityError

try:
    user = User(username="testuser", email="test@example.com")
    db.add(user)
    await db.commit()
except IntegrityError as e:
    await db.rollback()
    if "username" in str(e):
        raise HTTPException(400, "Username already exists")
    raise
```

---

### Orphaned Records

**Symptoms**:
- Trip photos without trip (trip deleted)
- User stats without user
- Foreign key references non-existent rows

**Cause**: Missing cascade delete or manual deletion.

**Solution**:

**1. Find orphaned records**:
```bash
# SQLite
sqlite3 contravento_dev.db "
SELECT tp.photo_id, tp.trip_id
FROM trip_photos tp
LEFT JOIN trips t ON tp.trip_id = t.trip_id
WHERE t.trip_id IS NULL;
"

# PostgreSQL
docker exec -it contravento-postgres-1 psql -U contravento -d contravento_dev -c "
SELECT tp.photo_id, tp.trip_id
FROM trip_photos tp
LEFT JOIN trips t ON tp.trip_id = t.trip_id
WHERE t.trip_id IS NULL;
"
```

**2. Clean up orphans**:
```bash
# Delete orphaned trip photos
sqlite3 contravento_dev.db "
DELETE FROM trip_photos
WHERE trip_id NOT IN (SELECT trip_id FROM trips);
"
```

**3. Add cascade delete** (via migration):
```python
# migrations/versions/add_cascade_delete.py
def upgrade():
    # Drop existing foreign key
    op.drop_constraint('fk_trip_photos_trip_id', 'trip_photos', type_='foreignkey')

    # Recreate with cascade
    op.create_foreign_key(
        'fk_trip_photos_trip_id',
        'trip_photos', 'trips',
        ['trip_id'], ['trip_id'],
        ondelete='CASCADE'  # Auto-delete photos when trip deleted
    )
```

**4. Use ORM cascade** (in models):
```python
# src/models/trip.py
class Trip(Base):
    __tablename__ = "trips"

    trip_id = Column(String, primary_key=True)

    # Cascade delete photos when trip deleted
    photos = relationship(
        "TripPhoto",
        back_populates="trip",
        cascade="all, delete-orphan"  # ← Auto-delete
    )
```

---

## Performance Issues

### Slow Queries (N+1 Problem)

**Symptoms**:
- API endpoint takes seconds to respond
- Logs show hundreds of identical queries
- Each trip triggers separate query for photos

**Cause**: N+1 query problem (not using eager loading).

**Solution**:

**1. Identify N+1 with logging**:
```python
# Enable SQL query logging
# src/database.py
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Log all queries
)
```

**2. Use eager loading**:
```python
# ❌ WRONG - N+1 queries (1 for trips, N for photos)
result = await db.execute(select(Trip))
trips = result.scalars().all()
for trip in trips:
    print(trip.photos)  # Triggers separate query per trip!

# ✅ CORRECT - Single query with JOIN
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Trip).options(selectinload(Trip.photos))
)
trips = result.scalars().all()
for trip in trips:
    print(trip.photos)  # No additional queries!
```

**3. Common eager loading patterns**:
```python
# Load multiple relationships
result = await db.execute(
    select(Trip).options(
        selectinload(Trip.photos),
        selectinload(Trip.locations),
        selectinload(Trip.tags)
    )
)

# Nested relationships
result = await db.execute(
    select(User).options(
        selectinload(User.trips).selectinload(Trip.photos)
    )
)
```

---

### Missing Indexes

**Symptoms**:
- Slow queries on large tables
- Filter/sort operations take seconds
- Database CPU usage high

**Cause**: Queries on columns without indexes.

**Solution**:

**1. Identify slow queries**:
```bash
# SQLite - Enable query profiling
sqlite3 contravento_dev.db "
PRAGMA query_only = ON;
EXPLAIN QUERY PLAN SELECT * FROM trips WHERE user_id = 'user123';
"

# Look for "SCAN TABLE" (bad) vs "SEARCH TABLE USING INDEX" (good)
```

**2. Add indexes**:
```python
# Via migration
def upgrade():
    op.create_index('idx_trips_user_id', 'trips', ['user_id'])
    op.create_index('idx_trips_status', 'trips', ['status'])
    op.create_index('idx_trip_photos_trip_id', 'trip_photos', ['trip_id'])

# Composite index for combined filters
def upgrade():
    op.create_index(
        'idx_trips_user_status',
        'trips',
        ['user_id', 'status']
    )
```

**3. Common indexes to add**:
```python
# Foreign keys (always index!)
idx_trips_user_id (trips.user_id)
idx_trip_photos_trip_id (trip_photos.trip_id)
idx_user_stats_user_id (user_stats.user_id)

# Filtered columns
idx_trips_status (trips.status)
idx_trips_is_private (trips.is_private)
idx_users_is_verified (users.is_verified)

# Sorted columns
idx_trips_created_at (trips.created_at)
idx_trips_start_date (trips.start_date)

# Unique constraints (automatically indexed)
users.username
users.email
trips.trip_id
```

---

## Related Documentation

- **[Getting Started - Database Setup](../getting-started.md#database-setup)** - Initial setup
- **[Backend Architecture - Database](../../architecture/backend/database.md)** - Dual DB strategy
- **[Scripts Overview - Dev Tools](../scripts/overview.md#development-tools)** - Database scripts
- **[Common Issues](common-issues.md)** - General troubleshooting

---

## Advanced Diagnostics

### Database Health Check Script

Create `scripts/dev-tools/check_db_health.py`:

```python
"""Database health check and diagnostics."""

import asyncio
from sqlalchemy import select, func, text
from src.database import AsyncSessionLocal
from src.models.trip import Trip
from src.models.user import User

async def check_database_health():
    """Run comprehensive database health checks."""
    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("DATABASE HEALTH CHECK")
        print("=" * 60)

        # Test connection
        try:
            await db.execute(select(func.count(User.id)))
            print("✓ Database connection: OK")
        except Exception as e:
            print(f"✗ Database connection: FAILED - {e}")
            return

        # Count records
        user_count = (await db.execute(select(func.count(User.id)))).scalar()
        trip_count = (await db.execute(select(func.count(Trip.trip_id)))).scalar()

        print(f"✓ Users: {user_count}")
        print(f"✓ Trips: {trip_count}")

        # Check for orphaned records
        orphaned_photos = (await db.execute(text("""
            SELECT COUNT(*)
            FROM trip_photos tp
            LEFT JOIN trips t ON tp.trip_id = t.trip_id
            WHERE t.trip_id IS NULL
        """))).scalar()

        if orphaned_photos > 0:
            print(f"⚠ Orphaned photos: {orphaned_photos} (consider cleanup)")
        else:
            print("✓ No orphaned records")

        # Check indexes (PostgreSQL only)
        if "postgresql" in str(db.get_bind().url):
            indexes = (await db.execute(text("""
                SELECT tablename, indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))).fetchall()

            print(f"✓ Indexes: {len(indexes)}")

        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_database_health())
```

**Usage**:
```bash
cd backend
poetry run python scripts/dev-tools/check_db_health.py
```

---

**Last Updated**: 2026-02-07
**Databases Supported**: SQLite (development), PostgreSQL (production)
**Issue Categories**: 6 (SQLite, PostgreSQL, Migrations, Connections, Integrity, Performance)
