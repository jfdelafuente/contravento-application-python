# Manual Testing Guide - Travel Diary API

Esta guía proporciona comandos `curl` para probar manualmente todos los endpoints de la API del Travel Diary (Trip CRUD + Photo Management).

## Tabla de Contenidos

- [Prerequisitos](#prerequisitos)
- [Configuración Inicial](#configuración-inicial)
- [Endpoints de Trip CRUD](#endpoints-de-trip-crud)
- [Endpoints de Photo Management](#endpoints-de-photo-management)
- [Casos de Prueba Completos](#casos-de-prueba-completos)
- [Troubleshooting](#troubleshooting)

---

## Prerequisitos

### 1. Servidor en ejecución

```bash
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Usuario de prueba creado

```bash
cd backend
poetry run python scripts/create_verified_user.py
```

Esto crea los usuarios por defecto:
- **testuser** / `test@example.com` / `TestPass123!`
- **maria_garcia** / `maria@example.com` / `SecurePass456!`

### 3. Variables de entorno

Configura estas variables para facilitar el testing:

```bash
# Linux/Mac
export API_URL="http://localhost:8000"

# Windows PowerShell
$env:API_URL="http://localhost:8000"

# Windows CMD
set API_URL=http://localhost:8000
```

---

## Configuración Inicial

### 1. Login y obtener token

```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "error": null
}
```

**Guardar el token:**

```bash
# Linux/Mac
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Windows PowerShell
$env:TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Windows CMD
set TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Endpoints de Trip CRUD

### 1. Crear un trip (draft)

```bash
curl -X POST "$API_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Vía Verde del Aceite",
    "description": "Un recorrido espectacular de 127 kilómetros entre Jaén y Córdoba, atravesando olivares centenarios y pueblos con encanto. Perfecto para cicloturismo.",
    "start_date": "2024-05-15",
    "end_date": "2024-05-17",
    "distance_km": 127.3,
    "difficulty": "moderate",
    "locations": [
      {"name": "Jaén"},
      {"name": "Baeza"},
      {"name": "Córdoba"}
    ],
    "tags": ["vías verdes", "andalucía", "olivares"]
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Vía Verde del Aceite",
    "description": "Un recorrido espectacular...",
    "status": "draft",
    "start_date": "2024-05-15",
    "end_date": "2024-05-17",
    "distance_km": 127.3,
    "difficulty": "moderate",
    "created_at": "2024-12-28T12:00:00Z",
    "updated_at": "2024-12-28T12:00:00Z",
    "published_at": null,
    "photos": [],
    "locations": [
      {
        "location_id": "loc-1",
        "name": "Jaén",
        "sequence": 0
      },
      {
        "location_id": "loc-2",
        "name": "Baeza",
        "sequence": 1
      },
      {
        "location_id": "loc-3",
        "name": "Córdoba",
        "sequence": 2
      }
    ],
    "tags": [
      {"tag_id": "tag-1", "name": "vías verdes"},
      {"tag_id": "tag-2", "name": "andalucía"},
      {"tag_id": "tag-3", "name": "olivares"}
    ]
  },
  "error": null
}
```

**Guardar el trip_id:**

```bash
# Linux/Mac
export TRIP_ID="550e8400-e29b-41d4-a716-446655440000"

# Windows PowerShell
$env:TRIP_ID="550e8400-e29b-41d4-a716-446655440000"

# Windows CMD
set TRIP_ID=550e8400-e29b-41d4-a716-446655440000
```

### 2. Obtener trip por ID

```bash
curl -X GET "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Publicar trip

```bash
curl -X POST "$API_URL/trips/$TRIP_ID/publish" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "published",
    "published_at": "2024-12-28T12:05:00Z"
  },
  "error": null
}
```

### 4. Editar trip (FR-016, FR-020) ⭐ NUEVO

```bash
curl -X PUT "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Vía Verde del Aceite - Actualizado",
    "description": "Un recorrido espectacular de 127 kilómetros entre Jaén y Córdoba. ACTUALIZADO: Añadido tramo nocturno espectacular bajo la luna llena.",
    "distance_km": 135.5,
    "client_updated_at": "2024-12-28T12:00:00Z"
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Vía Verde del Aceite - Actualizado",
    "description": "Un recorrido espectacular de 127 kilómetros entre Jaén y Córdoba. ACTUALIZADO: Añadido tramo nocturno espectacular bajo la luna llena.",
    "distance_km": 135.5,
    "updated_at": "2024-12-28T12:10:00Z",
    ...
  },
  "error": null
}
```

#### Actualización parcial (solo algunos campos)

```bash
# Solo actualizar título y distancia
curl -X PUT "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Nuevo Título",
    "distance_km": 150.0,
    "client_updated_at": "2024-12-28T12:10:00Z"
  }'
```

#### Validación: Conflicto de edición concurrente (Optimistic Locking)

```bash
# Usar timestamp antiguo (debe fallar con 409)
curl -X PUT "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Intento de actualización obsoleta",
    "client_updated_at": "2024-01-01T00:00:00Z"
  }'
```

**Respuesta esperada (error 409):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "CONFLICT",
    "message": "El viaje ha sido modificado por otra persona. Por favor, recarga y vuelve a intentarlo."
  }
}
```

#### Validación: Sin permisos (no eres el owner)

```bash
# Login como otro usuario
USER2_TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "maria@example.com", "password": "SecurePass456!"}' \
  | jq -r '.data.access_token')

# Intentar editar trip de otro usuario (debe fallar con 403)
curl -X PUT "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $USER2_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Intento de edición no autorizada"
  }'
```

**Respuesta esperada (error 403):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "No tienes permiso para editar este viaje"
  }
}
```

#### Validación: Trip no encontrado

```bash
curl -X PUT "$API_URL/trips/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Nuevo título"}'
```

**Respuesta esperada (error 404):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Viaje no encontrado"
  }
}
```

### 5. Eliminar trip (FR-017, FR-018) ⭐ NUEVO

```bash
curl -X DELETE "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "message": "Viaje eliminado correctamente",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "error": null
}
```

#### Verificar que el trip ya no existe

```bash
curl -X GET "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (error 404):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Viaje no encontrado"
  }
}
```

#### Validación: Sin permisos (no eres el owner)

```bash
# Login como otro usuario
USER2_TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "maria@example.com", "password": "SecurePass456!"}' \
  | jq -r '.data.access_token')

# Intentar eliminar trip de otro usuario (debe fallar con 403)
curl -X DELETE "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $USER2_TOKEN"
```

**Respuesta esperada (error 403):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "FORBIDDEN",
    "message": "No tienes permiso para eliminar este viaje"
  }
}
```

#### Validación: Trip no encontrado

```bash
curl -X DELETE "$API_URL/trips/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (error 404):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Viaje no encontrado"
  }
}
```

#### Verificar actualización de estadísticas del usuario

Después de eliminar un trip, las estadísticas del usuario deben actualizarse automáticamente:

```bash
# Obtener estadísticas del usuario
curl -X GET "$API_URL/users/me/stats" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "total_trips": 0,
    "published_trips": 0,
    "draft_trips": 0,
    "total_distance_km": 0.0,
    "total_photos": 0
  },
  "error": null
}
```

---

## Endpoints de Photo Management

### 1. Upload Photo (FR-009, FR-010, FR-011)

#### Crear una imagen de prueba (Linux/Mac con ImageMagick)

```bash
# Crear imagen de prueba 1200x800px
convert -size 1200x800 xc:red test_photo1.jpg

# O crear con texto
convert -size 1200x800 xc:skyblue \
  -gravity center \
  -pointsize 72 \
  -annotate +0+0 "Foto 1" \
  test_photo1.jpg
```

#### Upload con curl

```bash
curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_photo1.jpg"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "photo_id": "abc123-456def-789ghi",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "photo_url": "/storage/trip_photos/2024/12/550e8400.../abc123_optimized.jpg",
    "thumb_url": "/storage/trip_photos/2024/12/550e8400.../abc123_thumb.jpg",
    "order": 0
  },
  "error": null
}
```

**Guardar el photo_id:**

```bash
# Linux/Mac
export PHOTO1_ID="abc123-456def-789ghi"

# Windows PowerShell
$env:PHOTO1_ID="abc123-456def-789ghi"
```

#### Upload múltiples fotos

```bash
# Crear más fotos de prueba
convert -size 1200x800 xc:green -gravity center -pointsize 72 -annotate +0+0 "Foto 2" test_photo2.jpg
convert -size 1200x800 xc:blue -gravity center -pointsize 72 -annotate +0+0 "Foto 3" test_photo3.jpg

# Upload foto 2
curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_photo2.jpg"

# Guardar photo_id de respuesta
export PHOTO2_ID="def456-789ghi-012jkl"

# Upload foto 3
curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_photo3.jpg"

# Guardar photo_id de respuesta
export PHOTO3_ID="ghi789-012jkl-345mno"
```

#### Validación: Formato inválido

```bash
# Crear archivo de texto
echo "Este no es una imagen" > fake_photo.txt

# Intentar upload (debe fallar con 400)
curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@fake_photo.txt"
```

**Respuesta esperada (error 400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Formato de archivo no soportado. Usa JPG, PNG o WebP"
  }
}
```

#### Validación: Archivo muy grande

```bash
# Crear imagen grande (>10MB)
convert -size 5000x5000 xc:red large_photo.jpg

# Intentar upload (debe fallar con 400)
curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@large_photo.jpg"
```

**Respuesta esperada (error 400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La foto excede el tamaño máximo de 10MB"
  }
}
```

#### Validación: Límite de 20 fotos

```bash
# Script para subir 20 fotos (límite máximo)
for i in {1..20}; do
  convert -size 800x600 xc:blue -gravity center -pointsize 48 -annotate +0+0 "Foto $i" photo$i.jpg
  curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
    -H "Authorization: Bearer $TOKEN" \
    -F "photo=@photo$i.jpg"
  echo ""
done

# Intentar subir la foto 21 (debe fallar con 400)
convert -size 800x600 xc:red -gravity center -pointsize 48 -annotate +0+0 "Foto 21" photo21.jpg
curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@photo21.jpg"
```

**Respuesta esperada (error 400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Has alcanzado el límite de 20 fotos por viaje"
  }
}
```

### 2. Reorder Photos (FR-012)

```bash
curl -X PUT "$API_URL/trips/$TRIP_ID/photos/reorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "photo_order": [
      "'"$PHOTO3_ID"'",
      "'"$PHOTO1_ID"'",
      "'"$PHOTO2_ID"'"
    ]
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "message": "Fotos reordenadas correctamente"
  },
  "error": null
}
```

#### Verificar nuevo orden

```bash
curl -X GET "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.data.photos | sort_by(.order)'
```

**Respuesta esperada (orden 0, 1, 2):**
```json
[
  {
    "photo_id": "ghi789-012jkl-345mno",
    "photo_url": "/storage/.../ghi789_optimized.jpg",
    "thumb_url": "/storage/.../ghi789_thumb.jpg",
    "order": 0
  },
  {
    "photo_id": "abc123-456def-789ghi",
    "photo_url": "/storage/.../abc123_optimized.jpg",
    "thumb_url": "/storage/.../abc123_thumb.jpg",
    "order": 1
  },
  {
    "photo_id": "def456-789ghi-012jkl",
    "photo_url": "/storage/.../def456_optimized.jpg",
    "thumb_url": "/storage/.../def456_thumb.jpg",
    "order": 2
  }
]
```

#### Validación: IDs inválidos

```bash
curl -X PUT "$API_URL/trips/$TRIP_ID/photos/reorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "photo_order": [
      "fake-id-1",
      "fake-id-2"
    ]
  }'
```

**Respuesta esperada (error 400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "ID de foto inválido: la lista contiene fotos que no pertenecen a este viaje"
  }
}
```

#### Validación: Cantidad incorrecta

```bash
# Intentar reordenar con solo 2 IDs cuando hay 3 fotos
curl -X PUT "$API_URL/trips/$TRIP_ID/photos/reorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "photo_order": [
      "'"$PHOTO1_ID"'",
      "'"$PHOTO2_ID"'"
    ]
  }'
```

**Respuesta esperada (error 400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Cantidad inválida de fotos. El viaje tiene 3 fotos pero se proporcionaron 2"
  }
}
```

### 3. Delete Photo (FR-013)

```bash
curl -X DELETE "$API_URL/trips/$TRIP_ID/photos/$PHOTO2_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "message": "Foto eliminada correctamente"
  },
  "error": null
}
```

#### Verificar reordenamiento automático

Después de eliminar la foto del medio (order=1), las fotos restantes deben reordenarse:

```bash
curl -X GET "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.data.photos | sort_by(.order)'
```

**Respuesta esperada (orden 0, 1 - sin gaps):**
```json
[
  {
    "photo_id": "ghi789-012jkl-345mno",
    "order": 0
  },
  {
    "photo_id": "abc123-456def-789ghi",
    "order": 1
  }
]
```

#### Validación: Foto no encontrada

```bash
curl -X DELETE "$API_URL/trips/$TRIP_ID/photos/00000000-0000-0000-0000-000000000000" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (error 404):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Foto no encontrada"
  }
}
```

#### Validación: Sin autorización

```bash
# Intentar eliminar sin token
curl -X DELETE "$API_URL/trips/$TRIP_ID/photos/$PHOTO1_ID"
```

**Respuesta esperada (error 401):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token de autenticación inválido o expirado"
  }
}
```

---

## Casos de Prueba Completos

### Flujo Completo: Crear Trip con Galería de Fotos

Este script completo crea un trip, sube 5 fotos, las reordena, elimina una, y verifica el resultado final.

```bash
#!/bin/bash

# 1. Login
echo "=== 1. Login ==="
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.access_token')
echo "Token obtenido: ${TOKEN:0:50}..."

# 2. Crear trip
echo -e "\n=== 2. Crear Trip ==="
TRIP_RESPONSE=$(curl -s -X POST "$API_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Camino de Santiago - Etapa Sarria-Santiago",
    "description": "Última etapa del Camino Francés. 115 kilómetros divididos en 5 días, atravesando bosques gallegos y pueblos con encanto. Una experiencia única llena de espiritualidad y compañerismo.",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "distance_km": 115.2,
    "difficulty": "moderate",
    "locations": [
      {"name": "Sarria"},
      {"name": "Portomarín"},
      {"name": "Palas de Rei"},
      {"name": "Arzúa"},
      {"name": "Santiago de Compostela"}
    ],
    "tags": ["camino", "peregrinación", "galicia"]
  }')

TRIP_ID=$(echo $TRIP_RESPONSE | jq -r '.data.trip_id')
echo "Trip creado: $TRIP_ID"

# 3. Crear fotos de prueba
echo -e "\n=== 3. Crear fotos de prueba ==="
for i in {1..5}; do
  convert -size 1200x800 \
    gradient:blue-green \
    -gravity center \
    -pointsize 72 \
    -fill white \
    -annotate +0+0 "Etapa $i" \
    photo_camino_$i.jpg
done
echo "5 fotos creadas"

# 4. Upload fotos
echo -e "\n=== 4. Upload fotos ==="
PHOTO_IDS=()
for i in {1..5}; do
  echo "Uploading foto $i..."
  PHOTO_RESPONSE=$(curl -s -X POST "$API_URL/trips/$TRIP_ID/photos" \
    -H "Authorization: Bearer $TOKEN" \
    -F "photo=@photo_camino_$i.jpg")

  PHOTO_ID=$(echo $PHOTO_RESPONSE | jq -r '.data.photo_id')
  PHOTO_IDS+=($PHOTO_ID)
  echo "  Photo ID: $PHOTO_ID (order: $(echo $PHOTO_RESPONSE | jq -r '.data.order'))"
done

# 5. Verificar fotos subidas
echo -e "\n=== 5. Verificar trip con fotos ==="
curl -s -X GET "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '{
    trip_id: .data.trip_id,
    title: .data.title,
    photo_count: (.data.photos | length),
    photos: (.data.photos | map({photo_id, order}))
  }'

# 6. Reordenar fotos (invertir orden)
echo -e "\n=== 6. Reordenar fotos (invertir) ==="
REVERSED_ORDER=$(printf '"%s",' "${PHOTO_IDS[@]}" | tac -s, | sed 's/,$//')
curl -s -X PUT "$API_URL/trips/$TRIP_ID/photos/reorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"photo_order\": [$REVERSED_ORDER]}" \
  | jq '.data.message'

# 7. Verificar nuevo orden
echo -e "\n=== 7. Verificar nuevo orden ==="
curl -s -X GET "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.data.photos | sort_by(.order) | map({photo_id, order})'

# 8. Eliminar foto del medio (índice 2)
echo -e "\n=== 8. Eliminar foto del medio ==="
MIDDLE_PHOTO_ID=${PHOTO_IDS[2]}
curl -s -X DELETE "$API_URL/trips/$TRIP_ID/photos/$MIDDLE_PHOTO_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.data.message'

# 9. Verificar reordenamiento automático
echo -e "\n=== 9. Verificar reordenamiento automático ==="
curl -s -X GET "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '{
    photo_count: (.data.photos | length),
    photos: (.data.photos | sort_by(.order) | map({photo_id, order})),
    orders_sequential: (.data.photos | map(.order) | sort == [0,1,2,3])
  }'

# 10. Publicar trip
echo -e "\n=== 10. Publicar trip ==="
curl -s -X POST "$API_URL/trips/$TRIP_ID/publish" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '{status: .data.status, published_at: .data.published_at}'

echo -e "\n=== Test completado ==="
```

### Validación de Permisos

```bash
#!/bin/bash

# 1. Login usuario 1 (testuser)
USER1_TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}' \
  | jq -r '.data.access_token')

# 2. Login usuario 2 (maria_garcia)
USER2_TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "maria@example.com", "password": "SecurePass456!"}' \
  | jq -r '.data.access_token')

# 3. Usuario 1 crea trip
TRIP_ID=$(curl -s -X POST "$API_URL/trips" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Viaje Privado",
    "description": "Este es mi viaje privado que solo yo debería poder modificar.",
    "start_date": "2024-07-01"
  }' | jq -r '.data.trip_id')

echo "Trip creado por usuario 1: $TRIP_ID"

# 4. Usuario 1 sube foto
convert -size 800x600 xc:blue test_photo.jpg
PHOTO_ID=$(curl -s -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $USER1_TOKEN" \
  -F "photo=@test_photo.jpg" \
  | jq -r '.data.photo_id')

echo "Foto subida por usuario 1: $PHOTO_ID"

# 5. Usuario 2 intenta eliminar la foto (debe fallar con 403)
echo -e "\nUsuario 2 intenta eliminar foto de usuario 1:"
curl -s -X DELETE "$API_URL/trips/$TRIP_ID/photos/$PHOTO_ID" \
  -H "Authorization: Bearer $USER2_TOKEN" \
  | jq '{success, error}'

# 6. Usuario 2 intenta subir foto al trip de usuario 1 (debe fallar con 403)
echo -e "\nUsuario 2 intenta subir foto al trip de usuario 1:"
curl -s -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $USER2_TOKEN" \
  -F "photo=@test_photo.jpg" \
  | jq '{success, error}'
```

---

## Troubleshooting

### Error: "Connection refused"

```bash
# Verificar que el servidor está corriendo
curl -s http://localhost:8000/health | jq
```

**Solución:** Asegúrate de que el servidor está en ejecución:
```bash
cd backend
poetry run uvicorn src.main:app --reload
```

### Error: "Token inválido o expirado"

El token de acceso expira después de 15 minutos.

**Solución:** Vuelve a hacer login:
```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'
```

### Error: "Foto no encontrada" al acceder a archivos

Los archivos de fotos se almacenan en `storage/trip_photos/`.

**Verificar archivos:**
```bash
# Linux/Mac
ls -lR backend/storage/trip_photos/

# Windows
dir /s backend\storage\trip_photos\
```

### Limpiar datos de prueba

```bash
# Eliminar base de datos SQLite de desarrollo
rm backend/contravento.db

# Recrear base de datos
cd backend
poetry run alembic upgrade head

# Recrear usuarios de prueba
poetry run python scripts/create_verified_user.py
```

### Debugging con verbose output

Añade `-v` a curl para ver detalles de la request/response:

```bash
curl -v -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_photo.jpg"
```

### Validar respuestas JSON

Usa `jq` para formatear y validar JSON:

```bash
# Formatear respuesta
curl -s "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.'

# Extraer solo errores
curl -s "$API_URL/trips/invalid-id" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.error'

# Contar fotos
curl -s "$API_URL/trips/$TRIP_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.data.photos | length'
```

---

## Referencia Rápida

### Variables de entorno requeridas

```bash
export API_URL="http://localhost:8000"
export TOKEN="<access_token_from_login>"
export TRIP_ID="<trip_id_from_create_trip>"
export PHOTO1_ID="<photo_id_from_upload>"
export PHOTO2_ID="<photo_id_from_upload>"
export PHOTO3_ID="<photo_id_from_upload>"
```

### Comandos básicos

```bash
# Login
curl -X POST "$API_URL/auth/login" -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'

# Crear trip
curl -X POST "$API_URL/trips" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{...}'

# Upload foto
curl -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" -F "photo=@test.jpg"

# Reordenar fotos
curl -X PUT "$API_URL/trips/$TRIP_ID/photos/reorder" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"photo_order": ["id1", "id2", "id3"]}'

# Eliminar foto
curl -X DELETE "$API_URL/trips/$TRIP_ID/photos/$PHOTO_ID" \
  -H "Authorization: Bearer $TOKEN"

# Obtener trip
curl -X GET "$API_URL/trips/$TRIP_ID" -H "Authorization: Bearer $TOKEN"
```

---

## Documentación Relacionada

- **OpenAPI Spec**: `specs/002-travel-diary/contracts/trips-api.yaml`
- **Specification**: `specs/002-travel-diary/spec.md`
- **Implementation Plan**: `specs/002-travel-diary/plan.md`
- **Tasks**: `specs/002-travel-diary/tasks.md`
- **API Documentation**: http://localhost:8000/docs (cuando el servidor está corriendo)

---

**Última actualización:** 2025-12-30
**Versión:** 0.3.0 (User Story 3 - Edit/Delete Trips)
