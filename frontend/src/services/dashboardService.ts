/**
 * Dashboard Service
 * Feature: 015-dashboard-redesign
 *
 * API service for dashboard endpoints (stats, feed, routes, challenges, notifications, search).
 */

import { api } from './api';
import type {
  DashboardStats,
  FeedResponse,
  SuggestedRoutesResponse,
  ChallengesResponse,
  SearchResponse,
} from '../types/dashboard';
import type { NotificationsResponse } from '../types/notifications';

// Backend response interfaces
interface BackendStatsResponse {
  total_trips: number;
  total_kilometers: number;
  countries_visited: Array<{ code: string; name: string }>;
  total_photos: number;
  achievements_count: number;
  last_trip_date: string | null;
  updated_at: string;
}

interface BackendProfileResponse {
  username: string;
  followers_count: number;
  following_count: number;
  // ... otros campos no necesarios para stats
}

// ============================================================================
// 1. Dashboard Statistics
// ============================================================================

/**
 * Obtiene las estadísticas personales del usuario por username
 * Combina datos de /users/{username}/stats y /users/{username}/profile
 * @param username - Nombre de usuario
 * @returns DashboardStats con total_trips, distance_km, followers_count, etc.
 */
export async function getDashboardStats(username: string): Promise<DashboardStats> {
  // Hacer ambas peticiones en paralelo para mejor performance
  const [statsResponse, profileResponse] = await Promise.all([
    api.get<{ success: boolean; data: BackendStatsResponse }>(`/users/${username}/stats`),
    api.get<BackendProfileResponse>(`/users/${username}/profile`), // Retorna directamente ProfileResponse
  ]);

  if (!statsResponse.data.success) {
    throw new Error('Error al obtener estadísticas del usuario');
  }

  const statsData = statsResponse.data.data;
  const profileData = profileResponse.data; // Acceso directo, no .data.data

  // Combinar datos de ambos endpoints
  const stats: DashboardStats = {
    user_id: '', // No disponible en estos endpoints
    username: username,
    total_trips: statsData.total_trips,
    total_distance_km: statsData.total_kilometers,
    towns_visited: 0, // TODO: Agregar al backend en Feature 015
    countries_visited: statsData.countries_visited.length,
    total_photos: statsData.total_photos,
    local_economic_impact_euros: null, // TODO: Calcular en backend Feature 015
    followers_count: profileData.followers_count, // ✅ Desde /profile
    following_count: profileData.following_count, // ✅ Desde /profile
    achievements_unlocked: statsData.achievements_count,
    achievements_total: 20, // TODO: Endpoint de logros totales disponibles
    last_updated: statsData.updated_at,
  };

  return stats;
}

// ============================================================================
// 2. Activity Feed
// ============================================================================

export interface FeedParams {
  page?: number;
  limit?: number;
}

/**
 * Obtiene el feed de actividad social (viajes publicados, logros, etc.)
 * @param params - Parámetros de paginación (page, limit)
 * @returns FeedResponse con items, total_count, has_next
 */
export async function getActivityFeed(params: FeedParams = {}): Promise<FeedResponse> {
  const { page = 1, limit = 50 } = params;

  const response = await api.get<{ success: boolean; data: FeedResponse }>(
    '/api/v1/dashboard/feed',
    {
      params: { page, limit },
    }
  );

  if (!response.data.success) {
    throw new Error('Error al obtener feed de actividad');
  }

  return response.data.data;
}

// ============================================================================
// 3. Suggested Routes
// ============================================================================

export interface SuggestedRoutesParams {
  limit?: number;
}

/**
 * Obtiene rutas sugeridas para el usuario basadas en historial y preferencias
 * @param params - Parámetros de consulta (limit)
 * @returns SuggestedRoutesResponse con routes, total_available
 */
export async function getSuggestedRoutes(
  params: SuggestedRoutesParams = {}
): Promise<SuggestedRoutesResponse> {
  const { limit = 5 } = params;

  const response = await api.get<{ success: boolean; data: SuggestedRoutesResponse }>(
    '/api/v1/dashboard/suggested-routes',
    {
      params: { limit },
    }
  );

  if (!response.data.success) {
    throw new Error('Error al obtener rutas sugeridas');
  }

  return response.data.data;
}

// ============================================================================
// 4. Active Challenges
// ============================================================================

/**
 * Obtiene los desafíos activos del usuario
 * @returns ChallengesResponse con challenges, total_active, total_completed_all_time
 */
export async function getActiveChallenges(): Promise<ChallengesResponse> {
  const response = await api.get<{ success: boolean; data: ChallengesResponse }>(
    '/api/v1/dashboard/challenges'
  );

  if (!response.data.success) {
    throw new Error('Error al obtener desafíos activos');
  }

  return response.data.data;
}

// ============================================================================
// 5. Notifications
// ============================================================================

export interface NotificationsParams {
  unread?: boolean;
  limit?: number;
}

/**
 * Obtiene las notificaciones del usuario
 * @param params - Parámetros de consulta (unread, limit)
 * @returns NotificationsResponse con notifications, total_unread, total_count
 */
export async function getNotifications(
  params: NotificationsParams = {}
): Promise<NotificationsResponse> {
  const { unread, limit = 20 } = params;

  const response = await api.get<{ success: boolean; data: NotificationsResponse }>(
    '/api/v1/dashboard/notifications',
    {
      params: {
        ...(unread !== undefined && { unread }),
        limit,
      },
    }
  );

  if (!response.data.success) {
    throw new Error('Error al obtener notificaciones');
  }

  return response.data.data;
}

/**
 * Marca una notificación como leída
 * @param notificationId - ID de la notificación a marcar
 */
export async function markNotificationAsRead(notificationId: string): Promise<void> {
  const response = await api.patch<{ success: boolean }>(
    `/api/v1/dashboard/notifications/${notificationId}/read`
  );

  if (!response.data.success) {
    throw new Error('Error al marcar notificación como leída');
  }
}

/**
 * Marca todas las notificaciones como leídas
 */
export async function markAllNotificationsAsRead(): Promise<void> {
  const response = await api.post<{ success: boolean }>(
    '/api/v1/dashboard/notifications/mark-all-read'
  );

  if (!response.data.success) {
    throw new Error('Error al marcar todas las notificaciones como leídas');
  }
}

// ============================================================================
// 6. Global Search
// ============================================================================

export interface SearchParams {
  query: string;
  types?: ('user' | 'route' | 'town')[];
  limit?: number;
}

/**
 * Realiza una búsqueda global en usuarios, rutas y pueblos
 * @param params - Parámetros de búsqueda (query, types, limit)
 * @returns SearchResponse con results, total_count, query
 */
export async function globalSearch(params: SearchParams): Promise<SearchResponse> {
  const { query, types = ['user', 'route', 'town'], limit = 10 } = params;

  const response = await api.get<{ success: boolean; data: SearchResponse }>(
    '/api/v1/dashboard/search',
    {
      params: {
        q: query,
        types: types.join(','),
        limit,
      },
    }
  );

  if (!response.data.success) {
    throw new Error('Error al realizar búsqueda global');
  }

  return response.data.data;
}
