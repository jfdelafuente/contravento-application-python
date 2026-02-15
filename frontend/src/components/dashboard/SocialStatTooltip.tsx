/**
 * SocialStatTooltip Component
 *
 * Tooltip presentation component for displaying followers/following preview.
 * Handles loading, error, and empty states with Spanish messages.
 *
 * Performance optimizations:
 * - rendering-hoist-jsx: Static JSX hoisted outside component
 * - rerender-memo: Memoized to prevent unnecessary re-renders
 * - rendering-conditional-render: Ternary operator instead of &&
 * - js-cache-property-access: Cached computed values
 *
 * @see specs/019-followers-tooltip/IMPLEMENTATION_GUIDE.md § Task 2.2
 * @see specs/019-followers-tooltip/data-model.md § 5 (SocialStatTooltipProps interface)
 * @see specs/ANALISIS_TOOLTIP_FOLLOWERS.md lines 203-291
 */

import React, { useEffect, useState, memo, useMemo } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import type { UserSummaryForFollow } from '../../services/followService';
import './SocialStatTooltip.css';

interface SocialStatTooltipProps {
  users: UserSummaryForFollow[];
  totalCount: number;
  type: 'followers' | 'following';
  username: string;
  isLoading: boolean;
  error: string | null;
  visible: boolean;
  triggerRef?: React.RefObject<HTMLDivElement>;
}

// rendering-hoist-jsx: Static spinner JSX hoisted outside component
const LoadingSpinner = () => (
  <div className="social-stat-tooltip__loading">
    <div className="spinner"></div>
    <p>Cargando...</p>
  </div>
);

// UserListItem - Memoized child component to prevent re-renders
const UserListItem = memo<{ user: UserSummaryForFollow }>(({ user }) => (
  <li className="social-stat-tooltip__item">
    <Link
      to={`/users/${user.username}`}
      className="social-stat-tooltip__user-link"
    >
      {user.profile_photo_url ? (
        <img
          src={user.profile_photo_url}
          alt={user.username}
          className="social-stat-tooltip__avatar"
          loading="lazy" // Native lazy loading for images
        />
      ) : (
        <div className="social-stat-tooltip__avatar social-stat-tooltip__avatar--placeholder">
          {user.username.charAt(0).toUpperCase()}
        </div>
      )}
      <span className="social-stat-tooltip__username">
        {user.username}
      </span>
    </Link>
  </li>
));

UserListItem.displayName = 'UserListItem';

// rerender-memo: Memoize entire component to prevent unnecessary re-renders
const SocialStatTooltip: React.FC<SocialStatTooltipProps> = memo(({
  users,
  totalCount,
  type,
  username,
  isLoading,
  error,
  visible,
  triggerRef,
}) => {
  const [position, setPosition] = useState({ top: 0, left: 0 });

  // js-cache-property-access: Cache computed values
  const remaining = useMemo(() => totalCount - users.length, [totalCount, users.length]);
  const title = useMemo(() => type === 'followers' ? 'Seguidores' : 'Siguiendo', [type]);
  const emptyMessage = useMemo(
    () => type === 'followers' ? 'No tienes seguidores aún' : 'No sigues a nadie aún',
    [type]
  );

  useEffect(() => {
    if (visible && triggerRef?.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      setPosition({
        top: rect.bottom + window.scrollY + 8,
        left: rect.left + window.scrollX + rect.width / 2,
      });
    }
  }, [visible, triggerRef]);

  // rendering-conditional-render: Early return for hidden state
  if (!visible) return null;

  // rendering-conditional-render: Use ternary for state branches
  const tooltipContent = (
    <div
      className="social-stat-tooltip social-stat-tooltip--portal"
      role="tooltip"
      aria-live="polite"
      style={{
        position: 'fixed',
        top: `${position.top}px`,
        left: `${position.left}px`,
        transform: 'translateX(-50%)',
      }}
    >
      {isLoading ? (
        <LoadingSpinner />
      ) : error ? (
        <div className="social-stat-tooltip__error">
          <p>{error}</p>
        </div>
      ) : users.length === 0 ? (
        <div className="social-stat-tooltip__empty">
          <p>{emptyMessage}</p>
        </div>
      ) : (
        <>
          <div className="social-stat-tooltip__header">
            <h3 className="social-stat-tooltip__title">{title}</h3>
          </div>

          <ul className="social-stat-tooltip__list">
            {users.map((user) => (
              <UserListItem key={user.user_id} user={user} />
            ))}
          </ul>

          {remaining > 0 ? (
            <Link
              to={`/users/${username}/${type}`}
              className="social-stat-tooltip__view-all"
              aria-label={`Ver todos los ${type === 'followers' ? 'seguidores' : 'siguiendo'} (${totalCount} total)`}
            >
              + {remaining} más · Ver todos
            </Link>
          ) : null}
        </>
      )}
    </div>
  );

  return createPortal(tooltipContent, document.body);
});

SocialStatTooltip.displayName = 'SocialStatTooltip';

export default SocialStatTooltip;
