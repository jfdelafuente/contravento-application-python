# Getting Started - ContraVento Development

Complete onboarding guide for new developers to set up ContraVento from zero to coding in 10-15 minutes.

**Audience**: New developers, contributors

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Verify Installation](#verify-installation)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Python** | 3.12+ | Backend runtime | [python.org](https://www.python.org/downloads/) |
| **Poetry** | 1.7+ | Python dependency management | `pip install poetry` |
| **Node.js** | 20+ | Frontend runtime | [nodejs.org](https://nodejs.org/) |
| **npm** | 10+ | Frontend package manager | Included with Node.js |
| **Git** | 2.x | Version control | [git-scm.com](https://git-scm.com/) |

### Optional Tools (for Docker modes)

| Tool | Purpose | When Needed |
|------|---------|-------------|
| **Docker** | Container runtime | local-minimal, local-full modes |
| **Docker Compose** | Multi-container orchestration | local-minimal, local-full modes |

**Note**: For daily development, Docker is **not required**. Use `local-dev` mode (SQLite) for instant startup.

---

## Quick Start

**Fastest path to coding** (5 minutes):

```bash
# 1. Clone repository
git clone https://github.com/yourusername/contravento-application-python.git
cd contravento-application-python

# 2. Setup and start backend (one command)
./run-local-dev.sh --setup

# Backend now running at http://localhost:8000
# API docs at http://localhost:8000/docs

# 3. In another terminal, start frontend
cd frontend
npm install
npm run dev

# Frontend now running at http://localhost:5173
```

**Default credentials** (auto-created):
- **Admin**: `admin` / `AdminPass123!`
- **User**: `testuser` / `TestPass123!`

**You're ready to code!** 🎉

---

## Detailed Setup

### Step 1: Clone Repository

```bash
# Via HTTPS
git clone https://github.com/yourusername/contravento-application-python.git

# Via SSH (if configured)
git clone git@github.com:yourusername/contravento-application-python.git

cd contravento-application-python
```

---

### Step 2: Backend Setup

#### Install Python Dependencies

```bash
cd backend

# Install Poetry (if not installed)
pip install poetry

# Install dependencies
poetry install

# Verify installation
poetry run python --version
# Expected: Python 3.12.x
```

#### Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env with your SECRET_KEY
nano .env
```

**Minimal `.env` configuration**:
```bash
# Backend
SECRET_KEY=your-generated-secret-key-here
DEBUG=true
ENVIRONMENT=local-dev

# Database (SQLite - no config needed)
DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db

# Email (MailHog for local testing - optional)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USE_TLS=false
```

#### Setup Database

**Option 1: Automatic setup** (recommended):
```bash
./run-local-dev.sh --setup
```

This automatically:
- Creates SQLite database
- Applies all migrations
- Creates admin user (admin / AdminPass123!)
- Creates test users
- Seeds sample data

**Option 2: Manual setup**:
```bash
# Apply migrations
poetry run alembic upgrade head

# Create admin user
poetry run python scripts/user-mgmt/create_admin.py

# Create test user
poetry run python scripts/user-mgmt/create_verified_user.py
```

---

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will start at**: http://localhost:5173

**Backend must be running** at http://localhost:8000 for API calls.

---

### Step 4: Verify Installation

#### Backend Health Check

```bash
# API health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "database": "connected"}

# API documentation (browser)
open http://localhost:8000/docs
```

#### Frontend Health Check

**Browser**: Open http://localhost:5173

**Expected**:
- Login page loads
- Can login with `testuser` / `TestPass123!`
- Dashboard displays

#### Run Tests

```bash
# Backend tests
cd backend
poetry run pytest

# Expected: All tests pass (100+ tests)

# Frontend tests (if configured)
cd frontend
npm test
```

---

## Development Workflow

### Daily Workflow

```bash
# Terminal 1: Backend
./run-local-dev.sh

# Terminal 2: Frontend
cd frontend
npm run dev

# Code, test, commit!
```

### Making Changes

**Follow TDD** (Test-Driven Development):

1. **Write test first** (Red)
   ```bash
   cd backend
   poetry run pytest tests/unit/test_my_feature.py
   # Test fails (expected)
   ```

2. **Write implementation** (Green)
   ```python
   # src/services/my_service.py
   def my_new_feature():
       return "implemented"
   ```

3. **Verify test passes** (Green)
   ```bash
   poetry run pytest tests/unit/test_my_feature.py
   # Test passes ✅
   ```

4. **Refactor** (keep tests passing)
   ```bash
   poetry run pytest --cov=src --cov-fail-under=90
   # Coverage ≥90% ✅
   ```

See **[TDD Workflow](tdd-workflow.md)** for detailed process.

---

### Code Quality Checks

**Before committing**:

```bash
cd backend

# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/

# Run tests with coverage
poetry run pytest --cov=src --cov-fail-under=90
```

See **[Code Quality](code-quality.md)** for standards and automation.

---

## Project Structure

```
contravento-application-python/
├── backend/                    # FastAPI backend
│   ├── src/                   # Source code
│   │   ├── api/              # API routes
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   ├── tests/                # Tests (unit, integration, contract)
│   ├── migrations/           # Alembic migrations
│   ├── scripts/              # Utility scripts
│   └── pyproject.toml        # Poetry configuration
├── frontend/                  # React frontend
│   ├── src/                  # Source code
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── pages/            # Page components
│   │   ├── services/         # API clients
│   │   └── utils/            # Utilities
│   ├── public/               # Static assets
│   └── package.json          # npm configuration
├── docs/                      # Documentation
│   ├── deployment/           # Deployment guides
│   ├── architecture/         # Technical design
│   ├── api/                  # API reference
│   ├── testing/              # Testing guides
│   ├── user-guides/          # End-user docs
│   ├── features/             # Feature deep-dives
│   └── development/          # Developer workflows (you are here)
├── specs/                     # Feature specifications
├── config/                    # Configuration files
├── storage/                   # Local file storage (gitignored)
├── run-local-dev.sh          # Quick start script (Linux/Mac)
├── run-local-dev.ps1         # Quick start script (Windows)
└── README.md                  # Project README
```

---

## Environment Modes

ContraVento supports multiple development modes:

| Mode | Database | Docker | Startup | Use When |
|------|----------|--------|---------|----------|
| **local-dev** | SQLite | ❌ No | ~2s | Daily development (recommended) |
| **local-minimal** | PostgreSQL | ✅ Yes | ~10s | PostgreSQL testing |
| **local-full** | PostgreSQL | ✅ Yes | ~20s | Email/cache testing |

**Recommendation**: Use `local-dev` (SQLite) for 95% of development. Only switch to Docker modes when testing PostgreSQL-specific features.

See **[Deployment Documentation](../deployment/README.md)** for complete mode details.

---

## Common Tasks

### Create a New Migration

```bash
cd backend
poetry run alembic revision --autogenerate -m "Add new field to User"

# Review generated migration in migrations/versions/
# Edit if needed
# Apply migration
poetry run alembic upgrade head
```

### Create Test Users

```bash
cd backend

# Create verified user
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username johndoe \
  --email john@example.com \
  --password "SecurePass123!"

# Promote to admin
poetry run python scripts/user-mgmt/promote_to_admin.py --username johndoe
```

### Reset Database

```bash
# Reset local-dev database (SQLite)
./run-local-dev.sh --reset

# This will:
# - Delete contravento_dev.db
# - Re-run migrations
# - Re-seed admin and test users
```

### View Logs

```bash
# Backend logs (if running via script)
tail -f logs/backend.log

# Frontend logs (in terminal where npm run dev is running)
# Logs appear in real-time
```

---

## Next Steps

### Learn the Codebase

1. **[Architecture Documentation](../architecture/README.md)** - Understand system design
2. **[API Reference](../api/README.md)** - Learn API endpoints
3. **[Features Documentation](../features/README.md)** - Explore implemented features

### Explore Key Features

1. **Travel Diary**: `specs/002-travel-diary/spec.md`
2. **GPS Routes**: `specs/003-gps-routes/spec.md`
3. **Social Network**: `specs/004-social-network/spec.md`

### Contribute

1. Pick an issue from GitHub Issues
2. Follow [TDD Workflow](tdd-workflow.md)
3. Ensure [Code Quality](code-quality.md) checks pass
4. Submit Pull Request

---

## Troubleshooting

### Port 8000 Already in Use

**Error**: `Address already in use: 8000`

**Solution**:
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

### Database Connection Error

**Error**: `FOREIGN KEY constraint failed`

**Cause**: SQLite foreign keys not enabled (shouldn't happen with our setup)

**Solution**:
```bash
# Reset database
./run-local-dev.sh --reset
```

---

### Poetry Install Fails

**Error**: `Unable to find installation candidates for package`

**Solution**:
```bash
cd backend

# Clear cache
poetry cache clear pypi --all

# Reinstall
poetry install
```

---

### Frontend Proxy Error

**Error**: `ECONNREFUSED 127.0.0.1:8000`

**Cause**: Backend not running

**Solution**:
```bash
# Start backend first
./run-local-dev.sh

# Then start frontend
cd frontend
npm run dev
```

---

### Test Coverage Below 90%

**Error**: `FAIL Required test coverage of 90% not reached`

**Solution**:
```bash
# View coverage report
poetry run pytest --cov=src --cov-report=html

# Open htmlcov/index.html to see uncovered lines
# Write tests for uncovered code
```

See **[Troubleshooting](troubleshooting/)** for more solutions.

---

## Additional Resources

### Documentation

- **[TDD Workflow](tdd-workflow.md)** - Test-first development process
- **[Code Quality](code-quality.md)** - Linting, formatting, type checking
- **[Deployment Modes](../deployment/README.md)** - All environment modes
- **[Testing Strategies](../testing/README.md)** - Testing guide

### External Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **React**: https://react.dev/
- **Poetry**: https://python-poetry.org/docs/

---

## Getting Help

### Check Documentation First

1. **[Troubleshooting](troubleshooting/)** - Common issues
2. **[Deployment Docs](../deployment/README.md)** - Environment setup
3. **[Architecture Docs](../architecture/README.md)** - System design

### Ask for Help

- **GitHub Issues**: Report bugs or ask questions
- **Pull Request Comments**: Code-specific questions
- **Team Chat**: Real-time help (if available)

---

**Last Updated**: 2026-02-07
**Estimated Setup Time**: 10-15 minutes
**Status**: ✅ Complete
