// src/components/routing/ProtectedRoute.tsx

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireVerified?: boolean; // Enforce email verification
}

/**
 * Protected route component that enforces authentication and email verification
 *
 * @param requireVerified - If true, redirects unverified users to /verify-email (default: true)
 *
 * @example
 * ```tsx
 * <Route
 *   path="/dashboard"
 *   element={
 *     <ProtectedRoute>
 *       <DashboardPage />
 *     </ProtectedRoute>
 *   }
 * />
 * ```
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireVerified = true,
}) => {
  const { user, isLoading, isAuthenticated } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">Cargando...</div>
      </div>
    );
  }

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Authenticated but email not verified (per clarification Q3: complete block)
  if (requireVerified && user && !user.is_verified) {
    return <Navigate to="/verify-email" replace />;
  }

  // Authenticated and verified (or verification not required) - render protected content
  return <>{children}</>;
};
