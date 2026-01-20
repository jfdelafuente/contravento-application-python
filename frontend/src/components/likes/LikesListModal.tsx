import React, { useEffect, useRef } from 'react';
import { useTripLikes } from '../../hooks/useTripLikes';
import './LikesListModal.css';

// Inline SVG icons (to avoid adding lucide-react dependency)
const HeartIcon = ({ size = 20, fill = 'currentColor', className }: { size?: number; fill?: string; className?: string }) => (
  <svg
    className={className}
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill={fill}
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
  </svg>
);

const XIcon = ({ size = 24 }: { size?: number }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

const UserIcon = ({ size = 20 }: { size?: number }) => (
  <svg
    width={size}
    height={size}
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
);

interface LikesListModalProps {
  tripId: string;
  tripTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

/**
 * LikesListModal - Modal que muestra la lista de usuarios que dieron like a un viaje (T057, TC-US2-008).
 *
 * Features:
 * - Lista paginada de usuarios con avatar y username
 * - Infinite scroll para cargar más resultados
 * - Loading states con skeleton loaders
 * - Error handling con mensajes en español
 * - Diseño rústico consistente con la app
 * - Accessibility: ARIA labels, keyboard navigation (ESC to close)
 *
 * @param tripId - ID del viaje
 * @param tripTitle - Título del viaje (para mostrar en header)
 * @param isOpen - Si el modal está abierto
 * @param onClose - Callback para cerrar el modal
 */
export const LikesListModal: React.FC<LikesListModalProps> = ({
  tripId,
  tripTitle,
  isOpen,
  onClose,
}) => {
  const { likes, totalCount, isLoading, error, hasMore, loadMore } =
    useTripLikes({
      tripId,
      enabled: isOpen,
    });

  const listRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  // Keyboard navigation (ESC to close)
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Infinite scroll with Intersection Observer
  useEffect(() => {
    if (!isOpen || !hasMore || isLoading) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      },
      { threshold: 0.5 }
    );

    if (sentinelRef.current) {
      observerRef.current.observe(sentinelRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [isOpen, hasMore, isLoading, loadMore]);

  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  // Get profile photo URL or default placeholder
  const getPhotoUrl = (photoUrl: string | null): string => {
    if (!photoUrl) return '/images/placeholders/user-avatar.png';
    if (photoUrl.startsWith('http://') || photoUrl.startsWith('https://')) {
      return photoUrl;
    }
    return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${photoUrl}`;
  };

  // Format timestamp to relative time (e.g., "hace 2 horas")
  const formatRelativeTime = (isoString: string): string => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMinutes < 1) return 'Hace unos segundos';
    if (diffMinutes < 60) return `Hace ${diffMinutes} ${diffMinutes === 1 ? 'minuto' : 'minutos'}`;
    if (diffHours < 24) return `Hace ${diffHours} ${diffHours === 1 ? 'hora' : 'horas'}`;
    if (diffDays < 7) return `Hace ${diffDays} ${diffDays === 1 ? 'día' : 'días'}`;

    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  return (
    <div
      className="likes-list-modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="likes-modal-title"
    >
      <div
        className="likes-list-modal"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="likes-list-modal-header">
          <div className="likes-list-modal-title-container">
            <HeartIcon className="likes-list-modal-icon" size={20} fill="currentColor" />
            <div>
              <h2 id="likes-modal-title" className="likes-list-modal-title">
                Me gusta
              </h2>
              <p className="likes-list-modal-subtitle">{tripTitle}</p>
            </div>
          </div>
          <button
            className="likes-list-modal-close"
            onClick={onClose}
            aria-label="Cerrar modal de likes"
          >
            <XIcon size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="likes-list-modal-content" ref={listRef}>
          {/* Loading state (initial) */}
          {isLoading && likes.length === 0 && (
            <div className="likes-list-loading" role="status" aria-live="polite">
              <div className="spinner" aria-hidden="true"></div>
              <p>Cargando likes...</p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="likes-list-error" role="alert">
              <p>{error}</p>
              <button
                className="likes-list-retry-button"
                onClick={() => window.location.reload()}
              >
                Reintentar
              </button>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !error && likes.length === 0 && (
            <div className="likes-list-empty">
              <HeartIcon className="likes-list-empty-icon" size={48} />
              <p>Aún no hay likes en este viaje</p>
              <span className="likes-list-empty-hint">Sé el primero en darle me gusta</span>
            </div>
          )}

          {/* Likes list */}
          {likes.length > 0 && (
            <>
              <div className="likes-list-count">
                {totalCount} {totalCount === 1 ? 'persona' : 'personas'} {totalCount === 1 ? 'dio' : 'dieron'} like
              </div>

              <ul className="likes-list" role="list">
                {likes.map((like, index) => (
                  <li key={`${like.user.username}-${index}`} className="likes-list-item">
                    <a
                      href={`/users/${like.user.username}`}
                      className="likes-list-item-link"
                      onClick={() => {
                        // Allow default navigation behavior
                        onClose(); // Close modal when clicking user
                      }}
                    >
                      <div className="likes-list-item-avatar">
                        {like.user.profile_photo_url ? (
                          <img
                            src={getPhotoUrl(like.user.profile_photo_url)}
                            alt={`Avatar de ${like.user.username}`}
                            onError={(e) => {
                              // Fallback to default avatar on error
                              e.currentTarget.src = '/images/placeholders/user-avatar.png';
                            }}
                          />
                        ) : (
                          <div className="likes-list-item-avatar-placeholder">
                            <UserIcon size={20} />
                          </div>
                        )}
                      </div>
                      <div className="likes-list-item-info">
                        <span className="likes-list-item-username">
                          {like.user.username}
                        </span>
                        <span className="likes-list-item-time">
                          {formatRelativeTime(like.created_at)}
                        </span>
                      </div>
                    </a>
                  </li>
                ))}
              </ul>

              {/* Infinite scroll sentinel */}
              {hasMore && (
                <div ref={sentinelRef} className="likes-list-sentinel">
                  <div className="spinner" aria-hidden="true"></div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};
