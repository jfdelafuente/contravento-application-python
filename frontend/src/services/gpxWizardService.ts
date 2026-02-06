/**
 * GPX Wizard Service - API client for GPS Trip Creation Wizard.
 *
 * Provides methods for analyzing GPX files before trip creation.
 * Feature: 017-gps-trip-wizard
 * Task: T047
 */

import { api } from './api';

/**
 * Trip difficulty levels (matches backend TripDifficulty enum)
 */
export type TripDifficulty = 'easy' | 'moderate' | 'difficult' | 'very_difficult';

/**
 * Simplified trackpoint for map visualization in wizard
 */
export interface TrackPointSimple {
  latitude: number;
  longitude: number;
  elevation: number | null;
  distance_km: number;
}

/**
 * GPX Telemetry Data (matches backend GPXTelemetry schema)
 */
export interface GPXTelemetry {
  distance_km: number;
  elevation_gain: number | null;
  elevation_loss: number | null;
  max_elevation: number | null;
  min_elevation: number | null;
  has_elevation: boolean;
  has_timestamps: boolean;
  start_date: string | null;
  end_date: string | null;
  total_time_minutes: number | null;
  moving_time_minutes: number | null;
  difficulty: TripDifficulty;
  suggested_title: string;
  trackpoints: TrackPointSimple[] | null;
}

/**
 * GPX Analysis Response (matches backend GPXAnalysisResponse schema)
 */
export interface GPXAnalysisResponse {
  success: boolean;
  data: GPXTelemetry | null;
  error: {
    code: string;
    message: string;
    field?: string;
  } | null;
}

/**
 * Error codes from POST /gpx/analyze endpoint
 */
export enum GPXAnalysisErrorCode {
  MISSING_FILE = 'MISSING_FILE',
  INVALID_FILE_TYPE = 'INVALID_FILE_TYPE',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  FILE_READ_ERROR = 'FILE_READ_ERROR',
  INVALID_GPX_FILE = 'INVALID_GPX_FILE',
  INVALID_GPX_DATA = 'INVALID_GPX_DATA',
  PROCESSING_TIMEOUT = 'PROCESSING_TIMEOUT',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  UNAUTHORIZED = 'UNAUTHORIZED',
}

/**
 * Custom error class for GPX analysis failures
 */
export class GPXAnalysisError extends Error {
  code: string;
  field?: string;

  constructor(code: string, message: string, field?: string) {
    super(message);
    this.name = 'GPXAnalysisError';
    this.code = code;
    this.field = field;
  }
}

/**
 * Analyze GPX file without storing to database.
 *
 * This endpoint provides lightweight GPX analysis for wizard preview.
 * Does NOT create a trip or GPXFile record.
 *
 * Contract: POST /gpx/analyze
 * Feature: 017-gps-trip-wizard
 * Performance Goal: <2s for files up to 10MB
 *
 * @param file - GPX file to analyze (max 10MB)
 * @returns Promise<GPXTelemetry> - Telemetry data (distance, elevation, difficulty)
 * @throws GPXAnalysisError - If file is invalid or analysis fails
 * @throws Error - For network or unexpected errors
 *
 * @example
 * ```typescript
 * try {
 *   const telemetry = await analyzeGPXFile(gpxFile);
 *   console.log(`Distance: ${telemetry.distance_km} km`);
 *   console.log(`Difficulty: ${telemetry.difficulty}`);
 * } catch (error) {
 *   if (error instanceof GPXAnalysisError) {
 *     // Handle GPX-specific errors (file too large, invalid format, etc.)
 *     console.error(`GPX Error [${error.code}]: ${error.message}`);
 *   } else {
 *     // Handle network or unexpected errors
 *     console.error('Unexpected error:', error);
 *   }
 * }
 * ```
 */
export async function analyzeGPXFile(file: File): Promise<GPXTelemetry> {
  console.log('🔍 [Frontend] analyzeGPXFile called');
  console.log('📝 [Frontend] File info:', {
    name: file.name,
    size: file.size,
    type: file.type,
    lastModified: file.lastModified
  });

  // Client-side validation (matches backend validation)
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

  if (file.size > MAX_FILE_SIZE) {
    console.error('❌ [Frontend] File too large:', file.size);
    throw new GPXAnalysisError(
      GPXAnalysisErrorCode.FILE_TOO_LARGE,
      'El archivo GPX es demasiado grande. Tamaño máximo: 10MB',
      'file'
    );
  }

  const fileName = file.name.toLowerCase();
  console.log('📝 [Frontend] fileName (lowercase):', fileName);
  console.log('✅ [Frontend] fileName.endsWith(\'.gpx\'):', fileName.endsWith('.gpx'));

  if (!fileName.endsWith('.gpx')) {
    console.error('❌ [Frontend] Invalid file extension');
    throw new GPXAnalysisError(
      GPXAnalysisErrorCode.INVALID_FILE_TYPE,
      'Formato no válido. Solo se aceptan archivos .gpx',
      'file'
    );
  }

  console.log('✅ [Frontend] Validation passed, creating FormData');

  // Create FormData for multipart/form-data request
  const formData = new FormData();
  formData.append('file', file);

  console.log('📤 [Frontend] Sending POST request to /gpx/analyze');

  try {
    const response = await api.post<GPXAnalysisResponse>('/gpx/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // Timeout after 60 seconds (aligned with backend timeout)
      timeout: 60000,
    });

    // Check if response indicates success
    if (response.data.success && response.data.data) {
      console.log('✅ [Frontend] GPX analysis successful');
      console.log('📊 [Frontend] Telemetry data:', response.data.data);
      console.log('🗺️ [Frontend] Trackpoints received:', response.data.data.trackpoints ? response.data.data.trackpoints.length : 'null');
      return response.data.data;
    }

    // Response has error in standardized format
    if (response.data.error) {
      throw new GPXAnalysisError(
        response.data.error.code,
        response.data.error.message,
        response.data.error.field
      );
    }

    // Unexpected response format
    throw new Error('Respuesta del servidor en formato inesperado');
  } catch (error: any) {
    // Re-throw GPXAnalysisError as-is
    if (error instanceof GPXAnalysisError) {
      throw error;
    }

    // Handle HTTP errors with standardized error response
    if (error.response?.data?.error) {
      const { code, message, field } = error.response.data.error;
      throw new GPXAnalysisError(code, message, field);
    }

    // Handle network timeout
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      throw new GPXAnalysisError(
        GPXAnalysisErrorCode.PROCESSING_TIMEOUT,
        'El procesamiento del archivo GPX excedió el tiempo límite'
      );
    }

    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      throw new GPXAnalysisError(
        GPXAnalysisErrorCode.UNAUTHORIZED,
        'No autorizado. Inicia sesión para continuar'
      );
    }

    // Handle 413 Request Entity Too Large
    if (error.response?.status === 413) {
      throw new GPXAnalysisError(
        GPXAnalysisErrorCode.FILE_TOO_LARGE,
        'El archivo GPX es demasiado grande. Tamaño máximo: 10MB',
        'file'
      );
    }

    // Handle generic 400 errors
    if (error.response?.status === 400) {
      throw new GPXAnalysisError(
        GPXAnalysisErrorCode.INVALID_GPX_FILE,
        'No se pudo procesar el archivo GPX. Verifica que sea un archivo válido'
      );
    }

    // Handle generic 500 errors
    if (error.response?.status >= 500) {
      throw new GPXAnalysisError(
        GPXAnalysisErrorCode.INTERNAL_ERROR,
        'Error interno del servidor. Intenta de nuevo más tarde'
      );
    }

    // Re-throw unexpected errors
    throw error;
  }
}

/**
 * Format difficulty level for display in Spanish
 */
export function formatDifficulty(difficulty: TripDifficulty): string {
  const difficultyMap: Record<TripDifficulty, string> = {
    easy: 'Fácil',
    moderate: 'Moderada',
    difficult: 'Difícil',
    very_difficult: 'Muy Difícil',
  };

  return difficultyMap[difficulty] || difficulty;
}

/**
 * Get difficulty color for UI styling
 */
export function getDifficultyColor(difficulty: TripDifficulty): string {
  const colorMap: Record<TripDifficulty, string> = {
    easy: '#10b981', // Green
    moderate: '#f59e0b', // Orange
    difficult: '#ef4444', // Red
    very_difficult: '#9333ea', // Purple
  };

  return colorMap[difficulty] || '#6b7280'; // Gray fallback
}

/**
 * Format time from minutes to human-readable format
 *
 * @param minutes - Total time in minutes
 * @returns Formatted time string (e.g., "2h 30m", "1 día 3h", "45m")
 *
 * @example
 * formatTimeFromMinutes(45) // "45m"
 * formatTimeFromMinutes(150) // "2h 30m"
 * formatTimeFromMinutes(1500) // "1 día 1h"
 */
export function formatTimeFromMinutes(minutes: number | null): string | null {
  if (minutes === null || minutes === undefined) {
    return null;
  }

  const totalMinutes = Math.round(minutes);

  // Less than 1 hour - show only minutes
  if (totalMinutes < 60) {
    return `${totalMinutes}m`;
  }

  // Less than 24 hours - show hours and minutes
  if (totalMinutes < 1440) {
    const hours = Math.floor(totalMinutes / 60);
    const mins = totalMinutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  }

  // 24 hours or more - show days and hours
  const days = Math.floor(totalMinutes / 1440);
  const remainingMinutes = totalMinutes % 1440;
  const hours = Math.floor(remainingMinutes / 60);

  if (hours > 0) {
    return days === 1 ? `1 día ${hours}h` : `${days} días ${hours}h`;
  }

  return days === 1 ? '1 día' : `${days} días`;
}
