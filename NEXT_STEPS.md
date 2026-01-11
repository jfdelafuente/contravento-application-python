# ContraVento - Próximos Pasos

**Última actualización**: 2026-01-11
**Estado actual**: Feature 009 completada, listo para Feature 010

---

## Estado Actual ✅

### Feature 009: GPS Coordinates Frontend (COMPLETADA)

**Branch**: `009-gps-coordinates-frontend` → **MERGED to develop**
**Status**: ✅ Completada y mergeada
**Merge date**: 2026-01-11

**Logros**:
- ✅ Frontend UI para GPS coordinates con LocationInput component
- ✅ TripMap component con mapa interactivo (react-leaflet)
- ✅ Numbered markers y polyline route display
- ✅ Fullscreen mode para el mapa
- ✅ Error handling y retry para tiles
- ✅ Location list con indicador "Sin coordenadas GPS"
- ✅ Unit tests (TripMap.test.tsx - 601 lines)
- ✅ Integration tests para edición de coordenadas
- ✅ Testing documentation y guides

**Fases implementadas**:
1. Phase 1-3: Backend integration tests
2. Phase 4: Frontend UI (LocationInput component)
3. Phase 5: Map Visualization (TripMap component)
4. Phase 6: Edit GPS Coordinates

**Commits**: 40 commits mergeados a develop

---

## Próximos Pasos Inmediatos 🎯

### 1. Feature 010: Geocoding Reverso (SIGUIENTE)

**Branch**: `010-reverse-geocoding` (a crear)
**Base**: `develop`
**Prioridad**: Alta
**Estimación**: 3-4 días

**Objetivo**:
Permitir a los usuarios hacer click en el mapa para seleccionar ubicaciones automáticamente, utilizando reverse geocoding para obtener el nombre del lugar desde las coordenadas GPS.

**Características principales**:
- Click en mapa para agregar location con coordenadas
- Reverse geocoding API para obtener nombre del lugar
- Modo de edición del mapa en TripForm
- Drag markers para ajustar coordenadas
- Validación y feedback visual

**APIs a implementar**:
- Backend: Endpoint para reverse geocoding (Nominatim OSM API)
- Frontend: Hook `useMapClick` para captura de coordenadas
- Frontend: Modal de confirmación para lugares seleccionados

**Comandos para empezar**:
```bash
# Crear nueva branch desde develop
git checkout develop
git pull origin develop
git checkout -b 010-reverse-geocoding

# Crear estructura de especificación
mkdir -p specs/010-reverse-geocoding
```

---

## Roadmap de Features 🗺️

### ✅ Features Completadas

#### Feature 001: User Profiles Backend ✅
- Sistema de autenticación backend
- Perfiles de usuario
- Stats tracking

#### Feature 002: Travel Diary Backend ✅
- Trips CRUD
- Photos upload
- Tags system
- Draft workflow

#### Feature 005: Frontend User Auth ✅
- Sistema de autenticación completo
- Diseño rústico aplicado
- Dashboard y Profile placeholders

#### Feature 006: Dashboard Dinámico ✅
- Stats cards con datos reales
- Recent trips section
- Quick actions

#### Feature 007: Gestión de Perfil Completa ✅
- Editar perfil completo
- Upload y crop de foto de perfil
- Cambiar contraseña
- Configuración de cuenta

#### Feature 008: Travel Diary Frontend ✅
- Lista de viajes con filtros
- Crear/editar viaje (multi-step form)
- Detalle de viaje completo
- Upload múltiple de fotos
- Sistema de tags interactivo
- Photo gallery con lightbox

#### Feature 009: GPS Coordinates Frontend ✅
- LocationInput component para coordenadas
- TripMap component con react-leaflet
- Numbered markers y route polyline
- Fullscreen mode
- Error handling y tile retry
- Location list con estado "Sin coordenadas GPS"

---

### 🚧 Feature 010: Reverse Geocoding (SIGUIENTE)

**Prioridad**: Alta
**Estimación**: 3-4 días

**User Stories**:
1. Como usuario, quiero hacer click en el mapa para seleccionar ubicaciones automáticamente
2. Como usuario, quiero que el sistema obtenga el nombre del lugar desde las coordenadas GPS
3. Como usuario, quiero poder arrastrar markers para ajustar coordenadas
4. Como usuario, quiero confirmar o editar el nombre sugerido antes de agregarlo

**Entregables**:
- Backend: Endpoint `/api/geocoding/reverse?lat={lat}&lon={lon}`
- Frontend: `useMapClick` hook para captura de coordenadas
- Frontend: Modal de confirmación con nombre sugerido
- Frontend: Drag markers en modo edición
- Tests: Unit + integration para reverse geocoding
- Docs: Testing guide y troubleshooting

**APIs a integrar**:
- Nominatim OpenStreetMap API (https://nominatim.openstreetmap.org/)
- Rate limiting: 1 req/sec máximo
- Cache de resultados para evitar duplicados

**Arquitectura**:
```
User clicks map
    ↓
Capture lat/lng
    ↓
Call /api/geocoding/reverse
    ↓
Backend calls Nominatim API
    ↓
Return place name + address
    ↓
Show confirmation modal
    ↓
User confirms → Add to locations list
```

---

### ⏳ Features Futuras

#### Feature 003: GPS Routes (Backend complejo)
- **Prioridad**: Media-Alta
- **Estimación**: 7-10 días
- **Estado**: ❌ NO implementada (solo spec draft)
- Upload y procesamiento de archivos GPX
- Perfil de elevación interactivo
- Estadísticas avanzadas (velocidad, tiempo, gradientes)
- Puntos de interés en la ruta
- Análisis de rendimiento

#### Feature 011: Social Features Frontend (Completa Feature 004)
- **Prioridad**: Media
- **Estimación**: 6-8 días
- **Backend status**: ⚠️ Parcialmente implementado (solo Follow/Unfollow)
- **Frontend status**: ❌ No implementado
- Feed personalizado de viajes
- Likes y comentarios en viajes
- Compartir viajes
- Notificaciones de interacciones
- **Nota**: Backend tiene Follow/Unfollow, falta Feed, Likes, Comments, Shares, Notifications

#### Feature 012: Advanced Search & Filters
- **Prioridad**: Media
- **Estimación**: 3-4 días
- Búsqueda global de viajes
- Filtros avanzados (distancia, dificultad, tags)
- Mapa global con clustering

#### Feature 013: Route Export & Import
- **Prioridad**: Baja
- **Estimación**: 2-3 días
- Export routes to GPX/KML
- Import routes from Strava/Komoot
- Route statistics and elevation

---

## Comandos Útiles 🛠️

### Git Workflow
```bash
# Verificar estado
git status

# Ver commits recientes
git log --oneline -10

# Crear nueva branch para feature 010
git checkout develop
git pull origin develop
git checkout -b 010-reverse-geocoding

# Push de branch
git push -u origin 010-reverse-geocoding
```

### Frontend Development
```bash
# Instalar dependencias
cd frontend
npm install

# Dev server
npm run dev  # http://localhost:5173

# Run tests
npm run test

# Build
npm run build
```

### Backend Development
```bash
# Setup completo
cd backend
./run-local-dev.sh --setup

# Solo iniciar servidor
./run-local-dev.sh

# Run tests
poetry run pytest

# Ver logs de API
tail -f backend/logs/app.log
```

---

## Recursos Clave 📚

### Documentación del Proyecto
- **CLAUDE.md**: Guía principal del proyecto
- **frontend/TESTING_GUIDE.md**: Testing guide para GPS coordinates
- **specs/009-gps-coordinates/**: Especificación completa de Feature 009

### Especificaciones de Features
- **specs/001-user-profiles/**: Backend auth & profiles (merged)
- **specs/002-travel-diary/**: Backend travel diary (merged)
- **specs/005-frontend-user-profile/**: Frontend auth (merged)
- **specs/006-dashboard-dynamic/**: Dashboard dinámico (merged)
- **specs/007-profile-management/**: Gestión de perfil (merged)
- **specs/008-travel-diary-frontend/**: Travel Diary Frontend (merged)
- **specs/009-gps-coordinates/**: GPS Coordinates Frontend (merged)
- **specs/010-reverse-geocoding/**: Reverse Geocoding (a crear)

### APIs Backend
- **Swagger Docs**: http://localhost:8000/docs
- **Auth Endpoints**: `/api/auth/*`
- **Profile Endpoints**: `/api/profile/*`
- **Stats Endpoints**: `/api/stats/*`
- **Trips Endpoints**: `/api/trips/*`

---

## Métricas de Progreso 📊

### Features Completadas (9/13)
- ✅ 001: User Profiles Backend
- ✅ 002: Travel Diary Backend
- ✅ 005: Frontend User Auth
- ✅ 006: Dashboard Dinámico
- ✅ 007: Gestión de Perfil
- ✅ 008: Travel Diary Frontend
- ✅ 009: GPS Coordinates Frontend

### Features En Progreso (0/13)
- (Ninguna en progreso actualmente)

### Features Pendientes (4/13)
- 🎯 010: Reverse Geocoding (SIGUIENTE)
- ⏳ 011: Social Features Frontend
- ⏳ 012: Advanced Search & Filters
- ⏳ 013: Route Export & Import

### Líneas de Código (estimado)
- **Backend**: ~25,000 líneas (Python)
- **Frontend**: ~20,000 líneas (TypeScript/React)
- **Tests**: ~15,000 líneas
- **Docs**: ~20,000 líneas

---

## Decisiones Técnicas Recientes 📋

### Feature 009 (GPS Coordinates)
- ✅ Usar react-leaflet para mapa interactivo
- ✅ OpenStreetMap tiles (gratis, sin API key)
- ✅ Numbered markers con DivIcon
- ✅ Fullscreen API nativo del navegador
- ✅ Error handling con retry para tile loading
- ✅ Precision de 6 decimales para coordenadas GPS

### Feature 010 (Reverse Geocoding) - Pendientes
- [ ] ¿Usar Nominatim OSM o Google Geocoding API?
  - **Recomendación**: Nominatim (gratis, sin API key, rate limit 1 req/sec)
- [ ] ¿Cache de resultados en backend o frontend?
  - **Recomendación**: Backend cache con Redis (futuro) o SQLite
- [ ] ¿Modal de confirmación o edición inline?
  - **Recomendación**: Modal para mejor UX

---

**¡Listo para Feature 010: Reverse Geocoding!** 🚀

El sistema de GPS coordinates está completo y mergeado. Ahora podemos agregar la funcionalidad de reverse geocoding para que los usuarios puedan seleccionar ubicaciones haciendo click en el mapa.

**Siguiente acción**: Crear especificación de Feature 010 → Implementar → Testing → Merge
