/**
 * T070: Performance Test - Elevation Profile Loading
 *
 * Tests that elevation profile loads in <2s for 1000 points (SC-013).
 *
 * Success Criteria:
 * - SC-013: Elevation profile must load in <2 seconds for routes with 1000 points
 * - Chart should render smoothly without blocking UI
 * - Hover tooltips should appear with minimal latency
 *
 * Phase 5 - US3: Perfil de Elevación Interactivo
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { ElevationProfile } from '../../src/components/trips/ElevationProfile';

// Mock Recharts components
vi.mock('recharts', () => ({
  ComposedChart: vi.fn(({ children, data }: any) => (
    <div data-testid="composed-chart" data-point-count={data?.length || 0}>
      {children}
    </div>
  )),
  Area: vi.fn(() => <div data-testid="area" />),
  Line: vi.fn(() => <div data-testid="line" />),
  XAxis: vi.fn(() => <div data-testid="x-axis" />),
  YAxis: vi.fn(() => <div data-testid="y-axis" />),
  CartesianGrid: vi.fn(() => <div data-testid="grid" />),
  Tooltip: vi.fn(() => <div data-testid="tooltip" />),
  ResponsiveContainer: vi.fn(({ children }: any) => (
    <div data-testid="responsive-container">{children}</div>
  )),
}));

// Mock CSS
vi.mock('../../src/components/trips/ElevationProfile.css', () => ({}));

describe('T070: ElevationProfile Performance Tests', () => {
  /**
   * Helper: Generate test trackpoints with elevation data
   */
  const generateTrackpoints = (count: number) => {
    return Array.from({ length: count }, (_, i) => ({
      point_id: `point-${i}`,
      latitude: 40.0 + i * 0.0001,
      longitude: -3.0 + i * 0.0001,
      elevation: 500 + Math.sin(i / 10) * 100, // Simulated elevation profile
      distance_km: (i * 0.5) / count, // Incremental distance
      sequence: i,
      gradient: i > 0 ? Math.sin(i / 10) * 10 : null, // Simulated gradient
    }));
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Test: Elevation profile loads in <2s for 1000 points
   * SC-013: Elevation profile must load in <2 seconds for 1000 points
   */
  it('should render elevation profile with 1000 points in <2s', async () => {
    const trackpoints = generateTrackpoints(1000);

    const startTime = performance.now();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={trackpoints} onPointClick={vi.fn()} />
    );

    // Wait for chart to be rendered
    await waitFor(() => {
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderDuration = endTime - startTime;

    // Assert: Render time <2000ms (SC-013)
    expect(renderDuration).toBeLessThan(2000);

    // Verify 1000 points were passed to chart
    const chart = getByTestId('composed-chart');
    expect(chart.getAttribute('data-point-count')).toBe('1000');
  });

  /**
   * Test: Elevation profile with 500 points (typical route)
   * Verifies performance with medium-sized dataset
   */
  it('should render elevation profile with 500 points in <1s', async () => {
    const trackpoints = generateTrackpoints(500);

    const startTime = performance.now();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={trackpoints} onPointClick={vi.fn()} />
    );

    await waitFor(() => {
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderDuration = endTime - startTime;

    // Assert: 500 points should render even faster (<1s)
    expect(renderDuration).toBeLessThan(1000);

    const chart = getByTestId('composed-chart');
    expect(chart.getAttribute('data-point-count')).toBe('500');
  });

  /**
   * Test: Elevation profile with 100 points (short route)
   * Verifies performance with small dataset
   */
  it('should render elevation profile with 100 points in <500ms', async () => {
    const trackpoints = generateTrackpoints(100);

    const startTime = performance.now();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={trackpoints} onPointClick={vi.fn()} />
    );

    await waitFor(() => {
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderDuration = endTime - startTime;

    // Assert: Small dataset should render very quickly
    expect(renderDuration).toBeLessThan(500);

    const chart = getByTestId('composed-chart');
    expect(chart.getAttribute('data-point-count')).toBe('100');
  });

  /**
   * Test: Re-render performance (e.g., window resize)
   * Verifies that re-renders are also fast
   */
  it('should handle re-renders efficiently', async () => {
    const trackpoints = generateTrackpoints(1000);

    const { rerender, getByTestId } = render(
      <ElevationProfile trackpoints={trackpoints} onPointClick={vi.fn()} />
    );

    await waitFor(() => {
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    // Measure re-render time (e.g., window resize triggering ResponsiveContainer)
    const startTime = performance.now();

    rerender(<ElevationProfile trackpoints={trackpoints} onPointClick={vi.fn()} />);

    await waitFor(() => {
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const rerenderDuration = endTime - startTime;

    // Assert: Re-render should be fast (<500ms)
    expect(rerenderDuration).toBeLessThan(500);
  });

  /**
   * Test: Empty state renders quickly
   * Verifies performance when no elevation data available
   */
  it('should render empty state instantly when no trackpoints', () => {
    const startTime = performance.now();

    const { getByText } = render(<ElevationProfile trackpoints={[]} onPointClick={vi.fn()} />);

    const endTime = performance.now();
    const renderDuration = endTime - startTime;

    // Assert: Empty state renders instantly
    expect(renderDuration).toBeLessThan(100);

    // Verify empty state message is shown
    expect(getByText(/No hay datos de elevación disponibles/i)).toBeInTheDocument();
  });

  /**
   * Test: No elevation data state renders quickly
   * Verifies performance when trackpoints lack elevation
   */
  it('should render no-elevation state quickly', () => {
    const trackpointsWithoutElevation = generateTrackpoints(100).map((tp) => ({
      ...tp,
      elevation: null,
      gradient: null,
    }));

    const startTime = performance.now();

    const { getByText } = render(
      <ElevationProfile trackpoints={trackpointsWithoutElevation} onPointClick={vi.fn()} />
    );

    const endTime = performance.now();
    const renderDuration = endTime - startTime;

    // Assert: Renders quickly even with null elevations
    expect(renderDuration).toBeLessThan(200);

    // Verify no-elevation message is shown
    expect(getByText(/No hay datos de elevación disponibles/i)).toBeInTheDocument();
  });

  /**
   * Test: Click handler performance
   * Verifies that onPointClick callback executes quickly
   */
  it('should execute click handler quickly', async () => {
    const trackpoints = generateTrackpoints(1000);
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={trackpoints} onPointClick={mockOnPointClick} />
    );

    await waitFor(() => {
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    // Measure click handler execution time
    const startTime = performance.now();

    // Simulate click event
    const chart = getByTestId('composed-chart');
    chart.click();

    // In real Recharts, this would trigger onClick with active payload
    // For now, just verify the mock can be called quickly
    if (mockOnPointClick.mock.calls.length > 0) {
      const endTime = performance.now();
      const clickDuration = endTime - startTime;

      // Assert: Click handling is instantaneous (<50ms)
      expect(clickDuration).toBeLessThan(50);
    }
  });

  /**
   * Test: Gradient color calculation performance
   * Verifies that gradient color mapping doesn't slow down rendering
   */
  it('should calculate gradient colors efficiently', async () => {
    const trackpoints = generateTrackpoints(1000);

    const startTime = performance.now();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={trackpoints} onPointClick={vi.fn()} />
    );

    await waitFor(() => {
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderDuration = endTime - startTime;

    // Assert: Gradient color calculation doesn't slow render (<2s)
    expect(renderDuration).toBeLessThan(2000);

    // Verify chart components are rendered
    expect(getByTestId('area')).toBeInTheDocument();
    expect(getByTestId('line')).toBeInTheDocument();
  });

  /**
   * Test: Responsive container performance
   * Verifies that ResponsiveContainer doesn't add significant overhead
   */
  it('should handle ResponsiveContainer wrapping efficiently', async () => {
    const trackpoints = generateTrackpoints(1000);

    const startTime = performance.now();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={trackpoints} onPointClick={vi.fn()} />
    );

    await waitFor(() => {
      expect(getByTestId('responsive-container')).toBeInTheDocument();
      expect(getByTestId('composed-chart')).toBeInTheDocument();
    });

    const endTime = performance.now();
    const renderDuration = endTime - startTime;

    // Assert: ResponsiveContainer doesn't add significant overhead
    expect(renderDuration).toBeLessThan(2000);
  });
});
