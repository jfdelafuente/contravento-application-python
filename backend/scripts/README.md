# Backend Scripts

Colección de scripts útiles para desarrollo, testing y deployment de ContraVento backend.

## Testing & Development

### setup-postgres-testing.sh / setup-postgres-testing.ps1

Configura un entorno de testing minimalista con PostgreSQL para validar migraciones y compatibilidad antes de staging.

**Uso:**

```bash
# Linux/Mac
bash backend/scripts/setup-postgres-testing.sh

# Windows PowerShell
.\backend\scripts\setup-postgres-testing.ps1
```

**Lo que hace:**
1. ✅ Verifica que Docker esté corriendo
2. ✅ Inicia PostgreSQL container
3. ✅ Espera a que PostgreSQL esté ready
4. ✅ Crea base de datos `contravento_test`
5. ✅ Crea usuario `contravento_test`
6. ✅ Aplica todas las migraciones de Alembic
7. ✅ Verifica que las tablas se crearon correctamente

**Salida esperada:**

```
==========================================
✓ PostgreSQL Testing Environment Ready!
==========================================

Connection details:
  Host:     localhost
  Port:     5432
  Database: contravento_test
  User:     contravento_test
  Password: test_password

DATABASE_URL:
  postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test
```

**Siguiente paso:**

```bash
# Iniciar backend
cd backend
poetry run uvicorn src.main:app --reload --port 8000
```

---

### create_verified_user.py

Crea usuarios verificados para testing (evita tener que verificar email manualmente).

**Uso:**

```bash
# Crear usuarios por defecto (testuser y maria_garcia)
poetry run python scripts/create_verified_user.py

# Crear usuario personalizado
poetry run python scripts/create_verified_user.py \
  --username john \
  --email john@example.com \
  --password "SecurePass123!"

# Verificar usuario existente por email
poetry run python scripts/create_verified_user.py --verify-email test@example.com
```

**Usuarios por defecto:**
- `testuser` / `test@example.com` / `TestPass123!`
- `maria_garcia` / `maria@example.com` / `SecurePass456!`

---

### test-postgres-connection.py

Prueba la conexión a PostgreSQL y verifica configuración.

**Uso:**

```bash
poetry run python scripts/test-postgres-connection.py
```

**Verifica:**
- ✅ Conexión a PostgreSQL exitosa
- ✅ Versión de PostgreSQL
- ✅ Nombre de base de datos
- ✅ Listado de tablas existentes

---

## Testing de Trips

### test_tags.sh

Script interactivo para probar la funcionalidad de tags y filtrado de trips.

**Uso:**

```bash
cd backend
bash scripts/test_tags.sh
```

**Funcionalidades:**
- Crear trips con tags
- Filtrar trips por tag
- Filtrar por status (DRAFT/PUBLISHED)
- Paginación
- Búsqueda de tags populares

Ver [backend/docs/api/TAGS_TESTING.md](../docs/api/TAGS_TESTING.md) para guía completa.

---

## Database Scripts

### init-db.sql

Script SQL ejecutado automáticamente al crear el container de PostgreSQL (via docker-compose).

**Ubicación:** Montado en `/docker-entrypoint-initdb.d/init.sql`

**Función:**
- Configura encoding UTF-8
- Crea extensiones necesarias (uuid-ossp)
- Optimizaciones de performance

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
├── scripts/              # Scripts de automatización
├── storage/             # Archivos subidos (fotos)
├── storage_test/        # Archivos de testing (temporal)
└── contravento_dev.db  # SQLite de desarrollo (si se usa)
```

---

## Troubleshooting

### Script no ejecuta (Linux/Mac)

```bash
# Dar permisos de ejecución
chmod +x backend/scripts/setup-postgres-testing.sh
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
# Verificar conexión
poetry run python scripts/test-postgres-connection.py

# Ver estado de migraciones
poetry run alembic current

# Rollback y re-aplicar
poetry run alembic downgrade base
poetry run alembic upgrade head
```

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
    python scripts/my_script.py [options]
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
```

---

---

## Análisis GPS y RouteStatistics

Scripts para analizar archivos GPX y estadísticas de rutas. Organizados en dos carpetas:

- **`analysis/`**: Scripts Python con la lógica de análisis
- **`wrappers/`**: Scripts Bash para ejecutar los scripts Python de forma sencilla

### Scripts Migrados

| # | Script Python | Bash Wrapper | Dual Mode | Funcionalidad |
|---|--------------|--------------|-----------|---------------|
| 1 | `analyze_gpx_segments.py` | `analyze-segments.sh` | ✅ Sí | Analiza segmentos (slow, long, STOP) para detectar patrones de paradas |
| 2 | `analyze_slow_segments.py` | `analyze-slow-segments.sh` | ✅ Sí | Genera histograma de duración de segmentos lentos (<3 km/h) |
| 3 | `analyze_gpx_timing.py` | `analyze-timing.sh` | ✅ Sí | Analiza espaciado entre puntos GPS (distance gaps) |
| 4 | `check_route_stats.py` | `check-stats.sh` | ❌ DB-only | Verifica existencia de RouteStatistics en la base de datos |
| 5 | `recalculate_route_stats.py` | `recalculate-stats.sh` | ❌ DB-only | Recalcula RouteStatistics para un GPX existente |
| 6 | `delete_corrupt_stats.py` | `delete-stats.sh` | ❌ DB-only | Elimina RouteStatistics corruptas o no deseadas |

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

### Referencia Rápida

```bash
# Análisis (dual mode)
./scripts/wrappers/analyze-segments.sh <gpx_file_id>
./scripts/wrappers/analyze-segments.sh --file-path <ruta>

./scripts/wrappers/analyze-slow-segments.sh <gpx_file_id>
./scripts/wrappers/analyze-slow-segments.sh --file-path <ruta>

./scripts/wrappers/analyze-timing.sh <gpx_file_id>
./scripts/wrappers/analyze-timing.sh --file-path <ruta>

# RouteStatistics (DB-only)
./scripts/wrappers/check-stats.sh <gpx_file_id>
./scripts/wrappers/recalculate-stats.sh <gpx_file_id>
./scripts/wrappers/delete-stats.sh <gpx_file_id>
```

**Documentación completa**: Ver [GPS_ANALYSIS_SCRIPTS.md](GPS_ANALYSIS_SCRIPTS.md)

---

## Referencias

- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) - Guía completa de deployment
- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Guía de testing
- [TAGS_TESTING.md](../docs/api/TAGS_TESTING.md) - Testing de tags
- [GPS_ANALYSIS_SCRIPTS.md](GPS_ANALYSIS_SCRIPTS.md) - Documentación completa de scripts GPS
