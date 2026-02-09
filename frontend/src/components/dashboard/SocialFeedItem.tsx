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
  const getActivityIcon = () => {
    switch (activity.type) {
      case 'route_published':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 11a3 3 0 1 0 6 0a3 3 0 0 0 -6 0" />
            <path d="M17.657 16.657l-4.243 4.243a2 2 0 0 1 -2.827 0l-4.244 -4.243a8 8 0 1 1 11.314 0z" />
          </svg>
        );
      case 'achievement':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M6 9h12M6 15h12M9 3v18M15 3v18" />
          </svg>
        );
      case 'photo_uploaded':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
        );
      case 'new_follower':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="8.5" cy="7" r="4" />
            <line x1="20" y1="8" x2="20" y2="14" />
            <line x1="23" y1="11" x2="17" y2="11" />
          </svg>
        );
      case 'comment_added':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        );
      case 'trip_liked':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        );
      case 'route_completed':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        );
      case 'profile_updated':
        return (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        );
    }
  };

  const getActivityText = () => {
    const username = activity.user.username;

    switch (activity.type) {
      case 'route_published':
        return (
          <>
            <strong>{username}</strong> publicó una nueva ruta
          </>
        );
      case 'achievement':
        return (
          <>
            <strong>{username}</strong> consiguió un logro
          </>
        );
      case 'photo_uploaded':
        return (
          <>
            <strong>{username}</strong> subió una foto
          </>
        );
      case 'new_follower':
        return (
          <>
            <strong>{username}</strong> te está siguiendo
          </>
        );
      case 'comment_added':
        return (
          <>
            <strong>{username}</strong> comentó en una ruta
          </>
        );
      case 'trip_liked':
        return (
          <>
            <strong>{username}</strong> le gustó tu viaje
          </>
        );
      case 'route_completed':
        return (
          <>
            <strong>{username}</strong> completó una ruta
          </>
        );
      case 'profile_updated':
        return (
          <>
            <strong>{username}</strong> actualizó su perfil
          </>
        );
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

  const activityTypeClass = `social-feed-item--${activity.type.replace('_', '-')}`;

  return (
    <>
    <article
      className={`social-feed-item ${activityTypeClass}`}
      style={style}
      onClick={handleCardClick}
    >
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

        <div className="social-feed-item__meta">
          <p className="social-feed-item__text">{getActivityText()}</p>
          <time className="social-feed-item__timestamp" dateTime={activity.timestamp}>
            <svg
              className="social-feed-item__marker-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            {formatTimestamp(activity.timestamp)}
          </time>
        </div>
      </div>

      {activity.data.title && (
        <div className="social-feed-item__content">
          <h3 className="social-feed-item__title">{activity.data.title}</h3>
          {activity.data.description && (
            <p className="social-feed-item__description">{activity.data.description}</p>
          )}
          {activity.data.distance_km && (
            <div className="social-feed-item__stat">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              <span>{activity.data.distance_km} km</span>
            </div>
          )}
          {activity.data.achievement_name && (
            <div className="social-feed-item__badge">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="8" r="7" />
                <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
              </svg>
              <span>{activity.data.achievement_name}</span>
            </div>
          )}
        </div>
      )}

      {activity.data.photo_url && (
        <div className="social-feed-item__photo">
          <img
            src={getPhotoUrl(activity.data.photo_url)}
            alt={activity.data.title || 'Foto de ruta'}
            loading="lazy"
          />
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
