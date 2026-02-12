// frontend/src/components/landing/DiscoverTripsSection.tsx

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getPublicTrips } from '../../services/tripsService';
import { getPhotoUrl } from '../../utils/tripHelpers';
import { PublicTripSummary } from '../../types/trip';
import './DiscoverTripsSection.css';

/**
 * DiscoverTripsSection Component
 *
 * Displays the 4 most recent public trips to inspire visitors.
 * Shows trip cards with photo, title, and username.
 */
export const DiscoverTripsSection: React.FC = () => {
  const [trips, setTrips] = useState<PublicTripSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        setIsLoading(true);
        const response = await getPublicTrips(1, 4);

        console.log('[DiscoverTripsSection] API Response:', response);

        if (response.trips && Array.isArray(response.trips)) {
          setTrips(response.trips);
        } else {
          console.error('[DiscoverTripsSection] Invalid response format:', response);
          setError('Error al cargar viajes');
        }
      } catch (err: any) {
        console.error('[DiscoverTripsSection] Fetch Error:', err);
        console.error('[DiscoverTripsSection] Error details:', {
          message: err.message,
          response: err.response,
          status: err.response?.status,
        });
        setError('Error al cargar viajes');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrips();
  }, []);

  if (isLoading) {
    return (
      <section className="discover-trips-section">
        <div className="discover-trips-container">
          <h2 className="discover-trips-title">Descubre nuevas rutas</h2>
          <div className="discover-trips-loading">
            <p>Cargando viajes...</p>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="discover-trips-section">
        <div className="discover-trips-container">
          <h2 className="discover-trips-title">Descubre nuevas rutas</h2>
          <div className="discover-trips-error">
            <p>Error al cargar viajes. Por favor, intenta más tarde.</p>
          </div>
        </div>
      </section>
    );
  }

  if (trips.length === 0) {
    return (
      <section className="discover-trips-section">
        <div className="discover-trips-container">
          <h2 className="discover-trips-title">Descubre nuevas rutas</h2>
          <div className="discover-trips-empty">
            <p>No hay viajes disponibles en este momento.</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="discover-trips-section" aria-labelledby="discover-trips-title">
      <div className="discover-trips-container">
        <h2 id="discover-trips-title" className="discover-trips-title">
          Descubre nuevas rutas
        </h2>

        <div className="discover-trips-grid">
          {trips.map((trip) => (
            <Link
              key={trip.trip_id}
              to={`/trips/${trip.trip_id}`}
              className="discover-trip-card"
            >
              <div className="discover-trip-photo">
                <img
                  src={getPhotoUrl(trip.photo?.photo_url)}
                  alt={trip.title}
                  loading="lazy"
                />
              </div>
              <div className="discover-trip-content">
                <h3 className="discover-trip-title">{trip.title}</h3>
                <p className="discover-trip-username">por @{trip.author.username}</p>
              </div>
            </Link>
          ))}
        </div>

        <div className="discover-trips-cta">
          <Link to="/trips/public" className="discover-trips-link">
            Ver todos los viajes
          </Link>
        </div>
      </div>
    </section>
  );
};
