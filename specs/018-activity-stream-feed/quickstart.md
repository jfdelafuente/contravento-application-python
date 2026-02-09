# Quick Start: Activity Stream Feed

**Feature**: 018-activity-stream-feed
**Date**: 2026-02-09
**Estimated Setup Time**: 15 minutes

---

## Prerequisites

- ✅ ContraVento project cloned and dependencies installed
- ✅ PostgreSQL (production) or SQLite (development) configured
- ✅ Feature 004 (Social Network - Follow/Following) merged to develop
- ✅ Python 3.12+ with Poetry
- ✅ Node.js 18+ with npm (for frontend)

---

## Backend Setup

### 1. Install Dependencies

```bash
cd backend

# Install new dependencies for Feature 018
poetry add nh3  # HTML sanitizer (replacing bleach)
poetry add nh3 --dev  # For tests

# Verify installation
poetry show nh3
# Output: nh3 0.3.2 Python binding to Ammonia HTML sanitizer
```

### 2. Run Database Migration

```bash
# Apply migration to create activity_feed_items, likes, comments, comment_reports tables
poetry run alembic upgrade head

# Verify tables created
poetry run python -c "
from src.database import SessionLocal
from sqlalchemy import inspect

db = SessionLocal()
inspector = inspect(db.bind)
tables = inspector.get_table_names()
print('Activity Feed tables:', [t for t in tables if t in [
    'activity_feed_items', 'likes', 'comments', 'comment_reports'
]])
db.close()
"

# Expected output:
# Activity Feed tables: ['activity_feed_items', 'likes', 'comments', 'comment_reports']
```

### 3. Seed Test Data

Create seed script: `backend/scripts/seeding/seed_activity_feed.py`

```python
#!/usr/bin/env python3
"""
Seed script for Activity Stream Feed test data.

Creates:
- 3 test users (already exists from user seeding)
- 5 activities (trips, photos, achievements)
- 10 likes across activities
- 8 comments on activities

Usage:
    poetry run python scripts/seeding/seed_activity_feed.py
"""

import asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import select
from src.database import AsyncSessionLocal
from src.models.user import User
from src.models.activity_feed_item import ActivityFeedItem, ActivityType
from src.models.like import Like
from src.models.comment import Comment


async def seed_activities():
    """Seed activity feed test data."""
    async with AsyncSessionLocal() as db:
        # Get test users
        result = await db.execute(
            select(User).where(User.username.in_(['testuser', 'maria_garcia', 'admin']))
        )
        users = list(result.scalars().all())

        if len(users) < 2:
            print("⚠️  Need at least 2 users. Run create_verified_user.py first.")
            return

        testuser = next(u for u in users if u.username == 'testuser')
        maria = next(u for u in users if u.username == 'maria_garcia')

        print(f"✅ Found users: {[u.username for u in users]}")

        # Create activities
        activities = [
            ActivityFeedItem(
                activity_id=uuid4(),
                user_id=maria.user_id,
                activity_type=ActivityType.TRIP_PUBLISHED,
                related_id=uuid4(),  # Mock trip_id
                metadata={
                    "trip_title": "Ruta Bikepacking Pirineos",
                    "trip_distance_km": 320.5,
                    "trip_photo_url": "/storage/trips/2024/06/trip456/cover.jpg"
                },
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            ActivityFeedItem(
                activity_id=uuid4(),
                user_id=maria.user_id,
                activity_type=ActivityType.PHOTO_UPLOADED,
                related_id=uuid4(),  # Mock photo_id
                metadata={
                    "photo_url": "/storage/trips/2024/06/trip456/photo789.jpg",
                    "photo_caption": "Vista desde el Pico Aneto",
                    "trip_id": str(uuid4()),
                    "trip_title": "Ruta Bikepacking Pirineos"
                },
                created_at=datetime.utcnow() - timedelta(hours=1)
            ),
            ActivityFeedItem(
                activity_id=uuid4(),
                user_id=testuser.user_id,
                activity_type=ActivityType.ACHIEVEMENT_UNLOCKED,
                related_id=uuid4(),  # Mock user_achievement_id
                metadata={
                    "achievement_code": "first_100km",
                    "achievement_name": "Primera Ruta de 100km",
                    "achievement_badge_icon": "trophy-100km.svg"
                },
                created_at=datetime.utcnow() - timedelta(minutes=30)
            ),
        ]

        for activity in activities:
            db.add(activity)

        await db.commit()
        print(f"✅ Created {len(activities)} activities")

        # Create likes
        likes = [
            Like(
                like_id=uuid4(),
                user_id=testuser.user_id,
                activity_id=activities[0].activity_id,
                created_at=datetime.utcnow() - timedelta(minutes=90)
            ),
            Like(
                like_id=uuid4(),
                user_id=testuser.user_id,
                activity_id=activities[1].activity_id,
                created_at=datetime.utcnow() - timedelta(minutes=45)
            ),
            Like(
                like_id=uuid4(),
                user_id=maria.user_id,
                activity_id=activities[2].activity_id,
                created_at=datetime.utcnow() - timedelta(minutes=20)
            ),
        ]

        for like in likes:
            db.add(like)

        await db.commit()
        print(f"✅ Created {len(likes)} likes")

        # Create comments
        comments = [
            Comment(
                comment_id=uuid4(),
                user_id=testuser.user_id,
                activity_id=activities[0].activity_id,
                text="¡Increíble ruta! Me encantaría hacerla algún día.",
                created_at=datetime.utcnow() - timedelta(minutes=85)
            ),
            Comment(
                comment_id=uuid4(),
                user_id=maria.user_id,
                activity_id=activities[0].activity_id,
                text="Gracias! Es muy recomendable, especialmente en junio.",
                created_at=datetime.utcnow() - timedelta(minutes=80)
            ),
            Comment(
                comment_id=uuid4(),
                user_id=maria.user_id,
                activity_id=activities[2].activity_id,
                text="¡Felicidades por el logro! 🎉",
                created_at=datetime.utcnow() - timedelta(minutes=15)
            ),
        ]

        for comment in comments:
            db.add(comment)

        await db.commit()
        print(f"✅ Created {len(comments)} comments")

        print("\n📊 Seed Summary:")
        print(f"   - {len(activities)} activities")
        print(f"   - {len(likes)} likes")
        print(f"   - {len(comments)} comments")


if __name__ == "__main__":
    asyncio.run(seed_activities())
```

Run the seed script:

```bash
cd backend
poetry run python scripts/seeding/seed_activity_feed.py

# Expected output:
# ✅ Found users: ['testuser', 'maria_garcia', 'admin']
# ✅ Created 3 activities
# ✅ Created 3 likes
# ✅ Created 3 comments
# 📊 Seed Summary:
#    - 3 activities
#    - 3 likes
#    - 3 comments
```

### 4. Start Development Server

```bash
# Start backend server
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs at: http://localhost:8000/docs
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend

# Install React Query for state management
npm install @tanstack/react-query
npm install @tanstack/react-query-devtools --save-dev

# Verify installation
npm list @tanstack/react-query
# Output: @tanstack/react-query@5.x.x
```

### 2. Setup React Query Provider

Update `frontend/src/App.tsx`:

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60000, // 1 minute
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Existing routes */}
      <Routes>
        {/* Add feed route */}
        <Route path="/feed" element={<FeedPage />} />
      </Routes>

      {/* React Query DevTools (development only) */}
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}
```

### 3. Start Frontend Development Server

```bash
cd frontend
npm run dev

# Access at: http://localhost:5173
```

---

## API Testing

### Manual Testing with curl

**1. Get Activity Feed** (requires authentication):

```bash
# Login first to get JWT token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}' \
  | jq -r '.data.access_token')

# Get feed
curl -X GET http://localhost:8000/feed \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'

# Expected output:
# {
#   "activities": [
#     {
#       "activity_id": "...",
#       "user": {
#         "username": "maria_garcia",
#         "photo_url": null
#       },
#       "activity_type": "PHOTO_UPLOADED",
#       "metadata": {
#         "photo_url": "/storage/trips/2024/06/trip456/photo789.jpg",
#         "photo_caption": "Vista desde el Pico Aneto"
#       },
#       "created_at": "2024-06-16T14:20:00Z",
#       "likes_count": 1,
#       "comments_count": 0,
#       "is_liked": true
#     },
#     ...
#   ],
#   "next_cursor": "MTcwOTIxMTYwMC4wX2ExYjJjM2Q0...",
#   "has_next": false
# }
```

**2. Like an Activity**:

```bash
ACTIVITY_ID="<activity_id_from_feed>"

curl -X POST http://localhost:8000/activities/$ACTIVITY_ID/like \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'

# Expected output:
# {
#   "like_id": "...",
#   "activity_id": "...",
#   "user_id": "...",
#   "created_at": "2024-06-16T15:30:00Z"
# }
```

**3. Add a Comment**:

```bash
curl -X POST http://localhost:8000/activities/$ACTIVITY_ID/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "¡Qué ruta tan increíble! Me encantaría hacerla."}' \
  | jq '.'

# Expected output:
# {
#   "comment_id": "...",
#   "activity_id": "...",
#   "user": {
#     "username": "testuser",
#     "photo_url": null
#   },
#   "text": "¡Qué ruta tan increíble! Me encantaría hacerla.",
#   "created_at": "2024-06-16T15:35:00Z"
# }
```

**4. Report a Comment**:

```bash
COMMENT_ID="<comment_id_from_previous_response>"

curl -X POST http://localhost:8000/comments/$COMMENT_ID/report \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "spam", "notes": "Comentario repetitivo"}' \
  | jq '.'

# Expected output:
# {
#   "success": true,
#   "message": "Reporte enviado correctamente"
# }
```

### Postman Collection

Import the OpenAPI schema into Postman:

1. Open Postman
2. Click **Import** → **File** → Select `specs/018-activity-stream-feed/contracts/feed-api.yaml`
3. Postman generates collection with all endpoints
4. Set environment variable `{{baseUrl}}` = `http://localhost:8000`
5. Set environment variable `{{bearerToken}}` = JWT from login

---

## Testing

### Run Unit Tests

```bash
cd backend

# Run all feed-related tests
poetry run pytest tests/unit/test_feed_service.py -v
poetry run pytest tests/unit/test_like_service.py -v
poetry run pytest tests/unit/test_comment_service.py -v

# Run with coverage
poetry run pytest tests/unit/test_feed_service.py --cov=src.services.feed_service --cov-report=term
```

### Run Integration Tests

```bash
cd backend

# Test feed API endpoints
poetry run pytest tests/integration/test_feed_api.py -v
poetry run pytest tests/integration/test_likes_api.py -v
poetry run pytest tests/integration/test_comments_api.py -v
```

### Run Contract Tests

```bash
cd backend

# Validate OpenAPI schema compliance
poetry run pytest tests/contract/test_feed_contract.py -v
```

### Run Frontend E2E Tests

```bash
cd frontend

# Run E2E tests with Playwright
npm run test:e2e

# Run specific feed tests
npx playwright test tests/e2e/feed.spec.ts
```

---

## Admin Queries (Comment Moderation)

Since Option C (report button only, no UI) was chosen, admins query `comment_reports` table via SQL:

### PostgreSQL (Production)

```sql
-- Connect to database
psql -U contravento -d contravento_prod

-- Get most reported comments (3+ reports)
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
HAVING COUNT(r.report_id) >= 3
ORDER BY report_count DESC, c.created_at DESC;

-- Delete offensive comment
DELETE FROM comments WHERE comment_id = '<comment_id>';
-- (Cascades to comment_reports due to ON DELETE CASCADE)
```

### SQLite (Development)

```bash
# Connect to database
sqlite3 backend/contravento_dev.db

# Get most reported comments
SELECT
    c.comment_id,
    c.text,
    c.created_at,
    u.username AS comment_author,
    COUNT(r.report_id) AS report_count,
    GROUP_CONCAT(DISTINCT r.reason, ', ') AS report_reasons
FROM comments c
JOIN users u ON c.user_id = u.user_id
JOIN comment_reports r ON c.comment_id = r.comment_id
GROUP BY c.comment_id
HAVING COUNT(r.report_id) >= 3
ORDER BY report_count DESC, c.created_at DESC;

-- Delete offensive comment
DELETE FROM comments WHERE comment_id = '<comment_id>';
```

---

## Troubleshooting

### Issue: "Table 'activity_feed_items' doesn't exist"

**Cause**: Migration not applied

**Solution**:
```bash
cd backend
poetry run alembic upgrade head
```

### Issue: "Module 'nh3' not found"

**Cause**: Dependency not installed

**Solution**:
```bash
poetry add nh3
poetry install
```

### Issue: "Feed returns empty array"

**Cause**: No followed users or no activities

**Solution**:
```bash
# Check followed users
curl -X GET http://localhost:8000/users/testuser/following \
  -H "Authorization: Bearer $TOKEN"

# Follow a user
curl -X POST http://localhost:8000/users/maria_garcia/follow \
  -H "Authorization: Bearer $TOKEN"

# Re-run seed script
poetry run python scripts/seeding/seed_activity_feed.py
```

### Issue: "React Query DevTools not showing"

**Cause**: DevTools only work in development mode

**Solution**:
```typescript
// Ensure environment check:
{import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
```

---

## Performance Benchmarking

### Feed Load Time

```bash
# Benchmark feed endpoint (should be <2s for 20 activities - SC-001)
time curl -X GET http://localhost:8000/feed?limit=20 \
  -H "Authorization: Bearer $TOKEN" \
  > /dev/null

# Expected output:
# real    0m0.250s  (well under 2s requirement)
```

### Like/Unlike Latency

```bash
# Benchmark like operation (should be <200ms - SC-005)
time curl -X POST http://localhost:8000/activities/$ACTIVITY_ID/like \
  -H "Authorization: Bearer $TOKEN" \
  > /dev/null

# Expected output:
# real    0m0.150s  (under 200ms requirement)
```

---

## Next Steps

1. ✅ Backend setup complete → Proceed to `/speckit.tasks` to generate implementation tasks
2. ✅ Frontend setup complete → Begin implementing `FeedPage` component
3. ✅ Testing setup complete → Write TDD tests before implementation

---

**Quick Start Status**: ✅ READY
**Estimated Time to First API Call**: 15 minutes
**Last Updated**: 2026-02-09
