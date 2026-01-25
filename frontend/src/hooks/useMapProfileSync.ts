/**
 * useMapProfileSync Hook
 * Feature 003 - User Story 3: Interactive Elevation Profile
 *
 * Synchronizes map interactions with elevation profile:
 * - Click on profile point → centers map on that location
 * - Maintains map reference for programmatic control
 * - Handles smooth pan animations
 *
 * Usage:
 * ```tsx
 * const { mapRef, handleProfilePointClick } = useMapProfileSync();
 *
 * <TripMap ref={mapRef} ... />
 * <ElevationProfile onPointClick={handleProfilePointClick} ... />
 * ```
 */

import { useRef, useCallback } from 'react';
import type { Map as LeafletMap } from 'leaflet';
import type { TrackPoint } from '../components/trips/ElevationProfile';

interface UseMapProfileSyncReturn {
  /**
   * Reference to the Leaflet map instance
   * Pass this to TripMap component as ref
   */
  mapRef: React.MutableRefObject<LeafletMap | null>;

  /**
   * Callback to handle clicks on elevation profile points
   * Pass this to ElevationProfile component as onPointClick
   */
  handleProfilePointClick: (point: TrackPoint) => void;
}

/**
 * Hook to synchronize elevation profile clicks with map panning
 *
 * @returns Object with mapRef and handleProfilePointClick
 *
 * @example
 * ```tsx
 * const { mapRef, handleProfilePointClick } = useMapProfileSync();
 *
 * return (
 *   <>
 *     <TripMap
 *       ref={mapRef}
 *       locations={trip.locations}
 *       gpxRoute={trip.gpx_data?.simplified_track}
 *     />
 *     <ElevationProfile
 *       trackpoints={trip.gpx_data?.simplified_track || []}
 *       onPointClick={handleProfilePointClick}
 *     />
 *   </>
 * );
 * ```
 */
export const useMapProfileSync = (): UseMapProfileSyncReturn => {
  // Store reference to Leaflet map instance
  const mapRef = useRef<LeafletMap | null>(null);

  /**
   * Handle click on elevation profile point
   * Centers the map on the clicked point with smooth animation
   *
   * @param point - TrackPoint from elevation profile
   */
  const handleProfilePointClick = useCallback((point: TrackPoint) => {
    if (!mapRef.current) {
      return;
    }

    const { latitude, longitude } = point;

    // Validate coordinates
    if (
      typeof latitude !== 'number' ||
      typeof longitude !== 'number' ||
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      return;
    }

    try {
      // Pan to clicked point with smooth animation
      // zoom: 15 provides good detail for route context
      // duration: 0.5s for smooth but not too slow transition
      mapRef.current.flyTo([latitude, longitude], 15, {
        duration: 0.5,
        easeLinearity: 0.25,
      });
    } catch (error) {
      console.error('[useMapProfileSync] Error panning map:', error);
    }
  }, []);

  return {
    mapRef,
    handleProfilePointClick,
  };
};
