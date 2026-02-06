# Dev Deployment Mode - Development/Integration Server

**Purpose**: Integration testing environment with production-like build and real SMTP

**Target Users**: Development teams, CI/CD pipelines, integration testing

**Difficulty**: Intermediate

**Estimated Setup Time**: 20-30 minutes

**Prerequisites**:
- Docker 24.0+ and Docker Compose 2.0+
- SSH access to development server (optional, can run locally)
- Real SMTP provider (Mailtrap, Mailgun, or similar)
- Basic understanding of Nginx reverse proxy

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [Common Workflows](#common-workflows)
6. [Troubleshooting](#troubleshooting)
7. [Related Modes](#related-modes)

---

## Overview

### What is Dev Mode?

The **Dev** deployment mode provides an integration testing environment that mirrors production behavior without hot-reload. It's designed for team collaboration, CI/CD validation, and testing production builds before staging deployment.

**Key Characteristics**:
- ✅ Production-like Docker builds (no volume mounts, rebuilt images)
- ✅ Nginx reverse proxy (production configuration)
- ✅ Real SMTP server (Mailtrap, Mailgun, etc.)
- ✅ Structured JSON logging
- ✅ PostgreSQL database
- ✅ Redis cache
- ❌ No debug mode (DEBUG=false)
- ❌ No MailHog (use real SMTP)
- ❌ No pgAdmin (use database tools externally)

### When to Use Dev Mode

**Perfect For**:
- ✅ Integration testing before staging deployment
- ✅ CI/CD pipeline validation
- ✅ Team collaboration environment (shared dev server)
- ✅ Validating production build works correctly
- ✅ Testing with real SMTP without production credentials
- ✅ Verifying Nginx configuration changes

**Not Suitable For**:
- ❌ Daily feature development (use [local-dev](./local-dev.md) instead)
- ❌ Hot-reload debugging (use [local-full](./local-full.md) instead)
- ❌ Final pre-production testing (use [staging](./staging.md) instead)

### Comparison with Other Modes

| Feature | Dev | Local-Full | Staging |
|---------|:---:|:----------:|:-------:|
| **Docker Build** | Production | Development | Production |
| **Hot Reload** | ❌ | ✅ | ❌ |
| **SMTP** | Real (test) | MailHog | Real (prod) |
| **Nginx** | ✅ | ❌ | ✅ |
| **SSL** | ❌ | ❌ | ✅ |
| **Monitoring** | ❌ | ❌ | ✅ (Prometheus) |
| **Bcrypt Rounds** | 10 | 4 | 12 |
| **Log Level** | INFO | DEBUG | WARNING |
| **Startup Time** | ~20s | ~30s | ~40s |

---

## Quick Start

### 1. Prerequisites Check

```bash
# Verify Docker is installed
docker --version
# Required: 24.0+

# Verify Docker Compose
docker-compose --version
# Required: 2.0+

# Verify you have SMTP credentials
# Options: Mailtrap, Mailgun, SendGrid test credentials
```

### 2. Environment Setup

```bash
# Clone repository (if not already done)
git clone https://github.com/yourusername/contravento-application-python.git
cd contravento-application-python

# Copy environment template
cp .env.dev.example .env.dev
```

### 3. Generate Secrets

```bash
# Generate SECRET_KEY (min 64 characters)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate database password
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 24
```

### 4. Configure Environment Variables

Edit `.env.dev` with your generated values:

```bash
# Application
APP_NAME=ContraVento-Dev
APP_ENV=development
DEBUG=false                    # Production-like behavior

# Security
SECRET_KEY=<paste_generated_secret_64chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
BCRYPT_ROUNDS=10               # Moderate (faster than prod)

# Database
DATABASE_URL=postgresql+asyncpg://contravento_dev:<DB_PASSWORD>@postgres:5432/contravento_dev
POSTGRES_DB=contravento_dev
POSTGRES_USER=contravento_dev
POSTGRES_PASSWORD=<paste_generated_db_password>

# Redis
REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/0
REDIS_PASSWORD=<paste_generated_redis_password>

# SMTP (Example: Mailtrap)
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=<your_mailtrap_user>
SMTP_PASSWORD=<your_mailtrap_password>
SMTP_FROM=noreply@dev.contravento.local
SMTP_TLS=true

# CORS (adjust as needed)
CORS_ORIGINS=http://dev.contravento.local:8000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json                # Structured logging
```

### 5. Deploy Environment

**Linux/Mac**:
```bash
./deploy.sh dev
```

**Windows PowerShell**:
```powershell
.\deploy.ps1 dev
```

**Manual** (all platforms):
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up -d
```

### 6. Verify Deployment

```bash
# Check all containers are running
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev ps

# Expected output:
# NAME                     STATUS
# contravento-db-dev       Up (healthy)
# contravento-api-dev      Up (healthy)
# contravento-redis-dev    Up (healthy)
# contravento-nginx-dev    Up

# Test backend health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}

# Test Nginx proxy
curl http://localhost/health
# Expected: {"status":"healthy","database":"connected"}
```

### 7. Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** (direct) | http://localhost:8000 | API endpoints (bypasses Nginx) |
| **Backend API** (via Nginx) | http://localhost | API endpoints (through proxy) |
| **API Documentation** | http://localhost:8000/docs | Swagger UI (only if DEBUG=true) |
| **Database** | localhost:5432 | PostgreSQL connection |
| **Redis** | localhost:6379 | Redis cache |

**Database Connection**:
```
Host:      localhost
Port:      5432
Database:  contravento_dev
User:      contravento_dev
Password:  <from .env.dev>
```

---

## Architecture

### Service Stack

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT REQUEST                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   Nginx (Port 80)│  Reverse Proxy
         │   Load Balancer  │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Backend API     │  FastAPI (Port 8000)
         │  (Python 3.12)   │
         └────┬────────┬────┘
              │        │
      ┌───────┘        └────────┐
      │                         │
      ▼                         ▼
┌──────────┐             ┌──────────┐
│PostgreSQL│             │  Redis   │
│(Port 5432)│             │(Port 6379)│
└──────────┘             └──────────┘
      │
      │ (persistence)
      ▼
  ┌─────────────┐
  │ postgres_data│  Named Volume
  │  (persistent) │
  └─────────────┘
```

### Service Dependencies

1. **postgres** - Starts first (no dependencies)
2. **redis** - Starts in parallel with postgres
3. **backend** - Depends on postgres (waits for health check)
4. **nginx** - Starts after backend is healthy

**Startup Order**:
```
postgres, redis
    ↓ (wait for postgres healthy)
backend
    ↓ (wait for backend healthy)
nginx
```

### Network Configuration

**Network**: `contravento-network` (bridge driver)

**Internal DNS**:
- `postgres:5432` - PostgreSQL server (internal)
- `redis:6379` - Redis server (internal)
- `backend:8000` - Backend API (internal)

**Port Mappings**:
- `80:80` - Nginx reverse proxy
- `8000:8000` - Backend API (direct access)
- `5432:5432` - PostgreSQL (external tools)
- `6379:6379` - Redis (external tools)

### Storage Volumes

**Named Volumes** (persistent across restarts):
- `postgres_data` - Database files
- `redis_data` - Redis persistence (AOF)
- `backend_storage` - Uploaded files (photos, GPX)

**No Bind Mounts**: Dev mode rebuilds images, does not mount source code.

---

## Configuration

### Nginx Reverse Proxy

The dev environment includes Nginx configuration at `nginx/dev.conf`:

```nginx
# Upstream backend servers
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name dev.contravento.local localhost;

    # Client upload size (for photo/GPX uploads)
    client_max_body_size 10M;

    # Backend API proxy
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint (no auth)
    location /health {
        access_log off;
        proxy_pass http://backend/health;
    }
}
```

**Key Features**:
- Upstream connection pooling
- Request header forwarding (X-Real-IP, X-Forwarded-For)
- Client upload limit: 10 MB
- Timeouts: 60 seconds
- Health check bypass logging

### SMTP Configuration

Dev mode requires **real SMTP** provider (not MailHog). Recommended options:

**Option 1: Mailtrap** (Recommended for testing):
```bash
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=<mailtrap_inbox_user>
SMTP_PASSWORD=<mailtrap_inbox_password>
SMTP_TLS=true
```

**Option 2: Mailgun** (Sandbox for testing):
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@sandbox<id>.mailgun.org
SMTP_PASSWORD=<mailgun_smtp_password>
SMTP_TLS=true
```

**Option 3: SendGrid** (Free tier for testing):
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid_api_key>
SMTP_TLS=true
```

### Database Configuration

**PostgreSQL Settings** (in `docker-compose.dev.yml`):
```yaml
postgres:
  environment:
    POSTGRES_DB: contravento_dev
    POSTGRES_USER: contravento_dev
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U contravento_dev -d contravento_dev"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Connection Pool** (backend):
- Pool size: 10 connections
- Max overflow: 5 connections
- Pool timeout: 30 seconds
- Pool recycle: 3600 seconds (1 hour)

### Logging Configuration

Dev mode uses **structured JSON logging**:

```json
{
  "timestamp": "2026-02-06T14:23:45.123Z",
  "level": "INFO",
  "logger": "src.api.auth",
  "message": "User login successful",
  "user_id": "uuid-here",
  "username": "testuser",
  "ip": "172.18.0.1"
}
```

**Log Levels**:
- `LOG_LEVEL=INFO` - Standard logs (recommended)
- `LOG_LEVEL=DEBUG` - Verbose logs (not recommended for dev)
- `LOG_LEVEL=WARNING` - Only warnings and errors

**View Logs**:
```bash
# All services
./deploy.sh dev logs

# Specific service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev logs backend

# Follow logs in real-time
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev logs -f backend
```

---

## Common Workflows

### Daily Operations

**Start Environment**:
```bash
./deploy.sh dev
```

**Stop Environment**:
```bash
./deploy.sh dev stop
```

**Restart Services**:
```bash
# Restart all
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev restart

# Restart backend only
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev restart backend
```

**View Container Status**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev ps
```

### Code Deployment

**Rebuild and Deploy** (after code changes):
```bash
# Rebuild backend image
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev build backend

# Deploy updated image
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up -d backend

# Verify deployment
curl http://localhost:8000/health
```

**Full Rebuild** (all services):
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev build --no-cache
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up -d
```

### Database Operations

**Run Migrations**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec backend poetry run alembic upgrade head
```

**Create Admin User**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec backend poetry run python scripts/user-mgmt/create_admin.py
```

**Backup Database**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec postgres pg_dump -U contravento_dev -d contravento_dev -F c \
  -f /tmp/backup_$(date +%Y%m%d_%H%M%S).backup
```

**Restore Database**:
```bash
# Copy backup to container
docker cp backup.backup contravento-db-dev:/tmp/

# Restore
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec postgres pg_restore -U contravento_dev -d contravento_dev --clean /tmp/backup.backup
```

### Testing

**Run Integration Tests**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec backend poetry run pytest tests/integration/ -v
```

**Run API Tests** (with coverage):
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec backend poetry run pytest tests/api/ --cov=src --cov-report=html
```

**Test Email Delivery**:
```bash
# Trigger password reset email
curl -X POST http://localhost:8000/auth/password-reset \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Check Mailtrap inbox for email
```

### Nginx Configuration

**Test Nginx Config**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec nginx nginx -t
```

**Reload Nginx** (after config changes):
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec nginx nginx -s reload
```

**View Nginx Logs**:
```bash
# Access logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  logs nginx | grep "GET\|POST"

# Error logs only
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  logs nginx | grep "error"
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Backend Container Won't Start

**Symptoms**: Backend container status shows "Restarting" or "Exited"

**Diagnosis**:
```bash
# View backend logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev logs backend
```

**Common Causes**:

1. **Database connection failed**:
   ```
   Error: connection to server at "postgres" (172.18.0.2), port 5432 failed
   ```
   **Fix**: Wait for postgres health check to pass
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev ps
   # postgres should show "(healthy)"
   ```

2. **Invalid SECRET_KEY**:
   ```
   Error: SECRET_KEY must be at least 32 characters
   ```
   **Fix**: Regenerate SECRET_KEY in .env.dev
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

3. **Migration errors**:
   ```
   Error: alembic.util.exc.CommandError
   ```
   **Fix**: Reset database and re-run migrations
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev down -v
   ./deploy.sh dev
   ```

#### Issue 2: Nginx 502 Bad Gateway

**Symptoms**: Requests to http://localhost return "502 Bad Gateway"

**Diagnosis**:
```bash
# Check if backend is running
curl http://localhost:8000/health
# If this works, Nginx is the problem

# Check Nginx logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev logs nginx
```

**Common Causes**:

1. **Backend not ready**:
   ```
   connect() failed (111: Connection refused) while connecting to upstream
   ```
   **Fix**: Wait for backend health check
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev ps
   # backend should show "(healthy)"
   ```

2. **Nginx config syntax error**:
   ```
   nginx: [emerg] invalid parameter
   ```
   **Fix**: Test Nginx configuration
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
     exec nginx nginx -t
   ```

#### Issue 3: SMTP Emails Not Sending

**Symptoms**: Emails not arriving in Mailtrap/test inbox

**Diagnosis**:
```bash
# Check backend logs for email errors
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  logs backend | grep -i "smtp\|email"
```

**Common Causes**:

1. **Invalid SMTP credentials**:
   ```
   Error: 535 Authentication failed
   ```
   **Fix**: Verify SMTP credentials in .env.dev
   - Check SMTP_USER and SMTP_PASSWORD
   - Test credentials in email client

2. **SMTP port blocked**:
   ```
   Error: Connection timed out
   ```
   **Fix**: Verify firewall allows port 587
   ```bash
   telnet smtp.mailtrap.io 587
   # Should connect successfully
   ```

3. **TLS configuration**:
   ```
   Error: SSL/TLS handshake failed
   ```
   **Fix**: Set SMTP_TLS=true in .env.dev

#### Issue 4: Database Connection Pool Exhausted

**Symptoms**: Intermittent "connection pool timeout" errors

**Diagnosis**:
```bash
# Check active connections
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec postgres psql -U contravento_dev -d contravento_dev \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname='contravento_dev';"
```

**Fix**: Increase connection pool in .env.dev
```bash
# Add to .env.dev
DATABASE_POOL_SIZE=20    # Default: 10
DATABASE_MAX_OVERFLOW=10  # Default: 5
```

Restart backend:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev restart backend
```

#### Issue 5: Port Already in Use

**Symptoms**: `Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use`

**Diagnosis**:
```bash
# Find process using port 80
sudo lsof -i :80              # Linux/Mac
netstat -ano | findstr :80    # Windows
```

**Fix**: Stop conflicting service or change port

**Option 1**: Stop Apache/Nginx on host
```bash
sudo systemctl stop apache2    # or nginx
```

**Option 2**: Change Nginx port in docker-compose.dev.yml
```yaml
nginx:
  ports:
    - "8080:80"  # Use port 8080 instead
```

### Performance Issues

**Slow Response Times**:
```bash
# Check container resource usage
docker stats

# If high CPU/memory:
# 1. Check for N+1 query problems
# 2. Verify connection pooling enabled
# 3. Review slow query logs

# Enable PostgreSQL slow query logging
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec postgres psql -U contravento_dev -d contravento_dev \
  -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"  # Log queries >1s
```

**High Memory Usage**:
```bash
# Check Docker memory limits
docker inspect contravento-api-dev | grep -i memory

# Increase limit in docker-compose.dev.yml if needed
```

### Getting Help

**Collect Diagnostic Information**:
```bash
# Container status
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev ps

# All logs (last 100 lines)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev logs --tail=100

# Environment variables (sanitized)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev \
  exec backend env | grep -v "PASSWORD\|SECRET\|KEY" | sort
```

**Further Resources**:
- [Troubleshooting Guide](../guides/troubleshooting.md) - Comprehensive troubleshooting
- [Docker Compose Guide](../guides/docker-compose-guide.md) - Architecture deep dive
- [Database Management](../guides/database-management.md) - DB operations

---

## Related Modes

### Progression Path

```
Local Development → Dev → Staging → Production
```

**Typical Workflow**:
1. **Local-Dev** - Daily feature development with SQLite
2. **Local-Full** - Email feature development with MailHog
3. **Dev** - Integration testing with production-like build (YOU ARE HERE)
4. **Staging** - Final QA testing with monitoring
5. **Production** - Live deployment

### Migration Guide

#### From Local-Full to Dev

**What Changes**:
- ❌ No MailHog → Use real SMTP (Mailtrap)
- ❌ No pgAdmin → Use DBeaver/TablePlus
- ✅ Nginx added → Proxy configuration
- ✅ Production build → Slower startup, more stable

**Migration Steps**:
```bash
# 1. Get Mailtrap credentials (free account: https://mailtrap.io)
# 2. Copy environment
cp .env.dev.example .env.dev

# 3. Configure SMTP in .env.dev
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=<mailtrap_user>
SMTP_PASSWORD=<mailtrap_password>

# 4. Deploy
./deploy.sh dev
```

#### From Dev to Staging

**What Changes**:
- ✅ SSL/TLS certificates → HTTPS required
- ✅ Monitoring added → Prometheus + Grafana
- ✅ Stronger security → Bcrypt rounds = 12
- ✅ Production SMTP → Real email provider

**Migration Steps**:
1. Review [Staging Mode Guide](./staging.md)
2. Configure DNS records
3. Obtain SSL certificates
4. Update SMTP to production provider
5. Deploy with `./deploy.sh staging`

### Related Documentation

- **[Local-Full Mode](./local-full.md)** - Previous mode in progression
- **[Staging Mode](./staging.md)** - Next mode in progression
- **[Production Mode](./prod.md)** - Final deployment target
- **[Environment Variables Guide](../guides/environment-variables.md)** - Configuration reference
- **[Docker Compose Architecture](../guides/docker-compose-guide.md)** - Service dependencies

---

## Resource Requirements

**Minimum**:
- **CPU**: 2 cores
- **RAM**: 2 GB
- **Disk**: 5 GB
- **Network**: 100 Mbps

**Recommended**:
- **CPU**: 4 cores
- **RAM**: 4 GB
- **Disk**: 10 GB
- **Network**: 1 Gbps

**Estimated Costs** (cloud hosting):
- AWS t3.medium (2 vCPU, 4 GB RAM): ~$30/month
- DigitalOcean Droplet (2 CPU, 4 GB RAM): ~$24/month
- Hetzner Cloud CX21 (2 vCPU, 4 GB RAM): ~€6/month

---

## Security Considerations

**Dev Environment Security**:
- ✅ Use strong passwords (min 32 chars)
- ✅ Rotate secrets regularly (every 90 days)
- ✅ Use test SMTP credentials (not production)
- ✅ Restrict firewall to team IPs only
- ❌ Do NOT expose to public internet
- ❌ Do NOT use production database
- ❌ Do NOT share credentials in Slack/email

**Access Control**:
```bash
# Restrict Docker network (optional)
# Edit docker-compose.dev.yml
networks:
  contravento-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
```

**Firewall Rules** (example for UFW):
```bash
# Allow only from team IPs
sudo ufw allow from 203.0.113.0/24 to any port 80
sudo ufw allow from 203.0.113.0/24 to any port 8000
sudo ufw deny 80
sudo ufw deny 8000
```

---

**Last Updated**: 2026-02-06
**Document Version**: 1.0
**Feedback**: Report issues or suggest improvements via GitHub Issues
