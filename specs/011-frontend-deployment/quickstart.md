# Quick Start: Frontend Deployment Integration

**Feature**: 011-frontend-deployment
**Purpose**: Step-by-step guide to set up and run the React frontend in all deployment environments
**Target Audience**: Developers new to the ContraVento codebase

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Option 1: SQLite Local (No Docker)](#option-1-sqlite-local-no-docker---fastest-)
3. [Option 2: Docker Minimal](#option-2-docker-minimal-postgresql--backend--frontend)
4. [Option 3: Docker Full](#option-3-docker-full-all-services)
5. [Option 4: Production Builds](#option-4-production-builds-stagingproduction)
6. [Troubleshooting](#troubleshooting)
7. [Environment Variables Reference](#environment-variables-reference)

---

## Prerequisites

Before starting, ensure you have:

✅ **Node.js 18+** installed ([Download](https://nodejs.org/))
```bash
node --version  # Should show v18.x or higher
```

✅ **npm** installed (comes with Node.js)
```bash
npm --version  # Should show 9.x or higher
```

✅ **Backend running** (see [QUICK_START.md](../../../QUICK_START.md) for backend setup)

✅ **Git** installed (for cloning the repository)

---

## Option 1: SQLite Local (No Docker) - FASTEST ⚡

**Best for**: Daily development, quick iteration, prototyping

**Pros**: Instant startup (<30 seconds), no Docker required, lightweight
**Cons**: Uses SQLite instead of PostgreSQL, no MailHog/Redis

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

**Expected output**:
```
added 1234 packages in 45s
```

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env.development

# Verify VITE_API_URL points to local backend
cat .env.development
```

**Expected content**:
```env
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA
```

### Step 3: Start Backend + Frontend Together

**Option A: Start both with single script** (Recommended)
```bash
cd ..  # Return to project root
./run-local-dev.sh --with-frontend        # Linux/Mac
.\run-local-dev.ps1 -WithFrontend         # Windows PowerShell
```

**Option B: Start separately** (for debugging)
```bash
# Terminal 1: Backend
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Step 4: Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**Expected behavior**:
- Frontend loads with login page
- API requests to `/api/*` automatically proxy to backend
- No CORS errors in browser console (F12)

### Step 5: Test Hot Module Replacement (HMR)

1. Open `frontend/src/App.tsx` in your editor
2. Change any text (e.g., "ContraVento" → "ContraVento Dev")
3. Save the file

**Expected behavior**:
- Browser updates in <2 seconds without full reload
- Console shows `[vite] hot updated: /src/App.tsx`

**Status**: ✅ SQLite Local setup complete!

---

## Option 2: Docker Minimal (PostgreSQL + Backend + Frontend)

**Best for**: Testing PostgreSQL-specific features, pre-staging validation

**Pros**: Real PostgreSQL database, closer to production environment
**Cons**: Slower startup (~60 seconds), requires Docker

### Step 1: Ensure Docker is Running

```bash
docker --version  # Should show Docker version 20.x or higher
docker-compose --version  # Should show 2.x or higher
```

If Docker is not running, start Docker Desktop (Windows/Mac) or Docker service (Linux).

### Step 2: Configure Environment

```bash
# Ensure .env.local-minimal exists
cp .env.local-minimal.example .env.local-minimal

# Edit if needed (default values usually work)
nano .env.local-minimal
```

### Step 3: Start All Services

```bash
./deploy.sh local-minimal --with-frontend  # Linux/Mac
.\deploy.ps1 local-minimal -WithFrontend   # Windows PowerShell
```

**Expected output**:
```
Creating network "contravento_local-minimal" ... done
Creating contravento-db-local ... done
Creating contravento-backend-local ... done
Creating contravento-frontend-local ... done

✓ All services started successfully!

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
```

### Step 4: Verify Services are Running

```bash
docker-compose ps
```

**Expected output**:
```
NAME                       STATUS          PORTS
contravento-db-local       Up (healthy)    5432/tcp
contravento-backend-local  Up (healthy)    0.0.0.0:8000->8000/tcp
contravento-frontend-local Up              0.0.0.0:5173->5173/tcp
```

### Step 5: Check Frontend Logs

```bash
docker-compose logs -f frontend-dev
```

**Expected output**:
```
frontend-dev | VITE v5.0.8  ready in 1234 ms
frontend-dev |
frontend-dev |   ➜  Local:   http://localhost:5173/
frontend-dev |   ➜  Network: http://172.18.0.4:5173/
frontend-dev |   ➜  press h + enter to show help
```

**Status**: ✅ Docker Minimal setup complete!

---

## Option 3: Docker Full (All Services)

**Best for**: Testing emails, cache, full-stack integration

**Pros**: Complete environment (MailHog, Redis, pgAdmin)
**Cons**: Slowest startup (~90 seconds), highest resource usage (~1.5GB RAM)

### Step 1: Configure Environment

```bash
# Ensure .env.local exists
cp .env.local.example .env.local

# Edit with your settings
nano .env.local
```

**Required variables**:
- `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_urlsafe(64))"`)
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `PGADMIN_PASSWORD`

### Step 2: Start All Services

```bash
./deploy.sh local --with-frontend  # Linux/Mac
.\deploy.ps1 local -WithFrontend   # Windows PowerShell
```

**Expected output**:
```
Creating network "contravento_local" ... done
Creating contravento-db-local ... done
Creating contravento-redis-local ... done
Creating contravento-backend-local ... done
Creating contravento-frontend-local ... done
Creating contravento-mailhog-local ... done
Creating contravento-pgadmin-local ... done

✓ All services started successfully!

Access:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- MailHog: http://localhost:8025
- pgAdmin: http://localhost:5050
```

### Step 3: Test Email Functionality

1. Open frontend: http://localhost:5173
2. Click "Registrarse" (Register)
3. Fill registration form and submit
4. Open MailHog: http://localhost:8025
5. Verify email with subject "Verifica tu cuenta en ContraVento"

**Expected behavior**:
- Email appears in MailHog inbox within 5 seconds
- Email contains verification link

### Step 4: Access pgAdmin (Database UI)

1. Open pgAdmin: http://localhost:5050
2. Login with credentials from `.env.local`:
   - Email: `${PGADMIN_EMAIL}` (default: `admin@example.com`)
   - Password: `${PGADMIN_PASSWORD}`
3. Add server:
   - Host: `db` (Docker network name)
   - Port: `5432`
   - Database: `contravento`
   - Username: `${POSTGRES_USER}`
   - Password: `${POSTGRES_PASSWORD}`

**Status**: ✅ Docker Full setup complete!

---

## Option 4: Production Builds (Staging/Production)

**Best for**: Deployment to staging/production environments

**Pros**: Optimized builds, Nginx serving, production-ready
**Cons**: No hot reload, requires rebuild for changes

### Step 1: Configure Production Environment Variables

```bash
cd frontend

# For Staging
cp .env.example .env.staging
nano .env.staging
```

**`.env.staging` example**:
```env
VITE_API_URL=https://api-staging.contravento.com
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA
```

**`.env.production` example**:
```env
VITE_API_URL=https://api.contravento.com
VITE_TURNSTILE_SITE_KEY=<PRODUCTION_KEY>
```

### Step 2: Build for Staging

```bash
npm run build:staging
```

**Expected output**:
```
vite v5.0.8 building for production...
✓ 1234 modules transformed.
dist/index.html                  0.45 kB │ gzip: 0.30 kB
dist/assets/index-abc123.css    45.67 kB │ gzip: 12.34 kB
dist/assets/index-def456.js    234.56 kB │ gzip: 78.90 kB
✓ built in 23.45s
```

**Output**: `frontend/dist/` directory with optimized static files

### Step 3: Verify Build Output

```bash
ls -lh dist/
```

**Expected structure**:
```
dist/
├── index.html               # Entry point (NOT cached)
├── assets/
│   ├── index-[hash].css    # Hashed CSS bundle (cached 1 year)
│   ├── index-[hash].js     # Hashed JS bundle (cached 1 year)
│   └── vendor-[hash].js    # Vendor libraries bundle
└── images/
    └── logo-[hash].png     # Hashed images
```

### Step 4: Test Build Locally (Optional)

```bash
# Install local HTTP server
npm install -g serve

# Serve dist/ directory
serve -s dist -l 3000
```

**Access**: http://localhost:3000

**Expected behavior**:
- Frontend loads correctly
- API calls go to staging backend (configured in VITE_API_URL)

### Step 5: Deploy to Staging

```bash
cd ..  # Return to project root
./deploy.sh staging
```

**What happens**:
1. Script runs `npm run build:staging`
2. Builds Docker image with Nginx + static files
3. Pushes image to container registry
4. Deploys to staging environment
5. Nginx serves `dist/` files with caching headers

**Access**: https://staging.contravento.com

### Step 6: Deploy to Production

```bash
npm run build:prod  # In frontend/

# From project root
./deploy.sh prod
```

**Production differences**:
- Source maps disabled (security)
- Stricter cache headers
- HTTPS enforced
- Production API URL

**Status**: ✅ Production builds complete!

---

## Troubleshooting

### Issue: Port 5173 Already in Use

**Symptom**: Error when starting frontend dev server

```
Error: Port 5173 is already in use
```

**Solution**:

```bash
# Windows - Find process using port 5173
netstat -ano | findstr :5173

# Kill process (replace <PID> with actual process ID)
taskkill /PID <PID> /F

# Linux/Mac - Find and kill process
lsof -ti:5173 | xargs kill -9
```

### Issue: CORS Errors in Development

**Symptom**: Browser console shows CORS policy errors

```
Access to XMLHttpRequest at 'http://localhost:8000/api/users/me' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution**:

1. Verify Vite proxy is configured in `frontend/vite.config.ts`:
   ```typescript
   export default defineConfig({
     server: {
       proxy: {
         '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true
         }
       }
     }
   })
   ```

2. Ensure API requests use relative paths:
   ```typescript
   // ✅ Correct - proxied through Vite
   axios.get('/api/users/me')

   // ❌ Wrong - goes directly to backend (CORS error)
   axios.get('http://localhost:8000/api/users/me')
   ```

3. Restart frontend dev server

### Issue: Hot Reload Not Working (Docker)

**Symptom**: Code changes don't reflect in browser when using Docker

**Solution**:

1. Verify volumes are mounted in `docker-compose.local.yml`:
   ```yaml
   frontend-dev:
     volumes:
       - ./frontend:/app
       - /app/node_modules  # Important: prevents overwriting
   ```

2. Check frontend logs:
   ```bash
   docker-compose logs -f frontend-dev
   ```

   **Expected**: `[vite] HMR update: /src/App.tsx`

3. If still not working, restart Docker service:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Issue: Build Fails with "VITE_API_URL not defined"

**Symptom**: `npm run build:staging` or `build:prod` fails

```
Error: VITE_API_URL is required but not defined
```

**Solution**:

1. Ensure `.env.staging` or `.env.production` exists:
   ```bash
   ls frontend/.env.staging
   ```

2. Verify file contains required variables:
   ```bash
   cat frontend/.env.staging
   ```

   **Expected**:
   ```env
   VITE_API_URL=https://api-staging.contravento.com
   ```

3. Rebuild with correct mode:
   ```bash
   npm run build:staging  # For staging
   npm run build:prod     # For production
   ```

### Issue: Backend Not Responding in Docker

**Symptom**: Frontend loads but API calls fail with 502 Bad Gateway

**Solution**:

1. Check backend health:
   ```bash
   docker-compose ps
   ```

   **Expected**: `contravento-backend-local` shows `Up (healthy)`

2. Check backend logs:
   ```bash
   docker-compose logs backend
   ```

   **Look for**: Errors during startup (database connection, migrations)

3. Restart backend service:
   ```bash
   docker-compose restart backend
   ```

4. If database issues, reset volumes:
   ```bash
   docker-compose down -v  # ⚠️ Deletes all data!
   docker-compose up -d
   ```

---

## Environment Variables Reference

### Development (.env.development)

**File location**: `frontend/.env.development`

**Purpose**: Auto-loaded when running `npm run dev`

**Required variables**:
```env
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA
```

### Staging (.env.staging)

**File location**: `frontend/.env.staging`

**Purpose**: Loaded when running `npm run build:staging`

**Required variables**:
```env
VITE_API_URL=https://api-staging.contravento.com
VITE_TURNSTILE_SITE_KEY=<STAGING_KEY>
```

### Production (.env.production)

**File location**: `frontend/.env.production`

**Purpose**: Loaded when running `npm run build` or `npm run build:prod`

**Required variables**:
```env
VITE_API_URL=https://api.contravento.com
VITE_TURNSTILE_SITE_KEY=<PRODUCTION_KEY>
```

**Security Notes**:
- ⚠️ **Never commit** `.env.staging` or `.env.production` to git (use `.gitignore`)
- ✅ **Do commit** `.env.example` as a template
- ✅ Variables with `VITE_` prefix are exposed to frontend code (safe for public)
- ❌ **Never** put secret API keys in VITE_* variables (they're visible in browser)

---

## Quick Reference: Common Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `npm install` | Install dependencies | First time, or after `package.json` changes |
| `npm run dev` | Start Vite dev server | Daily development |
| `npm run build` | Build for production | Deployment to prod |
| `npm run build:staging` | Build for staging | Deployment to staging |
| `npm run preview` | Preview production build locally | Test build before deployment |
| `docker-compose up -d` | Start Docker services | Docker Minimal/Full development |
| `docker-compose down` | Stop Docker services | End of day, free resources |
| `docker-compose logs -f frontend-dev` | View frontend logs | Debugging Docker issues |

---

## Next Steps

✅ **Frontend deployment configured!**

**What to do next**:
1. **Read [CLAUDE.md](../../../CLAUDE.md)** - Development guidelines and patterns
2. **Read [frontend/TESTING_GUIDE.md](../../../frontend/TESTING_GUIDE.md)** - Testing best practices
3. **Start coding** - Create your first feature!

**Need help?**
- Check [TROUBLESHOOTING.md](../../../TROUBLESHOOTING.md) for common issues
- Ask in team chat or create a GitHub issue
