# Local Full (Complete Stack) Deployment Mode

**Perfect for**: Email/auth features, full-stack integration testing

**Command**: `./deploy.sh local` (Linux/Mac) or `.\deploy.ps1 local` (Windows)

**Startup Time**: ~20-30 seconds

**Docker Required**: ✅ Yes

---

## Overview

The **local-full** mode provides a **complete development stack** with all services enabled: PostgreSQL, Redis, MailHog (email testing UI), pgAdmin (database UI), and optional frontend. This is the most comprehensive local environment, ideal for testing auth flows, email features, and full integration scenarios.

### When to Use This Mode

✅ **Perfect for**:
- Developing registration/login/password reset flows
- Testing email templates and content
- Implementing Redis caching or sessions
- Full-stack integration testing
- Need visual database inspection (pgAdmin)
- Testing features that require all services

❌ **NOT suitable for**:
- If you don't have Docker installed → Use [local-dev](local-dev.md) instead
- Quick daily development → Use [local-dev](local-dev.md) or [local-minimal](local-minimal.md) (faster)
- If you don't need email/cache → Use [local-minimal](local-minimal.md) (lighter)
- Production-like testing → Use [staging](staging.md) or [prod](prod.md)

### What's Included

| Component | Version | Status | Access |
|-----------|---------|--------|--------|
| **Backend** | FastAPI | ✅ Enabled | http://localhost:8000 |
| **Database** | PostgreSQL 16 | ✅ Enabled | localhost:5432 |
| **Cache** | Redis 7 | ✅ Enabled | localhost:6379 |
| **Email Testing** | MailHog | ✅ Enabled | http://localhost:8025 |
| **Database UI** | pgAdmin 4 | ✅ Enabled | http://localhost:5050 |
| **Frontend** | Vite (optional) | ⚠️ Optional | http://localhost:5173 (with --with-frontend) |

### Key Features

- 📧 **MailHog UI** - Visual email testing (no real SMTP needed)
- 🖥️ **pgAdmin** - Web-based PostgreSQL management
- 💾 **Redis** - Caching and session storage
- 🐘 **PostgreSQL** - Production-grade database
- 🔄 **Hot reload** - Backend and frontend auto-reload
- ✅ **Auto-seeding** - Test users and data created automatically
- 📦 **Complete stack** - All dependencies for full integration testing

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
| **RAM** | 4 GB | 8 GB |
| **Disk Space** | 3 GB | 6 GB |
| **CPU** | 2 cores | 4 cores |
| **OS** | Windows 10, macOS 11, Ubuntu 20.04 | Latest versions |

**Note**: local-full uses ~1.5 GB RAM (vs. ~500 MB for local-minimal) due to Redis, MailHog, and pgAdmin.

### Network Requirements

- **Ports**: 8000 (backend), 5432 (PostgreSQL), 6379 (Redis), 8025 (MailHog), 5050 (pgAdmin), 5173 (frontend - optional)
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
cp .env.local.example .env.local
```

**Windows PowerShell**:
```powershell
Copy-Item .env.local.example .env.local
```

**Step 3**: Configure `.env.local`

Open `.env.local` and set:

```bash
# Generate a strong SECRET_KEY (required)
SECRET_KEY=<paste generated key>
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"

# PostgreSQL credentials
POSTGRES_USER=contravento
POSTGRES_PASSWORD=<your secure password>
POSTGRES_DB=contravento_local

# Redis credentials
REDIS_PASSWORD=<your secure password>

# pgAdmin credentials
PGADMIN_EMAIL=admin@contravento.com
PGADMIN_PASSWORD=<your secure password>
```

**Step 4**: Start the environment

**Linux/Mac**:
```bash
./deploy.sh local
```

**Windows PowerShell**:
```powershell
.\deploy.ps1 local
```

**First run takes longer** (~3-5 minutes):
- Pulls Docker images (postgres, redis, mailhog, pgadmin)
- Creates volumes
- Runs database migrations
- Seeds test data

**Subsequent runs** (~20-30 seconds):
- Uses cached images and existing volumes

**Step 5**: Verify it works

Open your browser and check all services:
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MailHog UI**: http://localhost:8025
- **pgAdmin**: http://localhost:5050
- **Health Check**: http://localhost:8000/health

**Check logs**:
```bash
./deploy.sh local logs
```

Press `Ctrl+C` to exit logs.

---

## Configuration

### Environment Variables (.env.local)

**Required variables**:

```bash
# Security
SECRET_KEY=your-64-char-random-string  # Generate with python secrets module
BCRYPT_ROUNDS=4                         # Fast hashing for development

# PostgreSQL Connection
POSTGRES_USER=contravento
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=contravento_local
POSTGRES_HOST=postgres  # Container name
POSTGRES_PORT=5432

# Redis Connection
REDIS_HOST=redis  # Container name
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-password

# Database URL (auto-constructed)
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# JWT Tokens
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email (MailHog SMTP)
SMTP_HOST=mailhog  # Container name
SMTP_PORT=1025     # MailHog SMTP port
SMTP_USER=         # Not needed for MailHog
SMTP_PASSWORD=     # Not needed for MailHog
SMTP_FROM=noreply@contravento.com
SMTP_TLS=false     # MailHog doesn't use TLS

# File Uploads
UPLOAD_MAX_SIZE_MB=10
STORAGE_PATH=./storage

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# pgAdmin
PGADMIN_EMAIL=admin@contravento.com
PGADMIN_PASSWORD=your-secure-password

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
./deploy.sh local

# Windows
.\deploy.ps1 local
```

**Backend + Frontend** (with Vite dev server):
```bash
# Linux/Mac
./deploy.sh local --with-frontend

# Windows
.\deploy.ps1 local -WithFrontend
```

#### View Logs

```bash
# All services
./deploy.sh local logs

# Specific service
./deploy.sh local logs backend
./deploy.sh local logs postgres
./deploy.sh local logs mailhog

# Follow logs (live)
./deploy.sh local logs -f
```

#### Stop Services

```bash
./deploy.sh local down
```

**Note**: Database and Redis data persist (stored in Docker volumes). Starting again will reuse the same data.

#### Restart Services

```bash
# Restart all
./deploy.sh local restart

# Restart specific service
./deploy.sh local restart backend
./deploy.sh local restart mailhog
```

#### Full Clean (Delete Data)

```bash
# Stop and remove volumes (⚠️ deletes database and Redis data)
./deploy.sh local down -v
```

---

### Testing Email Features with MailHog

MailHog is a **fake SMTP server** that captures all emails sent by the application. Perfect for testing registration, password reset, and notification features.

#### How MailHog Works

```
Backend sends email → MailHog SMTP (port 1025) → Captured and stored
                                                          ↓
                                                  View in UI (port 8025)
```

#### Testing Email Flow

**Step 1**: Start local-full
```bash
./deploy.sh local
```

**Step 2**: Register a new user (triggers verification email)

**Via API**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "SecurePass123!"
  }'
```

**Via Frontend** (with --with-frontend):
1. Open http://localhost:5173
2. Click "Register"
3. Fill form and submit

**Step 3**: Check email in MailHog UI
1. Open http://localhost:8025
2. You'll see the verification email
3. Click the email to view content
4. Copy the verification token from the email body

**Step 4**: Verify the email using the token

```bash
curl -X POST http://localhost:8000/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "token": "TOKEN_FROM_EMAIL"
  }'
```

#### MailHog Features

| Feature | Description | Access |
|---------|-------------|--------|
| **Web UI** | View all emails in browser | http://localhost:8025 |
| **Search** | Filter emails by recipient, subject | Web UI search bar |
| **HTML Preview** | View HTML email rendering | Click email in list |
| **Raw View** | See email source (headers, MIME) | Click "Source" tab |
| **Delete** | Clear email inbox | Click "Delete all messages" |

#### Common Email Testing Scenarios

**1. Registration Email Verification**:
- User registers → Email with verification link sent → MailHog captures → User clicks link → Account verified

**2. Password Reset**:
- User requests reset → Email with reset token sent → MailHog captures → User uses token → Password changed

**3. Email Template Testing**:
- Check HTML rendering
- Verify text/plain fallback
- Test different email clients (via MailHog preview)

---

### Using pgAdmin (Database UI)

pgAdmin provides a **web-based interface** for PostgreSQL management.

#### Accessing pgAdmin

1. Open http://localhost:5050
2. Login with credentials from `.env.local`:
   - **Email**: `${PGADMIN_EMAIL}` (e.g., admin@contravento.com)
   - **Password**: `${PGADMIN_PASSWORD}`

#### First-Time Setup: Add Server

**Step 1**: Click "Add New Server"

**Step 2**: Configure connection

**General tab**:
- **Name**: ContraVento Local

**Connection tab**:
- **Host name/address**: `postgres` (Docker container name)
- **Port**: `5432`
- **Maintenance database**: `contravento_local`
- **Username**: `${POSTGRES_USER}` (from `.env.local`)
- **Password**: `${POSTGRES_PASSWORD}` (from `.env.local`)
- **Save password**: ✅ Yes

**Step 3**: Click "Save"

#### Common pgAdmin Tasks

**View tables**:
1. Expand "Servers" → "ContraVento Local" → "Databases" → "contravento_local" → "Schemas" → "public" → "Tables"

**Query data**:
1. Right-click table → "View/Edit Data" → "All Rows"
2. Or use Query Tool (Tools → Query Tool):
   ```sql
   SELECT * FROM users;
   SELECT * FROM trips WHERE status = 'PUBLISHED';
   ```

**Export data**:
1. Right-click table → "Export"
2. Select format (CSV, JSON, etc.)

**View table structure**:
1. Right-click table → "Properties"
2. Go to "Columns" tab

---

### Using Redis (Cache/Sessions)

Redis is available for caching and session storage.

#### Connect to Redis

**Via redis-cli** (inside container):
```bash
docker exec -it contravento-redis-local redis-cli -a ${REDIS_PASSWORD}
```

**Basic commands**:
```bash
# Check connection
PING  # Should return PONG

# View all keys
KEYS *

# Get a key value
GET user:123:profile

# Set a key
SET test:key "Hello Redis"

# Delete a key
DEL test:key

# Flush all data (⚠️ clears cache)
FLUSHALL

# Exit redis-cli
EXIT
```

#### Redis Use Cases

**1. Session Storage**:
```python
# Store user session
await redis.setex(f"session:{token}", 3600, user_id)

# Retrieve session
user_id = await redis.get(f"session:{token}")
```

**2. Cache API Responses**:
```python
# Cache trip list
await redis.setex("trips:public:page1", 300, json.dumps(trips))

# Retrieve from cache
cached = await redis.get("trips:public:page1")
```

**3. Rate Limiting**:
```python
# Track login attempts
attempts = await redis.incr(f"login:attempts:{ip}")
await redis.expire(f"login:attempts:{ip}", 900)  # 15 min
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
│   contravento-backend-local                     │
│   • FastAPI + uvicorn --reload                  │
│   • Port 8000 → host:8000                       │
│   • Volume mount: ./backend/src (read-only)     │
└─────────────────────────────────────────────────┘
         ↓ asyncpg              ↓ aioredis         ↓ smtplib
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   PostgreSQL     │  │   Redis          │  │   MailHog        │
│   Port 5432      │  │   Port 6379      │  │   SMTP: 1025     │
│   Volume: pgdata │  │   Volume: redis  │  │   UI: 8025       │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────┐
│   pgAdmin Container                             │
│   Port 5050                                     │
│   • Connects to PostgreSQL container           │
│   • Web UI for database management             │
└─────────────────────────────────────────────────┘
```

### Docker Compose Files

This mode uses **multi-file composition**:

1. **docker-compose.yml** (base configuration)
2. **docker-compose.local.yml** (overrides for local-full mode)

**Start command expands to**:
```bash
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.local.yml \
  --env-file .env.local \
  up -d
```

### Network

All containers run in **contravento-network** (bridge network):
- Backend can reach PostgreSQL via hostname `postgres`
- Backend can reach Redis via hostname `redis`
- Backend can reach MailHog via hostname `mailhog`
- pgAdmin can reach PostgreSQL via hostname `postgres`
- Host can reach all services via `localhost:<port>`

### Volumes

**Persistent data**:
- `postgres_data_local` - PostgreSQL data directory
- `redis_data_local` - Redis persistence (if enabled)
- `pgadmin_data_local` - pgAdmin settings and server configs

**Bind mounts**:
- `./backend/src:/app/src:ro` - Source code (read-only, for hot reload)
- `./backend/storage:/app/storage` - Uploaded files (read-write)

---

## Troubleshooting

### Service Access Issues

#### Cannot access MailHog UI (http://localhost:8025)

**Cause**: MailHog container not running or port conflict

**Fix - Check container status**:
```bash
docker ps | grep mailhog
```

Should show `0.0.0.0:8025->8025/tcp`

**If not running**:
```bash
./deploy.sh local logs mailhog  # Check error logs
./deploy.sh local restart mailhog
```

**If port conflict**:
Edit `docker-compose.local.yml` and change host port:
```yaml
mailhog:
  ports:
    - "8026:8025"  # Change to 8026
```

---

#### Cannot access pgAdmin (http://localhost:5050)

**Cause**: pgAdmin container not running or login credentials wrong

**Fix - Check container**:
```bash
docker ps | grep pgadmin
```

**If not running**:
```bash
./deploy.sh local logs pgadmin
./deploy.sh local restart pgadmin
```

**If login fails**:
1. Verify credentials in `.env.local` match login attempt
2. Reset pgAdmin data:
   ```bash
   ./deploy.sh local down -v  # Delete volumes
   ./deploy.sh local          # Recreate
   ```

---

#### Cannot connect to PostgreSQL from pgAdmin

**Cause**: Wrong host name or credentials

**Fix - Verify connection settings**:
- **Host**: Must be `postgres` (not `localhost`)
- **Port**: `5432`
- **Username/Password**: Match `.env.local`

**Test connectivity from backend**:
```bash
docker exec -it contravento-backend-local poetry run alembic current
```

If this works, PostgreSQL is running fine.

---

### Email Testing Issues

#### Emails not appearing in MailHog

**Cause**: Backend not configured to use MailHog SMTP

**Fix - Verify `.env.local` SMTP settings**:
```bash
SMTP_HOST=mailhog  # Must be "mailhog" (not "localhost")
SMTP_PORT=1025      # Must be 1025 (not 587 or 25)
SMTP_TLS=false      # MailHog doesn't use TLS
```

**Restart backend**:
```bash
./deploy.sh local restart backend
```

**Test email sending**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@test.com", "password": "TestPass123!"}'
```

Check MailHog UI (http://localhost:8025) for email.

---

#### MailHog shows "connection refused"

**Cause**: MailHog container not in same Docker network

**Fix - Check network**:
```bash
docker network inspect contravento-network
```

Should show both `backend` and `mailhog` containers.

**Recreate network**:
```bash
./deploy.sh local down
./deploy.sh local
```

---

### Redis Issues

#### Error: "Redis connection refused"

**Cause**: Redis container not running or wrong host/port

**Fix - Check Redis container**:
```bash
docker ps | grep redis
```

**Test connection**:
```bash
docker exec -it contravento-redis-local redis-cli -a ${REDIS_PASSWORD} PING
```

Should return `PONG`.

**If fails, check `.env.local`**:
```bash
REDIS_HOST=redis  # Must be "redis" (not "localhost")
REDIS_PORT=6379
```

---

#### Error: "NOAUTH Authentication required"

**Cause**: Redis password mismatch

**Fix - Verify password**:
1. Check `.env.local` has `REDIS_PASSWORD` set
2. Restart Redis:
   ```bash
   ./deploy.sh local restart redis
   ```

---

### Performance Issues

#### Slow startup (>60 seconds)

**Cause**: Docker pulling images or resource limits

**Fix**:
- **First run**: Normal - pulling postgres, redis, mailhog, pgadmin (~2-3 minutes)
- **Subsequent runs**: Should be ~20-30 seconds
- **If always slow**: Increase Docker Desktop resources (Settings → Resources → Memory to 4+ GB)

---

#### High RAM usage (>2 GB)

**Cause**: Multiple services running

**Expected RAM usage**:
- PostgreSQL: ~100-200 MB
- Redis: ~50-100 MB
- Backend: ~200-300 MB
- MailHog: ~20-50 MB
- pgAdmin: ~100-200 MB
- **Total**: ~500 MB to 1.5 GB (normal)

**If exceeding 2 GB**:
- Check for memory leaks in backend code
- Reduce Docker Desktop memory limit if other apps need RAM
- Use [local-minimal](local-minimal.md) instead (no Redis/MailHog/pgAdmin)

---

## Related Modes

### Progression Path

```
local-dev (SQLite)
    ↓
local-minimal (Docker + PostgreSQL)
    ↓
local-full (Complete Stack)  ← You are here
    ↓
When deploying to server:
    → dev (Integration server)
    → staging (Pre-production)
    → prod (Live production)
```

### When to Upgrade

**From local-full to [dev](dev.md)**:
- Setting up shared development server
- Testing Nginx reverse proxy
- Real SMTP email sending (not MailHog)

**From local-full to [staging](staging.md)**:
- Final QA testing before production
- Testing SSL/TLS certificates
- Production-grade monitoring (Sentry)

### Quick Comparison

| Feature | local-dev | local-minimal | local-full | dev |
|---------|-----------|---------------|------------|-----|
| **Docker** | ❌ | ✅ | ✅ | ✅ |
| **Database** | SQLite | PostgreSQL | PostgreSQL | PostgreSQL |
| **Startup** | Instant | ~10s | ~20-30s | ~20s |
| **RAM Usage** | ~200 MB | ~500 MB | ~1.5 GB | ~1 GB |
| **MailHog** | ❌ | ❌ | ✅ | ❌ |
| **Redis** | ❌ | ❌ | ✅ | ✅ |
| **pgAdmin** | ❌ | Optional | ✅ | ❌ |
| **Nginx** | ❌ | ❌ | ❌ | ✅ |
| **Best for** | Daily dev | PostgreSQL testing | Email/cache testing | Integration server |

---

## Additional Resources

- **[Getting Started Guide](../guides/getting-started.md)** - General deployment introduction
- **[Environment Variables Guide](../guides/environment-variables.md)** - Complete .env reference
- **[Database Management Guide](../guides/database-management.md)** - PostgreSQL tips, backups
- **[Docker Compose Guide](../guides/docker-compose-guide.md)** - Multi-file composition explained
- **[Troubleshooting Guide](../guides/troubleshooting.md)** - Cross-mode common issues
- **[Deployment Index](../README.md)** - All deployment modes

---

**Need more help?** Check the [Troubleshooting Guide](../guides/troubleshooting.md) or open an issue on GitHub.

**Last Updated**: 2026-01-25
