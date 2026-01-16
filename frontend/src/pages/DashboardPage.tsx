// src/pages/DashboardPage.tsx

import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import StatsSection from '../components/dashboard/StatsSection';
import RecentTripsSection from '../components/dashboard/RecentTripsSection';
import QuickActionsSection from '../components/dashboard/QuickActionsSection';
import AchievementsSection from '../components/dashboard/AchievementsSection';
import SocialStatsSection from '../components/dashboard/SocialStatsSection';
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
          <h1 className="dashboard-header__logo">
            <svg
              className="dashboard-header__logo-icon"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM12 6C9.79 6 8 7.79 8 10H10C10 8.9 10.9 8 12 8C13.1 8 14 8.9 14 10C14 12 11 11.75 11 15H13C13 12.75 16 12.5 16 10C16 7.79 14.21 6 12 6Z"
                fill="currentColor"
              />
            </svg>
            <span>ContraVento</span>
          </h1>
          <UserMenu />
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="welcome-card">
            <div className="welcome-card__content">
              <h2>Bienvenido a tu Dashboard</h2>
              <p>
                Has iniciado sesión correctamente como <strong>{user.email}</strong>
              </p>
            </div>
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

          {/* Stats Section - FR-001 */}
          <StatsSection />

          {/* Achievements Section - FR-003 */}
          <AchievementsSection />

          {/* Social Stats Section - FR-003 */}
          <SocialStatsSection />

          {/* Recent Trips Section - FR-002 */}
          <RecentTripsSection />

          {/* Quick Actions Section - FR-004 */}
          <QuickActionsSection />

          <div className="placeholder-content">
            <h3>Próximamente</h3>
            <ul>
              <li>Feed de actividad social</li>
              <li>Galería de fotos avanzada</li>
              <li>Comparación de estadísticas</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
};
