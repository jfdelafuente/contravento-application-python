// src/pages/ProfilePage.tsx

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import HeaderQuickActions from '../components/dashboard/HeaderQuickActions';
import { getProfile } from '../services/profileService';
import { UserProfile } from '../types/profile';
import { CYCLING_TYPES } from '../types/profile';
import './ProfilePage.css';
import './DashboardPage.css'; // For dashboard-header__logo styles

/**
 * User profile page displaying user information
 *
 * Features:
 * - View profile information (bio, location, cycling type)
 * - Navigate to profile edit page
 * - Display profile photo
 * - Show verification status
 */
export const ProfilePage: React.FC = () => {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);

  // Fetch profile data when component mounts or when user photo changes
  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return;

      try {
        setIsLoadingProfile(true);
        const profileData = await getProfile(user.username);
        setProfile(profileData);
      } catch (error) {
        console.error('Error fetching profile:', error);
      } finally {
        setIsLoadingProfile(false);
      }
    };

    fetchProfile();
  }, [user, user?.photo_url]); // Re-fetch when photo_url changes

  if (authLoading || isLoadingProfile) {
    return (
      <div className="profile-page">
        <div className="loading-spinner">Cargando...</div>
      </div>
    );
  }

  if (!user) {
    return null; // ProtectedRoute will handle redirect
  }

  // Get cycling type label
  const cyclingTypeLabel = profile?.cycling_type
    ? CYCLING_TYPES.find((type) => type.value === profile.cycling_type)?.label || profile.cycling_type
    : null;

  // Get privacy settings labels (Feature 013)
  const getProfileVisibilityLabel = (visibility: 'public' | 'private') => {
    return visibility === 'public' ? 'Público' : 'Privado';
  };

  const getTripVisibilityLabel = (visibility: 'public' | 'followers' | 'private') => {
    switch (visibility) {
      case 'public':
        return 'Público';
      case 'followers':
        return 'Solo seguidores';
      case 'private':
        return 'Privado';
      default:
        return visibility;
    }
  };

  return (
    <div className="profile-page">
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

          <HeaderQuickActions />
          <UserMenu />
        </div>
      </header>

      <main className="profile-main">
        <div className="profile-content">
          <div className="profile-card">
            {/* Identity Band - Avatar + Button Left, Username + Bio Right */}
            <div className="profile-identity-band">
              {/* Left Column: Avatar + Button */}
              <div className="profile-identity-left">
                <div className="profile-avatar-large">
                  {profile?.photo_url ? (
                    <img src={profile.photo_url} alt={`${user.username} profile`} className="profile-photo" />
                  ) : (
                    <span className="profile-avatar-initial">{user.username.charAt(0).toUpperCase()}</span>
                  )}
                </div>
                <button
                  className="btn-edit-profile"
                  onClick={() => navigate('/profile/edit')}
                  type="button"
                  aria-label="Editar perfil"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    width="16"
                    height="16"
                    aria-hidden="true"
                  >
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                  </svg>
                  <span className="btn-edit-profile-text">Editar Perfil</span>
                </button>
              </div>

              {/* Right Column: Username + Bio */}
              <div className="profile-identity-right">
                <h2>@{user.username}</h2>
                {profile?.bio && (
                  <div className="profile-bio">
                    <p>{profile.bio}</p>
                  </div>
                )}
              </div>
            </div>

              <div className="profile-info">
                {/* Location */}
                {profile?.location && (
                  <div className="info-item">
                    <span className="info-label">Ubicación:</span>
                    <span className="info-value">{profile.location}</span>
                  </div>
                )}

                {/* Cycling Type */}
                {cyclingTypeLabel && (
                  <div className="info-item">
                    <span className="info-label">Tipo de ciclismo:</span>
                    <span className="info-value">{cyclingTypeLabel}</span>
                  </div>
                )}

                {/* Email */}
                <div className="info-item">
                  <span className="info-label">Email:</span>
                  <span className="info-value">{user.email}</span>
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

                {/* Member Since */}
                <div className="info-item">
                  <span className="info-label">Miembro desde:</span>
                  <span className="info-value">
                    {new Date(user.created_at).toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </span>
                </div>
              </div>

              {/* Privacy Settings Section (Feature 013) */}
              <div className="profile-privacy-section">
                <h3 className="privacy-section-title">Configuración de Privacidad</h3>
                <div className="profile-info">
                  {/* Profile Visibility */}
                  <div className="info-item">
                    <span className="info-label">Visibilidad del perfil:</span>
                    <span className="info-value privacy-badge" data-visibility={user.profile_visibility || 'public'}>
                      {getProfileVisibilityLabel(user.profile_visibility || 'public')}
                    </span>
                  </div>

                  {/* Trip Visibility */}
                  <div className="info-item">
                    <span className="info-label">Visibilidad de viajes:</span>
                    <span className="info-value privacy-badge" data-visibility={user.trip_visibility || 'public'}>
                      {getTripVisibilityLabel(user.trip_visibility || 'public')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="profile-placeholder">
                <h3>Próximamente</h3>
                <ul>
                  <li>Editar perfil de usuario</li>
                  <li>Subir foto de perfil</li>
                  <li>Preferencias de ciclismo</li>
                  <li>Estadísticas personales</li>
                  <li>Historial de viajes</li>
                </ul>
              </div>
            </div>
          </div>
      </main>
    </div>
  );
};
