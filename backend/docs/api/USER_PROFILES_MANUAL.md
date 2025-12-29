# Manual Testing Guide - User Profiles & Authentication

Guía completa con comandos `curl` para testing manual de autenticación, perfiles de usuario y features sociales.

## Tabla de Contenidos

- [Prerequisitos](#prerequisitos)
- [Configuración Inicial](#configuración-inicial)
- [Authentication](#authentication)
- [User Profiles](#user-profiles)
- [Social Features](#social-features)
- [User Stats](#user-stats)
- [Casos de Prueba Completos](#casos-de-prueba-completos)
- [Troubleshooting](#troubleshooting)

---

## Prerequisitos

### 1. Servidor en Ejecución

```bash
cd backend
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Base de Datos Inicializada

```bash
cd backend
poetry run alembic upgrade head
```

### 3. Variables de Entorno

**Linux/Mac:**
```bash
export API_URL="http://localhost:8000"
```

**Windows PowerShell:**
```powershell
$env:API_URL="http://localhost:8000"
```

**Windows CMD:**
```cmd
set API_URL=http://localhost:8000
```

---

## Configuración Inicial

### Health Check

Verificar que el servidor está funcionando:

```bash
curl -X GET "$API_URL/health"
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-29T12:00:00Z"
}
```

---

## Authentication

### 1. Register New User

```bash
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria_garcia",
    "email": "maria@example.com",
    "password": "SecurePass123!"
  }'
```

**Respuesta esperada (201):**
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

**Guardar user_id:**
```bash
# Linux/Mac
export USER_ID="550e8400-e29b-41d4-a716-446655440000"

# Windows PowerShell
$env:USER_ID="550e8400-e29b-41d4-a716-446655440000"
```

#### Validaciones de Registro

**Username ya existe:**
```bash
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "new@example.com",
    "password": "SecurePass123!"
  }'
```

**Respuesta esperada (400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "USERNAME_TAKEN",
    "message": "El nombre de usuario 'testuser' ya está en uso",
    "field": "username"
  }
}
```

**Contraseña débil:**
```bash
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "password": "weak"
  }'
```

**Respuesta esperada (400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "WEAK_PASSWORD",
    "message": "La contraseña debe tener al menos 8 caracteres",
    "field": "password"
  }
}
```

**Email inválido:**
```bash
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "invalid-email",
    "password": "SecurePass123!"
  }'
```

---

### 2. Login

```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "password": "SecurePass123!"
  }'
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NDc0ODAwfQ.abc123...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczODA2NjgwMH0.def456...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "error": null
}
```

**Guardar token:**
```bash
# Linux/Mac
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Windows PowerShell
$env:TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### Validaciones de Login

**Credenciales incorrectas:**
```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "password": "WrongPassword123!"
  }'
```

**Respuesta esperada (401):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email o contraseña incorrectos"
  }
}
```

**Usuario no existe:**
```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "SecurePass123!"
  }'
```

---

### 3. Get Current User

```bash
curl -X GET "$API_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (200):**
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

#### Validación sin Token

```bash
curl -X GET "$API_URL/auth/me"
```

**Respuesta esperada (401):**
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

### 4. Refresh Token

```bash
# Guardar refresh token primero
export REFRESH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "$API_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }"
```

**Respuesta esperada (200):**
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

## User Profiles

### 1. Get User Profile (Public)

```bash
curl -X GET "$API_URL/users/maria_garcia"
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "maria_garcia",
    "bio": null,
    "location": null,
    "cycling_type": null,
    "photo_url": null,
    "website": null,
    "instagram_handle": null,
    "is_verified": true,
    "followers_count": 0,
    "following_count": 0,
    "created_at": "2025-12-29T12:00:00Z"
  },
  "error": null
}
```

---

### 2. Get User Profile (Authenticated)

```bash
curl -X GET "$API_URL/users/maria_garcia" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3. Update Profile

```bash
curl -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Amante del bikepacking y las rutas de montaña. Documentando mis aventuras en dos ruedas. 🚴‍♀️",
    "location": "Barcelona, España",
    "cycling_type": "bikepacking",
    "website": "https://mariagarciacycling.com",
    "instagram_handle": "@maria_bikepacking"
  }'
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "maria_garcia",
    "bio": "Amante del bikepacking y las rutas de montaña. Documentando mis aventuras en dos ruedas. 🚴‍♀️",
    "location": "Barcelona, España",
    "cycling_type": "bikepacking",
    "website": "https://mariagarciacycling.com",
    "instagram_handle": "@maria_bikepacking",
    "photo_url": null,
    "updated_at": "2025-12-29T12:30:00Z"
  },
  "error": null
}
```

#### Validaciones de Update Profile

**Bio muy larga (> 500 caracteres):**
```bash
curl -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "'$(python3 -c "print('a' * 501)")'"
  }'
```

**Respuesta esperada (400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "La biografía no puede exceder 500 caracteres",
    "field": "bio"
  }
}
```

**Cycling type inválido:**
```bash
curl -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cycling_type": "invalid_type"
  }'
```

**Respuesta esperada (400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Tipo de ciclismo inválido. Opciones: road, gravel, mtb, bikepacking, urban",
    "field": "cycling_type"
  }
}
```

**URL de website inválida:**
```bash
curl -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "website": "not-a-valid-url"
  }'
```

---

### 4. Upload Profile Photo

**Crear imagen de prueba (Linux/Mac con ImageMagick):**
```bash
convert -size 400x400 xc:blue \
  -gravity center \
  -pointsize 48 \
  -fill white \
  -annotate +0+0 "Maria" \
  profile_photo.jpg
```

**Upload:**
```bash
curl -X POST "$API_URL/profile/photo" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@profile_photo.jpg"
```

**Respuesta esperada (200):**
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

#### Validaciones de Upload Photo

**Archivo muy grande (> 5MB):**
```bash
# Crear archivo grande
convert -size 3000x3000 xc:red large_photo.jpg

curl -X POST "$API_URL/profile/photo" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@large_photo.jpg"
```

**Respuesta esperada (400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "La foto excede el tamaño máximo de 5MB"
  }
}
```

**Formato inválido:**
```bash
echo "This is not an image" > fake_photo.txt

curl -X POST "$API_URL/profile/photo" \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@fake_photo.txt"
```

**Respuesta esperada (400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Formato de archivo no soportado. Usa JPG o PNG"
  }
}
```

---

## Social Features

### Setup: Crear Segundo Usuario

Para testear features sociales, necesitamos otro usuario:

```bash
# Registrar segundo usuario
curl -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "carlos_mtb",
    "email": "carlos@example.com",
    "password": "SecurePass123!"
  }'

# Login con segundo usuario
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "carlos@example.com",
    "password": "SecurePass123!"
  }'

# Guardar token del segundo usuario
export TOKEN2="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 1. Follow User

**Maria sigue a Carlos:**
```bash
curl -X POST "$API_URL/users/carlos_mtb/follow" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (201):**
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

#### Validaciones de Follow

**Seguirse a uno mismo:**
```bash
curl -X POST "$API_URL/users/maria_garcia/follow" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (400):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "SELF_FOLLOW",
    "message": "No puedes seguirte a ti mismo"
  }
}
```

**Seguir a usuario ya seguido (idempotente):**
```bash
# Seguir a Carlos nuevamente
curl -X POST "$API_URL/users/carlos_mtb/follow" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "following": true,
    "message": "Ya sigues a este usuario"
  },
  "error": null
}
```

**Usuario no existe:**
```bash
curl -X POST "$API_URL/users/nonexistent_user/follow" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (404):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Usuario no encontrado"
  }
}
```

**Sin autenticación:**
```bash
curl -X POST "$API_URL/users/carlos_mtb/follow"
```

**Respuesta esperada (401):**
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

### 2. Unfollow User

```bash
curl -X DELETE "$API_URL/users/carlos_mtb/follow" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (200):**
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

### 3. Get Followers

```bash
curl -X GET "$API_URL/users/carlos_mtb/followers?limit=20&offset=0"
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "followers": [
      {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "maria_garcia",
        "photo_url": "/storage/profile_photos/2024/12/550e8400_profile.jpg",
        "cycling_type": "bikepacking",
        "followed_at": "2025-12-29T13:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

**Con autenticación (muestra más detalles si el usuario es el owner):**
```bash
curl -X GET "$API_URL/users/maria_garcia/followers?limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 4. Get Following

```bash
curl -X GET "$API_URL/users/maria_garcia/following?limit=20&offset=0"
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "following": [
      {
        "user_id": "660e8400-e29b-41d4-a716-446655440001",
        "username": "carlos_mtb",
        "photo_url": null,
        "cycling_type": null,
        "followed_at": "2025-12-29T13:00:00Z"
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

---

### 5. Check Follow Status

```bash
curl -X GET "$API_URL/users/carlos_mtb/follow-status" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (200):**
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

**Explicación:**
- `following: true` - Maria sigue a Carlos
- `followed_by: false` - Carlos NO sigue a Maria

---

## User Stats

### 1. Get User Stats

```bash
curl -X GET "$API_URL/users/maria_garcia/stats"
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "total_distance_km": 0,
    "total_trips": 0,
    "countries_visited": 0,
    "total_photos": 0,
    "member_since": "2025-12-29",
    "achievements": []
  },
  "error": null
}
```

**Con datos (después de crear trips):**
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
      },
      {
        "achievement_id": "10_countries",
        "name": "Trotamundos",
        "description": "Visitaste 10 países diferentes",
        "icon_url": "/static/badges/10_countries.svg",
        "unlocked_at": "2024-09-01T10:00:00Z"
      }
    ]
  },
  "error": null
}
```

---

### 2. Get All Achievements

```bash
curl -X GET "$API_URL/stats/achievements" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada (200):**
```json
{
  "success": true,
  "data": {
    "achievements": [
      {
        "achievement_id": "first_trip",
        "name": "Primer Viaje",
        "description": "Completaste tu primer viaje",
        "icon_url": "/static/badges/first_trip.svg",
        "requirement": "Complete 1 trip",
        "unlocked": false,
        "unlocked_at": null
      },
      {
        "achievement_id": "100km",
        "name": "100 Kilómetros",
        "description": "Recorriste 100 km en total",
        "icon_url": "/static/badges/100km.svg",
        "requirement": "Ride 100 km total",
        "unlocked": false,
        "unlocked_at": null
      }
    ],
    "total_unlocked": 0,
    "total_achievements": 15
  },
  "error": null
}
```

---

## Casos de Prueba Completos

### Flujo Completo: Registro → Perfil → Social

Este script completo demuestra un flujo típico de usuario:

```bash
#!/bin/bash

echo "=== ContraVento - User Profiles Testing ==="
API_URL="http://localhost:8000"

# 1. Registrar Usuario 1
echo -e "\n=== 1. Registrar Maria ==="
MARIA_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria_garcia",
    "email": "maria@example.com",
    "password": "SecurePass123!"
  }')

echo $MARIA_RESPONSE | jq '.'
MARIA_ID=$(echo $MARIA_RESPONSE | jq -r '.data.user_id')
echo "Maria ID: $MARIA_ID"

# 2. Login Maria
echo -e "\n=== 2. Login Maria ==="
MARIA_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "password": "SecurePass123!"
  }')

MARIA_TOKEN=$(echo $MARIA_LOGIN | jq -r '.data.access_token')
echo "Token: ${MARIA_TOKEN:0:50}..."

# 3. Actualizar Perfil de Maria
echo -e "\n=== 3. Actualizar Perfil de Maria ==="
curl -s -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $MARIA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Amante del bikepacking y las rutas de montaña 🚴‍♀️",
    "location": "Barcelona, España",
    "cycling_type": "bikepacking",
    "website": "https://mariagarciacycling.com",
    "instagram_handle": "@maria_bikepacking"
  }' | jq '.'

# 4. Registrar Usuario 2
echo -e "\n=== 4. Registrar Carlos ==="
CARLOS_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "carlos_mtb",
    "email": "carlos@example.com",
    "password": "SecurePass123!"
  }')

CARLOS_ID=$(echo $CARLOS_RESPONSE | jq -r '.data.user_id')
echo "Carlos ID: $CARLOS_ID"

# 5. Login Carlos
echo -e "\n=== 5. Login Carlos ==="
CARLOS_LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "carlos@example.com",
    "password": "SecurePass123!"
  }')

CARLOS_TOKEN=$(echo $CARLOS_LOGIN | jq -r '.data.access_token')
echo "Token: ${CARLOS_TOKEN:0:50}..."

# 6. Actualizar Perfil de Carlos
echo -e "\n=== 6. Actualizar Perfil de Carlos ==="
curl -s -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $CARLOS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "MTB rider desde 2010. Trails y descensos 🚵",
    "location": "Madrid, España",
    "cycling_type": "mtb"
  }' | jq '.'

# 7. Maria sigue a Carlos
echo -e "\n=== 7. Maria sigue a Carlos ==="
curl -s -X POST "$API_URL/users/carlos_mtb/follow" \
  -H "Authorization: Bearer $MARIA_TOKEN" | jq '.'

# 8. Carlos sigue a Maria
echo -e "\n=== 8. Carlos sigue a Maria ==="
curl -s -X POST "$API_URL/users/maria_garcia/follow" \
  -H "Authorization: Bearer $CARLOS_TOKEN" | jq '.'

# 9. Verificar seguidores de Maria
echo -e "\n=== 9. Seguidores de Maria ==="
curl -s -X GET "$API_URL/users/maria_garcia/followers" \
  -H "Authorization: Bearer $MARIA_TOKEN" | jq '.'

# 10. Verificar siguiendo de Maria
echo -e "\n=== 10. Siguiendo de Maria ==="
curl -s -X GET "$API_URL/users/maria_garcia/following" \
  -H "Authorization: Bearer $MARIA_TOKEN" | jq '.'

# 11. Check follow status
echo -e "\n=== 11. Follow Status (Maria → Carlos) ==="
curl -s -X GET "$API_URL/users/carlos_mtb/follow-status" \
  -H "Authorization: Bearer $MARIA_TOKEN" | jq '.'

# 12. Ver perfil público de Carlos
echo -e "\n=== 12. Perfil Público de Carlos ==="
curl -s -X GET "$API_URL/users/carlos_mtb" | jq '.'

# 13. Ver stats de Maria
echo -e "\n=== 13. Stats de Maria ==="
curl -s -X GET "$API_URL/users/maria_garcia/stats" | jq '.'

echo -e "\n=== Testing Completado ==="
```

**Guardar como `test_user_profiles.sh` y ejecutar:**
```bash
chmod +x test_user_profiles.sh
./test_user_profiles.sh
```

---

### Test de Validaciones Completo

```bash
#!/bin/bash

echo "=== Validation Tests ==="
API_URL="http://localhost:8000"

# Crear usuario de prueba
curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "TestPass123!"}' > /dev/null

LOGIN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}')

TOKEN=$(echo $LOGIN | jq -r '.data.access_token')

# Test 1: Username ya existe
echo -e "\n=== Test 1: Username Taken ==="
curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "new@example.com", "password": "SecurePass123!"}' \
  | jq '{success, error}'

# Test 2: Contraseña débil
echo -e "\n=== Test 2: Weak Password ==="
curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "new@example.com", "password": "weak"}' \
  | jq '{success, error}'

# Test 3: Credenciales incorrectas
echo -e "\n=== Test 3: Wrong Password ==="
curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "WrongPassword123!"}' \
  | jq '{success, error}'

# Test 4: Bio muy larga
echo -e "\n=== Test 4: Bio Too Long ==="
LONG_BIO=$(python3 -c "print('a' * 501)")
curl -s -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"bio\": \"$LONG_BIO\"}" \
  | jq '{success, error}'

# Test 5: Cycling type inválido
echo -e "\n=== Test 5: Invalid Cycling Type ==="
curl -s -X PUT "$API_URL/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cycling_type": "invalid_type"}' \
  | jq '{success, error}'

# Test 6: Seguirse a uno mismo
echo -e "\n=== Test 6: Self Follow ==="
curl -s -X POST "$API_URL/users/testuser/follow" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '{success, error}'

# Test 7: Usuario no existe
echo -e "\n=== Test 7: User Not Found ==="
curl -s -X POST "$API_URL/users/nonexistent_user/follow" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '{success, error}'

# Test 8: Sin autenticación
echo -e "\n=== Test 8: Unauthorized ==="
curl -s -X GET "$API_URL/auth/me" \
  | jq '{success, error}'

echo -e "\n=== Validation Tests Completados ==="
```

---

## Troubleshooting

### Error: "Connection refused"

```bash
curl -s http://localhost:8000/health | jq
```

**Solución:** Verificar que el servidor está corriendo:
```bash
cd backend
poetry run uvicorn src.main:app --reload
```

---

### Error: "Token inválido o expirado"

El access token expira después de 15 minutos.

**Solución 1 - Refresh Token:**
```bash
curl -X POST "$API_URL/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

**Solución 2 - Re-login:**
```bash
curl -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "maria@example.com", "password": "SecurePass123!"}'
```

---

### Error: "Username already taken"

**Solución:** Usar un username diferente o eliminar la base de datos y reiniciar:

```bash
cd backend
rm contravento.db
poetry run alembic upgrade head
```

---

### Verificar Base de Datos

**SQLite:**
```bash
sqlite3 backend/contravento.db

.tables
SELECT * FROM users;
SELECT * FROM user_profiles;
SELECT * FROM follows;
.exit
```

---

### Limpiar Datos de Prueba

```bash
# Eliminar base de datos
rm backend/contravento.db

# Recrear base de datos
cd backend
poetry run alembic upgrade head

# Recrear usuarios de prueba
poetry run python scripts/create_verified_user.py
```

---

## Referencia Rápida

### Variables de Entorno

```bash
export API_URL="http://localhost:8000"
export TOKEN="<access_token_from_login>"
export REFRESH_TOKEN="<refresh_token_from_login>"
export USER_ID="<user_id_from_register>"
```

### Comandos Esenciales

```bash
# Health check
curl "$API_URL/health"

# Register
curl -X POST "$API_URL/auth/register" -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "user@example.com", "password": "Pass123!"}'

# Login
curl -X POST "$API_URL/auth/login" -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Pass123!"}'

# Get current user
curl -X GET "$API_URL/auth/me" -H "Authorization: Bearer $TOKEN"

# Update profile
curl -X PUT "$API_URL/profile" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"bio": "My bio"}'

# Follow user
curl -X POST "$API_URL/users/username/follow" -H "Authorization: Bearer $TOKEN"

# Get user stats
curl "$API_URL/users/username/stats"
```

---

## Documentación Relacionada

- **Postman Guide**: [USER_PROFILES_POSTMAN.md](USER_PROFILES_POSTMAN.md)
- **Travel Diary Manual**: [MANUAL_TESTING.md](MANUAL_TESTING.md)
- **OpenAPI Specs**: `../../specs/001-user-profiles/contracts/`
- **Main README**: `../../README.md`

---

**Última actualización:** 2024-12-29
**Versión:** 1.0.0 (User Profiles & Authentication)
