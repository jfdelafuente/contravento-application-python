/**
 * PublicFeedPage Component (Feature 013 - T029)
 *
 * Homepage displaying public trips feed.
 * Accessible to all users (no authentication required).
 */

import React, { useState } from 'react';
import { usePublicTrips } from '../hooks/usePublicTrips';
import { PublicTripCard } from '../components/trips/PublicTripCard';
import { PublicHeader } from '../components/layout/PublicHeader';
import './PublicFeedPage.css';

export const PublicFeedPage: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const { trips, pagination, isLoading, error } = usePublicTrips(currentPage, 20);

  // Loading state
  if (isLoading) {
    return (
      <>
        <PublicHeader />
        <div className="public-feed">
          <div className="public-feed__header">
            <h1 className="public-feed__title">Explora Viajes en Bicicleta</h1>
            <p className="public-feed__subtitle">
              Descubre las últimas aventuras compartidas por la comunidad ciclista
            </p>
          </div>
          <div className="public-feed__loading">
            <div className="spinner" aria-label="Cargando viajes..."></div>
            <p>Cargando viajes...</p>
          </div>
        </div>
      </>
    );
  }

  // Error state
  if (error) {
    return (
      <>
        <PublicHeader />
        <div className="public-feed">
          <div className="public-feed__header">
            <h1 className="public-feed__title">Explora Viajes en Bicicleta</h1>
            <p className="public-feed__subtitle">
              Descubre las últimas aventuras compartidas por la comunidad ciclista
            </p>
          </div>
          <div className="public-feed__error">
            <svg
              className="public-feed__error-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h2>Error al cargar viajes</h2>
            <p>{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="public-feed__error-button"
            >
              Intentar de nuevo
            </button>
          </div>
        </div>
      </>
    );
  }

  // Empty state
  if (!trips || trips.length === 0) {
    return (
      <>
        <PublicHeader />
        <div className="public-feed">
          <div className="public-feed__header">
            <h1 className="public-feed__title">Explora Viajes en Bicicleta</h1>
            <p className="public-feed__subtitle">
              Descubre las últimas aventuras compartidas por la comunidad ciclista
            </p>
          </div>
          <div className="public-feed__empty">
            <svg
              className="public-feed__empty-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
              />
            </svg>
            <h2>Aún no hay viajes publicados</h2>
            <p>Sé el primero en compartir tu aventura con la comunidad.</p>
          </div>
        </div>
      </>
    );
  }

  // Success state with trips
  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleNextPage = () => {
    if (pagination && currentPage < pagination.total_pages) {
      setCurrentPage(currentPage + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <>
      <PublicHeader />
      <div className="public-feed">
        <div className="public-feed__header">
          <h1 className="public-feed__title">Explora Viajes en Bicicleta</h1>
          <p className="public-feed__subtitle">
            Descubre las últimas aventuras compartidas por la comunidad ciclista
          </p>
          {pagination && (
            <p className="public-feed__count">
              {pagination.total} {pagination.total === 1 ? 'viaje' : 'viajes'}{' '}
              disponibles
            </p>
          )}
        </div>

      <div className="public-feed__grid">
        {trips.map((trip) => (
          <PublicTripCard key={trip.trip_id} trip={trip} />
        ))}
      </div>

      {/* Pagination */}
      {pagination && pagination.total_pages > 1 && (
        <div className="public-feed__pagination">
          <button
            className="public-feed__pagination-button"
            onClick={handlePreviousPage}
            disabled={currentPage === 1}
            aria-label="Página anterior"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Anterior
          </button>

          <span className="public-feed__pagination-info">
            Página {currentPage} de {pagination.total_pages}
          </span>

          <button
            className="public-feed__pagination-button"
            onClick={handleNextPage}
            disabled={currentPage === pagination.total_pages}
            aria-label="Página siguiente"
          >
            Siguiente
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      )}
      </div>
    </>
  );
};
