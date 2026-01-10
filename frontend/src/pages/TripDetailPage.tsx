/**
 * TripDetailPage Component
 *
 * Full trip detail page with hero image, photo gallery, map, and metadata.
 * Includes owner-only action buttons (Edit, Delete, Publish).
 *
 * Route: /trips/:tripId
 */

import React, { useState, useEffect, lazy, Suspense } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { TripGallery } from '../components/trips/TripGallery';
import { getTripById, deleteTrip, publishTrip } from '../services/tripService';
import {
  getDifficultyLabel,
  getDifficultyClass,
  formatDate,
  formatDateRange,
  formatDistance,
  getStatusLabel,
  getStatusClass,
  getPhotoUrl,
} from '../utils/tripHelpers';
import { Trip } from '../types/trip';
import toast from 'react-hot-toast';
import './TripDetailPage.css';

// Lazy load TripMap (only loads if trip has locations)
const TripMap = lazy(() =>
  import('../components/trips/TripMap').then((module) => ({ default: module.TripMap }))
);

export const TripDetailPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [trip, setTrip] = useState<Trip | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Fetch trip details
  useEffect(() => {
    const fetchTrip = async () => {
      if (!tripId) {
        setError('ID de viaje no válido');
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const tripData = await getTripById(tripId);
        setTrip(tripData);
      } catch (err: any) {
        console.error('Error fetching trip:', err);
        console.error('Error details:', {
          status: err.response?.status,
          data: err.response?.data,
          message: err.message,
        });

        // Handle authentication errors (401) - redirect to login
        if (err.response?.status === 401) {
          toast.error('Tu sesión ha expirado. Por favor inicia sesión nuevamente.', {
            duration: 5000,
            position: 'top-center',
          });
          navigate('/login');
          return;
        }

        const errorMessage =
          err.response?.status === 404
            ? 'Viaje no encontrado'
            : err.response?.status === 403
            ? 'No tienes permiso para ver este viaje'
            : 'Error al cargar el viaje. Intenta nuevamente.';

        setError(errorMessage);

        toast.error(errorMessage, {
          duration: 5000,
          position: 'top-center',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrip();
  }, [tripId]);

  // Check if current user is the trip owner
  const isOwner = user && trip && user.user_id === trip.user_id;

  // Handle trip deletion - Phase 8: Show confirmation dialog
  const handleDelete = () => {
    if (!trip || !isOwner) return;
    setShowDeleteConfirm(true);
  };

  // Confirm deletion after dialog confirmation
  const confirmDelete = async () => {
    if (!trip) return;

    setShowDeleteConfirm(false);
    setIsDeleting(true);

    try {
      await deleteTrip(trip.trip_id);

      toast.success('Viaje eliminado correctamente', {
        duration: 3000,
        position: 'top-center',
      });

      navigate('/trips');
    } catch (err: any) {
      console.error('Error deleting trip:', err);

      // Handle specific error cases
      const errorMessage =
        err.response?.status === 404
          ? 'Viaje no encontrado'
          : err.response?.status === 403
          ? 'No tienes permiso para eliminar este viaje'
          : err.response?.data?.error?.message || 'Error al eliminar el viaje. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  // Cancel deletion
  const cancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  // Handle trip publishing
  const handlePublish = async () => {
    if (!trip || !isOwner || trip.status !== 'draft') return;

    // Validate publish requirements
    if (trip.description.length < 50) {
      toast.error('La descripción debe tener al menos 50 caracteres para publicar', {
        duration: 5000,
        position: 'top-center',
      });
      return;
    }

    setIsPublishing(true);

    try {
      const publishedTrip = await publishTrip(trip.trip_id);
      setTrip(publishedTrip);

      toast.success('Viaje publicado correctamente', {
        duration: 3000,
        position: 'top-center',
      });
    } catch (err: any) {
      console.error('Error publishing trip:', err);

      const errorMessage =
        err.response?.data?.error?.message || 'Error al publicar el viaje. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsPublishing(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="trip-detail-page trip-detail-page--loading">
        <div className="trip-detail-page__skeleton">
          <div className="trip-detail-page__skeleton-hero" />
          <div className="trip-detail-page__skeleton-content">
            <div className="trip-detail-page__skeleton-title" />
            <div className="trip-detail-page__skeleton-meta" />
            <div className="trip-detail-page__skeleton-description" />
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !trip) {
    return (
      <div className="trip-detail-page trip-detail-page--error">
        <div className="trip-detail-page__error">
          <div className="trip-detail-page__error-icon">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h1 className="trip-detail-page__error-title">{error || 'Viaje no encontrado'}</h1>
          <Link to="/trips" className="trip-detail-page__error-button">
            Volver a Mis Viajes
          </Link>
        </div>
      </div>
    );
  }

  // Check if trip has valid locations for map
  const hasValidLocations =
    trip.locations && trip.locations.some((loc) => loc.latitude !== null && loc.longitude !== null);

  return (
    <div className="trip-detail-page">
      {/* Hero Section */}
      <div className="trip-detail-page__hero">
        {trip.photos.length > 0 ? (
          <img
            src={getPhotoUrl(trip.photos[0].photo_url) || ''}
            alt={trip.title}
            className="trip-detail-page__hero-image"
          />
        ) : (
          <div className="trip-detail-page__hero-placeholder">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Status Badge (T039: owner-only for drafts) */}
        {trip.status === 'draft' && isOwner && (
          <div className={`trip-detail-page__status-badge ${getStatusClass(trip.status)}`}>
            {getStatusLabel(trip.status)}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="trip-detail-page__content">
        {/* Header with Actions (T039: owner-only action buttons) */}
        <div className="trip-detail-page__header">
          <div className="trip-detail-page__header-content">
            <h1 className="trip-detail-page__title">{trip.title}</h1>

            {/* Metadata */}
            <div className="trip-detail-page__meta">
              {/* Date */}
              <div className="trip-detail-page__meta-item">
                <svg
                  className="trip-detail-page__meta-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span className="trip-detail-page__meta-text">
                  {formatDateRange(trip.start_date, trip.end_date)}
                </span>
              </div>

              {/* Distance */}
              {trip.distance_km !== null && (
                <div className="trip-detail-page__meta-item">
                  <svg
                    className="trip-detail-page__meta-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                    />
                  </svg>
                  <span className="trip-detail-page__meta-text">
                    {formatDistance(trip.distance_km)}
                  </span>
                </div>
              )}

              {/* Difficulty */}
              {trip.difficulty && (
                <div
                  className={`trip-detail-page__difficulty ${getDifficultyClass(trip.difficulty)}`}
                >
                  {getDifficultyLabel(trip.difficulty)}
                </div>
              )}
            </div>
          </div>

          {/* Owner-only action buttons (T039) */}
          {isOwner && (
            <div className="trip-detail-page__actions">
              {/* Publish button (only for drafts) */}
              {trip.status === 'draft' && (
                <button
                  className="trip-detail-page__action-button trip-detail-page__action-button--publish"
                  onClick={handlePublish}
                  disabled={isPublishing}
                >
                  {isPublishing ? 'Publicando...' : 'Publicar'}
                </button>
              )}

              {/* Edit button - Phase 7 */}
              <Link
                to={`/trips/${trip.trip_id}/edit`}
                className="trip-detail-page__action-button trip-detail-page__action-button--edit"
              >
                Editar
              </Link>

              {/* Delete button */}
              <button
                className="trip-detail-page__action-button trip-detail-page__action-button--delete"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          )}
        </div>

        {/* Description */}
        <section className="trip-detail-page__section">
          <h2 className="trip-detail-page__section-title">Descripción</h2>
          <div
            className="trip-detail-page__description"
            dangerouslySetInnerHTML={{ __html: trip.description }}
          />
        </section>

        {/* Tags */}
        {trip.tags.length > 0 && (
          <section className="trip-detail-page__section">
            <h2 className="trip-detail-page__section-title">Etiquetas</h2>
            <div className="trip-detail-page__tags">
              {trip.tags.map((tag) => (
                <Link
                  key={tag.tag_id}
                  to={`/trips?tag=${encodeURIComponent(tag.name)}`}
                  className="trip-detail-page__tag"
                >
                  {tag.name}
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Photo Gallery */}
        {trip.photos.length > 0 && (
          <section className="trip-detail-page__section">
            <h2 className="trip-detail-page__section-title">Galería de Fotos</h2>
            <TripGallery photos={trip.photos} tripTitle={trip.title} />
          </section>
        )}

        {/* Map (T038: conditional rendering only if locations exist) */}
        {hasValidLocations && (
          <section className="trip-detail-page__section">
            <h2 className="trip-detail-page__section-title">Ruta y Ubicaciones</h2>
            <Suspense
              fallback={
                <div className="trip-detail-page__map-loading">Cargando mapa...</div>
              }
            >
              <TripMap locations={trip.locations} tripTitle={trip.title} />
            </Suspense>
          </section>
        )}

        {/* Back to list button */}
        <div className="trip-detail-page__footer">
          <Link to="/trips" className="trip-detail-page__back-button">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Volver a Mis Viajes
          </Link>
        </div>
      </div>

      {/* Delete Confirmation Dialog - Phase 8 */}
      {showDeleteConfirm && (
        <div className="trip-detail-page__delete-dialog-overlay" onClick={cancelDelete}>
          <div
            className="trip-detail-page__delete-dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="trip-detail-page__delete-dialog-icon">
              <svg
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h3 className="trip-detail-page__delete-dialog-title">
              ¿Eliminar viaje?
            </h3>
            <p className="trip-detail-page__delete-dialog-text">
              ¿Estás seguro de que quieres eliminar este viaje? Esta acción es permanente y
              eliminará el viaje junto con todas sus fotos. No se puede deshacer.
            </p>
            <div className="trip-detail-page__delete-dialog-actions">
              <button
                type="button"
                className="trip-detail-page__delete-dialog-button trip-detail-page__delete-dialog-button--cancel"
                onClick={cancelDelete}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="trip-detail-page__delete-dialog-button trip-detail-page__delete-dialog-button--confirm"
                onClick={confirmDelete}
                disabled={isDeleting}
              >
                {isDeleting ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
