/**
 * FeedPage Component (Feature 004 - T037)
 *
 * Main page for personalized feed.
 * Displays feed items with infinite scroll for authenticated users.
 */

import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInfiniteFeed } from '../hooks/useFeed';
import { FeedList } from '../components/feed/FeedList';
import { useAuth } from '../contexts/AuthContext';
import './FeedPage.css';

/**
 * FeedPage Component
 *
 * Personalized feed page for authenticated users.
 * Shows trips from followed users + popular community backfill.
 *
 * **Requires authentication** - Redirects to login if not authenticated.
 *
 * Features:
 * - Infinite scroll (automatically loads more items)
 * - Performance target: SC-001 (<1s initial load), SC-002 (<500ms pagination)
 * - Empty state for new users
 * - Error handling
 *
 * @example
 * // Route configuration in App.tsx:
 * <Route path="/feed" element={<FeedPage />} />
 */
export const FeedPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLoading: isAuthLoading } = useAuth();

  const {
    trips,
    isLoading,
    isLoadingMore,
    hasMore,
    error,
    loadMore,
  } = useInfiniteFeed(10);

  /**
   * Redirect to login if not authenticated
   */
  useEffect(() => {
    if (!isAuthLoading && !user) {
      navigate('/login?redirect=/feed');
    }
  }, [user, isAuthLoading, navigate]);

  /**
   * Show loading state while checking authentication
   */
  if (isAuthLoading) {
    return (
      <div className="feed-page">
        <div className="feed-page__loading">
          <div className="feed-page__spinner" />
          <p>Cargando...</p>
        </div>
      </div>
    );
  }

  /**
   * Don't render if not authenticated (will redirect)
   */
  if (!user) {
    return null;
  }

  return (
    <div className="feed-page">
      {/* Page Header */}
      <header className="feed-page__header">
        <div className="feed-page__header-content">
          <h1 className="feed-page__title">Tu Feed</h1>
          <p className="feed-page__subtitle">
            Descubre los últimos viajes de ciclistas que sigues y de la comunidad
          </p>
        </div>
      </header>

      {/* Feed Content */}
      <main className="feed-page__content">
        <FeedList
          trips={trips}
          isLoading={isLoading}
          isLoadingMore={isLoadingMore}
          hasMore={hasMore}
          error={error}
          onLoadMore={loadMore}
          emptyMessage="No hay viajes en tu feed. ¡Empieza a seguir a otros ciclistas para ver sus aventuras aquí!"
        />
      </main>
    </div>
  );
};
