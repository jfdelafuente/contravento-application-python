/**
 * Unit tests for Step3Map component (Feature 017 - Phase 7 - US4)
 *
 * Tests the map visualization step of the GPS Trip Creation Wizard
 *
 * Coverage:
 * - T077: Telemetry panel display with GPX metrics
 * - T077: TripMap integration with GPX trackpoints
 * - T077: Navigation buttons (back, next)
 * - T077: Empty state when no GPX data
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Step3Map } from '../../src/components/trips/GPXWizard/Step3Map';
import type { GPXTelemetry } from '../../src/types/gpxWizard';
import { TripDifficulty } from '../../src/types/trip';

// Mock TripMap component (already tested in Feature 003)
vi.mock('../../src/components/trips/TripMap', () => ({
  TripMap: ({ gpxTrackPoints, gpxStartPoint, gpxEndPoint }: any) => (
    <div data-testid="trip-map-mock">
      <div>Track points: {gpxTrackPoints?.length || 0}</div>
      {gpxStartPoint && <div>Start: {gpxStartPoint.latitude},{gpxStartPoint.longitude}</div>}
      {gpxEndPoint && <div>End: {gpxEndPoint.latitude},{gpxEndPoint.longitude}</div>}
    </div>
  ),
}));

describe('Step3Map Component', () => {
  const mockTelemetry: GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 1250,
    elevation_loss: 1100,
    max_elevation: 1850,
    min_elevation: 450,
    has_elevation: true,
    difficulty: TripDifficulty.ADVANCED,
  };

  const mockTrackPoints = [
    { point_id: '1', latitude: 40.4165, longitude: -3.7026, elevation: 650, distance_km: 0, sequence: 0, gradient: null },
    { point_id: '2', latitude: 40.4175, longitude: -3.7036, elevation: 655, distance_km: 1.2, sequence: 1, gradient: 0.5 },
    { point_id: '3', latitude: 40.4185, longitude: -3.7046, elevation: 660, distance_km: 2.4, sequence: 2, gradient: 0.4 },
  ];

  const defaultProps = {
    telemetry: mockTelemetry,
    trackPoints: mockTrackPoints,
    onBack: vi.fn(),
    onNext: vi.fn(),
  };

  describe('Telemetry Panel (T077, T080)', () => {
    it('should display all telemetry metrics', () => {
      render(<Step3Map {...defaultProps} />);

      // Distance
      expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();

      // Elevation gain
      expect(screen.getByText(/1250\s*m/i)).toBeInTheDocument();

      // Elevation loss
      expect(screen.getByText(/1100\s*m/i)).toBeInTheDocument();

      // Max elevation
      expect(screen.getByText(/1850\s*m/i)).toBeInTheDocument();

      // Min elevation
      expect(screen.getByText(/450\s*m/i)).toBeInTheDocument();
    });

    it('should hide elevation metrics if not available', () => {
      const telemetryNoElevation: GPXTelemetry = {
        ...mockTelemetry,
        elevation_gain: null,
        elevation_loss: null,
        max_elevation: null,
        min_elevation: null,
        has_elevation: false,
      };
      render(<Step3Map {...defaultProps} telemetry={telemetryNoElevation} />);

      // Should still show distance metric
      expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();

      // Should NOT show elevation-related metrics
      expect(screen.queryByText(/Desnivel positivo/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Desnivel negativo/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Altitud máxima/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Altitud mínima/i)).not.toBeInTheDocument();
    });

    it('should display telemetry panel title', () => {
      render(<Step3Map {...defaultProps} />);

      expect(screen.getByText(/Datos de telemetría/i)).toBeInTheDocument();
    });
  });

  describe('TripMap Integration (T077, T079)', () => {
    it('should render TripMap component with GPX trackpoints', () => {
      render(<Step3Map {...defaultProps} />);

      const tripMap = screen.getByTestId('trip-map-mock');
      expect(tripMap).toBeInTheDocument();

      // Verify trackpoints count
      expect(tripMap).toHaveTextContent('Track points: 3');
    });

    it('should pass start point to TripMap', () => {
      render(<Step3Map {...defaultProps} />);

      const tripMap = screen.getByTestId('trip-map-mock');

      // Start point should be the first trackpoint
      expect(tripMap).toHaveTextContent('Start: 40.4165,-3.7026');
    });

    it('should pass end point to TripMap', () => {
      render(<Step3Map {...defaultProps} />);

      const tripMap = screen.getByTestId('trip-map-mock');

      // End point should be the last trackpoint
      expect(tripMap).toHaveTextContent('End: 40.4185,-3.7046');
    });

    it('should show empty state if no trackpoints', () => {
      render(<Step3Map {...defaultProps} trackPoints={[]} />);

      expect(screen.getByText(/No hay datos de ruta disponibles/i)).toBeInTheDocument();
    });

    it('should show empty state if trackpoints is undefined', () => {
      render(<Step3Map {...defaultProps} trackPoints={undefined} />);

      expect(screen.getByText(/No hay datos de ruta disponibles/i)).toBeInTheDocument();
    });
  });

  describe('Navigation Buttons (T077, T084)', () => {
    it('should render "Atrás" button', () => {
      render(<Step3Map {...defaultProps} />);

      const backButton = screen.getByRole('button', { name: /atrás/i });
      expect(backButton).toBeInTheDocument();
    });

    it('should render "Siguiente" button', () => {
      render(<Step3Map {...defaultProps} />);

      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      expect(nextButton).toBeInTheDocument();
    });

    it('should call onBack when "Atrás" is clicked', async () => {
      const user = userEvent.setup();
      const onBack = vi.fn();

      render(<Step3Map {...defaultProps} onBack={onBack} />);

      const backButton = screen.getByRole('button', { name: /atrás/i });
      await user.click(backButton);

      expect(onBack).toHaveBeenCalledOnce();
    });

    it('should call onNext when "Siguiente" is clicked', async () => {
      const user = userEvent.setup();
      const onNext = vi.fn();

      render(<Step3Map {...defaultProps} onNext={onNext} />);

      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      await user.click(nextButton);

      expect(onNext).toHaveBeenCalledOnce();
    });

    it('should disable "Siguiente" button if no trackpoints', () => {
      render(<Step3Map {...defaultProps} trackPoints={[]} />);

      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      expect(nextButton).toBeDisabled();
    });

    it('should enable "Siguiente" button if trackpoints exist', () => {
      render(<Step3Map {...defaultProps} />);

      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      expect(nextButton).toBeEnabled();
    });
  });

  describe('Layout and Structure (T077)', () => {
    it('should render step title', () => {
      render(<Step3Map {...defaultProps} />);

      expect(screen.getByText(/Visualiza tu ruta/i)).toBeInTheDocument();
    });

    it('should render step description', () => {
      render(<Step3Map {...defaultProps} />);

      expect(screen.getByText(/Verifica que el mapa muestre correctamente tu ruta/i)).toBeInTheDocument();
    });

    it('should render map section before telemetry panel', () => {
      const { container } = render(<Step3Map {...defaultProps} />);

      const sections = container.querySelectorAll('section, div[class*="section"]');
      const mapSection = screen.getByTestId('trip-map-mock').closest('section, div[class*="section"]');
      const telemetrySection = screen.getByText(/Datos de telemetría/i).closest('section, div[class*="section"]');

      expect(mapSection).toBeTruthy();
      expect(telemetrySection).toBeTruthy();

      // Map should appear before telemetry in the DOM
      const mapIndex = Array.from(sections).indexOf(mapSection!);
      const telemetryIndex = Array.from(sections).indexOf(telemetrySection!);

      expect(mapIndex).toBeLessThan(telemetryIndex);
    });
  });

  describe('Accessibility (T077)', () => {
    it('should have proper heading hierarchy', () => {
      render(<Step3Map {...defaultProps} />);

      const h2 = screen.getByRole('heading', { level: 2, name: /Visualiza tu ruta/i });
      expect(h2).toBeInTheDocument();

      const h3 = screen.getByRole('heading', { level: 3, name: /Datos de telemetría/i });
      expect(h3).toBeInTheDocument();
    });

    it('should have semantic navigation buttons', () => {
      render(<Step3Map {...defaultProps} />);

      const nav = screen.getByRole('navigation') || screen.getByRole('group');
      expect(nav).toBeInTheDocument();

      const backButton = screen.getByRole('button', { name: /atrás/i });
      const nextButton = screen.getByRole('button', { name: /siguiente/i });

      expect(backButton).toBeInTheDocument();
      expect(nextButton).toBeInTheDocument();
    });

    it('should provide descriptive button labels', () => {
      render(<Step3Map {...defaultProps} />);

      // Buttons should have clear text labels (not just icons)
      expect(screen.getByRole('button', { name: /atrás/i })).toHaveTextContent(/atrás/i);
      expect(screen.getByRole('button', { name: /siguiente/i })).toHaveTextContent(/siguiente/i);
    });
  });

  describe('Edge Cases (T077)', () => {
    it('should handle telemetry with zero distance', () => {
      const zeroTelemetry: GPXTelemetry = {
        distance_km: 0,
        elevation_gain: 0,
        elevation_loss: 0,
        max_elevation: 0,
        min_elevation: 0,
        has_elevation: true,
        difficulty: TripDifficulty.EASY,
      };

      render(<Step3Map {...defaultProps} telemetry={zeroTelemetry} />);

      expect(screen.getByText(/0\s*km/i)).toBeInTheDocument();
      expect(screen.getByText(/0\s*m/i)).toBeInTheDocument();
    });

    it('should handle very large elevation values', () => {
      const highElevation: GPXTelemetry = {
        ...mockTelemetry,
        max_elevation: 8848, // Mount Everest
        elevation_gain: 5000,
      };

      render(<Step3Map {...defaultProps} telemetry={highElevation} />);

      expect(screen.getByText(/8848\s*m/i)).toBeInTheDocument();
      expect(screen.getByText(/5000\s*m/i)).toBeInTheDocument();
    });

    it('should handle very long distances', () => {
      const longDistance: GPXTelemetry = {
        ...mockTelemetry,
        distance_km: 1234.567,
      };

      render(<Step3Map {...defaultProps} telemetry={longDistance} />);

      // Should display with 1 decimal place
      expect(screen.getByText(/1234\.6\s*km/i)).toBeInTheDocument();
    });

    it('should handle single trackpoint', () => {
      const singlePoint = [mockTrackPoints[0]];

      render(<Step3Map {...defaultProps} trackPoints={singlePoint} />);

      // Should still render map (TripMap handles single point)
      expect(screen.getByTestId('trip-map-mock')).toBeInTheDocument();

      // Navigation should be enabled (can proceed with single point)
      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      expect(nextButton).toBeEnabled();
    });
  });

  describe('Responsive Design (T077)', () => {
    it('should render without errors on mobile viewport', () => {
      // Simulate mobile viewport
      window.innerWidth = 375;
      window.innerHeight = 667;

      render(<Step3Map {...defaultProps} />);

      expect(screen.getByText(/Visualiza tu ruta/i)).toBeInTheDocument();
      expect(screen.getByTestId('trip-map-mock')).toBeInTheDocument();
    });

    it('should render without errors on desktop viewport', () => {
      // Simulate desktop viewport
      window.innerWidth = 1920;
      window.innerHeight = 1080;

      render(<Step3Map {...defaultProps} />);

      expect(screen.getByText(/Visualiza tu ruta/i)).toBeInTheDocument();
      expect(screen.getByTestId('trip-map-mock')).toBeInTheDocument();
    });
  });
});
