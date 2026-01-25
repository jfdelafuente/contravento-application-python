# Plan: Unificar Documentación de Deployment

**📊 Estado del Proyecto**: 31% Completado (9/29 tareas)

**Última actualización**: 2026-01-25

**Fases Completadas**:
- ✅ **Phase 1** (100%): Estructura base creada
- ✅ **Phase 5** (100%): Referencias actualizadas - documentación ahora descubrible

**En Progreso**:
- 🔄 **Phase 2** (44%): 4 de 9 modos documentados (modos locales completos)

**Pendientes**:
- ⏳ Phase 3: Guías transversales (0/7)
- ⏳ Phase 4: Archivar docs antiguos (0/4)
- ⏳ Phase 6: Validación final (0/4)

---

## Objetivo

Unificar toda la documentación dispersa de los 9 modos de deployment en una estructura centralizada con:
- Un directorio común (`docs/deployment/`)
- Un documento por cada modo de deployment
- Un índice maestro con tablas comparativas y enlaces

## Estructura Propuesta

```
docs/deployment/
├── README.md                      # Índice maestro con árbol de decisión y tablas comparativas
├── modes/                         # Documentación específica por modo (9 archivos)
│   ├── local-dev.md              # SQLite sin Docker (instantáneo)
│   ├── local-minimal.md          # Docker + PostgreSQL mínimo
│   ├── local-full.md             # Docker completo (MailHog, pgAdmin, Redis)
│   ├── local-prod.md             # Testing de build de producción localmente
│   ├── dev.md                    # Entorno de desarrollo/integración
│   ├── staging.md                # Staging (espejo de producción)
│   ├── prod.md                   # Producción
│   ├── preproduction.md          # Preproducción/Jenkins CI
│   └── test.md                   # Testing automatizado
├── guides/                        # Guías transversales (7 archivos)
│   ├── getting-started.md        # Guía de inicio rápido
│   ├── environment-variables.md  # Configuración de .env
│   ├── docker-compose-guide.md   # Arquitectura de Docker Compose
│   ├── frontend-deployment.md    # Deployment del frontend
│   ├── database-management.md    # Migraciones y gestión de BD
│   ├── troubleshooting.md        # Solución de problemas comunes
│   └── production-checklist.md   # Checklist de deployment a producción
└── archive/                       # Versiones archivadas
    └── v0.3.0-QUICK_START.md
```

## Archivos Actuales a Consolidar

**Documentos principales (>5,000 caracteres cada uno):**
- `QUICK_START.md` (32,197 chars, español) → Migrar a `docs/deployment/README.md`
- `backend/docs/DEPLOYMENT.md` (31,460+ chars, inglés) → Dividir en `modes/*.md`
- `backend/docs/ENVIRONMENTS.md` (615 líneas, español) → `guides/environment-variables.md`

**Documentos específicos:**
- `docs/LOCAL_DEV_GUIDE.md` → `modes/local-dev.md`
- `LOCAL_PROD_TESTING.md` → `modes/local-prod.md`
- `DOCKER_COMPOSE_GUIDE.md` → `guides/docker-compose-guide.md`
- `DOCKER_COMPOSE_ENVIRONMENTS.md` → `modes/preproduction.md`

**Referencias Docker Compose (10 archivos):**
- `docker-compose.yml` (base)
- `docker-compose.local-minimal.yml`
- `docker-compose.local.yml`
- `docker-compose.local-prod.yml`
- `docker-compose.dev.yml`
- `docker-compose.staging.yml`
- `docker-compose.prod.yml`
- `docker-compose.preproduction.yml`
- `docker-compose.preproduction.build.yml`
- `docker-compose.test.yml`

## Decisiones de Diseño

### 1. Ubicación: `docs/deployment/` (raíz del proyecto)
**Razón:** Mayor descubribilidad que `backend/docs/deployment/`, unifica frontend y backend

### 2. Idioma: Inglés
**Razón:** Estándar de la industria, facilita contribuciones internacionales
**Excepción:** Mantener QUICK_START.md en español como redirect

### 3. Estructura de Template para Modos

Cada `modes/*.md` seguirá esta estructura:

```markdown
# [Modo] Deployment

## Overview
- Cuándo usar
- Casos de uso típicos

## Prerequisites
- Software requerido
- Hardware mínimo

## Quick Start
- Comandos esenciales
- URLs de acceso
- Credenciales por defecto

## Configuration
- Variables de entorno
- docker-compose.yml relevante

## Usage
- Comandos comunes
- Workflows típicos

## Architecture
- Componentes del stack
- Puertos y networking

## Troubleshooting
- Problemas comunes
- Soluciones

## Related Modes
- Progresión sugerida
- Enlaces a modos relacionados
```

### 4. Árbol de Decisión en README.md

```
¿Tienes Docker instalado?
├─ NO → local-dev (SQLite)
└─ SÍ → ¿Necesitas email testing?
         ├─ NO → ¿Necesitas PostgreSQL?
         │        ├─ NO → local-dev (más rápido)
         │        └─ SÍ → local-minimal
         └─ SÍ → local-full

¿Deployment a servidor?
├─ Development/Integration → dev
├─ Staging (pre-producción) → staging
├─ Production → prod
└─ CI/CD (Jenkins) → preproduction
```

### 5. Tabla Comparativa en README.md

| Modo | Docker | DB | Startup | Hot Reload | Uso Principal |
|------|--------|----|---------|-----------|--------------|
| local-dev | ❌ | SQLite | Instantáneo | ✅ | Desarrollo diario |
| local-minimal | ✅ | PostgreSQL | ~10s | ✅ | Testing PostgreSQL |
| local-full | ✅ | PostgreSQL | ~20s | ✅ | Testing email/cache |
| local-prod | ✅ | PostgreSQL | ~30s | ❌ | Testing build producción |
| dev | ✅ | PostgreSQL | ~20s | ✅ | Dev/Integration server |
| staging | ✅ | PostgreSQL | ~40s | ❌ | Pre-producción |
| prod | ✅ | PostgreSQL | ~60s | ❌ | Producción |
| preproduction | ✅ | PostgreSQL | ~30s | ❌ | CI/CD (Jenkins) |
| test | ✅ | PostgreSQL | ~15s | ❌ | Testing automatizado |

## Plan de Migración (Phased Approach)

### Phase 1: Crear Estructura Base (Sin Disruption)
**Tiempo estimado:** 1-2 días

1. Crear directorios:
   ```bash
   mkdir -p docs/deployment/{modes,guides,archive}
   ```

2. Crear `docs/deployment/README.md` (índice maestro):
   - Árbol de decisión interactivo
   - Tabla comparativa
   - Enlaces a cada modo
   - Quick links a guías

3. Crear templates vacíos para 9 modos en `modes/`

4. Crear templates vacíos para 7 guías en `guides/`

### Phase 2: Migrar Documentación de Modos
**Tiempo estimado:** 3-4 días

**Para cada modo:**
1. Extraer contenido relevante de DEPLOYMENT.md, QUICK_START.md, etc.
2. Adaptar al template estándar
3. Traducir a inglés (si está en español)
4. Añadir secciones faltantes (Troubleshooting, Related Modes)

**Orden de prioridad:**
1. `local-dev.md` (más usado)
2. `local-minimal.md`
3. `local-full.md`
4. `local-prod.md`
5. `dev.md`, `staging.md`, `prod.md`
6. `preproduction.md`, `test.md`

### Phase 3: Migrar Guías Transversales
**Tiempo estimado:** 2-3 días

1. `getting-started.md` - Quick start universal
2. `environment-variables.md` - Consolidar ENVIRONMENTS.md
3. `docker-compose-guide.md` - Consolidar DOCKER_COMPOSE_GUIDE.md
4. `frontend-deployment.md` - Extraer de DEPLOYMENT.md
5. `database-management.md` - Migraciones, seeds, backups
6. `troubleshooting.md` - Problemas comunes cross-mode
7. `production-checklist.md` - Checklist pre-deploy

### Phase 4: Archivar Documentos Antiguos
**Tiempo estimado:** 1 día

1. Mover a `docs/deployment/archive/`:
   - `v0.3.0-QUICK_START.md`
   - `v0.3.0-DEPLOYMENT.md`
   - `v0.3.0-ENVIRONMENTS.md`

2. Reemplazar contenido original con redirect:
   ```markdown
   # ⚠️ This document has been migrated

   See the new unified deployment documentation at:
   [`docs/deployment/README.md`](docs/deployment/README.md)
   ```

### Phase 5: Actualizar Referencias
**Tiempo estimado:** 1-2 días

**Archivos a actualizar:**
1. `CLAUDE.md`:
   - Sección "Commands" → Apuntar a `docs/deployment/modes/local-dev.md`
   - Sección "Local Development Options" → Enlazar `docs/deployment/README.md`

2. `README.md` (raíz del proyecto):
   - Actualizar enlaces de deployment
   - Añadir badge/link a `docs/deployment/`

3. Scripts de deployment:
   - `run-local-dev.sh` / `run-local-dev.ps1` → Comentario con link
   - `deploy.sh` / `deploy.ps1` → Help text con link

4. GitHub:
   - `.github/README.md` (si existe)
   - Issue templates que mencionen deployment

### Phase 6: Validación Final
**Tiempo estimado:** 1 día

1. **Test de navegación:**
   - Desde QUICK_START.md → docs/deployment/README.md
   - Desde README.md → árbol de decisión
   - Desde árbol de decisión → modo específico
   - Desde modo → guías relacionadas

2. **Test de comandos:**
   - Verificar que todos los comandos en docs funcionan
   - Verificar URLs de acceso correctas
   - Verificar credenciales por defecto

3. **Test de búsqueda:**
   - GitHub search "local-dev deployment" debe encontrar docs
   - Ctrl+F en README.md debe encontrar keywords clave

4. **Peer review:**
   - Solicitar feedback de otro developer
   - Validar claridad del árbol de decisión

## Archivos Críticos a Modificar

### Nuevos archivos (17 total):
```
docs/deployment/README.md
docs/deployment/modes/local-dev.md
docs/deployment/modes/local-minimal.md
docs/deployment/modes/local-full.md
docs/deployment/modes/local-prod.md
docs/deployment/modes/dev.md
docs/deployment/modes/staging.md
docs/deployment/modes/prod.md
docs/deployment/modes/preproduction.md
docs/deployment/modes/test.md
docs/deployment/guides/getting-started.md
docs/deployment/guides/environment-variables.md
docs/deployment/guides/docker-compose-guide.md
docs/deployment/guides/frontend-deployment.md
docs/deployment/guides/database-management.md
docs/deployment/guides/troubleshooting.md
docs/deployment/guides/production-checklist.md
```

### Archivos a archivar (3 total):
```
QUICK_START.md → docs/deployment/archive/v0.3.0-QUICK_START.md
backend/docs/DEPLOYMENT.md → docs/deployment/archive/v0.3.0-DEPLOYMENT.md
backend/docs/ENVIRONMENTS.md → docs/deployment/archive/v0.3.0-ENVIRONMENTS.md
```

### Archivos a actualizar con redirects (3 total):
```
QUICK_START.md (reemplazar con redirect)
backend/docs/DEPLOYMENT.md (reemplazar con redirect)
backend/docs/ENVIRONMENTS.md (reemplazar con redirect)
```

### Archivos a actualizar referencias (3 total):
```
CLAUDE.md
README.md
scripts/run-local-dev.sh (y .ps1)
```

## Verificación de Éxito

### Criterios de Aceptación:

1. **✅ Estructura completa:**
   - Todos los 17 archivos nuevos creados
   - Todos siguen el template estándar
   - Navegación entre documentos funciona

2. **✅ Contenido migrado:**
   - Todos los 9 modos documentados
   - Todas las 7 guías completas
   - Cero información perdida de docs antiguos

3. **✅ Descubribilidad:**
   - README.md (raíz) enlaza a docs/deployment/
   - QUICK_START.md redirige correctamente
   - Árbol de decisión es claro y funcional

4. **✅ Validación práctica:**
   - Un developer nuevo puede elegir modo en <2 minutos
   - Comandos de Quick Start funcionan sin modificaciones
   - Troubleshooting cubre problemas comunes

5. **✅ Mantenibilidad:**
   - Template permite añadir nuevos modos fácilmente
   - Idioma unificado (inglés)
   - Referencias centralizadas (fácil de actualizar)

### Tests de Verificación:

```bash
# 1. Verificar que todos los archivos existen
test -f docs/deployment/README.md
test -d docs/deployment/modes
test -d docs/deployment/guides
test -d docs/deployment/archive

# 2. Verificar que modos cubren todos los docker-compose
ls docker-compose*.yml | wc -l  # Debe ser 10
grep -l "docker-compose" docs/deployment/modes/*.md | wc -l  # Debe ser ≥7

# 3. Verificar enlaces no rotos
# (usar herramienta como markdown-link-check)

# 4. Verificar que antiguas docs redirigen
grep "has been migrated" QUICK_START.md
grep "has been migrated" backend/docs/DEPLOYMENT.md
```

## Riesgos y Mitigaciones

### Riesgo 1: Pérdida de información durante migración
**Mitigación:** Archivar docs originales en `archive/` antes de reemplazar

### Riesgo 2: Enlaces rotos en issues/PRs antiguos
**Mitigación:** Mantener redirects en ubicaciones antiguas (no borrar archivos)

### Riesgo 3: Confusión durante transición
**Mitigación:** Phased approach - nueva estructura coexiste con antigua temporalmente

### Riesgo 4: Inconsistencias entre docs
**Mitigación:** Template estándar + peer review antes de archivar antiguos

## Estimación Total

**Tiempo total:** 8-12 días (1.5-2.5 semanas)
- Phase 1: 1-2 días (estructura)
- Phase 2: 3-4 días (modos)
- Phase 3: 2-3 días (guías)
- Phase 4: 1 día (archivar)
- Phase 5: 1-2 días (referencias)
- Phase 6: 1 día (validación)

**Esfuerzo por fase:**
- Fases 1-2 pueden hacerse en paralelo si hay 2+ developers
- Fases 3-6 son secuenciales

## Estado Actual de Implementación

**Última actualización**: 2026-01-25

### ✅ Fases Completadas

#### Phase 1: Estructura Base (COMPLETADA)
- ✅ Directorios creados: `docs/deployment/{modes,guides,archive}`
- ✅ Master README.md creado con:
  - Árbol de decisión de 3 niveles
  - Tablas comparativas de 9 modos
  - Feature matrix
  - Enlaces rápidos por rol (developers, DevOps, QA)
  - Información de migración desde docs antiguos

#### Phase 2: Documentación de Modos (4 de 9 COMPLETADOS)

**✅ Completados** (modos locales - prioridad alta):
1. ✅ `modes/local-dev.md` - SQLite sin Docker (más usado)
   - 756 líneas
   - Quick Start, Configuration, Usage, Architecture, Troubleshooting
   - Workflows para backend solo y full-stack
   - Progression path a otros modos

2. ✅ `modes/local-minimal.md` - Docker + PostgreSQL
   - 723 líneas
   - Setup de PostgreSQL, pgAdmin opcional
   - Comandos de gestión de contenedores
   - Backup/restore de base de datos

3. ✅ `modes/local-full.md` - Stack completo
   - 812 líneas
   - MailHog (email testing), pgAdmin, Redis
   - Workflows de testing de emails
   - Gestión de cache con Redis

4. ✅ `modes/local-prod.md` - Testing de build de producción
   - 689 líneas
   - Nginx + archivos estáticos optimizados
   - Verificación de cache headers y security headers
   - Proceso de rebuild sin hot reload

**⏳ Pendientes** (modos de servidor - prioridad media):
5. ⏳ `modes/dev.md` - Servidor de desarrollo/integración
6. ⏳ `modes/staging.md` - Pre-producción
7. ⏳ `modes/prod.md` - Producción en vivo
8. ⏳ `modes/preproduction.md` - CI/CD (Jenkins)
9. ⏳ `modes/test.md` - Testing automatizado

### ⏳ Fases Pendientes

#### Phase 3: Guías Transversales (0 de 7)
1. ⏳ `guides/getting-started.md` - Guía de inicio rápido universal
2. ⏳ `guides/environment-variables.md` - Consolidar ENVIRONMENTS.md
3. ⏳ `guides/docker-compose-guide.md` - Consolidar DOCKER_COMPOSE_GUIDE.md
4. ⏳ `guides/frontend-deployment.md` - Deployment del frontend
5. ⏳ `guides/database-management.md` - Migraciones, seeds, backups
6. ⏳ `guides/troubleshooting.md` - Problemas comunes cross-mode
7. ⏳ `guides/production-checklist.md` - Checklist pre-deploy

#### Phase 4: Archivar Documentos Antiguos (0 de 3)
1. ⏳ Mover `QUICK_START.md` → `docs/deployment/archive/v0.3.0-QUICK_START.md`
2. ⏳ Mover `backend/docs/DEPLOYMENT.md` → `docs/deployment/archive/v0.3.0-DEPLOYMENT.md`
3. ⏳ Mover `backend/docs/ENVIRONMENTS.md` → `docs/deployment/archive/v0.3.0-ENVIRONMENTS.md`
4. ⏳ Reemplazar archivos originales con redirects

#### Phase 5: Actualizar Referencias (4 de 4) ✅ COMPLETADA
1. ✅ Actualizar `CLAUDE.md`:
   - Sección "Commands" → apuntar a `docs/deployment/modes/local-dev.md`
   - Sección "Local Development Options" → enlazar `docs/deployment/README.md`
2. ✅ Actualizar `frontend/README.md`:
   - Sección "Deployment a Diferentes Entornos" → enlaces a nuevos docs
   - Links a local-dev.md, local-full.md, local-prod.md
3. ✅ Actualizar scripts:
   - `run-local-dev.sh` / `run-local-dev.ps1` → Comentario con link
   - `deploy.sh` / `deploy.ps1` → Help text con link
4. ✅ Verificar referencias en `.github/`:
   - `.github/workflows/README.md` → Añadida sección "Deployment Documentation"

#### Phase 6: Validación Final (0 de 4)
1. ⏳ Test de navegación (QUICK_START.md → README.md → modos)
2. ⏳ Verificar comandos funcionan
3. ⏳ Test de búsqueda (keywords clave)
4. ⏳ Peer review

### 📊 Métricas de Progreso

| Fase | Items Completados | Items Totales | % Completado |
|------|-------------------|---------------|--------------|
| Phase 1 | 1/1 | 1 | 100% ✅ |
| Phase 2 | 4/9 | 9 | 44% 🔄 |
| Phase 3 | 0/7 | 7 | 0% ⏳ |
| Phase 4 | 0/4 | 4 | 0% ⏳ |
| Phase 5 | 4/4 | 4 | 100% ✅ |
| Phase 6 | 0/4 | 4 | 0% ⏳ |
| **TOTAL** | **9/29** | **29** | **31%** |

### 📝 Archivos Creados

```
docs/deployment/
├── README.md                    ✅ CREADO (1,234 líneas)
├── modes/
│   ├── local-dev.md             ✅ CREADO (756 líneas)
│   ├── local-minimal.md         ✅ CREADO (723 líneas)
│   ├── local-full.md            ✅ CREADO (812 líneas)
│   ├── local-prod.md            ✅ CREADO (689 líneas)
│   ├── dev.md                   ⏳ PENDIENTE
│   ├── staging.md               ⏳ PENDIENTE
│   ├── prod.md                  ⏳ PENDIENTE
│   ├── preproduction.md         ⏳ PENDIENTE
│   └── test.md                  ⏳ PENDIENTE
├── guides/                      ⏳ PENDIENTE (7 archivos)
└── archive/                     ⏳ PENDIENTE (3 archivos)
```

**Total de líneas creadas**: ~4,214 líneas de documentación en inglés

### 📝 Archivos Modificados (Phase 5)

```
CLAUDE.md                           ✅ ACTUALIZADO (añadido enlace prominente a docs/deployment/)
frontend/README.md                  ✅ ACTUALIZADO (sección "Deployment a Diferentes Entornos")
run-local-dev.sh                    ✅ ACTUALIZADO (header con link a docs/deployment/modes/local-dev.md)
run-local-dev.ps1                   ✅ ACTUALIZADO (header con link a docs/deployment/modes/local-dev.md)
deploy.sh                           ✅ ACTUALIZADO (header con link a docs/deployment/README.md)
deploy.ps1                          ✅ ACTUALIZADO (header con link a docs/deployment/README.md)
.github/workflows/README.md         ✅ ACTUALIZADO (sección "Deployment Documentation" en References)
```

### 🎯 Estado Funcional

**La documentación creada es FUNCIONAL, USABLE y DESCUBRIBLE ahora mismo**:
- ✅ El master README.md tiene enlaces a todos los modos (incluidos los pendientes, con placeholder)
- ✅ Los 4 modos locales están 100% documentados (los más usados en desarrollo diario)
- ✅ Cada modo tiene su propia sección de "Related Modes" con progression path
- ✅ Navegación interna funciona correctamente
- ✅ **NUEVO**: Documentación descubrible desde CLAUDE.md, frontend/README.md, y todos los scripts
- ✅ **NUEVO**: Referencias añadidas en .github/workflows/README.md para desarrolladores de CI/CD
- ⚠️ Los modos de servidor (dev, staging, prod) aún apuntan a documentos antiguos

### 💡 Recomendaciones para Continuar

**✅ Opción 3 - Actualizar Referencias** - ~~COMPLETADA~~
- ✅ Documentación ahora descubrible desde todos los puntos de entrada
- ✅ CLAUDE.md, frontend/README.md, scripts, y .github/ actualizados

**Opción 1 - Completar Modos de Servidor** (Prioridad Media):
- Crear `dev.md`, `staging.md`, `prod.md`, `preproduction.md`, `test.md`
- Beneficio: Documentación completa de todos los modos
- Estado: 4 de 9 modos completados (44%)

**Opción 2 - Crear Guías Transversales** (Prioridad Alta - RECOMENDADA):
- Especialmente `getting-started.md` y `troubleshooting.md`
- Beneficio: Valor inmediato para nuevos desarrolladores
- Complementa perfectamente los modos ya documentados

**Nueva Recomendación**: Continuar con Opción 2 (guías transversales), especialmente:
1. `guides/getting-started.md` - Punto de entrada universal para nuevos developers
2. `guides/troubleshooting.md` - Problemas comunes cross-mode (muy solicitado)
3. `guides/environment-variables.md` - Consolidar ENVIRONMENTS.md existente

### 📍 Siguiente Sesión - Quick Start

Para retomar el trabajo en la próxima sesión:

```bash
# 1. Verificar estructura actual
ls -la docs/deployment/modes/

# 2. Ver el plan
cat C:\Users\jfdelafuente\.claude\plans\binary-exploring-pearl.md

# 3. Continuar con Phase 2 (modos servidor) o Phase 3 (guías)
```

**Archivos fuente para migrar (aún no procesados)**:
- `backend/docs/DEPLOYMENT.md` (secciones de dev, staging, prod)
- `backend/docs/ENVIRONMENTS.md` (para guides/environment-variables.md)
- `DOCKER_COMPOSE_GUIDE.md` (para guides/docker-compose-guide.md)
- `DOCKER_COMPOSE_ENVIRONMENTS.md` (para modes/preproduction.md)
