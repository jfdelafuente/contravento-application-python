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
  tripId: _tripId,
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
  const [selectedPhoto, setSelectedPhoto] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const isEditMode = !!editingPOI;
  const maxNameLength = 100;
  const maxDescriptionLength = 500;
  const MAX_PHOTO_SIZE_MB = 5;

  // Load editing POI data
  useEffect(() => {
    if (editingPOI) {
      setName(editingPOI.name);
      setDescription(editingPOI.description || '');
      setPoiType(editingPOI.poi_type);
      setPhotoPreview(editingPOI.photo_url);
    }
  }, [editingPOI]);

  // Cleanup photo preview URL on unmount
  useEffect(() => {
    return () => {
      if (photoPreview && photoPreview.startsWith('blob:')) {
        URL.revokeObjectURL(photoPreview);
      }
    };
  }, [photoPreview]);

  const handlePhotoSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setLocalError('Solo se permiten archivos de imagen');
      return;
    }

    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setLocalError('Solo se permiten archivos JPEG, PNG y WebP');
      return;
    }

    // Validate file size
    const sizeMB = file.size / (1024 * 1024);
    if (sizeMB > MAX_PHOTO_SIZE_MB) {
      setLocalError(`La foto excede el tamaño máximo de ${MAX_PHOTO_SIZE_MB}MB`);
      return;
    }

    // Clear previous error
    setLocalError(null);

    // Revoke previous preview URL
    if (photoPreview && photoPreview.startsWith('blob:')) {
      URL.revokeObjectURL(photoPreview);
    }

    // Create preview
    const preview = URL.createObjectURL(file);
    setPhotoPreview(preview);
    setSelectedPhoto(file);
  };

  const handleRemovePhoto = () => {
    if (photoPreview && photoPreview.startsWith('blob:')) {
      URL.revokeObjectURL(photoPreview);
    }
    setPhotoPreview(null);
    setSelectedPhoto(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSelectPhotoClick = () => {
    fileInputRef.current?.click();
  };

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
        // Check if we're in wizard mode (temporary poi_id starts with "temp-")
        const isWizardMode = editingPOI?.poi_id.startsWith('temp-');

        // Determine photo value (for wizard mode):
        // - If new photo selected: use new photo
        // - If photo was removed: set to null
        // - If photo wasn't touched: undefined (preserve existing)
        let photoValue: File | null | undefined = undefined;
        if (isWizardMode) {
          if (selectedPhoto) {
            photoValue = selectedPhoto; // New photo selected
          } else if (photoPreview === null && editingPOI?.photo_url) {
            photoValue = null; // Photo was removed
          }
          // else: undefined (photo wasn't touched)
        }

        // Determine photo_url value (for published trips):
        // - If photo was removed in published trip: set to null
        // - If photo wasn't touched: undefined (preserve existing)
        let photoUrlValue: string | null | undefined = undefined;
        if (!isWizardMode) {
          // Detect if photo was removed: photoPreview is null AND POI had a photo before
          if (photoPreview === null && editingPOI?.photo_url) {
            photoUrlValue = null; // Photo was removed - tell backend to delete it
          }
          // else: undefined (photo wasn't touched or new photo will be uploaded separately)
        }

        // Update existing POI
        const updateData: POIUpdateInput = {
          name: trimmedName,
          description: trimmedDescription || null,
          poi_type: poiType,
          // Include photo field for both wizard and published trips
          // The parent component will handle uploading if needed
          photo: isWizardMode ? photoValue : selectedPhoto || undefined,
          // Include photo_url: null in published trips to delete photo
          photo_url: photoUrlValue,
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
          photo: selectedPhoto || undefined, // Include photo file if selected
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

    // Clean up photo
    if (photoPreview && photoPreview.startsWith('blob:')) {
      URL.revokeObjectURL(photoPreview);
    }
    setPhotoPreview(null);
    setSelectedPhoto(null);

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

          {/* Photo upload field (optional) */}
          <div className="poi-form-field">
            <label className="poi-form-label">
              Foto (opcional)
            </label>

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={handlePhotoSelect}
              style={{ display: 'none' }}
              disabled={isSubmitting}
            />

            {/* Photo preview or select button */}
            {photoPreview ? (
              <div className="poi-form-photo-preview">
                <img
                  src={photoPreview}
                  alt="Vista previa"
                  className="poi-form-photo-image"
                />
                <button
                  type="button"
                  className="poi-form-photo-remove"
                  onClick={handleRemovePhoto}
                  disabled={isSubmitting}
                  aria-label="Eliminar foto"
                >
                  ✕
                </button>
              </div>
            ) : (
              <button
                type="button"
                className="poi-form-photo-select"
                onClick={handleSelectPhotoClick}
                disabled={isSubmitting}
              >
                <svg
                  className="poi-form-photo-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span>Seleccionar foto</span>
                <span className="poi-form-photo-hint">
                  JPEG, PNG, WebP (máx. {MAX_PHOTO_SIZE_MB}MB)
                </span>
              </button>
            )}
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
