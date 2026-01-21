/**
 * GPXStats Component
 *
 * Feature 003 - GPS Routes Interactive
 * Displays route statistics in a card-based grid layout.
 *
 * Functional Requirements: FR-003 (Display Route Statistics)
 * Success Criteria: SC-005 (>90% elevation accuracy)
 */

import React from 'react';
import { GPXStatsProps } from '../../types/gpx';
import './GPXStats.css';

/**
 * GPXStats component - Display route statistics in card grid
 *
 * Displays:
 * - Distance (km)
 * - Elevation Gain (meters, if available)
 * - Elevation Loss (meters, if available)
 * - Max/Min Altitude (meters, if available)
 *
 * Design pattern: Similar to StatsCard from dashboard
 */
export const GPXStats: React.FC<GPXStatsProps> = ({ metadata }) => {
  const {
    distance_km,
    elevation_gain,
    elevation_loss,
    max_elevation,
    min_elevation,
    has_elevation,
  } = metadata;

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
    </div>
  );
};
