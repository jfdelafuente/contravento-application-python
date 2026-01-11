# Tasks: Frontend Deployment Integration

**Input**: Design documents from `/specs/011-frontend-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: Not required for this infrastructure feature (deployment scripts and configuration)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each deployment environment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/` at repository root
- Root-level deployment scripts: `run-local-dev.sh`, `deploy.sh`, `docker-compose.*.yml`
- Documentation: `QUICK_START.md`, `backend/docs/DEPLOYMENT.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration files

- [x] T001 [P] Create frontend environment file templates: `frontend/.env.example` with VITE_API_URL and VITE_TURNSTILE_SITE_KEY
- [x] T002 [P] Create `frontend/.env.development` with VITE_API_URL=http://localhost:8000
- [x] T003 [P] Create `frontend/.env.staging` template with placeholder for staging API URL
- [x] T004 [P] Create `frontend/.env.production` template with placeholder for production API URL
- [x] T005 [P] Update `frontend/.gitignore` to exclude `.env.staging` and `.env.production` (security)
- [x] T006 [P] Create `frontend/Dockerfile.dev` for Vite dev server with volume mounts
- [x] T007 [P] Create `frontend/Dockerfile.prod` multi-stage build (Node builder + Nginx server)
- [x] T008 [P] Create `frontend/nginx.conf` with SPA routing (try_files) and cache headers

**Checkpoint**: Environment files and Dockerfiles ready for all deployment modes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T009 Update `frontend/vite.config.ts` to add server.proxy configuration for /api/* → http://localhost:8000
- [x] T010 [P] Update `frontend/package.json` to add build:staging script (vite build --mode staging)
- [x] T011 [P] Update `frontend/package.json` to add build:prod script (vite build --mode production)
- [x] T012 Verify Vite HMR works with proxy configuration by testing local dev server startup

**Checkpoint**: Frontend configuration ready - deployment scripts can now be implemented in parallel per environment

---

## Phase 3: User Story 1 - Desarrollo Local con Frontend y Backend (Priority: P1) 🎯 MVP

**Goal**: Developers can run frontend + backend together with a single command in SQLite Local mode (no Docker)

**Independent Test**: Execute `./run-local-dev.sh --with-frontend` (Linux/Mac) or `.\run-local-dev.ps1 -WithFrontend` (Windows) and verify:
1. Frontend starts on http://localhost:5173
2. Backend starts on http://localhost:8000
3. Login works (HttpOnly cookies)
4. TypeScript file change triggers HMR in <2 seconds

### Implementation for User Story 1

- [x] T013 [US1] Update `run-local-dev.sh` to add --with-frontend flag that starts both backend and frontend processes
- [x] T014 [US1] Update `run-local-dev.ps1` to add -WithFrontend parameter that starts both backend and frontend processes
- [x] T015 [US1] Add process management to `run-local-dev.sh` to handle cleanup when script exits (trap signals)
- [x] T016 [US1] Add process management to `run-local-dev.ps1` to handle cleanup when script exits (Register-EngineEvent)
- [x] T017 [US1] Add logging to `run-local-dev.sh` showing frontend and backend URLs when services start
- [x] T018 [US1] Add logging to `run-local-dev.ps1` showing frontend and backend URLs when services start
- [x] T019 [US1] Add error handling to `run-local-dev.sh` to detect if port 5173 is already in use
- [x] T020 [US1] Add error handling to `run-local-dev.ps1` to detect if port 5173 is already in use
- [ ] T021 [US1] Update `QUICK_START.md` section "SQLite Local" to document --with-frontend flag with examples
- [ ] T022 [US1] Create troubleshooting section in `QUICK_START.md` for "Port 5173 Already in Use" with Windows/Linux commands

**Checkpoint**: SQLite Local mode with frontend should be fully functional - developers can start both services with one command

---

## Phase 4: User Story 2 - Desarrollo con Docker Minimal (Priority: P2)

**Goal**: Developers can run frontend + backend + PostgreSQL in Docker Minimal mode

**Independent Test**: Execute `./deploy.sh local-minimal --with-frontend` and verify:
1. Frontend container (Vite dev) starts and is accessible at http://localhost:5173
2. Backend container connects to PostgreSQL
3. Hot reload works (file changes in mounted volumes trigger HMR)
4. All services pass healthchecks

### Implementation for User Story 2

- [ ] T023 [US2] Add frontend-dev service definition to `docker-compose.local-minimal.yml` with Dockerfile.dev
- [ ] T024 [US2] Configure volume mounts in `docker-compose.local-minimal.yml` frontend service: ./frontend:/app and /app/node_modules
- [ ] T025 [US2] Add depends_on with service_healthy condition for backend in `docker-compose.local-minimal.yml` frontend service
- [ ] T026 [US2] Add environment variable VITE_API_URL=http://backend:8000 to `docker-compose.local-minimal.yml` frontend service
- [ ] T027 [US2] Add healthcheck to `docker-compose.local-minimal.yml` frontend service (curl http://localhost:5173)
- [ ] T028 [US2] Add port mapping 5173:5173 to `docker-compose.local-minimal.yml` frontend service
- [ ] T029 [US2] Update `deploy.sh` to add --with-frontend flag that includes frontend service in local-minimal deployment
- [ ] T030 [US2] Update `deploy.ps1` to add -WithFrontend parameter that includes frontend service in local-minimal deployment
- [ ] T031 [US2] Update `QUICK_START.md` section "Docker Minimal" to document --with-frontend flag with docker-compose logs examples
- [ ] T032 [US2] Create troubleshooting section in `QUICK_START.md` for "Hot Reload Not Working (Docker)" with volume mount verification

**Checkpoint**: Docker Minimal mode should work end-to-end with frontend, backend, and PostgreSQL communicating correctly

---

## Phase 5: User Story 3 - Desarrollo con Docker Full (Priority: P3)

**Goal**: Developers can run frontend + backend + all services (PostgreSQL, Redis, MailHog, pgAdmin) in Docker Full mode

**Independent Test**: Execute `./deploy.sh local --with-frontend` and verify:
1. All 6 services start (frontend, backend, PostgreSQL, Redis, MailHog, pgAdmin)
2. User registration sends email that appears in MailHog (http://localhost:8025)
3. pgAdmin can visualize database (http://localhost:5050)
4. Frontend can complete full user flows (register, verify email, login, create trip)

### Implementation for User Story 3

- [ ] T033 [US3] Add frontend-dev service definition to `docker-compose.local.yml` (copy from local-minimal with same config)
- [ ] T034 [US3] Configure volume mounts in `docker-compose.local.yml` frontend service: ./frontend:/app and /app/node_modules
- [ ] T035 [US3] Add depends_on with service_healthy condition for backend in `docker-compose.local.yml` frontend service
- [ ] T036 [US3] Add environment variable VITE_API_URL=http://backend:8000 to `docker-compose.local.yml` frontend service
- [ ] T037 [US3] Add healthcheck to `docker-compose.local.yml` frontend service (curl http://localhost:5173)
- [ ] T038 [US3] Add port mapping 5173:5173 to `docker-compose.local.yml` frontend service
- [ ] T039 [US3] Update `deploy.sh` local mode to include frontend service when --with-frontend flag is used
- [ ] T040 [US3] Update `deploy.ps1` local mode to include frontend service when -WithFrontend parameter is used
- [ ] T041 [US3] Update `QUICK_START.md` section "Docker Full" to document all 6 services with access URLs
- [ ] T042 [US3] Update `QUICK_START.md` to add example testing email functionality with MailHog integration

**Checkpoint**: Docker Full mode should provide complete development environment with all services operational

---

## Phase 6: User Story 4 - Build de Producción para Staging/Prod (Priority: P1)

**Goal**: DevOps can generate optimized production builds for staging and production deployment

**Independent Test**: Execute `npm run build:staging` and `npm run build:prod` and verify:
1. `frontend/dist/` directory is created with minified HTML/CSS/JS
2. Assets have content hashes in filenames (e.g., index-abc123.js)
3. Build size is ≥60% smaller than dev files (SC-004)
4. Source maps are included in staging build but excluded in production build
5. Built files can be served by Nginx with SPA routing working

### Implementation for User Story 4

- [ ] T043 [US4] Update `frontend/vite.config.ts` to configure build.rollupOptions for chunking vendor libraries separately
- [ ] T044 [US4] Update `frontend/vite.config.ts` to configure build.sourcemap based on mode (true for staging, false for production)
- [ ] T045 [US4] Update `frontend/vite.config.ts` to configure build.minify='terser' for production builds
- [ ] T046 [US4] Update `frontend/vite.config.ts` to configure build.cssMinify=true for production builds
- [ ] T047 [US4] Verify `frontend/nginx.conf` has correct cache headers (1 year for hashed assets, no-cache for index.html)
- [ ] T048 [US4] Verify `frontend/nginx.conf` has security headers (X-Frame-Options, X-Content-Type-Options, X-XSS-Protection)
- [ ] T049 [US4] Verify `frontend/nginx.conf` has gzip compression enabled for text/css, application/javascript
- [ ] T050 [US4] Update `deploy.sh` staging mode to run `npm run build:staging` before building Docker image
- [ ] T051 [US4] Update `deploy.sh` prod mode to run `npm run build:prod` before building Docker image
- [ ] T052 [US4] Update `deploy.ps1` staging mode to run `npm run build:staging` before building Docker image
- [ ] T053 [US4] Update `deploy.ps1` prod mode to run `npm run build:prod` before building Docker image
- [ ] T054 [US4] Add frontend service definition to `docker-compose.staging.yml` using Dockerfile.prod
- [ ] T055 [US4] Add frontend service definition to `docker-compose.prod.yml` using Dockerfile.prod with HA configuration
- [ ] T056 [US4] Update `QUICK_START.md` section "Production Builds" to document build:staging and build:prod scripts
- [ ] T057 [US4] Update `QUICK_START.md` to add verification steps for checking dist/ output and file sizes

**Checkpoint**: Production builds should generate optimized static files ready for staging/production deployment with Nginx

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and improvements that affect multiple user stories

- [ ] T058 [P] Update `backend/docs/DEPLOYMENT.md` to reference frontend deployment instructions in QUICK_START.md
- [ ] T059 [P] Update `CLAUDE.md` section "Frontend Development" with deployment commands for all 4 environments
- [ ] T060 [P] Create `frontend/DEPLOYMENT_TESTING.md` with smoke test checklist for each environment
- [ ] T061 [P] Add "Environment Variables Reference" section to `QUICK_START.md` documenting all VITE_* variables
- [ ] T062 [P] Add "Common Commands" quick reference table to `QUICK_START.md` with npm/docker commands
- [ ] T063 Validate all 4 deployment modes work end-to-end following `specs/011-frontend-deployment/quickstart.md`
- [ ] T064 Run quickstart validation: SQLite Local startup completes in <30 seconds (SC-001)
- [ ] T065 Run quickstart validation: Docker Minimal startup completes in <60 seconds (SC-002)
- [ ] T066 Run quickstart validation: HMR updates complete in <2 seconds (SC-003)
- [ ] T067 Run quickstart validation: Production build reduces size by ≥60% (SC-004)
- [ ] T068 Run quickstart validation: No CORS errors in browser console (SC-006)
- [ ] T069 Code cleanup: Remove any debug logging or commented code from deployment scripts
- [ ] T070 Security review: Verify no secrets in `.env.example` files and .gitignore is correct

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - **US1 (SQLite Local)**: Can start after Foundational - No dependencies on other stories
  - **US2 (Docker Minimal)**: Can start after Foundational - Reuses patterns from US1 scripts
  - **US3 (Docker Full)**: Can start after Foundational - Reuses docker-compose patterns from US2
  - **US4 (Production Builds)**: Can start after Foundational - Independent from US1-3 (different concern)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - SQLite Local)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2 - Docker Minimal)**: Can start after Foundational (Phase 2) - Independently testable, though script patterns similar to US1
- **User Story 3 (P3 - Docker Full)**: Can start after Foundational (Phase 2) - Independently testable, though docker-compose patterns similar to US2
- **User Story 4 (P1 - Production Builds)**: Can start after Foundational (Phase 2) - Completely independent (build tooling vs runtime deployment)

### Within Each User Story

**US1 (SQLite Local)**:
1. Update shell scripts (.sh then .ps1 in parallel)
2. Add process management to scripts
3. Add logging and error handling
4. Update documentation

**US2 (Docker Minimal)**:
1. Update docker-compose.local-minimal.yml with frontend service
2. Update deploy scripts to handle --with-frontend flag
3. Update documentation with docker commands

**US3 (Docker Full)**:
1. Update docker-compose.local.yml with frontend service (reuse US2 config)
2. Update deploy scripts for local mode
3. Update documentation with all services access URLs

**US4 (Production Builds)**:
1. Configure vite.config.ts for optimized builds
2. Verify nginx.conf has production settings
3. Update deploy scripts to trigger builds
4. Add production docker-compose configs
5. Document build process

### Parallel Opportunities

- **Phase 1 (Setup)**: All T001-T008 can run in parallel (different files)
- **Phase 2 (Foundational)**: T010-T011 can run in parallel (package.json scripts are independent)
- **User Stories**: US1, US2, US3, US4 can all be developed in parallel by different team members after Foundational phase
- **Within US1**: T013-T014 (shell scripts), T015-T016 (process management), T017-T018 (logging), T019-T020 (error handling) can be paired (Linux + Windows together)
- **Within US2**: T023-T028 (docker-compose config), T029-T030 (deploy scripts) can be paired
- **Within US3**: T033-T038 (docker-compose config), T039-T040 (deploy scripts) can be paired
- **Within US4**: T043-T046 (vite.config), T047-T049 (nginx.conf), T050-T053 (deploy scripts), T054-T055 (docker-compose) can be done in parallel
- **Phase 7 (Polish)**: T058-T062 (documentation) can run in parallel

---

## Parallel Example: User Story 1 (SQLite Local)

```bash
# Launch shell script updates together (Linux + Windows):
Task: "Update run-local-dev.sh to add --with-frontend flag" (T013)
Task: "Update run-local-dev.ps1 to add -WithFrontend parameter" (T014)

# Launch process management together:
Task: "Add process management to run-local-dev.sh" (T015)
Task: "Add process management to run-local-dev.ps1" (T016)

# Launch logging together:
Task: "Add logging to run-local-dev.sh showing URLs" (T017)
Task: "Add logging to run-local-dev.ps1 showing URLs" (T018)
```

---

## Parallel Example: User Story 4 (Production Builds)

```bash
# Launch vite.config.ts updates together:
Task: "Configure rollupOptions for chunking" (T043)
Task: "Configure sourcemap based on mode" (T044)
Task: "Configure minify='terser'" (T045)
Task: "Configure cssMinify=true" (T046)

# Launch nginx.conf verification together:
Task: "Verify cache headers" (T047)
Task: "Verify security headers" (T048)
Task: "Verify gzip compression" (T049)

# Launch deploy script updates together (staging + prod, Linux + Windows):
Task: "Update deploy.sh staging mode" (T050)
Task: "Update deploy.sh prod mode" (T051)
Task: "Update deploy.ps1 staging mode" (T052)
Task: "Update deploy.ps1 prod mode" (T053)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 4 Only)

**Why**: US1 (SQLite Local) and US4 (Production Builds) are both P1 and cover the most common use cases (daily development + deployment)

1. Complete Phase 1: Setup → Environment files ready
2. Complete Phase 2: Foundational → Vite configured with proxy and build scripts
3. Complete Phase 3: User Story 1 (SQLite Local) → Daily development workflow ready
4. Complete Phase 6: User Story 4 (Production Builds) → Deployment to staging/prod ready
5. **STOP and VALIDATE**: Test both daily development and production deployment
6. Deploy to staging if ready

### Incremental Delivery

1. Complete Setup + Foundational → ✅ Foundation ready
2. Add User Story 1 (SQLite Local) → ✅ Daily development workflow (MVP!)
3. Add User Story 4 (Production Builds) → ✅ Deployment pipeline ready
4. Add User Story 2 (Docker Minimal) → ✅ PostgreSQL testing capability
5. Add User Story 3 (Docker Full) → ✅ Complete local environment
6. Each story adds value without breaking previous workflows

### Parallel Team Strategy

With multiple developers (after Foundational phase completes):

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - **Developer A**: User Story 1 (SQLite Local scripts)
   - **Developer B**: User Story 4 (Production builds + Nginx)
   - **Developer C**: User Story 2 (Docker Minimal)
   - **Developer D**: User Story 3 (Docker Full)
3. Stories complete and integrate independently
4. All 4 deployment modes work simultaneously without conflicts

---

## Notes

- **[P] tasks** = Different files, no dependencies - can run in parallel
- **[Story] label** = Maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Windows + Linux parity**: For every .sh script task, there's a corresponding .ps1 task to maintain cross-platform support
- **No tests required**: This is infrastructure/deployment work - manual validation via quickstart.md is sufficient
- **Constitution compliance**: All scripts must follow error handling patterns (set -e for bash, $ErrorActionPreference="Stop" for PowerShell)
- Avoid: Hardcoded URLs (use environment variables), skipping error handling, incomplete documentation
