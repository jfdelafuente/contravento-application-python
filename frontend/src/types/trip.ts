/**
 * Trip summary for dashboard and lists
 * Matches backend TripListItemResponse (actual runtime data)
 */
export interface TripSummary {
  trip_id: string;
  user_id: string;
  title: string;
  description?: string; // Only in detailed view
  start_date: string;
  end_date?: string; // Only in detailed view
  distance_km: number;
  difficulty?: 'easy' | 'moderate' | 'hard' | 'extreme'; // Only in detailed view
  status: 'draft' | 'published';
  tags: string[]; // Backend calls this tag_names but returns as tags
  photos_count: number; // Backend schema says photo_count but returns photos_count
  thumbnail_url?: string; // First photo thumbnail (optional)
  created_at: string;
  updated_at: string; // Only in some responses
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
