// src/services/followService.ts

import apiClient from './apiClient';

/**
 * Follow Service - API calls for follow/unfollow functionality.
 *
 * Endpoints:
 * - POST /social/follow/{user_id} - Follow a user
 * - DELETE /social/unfollow/{user_id} - Unfollow a user
 *
 * Backend integration with SocialService (Feature 004 - US1).
 */

/**
 * Follow a user.
 *
 * @param userId - ID of the user to follow
 * @throws Error if API call fails
 */
export const followUser = async (userId: string): Promise<void> => {
  await apiClient.post(`/social/follow/${userId}`);
};

/**
 * Unfollow a user.
 *
 * @param userId - ID of the user to unfollow
 * @throws Error if API call fails
 */
export const unfollowUser = async (userId: string): Promise<void> => {
  await apiClient.delete(`/social/unfollow/${userId}`);
};

/**
 * Get followers list for a user.
 *
 * @param userId - ID of the user
 * @returns Array of follower user objects
 */
export const getFollowers = async (userId: string): Promise<any[]> => {
  const response = await apiClient.get(`/social/${userId}/followers`);
  return response.data.data;
};

/**
 * Get following list for a user.
 *
 * @param userId - ID of the user
 * @returns Array of following user objects
 */
export const getFollowing = async (userId: string): Promise<any[]> => {
  const response = await apiClient.get(`/social/${userId}/following`);
  return response.data.data;
};

/**
 * Check if current user follows a specific user.
 *
 * @param userId - ID of the user to check
 * @returns true if following, false otherwise
 */
export const checkIsFollowing = async (userId: string): Promise<boolean> => {
  try {
    const response = await apiClient.get(`/social/following/${userId}/check`);
    return response.data.data.is_following;
  } catch {
    return false;
  }
};
