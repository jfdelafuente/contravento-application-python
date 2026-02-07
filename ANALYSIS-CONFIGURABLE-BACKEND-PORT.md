# Análisis: Puerto Configurable del Backend

## Objetivo
Permitir configurar el puerto donde escucha el backend mediante variables de entorno, facilitando despliegues en diferentes entornos sin modificar código.

---

## Estado Actual

### ✅ Configuración Existente (Parcialmente Implementada)

**`backend/src/config.py` (línea 138)**
```python
port: int = Field(default=8000, ge=1, le=65535, description="Server port")
backend_url: str = Field(default="http://localhost:8000", ...)
```

⚠️ **Problema**: Esta configuración existe pero **NO se está utilizando** al arrancar uvicorn.

---

## Archivos que Requieren Modificación

### 1. **Dockerfile** (2 ubicaciones)

**`backend/Dockerfile`**

#### Línea 68: EXPOSE (Development)
```dockerfile
# ACTUAL (hardcodeado)
EXPOSE 8000

# PROPUESTO (variable de entorno)
ARG PORT=8000
EXPOSE ${PORT}
```

#### Línea 74: CMD Development (con reload)
```dockerfile
# ACTUAL
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# PROPUESTO (lee de variable de entorno)
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload"]
```

#### Línea 112: EXPOSE (Production)
```dockerfile
# ACTUAL
EXPOSE 8000

# PROPUESTO
ARG PORT=8000
EXPOSE ${PORT}
```

#### Línea 116: HEALTHCHECK
```dockerfile
# ACTUAL
CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# PROPUESTO
CMD sh -c 'python -c "import urllib.request; urllib.request.urlopen(\"http://localhost:${PORT:-8000}/health\").read()"' || exit 1
```

#### Línea 122: CMD Production
```dockerfile
# ACTUAL
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# PROPUESTO
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

---

### 2. **Docker Compose Files** (11 archivos)

Todos los archivos `docker-compose.*.yml` tienen hardcodeado `"8000:8000"`.

#### Ejemplo: `docker-compose.local.yml` (línea ~110)
```yaml
# ACTUAL
ports:
  - "8000:8000"

# PROPUESTO
ports:
  - "${BACKEND_PORT:-8000}:${BACKEND_INTERNAL_PORT:-8000}"
```

**Archivos a modificar**:
- ✅ `docker-compose.yml` (general/default)
- ✅ `docker-compose.local.yml` (local full stack)
- ✅ `docker-compose.local-minimal.yml` (local minimal)
- ✅ `docker-compose.local-prod.yml` (local production)
- ✅ `docker-compose.dev.yml` (dev environment)
- ✅ `docker-compose.staging.yml` (staging - usa Nginx, no expone backend directamente)
- ✅ `docker-compose.prod.yml` (production - usa Nginx, no expone backend directamente)
- ✅ `docker-compose.test.yml` (tests)
- ✅ `docker-compose.preproduction.yml` (preproduction)
- ✅ `docker-compose.preproduction.dev.yml` (preproduction dev)
- ✅ `docker-compose.preproduction.build.yml` (preproduction build)

**Nota Importante**: En staging y production, el backend NO se expone directamente (Nginx hace proxy reverso).

---

### 3. **Scripts de Inicio Local** (2 archivos)

#### `run_backend.sh` (línea 17, 124)
```bash
# ACTUAL
PORT=8000
...
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port $PORT

# PROPUESTO
PORT=${BACKEND_PORT:-8000}
...
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port $PORT
```

#### `run_backend.ps1` (línea 7, ~80)
```powershell
# ACTUAL
$PORT = 8000
...
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port $PORT

# PROPUESTO
$PORT = if ($env:BACKEND_PORT) { $env:BACKEND_PORT } else { 8000 }
...
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port $PORT
```

---

### 4. **Scripts de Testing** (múltiples archivos)

Todos los scripts que apuntan a `http://localhost:8000` deben usar variable de entorno.

#### Patrón General:
```bash
# ACTUAL
BASE_URL="http://localhost:8000"

# PROPUESTO
BASE_URL="${BACKEND_URL:-http://localhost:8000}"
```

**Archivos afectados** (parcial):
- `scripts/run_smoke_tests.sh`
- `scripts/run_smoke_tests.ps1`
- `scripts/run_performance_tests.sh`
- `scripts/testing/gps/*.sh`
- `scripts/testing/gps/*.ps1`
- `scripts/seed/create_test_trips.sh`
- `scripts/seed/create_test_trips.ps1`

---

### 5. **Frontend - Variables de Entorno**

#### `.env.development` / `.env.development.example`
```bash
# ACTUAL
VITE_API_URL=http://localhost:8000

# PROPUESTO (más flexible)
VITE_API_URL=${VITE_API_URL:-http://localhost:8000}
```

**Archivos**:
- `frontend/.env.development`
- `frontend/.env.development.example`
- `frontend/.env.example`

---

### 6. **Documentación CLAUDE.md**

Actualizar referencias hardcodeadas a puerto 8000:
- Línea ~39: "Backend API: http://localhost:8000"
- Línea ~40: "API Docs: http://localhost:8000/docs"
- Múltiples menciones en ejemplos

**Propuesta**: Mencionar que el puerto por defecto es 8000 pero es configurable con `BACKEND_PORT`.

---

## Variables de Entorno Propuestas

### Para Docker Compose:
```bash
# Puerto expuesto en el host
BACKEND_PORT=8000

# Puerto interno del contenedor (normalmente igual al externo)
BACKEND_INTERNAL_PORT=8000

# URL completa del backend (para frontend y scripts)
BACKEND_URL=http://localhost:8000
```

### Para Scripts Locales:
```bash
# Puerto para run_backend.sh/ps1
BACKEND_PORT=8000

# URL para scripts de testing
BACKEND_URL=http://localhost:8000
```

---

## Estrategia de Implementación Recomendada

### Fase 1: Dockerfile y Config (CRÍTICO)
1. ✅ Modificar `backend/Dockerfile` (5 cambios)
2. ✅ Validar que `backend/src/config.py` ya tenga `port` (ya existe)
3. ✅ Opcional: Usar `settings.port` en código si es necesario

### Fase 2: Docker Compose (ALTA PRIORIDAD)
1. ✅ Modificar todos los `docker-compose.*.yml` (11 archivos)
2. ✅ Agregar `BACKEND_PORT` y `BACKEND_INTERNAL_PORT` a archivos `.env.*.example`
3. ✅ Probar cada entorno:
   - local-dev (SQLite)
   - local-minimal (PostgreSQL)
   - local-full (PostgreSQL + servicios)
   - preproduction
   - test

### Fase 3: Scripts de Inicio (MEDIA PRIORIDAD)
1. ✅ Modificar `run_backend.sh`
2. ✅ Modificar `run_backend.ps1`
3. ✅ Probar arranque local sin Docker

### Fase 4: Scripts de Testing (BAJA PRIORIDAD)
1. ✅ Modificar scripts en `scripts/testing/`
2. ✅ Modificar scripts en `scripts/seed/`
3. ✅ Modificar `scripts/run_smoke_tests.*`
4. ✅ Modificar `scripts/run_performance_tests.sh`

### Fase 5: Frontend y Documentación (BAJA PRIORIDAD)
1. ✅ Actualizar `.env.development*` files
2. ✅ Actualizar `CLAUDE.md`
3. ✅ Crear guía en `docs/deployment/` sobre configuración de puertos

---

## Archivos de Configuración Ejemplo

### `.env.local.example`
```bash
# Backend Configuration
BACKEND_PORT=8000
BACKEND_INTERNAL_PORT=8000
BACKEND_URL=http://localhost:8000

# Database
POSTGRES_PASSWORD=local_password
SECRET_KEY=your_secret_key_here

# Volúmenes
BACKEND_STORAGE_PATH=./backend/storage
POSTGRES_DATA_PATH=./data/postgres_local
```

### `.env.preproduction.example`
```bash
# Backend Configuration
BACKEND_PORT=8000
BACKEND_INTERNAL_PORT=8000
BACKEND_URL=http://localhost:8000

# Imágenes Docker Hub
BACKEND_IMAGE=jfdelafuente/contravento-backend:develop
FRONTEND_IMAGE=jfdelafuente/contravento-frontend:develop

# Database
POSTGRES_PASSWORD=jenkins_test_password

# Volúmenes
BACKEND_STORAGE_PATH=/mnt/storage/contravento/uploads
POSTGRES_DATA_PATH=/mnt/storage/contravento/postgres
PGADMIN_DATA_PATH=/mnt/storage/contravento/pgadmin
```

---

## Casos de Uso

### Caso 1: Desarrollo Local con Puerto Personalizado
```bash
# .env.local
BACKEND_PORT=9000
BACKEND_URL=http://localhost:9000

# Arranque
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

# Frontend debe apuntar a:
VITE_API_URL=http://localhost:9000
```

### Caso 2: Múltiples Instancias en el Mismo Host
```bash
# Instancia 1 (develop)
BACKEND_PORT=8000
POSTGRES_PORT=5432

# Instancia 2 (feature branch)
BACKEND_PORT=8001
POSTGRES_PORT=5433

# Evita conflictos de puertos
```

### Caso 3: Producción con Nginx Reverse Proxy
```yaml
# docker-compose.prod.yml
# Backend NO se expone externamente, solo internamente
backend:
  # NO tiene ports: expuestos
  networks:
    - prod-network

nginx:
  ports:
    - "80:80"
    - "443:443"
  # Nginx hace proxy a backend:${BACKEND_INTERNAL_PORT:-8000}
```

---

## Riesgos y Consideraciones

### ⚠️ Riesgos Potenciales:

1. **Healthchecks Hardcodeados**: Si no se actualiza el HEALTHCHECK en Dockerfile, Docker pensará que el servicio está caído
2. **Frontend desincronizado**: Si cambias `BACKEND_PORT` pero no actualizas `VITE_API_URL`, el frontend no podrá conectarse
3. **Scripts de testing**: Fallarán si no usan `BACKEND_URL` configurable
4. **Documentación desactualizada**: Usuarios confundidos si CLAUDE.md sigue diciendo "8000" sin mencionar configurabilidad

### ✅ Mitigaciones:

1. **Testing exhaustivo**: Probar TODOS los entornos después de cambios
2. **Documentación clara**: Actualizar CLAUDE.md y crear guía de configuración
3. **Valores por defecto**: Siempre usar `${VAR:-8000}` para mantener compatibilidad
4. **Validación en CI/CD**: Smoke tests deben verificar que el backend responde en el puerto configurado

---

## Orden de Prioridad para Implementación

### 🔴 Crítico (Fase 1):
- [ ] Dockerfile (5 cambios)
- [ ] run_backend.sh
- [ ] run_backend.ps1

### 🟡 Alta Prioridad (Fase 2):
- [ ] docker-compose.local.yml
- [ ] docker-compose.local-minimal.yml
- [ ] docker-compose.preproduction.dev.yml
- [ ] Archivos `.env.*.example`

### 🟢 Media Prioridad (Fase 3):
- [ ] Resto de docker-compose files
- [ ] Scripts de testing principales

### ⚪ Baja Prioridad (Fase 4):
- [ ] Scripts auxiliares
- [ ] Documentación
- [ ] Frontend .env files

---

## Comandos de Prueba

### Prueba 1: Local con puerto personalizado
```bash
export BACKEND_PORT=9000
./run_backend.sh start

# Verificar
curl http://localhost:9000/health
```

### Prueba 2: Docker Compose con puerto personalizado
```bash
echo "BACKEND_PORT=9000" > .env.local
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

# Verificar
curl http://localhost:9000/health
docker-compose -f docker-compose.local.yml logs backend | grep "Uvicorn running"
```

### Prueba 3: Verificar healthcheck
```bash
docker ps -a | grep contravento-api
# Debe mostrar "healthy" en STATUS
```

---

## Conclusión

**Resumen**: La configuración de puerto ya existe en `config.py` pero no se utiliza. Se requieren cambios en:
- 1 Dockerfile (5 ubicaciones)
- 11 docker-compose files
- 2 scripts de inicio
- ~20 scripts de testing
- 3 archivos .env del frontend
- 1 archivo de documentación (CLAUDE.md)

**Estimación**: 2-3 horas de trabajo + 1 hora de testing exhaustivo.

**Recomendación**: Implementar en fases, empezando por Dockerfile y scripts de inicio (que son los más usados), y luego expandir a docker-compose files y scripts auxiliares.
