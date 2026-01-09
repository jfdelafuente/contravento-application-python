import { useState, useEffect } from 'react';
import { UserStats } from '../types/stats';
import { getUserStats } from '../services/statsService';

interface UseStatsResult {
  stats: UserStats | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for fetching and managing user statistics
 * Includes caching (5 minutes) and automatic refetch
 * @param username - Username to fetch stats for
 */
export const useStats = (username: string): UseStatsResult => {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<number>(0);

  const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

  useEffect(() => {
    const fetchStats = async () => {
      if (!username) {
        setLoading(false);
        return;
      }

      const now = Date.now();

      // Check if cached data is still valid
      if (stats && lastFetch && now - lastFetch < CACHE_DURATION) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await getUserStats(username);
        setStats(data);
        setLastFetch(now);
      } catch (err: any) {
        console.error('Error fetching stats:', err);
        setError(err.response?.data?.message || 'Error al cargar estadísticas');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  const refetch = async () => {
    setLastFetch(0); // Clear cache

    if (!username) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getUserStats(username);
      setStats(data);
      setLastFetch(Date.now());
    } catch (err: any) {
      console.error('Error fetching stats:', err);
      setError(err.response?.data?.message || 'Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  };

  return {
    stats,
    loading,
    error,
    refetch,
  };
};
