# Tasks: Complete Deployment Documentation

**Feature Branch**: develop (documentation commits)
**Input**: `docs/deployment/MIGRATION_PLAN.md`, existing docs in `backend/docs/`, root directory
**Prerequisites**: Phase 1 and Phase 5 already complete
**Current Status**: 31% Complete (9/29 tasks done)

**Organization**: Tasks organized by phase (sequential completion recommended).

## Format: `[ID] [Status] Description`

- **✅**: Completed
- **⏳**: Pending
- **🔄**: In Progress

---

## Progress Summary

| Phase | Tasks | Complete | % | Priority |
|-------|-------|----------|---|----------|
| Phase 1: Base Structure | 1 | 1 | 100% | ✅ DONE |
| Phase 2: Document Modes | 9 | 9 | 100% | ✅ DONE |
| Phase 3: Create Guides | 7 | 7 | 100% | ✅ DONE |
| Phase 4: Archive Old Docs | 4 | 0 | 0% | **HIGHEST** |
| Phase 5: Update References | 4 | 4 | 100% | ✅ DONE |
| Phase 6: Final Validation | 4 | 0 | 0% | Medium |
| **TOTAL** | **29** | **21** | **72%** | - |

---

## Phase 1: Create Base Structure ✅ COMPLETE

**Purpose**: Directory structure and master index

- [✅] T001 Create directories: `docs/deployment/{modes,guides,archive}`
- [✅] T002 Create `docs/deployment/README.md` with decision tree, comparative tables, feature matrix, quick links
- [✅] T003 Verify master README has placeholders for all 9 modes and 7 guides

**Checkpoint**: ✅ Structure complete, navigation working (2026-01-25)

**Files Created**:
- `docs/deployment/README.md` (1,234 lines)
- Directory structure established

---

## Phase 2: Document Deployment Modes (4/9 Complete) 🔄

**Purpose**: Document all 9 deployment modes following standard template

### ✅ Completed (Local Modes - Priority P1)

- [✅] T004 Create `docs/deployment/modes/local-dev.md` - SQLite without Docker (756 lines)
- [✅] T005 Create `docs/deployment/modes/local-minimal.md` - Docker + PostgreSQL (723 lines)
- [✅] T006 Create `docs/deployment/modes/local-full.md` - Full stack with MailHog, pgAdmin, Redis (812 lines)
- [✅] T007 Create `docs/deployment/modes/local-prod.md` - Local production build testing (689 lines)

**Checkpoint**: ✅ All local modes documented (2026-01-25)

### ⏳ Pending (Server Modes - Priority P2)

**Source Content**: Extract from `backend/docs/DEPLOYMENT.md` sections on dev, staging, production

- [✅] T008 Create `docs/deployment/modes/dev.md` - Development/Integration server deployment ✅ COMPLETED (2026-02-06)
  - **Overview**: Remote development server for team integration testing
  - **Prerequisites**: Docker, SSH access to dev server, GitLab/GitHub CI access
  - **Quick Start**: `./deploy.sh dev` commands
  - **Configuration**: .env.dev variables (DATABASE_URL, SMTP settings)
  - **Architecture**: Nginx reverse proxy, PostgreSQL, backend API, frontend static
  - **Troubleshooting**: SSL certificate issues, database connection timeouts
  - **Related Modes**: Progression from local-full → dev → staging
  - **Created**: 850+ lines, comprehensive guide covering architecture, Nginx configuration, SMTP setup, testing workflows, troubleshooting, security considerations

- [✅] T009 Create `docs/deployment/modes/staging.md` - Staging environment (production mirror) ✅ COMPLETED (2026-02-06)
  - **Overview**: Pre-production testing environment, mirrors prod configuration
  - **Prerequisites**: Docker, production-like server specs (2CPU, 4GB RAM)
  - **Quick Start**: `./deploy.sh staging` commands
  - **Configuration**: .env.staging variables, SSL certificates, CORS origins
  - **Architecture**: Same as prod but isolated database, monitoring enabled
  - **Troubleshooting**: SSL verification failures, email delivery issues (use staging SMTP)
  - **Related Modes**: Progression from dev → staging → prod
  - **Created**: 1,100+ lines, comprehensive guide covering SSL/TLS setup with Certbot, Prometheus + Grafana monitoring, testing checklist, performance testing, security hardening, troubleshooting SSL and monitoring issues

- [✅] T010 Create `docs/deployment/modes/prod.md` - Production deployment ✅ COMPLETED (2026-02-06)
  - **Overview**: Live production environment, high availability setup
  - **Prerequisites**: Docker Swarm/Kubernetes, load balancer, backup strategy
  - **Quick Start**: `./deploy.sh prod` commands, rollback procedures
  - **Configuration**: .env.production variables (all secrets via env), SSL/TLS setup
  - **Architecture**: HA setup with replicas, health checks, auto-scaling, monitoring (Prometheus + Grafana)
  - **Troubleshooting**: Zero-downtime deployment issues, database migration rollback
  - **Related Modes**: Staging is required before prod deployment
  - **Created**: 1,850+ lines, MOST COMPREHENSIVE guide covering HA architecture with 3+ replicas, auto-scaling, maximum security (BCRYPT_ROUNDS=14, 128-char secrets), SSL/TLS auto-renewal, full monitoring stack (Prometheus + Grafana + exporters), automated backups to S3, zero-downtime deployment, disaster recovery procedures, incident response, security hardening, performance tuning

- [✅] T011 Create `docs/deployment/modes/preproduction.md` - CI/CD (Jenkins) integration ✅ COMPLETED (2026-02-06)
  - **Overview**: Automated deployment triggered by Jenkins CI/CD pipeline
  - **Prerequisites**: Jenkins server, docker-compose.preproduction.yml
  - **Quick Start**: Jenkins pipeline syntax, manual trigger commands
  - **Configuration**: Jenkins environment variables, build parameters
  - **Architecture**: Build agent → Docker build → Deploy to preproduction environment
  - **Troubleshooting**: Jenkins agent connectivity, Docker build cache issues
  - **Related Modes**: Used for automated testing before manual staging deploy
  - **Created**: 869 lines, comprehensive CI/CD integration guide covering Jenkins/GitHub Actions/GitLab CI pipelines, pre-built Docker Hub images, auto-configuration, helper scripts (run-jenkins-env.sh/ps1), complete Jenkinsfile examples, testing workflows

- [✅] T012 Create `docs/deployment/modes/test.md` - Automated testing environment ✅ COMPLETED (2026-02-06)
  - **Overview**: Isolated environment for running automated tests (pytest, frontend tests)
  - **Prerequisites**: Docker, docker-compose.test.yml
  - **Quick Start**: `docker-compose -f docker-compose.test.yml up` commands
  - **Configuration**: Test database (in-memory SQLite or PostgreSQL), test fixtures
  - **Architecture**: Ephemeral containers, test database, no persistent volumes
  - **Troubleshooting**: Test database conflicts, port collisions with local-dev
  - **Related Modes**: Complements local-dev for running full test suites
  - **Created**: 764 lines, comprehensive testing guide covering PostgreSQL test database (port 5433), Redis test instance (port 6380), pytest integration tests, migration testing, cache testing, E2E tests with Playwright, CI/CD integration, test isolation best practices

**Checkpoint**: ✅ Phase 2 COMPLETE - All 9 modes documented (2026-02-06)

**Estimated Effort**: 2-3 days (5 modes × 4-6 hours each)

---

## Phase 3: Create Cross-Cutting Guides ✅ COMPLETE

**Purpose**: Universal guides that apply across multiple deployment modes

**Source Content**:
- `backend/docs/ENVIRONMENTS.md` (for T014)
- `DOCKER_COMPOSE_GUIDE.md` (for T015)
- `backend/docs/DEPLOYMENT.md` (frontend section for T016)
- Troubleshooting sections from all modes (for T013, T018)

### User-Facing Guides (Priority P1)

- [✅] T013 Create `docs/deployment/guides/getting-started.md` - Universal onboarding ✅ COMPLETED (2026-02-06)
  - **Purpose**: First document a new developer reads
  - **Content**:
    - "Choose Your Mode" flowchart (5 questions → recommended mode)
    - First-time setup (git clone, install dependencies)
    - Verification steps (backend running, frontend running, login works)
    - Next steps (explore codebase, read CLAUDE.md, run tests)
  - **Created**: 550+ lines, comprehensive guide with role-based paths, decision tree, 3 setup options, verification steps
  - **Estimated Effort**: 3-4 hours

- [✅] T015 Create `docs/deployment/guides/troubleshooting.md` - Common problems cross-mode ✅ COMPLETED (2026-02-06)
  - **Purpose**: First place to look when something breaks
  - **Content** (organized by symptom):
    - **Port Conflicts**: 5173 (frontend), 8000 (backend), 5432 (PostgreSQL), 6379 (Redis), 8025 (MailHog)
      - How to find process using port (Windows, Linux, macOS)
      - How to kill process or change port
    - **Docker Issues**: Container won't start, can't connect to PostgreSQL, volume mount errors
      - `docker-compose ps` (check status)
      - `docker-compose logs` (view errors)
      - `docker-compose down -v` (clean start)
    - **Database Errors**: Connection refused, migration conflicts, seed data missing
      - Verify DATABASE_URL format
      - Run migrations: `poetry run alembic upgrade head`
      - Create admin user: `poetry run python scripts/user-mgmt/create_admin.py`
    - **Frontend Build Failures**: TypeScript errors, Vite build hangs, assets not loading
      - Clear node_modules: `rm -rf node_modules && npm install`
      - Check .env files: VITE_API_URL must match backend
      - Hard refresh browser: Ctrl+Shift+R
    - **Permission Errors**: Can't write to storage/, Docker socket permission denied
      - Linux/macOS: `sudo chown -R $USER:$USER storage/`
      - Windows: Run as Administrator or adjust folder permissions
  - **Created**: 900+ lines, comprehensive guide covering 7 categories with Windows/Linux/Mac solutions, quick diagnosis flowchart, emergency reset procedures
  - **Estimated Effort**: 4-5 hours

### Technical Guides (Priority P2)

- [✅] T014 Create `docs/deployment/guides/environment-variables.md` - Consolidate ENVIRONMENTS.md ✅ COMPLETED (2026-02-06)
  - **Purpose**: Reference for all .env configuration options
  - **Content** (migrate from `backend/docs/ENVIRONMENTS.md`):
    - Variable categories: Database, Auth, Email, Storage, Frontend, Testing
    - Default values per mode (table format)
    - Security warnings (SECRET_KEY must be 32+ chars, never commit .env files)
    - How to generate secrets: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - **Source**: `backend/docs/ENVIRONMENTS.md` (615 lines, español)
  - **Created**: 1000+ lines, comprehensive reference with 8 variable categories, configuration by mode, security best practices, secret generation, common pitfalls
  - **Estimated Effort**: 3-4 hours (mostly translation + reorganization)

- [✅] T016 Create `docs/deployment/guides/docker-compose-guide.md` - Docker Compose architecture ✅ COMPLETED (2026-02-06)
  - **Purpose**: Understand how services connect
  - **Content** (migrate from `DOCKER_COMPOSE_GUIDE.md` if exists, else extract from modes):
    - Service dependency diagram (ASCII art or Mermaid)
    - Networking (contravento-network bridge)
    - Volume management (persistent data vs ephemeral)
    - Health checks (when services are "ready")
    - Override patterns (docker-compose.override.yml)
  - **Created**: 850+ lines, comprehensive architecture guide with service dependencies, networking internals, volume management, health checks, overlay patterns, debugging, best practices
  - **Estimated Effort**: 3-4 hours

- [✅] T017 Create `docs/deployment/guides/frontend-deployment.md` - Frontend-specific deployment ✅ COMPLETED (2026-02-06)
  - **Purpose**: Deep dive into frontend build and deployment
  - **Content**:
    - Vite build process (dev vs staging vs prod)
    - Environment variable injection (import.meta.env.VITE_*)
    - Build output analysis (dist/ folder structure)
    - Nginx configuration (cache headers, security headers, gzip)
    - Source maps handling (staging: yes, prod: no)
    - Asset optimization (code splitting, lazy loading)
  - **Source**: Extract from `backend/docs/DEPLOYMENT.md` frontend sections
  - **Created**: 1100+ lines, comprehensive guide covering 3 build modes, environment variables, build process, Nginx configuration, optimization techniques
  - **Estimated Effort**: 3-4 hours

- [✅] T018 Create `docs/deployment/guides/database-management.md` - Migrations, seeds, backups ✅ COMPLETED (2026-02-06)
  - **Purpose**: Database administration tasks
  - **Content**:
    - Alembic workflow (create migration, apply, rollback)
    - Seed scripts (create_admin.py, create_verified_user.py, seed_cycling_types.py)
    - Backup procedures (PostgreSQL: pg_dump, SQLite: copy file)
    - Restore procedures
    - PostgreSQL vs SQLite differences (UUIDs, arrays, foreign keys)
  - **Created**: 950+ lines, comprehensive guide covering Alembic migrations, seed scripts, backup/restore procedures, database differences, common operations
  - **Estimated Effort**: 3-4 hours

- [✅] T019 Create `docs/deployment/guides/production-checklist.md` - Pre-deploy verification ✅ COMPLETED (2026-02-06)
  - **Purpose**: Prevent production incidents
  - **Content** (checklist format):
    - **Code Quality**:
      - [ ] All tests passing (`poetry run pytest`, `npm test`)
      - [ ] Linting clean (`poetry run ruff check`, `npm run lint`)
      - [ ] Type checking passing (`poetry run mypy`, `npm run type-check`)
    - **Database**:
      - [ ] Migrations applied (`poetry run alembic upgrade head`)
      - [ ] Seed data loaded (admin user exists)
      - [ ] Backup taken before deploy
    - **Security**:
      - [ ] .env.production has all secrets (SECRET_KEY, DATABASE_URL, SMTP credentials)
      - [ ] CORS_ORIGINS configured correctly (production domains only)
      - [ ] Rate limiting enabled
      - [ ] File upload validation working
    - **Performance**:
      - [ ] Frontend build optimized (`npm run build:prod`, check dist/ size)
      - [ ] Database indexes verified (no missing indexes)
      - [ ] Response times <500ms p95 (load testing)
    - **Monitoring**:
      - [ ] Health check endpoints working (/health, /api/health)
      - [ ] Error tracking configured (Sentry or similar)
      - [ ] Logs forwarding to centralized system
    - **Rollback Plan**:
      - [ ] Previous version tagged in git
      - [ ] Rollback command documented
      - [ ] Database rollback strategy (if migrations applied)
  - **Created**: 1,200+ lines, comprehensive pre-deployment checklist covering code quality, database, security, performance, monitoring, rollback preparation, deployment execution, post-deployment validation, and emergency procedures
  - **Estimated Effort**: 2-3 hours

**Checkpoint**: ✅ Phase 3 complete - All 7 guides created (2026-02-06)

**Total Content Created**: ~6,450 lines of documentation across 7 comprehensive guides

**Guides Created**:
1. getting-started.md (550+ lines) - Universal onboarding
2. troubleshooting.md (900+ lines) - Common problems cross-mode
3. environment-variables.md (1000+ lines) - Configuration reference
4. docker-compose-guide.md (850+ lines) - Architecture deep dive
5. frontend-deployment.md (1100+ lines) - Frontend build and deployment
6. database-management.md (950+ lines) - Migrations, seeds, backups
7. production-checklist.md (1200+ lines) - Pre-deploy verification

---

## Phase 4: Archive Old Documentation ✅ COMPLETE

**Purpose**: Preserve old docs and create redirects to prevent broken links

### Archive Old Files

- [✅] T020 Archive `QUICK_START.md` → `docs/deployment/archive/v0.3.0-QUICK_START.md`
  - ✅ Copied original file to archive (1,098 lines)
  - ✅ Preserved original formatting (no edits)
  - **Completion**: 2026-01-28

- [✅] T021 Archive `backend/docs/DEPLOYMENT.md` → `docs/deployment/archive/v0.3.0-DEPLOYMENT.md`
  - ✅ Copied original file to archive (3,725 lines)
  - ✅ Verified complete migration
  - **Completion**: 2026-01-28

- [✅] T022 Archive `backend/docs/ENVIRONMENTS.md` → `docs/deployment/archive/v0.3.0-ENVIRONMENTS.md`
  - ✅ Copied original file to archive
  - **Completion**: 2026-01-28

### Create Redirects

- [✅] T023 Replace original files with redirect documents
  - ✅ Replaced `QUICK_START.md` with redirect to `docs/deployment/README.md`
  - ✅ Replaced `backend/docs/DEPLOYMENT.md` with redirect to `docs/deployment/README.md`
  - ✅ Replaced `backend/docs/ENVIRONMENTS.md` with redirect to `docs/deployment/guides/environment-variables.md`
  - ✅ Used standard redirect template (FR-003)
  - **Completion**: 2026-01-28

**Checkpoint**: ✅ Old docs archived and redirects in place (2026-01-28)

**Estimated Effort**: 1 day (verification-heavy, ensure no data loss)

---

## Phase 5: Update References ✅ COMPLETE

**Purpose**: Make new documentation discoverable from all entry points

- [✅] T024 Update `CLAUDE.md`
  - Added prominent link to `docs/deployment/` in "Local Development Options" section
  - Updated "Commands" section to reference deployment modes

- [✅] T025 Update `frontend/README.md`
  - Added "Deployment a Diferentes Entornos" section
  - Links to local-dev.md, local-full.md, local-prod.md

- [✅] T026 Update deployment scripts with documentation links
  - `run-local-dev.sh` / `run-local-dev.ps1`: Header comment with link to modes/local-dev.md
  - `deploy.sh` / `deploy.ps1`: Help text with link to docs/deployment/README.md

- [✅] T027 Update `.github/workflows/README.md`
  - Added "Deployment Documentation" section in References
  - Link to docs/deployment/ for CI/CD context

**Checkpoint**: ✅ Documentation discoverable from CLAUDE.md, scripts, GitHub (2026-01-25)

---

## Phase 6: Final Validation (0/4 Complete) ⏳

**Purpose**: Ensure documentation quality and usability before marking complete

### Validation Tests

- [ ] T028 Test navigation flow
  - Start at `QUICK_START.md` redirect → verify lands on `docs/deployment/README.md`
  - Follow decision tree → verify reaches correct mode (e.g., "no Docker" → local-dev.md)
  - Click internal links → verify no 404 errors (all modes, guides linked)
  - Test "Related Modes" links → verify progression paths work

- [ ] T029 Verify commands work
  - Pick one mode (recommend local-dev as most common)
  - Follow Quick Start commands exactly as written
  - Verify URLs are correct (frontend: 5173, backend: 8000, etc.)
  - Verify default credentials work (admin/AdminPass123!)
  - Test at least one Troubleshooting solution

- [ ] T030 Test search and discoverability
  - GitHub search: "deployment local" → verify finds modes/local-dev.md
  - GitHub search: "environment variables" → verify finds guides/environment-variables.md
  - GitHub search: "troubleshooting" → verify finds guides/troubleshooting.md
  - Ctrl+F in README.md: Search for keywords (Docker, PostgreSQL, SQLite) → verify hits

- [ ] T031 Peer review
  - Request review from at least 1 other developer (not original author)
  - Questions for reviewer:
    - Is decision tree clear? (yes/no + suggestions)
    - Can you set up local-dev from docs alone? (yes/no + blockers)
    - Did you find any broken links? (list them)
    - What's missing or unclear? (open feedback)
  - Address feedback before marking complete

**Checkpoint**: Phase 6 complete when all validation tests pass

**Estimated Effort**: 1 day (testing is time-consuming)

---

## Dependencies & Execution Order

### Phase Dependencies

**Sequential (Must Complete in Order)**:
1. Phase 1 → Phase 2 (need structure before writing modes)
2. Phase 2 → Phase 3 (guides reference modes)
3. Phase 3 → Phase 4 (ensure all content migrated before archiving)
4. Phase 4 → Phase 6 (validate after archive/redirects in place)

**Independent (Can Do in Any Order)**:
- Phase 5 (Update References) - ✅ Already done early for discoverability
- Phase 2 and Phase 3 can partially overlap (start guides while finishing modes)

### Recommended Execution Strategy

**Option 1: Complete Phases Sequentially** (safest)
1. Finish Phase 2 (5 server modes) - 2-3 days
2. Complete Phase 3 (7 guides) - 2-3 days
3. Execute Phase 4 (archive) - 1 day
4. Validate Phase 6 - 1 day

**Total**: 6-8 days

**Option 2: Parallel Work** (faster if multiple contributors)
1. Developer A: Phase 2 (server modes)
2. Developer B: Phase 3 (guides)
3. Meet for Phase 4 and 6 together

**Total**: 4-5 days (with 2 developers)

**Option 3: Highest Value First** (recommended) ⭐
1. Phase 3: Guides (highest value for developers, especially getting-started.md and troubleshooting.md) - 2-3 days
2. Phase 2: Server modes (needed for DevOps) - 2-3 days
3. Phase 4: Archive (cleanup) - 1 day
4. Phase 6: Validation - 1 day

**Total**: 6-8 days, but value delivered earlier

---

## Notes

- **Language**: All new docs in English (industry standard, maintainability)
- **Template Compliance**: All modes and guides follow standard structure
- **No Content Loss**: Archive originals before replacing (Phase 4 critical)
- **Link Preservation**: Use redirects, not deletions (backward compatibility)
- **Peer Review**: At least 1 other developer reviews before marking complete
- **Iterative**: Can deploy docs as each phase completes (don't wait for 100%)

---

## Success Criteria Summary

**Completion**:
- ✅ 29/29 tasks complete (currently 9/29)
- ✅ 17 documentation files created (currently 5/17)
- ✅ ~12,000 lines of documentation (currently ~4,214)

**Quality**:
- ✅ Template compliance: 100% of modes follow structure
- ✅ Link validation: Zero broken links
- ✅ Command validation: All commands tested in ≥1 environment
- ✅ Peer review: Approved by ≥1 reviewer

**User Impact**:
- ✅ New developer onboarding: <10 minutes to environment setup
- ✅ Troubleshooting success: ≥80% of issues resolved via docs
- ✅ Search success: ≥90% of deployment searches find correct page
- ✅ Team feedback: ≥4/5 stars (qualitative survey)

---

## Total Tasks: 29 tasks across 6 phases

**Current Status**: 25/29 (86%) ✅

**Remaining Work**: 4 tasks
- Phase 6: 4 tasks (validation) ⭐ **HIGHEST PRIORITY**

**Estimated Remaining Effort**: 0.5 days

**Next Action**: Start Phase 6 (Final Validation) - T028 through T031
