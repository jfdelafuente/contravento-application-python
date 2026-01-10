/**
 * PasswordChangeSection Component
 *
 * Form section for changing user password with comprehensive validation,
 * strength indicator, and visual feedback on password requirements.
 *
 * Features:
 * - Current password input with show/hide toggle
 * - New password input with real-time strength indicator
 * - Confirm password input with matching validation
 * - Visual requirements checklist (min length, uppercase, lowercase, number)
 * - Password strength meter (weak/medium/strong)
 * - Accessible password toggle buttons
 * - Form validation with error messages
 *
 * @component
 * @example
 * ```tsx
 * <PasswordChangeSection
 *   register={registerPassword}
 *   errors={passwordErrors}
 *   newPasswordValue={newPassword}
 * />
 * ```
 */

import React, { useState } from 'react';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import { calculatePasswordStrength } from '../../utils/validators';
import type { PasswordStrength } from '../../types/profile';
import './PasswordChangeSection.css';

/**
 * Props for PasswordChangeSection component
 */
export interface PasswordChangeSectionProps {
  /** React Hook Form register function for form fields */
  register: UseFormRegister<any>;
  /** Form validation errors object */
  errors: FieldErrors;
  /** Current value of new password field (watched for strength calculation) */
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
    <section className="password-change-section" aria-labelledby="password-change-title">
      <h2 id="password-change-title" className="section-title">Cambiar Contraseña</h2>

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
          <p className="form-error" role="alert">
            <span className="error-icon" aria-hidden="true">⚠</span>
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
          <p className="form-error" role="alert">
            <span className="error-icon" aria-hidden="true">⚠</span>
            {errors.new_password.message as string}
          </p>
        )}

        {/* Password Strength Indicator */}
        {newPasswordValue && (
          <div className="password-strength" role="status" aria-live="polite">
            <div className="strength-bar-container" role="progressbar" aria-label="Fuerza de la contraseña">
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
        <div className="password-requirements" aria-label="Requisitos de contraseña">
          <p className="requirements-title">Requisitos:</p>
          <ul className="requirements-list">
            <li className={hasMinLength ? 'requirement-met' : 'requirement-unmet'} aria-label={hasMinLength ? 'Requisito cumplido: Mínimo 8 caracteres' : 'Requisito pendiente: Mínimo 8 caracteres'}>
              <span aria-hidden="true">{hasMinLength ? '✓' : '○'}</span> Mínimo 8 caracteres
            </li>
            <li className={hasUppercase ? 'requirement-met' : 'requirement-unmet'} aria-label={hasUppercase ? 'Requisito cumplido: Al menos una mayúscula' : 'Requisito pendiente: Al menos una mayúscula'}>
              <span aria-hidden="true">{hasUppercase ? '✓' : '○'}</span> Al menos una mayúscula
            </li>
            <li className={hasLowercase ? 'requirement-met' : 'requirement-unmet'} aria-label={hasLowercase ? 'Requisito cumplido: Al menos una minúscula' : 'Requisito pendiente: Al menos una minúscula'}>
              <span aria-hidden="true">{hasLowercase ? '✓' : '○'}</span> Al menos una minúscula
            </li>
            <li className={hasNumber ? 'requirement-met' : 'requirement-unmet'} aria-label={hasNumber ? 'Requisito cumplido: Al menos un número' : 'Requisito pendiente: Al menos un número'}>
              <span aria-hidden="true">{hasNumber ? '✓' : '○'}</span> Al menos un número
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
          <p className="form-error" role="alert">
            <span className="error-icon" aria-hidden="true">⚠</span>
            {errors.confirm_password.message as string}
          </p>
        )}
      </div>
    </section>
  );
};

export default PasswordChangeSection;
