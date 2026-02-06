# Testing Documentation - ContraVento

Comprehensive testing strategies, guides, and best practices for ContraVento.

**Audience**: Developers, QA engineers, test automation engineers

---

## Testing Strategy

ContraVento follows a **Test-Driven Development (TDD)** approach with comprehensive test coverage across all layers.

### Test Pyramid

```
        ┌─────────────┐
        │     E2E     │  ← Few (Playwright)
        │  (Slow)     │
        ├─────────────┤
        │ Integration │  ← Some (pytest + FastAPI TestClient)
        │  (Medium)   │
        ├─────────────┤
        │    Unit     │  ← Many (pytest + Vitest)
        │   (Fast)    │
        └─────────────┘
```

**Coverage Requirement**: ≥90% for all modules

---

## Quick Navigation

| I want to... | Go to |
|--------------|-------|
| 🧪 Write unit tests (backend) | [Backend Unit Tests](backend/unit-tests.md) |
| 🔗 Write integration tests | [Backend Integration Tests](backend/integration-tests.md) |
| ⚛️ Test React components | [Frontend Unit Tests](frontend/unit-tests.md) |
| 🌐 Write E2E tests | [Frontend E2E Tests](frontend/e2e-tests.md) |
| ♿ Test accessibility | [Accessibility Testing](frontend/accessibility.md) |
| 📝 Manual QA workflows | [Manual QA](manual-qa/) |
| 🤖 CI/CD testing | [GitHub Actions](ci-cd/github-actions.md) |

---

## Backend Testing

### Documentation

- **[Unit Tests](backend/unit-tests.md)** - Testing business logic, services, utilities
- **[Integration Tests](backend/integration-tests.md)** - API endpoints, database operations
- **[Contract Tests](backend/contract-tests.md)** - OpenAPI schema validation
- **[Performance Tests](backend/performance-tests.md)** - Load testing, benchmarks
- **[Fixtures](backend/fixtures.md)** - Test data, factories, mocks

### Quick Example

```python
# tests/unit/test_auth_service.py
async def test_register_user(db_session):
    """Test user registration creates user and sends verification email."""
    # Arrange
    user_data = {"email": "test@example.com", "password": "SecurePass123!"}

    # Act
    result = await AuthService.register(db_session, user_data)

    # Assert
    assert result.email == user_data["email"]
    assert result.is_verified is False
```

### Run Tests

```bash
cd backend

# All tests
poetry run pytest

# With coverage (required ≥90%)
poetry run pytest --cov=src --cov-report=html

# Specific test type
poetry run pytest tests/unit/ -v
poetry run pytest tests/integration/ -v
```

**Documentation Status**: ⏳ To be migrated in Phase 3 (Week 3)

---

## Frontend Testing

### Documentation

- **[Unit Tests](frontend/unit-tests.md)** - Component tests with Vitest
- **[E2E Tests](frontend/e2e-tests.md)** - End-to-end tests with Playwright
- **[Accessibility Tests](frontend/accessibility.md)** - WCAG 2.1 AA compliance

### Quick Example

```typescript
// tests/unit/TripCard.test.tsx
import { render, screen } from '@testing-library/react';
import { TripCard } from '@/components/trips/TripCard';

test('displays trip title and distance', () => {
  const trip = { title: 'My Trip', distance_km: 50.5 };

  render(<TripCard trip={trip} />);

  expect(screen.getByText('My Trip')).toBeInTheDocument();
  expect(screen.getByText('50.5 km')).toBeInTheDocument();
});
```

### Run Tests

```bash
cd frontend

# Unit tests (Vitest)
npm run test

# E2E tests (Playwright)
npm run test:e2e

# Accessibility (axe)
npm run test:a11y
```

**Documentation Status**: ⏳ To be migrated in Phase 3 (Week 3)

---

## Manual QA

### Documentation

- **[Trips Testing](manual-qa/trips-testing.md)** - Manual trip creation, editing, deletion
- **[GPS Testing](manual-qa/gps-testing.md)** - GPX upload, maps, elevation profiles
- **[Social Testing](manual-qa/social-testing.md)** - Follow, comments, likes
- **[Accessibility Testing](manual-qa/accessibility-testing.md)** - Screen reader, keyboard navigation

**Documentation Status**: ⏳ To be consolidated in Phase 3 (Week 3)

**Source**:
- specs/003-gps-routes/MANUAL_TESTING.md
- specs/004-social-network/MANUAL_TESTING_GUIDE.md (+ 13 more files)
- specs/008-travel-diary-frontend/TESTING_GUIDE.md
- frontend/TESTING_GUIDE.md

---

## CI/CD Testing

### Documentation

- **[GitHub Actions](ci-cd/github-actions.md)** - CI/CD pipeline configuration
- **[Quality Gates](ci-cd/quality-gates.md)** - Coverage, linting, type checking requirements

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Backend Tests
  run: poetry run pytest --cov=src --cov-fail-under=90

- name: Frontend Tests
  run: npm run test && npm run test:e2e
```

**Quality Gates**:
- ✅ Test coverage ≥90%
- ✅ All linters pass (black, ruff, ESLint)
- ✅ Type checking passes (mypy, TypeScript)
- ✅ No security vulnerabilities

**Documentation Status**: ⏳ To be created in Phase 3 (Week 3)

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
| `backend/docs/TESTING_GUIDE.md` (22,511 lines!) | `docs/testing/backend/integration-tests.md` | ⏳ Phase 3 |
| `frontend/TESTING_GUIDE.md` (1,966 lines) | `docs/testing/frontend/e2e-tests.md` | ⏳ Phase 3 |
| `specs/004-social-network/TESTING_*.md` (14 files) | `docs/testing/manual-qa/social-testing.md` | ⏳ Phase 3 |
| `specs/008-travel-diary-frontend/TESTING_GUIDE.md` | `docs/testing/manual-qa/trips-testing.md` | ⏳ Phase 3 |
| `specs/013-public-trips-feed/E2E_TESTING_GUIDE.md` | Consolidate into `frontend/e2e-tests.md` | ⏳ Phase 3 |

Migration will occur in **Phase 3** (Week 3) - HIGH PRIORITY

---

## Related Documentation

- **[Architecture](../architecture/README.md)** - System design and patterns
- **[Development](../development/README.md)** - Developer workflows
- **[API Reference](../api/README.md)** - API testing guides

---

**Last Updated**: 2026-02-06
**Consolidation Plan**: Phase 1 (Foundation) - Directory structure
