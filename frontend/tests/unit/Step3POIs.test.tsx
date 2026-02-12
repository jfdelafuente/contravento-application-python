/**
 * Unit tests for Step3POIs component (Feature 017 - Phase 8 - US5)
 *
 * Simplified tests for POI management step
 *
 * Coverage:
 * - Component rendering
 * - Navigation buttons
 * - POI counter display
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Step3POIs } from '../../src/components/wizard/Step3POIs';
import type { GPXTelemetry } from '../../src/types/gpxWizard';
import type { TripDetailsFormData } from '../../src/schemas/tripDetailsSchema';
import type { POICreateInput } from '../../src/types/poi';
import { POIType } from '../../src/types/poi';

// Mock TripMap component to avoid Leaflet errors in tests
vi.mock('../../src/components/trips/TripMap', () => ({
  TripMap: () => <div data-testid="mock-trip-map">Mocked Map</div>,
}));

// Mock POIForm component
vi.mock('../../src/components/trips/POIForm', () => ({
  POIForm: () => <div data-testid="mock-poi-form">Mocked POI Form</div>,
}));

// Mock SkeletonLoader component
vi.mock('../../src/components/common/SkeletonLoader', () => ({
  default: () => <div data-testid="mock-skeleton">Loading...</div>,
}));

describe('Step3POIs Component', () => {
  const mockTelemetry: GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 1250,
    elevation_loss: 1100,
    max_elevation: 1850,
    min_elevation: 450,
    has_elevation: true,
    has_timestamps: false,
    start_date: null,
    end_date: null,
    total_time_minutes: null,
    moving_time_minutes: null,
    difficulty: 'very_difficult',
    suggested_title: 'test-route',
    trackpoints: null,
  };

  const mockTripDetails: TripDetailsFormData = {
    title: 'Ruta de prueba',
    description: 'Descripción de prueba con más de 50 caracteres para cumplir validación',
    start_date: '2024-06-01',
    end_date: '2024-06-05',
    privacy: 'public',
  };

  const mockPOI: POICreateInput = {
    name: 'Mirador del Valle',
    description: 'Vista panorámica',
    poi_type: POIType.VIEWPOINT,
    latitude: 40.4165,
    longitude: -3.7026,
    sequence: 0,
  };

  const defaultProps = {
    telemetry: mockTelemetry,
    tripDetails: mockTripDetails,
    initialPOIs: [],
    onNext: vi.fn(),
    onPrevious: vi.fn(),
    onCancel: vi.fn(),
  };

  describe('Component Rendering', () => {
    it('should render without crashing', () => {
      render(<Step3POIs {...defaultProps} />);
      expect(screen.getByText('Puntos de Interés')).toBeInTheDocument();
    });

    it('should display POI counter with zero POIs initially', () => {
      render(<Step3POIs {...defaultProps} />);
      expect(screen.getByText(/0\/6/i)).toBeInTheDocument();
    });

    it('should display POI counter with initial POIs', () => {
      const threePOIs: POICreateInput[] = Array.from({ length: 3 }, (_, i) => ({
        ...mockPOI,
        name: `POI ${i + 1}`,
        sequence: i,
      }));

      render(<Step3POIs {...defaultProps} initialPOIs={threePOIs} />);
      expect(screen.getByText(/3\/6/i)).toBeInTheDocument();
    });

    it('should show limit reached message at 6 POIs', () => {
      const sixPOIs: POICreateInput[] = Array.from({ length: 6 }, (_, i) => ({
        ...mockPOI,
        name: `POI ${i + 1}`,
        sequence: i,
      }));

      render(<Step3POIs {...defaultProps} initialPOIs={sixPOIs} />);
      expect(screen.getByText(/límite alcanzado/i)).toBeInTheDocument();
      expect(screen.getByText(/6\/6/i)).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should call onPrevious when back button is clicked', async () => {
      const user = userEvent.setup();
      const onPrevious = vi.fn();

      render(<Step3POIs {...defaultProps} onPrevious={onPrevious} />);

      const backButton = screen.getByRole('button', { name: /volver al paso anterior/i });
      await user.click(backButton);

      expect(onPrevious).toHaveBeenCalledOnce();
    });

    it('should call onNext when next button is clicked', async () => {
      const user = userEvent.setup();
      const onNext = vi.fn();

      render(<Step3POIs {...defaultProps} onNext={onNext} />);

      const nextButton = screen.getByRole('button', { name: /continuar a revisión/i });
      await user.click(nextButton);

      expect(onNext).toHaveBeenCalledOnce();
    });

    it('should call onNext with empty array when skip button is clicked', async () => {
      const user = userEvent.setup();
      const onNext = vi.fn();

      render(<Step3POIs {...defaultProps} onNext={onNext} />);

      const skipButton = screen.getByRole('button', { name: /omitir/i });
      await user.click(skipButton);

      expect(onNext).toHaveBeenCalledOnce();
      expect(onNext).toHaveBeenCalledWith([]);
    });
  });

  describe('POI Button State', () => {
    it('should enable add POI button when less than 6 POIs', () => {
      render(<Step3POIs {...defaultProps} />);

      const addButton = screen.getByRole('button', { name: /añadir punto de interés/i });
      expect(addButton).not.toBeDisabled();
    });

    it('should disable add POI button at 6 POIs', () => {
      const sixPOIs: POICreateInput[] = Array.from({ length: 6 }, (_, i) => ({
        ...mockPOI,
        name: `POI ${i + 1}`,
        sequence: i,
      }));

      render(<Step3POIs {...defaultProps} initialPOIs={sixPOIs} />);

      const addButton = screen.getByRole('button', { name: /límite alcanzado/i });
      expect(addButton).toBeDisabled();
    });
  });

  describe('Props Validation', () => {
    it('should accept all required props', () => {
      expect(() => render(<Step3POIs {...defaultProps} />)).not.toThrow();
    });

    it('should render with custom initial POIs', () => {
      const customPOIs: POICreateInput[] = [
        { ...mockPOI, name: 'Custom POI 1', sequence: 0 },
        { ...mockPOI, name: 'Custom POI 2', sequence: 1 },
      ];

      render(<Step3POIs {...defaultProps} initialPOIs={customPOIs} />);
      expect(screen.getByText(/2\/6/i)).toBeInTheDocument();
    });
  });
});
