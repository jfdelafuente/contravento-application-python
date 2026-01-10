/**
 * PhotoUploadSection Component
 *
 * Component for uploading and managing profile photos with file validation,
 * preview, progress tracking, and crop functionality.
 *
 * Features:
 * - Current photo preview with placeholder fallback
 * - File validation (JPG/PNG formats, max 5MB size)
 * - Upload progress bar with percentage indicator
 * - Change photo button to select new image
 * - Remove photo button (shown only when photo exists)
 * - Real-time validation error display
 * - Accessible controls with ARIA labels
 *
 * @component
 * @example
 * ```tsx
 * <PhotoUploadSection
 *   currentPhotoUrl={user.photo_url}
 *   onPhotoSelected={handleFileSelected}
 *   onRemovePhoto={handleRemovePhoto}
 *   uploadProgress={50}
 *   isUploading={true}
 * />
 * ```
 */

import React, { useState, useRef } from 'react';
import type { ChangeEvent } from 'react';
import { validatePhotoFile } from '../../utils/fileHelpers';
import './PhotoUploadSection.css';

/**
 * Props for PhotoUploadSection component
 */
export interface PhotoUploadSectionProps {
  /** Current photo URL to display in preview (optional) */
  currentPhotoUrl?: string;
  /** Callback invoked when user selects a file (before crop modal) */
  onPhotoSelected: (file: File) => void;
  /** Callback invoked when user clicks remove photo button */
  onRemovePhoto: () => void;
  /** Upload progress percentage (0-100), shown in progress bar */
  uploadProgress?: number;
  /** Whether upload is currently in progress (disables buttons and shows progress) */
  isUploading?: boolean;
}

export const PhotoUploadSection: React.FC<PhotoUploadSectionProps> = ({
  currentPhotoUrl,
  onPhotoSelected,
  onRemovePhoto,
  uploadProgress = 0,
  isUploading = false,
}) => {
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file
    const validation = validatePhotoFile(file);
    if (!validation.valid) {
      setValidationError(validation.error || 'Archivo inválido');
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    // Clear any previous errors
    setValidationError(null);

    // Pass file to parent for cropping
    onPhotoSelected(file);

    // Reset file input for next selection
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleChangePhotoClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemovePhotoClick = () => {
    setValidationError(null);
    onRemovePhoto();
  };

  return (
    <section className="photo-upload-section" aria-labelledby="photo-upload-title">
      <h2 id="photo-upload-title" className="section-title">Foto de Perfil</h2>

      <div className="photo-upload-content">
        {/* Current Photo Preview */}
        <div className="photo-preview-container">
          {currentPhotoUrl ? (
            <img
              src={currentPhotoUrl}
              alt="Foto de perfil actual"
              className="photo-preview"
            />
          ) : (
            <div className="photo-preview-placeholder">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="photo-placeholder-icon"
              >
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              <p className="photo-placeholder-text">Sin foto</p>
            </div>
          )}
        </div>

        {/* Upload Progress Bar (shown during upload) */}
        {isUploading && (
          <div className="upload-progress-container" role="status" aria-live="polite">
            <div className="upload-progress-bar" role="progressbar" aria-valuenow={uploadProgress} aria-valuemin={0} aria-valuemax={100}>
              <div
                className="upload-progress-fill"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <p className="upload-progress-text">Subiendo foto... {uploadProgress}%</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="photo-actions">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFileChange}
            className="photo-input-hidden"
            disabled={isUploading}
            aria-label="Seleccionar foto de perfil"
          />

          {/* Change Photo Button */}
          <button
            type="button"
            onClick={handleChangePhotoClick}
            className="btn-change-photo"
            disabled={isUploading}
            aria-label="Seleccionar nueva foto de perfil"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="btn-icon"
            >
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
            Cambiar foto
          </button>

          {/* Remove Photo Button (only shown if photo exists) */}
          {currentPhotoUrl && (
            <button
              type="button"
              onClick={handleRemovePhotoClick}
              className="btn-remove-photo"
              disabled={isUploading}
              aria-label="Eliminar foto de perfil actual"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="btn-icon"
              >
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <line x1="10" y1="11" x2="10" y2="17" />
                <line x1="14" y1="11" x2="14" y2="17" />
              </svg>
              Eliminar foto
            </button>
          )}
        </div>

        {/* Validation Error */}
        {validationError && (
          <p className="photo-error" role="alert">
            <span className="error-icon" aria-hidden="true">⚠</span>
            {validationError}
          </p>
        )}

        {/* Help Text */}
        <p className="photo-help-text">
          Formatos permitidos: JPG, PNG • Tamaño máximo: 5MB
        </p>
      </div>
    </section>
  );
};

export default PhotoUploadSection;
