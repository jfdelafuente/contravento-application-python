# Deployment Guide - ContraVento Backend

Guía completa para desplegar ContraVento en producción.

## Índice

- [Pre-requisitos](#pre-requisitos)
- [Deployment con Docker](#deployment-con-docker)
- [PostgreSQL Setup](#postgresql-setup)
- [Migrations](#migrations)
- [Production Checklist](#production-checklist)
- [Monitoreo](#monitoreo)

---

## Pre-requisitos

### Software Requerido

- Docker 24.0+ y Docker Compose 2.0+
- PostgreSQL 14+ (si no usa Docker)
- Python 3.11+ (para desarrollo local)
- Git

### Servicios Externos

- **SMTP Provider**: SendGrid, AWS SES, Mailgun, o Gmail
- **Dominio**: Con DNS configurado
- **SSL Certificate**: Let's Encrypt (recomendado) o certificado propio
- **Monitoreo** (opcional): Sentry, DataDog, CloudWatch

---

## Deployment con Docker

### T249: Dockerfile Configuration

El `Dockerfile` está optimizado para producción con:
- ✅ Multi-stage build (imagen pequeña)
- ✅ Non-root user (seguridad)
- ✅ Health checks
- ✅ Production dependencies only

### T250: Docker Compose Setup

**Servicios incluidos:**
- `backend` - FastAPI application
- `postgres` - PostgreSQL 16
- `redis` - Redis 7 (caching)
- `mailhog` - Email testing (development only)
- `pgadmin` - Database UI (development only)

### Quick Start

1. **Clonar repositorio:**
```bash
git clone <repo-url>
cd contravento-application-python
```

2. **Configurar variables de entorno:**
```bash
cp backend/.env.prod.example backend/.env.prod
# Editar .env.prod con valores reales
nano backend/.env.prod
```

3. **Generar SECRET_KEY fuerte:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Copiar output a SECRET_KEY en .env.prod
```

4. **Iniciar servicios:**
```bash
# Production (solo backend, postgres, redis)
docker-compose --env-file backend/.env.prod up -d

# Development (incluye mailhog, pgadmin)
docker-compose --env-file backend/.env --profile development up -d
```

5. **Verificar deployment:**
```bash
# Check logs
docker-compose logs -f backend

# Health check
curl http://localhost:8000/health

# API docs (solo si APP_ENV=development)
open http://localhost:8000/docs
```

### Detener Servicios

```bash
docker-compose down

# Con limpieza de volúmenes (CUIDADO: borra datos)
docker-compose down -v
```

---

## PostgreSQL Setup

### T251: Test Backend with PostgreSQL

#### Opción 1: Docker Compose (Recomendado)

Ya incluido en `docker-compose.yml`:

```yaml
postgres:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: contravento
    POSTGRES_USER: contravento_user
    POSTGRES_PASSWORD: ${DB_PASSWORD}
```

Conectarse:
```bash
docker exec -it contravento-db psql -U contravento_user -d contravento
```

#### Opción 2: PostgreSQL Local

**Instalar PostgreSQL:**

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql@16

# Windows
# Descargar de: https://www.postgresql.org/download/windows/
```

**Crear base de datos:**

```bash
# Conectar como superuser
sudo -u postgres psql

# Crear usuario y database
CREATE USER contravento_user WITH PASSWORD 'your_password';
CREATE DATABASE contravento OWNER contravento_user;
GRANT ALL PRIVILEGES ON DATABASE contravento TO contravento_user;
\q
```

**Configurar DATABASE_URL:**

```bash
# En .env o .env.prod
DATABASE_URL=postgresql+asyncpg://contravento_user:your_password@localhost:5432/contravento
```

#### Opción 3: PostgreSQL en la Nube

**Providers recomendados:**
- AWS RDS (PostgreSQL)
- Google Cloud SQL
- Azure Database for PostgreSQL
- Supabase
- Railway
- Neon

**Configuración típica:**

```bash
DATABASE_URL=postgresql+asyncpg://user:password@host.region.provider.com:5432/database?ssl=require
```

### Verificar Conexión

```python
# Test connection
python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test():
    engine = create_async_engine('postgresql+asyncpg://...')
    async with engine.connect() as conn:
        result = await conn.execute('SELECT version()')
        print(result.scalar())
    await engine.dispose()

asyncio.run(test())
"
```

---

## Migrations

### T253: Verify Migrations with PostgreSQL

#### Ejecutar Migraciones

```bash
# Con Docker
docker-compose exec backend alembic upgrade head

# Local
cd backend
poetry run alembic upgrade head
```

#### Verificar Migraciones

```bash
# Ver historial
alembic history

# Ver estado actual
alembic current

# Ver migraciones pendientes
alembic heads
```

#### Migraciones Existentes

**User Profiles (001-user-profiles):**

```text
001_initial_auth_schema.py        - Users, profiles, password resets
002_add_privacy_settings.py       - Privacy columns
003_stats_and_achievements.py     - Stats and achievements
004_social_features.py            - Follow relationships
```

**Travel Diary (002-travel-diary):**

```text
005_travel_diary_trips.py         - Trips, photos, locations, tags
006_trip_tags_association.py      - Trip-tag many-to-many relationship
```

#### Testing Migrations

**Test de upgrade:**

```bash
# Rollback to base
alembic downgrade base

# Upgrade to head
alembic upgrade head

# Verify all tables created
docker exec contravento-db psql -U contravento_user -d contravento -c "\dt"
```

**Expected tables:**

**User Profiles:**
- users
- user_profiles
- password_resets
- user_stats
- achievements
- user_achievements
- follows

**Travel Diary:**
- trips
- trip_photos
- trip_locations
- tags
- trip_tags (association table)

**System:**

- alembic_version

#### Rollback en Caso de Error

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade 003

# Rollback all
alembic downgrade base
```

#### Crear Nueva Migración

```bash
# Auto-generate from models
alembic revision --autogenerate -m "add new feature"

# Manual migration
alembic revision -m "add custom index"
```

---

## Production Checklist

### Antes de Deploy

- [ ] **Environment Variables**
  - [ ] `APP_ENV=production`
  - [ ] `DEBUG=false`
  - [ ] Strong `SECRET_KEY` (64+ chars)
  - [ ] Strong `DB_PASSWORD` (16+ chars)
  - [ ] Strong `REDIS_PASSWORD` (16+ chars)
  - [ ] `BCRYPT_ROUNDS=12` or higher

- [ ] **Database**
  - [ ] PostgreSQL configured (not SQLite)
  - [ ] Database backups enabled
  - [ ] Connection pooling configured
  - [ ] Migrations tested

- [ ] **Email**
  - [ ] Real SMTP provider configured
  - [ ] `SMTP_TLS=true`
  - [ ] Sender domain verified
  - [ ] Test emails working

- [ ] **Security**
  - [ ] HTTPS enforced (via reverse proxy)
  - [ ] CORS restricted to domain only
  - [ ] Firewall rules configured
  - [ ] Rate limiting enabled
  - [ ] SSL certificates valid

- [ ] **Monitoring**
  - [ ] Error tracking (Sentry)
  - [ ] Log aggregation
  - [ ] Health checks configured
  - [ ] Alerts configured

- [ ] **Code Quality**
  - [ ] All tests passing
  - [ ] Coverage ≥90%
  - [ ] Linting passing
  - [ ] Type checking passing

### Después de Deploy

- [ ] Health check responds: `curl https://domain.com/health`
- [ ] API responds: `curl https://domain.com/`
- [ ] Registration flow works end-to-end
- [ ] Email delivery works
- [ ] Database connections stable
- [ ] Logs show no errors
- [ ] Performance within targets (<500ms auth, <200ms profiles)

---

## Reverse Proxy (Nginx)

### Configuración Nginx

```nginx
# /etc/nginx/sites-available/contravento

upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name contravento.com www.contravento.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name contravento.com www.contravento.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/contravento.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/contravento.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to backend
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files - Profile photos
    location /storage/profile_photos/ {
        alias /app/storage/profile_photos/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Static files - Trip photos
    location /storage/trip_photos/ {
        alias /app/storage/trip_photos/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/contravento_access.log;
    error_log /var/log/nginx/contravento_error.log;
}
```

### SSL con Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d contravento.com -d www.contravento.com

# Auto-renewal (cron)
sudo certbot renew --dry-run
```

---

## Monitoreo

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f redis

# Specific time range
docker-compose logs --since 1h backend

# Filter errors
docker-compose logs backend | grep ERROR
```

### Métricas de Sistema

```bash
# Container stats
docker stats

# Database connections
docker exec contravento-db psql -U contravento_user -d contravento -c "
SELECT count(*) FROM pg_stat_activity WHERE datname = 'contravento';
"

# Redis info
docker exec contravento-redis redis-cli INFO
```

### Health Checks

```bash
# Backend health
curl https://contravento.com/health

# Database health
docker exec contravento-db pg_isready -U contravento_user

# Redis health
docker exec contravento-redis redis-cli ping
```

---

## Escalado

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
```

### Load Balancer

Usar Nginx o cloud load balancer (AWS ALB, GCP Load Balancer).

### Database Read Replicas

```python
# config.py
DATABASE_WRITE_URL = "postgresql+asyncpg://..."
DATABASE_READ_URL = "postgresql+asyncpg://read-replica:5432/..."
```

---

## Troubleshooting

### Backend no inicia

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - DATABASE_URL incorrect
# - SECRET_KEY missing
# - Migrations not run
```

### Database connection failed

```bash
# Verify postgres is running
docker-compose ps postgres

# Check connection
docker exec contravento-db pg_isready

# Reset database
docker-compose down postgres
docker volume rm contravento_postgres_data
docker-compose up -d postgres
```

### Migrations failed

```bash
# Check current version
alembic current

# Try manual downgrade/upgrade
alembic downgrade -1
alembic upgrade head

# Check database state
docker exec contravento-db psql -U contravento_user -d contravento -c "SELECT * FROM alembic_version;"
```

---

## Backup & Recovery

### Database Backup

```bash
# Manual backup
docker exec contravento-db pg_dump -U contravento_user contravento > backup_$(date +%Y%m%d).sql

# Automated backup (cron)
0 2 * * * docker exec contravento-db pg_dump -U contravento_user contravento > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Restore

```bash
# Restore from backup
docker exec -i contravento-db psql -U contravento_user contravento < backup_20250123.sql
```

---

## Next Steps

- Configure CI/CD pipeline (GitHub Actions, GitLab CI)
- Set up monitoring (Sentry, DataDog)
- Configure auto-scaling
- Implement blue-green deployment
- Set up staging environment
