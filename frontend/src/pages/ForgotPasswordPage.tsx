// src/pages/ForgotPasswordPage.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ForgotPasswordForm } from '../components/auth/ForgotPasswordForm';
import './ForgotPasswordPage.css';

/**
 * Forgot password page with form and success messaging
 *
 * Features:
 * - Renders ForgotPasswordForm component
 * - Shows success message when reset email is sent
 * - Displays error messages for failures
 * - Auto-redirects to login after successful request
 */
export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(true);

  const handleSuccess = (email: string) => {
    setSuccessMessage(
      `Se ha enviado un enlace de recuperación a ${email}. Por favor revisa tu bandeja de entrada y sigue las instrucciones.`
    );
    setErrorMessage(null);
    setShowForm(false);

    // Redirect to login after delay
    setTimeout(() => {
      navigate('/login');
    }, 5000);
  };

  const handleError = (message: string) => {
    setErrorMessage(message);
    setSuccessMessage(null);
  };

  return (
    <div className="forgot-password-page">
      <div className="forgot-password-container">
        <div className="forgot-password-header">
          <h1>ContraVento</h1>
          <h2>Recuperar Contraseña</h2>
          <p>Solicita un enlace para restablecer tu contraseña</p>
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
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            <div>
              <strong>Email enviado</strong>
              <p>{successMessage}</p>
              <p className="redirect-notice">Serás redirigido al inicio de sesión en 5 segundos...</p>
            </div>
          </div>
        )}

        {/* Error banner */}
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

        {/* Form (hidden after success) */}
        {showForm && (
          <ForgotPasswordForm onSuccess={handleSuccess} onError={handleError} />
        )}
      </div>
    </div>
  );
};
