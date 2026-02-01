/**
 * Point of Interest (POI) types for Feature 003 - User Story 4
 *
 * Defines types for marking locations of interest along trip routes.
 */

/**
 * POI type enumeration
 *
 * Types of points of interest that can be marked on routes.
 */
export enum POIType {
  VIEWPOINT = 'viewpoint',      // Mirador
  TOWN = 'town',                 // Pueblo
  WATER = 'water',               // Fuente de agua
  ACCOMMODATION = 'accommodation', // Alojamiento
  RESTAURANT = 'restaurant',     // Restaurante
  MOUNTAIN_PASS = 'mountain_pass', // Puerto de montaña
  OTHER = 'other',               // Otro
}

/**
 * POI display labels in Spanish
 */
export const POI_TYPE_LABELS: Record<POIType, string> = {
  [POIType.VIEWPOINT]: 'Mirador',
  [POIType.TOWN]: 'Pueblo',
  [POIType.WATER]: 'Fuente de agua',
  [POIType.ACCOMMODATION]: 'Alojamiento',
  [POIType.RESTAURANT]: 'Restaurante',
  [POIType.MOUNTAIN_PASS]: 'Puerto',
  [POIType.OTHER]: 'Otro',
};

/**
 * POI emoji icons for badge display
 *
 * Maps POI types to emoji icons for visual identification
 */
export const POI_TYPE_EMOJI: Record<POIType, string> = {
  [POIType.VIEWPOINT]: '🔭',      // Telescope for viewpoint
  [POIType.TOWN]: '🏘️',           // Town/village
  [POIType.WATER]: '💧',          // Water droplet
  [POIType.ACCOMMODATION]: '🏠',  // House/accommodation
  [POIType.RESTAURANT]: '🍽️',     // Fork and knife
  [POIType.MOUNTAIN_PASS]: '⛰️',  // Mountain for pass
  [POIType.OTHER]: '📍',          // Location pin
};

/**
 * POI Leaflet marker icon names
 *
 * Maps POI types to Font Awesome icon classes
 */
export const POI_TYPE_ICONS: Record<POIType, string> = {
  [POIType.VIEWPOINT]: 'fa-binoculars',
  [POIType.TOWN]: 'fa-house',
  [POIType.WATER]: 'fa-droplet',
  [POIType.ACCOMMODATION]: 'fa-bed',
  [POIType.RESTAURANT]: 'fa-utensils',
  [POIType.MOUNTAIN_PASS]: 'fa-mountain',
  [POIType.OTHER]: 'fa-location-dot',
};

/**
 * POI marker colors
 *
 * Maps POI types to marker colors for visual distinction
 */
export const POI_TYPE_COLORS: Record<POIType, string> = {
  [POIType.VIEWPOINT]: '#3b82f6',     // blue
  [POIType.TOWN]: '#8b5cf6',          // purple
  [POIType.WATER]: '#06b6d4',         // cyan
  [POIType.ACCOMMODATION]: '#f59e0b', // amber
  [POIType.RESTAURANT]: '#ef4444',    // red
  [POIType.MOUNTAIN_PASS]: '#10b981', // green
  [POIType.OTHER]: '#6b7280',         // gray
};

/**
 * Point of Interest response from API
 *
 * Represents a single POI with all its details.
 */
export interface POI {
  poi_id: string;
  trip_id: string;
  name: string;
  description: string | null;
  poi_type: POIType;
  latitude: number;
  longitude: number;
  distance_from_start_km: number | null;
  photo_url: string | null;
  sequence: number;
  created_at: string; // ISO 8601 timestamp
}

/**
 * Input for creating a new POI
 */
export interface POICreateInput {
  name: string;
  description?: string | null;
  poi_type: POIType;
  latitude: number;
  longitude: number;
  distance_from_start_km?: number | null;
  photo_url?: string | null;
  sequence: number;
  /** Photo file to upload (wizard only, not sent to backend directly) */
  photo?: File;
}

/**
 * Input for updating an existing POI
 *
 * All fields are optional - only provided fields will be updated.
 */
export interface POIUpdateInput {
  name?: string;
  description?: string | null;
  poi_type?: POIType;
  latitude?: number;
  longitude?: number;
  distance_from_start_km?: number | null;
  photo_url?: string | null;
  sequence?: number;
}

/**
 * Input for reordering POIs
 */
export interface POIReorderInput {
  poi_ids: string[];
}

/**
 * POI list response from API
 */
export interface POIListResponse {
  pois: POI[];
  total: number;
}

/**
 * POI form data (for React Hook Form)
 */
export interface POIFormData {
  name: string;
  description: string;
  poi_type: POIType;
  latitude: number;
  longitude: number;
  distance_from_start_km: number | null;
  photo_url: string | null;
}
