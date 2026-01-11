/**
 * TripEditPage Component
 *
 * Page for editing an existing trip using the multi-step wizard.
 * Fetches trip data, pre-fills the form, and allows owners to update trip details.
 *
 * Route: /trips/:tripId/edit
 *
 * Features:
 * - Loads existing trip data and pre-fills form
 * - Uses TripFormWizard in edit mode
 * - Owner-only access (redirects if not owner)
 * - Optimistic locking to prevent concurrent edits
 * - Updates trip via PUT /trips/{id}
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TripFormWizard } from '../components/trips/TripForm/TripFormWizard';
import { useTripForm } from '../hooks/useTripForm';
import { getTripById } from '../services/tripService';
import { Trip, TripCreateInput } from '../types/trip';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';
import './TripEditPage.css';

export const TripEditPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { handleSubmit, isSubmitting } = useTripForm({
    tripId,
    isEditMode: true,
  });

  /**
   * Load existing trip data
   */
  useEffect(() => {
    const loadTrip = async () => {
      if (!tripId) {
        setError('ID de viaje no válido');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        const tripData = await getTripById(tripId);

        // Check ownership - compare user_id with current user's user_id
        if (tripData.user_id !== user?.user_id) {
          toast.error('No tienes permiso para editar este viaje');
          navigate(`/trips/${tripId}`);
          return;
        }

        setTrip(tripData);
        setError(null);
      } catch (err: any) {
        console.error('Error loading trip:', err);
        const errorMessage =
          err.response?.data?.error?.message ||
          'Error al cargar el viaje. Intenta nuevamente.';
        setError(errorMessage);
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    loadTrip();
  }, [tripId, user, navigate]);

  /**
   * Convert Trip to TripCreateInput for form initialization
   */
  const getInitialFormData = (): Partial<TripCreateInput> | undefined => {
    if (!trip) return undefined;

    return {
      title: trip.title,
      description: trip.description || '',
      start_date: trip.start_date,
      end_date: trip.end_date || undefined,
      distance_km: trip.distance_km || undefined,
      difficulty: trip.difficulty || undefined,
      tags: trip.tags?.map((tag) => tag.name) || [],
    };
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="trip-edit-page">
        <div className="trip-edit-page__loading">
          <div className="trip-edit-page__loading-spinner">
            <div className="spinner"></div>
          </div>
          <p className="trip-edit-page__loading-text">Cargando viaje...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !trip) {
    return (
      <div className="trip-edit-page">
        <div className="trip-edit-page__error">
          <svg
            className="trip-edit-page__error-icon"
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
          <h2 className="trip-edit-page__error-title">Error al cargar viaje</h2>
          <p className="trip-edit-page__error-text">
            {error || 'El viaje no existe o no tienes permiso para editarlo.'}
          </p>
          <button
            type="button"
            className="trip-edit-page__error-button"
            onClick={() => navigate('/trips')}
          >
            Volver a viajes
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="trip-edit-page">
      <div className="trip-edit-page__header">
        <div className="trip-edit-page__header-content">
          <h1 className="trip-edit-page__title">Editar Viaje</h1>
          <p className="trip-edit-page__subtitle">
            Actualiza la información de tu viaje. Los cambios se guardarán inmediatamente.
          </p>
        </div>
      </div>

      <div className="trip-edit-page__main">
        {/* Debug: Log trip photos */}
        {console.log('TripEditPage - trip.photos:', trip.photos)}
        {console.log('TripEditPage - passing existingPhotos:', trip.photos || [])}
        <TripFormWizard
          tripId={tripId}
          initialData={getInitialFormData()}
          existingPhotos={trip.photos || []}
          onSubmit={handleSubmit}
          isEditMode={true}
        />
      </div>
    </div>
  );
};
