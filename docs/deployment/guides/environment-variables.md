# Environment Variables Reference

**Complete configuration guide for all deployment modes**

**Purpose**: Central reference for all `.env` configuration options across all deployment modes

---

## Table of Contents

1. [Overview](#overview)
2. [File Locations](#file-locations)
3. [Variable Categories](#variable-categories)
4. [Configuration by Mode](#configuration-by-mode)
5. [Security Best Practices](#security-best-practices)
6. [Generating Secrets](#generating-secrets)
7. [Common Pitfalls](#common-pitfalls)

---

## Overview

ContraVento uses environment variables (`.env` files) to configure behavior across different deployment modes. Variables are organized into:

- **Backend variables**: Database, auth, email, storage
- **Frontend variables**: API URL, external services (Turnstile)
- **Docker variables**: Container configuration, networking
- **Testing variables**: Test-specific overrides

**Key Principle**: All modes use the same variable names, only values change.

---

## File Locations

### Root Directory (Docker Compose)

Used when running containers with `docker-compose`:

```
.
├── .env.local-minimal     # Docker Minimal (PostgreSQL + Backend)
├── .env.local             # Docker Full (all services)
├── .env.dev.example       # Template for dev server
├── .env.staging.example   # Template for staging
└── .env.prod.example      # Template for production
```

### Backend Directory (Local Execution)

Used when running backend locally without Docker:

```
backend/
├── .env                   # Active config (git-ignored)
├── .env.dev.example       # Template for SQLite local dev
├── .env.test              # Test configuration (pytest)
└── .env.example           # Full documentation of all variables
```

### Frontend Directory (Vite Builds)

Used when building frontend with Vite:

```
frontend/
├── .env.development       # Auto-loaded in dev mode (npm run dev)
├── .env.staging           # Used by npm run build:staging
├── .env.production        # Used by npm run build:prod
└── .env.example           # Template with all frontend variables
```

**Important**: Docker Compose only reads `.env` by default. Use `--env-file` for other files:
```bash
docker-compose --env-file .env.staging up
```

---

## Variable Categories

### 1. Database Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Full database connection string | ✅ Yes | Varies by mode |
| `POSTGRES_DB` | PostgreSQL database name | Docker only | `contravento` |
| `POSTGRES_USER` | PostgreSQL username | Docker only | `contravento_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | Docker only | `changeme` ⚠️ |
| `DB_ECHO` | Log all SQL queries | No | `false` |

**Examples**:

```env
# SQLite (local-dev)
DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db

# PostgreSQL (Docker local)
DATABASE_URL=postgresql+asyncpg://contravento_user:changeme@db:5432/contravento

# PostgreSQL (Docker host access)
DATABASE_URL=postgresql+asyncpg://contravento_user:changeme@localhost:5432/contravento

# PostgreSQL (production with SSL)
DATABASE_URL=postgresql+asyncpg://user:password@prod-db.example.com:5432/contravento?ssl=require
```

**⚠️ Important**:
- SQLite uses `sqlite+aiosqlite://` (async driver)
- PostgreSQL uses `postgresql+asyncpg://` (async driver)
- Change hostname from `db` (Docker internal) to `localhost` (host access)

---

### 2. Authentication & Security

| Variable | Description | Required | Default | Notes |
|----------|-------------|----------|---------|-------|
| `SECRET_KEY` | JWT token signing secret | ✅ Yes | None | Min 32 chars |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | No | `15` | Short-lived |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | No | `30` | Long-lived |
| `BCRYPT_ROUNDS` | Password hashing cost | No | Mode-specific | See table below |
| `CORS_ORIGINS` | Allowed CORS origins | No | `http://localhost:5173,http://localhost:3000` | Comma-separated |

**BCRYPT_ROUNDS by Mode**:

| Mode | Rounds | Hashing Time | Security Level |
|------|--------|--------------|----------------|
| local-dev | 4 | ~10 ms | ⚠️ Weak (dev only) |
| local-minimal | 4 | ~10 ms | ⚠️ Weak (dev only) |
| local-full | 4 | ~10 ms | ⚠️ Weak (dev only) |
| test | 4 | ~10 ms | ⚠️ Weak (fast tests) |
| staging | 12 | ~300 ms | ✅ Strong |
| production | 14 | ~700 ms | ✅ Very strong |

**Security Requirements**:
- `SECRET_KEY` must be ≥32 characters
- Use unique `SECRET_KEY` for each environment
- Never commit real `SECRET_KEY` to git
- Use HTTPS in production (enforces secure token transmission)

**Example**:
```env
# Development (weak for speed)
SECRET_KEY=dev-secret-key-min-32-characters-for-jwt-signing-change-in-production
BCRYPT_ROUNDS=4
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Production (strong)
SECRET_KEY=<USE_GENERATED_SECRET_64_CHARS_LONG>
BCRYPT_ROUNDS=14
CORS_ORIGINS=https://contravento.com,https://www.contravento.com
```

---

### 3. Email Configuration

| Variable | Description | Required | Default | Notes |
|----------|-------------|----------|---------|-------|
| `SMTP_HOST` | SMTP server hostname | For production | `localhost` | Use real SMTP in prod |
| `SMTP_PORT` | SMTP server port | No | `1025` | 1025=MailHog, 587=TLS |
| `SMTP_USER` | SMTP username | For auth | None | Optional for MailHog |
| `SMTP_PASSWORD` | SMTP password | For auth | None | Required for real SMTP |
| `SMTP_FROM_EMAIL` | Sender email address | No | `noreply@contravento.com` | Must match SMTP domain |
| `SMTP_FROM_NAME` | Sender display name | No | `ContraVento` | Shown in email client |

**Modes**:

**local-dev (Console Logging)**:
```env
# Emails printed to console only (no SMTP)
# No configuration needed
```

**local-full (MailHog)**:
```env
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_FROM_EMAIL=noreply@contravento.local
SMTP_FROM_NAME=ContraVento Dev
```

**Staging/Production (Real SMTP)**:
```env
# Example: SendGrid
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<SENDGRID_API_KEY>
SMTP_FROM_EMAIL=noreply@contravento.com
SMTP_FROM_NAME=ContraVento

# Example: AWS SES
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=<AWS_ACCESS_KEY_ID>
SMTP_PASSWORD=<AWS_SECRET_ACCESS_KEY>
SMTP_FROM_EMAIL=noreply@contravento.com
SMTP_FROM_NAME=ContraVento
```

**Email Templates**:
- Registration: `Verifica tu cuenta en ContraVento`
- Password Reset: `Restablece tu contraseña`
- Welcome: `Bienvenido a ContraVento`

---

### 4. Storage & File Uploads

| Variable | Description | Required | Default | Notes |
|----------|-------------|----------|---------|-------|
| `UPLOAD_DIR` | Base directory for uploads | No | `storage/` | Relative to backend/ |
| `PROFILE_PHOTOS_DIR` | Profile photo subdirectory | No | `storage/profile_photos/` | Auto-created |
| `TRIP_PHOTOS_DIR` | Trip photo subdirectory | No | `storage/trip_photos/` | Auto-created |
| `UPLOAD_MAX_SIZE_MB` | Max upload size (MB) | No | `5` | Per-file limit |
| `ALLOWED_IMAGE_TYPES` | Accepted MIME types | No | `image/jpeg,image/png,image/webp` | Comma-separated |

**File Organization**:
```
storage/
├── profile_photos/
│   ├── 2024/01/user_abc123.jpg
│   └── 2024/02/user_def456.jpg
├── trip_photos/
│   ├── 2024/01/trip_xyz789/photo_001.jpg
│   └── 2024/01/trip_xyz789/photo_002.jpg
└── gpx_files/
    └── 2024/01/trip_xyz789.gpx
```

**Docker Volume Mount**:
```yaml
# In docker-compose.yml
services:
  backend:
    volumes:
      - ./storage:/app/storage  # Persist uploads
```

**Permissions**:
```bash
# Linux/Mac
chmod 755 storage/
chown -R $USER:$USER storage/

# Docker (from inside container)
chown -R app:app /app/storage
```

---

### 5. Frontend (Vite) Variables

All frontend variables must be prefixed with `VITE_` to be exposed to client-side code.

| Variable | Description | Required | Default | Security |
|----------|-------------|----------|---------|----------|
| `VITE_API_URL` | Backend API base URL | ✅ Yes | Mode-specific | ✅ Public (safe) |
| `VITE_TURNSTILE_SITE_KEY` | Cloudflare Turnstile public key | No | Test key | ✅ Public (safe) |

**⚠️ Security Warning**:
- Variables with `VITE_` prefix are **publicly visible** in browser
- Never put API secrets, private keys, or passwords in `VITE_*` variables
- Backend API handles authentication (JWT tokens)

**Examples by Mode**:

```env
# .env.development (local dev)
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA

# .env.staging
VITE_API_URL=https://api-staging.contravento.com
VITE_TURNSTILE_SITE_KEY=<STAGING_SITE_KEY>

# .env.production
VITE_API_URL=https://api.contravento.com
VITE_TURNSTILE_SITE_KEY=<PRODUCTION_SITE_KEY>
```

**Usage in Code**:
```typescript
// frontend/src/config.ts
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const TURNSTILE_SITE_KEY = import.meta.env.VITE_TURNSTILE_SITE_KEY;
```

---

### 6. Logging & Debugging

| Variable | Description | Required | Default | Production |
|----------|-------------|----------|---------|------------|
| `DEBUG` | Enable debug mode | No | `false` | ❌ Must be `false` |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` | `WARNING` or `ERROR` |
| `LOG_FORMAT` | Log output format | No | `json` | Use `json` for parsing |

**LOG_LEVEL Values** (most to least verbose):
- `DEBUG`: All logs (queries, internal operations)
- `INFO`: General information (startup, requests)
- `WARNING`: Warnings and errors
- `ERROR`: Only errors
- `CRITICAL`: Only critical failures

**Examples**:
```env
# Development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text

# Production
DEBUG=false
LOG_LEVEL=WARNING
LOG_FORMAT=json
```

---

### 7. Testing Variables

Used by pytest (`backend/.env.test`):

| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | `sqlite+aiosqlite:///:memory:` | In-memory DB (fast, isolated) |
| `SECRET_KEY` | `test-secret-key-min-32-characters` | Test JWT signing |
| `BCRYPT_ROUNDS` | `4` | Fast hashing (~10ms vs 700ms) |
| `LOG_LEVEL` | `WARNING` | Reduce test output noise |
| `UPLOAD_DIR` | `storage/test/` | Isolated test uploads |
| `DEBUG` | `false` | Production-like behavior |

**Auto-Loading**:
Tests automatically load `backend/.env.test` via `conftest.py`:
```python
@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Load test environment variables from .env.test"""
    env_file = Path(__file__).parent.parent / ".env.test"
    if env_file.exists():
        load_dotenv(env_file, override=True)
```

**No manual configuration needed** - just run `poetry run pytest`.

---

### 8. Redis (Caching) Variables

Only used in `local-full`, `staging`, and `production` modes:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REDIS_HOST` | Redis server hostname | Docker only | `redis` |
| `REDIS_PORT` | Redis server port | No | `6379` |
| `REDIS_PASSWORD` | Redis password | Staging/Prod | None (dev) |
| `REDIS_DB` | Redis database number | No | `0` |

**Examples**:
```env
# local-full (Docker, no password)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Production (with password)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<GENERATED_PASSWORD>
REDIS_DB=0
```

**Usage**:
- Session storage
- API response caching
- Rate limiting counters
- Celery task queue (future feature)

---

## Configuration by Mode

### local-dev (SQLite, No Docker)

**File**: `backend/.env` (auto-created by setup script)

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db

# Security
SECRET_KEY=<AUTO_GENERATED_32_CHARS>
BCRYPT_ROUNDS=4
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Email (console logging only)
# No SMTP configuration needed

# Uploads
UPLOAD_DIR=storage/
UPLOAD_MAX_SIZE_MB=5

# Logging
DEBUG=true
LOG_LEVEL=DEBUG
```

**Created by**: `./run-local-dev.sh --setup` or `.\run-local-dev.ps1 -Setup`

---

### local-minimal (Docker + PostgreSQL)

**File**: `.env.local-minimal`

```env
# Database (Docker internal)
DATABASE_URL=postgresql+asyncpg://contravento_user:changeme@db:5432/contravento
POSTGRES_DB=contravento
POSTGRES_USER=contravento_user
POSTGRES_PASSWORD=changeme

# Security
SECRET_KEY=dev-secret-key-min-32-characters-change-in-production
BCRYPT_ROUNDS=4
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Email (console logging)
# No SMTP needed

# Logging
DEBUG=true
LOG_LEVEL=INFO
```

---

### local-full (Docker + All Services)

**File**: `.env.local`

```env
# Database
DATABASE_URL=postgresql+asyncpg://contravento_user:local_password@db:5432/contravento
POSTGRES_DB=contravento
POSTGRES_USER=contravento_user
POSTGRES_PASSWORD=local_password

# Security
SECRET_KEY=dev-secret-key-min-32-characters-change-in-production
BCRYPT_ROUNDS=4
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Email (MailHog)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_FROM_EMAIL=noreply@contravento.local
SMTP_FROM_NAME=ContraVento Dev

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@contravento.local
PGADMIN_DEFAULT_PASSWORD=admin

# Logging
DEBUG=true
LOG_LEVEL=INFO
```

---

### test (pytest)

**File**: `backend/.env.test` (pre-configured, no edits needed)

```env
# Database (in-memory SQLite)
DATABASE_URL=sqlite+aiosqlite:///:memory:

# Security (weak for speed)
SECRET_KEY=test-secret-key-min-32-characters-for-jwt-signing
BCRYPT_ROUNDS=4

# Uploads (isolated directory)
UPLOAD_DIR=storage/test/

# Logging (reduce noise)
DEBUG=false
LOG_LEVEL=WARNING

# Testing flags
TESTING=true
```

**Auto-loaded by pytest** - no manual setup required.

---

### staging

**File**: `.env.staging` (create from `.env.staging.example`)

```env
# Database (production-like)
DATABASE_URL=postgresql+asyncpg://contravento_user:<STRONG_PASSWORD>@db:5432/contravento
POSTGRES_DB=contravento
POSTGRES_USER=contravento_user
POSTGRES_PASSWORD=<STRONG_PASSWORD>

# Security (strong)
SECRET_KEY=<GENERATED_SECRET_64_CHARS>
BCRYPT_ROUNDS=12
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
CORS_ORIGINS=https://staging.contravento.com

# Email (real SMTP or MailHog)
SMTP_HOST=smtp.sendgrid.net  # Or mailhog for testing
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<SENDGRID_API_KEY>
SMTP_FROM_EMAIL=noreply@staging.contravento.com
SMTP_FROM_NAME=ContraVento Staging

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<GENERATED_PASSWORD>
REDIS_DB=0

# Logging
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

### production

**File**: `.env.prod` (create from `.env.prod.example`)

```env
# Database (managed service recommended)
DATABASE_URL=postgresql+asyncpg://contravento_user:<VERY_STRONG_PASSWORD>@prod-db.example.com:5432/contravento?ssl=require
POSTGRES_DB=contravento
POSTGRES_USER=contravento_user
POSTGRES_PASSWORD=<VERY_STRONG_PASSWORD>

# Security (maximum strength)
SECRET_KEY=<GENERATED_SECRET_64_CHARS_UNIQUE>
BCRYPT_ROUNDS=14
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
CORS_ORIGINS=https://contravento.com,https://www.contravento.com

# Email (real SMTP required)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<PRODUCTION_SENDGRID_KEY>
SMTP_FROM_EMAIL=noreply@contravento.com
SMTP_FROM_NAME=ContraVento

# Redis (managed service recommended)
REDIS_HOST=prod-redis.example.com
REDIS_PORT=6379
REDIS_PASSWORD=<VERY_STRONG_PASSWORD>
REDIS_DB=0
REDIS_SSL=true

# Logging
DEBUG=false
LOG_LEVEL=WARNING
LOG_FORMAT=json

# Monitoring
SENTRY_DSN=<SENTRY_PROJECT_DSN>  # Optional error tracking
```

**⚠️ Production Checklist**:
- [ ] Unique `SECRET_KEY` (never reuse from dev/staging)
- [ ] Strong `POSTGRES_PASSWORD` (≥32 chars, random)
- [ ] Strong `REDIS_PASSWORD` (≥32 chars, random)
- [ ] Real SMTP configured (SendGrid, AWS SES, etc.)
- [ ] CORS limited to production domains only
- [ ] `DEBUG=false`
- [ ] `BCRYPT_ROUNDS=14`
- [ ] SSL enabled for database (`?ssl=require`)
- [ ] All `.env` files in `.gitignore`

---

## Security Best Practices

### 1. Secret Generation

**Never use default secrets** (`changeme`, `test_password`, etc.) in staging/production.

**Generate strong secrets**:

```bash
# SECRET_KEY (64 characters recommended)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Database passwords (32 characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Redis passwords (32 characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output**:
```
SECRET_KEY: kJ9mN3pQ2wR5tY8uI0oP7aS4dF6gH1jK9lZ3xC5vB8nM2qW4eR6tY0uI3oP5aS7dF
DB_PASSWORD: xK2mN5pQ8wR1tY4uI7oP0aS3dF6gH9jK2lZ5
REDIS_PASSWORD: vB8nM2qW4eR6tY0uI3oP5aS7dF9gH1jK4lZ7
```

### 2. Environment Separation

**Use unique secrets for each environment**:

```bash
# ❌ WRONG - Same secret everywhere
SECRET_KEY=my-secret-123  # All environments

# ✅ CORRECT - Unique per environment
# .env.local
SECRET_KEY=dev-secret-abc123...

# .env.staging
SECRET_KEY=staging-secret-xyz789...

# .env.prod
SECRET_KEY=prod-secret-mno456...
```

**Why**: If dev environment is compromised, production remains secure.

### 3. Git Safety

**.gitignore must include**:
```gitignore
# Environment files (never commit)
.env
.env.local
.env.staging
.env.production
.env.prod

# Only commit templates
!.env.example
!.env.*.example
```

**Verify**:
```bash
# Check if .env is git-ignored
git check-ignore .env
# Should output: .env

# Check what would be committed
git status --ignored
# .env files should appear in "Ignored files"
```

### 4. Principle of Least Privilege

**Database users**:
```sql
-- ❌ WRONG - Using superuser
CREATE USER contravento WITH SUPERUSER PASSWORD '...';

-- ✅ CORRECT - Limited permissions
CREATE USER contravento WITH PASSWORD '...';
GRANT CONNECT ON DATABASE contravento TO contravento;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO contravento;
```

**CORS**:
```env
# ❌ WRONG - Allow all origins
CORS_ORIGINS=*

# ✅ CORRECT - Specific domains only
CORS_ORIGINS=https://contravento.com,https://www.contravento.com
```

### 5. Secrets Management (Production)

**For large deployments, use secret managers**:

- **AWS**: Secrets Manager or Parameter Store
- **Google Cloud**: Secret Manager
- **Azure**: Key Vault
- **HashiCorp**: Vault
- **Docker**: Docker Secrets (Swarm mode)

**Example with AWS Secrets Manager**:
```bash
# Store secret
aws secretsmanager create-secret \
  --name contravento/prod/secret-key \
  --secret-string "<GENERATED_SECRET>"

# Retrieve in container startup script
export SECRET_KEY=$(aws secretsmanager get-secret-value \
  --secret-id contravento/prod/secret-key \
  --query SecretString --output text)
```

---

## Generating Secrets

### Quick Reference

```bash
# 64-character SECRET_KEY (recommended)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"

# 32-character passwords
python -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(32))"

# All at once
python -c "
import secrets
print('# Generated secrets - ' + str(__import__('datetime').datetime.now()))
print('SECRET_KEY=' + secrets.token_urlsafe(64))
print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32))
print('REDIS_PASSWORD=' + secrets.token_urlsafe(32))
print('PGADMIN_PASSWORD=' + secrets.token_urlsafe(16))
"
```

**Copy output to your `.env.staging` or `.env.prod` file.**

---

## Common Pitfalls

### 1. Wrong DATABASE_URL Format

**❌ Wrong**:
```env
# Missing driver
DATABASE_URL=postgresql://user:pass@host:5432/db

# Wrong driver (sync instead of async)
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db

# Wrong hostname (db vs localhost)
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/db  # From host machine
```

**✅ Correct**:
```env
# SQLite (local-dev)
DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db

# PostgreSQL (Docker internal)
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/contravento

# PostgreSQL (Host access to Docker)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/contravento

# PostgreSQL (Production with SSL)
DATABASE_URL=postgresql+asyncpg://user:pass@prod.db.com:5432/db?ssl=require
```

### 2. Frontend Variables Not Prefixed

**❌ Wrong**:
```env
# Will NOT be exposed to frontend
API_URL=http://localhost:8000
TURNSTILE_KEY=1x00000000000000000000AA
```

**✅ Correct**:
```env
# VITE_ prefix required for frontend access
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA
```

### 3. Using Development Values in Production

**❌ Wrong**:
```env
# .env.prod (INSECURE!)
SECRET_KEY=dev-secret-key-min-32-characters-change-in-production
POSTGRES_PASSWORD=changeme
BCRYPT_ROUNDS=4
DEBUG=true
CORS_ORIGINS=*
```

**✅ Correct**:
```env
# .env.prod (SECURE)
SECRET_KEY=<GENERATED_64_CHAR_SECRET_UNIQUE_TO_PROD>
POSTGRES_PASSWORD=<GENERATED_32_CHAR_PASSWORD>
BCRYPT_ROUNDS=14
DEBUG=false
CORS_ORIGINS=https://contravento.com
```

### 4. Forgetting to Create .env Files

**Symptom**: Docker Compose fails with "variable not found"

**Solution**:
```bash
# Always create from template
cp .env.staging.example .env.staging
# Then edit with your values

# Or use deployment scripts (they check for you)
./deploy.sh staging
```

### 5. Wrong File Priority

**❌ Wrong**:
```bash
# Expecting docker-compose to read .env.staging
docker-compose up
# But it only reads .env by default!
```

**✅ Correct**:
```bash
# Explicitly specify file
docker-compose --env-file .env.staging up
# Or use deployment scripts
./deploy.sh staging  # Handles --env-file automatically
```

---

## See Also

- **[Getting Started](getting-started.md)** - Initial setup and first .env creation
- **[Troubleshooting](troubleshooting.md)** - Common environment variable errors
- **[Docker Compose Guide](docker-compose-guide.md)** - How variables flow to containers
- **[Deployment Modes](../README.md)** - Which variables for which mode

---

**Last Updated**: 2026-02-06

**Source**: Migrated from `backend/docs/ENVIRONMENTS.md` (Spanish → English)

**Feedback**: Found incorrect default values? [Open an issue](https://github.com/your-org/contravento-application-python/issues)
