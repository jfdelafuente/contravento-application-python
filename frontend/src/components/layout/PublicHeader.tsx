/**
 * Public Header Component (Feature 013 - T035)
 *
 * Authentication-aware header for the public feed page.
 * Shows login button for anonymous users or user profile/logout for authenticated users.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { UserMenu } from '../auth/UserMenu';
import HeaderQuickActions from '../dashboard/HeaderQuickActions';
import './PublicHeader.css';

export const PublicHeader: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const handleLogin = () => {
    navigate('/login');
  };

  const handleLogoClick = () => {
    navigate('/');
  };


  return (
    <header className="dashboard-header dashboard-header--route-map">
      <div className="dashboard-header__content">
        {/* Logo with Dashboard Brand Style */}
        <div className="dashboard-header__brand" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
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

        {/* Quick Actions - Only for authenticated users */}
        {isAuthenticated && <HeaderQuickActions />}

        {/* Auth Section - Use UserMenu for authenticated, custom login button for anonymous */}
        {isAuthenticated ? (
          <UserMenu />
        ) : (
          <button
            className="public-header__login-button"
            onClick={handleLogin}
            aria-label="Iniciar sesión"
          >
            Iniciar sesión
          </button>
        )}
      </div>
    </header>
  );
};
