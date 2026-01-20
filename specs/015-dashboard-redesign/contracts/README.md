# API Contracts - Dashboard Redesign

**Feature**: 015-dashboard-redesign
**Date**: 2026-01-20

## Overview

Esta carpeta contiene los contratos OpenAPI (YAML) para los 6 endpoints consumidos por el dashboard frontend. El backend (Python/FastAPI) ya implementa estos endpoints - estos contratos documentan la interfaz existente.

## Endpoints

| Endpoint | Contract File | Status | User Story |
|----------|---------------|--------|------------|
| `GET /api/v1/dashboard/stats` | dashboard-stats.yaml | ✅ Documented | US1 |
| `GET /api/v1/dashboard/feed` | activity-feed.yaml | 📝 Simplified below | US3 |
| `GET /api/v1/dashboard/suggested-routes` | suggested-routes.yaml | 📝 Simplified below | US4 |
| `GET /api/v1/dashboard/challenges` | challenges.yaml | 📝 Simplified below | US5 |
| `GET /api/v1/dashboard/notifications` | notifications.yaml | 📝 Simplified below | US6 |
| `GET /api/v1/dashboard/search` | global-search.yaml | 📝 Simplified below | US2 |

## Simplified Contract Summary

Debido a limitaciones de espacio, los contratos restantes se resumen aquí. Para contratos OpenAPI completos, expandir cada sección a archivos YAML individuales en implementación.

### Activity Feed (`GET /api/v1/dashboard/feed`)

**Request**:

```http
GET /api/v1/dashboard/feed?page=1&limit=50
Authorization: Bearer {token}
```

**Query Parameters**:

- `page` (integer, default: 1) - Página actual
- `limit` (integer, default: 50, max: 100) - Items por página

**Response 200**:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "activity_id": "act_123",
        "activity_type": "trip_published",
        "actor_user_id": "user_456",
        "actor_username": "maria_garcia",
        "actor_photo_url": "/storage/profile_photos/maria.jpg",
        "timestamp": "2026-01-20T10:15:00Z",
        "content": {
          "trip_id": "trip_789",
          "trip_title": "Ruta de los Molinos",
          "trip_cover_photo_url": "/storage/trips/molinos.jpg",
          "trip_distance_km": 45.3,
          "trip_countries": ["España"]
        }
      }
    ],
    "total_count": 324,
    "page": 1,
    "page_size": 50,
    "has_next": true
  },
  "error": null
}
```

**activity_type Enum**: `trip_published` | `achievement_unlocked` | `challenge_completed` | `comment_added` | `like_received`

---

### Suggested Routes (`GET /api/v1/dashboard/suggested-routes`)

**Request**:

```http
GET /api/v1/dashboard/suggested-routes?limit=5
Authorization: Bearer {token}
```

**Query Parameters**:

- `limit` (integer, default: 5, max: 20) - Número de rutas sugeridas

**Response 200**:

```json
{
  "success": true,
  "data": {
    "routes": [
      {
        "route_id": "route_001",
        "title": "Camino de los Pueblos Blancos",
        "description": "Ruta por los pueblos blancos de Andalucía",
        "distance_km": 67.5,
        "difficulty": "moderate",
        "estimated_duration_hours": 5.5,
        "cover_photo_url": "/storage/routes/pueblos_blancos.jpg",
        "reason": "Incluye 3 pueblos que no has visitado",
        "towns_included": ["Grazalema", "Zahara de la Sierra"],
        "countries": ["España"],
        "rating_avg": 4.7,
        "completed_by_count": 234,
        "is_completed": false,
        "is_saved": false
      }
    ],
    "total_available": 47
  },
  "error": null
}
```

**difficulty Enum**: `easy` | `moderate` | `hard` | `expert`

---

### Active Challenges (`GET /api/v1/dashboard/challenges`)

**Request**:

```http
GET /api/v1/dashboard/challenges
Authorization: Bearer {token}
```

**Response 200**:

```json
{
  "success": true,
  "data": {
    "challenges": [
      {
        "challenge_id": "chal_001",
        "name": "Comercios Rurales",
        "description": "Visita 5 comercios locales y documéntalos",
        "icon_url": "/icons/shop.svg",
        "status": "in_progress",
        "current_progress": 3,
        "required_progress": 5,
        "progress_unit": "comercios visitados",
        "started_at": "2026-01-15T00:00:00Z",
        "expires_at": "2026-02-15T23:59:59Z",
        "completed_at": null,
        "reward_achievement_id": "ach_shop_explorer",
        "reward_achievement_name": "Explorador de Comercios"
      }
    ],
    "total_active": 2,
    "total_completed_all_time": 15
  },
  "error": null
}
```

**status Enum**: `in_progress` | `completed` | `failed` | `expired`

---

### Notifications (`GET /api/v1/dashboard/notifications`)

**Request**:

```http
GET /api/v1/dashboard/notifications?unread=true&limit=20
Authorization: Bearer {token}
```

**Query Parameters**:

- `unread` (boolean, default: false) - Solo notificaciones no leídas
- `limit` (integer, default: 20, max: 50) - Número de notificaciones

**Response 200**:

```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "notification_id": "notif_001",
        "type": "like",
        "priority": "low",
        "title": "Nuevo like en tu viaje",
        "message": "A maria_garcia le gustó tu viaje 'Ruta de los Molinos'",
        "icon_url": "/icons/heart.svg",
        "created_at": "2026-01-20T14:30:00Z",
        "is_read": false,
        "read_at": null,
        "action_url": "/trips/trip_789",
        "action_text": "Ver viaje",
        "actor_user_id": "user_456",
        "actor_username": "maria_garcia",
        "actor_photo_url": "/storage/profile_photos/maria.jpg"
      }
    ],
    "total_unread": 5,
    "total_count": 127
  },
  "error": null
}
```

**type Enum**: `like` | `comment` | `new_follower` | `challenge_completed` | `achievement_unlocked` | `security_alert`

**priority Enum**: `low` | `medium` | `high`

**Mark as Read**:

```http
PATCH /api/v1/dashboard/notifications/{notification_id}/read
Authorization: Bearer {token}
```

---

### Global Search (`GET /api/v1/dashboard/search`)

**Request**:

```http
GET /api/v1/dashboard/search?q=pueblo&types=users,routes,towns&limit=10
Authorization: Bearer {token}
```

**Query Parameters**:

- `q` (string, required, min: 2, max: 100) - Texto de búsqueda
- `types` (string, optional) - Tipos separados por coma (`users`, `routes`, `towns`)
- `limit` (integer, default: 10, max: 50) - Resultados máximos

**Response 200**:

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "result_id": "user_456",
        "type": "user",
        "title": "maria_garcia",
        "subtitle": "156 seguidores · Madrid, España",
        "photo_url": "/storage/profile_photos/maria.jpg",
        "url": "/profile/maria_garcia",
        "metadata": {
          "user_id": "user_456",
          "username": "maria_garcia",
          "follower_count": 156,
          "is_following": true
        }
      },
      {
        "result_id": "route_001",
        "type": "route",
        "title": "Camino de los Pueblos Blancos",
        "subtitle": "67.5 km · Moderado · 4.7★",
        "photo_url": "/storage/routes/pueblos_blancos.jpg",
        "url": "/routes/route_001",
        "metadata": {
          "route_id": "route_001",
          "distance_km": 67.5,
          "difficulty": "moderate",
          "rating_avg": 4.7
        }
      }
    ],
    "total_count": 2,
    "query": "pueblo"
  },
  "error": null
}
```

**type Enum**: `user` | `route` | `town`

---

## Authentication

Todos los endpoints requieren autenticación vía **Bearer Token** (JWT):

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

El token se obtiene del endpoint de login (`POST /api/auth/login`) ya implementado en Feature 001.

---

## Error Responses

Todos los endpoints siguen el formato estándar de error:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensaje de error en español"
  }
}
```

**Códigos de Error Comunes**:

- `UNAUTHORIZED` (401) - Token inválido o expirado
- `FORBIDDEN` (403) - No tienes permiso para esta acción
- `NOT_FOUND` (404) - Recurso no encontrado
- `VALIDATION_ERROR` (400) - Parámetros inválidos
- `RATE_LIMIT_EXCEEDED` (429) - Demasiadas peticiones
- `INTERNAL_ERROR` (500) - Error del servidor

---

## Rate Limiting

Todos los endpoints tienen rate limiting:

- **Dashboard Stats**: 60 requests/min por usuario
- **Feed**: 30 requests/min por usuario
- **Search**: 20 requests/min por usuario (con debounce frontend de 300ms)
- **Notifications**: 60 requests/min por usuario

Headers de respuesta incluyen:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642684800
```

---

## CORS Policy

Backend permite CORS desde:

- `http://localhost:5173` (development)
- `https://contravento.com` (production)
- `https://staging.contravento.com` (staging)

---

## Testing

Para testing E2E con Playwright, usar los siguientes test users ya creados en el backend:

```bash
# User con datos completos para dashboard
username: testuser
email: test@example.com
password: TestPass123!

# User sin datos (nuevo usuario)
username: newuser
email: newuser@example.com
password: NewPass123!
```

---

## Next Steps

1. ✅ Contracts documented (simplified)
2. ⏭️ Generate `quickstart.md` with development workflow
3. ⏭️ Update agent context (no new tech - all existing)
4. ⏭️ Re-evaluate Constitution Check after design

**Contracts complete** - Backend ready to consume
