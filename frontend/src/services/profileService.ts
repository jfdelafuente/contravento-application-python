import { api } from './api';

interface ProfileResponse {
  success: boolean;
  data: {
    user_id: string;
    username: string;
    email: string;
    full_name?: string;
    bio?: string;
    location?: string;
    cycling_type?: string;
    photo_url?: string;
    is_public: boolean;
    followers_count: number;
    following_count: number;
    created_at: string;
  };
  error: null | any;
}

/**
 * Fetch user's public profile by username
 * @param username - Username to fetch profile for
 */
export const getUserProfile = async (username: string): Promise<ProfileResponse['data']> => {
  const response = await api.get<ProfileResponse>(`/users/${username}/profile`);
  return response.data.data;
};
