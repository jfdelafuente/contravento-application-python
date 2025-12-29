# Postman/Insomnia Collection - Travel Diary API

Esta guía proporciona la configuración para importar y usar la colección de Travel Diary en Postman o Insomnia.

## Tabla de Contenidos

- [Importar Colección](#importar-colección)
- [Variables de Entorno](#variables-de-entorno)
- [Flujo de Testing](#flujo-de-testing)
- [Exportar Colección JSON](#exportar-colección-json)

---

## Importar Colección

### Postman

1. Abrir Postman
2. Click en "Import" (arriba izquierda)
3. Seleccionar tab "Raw text"
4. Copiar y pegar el JSON de la colección (ver abajo)
5. Click "Import"

### Insomnia

1. Abrir Insomnia
2. Click en "Create" → "Import From" → "Clipboard"
3. Copiar y pegar el JSON de la colección (ver abajo)
4. Click "Scan"
5. Click "Import"

---

## Variables de Entorno

### Postman Environment

Crear un nuevo environment con estas variables:

```json
{
  "name": "ContraVento - Travel Diary",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "default",
      "enabled": true
    },
    {
      "key": "access_token",
      "value": "",
      "type": "default",
      "enabled": true
    },
    {
      "key": "trip_id",
      "value": "",
      "type": "default",
      "enabled": true
    },
    {
      "key": "photo1_id",
      "value": "",
      "type": "default",
      "enabled": true
    },
    {
      "key": "photo2_id",
      "value": "",
      "type": "default",
      "enabled": true
    },
    {
      "key": "photo3_id",
      "value": "",
      "type": "default",
      "enabled": true
    }
  ]
}
```

### Auto-Update Variables con Scripts

En Postman, puedes actualizar automáticamente las variables después de cada request usando scripts en la pestaña "Tests":

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

## Exportar Colección JSON

### Postman Collection v2.1 (Completa)

```json
{
  "info": {
    "name": "ContraVento - Travel Diary",
    "description": "API endpoints for Travel Diary feature (Photo Gallery)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "version": "0.2.0"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Login",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const response = pm.response.json();",
                  "",
                  "if (response.success && response.data.access_token) {",
                  "    pm.environment.set('access_token', response.data.access_token);",
                  "    console.log('Access token saved');",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"TestPass123!\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/login",
              "host": ["{{base_url}}"],
              "path": ["auth", "login"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Trips",
      "item": [
        {
          "name": "Create Trip",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const response = pm.response.json();",
                  "",
                  "if (response.success && response.data.trip_id) {",
                  "    pm.environment.set('trip_id', response.data.trip_id);",
                  "    console.log('Trip ID saved:', response.data.trip_id);",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Vía Verde del Aceite\",\n  \"description\": \"Un recorrido espectacular de 127 kilómetros entre Jaén y Córdoba, atravesando olivares centenarios y pueblos con encanto. Perfecto para cicloturismo.\",\n  \"start_date\": \"2024-05-15\",\n  \"end_date\": \"2024-05-17\",\n  \"distance_km\": 127.3,\n  \"difficulty\": \"moderate\",\n  \"locations\": [\n    {\"name\": \"Jaén\"},\n    {\"name\": \"Baeza\"},\n    {\"name\": \"Córdoba\"}\n  ],\n  \"tags\": [\"vías verdes\", \"andalucía\", \"olivares\"]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        },
        {
          "name": "Get Trip",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}"]
            }
          },
          "response": []
        },
        {
          "name": "Publish Trip",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/publish",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "publish"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Photos",
      "item": [
        {
          "name": "Upload Photo",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const response = pm.response.json();",
                  "",
                  "if (response.success && response.data.photo_id) {",
                  "    const photoId = response.data.photo_id;",
                  "    ",
                  "    if (!pm.environment.get('photo1_id')) {",
                  "        pm.environment.set('photo1_id', photoId);",
                  "        console.log('Photo 1 ID saved:', photoId);",
                  "    } else if (!pm.environment.get('photo2_id')) {",
                  "        pm.environment.set('photo2_id', photoId);",
                  "        console.log('Photo 2 ID saved:', photoId);",
                  "    } else if (!pm.environment.get('photo3_id')) {",
                  "        pm.environment.set('photo3_id', photoId);",
                  "        console.log('Photo 3 ID saved:', photoId);",
                  "    }",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "photo",
                  "type": "file",
                  "src": []
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/photos",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "photos"]
            }
          },
          "response": []
        },
        {
          "name": "Reorder Photos",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"photo_order\": [\n    \"{{photo3_id}}\",\n    \"{{photo1_id}}\",\n    \"{{photo2_id}}\"\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/photos/reorder",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "photos", "reorder"]
            }
          },
          "response": []
        },
        {
          "name": "Delete Photo",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/photos/{{photo2_id}}",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "photos", "{{photo2_id}}"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Validation Tests",
      "item": [
        {
          "name": "Upload Invalid Format (should fail 400)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "photo",
                  "type": "file",
                  "src": [],
                  "description": "Upload a .txt file to test validation"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/photos",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "photos"]
            }
          },
          "response": []
        },
        {
          "name": "Reorder with Invalid IDs (should fail 400)",
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"photo_order\": [\n    \"fake-id-1\",\n    \"fake-id-2\"\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/photos/reorder",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "photos", "reorder"]
            }
          },
          "response": []
        },
        {
          "name": "Delete Non-Existent Photo (should fail 404)",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/photos/00000000-0000-0000-0000-000000000000",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "photos", "00000000-0000-0000-0000-000000000000"]
            }
          },
          "response": []
        },
        {
          "name": "Upload without Auth (should fail 401)",
          "request": {
            "method": "POST",
            "header": [],
            "body": {
              "mode": "formdata",
              "formdata": [
                {
                  "key": "photo",
                  "type": "file",
                  "src": []
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/trips/{{trip_id}}/photos",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_id}}", "photos"]
            }
          },
          "response": []
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

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

- **Manual Testing con curl**: `MANUAL_TESTING.md`
- **OpenAPI Spec**: `contracts/trips-api.yaml`
- **Especificación**: `spec.md`

---

**Última actualización:** 2024-12-28
**Versión:** 0.2.0 (User Story 2 - Photo Gallery)
