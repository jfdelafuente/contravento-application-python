# Data Model: Dashboard Redesign (Frontend)

**Feature**: 015-dashboard-redesign
**Phase**: 1 - Design
**Date**: 2026-01-20

## Overview

Este documento define el modelo de datos **frontend** (TypeScript interfaces) para el dashboard mejorado. El backend (Python/FastAPI) ya está implementado y retorna estas estructuras vía API REST.

**Nota importante**: Este NO es un modelo de base de datos (backend), sino las interfaces TypeScript que el frontend usa para consumir los endpoints.

---

## 1. Dashboard Statistics (Personal Stats)

**Fuente**: `GET /api/v1/dashboard/stats`

```typescript
// frontend/src/types/dashboard.ts

export interface DashboardStats {
  user_id: string;
  username: string;
  total_trips: number;
  total_distance_km: number;
  towns_visited: number;
  countries_visited: number;
  total_photos: number;
  local_economic_impact_euros: number | null;
  followers_count: number;
  following_count: number;
  achievements_unlocked: number;
  achievements_total: number;
  last_updated: string; // ISO 8601 date
}

// Example response:
// {
//   "user_id": "550e8400-e29b-41d4-a716-446655440000",
//   "username": "ciclista_aventurero",
//   "total_trips": 42,
//   "total_distance_km": 3547.5,
//   "towns_visited": 87,
//   "countries_visited": 12,
//   "total_photos": 324,
//   "local_economic_impact_euros": 2850.00,
//   "followers_count": 156,
//   "following_count": 89,
//   "achievements_unlocked": 7,
//   "achievements_total": 15,
//   "last_updated": "2026-01-20T14:30:00Z"
// }
```

---

## 2. Activity Feed (Social Feed)

**Fuente**: `GET /api/v1/dashboard/feed?page=1&limit=50`

```typescript
// frontend/src/types/dashboard.ts

export type FeedActivityType =
  | 'trip_published'
  | 'achievement_unlocked'
  | 'challenge_completed'
  | 'comment_added'
  | 'like_received';

export interface FeedItem {
  activity_id: string;
  activity_type: FeedActivityType;
  actor_user_id: string;
  actor_username: string;
  actor_photo_url: string | null;
  timestamp: string; // ISO 8601 date

  // Polymorphic content based on activity_type
  content: TripPublishedContent | AchievementContent | ChallengeContent | CommentContent | LikeContent;
}

export interface TripPublishedContent {
  trip_id: string;
  trip_title: string;
  trip_cover_photo_url: string | null;
  trip_distance_km: number;
  trip_countries: string[];
}

export interface AchievementContent {
  achievement_id: string;
  achievement_name: string;
  achievement_icon_url: string;
  achievement_description: string;
}

export interface ChallengeContent {
  challenge_id: string;
  challenge_name: string;
  challenge_icon_url: string;
}

export interface CommentContent {
  trip_id: string;
  trip_title: string;
  comment_text: string;
}

export interface LikeContent {
  trip_id: string;
  trip_title: string;
  trip_cover_photo_url: string | null;
}

export interface FeedResponse {
  items: FeedItem[];
  total_count: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

// Example response:
// {
//   "items": [
//     {
//       "activity_id": "act_123",
//       "activity_type": "trip_published",
//       "actor_user_id": "user_456",
//       "actor_username": "maria_garcia",
//       "actor_photo_url": "/storage/profile_photos/maria.jpg",
//       "timestamp": "2026-01-20T10:15:00Z",
//       "content": {
//         "trip_id": "trip_789",
//         "trip_title": "Ruta de los Molinos",
//         "trip_cover_photo_url": "/storage/trips/molinos_cover.jpg",
//         "trip_distance_km": 45.3,
//         "trip_countries": ["España"]
//       }
//     }
//   ],
//   "total_count": 324,
//   "page": 1,
//   "page_size": 50,
//   "has_next": true
// }
```

---

## 3. Suggested Routes (Recommendations)

**Fuente**: `GET /api/v1/dashboard/suggested-routes?limit=5`

```typescript
// frontend/src/types/dashboard.ts

export type RouteDifficulty = 'easy' | 'moderate' | 'hard' | 'expert';

export interface SuggestedRoute {
  route_id: string;
  title: string;
  description: string;
  distance_km: number;
  difficulty: RouteDifficulty;
  estimated_duration_hours: number;
  cover_photo_url: string | null;

  // Why this route is suggested
  reason: string; // e.g., "Incluye pueblos que no has visitado", "Popular entre ciclistas que sigues"

  // Route metadata
  towns_included: string[];
  countries: string[];
  rating_avg: number; // 0-5
  completed_by_count: number;

  // User context
  is_completed: boolean;
  is_saved: boolean;
}

export interface SuggestedRoutesResponse {
  routes: SuggestedRoute[];
  total_available: number;
}

// Example response:
// {
//   "routes": [
//     {
//       "route_id": "route_001",
//       "title": "Camino de los Pueblos Blancos",
//       "description": "Ruta por los pueblos blancos de Andalucía...",
//       "distance_km": 67.5,
//       "difficulty": "moderate",
//       "estimated_duration_hours": 5.5,
//       "cover_photo_url": "/storage/routes/pueblos_blancos.jpg",
//       "reason": "Incluye 3 pueblos que no has visitado",
//       "towns_included": ["Grazalema", "Zahara de la Sierra", "Setenil"],
//       "countries": ["España"],
//       "rating_avg": 4.7,
//       "completed_by_count": 234,
//       "is_completed": false,
//       "is_saved": false
//     }
//   ],
//   "total_available": 47
// }
```

---

## 4. Active Challenges (Gamification)

**Fuente**: `GET /api/v1/dashboard/challenges`

```typescript
// frontend/src/types/dashboard.ts

export type ChallengeStatus = 'in_progress' | 'completed' | 'failed' | 'expired';

export interface ActiveChallenge {
  challenge_id: string;
  name: string;
  description: string;
  icon_url: string;
  status: ChallengeStatus;

  // Progress tracking
  current_progress: number;
  required_progress: number;
  progress_unit: string; // e.g., "comercios visitados", "kilómetros recorridos"

  // Dates
  started_at: string; // ISO 8601
  expires_at: string | null; // null if no expiration
  completed_at: string | null;

  // Rewards
  reward_achievement_id: string | null;
  reward_achievement_name: string | null;
}

export interface ChallengesResponse {
  challenges: ActiveChallenge[];
  total_active: number;
  total_completed_all_time: number;
}

// Example response:
// {
//   "challenges": [
//     {
//       "challenge_id": "chal_001",
//       "name": "Comercios Rurales",
//       "description": "Visita 5 comercios locales y documéntalos",
//       "icon_url": "/icons/shop.svg",
//       "status": "in_progress",
//       "current_progress": 3,
//       "required_progress": 5,
//       "progress_unit": "comercios visitados",
//       "started_at": "2026-01-15T00:00:00Z",
//       "expires_at": "2026-02-15T23:59:59Z",
//       "completed_at": null,
//       "reward_achievement_id": "ach_shop_explorer",
//       "reward_achievement_name": "Explorador de Comercios"
//     }
//   ],
//   "total_active": 2,
//   "total_completed_all_time": 15
// }
```

---

## 5. Notifications (Alerts & Updates)

**Fuente**: `GET /api/v1/dashboard/notifications?unread=true&limit=20`

```typescript
// frontend/src/types/notifications.ts

export type NotificationType =
  | 'like'
  | 'comment'
  | 'new_follower'
  | 'challenge_completed'
  | 'achievement_unlocked'
  | 'security_alert';

export type NotificationPriority = 'low' | 'medium' | 'high';

export interface Notification {
  notification_id: string;
  type: NotificationType;
  priority: NotificationPriority;
  title: string;
  message: string;
  icon_url: string | null;

  // Metadata
  created_at: string; // ISO 8601
  is_read: boolean;
  read_at: string | null;

  // Action link (optional)
  action_url: string | null; // e.g., "/trips/trip_123", "/profile/user_456"
  action_text: string | null; // e.g., "Ver viaje", "Ver perfil"

  // Actor (who triggered the notification)
  actor_user_id: string | null;
  actor_username: string | null;
  actor_photo_url: string | null;
}

export interface NotificationsResponse {
  notifications: Notification[];
  total_unread: number;
  total_count: number;
}

// Example response:
// {
//   "notifications": [
//     {
//       "notification_id": "notif_001",
//       "type": "like",
//       "priority": "low",
//       "title": "Nuevo like en tu viaje",
//       "message": "A maria_garcia le gustó tu viaje 'Ruta de los Molinos'",
//       "icon_url": "/icons/heart.svg",
//       "created_at": "2026-01-20T14:30:00Z",
//       "is_read": false,
//       "read_at": null,
//       "action_url": "/trips/trip_789",
//       "action_text": "Ver viaje",
//       "actor_user_id": "user_456",
//       "actor_username": "maria_garcia",
//       "actor_photo_url": "/storage/profile_photos/maria.jpg"
//     }
//   ],
//   "total_unread": 5,
//   "total_count": 127
// }
```

---

## 6. Global Search (Autocomplete)

**Fuente**: `GET /api/v1/dashboard/search?q={query}&types=users,routes,towns&limit=10`

```typescript
// frontend/src/types/dashboard.ts

export type SearchResultType = 'user' | 'route' | 'town';

export interface SearchResult {
  result_id: string;
  type: SearchResultType;
  title: string;
  subtitle: string | null;
  photo_url: string | null;
  url: string; // Frontend route to navigate to

  // Type-specific metadata
  metadata: UserMetadata | RouteMetadata | TownMetadata;
}

export interface UserMetadata {
  user_id: string;
  username: string;
  follower_count: number;
  is_following: boolean;
}

export interface RouteMetadata {
  route_id: string;
  distance_km: number;
  difficulty: RouteDifficulty;
  rating_avg: number;
}

export interface TownMetadata {
  town_id: string;
  country: string;
  visit_count: number; // How many users visited
}

export interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  query: string;
}

// Example response:
// {
//   "results": [
//     {
//       "result_id": "user_456",
//       "type": "user",
//       "title": "maria_garcia",
//       "subtitle": "156 seguidores · Madrid, España",
//       "photo_url": "/storage/profile_photos/maria.jpg",
//       "url": "/profile/maria_garcia",
//       "metadata": {
//         "user_id": "user_456",
//         "username": "maria_garcia",
//         "follower_count": 156,
//         "is_following": true
//       }
//     },
//     {
//       "result_id": "route_001",
//       "type": "route",
//       "title": "Camino de los Pueblos Blancos",
//       "subtitle": "67.5 km · Moderado · 4.7★",
//       "photo_url": "/storage/routes/pueblos_blancos.jpg",
//       "url": "/routes/route_001",
//       "metadata": {
//         "route_id": "route_001",
//         "distance_km": 67.5,
//         "difficulty": "moderate",
//         "rating_avg": 4.7
//       }
//     }
//   ],
//   "total_count": 2,
//   "query": "pueblo"
// }
```

---

## 7. Component State Models (Local State)

Estas interfaces NO vienen del backend - son para estado local del frontend:

```typescript
// frontend/src/types/dashboard.ts

// Responsive layout state
export type LayoutMode = 'mobile' | 'tablet' | 'desktop' | 'wide';

// Dashboard tab/section state (si usamos tabs en mobile)
export type DashboardSection =
  | 'overview'      // Stats + Feed (P1)
  | 'routes'        // Suggested routes (P2)
  | 'challenges'    // Active challenges (P3)
  | 'notifications'; // Notifications panel (P3)

// Search bar state
export interface SearchState {
  query: string;
  results: SearchResult[];
  isSearching: boolean;
  isOpen: boolean; // Dropdown open/closed
  selectedIndex: number; // For keyboard navigation
}

// Notification panel state
export interface NotificationPanelState {
  isOpen: boolean;
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
}

// Feed pagination state
export interface FeedPaginationState {
  page: number;
  pageSize: number;
  hasMore: boolean;
  isLoadingMore: boolean;
}
```

---

## API Response Standardization

Todos los endpoints siguen la estructura estándar del backend:

```typescript
// frontend/src/types/api.ts

export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  error: null;
}

export interface ApiErrorResponse {
  success: false;
  data: null;
  error: {
    code: string;
    message: string;
    field?: string;
  };
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

// Usage in services:
// const response = await axios.get<ApiSuccessResponse<DashboardStats>>('/api/v1/dashboard/stats');
// return response.data.data; // Unwrap the "data" field
```

---

## Validation Rules (Frontend)

Aunque el backend valida, el frontend debe validar para mejor UX:

```typescript
// frontend/src/utils/validation.ts

export const VALIDATION_RULES = {
  SEARCH_QUERY: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 100,
    PATTERN: /^[a-zA-Z0-9\sáéíóúñÁÉÍÓÚÑ_-]+$/,
  },

  NOTIFICATION_PANEL: {
    MAX_VISIBLE: 20,
    UNREAD_BADGE_MAX: 99, // Show "99+" if more
  },

  FEED: {
    PAGE_SIZE: 50,
    MAX_PAGES: 10, // Prevent infinite scroll beyond 500 items
  },
} as const;
```

---

## Type Guards & Utilities

```typescript
// frontend/src/types/dashboard.ts

// Type guard for feed content
export function isTripPublishedContent(content: any): content is TripPublishedContent {
  return 'trip_id' in content && 'trip_title' in content;
}

export function isAchievementContent(content: any): content is AchievementContent {
  return 'achievement_id' in content && 'achievement_name' in content;
}

// Type guard for API responses
export function isApiSuccess<T>(response: ApiResponse<T>): response is ApiSuccessResponse<T> {
  return response.success === true;
}

// Usage:
// if (isTripPublishedContent(feedItem.content)) {
//   console.log(feedItem.content.trip_title); // TypeScript knows this is safe
// }
```

---

## Summary

**Total Interfaces**: 20+ TypeScript interfaces definidas

**Endpoints Consumed**: 6 endpoints del backend (ya implementados)

**No Backend Changes Required**: ✅ Backend ya expone todos los endpoints necesarios

**Next Step**: Crear contratos API en `contracts/*.yaml` (OpenAPI spec)
