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

import React, { useCallback, useEffect, useImperativeHandle, forwardRef } from 'react';
import { GPXWizardUploader } from './GPXWizardUploader';
import { TelemetrySkeleton } from './TelemetrySkeleton';
import { MapPreview } from './MapPreview';
import { useGPXAnalysis } from '../../hooks/useGPXAnalysis';
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
 * Ref handle for Step1Upload component
 */
export interface Step1UploadHandle {
  /** Reset hook state (telemetry, error, loading) */
  resetAnalysis: () => void;
}

/**
 * Step 1: GPX Upload & Analysis
 *
 * Handles file upload, analysis, and displays telemetry preview.
 * Automatically analyzes uploaded GPX files and shows distance, elevation, difficulty.
 *
 * @param props - Component props
 * @param ref - Ref handle to expose resetAnalysis function
 */
export const Step1Upload = forwardRef<Step1UploadHandle, Step1UploadProps>(
  ({ onComplete, onFileRemove }, ref) => {
    const { analyzeFile, telemetry, isLoading, error, retry, reset } = useGPXAnalysis();

    // Store the last uploaded file for retry
    const [currentFile, setCurrentFile] = React.useState<File | null>(null);

    // Expose resetAnalysis function to parent via ref
    useImperativeHandle(ref, () => ({
      resetAnalysis: () => {
        setCurrentFile(null);
        reset();
      },
    }));

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
   * Clears current file, resets hook state, and calls parent callback.
   */
  const handleFileRemove = useCallback(() => {
    setCurrentFile(null);
    reset(); // Clear telemetry, error, and loading state from hook
    onFileRemove();
  }, [onFileRemove, reset]);

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
      {/* Step Title - Only show when no file is uploaded */}
      {!telemetry && (
        <div className="step1-upload__header">
          <h2 className="step1-upload__title">Sube tu archivo GPX</h2>
          <p className="step1-upload__description">
            Selecciona un archivo GPX de tu recorrido en bicicleta. Lo analizaremos automáticamente
            para obtener la distancia, elevación y dificultad.
          </p>
        </div>
      )}

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

      {/* Suggested Title & Map Preview - PHASE 2 OPTIMIZED */}
      {telemetry && !isLoading && !error && (
        <div
          className="step1-upload__preview"
          role="region"
          aria-label="Vista previa del recorrido"
        >
          {/* Success Status for Screen Readers */}
          <div role="status" aria-live="polite" className="sr-only">
            Análisis completado correctamente
          </div>

          {/* Suggested Title */}
          <div className="step1-upload__suggested-title">
            <h3>Título Sugerido</h3>
            <p className="step1-upload__suggested-title-value">{telemetry.suggested_title}</p>
            <small className="step1-upload__suggested-title-hint">
              Podrás editarlo en el siguiente paso
            </small>
          </div>

          {/* Map Preview */}
          {telemetry.trackpoints && telemetry.trackpoints.length > 0 && (
            <MapPreview trackpoints={telemetry.trackpoints} title={telemetry.suggested_title} />
          )}
        </div>
      )}
    </div>
  );
});

Step1Upload.displayName = 'Step1Upload';
