/**
 * Trip TypeScript Type Definitions
 *
 * Type definitions for the Travel Diary feature.
 * Based on backend API contracts from Feature 002 (Travel Diary Backend).
 */

// ============================================================================
// Core Entities (API Responses)
// ============================================================================

/**
 * Complete trip data from backend API
 *
 * Used in:
 * - TripDetailPage (view full trip)
 * - TripEditPage (edit existing trip)
 * - After creating/updating a trip
 */
export interface Trip {
  /** Unique trip identifier (UUID) */
  trip_id: string;

  /** Trip owner's user ID (UUID) */
  user_id: string;

  /** Trip title (1-200 characters) */
  title: string;

  /** Trip description (HTML, sanitized by backend, max 50000 chars) */
  description: string;

  /** Publication status */
  status: 'draft' | 'published';

  /** Trip start date (ISO 8601: YYYY-MM-DD) */
  start_date: string;

  /** Trip end date (ISO 8601: YYYY-MM-DD, null if single-day trip) */
  end_date: string | null;

  /** Distance in kilometers (0.1-10000, null if not provided) */
  distance_km: number | null;

  /** Difficulty level (null if not provided) */
  difficulty: TripDifficulty | null;

  /** Trip creation timestamp (ISO 8601: YYYY-MM-DDTHH:mm:ssZ) */
  created_at: string;

  /** Last update timestamp (ISO 8601: YYYY-MM-DDTHH:mm:ssZ) */
  updated_at: string;

  /** Publication timestamp (ISO 8601, null if draft) */
  published_at: string | null;

  /** Trip photos (ordered by display_order) */
  photos: TripPhoto[];

  /** Trip locations/waypoints (ordered by sequence) */
  locations: TripLocation[];

  /** Trip tags for categorization */
  tags: Tag[];
}

/**
 * Trip summary for list/grid views
 *
 * Used in:
 * - TripsListPage (browse all trips)
 * - ProfilePage (user's recent trips)
 * - Search results
 */
export interface TripListItem {
  /** Unique trip identifier (UUID) */
  trip_id: string;

  /** Trip owner's user ID (UUID) */
  user_id: string;

  /** Trip title */
  title: string;

  /** Trip start date (ISO 8601: YYYY-MM-DD) */
  start_date: string;

  /** Distance in kilometers (null if not provided) */
  distance_km: number | null;

  /** Publication status */
  status: 'draft' | 'published';

  /** Number of photos attached to trip */
  photo_count: number;

  /** Tag names only (for filtering, lighter payload) */
  tag_names: string[];

  /** First photo thumbnail URL (null if no photos) */
  thumbnail_url: string | null;

  /** Trip creation timestamp (ISO 8601: YYYY-MM-DDTHH:mm:ssZ) */
  created_at: string;
}

/**
 * Legacy alias for TripListItem (backward compatibility)
 * @deprecated Use TripListItem instead
 */
export type TripSummary = TripListItem;

/**
 * Trip photo data
 *
 * Used in:
 * - TripGallery (photo grid with lightbox)
 * - PhotoUploader (uploaded photo preview)
 */
export interface TripPhoto {
  /** Unique photo identifier (UUID) */
  photo_id: string;

  /** URL to optimized photo (max 2000px width) */
  photo_url: string;

  /** URL to thumbnail (400x400px) */
  thumbnail_url: string;

  /** Optional photo caption (max 500 chars) */
  caption: string | null;

  /** Display order in gallery (0-based, reorderable) */
  display_order: number;

  /** Optimized photo width in pixels */
  width: number;

  /** Optimized photo height in pixels */
  height: number;
}

/**
 * Trip tag for categorization
 *
 * Used in:
 * - TagInput (autocomplete suggestions)
 * - TripFilters (clickable tag chips)
 * - Trip detail view (tag chips)
 */
export interface Tag {
  /** Unique tag identifier (UUID) */
  tag_id: string;

  /** Display name (preserves original casing, e.g., "Vías Verdes") */
  name: string;

  /** Normalized name for matching (lowercase, e.g., "vias verdes") */
  normalized: string;

  /** Number of trips using this tag (for popularity sorting) */
  usage_count: number;
}

/**
 * Trip location/waypoint
 *
 * Used in:
 * - TripMap (display markers on map)
 * - Location list in trip details
 */
export interface TripLocation {
  /** Unique location identifier (UUID) */
  location_id: string;

  /** Location name (e.g., "Baeza", "Camino de Santiago") */
  name: string;

  /** Latitude coordinate (decimal degrees, null if not geocoded) */
  latitude: number | null;

  /** Longitude coordinate (decimal degrees, null if not geocoded) */
  longitude: number | null;

  /** Order in route (0 = start, 1 = next waypoint, etc.) */
  sequence: number;
}

// ============================================================================
// Request/Input Schemas
// ============================================================================

/**
 * Input data for creating a new trip
 *
 * Used in:
 * - TripFormWizard (multi-step form submission)
 * - Step 4 (Review & Publish)
 */
export interface TripCreateInput {
  /** Trip title (1-200 characters, required) */
  title: string;

  /** Trip description (1-50000 characters, required, HTML allowed) */
  description: string;

  /** Trip start date (ISO 8601: YYYY-MM-DD, cannot be future) */
  start_date: string;

  /** Trip end date (ISO 8601: YYYY-MM-DD, must be >= start_date) */
  end_date: string | null;

  /** Distance in kilometers (0.1-10000, optional) */
  distance_km: number | null;

  /** Difficulty level (optional) */
  difficulty: TripDifficulty | null;

  /** Locations visited during trip (max 50) */
  locations: LocationInput[];

  /** Tags for categorization (max 10 tags, max 50 chars each) */
  tags: string[];
}

/**
 * Input data for updating an existing trip
 *
 * All fields are optional - only provided fields will be updated.
 *
 * Used in:
 * - TripFormWizard (edit mode)
 * - Step 4 (Review & Publish)
 */
export interface TripUpdateInput {
  /** Trip title (1-200 characters) */
  title?: string;

  /** Trip description (1-50000 characters, HTML allowed) */
  description?: string;

  /** Trip start date (ISO 8601: YYYY-MM-DD) */
  start_date?: string;

  /** Trip end date (ISO 8601: YYYY-MM-DD, must be >= start_date) */
  end_date?: string | null;

  /** Distance in kilometers (0.1-10000) */
  distance_km?: number | null;

  /** Difficulty level */
  difficulty?: TripDifficulty | null;

  /** Locations (replaces existing) */
  locations?: LocationInput[];

  /** Tags (replaces existing, max 10) */
  tags?: string[];

  /** Timestamp when client loaded the trip (optimistic locking) */
  client_updated_at?: string;
}

/**
 * Location input for trip forms
 *
 * Used in:
 * - Step 1 (Basic Info) - location input field
 * - Trip creation/update requests
 */
export interface LocationInput {
  /** Location name (1-200 characters, required) */
  name: string;

  /** Country name (max 100 characters, optional) */
  country?: string;

  /** Latitude in decimal degrees (-90 to 90, optional) */
  latitude?: number | null;

  /** Longitude in decimal degrees (-180 to 180, optional) */
  longitude?: number | null;
}

// ============================================================================
// Response Schemas
// ============================================================================

/**
 * Paginated trip list response
 *
 * Used in:
 * - TripsListPage (browse trips with filters)
 * - useTripList hook (pagination logic)
 */
export interface TripListResponse {
  /** List of trip summaries for current page */
  trips: TripListItem[];

  /** Total number of trips matching filter (for pagination UI) */
  total: number;

  /** Page size used for this request */
  limit: number;

  /** Pagination offset used for this request */
  offset: number;
}

/**
 * Standard API error response
 *
 * Used in:
 * - All API service error handlers
 * - Error toast notifications
 */
export interface ApiError {
  /** Always false for errors */
  success: false;

  /** Null data payload */
  data: null;

  /** Error details */
  error: {
    /** Error code (e.g., "VALIDATION_ERROR", "NOT_FOUND") */
    code: string;

    /** User-friendly error message in Spanish */
    message: string;

    /** Optional field name for validation errors */
    field?: string;
  };
}

// ============================================================================
// Form State (Client-Only)
// ============================================================================

/**
 * Form state for TripFormWizard (all 4 steps combined)
 *
 * Used in:
 * - TripFormWizard (parent component state)
 * - All step components (Step1-4)
 * - Zod validation schema
 */
export interface TripFormData {
  // Step 1: Basic Info
  title: string;
  start_date: string; // HTML date input format: YYYY-MM-DD
  end_date: string;
  distance_km: string; // String in form, parsed to number on submit
  difficulty: TripDifficulty | '';

  // Step 2: Story & Tags
  description: string;
  tags: string[]; // Array of tag names

  // Step 3: Photos
  // Photos handled separately via PhotoUploader (file uploads)

  // Step 4: Review
  // Read-only summary of all fields above
}

/**
 * Photo upload state for PhotoUploader component
 *
 * Used in:
 * - PhotoUploader (Step 3)
 * - useTripPhotos hook
 */
export interface PhotoUploadState {
  /** Selected files for upload */
  files: File[];

  /** Upload progress per file (0-100) */
  progress: Record<string, number>; // key: file.name, value: percentage

  /** Upload status per file */
  status: Record<string, 'pending' | 'uploading' | 'success' | 'error'>;

  /** Uploaded photo responses from backend */
  uploadedPhotos: TripPhoto[];

  /** Error messages per file */
  errors: Record<string, string>;
}

// ============================================================================
// Enums and Constants
// ============================================================================

/**
 * Trip publication status
 */
export type TripStatus = 'draft' | 'published';

/**
 * Trip difficulty levels
 */
export type TripDifficulty = 'easy' | 'moderate' | 'difficult' | 'very_difficult';

/**
 * Difficulty labels in Spanish
 */
export const DIFFICULTY_LABELS: Record<TripDifficulty, string> = {
  easy: 'Fácil',
  moderate: 'Moderada',
  difficult: 'Difícil',
  very_difficult: 'Muy Difícil',
};

/**
 * Difficulty CSS class names
 */
export const DIFFICULTY_CLASSES: Record<TripDifficulty, string> = {
  easy: 'difficulty-badge--easy',
  moderate: 'difficulty-badge--moderate',
  difficult: 'difficulty-badge--difficult',
  very_difficult: 'difficulty-badge--very-difficult',
};

// ============================================================================
// Public Feed Types (Feature 013 - Public Trips Feed)
// ============================================================================

/**
 * User summary for public trip feed
 *
 * Minimal user info displayed on public trip cards - only public profile data.
 *
 * Used in:
 * - PublicFeedPage (homepage)
 * - PublicTripCard component
 */
export interface PublicUserSummary {
  /** Unique user identifier (UUID) */
  user_id: string;

  /** Username (for profile link) */
  username: string;

  /** Profile photo URL (null if no photo) */
  profile_photo_url: string | null;
}

/**
 * Photo summary for public trip feed
 *
 * Minimal photo info for trip cards - only first photo thumbnail.
 *
 * Used in:
 * - PublicTripCard (display first photo)
 */
export interface PublicPhotoSummary {
  /** URL to optimized photo */
  photo_url: string;

  /** URL to thumbnail */
  thumbnail_url: string;
}

/**
 * Location summary for public trip feed
 *
 * Minimal location info for trip cards - only first location name.
 *
 * Used in:
 * - PublicTripCard (display first location)
 */
export interface PublicLocationSummary {
  /** Location name (e.g., "Baeza, España") */
  name: string;
}

/**
 * Trip summary for public feed (Feature 013)
 *
 * Optimized for homepage display - shows only essential trip data.
 *
 * Requirements (FR-002):
 * - título, foto, distancia, location (primera), fecha, autor
 *
 * Used in:
 * - PublicFeedPage (homepage trip grid)
 * - PublicTripCard component
 */
export interface PublicTripSummary {
  /** Unique trip identifier (UUID) */
  trip_id: string;

  /** Trip title */
  title: string;

  /** Trip start date (ISO 8601: YYYY-MM-DD) */
  start_date: string;

  /** Distance in kilometers (null if not provided) */
  distance_km: number | null;

  /** First photo thumbnail (null if no photos) */
  photo: PublicPhotoSummary | null;

  /** First location (null if no locations) */
  location: PublicLocationSummary | null;

  /** Trip author summary */
  author: PublicUserSummary;

  /** Publication timestamp (ISO 8601, for sorting) */
  published_at: string;
}

/**
 * Pagination metadata for public feed
 *
 * Provides information for client-side pagination controls.
 *
 * Used in:
 * - PublicFeedPage (pagination UI)
 * - usePublicTrips hook
 */
export interface PaginationInfo {
  /** Total number of trips matching filter */
  total: number;

  /** Current page number (1-indexed) */
  page: number;

  /** Page size (trips per page, max 50) */
  limit: number;

  /** Total number of pages */
  total_pages: number;
}

/**
 * Paginated response for public trips feed (Feature 013)
 *
 * Main response schema for GET /trips/public endpoint.
 *
 * Used in:
 * - PublicFeedPage (homepage)
 * - usePublicTrips hook
 */
export interface PublicTripListResponse {
  /** List of public trip summaries */
  trips: PublicTripSummary[];

  /** Pagination metadata */
  pagination: PaginationInfo;
}
