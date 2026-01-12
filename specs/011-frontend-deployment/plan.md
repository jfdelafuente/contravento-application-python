# Implementation Plan: Frontend Deployment Integration

**Branch**: `011-frontend-deployment` | **Date**: 2026-01-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-frontend-deployment/spec.md`

## Summary

Integrate the React frontend (Vite-based) into all existing deployment environments (SQLite Local, Docker Minimal, Docker Full, staging, production) to enable full-stack development workflows. The frontend will run as a Vite dev server in local/docker dev environments, and as optimized static builds served by Nginx in staging/production.

**Primary Requirement**: Developers must be able to run frontend + backend together with a single command in any environment.

**Technical Approach**:
- Extend existing deployment scripts (`run-local-dev.sh`, `deploy.sh`) to orchestrate both frontend and backend services
- Add Docker service definitions for frontend Vite dev server in docker-compose files
- Configure Vite proxy for CORS-free local development
- Create npm scripts for production builds with environment-specific configuration
- Update QUICK_START.md with frontend-specific instructions

## Technical Context

**Language/Version**:
- **Backend**: Python 3.12 (already established)
- **Frontend**: TypeScript 5.2, Node.js 18+ (already established in Features 005, 008, 009, 010)

**Primary Dependencies**:
- **Frontend**: Vite 5.0.8, React 18.2, react-router-dom 6.21 (already in package.json)
- **Build**: npm (package manager), vite-plugin-react (already configured)
- **Deployment**: Docker Compose v2, Nginx (for production builds)

**Storage**:
- Frontend static assets served from `frontend/dist/` (production builds)
- No direct database access from frontend (API-only communication)

**Testing**:
- **Frontend**: Vitest (already configured), @testing-library/react (already in package.json)
- **Integration**: Manual QA following frontend/TESTING_GUIDE.md pattern
- **Deployment validation**: Smoke tests for each environment

**Target Platform**:
- **Development**: Windows/Linux/Mac (cross-platform scripts)
- **Docker environments**: Linux containers (Alpine/Debian base images)
- **Production**: Linux servers with Nginx

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- **Dev startup (SQLite Local)**: <30 seconds (frontend + backend)
- **Dev startup (Docker Minimal)**: <60 seconds (3 services: frontend, backend, PostgreSQL)
- **Build time**: <2 minutes for production build (npm run build)
- **HMR (Hot Module Replacement)**: <2 seconds for TypeScript/CSS changes

**Constraints**:
- **CORS**: Frontend must proxy API requests in development to avoid CORS issues
- **Ports**: Frontend uses 5173 (Vite default), backend uses 8000 (existing)
- **Environment variables**: VITE_* prefix required for all frontend env vars (Vite convention)
- **Docker volumes**: Frontend source code must be mounted for hot reload in Docker dev mode

**Scale/Scope**:
- **Scripts to update**: 4 files (`run-local-dev.sh`, `run-local-dev.ps1`, `deploy.sh`, `deploy.ps1`)
- **Docker Compose files**: 2 files (`docker-compose.local-minimal.yml`, `docker-compose.local.yml`)
- **Documentation updates**: 1 file (`QUICK_START.md`)
- **New frontend env config**: 3 files (`.env.development`, `.env.staging`, `.env.production`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **I. Code Quality & Maintainability**:
- Shell scripts will follow best practices (error handling, set -e, clear comments)
- Docker Compose files will use semantic naming and comments
- No code duplication (reuse existing script patterns from backend)

✅ **II. Testing Standards (TDD)**:
- Deployment scripts will be tested manually following new DEPLOYMENT_TESTING.md guide
- Smoke tests defined for each environment (frontend accessible, backend responsive, CORS working)
- No unit tests required for shell scripts (manual validation sufficient for infrastructure code)

✅ **III. User Experience Consistency**:
- All error messages in scripts will be in Spanish (consistent with backend)
- Clear success messages when services start ("Frontend disponible en http://localhost:5173")
- Consistent command structure across all deployment modes

✅ **IV. Performance Requirements**:
- Startup time requirements documented in spec (SC-001, SC-002)
- HMR performance monitored (SC-003)
- Production builds optimized with Vite (SC-004, SC-005)

✅ **Security & Data Protection**:
- Environment variables for API URLs and keys (no hardcoded values)
- CORS properly configured (only localhost in dev, specific domains in prod)
- No sensitive data in Docker images or version control

✅ **Development Workflow**:
- Feature branch `011-frontend-deployment` already created
- Changes will be documented in QUICK_START.md
- Pull request will include screenshots of all environments running

**GATE STATUS**: ✅ **PASSED** - No constitution violations. Ready for Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/011-frontend-deployment/
├── plan.md              # This file
├── research.md          # Phase 0 output (best practices, Docker patterns)
├── data-model.md        # N/A (no database changes for this feature)
├── quickstart.md        # Phase 1 output (step-by-step deployment guide)
├── contracts/           # N/A (no API changes)
└── tasks.md             # Phase 2 output (generated by /speckit.tasks)
```

### Source Code (repository root)

```text
# Option 2: Web application (frontend + backend) - SELECTED

backend/
├── src/                          # No changes needed
├── tests/                        # No changes needed
├── scripts/
│   ├── run-local-dev.sh          # UPDATE: Add frontend startup logic
│   └── run-local-dev.ps1         # UPDATE: Add frontend startup logic
└── docs/
    └── DEPLOYMENT.md             # UPDATE: Reference frontend instructions

frontend/
├── src/                          # No changes (already has components, pages)
├── tests/                        # No changes (Vitest already configured)
├── public/                       # No changes (static assets)
├── .env.development              # NEW: Vite env vars for local dev (VITE_API_URL=http://localhost:8000)
├── .env.staging                  # NEW: Vite env vars for staging
├── .env.production               # NEW: Vite env vars for production
├── vite.config.ts                # UPDATE: Add proxy configuration for /api/* → backend
├── package.json                  # UPDATE: Add build:staging, build:prod scripts
└── Dockerfile.dev                # NEW: Multi-stage Dockerfile for dev mode (Vite dev server)

# Root level
├── docker-compose.local-minimal.yml  # UPDATE: Add frontend service (Vite dev)
├── docker-compose.local.yml          # UPDATE: Add frontend service (Vite dev)
├── docker-compose.dev.yml            # UPDATE: Add frontend service (Vite dev with Nginx)
├── docker-compose.staging.yml        # UPDATE: Add frontend service (Nginx + static build)
├── docker-compose.prod.yml           # UPDATE: Add frontend service (Nginx + static build with HA)
├── deploy.sh                         # UPDATE: Add frontend build step for staging/prod
├── deploy.ps1                        # UPDATE: Add frontend build step for staging/prod
└── QUICK_START.md                    # UPDATE: Add frontend instructions for all environments
```

**Structure Decision**: Web application structure already exists. This feature extends deployment infrastructure to support frontend services alongside existing backend services. No source code changes in backend/ needed. All changes are in deployment scripts, Docker configs, and frontend build configuration.

## Complexity Tracking

> **This section is EMPTY because there are no constitution violations.**

No violations detected. All work aligns with existing infrastructure patterns.

---

## Phase 0: Research & Technical Decisions

**Goal**: Resolve all technical unknowns and establish best practices for frontend deployment.

### Research Tasks

1. **Vite Proxy Configuration Best Practices**
   - **Question**: How to configure Vite proxy to forward `/api/*` requests to backend without CORS issues?
   - **Research Focus**: Vite server.proxy options, rewritePath patterns, WebSocket support
   - **Expected Outcome**: Documented proxy configuration for vite.config.ts

2. **Docker Multi-Stage Builds for Frontend**
   - **Question**: Should we use multi-stage Dockerfile (dev vs prod) or separate Dockerfiles?
   - **Research Focus**: Docker best practices for Node.js apps, layer caching optimization
   - **Expected Outcome**: Decision on Dockerfile strategy with rationale

3. **Environment Variable Management in Vite**
   - **Question**: How to inject environment-specific variables (API URL, Turnstile key) into builds?
   - **Research Focus**: Vite .env file loading, VITE_ prefix convention, .env.mode files
   - **Expected Outcome**: Documented env var strategy for dev/staging/prod

4. **Nginx Configuration for SPA (Single Page Application)**
   - **Question**: How to configure Nginx to serve React SPA with client-side routing (react-router)?
   - **Research Focus**: try_files directive, 404 handling, cache headers for static assets
   - **Expected Outcome**: Nginx config template for production deployments

5. **Docker Compose Service Orchestration**
   - **Question**: How to ensure frontend waits for backend to be healthy before starting in Docker?
   - **Research Focus**: depends_on with healthchecks, wait-for-it.sh scripts
   - **Expected Outcome**: Documented healthcheck strategy

6. **Windows/Linux Script Compatibility**
   - **Question**: How to maintain parity between .sh and .ps1 scripts for cross-platform development?
   - **Research Focus**: Common patterns for error handling, process management, logging
   - **Expected Outcome**: Script template with cross-platform patterns

**Output**: `research.md` with all decisions documented and ready for Phase 1 implementation.

---

## Phase 1: Design & Implementation Artifacts

**Prerequisites**: `research.md` complete with all unknowns resolved.

### 1. Data Model (`data-model.md`)

**Status**: **N/A** - This feature has no database schema changes.

**Rationale**: Frontend deployment is purely infrastructure/deployment work. No new entities, tables, or migrations needed.

---

### 2. API Contracts (`/contracts/`)

**Status**: **N/A** - This feature has no API changes.

**Rationale**: Frontend uses existing backend APIs (auth, trips, profiles) without modification. No new endpoints or contract changes needed.

---

### 3. Quick Start Guide (`quickstart.md`)

**Status**: **REQUIRED** - Essential for developer onboarding.

**Content Structure**:

```markdown
# Quick Start: Frontend Deployment

## Prerequisites
- Node.js 18+ installed
- npm installed
- Backend running (see backend/docs/DEPLOYMENT.md)

## 1. SQLite Local (No Docker) - Recommended for Daily Development

### Initial Setup
\`\`\`bash
# Install frontend dependencies (first time only)
cd frontend
npm install

# Start backend + frontend together
cd ..
./run-local-dev.sh --with-frontend  # New flag

# Or start separately:
# Terminal 1: Backend
cd backend && poetry run uvicorn src.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
\`\`\`

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### How It Works
- Vite dev server runs on port 5173 with HMR enabled
- API requests to `/api/*` automatically proxy to backend (no CORS)
- Hot reload works for both frontend (Vite HMR) and backend (uvicorn --reload)

---

## 2. Docker Minimal (PostgreSQL + Backend + Frontend)

### Start All Services
\`\`\`bash
./deploy.sh local-minimal --with-frontend
\`\`\`

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### Docker Services Started
- `frontend-dev`: Vite dev server (with volumes for hot reload)
- `backend`: FastAPI server
- `db`: PostgreSQL 16

---

## 3. Docker Full (All Services + MailHog + pgAdmin)

### Start All Services
\`\`\`bash
./deploy.sh local --with-frontend
\`\`\`

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **MailHog UI**: http://localhost:8025
- **pgAdmin**: http://localhost:5050
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 4. Production Builds (Staging/Production)

### Build for Staging
\`\`\`bash
cd frontend
npm run build:staging

# Output: frontend/dist/ with optimized static files
# API URL configured for staging backend
\`\`\`

### Build for Production
\`\`\`bash
cd frontend
npm run build:prod

# Output: frontend/dist/ with optimized static files + source maps disabled
# API URL configured for production backend
\`\`\`

### Deploy with Nginx
\`\`\`bash
# Staging
./deploy.sh staging

# Production
./deploy.sh prod
\`\`\`

### How It Works
1. `npm run build` creates optimized static files in `frontend/dist/`
2. Nginx serves `index.html`, `assets/`, and routes all other requests to `index.html` (SPA)
3. Frontend makes API calls to backend using VITE_API_URL from `.env.staging` or `.env.production`
4. Nginx caches static assets (JS, CSS, images) with `Cache-Control` headers

---

## Troubleshooting

### Frontend Not Starting
\`\`\`bash
# Check if port 5173 is already in use
# Windows
netstat -ano | findstr :5173

# Linux/Mac
lsof -i :5173

# Kill process if needed
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
\`\`\`

### CORS Errors in Development
- **Symptom**: Console shows "CORS policy blocked..."
- **Solution**: Ensure Vite proxy is configured in `vite.config.ts`
- **Check**: API requests should go to `http://localhost:5173/api/*`, NOT `http://localhost:8000/api/*`

### Hot Reload Not Working (Docker)
- **Symptom**: Code changes don't reflect in browser
- **Solution**: Verify volumes are mounted correctly in `docker-compose.local.yml`
- **Check**: `docker-compose logs frontend-dev` should show "HMR update" messages

### Build Fails with "VITE_API_URL not defined"
- **Symptom**: `npm run build:staging` or `build:prod` fails
- **Solution**: Ensure `.env.staging` or `.env.production` exist with `VITE_API_URL=...`
- **Check**: `cat frontend/.env.staging` should show environment variables

---

## Environment Variables Reference

| File | Purpose | Required Variables |
|------|---------|-------------------|
| `.env.development` | Local dev (auto-loaded) | `VITE_API_URL=http://localhost:8000` |
| `.env.staging` | Staging builds | `VITE_API_URL=https://api-staging.contravento.com` |
| `.env.production` | Production builds | `VITE_API_URL=https://api.contravento.com` |

**Note**: Vite only exposes variables with `VITE_` prefix to the frontend code.
\`\`\`

**Delivery**: Complete quickstart.md with copy-paste commands for all 4 environments.

---

### 4. Update Agent Context (CLAUDE.md)

**Action**: Run context update script to add deployment patterns to CLAUDE.md.

**Command**:
```bash
# (This would be run by the script if PowerShell was available)
# .specify/scripts/powershell/update-agent-context.ps1 -AgentType claude
```

**Manual Update to CLAUDE.md** (since script unavailable):

Add new section under "## Commands" with deployment instructions:

```markdown
### Frontend Development

\`\`\`bash
# Start frontend dev server (from frontend/)
npm run dev

# Start both frontend + backend (from root)
./run-local-dev.sh --with-frontend        # Linux/Mac
.\\run-local-dev.ps1 -WithFrontend        # Windows PowerShell

# Build for production
npm run build:prod                        # Production build
npm run build:staging                     # Staging build
\`\`\`

### Docker with Frontend

\`\`\`bash
# Docker Minimal with frontend
./deploy.sh local-minimal --with-frontend

# Docker Full with frontend
./deploy.sh local --with-frontend

# View frontend logs
docker-compose logs -f frontend-dev
\`\`\`
```

**Delivery**: Updated CLAUDE.md section with frontend deployment commands.

---

## Phase 2: Task Breakdown

**Not generated by `/speckit.plan` command.**

Use `/speckit.tasks` after this plan is approved to generate detailed task breakdown (`tasks.md`).

**Expected Task Categories**:
1. **Infrastructure Tasks**: Update deployment scripts, Docker Compose files
2. **Configuration Tasks**: Create .env files, update vite.config.ts
3. **Documentation Tasks**: Update QUICK_START.md, create quickstart.md
4. **Testing Tasks**: Smoke test each environment, update TESTING_GUIDE.md
5. **Polish Tasks**: Cross-platform compatibility, error handling improvements

---

## Success Criteria (from spec.md)

Implementation will be validated against these criteria:

- **SC-001**: Developers can start frontend + backend in <30 seconds (SQLite Local)
- **SC-002**: Developers can start all services in <60 seconds (Docker Minimal)
- **SC-003**: TypeScript/CSS changes reflect in browser in <2 seconds (HMR)
- **SC-004**: Production builds reduce asset size by ≥60% (minification + tree-shaking)
- **SC-005**: Frontend loads initial page in <3 seconds on 3G (Lighthouse test)
- **SC-006**: Zero CORS errors in development console
- **SC-007**: 100% of developers can start environment from QUICK_START.md without help
- **SC-008**: Production builds are reproducible (same code = same file hashes)

---

## Implementation Phases Summary

| Phase | Deliverable | Status |
|-------|-------------|--------|
| **Phase 0** | research.md | ⏳ Pending |
| **Phase 1** | quickstart.md | ⏳ Pending |
| **Phase 1** | Agent context update (CLAUDE.md) | ⏳ Pending |
| **Phase 2** | tasks.md | ⏳ Pending (/speckit.tasks) |

**Next Step**: Execute Phase 0 research to resolve all technical unknowns.
