/**
 * Activity Feed types for Feature 018 - Activity Stream Feed
 *
 * Represents activities from followed users (trip published, photo uploaded, achievement unlocked).
 */

/**
 * Activity type enum
 */
export type ActivityType = 'TRIP_PUBLISHED' | 'PHOTO_UPLOADED' | 'ACHIEVEMENT_UNLOCKED';

/**
 * Public user summary for activity author
 */
export interface PublicUserSummary {
  user_id: string;
  username: string;
  photo_url: string | null;
}

/**
 * Activity metadata (type-specific data)
 */
export interface ActivityMetadata {
  // TRIP_PUBLISHED metadata
  trip_id?: string; // Trip UUID for navigation
  trip_title?: string;
  trip_distance_km?: number;
  trip_photo_url?: string;

  // PHOTO_UPLOADED metadata
  photo_url?: string;

  // ACHIEVEMENT_UNLOCKED metadata
  achievement_name?: string;
  achievement_badge?: string;
}

/**
 * Activity feed item
 * Matches backend schema: ActivityFeedItemSchema (backend/src/schemas/feed.py)
 */
export interface ActivityFeedItem {
  activity_id: string;
  user: PublicUserSummary;
  activity_type: ActivityType;
  metadata: ActivityMetadata;
  created_at: string; // ISO 8601 datetime
  likes_count: number;
  comments_count: number;
  is_liked_by_me: boolean;
}

/**
 * Activity feed response with cursor-based pagination
 * Matches backend schema: ActivityFeedResponseSchema (backend/src/schemas/feed.py)
 */
export interface ActivityFeedResponse {
  activities: ActivityFeedItem[];
  next_cursor: string | null;
  has_next: boolean;
}

/**
 * Parameters for getActivityFeed()
 */
export interface GetActivityFeedParams {
  cursor?: string | null; // Cursor for pagination (null for first page)
  limit?: number; // Items per page (min 1, max 50, default 20)
}
