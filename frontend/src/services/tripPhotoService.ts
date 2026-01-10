/**
 * Trip Photo Service
 *
 * API service for managing trip photos in the Travel Diary feature.
 * Based on backend API contracts from Feature 002 (Travel Diary Backend).
 */

import { api } from './api';
import { TripPhoto } from '../types/trip';

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Standard API response wrapper
 */
interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: null | {
    code: string;
    message: string;
    field?: string;
  };
}

/**
 * Upload progress callback
 */
export type UploadProgressCallback = (progress: number) => void;

// ============================================================================
// Photo Upload Operations
// ============================================================================

/**
 * Upload photo to trip gallery
 *
 * Uploads a single photo with optional caption.
 * Supports upload progress tracking via callback.
 *
 * @param tripId - UUID of the trip
 * @param file - Image file (JPG/PNG, max 10MB)
 * @param caption - Optional photo caption (max 500 characters)
 * @param onProgress - Optional callback for upload progress (0-100)
 * @returns Uploaded photo with assigned photo_id and URLs
 *
 * @throws 400 if file is invalid or photo limit exceeded (max 20 per trip)
 * @throws 403 if not the trip owner
 * @throws 404 if trip not found
 *
 * @example
 * // Basic upload
 * const photo = await uploadTripPhoto(tripId, file);
 *
 * // With caption
 * const photo = await uploadTripPhoto(tripId, file, 'Vista desde el viaducto');
 *
 * // With progress tracking
 * const photo = await uploadTripPhoto(
 *   tripId,
 *   file,
 *   'Sunset over the valley',
 *   (progress) => {
 *     console.log(`Upload progress: ${progress}%`);
 *     setUploadProgress(progress);
 *   }
 * );
 */
export const uploadTripPhoto = async (
  tripId: string,
  file: File,
  caption?: string,
  onProgress?: UploadProgressCallback
): Promise<TripPhoto> => {
  // Create FormData for multipart/form-data upload
  const formData = new FormData();
  formData.append('photo', file);
  if (caption) {
    formData.append('caption', caption);
  }

  // Upload with progress tracking
  const response = await api.post<ApiResponse<{ photo: TripPhoto }>>(
    `/trips/${tripId}/photos`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    }
  );

  return response.data.data.photo;
};

/**
 * Upload multiple photos in chunks
 *
 * Uploads photos in sequential chunks to avoid overwhelming the server.
 * Recommended for bulk uploads (Step 3: Photo Upload).
 *
 * @param tripId - UUID of the trip
 * @param files - Array of image files to upload
 * @param chunkSize - Number of photos to upload in parallel (default: 3)
 * @param onProgress - Optional callback for overall progress (0-100)
 * @returns Array of uploaded photos
 *
 * @example
 * const photos = await uploadTripPhotosChunked(
 *   tripId,
 *   selectedFiles,
 *   3, // Upload 3 at a time
 *   (progress) => {
 *     setOverallProgress(progress);
 *   }
 * );
 */
export const uploadTripPhotosChunked = async (
  tripId: string,
  files: File[],
  chunkSize: number = 3,
  onProgress?: UploadProgressCallback
): Promise<TripPhoto[]> => {
  const uploadedPhotos: TripPhoto[] = [];
  let completedCount = 0;

  // Process files in chunks
  for (let i = 0; i < files.length; i += chunkSize) {
    const chunk = files.slice(i, i + chunkSize);

    // Upload chunk in parallel
    const chunkResults = await Promise.allSettled(
      chunk.map((file) => uploadTripPhoto(tripId, file))
    );

    // Collect successful uploads
    for (const result of chunkResults) {
      if (result.status === 'fulfilled') {
        uploadedPhotos.push(result.value);
      } else {
        console.error('Photo upload failed:', result.reason);
      }
    }

    // Update progress
    completedCount += chunk.length;
    if (onProgress) {
      const progress = Math.round((completedCount * 100) / files.length);
      onProgress(progress);
    }
  }

  return uploadedPhotos;
};

// ============================================================================
// Photo Management Operations
// ============================================================================

/**
 * Delete photo from trip gallery
 *
 * Permanently deletes photo and associated files from storage.
 *
 * @param tripId - UUID of the trip
 * @param photoId - UUID of the photo to delete
 *
 * @throws 403 if not the trip owner
 * @throws 404 if photo or trip not found
 *
 * @example
 * await deleteTripPhoto(tripId, photoId);
 * toast.success('Foto eliminada correctamente');
 */
export const deleteTripPhoto = async (tripId: string, photoId: string): Promise<void> => {
  await api.delete(`/trips/${tripId}/photos/${photoId}`);
};

/**
 * Reorder photos in trip gallery
 *
 * Updates the display_order of photos based on user drag-and-drop.
 *
 * @param tripId - UUID of the trip
 * @param photoOrder - Array of photo IDs in desired order
 *
 * @throws 403 if not the trip owner
 * @throws 404 if trip not found
 *
 * @example
 * // User drags photo 3 to position 1
 * const newOrder = [photoId3, photoId1, photoId2];
 * await reorderTripPhotos(tripId, newOrder);
 */
export const reorderTripPhotos = async (
  tripId: string,
  photoOrder: string[]
): Promise<void> => {
  await api.put(`/trips/${tripId}/photos/reorder`, {
    photo_order: photoOrder,
  });
};

/**
 * Update photo caption
 *
 * Updates the caption of an existing photo.
 * This is a convenience wrapper around updateTrip (no dedicated endpoint).
 *
 * @param tripId - UUID of the trip
 * @param photoId - UUID of the photo to update
 * @param caption - New caption (max 500 characters)
 *
 * Note: This requires fetching the trip, modifying the photo array, and updating.
 * For MVP, users should delete and re-upload photos to change captions.
 *
 * @example
 * // Not implemented in MVP - delete and re-upload instead
 * await deleteTripPhoto(tripId, photoId);
 * await uploadTripPhoto(tripId, newFile, newCaption);
 */
export const updatePhotoCaption = async (
  tripId: string,
  photoId: string,
  caption: string
): Promise<void> => {
  // TODO: Implement in future if backend adds dedicated endpoint
  // For MVP: delete and re-upload photo with new caption
  throw new Error('updatePhotoCaption not implemented - delete and re-upload photo instead');
};

// ============================================================================
// Photo Validation Helpers
// ============================================================================

/**
 * Validate photo file before upload
 *
 * @param file - File to validate
 * @returns Object with valid flag and error message if invalid
 *
 * @example
 * const validation = validatePhotoFile(file);
 * if (!validation.valid) {
 *   toast.error(validation.error);
 *   return;
 * }
 * await uploadTripPhoto(tripId, file);
 */
export const validatePhotoFile = (file: File): { valid: boolean; error?: string } => {
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Solo se permiten imágenes JPG y PNG',
    };
  }

  // Check file size (max 10MB)
  const maxSizeBytes = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSizeBytes) {
    return {
      valid: false,
      error: 'El tamaño máximo permitido es 10MB',
    };
  }

  return { valid: true };
};

/**
 * Check if trip has reached photo limit
 *
 * @param currentPhotoCount - Current number of photos in trip
 * @returns True if photo limit (20) reached
 *
 * @example
 * if (isPhotoLimitReached(trip.photos.length)) {
 *   toast.error('Máximo 20 fotos permitidas por viaje');
 *   return;
 * }
 */
export const isPhotoLimitReached = (currentPhotoCount: number): boolean => {
  const MAX_PHOTOS_PER_TRIP = 20;
  return currentPhotoCount >= MAX_PHOTOS_PER_TRIP;
};

/**
 * Calculate remaining photo slots
 *
 * @param currentPhotoCount - Current number of photos in trip
 * @returns Number of photos that can still be uploaded
 *
 * @example
 * const remaining = getRemainingPhotoSlots(trip.photos.length);
 * console.log(`You can upload ${remaining} more photos`);
 */
export const getRemainingPhotoSlots = (currentPhotoCount: number): number => {
  const MAX_PHOTOS_PER_TRIP = 20;
  return Math.max(0, MAX_PHOTOS_PER_TRIP - currentPhotoCount);
};
