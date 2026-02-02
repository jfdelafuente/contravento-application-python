/**
 * Step2Details Component - Trip Details Form
 *
 * Wizard Step 2: Form for entering trip details after GPX upload.
 * Auto-populates title from filename and displays read-only difficulty.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 5 (US3)
 * Tasks: T052, T053, T054
 *
 * @example
 * ```typescript
 * <Step2Details
 *   gpxFile={file}
 *   telemetry={telemetry}
 *   onNext={(formData) => console.log('Next:', formData)}
 *   onPrevious={() => console.log('Previous')}
 *   onCancel={() => console.log('Cancel')}
 *   onRemoveGPX={() => console.log('Remove GPX')}
 * />
 * ```
 */

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { DifficultyBadge } from '../trips/DifficultyBadge';
import { tripDetailsSchema, type TripDetailsFormData } from '../../schemas/tripDetailsSchema';
import type { GPXTelemetry } from '../../services/gpxWizardService';
import './Step2Details.css';

/**
 * Props for Step2Details component
 */
export interface Step2DetailsProps {
  /** Uploaded GPX file */
  gpxFile: File;

  /** Telemetry data from GPX analysis */
  telemetry: GPXTelemetry;

  /** Callback when form is valid and user clicks "Siguiente" */
  onNext: (formData: TripDetailsFormData) => void;

  /** Callback when user clicks "Anterior" */
  onPrevious: () => void;

  /** Callback when user confirms wizard cancellation */
  onCancel: () => void;

  /** Callback when user confirms GPX file removal */
  onRemoveGPX: () => void;

  /** Initial form data (for editing) */
  initialData?: Partial<TripDetailsFormData>;
}

/**
 * Step 2: Trip Details Form
 *
 * Displays form for entering trip details with:
 * - Auto-populated title from GPX filename
 * - Read-only difficulty badge (calculated from telemetry)
 * - Form validation (title max 200, description min 50)
 * - Privacy selector (public/private)
 * - Date inputs (start/end)
 *
 * @param props - Component props
 */
export const Step2Details: React.FC<Step2DetailsProps> = ({
  gpxFile: _gpxFile,
  telemetry,
  onNext,
  onPrevious,
  onCancel,
  onRemoveGPX,
  initialData,
}) => {
  const [showCancelDialog, setShowCancelDialog] = useState(false);
  const [showRemoveDialog, setShowRemoveDialog] = useState(false);

  // Use Smart-Title from backend (cleaned and formatted)
  const defaultTitle = telemetry.suggested_title;

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<TripDetailsFormData>({
    resolver: zodResolver(tripDetailsSchema),
    mode: 'onChange',
    defaultValues: {
      title: initialData?.title || defaultTitle,
      description: initialData?.description || '',
      start_date: initialData?.start_date || telemetry.start_date || '',
      end_date: initialData?.end_date || telemetry.end_date || '',
      privacy: initialData?.privacy || 'public',
    },
  });

  // Watch description for character count
  const description = watch('description');
  const descriptionLength = description?.length || 0;

  /**
   * Handle ESC key to close dialogs (T100)
   */
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        if (showCancelDialog) {
          setShowCancelDialog(false);
        } else if (showRemoveDialog) {
          setShowRemoveDialog(false);
        }
      }
    };

    // Only add listener if a dialog is open
    if (showCancelDialog || showRemoveDialog) {
      document.addEventListener('keydown', handleEscKey);
      return () => {
        document.removeEventListener('keydown', handleEscKey);
      };
    }
  }, [showCancelDialog, showRemoveDialog]);

  /**
   * Handle form submission (Next button).
   */
  const onSubmit = (data: TripDetailsFormData) => {
    onNext(data);
  };

  /**
   * Handle cancel button click (show confirmation).
   */
  const handleCancelClick = () => {
    setShowCancelDialog(true);
  };

  /**
   * Confirm cancellation.
   */
  const confirmCancel = () => {
    setShowCancelDialog(false);
    onCancel();
  };

  /**
   * Handle remove GPX button click (show confirmation).
   */
  const handleRemoveClick = () => {
    setShowRemoveDialog(true);
  };

  /**
   * Confirm GPX removal.
   */
  const confirmRemove = () => {
    setShowRemoveDialog(false);
    onRemoveGPX();
  };

  return (
    <div className="step2-details">
      {/* Step Header */}
      <div className="step2-details__header">
        <h2 className="step2-details__title">Detalles del Viaje</h2>
        <p className="step2-details__description">
          Completa la información de tu viaje. La dificultad se calcula automáticamente según los
          datos del GPX.
        </p>
      </div>

      {/* Telemetry Summary */}
      <div className="step2-details__summary">
        <div className="step2-details__summary-item">
          <span className="step2-details__summary-label">Distancia:</span>
          <span className="step2-details__summary-value">{telemetry.distance_km} km</span>
        </div>

        {telemetry.has_elevation && telemetry.elevation_gain !== null && (
          <div className="step2-details__summary-item">
            <span className="step2-details__summary-label">Desnivel:</span>
            <span className="step2-details__summary-value">{telemetry.elevation_gain} m</span>
          </div>
        )}

        <div className="step2-details__summary-item">
          <span className="step2-details__summary-label">Dificultad:</span>
          <DifficultyBadge difficulty={telemetry.difficulty} />
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="step2-details__form">
        {/* Title */}
        <div className="step2-details__field">
          <label htmlFor="title" className="step2-details__label">
            Título <span className="step2-details__required">*</span>
          </label>
          <input
            id="title"
            type="text"
            {...register('title')}
            className={`step2-details__input ${errors.title ? 'step2-details__input--error' : ''}`}
            placeholder="Nombre de tu ruta"
            aria-required="true"
            aria-invalid={!!errors.title}
            aria-describedby={errors.title ? 'title-error' : undefined}
          />
          {errors.title && (
            <div id="title-error" role="alert" className="step2-details__error">
              {errors.title.message}
            </div>
          )}
          <div className="step2-details__hint">Máximo 200 caracteres</div>
        </div>

        {/* Description */}
        <div className="step2-details__field">
          <label htmlFor="description" className="step2-details__label">
            Descripción <span className="step2-details__required">*</span>
          </label>
          <textarea
            id="description"
            {...register('description')}
            className={`step2-details__textarea ${
              errors.description ? 'step2-details__input--error' : ''
            }`}
            placeholder="Describe tu viaje, lugares visitados, experiencias..."
            rows={5}
            aria-required="true"
            aria-invalid={!!errors.description}
            aria-describedby={errors.description ? 'description-error' : 'description-hint'}
          />
          {errors.description && (
            <div id="description-error" role="alert" className="step2-details__error">
              {errors.description.message}
            </div>
          )}
          <div
            id="description-hint"
            className={`step2-details__hint ${descriptionLength < 50 ? 'step2-details__hint--warn' : ''}`}
          >
            {descriptionLength} / 50 caracteres mínimos
          </div>
        </div>

        {/* Dates */}
        <div className="step2-details__date-group">
          <div className="step2-details__field">
            <label htmlFor="start_date" className="step2-details__label">
              Fecha de inicio <span className="step2-details__required">*</span>
            </label>
            <input
              id="start_date"
              type="date"
              {...register('start_date')}
              className={`step2-details__input ${
                errors.start_date ? 'step2-details__input--error' : ''
              }`}
              aria-required="true"
              aria-invalid={!!errors.start_date}
            />
            {errors.start_date && (
              <div role="alert" className="step2-details__error">
                {errors.start_date.message}
              </div>
            )}
            {telemetry.has_timestamps && telemetry.start_date && (
              <div className="step2-details__hint">Fecha extraída del GPX</div>
            )}
          </div>

          <div className="step2-details__field">
            <label htmlFor="end_date" className="step2-details__label">
              Fecha de fin
            </label>
            <input
              id="end_date"
              type="date"
              {...register('end_date')}
              className="step2-details__input"
            />
            {telemetry.has_timestamps && telemetry.end_date ? (
              <div className="step2-details__hint">Fecha extraída del GPX</div>
            ) : (
              <div className="step2-details__hint">Opcional</div>
            )}
          </div>
        </div>

        {/* Privacy */}
        <div className="step2-details__field">
          <label className="step2-details__label">
            Privacidad <span className="step2-details__required">*</span>
          </label>
          <div className="step2-details__radio-group">
            <label className="step2-details__radio-label">
              <input
                type="radio"
                {...register('privacy')}
                value="public"
                className="step2-details__radio"
              />
              <span>Público</span>
              <span className="step2-details__radio-description">
                Visible para todos los usuarios
              </span>
            </label>

            <label className="step2-details__radio-label">
              <input
                type="radio"
                {...register('privacy')}
                value="private"
                className="step2-details__radio"
              />
              <span>Privado</span>
              <span className="step2-details__radio-description">Solo visible para ti</span>
            </label>
          </div>
        </div>

        {/* Actions */}
        <div className="step2-details__actions">
          <div className="step2-details__actions-left">
            <button
              type="button"
              onClick={handleRemoveClick}
              className="step2-details__button step2-details__button--danger"
              aria-label="Eliminar archivo GPX y volver al paso anterior"
            >
              Eliminar archivo GPX
            </button>
          </div>

          <div className="step2-details__actions-right">
            <button
              type="button"
              onClick={onPrevious}
              className="step2-details__button step2-details__button--secondary"
              aria-label="Volver al paso anterior de carga de archivo"
            >
              Anterior
            </button>

            <button
              type="submit"
              disabled={!isValid}
              className="step2-details__button step2-details__button--primary"
              aria-label={isValid ? "Continuar al siguiente paso" : "Completar el formulario para continuar"}
            >
              Siguiente
            </button>

            <button
              type="button"
              onClick={handleCancelClick}
              className="step2-details__button step2-details__button--secondary"
              aria-label="Cancelar creación de viaje"
            >
              Cancelar
            </button>
          </div>
        </div>
      </form>

      {/* Cancel Confirmation Dialog */}
      {showCancelDialog && (
        <div
          className="step2-details__dialog-overlay"
          onClick={() => setShowCancelDialog(false)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="cancel-dialog-title"
        >
          <div className="step2-details__dialog" onClick={(e) => e.stopPropagation()}>
            <h3 id="cancel-dialog-title" className="step2-details__dialog-title">
              ¿Seguro que quieres cancelar el asistente?
            </h3>
            <p className="step2-details__dialog-text">
              Se perderán todos los datos ingresados, incluyendo el archivo GPX.
            </p>
            <div className="step2-details__dialog-actions">
              <button
                onClick={() => setShowCancelDialog(false)}
                className="step2-details__button step2-details__button--secondary"
              >
                No, continuar
              </button>
              <button
                onClick={confirmCancel}
                className="step2-details__button step2-details__button--danger"
              >
                Sí, cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Remove GPX Confirmation Dialog */}
      {showRemoveDialog && (
        <div
          className="step2-details__dialog-overlay"
          onClick={() => setShowRemoveDialog(false)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="remove-dialog-title"
        >
          <div className="step2-details__dialog" onClick={(e) => e.stopPropagation()}>
            <h3 id="remove-dialog-title" className="step2-details__dialog-title">
              ¿Eliminar archivo GPX?
            </h3>
            <p className="step2-details__dialog-text">
              Esto eliminará el archivo y volverás al paso 1. Deberás cargar un nuevo archivo GPX.
            </p>
            <div className="step2-details__dialog-actions">
              <button
                onClick={() => setShowRemoveDialog(false)}
                className="step2-details__button step2-details__button--secondary"
              >
                No, mantener
              </button>
              <button
                onClick={confirmRemove}
                className="step2-details__button step2-details__button--danger"
              >
                Sí, eliminar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
