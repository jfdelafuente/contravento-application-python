# Postman Collection - Cycling Types Management

Guía completa para testing de la gestión de tipos de ciclismo usando Postman o Insomnia.

## Tabla de Contenidos

- [Importar Colección](#importar-colección)
- [Variables de Entorno](#variables-de-entorno)
- [Flujos de Testing](#flujos-de-testing)
  - [Public Endpoints](#public-endpoints)
  - [Admin Endpoints](#admin-endpoints)
- [Colección JSON Completa](#colección-json-completa)
- [Troubleshooting](#troubleshooting)

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
3. Copiar y pegar el JSON de la colección
4. Click "Scan" → "Import"

---

## Variables de Entorno

### Environment Configuration

```json
{
  "name": "ContraVento - Cycling Types",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    },
    {
      "key": "access_token",
      "value": "",
      "enabled": true
    },
    {
      "key": "test_cycling_type_code",
      "value": "test-type",
      "enabled": true
    }
  ]
}
```

### Auto-Update Scripts

Los siguientes scripts se deben agregar en la pestaña "Tests" de cada request:

**Login Request (para obtener token):**
```javascript
const response = pm.response.json();

if (response.success && response.data.access_token) {
    pm.environment.set("access_token", response.data.access_token);
    console.log("Access token saved");
}
```

**Create Cycling Type:**
```javascript
const response = pm.response.json();

if (response.success && response.data) {
    pm.environment.set("test_cycling_type_code", response.data.code);
    console.log("Cycling type created:", response.data.code);
}
```

---

## Flujos de Testing

### Public Endpoints

#### 1. Listar Tipos Activos

```http
GET {{base_url}}/cycling-types
```

**Headers:**
```
Content-Type: application/json
```

**Expected Response (200 OK):**
```json
[
  {
    "code": "bikepacking",
    "display_name": "Bikepacking",
    "description": "Viajes de varios días en bicicleta con equipaje completo"
  },
  {
    "code": "mountain",
    "display_name": "Montaña (MTB)",
    "description": "Ciclismo de montaña en senderos y trails"
  },
  {
    "code": "road",
    "display_name": "Carretera",
    "description": "Ciclismo en carretera y asfalto"
  }
]
```

---

### Admin Endpoints

**IMPORTANTE**: Todos los endpoints admin requieren autenticación. Primero debes hacer login para obtener un `access_token`.

#### Prerequisito: Login

```http
POST {{base_url}}/auth/login
Content-Type: application/json

{
  "login": "testuser",
  "password": "TestPass123!"
}
```

**Guardar el `access_token` de la respuesta en las variables de entorno.**

---

#### 2. Listar Todos los Tipos (Admin)

```http
GET {{base_url}}/admin/cycling-types
Authorization: Bearer {{access_token}}
```

**Query Parameters (opcionales):**
- `active_only=true` - Solo tipos activos
- `active_only=false` - Todos los tipos (activos e inactivos)

**Expected Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "bikepacking",
    "display_name": "Bikepacking",
    "description": "Viajes de varios días en bicicleta con equipaje completo",
    "is_active": true,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
]
```

---

#### 3. Obtener Tipo por Código (Admin)

```http
GET {{base_url}}/admin/cycling-types/bikepacking
Authorization: Bearer {{access_token}}
```

**Expected Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "bikepacking",
  "display_name": "Bikepacking",
  "description": "Viajes de varios días en bicicleta con equipaje completo",
  "is_active": true,
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T10:00:00Z"
}
```

**Expected Response (404 Not Found):**
```json
{
  "detail": {
    "code": "NOT_FOUND",
    "message": "No se encontró el tipo de ciclismo 'invalid-code'"
  }
}
```

---

#### 4. Crear Nuevo Tipo (Admin)

```http
POST {{base_url}}/admin/cycling-types
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "code": "cyclocross",
  "display_name": "Ciclocross",
  "description": "Carreras en circuitos mixtos con obstáculos",
  "is_active": true
}
```

**Expected Response (201 Created):**
```json
{
  "success": true,
  "message": "Tipo de ciclismo creado correctamente",
  "data": {
    "id": "7f4a406b-d10f-4730-a48c-bec3ebe8204e",
    "code": "cyclocross",
    "display_name": "Ciclocross",
    "description": "Carreras en circuitos mixtos con obstáculos",
    "is_active": true,
    "created_at": "2026-01-08T11:00:00Z",
    "updated_at": "2026-01-08T11:00:00Z"
  },
  "error": null
}
```

**Expected Response (400 Bad Request - código duplicado):**
```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Ya existe un tipo de ciclismo con el código 'cyclocross'"
  }
}
```

**Validaciones:**
- `code`: 2-50 caracteres, lowercase, alfanumérico + guiones/guiones bajos
- `display_name`: 2-100 caracteres, requerido
- `description`: Máximo 500 caracteres, opcional
- `is_active`: Boolean, default true

---

#### 5. Actualizar Tipo Existente (Admin)

```http
PUT {{base_url}}/admin/cycling-types/cyclocross
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "display_name": "Ciclocross Pro",
  "description": "Carreras profesionales en circuitos mixtos",
  "is_active": true
}
```

**Notas:**
- Todos los campos son opcionales
- Solo se actualizan los campos enviados
- El `code` NO se puede modificar (es el identificador)

**Expected Response (200 OK):**
```json
{
  "success": true,
  "message": "Tipo de ciclismo actualizado correctamente",
  "data": {
    "id": "7f4a406b-d10f-4730-a48c-bec3ebe8204e",
    "code": "cyclocross",
    "display_name": "Ciclocross Pro",
    "description": "Carreras profesionales en circuitos mixtos",
    "is_active": true,
    "created_at": "2026-01-08T11:00:00Z",
    "updated_at": "2026-01-08T11:30:00Z"
  },
  "error": null
}
```

**Expected Response (404 Not Found):**
```json
{
  "detail": {
    "code": "NOT_FOUND",
    "message": "No se encontró el tipo de ciclismo 'invalid-code'"
  }
}
```

---

#### 6. Desactivar Tipo (Admin - Soft Delete)

```http
DELETE {{base_url}}/admin/cycling-types/cyclocross
Authorization: Bearer {{access_token}}
```

**Notas:**
- Por defecto hace **soft delete** (establece `is_active=false`)
- El registro permanece en la base de datos
- Deja de aparecer en el endpoint público `/cycling-types`

**Expected Response (204 No Content):**
```
(Sin contenido - solo status code 204)
```

---

#### 7. Eliminar Tipo Permanentemente (Admin - Hard Delete)

```http
DELETE {{base_url}}/admin/cycling-types/cyclocross?hard=true
Authorization: Bearer {{access_token}}
```

**⚠️ ADVERTENCIA**: Esta acción **elimina permanentemente** el registro de la base de datos y no se puede deshacer.

**Expected Response (204 No Content):**
```
(Sin contenido - solo status code 204)
```

---

## Colección JSON Completa

```json
{
  "info": {
    "name": "ContraVento - Cycling Types",
    "description": "API endpoints para gestión de tipos de ciclismo",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Public",
      "item": [
        {
          "name": "List Active Cycling Types",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "url": {
              "raw": "{{base_url}}/cycling-types",
              "host": ["{{base_url}}"],
              "path": ["cycling-types"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Admin",
      "item": [
        {
          "name": "Login (Get Token)",
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
                ]
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
              "raw": "{\n  \"login\": \"testuser\",\n  \"password\": \"TestPass123!\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/login",
              "host": ["{{base_url}}"],
              "path": ["auth", "login"]
            }
          },
          "response": []
        },
        {
          "name": "List All Cycling Types (Admin)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/admin/cycling-types?active_only=false",
              "host": ["{{base_url}}"],
              "path": ["admin", "cycling-types"],
              "query": [
                {
                  "key": "active_only",
                  "value": "false",
                  "description": "Filter to only active types"
                }
              ]
            }
          },
          "response": []
        },
        {
          "name": "Get Cycling Type by Code (Admin)",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/admin/cycling-types/bikepacking",
              "host": ["{{base_url}}"],
              "path": ["admin", "cycling-types", "bikepacking"]
            }
          },
          "response": []
        },
        {
          "name": "Create Cycling Type (Admin)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const response = pm.response.json();",
                  "",
                  "if (response.success && response.data) {",
                  "    pm.environment.set('test_cycling_type_code', response.data.code);",
                  "    console.log('Cycling type created:', response.data.code);",
                  "}"
                ]
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
              "raw": "{\n  \"code\": \"cyclocross\",\n  \"display_name\": \"Ciclocross\",\n  \"description\": \"Carreras en circuitos mixtos con obstáculos\",\n  \"is_active\": true\n}"
            },
            "url": {
              "raw": "{{base_url}}/admin/cycling-types",
              "host": ["{{base_url}}"],
              "path": ["admin", "cycling-types"]
            }
          },
          "response": []
        },
        {
          "name": "Update Cycling Type (Admin)",
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
              "raw": "{\n  \"display_name\": \"Ciclocross Pro\",\n  \"description\": \"Carreras profesionales en circuitos mixtos\",\n  \"is_active\": true\n}"
            },
            "url": {
              "raw": "{{base_url}}/admin/cycling-types/{{test_cycling_type_code}}",
              "host": ["{{base_url}}"],
              "path": ["admin", "cycling-types", "{{test_cycling_type_code}}"]
            }
          },
          "response": []
        },
        {
          "name": "Deactivate Cycling Type (Admin - Soft Delete)",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/admin/cycling-types/{{test_cycling_type_code}}",
              "host": ["{{base_url}}"],
              "path": ["admin", "cycling-types", "{{test_cycling_type_code}}"]
            }
          },
          "response": []
        },
        {
          "name": "Delete Cycling Type Permanently (Admin - Hard Delete)",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/admin/cycling-types/{{test_cycling_type_code}}?hard=true",
              "host": ["{{base_url}}"],
              "path": ["admin", "cycling-types", "{{test_cycling_type_code}}"],
              "query": [
                {
                  "key": "hard",
                  "value": "true",
                  "description": "Permanent deletion (cannot be undone)"
                }
              ]
            }
          },
          "response": []
        }
      ]
    }
  ]
}
```

---

## Troubleshooting

### Error: 401 Unauthorized en endpoints admin

**Causa**: Token de autenticación inválido o expirado.

**Solución**:
1. Ejecutar el request "Login (Get Token)"
2. Verificar que la variable `access_token` se guardó correctamente
3. Verificar que el header Authorization tenga formato: `Bearer {{access_token}}`

---

### Error: 400 "Ya existe un tipo de ciclismo con el código..."

**Causa**: Intentando crear un tipo con un código que ya existe.

**Solución**:
1. Cambiar el `code` a uno único
2. O actualizar el tipo existente con PUT en lugar de crear uno nuevo
3. O eliminar el tipo existente primero

---

### Error: 404 "No se encontró el tipo de ciclismo..."

**Causa**: El código especificado no existe en la base de datos.

**Solución**:
1. Verificar que el código esté escrito correctamente (lowercase)
2. Listar todos los tipos con `GET /admin/cycling-types` para ver los códigos disponibles
3. Si fue desactivado, verificar con `?active_only=false`

---

### Error: 400 "El código solo puede contener..."

**Causa**: El código contiene caracteres no permitidos.

**Solución**:
- Usar solo letras minúsculas, números, guiones y guiones bajos
- No usar espacios ni caracteres especiales
- Ejemplos válidos: `bikepacking`, `urban-trail`, `long_distance`
- Ejemplos inválidos: `Bikepacking`, `urban trail`, `ciclo@cross`

---

### No aparece el nuevo tipo en GET /cycling-types

**Causa**: El tipo está desactivado (`is_active=false`).

**Solución**:
1. El endpoint público solo muestra tipos activos
2. Verificar con `GET /admin/cycling-types?active_only=false`
3. Actualizar el tipo con `PUT` y establecer `is_active: true`

---

## Flujo de Testing Completo

```bash
1. GET  /cycling-types                        # Ver tipos públicos
2. POST /auth/login                           # Obtener token
3. GET  /admin/cycling-types                  # Ver todos los tipos (admin)
4. POST /admin/cycling-types                  # Crear nuevo tipo
5. GET  /admin/cycling-types/{code}           # Verificar tipo creado
6. PUT  /admin/cycling-types/{code}           # Actualizar tipo
7. GET  /cycling-types                        # Verificar en endpoint público
8. DELETE /admin/cycling-types/{code}         # Soft delete
9. GET  /cycling-types                        # Verificar que ya no aparece
10. GET  /admin/cycling-types?active_only=false # Ver que sigue existiendo
11. DELETE /admin/cycling-types/{code}?hard=true # Hard delete (opcional)
```

---

## Ejemplos Adicionales

### Crear tipo con descripción larga

```json
{
  "code": "ultra-endurance",
  "display_name": "Ultra Resistencia",
  "description": "Competiciones de ciclismo de ultra resistencia que superan las 200km en una sola etapa, incluyendo eventos como el Tour Divide, Race Across America (RAAM) y otras pruebas de bikepacking extremo.",
  "is_active": true
}
```

### Actualizar solo el nombre de visualización

```json
{
  "display_name": "MTB Montaña"
}
```

### Desactivar temporalmente un tipo

```json
{
  "is_active": false
}
```

---

## Referencias

- **Documentación completa**: [backend/docs/CYCLING_TYPES.md](../CYCLING_TYPES.md)
- **API Swagger**: http://localhost:8000/docs
- **Modelo**: `src/models/cycling_type.py`
- **Endpoints**: `src/api/cycling_types.py`
