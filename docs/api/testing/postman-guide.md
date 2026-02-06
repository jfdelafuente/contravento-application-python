# Postman/Insomnia Guide - ContraVento API

Esta guía proporciona la configuración para importar y usar las colecciones de ContraVento en Postman o Insomnia.

**Migrated from**: `backend/docs/api/POSTMAN_COLLECTION.md`

## Tabla de Contenidos

- [Importar Colección](#importar-colección)
- [Variables de Entorno](#variables-de-entorno)
- [Flujo de Testing](#flujo-de-testing)
- [Colecciones Disponibles](#colecciones-disponibles)
- [Tips para Testing Eficiente](#tips-para-testing-eficiente)
- [Troubleshooting](#troubleshooting)

---

## Importar Colección

### Postman

1. Abrir Postman
2. Click en "Import" (arriba izquierda)
3. Seleccionar tab "File"
4. Navegar a `docs/api/postman/collections/`
5. Seleccionar archivo `.postman_collection.json`
6. Click "Import"

### Insomnia

1. Abrir Insomnia
2. Click en "Create" → "Import From" → "File"
3. Navegar a `docs/api/postman/collections/`
4. Seleccionar archivo `.postman_collection.json`
5. Click "Scan"
6. Click "Import"

---

## Variables de Entorno

### Postman Environment

Importar el environment desde `docs/api/postman/environments/ContraVento-Local.postman_environment.json`:

**Variables incluidas**:
```json
{
  "base_url": "http://localhost:8000",
  "access_token": "",
  "trip_id": "",
  "photo1_id": "",
  "photo2_id": "",
  "photo3_id": ""
}
```

### Auto-Update Variables con Scripts

En Postman, las colecciones incluyen scripts automáticos que actualizan variables después de cada request:

**Login Request - Tests tab:**

```javascript
// Parse response
const response = pm.response.json();

// Save access token
if (response.success && response.data.access_token) {
    pm.environment.set("access_token", response.data.access_token);
    console.log("Access token saved:", response.data.access_token.substring(0, 20) + "...");
}
```

**Create Trip - Tests tab:**

```javascript
// Parse response
const response = pm.response.json();

// Save trip_id
if (response.success && response.data.trip_id) {
    pm.environment.set("trip_id", response.data.trip_id);
    console.log("Trip ID saved:", response.data.trip_id);
}
```

**Upload Photo - Tests tab:**

```javascript
// Parse response
const response = pm.response.json();

// Save photo_id to next available variable
if (response.success && response.data.photo_id) {
    const photoId = response.data.photo_id;

    // Try to store in photo1_id, photo2_id, photo3_id
    if (!pm.environment.get("photo1_id")) {
        pm.environment.set("photo1_id", photoId);
        console.log("Photo 1 ID saved:", photoId);
    } else if (!pm.environment.get("photo2_id")) {
        pm.environment.set("photo2_id", photoId);
        console.log("Photo 2 ID saved:", photoId);
    } else if (!pm.environment.get("photo3_id")) {
        pm.environment.set("photo3_id", photoId);
        console.log("Photo 3 ID saved:", photoId);
    }
}
```

---

## Flujo de Testing

### Paso 1: Login

**Request:** `POST {{base_url}}/auth/login`

**Body (JSON):**
```json
{
  "email": "test@example.com",
  "password": "TestPass123!"
}
```

**Headers:**
- `Content-Type: application/json`

**Expected Response (200):**
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

---

### Paso 2: Create Trip

**Request:** `POST {{base_url}}/trips`

**Body (JSON):**
```json
{
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
}
```

**Headers:**
- `Authorization: Bearer {{access_token}}`
- `Content-Type: application/json`

**Expected Response (201):**
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Vía Verde del Aceite",
    "status": "draft",
    "photos": [],
    "locations": [...],
    "tags": [...]
  },
  "error": null
}
```

---

### Paso 3: Upload Photo

**Request:** `POST {{base_url}}/trips/{{trip_id}}/photos`

**Body (form-data):**
- Key: `photo`
- Type: `File`
- Value: [Select image file]

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (201):**
```json
{
  "success": true,
  "data": {
    "photo_id": "abc123-456def-789ghi",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "photo_url": "/storage/trip_photos/2024/12/550e.../abc123_optimized.jpg",
    "thumb_url": "/storage/trip_photos/2024/12/550e.../abc123_thumb.jpg",
    "order": 0
  },
  "error": null
}
```

**Tip:** Subir 3 fotos para probar el reordenamiento.

---

### Paso 4: Get Trip with Photos

**Request:** `GET {{base_url}}/trips/{{trip_id}}`

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Vía Verde del Aceite",
    "photos": [
      {
        "photo_id": "abc123",
        "photo_url": "/storage/...",
        "thumb_url": "/storage/...",
        "order": 0
      },
      {
        "photo_id": "def456",
        "photo_url": "/storage/...",
        "thumb_url": "/storage/...",
        "order": 1
      },
      {
        "photo_id": "ghi789",
        "photo_url": "/storage/...",
        "thumb_url": "/storage/...",
        "order": 2
      }
    ]
  },
  "error": null
}
```

---

### Paso 5: Reorder Photos

**Request:** `PUT {{base_url}}/trips/{{trip_id}}/photos/reorder`

**Body (JSON):**
```json
{
  "photo_order": [
    "{{photo3_id}}",
    "{{photo1_id}}",
    "{{photo2_id}}"
  ]
}
```

**Headers:**
- `Authorization: Bearer {{access_token}}`
- `Content-Type: application/json`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Fotos reordenadas correctamente"
  },
  "error": null
}
```

---

### Paso 6: Delete Photo

**Request:** `DELETE {{base_url}}/trips/{{trip_id}}/photos/{{photo2_id}}`

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (200):**
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

### Paso 7: Publish Trip

**Request:** `POST {{base_url}}/trips/{{trip_id}}/publish`

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "published",
    "published_at": "2024-12-28T12:00:00Z"
  },
  "error": null
}
```

---

## Colecciones Disponibles

### ContraVento GPS Coordinates

**Location**: `docs/api/postman/collections/ContraVento_GPS_Coordinates.postman_collection.json`

**Features**:
- GPS trip creation with coordinates
- Location management
- GPX file upload testing
- Reverse geocoding validation

### ContraVento Travel Diary (Legacy)

**Location**: Available in collection file above

**Features**:
- Trip CRUD operations
- Photo gallery management
- Tags and filtering
- Validation tests

---

## Tips para Testing Eficiente

### 1. Pre-request Scripts

Puedes agregar validación automática en la pestaña "Pre-request Script":

```javascript
// Verificar que access_token existe
const token = pm.environment.get("access_token");
if (!token) {
    console.error("ERROR: Access token not found. Please run Login request first.");
}

// Verificar que trip_id existe (para requests de photos)
const tripId = pm.environment.get("trip_id");
if (!tripId) {
    console.error("ERROR: Trip ID not found. Please run Create Trip request first.");
}
```

### 2. Collection Runner

Para ejecutar toda la colección automáticamente:

**Postman:**
1. Click en la colección → "Run"
2. Seleccionar requests a ejecutar
3. Configurar delay entre requests (500ms recomendado)
4. Click "Run Collection"

**Insomnia:**
1. Click derecho en la colección → "Run Tests"

### 3. Visualizar Imágenes

No puedes ver las imágenes directamente en Postman/Insomnia, pero puedes:

1. Copiar la `photo_url` de la respuesta
2. Abrir en navegador: `http://localhost:8000/storage/trip_photos/...`

### 4. Limpiar Variables

Agregar un request de "Reset" al final:

```javascript
// Tests tab
pm.environment.unset("trip_id");
pm.environment.unset("photo1_id");
pm.environment.unset("photo2_id");
pm.environment.unset("photo3_id");
console.log("Environment variables cleared");
```

---

## Troubleshooting

### Error: "photo_id not set"

**Solución:** Asegúrate de que el script en "Tests" del request "Upload Photo" se ejecutó correctamente. Verifica en la consola de Postman.

### Error: "Unauthorized"

**Solución:** El token expiró (15 minutos). Vuelve a ejecutar el request "Login".

### Error: "Trip not found"

**Solución:** La variable `trip_id` no está configurada. Ejecuta el request "Create Trip" primero.

### File upload no funciona

**Insomnia:** Asegúrate de seleccionar "Multipart Form" en el dropdown del body.

**Postman:** Verifica que el key sea exactamente `photo` (case-sensitive).

---

## Documentación Relacionada

- **[Manual Testing](manual-testing.md)** - curl command reference
- **[API Overview](../README.md)** - API documentation hub
- **[OpenAPI Contracts](../contracts/)** - YAML schema definitions
- **[Authentication](../authentication.md)** - JWT authentication flow

---

**Last Updated**: 2026-02-06 (Migrated from backend/docs/api/)
**API Version**: 0.4.0
