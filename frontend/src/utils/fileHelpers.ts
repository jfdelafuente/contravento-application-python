/**
 * File Helper Utilities
 *
 * Utilities for file validation, MIME type checking, and image processing.
 */

/**
 * Allowed MIME types for profile photos
 */
const ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png'];

/**
 * Maximum file size in bytes (5MB)
 */
const MAX_FILE_SIZE = 5 * 1024 * 1024;

/**
 * Check if file MIME type is allowed
 *
 * @param file - File to check
 * @returns true if MIME type is allowed
 */
export const isAllowedMimeType = (file: File): boolean => {
  return ALLOWED_MIME_TYPES.includes(file.type);
};

/**
 * Check if file size is within allowed limit
 *
 * @param file - File to check
 * @returns true if file size is within limit
 */
export const isWithinSizeLimit = (file: File): boolean => {
  return file.size <= MAX_FILE_SIZE;
};

/**
 * Validate file for profile photo upload
 *
 * @param file - File to validate
 * @returns Validation result with error message if invalid
 */
export const validatePhotoFile = (file: File): { valid: boolean; error?: string } => {
  if (!isAllowedMimeType(file)) {
    return {
      valid: false,
      error: 'Solo se permiten archivos JPG o PNG',
    };
  }

  if (!isWithinSizeLimit(file)) {
    return {
      valid: false,
      error: 'El archivo no puede exceder 5MB',
    };
  }

  return { valid: true };
};

/**
 * Format file size for display
 *
 * @param bytes - File size in bytes
 * @returns Formatted file size string (e.g., "2.5 MB")
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Create a blob URL from file for preview
 *
 * @param file - File to create preview for
 * @returns Blob URL for preview
 */
export const createPreviewUrl = (file: File): string => {
  return URL.createObjectURL(file);
};

/**
 * Revoke blob URL to free memory
 *
 * @param url - Blob URL to revoke
 */
export const revokePreviewUrl = (url: string): void => {
  URL.revokeObjectURL(url);
};

/**
 * Read file as Data URL
 *
 * @param file - File to read
 * @returns Promise with Data URL string
 */
export const readFileAsDataURL = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = () => {
      if (reader.result) {
        resolve(reader.result as string);
      } else {
        reject(new Error('Failed to read file'));
      }
    };

    reader.onerror = () => {
      reject(new Error('Error reading file'));
    };

    reader.readAsDataURL(file);
  });
};

/**
 * Get file extension from filename
 *
 * @param filename - Filename to extract extension from
 * @returns File extension (e.g., "jpg", "png")
 */
export const getFileExtension = (filename: string): string => {
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
};
