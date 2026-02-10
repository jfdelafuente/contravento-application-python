/**
 * Activity Card Photo Variant (Feature 018)
 *
 * Displays PHOTO_UPLOADED activity with photo preview.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { ActivityFeedItem } from '../../types/activityFeed';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getPhotoUrl, getAvatarUrl } from '../../utils/tripHelpers';
import { LikeButton } from './LikeButton';
import './ActivityCard.css';

interface ActivityCardPhotoProps {
  activity: ActivityFeedItem;
}

/**
 * Activity Card Photo Component
 *
 * Displays a photo upload activity with:
 * - User info (avatar, username)
 * - Relative timestamp
 * - Photo preview
 * - Related trip title
 * - Like and comment counts
 *
 * **Metadata Expected**:
 * - photo_url: string
 * - trip_title?: string
 */
export const ActivityCardPhoto: React.FC<ActivityCardPhotoProps> = ({ activity }) => {
  const { user, metadata, created_at, likes_count, comments_count } = activity;

  const photoUrl = metadata.photo_url;
  const tripTitle = metadata.trip_title || 'un viaje';

  const timeAgo = formatDistanceToNow(new Date(created_at), {
    addSuffix: true,
    locale: es,
  });

  const profilePhotoUrl = getAvatarUrl(user.photo_url);

  return (
    <article className="activity-card">
      <header className="activity-card-header">
        <Link to={`/profile/${user.username}`} className="user-avatar-link">
          <img
            src={profilePhotoUrl}
            alt={`Avatar de ${user.username}`}
            className="user-avatar"
          />
        </Link>

        <div className="activity-card-meta">
          <div className="activity-card-title">
            <Link to={`/profile/${user.username}`} className="username-link">
              {user.username}
            </Link>
            <span className="activity-action">subió una foto a {tripTitle}</span>
          </div>
          <time className="activity-timestamp" dateTime={created_at}>
            {timeAgo}
          </time>
        </div>
      </header>

      <div className="activity-card-body">
        {photoUrl && (
          <div className="photo-preview-container">
            <img
              src={getPhotoUrl(photoUrl)}
              alt="Foto subida"
              className="photo-preview"
              loading="lazy"
            />
          </div>
        )}
      </div>

      <footer className="activity-card-footer">
        <div className="interaction-stats">
          <LikeButton
            activityId={activity.activity_id}
            isLiked={activity.is_liked_by_me}
            likesCount={likes_count}
          />
          <span className="stat-item">💬 {comments_count}</span>
        </div>
      </footer>
    </article>
  );
};
