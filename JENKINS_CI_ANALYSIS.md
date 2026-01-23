# Análisis de Coherencia: Jenkins CI/CD

**Fecha**: 2026-01-23
**Estado**: Incoherencias graves detectadas

---

## Resumen Ejecutivo

El Jenkinsfile actual y docker-compose-jenkins.yml tienen **múltiples incoherencias** que impiden su uso efectivo como entorno de CI:

1. ❌ Jenkinsfile solo hace build/push, **no ejecuta tests**
2. ❌ Frontend construido con variables de producción, **no puede conectarse al backend de Jenkins**
3. ❌ Healthcheck del frontend roto (wget no existe en nginx:alpine)
4. ❌ docker-compose-jenkins.yml nunca se usa en Jenkins
5. ❌ No hay validación de calidad de código
6. ❌ No hay reportes de coverage

---

## Problemas Detallados

### 1. Jenkinsfile: Solo Build & Push (NO es CI)

**Archivo**: `Jenkinsfile`

**Stages actuales**:
```groovy
- Git Checkout ✅
- Build Backend Docker Image ✅
- Build Frontend Docker Image ❌ (variables incorrectas)
- Login to Docker Hub ✅
- Push Backend Image ✅
- Push Frontend Image ✅
```

**Stages faltantes para CI real**:
```groovy
- Start CI Environment (usando docker-compose-jenkins.yml)
- Run Backend Tests
- Run Backend Linting (black, ruff, mypy)
- Run Frontend Tests
- Generate Coverage Reports
- Cleanup CI Environment
```

**Impacto**: Jenkins construye imágenes rotas y las sube a Docker Hub sin validar nada.

---

### 2. Frontend: Variables Hardcodeadas Incorrectas

**Archivo**: `Jenkinsfile` líneas 27-34

**Problema**:
```groovy
docker build -t jfdelafuente/contravento-frontend:latest \
  --build-arg VITE_API_URL=$VITE_API_URL \              # ❌ URL de producción/staging
  --build-arg VITE_TURNSTILE_SITE_KEY=$VITE_TURNSTILE_SITE_KEY \
  --build-arg VITE_ENV=production \                     # ❌ Debería ser 'ci'
  --build-arg VITE_DEBUG=false \                        # ❌ Debería ser 'true' para CI
```

**Consecuencia**:
- La imagen del frontend apunta a una API externa (producción/staging)
- NO puede conectarse al backend local de Jenkins en `http://localhost:8000`
- Tests E2E fallarían (si existieran)

**Solución**:
```groovy
# Construir imagen específica para CI
docker build -t jfdelafuente/contravento-frontend:ci \
  --build-arg VITE_API_URL=http://localhost:8000 \
  --build-arg VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA \
  --build-arg VITE_ENV=ci \
  --build-arg VITE_DEBUG=true \
  -f frontend/Dockerfile.prod frontend/
```

---

### 3. Healthcheck del Frontend Roto

**Archivo**: `docker-compose-jenkins.yml` línea 135

**Problema**:
```yaml
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:80"]
```

**Por qué falla**:
- La imagen base es `nginx:alpine`
- Alpine NO incluye `wget` ni `curl` por defecto
- El healthcheck siempre falla

**Solución aplicada**:
```yaml
# Eliminar healthcheck - no crítico para CI
# depends_on: backend: service_healthy ya garantiza orden correcto
```

---

### 4. docker-compose-jenkins.yml Nunca se Usa

**Problema**:
- El archivo está bien documentado
- Tiene ejemplos de uso en los comentarios (líneas 209-264)
- **Pero el Jenkinsfile nunca lo ejecuta**

**Impacto**:
- No hay entorno de testing en Jenkins
- No se ejecutan tests
- No se valida la aplicación antes de subir a Docker Hub

---

### 5. CORS Incoherente

**Archivo**: `docker-compose-jenkins.yml` línea 93

**Configuración**:
```yaml
CORS_ORIGINS: http://localhost:5173,http://localhost:8000
```

**Problema**:
- El backend espera requests desde `localhost:5173`
- Pero el frontend construido en Jenkins apunta a otra URL
- CORS fallará en runtime

---

### 6. Sin Validación de Calidad

**Falta**:
- ❌ Linting (black, ruff, mypy)
- ❌ Type checking
- ❌ Code coverage (≥90% requerido por CLAUDE.md)
- ❌ Security scanning
- ❌ Vulnerability checks

---

## Soluciones Propuestas

### Opción A: Jenkins Solo Build & Push (Documentar lo Actual)

**Si decides mantener el flujo actual**:

1. Renombrar `docker-compose-jenkins.yml` → `docker-compose-ci.yml`
2. Documentar que Jenkins **NO hace CI**, solo build/push
3. Mover testing a GitHub Actions
4. Actualizar README para aclarar responsabilidades

**Pros**:
- ✅ Mínimo cambio
- ✅ Simplicidad

**Contras**:
- ❌ No es realmente CI/CD
- ❌ Imágenes no validadas en Docker Hub
- ❌ Riesgo de deployar código roto

---

### Opción B: Jenkins CI Completo (RECOMENDADO)

**Implementar CI real en Jenkins**:

1. **Usar el nuevo Jenkinsfile** (`Jenkinsfile.proposed`):
   - Construye imágenes :ci con variables locales
   - Levanta entorno con docker-compose-jenkins.yml
   - Ejecuta tests backend + linting
   - Genera reportes de coverage
   - Solo hace push a Docker Hub en branch `main` después de tests exitosos

2. **Actualizar docker-compose-jenkins.yml** (ya hecho):
   - Soporta variables `BACKEND_IMAGE` y `FRONTEND_IMAGE`
   - Eliminado healthcheck roto del frontend
   - Documentación clara sobre imágenes :ci vs :latest

3. **Separar imágenes CI vs Producción**:
   - `:ci` - Construidas en Jenkins para testing (VITE_API_URL=localhost)
   - `:latest` - Construidas en Jenkins para producción (solo en `main`)

**Pros**:
- ✅ CI real con tests
- ✅ Validación antes de push
- ✅ Coverage reports
- ✅ Cumple estándares de CLAUDE.md

**Contras**:
- ⚠️ Requiere actualizar Jenkinsfile
- ⚠️ Pipeline más largo (pero más seguro)

---

## Cambios Realizados

### 1. `docker-compose-jenkins.yml`
- ✅ Backend usa variable `${BACKEND_IMAGE:-jfdelafuente/contravento-backend:latest}`
- ✅ Frontend usa variable `${FRONTEND_IMAGE:-jfdelafuente/contravento-frontend:latest}`
- ✅ Eliminado healthcheck roto del frontend
- ✅ Documentación actualizada sobre imágenes :ci vs :latest
- ✅ SMTP_FROM corregido a `noreply@contravento.com`

### 2. `Jenkinsfile.proposed` (Nuevo)
- ✅ Build de imágenes :ci con variables locales
- ✅ Stage de tests backend
- ✅ Stage de linting
- ✅ Stage de tests frontend (placeholder)
- ✅ Build de imágenes :latest solo en `main`
- ✅ Push a Docker Hub solo en `main` y después de tests
- ✅ Cleanup automático con `post: always`
- ✅ Coverage reports archivados

---

## Próximos Pasos

### Inmediatos

1. **Decidir flujo**: ¿Opción A (solo build) u Opción B (CI completo)?

2. **Si eliges Opción B**:
   ```bash
   # Renombrar Jenkinsfile
   mv Jenkinsfile Jenkinsfile.old
   mv Jenkinsfile.proposed Jenkinsfile

   # Commit y push
   git add Jenkinsfile docker-compose-jenkins.yml
   git commit -m "fix(ci): implementar CI completo en Jenkins con tests y validación"
   git push
   ```

3. **Configurar credenciales en Jenkins** (si Opción B):
   - `VITE_API_URL_PROD` - URL de producción
   - `VITE_TURNSTILE_SITE_KEY_PROD` - Key de producción
   - Mantener `DOCKERHUB_CREDENTIALS`

4. **Probar pipeline**:
   ```bash
   # Ejecutar manualmente en Jenkins
   # Verificar que:
   # - Se construyen imágenes :ci
   # - Se levantan servicios
   # - Se ejecutan tests
   # - Se generan reportes
   # - Se hace cleanup
   ```

### Mediano Plazo

1. **Agregar frontend tests** (actualmente placeholder)
2. **Configurar Sonarqube** para análisis de código
3. **Agregar stage de security scanning**
4. **Configurar notificaciones** (Slack/Email) en fallos
5. **Implementar deployment automático** a staging/producción

---

## Referencias

- **CLAUDE.md**: Requisitos de testing (≥90% coverage)
- **JENKINS_CI_README.md**: Documentación del entorno CI
- **docker-compose-jenkins.yml**: Configuración de servicios

---

## Conclusión

El setup actual de Jenkins **NO es un entorno de CI**, es solo un builder de imágenes.

**Recomendación**: Implementar **Opción B** (Jenkinsfile.proposed) para tener:
- ✅ Tests automatizados
- ✅ Validación de calidad
- ✅ Coverage reports
- ✅ Push seguro solo después de validación

**Riesgo actual**: Subir imágenes rotas a Docker Hub sin validación.
