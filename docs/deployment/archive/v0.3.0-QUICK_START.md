# ContraVento - Guía Rápida de Deploy

Guía simplificada de las diferentes formas de arrancar el proyecto para desarrollo.

---

## 📋 Tabla de Contenidos

1. [¿Qué opción elegir?](#-qué-opción-elegir-árbol-de-decisión)
2. [SQLite Local (Sin Docker)](#1-sqlite-local-sin-docker---la-más-rápida)
3. [Docker Minimal](#2-docker-minimal-postgresql--backend)
4. [Docker Full](#3-docker-full-todos-los-servicios)
5. [Comparación](#comparación-de-opciones)
6. [Comandos Útiles](#comandos-útiles)

---

## 🤔 ¿Qué opción elegir? (Árbol de decisión)

### Pregunta 1: ¿Tienes Docker instalado?

<details>
<summary><strong>❌ No tengo Docker (o no quiero usarlo)</strong></summary>

✅ **Usa: [SQLite Local](#1-sqlite-local-sin-docker---la-más-rápida)**

**Por qué:**

- ⚡ Arranque instantáneo (sin esperas)
- 🎯 Cero configuración (setup automático)
- 💻 Funciona en cualquier SO con Python
- 🔧 Perfecto para desarrollo diario

**Limitaciones:**

- Solo SQLite (no PostgreSQL)
- No puedes probar emails con MailHog
- Sin pgAdmin (usa extensiones de VS Code)

</details>

<details>
<summary><strong>✅ Sí, tengo Docker</strong></summary>

Continúa a la **Pregunta 2** 👇

</details>

### Pregunta 2: ¿Qué necesitas probar/desarrollar?

<details>
<summary><strong>🚴 Features básicas (trips, stats, profiles)</strong></summary>

✅ **Usa: [Docker Minimal](#2-docker-minimal-postgresql--backend)**

**Por qué:**

- 🐘 PostgreSQL real (igual que producción)
- ⚡ Ligero (~500 MB RAM)
- 🔄 Arranque rápido (~10s)
- ✅ Datos de prueba automáticos

**Incluye:**

- PostgreSQL 16
- Backend con hot reload
- 2 usuarios de prueba
- 9 achievements

**NO incluye:**

- Redis (no lo necesitas aún)
- MailHog (emails se logean en consola)
- pgAdmin (usa DBeaver o psql)

</details>

<details>
<summary><strong>📧 Autenticación / Emails / Cache</strong></summary>

✅ **Usa: [Docker Full](#3-docker-full-todos-los-servicios)**

**Por qué:**

- 📬 MailHog para ver emails de prueba
- 💾 Redis para cache/sesiones
- 🖥️ pgAdmin con interfaz web
- 🔍 Testing completo de integración

**Incluye TODO:**

- PostgreSQL 16
- Redis 7
- Backend con hot reload
- MailHog (ver emails en <http://localhost:8025>)
- pgAdmin (UI en <http://localhost:5050>)
- Datos de prueba automáticos

**Usa cuando:**

- Desarrollas registro/login
- Implementas reset de contraseña
- Pruebas notificaciones por email
- Necesitas cache con Redis

</details>

<details>
<summary><strong>🚀 Preparar para staging/producción</strong></summary>

✅ **Usa: Entornos específicos**

**Para staging:**

```bash
./deploy.sh dev       # Entorno de integración
./deploy.sh staging   # Pre-producción
```

**Para producción:**

```bash
./deploy.sh prod      # Producción con HA
```

Ver [DEPLOYMENT.md](backend/docs/DEPLOYMENT.md) para detalles completos.

</details>

### Resumen Rápido

| Tu situación                | Usa esto       | Comando                     |
|-----------------------------|----------------|-----------------------------|
| 💡 "Quiero empezar YA"      | SQLite Local   | `./run-local-dev.sh`        |
| 🐘 "Necesito PostgreSQL"    | Docker Minimal | `./deploy.sh local-minimal` |
| 📧 "Voy a probar emails"    | Docker Full    | `./deploy.sh local`         |
| 🎯 "Quiero ver pgAdmin"     | Docker Full    | `./deploy.sh local`         |
| 💾 "Necesito Redis"         | Docker Full    | `./deploy.sh local`         |
| 🔍 "Testing completo"       | Docker Full    | `./deploy.sh local`         |

---

## 1. SQLite Local (Sin Docker) - LA MÁS RÁPIDA ⚡

**Ideal para**: Desarrollo diario, pruebas rápidas, no requiere Docker.

### Windows

```powershell
# Setup inicial (primera vez)
.\run-local-dev.ps1 -Setup

# Iniciar servidor (backend solo)
.\run-local-dev.ps1

# Iniciar servidor con frontend React
.\run-local-dev.ps1 -WithFrontend

# Resetear base de datos
.\run-local-dev.ps1 -Reset

# Ver ayuda
.\run-local-dev.ps1 -Help
```

### Linux/Mac

```bash
# Setup inicial (primera vez)
./run-local-dev.sh --setup

# Iniciar servidor (backend solo)
./run-local-dev.sh

# Iniciar servidor con frontend React
./run-local-dev.sh --with-frontend

# Resetear base de datos
./run-local-dev.sh --reset

# Ver ayuda
./run-local-dev.sh --help
```

> **📖 Para documentación completa**: Ver [docs/LOCAL_DEV_GUIDE.md](docs/LOCAL_DEV_GUIDE.md) que incluye:
>
> - Detalles del flag `--with-frontend` y cuándo usarlo
> - Configuración de variables de entorno del frontend
> - Troubleshooting de puertos (5173, 8000)
> - Comandos para gestionar procesos backend/frontend
> - Flujo de trabajo con Hot Module Replacement (HMR)

### ¿Qué hace el setup automáticamente?

1. ✅ Copia `.env` desde `backend/.env.dev.example`
2. ✅ Instala dependencias con Poetry
3. ✅ Genera `SECRET_KEY` automáticamente
4. ✅ Ejecuta migraciones de Alembic
5. ✅ Crea usuarios de prueba (`testuser`, `maria_garcia`)
6. ✅ Carga 9 achievements predefinidos

### Acceso

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Base de datos**: `backend/contravento_dev.db` (archivo SQLite)

### Usuarios de prueba

| Usuario | Email | Password |
|---------|-------|----------|
| testuser | test@example.com | TestPass123! |
| maria_garcia | maria@example.com | SecurePass456! |

---

## 2. Docker Minimal (PostgreSQL + Backend)

**Ideal para**: Probar con PostgreSQL sin servicios extras.

### Comandos

```bash
# Windows
.\deploy.ps1 local-minimal                  # Iniciar (backend solo)
.\deploy.ps1 local-minimal -WithFrontend    # Iniciar con frontend
.\deploy.ps1 local-minimal logs             # Ver logs
.\deploy.ps1 local-minimal down             # Detener
.\deploy.ps1 local-minimal restart          # Reiniciar

# Linux/Mac
./deploy.sh local-minimal                   # Iniciar (backend solo)
./deploy.sh local-minimal --with-frontend   # Iniciar con frontend
./deploy.sh local-minimal logs              # Ver logs
./deploy.sh local-minimal down              # Detener
./deploy.sh local-minimal restart           # Reiniciar
```

### Servicios incluidos

**Backend solo** (por defecto):

- ✅ PostgreSQL 16 (base de datos)
- ✅ Backend FastAPI (con hot reload)
- ✅ Datos de prueba (cargados automáticamente)
- ❌ Redis (deshabilitado - usa `./deploy.sh local` si lo necesitas)
- ❌ MailHog (emails se logean en consola)
- 🔧 pgAdmin (disponible pero deshabilitado - ver abajo cómo habilitarlo)

**Con flag `--with-frontend`**:

- ✅ Frontend React (Vite dev server con HMR)
- ✅ Todo lo anterior

### Acceso

**Backend solo**:

- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **PostgreSQL**: localhost:5432

**Con frontend**:

- **Frontend**: <http://localhost:5173> (Vite dev server)
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>
- **PostgreSQL**: localhost:5432
  - User: `${POSTGRES_USER}` (ver `.env.local-minimal`)
  - Password: `${POSTGRES_PASSWORD}`
  - Database: `${POSTGRES_DB}`

### Usuarios de prueba (creados automáticamente)

| Usuario | Email | Password |
|---------|-------|----------|
| testuser | test@example.com | TestPass123! |
| maria_garcia | maria@example.com | SecurePass456! |

**Nota**: Al iniciar el contenedor por primera vez, se cargan automáticamente:

- 9 achievements predefinidos
- 2 usuarios de prueba verificados

### Configuración requerida

Primera vez: Edita `.env.local-minimal` y configura:
- `SECRET_KEY` (generar con: `python -c "import secrets; print(secrets.token_urlsafe(64))"`)
- `POSTGRES_PASSWORD`

### Habilitar pgAdmin (Opcional)

pgAdmin está disponible como contenedor pero deshabilitado por defecto para mantener el setup ligero. Para habilitarlo:

1. Edita `docker-compose.local-minimal.yml` (líneas 86-88)

2. Reemplaza:

   ```yaml
   pgadmin:
     deploy:
       replicas: 0
   ```

   Por:

   ```yaml
   pgadmin:
     deploy:
       replicas: 1
     ports:
       - "5050:80"
   ```

3. Reinicia:

   ```bash
   ./deploy.sh local-minimal down
   ./deploy.sh local-minimal
   ```

4. Accede a <http://localhost:5050>
   - Email: `admin@example.com` (ver `.env.local-minimal.example`)
   - Password: `admin`

**Alternativas a pgAdmin**: DBeaver, TablePlus, psql, VS Code PostgreSQL extension

---

## 3. Docker Full (Todos los servicios)

**Ideal para**: Desarrollo de auth/email, testing completo, integración.

### Comandos

```bash
# Windows
.\deploy.ps1 local                  # Iniciar (backend solo)
.\deploy.ps1 local -WithFrontend    # Iniciar con frontend
.\deploy.ps1 local logs             # Ver logs
.\deploy.ps1 local down             # Detener
.\deploy.ps1 local restart          # Reiniciar

# Linux/Mac
./deploy.sh local                   # Iniciar (backend solo)
./deploy.sh local --with-frontend   # Iniciar con frontend
./deploy.sh local logs              # Ver logs
./deploy.sh local down              # Detener
./deploy.sh local restart           # Reiniciar
```

### Servicios incluidos

**Backend (siempre):**

- ✅ PostgreSQL 16 (base de datos)
- ✅ Redis 7 (cache/sesiones)
- ✅ Backend FastAPI (con hot reload)
- ✅ Datos de prueba (cargados automáticamente)
- ✅ MailHog (para probar emails)
- ✅ pgAdmin 4 (interfaz web para PostgreSQL)

**Frontend (opcional con `--with-frontend`):**

- ✅ React + TypeScript + Vite (con hot reload)
- ✅ Configuración automática para conectar al backend

### Acceso

- **Frontend**: <http://localhost:5173> *(solo con `--with-frontend`)*
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MailHog UI**: http://localhost:8025 (ver emails de prueba)
- **pgAdmin**: http://localhost:5050
  - Email: `${PGADMIN_EMAIL}` (ver `.env.local`)
  - Password: `${PGADMIN_PASSWORD}`
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Usuarios de prueba (creados automáticamente)

Los mismos que en Docker Minimal - ver sección anterior.

### Probando funcionalidad de Email con MailHog

Docker Full incluye **MailHog**, un servidor SMTP de prueba que captura todos los emails enviados por la aplicación. Ideal para probar registro de usuarios, verificación de email, y recuperación de contraseña.

**Cómo funciona**:

1. **Inicia Docker Full** con el backend:

   ```bash
   # Windows
   .\deploy.ps1 local

   # Linux/Mac
   ./deploy.sh local
   ```

2. **Registra un nuevo usuario** desde el frontend o API:

   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "SecurePass123!"
     }'
   ```

3. **Abre MailHog UI** en tu navegador:

   - URL: <http://localhost:8025>
   - Verás el email de verificación que la aplicación "envió"
   - Click en el email para ver el token de verificación

4. **Verifica el email** usando el token recibido:

   ```bash
   curl -X POST http://localhost:8000/auth/verify-email \
     -H "Content-Type: application/json" \
     -d '{
       "email": "test@example.com",
       "token": "TOKEN_FROM_EMAIL"
     }'
   ```

**Ventajas de MailHog**:

- ✅ Sin configuración SMTP real necesaria
- ✅ Ver emails en tiempo real
- ✅ Probar templates de email
- ✅ Verificar contenido HTML y texto plano
- ✅ No se envían emails reales (seguro para testing)

### Configuración requerida

Primera vez: Edita `.env.local` y configura:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `PGADMIN_PASSWORD`

---

## Comparación de Opciones

| Característica | SQLite Local | Docker Minimal | Docker Full |
|----------------|:------------:|:--------------:|:-----------:|
| **Velocidad de inicio** | ⚡ Instantáneo | 🔄 ~10 segundos | 🔄 ~30 segundos |
| **Memoria RAM** | 💚 ~200 MB | 💛 ~500 MB | 🔶 ~1 GB |
| **Docker necesario** | ❌ No | ✅ Sí | ✅ Sí |
| **Base de datos** | SQLite | PostgreSQL | PostgreSQL |
| **Frontend React** | ✅ Opcional | ✅ Opcional | ✅ Opcional |
| **Probar emails** | ❌ Console | ❌ Console | ✅ MailHog |
| **Redis cache** | ❌ No | ❌ No | ✅ Sí |
| **UI para DB** | 🔧 Externo | 🔧 Externo | ✅ pgAdmin |
| **Hot reload** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Migraciones** | ✅ Alembic | ✅ Alembic | ✅ Alembic |

---

## Comandos Útiles

### Verificar requisitos

```bash
# Verificar Poetry (para SQLite local)
poetry --version

# Verificar Docker (para Docker minimal/full)
docker --version
docker-compose --version
```

### Ver logs

```bash
# SQLite local (ver en consola directamente)
# Los logs aparecen en la terminal donde ejecutaste el script

# Docker minimal/full
.\deploy.ps1 local-minimal logs        # Windows
./deploy.sh local-minimal logs         # Linux/Mac

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend

# Logs en tiempo real de un servicio específico
docker-compose logs -f backend
```

### Ejecutar migraciones manualmente

```bash
# SQLite local
cd backend
poetry run alembic upgrade head
cd ..

# Docker minimal/full
docker-compose exec backend poetry run alembic upgrade head
```

### Crear nueva migración

```bash
# SQLite local
cd backend
poetry run alembic revision --autogenerate -m "Descripción del cambio"
cd ..

# Docker minimal/full
docker-compose exec backend poetry run alembic revision --autogenerate -m "Descripción del cambio"
```

### Resetear base de datos

```bash
# SQLite local
.\run-local-dev.ps1 -Reset   # Windows
./run-local-dev.sh --reset   # Linux/Mac

# Docker minimal/full
docker-compose down -v       # ⚠️ ELIMINA TODOS LOS DATOS
```

### Ejecutar tests

```bash
# SQLite local
cd backend
poetry run pytest
poetry run pytest --cov=src --cov-report=html
cd ..

# Docker minimal/full
docker-compose exec backend poetry run pytest
docker-compose exec backend poetry run pytest --cov=src
```

### Conectar a PostgreSQL

```bash
# Con psql (cliente de línea de comandos)
psql -h localhost -p 5432 -U contravento_user -d contravento

# Con Docker
docker exec -it contravento-db-local psql -U contravento_user -d contravento
```

### Ver contenedores corriendo

```bash
docker ps                    # Todos los contenedores
docker-compose ps            # Contenedores del proyecto
```

### Detener todo

```bash
# Docker minimal/full
.\deploy.ps1 local-minimal down   # Windows
./deploy.sh local-minimal down    # Linux/Mac

# SQLite local
Ctrl+C (en la terminal donde corre el servidor)
```

---

## Troubleshooting

### Error: "Poetry not found"

```bash
# Instalar Poetry
pip install poetry

# O con pipx (recomendado)
pipx install poetry
```

### Error: "Port 8000 already in use" o "Port 5173 already in use"

```bash
# Windows - Ver qué proceso usa el puerto
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Linux/Mac - Ver qué proceso usa el puerto
lsof -i :8000
lsof -i :5173

# Matar el proceso (cambia PID por el número que te aparece)
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
```

> **💡 Troubleshooting detallado**: Ver [docs/LOCAL_DEV_GUIDE.md - Comandos Útiles](docs/LOCAL_DEV_GUIDE.md#comandos-útiles-para-gestión-de-procesos) para comandos específicos de gestión de procesos frontend/backend.

### Hot Reload Not Working (Docker)

**Problema**: El frontend no se actualiza automáticamente cuando cambias archivos `.tsx` o `.css` en Docker Minimal/Full.

**Causa**: Los volúmenes montados no están sincronizando correctamente los cambios.

**Solución**:

1. **Verificar que el servicio frontend está ejecutándose**:

   ```bash
   # Ver contenedores activos
   docker-compose -f docker-compose.yml -f docker-compose.local-minimal.yml ps

   # Debería mostrar "frontend" con estado "Up"
   ```

2. **Verificar volúmenes montados**:

   ```bash
   # Inspeccionar el contenedor frontend
   docker inspect contravento-frontend-dev | grep -A 10 "Mounts"

   # Deberías ver:
   # - ./frontend:/app (source code)
   # - /app/node_modules (anonymous volume)
   ```

3. **Verificar logs del frontend**:

   ```bash
   # Ver logs en tiempo real
   docker-compose -f docker-compose.yml -f docker-compose.local-minimal.yml logs -f frontend

   # Deberías ver: "VITE vX.X.X  ready in XXX ms"
   # Al guardar un archivo, debería aparecer: "hmr update /src/..."
   ```

4. **Reiniciar el servicio frontend**:

   ```bash
   # Detener y reiniciar solo el frontend
   docker-compose -f docker-compose.yml -f docker-compose.local-minimal.yml restart frontend
   ```

5. **Si persiste el problema, reconstruir el contenedor**:

   ```bash
   # Detener todo
   ./deploy.sh local-minimal down  # o .\deploy.ps1 local-minimal down

   # Eliminar volúmenes y reconstruir
   docker-compose -f docker-compose.yml -f docker-compose.local-minimal.yml down -v
   docker-compose -f docker-compose.yml -f docker-compose.local-minimal.yml build --no-cache frontend

   # Iniciar de nuevo con frontend
   ./deploy.sh local-minimal --with-frontend
   ```

**Nota para Windows**: Si usas WSL2, asegúrate de que los archivos están en el sistema de archivos de WSL, no en `/mnt/c/`. Los volúmenes montados desde Windows pueden tener problemas de sincronización.

### Error: "Docker daemon not running"

```bash
# Iniciar Docker Desktop (Windows/Mac)
# O iniciar servicio Docker (Linux)
sudo systemctl start docker
```

### Error al conectar a PostgreSQL

```bash
# Verificar que el contenedor está corriendo
docker ps | grep postgres

# Ver logs del contenedor
docker logs contravento-db-local

# Verificar credenciales en .env
cat .env.local-minimal
```

### Base de datos corrupta (SQLite)

```bash
# Eliminar base de datos y recrear
.\run-local-dev.ps1 -Reset   # Windows
./run-local-dev.sh --reset   # Linux/Mac
```

---

## Production Builds

**¿Cuándo usar?**: Cuando necesitas generar builds optimizados para staging o producción.

### Comandos de Build

```bash
# Staging build (incluye source maps para debugging)
cd frontend
npm run build:staging

# Production build (sin source maps, máxima optimización)
cd frontend
npm run build:prod
```

### ¿Qué genera el build?

El proceso de build crea un directorio `frontend/dist/` con:

1. **HTML/CSS/JS minificados**: Archivos optimizados y comprimidos
2. **Content hashes**: Nombres de archivo con hash (e.g., `index-abc123.js`) para cache busting
3. **Vendor chunks**: Librerías separadas para mejor caching:
   - `react-vendor`: React, React DOM, React Router
   - `form-vendor`: React Hook Form, Zod
   - `map-vendor`: Leaflet, React-Leaflet
4. **Source maps** (solo staging): Para debugging en staging

### Verificar el build

**1. Verificar que dist/ fue creado**:

```bash
cd frontend
ls -lh dist/

# Deberías ver:
# - index.html
# - assets/index-[hash].js
# - assets/index-[hash].css
# - assets/[vendor]-[hash].js
```

**2. Verificar tamaño de archivos**:

```bash
# Linux/Mac
du -sh dist/
du -h dist/assets/*.js | sort -h

# Windows PowerShell
Get-ChildItem dist -Recurse | Measure-Object -Property Length -Sum
Get-ChildItem dist/assets/*.js | Select-Object Name, @{Name="SizeKB";Expression={[math]::Round($_.Length/1KB,2)}} | Sort-Object SizeKB
```

**Tamaños esperados** (aproximados):

- **Total dist/**: ~800KB - 1.2MB (sin gzip)
- **index-[hash].js**: ~50-100KB (código de la app)
- **react-vendor-[hash].js**: ~150-200KB (React core)
- **form-vendor-[hash].js**: ~80-120KB (formularios)
- **map-vendor-[hash].js**: ~100-150KB (mapas)

**3. Verificar optimizaciones**:

```bash
# Verificar que archivos están minificados (no deberían tener espacios)
head -c 200 dist/assets/index-*.js

# Verificar source maps (solo en staging)
ls dist/assets/*.map   # Deberían existir en staging, no en prod
```

**4. Verificar que el build es ≥60% más pequeño** que dev:

```bash
# Comparar tamaño de node_modules vs dist
du -sh frontend/node_modules frontend/dist

# El build (dist/) debería ser al menos 60% más pequeño que node_modules
```

### Servir el build localmente con Nginx

**Usando Docker**:

```bash
# Staging
./deploy.sh staging    # Ejecuta build:staging automáticamente

# Production
./deploy.sh prod       # Ejecuta build:prod automáticamente
```

**El script de deployment**:

1. Ejecuta `npm run build:staging` o `npm run build:prod`
2. Construye la imagen Docker con Dockerfile.prod
3. Copia dist/ al contenedor Nginx
4. Sirve los archivos estáticos con Nginx

### Optimizaciones aplicadas

El build de producción incluye:

- ✅ **Minificación con Terser**: JS reducido al mínimo
- ✅ **CSS minificado**: Estilos comprimidos
- ✅ **Tree shaking**: Código no usado eliminado
- ✅ **Code splitting**: Chunks separados por vendor
- ✅ **Content hashing**: Cache busting automático
- ✅ **Gzip compression**: Nginx comprime en tiempo real
- ✅ **Cache headers**: 1 año para assets, no-cache para index.html
- ✅ **Security headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection

### Diferencias entre staging y production

| Característica | Staging | Production |
|----------------|---------|------------|
| Source maps | ✅ Incluidos | ❌ Excluidos |
| Debug mode | ❌ Disabled | ❌ Disabled |
| Minificación | ✅ Terser | ✅ Terser |
| VITE_ENV | `staging` | `production` |
| Réplicas Docker | 1 | 3 (HA) |

---

## Environment Variables Reference

### Backend Environment Variables

Las variables del backend se configuran en archivos `.env.*` dentro del directorio `backend/`:

| Variable | Desarrollo | Staging | Production | Descripción |
|----------|------------|---------|------------|-------------|
| `APP_NAME` | ContraVento-Local | ContraVento-Staging | ContraVento | Nombre de la aplicación |
| `APP_ENV` | local | staging | production | Entorno de ejecución |
| `DEBUG` | true | false | false | Modo debug (logs verbosos) |
| `LOG_LEVEL` | DEBUG | INFO | WARNING | Nivel de logging |
| `SECRET_KEY` | (generar 64 chars) | (generar 64 chars) | (generar 64 chars) | Clave secreta para JWT |
| `DATABASE_URL` | sqlite+aiosqlite:///... | postgresql+asyncpg://... | postgresql+asyncpg://... | URL de conexión a BD |
| `REDIS_URL` | N/A | redis://:password@... | redis://:password@... | URL de conexión a Redis |
| `BCRYPT_ROUNDS` | 4 | 12 | 12 | Rondas de hash bcrypt |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 15 | 15 | 15 | Duración token acceso |
| `REFRESH_TOKEN_EXPIRE_DAYS` | 30 | 30 | 30 | Duración token refresh |
| `SMTP_HOST` | localhost / mailhog | smtp.sendgrid.net | smtp.sendgrid.net | Servidor SMTP |
| `SMTP_PORT` | 1025 / 25 | 587 | 587 | Puerto SMTP |
| `SMTP_TLS` | false | true | true | Usar TLS para SMTP |
| `CORS_ORIGINS` | http://localhost:5173,... | https://staging.contravento.com | https://contravento.com | Orígenes CORS permitidos |
| `UPLOAD_MAX_SIZE_MB` | 10 | 5 | 5 | Tamaño máx. archivos |

**Generar SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Frontend Environment Variables (VITE_*)

Las variables del frontend se configuran en archivos `.env.*` dentro del directorio `frontend/`:

| Variable | Desarrollo | Staging | Production | Descripción |
|----------|------------|---------|------------|-------------|
| `VITE_API_URL` | http://localhost:8000 | https://staging.contravento.com | https://api.contravento.com | URL del backend API |
| `VITE_ENV` | development | staging | production | Entorno de ejecución |
| `VITE_DEBUG` | true | false | false | Modo debug (logs en consola) |
| `VITE_TURNSTILE_SITE_KEY` | 1x00000000000000000000AA | (clave real) | (clave real) | Clave pública Cloudflare Turnstile |

**Archivos de configuración:**
- `.env.development` - Variables por defecto para desarrollo (versionado en Git)
- `.env.staging` - Variables específicas de staging (crear manualmente)
- `.env.production` - Variables específicas de producción (crear manualmente)
- `.env.local` - Sobrescribe variables localmente (NO versionado, opcional)

**Cómo funcionan:**
- Vite carga automáticamente `.env.{mode}` según el comando ejecutado
- Variables con prefijo `VITE_*` se exponen al código frontend
- Variables sin `VITE_*` NO son accesibles desde el código (seguridad)

**Ejemplo de uso en código:**
```typescript
// Acceder a variables de entorno
const apiUrl = import.meta.env.VITE_API_URL;
const isProduction = import.meta.env.VITE_ENV === 'production';

// Verificar si variable está definida
if (!import.meta.env.VITE_TURNSTILE_SITE_KEY) {
  console.error('VITE_TURNSTILE_SITE_KEY no configurada');
}
```

**Validación de variables:**
```bash
# Ver variables cargadas durante el build
cd frontend
npm run build:staging 2>&1 | grep VITE_

# Verificar variables en el bundle
grep -r "VITE_API_URL" dist/assets/*.js
# Debería mostrar el valor configurado
```

---

## Common Commands

### Backend Commands

```bash
# Desarrollo local (SQLite)
./run-local-dev.sh --setup              # Primera vez: setup completo
./run-local-dev.sh                      # Arrancar backend
./run-local-dev.sh --reset              # Reset DB (borra datos)

# Migraciones de base de datos
cd backend
poetry run alembic upgrade head        # Aplicar migraciones
poetry run alembic revision --autogenerate -m "mensaje"  # Nueva migración
poetry run alembic downgrade -1        # Revertir última migración

# Testing
poetry run pytest                       # Todos los tests
poetry run pytest --cov=src             # Con cobertura
poetry run pytest tests/unit/ -v       # Solo tests unitarios

# Code quality
poetry run black src/ tests/            # Formatear código
poetry run ruff check src/ tests/       # Linter
poetry run mypy src/                    # Type checking

# Gestión de usuarios
poetry run python scripts/user-mgmt/create_admin.py                    # Crear admin
poetry run python scripts/user-mgmt/create_verified_user.py            # Crear usuario test
poetry run python scripts/user-mgmt/promote_to_admin.py --username X   # Promover a admin
```

### Frontend Commands

```bash
# Desarrollo
cd frontend
npm install                             # Instalar dependencias (primera vez)
npm run dev                             # Dev server standalone
npm run dev -- --host                   # Dev server accesible desde red local

# Production builds
npm run build:staging                   # Build staging (con source maps)
npm run build:prod                      # Build production (sin source maps)
npm run preview                         # Preview build localmente

# Análisis y debugging
npm run lint                            # ESLint
npm run type-check                      # TypeScript check
npm run build -- --analyze              # Analizar tamaño del bundle

# Limpieza
rm -rf dist/ node_modules/              # Limpiar archivos generados
npm install                             # Re-instalar dependencias
```

### Docker Commands

```bash
# Deployment scripts (recomendado)
./deploy.sh local                       # Docker Full
./deploy.sh local --with-frontend       # Docker Full + Frontend
./deploy.sh local-minimal               # Docker Minimal
./deploy.sh staging                     # Staging
./deploy.sh prod                        # Production
./deploy.sh <env> down                  # Apagar entorno

# Docker Compose directo (alternativa)
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.local.yml down
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f backend

# Gestión de contenedores
docker ps                               # Ver contenedores corriendo
docker logs contravento-backend-local   # Ver logs del backend
docker exec -it contravento-backend-local bash  # Entrar al contenedor
docker restart contravento-backend-local        # Reiniciar servicio
docker system prune -a                  # Limpiar imágenes/volúmenes no usados

# Database (PostgreSQL en Docker)
docker exec -it contravento-db-local psql -U contravento -d contravento
# Dentro de psql:
# \dt          - Listar tablas
# \d users     - Describir tabla users
# \q           - Salir
```

### Git Workflow Commands

```bash
# Crear nueva feature
git checkout develop
git pull origin develop
git checkout -b feature/mi-feature
# Hacer commits...
git push -u origin feature/mi-feature

# Merge a develop
git checkout develop
git merge feature/mi-feature --no-ff
git push origin develop

# Deploy a staging (desde develop)
git checkout develop
git pull origin develop
./deploy.sh staging

# Deploy a producción (desde main)
git checkout main
git merge develop --no-ff -m "Release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
./deploy.sh prod
```

### Quick Reference Table

| Tarea | Comando Rápido |
|-------|----------------|
| **Desarrollo diario** | `./run-local-dev.sh` (backend) + `npm run dev` (frontend) |
| **Reset DB local** | `./run-local-dev.sh --reset` |
| **Docker Full + Frontend** | `./deploy.sh local --with-frontend` |
| **Ver logs backend (Docker)** | `docker logs -f contravento-backend-local` |
| **Ver emails enviados** | Abrir <http://localhost:8025> (MailHog) |
| **DB UI (Docker Full)** | Abrir <http://localhost:5050> (pgAdmin) |
| **Correr tests** | `cd backend && poetry run pytest` |
| **Nueva migración** | `cd backend && poetry run alembic revision --autogenerate -m "X"` |
| **Build producción** | `cd frontend && npm run build:prod` |
| **Limpiar Docker** | `docker system prune -a` |
| **Deploy staging** | `./deploy.sh staging` |
| **Deploy producción** | `./deploy.sh prod` |

### Shortcuts (Scripts de utilidad)

**Backend:**
```bash
# Windows
cd backend
.\restart-backend.bat               # Reinicia backend (mata proceso y arranca)

# Linux/Mac
cd backend
./restart-backend.sh
```

**Frontend:**
```bash
# Windows
cd frontend
.\restart-frontend.bat              # Reinicia Vite dev server

# Linux/Mac
cd frontend
./restart-frontend.sh
```

**Accesos rápidos (alias recomendados para .bashrc / .zshrc):**
```bash
alias cv-backend="cd ~/contravento/backend && ./run-local-dev.sh"
alias cv-frontend="cd ~/contravento/frontend && npm run dev"
alias cv-test="cd ~/contravento/backend && poetry run pytest"
alias cv-docker="cd ~/contravento && ./deploy.sh local --with-frontend"
alias cv-logs="docker logs -f contravento-backend-local"
```

---

## Recomendaciones

### Para desarrollo diario
👉 Usa **SQLite Local** (Opción 1)
- Sin configuración
- Arranque instantáneo
- Suficiente para 90% del desarrollo

### Para testing con PostgreSQL
👉 Usa **Docker Minimal** (Opción 2)
- Cuando necesites probar queries específicas de PostgreSQL
- Antes de hacer deploy a staging/producción

### Para desarrollo de auth/email
👉 Usa **Docker Full** (Opción 3)
- Cuando necesites ver emails en MailHog
- Para probar features de cache con Redis
- Para usar pgAdmin como UI de base de datos

---

## Enlaces Útiles

- **Documentación completa**: [backend/docs/DEPLOYMENT.md](backend/docs/DEPLOYMENT.md)
- **CLAUDE.md**: [Guía para Claude Code](CLAUDE.md)
- **API Docs (cuando el servidor esté corriendo)**: http://localhost:8000/docs

---

**Última actualización**: 2026-01-13
