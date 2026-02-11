/**
 * usePublicTrips Hook (Feature 013 - T026)
 *
 * Custom hook for fetching and managing public trips feed.
 * Handles loading state, error handling, and pagination.
 */

import { useState, useEffect } from 'react';
import { getPublicTrips } from '../services/tripService';
import { PublicTripSummary, PaginationInfo } from '../types/trip';

interface UsePublicTripsReturn {
  /** List of public trips */
  trips: PublicTripSummary[];

  /** Pagination metadata */
  pagination: PaginationInfo | null;

  /** Loading state */
  isLoading: boolean;

  /** Error message (Spanish) */
  error: string | null;

  /** Refetch trips (useful after data changes) */
  refetch: () => Promise<void>;
}

/**
 * Hook for fetching public trips feed
 *
 * @param page - Page number (1-indexed, default 1)
 * @param limit - Items per page (optional, uses backend default if not specified)
 * @returns Object with trips, pagination, loading, error, and refetch
 *
 * @example
 * const { trips, pagination, isLoading, error } = usePublicTrips(1);
 *
 * if (isLoading) return <LoadingSpinner />;
 * if (error) return <ErrorMessage message={error} />;
 *
 * return (
 *   <div>
 *     {trips.map(trip => <PublicTripCard key={trip.trip_id} trip={trip} />)}
 *   </div>
 * );
 */
export const usePublicTrips = (
  page: number = 1,
  limit?: number
): UsePublicTripsReturn => {
  const [trips, setTrips] = useState<PublicTripSummary[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTrips = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await getPublicTrips(page, limit);

      setTrips(response.trips);
      setPagination(response.pagination);
    } catch (err: any) {
      console.error('Error fetching public trips:', err);

      // Extract error message from API response
      const errorMessage =
        err.response?.data?.detail?.message ||
        err.message ||
        'Error al cargar los viajes públicos';

      setError(errorMessage);
      setTrips([]);
      setPagination(null);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch trips on mount and when page/limit changes
  useEffect(() => {
    fetchTrips();
  }, [page, limit]);

  // Listen for follow status changes to refetch trips (Feature 004 - US1)
  useEffect(() => {
    const handleFollowChange = () => {
      fetchTrips();
    };

    window.addEventListener('followStatusChanged', handleFollowChange);

    return () => {
      window.removeEventListener('followStatusChanged', handleFollowChange);
    };
  }, [page, limit]);

  // Listen for like changes to refetch trips (Feature 018 - US2 integration)
  useEffect(() => {
    const handleLikeChange = () => {
      fetchTrips();
    };

    window.addEventListener('likeChanged', handleLikeChange);

    return () => {
      window.removeEventListener('likeChanged', handleLikeChange);
    };
  }, [page, limit]);

  return {
    trips,
    pagination,
    isLoading,
    error,
    refetch: fetchTrips,
  };
};
