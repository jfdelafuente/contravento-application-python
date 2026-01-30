/**
 * GPXWizard Container Component - GPS Trip Creation Wizard
 *
 * Main container for multi-step GPS Trip Creation Wizard.
 * Manages wizard state, navigation, and step rendering.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T041
 *
 * @example
 * ```typescript
 * <GPXWizard
 *   onSuccess={(trip) => {
 *     toast.success('Viaje creado correctamente');
 *     navigate(`/trips/${trip.trip_id}`);
 *   }}
 *   onError={(error) => {
 *     toast.error(error.message);
 *   }}
 *   onCancel={() => {
 *     navigate('/trips');
 *   }}
 * />
 * ```
 */

import React, { useState, useCallback } from 'react';
import { useGPXWizard } from '../../hooks/useGPXWizard';
import { Step1Upload } from './Step1Upload';
import { Step2Details } from './Step2Details';
import { Step3Map } from '../trips/GPXWizard/Step3Map';
import { Step3Review } from './Step3Review';
import { createTripWithGPX } from '../../services/tripService';
import type { GPXTelemetry } from '../../services/gpxWizardService';
import type { TripDetailsFormData } from '../../schemas/tripDetailsSchema';
import type { Trip } from '../../types/trip';
import './GPXWizard.css';

/**
 * Wizard completion data
 */
export interface WizardCompletionData {
  /** Selected GPX file */
  file: File;

  /** Telemetry data from analysis */
  telemetry: GPXTelemetry;

  /** Trip details form data */
  tripDetails: TripDetailsFormData;
}

/**
 * Props for GPXWizard component
 */
export interface GPXWizardProps {
  /** Callback when trip is created successfully (T074) */
  onSuccess: (trip: Trip) => void;

  /** Callback when trip creation fails (T074) */
  onError: (error: { code: string; message: string; field?: string }) => void;

  /** Callback when user cancels wizard */
  onCancel: () => void;
}

/**
 * GPS Trip Creation Wizard Container
 *
 * Multi-step wizard for creating trips from GPX files.
 * Handles file upload, analysis, trip details, map visualization, and review.
 *
 * Steps:
 * 0. GPX Upload & Analysis
 * 1. Trip Details
 * 2. Map Visualization (Phase 7 - US4)
 * 3. Review & Publish
 *
 * @param props - Component props
 */
export const GPXWizard: React.FC<GPXWizardProps> = ({ onSuccess, onError, onCancel }) => {
  const {
    currentStep,
    totalSteps,
    selectedFile,
    telemetryData,
    progressPercentage,
    isStep1Complete,
    nextStep,
    prevStep,
    setSelectedFile,
    setTelemetryData,
    resetWizard,
  } = useGPXWizard();

  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [tripDetails, setTripDetails] = useState<TripDetailsFormData | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);

  /**
   * Handle Step 1 completion.
   * Store file and telemetry data.
   */
  const handleStep1Complete = useCallback(
    (file: File, telemetry: GPXTelemetry) => {
      setSelectedFile(file);
      setTelemetryData(telemetry);
    },
    [setSelectedFile, setTelemetryData]
  );

  /**
   * Handle Step 2 completion.
   * Store trip details data and advance to Step 3.
   */
  const handleStep2Complete = useCallback(
    (data: TripDetailsFormData) => {
      setTripDetails(data);
      nextStep();
    },
    [nextStep]
  );

  /**
   * Handle Remove GPX action from Step 2.
   * Removes uploaded file, telemetry, and trip details.
   * Returns to Step 1.
   */
  const handleRemoveGPX = useCallback(() => {
    setSelectedFile(null);
    setTelemetryData(null);
    setTripDetails(null);
  }, [setSelectedFile, setTelemetryData]);

  /**
   * Handle file removal.
   * Clear file and telemetry data.
   */
  const handleFileRemove = useCallback(() => {
    setSelectedFile(null);
    setTelemetryData(null);
  }, [setSelectedFile, setTelemetryData]);

  /**
   * Handle cancel button click.
   * Show confirmation if wizard has data.
   */
  const handleCancel = useCallback(() => {
    // If no data, cancel immediately
    if (!selectedFile && !telemetryData && !tripDetails) {
      onCancel();
      return;
    }

    // Show confirmation dialog
    setShowCancelConfirm(true);
  }, [selectedFile, telemetryData, tripDetails, onCancel]);

  /**
   * Confirm cancellation.
   * Reset wizard and call onCancel.
   */
  const confirmCancel = useCallback(() => {
    setShowCancelConfirm(false);
    resetWizard();
    onCancel();
  }, [resetWizard, onCancel]);

  /**
   * Decline cancellation.
   * Close confirmation dialog.
   */
  const declineCancel = useCallback(() => {
    setShowCancelConfirm(false);
  }, []);

  /**
   * Handle wizard completion (Publish button).
   * Creates trip with GPX file via backend API (T073, T074).
   */
  const handlePublish = useCallback(async () => {
    if (!selectedFile || !telemetryData || !tripDetails) {
      return;
    }

    setIsPublishing(true);

    try {
      // Call backend API to create trip with GPX file
      const trip = await createTripWithGPX(selectedFile, {
        title: tripDetails.title,
        description: tripDetails.description,
        start_date: tripDetails.start_date,
        end_date: tripDetails.end_date || undefined,
        privacy: tripDetails.privacy,
      });

      // Success - notify parent component
      onSuccess(trip);
    } catch (error: any) {
      // Error handling with Spanish messages (T074)
      let errorData = {
        code: 'UNKNOWN_ERROR',
        message: 'Error desconocido al crear el viaje',
        field: undefined as string | undefined,
      };

      if (error.response?.data?.error) {
        // Backend returned structured error
        errorData = error.response.data.error;
      } else if (error.response?.status === 413) {
        // File too large
        errorData = {
          code: 'FILE_TOO_LARGE',
          message: 'El archivo GPX es demasiado grande (máximo 10 MB)',
          field: 'gpx_file',
        };
      } else if (error.response?.status === 400) {
        // Bad request - validation error
        errorData = {
          code: 'VALIDATION_ERROR',
          message: error.response.data?.error?.message || 'Error de validación en los datos del viaje',
          field: error.response.data?.error?.field,
        };
      } else if (error.response?.status === 401) {
        // Unauthorized
        errorData = {
          code: 'UNAUTHORIZED',
          message: 'Debes iniciar sesión para crear un viaje',
          field: undefined,
        };
      } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        // Timeout
        errorData = {
          code: 'TIMEOUT',
          message: 'El servidor tardó demasiado en responder. Intenta de nuevo.',
          field: undefined,
        };
      } else if (!error.response) {
        // Network error
        errorData = {
          code: 'NETWORK_ERROR',
          message: 'No se pudo conectar con el servidor. Verifica tu conexión a internet.',
          field: undefined,
        };
      }

      // Notify parent component of error
      onError(errorData);
    } finally {
      setIsPublishing(false);
    }
  }, [selectedFile, telemetryData, tripDetails, onSuccess, onError]);

  return (
    <div className="gpx-wizard">
      {/* Wizard Header */}
      <div className="gpx-wizard__header">
        <h1 className="gpx-wizard__title">Crear Viaje desde GPX</h1>
        <p className="gpx-wizard__subtitle">
          Sube tu archivo GPX y completa los detalles para crear tu viaje
        </p>
      </div>

      {/* Step Indicator */}
      <nav className="gpx-wizard__steps" aria-label="Progreso del asistente">
        <div className="gpx-wizard__step-list">
          {/* Step 1: Upload */}
          <div
            className={`wizard-step ${currentStep === 0 ? 'wizard-step--active' : ''} ${
              isStep1Complete ? 'wizard-step--completed' : ''
            }`}
          >
            <div className="wizard-step__number">
              {isStep1Complete && currentStep > 0 ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                '1'
              )}
            </div>
            <div className="wizard-step__label">Archivo GPX</div>
          </div>

          {/* Step 2: Trip Details */}
          <div
            className={`wizard-step ${currentStep === 1 ? 'wizard-step--active' : ''} ${
              currentStep > 1 ? 'wizard-step--completed' : ''
            }`}
          >
            <div className="wizard-step__number">
              {currentStep > 1 ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                '2'
              )}
            </div>
            <div className="wizard-step__label">Detalles del Viaje</div>
          </div>

          {/* Step 3: Map Visualization */}
          <div
            className={`wizard-step ${currentStep === 2 ? 'wizard-step--active' : ''} ${
              currentStep > 2 ? 'wizard-step--completed' : ''
            }`}
          >
            <div className="wizard-step__number">
              {currentStep > 2 ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              ) : (
                '3'
              )}
            </div>
            <div className="wizard-step__label">Mapa</div>
          </div>

          {/* Step 4: Review */}
          <div className={`wizard-step ${currentStep === 3 ? 'wizard-step--active' : ''}`}>
            <div className="wizard-step__number">4</div>
            <div className="wizard-step__label">Revisar y Publicar</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="gpx-wizard__progress">
          <div
            className="gpx-wizard__progress-bar"
            style={{ width: `${progressPercentage}%` }}
            role="progressbar"
            aria-valuenow={progressPercentage}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Progreso del asistente"
          />
        </div>
        <div className="gpx-wizard__progress-text">{progressPercentage}%</div>
      </nav>

      {/* Step Content */}
      <main className="gpx-wizard__content" role="main">
        {/* Step 1: GPX Upload */}
        {currentStep === 0 && (
          <Step1Upload onComplete={handleStep1Complete} onFileRemove={handleFileRemove} />
        )}

        {/* Step 2: Trip Details */}
        {currentStep === 1 && selectedFile && telemetryData && (
          <Step2Details
            gpxFile={selectedFile}
            telemetry={telemetryData}
            onNext={handleStep2Complete}
            onPrevious={prevStep}
            onCancel={handleCancel}
            onRemoveGPX={handleRemoveGPX}
            initialData={tripDetails || undefined}
          />
        )}

        {/* Step 3: Map Visualization */}
        {currentStep === 2 && selectedFile && telemetryData && (
          <Step3Map
            telemetry={telemetryData}
            onBack={prevStep}
            onNext={nextStep}
          />
        )}

        {/* Step 4: Review */}
        {currentStep === 3 && selectedFile && telemetryData && tripDetails && (
          <Step3Review
            gpxFile={selectedFile}
            telemetry={telemetryData}
            tripDetails={tripDetails}
            onPublish={handlePublish}
            onPrevious={prevStep}
            onCancel={handleCancel}
            isPublishing={isPublishing}
          />
        )}

        {/* Announce step changes to screen readers */}
        <div role="status" aria-live="polite" className="sr-only">
          Paso {currentStep + 1} de {totalSteps}
        </div>
      </main>

      {/* Navigation Buttons - Only for Step 1 (Upload) */}
      {currentStep === 0 && (
        <div className="gpx-wizard__actions">
          <button
            type="button"
            onClick={handleCancel}
            className="gpx-wizard__button gpx-wizard__button--secondary"
            aria-label="Cancelar asistente"
          >
            Cancelar
          </button>

          <div className="gpx-wizard__actions-right">
            <button
              type="button"
              onClick={nextStep}
              className="gpx-wizard__button gpx-wizard__button--primary"
              disabled={!isStep1Complete}
              aria-label="Siguiente"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {/* Cancel Confirmation Dialog */}
      {showCancelConfirm && (
        <div
          className="gpx-wizard__dialog-overlay"
          onClick={declineCancel}
          role="dialog"
          aria-modal="true"
          aria-labelledby="cancel-dialog-title"
        >
          <div className="gpx-wizard__dialog" onClick={(e) => e.stopPropagation()}>
            <h3 id="cancel-dialog-title" className="gpx-wizard__dialog-title">
              ¿Seguro que quieres cancelar?
            </h3>
            <p className="gpx-wizard__dialog-text">
              Se perderán todos los datos ingresados en el asistente.
            </p>
            <div className="gpx-wizard__dialog-actions">
              <button
                type="button"
                onClick={declineCancel}
                className="gpx-wizard__button gpx-wizard__button--secondary"
                aria-label="No, continuar con el asistente"
              >
                No, continuar
              </button>
              <button
                type="button"
                onClick={confirmCancel}
                className="gpx-wizard__button gpx-wizard__button--danger"
                aria-label="Sí, cancelar el asistente"
              >
                Sí, cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
