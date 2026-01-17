/**
 * FeedList Component (Feature 004 - T035)
 *
 * Displays feed items with infinite scroll functionality.
 * Uses Intersection Observer API to detect when user scrolls to bottom.
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { FeedItem } from './FeedItem';
import { FeedSkeleton } from './FeedSkeleton';
import { FeedItem as FeedItemType } from '../../services/feedService';
import './FeedList.css';

interface FeedListProps {
  /** Feed items to display */
  trips: FeedItemType[];

  /** Loading state for initial fetch */
  isLoading: boolean;

  /** Loading state for loading more items */
  isLoadingMore: boolean;

  /** Whether more items exist */
  hasMore: boolean;

  /** Error message (Spanish) */
  error: string | null;

  /** Callback to load more items (infinite scroll) */
  onLoadMore: () => void;

  /** Optional empty state message */
  emptyMessage?: string;
}

/**
 * FeedList Component
 *
 * Displays a list of feed items with infinite scroll.
 * Automatically loads more items when user scrolls near bottom.
 *
 * Features:
 * - Infinite scroll using Intersection Observer
 * - Loading skeletons
 * - Empty state
 * - Error handling
 * - "End of feed" message
 *
 * @example
 * ```typescript
 * const { trips, isLoading, isLoadingMore, hasMore, loadMore, error } = useInfiniteFeed();
 *
 * <FeedList
 *   trips={trips}
 *   isLoading={isLoading}
 *   isLoadingMore={isLoadingMore}
 *   hasMore={hasMore}
 *   error={error}
 *   onLoadMore={loadMore}
 * />
 * ```
 */
export const FeedList: React.FC<FeedListProps> = ({
  trips,
  isLoading,
  isLoadingMore,
  hasMore,
  error,
  onLoadMore,
  emptyMessage = 'No hay viajes en tu feed. ¡Empieza a seguir a otros ciclistas!',
}) => {
  const loadMoreRef = useRef<HTMLDivElement>(null);

  /**
   * Intersection Observer callback for infinite scroll
   */
  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;

      // Load more when sentinel element is visible AND conditions are met
      if (entry.isIntersecting && hasMore && !isLoadingMore && !isLoading) {
        onLoadMore();
      }
    },
    [hasMore, isLoadingMore, isLoading, onLoadMore]
  );

  /**
   * Setup Intersection Observer for infinite scroll
   */
  useEffect(() => {
    const observer = new IntersectionObserver(handleIntersection, {
      root: null, // viewport
      rootMargin: '200px', // Trigger 200px before reaching bottom
      threshold: 0.1,
    });

    const currentRef = loadMoreRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [handleIntersection]);

  /**
   * Initial loading state
   */
  if (isLoading && trips.length === 0) {
    return (
      <div className="feed-list">
        <FeedSkeleton count={5} />
      </div>
    );
  }

  /**
   * Error state
   */
  if (error && trips.length === 0) {
    return (
      <div className="feed-list">
        <div className="feed-list__error">
          <svg
            className="feed-list__error-icon"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h3 className="feed-list__error-title">Error al cargar el feed</h3>
          <p className="feed-list__error-message">{error}</p>
        </div>
      </div>
    );
  }

  /**
   * Empty state
   */
  if (trips.length === 0 && !isLoading) {
    return (
      <div className="feed-list">
        <div className="feed-list__empty">
          <svg
            className="feed-list__empty-icon"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M17 14h5v1a4 4 0 01-4 4H6a4 4 0 01-4-4v-1h5M12 16v6M4 8V4a2 2 0 012-2h12a2 2 0 012 2v4" />
          </svg>
          <h3 className="feed-list__empty-title">Feed vacío</h3>
          <p className="feed-list__empty-message">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  /**
   * Feed list with items
   */
  return (
    <div className="feed-list">
      {/* Feed Items */}
      {trips.map((trip) => (
        <FeedItem key={trip.trip_id} item={trip} />
      ))}

      {/* Loading More Indicator */}
      {isLoadingMore && (
        <div className="feed-list__loading-more">
          <div className="feed-list__spinner" />
          <p className="feed-list__loading-text">Cargando más viajes...</p>
        </div>
      )}

      {/* Sentinel Element for Intersection Observer */}
      <div ref={loadMoreRef} className="feed-list__sentinel" />

      {/* End of Feed Message */}
      {!hasMore && trips.length > 0 && !isLoadingMore && (
        <div className="feed-list__end">
          <svg
            className="feed-list__end-icon"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <p className="feed-list__end-message">
            Has llegado al final del feed. ¡No hay más viajes por ahora!
          </p>
        </div>
      )}
    </div>
  );
};
