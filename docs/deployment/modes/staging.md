# Staging Deployment Mode - Pre-Production Environment

**Purpose**: Production mirror for final testing, QA, and user acceptance testing (UAT)

**Target Users**: QA teams, product managers, stakeholders, deployment engineers

**Difficulty**: Advanced

**Estimated Setup Time**: 60-90 minutes (including SSL setup)

**Prerequisites**:
- Docker 24.0+ and Docker Compose 2.0+
- Production-like server (min 2 CPU, 4 GB RAM)
- Domain name with DNS access (e.g., staging.contravento.com)
- SSL certificate (Let's Encrypt recommended)
- Production or staging SMTP credentials
- Basic understanding of SSL/TLS and monitoring

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [SSL/TLS Setup](#ssltls-setup)
6. [Monitoring](#monitoring)
7. [Common Workflows](#common-workflows)
8. [Testing Checklist](#testing-checklist)
9. [Troubleshooting](#troubleshooting)
10. [Related Modes](#related-modes)

---

## Overview

### What is Staging Mode?

The **Staging** deployment mode provides a production-identical environment for final testing before production deployment. It mirrors production configuration exactly but uses isolated infrastructure to prevent impact on live users.

**Key Characteristics**:
- ✅ Identical to production configuration
- ✅ SSL/TLS certificates (HTTPS enforced)
- ✅ Monitoring stack (Prometheus + Grafana)
- ✅ Production-level security (bcrypt rounds = 12)
- ✅ Separate database (isolated from production)
- ✅ Resource limits and health checks
- ✅ Automated backups
- ✅ Real or staging SMTP provider
- ✅ Performance testing capabilities
- ❌ No debug mode (DEBUG=false)
- ❌ Lower traffic than production
- ❌ May use staging API keys (Stripe, etc.)

### When to Use Staging Mode

**Perfect For**:
- ✅ Final testing before production release
- ✅ Client demos and user acceptance testing (UAT)
- ✅ Performance testing under production conditions
- ✅ Validating monitoring and alerting configurations
- ✅ Training QA team on production environment
- ✅ Stakeholder review and sign-off
- ✅ Load testing and stress testing
- ✅ Verifying SSL certificate setup

**Not Suitable For**:
- ❌ Daily feature development (use [local-dev](./local-dev.md) instead)
- ❌ Integration testing (use [dev](./dev.md) instead)
- ❌ Serving real users (use [prod](./prod.md) instead)

### Comparison with Other Modes

| Feature | Staging | Dev | Production |
|---------|:-------:|:---:|:----------:|
| **SSL/TLS** | ✅ (HTTPS) | ❌ (HTTP) | ✅ (HTTPS) |
| **Monitoring** | ✅ Prometheus | ❌ | ✅ Full stack |
| **Bcrypt Rounds** | 12 | 10 | 14 |
| **Database** | PostgreSQL | PostgreSQL | PostgreSQL |
| **SMTP** | Real/Staging | Test (Mailtrap) | Production |
| **Log Level** | INFO | INFO | WARNING |
| **Debug Mode** | ❌ | ❌ | ❌ |
| **Replicas** | 1 | 1 | 3+ |
| **Auto-scaling** | ❌ | ❌ | ✅ |
| **Startup Time** | ~40s | ~20s | ~60s |

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

# Verify DNS is configured
nslookup staging.contravento.com
# Should resolve to your server IP

# Verify server specs
lscpu | grep "CPU(s):"        # Min 2 CPUs
free -h | grep "Mem:"         # Min 4 GB RAM
df -h | grep "/$"             # Min 20 GB disk
```

### 2. Environment Setup

```bash
# Clone repository (if not already done)
git clone https://github.com/yourusername/contravento-application-python.git
cd contravento-application-python

# Copy environment template
cp .env.staging.example .env.staging
```

### 3. Generate Strong Secrets

**CRITICAL**: Staging uses production-strength secrets.

```bash
# Generate STRONG SECRET_KEY (min 96 characters)
python -c "import secrets; print(secrets.token_urlsafe(96))"

# Generate strong database password (min 32 characters)
openssl rand -base64 32

# Generate strong Redis password (min 24 characters)
openssl rand -base64 24

# Generate Grafana admin password
openssl rand -base64 16
```

### 4. Configure Environment Variables

Edit `.env.staging` with your generated values:

```bash
# Application
APP_NAME=ContraVento-Staging
APP_ENV=production               # IMPORTANT: Use production mode!
DEBUG=false                      # CRITICAL: Must be false!

# Security (STRONG secrets required)
SECRET_KEY=<paste_generated_secret_96chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
BCRYPT_ROUNDS=12                 # Production-level security

# Database (separate from production!)
DATABASE_URL=postgresql+asyncpg://contravento_staging:<DB_PASSWORD>@postgres:5432/contravento_staging
POSTGRES_DB=contravento_staging
POSTGRES_USER=contravento_staging
POSTGRES_PASSWORD=<paste_generated_db_password>

# Redis (use DB index 1 to separate from production)
REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/1
REDIS_PASSWORD=<paste_generated_redis_password>

# SMTP (production or staging provider)
# Option 1: Production SMTP with staging sender
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid_api_key>
SMTP_FROM=noreply-staging@contravento.com
SMTP_TLS=true

# Option 2: Mailtrap for staging emails
# SMTP_HOST=smtp.mailtrap.io
# SMTP_PORT=587
# SMTP_USER=<mailtrap_user>
# SMTP_PASSWORD=<mailtrap_password>
# SMTP_FROM=noreply@staging.contravento.local
# SMTP_TLS=true

# CORS (staging domain only!)
CORS_ORIGINS=https://staging.contravento.com

# Domain (for SSL certificate)
DOMAIN=staging.contravento.com

# Logging
LOG_LEVEL=INFO                   # Standard logging
LOG_FORMAT=json

# Monitoring
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<paste_generated_grafana_password>

# Error Tracking (optional but recommended)
SENTRY_DSN=https://<key>@sentry.io/<staging-project>
SENTRY_ENVIRONMENT=staging
```

### 5. Configure DNS

**Point your staging domain to server IP**:

```bash
# DNS A Record (example)
# Type: A
# Name: staging.contravento.com
# Value: 203.0.113.50 (your server IP)
# TTL: 300

# Verify DNS propagation
dig staging.contravento.com +short
# Should return your server IP
```

### 6. Deploy Environment

**Linux/Mac**:
```bash
./deploy.sh staging
```

**Windows PowerShell**:
```powershell
.\deploy.ps1 staging
```

**Manual** (all platforms):
```bash
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging up -d
```

### 7. Verify SSL Certificate

```bash
# Check SSL certificate (Let's Encrypt automatic)
curl -I https://staging.contravento.com

# Expected headers:
# HTTP/2 200
# Strict-Transport-Security: max-age=31536000
# X-Frame-Options: DENY

# Verify certificate details
openssl s_client -connect staging.contravento.com:443 -servername staging.contravento.com | grep -i "verify return code"
# Expected: "Verify return code: 0 (ok)"
```

### 8. Run Post-Deployment Validation

See [Testing Checklist](#testing-checklist) section below.

### 9. Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Backend API** | https://staging.contravento.com | - |
| **API Documentation** | https://staging.contravento.com/docs | - (if DEBUG=true) |
| **Grafana** | http://server-ip:3000 | admin / <GRAFANA_PASSWORD> |
| **Prometheus** | http://server-ip:9090 | - |
| **Database** | server-ip:5432 | contravento_staging / <DB_PASSWORD> |

**Security Note**: Grafana and Prometheus should NOT be exposed to public internet. Access via SSH tunnel or VPN.

---

## Architecture

### Service Stack

```
┌─────────────────────────────────────────────────────────┐
│                 CLIENT REQUEST (HTTPS)                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ Nginx (Port 443) │  SSL Termination
         │  + SSL/TLS       │  Reverse Proxy
         │  + Let's Encrypt │
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
│ Staging  │             │  DB #1   │
└─────┬────┘             └──────────┘
      │
      │ (backup every 6 hours)
      ▼
  ┌─────────────┐
  │   Backups    │
  │ (S3 or local)│
  └─────────────┘

         MONITORING STACK
         ┌──────────────────┐
         │   Prometheus     │  Metrics Collection
         │   (Port 9090)    │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │    Grafana       │  Metrics Visualization
         │   (Port 3000)    │
         └──────────────────┘
```

### Service Dependencies

1. **postgres** - Starts first (no dependencies)
2. **redis** - Starts in parallel with postgres
3. **backend** - Depends on postgres (waits for health check)
4. **nginx** - Starts after backend is healthy
5. **prometheus** - Starts after backend (scrapes metrics)
6. **grafana** - Starts after prometheus (displays dashboards)

**Startup Order**:
```
postgres, redis
    ↓ (wait for postgres healthy)
backend
    ↓ (wait for backend healthy)
nginx, prometheus
    ↓ (wait for prometheus ready)
grafana
```

### Network Configuration

**Network**: `contravento-network` (bridge driver)

**Internal DNS**:
- `postgres:5432` - PostgreSQL server (internal)
- `redis:6379` - Redis server (internal)
- `backend:8000` - Backend API (internal)
- `prometheus:9090` - Prometheus (internal)
- `grafana:3000` - Grafana (internal)

**Port Mappings**:
- `443:443` - Nginx HTTPS
- `80:80` - Nginx HTTP (redirects to HTTPS)
- `3000:3000` - Grafana UI (restrict via firewall!)
- `9090:9090` - Prometheus UI (restrict via firewall!)
- `5432:5432` - PostgreSQL (external tools)
- `6379:6379` - Redis (external tools)

### Storage Volumes

**Named Volumes** (persistent across restarts):
- `postgres_data` - Database files
- `redis_data` - Redis persistence (AOF)
- `backend_storage` - Uploaded files (photos, GPX)
- `prometheus_data` - Metrics time-series data
- `grafana_data` - Dashboards and configuration
- `ssl_certificates` - Let's Encrypt SSL certificates

**Backup Strategy**:
- Database backups: Every 6 hours to external storage
- Volume snapshots: Daily
- Retention: 7 daily, 4 weekly, 3 monthly

---

## Configuration

### Nginx SSL Configuration

Staging uses **automatic SSL** with Let's Encrypt:

```nginx
# HTTP → HTTPS redirect
server {
    listen 80;
    server_name staging.contravento.com;

    # ACME challenge for SSL verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name staging.contravento.com;

    # SSL certificates (auto-generated by Certbot)
    ssl_certificate /etc/letsencrypt/live/staging.contravento.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/staging.contravento.com/privkey.pem;

    # SSL configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client upload size
    client_max_body_size 10M;

    # Backend API proxy
    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check (no auth)
    location /health {
        access_log off;
        proxy_pass http://backend:8000/health;
    }
}
```

### Database Configuration

**PostgreSQL Settings** (production-grade):
```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: contravento_staging
    POSTGRES_USER: contravento_staging
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=en_US.UTF-8"
  # Connection pooling
  command: >
    postgres
    -c max_connections=100
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c maintenance_work_mem=64MB
    -c checkpoint_completion_target=0.9
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U contravento_staging"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Connection Pool** (backend):
- Pool size: 20 connections
- Max overflow: 10 connections
- Pool timeout: 30 seconds
- Pool recycle: 1800 seconds (30 minutes)

### SMTP Configuration

**Option 1: Production SMTP** (recommended):
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid_api_key>
SMTP_FROM=noreply-staging@contravento.com
SMTP_TLS=true
```

**Option 2: Staging SMTP** (Mailtrap):
```bash
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=<mailtrap_user>
SMTP_PASSWORD=<mailtrap_password>
SMTP_FROM=noreply@staging.contravento.local
SMTP_TLS=true
```

### Security Configuration

**Production-Level Security**:
- `BCRYPT_ROUNDS=12` - Strong password hashing (1-2s per hash)
- `ACCESS_TOKEN_EXPIRE_MINUTES=15` - Short-lived JWT tokens
- `REFRESH_TOKEN_EXPIRE_DAYS=30` - Reasonable refresh window
- CORS restricted to staging domain only
- HTTPS enforced (HTTP redirects to HTTPS)
- Security headers enabled (HSTS, X-Frame-Options, etc.)

---

## SSL/TLS Setup

### Automatic SSL with Certbot

Staging uses **Certbot** for automatic SSL certificate management:

#### First-Time Setup

```bash
# 1. Deploy environment (Certbot will auto-request certificate)
./deploy.sh staging

# 2. Verify certificate obtained
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  logs certbot | grep "Successfully received certificate"

# 3. Test SSL
curl -I https://staging.contravento.com
# Should return HTTP/2 200 with SSL headers
```

#### Manual Certificate Renewal

```bash
# Certbot auto-renews every 12 hours, but you can force renewal:
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  exec certbot certbot renew

# Reload Nginx after renewal
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  exec nginx nginx -s reload
```

#### Verify Certificate

```bash
# Check certificate expiry
openssl s_client -connect staging.contravento.com:443 -servername staging.contravento.com 2>/dev/null | \
  openssl x509 -noout -dates

# Expected output:
# notBefore=Jan  1 00:00:00 2026 GMT
# notAfter=Apr  1 00:00:00 2026 GMT (90 days from issuance)

# Check certificate chain
openssl s_client -connect staging.contravento.com:443 -servername staging.contravento.com 2>/dev/null | \
  openssl x509 -noout -issuer -subject
```

### Troubleshooting SSL

**Issue**: Certificate not issued

```bash
# Check Certbot logs
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  logs certbot

# Common causes:
# 1. DNS not propagated (wait 5-10 minutes)
# 2. Port 80 not accessible (check firewall)
# 3. Domain validation failed (check ACME challenge)

# Test ACME challenge manually
curl http://staging.contravento.com/.well-known/acme-challenge/test
# Should return 404 (directory exists but file doesn't)
```

---

## Monitoring

### Prometheus + Grafana Stack

Staging includes full monitoring capabilities:

#### Accessing Grafana

```bash
# Grafana URL (via SSH tunnel recommended)
ssh -L 3000:localhost:3000 user@staging-server

# Open in browser: http://localhost:3000
# Login: admin / <GRAFANA_ADMIN_PASSWORD from .env.staging>
```

#### Pre-configured Dashboards

Import ContraVento dashboards (stored in `monitoring/grafana/dashboards/`):

1. **API Performance Dashboard**:
   - Response times (p50, p95, p99)
   - Request rate (requests/second)
   - Error rate (4xx, 5xx responses)

2. **Database Dashboard**:
   - Active connections
   - Query duration
   - Transaction rate
   - Slow queries (>1s)

3. **System Resources Dashboard**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

#### Key Metrics to Monitor

**API Health**:
```promql
# Request rate
rate(http_requests_total[5m])

# Response time (95th percentile)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

**Database Health**:
```promql
# Active connections
pg_stat_activity_count

# Slow queries
pg_stat_statements_mean_exec_time_seconds > 1
```

**System Health**:
```promql
# CPU usage
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

#### Alerting (Optional)

Configure Grafana alerts for:
- API response time > 500ms (p95)
- Error rate > 1%
- Database connections > 80%
- Memory usage > 90%
- Disk usage > 85%

---

## Common Workflows

### Daily Operations

**Start Environment**:
```bash
./deploy.sh staging
```

**Stop Environment**:
```bash
./deploy.sh staging stop
```

**Restart Services**:
```bash
# Restart all
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging restart

# Restart backend only
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging restart backend
```

**View Logs**:
```bash
# All services
./deploy.sh staging logs

# Specific service
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging logs backend -f

# Filter for errors
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging logs backend | grep -i "error\|exception"
```

### Code Deployment

**Deploy New Version**:
```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild backend image
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging build backend

# 3. Run database migrations (if any)
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  exec backend poetry run alembic upgrade head

# 4. Deploy updated image
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging up -d backend

# 5. Verify deployment
curl https://staging.contravento.com/health
```

### Database Operations

**Backup Database**:
```bash
# Create backup
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  exec postgres pg_dump -U contravento_staging -d contravento_staging -F c \
  -f /tmp/staging_backup_$(date +%Y%m%d_%H%M%S).backup

# Copy to host
docker cp contravento-db-staging:/tmp/staging_backup_*.backup ./backups/

# Upload to S3 (recommended)
aws s3 cp ./backups/staging_backup_*.backup s3://contravento-backups/staging/
```

**Restore Database**:
```bash
# Copy backup to container
docker cp backup.backup contravento-db-staging:/tmp/

# Restore
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  exec postgres pg_restore -U contravento_staging -d contravento_staging --clean /tmp/backup.backup
```

### Performance Testing

**Load Testing with Apache Bench**:
```bash
# Simple load test (100 requests, 10 concurrent)
ab -n 100 -c 10 https://staging.contravento.com/health

# Monitor metrics in Grafana while running
```

**Stress Testing**:
```bash
# Install k6 (https://k6.io)
# Create load test script (example in scripts/load-tests/api-load.js)

k6 run --vus 50 --duration 30s scripts/load-tests/api-load.js
```

---

## Testing Checklist

### Pre-Release Validation

Before promoting to production, verify all items:

#### Functional Tests

- [ ] **Health check** responds: `curl https://staging.contravento.com/health`
- [ ] **User registration** works end-to-end
- [ ] **Email verification** received (check inbox or Mailtrap)
- [ ] **Login** works with verified user
- [ ] **Create trip** works (draft → publish)
- [ ] **Upload photos** works (trip photos, profile photo)
- [ ] **GPX upload** works (map displays correctly)
- [ ] **Public feed** shows published trips
- [ ] **User profile** displays stats correctly

#### Security Tests

- [ ] **HTTPS enforced**: `curl -I http://staging.contravento.com` (should redirect to HTTPS)
- [ ] **SSL certificate valid**: No browser warnings
- [ ] **CORS configured**: Only staging domain allowed
- [ ] **Security headers present**: HSTS, X-Frame-Options, X-Content-Type-Options
- [ ] **API docs hidden**: `/docs` returns 404 (if DEBUG=false)
- [ ] **Sensitive data not logged**: Check logs for passwords, tokens

#### Performance Tests

- [ ] **API response times**: <500ms p95 (use Grafana dashboard)
- [ ] **Page load times**: <3s for main pages
- [ ] **Database queries**: No N+1 problems (check slow query log)
- [ ] **Photo upload**: <2s for 5MB file
- [ ] **Memory usage**: <80% under load
- [ ] **CPU usage**: <70% under load

#### Monitoring Tests

- [ ] **Prometheus scraping**: Metrics available at http://server-ip:9090/graph
- [ ] **Grafana dashboards**: All panels showing data
- [ ] **Health check metrics**: Backend uptime visible
- [ ] **Error tracking**: Sentry receiving errors (if configured)

#### Database Tests

- [ ] **Migrations applied**: `alembic current` shows latest revision
- [ ] **Seed data loaded**: Admin user exists
- [ ] **Backups working**: Verify automated backup ran
- [ ] **Connection pooling**: Max connections not exceeded (check `pg_stat_activity`)

---

## Troubleshooting

### Common Issues

#### Issue 1: SSL Certificate Not Issued

**Symptoms**: Browser shows "Certificate not found" or "NET::ERR_CERT_COMMON_NAME_INVALID"

**Diagnosis**:
```bash
# Check Certbot logs
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging logs certbot

# Expected: "Successfully received certificate"
```

**Common Causes**:

1. **DNS not propagated**:
   ```bash
   dig staging.contravento.com +short
   # Should return server IP
   ```
   **Fix**: Wait 5-10 minutes for DNS propagation

2. **Port 80 not accessible**:
   ```bash
   curl http://staging.contravento.com/.well-known/acme-challenge/
   # Should return 404 (not connection refused)
   ```
   **Fix**: Open port 80 in firewall
   ```bash
   sudo ufw allow 80/tcp
   ```

3. **Domain validation failed**:
   Check Certbot logs for specific error
   **Fix**: Ensure `DOMAIN` in .env.staging matches DNS record exactly

#### Issue 2: Monitoring Stack Not Working

**Symptoms**: Grafana shows "No data" or Prometheus targets down

**Diagnosis**:
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana health
curl http://localhost:3000/api/health
```

**Fixes**:

1. **Prometheus can't reach backend**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
     exec prometheus wget -O- http://backend:8000/metrics
   # Should return Prometheus metrics
   ```

2. **Grafana can't reach Prometheus**:
   ```bash
   # Verify Grafana data source configuration
   # Login to Grafana → Configuration → Data Sources
   # Prometheus URL should be: http://prometheus:9090
   ```

#### Issue 3: High Memory Usage

**Symptoms**: Server becomes slow, OOM (out of memory) errors

**Diagnosis**:
```bash
# Check container memory usage
docker stats --no-stream

# Check PostgreSQL memory
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  exec postgres psql -U contravento_staging -d contravento_staging \
  -c "SELECT pg_size_pretty(pg_database_size('contravento_staging'));"
```

**Fixes**:

1. **Increase server RAM** (upgrade to 8 GB)
2. **Reduce connection pool**:
   ```bash
   # In .env.staging
   DATABASE_POOL_SIZE=10  # Reduce from 20
   ```
3. **Add memory limits** in `docker-compose.staging.yml`:
   ```yaml
   backend:
     deploy:
       resources:
         limits:
           memory: 2G
   ```

#### Issue 4: Slow Response Times

**Symptoms**: API requests take >1s, timeouts

**Diagnosis**:
```bash
# Check slow queries
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  exec postgres psql -U contravento_staging -d contravento_staging \
  -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check backend logs
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging \
  logs backend | grep -i "slow\|timeout"
```

**Fixes**:

1. **Add database indexes** for slow queries
2. **Enable query caching** (Redis)
3. **Optimize N+1 queries** (use eager loading)
4. **Increase backend workers**:
   ```bash
   # In docker-compose.staging.yml
   environment:
     WEB_CONCURRENCY: 4  # Increase workers
   ```

### Getting Help

**Collect Diagnostic Information**:
```bash
# System info
uname -a
docker --version
docker-compose --version

# Container status
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging ps

# Resource usage
docker stats --no-stream

# Recent logs (last 100 lines per service)
docker-compose -f docker-compose.yml -f docker-compose.staging.yml --env-file .env.staging logs --tail=100

# Network connectivity
curl -I https://staging.contravento.com
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana
```

**Further Resources**:
- [Troubleshooting Guide](../guides/troubleshooting.md)
- [Production Checklist](../guides/production-checklist.md)
- [Monitoring Guide](../guides/monitoring.md) (future)

---

## Related Modes

### Progression Path

```
Dev → Staging → Production
```

**Typical Workflow**:
1. **Dev** - Integration testing with production-like build
2. **Staging** - Final QA testing with monitoring (YOU ARE HERE)
3. **Production** - Live deployment with HA and auto-scaling

### Migration Guide

#### From Dev to Staging

**What Changes**:
- ✅ SSL/TLS added → HTTPS required
- ✅ Monitoring added → Prometheus + Grafana
- ✅ Stronger security → Bcrypt rounds = 12
- ✅ Production SMTP → Real email provider (optional)
- ✅ DNS required → Domain name needed

**Migration Steps**:
```bash
# 1. Configure DNS
# Point staging.contravento.com to server IP

# 2. Copy environment
cp .env.dev .env.staging

# 3. Update .env.staging
# - Change APP_ENV=production
# - Increase BCRYPT_ROUNDS=12
# - Set DOMAIN=staging.contravento.com
# - Configure Grafana credentials

# 4. Deploy
./deploy.sh staging

# 5. Verify SSL
curl -I https://staging.contravento.com
```

#### From Staging to Production

**What Changes**:
- ✅ High availability → 3+ backend replicas
- ✅ Auto-scaling → Dynamic resource adjustment
- ✅ Stronger secrets → 128-char SECRET_KEY, 48-char DB password
- ✅ Stricter logging → LOG_LEVEL=WARNING
- ✅ Production database → Separate infrastructure
- ✅ Enhanced monitoring → Full observability stack

**Migration Steps**:
1. Review [Production Mode Guide](./prod.md)
2. Complete [Production Checklist](../guides/production-checklist.md)
3. Configure production infrastructure (load balancer, etc.)
4. Deploy with `./deploy.sh prod`

### Related Documentation

- **[Dev Mode](./dev.md)** - Previous mode in progression
- **[Production Mode](./prod.md)** - Next mode in progression
- **[Environment Variables Guide](../guides/environment-variables.md)** - Configuration reference
- **[Production Checklist](../guides/production-checklist.md)** - Pre-deployment validation

---

## Resource Requirements

**Minimum**:
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 20 GB
- **Network**: 100 Mbps
- **Bandwidth**: 100 GB/month

**Recommended**:
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB (with daily backups)
- **Network**: 1 Gbps
- **Bandwidth**: 500 GB/month

**Estimated Costs** (cloud hosting):
- AWS t3.large (2 vCPU, 8 GB RAM): ~$60/month
- DigitalOcean Droplet (4 CPU, 8 GB RAM): ~$48/month
- Hetzner Cloud CPX31 (4 vCPU, 8 GB RAM): ~€15/month

---

## Security Considerations

**Staging Security Best Practices**:
- ✅ Use production-strength secrets (min 96 chars for SECRET_KEY)
- ✅ Rotate secrets every 90 days
- ✅ Restrict Grafana/Prometheus to internal network only
- ✅ Enable firewall rules (allow only HTTPS + SSH)
- ✅ Use separate database from production
- ✅ Regularly update Docker images
- ❌ Do NOT use production database
- ❌ Do NOT use production API keys (use staging/sandbox)
- ❌ Do NOT expose monitoring ports to public internet

**Firewall Rules** (example for UFW):
```bash
# Allow HTTPS
sudo ufw allow 443/tcp

# Allow HTTP (for ACME challenge)
sudo ufw allow 80/tcp

# Allow SSH (restrict to known IPs)
sudo ufw allow from 203.0.113.0/24 to any port 22

# Deny all other inbound
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

**Access Control**:
```bash
# Restrict monitoring to VPN or SSH tunnel
# Do NOT expose ports 3000 (Grafana) and 9090 (Prometheus) to public

# Access via SSH tunnel:
ssh -L 3000:localhost:3000 -L 9090:localhost:9090 user@staging-server
```

---

**Last Updated**: 2026-02-06
**Document Version**: 1.0
**Feedback**: Report issues or suggest improvements via GitHub Issues
