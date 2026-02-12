# Database Management Guide

**Migrations, seeds, backups, and database administration**

**Purpose**: Complete guide for managing ContraVento databases across all deployment modes

---

## Table of Contents

1. [Overview](#overview)
2. [Alembic Migrations](#alembic-migrations)
3. [Seed Scripts](#seed-scripts)
4. [Backup & Restore](#backup--restore)
5. [PostgreSQL vs SQLite](#postgresql-vs-sqlite)
6. [Common Operations](#common-operations)
7. [Troubleshooting](#troubleshooting)

---

## Overview

ContraVento uses **SQLAlchemy 2.0** (async ORM) with **Alembic** for database migrations. The application supports both **PostgreSQL** (production) and **SQLite** (development).

### Database Modes

| Mode | Database | Use Case | Migrations |
|------|----------|----------|------------|
| **local-dev** | SQLite (file) | Daily development | Auto-applied on setup |
| **local-minimal** | PostgreSQL (Docker) | PostgreSQL testing | Manual or auto |
| **local-full** | PostgreSQL (Docker) | Full stack dev | Manual or auto |
| **test** | SQLite (in-memory) | Automated tests | Auto-applied |
| **staging** | PostgreSQL (server) | Pre-production | Manual |
| **production** | PostgreSQL (server) | Live users | Manual (carefully!) |

---

## Alembic Migrations

### What are Migrations?

**Migrations** are version-controlled database schema changes. Each migration contains:
- **Upgrade**: Apply schema change (add table, column, index, etc.)
- **Downgrade**: Revert schema change (rollback)

**Benefits**:
- Version control for database schema
- Reproducible across environments
- Reversible changes
- Team collaboration (no manual SQL)

---

### Migration Workflow

#### 1. Create Migration

**After changing SQLAlchemy models**, generate a migration:

```bash
cd backend

# Auto-generate migration from model changes
poetry run alembic revision --autogenerate -m "Add gpx_files table"

# Or create empty migration (for data migrations)
poetry run alembic revision -m "Seed initial achievements"
```

**Output**:
```
Generating migrations/versions/20240206_1430_abc123_add_gpx_files_table.py
```

**File structure**:
```python
"""Add gpx_files table

Revision ID: abc123def456
Revises: xyz789
Create Date: 2024-02-06 14:30:00
"""

def upgrade() -> None:
    """Apply schema change"""
    op.create_table('gpx_files',
        sa.Column('gpx_file_id', sa.UUID(), nullable=False),
        sa.Column('trip_id', sa.UUID(), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('gpx_file_id')
    )

def downgrade() -> None:
    """Revert schema change"""
    op.drop_table('gpx_files')
```

---

#### 2. Review Migration

**CRITICAL**: Always review auto-generated migrations before applying!

**Check for**:
- Correct table/column names
- Proper data types (UUID, String, Integer, etc.)
- Foreign key constraints
- Indexes on frequently queried columns
- Default values
- NOT NULL constraints

**Common issues**:
```python
# ❌ BAD - Missing index on foreign key
sa.Column('user_id', sa.UUID(), nullable=False)

# ✅ GOOD - Add index for query performance
sa.Column('user_id', sa.UUID(), nullable=False, index=True)
```

---

#### 3. Apply Migration

**Development**:
```bash
cd backend
poetry run alembic upgrade head
```

**Docker**:
```bash
# From host
docker-compose exec backend poetry run alembic upgrade head

# Inside container
docker exec -it contravento-backend-local poetry run alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Running upgrade -> abc123, Add gpx_files table
```

---

#### 4. Rollback Migration

**If migration fails or needs to be reverted**:

```bash
# Rollback last migration
poetry run alembic downgrade -1

# Rollback to specific revision
poetry run alembic downgrade abc123def456

# Rollback all migrations (⚠️ destroys schema!)
poetry run alembic downgrade base
```

**Example**:
```bash
# Apply migration
poetry run alembic upgrade head
# ERROR: column already exists

# Rollback
poetry run alembic downgrade -1

# Fix migration file
# Re-apply
poetry run alembic upgrade head
```

---

#### 5. View Migration History

```bash
# View all migrations
poetry run alembic history

# View verbose (shows file paths)
poetry run alembic history --verbose

# View current revision
poetry run alembic current
```

**Example output**:
```
abc123def456 -> xyz789uvw012 (head), Add gpx_files table
xyz789uvw012 -> mno345pqr678, Add trip_locations table
mno345pqr678 -> stu901vwx234, Create users table
<base> -> stu901vwx234, Initial schema
```

---

### Migration Best Practices

#### 1. One Concept Per Migration

```bash
# ✅ GOOD - Single focused migration
poetry run alembic revision -m "Add email_verified column to users"

# ❌ BAD - Multiple unrelated changes
poetry run alembic revision -m "Add columns, fix typos, add indexes"
```

---

#### 2. Always Test Migrations

```bash
# Test upgrade
poetry run alembic upgrade head

# Test downgrade
poetry run alembic downgrade -1

# Re-apply
poetry run alembic upgrade head
```

**Why**: Ensures migration is reversible

---

#### 3. Add Indexes for Foreign Keys

```python
# ✅ GOOD - Index on foreign key
sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.user_id'), index=True)

# ❌ BAD - No index (slow joins)
sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.user_id'))
```

---

#### 4. Use Batch Operations for SQLite

```python
# ✅ GOOD - Works on SQLite
with op.batch_alter_table('users') as batch_op:
    batch_op.add_column(sa.Column('email_verified', sa.Boolean(), default=False))

# ❌ BAD - Fails on SQLite (doesn't support ALTER TABLE fully)
op.add_column('users', sa.Column('email_verified', sa.Boolean(), default=False))
```

---

#### 5. Data Migrations

**For migrating data** (not just schema):

```python
def upgrade() -> None:
    """Migrate existing trips to new schema"""
    # First change schema
    op.add_column('trips', sa.Column('status', sa.String(20), default='PUBLISHED'))

    # Then migrate data
    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE trips SET status = 'PUBLISHED' WHERE is_draft = FALSE")
    )
    conn.execute(
        sa.text("UPDATE trips SET status = 'DRAFT' WHERE is_draft = TRUE")
    )

    # Finally drop old column
    op.drop_column('trips', 'is_draft')
```

---

## Seed Scripts

### Overview

**Seed scripts** populate the database with initial or test data.

**Located in**: `backend/scripts/seeding/` and `backend/scripts/user-mgmt/`

---

### User Management Scripts

#### Create Admin User

**Purpose**: Create the first admin account

**File**: `scripts/user-mgmt/create_admin.py`

**Usage**:
```bash
cd backend

# Create default admin (admin / AdminPass123!)
poetry run python scripts/user-mgmt/create_admin.py

# Create custom admin
poetry run python scripts/user-mgmt/create_admin.py \
  --username myadmin \
  --email admin@mycompany.com \
  --password "MySecurePass123!"
```

**Default credentials**:
- **Username**: `admin`
- **Email**: `admin@contravento.com`
- **Password**: `AdminPass123!`
- **Role**: ADMIN (verified)

---

#### Create Verified User

**Purpose**: Create test users with verified emails

**File**: `scripts/user-mgmt/create_verified_user.py`

**Usage**:
```bash
cd backend

# Create default test users (testuser, maria_garcia)
poetry run python scripts/user-mgmt/create_verified_user.py

# Create custom user
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username john \
  --email john@example.com \
  --password "SecurePass123!"

# Verify existing user's email
poetry run python scripts/user-mgmt/create_verified_user.py \
  --verify-email test@example.com
```

**Default users**:
- `testuser` / `test@example.com` / `TestPass123!`
- `maria_garcia` / `maria@example.com` / `SecurePass456!`

---

#### Promote User to Admin

**Purpose**: Grant admin role to existing user

**File**: `scripts/user-mgmt/promote_to_admin.py`

**Usage**:
```bash
cd backend

# Promote user to admin
poetry run python scripts/user-mgmt/promote_to_admin.py --username testuser

# Demote admin to regular user
poetry run python scripts/user-mgmt/promote_to_admin.py --username admin --demote
```

---

### Data Seeding Scripts

#### Seed Cycling Types

**Purpose**: Load cycling types from YAML config

**File**: `scripts/seeding/seed_cycling_types.py`

**Usage**:
```bash
cd backend

# Load cycling types from config/cycling_types.yaml
poetry run python scripts/seeding/seed_cycling_types.py

# Force update existing types
poetry run python scripts/seeding/seed_cycling_types.py --force

# List current types
poetry run python scripts/seeding/seed_cycling_types.py --list
```

**Config file**: `config/cycling_types.yaml`

```yaml
cycling_types:
  - code: bikepacking
    display_name: Bikepacking
    description: Viajes de varios días con equipaje
    is_active: true
  - code: road
    display_name: Carretera
    description: Ciclismo en asfalto
    is_active: true
```

---

#### Seed Achievements

**Purpose**: Load cycling achievements

**File**: `scripts/seeding/seed_achievements.py`

**Usage**:
```bash
cd backend
poetry run python scripts/seeding/seed_achievements.py
```

**Creates achievements**:
- "Primera Ruta" (complete first trip)
- "100km" (ride 100km total)
- "Explorador" (visit 5 different countries)

---

#### Initialize Dev Data

**Purpose**: One-command setup for development

**File**: `scripts/seeding/init_dev_data.py`

**Usage**:
```bash
cd backend
poetry run python scripts/seeding/init_dev_data.py
```

**What it does**:
1. Creates admin user
2. Creates test users
3. Seeds cycling types
4. Seeds achievements
5. (Optional) Creates sample trips

---

## Backup & Restore

### PostgreSQL Backup

#### Full Database Backup

```bash
# From host (Docker)
docker exec contravento-db-local pg_dump -U contravento -d contravento > backup_$(date +%Y%m%d).sql

# From server (direct PostgreSQL)
pg_dump -U contravento -h localhost -d contravento > backup_$(date +%Y%m%d).sql

# Compressed backup (recommended for large DBs)
pg_dump -U contravento -d contravento | gzip > backup_$(date +%Y%m%d).sql.gz
```

---

#### Schema-Only Backup

```bash
# Backup only schema (no data)
pg_dump -U contravento -d contravento --schema-only > schema_$(date +%Y%m%d).sql
```

---

#### Data-Only Backup

```bash
# Backup only data (no schema)
pg_dump -U contravento -d contravento --data-only > data_$(date +%Y%m%d).sql
```

---

#### Specific Table Backup

```bash
# Backup single table
pg_dump -U contravento -d contravento -t users > users_backup.sql

# Backup multiple tables
pg_dump -U contravento -d contravento -t users -t trips > users_trips_backup.sql
```

---

### PostgreSQL Restore

```bash
# Drop existing database (⚠️ destructive!)
docker exec -it contravento-db-local psql -U postgres -c "DROP DATABASE contravento;"
docker exec -it contravento-db-local psql -U postgres -c "CREATE DATABASE contravento;"

# Restore from backup
docker exec -i contravento-db-local psql -U contravento -d contravento < backup_20240206.sql

# Restore from compressed backup
gunzip -c backup_20240206.sql.gz | docker exec -i contravento-db-local psql -U contravento -d contravento
```

---

### SQLite Backup

#### Simple File Copy

```bash
# Backup SQLite database (while app is stopped)
cp backend/contravento_dev.db backend/contravento_dev.db.backup_$(date +%Y%m%d)

# Verify backup
ls -lh backend/contravento_dev.db*
```

---

#### Online Backup (While App Running)

```bash
# Use SQLite's online backup API
sqlite3 backend/contravento_dev.db ".backup backend/contravento_dev_backup.db"
```

---

### SQLite Restore

```bash
# Stop app first!
# Then restore from backup
cp backend/contravento_dev.db.backup_20240206 backend/contravento_dev.db

# Verify
sqlite3 backend/contravento_dev.db "SELECT COUNT(*) FROM users;"
```

---

### Automated Backup Script

**Create**: `scripts/backup_database.sh`

```bash
#!/bin/bash
# Automated daily backups

BACKUP_DIR="/backups/contravento"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker exec contravento-db-local pg_dump -U contravento -d contravento | \
  gzip > "$BACKUP_DIR/contravento_$DATE.sql.gz"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "contravento_*.sql.gz" -mtime +30 -delete

echo "Backup completed: contravento_$DATE.sql.gz"
```

**Schedule with cron**:
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_database.sh
```

---

## PostgreSQL vs SQLite

### Key Differences

| Feature | PostgreSQL | SQLite | Impact |
|---------|------------|--------|--------|
| **UUID Type** | Native `UUID` | `TEXT` (36 chars) | Query performance |
| **Arrays** | Native `ARRAY[]` | JSON | Query complexity |
| **Foreign Keys** | Always enabled | Must enable with `PRAGMA` | Data integrity |
| **ALTER TABLE** | Full support | Limited | Migration complexity |
| **Concurrency** | Row-level locking | Database-level lock | Multi-user performance |
| **Size Limit** | Unlimited | ~281 TB (theoretical) | Scalability |
| **Connection** | Network | File-based | Deployment |

---

### UUID Handling

**PostgreSQL**:
```python
# Model definition
user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

# In database: Stored as 16-byte binary
# Display: 550e8400-e29b-41d4-a716-446655440000
```

**SQLite**:
```python
# Same model definition
user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

# In database: Stored as TEXT (36 characters)
# Display: 550e8400-e29b-41d4-a716-446655440000
```

**SQLAlchemy handles conversion automatically** - no code changes needed!

---

### Foreign Keys

**PostgreSQL**: Always enforced

**SQLite**: Must enable explicitly

```python
# In src/database.py
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if isinstance(dbapi_conn, sqlite3.Connection):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

**Without this**, SQLite allows orphaned records!

---

### Array Columns

**PostgreSQL**:
```python
# Model with array column
countries: Mapped[List[str]] = mapped_column(ARRAY(String))

# Query
SELECT * FROM user_stats WHERE 'Spain' = ANY(countries);
```

**SQLite**:
```python
# Same model - SQLAlchemy converts to JSON automatically
countries: Mapped[List[str]] = mapped_column(ARRAY(String))

# Storage: JSON string ["Spain", "France", "Italy"]
# Query: More complex (JSON functions)
```

---

### Migration Differences

**PostgreSQL migrations**:
```python
def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), default=False))
```

**SQLite migrations** (needs batch):
```python
def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), default=False))
```

---

## Common Operations

### Connect to Database

**PostgreSQL (Docker)**:
```bash
# Using psql
docker exec -it contravento-db-local psql -U contravento -d contravento

# Using connection string
psql postgresql://contravento:password@localhost:5432/contravento
```

**SQLite**:
```bash
sqlite3 backend/contravento_dev.db
```

---

### Common Queries

**List tables**:
```sql
-- PostgreSQL
\dt

-- SQLite
.tables
```

**View table schema**:
```sql
-- PostgreSQL
\d users

-- SQLite
.schema users
```

**Count rows**:
```sql
-- Both
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM trips;
```

**View recent users**:
```sql
SELECT username, email, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
```

**View trips with photos**:
```sql
SELECT t.title, COUNT(p.photo_id) as photo_count
FROM trips t
LEFT JOIN trip_photos p ON t.trip_id = p.trip_id
GROUP BY t.trip_id, t.title
ORDER BY photo_count DESC;
```

---

### Reset Database

**Development (SQLite)**:
```bash
# Delete database file
rm backend/contravento_dev.db

# Re-run setup
./run-local-dev.sh --setup
```

**Docker (PostgreSQL)**:
```bash
# Stop containers and remove volumes
docker-compose down -v

# Start fresh
docker-compose up -d

# Apply migrations
docker-compose exec backend poetry run alembic upgrade head

# Seed data
docker-compose exec backend poetry run python scripts/seeding/init_dev_data.py
```

---

## Troubleshooting

### Migration Fails: "Target database is not up to date"

**Symptom**:
```
alembic.util.exc.CommandError: Target database is not up to date.
```

**Cause**: Database schema doesn't match migration history

**Solution**:
```bash
# Option 1: Reset database (⚠️ deletes data)
rm backend/contravento_dev.db
poetry run alembic upgrade head

# Option 2: Stamp current schema
poetry run alembic stamp head
```

---

### Foreign Key Constraint Violation (SQLite)

**Symptom**:
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

**Cause**: Foreign keys not enabled

**Solution**: Verify `PRAGMA foreign_keys=ON` in `src/database.py` (see [Foreign Keys](#foreign-keys))

---

### Connection Refused (PostgreSQL)

**Symptom**:
```
could not connect to server: Connection refused
Is the server running on host "localhost" and accepting connections on port 5432?
```

**Diagnosis**:
```bash
# Check if PostgreSQL container is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

**Solution**:
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Or wait for health check
docker-compose up -d
sleep 20
```

---

### Seed Script Fails: User Already Exists

**Symptom**:
```
ERROR: User 'admin' already exists
```

**Solution**:
```bash
# Option 1: Use --force flag (if supported)
poetry run python scripts/user-mgmt/create_admin.py --force

# Option 2: Delete existing user first (dev only!)
sqlite3 backend/contravento_dev.db "DELETE FROM users WHERE username='admin';"

# Option 3: Create with different username
poetry run python scripts/user-mgmt/create_admin.py --username admin2
```

---

## See Also

- **[Getting Started](getting-started.md)** - Initial database setup
- **[Troubleshooting](troubleshooting.md)** - Database-specific errors
- **[Environment Variables](environment-variables.md)** - DATABASE_URL configuration
- **[Docker Compose Guide](docker-compose-guide.md)** - PostgreSQL container setup

---

**Last Updated**: 2026-02-06

**Alembic Version**: 1.13.x

**SQLAlchemy Version**: 2.0.x

**Feedback**: Found incorrect migration instructions? [Open an issue](https://github.com/your-org/contravento-application-python/issues)
