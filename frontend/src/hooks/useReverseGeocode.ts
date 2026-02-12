/**
 * Custom hook for reverse geocoding with caching and debouncing
 * Feature: 010-reverse-geocoding
 *
 * Provides geocoding functionality with:
 * - Automatic caching (LRU, 100 entries)
 * - Debouncing (1-second delay for rate limiting)
 * - Loading and error state management
 * - Spanish error messages
 */

import { useState, useCallback, useRef } from 'react';
import debounce from 'lodash.debounce';
import { reverseGeocode, extractLocationName } from '../services/geocodingService';
import { geocodingCache } from '../utils/geocodingCache';

/**
 * Result from reverse geocoding operation
 */
interface GeocodeResult {
  /** Extracted place name (e.g., "Parque del Retiro") */
  name: string;
  /** Full address string from API */
  fullAddress: string;
}

/**
 * Hook return value
 */
interface UseReverseGeocodeReturn {
  /**
   * Geocode coordinates immediately (no debounce)
   * Use for: Map clicks, marker drag end (user-initiated actions)
   *
   * @param lat Latitude in decimal degrees
   * @param lng Longitude in decimal degrees
   * @returns Promise with extracted name and full address
   * @throws Error with Spanish message on failure
   */
  geocode: (lat: number, lng: number) => Promise<GeocodeResult>;

  /**
   * Geocode coordinates with 1-second debounce
   * Use for: Marker dragging (continuous updates)
   *
   * @param lat Latitude in decimal degrees
   * @param lng Longitude in decimal degrees
   * @returns Promise with extracted name and full address (may be undefined if debounced)
   */
  debouncedGeocode: (lat: number, lng: number) => Promise<GeocodeResult> | undefined;

  /** True while API call is in progress */
  isLoading: boolean;

  /** Error message (Spanish) or null if no error */
  error: string | null;

  /** Clear error state */
  clearError: () => void;
}

/**
 * Custom hook for reverse geocoding
 *
 * Features:
 * - Cache-first strategy (instant response on cache hit)
 * - Debounced geocoding for continuous updates (e.g., marker drag)
 * - Immediate geocoding for user actions (e.g., map click)
 * - Automatic error handling with Spanish messages
 * - Loading state management
 *
 * Usage:
 * ```typescript
 * const { geocode, debouncedGeocode, isLoading, error } = useReverseGeocode();
 *
 * // On map click (immediate)
 * const handleMapClick = async (lat: number, lng: number) => {
 *   try {
 *     const { name, fullAddress } = await geocode(lat, lng);
 *     setLocationName(name);
 *   } catch (err) {
 *     // Error already in hook state
 *   }
 * };
 *
 * // On marker drag (debounced)
 * const handleMarkerDrag = async (lat: number, lng: number) => {
 *   const { name } = await debouncedGeocode(lat, lng);
 *   setLocationName(name);
 * };
 * ```
 *
 * @returns Geocoding functions and state
 */
export function useReverseGeocode(): UseReverseGeocodeReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Core geocoding function with cache-first strategy
   */
  const geocode = useCallback(
    async (lat: number, lng: number): Promise<GeocodeResult> => {
      setIsLoading(true);
      setError(null);

      try {
        // Check cache first (instant response)
        const cached = geocodingCache.get(lat, lng);
        if (cached) {
          setIsLoading(false);
          return {
            name: extractLocationName(cached),
            fullAddress: cached.display_name,
          };
        }

        // Cache miss - call API
        const response = await reverseGeocode(lat, lng);

        // Store in cache for future use
        geocodingCache.set(lat, lng, response);

        setIsLoading(false);

        return {
          name: extractLocationName(response),
          fullAddress: response.display_name,
        };
      } catch (err: any) {
        const errorMessage =
          err.message || 'Error al obtener el nombre del lugar';
        setError(errorMessage);
        setIsLoading(false);
        throw err; // Re-throw so caller can handle
      }
    },
    []
  );

  /**
   * Debounced geocoding for continuous updates
   * 1-second delay to respect Nominatim rate limit (1 req/sec)
   */
  const debouncedGeocode = useRef(
    debounce(
      async (lat: number, lng: number): Promise<GeocodeResult> => {
        return geocode(lat, lng);
      },
      1000, // 1-second delay
      {
        leading: false, // Don't call immediately
        trailing: true, // Call after delay
      }
    )
  ).current;

  /**
   * Clear error state manually
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    geocode,
    debouncedGeocode,
    isLoading,
    error,
    clearError,
  };
}
