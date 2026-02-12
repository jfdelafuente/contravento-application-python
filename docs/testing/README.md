# Testing Documentation - ContraVento

Comprehensive testing strategies, guides, and best practices for ContraVento.

**Audience**: Developers, QA engineers, test automation engineers

---

## Testing Strategy

ContraVento follows a **Test-Driven Development (TDD)** approach with comprehensive test coverage across all layers.

### Test Pyramid

```
                 ┌──────────────┐
                 │  Manual QA   │  ← Exploratory (Human verification)
                 ├──────────────┤
                 │     E2E      │  ← Few (Playwright - 24/33 passing)
                 │   (Slow)     │     Critical user journeys
                 ├──────────────┤
                 │ Integration  │  ← Some (pytest + FastAPI TestClient)
                 │  (Medium)    │     API + Database interaction
                 ├──────────────┤
                 │     Unit     │  ← Many (pytest + Vitest)
                 │    (Fast)    │     Business logic, pure functions
                 └──────────────┘
```

**Testing Principles**:
1. **Write tests FIRST** (TDD) before implementation
2. **Test behavior**, not implementation details
3. **One assertion** per test (when possible)
4. **Fail fast** with clear error messages
5. **Isolated tests** - no dependencies between tests

**Coverage Requirements**:
- Backend: ≥90% (enforced)
- Frontend: ≥80% (recommended)
- E2E: ≥80% pass rate (24/33 = 72.7% - currently disabled)

---

## Quick Navigation

| I want to... | Go to |
|--------------|-------|
| 🧪 Write backend integration tests | [Backend Integration Tests](backend/integration-tests.md) |
| ⚙️ Configure test fixtures | [Backend Fixtures](backend/fixtures.md) |
| ⚛️ Write frontend E2E tests | [Frontend E2E Tests](frontend/e2e-tests.md) |
| ♿ Test accessibility (WCAG 2.1 AA) | [Accessibility Testing](frontend/accessibility.md) |
| 📝 Manual test trips/photos | [Trips Testing](manual-qa/trips-testing.md) |
| 🗺️ Manual test GPS/GPX features | [GPS Testing](manual-qa/gps-testing.md) |
| 👥 Manual test social features | [Social Testing](manual-qa/social-testing.md) |
| 🤖 Configure CI/CD pipeline | [GitHub Actions](ci-cd/github-actions.md) |
| 📊 Check quality gates | [Quality Gates](ci-cd/quality-gates.md) |

---

## Backend Testing

### Documentation

- **[Integration Tests](backend/integration-tests.md)** ✅ - API endpoints, database operations, contract tests
- **[Fixtures](backend/fixtures.md)** ✅ - Test configuration, pytest fixtures, test data factories

### Test Organization

```
backend/tests/
├── unit/              # Business logic tests (services, utils)
├── integration/       # API endpoint tests (routes, database)
├── contract/          # OpenAPI schema validation
└── conftest.py        # Shared fixtures (db_session, client, auth_headers)
```

### Quick Example

```python
# tests/integration/test_trip_api.py
async def test_create_trip_workflow(client, db_session, auth_headers):
    """Test complete trip creation → publish → edit flow"""
    # 1. Create draft trip
    response = await client.post("/trips", json={
        "title": "Test Trip",
        "description": "A" * 60,  # Min 50 chars for publish
        "start_date": "2024-06-01",
    }, headers=auth_headers)

    assert response.status_code == 201
    trip_id = response.json()["data"]["trip_id"]

    # 2. Publish trip
    response = await client.post(f"/trips/{trip_id}/publish", headers=auth_headers)
    assert response.json()["data"]["status"] == "published"

    # 3. Edit trip (optimistic locking)
    response = await client.put(f"/trips/{trip_id}", json={...}, headers=auth_headers)
    assert response.status_code == 200
```

### Run Tests

```bash
cd backend

# All tests
poetry run pytest

# With coverage (required ≥90%)
poetry run pytest --cov=src --cov-report=html --cov-report=term

# By test type
poetry run pytest tests/unit/ -v              # Unit tests only
poetry run pytest tests/integration/ -v       # Integration tests only
poetry run pytest tests/contract/ -v          # Contract tests only

# By feature
poetry run pytest tests/unit/test_auth_service.py -v
poetry run pytest tests/integration/test_trip_api.py -v
```

### Key Testing Patterns

**1. Database Fixtures**:
- `db_session`: Fresh SQLite in-memory DB per test
- Automatic rollback after each test
- Isolated test data (no cross-test pollution)

**2. Authentication**:
- `test_user`: Pre-created verified user
- `auth_headers`: Bearer token for protected endpoints
- `create_test_user()`: Factory for additional users

**3. Contract Tests**:
- Validate API responses against OpenAPI schemas
- 116 contract tests covering all endpoints
- Auto-generated from `docs/api/contracts/*.yaml`

**Documentation Status**: ✅ Complete (Phase 3)

---

## Frontend Testing

### Documentation

- **[E2E Tests](frontend/e2e-tests.md)** ✅ - Playwright tests for critical user journeys
- **[Accessibility Tests](frontend/accessibility.md)** ✅ - WCAG 2.1 AA compliance with axe-core

### Test Organization

```
frontend/
├── tests/
│   ├── e2e/               # Playwright E2E tests
│   │   ├── trips.spec.ts
│   │   ├── auth.spec.ts
│   │   └── social.spec.ts
│   └── unit/              # Vitest component tests
│       ├── TripCard.test.tsx
│       └── LocationConfirmModal.test.tsx
└── playwright.config.ts
```

### Quick Example - E2E Test

```typescript
// tests/e2e/trips.spec.ts
import { test, expect } from '@playwright/test';

test('should create trip with GPS coordinates', async ({ page }) => {
  await page.goto('http://localhost:5173/trips/new');

  // Fill basic info
  await page.fill('input[name="title"]', 'GPS Test Trip');
  await page.fill('textarea[name="description"]', 'Testing GPS coordinates functionality.');

  // Add location with coordinates
  await page.click('button:has-text("Añadir Ubicación")');
  await page.fill('input[name="locations[0].name"]', 'Madrid');
  await page.fill('input[name="locations[0].latitude"]', '40.416775');
  await page.fill('input[name="locations[0].longitude"]', '-3.703790');

  // Submit
  await page.click('button:has-text("Siguiente")');

  // Verify coordinates display
  await expect(page.locator('text=40.416775°, -3.703790°')).toBeVisible();
});
```

### Quick Example - Accessibility Test

```typescript
// tests/unit/LocationConfirmModal.test.tsx
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import { LocationConfirmModal } from '@/components/trips/LocationConfirmModal';

test('should have no accessibility violations', async () => {
  const { container } = render(
    <LocationConfirmModal
      location={{ name: 'Madrid', latitude: 40.416775, longitude: -3.703790 }}
      onConfirm={() => {}}
      onCancel={() => {}}
    />
  );

  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Run Tests

```bash
cd frontend

# E2E tests (Playwright) - all browsers
npx playwright test

# E2E tests - specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# E2E tests - headed mode (see browser)
npx playwright test --headed

# E2E tests - debug mode
npx playwright test --debug

# Unit tests (Vitest)
npm run test:unit

# With coverage
npm run test:unit -- --coverage
```

### Key Testing Patterns

**1. Page Object Model** (E2E):
- Encapsulate page interactions in reusable functions
- Example: `loginAs(page, username, password)`

**2. Test Fixtures** (E2E):
- `test.beforeEach()` for setup (login, create test data)
- `test.afterEach()` for cleanup

**3. Accessibility Testing**:
- Automated: axe-core integration
- Manual: Screen reader testing with NVDA/VoiceOver
- Keyboard navigation: Tab, Enter, Esc

**4. Visual Regression** (optional):
- Playwright screenshot comparison
- Detect unexpected UI changes

**Documentation Status**: ✅ Complete (Phase 3)

---

## Manual QA

### Documentation

- **[Trips Testing](manual-qa/trips-testing.md)** ✅ - Trip creation, editing, publish, delete, gallery, maps
- **[GPS Testing](manual-qa/gps-testing.md)** ✅ - GPX upload, download, map visualization, cascade deletion
- **[Social Testing](manual-qa/social-testing.md)** ✅ - Follow/unfollow, comments, likes, public feed

### Testing Workflows

#### Trips Management
- **Create & Publish**: Draft → validation → publish workflow
- **Photo Gallery**: Upload (max 20), reorder, delete, lightbox
- **Trip Actions**: Edit (optimistic locking), delete (cascade), owner-only permissions
- **Filters**: Search text, tags, status (draft/published)

#### GPS & Routes
- **GPX Upload**: Small files (<1MB sync), large files (>1MB error), validation
- **GPX Download**: Original file download (owner-only), filename = trip title
- **Map Visualization**: Interactive map, red polyline, start/end markers, auto-fit bounds

#### Social Features
- **Follow/Unfollow**: Follow button, confirmation modal, following list, pagination
- **Comments**: Add comment, delete own comment, validation (max 1000 chars), disabled on drafts
- **Likes**: Like/unlike trips, counter updates, like from feed
- **Public Feed**: View all published trips, filter by tag, pagination, sort by recent/popular

### Test Environment Setup

**Prerequisites**:
```bash
# Backend (LOCAL-DEV mode)
cd backend
./run-local-dev.sh --setup    # First time only
./run-local-dev.sh            # Start server

# Frontend
cd frontend
npm run dev
```

**Test Credentials** (auto-created during setup):
- Admin: `admin` / `AdminPass123!`
- User 1: `testuser` / `TestPass123!`
- User 2: `maria_garcia` / `SecurePass456!`

**Documentation Status**: ✅ Complete (Phase 3)

---

## CI/CD Testing

### Documentation

- **[GitHub Actions](ci-cd/github-actions.md)** ✅ - Complete CI/CD pipeline configuration
- **[Quality Gates](ci-cd/quality-gates.md)** ✅ - Coverage, linting, type checking, security scanning

### Pipeline Stages

```
┌─────────────┐
│   Changes   │  Path-based triggering (backend/frontend/docs)
│  Detection  │
└──────┬──────┘
       ├──────────────┬─────────────────┐
       v              v                 v
┌────────────┐ ┌──────────────┐ ┌────────────┐
│  Backend   │ │  Frontend    │ │  Security  │
│  Quality   │ │  Quality     │ │  Scanning  │
└──────┬─────┘ └──────┬───────┘ └────────────┘
       │              │
       v              v
┌────────────┐ ┌──────────────┐
│  Backend   │ │  Frontend    │
│  Tests     │ │  Tests       │
└──────┬─────┘ └──────┬───────┘
       └──────┬───────┘
              v
       ┌─────────────┐
       │  E2E Tests  │  ⚠️ Disabled (72.7% pass rate)
       └──────┬──────┘
              v
       ┌────────────────┐
       │  Build & Deploy │
       └────────────────┘
```

### Quality Gates

**Code Quality** (blocking):
- ✅ Formatting: black (backend), Prettier (frontend)
- ✅ Linting: ruff (backend), ESLint (frontend)
- ✅ Type Checking: mypy (backend), tsc (frontend)

**Test Coverage** (recommended):
- ✅ Backend: ≥90% (enforced)
- ✅ Frontend: ≥80% (recommended)
- ⚠️ E2E: ≥80% pass rate (currently 72.7%, disabled)

**Security** (non-blocking alerts):
- ✅ Trivy vulnerability scanner (filesystem scan)
- ✅ Safety (Python dependencies)
- ✅ GitHub Security tab integration

### Running Quality Checks Locally

**Backend**:
```bash
cd backend

# All quality checks
poetry run black src/ tests/
poetry run ruff check src/ tests/
poetry run mypy src/
poetry run pytest --cov=src --cov-report=term
```

**Frontend**:
```bash
cd frontend

# All quality checks
npm run lint
npm run type-check
npm run test:unit -- --coverage
```

**Documentation Status**: ✅ Complete (Phase 3)

---

## Test Data & Fixtures

### Backend Fixtures

```python
# tests/conftest.py
@pytest.fixture
async def db_session():
    """Fresh SQLite in-memory database per test."""
    ...

@pytest.fixture
def auth_headers(test_user):
    """Pre-authenticated user headers for protected endpoints."""
    ...
```

See [Backend Fixtures](backend/fixtures.md) for complete documentation.

### Frontend Test Data

```typescript
// tests/fixtures/trips.ts
export const mockTrip: Trip = {
  trip_id: 'uuid-123',
  title: 'Test Trip',
  distance_km: 50.5,
  ...
};
```

---

## Migration from Old Documentation

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `backend/docs/TESTING_GUIDE.md` (22,511 lines) | `docs/testing/backend/integration-tests.md` | ✅ Migrated |
| `backend/docs/TESTING_CONFIGURATION.md` | `docs/testing/backend/fixtures.md` | ✅ Migrated |
| `frontend/TESTING_GUIDE.md` (1,966 lines) | `docs/testing/frontend/e2e-tests.md` | ✅ Migrated |
| Accessibility section (frontend/TESTING_GUIDE.md) | `docs/testing/frontend/accessibility.md` | ✅ Extracted |
| `specs/004-social-network/TESTING_*.md` (10+ files) | `docs/testing/manual-qa/social-testing.md` | ✅ Consolidated |
| `specs/008-travel-diary-frontend/TESTING_GUIDE.md` | `docs/testing/manual-qa/trips-testing.md` | ✅ Consolidated |
| `specs/003-gps-routes/MANUAL_TESTING.md` | `docs/testing/manual-qa/gps-testing.md` | ✅ Consolidated |
| `.github/workflows/*.yml` (4 workflows) | `docs/testing/ci-cd/github-actions.md` | ✅ Documented |
| Quality standards (scattered) | `docs/testing/ci-cd/quality-gates.md` | ✅ Consolidated |

**Consolidation Strategy**: Intelligent consolidation - created concise, well-structured guides with cross-references to original documentation for deep dives.

**Phase 3 Results**:
- **Files Created**: 9 comprehensive testing documents
- **Lines Consolidated**: 22K + 1.9K + 1K+ lines → ~3.5K lines of focused documentation
- **Reduction**: ~85% reduction in total lines while preserving essential content
- **Improvement**: Clear navigation, consistent structure, no duplication

---

## Testing Metrics

### Current Coverage

| Component | Coverage | Target | Status |
|-----------|----------|--------|--------|
| Backend (src/) | ~95% | ≥90% | ✅ Exceeds |
| Frontend (unit) | ~75% | ≥80% | 🚧 In progress |
| E2E (Playwright) | 72.7% (24/33) | ≥80% | ⚠️ Below target |

### Test Counts

| Test Type | Count | Execution Time |
|-----------|-------|----------------|
| Backend Unit | ~150 tests | ~5s |
| Backend Integration | ~200 tests | ~15s |
| Backend Contract | 116 tests | ~8s |
| Frontend Unit | ~50 tests | ~3s |
| E2E (Playwright) | 33 tests | ~5 min |

**Total**: ~549 automated tests

---

## Related Documentation

- **[API Reference](../api/README.md)** - API endpoint documentation and testing
- **[Architecture](../architecture/README.md)** - System design and patterns
- **[Development](../development/README.md)** - Developer workflows
- **[Deployment](../deployment/README.md)** - Deployment modes and testing

---

**Last Updated**: 2026-02-07
**Consolidation Plan**: ✅ Phase 3 Complete (Testing Consolidation)
**Total Documents**: 9 files (backend: 2, frontend: 2, manual-qa: 3, ci-cd: 2)
