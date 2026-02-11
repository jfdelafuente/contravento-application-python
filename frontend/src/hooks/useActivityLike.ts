/**
 * useActivityLike Hook (Feature 018 - US2)
 *
 * Custom hook for liking/unliking activity feed items with optimistic updates.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { likeActivity, unlikeActivity } from '../services/activityLikeService';
import { ActivityFeedItem } from '../types/activityFeed';
import { emitLikeChanged } from '../utils/likeEvents';

interface UseActivityLikeOptions {
  activityId: string;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

interface UseActivityLikeReturn {
  toggleLike: () => void;
  isLiking: boolean;
}

/**
 * Hook for liking/unliking activities with optimistic UI updates.
 *
 * Automatically updates activity feed cache before API call completes.
 * Rolls back on error.
 *
 * @param options - Hook configuration
 * @returns toggleLike function and loading state
 *
 * @example
 * ```tsx
 * const { toggleLike, isLiking } = useActivityLike({
 *   activityId: activity.activity_id,
 * });
 *
 * <button onClick={toggleLike} disabled={isLiking}>
 *   {activity.is_liked_by_me ? 'Unlike' : 'Like'}
 * </button>
 * ```
 */
export const useActivityLike = ({
  activityId,
  onSuccess,
  onError,
}: UseActivityLikeOptions): UseActivityLikeReturn => {
  const queryClient = useQueryClient();

  // Mutation for toggling like
  const { mutate: toggleLike, isPending: isLiking } = useMutation({
    mutationFn: async (isCurrentlyLiked: boolean) => {
      if (isCurrentlyLiked) {
        await unlikeActivity(activityId);
        return { action: 'unlike' as const };
      } else {
        await likeActivity(activityId);
        return { action: 'like' as const };
      }
    },

    // Optimistic update: Update cache before API call completes
    onMutate: async (isCurrentlyLiked: boolean) => {
      // Cancel outgoing refetches (partial match on activityFeed)
      await queryClient.cancelQueries({ queryKey: ['activityFeed'] });

      // Snapshot all activityFeed queries for rollback
      const previousFeeds = queryClient.getQueriesData<{
        pages: { activities: ActivityFeedItem[] }[];
      }>({ queryKey: ['activityFeed'] });

      // Optimistically update all activityFeed caches
      queryClient.setQueriesData<{
        pages: { activities: ActivityFeedItem[] }[];
      }>({ queryKey: ['activityFeed'] }, (old) => {
        if (!old) return old;

        return {
          ...old,
          pages: old.pages.map((page) => ({
            ...page,
            activities: page.activities.map((activity) => {
              if (activity.activity_id === activityId) {
                return {
                  ...activity,
                  is_liked_by_me: !isCurrentlyLiked,
                  likes_count: isCurrentlyLiked
                    ? activity.likes_count - 1
                    : activity.likes_count + 1,
                };
              }
              return activity;
            }),
          })),
        };
      });

      // Return context for rollback
      return { previousFeeds };
    },

    // Rollback on error
    onError: (error, _variables, context) => {
      // Restore all previous feed states
      if (context?.previousFeeds) {
        context.previousFeeds.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }

      // Show error toast
      toast.error('Error al actualizar like. Intenta de nuevo.');

      // Call custom error handler
      if (onError) {
        onError(error as Error);
      }
    },

    // Refetch on success to ensure consistency across features
    onSuccess: (result) => {
      // Invalidate activity feed cache
      queryClient.invalidateQueries({ queryKey: ['activityFeed'] });

      // Invalidate Travel Diary caches (Feature 002/008 integration)
      // This ensures likes show up in /trips, /trips/public, /trips?user=...
      queryClient.invalidateQueries({ queryKey: ['trips'] });
      queryClient.invalidateQueries({ queryKey: ['publicTrips'] });

      // Emit like changed event for non-TanStack Query hooks (useTripList, usePublicTrips)
      // Extract trip_id from activity metadata
      const queries = queryClient.getQueriesData<{
        pages: { activities: ActivityFeedItem[] }[];
      }>({ queryKey: ['activityFeed'] });

      let tripId: string | undefined;
      for (const [_key, feedData] of queries) {
        if (!feedData) continue;

        for (const page of feedData.pages) {
          const activity = page.activities.find((a) => a.activity_id === activityId);
          if (activity && activity.metadata.trip_id) {
            tripId = activity.metadata.trip_id;
            break;
          }
        }
        if (tripId) break;
      }

      emitLikeChanged({
        activityId,
        tripId,
        action: result.action,
      });

      // Call custom success handler
      if (onSuccess) {
        onSuccess();
      }
    },
  });

  // Wrapper function to get current like state from cache
  const handleToggle = () => {
    // Get all activityFeed queries (there may be multiple with different limits)
    const queries = queryClient.getQueriesData<{
      pages: { activities: ActivityFeedItem[] }[];
    }>({ queryKey: ['activityFeed'] });

    if (queries.length === 0) {
      toast.error('No se pudo obtener el estado actual');
      return;
    }

    // Find activity in any of the feed queries
    let currentActivity: ActivityFeedItem | undefined;
    for (const [_key, feedData] of queries) {
      if (!feedData) continue;

      for (const page of feedData.pages) {
        currentActivity = page.activities.find(
          (a) => a.activity_id === activityId
        );
        if (currentActivity) break;
      }
      if (currentActivity) break;
    }

    if (!currentActivity) {
      toast.error('Actividad no encontrada');
      return;
    }

    // Toggle like
    toggleLike(currentActivity.is_liked_by_me);
  };

  return {
    toggleLike: handleToggle,
    isLiking,
  };
};
