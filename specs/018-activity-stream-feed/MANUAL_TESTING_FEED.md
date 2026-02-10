# Manual Testing Guide - Activity Feed (Feature 018 - US1)

**Feature**: 018-activity-stream-feed
**User Story**: US1 - Como usuario quiero ver un feed de actividades de los ciclistas que sigo para mantenerme al día de sus logros
**Phase**: Phase 3 - US1 - View Activity Feed from Followed Users (P1 - MVP)
**Status**: ✅ COMPLETE (40/40 tasks)

**Última actualización**: 2026-02-10

---

## Objetivo del Testing

Validar que el Activity Feed muestra correctamente actividades de usuarios seguidos en orden cronológico, con paginación infinita, empty states apropiados, y navegación funcional a detalles.

**Success Criteria**:
- **SC-001**: Feed carga en <2s con 20 actividades (p95)
- **SC-002**: Feed solo muestra actividades de usuarios seguidos (privacy)
- **FR-001**: Orden cronológico (más reciente primero)
- **FR-003**: Paginación de 20 items por batch
- **FR-004**: Metadata completa (autor, foto, timestamp relativo, preview)
- **FR-005**: Empty state cuando no hay follows

---

## Pre-requisitos

### a) Backend y Frontend Corriendo

**Backend**:
```bash
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Verificar que está corriendo:
# http://localhost:8000/docs (debe mostrar Swagger UI)
```

**Frontend**:
```bash
cd frontend
npm run dev

# Verificar que está corriendo:
# http://localhost:5173 (debe mostrar Landing Page)
```

### b) Usuarios de Prueba Creados

**Usuarios necesarios**: `testuser`, `maria_garcia` (ambos verificados)

```bash
cd backend

# Verificar que existen
poetry run python -c "
from sqlalchemy import create_engine, select
from src.models.user import User
from src.config import settings
engine = create_engine(str(settings.DATABASE_URL))
with engine.connect() as conn:
    users = conn.execute(select(User.username, User.email)).fetchall()
    print('Usuarios existentes:', users)
"

# Si no existen, crearlos:
poetry run python scripts/user-mgmt/create_verified_user.py
# Esto crea testuser y maria_garcia automáticamente
```

### c) Relaciones de "Follow" Establecidas

**IMPORTANTE**: El feed solo muestra actividades de usuarios seguidos.

**Opción 1 - Desde el frontend** (recomendado):
1. Login como `testuser`
2. Ir a perfil de `maria_garcia`: `http://localhost:5173/users/maria_garcia`
3. Click en botón "Seguir"
4. Logout
5. Login como `maria_garcia`
6. Ir a perfil de `testuser`: `http://localhost:5173/users/testuser`
7. Click en botón "Seguir"

**Opción 2 - Via script** (si botón no existe):
```bash
cd backend
poetry run python scripts/seeding/create_follows.py
# Crea follows bidireccionales entre testuser y maria_garcia
```

### d) Trips de Prueba con Actividades

**Crear trips para generar actividades TRIP_PUBLISHED**:

```bash
cd backend

# Crear trips para maria_garcia (estos aparecerán en el feed de testuser)
poetry run python scripts/seeding/seed_trips.py --user maria_garcia --count 4

# Crear trips para testuser (estos aparecerán en el feed de maria_garcia)
poetry run python scripts/seeding/seed_trips.py --user testuser --count 3

# Verificar actividades creadas:
poetry run python -c "
from sqlalchemy import create_engine, select
from src.models.activity_feed_item import ActivityFeedItem
from src.config import settings
engine = create_engine(str(settings.DATABASE_URL))
with engine.connect() as conn:
    count = conn.execute(select(ActivityFeedItem)).fetchall()
    print(f'Actividades en DB: {len(count)}')
"
```

**Resultado esperado**: ~7 actividades (4 de maria_garcia + 3 de testuser)

---

## Tests Principales

### 📋 TEST 1: Feed Cronológico Básico

**Objetivo**: Verificar que el feed muestra actividades en orden cronológico descendente.

**Pasos**:

1. **Login como testuser**
   - URL: `http://localhost:5173/login`
   - Credenciales: `testuser` / `TestPass123!`

2. **Ir al Activity Feed**
   - URL: `http://localhost:5173/activities`

3. **Verificar estructura del feed**

   **Verificaciones**:
   - [ ] ✅ El feed carga en <2s (SC-001)
   - [ ] ✅ Se muestran actividades de `maria_garcia` (usuarios seguidos)
   - [ ] ✅ NO se muestran actividades propias de `testuser` (solo de followed users)
   - [ ] ✅ Las actividades están ordenadas de más reciente a más antigua (timestamp descendente)
   - [ ] ✅ Cada actividad muestra:
     - Nombre del autor (`maria_garcia`)
     - Foto de perfil del autor
     - Tipo de actividad (ej: "publicó un viaje")
     - Timestamp relativo en español ("hace 2 horas", "hace 3 días")
     - Preview del contenido (título del trip, foto)

4. **Verificar metadata de actividad**

   - Localizar primera actividad (más reciente)
   - Verificar campos:
     - [ ] ✅ Avatar del autor es visible (o placeholder si no tiene foto)
     - [ ] ✅ Nombre del autor clickeable (link a perfil)
     - [ ] ✅ Timestamp relativo correcto (español)
     - [ ] ✅ Título del trip visible
     - [ ] ✅ Distancia del trip visible (ej: "📍 45.3 km")
     - [ ] ✅ Foto del trip visible **SOLO si el trip tiene fotos** (trips de seed_trips.py NO tienen fotos)
     - [ ] ❌ La descripción del trip NO se muestra (solo en trip detail page)

---

### 📋 TEST 2: Infinite Scroll / Paginación

**Objetivo**: Verificar que el feed carga más actividades al scrollear (cursor-based pagination).

**Prerequisito**: Tener >20 actividades en la DB (crear más trips si es necesario)

**Pasos**:

1. **Crear 25+ actividades** (si no hay suficientes):
   ```bash
   cd backend
   poetry run python scripts/seeding/seed_trips.py --user maria_garcia --count 25
   ```

2. **Login como testuser y acceder al feed**
   - URL: `http://localhost:5173/activities`

3. **Observar primera carga**

   **Verificaciones**:
   - [ ] ✅ Se muestran exactamente 20 actividades en la primera carga (FR-003)
   - [ ] ✅ Hay indicador de "Cargar más" o scroll infinito habilitado

4. **Scroll hasta el final de la lista**

   - Scrollear hacia abajo hasta llegar al final
   - Observar comportamiento

   **Verificaciones**:
   - [ ] ✅ Se cargan automáticamente las siguientes actividades (batch 2)
   - [ ] ✅ NO hay duplicados entre batch 1 y batch 2 (cursor funciona)
   - [ ] ✅ El loading indicator aparece durante la carga
   - [ ] ✅ Las nuevas actividades mantienen orden cronológico

5. **Verificar paginación completa**

   - Continuar scrolling hasta agotar todas las actividades

   **Verificaciones**:
   - [ ] ✅ El scroll se detiene cuando no hay más actividades
   - [ ] ✅ Mensaje "No hay más actividades" o botón deshabilitado

---

### 📋 TEST 3: Privacy - Solo Usuarios Seguidos

**Objetivo**: Verificar que el feed SOLO muestra actividades de usuarios seguidos, no de usuarios aleatorios.

**Pasos**:

1. **Crear un tercer usuario que testuser NO sigue**
   ```bash
   cd backend
   poetry run python scripts/user-mgmt/create_verified_user.py \
     --username john \
     --email john@example.com \
     --password "SecurePass789!"
   ```

2. **Crear trips para john**
   ```bash
   poetry run python scripts/seeding/seed_trips.py --user john --count 3
   ```

3. **Login como testuser**
   - URL: `http://localhost:5173/activities`

4. **Verificar feed**

   **Verificaciones**:
   - [ ] ✅ Se muestran actividades de `maria_garcia` (usuario seguido)
   - [ ] ❌ NO se muestran actividades de `john` (usuario NO seguido)
   - [ ] ✅ El feed está vacío de actividades de john

5. **Seguir a john desde el frontend**
   - Ir a perfil de john: `http://localhost:5173/users/john`
   - Click en "Seguir"
   - Volver al feed: `http://localhost:5173/activities`

6. **Verificar actualización del feed**

   **Verificaciones**:
   - [ ] ✅ Ahora aparecen actividades de `john` en el feed
   - [ ] ✅ Las actividades de john están mezcladas cronológicamente con las de maria_garcia

---

### 📋 TEST 4: Empty State - Sin Follows

**Objetivo**: Verificar que el feed muestra mensaje apropiado cuando el usuario no sigue a nadie.

**Pasos**:

1. **Crear un nuevo usuario sin follows**
   ```bash
   cd backend
   poetry run python scripts/user-mgmt/create_verified_user.py \
     --username lonely \
     --email lonely@example.com \
     --password "LonelyPass123!"
   ```

2. **Login como lonely**
   - URL: `http://localhost:5173/login`
   - Credenciales: `lonely` / `LonelyPass123!`

3. **Ir al Activity Feed**
   - URL: `http://localhost:5173/activities`

4. **Verificar Empty State**

   **Verificaciones**:
   - [ ] ✅ Se muestra mensaje: "Empieza a seguir usuarios para ver su actividad" o similar (FR-005)
   - [ ] ✅ El mensaje es claro y sugerente (no un error)
   - [ ] ✅ Hay un call-to-action para descubrir usuarios (opcional)
   - [ ] ✅ NO hay spinner de loading infinito
   - [ ] ✅ NO se muestra error 404 o 500

---

### 📋 TEST 5: Navegación a Detalles

**Objetivo**: Verificar que hacer click en una actividad redirige al detalle correspondiente.

**Pasos**:

1. **Login como testuser**
   - URL: `http://localhost:5173/activities`

2. **Localizar una actividad de tipo TRIP_PUBLISHED**

3. **Click en la tarjeta de la actividad** (área completa o título)

   **Verificaciones**:
   - [ ] ✅ Soy redirigido a `/trips/{trip_id}` (Trip Detail Page)
   - [ ] ✅ La página de detalle carga correctamente
   - [ ] ✅ El trip mostrado corresponde a la actividad clickeada

4. **Volver al feed con botón "Atrás" del navegador**

   **Verificaciones**:
   - [ ] ✅ El feed mantiene la posición de scroll (no vuelve al inicio)
   - [ ] ✅ Las actividades no se recargan innecesariamente (TanStack Query cache)

5. **Click en avatar o nombre de usuario en una actividad**

   **Verificaciones**:
   - [ ] ✅ Soy redirigido a `/users/{username}` (User Profile Page)
   - [ ] ✅ El perfil mostrado corresponde al autor de la actividad
   - [ ] ✅ Funciona tanto desde el avatar como desde el nombre de usuario

---

### 📋 TEST 6: Timestamps Relativos en Español

**Objetivo**: Verificar que los timestamps se muestran en español con formato relativo.

**Pasos**:

1. **Login como testuser y acceder al feed**
   - URL: `http://localhost:5173/activities`

2. **Observar timestamps de actividades recientes** (creadas hace <1 hora)

   **Verificaciones**:
   - [ ] ✅ Actividades recientes muestran "hace X minutos" o "hace X horas"
   - [ ] ✅ Actividades de ayer muestran "ayer" o "hace 1 día"
   - [ ] ✅ Actividades más antiguas muestran "hace X días"
   - [ ] ✅ TODO el texto está en español (no "2 hours ago" en inglés)

3. **Crear una actividad muy reciente** (para testing de "hace pocos segundos"):
   ```bash
   cd backend
   poetry run python scripts/seeding/seed_trips.py --user maria_garcia --count 1
   ```

4. **Refrescar el feed** (F5)

   **Verificaciones**:
   - [ ] ✅ La nueva actividad aparece en la parte superior
   - [ ] ✅ Muestra "hace pocos segundos" o "hace menos de 1 minuto"

---

### 📋 TEST 7: Activity Types (TRIP_PUBLISHED)

**Objetivo**: Verificar que actividades TRIP_PUBLISHED se renderizan correctamente.

**Pasos**:

1. **Verificar actividades de tipo TRIP_PUBLISHED**

   - Login como testuser
   - Buscar actividades en el feed

   **Verificaciones**:
   - [ ] ✅ Se muestra texto: "publicó un viaje"
   - [ ] ✅ Se muestra título del trip (metadata.trip_title)
   - [ ] ✅ Se muestra distancia del trip con icono: "📍 45.3 km" (metadata.trip_distance_km)
   - [ ] ✅ Se muestra foto del trip SOLO si tiene fotos (metadata.trip_photo_url)
   - [ ] ❌ NO se muestra descripción del trip (solo en detail page)
   - [ ] ❌ NO se muestra fecha de inicio (solo en detail page)

2. **Verificar metadatos específicos de trips**

   - Localizar actividad TRIP_PUBLISHED
   - Click en la tarjeta para ir al detalle

   **Verificaciones**:
   - [ ] ✅ El trip_id en la actividad corresponde al trip real
   - [ ] ✅ Los metadatos (title, distance) coinciden con el trip detail
   - [ ] ✅ La foto de portada (si existe) coincide con la primera foto del trip

---

## Casos Edge

### 🔍 EDGE 1: Usuario con 100+ follows

**Escenario**: Usuario sigue a muchos usuarios, generando feed muy largo

**Verificar**:
- [ ] El feed no se ralentiza con muchas actividades
- [ ] La paginación funciona correctamente (batches de 20)
- [ ] No hay memory leaks en infinite scroll

### 🔍 EDGE 2: Actividad sin foto de perfil

**Escenario**: Usuario sin foto de perfil publica un trip

**Verificar**:
- [ ] Se muestra avatar placeholder o iniciales
- [ ] NO se muestra broken image icon
- [ ] El feed sigue siendo visualmente coherente

### 🔍 EDGE 3: Trip sin foto

**Escenario**: Actividad TRIP_PUBLISHED de un trip sin fotos

**Verificar**:
- [ ] Se muestra placeholder de imagen del trip
- [ ] La tarjeta de actividad tiene altura consistente
- [ ] NO se rompe el layout del feed

### 🔍 EDGE 4: Refresh del feed con nuevas actividades

**Escenario**: Mientras el usuario está viendo el feed, otro usuario publica un trip

**Verificar**:
- [ ] Al refrescar la página (F5), aparecen las nuevas actividades
- [ ] Las nuevas actividades se insertan en el orden cronológico correcto
- [ ] No hay duplicados

---

## Problemas Conocidos y Limitaciones

### ⚠️ No hay actualización en tiempo real

**Estado actual**: El feed NO se actualiza automáticamente cuando hay nuevas actividades.

**Razón**: MVP no incluye WebSockets o Server-Sent Events (SSE).

**Workaround**: El usuario debe refrescar manualmente la página (F5) para ver nuevas actividades.

**Tarea futura**: Implementar real-time updates en iteración posterior.

### ⚠️ Solo actividades de tipo TRIP_PUBLISHED

**Estado actual**: El feed solo muestra actividades `TRIP_PUBLISHED`. Tipos como `PHOTO_UPLOADED` y `ACHIEVEMENT_UNLOCKED` están implementados en el backend pero requieren features adicionales:

- **PHOTO_UPLOADED**: Requiere Feature 002 (Travel Diary) con upload de fotos
- **ACHIEVEMENT_UNLOCKED**: Requiere sistema de achievements (US4)

**Impacto en testing**: Solo testear TRIP_PUBLISHED. Otros tipos se validarán en US4.

### ⚠️ Empty state sin sugerencias de usuarios

**Estado actual**: El empty state muestra solo un mensaje. NO incluye sugerencias de usuarios para seguir.

**Tarea futura**: Implementar sección "Usuarios sugeridos" en iteración posterior.

### ⚠️ Trips de seed_trips.py NO tienen fotos

**Estado actual**: Los trips creados con `poetry run python scripts/seeding/seed_trips.py` NO incluyen fotos automáticamente.

**Razón**: El script crea trips con metadatos básicos (título, descripción, distancia, fechas) pero NO sube fotos.

**Impacto en testing**:
- La tarjeta de actividad mostrará título y distancia
- NO mostrará foto del trip (campo `trip_photo_url` estará vacío en metadatos)
- Esto es **comportamiento esperado** - La foto solo aparece si el trip tiene fotos

**Workaround para testear con fotos**:
1. Crear trip manualmente desde el frontend: `http://localhost:5173/trips/new/manual`
2. Subir fotos al trip
3. Publicar el trip
4. Verificar que la actividad en el feed muestra la foto de portada

---

## Checklist de Testing Completo

Para considerar US1 completamente validado:

- [ ] TEST 1: Feed cronológico básico funciona ✅
- [ ] TEST 2: Infinite scroll con paginación ✅
- [ ] TEST 3: Privacy - Solo usuarios seguidos ✅
- [ ] TEST 4: Empty state sin follows ✅
- [ ] TEST 5: Navegación a detalles ✅
- [ ] TEST 6: Timestamps relativos en español ✅
- [ ] TEST 7: Activity types (TRIP_PUBLISHED) ✅
- [ ] EDGE 1: Usuario con 100+ follows ✅
- [ ] EDGE 2: Actividad sin foto de perfil ✅
- [ ] EDGE 3: Trip sin foto ✅
- [ ] EDGE 4: Refresh con nuevas actividades ✅
- [ ] Feed carga en <2s (SC-001) ✅
- [ ] Backend tests (40 tasks) passing ✅
- [ ] Frontend compila sin errores ✅

---

## Notas Técnicas

### TanStack Query Cache

El hook `useActivityFeed` usa **useInfiniteQuery** con cursor-based pagination:

1. **queryKey**: `['activityFeed', limit]` - Cache separado por limit
2. **queryFn**: `getActivityFeed({ cursor, limit })` - Llama API con cursor
3. **getNextPageParam**: Retorna `next_cursor` si `has_next: true`
4. **staleTime**: 60s - Data considerada fresh por 1 minuto

### API Response Format

**Get activity feed** (`GET /activity-feed?cursor={cursor}&limit={limit}`):
```json
{
  "activities": [
    {
      "activity_id": "uuid",
      "activity_type": "TRIP_PUBLISHED",
      "created_at": "2026-02-10T15:30:00Z",
      "user": {
        "user_id": "uuid",
        "username": "maria_garcia",
        "full_name": "María García",
        "profile_photo_url": "/storage/..."
      },
      "metadata": {
        "trip_id": "uuid",
        "title": "Ruta Pirineos",
        "distance_km": 45.3,
        "trip_photo_url": "/storage/..."
      },
      "likes_count": 5,
      "comments_count": 2,
      "is_liked_by_me": false
    }
  ],
  "next_cursor": "encoded_cursor_string",
  "has_next": true
}
```

### Cursor-Based Pagination

El cursor es un **string opaco** generado por el backend que codifica:
- Timestamp del último item
- ID del último item (para desambiguación)

**Ventajas sobre offset pagination**:
- ✅ No salta items si hay nuevas actividades
- ✅ Performance constante (no degrada con offset alto)
- ✅ Funciona con infinite scroll

---

## Soporte

Si encuentras bugs durante el testing manual:

1. **Verificar backend logs**: Revisar terminal del backend para errores
2. **Verificar frontend DevTools**: F12 → Console/Network para errores JS
3. **Verificar base de datos**: Queries directas a `activity_feed_items` table
   ```bash
   cd backend
   poetry run python -c "
   from sqlalchemy import create_engine, select
   from src.models.activity_feed_item import ActivityFeedItem
   from src.config import settings
   engine = create_engine(str(settings.DATABASE_URL))
   with engine.connect() as conn:
       items = conn.execute(select(ActivityFeedItem)).fetchall()
       print(f'Total activities: {len(items)}')
       for item in items[:5]:
           print(item)
   "
   ```
4. **Reportar**: Crear issue con pasos para reproducir

**Tests automatizados**: `cd backend && poetry run pytest tests/integration/test_activity_feed_api.py -v`

---

**Documento creado**: 2026-02-10
**Autor**: Claude
**Versión**: 1.0
