# Docker Compose Preproduction Environment

Este proyecto usa **docker-compose.preproduction.yml** para validación pre-producción local.

---

## 📊 Características

| Aspecto | `docker-compose.preproduction.yml` |
|---------|-----------------------------------|
| **Propósito** | Validación pre-producción local |
| **Frontend** | Docker Hub (Dockerfile.prod) |
| **Backend** | Docker Hub (latest) |
| **Variables VITE_*** | Build-time (inmutables) |
| **Hot Reload** | ❌ No |
| **Build Required** | ❌ No (Docker Hub) |
| **Tamaño** | ~50 MB |
| **Usado Por** | Validación manual/Jenkins |
| **Puerto Frontend** | 5173:80 (mapeo) |
| **Container Names** | `*-jenkins` |
| **Network Name** | `jenkins-network` |
| **Volumes** | `*_jenkins` |

---

## docker-compose.preproduction.yml

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

---

## 🔄 Flujo de Trabajo

```
   ┌─────────────────────┐
   │  GitHub Actions     │
   │  1. Tests           │
   │  2. Build images    │
   │  3. Push Docker Hub │
   └────────┬────────────┘
            │
            v
┌──────────────────────────┐
│  Preproducción (Jenkins) │
│  - Docker Hub images     │
│  - Validate before prod  │
│  - Manual testing        │
└────────┬─────────────────┘
         │
         v
   ┌──────────────┐
   │  PRODUCCIÓN  │
   └──────────────┘
```

**Nota**: Las imágenes se construyen en GitHub Actions y se descargan desde Docker Hub para validación pre-producción.

---

## 🎯 Uso

**¿Quieres validar localmente antes de deploy a producción?**

- ✅ Usa `docker-compose.preproduction.yml`

**Comandos**:

```bash
# Iniciar preproducción
docker-compose -f docker-compose.preproduction.yml up -d

# Ver logs
docker-compose -f docker-compose.preproduction.yml logs -f

# Detener
docker-compose -f docker-compose.preproduction.yml down

# Limpiar todo (incluyendo volúmenes)
docker-compose -f docker-compose.preproduction.yml down -v
```

---

## 📚 Documentación Adicional

- [DOCKER_COMPOSE_GUIDE.md](DOCKER_COMPOSE_GUIDE.md) - Guía detallada de comandos y troubleshooting
- [CLAUDE.md](CLAUDE.md) - Arquitectura general del proyecto
- [.github/workflows/](.github/workflows/) - GitHub Actions workflows

---

## ⚠️ Notas Importantes

### Sobre Variables VITE_*

**Variables hardcodeadas durante el BUILD**:

```bash
# Variables embebidas en tiempo de compilación
# No se pueden cambiar en runtime
# Definidas en GitHub Actions al construir la imagen
```

Las variables VITE_* son inmutables porque se embeben durante el build de producción.
Para cambiarlas, debes:

1. Modificar las variables en GitHub Actions secrets
2. Ejecutar el build/push nuevamente
3. Descargar la nueva imagen con `docker-compose pull`

### Sobre Imágenes

**docker-compose.preproduction.yml**:

- Frontend: Descarga de Docker Hub `jfdelafuente/contravento-frontend:latest` (Dockerfile.prod)
- Backend: Descarga de Docker Hub `jfdelafuente/contravento-backend:latest`
- Naming: `*-jenkins`, `jenkins-network`, `*_jenkins`

### Acceso

Una vez iniciado el entorno de preproducción:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (admin@example.com / jenkins_admin)
- **PostgreSQL**: localhost:5432 (contravento_jenkins / postgres / jenkins_test_password)

---

**Última actualización**: 2026-01-23
