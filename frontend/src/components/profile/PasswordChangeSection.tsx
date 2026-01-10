/**
 * PasswordChangeSection
 *
 * Component for changing user password with current password verification,
 * real-time strength indicator, and validation feedback.
 */

import React, { useState } from 'react';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import { calculatePasswordStrength } from '../../utils/validators';
import type { PasswordStrength } from '../../types/profile';
import './PasswordChangeSection.css';

export interface PasswordChangeSectionProps {
  /** React Hook Form register function */
  register: UseFormRegister<any>;
  /** Form errors from validation */
  errors: FieldErrors;
  /** New password value (watched for strength calculation) */
  newPasswordValue?: string;
}

export const PasswordChangeSection: React.FC<PasswordChangeSectionProps> = ({
  register,
  errors,
  newPasswordValue = '',
}) => {
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Calculate password strength
  const strength: PasswordStrength = calculatePasswordStrength(newPasswordValue);

  // Determine if requirements are met
  const hasMinLength = newPasswordValue.length >= 8;
  const hasUppercase = /[A-Z]/.test(newPasswordValue);
  const hasLowercase = /[a-z]/.test(newPasswordValue);
  const hasNumber = /\d/.test(newPasswordValue);

  return (
    <section className="password-change-section">
      <h2 className="section-title">Cambiar Contraseña</h2>

      {/* Current Password */}
      <div className="form-group">
        <label htmlFor="current_password" className="form-label">
          Contraseña Actual
        </label>
        <div className="password-input-wrapper">
          <input
            id="current_password"
            type={showCurrentPassword ? 'text' : 'password'}
            {...register('current_password')}
            className={`form-input ${errors.current_password ? 'form-input--error' : ''}`}
            placeholder="Ingresa tu contraseña actual"
            autoComplete="current-password"
          />
          <button
            type="button"
            className="password-toggle"
            onClick={() => setShowCurrentPassword(!showCurrentPassword)}
            aria-label={showCurrentPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            {showCurrentPassword ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        </div>
        {errors.current_password && (
          <p className="form-error">
            <span className="error-icon">⚠</span>
            {errors.current_password.message as string}
          </p>
        )}
      </div>

      {/* New Password */}
      <div className="form-group">
        <label htmlFor="new_password" className="form-label">
          Nueva Contraseña
        </label>
        <div className="password-input-wrapper">
          <input
            id="new_password"
            type={showNewPassword ? 'text' : 'password'}
            {...register('new_password')}
            className={`form-input ${errors.new_password ? 'form-input--error' : ''}`}
            placeholder="Ingresa tu nueva contraseña"
            autoComplete="new-password"
          />
          <button
            type="button"
            className="password-toggle"
            onClick={() => setShowNewPassword(!showNewPassword)}
            aria-label={showNewPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            {showNewPassword ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        </div>
        {errors.new_password && (
          <p className="form-error">
            <span className="error-icon">⚠</span>
            {errors.new_password.message as string}
          </p>
        )}

        {/* Password Strength Indicator */}
        {newPasswordValue && (
          <div className="password-strength">
            <div className="strength-bar-container">
              <div className={`strength-bar strength-bar--${strength}`} />
            </div>
            <p className={`strength-label strength-label--${strength}`}>
              {strength === 'weak' && 'Débil'}
              {strength === 'medium' && 'Media'}
              {strength === 'strong' && 'Fuerte'}
            </p>
          </div>
        )}

        {/* Requirements Checklist */}
        <div className="password-requirements">
          <p className="requirements-title">Requisitos:</p>
          <ul className="requirements-list">
            <li className={hasMinLength ? 'requirement-met' : 'requirement-unmet'}>
              {hasMinLength ? '✓' : '○'} Mínimo 8 caracteres
            </li>
            <li className={hasUppercase ? 'requirement-met' : 'requirement-unmet'}>
              {hasUppercase ? '✓' : '○'} Al menos una mayúscula
            </li>
            <li className={hasLowercase ? 'requirement-met' : 'requirement-unmet'}>
              {hasLowercase ? '✓' : '○'} Al menos una minúscula
            </li>
            <li className={hasNumber ? 'requirement-met' : 'requirement-unmet'}>
              {hasNumber ? '✓' : '○'} Al menos un número
            </li>
          </ul>
        </div>
      </div>

      {/* Confirm Password */}
      <div className="form-group">
        <label htmlFor="confirm_password" className="form-label">
          Confirmar Nueva Contraseña
        </label>
        <div className="password-input-wrapper">
          <input
            id="confirm_password"
            type={showConfirmPassword ? 'text' : 'password'}
            {...register('confirm_password')}
            className={`form-input ${errors.confirm_password ? 'form-input--error' : ''}`}
            placeholder="Confirma tu nueva contraseña"
            autoComplete="new-password"
          />
          <button
            type="button"
            className="password-toggle"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            aria-label={showConfirmPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          >
            {showConfirmPassword ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            )}
          </button>
        </div>
        {errors.confirm_password && (
          <p className="form-error">
            <span className="error-icon">⚠</span>
            {errors.confirm_password.message as string}
          </p>
        )}
      </div>
    </section>
  );
};

export default PasswordChangeSection;
