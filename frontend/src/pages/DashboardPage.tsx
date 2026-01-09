// src/pages/DashboardPage.tsx

import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import './DashboardPage.css';

/**
 * Protected dashboard page - only accessible to authenticated and verified users
 *
 * Features:
 * - Displays user information via UserMenu
 * - Shows logout button with loading state
 * - Placeholder for future dashboard content (trips, stats, etc.)
 */
export const DashboardPage: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="loading-spinner">Cargando...</div>
      </div>
    );
  }

  if (!user) {
    return null; // ProtectedRoute will handle redirect
  }

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>ContraVento</h1>
          <UserMenu />
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="welcome-card">
            <h2>Bienvenido a tu Dashboard</h2>
            <p>
              Has iniciado sesión correctamente como <strong>{user.email}</strong>
            </p>
            {user.is_verified && (
              <p className="verified-badge">
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
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Email verificado
              </p>
            )}
          </div>

          <div className="placeholder-content">
            <h3>Próximamente</h3>
            <ul>
              <li>Perfil de usuario editable</li>
              <li>Diario de viajes</li>
              <li>Estadísticas de ciclismo</li>
              <li>Galería de fotos</li>
              <li>Red social de ciclistas</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
};
