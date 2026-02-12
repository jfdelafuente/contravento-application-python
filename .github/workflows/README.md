# CI/CD Pipeline Documentation

GitHub Actions workflows for automated testing, quality checks, and deployment of ContraVento application.

## Workflows Overview

### 1. **ci.yml** - Main CI/CD Pipeline

**Triggers**:
- Pull requests to `main` or `develop`
- Pushes to `main` or `develop`
- Manual dispatch

**Jobs**:

1. **changes** - Detects which parts of codebase changed
   - Outputs: `backend`, `frontend`, `docs`
   - Uses: `dorny/paths-filter@v3`

2. **backend-quality** - Code quality checks
   - Black formatting check
   - Ruff linting
   - MyPy type checking
   - Runs only if backend files changed

3. **frontend-quality** - Code quality checks
   - ESLint linting
   - TypeScript type checking
   - Runs only if frontend files changed

4. **backend-tests** - Backend test suite
   - Unit + integration tests
   - Coverage threshold: ≥90%
   - PostgreSQL service container
   - Uploads coverage to Codecov
   - Publishes test results

5. **frontend-tests** - Frontend test suite
   - Vitest unit tests
   - Coverage reporting
   - Uploads coverage to Codecov

6. **e2e-tests** - End-to-end tests
   - Playwright across 3 browsers
   - Full stack (backend + frontend + database)
   - Runs only if backend or frontend changed
   - Timeout: 20 minutes
   - Uploads HTML report

7. **security-scan** - Security vulnerability scanning
   - Trivy filesystem scan
   - Python dependency check (safety)
   - Uploads results to GitHub Security

8. **build-and-validate** - Production build
   - Builds frontend for production
   - Validates bundle size (warns if > 5MB)
   - Uploads build artifacts
   - Runs only on `main` branch

9. **deploy-staging** - Staging deployment
   - Deploys on push to `develop`
   - Environment: `staging`
   - URL: https://staging.contravento.com

10. **deploy-production** - Production deployment
    - Deploys on push to `main`
    - Environment: `production`
    - URL: https://contravento.com
    - Requires manual approval

### 2. **backend-tests.yml** - Backend Test Suite

**Triggers**:
- PR/push to `main` or `develop` (backend files only)
- Manual dispatch

**Jobs**:

1. **lint-and-format**
   - Black, Ruff, MyPy checks
   - Python 3.12

2. **unit-tests**
   - Runs unit tests with coverage
   - Matrix: Python 3.12 (can expand)
   - Uploads coverage to Codecov

3. **integration-tests**
   - PostgreSQL service container
   - Integration tests with coverage
   - Uploads coverage to Codecov

4. **smoke-tests**
   - Runs smoke tests (local-minimal mode)
   - Starts backend server
   - Tests critical endpoints

5. **coverage-check**
   - Enforces ≥90% coverage threshold
   - Fails if coverage below threshold

### 3. **frontend-tests.yml** - Frontend Test Suite

**Triggers**:
- PR/push to `main` or `develop` (frontend files only)
- Manual dispatch

**Jobs**:

1. **lint-and-type-check**
   - ESLint + TypeScript
   - Node.js 20

2. **unit-tests**
   - Vitest with coverage
   - Uploads coverage report

3. **build**
   - Matrix: `staging` and `production`
   - Tests both build configs
   - Checks bundle size
   - Uploads build artifacts

4. **e2e-tests**
   - Playwright E2E tests
   - Full stack setup
   - Uploads HTML report

5. **accessibility-tests**
   - axe-core accessibility checks
   - Uploads a11y report

## Workflow Triggers

```yaml
# On pull request
on:
  pull_request:
    branches: [main, develop]

# On push to branch
on:
  push:
    branches: [main, develop]

# Only when specific paths change
on:
  pull_request:
    paths:
      - 'backend/**'
      - 'frontend/**'

# Manual trigger
on:
  workflow_dispatch:
```

## Environment Variables

### Global
```yaml
PYTHON_VERSION: '3.12'
NODE_VERSION: '20'
```

### Backend Tests
```yaml
DATABASE_URL: postgresql+asyncpg://user:pass@localhost:5432/db
SECRET_KEY: test_secret_key_***
ENVIRONMENT: test
CORS_ORIGINS: http://localhost:5173
```

### Frontend Tests
```yaml
VITE_APP_URL: http://localhost:5173
VITE_API_URL: http://localhost:8000
```

## Service Containers

### PostgreSQL for Testing
```yaml
services:
  postgres:
    image: postgres:16-alpine
    env:
      POSTGRES_USER: contravento_test
      POSTGRES_PASSWORD: test_password
      POSTGRES_DB: contravento_test_db
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

## Artifacts

### Test Results
- **Retention**: 7 days
- **Uploads**:
  - `unit-test-results-*` - Backend unit test JUnit XML
  - `integration-test-results` - Backend integration test JUnit XML
  - `frontend-unit-test-results` - Frontend unit test results
  - `e2e-test-results` - Playwright test results

### Coverage Reports
- **Retention**: 7 days
- **Uploads**:
  - `coverage-report-unit-*` - Backend unit coverage HTML
  - `coverage-report-integration` - Backend integration coverage HTML
  - `frontend-coverage-report` - Frontend coverage HTML

### Build Artifacts
- **Retention**: 7 days
- **Uploads**:
  - `build-staging` - Staging build (with source maps)
  - `build-production` - Production build (optimized)
  - `production-build` - Final production artifacts

### Playwright Reports
- **Retention**: 7 days
- **Uploads**:
  - `playwright-report` - HTML report with screenshots/videos

## Coverage Enforcement

### Backend
- **Threshold**: ≥90%
- **Check**: `coverage-check` job in `backend-tests.yml`
- **Failure**: Build fails if coverage < 90%

```bash
poetry run pytest --cov=src --cov-fail-under=90
```

### Frontend
- **Threshold**: Not enforced yet (recommended ≥80%)
- **Future**: Add coverage threshold to `frontend-tests.yml`

## Security Scanning

### Trivy
- **Scan Type**: Filesystem
- **Output**: SARIF format
- **Upload**: GitHub Security tab
- **Frequency**: Every push

### Python Dependencies
- **Tool**: `safety`
- **Check**: CVEs in dependencies
- **Failure**: Warning only (doesn't fail build)

## Deployment Environments

### Staging
- **Branch**: `develop`
- **URL**: https://staging.contravento.com
- **Approval**: Not required
- **Database**: Staging PostgreSQL
- **Monitoring**: Enabled

### Production
- **Branch**: `main`
- **URL**: https://contravento.com
- **Approval**: **Required** (manual approval in GitHub)
- **Database**: Production PostgreSQL
- **Monitoring**: Enabled
- **Alerts**: Configured

## GitHub Environments Setup

Configure environments in repository settings:

1. **Settings → Environments → New environment**

2. **Staging Environment**:
   - Name: `staging`
   - Protection rules: None
   - Secrets:
     - `STAGING_DATABASE_URL`
     - `STAGING_SECRET_KEY`
     - `STAGING_DEPLOY_KEY`

3. **Production Environment**:
   - Name: `production`
   - Protection rules:
     - ✅ Required reviewers (1+ approvers)
     - ✅ Deployment branches: `main` only
   - Secrets:
     - `PRODUCTION_DATABASE_URL`
     - `PRODUCTION_SECRET_KEY`
     - `PRODUCTION_DEPLOY_KEY`

## Status Badges

Add to README.md:

```markdown
[![CI/CD Pipeline](https://github.com/jfdelafuente/contravento-application-python/actions/workflows/ci.yml/badge.svg)](https://github.com/jfdelafuente/contravento-application-python/actions/workflows/ci.yml)

[![Backend Tests](https://github.com/jfdelafuente/contravento-application-python/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/jfdelafuente/contravento-application-python/actions/workflows/backend-tests.yml)

[![Frontend Tests](https://github.com/jfdelafuente/contravento-application-python/actions/workflows/frontend-tests.yml/badge.svg)](https://github.com/jfdelafuente/contravento-application-python/actions/workflows/frontend-tests.yml)

[![codecov](https://codecov.io/gh/jfdelafuente/contravento-application-python/branch/main/graph/badge.svg)](https://codecov.io/gh/jfdelafuente/contravento-application-python)
```

## Troubleshooting

### Backend Tests Fail

**Issue**: Database connection errors
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**: Check PostgreSQL service health
```yaml
options: >-
  --health-cmd pg_isready
  --health-interval 10s
```

### Frontend Build Fails

**Issue**: Out of memory
```
FATAL ERROR: Reached heap limit
```

**Solution**: Increase Node.js memory
```yaml
- name: Build production
  run: NODE_OPTIONS="--max_old_space_size=4096" npm run build:prod
```

### E2E Tests Timeout

**Issue**: Servers don't start in time
```
Error: Timeout waiting for http://localhost:8000/health
```

**Solution**: Increase timeout in global-setup.ts
```typescript
const MAX_RETRIES = 60; // Increase from 30
```

### Playwright Tests Flaky

**Issue**: Intermittent failures
```
Error: Timeout 30000ms exceeded
```

**Solution**: Increase retries in playwright.config.ts
```typescript
retries: process.env.CI ? 3 : 0, // Increase from 2
```

### Coverage Below Threshold

**Issue**: Coverage check fails
```
❌ Coverage 88% is below required 90%
```

**Solution**: Add tests for uncovered code
```bash
# Find uncovered lines
poetry run coverage report --show-missing

# Generate HTML report
poetry run coverage html
open htmlcov/index.html
```

## Performance Optimization

### Caching
- **Python dependencies**: Cached via `setup-python@v5`
- **Node dependencies**: Cached via `setup-node@v4`
- **Playwright browsers**: Installed once per job

### Parallelization
- **Backend tests**: Can run in parallel (pytest-xdist)
- **Frontend tests**: Vitest runs in parallel by default
- **E2E tests**: Playwright runs 2 workers on CI

### Conditional Execution
- **Path filters**: Only run jobs when relevant files change
- **needs**: Jobs wait for dependencies
- **if conditions**: Skip jobs based on branch/event

## Manual Workflow Dispatch

Trigger workflows manually from GitHub UI:

1. Go to **Actions** tab
2. Select workflow (e.g., `ci.yml`)
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow**

Or via GitHub CLI:
```bash
gh workflow run ci.yml --ref develop
gh workflow run backend-tests.yml --ref main
```

## Monitoring & Alerts

### GitHub Actions
- **Email**: Workflow failures send email to committer
- **Slack**: Configure webhook in repository secrets
- **Discord**: Configure webhook for notifications

### Codecov
- **Coverage reports**: Automatic on every push
- **PR comments**: Coverage diff in PR comments
- **Alerts**: Email when coverage drops > 1%

## Cost Optimization

### Free Tier Limits (GitHub Actions)
- **Public repos**: Unlimited minutes
- **Private repos**: 2,000 minutes/month

### Tips to Reduce Usage
1. **Use path filters**: Only run necessary jobs
2. **Cache dependencies**: Faster builds, fewer minutes
3. **Matrix strategy**: Test only critical versions
4. **Conditional jobs**: Skip staging on `main` branch
5. **Self-hosted runners**: For private repos (optional)

## References

### Deployment Documentation

For detailed guides on all deployment modes (local, staging, production), see:

- **[Deployment Guide](../../docs/deployment/README.md)** - Complete deployment documentation with decision tree and mode-specific guides

### External Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
- [Playwright CI Documentation](https://playwright.dev/docs/ci)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
