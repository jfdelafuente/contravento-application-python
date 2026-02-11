/**
 * Like Events - Custom event system for cross-feature like synchronization
 *
 * Allows Activity Feed (Feature 018) to notify Travel Diary (Feature 002/008)
 * when likes change, triggering refetch of trip data.
 */

/**
 * Event emitted when a like is added or removed
 */
export interface LikeChangedEvent {
  activityId: string;
  tripId?: string;
  action: 'like' | 'unlike';
}

/**
 * Emit a like changed event
 *
 * @param detail - Event details
 *
 * @example
 * ```typescript
 * emitLikeChanged({
 *   activityId: 'activity-123',
 *   tripId: 'trip-456',
 *   action: 'like'
 * });
 * ```
 */
export function emitLikeChanged(detail: LikeChangedEvent): void {
  const event = new CustomEvent('likeChanged', { detail });
  window.dispatchEvent(event);
}

/**
 * Subscribe to like changed events
 *
 * @param callback - Function to call when like changes
 * @returns Cleanup function to remove the listener
 *
 * @example
 * ```typescript
 * useEffect(() => {
 *   const unsubscribe = subscribeLikeChanged((event) => {
 *     console.log('Like changed:', event);
 *     refetch(); // Refetch trips data
 *   });
 *
 *   return unsubscribe; // Cleanup on unmount
 * }, [refetch]);
 * ```
 */
export function subscribeLikeChanged(
  callback: (event: LikeChangedEvent) => void
): () => void {
  const handler = (event: Event) => {
    const customEvent = event as CustomEvent<LikeChangedEvent>;
    callback(customEvent.detail);
  };

  window.addEventListener('likeChanged', handler);

  // Return cleanup function
  return () => {
    window.removeEventListener('likeChanged', handler);
  };
}
