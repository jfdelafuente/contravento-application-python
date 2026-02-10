# Manual Testing - Activity Likes (Feature 018 - US2)

**Feature**: Activity Stream Feed - Like Activities
**User Story**: US2 - Como usuario quiero dar "me gusta" a actividades del feed para expresar apreciación
**Last Updated**: 2026-02-10

---

## Pre-requisitos

### 1. Backend y Frontend en ejecución

```bash
# Terminal 1: Backend
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Usuarios de prueba

Se necesitan al menos **2 usuarios** para probar el flujo completo:

**Usuario 1 - testuser:**
- Username: `testuser`
- Password: `TestPass123!`

**Usuario 2 - maria_garcia:**
- Username: `maria_garcia`
- Password: `SecurePass456!`

Si no existen, crearlos con:

```bash
cd backend
poetry run python scripts/user-mgmt/create_verified_user.py --username testuser --email test@example.com --password "TestPass123!"
poetry run python scripts/user-mgmt/create_verified_user.py --username maria_garcia --email maria@example.com --password "SecurePass456!"
```

### 3. Datos de prueba necesarios

#### a) Crear trips para generar actividades

```bash
cd backend
# Crear trips para maria_garcia (estos aparecerán en el feed de testuser)
poetry run python scripts/seeding/seed_trips.py --user maria_garcia --count 2

# Crear trips para testuser (estos aparecerán en el feed de maria_garcia)
poetry run python scripts/seeding/seed_trips.py --user testuser --count 2
```

#### b) Establecer relaciones de "follow"

**IMPORTANTE**: El feed solo muestra actividades de usuarios seguidos. Necesitas que testuser siga a maria_garcia (y viceversa).

**Opción 1 - Desde el frontend** (recomendado):
1. Login como `testuser`
2. Ir a perfil de `maria_garcia`: `http://localhost:5173/@maria_garcia`
3. Click en botón "Seguir"
4. Logout
5. Login como `maria_garcia`
6. Ir a perfil de `testuser`: `http://localhost:5173/@testuser`
7. Click en botón "Seguir"

**Opción 2 - Via API directa** (si el botón no existe en UI):
```bash
# Login como testuser, copiar access_token del response
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}'

# Usar el token para seguir a maria_garcia (reemplazar {TOKEN} y {MARIA_ID})
curl -X POST "http://localhost:8000/users/{MARIA_ID}/follow" \
  -H "Authorization: Bearer {TOKEN}"

# Repetir para maria_garcia siguiendo a testuser
```

---

## Escenarios de Testing

### 📋 TEST 1: Like/Unlike básico con optimistic updates

**Objetivo**: Verificar que el botón de like funciona y la UI se actualiza inmediatamente.

**Pasos**:

1. **Login como testuser**
   - URL: `http://localhost:5173/login`
   - Credenciales: `testuser` / `TestPass123!`

2. **Ir al Activity Feed**
   - URL: `http://localhost:5173/feed`
   - Verificar que aparecen actividades de `maria_garcia`
   - Si no aparecen, verificar pre-requisitos (follow + trips creados)

3. **Like una actividad**
   - Localizar primera actividad (TRIP_PUBLISHED de maria_garcia)
   - Observar contador inicial de likes (ej: 0)
   - **Click en ícono de corazón ❤️**

   **Verificaciones**:
   - [ ] ✅ El corazón cambia de vacío a lleno **INMEDIATAMENTE** (optimistic update)
   - [ ] ✅ El contador aumenta en +1 **INMEDIATAMENTE** (ej: 0 → 1)
   - [ ] ✅ No hay retraso perceptible (<100ms)
   - [ ] ✅ No hay recarga de página

4. **Unlike la misma actividad**
   - **Click nuevamente en el corazón lleno**

   **Verificaciones**:
   - [ ] ✅ El corazón cambia de lleno a vacío **INMEDIATAMENTE**
   - [ ] ✅ El contador disminuye en -1 **INMEDIATAMENTE** (ej: 1 → 0)

5. **Recargar la página**
   - **F5** o **Ctrl+R**

   **Verificaciones**:
   - [ ] ✅ El corazón sigue vacío (unlike persistió)
   - [ ] ✅ El contador sigue en valor original (0)

---

### 📋 TEST 2: Idempotencia - Like múltiple

**Objetivo**: Verificar que hacer like varias veces no duplica el contador.

**Pasos**:

1. **Seguir en el feed como testuser**

2. **Click rápidamente 5 veces en el mismo corazón**
   - Hacer clicks muy rápidos consecutivos

   **Verificaciones**:
   - [ ] ✅ El contador solo aumenta 1 vez (no 5 veces)
   - [ ] ✅ La UI no "parpadea" o se comporta erráticamente
   - [ ] ✅ El estado final es "liked" (corazón lleno, contador +1)

3. **Recargar página**

   **Verificaciones**:
   - [ ] ✅ Solo hay 1 like registrado (no 5)

---

### 📋 TEST 3: Múltiples usuarios - is_liked_by_me

**Objetivo**: Verificar que cada usuario ve su propio estado de like independientemente.

**Pasos**:

1. **Como testuser**: Dar like a una actividad de maria_garcia
   - Observar: corazón lleno, contador = 1

2. **Abrir ventana de incógnito** (o navegador diferente)

3. **Login como maria_garcia** en la ventana de incógnito
   - URL: `http://localhost:5173/login`
   - Credenciales: `maria_garcia` / `SecurePass456!`

4. **Ir al feed de maria_garcia**
   - URL: `http://localhost:5173/feed`
   - Buscar una actividad de testuser

5. **Dar like a la actividad de testuser**

   **Verificaciones**:
   - [ ] ✅ El corazón cambia a lleno para maria_garcia
   - [ ] ✅ El contador aumenta (probablemente de 0 → 1)

6. **Volver a la ventana de testuser** (navegador original)

7. **Actualizar el feed** (scroll down y scroll up, o F5)

   **Verificaciones**:
   - [ ] ✅ Las actividades de maria_garcia que testuser ha likeado siguen con corazón lleno
   - [ ] ✅ Las actividades de testuser que maria_garcia ha likeado muestran contador > 0 pero corazón VACÍO para testuser (porque testuser no las ha likeado)

**Concepto clave**: `is_liked_by_me` es personal - cada usuario ve sus propios likes independientemente.

---

### 📋 TEST 4: Lista de usuarios que dieron like

**Objetivo**: Verificar el endpoint GET /activities/{id}/likes muestra quién dio like.

**Pasos**:

1. **Setup**: Tener una actividad con likes de 2 usuarios
   - testuser da like a actividad X
   - maria_garcia da like a actividad X

2. **Acceder al endpoint de likes** (usando navegador o curl)

   **Via navegador**:
   - Abrir: `http://localhost:8000/activities/{ACTIVITY_ID}/likes?page=1&limit=10`
   - Reemplazar `{ACTIVITY_ID}` con el ID real de la actividad
   - **Nota**: Este endpoint es público (no requiere autenticación)

   **Via curl**:
   ```bash
   curl "http://localhost:8000/activities/{ACTIVITY_ID}/likes?page=1&limit=10"
   ```

   **Verificaciones**:
   - [ ] ✅ Response muestra `total_count: 2`
   - [ ] ✅ Array `likes` contiene 2 elementos
   - [ ] ✅ Cada like muestra: `username`, `user_photo_url`, `created_at`
   - [ ] ✅ Están presentes `testuser` y `maria_garcia`

3. **Test paginación**:
   - Llamar con `limit=1&page=1`
   - **Verificaciones**:
     - [ ] ✅ Devuelve 1 like
     - [ ] ✅ `has_next: true`
     - [ ] ✅ `total_count: 2`

   - Llamar con `limit=1&page=2`
   - **Verificaciones**:
     - [ ] ✅ Devuelve el segundo like
     - [ ] ✅ `has_next: false`

---

### 📋 TEST 5: Error handling y rollback

**Objetivo**: Verificar que si el backend falla, la UI revierte el optimistic update.

**Pasos**:

1. **Simular fallo del backend**:
   - **Opción 1**: Detener el backend temporalmente
     ```bash
     # En terminal del backend: Ctrl+C
     ```

   - **Opción 2**: Usar DevTools para bloquear request
     - F12 → Network tab
     - Click derecho en request `POST /activities/{id}/like`
     - "Block request URL"

2. **Como testuser, intentar dar like**
   - Click en corazón

   **Verificaciones**:
   - [ ] ✅ UI muestra optimistic update inmediatamente (corazón lleno)
   - [ ] ✅ Después de ~3-5 segundos aparece toast de error: "Error al actualizar like. Intenta de nuevo."
   - [ ] ✅ El corazón vuelve a estado vacío (rollback)
   - [ ] ✅ El contador vuelve al valor original (rollback)

3. **Reiniciar el backend**

4. **Intentar like nuevamente**

   **Verificaciones**:
   - [ ] ✅ Ahora funciona correctamente
   - [ ] ✅ El like persiste al recargar

---

### 📋 TEST 6: Contador de likes preciso

**Objetivo**: Verificar que el contador siempre refleja el número correcto.

**Pasos**:

1. **Tener 2 navegadores abiertos** (o ventanas incógnito):
   - Navegador A: Login como `testuser`
   - Navegador B: Login como `maria_garcia`

2. **Ambos usuarios ven la misma actividad** (de un tercer usuario o entre ellos)

3. **Secuencia de acciones**:

   a) **testuser da like**
   - Navegador A: Click en corazón
   - **Verificar navegador A**: Contador = 1

   b) **maria_garcia da like**
   - Navegador B: Click en corazón
   - **Verificar navegador B**: Contador = 2

   c) **testuser quita like**
   - Navegador A: Click en corazón (unlike)
   - **Verificar navegador A**: Contador = 1

   d) **Recargar ambos navegadores** (F5)

   **Verificaciones finales**:
   - [ ] ✅ Navegador A (testuser): Corazón vacío, contador = 1
   - [ ] ✅ Navegador B (maria_garcia): Corazón lleno, contador = 1
   - [ ] ✅ Llamar API `/activities/{id}/likes` confirma `total_count: 1` y solo maria_garcia en la lista

---

### 📋 TEST 7: Stress test - Likes rápidos consecutivos

**Objetivo**: Verificar estabilidad con interacciones muy rápidas.

**Pasos**:

1. **Como testuser en el feed**

2. **Realizar 10 ciclos like/unlike muy rápidos**:
   - Click like
   - Click unlike
   - Click like
   - Click unlike
   - ... (repetir 10 veces en ~5 segundos)

   **Verificaciones durante**:
   - [ ] ✅ La UI responde a cada click sin lag
   - [ ] ✅ No hay mensajes de error
   - [ ] ✅ El corazón alterna correctamente entre lleno/vacío

3. **Estado final esperado**: Unlike (corazón vacío)

4. **Recargar página**

   **Verificaciones**:
   - [ ] ✅ El corazón sigue vacío
   - [ ] ✅ El contador está en el valor correcto (sin duplicados)

---

## Casos Edge

### 🔍 EDGE 1: Actividad sin likes

**Verificar**:
- [ ] Actividad nueva muestra contador = 0
- [ ] Corazón está vacío
- [ ] Primer like aumenta contador a 1 correctamente

### 🔍 EDGE 2: Actividad con muchos likes (>20)

**Verificar**:
- [ ] Endpoint `/activities/{id}/likes?page=1&limit=20` muestra primeros 20
- [ ] `has_next: true` si hay más de 20
- [ ] `page=2` muestra siguiente página

### 🔍 EDGE 3: Self-like (propio trip)

**Escenario**: testuser da like a su propia actividad

**Verificar**:
- [ ] ✅ El like funciona (está permitido)
- [ ] ✅ No se crea notificación (self-like no notifica)

---

## Problemas Conocidos y Limitaciones

### ⚠️ Feed vacío

**Síntoma**: Al entrar a `/feed` no aparecen actividades.

**Causas**:
1. El usuario no sigue a nadie → Feed solo muestra actividades de usuarios seguidos
2. Los usuarios seguidos no tienen trips publicados

**Solución**:
- Verificar follows: `testuser` debe seguir a `maria_garcia` (y viceversa)
- Crear trips con `seed_trips.py` como se indica en Pre-requisitos

### ⚠️ Notifications deshabilitadas

**Estado actual**: La creación de notificaciones al dar like está **DESHABILITADA** temporalmente.

**Razón**: El modelo `Notification` solo soporta notificaciones de trips (campo `trip_id` obligatorio), no de actividades genéricas.

**Tarea futura**: T051 - Extender esquema de Notification para soportar `activity_id`.

**Impacto en testing**: No se generan notificaciones al dar like. Esto es **esperado** en la implementación actual de US2.

---

## Checklist de Testing Completo

Para considerar US2 completamente validado:

- [ ] TEST 1: Like/Unlike básico funciona ✅
- [ ] TEST 2: Idempotencia confirmada ✅
- [ ] TEST 3: is_liked_by_me por usuario funciona ✅
- [ ] TEST 4: Lista de likes con paginación ✅
- [ ] TEST 5: Error handling y rollback ✅
- [ ] TEST 6: Contador preciso con múltiples usuarios ✅
- [ ] TEST 7: Stress test passed ✅
- [ ] EDGE 1: Actividad sin likes ✅
- [ ] EDGE 2: Paginación con >20 likes ✅
- [ ] EDGE 3: Self-like permitido ✅
- [ ] Optimistic updates inmediatos (<100ms) ✅
- [ ] Backend tests (21/21) passing ✅
- [ ] Frontend compila sin errores ✅

---

## Notas Técnicas

### TanStack Query Cache

El hook `useActivityLike` usa **optimistic updates** con TanStack Query:

1. **onMutate**: Actualiza cache ANTES de llamar API (UI instantánea)
2. **onError**: Revierte cache si API falla (rollback)
3. **Query key matching**: Usa partial match `['activityFeed']` para actualizar todas las queries del feed independientemente del `limit`

### API Response Format

**Like activity** (`POST /activities/{id}/like`):
```json
{
  "like_id": "uuid",
  "user_id": "uuid",
  "activity_id": "uuid",
  "created_at": "2026-02-10T15:30:00Z"
}
```

**Get likes** (`GET /activities/{id}/likes`):
```json
{
  "likes": [
    {
      "like_id": "uuid",
      "user_id": "uuid",
      "username": "testuser",
      "user_photo_url": "/storage/...",
      "created_at": "2026-02-10T15:30:00Z"
    }
  ],
  "total_count": 2,
  "page": 1,
  "limit": 20,
  "has_next": false
}
```

---

## Soporte

Si encuentras bugs durante el testing manual:

1. **Verificar backend logs**: Revisar terminal del backend para errores
2. **Verificar frontend DevTools**: F12 → Console/Network para errores JS
3. **Verificar base de datos**: Queries directas a `activity_likes` table
4. **Reportar**: Crear issue con pasos para reproducir

**Tests automatizados**: `cd backend && poetry run pytest tests/unit/test_activity_like_service.py -v`
