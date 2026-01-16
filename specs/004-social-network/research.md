# Research: Red Social y Feed de Ciclistas

**Feature**: 004-social-network
**Date**: 2026-01-16
**Status**: ✅ Completed

## Research Questions & Decisions

### 1. Feed Algorithm Approach

**Question**: ¿Qué algoritmo usar para el feed personalizado: cronológico simple o ranking inteligente?

**Options Evaluated**:

| Approach | Pros | Cons | Complexity |
|----------|------|------|------------|
| **Chronological (reverse)** | Simple, predecible, fácil debugging | Puede esconder contenido relevante | ✅ Baja |
| **Intelligent ranking** | Mejor relevancia, más engagement | Complejo, requiere ML/scoring | ❌ Alta |
| **Hybrid (chronological + popular)** | Balance entre simplicidad y relevancia | Dos queries, más complejo | ⚠️ Media |

**Decision**: ✅ **Hybrid approach (chronological + popular backfill)**

**Rationale**:
- Start simple with reverse chronological for followed users (FR-002)
- Backfill with popular/recent community content when user follows few people (FR-003)
- No machine learning required in v1
- Performance: Single query with UNION, sorted by timestamp
- Measurable: Easy to A/B test engagement vs pure chronological

**Implementation Pattern**:
```python
async def get_personalized_feed(
    db: AsyncSession,
    user_id: UUID,
    page: int = 1,
    limit: int = 10
) -> List[FeedItem]:
    """
    Get personalized feed for user.

    Algorithm:
    1. Get trips from followed users (ordered by created_at DESC)
    2. If < limit trips, backfill with popular community trips (order by likes_count DESC, created_at DESC)
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
            .where(Trip.user_id != user_id)  # Exclude own trips
            .order_by(Trip.likes_count.desc(), Trip.created_at.desc())
            .limit(remaining)
        )
        result = await db.execute(community_trips)
        trips.extend(result.scalars().all())

    return trips
```

**Alternatives Considered & Rejected**:
- **Pure chronological**: Rejected - Poor UX for users with few follows
- **Pure intelligent ranking**: Rejected - Over-engineering for v1, requires ML infrastructure
- **Activity-based scoring**: Rejected - Too complex, requires engagement tracking

---

### 2. Real-time Updates Strategy

**Question**: ¿Cómo actualizar el feed y notificaciones en tiempo real: WebSockets, polling, o manual refresh?

**Options Evaluated**:

| Strategy | Pros | Cons | Infrastructure |
|----------|------|------|----------------|
| **WebSockets** | Instant updates, bi-directional | Complex server, scaling issues | ❌ Requiere Redis/PubSub |
| **Server-Sent Events (SSE)** | Simple push, uni-directional | Not bidirectional, browser limits | ⚠️ Requiere nginx config |
| **Polling (short interval)** | Simple, stateless | Network overhead, battery drain | ✅ No extra infra |
| **Manual refresh** | Simplest, no overhead | Users must refresh manually | ✅ No extra infra |

**Decision**: ✅ **Manual refresh (v1) + Polling (v2 future)**

**Rationale**:
- **v1 (MVP)**: Manual refresh only
  - Simplest implementation, no new infrastructure
  - Users click "refresh" button or reload page
  - Meets all functional requirements (FR-001 to FR-045)
  - Social networks (Twitter, Facebook) work fine with manual refresh
- **v2 (Future)**: Short-interval polling (30-60 seconds)
  - Easy upgrade path from v1
  - No WebSocket complexity
  - Good enough for notifications badge
  - Can be feature-flagged for gradual rollout

**Implementation Pattern (v1)**:
```typescript
// Frontend: Manual refresh button
export const FeedPage: React.FC = () => {
  const { trips, isLoading, refetch } = useFeed();

  return (
    <div>
      <button onClick={() => refetch()}>Actualizar</button>
      {trips.map(trip => <FeedItem key={trip.id} trip={trip} />)}
    </div>
  );
};

// Backend: Stateless API (no real-time logic)
@router.get("/feed")
async def get_feed(
    page: int = 1,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    trips = await FeedService.get_personalized_feed(db, current_user.id, page)
    return {"trips": trips}
```

**Implementation Pattern (v2 - Future)**:
```typescript
// Frontend: Polling every 60s for new content
useEffect(() => {
  const interval = setInterval(() => {
    refetch({ silent: true }); // Fetch without spinner
  }, 60000); // 60 seconds

  return () => clearInterval(interval);
}, [refetch]);
```

**Alternatives Considered & Rejected**:
- **WebSockets**: Rejected - Over-engineering, requires Redis PubSub, scaling complexity
- **SSE**: Rejected - Nginx configuration complexity, browser connection limits
- **Aggressive polling (<10s)**: Rejected - Battery drain, server load

---

### 3. Notification Storage and Archiving Pattern

**Question**: ¿Cómo almacenar y archivar notificaciones: tabla única, particionado, o soft delete con archiving?

**Options Evaluated**:

| Pattern | Pros | Cons | Query Performance |
|---------|------|------|-------------------|
| **Single table, no archiving** | Simple | Table grows unbounded | ❌ Degraded over time |
| **Soft delete (is_archived flag)** | Simple queries | Still grows unbounded | ⚠️ Needs index on flag |
| **Partitioning (by month)** | Automatic archiving | PostgreSQL only, complex | ✅ Fast queries |
| **Separate archive table** | Clean separation | Requires migration script | ✅ Fast queries |

**Decision**: ✅ **Soft delete with scheduled cleanup (separate archive table)**

**Rationale**:
- Notifications table with `is_archived` boolean (default False)
- Background job (cron/celery) runs daily: archive notifications >30 days old
- Archived notifications moved to `notifications_archive` table
- Active queries only scan `notifications` table (fast)
- Archive queries (rare) scan `notifications_archive` table
- No PostgreSQL-specific features (works on SQLite for dev)

**Implementation Pattern**:
```python
# Models
class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20))  # "like", "comment", "share"
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))  # User who performed action
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"))
    content: Mapped[str] = mapped_column(Text, nullable=True)  # Comment excerpt
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
        Index("ix_notifications_created_at", "created_at"),
    )

class NotificationArchive(Base):
    __tablename__ = "notifications_archive"
    # Same structure as Notification

# Archiving service
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

**Alternatives Considered & Rejected**:
- **No archiving**: Rejected - Table grows to millions of rows, query performance degrades
- **PostgreSQL partitioning**: Rejected - Not SQLite-compatible, over-engineering
- **TTL/expiration**: Rejected - Requires background worker, doesn't preserve history

---

### 4. Frontend State Management for Social Interactions

**Question**: ¿Qué patrón usar para state management: Redux, Context API, React Query, o custom hooks?

**Options Evaluated**:

| Pattern | Pros | Cons | Learning Curve |
|---------|------|------|----------------|
| **Redux Toolkit** | Global state, DevTools, middleware | Boilerplate, over-engineering | ⚠️ High |
| **Context API + useReducer** | Native React, no dependencies | Re-renders, performance issues | ✅ Low |
| **React Query** | Cache, invalidation, optimistic updates | New paradigm, requires learning | ⚠️ Medium |
| **Custom hooks + useState** | Simple, local state | Manual cache management | ✅ Low |

**Decision**: ✅ **Custom hooks + Axios (established pattern in ContraVento)**

**Rationale**:
- ContraVento already uses custom hooks pattern (useTripForm, useTripList, useAuth)
- No new dependencies or learning curve
- Optimistic updates via local state + refetch on error
- Cache invalidation via manual refetch (simple, predictable)
- Consistency with existing codebase (Features 005, 007, 008)

**Implementation Pattern**:
```typescript
// Custom hook for likes with optimistic updates
export const useLike = (tripId: string) => {
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Fetch initial like status
    const fetchLikeStatus = async () => {
      const { data } = await likeService.getLikeStatus(tripId);
      setIsLiked(data.is_liked);
      setLikesCount(data.likes_count);
    };
    fetchLikeStatus();
  }, [tripId]);

  const toggleLike = async () => {
    // Optimistic update
    const previousIsLiked = isLiked;
    const previousCount = likesCount;
    setIsLiked(!isLiked);
    setLikesCount(isLiked ? likesCount - 1 : likesCount + 1);
    setIsLoading(true);

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
    } finally {
      setIsLoading(false);
    }
  };

  return { isLiked, likesCount, toggleLike, isLoading };
};

// Usage in component
export const LikeButton: React.FC<{ tripId: string }> = ({ tripId }) => {
  const { isLiked, likesCount, toggleLike, isLoading } = useLike(tripId);

  return (
    <button onClick={toggleLike} disabled={isLoading}>
      <HeartIcon className={isLiked ? 'text-red-500' : 'text-gray-400'} />
      <span>{likesCount}</span>
    </button>
  );
};
```

**Alternatives Considered & Rejected**:
- **Redux Toolkit**: Rejected - Overkill for feature scope, breaks codebase consistency
- **React Query**: Rejected - New dependency, learning curve, not established in project
- **Context API**: Rejected - Performance issues with frequent updates (likes, comments)

---

## Implementation Decisions Summary

| Component | Technology/Pattern | Rationale |
|-----------|--------------------|-----------|
| **Feed Algorithm** | Hybrid (chronological + popular backfill) | Simple, performant, meets FR-001 to FR-008 |
| **Real-time Updates** | Manual refresh (v1), Polling (v2 future) | No infrastructure overhead, easy upgrade path |
| **Notification Storage** | Soft delete + 30-day archiving | Fast queries, preserves history, SQLite-compatible |
| **Frontend State** | Custom hooks + Axios (established pattern) | Consistency with codebase, optimistic updates |

## Backend Enhancements Required

### Add `check_mutual_follow()` to SocialService

**Purpose**: Required for Feature 015 US3 (Social Links with MUTUAL_FOLLOWERS privacy level)

**Implementation**:
```python
# backend/src/services/social_service.py

async def check_mutual_follow(
    self,
    user_a_id: str,
    user_b_id: str
) -> bool:
    """
    Check if two users follow each other (mutual follow).

    Args:
        user_a_id: First user ID
        user_b_id: Second user ID

    Returns:
        True if both users follow each other, False otherwise
    """
    # Check if both follow relationships exist
    result = await self.db.execute(
        select(func.count())
        .select_from(Follow)
        .where(
            or_(
                and_(
                    Follow.follower_id == user_a_id,
                    Follow.following_id == user_b_id
                ),
                and_(
                    Follow.follower_id == user_b_id,
                    Follow.following_id == user_a_id
                )
            )
        )
    )
    count = result.scalar()
    return count == 2  # Both follow relationships exist
```

**Test**:
```python
# backend/tests/unit/test_social_service.py

async def test_check_mutual_follow_both_follow(db_session):
    """Test mutual follow detection when both users follow each other."""
    user_a = await create_test_user(db_session, username="user_a")
    user_b = await create_test_user(db_session, username="user_b")

    # Create both follow relationships
    await SocialService(db_session).follow_user("user_a", "user_b")
    await SocialService(db_session).follow_user("user_b", "user_a")

    # Check mutual follow
    is_mutual = await SocialService(db_session).check_mutual_follow(user_a.id, user_b.id)

    assert is_mutual is True

async def test_check_mutual_follow_one_way(db_session):
    """Test mutual follow detection when only one user follows."""
    user_a = await create_test_user(db_session, username="user_a")
    user_b = await create_test_user(db_session, username="user_b")

    # Create one-way follow
    await SocialService(db_session).follow_user("user_a", "user_b")

    # Check mutual follow
    is_mutual = await SocialService(db_session).check_mutual_follow(user_a.id, user_b.id)

    assert is_mutual is False
```

---

## Performance Benchmarks (Expected)

Based on research and similar implementations:

- **Feed Query**: ~150-300ms for 10 items with eager loading (SC-001: <1s ✅)
- **Like Toggle**: ~50-100ms (SC-006: <200ms ✅)
- **Comment Post**: ~100-200ms with sanitization (SC-013: <300ms ✅)
- **Notification Generation**: ~50-100ms (SC-020: <1s ✅)
- **Infinite Scroll (next page)**: ~100-200ms (SC-002: <500ms ✅)

## Dependencies Added

### Backend
- No new dependencies (uses existing FastAPI, SQLAlchemy, Pydantic stack)

### Frontend
- No new dependencies (uses existing React 18, Axios, react-hot-toast)

## Next Steps

✅ Research complete - Ready for Phase 1 (Design Artifacts)

1. Generate `data-model.md` with Like, Comment, Share, Notification schemas
2. Generate `contracts/social-api.yaml` with OpenAPI specs for all endpoints
3. Generate `quickstart.md` with testing scenarios
4. Update CLAUDE.md with new patterns (optimistic updates, infinite scroll)

---

**Research Status**: ✅ COMPLETED
**Date Completed**: 2026-01-16
**Ready for Phase 1**: YES
