/**
 * Trip summary for dashboard and lists
 */
export interface TripSummary {
  trip_id: string;
  user_id: string;
  title: string;
  description?: string;
  start_date: string;
  end_date?: string;
  distance_km: number;
  difficulty?: 'easy' | 'moderate' | 'hard' | 'extreme';
  status: 'draft' | 'published';
  tags: string[];
  photos_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Full trip details (for trip detail page)
 */
export interface Trip extends TripSummary {
  photos: TripPhoto[];
  location?: TripLocation;
}

/**
 * Trip photo
 */
export interface TripPhoto {
  id: string;
  trip_id: string;
  url: string;
  file_size: number;
  width: number;
  height: number;
  order: number;
  caption?: string;
  created_at: string;
}

/**
 * Trip location data
 */
export interface TripLocation {
  id: string;
  trip_id: string;
  latitude: number;
  longitude: number;
  address?: string;
  country?: string;
}
