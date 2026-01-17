// src/services/likeService.ts

import api from './api';

/**
 * LikeService - API client for likes endpoints (Feature 004 - US2).
 *
 * Endpoints:
 * - POST /trips/{id}/like: Like a trip
 * - DELETE /trips/{id}/like: Unlike a trip
 * - GET /trips/{id}/likes: Get users who liked a trip
 */

export interface LikeResponse {
  like_id: string;
  user_id: string;
  trip_id: string;
  created_at: string;
}

export interface UserSummaryForLike {
  username: string;
  profile_photo_url: string | null;
}

export interface LikeItem {
  user: UserSummaryForLike;
  created_at: string;
}

export interface LikesListResponse {
  likes: LikeItem[];
  total_count: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface UnlikeResponse {
  success: boolean;
  message: string;
}

/**
 * Like a trip (T059).
 *
 * @param tripId - Trip ID to like
 * @returns Like details
 * @throws Error if already liked, self-like, or unauthorized
 */
export async function likeTrip(tripId: string): Promise<LikeResponse> {
  const response = await api.post<{ data: LikeResponse }>(`/trips/${tripId}/like`);
  return response.data.data;
}

/**
 * Unlike a trip (T059).
 *
 * @param tripId - Trip ID to unlike
 * @returns Success response
 * @throws Error if not liked or unauthorized
 */
export async function unlikeTrip(tripId: string): Promise<UnlikeResponse> {
  const response = await api.delete<{ data: UnlikeResponse }>(`/trips/${tripId}/like`);
  return response.data.data;
}

/**
 * Get users who liked a trip (T059).
 *
 * Public endpoint (no auth required).
 *
 * @param tripId - Trip ID
 * @param page - Page number (default 1)
 * @param limit - Items per page (default 20, max 50)
 * @returns Paginated list of likes
 */
export async function getTripLikes(
  tripId: string,
  page: number = 1,
  limit: number = 20
): Promise<LikesListResponse> {
  const response = await api.get<{ data: LikesListResponse }>(`/trips/${tripId}/likes`, {
    params: { page, limit },
  });
  return response.data.data;
}
