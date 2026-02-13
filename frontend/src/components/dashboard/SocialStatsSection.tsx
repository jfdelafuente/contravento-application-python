import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useStats } from '../../hooks/useStats';
import { useFollowersTooltip } from '../../hooks/useFollowersTooltip';
import SocialStatTooltip from './SocialStatTooltip';
import './SocialStatsSection.css';
import './SocialStatTooltip.css';

/**
 * SocialStatsSection component - Display followers and following counts
 * Shows social connection statistics for the user
 */
const SocialStatsSection: React.FC = () => {
  const { user } = useAuth();
  const { stats, loading, error } = useStats(user?.username || '');
  const navigate = useNavigate();

  // State for tooltip visibility
  const [activeTooltip, setActiveTooltip] = useState<'followers' | 'following' | null>(null);
  const hoverTimeout = useRef<number | null>(null);
  const leaveTimeout = useRef<number | null>(null);
  const followersCardRef = useRef<HTMLDivElement>(null);
  const followingCardRef = useRef<HTMLDivElement>(null);

  // Detect touch device (T044 - Progressive enhancement)
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    // Detect touch device using media query
    const touchQuery = window.matchMedia('(hover: none)');
    setIsTouchDevice(touchQuery.matches);

    // Listen for changes (e.g., external monitor connected)
    const handleChange = (e: MediaQueryListEvent) => setIsTouchDevice(e.matches);
    touchQuery.addEventListener('change', handleChange);

    return () => touchQuery.removeEventListener('change', handleChange);
  }, []);

  // Initialize tooltip hooks
  const followersTooltip = useFollowersTooltip(user?.username || '', 'followers');
  const followingTooltip = useFollowersTooltip(user?.username || '', 'following');

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (hoverTimeout.current) clearTimeout(hoverTimeout.current);
      if (leaveTimeout.current) clearTimeout(leaveTimeout.current);
    };
  }, []);

  // Handle mouse enter with 500ms delay
  const handleMouseEnter = (type: 'followers' | 'following') => {
    // Clear any pending leave timeout
    if (leaveTimeout.current) {
      clearTimeout(leaveTimeout.current);
      leaveTimeout.current = null;
    }

    // Set 500ms hover delay
    hoverTimeout.current = window.setTimeout(() => {
      // Check count before fetching (T028)
      const count = type === 'followers' ? stats?.followers_count : stats?.following_count;
      if (count && count > 0) {
        // Fetch users and show tooltip
        if (type === 'followers') {
          followersTooltip.fetchUsers();
        } else {
          followingTooltip.fetchUsers();
        }
      }
      setActiveTooltip(type);
    }, 500);
  };

  // Handle mouse leave with 200ms delay
  const handleMouseLeave = () => {
    // Clear any pending hover timeout
    if (hoverTimeout.current) {
      clearTimeout(hoverTimeout.current);
      hoverTimeout.current = null;
    }

    // Set 200ms leave delay
    leaveTimeout.current = window.setTimeout(() => {
      setActiveTooltip(null);
    }, 200);
  };

  // Handle click on touch devices (T044 - Direct navigation)
  const handleCardClick = (type: 'followers' | 'following') => {
    if (isTouchDevice && user?.username) {
      navigate(`/users/${user.username}/${type}`);
    }
  };

  // Handle keyboard focus (T050 - Accessibility)
  const handleFocus = (type: 'followers' | 'following') => {
    // Same behavior as hover for keyboard users
    handleMouseEnter(type);
  };

  // Handle keyboard blur (T050 - Accessibility)
  const handleBlur = () => {
    // Same behavior as mouse leave for keyboard users
    handleMouseLeave();
  };

  // Handle keyboard events (T050 - Escape to close)
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      // Close tooltip immediately (no delay)
      if (hoverTimeout.current) {
        clearTimeout(hoverTimeout.current);
        hoverTimeout.current = null;
      }
      if (leaveTimeout.current) {
        clearTimeout(leaveTimeout.current);
        leaveTimeout.current = null;
      }
      setActiveTooltip(null);
    }
  };

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
          <div
            ref={followersCardRef}
            className={`social-stat-card ${activeTooltip === 'followers' ? 'social-stat-card--with-tooltip' : ''}`}
            tabIndex={0}
            role="button"
            aria-label="Ver seguidores"
            onMouseEnter={!isTouchDevice ? () => handleMouseEnter('followers') : undefined}
            onMouseLeave={!isTouchDevice ? handleMouseLeave : undefined}
            onFocus={() => handleFocus('followers')}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            onClick={() => handleCardClick('followers')}
            style={isTouchDevice ? { cursor: 'pointer' } : undefined}
            aria-describedby={activeTooltip === 'followers' ? 'followers-tooltip' : undefined}
          >
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

            {/* Followers Tooltip */}
            <SocialStatTooltip
              users={followersTooltip.users}
              totalCount={followersTooltip.totalCount}
              type="followers"
              username={user?.username || ''}
              isLoading={followersTooltip.isLoading}
              error={followersTooltip.error}
              visible={activeTooltip === 'followers'}
              triggerRef={followersCardRef}
            />
          </div>

          {/* Following - User with plus icon representing people you follow */}
          <div
            ref={followingCardRef}
            className={`social-stat-card ${activeTooltip === 'following' ? 'social-stat-card--with-tooltip' : ''}`}
            tabIndex={0}
            role="button"
            aria-label="Ver siguiendo"
            onMouseEnter={!isTouchDevice ? () => handleMouseEnter('following') : undefined}
            onMouseLeave={!isTouchDevice ? handleMouseLeave : undefined}
            onFocus={() => handleFocus('following')}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            onClick={() => handleCardClick('following')}
            style={isTouchDevice ? { cursor: 'pointer' } : undefined}
            aria-describedby={activeTooltip === 'following' ? 'following-tooltip' : undefined}
          >
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

            {/* Following Tooltip */}
            <SocialStatTooltip
              users={followingTooltip.users}
              totalCount={followingTooltip.totalCount}
              type="following"
              username={user?.username || ''}
              isLoading={followingTooltip.isLoading}
              error={followingTooltip.error}
              visible={activeTooltip === 'following'}
              triggerRef={followingCardRef}
            />
          </div>
        </div>
      )}
    </section>
  );
};

export default SocialStatsSection;
