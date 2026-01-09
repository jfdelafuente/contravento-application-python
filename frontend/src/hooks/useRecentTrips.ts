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

  useEffect(() => {
    const fetchTrips = async () => {
      if (!username) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const data = await getRecentTrips(username, limit);

        // Ensure data is an array
        if (Array.isArray(data)) {
          setTrips(data);
        } else {
          console.warn('Unexpected trips data format:', data);
          setTrips([]);
        }
      } catch (err: any) {
        console.error('Error fetching recent trips:', err);
        setError(err.response?.data?.message || 'Error al cargar viajes recientes');
        setTrips([]); // Ensure trips is always an array
      } finally {
        setLoading(false);
      }
    };

    fetchTrips();
  }, [username, limit]);

  const refetch = async () => {
    if (!username) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await getRecentTrips(username, limit);

      if (Array.isArray(data)) {
        setTrips(data);
      } else {
        console.warn('Unexpected trips data format:', data);
        setTrips([]);
      }
    } catch (err: any) {
      console.error('Error fetching recent trips:', err);
      setError(err.response?.data?.message || 'Error al cargar viajes recientes');
      setTrips([]);
    } finally {
      setLoading(false);
    }
  };

  return {
    trips,
    loading,
    error,
    refetch,
  };
};
