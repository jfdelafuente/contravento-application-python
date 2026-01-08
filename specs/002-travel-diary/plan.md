# Implementation Plan: Diario de Viajes Digital

**Branch**: `002-travel-diary` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-travel-diary/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementar el sistema de "Diario de Viajes Digital" que permite a los ciclistas documentar sus aventuras de cicloturismo mediante entradas de viaje con texto enriquecido, galerías de fotos, metadata del viaje (fechas, distancia, dificultad), etiquetas de categorización, y sistema de borradores.

**Enfoque técnico**: Backend FastAPI con arquitectura clean (API → Service → Model), almacenamiento dual PostgreSQL/SQLite, procesamiento asíncrono de imágenes con Pillow, sanitización HTML para texto enriquecido, y filesystem local para almacenamiento de fotos con migración futura a S3-compatible. Implementación en 5 fases priorizadas desde MVP (crear/publicar viajes) hasta funcionalidades avanzadas (borradores con auto-guardado).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- FastAPI 0.104+ (async web framework)
- SQLAlchemy 2.0+ (async ORM)
- Pillow 10.0+ (image processing)
- Bleach 6.0+ (HTML sanitization)
- python-multipart (file uploads)
- Alembic (database migrations)

**Storage**:
- Database: PostgreSQL 15+ (production) / SQLite 3.40+ (dev/test)
- Files: Filesystem local `backend/storage/trip_photos/{year}/{month}/{trip_id}/` (MVP)
- Future migration path: S3-compatible storage (AWS S3, MinIO, Cloudflare R2)

**Testing**: pytest 7.4+ with async support, pytest-cov for coverage (≥90% required)

**Target Platform**: Linux server (Ubuntu 22.04+), Docker containers for production

**Project Type**: Web application (backend API only - this feature)

**Performance Goals**:
- Simple trip queries: <200ms p95 (SC-023)
- Photo upload + processing: <3s per photo (SC-005)
- Concurrent trip creation: 50 users without degradation (SC-021)
- Trip publication: <2s (no photos) / <5s (with photos) (SC-003)

**Constraints**:
- Photo file size: 10MB max per photo, 20 photos max per trip
- Description length: 50,000 characters max
- Batch photo upload: Must use background tasks to avoid timeout
- HTML sanitization: Strict whitelist to prevent XSS
- Auto-save interval: 30 seconds for draft preservation

**Scale/Scope**:
- Initial: <1,000 users, ~10,000 trips
- Target: Support 500 trips per user without performance degradation (SC-022)
- Storage estimate: ~5MB average per trip (SC-024)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Code Quality & Maintainability ✅

**Status**: PASS

- PEP 8 compliance enforced via Black formatter and Ruff linter
- Type hints required on all functions (already established pattern)
- Google-style docstrings for all public APIs
- Single Responsibility: TripService, PhotoProcessorService, TagService separated
- No magic numbers: All limits (20 photos, 10MB, 50k chars) as constants in config

### Principle II: Testing Standards (TDD) ✅

**Status**: PASS

- TDD workflow mandatory: Tests written before implementation
- Unit tests for all services (TripService, PhotoProcessor, TagService)
- Integration tests for all API endpoints
- Contract tests for OpenAPI schemas
- Edge case coverage: Invalid dates, oversized photos, XSS attempts, concurrent edits
- Target: ≥90% coverage across all modules

**Test categories**:

- Unit: Business logic (trip creation, photo processing, HTML sanitization)
- Integration: API endpoints, database operations, file storage
- Contract: Request/response validation against OpenAPI spec

### Principle III: User Experience Consistency ✅

**Status**: PASS

- All API responses follow `{success, data, error}` structure (established pattern)
- Error messages in Spanish with actionable guidance
- Field-specific validation errors (e.g., "La distancia debe ser entre 0.1 y 10,000 km")
- HTTP status codes: 200 (success), 400 (validation), 401 (auth), 404 (not found), 500 (server error)
- Timezone-aware datetime handling for trip dates
- Accessibility: Auto-generated alt text for photos

### Principle IV: Performance Requirements ✅

**Status**: PASS

- Database indexes on: (user_id, status, published_at), (tag.normalized), (trip_id, order)
- Eager loading with `joinedload()` to prevent N+1 queries
- Pagination: Max 50 trips per page
- Background tasks for photo processing (async via FastAPI BackgroundTasks)
- Image optimization: Reduce to 30% original size while maintaining quality
- Connection pooling via SQLAlchemy async engine

**Performance targets**:

- Simple queries: <200ms p95
- Photo processing: <3s per photo
- Concurrent operations: 50 trips/sec without degradation

### Security & Data Protection ✅

**Status**: PASS

- HTML sanitization with Bleach (whitelist: b, i, ul, ol, li, a, p, br)
- File upload validation: MIME type check + extension validation + size limits
- Authorization: Only trip owner can edit/delete (enforced in TripService)
- SQL injection prevention: SQLAlchemy ORM only (no raw SQL)
- XSS prevention: HTML sanitization on all user text input
- File size limits: 10MB per photo, 20 photos max per trip

### Development Workflow ✅

**Status**: PASS

- Feature branch: `002-travel-diary` (current)
- Database migrations: Alembic with reversible up/down migrations
- All migrations tested in both PostgreSQL and SQLite
- CI/CD: Tests + linting before merge (existing pipeline)

**Gate Result**: ✅ ALL CHECKS PASSED - Proceed to Phase 0

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
│   ├── models/
│   │   ├── user.py               # Existing: User, UserProfile
│   │   ├── stats.py               # Existing: UserStats, Achievement
│   │   ├── social.py              # Existing: Follow
│   │   └── trip.py                # NEW: Trip, TripPhoto, Tag, TripTag, TripLocation
│   │
│   ├── schemas/
│   │   └── trip.py                # NEW: Pydantic schemas for Trip CRUD
│   │
│   ├── services/
│   │   ├── trip_service.py        # NEW: Business logic for trips
│   │   ├── photo_processor.py     # NEW: Image processing utilities
│   │   └── html_sanitizer.py      # NEW: HTML cleaning for rich text
│   │
│   ├── api/
│   │   └── trips.py               # NEW: FastAPI routes for trips
│   │
│   ├── utils/
│   │   └── file_storage.py        # NEW: File system operations
│   │
│   └── migrations/
│       └── versions/
│           └── YYYYMMDD_HHMM_*_add_trips.py  # NEW: Alembic migration
│
├── storage/                       # NEW: File storage directory
│   └── trip_photos/
│       └── {year}/
│           └── {month}/
│               └── {trip_id}/
│                   ├── original_*.jpg
│                   ├── optimized_*.jpg
│                   └── thumb_*.jpg
│
└── tests/
    ├── unit/
    │   ├── test_trip_service.py   # NEW: Trip business logic tests
    │   ├── test_photo_processor.py # NEW: Image processing tests
    │   └── test_html_sanitizer.py  # NEW: HTML sanitization tests
    │
    ├── integration/
    │   └── test_trips_api.py       # NEW: API endpoint tests
    │
    └── contract/
        └── test_trip_contracts.py  # NEW: OpenAPI schema validation
```

**Structure Decision**: Web application structure (Option 2). This feature extends the existing backend with new models, services, and API endpoints. Frontend implementation is out of scope for this specification. The storage directory is added at backend root for local file management during MVP phase.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All design decisions align with constitution principles.
