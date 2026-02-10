/**
 * Activity Like Service (Feature 018 - US2)
 *
 * API client for liking/unliking activity feed items.
 */

import { api } from './api';

export interface LikeActivityResponse {
  like_id: string;
  user_id: string;
  activity_id: string;
  created_at: string;
}

export interface ActivityLikeWithUser {
  like_id: string;
  user_id: string;
  username: string;
  user_photo_url: string | null;
  created_at: string;
}

export interface ActivityLikesListResponse {
  likes: ActivityLikeWithUser[];
  total_count: number;
  page: number;
  limit: number;
  has_next: boolean;
}

/**
 * Like an activity feed item.
 *
 * Idempotent: Returns existing like if already liked.
 *
 * @param activityId - Activity ID to like
 * @returns Promise with like details
 */
export const likeActivity = async (
  activityId: string
): Promise<LikeActivityResponse> => {
  const response = await api.post<LikeActivityResponse>(
    `/activities/${activityId}/like`
  );
  return response.data;
};

/**
 * Unlike an activity feed item.
 *
 * Idempotent: Returns success even if not liked.
 *
 * @param activityId - Activity ID to unlike
 * @returns Promise (void)
 */
export const unlikeActivity = async (activityId: string): Promise<void> => {
  await api.delete(`/activities/${activityId}/like`);
};

/**
 * Get users who liked an activity.
 *
 * @param activityId - Activity ID
 * @param page - Page number (1-indexed)
 * @param limit - Items per page
 * @returns Promise with paginated likes list
 */
export const getActivityLikes = async (
  activityId: string,
  page: number = 1,
  limit: number = 20
): Promise<ActivityLikesListResponse> => {
  const response = await api.get<ActivityLikesListResponse>(
    `/activities/${activityId}/likes`,
    {
      params: { page, limit },
    }
  );
  return response.data;
};
