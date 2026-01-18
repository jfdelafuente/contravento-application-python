// src/hooks/useFollow.ts

import { useState, useCallback } from 'react';
import { followUser, unfollowUser } from '../services/followService';
import { toast } from 'react-hot-toast';

/**
 * Custom hook for follow/unfollow functionality (Feature 004 - US1).
 *
 * Features:
 * - Optimistic UI updates (instant feedback)
 * - Error rollback on failure
 * - Loading state management
 * - Spanish error messages
 *
 * @param username - Username to follow/unfollow
 * @param initialFollowing - Initial following state
 * @returns Follow state and actions
 */
export function useFollow(
  username: string,
  initialFollowing: boolean = false
) {
  const [isFollowing, setIsFollowing] = useState<boolean>(initialFollowing);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  /**
   * Toggle follow/unfollow with optimistic updates.
   *
   * Optimistic UI pattern:
   * 1. Update UI immediately (instant feedback)
   * 2. Call API
   * 3. Rollback on error
   */
  const toggleFollow = useCallback(async () => {
    // Prevent double-clicks
    if (isLoading) return;

    // Store previous state for rollback
    const previousFollowing = isFollowing;

    // Optimistic update
    setIsFollowing(!isFollowing);
    setIsLoading(true);

    try {
      if (isFollowing) {
        // Unfollow
        await unfollowUser(username);
      } else {
        // Follow
        await followUser(username);
      }

      // Success - optimistic update was correct
      setIsLoading(false);

      // Emit custom event to notify other components (Feature 004 - US1)
      // This allows feed pages to refetch data and update all follow buttons
      window.dispatchEvent(new CustomEvent('followStatusChanged', {
        detail: { username, isFollowing: !previousFollowing }
      }));
    } catch (error: any) {
      // Rollback optimistic update
      setIsFollowing(previousFollowing);
      setIsLoading(false);

      // Show Spanish error message
      // Backend error structure: { success: false, data: null, error: { code, message } }
      const errorMessage =
        error.response?.data?.error?.message ||
        error.response?.data?.detail ||
        error.response?.data?.message ||
        'Error al procesar la acción. Intenta de nuevo.';
      toast.error(errorMessage);
    }
  }, [username, isFollowing, isLoading]);

  return {
    isFollowing,
    isLoading,
    toggleFollow,
  };
}
