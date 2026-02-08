# Jenkins Pipeline Guide - ContraVento

Guía completa para configurar y ejecutar el pipeline de Jenkins para ContraVento.

---

## 📋 Tabla de Contenidos

1. [Prerequisitos](#prerequisitos)
2. [Configuración Inicial](#configuración-inicial)
3. [Credenciales Requeridas](#credenciales-requeridas)
4. [Pipeline Stages](#pipeline-stages)
5. [Ejecutar el Pipeline](#ejecutar-el-pipeline)
6. [Troubleshooting](#troubleshooting)
7. [Mantenimiento](#mantenimiento)

---

## Prerequisitos

### Software Requerido en Jenkins Server

- **Jenkins**: Versión 2.400+ con Blue Ocean plugin (recomendado)
- **Docker**: Versión 24.0+ (con Docker Compose v2 integrado)
- **Git**: 2.40+
- **curl**: Para health checks

**Nota**: Python y Poetry **NO** son necesarios en el servidor Jenkins. Los tests se ejecutan dentro de contenedores Docker.

### Jenkins Plugins

Instalar los siguientes plugins en Jenkins:

```
- Pipeline
- Git
- Docker Pipeline
- Credentials Binding
- Blue Ocean (opcional, para mejor UI)
```

Instalar vía Jenkins UI:
```
Manage Jenkins → Plugins → Available Plugins
```

---

## Configuración Inicial

### 1. Crear Job en Jenkins

1. Ir a Jenkins Dashboard
2. Click en **"New Item"**
3. Nombre: `ContraVento-Pipeline`
4. Tipo: **Pipeline**
5. Click **OK**

### 2. Configurar Pipeline

En la configuración del job:

**General:**
- ✅ Discard old builds: Keep last 10 builds

**Build Triggers:**
- ✅ Poll SCM: `H/5 * * * *` (check every 5 minutes)
- O configurar webhook desde GitHub

**Pipeline:**
- Definition: **Pipeline script from SCM**
- SCM: **Git**
- Repository URL: `https://github.com/jfdelafuente/contravento-application-python.git`
- Branch: `develop`
- Script Path: `Jenkinsfile`

---

## Credenciales Requeridas

**📖 Guía Completa de Credenciales**: Para configuración detallada paso a paso con capturas de pantalla, scripts de verificación y troubleshooting avanzado, consulta:

👉 **[JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md)**

### Resumen Rápido

Necesitas configurar 3 credenciales en Jenkins:

| ID Credential | Tipo | Valor Ejemplo | Descripción |
|---------------|------|---------------|-------------|
| `dockerhub_id` | Username with password | username: jfdelafuente<br>password: [token] | Autenticación Docker Hub |
| `vite_api_url` | Secret text | `http://localhost:8000` | URL del backend para frontend |
| `vite_turnstile_site_key` | Secret text | `1x00000000000000000000AA` | Cloudflare Turnstile CAPTCHA |

### Configuración Rápida

**Paso 1: Acceder a Credentials**
```
Manage Jenkins → Credentials → System → Global credentials → Add Credentials
```

**Paso 2: Crear las 3 credenciales**

1. **dockerhub_id**:
   - Kind: `Username with password`
   - Username: `jfdelafuente`
   - Password: [Docker Hub Access Token]
   - ID: `dockerhub_id`

2. **vite_api_url**:
   - Kind: `Secret text`
   - Secret: `http://localhost:8000` (para preproducción local)
   - ID: `vite_api_url`

3. **vite_turnstile_site_key**:
   - Kind: `Secret text`
   - Secret: `1x00000000000000000000AA` (testing key)
   - ID: `vite_turnstile_site_key`

**⚠️ IMPORTANTE**: Los IDs deben ser **exactos** (case-sensitive).

Para obtener tokens reales y configuración avanzada, ver [JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md)

---

## Versiones del Pipeline

Este proyecto incluye **2 versiones** del Jenkinsfile:

### 📦 Versión Simplificada (Default) - `Jenkinsfile`

**3 Stages**: Git Checkout → Build (parallel) → Push

**Duración**: ~5-10 minutos

**Cuándo usar**: Solo necesitas build y push a Docker Hub

### 🚀 Versión Completa - `Jenkinsfile.full`

**6 Stages**: Git Checkout → Tests → Build (parallel) → Push → Deploy → Validate

**Duración**: ~15-20 minutos

**Cuándo usar**: Necesitas pipeline completo con tests y deployment automático

**📖 Ver comparación completa**: [JENKINSFILE_VERSIONS.md](JENKINSFILE_VERSIONS.md)

---

## Pipeline Stages (Versión Simplificada)

El pipeline simplificado ejecuta 3 stages principales:

### 1. Git Checkout
```
✅ Clona el repositorio desde GitHub
✅ Branch: develop
✅ Muestra el último commit
```

**Duración**: ~10-20 segundos

### 2. Build Docker Images (Parallel)

**Backend y Frontend se construyen en paralelo**:

```
Backend:
✅ Construye imagen desde backend/Dockerfile
✅ Tag: jfdelafuente/contravento-backend:latest

Frontend:
✅ Construye imagen desde frontend/Dockerfile.prod
✅ Variables VITE_* embebidas en tiempo de compilación
✅ Tag: jfdelafuente/contravento-frontend:latest
```

**Duración**: ~3-5 minutos (paralelo)

### 3. Push to Docker Hub
```
✅ Login a Docker Hub con credenciales
✅ Push jfdelafuente/contravento-backend:latest
✅ Push jfdelafuente/contravento-frontend:latest
```

**Duración**: ~1-3 minutos

---

## Pipeline Stages (Versión Completa)

La versión completa (`Jenkinsfile.full`) incluye 3 stages adicionales:

### 2. Run Backend Tests (adicional)
```
✅ Instala Poetry y dependencias
✅ Ejecuta pytest con coverage
✅ Requiere ≥90% coverage
```

### 5. Deploy to Preproduction (adicional)
```
✅ Detiene contenedores existentes
✅ Despliega con docker-compose.preproduction.yml
✅ Espera a que servicios estén healthy
```

### 6. Validate Deployment (adicional)
```
✅ Health checks automáticos
✅ Verifica frontend y backend
✅ Muestra logs
```

**Ver detalles completos**: [JENKINSFILE_VERSIONS.md](JENKINSFILE_VERSIONS.md)

---

## Ejecutar el Pipeline

### Seleccionar Versión del Pipeline

**Por defecto**: Usa `Jenkinsfile` (versión simplificada)

**Para usar versión completa**:
1. Opción A: Renombrar `Jenkinsfile.full` a `Jenkinsfile`
2. Opción B: Crear job separado en Jenkins apuntando a `Jenkinsfile.full`

Ver: [JENKINSFILE_VERSIONS.md - Cómo Cambiar de Versión](JENKINSFILE_VERSIONS.md#-cómo-cambiar-de-versión)

### Ejecución Manual

1. Ir a Jenkins Dashboard
2. Click en job **ContraVento-Pipeline**
3. Click **Build Now**
4. Monitorear progreso en **Blue Ocean** o **Console Output**

### Ejecución Automática

El pipeline se ejecuta automáticamente cuando:

**Via Poll SCM** (cada 5 minutos):
- Detecta nuevos commits en branch `develop`
- Se ejecuta automáticamente

**Via GitHub Webhook** (recomendado):

1. Configurar webhook en GitHub:
   ```
   Repository → Settings → Webhooks → Add webhook
   Payload URL: http://[jenkins-server]/github-webhook/
   Content type: application/json
   Events: Just the push event
   ```

2. En Jenkins job config:
   ```
   Build Triggers → GitHub hook trigger for GITScm polling
   ```

---

## Troubleshooting

### Error: "Docker login failed"

**Problema:** Credenciales de Docker Hub incorrectas

**Solución:**
```bash
# Verificar credenciales en Jenkins
Manage Jenkins → Credentials → dockerhub_id

# Verificar manualmente
docker login -u jfdelafuente
```

---

### Error: "Backend tests failed"

**Problema:** Tests de backend no pasan (coverage <90%)

**Solución:**
```bash
# Ejecutar tests localmente para depurar
cd backend
poetry install
poetry run pytest --cov=src --cov-report=term -v

# Ver reporte detallado
poetry run pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html
```

---

### Error: "Frontend build failed"

**Problema:** Variables VITE_* incorrectas o falta de dependencias

**Solución:**
```bash
# Verificar credenciales
Manage Jenkins → Credentials
- vite_api_url
- vite_turnstile_site_key

# Construir localmente para depurar
cd frontend
npm install
npm run build:prod
```

---

### Error: "Service not healthy"

**Problema:** Backend no responde en /health endpoint

**Solución:**
```bash
# Ver logs del contenedor
docker-compose -f docker-compose.preproduction.yml logs backend

# Verificar que la base de datos está corriendo
docker-compose -f docker-compose.preproduction.yml ps

# Reiniciar servicios
docker-compose -f docker-compose.preproduction.yml down -v
docker-compose -f docker-compose.preproduction.yml up -d
```

---

### Error: "Port already in use"

**Problema:** Puertos 5173, 8000, 5432, 5050 ocupados

**Solución:**
```bash
# Ver qué está usando los puertos
netstat -tulpn | grep -E '5173|8000|5432|5050'

# Detener contenedores existentes
docker-compose -f docker-compose.preproduction.yml down

# O matar procesos específicos
kill -9 $(lsof -ti:8000)
```

---

### Error: "Poetry not found"

**Problema:** Poetry no instalado en Jenkins server

**Solución:**
```bash
# SSH al Jenkins server
ssh jenkins-server

# Instalar Poetry globalmente
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/root/.local/bin:$PATH"

# Verificar instalación
poetry --version
```

---

## Mantenimiento

### Limpiar Recursos Docker

Ejecutar periódicamente en Jenkins server:

```bash
# Eliminar contenedores detenidos
docker container prune -f

# Eliminar imágenes sin usar
docker image prune -a -f

# Eliminar volúmenes huérfanos
docker volume prune -f

# Limpiar todo (⚠️ CUIDADO)
docker system prune -a -f --volumes
```

### Monitorear Espacio en Disco

```bash
# Ver uso de disco
df -h

# Ver espacio usado por Docker
docker system df

# Ver logs de contenedores (limitado a 10MB)
docker-compose -f docker-compose.preproduction.yml logs --tail=1000
```

### Actualizar Dependencias

**Backend:**
```bash
cd backend
poetry update
poetry lock
git commit -am "chore: update backend dependencies"
```

**Frontend:**
```bash
cd frontend
npm update
npm audit fix
git commit -am "chore: update frontend dependencies"
```

---

## Acceso a Entorno de Preproducción

Después de un build exitoso:

- **Frontend:** http://[jenkins-server]:5173
- **Backend API:** http://[jenkins-server]:8000
- **API Docs:** http://[jenkins-server]:8000/docs
- **pgAdmin:** http://[jenkins-server]:5050
  - Email: `admin@example.com`
  - Password: `jenkins`

---

## Workflow Completo

```
1. Desarrollador → Push a branch develop
       ↓
2. GitHub → Webhook trigger a Jenkins
       ↓
3. Jenkins → Git Checkout
       ↓
4. Jenkins → Run Backend Tests (pytest)
       ↓
5. Jenkins → Build Docker Images (backend + frontend)
       ↓
6. Jenkins → Push Images a Docker Hub
       ↓
7. Jenkins → Deploy to Preproduction (docker-compose.preproduction.yml)
       ↓
8. Jenkins → Validate Deployment (health checks)
       ↓
9. Jenkins → Success! Entorno accesible
```

---

## Configuración Avanzada

### Multi-Branch Pipeline

Para soportar múltiples branches (develop, staging, main):

```groovy
// Jenkinsfile con parámetros de branch
def getBranchName() {
    return env.BRANCH_NAME ?: 'develop'
}

environment {
    BRANCH = getBranchName()
    FRONTEND_IMAGE = "jfdelafuente/contravento-frontend:${BRANCH}"
    BACKEND_IMAGE = "jfdelafuente/contravento-backend:${BRANCH}"
}
```

### Slack Notifications

Agregar notificaciones a Slack:

```groovy
post {
    success {
        slackSend(
            color: 'good',
            message: "✅ Pipeline successful: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
    failure {
        slackSend(
            color: 'danger',
            message: "❌ Pipeline failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
        )
    }
}
```

---

## Referencias

- [Jenkinsfile](Jenkinsfile) - Pipeline definition
- [docker-compose.preproduction.yml](docker-compose.preproduction.yml) - Preproduction config
- [DOCKER_COMPOSE_ENVIRONMENTS.md](DOCKER_COMPOSE_ENVIRONMENTS.md) - Docker Compose guide
- [CLAUDE.md](CLAUDE.md) - Project architecture

---

**Última actualización:** 2026-01-23
