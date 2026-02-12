/**
 * Map Helper Utilities
 *
 * Utility functions for working with Leaflet maps and markers.
 *
 * Features:
 * - Custom numbered marker icon generation
 * - ContraVento branding consistency
 * - Accessibility support (aria-labels)
 */

import { DivIcon } from 'leaflet';

/**
 * Create a custom numbered marker icon for Leaflet maps
 *
 * Generates a DivIcon with a numbered badge styled with ContraVento colors.
 * The marker displays the location sequence number (1, 2, 3...) for better
 * route visualization.
 *
 * @param number - The location sequence number (1-based index)
 * @returns Leaflet DivIcon with numbered badge
 *
 * @example
 * ```tsx
 * const icon = createNumberedMarkerIcon(1);
 * <Marker position={[lat, lng]} icon={icon} />
 * ```
 */
export function createNumberedMarkerIcon(number: number): DivIcon {
  return new DivIcon({
    className: 'custom-numbered-marker',
    html: `
      <div class="numbered-marker-wrapper">
        <div class="numbered-marker-badge" aria-label="Ubicación ${number}">
          ${number}
        </div>
        <div class="numbered-marker-pin"></div>
      </div>
    `,
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -42],
  });
}

/**
 * Get ContraVento primary color for markers
 * @returns CSS color value
 */
export function getMarkerColor(): string {
  return '#2563eb'; // ContraVento primary blue
}

/**
 * Get marker shadow color
 * @returns CSS color value
 */
export function getMarkerShadowColor(): string {
  return 'rgba(0, 0, 0, 0.2)';
}
