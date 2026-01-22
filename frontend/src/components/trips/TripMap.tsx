/**
 * TripMap Component
 *
 * Interactive map showing trip locations using react-leaflet and OpenStreetMap.
 * Lazy-loaded for performance optimization.
 *
 * Used in:
 * - TripDetailPage (location section, conditionally rendered)
 */

import React, { useMemo, useState, useCallback, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMapEvents, useMap } from 'react-leaflet';
import { LatLngExpression, Icon, LatLngBounds } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { TripLocation } from '../../types/trip';
import { TrackPoint, Coordinate } from '../../types/gpx';
import { createNumberedMarkerIcon } from '../../utils/mapHelpers';
import { MapClickHandler } from './MapClickHandler';
import './TripMap.css';

interface TripMapProps {
  /** Array of trip locations */
  locations: TripLocation[];

  /** Trip title (for context) */
  tripTitle: string;

  /** Edit mode - enables map click to add locations (Feature 010) */
  isEditMode?: boolean;

  /** Callback when user clicks on map in edit mode (Feature 010 - User Story 1) */
  onMapClick?: (lat: number, lng: number) => void;

  /** Callback when user drags a marker in edit mode (Feature 010 - User Story 2) */
  onMarkerDrag?: (locationId: string, newLat: number, newLng: number) => void;

  /** GPX trackpoints for route visualization (Feature 003 - User Story 2) */
  gpxTrackPoints?: TrackPoint[];

  /** GPX route start point (Feature 003 - User Story 2) */
  gpxStartPoint?: Coordinate;

  /** GPX route end point (Feature 003 - User Story 2) */
  gpxEndPoint?: Coordinate;
}

// Custom icons for GPX route start/end markers
const START_MARKER_ICON = new Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const END_MARKER_ICON = new Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

/**
 * TileError Component
 * Listens for tile loading errors and notifies parent component
 */
interface TileErrorListenerProps {
  onError: () => void;
}

const TileErrorListener: React.FC<TileErrorListenerProps> = ({ onError }) => {
  useMapEvents({
    tileerror: () => {
      onError();
    },
  });
  return null;
};

/**
 * AutoFitBounds Component
 * Automatically adjusts map bounds to fit GPX route
 */
interface AutoFitBoundsProps {
  bounds: LatLngBounds | null;
}

const AutoFitBounds: React.FC<AutoFitBoundsProps> = ({ bounds }) => {
  const map = useMap();

  useEffect(() => {
    if (bounds && bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bounds, map]);

  return null;
};

export const TripMap: React.FC<TripMapProps> = ({
  locations,
  tripTitle,
  isEditMode = false,
  onMapClick,
  onMarkerDrag,
  gpxTrackPoints,
  gpxStartPoint,
  gpxEndPoint,
}) => {
  // Error state for map tile loading failures
  const [hasMapError, setHasMapError] = useState(false);
  const [mapKey, setMapKey] = useState(0); // Key for re-mounting MapContainer on retry

  // Fullscreen state
  const [isFullscreen, setIsFullscreen] = useState(false);
  const mapContainerRef = useRef<HTMLDivElement>(null);

  // Filter locations that have coordinates
  const validLocations = useMemo(
    () => locations.filter((loc) => loc.latitude !== null && loc.longitude !== null),
    [locations]
  );

  // Handle tile loading errors
  const handleTileError = useCallback(() => {
    setHasMapError(true);
  }, []);

  // Retry map loading by re-mounting the MapContainer
  const handleRetry = useCallback(() => {
    setHasMapError(false);
    setMapKey((prev) => prev + 1); // Force re-mount with new key
  }, []);

  // Handle fullscreen change events
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Toggle fullscreen mode
  const toggleFullscreen = useCallback(async () => {
    if (!mapContainerRef.current) return;

    try {
      if (!document.fullscreenElement) {
        await mapContainerRef.current.requestFullscreen();
      } else {
        await document.exitFullscreen();
      }
    } catch (error) {
      console.error('Error toggling fullscreen:', error);
    }
  }, []);

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

  // Create polyline for GPX route (Feature 003 - User Story 2)
  const gpxRoutePath: LatLngExpression[] = useMemo(() => {
    if (!gpxTrackPoints || gpxTrackPoints.length === 0) return [];
    return gpxTrackPoints.map((point) => [point.latitude, point.longitude]);
  }, [gpxTrackPoints]);

  // Calculate bounds for GPX route (for auto-fit)
  const gpxBounds = useMemo(() => {
    if (gpxRoutePath.length === 0) return null;

    const lats = gpxRoutePath.map((point) => (point as [number, number])[0]);
    const lngs = gpxRoutePath.map((point) => (point as [number, number])[1]);

    const bounds = new LatLngBounds(
      [Math.min(...lats), Math.min(...lngs)],
      [Math.max(...lats), Math.max(...lngs)]
    );

    return bounds;
  }, [gpxRoutePath]);

  // No locations at all and NOT in edit mode - show empty state
  if (locations.length === 0 && !isEditMode) {
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
    <div
      ref={mapContainerRef}
      className={`trip-map ${isFullscreen ? 'trip-map--fullscreen' : ''}`}
    >
      {/* Error State UI */}
      {hasMapError && (
        <div className="trip-map__error">
          <div className="trip-map__error-icon">
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
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h3 className="trip-map__error-title">Error al cargar el mapa</h3>
          <p className="trip-map__error-message">
            No se pudieron cargar las imágenes del mapa. Verifica tu conexión a internet e intenta
            nuevamente.
          </p>
          <button
            type="button"
            className="trip-map__error-button"
            onClick={handleRetry}
          >
            Reintentar
          </button>
        </div>
      )}

      {/* Map Container - Show if there are valid GPS coordinates OR in edit mode */}
      {!hasMapError && (validLocations.length > 0 || isEditMode) && (
        <MapContainer
          key={mapKey}
          center={center}
          zoom={zoom}
          scrollWheelZoom={true}
          className="trip-map__container"
        >
          {/* Tile Error Listener */}
          <TileErrorListener onError={handleTileError} />

          {/* Auto-fit bounds for GPX route */}
          {gpxBounds && <AutoFitBounds bounds={gpxBounds} />}

          {/* Map Click Handler (Feature 010: Reverse Geocoding) */}
          {isEditMode && onMapClick && (
            <MapClickHandler enabled={isEditMode} onMapClick={onMapClick} />
          )}

          {/* OpenStreetMap Tiles */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

        {/* GPX Route Polyline (Feature 003 - User Story 2) */}
        {gpxRoutePath.length > 1 && (
          <Polyline
            positions={gpxRoutePath}
            pathOptions={{
              color: '#dc2626',
              weight: 3,
              opacity: 0.8,
            }}
          />
        )}

        {/* GPX Start Marker (green) */}
        {gpxStartPoint && (
          <Marker
            position={[gpxStartPoint.latitude, gpxStartPoint.longitude]}
            icon={START_MARKER_ICON}
          >
            <Popup>
              <div className="trip-map__popup">
                <strong className="trip-map__popup-title">Inicio de ruta</strong>
                <p className="trip-map__popup-subtitle">
                  {gpxStartPoint.latitude.toFixed(5)}, {gpxStartPoint.longitude.toFixed(5)}
                </p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* GPX End Marker (red) */}
        {gpxEndPoint && (
          <Marker
            position={[gpxEndPoint.latitude, gpxEndPoint.longitude]}
            icon={END_MARKER_ICON}
          >
            <Popup>
              <div className="trip-map__popup">
                <strong className="trip-map__popup-title">Fin de ruta</strong>
                <p className="trip-map__popup-subtitle">
                  {gpxEndPoint.latitude.toFixed(5)}, {gpxEndPoint.longitude.toFixed(5)}
                </p>
              </div>
            </Popup>
          </Marker>
        )}

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
              draggable={isEditMode && !!onMarkerDrag}
              eventHandlers={
                isEditMode && onMarkerDrag
                  ? {
                      dragend: (e: any) => {
                        const { lat, lng } = e.target.getLatLng();
                        onMarkerDrag(location.location_id, lat, lng);
                      },
                    }
                  : undefined
              }
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
      )}

      {/* Fullscreen Toggle Button - Only show if map is visible */}
      {!hasMapError && (validLocations.length > 0 || isEditMode) && (
        <button
          type="button"
          className="trip-map__fullscreen-button"
          onClick={toggleFullscreen}
          aria-label={isFullscreen ? 'Salir de pantalla completa' : 'Pantalla completa'}
          title={isFullscreen ? 'Salir de pantalla completa (Esc)' : 'Pantalla completa'}
        >
          {isFullscreen ? (
            // Exit fullscreen icon
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          ) : (
            // Enter fullscreen icon
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
                d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
              />
            </svg>
          )}
        </button>
      )}

      {/* Location List - Show ALL locations (with or without GPS) */}
      <div className="trip-map__locations">
        <h4 className="trip-map__locations-title">Ubicaciones ({locations.length})</h4>
        <ul className="trip-map__locations-list">
          {locations
            .sort((a, b) => a.sequence - b.sequence)
            .map((location, index) => (
              <li key={location.location_id} className="trip-map__location-item">
                <span className="trip-map__location-number">{index + 1}</span>
                <div className="trip-map__location-details">
                  <span className="trip-map__location-name">{location.name}</span>
                  {location.latitude === null || location.longitude === null ? (
                    <span className="trip-map__location-no-gps">Sin coordenadas GPS</span>
                  ) : null}
                </div>
              </li>
            ))}
        </ul>
      </div>
    </div>
  );
};
