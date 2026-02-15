import React, { memo } from 'react';
import StatsCard from './StatsCard';
import { useStats } from '../../hooks/useStats';
import { useAuth } from '../../contexts/AuthContext';
import { formatStatNumber, formatDistance, formatCountries } from '../../utils/formatters';
import './StatsSection.css';

/**
 * Performance: rerender-memo - Prevents re-renders when parent re-renders unnecessarily
 * This component only depends on user.username from auth context
 */

// Performance: rendering-hoist-jsx - Static SVG icons hoisted outside component
const TRIPS_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);

const DISTANCE_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);

const COUNTRIES_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <line x1="2" y1="12" x2="22" y2="12" />
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
  </svg>
);

const PHOTOS_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <circle cx="8.5" cy="8.5" r="1.5" />
    <polyline points="21 15 16 10 5 21" />
  </svg>
);

/**
 * StatsSection component - Display 4 main user statistics
 * - Total published trips
 * - Total distance traveled
 * - Countries visited
 * - Current followers
 */
const StatsSection: React.FC = () => {
  const { user } = useAuth();
  const { stats, loading, error } = useStats(user?.username || '');

  return (
    <section className="stats-section" aria-labelledby="stats-heading">
      <h2 id="stats-heading" className="stats-section__title">
        Bitácora
      </h2>
      <div className="stats-section__grid">
        {/* Stat 1: Total Trips */}
        <StatsCard
          title="Viajes Publicados"
          value={stats ? formatStatNumber(stats.total_trips) : '0'}
          icon={TRIPS_ICON}
          loading={loading}
          error={error || undefined}
          color="var(--accent-amber)"
        />

        {/* Stat 2: Total Distance */}
        <StatsCard
          title="Kilómetros Recorridos"
          value={stats ? formatDistance(stats.total_kilometers) : '0 km'}
          icon={DISTANCE_ICON}
          loading={loading}
          error={error || undefined}
          color="var(--accent-moss)"
        />

        {/* Stat 3: Countries Visited */}
        <StatsCard
          title="Países Visitados"
          value={stats ? stats.countries_visited.length : 0}
          subtitle={stats ? formatCountries(stats.countries_visited.map(c => c.name)) : undefined}
          icon={COUNTRIES_ICON}
          loading={loading}
          error={error || undefined}
          color="#dc2626"
        />

        {/* Stat 4: Total Photos */}
        <StatsCard
          title="Fotos Subidas"
          value={stats ? formatStatNumber(stats.total_photos) : '0'}
          icon={PHOTOS_ICON}
          loading={loading}
          error={error || undefined}
          color="var(--accent-amber)"
        />
      </div>
    </section>
  );
};

// Performance: rerender-memo - Add display name for better debugging
StatsSection.displayName = 'StatsSection';

export default memo(StatsSection);
