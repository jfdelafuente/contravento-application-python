/**
 * GPXWizard Container Component Unit Tests
 *
 * Tests for main GPS Trip Creation Wizard container.
 * Tests multi-step navigation, state management, and wizard completion.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T040
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { GPXWizard } from '../../src/components/wizard/GPXWizard';
import * as gpxWizardService from '../../src/services/gpxWizardService';
import * as tripService from '../../src/services/tripService';
import * as poiService from '../../src/services/poiService';

// Mock gpxWizardService
vi.mock('../../src/services/gpxWizardService', () => ({
  analyzeGPXFile: vi.fn(),
  formatDifficulty: vi.fn((difficulty: string) => {
    const map: Record<string, string> = {
      easy: 'Fácil',
      moderate: 'Moderada',
      difficult: 'Difícil',
      very_difficult: 'Muy Difícil',
    };
    return map[difficulty] || difficulty;
  }),
  getDifficultyColor: vi.fn(() => '#10b981'),
  GPXAnalysisError: class GPXAnalysisError extends Error {
    code: string;
    field?: string;
    constructor(code: string, message: string, field?: string) {
      super(message);
      this.name = 'GPXAnalysisError';
      this.code = code;
      this.field = field;
    }
  },
}));

// Mock tripService
vi.mock('../../src/services/tripService', () => ({
  createTripWithGPX: vi.fn(),
}));

// Mock poiService
vi.mock('../../src/services/poiService', () => ({
  createPOI: vi.fn(),
}));

// Mock Step components
vi.mock('../../src/components/wizard/Step1Upload', () => ({
  Step1Upload: ({ onComplete }: any) => (
    <div data-testid="step1-upload">
      <h2>Sube tu archivo GPX</h2>
      <button onClick={() => onComplete(new File(['content'], 'route.gpx'), {
        distance_km: 42.5,
        elevation_gain: 850,
        elevation_loss: 820,
        max_elevation: 1250,
        min_elevation: 450,
        has_elevation: true,
        difficulty: 'moderate',
      })}>
        Mock Upload
      </button>
    </div>
  ),
}));

vi.mock('../../src/components/wizard/Step2Details', () => ({
  Step2Details: ({ onNext, onPrevious }: any) => (
    <div data-testid="step2-details">
      <h2>Detalles del Viaje</h2>
      <button onClick={onPrevious}>Anterior</button>
      <button onClick={() => onNext({ title: 'Test', description: 'Test desc', start_date: '2024-01-01', end_date: '2024-01-05', privacy: 'public' })}>
        Siguiente
      </button>
    </div>
  ),
}));

vi.mock('../../src/components/trips/GPXWizard/Step3Map', () => ({
  Step3Map: ({ onBack, onNext }: any) => (
    <div data-testid="step3-map">
      <h2>Mapa</h2>
      <button onClick={onBack}>Anterior</button>
      <button onClick={onNext}>Siguiente</button>
    </div>
  ),
}));

vi.mock('../../src/components/wizard/Step3POIs', () => ({
  Step3POIs: ({ onNext, onPrevious }: any) => (
    <div data-testid="step3-pois">
      <h2>Puntos de Interés</h2>
      <button onClick={onPrevious}>Anterior</button>
      <button onClick={() => onNext([])}>Siguiente</button>
    </div>
  ),
}));

vi.mock('../../src/components/wizard/Step4Review', () => ({
  Step4Review: ({ onPublish, onPrevious }: any) => (
    <div data-testid="step4-review">
      <h2>Revisar y Publicar</h2>
      <button onClick={onPrevious}>Anterior</button>
      <button onClick={onPublish}>Publicar Viaje</button>
    </div>
  ),
}));

describe('GPXWizard (T040)', () => {
  const mockOnSuccess = vi.fn();
  const mockOnError = vi.fn();
  const mockOnCancel = vi.fn();

  const mockAnalyzeGPXFile = vi.mocked(gpxWizardService.analyzeGPXFile);
  const mockCreateTripWithGPX = vi.mocked(tripService.createTripWithGPX);
  const mockCreatePOI = vi.mocked(poiService.createPOI);

  const mockTelemetry: gpxWizardService.GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 850,
    elevation_loss: 820,
    max_elevation: 1250,
    min_elevation: 450,
    has_elevation: true,
    difficulty: 'moderate',
  };

  const mockTrip = {
    trip_id: 'test-trip-id-123',
    title: 'Test Trip',
    description: 'Test description',
    start_date: '2024-01-01',
    end_date: '2024-01-05',
    privacy: 'public' as const,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockAnalyzeGPXFile.mockResolvedValue(mockTelemetry);
    mockCreateTripWithGPX.mockResolvedValue(mockTrip as any);
    mockCreatePOI.mockResolvedValue({ poi_id: 'test-poi-id' } as any);
  });

  describe('Initial Render', () => {
    it('should render wizard title', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      expect(screen.getByText(/crear viaje desde gpx/i)).toBeInTheDocument();
    });

    it('should show step indicator', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      expect(screen.getByRole('navigation', { name: /progreso del asistente/i })).toBeInTheDocument();
    });

    it('should show cancel button', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
    });

    it('should show step 1 upload component initially', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      expect(screen.getByTestId('step1-upload')).toBeInTheDocument();
    });
  });

  describe('Step Indicator', () => {
    it('should display all steps in indicator', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      expect(screen.getByText(/archivo gpx/i)).toBeInTheDocument();
      expect(screen.getByText(/detalles del viaje/i)).toBeInTheDocument();
      expect(screen.getByText(/^mapa$/i)).toBeInTheDocument();
      expect(screen.getByText(/puntos de interés/i)).toBeInTheDocument();
      expect(screen.getByText(/revisar y publicar/i)).toBeInTheDocument();
    });

    it('should highlight current step', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      const step1 = screen.getByText(/archivo gpx/i).closest('.wizard-step');
      expect(step1).toHaveClass('wizard-step--active');
    });

    it('should show completed steps with checkmark', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Complete step 1 by clicking mock upload button
      const uploadButton = screen.getByText('Mock Upload');
      fireEvent.click(uploadButton);

      // Wait for step 2 to render
      await waitFor(() => {
        expect(screen.getByTestId('step2-details')).toBeInTheDocument();
      });

      // Step 1 should be marked as complete
      const step1 = screen.getByText(/archivo gpx/i).closest('.wizard-step');
      expect(step1).toHaveClass('wizard-step--completed');
    });

    it('should show progress percentage', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Should show 0% on first step
      expect(screen.getByText(/0%/i)).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should advance to Step 2 after completing Step 1', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Initially on step 1
      expect(screen.getByTestId('step1-upload')).toBeInTheDocument();

      // Complete step 1
      const uploadButton = screen.getByText('Mock Upload');
      fireEvent.click(uploadButton);

      // Should advance to step 2
      await waitFor(() => {
        expect(screen.getByTestId('step2-details')).toBeInTheDocument();
      });
    });

    it('should navigate through all wizard steps', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Step 1: Upload
      expect(screen.getByTestId('step1-upload')).toBeInTheDocument();
      fireEvent.click(screen.getByText('Mock Upload'));

      // Step 2: Details
      await waitFor(() => expect(screen.getByTestId('step2-details')).toBeInTheDocument());
      fireEvent.click(screen.getByText('Siguiente'));

      // Step 3: Map
      await waitFor(() => expect(screen.getByTestId('step3-map')).toBeInTheDocument());
      fireEvent.click(screen.getByText('Siguiente'));

      // Step 4: POIs
      await waitFor(() => expect(screen.getByTestId('step3-pois')).toBeInTheDocument());
      fireEvent.click(screen.getByText('Siguiente'));

      // Step 5: Review
      await waitFor(() => expect(screen.getByTestId('step4-review')).toBeInTheDocument());
    });

    it('should navigate back to previous step', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Navigate to Step 2
      fireEvent.click(screen.getByText('Mock Upload'));
      await waitFor(() => expect(screen.getByTestId('step2-details')).toBeInTheDocument());

      // Go back to Step 1
      fireEvent.click(screen.getByText('Anterior'));
      await waitFor(() => expect(screen.getByTestId('step1-upload')).toBeInTheDocument());
    });
  });

  describe('Cancel Functionality', () => {
    it('should call onCancel when cancel button clicked', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should show confirmation dialog before canceling with data', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Complete step 1 (wizard has data)
      fireEvent.click(screen.getByText('Mock Upload'));
      await waitFor(() => expect(screen.getByTestId('step2-details')).toBeInTheDocument());

      // Click cancel
      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      // Should show confirmation dialog
      expect(screen.getByText(/¿seguro que quieres cancelar/i)).toBeInTheDocument();
    });

    it('should not call onCancel if user declines confirmation', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Complete step 1
      fireEvent.click(screen.getByText('Mock Upload'));
      await waitFor(() => expect(screen.getByTestId('step2-details')).toBeInTheDocument());

      // Click cancel
      fireEvent.click(screen.getByRole('button', { name: /cancelar/i }));

      // Click "No" in confirmation
      const noButton = screen.getByRole('button', { name: /no, continuar/i });
      fireEvent.click(noButton);

      expect(mockOnCancel).not.toHaveBeenCalled();
    });
  });

  describe('Wizard Completion', () => {
    it('should show "Publicar" button on last step', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Navigate through all steps to reach Review
      fireEvent.click(screen.getByText('Mock Upload'));
      await waitFor(() => expect(screen.getByTestId('step2-details')).toBeInTheDocument());

      fireEvent.click(screen.getByText('Siguiente'));
      await waitFor(() => expect(screen.getByTestId('step3-map')).toBeInTheDocument());

      fireEvent.click(screen.getByText('Siguiente'));
      await waitFor(() => expect(screen.getByTestId('step3-pois')).toBeInTheDocument());

      fireEvent.click(screen.getByText('Siguiente'));
      await waitFor(() => expect(screen.getByTestId('step4-review')).toBeInTheDocument());

      // Should show "Publicar" button
      expect(screen.getByRole('button', { name: /publicar viaje/i })).toBeInTheDocument();
    });

    it('should call onSuccess when publish clicked', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Navigate through all steps
      fireEvent.click(screen.getByText('Mock Upload'));
      await waitFor(() => expect(screen.getByTestId('step2-details')).toBeInTheDocument());

      fireEvent.click(screen.getByText('Siguiente'));
      await waitFor(() => expect(screen.getByTestId('step3-map')).toBeInTheDocument());

      fireEvent.click(screen.getByText('Siguiente'));
      await waitFor(() => expect(screen.getByTestId('step3-pois')).toBeInTheDocument());

      fireEvent.click(screen.getByText('Siguiente'));
      await waitFor(() => expect(screen.getByTestId('step4-review')).toBeInTheDocument());

      // Click publish
      const publishButton = screen.getByRole('button', { name: /publicar viaje/i });
      fireEvent.click(publishButton);

      // Should call onSuccess with created trip
      await waitFor(() => {
        expect(mockOnSuccess).toHaveBeenCalledWith(
          expect.objectContaining({
            trip_id: 'test-trip-id-123',
          })
        );
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA landmarks', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      expect(screen.getByRole('navigation', { name: /progreso del asistente/i })).toBeInTheDocument();
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    it('should announce step changes to screen readers', async () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Should have aria-live region
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      expect(liveRegion).toHaveTextContent('Paso 1 de 5');

      // Navigate to next step
      fireEvent.click(screen.getByText('Mock Upload'));
      await waitFor(() => expect(screen.getByTestId('step2-details')).toBeInTheDocument());

      // Should update step announcement
      expect(liveRegion).toHaveTextContent('Paso 2 de 5');
    });

    it('should have keyboard-accessible navigation', () => {
      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });

      // Should be focusable
      cancelButton.focus();
      expect(cancelButton).toHaveFocus();
    });
  });

  describe('Responsive Design', () => {
    it('should render mobile-friendly layout', () => {
      // Simulate mobile viewport
      global.innerWidth = 375;
      global.dispatchEvent(new Event('resize'));

      render(<GPXWizard onSuccess={mockOnSuccess} onError={mockOnError} onCancel={mockOnCancel} />);

      // Wizard should still be functional
      expect(screen.getByText(/crear viaje desde gpx/i)).toBeInTheDocument();
    });
  });
});
