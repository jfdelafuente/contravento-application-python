import { useState, useEffect } from 'react';
import { getUserTrips } from '../services/tripsService';

/**
 * Monthly statistics calculated from current month's trips
 */
export interface MonthStats {
  /** Number of trips published this month */
  tripCount: number;

  /** Total distance traveled this month (km) */
  totalDistance: number;

  /** Total elevation gain this month (m) */
  totalElevationGain: number;
}

interface UseMonthStatsResult {
  monthStats: MonthStats | null;
  loading: boolean;
  error: string | null;
}

/**
 * Custom hook for fetching current month's trip statistics
 *
 * Calculates stats from user's published trips in the current month:
 * - Trip count
 * - Total distance
 * - Total elevation gain (from GPX files)
 *
 * @param username - Username to fetch stats for
 * @returns Month statistics with loading/error state
 */
export const useMonthStats = (username: string): UseMonthStatsResult => {
  const [monthStats, setMonthStats] = useState<MonthStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMonthStats = async () => {
      if (!username) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        // Fetch all published trips for the user
        const trips = await getUserTrips({
          username,
          status: 'published',
        });

        // Get current month date range
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth(); // 0-indexed (0 = January, 11 = December)

        // Filter trips that started in the current month
        const monthTrips = trips.filter((trip) => {
          const tripDate = new Date(trip.start_date);
          return (
            tripDate.getFullYear() === currentYear &&
            tripDate.getMonth() === currentMonth
          );
        });

        // Calculate statistics
        const tripCount = monthTrips.length;
        const totalDistance = monthTrips.reduce((sum, trip) => {
          return sum + (trip.distance_km || 0);
        }, 0);

        // Calculate total elevation gain from GPX files
        const totalElevationGain = monthTrips.reduce((sum, trip) => {
          // @ts-expect-error - TODO: Add gpx_file to TripListItem interface
          if (trip.gpx_file && trip.gpx_file.elevation_gain) {
            // @ts-expect-error - TODO: Add gpx_file to TripListItem interface
            return sum + trip.gpx_file.elevation_gain;
          }
          return sum;
        }, 0);

        setMonthStats({
          tripCount,
          totalDistance: Math.round(totalDistance * 10) / 10, // Round to 1 decimal
          totalElevationGain: Math.round(totalElevationGain), // Round to integer
        });
      } catch (err: any) {
        console.error('Error fetching month stats:', err);
        setError(err.response?.data?.message || 'Error al cargar estadísticas del mes');
      } finally {
        setLoading(false);
      }
    };

    fetchMonthStats();
  }, [username]);

  return {
    monthStats,
    loading,
    error,
  };
};
