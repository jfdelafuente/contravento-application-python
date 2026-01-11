# Guía de Desarrollo Local - ContraVento

**Propósito**: Guía completa para usar los scripts `run-local-dev.sh` (Linux/Mac) y `run-local-dev.ps1` (Windows) para desarrollo local sin Docker.

**Audiencia**: Desarrolladores que trabajan en ContraVento

---

## Índice

1. [Descripción General](#descripción-general)
2. [Requisitos Previos](#requisitos-previos)
3. [Primera Vez: Configuración Inicial](#primera-vez-configuración-inicial)
4. [Uso Diario](#uso-diario)
5. [Todas las Opciones](#todas-las-opciones)
6. [Solución de Problemas](#solución-de-problemas)
7. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Descripción General

Los scripts `run-local-dev.*` permiten ejecutar ContraVento en modo desarrollo local usando SQLite (sin Docker). Son la forma **más rápida** de desarrollar: arrancan en menos de 30 segundos.

### ¿Cuándo usar cada modo?

| Modo | Comando | Cuándo usarlo |
|------|---------|---------------|
| **Backend solo** | `./run-local-dev.sh` | Trabajas solo en el backend (APIs, modelos, lógica) |
| **Backend + Frontend** | `./run-local-dev.sh --with-frontend` | Desarrollas features end-to-end o trabajas en el frontend |
| **Setup inicial** | `./run-local-dev.sh --setup` | Primera vez o después de cambios en dependencias |
| **Reset DB** | `./run-local-dev.sh --reset` | Base de datos corrupta o quieres datos limpios |

---

## Requisitos Previos

### Para Backend (Siempre Necesario)

✅ **Python 3.12+**
```bash
python --version  # Debe mostrar 3.12 o superior
```

✅ **Poetry** (gestor de dependencias Python)
```bash
poetry --version  # Si no lo tienes: pip install poetry
```

### Para Frontend (Solo con --with-frontend)

✅ **Node.js 18+**
```bash
node --version  # Debe mostrar v18.x o superior
```

✅ **npm** (viene con Node.js)
```bash
npm --version  # Debe mostrar 9.x o superior
```

---

## Primera Vez: Configuración Inicial

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/contravento-application-python.git
cd contravento-application-python
```

### Paso 2: Ejecutar Setup

**Linux/Mac**:
```bash
./run-local-dev.sh --setup
```

**Windows PowerShell**:
```powershell
.\run-local-dev.ps1 -Setup
```

### ¿Qué hace el setup?

1. **Crea `.env`** desde `.env.dev.example`
2. **Genera SECRET_KEY** automáticamente (para JWT tokens)
3. **Instala dependencias** con `poetry install`
4. **Crea base de datos** SQLite con migraciones
5. **Crea usuarios de prueba**:
   - Admin: `admin` / `AdminPass123!`
   - Usuario: `testuser` / `TestPass123!`
6. **Carga datos semilla**: achievements, cycling types

**Tiempo estimado**: 2-3 minutos la primera vez

### Paso 3: Verificar que Funciona

**Linux/Mac**:
```bash
./run-local-dev.sh
```

**Windows PowerShell**:
```powershell
.\run-local-dev.ps1
```

Deberías ver:
```
✅ Starting backend at http://localhost:8000
ℹ️  API Docs: http://localhost:8000/docs
ℹ️  Press Ctrl+C to stop
```

Abre http://localhost:8000/docs y verifica que la documentación de la API carga correctamente.

---

## Uso Diario

### Escenario 1: Trabajando Solo en el Backend

**Ejemplo**: Estás implementando un nuevo endpoint o arreglando lógica de negocio.

**Comando**:
```bash
# Linux/Mac
./run-local-dev.sh

# Windows
.\run-local-dev.ps1
```

**Qué se inicia**:
- Backend (FastAPI) en http://localhost:8000
- Hot reload activado (cambios en Python recargan automáticamente)

**Flujo de trabajo**:
1. Edita archivos en `backend/src/`
2. Guarda el archivo
3. El servidor se recarga automáticamente
4. Prueba en http://localhost:8000/docs

**Presiona Ctrl+C para detener**

---

### Escenario 2: Trabajando con Frontend y Backend

**Ejemplo**: Estás desarrollando una nueva feature que requiere cambios en frontend y backend.

**Comando**:
```bash
# Linux/Mac
./run-local-dev.sh --with-frontend

# Windows
.\run-local-dev.ps1 -WithFrontend
```

**Qué se inicia**:
- Backend (FastAPI) en http://localhost:8000
- Frontend (Vite) en http://localhost:5173 (puerto por defecto de Vite)
- Hot Module Replacement (HMR) en frontend
- Hot reload en backend

**¿Por qué puerto 5173?**

El puerto 5173 es el puerto por defecto de Vite (el servidor de desarrollo del frontend). Este puerto está configurado en `frontend/vite.config.ts`:

```typescript
server: {
  port: 5173, // Vite default port
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // Redirige llamadas API al backend
      changeOrigin: true,
    }
  }
}
```

Cuando visitas <http://localhost:5173> en el navegador, el frontend Vite actúa como proxy: todas las peticiones a `/api/*` se redirigen automáticamente al backend en puerto 8000. Esto elimina problemas de CORS durante el desarrollo.

**Configuración Frontend (Primera vez)**:

El frontend ya viene con `.env.development` configurado para desarrollo local:

```env
VITE_API_URL=http://localhost:8000
VITE_TURNSTILE_SITE_KEY=1x00000000000000000000AA  # Test key
VITE_ENV=development
VITE_DEBUG=true
```

✅ **No necesitas crear ni modificar nada** - funciona out-of-the-box.

**Flujo de trabajo**:

1. Edita archivos en `backend/src/` o `frontend/src/`
2. Guarda el archivo
3. **Frontend**: El navegador actualiza en <2 segundos sin recargar la página
4. **Backend**: El servidor se recarga automáticamente
5. Prueba en http://localhost:5173

**Primera vez con frontend**:

- El script detecta si faltan dependencias y ejecuta `npm install` automáticamente
- `.env.development` ya está configurado (no requiere acción)

**Presiona Ctrl+C para detener ambos servicios**

---

### Escenario 3: Resetear la Base de Datos

**Ejemplo**: Los datos están corruptos, quieres empezar limpio, o cambiaste el esquema manualmente.

**Comando**:
```bash
# Linux/Mac
./run-local-dev.sh --reset

# Windows
.\run-local-dev.ps1 -Reset
```

**Qué hace**:
1. Pregunta confirmación (⚠️ borra todos los datos)
2. Elimina `backend/contravento_dev.db`
3. Ejecuta migraciones desde cero
4. Recrea usuarios de prueba
5. Recarga datos semilla

**Cuándo usarlo**:
- Después de crear nuevas migraciones Alembic
- Base de datos corrupta
- Quieres datos limpios para testing
- Cambiaste el esquema manualmente (no recomendado)

---

## Todas las Opciones

### Sintaxis Completa

**Linux/Mac (Bash)**:
```bash
./run-local-dev.sh [comando] [opciones]
```

**Windows (PowerShell)**:
```powershell
.\run-local-dev.ps1 [comando] [opciones]
```

### Comandos Disponibles

| Comando | Bash | PowerShell | Descripción |
|---------|------|------------|-------------|
| **(ninguno)** | `./run-local-dev.sh` | `.\run-local-dev.ps1` | Inicia solo backend |
| **--with-frontend** | `./run-local-dev.sh --with-frontend` | `.\run-local-dev.ps1 -WithFrontend` | Inicia backend + frontend |
| **--setup** | `./run-local-dev.sh --setup` | `.\run-local-dev.ps1 -Setup` | Configuración inicial |
| **--reset** | `./run-local-dev.sh --reset` | `.\run-local-dev.ps1 -Reset` | Resetea base de datos |
| **--help** | `./run-local-dev.sh --help` | `.\run-local-dev.ps1 -Help` | Muestra ayuda |

### Ejemplos de Uso

**1. Setup inicial (solo primera vez)**:
```bash
./run-local-dev.sh --setup
```

**2. Desarrollo backend** (uso más común):
```bash
./run-local-dev.sh
```

**3. Desarrollo full-stack**:
```bash
./run-local-dev.sh --with-frontend
```

**4. Resetear datos**:
```bash
./run-local-dev.sh --reset
```

**5. Ver ayuda**:
```bash
./run-local-dev.sh --help
```

---

## Solución de Problemas

### Error: "Port 8000 is already in use"

**Problema**: Otro proceso está usando el puerto 8000 (backend).

**Solución Linux/Mac**:
```bash
# Encuentra el proceso
lsof -ti:8000

# Mata el proceso
lsof -ti:8000 | xargs kill -9
```

**Solución Windows**:
```powershell
# Encuentra y mata el proceso
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

---

### Error: "Port 5173 is already in use"

**Problema**: Otro proceso está usando el puerto 5173 (frontend).

**Solución Linux/Mac**:
```bash
lsof -ti:5173 | xargs kill -9
```

**Solución Windows**:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process
```

---

### Error: "Poetry not found"

**Problema**: Poetry no está instalado.

**Solución**:
```bash
pip install poetry

# O con pipx (recomendado)
pipx install poetry
```

---

### Error: "Node.js not found" (con --with-frontend)

**Problema**: Node.js no está instalado.

**Solución**:
1. Descarga Node.js 18+ desde https://nodejs.org/
2. Instala el paquete
3. Verifica: `node --version`

---

### Error: ".env not found"

**Problema**: No has ejecutado el setup inicial.

**Solución**:
```bash
./run-local-dev.sh --setup
```

---

### Error: "Database migration failed"

**Problema**: Las migraciones de Alembic tienen conflictos.

**Solución 1 - Resetear DB**:
```bash
./run-local-dev.sh --reset
```

**Solución 2 - Verificar migraciones**:
```bash
cd backend
poetry run alembic history  # Ver historial
poetry run alembic current  # Ver versión actual
poetry run alembic upgrade head  # Aplicar migraciones pendientes
```

---

### Error: "npm install failed" (frontend)

**Problema**: Dependencias de Node.js tienen conflictos.

**Solución**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..
```

---

### El frontend no recarga automáticamente (HMR no funciona)

**Problema**: Vite HMR no está funcionando.

**Solución 1 - Verificar puerto**:
```bash
# Debe mostrar Vite escuchando en 5173
lsof -i:5173
```

**Solución 2 - Limpiar cache**:
```bash
cd frontend
rm -rf node_modules/.vite
npm run dev
```

**Solución 3 - Verificar navegador**:
- Abre la consola del navegador (F12)
- Busca mensajes de error de WebSocket
- Recarga la página manualmente (Ctrl+R)

---

### Backend no recarga automáticamente

**Problema**: uvicorn --reload no está funcionando.

**Solución 1 - Verificar que el proceso está corriendo**:
```bash
# Linux/Mac
ps aux | grep uvicorn

# Windows
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

**Solución 2 - Reiniciar manualmente**:
```bash
# Detén el script (Ctrl+C)
./run-local-dev.sh
```

---

### CORS errors en el navegador (con --with-frontend)

**Problema**: El frontend no puede comunicarse con el backend.

**Causa**: Vite proxy no está configurado correctamente.

**Solución**:
1. Verifica que el frontend está en http://localhost:5173 (no otro puerto)
2. Verifica que el backend está en http://localhost:8000
3. Revisa `frontend/vite.config.ts` - debe tener proxy configurado

**Código correcto en vite.config.ts**:
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
  }
}
```

---

## Preguntas Frecuentes

### ¿Cuándo debo usar --setup?

- **Primera vez** que clonas el repositorio
- Después de **cambios importantes en dependencias** (nuevo `pyproject.toml` o `package.json`)
- Si el `.env` fue borrado o está corrupto
- Después de hacer `git pull` con nuevas migraciones

### ¿Cuándo debo usar --reset?

- Base de datos **corrupta** o con datos inconsistentes
- Después de **crear nuevas migraciones** Alembic (para probarlas desde cero)
- Quieres **datos limpios** para testing o demo
- Errores de **foreign key constraints** o datos huérfanos

### ¿Puedo ejecutar frontend sin backend?

No con estos scripts. El frontend depende del backend para autenticación y datos.

Si solo quieres ver el frontend estático:
```bash
cd frontend
npm run dev
```
Pero las llamadas a la API fallarán.

### ¿Qué diferencia hay con Docker?

| Característica | run-local-dev | Docker (local-minimal/local) |
|---------------|---------------|------------------------------|
| **Startup** | <30 segundos | 60-90 segundos |
| **Base de datos** | SQLite (archivo local) | PostgreSQL (contenedor) |
| **Redis** | No | Sí (solo local-full) |
| **MailHog** | No | Sí (solo local-full) |
| **Aislamiento** | Comparte entorno del OS | Aislado en contenedores |
| **Uso recomendado** | Desarrollo diario | Testing pre-staging |

**Regla general**: Usa `run-local-dev` para desarrollo diario, Docker para testing de integración.

### ¿Los cambios en código se guardan automáticamente?

**Backend**: Sí, con uvicorn `--reload`. Guarda un archivo `.py` y el servidor se recarga.

**Frontend**: Sí, con Vite HMR. Guarda un archivo `.tsx/.css` y el navegador actualiza en <2 segundos **sin recargar la página**.

### ¿Cómo detengo los servicios?

Presiona **Ctrl+C** en la terminal donde está corriendo el script.

El script detecta la señal y hace cleanup automático:
- Mata el proceso backend
- Mata el proceso frontend (si está corriendo)
- Muestra mensaje de confirmación

### ¿Puedo ejecutar múltiples instancias?

**No** en los puertos por defecto (8000 y 5173).

Si necesitas múltiples instancias (por ejemplo, para testing):
1. Modifica los puertos en el código
2. O usa Docker con diferentes perfiles

### ¿Qué datos se crean con --setup?

**Usuarios**:
- Admin: `admin` / `admin@contravento.com` / `AdminPass123!`
- Usuario: `testuser` / `test@example.com` / `TestPass123!`

**Datos semilla**:
- Achievements (logros de ciclismo)
- Cycling types (tipos de ciclismo: carretera, MTB, gravel, etc.)

### ¿Dónde está la base de datos SQLite?

```
backend/contravento_dev.db
```

Es un archivo binario. Puedes inspeccionarlo con:
```bash
sqlite3 backend/contravento_dev.db
sqlite> .tables
sqlite> SELECT * FROM users;
sqlite> .quit
```

O con herramientas GUI como [DB Browser for SQLite](https://sqlitebrowser.org/).

### ¿Qué archivos NO debo commitear?

❌ **NUNCA** commitear:
- `backend/contravento_dev.db` (base de datos local)
- `backend/.env` (credenciales locales)
- `frontend/.env.staging` (credenciales staging)
- `frontend/.env.production` (credenciales producción)
- `frontend/node_modules/` (dependencias)
- `backend/__pycache__/` (cache Python)

✅ **SÍ** commitear:
- `backend/.env.dev.example` (template)
- `frontend/.env.example` (template)
- `frontend/.env.staging.example` (template)
- `frontend/.env.production.example` (template)

### ¿Cómo actualizo dependencias?

**Backend (Poetry)**:
```bash
cd backend
poetry update  # Actualiza todas las dependencias
poetry show --outdated  # Ver qué está desactualizado
```

**Frontend (npm)**:
```bash
cd frontend
npm update  # Actualiza dependencias
npm outdated  # Ver qué está desactualizado
```

Después de actualizar, ejecuta `--setup` de nuevo:
```bash
./run-local-dev.sh --setup
```

---

## Resumen de Comandos Rápidos

### Uso Diario (90% de las veces)

```bash
# Backend solo
./run-local-dev.sh

# Backend + Frontend
./run-local-dev.sh --with-frontend
```

### Primera Vez o Después de git pull con Cambios

```bash
./run-local-dev.sh --setup
```

### Datos Corruptos o Quieres Empezar Limpio

```bash
./run-local-dev.sh --reset
```

### Ayuda

```bash
./run-local-dev.sh --help
```

---

## Siguientes Pasos

- **Desarrollo con Docker**: Ver [QUICK_START.md](../QUICK_START.md) secciones Docker Minimal y Docker Full
- **Deployment**: Ver [backend/docs/DEPLOYMENT.md](../backend/docs/DEPLOYMENT.md)
- **Testing**: Ver [frontend/TESTING_GUIDE.md](../frontend/TESTING_GUIDE.md)
- **Estructura del Proyecto**: Ver [CLAUDE.md](../CLAUDE.md)

---

**¿Preguntas?** Abre un issue en GitHub o consulta con el equipo en el canal de desarrollo.
