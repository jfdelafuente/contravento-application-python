# ContraVento - Docker Multi-Environment Deployment Guide

This guide explains how to deploy ContraVento across different environments using Docker Compose with environment-specific overlays.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Environment Types](#environment-types)
3. [Quick Start](#quick-start)
4. [Environment Details](#environment-details)
5. [Configuration Management](#configuration-management)
6. [Deployment Commands](#deployment-commands)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)

---

## Architecture Overview

ContraVento uses a **multi-file Docker Compose approach** with:

- **Base file** (`docker-compose.yml`): Common service definitions
- **Overlay files** (`docker-compose.<env>.yml`): Environment-specific configurations
- **Environment files** (`.env.<env>`): Environment variables

### Service Stack

| Service | Description | All Envs | Local | Dev | Staging | Prod |
|---------|-------------|:--------:|:-----:|:---:|:-------:|:----:|
| **postgres** | PostgreSQL 16 database | ✅ | ✅ | ✅ | ✅ | ✅ |
| **redis** | Redis 7 cache | ✅ | ✅ | ✅ | ✅ | ✅ |
| **backend** | FastAPI application | ✅ | ✅ | ✅ | ✅ | ✅ |
| **mailhog** | Email testing | ❌ | ✅ | ❌ | ❌ | ❌ |
| **pgadmin** | Database UI | ❌ | ✅ | ❌ | ❌ | ❌ |
| **nginx** | Reverse proxy | ❌ | ❌ | ✅ | ✅ | ✅ |
| **certbot** | SSL certificates | ❌ | ❌ | ❌ | ❌ | ✅ |
| **prometheus** | Metrics collection | ❌ | ❌ | ❌ | ✅ | ✅ |
| **grafana** | Metrics dashboards | ❌ | ❌ | ❌ | ✅ | ✅ |
| **exporters** | Metrics exporters | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## Environment Types

### 1. LOCAL (Development)

**Purpose**: Local development with hot reload and debugging tools

**Characteristics**:
- ✅ Hot reload for code changes
- ✅ Debug mode enabled
- ✅ MailHog for email testing
- ✅ pgAdmin for database management
- ✅ All ports exposed
- ✅ Fast bcrypt (4 rounds)
- ✅ Verbose logging

**Use when**: Developing features, writing code, debugging issues

---

### 2. DEV (Integration)

**Purpose**: Integration testing with production-like build

**Characteristics**:
- ✅ Production build (no hot reload)
- ✅ Nginx reverse proxy
- ✅ Real SMTP server
- ❌ No debug mode
- ✅ Moderate bcrypt (10 rounds)
- ✅ Structured logging (JSON)

**Use when**: Testing integrations, CI/CD pipelines, team testing

---

### 3. STAGING (Pre-Production)

**Purpose**: Production mirror for final testing

**Characteristics**:
- ✅ Identical to production
- ✅ Monitoring (Prometheus + Grafana)
- ✅ SSL/TLS
- ✅ Resource limits
- ✅ Automated backups
- ✅ Full security (bcrypt 12)

**Use when**: Final testing before production, client demos, UAT

---

### 4. PROD (Production)

**Purpose**: Live production environment

**Characteristics**:
- ✅ Maximum security (bcrypt 12-14)
- ✅ High availability (3 backend replicas)
- ✅ Auto-scaling
- ✅ Automated SSL renewal
- ✅ Full monitoring stack
- ✅ Log aggregation
- ✅ Automated backups
- ✅ Rate limiting

**Use when**: Serving real users

---

## Quick Start

### Prerequisites

```bash
# Install Docker and Docker Compose
# Verify installation
docker --version
docker-compose --version
```

### 1. Clone and Setup

```bash
cd contravento-application-python

# Copy environment files
cp .env.local.example .env.local
cp .env.dev.example .env.dev
cp .env.staging.example .env.staging
cp .env.prod.example .env.prod
```

### 2. Configure Environment

Edit `.env.<environment>` and set required variables:

```bash
# CRITICAL: Generate strong SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Edit environment file
nano .env.local  # or vim, code, etc.
```

**Required variables**:
- `SECRET_KEY` (min 32 chars for local, min 64 for prod)
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `SMTP_*` (for email functionality)

### 3. Deploy

```bash
# Linux/Mac
./deploy.sh local

# Windows PowerShell
.\deploy.ps1 local
```

### 4. Verify

```bash
# Check running containers
docker ps

# View logs
./deploy.sh local logs

# Test API
curl http://localhost:8000/health
```

---

## Environment Details

### LOCAL Environment

#### Files
- `docker-compose.yml` (base)
- `docker-compose.local.yml` (overlay)
- `.env.local` (configuration)

#### Start Command
```bash
# Linux/Mac
./deploy.sh local

# Or manual
docker-compose -f docker-compose.yml -f docker-compose.local.yml --env-file .env.local up -d
```

#### Access Points
| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| MailHog UI | http://localhost:8025 | - |
| pgAdmin | http://localhost:5050 | See `.env.local` |

#### Configuration Highlights
```bash
# .env.local
APP_ENV=local
DEBUG=true
BCRYPT_ROUNDS=4  # Fast for development
LOG_LEVEL=DEBUG
SMTP_HOST=mailhog  # No real emails sent
```

---

### DEV Environment

#### Files
- `docker-compose.yml` (base)
- `docker-compose.dev.yml` (overlay)
- `.env.dev` (configuration)

#### Start Command
```bash
./deploy.sh dev
```

#### Access Points
| Service | URL |
|---------|-----|
| Backend API | http://dev.contravento.local:8000 |
| API Docs | http://dev.contravento.local:8000/docs |

#### Configuration Highlights
```bash
# .env.dev
APP_ENV=development
DEBUG=false
BCRYPT_ROUNDS=10  # Moderate security
LOG_FORMAT=json
SMTP_HOST=smtp.mailtrap.io  # Real SMTP for testing
```

---

### STAGING Environment

#### Files
- `docker-compose.yml` (base)
- `docker-compose.staging.yml` (overlay)
- `.env.staging` (configuration)

#### Start Command
```bash
./deploy.sh staging
```

#### Access Points
| Service | URL | Notes |
|---------|-----|-------|
| Backend API | https://staging.contravento.com | SSL required |
| Grafana | http://localhost:3000 | Monitoring |
| Prometheus | http://localhost:9090 | Metrics |

#### Configuration Highlights
```bash
# .env.staging
APP_ENV=production
DEBUG=false
BCRYPT_ROUNDS=12  # Production-level security
CORS_ORIGINS=https://staging.contravento.com
```

---

### PROD Environment

#### Files
- `docker-compose.yml` (base)
- `docker-compose.prod.yml` (overlay)
- `.env.prod` (configuration)

#### Start Command
```bash
./deploy.sh prod
```

#### Access Points
| Service | URL | Notes |
|---------|-----|-------|
| Backend API | https://api.contravento.com | SSL enforced |
| Monitoring | https://monitoring.contravento.com | Via Nginx proxy |

#### Configuration Highlights
```bash
# .env.prod
APP_ENV=production
DEBUG=false
BCRYPT_ROUNDS=14  # Maximum security
LOG_LEVEL=WARNING  # Only warnings/errors
# Backend replicas: 3 (high availability)
```

---

## Configuration Management

### Environment Variable Precedence

Docker Compose resolves variables in this order (highest to lowest):

1. **Shell environment variables** (`export VAR=value`)
2. **--env-file parameter** (`.env.<env>`)
3. **Default values** (`${VAR:-default}`)

### Security Best Practices

#### 1. Secret Management

**❌ Never commit secrets to git**

```bash
# .gitignore (already configured)
.env
.env.*
!.env.*.example
```

**✅ Use secret management tools for production**:
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager

#### 2. Generate Strong Keys

```bash
# SECRET_KEY (min 64 chars for production)
python -c "import secrets; print(secrets.token_urlsafe(96))"

# Database password (min 32 chars)
openssl rand -base64 48

# Redis password
openssl rand -base64 32
```

#### 3. Rotate Secrets Regularly

- **Production**: Every 90 days minimum
- **Staging**: Every 180 days
- **Development**: Annually or after security incidents

---

## Deployment Commands

### Using Scripts (Recommended)

```bash
# Start environment
./deploy.sh <env>              # Linux/Mac
.\deploy.ps1 <env>              # Windows

# Stop environment
./deploy.sh <env> down
.\deploy.ps1 <env> down

# View logs (follow mode)
./deploy.sh <env> logs
.\deploy.ps1 <env> logs

# Show running containers
./deploy.sh <env> ps
.\deploy.ps1 <env> ps

# Restart environment
./deploy.sh <env> restart
.\deploy.ps1 <env> restart
```

### Manual Commands

```bash
# Start
docker-compose -f docker-compose.yml -f docker-compose.<env>.yml --env-file .env.<env> up -d

# Stop
docker-compose -f docker-compose.yml -f docker-compose.<env>.yml --env-file .env.<env> down

# Stop and remove volumes (⚠️  DELETES DATA)
docker-compose -f docker-compose.yml -f docker-compose.<env>.yml --env-file .env.<env> down -v

# View logs
docker-compose -f docker-compose.yml -f docker-compose.<env>.yml --env-file .env.<env> logs -f

# Rebuild services
docker-compose -f docker-compose.yml -f docker-compose.<env>.yml --env-file .env.<env> build

# Run database migrations
docker-compose -f docker-compose.yml -f docker-compose.<env>.yml --env-file .env.<env> exec backend poetry run alembic upgrade head
```

---

## Monitoring and Logging

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Since timestamp
docker-compose logs --since 2024-01-01T00:00:00 backend
```

### Monitoring Stack (Staging/Production)

#### Prometheus
- **URL**: http://localhost:9090 (staging) or https://monitoring.contravento.com/prometheus (prod)
- **Purpose**: Metrics collection
- **Retention**: 30 days

#### Grafana
- **URL**: http://localhost:3000 (staging) or https://monitoring.contravento.com (prod)
- **Purpose**: Metrics visualization
- **Default credentials**: See `.env.<env>` (`GRAFANA_ADMIN_USER/PASSWORD`)

#### Key Metrics
- API response times
- Request rate
- Error rate
- Database connections
- Redis hit/miss ratio
- System resources (CPU, memory, disk)

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Change port in .env file
BACKEND_PORT=8001
```

#### 2. Database Connection Failed

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# View PostgreSQL logs
docker logs contravento-db-<env>

# Test connection
docker exec contravento-db-<env> psql -U <user> -d <database> -c "SELECT 1"

# Check DATABASE_URL matches container credentials
grep DATABASE_URL .env.<env>
```

#### 3. Permission Denied on Scripts

```bash
# Make scripts executable
chmod +x deploy.sh
chmod +x diagnose-postgres.sh
```

#### 4. Containers Not Starting

```bash
# Check for errors
docker-compose logs

# Remove old containers and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

#### 5. SSL Certificate Issues (Production)

```bash
# Check Certbot logs
docker logs contravento-certbot

# Manual certificate renewal
docker-compose exec certbot certbot renew

# Verify certificate
openssl s_client -connect api.contravento.com:443 -servername api.contravento.com
```

---

## Security Best Practices

### Pre-Production Checklist

#### Configuration
- [ ] All passwords are strong (min 32 chars)
- [ ] SECRET_KEY is unique per environment (min 64 chars)
- [ ] DEBUG=false
- [ ] CORS restricted to specific domains (no `*`)
- [ ] SMTP_TLS=true
- [ ] SSL certificates installed and auto-renewing

#### Database
- [ ] PostgreSQL with strong password
- [ ] Automated backups configured and tested
- [ ] Backup restoration tested
- [ ] Database not exposed to public internet

#### Monitoring
- [ ] Prometheus + Grafana configured
- [ ] Alerts configured (email, Slack, PagerDuty)
- [ ] Uptime monitoring enabled
- [ ] Log aggregation configured

#### Security
- [ ] Firewall configured (only ports 80, 443 exposed)
- [ ] Rate limiting enabled
- [ ] File upload validation enabled
- [ ] SQL injection prevention (ORM only)
- [ ] XSS prevention (HTML sanitization)

### Production-Only Checklist

- [ ] High availability (multiple backend replicas)
- [ ] Load balancer configured
- [ ] CDN configured for static assets
- [ ] Automated backups to external storage
- [ ] Disaster recovery plan documented and tested
- [ ] Incident response plan defined
- [ ] On-call rotation established
- [ ] Post-mortem process defined

---

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)

---

## Support

For issues, questions, or contributions:

- **GitHub Issues**: [github.com/contravento/issues](https://github.com/contravento/issues)
- **Documentation**: See `backend/docs/` directory
- **API Docs**: https://api.contravento.com/docs

---

**Last Updated**: 2026-01-07
