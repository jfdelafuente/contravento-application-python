/**
 * TelemetrySkeleton Component - Loading Skeleton for Telemetry Data
 *
 * Displays placeholder skeleton while telemetry data is being analyzed.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 9 (Polish)
 * Task: T098
 */

import React from 'react';
import './TelemetrySkeleton.css';

/**
 * Telemetry Loading Skeleton
 *
 * Skeleton placeholder for telemetry preview in Step 1.
 * Shows shimmer animation while GPX file is being analyzed.
 */
export const TelemetrySkeleton: React.FC = () => {
  return (
    <div className="telemetry-skeleton" aria-busy="true" aria-label="Analizando datos GPS">
      <div className="telemetry-skeleton__header">
        <div className="telemetry-skeleton__title skeleton-shimmer" />
      </div>

      <div className="telemetry-skeleton__content">
        {/* Distance */}
        <div className="telemetry-skeleton__item">
          <div className="telemetry-skeleton__label skeleton-shimmer" />
          <div className="telemetry-skeleton__value skeleton-shimmer" />
        </div>

        {/* Elevation Gain */}
        <div className="telemetry-skeleton__item">
          <div className="telemetry-skeleton__label skeleton-shimmer" />
          <div className="telemetry-skeleton__value skeleton-shimmer" />
        </div>

        {/* Difficulty */}
        <div className="telemetry-skeleton__item">
          <div className="telemetry-skeleton__label skeleton-shimmer" />
          <div className="telemetry-skeleton__badge skeleton-shimmer" />
        </div>
      </div>

      <div className="telemetry-skeleton__footer">
        <div className="telemetry-skeleton__text skeleton-shimmer" />
      </div>

      {/* Screen reader announcement */}
      <div className="sr-only" role="status" aria-live="polite">
        Analizando archivo GPX...
      </div>
    </div>
  );
};
