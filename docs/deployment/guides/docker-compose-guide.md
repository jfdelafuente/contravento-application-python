# Docker Compose Architecture Guide

**Understanding how ContraVento services connect and communicate**

**Purpose**: Deep dive into Docker Compose stack architecture, networking, volumes, and service dependencies

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Service Dependencies](#service-dependencies)
3. [Networking](#networking)
4. [Volume Management](#volume-management)
5. [Health Checks](#health-checks)
6. [Overlay Pattern](#overlay-pattern)
7. [Common Commands](#common-commands)
8. [Debugging Services](#debugging-services)

---

## Architecture Overview

ContraVento uses Docker Compose to orchestrate multiple services that work together to provide the full platform.

### Full Stack Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ContraVento Docker Stack                        │
└─────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │  Frontend   │          │  Backend    │          │   Redis     │
    │  (Nginx)    │◄────────►│  (FastAPI)  │◄────────►│   Cache     │
    │  Port 5173  │          │  Port 8000  │          │  Port 6379  │
    └─────────────┘          └──────┬──────┘          └─────────────┘
                                    │
                                    │ SQL queries
                                    ▼
                            ┌───────────────┐
                            │  PostgreSQL   │
                            │   Database    │
                            │  Port 5432    │
                            └───────────────┘

    ┌─────────────┐          ┌─────────────┐
    │  MailHog    │          │   pgAdmin   │
    │  SMTP Mock  │          │  Database   │
    │  Port 8025  │          │     UI      │
    └─────────────┘          │  Port 5050  │
                             └─────────────┘

             All connected via: contravento-network (bridge)
```

### Service Roles

| Service | Role | Purpose | Always On? |
|---------|------|---------|------------|
| **postgres** | Database | Persistent data storage | ✅ Yes |
| **backend** | API Server | Business logic, REST API | ✅ Yes |
| **redis** | Cache | Session storage, caching | Mode-dependent |
| **frontend-dev** | Dev Server | Vite hot reload (dev) | Dev only |
| **frontend** | Web Server | Nginx static files (prod) | Prod only |
| **mailhog** | Email Testing | SMTP mock + UI | Dev only |
| **pgadmin** | Database UI | Visual DB management | Optional |

---

## Service Dependencies

### Dependency Chain

Services start in order based on `depends_on` declarations:

```
Level 1 (No dependencies):
  └─ postgres
  └─ redis

Level 2 (Depends on Level 1):
  └─ backend (waits for postgres healthy)

Level 3 (Depends on Level 2):
  └─ frontend-dev / frontend (optional, depends on backend)
  └─ mailhog (no dependencies)
  └─ pgadmin (waits for postgres)
```

**Example from docker-compose.yml**:

```yaml
backend:
  depends_on:
    postgres:
      condition: service_healthy  # Wait for postgres health check
```

**Why this matters**:
- Backend won't start until PostgreSQL is healthy
- Prevents "connection refused" errors on startup
- Ensures correct initialization order

---

### Health Check-Based Dependencies

ContraVento uses **condition-based dependencies** (not just existence):

```yaml
# ❌ BAD - Just waits for container to exist
depends_on:
  - postgres

# ✅ GOOD - Waits for service to be healthy
depends_on:
  postgres:
    condition: service_healthy
```

**Benefits**:
- Backend starts only when database accepts connections
- Reduces startup failures
- No need for manual retry logic

---

## Networking

### Bridge Network

All services communicate through a **dedicated bridge network**:

```yaml
networks:
  contravento-network:
    driver: bridge
```

**Key Properties**:
- **Isolated**: Services only see each other, not other Docker networks
- **DNS-based**: Services resolve each other by name (e.g., `postgres`, `backend`)
- **Automatic**: No manual IP configuration needed

### Service Resolution

Services use container names as hostnames:

```env
# In backend container
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/contravento
#                                          ^^^^^^^^
#                                        DNS name (not localhost!)

REDIS_URL=redis://redis:6379
#                 ^^^^^
#                 DNS name
```

**Common Mistake**:
```env
# ❌ WRONG - Won't work from inside backend container
DATABASE_URL=postgresql://user:pass@localhost:5432/contravento

# ✅ CORRECT - Uses Docker DNS
DATABASE_URL=postgresql://user:pass@postgres:5432/contravento
```

---

### Port Mapping

Ports are mapped from **container → host**:

```yaml
services:
  backend:
    ports:
      - "8000:8000"
      #  ^^^^  ^^^^
      #  host  container
```

**Port Mapping Table**:

| Service | Container Port | Host Port | Purpose |
|---------|----------------|-----------|---------|
| backend | 8000 | 8000 | API access from host |
| frontend-dev | 5173 | 5173 | Vite dev server |
| postgres | 5432 | 5432 | DB clients (DBeaver, psql) |
| redis | 6379 | 6379 | Redis clients |
| mailhog | 1025, 8025 | 8025 | SMTP + Web UI |
| pgadmin | 80 | 5050 | Web UI |

**Internal Communication**:
Services communicate on **container ports** (e.g., backend connects to `postgres:5432`, not `localhost:5432`).

**External Access**:
Host machine accesses services on **host ports** (e.g., browser opens `localhost:8000`).

---

## Volume Management

### Types of Volumes

ContraVento uses two volume types:

#### 1. Named Volumes (Persistent Data)

Managed by Docker, survive container removal:

```yaml
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  backend_storage:
    driver: local
  pgadmin_data:
    driver: local

services:
  postgres:
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**Characteristics**:
- **Persistent**: Data survives `docker-compose down`
- **Managed**: Docker handles storage location
- **Portable**: Can be backed up with `docker run --volumes-from`

**When to use**:
- Database files (PostgreSQL, Redis)
- Uploaded files (profile photos, trip photos)
- Application data that must persist

---

#### 2. Bind Mounts (Development)

Mount host directories into container:

```yaml
services:
  backend:
    volumes:
      - ./backend/src:/app/src:ro           # Read-only source code
      - ./backend/storage:/app/storage      # Read-write uploads
```

**Characteristics**:
- **Live sync**: Changes on host instantly visible in container
- **Hot reload**: Enable development without rebuilds
- **Editable**: Modify files with host editor (VS Code, etc.)

**Flags**:
- `:ro` = Read-only (container can't modify)
- `:rw` = Read-write (default)

**When to use**:
- Development mode (source code, hot reload)
- Accessing logs/uploads from host
- Testing configuration changes

---

### Volume Lifecycle

**Creating volumes**:
```bash
# Automatic on first `docker-compose up`
docker-compose up -d
```

**Listing volumes**:
```bash
docker volume ls | grep contravento
# contravento_postgres_data
# contravento_redis_data
# contravento_backend_storage
# contravento_pgadmin_data
```

**Inspecting volume location**:
```bash
docker volume inspect contravento_postgres_data
# "Mountpoint": "/var/lib/docker/volumes/contravento_postgres_data/_data"
```

**Backing up volume**:
```bash
# Backup PostgreSQL data
docker run --rm \
  -v contravento_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

**Restoring volume**:
```bash
# Restore PostgreSQL data
docker run --rm \
  -v contravento_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

**Deleting volumes**:
```bash
# Remove volumes (⚠️ deletes all data!)
docker-compose down -v

# Or remove specific volume
docker volume rm contravento_postgres_data
```

---

## Health Checks

### Purpose

Health checks tell Docker when a service is **ready** (not just running):

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s        # Check every 30 seconds
    timeout: 10s         # Fail if check takes >10s
    retries: 3           # Try 3 times before marking unhealthy
    start_period: 40s    # Grace period (ignore failures first 40s)
```

**States**:
- `starting`: During `start_period`, failures don't count
- `healthy`: Check succeeded
- `unhealthy`: Check failed `retries` times

---

### Health Check Examples

**PostgreSQL**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Backend API**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # Allow time for DB migrations
```

**Redis**:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
  interval: 10s
  timeout: 5s
  retries: 5
```

---

### Checking Health Status

```bash
# View health status
docker-compose ps

# Example output:
# NAME                STATUS         PORTS
# contravento-db      Up (healthy)   5432/tcp
# contravento-api     Up (healthy)   0.0.0.0:8000->8000/tcp
# contravento-redis   Up (healthy)   6379/tcp

# View detailed health check logs
docker inspect --format='{{json .State.Health}}' contravento-api | jq
```

---

## Overlay Pattern

ContraVento uses **overlay files** to customize configuration per environment:

### Base + Overlay Structure

```
docker-compose.yml                   # Base (common services)
docker-compose.local.yml             # Local dev overrides
docker-compose.local-minimal.yml     # Minimal dev overrides
docker-compose.staging.yml           # Staging overrides
docker-compose.prod.yml              # Production overrides
```

**How it works**:
```bash
# Compose merges base + overlay
docker-compose -f docker-compose.yml -f docker-compose.local.yml up

# Deployment scripts do this automatically:
./deploy.sh local          # Uses base + local.yml
./deploy.sh staging        # Uses base + staging.yml
./deploy.sh prod           # Uses base + prod.yml
```

---

### Override Examples

**Base (docker-compose.yml)** defines common structure:
```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      APP_ENV: ${APP_ENV}
      DEBUG: ${DEBUG:-false}
    volumes:
      - backend_storage:/app/storage
```

**Local overlay (docker-compose.local.yml)** adds development features:
```yaml
services:
  backend:
    build:
      target: development       # Different build stage
    volumes:
      - ./backend/src:/app/src:ro  # Add source code mount
    environment:
      DEBUG: "true"             # Override DEBUG
      LOG_LEVEL: DEBUG          # Add new variable
```

**Result when merged**:
```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development       # From overlay
    environment:
      APP_ENV: ${APP_ENV}
      DEBUG: "true"             # Overridden from overlay
      LOG_LEVEL: DEBUG          # Added from overlay
    volumes:
      - backend_storage:/app/storage      # From base
      - ./backend/src:/app/src:ro         # Added from overlay
```

---

### Common Override Patterns

**1. Add/remove services**:
```yaml
# local.yml - Add MailHog for email testing
services:
  mailhog:
    image: mailhog/mailhog
    ports:
      - "8025:8025"
```

**2. Change ports**:
```yaml
# staging.yml - Use different host port
services:
  backend:
    ports:
      - "8001:8000"  # Avoid conflict with local dev
```

**3. Override build target**:
```yaml
# local.yml - Use development Dockerfile stage
services:
  backend:
    build:
      target: development

# prod.yml - Use production Dockerfile stage
services:
  backend:
    build:
      target: production
```

**4. Add bind mounts**:
```yaml
# local.yml - Mount source code for hot reload
services:
  backend:
    volumes:
      - ./backend/src:/app/src:ro
```

---

## Common Commands

### Starting Services

```bash
# Start all services (detached)
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Start with specific overlay
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

# Start and view logs (foreground)
docker-compose up
```

---

### Viewing Logs

```bash
# All services
docker-compose logs

# Follow logs (tail -f)
docker-compose logs -f

# Specific service
docker-compose logs backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00 backend
```

---

### Stopping Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Stop specific service
docker-compose stop backend

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop and remove containers + volumes (⚠️ deletes data!)
docker-compose down -v

# Stop and remove containers + images
docker-compose down --rmi all
```

---

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Restart with rebuild
docker-compose up -d --build backend
```

---

### Executing Commands in Containers

```bash
# Run command in running container
docker-compose exec backend poetry run pytest

# Open shell in container
docker-compose exec backend sh

# Run command as different user
docker-compose exec -u root backend sh

# Run one-off command (creates new container)
docker-compose run --rm backend poetry run alembic upgrade head
```

---

### Inspecting Services

```bash
# List running containers
docker-compose ps

# View service configuration (after merging overlays)
docker-compose config

# View specific service config
docker-compose config backend

# Check service health
docker-compose ps
docker inspect --format='{{json .State.Health}}' contravento-api
```

---

### Rebuilding Services

```bash
# Rebuild all services
docker-compose build

# Rebuild without cache (clean build)
docker-compose build --no-cache

# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build
```

---

## Debugging Services

### Service Won't Start

**Check logs**:
```bash
docker-compose logs backend

# Look for:
# - Database connection errors
# - Missing environment variables
# - Port conflicts
# - Permission errors
```

**Check health status**:
```bash
docker-compose ps

# If "unhealthy", inspect health check:
docker inspect --format='{{json .State.Health}}' contravento-api | jq
```

**Check dependencies**:
```bash
# Ensure postgres is healthy before backend starts
docker-compose ps postgres

# If postgres unhealthy, check its logs:
docker-compose logs postgres
```

---

### Database Connection Issues

**Verify DATABASE_URL**:
```bash
# Check environment variable in container
docker-compose exec backend env | grep DATABASE_URL

# Should use container name, not localhost:
# DATABASE_URL=postgresql://user:pass@postgres:5432/db  # ✅ Correct
# DATABASE_URL=postgresql://user:pass@localhost:5432/db # ❌ Wrong
```

**Test connection manually**:
```bash
# From host (using port mapping)
psql postgresql://user:pass@localhost:5432/contravento

# From backend container (using container name)
docker-compose exec backend sh
$ psql $DATABASE_URL
```

---

### Network Issues

**List networks**:
```bash
docker network ls | grep contravento
```

**Inspect network**:
```bash
docker network inspect contravento_contravento-network

# Shows:
# - Connected containers
# - IP addresses
# - Subnet
```

**Test connectivity between services**:
```bash
# From backend, ping postgres
docker-compose exec backend ping postgres

# From backend, test PostgreSQL port
docker-compose exec backend nc -zv postgres 5432
```

---

### Volume Issues

**List volumes**:
```bash
docker volume ls | grep contravento
```

**Inspect volume**:
```bash
docker volume inspect contravento_postgres_data

# Check "Mountpoint" for physical location
```

**Check volume contents**:
```bash
# List files in postgres_data volume
docker run --rm -v contravento_postgres_data:/data alpine ls -la /data
```

**Reset volume** (⚠️ deletes data):
```bash
docker-compose down -v
docker-compose up -d
```

---

### Performance Issues

**Check resource usage**:
```bash
docker stats

# Shows:
# - CPU %
# - Memory usage
# - Network I/O
# - Disk I/O
```

**Limit resources** (in docker-compose.yml):
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Best Practices

### 1. Always Use Health Checks

```yaml
# ✅ GOOD - Service marked healthy only when ready
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]

# ❌ BAD - No health check, backend may start before DB ready
backend:
  # No healthcheck defined
```

---

### 2. Use Condition-Based Dependencies

```yaml
# ✅ GOOD - Wait for postgres to be healthy
backend:
  depends_on:
    postgres:
      condition: service_healthy

# ❌ BAD - Only waits for postgres container to exist
backend:
  depends_on:
    - postgres
```

---

### 3. Name Containers Consistently

```yaml
# ✅ GOOD - Environment-specific names
postgres:
  container_name: contravento-db-${APP_ENV:-local}

# ❌ BAD - Hardcoded name (can't run multiple environments)
postgres:
  container_name: contravento-db
```

---

### 4. Use Named Volumes for Data

```yaml
# ✅ GOOD - Named volume (survives container removal)
postgres:
  volumes:
    - postgres_data:/var/lib/postgresql/data

# ❌ BAD - Anonymous volume (deleted when container removed)
postgres:
  volumes:
    - /var/lib/postgresql/data
```

---

### 5. Bind Mount Source Code (Dev Only)

```yaml
# ✅ GOOD - Read-only mount prevents accidental changes
backend:
  volumes:
    - ./backend/src:/app/src:ro

# ❌ BAD - Read-write mount (container could modify source)
backend:
  volumes:
    - ./backend/src:/app/src
```

---

## See Also

- **[Getting Started](getting-started.md)** - Initial setup with Docker Compose
- **[Troubleshooting](troubleshooting.md)** - Docker-specific troubleshooting
- **[Environment Variables](environment-variables.md)** - Configuration reference
- **[Deployment Modes](../README.md)** - Which docker-compose file for which mode

---

**Last Updated**: 2026-02-06

**Source**: Extracted from `docker-compose.yml` and mode-specific overlays

**Feedback**: Found incorrect architecture details? [Open an issue](https://github.com/your-org/contravento-application-python/issues)
