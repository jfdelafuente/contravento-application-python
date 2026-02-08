# ContraVento - Deployment Documentation

Welcome to the unified deployment documentation for ContraVento, a FastAPI-based cycling social platform.

**Last Updated**: 2026-01-25

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Decision Tree](#decision-tree)
3. [Deployment Modes Comparison](#deployment-modes-comparison)
4. [Deployment Modes](#deployment-modes)
5. [Guides](#guides)
6. [Migration from Old Documentation](#migration-from-old-documentation)
7. [📋 Migration Plan](MIGRATION_PLAN.md) - Detailed implementation status

---

## Quick Start

**New to ContraVento?** Start here:

- 👉 **[Getting Started Guide](guides/getting-started.md)** - Your first steps with ContraVento deployment
- 🤔 **Not sure which mode to use?** → See [Decision Tree](#decision-tree) below
- 📚 **Need detailed configuration?** → See [Environment Variables Guide](guides/environment-variables.md)

**I just want to code:**
```bash
# Fastest option - SQLite, no Docker, instant startup
./run-local-dev.sh --setup  # First time only
./run-local-dev.sh          # Start development
```

---

## Decision Tree

### Choose Your Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│ Q1: Do you have Docker installed?                          │
└─────────────────────────────────────────────────────────────┘
         │
         ├─ NO ──► local-dev (SQLite)
         │         ./run-local-dev.sh
         │         ✅ Instant startup, zero config
         │
         └─ YES ──► Continue to Q2 ↓

┌─────────────────────────────────────────────────────────────┐
│ Q2: What do you need to test/develop?                      │
└─────────────────────────────────────────────────────────────┘
         │
         ├─ Basic features (trips, profiles, stats)
         │  ──► local-minimal (Docker + PostgreSQL)
         │      ./deploy.sh local-minimal
         │
         ├─ Email/auth features (registration, password reset)
         │  ──► local-full (Docker + PostgreSQL + MailHog + pgAdmin)
         │      ./deploy.sh local
         │
         ├─ Production build testing (Nginx + optimized frontend)
         │  ──► local-prod (Docker + Production build)
         │      ./deploy-local-prod.sh
         │
         └─ Continue to Q3 ↓

┌─────────────────────────────────────────────────────────────┐
│ Q3: Are you deploying to a server?                         │
└─────────────────────────────────────────────────────────────┘
         │
         ├─ Development/Integration server
         │  ──► dev (Docker + Nginx + Real SMTP)
         │      ./deploy.sh dev
         │
         ├─ Staging/Pre-production (production mirror)
         │  ──► staging (Docker + SSL + Monitoring)
         │      ./deploy.sh staging
         │
         ├─ Production (live users)
         │  ──► prod (Docker + HA + Auto-scaling)
         │      ./deploy.sh prod
         │
         ├─ CI/CD Pipeline (Jenkins, GitHub Actions)
         │  ──► preproduction (Docker + Jenkins integration)
         │      ./deploy.sh preproduction
         │
         └─ Automated testing
            ──► test (Docker + In-memory DB)
                ./deploy.sh test
```

### Quick Recommendations

| Your Situation | Use This Mode | Why? |
|----------------|---------------|------|
| 💡 "I want to start NOW" | [local-dev](modes/local-dev.md) | Instant startup, zero config |
| 🐘 "I need PostgreSQL" | [local-minimal](modes/local-minimal.md) | Real database, minimal overhead |
| 📧 "Testing emails" | [local-full](modes/local-full.md) | MailHog UI, full stack |
| 🎯 "Need pgAdmin/Redis" | [local-full](modes/local-full.md) | Complete tooling |
| 🚀 "Testing production build" | [local-prod](modes/local-prod.md) | Nginx + optimized frontend |
| 🔧 "Integration server" | [dev](modes/dev.md) | Real SMTP, Nginx proxy |
| 🧪 "Pre-production QA" | [staging](modes/staging.md) | Production mirror |
| ✅ "Live production" | [prod](modes/prod.md) | High availability |
| 🤖 "CI/CD pipeline" | [preproduction](modes/preproduction.md) | Jenkins integration |

---

## Deployment Modes Comparison

### Local Development Modes (For Developers)

| Mode | Docker | Database | Startup Time | Hot Reload | Email Testing | Use When |
|------|--------|----------|--------------|-----------|---------------|----------|
| **[local-dev](modes/local-dev.md)** | ❌ | SQLite | Instant | ✅ | Console logs | Daily development |
| **[local-minimal](modes/local-minimal.md)** | ✅ | PostgreSQL | ~10s | ✅ | Console logs | PostgreSQL testing |
| **[local-full](modes/local-full.md)** | ✅ | PostgreSQL | ~20-30s | ✅ | MailHog UI | Email/cache testing |
| **[local-prod](modes/local-prod.md)** | ✅ | PostgreSQL | ~30s | ❌ | MailHog UI | Production build testing |

### Server Deployment Modes (For Operations)

| Mode | Docker | Database | SSL/TLS | Monitoring | Scaling | Use When |
|------|--------|----------|---------|-----------|---------|----------|
| **[dev](modes/dev.md)** | ✅ | PostgreSQL | ❌ | Basic | Single instance | Development server |
| **[staging](modes/staging.md)** | ✅ | PostgreSQL | ✅ | Full | Single instance | Pre-production QA |
| **[prod](modes/prod.md)** | ✅ | PostgreSQL | ✅ | Full | Multi-instance | Live production |
| **[preproduction](modes/preproduction.md)** | ✅ | PostgreSQL | ❌ | Basic | Single instance | CI/CD pipelines |
| **[test](modes/test.md)** | ✅ | In-memory | ❌ | None | Single instance | Automated testing |

### Feature Matrix

| Feature | local-dev | local-minimal | local-full | local-prod | dev | staging | prod | preproduction | test |
|---------|-----------|---------------|------------|------------|-----|---------|------|---------------|------|
| **Backend Hot Reload** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Frontend Hot Reload** | N/A | N/A | ✅* | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **PostgreSQL** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Redis** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **MailHog (Email UI)** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **pgAdmin (DB UI)** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Nginx Reverse Proxy** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **SSL/TLS** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Monitoring (Sentry)** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Real SMTP** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Load Balancing** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |

*Frontend hot reload available when started with `./deploy.sh local --with-frontend`

### Deployment Philosophy

ContraVento follows a **progressive complexity** approach:

```
SQLite Local → Docker Minimal → Docker Full → Dev Server → Staging → Production
  Instant        ~10s            ~20-30s        ~20s         ~40s      ~60s
  Zero config    Minimal         Complete       Moderate     Full      Full HA
```

**Core Principles:**
1. **Development Speed First**: Start simple (SQLite), add complexity as needed
2. **Environment Parity**: Staging mirrors production exactly (same Docker Compose)
3. **Docker Compose Primary**: All modes use Docker Compose (except local-dev)
4. **Security by Default**: Production-grade security from staging onwards

---

## Deployment Modes

### Local Development Modes

#### 1. [Local Dev (SQLite)](modes/local-dev.md)
**Command**: `./run-local-dev.sh` or `.\run-local-dev.ps1`

**Perfect for**: Daily development, quick prototyping

**Stack**:
- SQLite database (file-based)
- FastAPI backend with hot reload
- No Docker required

**Key Features**:
- ⚡ Instant startup (no Docker overhead)
- 🎯 Zero configuration (auto-setup)
- 🔄 Hot reload on code changes
- 💻 Cross-platform (Windows/Mac/Linux)

---

#### 2. [Local Minimal (Docker + PostgreSQL)](modes/local-minimal.md)
**Command**: `./deploy.sh local-minimal`

**Perfect for**: Testing PostgreSQL-specific features

**Stack**:
- PostgreSQL 16
- FastAPI backend with hot reload

**Key Features**:
- 🐘 Real PostgreSQL (production parity)
- ⚡ Lightweight (~500 MB RAM)
- 🔄 Fast startup (~10 seconds)
- ✅ Test users auto-created

---

#### 3. [Local Full (Complete Stack)](modes/local-full.md)
**Command**: `./deploy.sh local` or `./deploy.sh local --with-frontend`

**Perfect for**: Email/auth features, full-stack testing

**Stack**:
- PostgreSQL 16
- Redis 7
- FastAPI backend with hot reload
- MailHog (email testing UI)
- pgAdmin (database UI)
- Optional: Vite frontend with hot reload

**Key Features**:
- 📧 MailHog UI at http://localhost:8025
- 🖥️ pgAdmin at http://localhost:5050
- 💾 Redis for caching/sessions
- 🔄 Frontend hot reload (when enabled)

---

#### 4. [Local Prod (Production Build Testing)](modes/local-prod.md)
**Command**: `./deploy-local-prod.sh` or `.\deploy-local-prod.ps1`

**Perfect for**: Testing production builds locally

**Stack**:
- PostgreSQL 16
- Redis 7
- FastAPI backend (development mode)
- **Nginx** serving optimized frontend (Dockerfile.prod)
- MailHog, pgAdmin

**Key Features**:
- 🚀 Production frontend build (minified, optimized)
- 🌐 Nginx reverse proxy (`/api/*` → backend)
- 📦 Static asset caching
- 🔒 Security headers testing

**⚠️ Note**: Frontend has NO hot reload (requires rebuild)

---

### Server Deployment Modes

#### 5. [Dev (Development/Integration Server)](modes/dev.md)
**Command**: `./deploy.sh dev`

**Perfect for**: Shared development server, integration testing

**Stack**:
- PostgreSQL 16
- Redis 7
- FastAPI backend
- Nginx reverse proxy
- Real SMTP (SendGrid/AWS SES)

**Key Features**:
- 🌐 Nginx at port 80
- 📧 Real email sending (not MailHog)
- 🔄 Backend hot reload
- 🔗 Shared environment for team

---

#### 6. [Staging (Pre-Production)](modes/staging.md)
**Command**: `./deploy.sh staging`

**Perfect for**: Final QA testing before production

**Stack**:
- PostgreSQL 16 (persistent volume)
- Redis 7
- FastAPI backend (production mode)
- Nginx with SSL/TLS
- Real SMTP
- Sentry monitoring
- Cloudflare Turnstile

**Key Features**:
- 🔒 SSL/TLS with Let's Encrypt
- 📊 Sentry error tracking
- 🚨 Production-grade logging
- 🔍 Mirrors production exactly

**⚠️ Important**: Staging is a **production mirror** - use for final validation only

---

#### 7. [Production (Live Users)](modes/prod.md)
**Command**: `./deploy.sh prod`

**Perfect for**: Serving real users in production

**Stack**:
- PostgreSQL 16 (HA with replication)
- Redis 7 (master-replica)
- FastAPI backend (multi-instance)
- Nginx with SSL/TLS
- Real SMTP
- Sentry monitoring
- Cloudflare Turnstile

**Key Features**:
- 🔄 Load balancing (3+ backend instances)
- 💾 Database backups (automated)
- 🔒 SSL/TLS required
- 📊 Comprehensive monitoring
- 🚨 Auto-scaling

**⚠️ Critical**: Follow [Production Checklist](guides/production-checklist.md) before deploying

---

#### 8. [Preproduction (CI/CD)](modes/preproduction.md)
**Command**: `./deploy.sh preproduction`

**Perfect for**: Jenkins CI/CD pipelines, automated deployments

**Stack**:
- PostgreSQL 16
- Redis 7
- FastAPI backend
- Nginx reverse proxy
- Real SMTP

**Key Features**:
- 🤖 Jenkins integration
- 🔧 Automated testing
- 📦 Build artifacts
- 🔄 Auto-deploy on merge

---

#### 9. [Test (Automated Testing)](modes/test.md)
**Command**: `./deploy.sh test`

**Perfect for**: pytest integration tests, CI/CD pipelines

**Stack**:
- In-memory database (fast)
- Minimal FastAPI backend
- No Nginx, no Redis

**Key Features**:
- ⚡ Ultra-fast startup
- 🧪 Isolated test environment
- 🔄 Clean state per run
- 💾 No persistent storage

---

## Guides

Cross-cutting guides for all deployment modes:

### Getting Started
- 📘 **[Getting Started Guide](guides/getting-started.md)** - Your first deployment from zero to running
- 🔑 **[Environment Variables](guides/environment-variables.md)** - Complete .env configuration reference
- 🐳 **[Docker Compose Architecture](guides/docker-compose-guide.md)** - Understanding multi-file composition

### Operations
- 🎨 **[Frontend Deployment](guides/frontend-deployment.md)** - React/Vite build and deployment
- 🗄️ **[Database Management](guides/database-management.md)** - Migrations, seeds, backups
- 🔧 **[Troubleshooting](guides/troubleshooting.md)** - Common issues and solutions
- 🔧 **[Preproduction Parameterization](modes/preproduction-parameterization.md)** - Complete variable reference, CI/CD integration, multiple instances

### Production
- ✅ **[Production Checklist](guides/production-checklist.md)** - Pre-deployment validation

---

## Migration from Old Documentation

This unified documentation replaces the following files (archived as of 2026-01-25):

| Old File | New Location | Status |
|----------|--------------|--------|
| `QUICK_START.md` (root) | `docs/deployment/README.md` (this file) | ⚠️ Redirect in place |
| `backend/docs/DEPLOYMENT.md` | Split into `modes/*.md` | ⚠️ Redirect in place |
| `backend/docs/ENVIRONMENTS.md` | `guides/environment-variables.md` | ⚠️ Redirect in place |
| `docs/LOCAL_DEV_GUIDE.md` | `modes/local-dev.md` | Archived |
| `LOCAL_PROD_TESTING.md` | `modes/local-prod.md` | Archived |
| `DOCKER_COMPOSE_GUIDE.md` | `guides/docker-compose-guide.md` | Archived |
| `DOCKER_COMPOSE_ENVIRONMENTS.md` | `modes/preproduction.md` | Archived |

**Archived versions** can be found in `docs/deployment/archive/v0.3.0-*.md` for reference.

### Migration Status

This documentation unification is an ongoing project. For complete migration plan, implementation status, and phased approach, see:

**[📋 Migration Plan](MIGRATION_PLAN.md)** - Detailed 6-phase plan with current progress (31% completed)

**Current Status** (2026-01-25):

- ✅ Phase 1: Structure base (100%)
- 🔄 Phase 2: Mode documentation (44% - 4/9 modes completed)
- ⏳ Phase 3: Cross-cutting guides (0%)
- ⏳ Phase 4: Archive old docs (0%)
- ✅ Phase 5: Update references (100%)
- ⏳ Phase 6: Final validation (0%)

---

## Quick Links

### For Developers
- [Start coding NOW (fastest)](modes/local-dev.md#quick-start)
- [Run with PostgreSQL](modes/local-minimal.md)
- [Test emails locally](modes/local-full.md#mailhog-usage)
- [Debug frontend build issues](modes/local-prod.md#troubleshooting)

### For DevOps
- [Deploy to development server](modes/dev.md)
- [Set up staging environment](modes/staging.md)
- [Production deployment checklist](guides/production-checklist.md)
- [Database backup/restore](guides/database-management.md#backups)

### For QA
- [Run integration tests](modes/test.md)
- [Staging validation workflow](modes/staging.md#qa-workflow)
- [Known issues and workarounds](guides/troubleshooting.md)

---

## Contributing

Found an issue or want to improve the documentation?

1. Check [Troubleshooting Guide](guides/troubleshooting.md) first
2. Open an issue on GitHub with tag `documentation`
3. Submit a PR following the template in each `modes/*.md` file

---

**Need help?** Open an issue on GitHub or reach out to the team.

**Last Updated**: 2026-01-25
