/**
 * Step1Upload Component - GPX Upload & Analysis Step
 *
 * Wizard Step 1: Handles GPX file upload, analysis, and telemetry preview.
 * Integrates GPXWizardUploader with useGPXAnalysis hook.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T044
 *
 * @example
 * ```typescript
 * <Step1Upload
 *   onComplete={(file, telemetry) => {
 *     console.log('File analyzed:', file.name);
 *     console.log('Distance:', telemetry.distance_km, 'km');
 *   }}
 *   onFileRemove={() => {
 *     console.log('File removed');
 *   }}
 * />
 * ```
 */

import React, { useCallback, useEffect } from 'react';
import { GPXWizardUploader } from './GPXWizardUploader';
import { TelemetrySkeleton } from './TelemetrySkeleton';
import { useGPXAnalysis } from '../../hooks/useGPXAnalysis';
import { formatDifficulty, getDifficultyColor } from '../../services/gpxWizardService';
import type { GPXTelemetry } from '../../services/gpxWizardService';
import './Step1Upload.css';

/**
 * Props for Step1Upload component
 */
export interface Step1UploadProps {
  /** Callback when file upload and analysis complete successfully */
  onComplete: (file: File, telemetry: GPXTelemetry) => void;

  /** Callback when user removes the uploaded file */
  onFileRemove: () => void;
}

/**
 * Step 1: GPX Upload & Analysis
 *
 * Handles file upload, analysis, and displays telemetry preview.
 * Automatically analyzes uploaded GPX files and shows distance, elevation, difficulty.
 *
 * @param props - Component props
 */
export const Step1Upload: React.FC<Step1UploadProps> = ({ onComplete, onFileRemove }) => {
  const { analyzeFile, telemetry, isLoading, error, retry } = useGPXAnalysis();

  // Store the last uploaded file for retry
  const [currentFile, setCurrentFile] = React.useState<File | null>(null);

  /**
   * Handle file selection from uploader.
   * Automatically starts analysis.
   */
  const handleFileSelect = useCallback(
    async (file: File) => {
      setCurrentFile(file);
      await analyzeFile(file);
    },
    [analyzeFile]
  );

  /**
   * Handle file removal.
   * Clears current file and calls parent callback.
   */
  const handleFileRemove = useCallback(() => {
    setCurrentFile(null);
    onFileRemove();
  }, [onFileRemove]);

  /**
   * Call onComplete when analysis succeeds.
   */
  useEffect(() => {
    if (telemetry && currentFile) {
      onComplete(currentFile, telemetry);
    }
  }, [telemetry, currentFile, onComplete]);

  return (
    <div className="step1-upload">
      {/* Step Title */}
      <div className="step1-upload__header">
        <h2 className="step1-upload__title">Sube tu archivo GPX</h2>
        <p className="step1-upload__description">
          Selecciona un archivo GPX de tu recorrido en bicicleta. Lo analizaremos automáticamente
          para obtener la distancia, elevación y dificultad.
        </p>
      </div>

      {/* File Upload */}
      <GPXWizardUploader
        onFileSelect={handleFileSelect}
        onFileRemove={handleFileRemove}
        selectedFile={currentFile || undefined}
        isLoading={isLoading}
        error={error || undefined}
      />

      {/* Error State with Retry */}
      {error && (
        <div className="step1-upload__error-actions">
          <button
            type="button"
            onClick={retry}
            className="step1-upload__retry-button"
            aria-label="Reintentar análisis"
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Loading Skeleton (T098) */}
      {isLoading && <TelemetrySkeleton />}

      {/* Telemetry Preview */}
      {telemetry && !isLoading && !error && (
        <div
          className="step1-upload__telemetry"
          role="region"
          aria-label="Información del recorrido"
        >
          {/* Success Status for Screen Readers */}
          <div role="status" aria-live="polite" className="sr-only">
            Análisis completado correctamente
          </div>

          <h3 className="step1-upload__telemetry-title">Información del Recorrido</h3>

          <div className="step1-upload__telemetry-grid">
            {/* Distance */}
            <div className="step1-upload__telemetry-item">
              <div className="step1-upload__telemetry-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z"
                  />
                </svg>
              </div>
              <div className="step1-upload__telemetry-content">
                <div className="step1-upload__telemetry-label">Distancia Total</div>
                <div className="step1-upload__telemetry-value">{telemetry.distance_km} km</div>
              </div>
            </div>

            {/* Elevation Gain */}
            <div className="step1-upload__telemetry-item">
              <div className="step1-upload__telemetry-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941"
                  />
                </svg>
              </div>
              <div className="step1-upload__telemetry-content">
                <div className="step1-upload__telemetry-label">Desnivel Positivo</div>
                <div className="step1-upload__telemetry-value">
                  {telemetry.has_elevation && telemetry.elevation_gain !== null
                    ? `${telemetry.elevation_gain} m`
                    : 'Sin datos de elevación'}
                </div>
              </div>
            </div>

            {/* Max Elevation */}
            {telemetry.has_elevation && telemetry.max_elevation !== null && (
              <div className="step1-upload__telemetry-item">
                <div className="step1-upload__telemetry-icon">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.031.352 5.988 5.988 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L18.75 4.971zm-16.5.52c.99-.203 1.99-.377 3-.52m0 0l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.989 5.989 0 01-2.031.352 5.989 5.989 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L5.25 4.971z"
                    />
                  </svg>
                </div>
                <div className="step1-upload__telemetry-content">
                  <div className="step1-upload__telemetry-label">Altitud Máxima</div>
                  <div className="step1-upload__telemetry-value">{telemetry.max_elevation} m</div>
                </div>
              </div>
            )}

            {/* Difficulty */}
            <div className="step1-upload__telemetry-item">
              <div className="step1-upload__telemetry-icon">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z"
                  />
                </svg>
              </div>
              <div className="step1-upload__telemetry-content">
                <div className="step1-upload__telemetry-label">Dificultad</div>
                <div
                  className="step1-upload__telemetry-value step1-upload__telemetry-difficulty"
                  style={{ color: getDifficultyColor(telemetry.difficulty) }}
                >
                  {formatDifficulty(telemetry.difficulty)}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
