/**
 * Step3POIs Component (Feature 017 - Phase 8 - US5)
 *
 * POI management step of the GPS Trip Creation Wizard.
 * Allows users to add up to 6 Points of Interest to their trip.
 *
 * Tasks:
 * - T088: Component implementation with UI structure
 * - T089: Add POI button with counter
 * - T090: Map click handler
 * - T091: POI markers
 * - T092: Disable button at 6 POIs
 */

import React, { useState, useCallback, useEffect } from 'react';
import type { GPXTelemetry } from '../../types/gpxWizard';
import type { TripDetailsFormData } from '../../schemas/tripDetailsSchema';
import type { POICreateInput, POIUpdateInput } from '../../types/poi';
import { POIType, POI_TYPE_EMOJI, POI_TYPE_LABELS } from '../../types/poi';
import { TripMap } from '../trips/TripMap';
import { POIForm } from '../trips/POIForm';
import SkeletonLoader from '../common/SkeletonLoader';
import './Step3POIs.css';

/**
 * Maximum POIs per trip (enforced by backend)
 */
const MAX_POIS = 6;

interface Step3POIsProps {
  /** GPX telemetry metrics from wizard analysis */
  telemetry: GPXTelemetry;

  /** Trip details from Step 2 */
  tripDetails: TripDetailsFormData;

  /** Initial POIs (if user navigates back from review) */
  initialPOIs?: POICreateInput[];

  /** Callback to proceed to next step (Step 4: Review) */
  onNext: (pois: POICreateInput[]) => void;

  /** Callback to go back to previous step (Step 2: Map) */
  onPrevious: () => void;

  /** Callback when user cancels wizard */
  onCancel: () => void;
}

export const Step3POIs: React.FC<Step3POIsProps> = ({
  telemetry,
  tripDetails,
  initialPOIs = [],
  onNext,
  onPrevious,
  onCancel,
}) => {
  // POI state management
  const [pois, setPOIs] = useState<POICreateInput[]>(initialPOIs);
  const [isAddingPOI, setIsAddingPOI] = useState(false);
  const [showPOIForm, setShowPOIForm] = useState(false);
  const [editingPOI, setEditingPOI] = useState<POICreateInput | null>(null);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [selectedCoordinates, setSelectedCoordinates] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);

  // Delete confirmation state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deletingIndex, setDeletingIndex] = useState<number | null>(null);

  // Map loading state (T098 - Phase 9)
  const [isMapLoading, setIsMapLoading] = useState(true);

  /**
   * Hide map skeleton after brief delay for map initialization (T098)
   */
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsMapLoading(false);
    }, 500); // 500ms delay for map to initialize

    return () => clearTimeout(timer);
  }, []);

  /**
   * Handle Escape key to close modals (T100 - Phase 9)
   */
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' || event.key === 'Esc') {
        // Close POI form if open
        if (showPOIForm) {
          event.preventDefault();
          setShowPOIForm(false);
          setEditingPOI(null);
          setEditingIndex(null);
          setSelectedCoordinates(null);
          setIsAddingPOI(false);
          return;
        }

        // Close delete confirmation dialog if open
        if (showDeleteConfirm) {
          event.preventDefault();
          setShowDeleteConfirm(false);
          setDeletingIndex(null);
          return;
        }
      }
    };

    // Add event listener
    document.addEventListener('keydown', handleKeyDown);

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showPOIForm, showDeleteConfirm]);

  /**
   * Handle "Añadir POI" button click (T089)
   * Enables map click mode
   */
  const handleAddClick = useCallback(() => {
    if (pois.length >= MAX_POIS) {
      // Show toast error
      const event = new CustomEvent('show-toast', {
        detail: {
          message: `Máximo ${MAX_POIS} POIs por viaje`,
          type: 'error',
        },
      });
      window.dispatchEvent(event);
      return;
    }

    setIsAddingPOI(true);
  }, [pois.length]);

  /**
   * Handle map click (T090)
   * Opens POI form with coordinates
   */
  const handleMapClick = useCallback(
    (lat: number, lng: number) => {
      if (!isAddingPOI) return;

      setSelectedCoordinates({ latitude: lat, longitude: lng });
      setShowPOIForm(true);
      setIsAddingPOI(false); // Disable click mode
    },
    [isAddingPOI]
  );

  /**
   * Handle POI form submit (T093)
   * Adds or updates POI in list (wizard mode - no API calls)
   */
  const handlePOISubmit = useCallback(
    async (data: POICreateInput | POIUpdateInput) => {
      if (editingIndex !== null) {
        // Update existing POI (merge update data with existing coordinates)
        const updated = [...pois];
        updated[editingIndex] = {
          ...updated[editingIndex],
          ...(data as POIUpdateInput),
          sequence: editingIndex,
        };
        setPOIs(updated);
      } else {
        // Add new POI
        setPOIs([...pois, { ...(data as POICreateInput), sequence: pois.length }]);
      }

      // Close form and reset state
      setShowPOIForm(false);
      setEditingPOI(null);
      setEditingIndex(null);
      setSelectedCoordinates(null);
    },
    [pois, editingIndex]
  );

  /**
   * Handle POI edit button click
   * Opens form with existing POI data
   */
  const handleEdit = useCallback((index: number) => {
    const poi = pois[index];
    setEditingPOI(poi);
    setEditingIndex(index);
    setSelectedCoordinates({ latitude: poi.latitude, longitude: poi.longitude });
    setShowPOIForm(true);
  }, [pois]);

  /**
   * Handle POI delete button click
   * Shows confirmation dialog
   */
  const handleDeleteClick = useCallback((index: number) => {
    setDeletingIndex(index);
    setShowDeleteConfirm(true);
  }, []);

  /**
   * Confirm POI deletion
   * Removes POI from list and map
   */
  const confirmDelete = useCallback(() => {
    if (deletingIndex === null) return;

    // Remove POI and resequence remaining
    const updated = pois
      .filter((_, i) => i !== deletingIndex)
      .map((poi, index) => ({ ...poi, sequence: index }));

    setPOIs(updated);
    setShowDeleteConfirm(false);
    setDeletingIndex(null);
  }, [pois, deletingIndex]);

  /**
   * Cancel POI deletion
   */
  const cancelDelete = useCallback(() => {
    setShowDeleteConfirm(false);
    setDeletingIndex(null);
  }, []);

  /**
   * Handle "Siguiente" button
   * Advances to Step 4 (Review) with POIs
   */
  const handleNext = useCallback(() => {
    onNext(pois);
  }, [pois, onNext]);

  /**
   * Handle "Omitir" button
   * Skips POI addition and advances to review with 0 POIs
   */
  const handleSkip = useCallback(() => {
    onNext([]);
  }, [onNext]);

  return (
    <div className="step3-pois">
      {/* Step Header */}
      <header className="step3-pois__header">
        <h2 className="step3-pois__title">Puntos de Interés</h2>
        <p className="step3-pois__description">
          Marca hasta 6 lugares destacados en tu ruta (opcional)
        </p>
      </header>

      {/* Add POI Button with Counter (T089) */}
      <div className="step3-pois__controls">
        <button
          type="button"
          onClick={handleAddClick}
          disabled={pois.length >= MAX_POIS}
          className={`step3-pois__add-button ${
            pois.length >= MAX_POIS ? 'step3-pois__add-button--disabled' : ''
          }`}
          aria-label={
            pois.length >= MAX_POIS
              ? `Límite alcanzado: ${pois.length} de ${MAX_POIS} POIs`
              : `Añadir punto de interés (${pois.length} de ${MAX_POIS})`
          }
        >
          {pois.length >= MAX_POIS
            ? `Límite alcanzado (${pois.length}/${MAX_POIS})`
            : `Añadir POI (${pois.length}/${MAX_POIS})`}
        </button>

        {/* Click mode indicator */}
        {isAddingPOI && (
          <p className="step3-pois__click-hint">
            Haz clic en el mapa para añadir un punto de interés
          </p>
        )}
      </div>

      {/* Interactive Map (T090, T091) */}
      <div
        className={`step3-pois__map-container ${
          isAddingPOI ? 'map-click-mode' : ''
        }`}
        data-testid="trip-map-container"
        role="region"
        aria-label={isAddingPOI ? "Mapa interactivo - Haz clic para añadir punto de interés" : "Mapa con puntos de interés"}
      >
        {/* Map Loading Skeleton (T098 - Phase 9) */}
        {isMapLoading && (
          <SkeletonLoader
            variant="rect"
            width="100%"
            height="400px"
            className="step3-pois__map-skeleton"
          />
        )}

        {/* TODO: Full GPX route visualization will be added in future phase */}
        {/* For now, map shows POI markers only (GPX trackpoints not available in wizard telemetry) */}
        {!isMapLoading && (
          <TripMap
          locations={[]}  // No text locations in wizard
          tripTitle={tripDetails.title}
          hasGPX={false}  // GPX route not displayed in POI step (shown in Step 2)
          isEditMode={isAddingPOI}
          onMapClick={handleMapClick}
          pois={pois.map((poi, index) => ({
            // Convert POICreateInput to POI for display
            poi_id: `temp-${index}`,  // Temporary ID for wizard
            trip_id: '',  // No trip yet
            name: poi.name,
            description: poi.description || null,
            poi_type: poi.poi_type,
            latitude: poi.latitude,
            longitude: poi.longitude,
            distance_from_start_km: poi.distance_from_start_km || null,
            photo_url: poi.photo_url || null,
            sequence: poi.sequence,
            created_at: new Date().toISOString(),
          }))}
          isOwner={true}  // User is creating this trip
          onPOIEdit={(poi) => {
            // Find POI index by sequence
            const index = pois.findIndex(p => p.sequence === poi.sequence);
            if (index !== -1) {
              handleEdit(index);
            }
          }}
          onPOIDelete={(poiId) => {
            // Extract index from temporary ID (format: "temp-0", "temp-1", etc.)
            const index = parseInt(poiId.replace('temp-', ''), 10);
            if (!isNaN(index) && index >= 0 && index < pois.length) {
              handleDeleteClick(index);
            }
          }}
          />
        )}
      </div>

      {/* POI List (T088) */}
      {pois.length > 0 && (
        <section className="step3-pois__list-section">
          <h3 className="step3-pois__list-title">
            Puntos de interés ({pois.length})
          </h3>
          <ul className="step3-pois__list">
            {pois.map((poi, index) => (
              <li key={index} className="poi-item">
                <div className="poi-item__icon">
                  <span role="img" aria-label={POI_TYPE_LABELS[poi.poi_type]}>
                    {POI_TYPE_EMOJI[poi.poi_type]}
                  </span>
                </div>
                <div className="poi-item__content">
                  <h4 className="poi-item__name">{poi.name}</h4>
                  <p className="poi-item__type">{POI_TYPE_LABELS[poi.poi_type]}</p>
                  {poi.description && (
                    <p className="poi-item__description">{poi.description}</p>
                  )}
                </div>
                <div className="poi-item__actions">
                  <button
                    type="button"
                    onClick={() => handleEdit(index)}
                    className="poi-item__button poi-item__button--edit"
                    aria-label={`Editar ${poi.name}`}
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDeleteClick(index)}
                    className="poi-item__button poi-item__button--delete"
                    aria-label={`Eliminar ${poi.name}`}
                  >
                    Eliminar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Screen reader announcements */}
      <div role="status" aria-live="polite" className="sr-only">
        {pois.length > 0 && `${pois.length} POI${pois.length > 1 ? 's' : ''} agregado${pois.length > 1 ? 's' : ''}`}
      </div>

      {/* Navigation Buttons (T088) */}
      <nav className="step3-pois__navigation" aria-label="Navegación del asistente">
        <button
          type="button"
          onClick={onPrevious}
          className="step3-pois__button step3-pois__button--secondary"
          aria-label="Volver al paso anterior (Mapa)"
        >
          Atrás
        </button>

        <div className="step3-pois__navigation-right">
          <button
            type="button"
            onClick={handleSkip}
            className="step3-pois__button step3-pois__button--tertiary"
            aria-label="Omitir puntos de interés y continuar"
          >
            Omitir
          </button>

          <button
            type="button"
            onClick={handleNext}
            className="step3-pois__button step3-pois__button--primary"
            aria-label={`Continuar a revisión con ${pois.length} ${pois.length === 1 ? 'punto' : 'puntos'} de interés`}
          >
            Siguiente
          </button>
        </div>
      </nav>

      {/* POIForm Modal (T093) */}
      {showPOIForm && (
        <POIForm
          tripId=""  // Empty string - trip doesn't exist yet in wizard
          editingPOI={
            editingPOI
              ? {
                  // Convert POICreateInput to POI for editing
                  poi_id: `temp-${editingIndex}`,
                  trip_id: '',
                  name: editingPOI.name,
                  description: editingPOI.description || null,
                  poi_type: editingPOI.poi_type,
                  latitude: editingPOI.latitude,
                  longitude: editingPOI.longitude,
                  distance_from_start_km: editingPOI.distance_from_start_km || null,
                  photo_url: editingPOI.photo_url || null,
                  sequence: editingPOI.sequence,
                  created_at: new Date().toISOString(),
                }
              : null
          }
          coordinates={selectedCoordinates}
          onCancel={() => {
            setShowPOIForm(false);
            setEditingPOI(null);
            setEditingIndex(null);
            setSelectedCoordinates(null);
          }}
          onSubmit={handlePOISubmit}
          isSubmitting={false}
          error={null}
        />
      )}

      {/* Delete Confirmation Dialog (T088) */}
      {showDeleteConfirm && deletingIndex !== null && (
        <div
          className="delete-dialog-overlay"
          onClick={cancelDelete}
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-dialog-title"
        >
          <div
            className="delete-dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="delete-dialog-icon">
              <svg
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
            </div>
            <h3 id="delete-dialog-title" className="delete-dialog-title">
              ¿Eliminar POI?
            </h3>
            <p className="delete-dialog-text">
              ¿Seguro que quieres eliminar este POI? Esta acción no se puede
              deshacer.
            </p>
            <div className="delete-dialog-actions">
              <button
                type="button"
                onClick={cancelDelete}
                className="delete-dialog-button delete-dialog-button--secondary"
                aria-label="Cancelar eliminación del POI"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={confirmDelete}
                className="delete-dialog-button delete-dialog-button--danger"
                aria-label={`Confirmar eliminación de ${pois[deletingIndex]?.name || 'POI'}`}
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
