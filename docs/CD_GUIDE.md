# Guía de CD - ContraVento

## Índice

1. [¿Qué es CD?](#qué-es-cd)
2. [Estrategia de Deployment](#estrategia-de-deployment)
3. [Ambientes de Deployment](#ambientes-de-deployment)
4. [Scripts de Deployment](#scripts-de-deployment)
5. [Proceso de Deployment](#proceso-de-deployment)
6. [Rollback y Recuperación](#rollback-y-recuperación)
7. [Monitoreo Post-Deployment](#monitoreo-post-deployment)
8. [Best Practices](#best-practices)

---

## ¿Qué es CD?

### CD en Términos Simples

**CD** son las siglas de **Continuous Deployment** (Despliegue Continuo).

#### Analogía del Mundo Real

Imagina que tienes una tienda:

**Sin CD** (Deployment Manual):
- 🏪 Cierras la tienda cada vez que quieres cambiar algo
- 📦 Cambias manualmente cada producto en el estante
- ⏰ Proceso toma horas, clientes esperan afuera
- 😰 Alto riesgo de errores al reorganizar
- 💥 Si algo sale mal, difícil revertir

**Con CD** (Deployment Automatizado):
- 🚀 Los cambios se despliegan automáticamente
- ⚡ Actualizaciones ocurren en segundos
- 👥 Clientes ni siquiera notan el cambio
- ✅ Si algo falla, se revierte automáticamente
- 😌 Proceso repetible y confiable

### Despliegue Continuo (CD)

**¿Qué hace?**
Después de que CI pasa, automáticamente:

1. **Construye la aplicación**: Crea versiones optimizadas para cada ambiente
2. **Ejecuta tests finales**: Smoke tests en staging para validar deployment
3. **Despliega a staging**: Actualiza ambiente de pruebas automáticamente
4. **Despliega a producción**: (con aprobación manual) Actualiza ambiente real

**Ejemplo en ContraVento**:

```bash
# Merge a rama 'develop'
git merge feature/user-profile

# GitHub Actions/Scripts automáticamente:
✅ Construye imágenes Docker
✅ Ejecuta smoke tests
✅ Despliega a staging.contravento.com
✅ Ejecuta tests E2E en staging
✅ Notifica al equipo

# Si staging es estable:
✅ Deploy manual a producción (con aprobación)
```

**Beneficio**: Despliegues **rápidos**, **seguros** y **confiables**.

---

## Estrategia de Deployment

ContraVento utiliza una estrategia de deployment basada en **scripts automatizados** con Docker:

### Herramientas de Deployment

- **Docker**: Contenedores para backend y frontend
- **Docker Compose**: Orquestación multi-contenedor
- **Scripts Shell**: Automatización de deployment (`deploy.sh`, `deploy.ps1`)
- **Nginx**: Servidor web para frontend y proxy reverso
- **PostgreSQL**: Base de datos en producción
- **Redis**: Cache y sesiones (opcional)

### Características Clave

- ✅ **Deployment Automatizado**: Un comando para desplegar (`./deploy.sh prod`)
- ✅ **Ambientes Aislados**: Local, Dev, Staging, Production
- ✅ **Health Checks**: Validación automática post-deployment
- ✅ **Logs Centralizados**: Docker logging con rotación
- ✅ **Backups Automáticos**: Base de datos y configuración

---

## Ambientes de Deployment

ContraVento soporta múltiples ambientes de deployment:

### 1. Local Development (SQLite)

**Propósito**: Desarrollo local rápido sin Docker

**Base de datos**: SQLite (archivo local)

**Deployment**:

```bash
# Windows
.\run-local-dev.ps1 -Setup  # Primera vez
.\run-local-dev.ps1          # Desarrollo diario

# Linux/Mac
./run-local-dev.sh --setup   # Primera vez
./run-local-dev.sh           # Desarrollo diario
```

**Acceso**:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. Local Full (Docker con PostgreSQL)

**Propósito**: Ambiente completo local con todos los servicios

**Base de datos**: PostgreSQL en contenedor

**Deployment**:

```bash
# Windows
.\deploy.ps1 local

# Linux/Mac
./deploy.sh local
```

**Acceso**:
- Backend API: http://localhost:8000
- Frontend: http://localhost:5173 (con `--with-frontend`)
- MailHog: http://localhost:8025 (email testing)
- pgAdmin: http://localhost:5050 (DB management)

### 3. Development/Integration

**Propósito**: Ambiente de integración compartido para el equipo

**Base de datos**: PostgreSQL

**Deployment**:

```bash
./deploy.sh dev
```

**Características**:
- Nginx como reverse proxy
- SMTP real (Gmail/SendGrid)
- Logs persistentes
- Monitoreo básico

### 4. Staging

**Propósito**: Replica exacta de producción para testing final

**Base de datos**: PostgreSQL (réplica de producción)

**Deployment**:

```bash
./deploy.sh staging
```

**Características**:
- SSL/TLS con certificados
- Monitoreo completo
- Logs centralizados
- Backups automáticos
- Tests E2E post-deployment

**URL**: https://staging.contravento.com

### 5. Production

**Propósito**: Ambiente de producción para usuarios finales

**Base de datos**: PostgreSQL con alta disponibilidad

**Deployment**:

```bash
# Requiere confirmación manual
./deploy.sh prod
```

**Características**:
- SSL/TLS con Let's Encrypt
- Load balancing (futuro)
- Auto-scaling (futuro)
- Monitoreo 24/7
- Backups incrementales
- Rollback automático si health checks fallan

**URL**: https://contravento.com

---

## Scripts de Deployment

### deploy.sh (Linux/Mac)

Script principal de deployment para Unix-like systems.

**Sintaxis**:

```bash
./deploy.sh <environment> [options]
```

**Ambientes disponibles**:
- `local-dev` - SQLite local (no Docker)
- `local-minimal` - PostgreSQL mínimo
- `local` - Stack completo local
- `dev` - Development/Integration
- `staging` - Staging environment
- `prod` - Production environment

**Opciones**:
- `--with-frontend` - Incluir frontend en deployment local
- `--build` - Forzar rebuild de imágenes Docker
- `--no-cache` - Build sin usar cache
- `--pull` - Pull de imágenes base antes de build

**Ejemplos**:

```bash
# Deployment local completo con frontend
./deploy.sh local --with-frontend

# Deployment a staging con rebuild
./deploy.sh staging --build

# Deployment a producción (requiere confirmación)
./deploy.sh prod
```

### deploy.ps1 (Windows PowerShell)

Script equivalente para Windows PowerShell.

**Sintaxis**:

```powershell
.\deploy.ps1 <Environment> [-WithFrontend] [-Build] [-NoCache] [-Pull]
```

**Ejemplos**:

```powershell
# Deployment local completo con frontend
.\deploy.ps1 local -WithFrontend

# Deployment a staging con rebuild
.\deploy.ps1 staging -Build

# Deployment a producción
.\deploy.ps1 prod
```

---

## Proceso de Deployment

### Pre-Deployment Checklist

Antes de cada deployment, verificar:

1. ✅ **Tests CI pasando**: Todos los workflows de GitHub Actions en verde
2. ✅ **Migrations listas**: Alembic migrations probadas localmente
3. ✅ **Variables de entorno**: `.env` actualizado para el ambiente target
4. ✅ **Backup reciente**: Base de datos respaldada (staging/prod)
5. ✅ **Changelog actualizado**: Documentar cambios importantes

### Deployment a Staging

**Paso 1: Validación Local**

```bash
# Ejecutar tests localmente
cd backend
poetry run pytest --cov=src

# Validar migrations
poetry run alembic upgrade head
```

**Paso 2: Deployment Automatizado**

```bash
# Deploy a staging
./deploy.sh staging --build

# El script automáticamente:
# 1. Valida configuración
# 2. Construye imágenes Docker
# 3. Ejecuta migrations
# 4. Inicia contenedores
# 5. Ejecuta health checks
# 6. Ejecuta smoke tests
```

**Paso 3: Validación Post-Deployment**

```bash
# Verificar servicios
docker ps

# Verificar logs
docker logs contravento-backend-staging
docker logs contravento-frontend-staging

# Ejecutar tests E2E contra staging
cd frontend
npm run test:e2e:staging
```

**Paso 4: Monitoreo**

- Revisar métricas en Grafana (futuro)
- Verificar logs en Loki (futuro)
- Monitorear errores en Sentry (futuro)

### Deployment a Production

**Requiere aprobación manual y validación adicional.**

**Paso 1: Validación en Staging**

```bash
# Staging debe estar estable por al menos 24 horas
# Ejecutar tests E2E completos
npm run test:e2e:staging

# Verificar performance
npm run test:performance:staging
```

**Paso 2: Backup de Producción**

```bash
# Backup automático antes de deployment
# El script deploy.sh crea backup automáticamente
./deploy.sh prod
```

**Paso 3: Deployment con Rollback Automático**

```bash
# Deploy con confirmación
./deploy.sh prod

# Confirmar deployment cuando se solicite
# El script realiza:
# 1. Backup de base de datos
# 2. Build de imágenes
# 3. Migrations en modo dry-run
# 4. Deployment gradual
# 5. Health checks continuos
# 6. Rollback automático si health checks fallan
```

**Paso 4: Validación Post-Deployment**

```bash
# Verificar estado de servicios
docker ps

# Verificar health endpoints
curl https://contravento.com/health

# Ejecutar smoke tests
curl https://contravento.com/api/health
```

**Paso 5: Monitoreo Intensivo (Primeras 2 horas)**

- Revisar logs en tiempo real
- Monitorear métricas de performance
- Verificar errores en Sentry
- Revisar feedback de usuarios

---

## Rollback y Recuperación

### Rollback Automático

El script `deploy.sh` incluye rollback automático si:

- Health checks fallan después de deployment
- Migrations fallan durante upgrade
- Servicios no inician correctamente

**Proceso automático**:

```bash
# Si deployment falla:
1. Detener nuevos contenedores
2. Restaurar contenedores anteriores
3. Revertir migrations (alembic downgrade)
4. Restaurar backup de base de datos (si es necesario)
5. Notificar al equipo
```

### Rollback Manual

Si es necesario hacer rollback manual:

**Opción 1: Revertir a última versión estable**

```bash
# Re-deploy última versión estable
./deploy.sh prod --tag=v1.2.3
```

**Opción 2: Rollback de Migrations**

```bash
# Conectar al contenedor
docker exec -it contravento-backend-prod bash

# Rollback migrations
poetry run alembic downgrade -1  # Revertir última migration
```

**Opción 3: Restaurar Backup de Base de Datos**

```bash
# Listar backups disponibles
ls -lh backups/prod/

# Restaurar backup
./scripts/restore-db.sh backups/prod/contravento-2024-01-15-10-30.sql
```

---

## Monitoreo Post-Deployment

### Health Checks

**Backend Health Endpoint**:

```bash
# Verificar estado de servicios
curl https://contravento.com/health

# Respuesta esperada:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "1.2.3"
}
```

**Frontend Health Check**:

```bash
# Verificar que frontend carga correctamente
curl -I https://contravento.com

# Respuesta esperada: 200 OK
```

### Logs

**Ver logs en tiempo real**:

```bash
# Backend logs
docker logs -f contravento-backend-prod

# Frontend logs (Nginx)
docker logs -f contravento-frontend-prod

# Database logs
docker logs -f contravento-db-prod
```

**Filtrar errores**:

```bash
# Errores de backend
docker logs contravento-backend-prod 2>&1 | grep ERROR

# Errores de Nginx
docker logs contravento-frontend-prod 2>&1 | grep error
```

### Métricas (Futuro)

**Herramientas planeadas**:

- **Prometheus**: Métricas de sistema y aplicación
- **Grafana**: Dashboards visuales
- **Loki**: Agregación de logs
- **Sentry**: Error tracking y alertas

---

## Best Practices

### 1. Deployments Frecuentes y Pequeños

✅ **DO**: Deploy cambios pequeños frecuentemente (diario/semanal)
❌ **DON'T**: Acumular semanas de cambios en un "big bang" deployment

**Beneficio**: Menor riesgo, más fácil identificar problemas

### 2. Validación en Staging Primero

✅ **DO**: Siempre deploy a staging antes de producción
❌ **DON'T**: Deploy directo a producción sin validación

**Beneficio**: Detectar problemas antes de afectar usuarios

### 3. Backups Antes de Deployment

✅ **DO**: Backup automático de base de datos antes de cada deployment
❌ **DON'T**: Deploy sin backup reciente

**Beneficio**: Recuperación rápida si algo sale mal

### 4. Monitoreo Post-Deployment

✅ **DO**: Monitorear intensivamente las primeras 2 horas post-deployment
❌ **DON'T**: "Deploy and forget"

**Beneficio**: Detectar problemas antes que los usuarios

### 5. Rollback Plan Siempre Listo

✅ **DO**: Tener plan de rollback documentado y probado
❌ **DON'T**: Esperar a que haya problema para pensar en rollback

**Beneficio**: Recuperación rápida ante fallos

### 6. Migrations Reversibles

✅ **DO**: Escribir migrations con `downgrade()` funcional
❌ **DON'T**: Migrations solo con `upgrade()`

**Beneficio**: Rollback completo si es necesario

### 7. Feature Flags para Cambios Grandes

✅ **DO**: Usar feature flags para funcionalidades nuevas grandes
❌ **DON'T**: Deploy de features grandes sin kill switch

**Beneficio**: Desactivar feature sin rollback completo

### 8. Deployment Windows Planificados

✅ **DO**: Deployments a producción en horarios de bajo tráfico
❌ **DON'T**: Deploy en horas pico

**Beneficio**: Menor impacto a usuarios si hay problemas

### 9. Comunicación del Equipo

✅ **DO**: Notificar al equipo antes/durante/después de deployments
❌ **DON'T**: Deployments silenciosos sin comunicación

**Beneficio**: Equipo preparado para responder a incidentes

### 10. Documentación de Deployments

✅ **DO**: Mantener log de deployments con cambios y fechas
❌ **DON'T**: Deployments sin documentación

**Beneficio**: Trazabilidad y auditoría

---

## Recursos Relacionados

### ContraVento Docs

- **CI Guide**: [docs/CI_GUIDE.md](./CI_GUIDE.md) - Guía de Continuous Integration
- **Deployment Guide**: [backend/docs/DEPLOYMENT.md](../backend/docs/DEPLOYMENT.md) - Detalles técnicos de deployment
- **Docker Guide**: [backend/docs/DOCKER.md](../backend/docs/DOCKER.md) - Configuración de contenedores
- **Database Migrations**: [backend/docs/MIGRATIONS.md](../backend/docs/MIGRATIONS.md) - Alembic migrations

### External Resources

- **Docker Documentation**: <https://docs.docker.com/>
- **Docker Compose**: <https://docs.docker.com/compose/>
- **Nginx**: <https://nginx.org/en/docs/>

---

## Resumen

### ¿Qué es CD?

**CD** = Continuous Deployment (Despliegue Continuo)

**En términos simples**:

- 🚀 Deployment **automático** después de que CI pasa
- 🔄 Proceso **repetible** y **confiable**
- ✅ **Validación automática** con health checks y smoke tests
- 🔙 **Rollback automático** si algo falla

### Ambientes de ContraVento

| Ambiente | Base de Datos | Deployment | Propósito |
|----------|---------------|------------|-----------|
| **local-dev** | SQLite | Manual (script) | Desarrollo diario |
| **local** | PostgreSQL | Docker Compose | Testing local completo |
| **dev** | PostgreSQL | Automatizado | Integración del equipo |
| **staging** | PostgreSQL | Automatizado | Validación pre-producción |
| **prod** | PostgreSQL | Manual (aprobado) | Usuarios finales |

### Beneficios

✅ **Deployments rápidos**: Minutos en lugar de horas
✅ **Menor riesgo**: Cambios pequeños y frecuentes
✅ **Rollback rápido**: Reversión automática si falla
✅ **Validación automática**: Health checks y smoke tests
✅ **Auditoría**: Log completo de deployments

### Flujo de Trabajo Típico

```text
Developer → Commit → Push → CI Pipeline
                              ↓
                        ✅ Tests pasan
                              ↓
                        🚀 Deploy a Staging
                              ↓
                        ✅ Validación manual
                              ↓
                        🚀 Deploy a Production
                              ↓
                        📊 Monitoreo
```

---

**Última actualización**: 2026-01-20

**Contacto**: Para preguntas sobre CD, revisa el [DEPLOYMENT.md](../backend/docs/DEPLOYMENT.md) o consulta este documento
