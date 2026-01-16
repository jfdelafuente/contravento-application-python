# Implementation Plan: Enlaces Sociales con Control de Privacidad Granular

**Branch**: `015-social-links-privacy` | **Date**: 2026-01-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-social-links-privacy/spec.md`

## Summary

Implementar sistema de enlaces a redes sociales externas (Instagram, Strava, Blog, Portfolio) con control de privacidad granular de 4 niveles (Público, Solo Comunidad, Círculo de Confianza, Oculto). Incluye validación robusta de URLs, sanitización contra XSS/phishing, y lógica de visibilidad basada en relaciones de seguimiento mutuo. Backend en Python con FastAPI + SQLAlchemy, frontend en React + TypeScript con indicadores visuales de privacidad.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5 (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0 (async), Pydantic (backend) | React 18, React Router 6, Axios (frontend)
**Storage**: PostgreSQL (production), SQLite (development) - extends existing User/UserProfile schema
**Testing**: pytest + pytest-asyncio (backend unit/integration), Vitest + React Testing Library (frontend unit), Playwright (E2E)
**Target Platform**: Linux server (backend), Modern browsers (frontend: Chrome 90+, Firefox 88+, Safari 14+)
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**: <200ms p95 for profile view with links, <500ms p95 for edit operations, zero XSS vulnerabilities
**Constraints**: Enlaces limitados a 6 por usuario, sanitización obligatoria de URLs, relaciones de seguimiento en tiempo real para "Círculo de Confianza"
**Scale/Scope**: ~10k usuarios concurrentes, 6 enlaces por perfil, soporta 4 redes sociales predefinidas + 2 custom

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Maintainability

- ✅ **PEP 8 Compliance**: Backend seguirá PEP 8 con black formatter
- ✅ **Single Responsibility**: SocialLinkService maneja lógica de negocio, validators separan sanitización
- ✅ **Type Hints**: Todos los métodos tendrán type hints (Pydantic models, AsyncSession, enums)
- ✅ **Named Constants**: Privacy levels como Enum (PUBLIC, COMMUNITY, MUTUAL_FOLLOWERS, HIDDEN)
- ✅ **Docstrings**: Google-style docstrings para ServiceLayer y validators

### II. Testing Standards (TDD STRICTLY ENFORCED)

- ✅ **TDD Workflow**: Tests escritos ANTES de implementación (Red → Green → Refactor)
- ✅ **Unit Tests**: ≥90% coverage para SocialLinkService, URL validators, privacy logic
- ✅ **Integration Tests**: API endpoints (POST/GET/PUT/DELETE /social-links), database operations
- ✅ **Contract Tests**: OpenAPI schema validation para todos los endpoints de enlaces sociales
- ✅ **Edge Cases**: Tests para XSS attempts, duplicados, límite de 6 enlaces, seguimiento mutuo edge cases
- ✅ **Frontend Tests**: Vitest para componentes de UI (indicadores de privacidad, botones CTA), Playwright para flujos E2E

### III. User Experience Consistency

- ✅ **Spanish First**: Todos los mensajes de error en español ("URL no válida...", "Máximo 6 enlaces permitidos")
- ✅ **Consistent API**: Estructura JSON estándar `{success, data, error}` para todas las respuestas
- ✅ **Field-Specific Errors**: Validación server-side retorna errores por campo (url, privacy_level, platform_type)
- ✅ **Visual Feedback**: Iconos de privacidad (candado abierto/cerrado, grupo, ojo tachado) se actualizan en tiempo real
- ✅ **Accessibility**: Alt text en iconos, ARIA labels para dropdowns de privacidad

### IV. Performance Requirements

- ✅ **Profile View**: <200ms p95 para GET /users/{username}/profile (incluye enlaces con privacy filtering)
- ✅ **Edit Operations**: <500ms p95 para POST/PUT /social-links (validación + sanitización + persist)
- ✅ **Query Optimization**: Eager loading de relaciones (User → SocialLinks → Follows) para evitar N+1
- ✅ **Pagination**: No aplica (max 6 enlaces por usuario, no necesita paginación)
- ✅ **Indexes**: Index en (user_id, platform_type) para unicidad, index en privacy_level para filtering

### Security & Data Protection

- ✅ **URL Sanitization**: Librería `bleach` para sanitizar URLs, eliminar scripts, validar dominios
- ✅ **XSS Prevention**: HTML rendering con `rel="me nofollow"`, `target="_blank"`, escaped output
- ✅ **Input Validation**: Pydantic schemas validan formato de URL, longitud, dominios permitidos
- ✅ **Authorization**: Solo el dueño del perfil puede editar sus enlaces (verificación en endpoints)
- ✅ **Privacy Enforcement**: Lógica server-side verifica relación de seguimiento para "Círculo de Confianza"

### Development Workflow

- ✅ **Feature Branch**: 015-social-links-privacy ya creada
- ✅ **Conventional Commits**: Mensajes siguiendo formato "feat(social-links): add URL validator"
- ✅ **PR Requirements**: Tests coverage ≥90%, screenshots de UI con indicadores de privacidad
- ✅ **Reversible Migrations**: Alembic migration para SocialLink table con downgrade script

**GATE STATUS**: ✅ **PASSED** - No violations, all principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/015-social-links-privacy/
├── plan.md              # This file
├── research.md          # Phase 0: URL sanitization libraries, privacy patterns
├── data-model.md        # Phase 1: SocialLink entity, PrivacyLevel enum
├── quickstart.md        # Phase 1: Testing scenarios para privacy levels
├── contracts/           # Phase 1: OpenAPI specs para /social-links endpoints
│   └── social-links-api.yaml
└── tasks.md             # Phase 2: Desglose de tareas TDD (NOT created by this command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   └── social_link.py          # SQLAlchemy SocialLink model + PrivacyLevel enum
│   ├── schemas/
│   │   └── social_link.py          # Pydantic schemas (SocialLinkCreate, SocialLinkResponse)
│   ├── services/
│   │   └── social_link_service.py  # Business logic: add/edit/delete links, privacy filtering
│   ├── utils/
│   │   └── url_validator.py        # URL sanitization, domain validation
│   └── api/
│       └── social_links.py         # FastAPI router: CRUD endpoints para enlaces
└── tests/
    ├── unit/
    │   ├── test_social_link_service.py
    │   └── test_url_validator.py
    ├── integration/
    │   └── test_social_links_api.py
    └── contract/
        └── test_social_links_contract.py

frontend/
├── src/
│   ├── types/
│   │   └── socialLink.ts           # TypeScript interfaces (SocialLink, PrivacyLevel)
│   ├── components/
│   │   └── profile/
│   │       ├── SocialLinksDisplay.tsx     # Visualización de iconos según privacidad
│   │       ├── SocialLinksEditor.tsx      # Formulario de edición con dropdowns
│   │       └── PrivacyIndicator.tsx       # Icono + tooltip para nivel de privacidad
│   ├── services/
│   │   └── socialLinksService.ts   # Axios calls a /social-links API
│   └── pages/
│       └── ProfileEditPage.tsx     # Integración de SocialLinksEditor
└── tests/
    ├── unit/
    │   └── profile/
    │       ├── SocialLinksDisplay.test.tsx
    │       ├── SocialLinksEditor.test.tsx
    │       └── PrivacyIndicator.test.tsx
    └── e2e/
        └── social-links.spec.ts    # Playwright: flujos de añadir/editar/privacidad
```

**Structure Decision**: Web application estructura (opción 2) porque esta feature extiende tanto backend (API + DB) como frontend (UI components). Los enlaces sociales se integran en perfiles existentes, requiriendo modificaciones en ambos lados.

## Complexity Tracking

> **No violations detected - this section intentionally left empty**

All constitution principles are satisfied without exceptions. No complexity justifications needed.

## Phase 0: Research & Unknowns

**Status**: 🔍 NEEDS RESOLUTION

### Research Tasks

1. **URL Sanitization Library Selection**
   - **Question**: ¿Qué librería usar para sanitizar URLs en Python con mejor protección contra XSS/phishing?
   - **Options**: `bleach`, `html5lib`, custom regex validators
   - **Decision Criteria**: Soporte de Python 3.12, facilidad de configuración de allowlist de dominios, performance

2. **Privacy Filtering Performance Pattern**
   - **Question**: ¿Cómo optimizar queries para verificar seguimiento mutuo al renderizar perfiles?
   - **Options**: Query JOIN con Follows table, cache de relaciones, denormalization
   - **Decision Criteria**: Performance <200ms p95, escalabilidad a 10k usuarios

3. **Frontend Icon Library**
   - **Question**: ¿Qué librería de iconos usar para redes sociales + indicadores de privacidad?
   - **Options**: HeroIcons (ya en proyecto), React Icons, FontAwesome, custom SVGs
   - **Decision Criteria**: Coherencia con estética ContraVento (tonos tierra), tamaño del bundle

4. **Domain Validation Strategy**
   - **Question**: ¿Validar dominios con allowlist estricta o regex flexible?
   - **Options**: Allowlist hardcoded (instagram.com, strava.com), regex pattern matching, hybrid approach
   - **Decision Criteria**: Balance entre seguridad y flexibilidad para blogs/portfolios custom

**Output**: research.md con decisiones documentadas

## Phase 1: Design Artifacts

**Status**: ⏳ PENDING (depends on Phase 0)

### Deliverables

1. **data-model.md**: Schema completo de SocialLink
   - Campos: `social_link_id` (UUID), `user_id` (FK), `platform_type` (Enum), `url` (Text), `privacy_level` (Enum), `created_at`, `updated_at`
   - Relaciones: `SocialLink.user` (Many-to-One con User), verificación de Follows para privacy
   - Constraints: UNIQUE (user_id, platform_type), CHECK (url length ≤2000), CHECK (platform_type in allowed values)
   - Enums: `PlatformType` (INSTAGRAM, STRAVA, BLOG, PORTFOLIO, CUSTOM_1, CUSTOM_2), `PrivacyLevel` (PUBLIC, COMMUNITY, MUTUAL_FOLLOWERS, HIDDEN)

2. **contracts/social-links-api.yaml**: OpenAPI 3.0 spec
   - `GET /users/{username}/social-links`: Retorna enlaces visibles según privacidad del caller
   - `POST /social-links`: Crear nuevo enlace (requiere autenticación)
   - `PUT /social-links/{link_id}`: Editar enlace existente
   - `DELETE /social-links/{link_id}`: Eliminar enlace
   - Schemas: SocialLinkCreate (url, platform_type, privacy_level), SocialLinkResponse (+ id, timestamps)

3. **quickstart.md**: Escenarios de testing
   - **Scenario 1**: Usuario anónimo visita perfil → solo ve enlaces PUBLIC
   - **Scenario 2**: Usuario autenticado visita perfil → ve PUBLIC + COMMUNITY
   - **Scenario 3**: Seguidor mutuo visita perfil → ve PUBLIC + COMMUNITY + MUTUAL_FOLLOWERS
   - **Scenario 4**: Dueño edita enlaces → cambia privacy_level de INSTAGRAM de PUBLIC a COMMUNITY
   - **Scenario 5**: Intento de XSS → URL con `javascript:alert()` rechazada con error 400

4. **Agent Context Update**
   - Run: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`
   - Add: `bleach` (URL sanitization), `SocialLink` model, `PrivacyLevel` enum to active technologies

**Output**: 4 archivos generados en specs/015-social-links-privacy/

## Implementation Strategy (Phase 2 Preview)

**Note**: Tareas detalladas serán generadas por `/speckit.tasks` después de este plan

### High-Level Phases

1. **Setup** (Foundation)
   - Create Alembic migration para SocialLink table
   - Define PrivacyLevel enum en código
   - Configurar bleach sanitizer con allowlist de dominios

2. **Backend Core** (TDD - Test First!)
   - **Tests primero**: test_url_validator.py (XSS attempts, domain validation)
   - **Implementación**: url_validator.py con bleach sanitization
   - **Tests**: test_social_link_service.py (add/edit/delete, privacy filtering logic)
   - **Implementación**: social_link_service.py con verificación de Follows
   - **Tests**: test_social_links_api.py (endpoints CRUD, authorization)
   - **Implementación**: social_links.py FastAPI router

3. **Frontend UI** (TDD)
   - **Tests**: SocialLinksDisplay.test.tsx (rendering condicional por privacidad)
   - **Implementación**: SocialLinksDisplay.tsx con iconos dinámicos
   - **Tests**: SocialLinksEditor.test.tsx (formulario, validación client-side)
   - **Implementación**: SocialLinksEditor.tsx con dropdowns de privacidad
   - **Tests**: PrivacyIndicator.test.tsx (iconos de candado/grupo/ojo)
   - **Implementación**: PrivacyIndicator.tsx con tooltips

4. **Integration & E2E**
   - Contract tests: Validar OpenAPI schema contra endpoints reales
   - Playwright E2E: Flujo completo de añadir Instagram público → cambiar a Community → verificar visibilidad

### Dependencies & Blockers

- **BLOCKER**: Feature 011 (Follows) debe estar implementada para soportar "Círculo de Confianza"
  - Workaround temporal: Implementar US1, US2, US5 (PUBLIC y COMMUNITY) primero
  - Postergar US3 (MUTUAL_FOLLOWERS) hasta que Feature 011 esté disponible
- **Dependency**: Feature 001 (User Profiles) ya está implementada (confirmed)

### Risk Mitigation

- **Risk**: Sanitización insuficiente permite XSS
  - **Mitigation**: TDD estricto con test cases de OWASP Top 10, code review enfocado en seguridad
- **Risk**: Performance degradation por queries de Follows en cada profile view
  - **Mitigation**: Profiling temprano, eager loading, considerar cache si p95 >200ms
- **Risk**: UX confusa para "Círculo de Confianza"
  - **Mitigation**: Tooltips explicativos, testing con usuarios reales, botón CTA claro

## Post-Implementation Checklist

- [ ] All tests pass (unit + integration + contract + E2E) con ≥90% coverage
- [ ] Black formatting + ruff linting sin warnings
- [ ] TypeScript compilation sin errores
- [ ] Alembic migration aplicada en SQLite dev y PostgreSQL staging
- [ ] OpenAPI docs generadas en /docs muestran nuevos endpoints
- [ ] Frontend icons coherentes con paleta ContraVento (tonos tierra)
- [ ] Manual testing de XSS attempts (rechazados correctamente)
- [ ] Manual testing de privacy levels con 3 usuarios (anónimo, autenticado, seguidor mutuo)
- [ ] Performance profiling: Profile view <200ms p95 con 6 enlaces
- [ ] Documentation update: CLAUDE.md refleja nueva feature

---

**Planning Complete**: Ready for `/speckit.tasks` to generate task breakdown
**Next Command**: `/speckit.tasks` (will create tasks.md with detailed TDD workflow)
