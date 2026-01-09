// src/pages/LoginPage.tsx

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoginForm } from '../components/auth/LoginForm';
import './LoginPage.css';

interface LocationState {
  from?: {
    pathname: string;
  };
}

/**
 * Login page with form, error messaging, and post-login redirect
 *
 * Features:
 * - Renders LoginForm component
 * - Redirects to intended destination after successful login (or /dashboard default)
 * - Handles email verification enforcement (redirects to /verify-email if not verified)
 * - Displays success/error banners
 */
export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Get the page user was trying to access (if redirected from ProtectedRoute)
  const from = (location.state as LocationState)?.from?.pathname || '/welcome';

  const handleSuccess = () => {
    setSuccessMessage('Inicio de sesión exitoso! Redirigiendo...');
    setErrorMessage(null);

    // Redirect to intended destination after short delay
    setTimeout(() => {
      navigate(from, { replace: true });
    }, 1000);
  };

  const handleError = (message: string) => {
    setErrorMessage(message);
    setSuccessMessage(null);
  };

  const handleEmailNotVerified = () => {
    setErrorMessage('Por favor verifica tu email antes de continuar.');
    setSuccessMessage(null);

    // Redirect to email verification page after short delay
    setTimeout(() => {
      navigate('/verify-email', { replace: true });
    }, 2000);
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>ContraVento</h1>
          <h2>Iniciar Sesión</h2>
          <p>Accede a tu cuenta para continuar</p>
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
            <span>{successMessage}</span>
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

        {/* Login form */}
        <LoginForm
          onSuccess={handleSuccess}
          onError={handleError}
          onEmailNotVerified={handleEmailNotVerified}
        />
      </div>
    </div>
  );
};
