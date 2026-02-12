/**
 * MapPreview Component - Static Map Preview for GPX Route
 *
 * Displays a non-interactive map preview of the GPX route in Wizard Step 1.
 * Uses Leaflet.js with all interactions disabled for performance.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 2 (Option C)
 * Task: T2
 *
 * @example
 * ```typescript
 * <MapPreview
 *   trackpoints={telemetry.trackpoints}
 *   title="Ruta Pirineos"
 * />
 * ```
 */

import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapPreview.css';

/**
 * Props for MapPreview component
 */
export interface MapPreviewProps {
  /** Array of trackpoints for route visualization */
  trackpoints: Array<{
    latitude: number;
    longitude: number;
    elevation?: number | null;
    distance_km?: number;
  }>;

  /** Route title for accessibility */
  title: string;
}

/**
 * MapPreview Component
 *
 * Renders a static (non-interactive) map preview of the GPX route.
 * All user interactions are disabled for simplicity.
 *
 * @param props - Component props
 */
export const MapPreview: React.FC<MapPreviewProps> = ({ trackpoints, title }) => {
  const mapRef = useRef<L.Map | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || trackpoints.length === 0) return;

    // Initialize map (only once)
    if (!mapRef.current) {
      const map = L.map(containerRef.current, {
        // Disable all interactions
        dragging: false,
        touchZoom: false,
        doubleClickZoom: false,
        scrollWheelZoom: false,
        boxZoom: false,
        keyboard: false,
        zoomControl: false,
        attributionControl: true,
      });

      // Add OpenStreetMap tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      mapRef.current = map;
    }

    // Clear previous route layers
    mapRef.current.eachLayer((layer) => {
      if (layer instanceof L.Polyline) {
        mapRef.current!.removeLayer(layer);
      }
    });

    // Convert trackpoints to LatLng array
    const latLngs: L.LatLngExpression[] = trackpoints.map((point) => [
      point.latitude,
      point.longitude,
    ]);

    // Draw route polyline
    const routeLine = L.polyline(latLngs, {
      color: '#d35400',
      weight: 3,
      opacity: 0.8,
    }).addTo(mapRef.current);

    // Fit map bounds to route
    mapRef.current.fitBounds(routeLine.getBounds(), {
      padding: [20, 20],
    });

    // Cleanup on unmount
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [trackpoints]);

  return (
    <div className="map-preview">
      <div className="map-preview__header">
        <h3 className="map-preview__title">Vista Previa de la Ruta</h3>
        <p className="map-preview__hint">
          Mapa interactivo disponible en el Paso 3 (Puntos de Interés)
        </p>
      </div>

      <div
        ref={containerRef}
        className="map-preview__container"
        role="img"
        aria-label={`Mapa de la ruta: ${title}`}
      />
    </div>
  );
};
