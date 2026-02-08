# Preproduction Environment - Full Parameterization Guide

**Document Version**: 1.0
**Last Updated**: 2026-02-08
**Target File**: `docker-compose.preproduction.dev.yml`

---

## Overview

The preproduction deployment environment has been **fully parametrized** to provide maximum flexibility for CI/CD pipelines and multi-instance deployments. All hardcoded values have been replaced with environment variables that have sensible defaults.

### What Changed?

**Before**: Fixed values for ports, container names, volumes, etc.
**After**: All values configurable via environment variables with defaults

### Benefits

- ✅ **Zero Configuration**: Works out-of-the-box with defaults
- ✅ **Port Flexibility**: Avoid conflicts by customizing ports
- ✅ **Multiple Instances**: Run parallel environments simultaneously
- ✅ **CI/CD Friendly**: Easy integration with Jenkins, GitHub Actions, GitLab CI
- ✅ **Custom Storage**: Control where data is persisted
- ✅ **Registry Agnostic**: Use Docker Hub, private registries, or local images

---

## Complete Variable Reference

### 🎯 Docker Images

| Variable | Description | Default |
|----------|-------------|---------|
| `BACKEND_IMAGE` | Backend Docker image | `jfdelafuente/contravento-backend:develop` |
| `FRONTEND_IMAGE` | Frontend Docker image | `jfdelafuente/contravento-frontend:develop` |

**Use Case**: Custom registry or feature branches
```bash
BACKEND_IMAGE=myregistry/backend:feature-xyz
FRONTEND_IMAGE=myregistry/frontend:feature-xyz
```

---

### 🔐 Security

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | `jenkins_default_secret_key_for_testing_only_do_not_use_in_production` |
| `POSTGRES_PASSWORD` | Database password | `jenkins_test_password` |

**Use Case**: Secure credentials
```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
POSTGRES_PASSWORD=my_secure_password_123
```

---

### 🗄️ Database Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `contravento_jenkins` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `jenkins_test_password` |

**Use Case**: Isolated database per branch
```bash
POSTGRES_DB=contravento_feature_xyz
POSTGRES_USER=feature_user
```

---

### 🔌 Port Mappings

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_PORT` | PostgreSQL host port | `5432` |
| `BACKEND_PORT` | Backend host port | `8000` |
| `BACKEND_INTERNAL_PORT` | Backend container port | `8000` |
| `BACKEND_URL` | Full backend URL | `http://localhost:8000` |
| `FRONTEND_PORT` | Frontend host port | `5173` |
| `PGADMIN_PORT` | pgAdmin host port | `5050` |

**Use Case**: Avoid port conflicts
```bash
POSTGRES_PORT=5433
BACKEND_PORT=8001
FRONTEND_PORT=5174
PGADMIN_PORT=5051
```

**Use Case**: Multiple parallel instances
```bash
# Instance 1 (defaults)
docker-compose -f docker-compose.preproduction.dev.yml up -d

# Instance 2 (custom ports)
POSTGRES_PORT=5433 \
BACKEND_PORT=8001 \
FRONTEND_PORT=5174 \
PGADMIN_PORT=5051 \
docker-compose -f docker-compose.preproduction.dev.yml -p instance2 up -d
```

---

### 📦 Container Names

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_CONTAINER` | PostgreSQL container | `contravento-db-jenkins` |
| `BACKEND_CONTAINER` | Backend container | `contravento-api-jenkins` |
| `FRONTEND_CONTAINER` | Frontend container | `contravento-frontend-jenkins` |
| `PGADMIN_CONTAINER` | pgAdmin container | `contravento-pgadmin-jenkins` |

**Use Case**: Unique names for parallel instances
```bash
POSTGRES_CONTAINER=contravento-db-feature-xyz
BACKEND_CONTAINER=contravento-api-feature-xyz
FRONTEND_CONTAINER=contravento-frontend-feature-xyz
```

---

### 💾 Volumes

| Variable | Description | Default |
|----------|-------------|---------|
| `BACKEND_STORAGE_PATH` | Local storage directory | `./backend/storage` |
| `POSTGRES_VOLUME` | PostgreSQL volume name | `postgres_data_jenkins` |
| `PGADMIN_VOLUME` | pgAdmin volume name | `pgadmin_data_jenkins` |

**Use Case**: Custom storage location
```bash
BACKEND_STORAGE_PATH=/mnt/shared/jenkins-storage
```

**Use Case**: Separate volumes per instance
```bash
POSTGRES_VOLUME=postgres_data_feature_xyz
PGADMIN_VOLUME=pgadmin_data_feature_xyz
```

---

### 🌐 Network

| Variable | Description | Default |
|----------|-------------|---------|
| `NETWORK_NAME` | Docker network name | `jenkins-network` |

**Use Case**: Isolated networks per instance
```bash
NETWORK_NAME=jenkins-network-feature-xyz
```

---

### 🛠️ pgAdmin

| Variable | Description | Default |
|----------|-------------|---------|
| `PGADMIN_EMAIL` | Login email | `admin@example.com` |
| `PGADMIN_PASSWORD` | Login password | `jenkins` |

**Use Case**: Custom credentials
```bash
PGADMIN_EMAIL=devops@mycompany.com
PGADMIN_PASSWORD=secure_password_123
```

---

## Usage Examples

### Example 1: Default Deployment (Zero Configuration)

```bash
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

All services use default values. No `.env` file needed.

---

### Example 2: Custom Ports (Avoid Conflicts)

```bash
POSTGRES_PORT=5433 \
BACKEND_PORT=8001 \
FRONTEND_PORT=5174 \
PGADMIN_PORT=5051 \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

Access:
- Frontend: http://localhost:5174
- Backend API: http://localhost:8001
- pgAdmin: http://localhost:5051

---

### Example 3: Multiple Parallel Instances

**Instance 1 (develop branch)**:
```bash
POSTGRES_PORT=5432 \
BACKEND_PORT=8000 \
FRONTEND_PORT=5173 \
POSTGRES_CONTAINER=contravento-db-develop \
BACKEND_CONTAINER=contravento-api-develop \
FRONTEND_CONTAINER=contravento-frontend-develop \
NETWORK_NAME=jenkins-network-develop \
POSTGRES_VOLUME=postgres_data_develop \
PGADMIN_VOLUME=pgadmin_data_develop \
docker-compose -f docker-compose.preproduction.dev.yml -p develop up -d
```

**Instance 2 (feature-xyz branch)**:
```bash
POSTGRES_PORT=5433 \
BACKEND_PORT=8001 \
FRONTEND_PORT=5174 \
POSTGRES_CONTAINER=contravento-db-feature-xyz \
BACKEND_CONTAINER=contravento-api-feature-xyz \
FRONTEND_CONTAINER=contravento-frontend-feature-xyz \
NETWORK_NAME=jenkins-network-feature-xyz \
POSTGRES_VOLUME=postgres_data_feature_xyz \
PGADMIN_VOLUME=pgadmin_data_feature_xyz \
docker-compose -f docker-compose.preproduction.dev.yml -p feature-xyz up -d
```

Both instances run simultaneously without conflicts.

---

### Example 4: Custom Registry (Private Images)

```bash
BACKEND_IMAGE=mycompany.registry.io/contravento-backend:v1.2.3 \
FRONTEND_IMAGE=mycompany.registry.io/contravento-frontend:v1.2.3 \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

---

### Example 5: Using .env File (Team Workflow)

**Create `.env.preproduction`**:
```bash
# Copy template
cp .env.preproduction.example .env.preproduction

# Edit values
nano .env.preproduction
```

**Content of `.env.preproduction`**:
```env
# Custom configuration for QA team
BACKEND_IMAGE=jfdelafuente/contravento-backend:develop
FRONTEND_IMAGE=jfdelafuente/contravento-frontend:develop

SECRET_KEY=qa_team_secret_key_abc123xyz
POSTGRES_PASSWORD=qa_secure_password_456

POSTGRES_PORT=5432
BACKEND_PORT=8000
FRONTEND_PORT=5173

PGADMIN_EMAIL=qa@mycompany.com
PGADMIN_PASSWORD=qa_pgadmin_password
```

**Deploy**:
```bash
docker-compose -f docker-compose.preproduction.dev.yml --env-file .env.preproduction up -d
```

---

## CI/CD Integration

### Jenkins Pipeline (Parameterized)

```groovy
pipeline {
    agent any

    parameters {
        string(name: 'BACKEND_IMAGE', defaultValue: 'jfdelafuente/contravento-backend:develop', description: 'Backend image')
        string(name: 'FRONTEND_IMAGE', defaultValue: 'jfdelafuente/contravento-frontend:develop', description: 'Frontend image')
        string(name: 'POSTGRES_PORT', defaultValue: '5432', description: 'PostgreSQL port')
        string(name: 'BACKEND_PORT', defaultValue: '8000', description: 'Backend port')
        string(name: 'FRONTEND_PORT', defaultValue: '5173', description: 'Frontend port')
    }

    environment {
        COMPOSE_FILE = 'docker-compose.preproduction.dev.yml'

        // Pass parameters as environment variables
        BACKEND_IMAGE = "${params.BACKEND_IMAGE}"
        FRONTEND_IMAGE = "${params.FRONTEND_IMAGE}"
        POSTGRES_PORT = "${params.POSTGRES_PORT}"
        BACKEND_PORT = "${params.BACKEND_PORT}"
        FRONTEND_PORT = "${params.FRONTEND_PORT}"
    }

    stages {
        stage('Deploy') {
            steps {
                sh '''
                    docker-compose -f ${COMPOSE_FILE} up -d
                    sleep 30
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    curl -f http://localhost:${BACKEND_PORT}/health || exit 1
                    curl -I http://localhost:${FRONTEND_PORT} || exit 1
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh '''
                    docker-compose -f ${COMPOSE_FILE} down -v
                '''
            }
        }
    }
}
```

---

### GitHub Actions (Matrix Strategy)

```yaml
name: Preproduction Matrix Test

on:
  push:
    branches: [develop, main]

jobs:
  test-matrix:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        branch: [develop, main]
        port_offset: [0, 10, 20]

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Calculate ports
        id: ports
        run: |
          OFFSET=${{ matrix.port_offset }}
          echo "postgres_port=$((5432 + OFFSET))" >> $GITHUB_OUTPUT
          echo "backend_port=$((8000 + OFFSET))" >> $GITHUB_OUTPUT
          echo "frontend_port=$((5173 + OFFSET))" >> $GITHUB_OUTPUT

      - name: Pull images
        run: |
          docker pull jfdelafuente/contravento-backend:${{ matrix.branch }}
          docker pull jfdelafuente/contravento-frontend:${{ matrix.branch }}

      - name: Deploy
        env:
          BACKEND_IMAGE: jfdelafuente/contravento-backend:${{ matrix.branch }}
          FRONTEND_IMAGE: jfdelafuente/contravento-frontend:${{ matrix.branch }}
          POSTGRES_PORT: ${{ steps.ports.outputs.postgres_port }}
          BACKEND_PORT: ${{ steps.ports.outputs.backend_port }}
          FRONTEND_PORT: ${{ steps.ports.outputs.frontend_port }}
        run: |
          docker-compose -f docker-compose.preproduction.dev.yml up -d
          sleep 30

      - name: Test
        run: |
          curl -f http://localhost:${{ steps.ports.outputs.backend_port }}/health
          curl -I http://localhost:${{ steps.ports.outputs.frontend_port }}

      - name: Cleanup
        if: always()
        run: |
          docker-compose -f docker-compose.preproduction.dev.yml down -v
```

---

## Important Notes

### Frontend Configuration with Custom Backend Ports

**⚠️ Critical**: When changing `BACKEND_PORT`, the frontend needs to know the new backend location.

**Problem**: Frontend images have `VITE_API_URL` hardcoded at build-time.

**Example Issue**:
```bash
# Backend on custom port
BACKEND_PORT=9000 docker-compose -f docker-compose.preproduction.dev.yml up -d

# Frontend still tries to connect to port 8000 (hardcoded in image)
# ❌ API calls fail: "Connection refused to http://localhost:8000"
```

**Solutions**:

#### Solution 1: Rebuild Frontend Image (Recommended for CI/CD)
```bash
# Build frontend with custom backend URL
cd frontend
VITE_API_URL=http://localhost:9000 npm run build

# Create new Docker image
docker build -t myregistry/contravento-frontend:custom-port .

# Deploy with custom images
BACKEND_PORT=9000 \
FRONTEND_IMAGE=myregistry/contravento-frontend:custom-port \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

#### Solution 2: Use Nginx Proxy (Best for Production)
Configure Nginx in frontend to proxy all API calls to backend service name:

```nginx
# frontend/nginx.conf
location /api/ {
    proxy_pass http://backend:8000;  # Uses Docker service name
}
```

**Benefits**:
- ✅ Frontend doesn't need to know backend port
- ✅ Works with any `BACKEND_PORT` value
- ✅ No rebuild required

#### Solution 3: Local Development
For local dev (npm run dev), update `.env.development`:

```bash
# frontend/.env.development
VITE_API_URL=http://localhost:9000

# Restart dev server
npm run dev
```

**When to Rebuild**:
- ✅ Changing `BACKEND_PORT` in CI/CD pipelines
- ✅ Creating separate environments (staging, prod)
- ✅ Running multiple parallel instances
- ❌ Quick local testing (use `.env.development` instead)

---

### pgAdmin Configuration Limitation

**⚠️ Warning**: The pgAdmin auto-configuration (`configs.pgadmin_servers`) **does NOT support variable interpolation** due to Docker Compose limitations.

If you change `POSTGRES_DB`, `POSTGRES_USER`, or `POSTGRES_PORT`, you must manually update the `configs` section in `docker-compose.preproduction.dev.yml` (lines 228-245).

**Workaround**: Configure pgAdmin manually via the web UI after deployment.

---

### Volume Naming

When using custom `POSTGRES_VOLUME` or `PGADMIN_VOLUME` names:

1. The volume **definition** in the `volumes:` section must match the volume **reference** in the service
2. Docker will create a volume with the exact name you specify
3. Use unique names to avoid conflicts between instances

**Example**:
```yaml
volumes:
  postgres_data_jenkins:
    driver: local
    name: ${POSTGRES_VOLUME:-postgres_data_jenkins}  # ✅ Correct
```

---

### Network Isolation

When running multiple instances, always use unique network names:

```bash
NETWORK_NAME=jenkins-network-instance-1
NETWORK_NAME=jenkins-network-instance-2
```

This ensures complete isolation between instances.

---

## Troubleshooting

### Issue: Port Already in Use

**Error**: `bind: address already in use`

**Solution**: Change port via environment variable
```bash
BACKEND_PORT=8001 docker-compose -f docker-compose.preproduction.dev.yml up -d
```

---

### Issue: Volume Name Conflict

**Error**: `Error response from daemon: volume name conflict`

**Solution**: Use unique volume names
```bash
POSTGRES_VOLUME=postgres_data_unique_name \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

---

### Issue: Container Name Conflict

**Error**: `Conflict. The container name "/contravento-db-jenkins" is already in use`

**Solution**: Use unique container names or stop existing containers
```bash
# Option 1: Stop existing
docker stop contravento-db-jenkins

# Option 2: Use unique names
POSTGRES_CONTAINER=contravento-db-jenkins-2 \
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

---

## Migration Guide

### From Non-Parameterized to Parameterized

**Before** (hardcoded values):
```bash
# Had to edit docker-compose file directly
nano docker-compose.preproduction.dev.yml
# Change ports manually
docker-compose -f docker-compose.preproduction.dev.yml up -d
```

**After** (parameterized):
```bash
# Just override with environment variables
BACKEND_PORT=8001 docker-compose -f docker-compose.preproduction.dev.yml up -d
```

**No Breaking Changes**: All defaults remain the same. Existing deployments work without modification.

---

## Related Documentation

- **[Preproduction Mode](modes/preproduction.md)** - Complete deployment guide
- **[Environment Variables Reference](guides/environment-variables.md)** - All variable categories
- **[Docker Compose Guide](guides/docker-compose-guide.md)** - Docker Compose usage

---

## Summary

The preproduction environment is now **fully configurable** via environment variables while maintaining **zero-configuration** defaults. This enables:

- ✅ Conflict-free deployments (custom ports)
- ✅ Parallel instance execution (multiple branches)
- ✅ CI/CD flexibility (Jenkins, GitHub Actions, GitLab CI)
- ✅ Custom registries (private images)
- ✅ Team customization (.env files)

**Key Takeaway**: You can now customize everything or nothing - both work seamlessly.

---

**Document Version**: 1.0
**Last Updated**: 2026-02-08
**Feedback**: Report issues or suggest improvements via GitHub Issues
