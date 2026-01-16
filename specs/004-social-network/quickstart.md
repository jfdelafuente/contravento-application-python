# Quick Start: Red Social y Feed de Ciclistas

**Feature**: 004-social-network
**Date**: 2026-01-16
**Status**: ✅ Ready for implementation

## Overview

This guide provides quick testing scenarios for all user stories in the Social Network feature.

## Prerequisites

```bash
# Start local development server
cd backend
poetry install
poetry run alembic upgrade head  # Apply migrations

# Create test users
poetry run python scripts/create_verified_user.py --username testuser --password TestPass123!
poetry run python scripts/create_verified_user.py --username maria --password TestPass123!
poetry run python scripts/create_verified_user.py --username carlos --password TestPass123!

# Start backend
poetry run uvicorn src.main:app --reload

# API docs at: http://localhost:8000/docs
```

## Test Data Setup

### 1. Create Follow Relationships

```bash
# Login as testuser
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Save access_token from response
export TOKEN="<access_token>"

# Follow maria
curl -X POST http://localhost:8000/users/maria/follow \
  -H "Authorization: Bearer $TOKEN"

# Follow carlos
curl -X POST http://localhost:8000/users/carlos/follow \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Create Sample Trips

```bash
# Login as maria
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "password": "TestPass123!"
  }'

export MARIA_TOKEN="<access_token>"

# Create published trip
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $MARIA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Bikepacking Pirineos",
    "description": "Viaje de 5 días por los Pirineos con camping salvaje y paisajes increíbles. Ruta exigente pero muy gratificante.",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "distance_km": 320.5,
    "difficulty": "HARD",
    "tags": ["bikepacking", "montaña", "camping"]
  }'

# Save trip_id from response
export TRIP_ID="<trip_id>"

# Publish trip
curl -X POST http://localhost:8000/trips/$TRIP_ID/publish \
  -H "Authorization: Bearer $MARIA_TOKEN"
```

---

## User Story 1: Feed Personalizado (P1)

**Goal**: Ver viajes de usuarios seguidos en feed personalizado

### Scenario 1.1: Feed with Followed Users

```bash
# Get personalized feed (testuser follows maria)
curl -X GET http://localhost:8000/feed \
  -H "Authorization: Bearer $TOKEN"

# Expected response (SC-001: <1s p95):
{
  "trips": [
    {
      "trip_id": "uuid",
      "title": "Ruta Bikepacking Pirineos",
      "author": {
        "username": "maria",
        "full_name": "María García"
      },
      "photos": [...],
      "distance_km": 320.5,
      "likes_count": 0,
      "comments_count": 0,
      "is_liked_by_me": false,
      "created_at": "2024-06-01T10:00:00Z"
    }
  ],
  "total_count": 1,
  "page": 1,
  "limit": 10,
  "has_more": false
}
```

### Scenario 1.2: Feed with Pagination (FR-005)

```bash
# Get second page
curl -X GET "http://localhost:8000/feed?page=2&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Expected: Empty array or additional trips
```

### Scenario 1.3: Infinite Scroll (FR-006)

**Frontend implementation** (see research.md for infinite scroll pattern):

```typescript
// Frontend: useInfiniteScroll hook
const { trips, fetchNextPage, hasMore, isLoading } = useInfiniteFeed();

// Load more on scroll
useEffect(() => {
  const handleScroll = () => {
    if (window.scrollY + window.innerHeight >= document.body.scrollHeight - 100) {
      if (hasMore && !isLoading) {
        fetchNextPage();
      }
    }
  };

  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, [hasMore, isLoading, fetchNextPage]);
```

---

## User Story 2: Likes (P2)

**Goal**: Dar y quitar "me gusta" a viajes

### Scenario 2.1: Like a Trip (FR-009)

```bash
# Like maria's trip
curl -X POST http://localhost:8000/trips/$TRIP_ID/like \
  -H "Authorization: Bearer $TOKEN"

# Expected response (SC-006: <200ms):
{
  "success": true,
  "message": "Me gusta añadido correctamente",
  "likes_count": 1,
  "is_liked": true
}

# Verify in feed
curl -X GET http://localhost:8000/feed \
  -H "Authorization: Bearer $TOKEN"

# Expected: is_liked_by_me = true, likes_count = 1
```

### Scenario 2.2: Cannot Like Own Trip (FR-011)

```bash
# Login as maria (trip owner)
# Try to like own trip
curl -X POST http://localhost:8000/trips/$TRIP_ID/like \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected error:
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "No puedes dar me gusta a tu propio viaje"
  }
}
```

### Scenario 2.3: Unlike a Trip (FR-012)

```bash
# Unlike trip
curl -X DELETE http://localhost:8000/trips/$TRIP_ID/like \
  -H "Authorization: Bearer $TOKEN"

# Expected response:
{
  "success": true,
  "message": "Me gusta eliminado correctamente",
  "likes_count": 0,
  "is_liked": false
}
```

### Scenario 2.4: View Likes List (FR-013)

```bash
# Like trip from multiple users
# (repeat login + like with different users: carlos, testuser)

# Get likes list
curl -X GET http://localhost:8000/trips/$TRIP_ID/likes \
  -H "Authorization: Bearer $TOKEN"

# Expected response (SC-010: <500ms):
{
  "likes": [
    {
      "user": {
        "username": "testuser",
        "full_name": null
      },
      "created_at": "2024-06-01T10:30:00Z"
    },
    {
      "user": {
        "username": "carlos",
        "full_name": "Carlos López"
      },
      "created_at": "2024-06-01T10:25:00Z"
    }
  ],
  "total_count": 2,
  "page": 1,
  "limit": 20,
  "has_more": false
}
```

---

## User Story 3: Comentarios (P3)

**Goal**: Comentar en viajes

### Scenario 3.1: Add Comment (FR-016)

```bash
# Post comment
curl -X POST http://localhost:8000/trips/$TRIP_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "¡Increíble ruta! Me encantaría hacerla algún día. ¿Cómo fue el camping salvaje?"
  }'

# Expected response (SC-013: <300ms):
{
  "comment_id": "uuid",
  "trip_id": "uuid",
  "author": {
    "username": "testuser",
    "full_name": null
  },
  "content": "¡Increíble ruta! Me encantaría hacerla algún día. ¿Cómo fue el camping salvaje?",
  "created_at": "2024-06-01T11:00:00Z",
  "updated_at": null,
  "is_edited": false
}

# Save comment_id
export COMMENT_ID="<comment_id>"
```

### Scenario 3.2: Comment Validation (FR-017)

```bash
# Too short comment (empty after trimming)
curl -X POST http://localhost:8000/trips/$TRIP_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "   "}'

# Expected error:
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El comentario debe tener entre 1 y 500 caracteres",
    "field": "content"
  }
}

# Too long comment (>500 chars)
curl -X POST http://localhost:8000/trips/$TRIP_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "<501 characters>"
  }'

# Expected error:
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El comentario debe tener entre 1 y 500 caracteres",
    "field": "content"
  }
}
```

### Scenario 3.3: Rate Limiting (FR-018)

```bash
# Post 10 comments rapidly
for i in {1..10}; do
  curl -X POST http://localhost:8000/trips/$TRIP_ID/comments \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"Comment $i\"}"
done

# 11th comment should fail with 429
curl -X POST http://localhost:8000/trips/$TRIP_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Comment 11"}'

# Expected error:
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Has superado el límite de 10 comentarios por hora. Intenta más tarde."
  }
}
```

### Scenario 3.4: Edit Comment (FR-019)

```bash
# Edit own comment
curl -X PUT http://localhost:8000/trips/$TRIP_ID/comments/$COMMENT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "¡Increíble ruta! Me encantaría hacerla pronto. ¿Cómo fue el camping salvaje?"
  }'

# Expected response (SC-018: <300ms):
{
  "comment_id": "uuid",
  "content": "¡Increíble ruta! Me encantaría hacerla pronto. ¿Cómo fue el camping salvaje?",
  "updated_at": "2024-06-01T11:15:00Z",
  "is_edited": true
}
```

### Scenario 3.5: Cannot Edit Other's Comment (FR-021)

```bash
# Login as carlos
# Try to edit testuser's comment
curl -X PUT http://localhost:8000/trips/$TRIP_ID/comments/$COMMENT_ID \
  -H "Authorization: Bearer $CARLOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Edited by attacker"}'

# Expected error:
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Solo puedes editar tus propios comentarios"
  }
}
```

### Scenario 3.6: Delete Comment (FR-020)

```bash
# Delete own comment
curl -X DELETE http://localhost:8000/trips/$TRIP_ID/comments/$COMMENT_ID \
  -H "Authorization: Bearer $TOKEN"

# Expected response (SC-020: <300ms):
{
  "success": true,
  "message": "Comentario eliminado correctamente"
}

# Verify deletion
curl -X GET http://localhost:8000/trips/$TRIP_ID/comments

# Expected: Comment not in list
```

### Scenario 3.7: View Comments List (FR-017)

```bash
# Get comments for trip
curl -X GET http://localhost:8000/trips/$TRIP_ID/comments

# Expected response (SC-015: <500ms):
{
  "comments": [
    {
      "comment_id": "uuid",
      "author": {...},
      "content": "...",
      "created_at": "2024-06-01T11:00:00Z",
      "is_edited": false
    }
  ],
  "total_count": 1,
  "page": 1,
  "limit": 20,
  "has_more": false
}
```

---

## User Story 4: Compartir Viajes (P4)

**Goal**: Compartir viajes con comentario opcional

### Scenario 4.1: Share Trip with Comment (FR-023)

```bash
# Share trip with commentary
curl -X POST http://localhost:8000/trips/$TRIP_ID/share \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Esta ruta es perfecta para iniciarse en bikepacking. ¡Muy recomendable!"
  }'

# Expected response (SC-023: <500ms):
{
  "success": true,
  "message": "Viaje compartido correctamente",
  "share_id": "uuid",
  "shares_count": 1
}

# Save share_id
export SHARE_ID="<share_id>"
```

### Scenario 4.2: Share Trip without Comment (FR-024)

```bash
# Share trip without commentary
curl -X POST http://localhost:8000/trips/$TRIP_ID/share \
  -H "Authorization: Bearer $TOKEN"

# Expected response:
{
  "success": true,
  "message": "Viaje compartido correctamente",
  "share_id": "uuid",
  "shares_count": 2
}
```

### Scenario 4.3: View Shares List (FR-025)

```bash
# Get shares list
curl -X GET http://localhost:8000/trips/$TRIP_ID/shares

# Expected response (SC-025: <500ms):
{
  "shares": [
    {
      "user": {
        "username": "testuser",
        "full_name": null
      },
      "comment": "Esta ruta es perfecta para iniciarse en bikepacking. ¡Muy recomendable!",
      "created_at": "2024-06-01T12:00:00Z"
    }
  ],
  "total_count": 1,
  "page": 1,
  "limit": 20,
  "has_more": false
}
```

---

## User Story 5: Notificaciones (P5)

**Goal**: Recibir notificaciones de interacciones sociales

### Scenario 5.1: Notification on Like (FR-028)

```bash
# Login as maria (trip owner)
# Check notifications after testuser liked trip
curl -X GET http://localhost:8000/notifications \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected response (SC-028: <500ms):
{
  "notifications": [
    {
      "notification_id": "uuid",
      "type": "like",
      "actor": {
        "username": "testuser",
        "full_name": null
      },
      "trip": {
        "trip_id": "uuid",
        "title": "Ruta Bikepacking Pirineos"
      },
      "content": null,
      "is_read": false,
      "created_at": "2024-06-01T10:30:00Z"
    }
  ],
  "total_count": 1,
  "page": 1,
  "limit": 20,
  "has_more": false
}

# Save notification_id
export NOTIF_ID="<notification_id>"
```

### Scenario 5.2: Notification on Comment (FR-028)

```bash
# After testuser commented on trip
curl -X GET http://localhost:8000/notifications \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected: Notification with type="comment" and content excerpt
{
  "notifications": [
    {
      "notification_id": "uuid",
      "type": "comment",
      "actor": {
        "username": "testuser"
      },
      "trip": {...},
      "content": "¡Increíble ruta! Me encantaría hacerla algún día. ¿Cómo fue el camping salvaje?",
      "is_read": false,
      "created_at": "2024-06-01T11:00:00Z"
    }
  ]
}
```

### Scenario 5.3: Notification on Share (FR-028)

```bash
# After testuser shared trip
curl -X GET http://localhost:8000/notifications \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected: Notification with type="share"
{
  "notifications": [
    {
      "notification_id": "uuid",
      "type": "share",
      "actor": {
        "username": "testuser"
      },
      "trip": {...},
      "content": null,
      "is_read": false,
      "created_at": "2024-06-01T12:00:00Z"
    }
  ]
}
```

### Scenario 5.4: Unread Count Badge (FR-030)

```bash
# Get unread count
curl -X GET http://localhost:8000/notifications/unread-count \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected response (SC-030: <100ms):
{
  "unread_count": 3
}
```

### Scenario 5.5: Mark Notification as Read (FR-031)

```bash
# Mark single notification as read
curl -X POST http://localhost:8000/notifications/$NOTIF_ID/mark-read \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected response (SC-031: <200ms):
{
  "notification_id": "uuid",
  "is_read": true
}

# Verify unread count decreased
curl -X GET http://localhost:8000/notifications/unread-count \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected: unread_count = 2
```

### Scenario 5.6: Mark All as Read (FR-032)

```bash
# Mark all notifications as read
curl -X POST http://localhost:8000/notifications/mark-all-read \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected response (SC-032: <500ms):
{
  "success": true,
  "message": "Todas las notificaciones marcadas como leídas",
  "marked_count": 2
}

# Verify unread count is 0
curl -X GET http://localhost:8000/notifications/unread-count \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected: unread_count = 0
```

### Scenario 5.7: Filter Unread Notifications (FR-029)

```bash
# Get only unread notifications
curl -X GET "http://localhost:8000/notifications?is_read=false" \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected: Empty array (all marked as read)

# Get only read notifications
curl -X GET "http://localhost:8000/notifications?is_read=true" \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Expected: Array with all 3 notifications
```

---

## Frontend Integration Tests

### Optimistic UI Updates (from research.md)

**Like button with optimistic update**:

```typescript
// Frontend: useLike hook
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

// Usage in component
<button onClick={() => toggleLike()}>
  <HeartIcon className={isLiked ? 'text-red-500' : 'text-gray-400'} />
  <span>{likesCount}</span>
</button>
```

**Test scenario**:
1. Click like button → UI updates immediately (red heart, count +1)
2. Backend request succeeds → no change (already updated)
3. Click unlike button → UI updates immediately (gray heart, count -1)
4. Backend request fails → UI reverts (red heart, original count) + error toast

---

## Performance Benchmarks

**Target vs Actual** (after implementation):

| Endpoint | Target (SC) | Actual | Pass? |
|----------|-------------|--------|-------|
| GET /feed | <1s p95 (SC-001) | TBD | ⏳ |
| GET /feed (scroll) | <500ms p95 (SC-002) | TBD | ⏳ |
| POST /trips/{id}/like | <200ms p95 (SC-006) | TBD | ⏳ |
| GET /trips/{id}/likes | <500ms p95 (SC-010) | TBD | ⏳ |
| POST /trips/{id}/comments | <300ms p95 (SC-013) | TBD | ⏳ |
| GET /trips/{id}/comments | <500ms p95 (SC-015) | TBD | ⏳ |
| PUT /comments/{id} | <300ms p95 (SC-018) | TBD | ⏳ |
| DELETE /comments/{id} | <300ms p95 (SC-020) | TBD | ⏳ |
| POST /trips/{id}/share | <500ms p95 (SC-023) | TBD | ⏳ |
| GET /trips/{id}/shares | <500ms p95 (SC-025) | TBD | ⏳ |
| GET /notifications | <500ms p95 (SC-028) | TBD | ⏳ |
| GET /notifications/unread-count | <100ms p95 (SC-030) | TBD | ⏳ |
| POST /notifications/{id}/mark-read | <200ms p95 (SC-031) | TBD | ⏳ |
| POST /notifications/mark-all-read | <500ms p95 (SC-032) | TBD | ⏳ |

**Measurement command**:
```bash
# Use Apache Bench for load testing
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" http://localhost:8000/feed

# Check p95 latency in output
```

---

## Common Issues & Troubleshooting

### Issue 1: Feed is Empty

**Symptom**: GET /feed returns empty array

**Causes**:
1. User doesn't follow anyone → backfill with popular trips (FR-003)
2. No published trips exist in database
3. Authentication token expired

**Solution**:
```bash
# Verify user follows someone
curl -X GET http://localhost:8000/users/testuser/following \
  -H "Authorization: Bearer $TOKEN"

# Create published trip if none exist
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $MARIA_TOKEN" \
  -d '{"title": "...", "description": "...", ...}'
```

### Issue 2: Cannot Like Trip (400 Error)

**Symptom**: POST /trips/{id}/like returns 400

**Causes**:
1. User trying to like own trip (FR-011)
2. User already liked trip (unique constraint)
3. Trip status is DRAFT (not PUBLISHED)

**Solution**:
```bash
# Check trip owner
curl -X GET http://localhost:8000/trips/$TRIP_ID

# Unlike trip first if already liked
curl -X DELETE http://localhost:8000/trips/$TRIP_ID/like \
  -H "Authorization: Bearer $TOKEN"
```

### Issue 3: Rate Limit on Comments (429 Error)

**Symptom**: POST /comments returns 429

**Cause**: Exceeded 10 comments per hour limit (FR-018)

**Solution**: Wait 1 hour or use different test user

```bash
# Check remaining quota (future enhancement)
curl -X GET http://localhost:8000/users/me/rate-limits \
  -H "Authorization: Bearer $TOKEN"
```

### Issue 4: Notifications Not Appearing

**Symptom**: GET /notifications returns empty array

**Causes**:
1. No social interactions on user's trips
2. User triggered actions themselves (no self-notifications)
3. Notifications archived (>30 days old)

**Solution**:
```bash
# Verify trip ownership
curl -X GET http://localhost:8000/users/maria/trips

# Have another user interact
curl -X POST http://localhost:8000/trips/$TRIP_ID/like \
  -H "Authorization: Bearer $TESTUSER_TOKEN"

# Check maria's notifications
curl -X GET http://localhost:8000/notifications \
  -H "Authorization: Bearer $MARIA_TOKEN"
```

---

## Clean Up Test Data

```bash
# Delete all test trips
curl -X DELETE http://localhost:8000/trips/$TRIP_ID \
  -H "Authorization: Bearer $MARIA_TOKEN"

# Unfollow users
curl -X DELETE http://localhost:8000/users/maria/unfollow \
  -H "Authorization: Bearer $TOKEN"

# (Optional) Reset database
poetry run alembic downgrade base
poetry run alembic upgrade head
```

---

**Quick Start Status**: ✅ COMPLETED
**Date Completed**: 2026-01-16
**Ready for Implementation**: YES
