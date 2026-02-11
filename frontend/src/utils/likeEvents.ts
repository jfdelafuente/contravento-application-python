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
  console.log('[likeEvents] Emitting likeChanged event:', detail);
  const event = new CustomEvent('likeChanged', { detail });
  window.dispatchEvent(event);
  console.log('[likeEvents] Event dispatched successfully');
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
  console.log('[likeEvents] Subscribing to likeChanged events');

  const handler = (event: Event) => {
    const customEvent = event as CustomEvent<LikeChangedEvent>;
    console.log('[likeEvents] Received likeChanged event:', customEvent.detail);
    callback(customEvent.detail);
  };

  window.addEventListener('likeChanged', handler);
  console.log('[likeEvents] Listener registered successfully');

  // Return cleanup function
  return () => {
    console.log('[likeEvents] Unsubscribing from likeChanged events');
    window.removeEventListener('likeChanged', handler);
  };
}
