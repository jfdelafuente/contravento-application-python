/**
 * LocationConfirmModal component for confirming geocoded location selection
 * Feature: 010-reverse-geocoding
 * Task: T016
 *
 * Displays a modal with:
 * - Suggested place name from reverse geocoding
 * - Editable name input (User Story 3)
 * - Coordinates (latitude, longitude)
 * - Confirm/Cancel buttons
 */

import React, { useState, useEffect } from 'react';
import type { LocationSelection } from '../../types/geocoding';
import './LocationConfirmModal.css';

interface LocationConfirmModalProps {
  /** Location data from geocoding (or null if modal closed) */
  location: LocationSelection | null;
  /** Callback when user confirms location */
  onConfirm: (name: string, lat: number, lng: number) => void;
  /** Callback when user cancels */
  onCancel: () => void;
}

/**
 * Modal for confirming location selection with geocoded place name
 *
 * Features:
 * - Displays suggested place name from reverse geocoding
 * - Allows editing name before confirming (FR-012, FR-013)
 * - Shows loading state during geocoding
 * - Displays errors if geocoding fails
 * - Validates name (required, max 200 chars)
 *
 * Usage:
 * ```tsx
 * <LocationConfirmModal
 *   location={pendingLocation}
 *   onConfirm={(name, lat, lng) => addLocation(name, lat, lng)}
 *   onCancel={() => setPendingLocation(null)}
 * />
 * ```
 */
export const LocationConfirmModal: React.FC<LocationConfirmModalProps> = ({
  location,
  onConfirm,
  onCancel,
}) => {
  const [editedName, setEditedName] = useState('');

  // Update edited name when location changes
  useEffect(() => {
    if (location) {
      setEditedName(location.editedName || location.suggestedName);
    }
  }, [location]);

  if (!location) {
    return null; // Modal closed
  }

  const handleConfirm = () => {
    const finalName = editedName.trim();
    if (finalName) {
      onConfirm(finalName, location.latitude, location.longitude);
    }
  };

  const handleCancel = () => {
    setEditedName(''); // Reset state
    onCancel();
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Close modal if clicking outside (on overlay)
    if (e.target === e.currentTarget) {
      handleCancel();
    }
  };

  const isNameValid = editedName.trim().length > 0 && editedName.length <= 200;

  return (
    <div
      className="location-confirm-modal-overlay"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="location-modal-title"
      aria-describedby="location-modal-description"
    >
      <div className="location-confirm-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="location-confirm-modal-header">
          <h3 id="location-modal-title">
            <svg
              width="24"
              height="24"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
              style={{ color: '#3b82f6' }}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            Confirmar ubicación
          </h3>
          <button
            className="location-confirm-modal-close"
            onClick={handleCancel}
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="location-confirm-modal-content" id="location-modal-description">
          {location.isLoading ? (
            // Loading state
            <div className="location-confirm-modal-loading" role="status" aria-live="polite">
              <div className="spinner" aria-hidden="true" />
              <p>Obteniendo nombre del lugar...</p>
            </div>
          ) : location.hasError ? (
            // Error state
            <div className="location-confirm-modal-error" role="alert" aria-live="assertive">
              <svg
                className="error-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p>{location.errorMessage || 'Error al obtener el nombre del lugar'}</p>
              <p className="location-confirm-modal-fallback">
                Puedes ingresar un nombre manualmente
              </p>
            </div>
          ) : (
            // Success state
            <div className="location-confirm-modal-success">
              <svg
                className="success-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <p className="location-confirm-modal-address">
                {location.fullAddress}
              </p>
            </div>
          )}

          {/* Name input (User Story 3: Edit location name) */}
          <div className="location-confirm-modal-input-group">
            <label htmlFor="location-name">Nombre de la ubicación</label>
            <input
              id="location-name"
              type="text"
              value={editedName}
              onChange={(e) => setEditedName(e.target.value)}
              placeholder="Ingresa un nombre para esta ubicación"
              maxLength={200}
              disabled={location.isLoading}
              className={!isNameValid ? 'invalid' : ''}
              autoFocus
            />
            {editedName.length > 0 && (
              <span className="location-confirm-modal-char-count">
                {editedName.length}/200
              </span>
            )}
            {!isNameValid && editedName.length > 0 && (
              <span className="location-confirm-modal-error-text">
                El nombre no puede estar vacío
              </span>
            )}
          </div>

          {/* Coordinates display */}
          <div className="location-confirm-modal-coordinates">
            <span>
              <strong>Latitud:</strong> {location.latitude.toFixed(6)}
            </span>
            <span>
              <strong>Longitud:</strong> {location.longitude.toFixed(6)}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="location-confirm-modal-footer">
          <button
            className="location-confirm-modal-button cancel"
            onClick={handleCancel}
            aria-label="Cancelar y cerrar el modal"
            type="button"
          >
            Cancelar
          </button>
          <button
            className="location-confirm-modal-button confirm"
            onClick={handleConfirm}
            disabled={!isNameValid || location.isLoading}
            aria-label={!isNameValid ? "Confirmar ubicación (deshabilitado: nombre inválido)" : "Confirmar y guardar la ubicación"}
            aria-disabled={!isNameValid || location.isLoading}
            type="button"
          >
            Confirmar ubicación
          </button>
        </div>
      </div>
    </div>
  );
};
