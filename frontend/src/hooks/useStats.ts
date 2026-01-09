import { useState, useEffect } from 'react';
import { UserStats } from '../types/stats';
import { getMyStats } from '../services/statsService';

interface UseStatsResult {
  stats: UserStats | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for fetching and managing user statistics
 * Includes caching (5 minutes) and automatic refetch
 */
export const useStats = (): UseStatsResult => {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastFetch, setLastFetch] = useState<number>(0);

  const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds

  const fetchStats = async () => {
    const now = Date.now();

    // Check if cached data is still valid
    if (stats && lastFetch && now - lastFetch < CACHE_DURATION) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getMyStats();
      setStats(data);
      setLastFetch(now);
    } catch (err: any) {
      console.error('Error fetching stats:', err);
      setError(err.response?.data?.message || 'Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  };

  const refetch = async () => {
    setLastFetch(0); // Clear cache
    await fetchStats();
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return {
    stats,
    loading,
    error,
    refetch,
  };
};
