/**
 * User statistics from backend API
 */
export interface UserStats {
  trip_count: number;
  total_distance_km: number;
  countries_visited: string[];
  follower_count: number;
  following_count: number;
  longest_trip_km: number;
  photo_count: number;
}

/**
 * Individual stat card data for display
 */
export interface StatCardData {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  color?: string; // For icon color theming
}
