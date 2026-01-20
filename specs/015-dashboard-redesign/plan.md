# Implementation Plan: Dashboard Principal Mejorado

**Branch**: `015-dashboard-redesign` | **Date**: 2026-01-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-dashboard-redesign/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementación de un dashboard mejorado para usuarios de ContraVento con navegación sticky header, layout de 3 columnas responsivo, estadísticas personales en tiempo real, feed de actividad social, rutas sugeridas personalizadas, desafíos activos, notificaciones y acciones rápidas. El objetivo es proporcionar una experiencia centralizada y motivadora que refuerce la conexión comunitaria y fomente la exploración territorial.

**Enfoque técnico**: Feature exclusivamente frontend utilizando React 18 + TypeScript con Tailwind CSS v4 (@tailwindcss/vite). El backend ya está construido y expondrá los endpoints necesarios. Se priorizarán componentes reutilizables, hooks personalizados para lógica de negocio, y optimización de rendimiento mediante lazy loading y virtualización de listas largas. Los componentes existentes (~70) mantienen CSS Modules sin cambios (coexistencia gradual).

## Technical Context

**Language/Version**: TypeScript 5.2+ (Frontend only - Backend Python 3.12 ya implementado)
**Primary Dependencies**: React 18.2, React Router 6.21, Axios 1.6, React Hook Form 7.70, Zod 3.25, date-fns 3.0
**Storage**: N/A (Frontend consume APIs REST del backend - PostgreSQL production / SQLite development)
**Testing**: Vitest 1.6 (unit), Playwright 1.40 (E2E), React Testing Library 14.3
**Target Platform**: Navegadores modernos (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (frontend only - backend ya existe)
**Performance Goals**:
  - First Contentful Paint (FCP) < 1.5s
  - Time to Interactive (TTI) < 3.5s
  - Smooth scroll >30 FPS en dispositivos gama media
  - Lazy loading de secciones below-the-fold

**Constraints**:
  - Dashboard completo carga en <2s (SC-001)
  - Feed de actividad renderiza 50 items en <2s (SC-003)
  - Sticky header permanece visible sin layout shift
  - Diseño responsive tablet (768px) y mobile (320px+)

**Scale/Scope**:
  - 8 user stories (3 P1, 3 P2, 2 P3)
  - ~12-15 componentes React nuevos
  - ~8-10 hooks personalizados
  - 4-6 nuevos endpoints backend (consumidos, no implementados)
  - ~1500-2000 LOC frontend estimado

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Code Quality & Maintainability

- ✅ **TypeScript type hints**: Todos los componentes y hooks tendrán interfaces tipadas
- ✅ **Single Responsibility**: Cada componente React tendrá una responsabilidad clara (dashboard sections, header, feed items)
- ✅ **Tailwind CSS v4**: Utility-first styling con @tailwindcss/vite, coexistencia con CSS Modules en componentes existentes
- ✅ **Linting**: ESLint configurado con reglas React + TypeScript
- ✅ **No magic numbers**: Breakpoints responsive y timings definidos como constantes

### Principle II: Testing Standards (TDD)

- ✅ **Unit Tests**: Vitest para hooks personalizados (useDashboardStats, useFeed, useSearch)
- ✅ **Integration Tests**: React Testing Library para componentes con interacción (header search, notification panel)
- ✅ **E2E Tests**: Playwright para user stories críticas (US1 - estadísticas, US2 - navegación)
- ⚠️ **TDD Workflow**: Tests escritos ANTES de implementación para cada user story
- ✅ **Coverage Target**: ≥90% en hooks y componentes críticos

### Principle III: User Experience Consistency

- ✅ **Spanish-first**: Todos los textos en español (botones, mensajes, labels)
- ✅ **Error handling**: Estados de error con mensajes claros y acciones de recuperación
- ✅ **Loading states**: Skeleton loaders durante carga de estadísticas y feed
- ✅ **Accessibility**: ARIA labels para header sticky, botones de acción rápida, contador notificaciones
- ✅ **Responsive**: Layout adapta de 3 columnas (desktop) → 2 (tablet) → 1 (mobile)

### Principle IV: Performance Requirements

- ✅ **<200ms p95**: Navegación entre secciones del dashboard
- ✅ **<1s load**: Estadísticas personales (SC-001)
- ✅ **<2s load**: Feed completo con 50 items (SC-003)
- ✅ **>30 FPS**: Scroll suave con sticky header (SC-010)
- ✅ **Lazy loading**: Secciones P3 (desafíos, notificaciones) cargan on-demand
- ✅ **Virtualization**: Feed usa react-window para listas >100 items

### Security & Data Protection

- ✅ **Authentication**: Rutas protegidas via AuthContext (ya implementado)
- ✅ **Input sanitization**: Búsqueda global sanitiza antes de enviar al backend
- ✅ **XSS prevention**: React escapado automático + DOMPurify para HTML del feed

### Development Workflow

- ✅ **Feature branch**: `015-dashboard-redesign` (ya creada)
- ✅ **Conventional commits**: `feat(dashboard):`, `test(dashboard):`, `style(dashboard):`
- ✅ **Code review**: PR incluirá screenshots desktop/tablet/mobile
- ✅ **No breaking changes**: Dashboard existente (Feature 006) permanece funcional durante migración

**GATE STATUS**: ✅ **PASSED** - Todos los principios cumplidos, no hay violaciones

## Project Structure

### Documentation (this feature)

```text
specs/015-dashboard-redesign/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0: Technology decisions, patterns, best practices
├── data-model.md        # Phase 1: Frontend state model, API response interfaces
├── quickstart.md        # Phase 1: Development workflow, testing guide
├── contracts/           # Phase 1: API endpoint contracts (consumed from backend)
│   ├── dashboard-stats.yaml
│   ├── activity-feed.yaml
│   ├── suggested-routes.yaml
│   ├── challenges.yaml
│   ├── notifications.yaml
│   └── global-search.yaml
└── tasks.md             # Phase 2: Implementation tasks (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure Decision**: Web application - Frontend only (backend ya existe)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/           # Dashboard-specific components (NUEVO - Tailwind CSS)
│   │   │   ├── DashboardHeader.tsx          # Sticky header with search + notifications
│   │   │   ├── DashboardLayout.tsx          # 3-column responsive grid
│   │   │   ├── GlobalSearch.tsx             # Autocomplete search bar
│   │   │   ├── NotificationPanel.tsx        # Dropdown notifications list
│   │   │   ├── StatsOverview.tsx            # Personal stats section
│   │   │   ├── ActivityFeed.tsx             # Social feed component
│   │   │   ├── ActivityFeedItem.tsx         # Individual feed entry
│   │   │   ├── SuggestedRoutes.tsx          # Routes recommendation
│   │   │   ├── RouteCard.tsx                # Single route suggestion
│   │   │   ├── ActiveChallenges.tsx         # Challenges section
│   │   │   └── ChallengeProgressBar.tsx     # Progress indicator
│   │   └── common/              # Shared components (existing)
│   │       └── SkeletonLoader.tsx (already exists)
│   │
│   ├── pages/
│   │   └── DashboardPage.tsx                # Main dashboard page (REEMPLAZA existente)
│   │
│   ├── hooks/                   # Custom hooks (NUEVO)
│   │   ├── useDashboardStats.ts             # Fetch personal stats
│   │   ├── useActivityFeed.ts               # Fetch & paginate feed
│   │   ├── useSuggestedRoutes.ts            # Fetch route recommendations
│   │   ├── useActiveChallenges.ts           # Fetch active challenges
│   │   ├── useNotifications.ts              # Fetch & mark read notifications
│   │   ├── useGlobalSearch.ts               # Search with debounce
│   │   └── useResponsiveLayout.ts           # Breakpoint detection
│   │
│   ├── lib/                     # Utilities (NUEVO)
│   │   └── cn.ts                            # clsx + tailwind-merge helper
│   │
│   ├── services/
│   │   └── dashboardService.ts              # API calls for dashboard endpoints (NUEVO)
│   │
│   ├── types/                   # TypeScript interfaces (NUEVO)
│   │   ├── dashboard.ts                     # DashboardStats, FeedItem, Route, Challenge
│   │   └── notifications.ts                 # Notification interface
│   │
│   ├── utils/
│   │   └── constants.ts                     # Responsive breakpoints (NUEVO)
│   │
│   └── index.css                            # Tailwind entry point (@import + @theme)
│
└── tests/
    ├── unit/                    # Vitest tests (NUEVO)
    │   ├── hooks/
    │   │   ├── useDashboardStats.test.ts
    │   │   ├── useActivityFeed.test.ts
    │   │   └── useGlobalSearch.test.ts
    │   └── components/
    │       ├── GlobalSearch.test.tsx
    │       └── NotificationPanel.test.tsx
    │
    └── e2e/                     # Playwright tests (NUEVO)
        ├── dashboard-stats.spec.ts          # US1: Vista rápida estadísticas
        ├── dashboard-navigation.spec.ts     # US2: Navegación y búsqueda
        └── dashboard-feed.spec.ts           # US3: Feed de actividad
```

## Complexity Tracking

> **No hay violaciones a la constitución - esta sección queda vacía**

---

## Phase 0 & Phase 1 Summary

### ✅ Phase 0: Research & Decisions (Completed)

**Output**: [research.md](research.md)

**Key Decisions**:

1. **CSS Strategy**: Tailwind CSS v4 con @tailwindcss/vite para componentes nuevos (Feature 015), CSS Modules sin cambios para componentes existentes
2. **Layout**: CSS Grid con Tailwind (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
3. **Data Fetching**: Custom hooks + Axios (sin react-query)
4. **Search Debounce**: lodash.debounce (ya instalado)
5. **Virtualization**: react-window solo si >100 items (condicional)
6. **Responsive**: Hook personalizado `useResponsiveLayout` + Tailwind breakpoints
7. **Sticky Header**: Tailwind `sticky top-0` con hardware acceleration
8. **Loading States**: Skeleton loaders con Tailwind (animate-pulse, bg-gray-200)
9. **Date Formatting**: date-fns (ya instalado)
10. **Error Handling**: react-hot-toast + inline errors
11. **Class Utilities**: clsx + tailwind-merge para manejo de clases condicionales (función cn())

**Technologies**:

- ✅ **Nuevas dependencias**: tailwindcss@4.1.18, @tailwindcss/vite@4.1.18, clsx, tailwind-merge
- ✅ **Existentes**: React 18.2, TypeScript 5.2, Axios 1.6, date-fns 3.0
- ✅ **Testing**: Vitest 1.6 (unit), Playwright 1.40 (E2E)
- ✅ **Documentación**: Ver [tailwind-setup.md](tailwind-setup.md) para setup completo

---

### ✅ Phase 1: Design & Contracts (Completed)

**Outputs**:

- [data-model.md](data-model.md) - 20+ TypeScript interfaces definidas
- [contracts/](contracts/) - 6 endpoints API documentados
  - `dashboard-stats.yaml` - Estadísticas personales (detallado)
  - `README.md` - Feed, Routes, Challenges, Notifications, Search (simplificado)
- [quickstart.md](quickstart.md) - Workflow de desarrollo, testing, debugging

**API Endpoints Consumidos** (Backend ya implementado):

1. `GET /api/v1/dashboard/stats` - Estadísticas personales
2. `GET /api/v1/dashboard/feed` - Feed de actividad social
3. `GET /api/v1/dashboard/suggested-routes` - Rutas sugeridas
4. `GET /api/v1/dashboard/challenges` - Desafíos activos
5. `GET /api/v1/dashboard/notifications` - Notificaciones
6. `GET /api/v1/dashboard/search` - Búsqueda global

---

## Constitution Re-Check (Post-Design)

*GATE: Must re-evaluate after Phase 1 design complete*

### Principle I: Code Quality & Maintainability ✅

- ✅ TypeScript interfaces definidas en `types/dashboard.ts` y `types/notifications.ts`
- ✅ Componentes con SRP (DashboardHeader, GlobalSearch, ActivityFeed separados)
- ✅ Tailwind CSS v4 con utility classes, función cn() para manejo de clases condicionales
- ✅ Breakpoints definidos en Tailwind config (@theme) y constantes TypeScript
- ✅ Hooks reutilizables (`useDashboardStats`, `useActivityFeed`, etc.)

**Status**: ✅ **PASSED**

### Principle II: Testing Standards ✅

- ✅ Test plan documentado en quickstart.md
- ✅ Unit tests: Vitest para hooks y componentes
- ✅ E2E tests: Playwright para user stories P1 (US1, US2)
- ⚠️ **TDD Workflow**: Debe aplicarse durante implementación (tests ANTES de código)
- ✅ Coverage target: ≥90% para componentes críticos

**Status**: ✅ **PASSED** (con recordatorio TDD)

### Principle III: User Experience Consistency ✅

- ✅ Todos los textos en español (error messages, labels, placeholders)
- ✅ Loading states: Skeleton loaders definidos
- ✅ Error handling: Toast + inline errors + retry buttons
- ✅ Accessibility: ARIA labels documentados para header, search, notifications
- ✅ Responsive: 3 breakpoints definidos (mobile/tablet/desktop)

**Status**: ✅ **PASSED**

### Principle IV: Performance Requirements ✅

- ✅ Performance goals documentados (FCP <1.5s, TTI <3.5s)
- ✅ Lazy loading strategy para componentes P3 (challenges, notifications)
- ✅ Virtualization condicional (react-window si >100 items)
- ✅ Debounce en search (300ms) para reducir API calls
- ✅ Sticky header con hardware acceleration (`will-change: transform`)

**Status**: ✅ **PASSED**

### Security & Data Protection ✅

- ✅ Authentication via AuthContext (ya implementado)
- ✅ Input sanitization en search (validation rules definidas)
- ✅ XSS prevention: React auto-escape + DOMPurify para HTML feed

**Status**: ✅ **PASSED**

### Development Workflow ✅

- ✅ Branch `015-dashboard-redesign` ya creada
- ✅ Conventional commits documentados (`feat(dashboard):`, etc.)
- ✅ PR requirements: screenshots desktop/tablet/mobile
- ✅ No breaking changes: Dashboard existente permanece funcional

**Status**: ✅ **PASSED**

---

## Final Gate Status

**Constitution Check**: ✅ **PASSED** - Todos los principios cumplidos post-diseño

**Phase 0 & Phase 1**: ✅ **COMPLETED**

**Ready for**:

- ⏭️ **Phase 2**: Generate tasks.md via `/speckit.tasks` command
- ⏭️ **Implementation**: Start coding with TDD workflow (tests first)

---

## Artifacts Generated

| Artifact | Status | Lines | Description |
|----------|--------|-------|-------------|
| plan.md | ✅ Complete | ~190 | This file - Implementation plan |
| research.md | ✅ Complete | ~450 | Technology decisions & rationale |
| data-model.md | ✅ Complete | ~400 | TypeScript interfaces (20+ types) |
| contracts/dashboard-stats.yaml | ✅ Complete | ~150 | OpenAPI spec (detailed) |
| contracts/README.md | ✅ Complete | ~300 | API contracts summary (5 endpoints) |
| quickstart.md | ✅ Complete | ~350 | Development workflow guide |

**Total Documentation**: ~1,840 lines generated

---

## Next Command

```bash
# Generate implementation tasks
/speckit.tasks
```

**Implementation Order** (User Stories by Priority):

1. **P1** - US1: Vista Rápida de Estadísticas (MVP core)
2. **P1** - US2: Navegación y Búsqueda Rápida (MVP core)
3. **P2** - US3: Feed de Actividad de la Comunidad
4. **P2** - US4: Rutas Sugeridas y Descubrimiento
5. **P2** - US8: Métricas Sociales
6. **P3** - US5: Desafíos Activos y Progreso
7. **P3** - US6: Notificaciones y Alertas
8. **P3** - US7: Acciones Rápidas

---

**Planning phase complete** ✅ - Ready to generate tasks and start implementation!
