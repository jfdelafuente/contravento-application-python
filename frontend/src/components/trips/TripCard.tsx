/**
 * TripCard Component
 *
 * Card component for displaying trip summary in grid/list views.
 * Shows thumbnail, title, dates, distance, difficulty badge, and tags.
 *
 * Used in:
 * - TripsListPage (grid of user's trips)
 * - ProfilePage (recent trips section)
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { TripListItem } from '../../types/trip';
import {
  formatDate,
  formatDistance,
  getStatusLabel,
  getStatusClass,
  getPhotoUrl,
} from '../../utils/tripHelpers';
import './TripCard.css';

interface TripCardProps {
  trip: TripListItem;
  showStatus?: boolean; // Show draft/published badge (default: false for public views)
}

export const TripCard: React.FC<TripCardProps> = ({ trip, showStatus = false }) => {
  const {
    trip_id,
    title,
    start_date,
    distance_km,
    status,
    is_private,
    photo_count,
    tag_names,
    thumbnail_url,
  } = trip;

  return (
    <Link to={`/trips/${trip_id}`} className="trip-card">
      {/* Thumbnail */}
      <div className="trip-card__thumbnail">
        {thumbnail_url ? (
          <img
            src={getPhotoUrl(thumbnail_url) || ''}
            alt={title}
            className="trip-card__image"
            loading="lazy"
          />
        ) : (
          <div className="trip-card__placeholder">
            <svg
              className="trip-card__placeholder-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}

        {/* Photo count badge */}
        {photo_count > 0 && (
          <div className="trip-card__photo-count">
            <svg
              className="trip-card__photo-count-icon"
              fill="currentColor"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
                clipRule="evenodd"
              />
            </svg>
            <span className="trip-card__photo-count-text">{photo_count}</span>
          </div>
        )}

        {/* Privacy badge - shown if trip is private (highest priority) */}
        {showStatus && is_private && (
          <div className="trip-card__privacy">
            <svg
              className="trip-card__privacy-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
            <span>Privado</span>
          </div>
        )}

        {/* Status badge (draft/published) - only shown if showStatus=true and not private */}
        {showStatus && !is_private && (
          <div className={`trip-card__status ${getStatusClass(status)}`}>
            {getStatusLabel(status)}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="trip-card__content">
        {/* Title */}
        <h3 className="trip-card__title">{title}</h3>

        {/* Metadata */}
        <div className="trip-card__meta">
          {/* Date */}
          <div className="trip-card__meta-item">
            <svg
              className="trip-card__meta-icon"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span className="trip-card__meta-text">{formatDate(start_date)}</span>
          </div>

          {/* Distance */}
          {distance_km !== null && (
            <div className="trip-card__meta-item">
              <svg
                className="trip-card__meta-icon"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                />
              </svg>
              <span className="trip-card__meta-text">{formatDistance(distance_km)}</span>
            </div>
          )}
        </div>

        {/* Tags */}
        {tag_names && tag_names.length > 0 && (
          <div className="trip-card__tags">
            {tag_names.slice(0, 3).map((tagName, index) => (
              <span key={index} className="trip-card__tag">
                {tagName}
              </span>
            ))}
            {tag_names.length > 3 && (
              <span className="trip-card__tag trip-card__tag--more">
                +{tag_names.length - 3}
              </span>
            )}
          </div>
        )}
      </div>
    </Link>
  );
};
