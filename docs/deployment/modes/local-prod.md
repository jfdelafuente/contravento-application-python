# Local Prod (Production Build Testing) Deployment Mode

**Perfect for**: Testing production builds locally before deployment

**Command**: `./deploy-local-prod.sh` (Linux/Mac) or `.\deploy-local-prod.ps1` (Windows)

**Startup Time**: ~30 seconds

**Docker Required**: ✅ Yes

---

## Overview

The **local-prod** mode allows you to test the **production build of the frontend** (Nginx + optimized static assets) on your local machine, connected to a local backend. This is the closest you can get to production without actually deploying.

### When to Use This Mode

✅ **Perfect for**:
- Testing production frontend build (minified, optimized)
- Validating Nginx configuration (`/api/*` → backend proxy)
- Verifying static asset optimization (cache busting, gzip)
- Testing security headers (X-Frame-Options, CSP)
- Simulating staging/production behavior locally
- Pre-deployment validation

❌ **NOT suitable for**:
- Daily development → Use [local-dev](local-dev.md) (has hot reload)
- Frequent frontend changes → Requires rebuild every time (no HMR)
- Debugging React code → No source maps in production build
- If you need hot reload → Use [local-full](local-full.md) instead

### What's Included

| Component | Version | Status | Notes |
|-----------|---------|--------|-------|
| **Frontend** | Nginx + React build | ✅ Enabled | Production-optimized (Dockerfile.prod) |
| **Backend** | FastAPI | ✅ Enabled | **Development mode** (hot reload enabled) |
| **Database** | PostgreSQL 16 | ✅ Enabled | Persistent volume |
| **Redis** | Redis 7 | ✅ Enabled | For caching/sessions |
| **MailHog** | Email testing | ✅ Enabled | http://localhost:8025 |
| **pgAdmin** | Database UI | ✅ Enabled | http://localhost:5050 |

### Key Features

- 🚀 **Production frontend build** - Minified, tree-shaken, optimized
- 🌐 **Nginx reverse proxy** - `/api/*` requests proxied to backend
- 📦 **Static asset caching** - Immutable assets with 1-year cache
- 🔒 **Security headers** - X-Frame-Options, X-Content-Type-Options, CSP
- ⚠️ **NO hot reload** - Frontend requires rebuild after changes
- 🔧 **Backend in dev mode** - Backend still has hot reload for testing

---

## Prerequisites

### Required Software

**Docker Desktop 24.0+**:
```bash
docker --version    # Must show 24.0 or higher
docker-compose --version  # Must show 2.0 or higher
```

**Download**: https://www.docker.com/products/docker-desktop/

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 4 GB | 8 GB |
| **Disk Space** | 3 GB | 6 GB |
| **CPU** | 2 cores | 4 cores |
| **OS** | Windows 10, macOS 11, Ubuntu 20.04 | Latest versions |

### Network Requirements

- **Ports**: 8080 (Nginx frontend), 8000 (backend), 5432 (PostgreSQL), 6379 (Redis), 8025 (MailHog), 5050 (pgAdmin)
- **Internet**: Required for initial Docker image pull and npm dependencies

---

## Quick Start

### First-Time Setup

**Step 1**: Verify Docker is running
```bash
docker ps  # Should show empty list or running containers
```

**Step 2**: Ensure `.env.local` exists

If you've already set up [local-full](local-full.md), you can reuse `.env.local`. Otherwise:

**Linux/Mac**:
```bash
cp .env.local.example .env.local
```

**Windows PowerShell**:
```powershell
Copy-Item .env.local.example .env.local
```

Configure as described in [local-full Configuration](local-full.md#configuration).

**Step 3**: Start the environment

**Linux/Mac**:
```bash
./deploy-local-prod.sh start
```

**Windows PowerShell**:
```powershell
.\deploy-local-prod.ps1 start
```

**First run takes longer** (~3-5 minutes):
- Builds frontend with Dockerfile.prod (multi-stage build)
  - Stage 1: `npm ci` + `npm run build` (compiles React → optimized dist/)
  - Stage 2: Copies dist/ to Nginx container
- Pulls Docker images (postgres, redis, mailhog, pgadmin)
- Runs database migrations
- Seeds test data

**Subsequent runs** (~30 seconds):
- Uses cached Docker images
- Serves pre-built frontend from container

**Step 4**: Verify it works

Open your browser:
- **Frontend (Nginx)**: http://localhost:8080 ← **Note port 8080** (not 5173)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MailHog UI**: http://localhost:8025
- **pgAdmin**: http://localhost:5050

---

## Configuration

### Environment Variables

Uses the same `.env.local` as [local-full](local-full.md) mode.

**Key differences**:
- Frontend runs on **port 8080** (Nginx) instead of 5173 (Vite)
- Frontend uses production build (minified, no source maps)
- Nginx proxies `/api/*` to backend

### Frontend Build Configuration

The frontend is built using `frontend/Dockerfile.prod`:

**Multi-stage build**:

**Stage 1 - Builder**:
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci  # Clean install from package-lock.json
COPY . .
RUN npm run build  # Creates dist/ with optimized assets
```

**Stage 2 - Runtime**:
```dockerfile
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

**Nginx config** (`frontend/nginx.conf`) handles:

**1. Static asset serving**:
```nginx
location / {
    root /usr/share/nginx/html;
    try_files $uri /index.html;  # SPA fallback
}
```

**2. API reverse proxy**:
```nginx
location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

**3. Cache headers**:
```nginx
# Cache immutable assets (JS/CSS with hash) for 1 year
location ~* \.(js|css|png|jpg|jpeg|gif|ico|woff|woff2)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Never cache index.html (allows deployments to take effect)
location = /index.html {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

**4. Security headers**:
```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

---

## Usage

### Basic Commands

#### Start Environment

```bash
# Linux/Mac
./deploy-local-prod.sh start

# Windows
.\deploy-local-prod.ps1 start
```

**Default action** (if no command specified):
```bash
./deploy-local-prod.sh  # Same as "start"
```

#### Stop Environment

```bash
# Linux/Mac
./deploy-local-prod.sh stop

# Windows
.\deploy-local-prod.ps1 stop
```

#### Rebuild Frontend (After Code Changes)

**⚠️ Important**: Unlike [local-full](local-full.md) with hot reload, **you must rebuild** the frontend after any code changes.

```bash
# Linux/Mac
./deploy-local-prod.sh rebuild

# Windows
.\deploy-local-prod.ps1 rebuild
```

**What rebuild does**:
1. Rebuilds frontend image with `--no-cache` (fresh build)
2. Runs `npm run build` inside builder container
3. Creates new Nginx container with updated dist/
4. Restarts frontend container

**Estimated time**: 2-3 minutes

#### View Logs

```bash
# Linux/Mac
./deploy-local-prod.sh logs

# Windows
.\deploy-local-prod.ps1 logs
```

Press `Ctrl+C` to exit.

#### Clean Everything

```bash
# Linux/Mac
./deploy-local-prod.sh clean

# Windows
.\deploy-local-prod.ps1 clean
```

**Warning**: This deletes all containers and volumes (database data will be lost).

---

### Development Workflow

#### Workflow 1: Frontend Production Build Testing

**Use when**: Validating frontend build before deploying to staging/production

**Steps**:
1. Make frontend changes in `frontend/src/`
2. Rebuild frontend:
   ```bash
   ./deploy-local-prod.sh rebuild
   ```
3. Wait ~2-3 minutes for build to complete
4. Test at http://localhost:8080
5. Repeat as needed

**⚠️ No hot reload** - Every change requires a full rebuild.

---

#### Workflow 2: Backend Development with Production Frontend

**Use when**: Testing backend changes against production-like frontend

**Steps**:
1. Start environment:
   ```bash
   ./deploy-local-prod.sh start
   ```
2. Edit backend code in `backend/src/`
3. Backend auto-restarts (~5 seconds) - **has hot reload**
4. Test at http://localhost:8080 (frontend) or http://localhost:8000 (API)
5. No frontend rebuild needed (unless you change frontend code)

**Best for**: API development where frontend is stable.

---

### Verification Checks

After starting local-prod, verify that everything works correctly:

#### 1. Frontend Serves Static Files

```bash
curl -I http://localhost:8080
```

**Expected**:
```
HTTP/1.1 200 OK
Server: nginx/...
Content-Type: text/html
```

#### 2. Nginx Proxy Works

```bash
# Call backend directly
curl http://localhost:8000/health
# {"status":"healthy","version":"1.0.0"}

# Call through Nginx proxy
curl http://localhost:8080/api/health
# {"status":"healthy","version":"1.0.0"}  ← Same response
```

#### 3. Cache Headers Correct

**Check JS/CSS assets** (should have 1-year cache):
```bash
curl -I http://localhost:8080/assets/main.abc123.js
```

**Expected**:
```
Cache-Control: public, immutable
Expires: ... (1 year from now)
```

**Check index.html** (should NOT be cached):
```bash
curl -I http://localhost:8080/index.html
```

**Expected**:
```
Cache-Control: no-cache, no-store, must-revalidate
```

#### 4. Security Headers Present

```bash
curl -I http://localhost:8080
```

**Expected headers**:
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

---

## Architecture

### Container Stack

```
┌─────────────────────────────────────────────────┐
│   Nginx Container (Frontend)                    │
│   contravento-frontend-local-prod               │
│   • Port 8080 → host:8080                       │
│   • Serves /usr/share/nginx/html (React build)  │
│   • Proxies /api/* → backend:8000               │
└─────────────────────────────────────────────────┘
                    ↓ HTTP Proxy
┌─────────────────────────────────────────────────┐
│   Backend Container                             │
│   contravento-backend-local-prod                │
│   • FastAPI (DEVELOPMENT mode with hot reload)  │
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
└─────────────────────────────────────────────────┘
```

### Docker Compose Files

This mode uses **multi-file composition**:

1. **docker-compose.yml** (base configuration)
2. **docker-compose.local-prod.yml** (overrides for local-prod mode)

**Start command expands to**:
```bash
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.local-prod.yml \
  --env-file .env.local \
  up -d
```

### Frontend Build Process

```
1. ./deploy-local-prod.sh start
   ↓
2. docker-compose build frontend
   ├─ Stage 1: Builder (node:18-alpine)
   │  ├─ npm ci (install dependencies)
   │  ├─ npm run build (compile to dist/)
   │  │  ├─ TypeScript → JavaScript
   │  │  ├─ Minification (Terser)
   │  │  ├─ Tree-shaking
   │  │  └─ Hash assets (main.abc123.js)
   │  └─ Generates dist/
   │
   └─ Stage 2: Runtime (nginx:alpine)
      ├─ COPY dist/ → /usr/share/nginx/html
      ├─ COPY nginx.conf
      └─ CMD nginx
   ↓
3. docker-compose up -d
   ├─ Backend (development) on :8000
   ├─ Frontend (nginx) on :8080
   ├─ PostgreSQL on :5432
   ├─ Redis on :6379
   ├─ MailHog on :8025
   └─ pgAdmin on :5050
   ↓
4. Access http://localhost:8080
   ├─ Browser → Nginx
   ├─ Requests /api/* → Nginx proxy → Backend:8000
   └─ Static files served from /usr/share/nginx/html
```

---

## Troubleshooting

### Frontend Issues

#### Error: "404 Not Found" when accessing http://localhost:8080

**Cause**: Nginx container not running or build failed

**Fix - Check frontend container**:
```bash
docker ps | grep contravento-frontend-local-prod
```

**If not running, check logs**:
```bash
docker logs contravento-frontend-local-prod
```

**If build failed, rebuild**:
```bash
./deploy-local-prod.sh rebuild
```

---

#### Frontend changes not appearing

**Cause**: Forgot to rebuild after changes (no hot reload)

**Fix - Rebuild frontend**:
```bash
./deploy-local-prod.sh rebuild
```

**If still not working, clean rebuild**:
```bash
./deploy-local-prod.sh clean
./deploy-local-prod.sh start
```

---

#### Error: "/api/* returns 502 Bad Gateway"

**Cause**: Nginx proxy can't reach backend

**Fix - Check backend is running**:
```bash
docker ps | grep contravento-backend-local-prod
```

**Test backend directly**:
```bash
curl http://localhost:8000/health
```

**If backend not running**:
```bash
./deploy-local-prod.sh logs backend
```

**Check Docker network**:
```bash
docker network inspect contravento-network
# Both backend and frontend should be in same network
```

---

### Build Issues

#### Error: "npm ERR! code ELIFECYCLE" during build

**Cause**: TypeScript compilation errors or missing dependencies

**Fix - Check build logs**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.local-prod.yml --env-file .env.local logs frontend
```

**Common causes**:
- **TypeScript errors**: Fix errors in `frontend/src/`
- **Missing dependencies**: Update `package.json` and rebuild
- **Environment variables**: Check `frontend/.env.production.example`

**Fix TypeScript errors first**:
```bash
cd frontend
npm run build  # Test build locally
```

---

#### Build takes too long (>10 minutes)

**Cause**: Slow network or Docker cache issues

**Fix - Use cached layers**:
```bash
# Normal rebuild (uses cache)
./deploy-local-prod.sh rebuild

# If rebuild is slow, check Docker Desktop resource limits
# Settings → Resources → Memory (increase to 4+ GB)
```

---

### Nginx Issues

#### Static assets not loading (404)

**Cause**: Build didn't copy dist/ to Nginx correctly

**Fix - Verify files exist in container**:
```bash
docker exec contravento-frontend-local-prod ls -la /usr/share/nginx/html
```

Should show:
```
index.html
assets/
  main.abc123.js
  main.def456.css
  ...
```

**If empty, rebuild**:
```bash
./deploy-local-prod.sh rebuild
```

---

#### Wrong cache headers

**Cause**: Nginx config not applied correctly

**Fix - Verify nginx.conf was copied**:
```bash
docker exec contravento-frontend-local-prod cat /etc/nginx/nginx.conf
```

**If missing config, rebuild image**:
```bash
./deploy-local-prod.sh clean
./deploy-local-prod.sh start
```

---

## Related Modes

### Progression Path

```
local-dev (SQLite)
    ↓
local-minimal (Docker + PostgreSQL)
    ↓
local-full (Complete Stack with Vite dev server)
    ↓
local-prod (Production build testing)  ← You are here
    ↓
When deploying to server:
    → dev (Integration server)
    → staging (Pre-production - same Nginx config)
    → prod (Live production)
```

### When to Upgrade

**From local-prod to [staging](staging.md)**:
- Ready for final QA testing
- Need SSL/TLS certificates
- Want production-grade monitoring (Sentry)
- Testing with real domain name

**From local-prod to [prod](prod.md)**:
- Ready to serve real users
- Need high availability (load balancing)
- Auto-scaling based on traffic

### Quick Comparison

| Feature | local-full | local-prod | staging | prod |
|---------|------------|------------|---------|------|
| **Frontend** | Vite dev | Nginx (production build) | Nginx | Nginx |
| **Hot Reload** | ✅ (HMR) | ❌ (rebuild needed) | ❌ | ❌ |
| **Backend Mode** | Development | Development | Production | Production |
| **SSL/TLS** | ❌ | ❌ | ✅ | ✅ |
| **Port** | 5173 | 8080 | 80/443 | 80/443 |
| **Minification** | ❌ | ✅ | ✅ | ✅ |
| **Source Maps** | ✅ | ❌ | ⚠️ (optional) | ❌ |
| **Cache Headers** | ❌ | ✅ | ✅ | ✅ |
| **Best for** | Development | Build testing | QA testing | Live users |

---

## Additional Resources

- **[Getting Started Guide](../guides/getting-started.md)** - General deployment introduction
- **[Environment Variables Guide](../guides/environment-variables.md)** - Complete .env reference
- **[Frontend Deployment Guide](../guides/frontend-deployment.md)** - React build process, Nginx config
- **[Docker Compose Guide](../guides/docker-compose-guide.md)** - Multi-file composition explained
- **[Production Checklist](../guides/production-checklist.md)** - Pre-deployment validation
- **[Troubleshooting Guide](../guides/troubleshooting.md)** - Cross-mode common issues
- **[Deployment Index](../README.md)** - All deployment modes

---

## Tips

1. **Daily development**: Use `./deploy.sh local --with-frontend` (has hot reload)
2. **Production build testing**: Use `./deploy-local-prod.sh` (this mode)
3. **CI/CD pipelines**: Use Dockerfile.prod automatically
4. **Performance**: Production build is ~10x faster to serve than dev server
5. **Debugging**: If you need source maps, use [local-full](local-full.md) (development mode)

---

**Need more help?** Check the [Troubleshooting Guide](../guides/troubleshooting.md) or open an issue on GitHub.

**Last Updated**: 2026-01-25
