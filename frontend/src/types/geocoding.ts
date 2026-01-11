/**
 * Geocoding types for reverse geocoding functionality
 * Feature: 010-reverse-geocoding
 */

/**
 * Nominatim address components from OpenStreetMap API
 * All fields are optional as Nominatim returns different fields based on location type
 */
export interface NominatimAddress {
  /** Park, garden, playground */
  leisure?: string;
  /** Restaurant, cafe, hospital, school */
  amenity?: string;
  /** Store, supermarket, mall */
  shop?: string;
  /** Museum, hotel, monument, attraction */
  tourism?: string;
  /** Street name */
  road?: string;
  /** Neighborhood name */
  suburb?: string;
  /** City name */
  city?: string;
  /** Town name (mutually exclusive with city/village) */
  town?: string;
  /** Village name (mutually exclusive with city/town) */
  village?: string;
  /** State/region/province */
  state?: string;
  /** Country name (localized) */
  country?: string;
  /** ISO 3166-1 alpha-2 country code (e.g., 'es') */
  country_code?: string;
  /** Postal code */
  postcode?: string;
}

/**
 * Response from Nominatim reverse geocoding API
 */
export interface GeocodingResponse {
  /** Unique identifier for this place in OSM database */
  place_id: number;
  /** OSM license information */
  licence: string;
  /** OSM object type (node, way, relation) */
  osm_type: string;
  /** OSM object ID */
  osm_id: number;
  /** Latitude (may differ slightly from query) */
  lat: string;
  /** Longitude (may differ slightly from query) */
  lon: string;
  /** Full address as comma-separated string */
  display_name: string;
  /** Structured address components */
  address: NominatimAddress;
  /** Geographic bounds [min_lat, max_lat, min_lon, max_lon] */
  boundingbox: [string, string, string, string];
}

/**
 * Error response from Nominatim API
 */
export interface GeocodingError {
  /** Error message */
  error: string;
}

/**
 * Location selection state for map interactions
 * Used during trip creation/editing when user clicks map or drags marker
 */
export interface LocationSelection {
  /** Latitude in decimal degrees (-90 to 90) */
  latitude: number;
  /** Longitude in decimal degrees (-180 to 180) */
  longitude: number;
  /** Suggested place name from reverse geocoding */
  suggestedName: string;
  /** Full address from reverse geocoding (display_name) */
  fullAddress: string;
  /** User-edited name (overrides suggestedName if provided) */
  editedName?: string;
  /** Loading state during API call */
  isLoading: boolean;
  /** Error state if geocoding fails */
  hasError: boolean;
  /** Error message to display to user (in Spanish) */
  errorMessage?: string;
  /** Location ID when updating existing location via drag (Feature 010 - User Story 2) */
  locationId?: string;
}
