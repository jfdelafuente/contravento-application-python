import React from 'react';
import StatsCard from './StatsCard';
import { useStats } from '../../hooks/useStats';
import { useAuth } from '../../contexts/AuthContext';
import { formatStatNumber, formatDistance, formatCountries } from '../../utils/formatters';
import './StatsSection.css';

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
        Tus Estadísticas
      </h2>
      <div className="stats-section__grid">
        {/* Stat 1: Total Trips */}
        <StatsCard
          title="Viajes Publicados"
          value={stats ? formatStatNumber(stats.total_trips) : '0'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          }
          loading={loading}
          error={error || undefined}
          color="var(--color-primary)"
        />

        {/* Stat 2: Total Distance */}
        <StatsCard
          title="Kilómetros Recorridos"
          value={stats ? formatDistance(stats.total_kilometers) : '0 km'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          }
          loading={loading}
          error={error || undefined}
          color="var(--color-forest)"
        />

        {/* Stat 3: Countries Visited */}
        <StatsCard
          title="Países Visitados"
          value={stats ? stats.countries_visited.length : 0}
          subtitle={stats ? formatCountries(stats.countries_visited.map(c => c.name)) : undefined}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="2" y1="12" x2="22" y2="12" />
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            </svg>
          }
          loading={loading}
          error={error || undefined}
          color="var(--color-earth)"
        />

        {/* Stat 4: Total Photos */}
        <StatsCard
          title="Fotos Subidas"
          value={stats ? formatStatNumber(stats.total_photos) : '0'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          }
          loading={loading}
          error={error || undefined}
          color="var(--color-brown)"
        />

        {/* Stat 5: Achievements */}
        <StatsCard
          title="Logros Desbloqueados"
          value={stats ? formatStatNumber(stats.achievements_count) : '0'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="8" r="7" />
              <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88" />
            </svg>
          }
          loading={loading}
          error={error || undefined}
          color="var(--color-accent)"
        />

        {/* Stat 6: Followers */}
        <StatsCard
          title="Seguidores"
          value={stats && stats.followers_count !== undefined ? formatStatNumber(stats.followers_count) : '0'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          }
          loading={loading}
          error={error || undefined}
          color="var(--color-secondary)"
        />

        {/* Stat 7: Following */}
        <StatsCard
          title="Siguiendo"
          value={stats && stats.following_count !== undefined ? formatStatNumber(stats.following_count) : '0'}
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="8.5" cy="7" r="4" />
              <line x1="20" y1="8" x2="20" y2="14" />
              <line x1="23" y1="11" x2="17" y2="11" />
            </svg>
          }
          loading={loading}
          error={error || undefined}
          color="var(--color-info)"
        />
      </div>
    </section>
  );
};

export default StatsSection;
