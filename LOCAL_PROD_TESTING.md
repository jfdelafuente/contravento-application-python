# 🧪 Testing Production Build Locally

Este entorno te permite probar el **build de producción del frontend** (Nginx + archivos estáticos optimizados) en tu máquina local, conectado al backend de desarrollo.

## 🎯 ¿Cuándo usar esto?

- ✅ Verificar que el build de producción funciona correctamente
- ✅ Probar el proxy de Nginx `/api/*` → `backend:8000/*`
- ✅ Validar archivos estáticos optimizados (minificación, cache busting)
- ✅ Testear configuración de Nginx (security headers, gzip, caching)
- ✅ Simular comportamiento de staging/producción sin deploy

## 🚫 Cuándo NO usar esto

- ❌ **Desarrollo diario**: Usa `./deploy.sh local --with-frontend` (tiene hot reload)
- ❌ Cambios frecuentes en frontend (necesitas rebuild cada vez)
- ❌ Debugging de código React (no hay source maps en producción)

---

## 🚀 Uso Rápido

### **Linux/Mac:**
```bash
# Iniciar
./deploy-local-prod.sh start

# Después de cambios en frontend
./deploy-local-prod.sh rebuild

# Detener
./deploy-local-prod.sh stop
```

### **Windows (PowerShell):**
```powershell
# Iniciar
.\deploy-local-prod.ps1 start

# Después de cambios en frontend
.\deploy-local-prod.ps1 rebuild

# Detener
.\deploy-local-prod.ps1 stop
```

---

## 🌐 URLs de Acceso

Una vez iniciado, accede a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend (Nginx)** | http://localhost:8080 | App React con archivos estáticos |
| **Backend API** | http://localhost:8000 | API FastAPI (con hot reload) |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **MailHog** | http://localhost:8025 | Emails de desarrollo |
| **pgAdmin** | http://localhost:5050 | UI de PostgreSQL |

---

## 📋 Diferencias con `./deploy.sh local`

| Característica | `deploy.sh local` | `deploy-local-prod.sh` |
|----------------|-------------------|------------------------|
| **Frontend** | Vite dev server | Nginx + archivos estáticos |
| **Hot Reload** | ✅ Sí | ❌ No (necesita rebuild) |
| **Puerto Frontend** | 5173 | 8080 |
| **Build** | No (sirve fuente) | Sí (minificado, optimizado) |
| **Source Maps** | ✅ Sí | ❌ No (código ofuscado) |
| **Proxy API** | Vite proxy | Nginx proxy |
| **Tamaño imagen** | ~400MB | ~30MB |
| **Velocidad** | Transpila on-the-fly | Sirve archivos pre-compilados |
| **Backend** | Hot reload | Hot reload (sin cambios) |

---

## 🔧 Comandos Disponibles

### **start** (default)
Construye el frontend con Dockerfile.prod e inicia todos los servicios.

```bash
./deploy-local-prod.sh start
```

### **stop**
Detiene todos los contenedores.

```bash
./deploy-local-prod.sh stop
```

### **rebuild**
Reconstruye el frontend después de cambios en código (sin cache).

```bash
# Ejemplo: Cambias un componente React
./deploy-local-prod.sh rebuild
# Espera ~2-3 minutos para rebuild
# Accede a http://localhost:8080 para ver cambios
```

### **logs**
Muestra logs de todos los servicios en tiempo real.

```bash
./deploy-local-prod.sh logs

# Ctrl+C para salir
```

### **clean**
Elimina contenedores y volúmenes (limpieza completa).

```bash
./deploy-local-prod.sh clean
```

---

## 🔍 Verificaciones

### **1. Frontend sirve archivos estáticos**
```bash
curl -I http://localhost:8080

# Debería devolver:
# HTTP/1.1 200 OK
# Server: nginx/...
# Content-Type: text/html
```

### **2. Proxy de Nginx funciona**
```bash
# Llamada directa al backend
curl http://localhost:8000/health
# {"status":"healthy","version":"1.0.0"}

# Llamada a través del proxy de Nginx
curl http://localhost:8080/api/health
# {"status":"healthy","version":"1.0.0"}  ← MISMO RESULTADO
```

### **3. Cache headers correctos**
```bash
# Assets (JS/CSS) deben tener cache de 1 año
curl -I http://localhost:8080/assets/main.abc123.js
# Cache-Control: public, immutable
# Expires: ... (1 año)

# index.html NO debe tener cache
curl -I http://localhost:8080/index.html
# Cache-Control: no-cache, no-store, must-revalidate
```

### **4. Security headers presentes**
```bash
curl -I http://localhost:8080
# X-Frame-Options: SAMEORIGIN
# X-Content-Type-Options: nosniff
# X-XSS-Protection: 1; mode=block
```

---

## 🐛 Troubleshooting

### **Frontend no carga (404)**
```bash
# Ver logs de Nginx
docker logs contravento-frontend-local-prod

# Verificar que archivos existen en contenedor
docker exec contravento-frontend-local-prod ls -la /usr/share/nginx/html
```

### **/api/* no funciona (502 Bad Gateway)**
```bash
# Verificar que backend esté corriendo
docker ps | grep backend

# Verificar red Docker
docker network inspect contravento-network
# Backend y frontend deben estar en la misma red
```

### **Cambios en frontend no aparecen**
```bash
# Rebuild sin cache
./deploy-local-prod.sh rebuild

# Si persiste, limpia todo
./deploy-local-prod.sh clean
./deploy-local-prod.sh start
```

---

## 📦 Archivos Involucrados

- **docker-compose.local-prod.yml**: Configuración de servicios
- **deploy-local-prod.sh**: Script de deploy (Linux/Mac)
- **deploy-local-prod.ps1**: Script de deploy (Windows)
- **frontend/Dockerfile.prod**: Dockerfile de producción (2 stages)
- **frontend/nginx.conf**: Configuración de Nginx
- **.env.local**: Variables de entorno

---

## 🎓 Flujo Interno

```
1. ./deploy-local-prod.sh start
   ↓
2. docker-compose build frontend
   ├─ Stage 1: Builder (node:18-alpine)
   │  ├─ npm ci (instala dependencias)
   │  ├─ npm run build (compila a dist/)
   │  │  ├─ TypeScript → JavaScript
   │  │  ├─ Minificación (Terser)
   │  │  ├─ Tree-shaking
   │  │  └─ Hash assets (main.abc123.js)
   │  └─ Genera dist/
   │
   └─ Stage 2: Runtime (nginx:alpine)
      ├─ COPY dist/ → /usr/share/nginx/html
      ├─ COPY nginx.conf
      └─ CMD nginx
   ↓
3. docker-compose up -d
   ├─ Backend (development) en :8000
   ├─ Frontend (nginx) en :8080
   ├─ PostgreSQL en :5432
   ├─ Redis en :6379
   ├─ MailHog en :8025
   └─ pgAdmin en :5050
   ↓
4. Acceder a http://localhost:8080
   ├─ Navegador → Nginx
   ├─ Peticiones /api/* → Nginx proxy → Backend:8000
   └─ Archivos estáticos servidos desde /usr/share/nginx/html
```

---

## 🔗 Ver También

- [DOCKER_COMPOSE_ENVIRONMENTS.md](DOCKER_COMPOSE_ENVIRONMENTS.md) - Todos los entornos disponibles
- [backend/Dockerfile](backend/Dockerfile) - Dockerfile multi-stage del backend
- [frontend/Dockerfile.prod](frontend/Dockerfile.prod) - Dockerfile de producción del frontend
- [frontend/nginx.conf](frontend/nginx.conf) - Configuración de Nginx

---

## 💡 Tips

1. **Desarrollo diario**: Usa `./deploy.sh local --with-frontend` (hot reload)
2. **Testing producción**: Usa `./deploy-local-prod.sh` (este entorno)
3. **CI/CD**: Los pipelines usan Dockerfile.prod automáticamente
4. **Performance**: El build de producción es ~10x más rápido que dev server
5. **Debugging**: Si necesitas source maps, usa desarrollo (no producción)
