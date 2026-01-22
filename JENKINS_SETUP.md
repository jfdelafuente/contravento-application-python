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

1. **Credential de Docker Hub configurado**:
   - ID: `dockerhub_id`
   - Tipo: Username with password
   - Username: `jfdelafuente`
   - Password: Token de Docker Hub

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

## 📊 Etapas del Pipeline

1. **Git Checkout**: Clona el repositorio (branch: develop)
2. **Build Docker Image**: Construye imagen desde `backend/Dockerfile`
3. **Login to Docker Hub**: Autenticación con credenciales
4. **Push Image to Docker Hub**: Sube imagen con tag `latest`
5. **Post-actions**: Logout de Docker Hub (siempre se ejecuta)

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

### Verificar imagen en Docker Hub:

```bash
docker pull jfdelafuente/contravento:latest
docker images | grep contravento
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

### Problema 4: Build falla en stage "Build Docker Image"
**Solución**: Verificar que `backend/Dockerfile` existe y es válido

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
