/**
 * LikeButton Component (Feature 018 - US2)
 *
 * Interactive like button for activity feed items with optimistic updates.
 */

import React from 'react';
import { useActivityLike } from '../../hooks/useActivityLike';
import './LikeButton.css';

interface LikeButtonProps {
  activityId: string;
  isLiked: boolean;
  likesCount: number;
  compact?: boolean;
}

/**
 * Like button with heart icon, count, and animated state transitions.
 *
 * Features:
 * - Optimistic UI updates (instant feedback)
 * - Animated heart on like/unlike
 * - Disabled state during API call
 * - Accessible (keyboard navigation, ARIA labels)
 *
 * @param activityId - Activity ID to like/unlike
 * @param isLiked - Whether current user has liked this activity
 * @param likesCount - Total number of likes
 * @param compact - Use compact layout (icon only, no text)
 *
 * @example
 * ```tsx
 * <LikeButton
 *   activityId={activity.activity_id}
 *   isLiked={activity.is_liked_by_me}
 *   likesCount={activity.likes_count}
 * />
 * ```
 */
export const LikeButton: React.FC<LikeButtonProps> = ({
  activityId,
  isLiked,
  likesCount,
  compact = false,
}) => {
  const { toggleLike, isLiking } = useActivityLike({ activityId });

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    toggleLike();
  };

  const ariaLabel = isLiked
    ? `Quitar me gusta (${likesCount} ${likesCount === 1 ? 'me gusta' : 'me gusta'})`
    : `Dar me gusta (${likesCount} ${likesCount === 1 ? 'me gusta' : 'me gusta'})`;

  return (
    <button
      className={`like-button ${isLiked ? 'like-button--liked' : ''} ${
        compact ? 'like-button--compact' : ''
      }`}
      onClick={handleClick}
      disabled={isLiking}
      aria-label={ariaLabel}
      aria-pressed={isLiked}
      type="button"
    >
      <span className="like-button__icon" aria-hidden="true">
        {isLiked ? '❤️' : '🤍'}
      </span>
      {!compact && (
        <span className="like-button__count">
          {likesCount}
        </span>
      )}
    </button>
  );
};
