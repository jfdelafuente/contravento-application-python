/**
 * Activity Card Achievement Variant (Feature 018)
 *
 * Displays ACHIEVEMENT_UNLOCKED activity with achievement badge and name.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { ActivityFeedItem } from '../../types/activityFeed';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { getAvatarUrl } from '../../utils/tripHelpers';
import { LikeButton } from './LikeButton';
import './ActivityCard.css';

interface ActivityCardAchievementProps {
  activity: ActivityFeedItem;
}

/**
 * Activity Card Achievement Component
 *
 * Displays an achievement unlock activity with:
 * - User info (avatar, username)
 * - Relative timestamp
 * - Achievement badge icon
 * - Achievement name
 * - Like and comment counts
 *
 * **Metadata Expected**:
 * - achievement_name: string
 * - achievement_badge: string (emoji or icon)
 */
export const ActivityCardAchievement: React.FC<ActivityCardAchievementProps> = ({
  activity,
}) => {
  const { user, metadata, created_at, likes_count, comments_count } = activity;

  const achievementName = metadata.achievement_name || 'Logro Desbloqueado';
  const achievementBadge = metadata.achievement_badge || '🏆';

  const timeAgo = formatDistanceToNow(new Date(created_at), {
    addSuffix: true,
    locale: es,
  });

  const profilePhotoUrl = getAvatarUrl(user.photo_url);

  return (
    <article className="activity-card activity-card-achievement">
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
            <span className="activity-action">desbloqueó un logro</span>
          </div>
          <time className="activity-timestamp" dateTime={created_at}>
            {timeAgo}
          </time>
        </div>
      </header>

      <div className="activity-card-body">
        <div className="achievement-display">
          <div className="achievement-badge">{achievementBadge}</div>
          <div className="achievement-name">{achievementName}</div>
        </div>
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
