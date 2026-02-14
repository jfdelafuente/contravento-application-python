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
import { TermsOfServicePage } from './pages/TermsOfServicePage';
import { PrivacyPolicyPage } from './pages/PrivacyPolicyPage';
import { LandingPage } from './pages/LandingPage';

// Lazy load non-critical routes for better performance
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(module => ({ default: module.DashboardPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then(module => ({ default: module.ProfilePage })));
const ProfileEditPage = lazy(() => import('./pages/ProfileEditPage').then(module => ({ default: module.ProfileEditPage })));

// Travel Diary routes (Feature 008)
const TripsListPage = lazy(() => import('./pages/TripsListPage').then(module => ({ default: module.TripsListPage })));
const TripDetailPage = lazy(() => import('./pages/TripDetailPage').then(module => ({ default: module.TripDetailPage })));
const TripCreatePage = lazy(() => import('./pages/TripCreatePage').then(module => ({ default: module.TripCreatePage })));
const TripEditPage = lazy(() => import('./pages/TripEditPage').then(module => ({ default: module.TripEditPage })));

// GPS Trip Creation Wizard (Feature 017)
const TripCreateModePage = lazy(() => import('./pages/TripCreateModePage').then(module => ({ default: module.TripCreateModePage })));
const GPXTripCreatePage = lazy(() => import('./pages/GPXTripCreatePage').then(module => ({ default: module.GPXTripCreatePage })));
const GPXTripEditPage = lazy(() => import('./pages/GPXTripEditPage').then(module => ({ default: module.GPXTripEditPage })));

// Public Trips Feed (Feature 013)
const PublicFeedPage = lazy(() => import('./pages/PublicFeedPage').then(module => ({ default: module.PublicFeedPage })));

// Personalized Feed (Feature 004)
const FeedPage = lazy(() => import('./pages/FeedPage').then(module => ({ default: module.FeedPage })));

// User Profile (Feature 004 - Social Network)
const UserProfilePage = lazy(() => import('./pages/UserProfilePage').then(module => ({ default: module.UserProfilePage })));

// Follow List Page (Feature 019 - Dashboard Tooltips)
const FollowListPage = lazy(() => import('./pages/FollowListPage').then(module => ({ default: module.FollowListPage })));

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
              <Route path="/" element={<LandingPage />} />
              <Route path="/trips/public" element={<PublicFeedPage />} />
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

              {/* Personalized Feed (Feature 004) */}
              <Route
                path="/feed"
                element={
                  <ProtectedRoute>
                    <FeedPage />
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

              {/* GPS Trip Creation Wizard (Feature 017) */}
              <Route
                path="/trips/new"
                element={
                  <ProtectedRoute>
                    <TripCreateModePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/trips/new/manual"
                element={
                  <ProtectedRoute>
                    <TripCreatePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/trips/new/gpx"
                element={
                  <ProtectedRoute>
                    <GPXTripCreatePage />
                  </ProtectedRoute>
                }
              />

              {/* Public route - no authentication required for public trips */}
              <Route
                path="/trips/:tripId"
                element={<TripDetailPage />}
              />
              {/* Edit trip route */}
              <Route
                path="/trips/:tripId/edit"
                element={
                  <ProtectedRoute>
                    <TripEditPage />
                  </ProtectedRoute>
                }
              />
              {/* Edit GPX trip route */}
              <Route
                path="/trips/:tripId/edit-gpx"
                element={
                  <ProtectedRoute>
                    <GPXTripEditPage />
                  </ProtectedRoute>
                }
              />

              {/* Follow Lists (Feature 019 - Dashboard Tooltips) - MUST come before /users/:username */}
              <Route
                path="/users/:username/followers"
                element={<FollowListPage type="followers" />}
              />
              <Route
                path="/users/:username/following"
                element={<FollowListPage type="following" />}
              />

              {/* User Profile (Feature 004 - Social Network) */}
              <Route path="/users/:username" element={<UserProfilePage />} />

              {/* Legal pages */}
              <Route path="/terms-of-service" element={<TermsOfServicePage />} />
              <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />

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
