# Architecture Documentation - ContraVento

Comprehensive technical design documentation for ContraVento's backend, frontend, and integrations.

**Audience**: Developers, technical architects, senior engineers

---

## Table of Contents

- [Overview](#overview)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Data Model](#data-model)
- [Integrations](#integrations)
- [Design Decisions](#design-decisions)
- [Related Documentation](#related-documentation)

---

## Overview

ContraVento is a full-stack cycling social platform built with modern technologies and architectural patterns.

### Technology Stack

**Backend**:
- **Framework**: FastAPI (Python 3.12)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: SQLite (dev/test), PostgreSQL 16 (production)
- **Authentication**: JWT tokens (access + refresh)
- **File Storage**: Local filesystem (future: S3)
- **Email**: MailHog (dev), SMTP (prod)

**Frontend**:
- **Framework**: React 18 + TypeScript 5
- **Build Tool**: Vite 5
- **Routing**: React Router 6
- **Forms**: React Hook Form + Zod
- **Maps**: Leaflet.js + react-leaflet
- **HTTP Client**: Axios
- **State**: React Context + local state

**Infrastructure**:
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx (staging/prod)
- **Monitoring**: Prometheus + Grafana (future)

---

### Architectural Principles

**1. Clean Architecture (Backend)**:
```
API Layer (FastAPI Routers)
    ↓ calls
Service Layer (Business Logic)
    ↓ uses
Model Layer (SQLAlchemy ORM)
    ↓ persists to
Database (SQLite/PostgreSQL)
```

**Key Rule**: Layers can only call downward. APIs call Services, Services use Models.

---

**2. Component-Based Architecture (Frontend)**:
```
Pages (Smart Containers)
    ↓ compose
Components (Presentational)
    ↓ use
Hooks (Business Logic)
    ↓ call
Services (API Client)
```

**Key Rule**: Separation of concerns. Pages manage state, components display UI, hooks encapsulate logic.

---

**3. Dependency Injection**:
- Database sessions injected via `Depends(get_db)`
- Current user injected via `Depends(get_current_user)`
- No global state or singletons

**4. Schema Separation**:
- **Pydantic Schemas** (`schemas/`): Request/response validation
- **SQLAlchemy Models** (`models/`): Database persistence
- Never mix the two

**5. Test-Driven Development (TDD)**:
- Write tests FIRST before implementation
- Coverage requirement: ≥90% (backend), ≥80% (frontend)
- Test behavior, not implementation

---

## Backend Architecture

Comprehensive backend design documentation.

📘 **Coming Soon** - Backend architecture documentation will be migrated from `backend/docs/ARCHITECTURE.md`

### Topics Covered

**Core Architecture**:
- Clean Architecture layers (API → Service → Model → Database)
- Service Layer pattern for business logic
- Async SQLAlchemy with asyncio
- Dual database support (SQLite dev, PostgreSQL prod)

**Security**:
- JWT authentication flow (access + refresh tokens)
- Password hashing with bcrypt (12 rounds)
- CORS configuration and security headers
- Error handling and validation

**Example - Dependency Injection**:
```python
from src.api.deps import get_current_user, get_db

@router.get("/trips")
async def get_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    trips = await TripService.get_user_trips(db, current_user)
    return {"success": True, "data": trips}
```

**Example - Service Layer**:
```python
class TripService:
    @staticmethod
    async def create_trip(
        db: AsyncSession,
        user: User,
        trip_data: TripCreateInput
    ) -> Trip:
        trip = Trip(**trip_data.dict(), user_id=user.user_id)
        db.add(trip)
        await db.commit()
        await db.refresh(trip)
        return trip
```

---

## Frontend Architecture

React + TypeScript architecture and patterns.

📘 **Coming Soon** - Frontend architecture documentation will be created from existing patterns

### Topics Covered

**Component Patterns**:
- Container/Presentational component pattern
- Custom hooks for business logic
- React Hook Form + Zod validation
- Wizard pattern for multi-step forms

**State Management**:
- Context API for shared state
- React Router protected routes
- Error handling and loading states

**Example - Custom Hook**:
```typescript
export const useTripList = (username: string, filters?: TripFilters) => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTrips = async () => {
      const response = await getUserTrips(username, filters);
      setTrips(response.data);
      setIsLoading(false);
    };
    fetchTrips();
  }, [username, filters]);

  return { trips, isLoading };
};
```

**Example - Container/Presentational**:
```typescript
// Container (Smart)
export const TripsListPage: React.FC = () => {
  const { trips, isLoading } = useTripList(username);
  return <TripGrid trips={trips} isLoading={isLoading} />;
};

// Presentational (Dumb)
export const TripGrid: React.FC<Props> = ({ trips }) => {
  return (
    <div className="grid">
      {trips.map(trip => <TripCard key={trip.trip_id} trip={trip} />)}
    </div>
  );
};
```

---

## Data Model

Database schemas, relationships, and migrations.

📘 **Coming Soon** - Data model documentation will consolidate `specs/*/data-model.md` files

### Entity Overview

```
User ──────┬───── UserProfile (1:1)
           ├───── UserStats (1:1)
           ├───── Trip (1:N)
           ├───── Comment (1:N)
           ├───── Follow (1:N as follower)
           └───── Follow (1:N as followed)

Trip ──────┬───── TripPhoto (1:N, max 20)
           ├───── TripLocation (1:N)
           ├───── Tag (N:N via trip_tags)
           ├───── GPXFile (1:1, optional)
           ├───── Comment (1:N)
           └───── Like (1:N)

GPXFile ───┴───── GPXTrack (1:N)
GPXTrack ──┴───── TrackPoint (1:N, simplified ~200-500 points)
```

**Key Entities**:
- **User**: Authentication, profile, stats
- **Trip**: Title, description, dates, distance, difficulty, status (draft/published)
- **TripPhoto**: Photos with order, captions (max 20 per trip)
- **GPXFile**: Original GPX with metadata
- **GPXTrack**: Simplified track with ~200-500 points
- **TrackPoint**: Lat/lng/elevation/gradient

**Database Strategy**:
- **SQLite**: Development, testing (file-based, in-memory)
- **PostgreSQL**: Staging, production (native UUID, arrays, concurrency)
- **Migrations**: Alembic auto-generates dialect-specific DDL

---

## Integrations

External services and third-party integrations.

📘 **Coming Soon** - Integration documentation for GPX, geocoding, and photo storage

### GPX Processing

```
1. Upload GPX file (max 10MB)
2. Parse with gpxpy library
3. Extract metadata (distance, elevation, trackpoints)
4. Simplify route (Douglas-Peucker: 5000 → 500 points)
5. Calculate gradients between points
6. Store simplified track in database
7. Return statistics to user
```

### Reverse Geocoding

```
1. User clicks on map → (lat, lng)
2. Check LRU cache (100 entries, 3-decimal precision)
3. Cache miss → Call Nominatim API
4. Debounce (1000ms) to prevent rate limits
5. Extract Spanish place name from response
6. Store in cache for future requests
7. Display location confirmation modal
```

### Photo Storage

```
1. Validate file (MIME type, size max 10MB)
2. Store original temporarily
3. Background task: Resize to 1200px width with Pillow
4. Save to: storage/trip_photos/{year}/{month}/{trip_id}/
5. Update database with photo_url
6. Delete original
```

---

## Design Decisions

### Why Clean Architecture?

**Benefits**:
- Clear separation of concerns
- Testable business logic (services)
- Easy to swap database or framework
- Prevents coupling between layers

**Trade-offs**:
- More boilerplate (schemas + models)
- Steeper learning curve
- Overhead for simple CRUD operations

**Verdict**: Worth it for maintainability and testability.

---

### Why Dual Database Strategy?

**Benefits**:
- Fast development (SQLite, no setup)
- Fast tests (in-memory SQLite)
- Production-ready (PostgreSQL)
- Same codebase, different dialects

**Trade-offs**:
- Must test on both databases
- Some PostgreSQL features unavailable (native UUID, arrays)
- Alembic migrations must support both

**Verdict**: Excellent developer experience, production-ready.

---

### Why React Hook Form + Zod?

**Benefits**:
- Type-safe validation
- Great DX (less boilerplate)
- Performance (uncontrolled inputs)
- Schema reuse (frontend + backend)

**Trade-offs**:
- Learning curve (Zod schema syntax)
- Less mature than Formik

**Verdict**: Modern, type-safe, worth the learning curve.

---

## Related Documentation

- **[API Reference](../api/README.md)** - API endpoints and contracts
- **[Testing](../testing/README.md)** - Test strategies and guides
- **[Deployment](../deployment/README.md)** - Deployment modes and configurations
- **[User Guides](../user-guides/README.md)** - End-user documentation
- **[Development](../development/README.md)** - Developer workflows

---

## Migration Status

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `backend/docs/ARCHITECTURE.md` (740 lines) | `docs/architecture/backend/overview.md` | ⏳ Planned |
| `backend/docs/SECURITY.md` (298 lines) | `docs/architecture/backend/security.md` | ⏳ Planned |
| `frontend/README.md` (architecture section) | `docs/architecture/frontend/overview.md` | ⏳ Planned |
| `frontend/docs/DESIGN_SYSTEM.md` | `docs/architecture/frontend/patterns.md` | ⏳ Planned |
| `specs/003-gps-routes/GPX_WIZARD_INTEGRATION_ANALYSIS.md` | `docs/architecture/integrations/gpx-processing.md` | ⏳ Planned |
| `specs/*/data-model.md` (multiple files) | `docs/architecture/data-model/schemas.md` | ⏳ Planned |

**Consolidation Strategy**: Migrate core architecture docs, consolidate scattered data models, create integration guides from specs.

---

**Last Updated**: 2026-02-07
**Consolidation Plan**: ⏳ Phase 5 (Architecture) - In progress
**Status**: Foundation created, migrations pending
