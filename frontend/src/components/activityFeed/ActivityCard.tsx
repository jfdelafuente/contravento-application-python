/**
 * Activity Card Component (Feature 018 - T038)
 *
 * Displays a single activity in the feed with user info, timestamp, and metadata.
 * Renders different variants based on activity type.
 */

import React from 'react';
import { ActivityFeedItem } from '../../types/activityFeed';
import { ActivityCardTrip } from './ActivityCardTrip';
import { ActivityCardPhoto } from './ActivityCardPhoto';
import { ActivityCardAchievement } from './ActivityCardAchievement';
import './ActivityCard.css';

interface ActivityCardProps {
  activity: ActivityFeedItem;
}

/**
 * Activity Card Component
 *
 * Wrapper component that renders the appropriate activity variant based on activity_type.
 *
 * **Activity Types**:
 * - TRIP_PUBLISHED → ActivityCardTrip
 * - PHOTO_UPLOADED → ActivityCardPhoto
 * - ACHIEVEMENT_UNLOCKED → ActivityCardAchievement
 *
 * @example
 * ```typescript
 * <ActivityCard activity={activity} />
 * ```
 */
export const ActivityCard: React.FC<ActivityCardProps> = ({ activity }) => {
  switch (activity.activity_type) {
    case 'TRIP_PUBLISHED':
      return <ActivityCardTrip activity={activity} />;
    case 'PHOTO_UPLOADED':
      return <ActivityCardPhoto activity={activity} />;
    case 'ACHIEVEMENT_UNLOCKED':
      return <ActivityCardAchievement activity={activity} />;
    default:
      // Fallback for unknown activity types
      return null;
  }
};
