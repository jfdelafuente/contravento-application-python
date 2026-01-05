# Guía de Entornos - ContraVento

Esta guía explica cómo usar diferentes archivos de configuración (`.env`) con Docker Compose para los distintos entornos.

## 📋 Archivos de Configuración Disponibles

```
backend/
├── .env.example          # Template base (development con SQLite)
├── .env.testing.example  # Template para testing con PostgreSQL
├── .env.staging.example  # Template para staging (full stack)
└── .env.prod.example     # Template para producción
```

## 🔍 Cómo Docker Compose Lee Variables

Docker Compose resuelve variables en este orden (de mayor a menor prioridad):

1. **Valores directos en la sección `environment` de docker-compose.yml** (hardcoded)
2. **Variables de entorno del shell** (exportadas con `export`)
3. **Archivo especificado con `--env-file`**
4. **Archivo `.env` en el directorio de docker-compose.yml** (por defecto)
5. **Valores por defecto en docker-compose.yml** (`${VAR:-default}`)

**Ejemplo práctico:**

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      # Prioridad 1: Valor hardcoded (siempre gana)
      APP_NAME: ContraVento

      # Prioridad 2-5: Usa shell > --env-file > .env > default
      DATABASE_URL: ${DATABASE_URL:-postgresql://default}
```

```bash
# Prioridad 2: Shell variable (segunda más alta)
export DATABASE_URL="postgresql://from_shell"

# Prioridad 3: --env-file (tercera)
echo "DATABASE_URL=postgresql://from_envfile" > custom.env
docker-compose --env-file custom.env up

# Prioridad 4: .env file (cuarta)
echo "DATABASE_URL=postgresql://from_dotenv" > .env

# Prioridad 5: Default value (última, solo si no hay ninguna otra)
# ${DATABASE_URL:-postgresql://default}
```

### ⚠️ Importante

Docker Compose **NO lee automáticamente** archivos como `.env.testing` o `.env.staging`. Solo lee `.env` por defecto.

## 🚀 Uso de Entornos

### 1️⃣ Desarrollo Local (SQLite)

**Archivo:** `backend/.env` (copiar desde `.env.example`)

```bash
# Setup
cp backend/.env.example backend/.env

# Editar .env si es necesario
nano backend/.env

# Iniciar (lee .env automáticamente)
docker-compose up -d

# O sin Docker (backend local con SQLite)
cd backend
poetry run uvicorn src.main:app --reload
```

**Características:**
- Base de datos: SQLite (archivo local)
- Email: MailHog (testing)
- Debug: habilitado
- Hot reload: activo

---

### 2️⃣ Testing con PostgreSQL

**Archivo:** `backend/.env.testing`

Este entorno usa PostgreSQL en Docker pero el backend corre localmente (no en Docker) para facilitar el debugging.

#### Opción A: Script Automatizado (Más Fácil)

```bash
# Linux/Mac
bash backend/scripts/setup-postgres-testing.sh

# Windows PowerShell
.\backend\scripts\setup-postgres-testing.ps1

# El script hace todo automáticamente:
# ✓ Inicia PostgreSQL
# ✓ Crea database y usuario
# ✓ Aplica migraciones
# ✓ Te da instrucciones para iniciar backend
```

Después de ejecutar el script:

```bash
# Iniciar backend localmente
cd backend
poetry run uvicorn src.main:app --reload
```

#### Opción B: Manual Paso a Paso

```bash
# 1. Crear archivo de configuración
cp backend/.env.testing.example backend/.env.testing

# 2. (Opcional) Editar valores si es necesario
# Los valores por defecto están bien para testing local
# nano backend/.env.testing

# 3. Iniciar solo PostgreSQL (sin backend en Docker)
docker-compose up postgres -d

# 4. Esperar a que PostgreSQL esté listo (5-10 segundos)
sleep 10

# 5. Crear base de datos y usuario de testing
docker exec -it contravento-db psql -U postgres -c "
  CREATE DATABASE contravento_test;
  CREATE USER contravento_test WITH PASSWORD 'test_password';
  GRANT ALL PRIVILEGES ON DATABASE contravento_test TO contravento_test;
"

# 6. Configurar DATABASE_URL para las migraciones
export DATABASE_URL="postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"

# 7. Aplicar migraciones
cd backend
poetry run alembic upgrade head

# 8. Iniciar backend localmente (usa .env.testing automáticamente)
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Opción C: Backend en Docker (menos común)

Si prefieres correr el backend también en Docker:

```bash
# 1. Crear .env.testing
cp backend/.env.testing.example backend/.env.testing

# 2. Iniciar backend + postgres con --env-file
docker-compose --env-file backend/.env.testing up backend postgres -d

# 3. Crear database dentro del container
docker exec -it contravento-db psql -U postgres -c "
  CREATE DATABASE contravento_test;
  CREATE USER contravento_test WITH PASSWORD 'test_password';
  GRANT ALL PRIVILEGES ON DATABASE contravento_test TO contravento_test;
"

# 4. Aplicar migraciones desde el container
docker-compose exec backend alembic upgrade head

# 5. Ver logs
docker-compose logs -f backend
```

**Nota importante:** Si usas esta opción, el DATABASE_URL debe usar `postgres` como host (no `localhost`) porque el backend está dentro de Docker.

**Características:**
- Base de datos: PostgreSQL (solo container de DB)
- Backend: local con Poetry (no en Docker)
- Redis: NO incluido
- MailHog: NO incluido
- Setup: 5 minutos

**¿Cómo lee FastAPI el archivo .env?**

FastAPI/Pydantic Settings busca automáticamente archivos `.env` en este orden:

1. `.env` en el directorio actual (donde ejecutas el comando)
2. Variables de entorno del sistema

Por eso, cuando ejecutas el backend localmente:

```bash
# Si tienes backend/.env.testing
cd backend
poetry run uvicorn src.main:app --reload

# FastAPI buscará automáticamente:
# - backend/.env (por defecto)
#
# Para usar .env.testing, tienes 2 opciones:
# Opción 1: Renombrar temporalmente
mv backend/.env backend/.env.old
mv backend/.env.testing backend/.env
poetry run uvicorn src.main:app --reload

# Opción 2: Exportar DATABASE_URL manualmente
export DATABASE_URL="postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"
export SECRET_KEY="test-secret-key-min-32-characters-for-jwt-signing"
poetry run uvicorn src.main:app --reload
```

**Recomendación:** Para testing, lo más simple es usar `.env` (no `.env.testing`) cuando corres el backend localmente, o exportar las variables necesarias.

---

### 3️⃣ Staging (Full Stack)

**Archivo:** `backend/.env.staging`

```bash
# 1. Crear archivo de staging
cp backend/.env.staging.example backend/.env.staging

# 2. Generar secrets únicos para staging
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(64))"
python -c "import secrets; print('DB_PASSWORD:', secrets.token_urlsafe(32))"
python -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(32))"

# 3. Editar .env.staging con los secrets generados
nano backend/.env.staging

# 4. Iniciar con --env-file (incluye MailHog y pgAdmin)
docker-compose --env-file backend/.env.staging --profile development up -d

# 5. Aplicar migraciones
docker-compose exec backend alembic upgrade head

# 6. Crear usuario de prueba
docker-compose exec backend python scripts/create_verified_user.py

# 7. Verificar
curl http://localhost:8000/health
```

**Acceso a servicios:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MailHog: http://localhost:8025
- pgAdmin: http://localhost:5050

**Características:**
- Base de datos: PostgreSQL (container)
- Backend: Docker container
- Redis: incluido
- MailHog: incluido (opcional: usar SMTP real)
- pgAdmin: incluido
- Setup: 15-30 minutos

---

### 4️⃣ Producción

**Archivo:** `backend/.env.prod`

```bash
# 1. Crear archivo de producción
cp backend/.env.prod.example backend/.env.prod

# 2. Generar secrets FUERTES únicos para producción
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(64))"
python -c "import secrets; print('DB_PASSWORD:', secrets.token_urlsafe(32))"
python -c "import secrets; print('REDIS_PASSWORD:', secrets.token_urlsafe(32))"

# 3. Editar .env.prod con:
#    - Secrets generados
#    - SMTP real (SendGrid, SES, etc.)
#    - CORS_ORIGINS con dominio de producción
nano backend/.env.prod

# 4. Iniciar SIN profile development (no MailHog, no pgAdmin)
docker-compose --env-file backend/.env.prod up -d

# 5. Aplicar migraciones
docker-compose exec backend alembic upgrade head

# 6. Verificar
curl https://tu-dominio.com/health
```

**Características:**
- Base de datos: PostgreSQL (container o RDS)
- Backend: Docker container
- Redis: incluido
- SMTP: servicio real (SendGrid, SES)
- Debug: deshabilitado
- HTTPS: requerido (via Nginx)

---

## 📊 Comparación de Entornos

| Aspecto | Development | Testing | Staging | Production |
|---------|-------------|---------|---------|------------|
| **Base de datos** | SQLite | PostgreSQL | PostgreSQL | PostgreSQL |
| **Backend** | Local/Docker | Local | Docker | Docker |
| **Redis** | Opcional | No | Sí | Sí |
| **Email** | MailHog | Localhost/No | MailHog/Real | SMTP Real |
| **Debug** | true | true | false | false |
| **Setup** | 2 min | 5 min | 15-30 min | 30-60 min |
| **Uso** | Desarrollo diario | Validar PostgreSQL | QA pre-producción | Live users |

---

## 🔧 Comandos Útiles por Entorno

### Desarrollo
```bash
# Usar .env por defecto
docker-compose up -d
docker-compose logs -f
docker-compose down
```

### Testing
```bash
# Solo PostgreSQL (backend local)
docker-compose up postgres -d
docker-compose logs -f postgres
docker-compose down
```

### Staging
```bash
# Full stack con --env-file
docker-compose --env-file backend/.env.staging --profile development up -d
docker-compose logs -f backend
docker-compose --env-file backend/.env.staging down
```

### Producción
```bash
# Full stack sin development profile
docker-compose --env-file backend/.env.prod up -d
docker-compose logs -f
docker-compose --env-file backend/.env.prod down
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

- [backend/docs/DEPLOYMENT.md](backend/docs/DEPLOYMENT.md) - Guía completa de deployment
- [backend/.env.example](backend/.env.example) - Template de desarrollo
- [backend/.env.testing.example](backend/.env.testing.example) - Template de testing
- [backend/.env.staging.example](backend/.env.staging.example) - Template de staging
- [backend/.env.prod.example](backend/.env.prod.example) - Template de producción
- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/) - Documentación oficial

---

## ✅ Checklist Rápido

### Antes de iniciar cualquier entorno:

- [ ] Copiar archivo `.env.{entorno}.example` a `.env.{entorno}`
- [ ] Generar secrets únicos (SECRET_KEY, DB_PASSWORD, REDIS_PASSWORD)
- [ ] Verificar que `DATABASE_URL` es correcto para el entorno
- [ ] Si usas PostgreSQL, crear database y usuario primero
- [ ] Usar `--env-file` con docker-compose si no es `.env`
- [ ] Aplicar migraciones después de iniciar containers
- [ ] Verificar con `curl http://localhost:8000/health`

### Nunca hacer en producción:

- ❌ Usar passwords por defecto ("changeme", "test_password")
- ❌ Usar el mismo SECRET_KEY que desarrollo/staging
- ❌ Dejar DEBUG=true
- ❌ Usar SQLite
- ❌ Permitir CORS desde `*` o localhost
- ❌ Commitear archivos `.env` a git (están en `.gitignore`)
