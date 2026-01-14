// src/components/auth/UserMenu.tsx

import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './UserMenu.css';

interface UserMenuProps {
  /** Optional CSS class for styling */
  className?: string;
  /** Show logout confirmation dialog (default: false for MVP) */
  showConfirmation?: boolean;
  /** Show navigation links (default: true) */
  showNavigation?: boolean;
}

/**
 * User menu component with user info and logout button
 *
 * Features:
 * - Displays username and verified badge
 * - Logout button with loading state
 * - Optional logout confirmation dialog
 * - Auto-redirect to login after logout
 * - Clears auth state and cached data
 */
export const UserMenu: React.FC<UserMenuProps> = ({
  className = '',
  showConfirmation = false,
  showNavigation = true,
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogoutClick = () => {
    if (showConfirmation) {
      setShowConfirmDialog(true);
    } else {
      performLogout();
    }
  };

  const performLogout = async () => {
    setIsLoggingOut(true);
    setError(null);

    try {
      // Call logout service (clears server-side session)
      await logout();

      // Clear any client-side cached data
      // The AuthContext already sets user to null
      // LocalStorage/SessionStorage can be cleared here if needed
      // For now, we rely on HttpOnly cookies being cleared by backend

      // Redirect to login page
      navigate('/login', { replace: true });
    } catch (err) {
      console.error('Logout error:', err);
      setError('Error al cerrar sesión. Inténtalo de nuevo.');
      setIsLoggingOut(false);
    }
  };

  const handleCancelLogout = () => {
    setShowConfirmDialog(false);
  };

  const handleConfirmLogout = () => {
    setShowConfirmDialog(false);
    performLogout();
  };

  if (!user) {
    return null;
  }

  return (
    <>
      <div className={`user-menu ${className}`}>
        {/* Navigation Links */}
        {showNavigation && (
          <nav className="user-navigation">
            <Link
              to="/"
              className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
            >
              <svg
                className="nav-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                />
              </svg>
              Inicio
            </Link>
            <Link
              to="/profile"
              className={`nav-link ${location.pathname === '/profile' ? 'active' : ''}`}
            >
              <svg
                className="nav-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              Perfil
            </Link>
          </nav>
        )}

        <div className="user-info">
          <div className="user-avatar">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div className="user-details">
            <span className="username">@{user.username}</span>
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
        </div>

        {error && (
          <div className="logout-error" role="alert">
            {error}
          </div>
        )}

        <button
          onClick={handleLogoutClick}
          disabled={isLoggingOut}
          className="logout-button"
        >
          {isLoggingOut ? (
            <>
              <span className="logout-spinner"></span>
              Cerrando sesión...
            </>
          ) : (
            <>
              <svg
                className="logout-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              Cerrar sesión
            </>
          )}
        </button>
      </div>

      {/* Confirmation Dialog (optional) */}
      {showConfirmDialog && (
        <div className="logout-confirm-overlay" onClick={handleCancelLogout}>
          <div
            className="logout-confirm-dialog"
            onClick={(e) => e.stopPropagation()}
          >
            <h3>¿Cerrar sesión?</h3>
            <p>¿Estás seguro de que quieres cerrar tu sesión?</p>
            <div className="dialog-actions">
              <button
                onClick={handleCancelLogout}
                className="cancel-button"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmLogout}
                className="confirm-button"
              >
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
