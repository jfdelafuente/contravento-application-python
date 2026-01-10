/**
 * ProfileEditPage
 *
 * Page container for editing user profile including bio, location, cycling type,
 * profile photo, password, and privacy settings.
 */

import React, { useState, useEffect, lazy, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { useProfileEdit } from '../hooks/useProfileEdit';
import { useUnsavedChanges } from '../hooks/useUnsavedChanges';
import { usePhotoUpload } from '../hooks/usePhotoUpload';
import { usePasswordChange } from '../hooks/usePasswordChange';
import { updateProfile, changePassword } from '../services/profileService';
import { BasicInfoSection } from '../components/profile/BasicInfoSection';
import { PhotoUploadSection } from '../components/profile/PhotoUploadSection';
import { PasswordChangeSection } from '../components/profile/PasswordChangeSection';
import { PrivacySettingsSection } from '../components/profile/PrivacySettingsSection';
import type { ProfileFormData, ProfileUpdateRequest, PasswordChangeRequest } from '../types/profile';
import './ProfileEditPage.css';

// Lazy load PhotoCropModal for better initial load performance
const PhotoCropModal = lazy(() => import('../components/profile/PhotoCropModal'));

export const ProfileEditPage: React.FC = () => {
  const { user, updateUser, logout } = useAuth();
  const navigate = useNavigate();
  const [isSaving, setIsSaving] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [currentPhotoUrl, setCurrentPhotoUrl] = useState(user?.photo_url || '');

  // Initialize form with current user data (includes privacy settings)
  const {
    register,
    handleSubmit,
    errors,
    isSubmitting,
    isDirty,
    reset,
    bioLength,
    watch,
  } = useProfileEdit({
    bio: user?.bio || '',
    location: user?.location || '',
    cycling_type: user?.cycling_type || '',
    profile_visibility: user?.profile_visibility || 'public',
    trip_visibility: user?.trip_visibility || 'public',
  });

  // Watch privacy settings for live updates
  const profileVisibility = watch('profile_visibility');
  const tripVisibility = watch('trip_visibility');

  // Photo upload hook
  const {
    isUploading,
    uploadProgress,
    isCropModalOpen,
    previewUrl,
    handleFileSelected,
    handleCropSave,
    handleCropCancel,
    handleRemovePhoto,
  } = usePhotoUpload(
    user?.username || '',
    (photoUrl) => {
      // Update local state and auth context when photo changes
      setCurrentPhotoUrl(photoUrl);
      if (updateUser) {
        updateUser({ ...user!, photo_url: photoUrl });
      }
    }
  );

  // Password change hook
  const {
    register: registerPassword,
    handleSubmit: handleSubmitPassword,
    errors: passwordErrors,
    isSubmitting: isPasswordSubmitting,
    isDirty: isPasswordDirty,
    reset: resetPassword,
    newPassword,
  } = usePasswordChange();

  // Update photo URL when user changes
  useEffect(() => {
    setCurrentPhotoUrl(user?.photo_url || '');
  }, [user?.photo_url]);

  // Warn about unsaved changes (profile or password)
  useUnsavedChanges(
    isDirty || isPasswordDirty,
    'Tienes cambios sin guardar. ¿Estás seguro de que quieres salir?'
  );

  if (!user) {
    return null;
  }

  const handleCancel = () => {
    if (isDirty || isPasswordDirty) {
      const confirmed = window.confirm(
        '¿Estás seguro de que quieres cancelar? Los cambios no guardados se perderán.'
      );
      if (!confirmed) return;
    }
    navigate('/profile');
  };

  const onPasswordSubmit = async (data: PasswordChangeRequest) => {
    try {
      setIsChangingPassword(true);

      await changePassword(user.username, data);

      toast.success('Contraseña actualizada correctamente. Por seguridad, debes iniciar sesión nuevamente.', {
        duration: 3000,
        position: 'top-center',
        style: {
          background: '#6b723b',
          color: '#f5f1e8',
          fontFamily: 'var(--font-sans)',
          fontSize: '0.875rem',
          fontWeight: '600',
        },
      });

      // Reset password form
      resetPassword();

      // Wait for toast to be visible, then logout and redirect
      setTimeout(async () => {
        await logout();
        navigate('/login', { replace: true });
      }, 1500);
    } catch (error: any) {
      console.error('Error changing password:', error);

      const errorMessage =
        error.response?.data?.message || 'Error al cambiar la contraseña. Intenta nuevamente.';

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
      setIsChangingPassword(false);
    }
  };

  const onSubmit = async (data: ProfileFormData) => {
    try {
      setIsSaving(true);

      // Prepare update data (includes privacy settings from User Story 4)
      const updateData: ProfileUpdateRequest = {
        bio: data.bio || undefined,
        location: data.location || undefined,
        cycling_type: data.cycling_type || undefined,
        profile_visibility: data.profile_visibility,
        trip_visibility: data.trip_visibility,
      };

      // Call API to update profile
      await updateProfile(user?.username || '', updateData);

      // Show success message
      toast.success('Perfil actualizado correctamente', {
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

      // Reset form dirty state
      reset(data);

      // Navigate back to profile
      setTimeout(() => {
        navigate('/profile');
      }, 1000);
    } catch (error: any) {
      console.error('Error updating profile:', error);

      // Show error message
      const errorMessage =
        error.response?.data?.message || 'Error al actualizar el perfil. Intenta nuevamente.';

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
      setIsSaving(false);
    }
  };

  return (
    <div className="profile-edit-page">
      <div className="profile-edit-container">
        <header className="profile-edit-header">
          <h1 className="profile-edit-title">Editar Perfil</h1>
          <button className="btn-cancel" onClick={handleCancel} type="button">
            Cancelar
          </button>
        </header>

        <form onSubmit={handleSubmit(onSubmit)} className="profile-edit-form">
          <div className="profile-edit-content">
            {/* User Story 1: Basic Info Section */}
            <BasicInfoSection register={register} errors={errors} bioLength={bioLength} />

            {/* User Story 2: Photo Upload Section */}
            <PhotoUploadSection
              currentPhotoUrl={currentPhotoUrl}
              onPhotoSelected={handleFileSelected}
              onRemovePhoto={handleRemovePhoto}
              uploadProgress={uploadProgress}
              isUploading={isUploading}
            />

            {/* User Story 4: Privacy Settings Section */}
            <PrivacySettingsSection
              register={register}
              errors={errors}
              profileVisibility={profileVisibility}
              tripVisibility={tripVisibility}
            />
          </div>

          {/* Save Button */}
          <div className="profile-edit-actions">
            <button
              type="submit"
              className="btn-save"
              disabled={isSaving || isSubmitting || !isDirty}
            >
              {isSaving ? (
                <>
                  <span className="spinner"></span>
                  Guardando...
                </>
              ) : (
                'Guardar Cambios'
              )}
            </button>
            {isDirty && (
              <p className="unsaved-indicator">
                <span className="unsaved-dot"></span>
                Tienes cambios sin guardar
              </p>
            )}
          </div>
        </form>

        {/* User Story 3: Password Change Section (separate form) */}
        <form
          onSubmit={handleSubmitPassword(onPasswordSubmit)}
          className="password-change-form"
        >
          <div className="profile-edit-content">
            <PasswordChangeSection
              register={registerPassword}
              errors={passwordErrors}
              newPasswordValue={newPassword}
            />
          </div>

          {/* Password Change Button */}
          <div className="profile-edit-actions">
            <button
              type="submit"
              className="btn-save btn-password-save"
              disabled={isChangingPassword || isPasswordSubmitting || !isPasswordDirty}
            >
              {isChangingPassword ? (
                <>
                  <span className="spinner"></span>
                  Cambiando contraseña...
                </>
              ) : (
                'Cambiar Contraseña'
              )}
            </button>
            {isPasswordDirty && (
              <p className="unsaved-indicator">
                <span className="unsaved-dot"></span>
                Cambios pendientes en la contraseña
              </p>
            )}
          </div>
        </form>

        {/* Photo Crop Modal (lazy loaded) */}
        {isCropModalOpen && previewUrl && (
          <Suspense fallback={<div>Cargando...</div>}>
            <PhotoCropModal
              photoUrl={previewUrl}
              onSave={handleCropSave}
              onCancel={handleCropCancel}
              isSaving={isUploading}
            />
          </Suspense>
        )}
      </div>
    </div>
  );
};

export default ProfileEditPage;
