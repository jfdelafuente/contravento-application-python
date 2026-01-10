/**
 * Photo Service
 *
 * API service for profile photo upload and management operations.
 */

import { api } from './api';
import type { PhotoUploadResponse } from '../types/profile';

/**
 * Upload and update profile photo
 * Endpoint: POST /api/users/{username}/profile/photo
 *
 * @param username - Username of the profile owner
 * @param file - Photo file to upload (JPG/PNG, max 5MB)
 * @param onUploadProgress - Optional callback for upload progress tracking
 * @returns Promise with photo URL and success message
 */
export const uploadPhoto = async (
  username: string,
  file: File,
  onUploadProgress?: (progressEvent: ProgressEvent) => void
): Promise<PhotoUploadResponse> => {
  const formData = new FormData();
  formData.append('photo', file);

  const response = await api.post<{ success: boolean; data: { photo_url: string }; message: string }>(
    `/users/${username}/profile/photo`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: onUploadProgress
        ? (progressEvent) => {
            if (progressEvent.total) {
              onUploadProgress(progressEvent as ProgressEvent);
            }
          }
        : undefined,
    }
  );

  return {
    photo_url: response.data.data.photo_url,
    message: response.data.message || 'Foto actualizada correctamente',
  };
};

/**
 * Remove current user's profile photo
 * Endpoint: DELETE /api/users/{username}/profile/photo
 *
 * @param username - Username of the profile owner
 */
export const removePhoto = async (username: string): Promise<{ message: string }> => {
  const response = await api.delete<{ success: boolean; message: string }>(`/users/${username}/profile/photo`);
  return { message: response.data.message };
};
