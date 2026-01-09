import React, { useState } from 'react';
import { TripSummary } from '../../types/trip';
import { formatShortDate, formatDistance } from '../../utils/formatters';
import './RecentTripCard.css';

export interface RecentTripCardProps {
  trip: TripSummary;
}

/**
 * RecentTripCard component - Display trip summary with photo and details
 * Features lazy loading for images and fallback placeholder
 */
const RecentTripCard: React.FC<RecentTripCardProps> = ({ trip }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  const handleImageError = () => {
    setImageError(true);
    setImageLoaded(true);
  };

  return (
    <article className="recent-trip-card">
      <a href={`/trips/${trip.id}`} className="recent-trip-card__link">
        {/* Photo */}
        <div className="recent-trip-card__photo">
          {!imageLoaded && !imageError && (
            <div className="recent-trip-card__photo-skeleton" aria-busy="true">
              Cargando...
            </div>
          )}
          {trip.photo_url && !imageError ? (
            <img
              src={trip.photo_url}
              alt={trip.title}
              className={`recent-trip-card__image ${imageLoaded ? 'recent-trip-card__image--loaded' : ''}`}
              loading="lazy"
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          ) : (
            <div className="recent-trip-card__photo-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <span>Sin foto</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="recent-trip-card__content">
          <h3 className="recent-trip-card__title">{trip.title}</h3>

          <div className="recent-trip-card__meta">
            <span className="recent-trip-card__date">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
              {formatShortDate(trip.start_date)}
            </span>

            <span className="recent-trip-card__distance">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
              {formatDistance(trip.distance_km)}
            </span>
          </div>

          {/* Tags */}
          {trip.tags && trip.tags.length > 0 && (
            <div className="recent-trip-card__tags">
              {trip.tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="recent-trip-card__tag">
                  {tag}
                </span>
              ))}
              {trip.tags.length > 3 && (
                <span className="recent-trip-card__tag recent-trip-card__tag--more">
                  +{trip.tags.length - 3}
                </span>
              )}
            </div>
          )}
        </div>
      </a>
    </article>
  );
};

export default RecentTripCard;
