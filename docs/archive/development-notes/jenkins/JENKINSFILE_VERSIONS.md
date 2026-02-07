# Jenkinsfile - Versiones Disponibles

Este proyecto incluye **2 versiones** del Jenkinsfile para diferentes necesidades.

---

## 📋 Versiones Disponibles

### 1. [Jenkinsfile](Jenkinsfile) - **Versión Simplificada** ⚡ (Recomendada)

**Alcance**: Build + Push a Docker Hub

**Stages** (3):
1. ✅ **Git Checkout** - Clona repositorio
2. ✅ **Build Docker Images (parallel)** - Backend + Frontend en paralelo
3. ✅ **Push to Docker Hub** - Sube imágenes a Docker Hub

**Duración estimada**: ~5-10 minutos

**Cuándo usar**:
- ✅ Solo necesitas construir y publicar imágenes
- ✅ Quieres un pipeline rápido y simple
- ✅ Los tests se ejecutan en GitHub Actions
- ✅ El deployment se hace manualmente o con otro pipeline

**Ventajas**:
- ⚡ Rápido (menos stages)
- 🎯 Fácil de entender y mantener
- 🔄 Builds paralelos (backend + frontend simultáneos)
- 📦 Imágenes disponibles inmediatamente en Docker Hub

---

### 2. [Jenkinsfile.full](Jenkinsfile.full) - **Versión Completa** 🚀

**Alcance**: Test + Build + Push + Deploy + Validate

**Stages** (6):
1. ✅ **Git Checkout** - Clona repositorio
2. ✅ **Run Backend Tests** - Ejecuta pytest con coverage
3. ✅ **Build Docker Images (parallel)** - Backend + Frontend en paralelo
4. ✅ **Push to Docker Hub** - Sube imágenes a Docker Hub
5. ✅ **Deploy to Preproduction** - Despliega con docker-compose.preproduction.yml
6. ✅ **Validate Deployment** - Health checks automáticos

**Duración estimada**: ~15-20 minutos

**Cuándo usar**:
- ✅ Necesitas ejecutar tests antes de build
- ✅ Quieres deployment automático a preproducción
- ✅ Necesitas validación automática del deployment
- ✅ Pipeline completo de CI/CD en Jenkins

**Ventajas**:
- 🧪 Tests automáticos (pytest)
- 🚀 Deployment automático
- ✅ Validación de health checks
- 📊 Pipeline completo de CI/CD

---

## 🔄 Cómo Cambiar de Versión

### Usar Versión Simplificada (Default)

Ya está configurado. El archivo `Jenkinsfile` es la versión simplificada.

```bash
# Verificar versión actual
cat Jenkinsfile | head -n 20
# Debe decir: "ContraVento - Jenkins Pipeline (Simplified)"
```

### Cambiar a Versión Completa

```bash
# Opción 1: Renombrar archivos
mv Jenkinsfile Jenkinsfile.simple
mv Jenkinsfile.full Jenkinsfile

# Opción 2: Crear job separado en Jenkins
# En Jenkins UI:
# 1. New Item → "ContraVento-Pipeline-Full"
# 2. Pipeline from SCM
# 3. Script Path: Jenkinsfile.full
```

---

## 📊 Comparación Detallada

| Característica | Simplificada | Completa |
|----------------|--------------|----------|
| **Stages** | 3 | 6 |
| **Tests** | ❌ No | ✅ Sí (pytest) |
| **Build Paralelo** | ✅ Sí | ✅ Sí |
| **Push Docker Hub** | ✅ Sí | ✅ Sí |
| **Deploy Automático** | ❌ No | ✅ Sí |
| **Health Checks** | ❌ No | ✅ Sí |
| **Duración** | ~5-10 min | ~15-20 min |
| **Complejidad** | Baja | Alta |
| **Mantenimiento** | Fácil | Medio |

---

## 🎯 Workflow Recomendado

### Opción A: GitHub Actions + Jenkins Simplificado (Recomendado)

```
┌─────────────────────┐
│  Developer Push     │
│  (develop branch)   │
└─────────┬───────────┘
          │
          ├────────────────────────────────┐
          │                                │
          v                                v
┌─────────────────────┐      ┌────────────────────────┐
│  GitHub Actions     │      │  Jenkins (Simplificado)│
│  - Run Tests        │      │  - Build Images        │
│  - Linting          │      │  - Push Docker Hub     │
│  - Type Checking    │      └────────────────────────┘
└─────────────────────┘
          │
          v
    Tests Pass
          │
          v
┌─────────────────────┐
│  Manual Deploy      │
│  (run-jenkins-env)  │
└─────────────────────┘
```

**Ventaja**: Separación de responsabilidades (GitHub Actions = Tests, Jenkins = Build/Push)

---

### Opción B: Jenkins Completo (Todo-en-Uno)

```
┌─────────────────────┐
│  Developer Push     │
│  (develop branch)   │
└─────────┬───────────┘
          │
          v
┌─────────────────────┐
│  Jenkins (Completo) │
│  - Run Tests        │
│  - Build Images     │
│  - Push Docker Hub  │
│  - Deploy           │
│  - Validate         │
└─────────┬───────────┘
          │
          v
    ┌─────────────┐
    │ Preproducción│
    │ Ready!       │
    └──────────────┘
```

**Ventaja**: Todo en un solo pipeline, deployment automático

---

## 💡 Recomendación por Caso de Uso

### Caso 1: Equipo Pequeño, Deploys Manuales
**Usar**: `Jenkinsfile` (Simplificado)

```bash
# Tests en GitHub Actions
git push → GitHub Actions ejecuta tests

# Build/Push en Jenkins (manual o webhook)
Jenkins → Build paralelo → Push Docker Hub

# Deploy manual cuando sea necesario
./run-jenkins-env.sh pull
./run-jenkins-env.sh restart
```

---

### Caso 2: Equipo Grande, Deploys Frecuentes
**Usar**: `Jenkinsfile.full` (Completo)

```bash
# Todo automático en Jenkins
git push → Jenkins webhook → Tests → Build → Push → Deploy → Validate

# Entorno de preproducción siempre actualizado
http://localhost:5173
```

---

### Caso 3: CI en GitHub, CD en Jenkins
**Usar**: `Jenkinsfile` (Simplificado) + GitHub Actions

```bash
# GitHub Actions para CI (tests, linting, etc.)
.github/workflows/
├── backend-tests.yml
├── frontend-tests.yml
└── ci.yml

# Jenkins para CD (build + push)
Jenkinsfile (simplificado)
```

---

## 🛠️ Configuración por Versión

### Credenciales Necesarias

**Ambas versiones requieren**:
- `dockerhub_id` - Docker Hub credentials
- `vite_api_url` - Frontend API URL
- `vite_turnstile_site_key` - Cloudflare Turnstile key

Ver: [JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md)

### Software Necesario en Jenkins Server

**Versión Simplificada**:
- ✅ Docker (para builds)
- ✅ Git

**Versión Completa**:
- ✅ Docker (para builds y tests dentro de contenedores)
- ✅ Git
- ✅ curl (para health checks)

**Nota**: Python y Poetry **NO** son necesarios. Los tests se ejecutan dentro de contenedores Docker.

---

## 📝 Migrar Entre Versiones

### De Simplificada a Completa

```bash
# 1. Instalar dependencias en Jenkins server
sudo apt-get install python3 python3-pip curl
pip install poetry

# 2. Cambiar Jenkinsfile
mv Jenkinsfile Jenkinsfile.simple
mv Jenkinsfile.full Jenkinsfile

# 3. Commit y push
git add .
git commit -m "chore: cambiar a Jenkinsfile completo"
git push
```

### De Completa a Simplificada

```bash
# 1. Cambiar Jenkinsfile
mv Jenkinsfile Jenkinsfile.full
mv Jenkinsfile.simple Jenkinsfile

# 2. Commit y push
git add .
git commit -m "chore: cambiar a Jenkinsfile simplificado"
git push
```

---

## 🧪 Testing de Pipeline

### Versión Simplificada

```bash
# Test local de builds
cd backend
docker build -t test-backend -f Dockerfile .

cd ../frontend
docker build -t test-frontend -f Dockerfile.prod .
```

### Versión Completa

```bash
# Test de todos los stages
cd backend
poetry install
poetry run pytest --cov=src

docker build -t test-backend -f Dockerfile .

cd ../frontend
docker build -t test-frontend -f Dockerfile.prod .

# Test de deployment
cd ..
docker-compose -f docker-compose.preproduction.yml up -d
curl -f http://localhost:8000/health
```

---

## 📞 Soporte

**Problemas con Versión Simplificada**:
- Ver: [JENKINS_GUIDE.md - Troubleshooting](JENKINS_GUIDE.md#troubleshooting)
- Enfoque: Build y Push stages

**Problemas con Versión Completa**:
- Ver: [JENKINS_GUIDE.md - Troubleshooting](JENKINS_GUIDE.md#troubleshooting)
- Enfoque: Todos los stages (tests, build, deploy, validate)

**Credenciales**:
- Ver: [JENKINS_CREDENTIALS_SETUP.md](JENKINS_CREDENTIALS_SETUP.md)

---

## 🔄 Changelog

### Versión Simplificada (Actual)
- ✅ 3 stages (Git → Build → Push)
- ✅ Builds paralelos
- ✅ ~5-10 minutos de ejecución

### Versión Completa (Jenkinsfile.full)
- ✅ 6 stages (Git → Tests → Build → Push → Deploy → Validate)
- ✅ Tests automáticos
- ✅ Deployment automático
- ✅ ~15-20 minutos de ejecución

---

**Última actualización**: 2026-01-23
