/**
 * Step4Review Component
 *
 * Fourth and final step of trip creation wizard - review all data before publishing.
 * Shows summary of all entered information: basic info, description, tags, photos (future).
 *
 * Used in:
 * - TripFormWizard (step 4/4)
 */

import React from 'react';
import { useFormContext } from 'react-hook-form';
import { TripCreateInput, DIFFICULTY_LABELS } from '../../../types/trip';
import { formatDate, formatDistance, getDifficultyLabel } from '../../../utils/tripHelpers';
import './Step1BasicInfo.css'; // Shared styles

export const Step4Review: React.FC = () => {
  const { watch, setValue } = useFormContext<TripCreateInput>();

  // Get all form values
  const formData = watch();
  const {
    title,
    description,
    start_date,
    end_date,
    distance_km,
    difficulty,
    tags = [],
    locations = [],
  } = formData;

  // Get selected photos from custom field
  const selectedPhotos = (formData as any).selectedPhotos || [];

  // Format display values
  const formattedStartDate = start_date ? formatDate(start_date) : 'No especificada';
  const formattedEndDate = end_date ? formatDate(end_date) : 'Viaje de un día';
  const formattedDistance = distance_km ? formatDistance(distance_km) : 'No especificada';
  const formattedDifficulty = difficulty ? getDifficultyLabel(difficulty) : 'No especificada';

  // Check if description meets publish requirements
  const isDescriptionValid = description && description.length >= 50;

  /**
   * Remove photo from selection
   */
  const handleRemovePhoto = (photoId: string) => {
    const updatedPhotos = selectedPhotos.filter((p: any) => p.id !== photoId);

    // Revoke blob URL to free memory
    const photoToRemove = selectedPhotos.find((p: any) => p.id === photoId);
    if (photoToRemove && photoToRemove.preview) {
      URL.revokeObjectURL(photoToRemove.preview);
    }

    setValue('selectedPhotos' as any, updatedPhotos);
  };

  return (
    <div className="step4-review">
      <div className="step4-review__header">
        <h2 className="step4-review__title">Revisión Final</h2>
        <p className="step4-review__description">
          Revisa la información de tu viaje antes de publicar. Puedes volver a cualquier paso anterior para hacer cambios.
        </p>
      </div>

      <div className="step4-review__content">
        {/* Basic Info Section */}
        <div className="review-section">
          <h3 className="review-section__title">Información Básica</h3>
          <div className="review-section__content">
            <div className="review-item">
              <span className="review-item__label">Título:</span>
              <span className="review-item__value">{title || 'Sin título'}</span>
            </div>
            <div className="review-item">
              <span className="review-item__label">Fecha de inicio:</span>
              <span className="review-item__value">{formattedStartDate}</span>
            </div>
            <div className="review-item">
              <span className="review-item__label">Fecha de fin:</span>
              <span className="review-item__value">{formattedEndDate}</span>
            </div>
            <div className="review-item">
              <span className="review-item__label">Distancia:</span>
              <span className="review-item__value">{formattedDistance}</span>
            </div>
            <div className="review-item">
              <span className="review-item__label">Dificultad:</span>
              <span className="review-item__value">{formattedDifficulty}</span>
            </div>
          </div>
        </div>

        {/* Locations Section */}
        <div className="review-section">
          <h3 className="review-section__title">Ubicaciones</h3>
          <div className="review-section__content">
            {locations.length > 0 ? (
              <div className="review-locations">
                {locations.map((location, index) => (
                  <div key={index} className="review-location">
                    <div className="review-location__header">
                      <span className="review-location__number">{index + 1}</span>
                      <span className="review-location__name">{location.name || 'Sin nombre'}</span>
                    </div>
                    {location.latitude !== null && location.longitude !== null ? (
                      <div className="review-location__coords">
                        <span className="review-location__coord">
                          📍 Lat: {location.latitude.toFixed(6)}°
                        </span>
                        <span className="review-location__coord">
                          Lon: {location.longitude.toFixed(6)}°
                        </span>
                      </div>
                    ) : (
                      <span className="review-location__no-coords">Sin coordenadas GPS</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="review-empty">Sin ubicaciones</p>
            )}
          </div>
        </div>

        {/* Description Section */}
        <div className="review-section">
          <h3 className="review-section__title">Descripción</h3>
          <div className="review-section__content">
            {description ? (
              <>
                <p className="review-description">{description}</p>
                <div className="review-description-meta">
                  <span className="review-description-length">
                    {description.length.toLocaleString()} caracteres
                  </span>
                  {!isDescriptionValid && (
                    <span className="review-description-warning">
                      ⚠️ Mínimo 50 caracteres para publicar (puedes guardar como borrador)
                    </span>
                  )}
                  {isDescriptionValid && (
                    <span className="review-description-success">
                      ✓ Listo para publicar
                    </span>
                  )}
                </div>
              </>
            ) : (
              <p className="review-empty">Sin descripción</p>
            )}
          </div>
        </div>

        {/* Tags Section */}
        <div className="review-section">
          <h3 className="review-section__title">Etiquetas</h3>
          <div className="review-section__content">
            {tags.length > 0 ? (
              <div className="review-tags">
                {tags.map((tag, index) => (
                  <span key={index} className="review-tag">
                    {tag}
                  </span>
                ))}
              </div>
            ) : (
              <p className="review-empty">Sin etiquetas</p>
            )}
          </div>
        </div>

        {/* Photos Section */}
        <div className="review-section">
          <h3 className="review-section__title">Fotos</h3>
          <div className="review-section__content">
            {selectedPhotos.length > 0 ? (
              <>
                <div className="review-photos-grid">
                  {selectedPhotos.map((photo: any) => (
                    <div key={photo.id} className="review-photo-thumbnail">
                      <img
                        src={photo.preview}
                        alt={photo.file.name}
                        className="review-photo-image"
                      />
                      <button
                        type="button"
                        className="review-photo-remove"
                        onClick={() => handleRemovePhoto(photo.id)}
                        aria-label="Eliminar foto"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
                <p className="review-photos-count">
                  {selectedPhotos.length} foto{selectedPhotos.length !== 1 ? 's' : ''} seleccionada{selectedPhotos.length !== 1 ? 's' : ''}
                </p>
              </>
            ) : (
              <p className="review-empty">
                Sin fotos (puedes añadirlas más tarde editando el viaje)
              </p>
            )}
          </div>
        </div>

        {/* Publish Warning */}
        {!isDescriptionValid && (
          <div className="review-warning">
            <svg
              className="review-warning__icon"
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
            <div className="review-warning__content">
              <h4 className="review-warning__title">Descripción muy corta para publicar</h4>
              <p className="review-warning__text">
                Para publicar tu viaje, la descripción debe tener al menos 50 caracteres.
                Puedes volver al Paso 2 para ampliar la descripción, o guardar como borrador
                y publicar más tarde.
              </p>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .step4-review__content {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .review-section {
          padding: 24px;
          background-color: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
        }

        .review-section__title {
          font-size: 1.125rem;
          font-weight: 600;
          color: var(--text-primary, #111827);
          margin: 0 0 16px 0;
          padding-bottom: 12px;
          border-bottom: 2px solid #f3f4f6;
        }

        .review-section__content {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .review-item {
          display: flex;
          gap: 12px;
        }

        .review-item__label {
          font-weight: 600;
          color: var(--text-secondary, #6b7280);
          min-width: 140px;
        }

        .review-item__value {
          color: var(--text-primary, #111827);
        }

        .review-description {
          font-size: 0.9375rem;
          line-height: 1.6;
          color: var(--text-primary, #111827);
          white-space: pre-wrap;
          margin: 0;
        }

        .review-description-meta {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-top: 8px;
          font-size: 0.875rem;
        }

        .review-description-length {
          color: var(--text-secondary, #6b7280);
        }

        .review-description-warning {
          color: #f59e0b;
          font-weight: 500;
        }

        .review-description-success {
          color: #10b981;
          font-weight: 500;
        }

        .review-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .review-tag {
          display: inline-block;
          padding: 6px 12px;
          background-color: #eff6ff;
          color: var(--primary-color, #2563eb);
          border: 1px solid #dbeafe;
          border-radius: 16px;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .review-empty {
          color: var(--text-secondary, #6b7280);
          font-style: italic;
          margin: 0;
        }

        .review-locations {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .review-location {
          padding: 12px;
          background-color: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
        }

        .review-location__header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 8px;
        }

        .review-location__number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          background-color: var(--primary-color, #2563eb);
          color: #ffffff;
          border-radius: 50%;
          font-size: 0.75rem;
          font-weight: 600;
        }

        .review-location__name {
          font-size: 0.9375rem;
          font-weight: 600;
          color: var(--text-primary, #111827);
        }

        .review-location__coords {
          display: flex;
          gap: 16px;
          font-size: 0.875rem;
          color: var(--text-secondary, #6b7280);
          font-family: 'Courier New', monospace;
        }

        .review-location__coord {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .review-location__no-coords {
          font-size: 0.875rem;
          color: var(--text-secondary, #6b7280);
          font-style: italic;
        }

        .review-photos-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
          gap: 12px;
          margin-bottom: 12px;
        }

        .review-photo-thumbnail {
          position: relative;
          aspect-ratio: 1;
          border-radius: 8px;
          overflow: hidden;
          background-color: #f3f4f6;
          border: 2px solid #e5e7eb;
        }

        .review-photo-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .review-photo-remove {
          position: absolute;
          top: 4px;
          right: 4px;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 0;
          background-color: rgba(0, 0, 0, 0.6);
          border: none;
          border-radius: 50%;
          color: #ffffff;
          font-size: 1.25rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease-in-out;
          line-height: 1;
        }

        .review-photo-remove:hover {
          background-color: #ef4444;
          transform: scale(1.1);
        }

        .review-photos-count {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-secondary, #6b7280);
          margin: 0;
        }

        .review-warning {
          display: flex;
          gap: 16px;
          padding: 16px;
          background-color: #fffbeb;
          border: 1px solid #fef3c7;
          border-left: 4px solid #f59e0b;
          border-radius: 8px;
        }

        .review-warning__icon {
          width: 24px;
          height: 24px;
          color: #f59e0b;
          flex-shrink: 0;
        }

        .review-warning__content {
          flex: 1;
        }

        .review-warning__title {
          font-size: 0.9375rem;
          font-weight: 600;
          color: #92400e;
          margin: 0 0 4px 0;
        }

        .review-warning__text {
          font-size: 0.875rem;
          line-height: 1.5;
          color: #78350f;
          margin: 0;
        }

        @media (max-width: 640px) {
          .review-section {
            padding: 16px;
          }

          .review-item {
            flex-direction: column;
            gap: 4px;
          }

          .review-item__label {
            min-width: auto;
          }

          .review-warning {
            flex-direction: column;
            gap: 12px;
          }
        }
      `}</style>
    </div>
  );
};
