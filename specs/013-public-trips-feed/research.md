# Research: Public Trips Feed

**Feature**: Public Trips Feed (013)
**Date**: 2026-01-13
**Phase**: 0 - Design Research

## Overview

This document consolidates research findings for implementing a public homepage that displays trips from users with public profiles. The feature builds on existing Trip (Feature 002) and User (Feature 001) models while introducing new privacy-aware querying patterns.

## Research Areas

### 1. Privacy-Aware Querying Patterns

**Decision**: Use SQLAlchemy joins with WHERE clause filtering on `profile_visibility='public'` and `status='PUBLISHED'`

**Rationale**:
- **Performance**: Single query with joins is more efficient than separate queries or subqueries
- **Data integrity**: Ensures privacy filter is applied at database level, not application level
- **Maintainability**: Clear, declarative query that's easy to understand and modify
- **Consistency**: Aligns with existing ContraVento patterns (Feature 008 uses similar filtering)

**Alternatives Considered**:
1. **Subquery approach**: `WHERE trip.user_id IN (SELECT id FROM users WHERE profile_visibility='public')`
   - Rejected: Less efficient, PostgreSQL may not optimize as well as JOIN
2. **Application-level filtering**: Fetch all trips, filter in Python
   - Rejected: Violates performance requirements (would load unnecessary data)
3. **Materialized view**: Pre-computed public trips table
   - Rejected: Adds complexity, stale data issues, overkill for current scale

**Implementation Pattern**:
```python
# Pseudo-code example
query = (
    select(Trip)
    .join(Trip.user)
    .where(Trip.status == TripStatus.PUBLISHED)
    .where(User.profile_visibility == 'public')
    .order_by(Trip.published_at.desc())
    .limit(20)
    .offset(page * 20)
    .options(joinedload(Trip.user), joinedload(Trip.photos).limit(1), joinedload(Trip.locations).limit(1))
)
```

**Sources**:
- SQLAlchemy 2.0 ORM Querying Guide: https://docs.sqlalchemy.org/en/20/orm/queryguide/
- PostgreSQL JOIN Performance: https://www.postgresql.org/docs/current/using-explain.html

---

### 2. Pagination Strategy

**Decision**: Offset-based pagination with page number and limit parameters

**Rationale**:
- **Simplicity**: Easy to implement and understand (`?page=1&limit=20`)
- **User expectation**: Standard pagination UI (page 1, 2, 3...) familiar to users
- **Current scale**: 1000+ trips is manageable with offset pagination
- **Backend support**: FastAPI + SQLAlchemy make offset/limit trivial
- **Frontend compatibility**: React state management with page number is straightforward

**Alternatives Considered**:
1. **Cursor-based pagination** (keyset pagination using `published_at` timestamp):
   - Pros: Better performance at scale (no offset scan), consistent results during concurrent inserts
   - Cons: Cannot jump to arbitrary pages (no "go to page 5"), harder to implement page numbers UI
   - Rejected: Overkill for current scale, worse UX for discovery use case
2. **Infinite scroll** (load more on scroll):
   - Pros: Mobile-friendly, no page navigation needed
   - Cons: Harder to share specific "pages", accessibility concerns, harder to reach footer
   - Rejected: Spec explicitly mentions "paginación" (paginated navigation)
3. **Hybrid approach** (offset pagination + cursor fallback):
   - Rejected: Added complexity, YAGNI (premature optimization)

**Performance Considerations**:
- **Index**: Ensure composite index on `(status, profile_visibility, published_at DESC)` exists
- **Limit offset scan**: At page 50 (offset 1000), PostgreSQL still performs well (<50ms)
- **Future migration path**: If scale exceeds 10k trips, cursor pagination can be added without breaking API (new query param `cursor=XYZ`)

**Implementation Pattern**:
```python
# Endpoint signature
@router.get("/trips/public")
async def get_public_trips(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * limit
    trips = await trip_service.get_public_trips(db, limit=limit, offset=offset)
    total = await trip_service.count_public_trips(db)
    return {
        "data": trips,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }
```

**Sources**:
- Use The Index, Luke (SQL indexing): https://use-the-index-luke.com/sql/partial-results/fetch-next-page
- Offset vs Cursor Pagination: https://www.citusdata.com/blog/2016/03/30/five-ways-to-paginate/

---

### 3. Frontend State Management for Public Feed

**Decision**: React hooks (useState, useEffect) with custom `usePublicTrips` hook, no global state

**Rationale**:
- **Simplicity**: Public feed is a standalone page, doesn't share state with other pages
- **No authentication dependency**: Anonymous users don't have auth context
- **Component isolation**: TripCard components are presentational, don't need global state
- **Performance**: Avoids re-renders from global state changes
- **Consistency**: Matches existing ContraVento patterns (Feature 008 uses custom hooks like `useTripList`)

**Alternatives Considered**:
1. **React Context API** for feed state:
   - Rejected: Overkill for single-page state, adds boilerplate
2. **Redux/Zustand** global store:
   - Rejected: No shared state between pages, unnecessary complexity
3. **React Query** (TanStack Query):
   - Pros: Caching, automatic refetching, built-in pagination support
   - Cons: New dependency, learning curve, may be overkill for simple fetch
   - Rejected: Current scale doesn't justify dependency, can add later if caching needs arise

**Implementation Pattern**:
```typescript
// Custom hook
export const usePublicTrips = (page: number = 1) => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrips = async () => {
      setIsLoading(true);
      try {
        const response = await tripService.getPublicTrips(page);
        setTrips(response.data);
        setPagination(response.pagination);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTrips();
  }, [page]);

  return { trips, pagination, isLoading, error };
};
```

**Sources**:
- React Hooks Best Practices: https://react.dev/learn/reusing-logic-with-custom-hooks
- Feature 008 implementation: `frontend/src/hooks/useTripList.ts`

---

### 4. Auth-Aware Header Component Pattern

**Decision**: Single `PublicHeader` component with conditional rendering based on `useAuth()` context

**Rationale**:
- **Reusability**: Same header works for authenticated and anonymous users
- **Single source of truth**: Auth state from existing AuthContext (Feature 005)
- **Performance**: No duplicate code, single component renders efficiently
- **Maintainability**: One component to update for header changes

**Alternatives Considered**:
1. **Separate components**: `AnonymousHeader` + `AuthenticatedHeader`
   - Rejected: Code duplication, harder to maintain consistent styling
2. **Layout component with slot pattern**:
   - Rejected: Over-engineering for a simple conditional render
3. **Header variants with prop-based configuration**:
   - Rejected: Props would just mimic auth state, redundant

**Implementation Pattern**:
```typescript
export const PublicHeader: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="public-header">
      <Link to="/" className="logo">ContraVento</Link>

      {isAuthenticated && user ? (
        <div className="user-menu">
          <Link to={`/profile/${user.username}`}>
            <img src={user.photo_url || '/default-avatar.png'} alt={user.username} />
            <span>{user.username}</span>
          </Link>
          <button onClick={logout}>Cerrar sesión</button>
        </div>
      ) : (
        <Link to="/login" className="login-button">Iniciar sesión</Link>
      )}
    </header>
  );
};
```

**Sources**:
- React Conditional Rendering: https://react.dev/learn/conditional-rendering
- Feature 005 AuthContext: `frontend/src/contexts/AuthContext.tsx`

---

### 5. Trip Card Design Pattern

**Decision**: Extend existing `RecentTripCard` component or create new `PublicTripCard` with location field

**Rationale**:
- **Consistency**: Reuse existing card design from Feature 008 (dashboard recent trips)
- **Location field**: Add first location display (new requirement for public feed)
- **Flexibility**: Separate component allows public-specific styling/behavior without affecting dashboard

**Comparison**:
| Aspect | Reuse RecentTripCard | New PublicTripCard |
|--------|---------------------|-------------------|
| Code reuse | ✅ High | ❌ Duplicate code |
| Location display | ❌ Requires modification | ✅ Built-in |
| Dashboard impact | ⚠️ May affect existing UI | ✅ No impact |
| Maintainability | ⚠️ Shared component complexity | ✅ Independent |

**Decision**: Create new `PublicTripCard` component to avoid modifying dashboard behavior

**Implementation Pattern**:
```typescript
// frontend/src/components/trips/PublicTripCard.tsx
export interface PublicTripCardProps {
  trip: PublicTripSummary; // Extends TripListItem with location
}

export const PublicTripCard: React.FC<PublicTripCardProps> = ({ trip }) => {
  const firstLocation = trip.locations?.[0];

  return (
    <article className="public-trip-card">
      <Link to={`/trips/${trip.trip_id}`}>
        <img src={getPhotoUrl(trip.photos?.[0]?.photo_url)} alt={trip.title} />
        <div className="content">
          <h3>{trip.title}</h3>
          {firstLocation && (
            <p className="location">
              <LocationIcon /> {firstLocation.name}
            </p>
          )}
          <div className="meta">
            <span>{formatDistance(trip.distance_km)}</span>
            <span>{formatDate(trip.start_date)}</span>
          </div>
          <div className="author">
            <img src={trip.user.photo_url} alt={trip.user.username} />
            <span>{trip.user.username}</span>
          </div>
        </div>
      </Link>
    </article>
  );
};
```

**Sources**:
- Feature 008 RecentTripCard: `frontend/src/components/dashboard/RecentTripCard.tsx`
- Component composition patterns: https://react.dev/learn/passing-props-to-a-component

---

### 6. Database Indexing Strategy

**Decision**: Add composite index on `(status, profile_visibility, published_at DESC)` to trips table and `(profile_visibility)` to users table

**Rationale**:
- **Query optimization**: WHERE clause filters on status + profile_visibility + ORDER BY published_at
- **Covering index potential**: Index can satisfy WHERE + ORDER BY without table scan
- **PostgreSQL optimizer**: Composite indexes are more efficient than separate single-column indexes for multi-condition queries
- **Existing schema**: Check if indexes exist from Features 001/002, add if missing

**Index Analysis**:
```sql
-- Primary query pattern
SELECT trips.*, users.username, users.photo_url
FROM trips
INNER JOIN users ON trips.user_id = users.user_id
WHERE trips.status = 'PUBLISHED'
  AND users.profile_visibility = 'public'
ORDER BY trips.published_at DESC
LIMIT 20 OFFSET 0;

-- Recommended indexes
CREATE INDEX IF NOT EXISTS idx_trips_public_feed
ON trips (status, published_at DESC)
WHERE status = 'PUBLISHED';

CREATE INDEX IF NOT EXISTS idx_users_profile_visibility
ON users (profile_visibility);
```

**Performance Impact** (estimated based on 1000 trips, 500 public users):
- Without index: ~150ms (full table scan)
- With index: <20ms (index scan + limit 20)
- At 10k trips: <50ms (index scales logarithmically)

**Alternatives Considered**:
1. **Partial index** on `status='PUBLISHED'`:
   - Pros: Smaller index size, faster writes
   - Cons: Can't use profile_visibility in index
   - Decision: Use WHERE clause in index creation for published trips only
2. **Separate indexes** on each column:
   - Rejected: PostgreSQL won't combine them efficiently for this query

**Sources**:
- PostgreSQL Index Types: https://www.postgresql.org/docs/current/indexes-types.html
- Partial Indexes: https://www.postgresql.org/docs/current/indexes-partial.html

---

### 7. Eager Loading Strategy for N+1 Prevention

**Decision**: Use SQLAlchemy `joinedload()` for `trip.user`, `selectinload()` for `trip.photos` and `trip.locations` with LIMIT 1

**Rationale**:
- **N+1 prevention**: Single query loads trip + related data
- **joinedload for user**: 1:1 relationship, always need username and photo
- **selectinload for photos/locations**: 1:N relationships, only need first item
- **Performance**: Avoid 20 separate queries for photos and 20 for locations

**Implementation**:
```python
from sqlalchemy.orm import joinedload, selectinload

query = (
    select(Trip)
    .join(Trip.user)
    .where(Trip.status == TripStatus.PUBLISHED)
    .where(User.profile_visibility == 'public')
    .options(
        joinedload(Trip.user),  # Always load user data
        selectinload(Trip.photos).limit(1),  # Load first photo only
        selectinload(Trip.locations).limit(1)  # Load first location only
    )
    .order_by(Trip.published_at.desc())
    .limit(20)
)
```

**Query Count**:
- Without eager loading: 1 (trips) + 20 (users) + 20 (photos) + 20 (locations) = **61 queries**
- With eager loading: 1 (trips + users joined) + 1 (photos batch) + 1 (locations batch) = **3 queries**

**Alternatives Considered**:
1. **All joinedload**: Join photos and locations
   - Rejected: Cartesian product issue (trip with 10 photos + 5 locations = 50 rows)
2. **Lazy loading**: Load on access
   - Rejected: Causes N+1 queries, violates performance requirements
3. **Subqueryload**: Use subquery instead of SELECT IN
   - Rejected: Less efficient than selectinload in SQLAlchemy 2.0

**Sources**:
- SQLAlchemy Relationship Loading: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html
- Feature 008 implementation: `backend/src/services/trip_service.py` (existing eager loading patterns)

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Privacy Querying | JOIN with WHERE filters | Single efficient query |
| Pagination | Offset-based (page + limit) | Simple, familiar UX |
| Frontend State | Custom React hooks | No global state needed |
| Header Component | Conditional render in one component | Code reuse, maintainability |
| Trip Card | New PublicTripCard component | Independent from dashboard |
| Database Indexes | Composite index (status, published_at) | <20ms query performance |
| Eager Loading | joinedload + selectinload | 3 queries instead of 61 |

**All decisions align with Constitution requirements and ContraVento existing patterns.**

---

## Open Questions

None - all technical decisions resolved through research.

---

## Next Phase

**Phase 1: Design** - Create data-model.md and OpenAPI contracts based on these research findings.
