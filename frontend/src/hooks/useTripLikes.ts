import { useState, useEffect, useCallback } from 'react';
import { getTripLikes } from '../services/likeService';

export interface LikeUser {
  username: string;
  profile_photo_url: string | null;
}

export interface TripLike {
  user: LikeUser;
  created_at: string;
}

export interface TripLikesData {
  likes: TripLike[];
  total_count: number;
  page: number;
  limit: number;
  has_more: boolean;
}

interface UseTripLikesOptions {
  tripId: string;
  enabled?: boolean; // Only fetch when enabled (e.g., modal is open)
}

interface UseTripLikesReturn {
  likes: TripLike[];
  totalCount: number;
  isLoading: boolean;
  error: string | null;
  hasMore: boolean;
  loadMore: () => Promise<void>;
  refetch: () => Promise<void>;
}

/**
 * Hook for fetching and managing the list of users who liked a trip.
 *
 * Features:
 * - Pagination support with infinite scroll
 * - Loading and error states
 * - Conditional fetching (only when enabled)
 * - Refetch capability
 *
 * @param options - Trip ID and enabled flag
 * @returns Likes data and control functions
 *
 * @example
 * ```tsx
 * const { likes, totalCount, isLoading, loadMore, hasMore } = useTripLikes({
 *   tripId: 'trip-123',
 *   enabled: isModalOpen
 * });
 * ```
 */
export function useTripLikes({
  tripId,
  enabled = true,
}: UseTripLikesOptions): UseTripLikesReturn {
  const [likes, setLikes] = useState<TripLike[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLikes = useCallback(
    async (pageNum: number, append: boolean = false) => {
      if (!enabled) return;

      setIsLoading(true);
      setError(null);

      try {
        const response = await getTripLikes(tripId, pageNum, 20);

        if (append) {
          setLikes((prev) => [...prev, ...response.likes]);
        } else {
          setLikes(response.likes);
        }

        setTotalCount(response.total_count);
        setHasMore(response.has_more);
        setPage(pageNum);
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.error?.message ||
          'Error al cargar la lista de likes';
        setError(errorMessage);
        console.error('[useTripLikes] Error:', err);
      } finally {
        setIsLoading(false);
      }
    },
    [tripId, enabled]
  );

  // Initial fetch when enabled changes
  useEffect(() => {
    if (enabled) {
      fetchLikes(1, false);
    } else {
      // Reset state when disabled (e.g., modal closed)
      setLikes([]);
      setTotalCount(0);
      setPage(1);
      setHasMore(false);
      setError(null);
    }
  }, [enabled, fetchLikes]);

  const loadMore = useCallback(async () => {
    if (!hasMore || isLoading) return;
    await fetchLikes(page + 1, true);
  }, [hasMore, isLoading, page, fetchLikes]);

  const refetch = useCallback(async () => {
    await fetchLikes(1, false);
  }, [fetchLikes]);

  return {
    likes,
    totalCount,
    isLoading,
    error,
    hasMore,
    loadMore,
    refetch,
  };
}
