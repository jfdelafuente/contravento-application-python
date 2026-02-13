/**
 * BasicInfoSection Component
 *
 * Form section for editing basic profile information including bio, location, and cycling preferences.
 *
 * Features:
 * - Bio textarea with real-time character counter (max 500 characters)
 * - Location input field with placeholder guidance
 * - Cycling type dropdown with predefined options
 * - Real-time validation and error display
 * - Accessible form controls with proper ARIA labels
 *
 * @component
 * @example
 * ```tsx
 * <BasicInfoSection
 *   register={register}
 *   errors={errors}
 *   bioLength={bioLength}
 * />
 * ```
 */

import React from 'react';
import { UseFormRegister, FieldErrors } from 'react-hook-form';
import { CYCLING_TYPES } from '../../types/profile';
import type { ProfileFormData } from '../../types/profile';
import './BasicInfoSection.css';

/**
 * Props for BasicInfoSection component
 */
interface BasicInfoSectionProps {
  /** React Hook Form register function for form fields */
  register: UseFormRegister<ProfileFormData>;
  /** Form validation errors */
  errors: FieldErrors<ProfileFormData>;
  /** Current length of bio text for character counter */
  bioLength: number;
}

export const BasicInfoSection: React.FC<BasicInfoSectionProps> = ({
  register,
  errors,
  bioLength,
}) => {
  const maxBioLength = 500;
  const remainingChars = maxBioLength - bioLength;
  const isNearLimit = remainingChars <= 50;
  const isAtLimit = remainingChars <= 0;

  return (
    <section className="basic-info-section">
      <div className="basic-info-grid">
        {/* Left Column: Bio */}
        <div className="basic-info-column">
          <div className="form-group">
            <label htmlFor="bio" className="form-label">
              Bio
              <span className="form-label-optional">(opcional)</span>
            </label>
            <div className="textarea-wrapper">
              <textarea
                id="bio"
                {...register('bio')}
                className={`form-textarea ${errors.bio ? 'form-textarea--error' : ''}`}
                placeholder="Cuéntanos sobre ti, tus aventuras en bicicleta, tus rutas favoritas..."
                rows={8}
                maxLength={maxBioLength}
              />
              <div className="char-counter-wrapper">
                <span
                  className={`char-counter ${
                    isAtLimit
                      ? 'char-counter--limit'
                      : isNearLimit
                      ? 'char-counter--warning'
                      : ''
                  }`}
                  aria-live="polite"
                  aria-label={`Caracteres utilizados: ${bioLength} de ${maxBioLength}`}
                >
                  {bioLength} / {maxBioLength}
                </span>
              </div>
            </div>
            {errors.bio && (
              <p className="form-error" role="alert">{errors.bio.message}</p>
            )}
          </div>
        </div>

        {/* Right Column: Location + Cycling Type */}
        <div className="basic-info-column">
          {/* Location Field */}
          <div className="form-group">
            <label htmlFor="location" className="form-label">
              Ubicación
              <span className="form-label-optional">(opcional)</span>
            </label>
            <input
              type="text"
              id="location"
              {...register('location')}
              className={`form-input ${errors.location ? 'form-input--error' : ''}`}
              placeholder="Barcelona, España"
            />
            {errors.location && (
              <p className="form-error" role="alert">{errors.location.message}</p>
            )}
          </div>

          {/* Cycling Type Field */}
          <div className="form-group">
            <label htmlFor="cycling_type" className="form-label">
              Tipo de Ciclismo
              <span className="form-label-optional">(opcional)</span>
            </label>
            <select
              id="cycling_type"
              {...register('cycling_type')}
              className={`form-select ${errors.cycling_type ? 'form-select--error' : ''}`}
            >
              <option value="">Selecciona tu estilo preferido</option>
              {CYCLING_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
            {errors.cycling_type && (
              <p className="form-error" role="alert">{errors.cycling_type.message}</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default BasicInfoSection;
