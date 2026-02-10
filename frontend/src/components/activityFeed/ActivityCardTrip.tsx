/**
 * Activity Card Trip Variant (Feature 018 - T039)
 *
 * Displays TRIP_PUBLISHED activity with trip title, distance, and cover photo.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { ActivityFeedItem } from '../../types/activityFeed';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getPhotoUrl, getAvatarUrl } from '../../utils/tripHelpers';
import { LikeButton } from './LikeButton';
import './ActivityCard.css';

interface ActivityCardTripProps {
  activity: ActivityFeedItem;
}

/**
 * Activity Card Trip Component
 *
 * Displays a trip publication activity with:
 * - User info (avatar, username)
 * - Relative timestamp
 * - Trip title and distance
 * - Cover photo (if available)
 * - Like and comment counts
 *
 * **Metadata Expected**:
 * - trip_title: string
 * - trip_distance_km?: number
 * - trip_photo_url?: string
 *
 * @example
 * ```typescript
 * <ActivityCardTrip activity={tripPublishedActivity} />
 * ```
 */
export const ActivityCardTrip: React.FC<ActivityCardTripProps> = ({ activity }) => {
  const { user, metadata, created_at, likes_count, comments_count } = activity;

  // Extract trip metadata
  const tripId = metadata.trip_id;
  const tripTitle = metadata.trip_title || 'Sin título';
  const tripDistance = metadata.trip_distance_km;
  const tripPhotoUrl = metadata.trip_photo_url;

  // Format timestamp (relative, Spanish)
  const timeAgo = formatDistanceToNow(new Date(created_at), {
    addSuffix: true,
    locale: es,
  });

  // Get profile photo URL with fallback
  const profilePhotoUrl = getAvatarUrl(user.photo_url);

  return (
    <article className="activity-card">
      {/* Header: User info and timestamp */}
      <header className="activity-card-header">
        <Link to={`/users/${user.username}`} className="user-avatar-link">
          <img
            src={profilePhotoUrl}
            alt={`Avatar de ${user.username}`}
            className="user-avatar"
          />
        </Link>

        <div className="activity-card-meta">
          <div className="activity-card-title">
            <Link to={`/users/${user.username}`} className="username-link">
              {user.username}
            </Link>
            <span className="activity-action">publicó un viaje</span>
          </div>
          <time className="activity-timestamp" dateTime={created_at}>
            {timeAgo}
          </time>
        </div>
      </header>

      {/* Body: Trip content - Clickable to navigate to trip detail */}
      {tripId ? (
        <Link to={`/trips/${tripId}`} className="activity-card-body-link">
          <div className="activity-card-body">
            <h3 className="trip-title">{tripTitle}</h3>

            {tripDistance && (
              <p className="trip-distance">
                📍 {tripDistance.toFixed(1)} km
              </p>
            )}

            {tripPhotoUrl && (
              <div className="trip-photo-container">
                <img
                  src={getPhotoUrl(tripPhotoUrl)}
                  alt={tripTitle}
                  className="trip-photo"
                  loading="lazy"
                />
              </div>
            )}
          </div>
        </Link>
      ) : (
        <div className="activity-card-body">
          <h3 className="trip-title">{tripTitle}</h3>

          {tripDistance && (
            <p className="trip-distance">
              📍 {tripDistance.toFixed(1)} km
            </p>
          )}

          {tripPhotoUrl && (
            <div className="trip-photo-container">
              <img
                src={getPhotoUrl(tripPhotoUrl)}
                alt={tripTitle}
                className="trip-photo"
                loading="lazy"
              />
            </div>
          )}
        </div>
      )}

      {/* Footer: Social interactions */}
      <footer className="activity-card-footer">
        <div className="interaction-stats">
          <LikeButton
            activityId={activity.activity_id}
            isLiked={activity.is_liked_by_me}
            likesCount={likes_count}
          />
          <span className="stat-item">
            💬 {comments_count} {comments_count === 1 ? 'comentario' : 'comentarios'}
          </span>
        </div>
      </footer>
    </article>
  );
};
