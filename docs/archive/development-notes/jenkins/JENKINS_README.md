# Jenkins - Índice de Documentación

Documentación completa para configurar y ejecutar el pipeline de Jenkins para ContraVento.

---

## 📚 Documentación Disponible

### 1. [JENKINS_GUIDE.md](JENKINS_GUIDE.md) - Guía Principal
**Guía completa del pipeline de Jenkins**

**Contenido**:
- ✅ Configuración inicial de Jenkins
- ✅ Pipeline de 6 stages (Checkout → Tests → Build → Push → Deploy → Validate)
- ✅ Resumen rápido de credenciales
- ✅ Troubleshooting del pipeline
- ✅ Mantenimiento y limpieza
- ✅ Workflow completo CI/CD

**Cuándo usar**: Lee esto primero para entender el pipeline completo.

---

### 2. [JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md) - Guía de Credenciales
**Guía especializada paso a paso para configurar credenciales**

**Contenido**:
- ✅ Instrucciones visuales paso a paso
- ✅ Diagramas de navegación en Jenkins UI
- ✅ Scripts de verificación en Groovy
- ✅ Testing dry-run del pipeline
- ✅ Configuración avanzada por entornos (Jenkins Folders)
- ✅ Troubleshooting exhaustivo de credenciales
- ✅ Security checklist completo

**Cuándo usar**: Consulta esto cuando necesites:
- Configurar credenciales por primera vez
- Crear credenciales para múltiples entornos
- Resolver problemas con credenciales
- Obtener tokens de Docker Hub o Cloudflare Turnstile

---

### 3. [Jenkinsfile](Jenkinsfile) - Pipeline Definition
**Definición del pipeline en Groovy**

**Stages**:
1. Git Checkout - Clona repositorio
2. Run Backend Tests - Ejecuta pytest
3. Build Docker Images (parallel) - Construye backend + frontend
4. Push to Docker Hub - Sube imágenes
5. Deploy to Preproduction - Despliega con docker-compose.preproduction.yml
6. Validate Deployment - Health checks

---

## 🚀 Quick Start

### Primer Setup (Configuración inicial)

1. **Instalar Jenkins** y plugins necesarios:
   - Docker Pipeline Plugin
   - Git Plugin
   - Credentials Plugin

2. **Configurar credenciales** (ver [JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md)):
   - `dockerhub_id` - Docker Hub credentials
   - `vite_api_url` - Frontend API URL
   - `vite_turnstile_site_key` - Cloudflare Turnstile key

3. **Crear Pipeline Job**:
   - Dashboard → New Item → Pipeline
   - Pipeline from SCM → Git
   - Repository: `https://github.com/jfdelafuente/contravento-application-python.git`
   - Branch: `develop`
   - Script Path: `Jenkinsfile`

4. **Ejecutar Build**:
   - Click "Build Now"
   - Monitorear en Console Output

---

## 📋 Workflows Comunes

### Workflow 1: Ejecutar Pipeline Manualmente

```bash
# En Jenkins UI
1. Ir al job "ContraVento-Pipeline"
2. Click "Build Now"
3. Monitorear progreso en Blue Ocean o Console Output
4. Al finalizar, acceder al entorno de preproducción
```

**Acceso al entorno**:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

---

### Workflow 2: Configurar Webhook de GitHub (Automático)

```bash
# En GitHub Repository Settings
1. Settings → Webhooks → Add webhook
2. Payload URL: http://[jenkins-server]/github-webhook/
3. Content type: application/json
4. Events: Just the push event
5. Active: ✓

# En Jenkins Job
1. Configure → Build Triggers
2. ✓ GitHub hook trigger for GITScm polling
3. Save
```

**Resultado**: Pipeline se ejecuta automáticamente en cada push a `develop`.

---

### Workflow 3: Actualizar Credenciales

```bash
# Escenario: Rotar Docker Hub token cada 90 días
1. Generar nuevo Access Token en Docker Hub
2. Manage Jenkins → Credentials → Global
3. Click en "dockerhub_id" → Update
4. Pegar nuevo token en campo "Password"
5. Save

# Verificar
6. Ejecutar Build Now
7. Verificar que login a Docker Hub funciona
```

Ver guía detallada en: [JENKINS_CREDENTIALS_SETUP.md#paso-2-configurar-docker-hub-credentials](JENKINS_CREDENTIALS_SETUP.md#-paso-2-configurar-docker-hub-credentials)

---

### Workflow 4: Múltiples Entornos (Staging + Production)

```bash
# Crear estructura de folders
1. Dashboard → New Item → Folder
2. Name: "staging" → OK
3. Repetir para "production"

# Configurar credenciales diferentes por folder
4. staging/ → Credentials → Add:
   - vite_api_url = "https://api-staging.contravento.com"
   - vite_turnstile_site_key = "1x00000000000000000000AA" (testing)

5. production/ → Credentials → Add:
   - vite_api_url = "https://api.contravento.com"
   - vite_turnstile_site_key = "[REAL_KEY]" (producción)

# Crear pipelines en cada folder
6. staging/ → New Item → Pipeline → Pipeline from SCM
7. production/ → New Item → Pipeline → Pipeline from SCM
```

Ver guía completa en: [JENKINS_CREDENTIALS_SETUP.md#paso-6-credentials-por-entorno-avanzado](JENKINS_CREDENTIALS_SETUP.md#-paso-6-credentials-por-entorno-avanzado)

---

## 🔧 Troubleshooting Rápido

### Error: "Credentials 'dockerhub_id' not found"

**Solución**:
```bash
1. Verificar ID exacto (case-sensitive)
2. Manage Jenkins → Credentials → Global
3. Verificar que existe "dockerhub_id"
4. Si no existe, crear según JENKINS_CREDENTIALS_SETUP.md
```

---

### Error: "Docker login failed"

**Solución**:
```bash
1. Verificar Docker Hub Access Token válido
2. Regenerar token en hub.docker.com/settings/security
3. Actualizar credential en Jenkins
```

---

### Error: "Backend tests failed"

**Solución**:
```bash
1. Ver logs del pipeline (Console Output)
2. Ejecutar tests localmente para depurar:
   cd backend
   poetry install
   poetry run pytest --cov=src -v
3. Corregir tests
4. Push y re-ejecutar pipeline
```

---

### Error: "Service not healthy"

**Solución**:
```bash
# Via helper scripts
./run-jenkins-env.sh logs       # Linux/Mac
.\run-jenkins-env.ps1 logs      # Windows

# Ver logs específicos
docker-compose -f docker-compose.preproduction.yml logs backend
docker-compose -f docker-compose.preproduction.yml logs frontend

# Reiniciar servicios
./run-jenkins-env.sh restart
```

Ver troubleshooting completo en: [JENKINS_GUIDE.md#troubleshooting](JENKINS_GUIDE.md#troubleshooting)

---

## 📂 Archivos Relacionados

### Docker Compose
- [docker-compose.preproduction.yml](docker-compose.preproduction.yml) - Entorno de preproducción
- [DOCKER_COMPOSE_ENVIRONMENTS.md](DOCKER_COMPOSE_ENVIRONMENTS.md) - Documentación de entornos
- [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md) - Guía rápida

### Helper Scripts
- [run-jenkins-env.sh](run-jenkins-env.sh) - Script Bash para Linux/Mac
- [run-jenkins-env.ps1](run-jenkins-env.ps1) - Script PowerShell para Windows

**Comandos disponibles**:
```bash
start    - Iniciar entorno de preproducción
stop     - Detener servicios
restart  - Reiniciar servicios
logs     - Ver logs
status   - Ver estado de servicios
pull     - Actualizar imágenes desde Docker Hub
clean    - Limpiar volúmenes
```

---

## 🎯 Flujo CI/CD Completo

```
Desarrollador
    │
    ├─ git push develop
    │
    v
GitHub Actions (PRIMARY)
    │
    ├─ 1. Run Tests
    ├─ 2. Build Images
    └─ 3. Push to Docker Hub
         │
         v
    Docker Hub Registry
         │
         ├─────────────────┬─────────────────┐
         v                 v                 v
    Jenkins Pipeline   GitHub Actions    Manual Pull
    (Preproduction)    (Testing)         (Local)
         │                 │                 │
         ├─ Deploy         ├─ Validate       ├─ run-jenkins-env.sh
         ├─ Validate       └─ Tests          └─ Testing local
         │
         v
    Preproduction Environment
    (http://localhost:5173)
         │
         v
    QA/Manual Testing
         │
         v
    Production Deployment
```

---

## 🔐 Security Best Practices

✅ **DO**:
- Rotar tokens cada 90 días
- Usar Access Tokens (no passwords)
- Mínimos permisos necesarios
- Credentials específicos por entorno
- Verificar logs no exponen secrets

❌ **DON'T**:
- Hardcodear secrets en Jenkinsfile
- Compartir credentials entre proyectos
- Usar testing keys en producción
- Loggear valores de credentials

---

## 📞 Soporte

**Problemas con el Pipeline**:
1. Revisar [JENKINS_GUIDE.md - Troubleshooting](JENKINS_GUIDE.md#troubleshooting)
2. Verificar logs: Console Output en Jenkins
3. Verificar servicios: `./run-jenkins-env.sh status`

**Problemas con Credenciales**:
1. Revisar [JENKINS_CREDENTIALS_SETUP.md - Troubleshooting](JENKINS_CREDENTIALS_SETUP.md#-troubleshooting)
2. Ejecutar script de verificación (Groovy)
3. Regenerar tokens si es necesario

**Problemas con Docker Compose**:
1. Revisar [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md)
2. Ver logs: `docker-compose -f docker-compose.preproduction.yml logs`
3. Reiniciar: `./run-jenkins-env.sh restart`

---

## 📚 Referencias Externas

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Hub Access Tokens](https://docs.docker.com/docker-hub/access-tokens/)
- [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/)
- [GitHub Webhooks](https://docs.github.com/en/webhooks)

---

**Última actualización**: 2026-01-23
