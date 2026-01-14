# Quickstart: Public Trips Feed

**Feature**: 013-public-trips-feed
**Date**: 2026-01-13
**For**: Developers implementing this feature

## Overview

This feature adds a public homepage displaying trips from users with public profiles. It consists of:

1. **Backend**: New GET /api/trips/public endpoint (FastAPI)
2. **Frontend**: PublicFeedPage (React) with auth-aware header
3. **Privacy**: Only PUBLISHED trips from public profiles

**Estimated Implementation Time**: 4-6 hours (1 backend session, 1 frontend session, 1 testing session)

---

## Prerequisites

✅ **Features 001, 002, 005, 008, 009 must be completed**:
- User model with `profile_visibility` field (Feature 001)
- Trip model with `status` and `published_at` (Feature 002)
- AuthContext for header authentication state (Feature 005)
- TripPhoto model for card images (Feature 008)
- TripLocation model for card locations (Feature 009)

✅ **Database indexes verified**:
```bash
# Check if indexes exist
cd backend
poetry run python scripts/check_indexes.py  # TODO: Create this script

# If missing, run migration
poetry run alembic upgrade head
```

✅ **Development environment running**:
```bash
# Backend (port 8000)
cd backend
poetry run uvicorn src.main:app --reload

# Frontend (port 5173)
cd frontend
npm run dev
```

---

## Implementation Steps

### Phase 1: Backend API (1-2 hours)

#### Step 1.1: Add Pydantic Schemas

**File**: `backend/src/schemas/trip.py`

```python
# Add these new schemas to existing file

class PublicUserSummary(BaseModel):
    """Minimal user info for public trip cards"""
    user_id: UUID
    username: str
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PublicLocationSummary(BaseModel):
    """First location for public trip cards"""
    location_id: UUID
    name: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)

class PublicPhotoSummary(BaseModel):
    """First photo for public trip cards"""
    photo_id: UUID
    photo_url: str
    caption: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PublicTripSummary(BaseModel):
    """Public trip card data"""
    trip_id: UUID
    title: str
    distance_km: float
    start_date: date
    published_at: datetime

    user: PublicUserSummary
    first_photo: Optional[PublicPhotoSummary] = None
    first_location: Optional[PublicLocationSummary] = None

    model_config = ConfigDict(from_attributes=True)

class PaginationInfo(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    total: int = Field(..., ge=0)
    pages: int = Field(..., ge=0)

class PublicTripListResponse(BaseModel):
    """Public feed API response"""
    success: bool = True
    data: list[PublicTripSummary]
    pagination: PaginationInfo
```

**Test**:
```bash
cd backend
poetry run pytest tests/unit/test_schemas.py -k PublicTrip -v
```

---

#### Step 1.2: Add Service Method

**File**: `backend/src/services/trip_service.py`

```python
# Add these methods to TripService class

async def get_public_trips(
    self,
    db: AsyncSession,
    page: int = 1,
    limit: int = 20
) -> list[Trip]:
    """
    Fetch published trips from users with public profiles.

    Performance: <20ms for 1000 trips (with indexes)
    """
    from sqlalchemy import select, func
    from sqlalchemy.orm import joinedload, selectinload
    from src.models.user import User
    from src.models.trip import Trip, TripStatus

    offset = (page - 1) * limit

    query = (
        select(Trip)
        .join(Trip.user)
        .where(Trip.status == TripStatus.PUBLISHED)
        .where(User.profile_visibility == 'public')
        .options(
            joinedload(Trip.user),
            selectinload(Trip.photos).options(limit=1),
            selectinload(Trip.locations).options(limit=1)
        )
        .order_by(Trip.published_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(query)
    trips = result.unique().scalars().all()
    return trips

async def count_public_trips(self, db: AsyncSession) -> int:
    """Count total public trips for pagination."""
    from sqlalchemy import select, func
    from src.models.user import User
    from src.models.trip import Trip, TripStatus

    query = (
        select(func.count(Trip.trip_id))
        .join(Trip.user)
        .where(Trip.status == TripStatus.PUBLISHED)
        .where(User.profile_visibility == 'public')
    )

    result = await db.execute(query)
    return result.scalar_one()
```

**Test**:
```bash
cd backend
poetry run pytest tests/unit/test_trip_service.py::test_get_public_trips -v
```

---

#### Step 1.3: Add API Endpoint

**File**: `backend/src/api/trips.py`

```python
# Add this new endpoint to existing router

@router.get("/public", response_model=PublicTripListResponse)
async def get_public_trips(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get public trips feed.

    Returns published trips from users with public profiles, ordered by
    publication date (most recent first).

    **No authentication required** - public endpoint.
    """
    try:
        # Fetch trips and count
        trips = await trip_service.get_public_trips(db, page=page, limit=limit)
        total = await trip_service.count_public_trips(db)

        # Calculate pagination metadata
        pages = (total + limit - 1) // limit

        # Transform to response schema
        trip_summaries = []
        for trip in trips:
            first_photo = trip.photos[0] if trip.photos else None
            first_location = trip.locations[0] if trip.locations else None

            trip_summaries.append(PublicTripSummary(
                trip_id=trip.trip_id,
                title=trip.title,
                distance_km=trip.distance_km,
                start_date=trip.start_date,
                published_at=trip.published_at,
                user=PublicUserSummary.model_validate(trip.user),
                first_photo=PublicPhotoSummary.model_validate(first_photo) if first_photo else None,
                first_location=PublicLocationSummary.model_validate(first_location) if first_location else None
            ))

        return PublicTripListResponse(
            success=True,
            data=trip_summaries,
            pagination=PaginationInfo(
                page=page,
                limit=limit,
                total=total,
                pages=pages
            )
        )

    except Exception as e:
        logger.error(f"Error fetching public trips: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "Error al obtener viajes públicos. Inténtalo de nuevo más tarde."
            }
        )
```

**Test**:
```bash
cd backend
poetry run pytest tests/integration/test_public_feed_api.py -v
```

**Manual Test** (with cURL):
```bash
curl http://localhost:8000/api/trips/public?page=1&limit=20 | jq
```

---

### Phase 2: Frontend UI (2-3 hours)

#### Step 2.1: Add TypeScript Types

**File**: `frontend/src/types/trip.ts`

```typescript
// Add these to existing types

export interface PublicUserSummary {
  user_id: string;
  username: string;
  photo_url: string | null;
}

export interface PublicLocationSummary {
  location_id: string;
  name: string;
  latitude: number;
  longitude: number;
}

export interface PublicPhotoSummary {
  photo_id: string;
  photo_url: string;
  caption: string | null;
}

export interface PublicTripSummary {
  trip_id: string;
  title: string;
  distance_km: number;
  start_date: string; // YYYY-MM-DD
  published_at: string; // ISO 8601

  user: PublicUserSummary;
  first_photo: PublicPhotoSummary | null;
  first_location: PublicLocationSummary | null;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface PublicTripListResponse {
  success: boolean;
  data: PublicTripSummary[];
  pagination: PaginationInfo;
}
```

---

#### Step 2.2: Add API Service Method

**File**: `frontend/src/services/tripService.ts`

```typescript
// Add this method to existing tripService

export const getPublicTrips = async (
  page: number = 1,
  limit: number = 20
): Promise<PublicTripListResponse> => {
  const response = await axios.get<PublicTripListResponse>(
    `${API_URL}/trips/public`,
    {
      params: { page, limit },
    }
  );
  return response.data;
};
```

---

#### Step 2.3: Create Custom Hook

**File**: `frontend/src/hooks/usePublicTrips.ts` (NEW FILE)

```typescript
import { useState, useEffect } from 'react';
import { getPublicTrips } from '../services/tripService';
import type { PublicTripSummary, PaginationInfo } from '../types/trip';

export const usePublicTrips = (page: number = 1) => {
  const [trips, setTrips] = useState<PublicTripSummary[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrips = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await getPublicTrips(page);
        setTrips(response.data);
        setPagination(response.pagination);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Error al cargar viajes públicos');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrips();
  }, [page]);

  return { trips, pagination, isLoading, error };
};
```

---

#### Step 2.4: Create PublicHeader Component

**File**: `frontend/src/components/layout/PublicHeader.tsx` (NEW FILE)

```typescript
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './PublicHeader.css';

export const PublicHeader: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="public-header">
      <div className="public-header__container">
        <Link to="/" className="public-header__logo">
          ContraVento
        </Link>

        {isAuthenticated && user ? (
          <div className="public-header__user-menu">
            <Link
              to={`/profile/${user.username}`}
              className="public-header__profile-link"
            >
              {user.photo_url ? (
                <img
                  src={user.photo_url}
                  alt={user.username}
                  className="public-header__avatar"
                />
              ) : (
                <div className="public-header__avatar-placeholder">
                  {user.username[0].toUpperCase()}
                </div>
              )}
              <span className="public-header__username">{user.username}</span>
            </Link>
            <button
              onClick={logout}
              className="public-header__logout-button"
            >
              Cerrar sesión
            </button>
          </div>
        ) : (
          <Link to="/login" className="public-header__login-button">
            Iniciar sesión
          </Link>
        )}
      </div>
    </header>
  );
};
```

---

#### Step 2.5: Create PublicTripCard Component

**File**: `frontend/src/components/trips/PublicTripCard.tsx` (NEW FILE)

```typescript
import React from 'react';
import { Link } from 'react-router-dom';
import type { PublicTripSummary } from '../../types/trip';
import { formatDistance, formatDate } from '../../utils/tripHelpers';
import { getPhotoUrl } from '../../utils/tripHelpers';
import './PublicTripCard.css';

export interface PublicTripCardProps {
  trip: PublicTripSummary;
}

export const PublicTripCard: React.FC<PublicTripCardProps> = ({ trip }) => {
  return (
    <article className="public-trip-card">
      <Link to={`/trips/${trip.trip_id}`} className="public-trip-card__link">
        {/* Photo */}
        <div className="public-trip-card__photo">
          {trip.first_photo ? (
            <img
              src={getPhotoUrl(trip.first_photo.photo_url)}
              alt={trip.title}
              className="public-trip-card__image"
              loading="lazy"
            />
          ) : (
            <div className="public-trip-card__photo-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <span>Sin foto</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="public-trip-card__content">
          <h3 className="public-trip-card__title">{trip.title}</h3>

          {/* Location (if exists) */}
          {trip.first_location && (
            <p className="public-trip-card__location">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              {trip.first_location.name}
            </p>
          )}

          {/* Meta (distance + date) */}
          <div className="public-trip-card__meta">
            <span className="public-trip-card__distance">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              {formatDistance(trip.distance_km)}
            </span>

            <span className="public-trip-card__date">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
              {formatDate(trip.start_date)}
            </span>
          </div>

          {/* Author */}
          <div className="public-trip-card__author">
            {trip.user.photo_url ? (
              <img
                src={trip.user.photo_url}
                alt={trip.user.username}
                className="public-trip-card__author-avatar"
              />
            ) : (
              <div className="public-trip-card__author-avatar-placeholder">
                {trip.user.username[0].toUpperCase()}
              </div>
            )}
            <span className="public-trip-card__author-name">{trip.user.username}</span>
          </div>
        </div>
      </Link>
    </article>
  );
};
```

---

#### Step 2.6: Create PublicFeedPage

**File**: `frontend/src/pages/PublicFeedPage.tsx` (NEW FILE)

```typescript
import React, { useState } from 'react';
import { PublicHeader } from '../components/layout/PublicHeader';
import { PublicTripCard } from '../components/trips/PublicTripCard';
import { usePublicTrips } from '../hooks/usePublicTrips';
import './PublicFeedPage.css';

export const PublicFeedPage: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const { trips, pagination, isLoading, error } = usePublicTrips(currentPage);

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="public-feed-page">
      <PublicHeader />

      <main className="public-feed-page__main">
        <div className="public-feed-page__container">
          <h1 className="public-feed-page__title">Viajes de la comunidad</h1>

          {/* Loading State */}
          {isLoading && (
            <div className="public-feed-page__loading">
              <div className="spinner" />
              <p>Cargando viajes...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="public-feed-page__error">
              <p>{error}</p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && trips.length === 0 && (
            <div className="public-feed-page__empty">
              <p>Aún no hay viajes públicos disponibles.</p>
            </div>
          )}

          {/* Trip Grid */}
          {!isLoading && !error && trips.length > 0 && (
            <>
              <div className="public-feed-page__grid">
                {trips.map((trip) => (
                  <PublicTripCard key={trip.trip_id} trip={trip} />
                ))}
              </div>

              {/* Pagination */}
              {pagination && pagination.pages > 1 && (
                <div className="public-feed-page__pagination">
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="public-feed-page__pagination-button"
                  >
                    Anterior
                  </button>

                  <span className="public-feed-page__pagination-info">
                    Página {pagination.page} de {pagination.pages}
                  </span>

                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === pagination.pages}
                    className="public-feed-page__pagination-button"
                  >
                    Siguiente
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
};
```

---

#### Step 2.7: Add Route

**File**: `frontend/src/App.tsx`

```typescript
// Add this route to existing router configuration

import { PublicFeedPage } from './pages/PublicFeedPage';

// Inside <Routes>
<Route path="/" element={<PublicFeedPage />} />  // NEW: Public feed as homepage
```

---

### Phase 3: Testing (1-2 hours)

#### Backend Tests

**File**: `backend/tests/unit/test_trip_service_public.py` (NEW FILE)

```python
import pytest
from src.services.trip_service import TripService
from src.models.user import User
from src.models.trip import Trip, TripStatus

@pytest.mark.asyncio
async def test_get_public_trips_filters_draft_trips(db_session):
    """Test that DRAFT trips are excluded from public feed"""
    # Setup: Create user with public profile + DRAFT trip
    # Assert: get_public_trips() returns empty list

@pytest.mark.asyncio
async def test_get_public_trips_filters_private_profiles(db_session):
    """Test that trips from private profiles are excluded"""
    # Setup: Create user with private profile + PUBLISHED trip
    # Assert: get_public_trips() returns empty list

@pytest.mark.asyncio
async def test_get_public_trips_includes_public_published(db_session):
    """Test that PUBLISHED trips from public profiles are included"""
    # Setup: Create user with public profile + PUBLISHED trip
    # Assert: get_public_trips() returns 1 trip

@pytest.mark.asyncio
async def test_get_public_trips_pagination(db_session):
    """Test pagination works correctly"""
    # Setup: Create 25 public trips
    # Assert: page 1 returns 20, page 2 returns 5

@pytest.mark.asyncio
async def test_get_public_trips_ordering(db_session):
    """Test trips ordered by published_at DESC"""
    # Setup: Create 3 trips with different published_at
    # Assert: Most recent first
```

**Run**:
```bash
cd backend
poetry run pytest tests/unit/test_trip_service_public.py -v
```

---

#### Frontend Tests

**File**: `frontend/tests/unit/PublicTripCard.test.tsx` (NEW FILE)

```typescript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { PublicTripCard } from '../../src/components/trips/PublicTripCard';

describe('PublicTripCard', () => {
  it('renders trip with all fields', () => {
    const trip = {
      trip_id: '123',
      title: 'Test Trip',
      distance_km: 100.5,
      start_date: '2024-01-15',
      published_at: '2024-01-20T10:00:00Z',
      user: {
        user_id: '456',
        username: 'testuser',
        photo_url: 'https://example.com/photo.jpg',
      },
      first_photo: {
        photo_id: '789',
        photo_url: 'https://example.com/trip-photo.jpg',
        caption: 'Test caption',
      },
      first_location: {
        location_id: '101',
        name: 'Parque Nacional',
        latitude: 42.5,
        longitude: 1.5,
      },
    };

    render(
      <BrowserRouter>
        <PublicTripCard trip={trip} />
      </BrowserRouter>
    );

    expect(screen.getByText('Test Trip')).toBeInTheDocument();
    expect(screen.getByText('Parque Nacional')).toBeInTheDocument();
    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('handles missing photo gracefully', () => {
    // Test with first_photo: null
  });

  it('handles missing location gracefully', () => {
    // Test with first_location: null
  });
});
```

**Run**:
```bash
cd frontend
npm run test
```

---

## Verification Checklist

✅ **Backend**:
- [ ] GET /api/trips/public returns 200 with valid response
- [ ] Privacy filters work (only public profiles + PUBLISHED trips)
- [ ] Pagination works (page, limit, total, pages)
- [ ] Unit tests pass (≥90% coverage)
- [ ] Integration tests pass (API contract validation)

✅ **Frontend**:
- [ ] Public feed page renders at `/`
- [ ] Header shows "Iniciar sesión" when not authenticated
- [ ] Header shows username + logout when authenticated
- [ ] Trip cards display all fields (title, photo, location, distance, date, author)
- [ ] Pagination buttons work correctly
- [ ] Loading/error/empty states display correctly
- [ ] Component tests pass

✅ **End-to-End**:
- [ ] Anonymous user can view public trips without login
- [ ] Authenticated user sees their username in header
- [ ] Clicking trip card navigates to trip detail page
- [ ] Private user trips do NOT appear in feed
- [ ] DRAFT trips do NOT appear in feed

---

## Common Issues & Solutions

### Issue: Query is slow (>500ms)

**Solution**: Check indexes exist
```sql
-- Run in PostgreSQL
EXPLAIN ANALYZE
SELECT trips.*, users.username
FROM trips
INNER JOIN users ON trips.user_id = users.user_id
WHERE trips.status = 'PUBLISHED' AND users.profile_visibility = 'public'
ORDER BY trips.published_at DESC
LIMIT 20;

-- Should show "Index Scan" not "Seq Scan"
```

If Seq Scan appears, create indexes:
```bash
cd backend
poetry run alembic upgrade head
```

---

### Issue: Frontend shows "Error al cargar viajes públicos"

**Solution**: Check CORS configuration
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ← Ensure frontend origin allowed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue: Photos/locations not loading

**Solution**: Verify eager loading in service
```python
# Should use selectinload, not lazy loading
.options(
    selectinload(Trip.photos).options(limit=1),
    selectinload(Trip.locations).options(limit=1)
)
```

---

## Next Steps

After completing this quickstart:

1. **Run `/speckit.tasks`** to generate granular task breakdown
2. **Implement tests first** (TDD workflow)
3. **Commit frequently** with descriptive messages
4. **Create PR** when all tests pass and coverage ≥90%

---

## Resources

- [spec.md](spec.md) - Full feature specification
- [data-model.md](data-model.md) - Database schema and query patterns
- [contracts/public-feed-api.yaml](contracts/public-feed-api.yaml) - OpenAPI contract
- [research.md](research.md) - Technical decisions and rationale
- [CLAUDE.md](../../../CLAUDE.md) - Project guidelines and patterns

**Questions?** Review research.md for design decisions or check existing Feature 008 implementation for similar patterns.
