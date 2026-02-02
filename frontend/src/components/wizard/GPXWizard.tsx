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

import React, { useState, useCallback, useRef } from 'react';
import toast from 'react-hot-toast';
import { useGPXWizard } from '../../hooks/useGPXWizard';
import { Step1Upload, type Step1UploadHandle } from './Step1Upload';
import { Step2Details } from './Step2Details';
import { Step3POIs } from './Step3POIs';
import { Step4Review } from './Step4Review';
import { createTripWithGPX } from '../../services/tripService';
import { createPOI, uploadPOIPhoto } from '../../services/poiService';
import type { GPXTelemetry } from '../../services/gpxWizardService';
import type { TripDetailsFormData } from '../../schemas/tripDetailsSchema';
import type { POICreateInput } from '../../types/poi';
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
 * Handles file upload, analysis, trip details, POI management, and review.
 *
 * Steps (Phase 2 - Option C):
 * 0. GPX Upload & Analysis + Map Preview
 * 1. Trip Details
 * 2. POI Management (Phase 8 - US5)
 * 3. Review & Publish (with complete telemetry)
 *
 * @param props - Component props
 */
export const GPXWizard: React.FC<GPXWizardProps> = ({ onSuccess, onError, onCancel }) => {
  const {
    currentStep,
    totalSteps,
    selectedFile,
    telemetryData,
    gpxTrackpoints,
    pois,
    progressPercentage,
    isStep1Complete,
    nextStep,
    prevStep,
    setSelectedFile,
    setTelemetryData,
    setGPXTrackpoints,
    setPOIs,
    resetWizard,
  } = useGPXWizard();

  const step1Ref = useRef<Step1UploadHandle>(null);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [tripDetails, setTripDetails] = useState<TripDetailsFormData | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishProgress, setPublishProgress] = useState<string | null>(null);

  /**
   * Handle Step 1 completion.
   * Store file, telemetry data, and trackpoints for map visualization.
   */
  const handleStep1Complete = useCallback(
    (file: File, telemetry: GPXTelemetry) => {
      console.log('🎯 [GPXWizard] handleStep1Complete called');
      console.log('📄 [GPXWizard] File:', file.name);
      console.log('📊 [GPXWizard] Telemetry:', telemetry);
      console.log('🗺️ [GPXWizard] Trackpoints to store:', telemetry.trackpoints ? telemetry.trackpoints.length : 'null');

      setSelectedFile(file);
      setTelemetryData(telemetry);
      // Store trackpoints for map visualization in POI step
      setGPXTrackpoints(telemetry.trackpoints || null);

      console.log('✅ [GPXWizard] State updated');
    },
    [setSelectedFile, setTelemetryData, setGPXTrackpoints]
  );

  /**
   * Handle Step 2 completion.
   * Store trip details data and advance to Step 3 (Map).
   */
  const handleStep2Complete = useCallback(
    (data: TripDetailsFormData) => {
      setTripDetails(data);
      nextStep();
    },
    [nextStep]
  );

  /**
   * Handle Step 3 completion (POI Management).
   * Store POIs data and advance to Step 4 (Review).
   */
  const handleStep3Complete = useCallback(
    (poisData: POICreateInput[]) => {
      setPOIs(poisData);
      nextStep();
    },
    [setPOIs, nextStep]
  );

  /**
   * Handle Remove GPX action from Step 2.
   * Removes uploaded file, telemetry, trackpoints, and trip details.
   * Returns to Step 1.
   */
  const handleRemoveGPX = useCallback(() => {
    setSelectedFile(null);
    setTelemetryData(null);
    setGPXTrackpoints(null);
    setTripDetails(null);
  }, [setSelectedFile, setTelemetryData, setGPXTrackpoints]);

  /**
   * Handle file removal.
   * Clear file, telemetry data, trackpoints, and reset Step1 hook state.
   */
  const handleFileRemove = useCallback(() => {
    // Reset Step1Upload hook state (telemetry, error, loading)
    step1Ref.current?.resetAnalysis();

    // Clear wizard state
    setSelectedFile(null);
    setTelemetryData(null);
    setGPXTrackpoints(null);
  }, [setSelectedFile, setTelemetryData, setGPXTrackpoints]);

  /**
   * Handle cancel button click.
   * Show confirmation if wizard has data.
   */
  const handleCancel = useCallback(() => {
    // If no data, cancel immediately
    if (!selectedFile && !telemetryData && !gpxTrackpoints && !tripDetails && pois.length === 0) {
      onCancel();
      return;
    }

    // Show confirmation dialog
    setShowCancelConfirm(true);
  }, [selectedFile, telemetryData, gpxTrackpoints, tripDetails, pois, onCancel]);

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
   * Creates trip with GPX file via backend API, then creates POIs sequentially (T094).
   */
  const handlePublish = useCallback(async () => {
    if (!selectedFile || !telemetryData || !tripDetails) {
      return;
    }

    setIsPublishing(true);
    setPublishProgress('Creando viaje...');

    try {
      // Step 1: Create trip with GPX file
      const trip = await createTripWithGPX(selectedFile, {
        title: tripDetails.title,
        description: tripDetails.description,
        start_date: tripDetails.start_date,
        end_date: tripDetails.end_date || undefined,
        privacy: tripDetails.privacy,
      });

      // Step 2: Create POIs sequentially (if any)
      if (pois.length > 0) {
        console.log(`🔄 [GPXWizard] Creating ${pois.length} POIs for trip ${trip.trip_id}...`);
        const createdPOIs: string[] = [];
        const failedPOIs: POICreateInput[] = [];
        const failedPhotoUploads: string[] = [];

        for (let i = 0; i < pois.length; i++) {
          const poi = pois[i];
          setPublishProgress(`Creando POI ${i + 1} de ${pois.length}...`);

          try {
            console.log(`  📍 [GPXWizard] Creating POI: ${poi.name}`);
            const createdPOI = await createPOI(trip.trip_id, {
              name: poi.name,
              description: poi.description,
              poi_type: poi.poi_type,
              latitude: poi.latitude,
              longitude: poi.longitude,
              sequence: poi.sequence,
            });
            console.log(`  ✅ [GPXWizard] POI created successfully: ${poi.name}`);

            // Upload photo if present (Feature 017 - FR-010)
            console.log(`  🔍 [GPXWizard] Checking photo for POI ${poi.name}:`, poi.photo ? `Has photo (${poi.photo.name}, ${poi.photo.size} bytes)` : 'No photo');
            if (poi.photo) {
              setPublishProgress(`Subiendo foto para POI ${i + 1}...`);

              try {
                console.log(`  📷 [GPXWizard] Uploading photo for POI: ${poi.name}`);
                console.log(`  📷 [GPXWizard] POI ID: ${createdPOI.poi_id}`);
                console.log(`  📷 [GPXWizard] Photo file:`, poi.photo.name, poi.photo.size, 'bytes');
                await uploadPOIPhoto(createdPOI.poi_id, poi.photo);
                console.log(`  ✅ [GPXWizard] Photo uploaded successfully for POI: ${poi.name}`);
              } catch (photoError: any) {
                console.error(`  ⚠️ [GPXWizard] Failed to upload photo for POI ${poi.name}:`, photoError);
                console.error(`  ⚠️ [GPXWizard] Error details:`, photoError.response?.data || photoError.message);

                // Notify user about failed photo upload
                toast(
                  `No se pudo subir la foto para "${poi.name}". El POI se creó sin imagen.`,
                  {
                    duration: 6000,
                    icon: '⚠️',
                  }
                );

                // Track failed photo upload
                failedPhotoUploads.push(poi.name);

                // Don't fail the whole POI creation if photo upload fails
                // POI is created, just without the photo
              }
            }

            createdPOIs.push(poi.name);
          } catch (poiError: any) {
            console.error(`  ❌ [GPXWizard] Failed to create POI:`, poi, poiError);
            failedPOIs.push(poi);
          }
        }

        // Log summary
        console.log(`📊 [GPXWizard] POI creation complete: ${createdPOIs.length}/${pois.length} successful`);
        if (failedPOIs.length > 0) {
          console.warn(`⚠️ [GPXWizard] ${failedPOIs.length} POIs failed:`, failedPOIs.map(p => p.name));
        }

        // Show summary of failed photo uploads
        if (failedPhotoUploads.length > 0) {
          toast.error(
            `${failedPhotoUploads.length} ${failedPhotoUploads.length === 1 ? 'foto no se pudo subir' : 'fotos no se pudieron subir'}. Puedes añadirlas después desde la página del viaje.`,
            { duration: 8000 }
          );
        }

        // Wait for DB consistency (ensure POIs are fully persisted before navigation)
        console.log('⏳ [GPXWizard] Waiting 500ms for DB consistency...');
        await new Promise(resolve => setTimeout(resolve, 500));

        // Navigate to trip detail page (POIs should be available now)
        console.log('✅ [GPXWizard] Navigating to trip detail page');
        onSuccess(trip);
      } else {
        // No POIs to create - success
        console.log('ℹ️ [GPXWizard] No POIs to create, navigating to trip detail');
        onSuccess(trip);
      }
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
      setPublishProgress(null);
    }
  }, [selectedFile, telemetryData, tripDetails, pois, onSuccess, onError]);

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

          {/* Step 3: POI Management */}
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
            <div className="wizard-step__label">Puntos de Interés</div>
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
          <Step1Upload ref={step1Ref} onComplete={handleStep1Complete} onFileRemove={handleFileRemove} />
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

        {/* Step 3: POI Management */}
        {currentStep === 2 && selectedFile && telemetryData && tripDetails && (
          <Step3POIs
            telemetry={telemetryData}
            gpxTrackpoints={gpxTrackpoints}
            tripDetails={tripDetails}
            initialPOIs={pois}
            onNext={handleStep3Complete}
            onPrevious={prevStep}
            onCancel={handleCancel}
          />
        )}

        {/* Step 4: Review */}
        {currentStep === 3 && selectedFile && telemetryData && tripDetails && (
          <Step4Review
            gpxFile={selectedFile}
            telemetry={telemetryData}
            tripDetails={tripDetails}
            pois={pois}
            onPublish={handlePublish}
            onPrevious={prevStep}
            onCancel={handleCancel}
            isPublishing={isPublishing}
          />
        )}

        {/* Publishing Progress Indicator */}
        {publishProgress && (
          <div className="gpx-wizard__publishing-overlay" role="status" aria-live="polite">
            <div className="gpx-wizard__publishing-dialog">
              <div className="gpx-wizard__publishing-spinner" aria-hidden="true">
                <div className="spinner"></div>
              </div>
              <p className="gpx-wizard__publishing-message">{publishProgress}</p>
            </div>
          </div>
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

          {/* File Info Preview (moved from uploader) */}
          {selectedFile && (
            <div className="gpx-wizard__file-badge">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className="gpx-wizard__file-badge-icon"
              >
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                <polyline points="13 2 13 9 20 9" />
              </svg>
              <span className="gpx-wizard__file-badge-name">{selectedFile.name}</span>
              <span className="gpx-wizard__file-badge-size">
                {selectedFile.size < 1024 * 1024
                  ? `${(selectedFile.size / 1024).toFixed(1)} KB`
                  : `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`}
              </span>
              <button
                type="button"
                onClick={handleFileRemove}
                className="gpx-wizard__file-badge-remove"
                aria-label="Eliminar archivo"
                title="Eliminar archivo"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
          )}

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
