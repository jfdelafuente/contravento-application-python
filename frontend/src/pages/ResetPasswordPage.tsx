// src/pages/ResetPasswordPage.tsx

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ResetPasswordForm } from '../components/auth/ResetPasswordForm';
import './ResetPasswordPage.css';

/**
 * Reset password page with token validation and form
 *
 * Features:
 * - Extracts token from URL query parameter (?token=xxx)
 * - Validates token presence
 * - Renders ResetPasswordForm component
 * - Handles token errors (expired, invalid)
 * - Shows success message and redirects to login
 */
export const ResetPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(true);

  // Extract token from URL
  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      setTokenError(
        'Enlace de recuperación inválido. Por favor solicita un nuevo enlace de recuperación.'
      );
      setShowForm(false);
    }
  }, [token]);

  const handleSuccess = () => {
    setSuccessMessage(
      'Tu contraseña ha sido restablecida exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña.'
    );
    setErrorMessage(null);
    setShowForm(false);

    // Redirect to login after delay
    setTimeout(() => {
      navigate('/login');
    }, 3000);
  };

  const handleTokenError = (_code: string, message: string) => {
    setTokenError(message);
    setErrorMessage(null);
    setShowForm(false);
  };

  const handleError = (message: string) => {
    setErrorMessage(message);
    setSuccessMessage(null);
  };

  const handleRequestNewLink = () => {
    navigate('/forgot-password');
  };

  return (
    <div className="reset-password-page">
      <div className="reset-password-container">
        <div className="reset-password-header">
          <h1>ContraVento</h1>
          <h2>Restablecer Contraseña</h2>
          <p>Ingresa tu nueva contraseña</p>
        </div>

        {/* Success banner */}
        {successMessage && (
          <div className="success-banner" role="alert">
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
                d="M5 13l4 4L19 7"
              />
            </svg>
            <div>
              <strong>Contraseña restablecida</strong>
              <p>{successMessage}</p>
              <p className="redirect-notice">
                Serás redirigido al inicio de sesión en 3 segundos...
              </p>
            </div>
          </div>
        )}

        {/* Token error banner */}
        {tokenError && (
          <div className="error-banner token-error" role="alert">
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
            <div>
              <strong>Enlace inválido o expirado</strong>
              <p>{tokenError}</p>
              <button onClick={handleRequestNewLink} className="request-link-button">
                Solicitar nuevo enlace
              </button>
            </div>
          </div>
        )}

        {/* General error banner */}
        {errorMessage && (
          <div className="error-banner" role="alert">
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
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Form (shown only if token is valid) */}
        {showForm && token && (
          <ResetPasswordForm
            token={token}
            onSuccess={handleSuccess}
            onTokenError={handleTokenError}
            onError={handleError}
          />
        )}
      </div>
    </div>
  );
};
