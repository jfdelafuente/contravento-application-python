/**
 * Public Header Component (Feature 013 - T035)
 *
 * Authentication-aware header for the public feed page.
 * Shows login button for anonymous users or user profile/logout for authenticated users.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './PublicHeader.css';

export const PublicHeader: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogin = () => {
    navigate('/login');
  };

  const handleLogout = async () => {
    try {
      await logout();
      // Reload page to show anonymous state
      window.location.reload();
    } catch (error) {
      console.error('Logout error:', error);
      // Force reload anyway
      window.location.reload();
    }
  };

  const handleDashboardClick = () => {
    navigate('/dashboard');
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  // Get first letter of username for avatar fallback
  const getUserInitial = (): string => {
    if (!user?.username) return '?';
    return user.username.charAt(0).toUpperCase();
  };

  return (
    <header className="public-header">
      <div className="public-header__container">
        {/* Logo */}
        <div className="public-header__logo" onClick={handleLogoClick}>
          <svg
            className="public-header__logo-icon"
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
          <span className="public-header__logo-text">ContraVento</span>
        </div>

        {/* Auth Section */}
        <div className="public-header__auth">
          {!isAuthenticated ? (
            /* Anonymous User - Show Login Button */
            <button
              className="public-header__login-button"
              onClick={handleLogin}
              aria-label="Iniciar sesión"
            >
              Iniciar sesión
            </button>
          ) : (
            /* Authenticated User - Show Profile + Logout */
            <div className="public-header__user-section">
              {/* User Profile/Dashboard */}
              <button
                className="public-header__profile-button"
                onClick={handleDashboardClick}
                aria-label={`Ir al dashboard de ${user?.username}`}
              >
                {user?.photo_url ? (
                  <img
                    src={user.photo_url}
                    alt={user.username}
                    className="public-header__profile-photo"
                  />
                ) : (
                  <div
                    className="public-header__profile-avatar"
                    aria-label={`Avatar de ${user?.username}`}
                  >
                    {getUserInitial()}
                  </div>
                )}
                <span className="public-header__username">{user?.username}</span>
              </button>

              {/* Logout Button */}
              <button
                className="public-header__logout-button"
                onClick={handleLogout}
                aria-label="Cerrar sesión"
              >
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
