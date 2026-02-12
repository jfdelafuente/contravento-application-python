// src/pages/WelcomePage.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './WelcomePage.css';

export const WelcomePage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  const handleGoToDashboard = () => {
    navigate('/dashboard');
  };

  const handleGoToProfile = () => {
    navigate('/profile');
  };

  return (
    <div className="welcome-page">
      <div className="welcome-container">
        <div className="welcome-header">
          <h1>¡Bienvenido a ContraVento!</h1>
          <p className="welcome-subtitle">
            Hola <strong>{user?.username}</strong>, te has autenticado correctamente
          </p>
        </div>

        <div className="welcome-content">
          <div className="welcome-message">
            <h2>Estás listo para empezar</h2>
            <p>
              ContraVento es tu plataforma social para documentar viajes en bicicleta,
              compartir rutas y conectar con la comunidad ciclista.
            </p>
          </div>

          <div className="welcome-actions">
            <h3>¿Qué te gustaría hacer?</h3>
            <div className="action-buttons">
              <button
                className="action-button primary"
                onClick={handleGoToDashboard}
              >
                <svg
                  className="button-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                  />
                </svg>
                Ir al Dashboard
              </button>

              <button
                className="action-button secondary"
                onClick={handleGoToProfile}
              >
                <svg
                  className="button-icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
                Ver mi Perfil
              </button>
            </div>
          </div>

          <div className="welcome-info">
            <h3>Información de tu cuenta</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Usuario:</span>
                <span className="info-value">{user?.username}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Email:</span>
                <span className="info-value">{user?.email}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Estado:</span>
                <span className="info-value">
                  {user?.is_verified ? (
                    <span className="verified-badge">✓ Verificado</span>
                  ) : (
                    <span className="unverified-badge">⚠ No verificado</span>
                  )}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="welcome-footer">
          <button className="logout-button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  );
};
