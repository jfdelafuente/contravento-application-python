/**
 * POIMarker Component
 *
 * Displays a Point of Interest marker on the map with distinctive icon by type.
 * Feature 003 - User Story 4: Points of Interest along routes.
 */

import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import { Icon, LatLngExpression } from 'leaflet';
import { POI, POI_TYPE_LABELS, POI_TYPE_COLORS, POI_TYPE_EMOJI } from '../../types/poi';
import { lightenColor, darkenColor } from '../../utils/colorUtils';
import { getPhotoUrl } from '../../utils/tripHelpers';
import './POIMarker.css';

interface POIMarkerProps {
  /** POI data */
  poi: POI;

  /** Whether the user is the trip owner (enables edit/delete) */
  isOwner?: boolean;

  /** Callback when user clicks "Edit" */
  onEdit?: (poi: POI) => void;

  /** Callback when user clicks "Delete" */
  onDelete?: (poiId: string) => void;
}

/**
 * Create a custom Leaflet icon with Font Awesome for POI markers
 *
 * Uses divIcon to render Font Awesome icons with custom colors.
 */
function createPOIIcon(poi: POI): Icon {
  const color = POI_TYPE_COLORS[poi.poi_type];

  // Use Leaflet's divIcon to create HTML-based icon
  return new Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 36" width="24" height="36">
        <path fill="${color}" stroke="#fff" stroke-width="1.5" d="M12 0C5.4 0 0 5.4 0 12c0 9 12 24 12 24s12-15 12-24c0-6.6-5.4-12-12-12z"/>
        <circle cx="12" cy="12" r="6" fill="#fff"/>
      </svg>
    `)}`,
    iconSize: [24, 36],
    iconAnchor: [12, 36],
    popupAnchor: [0, -36],
  });
}

export const POIMarker: React.FC<POIMarkerProps> = ({
  poi,
  isOwner = false,
  onEdit,
  onDelete,
}) => {
  const position: LatLngExpression = [poi.latitude, poi.longitude];
  const icon = createPOIIcon(poi);

  // Generate gradient colors from base POI type color
  const baseColor = POI_TYPE_COLORS[poi.poi_type];
  const lightColor = lightenColor(baseColor, 20);
  const darkColor = darkenColor(baseColor, 20);

  const handleEdit = () => {
    if (onEdit) {
      onEdit(poi);
    }
  };

  const handleDelete = () => {
    if (onDelete && window.confirm(`¿Eliminar "${poi.name}"?`)) {
      onDelete(poi.poi_id);
    }
  };

  return (
    <Marker position={position} icon={icon}>
      <Popup>
        <div className="poi-popup">
          {/* POI Type Badge */}
          <div className="poi-popup-header">
            <span
              className="poi-type-badge"
              style={{
                background: `linear-gradient(135deg, ${lightColor} 0%, ${baseColor} 50%, ${darkColor} 100%)`,
                boxShadow: `0 2px 4px rgba(0, 0, 0, 0.15), inset 0 1px 1px rgba(255, 255, 255, 0.2)`,
              }}
            >
              <span className="poi-badge-icon">{POI_TYPE_EMOJI[poi.poi_type]}</span>
              {POI_TYPE_LABELS[poi.poi_type]}
            </span>
          </div>

          {/* POI Name */}
          <h3 className="poi-popup-title">{poi.name}</h3>

          {/* POI Photo (FR-010) */}
          {poi.photo_url && (
            <div className="poi-popup-photo">
              <img
                src={getPhotoUrl(poi.photo_url)}
                alt={poi.name}
                className="poi-popup-photo-image"
              />
            </div>
          )}

          {/* POI Description */}
          {poi.description && (
            <p className="poi-popup-description">{poi.description}</p>
          )}

          {/* Distance from start (if available) */}
          {poi.distance_from_start_km !== null && (
            <p className="poi-popup-distance">
              📍 {poi.distance_from_start_km.toFixed(1)} km desde el inicio
            </p>
          )}

          {/* Owner Actions */}
          {isOwner && (
            <div className="poi-popup-actions">
              <button
                onClick={handleEdit}
                className="poi-popup-button poi-popup-button-edit"
              >
                ✏️ Editar
              </button>
              <button
                onClick={handleDelete}
                className="poi-popup-button poi-popup-button-delete"
              >
                🗑️ Eliminar
              </button>
            </div>
          )}
        </div>
      </Popup>
    </Marker>
  );
};
