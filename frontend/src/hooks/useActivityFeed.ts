/**
 * useActivityFeed Hook (Feature 018 - T036)
 *
 * Custom hook for fetching activity stream feed with infinite scroll using TanStack Query.
 * Supports cursor-based pagination for optimal performance.
 */

import { useInfiniteQuery } from '@tanstack/react-query';
import { getActivityFeed, ActivityFeedResponse } from '../services/activityFeedService';
import { ActivityFeedItem } from '../types/activityFeed';

/**
 * Parameters for useActivityFeed hook
 */
export interface UseActivityFeedOptions {
  /** Items per page (min 1, max 50, default 20) */
  limit?: number;

  /** Enable/disable the query (default: true) */
  enabled?: boolean;
}

/**
 * Return type for useActivityFeed hook
 */
export interface UseActivityFeedReturn {
  /** Flattened array of all activity feed items from all loaded pages */
  activities: ActivityFeedItem[];

  /** Loading state for initial fetch */
  isLoading: boolean;

  /** Error object if request failed */
  error: Error | null;

  /** Loading state for fetching next page */
  isFetchingNextPage: boolean;

  /** Whether more pages exist */
  hasNextPage: boolean;

  /** Function to load next page */
  fetchNextPage: () => void;

  /** Refetch all pages (useful after posting a new activity) */
  refetch: () => void;
}

/**
 * Hook for fetching activity feed with infinite scroll (Feature 018 - US1, T036)
 *
 * **Requires authentication** - User must be logged in
 *
 * Uses TanStack Query's useInfiniteQuery with cursor-based pagination.
 * Activities are automatically accumulated across pages.
 *
 * **Performance**: <2s for 20 activities (SC-001)
 *
 * @param options - Hook configuration (limit, enabled)
 * @returns Object with activities array, loading states, and pagination controls
 *
 * @example
 * ```typescript
 * const { activities, isLoading, hasNextPage, fetchNextPage } = useActivityFeed({ limit: 20 });
 *
 * if (isLoading) return <ActivityFeedSkeleton />;
 *
 * return (
 *   <div>
 *     {activities.map(activity => (
 *       <ActivityCard key={activity.activity_id} activity={activity} />
 *     ))}
 *     {hasNextPage && (
 *       <button onClick={() => fetchNextPage()}>Cargar más actividades</button>
 *     )}
 *   </div>
 * );
 * ```
 */
export const useActivityFeed = (
  options: UseActivityFeedOptions = {}
): UseActivityFeedReturn => {
  const { limit = 20, enabled = true } = options;

  const {
    data,
    error,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    refetch,
  } = useInfiniteQuery<
    ActivityFeedResponse,
    Error,
    { pages: ActivityFeedResponse[] },
    [string, number],
    string | null
  >({
    queryKey: ['activityFeed', limit],
    queryFn: ({ pageParam }: { pageParam: string | null }) =>
      getActivityFeed({
        cursor: pageParam,
        limit,
      }),
    enabled,
    initialPageParam: null,
    getNextPageParam: (lastPage: ActivityFeedResponse) => {
      // Return next_cursor if has_next is true, otherwise undefined (no more pages)
      return lastPage.has_next ? lastPage.next_cursor : undefined;
    },
    staleTime: 60 * 1000, // 60 seconds (data considered fresh for 1 minute)
    retry: 1, // Retry once on failure
  });

  // Flatten all pages into a single array of activities
  const activities =
    data?.pages.flatMap((page: ActivityFeedResponse) => page.activities) ?? [];

  return {
    activities,
    isLoading,
    error: error as Error | null,
    isFetchingNextPage,
    hasNextPage: hasNextPage ?? false,
    fetchNextPage: () => fetchNextPage(),
    refetch: () => refetch(),
  };
};
