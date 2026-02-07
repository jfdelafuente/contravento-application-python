# GitHub Actions CI/CD Pipeline

Automated testing and deployment pipeline configuration.

**Source**: `.github/workflows/ci.yml` and related workflow files

---

## Table of Contents

- [Overview](#overview)
- [Pipeline Structure](#pipeline-structure)
- [Job Definitions](#job-definitions)
- [Quality Gates](#quality-gates)
- [Test Execution](#test-execution)
- [Deployment Stages](#deployment-stages)
- [Configuration](#configuration)

---

## Overview

ContraVento uses GitHub Actions for continuous integration and deployment with the following features:

- ✅ **Path-Based Triggering** - Only runs tests for changed files
- ✅ **Parallel Execution** - Backend and frontend tested concurrently
- ✅ **Quality Checks** - Linting, formatting, type checking
- ✅ **Test Coverage** - Unit, integration, E2E tests with code coverage
- ✅ **Security Scanning** - Trivy vulnerability scanner + Safety checks
- ✅ **Automated Deployment** - Staging (develop branch), Production (main branch)

**Workflow File**: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

---

## Pipeline Structure

```
┌─────────────────┐
│  Pull Request   │
│   or Push to    │
│  main/develop   │
└────────┬────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         v                                         v
  ┌─────────────┐                          ┌─────────────┐
  │  Changes    │                          │  Security   │
  │  Detection  │                          │  Scanning   │
  └──────┬──────┘                          └─────────────┘
         │
         ├──────────────┬─────────────────┐
         │              │                 │
         v              v                 v
  ┌─────────────┐ ┌──────────────┐ ┌────────────┐
  │  Backend    │ │  Frontend    │ │   Docs     │
  │  Quality    │ │  Quality     │ │  Changed   │
  └──────┬──────┘ └──────┬───────┘ └────────────┘
         │              │
         v              v
  ┌─────────────┐ ┌──────────────┐
  │  Backend    │ │  Frontend    │
  │  Tests      │ │  Tests       │
  └──────┬──────┘ └──────┬───────┘
         │              │
         └──────┬───────┘
                │
                v
         ┌─────────────┐
         │  E2E Tests  │ ⚠️ Currently disabled
         └──────┬──────┘
                │
                v
         ┌────────────────┐
         │  Build & Validate │
         └──────┬──────┘
                │
                ├──────────────┬────────────────┐
                │              │                │
                v              v                v
         ┌───────────┐  ┌───────────┐  ┌──────────────┐
         │  Staging  │  │Production │  │   Artifact   │
         │  (develop)│  │  (main)   │  │   Storage    │
         └───────────┘  └───────────┘  └──────────────┘
```

---

## Job Definitions

### 1. changes (Detect Changes)

**Purpose**: Optimize pipeline by only running relevant jobs based on file changes

**Triggers**: PR or push to main/develop

**Path Filters**:
- `backend`: `backend/**`, `scripts/**`, backend workflow files
- `frontend`: `frontend/**`, frontend workflow files
- `docs`: `**.md`, `docs/**`

**Outputs**:
- `backend`: "true" if backend files changed
- `frontend`: "true" if frontend files changed
- `docs`: "true" if documentation changed

**Example**:
```yaml
# Only runs if backend code changed
if: needs.changes.outputs.backend == 'true'
```

---

### 2. backend-quality (Backend Quality Checks)

**Purpose**: Enforce code quality standards for Python code

**Dependencies**: `changes` job

**Runs when**: Backend files changed

**Steps**:
1. **Setup**:
   - Checkout code
   - Install Python 3.12
   - Install Poetry
   - Install dependencies (`poetry install`)

2. **Quality Checks**:
   ```bash
   # Code formatting (black)
   poetry run black --check src/ tests/

   # Linting (ruff)
   poetry run ruff check src/ tests/

   # Type checking (mypy)
   poetry run mypy src/
   ```

**Success Criteria**:
- Zero formatting violations
- Zero linting errors
- Zero type errors

---

### 3. frontend-quality (Frontend Quality Checks)

**Purpose**: Enforce code quality standards for TypeScript/React code

**Dependencies**: `changes` job

**Runs when**: Frontend files changed

**Steps**:
1. **Setup**:
   - Checkout code
   - Install Node.js 20
   - Install dependencies (`npm ci`)

2. **Quality Checks**:
   ```bash
   # ESLint
   npm run lint

   # TypeScript type checking
   npm run type-check
   ```

**Success Criteria**:
- Zero ESLint errors
- Zero TypeScript type errors

---

### 4. backend-tests (Backend Tests)

**Purpose**: Run backend unit and integration tests with PostgreSQL

**Dependencies**: `backend-quality` (must pass first)

**Services**:
- **PostgreSQL 16**:
  - Port: 5432
  - User: contravento_test
  - Database: contravento_test_db
  - Health checks every 10s

**Environment Variables**:
```yaml
DATABASE_URL: postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test_db
SECRET_KEY: ${{ secrets.SECRET_KEY }}
APP_ENV: testing
```

**Test Execution**:
```bash
poetry run pytest \
  --cov=src \
  --cov-report=xml \
  --cov-report=term \
  --junitxml=test-results/pytest.xml \
  -v
```

**Outputs**:
- **Coverage Report**: Uploaded to Codecov
- **Test Results**: Published as GitHub check
- **JUnit XML**: Stored for reporting

**Success Criteria**:
- All tests pass
- Coverage ≥90% (enforced separately)

---

### 5. frontend-tests (Frontend Tests)

**Purpose**: Run frontend unit tests (Vitest)

**Dependencies**: `frontend-quality` (must pass first)

**Test Execution**:
```bash
npm run test:unit -- --coverage
```

**Outputs**:
- **Coverage Report**: Uploaded to Codecov
- **Test Results**: Stored in `coverage/`

**Success Criteria**:
- All tests pass
- Coverage ≥80% (recommended)

---

### 6. e2e-tests (End-to-End Tests)

**Purpose**: Run full-stack integration tests with Playwright

**Dependencies**: `backend-tests`, `frontend-tests` (must both pass)

**Status**: ⚠️ **Currently Disabled** (72.7% pass rate - 24/33 tests)

**Why Disabled**:
- P28: Logout redirect failure
- P29: Duplicate username banner issue
- **Reactivation criteria**: Coverage >80% (27/33 tests passing)

**Services**:
- **PostgreSQL 16**:
  - Port: 5432
  - User: contravento
  - Database: contravento_db

**Steps**:
1. **Setup**:
   - Install Python 3.12 + Poetry
   - Install Node.js 20
   - Install backend dependencies
   - Run migrations (`alembic upgrade head`)

2. **Start Servers**:
   ```bash
   # Backend (port 8000)
   poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 &

   # Frontend (port 5173)
   npm run dev &
   ```

3. **Wait for Readiness**:
   - Backend: `curl http://localhost:8000/health`
   - Frontend: `curl http://localhost:5173`
   - Timeout: 90 seconds each
   - Extra stabilization: 5 seconds

4. **Run Tests**:
   ```bash
   npx playwright test
   ```

5. **Cleanup**:
   - Stop backend and frontend servers
   - Upload Playwright report as artifact

**Browsers**:
- Chromium
- Firefox
- WebKit

**Timeout**: 20 minutes max

---

### 7. security-scan (Security Scanning)

**Purpose**: Detect vulnerabilities in dependencies and code

**Runs on**: Every PR/push (always runs)

**Scanners**:

1. **Trivy** (Filesystem Scan):
   - Scans all files in repository
   - Checks for:
     - Known vulnerabilities in dependencies
     - Misconfigurations
     - Secrets in code
   - Output: SARIF format → GitHub Security tab

2. **Safety** (Python Dependencies):
   - Checks `requirements.txt` for known vulnerabilities
   - Uses Safety DB (Python security advisories)
   - Warnings allowed (not blocking)

**Reports**:
- GitHub Security → Code scanning alerts
- Pull request annotations

---

### 8. build-and-validate (Production Build)

**Purpose**: Build and validate production frontend bundle

**Dependencies**: `backend-tests`, `frontend-tests`

**Runs when**: Push to `main` branch only

**Steps**:

1. **Build Production**:
   ```bash
   npm run build:prod
   ```

2. **Validate Build**:
   ```bash
   # Check dist/ directory exists
   [ -d dist ] || exit 1

   # Check index.html exists
   [ -f dist/index.html ] || exit 1

   # Measure bundle size
   SIZE=$(du -sb dist | awk '{print $1}')

   # Warn if >5MB
   if [ $SIZE -gt 5242880 ]; then
     echo "::warning::Build exceeds 5MB"
   fi
   ```

3. **Upload Artifact**:
   - Name: `production-build`
   - Path: `frontend/dist/`
   - Retention: 30 days (GitHub default)

**Success Criteria**:
- Build completes without errors
- `dist/index.html` exists
- Size <5MB (warning if exceeded)

---

### 9. deploy-staging (Deploy to Staging)

**Purpose**: Automated deployment to staging environment

**Dependencies**: `build-and-validate`

**Triggers**:
- Push to `develop` branch only
- Manual dispatch

**Environment**:
- Name: `staging`
- URL: `https://staging.contravento.com`

**Steps**:
```bash
echo "🚀 Deploying to staging environment..."
# TODO: Add actual deployment commands
# e.g., docker-compose, kubectl, terraform
```

**Status**: 🚧 Placeholder (actual deployment commands to be added)

---

### 10. deploy-production (Deploy to Production)

**Purpose**: Automated deployment to production environment

**Dependencies**: `build-and-validate`

**Triggers**:
- Push to `main` branch only
- Manual dispatch

**Environment**:
- Name: `production`
- URL: `https://contravento.com`
- **Manual approval required** (GitHub environment protection rule)

**Steps**:
```bash
echo "🚀 Deploying to production environment..."
# TODO: Add actual deployment commands
# Requires manual approval in GitHub environments settings
```

**Status**: 🚧 Placeholder (actual deployment commands to be added)

---

## Quality Gates

### Code Quality

| Check | Tool | Backend | Frontend | Blocking |
|-------|------|---------|----------|----------|
| **Formatting** | black | ✅ Required | N/A | Yes |
| **Linting** | ruff | ✅ Required | N/A | Yes |
| **Linting** | ESLint | N/A | ✅ Required | Yes |
| **Type Check** | mypy | ✅ Required | N/A | Yes |
| **Type Check** | tsc | N/A | ✅ Required | Yes |

### Test Coverage

| Test Type | Tool | Target Coverage | Blocking |
|-----------|------|-----------------|----------|
| **Backend Unit** | pytest | ≥90% | Recommended |
| **Backend Integration** | pytest | ≥90% | Recommended |
| **Frontend Unit** | Vitest | ≥80% | Recommended |
| **E2E** | Playwright | ≥80% pass rate | Currently disabled |

### Security

| Check | Tool | Blocking |
|-------|------|----------|
| **Vulnerability Scan** | Trivy | No (alerts only) |
| **Python Dependencies** | Safety | No (warnings allowed) |

---

## Test Execution

### Backend Tests

**Command**:
```bash
poetry run pytest --cov=src --cov-report=xml --cov-report=term -v
```

**Includes**:
- Unit tests (`tests/unit/`)
- Integration tests (`tests/integration/`)
- Contract tests (`tests/contract/`)

**Database**: PostgreSQL 16 (service container)

**Reports**:
- Coverage: XML → Codecov
- Results: JUnit XML → GitHub checks

---

### Frontend Tests

**Command**:
```bash
npm run test:unit -- --coverage
```

**Includes**:
- Component tests (Vitest + @testing-library/react)
- Utility function tests

**Reports**:
- Coverage: JSON → Codecov
- Results: Console output

---

### E2E Tests (Disabled)

**Command**:
```bash
npx playwright test
```

**Browsers**:
- Chromium, Firefox, WebKit (parallel execution)

**Reports**:
- HTML report → Artifact upload
- Screenshots on failure
- Video recordings (if configured)

---

## Deployment Stages

### Staging (develop branch)

**Trigger**: Push to `develop`

**Environment**: `https://staging.contravento.com`

**Approval**: Automatic (no manual approval)

**Purpose**:
- Pre-production testing
- Integration validation
- Demo environment

---

### Production (main branch)

**Trigger**: Push to `main`

**Environment**: `https://contravento.com`

**Approval**: **Manual approval required**

**Protection Rules**:
- Reviewers: Require 1 approval
- Wait timer: Optional
- Deployment branches: `main` only

**Purpose**:
- Live production environment
- Requires manual QA sign-off

---

## Configuration

### Required Secrets

Configure in **GitHub Settings → Secrets and variables → Actions**:

| Secret | Description | Used By |
|--------|-------------|---------|
| `SECRET_KEY` | JWT secret (32+ chars) | Backend tests, E2E |
| `DOCKERHUB_USERNAME` | Docker Hub username | Docker build workflow |
| `DOCKERHUB_TOKEN` | Docker Hub access token | Docker build workflow |

**Generate SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### Environment Variables

**Backend Tests**:
```yaml
DATABASE_URL: postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test_db
SECRET_KEY: ${{ secrets.SECRET_KEY }}
APP_ENV: testing
```

**E2E Tests**:
```yaml
VITE_APP_URL: http://localhost:5173
VITE_API_URL: http://localhost:8000
DATABASE_URL: postgresql+asyncpg://contravento:contraventopass@localhost:5432/contravento_db
SECRET_KEY: ${{ secrets.SECRET_KEY }}
APP_ENV: testing
```

---

### Path Filters

**Backend**:
- `backend/**`
- `scripts/**`
- `.github/workflows/backend-tests.yml`
- `.github/workflows/ci.yml`

**Frontend**:
- `frontend/**`
- `.github/workflows/frontend-tests.yml`
- `.github/workflows/ci.yml`

**Docs**:
- `**.md`
- `docs/**`

---

## Workflow Optimization

### Caching

**Poetry** (Python dependencies):
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'  # Caches ~/.cache/pip
```

**npm** (Node.js dependencies):
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json
```

**Benefits**:
- Faster dependency installation (30-60s → 5-10s)
- Reduced network usage
- More reliable builds

---

### Parallelization

**Concurrent Jobs**:
- `backend-quality` and `frontend-quality` run in parallel
- `backend-tests` and `frontend-tests` run in parallel (after quality checks)

**Savings**:
- Sequential: ~15 minutes
- Parallel: ~8 minutes
- **Improvement**: ~47% faster

---

## Troubleshooting

### Common Issues

#### ❌ Backend Tests Fail: "connection refused"

**Cause**: PostgreSQL service not ready

**Solution**: Verify health checks are passing
```yaml
options: >-
  --health-cmd pg_isready
  --health-interval 10s
  --health-timeout 5s
  --health-retries 5
```

---

#### ❌ E2E Tests Timeout

**Cause**: Servers not starting in time

**Solution**: Increase wait time or check server logs
```bash
timeout 90 bash -c 'until curl -f http://localhost:8000/health 2>/dev/null; do sleep 2; done'
```

---

#### ❌ Coverage Upload Fails

**Cause**: Missing Codecov token (for private repos)

**Solution**: Add `CODECOV_TOKEN` secret (not required for public repos)

---

#### ❌ Build Size Warning

**Cause**: Production build exceeds 5MB

**Solution**:
- Check for large dependencies
- Verify source maps disabled in production
- Use bundle analyzer: `npm run build -- --analyze`

---

## Monitoring

### GitHub Actions UI

**View workflow runs**:
1. Repository → Actions tab
2. Select workflow: "CI/CD Pipeline"
3. Click on specific run for details

**Check logs**:
- Each job has expandable step logs
- Download logs for offline analysis
- View failed test details

---

### Codecov Integration

**View coverage reports**:
1. Go to: `https://codecov.io/gh/{org}/{repo}`
2. View per-file coverage
3. Track coverage trends over time

**Pull Request Comments**:
- Codecov bot adds coverage comment to PRs
- Shows coverage diff (new vs old)

---

## Related Documentation

- **[Quality Gates](quality-gates.md)** - Coverage and linting requirements
- **[Backend Tests](../backend/integration-tests.md)** - Backend testing guide
- **[Frontend Tests](../frontend/e2e-tests.md)** - Frontend testing guide
- **[Manual Testing](../manual-qa/)** - Manual QA procedures

---

**Last Updated**: 2026-02-07
**Workflow Version**: CI/CD Pipeline v1.0
**Status**: Active (E2E disabled temporarily)
