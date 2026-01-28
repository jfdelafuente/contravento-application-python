# Local Minimal (Docker + PostgreSQL) Deployment Mode

**Perfect for**: Testing PostgreSQL-specific features without extra services

**Command**: `./deploy.sh local-minimal` (Linux/Mac) or `.\deploy.ps1 local-minimal` (Windows)

**Startup Time**: ~10 seconds

**Docker Required**: ✅ Yes

---

## Overview

The **local-minimal** mode provides a **lightweight Docker environment** with PostgreSQL and the backend, without the overhead of Redis, MailHog, or pgAdmin. It's the perfect middle ground between [local-dev](local-dev.md) (SQLite) and [local-full](local-full.md) (complete stack).

### When to Use This Mode

✅ **Perfect for**:
- Testing PostgreSQL-specific features (array columns, native UUIDs, JSONB)
- Validating database migrations before deployment
- PostgreSQL performance testing
- Production database parity testing
- Daily development when you need PostgreSQL but not email/cache

❌ **NOT suitable for**:
- If you don't have Docker installed → Use [local-dev](local-dev.md) instead
- Testing email flows → Use [local-full](local-full.md) with MailHog
- Redis caching/session testing → Use [local-full](local-full.md)
- Full integration testing → Use [dev](dev.md) or [staging](staging.md)

### What's Included

| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| **Backend** | FastAPI | ✅ Enabled | Hot reload enabled |
| **Database** | PostgreSQL 16 | ✅ Enabled | Persistent volume |
| **Frontend** | Vite (optional) | ⚠️ Optional | Use `--with-frontend` flag |
| **Redis** | - | ❌ Disabled | Not included (use local-full) |
| **MailHog** | - | ❌ Disabled | Emails logged to console |
| **pgAdmin** | - | ⚠️ Available | Disabled by default (see below) |

### Key Features

- 🐘 **Real PostgreSQL** - Same database as production/staging
- ⚡ **Lightweight** - ~500 MB RAM (vs. ~1.5 GB for local-full)
- 🔄 **Fast startup** - ~10 seconds (vs. ~30 seconds for local-full)
- ✅ **Auto-seeding** - Test users and data created automatically
- 🔧 **Hot reload** - Backend restarts on code changes
- 💾 **Persistent data** - Database survives container restarts

---

## Prerequisites

### Required Software

**Docker Desktop 24.0+**:
```bash
docker --version    # Must show 24.0 or higher
docker-compose --version  # Must show 2.0 or higher
```

**Download**: https://www.docker.com/products/docker-desktop/

### Optional (for frontend)

**Node.js 18+** (only with `--with-frontend` flag):
```bash
node --version  # Must show v18.x or higher
npm --version   # Must show 9.x or higher
```

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 2 GB | 4 GB |
| **Disk Space** | 2 GB | 5 GB |
| **CPU** | 2 cores | 4 cores |
| **OS** | Windows 10, macOS 11, Ubuntu 20.04 | Latest versions |

### Network Requirements

- **Ports**: 8000 (backend), 5432 (PostgreSQL), 5173 (frontend - optional)
- **Internet**: Required for initial Docker image pull

---

## Quick Start

### First-Time Setup

**Step 1**: Verify Docker is running
```bash
docker ps  # Should show empty list or running containers
```

**Step 2**: Create environment file

**Linux/Mac**:
```bash
cp .env.local-minimal.example .env.local-minimal
```

**Windows PowerShell**:
```powershell
Copy-Item .env.local-minimal.example .env.local-minimal
```

**Step 3**: Configure `.env.local-minimal`

Open `.env.local-minimal` and set:

```bash
# Generate a strong SECRET_KEY (required)
SECRET_KEY=<paste generated key>
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"

# PostgreSQL credentials
POSTGRES_USER=contravento
POSTGRES_PASSWORD=<your secure password>
POSTGRES_DB=contravento_local
```

**Step 4**: Start the environment

**Linux/Mac**:
```bash
./deploy.sh local-minimal
```

**Windows PowerShell**:
```powershell
.\deploy.ps1 local-minimal
```

**First run takes longer** (~2-3 minutes):
- Pulls Docker images (postgres:16-alpine, backend)
- Creates volumes
- Runs database migrations
- Seeds test data

**Subsequent runs** (~10 seconds):
- Uses cached images and existing volumes

**Step 5**: Verify it works

Open your browser:
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

**Check logs**:
```bash
./deploy.sh local-minimal logs
```

Press `Ctrl+C` to exit logs.

---

## Configuration

### Environment Variables (.env.local-minimal)

**Required variables**:

```bash
# Security
SECRET_KEY=your-64-char-random-string  # Generate with python secrets module
BCRYPT_ROUNDS=4                         # Fast hashing for development

# PostgreSQL Connection
POSTGRES_USER=contravento
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=contravento_local
POSTGRES_HOST=postgres  # Container name (do not change)
POSTGRES_PORT=5432

# Database URL (auto-constructed from above)
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# JWT Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email (Console mode - no SMTP server needed)
SMTP_HOST=smtp.gmail.com  # Not used (emails logged to console)
SMTP_PORT=587
SMTP_USER=dummy@example.com
SMTP_PASSWORD=dummy
SMTP_FROM=noreply@contravento.com
SMTP_TLS=true

# File Uploads
UPLOAD_MAX_SIZE_MB=10
STORAGE_PATH=./storage

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### Frontend Configuration (with --with-frontend)

If using `--with-frontend` flag, the script uses `frontend/.env.development`:

```bash
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA  # Test key
VITE_ENV=development
VITE_DEBUG=true
```

### Test Users (Auto-Created)

| Username | Email | Password | Role |
|----------|-------|----------|------|
| **testuser** | test@example.com | TestPass123! | USER |
| **maria_garcia** | maria@example.com | SecurePass456! | USER |

### Seeded Data

**Achievements** (9 pre-configured):
- Primera Ruta, Explorador, Buen Compañero, etc.

**Cycling Types** (8 pre-configured):
- Road, MTB, Gravel, Bikepacking, etc.

---

## Usage

### Basic Commands

#### Start Services

**Backend only** (default):
```bash
# Linux/Mac
./deploy.sh local-minimal

# Windows
.\deploy.ps1 local-minimal
```

**Backend + Frontend** (with Vite dev server):
```bash
# Linux/Mac
./deploy.sh local-minimal --with-frontend

# Windows
.\deploy.ps1 local-minimal -WithFrontend
```

#### View Logs

```bash
# All services
./deploy.sh local-minimal logs

# Specific service
./deploy.sh local-minimal logs backend
./deploy.sh local-minimal logs postgres

# Follow logs (live)
./deploy.sh local-minimal logs -f
```

#### Stop Services

```bash
./deploy.sh local-minimal down
```

**Note**: Database data persists (stored in Docker volume). Starting again will reuse the same data.

#### Restart Services

```bash
# Restart all
./deploy.sh local-minimal restart

# Restart specific service
docker-compose -f docker-compose.yml -f docker-compose.local-minimal.yml --env-file .env.local-minimal restart backend
```

#### Full Clean (Delete Data)

```bash
# Stop and remove volumes (⚠️ deletes database)
./deploy.sh local-minimal down -v
```

---

### Daily Workflows

#### Workflow 1: Backend Development

**Use when**: Working on APIs, business logic, database models

**Command**:
```bash
./deploy.sh local-minimal
```

**What starts**:
- PostgreSQL container
- Backend container with hot reload

**Development flow**:
1. Edit files in `backend/src/`
2. Save the file
3. Backend container auto-restarts (~5 seconds)
4. Test at http://localhost:8000/docs

**Logs**:
```bash
./deploy.sh local-minimal logs backend -f
```

**Stop**: `./deploy.sh local-minimal down`

---

#### Workflow 2: Full-Stack Development

**Use when**: Building features that need frontend + backend

**Command**:
```bash
./deploy.sh local-minimal --with-frontend
```

**What starts**:
- PostgreSQL container
- Backend container with hot reload
- Frontend Vite dev server (port 5173) with HMR

**Development flow**:
1. Open browser at http://localhost:5173
2. Edit code:
   - **Frontend** (`frontend/src/*.tsx`): Saves → HMR updates in <2s
   - **Backend** (`backend/src/*.py`): Saves → Container restarts in ~5s
3. Test end-to-end at http://localhost:5173

**Stop**: `./deploy.sh local-minimal down`

---

#### Workflow 3: Database Testing

**Use when**: Testing migrations, PostgreSQL-specific queries

**Connect to PostgreSQL**:
```bash
# Using psql (if installed locally)
psql -h localhost -U contravento -d contravento_local

# Using Docker exec
docker exec -it contravento-postgres-local-minimal psql -U contravento -d contravento_local
```

**Run migrations**:
```bash
# From host (if Poetry installed)
cd backend
poetry run alembic upgrade head

# Or exec into backend container
docker exec -it contravento-backend-local-minimal poetry run alembic upgrade head
```

**Inspect database**:
```sql
-- List tables
\dt

-- Describe users table
\d users

-- Query data
SELECT * FROM users;

-- Exit psql
\q
```

---

### Advanced Operations

#### Enable pgAdmin (Optional)

pgAdmin is available but disabled by default to keep the environment lightweight.

**To enable**:

1. Edit `docker-compose.local-minimal.yml`
2. Find the `pgadmin` service (around line 86)
3. Change from:
   ```yaml
   pgadmin:
     deploy:
       replicas: 0
   ```

   To:
   ```yaml
   pgadmin:
     deploy:
       replicas: 1
     ports:
       - "5050:80"
   ```

4. Restart:
   ```bash
   ./deploy.sh local-minimal restart
   ```

5. Access pgAdmin at http://localhost:5050
   - **Email**: `admin@contravento.com`
   - **Password**: `${PGADMIN_DEFAULT_PASSWORD}` (from `.env.local-minimal`)

6. Add server in pgAdmin:
   - **Host**: `postgres` (container name)
   - **Port**: `5432`
   - **Username**: `${POSTGRES_USER}`
   - **Password**: `${POSTGRES_PASSWORD}`
   - **Database**: `${POSTGRES_DB}`

---

#### Reset Database (Delete All Data)

**Option 1 - Full reset** (delete volume):
```bash
./deploy.sh local-minimal down -v
./deploy.sh local-minimal
```

**Option 2 - Drop database** (keep volume):
```bash
# Connect to PostgreSQL
docker exec -it contravento-postgres-local-minimal psql -U contravento

# Drop and recreate database
DROP DATABASE contravento_local;
CREATE DATABASE contravento_local;
\q

# Restart backend (runs migrations)
./deploy.sh local-minimal restart backend
```

---

#### Backup Database

```bash
# Create backup
docker exec -t contravento-postgres-local-minimal pg_dump -U contravento contravento_local > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20260125.sql | docker exec -i contravento-postgres-local-minimal psql -U contravento -d contravento_local
```

---

## Architecture

### Container Stack

```
┌─────────────────────────────────────────────────┐
│   Frontend (Optional - with --with-frontend)   │
│   Vite Dev Server - Port 5173                  │
│   • Running on host (not in Docker)            │
│   • Proxies /api/* → http://localhost:8000     │
└─────────────────────────────────────────────────┘
                    ↓ HTTP
┌─────────────────────────────────────────────────┐
│   Backend Container                             │
│   contravento-backend-local-minimal             │
│   • FastAPI + uvicorn --reload                  │
│   • Port 8000 → host:8000                       │
│   • Volume mount: ./backend/src (read-only)     │
└─────────────────────────────────────────────────┘
                    ↓ asyncpg
┌─────────────────────────────────────────────────┐
│   PostgreSQL Container                          │
│   contravento-postgres-local-minimal            │
│   • PostgreSQL 16 Alpine                        │
│   • Port 5432 → host:5432                       │
│   • Volume: postgres_data_local_minimal         │
└─────────────────────────────────────────────────┘
```

### Docker Compose Files

This mode uses **multi-file composition**:

1. **docker-compose.yml** (base configuration)
2. **docker-compose.local-minimal.yml** (overrides for local-minimal mode)

**Start command expands to**:
```bash
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.local-minimal.yml \
  --env-file .env.local-minimal \
  up -d
```

### Network

All containers run in **contravento-network** (bridge network):
- Backend can reach PostgreSQL via hostname `postgres`
- Host can reach backend via `localhost:8000`
- Host can reach PostgreSQL via `localhost:5432`

### Volumes

**Persistent data**:
- `postgres_data_local_minimal` - PostgreSQL data directory (survives container restarts)

**Bind mounts**:
- `./backend/src:/app/src:ro` - Source code (read-only, for hot reload)
- `./backend/storage:/app/storage` - Uploaded files (read-write)

---

## Troubleshooting

### Docker Issues

#### Error: "Cannot connect to Docker daemon"

**Cause**: Docker Desktop is not running

**Fix**:
1. Start Docker Desktop
2. Wait for it to fully start (whale icon in system tray)
3. Verify: `docker ps`

---

#### Error: "Port 5432 is already in use"

**Cause**: Local PostgreSQL is running on port 5432

**Fix - Option 1** (stop local PostgreSQL):
```bash
# Linux
sudo systemctl stop postgresql

# macOS (Homebrew)
brew services stop postgresql

# Windows
# Stop PostgreSQL service via Services app (services.msc)
```

**Fix - Option 2** (change Docker port):
Edit `docker-compose.local-minimal.yml`:
```yaml
postgres:
  ports:
    - "5433:5432"  # Change host port to 5433
```

Update `.env.local-minimal`:
```bash
POSTGRES_PORT=5433  # Match new port
```

---

#### Error: "Port 8000 is already in use"

**Cause**: Another backend instance (local-dev, local-full) is running

**Fix**:
```bash
# Stop other instances
./run-local-dev.sh  # Press Ctrl+C if running
./deploy.sh local down  # If local-full is running

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
```

---

### Database Issues

#### Error: "FATAL: password authentication failed"

**Cause**: `.env.local-minimal` has wrong password or PostgreSQL hasn't restarted

**Fix**:
1. Verify `.env.local-minimal` has correct `POSTGRES_PASSWORD`
2. Recreate containers:
   ```bash
   ./deploy.sh local-minimal down -v
   ./deploy.sh local-minimal
   ```

---

#### Error: "Database contravento_local does not exist"

**Cause**: Initial setup didn't complete or database was manually deleted

**Fix**:
```bash
# Recreate database
docker exec -it contravento-postgres-local-minimal psql -U contravento -c "CREATE DATABASE contravento_local;"

# Run migrations
docker exec -it contravento-backend-local-minimal poetry run alembic upgrade head
```

---

#### Migrations fail: "Target database is not up to date"

**Cause**: Database schema out of sync with migrations

**Fix**:
```bash
# Check current migration
docker exec -it contravento-backend-local-minimal poetry run alembic current

# View migration history
docker exec -it contravento-backend-local-minimal poetry run alembic history

# Apply all pending migrations
docker exec -it contravento-backend-local-minimal poetry run alembic upgrade head
```

---

### Container Issues

#### Backend container keeps restarting

**Cause**: Application crash or dependency issue

**Fix - Check logs**:
```bash
./deploy.sh local-minimal logs backend
```

Common causes:
- **Missing SECRET_KEY**: Set in `.env.local-minimal`
- **Database connection failed**: Check PostgreSQL is running
- **Import error**: Rebuild image (`docker-compose build backend`)

**Rebuild backend image**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.local-minimal.yml build backend
./deploy.sh local-minimal restart backend
```

---

#### Cannot access http://localhost:8000

**Cause**: Container not exposing port or not running

**Fix - Check container status**:
```bash
docker ps | grep contravento
```

Should show `0.0.0.0:8000->8000/tcp`

If container not running:
```bash
./deploy.sh local-minimal logs backend  # Check why it failed
./deploy.sh local-minimal restart backend
```

---

### Performance Issues

#### Slow startup (>30 seconds)

**Cause**: Docker pulling images or heavy migrations

**Fix**:
- **First run**: Normal - Docker pulls postgres:16-alpine (~50 MB) and builds backend image
- **Subsequent runs**: Should be ~10 seconds
- **If always slow**: Check Docker Desktop resource limits (Settings → Resources)

---

#### Backend hot reload slow (>10 seconds)

**Cause**: Large codebase or Docker volume performance

**Fix - macOS/Windows** (known Docker volume issue):
```yaml
# Edit docker-compose.local-minimal.yml
# Change from:
- ./backend/src:/app/src:ro

# To (cached mode):
- ./backend/src:/app/src:cached
```

---

## Related Modes

### Progression Path

```
local-dev (SQLite)
    ↓
local-minimal (Docker + PostgreSQL)  ← You are here
    ↓
When you need email testing:
    → local-full (+ MailHog + pgAdmin + Redis)
    ↓
When deploying to server:
    → dev (Integration server)
    → staging (Pre-production)
    → prod (Live production)
```

### When to Upgrade

**From local-minimal to [local-full](local-full.md)**:
- Need email testing UI (MailHog)
- Implementing registration/password reset flows
- Testing Redis caching or sessions
- Need pgAdmin enabled by default

**From local-minimal to [dev](dev.md)**:
- Setting up shared development server
- Testing Nginx reverse proxy
- Real SMTP email sending

### Quick Comparison

| Feature | local-dev | local-minimal | local-full |
|---------|-----------|---------------|------------|
| **Docker** | ❌ | ✅ | ✅ |
| **Database** | SQLite | PostgreSQL | PostgreSQL |
| **Startup** | Instant | ~10s | ~20-30s |
| **RAM Usage** | ~200 MB | ~500 MB | ~1.5 GB |
| **MailHog** | ❌ | ❌ | ✅ |
| **Redis** | ❌ | ❌ | ✅ |
| **pgAdmin** | ❌ | Optional | ✅ |
| **Best for** | Daily dev | PostgreSQL testing | Email/cache testing |

---

## Additional Resources

- **[Getting Started Guide](../guides/getting-started.md)** - General deployment introduction
- **[Environment Variables Guide](../guides/environment-variables.md)** - Complete .env reference
- **[Database Management Guide](../guides/database-management.md)** - Migrations, backups, PostgreSQL tips
- **[Docker Compose Guide](../guides/docker-compose-guide.md)** - Multi-file composition explained
- **[Troubleshooting Guide](../guides/troubleshooting.md)** - Cross-mode common issues
- **[Deployment Index](../README.md)** - All deployment modes

---

**Need more help?** Check the [Troubleshooting Guide](../guides/troubleshooting.md) or open an issue on GitHub.

**Last Updated**: 2026-01-25
