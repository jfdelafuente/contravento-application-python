/**
 * GPXUploader Component
 *
 * Drag-and-drop GPX file uploader with progress tracking.
 * Supports both synchronous (<1MB) and asynchronous (>1MB) processing.
 *
 * Features:
 * - Drag-and-drop with react-dropzone
 * - File validation (.gpx extension, max 10MB)
 * - Progress bar with status messages
 * - Error handling with Spanish messages
 * - Auto-reload trip data on success
 *
 * Feature 003 - GPS Routes Interactive (T038)
 */

import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useGPXUpload } from '../../hooks/useGPXUpload';
import './GPXUploader.css';

export interface GPXUploaderProps {
  /** Trip ID to upload GPX to */
  tripId: string;

  /** Callback when upload completes successfully */
  onUploadComplete?: () => void;

  /** Disabled state */
  disabled?: boolean;
}

/**
 * GPXUploader Component
 *
 * Provides drag-and-drop interface for uploading GPX files to trips.
 */
export const GPXUploader: React.FC<GPXUploaderProps> = ({
  tripId,
  onUploadComplete,
  disabled = false,
}) => {
  const { upload, isUploading, uploadProgress, error, statusMessage, reset } =
    useGPXUpload();

  /**
   * Handle file drop
   */
  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      // Safety check: ensure acceptedFiles array exists
      if (!acceptedFiles || acceptedFiles.length === 0) {
        console.warn('GPXUploader: No files provided to onDrop callback');
        return;
      }

      // Only accept first file (trips can have max 1 GPX)
      const file = acceptedFiles[0];
      if (!file) return;

      try {
        await upload(tripId, file);

        // Notify parent on success
        if (onUploadComplete) {
          onUploadComplete();
        }
      } catch (err) {
        // Error is already set by useGPXUpload hook
        console.error('GPX upload failed:', err);
      }
    },
    [tripId, upload, onUploadComplete]
  );

  // Configure dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/gpx+xml': ['.gpx'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    disabled: disabled || isUploading,
  });

  return (
    <div className="gpx-uploader">
      <div
        {...getRootProps()}
        className={`gpx-dropzone ${isDragActive ? 'drag-active' : ''} ${
          isUploading ? 'uploading' : ''
        } ${error ? 'error' : ''}`}
      >
        <input {...getInputProps()} />

        {!isUploading && !error && (
          <div className="gpx-dropzone-content">
            <svg
              className="gpx-dropzone-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>

            {isDragActive ? (
              <p className="gpx-dropzone-text">Suelta el archivo GPX aquí...</p>
            ) : (
              <>
                <p className="gpx-dropzone-text">
                  Arrastra un archivo GPX aquí, o haz clic para seleccionar
                </p>
                <p className="gpx-dropzone-hint">
                  Máximo 10MB • Solo archivos .gpx
                </p>
              </>
            )}
          </div>
        )}

        {isUploading && (
          <div className="gpx-upload-progress">
            <div className="gpx-progress-spinner">
              <div className="spinner"></div>
            </div>

            <div className="gpx-progress-info">
              <p className="gpx-progress-message">{statusMessage}</p>
              <div className="gpx-progress-bar-container">
                <div
                  className="gpx-progress-bar"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="gpx-progress-percent">{uploadProgress}%</p>
            </div>
          </div>
        )}

        {error && (
          <div className="gpx-upload-error">
            <svg
              className="gpx-error-icon"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <p className="gpx-error-message">{error}</p>

            <button
              type="button"
              className="gpx-error-retry"
              onClick={(e) => {
                e.stopPropagation();
                reset();
              }}
            >
              Intentar de nuevo
            </button>
          </div>
        )}
      </div>

      <div className="gpx-uploader-info">
        <h4>¿Qué es un archivo GPX?</h4>
        <p>
          GPX (GPS Exchange Format) es un formato estándar para compartir rutas
          GPS. Puedes exportar archivos GPX desde aplicaciones como Strava,
          Komoot, Garmin Connect, y muchas otras.
        </p>
      </div>
    </div>
  );
};
