# Common Issues - Troubleshooting Guide

Quick fixes and solutions for common development issues in ContraVento.

**Audience**: Developers (all levels)

---

## Table of Contents

- [Server Issues](#server-issues)
- [Database Issues](#database-issues)
- [Dependency Issues](#dependency-issues)
- [Testing Issues](#testing-issues)
- [Frontend Issues](#frontend-issues)
- [GPX Upload Issues](#gpx-upload-issues)
- [Authentication Issues](#authentication-issues)
- [Email Testing Issues](#email-testing-issues)

---

## Server Issues

### Port 8000 Already in Use

**Error**:
```
ERROR:    [Errno 48] Address already in use
ERROR:    [Errno 98] Address already in use (Linux)
```

**Cause**: Another process (previous uvicorn instance) is using port 8000.

**Solution**:

**Linux/Mac**:
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Alternative: Kill by name
pkill -f uvicorn

# Verify port is free
lsof -i:8000
```

**Windows PowerShell**:
```powershell
# Find and kill process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# Alternative: Use netstat to find PID
netstat -ano | findstr :8000
# Then kill by PID
taskkill /PID <PID> /F
```

**Prevention**:
- Always stop servers with `Ctrl+C` (sends SIGTERM)
- Use `./run_backend.sh stop` to ensure clean shutdown
- Check for hanging processes before starting: `lsof -i:8000`

---

### Backend Not Responding (Hangs)

**Symptoms**:
- API requests timeout
- No response from http://localhost:8000
- Logs show no activity

**Possible Causes**:

**1. Database Connection Pool Exhausted**

Check logs for:
```
sqlalchemy.exc.TimeoutError: QueuePool limit of size 20 overflow 10 reached
```

**Solution**:
```bash
# Restart backend
./run_backend.sh restart

# If persists, check for unclosed database sessions in code
# All async functions must properly close sessions
```

**2. Infinite Loop in Code**

**Solution**:
```bash
# Find process PID
ps aux | grep uvicorn

# Attach debugger or check logs
tail -f logs/backend.log

# Kill and restart
pkill -f uvicorn
./run_backend.sh start
```

**3. Migration Lock**

**Solution**:
```bash
cd backend

# Check for stale Alembic lock
poetry run alembic current

# If stuck, remove lock (PostgreSQL only)
poetry run alembic stamp head

# Retry migration
poetry run alembic upgrade head
```

---

### Hot Reload Not Working

**Symptoms**:
- Code changes don't trigger server restart
- Must manually restart uvicorn to see changes

**Cause**: Uvicorn `--reload` flag missing or file watcher issues.

**Solution**:

**Check if reload is enabled**:
```bash
# Should see --reload in command
ps aux | grep uvicorn
```

**Restart with reload explicitly**:
```bash
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**File watcher issues (Mac with watchdog)**:
```bash
# Install watchdog for better file watching
poetry add --dev watchdog

# Restart uvicorn
```

**WSL2 (Windows Subsystem for Linux) issues**:
- File changes in Windows filesystem not detected by WSL
- **Solution**: Move project to WSL filesystem (`/home/user/...`)

---

## Database Issues

See **[Database Issues](database-issues.md)** for detailed database troubleshooting.

### Quick Fixes

**Reset SQLite database**:
```bash
./run-local-dev.sh --reset
```

**Check database connection**:
```bash
cd backend

# SQLite - check if file exists
ls -lh contravento_dev.db

# PostgreSQL - test connection
poetry run python -c "
from src.database import engine
import asyncio
async def test():
    async with engine.begin() as conn:
        print('Connection OK')
asyncio.run(test())
"
```

**View current migration status**:
```bash
cd backend
poetry run alembic current
poetry run alembic history
```

---

## Dependency Issues

### Poetry Install Fails

**Error**:
```
SolverProblemError: Package 'fastapi' has no compatible versions
Unable to find installation candidates for package
```

**Cause**: Poetry cache corruption or version conflicts.

**Solution**:

**1. Clear Poetry cache**:
```bash
cd backend

# Clear all caches
poetry cache clear pypi --all
poetry cache clear PyPI --all  # Case-sensitive on some systems

# Reinstall
poetry install
```

**2. Update lock file**:
```bash
# Update all dependencies
poetry update

# Or update specific package
poetry update fastapi
```

**3. Remove and recreate virtual environment**:
```bash
# Remove existing virtualenv
rm -rf $(poetry env info --path)

# Reinstall
poetry install
```

**4. Check Python version**:
```bash
# Verify Python 3.12+
python --version

# Ensure Poetry uses correct Python
poetry env use python3.12
poetry install
```

---

### Missing Dependencies

**Error**:
```
ModuleNotFoundError: No module named 'fastapi'
ImportError: cannot import name 'AsyncSession' from 'sqlalchemy.ext.asyncio'
```

**Cause**: Running Python outside Poetry environment.

**Solution**:

**Always use Poetry**:
```bash
# WRONG
python src/main.py

# CORRECT
poetry run python src/main.py
poetry run uvicorn src.main:app
```

**Activate Poetry shell** (optional):
```bash
# Enter Poetry virtualenv
poetry shell

# Now can run without 'poetry run'
python src/main.py
uvicorn src.main:app --reload

# Exit shell
exit
```

**Verify environment**:
```bash
# Show virtualenv path
poetry env info

# List installed packages
poetry show
```

---

### Dependency Version Conflicts

**Error**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**Cause**: Conflicting version requirements between packages.

**Solution**:

**1. Check dependency tree**:
```bash
poetry show --tree
```

**2. Identify conflict**:
```bash
# Example: fastapi requires pydantic>=2.0, but other package needs <2.0
poetry show pydantic
```

**3. Resolve manually**:
```bash
# Edit pyproject.toml
# Change version constraint to compatible range
# fastapi = "^0.109.0"
# pydantic = "^2.5.3"  # Must be compatible with fastapi

# Update lock file
poetry lock --no-update
poetry install
```

---

## Testing Issues

### Tests Failing: Database Errors

**Error**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
```

**Cause**: Test database not initialized or migrations not applied.

**Solution**:

**Use in-memory SQLite**:
```python
# tests/conftest.py
@pytest.fixture
async def db_session():
    # Create in-memory database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Apply migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # ... rest of fixture
```

**Or reset test database before tests**:
```bash
# Reset SQLite test database
rm backend/contravento_test.db
poetry run alembic upgrade head

# Run tests
poetry run pytest
```

---

### Tests Failing: Coverage Below 90%

**Error**:
```
FAILED - Required test coverage of 90% not reached. Total coverage: 87.5%
```

**Solution**:

**1. Generate HTML coverage report**:
```bash
cd backend
poetry run pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**2. Identify uncovered lines**:
- Red lines = not covered
- Yellow lines = partially covered
- Green lines = fully covered

**3. Write tests for uncovered code**:
```python
# Example: Uncovered error handling
async def delete_trip(trip_id: str, user_id: str) -> None:
    # ❌ Line 45 not covered (error case)
    if not trip:
        raise HTTPException(404, "Trip not found")

# Write test
async def test_delete_trip_not_found(db_session):
    """Test deleting non-existent trip raises 404."""
    with pytest.raises(HTTPException) as exc:
        await delete_trip("invalid-id", "user123")
    assert exc.value.status_code == 404
```

**4. Re-run coverage**:
```bash
poetry run pytest --cov=src --cov-fail-under=90
```

---

### Pytest Fixtures Not Found

**Error**:
```
fixture 'db_session' not found
```

**Cause**: `conftest.py` not in correct location or not imported.

**Solution**:

**Verify conftest.py location**:
```
backend/
  tests/
    conftest.py          ← Must be here
    unit/
      test_auth.py       ← Can use db_session fixture
    integration/
      test_trips.py      ← Can use db_session fixture
```

**Check fixture scope**:
```python
# conftest.py
@pytest.fixture(scope="function")  # New instance per test
async def db_session():
    pass

@pytest.fixture(scope="module")   # Shared within module
async def db_session():
    pass
```

**Import fixture explicitly** (if needed):
```python
# test_auth.py
from tests.conftest import db_session  # Usually not needed

async def test_register(db_session):  # Pytest auto-discovers
    pass
```

---

## Frontend Issues

### Frontend Not Loading (Blank Page)

**Symptoms**:
- http://localhost:5173 shows blank page
- No console errors
- Vite dev server running

**Solution**:

**1. Check browser console**:
- Open DevTools (F12)
- Check for JavaScript errors
- Check Network tab for failed requests

**2. Clear Vite cache**:
```bash
cd frontend

# Clear node_modules and cache
rm -rf node_modules .vite dist

# Reinstall
npm install

# Restart
npm run dev
```

**3. Check API connection**:
```bash
# Test backend from browser console
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
```

---

### CORS Errors in Browser

**Error**:
```
Access to fetch at 'http://localhost:8000/auth/login' from origin 'http://localhost:5173'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

**Cause**: Backend CORS not configured for frontend origin.

**Solution**:

**Check backend .env**:
```bash
# backend/.env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Verify CORS middleware** (in `src/main.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Restart backend**:
```bash
./run_backend.sh restart
```

---

### React Component Not Re-rendering

**Symptoms**:
- Data updates in state but UI doesn't change
- `useState` or `useEffect` not triggering

**Common Causes**:

**1. Mutating state directly**:
```typescript
// ❌ WRONG - Mutates array
const [trips, setTrips] = useState<Trip[]>([]);
trips.push(newTrip);  // React doesn't detect change

// ✅ CORRECT - Creates new array
setTrips([...trips, newTrip]);
setTrips(prev => [...prev, newTrip]);
```

**2. Missing dependency in useEffect**:
```typescript
// ❌ WRONG - Missing dependency
useEffect(() => {
  fetchTrips(username);
}, []);  // username not in deps

// ✅ CORRECT
useEffect(() => {
  fetchTrips(username);
}, [username]);
```

**3. Object reference not changing**:
```typescript
// ❌ WRONG - Same object reference
const [user, setUser] = useState<User>(initialUser);
user.name = "New Name";  // No re-render
setUser(user);

// ✅ CORRECT - New object
setUser({ ...user, name: "New Name" });
```

---

## GPX Upload Issues

### GPX File Upload Fails (413 Payload Too Large)

**Error**:
```
413 Request Entity Too Large
```

**Cause**: File size exceeds Nginx or backend limit.

**Solution**:

**Check file size**:
```bash
ls -lh route.gpx
# If >10 MB, file is too large for default settings
```

**Backend limit** (in `src/config.py`):
```python
UPLOAD_MAX_SIZE_MB = 10  # 10 MB default
```

**Nginx limit** (if using Docker):
```nginx
# nginx.conf
client_max_body_size 20M;  # Increase from 10M
```

**Temporary workaround**:
- Simplify GPX file in GPS software (reduce trackpoints)
- Use online GPX simplifier tools
- Split long route into segments

---

### GPX Parsing Fails (Invalid File)

**Error**:
```
400 Bad Request: GPX file format invalid
```

**Cause**: Malformed GPX XML or unsupported format.

**Solution**:

**Validate GPX file**:
```bash
# Use gpxpy to validate
cd backend
poetry run python -c "
import gpxpy
with open('route.gpx', 'r') as f:
    gpx = gpxpy.parse(f)
    print(f'Valid GPX: {len(gpx.tracks)} tracks')
"
```

**Common issues**:
- Missing `<trk>` or `<trkpt>` elements
- Invalid latitude/longitude values (must be -90 to 90, -180 to 180)
- Corrupted file (download again from GPS device)

**Check GPX structure**:
```xml
<!-- Valid GPX structure -->
<?xml version="1.0"?>
<gpx version="1.1">
  <trk>
    <name>My Route</name>
    <trkseg>
      <trkpt lat="42.123" lon="-1.456">
        <ele>850.5</ele>
        <time>2024-01-01T10:00:00Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
```

---

### GPX Statistics Incorrect

**Symptoms**:
- Total distance way too high or too low
- Elevation gain negative or unrealistic
- Moving time equals total time (no stops detected)

**Solution**:

**Analyze GPX file**:
```bash
cd backend

# Check segments and stop detection
poetry run python scripts/analysis/analyze_gpx_segments.py --file-path route.gpx

# Diagnose performance and statistics
poetry run python scripts/analysis/diagnose_gpx_performance.py --file-path route.gpx
```

**Common causes**:
1. **GPS drift**: Trackpoints jumping around (increases distance)
   - Solution: Increase Douglas-Peucker epsilon (simplify more)

2. **Missing timestamps**: Can't calculate moving time
   - Solution: Re-export GPX with timestamps from GPS device

3. **Elevation anomalies**: Sudden jumps in elevation (GPS noise)
   - Solution: Backend applies smoothing (see `gpx_service.py`)

---

## Authentication Issues

### Login Returns 401 Unauthorized

**Possible Causes**:

**1. Wrong credentials**:
```bash
# Verify user exists
cd backend
poetry run python scripts/user-mgmt/create_verified_user.py --list

# Or check directly
poetry run python -c "
from src.database import AsyncSessionLocal
from src.models.user import User
from sqlalchemy import select
import asyncio

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == 'testuser'))
        user = result.scalar_one_or_none()
        print(f'User exists: {user is not None}')

asyncio.run(check())
"
```

**2. User not verified**:
```bash
# Verify user manually
poetry run python scripts/user-mgmt/create_verified_user.py --verify-email test@example.com
```

**3. Bcrypt rounds mismatch**:
- Production uses 12 rounds, tests use 4 rounds
- Check `.env` file: `BCRYPT_ROUNDS=4` (development)

---

### JWT Token Expired

**Error**:
```json
{
  "detail": {
    "code": "TOKEN_EXPIRED",
    "message": "Token de autenticación expirado"
  }
}
```

**Cause**: Access token expired (15 min default).

**Solution**:

**Use refresh token**:
```bash
# Get new access token
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

**Frontend (automatic refresh)**:
```typescript
// Interceptor refreshes token automatically
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && !error.config._retry) {
      error.config._retry = true;
      const newToken = await refreshAccessToken();
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return axios.request(error.config);
    }
    return Promise.reject(error);
  }
);
```

---

### HttpOnly Cookie Not Set

**Symptoms**:
- Login succeeds but subsequent requests return 401
- No `access_token` cookie in browser

**Solution**:

**Check browser DevTools**:
1. Open Application tab → Cookies
2. Check for `access_token` cookie on `localhost:5173`
3. Verify `HttpOnly` and `SameSite=Lax` flags

**Backend CORS settings** (must allow credentials):
```python
# src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,  # Required for HttpOnly cookies
    # ...
)
```

**Frontend request** (must include credentials):
```typescript
// Axios configuration
const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,  // Required for HttpOnly cookies
});
```

---

## Email Testing Issues

### Emails Not Appearing in MailHog

**Symptoms**:
- Registration email not received
- Password reset email missing
- MailHog UI shows 0 emails

**Solution**:

**1. Check MailHog is running**:
```bash
# Docker Compose (local-full)
docker ps | grep mailhog

# Should show:
# mailhog:8025->8025/tcp
# mailhog:1025->1025/tcp
```

**2. Verify SMTP settings**:
```bash
# backend/.env (local-dev without Docker)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USE_TLS=false

# Docker (local-full)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USE_TLS=false
```

**3. Check backend logs**:
```bash
# Look for email sending errors
tail -f logs/backend.log | grep -i email
```

**4. Access MailHog UI**:
- http://localhost:8025
- Should show web interface
- If not loading: restart MailHog container

---

### MailHog Not Starting (Docker)

**Error**:
```
ERROR: for mailhog  Cannot start service mailhog: driver failed programming external connectivity on endpoint
```

**Cause**: Port 1025 or 8025 already in use.

**Solution**:
```bash
# Find process using port
lsof -i:8025
lsof -i:1025

# Kill process
kill -9 <PID>

# Restart Docker Compose
./deploy.sh local --restart
```

---

## Related Documentation

- **[Database Issues](database-issues.md)** - Database-specific troubleshooting
- **[Getting Started](../getting-started.md)** - Setup and installation
- **[Scripts Overview](../scripts/overview.md)** - Utility scripts for diagnostics
- **[TDD Workflow](../tdd-workflow.md)** - Testing best practices

---

## Getting Additional Help

### Debugging Checklist

Before asking for help, try:

1. ✅ Check logs (`logs/backend.log`, browser console)
2. ✅ Verify environment variables (`.env` file)
3. ✅ Restart services (`./run_backend.sh restart`)
4. ✅ Check database state (use scripts in `scripts/dev-tools/`)
5. ✅ Clear caches (Poetry cache, Vite cache, browser cache)
6. ✅ Search this troubleshooting guide
7. ✅ Search GitHub Issues (closed and open)

### Reporting Issues

When reporting issues, include:

- **Error message** (full stack trace)
- **Steps to reproduce**
- **Environment details** (OS, Python version, Docker/local-dev)
- **Relevant logs** (backend logs, browser console)
- **Expected vs actual behavior**

**GitHub Issue Template**:
```markdown
## Description
Brief description of the issue

## Steps to Reproduce
1. Start backend with ./run-local-dev.sh
2. Navigate to http://localhost:5173/trips/new
3. Upload GPX file
4. Error occurs

## Expected Behavior
GPX file should upload successfully

## Actual Behavior
Receives 413 Payload Too Large error

## Environment
- OS: macOS 14.2
- Python: 3.12.1
- Environment: local-dev (SQLite)
- Docker: Not using Docker

## Logs
```
[Paste relevant logs here]
```

## Additional Context
File size: 15 MB (too large for default 10 MB limit)
```

---

**Last Updated**: 2026-02-07
**Issue Count**: 20+ common issues documented
**Categories**: 8 (Server, Database, Dependencies, Testing, Frontend, GPX, Auth, Email)
