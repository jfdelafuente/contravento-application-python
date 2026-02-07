# ContraVento Documentation Hub

Welcome to the ContraVento documentation! This is your central navigation point for all documentation.

**Quick Links**: [Deployment](#deployment) • [User Guides](#user-guides) • [API](#api-reference) • [Architecture](#architecture) • [Testing](#testing)

---

## 🤔 What Are You Looking For?

### Decision Tree

```
┌────────────────────────────────────────────────────────────────┐
│ What do you want to do?                                       │
└────────────────────────────────────────────────────────────────┘
         │
         ├─ 🚀 Run ContraVento locally
         │   → [Deployment Documentation](#deployment)
         │   → Quick: ./run-local-dev.sh
         │
         ├─ 📖 Use ContraVento features (end-user)
         │   → [User Guides](#user-guides)
         │   → Create trips, upload GPX, follow users
         │
         ├─ 💻 Integrate with the API
         │   → [API Reference](#api-reference)
         │   → Endpoints, authentication, contracts
         │
         ├─ 🏗️ Understand the architecture
         │   → [Architecture](#architecture)
         │   → Backend, frontend, database, integrations
         │
         ├─ 🧪 Write tests
         │   → [Testing](#testing)
         │   → Unit, integration, E2E, manual QA
         │
         ├─ 🔍 Learn about a specific feature
         │   → [Features](#features)
         │   → Travel diary, GPS routes, social network
         │
         ├─ 🛠️ Set up development environment
         │   → [Development](#development)
         │   → Getting started, TDD workflow, troubleshooting
         │
         └─ 📊 Deploy to production / monitor
             → [Operations](#operations)
             → Monitoring, backups, incident response
```

---

## 📚 Documentation Categories

### 🚀 Deployment

**Run ContraVento in different environments (local, staging, production)**

📘 **[Deployment Documentation](deployment/README.md)**

**Quick Start**:
```bash
# Fastest way to start coding (no Docker, SQLite)
./run-local-dev.sh --setup  # First time only
./run-local-dev.sh          # Start developing
```

**Contents**:
- ✅ **9 Deployment Modes**: local-dev, local-minimal, local-full, local-prod, dev, staging, prod, preproduction, test
- ✅ **7 Cross-Cutting Guides**: Getting started, troubleshooting, environment variables, Docker Compose, frontend deployment, database management, production checklist
- ✅ **Decision Tree**: Find your deployment mode in <2 minutes
- ✅ **Archive**: Old deployment docs preserved with redirects

**Status**: ✅ **Complete** (Feature 016 - 97% complete, peer review pending)

---

### 📖 User Guides

**Learn how to use ContraVento features (end-user documentation)**

📘 **[User Guides Documentation](user-guides/README.md)**

**I want to...**:
- 🆕 **Get started** → [Getting Started](user-guides/getting-started.md)
- 📝 **Create my first trip** → [Creating Trips](user-guides/trips/creating-trips.md)
- 🗺️ **Upload a GPX file** → [Uploading GPX](user-guides/trips/uploading-gpx.md)
- 📸 **Add photos to trips** → [Adding Photos](user-guides/trips/adding-photos.md)
- 👥 **Follow other cyclists** → [Following Users](user-guides/social/following-users.md)
- 🔍 **Discover new trips** → [Public Feed](user-guides/social/public-feed.md)
- 🗺️ **Understand GPS maps** → [GPS Routes & Maps](user-guides/maps/gps-routes.md)

**Contents**:
- 🎯 **Getting Started**: Registration, login, platform tour, first trip
- 🚴 **Trips**: Creating (4-step wizard), uploading GPX, adding photos (max 20), draft vs published
- 👥 **Social**: Following users, public feed (filters, tags, search), comments, likes
- 🗺️ **Maps**: GPS routes visualization, interactive maps, location markers

**Status**: ✅ **Complete** (Phase 4 - 8 guides created)

---

### 💻 API Reference

**Integrate with the ContraVento API (developers, mobile apps)**

📘 **[API Documentation](api/README.md)**

**Base URL**: `http://localhost:8000` (dev) | `https://api.contravento.com` (prod)

**Quick Example**:
```bash
# Authenticate
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# Use access token
curl -X GET http://localhost:8000/trips \
  -H "Authorization: Bearer <access_token>"
```

**Contents**:
- 🔐 **[Authentication](api/authentication.md)**: JWT tokens, login, register
- 📍 **Endpoint Docs**: [Auth](api/endpoints/auth.md), [Trips](api/endpoints/trips.md), [Users](api/endpoints/users.md), [Social](api/endpoints/social.md), [GPX](api/endpoints/gpx.md)
- 📝 **[OpenAPI Contracts](api/contracts/)**: YAML schemas for all endpoints
- 📬 **[Postman Collections](api/postman/)**: Pre-built API test collections
- 🧪 **[Testing Guides](api/testing/)**: Manual testing, Postman setup

**Status**: ✅ **Complete** (Phase 2 - 18 files created)

---

### 🏗️ Architecture

**Understand the technical design and patterns**

📘 **[Architecture Documentation](architecture/README.md)**

**Topics**:
- **Backend**: Clean architecture, service layer, database strategy, security
- **Frontend**: Component patterns, state management, routing
- **Data Model**: Entity relationships, schemas (SQLite + PostgreSQL), migrations
- **Integrations**: GPX processing, reverse geocoding, photo storage

**Key Patterns**:
```python
# Dependency Injection
@router.get("/trips")
async def get_trips(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    trips = await TripService.get_user_trips(db, current_user)
    return trips
```

**Status**: 🔄 **In Progress** (Phase 5 - Foundation created)

---

### 🧪 Testing

**Testing strategies and guides (developers, QA engineers)**

📘 **[Testing Documentation](testing/README.md)**

**Test Pyramid**:
```
   ┌───────┐
   │  E2E  │  ← Few (Playwright)
   ├───────┤
   │ Integ │  ← Some (pytest + FastAPI TestClient)
   ├───────┤
   │ Unit  │  ← Many (pytest + Vitest)
   └───────┘
```

**Contents**:
- 🧪 **Backend**: Unit tests, integration tests, contract tests, performance tests
- ⚛️ **Frontend**: Component tests (Vitest), E2E tests (Playwright), accessibility (axe)
- 📝 **Manual QA**: Trips testing, GPS testing, social testing, accessibility testing
- 🤖 **CI/CD**: GitHub Actions, quality gates (coverage ≥90%, linting, type checking)

**Coverage Requirement**: ≥90% for all modules

**Status**: ✅ **Complete** (Phase 3 - 10 files created, consolidated from 25K+ lines)

---

### 🔍 Features

**Deep-dive documentation for all implemented features**

📘 **[Features Documentation](features/README.md)**

**Completed Features**:
- ✅ **Travel Diary**: Document trips with photos, tags, locations
- ✅ **GPS Routes**: GPX upload, route visualization, elevation profiles
- ✅ **Social Network**: Follow users, comments, likes (in progress)
- ✅ **User Profiles**: Profile management, stats, achievements
- ✅ **Reverse Geocoding**: Location naming from coordinates
- ✅ **Public Feed**: Discover trips, filters, search
- ✅ **Stats Integration**: Automatic stats updates
- ✅ **Cycling Types**: Dynamic type management
- ✅ **Elevation Profile**: Interactive elevation charts

**Status**: ⏳ **Planned** (Phase 6 - Week 6)

---

### 🛠️ Development

**Developer workflows and best practices**

📘 **[Development Documentation](development/README.md)**

**New Developer?** Start here:
1. [Getting Started](development/getting-started.md) - Setup from zero
2. [TDD Workflow](development/tdd-workflow.md) - Test-first development
3. [Code Quality](development/code-quality.md) - Linting, formatting, type checking

**Tools**:
- **[Scripts](development/scripts/)**: Analysis, seeding, user management
- **[Troubleshooting](development/troubleshooting/)**: Common issues, Docker, database, email

**Daily Workflow**:
```bash
./run-local-dev.sh                 # Start backend
poetry run pytest --cov=src        # Run tests (≥90% coverage)
poetry run black src/ tests/       # Format code
poetry run ruff check src/         # Lint
```

**Status**: ⏳ **Planned** (Phase 6 - Week 6)

---

### 📊 Operations

**Production operations, monitoring, and maintenance**

📘 **[Operations Documentation](operations/README.md)**

**Topics**:
- 📊 **Monitoring**: Prometheus, Grafana, logging
- 💾 **Backups**: S3 backups every 6 hours, restore procedures
- 🗄️ **Database Management**: Production DB admin, scaling
- 🚨 **Incident Response**: Runbooks, severity levels (P0/P1/P2)

**Deployment Checklist**: [Production Checklist](deployment/guides/production-checklist.md)

**Status**: ⏳ **Planned** (Phase 6 - Week 6)

---

## 🗂️ Archive

Old documentation preserved for reference:

📘 **[Documentation Archive](archive/README.md)**

**Archived Documentation**:
- ✅ **Deployment Docs (v0.3.0)**: QUICK_START.md, DEPLOYMENT.md, ENVIRONMENTS.md (archived 2026-01-28)
- ⏳ **Development Notes**: SESSION_*.md, PHASE*.md (planned Phase 7)
- ⏳ **Test Results**: Historical test reports (planned Phase 7)

**Policy**: Preserve, don't delete. See [Archive README](archive/README.md) for archival policy.

---

## 📋 Documentation Status

### By Phase (Consolidation Plan)

| Phase | Description | Status | Week |
|-------|-------------|--------|------|
| **Phase 1** | Foundation (directory structure) | ✅ **Complete** | Week 1 |
| **Phase 2** | API Documentation | ✅ **Complete** | Week 2 |
| **Phase 3** | Testing Consolidation | ✅ **Complete** | Week 3 |
| **Phase 4** | User Guides | ✅ **Complete** | Week 4 |
| **Phase 5** | Architecture | ⏳ Planned | Week 5 |
| **Phase 6** | Features & Development | ⏳ Planned | Week 6 |
| **Phase 7** | Archive & Cleanup | ⏳ Planned | Week 7 |
| **Phase 8** | Validation & Polish | ⏳ Planned | Week 8 |

### By Category

| Category | Structure | Content | Status |
|----------|-----------|---------|--------|
| **Deployment** | ✅ Complete | ✅ Complete (Feature 016) | ✅ 97% |
| **User Guides** | ✅ Complete | ✅ Complete (Phase 4) | ✅ 100% |
| **API** | ✅ Complete | ✅ Complete (Phase 2) | ✅ 100% |
| **Architecture** | ✅ Complete | 🔄 Phase 5 | 🔄 55% |
| **Testing** | ✅ Complete | ✅ Complete (Phase 3) | ✅ 100% |
| **Features** | ✅ Complete | ⏳ Phase 6 | 🔄 25% |
| **Development** | ✅ Complete | ⏳ Phase 6 | 🔄 25% |
| **Operations** | ✅ Complete | ⏳ Phase 6 | 🔄 25% |
| **Archive** | ✅ Complete | ✅ Complete | ✅ 100% |

---

## 🔍 Search Tips

**GitHub Search**:
- Search for "deployment" → `docs/deployment/`
- Search for "API" → `docs/api/`
- Search for "test" → `docs/testing/`

**Local Search** (grep):
```bash
# Search across all docs
grep -r "keyword" docs/

# Search specific category
grep -r "keyword" docs/api/
```

**IDE Navigation**:
- Use Ctrl+P (VS Code) to quickly open docs by filename
- Use Ctrl+Shift+F to search across all documentation

---

## 🤝 Contributing

Found an issue or want to improve documentation?

See **[Documentation Contributing Guide](CONTRIBUTING.md)** (to be created in Phase 8)

---

## 📞 Quick Links by Role

### For Developers

- 🚀 **[Start Coding](deployment/modes/local-dev.md#quick-start)** - Fastest way to begin
- 🧪 **[Write Tests](testing/README.md)** - Testing strategies
- 🏗️ **[Architecture](architecture/README.md)** - System design
- 💻 **[API Docs](api/README.md)** - API reference

### For End-Users

- 📖 **[User Guides](user-guides/README.md)** - How to use features
- 📝 **[Create Trip](user-guides/trips/creating-trips.md)** - Get started
- 🗺️ **[Upload GPX](user-guides/trips/uploading-gpx.md)** - Add GPS routes

### For DevOps

- 🚀 **[Deploy Staging](deployment/modes/staging.md)** - Pre-production
- ✅ **[Production Checklist](deployment/guides/production-checklist.md)** - Pre-deploy validation
- 📊 **[Monitoring](operations/monitoring.md)** - Observability
- 💾 **[Backups](operations/backups.md)** - Data protection

### For QA

- 🧪 **[Testing](testing/README.md)** - Test strategies
- 📝 **[Manual QA](testing/manual-qa/)** - Manual testing guides
- ✅ **[Staging Validation](deployment/modes/staging.md#qa-workflow)** - QA workflow

---

## 📈 Progress Tracking

**Total Documentation Files**: ~300+ markdown files (baseline)

**Consolidation Goal**: ~150 well-organized files (50% reduction via consolidation)

**Current Phase**: Phase 5 (Architecture) - 🔄 In Progress (Backend complete: 5/9 tasks)

**Next Milestone**: Phase 5 completion (Frontend/integrations/data model docs)

---

## 🗺️ Consolidation Plan

This documentation structure is being built incrementally as part of a comprehensive consolidation effort:

📋 **[Full Consolidation Plan](../.claude/plans/valiant-giggling-grove.md)**

**Goals**:
1. ✅ Eliminate duplicate documentation (testing guides in 5+ locations)
2. ✅ Improve discoverability (find docs in <30 seconds)
3. ✅ Centralize API reference (scattered across backend/docs/api/ and specs/)
4. ✅ Create user-facing guides (currently mixed with development docs)
5. ✅ Establish single source of truth for each topic

**Timeline**: 8 weeks (Phase 1 started 2026-02-06)

---

**Last Updated**: 2026-02-07
**Consolidation Plan**: Phase 5 (Architecture) - In Progress (5/9 tasks complete - Backend ✅)
**Next Phase**: Phase 5 completion (Frontend/integrations) → Phase 6 (Features & Development)
