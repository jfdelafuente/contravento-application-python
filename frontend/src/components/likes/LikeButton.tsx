// src/components/likes/LikeButton.tsx

import React from 'react';
import { useLike } from '../../hooks/useLike';
import './LikeButton.css';

/**
 * LikeButton component (T061).
 *
 * Features:
 * - Heart icon (outline when not liked, filled when liked)
 * - Like count display
 * - Optimistic UI updates
 * - Loading state with disabled button
 * - Accessible keyboard navigation
 *
 * Usage:
 * <LikeButton tripId="123" initialLiked={false} initialCount={5} />
 */

interface LikeButtonProps {
  tripId: string;
  initialLiked?: boolean;
  initialCount?: number;
  size?: 'small' | 'medium' | 'large';
  showCount?: boolean;
  onCountClick?: (e: React.MouseEvent) => void; // Callback when clicking the count (e.g., to open likes list)
}

export const LikeButton: React.FC<LikeButtonProps> = ({
  tripId,
  initialLiked = false,
  initialCount = 0,
  size = 'medium',
  showCount = true,
  onCountClick,
}) => {
  const { isLiked, likeCount, isLoading, toggleLike } = useLike(
    tripId,
    initialLiked,
    initialCount
  );

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation(); // Prevent event bubbling to parent (FeedItem)
    toggleLike();
  };

  const handleCountClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering like button
    if (onCountClick) {
      onCountClick(e);
    }
  };

  return (
    <button
      className={`like-button like-button--${size} ${isLiked ? 'like-button--liked' : ''}`}
      onClick={handleClick}
      disabled={isLoading}
      aria-label={isLiked ? 'Quitar like' : 'Dar like'}
      aria-pressed={isLiked}
      title={isLiked ? 'Quitar like' : 'Dar like'}
    >
      <svg
        className="like-button__icon"
        viewBox="0 0 24 24"
        fill={isLiked ? 'currentColor' : 'none'}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
      </svg>

      {showCount && (
        <span
          className={`like-button__count ${onCountClick && likeCount > 0 ? 'like-button__count--clickable' : ''}`}
          aria-label={`${likeCount} likes`}
          onClick={onCountClick && likeCount > 0 ? handleCountClick : undefined}
          role={onCountClick && likeCount > 0 ? 'button' : undefined}
          tabIndex={onCountClick && likeCount > 0 ? 0 : undefined}
        >
          {likeCount}
        </span>
      )}

      {isLoading && <span className="like-button__spinner" aria-hidden="true"></span>}
    </button>
  );
};
