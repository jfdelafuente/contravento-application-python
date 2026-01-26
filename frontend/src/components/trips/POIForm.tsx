/**
 * POIForm Component - Add/Edit Point of Interest (Feature 003 - US4: POIs)
 *
 * Features:
 * - Create new POIs by clicking on map
 * - Edit existing POIs (owner-only)
 * - Name, description, type selection
 * - Coordinates set via map click (read-only in form)
 * - Spanish labels and error messages
 * - Max 20 POIs per trip validation
 *
 * Related: FR-029, SC-029
 */

import React, { useState, useEffect } from 'react';
import { POI, POIType, POI_TYPE_LABELS, POICreateInput, POIUpdateInput } from '../../types/poi';
import './POIForm.css';

interface POIFormProps {
  /** Trip ID for creating new POI */
  tripId: string;

  /** POI being edited (null for create mode) */
  editingPOI?: POI | null;

  /** Coordinates from map click (for create mode) */
  coordinates?: { latitude: number; longitude: number } | null;

  /** Callback when POI is created */
  onPOICreated?: (poi: POI) => void;

  /** Callback when POI is updated */
  onPOIUpdated?: (poi: POI) => void;

  /** Callback to cancel form */
  onCancel: () => void;

  /** Callback to submit form */
  onSubmit: (data: POICreateInput | POIUpdateInput) => Promise<void>;

  /** Loading state from parent */
  isSubmitting?: boolean;

  /** Error message from parent */
  error?: string | null;
}

export const POIForm: React.FC<POIFormProps> = ({
  tripId,
  editingPOI,
  coordinates,
  onCancel,
  onSubmit,
  isSubmitting = false,
  error = null,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [poiType, setPoiType] = useState<POIType>(POIType.VIEWPOINT);
  const [localError, setLocalError] = useState<string | null>(null);

  const isEditMode = !!editingPOI;
  const maxNameLength = 100;
  const maxDescriptionLength = 500;

  // Load editing POI data
  useEffect(() => {
    if (editingPOI) {
      setName(editingPOI.name);
      setDescription(editingPOI.description || '');
      setPoiType(editingPOI.poi_type);
    }
  }, [editingPOI]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    // Validate name
    const trimmedName = name.trim();
    if (!trimmedName) {
      setLocalError('El nombre es obligatorio');
      return;
    }

    if (trimmedName.length > maxNameLength) {
      setLocalError(`El nombre debe tener máximo ${maxNameLength} caracteres`);
      return;
    }

    // Validate description (optional)
    const trimmedDescription = description.trim();
    if (trimmedDescription.length > maxDescriptionLength) {
      setLocalError(`La descripción debe tener máximo ${maxDescriptionLength} caracteres`);
      return;
    }

    // Validate coordinates for create mode
    if (!isEditMode && !coordinates) {
      setLocalError('Debes seleccionar una ubicación en el mapa');
      return;
    }

    try {
      if (isEditMode) {
        // Update existing POI
        const updateData: POIUpdateInput = {
          name: trimmedName,
          description: trimmedDescription || null,
          poi_type: poiType,
        };
        await onSubmit(updateData);
      } else {
        // Create new POI
        const createData: POICreateInput = {
          name: trimmedName,
          description: trimmedDescription || null,
          poi_type: poiType,
          latitude: coordinates!.latitude,
          longitude: coordinates!.longitude,
          sequence: 0, // Will be calculated by backend
        };
        await onSubmit(createData);
      }
    } catch (err) {
      // Error handled by parent
    }
  };

  const handleCancel = () => {
    setName('');
    setDescription('');
    setPoiType(POIType.VIEWPOINT);
    setLocalError(null);
    onCancel();
  };

  const displayError = error || localError;

  return (
    <div className="poi-form-overlay" onClick={handleCancel}>
      <div className="poi-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="poi-form-header">
          <h3 className="poi-form-title">
            {isEditMode ? 'Editar POI' : 'Añadir POI'}
          </h3>
          <button
            type="button"
            className="poi-form-close"
            onClick={handleCancel}
            aria-label="Cerrar formulario"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="poi-form">
          {/* Coordinates display (read-only) */}
          {!isEditMode && coordinates && (
            <div className="poi-form-field">
              <label className="poi-form-label">Ubicación</label>
              <p className="poi-form-coordinates">
                {coordinates.latitude.toFixed(5)}, {coordinates.longitude.toFixed(5)}
              </p>
            </div>
          )}

          {/* Name field */}
          <div className="poi-form-field">
            <label htmlFor="poi-name" className="poi-form-label">
              Nombre <span className="poi-form-required">*</span>
            </label>
            <input
              id="poi-name"
              type="text"
              className="poi-form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Mirador del Valle"
              maxLength={maxNameLength}
              disabled={isSubmitting}
              required
              aria-describedby={displayError ? 'poi-error' : undefined}
              aria-invalid={!!displayError}
            />
            <span className="poi-form-hint">
              {name.length}/{maxNameLength} caracteres
            </span>
          </div>

          {/* POI Type dropdown */}
          <div className="poi-form-field">
            <label htmlFor="poi-type" className="poi-form-label">
              Tipo <span className="poi-form-required">*</span>
            </label>
            <select
              id="poi-type"
              className="poi-form-select"
              value={poiType}
              onChange={(e) => setPoiType(e.target.value as POIType)}
              disabled={isSubmitting}
              required
            >
              {Object.values(POIType).map((type) => (
                <option key={type} value={type}>
                  {POI_TYPE_LABELS[type]}
                </option>
              ))}
            </select>
          </div>

          {/* Description field (optional) */}
          <div className="poi-form-field">
            <label htmlFor="poi-description" className="poi-form-label">
              Descripción (opcional)
            </label>
            <textarea
              id="poi-description"
              className="poi-form-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Un mirador impresionante con vistas a todo el valle..."
              rows={4}
              maxLength={maxDescriptionLength}
              disabled={isSubmitting}
            />
            <span className="poi-form-hint">
              {description.length}/{maxDescriptionLength} caracteres
            </span>
          </div>

          {/* Error message */}
          {displayError && (
            <div id="poi-error" className="poi-form-error" role="alert">
              {displayError}
            </div>
          )}

          {/* Actions */}
          <div className="poi-form-actions">
            <button
              type="button"
              onClick={handleCancel}
              className="poi-form-cancel"
              disabled={isSubmitting}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="poi-form-submit"
              disabled={isSubmitting || !name.trim()}
            >
              {isSubmitting
                ? 'Guardando...'
                : isEditMode
                ? 'Guardar cambios'
                : 'Añadir POI'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
