/**
 * Trip summary for dashboard and lists
 */
export interface TripSummary {
  id: string;
  title: string;
  description?: string;
  start_date: string;
  end_date?: string;
  distance_km: number;
  difficulty?: 'easy' | 'moderate' | 'hard' | 'extreme';
  status: 'DRAFT' | 'PUBLISHED';
  tags: string[];
  photo_url?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Full trip details (for trip detail page)
 */
export interface Trip extends TripSummary {
  user_id: string;
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
