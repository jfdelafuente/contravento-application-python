/**
 * GPXStats Component
 *
 * Feature 003 - GPS Routes Interactive
 * Displays route statistics in a card-based grid layout.
 *
 * Functional Requirements: FR-003 (Display Route Statistics), FR-039 (Download GPX)
 * Success Criteria: SC-005 (>90% elevation accuracy)
 */

import React, { useState } from 'react';
import { GPXStatsProps } from '../../types/gpx';
import { downloadGPX } from '../../services/gpxService';
import toast from 'react-hot-toast';
import './GPXStats.css';

/**
 * GPXStats component - Display route statistics in card grid
 *
 * Displays:
 * - Distance (km)
 * - Elevation Gain (meters, if available)
 * - Elevation Loss (meters, if available)
 * - Max/Min Altitude (meters, if available)
 * - Download button (owner-only)
 * - Delete button (owner-only)
 *
 * Design pattern: Similar to StatsCard from dashboard
 */
export const GPXStats: React.FC<GPXStatsProps> = ({
  metadata,
  gpxFileId,
  isOwner = false,
  onDelete,
}) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Safety check: metadata should always be provided by parent
  if (!metadata) {
    console.error('GPXStats: metadata is required');
    return null;
  }

  const {
    distance_km,
    elevation_gain,
    elevation_loss,
    max_elevation,
    min_elevation,
    has_elevation,
  } = metadata;

  /**
   * Handle GPX file download
   * FR-039: Owner can download original GPX file
   */
  const handleDownload = async () => {
    if (!gpxFileId) {
      toast.error('No se puede descargar: ID de archivo GPX no disponible');
      return;
    }

    try {
      await downloadGPX(gpxFileId);
      toast.success('Descargando archivo GPX original...');
    } catch (error: any) {
      console.error('Download error:', error);
      toast.error('Error al descargar archivo GPX');
    }
  };

  /**
   * Handle delete button click - show confirmation modal
   */
  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  /**
   * Handle delete confirmation
   */
  const handleConfirmDelete = () => {
    setShowDeleteConfirm(false);
    if (onDelete) {
      onDelete();
    }
  };

  /**
   * Handle delete cancellation
   */
  const handleCancelDelete = () => {
    setShowDeleteConfirm(false);
  };

  return (
    <div className="gpx-stats">
      <h3 className="gpx-stats__title">Estadísticas de la Ruta</h3>

      <div className="gpx-stats__grid">
        {/* Distance Card */}
        <div className="gpx-stat-card gpx-stat-card--distance">
          <div className="gpx-stat-card__icon-wrapper">
            <svg
              className="gpx-stat-card__icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </div>
          <div className="gpx-stat-card__content">
            <p className="gpx-stat-card__label">Distancia Total</p>
            <p className="gpx-stat-card__value">
              {distance_km.toFixed(2)} <span className="gpx-stat-card__unit">km</span>
            </p>
          </div>
        </div>

        {/* Elevation Gain Card */}
        {has_elevation && elevation_gain !== null && (
          <div className="gpx-stat-card gpx-stat-card--gain">
            <div className="gpx-stat-card__icon-wrapper">
              <svg
                className="gpx-stat-card__icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                <polyline points="17 6 23 6 23 12" />
              </svg>
            </div>
            <div className="gpx-stat-card__content">
              <p className="gpx-stat-card__label">Desnivel Positivo</p>
              <p className="gpx-stat-card__value">
                {elevation_gain.toFixed(0)} <span className="gpx-stat-card__unit">m</span>
              </p>
            </div>
          </div>
        )}

        {/* Elevation Loss Card */}
        {has_elevation && elevation_loss !== null && (
          <div className="gpx-stat-card gpx-stat-card--loss">
            <div className="gpx-stat-card__icon-wrapper">
              <svg
                className="gpx-stat-card__icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <polyline points="23 18 13.5 8.5 8.5 13.5 1 6" />
                <polyline points="17 18 23 18 23 12" />
              </svg>
            </div>
            <div className="gpx-stat-card__content">
              <p className="gpx-stat-card__label">Desnivel Negativo</p>
              <p className="gpx-stat-card__value">
                {elevation_loss.toFixed(0)} <span className="gpx-stat-card__unit">m</span>
              </p>
            </div>
          </div>
        )}

        {/* Max Elevation Card */}
        {has_elevation && max_elevation !== null && (
          <div className="gpx-stat-card gpx-stat-card--max">
            <div className="gpx-stat-card__icon-wrapper">
              <svg
                className="gpx-stat-card__icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <polyline points="4 15 12 3 20 15" />
                <line x1="4" y1="21" x2="20" y2="21" />
              </svg>
            </div>
            <div className="gpx-stat-card__content">
              <p className="gpx-stat-card__label">Altitud Máxima</p>
              <p className="gpx-stat-card__value">
                {max_elevation.toFixed(0)} <span className="gpx-stat-card__unit">m</span>
              </p>
            </div>
          </div>
        )}

        {/* Min Elevation Card */}
        {has_elevation && min_elevation !== null && (
          <div className="gpx-stat-card gpx-stat-card--min">
            <div className="gpx-stat-card__icon-wrapper">
              <svg
                className="gpx-stat-card__icon"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <polyline points="20 9 12 21 4 9" />
                <line x1="4" y1="3" x2="20" y2="3" />
              </svg>
            </div>
            <div className="gpx-stat-card__content">
              <p className="gpx-stat-card__label">Altitud Mínima</p>
              <p className="gpx-stat-card__value">
                {min_elevation.toFixed(0)} <span className="gpx-stat-card__unit">m</span>
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons (Owner-only) */}
      {isOwner && gpxFileId && (
        <div className="gpx-stats__actions">
          <button
            onClick={handleDownload}
            className="gpx-stats__download-btn"
            aria-label="Descargar archivo GPX original"
          >
            <svg
              className="gpx-stats__download-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            <span>Descargar GPX Original</span>
          </button>

          <button
            onClick={handleDeleteClick}
            className="gpx-stats__delete-btn"
            aria-label="Eliminar archivo GPX"
          >
            <svg
              className="gpx-stats__delete-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-hidden="true"
            >
              <polyline points="3 6 5 6 21 6" />
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              <line x1="10" y1="11" x2="10" y2="17" />
              <line x1="14" y1="11" x2="14" y2="17" />
            </svg>
            <span>Eliminar GPX</span>
          </button>
        </div>
      )}

      {/* No elevation data message */}
      {!has_elevation && (
        <div className="gpx-stats__no-elevation" role="status">
          <svg
            className="gpx-stats__no-elevation-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <p>Este archivo GPX no contiene datos de elevación.</p>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div
          className="gpx-delete-modal-overlay"
          onClick={handleCancelDelete}
          role="dialog"
          aria-modal="true"
          aria-labelledby="gpx-delete-title"
          aria-describedby="gpx-delete-description"
        >
          <div
            className="gpx-delete-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="gpx-delete-modal__icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                aria-hidden="true"
              >
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 id="gpx-delete-title" className="gpx-delete-modal__title">
              ¿Eliminar archivo GPX?
            </h3>
            <p id="gpx-delete-description" className="gpx-delete-modal__description">
              Esta acción eliminará permanentemente el archivo GPX y todos los datos asociados
              (ruta GPS, perfil de elevación, estadísticas). No se puede deshacer.
            </p>
            <div className="gpx-delete-modal__actions">
              <button
                onClick={handleCancelDelete}
                className="gpx-delete-modal__button gpx-delete-modal__button--cancel"
                aria-label="Cancelar eliminación"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmDelete}
                className="gpx-delete-modal__button gpx-delete-modal__button--confirm"
                aria-label="Confirmar eliminación del archivo GPX"
              >
                Eliminar GPX
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
