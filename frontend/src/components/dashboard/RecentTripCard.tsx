import React from 'react';
import { TripSummary } from '../../types/trip';
import { formatShortDate } from '../../utils/formatters';
import { formatDistance, getPhotoUrl } from '../../utils/tripHelpers';
import './RecentTripCard.css';

export interface RecentTripCardProps {
  trip: TripSummary;
}

/**
 * RecentTripCard component - Display trip summary with photo and details
 * Shows thumbnail if available, otherwise shows photo count placeholder
 */
const RecentTripCard: React.FC<RecentTripCardProps> = ({ trip }) => {
  return (
    <article className="recent-trip-card">
      <a href={`/trips/${trip.trip_id}`} className="recent-trip-card__link">
        {/* Photo */}
        <div className="recent-trip-card__photo">
          {trip.thumbnail_url ? (
            <img
              src={getPhotoUrl(trip.thumbnail_url)}
              alt={trip.title}
              className="recent-trip-card__image recent-trip-card__image--loaded"
              loading="lazy"
            />
          ) : (
            <div className="recent-trip-card__photo-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <span>{trip.photo_count > 0 ? `${trip.photo_count} foto${trip.photo_count > 1 ? 's' : ''}` : 'Sin foto'}</span>
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
          {trip.tag_names && trip.tag_names.length > 0 && (
            <div className="recent-trip-card__tags">
              {trip.tag_names.slice(0, 3).map((tag: string, index: number) => (
                <span key={index} className="recent-trip-card__tag">
                  {tag}
                </span>
              ))}
              {trip.tag_names.length > 3 && (
                <span className="recent-trip-card__tag recent-trip-card__tag--more">
                  +{trip.tag_names.length - 3}
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
