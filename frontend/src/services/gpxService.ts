/**
 * GPX Service - API client for GPS Routes feature.
 *
 * Provides methods for uploading, retrieving, and managing GPX files.
 * Feature 003 - GPS Routes Interactive (T036)
 */

import { api } from './api';

/**
 * GPX Upload Response (matches backend schema)
 */
export interface GPXUploadResponse {
  gpx_file_id: string;
  trip_id: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'error';
  distance_km?: number;
  elevation_gain?: number;
  elevation_loss?: number;
  max_elevation?: number;
  min_elevation?: number;
  has_elevation?: boolean;
  has_timestamps?: boolean;
  total_points?: number;
  simplified_points?: number;
  uploaded_at: string;
  processed_at?: string;
  error_message?: string;
}

/**
 * GPX Status Response
 */
export interface GPXStatusResponse {
  gpx_file_id: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'error';
  distance_km?: number;
  elevation_gain?: number;
  simplified_points?: number;
  uploaded_at: string;
  processed_at?: string;
  error_message?: string;
}

/**
 * GPX File Metadata
 */
export interface GPXFileMetadata {
  gpx_file_id: string;
  trip_id: string;
  file_name: string;
  file_size: number;
  distance_km: number;
  elevation_gain?: number;
  elevation_loss?: number;
  max_elevation?: number;
  min_elevation?: number;
  total_points: number;
  simplified_points: number;
  has_elevation: boolean;
  has_timestamps: boolean;
  processing_status: 'pending' | 'processing' | 'completed' | 'error';
  error_message?: string;
  uploaded_at: string;
  processed_at?: string;
}

/**
 * Track Point (simplified GPS coordinate)
 */
export interface TrackPoint {
  point_id: string;
  latitude: number;
  longitude: number;
  elevation: number | null;
  distance_km: number;
  sequence: number;
  gradient: number | null;
}

/**
 * Coordinate (lat/lon pair)
 */
export interface Coordinate {
  latitude: number;
  longitude: number;
}

/**
 * Route Statistics (User Story 5)
 */
export interface RouteStatistics {
  stats_id: string;
  gpx_file_id: string;
  avg_speed_kmh: number | null;
  max_speed_kmh: number | null;
  total_time_minutes: number | null;
  moving_time_minutes: number | null;
  avg_gradient: number | null;
  max_gradient: number | null;
  calculated_at: string;
}

/**
 * Track Data Response (for map rendering)
 */
export interface TrackDataResponse {
  gpx_file_id: string;
  trip_id: string;
  distance_km: number;
  elevation_gain?: number;
  simplified_points_count: number;
  has_elevation: boolean;
  start_point: Coordinate;
  end_point: Coordinate;
  trackpoints: TrackPoint[];
  route_statistics: RouteStatistics | null; // User Story 5
}

/**
 * Upload GPX file to trip
 *
 * @param tripId - Trip ID to attach GPX to
 * @param file - GPX file to upload
 * @returns Upload response with processing status
 */
export async function uploadGPX(
  tripId: string,
  file: File
): Promise<GPXUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post(`/trips/${tripId}/gpx`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 30000, // 30 seconds for GPX processing (files up to 10MB)
  });

  return response.data.data;
}

/**
 * Poll GPX processing status
 *
 * Used for async uploads (>1MB files) to check when processing completes.
 *
 * @param gpxFileId - GPX file ID
 * @returns Status response
 */
export async function getGPXStatus(
  gpxFileId: string
): Promise<GPXStatusResponse> {
  const response = await api.get(`/gpx/${gpxFileId}/status`, {
    timeout: 30000, // 30 seconds for status polling
  });
  return response.data.data;
}

/**
 * Get GPX file metadata for a trip
 *
 * @param tripId - Trip ID
 * @returns GPX file metadata
 */
export async function getGPXMetadata(
  tripId: string
): Promise<GPXFileMetadata> {
  const response = await api.get(`/trips/${tripId}/gpx`);
  return response.data.data;
}

/**
 * Get track data (simplified trackpoints for map rendering)
 *
 * @param gpxFileId - GPX file ID
 * @returns Track data with simplified points
 */
export async function getGPXTrack(
  gpxFileId: string
): Promise<TrackDataResponse> {
  const response = await api.get(`/gpx/${gpxFileId}/track`);
  return response.data.data;
}

/**
 * Download original GPX file
 *
 * Opens download in browser.
 *
 * @param gpxFileId - GPX file ID
 */
export async function downloadGPX(gpxFileId: string): Promise<void> {
  // Use window.location to trigger download
  const baseURL = api.defaults.baseURL || 'http://localhost:8000';
  window.location.href = `${baseURL}/gpx/${gpxFileId}/download`;
}

/**
 * Delete GPX file from trip
 *
 * Requires authentication and ownership.
 *
 * @param tripId - Trip ID
 */
export async function deleteGPX(tripId: string): Promise<void> {
  await api.delete(`/trips/${tripId}/gpx`);
}

/**
 * Poll GPX status until completed or error
 *
 * Helper function for async uploads.
 * Polls every 2 seconds until status is 'completed' or 'error'.
 *
 * @param gpxFileId - GPX file ID
 * @param onProgress - Callback for progress updates
 * @param maxWaitSeconds - Maximum wait time (default 30s)
 * @returns Final status response
 */
export async function pollGPXUntilComplete(
  gpxFileId: string,
  onProgress?: (status: GPXStatusResponse) => void,
  maxWaitSeconds: number = 30
): Promise<GPXStatusResponse> {
  const pollInterval = 2000; // 2 seconds
  const maxAttempts = Math.floor((maxWaitSeconds * 1000) / pollInterval);
  let consecutiveErrors = 0;
  const MAX_CONSECUTIVE_ERRORS = 3;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      console.log(`[GPX Polling] Attempt ${attempt + 1}/${maxAttempts} - Checking status...`);
      const status = await getGPXStatus(gpxFileId);
      consecutiveErrors = 0; // Reset error count on success

      console.log(`[GPX Polling] Status: ${status.processing_status}`, {
        distance_km: status.distance_km,
        elevation_gain: status.elevation_gain,
        simplified_points: status.simplified_points,
      });

      // Notify progress callback
      if (onProgress) {
        onProgress(status);
      }

      // Check if completed or error
      if (status.processing_status === 'completed') {
        console.log('[GPX Polling] ✅ Processing completed successfully!');
        return status;
      }

      if (status.processing_status === 'error') {
        console.error('[GPX Polling] ❌ Processing failed:', status.error_message);
        throw new Error(
          status.error_message || 'Error al procesar archivo GPX'
        );
      }

      // Wait before next poll
      console.log(`[GPX Polling] Status: ${status.processing_status}, waiting ${pollInterval}ms...`);
      await new Promise((resolve) => setTimeout(resolve, pollInterval));
    } catch (error: any) {
      consecutiveErrors++;

      // Si es timeout de red pero no hemos excedido límite de errores
      if (consecutiveErrors < MAX_CONSECUTIVE_ERRORS) {
        console.warn(`[GPX Polling] ⚠️ Attempt ${attempt + 1} failed (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS}), retrying...`, error.message);
        await new Promise((resolve) => setTimeout(resolve, pollInterval));
        continue; // Retry
      }

      // Si excedimos errores consecutivos, propagar error
      console.error('[GPX Polling] ❌ Max consecutive errors reached, giving up');
      throw error;
    }
  }

  throw new Error(
    `El procesamiento del archivo GPX excedió el tiempo máximo de ${maxWaitSeconds} segundos`
  );
}
