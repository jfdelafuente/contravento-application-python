/**
 * FeedItem Component (Feature 004 - T034)
 *
 * Displays a feed item (trip card) for the personalized feed.
 * Shows: photo, title, author, description excerpt, metadata, and interaction counters.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FeedItem as FeedItemType } from '../../services/feedService';
import { LikeButton } from '../likes/LikeButton';
import { FollowButton } from '../social/FollowButton';
import './FeedItem.css';

interface FeedItemProps {
  /** Feed item data to display */
  item: FeedItemType;

  /** Optional click handler (if not provided, navigates to trip detail) */
  onClick?: (tripId: string) => void;
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
 * Format date range for trip duration
 *
 * @param startDate - Start date (YYYY-MM-DD)
 * @param endDate - End date (YYYY-MM-DD) or null
 * @returns Formatted date range
 */
const formatDateRange = (startDate: string, endDate: string | null): string => {
  if (!endDate || startDate === endDate) {
    return formatDate(startDate);
  }

  return `${formatDate(startDate)} - ${formatDate(endDate)}`;
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
 * Truncate description to N characters with ellipsis
 *
 * @param text - HTML description
 * @param maxLength - Maximum length (default 150)
 * @returns Truncated text
 */
const truncateDescription = (text: string, maxLength: number = 150): string => {
  // Strip HTML tags
  const plainText = text.replace(/<[^>]*>/g, '');

  if (plainText.length <= maxLength) {
    return plainText;
  }

  return plainText.substring(0, maxLength).trim() + '...';
};

/**
 * FeedItem Component
 *
 * Displays a trip card in the personalized feed with:
 * - Trip photo (first photo or placeholder)
 * - Author info (avatar, username)
 * - Trip title and description excerpt
 * - Metadata (location, distance, date)
 * - Interaction counters (likes, comments, shares)
 * - Tags
 *
 * Clicking the card navigates to the trip detail page.
 *
 * @example
 * <FeedItem item={feedItemData} />
 */
export const FeedItem: React.FC<FeedItemProps> = ({ item, onClick }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick(item.trip_id);
    } else {
      navigate(`/trips/${item.trip_id}`);
    }
  };

  const photoUrl =
    item.photos.length > 0
      ? getPhotoUrl(item.photos[0].photo_url)
      : '/images/placeholders/trip-placeholder.jpg';

  const firstLocation = item.locations.length > 0 ? item.locations[0].name : null;

  return (
    <article className="feed-item" onClick={handleClick}>
      {/* Trip Photo */}
      <div className="feed-item__image-container">
        <img
          src={photoUrl}
          alt={item.title}
          className="feed-item__image"
          loading="lazy"
        />
      </div>

      {/* Trip Content */}
      <div className="feed-item__content">
        {/* Author with Follow Button */}
        <div className="feed-item__author">
          <div className="feed-item__author-main">
            {item.author.profile_photo_url ? (
              <img
                src={getPhotoUrl(item.author.profile_photo_url)}
                alt={item.author.username}
                className="feed-item__author-avatar"
              />
            ) : (
              <div className="feed-item__author-avatar feed-item__author-avatar--placeholder">
                {item.author.username.charAt(0).toUpperCase()}
              </div>
            )}
            <div className="feed-item__author-info">
              <span className="feed-item__author-username">{item.author.username}</span>
              {item.author.full_name && (
                <span className="feed-item__author-fullname">{item.author.full_name}</span>
              )}
            </div>
          </div>
          <FollowButton
            username={item.author.username}
            initialFollowing={item.author.is_following || false}
            size="small"
            variant="secondary"
          />
        </div>

        {/* Title */}
        <h3 className="feed-item__title">{item.title}</h3>

        {/* Description Excerpt */}
        <p className="feed-item__description">{truncateDescription(item.description)}</p>

        {/* Metadata (Location, Distance, Date) */}
        <div className="feed-item__metadata">
          {/* Location */}
          {firstLocation && (
            <div className="feed-item__metadata-item">
              <svg
                className="feed-item__icon"
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
              <span>{firstLocation}</span>
            </div>
          )}

          {/* Distance */}
          {item.distance_km && (
            <div className="feed-item__metadata-item">
              <svg
                className="feed-item__icon"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              <span>{item.distance_km.toFixed(1)} km</span>
            </div>
          )}

          {/* Date */}
          <div className="feed-item__metadata-item">
            <svg
              className="feed-item__icon"
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
            <span>{formatDateRange(item.start_date, item.end_date)}</span>
          </div>
        </div>

        {/* Tags */}
        {item.tags.length > 0 && (
          <div className="feed-item__tags">
            {item.tags.slice(0, 3).map((tag) => (
              <span key={tag.normalized} className="feed-item__tag">
                #{tag.name}
              </span>
            ))}
            {item.tags.length > 3 && (
              <span className="feed-item__tag feed-item__tag--more">
                +{item.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Interaction Counters */}
        <div className="feed-item__interactions">
          {/* Likes - Interactive LikeButton */}
          <LikeButton
            tripId={item.trip_id}
            initialLiked={item.is_liked_by_me}
            initialCount={item.likes_count}
            size="small"
            showCount={true}
          />

          {/* Comments */}
          <div className="feed-item__interaction">
            <svg
              className="feed-item__interaction-icon"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <span className="feed-item__interaction-count">{item.comments_count}</span>
          </div>

          {/* Shares */}
          <div className="feed-item__interaction">
            <svg
              className="feed-item__interaction-icon"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
            </svg>
            <span className="feed-item__interaction-count">{item.shares_count}</span>
          </div>
        </div>
      </div>
    </article>
  );
};
