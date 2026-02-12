/**
 * PhotoManager Component
 *
 * Simplified photo management for GPX trip editing.
 * Features:
 * - Drag-drop upload with react-dropzone
 * - Max 6 photos (hardcoded)
 * - Concurrent uploads with progress bars
 * - Drag-to-reorder with "Imagen principal" badge on first photo
 * - Delete with confirmation
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-hot-toast';
import { TripPhoto } from '../../types/trip';
import { uploadTripPhoto, deleteTripPhoto, reorderTripPhotos } from '../../services/tripService';
import { getPhotoUrl } from '../../utils/tripHelpers';
import './PhotoManager.css';

interface PhotoManagerProps {
  tripId: string;
  existingPhotos: TripPhoto[];
  onPhotosChange: (photos: TripPhoto[]) => void;
}

interface PhotoUploadState {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  error?: string;
  photoId?: string;
}

const MAX_PHOTOS = 6;
const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_CONCURRENT_UPLOADS = 3;

export const PhotoManager: React.FC<PhotoManagerProps> = ({
  tripId,
  existingPhotos,
  onPhotosChange,
}) => {
  const [uploadQueue, setUploadQueue] = useState<PhotoUploadState[]>([]);
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const photos = existingPhotos;
  const photoCount = photos.length + uploadQueue.filter((u) => u.status === 'success').length;

  /**
   * Upload a single file with progress tracking
   */
  const uploadFile = useCallback(
    async (file: File, index: number) => {
      try {
        // Update state to uploading
        setUploadQueue((prev) =>
          prev.map((item, i) =>
            i === index ? { ...item, status: 'uploading' as const, progress: 0 } : item
          )
        );

        // Simulate progress (uploadTripPhoto doesn't support onUploadProgress yet)
        const progressInterval = setInterval(() => {
          setUploadQueue((prev) =>
            prev.map((item, i) => {
              if (i === index && item.status === 'uploading' && item.progress < 90) {
                return { ...item, progress: item.progress + 10 };
              }
              return item;
            })
          );
        }, 200);

        // Upload to backend
        const response = await uploadTripPhoto(tripId, file);

        clearInterval(progressInterval);

        // Mark as success
        setUploadQueue((prev) =>
          prev.map((item, i) =>
            i === index
              ? { ...item, status: 'success' as const, progress: 100, photoId: (response as any).id }
              : item
          )
        );

        // Add to photos list
        onPhotosChange([...photos, response]);
      } catch (error: any) {
        const errorMessage =
          error.response?.data?.error?.message || 'Error al subir la foto';

        setUploadQueue((prev) =>
          prev.map((item, i) =>
            i === index
              ? { ...item, status: 'error' as const, progress: 0, error: errorMessage }
              : item
          )
        );

        toast.error(errorMessage);
      }
    },
    [tripId, photos, onPhotosChange]
  );

  /**
   * Process upload queue with concurrency limit
   */
  const processUploadQueue = useCallback(
    async (newQueue: PhotoUploadState[]) => {
      const uploading: Promise<void>[] = [];

      for (let i = 0; i < newQueue.length; i++) {
        if (uploading.length >= MAX_CONCURRENT_UPLOADS) {
          await Promise.race(uploading);
        }

        const uploadPromise = uploadFile(newQueue[i].file, i).finally(() => {
          uploading.splice(uploading.indexOf(uploadPromise), 1);
        });

        uploading.push(uploadPromise);
      }

      await Promise.all(uploading);
    },
    [uploadFile]
  );

  /**
   * Handle file drop
   */
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Check total limit
      const availableSlots = MAX_PHOTOS - photoCount;
      if (availableSlots <= 0) {
        toast.error(`Has alcanzado el límite de ${MAX_PHOTOS} fotos`);
        return;
      }

      // Limit to available slots
      const filesToUpload = acceptedFiles.slice(0, availableSlots);

      if (filesToUpload.length < acceptedFiles.length) {
        toast.error(
          `Solo puedes subir ${availableSlots} foto(s) más. Límite: ${MAX_PHOTOS} fotos`
        );
      }

      // Validate files
      const validFiles: File[] = [];
      for (const file of filesToUpload) {
        // Check type
        if (!ALLOWED_TYPES.includes(file.type)) {
          toast.error(`${file.name}: Formato no soportado. Usa JPG, PNG o WEBP`);
          continue;
        }

        // Check size
        if (file.size > MAX_FILE_SIZE_BYTES) {
          toast.error(`${file.name}: Tamaño máximo ${MAX_FILE_SIZE_MB}MB`);
          continue;
        }

        validFiles.push(file);
      }

      if (validFiles.length === 0) {
        return;
      }

      // Create upload queue
      const newQueue: PhotoUploadState[] = validFiles.map((file) => ({
        file,
        progress: 0,
        status: 'uploading' as const,
      }));

      setUploadQueue(newQueue);

      // Start uploading
      processUploadQueue(newQueue);
    },
    [photoCount, processUploadQueue]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
    },
    maxSize: MAX_FILE_SIZE_BYTES,
    disabled: photoCount >= MAX_PHOTOS,
  });

  /**
   * Handle photo deletion
   */
  const handleDelete = useCallback(
    async (photoId: string) => {
      try {
        await deleteTripPhoto(tripId, photoId);
        onPhotosChange(photos.filter((p) => ((p as any).id || p.photo_id) !== photoId));
        toast.success('Foto eliminada correctamente');
      } catch (error: any) {
        toast.error(error.response?.data?.error?.message || 'Error al eliminar foto');
      } finally {
        setDeleteConfirmId(null);
      }
    },
    [tripId, photos, onPhotosChange]
  );

  /**
   * Handle drag start
   */
  const handleDragStart = (index: number) => {
    setDraggedIndex(index);
  };

  /**
   * Handle drag over
   */
  const handleDragOver = (index: number) => {
    if (draggedIndex !== null && draggedIndex !== index) {
      setDragOverIndex(index);
    }
  };

  /**
   * Handle drop (reorder)
   */
  const handleDrop = useCallback(
    async (targetIndex: number) => {
      if (draggedIndex === null || draggedIndex === targetIndex) {
        setDraggedIndex(null);
        setDragOverIndex(null);
        return;
      }

      // Reorder array
      const reordered = [...photos];
      const [removed] = reordered.splice(draggedIndex, 1);
      reordered.splice(targetIndex, 0, removed);

      // Update display_order
      const updated = reordered.map((photo, index) => ({
        ...photo,
        display_order: index,
      }));

      // Optimistic update
      onPhotosChange(updated);

      try {
        // Persist to backend
        // Note: Backend returns 'id' field (via serialization_alias), not 'photo_id'
        const photoIds = updated.map((p) => (p as any).id || p.photo_id);
        console.log('[PhotoManager] Reordering photos:', photoIds);
        await reorderTripPhotos(tripId, photoIds);
      } catch (error: any) {
        // Revert on error
        onPhotosChange(photos);
        toast.error(error.response?.data?.error?.message || 'Error al reordenar fotos');
      } finally {
        setDraggedIndex(null);
        setDragOverIndex(null);
      }
    },
    [draggedIndex, photos, tripId, onPhotosChange]
  );

  return (
    <div className="photo-manager">
      <div className="photo-manager__header">
        <h3 className="photo-manager__title">Fotos del Viaje</h3>
        <span className="photo-manager__counter">
          {photoCount} / {MAX_PHOTOS} fotos
        </span>
      </div>

      {/* Warning for trips with >6 photos */}
      {photos.length > MAX_PHOTOS && (
        <div className="photo-manager__warning">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <p>
            Este viaje tiene {photos.length} fotos (límite actual: {MAX_PHOTOS}). No podrás subir
            más hasta eliminar algunas.
          </p>
        </div>
      )}

      {/* Photo Grid */}
      <div className="photo-manager__grid">
        {photos.map((photo, index) => (
          <div
            key={(photo as any).id || photo.photo_id}
            className={`photo-manager__item ${
              draggedIndex === index ? 'photo-manager__item--dragging' : ''
            } ${dragOverIndex === index ? 'photo-manager__item--drag-over' : ''}`}
            draggable
            onDragStart={() => handleDragStart(index)}
            onDragOver={(e) => {
              e.preventDefault();
              handleDragOver(index);
            }}
            onDrop={() => handleDrop(index)}
            onDragEnd={() => {
              setDraggedIndex(null);
              setDragOverIndex(null);
            }}
          >
            <img
              src={getPhotoUrl(photo.thumbnail_url)}
              alt={photo.caption || `Foto ${index + 1}`}
              className="photo-manager__thumbnail"
            />

            {/* Primary Badge */}
            {index === 0 && (
              <div className="photo-manager__badge">
                <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                Imagen principal
              </div>
            )}

            {/* Delete Button */}
            <button
              type="button"
              className="photo-manager__delete"
              onClick={() => setDeleteConfirmId((photo as any).id || photo.photo_id)}
              aria-label={`Eliminar foto ${index + 1}`}
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fillRule="evenodd"
                  d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        ))}

        {/* Upload Queue */}
        {uploadQueue.map((upload, index) => (
          <div key={index} className="photo-manager__item photo-manager__item--uploading">
            <div className="photo-manager__upload-progress">
              <p className="photo-manager__upload-filename">{upload.file.name}</p>
              {upload.status === 'uploading' && (
                <>
                  <div className="photo-manager__progress-bar">
                    <div
                      className="photo-manager__progress-fill"
                      style={{ width: `${upload.progress}%` }}
                    />
                  </div>
                  <p className="photo-manager__upload-status">{upload.progress}%</p>
                </>
              )}
              {upload.status === 'error' && (
                <p className="photo-manager__upload-error">{upload.error}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Dropzone */}
      {photoCount < MAX_PHOTOS && (
        <div
          {...getRootProps()}
          className={`photo-manager__dropzone ${
            isDragActive ? 'photo-manager__dropzone--active' : ''
          }`}
        >
          <input {...getInputProps()} aria-label="Subir foto" />
          <svg
            className="photo-manager__dropzone-icon"
            width="48"
            height="48"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
              clipRule="evenodd"
            />
          </svg>
          <p className="photo-manager__dropzone-text">
            {isDragActive
              ? 'Suelta las fotos aquí'
              : 'Arrastra fotos aquí o haz clic para seleccionar'}
          </p>
          <p className="photo-manager__dropzone-hint">
            Máximo {MAX_PHOTOS} fotos · {MAX_FILE_SIZE_MB}MB por foto · JPG, PNG, WEBP
          </p>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteConfirmId && (
        <div className="photo-manager__dialog-overlay" onClick={() => setDeleteConfirmId(null)}>
          <div className="photo-manager__dialog" onClick={(e) => e.stopPropagation()}>
            <h3 className="photo-manager__dialog-title">¿Eliminar foto?</h3>
            <p className="photo-manager__dialog-message">
              Esta acción es permanente y no se puede deshacer.
            </p>
            <div className="photo-manager__dialog-actions">
              <button
                type="button"
                onClick={() => setDeleteConfirmId(null)}
                className="photo-manager__dialog-button photo-manager__dialog-button--cancel"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={() => handleDelete(deleteConfirmId)}
                className="photo-manager__dialog-button photo-manager__dialog-button--delete"
              >
                Eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
