// src/hooks/useLike.ts

import { useState, useCallback } from 'react';
import { likeTrip, unlikeTrip } from '../services/likeService';
import { toast } from 'react-hot-toast';

/**
 * Custom hook for like/unlike functionality (T060).
 *
 * Features:
 * - Optimistic UI updates (instant feedback)
 * - Error rollback on failure
 * - Loading state management
 * - Spanish error messages
 *
 * @param tripId - Trip ID
 * @param initialLiked - Initial liked state
 * @param initialCount - Initial like count
 * @returns Like state and actions
 */
export function useLike(
  tripId: string,
  initialLiked: boolean = false,
  initialCount: number = 0
) {
  const [isLiked, setIsLiked] = useState<boolean>(initialLiked);
  const [likeCount, setLikeCount] = useState<number>(initialCount);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  /**
   * Toggle like/unlike with optimistic updates.
   *
   * Optimistic UI pattern:
   * 1. Update UI immediately (instant feedback)
   * 2. Call API
   * 3. Rollback on error
   */
  const toggleLike = useCallback(async () => {
    // Prevent double-clicks
    if (isLoading) return;

    // Store previous state for rollback
    const previousLiked = isLiked;
    const previousCount = likeCount;

    // Optimistic update
    setIsLiked(!isLiked);
    setLikeCount(isLiked ? likeCount - 1 : likeCount + 1);
    setIsLoading(true);

    try {
      if (isLiked) {
        // Unlike
        await unlikeTrip(tripId);
      } else {
        // Like
        await likeTrip(tripId);
      }

      // Success - optimistic update was correct
      setIsLoading(false);
    } catch (error: any) {
      // Rollback optimistic update
      setIsLiked(previousLiked);
      setLikeCount(previousCount);
      setIsLoading(false);

      // Show Spanish error message
      const errorMessage =
        error.response?.data?.error?.message ||
        'Error al procesar la acción. Intenta de nuevo.';
      toast.error(errorMessage);
    }
  }, [tripId, isLiked, likeCount, isLoading]);

  return {
    isLiked,
    likeCount,
    isLoading,
    toggleLike,
  };
}
