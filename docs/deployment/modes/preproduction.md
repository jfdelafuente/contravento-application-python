# Preproduction Deployment Mode - CI/CD Integration Environment

**Purpose**: Automated deployment environment for CI/CD pipelines (Jenkins, GitHub Actions)

**Target Users**: DevOps engineers, CI/CD pipeline developers, QA automation teams

**Difficulty**: Intermediate

**Estimated Setup Time**: 30-45 minutes

**Prerequisites**:
- Docker 24.0+ and Docker Compose 2.0+
- CI/CD server (Jenkins, GitHub Actions, GitLab CI)
- Access to Docker Hub or container registry
- Basic understanding of CI/CD pipelines

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [CI/CD Integration](#cicd-integration)
5. [Configuration](#configuration)
6. [Testing Workflows](#testing-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Related Modes](#related-modes)

---

## Overview

### What is Preproduction Mode?

The **Preproduction** deployment mode provides an automated testing environment that pulls pre-built Docker images from Docker Hub and deploys them for validation. It's designed for CI/CD pipelines to test deployments before promoting to staging or production.

**Key Characteristics**:
- ✅ Uses pre-built Docker images (no local builds)
- ✅ Pulls from Docker Hub (`jfdelafuente/contravento-backend:latest`)
- ✅ Automatic configuration (auto-generated SECRET_KEY)
- ✅ Fast spin-up/teardown (~20 seconds)
- ✅ Ephemeral environment (no persistent data retention)
- ✅ Ideal for automated testing in CI/CD pipelines
- ✅ PostgreSQL database (production-like)
- ✅ Frontend included (optional)
- ❌ No monitoring stack (lightweight for CI)
- ❌ No SSL/TLS (HTTP only, local access)
- ❌ No email UI (logs emails to console)

### When to Use Preproduction Mode

**Perfect For**:
- ✅ Jenkins CI/CD pipeline validation
- ✅ GitHub Actions deployment testing
- ✅ GitLab CI integration testing
- ✅ Automated smoke tests before staging
- ✅ Validating Docker image builds
- ✅ Quick deployment verification
- ✅ Local validation of production builds

**Not Suitable For**:
- ❌ Daily feature development (use [local-dev](./local-dev.md))
- ❌ Manual testing (use [staging](./staging.md))
- ❌ Production deployment (use [prod](./prod.md))

### Comparison with Other Modes

| Feature | Preproduction | Staging | Test |
|---------|:-------------:|:-------:|:----:|
| **Docker Build** | Pre-built (Hub) | Pre-built | Pre-built |
| **Database** | PostgreSQL | PostgreSQL | PostgreSQL/SQLite |
| **Frontend** | ✅ Optional | ✅ | ❌ |
| **Monitoring** | ❌ | ✅ | ❌ |
| **SSL** | ❌ | ✅ | ❌ |
| **Auto-config** | ✅ | ❌ | ✅ |
| **Startup Time** | ~20s | ~40s | ~15s |
| **Primary Use** | CI/CD validation | Pre-prod testing | Unit/integration tests |

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

# Verify access to Docker Hub
docker pull jfdelafuente/contravento-backend:latest
# Should download successfully
```

### 2. Quick Deployment (No Configuration Required)

**Linux/Mac**:
```bash
# Start preproduction environment
./run-jenkins-env.sh start

# Or with custom compose file:
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

**Windows PowerShell**:
```powershell
# Start preproduction environment
.\run-jenkins-env.ps1 start

# Or with custom compose file:
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

**That's it!** No `.env` file needed - all defaults are configured.

### 3. Verify Deployment

```bash
# Check all containers running
docker-compose -f docker-compose.preproduction.dev.yml ps

# Expected:
# contravento-db-preproduction          Up (healthy)
# contravento-backend-preproduction     Up (healthy)
# contravento-frontend-preproduction    Up (healthy) [if enabled]

# Test backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}

# Test frontend (if enabled)
curl -I http://localhost:5173
# Expected: HTTP/1.1 200 OK
```

### 4. Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Frontend** | http://localhost:5173 | React application (if enabled) |
| **Database** | localhost:5432 | PostgreSQL connection |

**Default Credentials**:
```
Database:
- Host: localhost
- Port: 5432
- Database: contravento_jenkins
- User: postgres
- Password: jenkins_test_password

Admin User (auto-created):
- Email: admin@example.com
- Password: jenkins
```

---

## Architecture

### Service Stack

```
┌─────────────────────────────────────────────────────────┐
│                     CI/CD PIPELINE                       │
│         (Jenkins, GitHub Actions, GitLab CI)             │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ (triggers deployment)
                 ▼
      ┌──────────────────────┐
      │   Docker Compose      │
      │   Preproduction      │
      └──────────┬───────────┘
                 │
                 │ (pulls images from Docker Hub)
                 ▼
      ┌──────────────────────┐
      │    Docker Hub         │
      │  - backend:latest     │
      │  - frontend:latest    │
      └──────────┬───────────┘
                 │
                 ▼
   ┌─────────────────────────────────┐
   │     LOCAL DEPLOYMENT             │
   │                                  │
   │  ┌─────────────────────────┐    │
   │  │  Frontend (Port 5173)    │    │
   │  │  Vite dev server         │    │
   │  └────────┬────────────────┘    │
   │           │                      │
   │           ▼                      │
   │  ┌─────────────────────────┐    │
   │  │  Backend API (Port 8000) │    │
   │  │  FastAPI                 │    │
   │  └────────┬────────────────┘    │
   │           │                      │
   │           ▼                      │
   │  ┌─────────────────────────┐    │
   │  │  PostgreSQL (Port 5432)  │    │
   │  │  contravento_jenkins     │    │
   │  └──────────────────────────┘    │
   └─────────────────────────────────┘
```

### Docker Image Source

**Images Built By**:
1. **PRIMARY**: GitHub Actions (`.github/workflows/docker-build-push.yml`)
   - Triggered on push to `develop` or `main` branches
   - Runs tests before building
   - Pushes to Docker Hub with tags: `latest`, `develop`, `v1.2.3`

2. **BACKUP**: Jenkins (`Jenkinsfile`)
   - Fallback if GitHub Actions fails
   - Manual trigger or scheduled builds
   - Same tagging strategy

**Image Registry**:
- Backend: `jfdelafuente/contravento-backend:latest`
- Frontend: `jfdelafuente/contravento-frontend:latest`

### Network Configuration

**Network**: `preproduction-network` (bridge driver)

**Port Mappings**:
- `8000:8000` - Backend API
- `5173:5173` - Frontend (Vite dev server)
- `5432:5432` - PostgreSQL
- `5050:80` - pgAdmin (optional)

**No Firewall Required**: Designed for local/internal use only.

---

## CI/CD Integration

### Jenkins Pipeline Example

**Complete Jenkinsfile**:

```groovy
pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.preproduction.dev.yml'
    }

    stages {
        stage('Cleanup Previous Environment') {
            steps {
                sh '''
                    docker-compose -f ${DOCKER_COMPOSE_FILE} down -v || true
                '''
            }
        }

        stage('Pull Latest Images') {
            steps {
                sh '''
                    docker pull jfdelafuente/contravento-backend:latest
                    docker pull jfdelafuente/contravento-frontend:latest
                '''
            }
        }

        stage('Start Environment') {
            steps {
                sh '''
                    docker-compose -f ${DOCKER_COMPOSE_FILE} up -d
                    sleep 30  # Wait for services to be healthy
                '''
            }
        }

        stage('Health Checks') {
            steps {
                sh '''
                    # Backend health check
                    curl -f http://localhost:8000/health || exit 1

                    # Database connectivity
                    docker-compose -f ${DOCKER_COMPOSE_FILE} exec -T postgres \
                        psql -U postgres -d contravento_jenkins -c "SELECT 1;"
                '''
            }
        }

        stage('Run Backend Tests') {
            steps {
                sh '''
                    docker-compose -f ${DOCKER_COMPOSE_FILE} exec -T backend \
                        poetry run pytest tests/ --cov=src --cov-report=term
                '''
            }
        }

        stage('Run Frontend Tests') {
            steps {
                sh '''
                    docker-compose -f ${DOCKER_COMPOSE_FILE} exec -T frontend \
                        npm test -- --run
                '''
            }
        }

        stage('E2E Tests') {
            steps {
                sh '''
                    docker-compose -f ${DOCKER_COMPOSE_FILE} exec -T frontend \
                        npm run test:e2e
                '''
            }
        }

        stage('Smoke Tests') {
            steps {
                sh '''
                    # Test registration endpoint
                    curl -X POST http://localhost:8000/auth/register \
                        -H "Content-Type: application/json" \
                        -d '{
                            "username": "testuser",
                            "email": "test@example.com",
                            "password": "TestPass123!",
                            "full_name": "Test User"
                        }' || exit 1

                    # Test login endpoint
                    curl -X POST http://localhost:8000/auth/login \
                        -H "Content-Type: application/json" \
                        -d '{
                            "username": "admin@example.com",
                            "password": "jenkins"
                        }' || exit 1
                '''
            }
        }
    }

    post {
        always {
            sh '''
                # Collect logs for debugging
                docker-compose -f ${DOCKER_COMPOSE_FILE} logs > jenkins_logs.txt

                # Cleanup environment
                docker-compose -f ${DOCKER_COMPOSE_FILE} down -v
            '''

            archiveArtifacts artifacts: 'jenkins_logs.txt', allowEmptyArchive: true
        }

        success {
            echo 'Preproduction validation successful! ✅'
        }

        failure {
            echo 'Preproduction validation failed! ❌'
        }
    }
}
```

### GitHub Actions Workflow Example

**Complete workflow** (`.github/workflows/preproduction-test.yml`):

```yaml
name: Preproduction Validation

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  preproduction-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Pull Docker images
        run: |
          docker pull jfdelafuente/contravento-backend:latest
          docker pull jfdelafuente/contravento-frontend:latest

      - name: Start preproduction environment
        run: |
          docker-compose -f docker-compose.preproduction.dev.yml up -d
          sleep 30  # Wait for services

      - name: Health checks
        run: |
          curl -f http://localhost:8000/health || exit 1
          curl -I http://localhost:5173 || exit 1

      - name: Run backend tests
        run: |
          docker-compose -f docker-compose.preproduction.dev.yml exec -T backend \
            poetry run pytest tests/ --cov=src --cov-report=xml

      - name: Run frontend tests
        run: |
          docker-compose -f docker-compose.preproduction.dev.yml exec -T frontend \
            npm test -- --run

      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

      - name: Cleanup
        if: always()
        run: |
          docker-compose -f docker-compose.preproduction.dev.yml logs
          docker-compose -f docker-compose.preproduction.dev.yml down -v
```

### GitLab CI Example

**Complete `.gitlab-ci.yml`**:

```yaml
stages:
  - validate

preproduction_validation:
  stage: validate
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_DRIVER: overlay2
    COMPOSE_FILE: docker-compose.preproduction.dev.yml

  before_script:
    - apk add --no-cache docker-compose curl

  script:
    # Pull latest images
    - docker pull jfdelafuente/contravento-backend:latest
    - docker pull jfdelafuente/contravento-frontend:latest

    # Start environment
    - docker-compose -f $COMPOSE_FILE up -d
    - sleep 30

    # Health checks
    - curl -f http://localhost:8000/health

    # Run tests
    - docker-compose -f $COMPOSE_FILE exec -T backend poetry run pytest
    - docker-compose -f $COMPOSE_FILE exec -T frontend npm test -- --run

  after_script:
    # Always cleanup
    - docker-compose -f $COMPOSE_FILE logs
    - docker-compose -f $COMPOSE_FILE down -v

  only:
    - develop
    - main
    - merge_requests
```

---

## Configuration

### Default Configuration

**Auto-configured** (no `.env` file needed):

All services use sensible defaults, so you can deploy without any configuration:

```bash
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

**Default values**:

```bash
# Application
APP_NAME=ContraVento
APP_ENV=production
DEBUG=true

# Security
SECRET_KEY=jenkins_default_secret_key_for_testing_only_do_not_use_in_production
BCRYPT_ROUNDS=4  # Fast hashing for testing

# Database Configuration
POSTGRES_DB=contravento_jenkins
POSTGRES_USER=postgres
POSTGRES_PASSWORD=jenkins_test_password

# Ports
POSTGRES_PORT=5432
BACKEND_PORT=8000
BACKEND_INTERNAL_PORT=8000
FRONTEND_PORT=5173
PGADMIN_PORT=5050

# Container Names
POSTGRES_CONTAINER=contravento-db-jenkins
BACKEND_CONTAINER=contravento-api-jenkins
FRONTEND_CONTAINER=contravento-frontend-jenkins
PGADMIN_CONTAINER=contravento-pgadmin-jenkins

# Volumes
BACKEND_STORAGE_PATH=./backend/storage
POSTGRES_VOLUME=postgres_data_jenkins
PGADMIN_VOLUME=pgadmin_data_jenkins

# Network
NETWORK_NAME=jenkins-network

# pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=jenkins

# Frontend (test key auto-passes Turnstile)
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=text
```

### Custom Configuration (Optional)

**If you need to customize**, use the provided template:

```bash
# Copy template
cp .env.preproduction.example .env.preproduction

# Edit values
nano .env.preproduction

# Deploy with custom config
docker-compose -f docker-compose.preproduction.dev.yml --env-file .env.preproduction up -d
```

### Advanced Configuration - All Available Variables

The preproduction environment is **fully parametrized** for maximum flexibility. Every aspect can be customized via environment variables.

**📖 Complete Reference**: For detailed parameterization guide with examples, CI/CD integration, and troubleshooting, see **[Preproduction Parameterization Guide](./preproduction-parameterization.md)**.

#### 🎯 Docker Images

```bash
# Backend image from Docker Hub
BACKEND_IMAGE=jfdelafuente/contravento-backend:develop

# Frontend image from Docker Hub
FRONTEND_IMAGE=jfdelafuente/contravento-frontend:develop

# Example: Use custom registry or branch
BACKEND_IMAGE=myregistry/backend:feature-branch
FRONTEND_IMAGE=myregistry/frontend:feature-branch
```

#### 🔐 Security

```bash
# JWT secret key (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=jenkins_default_secret_key_for_testing_only_do_not_use_in_production

# Database password
POSTGRES_PASSWORD=jenkins_test_password
```

#### 🗄️ Database Configuration

```bash
# Database name
POSTGRES_DB=contravento_jenkins

# Database user
POSTGRES_USER=postgres

# Database password (also used in DATABASE_URL)
POSTGRES_PASSWORD=jenkins_test_password
```

#### 🔌 Port Mappings

Customize ports to avoid conflicts or run multiple instances:

```bash
# PostgreSQL host port
POSTGRES_PORT=5432

# Backend host port
BACKEND_PORT=8000

# Backend container internal port
BACKEND_INTERNAL_PORT=8000

# Full backend URL (for testing scripts)
BACKEND_URL=http://localhost:8000

# Frontend host port
FRONTEND_PORT=5173

# pgAdmin host port
PGADMIN_PORT=5050
```

**Example - Avoid port conflicts**:
```bash
POSTGRES_PORT=5433 \
BACKEND_PORT=8001 \
FRONTEND_PORT=5174 \
PGADMIN_PORT=5051 \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

#### 📦 Container Names

Useful for running multiple instances simultaneously:

```bash
POSTGRES_CONTAINER=contravento-db-jenkins
BACKEND_CONTAINER=contravento-api-jenkins
FRONTEND_CONTAINER=contravento-frontend-jenkins
PGADMIN_CONTAINER=contravento-pgadmin-jenkins
```

**Example - Multiple instances**:
```bash
# Instance 1 (default names)
docker-compose -f docker-compose.preproduction.dev.yml up -d

# Instance 2 (custom names and ports)
POSTGRES_PORT=5433 \
BACKEND_PORT=8001 \
FRONTEND_PORT=5174 \
POSTGRES_CONTAINER=contravento-db-jenkins-2 \
BACKEND_CONTAINER=contravento-api-jenkins-2 \
FRONTEND_CONTAINER=contravento-frontend-jenkins-2 \
NETWORK_NAME=jenkins-network-2 \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

#### 💾 Volumes

```bash
# Backend storage (local directory for uploads)
BACKEND_STORAGE_PATH=./backend/storage

# PostgreSQL data volume (Docker managed)
POSTGRES_VOLUME=postgres_data_jenkins

# pgAdmin data volume (Docker managed)
PGADMIN_VOLUME=pgadmin_data_jenkins
```

**Example - Custom storage location**:
```bash
BACKEND_STORAGE_PATH=/mnt/external/jenkins-storage \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

#### 🌐 Network

```bash
# Docker network name
NETWORK_NAME=jenkins-network
```

#### 🛠️ pgAdmin Configuration

```bash
# pgAdmin login email
PGADMIN_EMAIL=admin@example.com

# pgAdmin login password
PGADMIN_PASSWORD=jenkins
```

**Note**: pgAdmin's auto-configuration (`configs.pgadmin_servers`) does NOT support variable interpolation due to Docker Compose limitations. If you change `POSTGRES_DB`, `POSTGRES_USER`, or `POSTGRES_PORT`, you must manually update the `configs` section in the docker-compose file (lines 228-245).

### Configuration Templates

**Complete `.env.preproduction` example**:

```bash
# ============================================================================
# ContraVento - Preproduction Environment (Fully Customized)
# ============================================================================

# Docker Images
BACKEND_IMAGE=jfdelafuente/contravento-backend:develop
FRONTEND_IMAGE=jfdelafuente/contravento-frontend:develop

# Security
SECRET_KEY=my_custom_secret_key_for_jenkins_testing
POSTGRES_PASSWORD=my_strong_password_123

# Database
POSTGRES_DB=contravento_jenkins
POSTGRES_USER=postgres

# Ports (custom to avoid conflicts)
POSTGRES_PORT=5433
BACKEND_PORT=8001
BACKEND_INTERNAL_PORT=8000
BACKEND_URL=http://localhost:8001
FRONTEND_PORT=5174
PGADMIN_PORT=5051

# Container Names (for multiple instances)
POSTGRES_CONTAINER=contravento-db-jenkins-custom
BACKEND_CONTAINER=contravento-api-jenkins-custom
FRONTEND_CONTAINER=contravento-frontend-jenkins-custom
PGADMIN_CONTAINER=contravento-pgadmin-jenkins-custom

# Volumes
BACKEND_STORAGE_PATH=/custom/path/storage
POSTGRES_VOLUME=postgres_data_jenkins_custom
PGADMIN_VOLUME=pgadmin_data_jenkins_custom

# Network
NETWORK_NAME=jenkins-network-custom

# pgAdmin
PGADMIN_EMAIL=devops@mycompany.com
PGADMIN_PASSWORD=secure_pgadmin_password
```

**Deploy with full customization**:
```bash
docker-compose -f docker-compose.preproduction.dev.yml --env-file .env.preproduction up -d
```

### Docker Compose Configuration

**Key sections** from `docker-compose.preproduction.dev.yml`:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: contravento-db-preproduction
    environment:
      POSTGRES_DB: contravento_jenkins
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: jenkins_test_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d contravento_jenkins"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: jfdelafuente/contravento-backend:latest  # Pre-built image
    container_name: contravento-backend-preproduction
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:jenkins_test_password@postgres:5432/contravento_jenkins
      SECRET_KEY: jenkins_default_secret_key_for_testing_only_do_not_use_in_production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: jfdelafuente/contravento-frontend:latest  # Pre-built image
    container_name: contravento-frontend-preproduction
    environment:
      VITE_API_URL: http://localhost:8000
      VITE_TURNSTILE_SITE_KEY: 1x00000000000000000000AA
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5173"]
      interval: 10s
      timeout: 5s
      retries: 3
```

---

## Testing Workflows

### Helper Scripts

**Linux/Mac** (`run-jenkins-env.sh`):

```bash
#!/bin/bash
# Helper script for preproduction environment

COMPOSE_FILE="docker-compose.preproduction.dev.yml"

case "$1" in
  start)
    echo "Starting preproduction environment..."
    docker-compose -f $COMPOSE_FILE up -d
    sleep 30
    echo "Environment ready!"
    ;;

  stop)
    echo "Stopping preproduction environment..."
    docker-compose -f $COMPOSE_FILE down
    ;;

  restart)
    echo "Restarting preproduction environment..."
    docker-compose -f $COMPOSE_FILE restart
    ;;

  logs)
    docker-compose -f $COMPOSE_FILE logs -f
    ;;

  status)
    docker-compose -f $COMPOSE_FILE ps
    docker-compose -f $COMPOSE_FILE exec backend curl -f http://localhost:8000/health
    ;;

  test)
    echo "Running tests..."
    docker-compose -f $COMPOSE_FILE exec backend poetry run pytest
    docker-compose -f $COMPOSE_FILE exec frontend npm test -- --run
    ;;

  clean)
    echo "Cleaning up (removing volumes)..."
    docker-compose -f $COMPOSE_FILE down -v
    ;;

  *)
    echo "Usage: $0 {start|stop|restart|logs|status|test|clean}"
    exit 1
    ;;
esac
```

**Windows PowerShell** (`run-jenkins-env.ps1`):

```powershell
# Helper script for preproduction environment
param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'test', 'clean')]
    [string]$Action = 'start'
)

$ComposeFile = "docker-compose.preproduction.dev.yml"

switch ($Action) {
    'start' {
        Write-Host "Starting preproduction environment..."
        docker-compose -f $ComposeFile up -d
        Start-Sleep -Seconds 30
        Write-Host "Environment ready!"
    }

    'stop' {
        Write-Host "Stopping preproduction environment..."
        docker-compose -f $ComposeFile down
    }

    'restart' {
        Write-Host "Restarting preproduction environment..."
        docker-compose -f $ComposeFile restart
    }

    'logs' {
        docker-compose -f $ComposeFile logs -f
    }

    'status' {
        docker-compose -f $ComposeFile ps
        docker-compose -f $ComposeFile exec backend curl -f http://localhost:8000/health
    }

    'test' {
        Write-Host "Running tests..."
        docker-compose -f $ComposeFile exec backend poetry run pytest
        docker-compose -f $ComposeFile exec frontend npm test -- --run
    }

    'clean' {
        Write-Host "Cleaning up (removing volumes)..."
        docker-compose -f $ComposeFile down -v
    }
}
```

### Manual Testing

**Full test sequence**:

```bash
# 1. Start environment
./run-jenkins-env.sh start

# 2. Verify health
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}

# 3. Run backend tests
docker-compose -f docker-compose.preproduction.dev.yml exec backend \
  poetry run pytest --cov=src --cov-report=term

# 4. Run frontend tests
docker-compose -f docker-compose.preproduction.dev.yml exec frontend \
  npm test -- --run

# 5. Test API endpoints
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# 6. Cleanup
./run-jenkins-env.sh clean
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Images Not Found

**Symptoms**: `Error: pull access denied for jfdelafuente/contravento-backend`

**Fix**: Verify images exist on Docker Hub
```bash
# Check if images are available
docker search jfdelafuente/contravento

# If not found, build and push images first:
cd backend
docker build -t jfdelafuente/contravento-backend:latest .
docker push jfdelafuente/contravento-backend:latest
```

#### Issue 2: Port Conflicts

**Symptoms**: `Error: bind: address already in use`

**Fix**: Stop conflicting services
```bash
# Find process using port 8000
lsof -i :8000              # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process or change port in docker-compose.preproduction.dev.yml
```

#### Issue 3: Database Not Ready

**Symptoms**: Backend fails with "connection refused"

**Fix**: Wait for PostgreSQL health check
```bash
# Check postgres health
docker-compose -f docker-compose.preproduction.dev.yml ps

# If unhealthy, check logs
docker-compose -f docker-compose.preproduction.dev.yml logs postgres

# Restart if needed
docker-compose -f docker-compose.preproduction.dev.yml restart postgres
```

#### Issue 4: Tests Fail in CI

**Symptoms**: Tests pass locally but fail in Jenkins/GitHub Actions

**Common Causes**:
1. **Insufficient wait time**: Increase sleep after `docker-compose up -d` (30s → 60s)
2. **Resource constraints**: CI runners may be slower (increase timeouts)
3. **Network isolation**: Ensure services can reach each other

**Fix**:
```bash
# Add explicit health check wait
docker-compose -f docker-compose.preproduction.dev.yml up -d
until curl -f http://localhost:8000/health; do
  echo "Waiting for backend..."
  sleep 5
done
```

---

## Related Modes

### Progression Path

```
Preproduction → Staging → Production
```

**Typical Workflow**:
1. **CI/CD builds** → Push images to Docker Hub
2. **Preproduction** → Automated testing (YOU ARE HERE)
3. **Staging** → Manual QA testing
4. **Production** → Live deployment

### Comparison with Test Mode

**Preproduction vs Test**:

| Aspect | Preproduction | Test |
|--------|:-------------:|:----:|
| **Database** | PostgreSQL | PostgreSQL/SQLite |
| **Frontend** | ✅ Included | ❌ Not included |
| **Image Source** | Docker Hub | Docker Hub |
| **Primary Use** | CI/CD validation | Unit/integration tests |
| **Persistence** | Ephemeral | Ephemeral |

**When to Use Each**:
- **Test Mode**: Unit and integration tests (fast, lightweight)
- **Preproduction Mode**: Full-stack validation with frontend (slower, complete)

### Related Documentation

- **[Test Mode](./test.md)** - Automated testing environment (unit/integration tests)
- **[Staging Mode](./staging.md)** - Next step after preproduction validation
- **[Production Mode](./prod.md)** - Final deployment target
- **[Getting Started Guide](../guides/getting-started.md)** - Universal onboarding

---

## Resource Requirements

**Minimum**:
- **CPU**: 2 cores
- **RAM**: 2 GB
- **Disk**: 5 GB
- **Startup Time**: ~20 seconds

**Estimated Costs** (CI/CD runner):
- GitHub Actions: Free for public repos
- Jenkins (self-hosted): Server costs only
- GitLab CI: 400 minutes/month free

---

## Summary

**Preproduction Mode** is designed for:
- ✅ **Fast** automated validation (~20s startup)
- ✅ **Zero configuration** (auto-generated secrets)
- ✅ **Pre-built images** (no local builds)
- ✅ **CI/CD friendly** (Jenkins, GitHub Actions, GitLab CI)
- ✅ **Ephemeral** (clean state every run)

**Use when**: You need to validate Docker images and run automated tests before promoting to staging.

---

**Last Updated**: 2026-02-06
**Document Version**: 1.0
**Feedback**: Report issues or suggest improvements via GitHub Issues
