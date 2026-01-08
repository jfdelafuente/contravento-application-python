# Manual Testing: Tags & Categorization (Phase 6)

**Feature**: 002-travel-diary - User Story 4
**Created**: 2025-12-30
**Endpoints**:
- `GET /users/{username}/trips` - List user trips with tag/status filtering
- `GET /tags` - Get all available tags

---

## Prerequisites

### 1. Start Development Server

```bash
cd backend
poetry run uvicorn src.main:app --reload
```

### 2. Create Test User and Login

```bash
# Create verified user
poetry run python scripts/create_verified_user.py --username tag_user --email tag@example.com --password "TagTest123!"

# Login to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "tag_user",
    "password": "TagTest123!"
  }'
```

**Save the access_token** from response:
```bash
export TOKEN="<your_access_token_here>"
```

---

## Test Flow: Complete Tag Scenario

### Step 1: Create Trips with Different Tags

**Trip 1: Bikepacking con tags "bikepacking" y "montaña"**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Bikepacking Pirineos",
    "description": "Viaje de 5 días por los Pirineos con acampada salvaje. Paisajes increíbles y senderos técnicos.",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "distance_km": 320.5,
    "tags": ["bikepacking", "montaña"]
  }'
```

Save `trip_id` as `TRIP1_ID`

**Trip 2: Gravel con tag "gravel"**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Gravel Costa Brava",
    "description": "Recorrido de 100km por caminos de tierra y carreteras secundarias de la Costa Brava.",
    "start_date": "2024-07-15",
    "distance_km": 102.3,
    "tags": ["gravel", "costa"]
  }'
```

Save `trip_id` as `TRIP2_ID`

**Trip 3: Montaña con tag "montaña" (como borrador)**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ascenso al Tourmalet",
    "description": "Clásica subida al Col du Tourmalet. Solo borrador por ahora.",
    "start_date": "2024-08-20",
    "distance_km": 45.0,
    "tags": ["montaña", "puerto"]
  }'
```

Save `trip_id` as `TRIP3_ID`

**Trip 4: Touring sin tags específicos**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Camino de Santiago",
    "description": "Última etapa del Camino de Santiago en bicicleta desde Sarria hasta Santiago de Compostela.",
    "start_date": "2024-09-10",
    "end_date": "2024-09-15",
    "distance_km": 115.0,
    "tags": ["touring", "camino"]
  }'
```

Save `trip_id` as `TRIP4_ID`

---

### Step 2: Publish Some Trips

**Publish Trip 1 (Bikepacking)**

```bash
curl -X POST "http://localhost:8000/trips/$TRIP1_ID/publish" \
  -H "Authorization: Bearer $TOKEN"
```

**Publish Trip 2 (Gravel)**

```bash
curl -X POST "http://localhost:8000/trips/$TRIP2_ID/publish" \
  -H "Authorization: Bearer $TOKEN"
```

**Leave Trip 3 as DRAFT** (no publicar)

**Publish Trip 4 (Touring)**

```bash
curl -X POST "http://localhost:8000/trips/$TRIP4_ID/publish" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Step 3: Test GET /tags Endpoint

**Get all available tags (ordered by usage count)**

```bash
curl -X GET "http://localhost:8000/tags" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "tag_id": "...",
        "name": "bikepacking",
        "normalized": "bikepacking",
        "usage_count": 1,
        "created_at": "2024-..."
      },
      {
        "tag_id": "...",
        "name": "montaña",
        "normalized": "montaña",
        "usage_count": 2,
        "created_at": "2024-..."
      },
      {
        "tag_id": "...",
        "name": "gravel",
        "normalized": "gravel",
        "usage_count": 1,
        "created_at": "2024-..."
      },
      // ... otros tags
    ],
    "count": 7
  },
  "error": null
}
```

**Validation:**
- ✅ "montaña" should have `usage_count: 2` (used in Trip1 and Trip3)
- ✅ Tags ordered by usage_count descending (most popular first)
- ✅ All 7 unique tags present

---

### Step 4: Test GET /users/{username}/trips - No Filters

**Get all trips for user (default: all statuses)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "...",
        "title": "Camino de Santiago",
        "status": "PUBLISHED",
        "tags": ["touring", "camino"],
        // ...
      },
      {
        "trip_id": "...",
        "title": "Ascenso al Tourmalet",
        "status": "DRAFT",
        "tags": ["montaña", "puerto"],
        // ...
      },
      {
        "trip_id": "...",
        "title": "Ruta Gravel Costa Brava",
        "status": "PUBLISHED",
        "tags": ["gravel", "costa"],
        // ...
      },
      {
        "trip_id": "...",
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED",
        "tags": ["bikepacking", "montaña"],
        // ...
      }
    ],
    "count": 4,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Validation:**
- ✅ All 4 trips returned (PUBLISHED + DRAFT)
- ✅ Ordered by `created_at` descending (newest first)
- ✅ Each trip includes `tags` array

---

### Step 5: Test Tag Filtering (Case-Insensitive)

**Filter by tag "montaña" (should return Trip1 and Trip3)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=montaña" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "...",
        "title": "Ascenso al Tourmalet",
        "status": "DRAFT",
        "tags": ["montaña", "puerto"]
      },
      {
        "trip_id": "...",
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED",
        "tags": ["bikepacking", "montaña"]
      }
    ],
    "count": 2,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Test case-insensitivity:**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=MONTAÑA" \
  -H "Authorization: Bearer $TOKEN"
```

Should return **same 2 trips** (case-insensitive match)

**Filter by tag "gravel" (should return only Trip2)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=gravel" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only 1 trip with tag "gravel"

**Filter by non-existent tag "carretera"**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=carretera" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Empty trips array `"count": 0`

---

### Step 6: Test Status Filtering

**Get only PUBLISHED trips**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?status=PUBLISHED" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "title": "Camino de Santiago",
        "status": "PUBLISHED"
      },
      {
        "title": "Ruta Gravel Costa Brava",
        "status": "PUBLISHED"
      },
      {
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED"
      }
    ],
    "count": 3,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Validation:**
- ✅ Only 3 trips (Trip1, Trip2, Trip4)
- ✅ Trip3 (DRAFT) not included

**Get only DRAFT trips**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?status=DRAFT" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only 1 trip (Trip3 - "Ascenso al Tourmalet")

---

### Step 7: Test Combined Filters (Tag + Status)

**Get PUBLISHED trips with tag "montaña"**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=montaña&status=PUBLISHED" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED",
        "tags": ["bikepacking", "montaña"]
      }
    ],
    "count": 1,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Validation:**
- ✅ Only Trip1 returned (PUBLISHED + has "montaña" tag)
- ✅ Trip3 excluded (has "montaña" but is DRAFT)

---

### Step 8: Test Pagination

**Get trips with limit=2**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?limit=2" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only 2 trips (first page)

**Get next page with offset=2**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?limit=2&offset=2" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Next 2 trips (second page)

---

### Step 9: Test Edge Cases

**Non-existent user**

```bash
curl -X GET "http://localhost:8000/users/nonexistent_user/trips" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Usuario 'nonexistent_user' no encontrado"
  }
}
```

**Status Code:** 404

**Invalid limit (>100)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?limit=150" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Validation error (limit must be ≤ 100)

**Invalid offset (negative)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?offset=-5" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Validation error (offset must be ≥ 0)

---

## Automated Test Script

Un script automatizado completo está disponible en `backend/scripts/test_tags.sh`.

### Uso del Script

**Requisitos previos:**

- Servidor corriendo en `localhost:8000`
- Git Bash o terminal con soporte bash (Windows)

**Ejecución:**

```bash
cd backend

# Dar permisos de ejecución (Linux/Mac)
chmod +x scripts/test_tags.sh

# Ejecutar script
bash scripts/test_tags.sh
```

**El script te pedirá:**

1. Email del usuario de prueba
2. Password del usuario

**Luego ejecutará automáticamente:**

- ✅ Login y obtención de token
- ✅ Creación de 4 trips con diferentes tags
- ✅ Publicación de algunos trips (otros quedan DRAFT)
- ✅ Filtrado por tags (case-insensitive)
- ✅ Filtrado por status (DRAFT/PUBLISHED)
- ✅ Filtros combinados (tag + status)
- ✅ Paginación (limit/offset)
- ✅ Listado de tags con popularidad
- ✅ Limpieza opcional de datos de prueba

**Output esperado:**

```text
ℹ === STEP 1: Login ===
✓ Login exitoso como testuser

ℹ === STEP 2: Crear trips con tags ===
✓ Trip 1 creado: 550e8400-e29b-41d4-a716-446655440000
✓ Trip 2 creado: 550e8400-e29b-41d4-a716-446655440001
✓ Trip 3 creado: 550e8400-e29b-41d4-a716-446655440002
✓ Trip 4 creado: 550e8400-e29b-41d4-a716-446655440003

ℹ === STEP 4: Filtrado por tags (case-insensitive) ===
→ Test: Filtrar por tag 'montaña' (lowercase)
✓ Encontrados: 2 trips (esperado: 2 - trip1 y trip3)
→ Test: Filtrar por tag 'MONTAÑA' (uppercase)
✓ Encontrados: 2 trips (esperado: 2 - case insensitive)

ℹ === STEP 8: Listado de tags con popularidad ===
→ Test: Obtener todos los tags disponibles
✓ Tag: montaña (usado en 2 trips)
✓ Tag: aventura (usado en 1 trips)
✓ Tag: playa (usado en 1 trips)

ℹ === RESUMEN DE TESTS ===
✓ Creación de trips con tags
✓ Filtrado case-insensitive por tags
✓ Filtrado por status (DRAFT/PUBLISHED)
✓ Filtros combinados (tag + status)
✓ Paginación con limit/offset
✓ Listado de tags con popularidad

✓ Tests completados exitosamente!
