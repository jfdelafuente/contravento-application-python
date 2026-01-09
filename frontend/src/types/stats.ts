/**
 * Country information from backend API
 */
export interface CountryInfo {
  code: string;
  name: string;
}

/**
 * User statistics from backend API
 */
export interface UserStats {
  total_trips: number;
  total_kilometers: number;
  countries_visited: CountryInfo[];
  total_photos: number;
  achievements_count: number;
  last_trip_date: string | null;
  updated_at: string;
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
