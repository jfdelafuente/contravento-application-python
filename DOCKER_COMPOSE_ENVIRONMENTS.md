# Docker Compose Environments - Quick Reference

Este proyecto usa **2 archivos docker-compose** para diferentes propósitos. Aquí está la guía rápida para saber cuál usar:

---

## 📊 Comparación Rápida

| Aspecto | `docker-compose.ci.yml` | `docker-compose.preproduction.yml` |
|---------|-------------------------|-----------------------------------|
| **Propósito** | Testing local flexible | Validar imágenes de producción |
| **Frontend** | Dockerfile.dev (dev server) | Dockerfile.prod (Nginx) |
| **Variables VITE_*** | Runtime (mutables) | Build-time (inmutables) |
| **Hot Reload** | ✅ Sí | ❌ No |
| **Build Required** | ✅ Sí (local) | ❌ No (Docker Hub) |
| **Tamaño** | ~500 MB | ~50 MB |
| **Usado Por** | GitHub Actions, devs | Validación pre-deploy |
| **Puerto Frontend** | 5173 (nativo) | 5173:80 (mapeo) |

---

## 1️⃣ docker-compose.ci.yml

### **Cuándo usar**:
- ✅ Testing local con configuración flexible
- ✅ GitHub Actions workflows
- ✅ Necesitas cambiar VITE_API_URL en runtime
- ✅ Debugging con hot reload
- ✅ Desarrollo de features

### **Características**:
```yaml
frontend:
  build:
    dockerfile: Dockerfile.dev  # Dev server
  environment:
    VITE_API_URL: http://localhost:8000  # ✅ Cambiable
    VITE_ENV: ci
```

### **Comandos**:
```bash
# Iniciar (con build)
docker-compose -f docker-compose.ci.yml up -d --build

# Cambiar variables y reiniciar
VITE_API_URL=http://backend:8000 docker-compose -f docker-compose.ci.yml up -d --force-recreate frontend

# Ver logs en tiempo real
docker-compose -f docker-compose.ci.yml logs -f frontend
```

### **Pros**:
- ✅ Variables flexibles en runtime
- ✅ Hot reload para debugging
- ✅ Incluye curl para healthchecks
- ✅ Ideal para iteración rápida

### **Contras**:
- ❌ Más lento (servidor de desarrollo)
- ❌ Más pesado (~500 MB)
- ❌ NO testea la imagen de producción
- ❌ Requiere build local

---

## 2️⃣ docker-compose.preproduction.yml

### **Cuándo usar**:
- ✅ Validar imágenes antes de producción
- ✅ Testear exactamente lo que irá a producción
- ✅ Verificar que las imágenes de Docker Hub funcionan
- ✅ Simular entorno de producción localmente

### **Características**:
```yaml
frontend:
  image: jfdelafuente/contravento-frontend:latest  # Pre-construida
  # VITE_* variables ya embebidas, NO SE PUEDEN CAMBIAR
```

### **Comandos**:
```bash
# Pull de Docker Hub y desplegar
docker-compose -f docker-compose.preproduction.yml up -d

# Actualizar a última imagen
docker-compose -f docker-compose.preproduction.yml pull
docker-compose -f docker-compose.preproduction.yml up -d --force-recreate
```

### **Pros**:
- ✅ Rápido (imagen pre-construida)
- ✅ Ligero (~50 MB)
- ✅ Testeas EXACTAMENTE la imagen de producción
- ✅ Sin builds locales

### **Contras**:
- ❌ Variables VITE_* inmutables (hardcodeadas)
- ❌ Sin hot reload
- ❌ Depende de Docker Hub
- ❌ Menos flexible

---

## 🔄 Flujo de Trabajo Completo

```
┌─────────────────────────┐
│  Desarrollo Local       │
│  (docker-compose.ci.yml)│
│  - Variables flexibles  │
│  - Hot reload           │
└────────────┬────────────┘
             │
             v
   ┌─────────────────────┐
   │  GitHub Actions     │
   │  1. Tests           │
   │  2. Build images    │
   │  3. Push Docker Hub │
   └────────┬────────────┘
            │
            v
┌────────────────────────────────┐
│  Validación Preproducción      │
│  (docker-compose.preproduction)│
│  - Descargar de Docker Hub     │
│  - Validar imagen producción   │
└────────────┬───────────────────┘
             │
             v
   ┌──────────────────┐
   │   PRODUCCIÓN     │
   └──────────────────┘
```

---

## 🎯 Guía Rápida de Decisión

**Necesitas cambiar VITE_API_URL?**
- ✅ Sí → Usa `docker-compose.ci.yml`
- ❌ No → Usa `docker-compose.preproduction.yml`

**Estás desarrollando una feature?**
- ✅ Sí → Usa `docker-compose.ci.yml`

**Quieres validar antes de deploy a producción?**
- ✅ Sí → Usa `docker-compose.preproduction.yml`

**Necesitas hot reload?**
- ✅ Sí → Usa `docker-compose.ci.yml`
- ❌ No → Usa `docker-compose.preproduction.yml`

---

## 📚 Documentación Adicional

- [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md) - Guía detallada de comandos y troubleshooting
- [CLAUDE.md](CLAUDE.md) - Arquitectura general del proyecto
- [.github/workflows/](..github/workflows/) - GitHub Actions workflows

---

## ⚠️ Notas Importantes

### Sobre Variables VITE_*

**En docker-compose.ci.yml** (Dockerfile.dev):
```bash
# Variables en runtime - MUTABLES
VITE_API_URL=http://api.local:8000 docker-compose -f docker-compose.ci.yml up -d
```

**En docker-compose.preproduction.yml** (Dockerfile.prod):
```bash
# Variables hardcodeadas durante el BUILD
# No se pueden cambiar en runtime
# Definidas en GitHub Actions o Jenkins al construir la imagen
```

### Sobre Imágenes

**docker-compose.ci.yml**:
- Frontend: Se construye localmente desde `frontend/Dockerfile.dev`
- Backend: Descarga de Docker Hub (configurable con `BACKEND_IMAGE`)

**docker-compose.preproduction.yml**:
- Frontend: Descarga de Docker Hub `jfdelafuente/contravento-frontend:latest`
- Backend: Descarga de Docker Hub `jfdelafuente/contravento-backend:latest`

---

**Última actualización**: 2026-01-23
