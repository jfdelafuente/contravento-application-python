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
