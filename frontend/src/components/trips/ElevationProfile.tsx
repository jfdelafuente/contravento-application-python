/**
 * ElevationProfile Component (Feature 003 - User Story 3)
 *
 * Interactive elevation profile chart using Recharts.
 *
 * Features:
 * - FR-017: Line chart showing elevation vs distance
 * - FR-018: Hover tooltip with elevation, distance, gradient
 * - FR-019: Click handler emits onPointClick(point) event for map sync
 * - FR-020: Color coding by gradient (green=uphill, blue=downhill)
 * - FR-021: "No elevation data" message when GPX lacks elevation
 * - FR-022: Responsive layout for mobile devices
 *
 * Success Criteria:
 * - SC-013: Chart loads in <2s for 1000 points
 * - SC-016: Click-to-map sync <300ms (handled by parent)
 */

import React, { useMemo, useCallback, useRef, useState, useEffect } from 'react';
import {
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
} from 'recharts';
import { interpolateTrackPoint } from '../../utils/trackpointInterpolation';
import './ElevationProfile.css';

export interface TrackPoint {
  point_id: string;
  latitude: number;
  longitude: number;
  elevation: number | null;
  distance_km: number;
  sequence: number;
  gradient: number | null;
}

interface ElevationProfileProps {
  /** Simplified trackpoints with elevation data */
  trackpoints: TrackPoint[];

  /** Whether GPX file contains elevation data */
  hasElevation: boolean;

  /** Total distance in kilometers */
  distanceKm: number;

  /** Callback when user clicks a point on the chart (FR-019) */
  onPointClick?: (point: TrackPoint) => void;

  /** Callback when user hovers over a point on the chart */
  onPointHover?: (point: TrackPoint | null) => void;

  /** Chart height in pixels (default: 300) */
  height?: number;
}

/**
 * Custom tooltip showing elevation, distance, and gradient (FR-018)
 */
const CustomTooltip: React.FC<any> = ({ active, payload }) => {
  if (!active || !payload || !payload.length) {
    return null;
  }

  const data = payload[0].payload;

  return (
    <div className="elevation-tooltip">
      <div className="tooltip-row">
        <span className="tooltip-label">Distancia:</span>
        <span className="tooltip-value">{data.distance_km.toFixed(2)} km</span>
      </div>
      <div className="tooltip-row">
        <span className="tooltip-label">Elevación:</span>
        <span className="tooltip-value">{data.elevation.toFixed(0)} m</span>
      </div>
      {data.gradient !== null && (
        <div className="tooltip-row">
          <span className="tooltip-label">Pendiente:</span>
          <span className="tooltip-value tooltip-gradient" data-gradient={data.gradient >= 0 ? 'uphill' : 'downhill'}>
            {data.gradient > 0 ? '+' : ''}{data.gradient.toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
};

/**
 * Determine point color based on gradient (FR-020)
 * - Green shades: Uphill (0% to >10%)
 * - Blue shades: Downhill (<0%)
 * - Gray: Flat (~0%)
 */
const getGradientColor = (gradient: number | null): string => {
  if (gradient === null) return '#94a3b8'; // slate-400 (neutral)

  if (Math.abs(gradient) < 0.5) return '#94a3b8'; // Flat (0-0.5%)

  if (gradient > 0) {
    // Uphill - Green shades
    if (gradient > 10) return '#15803d'; // green-700 (very steep)
    if (gradient > 6) return '#16a34a'; // green-600 (steep)
    if (gradient > 3) return '#22c55e'; // green-500 (moderate)
    return '#4ade80'; // green-400 (gentle)
  } else {
    // Downhill - Blue shades
    if (gradient < -10) return '#1e40af'; // blue-700 (very steep)
    if (gradient < -6) return '#2563eb'; // blue-600 (steep)
    if (gradient < -3) return '#3b82f6'; // blue-500 (moderate)
    return '#60a5fa'; // blue-400 (gentle)
  }
};

export const ElevationProfile: React.FC<ElevationProfileProps> = ({
  trackpoints,
  hasElevation,
  distanceKm,
  onPointClick,
  onPointHover,
  height = 300,
}) => {
  // Ref to track chart container for native mouse position capture
  const containerRef = useRef<HTMLDivElement>(null);

  // Track chart rendering dimensions (calculated from margins)
  const [chartDimensions, setChartDimensions] = useState<{
    width: number;
    leftMargin: number;
  } | null>(null);

  // Check if we have elevation data (FR-021)
  const hasValidElevation = useMemo(() => {
    return hasElevation && trackpoints.some((p) => p.elevation !== null);
  }, [hasElevation, trackpoints]);

  // Prepare chart data with color coding
  const chartData = useMemo(() => {
    if (!hasValidElevation) return [];

    return trackpoints
      .filter((p) => p.elevation !== null)
      .map((point) => ({
        ...point,
        color: getGradientColor(point.gradient),
      }));
  }, [trackpoints, hasValidElevation]);

  // Calculate elevation range for Y-axis
  const elevationRange = useMemo(() => {
    if (chartData.length === 0) return { min: 0, max: 100 };

    const elevations = chartData.map((p) => p.elevation as number);
    const min = Math.min(...elevations);
    const max = Math.max(...elevations);
    const padding = (max - min) * 0.1 || 10; // 10% padding or 10m minimum

    return {
      min: Math.floor(min - padding),
      max: Math.ceil(max + padding),
    };
  }, [chartData]);

  // Update chart dimensions when container resizes
  useEffect(() => {
    if (!containerRef.current) return;

    const updateDimensions = () => {
      if (!containerRef.current) return;

      const containerWidth = containerRef.current.offsetWidth;

      // Try to find the actual SVG element rendered by Recharts to measure Y-axis
      const svgElement = containerRef.current.querySelector('svg');
      let leftMargin = 50; // Default fallback

      if (svgElement) {
        // Look for the Y-axis group element (g.recharts-yAxis)
        const yAxisGroup = svgElement.querySelector('.recharts-yAxis');
        if (yAxisGroup) {
          const bbox = (yAxisGroup as SVGGraphicsElement).getBBox();
          // Y-axis width + some padding
          leftMargin = Math.max(bbox.width + 10, 40); // Min 40px, add 10px padding
        }
      }

      const rightMargin = 30; // From Recharts margins
      const plotWidth = containerWidth - leftMargin - rightMargin;

      // Only update if dimensions actually changed (prevent infinite loop)
      setChartDimensions((prev) => {
        if (prev && prev.width === plotWidth && prev.leftMargin === leftMargin) {
          return prev; // No change, return same object to prevent re-render
        }
        return {
          width: plotWidth,
          leftMargin: leftMargin,
        };
      });
    };

    // Initial measurement with delay to let Recharts render
    const initialTimer = setTimeout(updateDimensions, 100);

    // Use ResizeObserver for container size changes (more efficient than window resize)
    const resizeObserver = new ResizeObserver(updateDimensions);
    resizeObserver.observe(containerRef.current);

    return () => {
      clearTimeout(initialTimer);
      resizeObserver.disconnect();
    };
  }, []); // Empty deps - only set up observers once

  // Handle click on chart point (FR-019)
  const handleClick = (data: any) => {
    // Recharts 3.x uses activeIndex instead of activePayload
    if (data && typeof data.activeIndex !== 'undefined' && chartData.length > 0) {
      const index = parseInt(data.activeIndex as string, 10);

      if (index >= 0 && index < chartData.length) {
        const point = chartData[index] as TrackPoint;
        onPointClick?.(point);
      }
    }
  };

  // Handle native mouse move for smooth interpolation
  const handleNativeMouseMove = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    if (!chartDimensions || chartData.length === 0 || !containerRef.current) {
      return;
    }

    // Get mouse X position relative to container
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;

    // Calculate mouse X position relative to plot area (excluding margins)
    const plotX = mouseX - chartDimensions.leftMargin;

    // Check if mouse is within plot area
    if (plotX < 0 || plotX > chartDimensions.width) {
      onPointHover?.(null);
      return;
    }

    // Convert mouse X position to distance (km)
    // plotX / chartDimensions.width = targetDistance / distanceKm
    const targetDistance = (plotX / chartDimensions.width) * distanceKm;

    // Interpolate trackpoint at target distance
    const interpolatedPoint = interpolateTrackPoint(chartData as TrackPoint[], targetDistance);

    if (interpolatedPoint) {
      onPointHover?.(interpolatedPoint);
    }
  }, [chartDimensions, chartData, distanceKm, onPointHover]);

  // Handle mouse move over chart (fallback for Recharts event)
  // This provides discrete point tracking if native events don't fire
  const handleMouseMove = useCallback((data: any) => {
    // Only use Recharts event if we don't have chart dimensions yet
    if (chartDimensions) return; // Prefer native mouse events

    if (data && typeof data.activeIndex !== 'undefined' && chartData.length > 0) {
      const index = parseInt(data.activeIndex as string, 10);

      if (index >= 0 && index < chartData.length) {
        const point = chartData[index] as TrackPoint;
        onPointHover?.(point);
      }
    }
  }, [chartData, onPointHover, chartDimensions]);

  // Handle mouse leave from chart
  const handleMouseLeave = useCallback(() => {
    onPointHover?.(null);
  }, [onPointHover]);

  // Show "No elevation data" message (FR-021)
  if (!hasValidElevation) {
    return (
      <div className="elevation-profile-empty">
        <svg
          className="icon-mountain"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 3l3.057-3L12 2.557 16.943 0 20 3v18l-3.057 3L12 21.443 7.057 24 4 21V3z"
          />
        </svg>
        <p className="message-title">No hay datos de elevación disponibles</p>
        <p className="message-subtitle">
          Este archivo GPX no incluye información de altitud
        </p>
      </div>
    );
  }

  return (
    <div
      className="elevation-profile"
      ref={containerRef}
      onMouseMove={handleNativeMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="profile-header">
        <h3 className="profile-title">Perfil de Elevación</h3>
        <div className="profile-legend">
          <div className="legend-item">
            <div className="legend-color legend-uphill" />
            <span>Subida</span>
          </div>
          <div className="legend-item">
            <div className="legend-color legend-downhill" />
            <span>Bajada</span>
          </div>
          <div className="legend-item">
            <div className="legend-color legend-flat" />
            <span>Llano</span>
          </div>
        </div>
      </div>

      {/* Responsive container (FR-022) */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={chartData}
          onClick={handleClick}
          onMouseMove={handleMouseMove}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <defs>
            {/* Gradient fill for area under line */}
            <linearGradient id="colorElevation" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />

          <XAxis
            dataKey="distance_km"
            type="number"
            domain={[0, distanceKm]}
            tickFormatter={(value) => `${value.toFixed(1)} km`}
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />

          <YAxis
            domain={[elevationRange.min, elevationRange.max]}
            tickFormatter={(value) => `${value}m`}
            stroke="#64748b"
            style={{ fontSize: '12px' }}
          />

          <Tooltip content={<CustomTooltip />} />

          {/* Area fill under line */}
          <Area
            type="monotone"
            dataKey="elevation"
            fill="url(#colorElevation)"
            stroke="none"
          />

          {/* Main elevation line with color coding by gradient (FR-020) */}
          <Line
            type="monotone"
            dataKey="elevation"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            activeDot={{
              r: 6,
              fill: '#3b82f6',
              stroke: '#fff',
              strokeWidth: 2,
            }}
            isAnimationActive={false} // Disable animation for better performance (SC-013)
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
