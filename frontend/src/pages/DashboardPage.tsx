// src/pages/DashboardPage.tsx
// Dashboard "Mapa de Ruta" - ContraVento
// Diseño: Dashboard como mapa topográfico personal del ciclista

import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import HeaderQuickActions from '../components/dashboard/HeaderQuickActions';
import StatsSection from '../components/dashboard/StatsSection';
import RecentTripsSection from '../components/dashboard/RecentTripsSection';
import AchievementsSection from '../components/dashboard/AchievementsSection';
import SocialStatsSection from '../components/dashboard/SocialStatsSection';
import SocialFeedSection from '../components/dashboard/SocialFeedSection';
import './DashboardPage.css';

/**
 * Protected dashboard page - Mapa de Ruta design
 *
 * Design Intent: Dashboard como mapa topográfico de tu actividad ciclista.
 * Color Palette: Asfalto + Verde musgo + Ámbar (terroso, orgánico)
 * Layout: "Valle Compartido" - Dos columnas balanceadas (45/45) con hero compacto arriba
 * Signature: Feed con elevation bands (bandas topográficas) y leading edge coloreado
 */
export const DashboardPage: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="loading-spinner">Cargando tu ruta...</div>
      </div>
    );
  }

  if (!user) {
    return null; // ProtectedRoute will handle redirect
  }

  return (
    <div className="dashboard-page dashboard-page--route-map">
      {/* Navigation Header - Integrado como parte del mapa */}
      <header className="dashboard-header dashboard-header--route-map">
        <div className="dashboard-header__content">
          <div className="dashboard-header__brand">
            {/* Logo con estética de señalización de ruta */}
            <svg
              className="dashboard-header__logo-icon"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M12 2L2 7V17L12 22L22 17V7L12 2Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                fill="none"
              />
              <path
                d="M12 22V12"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
              <path
                d="M2 7L12 12L22 7"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
            <div className="dashboard-header__brand-text">
              <span className="dashboard-header__brand-name">ContraVento</span>
              <span className="dashboard-header__brand-tagline">Tu mapa de rutas</span>
            </div>
          </div>

          {/* Quick Actions - Brújula de Cabecera */}
          <HeaderQuickActions />

          <UserMenu />
        </div>
      </header>

      {/* Hero Section - Compact, full-width */}
      <section className="dashboard-hero dashboard-hero--compact">
        <div className="dashboard-hero__header">
          <div>
            <h1 className="dashboard-hero__greeting">
              Hola, {user.username}
            </h1>
            <p className="dashboard-hero__subtitle">
              Bienvenido a tu bitácora de rutas
            </p>
          </div>
          {user.is_verified && (
            <div className="dashboard-hero__badge">
              <svg
                className="dashboard-hero__badge-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
              <span className="dashboard-hero__badge-text">Verificado</span>
            </div>
          )}
        </div>
      </section>

      {/* Main Layout - "Valle Compartido" - Two balanced columns */}
      <div className="dashboard-layout dashboard-layout--two-column">
        {/* Left Column - Personal Journey (35%) */}
        <section className="dashboard-main">
          <div className="dashboard-personal-stats">
            {/* Social Stats Section */}
            <SocialStatsSection />

            {/* Stats Section */}
            <StatsSection />

            {/* Achievements Section */}
            <AchievementsSection />

            {/* Recent Trips Section */}
            <RecentTripsSection />
          </div>
        </section>

        {/* Right Column - Pelotón Feed (55%) */}
        <aside className="dashboard-feed">
          <SocialFeedSection />
        </aside>
      </div>
    </div>
  );
};
