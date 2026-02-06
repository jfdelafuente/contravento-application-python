# ContraVento - Próximos Pasos

**Última actualización**: 2026-02-06
**Estado actual**: 3 features con trabajo pendiente, ordenadas por prioridad

---

## 📋 Resumen Ejecutivo

| Feature | Prioridad | Estado | Tareas Pendientes | Tiempo Estimado | Bloqueadores |
| ------- | --------- | ------ | ----------------- | --------------- | ------------ |
| ~~**012-typescript-code-quality**~~ | ✅ Completada | 100% | 0 errores | ✅ ~1 hora | Ninguno |
| ~~**017-gps-trip-wizard**~~ | ✅ Completada | 93% (98/105) | 7 tareas opcionales | ✅ ~3 días | Ninguno |
| ~~**011-frontend-deployment**~~ | ✅ Completada | 100% (70/70) | 0 tareas | ✅ ~15 min | Ninguno |
| ~~**015-gpx-wizard-integration**~~ | ❌ Descartada | N/A | Supersedida por F017 | N/A | Feature 017 ya implementa esto |
| **016-deployment-docs** | 🟡 Media | 31% (9/29) | 20 tareas | 5-8 días | Ninguno |
| **014-landing-page** | 🟡 Media | 62% (44/71) | 27 tareas | 1-2 días | Ninguno |
| **006-dashboard-dynamic** | 🟢 Baja | 0% | 72 tareas | 3-4 días | Ninguno |
| **004-celery-async-tasks** | 🟢 Baja | 0% | TBD | 2-3 días | Ninguno |

**Recomendación**: Feature 016 (Deployment Docs) o Feature 014 (Landing Page) según prioridad de negocio

---

## ✅ FEATURES COMPLETADAS

### Feature 017: GPS Trip Creation Wizard ✅

**Branch**: `017-gps-trip-wizard` (pendiente merge a develop)

**Estado**: ✅ **93% COMPLETADA** (98/105 tareas) - MVP++ Ready for Production

**Fecha de cierre**: 2026-02-06

**Tiempo total**: ~3 días (~24 horas de desarrollo)

#### Resumen de Logros

- ✅ 60 commits implementando wizard completo de 4 pasos
- ✅ Frontend: 6 user stories (mode selection, GPX upload, details, map, POI, publish)
- ✅ Backend: GPX processing, route statistics, atomic transactions
- ✅ 26 E2E tests + unit tests con TDD
- ✅ Smart-Title cleaning, telemetry extraction, privacy controls
- ✅ Map preview en Step 1, complete telemetry en Step 4 Review
- ✅ Support para 6 trip photos + unlimited POI photos
- ✅ Optimized 4-step wizard (reducido de 5 pasos, 20% más rápido)
- ✅ Trip filters, sorting (date, distance, popularity)
- ✅ Integration tests para photo & draft listing pasando
- ✅ 21 mypy type errors resueltos (backend type-safe)
- ✅ CI/CD smoke tests configurados (Docker build validation)

#### Fases Completadas (9/10)

1. ✅ Setup & Prerequisites (8/8 tasks)
2. ✅ Foundational Services (12/12 tasks)
3. ✅ US1: Mode Selection Modal (10/10 tasks)
4. ✅ US2: GPX Upload & Processing (18/18 tasks)
5. ✅ US3: Trip Details + Difficulty (14/14 tasks)
6. ✅ US6: Publish Trip (Atomic) (10/10 tasks)
7. ✅ US4: Map Visualization (8/8 tasks)
8. ✅ US5: POI Management (10/10 tasks)
9. ⏸️ Phase 9: Polish & Cross-Cutting (0/7 tasks - opcional)
10. ✅ Post-MVP: Wizard UX Optimization (8/8 tasks)

#### Últimos Commits Relevantes

1. 81fecd2 - fix(ci): update frontend smoke test to avoid nginx config validation
2. 5a07e69 - fix(ci): use locally built images for smoke tests
3. 947e281 - fix: resolve all mypy type checking errors (21 errors across 4 files)
4. 070afe7 - feat: add trip filters and sort functionality
5. 746db84 - feat: add GPX trip edit page with privacy and 6-photo limit

#### Pendiente para Merge

- [ ] Crear Pull Request a develop (60 commits)
- [ ] Review de código
- [ ] Validación final de CI/CD
- [ ] Merge a develop (trigger Docker Hub push)
- [ ] Opcional: 7 tareas de Phase 9 (polish)

---

### Feature 012: TypeScript Code Quality ✅

**Branch**: `develop` (merged from `012-typescript-code-quality`)

**Estado**: ✅ **100% COMPLETADA** (0 errores TypeScript)

**Fecha de cierre**: 2026-01-28

**Tiempo total**: ~1 hora (bajo el estimado de 2-4 horas)

#### Resumen de Logros

- ✅ 96 errores TypeScript resueltos en 7 commits
- ✅ Production build pasa con 0 errores (37.53s)
- ✅ Build size: ~1.06 MB uncompressed, ~360 KB gzipped
- ✅ Todas las métricas cumplidas (AC-001 a AC-006)
- ✅ Feature 011 T067 DESBLOQUEADA

#### Commits

1. cca0483 - Import fixes (APIError → ApiError)
2. b150573 - Remove unused imports
3. ebb94a3 - Property mismatches + AxiosError typing
4. 56146a4 - RegisterForm + authService transform
5. d42e364 - Unused variables batch 1
6. f2fa7ec - LoginPage unused login removal
7. 1129057 - Add missing dependencies (clsx, tailwind-merge)

---

### Feature 011: Frontend Deployment Integration ✅

**Branch**: `develop` (merged from `011-frontend-deployment`)

**Estado**: ✅ **100% COMPLETADA** (70/70 tareas)

**Fecha de cierre**: 2026-02-06

**Tiempo total**: ~15 minutos (validación final T063)

#### Resumen de Logros

- ✅ 4 modos de deployment configurados y validados:
  - **SQLite Local** (no Docker) - startup <30s ✅
  - **Docker Minimal** (PostgreSQL + Backend + Frontend) - startup <60s ✅
  - **Docker Full** (MailHog, Redis, pgAdmin) - startup <90s ✅
  - **Production Builds** (staging/prod con Nginx) - optimized builds ✅
- ✅ Scripts de deployment para Linux/Mac (`.sh`) y Windows (`.ps1`)
- ✅ Configuración de ambiente para dev, staging y production
- ✅ Frontend con Vite + proxy configurado (no CORS errors)
- ✅ Hot Module Replacement (HMR) <2s
- ✅ Production build reduce 66% tamaño (~360 KB gzipped)
- ✅ Nginx configurado con cache headers y SPA routing
- ✅ Docker Compose para todos los ambientes
- ✅ Documentación completa en `quickstart.md`

#### Fases Completadas (7/7)

1. ✅ Setup (8/8 tasks) - Environment files y Dockerfiles
2. ✅ Foundational (4/4 tasks) - Vite config y build scripts
3. ✅ US1: SQLite Local (10/10 tasks) - Development workflow
4. ✅ US2: Docker Minimal (10/10 tasks) - PostgreSQL testing
5. ✅ US3: Docker Full (10/10 tasks) - Complete environment
6. ✅ US4: Production Builds (15/15 tasks) - Staging/Prod deployment
7. ✅ Polish & Cross-Cutting (13/13 tasks) - Docs & validation (T063 ✅)

---

## ❌ FEATURES DESCARTADAS

### Feature 015: GPX Wizard Integration ❌

**Estado**: ❌ **DESCARTADA** - Supersedida por Feature 017

**Fecha de descarte**: 2026-02-06

**Razón**: Feature 017 (GPS Trip Creation Wizard) implementó una solución superior que incluye y supera los objetivos de Feature 015.

#### ¿Por qué se descartó?

Feature 015 pretendía agregar un modal post-creación para subir GPX después de crear un trip manual. Sin embargo, **Feature 017 implementó un wizard completo de 4 pasos** que ofrece una experiencia mucho mejor:

**Lo que Feature 015 proponía**:
- ✅ Modal post-creación para subir GPX
- ✅ Flujo: Crear trip manual → Modal GPX opcional

**Lo que Feature 017 implementó (superior)**:
- ✅ **Mode Selection**: Usuario elige GPS o Manual desde el inicio
- ✅ **Wizard optimizado**: 4 pasos con GPX upload integrado en Step 1
- ✅ **Smart-Title cleaning**: Extracción automática de título desde GPX
- ✅ **Telemetry extraction**: Distancia, elevación, gradiente automáticos
- ✅ **Map preview**: Vista previa inmediata del track GPS
- ✅ **POI management**: Agregar puntos de interés con photos
- ✅ **Atomic transaction**: Trip + GPX + RouteStatistics en una sola operación

#### Ventajas de Feature 017 sobre Feature 015

1. **Discoverability superior**: Usuario ve opción GPS desde el inicio (no después de crear)
2. **Mejor UX**: Flujo unificado desde el principio, no como afterthought
3. **Más funcionalidades**: Telemetría automática, POIs, mapas, etc.
4. **Production-ready**: 26 E2E tests, type-safe, CI/CD smoke tests

**Conclusión**: Feature 017 hace que Feature 015 sea innecesaria y obsoleta.

---

## 🟡 PRIORIDAD MEDIA

### Feature 016: Complete Deployment Documentation

**Branch**: `016-deployment-docs-completion` (specs creadas)

**Estado**: 🔄 **31% completo** (9/29 tareas)

**Prioridad**: 🟡 **Media** (documentación & DX)

**Tiempo restante**: 5-8 días (1-1.5 semanas)

**Bloqueadores**: Ninguno

#### Descripción Feature 016

Completar la consolidación de documentación de deployment iniciada el 2026-01-25. Unifica 10+ archivos dispersos en un directorio `docs/deployment/` con estructura consistente.

#### Estado Actual Feature 016

**Completado**:

- ✅ Phase 1 (Base Structure): 100% - README.md con decision tree
- ✅ Phase 2 (Document Modes): 44% - 4/9 modos (local-dev, local-minimal, local-full, local-prod)
- ✅ Phase 5 (Update References): 100% - CLAUDE.md, scripts, GitHub actualizados

**Documentación creada**: ~4,214 líneas en 4 archivos de modos locales

**Pendiente**:

- ⏳ Phase 2 (Document Modes): 56% - 5 modos server pendientes
- ⏳ Phase 3 (Create Guides): 0% - 7 guías cross-cutting
- ⏳ Phase 4 (Archive): 0% - Archivar docs antiguos
- ⏳ Phase 6 (Validation): 0% - Validación final

#### Tareas Pendientes Feature 016 (20 de 29)

**Phase 2: Document Modes** (5 tareas - T008-T012)

```bash
# Server modes (dev, staging, prod, preproduction, test)
# Plantilla: 8 secciones (Overview → Related Modes)
# Fuente: backend/docs/DEPLOYMENT.md

T008 - modes/dev.md              # Development server
T009 - modes/staging.md          # Pre-production
T010 - modes/prod.md             # Production
T011 - modes/preproduction.md    # CI/CD
T012 - modes/test.md             # Automated testing
```

**Phase 3: Create Guides** ⭐ **HIGHEST PRIORITY** (7 tareas - T013-T019)

```bash
# Cross-cutting guides (mayor valor para developers)

T013 - guides/getting-started.md        # Universal onboarding ⭐ START HERE
T014 - guides/environment-variables.md  # Consolidar ENVIRONMENTS.md
T015 - guides/troubleshooting.md        # Common problems ⭐ HIGH PRIORITY
T016 - guides/docker-compose-guide.md   # Compose patterns
T017 - guides/frontend-deployment.md    # Frontend-specific
T018 - guides/database-management.md    # DB operations
T019 - guides/production-checklist.md   # Pre-deploy checklist
```

**Phase 4: Archive** (4 tareas - T020-T023)

```bash
T020 - Archive QUICK_START.md → archive/
T021 - Archive DEPLOYMENT.md → archive/
T022 - Archive ENVIRONMENTS.md → archive/
T023 - Create redirects to new docs
```

**Phase 6: Validation** (4 tareas - T028-T031)

```bash
T028 - Test navigation flow (all links work)
T029 - Verify commands work (copy-paste validation)
T030 - Test search/discoverability (find docs easily)
T031 - Peer review (at least 1 reviewer approval)
```

#### Estrategia de Implementación Feature 016

**Orden recomendado**:

1. **T013-T015**: Guides (getting-started, troubleshooting, environment-variables) - Highest value
2. **T008-T012**: Server modes - Completar documentación de modos
3. **T016-T019**: Remaining guides - Completar guías
4. **T020-T023**: Archive old docs - Cleanup
5. **T028-T031**: Validation - Final checks

**Parallel work** (si hay 2 developers):

- Developer A: Phase 3 (Guides) - 2-3 días
- Developer B: Phase 2 (Modes) - 2-3 días
- Both: Phase 4 + 6 together - 2 días

#### Templates to Follow Feature 016

**Para Modes** (`modes/*.md`):

```markdown
# [Mode Name] Deployment

## Overview
- When to use this mode
- Typical use cases

## Prerequisites
- Required software
- Minimum hardware

## Quick Start
- Commands to get running
- Access URLs
- Default credentials

## Configuration
- Environment variables
- docker-compose.yml reference

## Usage
- Common commands
- Typical workflows

## Architecture
- Stack components
- Ports and networking

## Troubleshooting
- Common problems
- Solutions

## Related Modes
- Progression path
- Links to related modes
```

**Para Guides** (`guides/*.md`):

```markdown
# [Guide Title]

## Purpose
- What this guide covers
- Who should read it

## [Section 1]
- Content organized by topic

## [Section 2]
- Use tables, code blocks, lists

## Common Pitfalls
- What to avoid

## See Also
- Links to related modes/guides
```

#### Quality Checklist Feature 016

**Para Modes**:

- [ ] Follows 8-section template
- [ ] All commands tested
- [ ] URLs verified (ports, endpoints)
- [ ] Troubleshooting section has ≥3 issues
- [ ] Related Modes section links ≥2 modes

**Para Guides**:

- [ ] Clear purpose statement
- [ ] Organized by topic
- [ ] Examples for all commands
- [ ] Links to relevant modes
- [ ] "See Also" section at end

**General**:

- [ ] English language (no Spanish)
- [ ] Professional tone (concise, example-driven)
- [ ] Markdown lint clean
- [ ] Links relative (no absolute paths)

#### Recursos Feature 016

- **Especificación**: `specs/016-deployment-docs-completion/spec.md`
- **Tasks**: `specs/016-deployment-docs-completion/tasks.md`
- **Quick Start**: `specs/016-deployment-docs-completion/README.md`
- **Migration Plan**: `docs/deployment/MIGRATION_PLAN.md`
- **Master Index**: `docs/deployment/README.md`

#### Criterios de Aceptación Feature 016

- [ ] 17 archivos de documentación (9 modes + 7 guides + 1 README)
- [ ] ~12,000 líneas de documentación en inglés
- [ ] 100% template compliance
- [ ] Zero broken links
- [ ] Peer review approval

---

### Feature 014: Landing Page Inspiradora - Polish & Validation

**Branch**: `014-landing-page-inspiradora` (merged a develop)

**Estado**: 🔄 **62% completo** (44/71 tareas)

**Prioridad**: 🟡 **Media** (polish para producción)

**Tiempo restante**: 1-2 días

**Bloqueadores**: Ninguno

#### Descripción Feature 014

Completar Phase 8 (Polish & Cross-Cutting Concerns) para tener la landing page lista para producción.

#### Estado Actual Feature 014

**Completado**:

- ✅ Setup (Phase 1): 8/8 tareas
- ✅ Foundational (Phase 2): 3/3 tareas
- ✅ User Story 1 (Hero + Manifesto): 12/12 tareas
- ✅ User Story 2 (Value Pillars): 5/5 tareas
- ✅ User Story 3 (How It Works): 5/5 tareas
- ✅ User Story 4 (CTA): 6/6 tareas
- ✅ User Story 5 (Footer): 5/5 tareas

**Tests**: 172/172 unit tests passing (100% coverage)

#### Tareas Pendientes Feature 014: Phase 8 - Polish (27 tareas)

**1. Responsive Design & Accessibility** (6 tareas)

```bash
T045 - Probar/refinar estilos móviles (< 768px)
T046 - Probar/refinar estilos tablet (768-1024px)
T047 - Verificar contraste WCAG AA
       # terracota: 4.8:1, verde bosque: 15.2:1, gris carbón: 9.7:1
T048 - Agregar ARIA labels y HTML semántico
T049 - Verificar navegación por teclado (Tab, Enter)
T050 - Agregar alt text a todas las imágenes
```

**2. Performance Optimization** (5 tareas)

```bash
T051 - Lighthouse audit
       # Target: LCP < 2.5s, FID < 100ms, CLS < 0.1
T052 - Analizar bundle size (< 500KB inicial)
T053 - Lazy loading para imágenes below-the-fold
T054 - Preload fuentes críticas (Playfair Display)
T055 - Verificar hero image WebP + JPG fallback
```

**3. Cross-Browser Testing** (6 tareas)

```bash
T056 - Chrome (últimas 2 versiones)
T057 - Firefox (últimas 2 versiones)
T058 - Safari macOS (últimas 2 versiones)
T059 - Edge (últimas 2 versiones)
T060 - Safari iOS (dispositivo real)
T061 - Chrome Android (dispositivo real)
```

**4. E2E Testing** (2 tareas)

```bash
T062 - Test E2E: authenticated user auto-redirect
T063 - Test E2E: mobile responsive behavior
```

**5. SEO & Meta Tags** (2 tareas - 1 completa)

```bash
✅ T064 - Verificar meta tags presentes
T065 - Probar Open Graph con Facebook Sharing Debugger
✅ T066 - Verificar jerarquía HTML (h1 → h2 → h3)
```

**6. Validación Final** (5 tareas - 2 completas)

```bash
✅ T067 - Tests unitarios ≥90% coverage (172/172 passing, 100%)
T068 - Tests E2E passing
T069 - Ejecutar quickstart.md scenarios
T070 - Verificar PublicFeedPage funciona en /trips/public
✅ T071 - Actualizar CHANGELOG.md
```

#### Priorización Recomendada Feature 014

**Alta prioridad** (debe hacerse antes de merge):

- T045, T046: Responsive testing
- T047, T048: Accessibility WCAG AA
- T051: Lighthouse audit
- T062, T063, T068: E2E tests

**Media prioridad** (nice-to-have):

- T053, T054, T055: Performance optimizations
- T056-T061: Cross-browser testing (puede hacerse post-merge)
- T065: Open Graph preview

#### Criterios de Aceptación Feature 014

- [ ] Responsive design validado (móvil, tablet, desktop)
- [ ] WCAG 2.1 AA compliant
- [ ] Lighthouse score ≥90 (Performance, Accessibility, Best Practices)
- [ ] Tests E2E passing
- [ ] Cross-browser compatible (Chrome, Firefox, Safari, Edge)

---

## 🟢 PRIORIDAD BAJA

### Feature 006: Dashboard Dinámico

**Branch**: `006-dashboard-dynamic` (a crear)

**Estado**: ⏸️ **No iniciado** (0/72 tareas)

**Prioridad**: 🟢 **Baja** (nueva funcionalidad)

**Tiempo estimado**: 3-4 días

**Bloqueadores**: Ninguno

#### Descripción Feature 006

Dashboard personalizable con stats cards, recent trips, quick actions, welcome banner y activity feed.

#### Tareas Feature 006 (72 total)

**MVP Recomendado** (44 tareas):

1. **Phase 1: Setup** (5 tareas)
   - Crear estructura de directorios
   - Crear utils para formatters

2. **Phase 2: Foundational** (9 tareas) - **CRÍTICO**
   - Definir interfaces TypeScript
   - Implementar formatters
   - Crear SkeletonLoader component

3. **Phase 3: FR-001 Stats Cards** (11 tareas) 🎯
   - StatsCard component (viajes, distancia, países, seguidores)
   - Integrar API `/api/stats/me`
   - Diseño rústico con estados de carga/error

4. **Phase 4: FR-002 Recent Trips** (12 tareas)
   - RecentTripCard (últimos 3-5 viajes)
   - Lazy loading de imágenes
   - Estado vacío

5. **Phase 5: FR-004 Quick Actions** (7 tareas)
   - 4 botones: Crear, Ver Perfil, Explorar, Editar
   - Grid responsive (2x2 móvil)

**Opcional** (28 tareas):

- Phase 6: FR-005 Welcome Banner (6 tareas)
- Phase 7: FR-003 Activity Feed (13 tareas - requiere backend)
- Phase 8: Polish (9 tareas)

#### Estrategia de Implementación Feature 006

```bash
# Orden recomendado
1. Setup + Foundational (T001-T014) → Base lista
2. FR-001 Stats Cards (T015-T025) → Primera funcionalidad
3. FR-002 Recent Trips (T026-T037) → Contenido enriquecido
4. FR-004 Quick Actions (T038-T044) → Navegación rápida
# PARAR → Validar MVP funcional
5. Polish si hay tiempo
```

#### Recursos Feature 006

- **Tasks**: `specs/006-dashboard-dynamic/tasks.md`
- **Plan**: `specs/006-dashboard-dynamic/plan.md`

---

### Feature 004: Async GPX Processing con Celery + Redis

**Branch**: `004-celery-async-tasks` (specs completas)

**Estado**: ⏸️ **No iniciado** (specs completas)

**Prioridad**: 🟢 **Baja** (performance optimization)

**Tiempo estimado**: 2-3 días

**Bloqueadores**: Ninguno

#### Descripción Feature 004

Agregar cola de tareas distribuida (Celery + Redis) para procesamiento asíncrono de archivos GPX grandes (>5MB).

#### Motivación Feature 004

**Actual**:

- Files ≤1MB: Procesamiento sincrónico (~1-2s)
- Files >1MB: FastAPI BackgroundTasks (~7-8s)
- Limitaciones: No persistence, no retry, no scaling, no monitoring

**Propuesto**:

- Files ≤5MB: Continue usando BackgroundTasks
- Files >5MB: Procesar con Celery workers
- Beneficios: Horizontal scaling, persistence, retries, monitoring (Flower)

#### Implementación Feature 004 (7 fases según plan)

**Phase 1: Dependencies & Configuration** (~2 horas)

- Agregar Celery + Redis a `pyproject.toml`
- Configurar `config.py` con variables Celery
- Crear `.env` variables

**Phase 2: Celery Application** (~3 horas)

- Crear `backend/src/celery_app.py`
- Configurar broker, backend, serialization

**Phase 3: GPX Processing Task** (~4 horas)

- Crear `backend/src/tasks/gpx_tasks.py`
- Implementar `process_gpx_file_async` task
- Base64 encoding para JSON serialization
- Retry policy (max 3 attempts, exponential backoff)

**Phase 4: Update Upload Endpoint** (~2 horas)

- Modificar `backend/src/api/trips.py`
- Routing logic: >5MB → Celery, ≤5MB → BackgroundTasks
- Backward compatible (testing mode usa BackgroundTasks)

**Phase 5: Docker Infrastructure** (~3 horas)

- Agregar Redis service a docker-compose
- Agregar celery_worker service
- Agregar flower monitoring service
- Escalado en producción (autoscale 2-10 workers)

**Phase 6: Testing** (~4 hours)

- Unit tests: `test_gpx_tasks.py`
- Integration test: Files >5MB usan Celery
- Manual testing con Flower UI

**Phase 7: Deployment & Rollout** (~2 horas)

- Phased rollout (staging → 10% → 100%)
- Monitoring con Flower
- Tune worker concurrency

#### Recursos Feature 004

- **Especificación**: `specs/004-celery-async-tasks/spec.md`
- **Plan**: Plan disponible en claude plan file (ver system reminder)

#### Criterios de Aceptación Feature 004

- [ ] Files >5MB procesados asíncronomente con Celery
- [ ] Files ≤5MB continúan usando BackgroundTasks
- [ ] Tasks retry automáticamente (max 3 intentos)
- [ ] Monitoring vía Flower UI
- [ ] Horizontal scaling funcional (múltiples workers)

---

## 📊 Tracking de Progreso

### Features en Desarrollo

| Feature | Branch | Estado | Próximo Hito |
| ------- | ------ | ------ | ------------ |
| ~~012-typescript-code-quality~~ | develop (merged) | 100% ✅ | Completado |
| ~~017-gps-trip-wizard~~ | develop (merged) | 93% ✅ | Completado |
| ~~011-frontend-deployment~~ | develop (merged) | 100% ✅ | Completado |
| 015-gpx-wizard-integration | N/A | 0% | Phase 1: Setup |
| 016-deployment-docs | N/A | 31% | T013: getting-started.md |
| 014-landing-page | develop | 62% | Phase 8: Polish |
| 006-dashboard-dynamic | N/A | 0% | Phase 1: Setup |
| 004-celery-async-tasks | N/A | 0% | Phase 1: Dependencies |

### Orden de Trabajo Recomendado

**Próximas prioridades** (Febrero 2026):

1. 🔴 **Feature 015** - GPX Wizard Integration (4-8 horas) - UX enhancement de alto valor
2. 🟡 **Feature 016** - Core guides (T013-T015, 2-3 días) - Deployment documentation
3. 🟡 **Feature 014** - Polish landing page (1-2 días) - Marketing & branding

**Futuro** (según prioridad de negocio):

- Feature 006 (Dashboard Dinámico) - 3-4 días
- Feature 004 (Celery + Redis) - 2-3 días

---

## 🎯 Métricas de Éxito

### Coverage Targets

- Backend Unit: ≥90% (actual: ~90% ✅)
- Frontend Unit: ≥80% (actual: variable por feature)
- E2E Tests: ≥85% coverage (actual: 72.7%)
- Integration Tests: 111/156 passing (71%)

### Build Targets

- TypeScript: 0 errors (actual: 25 en Feature 012)
- Production Build: < 1.2MB (blocked by Feature 012)
- Build Time: < 60s (SC-001)

### Documentation Targets

- Deployment Docs: 17 archivos, ~12,000 líneas (actual: 31%)
- API Docs: Swagger up-to-date ✅
- Feature Specs: 100% features tienen spec.md ✅

---

## 🔗 Recursos Clave

### Comandos Rápidos

```bash
# Feature 012: TypeScript fixes
git checkout 012-typescript-code-quality
npm run type-check
npm run build:prod

# Feature 011: Deployment validation
./deploy.sh local --with-frontend
npm run build:prod

# Feature 015: GPX Wizard (nuevo)
git checkout -b 015-gpx-wizard-integration
# Seguir specs/015-gpx-wizard-integration/tasks.md

# Feature 016: Docs (nuevo)
# Seguir specs/016-deployment-docs-completion/README.md

# Feature 014: Landing page polish
git checkout 014-landing-page-inspiradora
npm run test
npm run dev
```

### Documentación

- **CLAUDE.md**: Guía principal del proyecto
- **QUICK_START.md**: Deployment rápido
- **docs/deployment/README.md**: Master index de deployment
- **specs/**: Todas las especificaciones de features

### URLs de Desarrollo

- Frontend Dev: <http://localhost:5173>
- Backend API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>
- Flower (Celery): <http://localhost:5555> (Feature 004)

---

**Última actualización**: 2026-02-06

**Próxima revisión**: Después de merge de Feature 017 a develop

**Mantenedor**: Claude Code
