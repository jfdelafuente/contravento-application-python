import React, { memo, useState, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { FeedActivity } from './SocialFeedSection';
import { LikeButton } from '../likes/LikeButton';
import { LikesListModal } from '../likes/LikesListModal';
import { getPhotoUrl } from '../../utils/tripHelpers';
import './SocialFeedItem.css';

/**
 * Performance: rerender-memo - Prevents re-renders when parent re-renders
 * Performance: rerender-functional-setstate - Stable event handler callbacks
 * Performance: js-cache-property-access - Memoize formatTimestamp and formatDate
 * Performance: rendering-hoist-jsx - Static placeholder icons outside component
 */

interface SocialFeedItemProps {
  activity: FeedActivity;
  style?: React.CSSProperties;
}

// Performance: rendering-hoist-jsx - Static SVG icons outside component
const PHOTO_PLACEHOLDER_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <circle cx="8.5" cy="8.5" r="1.5" />
    <polyline points="21 15 16 10 5 21" />
  </svg>
);

const DISTANCE_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
  </svg>
);

const LOCATION_PIN_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <circle cx="12" cy="10" r="3" />
  </svg>
);

const COMMENTS_ICON = (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
);

const SHARE_ICON = (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="18" cy="5" r="3" />
    <circle cx="6" cy="12" r="3" />
    <circle cx="18" cy="19" r="3" />
    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
    <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
  </svg>
);

/**
 * Format timestamp as relative time (e.g., "hace 5m", "hace 2h")
 */
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `hace ${diffMins}m`;
  if (diffHours < 24) return `hace ${diffHours}h`;
  if (diffDays < 7) return `hace ${diffDays}d`;
  return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
};

/**
 * Format date as readable text (e.g., "15 de enero, 2024")
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString + 'T00:00:00'); // Force local timezone
  return date.toLocaleDateString('es-ES', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });
};

/**
 * Extract primary location (first location or country)
 */
const getPrimaryLocation = (activity: FeedActivity): string | null => {
  // Try to get location from trip data
  if (activity.data.location) {
    return activity.data.location;
  }
  return null;
};

/**
 * SocialFeedItem - Enhanced information-rich feed card
 * Displays trip as vintage postcard with annotations, date stamp, tags
 */
const SocialFeedItem: React.FC<SocialFeedItemProps> = ({ activity, style }) => {
  const navigate = useNavigate();
  const [showLikesModal, setShowLikesModal] = useState(false);

  // Performance: rerender-functional-setstate - Stable event handler callbacks
  const handleCardClick = useCallback(() => {
    if (activity.data.trip_id) {
      navigate(`/trips/${activity.data.trip_id}`);
    }
  }, [activity.data.trip_id, navigate]);

  const handleLikesClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setShowLikesModal(true);
  }, []);

  const handleCommentsClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      if (activity.data.trip_id) {
        navigate(`/trips/${activity.data.trip_id}#comments`);
      }
    },
    [activity.data.trip_id, navigate]
  );

  const handleShareClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      if (activity.data.trip_id) {
        const tripUrl = `${window.location.origin}/trips/${activity.data.trip_id}`;
        navigator.clipboard.writeText(tripUrl);
        // TODO: Show toast notification
      }
    },
    [activity.data.trip_id]
  );

  const handleCloseModal = useCallback(() => {
    setShowLikesModal(false);
  }, []);

  // Performance: js-cache-property-access - Memoize computed values
  const formattedTimestamp = useMemo(() => formatTimestamp(activity.timestamp), [activity.timestamp]);

  const formattedDate = useMemo(() => {
    if (activity.data.start_date) {
      return formatDate(activity.data.start_date);
    }
    return null;
  }, [activity.data.start_date]);

  const primaryLocation = useMemo(() => getPrimaryLocation(activity), [activity]);

  // Tags: Display max 3, then "+N more"
  const visibleTags = useMemo(() => {
    const tags = activity.data.tags || [];
    const maxVisible = 3;
    const visible = tags.slice(0, maxVisible);
    const remaining = tags.length - maxVisible;
    return { visible, remaining };
  }, [activity.data.tags]);

  return (
    <>
      <article
        className="social-feed-item"
        style={style}
        onClick={handleCardClick}
        role="button"
        tabIndex={0}
        aria-label={`Ver viaje: ${activity.data.title || 'Sin título'} de ${activity.user.username}`}
      >
        {/* Thumbnail */}
        <div className="social-feed-item__thumbnail">
          <div className="social-feed-item__thumbnail-inner">
            {activity.data.photo_url ? (
              <img
                src={getPhotoUrl(activity.data.photo_url)}
                alt={activity.data.title || 'Foto de ruta'}
                className="social-feed-item__thumbnail-img"
                loading="lazy"
              />
            ) : (
              <div className="social-feed-item__thumbnail-placeholder">
                {PHOTO_PLACEHOLDER_ICON}
              </div>
            )}
          </div>
        </div>

        {/* Content: Main column + Annotations sidebar */}
        <div className="social-feed-item__content">
          {/* Main Column */}
          <div className="social-feed-item__main">
            {/* Header: avatar + username + timestamp */}
            <div className="social-feed-item__header">
              <div className="social-feed-item__avatar">
                {activity.user.profile_photo_url ? (
                  <img
                    src={activity.user.profile_photo_url}
                    alt={activity.user.username}
                    className="social-feed-item__avatar-img"
                  />
                ) : (
                  <div className="social-feed-item__avatar-placeholder">
                    {activity.user.username.charAt(0).toUpperCase()}
                  </div>
                )}
              </div>
              <span className="social-feed-item__username">{activity.user.username}</span>
              <span className="social-feed-item__dot">•</span>
              <time className="social-feed-item__timestamp" dateTime={activity.timestamp}>
                {formattedTimestamp}
              </time>
            </div>

            {/* Title - Allow 2 lines */}
            {activity.data.title && (
              <h3 className="social-feed-item__title">{activity.data.title}</h3>
            )}

            {/* Date - Below title */}
            {formattedDate && (
              <time className="social-feed-item__date" dateTime={activity.data.start_date}>
                {formattedDate}
              </time>
            )}
          </div>

          {/* Annotations Sidebar - Handwritten margin notes */}
          <div className="social-feed-item__annotations">
            {/* Distance annotation */}
            {activity.data.distance_km && (
              <div className="social-feed-item__annotation">
                <span className="social-feed-item__annotation-label">distancia</span>
                <span className="social-feed-item__annotation-value social-feed-item__annotation-value--distance">
                  {DISTANCE_ICON}
                  <span>{activity.data.distance_km} km</span>
                </span>
              </div>
            )}

            {/* Location annotation */}
            {primaryLocation && (
              <div className="social-feed-item__annotation">
                <span className="social-feed-item__annotation-label">ubicación</span>
                <span className="social-feed-item__annotation-value social-feed-item__annotation-value--location">
                  {LOCATION_PIN_ICON}
                  <span>{primaryLocation}</span>
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Tags + Interactions Strip */}
        <div className="social-feed-item__tags-strip">
          {/* Tags as postage stamps */}
          {visibleTags.visible.length > 0 && (
            <div className="social-feed-item__tags">
              {visibleTags.visible.map((tag, index) => (
                <span key={tag.normalized || index} className="social-feed-item__tag">
                  {tag.name}
                </span>
              ))}
              {visibleTags.remaining > 0 && (
                <span className="social-feed-item__tag social-feed-item__tag--more">
                  +{visibleTags.remaining}
                </span>
              )}
            </div>
          )}

          {/* Interaction Buttons */}
          {activity.data.trip_id && (
            <div className="social-feed-item__interactions">
              <LikeButton
                tripId={activity.data.trip_id}
                initialLiked={activity.is_liked_by_me}
                initialCount={activity.likes_count}
                size="small"
                showCount={true}
                onCountClick={activity.likes_count > 0 ? handleLikesClick : undefined}
              />

              <button
                className="social-feed-item__interaction-button"
                onClick={handleCommentsClick}
                aria-label={`${activity.comments_count} comentarios`}
                title="Ver comentarios"
              >
                <span className="social-feed-item__interaction-icon">
                  {COMMENTS_ICON}
                </span>
                <span className="social-feed-item__interaction-count">
                  {activity.comments_count}
                </span>
              </button>

              <button
                className="social-feed-item__interaction-button"
                onClick={handleShareClick}
                aria-label="Compartir viaje"
                title="Compartir"
              >
                <span className="social-feed-item__interaction-icon">
                  {SHARE_ICON}
                </span>
                <span className="social-feed-item__interaction-count">
                  {activity.shares_count}
                </span>
              </button>
            </div>
          )}
        </div>
      </article>

      {/* Likes List Modal */}
      {activity.data.trip_id && (
        <LikesListModal
          tripId={activity.data.trip_id}
          tripTitle={activity.data.title || 'Viaje'}
          isOpen={showLikesModal}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
};

// Performance: rerender-memo - Add display name for better debugging
SocialFeedItem.displayName = 'SocialFeedItem';

export default memo(SocialFeedItem);
