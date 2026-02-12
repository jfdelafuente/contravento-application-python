/**
 * MapClickHandler component for capturing map click events
 * Feature: 010-reverse-geocoding
 * Task: T015
 *
 * This component uses react-leaflet's useMapEvents hook to listen for
 * map click events and trigger the onMapClick callback with coordinates.
 */

import { useMapEvents } from 'react-leaflet';
import type { LeafletMouseEvent } from 'leaflet';

interface MapClickHandlerProps {
  /**
   * Callback fired when user clicks on the map
   * @param lat - Latitude of clicked location
   * @param lng - Longitude of clicked location
   */
  onMapClick: (lat: number, lng: number) => void;
  /**
   * Whether map clicks should be handled
   * If false, clicks are ignored
   */
  enabled: boolean;
}

/**
 * Component that handles map click events in react-leaflet
 *
 * Usage:
 * ```tsx
 * <MapContainer>
 *   <MapClickHandler
 *     enabled={isEditMode}
 *     onMapClick={(lat, lng) => handleMapClick(lat, lng)}
 *   />
 * </MapContainer>
 * ```
 *
 * Note: This component does not render any visible elements.
 * It only registers event handlers with the Leaflet map.
 */
export const MapClickHandler: React.FC<MapClickHandlerProps> = ({
  onMapClick,
  enabled,
}) => {
  useMapEvents({
    click: (e: LeafletMouseEvent) => {
      if (enabled) {
        const { lat, lng } = e.latlng;
        onMapClick(lat, lng);
      }
    },
  });

  // This component doesn't render anything
  return null;
};
