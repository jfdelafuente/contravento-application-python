# Architecture Documentation - ContraVento

Technical architecture, design decisions, and system patterns for ContraVento cycling social platform.

**Audience**: Developers, architects, technical leads

---

## Quick Navigation

| I need to understand... | Go to |
|------------------------|-------|
| 🏗️ Backend architecture | [Backend Overview](backend/overview.md) |
| 🔒 Security patterns | [Backend Security](backend/security.md) |
| 📊 Database design | [Data Model](data-model/schemas.md) |
| ⚛️ Frontend architecture | [Frontend Overview](frontend/overview.md) |
| 🎨 Component patterns | [Frontend Patterns](frontend/patterns.md) |
| 🔌 External integrations | [Integrations](integrations/) |

---

## Architecture Overview

ContraVento is built with a **Clean Architecture** approach, separating concerns into distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│              React 18 + TypeScript + Vite                │
│          (Container/Presentational Pattern)              │
└─────────────────────────────────────────────────────────┘
                           ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                      API Layer                           │
│                 FastAPI Routers                          │
│           (Request validation, Response formatting)       │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                         │
│                  Business Logic                          │
│         (AuthService, TripService, UserService)          │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                     Model Layer                          │
│              SQLAlchemy ORM Models                       │
│           (User, Trip, Photo, Achievement)               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   Database Layer                         │
│           SQLite (dev) / PostgreSQL (prod)               │
└─────────────────────────────────────────────────────────┘
```

**Key Principle**: Layers can only call downward. APIs call Services, Services use Models. Never skip layers.

---

## Backend Architecture

### Core Documentation

- 📘 **[Backend Overview](backend/overview.md)** - Clean architecture, layered design, async patterns
- 📘 **[Service Layer](backend/services.md)** - Business logic patterns, dependency injection
- 📘 **[Database Strategy](backend/database.md)** - Dual DB (SQLite/PostgreSQL), migrations, async queries
- 📘 **[Security Architecture](backend/security.md)** - Authentication, authorization, data protection

### Key Patterns

**Dependency Injection**:
```python
@router.get("/trips/{trip_id}")
async def get_trip(
    trip_id: UUID,
    current_user: User = Depends(get_current_user),  # Injected
    db: AsyncSession = Depends(get_db)               # Injected
):
    trip = await TripService.get_trip(db, trip_id, current_user)
    return {"success": True, "data": trip}
```

**Service Layer Pattern**:
```python
class TripService:
    @staticmethod
    async def create_trip(
        db: AsyncSession,
        trip_data: TripCreate,
        user: User
    ) -> Trip:
        # Business logic here
        # Validation, stats updates, notifications
        pass
```

**Documentation Status**:

| Document | Status | Source | Last Updated |
|----------|--------|--------|--------------|
| [backend/overview.md](backend/overview.md) | ⏳ Planned | backend/docs/ARCHITECTURE.md | - |
| [backend/services.md](backend/services.md) | ⏳ Planned | Extract from ARCHITECTURE.md | - |
| [backend/database.md](backend/database.md) | ⏳ Planned | Extract from ARCHITECTURE.md | - |
| [backend/security.md](backend/security.md) | ⏳ Planned | backend/docs/SECURITY.md | - |

---

## Frontend Architecture

### Core Documentation

- 📘 **[Frontend Overview](frontend/overview.md)** - Component architecture, routing, state management
- 📘 **[Component Patterns](frontend/patterns.md)** - Container/Presentational, custom hooks, forms
- 📘 **[State Management](frontend/state-management.md)** - Context API, React Hook Form, local state
- 📘 **[Routing Patterns](frontend/routing.md)** - React Router, protected routes, navigation

### Key Patterns

**Container/Presentational**:
```typescript
// Smart Container (Page)
export const TripsListPage: React.FC = () => {
  const { trips, isLoading } = useTripList(username);
  return <TripCard trips={trips} />;
};

// Presentational Component
export const TripCard: React.FC<TripCardProps> = ({ trip }) => {
  return <div>{trip.title}</div>;
};
```

**Custom Hooks**:
```typescript
export const useTripList = (username: string) => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTrips(username).then(setTrips);
  }, [username]);

  return { trips, isLoading };
};
```

**Documentation Status**:

| Document | Status | Source | Last Updated |
|----------|--------|--------|--------------|
| [frontend/overview.md](frontend/overview.md) | ⏳ Planned | frontend/README.md | - |
| [frontend/patterns.md](frontend/patterns.md) | ⏳ Planned | frontend/docs/DESIGN_SYSTEM.md | - |
| [frontend/state-management.md](frontend/state-management.md) | ⏳ Planned | CLAUDE.md + frontend/README.md | - |
| [frontend/routing.md](frontend/routing.md) | ⏳ Planned | Extract from specs/005 | - |

---

## Data Model

### Core Documentation

- 📘 **[Database Schemas](data-model/schemas.md)** - Complete DDL (SQLite + PostgreSQL), entity relationships
- 📘 **[Migration Strategy](data-model/migrations.md)** - Alembic workflow, versioning, rollback procedures

### Entity Relationship Diagram

```
┌─────────┐       ┌─────────┐       ┌──────────┐
│  User   │──────<│  Trip   │>──────│ TripPhoto│
└─────────┘       └─────────┘       └──────────┘
     │                 │
     │                 │
     ▼                 ▼
┌───────────┐     ┌──────────┐
│UserProfile│     │   Tag    │
└───────────┘     └──────────┘
     │                 │
     ▼                 ▼
┌───────────┐     ┌────────────┐
│ UserStats │     │TripLocation│
└───────────┘     └────────────┘
```

**Key Entities**:
- User, UserProfile, UserStats
- Trip, TripPhoto, TripLocation, Tag
- Achievement, CyclingType
- GPXFile, POI (Points of Interest)
- Follow, Comment, Like (social features)

**Documentation Status**:

| Document | Status | Source | Last Updated |
|----------|--------|--------|--------------|
| [data-model/schemas.md](data-model/schemas.md) | ⏳ Planned | Consolidate from specs/*/data-model.md | - |
| [data-model/migrations.md](data-model/migrations.md) | ⏳ Planned | Extract from CLAUDE.md | - |

---

## Integrations

External services and third-party integrations:

- 📘 **[GPX Processing](integrations/gpx-processing.md)** - GPX parsing, track simplification, elevation extraction
- 📘 **[Reverse Geocoding](integrations/reverse-geocoding.md)** - Nominatim API, caching strategy, rate limiting
- 📘 **[Photo Storage](integrations/photo-storage.md)** - File upload, image resizing, storage strategy

### Integration Patterns

**GPX Simplification** (Douglas-Peucker):
```python
# Reduce 5000 trackpoints → ~200-500 points
simplified_track = simplify_track(
    trackpoints=gpx.tracks[0].segments[0].points,
    epsilon=0.0001  # Tolerance for simplification
)
```

**Reverse Geocoding Cache**:
```typescript
// LRU cache (100 entries, ~111m precision)
const cached = geocodingCache.get(lat, lng);
if (cached) return cached;  // Cache hit (~70-80% hit rate)

const result = await nominatimAPI.reverseGeocode(lat, lng);
geocodingCache.set(lat, lng, result);
```

**Documentation Status**:

| Document | Status | Source | Last Updated |
|----------|--------|--------|--------------|
| [integrations/gpx-processing.md](integrations/gpx-processing.md) | ⏳ Planned | specs/003/GPX_WIZARD_INTEGRATION_ANALYSIS.md | - |
| [integrations/reverse-geocoding.md](integrations/reverse-geocoding.md) | ⏳ Planned | CLAUDE.md (Reverse Geocoding section) | - |
| [integrations/photo-storage.md](integrations/photo-storage.md) | ⏳ Planned | Extract from CLAUDE.md | - |

---

## Design Decisions

Key architectural decisions and their rationale:

### Dual Database Strategy

**Decision**: Support both SQLite (dev) and PostgreSQL (prod) from same codebase

**Rationale**:
- ✅ **Fast Development**: SQLite = instant startup, no Docker
- ✅ **Production Parity**: PostgreSQL = production-grade features
- ✅ **Test Isolation**: In-memory SQLite for fast tests
- ⚠️ **Tradeoff**: Alembic migrations must handle both dialects

**Implementation**: See [Database Strategy](backend/database.md)

---

### Clean Architecture Layers

**Decision**: Strict layer separation (API → Service → Model → Database)

**Rationale**:
- ✅ **Testability**: Each layer can be tested in isolation
- ✅ **Maintainability**: Business logic separated from HTTP concerns
- ✅ **Scalability**: Easy to swap implementations (e.g., different DB)
- ⚠️ **Tradeoff**: More boilerplate for simple CRUD operations

**Implementation**: See [Backend Overview](backend/overview.md)

---

### Service Layer Pattern

**Decision**: All business logic in service classes, not in API routes

**Rationale**:
- ✅ **Reusability**: Services can be called from APIs, background tasks, CLI
- ✅ **Testing**: Unit test services without HTTP layer
- ✅ **Single Responsibility**: Routes handle HTTP, services handle logic
- ⚠️ **Tradeoff**: Extra layer adds complexity

**Implementation**: See [Service Layer](backend/services.md)

---

## Migration from Old Documentation

This consolidated architecture documentation replaces:

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `backend/docs/ARCHITECTURE.md` | `docs/architecture/backend/` | ⏳ Phase 5 migration |
| `backend/docs/SECURITY.md` | `docs/architecture/backend/security.md` | ⏳ Phase 5 migration |
| `frontend/README.md` (architecture) | `docs/architecture/frontend/` | ⏳ Phase 5 migration |
| `frontend/docs/DESIGN_SYSTEM.md` | `docs/architecture/frontend/patterns.md` | ⏳ Phase 5 migration |
| `specs/*/data-model.md` | `docs/architecture/data-model/schemas.md` | ⏳ Phase 5 migration |

Migration will occur in **Phase 5** (Week 5) of the documentation consolidation plan.

---

## Related Documentation

- **[API Reference](../api/README.md)** - API endpoints and contracts
- **[Testing](../testing/README.md)** - Testing strategies
- **[Features](../features/README.md)** - Feature specifications
- **[Development](../development/README.md)** - Developer workflows

---

**Last Updated**: 2026-02-06
**Consolidation Plan**: Phase 1 (Foundation) - Directory structure
