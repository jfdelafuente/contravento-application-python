# Estrategia de Branching y CI/CD - ContraVento

**Fecha**: 2026-02-12
**Autor**: Development Team
**Estado**: Draft → Para Aprobación

---

## 📋 Tabla de Contenidos

1. [Análisis del Estado Actual](#análisis-del-estado-actual)
2. [Modelo de Branching Propuesto](#modelo-de-branching-propuesto)
3. [Pipeline CI/CD Completo](#pipeline-cicd-completo)
4. [Estrategia de Releases](#estrategia-de-releases)
5. [Workflow End-to-End](#workflow-end-to-end)
6. [Plan de Implementación](#plan-de-implementación)
7. [Mejoras Propuestas](#mejoras-propuestas)

---

## 1. Análisis del Estado Actual

### ✅ Fortalezas Identificadas

#### CI/CD Existente
- **GitHub Actions configurado**: 5 workflows (ci.yml, backend-tests.yml, frontend-tests.yml, docker-build-push.yml, claude.yml)
- **Quality checks**: Black, Ruff, MyPy (backend) + ESLint, TypeScript (frontend)
- **Testing robusto**: Unit + Integration + E2E (Playwright) con coverage ≥90%
- **Security scanning**: Trivy + Safety para vulnerabilidades
- **Path filters**: Ejecución condicional (solo jobs necesarios)
- **Artifacts**: Reportes de tests y coverage (7 días retención)

#### Infraestructura de Deployment
- **Entornos definidos**: staging + production en GitHub Environments
- **Múltiples modos**: local-dev, local-minimal, local-full, dev, staging, prod
- **Scripts de deploy**: deploy.sh + deploy.ps1 con parametrización completa
- **Docker setup**: docker-compose configs para cada entorno

### ⚠️ Debilidades y Gaps Críticos

#### 1. **Modelo de Branching NO Documentado**
**Problema**:
- No existe documentación formal del modelo de branching
- 964 commits en `develop` sin mergear a `main` (indica falta de releases regulares)
- Ramas feature sin naming convention clara
- No hay política de cleanup de ramas viejas

**Impacto**:
- Confusión sobre qué rama usar para cada tipo de cambio
- Dificultad para hacer releases estables
- `main` desactualizado (no representa estado de producción)

#### 2. **Deployment Automático NO Implementado**
**Problema**:
```yaml
# ci.yml - deploy-staging job
deploy-staging:
  steps:
    - name: Deploy to staging
      run: |
        echo "🚀 Deploying to staging environment..."
        # TODO: Add actual deployment commands here
```

**Impacto**:
- Deployments manuales (propensos a errores)
- No hay automatización develop → staging
- No hay automatización main → production
- Scripts `deploy.sh` no se usan en CI/CD

#### 3. **Falta de Versionado Semántico**
**Problema**:
- No hay tags de versión (v1.0.0, v1.1.0, etc.)
- No hay changelog automatizado
- No hay política de releases

**Impacto**:
- Imposible hacer rollback a versión específica
- No se puede trackear qué features están en producción
- Usuarios/stakeholders no saben qué versión tienen

#### 4. **Environments NO Configurados en GitHub**
**Problema**:
- Workflows referencian environments `staging` y `production`
- Pero no están configurados en Settings → Environments
- Falta secrets para deployment (DATABASE_URL, DEPLOY_KEY, etc.)

**Impacto**:
- Deployment jobs fallan silenciosamente
- No hay approval workflow para producción
- No hay protección contra deploys accidentales

#### 5. **Estrategia de Hotfixes NO Definida**
**Problema**:
- ¿Qué hacer ante un bug crítico en producción?
- No hay rama `hotfix/*` documentada
- No hay proceso de fast-track a main

**Impacto**:
- Tiempo de resolución de incidentes alto
- Necesidad de mergear develop completo (arriesgado)

---

## 2. Modelo de Branching Propuesto

### Modelo Híbrido: **Git Flow Simplificado + GitHub Flow**

#### ¿Por qué Híbrido?

**Git Flow tradicional** es muy pesado (ramas develop, release, hotfix).
**GitHub Flow** es muy simple (solo main + features).

ContraVento necesita algo **intermedio**:
- ✅ Soporte para staging + production (2 entornos)
- ✅ Desarrollo continuo sin bloqueos
- ✅ Hotfixes rápidos a producción
- ✅ Releases controladas y versionadas

---

### 🌳 Estructura de Ramas

```
main (producción)
  ↑
  │ (PR con approval manual)
  │
develop (staging)
  ↑
  ├── feature/019-followers-tooltip
  ├── feature/020-notifications
  ├── bugfix/fix-gpx-upload
  └── hotfix/v1.2.1-critical-auth-bug
```

---

### 📌 Ramas Principales (Long-lived)

#### **`main`** - Producción Estable
- **Propósito**: Código en producción (https://contravento.com)
- **Deployments**: Automático a producción con approval manual
- **Protection rules**:
  - ✅ Require PR review (1+ approvers)
  - ✅ Require status checks (all CI jobs passing)
  - ✅ No force push
  - ✅ No delete
- **Versioning**: Cada merge crea tag semver (v1.2.0, v1.3.0)
- **Merge desde**: `develop` (releases) o `hotfix/*` (fixes críticos)

#### **`develop`** - Staging & Integration
- **Propósito**: Integración continua de features (https://staging.contravento.com)
- **Deployments**: Automático a staging en cada push
- **Protection rules**:
  - ✅ Require PR review (1+ approvers - puede ser self-approve)
  - ✅ Require status checks (backend + frontend tests)
  - ⚠️ Allow force push (solo owner, con precaución)
- **Merge desde**: `feature/*`, `bugfix/*`
- **Merge hacia**: `main` (via release PR)

---

### 🔀 Ramas Temporales (Short-lived)

#### **`feature/NNN-short-name`** - Nuevas Features
- **Naming**: `feature/019-followers-tooltip`
- **Branch desde**: `develop`
- **Merge hacia**: `develop` (via PR)
- **Lifetime**: 1-14 días
- **Cleanup**: Eliminar después de merge

**Ejemplo**:
```bash
git checkout develop
git pull origin develop
git checkout -b feature/019-followers-tooltip
# ... desarrollo ...
git push origin feature/019-followers-tooltip
# Crear PR: feature/019-followers-tooltip → develop
# Después de merge: eliminar rama
```

#### **`bugfix/fix-description`** - Bugs No Críticos
- **Naming**: `bugfix/fix-gpx-upload-timeout`
- **Branch desde**: `develop`
- **Merge hacia**: `develop` (via PR)
- **Lifetime**: 1-3 días
- **Cleanup**: Eliminar después de merge

**Ejemplo**:
```bash
git checkout -b bugfix/fix-gpx-upload-timeout develop
# ... fix ...
git push origin bugfix/fix-gpx-upload-timeout
# PR → develop
```

#### **`hotfix/vX.Y.Z-description`** - Bugs Críticos en Producción
- **Naming**: `hotfix/v1.2.1-critical-auth-bug`
- **Branch desde**: `main` ⚠️ (no develop)
- **Merge hacia**: `main` + `develop` (ambos)
- **Lifetime**: Horas (urgente)
- **Versioning**: Incrementa patch version (1.2.0 → 1.2.1)

**Ejemplo**:
```bash
# Bug crítico detectado en producción (main)
git checkout main
git pull origin main
git checkout -b hotfix/v1.2.1-critical-auth-bug

# ... fix rápido ...
git commit -m "fix: critical authentication bypass vulnerability"
git push origin hotfix/v1.2.1-critical-auth-bug

# PR 1: hotfix → main (approval urgente)
# PR 2: hotfix → develop (backport fix)

# Después de merge a main → tag v1.2.1
git checkout main
git pull origin main
git tag -a v1.2.1 -m "Hotfix: Critical auth bug"
git push origin v1.2.1
```

#### **`release/vX.Y.0`** - Preparación de Release (Opcional)
- **Naming**: `release/v1.3.0`
- **Branch desde**: `develop`
- **Merge hacia**: `main` + `develop`
- **Lifetime**: 1-2 días (QA final)
- **Uso**: Solo si necesitas QA adicional antes de producción

**Flujo**:
```bash
# Cuando develop está listo para release
git checkout -b release/v1.3.0 develop

# Bump version, changelog, tests finales
npm version minor  # 1.2.0 → 1.3.0
git commit -m "chore: bump version to 1.3.0"

# PR 1: release → main (con changelog)
# PR 2: release → develop (backport version bump)
```

---

### 🏷️ Naming Conventions

| Tipo | Pattern | Ejemplo |
|------|---------|---------|
| **Feature** | `feature/NNN-short-description` | `feature/019-followers-tooltip` |
| **Bugfix** | `bugfix/fix-specific-issue` | `bugfix/fix-gpx-timeout` |
| **Hotfix** | `hotfix/vX.Y.Z-critical-issue` | `hotfix/v1.2.1-auth-bypass` |
| **Release** | `release/vX.Y.0` | `release/v1.3.0` |
| **Experimental** | `experiment/idea-name` | `experiment/celery-redis` |
| **Documentation** | `docs/update-area` | `docs/update-deployment` |

**Reglas**:
- Usar **kebab-case** (lowercase con guiones)
- Feature number = specs folder number (019 → specs/019-followers-tooltip)
- Descriptivo pero conciso (max 30 caracteres después del prefijo)

---

### 🔒 Branch Protection Rules

#### **`main`** - Máxima Protección
```yaml
Settings → Branches → main:
  ✅ Require a pull request before merging
    - Require approvals: 1
    - Dismiss stale PR approvals when new commits are pushed
  ✅ Require status checks to pass before merging
    - backend-tests
    - frontend-tests
    - backend-quality
    - frontend-quality
  ✅ Require branches to be up to date before merging
  ✅ Do not allow bypassing the above settings
  ✅ Restrict who can push to matching branches (Admins only)
  ❌ Allow force pushes (NEVER)
  ❌ Allow deletions (NEVER)
```

#### **`develop`** - Protección Moderada
```yaml
Settings → Branches → develop:
  ✅ Require a pull request before merging
    - Require approvals: 1 (puede ser self-approve para owner)
  ✅ Require status checks to pass before merging
    - backend-tests
    - frontend-tests
  ⚠️ Allow force pushes (solo owner, con precaución extrema)
  ❌ Allow deletions
```

---

## 3. Pipeline CI/CD Completo

### 🔄 Workflow Actual vs Propuesto

#### **Estado Actual** (Parcialmente Implementado)
```
[feature branch] → PR → [develop]
                           ↓
                    ❌ Build Docker images (NOT IMPLEMENTED)

[develop] → PR → [main]
                  ↓
           ❌ Build Docker images (NOT IMPLEMENTED)
           ❌ Push to Docker Hub (NOT IMPLEMENTED)
```

#### **Propuesta: Modelo Semi-Automático**
```
[feature/NNN] → PR + Tests → [develop]
                               ↓ (auto)
                        ✅ Build staging images
                        ✅ Push to Docker Hub
                        ✅ Tag: staging-latest, staging-{SHA}
                               ↓ (manual - SSH al servidor)
                        👤 Deploy to Staging: ./deploy.sh staging --pull-latest
                        👤 Smoke tests + QA manual
                               ↓ (cuando listo)
[develop] → Release PR → [main]
                          ↓ (auto)
                   ✅ Build production images
                   ✅ Push to Docker Hub
                   ✅ Tag: latest, v1.3.0
                   ✅ Create Git Tag
                   ✅ Generate Changelog
                          ↓ (manual - SSH al servidor)
                   👤 Deploy to Production: ./deploy.sh prod --pull-version v1.3.0
                   👤 Health checks + monitoring
```

---

### 🚀 Jobs del Pipeline

#### **1. Feature Branch → develop**

```yaml
# Triggered: PR to develop
jobs:
  - changes (detect backend/frontend)
  - backend-quality (black, ruff, mypy)
  - frontend-quality (eslint, tsc)
  - backend-tests (unit + integration, coverage ≥90%)
  - frontend-tests (vitest, coverage ≥80%)
  - e2e-tests (playwright, 3 browsers)
  - security-scan (trivy, safety)

# Si todos pasan → Merge allow
# Después de merge → Trigger deploy-staging
```

#### **2. develop → Build Staging Image (Automático)**

```yaml
# Triggered: Push to develop
build-staging-image:
  steps:
    - Checkout code
    - Set up Docker Buildx
    - Login to Docker Hub
    - Build Docker images (backend + frontend)
      - Tag: jfdelafuente/contravento-backend:staging-latest
      - Tag: jfdelafuente/contravento-backend:staging-${GITHUB_SHA}
      - Tag: jfdelafuente/contravento-frontend:staging-latest
      - Tag: jfdelafuente/contravento-frontend:staging-${GITHUB_SHA}
    - Push to Docker Hub
    - Notify Slack: "✅ Staging images built and pushed to Docker Hub"
```

**Deploy a Staging (Manual)**:
```bash
# En servidor staging (SSH manual o script)
ssh staging-server
cd /opt/contravento
./deploy.sh staging --pull-latest  # Pull staging-latest from Docker Hub
# O específica un commit SHA:
./deploy.sh staging --pull-commit abc123def
```

**Herramientas**:
- Docker Hub (registry centralizado)
- docker-compose con image tags configurables
- deploy.sh actualizado para pull desde registry

#### **3. develop → main (Release PR)**

```yaml
# Triggered: PR from develop to main
jobs:
  - All tests (backend + frontend + e2e)
  - Build production artifacts
  - Generate changelog (desde último tag)
  - Validate version bump
  - Require manual approval (GitHub Environments)
```

#### **4. main → Build Production Image (Automático)**

```yaml
# Triggered: Push to main
build-production-image:
  steps:
    - Checkout code
    - Set up Docker Buildx
    - Login to Docker Hub
    - Build Docker images (backend + frontend)
      - Tag: jfdelafuente/contravento-backend:latest
      - Tag: jfdelafuente/contravento-backend:v${VERSION}
      - Tag: jfdelafuente/contravento-frontend:latest
      - Tag: jfdelafuente/contravento-frontend:v${VERSION}
    - Push to Docker Hub
    - Create Git tag (v1.3.0)
    - Generate GitHub Release with changelog
    - Notify team: "🎉 Production images ready for deployment"
```

**Deploy a Production (Manual)**:
```bash
# Después de verificar staging, deploy manual a producción
ssh production-server
cd /opt/contravento

# Deploy specific version (recommended)
./deploy.sh prod --pull-version v1.3.0

# O pull latest (solo si confianza total)
./deploy.sh prod --pull-latest

# Verificar health checks
curl https://contravento.com/health

# Rollback si problemas
./deploy.sh prod --rollback-to v1.2.0
```

---

### 🔥 Hotfix Workflow

```yaml
# Triggered: PR from hotfix/* to main
jobs:
  - Fast-track tests (solo críticos, <5 min)
  - Security scan
  - Build production

# Después de merge a main:
  - Deploy to production (approval urgente)
  - Create patch tag (v1.2.1)
  - Backport PR: hotfix → develop
```

---

## 4. Estrategia de Releases

### 📦 Versionado Semántico (SemVer)

**Formato**: `vMAJOR.MINOR.PATCH`

- **MAJOR** (v2.0.0): Breaking changes incompatibles con API anterior
- **MINOR** (v1.3.0): Nuevas features backward-compatible
- **PATCH** (v1.2.1): Bug fixes backward-compatible

**Ejemplos**:
```
v1.0.0 → MVP inicial en producción
v1.1.0 → Feature 019 (followers tooltip)
v1.2.0 → Feature 020 (notifications)
v1.2.1 → Hotfix: critical auth bug
v1.3.0 → Feature 021 + 022 + 023
v2.0.0 → Backend API v2 (breaking changes)
```

---

### 🏷️ Tagging Strategy

#### **Cuándo Crear Tags**

1. **Después de merge a `main`** (siempre)
2. **Automático via GitHub Actions** (preferido)
3. **Manual solo para hotfixes** (si CI falla)

#### **Comandos**

```bash
# Opción 1: Automático (GitHub Actions)
# Tag creado automáticamente en deploy-production job

# Opción 2: Manual (solo si necesario)
git checkout main
git pull origin main
git tag -a v1.3.0 -m "Release v1.3.0: Followers tooltip + Notifications"
git push origin v1.3.0
```

#### **Metadata en Tags**

```bash
git tag -a v1.3.0 -m "
Release v1.3.0 (2026-02-15)

## Features
- Feature 019: Followers/Following tooltips
- Feature 020: Notification system

## Fixes
- Fix GPX upload timeout
- Fix elevation chart gradient colors

## Breaking Changes
None

## Migration
No migration required
"
```

---

### 📝 Changelog Automatizado

**Herramienta**: `conventional-changelog` (genera desde commits)

#### **Commit Message Convention**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: Nueva feature
- `fix`: Bug fix
- `docs`: Cambios en documentación
- `chore`: Tareas de mantenimiento
- `refactor`: Refactoring sin cambios funcionales
- `test`: Añadir tests
- `perf`: Mejora de performance

**Ejemplos**:
```bash
feat(dashboard): add followers tooltip on social stats cards
fix(gpx): resolve upload timeout for large files
docs(deployment): update staging environment guide
chore(deps): bump react from 18.2.0 to 18.3.0
```

#### **Generación de Changelog**

```bash
# Install conventional-changelog
npm install -g conventional-changelog-cli

# Generate CHANGELOG.md
conventional-changelog -p angular -i CHANGELOG.md -s

# Contenido generado:
# CHANGELOG.md
## [1.3.0] - 2026-02-15
### Features
* **dashboard**: add followers tooltip on social stats cards ([a1b2c3d](commit-link))
* **notifications**: implement real-time notification system ([e4f5g6h](commit-link))

### Bug Fixes
* **gpx**: resolve upload timeout for large files ([i7j8k9l](commit-link))
```

---

### 🎯 Release Cadence

| Tipo | Frecuencia | Trigger |
|------|-----------|---------|
| **Patch** (v1.2.1) | Ad-hoc (hotfixes) | Bug crítico en prod |
| **Minor** (v1.3.0) | Bi-weekly | Features completadas en develop |
| **Major** (v2.0.0) | Quarterly | Breaking changes acumulados |

**Ejemplo Calendario**:
```
Semana 1-2: Desarrollo features en branches
  → feature/019, feature/020, bugfix/fix-gpx

Semana 3: Integración en develop
  → Merge PRs → Auto-deploy a staging
  → QA manual en staging

Semana 4: Release a main
  → PR develop → main
  → Approval + Deploy to production
  → Tag v1.3.0
  → Comunicar release notes
```

---

## 5. Workflow End-to-End

### 🔄 Flujo Completo: Feature → Production

#### **Fase 1: Desarrollo (Developer)**

```bash
# 1. Sincronizar develop
git checkout develop
git pull origin develop

# 2. Crear feature branch
git checkout -b feature/019-followers-tooltip

# 3. Desarrollo con commits pequeños
git commit -m "feat(dashboard): add useFollowersTooltip hook"
git commit -m "feat(dashboard): add SocialStatTooltip component"
git commit -m "feat(dashboard): integrate tooltip with SocialStatsSection"
git commit -m "test(dashboard): add unit tests for tooltip"
git commit -m "docs(dashboard): document tooltip accessibility"

# 4. Push a GitHub
git push origin feature/019-followers-tooltip

# 5. Crear Pull Request (GitHub UI)
# Title: "Feature 019: Dashboard Followers/Following Tooltips"
# Description: Link a specs/019-followers-tooltip/spec.md
# Reviewers: Assign 1+ reviewers
```

#### **Fase 2: Code Review (Reviewer)**

```
1. GitHub → Pull Requests → #59
2. Revisar cambios:
   ✅ Spec implementada correctamente
   ✅ Tests añadidos (coverage ≥90%)
   ✅ Código sigue estándares (linter pass)
   ✅ No secrets hardcodeados
   ✅ Accesibilidad WCAG 2.1 AA
3. Aprobar o Request Changes
4. Si aprobado → Developer puede mergear
```

#### **Fase 3: Merge a develop → Build Images (Automático)**

```yaml
# GitHub Actions triggered on merge to develop
jobs:
  - ✅ backend-quality (si backend cambió)
  - ✅ frontend-quality (si frontend cambió)
  - ✅ backend-tests
  - ✅ frontend-tests
  - ✅ e2e-tests
  - ✅ security-scan

# Si todos pasan → build-staging-image triggered
build-staging-image:
  - Build Docker images (backend + frontend)
  - Tag: staging-latest, staging-{GITHUB_SHA}
  - Push to Docker Hub
  - Notify Slack: "✅ Staging images built: staging-abc123d"
```

**Deploy Manual a Staging**:
```bash
# Desarrollador o DevOps hace SSH al servidor
ssh staging-server
cd /opt/contravento

# Pull y deploy imágenes recién construidas
./deploy.sh staging --pull-latest

# Logs para verificar deployment
docker-compose logs -f backend frontend
```

**Verificación Manual en Staging**:
```
1. Abrir https://staging.contravento.com
2. Login con test user
3. Ir a dashboard
4. Hover sobre "Seguidores" → verificar tooltip
5. Hover sobre "Siguiendo" → verificar tooltip
6. Click en username → verificar navegación
7. Verificar mobile (touch navigation)
8. ✅ Confirmar que funciona correctamente
```

#### **Fase 4: Preparación de Release (Release Manager)**

```bash
# Cada 2 semanas: Release a producción

# 1. Crear Release PR
# GitHub UI: New Pull Request
# Base: main ← Compare: develop
# Title: "Release v1.3.0: Followers Tooltip + Notifications"

# 2. Descripción del PR (usar plantilla)
# - Lista de features incluidas (019, 020)
# - Lista de bugfixes
# - Breaking changes (si aplica)
# - Migration steps (si aplica)

# 3. Asignar reviewers (Lead + Stakeholder)

# 4. Esperar aprobación
```

#### **Fase 5: Merge a main → Build Production Images (Automático)**

```yaml
# GitHub Actions triggered on merge to main
jobs:
  - ✅ All tests (último check)
  - ✅ Build production artifacts

# build-production-image triggered
build-production-image:
  - Extract version from package.json or calculate from commits
  - Build Docker images (backend + frontend)
  - Tag: latest, v1.3.0, production-{GITHUB_SHA}
  - Push to Docker Hub
  - Create Git tag v1.3.0
  - Generate GitHub Release with changelog
  - Notify Slack: "🎉 Production images ready: v1.3.0"
```

**Deploy Manual a Production** (Después de Approval del Team Lead):
```bash
# Team Lead o DevOps hace SSH al servidor
ssh production-server
cd /opt/contravento

# IMPORTANTE: Siempre usar versión específica en producción
./deploy.sh prod --pull-version v1.3.0

# Verificar deployment
curl https://contravento.com/health
docker-compose ps

# Monitorear logs primeros 5 minutos
docker-compose logs -f --tail=100 backend frontend

# Si todo OK → Anunciar deployment
# Si problemas → Rollback inmediato
./deploy.sh prod --rollback-to v1.2.0
```

#### **Fase 6: Post-Deployment**

```bash
# 1. Verificación en Producción
https://contravento.com → Login → Dashboard → Test tooltip

# 2. Monitoring (primeras 24h)
- Check error logs
- Check performance metrics
- Check user analytics

# 3. Comunicación
- Email a stakeholders
- Release notes en blog/changelog
- Social media announcement (si aplica)

# 4. Cleanup
# Eliminar feature branch mergeada
git branch -d feature/019-followers-tooltip
git push origin --delete feature/019-followers-tooltip
```

---

### 🔥 Flujo de Hotfix (Urgente)

```bash
# Bug crítico detectado en producción
# Ejemplo: Authentication bypass vulnerability

# 1. Crear hotfix branch desde main
git checkout main
git pull origin main
git checkout -b hotfix/v1.2.1-critical-auth-bug

# 2. Fix rápido (solo lo esencial)
# ... código ...
git commit -m "fix(auth): patch critical authentication bypass (CVE-2026-12345)"

# 3. Push + PR urgente
git push origin hotfix/v1.2.1-critical-auth-bug
# PR: hotfix → main (marcar como URGENT)

# 4. Fast-track review (1 approver, <1 hora)
# Reviewer aprueba → Merge

# 5. Auto-deploy to production
# GitHub Actions:
#   - Tests críticos (5 min)
#   - Deploy with urgent approval
#   - Tag v1.2.1
#   - Notify incidents channel

# 6. Backport a develop
git checkout develop
git merge hotfix/v1.2.1-critical-auth-bug
git push origin develop

# 7. Cleanup
git branch -d hotfix/v1.2.1-critical-auth-bug
git push origin --delete hotfix/v1.2.1-critical-auth-bug
```

---

## 6. Plan de Implementación

### 📅 Roadmap de Mejoras (8 Semanas)

#### **Semana 1-2: Cleanup y Documentación**

**Tareas**:
1. ✅ Documentar estrategia de branching (este documento)
2. ✅ Actualizar README.md con badges de CI/CD
3. ✅ Añadir CONTRIBUTING.md con guía de branching
4. 🔧 Cleanup de ramas viejas:
   - Eliminar ramas mergeadas hace >30 días
   - Archivar ramas experimentales
   - Verificar estado de 009-gps-coordinates-frontend
5. 🔧 Sincronizar main con develop:
   - Crear Release PR: develop → main
   - Aprobar y mergear (este es el objetivo inmediato)
   - Tag como v1.0.0 (MVP baseline)

**Entregables**:
- [ ] BRANCHING_STRATEGY_CICD.md (este doc)
- [ ] CONTRIBUTING.md
- [ ] README.md actualizado con badges
- [ ] main sincronizado con develop

---

#### **Semana 3-4: Configurar Docker Hub y Repository Secrets**

**Tareas**:
1. Configurar **Docker Hub**:
   ```
   1. Crear cuenta en Docker Hub (si no existe)
   2. Crear organization: "contravento"
   3. Crear repositorios:
      - jfdelafuente/contravento-backend (public o private)
      - jfdelafuente/contravento-frontend (public o private)
   4. Generar Access Token:
      - Docker Hub → Account Settings → Security
      - New Access Token → Read/Write permissions
   ```

2. Configurar **GitHub Repository Secrets**:
   ```
   Settings → Secrets and variables → Actions → New repository secret

   Secrets requeridos:
   - DOCKERHUB_USERNAME: tu-usuario-dockerhub
   - DOCKERHUB_TOKEN: token-generado-en-paso-anterior
   ```

3. **Opcional**: Configurar GitHub Environments (para tracking):
   ```
   Settings → Environments → New environment

   Staging environment:
   - Name: "staging"
   - Protection rules: None
   - Environment URL: https://staging.contravento.com
   - Nota: Solo para tracking, no para secrets

   Production environment:
   - Name: "production"
   - Protection rules: None (deployment es manual)
   - Environment URL: https://contravento.com
   ```

4. Preparar servidores remotos:
   - Docker + docker-compose instalado
   - Scripts deploy.sh actualizados en `/opt/contravento/`
   - Nginx configurado
   - Credenciales Docker Hub (docker login en servidor)

**Entregables**:
- [ ] Docker Hub account y repositories creados
- [ ] GitHub secrets configurados (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- [ ] Servidores con Docker Hub login configurado
- [ ] deploy.sh actualizado con función pull_from_dockerhub()
- [ ] Documentación en docs/deployment/docker-hub-setup.md

---

#### **Semana 5-6: Implementar Auto-Build de Docker Images**

**Tareas**:
1. Actualizar `.github/workflows/ci.yml`:
   ```yaml
   build-staging-image:
     name: Build Staging Docker Images
     runs-on: ubuntu-latest
     if: github.ref == 'refs/heads/develop' && github.event_name == 'push'

     steps:
       - name: Checkout code
         uses: actions/checkout@v4

       - name: Set up Docker Buildx
         uses: docker/setup-buildx-action@v3

       - name: Login to Docker Hub
         uses: docker/login-action@v3
         with:
           username: ${{ secrets.DOCKERHUB_USERNAME }}
           password: ${{ secrets.DOCKERHUB_TOKEN }}

       - name: Build and push backend
         uses: docker/build-push-action@v5
         with:
           context: ./backend
           push: true
           tags: |
             jfdelafuente/contravento-backend:staging-latest
             jfdelafuente/contravento-backend:staging-${{ github.sha }}
           cache-from: type=registry,ref=jfdelafuente/contravento-backend:staging-latest
           cache-to: type=inline

       - name: Build and push frontend
         uses: docker/build-push-action@v5
         with:
           context: ./frontend
           push: true
           build-args: |
             VITE_API_URL=https://staging.contravento.com/api
           tags: |
             jfdelafuente/contravento-frontend:staging-latest
             jfdelafuente/contravento-frontend:staging-${{ github.sha }}

       - name: Notify Slack
         run: |
           echo "✅ Staging images built: staging-latest, staging-${GITHUB_SHA}"
   ```

2. Implementar build-production-image similar (con tags: latest, v1.3.0)

3. Actualizar deploy.sh para pull desde Docker Hub:
   ```bash
   # En deploy.sh - añadir función
   pull_from_dockerhub() {
       local env=$1
       local version=$2  # "latest", "staging-latest", "v1.3.0", etc.

       echo "Pulling images from Docker Hub..."
       docker pull jfdelafuente/contravento-backend:${version}
       docker pull jfdelafuente/contravento-frontend:${version}

       # Tag como latest para docker-compose
       docker tag jfdelafuente/contravento-backend:${version} jfdelafuente/contravento-backend:latest
       docker tag jfdelafuente/contravento-frontend:${version} jfdelafuente/contravento-frontend:latest
   }
   ```

4. Testear workflow:
   - Hacer cambio trivial en develop
   - Verificar auto-build + push a Docker Hub
   - SSH a staging server
   - Ejecutar: `./deploy.sh staging --pull-latest`
   - Verificar deployment funciona

**Entregables**:
- [ ] build-staging-image job funcional
- [ ] build-production-image job funcional
- [ ] Images en Docker Hub con tags correctos
- [ ] deploy.sh actualizado para pull desde registry
- [ ] Documentación de deployment manual

---

#### **Semana 7: Implementar Tagging y Changelog**

**Tareas**:
1. Añadir job `create-release` en ci.yml:
   ```yaml
   create-release:
     runs-on: ubuntu-latest
     needs: deploy-production
     if: github.ref == 'refs/heads/main'
     steps:
       - name: Checkout
         uses: actions/checkout@v4
         with:
           fetch-depth: 0  # Full history for changelog

       - name: Get version
         id: version
         run: |
           # Extract from package.json or auto-increment
           echo "version=v1.3.0" >> $GITHUB_OUTPUT

       - name: Generate changelog
         run: |
           npm install -g conventional-changelog-cli
           conventional-changelog -p angular -i CHANGELOG.md -s

       - name: Create Git tag
         run: |
           git config user.name "GitHub Actions"
           git config user.email "actions@github.com"
           git tag -a ${{ steps.version.outputs.version }} -m "Release ${{ steps.version.outputs.version }}"
           git push origin ${{ steps.version.outputs.version }}

       - name: Create GitHub Release
         uses: actions/create-release@v1
         env:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         with:
           tag_name: ${{ steps.version.outputs.version }}
           release_name: Release ${{ steps.version.outputs.version }}
           body_path: CHANGELOG.md
   ```

2. Configurar conventional commits:
   - Añadir commitlint config
   - Añadir pre-commit hook
   - Documentar en CONTRIBUTING.md

**Entregables**:
- [ ] Auto-tagging en main merges
- [ ] Changelog generado automáticamente
- [ ] GitHub Releases creados
- [ ] Commits siguiendo conventional format

---

#### **Semana 8: Testing y Rollout**

**Tareas**:
1. Test completo del workflow:
   - Feature branch → develop → staging
   - develop → main → production (con approval)
   - Hotfix → main → production (fast-track)

2. Documentar escenarios de rollback:
   - Rollback via Git (revert commit)
   - Rollback via Docker (previous image tag)
   - Rollback via deploy script (specify version)

3. Training del equipo:
   - Presentación de la estrategia
   - Walkthrough de workflows
   - Q&A session

4. Comunicar a stakeholders:
   - Email con nueva estrategia
   - Changelog de cambios en proceso
   - Calendario de releases

**Entregables**:
- [ ] Workflow testeado end-to-end
- [ ] Rollback procedures documentados
- [ ] Equipo entrenado
- [ ] Stakeholders informados
- [ ] Go-live de la nueva estrategia

---

## 7. Mejoras Propuestas

### 🚀 Quick Wins (Implementar YA)

#### 1. **Crear Release v1.0.0 (Esta Semana)**
```bash
# PR inmediato: develop → main
# Tag como v1.0.0 (MVP baseline)
# Esto establece punto de partida para SemVer
```

#### 2. **Branch Protection Rules**
```
Settings → Branches:
  - Protect main (require reviews + status checks)
  - Protect develop (require status checks)
```

#### 3. **README Badges**
```markdown
[![CI/CD](https://github.com/.../workflows/ci.yml/badge.svg)](...)
[![Coverage](https://codecov.io/.../badge.svg)](...)
[![Deploy](https://img.shields.io/badge/deploy-staging-blue)]
```

#### 4. **CONTRIBUTING.md**
```markdown
# Crear guía para contributors
- Branching strategy
- Commit message format
- PR template
- Review process
```

---

### 🎯 Medium-term (Próximos 3 Meses)

#### 1. **Automated Version Bumping**
- Usar `semantic-release` para auto-increment
- Basado en conventional commits
- Actualiza package.json automáticamente

#### 2. **Blue-Green Deployment**
- Deploy a new container sin downtime
- Health check antes de switch
- Rollback instantáneo si falla

#### 3. **Database Migration Strategy**
- Migrations en CI/CD pipeline
- Rollback de migrations
- Backup pre-migration

#### 4. **Feature Flags**
- Toggle features en runtime
- A/B testing
- Gradual rollout

#### 5. **Monitoring & Alerting**
- Sentry para error tracking
- Grafana + Prometheus para métricas
- Alertas en Slack/Discord

---

### 🔮 Long-term (6+ Meses)

#### 1. **Multi-Environment**
- Añadir `dev` environment (pre-staging)
- Añadir `preview` deploys para PRs
- Environment por feature branch (opcional)

#### 2. **Canary Releases**
- Deploy a 10% de usuarios primero
- Monitor errors/performance
- Rollout gradual si metrics OK

#### 3. **Infrastructure as Code**
- Terraform para servers
- Ansible para configuración
- GitOps workflow

#### 4. **Security Enhancements**
- SAST (Static Analysis) con SonarQube
- DAST (Dynamic Analysis) con OWASP ZAP
- Dependency scanning con Snyk

---

## 8. Preguntas Frecuentes

### Q1: ¿Cuándo crear una feature branch vs commitear directo a develop?

**A**: **NUNCA** commitear directo a develop. Siempre usar feature branch + PR, incluso para cambios pequeños.

**Excepción**: Hotfixes críticos pueden commitear a develop DESPUÉS de mergear a main.

---

### Q2: ¿Puedo hacer force push a develop?

**A**: Solo el owner y **con extrema precaución**. Avisar al equipo antes.

Casos válidos:
- Rebase de feature branch antes de merge
- Revertir commit problemático reciente

Casos inválidos:
- Reescribir historia pública (>24 horas)
- Ocultar errores

---

### Q3: ¿Qué hacer si olvidé hacer PR y commiteé directo a develop?

**A**:
```bash
# 1. Revertir commit en develop
git revert <commit-hash>
git push origin develop

# 2. Crear feature branch desde commit original
git checkout -b feature/my-changes <commit-hash>
git push origin feature/my-changes

# 3. Crear PR normal
```

---

### Q4: ¿Puedo mergear mi propio PR?

**A**:
- **develop**: Sí (después de approval y CI pass)
- **main**: No (requiere reviewer diferente)

---

### Q5: ¿Cómo hago rollback de un deploy fallido?

**A**:

**Opción 1: Revert commit**
```bash
git revert <bad-commit>
git push origin main
# Trigger auto-redeploy
```

**Opción 2: Deploy versión anterior**
```bash
ssh production-server
cd /opt/contravento
./deploy.sh prod --tag v1.2.0  # Version anterior
```

**Opción 3: Docker rollback**
```bash
docker tag contravento-backend:v1.2.0 contravento-backend:latest
docker-compose up -d
```

---

### Q6: ¿Con qué frecuencia hacer releases?

**A**: Depende del ritmo de desarrollo.

**Recomendado**:
- **Bi-weekly** (cada 2 semanas): Si desarrollo activo
- **Monthly** (mensual): Si desarrollo estable
- **Ad-hoc**: Solo para hotfixes críticos

**Regla de oro**: No dejar develop sin mergear a main >4 semanas.

---

## 9. Checklist de Implementación

### ✅ Fase 1: Immediate (Esta Semana)

- [ ] Leer y aprobar este documento
- [ ] Crear PR: develop → main (Release v1.0.0)
- [ ] Mergear PR después de approval
- [ ] Crear tag `v1.0.0` en main
- [ ] Configurar branch protection rules (main + develop)
- [ ] Añadir CI/CD badges a README.md
- [ ] Cleanup de ramas viejas (015-dashboard-redesign, etc.)

### ✅ Fase 2: Short-term (Semanas 3-6)

- [ ] Configurar GitHub Environments (staging + production)
- [ ] Añadir secrets para SSH deployment
- [ ] Implementar deploy-staging job (auto)
- [ ] Implementar deploy-production job (con approval)
- [ ] Testear deployment end-to-end
- [ ] Documentar rollback procedures

### ✅ Fase 3: Medium-term (Semanas 7-8)

- [ ] Implementar auto-tagging en releases
- [ ] Configurar conventional-changelog
- [ ] Añadir commitlint + pre-commit hook
- [ ] Crear CONTRIBUTING.md
- [ ] Training session con equipo
- [ ] Go-live de nueva estrategia

### ✅ Fase 4: Ongoing

- [ ] Review branch strategy mensualmente
- [ ] Cleanup de ramas mergeadas semanalmente
- [ ] Actualizar docs según feedback
- [ ] Monitorear métricas de deployment (MTTR, frequency)

---

## 10. Contacto y Soporte

**Mantenido por**: Development Team
**Última actualización**: 2026-02-12
**Próxima revisión**: 2026-03-12

**Para preguntas o sugerencias**:
- GitHub Issues: [Repo Issues](https://github.com/jfdelafuente/contravento-application-python/issues)
- Slack: #dev-contravento
- Email: dev-team@contravento.com

---

**Este documento es un borrador para aprobación. Requiere:**
1. ✅ Aprobación de Lead Developer
2. ✅ Review de DevOps (si aplica)
3. ✅ Buy-in del equipo completo

**Después de aprobación**:
- Mover a `docs/operations/branching-strategy.md`
- Añadir link desde README.md
- Comunicar a todos los contributors
