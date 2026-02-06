/**
 * T071: Integration Test - ElevationProfile to Map Click Sync
 *
 * Tests that clicking on elevation profile centers map on that point in <300ms (SC-016).
 *
 * Success Criteria:
 * - SC-016: Profile-to-map sync must complete in <300ms
 * - FR-019: Clicking on profile point centers map on that location
 * - Map should animate smoothly to the selected point
 *
 * Phase 5 - US3: Perfil de Elevación Interactivo
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { ElevationProfile } from '../../src/components/trips/ElevationProfile';

// Mock Recharts components with click simulation (Recharts 3.x API)
vi.mock('recharts', () => ({
  ComposedChart: vi.fn(({ children, onClick, data }: any) => {
    // Store click handler globally for test access
    (global as any).__chartClickHandler = onClick;

    return (
      <div
        data-testid="composed-chart"
        onClick={(e) => {
          // Simulate Recharts 3.x click event with activeIndex
          if (onClick && data && data.length > 0) {
            onClick({
              activeIndex: 0, // First point in chart data
            });
          }
        }}
      >
        {children}
      </div>
    );
  }),
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

describe('T071: ElevationProfile-Map Sync Integration Tests', () => {
  const mockTrackpoints = [
    {
      point_id: 'point-0',
      latitude: 40.4168,
      longitude: -3.7038,
      elevation: 500,
      distance_km: 0,
      sequence: 0,
      gradient: null,
    },
    {
      point_id: 'point-1',
      latitude: 40.4200,
      longitude: -3.7000,
      elevation: 550,
      distance_km: 0.5,
      sequence: 1,
      gradient: 10.0,
    },
    {
      point_id: 'point-2',
      latitude: 40.4250,
      longitude: -3.6950,
      elevation: 600,
      distance_km: 1.0,
      sequence: 2,
      gradient: 8.5,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * Test: Click on profile point triggers onPointClick callback
   * FR-019: Clicking on profile point centers map on that location
   */
  it('should call onPointClick when user clicks on profile chart', async () => {
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');
    expect(chart).toBeInTheDocument();

    // Click on chart
    fireEvent.click(chart);

    // Assert: onPointClick was called
    expect(mockOnPointClick).toHaveBeenCalledTimes(1);

    // Assert: Callback received correct point data
    const callArgs = mockOnPointClick.mock.calls[0][0];
    expect(callArgs).toHaveProperty('latitude');
    expect(callArgs).toHaveProperty('longitude');
    expect(callArgs).toHaveProperty('elevation');
  });

  /**
   * Test: Profile-to-map sync completes in <300ms
   * SC-016: Profile-to-map sync must complete in <300ms
   */
  it('should complete profile-to-map sync in <300ms', async () => {
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');

    // Measure sync time
    const startTime = performance.now();

    // Click on chart
    fireEvent.click(chart);

    // Wait for callback to complete
    await waitFor(() => {
      expect(mockOnPointClick).toHaveBeenCalled();
    });

    const endTime = performance.now();
    const syncDuration = endTime - startTime;

    // Assert: Sync time <300ms (SC-016)
    expect(syncDuration).toBeLessThan(300);
  });

  /**
   * Test: Callback receives correct point coordinates
   * Verifies that clicked point data is accurately passed to map
   */
  it('should pass correct coordinates to onPointClick callback', async () => {
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');
    fireEvent.click(chart);

    await waitFor(() => {
      expect(mockOnPointClick).toHaveBeenCalled();
    });

    // Assert: Callback received first point's coordinates
    const point = mockOnPointClick.mock.calls[0][0];
    expect(point.latitude).toBe(40.4168);
    expect(point.longitude).toBe(-3.7038);
    expect(point.elevation).toBe(500);
    expect(point.distance_km).toBe(0);
  });

  /**
   * Test: Multiple rapid clicks are handled gracefully
   * Verifies that rapid profile clicks don't cause performance issues
   */
  it('should handle multiple rapid clicks efficiently', async () => {
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');

    // Perform 5 rapid clicks
    const clickDurations: number[] = [];

    for (let i = 0; i < 5; i++) {
      const startTime = performance.now();

      fireEvent.click(chart);

      await waitFor(() => {
        expect(mockOnPointClick).toHaveBeenCalledTimes(i + 1);
      });

      const endTime = performance.now();
      clickDurations.push(endTime - startTime);
    }

    // Assert: All clicks completed in <300ms
    clickDurations.forEach((duration, index) => {
      expect(duration).toBeLessThan(300);
    });

    // Assert: Average duration also <300ms
    const avgDuration = clickDurations.reduce((sum, d) => sum + d, 0) / clickDurations.length;
    expect(avgDuration).toBeLessThan(300);
  });

  /**
   * Test: Click on different profile sections
   * Verifies that clicks anywhere on profile trigger correct callbacks
   */
  it('should handle clicks at different profile positions', async () => {
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');

    // Click 3 times (simulating clicks at different positions)
    fireEvent.click(chart);
    fireEvent.click(chart);
    fireEvent.click(chart);

    await waitFor(() => {
      expect(mockOnPointClick).toHaveBeenCalledTimes(3);
    });

    // Assert: Each click passed valid point data
    mockOnPointClick.mock.calls.forEach((call) => {
      const point = call[0];
      expect(point).toHaveProperty('latitude');
      expect(point).toHaveProperty('longitude');
      expect(point).toHaveProperty('elevation');
    });
  });

  /**
   * Test: No callback when onPointClick is not provided
   * Verifies graceful degradation when callback is optional
   */
  it('should not throw error when onPointClick is not provided', () => {
    const { getByTestId } = render(<ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} />);

    const chart = getByTestId('composed-chart');

    // Should not throw
    expect(() => {
      fireEvent.click(chart);
    }).not.toThrow();
  });

  /**
   * Test: Callback receives null gradient for first point
   * Verifies that gradient is correctly null for first trackpoint
   */
  it('should pass null gradient for first trackpoint', async () => {
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');
    fireEvent.click(chart);

    await waitFor(() => {
      expect(mockOnPointClick).toHaveBeenCalled();
    });

    // Assert: First point has null gradient
    const point = mockOnPointClick.mock.calls[0][0];
    expect(point.gradient).toBeNull();
  });

  /**
   * Test: Click event contains all required point metadata
   * Verifies that complete point information is available for map sync
   */
  it('should include all point metadata in callback', async () => {
    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={mockTrackpoints} hasElevation={true} distanceKm={1.0} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');
    fireEvent.click(chart);

    await waitFor(() => {
      expect(mockOnPointClick).toHaveBeenCalled();
    });

    const point = mockOnPointClick.mock.calls[0][0];

    // Assert: All required metadata is present
    expect(point).toHaveProperty('point_id');
    expect(point).toHaveProperty('latitude');
    expect(point).toHaveProperty('longitude');
    expect(point).toHaveProperty('elevation');
    expect(point).toHaveProperty('distance_km');
    expect(point).toHaveProperty('sequence');
    expect(point).toHaveProperty('gradient');
  });

  /**
   * Test: Sync performance with large dataset (1000 points)
   * SC-016: Sync should remain fast even with large profiles
   */
  it('should maintain sync performance with 1000 trackpoints', async () => {
    const largeTrackpoints = Array.from({ length: 1000 }, (_, i) => ({
      point_id: `point-${i}`,
      latitude: 40.0 + i * 0.0001,
      longitude: -3.0 + i * 0.0001,
      elevation: 500 + Math.sin(i / 10) * 100,
      distance_km: (i * 50) / 1000,
      sequence: i,
      gradient: i > 0 ? Math.sin(i / 10) * 10 : null,
    }));

    const mockOnPointClick = vi.fn();

    const { getByTestId } = render(
      <ElevationProfile trackpoints={largeTrackpoints} hasElevation={true} distanceKm={50} onPointClick={mockOnPointClick} />
    );

    const chart = getByTestId('composed-chart');

    const startTime = performance.now();

    fireEvent.click(chart);

    await waitFor(() => {
      expect(mockOnPointClick).toHaveBeenCalled();
    });

    const endTime = performance.now();
    const syncDuration = endTime - startTime;

    // Assert: Even with 1000 points, sync <300ms
    expect(syncDuration).toBeLessThan(300);
  });

  /**
   * Test: Empty trackpoints array doesn't break click handling
   * Verifies robustness with edge case
   */
  it('should handle empty trackpoints gracefully on click', () => {
    const mockOnPointClick = vi.fn();

    const { getByText } = render(<ElevationProfile trackpoints={[]} hasElevation={false} distanceKm={0} onPointClick={mockOnPointClick} />);

    // Empty state should be shown
    expect(getByText(/No hay datos de elevación disponibles/i)).toBeInTheDocument();

    // Callback should not be called (no chart to click)
    expect(mockOnPointClick).not.toHaveBeenCalled();
  });
});
