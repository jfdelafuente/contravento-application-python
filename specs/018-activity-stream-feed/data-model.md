# Data Model: Activity Stream Feed

**Feature**: 018-activity-stream-feed
**Date**: 2026-02-09
**Database**: PostgreSQL (production), SQLite (development)

---

## Entity Relationship Diagram

```
User (existing)
  │
  ├──< ActivityFeedItem (many)
  │     │
  │     ├──< Like (many)
  │     │     └──> User (liker)
  │     │
  │     └──< Comment (many)
  │           └──> User (commenter)
  │
  ├──< Notification (many)
  │
  └──< CommentReport (many)
```

---

## New Entities

### 1. ActivityFeedItem

Represents an activity in the feed (trip published, photo uploaded, achievement unlocked).

**Attributes**:
- `activity_id` (UUID, PK): Unique activity identifier
- `user_id` (UUID, FK → users.user_id): Author of the activity
- `activity_type` (ENUM): Type of activity - TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED
- `related_id` (UUID): Reference to related entity (trip_id, photo_id, user_achievement_id)
- `metadata` (JSONB): Type-specific data (trip title, photo URL, achievement code)
- `created_at` (TIMESTAMP WITH TIME ZONE): Activity creation timestamp

**Relationships**:
- Belongs to User (author) via `user_id`
- Has many Likes via `activity_id`
- Has many Comments via `activity_id`

**Indexes**:
- `idx_activities_user_created`: (user_id, created_at DESC) - Feed generation for user's activities
- `idx_activities_type_created`: (activity_type, created_at DESC) - Filter by activity type
- `idx_activities_created`: (created_at DESC) - Global chronological ordering

**Constraints**:
- `user_id` NOT NULL, FK to users.user_id ON DELETE CASCADE
- `activity_type` NOT NULL
- `related_id` NOT NULL
- `created_at` NOT NULL, DEFAULT NOW()

---

### 2. Like

Represents a like on an activity.

**Attributes**:
- `like_id` (UUID, PK): Unique like identifier
- `user_id` (UUID, FK → users.user_id): User who liked
- `activity_id` (UUID, FK → activity_feed_items.activity_id): Activity being liked
- `created_at` (TIMESTAMP WITH TIME ZONE): Like timestamp

**Relationships**:
- Belongs to User (liker) via `user_id`
- Belongs to ActivityFeedItem via `activity_id`

**Indexes**:
- `idx_likes_activity`: (activity_id) - Aggregate likes count per activity
- `idx_likes_user`: (user_id) - User's liked activities
- `idx_likes_created`: (created_at DESC) - Chronological ordering

**Constraints**:
- `user_id` NOT NULL, FK to users.user_id ON DELETE CASCADE
- `activity_id` NOT NULL, FK to activity_feed_items.activity_id ON DELETE CASCADE
- `created_at` NOT NULL, DEFAULT NOW()
- **UNIQUE** (user_id, activity_id) - One like per user per activity

---

### 3. Comment

Represents a comment on an activity.

**Attributes**:
- `comment_id` (UUID, PK): Unique comment identifier
- `user_id` (UUID, FK → users.user_id): Comment author
- `activity_id` (UUID, FK → activity_feed_items.activity_id): Activity being commented
- `text` (TEXT): Comment text (max 500 characters)
- `created_at` (TIMESTAMP WITH TIME ZONE): Comment timestamp

**Relationships**:
- Belongs to User (author) via `user_id`
- Belongs to ActivityFeedItem via `activity_id`
- Has many CommentReports via `comment_id`

**Indexes**:
- `idx_comments_activity`: (activity_id, created_at ASC) - Comments for activity (oldest first)
- `idx_comments_user`: (user_id) - User's comments
- `idx_comments_created`: (created_at DESC) - Chronological ordering

**Constraints**:
- `user_id` NOT NULL, FK to users.user_id ON DELETE CASCADE
- `activity_id` NOT NULL, FK to activity_feed_items.activity_id ON DELETE CASCADE
- `text` NOT NULL, CHECK (LENGTH(text) > 0 AND LENGTH(text) <= 500)
- `created_at` NOT NULL, DEFAULT NOW()

---

### 4. CommentReport

Stores reports of offensive comments (Option C: no moderation UI in MVP).

**Attributes**:
- `report_id` (UUID, PK): Unique report identifier
- `comment_id` (UUID, FK → comments.comment_id): Reported comment
- `reporter_user_id` (UUID, FK → users.user_id): User who reported
- `reason` (VARCHAR(50)): Report reason - "spam", "offensive", "harassment", "other"
- `notes` (TEXT, nullable): Optional additional context
- `created_at` (TIMESTAMP WITH TIME ZONE): Report timestamp

**Relationships**:
- Belongs to Comment via `comment_id`
- Belongs to User (reporter) via `reporter_user_id`

**Indexes**:
- `idx_comment_reports_comment`: (comment_id) - Reports for a comment
- `idx_comment_reports_created`: (created_at DESC) - Recent reports

**Constraints**:
- `comment_id` NOT NULL, FK to comments.comment_id ON DELETE CASCADE
- `reporter_user_id` NOT NULL, FK to users.user_id ON DELETE CASCADE
- `reason` NOT NULL, CHECK (reason IN ('spam', 'offensive', 'harassment', 'other'))
- `created_at` NOT NULL, DEFAULT NOW()
- **UNIQUE** (comment_id, reporter_user_id) - One report per user per comment

---

## Modified Entities

### Notification (Existing - Add New Types)

**Existing Structure** (from `backend/src/models/notification.py`):
- `notification_id` (UUID, PK)
- `user_id` (UUID, FK → users.user_id): Notification recipient
- `type` (ENUM): NotificationType - LIKE, COMMENT, SHARE
- `related_id` (UUID): Reference to like_id or comment_id
- `is_read` (BOOLEAN): Read status
- `created_at` (TIMESTAMP WITH TIME ZONE)

**Modification Required**: None - Existing types (LIKE, COMMENT) cover Activity Feed needs.

**Usage**:
- LIKE notification: `related_id` = like_id
- COMMENT notification: `related_id` = comment_id

---

## Enums

### ActivityType (New)

```python
class ActivityType(str, Enum):
    TRIP_PUBLISHED = "TRIP_PUBLISHED"
    PHOTO_UPLOADED = "PHOTO_UPLOADED"
    ACHIEVEMENT_UNLOCKED = "ACHIEVEMENT_UNLOCKED"
```

**Location**: `backend/src/models/activity_feed_item.py`

### CommentReportReason (New)

```python
class CommentReportReason(str, Enum):
    SPAM = "spam"
    OFFENSIVE = "offensive"
    HARASSMENT = "harassment"
    OTHER = "other"
```

**Location**: `backend/src/models/comment_report.py`

---

## DDL: PostgreSQL (Production)

```sql
-- ============================================================================
-- Activity Stream Feed Tables - PostgreSQL
-- ============================================================================

-- Create ActivityType enum
CREATE TYPE activity_type AS ENUM (
    'TRIP_PUBLISHED',
    'PHOTO_UPLOADED',
    'ACHIEVEMENT_UNLOCKED'
);

-- Create CommentReportReason enum
CREATE TYPE comment_report_reason AS ENUM (
    'spam',
    'offensive',
    'harassment',
    'other'
);

-- ============================================================================
-- 1. ActivityFeedItem Table
-- ============================================================================

CREATE TABLE activity_feed_items (
    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_type activity_type NOT NULL,
    related_id UUID NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for feed generation
CREATE INDEX idx_activities_user_created
ON activity_feed_items (user_id, created_at DESC);

CREATE INDEX idx_activities_type_created
ON activity_feed_items (activity_type, created_at DESC);

CREATE INDEX idx_activities_created
ON activity_feed_items (created_at DESC);

-- ============================================================================
-- 2. Likes Table
-- ============================================================================

CREATE TABLE likes (
    like_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Unique constraint: one like per user per activity
    UNIQUE (user_id, activity_id)
);

-- Indexes for likes aggregation
CREATE INDEX idx_likes_activity
ON likes (activity_id);

CREATE INDEX idx_likes_user
ON likes (user_id);

CREATE INDEX idx_likes_created
ON likes (created_at DESC);

-- ============================================================================
-- 3. Comments Table
-- ============================================================================

CREATE TABLE comments (
    comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    activity_id UUID NOT NULL REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE,
    text TEXT NOT NULL CHECK (LENGTH(text) > 0 AND LENGTH(text) <= 500),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for comments retrieval
CREATE INDEX idx_comments_activity
ON comments (activity_id, created_at ASC);

CREATE INDEX idx_comments_user
ON comments (user_id);

CREATE INDEX idx_comments_created
ON comments (created_at DESC);

-- ============================================================================
-- 4. CommentReports Table (Option C: Report button, no UI)
-- ============================================================================

CREATE TABLE comment_reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id UUID NOT NULL REFERENCES comments(comment_id) ON DELETE CASCADE,
    reporter_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    reason comment_report_reason NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Unique constraint: one report per user per comment
    UNIQUE (comment_id, reporter_user_id)
);

-- Indexes for report querying
CREATE INDEX idx_comment_reports_comment
ON comment_reports (comment_id);

CREATE INDEX idx_comment_reports_created
ON comment_reports (created_at DESC);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE activity_feed_items IS 'Activity feed items for social stream (trips, photos, achievements)';
COMMENT ON TABLE likes IS 'User likes on activity feed items';
COMMENT ON TABLE comments IS 'User comments on activity feed items (max 500 chars)';
COMMENT ON TABLE comment_reports IS 'User reports of offensive comments (Option C: stored for future moderation)';

COMMENT ON COLUMN activity_feed_items.metadata IS 'Type-specific JSON data (trip title, photo URL, achievement code)';
COMMENT ON COLUMN comments.text IS 'Comment text (sanitized HTML, max 500 characters)';
COMMENT ON COLUMN comment_reports.reason IS 'Report reason: spam, offensive, harassment, other';
```

---

## DDL: SQLite (Development)

```sql
-- ============================================================================
-- Activity Stream Feed Tables - SQLite
-- ============================================================================

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- 1. ActivityFeedItem Table
-- ============================================================================

CREATE TABLE activity_feed_items (
    activity_id TEXT PRIMARY KEY, -- UUID as TEXT in SQLite
    user_id TEXT NOT NULL,
    activity_type TEXT NOT NULL CHECK (
        activity_type IN ('TRIP_PUBLISHED', 'PHOTO_UPLOADED', 'ACHIEVEMENT_UNLOCKED')
    ),
    related_id TEXT NOT NULL,
    metadata TEXT DEFAULT '{}', -- JSON as TEXT in SQLite
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexes for feed generation
CREATE INDEX idx_activities_user_created
ON activity_feed_items (user_id, created_at DESC);

CREATE INDEX idx_activities_type_created
ON activity_feed_items (activity_type, created_at DESC);

CREATE INDEX idx_activities_created
ON activity_feed_items (created_at DESC);

-- ============================================================================
-- 2. Likes Table
-- ============================================================================

CREATE TABLE likes (
    like_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    activity_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE,

    -- Unique constraint: one like per user per activity
    UNIQUE (user_id, activity_id)
);

-- Indexes for likes aggregation
CREATE INDEX idx_likes_activity
ON likes (activity_id);

CREATE INDEX idx_likes_user
ON likes (user_id);

CREATE INDEX idx_likes_created
ON likes (created_at DESC);

-- ============================================================================
-- 3. Comments Table
-- ============================================================================

CREATE TABLE comments (
    comment_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    activity_id TEXT NOT NULL,
    text TEXT NOT NULL CHECK (LENGTH(text) > 0 AND LENGTH(text) <= 500),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (activity_id) REFERENCES activity_feed_items(activity_id) ON DELETE CASCADE
);

-- Indexes for comments retrieval
CREATE INDEX idx_comments_activity
ON comments (activity_id, created_at ASC);

CREATE INDEX idx_comments_user
ON comments (user_id);

CREATE INDEX idx_comments_created
ON comments (created_at DESC);

-- ============================================================================
-- 4. CommentReports Table (Option C: Report button, no UI)
-- ============================================================================

CREATE TABLE comment_reports (
    report_id TEXT PRIMARY KEY,
    comment_id TEXT NOT NULL,
    reporter_user_id TEXT NOT NULL,
    reason TEXT NOT NULL CHECK (reason IN ('spam', 'offensive', 'harassment', 'other')),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now')),

    FOREIGN KEY (comment_id) REFERENCES comments(comment_id) ON DELETE CASCADE,
    FOREIGN KEY (reporter_user_id) REFERENCES users(user_id) ON DELETE CASCADE,

    -- Unique constraint: one report per user per comment
    UNIQUE (comment_id, reporter_user_id)
);

-- Indexes for report querying
CREATE INDEX idx_comment_reports_comment
ON comment_reports (comment_id);

CREATE INDEX idx_comment_reports_created
ON comment_reports (created_at DESC);
```

---

## Sample Data

### ActivityFeedItem Examples

**Trip Published**:
```json
{
    "activity_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "user_id": "user123",
    "activity_type": "TRIP_PUBLISHED",
    "related_id": "trip456",
    "metadata": {
        "trip_title": "Ruta Bikepacking Pirineos",
        "trip_distance_km": 320.5,
        "trip_photo_url": "/storage/trips/2024/06/trip456/cover.jpg"
    },
    "created_at": "2024-06-15T10:30:00Z"
}
```

**Photo Uploaded**:
```json
{
    "activity_id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
    "user_id": "user123",
    "activity_type": "PHOTO_UPLOADED",
    "related_id": "photo789",
    "metadata": {
        "photo_url": "/storage/trips/2024/06/trip456/photo789.jpg",
        "photo_caption": "Vista desde el Pico Aneto",
        "trip_id": "trip456",
        "trip_title": "Ruta Bikepacking Pirineos"
    },
    "created_at": "2024-06-16T14:20:00Z"
}
```

**Achievement Unlocked**:
```json
{
    "activity_id": "c3d4e5f6-g7h8-9012-cdef-123456789012",
    "user_id": "user123",
    "activity_type": "ACHIEVEMENT_UNLOCKED",
    "related_id": "user_achievement_001",
    "metadata": {
        "achievement_code": "first_100km",
        "achievement_name": "Primera Ruta de 100km",
        "achievement_badge_icon": "trophy-100km.svg"
    },
    "created_at": "2024-06-15T10:30:05Z"
}
```

---

## Migration Plan

### Alembic Migration

**File**: `backend/migrations/versions/XXXX_add_activity_feed_tables.py`

**Migration Steps**:
1. Create `activity_type` enum (PostgreSQL) or check constraint (SQLite)
2. Create `comment_report_reason` enum (PostgreSQL) or check constraint (SQLite)
3. Create `activity_feed_items` table with indexes
4. Create `likes` table with unique constraint and indexes
5. Create `comments` table with check constraint and indexes
6. Create `comment_reports` table with unique constraint and indexes

**Rollback Steps**:
1. Drop tables in reverse order (comment_reports, comments, likes, activity_feed_items)
2. Drop enums (PostgreSQL only)

---

## Query Patterns

### 1. Get Feed for User (with pagination)

```sql
-- PostgreSQL with cursor-based pagination
SELECT
    a.activity_id,
    a.user_id,
    a.activity_type,
    a.related_id,
    a.metadata,
    a.created_at,
    u.username,
    u.photo_url AS user_photo,
    COUNT(DISTINCT l.like_id) AS likes_count,
    COUNT(DISTINCT c.comment_id) AS comments_count,
    EXISTS(
        SELECT 1 FROM likes l2
        WHERE l2.activity_id = a.activity_id
          AND l2.user_id = :current_user_id
    ) AS is_liked
FROM activity_feed_items a
JOIN users u ON a.user_id = u.user_id
LEFT JOIN likes l ON a.activity_id = l.activity_id
LEFT JOIN comments c ON a.activity_id = c.activity_id
WHERE a.user_id IN (
    SELECT followed_user_id
    FROM user_followers
    WHERE user_id = :current_user_id
)
  AND (
    -- Cursor filtering (if cursor provided)
    a.created_at < :cursor_created_at
    OR (a.created_at = :cursor_created_at AND a.activity_id < :cursor_activity_id)
  )
GROUP BY a.activity_id, u.user_id
ORDER BY a.created_at DESC, a.activity_id DESC
LIMIT 21; -- Fetch +1 to detect hasNextPage
```

### 2. Get Comments for Activity

```sql
SELECT
    c.comment_id,
    c.text,
    c.created_at,
    u.username,
    u.photo_url AS user_photo
FROM comments c
JOIN users u ON c.user_id = u.user_id
WHERE c.activity_id = :activity_id
ORDER BY c.created_at ASC
LIMIT 50;
```

### 3. Get Most Reported Comments (Admin Query)

```sql
-- Admin query to find comments needing moderation
SELECT
    c.comment_id,
    c.text,
    c.created_at,
    u.username AS comment_author,
    COUNT(r.report_id) AS report_count,
    STRING_AGG(DISTINCT r.reason, ', ') AS report_reasons
FROM comments c
JOIN users u ON c.user_id = u.user_id
JOIN comment_reports r ON c.comment_id = r.comment_id
GROUP BY c.comment_id, c.text, c.created_at, u.username
HAVING COUNT(r.report_id) >= 3 -- 3+ reports threshold
ORDER BY report_count DESC, c.created_at DESC;
```

---

## Data Retention

- **ActivityFeedItem**: Retain for 90 days (configurable)
- **Likes**: Retain indefinitely (part of social graph)
- **Comments**: Retain indefinitely unless deleted by author/admin
- **CommentReports**: Retain for 90 days after comment deletion

**Future Enhancement**: Archive old activities to `activity_feed_items_archive` table similar to `notifications_archive` pattern.

---

**Last Updated**: 2026-02-09
**Status**: ✅ READY FOR IMPLEMENTATION
