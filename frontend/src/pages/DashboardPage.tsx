// src/pages/DashboardPage.tsx
// Dashboard "Mapa de Ruta" - ContraVento
// Diseño: Dashboard como mapa topográfico personal del ciclista

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
 * Protected dashboard page - Mapa de Ruta design
 *
 * Design Intent: Dashboard como mapa topográfico de tu actividad ciclista.
 * Color Palette: Asfalto + Verde musgo + Ámbar (terroso, orgánico)
 * Layout: Asimétrico 70/30 - Columna principal con hero + actividad, sidebar con quick actions
 * Signature: Mini perfiles de elevación como indicadores de progreso
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
          <UserMenu />
        </div>
      </header>

      {/* Main Layout - Asimétrico 70/30 */}
      <div className="dashboard-layout">
        {/* Columna Principal - Hero + Contenido */}
        <main className="dashboard-main">
          {/* Hero Section - "Tu Ruta del Mes" */}
          <section className="dashboard-hero">
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

            {/* Placeholder para visualización de ruta del mes */}
            <div className="route-preview">
              <div className="route-preview__map">
                {/* Aquí iría un mapa de calor o polyline de rutas */}
                <svg
                  viewBox="0 0 400 120"
                  className="route-preview__elevation"
                  preserveAspectRatio="none"
                >
                  {/* Mini perfil de elevación decorativo */}
                  <path
                    d="M0,100 L50,90 L100,70 L150,85 L200,60 L250,75 L300,50 L350,65 L400,55"
                    stroke="var(--accent-amber)"
                    strokeWidth="3"
                    fill="none"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity="0.6"
                  />
                  <path
                    d="M0,100 L50,90 L100,70 L150,85 L200,60 L250,75 L300,50 L350,65 L400,55 L400,120 L0,120 Z"
                    fill="url(#elevationGradient)"
                    opacity="0.2"
                  />
                  <defs>
                    <linearGradient id="elevationGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="var(--accent-amber)" stopOpacity="0.6" />
                      <stop offset="100%" stopColor="var(--accent-amber)" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <div className="route-preview__stats">
                <div className="route-preview__stat">
                  <span className="route-preview__stat-label">Este mes</span>
                  <span className="route-preview__stat-value">12 rutas</span>
                </div>
                <div className="route-preview__stat">
                  <span className="route-preview__stat-label">Distancia</span>
                  <span className="route-preview__stat-value">324 km</span>
                </div>
                <div className="route-preview__stat">
                  <span className="route-preview__stat-label">Desnivel</span>
                  <span className="route-preview__stat-value">4.2k m</span>
                </div>
              </div>
            </div>
          </section>

          {/* Stats Section - Hitos del viaje */}
          <StatsSection />

          {/* Achievements Section */}
          <AchievementsSection />

          {/* Social Stats Section */}
          <SocialStatsSection />

          {/* Recent Trips Section */}
          <RecentTripsSection />

          {/* Próximamente */}
          <section className="dashboard-upcoming">
            <h3 className="dashboard-upcoming__title">En el camino</h3>
            <div className="dashboard-upcoming__grid">
              <div className="dashboard-upcoming__card">
                <svg
                  className="dashboard-upcoming__icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
                <h4 className="dashboard-upcoming__card-title">Feed Social</h4>
                <p className="dashboard-upcoming__card-desc">
                  Actividad de tu pelotón
                </p>
              </div>
              <div className="dashboard-upcoming__card">
                <svg
                  className="dashboard-upcoming__icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <h4 className="dashboard-upcoming__card-title">Galería Avanzada</h4>
                <p className="dashboard-upcoming__card-desc">
                  Tus fotos de ruta
                </p>
              </div>
              <div className="dashboard-upcoming__card">
                <svg
                  className="dashboard-upcoming__icon"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
                <h4 className="dashboard-upcoming__card-title">Comparación</h4>
                <p className="dashboard-upcoming__card-desc">
                  Analiza tu progreso
                </p>
              </div>
            </div>
          </section>
        </main>

        {/* Sidebar - Quick Actions (30%) */}
        <aside className="dashboard-sidebar">
          <QuickActionsSection />
        </aside>
      </div>
    </div>
  );
};
