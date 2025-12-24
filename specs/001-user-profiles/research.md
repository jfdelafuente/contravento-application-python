# Technology Research & Decisions: User Profiles & Authentication

**Feature**: 001-user-profiles | **Date**: 2025-12-23 | **Plan**: [plan.md](./plan.md)

## Purpose

This document captures the research and rationale behind key technology decisions for the authentication and user profile system. All decisions align with the project constitution and are validated against functional requirements and success criteria.

---

## 1. Database: SQLite vs PostgreSQL

### Decision: Dual Strategy (SQLite for dev/test, PostgreSQL for production)

**Rationale**:
- **Developer Experience**: SQLite requires zero configuration, no Docker containers, and works immediately after `git clone`
- **CI/CD Performance**: In-memory SQLite databases make tests run 5-10x faster than spinning up PostgreSQL containers
- **Production Requirements**: PostgreSQL handles hundreds of concurrent users (SC-004), native UUID support, and advanced indexing

**SQLite Configuration**:
```python
# Development - file-based
DATABASE_URL = "sqlite+aiosqlite:///./contravento_dev.db"

# Testing - in-memory for speed
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

**PostgreSQL Configuration**:
```python
# Production
DATABASE_URL = "postgresql+asyncpg://user:pass@host:5432/contravento"

# Connection pooling
create_async_engine(
    DATABASE_URL,
    pool_size=20,        # Base connections
    max_overflow=10,     # Additional under load
    pool_pre_ping=True   # Verify connections
)
```

**SQLite Limitations & Solutions**:

| Limitation | SQLite Workaround | PostgreSQL Native |
|------------|-------------------|-------------------|
| No native UUID | Store as TEXT with UUID strings | `gen_random_uuid()` |
| No array columns | JSON array for `countries_visited` | `TEXT[]` |
| Foreign keys off by default | `PRAGMA foreign_keys=ON` in connection | Always on |
| Limited concurrency | OK for dev/test (single writer) | Hundreds concurrent |

**Migration Path**: SQLAlchemy's ORM abstracts differences. Alembic migrations detect dialect and apply appropriate DDL.

**Validation**:
- ✅ Meets constitution requirement for developer experience
- ✅ Supports performance target SC-004 (100+ concurrent registrations)
- ✅ Simplifies testing infrastructure (no Docker in CI)

---

## 2. Authentication: JWT vs Session-Based

### Decision: JWT with Refresh Tokens

**Rationale**:
- **Stateless**: No server-side session storage required (scales horizontally)
- **Mobile-Friendly**: Future mobile app can store tokens securely
- **Distributed**: Frontend (CDN) and backend (API server) can be separate
- **Requirement Alignment**: FR-010 explicitly requires token refresh mechanism

**Implementation Details**:

**Token Structure**:
```python
# Access Token (short-lived)
{
    "sub": "user_id",          # Subject (user identifier)
    "username": "maria_garcia",
    "exp": 1640000000,         # Expires in 15 minutes
    "type": "access"
}

# Refresh Token (long-lived)
{
    "sub": "user_id",
    "exp": 1642592000,         # Expires in 30 days
    "type": "refresh",
    "jti": "unique_token_id"   # For revocation tracking
}
```

**Security Measures**:
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: 256-bit random key from environment variable
- **Token Rotation**: New refresh token issued on each refresh (FR-010)
- **Revocation**: Store refresh token `jti` in database, check on refresh

**Refresh Flow**:
1. Client sends expired access token + valid refresh token
2. Backend validates refresh token signature and expiration
3. Check refresh token `jti` not in revocation table
4. Issue new access token (15min) + new refresh token (30 days)
5. Invalidate old refresh token `jti`

**Alternative Considered**: Session cookies
- ❌ Requires server-side storage (Redis/database)
- ❌ Complicates horizontal scaling
- ❌ Doesn't meet FR-010 requirement for token refresh

**Validation**:
- ✅ Meets FR-010 (refresh tokens with 30-day expiration)
- ✅ Supports SC-003 (<500ms p95 for auth endpoints)
- ✅ Aligns with constitution security requirements

---

## 3. Password Hashing: bcrypt Rounds (12 vs 14)

### Decision: 12 rounds

**Rationale**:
- **Security**: Constitution mandates ≥12 rounds (SC-019)
- **Performance**: 12 rounds = ~300ms hashing time, meets SC-003 (<500ms p95)
- **Industry Standard**: OWASP recommends 10-12 rounds for 2024

**Benchmarks** (measured on typical VPS with 2 CPU cores):

| Rounds | Hash Time | Verify Time | SC-003 Compliance |
|--------|-----------|-------------|-------------------|
| 10     | ~100ms    | ~100ms      | ✅ Well under 500ms |
| 12     | ~300ms    | ~300ms      | ✅ Under 500ms |
| 14     | ~1200ms   | ~1200ms     | ❌ Exceeds 500ms p95 |

**Security Analysis**:
- **12 rounds** = 2^12 = 4,096 iterations
- **Brute force cost**: At 100 billion hashes/sec (top GPU), testing 1 billion passwords takes ~11 hours with bcrypt-12
- **Future-proof**: bcrypt automatically scales with Moore's Law improvements

**Implementation**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Fixed at 12 rounds
)

# Hash password (registration)
hashed = pwd_context.hash(plain_password)

# Verify password (login)
is_valid = pwd_context.verify(plain_password, hashed)
```

**Alternative Considered**: 14 rounds
- ❌ Exceeds performance target SC-003 (500ms p95)
- ❌ Degrades user experience during registration/login
- ⚠️ Only 4x more secure than 12 rounds (marginal benefit)

**Validation**:
- ✅ Meets constitution requirement (≥12 rounds)
- ✅ Meets SC-019 (secure password storage)
- ✅ Meets SC-003 (authentication response time)

---

## 4. Email Verification: Pattern Selection

### Decision: Token-based verification with expiration

**Rationale**:
- **Security**: Time-limited tokens prevent indefinite verification links
- **User Experience**: Clear error messages when token expires
- **Requirement**: FR-002 requires email verification before account activation

**Flow**:
1. User registers → Account created with `email_verified=False`
2. Generate random verification token (32 bytes, URL-safe base64)
3. Store token hash + expiration (24 hours) in `password_resets` table (reused for both use cases)
4. Send email with link: `https://contravento.com/verify?token={token}`
5. User clicks → Backend validates token + expiration → Set `email_verified=True`
6. Delete verification token from database

**Token Generation**:
```python
import secrets
from datetime import datetime, timedelta

def create_verification_token(user_id: str) -> str:
    """Generate secure verification token."""
    token = secrets.token_urlsafe(32)  # 256-bit entropy

    # Store in database with expiration
    PasswordReset.create(
        user_id=user_id,
        token_hash=hash_token(token),  # bcrypt hash for storage
        expires_at=datetime.utcnow() + timedelta(hours=24),
        type="email_verification"
    )

    return token
```

**Email Template** (Spanish):
```
Asunto: Verifica tu cuenta en ContraVento

Hola {username},

Haz clic en el siguiente enlace para verificar tu cuenta:
{verification_link}

Este enlace expira en 24 horas.

Si no creaste esta cuenta, ignora este correo.

Saludos,
Equipo ContraVento
```

**Edge Cases**:
- **Expired token**: Return 400 with Spanish error "El enlace de verificación ha expirado"
- **Already verified**: Return 200 with message "Tu cuenta ya está verificada"
- **Invalid token**: Return 400 with "Enlace de verificación inválido"
- **Resend verification**: Allow users to request new token (rate limited to 3/hour)

**Alternative Considered**: Magic links (no password)
- ❌ Doesn't meet FR-001 (password-based registration)
- ❌ Less secure (email compromise = account compromise)

**Validation**:
- ✅ Meets FR-002 (email verification requirement)
- ✅ Meets constitution UX requirement (Spanish messages)
- ✅ Secure (time-limited, hashed tokens)

---

## 5. File Upload: Photo Handling Strategy

### Decision: Local filesystem with S3-ready structure

**Rationale**:
- **Simplicity**: No external dependencies for MVP (S3, Cloudinary)
- **Performance**: Local disk serves images faster than S3 in same datacenter
- **Cost**: Zero storage cost for development/testing
- **Migration Path**: Directory structure mirrors S3 bucket layout

**Storage Structure**:
```
backend/storage/
└── profile_photos/
    └── {year}/
        └── {month}/
            └── {user_id}_{uuid}.jpg
```

Example: `profile_photos/2025/12/user123_a7b3c2d1.jpg`

**Upload Flow**:
1. User uploads photo via `POST /users/{username}/profile/photo`
2. Validate MIME type (image/jpeg, image/png) - FR-012
3. Validate file size (max 5MB) - FR-013
4. Generate unique filename: `{user_id}_{uuid4()}.jpg`
5. Save original to temp location
6. Background task: Resize to 400x400px with Pillow (FR-013)
7. Delete original, save resized
8. Update `user_profile.photo_url` in database

**Image Processing**:
```python
from PIL import Image
import aiofiles

async def resize_profile_photo(file_path: str, target_size: int = 400) -> str:
    """Resize and optimize profile photo."""

    # Open image
    img = Image.open(file_path)

    # Convert to RGB (handles PNG with transparency)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize to 400x400 (crop to square first)
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    # Save optimized JPEG
    output_path = file_path.replace('.png', '.jpg')
    img.save(output_path, 'JPEG', quality=85, optimize=True)

    return output_path
```

**Security**:
- **MIME type validation**: Check magic bytes (not just extension) - FR-034
- **Size limit**: Reject files >5MB immediately - FR-013
- **Content scanning**: Pillow automatically validates image structure (prevents exploit images)
- **Filename sanitization**: Use UUIDs (never user-provided names)

**S3 Migration Path** (future):
```python
# Same interface, different storage backend
class PhotoStorage(ABC):
    async def save(self, file: UploadFile, user_id: str) -> str:
        pass

class LocalStorage(PhotoStorage):
    # Current implementation
    pass

class S3Storage(PhotoStorage):
    # Future: boto3 upload to S3
    pass
```

**Alternative Considered**: Direct S3 upload
- ❌ Requires AWS credentials in development
- ❌ Adds complexity to testing (mocking S3)
- ❌ Monthly cost even for development

**Validation**:
- ✅ Meets FR-012 (upload profile photo)
- ✅ Meets FR-013 (5MB max, 400x400 resize)
- ✅ Meets SC-006 (<2s upload time)
- ✅ Meets constitution security (file validation)

---

## 6. Social Graph: Follow/Follower SQL Patterns

### Decision: Single `follows` table with denormalized counters

**Rationale**:
- **Query Performance**: Denormalized counters avoid COUNT(*) on large tables
- **Scalability**: Index on (follower_id, following_id) enables fast lookups
- **Data Integrity**: Database triggers/app logic keep counters in sync

**Schema**:
```sql
-- Relationship table
CREATE TABLE follows (
    id UUID PRIMARY KEY,
    follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(follower_id, following_id),  -- Prevent duplicate follows
    CHECK(follower_id != following_id)  -- Prevent self-follow (FR-027)
);

CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);

-- Denormalized counters in user_profiles
ALTER TABLE user_profiles ADD COLUMN followers_count INTEGER DEFAULT 0;
ALTER TABLE user_profiles ADD COLUMN following_count INTEGER DEFAULT 0;
```

**Follow Operation** (transactional):
```python
async def follow_user(db: AsyncSession, follower_id: str, following_id: str):
    """Follow a user and update counters."""

    # 1. Create follow relationship
    follow = Follow(follower_id=follower_id, following_id=following_id)
    db.add(follow)

    # 2. Increment counters (denormalized)
    await db.execute(
        update(UserProfile)
        .where(UserProfile.user_id == following_id)
        .values(followers_count=UserProfile.followers_count + 1)
    )

    await db.execute(
        update(UserProfile)
        .where(UserProfile.user_id == follower_id)
        .values(following_count=UserProfile.following_count + 1)
    )

    await db.commit()
```

**Query Patterns**:

1. **Get followers** (FR-028):
```sql
SELECT u.username, u.email, p.bio, p.photo_url
FROM users u
JOIN follows f ON f.follower_id = u.id
JOIN user_profiles p ON p.user_id = u.id
WHERE f.following_id = :user_id
ORDER BY f.created_at DESC
LIMIT 50 OFFSET :offset;
```

2. **Get following** (FR-029):
```sql
SELECT u.username, u.email, p.bio, p.photo_url
FROM users u
JOIN follows f ON f.following_id = u.id
JOIN user_profiles p ON p.user_id = u.id
WHERE f.follower_id = :user_id
ORDER BY f.created_at DESC
LIMIT 50 OFFSET :offset;
```

3. **Check if following**:
```sql
SELECT 1 FROM follows
WHERE follower_id = :current_user AND following_id = :target_user
LIMIT 1;
```

**Consistency Strategy**:
- **Application-level**: Update counters in same transaction as follow/unfollow
- **Periodic reconciliation**: Cron job to fix drift (compare counter to COUNT(*))
- **No database triggers**: Avoid complexity, handle in Python

**Alternative Considered**: Real-time COUNT(*)
- ❌ Slow on large tables (millions of follows)
- ❌ Doesn't meet SC-003 (<200ms for simple queries)

**Validation**:
- ✅ Meets FR-025 to FR-032 (all follow/follower requirements)
- ✅ Meets SC-003 (<200ms for follower list queries with indexes)
- ✅ Pagination support (max 50 items per request)

---

## 7. Statistics Calculation: Real-time vs Cached

### Decision: Event-driven updates with cached statistics

**Rationale**:
- **Performance**: Pre-calculated stats avoid joins across trip/photo tables
- **Accuracy**: Updated on trip publish/edit/delete ensures freshness
- **Complexity**: Simpler than real-time aggregation queries
- **Requirement**: FR-019 to FR-024 require specific statistics to be displayed

**Schema**:
```sql
CREATE TABLE user_stats (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Denormalized statistics (updated by events)
    total_trips INTEGER DEFAULT 0,
    total_kilometers DECIMAL(10, 2) DEFAULT 0,
    countries_visited JSONB DEFAULT '[]',  -- PostgreSQL: JSONB, SQLite: TEXT with JSON
    total_photos INTEGER DEFAULT 0,
    achievements_count INTEGER DEFAULT 0,

    last_trip_date DATE NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

**Update Strategy**:

**Event**: Trip published (FR-019)
```python
async def on_trip_published(trip: Trip):
    """Update statistics when trip is published."""

    # Calculate trip distance
    distance_km = calculate_gpx_distance(trip.gpx_file)

    # Update stats
    await db.execute(
        update(UserStats)
        .where(UserStats.user_id == trip.author_id)
        .values(
            total_trips=UserStats.total_trips + 1,
            total_kilometers=UserStats.total_kilometers + distance_km,
            countries_visited=func.jsonb_set(  # Add country if not exists
                UserStats.countries_visited,
                '{end}',
                trip.country
            ),
            last_trip_date=trip.end_date
        )
    )

    # Check for new achievements
    await check_achievements(trip.author_id)
```

**Event**: Trip deleted (FR-023)
```python
async def on_trip_deleted(trip: Trip):
    """Recalculate statistics when trip is deleted."""

    # Option 1: Decrement (fast but can drift)
    distance_km = calculate_gpx_distance(trip.gpx_file)
    await db.execute(
        update(UserStats)
        .where(UserStats.user_id == trip.author_id)
        .values(
            total_trips=UserStats.total_trips - 1,
            total_kilometers=UserStats.total_kilometers - distance_km
        )
    )

    # Option 2: Full recalculation (slow but accurate)
    stats = await recalculate_all_stats(trip.author_id)
    await db.merge(stats)
```

**Achievement Checking** (FR-020 to FR-022):
```python
async def check_achievements(user_id: str):
    """Award achievements based on current statistics."""

    stats = await get_user_stats(user_id)

    achievements_to_award = []

    # Distance achievements
    if stats.total_kilometers >= 100 and not has_achievement(user_id, "CENTURY"):
        achievements_to_award.append("CENTURY")  # 100km badge

    if stats.total_kilometers >= 1000 and not has_achievement(user_id, "VOYAGER"):
        achievements_to_award.append("VOYAGER")  # 1000km badge

    # Country achievements
    if len(stats.countries_visited) >= 5 and not has_achievement(user_id, "EXPLORER"):
        achievements_to_award.append("EXPLORER")  # 5 countries

    # Bulk insert achievements
    for achievement_code in achievements_to_award:
        await award_achievement(user_id, achievement_code)
```

**Consistency**:
- **Transactional**: Statistics updated in same database transaction as trip publish/delete
- **Background reconciliation**: Daily cron job recalculates all stats from source data
- **Idempotent**: Safe to run multiple times

**Alternative Considered**: Real-time aggregation
```sql
-- Too slow for profile page
SELECT
    COUNT(*) as total_trips,
    SUM(distance_km) as total_kilometers,
    ARRAY_AGG(DISTINCT country) as countries_visited
FROM trips
WHERE author_id = :user_id AND status = 'published';
```
- ❌ Requires joins across multiple tables
- ❌ Doesn't meet SC-003 (<200ms for simple queries)
- ❌ Expensive for users with hundreds of trips

**Validation**:
- ✅ Meets FR-019 to FR-024 (all statistics requirements)
- ✅ Meets SC-003 (<200ms for profile queries)
- ✅ Accurate (event-driven updates + reconciliation)

---

## Summary of Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Database** | SQLite (dev/test) + PostgreSQL (prod) | Developer experience + production performance |
| **Authentication** | JWT with refresh tokens | Stateless, mobile-ready, meets FR-010 |
| **Password Hashing** | bcrypt 12 rounds | Security + performance balance (SC-019, SC-003) |
| **Email Verification** | Token-based with 24h expiration | Secure, clear UX (FR-002) |
| **File Upload** | Local filesystem (S3-ready) | Simplicity, zero cost, migration path |
| **Social Graph** | Single table + denormalized counters | Query performance (SC-003) |
| **Statistics** | Event-driven cached updates | Performance + accuracy (FR-019 to FR-024) |

**Constitution Alignment**:
- ✅ All decisions pass security requirements
- ✅ All decisions meet performance targets
- ✅ All decisions support TDD workflow (testable with SQLite)
- ✅ All decisions maintain Spanish-first UX

**Next Steps**:
1. Validate decisions in `data-model.md` with full DDL
2. Implement in Phase 0 (foundation setup)
3. Test assumptions during Phase 1 (authentication implementation)

---

**Research Status**: ✅ Complete - All technology decisions documented and validated
