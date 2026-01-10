import { api } from './api';

interface ProfileData {
  username: string;
  full_name?: string | null;
  bio?: string | null;
  location?: string | null;
  cycling_type?: string | null;
  photo_url?: string | null;
  show_email: boolean;
  show_location: boolean;
  followers_count: number;
  following_count: number;
  stats: {
    total_trips: number;
    total_kilometers: number;
    achievements_count: number;
  };
  created_at: string;
}

/**
 * Fetch user's public profile by username
 * @param username - Username to fetch profile for
 */
export const getUserProfile = async (username: string): Promise<ProfileData> => {
  const response = await api.get<ProfileData>(`/users/${username}/profile`);
  return response.data;
};

// ============================================================================
// Profile Management Functions
// ============================================================================

import type {
  UserProfile,
  ProfileUpdateRequest,
  PrivacySettingsUpdate,
  PasswordChangeRequest,
} from '../types/profile';

/**
 * Update current user's profile information
 * Endpoint: PUT /api/users/{username}/profile
 */
export const updateProfile = async (username: string, data: ProfileUpdateRequest): Promise<UserProfile> => {
  const response = await api.put<{ success: boolean; data: UserProfile }>(`/users/${username}/profile`, data);
  return response.data.data;
};

/**
 * Update current user's privacy settings
 * Endpoint: PUT /api/profile/me
 * Note: Privacy settings are part of the same profile endpoint
 */
export const updatePrivacy = async (data: PrivacySettingsUpdate): Promise<UserProfile> => {
  const response = await api.put<{ success: boolean; data: UserProfile }>('/profile/me', data);
  return response.data.data;
};

/**
 * Change current user's password
 * Endpoint: PUT /api/profile/me/password
 */
export const changePassword = async (data: PasswordChangeRequest): Promise<{ message: string }> => {
  const response = await api.put<{ success: boolean; message: string }>('/profile/me/password', data);
  return { message: response.data.message };
};

/**
 * Get current user's profile
 * Endpoint: GET /api/profile/me
 */
export const getMyProfile = async (): Promise<UserProfile> => {
  const response = await api.get<{ success: boolean; data: UserProfile }>('/profile/me');
  return response.data.data;
};

/**
 * Get user profile by username
 * Endpoint: GET /api/users/{username}/profile
 *
 * @param username - Username of the profile to fetch
 * @returns Complete user profile data
 */
export const getProfile = async (username: string): Promise<UserProfile> => {
  const response = await api.get<{ success: boolean; data: UserProfile }>(`/users/${username}/profile`);
  return response.data.data;
};
