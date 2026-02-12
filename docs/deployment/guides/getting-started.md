# Getting Started with ContraVento

**Your first steps with ContraVento deployment**

**Reading Time**: 5-10 minutes

**Goal**: Get your development environment running in <10 minutes

---

## Overview

This guide helps you:

1. **Choose** the right deployment mode for your needs
2. **Set up** your first development environment
3. **Verify** everything works correctly
4. **Know** where to go next

---

## Quick Start by Role

**Choose your path based on your role:**

| I am a... | Start with... | Why? |
|-----------|---------------|------|
| **New Developer** 🆕 | [local-dev](../modes/local-dev.md) | Instant startup, zero config, focus on code |
| **Backend Developer** 💻 | [local-dev](../modes/local-dev.md) | SQLite is perfect for backend work |
| **Frontend Developer** 🎨 | [local-dev](../modes/local-dev.md) + `--with-frontend` | Full stack with hot reload |
| **Full-Stack Developer** 🔧 | [local-minimal](../modes/local-minimal.md) | PostgreSQL + backend + frontend |
| **DevOps Engineer** 🚀 | [dev](../modes/dev.md) or [staging](../modes/staging.md) | Server deployment modes |
| **QA Tester** 🧪 | [test](../modes/test.md) | Automated testing environment |

**Still not sure?** → See [Decision Tree](#decision-tree) below

---

## Decision Tree

### 5 Questions to Find Your Perfect Mode

**Question 1**: Do you have Docker installed?

```
┌─────────────────────────────────────────┐
│ Q1: Do you have Docker installed?      │
└─────────────────────────────────────────┘
         │
         ├─ NO ──► Use local-dev (SQLite)
         │         ✅ No Docker needed
         │         ✅ Instant startup
         │         → [Jump to Setup](#option-1-local-dev-fastest-)
         │
         └─ YES ──► Continue to Q2 ↓
```

**Question 2**: What do you need to test?

```
┌─────────────────────────────────────────┐
│ Q2: What are you working on?           │
└─────────────────────────────────────────┘
         │
         ├─ Backend features (trips, profiles, stats)
         │  ──► local-dev (SQLite)
         │      ✅ Fastest option
         │      → [Jump to Setup](#option-1-local-dev-fastest-)
         │
         ├─ PostgreSQL-specific features (UUIDs, arrays)
         │  ──► local-minimal (Docker + PostgreSQL)
         │      → [Jump to Setup](#option-2-local-minimal-postgresql)
         │
         ├─ Email/auth features (registration, password reset)
         │  ──► local-full (Docker + MailHog + pgAdmin)
         │      → [Jump to Setup](#option-3-local-full-complete-stack)
         │
         └─ Continue to Q3 ↓
```

**Question 3**: Are you testing production builds?

```
┌─────────────────────────────────────────┐
│ Q3: Testing production builds?         │
└─────────────────────────────────────────┘
         │
         ├─ YES ──► local-prod (Docker + Nginx + optimized build)
         │          → [See local-prod guide](../modes/local-prod.md)
         │
         └─ NO ──► Continue to Q4 ↓
```

**Question 4**: Are you deploying to a server?

```
┌─────────────────────────────────────────┐
│ Q4: Deploying to server?               │
└─────────────────────────────────────────┘
         │
         ├─ Development/Integration server
         │  ──► dev mode
         │      → [See dev guide](../modes/dev.md)
         │
         ├─ Staging (production mirror)
         │  ──► staging mode
         │      → [See staging guide](../modes/staging.md)
         │
         ├─ Production (live users)
         │  ──► prod mode
         │      → [See prod guide](../modes/prod.md)
         │
         └─ Continue to Q5 ↓
```

**Question 5**: Are you doing CI/CD or automated testing?

```
┌─────────────────────────────────────────┐
│ Q5: CI/CD or automated testing?        │
└─────────────────────────────────────────┘
         │
         ├─ Jenkins/GitHub Actions
         │  ──► preproduction mode
         │      → [See preproduction guide](../modes/preproduction.md)
         │
         └─ Automated test suite
            ──► test mode
                → [See test guide](../modes/test.md)
```

---

## First-Time Setup

### Prerequisites Check

Before starting, verify you have these installed:

#### Required for ALL Modes

**Git**:
```bash
git --version  # Should show 2.x or higher
```

#### Required for local-dev (No Docker)

**Python 3.12+**:
```bash
python --version  # Must show 3.12 or higher
```

**Poetry**:
```bash
poetry --version

# If not installed:
pip install poetry
# Or with pipx (recommended):
pipx install poetry
```

**Node.js 18+** (only if using frontend):
```bash
node --version  # Must show v18.x or higher
npm --version   # Must show 9.x or higher
```

#### Required for Docker Modes

**Docker**:
```bash
docker --version         # Should show 20.x or higher
docker-compose --version # Should show 2.x or higher
```

If Docker is not running:
- **Windows/Mac**: Start Docker Desktop
- **Linux**: `sudo systemctl start docker`

---

### Option 1: local-dev (Fastest) ⚡

**Best for**: Most developers, daily work, quick prototyping

**Estimated setup time**: 2-3 minutes

#### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/contravento-application-python.git
cd contravento-application-python
```

#### Step 2: Run Setup

**Linux/Mac**:
```bash
./run-local-dev.sh --setup
```

**Windows PowerShell**:
```powershell
.\run-local-dev.ps1 -Setup
```

**What setup does**:
- ✅ Creates `.env` file with database configuration
- ✅ Installs Python dependencies (~1 minute)
- ✅ Creates SQLite database with migrations
- ✅ Creates admin user and test users
- ✅ Seeds initial data (achievements, cycling types)

#### Step 3: Start Development Server

**Linux/Mac**:
```bash
./run-local-dev.sh
```

**Windows PowerShell**:
```powershell
.\run-local-dev.ps1
```

**Expected output**:
```
✅ Starting backend at http://localhost:8000
ℹ️  API Docs: http://localhost:8000/docs
ℹ️  Press Ctrl+C to stop
```

#### Step 4: Verify Backend Works

Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see the Swagger UI with all available endpoints.

#### Step 5: (Optional) Start Frontend

**Linux/Mac**:
```bash
./run-local-dev.sh --with-frontend
```

**Windows PowerShell**:
```powershell
.\run-local-dev.ps1 -WithFrontend
```

**Expected output**:
```
✅ Backend running at http://localhost:8000
✅ Frontend running at http://localhost:5173
ℹ️  Press Ctrl+C to stop both servers
```

Open browser: http://localhost:5173

**→ Continue to [Verification](#verification-steps) below**

---

### Option 2: local-minimal (PostgreSQL)

**Best for**: Testing PostgreSQL features, pre-staging validation

**Estimated setup time**: 30-60 seconds

#### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/contravento-application-python.git
cd contravento-application-python
```

#### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.local-minimal.example .env.local-minimal

# Edit if needed (default values usually work)
nano .env.local-minimal
```

#### Step 3: Start Services

```bash
./deploy.sh local-minimal
```

**Expected output**:
```
Creating network "contravento_local-minimal" ... done
Creating contravento-db-local ... done
Creating contravento-backend-local ... done

✓ All services started successfully!

Access:
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
```

#### Step 4: Verify Services

```bash
docker-compose ps
```

**Expected output**:
```
NAME                       STATUS          PORTS
contravento-db-local       Up (healthy)    5432/tcp
contravento-backend-local  Up (healthy)    0.0.0.0:8000->8000/tcp
```

**→ Continue to [Verification](#verification-steps) below**

---

### Option 3: local-full (Complete Stack)

**Best for**: Testing emails, caching, full integration

**Estimated setup time**: 60-90 seconds

#### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/contravento-application-python.git
cd contravento-application-python
```

#### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.local.example .env.local

# Edit with your settings (passwords, secrets)
nano .env.local
```

**Required variables**:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `POSTGRES_PASSWORD` - Set your PostgreSQL password
- `REDIS_PASSWORD` - Set your Redis password
- `PGADMIN_PASSWORD` - Set your pgAdmin password

#### Step 3: Start All Services

```bash
./deploy.sh local
```

**Expected output**:
```
Creating network "contravento_local" ... done
Creating contravento-db-local ... done
Creating contravento-redis-local ... done
Creating contravento-backend-local ... done
Creating contravento-mailhog-local ... done
Creating contravento-pgadmin-local ... done

✓ All services started successfully!

Access:
- Backend: http://localhost:8000
- MailHog: http://localhost:8025
- pgAdmin: http://localhost:5050
```

#### Step 4: Verify All Services

```bash
docker-compose ps
```

**Expected output**:
```
NAME                       STATUS          PORTS
contravento-db-local       Up (healthy)    5432/tcp
contravento-redis-local    Up (healthy)    6379/tcp
contravento-backend-local  Up (healthy)    0.0.0.0:8000->8000/tcp
contravento-mailhog-local  Up              0.0.0.0:8025->8025/tcp
contravento-pgadmin-local  Up              0.0.0.0:5050->80/tcp
```

**→ Continue to [Verification](#verification-steps) below**

---

## Verification Steps

### 1. Backend Health Check

**Visit**: http://localhost:8000/health

**Expected response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-06T10:00:00Z"
}
```

✅ If you see this → Backend is working!

❌ If you see error → See [Troubleshooting](troubleshooting.md#backend-wont-start)

### 2. API Documentation

**Visit**: http://localhost:8000/docs

**Expected**:
- Swagger UI loads
- You see endpoints organized by tags (auth, trips, profiles, etc.)
- You can expand endpoints and see request/response schemas

✅ If you see Swagger UI → API is working!

### 3. Test API Login

**Using Swagger UI** (http://localhost:8000/docs):

1. Expand **POST /auth/login** endpoint
2. Click "Try it out"
3. Use default credentials:
   ```json
   {
     "username": "admin",
     "password": "AdminPass123!"
   }
   ```
4. Click "Execute"

**Expected response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

✅ If you get tokens → Authentication is working!

❌ If you get 401 error → See [Troubleshooting](troubleshooting.md#login-fails)

### 4. (Optional) Test Frontend

**If using `--with-frontend` flag**:

1. **Visit**: http://localhost:5173
2. You should see ContraVento login page
3. Try logging in with:
   - **Username**: `admin`
   - **Password**: `AdminPass123!`

**Expected behavior**:
- Login form works
- No console errors (press F12 → Console tab)
- Redirects to dashboard after login

✅ If login works → Frontend is connected to backend!

❌ If login fails → Check browser console for errors

### 5. Database Verification

**For local-dev (SQLite)**:
```bash
# Check database file exists
ls -lh backend/contravento_dev.db

# Should show file size >100 KB (with seeded data)
```

**For Docker modes (PostgreSQL)**:
```bash
# Connect to database
docker exec -it contravento-db-local psql -U contravento -d contravento

# List tables
\dt

# Check users exist
SELECT username, email, is_verified FROM users;

# Expected: admin, testuser, maria_garcia

# Exit
\q
```

✅ If you see test users → Database is seeded correctly!

---

## Next Steps

### 1. Explore the Codebase

**Key directories**:
```
contravento-application-python/
├── backend/
│   ├── src/
│   │   ├── api/          # FastAPI routers (REST endpoints)
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic schemas (validation)
│   │   ├── services/     # Business logic layer
│   │   └── utils/        # Shared utilities
│   ├── tests/            # Pytest unit/integration tests
│   └── migrations/       # Alembic database migrations
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── pages/        # Page components
│   │   └── services/     # API client services
│   └── tests/            # Frontend tests
└── docs/                 # Documentation (you are here!)
```

### 2. Read Project Documentation

**Essential reading** (in order):

1. **[CLAUDE.md](../../../CLAUDE.md)** (30 min) - Development guidelines, architecture, testing patterns
2. **[README.md](../../../README.md)** (10 min) - Project overview, features
3. **[CONTRIBUTING.md](../../../CONTRIBUTING.md)** (15 min) - How to contribute, code style, PR process

**Deployment-specific**:
- **[Deployment Modes Comparison](../README.md#deployment-modes-comparison)** - Which mode for what
- **[Troubleshooting Guide](troubleshooting.md)** - Common problems and solutions
- **[Environment Variables Guide](environment-variables.md)** - Configuration reference

### 3. Run Tests

**Backend tests** (pytest):
```bash
cd backend

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/unit/test_auth_service.py -v
```

**Expected**: All tests pass, coverage ≥90%

**Frontend tests** (Vitest):
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### 4. Make Your First Change

**Try this simple exercise**:

1. **Backend**: Add a new endpoint
   ```bash
   # File: backend/src/api/health.py
   # Add a new endpoint that returns the current server time
   ```

2. **Test it**: http://localhost:8000/health/time

3. **Frontend**: Display the server time on the health check page

4. **Commit**: Follow commit message format in [CONTRIBUTING.md](../../../CONTRIBUTING.md)

### 5. Join the Team

**Development workflow**:
1. Read active features in [NEXT_STEPS.md](../../../NEXT_STEPS.md)
2. Pick a task from current sprint
3. Create feature branch: `git checkout -b feature-name`
4. Make changes following TDD (test first!)
5. Run quality checks: `poetry run black src/ tests/ && poetry run ruff check src/ tests/ && poetry run mypy src/`
6. Submit PR with tests and documentation

---

## Common Issues

**If you encounter problems during setup**, see the detailed [Troubleshooting Guide](troubleshooting.md).

**Quick fixes for common issues**:

| Problem | Quick Fix |
|---------|-----------|
| Port 8000 already in use | Kill existing process or change port in `.env` |
| Port 5173 already in use | Kill existing process: `lsof -ti:5173 \| xargs kill -9` |
| Docker daemon not running | Start Docker Desktop (Windows/Mac) or `sudo systemctl start docker` (Linux) |
| Database migration errors | Reset database: `rm backend/contravento_dev.db && ./run-local-dev.sh --setup` |
| `poetry install` fails | Update Poetry: `pip install --upgrade poetry` |
| npm install fails | Clear cache: `rm -rf node_modules package-lock.json && npm install` |

**Still stuck?**
- Check [Troubleshooting Guide](troubleshooting.md)
- Ask in team chat
- Open an issue on GitHub

---

## Environment Comparison

### Quick Reference: Which Mode When?

| Mode | Startup | Docker | DB | Email UI | Best For |
|------|---------|--------|----|---------||----------|
| **local-dev** | ⚡ <30s | ❌ | SQLite | ❌ | Daily development, learning |
| **local-minimal** | ~30s | ✅ | PostgreSQL | ❌ | PostgreSQL testing |
| **local-full** | ~60s | ✅ | PostgreSQL | ✅ | Email/auth testing |
| **local-prod** | ~60s | ✅ | PostgreSQL | ❌ | Production build testing |
| **dev** | ~90s | ✅ | PostgreSQL | ❌ | Integration server |
| **staging** | ~90s | ✅ | PostgreSQL | ❌ | Pre-production testing |
| **prod** | ~120s | ✅ | PostgreSQL | ❌ | Live production |
| **preproduction** | ~90s | ✅ | PostgreSQL | ❌ | CI/CD pipelines |
| **test** | ~30s | ✅ | In-memory | ❌ | Automated tests |

---

## See Also

- **[Deployment Modes](../README.md#deployment-modes)** - Detailed comparison of all 9 modes
- **[Troubleshooting](troubleshooting.md)** - Solutions to common problems
- **[Environment Variables](environment-variables.md)** - Configuration reference
- **[Docker Compose Guide](docker-compose-guide.md)** - Understanding the Docker stack
- **[Frontend Deployment](frontend-deployment.md)** - Frontend-specific deployment

---

**Last Updated**: 2026-02-06

**Feedback**: Found an error or have a suggestion? [Open an issue](https://github.com/your-org/contravento-application-python/issues)
