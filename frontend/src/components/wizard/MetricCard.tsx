/**
 * MetricCard Component
 *
 * Displays a single metric with label and value.
 * Used within MetricGroup to show telemetry data.
 *
 * Feature: 017-gps-trip-wizard (Phase 1 Optimization)
 * Task: T003
 */

import React, { ReactNode } from 'react';
import './MetricCard.css';

export interface MetricCardProps {
  /** Metric label (e.g., "Distancia Total") */
  label: string;

  /** Metric value (e.g., "42.5 km") */
  value: string | number;

  /** Optional icon */
  icon?: ReactNode;

  /** Size variant */
  size?: 'small' | 'medium' | 'large';

  /** Color variant */
  variant?: 'default' | 'primary' | 'success' | 'warning';
}

/**
 * MetricCard - Individual metric display card
 *
 * @example
 * ```tsx
 * <MetricCard
 *   label="Distancia Total"
 *   value="42.5 km"
 *   icon={<ArrowRightIcon />}
 *   size="medium"
 * />
 * ```
 */
export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  icon,
  size = 'medium',
  variant = 'default',
}) => {
  return (
    <div className={`metric-card metric-card--${size} metric-card--${variant}`}>
      {icon && <span className="metric-card__icon">{icon}</span>}
      <div className="metric-card__content">
        <span className="metric-card__label">{label}</span>
        <span className="metric-card__value">{value}</span>
      </div>
    </div>
  );
};
