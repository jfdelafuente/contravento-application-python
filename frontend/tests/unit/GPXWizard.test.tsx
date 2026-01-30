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

describe('GPXWizard (T040)', () => {
  const mockOnComplete = vi.fn();
  const mockOnCancel = vi.fn();

  const mockAnalyzeGPXFile = vi.mocked(gpxWizardService.analyzeGPXFile);

  const mockTelemetry: gpxWizardService.GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 850,
    elevation_loss: 820,
    max_elevation: 1250,
    min_elevation: 450,
    has_elevation: true,
    difficulty: 'moderate',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockAnalyzeGPXFile.mockResolvedValue(mockTelemetry);
  });

  describe('Initial Render', () => {
    it('should render wizard title', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      expect(screen.getByText(/crear viaje desde gpx/i)).toBeInTheDocument();
    });

    it('should show step indicator', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      expect(screen.getByRole('navigation', { name: /progreso del asistente/i })).toBeInTheDocument();
    });

    it('should render Step 1 (Upload) initially', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      expect(screen.getByText(/sube tu archivo gpx/i)).toBeInTheDocument();
    });

    it('should show cancel button', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
    });

    it('should not show previous button on first step', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      expect(screen.queryByRole('button', { name: /anterior/i })).not.toBeInTheDocument();
    });

    it('should show next button disabled on first step', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      expect(nextButton).toBeInTheDocument();
      expect(nextButton).toBeDisabled();
    });
  });

  describe('Step Indicator', () => {
    it('should display all steps in indicator', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      expect(screen.getByText(/archivo gpx/i)).toBeInTheDocument();
      expect(screen.getByText(/detalles del viaje/i)).toBeInTheDocument();
      expect(screen.getByText(/revisar y publicar/i)).toBeInTheDocument();
    });

    it('should highlight current step', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      const step1 = screen.getByText(/archivo gpx/i).closest('.wizard-step');
      expect(step1).toHaveClass('wizard-step--active');
    });

    it('should show completed steps with checkmark', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Upload file to complete step 1
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /siguiente/i })).not.toBeDisabled();
      });

      // Go to next step
      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      fireEvent.click(nextButton);

      // Step 1 should be marked as complete
      const step1 = screen.getByText(/archivo gpx/i).closest('.wizard-step');
      expect(step1).toHaveClass('wizard-step--completed');
    });

    it('should show progress percentage', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Should show 0% on first step
      expect(screen.getByText(/0%/i)).toBeInTheDocument();
    });
  });

  describe('Navigation', () => {
    it('should enable next button after completing Step 1', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      expect(nextButton).toBeDisabled();

      // Upload and analyze file
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(nextButton).not.toBeDisabled();
      });
    });

    it('should advance to Step 2 when next button clicked', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Complete Step 1
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /siguiente/i })).not.toBeDisabled();
      });

      // Click next
      const nextButton = screen.getByRole('button', { name: /siguiente/i });
      fireEvent.click(nextButton);

      // Should show Step 2
      expect(screen.getByText(/detalles del viaje/i)).toBeInTheDocument();
    });

    it('should show previous button on Step 2', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Navigate to Step 2
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /siguiente/i })).not.toBeDisabled();
      });

      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));

      // Previous button should be visible
      expect(screen.getByRole('button', { name: /anterior/i })).toBeInTheDocument();
    });

    it('should go back to previous step when previous button clicked', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Navigate to Step 2
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /siguiente/i })).not.toBeDisabled();
      });

      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));

      // Go back
      const prevButton = screen.getByRole('button', { name: /anterior/i });
      fireEvent.click(prevButton);

      // Should be back on Step 1
      expect(screen.getByText(/sube tu archivo gpx/i)).toBeInTheDocument();
    });

    it('should preserve file data when navigating back', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Upload file
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();
      });

      // Go to Step 2
      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));

      // Go back to Step 1
      fireEvent.click(screen.getByRole('button', { name: /anterior/i }));

      // Telemetry should still be visible
      expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();
    });
  });

  describe('Cancel Functionality', () => {
    it('should call onCancel when cancel button clicked', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should show confirmation dialog before canceling with data', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Upload file (wizard has data)
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();
      });

      // Click cancel
      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      // Should show confirmation dialog
      expect(screen.getByText(/¿seguro que quieres cancelar/i)).toBeInTheDocument();
    });

    it('should not call onCancel if user declines confirmation', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Upload file
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();
      });

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
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Complete Step 1 and navigate to last step
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /siguiente/i })).not.toBeDisabled();
      });

      // Navigate to last step (Step 2 in this case)
      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));
      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));

      // Should show "Publicar" instead of "Siguiente"
      expect(screen.getByRole('button', { name: /publicar viaje/i })).toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /siguiente/i })).not.toBeInTheDocument();
    });

    it('should call onComplete with wizard data when publish clicked', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Complete wizard flow
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /siguiente/i })).not.toBeDisabled();
      });

      // Navigate to last step
      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));
      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));

      // Click publish
      const publishButton = screen.getByRole('button', { name: /publicar viaje/i });
      fireEvent.click(publishButton);

      // Should call onComplete with file and telemetry
      expect(mockOnComplete).toHaveBeenCalledWith(
        expect.objectContaining({
          file: mockFile,
          telemetry: mockTelemetry,
        })
      );
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA landmarks', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      expect(screen.getByRole('navigation', { name: /progreso del asistente/i })).toBeInTheDocument();
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    it('should announce step changes to screen readers', async () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Complete Step 1 and navigate
      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /siguiente/i })).not.toBeDisabled();
      });

      fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));

      // Should have aria-live region announcing step change
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
    });

    it('should have keyboard-accessible navigation', () => {
      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

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

      render(<GPXWizard onComplete={mockOnComplete} onCancel={mockOnCancel} />);

      // Wizard should still be functional
      expect(screen.getByText(/crear viaje desde gpx/i)).toBeInTheDocument();
    });
  });
});
