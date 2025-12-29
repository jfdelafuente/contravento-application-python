# Postman Collection - User Profiles & Authentication

Guía completa para testing de autenticación y perfiles de usuario usando Postman o Insomnia.

## Tabla de Contenidos

- [Importar Colección](#importar-colección)
- [Variables de Entorno](#variables-de-entorno)
- [Flujos de Testing](#flujos-de-testing)
  - [Authentication](#authentication)
  - [User Profiles](#user-profiles)
  - [Social Features](#social-features)
  - [User Stats](#user-stats)
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
  "name": "ContraVento - User Profiles",
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
      "key": "refresh_token",
      "value": "",
      "enabled": true
    },
    {
      "key": "user_id",
      "value": "",
      "enabled": true
    },
    {
      "key": "username",
      "value": "",
      "enabled": true
    },
    {
      "key": "test_user_id",
      "value": "",
      "enabled": true
    }
  ]
}
```

### Auto-Update Scripts

Los siguientes scripts se deben agregar en la pestaña "Tests" de cada request:

**Register Request:**
```javascript
const response = pm.response.json();

if (response.success && response.data) {
    pm.environment.set("user_id", response.data.user_id);
    pm.environment.set("username", response.data.username);
    console.log("User registered:", response.data.username);
}
```

**Login Request:**
```javascript
const response = pm.response.json();

if (response.success && response.data.access_token) {
    pm.environment.set("access_token", response.data.access_token);
    pm.environment.set("refresh_token", response.data.refresh_token);
    console.log("Tokens saved. Expires in:", response.data.expires_in, "seconds");
}
```

**Get Profile Request:**
```javascript
const response = pm.response.json();

if (response.success && response.data) {
    pm.environment.set("user_id", response.data.user_id);
    console.log("Profile loaded for:", response.data.username);
}
```

---

## Flujos de Testing

### Authentication

#### 1. Register New User

**Request:** `POST {{base_url}}/auth/register`

**Body (JSON):**
```json
{
  "username": "maria_garcia",
  "email": "maria@example.com",
  "password": "SecurePass123!"
}
```

**Headers:**
- `Content-Type: application/json`

**Expected Response (201):**
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "maria_garcia",
    "email": "maria@example.com",
    "is_verified": false,
    "created_at": "2025-12-29T12:00:00Z"
  },
  "error": null,
  "message": "Usuario registrado. Revisa tu email para verificar tu cuenta."
}
```

**Validations to Test:**
- ✅ Username ya existe (400)
- ✅ Email ya registrado (400)
- ✅ Contraseña débil - menos de 8 caracteres (400)
- ✅ Email inválido (400)
- ✅ Username con caracteres especiales (400)

---

#### 2. Login

**Request:** `POST {{base_url}}/auth/login`

**Body (JSON):**
```json
{
  "login": "maria@example.com",
  "password": "SecurePass123!"
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

**Validations to Test:**
- ✅ Credenciales incorrectas (401)
- ✅ Email no registrado (401)
- ✅ Usuario no verificado - login permitido (200)
- ✅ Rate limiting - 5 intentos fallidos (429)

---

#### 3. Refresh Token

**Request:** `POST {{base_url}}/auth/refresh`

**Body (JSON):**
```json
{
  "refresh_token": "{{refresh_token}}"
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

#### 4. Get Current User

**Request:** `GET {{base_url}}/auth/me`

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "maria_garcia",
    "email": "maria@example.com",
    "is_verified": true,
    "is_active": true,
    "created_at": "2025-12-29T12:00:00Z"
  },
  "error": null
}
```

---

### User Profiles

#### 1. Get User Profile

**Request:** `GET {{base_url}}/users/{{username}}/profile`

**Headers:**
- `Authorization: Bearer {{access_token}}` (opcional para perfiles públicos)

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "maria_garcia",
    "bio": "Amante del bikepacking y las rutas de montaña",
    "location": "Barcelona, España",
    "cycling_type": "bikepacking",
    "photo_url": "/storage/profile_photos/2024/12/550e8400_profile.jpg",
    "is_verified": true,
    "followers_count": 145,
    "following_count": 89,
    "created_at": "2025-12-29T12:00:00Z"
  },
  "error": null
}
```

---

#### 2. Update Profile

**Request:** `PUT {{base_url}}/users/{{username}}/profile`

**Body (JSON):**
```json
{
  "bio": "Amante del bikepacking y las rutas de montaña. 🚴‍♀️",
  "location": "Barcelona, España",
  "cycling_type": "bikepacking",
  "website": "https://mariagarciacycling.com",
  "instagram_handle": "@maria_bikepacking"
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
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "maria_garcia",
    "bio": "Amante del bikepacking y las rutas de montaña. 🚴‍♀️",
    "location": "Barcelona, España",
    "cycling_type": "bikepacking",
    "website": "https://mariagarciacycling.com",
    "instagram_handle": "@maria_bikepacking",
    "updated_at": "2025-12-29T12:30:00Z"
  },
  "error": null
}
```

**Validations to Test:**
- ✅ Bio con más de 500 caracteres (400)
- ✅ Cycling type inválido (400)
- ✅ URL de website inválida (400)
- ✅ Instagram handle sin @ (se añade automáticamente)

---

#### 3. Upload Profile Photo

**Request:** `POST {{base_url}}/users/{{username}}/profile/photo`

**Body (form-data):**
- Key: `photo`
- Type: `File`
- Value: [Select image file]

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "photo_url": "/storage/profile_photos/2024/12/550e8400_profile.jpg",
    "uploaded_at": "2025-12-29T12:45:00Z"
  },
  "error": null
}
```

**Validations to Test:**
- ✅ Archivo muy grande > 5MB (400)
- ✅ Formato inválido (no JPG/PNG) (400)
- ✅ Archivo corrupto (400)

---

### Social Features

#### 1. Follow User

**Request:** `POST {{base_url}}/users/{{username}}/follow`

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (201):**
```json
{
  "success": true,
  "data": {
    "following": true,
    "follower_user_id": "550e8400-e29b-41d4-a716-446655440000",
    "followed_user_id": "660e8400-e29b-41d4-a716-446655440001",
    "created_at": "2025-12-29T13:00:00Z"
  },
  "error": null
}
```

**Validations to Test:**
- ✅ Seguir a uno mismo (400)
- ✅ Seguir a usuario ya seguido (idempotente - 200)
- ✅ Usuario no existe (404)
- ✅ Sin autenticación (401)

---

#### 2. Unfollow User

**Request:** `DELETE {{base_url}}/users/{{username}}/follow`

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "following": false
  },
  "error": null
}
```

---

#### 3. Get Followers

**Request:** `GET {{base_url}}/users/{{username}}/followers?limit=20&offset=0`

**Headers:**
- `Authorization: Bearer {{access_token}}` (opcional)

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "followers": [
      {
        "user_id": "770e8400-e29b-41d4-a716-446655440002",
        "username": "carlos_mtb",
        "photo_url": "/storage/profile_photos/2024/12/carlos_profile.jpg",
        "cycling_type": "mtb",
        "followed_at": "2025-12-28T10:00:00Z"
      }
    ],
    "total": 145,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

---

#### 4. Get Following

**Request:** `GET {{base_url}}/users/{{username}}/following?limit=20&offset=0`

**Headers:**
- `Authorization: Bearer {{access_token}}` (opcional)

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "following": [
      {
        "user_id": "880e8400-e29b-41d4-a716-446655440003",
        "username": "laura_gravel",
        "photo_url": "/storage/profile_photos/2024/12/laura_profile.jpg",
        "cycling_type": "gravel",
        "followed_at": "2025-12-27T15:30:00Z"
      }
    ],
    "total": 89,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

---

#### 5. Check Follow Status

**Request:** `GET {{base_url}}/users/{{username}}/follow-status`

**Headers:**
- `Authorization: Bearer {{access_token}}`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "following": true,
    "followed_by": false
  },
  "error": null
}
```

---

### User Stats

#### 1. Get User Stats

**Request:** `GET {{base_url}}/users/{{username}}/stats`

**Expected Response (200):**
```json
{
  "success": true,
  "data": {
    "total_distance_km": 2456.8,
    "total_trips": 37,
    "countries_visited": 8,
    "total_photos": 342,
    "member_since": "2024-01-15",
    "achievements": [
      {
        "achievement_id": "first_trip",
        "name": "Primer Viaje",
        "description": "Completaste tu primer viaje",
        "icon_url": "/static/badges/first_trip.svg",
        "unlocked_at": "2024-01-20T14:00:00Z"
      },
      {
        "achievement_id": "1000km",
        "name": "1000 Kilómetros",
        "description": "Recorriste 1000 km en total",
        "icon_url": "/static/badges/1000km.svg",
        "unlocked_at": "2024-06-15T18:30:00Z"
      }
    ]
  },
  "error": null
}
```

---

## Colección JSON Completa

### Postman Collection v2.1

```json
{
  "info": {
    "name": "ContraVento - User Profiles & Authentication",
    "description": "Colección completa para testing de autenticación, perfiles y features sociales",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "version": "1.0.0"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const response = pm.response.json();",
                  "",
                  "if (response.success && response.data) {",
                  "    pm.environment.set('user_id', response.data.user_id);",
                  "    pm.environment.set('username', response.data.username);",
                  "    console.log('User registered:', response.data.username);",
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
              "raw": "{\n  \"username\": \"maria_garcia\",\n  \"email\": \"maria@example.com\",\n  \"password\": \"SecurePass123!\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register",
              "host": ["{{base_url}}"],
              "path": ["auth", "register"]
            }
          },
          "response": []
        },
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
                  "    pm.environment.set('refresh_token', response.data.refresh_token);",
                  "    console.log('Tokens saved. Expires in:', response.data.expires_in, 'seconds');",
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
              "raw": "{\n  \"login\": \"maria@example.com\",\n  \"password\": \"SecurePass123!\"\n}"
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
          "name": "Refresh Token",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const response = pm.response.json();",
                  "",
                  "if (response.success && response.data.access_token) {",
                  "    pm.environment.set('access_token', response.data.access_token);",
                  "    pm.environment.set('refresh_token', response.data.refresh_token);",
                  "    console.log('Tokens refreshed');",
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
              "raw": "{\n  \"refresh_token\": \"{{refresh_token}}\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/refresh",
              "host": ["{{base_url}}"],
              "path": ["auth", "refresh"]
            }
          },
          "response": []
        },
        {
          "name": "Get Current User",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/auth/me",
              "host": ["{{base_url}}"],
              "path": ["auth", "me"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Profile",
      "item": [
        {
          "name": "Get User Profile",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users/{{username}}",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}"]
            }
          },
          "response": []
        },
        {
          "name": "Update Profile",
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
              "raw": "{\n  \"bio\": \"Amante del bikepacking y las rutas de montaña. 🚴‍♀️\",\n  \"location\": \"Barcelona, España\",\n  \"cycling_type\": \"bikepacking\",\n  \"website\": \"https://mariagarciacycling.com\",\n  \"instagram_handle\": \"@maria_bikepacking\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/users/{{username}}/profile",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "profile"]
            }
          },
          "response": []
        },
        {
          "name": "Upload Profile Photo",
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
              "raw": "{{base_url}}/users/{{username}}/profile/photo",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "profile", "photo"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Social",
      "item": [
        {
          "name": "Follow User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users/{{username}}/follow",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "follow"]
            }
          },
          "response": []
        },
        {
          "name": "Unfollow User",
          "request": {
            "method": "DELETE",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users/{{username}}/follow",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "follow"]
            }
          },
          "response": []
        },
        {
          "name": "Get Followers",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users/{{username}}/followers?limit=20&offset=0",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "followers"],
              "query": [
                {
                  "key": "limit",
                  "value": "20"
                },
                {
                  "key": "offset",
                  "value": "0"
                }
              ]
            }
          },
          "response": []
        },
        {
          "name": "Get Following",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users/{{username}}/following?limit=20&offset=0",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "following"],
              "query": [
                {
                  "key": "limit",
                  "value": "20"
                },
                {
                  "key": "offset",
                  "value": "0"
                }
              ]
            }
          },
          "response": []
        },
        {
          "name": "Check Follow Status",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users/{{username}}/follow-status",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "follow-status"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "Stats",
      "item": [
        {
          "name": "Get User Stats",
          "request": {
            "method": "GET",
            "url": {
              "raw": "{{base_url}}/users/{{username}}/stats",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "stats"]
            }
          },
          "response": []
        },
        {
          "name": "Get Achievements",
          "request": {
            "method": "GET",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/achievements",
              "host": ["{{base_url}}"],
              "path": ["achievements"]
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
          "name": "Register - Username Taken (400)",
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
              "raw": "{\n  \"username\": \"testuser\",\n  \"email\": \"new@example.com\",\n  \"password\": \"SecurePass123!\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register",
              "host": ["{{base_url}}"],
              "path": ["auth", "register"]
            }
          },
          "response": []
        },
        {
          "name": "Register - Weak Password (400)",
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
              "raw": "{\n  \"username\": \"newuser\",\n  \"email\": \"new@example.com\",\n  \"password\": \"weak\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/register",
              "host": ["{{base_url}}"],
              "path": ["auth", "register"]
            }
          },
          "response": []
        },
        {
          "name": "Login - Wrong Password (401)",
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
              "raw": "{\n  \"login\": \"test@example.com\",\n  \"password\": \"WrongPassword123!\"\n}"
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
          "name": "Follow Self (400)",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": {
              "raw": "{{base_url}}/users/{{username}}/follow",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "follow"]
            }
          },
          "response": []
        },
        {
          "name": "Upload Large Photo (400)",
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
                  "description": "Upload file > 5MB"
                }
              ]
            },
            "url": {
              "raw": "{{base_url}}/users/{{username}}/profile/photo",
              "host": ["{{base_url}}"],
              "path": ["users", "{{username}}", "profile", "photo"]
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

## Troubleshooting

### Token Expirado

**Error:** `{"error": {"code": "UNAUTHORIZED", "message": "Token de autenticación inválido o expirado"}}`

**Solución:**
1. Ejecutar request "Refresh Token"
2. O ejecutar request "Login" nuevamente
3. Verificar que el script de auto-update se ejecutó correctamente

---

### Variables No Se Guardan

**Problema:** Las variables de entorno no se actualizan automáticamente.

**Solución:**
1. Verificar que el environment está seleccionado en la esquina superior derecha
2. Revisar que los scripts en la pestaña "Tests" están correctos
3. Verificar la consola de Postman para errores en scripts

---

### Error al Subir Foto

**Error:** `{"error": {"code": "VALIDATION_ERROR", "message": "La foto excede el tamaño máximo de 5MB"}}`

**Solución:**
- Usar una imagen < 5MB
- Formatos permitidos: JPG, PNG
- Verificar que el key del form-data es exactamente "photo"

---

### Rate Limiting

**Error:** `{"error": {"code": "TOO_MANY_REQUESTS"}}`

**Solución:**
- Esperar 15 minutos después de 5 intentos fallidos de login
- O reiniciar el servidor en desarrollo

---

## Quick Start Workflow

### Setup Inicial

1. **Importar colección** (ver sección [Importar Colección](#importar-colección))
2. **Crear environment** con variables base
3. **Iniciar servidor**:
   ```bash
   cd backend
   poetry run uvicorn src.main:app --reload
   ```

### Flujo Básico

1. **Register** → Guarda `user_id` y `username`
2. **Login** → Guarda `access_token` y `refresh_token`
3. **Get Current User** → Verifica autenticación
4. **Update Profile** → Actualiza bio y location
5. **Upload Profile Photo** → Sube imagen
6. **Get User Profile** → Verifica cambios
7. **Follow User** → Crea conexión social
8. **Get User Stats** → Verifica estadísticas

### Testing de Validaciones

Ejecutar todos los requests en "Validation Tests" folder para verificar:
- Manejo de errores 400 (bad request)
- Manejo de errores 401 (unauthorized)
- Manejo de errores 404 (not found)
- Rate limiting y seguridad

---

## Documentación Relacionada

- **OpenAPI Specs**:
  - `../../specs/001-user-profiles/contracts/auth.yaml`
  - `../../specs/001-user-profiles/contracts/profile.yaml`
  - `../../specs/001-user-profiles/contracts/social.yaml`
  - `../../specs/001-user-profiles/contracts/stats.yaml`
- **Specification**: `../../specs/001-user-profiles/spec.md`
- **Main README**: `../README.md`
- **Travel Diary Collection**: `POSTMAN_COLLECTION.md`

---

**Última actualización:** 2024-12-29
**Versión:** 1.0.0 (User Profiles & Authentication)
