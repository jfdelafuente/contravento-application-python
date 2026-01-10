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
import { TripCreateInput } from '../../../types/trip';
import './Step1BasicInfo.css'; // Shared styles

export interface PhotoPreview {
  file: File;
  preview: string;
  id: string;
}

export const Step3Photos: React.FC = () => {
  const [photos, setPhotos] = useState<PhotoPreview[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { setValue } = useFormContext<TripCreateInput>();

  const MAX_PHOTOS = 20;
  const MAX_SIZE_MB = 10;

  // Sync photos with form context (stored in a custom field)
  useEffect(() => {
    setValue('selectedPhotos' as any, photos);
  }, [photos, setValue]);

  /**
   * Handle file selection
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const filesArray = Array.from(files);

    // Validate count
    const remainingSlots = MAX_PHOTOS - photos.length;
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
   * Remove photo
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
          Selecciona fotos para subirlas después de crear el viaje. Puedes subir hasta 20 fotos (máximo 10MB cada una).
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
        {photos.length < MAX_PHOTOS && (
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
            <span>Seleccionar Fotos</span>
            <span className="step3-photos__select-hint">
              ({photos.length}/{MAX_PHOTOS} seleccionadas)
            </span>
          </button>
        )}

        {/* Photo Previews */}
        {photos.length > 0 && (
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
        )}

        {/* Info Note */}
        <p className="step3-photos__note">
          <strong>Nota:</strong> Las fotos seleccionadas se subirán automáticamente después de crear el viaje.
          Si guardas como borrador, las fotos no se subirán hasta que publiques el viaje.
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
