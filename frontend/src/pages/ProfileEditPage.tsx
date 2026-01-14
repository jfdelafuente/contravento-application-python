/**
 * ProfileEditPage Component
 *
 * Main page for editing user profile with multiple sections organized in a card-based layout.
 * Uses rustic design aesthetic with gradient backgrounds and decorative elements.
 *
 * Features:
 * - **Basic Info Section**: Edit bio, location, and cycling type preferences
 * - **Photo Upload Section**: Upload, crop, and manage profile photo
 * - **Password Change Section**: Change password with strength validation
 * - **Privacy Settings Section**: Configure profile and trip visibility
 *
 * Layout:
 * - Row 1: Basic Info (left) + Photo Upload (right) - 2 columns
 * - Row 2: Password Change - full width
 * - Row 3: Privacy Settings - full width
 *
 * Each section has:
 * - Separate form for independent submission
 * - Save button that enables only when form is dirty
 * - Unsaved changes indicator with visual dot
 * - Loading states during API calls
 *
 * User Experience:
 * - Warns before navigating away with unsaved changes
 * - Shows toast notifications for success/error states
 * - Auto-logout after password change for security
 * - Lazy-loads photo crop modal for better performance
 *
 * @component
 * @page
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
  const { user, refreshUser, logout } = useAuth();
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
    async (photoUrl) => {
      // Update local state when photo changes
      setCurrentPhotoUrl(photoUrl);
      // Refresh user data from server to get updated photo_url
      await refreshUser();
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

  // Reset form when user data is loaded/updated (Feature 013)
  useEffect(() => {
    if (user) {
      reset({
        bio: user.bio || '',
        location: user.location || '',
        cycling_type: user.cycling_type || '',
        profile_visibility: user.profile_visibility || 'public',
        trip_visibility: user.trip_visibility || 'public',
      });
    }
  }, [user, reset]);

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

      // Refresh user data to get updated values from server (Feature 013)
      await refreshUser();

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
          <h1 id="profile-edit-title" className="profile-edit-title">Editar Perfil</h1>
          <button className="btn-cancel" onClick={handleCancel} type="button" aria-label="Volver al perfil">
            Volver
          </button>
        </header>

        <div className="profile-edit-content-wrapper" aria-labelledby="profile-edit-title">
          {/* Primera fila: Información Básica + Foto de Perfil */}
          <div className="profile-edit-row">
            {/* Información Básica */}
            <form onSubmit={handleSubmit(onSubmit)} aria-label="Formulario de información básica">
              <div className="profile-edit-section">
                <div className="section-content">
                  <BasicInfoSection register={register} errors={errors} bioLength={bioLength} />
                </div>
                <div className="section-actions">
                  <button
                    type="submit"
                    className="btn-save"
                    disabled={isSaving || isSubmitting || !isDirty}
                    aria-label={isSaving ? 'Guardando cambios' : 'Guardar cambios de información básica'}
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
                    <p className="unsaved-indicator" role="status" aria-live="polite">
                      <span className="unsaved-dot" aria-hidden="true"></span>
                      Tienes cambios sin guardar
                    </p>
                  )}
                </div>
              </div>
            </form>

            {/* Foto de Perfil */}
            <div className="profile-edit-section">
              <div className="section-content">
                <PhotoUploadSection
                  currentPhotoUrl={currentPhotoUrl}
                  onPhotoSelected={handleFileSelected}
                  onRemovePhoto={handleRemovePhoto}
                  uploadProgress={uploadProgress}
                  isUploading={isUploading}
                />
              </div>
              <div className="section-actions">
                <p className="temp-message" style={{ fontSize: 'var(--text-xs)', padding: 'var(--space-2)' }}>
                  {isUploading ? 'Subiendo foto...' : 'Selecciona una foto para cambiarla'}
                </p>
              </div>
            </div>
          </div>

          {/* Segunda fila: Cambio de Contraseña + Configuración de Privacidad */}
          <div className="profile-edit-row">
            {/* Cambio de Contraseña */}
            <form onSubmit={handleSubmitPassword(onPasswordSubmit)} aria-label="Formulario de cambio de contraseña">
              <div className="profile-edit-section">
                <div className="section-content">
                  <PasswordChangeSection
                    register={registerPassword}
                    errors={passwordErrors}
                    newPasswordValue={newPassword}
                  />
                </div>
                <div className="section-actions">
                  <button
                    type="submit"
                    className="btn-save"
                    disabled={isChangingPassword || isPasswordSubmitting || !isPasswordDirty}
                    aria-label={isChangingPassword ? 'Cambiando contraseña' : 'Cambiar contraseña'}
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
                    <p className="unsaved-indicator" role="status" aria-live="polite">
                      <span className="unsaved-dot" aria-hidden="true"></span>
                      Cambios pendientes en la contraseña
                    </p>
                  )}
                </div>
              </div>
            </form>

            {/* Configuración de Privacidad */}
            <form onSubmit={handleSubmit(onSubmit)} aria-label="Formulario de configuración de privacidad">
              <div className="profile-edit-section">
                <div className="section-content">
                  <PrivacySettingsSection
                    register={register}
                    errors={errors}
                    profileVisibility={profileVisibility}
                    tripVisibility={tripVisibility}
                  />
                </div>
                <div className="section-actions">
                  <button
                    type="submit"
                    className="btn-save"
                    disabled={isSaving || isSubmitting || !isDirty}
                    aria-label={isSaving ? 'Guardando configuración' : 'Guardar configuración de privacidad'}
                  >
                    {isSaving ? (
                      <>
                        <span className="spinner"></span>
                        Guardando...
                      </>
                    ) : (
                      'Guardar Configuración'
                    )}
                  </button>
                  {isDirty && (
                    <p className="unsaved-indicator" role="status" aria-live="polite">
                      <span className="unsaved-dot" aria-hidden="true"></span>
                      Tienes cambios sin guardar
                    </p>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>

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
