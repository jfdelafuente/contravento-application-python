// src/pages/ProfilePage.tsx

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import { getProfile } from '../services/profileService';
import { UserProfile } from '../types/profile';
import { CYCLING_TYPES } from '../types/profile';
import './ProfilePage.css';

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
      <header className="profile-header">
        <div className="header-content">
          <h1>ContraVento</h1>
          <UserMenu />
        </div>
      </header>

      <main className="profile-main">
        <div className="profile-content">
          <div className="profile-card">
            {/* Left Column - Avatar and Edit Button */}
            <div className="profile-left">
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
              >
                Editar Perfil
              </button>
            </div>

            {/* Right Column - Profile Info */}
            <div className="profile-right">
              <div className="profile-header-section">
                <h2>@{user.username}</h2>
              </div>

              {/* Profile Bio */}
              {profile?.bio && (
                <div className="profile-bio">
                  <p>{profile.bio}</p>
                </div>
              )}

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
                    <span className="info-value privacy-badge" data-visibility={user.profile_visibility}>
                      {getProfileVisibilityLabel(user.profile_visibility)}
                    </span>
                  </div>

                  {/* Trip Visibility */}
                  <div className="info-item">
                    <span className="info-label">Visibilidad de viajes:</span>
                    <span className="info-value privacy-badge" data-visibility={user.trip_visibility}>
                      {getTripVisibilityLabel(user.trip_visibility)}
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
        </div>
      </main>
    </div>
  );
};
