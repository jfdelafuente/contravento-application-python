// src/pages/RegisterPage.tsx

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RegisterForm } from '../components/auth/RegisterForm';
import './RegisterPage.css';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSuccess = (userData?: { is_verified?: boolean }) => {
    setErrorMessage(null);

    // Check if user was auto-verified (testing environment)
    if (userData?.is_verified) {
      setSuccessMessage(
        'Registro exitoso! Tu cuenta ha sido verificada automáticamente. Serás redirigido al inicio de sesión...'
      );

      // Redirect to login page after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } else {
      setSuccessMessage(
        'Registro exitoso! Revisa tu email para verificar tu cuenta antes de iniciar sesión.'
      );

      // Redirect to verify email page after 3 seconds
      setTimeout(() => {
        navigate('/verify-email');
      }, 3000);
    }
  };

  const handleError = (error: string) => {
    setSuccessMessage(null);
    setErrorMessage(error);

    // Clear error after 5 seconds
    setTimeout(() => {
      setErrorMessage(null);
    }, 5000);
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-header">
          <h1>Crear cuenta</h1>
          <p>Únete a la comunidad de ciclistas de ContraVento</p>
        </div>

        {/* Success message (T039) */}
        {successMessage && (
          <div className="success-banner" role="alert" aria-live="polite">
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

        {/* Error message (T039) */}
        {errorMessage && (
          <div className="error-banner" role="alert" aria-live="assertive">
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

        <RegisterForm onSuccess={handleSuccess} onError={handleError} />

        <div className="register-footer">
          <p>
            Al crear una cuenta, aceptas nuestros{' '}
            <a href="/terms" target="_blank" rel="noopener noreferrer">
              Términos de Servicio
            </a>{' '}
            y{' '}
            <a href="/privacy" target="_blank" rel="noopener noreferrer">
              Política de Privacidad
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};
