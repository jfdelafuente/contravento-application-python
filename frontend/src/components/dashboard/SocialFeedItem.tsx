import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FeedActivity } from './SocialFeedSection';
import { LikeButton } from '../likes/LikeButton';
import { LikesListModal } from '../likes/LikesListModal';
import { getPhotoUrl } from '../../utils/tripHelpers';
import './SocialFeedItem.css';

interface SocialFeedItemProps {
  activity: FeedActivity;
  style?: React.CSSProperties;
}

/**
 * SocialFeedItem - Individual feed activity card
 * Interactive feed item with likes, comments, and share functionality
 */
const SocialFeedItem: React.FC<SocialFeedItemProps> = ({ activity, style }) => {
  const navigate = useNavigate();
  const [showLikesModal, setShowLikesModal] = useState(false);

  const handleCardClick = () => {
    if (activity.data.trip_id) {
      navigate(`/trips/${activity.data.trip_id}`);
    }
  };

  const handleLikesClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowLikesModal(true);
  };

  const handleCommentsClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (activity.data.trip_id) {
      navigate(`/trips/${activity.data.trip_id}#comments`);
    }
  };

  const handleShareClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (activity.data.trip_id) {
      const tripUrl = `${window.location.origin}/trips/${activity.data.trip_id}`;
      navigator.clipboard.writeText(tripUrl);
      // TODO: Show toast notification
    }
  };


  const formatTimestamp = (timestamp: string) => {
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

  return (
    <>
      <article
        className="social-feed-item"
        style={style}
        onClick={handleCardClick}
      >
        {/* Thumbnail 120x120px - Left (route marker pin) */}
        <div className="social-feed-item__thumbnail">
          {activity.data.photo_url ? (
            <img
              src={getPhotoUrl(activity.data.photo_url)}
              alt={activity.data.title || 'Foto de ruta'}
              className="social-feed-item__thumbnail-img"
              loading="lazy"
            />
          ) : (
            <div className="social-feed-item__thumbnail-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
          )}
        </div>

        {/* Content - Right (horizontal flow) */}
        <div className="social-feed-item__content">
          {/* Header: avatar + username + timestamp inline */}
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
              {formatTimestamp(activity.timestamp)}
            </time>
          </div>

          {/* Title */}
          {activity.data.title && (
            <h3 className="social-feed-item__title">{activity.data.title}</h3>
          )}

          {/* Distance inline with icon */}
          {activity.data.distance_km && (
            <div className="social-feed-item__distance">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              <span>{activity.data.distance_km} km</span>
            </div>
          )}

          {/* Interaction Buttons - inline, compact */}
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
                <svg
                  className="social-feed-item__interaction-icon"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
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
                <svg
                  className="social-feed-item__interaction-icon"
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
          onClose={() => setShowLikesModal(false)}
        />
      )}
    </>
  );
};

export default SocialFeedItem;
