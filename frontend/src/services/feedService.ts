/**
 * Feed Service - API calls for personalized feed (Feature 004 - T031)
 *
 * Provides functions to interact with the personalized feed endpoint.
 * The feed shows trips from followed users + popular community backfill.
 */

import { api } from './api';

/**
 * User summary for feed item author
 */
export interface UserSummary {
  username: string;
  full_name: string | null;
  profile_photo_url: string | null;
}

/**
 * Photo summary for feed item
 */
export interface PhotoSummary {
  photo_url: string;
  caption: string | null;
}

/**
 * Location summary for feed item
 */
export interface LocationSummary {
  name: string;
  latitude: number;
  longitude: number;
}

/**
 * Tag summary for feed item
 */
export interface TagSummary {
  name: string;
  normalized: string;
}

/**
 * Feed item - single trip in the personalized feed
 * Matches backend schema: FeedItem (backend/src/schemas/feed.py)
 */
export interface FeedItem {
  trip_id: string;
  title: string;
  description: string;
  author: UserSummary;
  photos: PhotoSummary[];
  distance_km: number | null;
  start_date: string; // ISO 8601 date (YYYY-MM-DD)
  end_date: string | null; // ISO 8601 date (YYYY-MM-DD)
  locations: LocationSummary[];
  tags: TagSummary[];
  likes_count: number;
  comments_count: number;
  shares_count: number;
  is_liked_by_me: boolean;
  created_at: string; // ISO 8601 datetime
}

/**
 * Feed response with pagination
 * Matches backend schema: FeedResponse (backend/src/schemas/feed.py)
 */
export interface FeedResponse {
  trips: FeedItem[];
  total_count: number;
  page: number;
  limit: number;
  has_more: boolean;
}

/**
 * Parameters for getFeed()
 */
export interface GetFeedParams {
  page?: number; // Page number (min 1, default 1)
  limit?: number; // Items per page (min 1, max 50, default 10)
}

/**
 * Fetch personalized feed (Feature 004 - FR-001)
 *
 * Returns personalized trip feed for authenticated user with hybrid algorithm:
 * 1. Trips from followed users (chronological DESC)
 * 2. Popular community trips backfill if needed
 *
 * **Requires authentication** - JWT token must be present in cookies
 *
 * @param params - Pagination parameters (page, limit)
 * @returns FeedResponse with trips and pagination metadata
 * @throws 401 if user is not authenticated
 * @throws 400 if pagination parameters are invalid
 *
 * @example
 * ```typescript
 * // Get first page with default limit (10)
 * const feed = await getFeed({ page: 1 });
 *
 * // Get page 2 with custom limit
 * const feed = await getFeed({ page: 2, limit: 20 });
 * ```
 */
export const getFeed = async (params: GetFeedParams = {}): Promise<FeedResponse> => {
  const { page = 1, limit = 10 } = params;

  const queryParams = new URLSearchParams();
  queryParams.append('page', page.toString());
  queryParams.append('limit', limit.toString());

  const url = `/feed?${queryParams.toString()}`;
  const response = await api.get<FeedResponse>(url);

  return response.data;
};
