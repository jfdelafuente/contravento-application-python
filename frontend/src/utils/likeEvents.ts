/**
 * Like Events - Cross-tab event system for like synchronization
 *
 * Uses BroadcastChannel API to notify ALL browser tabs/windows when likes change.
 * Allows Activity Feed (Feature 018) to notify Travel Diary (Feature 002/008)
 * across different tabs in real-time.
 */

/**
 * Event emitted when a like is added or removed
 */
export interface LikeChangedEvent {
  activityId: string;
  tripId?: string;
  action: 'like' | 'unlike';
}

// BroadcastChannel for cross-tab communication
// Falls back to window events for same-tab communication
let broadcastChannel: BroadcastChannel | null = null;

// Initialize BroadcastChannel (only once)
if (typeof window !== 'undefined' && 'BroadcastChannel' in window) {
  try {
    broadcastChannel = new BroadcastChannel('contravento-likes');
    console.log('[likeEvents] BroadcastChannel initialized (cross-tab support enabled)');
  } catch (error) {
    console.warn('[likeEvents] BroadcastChannel not available, using fallback', error);
  }
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
  console.log('[likeEvents] Emitting likeChanged event (cross-tab):', detail);

  // Emit to other tabs via BroadcastChannel
  if (broadcastChannel) {
    try {
      broadcastChannel.postMessage(detail);
      console.log('[likeEvents] Event sent via BroadcastChannel (other tabs will receive)');
    } catch (error) {
      console.error('[likeEvents] BroadcastChannel postMessage failed:', error);
    }
  }

  // Also emit locally via CustomEvent (for same-tab listeners)
  const event = new CustomEvent('likeChanged', { detail });
  window.dispatchEvent(event);
  console.log('[likeEvents] Event dispatched locally (same tab)');
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
  console.log('[likeEvents] Subscribing to likeChanged events (cross-tab + same-tab)');

  // Handler for BroadcastChannel messages (cross-tab)
  const broadcastHandler = (event: MessageEvent<LikeChangedEvent>) => {
    console.log('[likeEvents] Received likeChanged from BroadcastChannel (other tab):', event.data);
    callback(event.data);
  };

  // Handler for CustomEvent (same-tab fallback)
  const customEventHandler = (event: Event) => {
    const customEvent = event as CustomEvent<LikeChangedEvent>;
    console.log('[likeEvents] Received likeChanged from CustomEvent (same tab):', customEvent.detail);
    callback(customEvent.detail);
  };

  // Subscribe to BroadcastChannel (cross-tab)
  if (broadcastChannel) {
    broadcastChannel.addEventListener('message', broadcastHandler);
    console.log('[likeEvents] BroadcastChannel listener registered (will receive cross-tab events)');
  }

  // Subscribe to CustomEvent (same-tab fallback)
  window.addEventListener('likeChanged', customEventHandler);
  console.log('[likeEvents] CustomEvent listener registered (will receive same-tab events)');

  // Return cleanup function
  return () => {
    console.log('[likeEvents] Unsubscribing from likeChanged events');

    if (broadcastChannel) {
      broadcastChannel.removeEventListener('message', broadcastHandler);
    }

    window.removeEventListener('likeChanged', customEventHandler);
  };
}
