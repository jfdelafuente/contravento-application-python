/**
 * GPX Trip Creation Wizard Type Definitions
 *
 * Feature: 017-gps-trip-wizard
 * Type definitions for the GPS Trip Creation Wizard feature.
 * Based on backend API contracts: specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml
 */

import { TripDifficulty } from './trip';

// ============================================================================
// GPX Analysis Response (POST /gpx/analyze)
// ============================================================================

/**
 * Simplified trackpoint for map visualization in wizard.
 *
 * Used in:
 * - Step3POIs (displaying GPX route on map)
 * - GPXTelemetry (trackpoints array)
 */
export interface TrackPointSimple {
  /** Latitude coordinate (-90 to 90) */
  latitude: number;

  /** Longitude coordinate (-180 to 180) */
  longitude: number;

  /** Elevation in meters (null if no elevation data) */
  elevation: number | null;

  /** Cumulative distance from start in kilometers */
  distance_km: number;
}

/**
 * Telemetry data extracted from GPX file for wizard preview.
 *
 * Returned by POST /gpx/analyze endpoint after quick GPX analysis.
 * Provides essential route metrics without saving to database.
 *
 * Used in:
 * - WizardStep1 (upload GPX and display telemetry preview)
 * - useGPXAnalysis hook (GPX file upload handler)
 *
 * Backend: src/schemas/gpx_wizard.py:GPXTelemetry
 */
export interface GPXTelemetry {
  /** Total route distance in kilometers (≥0) */
  distance_km: number;

  /** Cumulative uphill elevation in meters (null if no elevation data, ≥0) */
  elevation_gain: number | null;

  /** Cumulative downhill elevation in meters (null if no elevation data, ≥0) */
  elevation_loss: number | null;

  /** Maximum altitude in meters (null if no elevation data) */
  max_elevation: number | null;

  /** Minimum altitude in meters (null if no elevation data) */
  min_elevation: number | null;

  /** Whether GPX contains elevation data */
  has_elevation: boolean;

  /** Auto-calculated trip difficulty from distance and elevation */
  difficulty: TripDifficulty;

  /**
   * Simplified trackpoints for map visualization (null if not requested).
   *
   * Trackpoints are simplified using Douglas-Peucker algorithm (~200-500 points).
   * Used in wizard to display the GPX route on the map for POI placement.
   */
  trackpoints: TrackPointSimple[] | null;
}

/**
 * Response from POST /gpx/analyze endpoint.
 *
 * Standardized API response with success/data/error structure.
 *
 * Used in:
 * - useGPXAnalysis hook (parsing response)
 * - WizardStep1 (error handling)
 *
 * Backend: src/schemas/gpx_wizard.py:GPXAnalysisResponse
 */
export interface GPXAnalysisResponse {
  /** Whether the request was successful */
  success: boolean;

  /** Telemetry data if successful, null if failed */
  data: GPXTelemetry | null;

  /** Error details if failed, null if successful */
  error: {
    /** Error code (e.g., "INVALID_GPX_FILE", "FILE_TOO_LARGE") */
    code: string;

    /** User-friendly error message in Spanish */
    message: string;

    /** Field name that caused the error (e.g., "file") */
    field?: string;
  } | null;
}

// ============================================================================
// Trip Creation via Wizard (POST /trips/gpx-wizard)
// ============================================================================

/**
 * Point of Interest (POI) input for wizard submission.
 *
 * Max 6 POIs per trip (FR-010: MAX_POIS_PER_TRIP = 6).
 *
 * Used in:
 * - WizardStep2 (POI form inputs)
 * - GPXTripFormData (pois array)
 *
 * Backend: src/schemas/poi.py:POICreateInput (via multipart/form-data)
 */
export interface POIInput {
  /** POI name (1-200 characters, required) */
  name: string;

  /** POI description (max 500 characters, optional) */
  description?: string;

  /** POI category (e.g., "accommodation", "restaurant", "viewpoint") */
  category: string;

  /** Display order in POI list (0-based) */
  order: number;
}

/**
 * Form data for GPS Trip Creation Wizard submission.
 *
 * This represents the complete wizard form state across all steps.
 * Submitted as multipart/form-data to POST /trips/gpx-wizard.
 *
 * Used in:
 * - GPXWizard component (overall wizard state)
 * - WizardStep3 (final review & submit)
 * - useGPXWizard hook (form submission handler)
 *
 * Backend: src/schemas/gpx_wizard.py:GPXTripCreateInput + multipart file fields
 */
export interface GPXTripFormData {
  // ===== Trip Basic Info (Step 1) =====

  /** Trip title (1-200 characters, required) */
  title: string;

  /** Trip description (minimum 50 characters, required) */
  description: string;

  /** Trip start date (YYYY-MM-DD format, required) */
  start_date: string;

  /** Trip end date (YYYY-MM-DD format, optional) */
  end_date: string | null;

  /** Trip privacy setting (default: "public") */
  privacy: 'public' | 'private';

  // ===== GPX File (Step 1) =====

  /**
   * Uploaded GPX file (binary data, required).
   *
   * Constraints:
   * - Max file size: 10MB (FR-002)
   * - Allowed extensions: .gpx
   * - MIME type: application/gpx+xml
   */
  gpx_file: File;

  /**
   * Pre-analyzed telemetry from GPX file (optional, for UI display).
   *
   * Populated after POST /gpx/analyze in Step 1.
   * NOT sent to backend (backend re-analyzes the gpx_file).
   */
  telemetry?: GPXTelemetry;

  // ===== Points of Interest (Step 2) =====

  /**
   * Array of POIs to create with the trip (max 6, optional).
   *
   * Submitted as JSON string in multipart/form-data:
   * - Form field name: "pois"
   * - Format: JSON.stringify(pois)
   *
   * Backend parses this JSON string to list[POICreateInput].
   */
  pois: POIInput[];
}

// ============================================================================
// Wizard UI State (Client-Only)
// ============================================================================

/**
 * Wizard step indicator.
 *
 * Used in:
 * - GPXWizard component (step navigation)
 * - WizardStepIndicator component (progress bar)
 */
export type WizardStep = 1 | 2 | 3;

/**
 * Wizard navigation actions.
 *
 * Used in:
 * - GPXWizard component (navigation handlers)
 * - useWizardNavigation hook
 */
export interface WizardNavigation {
  /** Current wizard step (1-3) */
  currentStep: WizardStep;

  /** Navigate to next step (disabled on last step) */
  goNext: () => void;

  /** Navigate to previous step (disabled on first step) */
  goPrevious: () => void;

  /** Jump to specific step */
  goToStep: (step: WizardStep) => void;

  /** Whether current step can proceed to next (validation passed) */
  canProceed: boolean;
}

/**
 * Wizard submission state.
 *
 * Used in:
 * - GPXWizard component (submit handler)
 * - WizardStep3 (submit button state)
 */
export interface WizardSubmitState {
  /** Whether wizard is currently submitting */
  isSubmitting: boolean;

  /** Submission error message (Spanish) */
  error: string | null;

  /** Submission progress (0-100, for large file uploads) */
  progress: number;
}
