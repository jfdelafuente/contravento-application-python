# Data Model: User Profiles & Authentication

**Feature**: 001-user-profiles | **Date**: 2025-12-23 | **Plan**: [plan.md](./plan.md)

## Purpose

This document defines the complete database schema for the authentication and user profile system, including DDL for both SQLite (development/testing) and PostgreSQL (production).

---

## Entity Relationship Diagram

```
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │───┐
│ username    │   │
│ email       │   │
│ password    │   │
│ verified    │   │
└─────────────┘   │
                  │
                  ├──────────────────┐
                  │                  │
                  ▼                  ▼
       ┌─────────────────┐  ┌──────────────┐
       │  user_profiles  │  │  user_stats  │
       │─────────────────│  │──────────────│
       │ id (PK)         │  │ id (PK)      │
       │ user_id (FK)    │  │ user_id (FK) │
       │ bio             │  │ total_trips  │
       │ photo_url       │  │ total_km     │
       │ location        │  │ countries    │
       │ cycling_type    │  │ photos_count │
       └─────────────────┘  └──────────────┘
                  │
                  │
                  ▼
       ┌──────────────────┐
       │     follows      │
       │──────────────────│
       │ id (PK)          │
       │ follower_id (FK) │───┐
       │ following_id(FK) │   │
       └──────────────────┘   │
                              │
          ┌───────────────────┘
          │
          ▼
       ┌─────────────────────┐       ┌──────────────────────┐
       │    achievements     │       │  user_achievements   │
       │─────────────────────│       │──────────────────────│
       │ id (PK)             │◄──────│ achievement_id (FK)  │
       │ code (UNIQUE)       │       │ user_id (FK)         │
       │ name                │       │ awarded_at           │
       │ description         │       └──────────────────────┘
       │ badge_icon          │
       └─────────────────────┘

       ┌─────────────────────┐
       │  password_resets    │
       │─────────────────────│
       │ id (PK)             │
       │ user_id (FK)        │───────►  users.id
       │ token_hash          │
       │ expires_at          │
       │ type                │  ('password_reset' | 'email_verification')
       └─────────────────────┘
```

---

## Table Definitions

### 1. users

**Purpose**: Core authentication table storing login credentials.

**SQLite DDL**:
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,  -- UUID stored as TEXT
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    hashed_password TEXT NOT NULL,  -- bcrypt hash
    is_active BOOLEAN NOT NULL DEFAULT 1,
    is_verified BOOLEAN NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),

    -- Constraints
    CHECK(length(username) >= 3 AND length(username) <= 30),
    CHECK(email LIKE '%_@__%.__%'),
    CHECK(length(hashed_password) = 60)  -- bcrypt produces 60-char hash
);

-- Indexes
CREATE UNIQUE INDEX idx_users_username_lower ON users(lower(username));
CREATE UNIQUE INDEX idx_users_email_lower ON users(lower(email));
CREATE INDEX idx_users_created_at ON users(created_at);
```

**PostgreSQL DDL**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(60) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT username_length CHECK(length(username) >= 3),
    CONSTRAINT email_format CHECK(email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT password_hash_length CHECK(length(hashed_password) = 60)
);

-- Indexes
CREATE UNIQUE INDEX idx_users_username_lower ON users(LOWER(username));
CREATE UNIQUE INDEX idx_users_email_lower ON users(LOWER(email));
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Fields**:
- `id`: Unique identifier (UUID)
- `username`: Login handle, 3-30 chars, case-insensitive unique (FR-001)
- `email`: Email address, case-insensitive unique (FR-001)
- `hashed_password`: bcrypt hash with 12 rounds (SC-019)
- `is_active`: Account active status (soft delete)
- `is_verified`: Email verification status (FR-002)
- `created_at`, `updated_at`: Audit timestamps (UTC)

**Sample Data**:
```sql
INSERT INTO users (id, username, email, hashed_password, is_verified) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'maria_garcia', 'maria@example.com', '$2b$12$...', 1),
('660e8400-e29b-41d4-a716-446655440001', 'juan_perez', 'juan@example.com', '$2b$12$...', 1);
```

---

### 2. user_profiles

**Purpose**: Extended user information and profile settings.

**SQLite DDL**:
```sql
CREATE TABLE user_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Profile information
    full_name TEXT,
    bio TEXT,
    photo_url TEXT,
    location TEXT,
    cycling_type TEXT,  -- 'road', 'mountain', 'gravel', 'touring', 'commuting'

    -- Privacy settings
    show_email BOOLEAN NOT NULL DEFAULT 0,
    show_location BOOLEAN NOT NULL DEFAULT 1,

    -- Social counters (denormalized)
    followers_count INTEGER NOT NULL DEFAULT 0,
    following_count INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),

    -- Constraints
    CHECK(length(bio) <= 500),
    CHECK(cycling_type IN ('road', 'mountain', 'gravel', 'touring', 'commuting') OR cycling_type IS NULL),
    CHECK(followers_count >= 0),
    CHECK(following_count >= 0)
);

-- Indexes
CREATE UNIQUE INDEX idx_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_profiles_cycling_type ON user_profiles(cycling_type) WHERE cycling_type IS NOT NULL;
```

**PostgreSQL DDL**:
```sql
CREATE TYPE cycling_type_enum AS ENUM ('road', 'mountain', 'gravel', 'touring', 'commuting');

CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Profile information
    full_name VARCHAR(100),
    bio TEXT,
    photo_url VARCHAR(500),
    location VARCHAR(100),
    cycling_type cycling_type_enum,

    -- Privacy settings
    show_email BOOLEAN NOT NULL DEFAULT false,
    show_location BOOLEAN NOT NULL DEFAULT true,

    -- Social counters (denormalized)
    followers_count INTEGER NOT NULL DEFAULT 0,
    following_count INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT bio_max_length CHECK(length(bio) <= 500),
    CONSTRAINT counters_non_negative CHECK(followers_count >= 0 AND following_count >= 0)
);

-- Indexes
CREATE UNIQUE INDEX idx_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_profiles_cycling_type ON user_profiles(cycling_type) WHERE cycling_type IS NOT NULL;
```

**Fields**:
- `user_id`: Foreign key to users table (1-to-1 relationship)
- `full_name`: Display name (optional) (FR-014)
- `bio`: Profile description, max 500 chars (FR-014)
- `photo_url`: URL to profile photo (FR-012)
- `location`: User's location (FR-014)
- `cycling_type`: Preferred cycling discipline (FR-014)
- `show_email`, `show_location`: Privacy controls (FR-017, FR-018)
- `followers_count`, `following_count`: Cached counts (FR-025, FR-026)

**Sample Data**:
```sql
INSERT INTO user_profiles (id, user_id, full_name, bio, location, cycling_type) VALUES
('770e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000',
 'María García', 'Amante del ciclismo de montaña 🚵‍♀️', 'Barcelona, España', 'mountain');
```

---

### 3. user_stats

**Purpose**: Cached statistics calculated from trip data.

**SQLite DDL**:
```sql
CREATE TABLE user_stats (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Trip statistics
    total_trips INTEGER NOT NULL DEFAULT 0,
    total_kilometers REAL NOT NULL DEFAULT 0.0,
    countries_visited TEXT NOT NULL DEFAULT '[]',  -- JSON array of country codes
    total_photos INTEGER NOT NULL DEFAULT 0,

    -- Achievement counter
    achievements_count INTEGER NOT NULL DEFAULT 0,

    -- Last activity
    last_trip_date TEXT,  -- ISO 8601 date format

    -- Timestamps
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),

    -- Constraints
    CHECK(total_trips >= 0),
    CHECK(total_kilometers >= 0),
    CHECK(total_photos >= 0),
    CHECK(achievements_count >= 0)
);

-- Indexes
CREATE UNIQUE INDEX idx_stats_user_id ON user_stats(user_id);
CREATE INDEX idx_stats_total_km ON user_stats(total_kilometers);
```

**PostgreSQL DDL**:
```sql
CREATE TABLE user_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Trip statistics
    total_trips INTEGER NOT NULL DEFAULT 0,
    total_kilometers NUMERIC(10, 2) NOT NULL DEFAULT 0,
    countries_visited TEXT[] NOT NULL DEFAULT '{}',  -- Array of ISO country codes
    total_photos INTEGER NOT NULL DEFAULT 0,

    -- Achievement counter
    achievements_count INTEGER NOT NULL DEFAULT 0,

    -- Last activity
    last_trip_date DATE,

    -- Timestamps
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT stats_non_negative CHECK(
        total_trips >= 0 AND
        total_kilometers >= 0 AND
        total_photos >= 0 AND
        achievements_count >= 0
    )
);

-- Indexes
CREATE UNIQUE INDEX idx_stats_user_id ON user_stats(user_id);
CREATE INDEX idx_stats_total_km ON user_stats(total_kilometers);
CREATE INDEX idx_stats_countries ON user_stats USING GIN(countries_visited);
```

**Fields**:
- `user_id`: Foreign key to users table (1-to-1)
- `total_trips`: Count of published trips (FR-019)
- `total_kilometers`: Sum of all trip distances (FR-019)
- `countries_visited`: Array/JSON of unique ISO country codes (FR-019)
- `total_photos`: Count of photos across all trips (FR-019)
- `achievements_count`: Number of unlocked achievements (FR-020)
- `last_trip_date`: Most recent trip end date
- `updated_at`: Last statistics update timestamp

**Sample Data**:
```sql
-- SQLite
INSERT INTO user_stats (id, user_id, total_trips, total_kilometers, countries_visited, total_photos, achievements_count) VALUES
('880e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000',
 12, 1547.85, '["ES", "FR", "IT"]', 48, 3);

-- PostgreSQL
INSERT INTO user_stats (id, user_id, total_trips, total_kilometers, countries_visited, total_photos, achievements_count) VALUES
('880e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000',
 12, 1547.85, ARRAY['ES', 'FR', 'IT'], 48, 3);
```

---

### 4. achievements

**Purpose**: Master table of all available achievements/badges.

**SQLite DDL**:
```sql
CREATE TABLE achievements (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    badge_icon TEXT,  -- URL or emoji
    requirement_type TEXT NOT NULL,  -- 'distance', 'trips', 'countries', 'photos'
    requirement_value REAL NOT NULL,

    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),

    CHECK(code = upper(code)),
    CHECK(requirement_type IN ('distance', 'trips', 'countries', 'photos')),
    CHECK(requirement_value > 0)
);

CREATE UNIQUE INDEX idx_achievements_code ON achievements(code);
```

**PostgreSQL DDL**:
```sql
CREATE TYPE achievement_type_enum AS ENUM ('distance', 'trips', 'countries', 'photos');

CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    badge_icon VARCHAR(200),
    requirement_type achievement_type_enum NOT NULL,
    requirement_value NUMERIC(10, 2) NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT code_uppercase CHECK(code = UPPER(code)),
    CONSTRAINT requirement_positive CHECK(requirement_value > 0)
);

CREATE UNIQUE INDEX idx_achievements_code ON achievements(code);
```

**Fields**:
- `code`: Unique achievement identifier (e.g., 'CENTURY', 'EXPLORER')
- `name`: Display name in Spanish (e.g., 'Centurión')
- `description`: Achievement description (e.g., 'Recorriste 100 km')
- `badge_icon`: Icon or emoji (e.g., '🏆', URL to image)
- `requirement_type`: What triggers the achievement
- `requirement_value`: Threshold (e.g., 100 for 100km)

**Sample Data**:
```sql
INSERT INTO achievements (id, code, name, description, badge_icon, requirement_type, requirement_value) VALUES
('990e8400-e29b-41d4-a716-446655440001', 'FIRST_TRIP', 'Primer Viaje', 'Publicaste tu primer viaje', '🚴', 'trips', 1),
('990e8400-e29b-41d4-a716-446655440002', 'CENTURY', 'Centurión', 'Recorriste 100 km en total', '💯', 'distance', 100),
('990e8400-e29b-41d4-a716-446655440003', 'VOYAGER', 'Viajero', 'Acumulaste 1000 km', '🌍', 'distance', 1000),
('990e8400-e29b-41d4-a716-446655440004', 'EXPLORER', 'Explorador', 'Visitaste 5 países', '🗺️', 'countries', 5),
('990e8400-e29b-41d4-a716-446655440005', 'PHOTOGRAPHER', 'Fotógrafo', 'Subiste 50 fotos', '📷', 'photos', 50),
('990e8400-e29b-41d4-a716-446655440006', 'GLOBETROTTER', 'Trotamundos', 'Visitaste 10 países', '✈️', 'countries', 10),
('990e8400-e29b-41d4-a716-446655440007', 'MARATHONER', 'Maratonista', 'Recorriste 5000 km', '🏃', 'distance', 5000),
('990e8400-e29b-41d4-a716-446655440008', 'INFLUENCER', 'Influencer', 'Tienes 100 seguidores', '⭐', 'followers', 100),
('990e8400-e29b-41d4-a716-446655440009', 'PROLIFIC', 'Prolífico', 'Publicaste 25 viajes', '📝', 'trips', 25);
```

---

### 5. user_achievements

**Purpose**: Junction table tracking which users earned which achievements.

**SQLite DDL**:
```sql
CREATE TABLE user_achievements (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id TEXT NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    awarded_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),

    UNIQUE(user_id, achievement_id)  -- User can earn each achievement only once
);

-- Indexes
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_awarded ON user_achievements(awarded_at);
```

**PostgreSQL DDL**:
```sql
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    awarded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT user_achievement_unique UNIQUE(user_id, achievement_id)
);

-- Indexes
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_awarded ON user_achievements(awarded_at);
```

**Fields**:
- `user_id`: User who earned the achievement
- `achievement_id`: Achievement that was earned
- `awarded_at`: Timestamp when achievement was unlocked

**Sample Data**:
```sql
INSERT INTO user_achievements (id, user_id, achievement_id) VALUES
('aa0e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', '990e8400-e29b-41d4-a716-446655440001'),
('aa0e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440000', '990e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', '990e8400-e29b-41d4-a716-446655440004');
```

---

### 6. follows

**Purpose**: Social graph representing follower/following relationships.

**SQLite DDL**:
```sql
CREATE TABLE follows (
    id TEXT PRIMARY KEY,
    follower_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),

    UNIQUE(follower_id, following_id),  -- Prevent duplicate follows
    CHECK(follower_id != following_id)  -- Prevent self-follow (FR-027)
);

-- Indexes
CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);
CREATE INDEX idx_follows_created ON follows(created_at);
```

**PostgreSQL DDL**:
```sql
CREATE TABLE follows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    CONSTRAINT follow_unique UNIQUE(follower_id, following_id),
    CONSTRAINT no_self_follow CHECK(follower_id != following_id)
);

-- Indexes
CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);
CREATE INDEX idx_follows_created ON follows(created_at);
```

**Fields**:
- `follower_id`: User who is following (FR-025)
- `following_id`: User being followed (FR-025)
- `created_at`: When the follow relationship was created

**Sample Data**:
```sql
-- User maria_garcia follows juan_perez
INSERT INTO follows (id, follower_id, following_id) VALUES
('bb0e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', '660e8400-e29b-41d4-a716-446655440001');
```

---

### 7. password_resets

**Purpose**: Temporary tokens for password reset and email verification.

**SQLite DDL**:
```sql
CREATE TABLE password_resets (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,  -- bcrypt hash of token
    expires_at TEXT NOT NULL,
    token_type TEXT NOT NULL,  -- 'password_reset' or 'email_verification'
    used_at TEXT,  -- NULL if not used yet

    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),

    CHECK(token_type IN ('password_reset', 'email_verification'))
);

-- Indexes
CREATE INDEX idx_password_resets_user ON password_resets(user_id);
CREATE INDEX idx_password_resets_expires ON password_resets(expires_at);
CREATE INDEX idx_password_resets_type ON password_resets(token_type);
```

**PostgreSQL DDL**:
```sql
CREATE TYPE token_type_enum AS ENUM ('password_reset', 'email_verification');

CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(60) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    token_type token_type_enum NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_password_resets_user ON password_resets(user_id);
CREATE INDEX idx_password_resets_expires ON password_resets(expires_at);
CREATE INDEX idx_password_resets_type ON password_resets(token_type);
```

**Fields**:
- `user_id`: User requesting password reset or email verification
- `token_hash`: bcrypt hash of the token (never store plain token)
- `expires_at`: Token expiration (24 hours for email, 1 hour for password)
- `token_type`: Differentiate between use cases
- `used_at`: Timestamp when token was used (prevent reuse)

**Sample Data**:
```sql
-- Email verification token (expires in 24 hours)
INSERT INTO password_resets (id, user_id, token_hash, expires_at, token_type) VALUES
('cc0e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000',
 '$2b$12$...', datetime('now', '+1 day'), 'email_verification');
```

---

## Database-Specific Notes

### SQLite Specifics

**Enable Foreign Keys** (must run on every connection):
```python
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if 'sqlite' in str(dbapi_conn):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

**UUID Handling**:
```python
import uuid
from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class UUID(TypeDecorator):
    """Platform-independent UUID type."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)
```

**JSON Array for Countries** (SQLite):
```python
import json
from sqlalchemy import TypeDecorator, TEXT

class JSONList(TypeDecorator):
    """Store list as JSON string in SQLite."""

    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return '[]'

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return []
```

### PostgreSQL Specifics

**Use Native Types**:
- UUID: `gen_random_uuid()` for primary keys
- Arrays: `TEXT[]` for `countries_visited`
- ENUMs: Custom types for `cycling_type`, `achievement_type`, `token_type`
- JSONB: For complex nested data (future use)

**Full-Text Search** (future feature):
```sql
-- Add tsvector column for searching bios
ALTER TABLE user_profiles ADD COLUMN bio_search tsvector
    GENERATED ALWAYS AS (to_tsvector('spanish', coalesce(bio, ''))) STORED;

CREATE INDEX idx_profiles_bio_search ON user_profiles USING GIN(bio_search);
```

---

## Migration Strategy

### Alembic Configuration

**1. Create initial migration**:
```bash
alembic revision --autogenerate -m "Initial schema: users, profiles, stats, achievements"
```

**2. Dialect-specific migrations**:
```python
# migrations/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Detect dialect
    conn = op.get_bind()
    dialect = conn.dialect.name

    if dialect == 'postgresql':
        # Create ENUMs first
        op.execute("CREATE TYPE cycling_type_enum AS ENUM ('road', 'mountain', 'gravel', 'touring', 'commuting')")

        # Create tables with PostgreSQL types
        op.create_table(
            'users',
            sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), primary_key=True),
            # ...
        )

    elif dialect == 'sqlite':
        # Create tables with SQLite types
        op.create_table(
            'users',
            sa.Column('id', sa.TEXT(), primary_key=True),
            # ...
        )

        # Enable foreign keys
        op.execute("PRAGMA foreign_keys=ON")

def downgrade():
    # Drop in reverse order
    op.drop_table('user_achievements')
    op.drop_table('follows')
    op.drop_table('password_resets')
    op.drop_table('user_stats')
    op.drop_table('user_profiles')
    op.drop_table('achievements')
    op.drop_table('users')
```

**3. Seeding achievements**:
```python
# migrations/versions/002_seed_achievements.py
def upgrade():
    achievements_data = [
        ('FIRST_TRIP', 'Primer Viaje', 'Publicaste tu primer viaje', '🚴', 'trips', 1),
        ('CENTURY', 'Centurión', 'Recorriste 100 km en total', '💯', 'distance', 100),
        # ... (see achievements table sample data)
    ]

    op.bulk_insert(
        sa.table('achievements',
            sa.column('code', sa.String),
            sa.column('name', sa.String),
            # ...
        ),
        [dict(zip(['code', 'name', ...], row)) for row in achievements_data]
    )
```

---

## Query Examples

### 1. User Registration with Profile

```sql
BEGIN TRANSACTION;

-- Insert user
INSERT INTO users (id, username, email, hashed_password, is_verified)
VALUES ('...', 'nueva_usuaria', 'nueva@example.com', '$2b$12$...', 0);

-- Create profile
INSERT INTO user_profiles (id, user_id)
VALUES ('...', '...');

-- Create stats record
INSERT INTO user_stats (id, user_id)
VALUES ('...', '...');

COMMIT;
```

### 2. Get User Profile with Stats

```sql
-- PostgreSQL (JOIN)
SELECT
    u.username,
    u.email,
    u.is_verified,
    p.full_name,
    p.bio,
    p.photo_url,
    p.location,
    p.cycling_type,
    p.followers_count,
    p.following_count,
    s.total_trips,
    s.total_kilometers,
    s.countries_visited,
    s.achievements_count
FROM users u
JOIN user_profiles p ON p.user_id = u.id
JOIN user_stats s ON s.user_id = u.id
WHERE u.username = 'maria_garcia';
```

### 3. Get User Achievements

```sql
SELECT
    a.code,
    a.name,
    a.description,
    a.badge_icon,
    ua.awarded_at
FROM user_achievements ua
JOIN achievements a ON a.id = ua.achievement_id
WHERE ua.user_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY ua.awarded_at DESC;
```

### 4. Get Followers (Paginated)

```sql
SELECT
    u.username,
    p.full_name,
    p.photo_url,
    p.bio,
    f.created_at as followed_at
FROM follows f
JOIN users u ON u.id = f.follower_id
JOIN user_profiles p ON p.user_id = u.id
WHERE f.following_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY f.created_at DESC
LIMIT 50 OFFSET 0;
```

### 5. Update Statistics After Trip Publish

```sql
-- PostgreSQL
UPDATE user_stats
SET
    total_trips = total_trips + 1,
    total_kilometers = total_kilometers + 125.5,
    countries_visited = array_append(countries_visited, 'IT'),
    last_trip_date = '2025-12-20',
    updated_at = NOW()
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000';

-- SQLite
UPDATE user_stats
SET
    total_trips = total_trips + 1,
    total_kilometers = total_kilometers + 125.5,
    countries_visited = json_insert(countries_visited, '$[#]', 'IT'),
    last_trip_date = '2025-12-20',
    updated_at = datetime('now', 'utc')
WHERE user_id = '550e8400-e29b-41d4-a716-446655440000';
```

---

## Performance Considerations

### Index Strategy

**Critical indexes** (already included above):
1. `idx_users_username_lower` - Login queries
2. `idx_users_email_lower` - Email lookups, password reset
3. `idx_follows_follower` - Get users I'm following
4. `idx_follows_following` - Get my followers
5. `idx_stats_total_km` - Leaderboards (future)

**Query optimization**:
- Use `EXPLAIN QUERY PLAN` (SQLite) or `EXPLAIN ANALYZE` (PostgreSQL) for slow queries
- Profile denormalized counters avoid `COUNT(*)` on large tables
- Pagination via `LIMIT`/`OFFSET` (consider cursor-based for scale)

### Connection Pooling

**SQLite** (development/testing):
```python
engine = create_async_engine(
    "sqlite+aiosqlite:///./contravento_dev.db",
    connect_args={"check_same_thread": False},
    poolclass=NullPool  # Single connection
)
```

**PostgreSQL** (production):
```python
engine = create_async_engine(
    "postgresql+asyncpg://...",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

---

## Data Model Status

✅ **Complete** - All 7 tables defined with:
- SQLite DDL (development/testing)
- PostgreSQL DDL (production)
- Indexes for performance
- Constraints for data integrity
- Sample data
- Migration strategy
- Query examples

**Next Steps**:
1. Implement SQLAlchemy ORM models in `backend/src/models/`
2. Create Alembic migration scripts
3. Write Pydantic schemas for validation
4. Define API contracts in `contracts/`
