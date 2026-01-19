/**
 * useFeed Hooks (Feature 004 - T032, T033)
 *
 * Custom hooks for fetching and managing personalized feed.
 * - useFeed: Standard pagination hook
 * - useInfiniteFeed: Infinite scroll hook with load more functionality
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { getFeed, FeedItem, FeedResponse } from '../services/feedService';

/**
 * Return type for useFeed hook
 */
interface UseFeedReturn {
  /** List of feed items (trips) */
  trips: FeedItem[];

  /** Total count of available trips */
  totalCount: number;

  /** Current page number */
  page: number;

  /** Items per page */
  limit: number;

  /** Whether more pages exist */
  hasMore: boolean;

  /** Loading state */
  isLoading: boolean;

  /** Error message (Spanish) */
  error: string | null;

  /** Refetch current page (useful after data changes) */
  refetch: () => Promise<void>;
}

/**
 * Hook for fetching personalized feed with standard pagination (T032)
 *
 * **Requires authentication** - User must be logged in
 *
 * @param page - Page number (1-indexed, default 1)
 * @param limit - Items per page (default 10, max 50)
 * @returns Object with trips, pagination metadata, loading, error, and refetch
 *
 * @example
 * ```typescript
 * const { trips, isLoading, error, hasMore } = useFeed(1, 10);
 *
 * if (isLoading) return <FeedSkeleton />;
 * if (error) return <ErrorMessage message={error} />;
 *
 * return (
 *   <div>
 *     {trips.map(trip => <FeedItem key={trip.trip_id} trip={trip} />)}
 *     {hasMore && <button onClick={() => goToNextPage()}>Cargar más</button>}
 *   </div>
 * );
 * ```
 */
export const useFeed = (page: number = 1, limit: number = 10): UseFeedReturn => {
  const [trips, setTrips] = useState<FeedItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(page);
  const [currentLimit, setCurrentLimit] = useState<number>(limit);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFeed = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response: FeedResponse = await getFeed({ page, limit });

      setTrips(response.trips);
      setTotalCount(response.total_count);
      setCurrentPage(response.page);
      setCurrentLimit(response.limit);
      setHasMore(response.has_more);
    } catch (err: any) {
      console.error('Error fetching feed:', err);

      // Extract error message from API response (Spanish)
      let errorMessage = 'Error al cargar el feed';

      if (err.response?.status === 401) {
        errorMessage = 'Debes iniciar sesión para ver el feed';
      } else if (err.response?.data?.detail?.message) {
        errorMessage = err.response.data.detail.message;
      } else if (err.response?.data?.error?.message) {
        errorMessage = err.response.data.error.message;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
      setTrips([]);
      setTotalCount(0);
      setHasMore(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch feed on mount and when page/limit changes
  useEffect(() => {
    fetchFeed();
  }, [page, limit]);

  // Listen for follow status changes to update cached feed items (Feature 004 - US1)
  useEffect(() => {
    const handleFollowChange = (event: Event) => {
      const customEvent = event as CustomEvent<{ username: string; isFollowing: boolean }>;
      const { username, isFollowing } = customEvent.detail;

      // Update cached feed items' is_following status for this author
      setTrips((prevTrips) =>
        prevTrips.map((trip) =>
          trip.author.username === username
            ? {
                ...trip,
                author: {
                  ...trip.author,
                  is_following: isFollowing,
                },
              }
            : trip
        )
      );
    };

    window.addEventListener('followStatusChanged', handleFollowChange);

    return () => {
      window.removeEventListener('followStatusChanged', handleFollowChange);
    };
  }, []); // No dependencies - event handler updates state directly

  return {
    trips,
    totalCount,
    page: currentPage,
    limit: currentLimit,
    hasMore,
    isLoading,
    error,
    refetch: fetchFeed,
  };
};

/**
 * Return type for useInfiniteFeed hook
 */
interface UseInfiniteFeedReturn {
  /** Accumulated list of feed items (trips) from all loaded pages */
  trips: FeedItem[];

  /** Total count of available trips */
  totalCount: number;

  /** Current page number */
  page: number;

  /** Whether more pages exist */
  hasMore: boolean;

  /** Loading state for initial fetch */
  isLoading: boolean;

  /** Loading state for loading more items */
  isLoadingMore: boolean;

  /** Error message (Spanish) */
  error: string | null;

  /** Load next page and append to trips array */
  loadMore: () => Promise<void>;

  /** Refetch from page 1 (useful after data changes) */
  refetch: () => Promise<void>;
}

/**
 * Hook for fetching personalized feed with infinite scroll (T033)
 *
 * **Requires authentication** - User must be logged in
 *
 * Accumulates trips across pages. Use `loadMore()` to fetch next page.
 * When user scrolls to bottom, call `loadMore()` to append more trips.
 *
 * @param limit - Items per page (default 10, max 50)
 * @returns Object with accumulated trips, loading states, and loadMore function
 *
 * @example
 * ```typescript
 * const { trips, isLoading, isLoadingMore, hasMore, loadMore } = useInfiniteFeed(10);
 *
 * // Infinite scroll implementation
 * const handleScroll = () => {
 *   if (isLoadingMore || !hasMore) return;
 *
 *   const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
 *   if (scrollTop + clientHeight >= scrollHeight - 100) {
 *     loadMore();
 *   }
 * };
 *
 * useEffect(() => {
 *   window.addEventListener('scroll', handleScroll);
 *   return () => window.removeEventListener('scroll', handleScroll);
 * }, [isLoadingMore, hasMore]);
 *
 * return (
 *   <div>
 *     {isLoading && <FeedSkeleton />}
 *     {trips.map(trip => <FeedItem key={trip.trip_id} trip={trip} />)}
 *     {isLoadingMore && <LoadingSpinner />}
 *     {!hasMore && trips.length > 0 && <p>Has llegado al final del feed</p>}
 *   </div>
 * );
 * ```
 */
export const useInfiniteFeed = (limit: number = 10): UseInfiniteFeedReturn => {
  const [trips, setTrips] = useState<FeedItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingMore, setIsLoadingMore] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Prevent concurrent fetches
  const isFetchingRef = useRef<boolean>(false);

  /**
   * Fetch a specific page and append to trips array
   */
  const fetchPage = async (pageNumber: number, append: boolean = false) => {
    // Prevent concurrent fetches
    if (isFetchingRef.current) {
      return;
    }

    isFetchingRef.current = true;

    try {
      // Set appropriate loading state
      if (append) {
        setIsLoadingMore(true);
      } else {
        setIsLoading(true);
      }

      setError(null);

      const response: FeedResponse = await getFeed({ page: pageNumber, limit });

      if (append) {
        // Append to existing trips (infinite scroll)
        setTrips((prev) => [...prev, ...response.trips]);
      } else {
        // Replace trips (initial load or refetch)
        setTrips(response.trips);
      }

      setTotalCount(response.total_count);
      setPage(response.page);
      setHasMore(response.has_more);
    } catch (err: any) {
      console.error('Error fetching feed:', err);

      // Extract error message from API response (Spanish)
      let errorMessage = 'Error al cargar el feed';

      if (err.response?.status === 401) {
        errorMessage = 'Debes iniciar sesión para ver el feed';
      } else if (err.response?.data?.detail?.message) {
        errorMessage = err.response.data.detail.message;
      } else if (err.response?.data?.error?.message) {
        errorMessage = err.response.data.error.message;
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);

      if (!append) {
        // Only clear trips on initial load error
        setTrips([]);
        setTotalCount(0);
        setHasMore(false);
      }
    } finally {
      if (append) {
        setIsLoadingMore(false);
      } else {
        setIsLoading(false);
      }
      isFetchingRef.current = false;
    }
  };

  /**
   * Load next page and append to trips array
   */
  const loadMore = useCallback(async () => {
    if (isLoadingMore || !hasMore) return;

    await fetchPage(page + 1, true);
  }, [page, hasMore, isLoadingMore, limit]);

  /**
   * Refetch from page 1 (reset feed)
   */
  const refetch = useCallback(async () => {
    setPage(1);
    await fetchPage(1, false);
  }, [limit]);

  // Initial fetch on mount
  useEffect(() => {
    // Prevent double-fetch in React StrictMode
    let cancelled = false;

    const initialFetch = async () => {
      if (!cancelled) {
        await fetchPage(1, false);
      }
    };

    initialFetch();

    return () => {
      cancelled = true;
    };
  }, [limit]); // Only re-fetch if limit changes

  // Listen for follow status changes to update cached feed items (Feature 004 - US1)
  useEffect(() => {
    const handleFollowChange = (event: Event) => {
      const customEvent = event as CustomEvent<{ username: string; isFollowing: boolean }>;
      const { username, isFollowing } = customEvent.detail;

      // Update cached feed items' is_following status for this author
      setTrips((prevTrips) =>
        prevTrips.map((trip) =>
          trip.author.username === username
            ? {
                ...trip,
                author: {
                  ...trip.author,
                  is_following: isFollowing,
                },
              }
            : trip
        )
      );
    };

    window.addEventListener('followStatusChanged', handleFollowChange);

    return () => {
      window.removeEventListener('followStatusChanged', handleFollowChange);
    };
  }, []); // No dependencies - event handler updates state directly

  return {
    trips,
    totalCount,
    page,
    hasMore,
    isLoading,
    isLoadingMore,
    error,
    loadMore,
    refetch,
  };
};
