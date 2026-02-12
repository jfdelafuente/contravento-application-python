import { api } from './api';
import { UserStats } from '../types/stats';

interface StatsApiResponse {
  success: boolean;
  data: UserStats;
  error: null | any;
}

/**
 * Fetch user's statistics by username
 * @param username - Username to fetch stats for
 */
export const getUserStats = async (username: string): Promise<UserStats> => {
  const response = await api.get<StatsApiResponse>(`/users/${username}/stats`);
  return response.data.data;
};
