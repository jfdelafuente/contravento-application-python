# Data Model: Enlaces Sociales con Control de Privacidad Granular

**Feature**: 015-social-links-privacy
**Date**: 2026-01-16
**Database**: PostgreSQL 15+ (production) / SQLite 3.40+ (development/test)

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ users (existing from 001-user-profiles)                     │
│ ────────────────────────────────────────────────────────────│
│ • id                  UUID/TEXT PRIMARY KEY                  │
│ • username            VARCHAR UNIQUE NOT NULL                │
│ • email               VARCHAR UNIQUE NOT NULL                │
│ • ...                                                        │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ 1:N (one user has many social links)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ social_links (NEW)                                           │
│ ────────────────────────────────────────────────────────────│
│ • id                  UUID/TEXT PRIMARY KEY                  │
│ • user_id             UUID/TEXT FOREIGN KEY → users.id       │
│ • platform_type       ENUM/TEXT NOT NULL                     │
│ • url                 TEXT NOT NULL                          │
│ • privacy_level       ENUM/TEXT NOT NULL DEFAULT 'PUBLIC'    │
│ • created_at          TIMESTAMP NOT NULL                     │
│ • updated_at          TIMESTAMP NOT NULL                     │
└─────────────────────────────────────────────────────────────┘
                             │
                             │ (privacy filtering via Follows table)
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ follows (existing from 011-follows)                          │
│ ────────────────────────────────────────────────────────────│
│ • follower_id         UUID/TEXT FOREIGN KEY → users.id       │
│ • following_id        UUID/TEXT FOREIGN KEY → users.id       │
│ • created_at          TIMESTAMP NOT NULL                     │
│ • ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

**Note**: Privacy level "MUTUAL_FOLLOWERS" requires checking bidirectional relationships in the `follows` table (both users follow each other).

---

## Entity Specifications

### 1. SocialLink (Core Entity)

**Purpose**: Represents a link to an external social media platform configured by a user with granular privacy control.

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID (PG) / TEXT (SQLite) | PRIMARY KEY | Unique social link identifier |
| `user_id` | UUID/TEXT | FOREIGN KEY → users.id, NOT NULL, ON DELETE CASCADE | Owner of the link |
| `platform_type` | ENUM/TEXT | NOT NULL, CHECK IN ('INSTAGRAM', 'STRAVA', 'BLOG', 'PORTFOLIO', 'CUSTOM_1', 'CUSTOM_2') | Social platform type |
| `url` | TEXT | NOT NULL, CHECK (length(url) ≤ 2000) | Sanitized URL to social profile |
| `privacy_level` | ENUM/TEXT | NOT NULL, DEFAULT 'PUBLIC', CHECK IN ('PUBLIC', 'COMMUNITY', 'MUTUAL_FOLLOWERS', 'HIDDEN') | Visibility level |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification time |

**Indexes**:
```sql
-- Uniqueness: one link per platform per user
CREATE UNIQUE INDEX idx_social_link_user_platform ON social_links(user_id, platform_type);

-- Performance: filter by privacy level when viewing profiles
CREATE INDEX idx_social_link_privacy ON social_links(privacy_level);

-- Performance: user's links lookup
CREATE INDEX idx_social_link_user ON social_links(user_id);
```

**Validation Rules** (enforced in application layer):
- URL:
  - Maximum 2000 characters (FR-003)
  - Must pass validators.url() format check
  - Domain validation based on platform_type (see research.md)
  - Sanitized to prevent XSS/phishing (FR-004)
- Platform Type:
  - Instagram/Strava: Strict domain allowlist (instagram.com, strava.com)
  - Blog: Flexible allowlist (substack.com, medium.com, wordpress.com, etc.)
  - Portfolio/Custom: Any domain allowed (with format validation)
- Privacy Level:
  - PUBLIC: Visible to everyone (anonymous + authenticated)
  - COMMUNITY: Only authenticated users (members of ContraVento)
  - MUTUAL_FOLLOWERS: Only users with bidirectional follow relationship
  - HIDDEN: Saved in DB but not displayed (useful for temporary storage)
- Uniqueness: Maximum 1 link per platform_type per user (FR-010)

**State Transitions**:
```
PUBLIC ←→ COMMUNITY ←→ MUTUAL_FOLLOWERS ←→ HIDDEN
(all transitions allowed, no restrictions)
```

---

## Enumerations

### 1. PlatformType

**Purpose**: Defines supported social media platforms and custom link slots.

**Values**:

| Value | Display Name | Domain Validation | Description |
|-------|--------------|-------------------|-------------|
| `INSTAGRAM` | Instagram | Strict (instagram.com) | Instagram profile |
| `STRAVA` | Strava | Strict (strava.com, app.strava.com) | Strava athlete profile |
| `BLOG` | Blog | Flexible allowlist | Personal blog or writing platform |
| `PORTFOLIO` | Portfolio | Any domain | Portfolio website (photographers, artists) |
| `CUSTOM_1` | Enlace personalizado | Any domain | User-defined platform (e.g., YouTube, TikTok) |
| `CUSTOM_2` | Enlace personalizado | Any domain | Second user-defined platform |

**Implementation**:
```python
from enum import Enum

class PlatformType(str, Enum):
    INSTAGRAM = "INSTAGRAM"
    STRAVA = "STRAVA"
    BLOG = "BLOG"
    PORTFOLIO = "PORTFOLIO"
    CUSTOM_1 = "CUSTOM_1"
    CUSTOM_2 = "CUSTOM_2"
```

**Notes**:
- Maximum 6 links per user (1 per platform type)
- CUSTOM_1 and CUSTOM_2 allow flexibility for emerging platforms
- Future expansion: Add new platform types via migration (e.g., YOUTUBE, TIKTOK)

---

### 2. PrivacyLevel

**Purpose**: Defines visibility levels for social links based on viewer's relationship with link owner.

**Values**:

| Value | Display Name | Visible To | Icon | Use Case |
|-------|--------------|------------|------|----------|
| `PUBLIC` | Público | Everyone (anonymous + authenticated) | LockOpenIcon (candado abierto) | Professional guides, content creators seeking maximum visibility |
| `COMMUNITY` | Solo Comunidad | Authenticated users only | LockClosedIcon (candado cerrado) | Community members who want privacy from search engines |
| `MUTUAL_FOLLOWERS` | Círculo de Confianza | Users with mutual follow relationship | UserGroupIcon (grupo de personas) | Personal contact info (WhatsApp, Telegram) shared only with trusted connections |
| `HIDDEN` | Oculto | No one (owner only in edit mode) | EyeSlashIcon (ojo tachado) | Temporary storage, migration data, future publication |

**Implementation**:
```python
from enum import Enum

class PrivacyLevel(str, Enum):
    PUBLIC = "PUBLIC"
    COMMUNITY = "COMMUNITY"
    MUTUAL_FOLLOWERS = "MUTUAL_FOLLOWERS"
    HIDDEN = "HIDDEN"
```

**Privacy Filtering Logic** (service layer):
```python
def get_visible_links(
    db: AsyncSession,
    profile_user_id: UUID,
    viewer_user_id: UUID | None
) -> List[SocialLink]:
    """
    Filter social links based on viewer's relationship with profile owner.

    Rules:
    - Anonymous (viewer_user_id is None): Only PUBLIC
    - Authenticated non-owner: PUBLIC + COMMUNITY (+ MUTUAL_FOLLOWERS if mutual follow exists)
    - Owner (viewer_user_id == profile_user_id): All links including HIDDEN
    """
    if viewer_user_id is None:
        # Anonymous: only PUBLIC
        return query.filter(privacy_level == PrivacyLevel.PUBLIC)
    elif viewer_user_id == profile_user_id:
        # Owner: see all
        return query.all()
    else:
        # Authenticated: PUBLIC + COMMUNITY + check mutual follow
        mutual_follow = check_mutual_follow(db, profile_user_id, viewer_user_id)
        if mutual_follow:
            return query.filter(privacy_level.in_([PUBLIC, COMMUNITY, MUTUAL_FOLLOWERS]))
        else:
            return query.filter(privacy_level.in_([PUBLIC, COMMUNITY]))
```

**Notes**:
- Mutual follow check queries the `follows` table for bidirectional relationship
- Privacy filtering happens server-side (never trust client)
- Performance target: <200ms p95 for profile view with privacy filtering

---

## Database Schema DDL

### PostgreSQL (Production)

```sql
-- ============================================================================
-- SOCIAL LINKS FEATURE - PostgreSQL DDL
-- ============================================================================

-- Enums
CREATE TYPE platform_type AS ENUM (
    'INSTAGRAM',
    'STRAVA',
    'BLOG',
    'PORTFOLIO',
    'CUSTOM_1',
    'CUSTOM_2'
);

CREATE TYPE privacy_level AS ENUM (
    'PUBLIC',
    'COMMUNITY',
    'MUTUAL_FOLLOWERS',
    'HIDDEN'
);

-- Social Links table
CREATE TABLE social_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform_type platform_type NOT NULL,
    url TEXT NOT NULL CHECK (length(url) <= 2000),
    privacy_level privacy_level NOT NULL DEFAULT 'PUBLIC',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Uniqueness: one link per platform per user
    CONSTRAINT unique_user_platform UNIQUE (user_id, platform_type)
);

-- Indexes
CREATE UNIQUE INDEX idx_social_link_user_platform ON social_links(user_id, platform_type);
CREATE INDEX idx_social_link_privacy ON social_links(privacy_level);
CREATE INDEX idx_social_link_user ON social_links(user_id);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_social_link_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER social_link_updated_at
    BEFORE UPDATE ON social_links
    FOR EACH ROW
    EXECUTE FUNCTION update_social_link_timestamp();

-- Comments for documentation
COMMENT ON TABLE social_links IS 'User social media links with granular privacy control';
COMMENT ON COLUMN social_links.platform_type IS 'Social platform: INSTAGRAM, STRAVA, BLOG, PORTFOLIO, CUSTOM_1, CUSTOM_2';
COMMENT ON COLUMN social_links.privacy_level IS 'Visibility: PUBLIC, COMMUNITY, MUTUAL_FOLLOWERS, HIDDEN';
COMMENT ON COLUMN social_links.url IS 'Sanitized URL (max 2000 chars, validated and XSS-safe)';
```

### SQLite (Development/Test)

```sql
-- ============================================================================
-- SOCIAL LINKS FEATURE - SQLite DDL
-- ============================================================================

-- Social Links table
CREATE TABLE social_links (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform_type TEXT NOT NULL CHECK (
        platform_type IN ('INSTAGRAM', 'STRAVA', 'BLOG', 'PORTFOLIO', 'CUSTOM_1', 'CUSTOM_2')
    ),
    url TEXT NOT NULL CHECK (length(url) <= 2000),
    privacy_level TEXT NOT NULL DEFAULT 'PUBLIC' CHECK (
        privacy_level IN ('PUBLIC', 'COMMUNITY', 'MUTUAL_FOLLOWERS', 'HIDDEN')
    ),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Uniqueness: one link per platform per user
    CONSTRAINT unique_user_platform UNIQUE (user_id, platform_type)
);

-- Indexes
CREATE UNIQUE INDEX idx_social_link_user_platform ON social_links(user_id, platform_type);
CREATE INDEX idx_social_link_privacy ON social_links(privacy_level);
CREATE INDEX idx_social_link_user ON social_links(user_id);

-- Trigger to update updated_at
CREATE TRIGGER social_link_updated_at
    AFTER UPDATE ON social_links
    FOR EACH ROW
    BEGIN
        UPDATE social_links SET updated_at = datetime('now') WHERE id = NEW.id;
    END;

-- Enable foreign keys in SQLite
PRAGMA foreign_keys = ON;
```

---

## Sample Queries

### Query 1: Get visible social links for profile viewer

```sql
-- Get links visible to anonymous user (PUBLIC only)
SELECT
    sl.id,
    sl.platform_type,
    sl.url,
    sl.privacy_level
FROM social_links sl
WHERE sl.user_id = :profile_user_id
  AND sl.privacy_level = 'PUBLIC'
ORDER BY sl.platform_type;

-- Get links visible to authenticated user (PUBLIC + COMMUNITY + check mutual follow)
-- Step 1: Check if mutual follow exists
WITH mutual_follow AS (
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM follows
            WHERE follower_id = :viewer_user_id AND following_id = :profile_user_id
        ) AND EXISTS (
            SELECT 1 FROM follows
            WHERE follower_id = :profile_user_id AND following_id = :viewer_user_id
        ) THEN TRUE
        ELSE FALSE
    END AS is_mutual
)
-- Step 2: Filter links based on mutual follow status
SELECT
    sl.id,
    sl.platform_type,
    sl.url,
    sl.privacy_level
FROM social_links sl
CROSS JOIN mutual_follow mf
WHERE sl.user_id = :profile_user_id
  AND (
    sl.privacy_level = 'PUBLIC'
    OR sl.privacy_level = 'COMMUNITY'
    OR (sl.privacy_level = 'MUTUAL_FOLLOWERS' AND mf.is_mutual = TRUE)
  )
ORDER BY sl.platform_type;
```

### Query 2: Get user's own links (including HIDDEN)

```sql
-- Owner sees all links including HIDDEN (for edit mode)
SELECT
    sl.id,
    sl.platform_type,
    sl.url,
    sl.privacy_level,
    sl.created_at,
    sl.updated_at
FROM social_links sl
WHERE sl.user_id = :current_user_id
ORDER BY
    CASE sl.platform_type
        WHEN 'INSTAGRAM' THEN 1
        WHEN 'STRAVA' THEN 2
        WHEN 'BLOG' THEN 3
        WHEN 'PORTFOLIO' THEN 4
        WHEN 'CUSTOM_1' THEN 5
        WHEN 'CUSTOM_2' THEN 6
    END;
```

### Query 3: Check mutual follow relationship

```sql
-- Efficient mutual follow check (used in privacy filtering)
SELECT COUNT(*) = 2 AS is_mutual
FROM (
    SELECT 1 FROM follows
    WHERE follower_id = :user_a_id AND following_id = :user_b_id
    UNION ALL
    SELECT 1 FROM follows
    WHERE follower_id = :user_b_id AND following_id = :user_a_id
) AS mutual_check;
```

### Query 4: Validate uniqueness before insert (application layer)

```sql
-- Check if user already has a link for this platform
SELECT COUNT(*) AS link_exists
FROM social_links
WHERE user_id = :user_id
  AND platform_type = :platform_type;
-- If link_exists > 0, reject with error: "Ya tienes un enlace de Instagram configurado"
```

---

## Data Migration Plan

### From Current Version to 015-social-links-privacy

**Alembic Migration Steps**:

1. Create `social_links` table with all columns
2. Create indexes (unique constraint on user_id + platform_type)
3. Create triggers (PostgreSQL) for updated_at
4. Create enums (PostgreSQL only)
5. No data migration needed (new feature, no existing data)

**Rollback Plan**:

1. Drop triggers
2. Drop indexes
3. Drop `social_links` table
4. Drop enums (PostgreSQL only)

**Migration File Template**:
```python
"""add_social_links_table

Revision ID: 20260116_1200
Revises: <previous_revision>
Create Date: 2026-01-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260116_1200'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None

def upgrade():
    # Create enums (PostgreSQL only)
    if op.get_bind().dialect.name == 'postgresql':
        platform_type_enum = postgresql.ENUM(
            'INSTAGRAM', 'STRAVA', 'BLOG', 'PORTFOLIO', 'CUSTOM_1', 'CUSTOM_2',
            name='platform_type',
            create_type=True
        )
        platform_type_enum.create(op.get_bind())

        privacy_level_enum = postgresql.ENUM(
            'PUBLIC', 'COMMUNITY', 'MUTUAL_FOLLOWERS', 'HIDDEN',
            name='privacy_level',
            create_type=True
        )
        privacy_level_enum.create(op.get_bind())

    # Create social_links table
    op.create_table(
        'social_links',
        sa.Column('id', sa.String() if op.get_bind().dialect.name == 'sqlite' else postgresql.UUID(), primary_key=True),
        sa.Column('user_id', sa.String() if op.get_bind().dialect.name == 'sqlite' else postgresql.UUID(), nullable=False),
        sa.Column('platform_type', sa.String() if op.get_bind().dialect.name == 'sqlite' else platform_type_enum, nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('privacy_level', sa.String() if op.get_bind().dialect.name == 'sqlite' else privacy_level_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'platform_type', name='unique_user_platform')
    )

    # Create indexes
    op.create_index('idx_social_link_user_platform', 'social_links', ['user_id', 'platform_type'], unique=True)
    op.create_index('idx_social_link_privacy', 'social_links', ['privacy_level'])
    op.create_index('idx_social_link_user', 'social_links', ['user_id'])

    # Create trigger (PostgreSQL only)
    if op.get_bind().dialect.name == 'postgresql':
        op.execute("""
            CREATE OR REPLACE FUNCTION update_social_link_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        op.execute("""
            CREATE TRIGGER social_link_updated_at
                BEFORE UPDATE ON social_links
                FOR EACH ROW
                EXECUTE FUNCTION update_social_link_timestamp();
        """)

def downgrade():
    # Drop trigger (PostgreSQL only)
    if op.get_bind().dialect.name == 'postgresql':
        op.execute("DROP TRIGGER IF EXISTS social_link_updated_at ON social_links;")
        op.execute("DROP FUNCTION IF EXISTS update_social_link_timestamp();")

    # Drop indexes
    op.drop_index('idx_social_link_user', table_name='social_links')
    op.drop_index('idx_social_link_privacy', table_name='social_links')
    op.drop_index('idx_social_link_user_platform', table_name='social_links')

    # Drop table
    op.drop_table('social_links')

    # Drop enums (PostgreSQL only)
    if op.get_bind().dialect.name == 'postgresql':
        sa.Enum(name='privacy_level').drop(op.get_bind())
        sa.Enum(name='platform_type').drop(op.get_bind())
```

---

## Data Integrity & Constraints Summary

| Constraint Type | Rule | Enforced By |
|-----------------|------|-------------|
| Primary Keys | All rows have UUID/TEXT primary keys | Database |
| Foreign Keys | Cascading deletes (delete user → delete all their links) | Database |
| Uniqueness | One link per (user_id, platform_type) pair | Database (UNIQUE INDEX) |
| Check Constraints | URL ≤ 2000 chars, platform_type in allowed values, privacy_level in allowed values | Database |
| Length Limits | URL max 2000 characters | Database CHECK + Application validation |
| Required Fields | user_id, platform_type, url, privacy_level | Database NOT NULL |
| Enum Values | platform_type: 6 values, privacy_level: 4 values | Database ENUM/CHECK |
| Domain Validation | Instagram → instagram.com, Strava → strava.com, etc. | Application (validators library + custom logic) |
| XSS Protection | URL sanitization before storage | Application (validators library + bleach/custom sanitizer) |
| Timestamps | Auto-updated on modification | Database Triggers |

---

## Storage Estimates

### Per User (Average)

- 6 social links (max): 6 × 0.3 KB = 1.8 KB
- **Total per user**: ~2 KB

### Scale Projections

| Users | Links per User | Total Links | Storage (Links) | Database Growth |
|-------|----------------|-------------|-----------------|-----------------|
| 100 | 3 | 300 | 90 KB | Negligible |
| 1,000 | 4 | 4,000 | 1.2 MB | Negligible |
| 10,000 | 5 | 50,000 | 15 MB | Negligible |
| 100,000 | 5 | 500,000 | 150 MB | Minor |

**Recommendation**: Social links table is extremely lightweight. No special storage considerations needed. Standard PostgreSQL indexes are sufficient for 100k+ users.

---

## Appendix: SQLAlchemy Model Reference

```python
# backend/src/models/social_link.py
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime
from enum import Enum as PythonEnum
import uuid

class PlatformType(str, PythonEnum):
    INSTAGRAM = "INSTAGRAM"
    STRAVA = "STRAVA"
    BLOG = "BLOG"
    PORTFOLIO = "PORTFOLIO"
    CUSTOM_1 = "CUSTOM_1"
    CUSTOM_2 = "CUSTOM_2"

class PrivacyLevel(str, PythonEnum):
    PUBLIC = "PUBLIC"
    COMMUNITY = "COMMUNITY"
    MUTUAL_FOLLOWERS = "MUTUAL_FOLLOWERS"
    HIDDEN = "HIDDEN"

class SocialLink(Base):
    __tablename__ = "social_links"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform_type = Column(SQLEnum(PlatformType), nullable=False)
    url = Column(Text, nullable=False)
    privacy_level = Column(SQLEnum(PrivacyLevel), nullable=False, default=PrivacyLevel.PUBLIC)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="social_links")

    # Unique constraint: one link per platform per user
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    def to_dict(self):
        """Serialize to dictionary for JSON responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform_type": self.platform_type.value,
            "url": self.url,
            "privacy_level": self.privacy_level.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

# Add relationship to User model
# In backend/src/models/user.py:
# social_links = relationship("SocialLink", back_populates="user", cascade="all, delete-orphan")
```

---

## Security Considerations

### URL Sanitization Pipeline

```python
from validators import url as validate_url_format
from urllib.parse import urlparse

def sanitize_social_link_url(url: str, platform_type: PlatformType) -> str:
    """
    Sanitize and validate URL for social link.

    Steps:
    1. Validate URL format (RFC 3986)
    2. Extract domain and validate against allowlist
    3. Remove dangerous query params for social platforms
    4. Return clean URL

    Raises:
        ValueError: If URL is invalid or domain not allowed
    """
    # 1. Format validation
    if not validate_url_format(url):
        raise ValueError("URL inválida. Verifica el formato (debe comenzar con https://)")

    # 2. Parse URL
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace('www.', '')

    # 3. Domain allowlist check
    allowed_domains = DOMAIN_ALLOWLIST.get(platform_type)
    if allowed_domains and domain not in [d.replace('www.', '') for d in allowed_domains]:
        platform_name = PLATFORM_DISPLAY_NAMES.get(platform_type)
        raise ValueError(f"Dominio no permitido para {platform_name}. Usa un enlace válido.")

    # 4. Sanitize: remove query params for social platforms (prevent tracking/XSS)
    if platform_type in [PlatformType.INSTAGRAM, PlatformType.STRAVA]:
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    else:
        # Keep full URL for blogs/portfolios (may need query params)
        clean_url = url

    return clean_url
```

**XSS Prevention**:
- No `javascript:`, `data:`, `file:` schemes allowed (blocked by validators library)
- HTML rendering uses `rel="me nofollow"` and `target="_blank"`
- URL output is escaped in Jinja2/React templates

**Phishing Prevention**:
- Strict domain allowlist for Instagram/Strava prevents spoofing
- Flexible allowlist for blogs allows legitimate platforms only
- Subdomains not allowed (prevents `evil.instagram.com` attacks)

---

**Data Model Version**: 1.0
**Last Updated**: 2026-01-16
**Status**: ✅ Ready for Implementation
