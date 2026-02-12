# Docker Hub Setup Guide

**Propósito**: Configurar Docker Hub como registry centralizado para imágenes de ContraVento (staging y producción).

**Fecha**: 2026-02-12

**Prerequisitos**: Ninguno (cuenta gratuita de Docker Hub es suficiente)

---

## 📋 Checklist Completo

**Nota**: Este proyecto usa repositorios de usuario personal (`jfdelafuente/contravento-backend`, `jfdelafuente/contravento-frontend`) en lugar de organización.

- [ ] Paso 1: Crear cuenta Docker Hub (o usar existente)
- [ ] ~~Paso 2: Crear organization~~ (SKIP - usando usuario personal)
- [ ] Paso 3: Crear repositorios (contravento-backend, contravento-frontend)
- [ ] Paso 4: Generar Access Token
- [ ] Paso 5: Configurar GitHub Secrets
- [ ] Paso 6: Configurar Docker login en servidores
- [ ] Paso 7: Test workflow con push a develop

---

## Paso 1: Crear Cuenta Docker Hub

**Duración estimada**: 5 minutos

### Acciones

1. Ir a [https://hub.docker.com/signup](https://hub.docker.com/signup)

2. Registrarse con:
   - **Docker ID**: Elegir username (ejemplo: `contraventoapp` o tu username personal)
   - **Email**: Email válido para notificaciones
   - **Password**: Contraseña segura (min 9 caracteres)

3. Verificar email (check inbox + spam)

4. Login en [https://hub.docker.com](https://hub.docker.com)

**Resultado esperado**: Acceso al dashboard de Docker Hub

---

## Paso 2: Crear Organization "contravento"

**Duración estimada**: 0 minutos (SKIP - no necesario)

### ⚠️ NOTA: Usando Repositorios de Usuario Personal

Este proyecto usa repositorios bajo el usuario personal en lugar de organización:
- `jfdelafuente/contravento-backend`
- `jfdelafuente/contravento-frontend`

**Ventajas**:
- ✅ Setup más simple (sin organización)
- ✅ Free tier: unlimited public repositories
- ✅ Suficiente para proyectos individuales

**Desventajas**:
- ⚠️ Menos separación entre proyectos personales
- ⚠️ Colaboración más limitada (se puede añadir después)

### Acciones

**SKIP este paso** - No es necesario crear organización.

Los repositorios se crearán directamente bajo el usuario `jfdelafuente`.

---

## Paso 3: Crear Repositorios (backend, frontend)

**Duración estimada**: 5 minutos

### Repositorio 1: Backend

1. En organization page, click en **"Create Repository"**

2. Configurar repositorio:
   ```
   Namespace: jfdelafuente
   Repository name: contravento-backend
   Description: ContraVento FastAPI Backend - Production & Staging Images
   Visibility: Public (o Private si prefieres - Free plan: 1 private repo max)
   ```

3. Click en **"Create"**

**Resultado**: Repository creado en `jfdelafuente/contravento-backend`

### Repositorio 2: Frontend

1. Repetir proceso anterior

2. Configurar repositorio:
   ```
   Namespace: contravento
   Repository name: frontend
   Description: ContraVento React Frontend - Production & Staging Images
   Visibility: Public (o Private - requiere upgrade si backend ya es private)
   ```

3. Click en **"Create"**

**Resultado**: Repository creado en `jfdelafuente/contravento-frontend`

### Verificación

Ambos repositorios deben estar visibles en:
- https://hub.docker.com/r/jfdelafuente/contravento-backend
- https://hub.docker.com/r/jfdelafuente/contravento-frontend

**Status inicial**: "No tags" (esperado - se crearán cuando GitHub Actions haga push)

---

## Paso 4: Generar Access Token

**Duración estimada**: 3 minutos

### ¿Por qué Access Token?

- GitHub Actions necesita autenticarse para push de imágenes
- Más seguro que usar password directamente
- Permite revocar acceso sin cambiar password
- Permisos granulares (Read, Write, Delete)

### Acciones

1. Click en tu avatar (esquina superior derecha) → **"Account Settings"**

2. En sidebar izquierdo, click en **"Security"**

3. Scroll hasta sección **"Access Tokens"**

4. Click en **"New Access Token"**

5. Configurar token:
   ```
   Access Token Description: GitHub Actions CI/CD
   Access permissions: Read, Write, Delete
   ```

   **Importante**: Habilitar los 3 permisos:
   - ✅ **Read**: Permite pull de imágenes
   - ✅ **Write**: Permite push de imágenes (CRÍTICO)
   - ✅ **Delete**: Permite limpiar tags antiguos (opcional pero útil)

6. Click en **"Generate"**

7. **CRÍTICO**: Copiar el token **INMEDIATAMENTE**
   ```
   Token format: dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

   ⚠️ **ADVERTENCIA**: El token solo se muestra UNA VEZ. Si lo pierdes, tendrás que generar uno nuevo.

8. Guardar token en lugar seguro (password manager recomendado)

**Resultado esperado**: Token copiado, listo para configurar en GitHub

---

## Paso 5: Configurar GitHub Secrets

**Duración estimada**: 3 minutos

### Acciones

1. Ir a tu repositorio GitHub:
   ```
   https://github.com/jfdelafuente/contravento-application-python
   ```

2. Click en **Settings** (tab superior)

3. En sidebar izquierdo, expandir **"Secrets and variables"** → click en **"Actions"**

4. Click en **"New repository secret"**

5. **Secret 1: DOCKERHUB_USERNAME**
   ```
   Name: DOCKERHUB_USERNAME
   Secret: jfdelafuente  (tu username de Docker Hub)
   ```

   Click en **"Add secret"**

6. Click en **"New repository secret"** de nuevo

7. **Secret 2: DOCKERHUB_TOKEN**
   ```
   Name: DOCKERHUB_TOKEN
   Secret: dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  (pegar token del Paso 4)
   ```

   Click en **"Add secret"**

### Verificación

En la página "Actions secrets and variables", debes ver:
```
Repository secrets (2):
- DOCKERHUB_USERNAME
- DOCKERHUB_TOKEN
```

**Nota**: Los valores no son visibles (solo nombres). Esto es correcto por seguridad.

---

## Paso 6: Configurar Docker Login en Servidores

**Duración estimada**: 5 minutos por servidor

### ¿Por qué es necesario?

Los servidores (staging, production) necesitan autenticarse con Docker Hub para **pull** de imágenes durante el deployment manual.

### Servidor Staging

1. SSH al servidor staging:
   ```bash
   ssh staging-server
   ```

2. Login a Docker Hub:
   ```bash
   docker login
   ```

3. Cuando pregunte:
   ```
   Username: contravento
   Password: [pegar el mismo Access Token del Paso 4]
   ```

   **Importante**: Usa el Access Token como password, NO tu password de Docker Hub.

4. Verificar login exitoso:
   ```bash
   docker pull jfdelafuente/contravento-backend:staging-latest
   # Expected: Error (image doesn't exist yet) - esto es OK
   # Si dice "unauthorized", el login falló
   ```

5. El login queda persistido en `~/.docker/config.json`

### Servidor Production

Repetir proceso anterior en servidor de producción:

```bash
ssh production-server
docker login
# Username: contravento
# Password: [Access Token]
```

**Resultado esperado**: Ambos servidores autenticados con Docker Hub

---

## Paso 7: Test Workflow con Push a develop

**Duración estimada**: 10-15 minutos

### Pre-requisitos

Asegúrate de que los workflows estén commiteados y pusheados:

```bash
git status
# Verificar que .github/workflows/build-staging-image.yml existe
# Verificar que .github/workflows/build-production-image.yml existe

git add .github/workflows/
git commit -m "ci: add Docker Hub build workflows for staging and production"
git push origin develop
```

### Test del Workflow de Staging

1. **Crear cambio trivial en develop**:
   ```bash
   git checkout develop
   git pull origin develop

   # Crear cambio trivial (ejemplo: actualizar README)
   echo "" >> README.md
   echo "**Última actualización CI/CD**: $(date)" >> README.md

   git add README.md
   git commit -m "chore: test Docker Hub workflow"
   git push origin develop
   ```

2. **Monitorear GitHub Actions**:
   - Ir a https://github.com/jfdelafuente/contravento-application-python/actions
   - Debería aparecer un nuevo workflow run: "Build Staging Images"
   - Click en el workflow para ver logs en vivo

3. **Verificar pasos del workflow**:
   ```
   ✅ Checkout code
   ✅ Set up Docker Buildx
   ✅ Login to Docker Hub
   ✅ Extract commit SHA (short)
   ✅ Build and push backend
      - Tag: jfdelafuente/contravento-backend:staging-latest
      - Tag: jfdelafuente/contravento-backend:staging-abc123d
   ✅ Build and push frontend
      - Tag: jfdelafuente/contravento-frontend:staging-latest
      - Tag: jfdelafuente/contravento-frontend:staging-abc123d
   ✅ Summary
   ```

4. **Verificar imágenes en Docker Hub**:
   - Backend: https://hub.docker.com/r/jfdelafuente/contravento-backend/tags
   - Frontend: https://hub.docker.com/r/jfdelafuente/contravento-frontend/tags

   Debes ver tags:
   ```
   jfdelafuente/contravento-backend
   - staging-latest (pushed X minutes ago)
   - staging-abc123d (pushed X minutes ago)

   jfdelafuente/contravento-frontend
   - staging-latest (pushed X minutes ago)
   - staging-abc123d (pushed X minutes ago)
   ```

5. **Test manual deploy en staging server**:
   ```bash
   ssh staging-server
   cd /opt/contravento

   # ✅ Deploy usando la función pull_from_dockerhub() de deploy.sh
   ./deploy.sh staging --pull-latest

   # Verificar deployment exitoso
   docker-compose ps
   docker-compose logs -f --tail=50 backend frontend

   # Verificar imágenes descargadas
   docker images | grep contravento
   # Expected:
   # jfdelafuente/contravento-backend    staging-latest   abc123def   2 minutes ago   XMB
   # jfdelafuente/contravento-backend    latest           abc123def   2 minutes ago   XMB
   # jfdelafuente/contravento-frontend   staging-latest   def456ghi   2 minutes ago   YMB
   # jfdelafuente/contravento-frontend   latest           def456ghi   2 minutes ago   YMB
   ```

### Test del Workflow de Production (Opcional)

**Advertencia**: Esto hará push a `main` y generará un release. Solo si quieres crear Release v1.0.0:

```bash
git checkout main
git merge develop
git push origin main
```

Workflow `build-production-image.yml` se ejecutará:
- Build de imágenes con tags: `latest`, `v1.0.0`, `production-{SHA}`
- Creación de Git tag `v1.0.0`
- Generación de changelog
- Creación de GitHub Release

---

## 🎉 Verificación Final

### Checklist de Éxito

- [x] Cuenta Docker Hub creada y verificada
- [x] Organization `contravento` creada
- [x] Repositorios `jfdelafuente/contravento-backend` y `jfdelafuente/contravento-frontend` creados
- [x] Access Token generado y guardado
- [x] GitHub Secrets configurados (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN)
- [x] Servidores con `docker login` configurado
- [x] Workflow `build-staging-image.yml` ejecutado exitosamente
- [x] Imágenes visibles en Docker Hub con tags correctos
- [x] Pull manual de imágenes funciona desde staging server

### Qué sigue

Con Docker Hub configurado, el próximo paso es:

**Opción B - Actualizar deploy.sh**: Añadir función `pull_from_dockerhub()` para automatizar pulls desde registry.

Ver: [SEMI_AUTO_DEPLOYMENT_SUMMARY.md](SEMI_AUTO_DEPLOYMENT_SUMMARY.md#semana-4-actualizar-deploysh)

---

## Troubleshooting

### Problema 1: "unauthorized" al hacer push desde GitHub Actions

**Síntoma**:
```
Error: failed to solve: failed to push jfdelafuente/contravento-backend:staging-latest: unauthorized
```

**Soluciones**:
1. Verificar que `DOCKERHUB_USERNAME` es `contravento` (el namespace, no tu user personal)
2. Verificar que `DOCKERHUB_TOKEN` es el Access Token completo (empieza con `dckr_pat_`)
3. Regenerar Access Token con permisos Read, Write, Delete
4. Re-configurar secrets en GitHub

### Problema 2: "repository does not exist" en Docker Hub

**Síntoma**:
```
Error: failed to push: repository jfdelafuente/contravento-backend does not exist
```

**Soluciones**:
1. Verificar que los repositorios existen en Docker Hub
2. Verificar que están bajo organization `contravento`, no bajo user personal
3. Si los repositorios son **private**, verificar que tienes límite disponible (Free plan: 1 private repo)

### Problema 3: Workflow no se ejecuta después de push

**Síntoma**: No aparece workflow en Actions tab después de push a develop

**Soluciones**:
1. Verificar que `.github/workflows/build-staging-image.yml` está en la rama develop
2. Verificar sintaxis YAML con: https://www.yamllint.com/
3. Revisar triggers en workflow:
   ```yaml
   on:
     push:
       branches: [develop]
   ```
4. Verificar que el push fue a `develop`, no a otra rama

### Problema 4: "docker login" falla en servidor

**Síntoma**:
```
Error saving credentials: error storing credentials
```

**Soluciones**:
1. Instalar `pass` o `gnupg2` en el servidor:
   ```bash
   sudo apt-get update
   sudo apt-get install pass gnupg2
   ```
2. O usar plain text credentials (menos seguro):
   ```bash
   # En ~/.docker/config.json, configurar:
   {
     "auths": {
       "https://index.docker.io/v1/": {
         "auth": "<base64 de username:token>"
       }
     }
   }
   ```

### Problema 5: Build tarda demasiado (>10 minutos)

**Síntoma**: Workflow tarda >10 minutos en build + push

**Soluciones**:
1. Verificar que cache está configurado:
   ```yaml
   cache-from: type=registry,ref=jfdelafuente/contravento-backend:staging-latest
   cache-to: type=inline
   ```
2. Primer build siempre es lento (~5-10 min). Builds posteriores usan cache (~2-3 min)
3. Optimizar Dockerfile:
   - Ordenar layers de menos a más cambiantes
   - Usar multi-stage builds si aplica
   - Añadir `.dockerignore` para excluir archivos innecesarios

---

## Recursos

- **Docker Hub Docs**: https://docs.docker.com/docker-hub/
- **GitHub Actions Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **Docker Build Push Action**: https://github.com/docker/build-push-action
- **Troubleshooting Docker Hub**: https://docs.docker.com/docker-hub/troubleshoot/

---

**Última actualización**: 2026-02-12
**Próxima revisión**: Después del primer deployment exitoso a staging
