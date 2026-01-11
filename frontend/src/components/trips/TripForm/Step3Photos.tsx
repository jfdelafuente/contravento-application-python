/**
 * Step3Photos Component
 *
 * Third step of trip creation wizard - select photos to upload.
 * Photos are stored temporarily and will be uploaded after trip creation.
 *
 * Used in:
 * - TripFormWizard (step 3/4)
 */

import React, { useState, useRef, useEffect } from 'react';
import { useFormContext } from 'react-hook-form';
import toast from 'react-hot-toast';
import { TripCreateInput, TripPhoto } from '../../../types/trip';
import { getPhotoUrl } from '../../../utils/tripHelpers';
import './Step1BasicInfo.css'; // Shared styles

export interface PhotoPreview {
  file: File;
  preview: string;
  id: string;
}

interface Step3PhotosProps {
  /** Trip ID (for edit mode) */
  tripId?: string;

  /** Existing photos from server (for edit mode) */
  existingPhotos?: TripPhoto[];
}

export const Step3Photos: React.FC<Step3PhotosProps> = ({
  tripId,
  existingPhotos = []
}) => {
  const [photos, setPhotos] = useState<PhotoPreview[]>([]);
  const [serverPhotos, setServerPhotos] = useState<TripPhoto[]>(existingPhotos);
  const [photosToDelete, setPhotosToDelete] = useState<string[]>([]); // Photo IDs to delete
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { setValue } = useFormContext<TripCreateInput>();

  const MAX_PHOTOS = 20;
  const MAX_SIZE_MB = 10;

  // Calculate total photo count (existing + new - deleted)
  const totalPhotoCount = serverPhotos.filter(p => !photosToDelete.includes(p.photo_id)).length + photos.length;

  // Update server photos when existingPhotos prop changes (when trip loads)
  useEffect(() => {
    if (existingPhotos && existingPhotos.length > 0) {
      setServerPhotos(existingPhotos);
    }
  }, [existingPhotos]);

  // Sync photos and deletion list with form context
  useEffect(() => {
    setValue('selectedPhotos' as any, photos);
    setValue('photosToDelete' as any, photosToDelete);
  }, [photos, photosToDelete, setValue]);

  /**
   * Handle file selection
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const filesArray = Array.from(files);

    // Validate count (consider existing photos not marked for deletion)
    const remainingSlots = MAX_PHOTOS - totalPhotoCount;
    if (filesArray.length > remainingSlots) {
      toast.error(`Solo puedes agregar ${remainingSlots} fotos más (máximo ${MAX_PHOTOS} fotos)`);
      return;
    }

    // Validate and create previews
    const validFiles: PhotoPreview[] = [];

    for (const file of filesArray) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast.error(`${file.name} no es una imagen válida`);
        continue;
      }

      // Validate file size
      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > MAX_SIZE_MB) {
        toast.error(`${file.name} excede el tamaño máximo de ${MAX_SIZE_MB}MB`);
        continue;
      }

      validFiles.push({
        file,
        preview: URL.createObjectURL(file),
        id: `${Date.now()}-${Math.random()}`,
      });
    }

    setPhotos((prev) => [...prev, ...validFiles]);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  /**
   * Remove new photo (not yet uploaded)
   */
  const handleRemovePhoto = (id: string) => {
    setPhotos((prev) => {
      const photoToRemove = prev.find((p) => p.id === id);
      if (photoToRemove) {
        URL.revokeObjectURL(photoToRemove.preview);
      }
      return prev.filter((p) => p.id !== id);
    });
  };

  /**
   * Mark server photo for deletion
   */
  const handleRemoveServerPhoto = (photoId: string) => {
    setPhotosToDelete((prev) => [...prev, photoId]);
    toast.success('Foto marcada para eliminar', { duration: 2000 });
  };

  /**
   * Restore server photo (undo deletion mark)
   */
  const handleRestoreServerPhoto = (photoId: string) => {
    setPhotosToDelete((prev) => prev.filter((id) => id !== photoId));
    toast.success('Foto restaurada', { duration: 2000 });
  };

  /**
   * Trigger file input click
   */
  const handleSelectClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="step3-photos">
      <div className="step3-photos__header">
        <h2 className="step3-photos__title">Fotos del Viaje</h2>
        <p className="step3-photos__description">
          {tripId
            ? 'Administra las fotos de tu viaje. Puedes eliminar fotos existentes o agregar nuevas (máximo 20 fotos totales).'
            : 'Selecciona fotos para subirlas después de crear el viaje. Puedes subir hasta 20 fotos (máximo 10MB cada una).'}
        </p>
      </div>

      <div className="step3-photos__content">
        {/* File Input (hidden) */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          multiple
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        {/* Select Button */}
        {totalPhotoCount < MAX_PHOTOS && (
          <button
            type="button"
            className="step3-photos__select-button"
            onClick={handleSelectClick}
          >
            <svg
              className="step3-photos__select-icon"
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
            <span>{tripId ? 'Agregar Más Fotos' : 'Seleccionar Fotos'}</span>
            <span className="step3-photos__select-hint">
              ({totalPhotoCount}/{MAX_PHOTOS} fotos)
            </span>
          </button>
        )}

        {/* Existing Server Photos (Edit Mode) */}
        {tripId && serverPhotos.length > 0 && (
          <div>
            <h3 style={{ marginBottom: '12px', fontSize: '1rem', fontWeight: 600 }}>
              Fotos Actuales ({serverPhotos.filter(p => !photosToDelete.includes(p.photo_id)).length})
            </h3>
            <div className="step3-photos__grid">
              {serverPhotos.map((photo) => {
                const isMarkedForDeletion = photosToDelete.includes(photo.photo_id);
                return (
                  <div
                    key={photo.photo_id}
                    className={`step3-photos__thumbnail ${isMarkedForDeletion ? 'step3-photos__thumbnail--deleted' : ''}`}
                  >
                    <img
                      src={getPhotoUrl(photo.thumbnail_url || photo.photo_url)}
                      alt={photo.caption || 'Foto del viaje'}
                      className="step3-photos__thumbnail-image"
                      style={{ opacity: isMarkedForDeletion ? 0.3 : 1 }}
                    />
                    {isMarkedForDeletion ? (
                      <button
                        type="button"
                        className="step3-photos__restore-button"
                        onClick={() => handleRestoreServerPhoto(photo.photo_id)}
                        aria-label="Restaurar foto"
                      >
                        ↺ Restaurar
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="step3-photos__remove-button"
                        onClick={() => handleRemoveServerPhoto(photo.photo_id)}
                        aria-label="Eliminar foto"
                      >
                        ×
                      </button>
                    )}
                    {photo.caption && !isMarkedForDeletion && (
                      <div className="step3-photos__thumbnail-info">
                        <span className="step3-photos__thumbnail-name">
                          {photo.caption.length > 20
                            ? photo.caption.substring(0, 17) + '...'
                            : photo.caption}
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* New Photo Previews */}
        {photos.length > 0 && (
          <div>
            {tripId && <h3 style={{ marginBottom: '12px', fontSize: '1rem', fontWeight: 600 }}>
              Nuevas Fotos ({photos.length})
            </h3>}
            <div className="step3-photos__grid">
              {photos.map((photo) => (
                <div key={photo.id} className="step3-photos__thumbnail">
                  <img
                    src={photo.preview}
                    alt={photo.file.name}
                    className="step3-photos__thumbnail-image"
                  />
                  <button
                    type="button"
                    className="step3-photos__remove-button"
                    onClick={() => handleRemovePhoto(photo.id)}
                    aria-label="Eliminar foto"
                  >
                    ×
                  </button>
                  <div className="step3-photos__thumbnail-info">
                    <span className="step3-photos__thumbnail-name">
                      {photo.file.name.length > 20
                        ? photo.file.name.substring(0, 17) + '...'
                        : photo.file.name}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Note */}
        <p className="step3-photos__note">
          <strong>Nota:</strong> {tripId
            ? 'Las fotos marcadas para eliminar se eliminarán al guardar los cambios.'
            : 'Las fotos seleccionadas se subirán automáticamente después de crear el viaje. Si guardas como borrador, las fotos no se subirán hasta que publiques el viaje.'}
        </p>
      </div>

      <style>{`
        .step3-photos__content {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .step3-photos__select-button {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 48px 32px;
          background-color: #f9fafb;
          border: 2px dashed #d1d5db;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s ease-in-out;
          font-size: 1rem;
          font-weight: 600;
          color: var(--text-primary, #111827);
          gap: 12px;
        }

        .step3-photos__select-button:hover {
          border-color: var(--primary-color, #2563eb);
          background-color: #eff6ff;
        }

        .step3-photos__select-icon {
          width: 48px;
          height: 48px;
          color: var(--primary-color, #2563eb);
        }

        .step3-photos__select-hint {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-secondary, #6b7280);
        }

        .step3-photos__grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          gap: 16px;
        }

        .step3-photos__thumbnail {
          position: relative;
          aspect-ratio: 1;
          border-radius: 8px;
          overflow: hidden;
          background-color: #f3f4f6;
          border: 2px solid #e5e7eb;
        }

        .step3-photos__thumbnail-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .step3-photos__remove-button {
          position: absolute;
          top: 8px;
          right: 8px;
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          background-color: rgba(0, 0, 0, 0.6);
          border: none;
          border-radius: 50%;
          color: #ffffff;
          font-size: 1.5rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease-in-out;
          line-height: 1;
        }

        .step3-photos__remove-button:hover {
          background-color: #ef4444;
          transform: scale(1.1);
        }

        .step3-photos__restore-button {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          padding: 8px 16px;
          background-color: #10b981;
          border: none;
          border-radius: 6px;
          color: #ffffff;
          font-size: 0.875rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease-in-out;
          z-index: 10;
        }

        .step3-photos__restore-button:hover {
          background-color: #059669;
          transform: translate(-50%, -50%) scale(1.05);
        }

        .step3-photos__thumbnail--deleted {
          position: relative;
        }

        .step3-photos__thumbnail--deleted::after {
          content: 'Eliminando';
          position: absolute;
          top: 8px;
          left: 8px;
          padding: 4px 8px;
          background-color: rgba(239, 68, 68, 0.9);
          color: white;
          font-size: 0.75rem;
          font-weight: 600;
          border-radius: 4px;
        }

        .step3-photos__thumbnail-info {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          padding: 8px;
          background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
        }

        .step3-photos__thumbnail-name {
          font-size: 0.75rem;
          color: #ffffff;
          display: block;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .step3-photos__note {
          padding: 16px;
          background-color: #eff6ff;
          border-left: 4px solid var(--primary-color, #2563eb);
          border-radius: 8px;
          font-size: 0.9375rem;
          color: var(--text-primary, #111827);
          margin: 0;
        }

        .step3-photos__note strong {
          font-weight: 600;
          color: var(--primary-color, #2563eb);
        }

        @media (max-width: 640px) {
          .step3-photos__select-button {
            padding: 32px 24px;
          }

          .step3-photos__select-icon {
            width: 40px;
            height: 40px;
          }

          .step3-photos__grid {
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 12px;
          }
        }
      `}</style>
    </div>
  );
};
