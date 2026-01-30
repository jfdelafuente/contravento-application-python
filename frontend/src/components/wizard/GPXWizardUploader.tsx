/**
 * GPXWizardUploader Component
 *
 * Drag-and-drop file upload component for GPX Trip Creation Wizard.
 *
 * Features:
 * - Drag-and-drop file upload
 * - File validation (max 10MB, .gpx extension only)
 * - Visual feedback during drag
 * - File preview with size display
 * - Remove file action
 * - Loading state during analysis
 * - Error display
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T038
 */

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import './GPXWizardUploader.css';

interface GPXWizardUploaderProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  selectedFile?: File;
  isLoading?: boolean;
  error?: string;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes
const ACCEPTED_EXTENSIONS = ['.gpx'];

export const GPXWizardUploader: React.FC<GPXWizardUploaderProps> = ({
  onFileSelect,
  onFileRemove,
  selectedFile,
  isLoading = false,
  error,
}) => {
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateFile = useCallback((file: File): string | null => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return 'El archivo es demasiado grande. Tamaño máximo: 10MB';
    }

    // Check file extension (case insensitive)
    const fileName = file.name.toLowerCase();
    const hasValidExtension = ACCEPTED_EXTENSIONS.some((ext) => fileName.endsWith(ext));

    if (!hasValidExtension) {
      return 'Solo se aceptan archivos .gpx';
    }

    return null;
  }, []);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (isLoading) return;

      // Clear previous validation error
      setValidationError(null);

      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      const error = validateFile(file);

      if (error) {
        setValidationError(error);
        return;
      }

      onFileSelect(file);
    },
    [isLoading, validateFile, onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/gpx+xml': ACCEPTED_EXTENSIONS,
      'application/xml': ACCEPTED_EXTENSIONS,
      'text/xml': ACCEPTED_EXTENSIONS,
    },
    multiple: false,
    disabled: isLoading,
  });

  const handleRemove = () => {
    setValidationError(null);
    onFileRemove();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const displayError = error || validationError;

  return (
    <div className="gpx-wizard-uploader">
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={`gpx-wizard-uploader__dropzone ${
            isDragActive ? 'gpx-wizard-uploader--active' : ''
          } ${displayError ? 'gpx-wizard-uploader--error' : ''} ${
            isLoading ? 'gpx-wizard-uploader--loading' : ''
          }`}
          role="button"
          tabIndex={0}
          aria-label="Arrastra tu archivo GPX aquí o haz clic para seleccionar"
        >
          <input {...getInputProps()} disabled={isLoading} />

          {isLoading ? (
            <div className="gpx-wizard-uploader__loading">
              <div className="gpx-wizard-uploader__spinner" />
              <p>Analizando archivo...</p>
            </div>
          ) : (
            <>
              <div className="gpx-wizard-uploader__icon">
                <svg
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>

              <div className="gpx-wizard-uploader__text">
                <p className="gpx-wizard-uploader__primary">
                  Arrastra tu archivo GPX aquí
                </p>
                <p className="gpx-wizard-uploader__secondary">
                  o haz clic para seleccionar
                </p>
              </div>

              <div className="gpx-wizard-uploader__constraints">
                <p>Formatos aceptados: .gpx</p>
                <p>Máximo 10MB</p>
              </div>
            </>
          )}
        </div>
      ) : (
        <div className="gpx-wizard-uploader__preview">
          <div className="gpx-wizard-uploader__file-info">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="gpx-wizard-uploader__file-icon"
            >
              <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
              <polyline points="13 2 13 9 20 9" />
            </svg>

            <div className="gpx-wizard-uploader__file-details">
              <p className="gpx-wizard-uploader__file-name">{selectedFile.name}</p>
              <p className="gpx-wizard-uploader__file-size">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleRemove}
            disabled={isLoading}
            className="gpx-wizard-uploader__remove-button"
            aria-label="Eliminar archivo"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      )}

      {displayError && (
        <div className="gpx-wizard-uploader__error" role="alert">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{displayError}</span>
        </div>
      )}
    </div>
  );
};
