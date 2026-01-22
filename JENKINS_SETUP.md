# Jenkins Pipeline - Guía de Configuración

## ✅ Correcciones Realizadas

### 1. Renombrado de archivo
- **Antes**: `Pipeline.yml` (causaba errores de sintaxis YAML)
- **Después**: `Jenkinsfile` (sintaxis Groovy correcta)

### 2. Typo corregido
- **Antes**: `jfdelafuente/contravento:lastest`
- **Después**: `jfdelafuente/contravento:latest`

### 3. Dockerfile path corregido
- **Antes**: `docker build -t jfdelafuente/contravento:latest .` (falla - no existe Dockerfile en raíz)
- **Después**: `docker build -t jfdelafuente/contravento:latest -f backend/Dockerfile backend/`

### 4. Formateo mejorado
- Indentación consistente (4 espacios)
- Sintaxis Groovy correcta

## 📋 Requisitos Previos

### En Jenkins:

1. **Credentials configurados** (ver sección "Configuración de Credentials" más abajo):
   - `dockerhub_id` - Credenciales de Docker Hub (Username with password)
   - `vite_api_url` - URL del API backend (Secret text)
   - `vite_turnstile_site_key` - Cloudflare Turnstile Site Key (Secret text)

2. **Plugins necesarios**:
   - Docker Pipeline Plugin
   - Git Plugin
   - Credentials Plugin

### En el servidor Jenkins:

```bash
# Docker instalado y accesible
docker --version

# Git instalado
git --version
```

## 🚀 Cómo Usar

### Opción A: Pipeline desde SCM (Recomendado)

1. Crear nuevo Pipeline Job en Jenkins
2. En "Pipeline" → "Definition" → seleccionar "Pipeline script from SCM"
3. SCM: Git
4. Repository URL: `https://github.com/jfdelafuente/contravento-application-python.git`
5. Branch: `develop`
6. Script Path: `Jenkinsfile`
7. Guardar y ejecutar "Build Now"

### Opción B: Pipeline script directo

1. Crear nuevo Pipeline Job en Jenkins
2. En "Pipeline" → "Definition" → seleccionar "Pipeline script"
3. Copiar el contenido de `Jenkinsfile` en el campo de texto
4. Guardar y ejecutar "Build Now"

## 🔐 Configuración de Credentials en Jenkins

Antes de ejecutar el pipeline, debes configurar las siguientes credentials en Jenkins.

### Paso 1: Acceder a Credentials

1. Ir a Jenkins Dashboard
2. Click en "Manage Jenkins"
3. Click en "Manage Credentials"
4. Seleccionar el dominio "(global)" o crear uno específico
5. Click en "Add Credentials"

### Paso 2: Configurar Docker Hub Credentials

**Credential 1: dockerhub_id**

```text
Kind: Username with password
Scope: Global
Username: jfdelafuente
Password: [Tu Docker Hub Access Token]
ID: dockerhub_id
Description: Docker Hub credentials for pushing images
```

**Cómo obtener Docker Hub Access Token:**

1. Login en [hub.docker.com](https://hub.docker.com)
2. Ir a Account Settings → Security
3. Click "New Access Token"
4. Name: `jenkins-pipeline`
5. Access permissions: Read, Write, Delete
6. Copiar el token generado (solo se muestra una vez)

### Paso 3: Configurar Frontend Environment Variables

**Credential 2: vite_api_url**

```text
Kind: Secret text
Scope: Global
Secret: https://api.contravento.com
ID: vite_api_url
Description: Frontend API URL for production builds
```

**Valores por entorno:**

- **Development**: `http://localhost:8000`
- **Staging**: `https://api-staging.contravento.com`
- **Production**: `https://api.contravento.com`

**Credential 3: vite_turnstile_site_key**

```text
Kind: Secret text
Scope: Global
Secret: [Tu Cloudflare Turnstile Site Key]
ID: vite_turnstile_site_key
Description: Cloudflare Turnstile site key for CAPTCHA
```

**Cómo obtener Cloudflare Turnstile Site Key:**

1. Login en [dash.cloudflare.com](https://dash.cloudflare.com)
2. Ir a "Turnstile"
3. Seleccionar tu sitio o crear uno nuevo
4. Copiar el "Site Key" (clave pública)

**Nota**: Para testing/staging puedes usar: `1x00000000000000000000AA` (testing key que auto-pasa)

### Paso 4: Verificar Credentials

Ejecutar este script en Jenkins Script Console (Manage Jenkins → Script Console):

```groovy
import com.cloudbees.plugins.credentials.CredentialsProvider
import jenkins.model.Jenkins

def creds = CredentialsProvider.lookupCredentials(
    com.cloudbees.plugins.credentials.common.StandardCredentials.class,
    Jenkins.instance,
    null,
    null
)

println "=== Configured Credentials ==="
creds.each { c ->
    println "ID: ${c.id} | Description: ${c.description ?: 'N/A'}"
}
```

**Expected output:**

```text
=== Configured Credentials ===
ID: dockerhub_id | Description: Docker Hub credentials for pushing images
ID: vite_api_url | Description: Frontend API URL for production builds
ID: vite_turnstile_site_key | Description: Cloudflare Turnstile site key for CAPTCHA
```

### Paso 5: Uso en el Pipeline

El Jenkinsfile usa estas credentials automáticamente:

```groovy
environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub_id')
    VITE_API_URL = credentials('vite_api_url')
    VITE_TURNSTILE_SITE_KEY = credentials('vite_turnstile_site_key')
}
```

**Características de seguridad:**

- ✅ Credentials nunca aparecen en logs (Jenkins las enmascara automáticamente)
- ✅ Solo accesibles durante la ejecución del pipeline
- ✅ Pueden tener diferentes valores por entorno (usando folders)
- ✅ Soportan rotación sin cambiar el Jenkinsfile

### Paso 6: Credentials por Entorno (Opcional)

Para tener diferentes valores por entorno, usa **Jenkins Folders**:

1. Crear folders: `staging/`, `production/`
2. Configurar credentials con mismo ID pero diferentes valores en cada folder
3. Los pipelines heredan las credentials del folder padre

**Ejemplo estructura:**

```text
Jenkins
├── staging/
│   └── Credentials
│       ├── vite_api_url = "https://api-staging.contravento.com"
│       └── vite_turnstile_site_key = "1x00000000000000000000AA"
└── production/
    └── Credentials
        ├── vite_api_url = "https://api.contravento.com"
        └── vite_turnstile_site_key = "YOUR_PRODUCTION_KEY"
```

## 📊 Etapas del Pipeline

1. **Git Checkout**: Clona el repositorio (branch: develop)
2. **Build Backend Docker Image**: Construye imagen backend desde `backend/Dockerfile`
3. **Build Frontend Docker Image**: Construye imagen frontend desde `frontend/Dockerfile.prod`
4. **Login to Docker Hub**: Autenticación con credenciales
5. **Push Backend Image to Docker Hub**: Sube imagen backend con tag `latest`
6. **Push Frontend Image to Docker Hub**: Sube imagen frontend con tag `latest`
7. **Post-actions**: Logout de Docker Hub (siempre se ejecuta)

## 🔍 Verificar Ejecución

### Logs esperados:

```
[Pipeline] stage (Git Checkout)
✓ Git Checkout Completed

[Pipeline] stage (Build Docker Image)
✓ Build Image Completed

[Pipeline] stage (Login to Docker Hub)
✓ Login Completed

[Pipeline] stage (Push Image to Docker Hub)
✓ Push Image Completed

[Pipeline] post
✓ Logout completed
```

### Verificar imágenes en Docker Hub:

```bash
# Pull backend image
docker pull jfdelafuente/contravento-backend:latest

# Pull frontend image
docker pull jfdelafuente/contravento-frontend:latest

# List images
docker images | grep contravento
```

### Ejecutar contenedores:

```bash
# Run backend (requires PostgreSQL)
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e SECRET_KEY="your-secret-key" \
  jfdelafuente/contravento-backend:latest

# Run frontend (Nginx on port 80)
docker run -d -p 80:80 jfdelafuente/contravento-frontend:latest
```

## ⚠️ Problemas Conocidos y Soluciones

### Problema 1: "Credential not found"
**Solución**: Crear credential con ID exacto `dockerhub_id`

### Problema 2: "docker: command not found"
**Solución**: Instalar Docker en el agente Jenkins o usar agente con Docker

### Problema 3: "permission denied while trying to connect to Docker"
**Solución**: Añadir usuario Jenkins al grupo docker:
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Problema 4: Build falla en stage "Build Backend Docker Image"
**Solución**: Verificar que `backend/Dockerfile` existe y es válido

### Problema 5: Frontend build falla - "VITE_API_URL not set"
**Causa**: Credentials no configurados en Jenkins

**Solución**: Verificar que las credentials están configuradas (ver sección "🔐 Configuración de Credentials"):

```bash
# Opción 1: Verificar en Jenkins UI
Manage Jenkins → Manage Credentials → Global → Verificar que existen:
- dockerhub_id
- vite_api_url
- vite_turnstile_site_key

# Opción 2: Verificar via Script Console
# Ver Paso 4 en "Configuración de Credentials"
```

**Solución temporal** (para testing sin credentials):

Modificar el stage 'Build Frontend Docker Image' en Jenkinsfile con valores hardcodeados:

```groovy
sh '''
    docker build -t jfdelafuente/contravento-frontend:latest \
      --build-arg VITE_API_URL=https://api.contravento.com \
      --build-arg VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA \
      -f frontend/Dockerfile.prod frontend/
'''
```

**Nota**: Esto NO es recomendado para producción (secrets en código)

## 🔄 Próximas Mejoras Recomendadas

### Mejoras de Producción (Pendientes):

1. **Multi-branch Pipeline**: Builds automáticos por branch
2. **Testing Stage**: Ejecutar pytest antes de build
3. **Security Scanning**: Trivy/Snyk para vulnerabilidades
4. **Tagging semántico**: Usar tags de versión (v1.0.0) en lugar de `latest`
5. **Notificaciones**: Slack/Email en fallos
6. **Rollback**: Capacidad de volver a versión anterior

### Ejemplo de Pipeline Completo (Futuro):

```groovy
pipeline {
    agent any

    stages {
        stage('Tests') {
            steps {
                sh 'cd backend && poetry run pytest --cov=src'
            }
        }

        stage('Security Scan') {
            steps {
                sh 'trivy image jfdelafuente/contravento:latest'
            }
        }

        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                sh 'docker-compose -f docker-compose.staging.yml up -d'
            }
        }
    }
}
```

## 📚 Documentación Relacionada

- [Jenkinsfile Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Backend Dockerfile](backend/Dockerfile)
- [Deployment Guide](backend/docs/DEPLOYMENT.md)

## 🆘 Soporte

Si encuentras problemas:

1. Revisa logs de Jenkins Console Output
2. Verifica credenciales de Docker Hub
3. Confirma que Docker daemon está corriendo
4. Consulta [NEXT_STEPS.md](NEXT_STEPS.md) para contexto del proyecto

---

**Última actualización**: 2026-01-22
**Estado**: ✅ Jenkinsfile corregido y listo para uso
