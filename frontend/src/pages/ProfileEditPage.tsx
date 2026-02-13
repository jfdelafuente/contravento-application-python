/**
 * ProfileEditPage Component - "Trail Journal Checkpoints"
 *
 * Vertical sections profile editing interface for cyclists updating their trail journal.
 * Organized, sequential, warm layout with numbered checkpoint badges.
 *
 * Features:
 * - **Vertical Stack Layout**: 4 sections displayed sequentially, one below another
 * - **Section 1**: Información Básica - Bio, location, cycling type
 * - **Section 2**: Foto de Perfil - Upload, crop, and manage profile photo
 * - **Section 3**: Cambiar Contraseña - Change password with strength validation
 * - **Section 4**: Configuración de Privacidad - Profile and trip visibility settings
 *
 * Each section:
 * - Numbered badge (1 de 4, 2 de 4, etc.) as trail checkpoint marker
 * - Independent form submission
 * - Save button enabled only when dirty
 * - Unsaved changes indicator
 * - Olive accent line on header
 *
 * @component
 * @page
 */

import React, { useState, useEffect, lazy, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import HeaderQuickActions from '../components/dashboard/HeaderQuickActions';
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
import './DashboardPage.css'; // For dashboard-header__logo styles

// Lazy load PhotoCropModal
const PhotoCropModal = lazy(() => import('../components/profile/PhotoCropModal'));

export const ProfileEditPage: React.FC = () => {
  const { user, refreshUser, logout } = useAuth();
  const navigate = useNavigate();
  const [isSaving, setIsSaving] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [currentPhotoUrl, setCurrentPhotoUrl] = useState(user?.photo_url || '');

  // Profile form (for basic info + privacy)
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

  // Watch privacy settings
  const profileVisibility = watch('profile_visibility');
  const tripVisibility = watch('trip_visibility');

  // Photo upload
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
      setCurrentPhotoUrl(photoUrl);
      await refreshUser();
    }
  );

  // Password change
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

  // Reset form when user data loads
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

  // Warn about unsaved changes
  useUnsavedChanges(
    isDirty || isPasswordDirty,
    'Tienes cambios sin guardar. ¿Estás seguro de que quieres salir?'
  );

  if (!user) {
    return null;
  }

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

      resetPassword();

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

      const updateData: ProfileUpdateRequest = {
        bio: data.bio || undefined,
        location: data.location || undefined,
        cycling_type: data.cycling_type || undefined,
        profile_visibility: data.profile_visibility,
        trip_visibility: data.trip_visibility,
      };

      await updateProfile(user?.username || '', updateData);
      await refreshUser();

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

      reset(data);

      setTimeout(() => {
        navigate('/profile');
      }, 1000);
    } catch (error: any) {
      console.error('Error updating profile:', error);

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
      <header className="dashboard-header dashboard-header--route-map">
        <div className="dashboard-header__content">
          <div className="dashboard-header__brand">
            {/* Logo con estética de señalización de ruta */}
            <svg
              className="dashboard-header__logo-icon"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M12 2L2 7V17L12 22L22 17V7L12 2Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
              />
              <path
                d="M12 22V12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
              <path
                d="M2 7L12 12L22 7"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
            <div className="dashboard-header__brand-text">
              <span className="dashboard-header__brand-name">ContraVento</span>
              <span className="dashboard-header__brand-tagline">Tu mapa de rutas</span>
            </div>
          </div>

          <HeaderQuickActions />
          <UserMenu />
        </div>
      </header>

      <div className="profile-edit-container">
        {/* Page Title */}
        <div className="profile-edit-title-section">
          <h1 id="profile-edit-title" className="profile-edit-page-title">Editar Perfil</h1>
        </div>

        {/* Vertical Sections Stack - Trail Journal Checkpoints */}
        <div className="profile-edit-sections">
          {/* Section 1: Información Básica */}
          <section className="profile-edit-section" aria-labelledby="section-1-title">
            <div className="profile-edit-section-header">
              <div className="profile-edit-section-number" aria-label="Sección 1 de 4">1</div>
              <h2 id="section-1-title" className="profile-edit-section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                Información Básica
              </h2>
            </div>
            <div className="profile-edit-section-description">
            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="profile-edit-section-content">
                <BasicInfoSection register={register} errors={errors} bioLength={bioLength} />
              </div>

              <div className="profile-edit-section-actions">
                {isDirty && (
                  <p className="unsaved-indicator" role="status" aria-live="polite">
                    <span className="unsaved-dot" aria-hidden="true"></span>
                    Tienes cambios sin guardar
                  </p>
                )}
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
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Guardar Cambios
                    </>
                  )}
                </button>
              </div>
            </form>
            </div>
          </section>

          {/* Section 2: Foto de Perfil */}
          <section className="profile-edit-section" aria-labelledby="section-2-title">
            <div className="profile-edit-section-header">
              <div className="profile-edit-section-number" aria-label="Sección 2 de 4">2</div>
              <h2 id="section-2-title" className="profile-edit-section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
                Foto de Perfil
              </h2>
            </div>

            <div className="profile-edit-section-content">
              <PhotoUploadSection
                currentPhotoUrl={currentPhotoUrl}
                onPhotoSelected={handleFileSelected}
                onRemovePhoto={handleRemovePhoto}
                uploadProgress={uploadProgress}
                isUploading={isUploading}
              />
            </div>
          </section>

          {/* Section 3: Cambiar Contraseña */}
          <section className="profile-edit-section" aria-labelledby="section-3-title">
            <div className="profile-edit-section-header">
              <div className="profile-edit-section-number" aria-label="Sección 3 de 4">3</div>
              <h2 id="section-3-title" className="profile-edit-section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                Cambiar Contraseña
              </h2>
            </div>

            <form onSubmit={handleSubmitPassword(onPasswordSubmit)}>
              <div className="profile-edit-section-content">
                <PasswordChangeSection
                  register={registerPassword}
                  errors={passwordErrors}
                  newPasswordValue={newPassword}
                />
              </div>

              <div className="profile-edit-section-actions">
                {isPasswordDirty && (
                  <p className="unsaved-indicator" role="status" aria-live="polite">
                    <span className="unsaved-dot" aria-hidden="true"></span>
                    Cambios pendientes en la contraseña
                  </p>
                )}
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
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Cambiar Contraseña
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>

          {/* Section 4: Configuración de Privacidad */}
          <section className="profile-edit-section" aria-labelledby="section-4-title">
            <div className="profile-edit-section-header">
              <div className="profile-edit-section-number" aria-label="Sección 4 de 4">4</div>
              <h2 id="section-4-title" className="profile-edit-section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
                Configuración de Privacidad
              </h2>
            </div>

            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="profile-edit-section-content">
                <PrivacySettingsSection
                  register={register}
                  errors={errors}
                  profileVisibility={profileVisibility}
                  tripVisibility={tripVisibility}
                />
              </div>

              <div className="profile-edit-section-actions">
                {isDirty && (
                  <p className="unsaved-indicator" role="status" aria-live="polite">
                    <span className="unsaved-dot" aria-hidden="true"></span>
                    Tienes cambios sin guardar
                  </p>
                )}
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
                    <>
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                      Guardar Configuración
                    </>
                  )}
                </button>
              </div>
            </form>
          </section>
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
