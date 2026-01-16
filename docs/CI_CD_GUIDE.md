# Guía de CI/CD - ContraVento

## Índice

1. [¿Qué es CI/CD?](#qué-es-cicd)
2. [Arquitectura del Pipeline](#arquitectura-del-pipeline)
3. [Workflows Implementados](#workflows-implementados)
4. [Configuración de GitHub Actions](#configuración-de-github-actions)
5. [Ejecución de Workflows](#ejecución-de-workflows)
6. [Reportes y Artefactos](#reportes-y-artefactos)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## ¿Qué es CI/CD?

### CI/CD en Términos Simples

**CI/CD** son las siglas de **Continuous Integration / Continuous Deployment** (Integración Continua / Despliegue Continuo).

#### Analogía del Mundo Real

Imagina que estás construyendo un edificio:

**Sin CI/CD** (Construcción Manual):
- 🏗️ Cada obrero trabaja en su propia área sin coordinación
- 🔨 Al final del mes, intentan juntar todas las piezas
- 💥 Muchas piezas no encajan, hay conflictos
- ⏰ Semanas de trabajo para arreglar problemas
- 😰 Estrés y retrasos constantes

**Con CI/CD** (Construcción Automatizada):
- 👷 Los obreros integran su trabajo cada día
- 🔍 Un inspector automático verifica todo inmediatamente
- ✅ Los problemas se detectan y arreglan al instante
- 🚀 El edificio se construye de forma incremental y segura
- 😌 Confianza y velocidad constante

### Componentes de CI/CD

#### CI - Continuous Integration (Integración Continua)

**¿Qué hace?**
Cada vez que un desarrollador hace un commit a GitHub:

1. **Compila el código**: Verifica que no haya errores de sintaxis
2. **Ejecuta tests**: Corre todos los tests automáticos
3. **Verifica calidad**: Revisa estilo de código, linting, tipos
4. **Genera reportes**: Crea informes de cobertura y resultados

**Ejemplo en ContraVento**:
```bash
# Developer hace un commit
git commit -m "Add user profile endpoint"
git push origin feature/user-profile

# GitHub Actions se activa automáticamente:
✅ Backend Tests (pytest)
✅ Frontend Tests (Vitest)
✅ E2E Tests (Playwright)
✅ Code Quality (black, ruff, eslint)
✅ Type Checking (mypy, tsc)

# Si TODO pasa: ✅ PR puede ser aprobado
# Si algo falla: ❌ PR bloqueado, necesita corrección
```

**Beneficio**: Detecta problemas **inmediatamente**, no semanas después.

#### CD - Continuous Deployment (Despliegue Continuo)

**¿Qué hace?**
Después de que CI pasa, automáticamente:

1. **Construye la aplicación**: Crea versiones optimizadas
2. **Ejecuta tests finales**: Smoke tests en staging
3. **Despliega a staging**: Actualiza ambiente de pruebas
4. **Despliega a producción**: (opcional) Actualiza ambiente real

**Ejemplo en ContraVento**:
```bash
# Merge a rama 'develop'
git merge feature/user-profile

# GitHub Actions automáticamente:
✅ Construye imágenes Docker
✅ Ejecuta smoke tests
✅ Despliega a staging.contravento.com
✅ Ejecuta tests E2E en staging
✅ Notifica al equipo

# Si staging es estable por 24h:
✅ Deploy manual a producción (con aprobación)
```

**Beneficio**: Despliegues **rápidos**, **seguros** y **confiables**.

### Comparación: Sin CI/CD vs Con CI/CD

| Aspecto | Sin CI/CD | Con CI/CD |
|---------|-----------|-----------|
| **Detección de bugs** | Días/semanas después | Minutos después |
| **Frecuencia de deploy** | Mensual | Diaria/horaria |
| **Riesgo de deploy** | Alto (cambios acumulados) | Bajo (cambios pequeños) |
| **Tiempo de arreglo** | Horas/días | Minutos |
| **Confianza en el código** | Baja (tests manuales) | Alta (tests automáticos) |
| **Estrés del equipo** | Alto | Bajo |
| **Velocidad de desarrollo** | Lenta | Rápida |

---

## Arquitectura del Pipeline

### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────┐
│  DESARROLLADOR                                                   │
│  git commit -m "Add feature" && git push                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  GITHUB (Repositorio)                                            │
│  - Recibe commit                                                 │
│  - Detecta cambios en código                                     │
│  - Activa GitHub Actions workflows                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬───────────────┐
         │               │               │               │
         ▼               ▼               ▼               ▼
┌────────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
│  BACKEND       │ │  FRONTEND   │ │  E2E TESTS  │ │  DEPLOYMENT  │
│  WORKFLOW      │ │  WORKFLOW   │ │  WORKFLOW   │ │  WORKFLOW    │
└────────┬───────┘ └──────┬──────┘ └──────┬──────┘ └──────┬───────┘
         │                │               │               │
         ▼                ▼               ▼               ▼
┌────────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
│ 1. Setup       │ │ 1. Setup    │ │ 1. Setup    │ │ 1. Build     │
│ 2. Install     │ │ 2. Install  │ │ 2. Install  │ │ 2. Tag       │
│ 3. Lint        │ │ 3. Lint     │ │ 3. Start    │ │ 3. Push      │
│ 4. Type Check  │ │ 4. Type     │ │    Services │ │ 4. Deploy    │
│ 5. Unit Tests  │ │ 5. Build    │ │ 4. Run E2E  │ │ 5. Smoke     │
│ 6. Coverage    │ │ 6. Tests    │ │ 5. Upload   │ │    Tests     │
│ 7. Upload      │ │ 7. Upload   │ │    Reports  │ │ 6. Notify    │
└────────┬───────┘ └──────┬──────┘ └──────┬──────┘ └──────┬───────┘
         │                │               │               │
         └────────────────┴───────┬───────┴───────────────┘
                                  │
                                  ▼
                        ┌──────────────────┐
                        │  ALL JOBS PASS?  │
                        └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              ✅ SUCCESS                 ❌ FAILURE
         ┌──────────────────┐      ┌─────────────────┐
         │ - PR Aprobable   │      │ - PR Bloqueado  │
         │ - Deploy Seguro  │      │ - Notificación  │
         │ - Merge Permitido│      │ - Review Logs   │
         └──────────────────┘      └─────────────────┘
```

### Componentes Clave

#### 1. Triggers (Disparadores)

Los workflows se ejecutan automáticamente cuando:

```yaml
# Ejemplo: backend-tests.yml
on:
  push:
    branches: [main, develop, 'feature/*']
    paths:
      - 'backend/**'
      - '.github/workflows/backend-tests.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'backend/**'
```

**Disparadores configurados**:
- ✅ Push a ramas principales (main, develop)
- ✅ Push a ramas de features (feature/*)
- ✅ Pull Requests a main/develop
- ✅ Cambios en archivos específicos (backend/, frontend/)
- ✅ Ejecución manual (workflow_dispatch)
- ✅ Horarios programados (cron jobs)

#### 2. Jobs (Trabajos)

Cada workflow tiene uno o más jobs que se ejecutan:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install

      - name: Run tests
        run: |
          cd backend
          poetry run pytest --cov=src --cov-report=xml
```

**Jobs configurados en ContraVento**:
- `backend-tests`: Tests unitarios e integración backend
- `frontend-tests`: Tests unitarios frontend
- `e2e-tests`: Tests end-to-end con Playwright
- `build-and-deploy`: Construcción y despliegue

#### 3. Steps (Pasos)

Cada job contiene steps que ejecutan acciones específicas:

- **Checkout**: Descarga el código del repositorio
- **Setup**: Configura entorno (Python, Node.js, etc.)
- **Install**: Instala dependencias
- **Lint**: Verifica estilo de código
- **Test**: Ejecuta tests
- **Build**: Construye la aplicación
- **Deploy**: Despliega a ambientes
- **Upload**: Sube artefactos (reportes, logs)

#### 4. Artifacts (Artefactos)

Archivos generados durante el workflow que se guardan:

```yaml
- name: Upload coverage report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: backend/htmlcov/
    retention-days: 30
```

**Artefactos generados**:
- 📊 Reportes de cobertura (HTML)
- 📸 Screenshots de tests E2E fallidos
- 🎥 Videos de ejecución de Playwright
- 🔍 Traces interactivos de debugging
- 📋 Logs de ejecución

---

## Workflows Implementados

ContraVento tiene **4 workflows principales** configurados en `.github/workflows/`:

### 1. Backend Tests (`backend-tests.yml`)

**Propósito**: Validar calidad y funcionalidad del backend Python/FastAPI

**Triggers**:
- Push a main, develop, feature/*
- Pull requests a main/develop
- Cambios en `backend/` o archivos de workflow

**Jobs**:

#### Job 1: `lint-and-type-check`
```yaml
steps:
  - Setup Python 3.12
  - Install Poetry dependencies
  - Run Black (formatting check)
  - Run Ruff (linting)
  - Run MyPy (type checking)
```

**Verifica**:
- ✅ Código formateado correctamente (black)
- ✅ Sin errores de linting (ruff)
- ✅ Type hints correctos (mypy)

#### Job 2: `test`
```yaml
steps:
  - Setup Python 3.12
  - Install dependencies
  - Run pytest with coverage
  - Generate coverage report
  - Upload coverage artifact
```

**Verifica**:
- ✅ Todos los tests pasan
- ✅ Cobertura ≥ 90%
- ✅ Tests unitarios e integración

**Artefactos generados**:
- `coverage-report/` (HTML con detalles de cobertura)

**Tiempo de ejecución**: ~3-5 minutos

---

### 2. Frontend Tests (`frontend-tests.yml`)

**Propósito**: Validar calidad y funcionalidad del frontend React/TypeScript

**Triggers**:
- Push a main, develop, feature/*
- Pull requests a main/develop
- Cambios en `frontend/` o archivos de workflow

**Jobs**:

#### Job 1: `lint-and-type-check`
```yaml
steps:
  - Setup Node.js 20.x
  - Install npm dependencies (with cache)
  - Run ESLint (linting)
  - Run TypeScript compiler (type check)
```

**Verifica**:
- ✅ Código sin errores de linting
- ✅ Tipos TypeScript correctos
- ✅ Imports válidos

#### Job 2: `test`
```yaml
steps:
  - Setup Node.js 20.x
  - Install dependencies
  - Run Vitest with coverage
  - Generate coverage report
  - Upload coverage artifact
```

**Verifica**:
- ✅ Tests unitarios pasan
- ✅ Cobertura ≥ 80%
- ✅ Componentes React funcionan

#### Job 3: `build`
```yaml
steps:
  - Setup Node.js 20.x
  - Install dependencies
  - Build production bundle
  - Verify bundle size
```

**Verifica**:
- ✅ Aplicación compila sin errores
- ✅ Bundle optimizado (<500 KB gzipped)
- ✅ Sin warnings de producción

**Artefactos generados**:
- `frontend-coverage/` (Reporte de cobertura)
- `frontend-build/` (Bundle de producción)

**Tiempo de ejecución**: ~4-6 minutos

---

### 3. E2E Tests (`e2e-tests.yml`)

**Propósito**: Validar flujos completos de usuario con Playwright

**Triggers**:
- Push a main, develop
- Pull requests a main/develop
- Cambios en `frontend/tests/e2e/` o archivos de workflow
- Manual (workflow_dispatch)

**Jobs**:

#### Job 1: `e2e-tests`
```yaml
strategy:
  matrix:
    browser: [chromium, firefox, webkit]

steps:
  - Setup Node.js 20.x
  - Install dependencies
  - Install Playwright browsers
  - Start backend (FastAPI)
  - Start frontend (Vite)
  - Wait for services (health checks)
  - Run Playwright tests
  - Upload artifacts (screenshots, videos, traces)
```

**Verifica**:
- ✅ 57 tests E2E en 3 navegadores (171 ejecuciones)
- ✅ Autenticación funciona
- ✅ Creación de viajes funciona
- ✅ Feed público funciona
- ✅ Mapas interactivos funcionan

**Matrix Strategy**:
El workflow ejecuta tests en paralelo en 3 navegadores:

```yaml
matrix:
  browser: [chromium, firefox, webkit]
```

**Resultado**: 3 jobs simultáneos (uno por navegador)

**Artefactos generados**:
- `playwright-report-chromium/` (Reporte HTML + screenshots)
- `playwright-report-firefox/` (Reporte HTML + screenshots)
- `playwright-report-webkit/` (Reporte HTML + screenshots)
- Videos de tests fallidos (automático)
- Traces para debugging (automático)

**Tiempo de ejecución**: ~8-12 minutos (paralelo)

---

### 4. Deployment (`deploy-staging.yml`)

**Propósito**: Desplegar automáticamente a staging después de CI exitoso

**Triggers**:
- Push a rama `develop`
- Manual (workflow_dispatch)

**Jobs**:

#### Job 1: `build`
```yaml
steps:
  - Checkout code
  - Setup Docker Buildx
  - Login to Docker Hub
  - Build backend image
  - Build frontend image
  - Tag images (staging-YYYYMMDD-SHA)
  - Push images to registry
```

**Genera**:
- `contravento-backend:staging-20260116-a1b2c3d`
- `contravento-frontend:staging-20260116-a1b2c3d`

#### Job 2: `deploy`
```yaml
steps:
  - SSH to staging server
  - Pull latest images
  - Update docker-compose.yml
  - Run docker compose up -d
  - Wait for services to start
  - Run smoke tests
  - Notify team (Slack/Discord)
```

**Verifica**:
- ✅ Servicios iniciados correctamente
- ✅ Health checks pasan
- ✅ Smoke tests pasan
- ✅ No errores en logs

**Notificaciones**:
- ✅ Slack: Deploy exitoso con link a staging
- ❌ Slack: Deploy fallido con logs de error
- 📧 Email: Resumen de deploy (opcional)

**Tiempo de ejecución**: ~5-8 minutos

---

## Configuración de GitHub Actions

### Requisitos Previos

#### 1. Secrets de GitHub

Los workflows necesitan credenciales seguras configuradas en:
**Settings → Secrets and variables → Actions**

**Secrets requeridos**:

```bash
# Docker Hub (para push de imágenes)
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password

# Staging Server (para deploy)
STAGING_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
STAGING_HOST=staging.contravento.com
STAGING_USER=deploy

# Production Server (opcional)
PRODUCTION_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----...
PRODUCTION_HOST=contravento.com
PRODUCTION_USER=deploy

# Notificaciones (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

**Cómo añadir secrets**:

1. Ve a tu repositorio en GitHub
2. Click en **Settings** → **Secrets and variables** → **Actions**
3. Click en **New repository secret**
4. Nombre: `DOCKER_USERNAME`
5. Valor: `tu-usuario-docker`
6. Click **Add secret**
7. Repetir para cada secret

#### 2. GitHub Environments

Configura ambientes para deploy controlado:

**Settings → Environments → New environment**

**Ambientes recomendados**:

1. **staging**
   - Protection rules: None (deploy automático)
   - Secrets: `STAGING_SSH_KEY`, `STAGING_HOST`

2. **production**
   - Protection rules:
     - ✅ Required reviewers (2 personas)
     - ✅ Wait timer (5 minutos)
   - Secrets: `PRODUCTION_SSH_KEY`, `PRODUCTION_HOST`

**Ejemplo de uso en workflow**:

```yaml
deploy-production:
  runs-on: ubuntu-latest
  environment: production  # Requiere aprobación manual
  steps:
    - name: Deploy to production
      run: echo "Deploying to ${{ secrets.PRODUCTION_HOST }}"
```

#### 3. Branch Protection Rules

Configura reglas para proteger ramas principales:

**Settings → Branches → Add rule**

**Para rama `main`**:

```yaml
Branch name pattern: main

Protection rules:
✅ Require a pull request before merging
  ✅ Require approvals: 2
  ✅ Dismiss stale pull request approvals when new commits are pushed

✅ Require status checks to pass before merging
  ✅ Require branches to be up to date before merging
  Status checks:
    - backend-tests / lint-and-type-check
    - backend-tests / test
    - frontend-tests / lint-and-type-check
    - frontend-tests / test
    - frontend-tests / build
    - e2e-tests / e2e-tests (chromium)
    - e2e-tests / e2e-tests (firefox)
    - e2e-tests / e2e-tests (webkit)

✅ Require conversation resolution before merging
✅ Require signed commits (opcional)
✅ Include administrators
```

**Para rama `develop`**:

```yaml
Branch name pattern: develop

Protection rules:
✅ Require a pull request before merging
  ✅ Require approvals: 1

✅ Require status checks to pass before merging
  Status checks:
    - backend-tests / test
    - frontend-tests / test
    - e2e-tests / e2e-tests (chromium)
```

### Estructura de Archivos

```
.github/
└── workflows/
    ├── backend-tests.yml          # Tests backend (pytest)
    ├── frontend-tests.yml         # Tests frontend (Vitest)
    ├── e2e-tests.yml              # Tests E2E (Playwright)
    ├── deploy-staging.yml         # Deploy a staging
    ├── deploy-production.yml      # Deploy a production (manual)
    └── performance-tests.yml      # Tests de performance (nightly)
```

### Anatomía de un Workflow

**Ejemplo: backend-tests.yml**

```yaml
# 1. Metadatos del workflow
name: Backend Tests

# 2. Triggers (cuándo se ejecuta)
on:
  push:
    branches: [main, develop, 'feature/*']
    paths:
      - 'backend/**'
      - '.github/workflows/backend-tests.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'backend/**'

# 3. Jobs (trabajos a ejecutar)
jobs:
  # 3.1 Job de linting y type checking
  lint-and-type-check:
    runs-on: ubuntu-latest

    steps:
      # 3.1.1 Checkout del código
      - name: Checkout code
        uses: actions/checkout@v4

      # 3.1.2 Setup de Python
      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      # 3.1.3 Instalación de dependencias
      - name: Install Poetry
        run: |
          cd backend
          pip install poetry
          poetry install

      # 3.1.4 Ejecución de linters
      - name: Run Black
        run: |
          cd backend
          poetry run black --check src/ tests/

      - name: Run Ruff
        run: |
          cd backend
          poetry run ruff check src/ tests/

      - name: Run MyPy
        run: |
          cd backend
          poetry run mypy src/

  # 3.2 Job de tests
  test:
    runs-on: ubuntu-latest
    needs: lint-and-type-check  # Depende del job anterior

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install poetry
          poetry install

      - name: Run tests with coverage
        run: |
          cd backend
          poetry run pytest \
            --cov=src \
            --cov-report=html \
            --cov-report=xml \
            --cov-report=term \
            -v

      # 3.2.1 Upload de artefactos
      - name: Upload coverage report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: backend-coverage-report
          path: backend/htmlcov/
          retention-days: 30

      # 3.2.2 Comentario en PR con cobertura
      - name: Comment coverage on PR
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
```

---

## Ejecución de Workflows

### Ejecución Automática

Los workflows se ejecutan automáticamente cuando se cumplen los triggers:

#### 1. Push a Rama

```bash
# Developer trabaja en feature
git checkout -b feature/add-user-stats
# ... hace cambios en backend/src/services/stats_service.py

# Commit y push
git add .
git commit -m "feat: add user stats calculation"
git push origin feature/add-user-stats

# GitHub Actions se activa automáticamente:
# ✅ backend-tests.yml (detecta cambios en backend/)
# ⏭️  frontend-tests.yml (no hay cambios en frontend/)
# ⏭️  e2e-tests.yml (solo en PRs a main/develop)
```

**Resultado en GitHub UI**:

```
Backend Tests
├── ✅ lint-and-type-check (1m 23s)
│   ├── ✅ Black formatting
│   ├── ✅ Ruff linting
│   └── ✅ MyPy type checking
└── ✅ test (2m 45s)
    ├── ✅ 234 tests passed
    ├── ✅ Coverage: 92%
    └── ✅ Artifact uploaded: backend-coverage-report
```

#### 2. Pull Request

```bash
# Crear PR desde GitHub UI o CLI
gh pr create \
  --title "feat: Add user stats calculation" \
  --body "Implements FR-045 user stats calculation" \
  --base develop \
  --head feature/add-user-stats

# GitHub Actions ejecuta:
# ✅ backend-tests.yml
# ✅ frontend-tests.yml (aunque no hubo cambios, verifica regresión)
# ✅ e2e-tests.yml (verifica integración completa)
```

**Resultado en PR**:

```
Status checks - 8 checks

Required checks:
✅ backend-tests / lint-and-type-check
✅ backend-tests / test
✅ frontend-tests / lint-and-type-check
✅ frontend-tests / test
✅ frontend-tests / build
✅ e2e-tests / e2e-tests (chromium)
✅ e2e-tests / e2e-tests (firefox)
✅ e2e-tests / e2e-tests (webkit)

All checks have passed ✅

This branch has no conflicts with the base branch
Merge pull request
```

#### 3. Merge a Develop

```bash
# Merge del PR (desde GitHub UI o CLI)
gh pr merge 123 --squash --delete-branch

# GitHub Actions ejecuta:
# ✅ backend-tests.yml (verifica develop estable)
# ✅ frontend-tests.yml
# ✅ e2e-tests.yml
# 🚀 deploy-staging.yml (deploy automático a staging)
```

**Resultado del deploy**:

```
Deploy to Staging
├── ✅ build (4m 12s)
│   ├── ✅ Build backend image
│   ├── ✅ Build frontend image
│   └── ✅ Push to Docker Hub
└── ✅ deploy (3m 34s)
    ├── ✅ SSH to staging server
    ├── ✅ Pull latest images
    ├── ✅ Update services
    ├── ✅ Smoke tests passed
    └── ✅ Notification sent to Slack

Staging URL: https://staging.contravento.com
```

### Ejecución Manual

Algunos workflows permiten ejecución manual con `workflow_dispatch`:

#### 1. Desde GitHub UI

1. Ve a **Actions** tab en GitHub
2. Selecciona el workflow (ej: "E2E Tests")
3. Click **Run workflow** (botón derecho)
4. Selecciona rama: `develop`
5. (Opcional) Ingresa parámetros
6. Click **Run workflow** (botón verde)

#### 2. Desde GitHub CLI

```bash
# Ejecutar E2E tests manualmente
gh workflow run e2e-tests.yml \
  --ref develop \
  --field browser=chromium

# Ejecutar deploy a staging manualmente
gh workflow run deploy-staging.yml \
  --ref develop

# Ver estado del workflow
gh run list --workflow=e2e-tests.yml

# Ver logs de la última ejecución
gh run view --log
```

#### 3. Con Parámetros

**Ejemplo: Performance Tests con parámetros**

```yaml
# .github/workflows/performance-tests.yml
on:
  workflow_dispatch:
    inputs:
      test_type:
        description: 'Type of performance test'
        required: true
        type: choice
        options:
          - benchmark
          - load
          - stress
      duration:
        description: 'Test duration (seconds)'
        required: false
        default: '60'
```

**Ejecución**:

```bash
gh workflow run performance-tests.yml \
  --ref main \
  --field test_type=stress \
  --field duration=300
```

### Monitoreo de Workflows

#### 1. GitHub UI

**Actions Tab**:
```
All workflows
├── Backend Tests         ✅ Success (3m 45s)  main  a1b2c3d
├── Frontend Tests        ✅ Success (5m 12s)  main  a1b2c3d
├── E2E Tests            ✅ Success (9m 34s)  main  a1b2c3d
└── Deploy Staging       🚀 In progress...     develop  e4f5g6h
```

**Workflow Detail**:
```
Backend Tests #234
Triggered by jfdelafuente via push
Run duration: 3m 45s
Workflow file: backend-tests.yml

Jobs:
✅ lint-and-type-check (1m 23s)
   ├── ✅ Checkout code
   ├── ✅ Set up Python 3.12
   ├── ✅ Install Poetry
   ├── ✅ Run Black (passed)
   ├── ✅ Run Ruff (passed)
   └── ✅ Run MyPy (passed)

✅ test (2m 45s)
   ├── ✅ Checkout code
   ├── ✅ Set up Python 3.12
   ├── ✅ Install dependencies
   ├── ✅ Run tests (234 passed, 0 failed)
   └── ✅ Upload coverage report (artifact)

Artifacts:
📦 backend-coverage-report (1.2 MB) - expires in 30 days
```

#### 2. GitHub CLI

```bash
# Ver workflows activos
gh run list --limit 10

# Ver detalles de un workflow
gh run view 1234567890

# Ver logs de un job específico
gh run view 1234567890 --job=test --log

# Descargar artefactos
gh run download 1234567890 --name backend-coverage-report

# Re-ejecutar workflow fallido
gh run rerun 1234567890

# Cancelar workflow en ejecución
gh run cancel 1234567890
```

#### 3. Notificaciones

**Email (GitHub)**:
- ❌ Workflow failed (solo si falla)
- ✅ Workflow success (si lo habilitas en Settings)

**Slack (custom)**:
```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "❌ Workflow failed: ${{ github.workflow }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Workflow*: ${{ github.workflow }}\n*Status*: Failed ❌\n*Branch*: ${{ github.ref }}\n*Actor*: ${{ github.actor }}\n*Commit*: <${{ github.event.head_commit.url }}|${{ github.sha }}>"
            }
          }
        ]
      }
```

---

## Reportes y Artefactos

### Tipos de Artefactos

#### 1. Coverage Reports (Cobertura de Código)

**Backend Coverage**:
```
backend-coverage-report/
├── index.html           # Reporte principal
├── src_api_auth.py.html # Detalle por archivo
├── src_services_*.html  # Detalle por servicio
└── coverage.xml         # Formato para herramientas
```

**Cómo acceder**:
1. Ve a workflow en GitHub Actions
2. Scroll hasta **Artifacts**
3. Click **backend-coverage-report** → Download ZIP
4. Descomprime y abre `index.html` en navegador

**Información mostrada**:
- ✅ Cobertura global (92%)
- ✅ Cobertura por archivo
- ✅ Líneas cubiertas (verde) vs no cubiertas (rojo)
- ✅ Branches cubiertas/faltantes

**Frontend Coverage**:
```
frontend-coverage-report/
├── index.html
├── src/components/     # Cobertura de componentes
├── src/hooks/          # Cobertura de hooks
└── src/services/       # Cobertura de servicios
```

#### 2. Playwright Reports (Tests E2E)

**Estructura**:
```
playwright-report-chromium/
├── index.html          # Reporte interactivo
├── data/
│   ├── screenshots/    # Screenshots de tests fallidos
│   ├── videos/         # Videos de ejecución
│   └── traces/         # Traces para debugging
└── test-results/
    ├── auth-login-chromium.txt
    └── trip-creation-chromium.txt
```

**Cómo acceder**:
1. Ve a workflow **E2E Tests**
2. Busca job **e2e-tests (chromium)**
3. Scroll a **Artifacts**
4. Download **playwright-report-chromium**
5. Descomprime y abre `index.html`

**Reporte interactivo muestra**:
- ✅ Tests pasados/fallidos por navegador
- ✅ Duración de cada test
- ✅ Screenshots del último paso antes de fallar
- ✅ Videos completos de ejecución
- ✅ Traces interactivos (timeline de acciones)

**Ejemplo de trace**:

```
Trace Viewer (trace.playwright.dev)

Timeline:
00:00.000 ├── navigate to http://localhost:5173/login
00:00.245 ├── fill input[name="login"] with "testuser"
00:00.512 ├── fill input[name="password"] with "TestPass123!"
00:00.678 ├── click button[type="submit"]
00:01.234 ├── wait for navigation
00:01.456 ├── ❌ expect(page).toHaveURL(/\/dashboard/)
            │   Actual: http://localhost:5173/login?error=invalid
            │   Expected: /\/dashboard/

Screenshots:
📸 Before click: login-before.png
📸 After click: login-after.png (failed state)

Network:
POST /auth/login → 401 Unauthorized
```

#### 3. Build Artifacts (Bundles de Producción)

**Frontend Build**:
```
frontend-build/
└── dist/
    ├── index.html
    ├── assets/
    │   ├── index-a1b2c3d4.js       # Main bundle (gzipped: 145 KB)
    │   ├── vendor-e5f6g7h8.js      # Vendor bundle (gzipped: 180 KB)
    │   └── index-i9j0k1l2.css      # Styles (gzipped: 12 KB)
    └── favicon.ico

Total bundle size: 337 KB (gzipped)
```

**Cómo verificar tamaño**:

```yaml
- name: Check bundle size
  run: |
    cd frontend/dist
    du -sh .
    find assets -name "*.js" -exec gzip -c {} \; | wc -c
```

**Límites recomendados**:
- ✅ Total gzipped: <500 KB
- ✅ Main bundle: <200 KB
- ✅ Vendor bundle: <250 KB
- ⚠️  Warning si excede límites (no falla)

#### 4. Docker Images

**Imágenes generadas**:
```
Docker Hub: contravento/backend:staging-20260116-a1b2c3d
           contravento/frontend:staging-20260116-a1b2c3d

Tags:
- staging-20260116-a1b2c3d (específico)
- staging-latest (alias)
- develop (rama)
```

**Metadata**:
```json
{
  "labels": {
    "git.commit": "a1b2c3d4e5f6",
    "git.branch": "develop",
    "build.date": "2026-01-16T14:23:45Z",
    "build.workflow": "deploy-staging.yml"
  }
}
```

### Descarga de Artefactos

#### Método 1: GitHub UI

1. Ve a **Actions** → selecciona workflow run
2. Scroll a **Artifacts** (bottom)
3. Click en nombre de artefacto → download ZIP
4. Descomprime localmente

#### Método 2: GitHub CLI

```bash
# Listar artefactos de un workflow run
gh run view 1234567890

# Descargar artefacto específico
gh run download 1234567890 --name backend-coverage-report

# Descargar todos los artefactos
gh run download 1234567890

# Descargar a directorio específico
gh run download 1234567890 --dir ./reports/
```

#### Método 3: API de GitHub

```bash
# Obtener lista de artefactos
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/USER/REPO/actions/runs/1234567890/artifacts

# Descargar artefacto
curl -L -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/USER/REPO/actions/artifacts/9876543210/zip \
  -o coverage-report.zip
```

### Retención de Artefactos

**Configuración por defecto**:
```yaml
- name: Upload coverage report
  uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: backend/htmlcov/
    retention-days: 30  # Se borra después de 30 días
```

**Políticas recomendadas**:
- Coverage reports: 30 días
- Playwright reports: 14 días (ocupan mucho espacio)
- Build artifacts: 7 días
- Production builds: 90 días

---

## Troubleshooting

### Problemas Comunes

#### 1. Workflow No Se Ejecuta

**Síntoma**: Push a rama pero workflow no aparece en Actions

**Causas posibles**:

✅ **Path filters no coinciden**:
```yaml
# Workflow solo se ejecuta si hay cambios en backend/
on:
  push:
    paths:
      - 'backend/**'

# Si solo modificaste frontend/, no se ejecuta
```

**Solución**: Verifica que los cambios coincidan con los path filters

✅ **Branch no está en trigger**:
```yaml
on:
  push:
    branches: [main, develop]  # Solo estas ramas

# Si haces push a feature/xyz, no se ejecuta
```

**Solución**: Agrega la rama o usa pattern `'feature/*'`

✅ **Workflow YAML tiene errores de sintaxis**:
```yaml
# Error: indentación incorrecta
jobs:
test:  # ❌ Falta indentación
  runs-on: ubuntu-latest
```

**Solución**: Valida YAML con linter online (yamllint.com)

#### 2. Tests Fallan en CI pero Pasan Localmente

**Síntoma**: `pytest` pasa local pero falla en GitHub Actions

**Causas posibles**:

✅ **Dependencias de versión**:
```bash
# Local: Python 3.11
# CI: Python 3.12

# Diferencias en comportamiento de librerías
```

**Solución**: Usa mismo Python version en CI y local

✅ **Variables de entorno faltantes**:
```python
# Test usa SECRET_KEY del .env
secret = os.getenv("SECRET_KEY")  # None en CI

# ❌ Falla porque no encuentra SECRET_KEY
```

**Solución**: Añade variables en workflow:
```yaml
env:
  SECRET_KEY: test-secret-key-for-ci
```

✅ **Timezone differences**:
```python
# Local: America/Mexico_City
# CI: UTC

# Tests de fecha/hora fallan
assert datetime.now().hour == 14  # ❌ En CI puede ser 20
```

**Solución**: Usa UTC en tests o configura TZ:
```yaml
env:
  TZ: America/Mexico_City
```

✅ **Race conditions**:
```python
# Test pasa solo a veces
async def test_concurrent_users():
    # ❌ Depende de timing
    await asyncio.sleep(0.1)
    assert user.is_ready
```

**Solución**: Usa awaits explícitos, no sleeps

#### 3. E2E Tests Fallan

**Síntoma**: Playwright tests fallan en CI

**Causas posibles**:

✅ **Backend no está listo**:
```yaml
# ❌ Empieza tests antes de que backend esté listo
- run: npm run dev &
- run: npx playwright test  # Falla porque backend no responde
```

**Solución**: Espera health check:
```yaml
- run: npm run dev &
- run: |
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 1; done'
- run: npx playwright test
```

✅ **Headless mode issues**:
```typescript
// Algunos tests solo pasan con UI visible
test('drag and drop', async ({ page }) => {
  // ❌ Puede fallar en headless
  await page.dragAndDrop('#source', '#target');
});
```

**Solución**: Debug con headed mode:
```yaml
- run: npx playwright test --headed  # Solo para debugging
```

✅ **Timeouts en CI**:
```typescript
// CI es más lento que local
await expect(page.locator('.loading')).toBeVisible();  // ❌ Timeout
```

**Solución**: Aumenta timeouts en CI:
```typescript
// playwright.config.ts
export default defineConfig({
  timeout: process.env.CI ? 60000 : 30000,  // 60s en CI, 30s local
});
```

#### 4. Deploy Falla

**Síntoma**: Deploy workflow falla en staging

**Causas posibles**:

✅ **SSH key inválida**:
```
Error: Permission denied (publickey)
```

**Solución**: Verifica SSH key en secrets:
```bash
# Genera nueva key
ssh-keygen -t ed25519 -C "github-actions@contravento.com"

# Copia a servidor
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@staging.contravento.com

# Añade private key a GitHub Secrets
cat ~/.ssh/id_ed25519  # Copiar contenido completo
```

✅ **Docker images no accesibles**:
```
Error: pull access denied for contravento/backend
```

**Solución**: Verifica Docker Hub credentials:
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}  # Verifica este secret
```

✅ **Servicios no inician**:
```
Error: Service 'backend' failed to start
```

**Solución**: Revisa logs en servidor:
```bash
# SSH al servidor
ssh deploy@staging.contravento.com

# Ver logs
cd /var/www/contravento
docker compose logs backend --tail=100
```

### Debugging de Workflows

#### 1. Habilitar Debug Logging

**En repositorio Settings**:
1. Settings → Secrets and variables → Actions
2. New repository variable:
   - Name: `ACTIONS_RUNNER_DEBUG`
   - Value: `true`
3. New repository variable:
   - Name: `ACTIONS_STEP_DEBUG`
   - Value: `true`

**Resultado**: Logs mucho más verbosos

#### 2. SSH Debugging (tmate)

Para debuggear interactivamente en CI:

```yaml
- name: Setup tmate session
  if: failure()  # Solo si falla
  uses: mxschmitt/action-tmate@v3
  timeout-minutes: 15
```

**Uso**:
1. Workflow falla
2. GitHub Actions muestra: `SSH: ssh abc123@nyc1.tmate.io`
3. Conéctate desde terminal:
   ```bash
   ssh abc123@nyc1.tmate.io
   ```
4. Explora el ambiente, ejecuta comandos, debuggea
5. Presiona Ctrl+C para continuar workflow

#### 3. Act (Ejecutar Workflows Localmente)

Herramienta para correr GitHub Actions en local:

```bash
# Instalar act
brew install act  # macOS
choco install act  # Windows

# Ejecutar workflow
act -j test  # Ejecuta job 'test'

# Ejecutar con secrets
act -j deploy --secret-file .secrets

# Ejecutar workflow específico
act -W .github/workflows/backend-tests.yml
```

**Limitaciones**:
- No soporta todos los features de GitHub Actions
- Puede tener diferencias de comportamiento
- Útil para debugging rápido

---

## Best Practices

### 1. Workflow Design

#### ✅ Keep Workflows Fast

**Problema**: Workflows lentos retrasan desarrollo

**Solución**:
```yaml
# ❌ Malo: Instalar dependencias cada vez (5 minutos)
- name: Install dependencies
  run: pip install poetry && poetry install

# ✅ Bueno: Usar cache (30 segundos)
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'  # Cache automático de dependencias
    cache-dependency-path: 'backend/poetry.lock'

- name: Install dependencies
  run: pip install poetry && poetry install
```

**Otras optimizaciones**:
- ✅ Paralelizar jobs independientes
- ✅ Usar Docker layer caching
- ✅ Limitar profundidad de checkout (`fetch-depth: 1`)
- ✅ Dividir workflows grandes en pequeños

#### ✅ Fail Fast

**Problema**: Esperar 10 minutos para descubrir error de sintaxis

**Solución**:
```yaml
jobs:
  # Primero: Checks rápidos (linting, formatting)
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: black --check .
      - run: ruff check .

  # Después: Tests (más lentos)
  test:
    needs: lint  # Solo si lint pasa
    runs-on: ubuntu-latest
    steps:
      - run: pytest
```

**Orden recomendado**:
1. Linting/formatting (10-30s)
2. Type checking (30-60s)
3. Unit tests (1-3 min)
4. Integration tests (3-5 min)
5. E2E tests (5-10 min)

#### ✅ Use Matrix Strategy for Parallel Testing

**Problema**: Tests E2E toman 30 minutos (3 browsers × 10 min cada uno)

**Solución**:
```yaml
jobs:
  e2e:
    strategy:
      matrix:
        browser: [chromium, firefox, webkit]
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - run: npx playwright test --project=${{ matrix.browser }}

# Resultado: 6 jobs en paralelo → 10 minutos total
```

### 2. Security

#### ✅ Never Hardcode Secrets

**❌ Malo**:
```yaml
- name: Deploy
  run: |
    docker login -u myuser -p mypassword123  # ❌ Password visible
```

**✅ Bueno**:
```yaml
- name: Deploy
  env:
    DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
  run: |
    echo "$DOCKER_PASSWORD" | docker login -u myuser --password-stdin
```

#### ✅ Limit Permissions

**❌ Malo (permisos por defecto)**:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    # Tiene acceso write a todo el repositorio
```

**✅ Bueno (principio de mínimo privilegio)**:
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read        # Solo lectura de código
      packages: write       # Write para subir Docker images
      pull-requests: write  # Write para comentar en PR
```

#### ✅ Pin Action Versions

**❌ Malo**:
```yaml
- uses: actions/checkout@v4  # ❌ Puede cambiar sin avisar
```

**✅ Bueno**:
```yaml
- uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab  # v4.1.1
```

**Nota**: Usa Dependabot para mantener actions actualizadas:
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 3. Monitoring & Observability

#### ✅ Add Meaningful Logs

**❌ Malo**:
```yaml
- name: Run tests
  run: pytest  # No se ve qué pasa
```

**✅ Bueno**:
```yaml
- name: Run tests
  run: |
    echo "::group::Running unit tests"
    pytest tests/unit -v
    echo "::endgroup::"

    echo "::group::Running integration tests"
    pytest tests/integration -v
    echo "::endgroup::"
```

**Resultado**: Logs organizados en grupos colapsables

#### ✅ Add Job Summaries

```yaml
- name: Generate test summary
  if: always()
  run: |
    echo "## Test Results 📊" >> $GITHUB_STEP_SUMMARY
    echo "" >> $GITHUB_STEP_SUMMARY
    echo "| Suite | Passed | Failed | Duration |" >> $GITHUB_STEP_SUMMARY
    echo "|-------|--------|--------|----------|" >> $GITHUB_STEP_SUMMARY
    echo "| Unit | 234 | 0 | 2m 45s |" >> $GITHUB_STEP_SUMMARY
    echo "| Integration | 89 | 1 | 4m 12s |" >> $GITHUB_STEP_SUMMARY
```

**Resultado**: Resumen markdown visible en workflow summary

#### ✅ Upload Artifacts on Failure

```yaml
- name: Run E2E tests
  run: npx playwright test

- name: Upload failure artifacts
  if: failure()  # Solo si falla
  uses: actions/upload-artifact@v4
  with:
    name: e2e-failure-report
    path: |
      playwright-report/
      test-results/
      screenshots/
```

### 4. Cost Optimization

#### ✅ Use Self-Hosted Runners (si aplica)

**GitHub-hosted runners**:
- ✅ Fácil setup
- ✅ Siempre actualizados
- ❌ Caro para repos privados
- ❌ Límites de minutos

**Self-hosted runners**:
- ✅ Gratis (solo hardware)
- ✅ Sin límites de minutos
- ❌ Mantenimiento manual
- ❌ Consideraciones de seguridad

**Cuándo usar self-hosted**:
- Repo privado con >100 workflows/mes
- Tests que necesitan hardware específico
- Datos sensibles que no pueden salir de la empresa

#### ✅ Cancel Redundant Workflows

```yaml
name: Backend Tests

on:
  pull_request:
    branches: [main, develop]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancela workflows anteriores si hay push nuevo
```

**Beneficio**: Ahorra minutos si haces múltiples pushes rápidos

---

## Recursos Adicionales

### Documentación Oficial

- **GitHub Actions**: https://docs.github.com/en/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- **GitHub CLI**: https://cli.github.com/manual/

### Herramientas

- **Act** (Local workflow execution): https://github.com/nektos/act
- **actionlint** (Workflow linter): https://github.com/rhysd/actionlint
- **GitHub Actions VSCode Extension**: marketplace.visualstudio.com

### ContraVento Docs

- **QA Testing Manual**: [docs/QA_TESTING_MANUAL.md](./QA_TESTING_MANUAL.md)
- **Deployment Guide**: [backend/docs/DEPLOYMENT.md](../backend/docs/DEPLOYMENT.md)
- **Performance Testing**: [backend/tests/performance/PERFORMANCE_TESTING.md](../backend/tests/performance/PERFORMANCE_TESTING.md)

---

## Resumen

### ¿Qué es CI/CD?

**CI/CD** = Integración Continua + Despliegue Continuo

**En términos simples**:
- 🤖 Robot que **revisa tu código automáticamente** cada vez que haces commit
- ✅ **Ejecuta todos los tests** para asegurar que nada se rompa
- 🚀 **Despliega automáticamente** a staging/production si todo pasa

### Workflows de ContraVento

| Workflow | Propósito | Triggers | Duración |
|----------|-----------|----------|----------|
| **backend-tests.yml** | Tests backend (pytest) | Push, PR | ~3-5 min |
| **frontend-tests.yml** | Tests frontend (Vitest) | Push, PR | ~4-6 min |
| **e2e-tests.yml** | Tests E2E (Playwright) | Push, PR | ~8-12 min |
| **deploy-staging.yml** | Deploy a staging | Merge to develop | ~5-8 min |

### Beneficios

✅ **Detección temprana de bugs**: Minutos, no días
✅ **Confianza en el código**: Tests automáticos siempre
✅ **Deploys seguros**: Validación antes de producción
✅ **Velocidad**: Deploy diario vs mensual
✅ **Menos estrés**: Automatización reduce errores humanos

### Flujo de Trabajo Típico

```
Developer → Commit → Push → GitHub Actions
                              ↓
                        ✅ Lint, Type Check
                        ✅ Unit Tests
                        ✅ Integration Tests
                        ✅ E2E Tests
                              ↓
                        All Passed? ✅
                              ↓
                        Merge to Develop
                              ↓
                        🚀 Auto Deploy to Staging
                              ↓
                        Smoke Tests Pass? ✅
                              ↓
                        🎉 Ready for Production
```

---

**Última actualización**: 2026-01-16

**Contacto**: Para preguntas sobre CI/CD, contacta al equipo de DevOps
