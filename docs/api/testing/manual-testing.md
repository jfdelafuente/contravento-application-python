# Manual Testing Guide - ContraVento API

Esta guía proporciona comandos `curl` para probar manualmente todos los endpoints de la API de ContraVento.

**Migrated from**: `backend/docs/api/MANUAL_TESTING.md`

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
poetry run python scripts/user-mgmt/create_verified_user.py
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

### 4. Editar trip

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

### 5. Eliminar trip

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

---

## Endpoints de Photo Management

### 1. Upload Photo

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

### 2. Reorder Photos

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

### 3. Delete Photo

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
poetry run python scripts/user-mgmt/create_verified_user.py
```

### Debugging con verbose output

Añade `-v` a curl para ver detalles de la request/response:

```bash
curl -v -X POST "$API_URL/trips/$TRIP_ID/photos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@test_photo.jpg"
```

---

## Documentación Relacionada

- **[API Overview](../README.md)** - API documentation hub
- **[OpenAPI Contracts](../contracts/)** - YAML schema definitions
- **[Postman Guide](postman-guide.md)** - Postman/Insomnia testing
- **[Authentication](../authentication.md)** - JWT authentication flow

---

**Last Updated**: 2026-02-06 (Migrated from backend/docs/api/)
**API Version**: 0.4.0
