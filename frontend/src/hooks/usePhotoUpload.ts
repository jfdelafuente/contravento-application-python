/**
 * usePhotoUpload Hook
 *
 * Custom hook for managing photo upload state including file selection,
 * cropping, upload progress, and error handling.
 */

import { useState, useCallback } from 'react';
import type { Area } from 'react-easy-crop';
import { uploadPhoto, removePhoto } from '../services/photoService';
import { createPreviewUrl, revokePreviewUrl } from '../utils/fileHelpers';
import toast from 'react-hot-toast';

interface UsePhotoUploadReturn {
  /** Selected file for cropping */
  selectedFile: File | null;
  /** Blob URL for preview */
  previewUrl: string | null;
  /** Whether upload is in progress */
  isUploading: boolean;
  /** Upload progress (0-100) */
  uploadProgress: number;
  /** Whether crop modal is open */
  isCropModalOpen: boolean;
  /** Handle file selection */
  handleFileSelected: (file: File) => void;
  /** Handle crop save */
  handleCropSave: (croppedArea: Area) => Promise<void>;
  /** Handle crop cancel */
  handleCropCancel: () => void;
  /** Handle photo removal */
  handleRemovePhoto: () => Promise<void>;
}

/**
 * Hook for managing photo upload workflow
 *
 * @param username - Username of the profile owner
 * @param onPhotoUpdated - Callback when photo is updated
 */
export const usePhotoUpload = (
  username: string,
  onPhotoUpdated?: (photoUrl: string) => void
): UsePhotoUploadReturn => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isCropModalOpen, setIsCropModalOpen] = useState(false);

  const handleFileSelected = useCallback((file: File) => {
    // Clean up previous preview URL
    if (previewUrl) {
      revokePreviewUrl(previewUrl);
    }

    // Create new preview URL
    const newPreviewUrl = createPreviewUrl(file);
    setPreviewUrl(newPreviewUrl);
    setSelectedFile(file);
    setIsCropModalOpen(true);
  }, [previewUrl]);

  const handleCropSave = useCallback(async (croppedArea: Area) => {
    if (!selectedFile || !previewUrl) return;

    try {
      setIsUploading(true);
      setUploadProgress(0);

      // Create canvas to crop the image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        throw new Error('Failed to get canvas context');
      }

      // Load image
      const image = new Image();
      image.src = previewUrl;
      await new Promise((resolve, reject) => {
        image.onload = resolve;
        image.onerror = reject;
      });

      // Set canvas size to cropped area
      canvas.width = croppedArea.width;
      canvas.height = croppedArea.height;

      // Draw cropped image
      ctx.drawImage(
        image,
        croppedArea.x,
        croppedArea.y,
        croppedArea.width,
        croppedArea.height,
        0,
        0,
        croppedArea.width,
        croppedArea.height
      );

      // Convert canvas to blob
      const blob = await new Promise<Blob>((resolve, reject) => {
        canvas.toBlob((blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to create blob'));
          }
        }, 'image/jpeg', 0.95);
      });

      // Create File from blob
      const croppedFile = new File([blob], selectedFile.name, {
        type: 'image/jpeg',
        lastModified: Date.now(),
      });

      // Upload cropped image
      const result = await uploadPhoto(username, croppedFile, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
        setUploadProgress(progress);
      });

      // Show success message
      toast.success(result.message || 'Foto actualizada correctamente', {
        duration: 4000,
        position: 'top-center',
        style: {
          background: '#6b723b',
          color: '#f5f1e8',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.875rem',
          fontWeight: '600',
        },
      });

      // Close modal and clean up
      setIsCropModalOpen(false);
      revokePreviewUrl(previewUrl);
      setPreviewUrl(null);
      setSelectedFile(null);

      // Notify parent component
      try {
        if (onPhotoUpdated) {
          onPhotoUpdated(result.photo_url);
        }
      } catch (callbackError) {
        console.error('Error in onPhotoUpdated callback:', callbackError);
      }
    } catch (error: any) {
      console.error('Error uploading photo:', error);

      const errorMessage =
        error.response?.data?.message || 'Error al subir la foto. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
        style: {
          background: '#dc2626',
          color: '#f5f1e8',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.875rem',
          fontWeight: '600',
        },
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [username, selectedFile, previewUrl, onPhotoUpdated]);

  const handleCropCancel = useCallback(() => {
    // Clean up preview URL
    if (previewUrl) {
      revokePreviewUrl(previewUrl);
    }

    setIsCropModalOpen(false);
    setPreviewUrl(null);
    setSelectedFile(null);
  }, [previewUrl]);

  const handleRemovePhoto = useCallback(async () => {
    const confirmed = window.confirm(
      '¿Estás seguro de que quieres eliminar tu foto de perfil?'
    );

    if (!confirmed) return;

    try {
      setIsUploading(true);

      await removePhoto(username);

      toast.success('Foto eliminada correctamente', {
        duration: 4000,
        position: 'top-center',
        style: {
          background: '#6b723b',
          color: '#f5f1e8',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.875rem',
          fontWeight: '600',
        },
      });

      // Notify parent component
      if (onPhotoUpdated) {
        onPhotoUpdated('');
      }
    } catch (error: any) {
      console.error('Error removing photo:', error);

      const errorMessage =
        error.response?.data?.message || 'Error al eliminar la foto. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
        style: {
          background: '#dc2626',
          color: '#f5f1e8',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.875rem',
          fontWeight: '600',
        },
      });
    } finally {
      setIsUploading(false);
    }
  }, [username, onPhotoUpdated]);

  return {
    selectedFile,
    previewUrl,
    isUploading,
    uploadProgress,
    isCropModalOpen,
    handleFileSelected,
    handleCropSave,
    handleCropCancel,
    handleRemovePhoto,
  };
};

export default usePhotoUpload;
