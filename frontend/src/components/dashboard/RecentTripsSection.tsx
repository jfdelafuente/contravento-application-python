import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useRecentTrips } from '../../hooks/useRecentTrips';
import RecentTripCard from './RecentTripCard';
import SkeletonLoader from '../common/SkeletonLoader';
import './RecentTripsSection.css';

/**
 * RecentTripsSection component - Display user's recent published trips
 * Shows last 5 trips with photos, or empty state if none
 */
const RecentTripsSection: React.FC = () => {
  const { user } = useAuth();
  const { trips, loading, error } = useRecentTrips(user?.username || '', 5);

  if (error) {
    return (
      <section className="recent-trips-section" aria-labelledby="recent-trips-heading">
        <h2 id="recent-trips-heading" className="recent-trips-section__title">
          Viajes Recientes
        </h2>
        <div className="recent-trips-section__error" role="alert">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
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
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12" />
              <polyline points="12 5 19 12 12 19" />
            </svg>
          </a>
        )}
      </div>

      {loading ? (
        <div className="recent-trips-section__grid" aria-busy="true">
          {[1, 2, 3].map((i) => (
            <div key={i} className="recent-trips-section__skeleton-card">
              <SkeletonLoader variant="rect" height="200px" />
              <div style={{ padding: '1.25rem' }}>
                <SkeletonLoader variant="text" width="80%" height="1.25rem" />
                <SkeletonLoader variant="text" width="60%" height="0.875rem" />
                <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
                  <SkeletonLoader variant="rect" width="60px" height="24px" />
                  <SkeletonLoader variant="rect" width="70px" height="24px" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : trips.length === 0 ? (
        <div className="recent-trips-section__empty">
          <div className="recent-trips-section__empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
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
              key={trip.id}
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

export default RecentTripsSection;
