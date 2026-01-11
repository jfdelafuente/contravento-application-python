/**
 * TripMap Component
 *
 * Interactive map showing trip locations using react-leaflet and OpenStreetMap.
 * Lazy-loaded for performance optimization.
 *
 * Used in:
 * - TripDetailPage (location section, conditionally rendered)
 */

import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { TripLocation } from '../../types/trip';
import { createNumberedMarkerIcon } from '../../utils/mapHelpers';
import './TripMap.css';

interface TripMapProps {
  /** Array of trip locations */
  locations: TripLocation[];

  /** Trip title (for context) */
  tripTitle: string;
}

export const TripMap: React.FC<TripMapProps> = ({ locations, tripTitle }) => {
  // Filter locations that have coordinates
  const validLocations = useMemo(
    () => locations.filter((loc) => loc.latitude !== null && loc.longitude !== null),
    [locations]
  );

  // Calculate map center (average of all coordinates)
  const center: LatLngExpression = useMemo(() => {
    if (validLocations.length === 0) {
      // Default to Spain center if no valid locations
      return [40.4168, -3.7038]; // Madrid
    }

    if (validLocations.length === 1) {
      return [validLocations[0].latitude!, validLocations[0].longitude!];
    }

    const avgLat =
      validLocations.reduce((sum, loc) => sum + loc.latitude!, 0) / validLocations.length;
    const avgLng =
      validLocations.reduce((sum, loc) => sum + loc.longitude!, 0) / validLocations.length;

    return [avgLat, avgLng];
  }, [validLocations]);

  // Calculate zoom level based on location spread
  const zoom = useMemo(() => {
    if (validLocations.length === 0) return 6; // Spain overview
    if (validLocations.length === 1) return 12; // City level

    // Calculate bounding box
    const lats = validLocations.map((loc) => loc.latitude!);
    const lngs = validLocations.map((loc) => loc.longitude!);

    const latDiff = Math.max(...lats) - Math.min(...lats);
    const lngDiff = Math.max(...lngs) - Math.min(...lngs);
    const maxDiff = Math.max(latDiff, lngDiff);

    // Simple zoom calculation (adjust as needed)
    if (maxDiff > 10) return 5; // Country level
    if (maxDiff > 5) return 6; // Region level
    if (maxDiff > 2) return 7; // Multi-city
    if (maxDiff > 1) return 8; // City area
    if (maxDiff > 0.5) return 9; // City
    if (maxDiff > 0.1) return 11; // District
    return 12; // Neighborhood
  }, [validLocations]);

  // Create polyline for route (connects locations in sequence order)
  const routePath: LatLngExpression[] = useMemo(
    () =>
      validLocations
        .sort((a, b) => a.sequence - b.sequence)
        .map((loc) => [loc.latitude!, loc.longitude!]),
    [validLocations]
  );

  // Empty state
  if (validLocations.length === 0) {
    return (
      <div className="trip-map trip-map--empty">
        <div className="trip-map__empty-icon">
          <svg
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
            />
          </svg>
        </div>
        <p className="trip-map__empty-text">No hay ubicaciones en este viaje</p>
      </div>
    );
  }

  return (
    <div className="trip-map">
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        className="trip-map__container"
      >
        {/* OpenStreetMap Tiles */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Route Polyline (if multiple locations) */}
        {routePath.length > 1 && (
          <Polyline
            positions={routePath}
            pathOptions={{
              color: '#2563eb',
              weight: 3,
              opacity: 0.7,
              dashArray: '10, 10',
            }}
          />
        )}

        {/* Location Markers with Numbered Icons */}
        {validLocations
          .sort((a, b) => a.sequence - b.sequence)
          .map((location, index) => (
            <Marker
              key={location.location_id}
              position={[location.latitude!, location.longitude!]}
              icon={createNumberedMarkerIcon(index + 1)}
            >
              <Popup>
                <div className="trip-map__popup">
                  <strong className="trip-map__popup-title">
                    {index + 1}. {location.name}
                  </strong>
                  <p className="trip-map__popup-subtitle">{tripTitle}</p>
                </div>
              </Popup>
            </Marker>
          ))}
      </MapContainer>

      {/* Location List */}
      <div className="trip-map__locations">
        <h4 className="trip-map__locations-title">Ubicaciones ({validLocations.length})</h4>
        <ul className="trip-map__locations-list">
          {validLocations
            .sort((a, b) => a.sequence - b.sequence)
            .map((location, index) => (
              <li key={location.location_id} className="trip-map__location-item">
                <span className="trip-map__location-number">{index + 1}</span>
                <span className="trip-map__location-name">{location.name}</span>
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
};
