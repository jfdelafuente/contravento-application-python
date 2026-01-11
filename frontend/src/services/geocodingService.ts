/**
 * Geocoding service for reverse geocoding (coordinates → place names)
 * Feature: 010-reverse-geocoding
 *
 * Uses Nominatim OpenStreetMap API for reverse geocoding
 * API Docs: https://nominatim.org/release-docs/latest/api/Reverse/
 */

import axios, { AxiosError } from 'axios';
import type { GeocodingResponse, GeocodingError } from '../types/geocoding';

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org';
const USER_AGENT = 'ContraVento/1.0 (contact@contravento.com)';
const REQUEST_TIMEOUT_MS = 5000; // 5 seconds

/**
 * Reverse geocode coordinates to place name using Nominatim API
 *
 * API Endpoint: GET https://nominatim.openstreetmap.org/reverse
 * Query params: lat, lon, format=json, accept-language=es
 * Rate limit: 1 request/second (enforced by caller via debounce)
 *
 * @param lat Latitude in decimal degrees (-90 to 90)
 * @param lng Longitude in decimal degrees (-180 to 180)
 * @returns Promise<GeocodingResponse> with place name and address
 * @throws Error if API call fails or coordinates invalid
 *
 * Error scenarios:
 * - Invalid coordinates: Throws validation error (Spanish)
 * - Network timeout: Throws timeout error (Spanish)
 * - Rate limit (429): Throws rate limit error (Spanish)
 * - No result found: Throws geocoding error (Spanish)
 * - API error (500): Throws generic error (Spanish)
 *
 * Example:
 * ```typescript
 * const response = await reverseGeocode(40.416775, -3.703790);
 * // response.display_name: "Parque del Retiro, Retiro, Madrid, ..."
 * // response.address.leisure: "Parque del Retiro"
 * ```
 */
export async function reverseGeocode(
  lat: number,
  lng: number
): Promise<GeocodingResponse> {
  // Validate coordinates
  if (lat < -90 || lat > 90) {
    throw new Error('Latitud inválida: debe estar entre -90 y 90 grados');
  }
  if (lng < -180 || lng > 180) {
    throw new Error('Longitud inválida: debe estar entre -180 y 180 grados');
  }

  try {
    const response = await axios.get<GeocodingResponse | GeocodingError>(
      `${NOMINATIM_BASE_URL}/reverse`,
      {
        params: {
          lat,
          lon: lng,
          format: 'json',
          'accept-language': 'es', // Spanish place names
          addressdetails: 1, // Include address breakdown
          zoom: 18, // Maximum detail (building-level)
        },
        headers: {
          'User-Agent': USER_AGENT,
        },
        timeout: REQUEST_TIMEOUT_MS,
      }
    );

    // Check for error response (Nominatim returns 200 with error field)
    if ('error' in response.data) {
      throw new Error(
        `No se pudo obtener el nombre del lugar: ${response.data.error}`
      );
    }

    return response.data as GeocodingResponse;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;

      // Rate limit exceeded (429)
      if (axiosError.response?.status === 429) {
        throw new Error(
          'Demasiadas solicitudes. Por favor, espera un momento e intenta de nuevo.'
        );
      }

      // Network timeout
      if (axiosError.code === 'ECONNABORTED') {
        throw new Error(
          'El servidor de mapas no responde. Verifica tu conexión a internet.'
        );
      }

      // Generic network error
      throw new Error(
        'No se pudo conectar con el servicio de mapas. Intenta nuevamente.'
      );
    }

    // Unknown error (re-throw)
    throw error;
  }
}

/**
 * Extract most relevant place name from geocoding response
 *
 * Priority order (from most specific to least):
 * 1. leisure (park, garden) - "Parque del Retiro"
 * 2. amenity (restaurant, hospital) - "Hospital Gregorio Marañón"
 * 3. tourism (museum, monument) - "Museo del Prado"
 * 4. shop (store, supermarket) - "El Corte Inglés"
 * 5. road (street name) - "Calle de Alcalá"
 * 6. city/town/village (municipality) - "Madrid"
 * 7. display_name (full address, truncated) - "Parque del Retiro, Retiro..."
 * 8. fallback - "Ubicación sin nombre"
 *
 * @param response Geocoding API response
 * @returns Human-readable place name (Spanish)
 *
 * Examples:
 * - Park: "Parque del Retiro" (from address.leisure)
 * - Street: "Calle de Alcalá" (from address.road)
 * - City: "Madrid" (from address.city)
 * - Unknown: "Ubicación sin nombre" (fallback)
 */
export function extractLocationName(response: GeocodingResponse): string {
  const { address } = response;

  // Priority 1-6: Check address components (most specific first)
  const name =
    address.leisure ||
    address.amenity ||
    address.tourism ||
    address.shop ||
    address.road ||
    address.city ||
    address.town ||
    address.village;

  if (name) {
    return name;
  }

  // Priority 7: Use display_name (truncated if too long)
  if (response.display_name) {
    const maxLength = 50;
    return response.display_name.length > maxLength
      ? response.display_name.substring(0, maxLength) + '...'
      : response.display_name;
  }

  // Priority 8: Default fallback
  return 'Ubicación sin nombre';
}
