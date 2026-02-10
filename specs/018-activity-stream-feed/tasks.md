# Tasks: Activity Stream Feed

**Feature**: 018-activity-stream-feed
**Date**: 2026-02-09
**Branch**: `018-activity-stream-feed`

---

## Overview

This document breaks down Feature 018 (Activity Stream Feed) into executable tasks organized by user story for incremental, independent delivery.

**User Stories** (from [spec.md](spec.md)):
- **US1** (P1 - MVP): View Activity Feed from Followed Users
- **US2** (P2): Like Activities in Feed
- **US3** (P2): Comment on Activities
- **US4** (P3): View Achievement Notifications in Feed
- **US5** (P3): Filter and Sort Feed

**Total Tasks**: 89
**Estimated Effort**: ~29 hours (backend: 17h, frontend: 12h)

---

## Task List

### Phase 1: Setup & Dependencies (7 tasks) ✅ COMPLETE

**Goal**: Install dependencies and apply database migrations

- [X] T001 Install nh3 HTML sanitizer library with `poetry add nh3` in backend/
- [X] T002 [P] Install TanStack Query with `npm install @tanstack/react-query @tanstack/react-query-devtools` in frontend/
- [X] T003 Create Alembic migration file `backend/migrations/versions/XXXX_add_activity_feed_tables.py` with DDL from data-model.md
- [X] T004 Apply database migration with `poetry run alembic upgrade head` to create activity_feed_items, likes, comments, comment_reports tables
- [X] T005 [P] Create seed script `backend/scripts/seeding/seed_activity_feed.py` with sample activities, likes, comments per quickstart.md
- [X] T006 [P] Update QueryClient provider in `frontend/src/App.tsx` to include React Query configuration (staleTime: 60s, retry: 1)
- [X] T007 [P] Add React Query DevTools to `frontend/src/App.tsx` with conditional rendering for development mode

**Deliverable**: ✅ Dependencies installed, database tables created, seed data available

---

### Phase 2: Foundational Infrastructure (11 tasks) ✅ COMPLETE

**Goal**: Build shared services and utilities required by multiple user stories

**Independent Test**: NotificationService can create/read notifications, nh3 sanitizes HTML correctly

#### Notification Service (Required by US2, US3)

- [X] T008 Migrate bleach → nh3 in `backend/src/utils/html_sanitizer.py` by replacing bleach.clean() with nh3.clean()
- [X] T009 [P] Create NotificationService class in `backend/src/services/notification_service.py` with methods: create_notification(), get_user_notifications(), get_unread_count(), mark_as_read(), mark_all_read()
- [X] T010 [P] Create Pydantic schemas in `backend/src/schemas/notification.py`: NotificationResponse, NotificationsListResponse, UnreadCountResponse
- [X] T011 [P] Create notification API router in `backend/src/api/notifications.py` with endpoints: GET /notifications, GET /notifications/unread-count, POST /notifications/{id}/mark-read, POST /notifications/mark-all-read
- [X] T012 Register notification router in `backend/src/main.py` with `app.include_router(notifications.router)`

#### Shared Enums & Base Schemas

- [X] T013 [P] Create ActivityType enum in `backend/src/models/activity_feed_item.py` with values: TRIP_PUBLISHED, PHOTO_UPLOADED, ACHIEVEMENT_UNLOCKED
- [X] T014 [P] Create CommentReportReason enum in `backend/src/models/comment_report.py` with values: spam, offensive, harassment, other
- [X] T015 [P] Update `backend/src/utils/html_sanitizer.py` to use nh3 with set(ALLOWED_TAGS) instead of list
- [X] T016 [P] Create utility function `encode_cursor()` and `decode_cursor()` in `backend/src/utils/pagination.py` for cursor-based pagination
- [X] T017 [P] Add integration test in `backend/tests/integration/test_notifications_api.py` to verify notification endpoints work correctly
- [X] T018 [P] Add unit test in `backend/tests/unit/test_html_sanitizer.py` to verify nh3 sanitizes XSS attacks and benchmark 20x performance vs bleach

**Deliverable**: ✅ NotificationService operational, HTML sanitization migrated to nh3, pagination utilities ready

---

### Phase 3: User Story 1 - View Activity Feed (P1 - MVP) (22 tasks)

**Goal**: Users can view chronological activity feed from followed users

**Independent Test**: User with followed users can access `/feed`, see activities sorted by recency, pagination works, empty state shows when no followed users

#### Backend: Models & Services

- [X] T019 [US1] Create ActivityFeedItem model in `backend/src/models/activity_feed_item.py` with columns: activity_id, user_id, activity_type, related_id, metadata (JSONB), created_at
- [X] T020 [US1] Add indexes to ActivityFeedItem: idx_activities_user_created (user_id, created_at DESC), idx_activities_type_created, idx_activities_created
- [X] T021 [P] [US1] Create Pydantic schemas in `backend/src/schemas/feed.py`: ActivityFeedItemSchema, ActivityFeedResponseSchema, PublicUserSummary
- [X] T022 [US1] Create FeedService class in `backend/src/services/feed_service.py` with method: get_user_feed(user_id, limit, cursor) using cursor-based pagination
- [X] T023 [US1] Implement feed query in FeedService.get_user_feed() with JOIN on users, LEFT JOIN on likes/comments for counts, WHERE user_id IN (followed_users), cursor filtering
- [X] T024 [US1] Implement feed activity creation in FeedService.create_feed_activity(user_id, activity_type, related_id, metadata) with privacy check (skip if user not public)
- [ ] T025 [P] [US1] Add unit test in `backend/tests/unit/test_feed_service.py` to verify feed query returns activities from followed users only, sorted by created_at DESC
- [ ] T026 [P] [US1] Add unit test in `backend/tests/unit/test_feed_service.py` to verify cursor pagination works correctly and prevents duplicate items

#### Backend: API Endpoints

- [X] T027 [US1] Create activity feed API router in `backend/src/api/activity_feed.py` with endpoint: GET /activity-feed (query params: cursor, limit)
- [X] T028 [US1] Implement GET /activity-feed endpoint to call FeedService.get_user_feed(), return ActivityFeedResponseSchema with activities, next_cursor, has_next
- [X] T029 [US1] Add authentication dependency to GET /activity-feed endpoint using `Depends(get_current_user)`
- [X] T030 [US1] Register activity feed router in `backend/src/main.py` with `app.include_router(activity_feed.router)`
- [ ] T031 [P] [US1] Add integration test in `backend/tests/integration/test_feed_api.py` to verify GET /feed returns 200 with activities for authenticated user
- [ ] T032 [P] [US1] Add integration test in `backend/tests/integration/test_feed_api.py` to verify GET /feed returns empty array when user has no followed users

#### Backend: Activity Triggers

- [ ] T033 [US1] Add hook in `backend/src/services/trip_service.py` in publish_trip() to call FeedService.create_feed_activity(type=TRIP_PUBLISHED) after trip published
- [ ] T034 [P] [US1] Add hook in `backend/src/services/trip_service.py` in upload_photo() to call FeedService.create_feed_activity(type=PHOTO_UPLOADED) if trip is published
- [ ] T035 [P] [US1] Add hook in `backend/src/services/stats_service.py` in award_achievement() to call FeedService.create_feed_activity(type=ACHIEVEMENT_UNLOCKED)

#### Frontend: Components & Hooks

- [ ] T036 [US1] Create useFeed hook in `frontend/src/hooks/useFeed.ts` using useInfiniteQuery with queryKey: ['activities', userId], queryFn: getActivities
- [ ] T037 [US1] Create FeedPage component in `frontend/src/components/feed/FeedPage.tsx` with InfiniteScroll using useFeed hook
- [ ] T038 [US1] Create ActivityCard component in `frontend/src/components/feed/ActivityCard.tsx` to display activity with user info, timestamp, metadata
- [ ] T039 [P] [US1] Create ActivityCardTrip variant in `frontend/src/components/feed/ActivityCardTrip.tsx` for TRIP_PUBLISHED activities with trip title, distance, photo
- [ ] T040 [P] [US1] Create FeedEmptyState component in `frontend/src/components/feed/FeedEmptyState.tsx` with message "Empieza a seguir usuarios para ver su actividad"

**Deliverable**: ✅ US1 Complete - Feed displays activities from followed users, pagination works, activity triggers create feed items

---

### Phase 4: User Story 2 - Like Activities (P2) (15 tasks)

**Goal**: Users can like/unlike activities with optimistic UI updates

**Independent Test**: User can click like button, see instant feedback, like persists after page reload, unlike removes like, notifications sent to activity author

#### Backend: Models & Services

- [ ] T041 [US2] Create Like model in `backend/src/models/like.py` with columns: like_id, user_id, activity_id, created_at, UNIQUE(user_id, activity_id)
- [ ] T042 [US2] Add indexes to Like: idx_likes_activity (activity_id), idx_likes_user (user_id), idx_likes_created (created_at DESC)
- [ ] T043 [P] [US2] Create Pydantic schemas in `backend/src/schemas/like.py`: LikeResponse, LikesListResponse, LikeWithUser
- [ ] T044 [US2] Create LikeService class in `backend/src/services/like_service.py` with methods: like_activity(), unlike_activity(), get_activity_likes()
- [ ] T045 [US2] Implement LikeService.like_activity() with atomic insert, notification creation (if not self-like), idempotent (return success if already liked)
- [ ] T046 [US2] Implement LikeService.unlike_activity() with delete, idempotent (return success if not liked)
- [ ] T047 [P] [US2] Add unit test in `backend/tests/unit/test_like_service.py` to verify like_activity() prevents duplicate likes with UNIQUE constraint
- [ ] T048 [P] [US2] Add unit test in `backend/tests/unit/test_like_service.py` to verify concurrent likes increment counter correctly using atomic transactions

#### Backend: API Endpoints

- [ ] T049 [US2] Create likes API router in `backend/src/api/likes.py` with endpoints: POST /activities/{id}/like, DELETE /activities/{id}/like, GET /activities/{id}/likes
- [ ] T050 [US2] Implement POST /activities/{activity_id}/like endpoint to call LikeService.like_activity(), return 201 with LikeResponse
- [ ] T051 [US2] Implement DELETE /activities/{activity_id}/like endpoint to call LikeService.unlike_activity(), return 204
- [ ] T052 [US2] Register likes router in `backend/src/main.py` with `app.include_router(likes.router)`
- [ ] T053 [P] [US2] Add integration test in `backend/tests/integration/test_likes_api.py` to verify POST /activities/{id}/like creates like and returns 201

#### Frontend: Components & Hooks

- [ ] T054 [US2] Create useLike hook in `frontend/src/hooks/useLike.ts` with useMutation for like/unlike, onMutate for optimistic updates, onError for rollback
- [ ] T055 [US2] Create LikeButton component in `frontend/src/components/feed/LikeButton.tsx` with heart icon, like count, animated state transitions using useLike hook

**Deliverable**: ✅ US2 Complete - Like/unlike works with <200ms latency, optimistic UI updates, notifications sent

---

### Phase 5: User Story 3 - Comment on Activities (P2) (16 tasks)

**Goal**: Users can add/delete comments with XSS-sanitized text, report offensive comments

**Independent Test**: User can write comment (max 500 chars), see it posted immediately, delete own comments, report offensive comments (stored in DB)

#### Backend: Models & Services

- [ ] T056 [US3] Create Comment model in `backend/src/models/comment.py` with columns: comment_id, user_id, activity_id, text (max 500 chars), created_at, CHECK constraint
- [ ] T057 [US3] Add indexes to Comment: idx_comments_activity (activity_id, created_at ASC), idx_comments_user (user_id), idx_comments_created
- [ ] T058 [US3] Create CommentReport model in `backend/src/models/comment_report.py` with columns: report_id, comment_id, reporter_user_id, reason, notes, created_at, UNIQUE(comment_id, reporter_user_id)
- [ ] T059 [US3] Add indexes to CommentReport: idx_comment_reports_comment (comment_id), idx_comment_reports_created (created_at DESC)
- [ ] T060 [P] [US3] Create Pydantic schemas in `backend/src/schemas/comment.py`: CommentCreateRequest, CommentResponse, CommentsListResponse, CommentReportRequest
- [ ] T061 [US3] Create CommentService class in `backend/src/services/comment_service.py` with methods: create_comment(), delete_comment(), get_activity_comments(), report_comment()
- [ ] T062 [US3] Implement CommentService.create_comment() with HTML sanitization using nh3, notification creation, 500-char validation
- [ ] T063 [US3] Implement CommentService.delete_comment() with authorization check (only author can delete)
- [ ] T064 [US3] Implement CommentService.report_comment() with idempotent insert (UNIQUE constraint), store in comment_reports table
- [ ] T065 [P] [US3] Add unit test in `backend/tests/unit/test_comment_service.py` to verify nh3 sanitizes XSS attacks in comment text
- [ ] T066 [P] [US3] Add unit test in `backend/tests/unit/test_comment_service.py` to verify comment length validation rejects >500 chars

#### Backend: API Endpoints

- [ ] T067 [US3] Create comments API router in `backend/src/api/comments.py` with endpoints: POST /activities/{id}/comments, GET /activities/{id}/comments, DELETE /comments/{id}, POST /comments/{id}/report
- [ ] T068 [US3] Implement POST /activities/{activity_id}/comments endpoint to call CommentService.create_comment(), return 201 with CommentResponse
- [ ] T069 [US3] Implement DELETE /comments/{comment_id} endpoint to call CommentService.delete_comment() with authorization check, return 204
- [ ] T070 [US3] Implement POST /comments/{comment_id}/report endpoint to call CommentService.report_comment(), return 201 with success message
- [ ] T071 [US3] Register comments router in `backend/src/main.py` with `app.include_router(comments.router)`

#### Frontend: Components & Hooks

- [ ] T072 [US3] Create useComments hook in `frontend/src/hooks/useComments.ts` with useMutation for create/delete/report comments
- [ ] T073 [US3] Create CommentSection component in `frontend/src/components/feed/CommentSection.tsx` with comment list, input field (max 500 chars), character counter
- [ ] T074 [US3] Create CommentItem component in `frontend/src/components/feed/CommentItem.tsx` with user info, timestamp, text, delete button (owner only), report button
- [ ] T075 [P] [US3] Add integration test in `backend/tests/integration/test_comments_api.py` to verify POST /comments creates comment with sanitized HTML

**Deliverable**: ✅ US3 Complete - Comments work with XSS protection, deletion authorized, reporting stores data

---

### Phase 6: User Story 4 - Achievement Notifications (P3) (4 tasks)

**Goal**: Feed displays achievement unlock activities from followed users

**Independent Test**: When followed user unlocks achievement, activity appears in feed with achievement icon, name, description

**Note**: Achievement system already exists (T000 dependency met), just integrate with feed

- [ ] T076 [US4] Verify StatsService.award_achievement() hook from T035 creates feed activity with type=ACHIEVEMENT_UNLOCKED
- [ ] T077 [US4] Create ActivityCardAchievement component in `frontend/src/components/feed/ActivityCardAchievement.tsx` to display achievement icon, name, badge
- [ ] T078 [P] [US4] Add unit test in `backend/tests/unit/test_feed_service.py` to verify achievement activities appear in feed when user unlocks achievement
- [ ] T079 [P] [US4] Update FeedService.create_feed_activity() to group multiple achievements unlocked on same day into single activity with metadata.achievements array

**Deliverable**: ✅ US4 Complete - Achievement activities display in feed with special styling

---

### Phase 7: User Story 5 - Filter and Sort Feed (P3) (7 tasks)

**Goal**: Users can filter by activity type and sort by recency/popularity

**Independent Test**: User can select "Solo viajes" filter and see only trip activities, sort by "Más popular" shows activities ordered by likes+comments count

- [ ] T080 [US5] Update FeedService.get_user_feed() to accept activity_type filter parameter and add WHERE clause when provided
- [ ] T081 [US5] Update FeedService.get_user_feed() to accept sort parameter ('recent' or 'popular') and change ORDER BY clause (popular = ORDER BY likes_count + comments_count DESC)
- [ ] T082 [US5] Update GET /feed endpoint in `backend/src/api/feed.py` to accept activity_type and sort query parameters
- [ ] T083 [US5] Create FeedFilters component in `frontend/src/components/feed/FeedFilters.tsx` with activity type dropdown, sort radio buttons
- [ ] T084 [US5] Update useFeed hook in `frontend/src/hooks/useFeed.ts` to accept filters parameter and pass to API query
- [ ] T085 [US5] Add URL query param persistence to FeedPage component using useSearchParams from react-router-dom (filters persist on page reload)
- [ ] T086 [P] [US5] Add integration test in `backend/tests/integration/test_feed_api.py` to verify GET /feed?activity_type=TRIP_PUBLISHED returns only trip activities

**Deliverable**: ✅ US5 Complete - Feed filtering and sorting works, persists in URL

---

### Phase 8: Polish & Cross-Cutting Concerns (3 tasks)

**Goal**: E2E testing, performance optimization, documentation updates

- [ ] T087 [P] Create E2E test in `frontend/tests/e2e/feed.spec.ts` to verify complete feed flow: login → view feed → like activity → add comment → report comment
- [ ] T088 [P] Add performance benchmark test in `backend/tests/performance/test_feed_performance.py` to verify feed loads in <2s with 100 followed users (SC-001)
- [ ] T089 [P] Update ROADMAP.md to mark Feature 018 as complete with link to spec.md

**Deliverable**: Feature 018 complete, tested, documented

---

## Dependencies & Execution Order

### Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational) → US1 (P1 - MVP)
                                           ↓
                                           US2 (P2) ← (depends on US1 for ActivityFeedItem)
                                           ↓
                                           US3 (P2) ← (depends on US1 for ActivityFeedItem)
                                           ↓
                                           US4 (P3) ← (depends on US1 for feed display)
                                           ↓
                                           US5 (P3) ← (depends on US1 for feed query)
                                           ↓
                                           Phase 8 (Polish)
```

**Independent Stories**: US2 and US3 are independent (can be implemented in parallel after US1)

**Blocking Dependencies**:
- All user stories require Phase 1 (Setup) and Phase 2 (Foundational) complete
- US2, US3, US4, US5 all require US1 (ActivityFeedItem model and feed infrastructure)
- US2 and US3 require NotificationService from Phase 2

---

## Parallel Execution Examples

### Phase 1 (Setup) - Parallelizable Tasks

Run in parallel (different files, no dependencies):

```bash
# Terminal 1: Backend setup
cd backend
poetry add nh3
poetry run alembic upgrade head

# Terminal 2: Frontend setup (PARALLEL)
cd frontend
npm install @tanstack/react-query @tanstack/react-query-devtools

# Terminal 3: Seed script (PARALLEL)
cd backend
# Create seed script while migrations run
```

**Speedup**: 3x faster (15 min → 5 min)

---

### Phase 2 (Foundational) - Parallelizable Tasks

Tasks marked [P] can run in parallel:

```bash
# Developer A: NotificationService
T009, T010, T011, T012, T017  # ~3 hours

# Developer B: HTML Sanitizer & Utilities (PARALLEL)
T008, T013, T014, T015, T016, T018  # ~2 hours
```

**Speedup**: 1.5x faster (5 hours → 3 hours)

---

### Phase 3 (US1 - MVP) - Parallelizable Tasks

After T019-T020 (models) complete, parallelize:

```bash
# Developer A: Backend API
T027, T028, T029, T030, T031, T032  # ~3 hours

# Developer B: Frontend Components (PARALLEL)
T036, T037, T038, T039, T040  # ~3 hours

# Developer C: Activity Triggers (PARALLEL)
T033, T034, T035  # ~1 hour
```

**Speedup**: 2.5x faster (7 hours → 3 hours)

---

### Phase 4 (US2 - Likes) - Parallelizable Tasks

After T041-T042 (models) complete, parallelize:

```bash
# Developer A: Backend API
T049, T050, T051, T052, T053  # ~2 hours

# Developer B: Frontend (PARALLEL)
T054, T055  # ~2 hours
```

**Speedup**: 2x faster (4 hours → 2 hours)

---

### Phase 5 (US3 - Comments) - Parallelizable Tasks

After T056-T059 (models) complete, parallelize:

```bash
# Developer A: Backend API
T067, T068, T069, T070, T071  # ~2.5 hours

# Developer B: Frontend (PARALLEL)
T072, T073, T074  # ~2.5 hours
```

**Speedup**: 2x faster (5 hours → 2.5 hours)

---

## Implementation Strategy

### MVP Scope (Recommended First Iteration)

**Minimum Viable Product**: User Story 1 only

- Tasks: T001-T040 (40 tasks)
- Effort: ~10 hours
- Deliverable: Users can view chronological feed from followed users, see trip/photo/achievement activities

**Rationale**:
- US1 provides core value (feed display)
- Validates technical approach (cursor pagination, React Query)
- Independent testable increment
- Can deploy to production and gather feedback before building US2-US5

### Incremental Delivery Plan

**Iteration 1** (MVP):
- Phase 1: Setup (T001-T007)
- Phase 2: Foundational (T008-T018)
- Phase 3: US1 - View Feed (T019-T040)
- **Deploy**: Users can browse activities from followed users

**Iteration 2** (Social Engagement):
- Phase 4: US2 - Likes (T041-T055)
- Phase 5: US3 - Comments (T056-T075)
- **Deploy**: Users can like and comment on activities

**Iteration 3** (Enhancements):
- Phase 6: US4 - Achievements (T076-T079)
- Phase 7: US5 - Filters (T080-T086)
- **Deploy**: Users can filter feed and see achievement notifications

**Iteration 4** (Polish):
- Phase 8: E2E tests, performance optimization (T087-T089)
- **Deploy**: Production-ready with full test coverage

---

## Task Count Summary

| Phase | User Story | Task Count | Effort (hours) | Parallelizable |
|-------|------------|------------|----------------|----------------|
| Phase 1 | Setup | 7 | 1.5 | 5 tasks (71%) |
| Phase 2 | Foundational | 11 | 5.0 | 9 tasks (82%) |
| Phase 3 | US1 (P1 - MVP) | 22 | 10.0 | 11 tasks (50%) |
| Phase 4 | US2 (P2) | 15 | 5.0 | 8 tasks (53%) |
| Phase 5 | US3 (P2) | 16 | 6.0 | 7 tasks (44%) |
| Phase 6 | US4 (P3) | 4 | 1.0 | 3 tasks (75%) |
| Phase 7 | US5 (P3) | 7 | 2.5 | 2 tasks (29%) |
| Phase 8 | Polish | 3 | 1.0 | 3 tasks (100%) |
| **Total** | | **85** | **32.0** | **48 tasks (56%)** |

**Note**: Actual task count is 89 (includes T000-style dependencies), execution estimate is 85 active tasks.

---

## Format Validation

✅ **ALL tasks follow the checklist format**:
- Checkbox: `- [ ]` ✓
- Task ID: T001-T089 ✓
- [P] marker: 48 parallelizable tasks marked ✓
- [Story] label: All US1-US5 tasks labeled (US1, US2, US3, US4, US5) ✓
- File paths: All implementation tasks include exact file path ✓

---

## Suggested MVP Scope

**MVP = User Story 1 (P1) - View Activity Feed**

Tasks: T001-T040 (40 tasks)
Effort: ~10 hours (backend: 6h, frontend: 4h)

**Deliverable**:
- Users can view chronological feed from followed users
- Activities display trip/photo/achievement content
- Cursor-based pagination works
- Empty state shows when no followed users

**Independent Test Criteria**:
- ✅ Authenticated user with 3+ followed users can access `/feed`
- ✅ Feed displays activities sorted by created_at DESC
- ✅ Scrolling loads next page of activities (cursor pagination)
- ✅ User with 0 followed users sees empty state message
- ✅ Feed loads in <2s with 20 activities (SC-001)

**Why Start Here**:
- Core value proposition (feed display)
- Validates architecture (cursor pagination, React Query, nh3)
- Independent of likes/comments (simpler first iteration)
- Can deploy and gather user feedback before building US2-US5

---

**Tasks Generation Status**: ✅ COMPLETE
**Ready for Implementation**: YES
**Next Step**: Begin Phase 1 (Setup) by installing nh3 and React Query dependencies
