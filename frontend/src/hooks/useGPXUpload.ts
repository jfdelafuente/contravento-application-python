/**
 * useGPXUpload Hook - Custom hook for GPX file upload with progress tracking.
 *
 * Handles both synchronous (<1MB) and asynchronous (>1MB) processing.
 * Feature 003 - GPS Routes Interactive (T037)
 */

import { useState, useCallback } from 'react';
import {
  uploadGPX,
  pollGPXUntilComplete,
  GPXUploadResponse,
  GPXStatusResponse,
} from '../services/gpxService';

export interface UseGPXUploadReturn {
  /**
   * Upload GPX file to trip
   */
  upload: (tripId: string, file: File) => Promise<GPXUploadResponse>;

  /**
   * Current upload progress (0-100)
   */
  uploadProgress: number;

  /**
   * Whether upload/processing is in progress
   */
  isUploading: boolean;

  /**
   * Error message if upload failed
   */
  error: string | null;

  /**
   * Processing status message
   */
  statusMessage: string | null;

  /**
   * Reset upload state
   */
  reset: () => void;
}

/**
 * Custom hook for GPX file upload with progress tracking
 *
 * Features:
 * - Synchronous processing for files <1MB (immediate response)
 * - Asynchronous processing for files >1MB (with polling)
 * - Progress tracking (0-100%)
 * - Error handling with Spanish messages
 *
 * @example
 * ```tsx
 * const { upload, isUploading, uploadProgress, error } = useGPXUpload();
 *
 * const handleUpload = async (file: File) => {
 *   try {
 *     const result = await upload(tripId, file);
 *     console.log('Upload complete:', result);
 *   } catch (err) {
 *     console.error('Upload failed:', err);
 *   }
 * };
 * ```
 */
export function useGPXUpload(): UseGPXUploadReturn {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  /**
   * Upload GPX file with progress tracking
   */
  const upload = useCallback(
    async (tripId: string, file: File): Promise<GPXUploadResponse> => {
      try {
        // Reset state
        setIsUploading(true);
        setError(null);
        setUploadProgress(0);
        setStatusMessage('Subiendo archivo GPX...');

        // Validate file size (max 10MB)
        const MAX_SIZE_MB = 10;
        const fileSizeMB = file.size / (1024 * 1024);

        if (fileSizeMB > MAX_SIZE_MB) {
          throw new Error(
            `El archivo excede el tamaño máximo de ${MAX_SIZE_MB}MB (${fileSizeMB.toFixed(1)}MB)`
          );
        }

        // Validate file extension
        if (!file.name.toLowerCase().endsWith('.gpx')) {
          throw new Error('Solo se permiten archivos .gpx');
        }

        // Upload file
        setUploadProgress(10);
        const uploadResponse = await uploadGPX(tripId, file);

        // Check processing status
        if (uploadResponse.processing_status === 'completed') {
          // Synchronous processing (files <1MB)
          setUploadProgress(100);
          setStatusMessage('Archivo GPX procesado correctamente');
          setIsUploading(false);
          return uploadResponse;
        } else if (
          uploadResponse.processing_status === 'pending' ||
          uploadResponse.processing_status === 'processing'
        ) {
          // Asynchronous processing (files >1MB)
          setUploadProgress(20);
          setStatusMessage('Procesando archivo GPX...');

          // Poll status until completed
          const finalStatus = await pollGPXUntilComplete(
            uploadResponse.gpx_file_id,
            (status: GPXStatusResponse) => {
              // Update progress based on status
              if (status.processing_status === 'processing') {
                // Gradually increase progress from 20% to 90%
                setUploadProgress((prev) => Math.min(prev + 10, 90));
              }
            },
            30 // Max 30 seconds
          );

          // Convert status response to upload response
          const completeResponse: GPXUploadResponse = {
            ...uploadResponse,
            processing_status: finalStatus.processing_status,
            distance_km: finalStatus.distance_km,
            elevation_gain: finalStatus.elevation_gain,
            simplified_points: finalStatus.simplified_points,
            processed_at: finalStatus.processed_at,
          };

          setUploadProgress(100);
          setStatusMessage('Archivo GPX procesado correctamente');
          setIsUploading(false);
          return completeResponse;
        } else if (uploadResponse.processing_status === 'error') {
          throw new Error(
            uploadResponse.error_message || 'Error al procesar archivo GPX'
          );
        }

        // Unknown status
        throw new Error('Estado de procesamiento desconocido');
      } catch (err: any) {
        const errorMessage =
          err.response?.data?.error?.message ||
          err.message ||
          'Error al subir archivo GPX';

        setError(errorMessage);
        setStatusMessage(null);
        setIsUploading(false);
        throw new Error(errorMessage);
      }
    },
    []
  );

  /**
   * Reset upload state
   */
  const reset = useCallback(() => {
    setUploadProgress(0);
    setIsUploading(false);
    setError(null);
    setStatusMessage(null);
  }, []);

  return {
    upload,
    uploadProgress,
    isUploading,
    error,
    statusMessage,
    reset,
  };
}
