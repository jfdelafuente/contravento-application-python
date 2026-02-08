# Guía de Migración: Jenkins → GitHub Actions

Esta guía documenta el proceso de migración del pipeline CI/CD de Jenkins a GitHub Actions para ContraVento.

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Comparativa de Sintaxis](#comparativa-de-sintaxis)
3. [Mapeo de Conceptos](#mapeo-de-conceptos)
4. [Migración Paso a Paso](#migración-paso-a-paso)
5. [Estrategias de Coexistencia](#estrategias-de-coexistencia)
6. [Ventajas y Desventajas](#ventajas-y-desventajas)

---

## Resumen Ejecutivo

### Estado Actual

✅ **Jenkins Pipeline** (Jenkinsfile): Operacional, documentado en [JENKINS_SETUP.md](JENKINS_SETUP.md)
✅ **GitHub Actions Workflow**: Implementado en `.github/workflows/docker-build-push.yml`

**Ambos pipelines están listos para uso en paralelo.**

### ¿Por Qué Migrar?

**Ventajas de GitHub Actions**:
- 🚀 **Zero Infrastructure**: No requiere servidor Jenkins
- 💰 **Costo**: 2000 minutos/mes gratis (repositorios privados), ilimitado (públicos)
- 🔗 **Integración**: Triggers automáticos en push/PR sin webhooks manuales
- 🔐 **Secrets**: UI integrada (no plugin adicional)
- 📊 **Visibilidad**: Logs y status en GitHub UI

**Casos para Mantener Jenkins**:
- ✅ Ya tienes infraestructura Jenkins robusta
- ✅ Workflows muy complejos con plugins específicos
- ✅ Self-hosted requirements (datos sensibles)
- ✅ Necesitas control total del entorno de build

---

## Comparativa de Sintaxis

### 1. Estructura Básica

**Jenkins (Jenkinsfile)**:
```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'docker build -t myapp .'
            }
        }
    }
}
```

**GitHub Actions (YAML)**:
```yaml
name: Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Build Docker Image
        run: docker build -t myapp .
```

### 2. Credentials / Secrets

**Jenkins**:
```groovy
environment {
    DOCKER_CREDS = credentials('dockerhub_id')
}

steps {
    sh 'echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin'
}
```

**GitHub Actions**:
```yaml
steps:
  - name: Login to Docker Hub
    uses: docker/login-action@v3
    with:
      username: ${{ secrets.DOCKERHUB_USERNAME }}
      password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**Clave**: GitHub usa `secrets.NOMBRE`, Jenkins usa `credentials('id')`.

### 3. Build Arguments

**Jenkins**:
```groovy
sh '''
    docker build -t myapp \
      --build-arg API_URL=$VITE_API_URL \
      -f Dockerfile .
'''
```

**GitHub Actions**:
```yaml
- name: Build Docker Image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: Dockerfile
    build-args: |
      API_URL=${{ secrets.VITE_API_URL }}
```

### 4. Conditional Execution

**Jenkins**:
```groovy
stage('Push to Production') {
    when {
        branch 'main'
    }
    steps {
        sh 'docker push myapp:latest'
    }
}
```

**GitHub Actions**:
```yaml
- name: Push to Production
  if: github.ref == 'refs/heads/main'
  run: docker push myapp:latest
```

### 5. Parallel Execution

**Jenkins**:
```groovy
stage('Tests') {
    parallel {
        stage('Unit Tests') {
            steps {
                sh 'npm test'
            }
        }
        stage('Lint') {
            steps {
                sh 'npm run lint'
            }
        }
    }
}
```

**GitHub Actions**:
```yaml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: npm test

  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint
```

**Clave**: GitHub Actions paraleliza jobs por defecto, Jenkins requiere `parallel {}`.

---

## Mapeo de Conceptos

| Concepto Jenkins | Concepto GitHub Actions | Notas |
|------------------|-------------------------|-------|
| **Jenkinsfile** | **Workflow YAML** (.github/workflows/*.yml) | Sintaxis diferente |
| **Pipeline** | **Workflow** | Contenedor de todo el CI/CD |
| **Stage** | **Job** | Unidad lógica de trabajo |
| **Step** | **Step** | Comando individual |
| **Agent** | **Runner** | Máquina que ejecuta el pipeline |
| **Credentials** | **Secrets** | Almacenamiento de secretos |
| **Blue Ocean** | **Actions Tab** | UI para ver ejecuciones |
| **Plugin** | **Action (Marketplace)** | Extensiones reutilizables |
| **Trigger (webhook)** | **on: [push, pull_request]** | Eventos que inician pipeline |
| **post { always {} }** | **if: always()** | Cleanup/finalización |

---

## Migración Paso a Paso

### Fase 1: Preparación (15 minutos)

**1. Crear Branch de Migración**
```bash
git checkout -b ci/add-github-actions
```

**2. Copiar Workflow Template**
```bash
mkdir -p .github/workflows
# El workflow ya está creado en .github/workflows/docker-build-push.yml
```

**3. Configurar Secrets en GitHub**

Seguir [GITHUB_ACTIONS_SETUP.md - Paso 1 a 3](GITHUB_ACTIONS_SETUP.md#paso-1-configurar-github-secrets):

- `DOCKERHUB_USERNAME` = `jfdelafuente`
- `DOCKERHUB_TOKEN` = [Access Token de Docker Hub]
- `VITE_API_URL` = `https://api.contravento.com`
- `VITE_TURNSTILE_SITE_KEY` = [Cloudflare Turnstile Site Key]

### Fase 2: Testing Inicial (30 minutos)

**1. Push del Workflow**
```bash
git add .github/workflows/docker-build-push.yml
git commit -m "ci: add GitHub Actions workflow for Docker builds"
git push origin ci/add-github-actions
```

**2. Verificar Ejecución Automática**

1. Ir a GitHub → **Actions** tab
2. Verificar que workflow **"Docker Build and Push"** se ejecutó automáticamente
3. Click en la ejecución para ver logs

**3. Validar Cada Stage**

Verificar que todos los steps pasan:

```
✓ Checkout code
✓ Set up Docker Buildx
✓ Log in to Docker Hub
✓ Build Backend Docker Image
✓ Build Frontend Docker Image
✓ Test Backend Image (Health Check)
✓ Test Frontend Image (Nginx Config)
✓ Push Backend Image (solo si no es PR)
✓ Push Frontend Image (solo si no es PR)
```

**4. Verificar Imágenes en Docker Hub**

```bash
# Verificar que las imágenes se pushearon con el tag correcto
docker pull jfdelafuente/contravento-backend:ci-add-github-actions
docker pull jfdelafuente/contravento-frontend:ci-add-github-actions
```

### Fase 3: Integración con Pull Requests (15 minutos)

**1. Crear Pull Request**
```bash
# PR desde ci/add-github-actions → develop
gh pr create --title "CI: Add GitHub Actions workflow" \
  --body "Adds GitHub Actions as CI/CD alternative to Jenkins"
```

**2. Verificar Checks en PR**

GitHub automáticamente ejecutará el workflow en el PR:

1. Ir a la página del PR
2. Scroll a **"Checks"** section
3. Verificar status **"Docker Build and Push"**
4. ✅ **Expected**: Build pasa pero NO pushea a Docker Hub (por diseño)

**3. Merge del PR**

Una vez aprobado:
```bash
gh pr merge --squash
```

### Fase 4: Production Deployment (20 minutos)

**1. Tag de Release**
```bash
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release 1.0.0 - GitHub Actions CI/CD"
git push origin v1.0.0
```

**2. Verificar Build Automático**

GitHub Actions detectará el tag y creará:
- `jfdelafuente/contravento-backend:1.0.0`
- `jfdelafuente/contravento-backend:1.0`
- `jfdelafuente/contravento-frontend:1.0.0`
- `jfdelafuente/contravento-frontend:1.0`

**3. Validar en Production**
```bash
docker pull jfdelafuente/contravento-backend:1.0.0
docker pull jfdelafuente/contravento-frontend:1.0.0

# Ejecutar containers y verificar
docker run -p 8000:8000 jfdelafuente/contravento-backend:1.0.0
docker run -p 80:80 jfdelafuente/contravento-frontend:1.0.0
```

---

## Estrategias de Coexistencia

Puedes mantener **ambos** pipelines (Jenkins + GitHub Actions) en paralelo.

### Estrategia 1: GitHub Actions Principal, Jenkins Backup

**Configuración**:
- GitHub Actions: CI automático en todos los push/PR
- Jenkins: Manual trigger para deploys críticos

**Uso**:
```bash
# Push automático → GitHub Actions ejecuta
git push origin develop

# Deploy a producción → Ejecutar Jenkins manualmente
# (con aprobaciones humanas configuradas)
```

### Estrategia 2: Split por Entorno

**Configuración**:
- GitHub Actions: staging, development
- Jenkins: production (mayor control)

**Implementación**:

GitHub Actions (`.github/workflows/docker-build-push.yml`):
```yaml
on:
  push:
    branches:
      - develop
      - 'feature/**'
```

Jenkins (Jenkinsfile):
```groovy
when {
    branch 'main'  // Solo producción
}
```

### Estrategia 3: Split por Tipo de Build

**Configuración**:
- GitHub Actions: Docker images (rápido, paralelizable)
- Jenkins: Workflows complejos (tests E2E, deploys con pasos manuales)

**Ejemplo**:

GitHub Actions:
```yaml
jobs:
  build-images:
    # Construir imágenes Docker
```

Jenkins:
```groovy
stage('E2E Tests') {
    steps {
        sh 'npm run test:e2e'
    }
}
stage('Deploy to Production') {
    input message: '¿Aprobar deploy a producción?'
    steps {
        sh './deploy.sh prod'
    }
}
```

---

## Ventajas y Desventajas

### GitHub Actions

**Ventajas** ✅:
- Zero setup (no servidor que mantener)
- Integración nativa con GitHub (UI, PRs, checks)
- Secrets management integrado
- 2000 minutos/mes gratis (repositorios privados)
- Cache de Docker layers automático
- Matrix builds para múltiples versiones
- Marketplace con miles de actions pre-hechas

**Desventajas** ❌:
- Limitaciones de runners (14GB disco, 2 cores, 7GB RAM)
- Timeout de 6 horas por job
- No hay UI visual como Blue Ocean
- Menos flexible para workflows muy complejos
- Logs se borran después de 90 días (plan gratis)

### Jenkins

**Ventajas** ✅:
- Control total (self-hosted)
- Sin límites de tiempo/recursos
- Plugins para cualquier caso de uso
- Blue Ocean (UI visual para pipelines)
- Aprobaciones manuales robustas
- Historial infinito de builds
- Pipelines compartidos entre repos

**Desventajas** ❌:
- Requiere servidor dedicado (costo infraestructura)
- Mantenimiento del servidor + plugins
- Setup complejo (webhooks manuales)
- UI menos moderna que GitHub Actions
- Credentials management requiere plugin adicional

---

## Recomendación Final

### Para ContraVento

**Estrategia Recomendada**: **Migración Completa a GitHub Actions**

**Razones**:
1. ✅ **Repositorio en GitHub**: Integración nativa
2. ✅ **Team Pequeño**: No justifica servidor Jenkins dedicado
3. ✅ **Builds Simples**: Docker build + push (no workflows complejos)
4. ✅ **Costo**: Gratis (repositorio público o <2000 min/mes)
5. ✅ **Mantenimiento**: Zero (GitHub gestiona runners)

**Plan de Migración**:

```
Semana 1: Setup GitHub Actions (DONE ✅)
├── Configurar secrets
├── Crear workflow .github/workflows/docker-build-push.yml
└── Testear en branch de prueba

Semana 2: Parallel Run
├── Mantener Jenkins activo
├── Monitorear ambos pipelines
└── Validar que GitHub Actions funciona correctamente

Semana 3: Deprecate Jenkins
├── Actualizar README.md con instrucciones de GitHub Actions
├── Archivar Jenkinsfile (no eliminar, solo deprecar)
└── Documentar que GitHub Actions es el pipeline oficial

Semana 4: Cleanup
├── Apagar servidor Jenkins (opcional - mantener como backup)
├── Actualizar documentación de deployment
└── Entrenar equipo en GitHub Actions
```

**Rollback Plan**:

Si GitHub Actions falla en producción:
1. Jenkinsfile todavía está en el repo (deprecado pero funcional)
2. Re-activar servidor Jenkins
3. Trigger build manual
4. Investigar issue de GitHub Actions en paralelo

---

## Recursos Adicionales

### Documentación Creada

- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md): Guía completa de setup
- [JENKINS_SETUP.md](JENKINS_SETUP.md): Guía de Jenkins (legacy)
- [JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md): Setup de credentials Jenkins

### Archivos Clave

- `.github/workflows/docker-build-push.yml`: GitHub Actions workflow
- `Jenkinsfile`: Jenkins pipeline (mantener como backup)

### Siguientes Pasos

1. ✅ **Testing**: Ejecutar workflow en branch de prueba
2. ✅ **Secrets**: Configurar GitHub Secrets
3. ⏳ **Monitoring**: Monitorear ejecuciones durante 1-2 semanas
4. ⏳ **Deprecation**: Marcar Jenkinsfile como deprecated
5. ⏳ **Documentation**: Actualizar README.md con GitHub Actions como principal

---

**Última actualización**: 2026-01-22
**Autor**: Claude + @jfdelafuente
**Estado**: ✅ Migración implementada, lista para testing
