// src/components/social/FollowButton.tsx

import React from 'react';
import { useFollow } from '../../hooks/useFollow';
import './FollowButton.css';

/**
 * FollowButton component (Feature 004 - US1).
 *
 * Features:
 * - Follow/Unfollow toggle button
 * - Optimistic UI updates
 * - Loading state with disabled button
 * - Accessible keyboard navigation
 * - Prevents following yourself
 *
 * Usage:
 * <FollowButton userId="123" initialFollowing={false} currentUserId="456" />
 */

interface FollowButtonProps {
  userId: string;
  initialFollowing?: boolean;
  currentUserId?: string;
  size?: 'small' | 'medium' | 'large';
  variant?: 'primary' | 'secondary';
}

export const FollowButton: React.FC<FollowButtonProps> = ({
  userId,
  initialFollowing = false,
  currentUserId,
  size = 'medium',
  variant = 'primary',
}) => {
  const { isFollowing, isLoading, toggleFollow } = useFollow(
    userId,
    initialFollowing
  );

  // Don't show button if user is viewing their own profile
  if (currentUserId && currentUserId === userId) {
    return null;
  }

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation(); // Prevent event bubbling to parent (e.g., TripCard click)
    toggleFollow();
  };

  return (
    <button
      className={`follow-button follow-button--${size} follow-button--${variant} ${
        isFollowing ? 'follow-button--following' : ''
      }`}
      onClick={handleClick}
      disabled={isLoading}
      aria-label={isFollowing ? 'Dejar de seguir' : 'Seguir'}
      aria-pressed={isFollowing}
      title={isFollowing ? 'Dejar de seguir' : 'Seguir'}
    >
      {isLoading ? (
        <span className="follow-button__spinner" aria-hidden="true"></span>
      ) : (
        <>
          <svg
            className="follow-button__icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            {isFollowing ? (
              // User Check icon (following)
              <>
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <polyline points="16 11 18 13 22 9"></polyline>
              </>
            ) : (
              // User Plus icon (not following)
              <>
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <line x1="19" y1="8" x2="19" y2="14"></line>
                <line x1="22" y1="11" x2="16" y2="11"></line>
              </>
            )}
          </svg>
          <span className="follow-button__text">
            {isFollowing ? 'Siguiendo' : 'Seguir'}
          </span>
        </>
      )}
    </button>
  );
};
