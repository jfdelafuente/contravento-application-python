/**
 * PrivacySettingsSection Component
 *
 * Form section for configuring user privacy settings with intuitive radio button controls.
 *
 * Features:
 * - Profile visibility control (public/private)
 * - Trip visibility control (public/followers/private)
 * - Visual icons for each privacy level
 * - Clear descriptions for each option
 * - Radio button groups with proper ARIA labels
 * - Real-time validation and error display
 *
 * Privacy Levels:
 * - **Public**: Content visible to everyone
 * - **Followers**: Content visible only to followers
 * - **Private**: Content visible only to the user
 *
 * @component
 * @example
 * ```tsx
 * <PrivacySettingsSection
 *   register={register}
 *   errors={errors}
 *   profileVisibility="public"
 *   tripVisibility="followers"
 * />
 * ```
 */

import React from 'react';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import './PrivacySettingsSection.css';

/**
 * Props for PrivacySettingsSection component
 */
export interface PrivacySettingsSectionProps {
  /** React Hook Form register function for form fields */
  register: UseFormRegister<any>;
  /** Form validation errors object */
  errors: FieldErrors;
  /** Current profile visibility setting (public/private) */
  profileVisibility?: string;
  /** Current trip visibility setting (public/followers/private) */
  tripVisibility?: string;
}

export const PrivacySettingsSection: React.FC<PrivacySettingsSectionProps> = ({
  register,
  errors,
  profileVisibility = 'public',
  tripVisibility = 'public',
}) => {
  return (
    <section className="privacy-settings-section" aria-labelledby="privacy-settings-title">
      <h2 id="privacy-settings-title" className="section-title">Configuración de Privacidad</h2>

      {/* Profile Visibility */}
      <div className="form-group">
        <div className="privacy-header">
          <label htmlFor="profile_visibility" className="form-label">
            Visibilidad del Perfil
          </label>
          <p className="privacy-description">
            Controla quién puede ver tu perfil y tu información
          </p>
        </div>

        <div className="radio-group" role="radiogroup" aria-labelledby="profile_visibility">
          <label className="radio-option">
            <input
              type="radio"
              {...register('profile_visibility')}
              value="public"
              className="radio-input"
              aria-describedby="profile-public-help"
            />
            <div className="radio-content">
              <div className="radio-label">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="radio-icon"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <span className="radio-title">Público</span>
              </div>
              <p id="profile-public-help" className="radio-help">Cualquiera puede ver tu perfil</p>
            </div>
          </label>

          <label className="radio-option">
            <input
              type="radio"
              {...register('profile_visibility')}
              value="private"
              className="radio-input"
              aria-describedby="profile-private-help"
            />
            <div className="radio-content">
              <div className="radio-label">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="radio-icon"
                >
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                <span className="radio-title">Privado</span>
              </div>
              <p id="profile-private-help" className="radio-help">Solo tus seguidores pueden ver tu perfil</p>
            </div>
          </label>
        </div>

        {errors.profile_visibility && (
          <p className="form-error" role="alert">
            <span className="error-icon" aria-hidden="true">⚠</span>
            {errors.profile_visibility.message as string}
          </p>
        )}
      </div>

      {/* Trip Visibility */}
      <div className="form-group">
        <div className="privacy-header">
          <label htmlFor="trip_visibility" className="form-label">
            Visibilidad de Viajes
          </label>
          <p className="privacy-description">
            Controla quién puede ver tus viajes publicados
          </p>
        </div>

        <div className="radio-group" role="radiogroup" aria-labelledby="trip_visibility">
          <label className="radio-option">
            <input
              type="radio"
              {...register('trip_visibility')}
              value="public"
              className="radio-input"
              aria-describedby="trip-public-help"
            />
            <div className="radio-content">
              <div className="radio-label">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="radio-icon"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="2" y1="12" x2="22" y2="12" />
                  <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <span className="radio-title">Público</span>
              </div>
              <p id="trip-public-help" className="radio-help">Cualquiera puede ver tus viajes</p>
            </div>
          </label>

          <label className="radio-option">
            <input
              type="radio"
              {...register('trip_visibility')}
              value="followers"
              className="radio-input"
              aria-describedby="trip-followers-help"
            />
            <div className="radio-content">
              <div className="radio-label">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="radio-icon"
                >
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                <span className="radio-title">Solo Seguidores</span>
              </div>
              <p id="trip-followers-help" className="radio-help">Solo tus seguidores pueden ver tus viajes</p>
            </div>
          </label>

          <label className="radio-option">
            <input
              type="radio"
              {...register('trip_visibility')}
              value="private"
              className="radio-input"
              aria-describedby="trip-private-help"
            />
            <div className="radio-content">
              <div className="radio-label">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="radio-icon"
                >
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                <span className="radio-title">Privado</span>
              </div>
              <p id="trip-private-help" className="radio-help">Solo tú puedes ver tus viajes</p>
            </div>
          </label>
        </div>

        {errors.trip_visibility && (
          <p className="form-error" role="alert">
            <span className="error-icon" aria-hidden="true">⚠</span>
            {errors.trip_visibility.message as string}
          </p>
        )}
      </div>
    </section>
  );
};

export default PrivacySettingsSection;
