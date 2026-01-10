/**
 * PrivacySettingsSection
 *
 * Component for configuring account privacy settings including profile visibility
 * (public/private) and trip visibility (public/followers only/private).
 */

import React from 'react';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import './PrivacySettingsSection.css';

export interface PrivacySettingsSectionProps {
  /** React Hook Form register function */
  register: UseFormRegister<any>;
  /** Form errors from validation */
  errors: FieldErrors;
  /** Current profile visibility value */
  profileVisibility?: string;
  /** Current trip visibility value */
  tripVisibility?: string;
}

export const PrivacySettingsSection: React.FC<PrivacySettingsSectionProps> = ({
  register,
  errors,
  profileVisibility = 'public',
  tripVisibility = 'public',
}) => {
  return (
    <section className="privacy-settings-section">
      <h2 className="section-title">Configuración de Privacidad</h2>

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

        <div className="radio-group">
          <label className="radio-option">
            <input
              type="radio"
              {...register('profile_visibility')}
              value="public"
              className="radio-input"
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
              <p className="radio-help">Cualquiera puede ver tu perfil</p>
            </div>
          </label>

          <label className="radio-option">
            <input
              type="radio"
              {...register('profile_visibility')}
              value="private"
              className="radio-input"
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
              <p className="radio-help">Solo tus seguidores pueden ver tu perfil</p>
            </div>
          </label>
        </div>

        {errors.profile_visibility && (
          <p className="form-error">
            <span className="error-icon">⚠</span>
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

        <div className="radio-group">
          <label className="radio-option">
            <input
              type="radio"
              {...register('trip_visibility')}
              value="public"
              className="radio-input"
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
              <p className="radio-help">Cualquiera puede ver tus viajes</p>
            </div>
          </label>

          <label className="radio-option">
            <input
              type="radio"
              {...register('trip_visibility')}
              value="followers"
              className="radio-input"
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
              <p className="radio-help">Solo tus seguidores pueden ver tus viajes</p>
            </div>
          </label>

          <label className="radio-option">
            <input
              type="radio"
              {...register('trip_visibility')}
              value="private"
              className="radio-input"
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
              <p className="radio-help">Solo tú puedes ver tus viajes</p>
            </div>
          </label>
        </div>

        {errors.trip_visibility && (
          <p className="form-error">
            <span className="error-icon">⚠</span>
            {errors.trip_visibility.message as string}
          </p>
        )}
      </div>
    </section>
  );
};

export default PrivacySettingsSection;
