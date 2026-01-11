/**
 * useTripList Hook
 *
 * Custom hook for fetching and managing trips list with pagination.
 * Handles loading states, errors, and automatic refetching when filters change.
 *
 * Used in:
 * - TripsListPage (main trips grid)
 * - ProfilePage (user's recent trips)
 */

import { useState, useEffect, useCallback } from 'react';
import { TripListItem, TripListResponse } from '../types/trip';
import { getUserTrips } from '../services/tripService';
import toast from 'react-hot-toast';

interface UseTripListParams {
  /** Username to fetch trips for */
  username: string;

  /** Current search query (optional) */
  searchQuery?: string;

  /** Selected tag filter (optional) */
  selectedTag?: string | null;

  /** Selected status filter (optional) */
  selectedStatus?: 'draft' | 'published' | null;

  /** Items per page (default: 12) */
  limit?: number;

  /** Current page offset (default: 0) */
  offset?: number;
}

interface UseTripListReturn {
  /** List of trips */
  trips: TripListItem[];

  /** Total number of trips matching filters */
  total: number;

  /** Current limit (items per page) */
  limit: number;

  /** Current offset */
  offset: number;

  /** Loading state */
  isLoading: boolean;

  /** Error state */
  error: Error | null;

  /** Refetch trips (useful after create/update/delete) */
  refetch: () => Promise<void>;

  /** Whether there are more trips to load */
  hasMore: boolean;

  /** Current page number (1-indexed) */
  currentPage: number;

  /** Total number of pages */
  totalPages: number;
}

export const useTripList = ({
  username,
  searchQuery = '',
  selectedTag = null,
  selectedStatus = null,
  limit = 12,
  offset = 0,
}: UseTripListParams): UseTripListReturn => {
  const [trips, setTrips] = useState<TripListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Fetch trips function
  const fetchTrips = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params: {
        tag?: string;
        status?: 'draft' | 'published';
        limit: number;
        offset: number;
      } = {
        limit,
        offset,
      };

      // Add tag filter if selected
      if (selectedTag) {
        params.tag = selectedTag;
      }

      // Add status filter if selected
      if (selectedStatus) {
        params.status = selectedStatus;
      }

      const response: TripListResponse = await getUserTrips(username, params);

      // Client-side search filtering (if backend doesn't support it)
      let filteredTrips = response.trips;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filteredTrips = response.trips.filter((trip) => {
          const titleMatch = trip.title.toLowerCase().includes(query);
          const tagsMatch = trip.tag_names.some((tag) =>
            tag.toLowerCase().includes(query)
          );
          return titleMatch || tagsMatch;
        });
      }

      setTrips(filteredTrips);
      setTotal(searchQuery ? filteredTrips.length : response.total);
    } catch (err) {
      const error = err as Error;
      setError(error);
      console.error('Error fetching trips:', error);

      toast.error('Error al cargar viajes. Intenta nuevamente.', {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsLoading(false);
    }
  }, [username, searchQuery, selectedTag, selectedStatus, limit, offset]);

  // Fetch trips when params change
  useEffect(() => {
    fetchTrips();
  }, [fetchTrips]);

  // Calculate pagination values
  const hasMore = offset + limit < total;
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  return {
    trips,
    total,
    limit,
    offset,
    isLoading,
    error,
    refetch: fetchTrips,
    hasMore,
    currentPage,
    totalPages,
  };
};
