/**
 * useTripForm Hook
 *
 * Custom hook for managing trip creation/editing wizard state.
 * Handles form data persistence, validation, and submission.
 *
 * Features:
 * - Wizard step navigation with validation
 * - Form data persistence (localStorage)
 * - Draft vs publish submission
 * - Error handling and success feedback
 *
 * Used in:
 * - TripCreatePage (new trip)
 * - TripEditPage (edit existing trip)
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTrip, updateTrip, publishTrip } from '../services/tripService';
import { uploadTripPhoto } from '../services/tripPhotoService';
import { TripCreateInput, Trip } from '../types/trip';
import toast from 'react-hot-toast';
import type { PhotoPreview } from '../components/trips/TripForm/Step3Photos';

interface UseTripFormOptions {
  /** Trip ID (for editing existing trip) */
  tripId?: string;

  /** Initial form data */
  initialData?: Partial<TripCreateInput>;

  /** Is edit mode? */
  isEditMode?: boolean;

  /** Enable localStorage persistence? */
  enablePersistence?: boolean;
}

interface UseTripFormReturn {
  /** Submit form data (create or update trip) */
  handleSubmit: (data: TripCreateInput, isDraft: boolean, photos?: PhotoPreview[]) => Promise<void>;

  /** Is form submitting? */
  isSubmitting: boolean;

  /** Get persisted form data from localStorage */
  getPersistedData: () => Partial<TripCreateInput> | null;

  /** Save form data to localStorage */
  persistFormData: (data: Partial<TripCreateInput>) => void;

  /** Clear persisted form data */
  clearPersistedData: () => void;
}

const STORAGE_KEY = 'trip_form_draft';

export const useTripForm = ({
  tripId,
  initialData,
  isEditMode = false,
  enablePersistence = true,
}: UseTripFormOptions = {}): UseTripFormReturn => {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Get persisted form data from localStorage
   */
  const getPersistedData = useCallback((): Partial<TripCreateInput> | null => {
    if (!enablePersistence || isEditMode) return null;

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return null;

      const data = JSON.parse(stored);

      // Validate timestamp (discard if older than 7 days)
      const timestamp = data._timestamp;
      if (!timestamp || Date.now() - timestamp > 7 * 24 * 60 * 60 * 1000) {
        localStorage.removeItem(STORAGE_KEY);
        return null;
      }

      // Remove metadata
      delete data._timestamp;

      return data;
    } catch (error) {
      console.error('Error reading persisted form data:', error);
      return null;
    }
  }, [enablePersistence, isEditMode]);

  /**
   * Save form data to localStorage
   */
  const persistFormData = useCallback(
    (data: Partial<TripCreateInput>) => {
      if (!enablePersistence || isEditMode) return;

      try {
        const dataWithTimestamp = {
          ...data,
          _timestamp: Date.now(),
        };

        localStorage.setItem(STORAGE_KEY, JSON.stringify(dataWithTimestamp));
      } catch (error) {
        console.error('Error persisting form data:', error);
      }
    },
    [enablePersistence, isEditMode]
  );

  /**
   * Clear persisted form data
   */
  const clearPersistedData = useCallback(() => {
    if (!enablePersistence) return;

    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing persisted data:', error);
    }
  }, [enablePersistence]);

  /**
   * Submit form (create new trip or update existing)
   */
  const handleSubmit = useCallback(
    async (data: TripCreateInput, isDraft: boolean, photos?: PhotoPreview[]) => {
      setIsSubmitting(true);

      try {
        let trip: Trip;

        if (isEditMode && tripId) {
          // Update existing trip
          trip = await updateTrip(tripId, data);

          // If publishing from draft, call publish endpoint
          if (!isDraft && trip.status === 'DRAFT') {
            trip = await publishTrip(tripId);
          }

          toast.success('Viaje actualizado correctamente', {
            duration: 3000,
            position: 'top-center',
          });
        } else {
          // Create new trip
          trip = await createTrip(data);

          // Upload photos if provided (only for published trips or if explicitly requested)
          if (photos && photos.length > 0 && !isDraft) {
            toast.loading(`Subiendo ${photos.length} foto(s)...`, { id: 'photo-upload' });

            try {
              let uploadedCount = 0;

              for (const photo of photos) {
                try {
                  await uploadTripPhoto(trip.trip_id, photo.file);
                  uploadedCount++;
                } catch (error) {
                  console.error(`Error uploading ${photo.file.name}:`, error);
                }
              }

              toast.success(`${uploadedCount} de ${photos.length} foto(s) subida(s)`, {
                id: 'photo-upload',
                duration: 3000
              });
            } catch (error) {
              toast.error('Error al subir algunas fotos', { id: 'photo-upload' });
            }
          }

          // If publishing, call publish endpoint
          if (!isDraft) {
            trip = await publishTrip(trip.trip_id);
          }

          toast.success(
            isDraft
              ? 'Borrador guardado correctamente'
              : 'Viaje publicado correctamente',
            {
              duration: 3000,
              position: 'top-center',
            }
          );

          // Clear persisted data on successful creation
          clearPersistedData();
        }

        // Navigate to trip detail or trips list
        navigate(`/trips/${trip.trip_id}`);
      } catch (error: any) {
        console.error('Error submitting trip:', error);

        const errorMessage =
          error.response?.data?.error?.message ||
          (isEditMode
            ? 'Error al actualizar el viaje. Intenta nuevamente.'
            : isDraft
            ? 'Error al guardar el borrador. Intenta nuevamente.'
            : 'Error al publicar el viaje. Intenta nuevamente.');

        toast.error(errorMessage, {
          duration: 5000,
          position: 'top-center',
        });

        throw error; // Re-throw for component to handle if needed
      } finally {
        setIsSubmitting(false);
      }
    },
    [tripId, isEditMode, navigate, clearPersistedData]
  );

  /**
   * Auto-restore persisted data on mount (for new trips only)
   */
  useEffect(() => {
    if (!isEditMode && enablePersistence) {
      const persisted = getPersistedData();

      if (persisted) {
        const shouldRestore = window.confirm(
          'Encontramos un borrador guardado. ¿Quieres continuar desde donde lo dejaste?'
        );

        if (!shouldRestore) {
          clearPersistedData();
        }
      }
    }
  }, []); // Run only on mount

  return {
    handleSubmit,
    isSubmitting,
    getPersistedData,
    persistFormData,
    clearPersistedData,
  };
};
