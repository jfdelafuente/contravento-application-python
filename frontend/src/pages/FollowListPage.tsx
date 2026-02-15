// src/pages/FollowListPage.tsx

import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserMenu } from '../components/auth/UserMenu';
import { getFollowers, getFollowing, UserSummaryForFollow } from '../services/followService';
import './ProfilePage.css';
import './DashboardPage.css';

interface FollowListPageProps {
  type: 'followers' | 'following';
}

/**
 * Follow List Page - displays followers or following list for a user
 *
 * Routes:
 * - /users/:username/followers - Shows user's followers
 * - /users/:username/following - Shows users that user follows
 */
export const FollowListPage: React.FC<FollowListPageProps> = ({ type }) => {
  const { username } = useParams<{ username: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [users, setUsers] = useState<UserSummaryForFollow[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch followers or following
  useEffect(() => {
    const fetchUsers = async () => {
      if (!username) return;

      try {
        setIsLoading(true);
        setError(null);

        if (type === 'followers') {
          const response = await getFollowers(username);
          setUsers(response.followers || []);
          setTotalCount(response.total_count || 0);
        } else {
          const response = await getFollowing(username);
          setUsers(response.following || []);
          setTotalCount(response.total_count || 0);
        }
      } catch (err: any) {
        console.error(`Error fetching ${type}:`, err);
        setError(err.response?.data?.error?.message || `Error al cargar ${type === 'followers' ? 'seguidores' : 'siguiendo'}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, [username, type]);

  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="loading-spinner">Cargando...</div>
      </div>
    );
  }

  const title = type === 'followers' ? 'Seguidores' : 'Siguiendo';
  const emptyMessage = type === 'followers'
    ? 'No tiene seguidores aún'
    : 'No sigue a nadie aún';

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
        <div className="follow-list-container">
          {/* Back navigation and title */}
          <div className="follow-list-header">
            <button
              onClick={() => navigate(`/users/${username}`)}
              className="follow-list-back-button"
              aria-label="Volver al perfil"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h2 className="follow-list-title">{title}</h2>
              <p className="follow-list-subtitle">@{username}</p>
            </div>
          </div>

          {/* Error state */}
          {error && (
            <div className="follow-list-error">
              <p>{error}</p>
            </div>
          )}

          {/* Empty state */}
          {!error && users.length === 0 && (
            <div className="follow-list-empty">
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                style={{ opacity: 0.3, marginBottom: '1rem' }}
              >
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              <p>{emptyMessage}</p>
            </div>
          )}

          {/* User list */}
          {!error && users.length > 0 && (
            <div className="follow-list">
              <p className="follow-list-count">
                {totalCount} {type === 'followers' ? (totalCount === 1 ? 'seguidor' : 'seguidores') : 'siguiendo'}
              </p>
              <ul className="follow-list-items">
                {users.map((followUser) => (
                  <li key={followUser.user_id} className="follow-list-item">
                    <Link
                      to={`/users/${followUser.username}`}
                      className="follow-list-item-link"
                    >
                      {/* Avatar */}
                      {followUser.profile_photo_url ? (
                        <img
                          src={followUser.profile_photo_url}
                          alt={followUser.username}
                          className="follow-list-avatar"
                        />
                      ) : (
                        <div className="follow-list-avatar-placeholder">
                          {followUser.username.charAt(0).toUpperCase()}
                        </div>
                      )}

                      {/* Username */}
                      <span className="follow-list-username">
                        @{followUser.username}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
