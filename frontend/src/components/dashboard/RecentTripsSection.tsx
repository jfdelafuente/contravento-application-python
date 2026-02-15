import React, { memo } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRecentTrips } from '../../hooks/useRecentTrips';
import RecentTripCard from './RecentTripCard';
import SkeletonLoader from '../common/SkeletonLoader';
import './RecentTripsSection.css';

/**
 * Performance: rerender-memo - Prevents re-renders when parent re-renders
 * Performance: rendering-conditional-render - Early return for error state
 * Performance: rendering-hoist-jsx - Static JSX hoisted outside component
 */

// Performance: rendering-hoist-jsx - Static error icon outside component
const ERROR_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

const VIEW_ALL_ARROW = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="5" y1="12" x2="19" y2="12" />
    <polyline points="12 5 19 12 12 19" />
  </svg>
);

const EMPTY_ICON = (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);

/**
 * RecentTripsSection component - Display user's recent published trips
 * Shows last 4 trips in horizontal "route ribbon" format, or empty state if none
 */
const RecentTripsSection: React.FC = () => {
  const { user } = useAuth();
  const { trips, loading, error } = useRecentTrips(user?.username || '', 4);

  // Performance: rendering-conditional-render - Early return for error state
  if (error) {
    return (
      <section className="recent-trips-section" aria-labelledby="recent-trips-heading">
        <h2 id="recent-trips-heading" className="recent-trips-section__title">
          Viajes Recientes
        </h2>
        <div className="recent-trips-section__error" role="alert">
          {ERROR_ICON}
          <p>{error}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="recent-trips-section" aria-labelledby="recent-trips-heading">
      <div className="recent-trips-section__header">
        <h2 id="recent-trips-heading" className="recent-trips-section__title">
          Viajes Recientes
        </h2>
        {trips.length > 0 && (
          <a href="/trips" className="recent-trips-section__view-all">
            Ver todos los viajes
            {VIEW_ALL_ARROW}
          </a>
        )}
      </div>

      {loading ? (
        <div className="recent-trips-section__grid" aria-busy="true">
          {[1, 2, 3].map((i) => (
            <div key={i} className="recent-trips-section__skeleton-card">
              {/* Left: Photo skeleton (40%) */}
              <SkeletonLoader variant="rect" height="100%" />

              {/* Right: Content skeleton (60%) */}
              <div style={{ padding: 'var(--space-4) var(--space-5)', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 'var(--space-2)' }}>
                <SkeletonLoader variant="text" width="85%" height="18px" />
                <SkeletonLoader variant="text" width="65%" height="18px" />
                <div style={{ display: 'flex', gap: 'var(--space-4)', marginTop: 'var(--space-2)' }}>
                  <SkeletonLoader variant="rect" width="80px" height="20px" />
                  <SkeletonLoader variant="rect" width="70px" height="20px" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : trips.length === 0 ? (
        <div className="recent-trips-section__empty">
          <div className="recent-trips-section__empty-icon">
            {EMPTY_ICON}
          </div>
          <h3 className="recent-trips-section__empty-title">Aún no has publicado viajes</h3>
          <p className="recent-trips-section__empty-text">
            Comienza a documentar tus aventuras en bicicleta y compártelas con la comunidad.
          </p>
          <a href="/trips/new" className="recent-trips-section__empty-button">
            Crear tu primer viaje
          </a>
        </div>
      ) : (
        <div className="recent-trips-section__grid">
          {trips.map((trip, index) => (
            <div
              key={trip.trip_id}
              style={{ animationDelay: `${index * 0.1}s` }}
              className="recent-trips-section__grid-item"
            >
              <RecentTripCard trip={trip} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

// Performance: rerender-memo - Add display name for better debugging
RecentTripsSection.displayName = 'RecentTripsSection';

export default memo(RecentTripsSection);
