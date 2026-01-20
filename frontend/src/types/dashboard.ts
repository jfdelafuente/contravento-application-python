/**
 * Dashboard TypeScript Interfaces
 * Feature: 015-dashboard-redesign
 *
 * Interfaces para consumir endpoints del dashboard backend (Python/FastAPI).
 * No son modelos de base de datos, sino contratos de API frontend-backend.
 */

// ============================================================================
// 1. Dashboard Statistics (Personal Stats)
// Fuente: GET /api/v1/dashboard/stats
// ============================================================================

export interface DashboardStats {
  user_id: string;
  username: string;
  total_trips: number;
  total_distance_km: number;
  towns_visited: number;
  countries_visited: number;
  total_photos: number;
  local_economic_impact_euros: number | null;
  followers_count: number;
  following_count: number;
  achievements_unlocked: number;
  achievements_total: number;
  last_updated: string; // ISO 8601 date
}

// ============================================================================
// 2. Activity Feed (Social Feed)
// Fuente: GET /api/v1/dashboard/feed?page=1&limit=50
// ============================================================================

export type FeedActivityType =
  | 'trip_published'
  | 'achievement_unlocked'
  | 'challenge_completed'
  | 'comment_added'
  | 'like_received';

export interface FeedItem {
  activity_id: string;
  activity_type: FeedActivityType;
  actor_user_id: string;
  actor_username: string;
  actor_photo_url: string | null;
  timestamp: string; // ISO 8601 date

  // Polymorphic content based on activity_type
  content: TripPublishedContent | AchievementContent | ChallengeContent | CommentContent | LikeContent;
}

export interface TripPublishedContent {
  trip_id: string;
  trip_title: string;
  trip_cover_photo_url: string | null;
  trip_distance_km: number;
  trip_countries: string[];
}

export interface AchievementContent {
  achievement_id: string;
  achievement_name: string;
  achievement_icon_url: string;
  achievement_description: string;
}

export interface ChallengeContent {
  challenge_id: string;
  challenge_name: string;
  challenge_icon_url: string;
}

export interface CommentContent {
  trip_id: string;
  trip_title: string;
  comment_text: string;
}

export interface LikeContent {
  trip_id: string;
  trip_title: string;
  trip_cover_photo_url: string | null;
}

export interface FeedResponse {
  items: FeedItem[];
  total_count: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

// ============================================================================
// 3. Suggested Routes (Recommendations)
// Fuente: GET /api/v1/dashboard/suggested-routes?limit=5
// ============================================================================

export type RouteDifficulty = 'easy' | 'moderate' | 'hard' | 'expert';

export interface SuggestedRoute {
  route_id: string;
  title: string;
  description: string;
  distance_km: number;
  difficulty: RouteDifficulty;
  estimated_duration_hours: number;
  cover_photo_url: string | null;

  // Why this route is suggested
  reason: string; // e.g., "Incluye pueblos que no has visitado"

  // Route metadata
  towns_included: string[];
  countries: string[];
  rating_avg: number; // 0-5
  completed_by_count: number;

  // User context
  is_completed: boolean;
  is_saved: boolean;
}

export interface SuggestedRoutesResponse {
  routes: SuggestedRoute[];
  total_available: number;
}

// ============================================================================
// 4. Active Challenges (Gamification)
// Fuente: GET /api/v1/dashboard/challenges
// ============================================================================

export type ChallengeStatus = 'in_progress' | 'completed' | 'failed' | 'expired';

export interface ActiveChallenge {
  challenge_id: string;
  name: string;
  description: string;
  icon_url: string;
  status: ChallengeStatus;

  // Progress tracking
  current_progress: number;
  required_progress: number;
  progress_unit: string; // e.g., "comercios visitados", "kilómetros recorridos"

  // Dates
  started_at: string; // ISO 8601
  expires_at: string | null; // null if no expiration
  completed_at: string | null;

  // Rewards
  reward_achievement_id: string | null;
  reward_achievement_name: string | null;
}

export interface ChallengesResponse {
  challenges: ActiveChallenge[];
  total_active: number;
  total_completed_all_time: number;
}

// ============================================================================
// 5. Global Search (Autocomplete)
// Fuente: GET /api/v1/dashboard/search?q={query}&types=users,routes,towns
// ============================================================================

export type SearchResultType = 'user' | 'route' | 'town';

export interface SearchResult {
  result_id: string;
  type: SearchResultType;
  title: string;
  subtitle: string | null;
  photo_url: string | null;
  url: string; // Frontend route to navigate to

  // Type-specific metadata
  metadata: UserMetadata | RouteMetadata | TownMetadata;
}

export interface UserMetadata {
  user_id: string;
  username: string;
  follower_count: number;
  is_following: boolean;
}

export interface RouteMetadata {
  route_id: string;
  distance_km: number;
  difficulty: RouteDifficulty;
  completed_by_count: number;
}

export interface TownMetadata {
  town_id: string;
  country: string;
  visitor_count: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total_count: number;
  query: string;
}
