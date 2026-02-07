# GitHub Actions - Guía de Configuración

Esta guía proporciona instrucciones paso a paso para configurar GitHub Actions como alternativa/complemento a Jenkins para CI/CD.

## 📋 Resumen

GitHub Actions es la plataforma de CI/CD integrada en GitHub. Ventajas sobre Jenkins:

- ✅ **Zero Infrastructure**: No requiere servidor Jenkins (GitHub-hosted runners)
- ✅ **Integración Nativa**: Triggers automáticos en push/PR
- ✅ **Secrets Management**: UI integrada para gestión de secretos
- ✅ **Marketplace**: Miles de actions pre-hechas
- ✅ **Gratis**: 2000 minutos/mes para repositorios privados (ilimitado para públicos)

## 🔐 Paso 1: Configurar GitHub Secrets

Los secrets en GitHub Actions son equivalentes a las credentials de Jenkins.

### Acceder a Secrets

1. Ir a tu repositorio en GitHub
2. Click en **"Settings"** (tab superior)
3. En el menú lateral izquierdo, expandir **"Secrets and variables"**
4. Click en **"Actions"**
5. Click en **"New repository secret"**

### Descripción Visual

```
GitHub Repository
└── Settings (tab)
    └── Secrets and variables (sidebar)
        └── Actions
            └── Repository secrets
                └── [New repository secret]
```

## 🐳 Paso 2: Configurar Docker Hub Secrets

### Secret 1: DOCKERHUB_USERNAME

**Campos a completar:**

| Campo | Valor |
|-------|-------|
| **Name** | `DOCKERHUB_USERNAME` ⚠️ **EXACTO - case-sensitive** |
| **Secret** | `jfdelafuente` |

Click **"Add secret"**

### Secret 2: DOCKERHUB_TOKEN

**Campos a completar:**

| Campo | Valor |
|-------|-------|
| **Name** | `DOCKERHUB_TOKEN` ⚠️ **EXACTO - case-sensitive** |
| **Secret** | `[Tu Docker Hub Access Token]` |

### ⚠️ IMPORTANTE: Usar Access Token, NO tu contraseña

**Obtener Docker Hub Access Token** (mismo proceso que Jenkins):

1. Login en https://hub.docker.com
2. Click en tu avatar (esquina superior derecha)
3. Click **"Account Settings"**
4. Click **"Security"** (menú lateral)
5. Scroll hasta **"Access Tokens"**
6. Click **"New Access Token"**

**Formulario de creación del token:**

| Campo | Valor |
|-------|-------|
| **Access Token Description** | `github-actions-contravento` |
| **Access permissions** | ✅ Read<br>✅ Write<br>✅ Delete |

7. Click **"Generate"**
8. **⚠️ COPIAR EL TOKEN INMEDIATAMENTE** (solo se muestra una vez)
9. Pegar el token en el campo "Secret" de GitHub

**Ejemplo de token** (no usar, es de ejemplo):
```
dckr_pat_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

## 🌐 Paso 3: Configurar Frontend Environment Secrets

### Secret 3: VITE_API_URL

**Campos a completar:**

| Campo | Valor |
|-------|-------|
| **Name** | `VITE_API_URL` ⚠️ **EXACTO - case-sensitive** |
| **Secret** | `https://api.contravento.com` |

### Valores por Entorno

Si usas múltiples entornos, puedes crear **Environment secrets** en lugar de Repository secrets:

1. Settings → Environments → **"New environment"**
2. Crear entornos: `staging`, `production`
3. En cada entorno, añadir secrets con diferentes valores:

| Entorno | VITE_API_URL |
|---------|--------------|
| **staging** | `https://api-staging.contravento.com` |
| **production** | `https://api.contravento.com` |

**Modificar workflow para usar environments**:
```yaml
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    environment: production  # O staging
    steps:
      # Los secrets se toman del environment especificado
```

### Secret 4: VITE_TURNSTILE_SITE_KEY

**Campos a completar:**

| Campo | Valor |
|-------|-------|
| **Name** | `VITE_TURNSTILE_SITE_KEY` ⚠️ **EXACTO - case-sensitive** |
| **Secret** | `[Tu Cloudflare Turnstile Site Key]` |

**Obtener Cloudflare Turnstile Site Key** (mismo proceso que Jenkins):

1. Login en https://dash.cloudflare.com
2. En el menú lateral, click **"Turnstile"**
3. Si no tienes un widget, click **"Add widget"**
4. Configurar el widget:

| Campo | Valor |
|-------|-------|
| **Widget name** | `ContraVento Production` |
| **Domain** | `contravento.com` |
| **Widget mode** | `Managed` (recomendado) |

5. Click **"Create"**
6. Copiar el **"Site Key"** (empieza con `0x4...`)
7. Pegar el Site Key en el campo "Secret" de GitHub

**Para Testing/Staging** (siempre pasan):
```
Site Key: 1x00000000000000000000AA
```

## ✅ Paso 4: Verificar Secrets Configurados

### Opción A: Verificación Visual (UI)

1. Ir a **Settings** → **Secrets and variables** → **Actions**
2. Deberías ver exactamente 4 secrets:

```
Repository secrets
├── DOCKERHUB_USERNAME
├── DOCKERHUB_TOKEN
├── VITE_API_URL
└── VITE_TURNSTILE_SITE_KEY
```

### Opción B: Test con Workflow

Crear un workflow temporal para validar:

```yaml
# .github/workflows/test-secrets.yml
name: Test Secrets

on:
  workflow_dispatch  # Solo ejecución manual

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test Secrets
        run: |
          echo "=== Secrets Validation ==="
          echo "DOCKERHUB_USERNAME is set: ${{ secrets.DOCKERHUB_USERNAME != '' }}"
          echo "DOCKERHUB_TOKEN is set: ${{ secrets.DOCKERHUB_TOKEN != '' }}"
          echo "VITE_API_URL is set: ${{ secrets.VITE_API_URL != '' }}"
          echo "VITE_TURNSTILE_SITE_KEY is set: ${{ secrets.VITE_TURNSTILE_SITE_KEY != '' }}"
          echo "=== All secrets validated ==="
```

Ejecutar manualmente:
1. Ir a **Actions** tab
2. Click en workflow **"Test Secrets"**
3. Click **"Run workflow"**
4. Verificar output (no muestra valores, solo confirma que existen)

**Output esperado**:
```
=== Secrets Validation ===
DOCKERHUB_USERNAME is set: true
DOCKERHUB_TOKEN is set: true
VITE_API_URL is set: true
VITE_TURNSTILE_SITE_KEY is set: true
=== All secrets validated ===
```

Eliminar el workflow después de validar.

## 🚀 Paso 5: Workflow Automático

El workflow está en `.github/workflows/docker-build-push.yml` y se ejecuta automáticamente en:

- **Push** a `develop`, `main`, o branches `feature/**`
- **Pull Request** a `develop` o `main`
- **Manual** (workflow_dispatch)

### Triggers del Workflow

```yaml
on:
  push:
    branches:
      - develop
      - main
      - 'feature/**'
  pull_request:
    branches:
      - develop
      - main
  workflow_dispatch:  # Permite ejecución manual
```

### Ejecución Manual

1. Ir a **Actions** tab en GitHub
2. Seleccionar workflow **"Docker Build and Push"**
3. Click **"Run workflow"** dropdown
4. Seleccionar branch (ej. `develop`)
5. Click **"Run workflow"** button

### Diferencias con Pull Requests

⚠️ **IMPORTANTE**: En Pull Requests, las imágenes se **construyen pero NO se pushean** a Docker Hub:

```yaml
- name: Push Backend Image to Docker Hub
  if: github.event_name != 'pull_request'  # Solo push en eventos directos
```

**Razón**: PRs pueden venir de forks sin permisos de push a Docker Hub.

## 📊 Paso 6: Monitorear Ejecuciones

### Ver Workflow Runs

1. Ir a **Actions** tab
2. Ver lista de ejecuciones recientes
3. Click en una ejecución para ver detalles

**Estados posibles**:
- 🟢 **Success**: Build y push completados
- 🔴 **Failure**: Error en algún step
- 🟡 **In progress**: Ejecutándose
- ⚪ **Queued**: Esperando runner disponible

### Logs Detallados

Click en una ejecución → Ver steps:

```
✓ Checkout code (5s)
✓ Set up Docker Buildx (12s)
✓ Log in to Docker Hub (3s)
✓ Extract metadata for Backend (1s)
✓ Extract metadata for Frontend (1s)
✓ Build Backend Docker Image (3m 45s)
✓ Build Frontend Docker Image (2m 30s)
✓ Test Backend Image (Health Check) (15s)
✓ Test Frontend Image (Nginx Config) (10s)
✓ Push Backend Image to Docker Hub (1m 20s)
✓ Push Frontend Image to Docker Hub (45s)
✓ Image Digest (1s)
```

### Descargar Logs

1. En cualquier workflow run, click en **⋯** (tres puntos)
2. Click **"Download log archive"**
3. Se descarga un ZIP con todos los logs

## 🎯 Paso 7: Tagging Semántico (Opcional)

El workflow está configurado para crear tags automáticos basados en eventos Git:

### Tags Automáticos Generados

```yaml
tags: |
  type=ref,event=branch        # develop, main, feature/xyz
  type=ref,event=pr            # pr-123
  type=semver,pattern={{version}}        # 1.0.0
  type=semver,pattern={{major}}.{{minor}}  # 1.0
  type=raw,value=latest,enable={{is_default_branch}}  # latest (solo main)
```

**Ejemplos**:

| Git Action | Docker Tags Generados |
|------------|----------------------|
| Push a `develop` | `jfdelafuente/contravento-backend:develop` |
| Push a `main` | `jfdelafuente/contravento-backend:main`<br>`jfdelafuente/contravento-backend:latest` |
| PR #123 | `jfdelafuente/contravento-backend:pr-123` (no se pushea) |
| Git tag `v1.0.0` | `jfdelafuente/contravento-backend:1.0.0`<br>`jfdelafuente/contravento-backend:1.0` |

### Crear Release con Tag

```bash
# Tag semántico
git tag -a v1.0.0 -m "Release 1.0.0 - Feature 003 GPS Routes"
git push origin v1.0.0

# GitHub Actions detectará el tag y creará:
# - jfdelafuente/contravento-backend:1.0.0
# - jfdelafuente/contravento-backend:1.0
# - jfdelafuente/contravento-frontend:1.0.0
# - jfdelafuente/contravento-frontend:1.0
```

## 🏗️ Paso 8: Optimizaciones de Build

### Cache de Layers Docker

El workflow usa **GitHub Actions Cache** para acelerar builds:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

**Beneficios**:
- Primera build: ~6 minutos
- Builds posteriores (con cache): ~2 minutos
- Cache compartido entre branches

### Build Paralelo

Backend y Frontend se construyen **secuencialmente** pero podrían paralelizarse con matrix strategy:

```yaml
jobs:
  build-backend:
    # ... build backend

  build-frontend:
    # ... build frontend

  push:
    needs: [build-backend, build-frontend]
    # ... push images
```

**Trade-off**: Más paralelismo = más minutos consumidos (importante si tienes límite).

### Health Checks

El workflow valida que las imágenes funcionen antes de pushear:

**Backend**:
```bash
docker run -d --name backend-test -p 8000:8000 backend:latest
curl -f http://localhost:8000/health || exit 1
```

**Frontend**:
```bash
docker run -d --name frontend-test -p 80:80 frontend:latest
curl -f http://localhost:80 || exit 1
```

Si los health checks fallan → build falla → no se pushea a Docker Hub.

## 🔧 Troubleshooting

### Error: "Resource not accessible by integration"

**Causa**: Permisos insuficientes en el repositorio

**Solución**:
1. Settings → Actions → General
2. En **"Workflow permissions"**, seleccionar:
   - ✅ **Read and write permissions**
3. Guardar cambios

### Error: "Invalid username or password" (Docker Hub)

**Causa**: Token de Docker Hub incorrecto o expirado

**Solución**:
1. Verificar que `DOCKERHUB_TOKEN` es un **Access Token**, no tu password
2. Regenerar token en Docker Hub si ha expirado
3. Actualizar secret en GitHub (Settings → Secrets → Actions)

### Error: "Secret VITE_API_URL not found"

**Causa**: Secret no configurado o nombre incorrecto (case-sensitive)

**Solución**:
1. Verificar nombre exacto: `VITE_API_URL` (no `vite_api_url`)
2. Verificar que está en **Repository secrets** (no Environment secrets sin configurar environment)

### Warning: "Runner out of disk space"

**Causa**: Imágenes Docker llenan disco del runner (runners tienen ~14GB)

**Solución**: Añadir cleanup step al workflow:

```yaml
- name: Cleanup Docker
  if: always()
  run: |
    docker system prune -af --volumes
```

### Error: Build timeout (6 horas)

**Causa**: Build extremadamente lento (muy raro)

**Solución**: Optimizar Dockerfile (multi-stage builds, menos layers)

## 📚 Comparativa: Jenkins vs GitHub Actions

| Aspecto | Jenkins | GitHub Actions |
|---------|---------|----------------|
| **Hosting** | Self-hosted (tu servidor) | GitHub-hosted (gratis) o self-hosted |
| **Setup** | Instalar Jenkins, plugins | Zero setup (archivo YAML) |
| **Credentials** | Credentials Plugin | GitHub Secrets (UI integrada) |
| **Triggers** | Webhooks manuales | Git events automáticos |
| **UI** | Blue Ocean (plugin) | GitHub Actions tab |
| **Costo** | Infraestructura propia | 2000 min/mes gratis (privados) |
| **Debugging** | SSH a servidor Jenkins | Logs en GitHub, re-run con debug |
| **Ecosystem** | Jenkins plugins | GitHub Marketplace (actions) |

**Recomendación**:
- **GitHub Actions**: Para equipos pequeños, repos en GitHub, builds rápidos
- **Jenkins**: Para workflows complejos, self-hosted requirements, multi-repo

**Estrategia Híbrida** (recomendada):
- GitHub Actions para CI (builds, tests)
- Jenkins para CD (deploys a producción con aprobaciones manuales)

## 🔒 Security Best Practices

### 1. Secrets Rotation

Rotar secrets cada 90 días:

```bash
# Regenerar Docker Hub token
# En GitHub: Settings → Secrets → Actions → DOCKERHUB_TOKEN → Update
```

### 2. Branch Protection

Proteger branches principales:

1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require status checks to pass (seleccionar workflow)
   - ✅ Require pull request reviews
   - ✅ Require branches to be up to date

### 3. Environment Protection Rules

Para production environment:

1. Settings → Environments → production → Protection rules
2. Enable:
   - ✅ Required reviewers (añadir tus maintainers)
   - ✅ Wait timer: 5 minutes (cooldown antes de deploy)

### 4. Secrets Scoping

⚠️ **NUNCA** usar secrets en PRs de forks (riesgo de exfiltración):

```yaml
jobs:
  build:
    # Solo ejecutar en repo principal, no en forks
    if: github.event.pull_request.head.repo.full_name == github.repository
```

El workflow actual ya incluye esta protección con `if: github.event_name != 'pull_request'`.

## 🆘 Recursos Adicionales

### Documentación Oficial

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

### Marketplace Actions Útiles

- [docker/login-action](https://github.com/docker/login-action) - Docker Hub login
- [docker/build-push-action](https://github.com/docker/build-push-action) - Build optimizado
- [docker/metadata-action](https://github.com/docker/metadata-action) - Tags automáticos
- [actions/cache](https://github.com/actions/cache) - Cache de dependencies

### Ejemplos de Workflows Avanzados

```yaml
# Multi-environment deployment
name: Deploy to Multiple Environments

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    steps:
      - name: Deploy to ${{ github.event.inputs.environment }}
        run: echo "Deploying to ${{ github.event.inputs.environment }}"
```

### Security Checklist

Antes de ir a producción, verificar:

- [ ] Secrets configurados con valores correctos
- [ ] Docker Hub Access Token tiene permisos mínimos (Read/Write, no Admin)
- [ ] Turnstile Site Key es de producción (no testing key)
- [ ] API URL usa HTTPS (no HTTP)
- [ ] Branch protection habilitada en `main`
- [ ] Required status checks incluyen workflow
- [ ] Environment protection rules configuradas (si usas environments)
- [ ] No hay secrets hardcodeados en workflow YAML
- [ ] Fork PR protection habilitada (`if: github.event_name != 'pull_request'`)

---

**Última actualización**: 2026-01-22
**Autor**: Claude + @jfdelafuente
**Estado**: ✅ Documentación completa y verificada
