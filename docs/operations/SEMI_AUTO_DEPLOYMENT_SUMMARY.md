# Deployment Semi-Automático - Resumen Ejecutivo

**Fecha**: 2026-02-12
**Estado**: Propuesta Aprobada
**Modelo**: Build Automático + Deploy Manual

---

## 🎯 Decisión: Deployment Semi-Automático

### ¿Por qué Semi-Automático?

**Ventajas vs Full-Automático**:
- ✅ **Más control**: Decides cuándo hacer deploy (no automático al mergear)
- ✅ **Más simple**: No requiere SSH keys en GitHub Actions
- ✅ **Más seguro**: Verificas staging antes de producción
- ✅ **Más flexible**: Puedes hacer rollback inmediato si algo falla
- ✅ **Mejor para equipos pequeños**: No necesitas configurar GitHub Environments complejos

**Trade-offs**:
- ⚠️ Requiere SSH manual al servidor (pero ya lo haces)
- ⚠️ Deploy no es instantáneo (pero tienes control)

---

## 🔄 Workflow Completo

### Desarrollo → Staging

```
1. Feature branch → PR → develop
2. GitHub Actions:
   ✅ Run tests (backend + frontend + E2E)
   ✅ Build Docker images
   ✅ Tag: staging-latest, staging-{commit-sha}
   ✅ Push to Docker Hub
   ✅ Notify: "Staging images ready"

3. Developer (manual):
   ssh staging-server
   cd /opt/contravento
   ./deploy.sh staging --pull-latest

4. QA manual en https://staging.contravento.com
```

### Staging → Production

```
1. develop → Release PR → main
2. GitHub Actions:
   ✅ Run all tests
   ✅ Build Docker images (production)
   ✅ Tag: latest, v1.3.0, production-{commit-sha}
   ✅ Push to Docker Hub
   ✅ Create Git tag v1.3.0
   ✅ Generate GitHub Release + Changelog
   ✅ Notify: "Production images ready: v1.3.0"

3. Team Lead (manual):
   ssh production-server
   cd /opt/contravento
   ./deploy.sh prod --pull-version v1.3.0

4. Health checks + Monitoring
5. Rollback si problemas:
   ./deploy.sh prod --rollback-to v1.2.0
```

---

## 🐳 Docker Hub Setup

### 1. Crear Cuenta y Repositorios

```bash
# 1. Ir a https://hub.docker.com
# 2. Crear account (free tier es suficiente)
# 3. Crear organization: "contravento"
# 4. Crear 2 repositorios:
#    - jfdelafuente/contravento-backend (public o private)
#    - jfdelafuente/contravento-frontend (public o private)
```

### 2. Generar Access Token

```
Docker Hub → Account Settings → Security → New Access Token
- Description: "GitHub Actions CI/CD"
- Permissions: Read, Write, Delete
- Copy token (solo se muestra una vez)
```

### 3. Configurar GitHub Secrets

```
GitHub Repo → Settings → Secrets and variables → Actions

Añadir 2 secrets:
- DOCKERHUB_USERNAME: tu-usuario-dockerhub
- DOCKERHUB_TOKEN: dckr_pat_xxxxxxxxxxxxx (token del paso anterior)
```

---

## 📦 Estructura de Tags en Docker Hub

### Staging (develop branch)

```
jfdelafuente/contravento-backend:staging-latest         ← Siempre apunta al último commit en develop
jfdelafuente/contravento-backend:staging-abc123d        ← Commit SHA específico (inmutable)
jfdelafuente/contravento-backend:staging-def456e        ← Otro commit SHA

jfdelafuente/contravento-frontend:staging-latest
jfdelafuente/contravento-frontend:staging-abc123d
jfdelafuente/contravento-frontend:staging-def456e
```

### Production (main branch)

```
jfdelafuente/contravento-backend:latest                 ← Siempre apunta a la última release
jfdelafuente/contravento-backend:v1.3.0                 ← Versión semántica (inmutable)
jfdelafuente/contravento-backend:v1.2.0
jfdelafuente/contravento-backend:production-abc123d     ← Commit SHA (backup)

jfdelafuente/contravento-frontend:latest
jfdelafuente/contravento-frontend:v1.3.0
jfdelafuente/contravento-frontend:v1.2.0
jfdelafuente/contravento-frontend:production-abc123d
```

**Regla de Oro**: En producción SIEMPRE usar versión específica (`v1.3.0`), nunca `latest`.

---

## 🛠️ Actualizar deploy.sh

### Añadir Función Pull desde Docker Hub

```bash
# En deploy.sh (nuevo)

pull_from_dockerhub() {
    local env=$1
    local tag=$2  # "staging-latest", "v1.3.0", etc.

    echo "🐳 Pulling images from Docker Hub..."
    docker pull jfdelafuente/contravento-backend:${tag}
    docker pull jfdelafuente/contravento-frontend:${tag}

    # Re-tag como latest para docker-compose
    docker tag jfdelafuente/contravento-backend:${tag} jfdelafuente/contravento-backend:latest
    docker tag jfdelafuente/contravento-frontend:${tag} jfdelafuente/contravento-frontend:latest

    echo "✅ Images pulled and tagged"
}

# Modificar función deploy
deploy() {
    local env=$1
    local pull_option=$2
    local version=$3

    case "$pull_option" in
        --pull-latest)
            if [ "$env" == "staging" ]; then
                pull_from_dockerhub "$env" "staging-latest"
            elif [ "$env" == "prod" ]; then
                echo "❌ Error: Use --pull-version for production"
                exit 1
            fi
            ;;
        --pull-version)
            if [ "$env" == "prod" ]; then
                pull_from_dockerhub "$env" "$version"
            else
                echo "❌ Error: --pull-version only for production"
                exit 1
            fi
            ;;
        --rollback-to)
            pull_from_dockerhub "$env" "$version"
            ;;
        *)
            echo "❌ Invalid option. Use: --pull-latest, --pull-version, or --rollback-to"
            exit 1
            ;;
    esac

    # Continuar con deploy normal
    docker-compose -f docker-compose.yml -f docker-compose.${env}.yml up -d
}

# Ejemplos de uso:
# ./deploy.sh staging --pull-latest
# ./deploy.sh prod --pull-version v1.3.0
# ./deploy.sh prod --rollback-to v1.2.0
```

---

## 🔧 GitHub Actions Workflow

### build-staging-image.yml (Nuevo)

```yaml
name: Build Staging Images

on:
  push:
    branches: [develop]

jobs:
  build-and-push:
    name: Build and Push Staging Images
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract commit SHA (short)
        id: vars
        run: echo "sha_short=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            jfdelafuente/contravento-backend:staging-latest
            jfdelafuente/contravento-backend:staging-${{ steps.vars.outputs.sha_short }}
          cache-from: type=registry,ref=jfdelafuente/contravento-backend:staging-latest
          cache-to: type=inline

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          build-args: |
            VITE_API_URL=https://staging.contravento.com/api
          tags: |
            jfdelafuente/contravento-frontend:staging-latest
            jfdelafuente/contravento-frontend:staging-${{ steps.vars.outputs.sha_short }}
          cache-from: type=registry,ref=jfdelafuente/contravento-frontend:staging-latest
          cache-to: type=inline

      - name: Notify success
        run: |
          echo "✅ Staging images built and pushed:"
          echo "   - backend:staging-latest"
          echo "   - backend:staging-${{ steps.vars.outputs.sha_short }}"
          echo "   - frontend:staging-latest"
          echo "   - frontend:staging-${{ steps.vars.outputs.sha_short }}"
```

### build-production-image.yml (Nuevo)

```yaml
name: Build Production Images

on:
  push:
    branches: [main]

jobs:
  build-and-push:
    name: Build and Push Production Images
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract version from package.json
        id: version
        run: |
          VERSION=$(node -p "require('./package.json').version")
          echo "version=v${VERSION}" >> $GITHUB_OUTPUT

      - name: Extract commit SHA (short)
        id: vars
        run: echo "sha_short=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            jfdelafuente/contravento-backend:latest
            jfdelafuente/contravento-backend:${{ steps.version.outputs.version }}
            jfdelafuente/contravento-backend:production-${{ steps.vars.outputs.sha_short }}
          cache-from: type=registry,ref=jfdelafuente/contravento-backend:latest
          cache-to: type=inline

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          build-args: |
            VITE_API_URL=https://contravento.com/api
          tags: |
            jfdelafuente/contravento-frontend:latest
            jfdelafuente/contravento-frontend:${{ steps.version.outputs.version }}
            jfdelafuente/contravento-frontend:production-${{ steps.vars.outputs.sha_short }}
          cache-from: type=registry,ref=jfdelafuente/contravento-frontend:latest
          cache-to: type=inline

      - name: Create Git tag
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git tag -a ${{ steps.version.outputs.version }} -m "Release ${{ steps.version.outputs.version }}"
          git push origin ${{ steps.version.outputs.version }}

      - name: Generate changelog
        run: |
          # Install conventional-changelog
          npm install -g conventional-changelog-cli
          conventional-changelog -p angular -i CHANGELOG.md -s

      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ steps.version.outputs.version }}
          release_name: Release ${{ steps.version.outputs.version }}
          body_path: CHANGELOG.md
          draft: false
          prerelease: false

      - name: Notify success
        run: |
          echo "🎉 Production images built and pushed:"
          echo "   - backend:latest"
          echo "   - backend:${{ steps.version.outputs.version }}"
          echo "   - frontend:latest"
          echo "   - frontend:${{ steps.version.outputs.version }}"
          echo ""
          echo "🏷️ Git tag created: ${{ steps.version.outputs.version }}"
          echo "📦 GitHub Release created"
          echo ""
          echo "👤 Ready for manual deployment!"
```

---

## 📋 Checklist de Implementación

### Semana 1-2: Setup Docker Hub

- [ ] Crear cuenta Docker Hub
- [ ] Crear organization "contravento"
- [ ] Crear repositorios: backend, frontend
- [ ] Generar Access Token
- [ ] Añadir secrets a GitHub (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- [ ] Test: Build local y push manual a Docker Hub

### Semana 3: Implementar Workflows

- [ ] Crear `.github/workflows/build-staging-image.yml`
- [ ] Crear `.github/workflows/build-production-image.yml`
- [ ] Test: Push a develop → verificar build automático
- [ ] Test: Verificar imágenes en Docker Hub

### Semana 4: Actualizar deploy.sh

- [ ] Añadir función `pull_from_dockerhub()`
- [ ] Modificar función `deploy()` con opciones: --pull-latest, --pull-version, --rollback-to
- [ ] Test en staging server: `./deploy.sh staging --pull-latest`
- [ ] Documentar en `docs/deployment/manual-deploy-guide.md`

### Semana 5: Testing End-to-End

- [ ] Feature branch → develop → build staging images → deploy manual a staging
- [ ] develop → main → build production images → deploy manual a production
- [ ] Test rollback: `./deploy.sh prod --rollback-to v1.2.0`
- [ ] Verificar health checks funcionan

### Semana 6: Documentación y Training

- [ ] Actualizar README.md con nuevo workflow
- [ ] Crear video/walkthrough del proceso
- [ ] Team training session
- [ ] Comunicar a stakeholders

---

## 🚀 Deployment Manual - Comandos Rápidos

### Staging (después de merge a develop)

```bash
# 1. Esperar notificación: "Staging images ready"

# 2. SSH al servidor
ssh staging-server

# 3. Deploy
cd /opt/contravento
./deploy.sh staging --pull-latest

# 4. Verificar logs
docker-compose logs -f --tail=50 backend frontend

# 5. Test manual en https://staging.contravento.com
```

### Production (después de merge a main)

```bash
# 1. Esperar notificación: "Production images ready: v1.3.0"

# 2. Verificar staging primero
# QA manual en staging

# 3. SSH al servidor producción
ssh production-server

# 4. Deploy versión específica
cd /opt/contravento
./deploy.sh prod --pull-version v1.3.0

# 5. Verificar health
curl https://contravento.com/health

# 6. Monitorear logs (primeros 5 min)
docker-compose logs -f --tail=100 backend frontend

# 7. Si problemas → Rollback inmediato
./deploy.sh prod --rollback-to v1.2.0
```

---

## 🔍 Monitoreo Post-Deployment

### Health Checks

```bash
# Backend health
curl https://contravento.com/health
# Expected: {"status": "healthy", "version": "1.3.0"}

# Frontend (verificar versión en HTML)
curl https://contravento.com | grep version

# Database connection
docker-compose exec backend python -c "from src.database import engine; engine.connect()"
```

### Logs en Vivo

```bash
# Backend logs
docker-compose logs -f backend

# Frontend (Nginx) logs
docker-compose logs -f frontend

# Errores críticos (últimas 24h)
docker-compose logs --since 24h backend | grep ERROR

# Performance (requests lentos >1s)
docker-compose logs backend | grep "duration_ms" | awk '{if ($NF > 1000) print}'
```

### Métricas Clave (Primeras 2 Horas)

- ✅ Error rate <1%
- ✅ Response time p95 <500ms
- ✅ Memory usage <80%
- ✅ CPU usage <70%
- ❌ Si alguno falla → Rollback

---

## 📞 Soporte y Troubleshooting

### Problemas Comunes

**1. "Error: Cannot connect to Docker Hub"**
```bash
# Solución: Re-login al servidor
ssh staging-server
docker login
# Username: tu-usuario-dockerhub
# Password: (pegar access token)
```

**2. "Error: Image not found"**
```bash
# Verificar que GitHub Actions completó
# Ver https://github.com/jfdelafuente/contravento-application-python/actions

# Verificar imagen existe en Docker Hub
docker pull jfdelafuente/contravento-backend:staging-latest
```

**3. "Container crashed después de deploy"**
```bash
# Ver logs
docker-compose logs backend

# Rollback a versión anterior
./deploy.sh prod --rollback-to v1.2.0
```

### Contacto

- **GitHub Issues**: Para reportar bugs en CI/CD
- **Slack #devops**: Para soporte deployment
- **Documentación**: `docs/operations/BRANCHING_STRATEGY_CICD.md`

---

**Última actualización**: 2026-02-12
**Próxima revisión**: Después de primer deployment en producción
