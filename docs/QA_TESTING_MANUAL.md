# Manual de Testing QA - ContraVento

**Versión**: 1.0
**Fecha**: Enero 2026
**Feature**: 001-testing-qa

---

## Índice

1. [Introducción](#introducción)
2. [Requisitos Previos](#requisitos-previos)
3. [Smoke Tests](#smoke-tests)
4. [Tests de Integración (Backend)](#tests-de-integración-backend)
5. [Tests Unitarios (Frontend)](#tests-unitarios-frontend)
6. [Tests E2E (End-to-End)](#tests-e2e-end-to-end)
7. [Tests de Performance](#tests-de-performance)
8. [Pre-commit Checks](#pre-commit-checks)
9. [Generación de Reportes](#generación-de-reportes)
10. [Troubleshooting](#troubleshooting)

---

## Introducción

Este manual está diseñado para que el equipo de QA pueda ejecutar todos los tipos de tests implementados en ContraVento de forma sistemática y efectiva.

### Tipos de Tests Disponibles

| Tipo de Test | Propósito | Duración Aprox. | Frecuencia Recomendada |
|--------------|-----------|-----------------|------------------------|
| **Smoke Tests** | Verificar funcionalidad crítica | 1-2 min | Cada despliegue |
| **Tests de Integración** | Validar APIs y DB | 5-10 min | Cada PR |
| **Tests E2E** | Simular flujos de usuario | 10-20 min | Antes de release |
| **Tests de Performance** | Medir latencia y carga | 15-30 min | Semanal |
| **Pre-commit Checks** | Verificar calidad de código | 3-5 min | Antes de cada commit |

---

## Requisitos Previos

### Software Necesario

#### Para Tests de Backend
```bash
# Python 3.12
python --version
# Debe mostrar: Python 3.12.x

# Poetry (gestor de dependencias)
poetry --version
# Debe mostrar: Poetry (version 1.7.0 o superior)
```

#### Para Tests de Frontend
```bash
# Node.js 20
node --version
# Debe mostrar: v20.x.x

# npm
npm --version
# Debe mostrar: 10.x.x o superior
```

#### Para Tests E2E
```bash
# Playwright (se instala automáticamente con npm)
npx playwright --version
```

### Instalación de Dependencias

#### Backend
```bash
cd backend
poetry install
```

#### Frontend
```bash
cd frontend
npm ci
```

### Verificar Instalación

```bash
# Backend
cd backend
poetry run pytest --version

# Frontend
cd frontend
npx playwright --version
```

---

## Smoke Tests

### ¿Qué son los Smoke Tests?

Los smoke tests verifican que las funcionalidades críticas del sistema funcionan correctamente. Son rápidos y se ejecutan después de cada despliegue.

### Tests Incluidos

1. **Health Check** - Verifica que la API responde
2. **Auth Endpoint** - Valida rechazo de credenciales inválidas
3. **Protected Endpoint** - Verifica autenticación requerida
4. **Database Connectivity** - Confirma conexión a la base de datos

### Ejecución

#### Windows (PowerShell)

```powershell
# Modo local-dev (SQLite)
.\scripts\run_smoke_tests.ps1 -Mode local-dev

# Modo local-minimal (PostgreSQL con Docker)
.\scripts\run_smoke_tests.ps1 -Mode local-minimal

# Modo local-full (Full Docker stack)
.\scripts\run_smoke_tests.ps1 -Mode local-full

# Modo staging
.\scripts\run_smoke_tests.ps1 -Mode staging
```

#### Linux/Mac (Bash)

```bash
# Modo local-dev (SQLite)
bash scripts/run_smoke_tests.sh local-dev

# Modo local-minimal (PostgreSQL con Docker)
bash scripts/run_smoke_tests.sh local-minimal

# Modo local-full (Full Docker stack)
bash scripts/run_smoke_tests.sh local-full

# Modo staging
bash scripts/run_smoke_tests.sh staging
```

### Interpretación de Resultados

#### ✅ **TODOS LOS TESTS PASAN**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Tests: 4
  Passed: 4
  Failed: 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ All smoke tests passed!
```

**Acción**: Sistema listo para usar ✅

---

#### ❌ **ALGÚN TEST FALLA**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Tests: 4
  Passed: 3
  Failed: 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ 1 test(s) failed

Troubleshooting:
  1. Verify the application is running for mode: local-dev
  2. Check application logs for errors
  3. Verify database is accessible
  4. Check network connectivity to http://localhost:8000
```

**Acción**: Ver sección [Troubleshooting](#troubleshooting) ⚠️

---

## Tests de Integración (Backend)

### ¿Qué son los Tests de Integración?

Validan que los endpoints de la API funcionan correctamente y que la integración con la base de datos es correcta.

### Suites de Tests Disponibles

| Suite | Archivo | Tests | Descripción |
|-------|---------|-------|-------------|
| **Auth API** | `test_auth_api.py` | 10 | Registro, login, tokens, verificación |
| **Public Feed** | `test_public_feed.py` | 12 | Feed público, filtrado, paginación |
| **Trips API** | `test_trips_api.py` | 67 | CRUD de viajes, fotos, tags, ubicaciones |

### Pre-requisitos

#### Opción 1: SQLite (Recomendado para tests locales)

```bash
# No requiere configuración adicional
# Los tests usan base de datos en memoria
```

#### Opción 2: PostgreSQL con Docker

```bash
# Iniciar contenedor de PostgreSQL
docker-compose -f docker-compose.test.yml up -d postgres

# Verificar que está corriendo
docker ps | grep postgres
```

### Ejecución

#### Ejecutar TODOS los tests de integración

```bash
cd backend

# Con reporte de coverage
poetry run pytest tests/integration/ -v --cov=src --cov-report=html

# Solo resultados (sin coverage)
poetry run pytest tests/integration/ -v
```

#### Ejecutar suite específica

```bash
cd backend

# Solo tests de autenticación
poetry run pytest tests/integration/test_auth_api.py -v

# Solo tests de public feed
poetry run pytest tests/integration/test_public_feed.py -v

# Solo tests de trips
poetry run pytest tests/integration/test_trips_api.py -v
```

#### Ejecutar test individual

```bash
cd backend

# Ejecutar un test específico
poetry run pytest tests/integration/test_auth_api.py::TestAuthLogin::test_login_valid_credentials -v
```

### Interpretación de Resultados

#### ✅ **TODOS LOS TESTS PASAN**

```
======================== test session starts =========================
platform win32 -- Python 3.12.0, pytest-7.4.4, pluggy-1.3.0
collected 35 items

tests/integration/test_auth_api.py::TestAuthRegistrationFlow::test_register_user_flow PASSED [ 2%]
tests/integration/test_auth_api.py::TestAuthLogin::test_login_valid_credentials PASSED [ 5%]
...
tests/integration/test_public_feed.py::TestAnonymousPublicFeedAccess::test_anonymous_access_to_public_trips PASSED [100%]

========================= 35 passed in 12.34s =========================

---------- coverage: platform win32, python 3.12.0 -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
src/api/auth.py                 123      5    96%
src/api/trips.py                 245     15    94%
src/services/auth_service.py     178      8    95%
src/services/trip_service.py     312     18    94%
-------------------------------------------------
TOTAL                           1234     78    94%
```

**Acción**: Todos los tests pasaron ✅

---

#### ❌ **ALGÚN TEST FALLA**

```
======================== test session starts =========================
collected 35 items

tests/integration/test_auth_api.py::TestAuthLogin::test_login_valid_credentials FAILED [ 5%]

============================== FAILURES ==============================
____ TestAuthLogin::test_login_valid_credentials ____

    async def test_login_valid_credentials(self, client, test_user):
        response = await client.post("/auth/login", json={...})
>       assert response.status_code == 200
E       AssertionError: assert 401 == 200

tests/integration/test_auth_api.py:145: AssertionError
========================= 1 failed, 34 passed in 15.67s ==============
```

**Acción**:
1. Revisar el traceback completo
2. Verificar datos de prueba
3. Consultar logs del backend
4. Ver sección [Troubleshooting](#troubleshooting)

---

### Generar Reporte HTML de Coverage

```bash
cd backend
poetry run pytest tests/integration/ --cov=src --cov-report=html

# Abrir reporte en navegador
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

El reporte muestra:
- ✅ Líneas cubiertas (verde)
- ❌ Líneas no cubiertas (rojo)
- ⚠️ Branches parcialmente cubiertos (amarillo)

---

## Tests Unitarios (Frontend)

### ¿Qué son los Tests Unitarios?

Validan componentes individuales del frontend (React, TypeScript) de forma aislada.

### Framework

- **Vitest** - Test runner rápido para Vite
- **React Testing Library** - Para tests de componentes React

### Ejecución

#### Ejecutar todos los tests

```bash
cd frontend

# Modo watch (se re-ejecutan al guardar cambios)
npm run test:unit

# Modo CI (ejecutar una vez)
npm run test:unit -- --run

# Con coverage
npm run test:unit -- --coverage
```

#### Ejecutar tests específicos

```bash
cd frontend

# Por archivo
npm run test:unit -- LocationConfirmModal.test.tsx

# Por patrón
npm run test:unit -- --grep "geocoding"
```

### Interpretación de Resultados

```
 ✓ src/components/trips/LocationConfirmModal.test.tsx (23)
   ✓ LocationConfirmModal (23)
     ✓ should render modal when location is provided
     ✓ should not render when location is null
     ✓ should display coordinates with 6 decimal precision
     ✓ should allow editing location name
     ...

 Test Files  1 passed (1)
      Tests  23 passed (23)
   Start at  16:30:45
   Duration  1.23s
```

---

## Tests E2E (End-to-End)

### ¿Qué son los Tests E2E?

Simulan interacciones reales de usuarios en navegadores (Chrome, Firefox, Safari). Validan flujos completos desde el frontend hasta el backend.

### Suites de Tests

| Suite | Archivo | Tests | Navegadores |
|-------|---------|-------|-------------|
| **Autenticación** | `auth.spec.ts` | 12 | ✅ Chrome, Firefox, Safari |
| **Creación de Viajes** | `trip-creation.spec.ts` | 15 | ✅ Chrome, Firefox, Safari |
| **Feed Público** | `public-feed.spec.ts` | 18 | ✅ Chrome, Firefox, Safari |
| **Edición de Ubicaciones** | `location-editing.spec.ts` | 12 | ✅ Chrome, Firefox, Safari |

**Total**: 57 tests × 3 navegadores = **171 ejecuciones de test**

### Pre-requisitos

#### 1. Backend en ejecución

```bash
# Terminal 1: Iniciar backend
cd backend
poetry run uvicorn src.main:app --reload

# Verificar
curl http://localhost:8000/health
```

#### 2. Frontend en ejecución

```bash
# Terminal 2: Iniciar frontend
cd frontend
npm run dev

# Verificar
curl http://localhost:5173
```

#### 3. Instalar navegadores de Playwright

```bash
cd frontend

# Primera vez solamente
npx playwright install
```

### Ejecución

#### Ejecutar TODOS los tests E2E

```bash
cd frontend

# Todos los navegadores
npx playwright test

# Solo Chrome
npx playwright test --project=chromium

# Solo Firefox
npx playwright test --project=firefox

# Solo Safari
npx playwright test --project=webkit
```

#### Ejecutar suite específica

```bash
cd frontend

# Solo tests de autenticación
npx playwright test auth.spec.ts

# Solo tests de creación de viajes
npx playwright test trip-creation.spec.ts

# Solo tests de feed público
npx playwright test public-feed.spec.ts

# Solo tests de ubicaciones
npx playwright test location-editing.spec.ts
```

#### Ejecutar test específico

```bash
cd frontend

# Por nombre del test
npx playwright test -g "should login with valid credentials"

# Por archivo y navegador
npx playwright test auth.spec.ts --project=chromium
```

#### Modo Interactivo (UI Mode)

```bash
cd frontend

# Abrir interfaz visual de Playwright
npx playwright test --ui
```

**Ventajas**:
- ✅ Ver tests ejecutándose en vivo
- ✅ Depurar paso a paso
- ✅ Inspeccionar elementos
- ✅ Ver screenshots automáticos

#### Modo Debug

```bash
cd frontend

# Ejecutar en modo debug (con inspector)
npx playwright test auth.spec.ts --debug
```

#### Modo Headed (Ver navegador)

```bash
cd frontend

# Ver navegador durante ejecución
npx playwright test --headed

# Más lento (útil para depuración)
npx playwright test --headed --slow-mo=1000
```

### Interpretación de Resultados

#### ✅ **TODOS LOS TESTS PASAN**

```
Running 57 tests using 3 workers

  ✓  [chromium] › auth.spec.ts:25:7 › User Registration Flow › should complete full registration workflow (5.2s)
  ✓  [chromium] › auth.spec.ts:45:7 › User Registration Flow › should show validation errors for invalid input (2.1s)
  ✓  [chromium] › trip-creation.spec.ts:30:7 › Trip Creation Wizard - Step 1 › should display step 1 form correctly (1.8s)
  ...

  57 passed (3m 45s)

To open last HTML report run:
  npx playwright show-report
```

**Acción**: Todos los tests E2E pasaron ✅

---

#### ❌ **ALGÚN TEST FALLA**

```
Running 57 tests using 3 workers

  ✓  [chromium] › auth.spec.ts:25:7 › User Registration Flow › should complete full registration workflow (5.2s)
  ✗  [chromium] › auth.spec.ts:67:7 › Login Flow › should login with valid credentials (15.3s)

  1) [chromium] › auth.spec.ts:67:7 › Login Flow › should login with valid credentials ────

    Error: Timeout 15000ms exceeded.
    waiting for locator('text=/home|dashboard|trips/') to be visible

    Call log:
      - waiting for locator('text=/home|dashboard|trips/')
      - locator resolved to <not found>

  1 failed
    [chromium] › auth.spec.ts:67:7 › Login Flow › should login with valid credentials
  56 passed (4m 12s)
```

**Acción**:
1. Ver screenshots de la falla: `test-results/`
2. Ver video: `test-results/.../video.webm`
3. Ver trace: `npx playwright show-trace test-results/.../trace.zip`
4. Consultar [Troubleshooting](#troubleshooting)

---

### Ver Reporte HTML

```bash
cd frontend

# Generar y abrir reporte
npx playwright show-report
```

El reporte incluye:
- ✅ Screenshots del último paso antes de fallar
- 🎥 Videos de ejecución (solo tests fallidos)
- 🔍 Traces interactivos (timeline de acciones)
- 📋 Logs de consola del navegador

---

## Tests de Performance

### ¿Qué son los Tests de Performance?

Miden la velocidad de respuesta del sistema y su capacidad de manejar carga concurrente.

### Tipos de Tests

| Tipo | Herramienta | Propósito | Duración |
|------|-------------|-----------|----------|
| **Benchmarks** | pytest-benchmark | Latencia de endpoints | 5 min |
| **Load Tests** | Locust | Carga concurrente | 2-5 min |
| **Stress Tests** | Locust | Punto de quiebre | 5-10 min |

### Pre-requisitos

```bash
# Backend debe estar corriendo
cd backend
poetry run uvicorn src.main:app

# Verificar
curl http://localhost:8000/health
```

### Ejecución con Script Helper

#### Windows (PowerShell)

```powershell
# Solo benchmarks
.\scripts\run_performance_tests.sh benchmark

# Load test ligero (50 usuarios, 2 min)
.\scripts\run_performance_tests.sh load

# Load test pesado (200 usuarios, 5 min)
.\scripts\run_performance_tests.sh load-heavy

# Todos los tests
.\scripts\run_performance_tests.sh all
```

#### Linux/Mac (Bash)

```bash
# Solo benchmarks
bash scripts/run_performance_tests.sh benchmark

# Load test ligero (50 usuarios, 2 min)
bash scripts/run_performance_tests.sh load

# Load test pesado (200 usuarios, 5 min)
bash scripts/run_performance_tests.sh load-heavy

# Todos los tests
bash scripts/run_performance_tests.sh all
```

### Ejecución Manual

#### 1. Benchmarks (pytest-benchmark)

```bash
cd backend

# Ejecutar todos los benchmarks
poetry run pytest tests/performance/test_api_benchmarks.py --benchmark-only

# Solo ver estadísticas (sin tests)
poetry run pytest tests/performance/test_api_benchmarks.py \
    --benchmark-only \
    --benchmark-verbose

# Guardar baseline para comparación
poetry run pytest tests/performance/test_api_benchmarks.py \
    --benchmark-only \
    --benchmark-save=baseline

# Comparar con baseline
poetry run pytest tests/performance/test_api_benchmarks.py \
    --benchmark-only \
    --benchmark-compare=baseline
```

**Interpretación de Resultados**:

```
--------------------------------- benchmark: 8 tests ---------------------------------
Name (time in ms)                          Min     Max    Mean  StdDev  Median  Ops/s
---------------------------------------------------------------------------------------
test_health_endpoint_latency            50.23   75.12   55.34    5.21   54.12  18.07
test_login_endpoint_latency            245.67  498.23  312.45   48.12  301.23   3.20
test_public_feed_latency_empty          89.34  145.67  105.23   12.34   98.45   9.50
test_create_trip_latency               456.78  987.23  678.34   89.12  654.23   1.47
---------------------------------------------------------------------------------------
```

**Criterios de Éxito**:
- ✅ `Mean` (promedio) está dentro del target
- ✅ `StdDev` (desviación estándar) es baja (consistencia)
- ✅ `Max` no excede 2× el target

**Targets**:
- Health: <200ms
- Login: <500ms
- Public Feed: <200ms
- Create Trip: <1000ms

---

#### 2. Load Tests (Locust)

##### Modo Interactivo (Web UI)

```bash
cd backend

# Iniciar Locust con interfaz web
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000

# Abrir navegador en: http://localhost:8089
```

**Pasos en la UI**:
1. Ingresar **Number of users**: `100`
2. Ingresar **Spawn rate**: `10` (usuarios/segundo)
3. Click **Start swarming**
4. Observar gráficas en tiempo real
5. Click **Stop** cuando termine

---

##### Modo Headless (Sin UI)

```bash
cd backend

# Load test de 100 usuarios por 2 minutos
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 2m \
    --headless

# Con reporte HTML
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 2m \
    --headless \
    --html=load-test-report.html

# Con reportes CSV
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 2m \
    --headless \
    --csv=load-test
```

**Interpretación de Resultados**:

```
Type     Name                       # reqs  # fails  Avg  Min  Max  Median  p95  p99   RPS
--------------------------------------------------------------------------------------------
GET      /health                      5000      0    52   15   180    50    78   95   83.3
POST     /auth/login                  2500      2   315  120   890   305   487  550   41.7
GET      /users/[username]/trips     10000      5   145   45   540   140   198  225  166.7
--------------------------------------------------------------------------------------------
Aggregated                           17500      7   154   15   890   148   312  425  291.7

Response time percentiles (approximated):
 Type     Name                       50%  66%  75%  80%  90%  95%  98%  99% 100%
--------------------------------------------------------------------------------
 GET      /health                     50   55   60   65   72   78   85   90  180
 POST     /auth/login                305  350  380  410  455  487  520  550  890
 GET      /users/[username]/trips    140  155  168  180  190  198  210  225  540
```

**Criterios de Éxito**:
- ✅ `p95 < target` (95% de requests cumplen latencia)
- ✅ `Failure rate < 1%` (menos de 1% de errores)
- ✅ `RPS estable` (throughput consistente)

---

#### 3. Stress Test (Encontrar límite)

```bash
cd backend

# Incrementar usuarios hasta encontrar punto de quiebre
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 500 \
    --spawn-rate 50 \
    --run-time 5m \
    --headless \
    --html=stress-test-report.html
```

**Objetivo**: Encontrar el número máximo de usuarios concurrentes antes de que:
- ❌ Failure rate > 1%
- ❌ p95 > 2× target
- ❌ Timeouts frecuentes

---

### Ver Reportes

#### Reporte HTML de Locust

```bash
# Abrir reporte en navegador
# Windows
start load-test-report.html

# Linux/Mac
open load-test-report.html
```

Incluye:
- 📊 Gráficas de response time
- 📈 Gráficas de RPS (requests/second)
- 📋 Tabla de estadísticas por endpoint
- 🔥 Distribución de percentiles

---

## Pre-commit Checks

### ¿Qué son los Pre-commit Checks?

Verificaciones de calidad de código que deben ejecutarse **antes** de hacer commit para asegurar que el código cumple los estándares del proyecto.

### Checks Incluidos

| Check | Herramienta | Descripción |
|-------|-------------|-------------|
| **1. Backend Formatting** | Black | Formato de código Python |
| **2. Backend Linting** | Ruff | Linting de código Python |
| **3. Backend Type Check** | MyPy | Verificación de tipos |
| **4. Frontend Linting** | ESLint | Linting de TypeScript |
| **5. Frontend Type Check** | TypeScript | Verificación de tipos |
| **6. Backend Unit Tests** | pytest | Tests unitarios backend |
| **7. Backend Integration Tests** | pytest | Tests integración backend |
| **8. Coverage Check** | pytest-cov | Coverage ≥90% |
| **9. Frontend Unit Tests** | Vitest | Tests unitarios frontend |
| **10. Frontend Build** | Vite | Build de producción |
| **11. Git Changes Check** | git | Cambios sin commitear |
| **12. Git Branch Check** | git | Evitar commits en main/develop |

### Ejecución

#### Modo Completo

```bash
# Windows
.\scripts\run_pre_commit_checks.ps1

# Linux/Mac
bash scripts/run_pre_commit_checks.sh
```

#### Modo Rápido (sin tests)

```bash
# Windows
.\scripts\run_pre_commit_checks.ps1 -Quick

# Linux/Mac
bash scripts/run_pre_commit_checks.sh --quick
```

### Interpretación de Resultados

#### ✅ **TODOS LOS CHECKS PASAN**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pre-commit Checks Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Passed: 12
  Total Failed: 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 All checks passed! Ready to commit.
```

**Acción**: Puedes hacer commit con seguridad ✅

---

#### ❌ **ALGÚN CHECK FALLA**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pre-commit Checks Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Passed: 10
  Total Failed: 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💥 2 check(s) failed. Fix errors before committing.
```

**Acción**:
1. Revisar qué checks fallaron (aparecen en rojo)
2. Seguir las instrucciones de cada check
3. Corregir errores
4. Volver a ejecutar checks

**Ejemplos de Correcciones**:

```bash
# Si falla formatting (Black)
cd backend
poetry run black src/ tests/

# Si falla linting (Ruff)
cd backend
poetry run ruff check src/ tests/ --fix

# Si falla linting (ESLint)
cd frontend
npm run lint -- --fix

# Si falla coverage
cd backend
# Añadir más tests para incrementar coverage
```

---

## Generación de Reportes

### Reportes de Coverage (Backend)

```bash
cd backend

# Generar reporte HTML
poetry run pytest --cov=src --cov-report=html

# Abrir en navegador
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### Reportes de E2E (Playwright)

```bash
cd frontend

# Ejecutar tests y generar reporte
npx playwright test

# Abrir reporte
npx playwright show-report
```

### Reportes de Performance

```bash
cd backend

# Locust: Generar reporte HTML
poetry run locust -f tests/performance/locustfile.py \
    --host=http://localhost:8000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 2m \
    --headless \
    --html=performance-report.html

# Abrir reporte
# Windows
start performance-report.html

# Linux/Mac
open performance-report.html
```

---

## Troubleshooting

### Problema: Backend no responde

**Síntomas**:
```
Error: Backend server is not running at http://localhost:8000
```

**Solución**:
```bash
# Verificar si el backend está corriendo
curl http://localhost:8000/health

# Si no responde, iniciarlo
cd backend
poetry run uvicorn src.main:app --reload
```

---

### Problema: Frontend no responde

**Síntomas**:
```
Error: Frontend server is not running at http://localhost:5173
```

**Solución**:
```bash
# Verificar si el frontend está corriendo
curl http://localhost:5173

# Si no responde, iniciarlo
cd frontend
npm run dev
```

---

### Problema: Puerto ocupado

**Síntomas**:
```
Error: listen EADDRINUSE: address already in use :::8000
```

**Solución Windows**:
```powershell
# Encontrar proceso usando el puerto
netstat -ano | findstr :8000

# Matar proceso
taskkill /PID <PID> /F
```

**Solución Linux/Mac**:
```bash
# Encontrar y matar proceso
lsof -ti:8000 | xargs kill -9
```

---

### Problema: Base de datos no conecta

**Síntomas**:
```
❌ FAIL - Database connection failed
```

**Solución**:
```bash
# Verificar que PostgreSQL está corriendo (Docker)
docker ps | grep postgres

# Si no está corriendo, iniciarlo
docker-compose -f docker-compose.test.yml up -d postgres

# Verificar logs
docker logs contravento_postgres
```

---

### Problema: Tests E2E fallan por timeout

**Síntomas**:
```
Error: Timeout 30000ms exceeded
```

**Solución**:
```bash
# 1. Verificar que backend y frontend están corriendo
curl http://localhost:8000/health
curl http://localhost:5173

# 2. Incrementar timeout en playwright.config.ts
# timeout: 60 * 1000  // Aumentar a 60 segundos

# 3. Ejecutar en modo headed para ver qué pasa
cd frontend
npx playwright test --headed --debug
```

---

### Problema: Coverage bajo

**Síntomas**:
```
❌ Coverage 85% is below required 90%
```

**Solución**:
```bash
# Ver reporte detallado
cd backend
poetry run coverage report --show-missing

# Identificar líneas no cubiertas
poetry run coverage html
open htmlcov/index.html

# Añadir tests para líneas no cubiertas
# Enfocarse en archivos con coverage < 90%
```

---

### Problema: Playwright no encuentra navegadores

**Síntomas**:
```
Error: Executable doesn't exist at /path/to/chromium
```

**Solución**:
```bash
cd frontend

# Reinstalar navegadores
npx playwright install

# Con dependencias del sistema
npx playwright install --with-deps
```

---

### Problema: Tests de performance muestran latencia alta

**Síntomas**:
```
Mean response time: 1500ms (expected < 500ms)
```

**Solución**:
1. **Verificar carga del sistema**:
   ```bash
   # Ver CPU y memoria
   htop  # Linux/Mac
   # o Task Manager en Windows
   ```

2. **Cerrar aplicaciones pesadas**
3. **Usar PostgreSQL en lugar de SQLite para tests de carga**
4. **Verificar logs del backend**:
   ```bash
   tail -f backend/logs/uvicorn.log
   ```

---

## Checklist de Testing Completo

Usa este checklist antes de cada release:

### Pre-Release Testing Checklist

- [ ] **1. Smoke Tests**
  - [ ] Ejecutar en local-dev
  - [ ] Ejecutar en local-minimal
  - [ ] Ejecutar en staging
  - [ ] Todos los tests pasan (4/4)

- [ ] **2. Tests de Integración Backend**
  - [ ] Suite completa pasa (35+ tests)
  - [ ] Coverage ≥ 90%
  - [ ] Reporte HTML generado

- [ ] **3. Tests Unitarios Frontend**
  - [ ] Todos los tests pasan
  - [ ] Coverage reportado

- [ ] **4. Tests E2E**
  - [ ] Suite de auth pasa (3 navegadores)
  - [ ] Suite de trip-creation pasa (3 navegadores)
  - [ ] Suite de public-feed pasa (3 navegadores)
  - [ ] Suite de location-editing pasa (3 navegadores)
  - [ ] Reporte HTML generado

- [ ] **5. Tests de Performance**
  - [ ] Benchmarks ejecutados
  - [ ] Todos los endpoints cumplen targets
  - [ ] Load test con 100 usuarios exitoso
  - [ ] Failure rate < 1%
  - [ ] Reporte generado

- [ ] **6. Pre-commit Checks**
  - [ ] Todos los checks pasan
  - [ ] No hay cambios sin commitear

- [ ] **7. Documentación**
  - [ ] Reportes archivados
  - [ ] Incidencias documentadas
  - [ ] Changelog actualizado

---

## Contacto y Soporte

**Equipo de Desarrollo**:
- Issues: https://github.com/jfdelafuente/contravento-application-python/issues
- Documentación: `/docs`
- CI/CD: `.github/workflows/`

**Recursos Adicionales**:
- [README Principal](../README.md)
- [Guía de Performance Testing](../backend/tests/performance/PERFORMANCE_TESTING.md)
- [README de E2E Tests](../frontend/tests/e2e/README.md)
- [README de CI/CD](.github/workflows/README.md)

---

**Última actualización**: Enero 2026
**Versión del documento**: 1.0
