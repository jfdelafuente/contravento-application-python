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
import { uploadTripPhoto, deleteTripPhoto } from '../services/tripPhotoService';
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
  initialData: _initialData,
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

        // Sanitize data: convert empty strings to null for optional fields
        const sanitizedData: TripCreateInput = {
          ...data,
          difficulty: data.difficulty || null,
          distance_km: !data.distance_km || isNaN(data.distance_km as any) ? null : data.distance_km,
          end_date: data.end_date === '' ? null : data.end_date,
        };

        if (isEditMode && tripId) {
          // Update existing trip
          try {
            trip = await updateTrip(tripId, sanitizedData);

            // Handle photo deletions (from photosToDelete)
            const photosToDelete = (data as any).photosToDelete as string[] | undefined;
            if (photosToDelete && photosToDelete.length > 0) {
              toast.loading(`Eliminando ${photosToDelete.length} foto(s)...`, { id: 'photo-delete' });

              try {
                let deletedCount = 0;

                for (const photoId of photosToDelete) {
                  try {
                    await deleteTripPhoto(tripId, photoId);
                    deletedCount++;
                  } catch (error) {
                    console.error(`Error deleting photo ${photoId}:`, error);
                  }
                }

                toast.success(`${deletedCount} foto(s) eliminada(s)`, {
                  id: 'photo-delete',
                  duration: 3000
                });
              } catch (error) {
                toast.error('Error al eliminar algunas fotos', { id: 'photo-delete' });
              }
            }

            // Handle new photo uploads
            if (photos && photos.length > 0) {
              toast.loading(`Subiendo ${photos.length} foto(s) nueva(s)...`, { id: 'photo-upload' });

              try {
                let uploadedCount = 0;

                for (const photo of photos) {
                  try {
                    await uploadTripPhoto(tripId, photo.file);
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

            // If publishing from draft, call publish endpoint
            if (!isDraft && trip.status === 'draft') {
              trip = await publishTrip(tripId);
            }

            toast.success('Viaje actualizado correctamente', {
              duration: 3000,
              position: 'top-center',
            });
          } catch (error: any) {
            // Handle optimistic locking conflict (409)
            if (error.response?.status === 409) {
              toast.error(
                'El viaje fue modificado por otra sesión. Recarga la página para ver los cambios más recientes.',
                {
                  duration: 6000,
                  position: 'top-center',
                }
              );
              throw error; // Re-throw to stop execution
            }
            throw error; // Re-throw other errors
          }
        } else {
          // Create new trip
          trip = await createTrip(sanitizedData);

          // Upload photos if provided (now also for drafts!)
          if (photos && photos.length > 0) {
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
