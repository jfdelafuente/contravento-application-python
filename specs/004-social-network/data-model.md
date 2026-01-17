# Data Model: Red Social y Feed de Ciclistas

**Feature**: 004-social-network
**Date**: 2026-01-16
**Status**: ✅ Completed

## Overview

This document defines the database schema for the Social Network feature, including Likes, Comments, Shares, Notifications, and Feed items.

## Entity Relationship Diagram

```
User (existing)
  ↓ 1:N
Like ────→ Trip (existing)
  │
Comment ──→ Trip
  │
Share ────→ Trip
  │
Notification → User (recipient)
             → User (actor)
             → Trip (context)

NotificationArchive (soft delete, 30-day retention)
```

## Entities

### 1. Like

**Purpose**: Track user likes on trips (FR-009)

**Fields**:
- `id` (PK): Unique identifier (UUID)
- `user_id` (FK): User who liked the trip
- `trip_id` (FK): Trip being liked
- `created_at`: Timestamp of like action

**Constraints**:
- Unique (user_id, trip_id): User can like trip only once
- CASCADE delete when user or trip deleted

**Indexes**:
- `ix_likes_trip_id`: Fast lookup of trip likes count
- `ix_likes_user_id`: Fast lookup of user's liked trips
- `ix_likes_created_at`: Chronological ordering

---

### 2. Comment

**Purpose**: User comments on trips (FR-016)

**Fields**:
- `id` (PK): Unique identifier (UUID)
- `user_id` (FK): Comment author
- `trip_id` (FK): Trip being commented on
- `content` (Text): Comment text (max 500 chars)
- `created_at`: Original creation timestamp
- `updated_at`: Last edit timestamp (nullable)
- `is_edited`: Boolean flag for edited comments

**Constraints**:
- content length: 1-500 characters
- CASCADE delete when user or trip deleted
- CHECK: content must not be empty after trimming

**Indexes**:
- `ix_comments_trip_id`: Fast lookup of trip comments
- `ix_comments_user_id`: Fast lookup of user's comments
- `ix_comments_created_at`: Chronological ordering

---

### 3. Share

**Purpose**: Share trips with optional commentary (FR-023)

**Fields**:
- `id` (PK): Unique identifier (UUID)
- `user_id` (FK): User sharing the trip
- `trip_id` (FK): Trip being shared
- `comment` (Text): Optional share commentary (max 200 chars)
- `created_at`: Timestamp of share action

**Constraints**:
- comment length: 0-200 characters (nullable)
- CASCADE delete when user or trip deleted

**Indexes**:
- `ix_shares_trip_id`: Fast lookup of trip shares count
- `ix_shares_user_id`: Fast lookup of user's shares
- `ix_shares_created_at`: Chronological ordering

---

### 4. Notification

**Purpose**: User notifications for social interactions (FR-028)

**Fields**:
- `id` (PK): Unique identifier (UUID)
- `user_id` (FK): Notification recipient
- `type` (String): Notification type ("like", "comment", "share")
- `actor_id` (FK): User who performed the action
- `trip_id` (FK): Trip context
- `content` (Text): Comment excerpt for "comment" type (nullable)
- `is_read` (Boolean): Read status (default False)
- `created_at`: Timestamp of notification creation

**Constraints**:
- type must be one of: "like", "comment", "share"
- CASCADE delete when user, actor, or trip deleted
- content required for type="comment", null otherwise

**Indexes**:
- `ix_notifications_user_read`: Fast lookup of unread notifications
- `ix_notifications_created_at`: Chronological ordering

**Archiving Strategy**:
- Notifications older than 30 days are moved to `notifications_archive` table
- Background job runs daily to archive old notifications
- Active queries only scan `notifications` table (fast)

---

### 5. NotificationArchive

**Purpose**: Archive old notifications for history preservation

**Fields**: Same structure as `Notification`

**Archiving Logic**:
- Daily cron job identifies notifications created > 30 days ago
- Move to `notifications_archive` table
- Delete from `notifications` table
- Preserves history while keeping active table small

---

## SQLite DDL (Development/Testing)

```sql
-- ============================================================
-- LIKES TABLE
-- ============================================================
CREATE TABLE likes (
    id TEXT PRIMARY KEY NOT NULL,  -- UUID as TEXT
    user_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,

    UNIQUE (user_id, trip_id)  -- User can like trip only once
);

CREATE INDEX ix_likes_trip_id ON likes(trip_id);
CREATE INDEX ix_likes_user_id ON likes(user_id);
CREATE INDEX ix_likes_created_at ON likes(created_at);

-- ============================================================
-- COMMENTS TABLE
-- ============================================================
CREATE TABLE comments (
    id TEXT PRIMARY KEY NOT NULL,  -- UUID as TEXT
    user_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    content TEXT NOT NULL CHECK(LENGTH(TRIM(content)) BETWEEN 1 AND 500),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_edited BOOLEAN NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE INDEX ix_comments_trip_id ON comments(trip_id);
CREATE INDEX ix_comments_user_id ON comments(user_id);
CREATE INDEX ix_comments_created_at ON comments(created_at);

-- ============================================================
-- SHARES TABLE
-- ============================================================
CREATE TABLE shares (
    id TEXT PRIMARY KEY NOT NULL,  -- UUID as TEXT
    user_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    comment TEXT CHECK(comment IS NULL OR LENGTH(comment) <= 200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE INDEX ix_shares_trip_id ON shares(trip_id);
CREATE INDEX ix_shares_user_id ON shares(user_id);
CREATE INDEX ix_shares_created_at ON shares(created_at);

-- ============================================================
-- NOTIFICATIONS TABLE
-- ============================================================
CREATE TABLE notifications (
    id TEXT PRIMARY KEY NOT NULL,  -- UUID as TEXT
    user_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('like', 'comment', 'share')),
    actor_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    content TEXT,  -- Comment excerpt for type='comment'
    is_read BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,

    CHECK (
        (type = 'comment' AND content IS NOT NULL) OR
        (type IN ('like', 'share') AND content IS NULL)
    )
);

CREATE INDEX ix_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX ix_notifications_created_at ON notifications(created_at);

-- ============================================================
-- NOTIFICATIONS ARCHIVE TABLE
-- ============================================================
CREATE TABLE notifications_archive (
    id TEXT PRIMARY KEY NOT NULL,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    content TEXT,
    is_read BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    archived_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_notifications_archive_user ON notifications_archive(user_id);
CREATE INDEX ix_notifications_archive_created_at ON notifications_archive(created_at);
```

---

## PostgreSQL DDL (Production)

```sql
-- ============================================================
-- LIKES TABLE
-- ============================================================
CREATE TABLE likes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    trip_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,

    UNIQUE (user_id, trip_id)
);

CREATE INDEX ix_likes_trip_id ON likes(trip_id);
CREATE INDEX ix_likes_user_id ON likes(user_id);
CREATE INDEX ix_likes_created_at ON likes(created_at);

-- ============================================================
-- COMMENTS TABLE
-- ============================================================
CREATE TABLE comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    trip_id UUID NOT NULL,
    content TEXT NOT NULL CHECK(LENGTH(TRIM(content)) BETWEEN 1 AND 500),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    is_edited BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE INDEX ix_comments_trip_id ON comments(trip_id);
CREATE INDEX ix_comments_user_id ON comments(user_id);
CREATE INDEX ix_comments_created_at ON comments(created_at);

-- ============================================================
-- SHARES TABLE
-- ============================================================
CREATE TABLE shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    trip_id UUID NOT NULL,
    comment TEXT CHECK(comment IS NULL OR LENGTH(comment) <= 200),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE INDEX ix_shares_trip_id ON shares(trip_id);
CREATE INDEX ix_shares_user_id ON shares(user_id);
CREATE INDEX ix_shares_created_at ON shares(created_at);

-- ============================================================
-- NOTIFICATIONS TABLE
-- ============================================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type VARCHAR(20) NOT NULL CHECK(type IN ('like', 'comment', 'share')),
    actor_id UUID NOT NULL,
    trip_id UUID NOT NULL,
    content TEXT,  -- Comment excerpt for type='comment'
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE,

    CHECK (
        (type = 'comment' AND content IS NOT NULL) OR
        (type IN ('like', 'share') AND content IS NULL)
    )
);

CREATE INDEX ix_notifications_user_read ON notifications(user_id, is_read);
CREATE INDEX ix_notifications_created_at ON notifications(created_at);

-- ============================================================
-- NOTIFICATIONS ARCHIVE TABLE
-- ============================================================
CREATE TABLE notifications_archive (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    type VARCHAR(20) NOT NULL,
    actor_id UUID NOT NULL,
    trip_id UUID NOT NULL,
    content TEXT,
    is_read BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    archived_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_notifications_archive_user ON notifications_archive(user_id);
CREATE INDEX ix_notifications_archive_created_at ON notifications_archive(created_at);
```

---

## Migrations

### Migration 1: Create Social Tables

**File**: `backend/migrations/versions/YYYYMMDD_HHMMSS_create_social_tables.py`

**Upgrade**:
1. Create `likes` table
2. Create `comments` table
3. Create `shares` table
4. Create `notifications` table
5. Create `notifications_archive` table
6. Create all indexes

**Downgrade**:
1. Drop all indexes
2. Drop all tables in reverse order

---

## Data Model Notes

### Like Counting

**Counter denormalization** (future enhancement):
- Add `likes_count` column to `trips` table
- Update counter via database trigger or service layer
- Query optimization: `SELECT likes_count FROM trips` instead of `COUNT(*) FROM likes`

### Comment Threading

**Future enhancement**:
- Add `parent_comment_id` (FK to comments.id) for nested replies
- Add `thread_depth` integer for limiting nesting (max 3 levels)
- Current v1: Flat comments only

### Notification Grouping

**Optimization** (future enhancement):
- Group similar notifications: "John and 5 others liked your trip"
- Add `notification_groups` table with aggregation logic
- Current v1: Individual notifications

### Feed Materialization

**Performance optimization** (future enhancement):
- Create `feed_cache` table with pre-computed feed items
- Invalidate cache on new trip publish, like, comment, share
- Current v1: Real-time query aggregation

---

## Performance Considerations

### Indexing Strategy

**High-cardinality indexes**:
- `ix_likes_trip_id`: Lookup trip likes count (FR-010)
- `ix_comments_trip_id`: Lookup trip comments (FR-016)
- `ix_notifications_user_read`: Unread notifications query (FR-030)

**Composite index**:
- `ix_notifications_user_read (user_id, is_read)`: Fast unread count per user

**Date indexes**:
- `ix_*_created_at`: Chronological ordering for feeds

### Query Optimization

**Eager loading**:
- Use SQLAlchemy `selectinload()` for user, trip relationships
- Prevent N+1 queries when fetching feed with likes/comments

**Pagination**:
- Cursor-based pagination for infinite scroll (FR-006)
- Offset-based pagination for notifications (max 50 per page)

### Archiving Strategy

**Background job** (cron/celery):
```python
# Daily at 2 AM
async def archive_old_notifications(db: AsyncSession):
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    # Move to archive
    result = await db.execute(
        select(Notification).where(Notification.created_at < cutoff_date)
    )
    old_notifications = result.scalars().all()

    for notif in old_notifications:
        archive = NotificationArchive(**notif.__dict__)
        db.add(archive)
        await db.delete(notif)

    await db.commit()
```

---

## Validation Rules

### Like (FR-011)
- User cannot like own trips
- User can like trip only once (enforced by UNIQUE constraint)
- Trip must be PUBLISHED status

### Comment (FR-017, FR-018)
- Content: 1-500 characters after trimming
- HTML sanitization required (prevent XSS)
- Rate limit: 10 comments per hour per user
- Trip must be PUBLISHED status

### Share (FR-024)
- Optional comment: 0-200 characters
- User can share trip multiple times
- Trip must be PUBLISHED status

### Notification (FR-029)
- Auto-generated by system (users cannot create directly)
- Batch notifications: Max 1 per user per trip per type per hour
- Don't notify user of their own actions

---

## Success Criteria Mapping

- **SC-001**: Feed query <1s p95 → Indexes on created_at, compound queries
- **SC-002**: Infinite scroll <500ms → Cursor-based pagination
- **SC-006**: Like toggle <200ms → Simple INSERT/DELETE, indexed lookups
- **SC-013**: Comment post <300ms → Text validation, indexed inserts
- **SC-020**: Notification generation <1s → Async background task
- **SC-030**: Unread count <100ms → Composite index (user_id, is_read)

---

**Data Model Status**: ✅ COMPLETED
**Date Completed**: 2026-01-16
**Ready for Contracts**: YES
