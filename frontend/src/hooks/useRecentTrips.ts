import { useState, useEffect } from 'react';
import { TripSummary } from '../types/trip';
import { getRecentTrips } from '../services/tripsService';

interface UseRecentTripsResult {
  trips: TripSummary[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for fetching recent published trips
 * @param username - Username to fetch trips for
 * @param limit - Number of trips to fetch (default: 5)
 */
export const useRecentTrips = (username: string, limit: number = 5): UseRecentTripsResult => {
  const [trips, setTrips] = useState<TripSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrips = async () => {
    if (!username) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getRecentTrips(username, limit);
      setTrips(data);
    } catch (err: any) {
      console.error('Error fetching recent trips:', err);
      setError(err.response?.data?.message || 'Error al cargar viajes recientes');
    } finally {
      setLoading(false);
    }
  };

  const refetch = async () => {
    await fetchTrips();
  };

  useEffect(() => {
    fetchTrips();
  }, [username, limit]);

  return {
    trips,
    loading,
    error,
    refetch,
  };
};
