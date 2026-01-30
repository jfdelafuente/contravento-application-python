/**
 * Step1Upload Component Unit Tests
 *
 * Tests for wizard Step 1 (GPX Upload & Analysis) component.
 * Tests file upload flow, analysis integration, and telemetry preview.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T043
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { Step1Upload } from '../../src/components/wizard/Step1Upload';
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

describe('Step1Upload (T043)', () => {
  const mockOnComplete = vi.fn();
  const mockOnFileRemove = vi.fn();

  const mockAnalyzeGPXFile = vi.mocked(gpxWizardService.analyzeGPXFile);

  const mockTelemetryWithElevation: gpxWizardService.GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 850,
    elevation_loss: 820,
    max_elevation: 1250,
    min_elevation: 450,
    has_elevation: true,
    difficulty: 'moderate',
  };

  const mockTelemetryWithoutElevation: gpxWizardService.GPXTelemetry = {
    distance_km: 15.3,
    elevation_gain: null,
    elevation_loss: null,
    max_elevation: null,
    min_elevation: null,
    has_elevation: false,
    difficulty: 'easy',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Render', () => {
    it('should render upload area when no file selected', () => {
      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      expect(screen.getByText(/arrastra tu archivo gpx/i)).toBeInTheDocument();
    });

    it('should render step title', () => {
      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      expect(screen.getByText(/sube tu archivo gpx/i)).toBeInTheDocument();
    });

    it('should not show telemetry preview initially', () => {
      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      expect(screen.queryByText(/distancia total/i)).not.toBeInTheDocument();
    });
  });

  describe('File Upload Flow', () => {
    it('should show loading state during analysis', async () => {
      mockAnalyzeGPXFile.mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(mockTelemetryWithElevation), 100);
          })
      );

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['gpx content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText(/analizando archivo/i)).toBeInTheDocument();
      });
    });

    it('should call onComplete with file and telemetry on success', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith(mockFile, mockTelemetryWithElevation);
      });
    });

    it('should display error message on analysis failure', async () => {
      const error = new gpxWizardService.GPXAnalysisError(
        'INVALID_GPX_FILE',
        'No se pudo procesar el archivo GPX'
      );
      mockAnalyzeGPXFile.mockRejectedValue(error);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/no se pudo procesar el archivo gpx/i)).toBeInTheDocument();
      });

      expect(mockOnComplete).not.toHaveBeenCalled();
    });

    it('should not call onComplete on analysis error', async () => {
      mockAnalyzeGPXFile.mockRejectedValue(
        new gpxWizardService.GPXAnalysisError('INVALID_FILE_TYPE', 'Invalid file type')
      );

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'document.pdf', { type: 'application/pdf' });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(mockOnComplete).not.toHaveBeenCalled();
      });
    });
  });

  describe('Telemetry Preview - With Elevation', () => {
    it('should display distance in telemetry preview', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();
      });
    });

    it('should display elevation gain', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/850\s*m/i)).toBeInTheDocument();
      });
    });

    it('should display difficulty level', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/moderada/i)).toBeInTheDocument();
      });
    });

    it('should display max elevation', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/1250\s*m/i)).toBeInTheDocument();
      });
    });
  });

  describe('Telemetry Preview - Without Elevation', () => {
    it('should display distance even without elevation', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithoutElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'flat_route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/15\.3\s*km/i)).toBeInTheDocument();
      });
    });

    it('should show placeholder for missing elevation data', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithoutElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'flat_route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/sin datos de elevación/i)).toBeInTheDocument();
      });
    });

    it('should still display difficulty without elevation', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithoutElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'flat_route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/fácil/i)).toBeInTheDocument();
      });
    });
  });

  describe('File Removal', () => {
    it('should call onFileRemove when remove button clicked', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /eliminar/i })).toBeInTheDocument();
      });

      const removeButton = screen.getByRole('button', { name: /eliminar/i });
      fireEvent.click(removeButton);

      expect(mockOnFileRemove).toHaveBeenCalledTimes(1);
    });

    it('should clear telemetry preview on file removal', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { rerender } = render(
        <Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />
      );

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();
      });

      // Simulate file removal by parent component
      rerender(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      expect(screen.queryByText(/42\.5\s*km/i)).not.toBeInTheDocument();
    });
  });

  describe('Retry Functionality', () => {
    it('should show retry button on error', async () => {
      mockAnalyzeGPXFile.mockRejectedValue(
        new gpxWizardService.GPXAnalysisError('PROCESSING_TIMEOUT', 'Timeout error')
      );

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
      });
    });

    it('should retry analysis when retry button clicked', async () => {
      // First attempt fails
      mockAnalyzeGPXFile
        .mockRejectedValueOnce(
          new gpxWizardService.GPXAnalysisError('PROCESSING_TIMEOUT', 'Timeout error')
        )
        .mockResolvedValueOnce(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /reintentar/i });
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith(mockFile, mockTelemetryWithElevation);
      });

      expect(mockAnalyzeGPXFile).toHaveBeenCalledTimes(2);
    });
  });

  describe('Accessibility', () => {
    it('should have accessible telemetry preview region', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        const telemetrySection = screen.getByRole('region', { name: /información del recorrido/i });
        expect(telemetrySection).toBeInTheDocument();
      });
    });

    it('should announce analysis completion to screen readers', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        const statusElement = screen.getByRole('status');
        expect(statusElement).toHaveAttribute('aria-live', 'polite');
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid file changes', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const file1 = new File(['content1'], 'route1.gpx', { type: 'application/gpx+xml' });
      const file2 = new File(['content2'], 'route2.gpx', { type: 'application/gpx+xml' });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });

      // Upload file 1
      fireEvent.change(input, { target: { files: [file1] } });

      // Quickly upload file 2
      fireEvent.change(input, { target: { files: [file2] } });

      // Should only call onComplete with file2
      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenLastCalledWith(file2, mockTelemetryWithElevation);
      });
    });

    it('should handle zero distance gracefully', async () => {
      const zeroDistanceTelemetry = {
        ...mockTelemetryWithoutElevation,
        distance_km: 0,
      };

      mockAnalyzeGPXFile.mockResolvedValue(zeroDistanceTelemetry);

      render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'point.gpx', { type: 'application/gpx+xml' });

      const input = screen.getByLabelText(/arrastra tu archivo gpx/i, { selector: 'input' });
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/0\s*km/i)).toBeInTheDocument();
      });
    });
  });
});
