// src/services/followService.ts

import { api } from './api';

/**
 * Follow Service - API calls for follow/unfollow functionality (Feature 004 - US1).
 *
 * Endpoints:
 * - POST /users/{username}/follow - Follow a user
 * - DELETE /users/{username}/follow - Unfollow a user
 * - GET /users/{username}/followers - Get user's followers
 * - GET /users/{username}/following - Get users that user follows
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
 * @param username - Username of the user to follow
 * @returns Follow details
 * @throws Error if already following, self-follow, or unauthorized
 */
export async function followUser(username: string): Promise<FollowResponse> {
  const response = await api.post<FollowResponse>(`/users/${username}/follow`);
  return response.data;
}

/**
 * Unfollow a user.
 *
 * @param username - Username of the user to unfollow
 * @returns Success response
 * @throws Error if not following or unauthorized
 */
export async function unfollowUser(username: string): Promise<UnfollowResponse> {
  const response = await api.delete<UnfollowResponse>(`/users/${username}/follow`);
  return response.data;
}

/**
 * Get followers list for a user.
 *
 * Public endpoint (no auth required).
 *
 * @param username - Username of the user
 * @returns List of followers
 */
export async function getFollowers(username: string): Promise<FollowersListResponse> {
  const response = await api.get<FollowersListResponse>(`/users/${username}/followers`);
  return response.data;
}

/**
 * Get following list for a user.
 *
 * Public endpoint (no auth required).
 *
 * @param username - Username of the user
 * @returns List of users being followed
 */
export async function getFollowing(username: string): Promise<FollowingListResponse> {
  const response = await api.get<FollowingListResponse>(`/users/${username}/following`);
  return response.data;
}
