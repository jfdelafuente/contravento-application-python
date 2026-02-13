/**
 * SocialStatTooltip Component
 *
 * Tooltip presentation component for displaying followers/following preview.
 * Handles loading, error, and empty states with Spanish messages.
 *
 * @see specs/019-followers-tooltip/IMPLEMENTATION_GUIDE.md § Task 2.2
 * @see specs/019-followers-tooltip/data-model.md § 5 (SocialStatTooltipProps interface)
 * @see specs/ANALISIS_TOOLTIP_FOLLOWERS.md lines 203-291
 */

import React from 'react';
import { Link } from 'react-router-dom';
import type { UserSummaryForFollow } from '../../types/follow';
import './SocialStatTooltip.css';

interface SocialStatTooltipProps {
  users: UserSummaryForFollow[];
  totalCount: number;
  type: 'followers' | 'following';
  username: string;
  isLoading: boolean;
  error: string | null;
  visible: boolean;
}

const SocialStatTooltip: React.FC<SocialStatTooltipProps> = ({
  users,
  totalCount,
  type,
  username,
  isLoading,
  error,
  visible,
}) => {
  if (!visible) return null;

  const remaining = totalCount - users.length;
  const title = type === 'followers' ? 'Seguidores' : 'Siguiendo';
  const emptyMessage =
    type === 'followers'
      ? 'No tienes seguidores aún'
      : 'No sigues a nadie aún';

  return (
    <div
      className="social-stat-tooltip"
      role="tooltip"
      aria-live="polite"
    >
      {isLoading ? (
        <div className="social-stat-tooltip__loading">
          <div className="spinner"></div>
          <p>Cargando...</p>
        </div>
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
              <li key={user.user_id} className="social-stat-tooltip__item">
                <Link
                  to={`/users/${user.username}`}
                  className="social-stat-tooltip__user-link"
                >
                  {user.profile_photo_url ? (
                    <img
                      src={user.profile_photo_url}
                      alt={user.username}
                      className="social-stat-tooltip__avatar"
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
            ))}
          </ul>

          {remaining > 0 && (
            <Link
              to={`/users/${username}/${type}`}
              className="social-stat-tooltip__view-all"
            >
              + {remaining} más · Ver todos
            </Link>
          )}
        </>
      )}
    </div>
  );
};

export default SocialStatTooltip;
