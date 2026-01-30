/**
 * Step3Review Component - Review and Publish
 *
 * Wizard Step 3: Displays summary of all wizard data before publishing.
 * Shows trip details, GPX info, and telemetry with publish button.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 6 (US6)
 * Tasks: T069, T070, T071
 *
 * @example
 * ```typescript
 * <Step3Review
 *   gpxFile={file}
 *   telemetry={telemetry}
 *   tripDetails={tripDetails}
 *   onPublish={() => console.log('Publishing...')}
 *   onPrevious={() => console.log('Previous')}
 *   onCancel={() => console.log('Cancel')}
 *   isPublishing={false}
 * />
 * ```
 */

import React from 'react';
import { DifficultyBadge } from '../trips/DifficultyBadge';
import type { GPXTelemetry } from '../../services/gpxWizardService';
import type { TripDetailsFormData } from '../../schemas/tripDetailsSchema';
import './Step3Review.css';

/**
 * Props for Step3Review component
 */
export interface Step3ReviewProps {
  /** Uploaded GPX file */
  gpxFile: File;

  /** Telemetry data from GPX analysis */
  telemetry: GPXTelemetry;

  /** Trip details form data */
  tripDetails: TripDetailsFormData;

  /** Callback when user clicks "Publicar Viaje" */
  onPublish: () => void;

  /** Callback when user clicks "Anterior" */
  onPrevious: () => void;

  /** Callback when user clicks "Cancelar" */
  onCancel: () => void;

  /** Whether the publish request is in progress */
  isPublishing: boolean;
}

/**
 * Format date for display in Spanish
 * @param dateString - Date string in YYYY-MM-DD format
 * @returns Formatted date (e.g., "1 de junio de 2024")
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString + 'T00:00:00');
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Format date range for display
 * @param startDate - Start date string
 * @param endDate - End date string (optional)
 * @returns Formatted date range or single date
 */
function formatDateRange(startDate: string, endDate?: string | null): string {
  if (!endDate || endDate === '') {
    return formatDate(startDate);
  }

  return `${formatDate(startDate)} - ${formatDate(endDate)}`;
}

/**
 * Truncate description to first N words
 * @param description - Full description text
 * @param maxWords - Maximum number of words to show (default: 50)
 * @returns Truncated description with "..." if shortened
 */
function truncateDescription(description: string, maxWords: number = 50): string {
  const words = description.trim().split(/\s+/);

  if (words.length <= maxWords) {
    return description;
  }

  return words.slice(0, maxWords).join(' ') + '...';
}

/**
 * Step 3: Review and Publish
 *
 * Displays comprehensive summary of all wizard data:
 * - Trip details (title, description, dates, privacy)
 * - GPX file info (filename, distance, elevation, difficulty)
 * - Publish button with loading state
 *
 * @param props - Component props
 */
export const Step3Review: React.FC<Step3ReviewProps> = ({
  gpxFile,
  telemetry,
  tripDetails,
  onPublish,
  onPrevious,
  onCancel,
  isPublishing,
}) => {
  return (
    <div className="step3-review">
      {/* Step Header */}
      <div className="step3-review__header">
        <h2 className="step3-review__title">Revisar y Publicar</h2>
        <p className="step3-review__description">
          Revisa los datos de tu viaje antes de publicarlo. Podrás editarlo después si es necesario.
        </p>
      </div>

      {/* Summary Sections */}
      <div className="step3-review__summary">
        {/* Trip Details Section */}
        <section className="step3-review__section">
          <h3 className="step3-review__section-title">Detalles del Viaje</h3>

          <div className="step3-review__field">
            <span className="step3-review__label">Título:</span>
            <span className="step3-review__value">{tripDetails.title}</span>
          </div>

          <div className="step3-review__field">
            <span className="step3-review__label">Descripción:</span>
            <p className="step3-review__value step3-review__value--multiline">
              {truncateDescription(tripDetails.description)}
            </p>
          </div>

          <div className="step3-review__field">
            <span className="step3-review__label">Fechas:</span>
            <span className="step3-review__value">
              {formatDateRange(tripDetails.start_date, tripDetails.end_date)}
            </span>
          </div>

          <div className="step3-review__field">
            <span className="step3-review__label">Privacidad:</span>
            <span className="step3-review__value">
              {tripDetails.privacy === 'public' ? 'Público' : 'Privado'}
            </span>
          </div>
        </section>

        {/* GPX File Section */}
        <section className="step3-review__section">
          <h3 className="step3-review__section-title">Archivo GPX</h3>

          <div className="step3-review__field">
            <span className="step3-review__label">Archivo:</span>
            <span className="step3-review__value">{gpxFile.name}</span>
          </div>

          <div className="step3-review__field">
            <span className="step3-review__label">Distancia:</span>
            <span className="step3-review__value">{telemetry.distance_km} km</span>
          </div>

          {telemetry.has_elevation && telemetry.elevation_gain !== null && (
            <div className="step3-review__field">
              <span className="step3-review__label">Desnivel positivo:</span>
              <span className="step3-review__value">{telemetry.elevation_gain} m</span>
            </div>
          )}

          {telemetry.has_elevation && telemetry.elevation_loss !== null && (
            <div className="step3-review__field">
              <span className="step3-review__label">Desnivel negativo:</span>
              <span className="step3-review__value">{telemetry.elevation_loss} m</span>
            </div>
          )}

          {telemetry.has_elevation && telemetry.max_elevation !== null && (
            <div className="step3-review__field">
              <span className="step3-review__label">Altitud máxima:</span>
              <span className="step3-review__value">{telemetry.max_elevation} m</span>
            </div>
          )}

          {telemetry.has_elevation && telemetry.min_elevation !== null && (
            <div className="step3-review__field">
              <span className="step3-review__label">Altitud mínima:</span>
              <span className="step3-review__value">{telemetry.min_elevation} m</span>
            </div>
          )}

          <div className="step3-review__field">
            <span className="step3-review__label">Dificultad:</span>
            <span className="step3-review__value">
              <DifficultyBadge difficulty={telemetry.difficulty} />
            </span>
          </div>
        </section>
      </div>

      {/* Actions */}
      <div className="step3-review__actions">
        <button
          type="button"
          onClick={onCancel}
          className="step3-review__button step3-review__button--secondary"
          disabled={isPublishing}
          aria-label="Cancelar asistente"
        >
          Cancelar
        </button>

        <div className="step3-review__actions-right">
          <button
            type="button"
            onClick={onPrevious}
            className="step3-review__button step3-review__button--secondary"
            disabled={isPublishing}
            aria-label="Volver al paso anterior"
          >
            Anterior
          </button>

          <button
            type="button"
            onClick={onPublish}
            className="step3-review__button step3-review__button--primary"
            disabled={isPublishing}
            aria-label={isPublishing ? 'Publicando viaje...' : 'Publicar viaje'}
          >
            {isPublishing ? (
              <>
                <span className="step3-review__spinner" aria-hidden="true"></span>
                Publicando...
              </>
            ) : (
              'Publicar Viaje'
            )}
          </button>
        </div>
      </div>

      {/* Live region for screen readers */}
      <div role="status" aria-live="polite" className="sr-only">
        {isPublishing && 'Publicando viaje, por favor espera...'}
      </div>
    </div>
  );
};
