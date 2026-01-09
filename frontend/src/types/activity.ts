/**
 * Activity types for user activity feed
 */
export type ActivityType =
  | 'trip_published'
  | 'photo_uploaded'
  | 'new_follower'
  | 'badge_earned'
  | 'trip_liked'
  | 'trip_commented';

/**
 * Activity item in user feed
 */
export interface Activity {
  id: string;
  user_id: string;
  type: ActivityType;
  message: string;
  timestamp: string;
  link?: string;
  metadata?: {
    trip_id?: string;
    trip_title?: string;
    photo_count?: number;
    follower_username?: string;
    badge_name?: string;
  };
}

/**
 * Activity feed response
 */
export interface ActivityFeed {
  activities: Activity[];
  total_count: number;
  has_more: boolean;
}
