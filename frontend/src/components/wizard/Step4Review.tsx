/**
 * Step4Review Component - Review and Publish
 *
 * Wizard Step 4 (was Step 3): Displays summary of all wizard data before publishing.
 * Shows trip details, GPX info, telemetry, POIs, and publish button.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 8 (POI Management)
 * Tasks: T094, Rename Step3Review → Step4Review
 *
 * @example
 * ```typescript
 * <Step4Review
 *   gpxFile={file}
 *   telemetry={telemetry}
 *   tripDetails={tripDetails}
 *   pois={pois}
 *   onPublish={() => console.log('Publishing...')}
 *   onPrevious={() => console.log('Previous')}
 *   onCancel={() => console.log('Cancel')}
 *   isPublishing={false}
 * />
 * ```
 */

import React from 'react';
import { MetricGroup } from './MetricGroup';
import { MetricCard } from './MetricCard';
import { formatDifficulty } from '../../services/gpxWizardService';
import { POI_TYPE_EMOJI, POI_TYPE_LABELS } from '../../types/poi';
import type { GPXTelemetry } from '../../services/gpxWizardService';
import type { TripDetailsFormData } from '../../schemas/tripDetailsSchema';
import type { POICreateInput } from '../../types/poi';
import './Step3Review.css'; // Reuse existing styles

/**
 * Props for Step4Review component
 */
export interface Step4ReviewProps {
  /** Uploaded GPX file */
  gpxFile: File;

  /** Telemetry data from GPX analysis */
  telemetry: GPXTelemetry;

  /** Trip details form data */
  tripDetails: TripDetailsFormData;

  /** POIs to be created with the trip */
  pois: POICreateInput[];

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
 * Step 4: Review and Publish
 *
 * Displays comprehensive summary of all wizard data:
 * - Trip details (title, description, dates, privacy)
 * - GPX file info (filename, distance, elevation, difficulty)
 * - POIs (if any) with emoji icons and types
 * - Publish button with loading state
 *
 * @param props - Component props
 */
export const Step4Review: React.FC<Step4ReviewProps> = ({
  gpxFile,
  telemetry,
  tripDetails,
  pois,
  onPublish,
  onPrevious,
  onCancel,
  isPublishing,
}) => {
  return (
    <div className="step3-review" data-testid="step4-review">
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

        {/* GPX File Info Section */}
        <section className="step3-review__section">
          <h3 className="step3-review__section-title">Archivo GPX</h3>

          <div className="step3-review__field">
            <span className="step3-review__label">Archivo:</span>
            <span className="step3-review__value">{gpxFile.name}</span>
          </div>
        </section>

        {/* Telemetry Section - Complete Metrics (Phase 2 - Option C) */}
        <section className="step3-review__section step3-review__section--full-width">
          <h3 className="step3-review__section-title">Telemetría del Recorrido</h3>

          {/* Group 1: Distancia */}
          <MetricGroup title="Distancia">
            <MetricCard
              label="Distancia Total"
              value={`${telemetry.distance_km.toFixed(1)} km`}
              variant="primary"
              size="large"
            />
          </MetricGroup>

          {/* Group 2: Desnivel (if elevation data available) */}
          {telemetry.has_elevation && (
            <MetricGroup title="Desnivel">
              <MetricCard
                label="Desnivel Positivo (+)"
                value={telemetry.elevation_gain !== null ? `${telemetry.elevation_gain} m` : 'N/A'}
                variant="success"
              />
              <MetricCard
                label="Desnivel Negativo (-)"
                value={telemetry.elevation_loss !== null ? `${telemetry.elevation_loss} m` : 'N/A'}
              />
            </MetricGroup>
          )}

          {/* Group 3: Altitudes (if elevation data available) */}
          {telemetry.has_elevation && (
            <MetricGroup title="Altitudes">
              <MetricCard
                label="Altitud Máxima"
                value={telemetry.max_elevation !== null ? `${telemetry.max_elevation} m` : 'N/A'}
              />
              <MetricCard
                label="Altitud Mínima"
                value={telemetry.min_elevation !== null ? `${telemetry.min_elevation} m` : 'N/A'}
              />
            </MetricGroup>
          )}

          {/* Group 4: Dificultad */}
          <MetricGroup title="Dificultad">
            <MetricCard
              label="Nivel de Dificultad"
              value={formatDifficulty(telemetry.difficulty)}
              size="large"
              variant={
                telemetry.difficulty === 'easy'
                  ? 'success'
                  : telemetry.difficulty === 'moderate'
                  ? 'default'
                  : 'warning'
              }
            />
          </MetricGroup>

          {/* No elevation data message */}
          {!telemetry.has_elevation && (
            <div className="step3-review__no-elevation">
              <p>
                ℹ️ Este archivo GPX no contiene datos de elevación. Solo se mostrará la
                distancia.
              </p>
            </div>
          )}
        </section>

        {/* POI Section (NEW) */}
        {pois.length > 0 && (
          <section className="step3-review__section">
            <h3 className="step3-review__section-title">Puntos de Interés ({pois.length})</h3>

            <div className="step3-review__pois">
              {pois.map((poi, index) => (
                <div key={index} className="step3-review__poi-item">
                  <span className="step3-review__poi-icon" aria-hidden="true">
                    {POI_TYPE_EMOJI[poi.poi_type]}
                  </span>
                  <div className="step3-review__poi-details">
                    <strong className="step3-review__poi-name">{poi.name}</strong>
                    <span className="step3-review__poi-type">
                      {POI_TYPE_LABELS[poi.poi_type]}
                    </span>
                    {poi.description && (
                      <p className="step3-review__poi-description">
                        {truncateDescription(poi.description, 20)}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
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
