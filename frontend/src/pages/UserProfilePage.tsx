// src/pages/UserProfilePage.tsx

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import { FollowButton } from '../components/social/FollowButton';
import { getProfile } from '../services/profileService';
import { UserProfile } from '../types/profile';
import { CYCLING_TYPES } from '../types/profile';
import './ProfilePage.css';
import './DashboardPage.css';

/**
 * Public user profile page - displays any user's public profile
 *
 * Features:
 * - View public profile information
 * - Follow/unfollow button for other users
 * - Navigate to user's trips
 * - If viewing own profile, redirect to /profile
 */
export const UserProfilePage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // If viewing own profile, redirect to /profile
  useEffect(() => {
    if (user && username === user.username) {
      navigate('/profile', { replace: true });
    }
  }, [user, username, navigate]);

  // Fetch profile data
  useEffect(() => {
    const fetchProfile = async () => {
      if (!username) return;

      try {
        setIsLoading(true);
        setError(null);
        const profileData = await getProfile(username);
        setProfile(profileData);
      } catch (err: any) {
        console.error('Error fetching profile:', err);
        setError(err.response?.data?.error?.message || 'Error al cargar el perfil');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, [username]);

  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="loading-spinner">Cargando perfil...</div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="profile-page">
        <header className="profile-header">
          <div className="header-content">
            <h1 className="dashboard-header__logo">
              <Link to="/">
                <svg
                  className="dashboard-header__logo-icon"
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
                <span>ContraVento</span>
              </Link>
            </h1>
            {user && <UserMenu />}
          </div>
        </header>

        <div className="profile-content">
          <div className="profile-error">
            <h2>
              {error?.includes('privado') ? 'Perfil privado' : 'Usuario no encontrado'}
            </h2>
            <p>
              {error || 'El perfil que buscas no existe o no está disponible'}
            </p>
            <Link to="/" className="btn btn-primary">Volver al inicio</Link>
          </div>
        </div>
      </div>
    );
  }

  // Get cycling type label
  const cyclingTypeLabel = profile.cycling_type
    ? CYCLING_TYPES.find((type) => type.value === profile.cycling_type)?.label || profile.cycling_type
    : null;

  const isOwnProfile = user && user.username === username;

  return (
    <div className="profile-page">
      <header className="profile-header">
        <div className="header-content">
          <h1 className="dashboard-header__logo">
            <Link to="/">
              <svg
                className="dashboard-header__logo-icon"
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
              <span>ContraVento</span>
            </Link>
          </h1>
          {user && <UserMenu />}
        </div>
      </header>

      <div className="profile-content">
        <div className="profile-info">
          {/* Profile Photo */}
          <div className="profile-photo-container">
            {profile.photo_url ? (
              <img
                src={profile.photo_url}
                alt={`Foto de perfil de ${profile.username}`}
                className="profile-photo"
              />
            ) : (
              <div className="profile-photo-placeholder">
                <svg
                  width="80"
                  height="80"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
            )}
          </div>

          {/* User Info */}
          <div className="profile-details">
            <div className="profile-header-info">
              <div>
                <h2 className="profile-username">@{profile.username}</h2>
                {profile.full_name && (
                  <p className="profile-fullname">{profile.full_name}</p>
                )}
              </div>

              {/* Follow Button - only show if not own profile and user is logged in */}
              {!isOwnProfile && user && (
                <FollowButton
                  username={profile.username}
                  initialFollowing={profile.is_following || false}
                  size="medium"
                  variant="primary"
                />
              )}
            </div>

            {/* Bio */}
            {profile.bio && (
              <div className="profile-field">
                <label className="profile-label">Biografía</label>
                <p className="profile-value profile-bio">{profile.bio}</p>
              </div>
            )}

            {/* Location */}
            {profile.location && (
              <div className="profile-field">
                <label className="profile-label">Ubicación</label>
                <p className="profile-value">
                  <svg
                    className="profile-icon"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                    <circle cx="12" cy="10" r="3" />
                  </svg>
                  {profile.location}
                </p>
              </div>
            )}

            {/* Cycling Type */}
            {cyclingTypeLabel && (
              <div className="profile-field">
                <label className="profile-label">Tipo de ciclismo</label>
                <p className="profile-value">
                  <svg
                    className="profile-icon"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="5.5" cy="17.5" r="3.5" />
                    <circle cx="18.5" cy="17.5" r="3.5" />
                    <path d="M15 6a1 1 0 1 0 0-2 1 1 0 0 0 0 2z" />
                    <path d="M12 17.5V14l-3-3 4-3 2 3h2" />
                  </svg>
                  {cyclingTypeLabel}
                </p>
              </div>
            )}

            {/* Link to user's trips */}
            <div className="profile-actions">
              <Link to={`/trips?user=${profile.username}`} className="btn btn-secondary">
                Ver viajes de {profile.username}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
