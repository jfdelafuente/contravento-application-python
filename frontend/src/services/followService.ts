// src/services/followService.ts

import { api } from './api';

/**
 * Follow Service - API calls for follow/unfollow functionality (Feature 004 - US1).
 *
 * Endpoints:
 * - POST /social/follow/{user_id} - Follow a user
 * - DELETE /social/unfollow/{user_id} - Unfollow a user
 * - GET /social/{user_id}/followers - Get user's followers
 * - GET /social/{user_id}/following - Get users that user follows
 *
 * Backend integration with SocialService.
 */

export interface FollowResponse {
  follower_id: string;
  following_id: string;
  created_at: string;
}

export interface UnfollowResponse {
  success: boolean;
  message: string;
}

export interface UserSummaryForFollow {
  user_id: string;
  username: string;
  profile_photo_url: string | null;
}

export interface FollowersListResponse {
  followers: UserSummaryForFollow[];
  total_count: number;
}

export interface FollowingListResponse {
  following: UserSummaryForFollow[];
  total_count: number;
}

/**
 * Follow a user.
 *
 * @param userId - ID of the user to follow
 * @returns Follow details
 * @throws Error if already following, self-follow, or unauthorized
 */
export async function followUser(userId: string): Promise<FollowResponse> {
  const response = await api.post<FollowResponse>(`/social/follow/${userId}`);
  return response.data;
}

/**
 * Unfollow a user.
 *
 * @param userId - ID of the user to unfollow
 * @returns Success response
 * @throws Error if not following or unauthorized
 */
export async function unfollowUser(userId: string): Promise<UnfollowResponse> {
  const response = await api.delete<UnfollowResponse>(`/social/unfollow/${userId}`);
  return response.data;
}

/**
 * Get followers list for a user.
 *
 * Public endpoint (no auth required).
 *
 * @param userId - ID of the user
 * @returns List of followers
 */
export async function getFollowers(userId: string): Promise<FollowersListResponse> {
  const response = await api.get<FollowersListResponse>(`/social/${userId}/followers`);
  return response.data;
}

/**
 * Get following list for a user.
 *
 * Public endpoint (no auth required).
 *
 * @param userId - ID of the user
 * @returns List of users being followed
 */
export async function getFollowing(userId: string): Promise<FollowingListResponse> {
  const response = await api.get<FollowingListResponse>(`/social/${userId}/following`);
  return response.data;
}
