# Feature Specification: Frontend Deployment Integration

**Feature Branch**: `011-frontend-deployment`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "Integrar frontend React en los distintos entornos de despliegue (SQLite Local, Docker Minimal, Docker Full) con Vite dev server y builds de producción para staging/prod"

## User Scenarios & Testing

### User Story 1 - Desarrollo Local con Frontend y Backend (Priority: P1)

Como **desarrollador**, quiero poder ejecutar el frontend React junto con el backend FastAPI en mi entorno local para desarrollar y probar features end-to-end sin configuración compleja.

**Why this priority**: Es la experiencia más común de desarrollo diario. El 90% de los desarrolladores necesitan correr frontend + backend localmente para iterar rápidamente.

**Independent Test**: Puede ser probado ejecutando el comando de desarrollo local y verificando que ambos servicios (frontend en puerto 5173, backend en puerto 8000) están accesibles y comunicándose correctamente.

**Acceptance Scenarios**:

1. **Given** un desarrollador con Python y Node.js instalados, **When** ejecuta el script de desarrollo local (SQLite), **Then** el frontend se inicia automáticamente en http://localhost:5173 y puede comunicarse con el backend en http://localhost:8000
2. **Given** el frontend y backend corriendo localmente, **When** el desarrollador modifica un archivo TypeScript, **Then** el navegador recarga automáticamente con hot-reload (HMR)
3. **Given** el frontend y backend corriendo localmente, **When** el desarrollador hace login en la aplicación, **Then** la autenticación funciona correctamente usando cookies HttpOnly del backend

---

### User Story 2 - Desarrollo con Docker Minimal (Priority: P2)

Como **desarrollador**, quiero poder ejecutar frontend y backend en Docker con PostgreSQL para probar features que requieren compatibilidad con la base de datos de producción, sin necesidad de servicios adicionales como Redis o MailHog.

**Why this priority**: Útil para validación pre-staging de features que dependen de comportamientos específicos de PostgreSQL (UUIDs nativos, arrays, etc.)

**Independent Test**: Puede ser probado levantando Docker Minimal con `docker-compose` y verificando que frontend, backend y PostgreSQL están corriendo y comunicándose.

**Acceptance Scenarios**:

1. **Given** un desarrollador con Docker instalado, **When** ejecuta `./deploy.sh local-minimal`, **Then** los contenedores de frontend (Vite dev), backend y PostgreSQL se levantan correctamente
2. **Given** Docker Minimal corriendo, **When** el desarrollador accede a http://localhost:5173, **Then** el frontend carga correctamente y muestra datos del backend conectado a PostgreSQL
3. **Given** Docker Minimal corriendo, **When** el desarrollador detiene los contenedores con `./deploy.sh local-minimal down`, **Then** todos los servicios se detienen limpiamente

---

### User Story 3 - Desarrollo con Docker Full (Priority: P3)

Como **desarrollador**, quiero poder ejecutar frontend, backend, PostgreSQL, Redis y MailHog en Docker para probar features completas que requieren todos los servicios (autenticación con emails, cache, etc.)

**Why this priority**: Necesario solo para features específicas que requieren servicios adicionales como emails de verificación o cache distribuido.

**Independent Test**: Puede ser probado levantando Docker Full y verificando que todos los servicios están operativos y el frontend puede interactuar con features que dependen de Redis y MailHog.

**Acceptance Scenarios**:

1. **Given** un desarrollador con Docker instalado, **When** ejecuta `./deploy.sh local`, **Then** frontend, backend, PostgreSQL, Redis, MailHog y pgAdmin se levantan correctamente
2. **Given** Docker Full corriendo, **When** un usuario se registra en el frontend, **Then** el email de verificación aparece en MailHog (http://localhost:8025)
3. **Given** Docker Full corriendo, **When** el desarrollador accede a pgAdmin (http://localhost:5050), **Then** puede visualizar la base de datos PostgreSQL

---

### User Story 4 - Build de Producción para Staging/Prod (Priority: P1)

Como **DevOps/desarrollador**, quiero poder generar builds optimizados del frontend para desplegar en entornos de staging y producción, con archivos estáticos servidos eficientemente.

**Why this priority**: Crítico para deployment a entornos no-locales. Sin builds de producción, no podemos desplegar la aplicación a staging o producción.

**Independent Test**: Puede ser probado ejecutando el comando de build y verificando que se generan archivos estáticos optimizados en `frontend/dist/` que pueden ser servidos por Nginx o cualquier servidor estático.

**Acceptance Scenarios**:

1. **Given** el código fuente del frontend, **When** se ejecuta `npm run build`, **Then** se genera el directorio `frontend/dist/` con HTML, CSS, JS y assets minificados
2. **Given** el directorio `dist/` generado, **When** se sirve con Nginx o servidor estático, **Then** la aplicación carga correctamente y se comunica con el backend de staging/prod
3. **Given** el build de producción, **When** se ejecuta con variables de entorno para staging (VITE_API_URL apuntando a staging), **Then** el frontend apunta correctamente al backend de staging

---

### Edge Cases

- **¿Qué pasa si el frontend intenta conectarse al backend pero el backend no está corriendo?** El frontend debe mostrar un mensaje de error amigable como "No se puede conectar al servidor. Verifica que el backend esté corriendo."
- **¿Qué pasa si las variables de entorno VITE_* no están configuradas?** El build debe usar valores por defecto razonables (localhost:8000 para desarrollo local)
- **¿Cómo se manejan las diferencias de CORS entre desarrollo y producción?** El backend debe configurar CORS apropiadamente según el entorno (permitir localhost en dev, dominio específico en prod)
- **¿Qué pasa si el desarrollador ejecuta `npm run dev` pero el puerto 5173 ya está en uso?** Vite debe detectar el conflicto y ofrecer usar otro puerto automáticamente (5174, 5175, etc.)
- **¿Cómo se sincronizan las dependencias del frontend en Docker?** Los contenedores Docker deben ejecutar `npm install` automáticamente al construirse si `package.json` cambió

## Requirements

### Functional Requirements

- **FR-001**: El sistema DEBE proporcionar scripts para iniciar frontend y backend simultáneamente en modo desarrollo local (SQLite Local)
- **FR-002**: El sistema DEBE configurar Vite dev server con proxy inverso al backend para evitar problemas de CORS en desarrollo
- **FR-003**: El sistema DEBE proporcionar configuraciones de Docker Compose que incluyan el servicio frontend para entornos local-minimal y local (Docker Full)
- **FR-004**: El sistema DEBE generar builds de producción optimizados del frontend con minificación de CSS/JS y compresión de assets
- **FR-005**: El sistema DEBE permitir configurar la URL del backend mediante variables de entorno (VITE_API_URL) para diferentes entornos (dev, staging, prod)
- **FR-006**: El frontend en modo desarrollo DEBE soportar Hot Module Replacement (HMR) para recarga rápida sin perder estado de la aplicación
- **FR-007**: El sistema DEBE documentar claramente en QUICK_START.md los comandos para iniciar frontend en cada entorno (SQLite Local, Docker Minimal, Docker Full)
- **FR-008**: Los contenedores Docker del frontend DEBEN reconstruirse automáticamente cuando cambian dependencias (package.json o package-lock.json)
- **FR-009**: El sistema DEBE proporcionar healthchecks para el servicio frontend en Docker para verificar que Vite dev server está listo
- **FR-010**: El build de producción DEBE incluir source maps solo en staging (no en producción) para facilitar debugging

### Key Entities

- **Frontend Service**: Servicio Vite dev server que sirve la aplicación React en modo desarrollo con HMR
- **Frontend Build**: Artifacts estáticos (HTML, CSS, JS, assets) generados por `npm run build` para deployment en staging/producción
- **Environment Configuration**: Variables de entorno (VITE_API_URL, VITE_TURNSTILE_SITE_KEY, etc.) que configuran el comportamiento del frontend según el entorno

## Success Criteria

### Measurable Outcomes

- **SC-001**: Los desarrolladores pueden iniciar frontend + backend en menos de 30 segundos en modo SQLite Local (sin Docker)
- **SC-002**: Los desarrolladores pueden iniciar frontend + backend + PostgreSQL en menos de 60 segundos en modo Docker Minimal
- **SC-003**: Los cambios en archivos TypeScript/CSS se reflejan en el navegador en menos de 2 segundos gracias a HMR
- **SC-004**: El build de producción reduce el tamaño de los assets en al menos 60% comparado con archivos de desarrollo (gracias a minificación y tree-shaking)
- **SC-005**: El frontend en producción carga la página inicial en menos de 3 segundos en una conexión 3G (medido con Lighthouse)
- **SC-006**: Cero errores de CORS reportados en consola del navegador durante desarrollo local
- **SC-007**: El 100% de los desarrolladores pueden levantar el entorno completo (frontend + backend) siguiendo QUICK_START.md sin ayuda adicional
- **SC-008**: Los builds de producción son reproducibles (mismo código genera mismo hash de archivos) para facilitar cache y deployments

## Assumptions

1. **Node.js 18+**: Asumimos que los desarrolladores tienen Node.js 18 o superior instalado localmente
2. **npm vs yarn/pnpm**: Usaremos npm como gestor de paquetes por defecto (ya usado en el proyecto)
3. **Vite como build tool**: Asumimos que Vite es la herramienta de build (ya configurada en el proyecto)
4. **Nginx para producción**: Asumimos que los archivos estáticos en producción serán servidos por Nginx (patrón estándar)
5. **Dominio único**: Asumimos que frontend y backend comparten el mismo dominio en producción (evita CORS), posiblemente con subdominios (app.contravento.com y api.contravento.com)
6. **Variables de entorno en .env.local**: Asumimos que las variables VITE_* se configurarán en archivos `.env.local` para desarrollo local
7. **Docker Compose v2**: Asumimos Docker Compose v2+ (sintaxis `docker compose` no `docker-compose`)

## Dependencies

- **Feature 005 (Frontend User Profile)**: El frontend ya existe con autenticación funcional
- **Feature 008 (Travel Diary Frontend)**: El frontend incluye features de trips que deben funcionar en todos los entornos
- **Feature 009 (GPS Coordinates Frontend)**: El frontend incluye mapas con Leaflet que requieren assets estáticos
- **Feature 010 (Reverse Geocoding)**: El frontend incluye integración con API externa (Nominatim) que debe funcionar en todos los entornos
- **Backend deployment scripts**: Los scripts `deploy.sh` y `run-local-dev.sh` ya existen y deben extenderse para incluir frontend
- **QUICK_START.md**: El documento de deployment ya existe y debe actualizarse para incluir instrucciones de frontend

## Out of Scope

- **CDN configuration**: La configuración de CDN para servir assets estáticos en producción (Cloudflare, AWS CloudFront) está fuera del alcance
- **CI/CD pipelines**: La configuración de GitHub Actions o Jenkins para builds automáticos está fuera del alcance
- **Monitoring/Analytics**: La integración de herramientas de monitoreo (Sentry, Google Analytics) está fuera del alcance
- **PWA features**: Service Workers, offline mode y funcionalidades de Progressive Web App están fuera del alcance
- **Kubernetes deployment**: La configuración para Kubernetes (Helm charts, K8s manifests) está fuera del alcance
