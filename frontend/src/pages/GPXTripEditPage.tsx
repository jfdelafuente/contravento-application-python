/**
 * GPXTripEditPage Component
 *
 * Simplified edit page for trips with GPX files.
 * Features:
 * - Form 1: Edit title, description, privacy (with Cancelar/Guardar buttons)
 * - Form 2: PhotoManager for uploading/managing up to 6 photos
 * - Final buttons: Cancelar and Actualizar (navigate to detail)
 */

import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { getTripById, updateTrip } from '../services/tripService';
import { Trip, TripPhoto } from '../types/trip';
import { PhotoManager } from '../components/trips/PhotoManager';
import './GPXTripEditPage.css';

export const GPXTripEditPage: React.FC = () => {
  const { tripId } = useParams<{ tripId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [trip, setTrip] = useState<Trip | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Form 1 state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isPrivate, setIsPrivate] = useState(false);

  // Form 2 state (photos managed by PhotoManager)
  const [photos, setPhotos] = useState<TripPhoto[]>([]);

  /**
   * Load trip data on mount
   */
  useEffect(() => {
    const fetchTrip = async () => {
      if (!tripId) {
        navigate('/trips');
        return;
      }

      try {
        setIsLoading(true);
        const tripData = await getTripById(tripId);

        // Verify it's a GPX trip
        if (!tripData.gpx_file) {
          toast.error('Este viaje no tiene archivo GPX. Usa el editor estándar.');
          navigate(`/trips/${tripId}/edit`);
          return;
        }

        setTrip(tripData);
        setTitle(tripData.title);
        setDescription(tripData.description);
        setIsPrivate(tripData.is_private);
        setPhotos(tripData.photos);
      } catch (error: any) {
        toast.error(error.response?.data?.error?.message || 'Error al cargar el viaje');
        navigate('/trips');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTrip();
  }, [tripId, navigate]);

  /**
   * Check ownership
   */
  useEffect(() => {
    if (trip && user && trip.user_id !== user.user_id) {
      toast.error('No tienes permiso para editar este viaje');
      navigate(`/trips/${tripId}`);
    }
  }, [trip, user, tripId, navigate]);

  /**
   * Save Form 1 metadata
   */
  const handleSaveMetadata = useCallback(async () => {
    if (!trip || !tripId) return;

    // Validate title
    if (title.trim().length < 1 || title.length > 200) {
      toast.error('El título debe tener entre 1 y 200 caracteres');
      return;
    }

    // Validate description (min 50 chars for published trips)
    if (trip.status === 'published' && description.trim().length < 50) {
      toast.error('La descripción debe tener al menos 50 caracteres para viajes publicados');
      return;
    }

    try {
      setIsSaving(true);

      await updateTrip(tripId, {
        title: title.trim(),
        description: description.trim(),
        is_private: isPrivate,
      });

      toast.success('Información actualizada correctamente');
    } catch (error: any) {
      // Handle optimistic locking conflicts (409)
      if (error.response?.status === 409) {
        toast.error(
          'El viaje fue modificado por otra sesión. Recarga la página para ver los cambios más recientes.',
          { duration: 6000 }
        );
      } else {
        toast.error(error.response?.data?.error?.message || 'Error al guardar');
      }
    } finally {
      setIsSaving(false);
    }
  }, [trip, tripId, title, description, isPrivate]);

  /**
   * Handle final update (navigate to detail)
   */
  const handleUpdate = useCallback(() => {
    // All changes are auto-saved, just navigate
    navigate(`/trips/${tripId}`);
  }, [tripId, navigate]);

  /**
   * Handle cancel
   */
  const handleCancel = useCallback(() => {
    navigate(`/trips/${tripId}`);
  }, [tripId, navigate]);

  if (isLoading) {
    return (
      <div className="gpx-trip-edit-page">
        <div className="gpx-trip-edit-page__loading">
          <div className="spinner" />
          <p>Cargando viaje...</p>
        </div>
      </div>
    );
  }

  if (!trip) {
    return null;
  }

  return (
    <div className="gpx-trip-edit-page">
      <div className="gpx-trip-edit-page__container">
        <h1 className="gpx-trip-edit-page__heading">Editar Viaje con GPX</h1>

        {/* Form 1: Información del Viaje */}
        <section className="gpx-trip-edit-page__section">
          <h2 className="gpx-trip-edit-page__section-title">Información del Viaje</h2>

          <div className="gpx-trip-edit-page__form">
            {/* Title */}
            <div className="gpx-trip-edit-page__field">
              <label htmlFor="title" className="gpx-trip-edit-page__label">
                Título
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="gpx-trip-edit-page__input"
                maxLength={200}
                required
                aria-describedby="title-hint"
              />
              <p id="title-hint" className="gpx-trip-edit-page__hint">
                {title.length} / 200 caracteres
              </p>
            </div>

            {/* Description */}
            <div className="gpx-trip-edit-page__field">
              <label htmlFor="description" className="gpx-trip-edit-page__label">
                Descripción
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="gpx-trip-edit-page__textarea"
                rows={6}
                maxLength={50000}
                required
                aria-describedby="description-hint"
              />
              <p id="description-hint" className="gpx-trip-edit-page__hint">
                {description.length} caracteres
                {trip.status === 'published' && ' (mínimo 50 para viajes publicados)'}
              </p>
            </div>

            {/* Privacy */}
            <div className="gpx-trip-edit-page__field">
              <label htmlFor="privacy" className="gpx-trip-edit-page__label">
                Privacidad
              </label>
              <select
                id="privacy"
                value={isPrivate ? 'private' : 'public'}
                onChange={(e) => setIsPrivate(e.target.value === 'private')}
                className="gpx-trip-edit-page__select"
                aria-label="Privacidad del viaje"
              >
                <option value="public">Público</option>
                <option value="private">Privado</option>
              </select>
              <p className="gpx-trip-edit-page__hint">
                {isPrivate
                  ? 'Solo tú puedes ver este viaje'
                  : 'Visible en el feed público'}
              </p>
            </div>

            {/* Form 1 Buttons */}
            <div className="gpx-trip-edit-page__form-actions">
              <button
                type="button"
                onClick={handleCancel}
                className="gpx-trip-edit-page__button gpx-trip-edit-page__button--secondary"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleSaveMetadata}
                disabled={isSaving}
                className="gpx-trip-edit-page__button gpx-trip-edit-page__button--primary"
              >
                {isSaving ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </section>

        {/* Form 2: Fotos del Viaje */}
        <section className="gpx-trip-edit-page__section">
          <PhotoManager tripId={tripId!} existingPhotos={photos} onPhotosChange={setPhotos} />
        </section>

        {/* Final Buttons */}
        <div className="gpx-trip-edit-page__final-actions">
          <button
            type="button"
            onClick={handleCancel}
            className="gpx-trip-edit-page__button gpx-trip-edit-page__button--secondary"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleUpdate}
            className="gpx-trip-edit-page__button gpx-trip-edit-page__button--primary"
          >
            Actualizar
          </button>
        </div>
      </div>
    </div>
  );
};
