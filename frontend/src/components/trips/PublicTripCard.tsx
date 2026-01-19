/**
 * PublicTripCard Component (Feature 013 - T027)
 *
 * Displays a public trip card for the homepage feed.
 * Shows: title, photo, location (if exists), distance, date, author.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PublicTripSummary } from '../../types/trip';
import { LikeButton } from '../likes/LikeButton';
import { FollowButton } from '../social/FollowButton';
import { LikesListModal } from '../likes/LikesListModal';
import './PublicTripCard.css';

interface PublicTripCardProps {
  /** Trip data to display */
  trip: PublicTripSummary;
}

/**
 * Format date in Spanish locale
 *
 * @param dateString - ISO date string (YYYY-MM-DD)
 * @returns Formatted date (e.g., "15 de mayo de 2024")
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString + 'T00:00:00'); // Force local timezone
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * Get photo URL with fallback
 *
 * @param url - Photo URL (can be null)
 * @returns Photo URL or placeholder
 */
const getPhotoUrl = (url: string | null | undefined): string => {
  if (!url) return '/images/placeholders/trip-placeholder.jpg';

  // Already absolute URL (from backend)
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // Relative path (development only)
  return `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`;
};

/**
 * PublicTripCard Component
 *
 * Displays a trip card with photo, title, author, location, distance, and date.
 * Clicking the card navigates to the trip detail page.
 *
 * @example
 * <PublicTripCard trip={tripData} />
 */
export const PublicTripCard: React.FC<PublicTripCardProps> = ({ trip }) => {
  const navigate = useNavigate();
  const [showLikesModal, setShowLikesModal] = useState(false);

  const handleClick = () => {
    navigate(`/trips/${trip.trip_id}`);
  };

  const handleLikesClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click navigation
    setShowLikesModal(true);
  };

  const handleAuthorClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click navigation
    navigate(`/users/${trip.author.username}`);
  };

  const photoUrl = trip.photo
    ? getPhotoUrl(trip.photo.thumbnail_url)
    : '/images/placeholders/trip-placeholder.jpg';

  return (
    <>
      <article className="public-trip-card" onClick={handleClick}>
        {/* Trip Photo */}
        <div className="public-trip-card__image-container">
          <img
            src={photoUrl}
            alt={trip.title}
            className="public-trip-card__image"
            loading="lazy"
          />
        </div>

        {/* Trip Content */}
        <div className="public-trip-card__content">
          {/* Title */}
          <h3 className="public-trip-card__title">{trip.title}</h3>

          {/* Author with Follow Button */}
          <div className="public-trip-card__author">
            <div className="public-trip-card__author-info" onClick={handleAuthorClick} style={{ cursor: 'pointer' }}>
              {trip.author.profile_photo_url ? (
                <img
                  src={getPhotoUrl(trip.author.profile_photo_url)}
                  alt={trip.author.username}
                  className="public-trip-card__author-avatar"
                />
              ) : (
                <div className="public-trip-card__author-avatar public-trip-card__author-avatar--placeholder">
                  {trip.author.username.charAt(0).toUpperCase()}
                </div>
              )}
              <span className="public-trip-card__author-name">{trip.author.username}</span>
            </div>
            <FollowButton
              username={trip.author.username}
              initialFollowing={trip.author.is_following || false}
              size="small"
              variant="secondary"
            />
          </div>

          {/* Metadata (Location, Distance, Date) */}
          <div className="public-trip-card__metadata">
            {/* Location */}
            {trip.location && (
              <div className="public-trip-card__metadata-item">
                <svg
                  className="public-trip-card__icon"
                  xmlns="http://www.w3.org/2000/svg"
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
                <span>{trip.location.name}</span>
              </div>
            )}

            {/* Distance */}
            {trip.distance_km && (
              <div className="public-trip-card__metadata-item">
                <svg
                  className="public-trip-card__icon"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M17 14h5v1a4 4 0 01-4 4H6a4 4 0 01-4-4v-1h5M12 16v6M4 8V4a2 2 0 012-2h12a2 2 0 012 2v4" />
                </svg>
                <span>{trip.distance_km.toFixed(1)} km</span>
              </div>
            )}

            {/* Date */}
            <div className="public-trip-card__metadata-item">
              <svg
                className="public-trip-card__icon"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>
              <span>{formatDate(trip.start_date)}</span>
            </div>
          </div>

          {/* Like Button (Feature 004 - US2) */}
          <div className="public-trip-card__interactions">
            <LikeButton
              tripId={trip.trip_id}
              initialLiked={trip.is_liked || false}
              initialCount={trip.like_count}
              size="small"
              showCount={true}
              onCountClick={trip.like_count > 0 ? handleLikesClick : undefined}
            />
          </div>
        </div>
      </article>

      {/* Likes List Modal - Outside article to prevent event bubbling */}
      <LikesListModal
        tripId={trip.trip_id}
        tripTitle={trip.title}
        isOpen={showLikesModal}
        onClose={() => setShowLikesModal(false)}
      />
    </>
  );
};
