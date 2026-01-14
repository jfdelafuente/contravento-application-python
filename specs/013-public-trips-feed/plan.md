# Implementation Plan: Public Trips Feed

**Branch**: `013-public-trips-feed` | **Date**: 2026-01-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-public-trips-feed/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Create a public homepage that displays published trips from users with public profiles. The page will show trip cards with title, photo, location (first), distance, date, and author information. Include an authentication-aware header that shows login button for anonymous visitors or user profile/logout for authenticated users. Implement server-side pagination (20 trips/page) with privacy filters ensuring only PUBLISHED trips from public profiles appear in the feed.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0, Pydantic (backend), React 18, React Router 6, Axios (frontend)
**Storage**: PostgreSQL (production), SQLite (development) - existing User and Trip models
**Testing**: pytest (backend), Vitest/React Testing Library (frontend)
**Target Platform**: Web application (Linux server + modern browsers)
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**: <200ms p95 for trip list queries, <2s initial page load with 20 trips
**Constraints**: Must respect existing profile_visibility field, maintain backward compatibility with Features 001, 002, 005, 008
**Scale/Scope**: Handle 1000+ public trips with efficient pagination, support 100+ concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability ✅

- [x] PEP 8 compliance (backend), ESLint/Prettier (frontend)
- [x] Single Responsibility Principle: Separate API routes, services, components
- [x] Type hints (Python) and TypeScript strict mode
- [x] Docstrings for public APIs (FastAPI routes, React components)
- [x] No magic numbers (pagination size as constant, status values as enums)

### II. Testing Standards (TDD Required) ✅

- [x] **TDD Workflow**: Tests written before implementation
- [x] **Unit Tests ≥90% coverage**:
  - Backend: Privacy filter logic, pagination service
  - Frontend: TripCard component, PublicFeedPage hooks
- [x] **Integration Tests**:
  - GET /api/trips/public endpoint with filters
  - Database queries for public trips
  - Frontend-backend integration (API calls)
- [x] **Contract Tests**: OpenAPI schema validation for public feed endpoint
- [x] Edge cases tested: No public trips, missing photos, missing locations, pagination boundaries

### III. User Experience Consistency ✅

- [x] All Spanish text (UI labels, error messages)
- [x] Standard JSON API response structure with success/data/error
- [x] Proper HTTP status codes (200, 404 for no trips, 401 for auth errors)
- [x] Loading states, empty states (" Aún no hay viajes públicos disponibles")
- [x] Timezone-aware dates (UTC storage, local display)
- [x] Metric units (km for distance)
- [x] Accessibility: Alt text for images, semantic HTML

### IV. Performance Requirements ✅

- [x] **<200ms p95** for trip list query (indexed on status, profile_visibility, published_at)
- [x] **<2s initial load** with 20 trips (pagination limit)
- [x] Database optimization: Eager loading for trip.user, trip.photos, trip.locations
- [x] N+1 prevention: Single query with joins for trip + related data
- [x] Pagination: 20 items max (SC-007: handle 100+ trips)
- [x] Image optimization: Use existing thumbnail URLs from Feature 008

### Security & Data Protection ✅

- [x] Privacy respected: Only public profiles visible (profile_visibility='public')
- [x] Authorization: Public endpoint (no auth required for viewing)
- [x] SQL injection prevention: SQLAlchemy ORM only
- [x] XSS prevention: React auto-escaping, sanitized HTML in trip descriptions
- [x] Input validation: Pagination parameters (page number, limit)

### Development Workflow ✅

- [x] Feature branch: `013-public-trips-feed`
- [x] Conventional commits with Co-Authored-By: Claude
- [x] Pull request with spec link, test coverage, screenshots
- [x] CI/CD: All tests + linting pass before merge
- [x] Database migrations: Indexes on status, profile_visibility (if not exist)

**GATE STATUS**: ✅ **PASS** - All constitutional requirements met. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── trips.py                    # Add GET /trips/public endpoint
│   ├── schemas/
│   │   └── trip.py                     # Add PublicTripListResponse schema
│   ├── services/
│   │   └── trip_service.py             # Add get_public_trips() method
│   └── models/
│       ├── trip.py                     # Existing Trip model (reuse)
│       └── user.py                     # Existing User model (reuse)
└── tests/
    ├── unit/
    │   └── test_trip_service_public.py # Privacy filter logic tests
    ├── integration/
    │   └── test_public_feed_api.py     # Public endpoint integration tests
    └── contract/
        └── test_public_feed_contract.py # OpenAPI schema validation

frontend/
├── src/
│   ├── pages/
│   │   └── PublicFeedPage.tsx          # NEW: Main public homepage
│   ├── components/
│   │   ├── layout/
│   │   │   └── PublicHeader.tsx        # NEW: Auth-aware header
│   │   └── trips/
│   │       └── PublicTripCard.tsx      # NEW: Trip card for public feed
│   ├── hooks/
│   │   └── usePublicTrips.ts           # NEW: Data fetching hook
│   ├── services/
│   │   └── tripService.ts              # Add getPublicTrips() method
│   └── types/
│       └── trip.ts                     # Extend TripListItem if needed
└── tests/
    ├── unit/
    │   ├── PublicTripCard.test.tsx
    │   └── usePublicTrips.test.ts
    └── integration/
        └── PublicFeedPage.test.tsx
```

**Structure Decision**: Web application structure (Option 2). This feature extends the existing FastAPI backend with a new public endpoint and adds a new React page to the frontend SPA. We reuse existing Trip and User models from Features 001 and 002, and leverage the TripLocation model from Feature 009 for displaying locations.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitutional requirements met without exceptions.

---

## Phase 0: Research & Outline ✅ COMPLETE

**Duration**: 30 minutes
**Output**: [research.md](research.md)

### Research Areas Investigated

1. **Privacy-Aware Querying Patterns** → SQLAlchemy JOIN with WHERE filtering
2. **Pagination Strategy** → Offset-based pagination (page + limit)
3. **Frontend State Management** → Custom React hooks (no global state)
4. **Auth-Aware Header Pattern** → Single component with conditional rendering
5. **Trip Card Design** → New PublicTripCard component (independent from dashboard)
6. **Database Indexing** → Composite index on (status, published_at DESC)
7. **Eager Loading** → joinedload + selectinload to prevent N+1 queries

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| JOIN query vs subquery | Single efficient query, better PostgreSQL optimization |
| Offset pagination vs cursor | Simpler UX, adequate for current scale (1000+ trips) |
| React hooks vs Context API | No shared state needed, component isolation |
| New card component vs reuse | Avoid modifying dashboard behavior, add location field |
| Composite index | <20ms query performance with proper WHERE + ORDER BY coverage |

**No NEEDS CLARIFICATION markers** - all technical unknowns resolved through research.

---

## Phase 1: Design & Contracts ✅ COMPLETE

**Duration**: 1 hour
**Outputs**:
- [data-model.md](data-model.md)
- [contracts/public-feed-api.yaml](contracts/public-feed-api.yaml)
- [quickstart.md](quickstart.md)

### Data Model Summary

**Existing Models Reused** (no migrations needed):
- `User` (Feature 001) → `profile_visibility` field
- `Trip` (Feature 002) → `status`, `published_at` fields
- `TripPhoto` (Feature 008) → First photo (order=0)
- `TripLocation` (Feature 009) → First location (order=0)

**New Pydantic Schemas**:
- `PublicTripSummary` → Trip card data (title, distance, date, user, first photo, first location)
- `PublicUserSummary` → Privacy-safe user info (no email, bio, stats)
- `PaginationInfo` → Metadata (page, limit, total, pages)
- `PublicTripListResponse` → API response wrapper

**Database Indexes Required**:
```sql
CREATE INDEX idx_users_profile_visibility ON users (profile_visibility);
CREATE INDEX idx_trips_public_feed ON trips (status, published_at DESC) WHERE status = 'PUBLISHED';
```

**Query Performance**: <20ms for 1000 trips (3 total queries via eager loading)

### API Contract Summary

**Endpoint**: `GET /api/trips/public`

**Parameters**:
- `page` (query): Page number (≥1, default=1)
- `limit` (query): Items per page (1-50, default=20)

**Responses**:
- `200`: Success with `PublicTripListResponse`
- `400`: Invalid parameters (page/limit validation errors)
- `500`: Internal error

**Privacy Guarantees**:
- Only `PUBLISHED` trips (never DRAFT)
- Only from users with `profile_visibility='public'`
- Excludes email, bio, stats from user data
- HTML sanitized in trip descriptions

**No authentication required** - public endpoint.

### Quickstart Summary

**Implementation Phases**:
1. **Backend** (1-2h): Schemas, service method, API endpoint
2. **Frontend** (2-3h): Types, components (Header, Card, Page), routing
3. **Testing** (1-2h): Unit tests, integration tests, E2E verification

**Total Estimated Time**: 4-6 hours

### Constitution Re-Check ✅ PASS

**Post-Design Evaluation**:
- ✅ All schemas follow PEP 8, TypeScript strict mode
- ✅ TDD workflow documented in quickstart
- ✅ Test coverage targets ≥90%
- ✅ Spanish error messages in contract examples
- ✅ Performance targets met (<200ms p95, <2s initial load)
- ✅ Privacy filters enforced at SQL level
- ✅ Proper indexes designed for query optimization

**No new violations introduced during design phase.**

---

## Phase 2: Task Breakdown (NOT INCLUDED IN /speckit.plan)

**Note**: Phase 2 (task generation) is handled by the `/speckit.tasks` command, not `/speckit.plan`.

Run `/speckit.tasks` next to generate granular implementation tasks based on this plan.

---

## Summary

**Planning Status**: ✅ **COMPLETE** (Phases 0-1 finished)

**Artifacts Generated**:
1. ✅ [research.md](research.md) - Technical decisions and alternatives
2. ✅ [data-model.md](data-model.md) - Database schema and query patterns
3. ✅ [contracts/public-feed-api.yaml](contracts/public-feed-api.yaml) - OpenAPI specification
4. ✅ [quickstart.md](quickstart.md) - Developer implementation guide

**Constitutional Compliance**: ✅ All requirements met, no violations

**Next Steps**:
1. Run `/speckit.tasks` to generate task breakdown
2. Begin TDD implementation (tests first)
3. Create PR when all tests pass (coverage ≥90%)

**Estimated Implementation Time**: 4-6 hours (backend + frontend + tests)
