// src/types/user.ts

export interface User {
  /** Unique user identifier (UUID from backend) */
  id: string;

  /** Unique username (3-30 alphanumeric + underscore) */
  username: string;

  /** User email address */
  email: string;

  /** Email verification status (per FR-008) */
  is_verified: boolean;

  /** Account creation timestamp */
  created_at: string; // ISO 8601

  /** Optional profile data */
  profile?: UserProfile;

  /** Optional statistics */
  stats?: UserStats;
}

export interface UserProfile {
  /** Full name (optional) */
  full_name?: string;

  /** Profile photo URL */
  photo_url?: string;

  /** Short biography (max 500 chars) */
  bio?: string;

  /** User location */
  location?: string;

  /** Social media links */
  social_links?: {
    instagram?: string;
    strava?: string;
    website?: string;
  };
}

export interface UserStats {
  /** Total trips published */
  trip_count: number;

  /** Total distance cycled (km) */
  total_distance_km: number;

  /** Number of followers */
  followers_count: number;

  /** Number of users following */
  following_count: number;
}
