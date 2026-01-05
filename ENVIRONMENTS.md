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

Docker Compose busca variables en este orden (de mayor a menor prioridad):

1. **Variables de entorno del shell** (exportadas con `export`)
2. **Archivo especificado con `--env-file`**
3. **Archivo `.env` en el directorio de docker-compose.yml** (por defecto)
4. **Valores por defecto en docker-compose.yml** (`${VAR:-default}`)

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

#### Opción A: Con `--env-file` (Recomendado)

```bash
# 1. Crear archivo de testing
cp backend/.env.testing.example backend/.env.testing

# 2. Editar si es necesario (valores por defecto están OK)
nano backend/.env.testing

# 3. Iniciar SOLO PostgreSQL
docker-compose up postgres -d

# 4. Crear base de datos de testing
docker exec -it contravento-db psql -U postgres -c "
  CREATE DATABASE contravento_test;
  CREATE USER contravento_test WITH PASSWORD 'test_password';
  GRANT ALL PRIVILEGES ON DATABASE contravento_test TO contravento_test;
"

# 5. Aplicar migraciones
cd backend
export DATABASE_URL="postgresql+asyncpg://contravento_test:test_password@localhost:5432/contravento_test"
poetry run alembic upgrade head

# 6. Iniciar backend localmente (no con Docker)
poetry run uvicorn src.main:app --reload
```

#### Opción B: Script Automatizado

```bash
# Linux/Mac
bash backend/scripts/setup-postgres-testing.sh

# Windows PowerShell
.\backend\scripts\setup-postgres-testing.ps1
```

**Características:**
- Base de datos: PostgreSQL (solo container de DB)
- Backend: local con Poetry (no en Docker)
- Redis: NO incluido
- MailHog: NO incluido
- Setup: 5 minutos

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

**Causa:** Docker Compose solo lee `.env` por defecto.

**Solución:**

```bash
# Opción 1: Usar --env-file
docker-compose --env-file backend/.env.testing up -d

# Opción 2: Copiar a .env
cp backend/.env.testing backend/.env
docker-compose up -d

# Opción 3: Exportar variables manualmente
export DATABASE_URL="postgresql+asyncpg://..."
docker-compose up -d
```

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
