# PostgreSQL Quick Start Guide

This guide helps you set up PostgreSQL for ContraVento using Docker.

---

## Prerequisites

- Docker Desktop installed and running
- Poetry installed
- Backend dependencies installed (`poetry install`)

---

## 1. Start PostgreSQL Container

```bash
# From project root
docker-compose up -d postgres
```

This will:
- Pull `postgres:16-alpine` image
- Create container named `contravento-db`
- Expose port `5432`
- Run `init-db.sql` script (enables UUID extensions)
- Create volume `postgres_data` for persistence

**Verify container is running:**
```bash
docker ps | grep contravento-db
```

---

## 2. Configure Environment

Create `.env` file in `backend/` directory:

```bash
cd backend
cp .env.example .env
```

**Edit `.env` and update DATABASE_URL:**

```bash
# Change from SQLite:
# DATABASE_URL=sqlite+aiosqlite:///./contravento_dev.db

# To PostgreSQL:
DATABASE_URL=postgresql+asyncpg://contravento_user:changeme_in_production@localhost:5432/contravento
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and update `SECRET_KEY` in `.env`.

---

## 3. Run Database Migrations

```bash
cd backend

# Apply all migrations (creates tables, indexes, constraints)
poetry run alembic upgrade head

# Verify migrations applied
poetry run alembic current
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_auth_schema
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_add_privacy_settings
...
INFO  [alembic.runtime.migration] Running upgrade 005 -> 006_trip_tags_association
```

---

## 4. Seed Initial Data

**Seed Achievements:**
```bash
poetry run python scripts/seed_achievements.py
```

This creates 9 predefined achievements:
- FIRST_TRIP, CENTURY, VOYAGER, EXPLORER, PHOTOGRAPHER, GLOBETROTTER, MARATHONER, INFLUENCER, PROLIFIC

**Create Test User:**
```bash
poetry run python scripts/create_verified_user.py
```

Default credentials:
- Username: `testuser`
- Email: `test@example.com`
- Password: `TestPass123!`

---

## 5. Verify Setup

```bash
# Run verification script
bash scripts/verify-postgres.sh
```

This checks:
- Docker is running
- PostgreSQL container is healthy
- Extensions are enabled
- Migrations are applied
- Lists current tables

---

## 6. Start Backend Server

```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify API is running:**
- API Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## 7. Test API Endpoints

**Login with test user:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "user": {
      "user_id": "...",
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

---

## Database Management

### View Tables

```bash
docker exec -it contravento-db psql -U contravento_user -d contravento -c "\dt"
```

### Connect to PostgreSQL CLI

```bash
docker exec -it contravento-db psql -U contravento_user -d contravento
```

**Useful commands:**
- `\dt` - List tables
- `\d table_name` - Describe table schema
- `\q` - Quit

### View Logs

```bash
docker logs contravento-db
```

### Stop PostgreSQL

```bash
docker-compose stop postgres
```

### Restart PostgreSQL

```bash
docker-compose restart postgres
```

### Reset Database (DELETE ALL DATA)

```bash
# Stop and remove container + volume
docker-compose down -v

# Recreate from scratch
docker-compose up -d postgres
cd backend
poetry run alembic upgrade head
poetry run python scripts/seed_achievements.py
```

---

## Troubleshooting

### Connection Refused

**Symptom**: `psycopg.OperationalError: connection refused`

**Solution**:
```bash
# Check if container is running
docker ps | grep contravento-db

# Check logs for errors
docker logs contravento-db

# Restart container
docker-compose restart postgres
```

### Migrations Fail

**Symptom**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solution**:
```bash
# Check current revision
poetry run alembic current

# Downgrade to base (CAUTION: deletes data)
poetry run alembic downgrade base

# Re-apply all migrations
poetry run alembic upgrade head
```

### Port 5432 Already in Use

**Symptom**: `Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use`

**Solution**:
```bash
# Check what's using port 5432
# Windows:
netstat -ano | findstr :5432

# Linux/Mac:
lsof -i :5432

# Stop other PostgreSQL instance or change port in docker-compose.yml
```

### Cannot Connect from Host

**Symptom**: Application can't connect to PostgreSQL

**Solution**:
1. Verify `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://contravento_user:changeme_in_production@localhost:5432/contravento
   ```

2. Check container network:
   ```bash
   docker inspect contravento-db | grep IPAddress
   ```

3. Test connection manually:
   ```bash
   docker exec contravento-db pg_isready -U contravento_user -d contravento
   ```

---

## Production Deployment

### Update .env for Production

```bash
# Use strong password
DATABASE_URL=postgresql+asyncpg://contravento_user:STRONG_PASSWORD_HERE@postgres:5432/contravento

# Change postgres to actual hostname in production
# localhost → works when running backend outside Docker
# postgres → works when running backend inside Docker (docker-compose)
```

### Enable Connection Pooling

PostgreSQL connection pool is configured in `src/database.py`:
- Pool size: 20 connections
- Max overflow: 10 connections
- Recycle time: 3600 seconds (1 hour)

No changes needed for production.

### Backup Database

```bash
# Create backup
docker exec contravento-db pg_dump -U contravento_user contravento > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker exec -i contravento-db psql -U contravento_user -d contravento < backup_20251231_120000.sql
```

### Automated Backups

Add to crontab (Linux/Mac):
```bash
# Daily backup at 2 AM
0 2 * * * docker exec contravento-db pg_dump -U contravento_user contravento > /backups/contravento_$(date +\%Y\%m\%d).sql
```

---

## Using pgAdmin (Optional)

pgAdmin is included in docker-compose for database management UI.

**Start pgAdmin:**
```bash
docker-compose --profile development up -d pgadmin
```

**Access pgAdmin:**
- URL: http://localhost:5050
- Email: `admin@contravento.com`
- Password: `admin` (change in docker-compose.yml for production)

**Add Server:**
1. Right-click "Servers" → Create → Server
2. General tab:
   - Name: `ContraVento Local`
3. Connection tab:
   - Host: `postgres` (or `localhost` if pgAdmin not in Docker)
   - Port: `5432`
   - Database: `contravento`
   - Username: `contravento_user`
   - Password: `changeme_in_production`

---

## Next Steps

- ✅ PostgreSQL running
- ✅ Migrations applied
- ✅ Test user created
- ✅ Backend API running

**Now you can:**
1. Test API endpoints with Postman/curl
2. Run integration tests: `poetry run pytest tests/integration/`
3. Develop new features
4. Deploy to production (see MVP_RELEASE_NOTES.md)

---

## Additional Resources

- **Alembic Migrations**: `backend/src/migrations/versions/`
- **Database Models**: `backend/src/models/`
- **Environment Config**: `backend/.env.example`
- **Docker Compose**: `docker-compose.yml`
- **Deployment Guide**: `backend/docs/DEPLOYMENT.md`

---

**Last Updated**: 2025-12-31
