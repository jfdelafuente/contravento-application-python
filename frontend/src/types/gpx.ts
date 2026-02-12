/**
 * GPX TypeScript Type Definitions
 *
 * Type definitions for Feature 003 - GPS Routes Interactive.
 * Based on backend API contracts from specs/003-gps-routes/contracts/gpx-api.yaml.
 */

// ============================================================================
// Core Entities (API Responses)
// ============================================================================

/**
 * GPX file metadata and processing results
 *
 * Represents a GPX file attached to a trip, including:
 * - Original file metadata (url, size, name)
 * - Processing status (pending, processing, completed, error)
 * - Route statistics (distance, elevation, bounds)
 * - Track simplification metadata (total_points vs simplified_points)
 *
 * Used in:
 * - Trip detail view (display GPX stats)
 * - GPXUploader (upload status tracking)
 * - GPXMapView (render track on map)
 */
export interface GPXFileMetadata {
  /** Unique GPX file identifier (UUID) */
  gpx_file_id: string;

  /** Associated trip ID (UUID) */
  trip_id: string;

  /** Original filename (e.g., "Camino_del_Cid.gpx") */
  file_name: string;

  /** File size in bytes */
  file_size: number;

  /** Total distance in kilometers */
  distance_km: number;

  /** Total elevation gain in meters (null if no elevation data) */
  elevation_gain: number | null;

  /** Total elevation loss in meters (null if no elevation data) */
  elevation_loss: number | null;

  /** Maximum altitude in meters (null if no elevation data) */
  max_elevation: number | null;

  /** Minimum altitude in meters (null if no elevation data) */
  min_elevation: number | null;

  /** Original trackpoint count before simplification */
  total_points: number;

  /** Reduced trackpoint count after Douglas-Peucker simplification */
  simplified_points: number;

  /** True if GPX includes elevation data */
  has_elevation: boolean;

  /** True if GPX includes timestamp data */
  has_timestamps: boolean;

  /** Current processing status */
  processing_status: GPXProcessingStatus;

  /** Error details if processing failed */
  error_message: string | null;

  /** Upload timestamp (ISO 8601) */
  uploaded_at: string;

  /** Processing completion timestamp (ISO 8601, null if not yet processed) */
  processed_at: string | null;
}

/**
 * Individual GPS trackpoint with coordinates and metrics
 *
 * Represents a single point on the simplified GPS track with:
 * - Geographic coordinates (latitude, longitude, elevation)
 * - Cumulative distance from route start
 * - Sequence number for ordering
 * - Calculated gradient (% slope)
 *
 * Used in:
 * - GPXMapView (render polyline on map)
 * - ElevationProfile (render elevation chart)
 * - Track analytics
 */
export interface TrackPoint {
  /** Unique trackpoint identifier (UUID) */
  point_id: string;

  /** Latitude in decimal degrees (-90 to 90) */
  latitude: number;

  /** Longitude in decimal degrees (-180 to 180) */
  longitude: number;

  /** Altitude in meters (null if not available) */
  elevation: number | null;

  /** Cumulative distance from start in kilometers */
  distance_km: number;

  /** Order in track (0-indexed) */
  sequence: number;

  /** Percentage slope (e.g., 5.2 = 5.2% uphill, null if no elevation data) */
  gradient: number | null;
}

/**
 * Geographic coordinate (start/end point)
 *
 * Simple lat/lon coordinate pair for route bounds.
 *
 * Used in:
 * - GPXMapView (display start/end markers)
 * - Track bounds calculation
 */
export interface Coordinate {
  /** Latitude in decimal degrees (-90 to 90) */
  latitude: number;

  /** Longitude in decimal degrees (-180 to 180) */
  longitude: number;
}

// ============================================================================
// Response Schemas
// ============================================================================

/**
 * Response from GPX upload endpoint
 *
 * Returned by POST /trips/{trip_id}/gpx after uploading a GPX file.
 *
 * Two modes:
 * - Synchronous (201): Small files (<1MB) processed immediately, includes full metadata
 * - Asynchronous (202): Large files (1-10MB) processing in background, includes status_url
 *
 * Used in:
 * - GPXUploader (upload feedback)
 * - useGPXUpload hook
 */
export interface GPXUploadResponse {
  /** Always true for successful uploads */
  success: true;

  /** GPX file data */
  data: {
    /** Unique GPX file identifier (UUID) */
    gpx_file_id: string;

    /** Associated trip ID (UUID) */
    trip_id: string;

    /** Current processing status */
    processing_status: GPXProcessingStatus;

    // Fields below only present if processing_status = 'completed'

    /** Total distance in kilometers (only if completed) */
    distance_km?: number;

    /** Total elevation gain in meters (only if completed) */
    elevation_gain?: number | null;

    /** Total elevation loss in meters (only if completed) */
    elevation_loss?: number | null;

    /** Maximum altitude in meters (only if completed) */
    max_elevation?: number | null;

    /** Minimum altitude in meters (only if completed) */
    min_elevation?: number | null;

    /** True if GPX includes elevation data (only if completed) */
    has_elevation?: boolean;

    /** True if GPX includes timestamp data (only if completed) */
    has_timestamps?: boolean;

    /** Original trackpoint count (only if completed) */
    total_points?: number;

    /** Reduced trackpoint count (only if completed) */
    simplified_points?: number;

    /** Upload timestamp (ISO 8601) */
    uploaded_at: string;

    /** Processing completion timestamp (ISO 8601, only if completed) */
    processed_at?: string;

    /** Error details (only if processing_status = 'error') */
    error_message?: string;
  };

  /** Optional message for async uploads */
  message?: string;
}

/**
 * Response from GPX status polling endpoint
 *
 * Returned by GET /gpx/{gpx_file_id}/status when polling async uploads.
 *
 * Poll every 2 seconds until status = "completed" or "error".
 *
 * Used in:
 * - GPXUploader (async upload polling)
 * - useGPXUpload hook
 */
export interface GPXStatusResponse {
  /** Always true for successful status checks */
  success: true;

  /** Same structure as GPXUploadResponse.data */
  data: GPXUploadResponse['data'];
}

/**
 * Individual climb data in top climbs list (User Story 5)
 *
 * Represents a single climb segment with elevation and gradient details.
 */
export interface TopClimb {
  /** Distance from start where climb begins (km) */
  start_km: number;

  /** Distance from start where climb ends (km) */
  end_km: number;

  /** Length of climb (km) - calculated as end_km - start_km */
  distance_km: number;

  /** Total elevation gain in climb (meters) */
  elevation_gain_m: number;

  /** Average gradient of climb (percentage, e.g., 8.5 = 8.5% slope) */
  avg_gradient: number;

  /** Human-readable climb description */
  description: string;
}

/**
 * Gradient category statistics (User Story 5 - FR-032)
 *
 * Statistics for one gradient category in the route.
 */
export interface GradientCategory {
  /** Total distance in this category (km) */
  distance_km: number;

  /** Percentage of total route distance */
  percentage: number;
}

/**
 * Gradient distribution breakdown (User Story 5 - FR-032)
 *
 * Classifies route segments into gradient categories:
 * - Llano (flat): 0-3%
 * - Moderado (moderate): 3-6%
 * - Empinado (steep): 6-10%
 * - Muy empinado (very steep): >10%
 */
export interface GradientDistribution {
  /** Flat terrain: 0-3% gradient */
  llano: GradientCategory;

  /** Moderate terrain: 3-6% gradient */
  moderado: GradientCategory;

  /** Steep terrain: 6-10% gradient */
  empinado: GradientCategory;

  /** Very steep terrain: >10% gradient */
  muy_empinado: GradientCategory;
}

/**
 * Advanced route statistics (User Story 5)
 *
 * Only present if GPX file has timestamps (has_timestamps=True).
 * Includes speed metrics, time analysis, gradient analysis, and top climbs.
 */
export interface RouteStatistics {
  /** Unique statistics record ID (UUID) */
  stats_id: string;

  /** Associated GPX file ID (UUID) */
  gpx_file_id: string;

  /** Average speed (km/h) */
  avg_speed_kmh: number | null;

  /** Maximum speed (km/h) */
  max_speed_kmh: number | null;

  /** Total elapsed time (minutes) */
  total_time_minutes: number | null;

  /** Time in motion, excludes stops (minutes) */
  moving_time_minutes: number | null;

  /** Average gradient over route (%) */
  avg_gradient: number | null;

  /** Maximum gradient (steepest uphill) (%) */
  max_gradient: number | null;

  /** Top 3 hardest climbs (max 3 items) */
  top_climbs: TopClimb[] | null;

  /** When statistics were calculated (ISO 8601) */
  created_at: string;

  /** Gradient distribution breakdown (FR-032) */
  gradient_distribution?: GradientDistribution;
}

/**
 * Response from track data endpoint
 *
 * Returned by GET /gpx/{gpx_file_id}/track with simplified trackpoints for rendering.
 *
 * Used in:
 * - GPXMapView (render route polyline)
 * - ElevationProfile (render elevation chart)
 * - useGPXTrack hook
 */
export interface TrackDataResponse {
  /** Always true for successful requests */
  success: true;

  /** Track data with simplified points */
  data: {
    /** Unique GPX file identifier (UUID) */
    gpx_file_id: string;

    /** Associated trip ID (UUID) */
    trip_id: string;

    /** Total distance in kilometers */
    distance_km: number;

    /** Total elevation gain in meters (null if no elevation data) */
    elevation_gain: number | null;

    /** Number of points in trackpoints array */
    simplified_points_count: number;

    /** True if trackpoints contain elevation data */
    has_elevation: boolean;

    /** Route start coordinate */
    start_point: Coordinate;

    /** Route end coordinate */
    end_point: Coordinate;

    /** Simplified trackpoints ordered by sequence */
    trackpoints: TrackPoint[];

    /** Advanced route statistics (only if GPX has timestamps) - User Story 5 */
    route_statistics: RouteStatistics | null;
  };
}

// ============================================================================
// Enums and Constants
// ============================================================================

/**
 * GPX file processing status
 *
 * Lifecycle:
 * - pending: File uploaded, not yet processing
 * - processing: Background task running (for files >1MB)
 * - completed: Successfully processed, trackpoints extracted
 * - error: Processing failed (malformed GPX, corrupted file, etc.)
 */
export type GPXProcessingStatus = 'pending' | 'processing' | 'completed' | 'error';

/**
 * Processing status labels in Spanish
 */
export const PROCESSING_STATUS_LABELS: Record<GPXProcessingStatus, string> = {
  pending: 'Pendiente',
  processing: 'Procesando',
  completed: 'Completado',
  error: 'Error',
};

/**
 * Processing status CSS class names
 */
export const PROCESSING_STATUS_CLASSES: Record<GPXProcessingStatus, string> = {
  pending: 'gpx-status--pending',
  processing: 'gpx-status--processing',
  completed: 'gpx-status--completed',
  error: 'gpx-status--error',
};

// ============================================================================
// Component Props (Client-Only)
// ============================================================================

/**
 * Props for GPXUploader component
 *
 * Used in:
 * - TripDetailPage (upload GPX to trip)
 */
export interface GPXUploaderProps {
  /** Trip ID to attach GPX file to */
  tripId: string;

  /** Callback when upload completes successfully */
  onUploadComplete?: (gpxFileId: string) => void;

  /** Callback when upload fails */
  onUploadError?: (error: string) => void;
}

/**
 * Props for GPXMapView component
 *
 * Used in:
 * - TripDetailPage (display route on map)
 */
export interface GPXMapViewProps {
  /** Trackpoints to render as polyline */
  trackPoints: TrackPoint[];

  /** Route start coordinate */
  startPoint: Coordinate;

  /** Route end coordinate */
  endPoint: Coordinate;

  /** Auto-fit map bounds to track on load (default: true) */
  autoFitBounds?: boolean;

  /** Callback when trackpoint is clicked */
  onPointClick?: (point: TrackPoint) => void;
}

/**
 * Props for ElevationProfile component
 *
 * Used in:
 * - TripDetailPage (display elevation chart)
 */
export interface ElevationProfileProps {
  /** Trackpoints to render in elevation profile */
  trackPoints: TrackPoint[];

  /** Callback when chart point is clicked */
  onPointClick?: (point: TrackPoint) => void;

  /** Chart height in pixels (default: 300) */
  height?: number;
}

/**
 * Props for GPXStats component
 *
 * Used in:
 * - TripDetailPage (display route statistics)
 */
export interface GPXStatsProps {
  /** GPX file metadata to display */
  metadata: GPXFileMetadata;

  /** GPX file ID (required for download functionality) */
  gpxFileId?: string;

  /** Whether current user is trip owner (enables download and delete buttons) */
  isOwner?: boolean;

  /** Callback when GPX file is deleted (owner-only action) */
  onDelete?: () => void;
}

// ============================================================================
// Upload State (Client-Only)
// ============================================================================

/**
 * GPX upload state for useGPXUpload hook
 *
 * Tracks upload progress and processing status.
 *
 * Used in:
 * - GPXUploader component
 * - useGPXUpload hook
 */
export interface GPXUploadState {
  /** Whether upload is in progress */
  isUploading: boolean;

  /** Whether processing is in progress (for async uploads) */
  isProcessing: boolean;

  /** Upload progress percentage (0-100) */
  uploadProgress: number;

  /** Current processing status */
  processingStatus: GPXProcessingStatus | null;

  /** Uploaded GPX file ID (null until upload completes) */
  gpxFileId: string | null;

  /** Error message (null if no error) */
  error: string | null;
}
