# Implementation Plan: Activity Stream Feed

**Branch**: `018-activity-stream-feed` | **Date**: 2026-02-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/018-activity-stream-feed/spec.md`

## Summary

Implement a social activity feed that displays chronological activities from followed users, including trip publications, photo uploads, and achievement unlocks. Users can interact through likes and comments, fostering community engagement. The feature supports filtering by activity type and sorting by recency or popularity.

**Primary Requirements**:
- Chronological feed showing activities from followed users only (FR-001)
- Support for trip, photo, and achievement activity types (FR-002)
- Like/unlike functionality with real-time UI updates (FR-006, FR-007)
- Comment system with 500-character limit and sanitization (FR-012, FR-018)
- Pagination with 20 activities per batch (FR-003)
- Performance: <2s initial load, <200ms like/unlike latency (FR-027, SC-005)

**Technical Approach**:
- Backend: FastAPI endpoints for feed generation, likes, comments with eager loading to prevent N+1 queries
- Database: New tables for ActivityFeedItem, Like, Comment, Notification with appropriate indexes
- Frontend: React components with infinite scroll, optimistic UI updates for likes
- Event-driven: Trigger feed activity creation on trip publish, photo upload, achievement unlock

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic (backend) | React 18, React Query/SWR (frontend state), Axios (HTTP)
**Storage**: PostgreSQL (production), SQLite (development) - activity_feed_items, likes, comments, notifications tables
**Testing**: pytest (backend unit/integration), Playwright (frontend E2E)
**Target Platform**: Web application (responsive, mobile-first design)
**Project Type**: Web (backend API + frontend SPA)
**Performance Goals**:
  - Feed load: <2s for 20 activities (SC-001)
  - Like/unlike: <200ms perceived latency (SC-005)
  - Support 100+ followed users without degradation (SC-006)
  - Concurrent operations without data inconsistencies (SC-007)
**Constraints**:
  - Comments max 500 characters (FR-012)
  - Max 20 activities per page (FR-003)
  - Chronological ordering by default (most recent first)
  - Activity privacy respects source content privacy
**Scale/Scope**:
  - Expected: 1000+ users, 10k+ activities, 100k+ likes/comments
  - Feed retention: 90 days of activities
  - Activity types: 3 (trip, photo, achievement)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability

- ✅ **PEP 8 compliance**: All backend code will follow PEP 8 with black formatter
- ✅ **Single Responsibility**: Services separated (FeedService, LikeService, CommentService, NotificationService)
- ✅ **Type hints**: All functions will include type annotations
- ✅ **Docstrings**: Public APIs documented with Google-style docstrings
- ✅ **No magic numbers**: Constants in config (FEED_PAGE_SIZE=20, COMMENT_MAX_LENGTH=500)
- ✅ **Linting**: black + ruff will pass with zero warnings

**Status**: ✅ PASS - Standard architecture patterns apply

### II. Testing Standards (Non-Negotiable)

- ✅ **TDD Workflow**: Tests written first for all services and endpoints
- ✅ **Unit Tests**: FeedService, LikeService, CommentService, NotificationService (target ≥90% coverage)
- ✅ **Integration Tests**:
  - Feed generation with joins (user, likes count, comments count)
  - Like/unlike operations with concurrency scenarios
  - Comment create/delete with XSS sanitization
  - Notification triggers on like/comment
- ✅ **Contract Tests**: OpenAPI schemas for all feed endpoints
- ✅ **Edge Cases**: Empty feed, blocked users, deleted activities, concurrent likes
- ✅ **Performance Tests**: Feed query performance with 100+ followed users, N+1 query prevention

**Status**: ✅ PASS - Comprehensive test coverage required and planned

### III. User Experience Consistency

- ✅ **Spanish Text**: All error messages, timestamps ("hace 2 horas"), UI labels in Spanish
- ✅ **Consistent API Response**:
  ```json
  {
    "success": true,
    "data": { "activities": [...], "pagination": {...} },
    "error": null
  }
  ```
- ✅ **Field-specific Validation**: Comment length, activity type, user permissions
- ✅ **Loading/Empty/Error States**:
  - Loading: Skeleton cards
  - Empty: "Empieza a seguir usuarios para ver su actividad"
  - Error: "Error al cargar el feed. Intenta de nuevo."
- ✅ **Visual Feedback**: Like button animation, comment submit disabled during posting
- ✅ **Accessibility**: ARIA labels, keyboard navigation, screen reader support
- ✅ **Relative Timestamps**: Spanish localized ("hace 2 horas", "ayer", "hace 3 días")

**Status**: ✅ PASS - UX patterns align with existing ContraVento features

### IV. Performance Requirements

- ✅ **API Response Times**:
  - Feed load: <2s (FR-027)
  - Like/unlike: <200ms (SC-005)
- ✅ **Database Optimization**:
  - Indexes on activity_feed_items.created_at, likes.activity_id, comments.activity_id
  - Eager loading for likes_count, comments_count using subqueries
  - Pagination with cursor-based or offset (20 items per page)
- ✅ **N+1 Prevention**: Single query with joins for feed items + aggregated counts
- ✅ **Asynchronous Operations**: Background notification creation (Celery if heavy load)
- ✅ **Caching**: NEEDS CLARIFICATION - Redis cache for feed pages? Or rely on DB indexes?

**Status**: ⚠️ NEEDS CLARIFICATION - Caching strategy (Redis vs DB-only)

### Security & Data Protection

- ✅ **Authentication**: Feed endpoint requires JWT token (get_current_user dependency)
- ✅ **Authorization**: Users can only see activities from followed users (not all users)
- ✅ **SQL Injection Prevention**: SQLAlchemy ORM only, no raw SQL
- ✅ **XSS Prevention**: HTML sanitization on comment text (FR-018)
- ✅ **Input Validation**: Pydantic schemas for comment text, activity filters
- ✅ **Privacy**: Private trips don't generate feed activities (activity creation conditional on trip.is_public)

**Status**: ✅ PASS - Security measures align with existing auth patterns

### Development Workflow

- ✅ **Feature Branch**: `018-activity-stream-feed` (already created)
- ✅ **Conventional Commits**: feat(feed), test(feed), fix(comments), etc.
- ✅ **PR Requirements**: Tests, coverage report, API contract validation
- ✅ **Database Migrations**: Alembic migrations for new tables (reversible)
- ✅ **Documentation**: OpenAPI schemas, data-model.md, quickstart.md

**Status**: ✅ PASS - Standard workflow applies

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | - | - |

**Notes**:
- ⚠️ **Caching Strategy NEEDS CLARIFICATION**: Research needed to determine if Redis caching is required for feed pages or if PostgreSQL indexes + query optimization are sufficient for <2s load time with 100+ followed users.

## Project Structure

### Documentation (this feature)

```text
specs/018-activity-stream-feed/
├── spec.md              # Feature specification ✅ COMPLETE
├── checklists/
│   └── requirements.md  # Quality validation checklist ✅ COMPLETE
├── plan.md              # This file (implementation plan) 🔄 IN PROGRESS
├── research.md          # Phase 0 output (to be created by /speckit.plan)
├── data-model.md        # Phase 1 output (to be created by /speckit.plan)
├── quickstart.md        # Phase 1 output (to be created by /speckit.plan)
├── contracts/           # Phase 1 output (OpenAPI schemas)
└── tasks.md             # Phase 2 output (created by /speckit.tasks - NOT by /speckit.plan)
```

### Source Code (repository root)

```text
# Option 2: Web application (backend API + frontend SPA)

backend/
├── src/
│   ├── models/
│   │   ├── activity_feed_item.py  # NEW - ActivityFeedItem model
│   │   ├── like.py                 # NEW - Like model
│   │   ├── comment.py              # NEW - Comment model
│   │   └── notification.py         # MODIFIED - Add LIKE, COMMENT notification types
│   ├── schemas/
│   │   ├── feed.py                 # NEW - ActivityFeedItemSchema, FeedResponseSchema
│   │   ├── like.py                 # NEW - LikeSchema, LikeCreateSchema
│   │   └── comment.py              # NEW - CommentSchema, CommentCreateSchema
│   ├── services/
│   │   ├── feed_service.py         # NEW - Feed generation, filtering, sorting
│   │   ├── like_service.py         # NEW - Like/unlike operations
│   │   ├── comment_service.py      # NEW - Comment CRUD, sanitization
│   │   └── notification_service.py # MODIFIED - Add like/comment notification creation
│   ├── api/
│   │   ├── feed.py                 # NEW - Feed endpoints (GET /feed, filters, pagination)
│   │   ├── likes.py                # NEW - Like endpoints (POST /activities/{id}/like, DELETE)
│   │   └── comments.py             # NEW - Comment endpoints (POST /activities/{id}/comments, DELETE)
│   └── utils/
│       └── feed_helpers.py         # NEW - Activity type enums, feed event triggers
└── tests/
    ├── unit/
    │   ├── test_feed_service.py    # NEW
    │   ├── test_like_service.py    # NEW
    │   └── test_comment_service.py # NEW
    ├── integration/
    │   ├── test_feed_api.py        # NEW
    │   ├── test_likes_api.py       # NEW
    │   └── test_comments_api.py    # NEW
    └── contract/
        └── feed-api.yaml           # NEW - OpenAPI contract

frontend/
├── src/
│   ├── components/
│   │   ├── feed/
│   │   │   ├── FeedPage.tsx           # NEW - Main feed container
│   │   │   ├── ActivityCard.tsx       # NEW - Single activity card
│   │   │   ├── ActivityCardTrip.tsx   # NEW - Trip activity variant
│   │   │   ├── ActivityCardPhoto.tsx  # NEW - Photo activity variant
│   │   │   ├── ActivityCardAchievement.tsx # NEW - Achievement activity variant
│   │   │   ├── LikeButton.tsx         # NEW - Like/unlike button with optimistic UI
│   │   │   ├── CommentSection.tsx     # NEW - Comment list + input
│   │   │   ├── CommentItem.tsx        # NEW - Single comment display
│   │   │   ├── FeedFilters.tsx        # NEW - Activity type filters, sort options
│   │   │   └── FeedEmptyState.tsx     # NEW - Empty feed message + follow suggestions
│   │   └── common/
│   │       └── InfiniteScroll.tsx     # NEW - Infinite scroll component
│   ├── hooks/
│   │   ├── useFeed.ts                 # NEW - Feed data fetching, pagination
│   │   ├── useLike.ts                 # NEW - Like/unlike mutations
│   │   └── useComments.ts             # NEW - Comment create/delete mutations
│   ├── services/
│   │   ├── feedService.ts             # NEW - API calls for feed
│   │   ├── likeService.ts             # NEW - API calls for likes
│   │   └── commentService.ts          # NEW - API calls for comments
│   └── types/
│       └── feed.ts                    # NEW - TypeScript types for activities, likes, comments
└── tests/
    └── e2e/
        ├── feed.spec.ts               # NEW - Feed load, pagination, filters
        ├── likes.spec.ts              # NEW - Like/unlike interactions
        └── comments.spec.ts           # NEW - Comment create, delete

# Database Migrations
backend/migrations/versions/
└── XXXX_add_activity_feed_tables.py   # NEW - Create activity_feed_items, likes, comments tables
```

**Structure Decision**:
- **Web application** (Option 2) selected because feature requires both backend API and frontend UI
- **Backend**: New models (ActivityFeedItem, Like, Comment), services (FeedService, LikeService, CommentService), and API routes
- **Frontend**: New feed page with activity cards, like button, comment section components
- **Database**: New tables for activity tracking, social interactions, and notifications

## Dependencies

### Internal Dependencies

**Required (Blockers)**:
- ✅ **Feature 004 (Social Network)**: Follow/Following system MUST exist to determine whose activities appear in feed
  - **Status**: ✅ COMPLETE (merged to develop) - Follow, Unfollow, Followers list, Following list implemented
  - **Models needed**: UserFollower relationship (user_id, followed_user_id)
  - **Impact**: Feed query filters activities WHERE author_id IN (followed_users)

**Optional (Progressive Enhancement)**:
- ⚠️ **Achievement System**: NEEDS CLARIFICATION - Does this exist or is it planned?
  - **If exists**: Feed can display achievement activities immediately
  - **If not exists**: Feature 018 can launch with US1-US3 (feed, likes, comments) and defer US4 (achievements) until achievement system is ready
  - **Approach**: Implement ActivityFeedItem with type=ACHIEVEMENT_UNLOCKED but gate achievement activity creation behind achievement system availability check

- ⚠️ **Notification System**: NEEDS CLARIFICATION - Does basic notification infrastructure exist?
  - **If exists**: Like/comment notifications work immediately (FR-011, FR-017)
  - **If not exists**: Implement basic Notification model and API as part of this feature
  - **Approach**: Create minimal notification system (Notification model, GET /notifications endpoint) scoped to feed interactions only

### External Dependencies

- ✅ **FastAPI**: Existing framework for API endpoints
- ✅ **SQLAlchemy 2.0**: Existing ORM for database models
- ✅ **React 18**: Existing frontend framework
- 🆕 **React Query or SWR**: NEW - State management for feed data (choose one during research)
- 🆕 **HTML Sanitizer**: NEW - Python library (bleach or html5lib) for comment XSS prevention
- ✅ **Pydantic**: Existing schema validation

## Phase 0: Research & Unknowns

**Status**: ✅ COMPLETE (with 1 blocker)

### Research Completed

All research tasks have been executed and findings documented in [research.md](research.md):

1. ✅ **Caching Strategy**: PostgreSQL-only (no Redis) for MVP
   - Decision: PostgreSQL with optimized indexes meets <2s requirement (100-300ms projected)
   - Add Redis only if p95 latency > 1s (unlikely at current scale)

2. ✅ **Frontend State Management**: React Query (TanStack Query)
   - Decision: Use `@tanstack/react-query` for built-in infinite scroll and optimistic updates
   - Impact: +10 KB gzipped, -75% boilerplate vs manual state management

3. ✅ **HTML Sanitization Library**: Migrate bleach → nh3
   - Decision: Replace deprecated bleach with nh3 (20x faster, Rust-based security)
   - Migration effort: ~30 minutes

4. ✅ **Achievement System Status**: EXISTS - Fully implemented
   - Confirmation: Complete implementation ready to use (models, service, API endpoints)
   - No additional work required

5. ✅ **Notification System Status**: PARTIAL - Models exist, service/API missing
   - Confirmation: Notification model in database, need to build service/API (~6 hours)
   - Required for FR-011 (like notifications) and FR-017 (comment notifications)

6. ✅ **Feed Activity Trigger Pattern**: Service hooks (observer pattern)
   - Decision: Explicit service calls in TripService, StatsService to create feed activities
   - Pattern: Simple, testable, no event dispatcher needed

7. ⚠️ **Comment Moderation**: BLOCKED - User decision required
   - **Question**: Include comment reporting system in MVP?
   - **Options**:
     - A: Basic report button + manual moderation (+2-3 days)
     - B: No reporting in MVP (simplest, defer to future)
     - C: Report button only, no UI (+1 day) - **RECOMMENDED**
   - **Action Required**: User must choose A, B, or C before Phase 1

### Research Artifacts

**Created**: ✅ [`research.md`](research.md) (comprehensive technical decisions report)

**Summary**:
- 6 of 7 research tasks completed
- 1 blocker identified (comment moderation user decision)
- All technical unknowns resolved except user-choice feature scope

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE

### Artifacts Created

1. ✅ **[data-model.md](data-model.md)**:
   - ActivityFeedItem entity (activity_id, user_id, activity_type, related_id, created_at, metadata)
   - Like entity (like_id, user_id, activity_id, created_at, unique constraint)
   - Comment entity (comment_id, user_id, activity_id, text, created_at)
   - CommentReport entity (report_id, comment_id, reporter_user_id, reason, notes)
   - Complete DDL for PostgreSQL and SQLite
   - Query patterns for feed generation, comments, admin moderation
   - Sample data and migration plan

2. ✅ **[contracts/feed-api.yaml](contracts/feed-api.yaml)**: OpenAPI 3.0 schema
   - GET /feed (cursor-based pagination, filters, sort)
   - POST /activities/{activity_id}/like, DELETE /activities/{activity_id}/like
   - GET /activities/{activity_id}/likes (like list for modal)
   - POST /activities/{activity_id}/comments, GET /activities/{activity_id}/comments
   - DELETE /comments/{comment_id}
   - POST /comments/{comment_id}/report (Option C: report button, no UI)
   - Complete request/response schemas with validation

3. ✅ **[quickstart.md](quickstart.md)**: Developer setup guide
   - Backend setup (nh3 installation, migration, seeding)
   - Frontend setup (React Query installation, provider setup)
   - API testing with curl examples (login, feed, like, comment, report)
   - Postman collection import instructions
   - Testing commands (unit, integration, contract, E2E)
   - Admin SQL queries for comment moderation (Option C)
   - Troubleshooting guide
   - Performance benchmarking

4. ✅ **Agent Context Update**: CLAUDE.md updated
   - Added: TanStack Query 5.x (React Query), nh3 0.3.2
   - Database: activity_feed_items, likes, comments, comment_reports tables
   - Technologies documented for Feature 018

## Phase 2: Task Breakdown

**Status**: ⏳ PENDING (to be created by `/speckit.tasks` command)

**Next Command**: `/speckit.tasks` (NOT executed by `/speckit.plan`)

---

## Implementation Phases (Preview)

*These will be formalized in tasks.md by `/speckit.tasks` command*

### Phase 1: Backend Models & Migrations
- Create ActivityFeedItem, Like, Comment, Notification models
- Alembic migrations for new tables
- Seed script for test data

### Phase 2: Feed Service
- FeedService.get_user_feed() with pagination
- Filter by activity type
- Sort by recency vs popularity
- N+1 query prevention with eager loading

### Phase 3: Like & Comment Services
- LikeService.like(), unlike() with atomic operations
- CommentService.create(), delete() with XSS sanitization
- NotificationService integration

### Phase 4: API Endpoints
- GET /feed, POST /activities/{id}/like, POST /activities/{id}/comments
- OpenAPI schema validation
- Integration tests

### Phase 5: Frontend Components
- FeedPage with infinite scroll
- ActivityCard variants (trip, photo, achievement)
- LikeButton with optimistic UI
- CommentSection with real-time updates

### Phase 6: E2E Testing
- Feed pagination flow
- Like/unlike interactions
- Comment create/delete
- Empty state handling

---

**Plan Status**: 🔄 IN PROGRESS - Phase 0 research pending
**Next Action**: Execute research tasks to resolve NEEDS CLARIFICATION items
**Blocked By**: User decision on comment moderation (spec clarification)
