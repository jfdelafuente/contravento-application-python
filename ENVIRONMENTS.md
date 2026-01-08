# Guía de Entornos - ContraVento

Esta guía explica cómo usar diferentes archivos de configuración (`.env`) con Docker Compose para los distintos entornos.

> **💡 Para iniciar rápido**: Consulta [QUICK_START.md](QUICK_START.md) para guías simples de cada método de deployment.

## 📋 Archivos de Configuración Disponibles

### Archivos en directorio raíz (para Docker Compose)

```
.
├── .env.local-minimal    # Docker Minimal: PostgreSQL + Backend
├── .env.local            # Docker Full: PostgreSQL + Redis + Backend + MailHog + pgAdmin
├── .env.dev.example      # Template para desarrollo (todos los servicios)
├── .env.staging.example  # Template para staging
└── .env.prod.example     # Template para producción
```

### Archivos en backend/ (para ejecución local sin Docker)

```
backend/
├── .env.dev.example      # Template para desarrollo local con SQLite
├── .env.test             # Configuración para tests (pytest con SQLite in-memory)
└── .env.example          # Documentación completa de todas las variables
```

**Separación de archivos .env por propósito:**

- **Raíz**: Variables para Docker Compose (controlan contenedores)
- **backend/**: Variables para FastAPI cuando se ejecuta localmente sin Docker

## 🔍 Cómo Docker Compose Lee Variables

Docker Compose resuelve variables en este orden (de mayor a menor prioridad):

1. **Variables de entorno del shell** (exportadas con `export`)
2. **Archivo especificado con `--env-file`**
3. **Archivo `.env` en el directorio de docker-compose.yml** (por defecto)
4. **Valores por defecto en docker-compose.yml** (`${VAR:-default}`)

**✨ Importante:** Este proyecto **NO usa valores hardcoded** en docker-compose.yml. Todas las variables usan el patrón `${VAR:-default}`, lo que te da máxima flexibilidad para configurar cualquier entorno.

**Ejemplo práctico:**

```yaml
# docker-compose.yml (configuración actual del proyecto)
services:
  postgres:
    environment:
      # Todo es flexible con defaults razonables
      POSTGRES_DB: ${POSTGRES_DB:-contravento}
      POSTGRES_USER: ${POSTGRES_USER:-contravento_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme_in_production}

  backend:
    environment:
      # Todas las variables son configurables
      DATABASE_URL: ${DATABASE_URL:-postgresql+asyncpg://contravento_user:changeme@postgres:5432/contravento}
      DEBUG: ${DEBUG:-false}
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
```

```bash
# Prioridad 1: Shell variable (más alta)
export DATABASE_URL="postgresql://from_shell"
docker-compose up

# Prioridad 2: --env-file (segunda)
echo "DATABASE_URL=postgresql://from_envfile" > custom.env
docker-compose --env-file custom.env up

# Prioridad 3: .env file (tercera)
echo "DATABASE_URL=postgresql://from_dotenv" > .env
docker-compose up

# Prioridad 4: Default value (última, solo si no hay ninguna otra)
# Se usa el valor después de :- en docker-compose.yml
```

### ⚠️ Importante

Docker Compose **NO lee automáticamente** archivos como `.env.testing` o `.env.staging`. Solo lee `.env` por defecto.

## 🚀 Uso de Entornos

### 1️⃣ SQLite Local (Sin Docker) - LA MÁS RÁPIDA ⚡

**Ideal para:** Desarrollo diario, pruebas rápidas, sin necesidad de Docker.

**Scripts automatizados:**

```bash
# Windows
.\run-local-dev.ps1 -Setup    # Primera vez: instala deps, crea .env, migra DB
.\run-local-dev.ps1           # Iniciar servidor
.\run-local-dev.ps1 -Reset    # Resetear base de datos

# Linux/Mac
./run-local-dev.sh --setup    # Primera vez
./run-local-dev.sh            # Iniciar servidor
./run-local-dev.sh --reset    # Resetear base de datos
```

**Características:**
- Base de datos: SQLite archivo (`backend/contravento_dev.db`)
- Backend: Local con Poetry (sin Docker)
- Email: Console logging (no MailHog)
- Setup automático: `.env`, SECRET_KEY, migraciones, usuarios de prueba, achievements
- Velocidad: ⚡ Arranque instantáneo (~200 MB RAM)

**Acceso:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

### 2️⃣ Docker Minimal (PostgreSQL + Backend)

**Ideal para:** Probar con PostgreSQL sin servicios extras.

**Scripts automatizados:**

```bash
# Windows
.\deploy.ps1 local-minimal        # Iniciar
.\deploy.ps1 local-minimal logs   # Ver logs
.\deploy.ps1 local-minimal down   # Detener

# Linux/Mac
./deploy.sh local-minimal         # Iniciar
./deploy.sh local-minimal logs    # Ver logs
./deploy.sh local-minimal down    # Detener
```

**Características:**
- Base de datos: PostgreSQL (container)
- Backend: Docker container con hot reload
- Redis: ❌ No incluido
- MailHog: ❌ No incluido (emails en console)
- pgAdmin: ❌ No incluido (usa DBeaver, TablePlus, psql)
- Velocidad: ~10 segundos (~500 MB RAM)

**Acceso:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

**Configuración:** Edita `.env.local-minimal` (primera vez)

---

### 3️⃣ Docker Full (Todos los Servicios)

**Ideal para:** Desarrollo de auth/email, testing completo, integración.

**Scripts automatizados:**

```bash
# Windows
.\deploy.ps1 local        # Iniciar
.\deploy.ps1 local logs   # Ver logs
.\deploy.ps1 local down   # Detener

# Linux/Mac
./deploy.sh local         # Iniciar
./deploy.sh local logs    # Ver logs
./deploy.sh local down    # Detener
```

**Características:**
- Base de datos: PostgreSQL (container)
- Backend: Docker container con hot reload
- Redis: ✅ Incluido (cache/sesiones - opcional)
- MailHog: ✅ Incluido (email testing)
- pgAdmin: ✅ Incluido (UI web para DB)
- Velocidad: ~30 segundos (~1 GB RAM)

**Acceso:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- MailHog UI: http://localhost:8025
- pgAdmin: http://localhost:5050
- PostgreSQL: localhost:5432
- Redis: localhost:6379

**Configuración:** Edita `.env.local` (primera vez)

---

### 4️⃣ Testing Automatizado (pytest)

**Archivo:** `backend/.env.test`

**Configuración automática con conftest.py** - Los tests usan un archivo `.env.test` que se carga automáticamente al ejecutar pytest.

**Ejecución de tests:**

```bash
cd backend

# Ejecutar todos los tests (usa .env.test automáticamente)
poetry run pytest

# Tests con coverage
poetry run pytest --cov=src --cov-report=html

# Tests por categoría
poetry run pytest tests/unit/ -v              # Solo unit tests
poetry run pytest tests/integration/ -v       # Solo integration tests
poetry run pytest -m unit                     # Por marker
```

**Características:**

- Base de datos: **SQLite in-memory** (`:memory:`)
- Configuración: Carga automática desde `backend/.env.test` via `conftest.py`
- Performance: BCRYPT_ROUNDS=4 (hashing rápido ~10ms vs 300ms)
- Aislamiento: Cada test tiene DB fresh y limpia
- Log level: WARNING (reduce ruido en output)

**¿Cómo funciona la carga automática?**

El archivo `backend/tests/conftest.py` tiene un fixture con `autouse=True`:

```python
@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Load test environment variables from .env.test"""
    env_file = Path(__file__).parent.parent / ".env.test"

    if env_file.exists():
        load_dotenv(env_file, override=True)
        os.environ["APP_ENV"] = "testing"
```

Este fixture se ejecuta **automáticamente** antes de cualquier test, por lo que no necesitas configuración manual.

**Documentación completa:** Ver [backend/docs/TESTING_CONFIGURATION.md](backend/docs/TESTING_CONFIGURATION.md) para detalles sobre:

- Explicación detallada de cada variable de `.env.test`
- Troubleshooting de problemas comunes
- Customización de configuración de tests
- Best practices

---

### 5️⃣ Staging (Full Stack con Docker)

**Archivo:** `.env.staging.example` (raíz del proyecto)

**Ideal para:** QA, pre-producción, testing antes de deploy.

```bash
# 1. Crear archivo de staging
cp .env.staging.example .env.staging

# 2. Generar secrets únicos para staging
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(64))"
python -c "import secrets; print('DB_PASSWORD:', secrets.token_urlsafe(32))"
python -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(32))"

# 3. Editar .env.staging con los secrets generados
nano .env.staging

# 4. Iniciar con scripts de deployment
./deploy.sh staging        # Linux/Mac
.\deploy.ps1 staging       # Windows

# 5. Aplicar migraciones
docker-compose exec backend poetry run alembic upgrade head

# 6. Crear usuario de prueba
docker-compose exec backend poetry run python scripts/create_verified_user.py

# 7. Verificar
curl http://localhost:8000/health
```

**Características:**

- Base de datos: PostgreSQL (container)
- Backend: Docker container
- Redis: ✅ Incluido
- BCRYPT_ROUNDS: 12 (más seguro que dev)
- Email: MailHog o SMTP real
- Debug: false
- Setup: 15-30 minutos

---

### 6️⃣ Producción (Docker)

**Archivo:** `.env.prod.example` (raíz del proyecto)

**Ideal para:** Deployment en servidor de producción.

```bash
# 1. Crear archivo de producción
cp .env.prod.example .env.prod

# 2. Generar secrets FUERTES únicos para producción
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(64))"
python -c "import secrets; print('DB_PASSWORD:', secrets.token_urlsafe(32))"
python -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(32))"

# 3. Editar .env.prod con:
#    - Secrets generados
#    - SMTP real (SendGrid, SES, etc.)
#    - CORS_ORIGINS con dominio de producción
nano .env.prod

# 4. Iniciar con scripts de deployment
./deploy.sh prod           # Linux/Mac
.\deploy.ps1 prod          # Windows

# 5. Aplicar migraciones
docker-compose exec backend poetry run alembic upgrade head

# 6. Verificar
curl https://tu-dominio.com/health
```

**Características:**

- Base de datos: PostgreSQL (container o RDS)
- Backend: Docker container
- Redis: ✅ Incluido
- BCRYPT_ROUNDS: 14 (máxima seguridad)
- SMTP: Servicio real (SendGrid, SES)
- Debug: false
- HTTPS: Requerido (vía Nginx)
- MailHog/pgAdmin: ❌ No incluidos

---

## 📊 Comparación de Entornos

| Aspecto | SQLite Local | Docker Minimal | Docker Full | Testing | Staging | Production |
|---------|:------------:|:--------------:|:-----------:|:-------:|:-------:|:----------:|
| **Base de datos** | SQLite | PostgreSQL | PostgreSQL | SQLite (memory) | PostgreSQL | PostgreSQL |
| **Backend** | Local | Docker | Docker | Local (pytest) | Docker | Docker |
| **Redis** | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Email** | Console | Console | MailHog | Mocked | MailHog/Real | SMTP Real |
| **Debug** | true | true | true | false | false | false |
| **BCRYPT** | 4 rounds | 4 rounds | 4 rounds | 4 rounds | 12 rounds | 14 rounds |
| **Setup** | Instantáneo | ~10 seg | ~30 seg | Automático | 15-30 min | 30-60 min |
| **RAM** | ~200 MB | ~500 MB | ~1 GB | Mínimo | Variable | Variable |
| **Uso** | Desarrollo diario | Testing PostgreSQL | Desarrollo full-stack | Tests automatizados | QA/Pre-prod | Usuarios reales |

---

## 🔧 Comandos Útiles por Entorno

### SQLite Local (Sin Docker)

```bash
# Windows
.\run-local-dev.ps1 -Setup    # Primera vez
.\run-local-dev.ps1           # Iniciar
.\run-local-dev.ps1 -Reset    # Resetear DB

# Linux/Mac
./run-local-dev.sh --setup    # Primera vez
./run-local-dev.sh            # Iniciar
./run-local-dev.sh --reset    # Resetear DB
```

### Docker Minimal

```bash
# Windows
.\deploy.ps1 local-minimal
.\deploy.ps1 local-minimal logs
.\deploy.ps1 local-minimal down

# Linux/Mac
./deploy.sh local-minimal
./deploy.sh local-minimal logs
./deploy.sh local-minimal down
```

### Docker Full

```bash
# Windows
.\deploy.ps1 local
.\deploy.ps1 local logs
.\deploy.ps1 local down

# Linux/Mac
./deploy.sh local
./deploy.sh local logs
./deploy.sh local down
```

### Testing (pytest)

```bash
cd backend
poetry run pytest                           # Todos los tests
poetry run pytest --cov=src                 # Con coverage
poetry run pytest tests/unit/ -v            # Solo unit tests
```

### Staging

```bash
# Windows
.\deploy.ps1 staging
.\deploy.ps1 staging logs
.\deploy.ps1 staging down

# Linux/Mac
./deploy.sh staging
./deploy.sh staging logs
./deploy.sh staging down
```

### Producción

```bash
# Windows
.\deploy.ps1 prod
.\deploy.ps1 prod logs
.\deploy.ps1 prod down

# Linux/Mac
./deploy.sh prod
./deploy.sh prod logs
./deploy.sh prod down
```

---

## 🐛 Troubleshooting

### Error: "password authentication failed for user"

**Causa:** El `DATABASE_URL` en tu archivo `.env` no coincide con el usuario/password de PostgreSQL.

**Solución:**

```bash
# 1. Verificar qué DATABASE_URL está usando docker-compose
docker-compose --env-file backend/.env.testing config | grep DATABASE_URL

# 2. Verificar usuario en PostgreSQL
docker exec -it contravento-db psql -U postgres -c "\du"

# 3. Resetear password del usuario
docker exec -it contravento-db psql -U postgres -c "
  ALTER USER contravento_test WITH PASSWORD 'test_password';
"

# 4. O crear usuario si no existe
docker exec -it contravento-db psql -U postgres -c "
  CREATE USER contravento_test WITH PASSWORD 'test_password';
  GRANT ALL PRIVILEGES ON DATABASE contravento_test TO contravento_test;
"
```

### Error: Docker Compose no lee mi archivo .env.testing

**Causa:** Docker Compose solo lee `.env` por defecto. Los archivos `.env.testing`, `.env.staging`, etc. deben especificarse explícitamente con `--env-file`.

**Solución:**

```bash
# Opción 1: Usar --env-file (RECOMENDADO)
docker-compose --env-file backend/.env.testing up -d

# Opción 2: Copiar a .env
cp backend/.env.testing backend/.env
docker-compose up -d

# Opción 3: Exportar variables manualmente
export DATABASE_URL="postgresql+asyncpg://..."
docker-compose up -d
```

### Error: FastAPI no lee mi archivo .env.testing

**Causa:** Pydantic Settings (usado por FastAPI) solo busca archivos llamados `.env` por defecto.

**Solución:**

```bash
# Opción 1: Usar .env como nombre de archivo (RECOMENDADO para local)
cp backend/.env.testing backend/.env
cd backend
poetry run uvicorn src.main:app --reload

# Opción 2: Exportar variables de entorno
export DATABASE_URL="postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"
export SECRET_KEY="test-secret-key-min-32-characters-for-jwt-signing"
cd backend
poetry run uvicorn src.main:app --reload

# Opción 3: Especificar archivo en código (requiere cambios en config.py)
# NO RECOMENDADO - mejor usar opciones 1 o 2
```

**Diferencia importante:**

| Tool | Archivo por defecto | Cómo usar otros archivos |
|------|---------------------|--------------------------|
| **Docker Compose** | `.env` | `--env-file ruta/archivo.env` |
| **FastAPI/Pydantic** | `.env` | Exportar variables o renombrar a `.env` |

Por eso, para testing local recomendamos:
1. **PostgreSQL en Docker** → usa `docker-compose up postgres -d` (no necesita .env)
2. **Backend local** → usa `backend/.env` (crear/modificar desde .env.testing)
3. **Migraciones** → usa `export DATABASE_URL=...` antes de ejecutar

### Error: Variable no definida en docker-compose

**Causa:** Falta una variable requerida en tu archivo `.env`.

**Solución:**

```bash
# Ver qué variables necesita docker-compose
docker-compose config

# Ver valores actuales (sin iniciar containers)
docker-compose --env-file backend/.env.testing config | grep -A 5 environment

# Asegurarse de que el archivo .env tiene todas las variables
# Comparar con .env.example
diff backend/.env.testing backend/.env.testing.example
```

---

## 📚 Referencias

### Documentación del Proyecto

- **[QUICK_START.md](QUICK_START.md)** - Guía rápida de deployment (recomendado empezar aquí)
- **[backend/docs/DEPLOYMENT.md](backend/docs/DEPLOYMENT.md)** - Guía completa de deployment (Docker, cloud, tradicional)
- **[backend/docs/TESTING_CONFIGURATION.md](backend/docs/TESTING_CONFIGURATION.md)** - Configuración de tests con `.env.test`

### Archivos de Configuración (Raíz - Docker Compose)

- [.env.local-minimal](.env.local-minimal) - Docker Minimal (PostgreSQL + Backend)
- [.env.local](.env.local) - Docker Full (todos los servicios)
- [.env.dev.example](.env.dev.example) - Template para desarrollo con Docker
- [.env.staging.example](.env.staging.example) - Template para staging
- [.env.prod.example](.env.prod.example) - Template para producción

### Archivos de Configuración (backend/ - Ejecución Local)

- [backend/.env.dev.example](backend/.env.dev.example) - Template para SQLite local
- [backend/.env.test](backend/.env.test) - Configuración para tests (pytest)
- [backend/.env.example](backend/.env.example) - Documentación completa de variables

### Scripts de Deployment

- [run-local-dev.ps1](run-local-dev.ps1) - Setup y servidor local SQLite (Windows)
- [run-local-dev.sh](run-local-dev.sh) - Setup y servidor local SQLite (Linux/Mac)
- [deploy.ps1](deploy.ps1) - Deployment con Docker (Windows)
- [deploy.sh](deploy.sh) - Deployment con Docker (Linux/Mac)

### Documentación Externa

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/) - Documentación oficial de Docker Compose
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Cómo Pydantic carga archivos .env

---

## ✅ Checklist Rápido

### Antes de iniciar cualquier entorno

**SQLite Local (Sin Docker):**

- [ ] Ejecutar `./run-local-dev.sh --setup` o `.\run-local-dev.ps1 -Setup`
- [ ] El script hace todo automáticamente (deps, .env, SECRET_KEY, migraciones, usuarios)
- [ ] Verificar: <http://localhost:8000/health>

**Docker Minimal/Full:**

- [ ] Ejecutar script de deployment: `./deploy.sh local-minimal` o `.\deploy.ps1 local`
- [ ] Editar `.env.local-minimal` o `.env.local` si es necesario
- [ ] Verificar containers: `docker-compose ps`
- [ ] Verificar: <http://localhost:8000/health>

**Testing (pytest):**

- [ ] El archivo `backend/.env.test` ya existe y está configurado
- [ ] Ejecutar: `cd backend && poetry run pytest`
- [ ] No requiere configuración manual (carga automática)

**Staging/Producción:**

- [ ] Copiar archivo: `cp .env.{entorno}.example .env.{entorno}`
- [ ] Generar secrets únicos (SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD)
- [ ] Editar .env con secrets y configuración específica
- [ ] Usar scripts: `./deploy.sh {entorno}` o `.\deploy.ps1 {entorno}`
- [ ] Aplicar migraciones: `docker-compose exec backend poetry run alembic upgrade head`
- [ ] Verificar salud del servicio

### ⚠️ Nunca hacer en producción

- ❌ Usar passwords por defecto ("changeme", "test_password")
- ❌ Usar el mismo SECRET_KEY que desarrollo/staging
- ❌ Dejar DEBUG=true
- ❌ Usar SQLite (solo para dev/testing)
- ❌ Usar BCRYPT_ROUNDS bajo (4 solo para dev/tests, 14 para prod)
- ❌ Permitir CORS desde `*` o localhost
- ❌ Commitear archivos `.env` a git (están en `.gitignore`)
- ❌ Exponer servicios internos (Redis, PostgreSQL) sin autenticación
