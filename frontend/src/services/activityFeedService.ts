/**
 * Activity Feed Service - API calls for activity stream feed (Feature 018)
 *
 * Provides functions to interact with the activity feed endpoint.
 * The feed shows activities from followed users (trip published, photo uploaded, achievement unlocked).
 */

import { api } from './api';
import { ActivityFeedResponse, GetActivityFeedParams } from '../types/activityFeed';

// Re-export types for convenience
export type { ActivityFeedResponse, GetActivityFeedParams };

/**
 * Fetch activity feed (Feature 018 - US1, FR-001)
 *
 * Returns chronological activity stream from followed users with cursor-based pagination.
 *
 * **Activity Types**:
 * - TRIP_PUBLISHED: User published a new trip
 * - PHOTO_UPLOADED: User uploaded photos to a trip
 * - ACHIEVEMENT_UNLOCKED: User earned an achievement badge
 *
 * **Requires authentication** - JWT token must be present in cookies
 *
 * @param params - Pagination parameters (cursor, limit)
 * @returns ActivityFeedResponse with activities and pagination metadata
 * @throws 401 if user is not authenticated
 * @throws 400 if pagination parameters are invalid
 *
 * @example
 * ```typescript
 * // Get first page with default limit (20)
 * const feed = await getActivityFeed({});
 *
 * // Get next page with cursor
 * const nextPage = await getActivityFeed({ cursor: 'ABC123', limit: 20 });
 * ```
 */
export const getActivityFeed = async (
  params: GetActivityFeedParams = {}
): Promise<ActivityFeedResponse> => {
  const { cursor = null, limit = 20 } = params;

  const queryParams = new URLSearchParams();
  if (cursor) {
    queryParams.append('cursor', cursor);
  }
  queryParams.append('limit', limit.toString());

  const url = `/activity-feed?${queryParams.toString()}`;
  const response = await api.get<ActivityFeedResponse>(url);

  return response.data;
};
