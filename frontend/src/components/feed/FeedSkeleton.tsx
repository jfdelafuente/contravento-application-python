/**
 * FeedSkeleton Component (Feature 004 - T036)
 *
 * Loading skeleton for feed items.
 * Shows placeholder cards while feed is loading.
 */

import React from 'react';
import './FeedSkeleton.css';

interface FeedSkeletonProps {
  /** Number of skeleton items to show (default: 3) */
  count?: number;
}

/**
 * FeedSkeleton Component
 *
 * Displays loading skeleton cards for feed.
 * Used during initial load and infinite scroll loading states.
 *
 * @example
 * ```typescript
 * {isLoading && <FeedSkeleton count={5} />}
 * ```
 */
export const FeedSkeleton: React.FC<FeedSkeletonProps> = ({ count = 3 }) => {
  return (
    <div className="feed-skeleton">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="feed-skeleton__item">
          {/* Image Skeleton */}
          <div className="feed-skeleton__image" />

          {/* Content Skeleton */}
          <div className="feed-skeleton__content">
            {/* Author Skeleton */}
            <div className="feed-skeleton__author">
              <div className="feed-skeleton__avatar" />
              <div className="feed-skeleton__author-info">
                <div className="feed-skeleton__line feed-skeleton__line--username" />
                <div className="feed-skeleton__line feed-skeleton__line--fullname" />
              </div>
            </div>

            {/* Title Skeleton */}
            <div className="feed-skeleton__title">
              <div className="feed-skeleton__line feed-skeleton__line--title" />
              <div className="feed-skeleton__line feed-skeleton__line--title feed-skeleton__line--short" />
            </div>

            {/* Description Skeleton */}
            <div className="feed-skeleton__description">
              <div className="feed-skeleton__line" />
              <div className="feed-skeleton__line" />
              <div className="feed-skeleton__line feed-skeleton__line--short" />
            </div>

            {/* Metadata Skeleton */}
            <div className="feed-skeleton__metadata">
              <div className="feed-skeleton__line feed-skeleton__line--metadata" />
              <div className="feed-skeleton__line feed-skeleton__line--metadata" />
              <div className="feed-skeleton__line feed-skeleton__line--metadata" />
            </div>

            {/* Tags Skeleton */}
            <div className="feed-skeleton__tags">
              <div className="feed-skeleton__tag" />
              <div className="feed-skeleton__tag" />
              <div className="feed-skeleton__tag" />
            </div>

            {/* Interactions Skeleton */}
            <div className="feed-skeleton__interactions">
              <div className="feed-skeleton__interaction" />
              <div className="feed-skeleton__interaction" />
              <div className="feed-skeleton__interaction" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
