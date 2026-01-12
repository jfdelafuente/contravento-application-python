// src/pages/VerifyEmailPage.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../services/authService';
import type { ApiError } from '../types/api';
import './VerifyEmailPage.css';

/**
 * Email verification page with token validation and resend functionality
 *
 * Features:
 * - Extracts token from URL query parameter (?token=xxx)
 * - Automatically verifies email on mount if token present
 * - Handles token errors (expired, invalid)
 * - Resend verification email functionality
 * - Success animation and auto-redirect to login
 * - Rate limiting feedback for resend (max 1 per 5 minutes)
 */
export const VerifyEmailPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [tokenError, setTokenError] = useState<{
    code: string;
    message: string;
  } | null>(null);
  const [resentEmail, setResentEmail] = useState<string | null>(null);

  // Extract token from URL
  const token = searchParams.get('token');

  // Auto-verify on mount if token present
  useEffect(() => {
    if (token) {
      verifyEmail(token);
    }
  }, [token]);

  const verifyEmail = async (verificationToken: string) => {
    setIsVerifying(true);
    setErrorMessage(null);
    setTokenError(null);

    try {
      await authService.verifyEmail(verificationToken);

      setSuccessMessage(
        '¡Email verificado exitosamente! Tu cuenta está ahora activa. Serás redirigido al inicio de sesión en 3 segundos...'
      );

      // Redirect to login after delay
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (error) {
      const apiError = error as ApiError;

      // Handle token expired
      if (
        apiError.response?.status === 400 &&
        apiError.response.data?.error?.code === 'TOKEN_EXPIRED'
      ) {
        const message =
          apiError.response.data?.error?.message ||
          'El enlace de verificación ha expirado. Solicita un nuevo enlace.';
        setTokenError({ code: 'TOKEN_EXPIRED', message });
        return;
      }

      // Handle invalid token
      if (
        apiError.response?.status === 400 &&
        apiError.response.data?.error?.code === 'INVALID_TOKEN'
      ) {
        const message =
          apiError.response.data?.error?.message ||
          'El enlace de verificación es inválido.';
        setTokenError({ code: 'INVALID_TOKEN', message });
        return;
      }

      // Handle already verified
      if (
        apiError.response?.status === 400 &&
        apiError.response.data?.error?.code === 'ALREADY_VERIFIED'
      ) {
        setSuccessMessage(
          'Tu email ya ha sido verificado. Puedes iniciar sesión ahora.'
        );
        setTimeout(() => {
          navigate('/login');
        }, 3000);
        return;
      }

      // Generic error fallback
      const message =
        apiError.response?.data?.error?.message ||
        'Error al verificar email. Inténtalo de nuevo.';
      setErrorMessage(message);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResendVerification = async () => {
    setIsResending(true);
    setErrorMessage(null);
    setResentEmail(null);

    try {
      const emailSentTo = await authService.resendVerificationEmail();
      setResentEmail(emailSentTo);
      setTokenError(null);
    } catch (error) {
      const apiError = error as ApiError;

      // Handle rate limiting (max 1 per 5 minutes)
      if (apiError.response?.status === 429) {
        const message =
          apiError.response.data?.error?.message ||
          'Has solicitado demasiados correos de verificación. Por favor espera 5 minutos antes de intentar de nuevo.';
        setErrorMessage(message);
        return;
      }

      // Handle already verified
      if (
        apiError.response?.status === 400 &&
        apiError.response.data?.error?.code === 'ALREADY_VERIFIED'
      ) {
        setSuccessMessage(
          'Tu email ya ha sido verificado. Puedes iniciar sesión ahora.'
        );
        setTimeout(() => {
          navigate('/login');
        }, 3000);
        return;
      }

      // Generic error fallback
      const message =
        apiError.response?.data?.error?.message ||
        'Error al reenviar verificación. Inténtalo de nuevo.';
      setErrorMessage(message);
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="verify-email-page">
      <div className="verify-email-container">
        <div className="verify-email-header">
          <h1>ContraVento</h1>
          <h2>Verificación de Email</h2>
        </div>

        {/* Loading state while verifying */}
        {isVerifying && (
          <div className="loading-card">
            <div className="spinner"></div>
            <p>Verificando tu email...</p>
          </div>
        )}

        {/* Success message with animation */}
        {successMessage && !isVerifying && (
          <div className="success-card" role="alert">
            <div className="success-animation">
              <svg
                className="checkmark"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 52 52"
              >
                <circle
                  className="checkmark-circle"
                  cx="26"
                  cy="26"
                  r="25"
                  fill="none"
                />
                <path
                  className="checkmark-check"
                  fill="none"
                  d="M14.1 27.2l7.1 7.2 16.7-16.8"
                />
              </svg>
            </div>
            <h3>¡Verificación exitosa!</h3>
            <p>{successMessage}</p>
          </div>
        )}

        {/* Token error (expired or invalid) */}
        {tokenError && !isVerifying && !successMessage && (
          <div className="error-card token-error" role="alert">
            <svg
              className="icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h3>
              {tokenError.code === 'TOKEN_EXPIRED'
                ? 'Enlace expirado'
                : 'Enlace inválido'}
            </h3>
            <p>{tokenError.message}</p>

            {/* Resent email success */}
            {resentEmail && (
              <div className="resend-success">
                <p>
                  Se ha enviado un nuevo enlace de verificación a{' '}
                  <strong>{resentEmail}</strong>. Por favor revisa tu bandeja de
                  entrada.
                </p>
              </div>
            )}

            {/* Resend button */}
            {!resentEmail && (
              <button
                onClick={handleResendVerification}
                disabled={isResending}
                className="resend-button"
              >
                {isResending
                  ? 'Enviando...'
                  : 'Enviar nuevo enlace de verificación'}
              </button>
            )}
          </div>
        )}

        {/* General error */}
        {errorMessage && !isVerifying && !successMessage && !tokenError && (
          <div className="error-card" role="alert">
            <svg
              className="icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
            <h3>Error de verificación</h3>
            <p>{errorMessage}</p>
            <button onClick={handleResendVerification} className="resend-button">
              Enviar nuevo enlace de verificación
            </button>
          </div>
        )}

        {/* No token provided - show info card */}
        {!token && !isVerifying && (
          <div className="info-card">
            <svg
              className="icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            <h3>Verifica tu email</h3>
            <p>
              Hemos enviado un enlace de verificación a tu correo electrónico. Por
              favor revisa tu bandeja de entrada y haz clic en el enlace para
              activar tu cuenta.
            </p>
            <p className="help-text">
              ¿No recibiste el email? Revisa tu carpeta de spam o solicita un nuevo
              enlace.
            </p>
            <button
              onClick={handleResendVerification}
              disabled={isResending}
              className="resend-button"
            >
              {isResending ? 'Enviando...' : 'Reenviar email de verificación'}
            </button>
          </div>
        )}

        {/* Back to login link */}
        <div className="page-footer">
          <a href="/login">Volver a iniciar sesión</a>
        </div>
      </div>
    </div>
  );
};
