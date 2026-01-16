# Implementation Plan: Red Social y Feed de Ciclistas

**Branch**: `004-social-network` | **Date**: 2026-01-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/004-social-network/spec.md`

## Summary

Implement a complete social networking system for cyclists including personalized feed, likes, comments, shares, and notifications. This feature enables community engagement around trip content using a hybrid feed algorithm (chronological + popular backfill), custom React hooks for state management, and notification archiving for scalability.

**Key Technical Approach** (from research.md):
- **Feed Algorithm**: Hybrid (trips from followed users + popular community backfill)
- **Real-time Updates**: Manual refresh (v1) with polling planned for v2
- **Notification Storage**: Soft delete with 30-day archiving to separate table
- **Frontend State**: Custom hooks pattern with optimistic updates (consistent with existing codebase)
- **check_mutual_follow()**: Added to SocialService for Feature 015 dependency

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy 2.0 (async), Pydantic
- Frontend: React 18, Axios, react-hot-toast

**Storage**: PostgreSQL (production), SQLite (development)
- New tables: likes, comments, shares, notifications, notifications_archive
- Existing tables: users, trips, follows (from Feature 003)

**Testing**: pytest (backend TDD), Vitest + React Testing Library (frontend)
**Target Platform**: Web application (Linux server + modern browsers)
**Project Type**: Web (backend + frontend)

**Performance Goals**:
- Feed query: <1s p95 (SC-001)
- Like toggle: <200ms p95 (SC-006)
- Comment post: <300ms p95 (SC-013)
- Notification generation: <1s p95 (SC-020)
- Unread count: <100ms p95 (SC-030)

**Constraints**:
- Rate limiting: 10 comments/hour per user (FR-018), 100 likes/hour per user
- Comment length: 1-500 characters (FR-017)
- Share comment: 0-200 characters (FR-024)
- Notification archiving: 30-day retention in active table
- No WebSockets in v1 (manual refresh only)

**Scale/Scope**:
- 5 user stories (Feed P1, Likes P2, Comments P3, Shares P4, Notifications P5)
- 4 new database tables + 1 archive table
- 15 API endpoints (Feed, Likes, Comments, Shares, Notifications)
- Frontend: Custom hooks, infinite scroll, optimistic updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality
- ✅ **PEP 8 with black formatter**: All backend code follows existing convention
- ✅ **Type hints required**: All service functions will have type annotations
- ✅ **Google-style docstrings**: All public functions documented
- ✅ **Single Responsibility**: Services handle business logic, models only data
- ✅ **No magic numbers**: Rate limits, text lengths, archiving days in config

### Testing (TDD Mandatory)
- ✅ **Write tests FIRST**: Contract tests → Unit tests → Implementation
- ✅ **Coverage ≥90%**: Required across all new modules (likes, comments, shares, notifications)
- ✅ **Test structure**:
  - Contract tests: OpenAPI schema validation against social-api.yaml
  - Unit tests: Service layer business logic
  - Integration tests: API endpoints, database operations

### User Experience
- ✅ **Spanish language**: All user-facing text (error messages, notifications)
- ✅ **Standardized JSON responses**: `{success, data, error}` format
- ✅ **Field-specific errors**: Validation errors with field names
- ✅ **UTC timestamps**: All created_at/updated_at with timezone awareness

### Performance
- ✅ **Query optimization**: Indexed columns (trip_id, user_id, created_at)
- ✅ **Eager loading**: selectinload() to prevent N+1 queries in feed
- ✅ **Pagination**: max 50 items per page
- ✅ **Rate limiting**: Enforced at service layer

### Security
- ✅ **Bcrypt hashing**: Already implemented in AuthService
- ✅ **JWT tokens**: Existing authentication (15min access, 30-day refresh)
- ✅ **SQLAlchemy ORM only**: No raw SQL queries
- ✅ **HTML sanitization**: Applied to comment content (prevent XSS)
- ✅ **Authorization checks**: User can only edit/delete own comments

**Constitution Status**: ✅ PASS (no violations)

## Project Structure

### Documentation (this feature)

```text
specs/004-social-network/
├── spec.md              # Feature specification (5 user stories, 33 FRs, 14 SCs)
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output (4 architectural decisions)
├── data-model.md        # Phase 1 output (5 entities with SQLite + PostgreSQL DDL)
├── quickstart.md        # Phase 1 output (manual testing scenarios)
├── contracts/
│   └── social-api.yaml  # Phase 1 output (OpenAPI 3.1.0 spec, 15 endpoints)
└── tasks.md             # Phase 2 output (NOT YET CREATED - awaiting /speckit.tasks)
```

### Source Code (repository root)

**Web application structure** (backend + frontend):

```text
backend/
├── src/
│   ├── models/
│   │   ├── social.py            # Follow model (EXISTING from Feature 003)
│   │   ├── like.py              # NEW: Like model
│   │   ├── comment.py           # NEW: Comment model
│   │   ├── share.py             # NEW: Share model
│   │   └── notification.py      # NEW: Notification + NotificationArchive models
│   │
│   ├── schemas/
│   │   ├── social.py            # EXISTING: FollowResponse, etc.
│   │   ├── like.py              # NEW: LikeResponse, LikesListResponse
│   │   ├── comment.py           # NEW: CommentCreateInput, CommentResponse
│   │   ├── share.py             # NEW: ShareCreateInput, ShareResponse
│   │   └── notification.py      # NEW: NotificationResponse, NotificationsListResponse
│   │
│   ├── services/
│   │   ├── social_service.py    # UPDATE: Add check_mutual_follow()
│   │   ├── feed_service.py      # NEW: Personalized feed logic
│   │   ├── like_service.py      # NEW: Like/unlike operations
│   │   ├── comment_service.py   # NEW: Comment CRUD + rate limiting
│   │   ├── share_service.py     # NEW: Share operations
│   │   └── notification_service.py  # NEW: Notification generation + archiving
│   │
│   ├── api/
│   │   ├── feed.py              # NEW: GET /feed
│   │   ├── likes.py             # NEW: POST/DELETE /trips/{id}/like, GET /trips/{id}/likes
│   │   ├── comments.py          # NEW: POST/GET/PUT/DELETE /trips/{id}/comments
│   │   ├── shares.py            # NEW: POST /trips/{id}/share, GET /trips/{id}/shares
│   │   └── notifications.py     # NEW: GET /notifications, mark-read endpoints
│   │
│   └── utils/
│       ├── rate_limiter.py      # NEW: Rate limiting decorator (10 comments/hour)
│       └── html_sanitizer.py    # NEW: HTML sanitization for comments
│
├── tests/
│   ├── contract/
│   │   └── test_social_api.py   # NEW: OpenAPI contract validation (social-api.yaml)
│   │
│   ├── unit/
│   │   ├── test_feed_service.py
│   │   ├── test_like_service.py
│   │   ├── test_comment_service.py
│   │   ├── test_share_service.py
│   │   ├── test_notification_service.py
│   │   └── test_social_service.py  # UPDATE: Add test_check_mutual_follow()
│   │
│   └── integration/
│       ├── test_feed_api.py
│       ├── test_likes_api.py
│       ├── test_comments_api.py
│       ├── test_shares_api.py
│       └── test_notifications_api.py
│
└── migrations/
    └── versions/
        └── YYYYMMDD_HHMMSS_create_social_tables.py  # NEW: Alembic migration

frontend/
├── src/
│   ├── components/
│   │   ├── feed/
│   │   │   ├── FeedList.tsx             # NEW: Infinite scroll feed
│   │   │   ├── FeedItem.tsx             # NEW: Single feed trip card
│   │   │   └── FeedSkeleton.tsx         # NEW: Loading state
│   │   │
│   │   ├── likes/
│   │   │   ├── LikeButton.tsx           # NEW: Optimistic like toggle
│   │   │   └── LikesList.tsx            # NEW: Modal with users who liked
│   │   │
│   │   ├── comments/
│   │   │   ├── CommentForm.tsx          # NEW: Add/edit comment
│   │   │   ├── CommentList.tsx          # NEW: Trip comments
│   │   │   └── CommentItem.tsx          # NEW: Single comment with edit/delete
│   │   │
│   │   ├── shares/
│   │   │   ├── ShareButton.tsx          # NEW: Share trip dialog
│   │   │   └── SharesList.tsx           # NEW: Users who shared
│   │   │
│   │   └── notifications/
│   │       ├── NotificationBadge.tsx    # NEW: Unread count badge
│   │       ├── NotificationList.tsx     # NEW: Notifications drawer
│   │       └── NotificationItem.tsx     # NEW: Single notification
│   │
│   ├── hooks/
│   │   ├── useFeed.ts                   # NEW: Infinite scroll feed hook
│   │   ├── useLike.ts                   # NEW: Optimistic like toggle
│   │   ├── useComment.ts                # NEW: Comment CRUD operations
│   │   ├── useShare.ts                  # NEW: Share trip hook
│   │   └── useNotifications.ts          # NEW: Notifications with unread count
│   │
│   ├── services/
│   │   ├── feedService.ts               # NEW: Axios API calls for feed
│   │   ├── likeService.ts               # NEW: Axios API calls for likes
│   │   ├── commentService.ts            # NEW: Axios API calls for comments
│   │   ├── shareService.ts              # NEW: Axios API calls for shares
│   │   └── notificationService.ts       # NEW: Axios API calls for notifications
│   │
│   └── pages/
│       ├── FeedPage.tsx                 # NEW: Main feed page (/)
│       └── NotificationsPage.tsx        # NEW: Notifications page (/notifications)
│
└── tests/
    └── unit/
        ├── useLike.test.tsx             # NEW: Optimistic update tests
        ├── useComment.test.tsx          # NEW: Comment form validation
        └── useFeed.test.tsx             # NEW: Infinite scroll tests
```

**Structure Decision**: Web application (Option 2) with backend + frontend separation. This matches the existing ContraVento architecture with FastAPI backend and React frontend. All social features follow the established pattern:
- Backend: Models → Schemas → Services → API routers
- Frontend: Services → Hooks → Components → Pages
- Testing: Contract → Unit → Integration (TDD workflow)

## Complexity Tracking

**Constitution Check**: ✅ PASS (no violations requiring justification)

This feature follows all existing ContraVento patterns and conventions with no new architectural complexity.

## Phase Breakdown

### Phase 0: Research & Decision Making ✅ COMPLETED

**Deliverable**: [research.md](research.md)

**Key Decisions Made**:

1. **Feed Algorithm**: Hybrid approach
   - Trips from followed users (chronological DESC)
   - Backfill with popular community trips (likes_count DESC) if < limit
   - No machine learning in v1
   - Single query with UNION, sorted by timestamp

2. **Real-time Updates**: Manual refresh (v1)
   - No WebSockets/SSE complexity
   - Simple stateless API
   - Future polling (v2) at 30-60s interval
   - Easy upgrade path

3. **Notification Storage**: Soft delete + archiving
   - Active table: notifications (30 days retention)
   - Archive table: notifications_archive (historical data)
   - Daily background job moves old notifications
   - Fast queries on active table (<100ms)

4. **Frontend State Management**: Custom hooks pattern
   - Consistent with existing codebase (useTripForm, useTripList)
   - No new dependencies (Redux, React Query)
   - Optimistic updates for likes/comments
   - Cache invalidation via manual refetch

**Research Status**: ✅ COMPLETED (2026-01-16)

---

### Phase 1: Design Artifacts ✅ COMPLETED

**Deliverables**:
1. ✅ [data-model.md](data-model.md) - 5 entities with SQLite + PostgreSQL DDL
2. ✅ [contracts/social-api.yaml](contracts/social-api.yaml) - OpenAPI 3.1.0 spec (15 endpoints)
3. ✅ [quickstart.md](quickstart.md) - Manual testing scenarios for all user stories

**Data Model Summary**:
- **Like**: (user_id, trip_id, created_at) - Unique constraint on (user_id, trip_id)
- **Comment**: (user_id, trip_id, content 1-500 chars, created_at, updated_at, is_edited)
- **Share**: (user_id, trip_id, comment 0-200 chars, created_at)
- **Notification**: (user_id, type, actor_id, trip_id, content, is_read, created_at)
- **NotificationArchive**: Same structure as Notification + archived_at

**API Contracts Summary** (15 endpoints):
- Feed: GET /feed (FR-001 to FR-008)
- Likes: POST /trips/{id}/like, DELETE /trips/{id}/like, GET /trips/{id}/likes
- Comments: POST/GET /trips/{id}/comments, PUT/DELETE /trips/{id}/comments/{cid}
- Shares: POST /trips/{id}/share, GET /trips/{id}/shares
- Notifications: GET /notifications, GET /notifications/unread-count, POST /notifications/{id}/mark-read, POST /notifications/mark-all-read

**Design Status**: ✅ COMPLETED (2026-01-16)

---

### Phase 2: Task Breakdown ⏳ PENDING

**Command**: `/speckit.tasks` (run from branch 004-social-network)

**Expected Output**: [tasks.md](tasks.md)

**Task Organization** (preview):
- **Phase 1: Setup** - Alembic migration, enum types, validators
- **Phase 2: Tests (TDD)** - Contract tests for social-api.yaml validation
- **Phase 3: US1 - Feed Personalizado (P1)** - Feed service + API + frontend
- **Phase 4: US2 - Likes (P2)** - Like service + API + frontend with optimistic updates
- **Phase 5: US3 - Comentarios (P3)** - Comment service + rate limiting + HTML sanitization
- **Phase 6: US4 - Compartir (P4)** - Share service + API + frontend
- **Phase 7: US5 - Notificaciones (P5)** - Notification service + archiving + frontend
- **Phase 8: Polish** - Performance optimization, documentation, agent context update

**Task Status**: ⏳ PENDING (awaiting /speckit.tasks command)

---

### Phase 3: Implementation ⏳ BLOCKED (requires tasks.md)

**Command**: `/speckit.implement` (after tasks.md generated)

**Dependencies**:
- Existing Feature 003 (Follow/Unfollow) - ✅ Implemented
- check_mutual_follow() - ⚠️ Will be added in Phase 7 (for Feature 015 US3)

**Blockers**: None (Follow model exists, all dependencies met)

---

## Agent Context Updates

**File**: `CLAUDE.md`

**New Sections to Add**:

### Social Network Feature (Feature 004)

The Social Network feature provides a complete social layer for trip engagement including feed, likes, comments, shares, and notifications.

#### Feed Algorithm Pattern

Hybrid approach with followed users + popular backfill:

```python
# backend/src/services/feed_service.py
async def get_personalized_feed(
    db: AsyncSession,
    user_id: str,
    page: int = 1,
    limit: int = 10
) -> List[FeedItem]:
    """
    Get personalized feed for user.

    Algorithm:
    1. Get trips from followed users (chronological DESC)
    2. If < limit trips, backfill with popular community trips
    3. Combine and paginate
    """
    # Query 1: Trips from followed users
    followed_trips = (
        select(Trip)
        .join(Follow, Follow.following_id == Trip.user_id)
        .where(Follow.follower_id == user_id)
        .where(Trip.status == TripStatus.PUBLISHED)
        .order_by(Trip.created_at.desc())
        .limit(limit)
        .offset((page - 1) * limit)
    )

    result = await db.execute(followed_trips)
    trips = result.scalars().all()

    # Backfill with popular community trips if needed
    if len(trips) < limit:
        remaining = limit - len(trips)
        community_trips = (
            select(Trip)
            .where(Trip.status == TripStatus.PUBLISHED)
            .where(Trip.user_id != user_id)
            .order_by(Trip.likes_count.desc(), Trip.created_at.desc())
            .limit(remaining)
        )
        result = await db.execute(community_trips)
        trips.extend(result.scalars().all())

    return trips
```

#### Optimistic UI Updates Pattern

Custom hooks with rollback on error:

```typescript
// frontend/src/hooks/useLike.ts
export const useLike = (tripId: string) => {
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);

  const toggleLike = async () => {
    // Optimistic update
    const previousIsLiked = isLiked;
    const previousCount = likesCount;
    setIsLiked(!isLiked);
    setLikesCount(isLiked ? likesCount - 1 : likesCount + 1);

    try {
      if (isLiked) {
        await likeService.unlikeTrip(tripId);
      } else {
        await likeService.likeTrip(tripId);
      }
    } catch (error) {
      // Rollback on error
      setIsLiked(previousIsLiked);
      setLikesCount(previousCount);
      toast.error('Error al dar like');
    }
  };

  return { isLiked, likesCount, toggleLike };
};
```

#### Rate Limiting Pattern

Decorator for service methods:

```python
# backend/src/utils/rate_limiter.py
from functools import wraps
from datetime import datetime, timedelta

def rate_limit(max_calls: int, period_hours: int):
    """Rate limit decorator for service methods."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, db: AsyncSession, user_id: str, *args, **kwargs):
            # Check rate limit
            cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
            result = await db.execute(
                select(func.count())
                .select_from(Comment)
                .where(Comment.user_id == user_id)
                .where(Comment.created_at >= cutoff_time)
            )
            count = result.scalar()

            if count >= max_calls:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Has superado el límite de {max_calls} comentarios por hora"
                    }
                )

            return await func(self, db, user_id, *args, **kwargs)
        return wrapper
    return decorator

# Usage
class CommentService:
    @rate_limit(max_calls=10, period_hours=1)
    async def create_comment(self, db: AsyncSession, user_id: str, ...):
        # Implementation
```

#### Notification Archiving Pattern

Background job (cron/celery):

```python
# backend/src/services/notification_service.py
async def archive_old_notifications(db: AsyncSession):
    """Archive notifications older than 30 days."""
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    # Get old notifications
    result = await db.execute(
        select(Notification).where(Notification.created_at < cutoff_date)
    )
    old_notifications = result.scalars().all()

    # Move to archive
    for notif in old_notifications:
        archive = NotificationArchive(**notif.__dict__)
        db.add(archive)
        await db.delete(notif)

    await db.commit()
```

#### Infinite Scroll Pattern

Frontend custom hook with cursor-based pagination:

```typescript
// frontend/src/hooks/useFeed.ts
export const useInfiniteFeed = () => {
  const [trips, setTrips] = useState<FeedItem[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const fetchNextPage = async () => {
    if (isLoading || !hasMore) return;

    setIsLoading(true);
    try {
      const response = await feedService.getFeed(page + 1, 10);
      setTrips([...trips, ...response.trips]);
      setPage(page + 1);
      setHasMore(response.has_more);
    } catch (error) {
      toast.error('Error al cargar más viajes');
    } finally {
      setIsLoading(false);
    }
  };

  return { trips, fetchNextPage, hasMore, isLoading };
};
```

---

## Implementation Sequence

**Critical Path** (must implement in order):

1. ✅ Phase 0: Research (research.md) - COMPLETED
2. ✅ Phase 1: Design (data-model.md, contracts/, quickstart.md) - COMPLETED
3. ⏳ Phase 2: Tasks (tasks.md) - PENDING (run /speckit.tasks)
4. ⏳ Phase 3: Implementation (run /speckit.implement after tasks.md)

**Ready for**: `/speckit.tasks` command to generate task breakdown

**Branch**: `004-social-network` (active)
**Status**: Phase 1 complete, ready for Phase 2 task generation

---

**Plan Status**: ✅ COMPLETED (Phases 0-1)
**Date Completed**: 2026-01-16
**Ready for Tasks**: YES (run /speckit.tasks next)
