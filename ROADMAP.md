# ContraVento - Product Roadmap

**Last Updated**: 2026-02-09
**Current Version**: MVP + Core Features
**Active Development Branch**: `develop`

---

## 📊 Progress Overview

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Completed | 12 features | 71% |
| 🚧 In Progress | 2 features | 12% |
| 📋 Planned | 2 features | 12% |
| ❌ Discarded | 2 features | - |

---

## ✅ Completed Features (In Production)

### Core Backend (Authentication & Profiles)

- **[001] User Profiles & Authentication** (`001-user-profiles`)
  - JWT authentication (access + refresh tokens)
  - User registration with email verification
  - Password reset flow
  - User statistics tracking
  - **Status**: ✅ Merged to `develop`
  - **Tech**: FastAPI, SQLAlchemy 2.0, Bcrypt

- **[007] Profile Management** (`007-profile-management`)
  - Update user profile (bio, location, cycling_type)
  - Photo upload with background processing
  - Privacy settings
  - **Status**: ✅ Merged to `develop`
  - **Tech**: FastAPI, Pillow (image processing)

---

### Travel Diary & Trips

- **[002] Travel Diary Backend** (`002-travel-diary`)
  - Trip CRUD operations
  - Draft/Published workflow
  - Photo uploads (max 20 per trip)
  - Tag system with normalization
  - Trip locations (GPS coordinates)
  - **Status**: ✅ Merged to `develop`
  - **Tech**: FastAPI, SQLAlchemy, HTML sanitization

- **[008] Travel Diary Frontend** (`008-travel-diary-frontend`)
  - Trip creation wizard
  - Photo gallery with lightbox
  - Tag filtering
  - Trip detail page
  - Owner-only edit/delete
  - **Status**: ✅ Merged to `develop`
  - **Tech**: React 18, React Hook Form, Zod, react-dropzone

- **[003] GPS Routes** (`003-gps-routes`)
  - GPX file upload and parsing
  - Interactive map with Leaflet
  - Elevation profile with gradient visualization
  - Track simplification (Douglas-Peucker)
  - **Status**: ✅ Merged to `develop` (User Story 3 complete)
  - **Tech**: FastAPI, gpxpy, react-leaflet, Recharts 3.7.0

- **[009] GPS Coordinates** (`009-gps-coordinates`)
  - Add GPS coordinates to trips
  - Multiple locations per trip
  - Map integration
  - **Status**: ✅ Merged to `develop`
  - **Tech**: react-leaflet, Leaflet.js

- **[010] Reverse Geocoding** (`010-reverse-geocoding`)
  - Click map to add location
  - Automatic place name lookup (Nominatim)
  - Drag markers to update coordinates
  - Location name editing
  - **Status**: ✅ Merged to `develop`
  - **Tech**: Nominatim API, lodash.debounce, LRU cache

- **[017] GPS Trip Creation Wizard** (`017-gps-trip-wizard`)
  - 4-step wizard (Mode Selection, GPX Upload, Trip Details, Review)
  - Smart title extraction from GPX files
  - Drag-and-drop file upload
  - Automatic telemetry extraction (distance, elevation, duration)
  - Route statistics display with MetricGroup/MetricCard
  - Map preview in Step 1
  - Atomic trip creation with RouteStatistics
  - POI management (unlimited photos per POI)
  - Trip filters & sorting (date, distance, popularity)
  - E2E test coverage (26 tests)
  - **Status**: ✅ Merged to `develop` (PR #51, #50)
  - **Progress**: 98/105 tasks (93%) - MVP++ Complete
  - **Tech**: React 18, React Hook Form 7.70, react-leaflet 4.2.1, FastAPI, SQLAlchemy 2.0

---

### Frontend Infrastructure

- **[005] Frontend User Profile** (`005-frontend-user-profile`)
  - Login/Register pages
  - Profile page with edit mode
  - Authentication context
  - HttpOnly cookie handling
  - **Status**: ✅ Merged to `develop`
  - **Tech**: React 18, TypeScript 5, Vite, Axios

- **[011] Frontend Deployment** (`011-frontend-deployment`)
  - Production build configuration
  - Nginx integration
  - Environment variable handling
  - **Status**: ✅ Merged to `develop`
  - **Tech**: Vite, Nginx, Docker

---

### Documentation & DevOps

- **[016] Deployment Documentation** (`016-deployment-docs-completion`)
  - Complete deployment guides (local-dev, local-minimal, local-full, dev, staging, prod)
  - Environment variables reference
  - Troubleshooting guides
  - Database management
  - **Status**: ✅ Merged to `develop` (97% complete)
  - **Docs**: [docs/deployment/README.md](docs/deployment/README.md)

- **[001] Testing & QA Suite** (`001-testing-qa`)
  - Unit, integration, contract tests
  - E2E testing setup
  - Coverage requirements (≥90%)
  - **Status**: ✅ Framework established
  - **Tech**: pytest, Playwright

---

## 🚧 In Progress

- **[013] Public Trips Feed** (`013-public-trips-feed`)
  - **Branch**: `remotes/origin/013-public-trips-feed`
  - **Progress**: Unknown
  - **Planned Features**:
    - Browse published trips from all users
    - Filter by tag, distance, difficulty
    - Trip detail view for non-owners
    - Social engagement (likes, comments)
  - **Status**: Feature branch exists remotely
  - **Tech**: React 18, FastAPI

- **[014] Landing Page Inspiradora** (`014-landing-page-inspiradora`)
  - **Branch**: `014-landing-page-inspiradora` (local)
  - **Progress**: Unknown
  - **Planned Features**:
    - Marketing landing page
    - Hero section with CTA
    - Feature highlights
    - User testimonials
  - **Status**: Feature branch exists locally
  - **Tech**: React 18, CSS animations

---

## 📋 Planned (Backlog)

### Social Features

- **[004] Social Network** (`004-social-network`)
  - User following/followers
  - Activity feed
  - Social interactions (likes, comments)
  - Notifications
  - **Priority**: High
  - **Dependencies**: 013-public-trips-feed
  - **Tech**: FastAPI, WebSockets (planned)

---

### Performance & Infrastructure

- **[004] Celery + Redis** (`004-celery-async-tasks`)
  - Asynchronous GPX processing
  - Background photo resizing
  - Email sending queue
  - Task monitoring
  - **Priority**: Medium
  - **Dependencies**: Heavy GPX processing workload
  - **Tech**: Celery, Redis, Flower

---

## ❌ Discarded Features

- **[015] GPX Wizard Integration** (`015-gpx-wizard-integration`)
  - **Reason**: Superseded by 017-gps-trip-wizard (more comprehensive implementation)
  - **Date Discarded**: 2026-01-28
  - **Note**: 017 provides all features of 015 plus enhanced UX and atomic operations

- **[006] Dynamic Dashboard** (`006-dashboard-dynamic`)
  - **Reason**: Feature deprioritized - Core functionality already covered by user profiles and trips
  - **Date Discarded**: 2026-02-09
  - **Note**: Dashboard widgets and statistics are available through existing profile and trips pages. Feature adds complexity without clear user value at current stage.

---

## 🎯 Next Milestones

### Q1 2026 (Current)

- ✅ Complete 017-gps-trip-wizard (DONE - merged)
- 🚧 Complete 013-public-trips-feed (In Progress)
- 🚧 Complete 014-landing-page-inspiradora (In Progress)

### Q2 2026
- Start 004-social-network
- Evaluate need for 004-celery-async-tasks
- Performance optimization (caching, query optimization)

### Future
- Mobile app (React Native or native)
- Real-time notifications (WebSockets)
- Offline-first PWA
- Route recommendations (AI/ML)

---

## 📈 Feature Adoption Tracking

| Feature | Users Engaged | Avg Usage | Top Use Case |
|---------|---------------|-----------|--------------|
| Travel Diary | - | - | Trip documentation |
| GPS Routes | - | - | Route sharing |
| Profile Management | - | - | Photo uploads |

*Note: Metrics to be added once analytics are implemented*

---

## 🚀 Deployment Status

| Environment | Branch | Status | URL |
|-------------|--------|--------|-----|
| **Production** | `main` | 🟢 Live | https://contravento.com |
| **Staging** | `develop` | 🟢 Live | https://staging.contravento.com |
| **Development** | Feature branches | 🟢 Active | http://localhost:8000 |

---

## 📝 Contributing

To propose a new feature:

1. Create spec in `specs/{number}-{feature-name}/`
2. Follow spec template: `spec.md`, `plan.md`, `tasks.md`
3. Use `/speckit.specify` for specification generation
4. Submit for review before implementation

See [CLAUDE.md](CLAUDE.md) for development guidelines.

---

## 📚 Related Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[CLAUDE.md](CLAUDE.md)** - Development guide and recent changes
- **[docs/README.md](docs/README.md)** - Complete documentation hub
- **[docs/features/README.md](docs/features/README.md)** - Feature deep-dives

---

**Maintained by**: Development Team
**Update Frequency**: After each feature completion or milestone
