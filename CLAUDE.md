# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ContraVento** is a cycling social platform built with FastAPI (backend) and React (frontend planned). The platform enables cyclists to document trips, share routes, track statistics, and connect with the cycling community.

## Commands

### Setup & Installation

```bash
# Navigate to backend
cd backend

# Install dependencies with Poetry
poetry install

# Generate SECRET_KEY for .env
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Copy and configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY and other settings
```

### Database Migrations

```bash
# Apply all migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Rollback last migration
poetry run alembic downgrade -1

# View migration history
poetry run alembic history
```

### Frontend Development

```bash
# Install dependencies (first time only)
cd frontend
npm install

# Start development server
npm run dev

# Quick restart (kills all Node.js processes and starts fresh)
# Windows CMD:
restart-frontend.bat

# Windows PowerShell:
.\restart-frontend.ps1

# Linux/Mac:
./restart-frontend.sh
```

### Local Development Options

ContraVento offers multiple ways to develop locally, from instant SQLite setup to full Docker environments:

#### Option 1: LOCAL-DEV (SQLite - No Docker) ⚡ FASTEST & RECOMMENDED

**Zero configuration, instant startup with SQLite database**

```bash
# First-time setup (one-time) - Creates DB, admin user, test users, and seeds data
./run-local-dev.sh --setup      # Linux/Mac
.\run-local-dev.ps1 -Setup      # Windows PowerShell

# Start development server
./run-local-dev.sh              # Linux/Mac
.\run-local-dev.ps1             # Windows PowerShell

# Access:
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Database: backend/contravento_dev.db (SQLite file)

# Default credentials (auto-created during setup):
# - Admin:  admin / AdminPass123!
# - User:   testuser / TestPass123!
```

**Perfect for:**
- ✅ Quick development iterations
- ✅ Learning the codebase
- ✅ Working on trips, stats, profiles
- ✅ Prototyping features
- ✅ No Docker needed!

---

#### Option 2: LOCAL-MINIMAL (PostgreSQL via Docker)

**When you need PostgreSQL compatibility testing**

```bash
# Setup
cp .env.local-minimal.example .env.local-minimal
nano .env.local-minimal
./deploy.sh local-minimal

# Access:
# - Backend API: http://localhost:8000
# - PostgreSQL: localhost:5432
```

**Perfect for:**
- ✅ Testing PostgreSQL-specific features
- ✅ Pre-staging validation
- ✅ Database migration testing

---

#### Option 3: LOCAL-FULL (Complete Stack via Docker)

**When you need email testing, Redis, or visual DB tools**

```bash
./deploy.sh local

# Access:
# - Backend API: http://localhost:8000
# - MailHog UI: http://localhost:8025 (email testing)
# - pgAdmin: http://localhost:5050 (database UI)
# - PostgreSQL: localhost:5432
# - Redis: localhost:6379
```

**Perfect for:**
- ✅ Testing auth/email features
- ✅ Implementing Redis cache
- ✅ Full-stack integration testing

---

#### Other Environments

```bash
./deploy.sh dev       # Development/Integration (Nginx, real SMTP)
./deploy.sh staging   # Staging (production mirror with monitoring)
./deploy.sh prod      # Production (high availability, SSL/TLS)
```

**Quick Reference:**

| Environment | Startup | Docker | Database | Use When |
|------------|---------|--------|----------|----------|
| **local-dev** | ⚡ Instant | ❌ No | SQLite | Daily development (RECOMMENDED) |
| **local-minimal** | ~10s | ✅ Yes | PostgreSQL | PostgreSQL testing |
| **local-full** | ~20s | ✅ Yes | PostgreSQL | Email/cache testing |

See [backend/docs/DEPLOYMENT.md](backend/docs/DEPLOYMENT.md) for complete deployment guide.

### Development Server

```bash
# Run development server with hot reload
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# API docs at: http://localhost:8000/docs
```

### User Management

**Note**: Admin and test users are automatically created during `./run-local-dev.sh --setup`. Use the scripts below for additional users or manual management.

```bash
cd backend

# Create admin user (auto-created during setup, or manually)
poetry run python scripts/create_admin.py
# Default: admin / admin@contravento.com / AdminPass123!

# Create additional admin with custom credentials
poetry run python scripts/create_admin.py --username myadmin --email admin@mycompany.com --password "MySecurePass123!"

# Create default test users (testuser and maria_garcia)
poetry run python scripts/create_verified_user.py

# Create custom verified user
poetry run python scripts/create_verified_user.py --username john --email john@example.com --password "SecurePass123!"

# Create custom admin user
poetry run python scripts/create_verified_user.py --username myadmin --email admin@mycompany.com --password "AdminPass123!" --role admin

# Verify existing user by email
poetry run python scripts/create_verified_user.py --verify-email test@example.com

# Promote existing user to admin
poetry run python scripts/promote_to_admin.py --username testuser

# Demote admin to regular user
poetry run python scripts/promote_to_admin.py --username admin --demote
```

**Default credentials (auto-created during setup):**

- **Admin**: `admin` / `admin@contravento.com` / `AdminPass123!` (role: ADMIN)
- **User**: `testuser` / `test@example.com` / `TestPass123!` (role: USER)

**Additional users (created manually with scripts):**

- `maria_garcia` / `maria@example.com` / `SecurePass456!` (role: USER)

### Testing

```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage (required ≥90%)
poetry run pytest --cov=src --cov-report=html --cov-report=term

# Run specific test types
poetry run pytest tests/unit/ -v              # Unit tests only
poetry run pytest tests/integration/ -v       # Integration tests only
poetry run pytest tests/contract/ -v          # Contract tests only

# Run single test file
poetry run pytest tests/unit/test_auth_service.py -v

# Run single test function
poetry run pytest tests/unit/test_auth_service.py::test_register_user -v
```

### Code Quality

```bash
cd backend

# Format code (required before commit)
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/

# Run all quality checks
poetry run black src/ tests/ && \
poetry run ruff check src/ tests/ && \
poetry run mypy src/ && \
poetry run pytest --cov=src
```

## Architecture

### Layer Structure (Clean Architecture)

The backend follows a strict layered architecture with clear separation of concerns:

```
API Layer (FastAPI Routers)
    ↓ calls
Service Layer (Business Logic)
    ↓ uses
Model Layer (SQLAlchemy ORM)
    ↓ persists to
Database (SQLite dev/test, PostgreSQL prod)
```

**Critical Rule**: Layers can only call downward. APIs call Services, Services use Models. Never skip layers.

### Key Architectural Patterns

1. **Dependency Injection**: All database sessions and current user passed via FastAPI `Depends()`
2. **Schema Separation**: Pydantic schemas for validation (in `schemas/`) are distinct from SQLAlchemy models (in `models/`)
3. **Service Layer Pattern**: All business logic lives in `services/`, never in API routes or models
4. **Repository Pattern**: Services interact with database through async SQLAlchemy session, not direct SQL

### Module Organization

- **`src/models/`**: SQLAlchemy ORM models (User, UserProfile, UserStats, etc.)
- **`src/schemas/`**: Pydantic models for request/response validation
- **`src/services/`**: Business logic (AuthService, ProfileService, StatsService, SocialService)
- **`src/api/`**: FastAPI routers - thin layer that calls services
- **`src/utils/`**: Shared utilities (security, email, file storage, validators)
- **`src/config.py`**: Environment variable management with Pydantic Settings
- **`src/database.py`**: Async SQLAlchemy engine and session management

## Database Strategy

**Dual Database Approach** - Same codebase runs on both:

- **Development/Testing**: SQLite with aiosqlite (file-based or in-memory)
  - Zero configuration, fast tests, no Docker required
  - In-memory mode for test isolation

- **Production**: PostgreSQL with asyncpg
  - Native UUID support, array columns, better concurrency
  - Connection pooling (pool_size=20)

**Important Differences**:
- UUIDs: PostgreSQL uses native UUID type, SQLite stores as TEXT
- Arrays: PostgreSQL uses ARRAY[], SQLite uses JSON
- Foreign Keys: Must enable explicitly in SQLite with `PRAGMA foreign_keys=ON`

Alembic migrations detect the dialect and apply appropriate DDL for each database type.

## Constitution Requirements (Non-Negotiable)

### I. Code Quality
- PEP 8 with black formatter (100 char line length)
- Type hints required on ALL functions
- Google-style docstrings for public functions
- Single Responsibility Principle strictly enforced
- No magic numbers - use constants in config.py

### II. Testing (TDD Mandatory)
- **Write tests FIRST** before any implementation
- Coverage requirement: ≥90% across all modules
- Test structure:
  - Unit tests: Business logic in services/
  - Integration tests: API endpoints, database operations
  - Contract tests: OpenAPI schema validation
- All tests must pass before PR merge

### III. User Experience
- All user-facing text in Spanish (primary language)
- Standardized JSON API responses:
  ```json
  {
    "success": true,
    "data": {...},
    "error": null
  }
  ```
- Field-specific validation errors with Spanish messages
- UTC timestamps with timezone awareness

### IV. Performance
- Simple queries: <200ms p95
- Auth endpoints: <500ms p95
- Photo uploads: <2s for 5MB files
- Use eager loading to prevent N+1 queries
- Pagination: max 50 items per page

### V. Security
- Bcrypt password hashing with 12 rounds (production)
- JWT: 15min access tokens, 30-day refresh tokens
- Rate limiting: 5 login attempts, 15min lockout
- Only use SQLAlchemy ORM - never raw SQL
- Validate all file uploads (MIME type, size, content)

## Authentication & Authorization

**JWT Token Flow**:
1. User logs in → receives access token (15min) + refresh token (30 days)
2. Access token in Authorization header: `Bearer {token}`
3. When access token expires → use refresh token to get new pair
4. On logout → invalidate refresh token

**Dependency Injection Pattern**:
```python
from src.api.deps import get_current_user, get_db

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # current_user is automatically validated from JWT
    # db is async database session
    pass
```

## Specification-Driven Development

This project uses a structured specification workflow in `specs/`:

1. **spec.md**: User stories, functional requirements (FR-###), success criteria (SC-###)
2. **plan.md**: Technical implementation plan, architecture decisions
3. **data-model.md**: Database schema with DDL for SQLite and PostgreSQL
4. **contracts/**: OpenAPI YAML files defining all API endpoints
5. **tasks.md**: Step-by-step implementation tasks

**Always reference**:
- Functional requirements as FR-### in code comments
- Success criteria as SC-### for performance targets
- OpenAPI contracts for exact request/response schemas

## File Upload Handling

Profile photos follow this pattern:
1. Validate: Check MIME type, size (max 5MB)
2. Store original temporarily
3. **Background task**: Resize to 400x400px with Pillow
4. Save to: `storage/profile_photos/{year}/{month}/{user_id}_{uuid}.jpg`
5. Update database with photo_url
6. Delete original

**Security**: Never trust client-provided filenames or MIME types - validate content.

## Travel Diary Feature (002-travel-diary)

The Travel Diary feature allows cyclists to document trips with rich content, photos, tags, and draft workflow.

### Key Entities

- **Trip**: Main entity for documenting cycling trips
  - Fields: title, description, start_date, end_date, distance_km, difficulty, status (DRAFT/PUBLISHED)
  - Relationships: belongs to User, has many TripPhoto, TripLocation, Tag
- **TripPhoto**: Photos attached to trips (max 20 per trip)
  - Fields: url, file_size, width, height, order, caption
  - Stored at: `storage/trip_photos/{year}/{month}/{trip_id}/`
- **Tag**: Categorization tags (case-insensitive matching)
  - Fields: name, normalized (lowercase for matching), usage_count
  - Max 10 tags per trip
- **TripLocation**: Optional location data for trips
  - Fields: latitude, longitude, address, country

### Trip Workflow

**Create Trip** (Draft by default):

```bash
POST /trips
{
  "title": "Ruta Bikepacking Pirineos",
  "description": "Viaje de 5 días...",
  "start_date": "2024-06-01",
  "end_date": "2024-06-05",
  "distance_km": 320.5,
  "tags": ["bikepacking", "montaña"]
}
```

**Publish Trip** (validates requirements):

```bash
POST /trips/{trip_id}/publish
# Requirements: description ≥50 chars, valid dates
```

**Upload Photos**:

```bash
POST /trips/{trip_id}/photos
Content-Type: multipart/form-data
# Max 20 photos per trip, 10MB per photo
```

**Filter Trips by Tag/Status**:

```bash
GET /users/{username}/trips?tag=bikepacking&status=PUBLISHED
GET /users/{username}/trips?status=DRAFT  # Owner-only
```

**Get Popular Tags**:

```bash
GET /tags  # Returns tags ordered by usage_count
```

### Draft Workflow

- Trips default to `status=DRAFT` on creation
- Drafts visible only to owner
- Minimal validation for drafts (title + description required)
- Publishing enforces full validation (description ≥50 chars)
- Draft→Published transition updates stats automatically

### Stats Integration

Trip actions automatically update UserStats:

- **Publish trip**: Increments trip_count, adds distance_km, updates countries
- **Upload photo**: Increments photo_count (if trip published)
- **Edit trip**: Recalculates distance_km, longest_trip_km
- **Delete trip**: Decrements trip_count, subtracts distance_km

See [backend/docs/STATS_INTEGRATION.md](backend/docs/STATS_INTEGRATION.md) for full details.

### Manual Testing

**Tags & Categorization**:

```bash
cd backend
bash scripts/test_tags.sh
# Interactive script for testing tag filtering, status filtering, pagination
```

See [backend/docs/api/TAGS_TESTING.md](backend/docs/api/TAGS_TESTING.md) for detailed manual testing guide.

### Implementation Notes

- **TripService** (`src/services/trip_service.py`): Core business logic
  - create_trip(), publish_trip(), update_trip(), delete_trip()
  - upload_photo(), delete_photo(), reorder_photos()
  - get_user_trips() with tag/status filtering
- **Trips API** (`src/api/trips.py`): RESTful endpoints
- **HTML Sanitization**: Applied to trip descriptions to prevent XSS
- **Tag Normalization**: Case-insensitive matching via `tag.normalized` column
- **Photo Processing**: Background tasks for metadata extraction
- **Optimistic Locking**: Prevents concurrent edit conflicts (future enhancement)

### Data Model

See [specs/002-travel-diary/data-model.md](../specs/002-travel-diary/data-model.md) for complete schema including:

- SQLite DDL (development/testing)
- PostgreSQL DDL (production)
- Migrations in `backend/migrations/versions/`

## Testing Patterns

### TDD Workflow (Strictly Enforced)
1. Write test for feature (Red - test fails)
2. Implement minimal code to pass (Green - test passes)
3. Refactor while keeping tests passing
4. Never write production code without a failing test first

### Test Fixtures (conftest.py)
- `db_session`: Fresh SQLite in-memory database per test
- `client`: AsyncClient for API testing
- `auth_headers`: Pre-authenticated user headers for protected endpoints
- `faker`: Faker instance for generating test data

### Example Test Structure
```python
# tests/unit/test_auth_service.py
async def test_register_user(db_session):
    """Test user registration creates user and sends verification email."""
    # Arrange
    user_data = {...}

    # Act
    result = await AuthService.register(db_session, user_data)

    # Assert
    assert result.email == user_data["email"]
    assert result.is_verified is False
```

## Error Handling

All errors must return standardized JSON with Spanish messages:

```python
from fastapi import HTTPException

# Bad request with field-specific error
raise HTTPException(
    status_code=400,
    detail={
        "code": "VALIDATION_ERROR",
        "message": "El email ya está registrado",
        "field": "email"
    }
)

# Unauthorized
raise HTTPException(
    status_code=401,
    detail={
        "code": "UNAUTHORIZED",
        "message": "Token de autenticación inválido"
    }
)
```

## Environment Variables

Critical variables (see `.env.example` for complete list):
- `DATABASE_URL`: Database connection string (SQLite or PostgreSQL)
- `SECRET_KEY`: JWT secret (min 32 chars) - generate with `secrets.token_urlsafe(32)`
- `BCRYPT_ROUNDS`: 12 for production, 4 for tests (faster)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: 15
- `REFRESH_TOKEN_EXPIRE_DAYS`: 30
- `UPLOAD_MAX_SIZE_MB`: 5
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Cycling Types - Dynamic Management

ContraVento allows dynamic management of cycling types through database instead of hardcoded values.

### Setup

```bash
cd backend

# Apply migration to create cycling_types table
poetry run alembic upgrade head

# Load initial types from YAML config
poetry run python scripts/seed_cycling_types.py

# List current types
poetry run python scripts/seed_cycling_types.py --list
```

### Configuration File

Initial types are defined in `config/cycling_types.yaml`:

```yaml
cycling_types:
  - code: bikepacking
    display_name: Bikepacking
    description: Viajes de varios días en bicicleta con equipaje completo
    is_active: true
```

### API Endpoints

**Public** (no authentication):

- `GET /cycling-types`: List active types

**Admin** (requires authentication):

- `GET /admin/cycling-types`: List all types
- `POST /admin/cycling-types`: Create new type
- `PUT /admin/cycling-types/{code}`: Update type
- `DELETE /admin/cycling-types/{code}`: Deactivate type (soft delete)

### Adding New Types

**Option 1**: Via YAML + seed script (for initial setup)

```bash
# Edit config/cycling_types.yaml
# Add new type entry

# Load with force to update existing
poetry run python scripts/seed_cycling_types.py --force
```

**Option 2**: Via API (for operational changes)

```bash
curl -X POST http://localhost:8000/admin/cycling-types \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "cyclocross",
    "display_name": "Ciclocross",
    "description": "Carreras en circuitos mixtos",
    "is_active": true
  }'
```

### Validation

Cycling types are validated dynamically against the database:

- Legacy validator `validate_cycling_type()`: Uses hardcoded values (backward compatibility)
- New validator `validate_cycling_type_async()`: Queries database for active types
- ProfileService uses dynamic validation when users update their cycling_type

See [backend/docs/CYCLING_TYPES.md](backend/docs/CYCLING_TYPES.md) for complete documentation.

## Common Pitfalls to Avoid

1. **Don't skip TDD**: Tests must be written before implementation
2. **Don't mix layers**: API routes should only call services, never access models directly
3. **Don't use raw SQL**: Always use SQLAlchemy ORM for query safety
4. **Don't forget async**: All database operations and file I/O must be async
5. **Don't hardcode Spanish text**: Use constants or configuration for i18n readiness
6. **Don't skip foreign key pragma**: SQLite requires explicit `PRAGMA foreign_keys=ON`
7. **Don't trust user input**: Validate everything with Pydantic schemas
8. **Don't forget indexes**: Add indexes for frequently queried columns
9. **Don't return stack traces to users**: Catch exceptions and return friendly Spanish errors
10. **Don't skip coverage**: ≥90% is mandatory before PR approval

## Specification Commands

This project uses `/speckit.*` commands for specification-driven development:

- `/speckit.specify`: Create feature specifications
- `/speckit.plan`: Generate implementation plans
- `/speckit.tasks`: Break down features into tasks
- `/speckit.implement`: Execute implementation phases

See `.specify/` directory for templates and workflows.

## Active Technologies
- Python 3.12 (backend), TypeScript 5 (frontend) + FastAPI, SQLAlchemy 2.0, Pydantic (backend), React 18, react-leaflet, Leaflet.js (frontend) (009-gps-coordinates)
- PostgreSQL (production), SQLite (development) - TripLocation model already has latitude/longitude Float columns (009-gps-coordinates)
- TypeScript 5 (frontend), Python 3.12 (backend - no changes) + react-leaflet 4.x, Leaflet.js 1.9.x, lodash.debounce 4.x (NEW), axios 1.x (010-reverse-geocoding)
- No new backend storage (uses existing TripLocation model) (010-reverse-geocoding)

### Backend (Python/FastAPI)
- Python 3.12 + FastAPI (001-user-profiles, 002-travel-diary)
- SQLAlchemy 2.0 (async ORM)
- PostgreSQL (production) / SQLite (development)

### Frontend (React/TypeScript)
- React 18 + TypeScript 5 + Vite (005-frontend-user-profile, 008-travel-diary-frontend)
- React Router 6 for navigation
- React Hook Form + Zod for form validation
- Axios for HTTP client (HttpOnly cookie authentication)
- Cloudflare Turnstile for CAPTCHA
- react-dropzone for photo uploads
- yet-another-react-lightbox for photo galleries
- react-leaflet for map display

## Travel Diary Frontend (Feature 008)

The Travel Diary Frontend provides a comprehensive UI for managing cycling trips with photos, tags, and rich metadata.

### Architecture Pattern: Container/Presentational Components

**Smart Containers** (Pages):
- Manage state with hooks (useTripList, useTripForm, useTripPhotos)
- Handle API calls and error handling
- Pass data and callbacks to presentational components

**Presentational Components**:
- Display UI based on props
- No direct API calls
- Reusable across features

Example:
```typescript
// Smart Container
export const TripsListPage: React.FC = () => {
  const { trips, isLoading, error } = useTripList(username);
  const { filters, setFilter } = useTripFilters();

  return (
    <div>
      <TripFilters filters={filters} onChange={setFilter} />
      <TripCard trips={trips} />
    </div>
  );
};

// Presentational Component
interface TripCardProps {
  trip: Trip;
  onClick?: (tripId: string) => void;
}

export const TripCard: React.FC<TripCardProps> = ({ trip, onClick }) => {
  return (
    <div className="trip-card" onClick={() => onClick?.(trip.trip_id)}>
      <img src={getPhotoUrl(trip.photos[0]?.photo_url)} alt={trip.title} />
      <h3>{trip.title}</h3>
    </div>
  );
};
```

### Custom Hooks Pattern

All business logic lives in custom hooks for reusability:

**Data Fetching Hooks**:
```typescript
// frontend/src/hooks/useTripList.ts
export const useTripList = (username: string, filters?: TripFilters) => {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const response = await getUserTrips(username, filters);
        setTrips(response.data);
      } catch (err: any) {
        setError(err.response?.data?.error?.message || 'Error al cargar viajes');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrips();
  }, [username, filters]);

  return { trips, isLoading, error };
};
```

**Form Management Hooks**:
```typescript
// frontend/src/hooks/useTripForm.ts
export const useTripForm = ({ tripId, isEditMode }: Options) => {
  const methods = useForm<TripCreateInput>({
    resolver: zodResolver(tripFormSchema),
  });

  const handleSubmit = async (data: TripCreateInput, isDraft: boolean) => {
    try {
      if (isEditMode && tripId) {
        const trip = await updateTrip(tripId, data);
        toast.success('Viaje actualizado correctamente');
      } else {
        const trip = await createTrip(data);
        if (!isDraft) {
          await publishTrip(trip.trip_id);
        }
        toast.success('Viaje creado correctamente');
      }
      navigate('/trips');
    } catch (error: any) {
      // Handle optimistic locking conflicts (409)
      if (error.response?.status === 409) {
        toast.error('El viaje fue modificado por otra sesión. Recarga la página...');
      }
    }
  };

  return { methods, handleSubmit, isSubmitting };
};
```

### Photo Upload Pattern

Chunked upload with progress tracking using react-dropzone:

```typescript
// frontend/src/hooks/useTripPhotos.ts
export const useTripPhotos = ({ tripId, maxPhotos = 20 }: Options) => {
  const [photos, setPhotos] = useState<PhotoFile[]>([]);

  const uploadPhoto = useCallback(
    async (file: File, onProgress: (progress: number) => void) => {
      try {
        const response = await uploadTripPhoto(tripId, file);
        onProgress(100);
        return response.photo_id;
      } catch (error: any) {
        throw new Error(error.response?.data?.error?.message || 'Error al subir foto');
      }
    },
    [tripId]
  );

  const reorderPhotos = useCallback(
    async (photoIds: string[]) => {
      // Optimistic update
      const reordered = photoIds
        .map((id) => photos.find((p) => p.photoId === id))
        .filter(Boolean);
      setPhotos(reordered);

      // Persist to backend
      try {
        await reorderTripPhotos(tripId, photoIds);
      } catch (error) {
        setPhotos(photos); // Revert on error
      }
    },
    [photos, tripId]
  );

  return { photos, uploadPhoto, reorderPhotos };
};
```

### Wizard Pattern (Multi-Step Forms)

Use React Hook Form's FormProvider for shared state across steps:

```typescript
// frontend/src/components/trips/TripForm/TripFormWizard.tsx
export const TripFormWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const methods = useForm<TripCreateInput>({
    resolver: zodResolver(tripFormSchema),
    mode: 'onChange',
  });

  const steps = [
    <Step1BasicInfo />,
    <Step2StoryTags />,
    <Step3Photos />,
    <Step4Review />,
  ];

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)}>
        <FormStepIndicator currentStep={currentStep} totalSteps={4} />
        {steps[currentStep]}
        <div className="wizard-navigation">
          {currentStep > 0 && <button onClick={handlePrevious}>Anterior</button>}
          {currentStep < 3 && <button onClick={handleNext}>Siguiente</button>}
          {currentStep === 3 && <button type="submit">Publicar</button>}
        </div>
      </form>
    </FormProvider>
  );
};

// Each step uses useFormContext to access shared form state
export const Step1BasicInfo: React.FC = () => {
  const { register, formState } = useFormContext<TripCreateInput>();

  return (
    <div>
      <input {...register('title')} />
      {formState.errors.title && <span>{formState.errors.title.message}</span>}
    </div>
  );
};
```

### Photo URL Helper Pattern

**CRITICAL**: Backend returns absolute URLs, not relative paths. Always use `getPhotoUrl()`:

```typescript
// frontend/src/utils/tripHelpers.ts
export const getPhotoUrl = (url: string | null | undefined): string => {
  if (!url) return '/images/placeholders/trip-placeholder.jpg';

  // Already absolute URL (from backend)
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // Relative path (development only)
  return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`;
};

// Usage
<img src={getPhotoUrl(trip.photos[0]?.photo_url)} alt={trip.title} />
```

### Optimistic Locking Pattern

Prevent concurrent edits with 409 Conflict detection:

```typescript
// frontend/src/hooks/useTripForm.ts
const handleSubmit = async (data: TripCreateInput) => {
  try {
    const trip = await updateTrip(tripId, data);
    toast.success('Viaje actualizado correctamente');
    navigate(`/trips/${trip.trip_id}`);
  } catch (error: any) {
    // Detect optimistic locking conflict
    if (error.response?.status === 409) {
      toast.error(
        'El viaje fue modificado por otra sesión. Recarga la página para ver los cambios más recientes.',
        { duration: 6000 }
      );
      throw error; // Stop execution
    }

    // Other errors
    const errorMessage = error.response?.data?.error?.message || 'Error al actualizar viaje';
    toast.error(errorMessage);
  }
};
```

### Owner-Only Actions Pattern

Check ownership on page load and hide/disable actions for non-owners:

```typescript
// frontend/src/pages/TripDetailPage.tsx
export const TripDetailPage: React.FC = () => {
  const { user } = useAuth();
  const [trip, setTrip] = useState<Trip | null>(null);

  useEffect(() => {
    const fetchTrip = async () => {
      const tripData = await getTripById(tripId);
      setTrip(tripData);
    };
    fetchTrip();
  }, [tripId]);

  // Ownership check
  const isOwner = user && trip && user.user_id === trip.user_id;

  return (
    <div>
      <h1>{trip.title}</h1>

      {/* Owner-only action buttons */}
      {isOwner && (
        <div className="actions">
          {trip.status === 'draft' && (
            <button onClick={handlePublish}>Publicar</button>
          )}
          <Link to={`/trips/${trip.trip_id}/edit`}>Editar</Link>
          <button onClick={handleDelete}>Eliminar</button>
        </div>
      )}
    </div>
  );
};
```

### Tag Normalization Pattern

Backend stores tags with both `name` (display) and `normalized` (lowercase for matching):

```typescript
// Display tags using tag.name
<div className="tags">
  {trip.tags.map(tag => (
    <Link key={tag.tag_id} to={`/trips?tag=${tag.normalized}`}>
      {tag.name}  {/* Display with original capitalization */}
    </Link>
  ))}
</div>

// Filter tags using tag.normalized
const filterTrips = (tagName: string) => {
  const params = {
    tag: tagName.toLowerCase()  // Always lowercase for matching
  };
  navigate(`/trips?${new URLSearchParams(params)}`);
};
```

### Date Handling Pattern

Backend stores dates as `YYYY-MM-DD` strings (no timezone). Parse as **local dates**:

```typescript
// frontend/src/utils/tripHelpers.ts
export const formatDate = (dateString: string): string => {
  // Force local timezone to avoid off-by-one errors
  const date = new Date(dateString + 'T00:00:00');
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatDateRange = (startDate: string, endDate?: string): string => {
  if (!endDate || startDate === endDate) {
    return formatDate(startDate);
  }

  const start = new Date(startDate + 'T00:00:00');
  const end = new Date(endDate + 'T00:00:00');

  return `${formatDate(startDate)} - ${formatDate(endDate)}`;
};
```

### Confirmation Dialog Pattern

Use modal overlays for destructive actions instead of `window.confirm()`:

```typescript
// State management
const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

// Event handlers
const handleDelete = () => setShowDeleteConfirm(true);
const confirmDelete = async () => {
  setShowDeleteConfirm(false);
  await deleteTrip(tripId);
  navigate('/trips');
};
const cancelDelete = () => setShowDeleteConfirm(false);

// Modal JSX
{showDeleteConfirm && (
  <div className="delete-dialog-overlay" onClick={cancelDelete}>
    <div className="delete-dialog" onClick={(e) => e.stopPropagation()}>
      <div className="delete-dialog-icon">
        <svg>{/* Warning icon */}</svg>
      </div>
      <h3>¿Eliminar viaje?</h3>
      <p>Esta acción es permanente y eliminará el viaje junto con todas sus fotos...</p>
      <div className="delete-dialog-actions">
        <button onClick={cancelDelete}>Cancelar</button>
        <button onClick={confirmDelete}>Eliminar</button>
      </div>
    </div>
  </div>
)}
```

### Common Pitfalls - Frontend

1. **Don't use photo URLs directly**: Always use `getPhotoUrl()` helper (backend returns absolute URLs)
2. **Don't parse dates as UTC**: Use local timezone to avoid off-by-one errors
3. **Don't skip tag normalization**: Always lowercase tags for matching
4. **Don't forget owner checks**: Hide edit/delete buttons for non-owners
5. **Don't ignore 409 conflicts**: Handle optimistic locking errors gracefully
6. **Don't use window.confirm()**: Use modal dialogs for better UX
7. **Don't skip loading states**: Show skeletons/spinners during async operations
8. **Don't forget Spanish error messages**: All user-facing text must be in Spanish
9. **Don't batch state updates in forms**: Use single FormProvider for wizard steps
10. **Don't forget photo reordering**: Wire onReorder callback to persist changes

### Testing Frontend Features

```bash
# Manual testing guide
cat specs/008-travel-diary-frontend/TESTING_GUIDE.md

# Troubleshooting common issues
cat specs/008-travel-diary-frontend/TROUBLESHOOTING.md

# Run frontend dev server
cd frontend
npm run dev

# Access at http://localhost:5173
```

## Reverse Geocoding Feature (Feature 010)

The Reverse Geocoding feature enables users to add trip locations by clicking on a map, automatically retrieving place names from coordinates using the Nominatim API (OpenStreetMap).

### Key Features

**User Stories**:
1. **US1 - Click to Add**: Click map → automatic geocoding → confirm location with suggested name
2. **US2 - Drag to Adjust**: Drag existing markers → update coordinates → re-geocode automatically
3. **US3 - Edit Names**: Modify suggested place names before saving

### Core Components

**[LocationConfirmModal.tsx](frontend/src/components/trips/LocationConfirmModal.tsx)**
Modal component for confirming geocoded locations:
- Displays suggested place name from reverse geocoding
- Editable name input (max 200 chars, required)
- Shows coordinates (latitude, longitude with 6 decimal precision)
- Loading/error states with Spanish messages
- Full ARIA accessibility support
- Mobile-responsive design with touch optimizations

**[useReverseGeocode.ts](frontend/src/hooks/useReverseGeocode.ts)**
Custom hook for geocoding operations:
```typescript
const { geocode, debouncedGeocode, isLoading, error } = useReverseGeocode();

// Immediate geocoding (for map clicks)
const result = await geocode(lat, lng);

// Debounced geocoding (for drag operations - 1000ms delay)
debouncedGeocode(lat, lng);
```

**[geocodingService.ts](frontend/src/services/geocodingService.ts)**
Service layer for Nominatim API:
- Rate limit compliance (1 req/sec via debounce)
- Coordinate validation (lat: -90 to 90, lng: -180 to 180)
- Spanish place name extraction with fallbacks
- Error handling with localized messages

**[geocodingCache.ts](frontend/src/utils/geocodingCache.ts)**
LRU cache for API responses:
- 100-entry capacity with automatic eviction
- ~111m precision (rounds to 3 decimal places)
- Hit/miss tracking with development logging
- Cache stats API for monitoring

### Implementation Patterns

#### 1. Debouncing Pattern

Prevents rate limit violations during rapid interactions:

```typescript
// In TripDetailPage - handling marker drag
const { debouncedGeocode } = useReverseGeocode();

const handleMarkerDrag = (locationId: string, newLat: number, newLng: number) => {
  // Update coordinates immediately (optimistic update)
  updateLocationCoordinates(locationId, newLat, newLng);

  // Geocode after 1000ms of no movement (debounced)
  debouncedGeocode(newLat, newLng);
};
```

**Important**: Use `geocode()` for single clicks, `debouncedGeocode()` for drag operations.

#### 2. Cache-First Strategy

Reduces API calls by ~70-80% in typical usage:

```typescript
// Automatic caching in geocodingService
export async function reverseGeocode(lat: number, lng: number): Promise<GeocodingResponse> {
  // Check cache first (O(1) lookup)
  const cached = geocodingCache.get(lat, lng);
  if (cached) {
    console.log('[Cache HIT]', cached);
    return cached;
  }

  // Cache miss - call API
  const response = await callNominatimAPI(lat, lng);
  geocodingCache.set(lat, lng, response);

  return response;
}
```

**Cache precision**: Coordinates are rounded to 3 decimal places (~111 meters at equator).

#### 3. Modal Confirmation Pattern

Two-step workflow for location selection:

```typescript
const [pendingLocation, setPendingLocation] = useState<LocationSelection | null>(null);
const { geocode } = useReverseGeocode();

// Step 1: Map click → geocode → show modal
const handleMapClick = async (lat: number, lng: number) => {
  try {
    const result = await geocode(lat, lng);
    setPendingLocation(result); // Triggers modal
  } catch (error) {
    toast.error('Error al obtener ubicación');
  }
};

// Step 2: User confirms → persist to database
const handleConfirm = async (name: string, lat: number, lng: number) => {
  await addLocationToTrip(tripId, { name, latitude: lat, longitude: lng });
  setPendingLocation(null); // Close modal
};

<LocationConfirmModal
  location={pendingLocation}
  onConfirm={handleConfirm}
  onCancel={() => setPendingLocation(null)}
/>
```

### Accessibility Features (T044)

Full WCAG 2.1 AA compliance:

```typescript
// Dialog structure
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="location-modal-title"
  aria-describedby="location-modal-description"
>
  {/* Loading state */}
  <div role="status" aria-live="polite">
    <div className="spinner" aria-hidden="true" />
    <p>Obteniendo nombre del lugar...</p>
  </div>

  {/* Error state */}
  <div role="alert" aria-live="assertive">
    <p>{errorMessage}</p>
  </div>

  {/* Buttons with context-aware labels */}
  <button
    aria-label={!isNameValid ?
      "Confirmar ubicación (deshabilitado: nombre inválido)" :
      "Confirmar y guardar la ubicación"
    }
    aria-disabled={!isNameValid}
  >
    Confirmar ubicación
  </button>
</div>
```

**Screen reader support**:
- Live regions announce loading/error states
- Dynamic aria-labels describe button state
- Keyboard navigation (Tab, Enter, Esc)

### Mobile Responsiveness (T045)

Touch-optimized design for mobile devices:

**Layout**:
- Bottom-aligned modal on mobile (easier thumb reach)
- Full-width buttons (stacked vertically)
- 85vh max height (leaves space for mobile UI)

**Touch Targets**:
- Minimum 44×44px (iOS Human Interface Guidelines)
- Confirm button: 48px height
- Close button: 40×40px on mobile

**Typography**:
- 16px font size on inputs (prevents iOS zoom on focus)
- Larger button text (1.0625rem / 17px)

**Device Detection**:
```css
/* Touch device optimizations */
@media (hover: none) and (pointer: coarse) {
  .location-confirm-modal-button {
    min-height: 48px;
  }

  /* Remove hover effects on touch devices */
  .location-confirm-modal-button:hover {
    transform: none;
  }
}
```

### Performance Optimizations

**Cache Performance** (T047):
- Development logging shows hit/miss rates
- Enable via `geocodingCache.setLogging(true)`
- Stats API: `geocodingCache.getStats()`

**Rate Limit Compliance**:
- 1000ms debounce on drag operations
- Nominatim limit: 1 request/second
- 429 error handling with Spanish message

**Network Optimization**:
- 10-second timeout on API calls
- Retry logic with exponential backoff
- Graceful degradation (manual name entry on failure)

### Error Handling

All errors use Spanish messages:

```typescript
// Validation errors
throw new Error('Las coordenadas deben estar entre -90 y 90 (latitud), -180 y 180 (longitud)');

// Rate limit (429)
'Demasiadas solicitudes al servidor de mapas. Espera un momento e intenta de nuevo.'

// Network timeout
'El servidor de mapas no responde. Verifica tu conexión.'

// Geocoding failure
'No se pudo obtener el nombre del lugar. Puedes ingresar un nombre manualmente.'
```

### Testing

**Unit Tests**: [LocationConfirmModal.test.tsx](frontend/tests/unit/LocationConfirmModal.test.tsx)
- 23/23 tests passing (100% coverage)
- Name validation, editing, trimming
- Loading/error states
- Accessibility features
- Modal behavior (overlay click, ESC key)

**Manual Testing**: See [TESTING_GUIDE.md](frontend/TESTING_GUIDE.md) - Reverse Geocoding section
- User Story scenarios (click, drag, edit)
- Accessibility testing (screen readers)
- Mobile device testing
- Performance validation (cache hit rates)

### Common Pitfalls to Avoid

1. **Don't skip debounce for drag**: Always use `debouncedGeocode()` for marker drag events to prevent rate limits
2. **Don't ignore validation**: Validate coordinates before geocoding (lat: -90 to 90, lng: -180 to 180)
3. **Don't forget loading states**: Show spinner during API calls to provide feedback
4. **Don't use geocoding without cache**: Always use the `geocodingService` which includes caching
5. **Don't hardcode English text**: All user-facing messages must be in Spanish
6. **Don't assume geocoding always succeeds**: Handle errors gracefully with manual name entry fallback
7. **Don't skip accessibility attributes**: ARIA labels are required for screen reader support
8. **Don't ignore mobile UX**: Use touch-friendly targets (44px minimum) and prevent iOS zoom (16px font)

### Integration Example

Complete integration in TripDetailPage:

```typescript
export const TripDetailPage: React.FC = () => {
  const [trip, setTrip] = useState<Trip | null>(null);
  const [isMapEditMode, setIsMapEditMode] = useState(false);
  const [pendingLocation, setPendingLocation] = useState<LocationSelection | null>(null);
  const { geocode, debouncedGeocode } = useReverseGeocode();

  // Handle map click (User Story 1)
  const handleMapClick = async (lat: number, lng: number) => {
    try {
      const result = await geocode(lat, lng);
      setPendingLocation(result);
    } catch (error: any) {
      toast.error(error.message || 'Error al geocodificar ubicación');
    }
  };

  // Handle marker drag (User Story 2)
  const handleMarkerDrag = (locationId: string, newLat: number, newLng: number) => {
    // Optimistic update
    setTrip(prev => ({
      ...prev!,
      locations: prev!.locations.map(loc =>
        loc.location_id === locationId
          ? { ...loc, latitude: newLat, longitude: newLng }
          : loc
      ),
    }));

    // Debounced geocoding
    debouncedGeocode(newLat, newLng);
  };

  // Handle location confirmation (User Story 3)
  const handleLocationConfirm = async (name: string, lat: number, lng: number) => {
    if (pendingLocation?.locationId) {
      // Update existing location
      await updateTripLocation(trip!.trip_id, pendingLocation.locationId, {
        name,
        latitude: lat,
        longitude: lng,
      });
    } else {
      // Add new location
      await addTripLocation(trip!.trip_id, { name, latitude: lat, longitude: lng });
    }

    setPendingLocation(null);
    refetchTrip();
  };

  return (
    <div>
      <TripMap
        locations={trip?.locations || []}
        tripTitle={trip?.title || ''}
        isEditMode={isMapEditMode}
        onMapClick={handleMapClick}
        onMarkerDrag={handleMarkerDrag}
      />

      <LocationConfirmModal
        location={pendingLocation}
        onConfirm={handleLocationConfirm}
        onCancel={() => setPendingLocation(null)}
      />
    </div>
  );
};
```

### API Reference

**Nominatim API** (OpenStreetMap):
- Endpoint: `https://nominatim.openstreetmap.org/reverse`
- Format: `json`
- Accept-Language: `es` (Spanish names preferred)
- User-Agent: `ContraVento/1.0` (required by Nominatim)
- Rate limit: 1 request/second

**Response Structure**:
```typescript
interface GeocodingResponse {
  place_id: number;
  display_name: string; // Full address
  address: {
    leisure?: string;    // Park, garden
    amenity?: string;    // Restaurant, hospital
    road?: string;       // Street name
    city?: string;       // City name
    country?: string;    // Country name
    // ... more fields
  };
}
```

### Configuration

**Cache Settings** (in `geocodingCache.ts`):
```typescript
const geocodingCache = new GeocodingCache(
  100,              // maxSize: 100 entries
  isDevelopment     // enableLogging: true in dev mode
);
```

**Debounce Delay** (in `useReverseGeocode.ts`):
```typescript
const DEBOUNCE_DELAY_MS = 1000; // 1 second
```

**Coordinate Precision** (in `geocodingCache.ts`):
```typescript
const PRECISION_DECIMALS = 3; // ~111m at equator
```

## Recent Changes
- 010-reverse-geocoding: Added TypeScript 5 (frontend), Python 3.12 (backend - no changes) + react-leaflet 4.x, Leaflet.js 1.9.x, lodash.debounce 4.x (NEW), axios 1.x
- 009-gps-coordinates: Added Python 3.12 (backend), TypeScript 5 (frontend) + FastAPI, SQLAlchemy 2.0, Pydantic (backend), React 18, react-leaflet, Leaflet.js (frontend)

- 008-travel-diary-frontend: Added full CRUD UI for trips with photos, multi-step wizard, and owner controls

**Last updated**: 2026-01-11
