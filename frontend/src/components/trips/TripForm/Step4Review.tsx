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
  const { watch } = useFormContext<TripCreateInput>();

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
  } = formData;

  // Format display values
  const formattedStartDate = start_date ? formatDate(start_date) : 'No especificada';
  const formattedEndDate = end_date ? formatDate(end_date) : 'Viaje de un día';
  const formattedDistance = distance_km ? formatDistance(distance_km) : 'No especificada';
  const formattedDifficulty = difficulty ? getDifficultyLabel(difficulty) : 'No especificada';

  // Check if description meets publish requirements
  const isDescriptionValid = description && description.length >= 50;

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

        {/* Photos Section (placeholder) */}
        <div className="review-section">
          <h3 className="review-section__title">Fotos</h3>
          <div className="review-section__content">
            <p className="review-empty">
              La gestión de fotos se implementará en la siguiente fase (T048)
            </p>
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
