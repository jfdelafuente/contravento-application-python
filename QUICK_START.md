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

# Iniciar servidor
.\run-local-dev.ps1

# Resetear base de datos
.\run-local-dev.ps1 -Reset

# Ver ayuda
.\run-local-dev.ps1 -Help
```

### Linux/Mac

```bash
# Setup inicial (primera vez)
./run-local-dev.sh --setup

# Iniciar servidor
./run-local-dev.sh

# Resetear base de datos
./run-local-dev.sh --reset

# Ver ayuda
./run-local-dev.sh --help
```

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
.\deploy.ps1 local-minimal        # Iniciar
.\deploy.ps1 local-minimal logs   # Ver logs
.\deploy.ps1 local-minimal down   # Detener
.\deploy.ps1 local-minimal restart # Reiniciar

# Linux/Mac
./deploy.sh local-minimal         # Iniciar
./deploy.sh local-minimal logs    # Ver logs
./deploy.sh local-minimal down    # Detener
./deploy.sh local-minimal restart # Reiniciar
```

### Servicios incluidos

- ✅ PostgreSQL 16 (base de datos)
- ✅ Backend FastAPI (con hot reload)
- ✅ Datos de prueba (cargados automáticamente)
- ❌ Redis (deshabilitado - usa `./deploy.sh local` si lo necesitas)
- ❌ MailHog (emails se logean en consola)
- 🔧 pgAdmin (disponible pero deshabilitado - ver abajo cómo habilitarlo)

### Acceso

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
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
   - Email: `admin@contravento.local`
   - Password: `admin`

**Alternativas a pgAdmin**: DBeaver, TablePlus, psql, VS Code PostgreSQL extension

---

## 3. Docker Full (Todos los servicios)

**Ideal para**: Desarrollo de auth/email, testing completo, integración.

### Comandos

```bash
# Windows
.\deploy.ps1 local        # Iniciar
.\deploy.ps1 local logs   # Ver logs
.\deploy.ps1 local down   # Detener
.\deploy.ps1 local restart # Reiniciar

# Linux/Mac
./deploy.sh local         # Iniciar
./deploy.sh local logs    # Ver logs
./deploy.sh local down    # Detener
./deploy.sh local restart # Reiniciar
```

### Servicios incluidos

- ✅ PostgreSQL 16 (base de datos)
- ✅ Redis 7 (cache/sesiones)
- ✅ Backend FastAPI (con hot reload)
- ✅ Datos de prueba (cargados automáticamente)
- ✅ MailHog (para probar emails)
- ✅ pgAdmin 4 (interfaz web para PostgreSQL)

### Acceso

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

### Error: "Port 8000 already in use"

```bash
# Windows - Ver qué proceso usa el puerto
netstat -ano | findstr :8000

# Linux/Mac - Ver qué proceso usa el puerto
lsof -i :8000

# Matar el proceso (cambia PID por el número que te aparece)
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
```

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

**Última actualización**: 2026-01-07
