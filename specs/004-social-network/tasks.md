# Task Breakdown: Red Social y Feed de Ciclistas

**Feature**: 004-social-network
**Branch**: `004-social-network`
**Date**: 2026-01-16
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Overview

This document breaks down Feature 004 (Social Network) into executable tasks following **TDD methodology** (tests FIRST). Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks**: 156
**User Stories**: 5 (Feed P1, Likes P2, Comments P3, Shares P4, Notifications P5)
**Testing Strategy**: Contract tests → Unit tests → Implementation (TDD workflow)

---

## Task Format

All tasks follow strict checklist format:

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **TaskID**: Sequential number (T001, T002, ...)
- **[P]**: Parallelizable task (different files, no dependencies)
- **[Story]**: User story label ([US1], [US2], etc.) - ONLY for user story phases
- **Description**: Clear action with exact file path

---

## Phase 1: Setup (7 tasks) ✅ COMPLETED

**Goal**: Initialize database tables, utilities, and foundational infrastructure

- [X] T001 Create Alembic migration for social tables in backend/migrations/versions/20260116_2222_8e8f4eaba47d_create_social_network_tables_likes_.py
- [X] T002 [P] Create HTML sanitizer utility in backend/src/utils/html_sanitizer.py (extended with sanitize_comment, validate_comment_content)
- [X] T003 [P] Create rate limiter decorator utility in backend/src/utils/rate_limiter.py
- [X] T004 [P] Create NotificationType enum in backend/src/models/notification.py (plus Like, Comment, Share, Notification, NotificationArchive models)
- [X] T005 Apply migration to create likes, comments, shares, notifications, notifications_archive tables
- [X] T006 Verify migration with alembic history and database inspection
- [X] T007 Seed test data with users, trips, and follows for manual testing (skipped - existing test data sufficient)

---

## Phase 2: Foundational - Contract Tests (TDD) (5 tasks) ✅ COMPLETED

**Goal**: Validate OpenAPI contract compliance for ALL social endpoints

**Independent Test**: Contract tests pass for all 15 endpoints defined in contracts/social-api.yaml

- [X] T008 [P] Create contract test for Feed endpoints in backend/tests/contract/test_feed_contract.py
- [X] T009 [P] Create contract test for Like endpoints in backend/tests/contract/test_likes_contract.py
- [X] T010 [P] Create contract test for Comment endpoints in backend/tests/contract/test_comments_contract.py
- [X] T011 [P] Create contract test for Share endpoints in backend/tests/contract/test_shares_contract.py
- [X] T012 [P] Create contract test for Notification endpoints in backend/tests/contract/test_notifications_contract.py

---

## Phase 3: User Story 1 - Feed Personalizado (P1) 🎯 MVP (28 tasks) ✅ COMPLETE

**Goal**: Implement personalized feed with hybrid algorithm (chronological + popular backfill)

**Backend Status**: ✅ 18/18 tasks completed (Tests + Implementation)
**Frontend Status**: ✅ 10/10 tasks completed (Services + Hooks + Components + Page + Routing)
**Manual Testing**: ✅ 2/2 tests completed (T039-T040) - All success criteria met!
**Follow/Unfollow UI**: ✅ COMPLETED (2026-01-19) - See [SESSION_FOLLOW_UI.md](SESSION_FOLLOW_UI.md)

### Follow/Unfollow UI Integration (Additional Work - 2026-01-19)

This work extends US1 with follow/unfollow functionality across all pages:

**Completed Features**:

- ✅ Follow/Unfollow from user profile pages (integrated with backend API)
- ✅ Follow/Unfollow from feed cards (both `/` and `/feed`)
- ✅ Follow/Unfollow from trip detail page
- ✅ Automatic state synchronization across all components (no page refresh)
- ✅ Clickable author links navigate to user profiles

**Git Commits** (pushed to `origin/004-social-network`):

- `5b9f5af` - Integrate Follow/Unfollow UI with profile API
- `8d3ad83` - Clickable author links in feed cards
- `f59d60c` - Synchronize follow button state across all feed items
- `0ef1712` - Add author section with follow button to trip detail page
- `d435926` - Load UserProfile when building trip author summary
- `9fc9f2c` - Use correct field name profile_photo_url from UserProfile
- `0ff2349` - Align author section with metadata in trip detail

**Files Modified**:

- Backend: `backend/src/schemas/trip.py`, `backend/src/services/trip_service.py`
- Frontend: `frontend/src/hooks/useFollow.ts`, `frontend/src/hooks/useFeed.ts`, `frontend/src/components/feed/FeedItem.tsx`, `frontend/src/components/trips/PublicTripCard.tsx`, `frontend/src/pages/TripDetailPage.tsx`, `frontend/src/pages/TripDetailPage.css`, `frontend/src/types/trip.ts`

**Technical Achievements**:

- Optimistic UI with cross-component state synchronization using custom events
- Efficient cached data updates (no full refetch)
- Proper event bubbling control for nested clickable elements
- SQLAlchemy eager loading for related entities (User → UserProfile)

**Independent Test**:
- Create multiple users with published trips
- Follow some users
- Access /feed endpoint
- Verify feed shows trips from followed users + popular backfill
- Verify chronological ordering and pagination
- Verify infinite scroll works

### Tests (TDD - Write FIRST) (10 tasks) ✅ COMPLETED

- [X] T013 [P] [US1] Write unit test for FeedService.get_personalized_feed() in backend/tests/unit/test_feed_service.py
- [X] T014 [P] [US1] Write unit test for FeedService.get_followed_trips() in backend/tests/unit/test_feed_service.py
- [X] T015 [P] [US1] Write unit test for FeedService.get_community_trips() backfill in backend/tests/unit/test_feed_service.py
- [X] T016 [P] [US1] Write unit test for feed pagination logic in backend/tests/unit/test_feed_service.py
- [X] T017 [P] [US1] Write unit test for feed when user follows nobody in backend/tests/unit/test_feed_service.py
- [X] T018 [P] [US1] Write integration test for GET /feed (authenticated) in backend/tests/integration/test_feed_api.py
- [X] T019 [P] [US1] Write integration test for GET /feed with pagination in backend/tests/integration/test_feed_api.py
- [X] T020 [P] [US1] Write integration test for GET /feed (unauthorized - 401) in backend/tests/integration/test_feed_api.py
- [X] T021 [P] [US1] Write integration test for feed ordering (chronological DESC) in backend/tests/integration/test_feed_api.py
- [X] T022 [P] [US1] Write integration test for feed with interaction counters in backend/tests/integration/test_feed_api.py

### Backend Implementation (8 tasks) ✅ COMPLETED

- [X] T023 [US1] Create FeedItem Pydantic schema in backend/src/schemas/feed.py
- [X] T024 [US1] Create FeedResponse Pydantic schema in backend/src/schemas/feed.py
- [X] T025 [US1] Implement FeedService.get_personalized_feed() with hybrid algorithm in backend/src/services/feed_service.py
- [X] T026 [US1] Implement FeedService._get_followed_trips() helper in backend/src/services/feed_service.py
- [X] T027 [US1] Implement FeedService._get_community_trips() helper (popular backfill) in backend/src/services/feed_service.py
- [X] T028 [US1] Create GET /feed endpoint in backend/src/api/feed.py
- [X] T029 [US1] Register feed router in backend/src/main.py
- [X] T030 [US1] Run unit tests to verify FeedService implementation (SC-001: <1s p95)

### Frontend Implementation (10 tasks) ✅ COMPLETED

- [X] T031 [P] [US1] Create FeedService with getFeed() API call in frontend/src/services/feedService.ts
- [X] T032 [P] [US1] Create useFeed() custom hook with pagination in frontend/src/hooks/useFeed.ts
- [X] T033 [P] [US1] Create useInfiniteFeed() custom hook for infinite scroll in frontend/src/hooks/useFeed.ts
- [X] T034 [P] [US1] Create FeedItem component (trip card) in frontend/src/components/feed/FeedItem.tsx
- [X] T035 [P] [US1] Create FeedList component with infinite scroll in frontend/src/components/feed/FeedList.tsx
- [X] T036 [P] [US1] Create FeedSkeleton loading component in frontend/src/components/feed/FeedSkeleton.tsx
- [X] T037 [US1] Create FeedPage main page in frontend/src/pages/FeedPage.tsx
- [X] T038 [US1] Add /feed route to React Router in frontend/src/App.tsx
- [X] T039 [US1] Manual test: Verify feed loads in <1s with 10 trips (SC-001)
- [X] T040 [US1] Manual test: Verify infinite scroll loads next page <500ms (SC-002)

---

## Phase 4: User Story 2 - Likes/Me Gusta (P2) 🎯 MVP (30 tasks)

**Goal**: Implement like/unlike functionality with optimistic UI updates

**Independent Test**:
- View a published trip
- Click like button → verify counter increments, icon changes
- Click unlike button → verify counter decrements, icon changes
- Verify like appears in "Viajes que me gustan" section
- Verify trip owner sees like in "who liked" list

### Tests (TDD - Write FIRST) (11 tasks)

- [ ] T041 [P] [US2] Write unit test for LikeService.like_trip() in backend/tests/unit/test_like_service.py
- [ ] T042 [P] [US2] Write unit test for LikeService.unlike_trip() in backend/tests/unit/test_like_service.py
- [ ] T043 [P] [US2] Write unit test for LikeService.get_trip_likes() pagination in backend/tests/unit/test_like_service.py
- [ ] T044 [P] [US2] Write unit test for preventing duplicate likes (FR-010) in backend/tests/unit/test_like_service.py
- [ ] T045 [P] [US2] Write unit test for preventing self-likes (FR-011) in backend/tests/unit/test_like_service.py
- [ ] T046 [P] [US2] Write integration test for POST /trips/{id}/like in backend/tests/integration/test_likes_api.py
- [ ] T047 [P] [US2] Write integration test for DELETE /trips/{id}/like in backend/tests/integration/test_likes_api.py
- [ ] T048 [P] [US2] Write integration test for GET /trips/{id}/likes in backend/tests/integration/test_likes_api.py
- [ ] T049 [P] [US2] Write integration test for like (unauthorized - 401) in backend/tests/integration/test_likes_api.py
- [ ] T050 [P] [US2] Write integration test for duplicate like (400) in backend/tests/integration/test_likes_api.py
- [ ] T051 [P] [US2] Write integration test for self-like (400) in backend/tests/integration/test_likes_api.py

### Backend Implementation (9 tasks)

- [ ] T052 [US2] Create Like model in backend/src/models/like.py
- [ ] T053 [US2] Create LikeResponse Pydantic schema in backend/src/schemas/like.py
- [ ] T054 [US2] Create LikesListResponse Pydantic schema in backend/src/schemas/like.py
- [ ] T055 [US2] Implement LikeService.like_trip() with validations in backend/src/services/like_service.py
- [ ] T056 [US2] Implement LikeService.unlike_trip() in backend/src/services/like_service.py
- [ ] T057 [US2] Implement LikeService.get_trip_likes() with pagination in backend/src/services/like_service.py
- [ ] T058 [US2] Create POST /trips/{id}/like endpoint in backend/src/api/likes.py
- [ ] T059 [US2] Create DELETE /trips/{id}/like endpoint in backend/src/api/likes.py
- [ ] T060 [US2] Create GET /trips/{id}/likes endpoint in backend/src/api/likes.py

### Frontend Implementation (10 tasks)

- [ ] T061 [P] [US2] Create LikeService with likeTrip(), unlikeTrip() in frontend/src/services/likeService.ts
- [ ] T062 [P] [US2] Create useLike() custom hook with optimistic updates in frontend/src/hooks/useLike.ts
- [ ] T063 [P] [US2] Create LikeButton component with heart icon in frontend/src/components/likes/LikeButton.tsx
- [ ] T064 [P] [US2] Create LikesList modal component in frontend/src/components/likes/LikesList.tsx
- [ ] T065 [US2] Integrate LikeButton into FeedItem component in frontend/src/components/feed/FeedItem.tsx
- [ ] T066 [US2] Integrate LikeButton into TripDetailPage in frontend/src/pages/TripDetailPage.tsx
- [ ] T067 [US2] Register likes router in backend/src/main.py
- [ ] T068 [US2] Run unit tests to verify LikeService implementation (SC-006: <200ms)
- [ ] T069 [US2] Manual test: Verify like toggle responds in <200ms (SC-006)
- [ ] T070 [US2] Manual test: Verify optimistic update rollback on error

---

## Phase 5: User Story 3 - Comentarios (P3) (35 tasks)

**Goal**: Implement comment CRUD with rate limiting and HTML sanitization

**Independent Test**:
- View a published trip
- Post a comment (1-500 chars) → verify appears immediately
- Edit own comment → verify "editado" marker appears
- Delete own comment → verify removal
- Verify rate limit (max 10 comments/hour)
- Verify HTML sanitization prevents XSS

### Tests (TDD - Write FIRST) (13 tasks)

- [ ] T071 [P] [US3] Write unit test for CommentService.create_comment() in backend/tests/unit/test_comment_service.py
- [ ] T072 [P] [US3] Write unit test for CommentService.update_comment() in backend/tests/unit/test_comment_service.py
- [ ] T073 [P] [US3] Write unit test for CommentService.delete_comment() in backend/tests/unit/test_comment_service.py
- [ ] T074 [P] [US3] Write unit test for CommentService.get_trip_comments() pagination in backend/tests/unit/test_comment_service.py
- [ ] T075 [P] [US3] Write unit test for comment rate limiting (10/hour) in backend/tests/unit/test_comment_service.py
- [ ] T076 [P] [US3] Write unit test for HTML sanitization in backend/tests/unit/test_html_sanitizer.py
- [ ] T077 [P] [US3] Write integration test for POST /trips/{id}/comments in backend/tests/integration/test_comments_api.py
- [ ] T078 [P] [US3] Write integration test for GET /trips/{id}/comments in backend/tests/integration/test_comments_api.py
- [ ] T079 [P] [US3] Write integration test for PUT /comments/{id} (edit) in backend/tests/integration/test_comments_api.py
- [ ] T080 [P] [US3] Write integration test for DELETE /comments/{id} in backend/tests/integration/test_comments_api.py
- [ ] T081 [P] [US3] Write integration test for comment (unauthorized - 401) in backend/tests/integration/test_comments_api.py
- [ ] T082 [P] [US3] Write integration test for rate limit exceeded (429) in backend/tests/integration/test_comments_api.py
- [ ] T083 [P] [US3] Write integration test for XSS prevention (sanitization) in backend/tests/integration/test_comments_api.py

### Backend Implementation (12 tasks)

- [ ] T084 [US3] Create Comment model in backend/src/models/comment.py
- [ ] T085 [US3] Create CommentCreateInput Pydantic schema in backend/src/schemas/comment.py
- [ ] T086 [US3] Create CommentUpdateInput Pydantic schema in backend/src/schemas/comment.py
- [ ] T087 [US3] Create CommentResponse Pydantic schema in backend/src/schemas/comment.py
- [ ] T088 [US3] Create CommentsListResponse Pydantic schema in backend/src/schemas/comment.py
- [ ] T089 [US3] Implement @rate_limit decorator in backend/src/utils/rate_limiter.py
- [ ] T090 [US3] Implement HTML sanitization function in backend/src/utils/html_sanitizer.py
- [ ] T091 [US3] Implement CommentService.create_comment() with rate limiting in backend/src/services/comment_service.py
- [ ] T092 [US3] Implement CommentService.update_comment() with authorization in backend/src/services/comment_service.py
- [ ] T093 [US3] Implement CommentService.delete_comment() with authorization in backend/src/services/comment_service.py
- [ ] T094 [US3] Implement CommentService.get_trip_comments() with pagination in backend/src/services/comment_service.py
- [ ] T095 [US3] Create POST/GET /trips/{id}/comments endpoints in backend/src/api/comments.py

### Frontend Implementation (10 tasks)

- [ ] T096 [P] [US3] Create CommentService with API calls in frontend/src/services/commentService.ts
- [ ] T097 [P] [US3] Create useComment() custom hook in frontend/src/hooks/useComment.ts
- [ ] T098 [P] [US3] Create CommentForm component (add/edit) in frontend/src/components/comments/CommentForm.tsx
- [ ] T099 [P] [US3] Create CommentItem component (with edit/delete) in frontend/src/components/comments/CommentItem.tsx
- [ ] T100 [P] [US3] Create CommentList component with pagination in frontend/src/components/comments/CommentList.tsx
- [ ] T101 [US3] Create PUT /comments/{id} endpoint in backend/src/api/comments.py
- [ ] T102 [US3] Create DELETE /comments/{id} endpoint in backend/src/api/comments.py
- [ ] T103 [US3] Integrate CommentList into TripDetailPage in frontend/src/pages/TripDetailPage.tsx
- [ ] T104 [US3] Register comments router in backend/src/main.py
- [ ] T105 [US3] Run unit tests to verify CommentService implementation (SC-013: <300ms)

---

## Phase 6: User Story 4 - Compartir Viajes (P4) (25 tasks)

**Goal**: Implement share functionality with optional commentary

**Independent Test**:
- View a trip
- Share trip with optional comment (0-200 chars)
- Verify share appears in user's feed
- Verify followers see shared trip
- Verify share counter updates

### Tests (TDD - Write FIRST) (9 tasks)

- [ ] T106 [P] [US4] Write unit test for ShareService.share_trip() in backend/tests/unit/test_share_service.py
- [ ] T107 [P] [US4] Write unit test for ShareService.get_trip_shares() pagination in backend/tests/unit/test_share_service.py
- [ ] T108 [P] [US4] Write unit test for ShareService.delete_share() in backend/tests/unit/test_share_service.py
- [ ] T109 [P] [US4] Write integration test for POST /trips/{id}/share in backend/tests/integration/test_shares_api.py
- [ ] T110 [P] [US4] Write integration test for GET /trips/{id}/shares in backend/tests/integration/test_shares_api.py
- [ ] T111 [P] [US4] Write integration test for share with comment in backend/tests/integration/test_shares_api.py
- [ ] T112 [P] [US4] Write integration test for share without comment in backend/tests/integration/test_shares_api.py
- [ ] T113 [P] [US4] Write integration test for share (unauthorized - 401) in backend/tests/integration/test_shares_api.py
- [ ] T114 [P] [US4] Write integration test for deleted original trip handling in backend/tests/integration/test_shares_api.py

### Backend Implementation (8 tasks)

- [ ] T115 [US4] Create Share model in backend/src/models/share.py
- [ ] T116 [US4] Create ShareCreateInput Pydantic schema in backend/src/schemas/share.py
- [ ] T117 [US4] Create ShareResponse Pydantic schema in backend/src/schemas/share.py
- [ ] T118 [US4] Create SharesListResponse Pydantic schema in backend/src/schemas/share.py
- [ ] T119 [US4] Implement ShareService.share_trip() in backend/src/services/share_service.py
- [ ] T120 [US4] Implement ShareService.get_trip_shares() with pagination in backend/src/services/share_service.py
- [ ] T121 [US4] Create POST /trips/{id}/share endpoint in backend/src/api/shares.py
- [ ] T122 [US4] Create GET /trips/{id}/shares endpoint in backend/src/api/shares.py

### Frontend Implementation (8 tasks)

- [ ] T123 [P] [US4] Create ShareService with API calls in frontend/src/services/shareService.ts
- [ ] T124 [P] [US4] Create useShare() custom hook in frontend/src/hooks/useShare.ts
- [ ] T125 [P] [US4] Create ShareButton component with modal in frontend/src/components/shares/ShareButton.tsx
- [ ] T126 [P] [US4] Create SharesList component in frontend/src/components/shares/SharesList.tsx
- [ ] T127 [US4] Integrate ShareButton into TripDetailPage in frontend/src/pages/TripDetailPage.tsx
- [ ] T128 [US4] Register shares router in backend/src/main.py
- [ ] T129 [US4] Run unit tests to verify ShareService implementation (SC-023: <500ms)
- [ ] T130 [US4] Manual test: Verify share appears in follower's feed

---

## Phase 7: User Story 5 - Notificaciones (P5) (26 tasks)

**Goal**: Implement notification generation with archiving and unread badge

**Independent Test**:
- Create a trip with User A
- Like/comment/share trip with User B
- Verify User A receives notifications
- Verify unread count badge updates
- Mark notifications as read
- Verify archiving after 30 days

### Tests (TDD - Write FIRST) (11 tasks)

- [ ] T131 [P] [US5] Write unit test for NotificationService.create_like_notification() in backend/tests/unit/test_notification_service.py
- [ ] T132 [P] [US5] Write unit test for NotificationService.create_comment_notification() in backend/tests/unit/test_notification_service.py
- [ ] T133 [P] [US5] Write unit test for NotificationService.create_share_notification() in backend/tests/unit/test_notification_service.py
- [ ] T134 [P] [US5] Write unit test for NotificationService.get_user_notifications() in backend/tests/unit/test_notification_service.py
- [ ] T135 [P] [US5] Write unit test for NotificationService.mark_as_read() in backend/tests/unit/test_notification_service.py
- [ ] T136 [P] [US5] Write unit test for NotificationService.archive_old_notifications() in backend/tests/unit/test_notification_service.py
- [ ] T137 [P] [US5] Write integration test for GET /notifications in backend/tests/integration/test_notifications_api.py
- [ ] T138 [P] [US5] Write integration test for GET /notifications/unread-count in backend/tests/integration/test_notifications_api.py
- [ ] T139 [P] [US5] Write integration test for POST /notifications/{id}/mark-read in backend/tests/integration/test_notifications_api.py
- [ ] T140 [P] [US5] Write integration test for POST /notifications/mark-all-read in backend/tests/integration/test_notifications_api.py
- [ ] T141 [P] [US5] Write integration test for notification filtering (is_read) in backend/tests/integration/test_notifications_api.py

### Backend Implementation (8 tasks)

- [ ] T142 [US5] Create Notification model in backend/src/models/notification.py
- [ ] T143 [US5] Create NotificationArchive model in backend/src/models/notification.py
- [ ] T144 [US5] Create NotificationResponse Pydantic schema in backend/src/schemas/notification.py
- [ ] T145 [US5] Create NotificationsListResponse Pydantic schema in backend/src/schemas/notification.py
- [ ] T146 [US5] Implement NotificationService.create_notification() in backend/src/services/notification_service.py
- [ ] T147 [US5] Implement NotificationService.get_user_notifications() with filtering in backend/src/services/notification_service.py
- [ ] T148 [US5] Implement NotificationService.mark_as_read() and mark_all_as_read() in backend/src/services/notification_service.py
- [ ] T149 [US5] Implement NotificationService.archive_old_notifications() background job in backend/src/services/notification_service.py

### Frontend Implementation (7 tasks)

- [ ] T150 [P] [US5] Create NotificationService with API calls in frontend/src/services/notificationService.ts
- [ ] T151 [P] [US5] Create useNotifications() custom hook with unread count in frontend/src/hooks/useNotifications.ts
- [ ] T152 [P] [US5] Create NotificationBadge component in frontend/src/components/notifications/NotificationBadge.tsx
- [ ] T153 [P] [US5] Create NotificationItem component in frontend/src/components/notifications/NotificationItem.tsx
- [ ] T154 [P] [US5] Create NotificationList drawer component in frontend/src/components/notifications/NotificationList.tsx
- [ ] T155 [US5] Create NotificationsPage in frontend/src/pages/NotificationsPage.tsx
- [ ] T156 [US5] Add /notifications route to React Router in frontend/src/App.tsx

---

## Phase 8: Polish & Cross-Cutting Concerns (3 tasks)

**Goal**: Finalize endpoints, run all tests, optimize performance, update documentation

- [ ] T157 Create GET /notifications, GET /notifications/unread-count, POST /notifications/{id}/mark-read endpoints in backend/src/api/notifications.py
- [ ] T158 Register notifications router in backend/src/main.py and run full test suite (≥90% coverage)
- [ ] T159 Update CLAUDE.md with Social Network patterns (feed algorithm, optimistic updates, rate limiting, archiving)

---

## Dependencies

### Story Dependencies

```
Setup (Phase 1)
  ↓
Foundational - Contract Tests (Phase 2)
  ↓
Feed (US1) ────┐
               ├─→ Likes (US2) ────┐
               │                   ├─→ Notificaciones (US5)
Comentarios (US3) ─┘                │
               │                    │
Compartir (US4) ────────────────────┘
```

**Independent Stories**:
- ✅ Feed (US1) - No dependencies (uses existing Follow and Trip models)
- ✅ Likes (US2) - Requires Feed for display, but can be implemented independently
- ✅ Comments (US3) - Independent from Likes and Shares
- ✅ Shares (US4) - Requires Feed to show shared trips, independent otherwise
- ⚠️ Notifications (US5) - Depends on Likes, Comments, Shares (notification triggers)

**Suggested Implementation Order**:
1. Setup + Contract Tests (Phases 1-2)
2. Feed (US1) → Likes (US2) → Comments (US3) → Shares (US4) → Notifications (US5)
3. Polish (Phase 8)

### Task Dependencies Within User Stories

**Feed (US1)**:
- Tests (T013-T022) can run in parallel
- Backend implementation sequential: Schemas → Service → API
- Frontend implementation: Service → Hooks → Components → Page

**Likes (US2)**:
- Tests (T041-T051) can run in parallel
- Backend implementation sequential: Model → Schemas → Service → API
- Frontend implementation: Service → Hook → Components → Integration

**Comments (US3)**:
- Tests (T071-T083) can run in parallel
- Backend utilities (T089-T090) before Service
- Frontend components can be developed in parallel

**Shares (US4)**:
- Tests (T106-T114) can run in parallel
- Similar pattern to Likes

**Notifications (US5)**:
- Tests (T131-T141) can run in parallel
- Backend models and service before endpoints
- Frontend components can be developed in parallel

---

## Parallel Execution Opportunities

### Phase 1 (Setup) - 4 parallel tasks
```bash
# Can run simultaneously:
- T002 (HTML sanitizer)
- T003 (Rate limiter)
- T004 (NotificationType enum)
# After T001 migration is created
```

### Phase 2 (Contract Tests) - 5 parallel tasks
```bash
# All contract tests can run in parallel:
- T008 (Feed contract)
- T009 (Likes contract)
- T010 (Comments contract)
- T011 (Shares contract)
- T012 (Notifications contract)
```

### User Story Tests - All tests within a story can run in parallel
```bash
# Example for US1 (Feed):
- T013-T022 (10 tests in parallel)

# Example for US2 (Likes):
- T041-T051 (11 tests in parallel)
```

### Frontend Components - All components for a story can run in parallel
```bash
# Example for US1 (Feed):
- T031 (FeedService)
- T032 (useFeed hook)
- T033 (useInfiniteFeed hook)
- T034 (FeedItem component)
- T035 (FeedList component)
- T036 (FeedSkeleton component)
```

**Total Parallelization Potential**: ~60-70% of tasks can run in parallel within their phases

---

## Implementation Strategy

### MVP Scope (Recommended First Release)

**Minimum Viable Product** includes:
- ✅ **Phase 1**: Setup (database, utilities)
- ✅ **Phase 2**: Contract tests
- ✅ **Phase 3**: Feed (US1) - Core social feature
- ✅ **Phase 4**: Likes (US2) - Simple interaction
- ⏳ **Phase 8**: Polish (partial - basic testing and docs)

**Deferred for v2**:
- Comments (US3)
- Shares (US4)
- Notifications (US5)

**MVP Justification**:
- Feed + Likes provide core social value (discovery + feedback)
- Comments/Shares/Notifications are enhancements
- MVP can ship faster with 70 tasks instead of 159 tasks
- Incremental delivery allows user feedback before building complex features

### Full Feature Scope

**Complete Implementation** includes all 5 user stories:
- Feed (US1) - 28 tasks
- Likes (US2) - 30 tasks
- Comments (US3) - 35 tasks
- Shares (US4) - 25 tasks
- Notifications (US5) - 26 tasks
- Setup + Tests + Polish - 15 tasks

**Total**: 159 tasks

### Incremental Delivery Plan

```
Week 1: Setup + Contract Tests (Phases 1-2)
Week 2: Feed (US1) - 28 tasks
Week 3: Likes (US2) - 30 tasks
------- MVP Release -------
Week 4: Comments (US3) - 35 tasks
Week 5: Shares (US4) - 25 tasks
Week 6: Notifications (US5) - 26 tasks
Week 7: Polish + Performance tuning
```

---

## Testing Strategy

### TDD Workflow (Strictly Enforced)

**For each user story**:
1. **Red**: Write failing tests (contract → unit → integration)
2. **Green**: Implement minimal code to pass tests
3. **Refactor**: Optimize while keeping tests passing
4. **Verify**: Run test suite, check coverage ≥90%

### Test Organization

**Contract Tests** (Phase 2):
- Validate OpenAPI schema compliance
- Run before any implementation
- Ensure API contracts are correct

**Unit Tests** (per user story):
- Test service layer business logic in isolation
- Mock database and external dependencies
- Fast execution (<1s per test)

**Integration Tests** (per user story):
- Test API endpoints end-to-end
- Use in-memory SQLite database
- Verify request/response flow

### Coverage Requirements

**Minimum 90% coverage** across:
- `backend/src/services/feed_service.py`
- `backend/src/services/like_service.py`
- `backend/src/services/comment_service.py`
- `backend/src/services/share_service.py`
- `backend/src/services/notification_service.py`
- `backend/src/utils/rate_limiter.py`
- `backend/src/utils/html_sanitizer.py`

---

## Success Metrics

### Performance Targets (from Success Criteria)

| Endpoint | Target (p95) | SC Reference |
|----------|--------------|--------------|
| GET /feed | <1s | SC-001 |
| GET /feed (scroll) | <500ms | SC-002 |
| POST /trips/{id}/like | <200ms | SC-006 |
| GET /trips/{id}/likes | <500ms | SC-010 |
| POST /trips/{id}/comments | <300ms | SC-013 |
| GET /trips/{id}/comments | <500ms | SC-015 |
| POST /trips/{id}/share | <500ms | SC-023 |
| GET /notifications | <500ms | SC-028 |
| GET /notifications/unread-count | <100ms | SC-030 |

### Acceptance Criteria Validation

**Each user story must pass ALL acceptance scenarios** defined in spec.md:

- **US1 (Feed)**: 6 acceptance scenarios
- **US2 (Likes)**: 6 acceptance scenarios
- **US3 (Comments)**: 6 acceptance scenarios
- **US4 (Shares)**: 6 acceptance scenarios
- **US5 (Notifications)**: 6 acceptance scenarios

**Total**: 30 acceptance scenarios to validate manually using quickstart.md

---

## Task Validation Checklist

✅ **Format Validation**:
- All 159 tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- All TaskIDs are sequential (T001-T159)
- All user story tasks have [US#] labels
- All parallelizable tasks have [P] markers

✅ **Completeness Validation**:
- Each user story has tests FIRST (TDD workflow)
- Each user story has backend implementation
- Each user story has frontend implementation
- All file paths are absolute and specific

✅ **Dependency Validation**:
- Setup phase before all user stories
- Contract tests before implementation
- Tests before implementation within each story
- Stories can be implemented in any order (mostly independent)

---

**Tasks Status**: ✅ COMPLETED
**Date Generated**: 2026-01-16
**Ready for Implementation**: YES (run /speckit.implement)
