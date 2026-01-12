// src/components/auth/ResetPasswordForm.tsx

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authService } from '../../services/authService';
import { PasswordStrengthMeter } from './PasswordStrengthMeter';
import type { ApiError } from '../../types/api';
import './ResetPasswordForm.css';

// Validation schema
const resetPasswordSchema = z
  .object({
    newPassword: z
      .string()
      .min(8, 'La contraseña debe tener al menos 8 caracteres')
      .regex(/[A-Z]/, 'Debe contener al menos una letra mayúscula')
      .regex(/[a-z]/, 'Debe contener al menos una letra minúscula')
      .regex(/\d/, 'Debe contener al menos un número'),
    confirmPassword: z.string().min(1, 'Confirma tu contraseña'),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'Las contraseñas no coinciden',
    path: ['confirmPassword'],
  });

type ResetPasswordFormValues = z.infer<typeof resetPasswordSchema>;

interface ResetPasswordFormProps {
  /** Reset token from URL */
  token: string;
  /** Callback on successful password reset */
  onSuccess: () => void;
  /** Callback on token error (expired or invalid) */
  onTokenError?: (code: string, message: string) => void;
  /** Callback on other errors (optional) */
  onError?: (message: string) => void;
}

/**
 * Reset password form with new password fields and strength meter
 *
 * Handles:
 * - New password validation with strength requirements
 * - Password confirmation matching
 * - Token validation (expired, invalid)
 * - Success messaging
 */
export const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({
  token,
  onSuccess,
  onTokenError,
  onError,
}) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const [generalError, setGeneralError] = useState<string | null>(null);

  const newPassword = watch('newPassword') || '';

  const onSubmit = async (data: ResetPasswordFormValues) => {
    setGeneralError(null);

    try {
      await authService.resetPassword(token, data.newPassword);
      onSuccess();
    } catch (error) {
      const apiError = error as ApiError;

      // Handle token errors
      if (apiError.response?.status === 400) {
        const errorCode = apiError.response.data?.error?.code;

        if (errorCode === 'TOKEN_EXPIRED') {
          const message =
            apiError.response.data?.error?.message ||
            'El enlace de recuperación ha expirado. Solicita uno nuevo.';
          if (onTokenError) {
            onTokenError(errorCode, message);
          } else {
            setGeneralError(message);
          }
          return;
        }

        if (errorCode === 'INVALID_TOKEN') {
          const message =
            apiError.response.data?.error?.message ||
            'El enlace de recuperación es inválido. Solicita uno nuevo.';
          if (onTokenError) {
            onTokenError(errorCode, message);
          } else {
            setGeneralError(message);
          }
          return;
        }
      }

      // Handle weak password error
      if (
        apiError.response?.status === 400 &&
        apiError.response.data?.error?.code === 'WEAK_PASSWORD'
      ) {
        const message =
          apiError.response.data?.error?.message ||
          'La contraseña no cumple con los requisitos de seguridad.';
        setGeneralError(message);
        if (onError) onError(message);
        return;
      }

      // Generic error fallback
      const message =
        apiError.response?.data?.error?.message ||
        'Error al restablecer contraseña. Inténtalo de nuevo.';
      setGeneralError(message);
      if (onError) onError(message);
    }
  };

  return (
    <form className="reset-password-form" onSubmit={handleSubmit(onSubmit)} noValidate>
      {/* General error display */}
      {generalError && (
        <div className="form-error" role="alert">
          {generalError}
        </div>
      )}

      <p className="form-description">
        Ingresa tu nueva contraseña. Debe ser segura y diferente de contraseñas anteriores.
      </p>

      {/* New password field */}
      <div className="form-field">
        <label htmlFor="newPassword">Nueva contraseña</label>
        <input
          id="newPassword"
          type="password"
          autoComplete="new-password"
          {...register('newPassword')}
          aria-invalid={!!errors.newPassword}
          aria-describedby={errors.newPassword ? 'newPassword-error' : undefined}
        />
        {errors.newPassword && (
          <span id="newPassword-error" className="field-error" role="alert">
            {errors.newPassword.message}
          </span>
        )}

        {/* Password strength meter */}
        {newPassword && (
          <div className="password-strength-container">
            <PasswordStrengthMeter password={newPassword} />
          </div>
        )}
      </div>

      {/* Confirm password field */}
      <div className="form-field">
        <label htmlFor="confirmPassword">Confirmar contraseña</label>
        <input
          id="confirmPassword"
          type="password"
          autoComplete="new-password"
          {...register('confirmPassword')}
          aria-invalid={!!errors.confirmPassword}
          aria-describedby={errors.confirmPassword ? 'confirmPassword-error' : undefined}
        />
        {errors.confirmPassword && (
          <span id="confirmPassword-error" className="field-error" role="alert">
            {errors.confirmPassword.message}
          </span>
        )}
      </div>

      {/* Submit button */}
      <button
        type="submit"
        className="submit-button"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Restableciendo...' : 'Restablecer contraseña'}
      </button>

      {/* Back to login link */}
      <div className="form-footer">
        <p>
          <a href="/login">Volver a iniciar sesión</a>
        </p>
      </div>
    </form>
  );
};
