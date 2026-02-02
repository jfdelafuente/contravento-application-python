/**
 * MetricGroup Component
 *
 * Groups related metrics with optional collapsible behavior.
 * Used in Step1Upload to display telemetry data organized by category.
 *
 * Feature: 017-gps-trip-wizard (Phase 1 Optimization)
 * Task: T003
 */

import React, { ReactNode } from 'react';
import './MetricGroup.css';

export interface MetricGroupProps {
  /** Group title */
  title: string;

  /** Children (usually MetricCard components) */
  children: ReactNode;

  /** Optional icon before title */
  icon?: ReactNode;

  /** Whether to display in grid layout (default: true) */
  grid?: boolean;

  /** Custom className for styling */
  className?: string;
}

/**
 * MetricGroup - Container for grouping related metrics
 *
 * @example
 * ```tsx
 * <MetricGroup title="Distancia y Tiempo" icon={<ClockIcon />}>
 *   <MetricCard label="Distancia" value="42.5 km" />
 *   <MetricCard label="Tiempo Total" value="2h 30m" />
 * </MetricGroup>
 * ```
 */
export const MetricGroup: React.FC<MetricGroupProps> = ({
  title,
  children,
  icon,
  grid = true,
  className = '',
}) => {
  return (
    <div className={`metric-group ${className}`}>
      {/* Header */}
      <div className="metric-group__header">
        {icon && <span className="metric-group__icon">{icon}</span>}
        <h3 className="metric-group__title">{title}</h3>
      </div>

      {/* Content */}
      <div className={`metric-group__content ${grid ? 'metric-group__content--grid' : ''}`}>
        {children}
      </div>
    </div>
  );
};
