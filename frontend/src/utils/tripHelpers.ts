/**
 * Trip Helper Utilities
 *
 * Utility functions for working with trip data in the Travel Diary feature.
 * Based on backend API contracts from Feature 002 (Travel Diary Backend).
 */

import { TripDifficulty, DIFFICULTY_LABELS, DIFFICULTY_CLASSES } from '../types/trip';

// ============================================================================
// API URL Helper
// ============================================================================

/**
 * Get the base URL for the backend API
 *
 * @returns Backend API base URL (e.g., 'http://localhost:8000')
 */
const getApiBaseUrl = (): string => {
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

/**
 * Convert relative photo URL to absolute URL
 *
 * Backend returns relative URLs like "/storage/trip_photos/..."
 * This converts them to absolute URLs like "http://localhost:8000/storage/trip_photos/..."
 *
 * @param relativeUrl - Relative URL from backend (e.g., '/storage/trip_photos/...')
 * @returns Absolute URL pointing to backend
 *
 * @example
 * getPhotoUrl('/storage/trip_photos/2024/01/photo.jpg')
 * // Returns: 'http://localhost:8000/storage/trip_photos/2024/01/photo.jpg'
 */
export const getPhotoUrl = (relativeUrl: string | null | undefined): string | null => {
  if (!relativeUrl) return null;

  // If already absolute URL, return as-is
  if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
    return relativeUrl;
  }

  // Convert relative to absolute
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}${relativeUrl}`;
};

// ============================================================================
// Difficulty Helpers
// ============================================================================

/**
 * Get Spanish label for difficulty level
 *
 * @param difficulty - Difficulty level ('easy', 'moderate', 'difficult', 'very_difficult')
 * @returns Spanish label for the difficulty level
 *
 * @example
 * getDifficultyLabel('easy') // 'Fácil'
 * getDifficultyLabel('very_difficult') // 'Muy Difícil'
 */
export const getDifficultyLabel = (difficulty: TripDifficulty | null): string => {
  if (!difficulty) return 'No especificada';
  return DIFFICULTY_LABELS[difficulty];
};

/**
 * Get CSS class for difficulty badge
 *
 * @param difficulty - Difficulty level ('easy', 'moderate', 'difficult', 'very_difficult')
 * @returns CSS class name for styling the difficulty badge
 *
 * @example
 * <span className={getDifficultyClass('moderate')}>Moderada</span>
 * // Output: <span class="difficulty-badge--moderate">Moderada</span>
 */
export const getDifficultyClass = (difficulty: TripDifficulty | null): string => {
  if (!difficulty) return 'difficulty-badge--default';
  return DIFFICULTY_CLASSES[difficulty];
};

// ============================================================================
// Date Formatting Helpers
// ============================================================================

/**
 * Format ISO 8601 date string to Spanish locale
 *
 * @param dateString - ISO 8601 date string (YYYY-MM-DD)
 * @returns Formatted date in Spanish (e.g., "15 de mayo de 2024")
 *
 * @example
 * formatDate('2024-05-15') // '15 de mayo de 2024'
 * formatDate('2024-12-01') // '1 de diciembre de 2024'
 */
export const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'Fecha no disponible';

  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Fecha inválida';

    return new Intl.DateTimeFormat('es-ES', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(date);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Fecha inválida';
  }
};

/**
 * Format ISO 8601 timestamp to Spanish locale with time
 *
 * @param dateTimeString - ISO 8601 timestamp (YYYY-MM-DDTHH:mm:ssZ)
 * @returns Formatted date and time in Spanish (e.g., "15 de mayo de 2024, 10:30")
 *
 * @example
 * formatDateTime('2024-05-15T10:30:00Z') // '15 de mayo de 2024, 10:30'
 * formatDateTime('2024-12-01T15:45:00Z') // '1 de diciembre de 2024, 15:45'
 */
export const formatDateTime = (dateTimeString: string | null): string => {
  if (!dateTimeString) return 'Fecha no disponible';

  try {
    const date = new Date(dateTimeString);
    if (isNaN(date.getTime())) return 'Fecha inválida';

    return new Intl.DateTimeFormat('es-ES', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch (error) {
    console.error('Error formatting datetime:', error);
    return 'Fecha inválida';
  }
};

/**
 * Format date range for trip duration display
 *
 * @param startDate - ISO 8601 start date (YYYY-MM-DD)
 * @param endDate - ISO 8601 end date (YYYY-MM-DD) or null for single-day trips
 * @returns Formatted date range in Spanish
 *
 * @example
 * formatDateRange('2024-05-15', '2024-05-17')
 * // '15 - 17 de mayo de 2024'
 *
 * formatDateRange('2024-05-15', '2024-06-02')
 * // '15 de mayo - 2 de junio de 2024'
 *
 * formatDateRange('2024-05-15', null)
 * // '15 de mayo de 2024'
 */
export const formatDateRange = (startDate: string, endDate: string | null): string => {
  if (!endDate) {
    return formatDate(startDate);
  }

  try {
    const start = new Date(startDate);
    const end = new Date(endDate);

    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      return 'Fechas inválidas';
    }

    // Same month and year - show: "15 - 17 de mayo de 2024"
    if (start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()) {
      const startDay = start.getDate();
      const endDay = end.getDate();
      const month = new Intl.DateTimeFormat('es-ES', { month: 'long' }).format(start);
      const year = start.getFullYear();

      return `${startDay} - ${endDay} de ${month} de ${year}`;
    }

    // Different months - show: "15 de mayo - 2 de junio de 2024"
    const startFormatted = new Intl.DateTimeFormat('es-ES', {
      day: 'numeric',
      month: 'long',
    }).format(start);

    const endFormatted = new Intl.DateTimeFormat('es-ES', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(end);

    return `${startFormatted} - ${endFormatted}`;
  } catch (error) {
    console.error('Error formatting date range:', error);
    return 'Fechas inválidas';
  }
};

// ============================================================================
// Distance Formatting Helpers
// ============================================================================

/**
 * Format distance in kilometers with locale formatting
 *
 * @param distanceKm - Distance in kilometers (null if not provided)
 * @returns Formatted distance string (e.g., "127.3 km")
 *
 * @example
 * formatDistance(127.3) // '127.3 km'
 * formatDistance(1000) // '1,000 km'
 * formatDistance(null) // 'No especificada'
 */
export const formatDistance = (distanceKm: number | null): string => {
  if (distanceKm === null || distanceKm === undefined) {
    return 'No especificada';
  }

  try {
    return `${new Intl.NumberFormat('es-ES', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 1,
    }).format(distanceKm)} km`;
  } catch (error) {
    console.error('Error formatting distance:', error);
    return 'Distancia inválida';
  }
};

// ============================================================================
// Status Helpers
// ============================================================================

/**
 * Get Spanish label for trip status
 *
 * @param status - Trip status ('draft' or 'published')
 * @returns Spanish label for the status
 *
 * @example
 * getStatusLabel('draft') // 'Borrador'
 * getStatusLabel('published') // 'Publicado'
 */
export const getStatusLabel = (status: 'draft' | 'published'): string => {
  const labels: Record<'draft' | 'published', string> = {
    draft: 'Borrador',
    published: 'Publicado',
  };

  return labels[status];
};

/**
 * Get CSS class for status badge
 *
 * @param status - Trip status ('draft' or 'published')
 * @returns CSS class name for styling the status badge
 *
 * @example
 * <span className={getStatusClass('draft')}>Borrador</span>
 * // Output: <span class="status-badge--draft">Borrador</span>
 */
export const getStatusClass = (status: 'draft' | 'published'): string => {
  const classes: Record<'draft' | 'published', string> = {
    draft: 'status-badge--draft',
    published: 'status-badge--published',
  };

  return classes[status];
};

// ============================================================================
// Form Helpers
// ============================================================================

/**
 * Convert form data to API request payload
 *
 * @param formData - Form data from React Hook Form (TripFormData)
 * @returns API request payload (TripCreateInput or TripUpdateInput)
 *
 * @example
 * const formData = {
 *   title: 'Vía Verde del Aceite',
 *   start_date: '2024-05-15',
 *   end_date: '2024-05-17',
 *   distance_km: '127.3',
 *   difficulty: 'moderate',
 *   description: '<p>Ruta espectacular...</p>',
 *   tags: ['vías verdes', 'andalucía'],
 * };
 *
 * const apiPayload = formDataToApiPayload(formData);
 * // {
 * //   title: 'Vía Verde del Aceite',
 * //   start_date: '2024-05-15',
 * //   end_date: '2024-05-17',
 * //   distance_km: 127.3,
 * //   difficulty: 'moderate',
 * //   description: '<p>Ruta espectacular...</p>',
 * //   tags: ['vías verdes', 'andalucía'],
 * //   locations: []
 * // }
 */
export const formDataToApiPayload = (formData: {
  title: string;
  start_date: string;
  end_date: string;
  distance_km: string;
  difficulty: TripDifficulty | '';
  description: string;
  tags: string[];
}): {
  title: string;
  description: string;
  start_date: string;
  end_date: string | null;
  distance_km: number | null;
  difficulty: TripDifficulty | null;
  locations: { name: string; country?: string }[];
  tags: string[];
} => {
  return {
    title: formData.title.trim(),
    description: formData.description,
    start_date: formData.start_date,
    end_date: formData.end_date || null,
    distance_km: formData.distance_km ? parseFloat(formData.distance_km) : null,
    difficulty: formData.difficulty || null,
    locations: [], // Phase 1 MVP: no location input
    tags: formData.tags,
  };
};

/**
 * Check if trip meets publish requirements
 *
 * @param formData - Form data to validate
 * @returns True if trip meets publish requirements, false otherwise
 *
 * @example
 * canPublishTrip(formData) // true if description >= 50 chars
 */
export const canPublishTrip = (formData: {
  description: string;
}): boolean => {
  return formData.description.length >= 50;
};

// ============================================================================
// Photo Helpers
// ============================================================================

/**
 * Validate photo file before upload
 *
 * @param file - File to validate
 * @returns Object with valid flag and error message if invalid
 *
 * @example
 * const validation = validatePhotoFile(file);
 * if (!validation.valid) {
 *   toast.error(validation.error);
 *   return;
 * }
 */
export const validatePhotoFile = (file: File): { valid: boolean; error?: string } => {
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Solo se permiten imágenes JPG y PNG',
    };
  }

  // Check file size (max 10MB)
  const maxSizeBytes = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSizeBytes) {
    return {
      valid: false,
      error: 'El tamaño máximo permitido es 10MB',
    };
  }

  return { valid: true };
};

/**
 * Format file size in human-readable format
 *
 * @param bytes - File size in bytes
 * @returns Formatted file size (e.g., "2.5 MB")
 *
 * @example
 * formatFileSize(2621440) // '2.5 MB'
 * formatFileSize(1024) // '1 KB'
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};
