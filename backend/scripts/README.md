# Backend Scripts

Colección de scripts útiles para desarrollo, testing y deployment de ContraVento backend.

## 📂 Estructura Organizativa

Los scripts están organizados por función en carpetas temáticas:

```
scripts/
├── analysis/        # Análisis GPS, RouteStatistics y Performance Testing (10 scripts Python)
├── wrappers/        # Bash wrappers para scripts de análisis (7 scripts)
├── testing/         # Tests de integración y manuales (4 scripts)
├── seeding/         # Carga de datos iniciales (5 scripts)
├── user-mgmt/       # Gestión de usuarios (4 scripts)
├── dev-tools/       # Herramientas de desarrollo (4 scripts)
├── config/          # Archivos de configuración (2 archivos YAML/TXT)
└── deployment/      # Scripts de despliegue y CI (2 scripts)
```

### 📋 Índice Rápido por Categoría

| Categoría | Scripts | Uso Principal |
|-----------|---------|---------------|
| **analysis/** | 10 scripts | Análisis de GPX, detección de stops, RouteStatistics, comparación de algoritmos, performance testing |
| **wrappers/** | 7 scripts | Ejecutores bash para scripts de análisis |
| **testing/** | 4 scripts | Tests de integración API, User Stories |
| **seeding/** | 5 scripts | Carga de datos iniciales (achievements, trips, users) |
| **user-mgmt/** | 4 scripts | Crear admin, usuarios, promover roles |
| **dev-tools/** | 4 scripts | Inspeccionar datos, encontrar GPX, limpiar trips |
| **config/** | 2 archivos | Configuración de tipos de ciclismo y palabras bloqueadas |
| **deployment/** | 2 scripts | Docker entrypoint, verificación MVP |

---

## 🧪 Testing & Integration

### testing/test_route_statistics.py

Test manual para User Story 5 (Advanced Statistics). Crea trip con GPX, calcula RouteStatistics y valida resultados.

**Uso:**

```bash
poetry run python scripts/testing/test_route_statistics.py
```

**Lo que hace:**
1. ✅ Crea usuario de test
2. ✅ Crea trip de prueba
3. ✅ Sube archivo GPX con timestamps
4. ✅ Calcula RouteStatistics automáticamente
5. ✅ Muestra resultados de speed, time, gradient, climbs

---

### testing/test_gpx_statistics.sh / .ps1

Integration tests para validar API endpoints de GPX y RouteStatistics.

**Uso:**

```bash
# Linux/Mac
bash scripts/testing/test_gpx_statistics.sh

# Windows PowerShell
.\scripts\testing\test_gpx_statistics.ps1
```

**Requisitos:**
- Backend corriendo en `http://localhost:8000`
- Usuario `testuser` existente

---

### testing/test_tags.sh

Script interactivo para probar la funcionalidad de tags y filtrado de trips.

**Uso:**

```bash
bash scripts/testing/test_tags.sh
```

**Funcionalidades:**
- Crear trips con tags
- Filtrar trips por tag
- Filtrar por status (DRAFT/PUBLISHED)
- Paginación
- Búsqueda de tags populares

Ver [backend/docs/api/TAGS_TESTING.md](../docs/api/TAGS_TESTING.md) para guía completa.

---

## 🌱 Seeding & Inicialización

### seeding/init_dev_data.py

Script maestro que ejecuta todos los scripts de seeding en orden correcto.

**Uso:**

```bash
poetry run python scripts/seeding/init_dev_data.py
```

**Ejecuta en orden:**
1. `seed_achievements.py` - Carga 9 achievements predefinidos
2. `seed_cycling_types.py` - Carga tipos de ciclismo desde YAML
3. `create_admin.py` - Crea usuario administrador
4. `create_verified_user.py` - Crea usuarios de prueba

**Usuarios creados:**
- `admin` / `admin@contravento.com` / `AdminPass123!` (ADMIN)
- `testuser` / `test@example.com` / `TestPass123!` (USER)
- `maria_garcia` / `maria@example.com` / `SecurePass456!` (USER)

---

### seeding/seed_achievements.py

Carga los 9 achievements predefinidos en la base de datos.

**Uso:**

```bash
poetry run python scripts/seeding/seed_achievements.py
```

**Achievements:**
- FIRST_TRIP, CENTURY, VOYAGER, EXPLORER, PHOTOGRAPHER, GLOBETROTTER, MARATHONER, INFLUENCER, PROLIFIC

---

### seeding/seed_cycling_types.py

Carga tipos de ciclismo desde `config/cycling_types.yaml`.

**Uso:**

```bash
# Cargar tipos (skip si existen)
poetry run python scripts/seeding/seed_cycling_types.py

# Forzar actualización de existentes
poetry run python scripts/seeding/seed_cycling_types.py --force

# Listar tipos actuales
poetry run python scripts/seeding/seed_cycling_types.py --list
```

---

### seeding/seed_trips.py

Crea viajes de ejemplo para testing con tags, ubicaciones y diferentes estados.

**Uso:**

```bash
# Crear todos los trips de ejemplo para testuser
poetry run python scripts/seeding/seed_trips.py

# Crear para usuario específico
poetry run python scripts/seeding/seed_trips.py --user maria_garcia

# Crear solo N trips
poetry run python scripts/seeding/seed_trips.py --count 3

# Listar trips existentes
poetry run python scripts/seeding/seed_trips.py --list
```

---

### seeding/add_test_trip_with_coordinates.py

Crea trip con 3 ubicaciones GPS para probar mapa en modo fullscreen.

**Uso:**

```bash
poetry run python scripts/seeding/add_test_trip_with_coordinates.py
```

**Ubicaciones creadas:**
- Madrid (40.4168, -3.7038)
- Valencia (39.4699, -0.3763)
- Barcelona (41.3851, 2.1734)

---

## 👥 Gestión de Usuarios

### user-mgmt/create_admin.py

Crea usuario administrador con credenciales personalizadas.

**Uso:**

```bash
# Crear admin por defecto
poetry run python scripts/user-mgmt/create_admin.py

# Crear admin personalizado
poetry run python scripts/user-mgmt/create_admin.py \
  --username myadmin \
  --email admin@mycompany.com \
  --password "MySecurePass123!"

# Forzar creación (skip confirmación)
poetry run python scripts/user-mgmt/create_admin.py --force
```

**Admin por defecto:**
- Username: `admin`
- Email: `admin@contravento.com`
- Password: `AdminPass123!`

---

### user-mgmt/create_verified_user.py

Crea usuarios verificados para testing (evita verificación manual de email).

**Uso:**

```bash
# Crear usuarios por defecto (testuser y maria_garcia)
poetry run python scripts/user-mgmt/create_verified_user.py

# Crear usuario personalizado
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username john \
  --email john@example.com \
  --password "SecurePass123!"

# Crear usuario con rol admin
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username myadmin \
  --email admin@example.com \
  --password "AdminPass123!" \
  --role admin

# Verificar usuario existente por email
poetry run python scripts/user-mgmt/create_verified_user.py --verify-email test@example.com
```

---

### user-mgmt/promote_to_admin.py

Promociona usuario existente a rol admin (o degrada a usuario regular).

**Uso:**

```bash
# Promover a admin por username
poetry run python scripts/user-mgmt/promote_to_admin.py --username testuser

# Promover a admin por email
poetry run python scripts/user-mgmt/promote_to_admin.py --email test@example.com

# Degradar admin a usuario regular
poetry run python scripts/user-mgmt/promote_to_admin.py --username admin --demote
```

---

### user-mgmt/manage_follows.py

Gestiona relaciones de seguimiento entre usuarios.

**Uso:**

```bash
# Hacer que testuser siga a maria_garcia
poetry run python scripts/user-mgmt/manage_follows.py \
  --follower testuser \
  --following maria_garcia

# Dejar de seguir
poetry run python scripts/user-mgmt/manage_follows.py \
  --follower testuser \
  --following maria_garcia \
  --unfollow

# Listar usuarios que testuser sigue
poetry run python scripts/user-mgmt/manage_follows.py --follower testuser --list

# Listar seguidores de testuser
poetry run python scripts/user-mgmt/manage_follows.py --following testuser --list
```

---

## 🛠️ Herramientas de Desarrollo

### dev-tools/check_latest_gpx.py

Encuentra automáticamente el GPX más reciente en la base de datos.

**Uso:**

```bash
poetry run python scripts/dev-tools/check_latest_gpx.py
```

**Útil para:**
- Testing rápido sin buscar UUIDs manualmente
- Verificar últimas subidas de GPX

---

### dev-tools/check_test_data.py

Verifica usuarios y trips en la base de datos de desarrollo.

**Uso:**

```bash
poetry run python scripts/dev-tools/check_test_data.py
```

**Muestra:**
- Listado de usuarios con emails
- Conteo de trips por usuario

---

### dev-tools/check_stats.py

Inspecciona UserStats para un usuario específico (por defecto: testuser).

**Uso:**

```bash
poetry run python scripts/dev-tools/check_stats.py
```

**Muestra:**
- Total trips
- Total kilometers
- Countries visited
- Tipo de datos (para debugging)

---

### dev-tools/clean_trips.py

Elimina todos los trips de un usuario (útil para resetear datos de test).

**Uso:**

```bash
poetry run python scripts/dev-tools/clean_trips.py
```

⚠️ **ADVERTENCIA**: Operación destructiva sin opción de deshacer.

---

## 🚀 Deployment & CI

### deployment/docker-entrypoint.sh

Script de entrypoint para containers Docker. Ejecutado automáticamente al iniciar el container.

**Función:**
1. ✅ Aplica migraciones de Alembic (`alembic upgrade head`)
2. ✅ Inicializa datos de desarrollo (solo en dev/testing/ci environments)
3. ✅ Inicia el servidor FastAPI

**No se ejecuta manualmente**. Es referenciado por `ENTRYPOINT` en Dockerfile.

---

### deployment/mvp-check.sh

Checklist de verificación para MVP (Minimum Viable Product).

**Uso:**

```bash
bash scripts/deployment/mvp-check.sh
```

**Verifica:**
1. ✅ Code Quality (Black, Ruff)
2. ✅ Tests & Coverage (≥90%)
3. ✅ PostgreSQL funcionando
4. ✅ Migraciones aplicadas
5. ✅ No errores en inglés (solo español)

---

## 📊 Análisis GPS y RouteStatistics

Scripts para analizar archivos GPX y estadísticas de rutas. Organizados en dos carpetas:

- **`analysis/`**: Scripts Python con la lógica de análisis
- **`wrappers/`**: Scripts Bash para ejecutar los scripts Python de forma sencilla

### Scripts de Análisis GPS

| # | Script Python | Bash Wrapper | Dual Mode | Funcionalidad |
|---|--------------|--------------|-----------|---------------|
| 1 | `analyze_gpx_segments.py` | `analyze-segments.sh` | ✅ Sí | Analiza segmentos (slow, long, STOP) para detectar patrones de paradas |
| 2 | `analyze_slow_segments.py` | `analyze-slow-segments.sh` | ✅ Sí | Genera histograma de duración de segmentos lentos (<1 km/h) |
| 3 | `analyze_gpx_timing.py` | `analyze-timing.sh` | ✅ Sí | Analiza espaciado entre puntos GPS (distance gaps) |
| 4 | `gpx_stats.py` | - | ✅ File | Calcula estadísticas usando gpxpy (referencia) |
| 5 | `app_gpx_stats.py` | - | ✅ File | Calcula estadísticas usando lógica de la app |
| 6 | - | `compare-gpx-stats.sh` | ✅ File | Compara gpxpy vs lógica de la app lado a lado |
| 7 | `check_route_stats.py` | `check-stats.sh` | ❌ DB-only | Verifica existencia de RouteStatistics en la base de datos |
| 8 | `recalculate_route_stats.py` | `recalculate-stats.sh` | ❌ DB-only | Recalcula RouteStatistics para un GPX existente |
| 9 | `delete_corrupt_stats.py` | `delete-stats.sh` | ❌ DB-only | Elimina RouteStatistics corruptas o no deseadas |

**Leyenda de Modos:**
- **✅ Dual Mode**: Soporta modo database (GPX en DB) y modo file path (GPX local)
- **❌ DB-only**: Solo opera con base de datos (requiere GPX en DB)

### Ejemplos de Uso Completo

#### 1. Análisis de Segmentos GPS

Analiza segmentos para detectar paradas (velocidad < 3 km/h Y duración > 2 min):

```bash
# Modo Database (desde GPX en DB)
./scripts/wrappers/analyze-segments.sh 13e24f2f-f792-4873-b636-ad3568861514

# Modo File Path (desde archivo local)
./scripts/wrappers/analyze-segments.sh --file-path /tmp/my-route.gpx
```

#### 2. Histograma de Segmentos Lentos

Genera histograma de duración de segmentos lentos (<3 km/h):

```bash
# Modo Database
./scripts/wrappers/analyze-slow-segments.sh 13e24f2f-f792-4873-b636-ad3568861514

# Modo File Path
./scripts/wrappers/analyze-slow-segments.sh --file-path /tmp/route.gpx
```

#### 3. Análisis de Espaciado GPS

Analiza espaciado entre puntos GPS (detecta gaps >0.5km):

```bash
# Modo Database
./scripts/wrappers/analyze-timing.sh 13e24f2f-f792-4873-b636-ad3568861514

# Modo File Path
./scripts/wrappers/analyze-timing.sh --file-path /home/user/route.gpx
```

#### 4. Verificar RouteStatistics

Verifica si un GPX tiene estadísticas calculadas:

```bash
./scripts/wrappers/check-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
```

**Salida si existe:**
```
[OK] RouteStatistics FOUND!
[SPEED]  Avg Speed: 18.5 km/h, Max Speed: 42.3 km/h
[TIME]   Total: 120.5 min, Moving: 95.2 min
[GRADIENT] Avg: 2.3%, Max: 12.5%
[CLIMBS] 3 climbs found
```

#### 5. Recalcular RouteStatistics

Recalcula estadísticas (útil después de cambios en algoritmo):

```bash
./scripts/wrappers/recalculate-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
```

⚠️ **ADVERTENCIA**: Elimina RouteStatistics existente y crea uno nuevo.

#### 6. Eliminar RouteStatistics

Elimina estadísticas corruptas o no deseadas:

```bash
./scripts/wrappers/delete-stats.sh 13e24f2f-f792-4873-b636-ad3568861514
```

⚠️ **ADVERTENCIA**: Operación destructiva sin opción de deshacer.

### Workflows Típicos

#### Workflow 1: Diagnosticar Moving Time ≈ Total Time

```bash
# 1. Analizar segmentos
./scripts/wrappers/analyze-segments.sh <gpx_file_id>

# 2. Ver histograma de paradas
./scripts/wrappers/analyze-slow-segments.sh <gpx_file_id>

# 3. Verificar gaps GPS
./scripts/wrappers/analyze-timing.sh <gpx_file_id>
```

#### Workflow 2: Corregir RouteStatistics Corruptas

```bash
# 1. Verificar estadísticas actuales
./scripts/wrappers/check-stats.sh <gpx_file_id>

# 2. Eliminar estadísticas corruptas
./scripts/wrappers/delete-stats.sh <gpx_file_id>

# 3. Recalcular estadísticas correctas
./scripts/wrappers/recalculate-stats.sh <gpx_file_id>

# 4. Verificar resultados
./scripts/wrappers/check-stats.sh <gpx_file_id>
```

#### Workflow 3: Analizar GPX Externo (Sin Subir a DB)

```bash
# Analizar segmentos
./scripts/wrappers/analyze-segments.sh --file-path /tmp/route.gpx

# Analizar segmentos lentos
./scripts/wrappers/analyze-slow-segments.sh --file-path /tmp/route.gpx

# Analizar espaciado GPS
./scripts/wrappers/analyze-timing.sh --file-path /tmp/route.gpx
```

#### Workflow 4: Backfill de RouteStatistics (Múltiples GPX)

```bash
# Recalcular para múltiples GPX
for id in id1 id2 id3; do
  echo "Processing $id..."
  ./scripts/wrappers/recalculate-stats.sh "$id"
done
```

### Comparación de Estadísticas GPX

**Nuevos scripts (2026-01-31):** Herramientas para validar algoritmos de cálculo de estadísticas.

#### 1. Estadísticas con gpxpy (Referencia)

Usa directamente la librería gpxpy para calcular estadísticas (implementación de referencia):

```bash
poetry run python scripts/analysis/gpx_stats.py scripts/datos/QH_2013.gpx
```

#### 2. Estadísticas con Lógica de la App

Usa los mismos servicios que la aplicación (`GPXService` + `RouteStatsService`):

```bash
poetry run python scripts/analysis/app_gpx_stats.py scripts/datos/QH_2013.gpx
```

#### 3. Comparación Lado a Lado (RECOMENDADO)

Ejecuta ambos scripts en paralelo para comparación visual:

```bash
./scripts/wrappers/compare-gpx-stats.sh scripts/datos/QH_2013.gpx
```

**Útil para:**
- ✅ Validar que algoritmos de la app coinciden con gpxpy
- ✅ Verificar corrección de bugs en cálculos de estadísticas
- ✅ Testing de regresión tras cambios en `RouteStatsService`
- ✅ Documentar diferencias entre implementaciones

**Métricas clave a comparar:**
- Tiempo en movimiento: debe ser similar (±5%)
- Velocidad media: debe ser similar (±5%)
- Distancia total: debe coincidir exactamente

**Cambios recientes en algoritmos (2026-01-31):**
- ✅ Umbral de paradas: 3 km/h → **1 km/h** (matches gpxpy)
- ✅ Eliminado requisito de duración mínima (antes: solo paradas > 2 min)
- ✅ Filtro de velocidades anómalas: max_speed < 100 km/h
- ✅ Filtro de segmentos muy cortos: > 2 segundos

---

### Referencia Rápida

```bash
# Análisis de segmentos (dual mode)
./scripts/wrappers/analyze-segments.sh <gpx_file_id>
./scripts/wrappers/analyze-segments.sh --file-path <ruta>

./scripts/wrappers/analyze-slow-segments.sh <gpx_file_id>
./scripts/wrappers/analyze-slow-segments.sh --file-path <ruta>

./scripts/wrappers/analyze-timing.sh <gpx_file_id>
./scripts/wrappers/analyze-timing.sh --file-path <ruta>

# Comparación de estadísticas (file mode)
poetry run python scripts/analysis/gpx_stats.py <ruta>
poetry run python scripts/analysis/app_gpx_stats.py <ruta>
./scripts/wrappers/compare-gpx-stats.sh <ruta>

# RouteStatistics (DB-only)
./scripts/wrappers/check-stats.sh <gpx_file_id>
./scripts/wrappers/recalculate-stats.sh <gpx_file_id>
./scripts/wrappers/delete-stats.sh <gpx_file_id>
```

**Documentación completa**: Ver [GPS_ANALYSIS_SCRIPTS.md](GPS_ANALYSIS_SCRIPTS.md)

---

## 🚀 Performance Testing (Feature 017)

Scripts para validar el performance del GPS Trip Creation Wizard y diagnosticar cuellos de botella.

### analysis/test_gpx_analyze.py

Prueba el endpoint `/gpx/analyze` con medición de tiempo para validar SC-002.

**Uso:**

```bash
cd backend

# Test con archivo pequeño (default)
poetry run python scripts/analysis/test_gpx_analyze.py

# Test con archivo 10MB (SC-002 validation)
poetry run python scripts/analysis/test_gpx_analyze.py tests/fixtures/gpx/long_route_10mb.gpx
```

**Valida:**
- ✅ **SC-002**: GPX processing <2s for 10MB files
- Evita problemas de autenticación con curl (workaround para shell escaping)

**Salida:**
```
✓ Token obtained: eyJhbGci...
✓ Reading GPX file: tests/fixtures/gpx/long_route_10mb.gpx
  File size: 10,886,608 bytes (10.38 MB)
⏱  Processing time: 4.929 seconds
✗ SC-002 FAIL: 10MB+ file processed in 4.929s (>2s target)
```

---

### analysis/diagnose_gpx_performance.py

Diagnóstico detallado paso a paso para identificar cuellos de botella.

**Uso:**

```bash
cd backend
poetry run python scripts/analysis/diagnose_gpx_performance.py
```

**Analiza:**
- XML parsing time (gpxpy)
- RDP simplification time (Douglas-Peucker)
- Service layer overhead
- Bottleneck distribution

**Salida:**
```
BOTTLENECK ANALYSIS
────────────────────────────────────────
XML parsing:        2.229s (44.9%)
RDP algorithm:      2.269s (45.7%)
Other operations:   0.462s (9.3%)
```

### Limitaciones Conocidas

⚠️ **Ver [analysis/README.md](analysis/README.md) para documentación completa de limitaciones**

**Resumen:**

1. **Autenticación con curl**: Falla con caracteres especiales en password
   - Workaround: Usar `test_gpx_analyze.py`

2. **Performance SC-002 FAIL**: 4.96s vs objetivo 2s
   - Bottleneck: gpxpy parsing (45%) + RDP algorithm (46%)
   - Requiere optimización (cambiar parser, optimizar RDP)

3. **Simplificación extrema**: Archivo de prueba genera ruta recta
   - 85,000 → 2 trackpoints (no representativo de rutas reales)

---

## Convenciones

### Nombrado de Scripts

- **`.sh`**: Scripts Bash (Linux/Mac)
- **`.ps1`**: Scripts PowerShell (Windows)
- **`.py`**: Scripts Python (cross-platform)

### Variables de Entorno

Todos los scripts respetan estas variables si están configuradas:

```bash
DATABASE_URL           # URL de conexión a base de datos
APP_ENV               # Entorno (development/testing/staging/production)
SECRET_KEY            # Clave secreta para JWT
```

### Ubicación de Datos

```
backend/
├── scripts/              # Scripts de automatización (organizados por función)
├── storage/             # Archivos subidos (fotos)
├── storage_test/        # Archivos de testing (temporal)
└── contravento_dev.db  # SQLite de desarrollo (si se usa)
```

---

## Troubleshooting

### Script no ejecuta (Linux/Mac)

```bash
# Dar permisos de ejecución
chmod +x backend/scripts/wrappers/analyze-segments.sh
```

### Script no ejecuta (Windows PowerShell)

```powershell
# Habilitar ejecución de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PostgreSQL no inicia

```bash
# Verificar Docker
docker ps

# Ver logs
docker-compose logs postgres

# Resetear completamente
docker-compose down -v
docker-compose up postgres -d
```

### Migraciones fallan

```bash
# Ver estado de migraciones
poetry run alembic current

# Rollback y re-aplicar
poetry run alembic downgrade base
poetry run alembic upgrade head
```

### ImportError después de reorganización

Si ves errores como `ModuleNotFoundError: No module named 'scripts.seed_achievements'`, verifica que:

1. Estés usando las rutas actualizadas:
   - ✅ `scripts.seeding.seed_achievements`
   - ❌ `scripts.seed_achievements`

2. El script use `sys.path.insert` correcto según su ubicación:
   - En `scripts/seeding/`: `Path(__file__).parent.parent.parent` (3 niveles)
   - En `scripts/`: `Path(__file__).parent.parent` (2 niveles)

---

## Agregar Nuevos Scripts

### Template para script Bash

```bash
#!/bin/bash
set -e  # Exit on error

echo "Script description"

# Your code here
```

### Template para script PowerShell

```powershell
$ErrorActionPreference = "Stop"

Write-Host "Script description" -ForegroundColor Cyan

# Your code here
```

### Template para script Python

```python
#!/usr/bin/env python3
"""
Script description.

Usage:
    python scripts/<category>/my_script.py [options]
"""

import sys
from pathlib import Path

# Add backend to path (adjust parent levels based on script location)
# If in scripts/: parent.parent
# If in scripts/<category>/: parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
```

---

## Referencias

- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) - Guía completa de deployment
- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Guía de testing
- [TAGS_TESTING.md](../docs/api/TAGS_TESTING.md) - Testing de tags
- [GPS_ANALYSIS_SCRIPTS.md](GPS_ANALYSIS_SCRIPTS.md) - Documentación completa de scripts GPS
