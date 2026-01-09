import { api } from './api';
import { UserStats } from '../types/stats';

/**
 * Fetch current user's statistics
 */
export const getMyStats = async (): Promise<UserStats> => {
  const response = await api.get<UserStats>('/api/stats/me');
  return response.data;
};
