// src/pages/ProfilePage.tsx

import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import './ProfilePage.css';

/**
 * User profile page - placeholder for future implementation
 *
 * Features (future):
 * - View and edit profile information
 * - Upload profile photo
 * - Manage cycling preferences
 * - View statistics and achievements
 */
export const ProfilePage: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="loading-spinner">Cargando...</div>
      </div>
    );
  }

  if (!user) {
    return null; // ProtectedRoute will handle redirect
  }

  return (
    <div className="profile-page">
      <header className="profile-header">
        <div className="header-content">
          <h1>ContraVento</h1>
          <UserMenu />
        </div>
      </header>

      <main className="profile-main">
        <div className="profile-content">
          <div className="profile-card">
            <div className="profile-avatar-large">
              {user.username.charAt(0).toUpperCase()}
            </div>

            <h2>@{user.username}</h2>

            <div className="profile-info">
              <div className="info-item">
                <span className="info-label">Email:</span>
                <span className="info-value">{user.email}</span>
                {user.is_verified && (
                  <span className="verified-badge" title="Email verificado">
                    <svg
                      className="verified-icon"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </span>
                )}
              </div>

              <div className="info-item">
                <span className="info-label">Miembro desde:</span>
                <span className="info-value">
                  {new Date(user.created_at).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </span>
              </div>
            </div>

            <div className="profile-placeholder">
              <h3>Próximamente</h3>
              <ul>
                <li>Editar perfil de usuario</li>
                <li>Subir foto de perfil</li>
                <li>Preferencias de ciclismo</li>
                <li>Estadísticas personales</li>
                <li>Historial de viajes</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
