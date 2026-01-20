// src/components/auth/LoginForm.tsx

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../../contexts/AuthContext';
import { AccountBlockedMessage } from './AccountBlockedMessage';
import { TurnstileWidget } from './TurnstileWidget';
import type { AxiosError } from 'axios';
import './LoginForm.css';

// Validation schema
const loginSchema = z.object({
  login: z.string().min(1, 'Usuario o email requerido'),
  password: z.string().min(1, 'La contraseña es requerida'),
  rememberMe: z.boolean().optional(),
});

type LoginFormValues = z.infer<typeof loginSchema>;

interface LoginFormProps {
  /** Callback on successful login */
  onSuccess: () => void;
  /** Callback on error (optional) */
  onError?: (message: string) => void;
  /** Callback when email not verified (optional) */
  onEmailNotVerified?: () => void;
}

/**
 * Login form with Remember Me, account blocking, and error handling
 *
 * Handles:
 * - Username/email + password validation (accepts both)
 * - Remember Me checkbox (affects refresh token duration)
 * - Account blocking with countdown timer (5 failed attempts = 15min block)
 * - Email verification enforcement
 * - Optional Turnstile CAPTCHA (if rate limited)
 */
export const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onError,
  onEmailNotVerified,
}) => {
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      rememberMe: false,
    },
  });

  const [blockedUntil, setBlockedUntil] = useState<string | null>(null);
  const [showTurnstile, setShowTurnstile] = useState(false);
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);
  const [generalError, setGeneralError] = useState<string | null>(null);

  const onSubmit = async (data: LoginFormValues) => {
    setGeneralError(null);

    try {
      await login(
        data.login,
        data.password,
        data.rememberMe ?? false
      );

      onSuccess();
    } catch (error) {
      const apiError = error as AxiosError<any>;

      // Handle account blocking (403 ACCOUNT_BLOCKED)
      if (
        apiError.response?.status === 403 &&
        apiError.response.data?.error?.code === 'ACCOUNT_BLOCKED'
      ) {
        const blockedUntilTimestamp = apiError.response.data?.error?.blocked_until;
        if (blockedUntilTimestamp) {
          setBlockedUntil(blockedUntilTimestamp);
          return;
        }
      }

      // Handle email not verified (403 EMAIL_NOT_VERIFIED)
      if (
        apiError.response?.status === 403 &&
        apiError.response.data?.error?.code === 'EMAIL_NOT_VERIFIED'
      ) {
        if (onEmailNotVerified) {
          onEmailNotVerified();
        } else {
          setGeneralError('Por favor verifica tu email antes de iniciar sesión.');
        }
        return;
      }

      // Handle rate limiting (429 RATE_LIMIT_EXCEEDED)
      if (apiError.response?.status === 429) {
        setShowTurnstile(true);
        const message = apiError.response.data?.error?.message || 'Demasiados intentos. Por favor completa la verificación.';
        setGeneralError(message);
        return;
      }

      // Handle invalid credentials (401 INVALID_CREDENTIALS)
      if (
        apiError.response?.status === 401 &&
        apiError.response.data?.error?.code === 'INVALID_CREDENTIALS'
      ) {
        const remainingAttempts = apiError.response.data?.error?.remaining_attempts;
        let message = 'Usuario o contraseña incorrectos.';

        if (remainingAttempts !== undefined && remainingAttempts > 0) {
          message += ` Tienes ${remainingAttempts} ${remainingAttempts === 1 ? 'intento' : 'intentos'} restantes.`;
        }

        setGeneralError(message);
        if (onError) onError(message);
        return;
      }

      // Generic error fallback
      const message = apiError.response?.data?.error?.message || 'Error al iniciar sesión. Inténtalo de nuevo.';
      setGeneralError(message);
      if (onError) onError(message);
    }
  };

  const handleUnblock = () => {
    setBlockedUntil(null);
    setGeneralError(null);
  };

  const handleTurnstileVerify = (token: string) => {
    setTurnstileToken(token);
    setGeneralError(null);
  };

  const handleTurnstileError = () => {
    setGeneralError('Error en la verificación de seguridad. Por favor inténtalo de nuevo.');
  };

  // Show account blocking message if blocked
  if (blockedUntil) {
    return (
      <AccountBlockedMessage
        blockedUntil={blockedUntil}
        onUnblock={handleUnblock}
      />
    );
  }

  return (
    <form className="login-form" onSubmit={handleSubmit(onSubmit)} noValidate>
      {/* General error display */}
      {generalError && (
        <div className="form-error" role="alert">
          {generalError}
        </div>
      )}

      {/* Login field (username or email) */}
      <div className="form-field">
        <label htmlFor="login">Usuario o Email</label>
        <input
          id="login"
          name="login"
          type="text"
          autoComplete="username"
          placeholder="usuario123 o tu@email.com"
          {...register('login')}
          aria-invalid={!!errors.login}
          aria-describedby={errors.login ? 'login-error' : undefined}
        />
        {errors.login && (
          <span id="login-error" className="field-error" role="alert">
            {errors.login.message}
          </span>
        )}
      </div>

      {/* Password field */}
      <div className="form-field">
        <label htmlFor="password">Contraseña</label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          {...register('password')}
          aria-invalid={!!errors.password}
          aria-describedby={errors.password ? 'password-error' : undefined}
        />
        {errors.password && (
          <span id="password-error" className="field-error" role="alert">
            {errors.password.message}
          </span>
        )}
      </div>

      {/* Remember Me checkbox */}
      <div className="form-field checkbox-field">
        <label>
          <input
            type="checkbox"
            {...register('rememberMe')}
          />
          <span>Recordarme (mantener sesión por 30 días)</span>
        </label>
      </div>

      {/* Forgot password link */}
      <div className="form-links">
        <a href="/forgot-password" className="forgot-password-link">
          ¿Olvidaste tu contraseña?
        </a>
      </div>

      {/* Turnstile CAPTCHA (shown if rate limited) */}
      {showTurnstile && (
        <div className="form-field">
          <TurnstileWidget
            onVerify={handleTurnstileVerify}
            onError={handleTurnstileError}
            action="login"
          />
        </div>
      )}

      {/* Submit button */}
      <button
        type="submit"
        className="submit-button"
        disabled={isSubmitting || (showTurnstile && !turnstileToken)}
      >
        {isSubmitting ? 'Iniciando sesión...' : 'Iniciar sesión'}
      </button>

      {/* Register link */}
      <div className="form-footer">
        <p>
          ¿No tienes una cuenta? <a href="/register">Regístrate aquí</a>
        </p>
      </div>
    </form>
  );
};
