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

## Referencias

- [DEPLOYMENT.md](../docs/DEPLOYMENT.md) - Guía completa de deployment
- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Guía de testing
- [TAGS_TESTING.md](../docs/api/TAGS_TESTING.md) - Testing de tags
