// src/components/auth/ForgotPasswordForm.tsx

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authService } from '../../services/authService';
import { TurnstileWidget } from './TurnstileWidget';
import type { APIError } from '../../types/api';
import './ForgotPasswordForm.css';

// Validation schema
const forgotPasswordSchema = z.object({
  email: z.string().email('Email inválido'),
});

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

interface ForgotPasswordFormProps {
  /** Callback on successful password reset request */
  onSuccess: (email: string) => void;
  /** Callback on error (optional) */
  onError?: (message: string) => void;
}

/**
 * Forgot password form with email field and CAPTCHA
 *
 * Handles:
 * - Email validation
 * - CAPTCHA verification
 * - Success messaging with email sent confirmation
 */
export const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({
  onSuccess,
  onError,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [generalError, setGeneralError] = useState<string | null>(null);

  const onSubmit = async (data: ForgotPasswordFormValues) => {
    setGeneralError(null);

    if (!turnstileToken) {
      setGeneralError('Por favor completa la verificación de seguridad.');
      return;
    }

    try {
      const emailSentTo = await authService.requestPasswordReset(
        data.email,
        turnstileToken
      );

      onSuccess(emailSentTo);
    } catch (error) {
      const apiError = error as APIError;

      // Handle rate limiting
      if (apiError.response?.status === 429) {
        const message =
          apiError.response.data?.error?.message ||
          'Demasiados intentos. Por favor espera antes de intentar de nuevo.';
        setGeneralError(message);
        if (onError) onError(message);
        return;
      }

      // Handle user not found (we show generic message for security)
      if (
        apiError.response?.status === 404 &&
        apiError.response.data?.error?.code === 'USER_NOT_FOUND'
      ) {
        // Don't reveal if email exists - show success message anyway
        onSuccess(data.email);
        return;
      }

      // Generic error fallback
      const message =
        apiError.response?.data?.error?.message ||
        'Error al solicitar recuperación de contraseña. Inténtalo de nuevo.';
      setGeneralError(message);
      if (onError) onError(message);
    }
  };

  const handleTurnstileVerify = (token: string) => {
    setTurnstileToken(token);
    setGeneralError(null);
  };

  const handleTurnstileError = () => {
    setGeneralError(
      'Error en la verificación de seguridad. Por favor inténtalo de nuevo.'
    );
  };

  return (
    <form className="forgot-password-form" onSubmit={handleSubmit(onSubmit)} noValidate>
      {/* General error display */}
      {generalError && (
        <div className="form-error" role="alert">
          {generalError}
        </div>
      )}

      <p className="form-description">
        Ingresa tu email y te enviaremos un enlace para restablecer tu contraseña.
      </p>

      {/* Email field */}
      <div className="form-field">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          {...register('email')}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <span id="email-error" className="field-error" role="alert">
            {errors.email.message}
          </span>
        )}
      </div>

      {/* Turnstile CAPTCHA */}
      <div className="form-field">
        <TurnstileWidget
          onVerify={handleTurnstileVerify}
          onError={handleTurnstileError}
          action="forgot-password"
        />
      </div>

      {/* Submit button */}
      <button
        type="submit"
        className="submit-button"
        disabled={isSubmitting || !turnstileToken}
      >
        {isSubmitting ? 'Enviando...' : 'Enviar enlace de recuperación'}
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
