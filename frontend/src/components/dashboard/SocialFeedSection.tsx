import React, { memo, useEffect, useRef, useCallback, useMemo } from 'react';
import { FeedItem } from '../../services/feedService';
import { useInfiniteFeed } from '../../hooks/useFeed';
import SocialFeedItem from './SocialFeedItem';
import SkeletonLoader from '../common/SkeletonLoader';
import './SocialFeedSection.css';

/**
 * Performance: rerender-memo - Prevents re-renders when parent re-renders
 * Performance: rerender-functional-setstate - Already uses useCallback for event handlers
 * Performance: js-cache-property-access - Already uses useMemo for activities conversion
 * Performance: rendering-hoist-jsx - Static error/empty state icons can be hoisted
 */

// Performance: rendering-hoist-jsx - Static SVG icons outside component
const ERROR_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

const EMPTY_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
    />
  </svg>
);

const LOADING_SPINNER = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" opacity="0.25" />
    <path d="M12 2a10 10 0 0 1 10 10" opacity="0.75" />
  </svg>
);

const END_OF_FEED_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="6 9 12 15 18 9" />
  </svg>
);

export interface FeedActivity {
  id: string;
  type:
    | 'route_published'
    | 'achievement'
    | 'new_follower'
    | 'photo_uploaded'
    | 'comment_added'
    | 'trip_liked'
    | 'route_completed'
    | 'profile_updated';
  user: {
    username: string;
    profile_photo_url?: string;
  };
  timestamp: string;
  data: {
    title?: string;
    description?: string;
    distance_km?: number;
    photo_url?: string;
    achievement_name?: string;
    trip_id?: string;
    comment_text?: string;
    route_title?: string;
  };
  // Interaction counters
  likes_count: number;
  comments_count: number;
  shares_count: number;
  is_liked_by_me: boolean;
}

/**
 * Convert FeedItem (trip) to FeedActivity (route_published)
 */
const convertTripToActivity = (trip: FeedItem): FeedActivity => ({
  id: trip.trip_id,
  type: 'route_published',
  user: {
    username: trip.author.username,
    profile_photo_url: trip.author.profile_photo_url || undefined,
  },
  timestamp: trip.created_at,
  data: {
    title: trip.title,
    description: trip.description,
    distance_km: trip.distance_km || undefined,
    photo_url: trip.photos[0]?.photo_url || undefined,
    trip_id: trip.trip_id,
  },
  // Pass through interaction data from FeedItem
  likes_count: trip.likes_count,
  comments_count: trip.comments_count,
  shares_count: trip.shares_count,
  is_liked_by_me: trip.is_liked_by_me,
});

/**
 * SocialFeedSection - "Pelotón" activity stream
 * Shows recent activity from followed cyclists with infinite scroll
 */
const SocialFeedSection: React.FC = () => {
  // Use infinite feed hook (10 items per page)
  const { trips, isLoading, isLoadingMore, hasMore, error, loadMore } = useInfiniteFeed(10);

  // Intersection Observer ref for infinite scroll
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Performance: js-cache-property-access - Memoize activities conversion
  const activities = useMemo(() => {
    return trips.map(convertTripToActivity);
  }, [trips]);

  // Performance: rerender-functional-setstate - Stable intersection callback
  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && hasMore && !isLoadingMore && !isLoading) {
        loadMore();
      }
    },
    [hasMore, isLoadingMore, isLoading, loadMore]
  );

  // Set up Intersection Observer
  useEffect(() => {
    const observer = new IntersectionObserver(handleIntersection, {
      root: null,
      rootMargin: '100px', // Trigger 100px before reaching bottom
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

  // Error state
  if (error) {
    return (
      <section className="social-feed-section" aria-labelledby="feed-heading">
        <h2 id="feed-heading" className="social-feed-section__title">
          Tu Pelotón
        </h2>
        <div className="social-feed-section__error" role="alert">
          {ERROR_ICON}
          <p>{error}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="social-feed-section" aria-labelledby="feed-heading">
      <div className="social-feed-section__header">
        <h2 id="feed-heading" className="social-feed-section__title">
          Tu Pelotón
        </h2>
      </div>

      {/* Initial loading state */}
      {isLoading ? (
        <div className="social-feed-section__list" aria-busy="true">
          {[1, 2, 3].map((i) => (
            <div key={i} className="social-feed-section__skeleton">
              <SkeletonLoader variant="circle" width="40px" height="40px" />
              <div style={{ flex: 1 }}>
                <SkeletonLoader variant="text" width="60%" height="1rem" />
                <SkeletonLoader variant="text" width="40%" height="0.875rem" />
              </div>
            </div>
          ))}
        </div>
      ) : activities.length === 0 ? (
        /* Empty state */
        <div className="social-feed-section__empty">
          <div className="social-feed-section__empty-icon">
            {EMPTY_ICON}
          </div>
          <h3 className="social-feed-section__empty-title">Tu pelotón está vacío</h3>
          <p className="social-feed-section__empty-text">
            Comienza a seguir a otros ciclistas para ver su actividad aquí.
          </p>
        </div>
      ) : (
        /* Feed list with infinite scroll */
        <>
          <div className="social-feed-section__list">
            {activities.map((activity, index) => (
              <SocialFeedItem
                key={activity.id}
                activity={activity}
                style={{ animationDelay: `${index * 0.05}s` }}
              />
            ))}
          </div>

          {/* Loading more indicator */}
          {isLoadingMore && (
            <div className="social-feed-section__loading-more">
              <div className="social-feed-section__spinner" aria-label="Cargando más actividades">
                {LOADING_SPINNER}
              </div>
              <p>Cargando más actividades...</p>
            </div>
          )}

          {/* Intersection observer sentinel */}
          <div ref={loadMoreRef} className="social-feed-section__sentinel" aria-hidden="true" />

          {/* End of feed message */}
          {!hasMore && activities.length > 0 && (
            <div className="social-feed-section__end">
              {END_OF_FEED_ICON}
              <p>Has visto toda la actividad reciente</p>
            </div>
          )}
        </>
      )}
    </section>
  );
};

// Performance: rerender-memo - Add display name for better debugging
SocialFeedSection.displayName = 'SocialFeedSection';

export default memo(SocialFeedSection);
