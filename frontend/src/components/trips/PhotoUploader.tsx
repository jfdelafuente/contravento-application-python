/**
 * PhotoUploader Component
 *
 * Drag-and-drop photo uploader with chunked upload (3 at a time).
 * Shows progress bars, thumbnails, and allows reordering/removal.
 *
 * Features:
 * - Drag-and-drop with react-dropzone
 * - File validation (MIME type, size max 10MB)
 * - Upload 3 photos concurrently with progress tracking
 * - Thumbnail preview grid
 * - Drag-to-reorder thumbnails
 * - Remove photos before/after upload
 * - Max 20 photos per trip
 *
 * Used in:
 * - Step3Photos (trip creation wizard)
 * - TripEditPage (editing existing trips)
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './PhotoUploader.css';

/**
 * Drag-and-drop reorder state
 */
interface DragState {
  draggedIndex: number | null;
  dragOverIndex: number | null;
}

export interface PhotoFile {
  /** Unique local ID for tracking */
  id: string;

  /** File object (for upload) */
  file?: File;

  /** Preview URL (local blob or server URL) */
  preview: string;

  /** Upload progress (0-100) */
  progress: number;

  /** Upload status */
  status: 'pending' | 'uploading' | 'success' | 'error';

  /** Error message (if upload failed) */
  errorMessage?: string;

  /** Server photo ID (after successful upload) */
  photoId?: string;
}

interface PhotoUploaderProps {
  /** Current photos (local files + uploaded) */
  photos: PhotoFile[];

  /** Callback when photos change */
  onChange: (photos: PhotoFile[]) => void;

  /** Upload function (returns photo ID on success) */
  onUpload: (file: File, onProgress: (progress: number) => void) => Promise<string>;

  /** Delete function (for already uploaded photos) */
  onDelete?: (photoId: string) => Promise<void>;

  /** Reorder function (for drag-and-drop reordering) */
  onReorder?: (photoIds: string[]) => Promise<void>;

  /** Maximum number of photos (default: 20) */
  maxPhotos?: number;

  /** Maximum file size in MB (default: 10) */
  maxSizeMB?: number;

  /** Disabled state */
  disabled?: boolean;
}

export const PhotoUploader: React.FC<PhotoUploaderProps> = ({
  photos,
  onChange,
  onUpload,
  onDelete,
  onReorder,
  maxPhotos = 20,
  maxSizeMB = 10,
  disabled = false,
}) => {
  // Future: Track upload queue for progress indicators
  // const [uploadQueue, setUploadQueue] = useState<string[]>([]); // IDs of photos being uploaded
  const [dragState, setDragState] = useState<DragState>({
    draggedIndex: null,
    dragOverIndex: null,
  });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null); // Photo ID to delete

  /**
   * Handle file drop/selection
   */
  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Show errors for rejected files
      rejectedFiles.forEach((rejection) => {
        const errors = rejection.errors.map((e: any) => e.message).join(', ');
        console.error(`File ${rejection.file.name} rejected: ${errors}`);
      });

      // Check max photos limit
      const remainingSlots = maxPhotos - photos.length;
      if (acceptedFiles.length > remainingSlots) {
        alert(`Solo puedes agregar ${remainingSlots} fotos más (máximo ${maxPhotos} fotos por viaje)`);
        acceptedFiles = acceptedFiles.slice(0, remainingSlots);
      }

      // Create photo objects
      const newPhotos: PhotoFile[] = acceptedFiles.map((file) => ({
        id: `${Date.now()}-${Math.random()}`,
        file,
        preview: URL.createObjectURL(file),
        progress: 0,
        status: 'pending' as const,
      }));

      // Add to photos list
      onChange([...photos, ...newPhotos]);

      // Start uploading (3 at a time)
      uploadPhotosInChunks([...photos, ...newPhotos]);
    },
    [photos, maxPhotos, onChange]
  );

  /**
   * Upload photos in chunks of 3 concurrently
   */
  const uploadPhotosInChunks = async (allPhotos: PhotoFile[]) => {
    const pendingPhotos = allPhotos.filter((p) => p.status === 'pending');
    const CHUNK_SIZE = 3;

    for (let i = 0; i < pendingPhotos.length; i += CHUNK_SIZE) {
      const chunk = pendingPhotos.slice(i, i + CHUNK_SIZE);

      // Upload chunk in parallel
      await Promise.all(
        chunk.map(async (photo) => {
          if (!photo.file) return;

          // Mark as uploading
          updatePhotoStatus(photo.id, 'uploading');

          try {
            // Upload with progress tracking
            const photoId = await onUpload(photo.file, (progress) => {
              updatePhotoProgress(photo.id, progress);
            });

            // Mark as success
            updatePhotoAfterUpload(photo.id, photoId, 'success');
          } catch (error: any) {
            console.error('Upload error:', error);
            updatePhotoAfterUpload(
              photo.id,
              undefined,
              'error',
              error.message || 'Error al subir la foto'
            );
          }
        })
      );
    }
  };

  /**
   * Update photo upload status
   */
  const updatePhotoStatus = (photoId: string, status: PhotoFile['status']) => {
    onChange(
      photos.map((p) =>
        p.id === photoId ? { ...p, status } : p
      )
    );
  };

  /**
   * Update photo upload progress
   */
  const updatePhotoProgress = (photoId: string, progress: number) => {
    onChange(
      photos.map((p) =>
        p.id === photoId ? { ...p, progress } : p
      )
    );
  };

  /**
   * Update photo after upload completes
   */
  const updatePhotoAfterUpload = (
    photoId: string,
    serverPhotoId: string | undefined,
    status: 'success' | 'error',
    errorMessage?: string
  ) => {
    onChange(
      photos.map((p) =>
        p.id === photoId
          ? {
              ...p,
              photoId: serverPhotoId,
              status,
              errorMessage,
              progress: status === 'success' ? 100 : p.progress,
            }
          : p
      )
    );
  };

  /**
   * Handle drag start for photo reordering
   */
  const handleDragStart = (e: React.DragEvent, index: number) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', e.currentTarget.innerHTML);
    setDragState({ draggedIndex: index, dragOverIndex: null });
  };

  /**
   * Handle drag over for photo reordering
   */
  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';

    if (dragState.draggedIndex !== index) {
      setDragState((prev) => ({ ...prev, dragOverIndex: index }));
    }
  };

  /**
   * Handle drop for photo reordering
   */
  const handleDrop = async (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();

    const { draggedIndex } = dragState;
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDragState({ draggedIndex: null, dragOverIndex: null });
      return;
    }

    // Reorder photos array
    const reordered = [...photos];
    const [draggedPhoto] = reordered.splice(draggedIndex, 1);
    reordered.splice(dropIndex, 0, draggedPhoto);

    // Update local state
    onChange(reordered);

    // Call backend to persist order
    if (onReorder) {
      try {
        const photoIds = reordered
          .filter((p) => p.photoId) // Only include uploaded photos
          .map((p) => p.photoId!);

        if (photoIds.length > 0) {
          await onReorder(photoIds);
        }
      } catch (error) {
        console.error('Reorder error:', error);
        // Revert to original order on error
        onChange(photos);
      }
    }

    setDragState({ draggedIndex: null, dragOverIndex: null });
  };

  /**
   * Handle drag end
   */
  const handleDragEnd = () => {
    setDragState({ draggedIndex: null, dragOverIndex: null });
  };

  /**
   * Remove photo (local or uploaded) with confirmation
   */
  const handleRemove = async (photo: PhotoFile) => {
    // If uploaded, call onDelete
    if (photo.photoId && onDelete) {
      try {
        await onDelete(photo.photoId);
      } catch (error) {
        console.error('Delete error:', error);
        alert('Error al eliminar la foto. Intenta nuevamente.');
        return;
      }
    }

    // Revoke blob URL if it's a local preview
    if (photo.preview.startsWith('blob:')) {
      URL.revokeObjectURL(photo.preview);
    }

    // Remove from list
    onChange(photos.filter((p) => p.id !== photo.id));

    // Close confirmation dialog
    setShowDeleteConfirm(null);
  };

  /**
   * Show delete confirmation dialog
   */
  const confirmDelete = (photoId: string) => {
    setShowDeleteConfirm(photoId);
  };

  /**
   * Cancel delete operation
   */
  const cancelDelete = () => {
    setShowDeleteConfirm(null);
  };

  /**
   * Retry failed upload
   */
  const handleRetry = async (photo: PhotoFile) => {
    if (!photo.file) return;

    // Reset status
    updatePhotoStatus(photo.id, 'pending');

    // Upload single photo
    uploadPhotosInChunks(photos);
  };

  /**
   * Configure dropzone
   */
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/webp': ['.webp'],
    },
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: true,
    disabled: disabled || photos.length >= maxPhotos,
  });

  const isMaxReached = photos.length >= maxPhotos;

  return (
    <div className="photo-uploader">
      {/* Drop Zone */}
      {!isMaxReached && (
        <div
          {...getRootProps()}
          className={`photo-uploader__dropzone ${
            isDragActive ? 'photo-uploader__dropzone--active' : ''
          } ${disabled ? 'photo-uploader__dropzone--disabled' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="photo-uploader__dropzone-content">
            <svg
              className="photo-uploader__dropzone-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p className="photo-uploader__dropzone-title">
              {isDragActive
                ? 'Suelta las fotos aquí'
                : 'Arrastra fotos o haz clic para seleccionar'}
            </p>
            <p className="photo-uploader__dropzone-subtitle">
              Máximo {maxPhotos} fotos · {maxSizeMB}MB por foto · JPG, PNG, WEBP
            </p>
          </div>
        </div>
      )}

      {/* Max Reached Message */}
      {isMaxReached && (
        <div className="photo-uploader__max-message">
          Has alcanzado el límite de {maxPhotos} fotos. Elimina algunas para agregar más.
        </div>
      )}

      {/* Thumbnail Grid */}
      {photos.length > 0 && (
        <div className="photo-uploader__grid">
          {photos.map((photo, index) => {
            const isBeingDragged = dragState.draggedIndex === index;
            const isDraggedOver = dragState.dragOverIndex === index;

            return (
              <div
                key={photo.id}
                className={`photo-uploader__thumbnail ${
                  isBeingDragged ? 'photo-uploader__thumbnail--dragging' : ''
                } ${isDraggedOver ? 'photo-uploader__thumbnail--drag-over' : ''}`}
                draggable={photo.status !== 'uploading' && !disabled}
                onDragStart={(e) => handleDragStart(e, index)}
                onDragOver={(e) => handleDragOver(e, index)}
                onDrop={(e) => handleDrop(e, index)}
                onDragEnd={handleDragEnd}
              >
                {/* Drag Handle (visible on hover) */}
                {photo.status !== 'uploading' && !disabled && (
                  <div className="photo-uploader__drag-handle">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 16 16"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M3 5h10M3 8h10M3 11h10"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  </div>
                )}

                {/* Preview Image */}
                <img
                  src={photo.preview}
                  alt="Preview"
                  className="photo-uploader__thumbnail-image"
                />

              {/* Upload Progress Overlay */}
              {photo.status === 'uploading' && (
                <div className="photo-uploader__thumbnail-overlay">
                  <div className="photo-uploader__progress-bar">
                    <div
                      className="photo-uploader__progress-fill"
                      style={{ width: `${photo.progress}%` }}
                    />
                  </div>
                  <span className="photo-uploader__progress-text">
                    {Math.round(photo.progress)}%
                  </span>
                </div>
              )}

              {/* Error Overlay */}
              {photo.status === 'error' && (
                <div className="photo-uploader__thumbnail-overlay photo-uploader__thumbnail-overlay--error">
                  <p className="photo-uploader__error-text">
                    {photo.errorMessage || 'Error'}
                  </p>
                  <button
                    type="button"
                    className="photo-uploader__retry-button"
                    onClick={() => handleRetry(photo)}
                  >
                    Reintentar
                  </button>
                </div>
              )}

              {/* Success Check */}
              {photo.status === 'success' && (
                <div className="photo-uploader__thumbnail-success">
                  <svg
                    className="photo-uploader__success-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
              )}

                {/* Remove Button */}
                <button
                  type="button"
                  className="photo-uploader__remove-button"
                  onClick={() => confirmDelete(photo.id)}
                  disabled={photo.status === 'uploading'}
                  aria-label="Eliminar foto"
                >
                  ×
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Upload Summary */}
      {photos.length > 0 && (
        <div className="photo-uploader__summary">
          <span className="photo-uploader__summary-count">
            {photos.length} / {maxPhotos} fotos
          </span>
          {photos.some((p) => p.status === 'uploading') && (
            <span className="photo-uploader__summary-uploading">
              Subiendo...
            </span>
          )}
          {photos.some((p) => p.status === 'error') && (
            <span className="photo-uploader__summary-error">
              {photos.filter((p) => p.status === 'error').length} error(es)
            </span>
          )}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="photo-uploader__delete-dialog-overlay">
          <div className="photo-uploader__delete-dialog">
            <h3 className="photo-uploader__delete-dialog-title">
              ¿Eliminar foto?
            </h3>
            <p className="photo-uploader__delete-dialog-text">
              Esta acción no se puede deshacer. ¿Estás seguro de que deseas eliminar esta foto?
            </p>
            <div className="photo-uploader__delete-dialog-actions">
              <button
                type="button"
                className="photo-uploader__delete-dialog-button photo-uploader__delete-dialog-button--cancel"
                onClick={cancelDelete}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="photo-uploader__delete-dialog-button photo-uploader__delete-dialog-button--confirm"
                onClick={() => {
                  const photo = photos.find((p) => p.id === showDeleteConfirm);
                  if (photo) {
                    handleRemove(photo);
                  }
                }}
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
