import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useStats } from '../../hooks/useStats';
import './SocialStatsSection.css';

/**
 * SocialStatsSection component - Display followers and following counts
 * Shows social connection statistics for the user
 */
const SocialStatsSection: React.FC = () => {
  const { user } = useAuth();
  const { stats, loading, error } = useStats(user?.username || '');

  return (
    <section className="social-stats-section" aria-labelledby="social-stats-heading">
      <h2 id="social-stats-heading" className="social-stats-section__title">
        Pelotón
      </h2>

      {loading && (
        <div className="social-stats-section__loading">
          <div className="spinner"></div>
        </div>
      )}

      {error && (
        <div className="social-stats-section__error">
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && (
        <div className="social-stats-section__grid">
          {/* Followers - Heart icon representing people who follow you */}
          <div className="social-stat-card">
            <div className="social-stat-card__icon social-stat-card__icon--followers">
              <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
              </svg>
            </div>
            <div className="social-stat-card__content">
              <h3 className="social-stat-card__label">Seguidores</h3>
              <p className="social-stat-card__value">
                {stats?.followers_count ?? 0}
              </p>
            </div>
          </div>

          {/* Following - User with plus icon representing people you follow */}
          <div className="social-stat-card">
            <div className="social-stat-card__icon social-stat-card__icon--following">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="8.5" cy="7" r="4" />
                <line x1="20" y1="8" x2="20" y2="14" />
                <line x1="23" y1="11" x2="17" y2="11" />
              </svg>
            </div>
            <div className="social-stat-card__content">
              <h3 className="social-stat-card__label">Siguiendo</h3>
              <p className="social-stat-card__value">
                {stats?.following_count ?? 0}
              </p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default SocialStatsSection;
