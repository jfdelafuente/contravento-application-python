import React, { memo, useMemo } from 'react';
import { TripSummary } from '../../types/trip';
import { formatShortDate } from '../../utils/formatters';
import { formatDistance, getPhotoUrl } from '../../utils/tripHelpers';
import './RecentTripCard.css';

export interface RecentTripCardProps {
  trip: TripSummary;
}

// rendering-hoist-jsx: Static SVG icons hoisted outside component
const PhotoPlaceholderIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    <circle cx="8.5" cy="8.5" r="1.5" />
    <polyline points="21 15 16 10 5 21" />
  </svg>
);

const CalendarIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
    <line x1="16" y1="2" x2="16" y2="6" />
    <line x1="8" y1="2" x2="8" y2="6" />
    <line x1="3" y1="10" x2="21" y2="10" />
  </svg>
);

const DistanceIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
  </svg>
);

/**
 * RecentTripCard component - Display trip summary with photo and details
 * Shows thumbnail if available, otherwise shows photo count placeholder
 *
 * Performance optimizations:
 * - rerender-memo: Memoized to prevent re-renders when parent re-renders
 * - rendering-hoist-jsx: SVG icons hoisted outside component
 * - js-cache-property-access: Cached computed values with useMemo
 */
const RecentTripCard: React.FC<RecentTripCardProps> = memo(({ trip }) => {
  // js-cache-property-access: Cache computed values
  const photoUrl = useMemo(() => getPhotoUrl(trip.thumbnail_url), [trip.thumbnail_url]);
  const shortDate = useMemo(() => formatShortDate(trip.start_date), [trip.start_date]);
  const distanceText = useMemo(() => formatDistance(trip.distance_km), [trip.distance_km]);
  const photoCountText = useMemo(() => {
    if (trip.photo_count === 0) return 'Sin foto';
    return `${trip.photo_count} foto${trip.photo_count > 1 ? 's' : ''}`;
  }, [trip.photo_count]);

  const visibleTags = useMemo(() => trip.tag_names?.slice(0, 3) || [], [trip.tag_names]);
  const remainingTagsCount = useMemo(() =>
    (trip.tag_names?.length || 0) - 3,
    [trip.tag_names]
  );

  return (
    <article className="recent-trip-card">
      <a href={`/trips/${trip.trip_id}`} className="recent-trip-card__link">
        {/* Photo */}
        <div className="recent-trip-card__photo">
          {trip.thumbnail_url ? (
            <img
              src={photoUrl}
              alt={trip.title}
              className="recent-trip-card__image"
              loading="lazy"
            />
          ) : (
            <div className="recent-trip-card__photo-placeholder">
              <PhotoPlaceholderIcon />
              <span>{photoCountText}</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="recent-trip-card__content">
          <h3 className="recent-trip-card__title">{trip.title}</h3>

          <div className="recent-trip-card__meta">
            <span className="recent-trip-card__date">
              <CalendarIcon />
              {shortDate}
            </span>

            <span className="recent-trip-card__distance">
              <DistanceIcon />
              {distanceText}
            </span>
          </div>

          {/* Tags */}
          {visibleTags.length > 0 && (
            <div className="recent-trip-card__tags">
              {visibleTags.map((tag: string, index: number) => (
                <span key={index} className="recent-trip-card__tag">
                  {tag}
                </span>
              ))}
              {remainingTagsCount > 0 && (
                <span className="recent-trip-card__tag recent-trip-card__tag--more">
                  +{remainingTagsCount}
                </span>
              )}
            </div>
          )}
        </div>
      </a>
    </article>
  );
});

RecentTripCard.displayName = 'RecentTripCard';

export default RecentTripCard;
