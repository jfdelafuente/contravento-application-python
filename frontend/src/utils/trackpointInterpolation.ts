/**
 * Trackpoint Interpolation Utilities (Feature 003 - User Story 3)
 *
 * Provides smooth hover marker movement on map by interpolating between
 * simplified trackpoints when user hovers over elevation profile.
 *
 * Problem: Douglas-Peucker simplification reduces trackpoints to ~200-500 points,
 * causing the hover marker to "jump" between discrete points.
 *
 * Solution: Linear interpolation between nearest trackpoints based on mouse
 * position (distance_km) to create virtual trackpoint at exact hover location.
 *
 * Interpolated fields:
 * - latitude
 * - longitude
 * - elevation
 * - gradient
 */

import { TrackPoint } from '../types/gpx';

/**
 * Linear interpolation between two values
 * @param a - Start value
 * @param b - End value
 * @param t - Interpolation factor (0 to 1)
 * @returns Interpolated value
 */
function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/**
 * Find the two nearest trackpoints surrounding the target distance
 *
 * @param trackpoints - Array of trackpoints sorted by distance_km
 * @param targetDistance - Target distance in km
 * @returns Object with before/after trackpoints and interpolation factor, or null if not found
 */
function findSurroundingPoints(
  trackpoints: TrackPoint[],
  targetDistance: number
): { before: TrackPoint; after: TrackPoint; factor: number } | null {
  // Edge case: empty or single trackpoint
  if (trackpoints.length === 0) return null;
  if (trackpoints.length === 1) {
    return {
      before: trackpoints[0],
      after: trackpoints[0],
      factor: 0,
    };
  }

  // Find the first trackpoint after target distance
  let afterIndex = trackpoints.findIndex((p) => p.distance_km >= targetDistance);

  // Edge case: target is before all trackpoints (return first point)
  if (afterIndex === 0) {
    return {
      before: trackpoints[0],
      after: trackpoints[0],
      factor: 0,
    };
  }

  // Edge case: target is after all trackpoints (return last point)
  if (afterIndex === -1) {
    const lastPoint = trackpoints[trackpoints.length - 1];
    return {
      before: lastPoint,
      after: lastPoint,
      factor: 0,
    };
  }

  // Normal case: target is between two trackpoints
  const before = trackpoints[afterIndex - 1];
  const after = trackpoints[afterIndex];

  // Calculate interpolation factor (0 to 1)
  const segmentDistance = after.distance_km - before.distance_km;
  const targetOffset = targetDistance - before.distance_km;
  const factor = segmentDistance > 0 ? targetOffset / segmentDistance : 0;

  return { before, after, factor };
}

/**
 * Interpolate trackpoint at specific distance from elevation profile hover
 *
 * Creates a "virtual" trackpoint at the exact mouse position by linear
 * interpolation between the nearest simplified trackpoints.
 *
 * @param trackpoints - Array of trackpoints sorted by distance_km
 * @param targetDistance - Target distance in km (from mouse hover)
 * @returns Interpolated trackpoint, or null if interpolation not possible
 *
 * @example
 * ```typescript
 * const trackpoints = [...]; // Simplified trackpoints (~200-500 points)
 * const mouseDistance = 12.345; // km from hover event
 *
 * const interpolatedPoint = interpolateTrackPoint(trackpoints, mouseDistance);
 * // Returns smooth trackpoint at exact mouse position
 * ```
 */
export function interpolateTrackPoint(
  trackpoints: TrackPoint[],
  targetDistance: number
): TrackPoint | null {
  const surrounding = findSurroundingPoints(trackpoints, targetDistance);

  if (!surrounding) return null;

  const { before, after, factor } = surrounding;

  // If factor is 0, we're exactly at one of the trackpoints
  if (factor === 0) return before;

  // IMPORTANT: Use nearest trackpoint coordinates to keep marker on GPX line
  // Linear interpolation in lat/lng creates a straight line that doesn't match
  // Leaflet's Mercator projection, causing the marker to visually "drift" off the line.
  // Solution: Use coordinates from nearest trackpoint, but interpolate elevation/gradient
  const useNearest = factor < 0.5 ? before : after;

  // Interpolate numeric values for accurate tooltip display
  const interpolatedPoint: TrackPoint = {
    // Use nearest point's ID
    point_id: useNearest.point_id,

    // Use nearest trackpoint coordinates to keep marker ON the GPX line visual
    // This prevents the marker from appearing "off" the line due to map projection
    latitude: useNearest.latitude,
    longitude: useNearest.longitude,

    // Interpolate elevation for smooth tooltip values (doesn't affect visual position)
    elevation:
      before.elevation !== null && after.elevation !== null
        ? lerp(before.elevation, after.elevation, factor)
        : before.elevation ?? after.elevation ?? null,

    // Interpolate distance for accurate tooltip
    distance_km: targetDistance,

    // Sequence: use nearest's sequence
    sequence: useNearest.sequence,

    // Interpolate gradient for smooth tooltip values
    gradient:
      before.gradient !== null && after.gradient !== null
        ? lerp(before.gradient, after.gradient, factor)
        : before.gradient ?? after.gradient ?? null,
  };

  return interpolatedPoint;
}

/**
 * Get trackpoint at specific chart position (for Recharts integration)
 *
 * Recharts provides activeIndex which corresponds to a chart data point.
 * This function converts the activeIndex to a distance, then interpolates.
 *
 * @param chartData - Array of chart data points (same as trackpoints)
 * @param activeIndex - Active index from Recharts onMouseMove event
 * @param allTrackpoints - Full array of trackpoints for interpolation
 * @returns Interpolated trackpoint at mouse position
 *
 * @example
 * ```typescript
 * // In Recharts onMouseMove handler
 * const handleMouseMove = (data: any) => {
 *   if (data && typeof data.activeIndex !== 'undefined') {
 *     const point = getTrackPointAtChartPosition(
 *       chartData,
 *       data.activeIndex,
 *       trackpoints
 *     );
 *     onPointHover?.(point);
 *   }
 * };
 * ```
 */
export function getTrackPointAtChartPosition(
  chartData: TrackPoint[],
  activeIndex: number,
  allTrackpoints: TrackPoint[]
): TrackPoint | null {
  // Validate index
  if (activeIndex < 0 || activeIndex >= chartData.length) {
    return null;
  }

  // Get the chart data point at activeIndex
  const chartPoint = chartData[activeIndex];

  // Interpolate based on the distance of this chart point
  // Note: chartData and allTrackpoints are the same in our case,
  // but this function is designed to be flexible
  return interpolateTrackPoint(allTrackpoints, chartPoint.distance_km);
}
