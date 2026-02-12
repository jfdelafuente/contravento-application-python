# Troubleshooting Common Deployment Issues

**When something breaks, start here**

**Purpose**: Quick solutions to the most common problems across all deployment modes

---

## Table of Contents

1. [Port Conflicts](#port-conflicts)
2. [Docker Issues](#docker-issues)
3. [Database Errors](#database-errors)
4. [Frontend Build Failures](#frontend-build-failures)
5. [Permission Errors](#permission-errors)
6. [Authentication & API Issues](#authentication--api-issues)
7. [Performance Issues](#performance-issues)
8. [Quick Diagnosis Guide](#quick-diagnosis-guide)

---

## Port Conflicts

### Port 8000 Already in Use (Backend)

**Symptom**:
```
ERROR: Port 8000 is already in use
Address already in use
```

**Cause**: Another process (usually a zombie uvicorn or Docker container) is using port 8000

**Solution**:

**Linux/Mac**:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
lsof -ti:8000 | xargs kill -9

# Verify port is free
lsof -ti:8000  # Should return nothing
```

**Windows PowerShell**:
```powershell
# Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Kill the process (replace <PID> with actual process ID)
Stop-Process -Id <PID> -Force

# Alternative one-liner
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

**Windows CMD**:
```cmd
# Find process
netstat -ano | findstr :8000

# Kill process (replace <PID> with process ID from previous command)
taskkill /PID <PID> /F
```

---

### Port 5173 Already in Use (Frontend)

**Symptom**:
```
ERROR: Port 5173 is already in use
Failed to start dev server
```

**Cause**: Another Vite dev server or process is using port 5173

**Solution**:

**Linux/Mac**:
```bash
# Find and kill process
lsof -ti:5173 | xargs kill -9
```

**Windows PowerShell**:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process
```

**Windows CMD**:
```cmd
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Alternative**: Change the port in `frontend/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 5174  // Change to different port
  }
})
```

---

### Port 5432 Already in Use (PostgreSQL)

**Symptom**:
```
ERROR: for db  Cannot start service db: driver failed programming external connectivity
Bind for 0.0.0.0:5432 failed: port is already allocated
```

**Cause**: Another PostgreSQL instance or Docker container is using port 5432

**Solution**:

**Option 1**: Stop existing PostgreSQL
```bash
# Linux
sudo systemctl stop postgresql

# Mac
brew services stop postgresql

# Windows
# Stop PostgreSQL service from Services app (services.msc)
```

**Option 2**: Change port in `docker-compose.*.yml`
```yaml
services:
  db:
    ports:
      - "5433:5432"  # Map external port 5433 to internal 5432
```

Then update `DATABASE_URL` in `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5433/contravento
```

---

### Port 6379 Already in Use (Redis)

**Symptom**:
```
ERROR: for redis  Cannot start service redis: driver failed programming external connectivity
Bind for 0.0.0.0:6379 failed: port is already allocated
```

**Cause**: Another Redis instance is running

**Solution**:
```bash
# Find and kill Redis process
# Linux/Mac
ps aux | grep redis-server
kill -9 <PID>

# Or change port in docker-compose.yml
services:
  redis:
    ports:
      - "6380:6379"
```

---

### Port 8025 Already in Use (MailHog)

**Symptom**:
```
ERROR: for mailhog  Cannot start service mailhog: driver failed programming external connectivity
Bind for 0.0.0.0:8025 failed: port is already allocated
```

**Solution**:
```bash
# Find process
lsof -ti:8025 | xargs kill -9  # Linux/Mac

# Or change port in docker-compose.yml
services:
  mailhog:
    ports:
      - "8026:8025"
```

---

## Docker Issues

### Docker Daemon Not Running

**Symptom**:
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

**Solution**:

**Windows/Mac**:
1. Open Docker Desktop application
2. Wait for Docker icon to show "running" status
3. Retry deployment command

**Linux**:
```bash
# Start Docker daemon
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Verify Docker is running
sudo systemctl status docker
```

---

### Container Won't Start (Unhealthy Status)

**Symptom**:
```bash
docker-compose ps
# Shows container status as "unhealthy" or "restarting"
```

**Diagnosis**:
```bash
# Check container logs
docker-compose logs backend
docker-compose logs db
docker-compose logs redis

# Check specific container
docker logs contravento-backend-local
```

**Common Causes & Fixes**:

**1. Database not ready**:
```bash
# Backend logs show: "Could not connect to database"

# Fix: Wait longer for DB to initialize (add depends_on in docker-compose.yml)
# Or manually restart backend after DB is ready
docker-compose restart backend
```

**2. Missing environment variables**:
```bash
# Backend logs show: "SECRET_KEY is required"

# Fix: Verify .env file exists and has all required variables
cat .env.local  # Check for missing values
```

**3. Migration failures**:
```bash
# Backend logs show: "Migration failed"

# Fix: Reset database
docker-compose down -v  # ⚠️ Deletes all data
docker-compose up -d
```

---

### Can't Connect to PostgreSQL from Backend

**Symptom**:
```
could not connect to server: Connection refused
Is the server running on host "db" and accepting TCP/IP connections on port 5432?
```

**Diagnosis**:
```bash
# Check if PostgreSQL container is running
docker-compose ps db

# Expected: "Up (healthy)"
# If "unhealthy" or "restarting", check logs:
docker-compose logs db
```

**Solutions**:

**1. Database not fully initialized**:
```bash
# Wait 10-20 seconds for PostgreSQL to finish initialization
sleep 20
docker-compose restart backend
```

**2. Wrong hostname in DATABASE_URL**:
```bash
# Verify .env file uses correct hostname
cat .env.local | grep DATABASE_URL

# Should be: postgresql://user:password@db:5432/contravento
# NOT: postgresql://user:password@localhost:5432/contravento
```

**3. Network issues**:
```bash
# Restart all services
docker-compose down
docker-compose up -d
```

---

### Volume Mount Errors (Hot Reload Not Working)

**Symptom**:
- Code changes in `backend/` or `frontend/` don't reflect in running containers
- OR: Permission denied errors

**Diagnosis**:
```bash
# Check if volumes are mounted
docker inspect contravento-backend-local | grep -A 10 Mounts

# Expected: You should see ./backend:/app mapped
```

**Solution**:

**1. Verify docker-compose.yml has volumes**:
```yaml
services:
  backend:
    volumes:
      - ./backend:/app
      - /app/.venv  # Don't overwrite Python virtual environment

  frontend-dev:
    volumes:
      - ./frontend:/app
      - /app/node_modules  # Don't overwrite node_modules
```

**2. Restart containers**:
```bash
docker-compose down
docker-compose up -d
```

**3. Windows-specific: Enable file sharing**:
- Docker Desktop → Settings → Resources → File Sharing
- Add project directory
- Apply & Restart

---

### Docker Build Fails (Out of Space)

**Symptom**:
```
ERROR: failed to solve: write /var/lib/docker/tmp/...: no space left on device
```

**Solution**:
```bash
# Clean up unused Docker resources
docker system prune -a --volumes

# This removes:
# - All stopped containers
# - All networks not used by at least one container
# - All volumes not used by at least one container
# - All images without at least one container associated to them
# - All build cache

# WARNING: This will delete ALL Docker data, including other projects!
# More selective cleanup:
docker image prune -a  # Remove unused images
docker container prune  # Remove stopped containers
docker volume prune  # Remove unused volumes
```

---

## Database Errors

### Database Connection Refused (local-dev)

**Symptom**:
```
sqlite3.OperationalError: unable to open database file
```

**Cause**: Database file doesn't exist or wrong path

**Solution**:
```bash
# Run setup again
./run-local-dev.sh --setup  # Linux/Mac
.\run-local-dev.ps1 -Setup  # Windows

# Or manually create database
cd backend
poetry run alembic upgrade head
```

---

### Migration Conflicts

**Symptom**:
```
alembic.util.exc.CommandError: Target database is not up to date.
Can't locate revision identified by '...'
```

**Cause**: Database schema doesn't match migration history

**Solution**:

**Option 1**: Reset database (⚠️ deletes all data)
```bash
# local-dev (SQLite)
rm backend/contravento_dev.db
./run-local-dev.sh --setup

# Docker modes (PostgreSQL)
docker-compose down -v
docker-compose up -d
```

**Option 2**: Force schema to specific version
```bash
cd backend

# Downgrade to base
poetry run alembic downgrade base

# Upgrade to latest
poetry run alembic upgrade head
```

**Option 3**: Stamp current schema without running migrations
```bash
cd backend

# Get latest revision ID
poetry run alembic history | head -n 1

# Stamp database (replace <rev_id> with actual revision)
poetry run alembic stamp <rev_id>
```

---

### Seed Data Missing (No Admin User)

**Symptom**:
- Can't log in with `admin / AdminPass123!`
- `/api/users/me` returns 401 Unauthorized

**Diagnosis**:
```bash
# local-dev (SQLite)
sqlite3 backend/contravento_dev.db "SELECT username FROM users;"

# Docker modes (PostgreSQL)
docker exec -it contravento-db-local psql -U contravento -d contravento -c "SELECT username FROM users;"
```

**Expected**: Should see `admin`, `testuser`, `maria_garcia`

**Solution**:
```bash
cd backend

# Create admin user manually
poetry run python scripts/user-mgmt/create_admin.py

# Create test users
poetry run python scripts/user-mgmt/create_verified_user.py

# Seed cycling types
poetry run python scripts/seeding/seed_cycling_types.py
```

---

### Foreign Key Constraint Violations (SQLite)

**Symptom**:
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

**Cause**: SQLite foreign key enforcement is disabled by default

**Solution**:

**1. Verify foreign keys are enabled in `backend/src/database.py`**:
```python
# For SQLite connections
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if isinstance(dbapi_conn, sqlite3.Connection):  # SQLite only
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
```

**2. Recreate database**:
```bash
rm backend/contravento_dev.db
./run-local-dev.sh --setup
```

---

## Frontend Build Failures

### VITE_API_URL Not Defined

**Symptom**:
```
Error: VITE_API_URL is required but not defined
Build failed
```

**Cause**: Missing environment file for build mode

**Solution**:

**For staging build**:
```bash
# Create .env.staging file
cd frontend
cp .env.example .env.staging

# Edit and set API URL
echo "VITE_API_URL=https://api-staging.contravento.com" > .env.staging
echo "VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA" >> .env.staging

# Build
npm run build:staging
```

**For production build**:
```bash
# Create .env.production file
cd frontend
cp .env.example .env.production

# Edit and set production API URL
echo "VITE_API_URL=https://api.contravento.com" > .env.production
echo "VITE_TURNSTILE_SITE_KEY=<PRODUCTION_KEY>" >> .env.production

# Build
npm run build:prod
```

---

### TypeScript Type Errors

**Symptom**:
```
error TS2345: Argument of type 'string | undefined' is not assignable to parameter of type 'string'
Build failed with 5 errors
```

**Solution**:

**Quick fix (not recommended for production)**:
```bash
# Skip type checking (emergency only)
npm run build -- --mode production --skipLibCheck
```

**Proper fix**:
```bash
# Check type errors
npm run type-check

# Fix errors in code
# Add null checks, fix type definitions, etc.

# Then build
npm run build:prod
```

---

### Vite Build Hangs or Takes Too Long

**Symptom**:
- `npm run build` runs for >5 minutes without finishing
- OR: Build uses >8 GB RAM and crashes

**Solution**:

**1. Clear Vite cache**:
```bash
cd frontend
rm -rf node_modules/.vite
npm run build
```

**2. Increase Node.js memory limit**:
```bash
# Linux/Mac
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build

# Windows PowerShell
$env:NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

**3. Disable source maps (faster builds)**:
```typescript
// frontend/vite.config.ts
export default defineConfig({
  build: {
    sourcemap: false  // Disable for faster builds
  }
})
```

---

### Assets Not Loading (404 Errors)

**Symptom**:
- Frontend loads but images/fonts show 404 errors
- Console shows: `GET http://localhost:5173/assets/logo.png 404 (Not Found)`

**Diagnosis**:
```bash
# Check if assets exist in dist/
ls -la frontend/dist/assets/

# Check Nginx logs (Docker modes)
docker-compose logs frontend
```

**Solution**:

**1. Verify asset paths use import**:
```typescript
// ✅ Correct - Vite processes this
import logo from '@/assets/logo.png'
<img src={logo} alt="Logo" />

// ❌ Wrong - Path won't be resolved
<img src="/assets/logo.png" alt="Logo" />
```

**2. Check Nginx configuration** (production builds):
```nginx
# In frontend/nginx.conf
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**3. Hard refresh browser**:
- Chrome/Firefox: `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- Safari: `Cmd + Option + R`

---

### npm install Fails (Dependency Conflicts)

**Symptom**:
```
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR! Found: react@18.2.0
npm ERR! Could not resolve dependency: peer react@"^17.0.0" from ...
```

**Solution**:

**1. Clear cache and reinstall**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**2. Use legacy peer deps** (if conflicts persist):
```bash
npm install --legacy-peer-deps
```

**3. Update dependencies**:
```bash
# Check for outdated packages
npm outdated

# Update specific package
npm update <package-name>

# Update all packages (use with caution)
npm update
```

---

## Permission Errors

### Can't Write to storage/ Directory

**Symptom**:
```
PermissionError: [Errno 13] Permission denied: 'storage/profile_photos/...'
```

**Cause**: Wrong file ownership or permissions

**Solution**:

**Linux/Mac**:
```bash
# Change ownership to current user
sudo chown -R $USER:$USER storage/

# Set correct permissions
chmod -R 755 storage/
```

**Windows**:
1. Right-click `storage/` folder
2. Properties → Security tab
3. Edit → Add your user account
4. Grant "Full control"
5. Apply to this folder, subfolders, and files

---

### Docker Socket Permission Denied

**Symptom**:
```
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

**Cause**: Current user is not in `docker` group (Linux only)

**Solution**:

**Linux**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in (or restart)
# Verify membership
groups

# Test Docker without sudo
docker ps
```

**Alternative (not recommended)**: Use sudo for docker commands
```bash
sudo docker-compose up -d
```

---

### Can't Create Files in Project Directory (Windows)

**Symptom**:
```
OSError: [WinError 5] Access is denied
```

**Cause**: Project in protected directory (Program Files, System32, etc.)

**Solution**:
1. Move project to user directory:
   ```bash
   # Good locations
   C:\Users\YourName\Projects\contravento
   C:\Dev\contravento
   ```

2. OR: Run terminal as Administrator (not recommended for daily work)

---

## Authentication & API Issues

### Login Returns 401 Unauthorized

**Symptom**:
```json
{
  "detail": {
    "code": "INVALID_CREDENTIALS",
    "message": "Usuario o contraseña incorrectos"
  }
}
```

**Diagnosis**:
```bash
# Verify user exists in database
# SQLite
sqlite3 backend/contravento_dev.db "SELECT username, is_verified FROM users WHERE username='admin';"

# PostgreSQL (Docker)
docker exec -it contravento-db-local psql -U contravento -d contravento -c "SELECT username, is_verified FROM users WHERE username='admin';"
```

**Solution**:

**1. User doesn't exist**:
```bash
cd backend
poetry run python scripts/user-mgmt/create_admin.py
```

**2. User not verified**:
```bash
cd backend
poetry run python scripts/user-mgmt/create_verified_user.py --verify-email admin@contravento.com
```

**3. Wrong credentials**:
```bash
# Default credentials (if created with setup script)
Username: admin
Password: AdminPass123!

# Reset password (create new admin)
cd backend
poetry run python scripts/user-mgmt/create_admin.py --username newadmin --password "NewPass123!"
```

---

### CORS Errors in Browser Console

**Symptom**:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/users/me' from origin 'http://localhost:5173'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

**Cause**: API requests not proxied through Vite

**Solution**:

**1. Verify Vite proxy configuration** (`frontend/vite.config.ts`):
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

**2. Use relative paths in API calls**:
```typescript
// ✅ Correct - proxied through Vite
axios.get('/api/users/me')

// ❌ Wrong - goes directly to backend (CORS error)
axios.get('http://localhost:8000/api/users/me')
```

**3. Restart frontend dev server**:
```bash
# Kill existing process
lsof -ti:5173 | xargs kill -9  # Linux/Mac
# Or Ctrl+C in terminal where frontend is running

# Start again
./run-local-dev.sh --with-frontend
```

---

### JWT Token Expired (403 Forbidden)

**Symptom**:
```json
{
  "detail": {
    "code": "TOKEN_EXPIRED",
    "message": "Token de acceso expirado"
  }
}
```

**Cause**: Access token expired after 15 minutes (by design)

**Solution**:

**1. Use refresh token to get new access token**:
```bash
# POST /auth/refresh
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your-refresh-token-here"}'
```

**2. Or log in again**:
```bash
# POST /auth/login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPass123!"}'
```

---

## Performance Issues

### Slow API Response Times (>2s)

**Diagnosis**:
```bash
# Check backend logs for slow queries
docker-compose logs backend | grep "slow query"

# Profile with curl
time curl http://localhost:8000/api/users/me
```

**Common Causes**:

**1. N+1 Query Problem**:
- Check SQLAlchemy relationships use `lazy='joined'` or eager loading
- Add `selectinload()` or `joinedload()` in queries

**2. Missing Database Indexes**:
```sql
-- Check for missing indexes
EXPLAIN ANALYZE SELECT * FROM trips WHERE user_id = '...';

-- Add index if needed (via Alembic migration)
CREATE INDEX idx_trips_user_id ON trips(user_id);
```

**3. Large Response Payloads**:
- Use pagination (`limit` and `offset` query params)
- Exclude unnecessary fields from response schemas

---

### High Memory Usage (>2 GB)

**Diagnosis**:
```bash
# Check memory usage
docker stats

# Linux
free -h

# Mac
vm_stat

# Windows
Get-Process | Sort-Object WS -Descending | Select-Object -First 10
```

**Solutions**:

**1. Limit Docker resources**:
```bash
# Docker Desktop → Settings → Resources
# Set CPU limit: 2-4 cores
# Set Memory limit: 2-4 GB
```

**2. Clean up unused containers**:
```bash
docker system prune -a
```

**3. Use production build** (instead of dev):
```bash
# Dev mode uses source maps and hot reload (memory-intensive)
# Use local-prod for testing without dev overhead
./deploy-local-prod.sh
```

---

## Quick Diagnosis Guide

**Use this flowchart to quickly identify the problem category:**

### 1. Check Service Health

```bash
# If using Docker
docker-compose ps

# Expected: All services "Up (healthy)"
# If any service is down or unhealthy → See [Docker Issues](#docker-issues)
```

### 2. Check Port Availability

```bash
# Linux/Mac
lsof -ti:8000  # Backend
lsof -ti:5173  # Frontend
lsof -ti:5432  # PostgreSQL

# If port in use → See [Port Conflicts](#port-conflicts)
```

### 3. Check Logs for Errors

```bash
# local-dev (no Docker)
# Check terminal output where you ran ./run-local-dev.sh

# Docker modes
docker-compose logs backend
docker-compose logs db
docker-compose logs frontend-dev

# Look for keywords: ERROR, FATAL, exception, failed
```

### 4. Test API Directly

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status": "healthy", ...}
# If error → See [Database Errors](#database-errors)

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPass123!"}'

# Expected: {"access_token": "...", ...}
# If 401 → See [Authentication & API Issues](#authentication--api-issues)
```

### 5. Frontend Specific Issues

```bash
# Open browser DevTools (F12)
# Check Console tab for errors

# Common error patterns:
# - "CORS" → See [CORS Errors](#cors-errors-in-browser-console)
# - "404" → See [Assets Not Loading](#assets-not-loading-404-errors)
# - "Network error" → Check backend is running
```

---

## Emergency Reset Procedures

### Complete Reset (Local Development)

**⚠️ WARNING**: This deletes ALL local data, settings, and databases

**SQLite (local-dev)**:
```bash
# Delete everything
rm backend/contravento_dev.db
rm backend/.env
rm -rf backend/.venv
rm -rf frontend/node_modules

# Start fresh
./run-local-dev.sh --setup
./run-local-dev.sh --with-frontend
```

**Docker (local-minimal, local-full)**:
```bash
# Stop and remove all containers, volumes, networks
docker-compose down -v

# Remove all ContraVento images
docker images | grep contravento | awk '{print $3}' | xargs docker rmi -f

# Remove environment files (optional)
rm .env.local .env.local-minimal

# Start fresh
cp .env.local.example .env.local
./deploy.sh local
```

---

### Partial Reset (Keep Data, Reset Code)

**Backend Only**:
```bash
cd backend

# Delete virtual environment
rm -rf .venv

# Reinstall dependencies
poetry install

# Restart server
./run-local-dev.sh
```

**Frontend Only**:
```bash
cd frontend

# Delete node_modules
rm -rf node_modules package-lock.json

# Clear cache
npm cache clean --force

# Reinstall dependencies
npm install

# Restart dev server
npm run dev
```

---

## See Also

- **[Getting Started](getting-started.md)** - Initial setup and verification
- **[Environment Variables](environment-variables.md)** - Configuration reference
- **[Docker Compose Guide](docker-compose-guide.md)** - Understanding the Docker stack
- **[Deployment Modes](../README.md#deployment-modes)** - Mode-specific troubleshooting

---

## Still Need Help?

If none of these solutions work:

1. **Check mode-specific troubleshooting**:
   - [local-dev](../modes/local-dev.md#troubleshooting)
   - [local-minimal](../modes/local-minimal.md#troubleshooting)
   - [local-full](../modes/local-full.md#troubleshooting)
   - [local-prod](../modes/local-prod.md#troubleshooting)

2. **Search existing issues**: [GitHub Issues](https://github.com/your-org/contravento-application-python/issues)

3. **Ask in team chat** with:
   - Deployment mode (e.g., local-dev, local-full)
   - OS (Windows, Mac, Linux)
   - Error message (full text)
   - Steps to reproduce

4. **Open a new issue** with the bug report template

---

**Last Updated**: 2026-02-06

**Feedback**: Found a solution not listed here? [Open a PR](https://github.com/your-org/contravento-application-python/pulls) to add it!
