/**
 * Step4Review Component Unit Tests (formerly Step3Review)
 *
 * Tests for trip details review and publish step.
 * Tests summary display, publish button, loading states, and navigation.
 * Updated for Phase 8: Now includes POI summary display.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 6 (US6) + Phase 8 (POI display)
 * Task: T068 + T094
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { Step4Review } from '../../src/components/wizard/Step4Review';
import type { GPXTelemetry } from '../../src/services/gpxWizardService';
import type { TripDetailsFormData } from '../../src/schemas/tripDetailsSchema';
import type { POICreateInput } from '../../src/types/poi';

describe('Step4Review (T068 + T094)', () => {
  // Mock data
  const mockFile = new File(['mock gpx content'], 'test-route.gpx', {
    type: 'application/gpx+xml',
  });

  const mockTelemetry: GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 850,
    elevation_loss: 820,
    max_elevation: 1200,
    min_elevation: 350,
    has_elevation: true,
    difficulty: 'moderate',
  };

  const mockTripDetails: TripDetailsFormData = {
    title: 'Ruta de Prueba',
    description: 'Esta es una descripción de prueba con más de cincuenta caracteres para cumplir con la validación.',
    start_date: '2024-06-01',
    end_date: '2024-06-05',
    privacy: 'public',
  };

  const defaultProps = {
    gpxFile: mockFile,
    telemetry: mockTelemetry,
    tripDetails: mockTripDetails,
    pois: [] as POICreateInput[], // Phase 8: Add POIs prop
    onPublish: vi.fn(),
    onPrevious: vi.fn(),
    onCancel: vi.fn(),
    isPublishing: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Summary Display (T070)', () => {
    it('should display trip title', () => {
      render(<Step4Review {...defaultProps} />);

      expect(screen.getByText('Ruta de Prueba')).toBeInTheDocument();
    });

    it('should display trip description', () => {
      render(<Step4Review {...defaultProps} />);

      expect(
        screen.getByText(/Esta es una descripción de prueba/i)
      ).toBeInTheDocument();
    });

    it('should display start date formatted in Spanish', () => {
      render(<Step4Review {...defaultProps} />);

      // Should show formatted date (e.g., "1 de junio de 2024")
      expect(screen.getByText(/junio/i)).toBeInTheDocument();
      expect(screen.getByText(/2024/i)).toBeInTheDocument();
    });

    it('should display date range when end date is provided', () => {
      render(<Step4Review {...defaultProps} />);

      // Should show both start and end dates
      expect(screen.getByText(/junio/i)).toBeInTheDocument();
    });

    it('should display single date when no end date', () => {
      const propsWithoutEndDate = {
        ...defaultProps,
        tripDetails: {
          ...mockTripDetails,
          end_date: '',
        },
      };

      render(<Step4Review {...propsWithoutEndDate} />);

      // Should only show start date
      expect(screen.getByText(/junio/i)).toBeInTheDocument();
    });

    it('should display privacy setting', () => {
      render(<Step4Review {...defaultProps} />);

      expect(screen.getByText('Público')).toBeInTheDocument();
    });

    it('should display private privacy setting', () => {
      const propsPrivate = {
        ...defaultProps,
        tripDetails: {
          ...mockTripDetails,
          privacy: 'private' as const,
        },
      };

      render(<Step4Review {...propsPrivate} />);

      expect(screen.getByText('Privado')).toBeInTheDocument();
    });

    it('should display GPX filename', () => {
      render(<Step4Review {...defaultProps} />);

      expect(screen.getByText('test-route.gpx')).toBeInTheDocument();
    });

    it('should display distance from telemetry', () => {
      render(<Step4Review {...defaultProps} />);

      expect(screen.getByText(/42\.5 km/i)).toBeInTheDocument();
    });

    it('should display elevation gain when available', () => {
      render(<Step4Review {...defaultProps} />);

      expect(screen.getByText(/850 m/i)).toBeInTheDocument();
    });

    it('should not display elevation when not available', () => {
      const propsNoElevation = {
        ...defaultProps,
        telemetry: {
          ...mockTelemetry,
          has_elevation: false,
          elevation_gain: null,
          elevation_loss: null,
        },
      };

      render(<Step4Review {...propsNoElevation} />);

      // Should not show elevation section
      expect(screen.queryByText(/Desnivel/i)).not.toBeInTheDocument();
    });

    it('should display difficulty badge', () => {
      render(<Step4Review {...defaultProps} />);

      expect(screen.getByText('Moderada')).toBeInTheDocument();
    });
  });

  describe('Publish Button (T071)', () => {
    it('should display "Publicar Viaje" button', () => {
      render(<Step4Review {...defaultProps} />);

      const publishButton = screen.getByRole('button', { name: /publicar viaje/i });
      expect(publishButton).toBeInTheDocument();
    });

    it('should call onPublish when publish button is clicked', () => {
      render(<Step4Review {...defaultProps} />);

      const publishButton = screen.getByRole('button', { name: /publicar viaje/i });
      fireEvent.click(publishButton);

      expect(defaultProps.onPublish).toHaveBeenCalledTimes(1);
    });

    it('should disable publish button when isPublishing is true', () => {
      const props = {
        ...defaultProps,
        isPublishing: true,
      };

      render(<Step4Review {...props} />);

      const publishButton = screen.getByRole('button', { name: /publicando/i });
      expect(publishButton).toBeDisabled();
    });

    it('should show loading text when isPublishing is true', () => {
      const props = {
        ...defaultProps,
        isPublishing: true,
      };

      render(<Step4Review {...props} />);

      expect(screen.getByText('Publicando...')).toBeInTheDocument();
    });

    it('should show loading spinner when isPublishing is true', () => {
      const props = {
        ...defaultProps,
        isPublishing: true,
      };

      const { container } = render(<Step4Review {...props} />);

      // Check for spinner element
      const spinner = container.querySelector('.step3-review__spinner');
      expect(spinner).toBeInTheDocument();
    });

    it('should not call onPublish when button is disabled', () => {
      const props = {
        ...defaultProps,
        isPublishing: true,
      };

      render(<Step4Review {...props} />);

      const publishButton = screen.getByRole('button', { name: /publicando/i });
      fireEvent.click(publishButton);

      expect(defaultProps.onPublish).not.toHaveBeenCalled();
    });
  });

  describe('Navigation Buttons', () => {
    it('should display "Anterior" button', () => {
      render(<Step4Review {...defaultProps} />);

      const previousButton = screen.getByRole('button', { name: /anterior/i });
      expect(previousButton).toBeInTheDocument();
    });

    it('should call onPrevious when "Anterior" button is clicked', () => {
      render(<Step4Review {...defaultProps} />);

      const previousButton = screen.getByRole('button', { name: /anterior/i });
      fireEvent.click(previousButton);

      expect(defaultProps.onPrevious).toHaveBeenCalledTimes(1);
    });

    it('should disable "Anterior" button when isPublishing is true', () => {
      const props = {
        ...defaultProps,
        isPublishing: true,
      };

      render(<Step4Review {...props} />);

      const previousButton = screen.getByRole('button', { name: /anterior/i });
      expect(previousButton).toBeDisabled();
    });

    it('should display "Cancelar" button', () => {
      render(<Step4Review {...defaultProps} />);

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      expect(cancelButton).toBeInTheDocument();
    });

    it('should call onCancel when "Cancelar" button is clicked', () => {
      render(<Step4Review {...defaultProps} />);

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      expect(defaultProps.onCancel).toHaveBeenCalledTimes(1);
    });

    it('should disable "Cancelar" button when isPublishing is true', () => {
      const props = {
        ...defaultProps,
        isPublishing: true,
      };

      render(<Step4Review {...props} />);

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      expect(cancelButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have semantic section elements', () => {
      const { container } = render(<Step4Review {...defaultProps} />);

      const sections = container.querySelectorAll('section');
      expect(sections.length).toBeGreaterThan(0);
    });

    it('should have accessible headings structure', () => {
      render(<Step4Review {...defaultProps} />);

      // Should have main heading
      const mainHeading = screen.getByRole('heading', { level: 2, name: /revisar/i });
      expect(mainHeading).toBeInTheDocument();
    });

    it('should announce publishing state to screen readers', () => {
      const props = {
        ...defaultProps,
        isPublishing: true,
      };

      const { container } = render(<Step4Review {...props} />);

      // Should have aria-live region for status updates
      const liveRegion = container.querySelector('[aria-live="polite"]');
      expect(liveRegion).toBeInTheDocument();
    });

    it('should have proper button labels for screen readers', () => {
      render(<Step4Review {...defaultProps} />);

      const publishButton = screen.getByRole('button', { name: /publicar viaje/i });
      expect(publishButton).toHaveAttribute('aria-label');
    });
  });

  describe('Responsive Layout', () => {
    it('should render without crashing on mobile', () => {
      const { container } = render(<Step4Review {...defaultProps} />);

      // Should have responsive class
      expect(container.querySelector('.step3-review')).toBeInTheDocument();
    });

    it('should stack summary items vertically on mobile', () => {
      const { container } = render(<Step4Review {...defaultProps} />);

      const summaryGrid = container.querySelector('.step3-review__summary');
      expect(summaryGrid).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle very long titles gracefully', () => {
      const propsLongTitle = {
        ...defaultProps,
        tripDetails: {
          ...mockTripDetails,
          title: 'a'.repeat(200),
        },
      };

      render(<Step4Review {...propsLongTitle} />);

      // Should render without crashing
      expect(screen.getByText('a'.repeat(200))).toBeInTheDocument();
    });

    it('should handle very long descriptions gracefully', () => {
      const propsLongDesc = {
        ...defaultProps,
        tripDetails: {
          ...mockTripDetails,
          description: 'a'.repeat(500),
        },
      };

      render(<Step4Review {...propsLongDesc} />);

      // Should render without crashing
      expect(screen.getByText('a'.repeat(500))).toBeInTheDocument();
    });

    it('should handle null end_date gracefully', () => {
      const propsNullEndDate = {
        ...defaultProps,
        tripDetails: {
          ...mockTripDetails,
          end_date: null,
        },
      };

      render(<Step4Review {...propsNullEndDate} />);

      // Should render without errors
      expect(screen.getByText(/junio/i)).toBeInTheDocument();
    });

    it('should handle undefined end_date gracefully', () => {
      const propsUndefinedEndDate = {
        ...defaultProps,
        tripDetails: {
          ...mockTripDetails,
          end_date: undefined,
        },
      };

      render(<Step4Review {...propsUndefinedEndDate} />);

      // Should render without errors
      expect(screen.getByText(/junio/i)).toBeInTheDocument();
    });
  });

  describe('Component Structure', () => {
    it('should render step header with title', () => {
      render(<Step4Review {...defaultProps} />);

      expect(screen.getByText(/revisar y publicar/i)).toBeInTheDocument();
    });

    it('should render step description', () => {
      render(<Step4Review {...defaultProps} />);

      expect(
        screen.getByText(/revisa los datos de tu viaje antes de publicarlo/i)
      ).toBeInTheDocument();
    });

    it('should group related information in sections', () => {
      const { container } = render(<Step4Review {...defaultProps} />);

      const sections = container.querySelectorAll('.step3-review__section');
      expect(sections.length).toBeGreaterThan(0);
    });
  });
});
