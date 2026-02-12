# Production Deployment Mode - Live Production Environment

**Purpose**: Live production environment serving real users with high availability and auto-scaling

**Target Users**: DevOps engineers, SRE teams, production deployment leads

**Difficulty**: Expert

**Estimated Setup Time**: 120-180 minutes (initial deployment)

**Prerequisites**:
- Docker 24.0+ and Docker Compose 2.0+ (or Docker Swarm/Kubernetes)
- Production-grade server infrastructure (min 4 CPU, 8 GB RAM)
- Domain name with DNS access (e.g., api.contravento.com, contravento.com)
- SSL certificates (Let's Encrypt or commercial)
- Production SMTP provider (SendGrid, AWS SES, Mailgun)
- Backup strategy and external storage (S3, GCS, or equivalent)
- Monitoring and alerting infrastructure
- 24/7 on-call schedule established

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [High Availability Setup](#high-availability-setup)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Monitoring & Observability](#monitoring--observability)
8. [Backup & Recovery](#backup--recovery)
9. [Scaling](#scaling)
10. [Zero-Downtime Deployment](#zero-downtime-deployment)
11. [Security](#security)
12. [Disaster Recovery](#disaster-recovery)
13. [Troubleshooting](#troubleshooting)
14. [Related Modes](#related-modes)

---

## Overview

### What is Production Mode?

The **Production** deployment mode provides a live, high-availability environment for serving real users with enterprise-grade reliability, security, and performance. It includes automatic failover, load balancing, comprehensive monitoring, and disaster recovery capabilities.

**Key Characteristics**:
- ✅ High availability (3+ backend replicas, automatic failover)
- ✅ Auto-scaling (CPU/memory-based)
- ✅ Maximum security (bcrypt rounds = 14, 128-char SECRET_KEY)
- ✅ SSL/TLS with automatic renewal
- ✅ Full monitoring stack (Prometheus + Grafana + exporters)
- ✅ Log aggregation (CloudWatch, Elasticsearch, or Datadog)
- ✅ Automated backups to external storage (S3/GCS)
- ✅ Rate limiting and DDoS protection
- ✅ Zero-downtime deployments
- ✅ 24/7 uptime SLA (99.9%+)
- ❌ No debug mode (DEBUG=false, CRITICAL)
- ❌ No public error details (generic error messages only)
- ❌ No API documentation exposed (Swagger UI hidden)

### When to Use Production Mode

**Perfect For**:
- ✅ Serving real users in production
- ✅ Requires 24/7 uptime and automatic failover
- ✅ Compliance requirements (SOC2, HIPAA, GDPR)
- ✅ SLA commitments (99.9% uptime or higher)
- ✅ Handling high traffic (1000+ requests/minute)
- ✅ Financial transactions or sensitive data

**Not Suitable For**:
- ❌ Development or testing (use [local-dev](./local-dev.md) or [dev](./dev.md))
- ❌ Pre-production testing (use [staging](./staging.md))
- ❌ Learning or experimentation

### Comparison with Other Modes

| Feature | Production | Staging | Dev |
|---------|:----------:|:-------:|:---:|
| **Replicas** | 3+ (HA) | 1 | 1 |
| **Auto-scaling** | ✅ | ❌ | ❌ |
| **Bcrypt Rounds** | 14 (max) | 12 | 10 |
| **SECRET_KEY Length** | 128 chars | 96 chars | 64 chars |
| **SSL/TLS** | ✅ (HTTPS) | ✅ | ❌ |
| **Monitoring** | Full stack | Prometheus + Grafana | ❌ |
| **Log Level** | WARNING | INFO | INFO |
| **Debug Mode** | ❌ NEVER | ❌ | ❌ |
| **API Docs** | ❌ Hidden | ✅ | ✅ |
| **Backups** | Automated + External | Automated | Manual |
| **Startup Time** | ~60s | ~40s | ~20s |
| **Uptime SLA** | 99.9%+ | Best effort | Best effort |

---

## Quick Start

### ⚠️ CRITICAL PRE-DEPLOYMENT CHECKLIST

**DO NOT DEPLOY TO PRODUCTION** without completing:

1. [ ] **Staging validation complete** - All tests passing on [staging](./staging.md)
2. [ ] **Production checklist complete** - See [Production Checklist](../guides/production-checklist.md)
3. [ ] **Database backup verified** - Recent backup tested and restored successfully
4. [ ] **Rollback plan documented** - Know how to revert deployment
5. [ ] **On-call team notified** - Team aware of deployment window
6. [ ] **Monitoring configured** - Alerts and dashboards ready
7. [ ] **Secret rotation complete** - All production secrets unique and strong

### 1. Prerequisites Check

```bash
# Verify Docker is installed (server)
docker --version
# Required: 24.0+

# Verify Docker Compose
docker-compose --version
# Required: 2.0+

# Verify DNS is configured
nslookup api.contravento.com
# Should resolve to production load balancer IP

# Verify server specs (MINIMUM for production)
lscpu | grep "CPU(s):"        # Min 4 CPUs (8 recommended)
free -h | grep "Mem:"         # Min 8 GB RAM (16 GB recommended)
df -h | grep "/$"             # Min 50 GB disk (100 GB recommended)
```

### 2. Environment Setup

```bash
# Clone repository (production server)
git clone https://github.com/yourusername/contravento-application-python.git
cd contravento-application-python

# Checkout production branch or tag
git checkout v1.2.3  # Use stable release tag

# Copy environment template
cp .env.prod.example .env.prod
```

### 3. Generate VERY STRONG Secrets

**CRITICAL**: Production requires maximum-strength secrets.

```bash
# Generate VERY STRONG SECRET_KEY (min 128 characters)
python -c "import secrets; print(secrets.token_urlsafe(128))"

# Generate very strong database password (min 48 characters)
openssl rand -base64 48

# Generate very strong Redis password (min 32 characters)
openssl rand -base64 32

# Generate Grafana admin password (min 24 characters)
openssl rand -base64 24

# RECOMMENDED: Use secret manager instead of .env file
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
# - Google Secret Manager
```

### 4. Configure Environment Variables

**CRITICAL**: Edit `.env.prod` with PRODUCTION values:

```bash
# Application
APP_NAME=ContraVento
APP_ENV=production               # CRITICAL: Must be production!
DEBUG=false                      # CRITICAL: NEVER true in production!

# Security (MAXIMUM strength)
SECRET_KEY=<paste_128_char_secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
BCRYPT_ROUNDS=14                 # MAXIMUM security (2-4s per hash)

# Database (production credentials)
DATABASE_URL=postgresql+asyncpg://contravento_user:<STRONG_PASSWORD>@postgres:5432/contravento
POSTGRES_DB=contravento
POSTGRES_USER=contravento_user
POSTGRES_PASSWORD=<paste_48_char_db_password>

# Redis (production, DB index 0)
REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/0
REDIS_PASSWORD=<paste_32_char_redis_password>

# SMTP (PRODUCTION provider - SendGrid example)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid_api_key>
SMTP_FROM=noreply@contravento.com
SMTP_TLS=true                    # CRITICAL: Must be true!

# CORS (ONLY production domains)
CORS_ORIGINS=https://contravento.com,https://www.contravento.com

# Domain (for SSL certificate)
DOMAIN=api.contravento.com

# Logging (minimal in production)
LOG_LEVEL=WARNING                # Only warnings and errors
LOG_FORMAT=json                  # Structured logging for aggregation

# Monitoring (REQUIRED)
SENTRY_DSN=https://<key>@sentry.io/<production-project>
SENTRY_ENVIRONMENT=production
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<paste_24_char_grafana_password>

# Backup (external storage required)
BACKUP_S3_BUCKET=contravento-backups-prod
BACKUP_S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=<aws_access_key>
AWS_SECRET_ACCESS_KEY=<aws_secret_key>

# Rate Limiting (if enabled)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN=5/15m          # 5 attempts per 15 minutes
RATE_LIMIT_API=100/1m           # 100 requests per minute
```

### 5. Configure DNS

**Point production domains to load balancer IP**:

```bash
# DNS A Records (example)
# Type: A
# Name: api.contravento.com
# Value: 203.0.113.100 (load balancer IP)
# TTL: 300

# Type: A
# Name: contravento.com
# Value: 203.0.113.100 (same load balancer)
# TTL: 300

# Verify DNS propagation
dig api.contravento.com +short
dig contravento.com +short
# Both should return load balancer IP
```

### 6. Initial Database Setup

```bash
# Run migrations BEFORE deploying backend
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
  up -d postgres

# Wait for postgres healthy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod ps

# Run migrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
  run --rm backend poetry run alembic upgrade head

# Create admin user (production credentials!)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
  run --rm backend poetry run python scripts/user-mgmt/create_admin.py \
  --username admin --email admin@contravento.com --password "STRONG_PRODUCTION_PASSWORD"

# Seed essential data
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
  run --rm backend poetry run python scripts/seeding/seed_cycling_types.py
```

### 7. Deploy Production Environment

**Linux/Mac**:
```bash
./deploy.sh prod
```

**Windows PowerShell**:
```powershell
.\deploy.ps1 prod
```

**Manual** (all platforms):
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 8. Verify Deployment

**CRITICAL POST-DEPLOYMENT CHECKS**:

```bash
# 1. Health check (MUST return 200)
curl https://api.contravento.com/health
# Expected: {"status":"healthy","database":"connected"}

# 2. HTTPS enforced (HTTP redirects to HTTPS)
curl -I http://api.contravento.com
# Expected: HTTP/1.1 301 Moved Permanently, Location: https://...

# 3. SSL certificate valid
curl -I https://api.contravento.com
# Expected: HTTP/2 200, valid certificate (no errors)

# 4. API docs HIDDEN (CRITICAL security check)
curl https://api.contravento.com/docs
# Expected: 404 Not Found (docs MUST be hidden in production)

# 5. CORS configured correctly
curl -H "Origin: https://contravento.com" \
     -I https://api.contravento.com/health
# Expected: Access-Control-Allow-Origin: https://contravento.com

# 6. All replicas healthy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod ps
# Expected: All containers "Up (healthy)"

# 7. Monitoring active
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health # Grafana

# 8. Logs showing no errors
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod \
  logs backend | grep -i "error\|exception" | head -n 20
# Expected: No critical errors
```

### 9. Access Points (PRODUCTION)

| Service | URL | Access Control |
|---------|-----|----------------|
| **Backend API** | https://api.contravento.com | Public |
| **Frontend** | https://contravento.com | Public |
| **Grafana** | http://server-ip:3000 | VPN/SSH tunnel ONLY |
| **Prometheus** | http://server-ip:9090 | VPN/SSH tunnel ONLY |
| **Database** | server-ip:5432 | Internal network ONLY |

**CRITICAL**: Grafana, Prometheus, and Database MUST NOT be exposed to public internet. Use VPN or SSH tunnels.

---

## Architecture

### High-Level Production Stack

```
                    ┌──────────────────────────────────────┐
                    │         INTERNET USERS               │
                    └────────────────┬─────────────────────┘
                                     │
                                     ▼
                    ┌──────────────────────────────────────┐
                    │      CLOUDFLARE / AWS CLOUDFRONT     │
                    │      (CDN + DDoS Protection)         │
                    └────────────────┬─────────────────────┘
                                     │
                                     ▼
                    ┌──────────────────────────────────────┐
                    │    LOAD BALANCER (AWS ALB/NLB)       │
                    │    - SSL Termination                 │
                    │    - Health Checks                   │
                    │    - Auto-scaling groups             │
                    └────────────────┬─────────────────────┘
                                     │
                   ┌─────────────────┴─────────────────┐
                   │                                   │
                   ▼                                   ▼
        ┌────────────────────┐            ┌────────────────────┐
        │   Nginx (Port 443)  │            │   Nginx (Replica 2)│
        │   SSL/TLS Proxy     │            │   (Failover)       │
        └──────────┬──────────┘            └──────────┬─────────┘
                   │                                   │
                   └─────────────────┬─────────────────┘
                                     │
                   ┌─────────────────┴─────────────────┐
                   │                │                  │
                   ▼                ▼                  ▼
        ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
        │  Backend API  │  │  Backend API  │  │  Backend API  │
        │  (Replica 1)  │  │  (Replica 2)  │  │  (Replica 3)  │
        │  Port 8000    │  │  Port 8000    │  │  Port 8000    │
        └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
                │                  │                  │
                └──────────────────┴──────────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   │                               │
                   ▼                               ▼
        ┌────────────────────┐          ┌────────────────────┐
        │   PostgreSQL       │          │      Redis         │
        │   (Primary)        │          │    (Cache)         │
        │   Port 5432        │          │    Port 6379       │
        └──────────┬─────────┘          └────────────────────┘
                   │
                   │ (replicas for HA)
                   ▼
        ┌────────────────────┐
        │  PostgreSQL        │
        │  (Read Replicas)   │
        │  (Optional)        │
        └────────────────────┘

                MONITORING & OBSERVABILITY
        ┌──────────────────────────────────────┐
        │         Prometheus (Metrics)          │
        │            Port 9090                  │
        └────────────────┬─────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────────┐
        │      Grafana (Dashboards)             │
        │            Port 3000                  │
        └──────────────────────────────────────┘
        ┌──────────────────────────────────────┐
        │      Sentry (Error Tracking)          │
        │      External SaaS                    │
        └──────────────────────────────────────┘

                BACKUP & STORAGE
        ┌──────────────────────────────────────┐
        │      AWS S3 / Google Cloud Storage    │
        │      - Database backups (daily)       │
        │      - File uploads (photos, GPX)     │
        │      - Log archives                   │
        └──────────────────────────────────────┘
```

### Service Stack

**Core Services** (3+ replicas for HA):
- **nginx** (1-2 instances) - Reverse proxy, SSL termination, load balancing
- **backend** (3+ instances) - FastAPI application servers
- **postgres** (1 primary + optional read replicas) - Database
- **redis** (1-3 instances) - Cache and session store

**Monitoring Services**:
- **prometheus** - Metrics collection
- **grafana** - Metrics visualization
- **node-exporter** - System metrics
- **postgres-exporter** - Database metrics
- **redis-exporter** - Cache metrics

**Utility Services**:
- **certbot** - SSL certificate auto-renewal
- **log-shipper** (optional) - Forward logs to CloudWatch/Elasticsearch

### Network Architecture

**External Load Balancer**:
- AWS Application Load Balancer (ALB) or Network Load Balancer (NLB)
- Distributes traffic across Nginx instances
- SSL termination at LB or Nginx (or both)
- Health checks on `/health` endpoint
- Auto-scaling group integration

**Internal Network**: `contravento-network` (bridge or overlay)

**Internal DNS** (Docker Compose):
- `postgres:5432` - PostgreSQL primary
- `redis:6379` - Redis cache
- `backend:8000` - Backend API (load-balanced internally by Docker)
- `prometheus:9090` - Prometheus
- `grafana:3000` - Grafana

**Port Mappings** (production server):
- `443:443` - Nginx HTTPS (public)
- `80:80` - Nginx HTTP → HTTPS redirect (public)
- `3000:3000` - Grafana (INTERNAL ONLY - VPN/SSH tunnel)
- `9090:9090` - Prometheus (INTERNAL ONLY - VPN/SSH tunnel)
- `5432:5432` - PostgreSQL (INTERNAL ONLY - no external access)
- `6379:6379` - Redis (INTERNAL ONLY - no external access)

**Firewall Rules** (CRITICAL):
```bash
# Allow HTTPS
sudo ufw allow 443/tcp

# Allow HTTP (for ACME challenge and redirect)
sudo ufw allow 80/tcp

# Allow SSH (restrict to known IPs)
sudo ufw allow from 203.0.113.0/24 to any port 22

# DENY all other inbound (CRITICAL)
sudo ufw deny 3000/tcp   # Grafana
sudo ufw deny 9090/tcp   # Prometheus
sudo ufw deny 5432/tcp   # PostgreSQL
sudo ufw deny 6379/tcp   # Redis

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

### Storage Volumes

**Named Volumes** (persistent, backed up):
- `postgres_data` - Database files (daily backups to S3)
- `redis_data` - Redis persistence (optional backups)
- `backend_storage` - Uploaded files (photos, GPX) - **replicated to S3**
- `prometheus_data` - Metrics time-series (retain 90 days)
- `grafana_data` - Dashboards and configuration
- `ssl_certificates` - Let's Encrypt SSL certificates

**Backup Strategy**:
- Database: Full backup every 6 hours → S3 (retain 7 daily, 4 weekly, 12 monthly)
- Files: Uploaded photos/GPX replicated to S3 in real-time
- Logs: Shipped to CloudWatch/Elasticsearch (retain 30 days)
- Prometheus metrics: Local retention 90 days (remote write to Thanos optional)

---

## Configuration

### Production Environment Variables

**Complete `.env.prod` template**:

```bash
# ============================================================================
# ContraVento - Production Environment Configuration
# ============================================================================
# CRITICAL: Review all values before deployment
# NEVER commit this file to version control
# ============================================================================

# Application
APP_NAME=ContraVento
APP_ENV=production
DEBUG=false                      # CRITICAL: NEVER true in production!
ALLOWED_HOSTS=api.contravento.com,contravento.com

# Security (MAXIMUM strength)
SECRET_KEY=<128_char_secret_from_secret_manager>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
BCRYPT_ROUNDS=14                 # Maximum security (2-4s per hash)

# Database (production)
DATABASE_URL=postgresql+asyncpg://contravento_user:<STRONG_PASSWORD>@postgres:5432/contravento
POSTGRES_DB=contravento
POSTGRES_USER=contravento_user
POSTGRES_PASSWORD=<48_char_password>
DATABASE_POOL_SIZE=30            # Increased for production load
DATABASE_MAX_OVERFLOW=15         # Additional connections under load
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=1800

# Redis (production)
REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/0
REDIS_PASSWORD=<32_char_password>

# SMTP (production - SendGrid example)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid_api_key>
SMTP_FROM=noreply@contravento.com
SMTP_TLS=true

# CORS (ONLY production domains - NO wildcards!)
CORS_ORIGINS=https://contravento.com,https://www.contravento.com,https://api.contravento.com

# Domain & SSL
DOMAIN=api.contravento.com
SSL_EMAIL=ops@contravento.com

# Logging (minimal in production)
LOG_LEVEL=WARNING                # Only warnings and errors
LOG_FORMAT=json
LOG_FILE=/var/log/contravento/app.log  # If using file logging

# Monitoring & Error Tracking
SENTRY_DSN=https://<key>@sentry.io/<production-project>
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1   # Sample 10% of transactions
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<24_char_password>

# Backup & Storage
STORAGE_PATH=/app/storage
BACKUP_ENABLED=true
BACKUP_S3_BUCKET=contravento-backups-prod
BACKUP_S3_REGION=us-east-1
BACKUP_RETENTION_DAYS=90
AWS_ACCESS_KEY_ID=<aws_access_key>
AWS_SECRET_ACCESS_KEY=<aws_secret_key>

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_LOGIN=5/15m          # 5 attempts per 15 minutes
RATE_LIMIT_REGISTER=3/1h        # 3 registrations per hour per IP
RATE_LIMIT_API=100/1m           # 100 API requests per minute per user
RATE_LIMIT_UPLOAD=10/1m         # 10 file uploads per minute per user

# File Upload Limits
UPLOAD_MAX_SIZE_MB=10
UPLOAD_ALLOWED_EXTENSIONS=jpg,jpeg,png,webp,gpx

# Performance
WEB_CONCURRENCY=4                # Workers per backend instance
WORKER_CLASS=uvicorn.workers.UvicornWorker
WORKER_TIMEOUT=120               # 2 minutes

# Feature Flags (if using)
FEATURE_GPX_UPLOAD=true
FEATURE_SOCIAL_FEED=true
FEATURE_ACHIEVEMENTS=true

# ============================================================================
# DO NOT MODIFY BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================

# Internal service ports (Docker Compose)
POSTGRES_PORT=5432
REDIS_PORT=6379
BACKEND_PORT=8000
NGINX_PORT_HTTP=80
NGINX_PORT_HTTPS=443
GRAFANA_PORT=3000
PROMETHEUS_PORT=9090
```

### Database Configuration (PostgreSQL)

**Production-grade PostgreSQL settings**:

```yaml
# docker-compose.prod.yml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: ${POSTGRES_DB}
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  command: >
    postgres
    -c max_connections=200
    -c shared_buffers=512MB
    -c effective_cache_size=2GB
    -c maintenance_work_mem=128MB
    -c checkpoint_completion_target=0.9
    -c wal_buffers=16MB
    -c default_statistics_target=100
    -c random_page_cost=1.1
    -c effective_io_concurrency=200
    -c work_mem=5MB
    -c min_wal_size=1GB
    -c max_wal_size=4GB
    -c max_worker_processes=4
    -c max_parallel_workers_per_gather=2
    -c max_parallel_workers=4
    -c max_parallel_maintenance_workers=2
    -c log_min_duration_statement=1000  # Log queries >1s
    -c log_line_prefix='%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Nginx SSL Configuration (Production)

**Complete Nginx production config** (`nginx/prod.conf`):

```nginx
# HTTP → HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name api.contravento.com contravento.com www.contravento.com;

    # ACME challenge for SSL verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server (production)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.contravento.com contravento.com www.contravento.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.contravento.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.contravento.com/privkey.pem;
    ssl_dhparam /etc/letsencrypt/dhparam.pem;

    # SSL configuration (Mozilla Modern)
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    # Client upload size
    client_max_body_size 10M;
    client_body_buffer_size 128k;

    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    send_timeout 60s;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Backend API proxy (load balanced)
    location / {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Disable buffering for SSE (if used)
        proxy_buffering off;
    }

    # Auth endpoints (stricter rate limiting)
    location ~ ^/auth/(login|register|password-reset) {
        limit_req zone=auth_limit burst=3 nodelay;

        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check (no rate limiting, no logging)
    location /health {
        access_log off;
        proxy_pass http://backend/health;
    }

    # Static files (if serving from backend)
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Uploaded files (served via backend for access control)
    location /storage/ {
        internal;  # Only accessible via X-Accel-Redirect from backend
        alias /app/storage/;
    }
}

# Upstream backend servers (3 replicas)
upstream backend {
    least_conn;  # Least connections load balancing
    server backend-1:8000 weight=1 max_fails=3 fail_timeout=30s;
    server backend-2:8000 weight=1 max_fails=3 fail_timeout=30s;
    server backend-3:8000 weight=1 max_fails=3 fail_timeout=30s;
    keepalive 32;  # Connection pooling
}
```

---

## High Availability Setup

### Backend Replicas

**3+ replicas for automatic failover**:

```yaml
# docker-compose.prod.yml
services:
  backend:
    image: jfdelafuente/contravento-backend:latest
    deploy:
      replicas: 3                # 3 instances for HA
      update_config:
        parallelism: 1           # Update one at a time
        delay: 30s               # Wait 30s between updates
        failure_action: rollback # Auto-rollback on failure
      restart_policy:
        condition: on-failure
        max_attempts: 3
        delay: 10s
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

**Load Balancing Strategy**:
- Algorithm: Least connections (distributes to instance with fewest active connections)
- Health checks: Every 30s, remove unhealthy instances automatically
- Session affinity: None (stateless API, sessions in Redis)

### Database HA (Optional)

**PostgreSQL Replication** (for read scaling):

```yaml
# docker-compose.prod.yml
services:
  postgres-primary:
    image: postgres:16-alpine
    environment:
      POSTGRES_REPLICATION_MODE: master
    # ... (see Configuration section)

  postgres-replica:
    image: postgres:16-alpine
    environment:
      POSTGRES_REPLICATION_MODE: slave
      POSTGRES_MASTER_HOST: postgres-primary
    depends_on:
      - postgres-primary
```

**Note**: Full PostgreSQL HA (with automatic failover) typically requires:
- **Patroni** or **Stolon** (automatic failover)
- **etcd** or **Consul** (distributed consensus)
- **pgBouncer** (connection pooling)

For most deployments, single PostgreSQL with daily backups is sufficient.

### Redis HA

**Redis Sentinel** (automatic failover):

```yaml
# docker-compose.prod.yml (if using Redis Sentinel)
services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}

  redis-replica:
    image: redis:7-alpine
    command: redis-server --slaveof redis-master 6379 --requirepass ${REDIS_PASSWORD}

  redis-sentinel:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    volumes:
      - ./redis/sentinel.conf:/etc/redis/sentinel.conf:ro
```

**Simpler alternative**: Single Redis with daily snapshots (RDB) + AOF persistence.

---

## SSL/TLS Configuration

### Automatic SSL with Certbot

**Let's Encrypt automatic renewal**:

```yaml
# docker-compose.prod.yml
services:
  certbot:
    image: certbot/certbot:latest
    container_name: contravento-certbot-prod
    volumes:
      - ssl_certificates:/etc/letsencrypt
      - ./nginx/certbot:/var/www/certbot:ro
    command: >
      certonly --webroot --webroot-path=/var/www/certbot
      --email ops@contravento.com
      --agree-tos --no-eff-email
      -d api.contravento.com
      -d contravento.com
      -d www.contravento.com
    restart: unless-stopped

  # Renewal cron (runs every 12 hours)
  certbot-renew:
    image: certbot/certbot:latest
    volumes:
      - ssl_certificates:/etc/letsencrypt
      - ./nginx/certbot:/var/www/certbot:ro
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
    restart: unless-stopped
```

### SSL Best Practices

**Security Enhancements**:

1. **Generate Strong DH Parameters**:
   ```bash
   openssl dhparam -out nginx/dhparam.pem 4096
   ```

2. **Enable HSTS Preload**:
   - Submit domain to https://hstspreload.org
   - Add `Strict-Transport-Security` header with `preload` directive

3. **Test SSL Configuration**:
   ```bash
   # SSL Labs test
   https://www.ssllabs.com/ssltest/analyze.html?d=api.contravento.com

   # Expected grade: A+ with HSTS preload
   ```

4. **Monitor Certificate Expiry**:
   ```bash
   # Add to monitoring
   openssl s_client -connect api.contravento.com:443 -servername api.contravento.com 2>/dev/null | \
     openssl x509 -noout -dates
   ```

---

## Monitoring & Observability

### Prometheus + Grafana Stack

**Full monitoring configuration** in `docker-compose.prod.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: contravento-prometheus-prod
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    ports:
      - "9090:9090"  # INTERNAL ONLY - firewall blocked
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: contravento-grafana-prod
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3000:3000"  # INTERNAL ONLY - firewall blocked
    depends_on:
      - prometheus
    restart: unless-stopped

  # System metrics
  node-exporter:
    image: prom/node-exporter:latest
    container_name: contravento-node-exporter-prod
    command:
      - '--path.rootfs=/host'
    pid: host
    restart: unless-stopped
    volumes:
      - '/:/host:ro,rslave'

  # PostgreSQL metrics
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: contravento-postgres-exporter-prod
    environment:
      DATA_SOURCE_NAME: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}?sslmode=disable"
    depends_on:
      - postgres
    restart: unless-stopped

  # Redis metrics
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: contravento-redis-exporter-prod
    environment:
      REDIS_ADDR: "redis:6379"
      REDIS_PASSWORD: "${REDIS_PASSWORD}"
    depends_on:
      - redis
    restart: unless-stopped
```

### Key Metrics to Monitor

**API Performance**:
- Response time (p50, p95, p99)
- Request rate (requests/second)
- Error rate (4xx, 5xx responses)
- Endpoint-specific latency

**Database Health**:
- Connection pool usage
- Query duration (slow queries >1s)
- Transaction rate
- Cache hit ratio
- Database size growth

**System Resources**:
- CPU usage (per container and host)
- Memory usage
- Disk I/O
- Network throughput

**Business Metrics**:
- Active users (DAU/MAU)
- New registrations
- Trip creation rate
- Photo upload rate

### Alerting Rules

**Critical Alerts** (Prometheus `alert.rules.yml`):

```yaml
groups:
  - name: production_critical
    interval: 30s
    rules:
      # API down
      - alert: APIDown
        expr: up{job="backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Backend API is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute."

      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High 5xx error rate detected"

      # Database connection pool exhausted
      - alert: DBConnectionPoolExhausted
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool >80% utilized"

      # Disk usage high
      - alert: DiskSpaceRunningOut
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.15
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Disk space <15% remaining"

      # Memory usage high
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Memory usage >90%"
```

### Error Tracking (Sentry)

**Sentry Integration**:

```python
# src/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.SENTRY_ENVIRONMENT,
    traces_sample_rate=0.1,  # Sample 10% of transactions
    profiles_sample_rate=0.1,  # Enable profiling
    integrations=[
        FastApiIntegration(),
        SqlalchemyIntegration(),
    ],
    # Don't send sensitive data
    send_default_pii=False,
    before_send=sanitize_event,  # Custom sanitization
)
```

---

## Backup & Recovery

### Automated Database Backups

**Daily backups to S3**:

```yaml
# docker-compose.prod.yml
services:
  backup-cron:
    image: alpine:latest
    container_name: contravento-backup-cron-prod
    volumes:
      - ./scripts/backup.sh:/backup.sh:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      BACKUP_S3_BUCKET: ${BACKUP_S3_BUCKET}
      BACKUP_S3_REGION: ${BACKUP_S3_REGION}
    entrypoint: >
      /bin/sh -c "apk add --no-cache docker-cli aws-cli postgresql-client &&
      echo '0 */6 * * * /backup.sh' > /etc/crontabs/root &&
      crond -f -l 2"
    restart: unless-stopped
```

**Backup Script** (`scripts/backup.sh`):

```bash
#!/bin/sh
# Production database backup script
# Runs every 6 hours via cron

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="contravento_prod_${TIMESTAMP}.backup"
BACKUP_PATH="/tmp/${BACKUP_FILE}"

echo "[$(date)] Starting database backup..."

# Create backup using pg_dump
docker exec contravento-db-prod pg_dump \
  -U ${POSTGRES_USER} \
  -d ${POSTGRES_DB} \
  -F c \
  -b \
  -v \
  -f /tmp/${BACKUP_FILE}

# Copy backup from container to host
docker cp contravento-db-prod:/tmp/${BACKUP_FILE} ${BACKUP_PATH}

# Upload to S3
aws s3 cp ${BACKUP_PATH} \
  s3://${BACKUP_S3_BUCKET}/database/${BACKUP_FILE} \
  --region ${BACKUP_S3_REGION} \
  --storage-class STANDARD_IA

# Cleanup local backup
rm -f ${BACKUP_PATH}
docker exec contravento-db-prod rm -f /tmp/${BACKUP_FILE}

echo "[$(date)] Backup complete: s3://${BACKUP_S3_BUCKET}/database/${BACKUP_FILE}"

# Cleanup old backups (retain 7 daily, 4 weekly, 12 monthly)
# ... (implement retention policy)
```

### Backup Verification

**Test restore monthly**:

```bash
# Download recent backup from S3
aws s3 cp s3://${BACKUP_S3_BUCKET}/database/latest.backup /tmp/test_restore.backup

# Restore to test database
docker exec -i contravento-db-prod pg_restore \
  -U ${POSTGRES_USER} \
  -d contravento_test \
  --clean \
  /tmp/test_restore.backup

# Verify data integrity
docker exec contravento-db-prod psql -U ${POSTGRES_USER} -d contravento_test \
  -c "SELECT count(*) FROM users; SELECT count(*) FROM trips;"

# Cleanup test database
docker exec contravento-db-prod psql -U ${POSTGRES_USER} -c "DROP DATABASE contravento_test;"
```

### Disaster Recovery Plan

**RTO/RPO Targets**:
- **RPO** (Recovery Point Objective): 6 hours (backup frequency)
- **RTO** (Recovery Time Objective): 2 hours (restoration time)

**Recovery Procedure** (complete failure):

1. **Provision new infrastructure** (15 minutes):
   ```bash
   # Terraform or manual server provisioning
   # Install Docker, Docker Compose
   ```

2. **Restore database** (30 minutes):
   ```bash
   # Download latest backup from S3
   aws s3 cp s3://${BACKUP_S3_BUCKET}/database/latest.backup /tmp/restore.backup

   # Start PostgreSQL
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres

   # Restore database
   docker exec -i contravento-db-prod pg_restore \
     -U ${POSTGRES_USER} \
     -d ${POSTGRES_DB} \
     --clean \
     /tmp/restore.backup
   ```

3. **Deploy application** (30 minutes):
   ```bash
   # Pull latest code
   git clone https://github.com/yourusername/contravento-application-python.git
   cd contravento-application-python
   git checkout v1.2.3  # Stable release

   # Copy production .env (from secret manager)
   # ...

   # Deploy
   ./deploy.sh prod
   ```

4. **Verify and test** (45 minutes):
   - Run health checks
   - Test critical user flows
   - Verify monitoring dashboards
   - Update DNS if necessary

**Total Recovery Time**: ~2 hours

---

## Scaling

### Vertical Scaling (Increase Resources)

**Increase container resources**:

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4.0'      # Increase from 2.0
          memory: 4G       # Increase from 2G
        reservations:
          cpus: '2.0'
          memory: 2G
```

**Increase database connections**:

```bash
# In .env.prod
DATABASE_POOL_SIZE=50      # Increase from 30
DATABASE_MAX_OVERFLOW=25   # Increase from 15
```

**Increase workers per backend instance**:

```bash
# In .env.prod
WEB_CONCURRENCY=8          # Increase from 4
```

### Horizontal Scaling (More Replicas)

**Increase backend replicas**:

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 5          # Increase from 3
```

**Auto-scaling** (Docker Swarm or Kubernetes):

```yaml
# Docker Swarm example
services:
  backend:
    deploy:
      replicas: 3
      placement:
        max_replicas_per_node: 2
      update_config:
        parallelism: 1
        delay: 30s
      # Auto-scaling via external tool (Docker Swarm doesn't have built-in auto-scaling)
```

**Kubernetes Horizontal Pod Autoscaler** (if using K8s):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: contravento-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: contravento-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### Database Scaling

**Read Replicas** (for read-heavy workloads):

1. Set up PostgreSQL streaming replication
2. Configure read-only connections in backend:
   ```python
   # src/database.py
   read_engine = create_async_engine(
       settings.DATABASE_READ_URL,  # Points to read replica
       pool_size=20,
   )
   ```

3. Route read-only queries to replica:
   ```python
   # Read from replica
   async with read_engine.begin() as conn:
       result = await conn.execute(select(User))

   # Write to primary
   async with engine.begin() as conn:
       await conn.execute(insert(User).values(...))
   ```

**Connection Pooling** (pgBouncer):

```yaml
services:
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    environment:
      DATABASES_HOST: postgres
      DATABASES_PORT: 5432
      DATABASES_DBNAME: contravento
      PGBOUNCER_POOL_MODE: transaction
      PGBOUNCER_MAX_CLIENT_CONN: 1000
      PGBOUNCER_DEFAULT_POOL_SIZE: 50
    ports:
      - "6432:6432"
```

---

## Zero-Downtime Deployment

### Rolling Update Strategy

**Docker Compose** (basic rolling update):

```bash
# Update backend one replica at a time
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --scale backend=3 --no-recreate backend

# Health checks ensure old instances aren't removed until new ones are healthy
```

**Docker Swarm** (advanced rolling update):

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1           # Update 1 replica at a time
        delay: 30s               # Wait 30s between replicas
        failure_action: rollback # Auto-rollback on failure
        monitor: 60s             # Monitor for 60s after update
        max_failure_ratio: 0.3   # Allow 30% failures before rollback
      rollback_config:
        parallelism: 1
        delay: 10s
```

**Deployment Procedure**:

```bash
# 1. Tag release in git
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0

# 2. Build and push new Docker image
docker build -t jfdelafuente/contravento-backend:v1.3.0 ./backend
docker push jfdelafuente/contravento-backend:v1.3.0
docker tag jfdelafuente/contravento-backend:v1.3.0 jfdelafuente/contravento-backend:latest
docker push jfdelafuente/contravento-backend:latest

# 3. Run database migrations (if any)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec backend poetry run alembic upgrade head

# 4. Deploy with rolling update
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --no-deps backend

# 5. Monitor deployment
watch -n 2 'docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps'

# 6. Verify health checks
for i in {1..3}; do
  curl https://api.contravento.com/health
  sleep 5
done

# 7. Monitor error rate in Grafana
# - Check for spike in 5xx errors
# - Check response time increase
# - Check database connection errors

# 8. If issues detected, rollback:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  pull backend  # Pull previous image
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --no-deps backend
```

### Blue-Green Deployment (Advanced)

**For critical updates requiring instant rollback**:

1. Deploy new version (green) alongside current (blue)
2. Run smoke tests on green
3. Switch load balancer to green
4. Monitor for 30 minutes
5. Decommission blue or keep as hot standby

---

## Security

### Production Security Checklist

**Application Security**:
- [ ] `DEBUG=false` (CRITICAL - verified in .env.prod)
- [ ] API documentation hidden (`/docs` returns 404)
- [ ] Strong secrets (SECRET_KEY ≥128 chars, DB password ≥48 chars)
- [ ] Secrets stored in secret manager (not .env file)
- [ ] CORS restricted to production domains only
- [ ] Rate limiting enabled on auth endpoints
- [ ] File upload validation (MIME type, size, content)
- [ ] SQL injection protection (use SQLAlchemy ORM only)
- [ ] XSS protection (sanitize user input)
- [ ] CSRF protection (SameSite cookies)

**Network Security**:
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] HSTS enabled with preload
- [ ] Security headers configured (X-Frame-Options, CSP, etc.)
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Monitoring ports blocked (3000, 9090)
- [ ] Database port blocked (5432)
- [ ] Redis port blocked (6379)
- [ ] SSH key-based authentication only
- [ ] Fail2ban installed and configured

**Infrastructure Security**:
- [ ] Server OS patched and updated
- [ ] Docker images updated monthly
- [ ] Dependencies audited for vulnerabilities
- [ ] Backups encrypted at rest
- [ ] SSL certificates auto-renewed
- [ ] Access logs monitored for suspicious activity
- [ ] Intrusion detection system (IDS) configured
- [ ] DDoS protection enabled (Cloudflare/AWS Shield)

**Operational Security**:
- [ ] Principle of least privilege (minimal container permissions)
- [ ] Secrets rotated every 90 days
- [ ] Audit logs enabled and retained
- [ ] Incident response plan documented
- [ ] On-call schedule established
- [ ] Disaster recovery plan tested

### Vulnerability Scanning

**Scan Docker images**:

```bash
# Trivy scan
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image jfdelafuente/contravento-backend:latest

# Expected: No HIGH or CRITICAL vulnerabilities
```

**Dependency audit**:

```bash
# Backend (Python)
cd backend
poetry audit  # Or use safety
poetry show --outdated

# Frontend (npm)
cd frontend
npm audit
npm outdated
```

---

## Disaster Recovery

### Incident Response Procedure

**Severity Levels**:

**P0 - Critical** (Complete outage):
- Examples: API down, database corruption, data breach
- Response time: Immediate (15 minutes)
- On-call escalation: Automatic via PagerDuty

**P1 - Major** (Significant degradation):
- Examples: High error rate, slow response times, partial outage
- Response time: 1 hour
- On-call escalation: Manual

**P2 - Minor** (Minor issues):
- Examples: Non-critical feature broken, UI bugs
- Response time: Next business day
- On-call escalation: None

### Emergency Rollback

**Immediate rollback procedure** (< 5 minutes):

```bash
# 1. Checkout previous stable version
git checkout v1.2.3  # Previous release tag

# 2. Pull previous Docker image
docker pull jfdelafuente/contravento-backend:v1.2.3

# 3. Deploy previous version
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --no-deps backend

# 4. Rollback database migration (if needed)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec backend poetry run alembic downgrade -1

# 5. Verify health
curl https://api.contravento.com/health

# 6. Monitor error rate
# Check Grafana for reduction in 5xx errors

# 7. Post-mortem
# Document what went wrong, root cause, prevention measures
```

### Communication Plan

**Stakeholder Notification**:

1. **Users**: Status page (status.contravento.com)
2. **Team**: Slack #incidents channel
3. **Management**: Email to CTO/VP Engineering
4. **Customers** (B2B): Direct email/phone

**Status Page Updates**:
- Update every 30 minutes during incident
- Include ETA for resolution
- Post-mortem published within 48 hours

---

## Troubleshooting

### Common Production Issues

#### Issue 1: High Load / Slow Response Times

**Symptoms**: API response times >2s, timeouts

**Diagnosis**:
```bash
# Check backend resource usage
docker stats

# Check database connections
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Check slow queries
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

**Fixes**:
1. Scale horizontally (increase replicas)
2. Optimize slow queries (add indexes)
3. Enable caching (Redis)
4. Increase database connection pool

#### Issue 2: Memory Leak

**Symptoms**: Gradual memory increase, eventual OOM crash

**Diagnosis**:
```bash
# Monitor memory over time
watch -n 10 'docker stats --no-stream | grep backend'

# Check for memory leaks in Python
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec backend python -m memory_profiler src/main.py
```

**Fixes**:
1. Restart backend instances (temporary)
2. Identify leak source (use memory profiling)
3. Fix code and deploy patch
4. Add memory limits to prevent cascading failures

#### Issue 3: Database Connection Pool Exhausted

**Symptoms**: "connection pool timeout" errors

**Diagnosis**:
```bash
# Check active connections
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname='${POSTGRES_DB}';"

# Check max connections
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  -c "SHOW max_connections;"
```

**Fixes**:
1. Increase `DATABASE_POOL_SIZE` in .env.prod
2. Increase PostgreSQL `max_connections`
3. Implement connection pooling (pgBouncer)
4. Fix connection leaks in code

#### Issue 4: SSL Certificate Expiry

**Symptoms**: Browser shows "certificate expired" error

**Diagnosis**:
```bash
# Check certificate expiry
openssl s_client -connect api.contravento.com:443 -servername api.contravento.com 2>/dev/null | \
  openssl x509 -noout -dates
```

**Fixes**:
1. Manual renewal:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
     exec certbot certbot renew --force-renewal

   docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
     exec nginx nginx -s reload
   ```

2. Verify auto-renewal cron is running:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs certbot-renew
   ```

### Performance Tuning

**Optimize PostgreSQL**:

```sql
-- Analyze tables (update statistics)
ANALYZE VERBOSE;

-- Reindex if needed
REINDEX DATABASE contravento;

-- Vacuum (reclaim storage)
VACUUM ANALYZE;

-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY abs(correlation) DESC
LIMIT 20;
```

**Optimize Redis**:

```bash
# Check memory usage
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec redis redis-cli INFO memory

# Check hit rate
docker-compose -f docker-compose.yml -f docker-compose.prod.yml \
  exec redis redis-cli INFO stats | grep keyspace
```

---

## Related Modes

### Progression Path

```
Dev → Staging → Production (YOU ARE HERE)
```

**Migration from Staging**:

See [Production Checklist](../guides/production-checklist.md) for complete pre-deployment validation.

**Key Differences from Staging**:
- 3+ backend replicas (vs 1 in staging)
- Auto-scaling enabled
- Maximum security (BCRYPT_ROUNDS=14, 128-char secrets)
- Automated backups to external storage
- 24/7 monitoring and alerting
- Disaster recovery plan required

### Related Documentation

- **[Staging Mode](./staging.md)** - Pre-production testing environment
- **[Production Checklist](../guides/production-checklist.md)** - **MUST COMPLETE before deploying**
- **[Database Management](../guides/database-management.md)** - Backup and restore procedures
- **[Environment Variables Guide](../guides/environment-variables.md)** - Configuration reference
- **[Troubleshooting Guide](../guides/troubleshooting.md)** - Common issues

---

## Resource Requirements

**Minimum** (single-server deployment):
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB (SSD recommended)
- **Network**: 1 Gbps
- **Bandwidth**: 500 GB/month

**Recommended** (high-traffic production):
- **CPU**: 8 cores
- **RAM**: 16 GB
- **Disk**: 100 GB (SSD)
- **Network**: 10 Gbps
- **Bandwidth**: 2 TB/month

**Estimated Costs** (cloud hosting - single server):
- AWS t3.xlarge (4 vCPU, 16 GB RAM): ~$120/month
- DigitalOcean Droplet (8 CPU, 16 GB RAM): ~$96/month
- Hetzner Cloud CPX51 (16 vCPU, 32 GB RAM): ~€50/month

**Add-on Costs**:
- S3 storage (backups): ~$20/month
- Load balancer: ~$20/month
- Monitoring (Sentry): ~$26/month
- SMTP (SendGrid): ~$15/month
- **Total Estimated**: ~$180-200/month

---

**Last Updated**: 2026-02-06
**Document Version**: 1.0
**Feedback**: Report issues or suggest improvements via GitHub Issues

**⚠️ PRODUCTION DEPLOYMENT REQUIRES APPROVAL FROM:**
- DevOps Lead
- Engineering Manager
- CTO (for first production deployment)
