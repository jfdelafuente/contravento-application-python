/**
 * Activity Feed Empty State Component (Feature 018 - T040)
 *
 * Displays when user has no activities in feed (no followed users or no activity yet).
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './ActivityFeedEmptyState.css';

/**
 * Activity Feed Empty State Component
 *
 * Displays a friendly message when the activity feed is empty.
 * Provides a call-to-action to discover and follow other users.
 *
 * **Displayed when**:
 * - User follows nobody
 * - Followed users have no activities
 *
 * **Features**:
 * - Friendly illustration/icon
 * - Clear explanation message
 * - Call-to-action button to discover users
 *
 * @example
 * ```typescript
 * {activities.length === 0 && <ActivityFeedEmptyState />}
 * ```
 */
export const ActivityFeedEmptyState: React.FC = () => {
  return (
    <div className="activity-feed-empty">
      <div className="empty-state-icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="empty-icon"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"
          />
        </svg>
      </div>

      <h2 className="empty-state-title">Tu feed está vacío</h2>

      <p className="empty-state-message">
        Empieza a seguir a otros ciclistas para ver su actividad aquí.
        Descubre nuevos viajes, fotos y logros de la comunidad.
      </p>

      <Link to="/explore" className="discover-button">
        Descubrir ciclistas
      </Link>
    </div>
  );
};
