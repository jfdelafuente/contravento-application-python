/**
 * BasicInfoSection Component
 *
 * Form section for editing basic profile information:
 * - Bio (max 500 characters with counter)
 * - Location (free text)
 * - Cycling Type (dropdown)
 */

import React from 'react';
import { UseFormRegister, FieldErrors } from 'react-hook-form';
import { CYCLING_TYPES } from '../../types/profile';
import type { ProfileFormData } from '../../types/profile';
import './BasicInfoSection.css';

interface BasicInfoSectionProps {
  register: UseFormRegister<ProfileFormData>;
  errors: FieldErrors<ProfileFormData>;
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
      <h2 className="section-title">Información Básica</h2>

      {/* Bio Field */}
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
            rows={5}
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
            >
              {bioLength} / {maxBioLength}
            </span>
          </div>
        </div>
        {errors.bio && (
          <p className="form-error">{errors.bio.message}</p>
        )}
      </div>

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
          <p className="form-error">{errors.location.message}</p>
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
          <p className="form-error">{errors.cycling_type.message}</p>
        )}
      </div>
    </section>
  );
};

export default BasicInfoSection;
