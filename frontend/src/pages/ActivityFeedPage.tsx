/**
 * Activity Feed Page (Feature 018 - T037)
 *
 * Main page component displaying chronological activity stream from followed users.
 * Features infinite scroll with cursor-based pagination.
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { useActivityFeed } from '../hooks/useActivityFeed';
import { ActivityCard } from '../components/activityFeed/ActivityCard';
import { ActivityFeedEmptyState } from '../components/activityFeed/ActivityFeedEmptyState';
import './ActivityFeedPage.css';

/**
 * Activity Feed Page Component
 *
 * Displays activity stream from followed users with infinite scroll.
 *
 * **Features**:
 * - Chronological feed (most recent first)
 * - Infinite scroll with cursor-based pagination
 * - Loading skeletons
 * - Empty state when no followed users
 * - Error handling with Spanish messages
 *
 * **Performance**: <2s for 20 activities (SC-001)
 */
export const ActivityFeedPage: React.FC = () => {
  const {
    activities,
    isLoading,
    error,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
  } = useActivityFeed({ limit: 20 });

  const loadMoreRef = useRef<HTMLDivElement>(null);

  /**
   * Intersection Observer callback for infinite scroll
   */
  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;

      // Load more when sentinel element is visible AND conditions are met
      if (entry.isIntersecting && hasNextPage && !isFetchingNextPage && !isLoading) {
        fetchNextPage();
      }
    },
    [hasNextPage, isFetchingNextPage, isLoading, fetchNextPage]
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

  // Initial loading state
  if (isLoading) {
    return (
      <div className="activity-feed-page">
        <div className="activity-feed-container">
          <h1 className="activity-feed-title">Feed de Actividades</h1>
          <div className="activity-feed-list">
            {Array.from({ length: 3 }).map((_, index) => (
              <ActivityFeedSkeleton key={index} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="activity-feed-page">
        <div className="activity-feed-container">
          <h1 className="activity-feed-title">Feed de Actividades</h1>
          <div className="activity-feed-error">
            <div className="error-icon">⚠️</div>
            <p className="error-message">{error.message || 'Error al cargar el feed'}</p>
            <button
              className="retry-button"
              onClick={() => window.location.reload()}
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Empty state
  if (activities.length === 0) {
    return (
      <div className="activity-feed-page">
        <div className="activity-feed-container">
          <h1 className="activity-feed-title">Feed de Actividades</h1>
          <ActivityFeedEmptyState />
        </div>
      </div>
    );
  }

  // Feed with activities
  return (
    <div className="activity-feed-page">
      <div className="activity-feed-container">
        <h1 className="activity-feed-title">Feed de Actividades</h1>

        <div className="activity-feed-list">
          {activities.map((activity) => (
            <ActivityCard key={activity.activity_id} activity={activity} />
          ))}
        </div>

        {/* Infinite scroll sentinel */}
        {hasNextPage && (
          <div ref={loadMoreRef} className="load-more-sentinel">
            {isFetchingNextPage && (
              <div className="loading-more">
                <div className="spinner" />
                <p>Cargando más actividades...</p>
              </div>
            )}
          </div>
        )}

        {/* End of feed message */}
        {!hasNextPage && activities.length > 0 && (
          <div className="end-of-feed">
            <p>Has llegado al final del feed</p>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Skeleton loader for activity feed items
 */
const ActivityFeedSkeleton: React.FC = () => {
  return (
    <div className="activity-card skeleton">
      <div className="activity-card-header">
        <div className="skeleton-avatar" />
        <div className="skeleton-text skeleton-text-short" />
      </div>
      <div className="activity-card-body">
        <div className="skeleton-text skeleton-text-medium" />
        <div className="skeleton-text skeleton-text-long" />
      </div>
    </div>
  );
};
