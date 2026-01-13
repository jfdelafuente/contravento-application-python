import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/routing/ProtectedRoute';
import { ErrorBoundary } from './components/ErrorBoundary';
import { RegisterPage } from './pages/RegisterPage';
import { LoginPage } from './pages/LoginPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { WelcomePage } from './pages/WelcomePage';

// Lazy load non-critical routes for better performance
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(module => ({ default: module.DashboardPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then(module => ({ default: module.ProfilePage })));
const ProfileEditPage = lazy(() => import('./pages/ProfileEditPage').then(module => ({ default: module.ProfileEditPage })));

// Travel Diary routes (Feature 008)
const TripsListPage = lazy(() => import('./pages/TripsListPage').then(module => ({ default: module.TripsListPage })));
const TripDetailPage = lazy(() => import('./pages/TripDetailPage').then(module => ({ default: module.TripDetailPage })));
const TripCreatePage = lazy(() => import('./pages/TripCreatePage').then(module => ({ default: module.TripCreatePage })));
const TripEditPage = lazy(() => import('./pages/TripEditPage').then(module => ({ default: module.TripEditPage })));

// Public Trips Feed (Feature 013)
const PublicFeedPage = lazy(() => import('./pages/PublicFeedPage').then(module => ({ default: module.PublicFeedPage })));

// Loading fallback component for lazy-loaded routes
const LoadingFallback: React.FC = () => (
  <div className="loading-container">
    <div className="loading-spinner">Cargando...</div>
  </div>
);

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AuthProvider>
          <Toaster />
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<PublicFeedPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />

              {/* Protected routes */}
              <Route
                path="/welcome"
                element={
                  <ProtectedRoute>
                    <WelcomePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile/edit"
                element={
                  <ProtectedRoute>
                    <ProfileEditPage />
                  </ProtectedRoute>
                }
              />

              {/* Travel Diary routes (Feature 008) */}
              <Route
                path="/trips"
                element={
                  <ProtectedRoute>
                    <TripsListPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/trips/new"
                element={
                  <ProtectedRoute>
                    <TripCreatePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/trips/:tripId"
                element={
                  <ProtectedRoute>
                    <TripDetailPage />
                  </ProtectedRoute>
                }
              />
              {/* Phase 7: Edit trip route */}
              <Route
                path="/trips/:tripId/edit"
                element={
                  <ProtectedRoute>
                    <TripEditPage />
                  </ProtectedRoute>
                }
              />

              {/* Catch-all redirect */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
