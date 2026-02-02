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

// Mock MapPreview component (Leaflet doesn't work in jsdom)
vi.mock('../../src/components/wizard/MapPreview', () => ({
  MapPreview: ({ title }: { title?: string }) => (
    <div data-testid="map-preview" aria-label={`Mapa de ${title || 'ruta'}`}>
      <p>Mapa Preview</p>
    </div>
  ),
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
    has_timestamps: false,
    start_date: null,
    end_date: null,
    difficulty: 'moderate',
    suggested_title: 'Ruta en Bicicleta de 42.5 km',
    trackpoints: [
      { latitude: 40.4168, longitude: -3.7038, elevation: 650, distance_km: 0 },
      { latitude: 40.4269, longitude: -3.7138, elevation: 700, distance_km: 42.5 },
    ],
  };

  const mockTelemetryWithoutElevation: gpxWizardService.GPXTelemetry = {
    distance_km: 15.3,
    elevation_gain: null,
    elevation_loss: null,
    max_elevation: null,
    min_elevation: null,
    has_elevation: false,
    has_timestamps: false,
    start_date: null,
    end_date: null,
    difficulty: 'easy',
    suggested_title: 'Ruta en Bicicleta de 15.3 km',
    trackpoints: [
      { latitude: 41.3874, longitude: 2.1686, elevation: null, distance_km: 0 },
      { latitude: 41.3974, longitude: 2.1786, elevation: null, distance_km: 15.3 },
    ],
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

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['gpx content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      // Should show loading state
      await waitFor(() => {
        expect(screen.getByText(/analizando archivo/i)).toBeInTheDocument();
      });
    });

    it('should call onComplete with file and telemetry on success', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
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

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
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

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'document.pdf', { type: 'application/pdf' });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(mockOnComplete).not.toHaveBeenCalled();
      });
    });
  });

  describe('Telemetry Preview - Phase 2 (Suggested Title & Map)', () => {
    it('should display suggested title in telemetry preview', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/ruta en bicicleta de 42\.5 km/i)).toBeInTheDocument();
      });
    });

    it('should display suggested title header', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/título sugerido/i)).toBeInTheDocument();
      });
    });

    it('should display hint about editing title in next step', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/podrás editarlo en el siguiente paso/i)).toBeInTheDocument();
      });
    });

    it('should hide step title when telemetry is shown', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      // Initially shows step title
      expect(screen.getByText(/sube tu archivo gpx/i)).toBeInTheDocument();

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      // After analysis, step title should be hidden
      await waitFor(() => {
        expect(screen.queryByText(/sube tu archivo gpx/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Telemetry Preview - Routes Without Elevation', () => {
    it('should display suggested title even without elevation', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithoutElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'flat_route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/ruta en bicicleta de 15\.3 km/i)).toBeInTheDocument();
      });
    });

    it('should show telemetry preview section for routes without elevation', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithoutElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'flat_route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        const telemetrySection = screen.getByRole('region', { name: /vista previa del recorrido/i });
        expect(telemetrySection).toBeInTheDocument();
      });
    });
  });

  describe('File Removal', () => {
    it('should call onFileRemove when remove button clicked', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
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

      const { container } = render(
        <Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />
      );

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        expect(screen.getByText(/ruta en bicicleta de 42\.5 km/i)).toBeInTheDocument();
      });

      // Click remove button to clear telemetry
      const removeButton = screen.getByRole('button', { name: /eliminar/i });
      fireEvent.click(removeButton);

      // Telemetry preview should be cleared
      await waitFor(() => {
        expect(screen.queryByText(/ruta en bicicleta de 42\.5 km/i)).not.toBeInTheDocument();
      });

      // Verify onFileRemove was called
      expect(mockOnFileRemove).toHaveBeenCalledTimes(1);
    });
  });

  describe('Retry Functionality', () => {
    it('should show retry button on error', async () => {
      mockAnalyzeGPXFile.mockRejectedValue(
        new gpxWizardService.GPXAnalysisError('PROCESSING_TIMEOUT', 'Timeout error')
      );

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
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

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
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

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      await waitFor(() => {
        const telemetrySection = screen.getByRole('region', { name: /vista previa del recorrido/i });
        expect(telemetrySection).toBeInTheDocument();
      });
    });

    it('should announce analysis completion to screen readers', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
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

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const file1 = new File(['content1'], 'route1.gpx', { type: 'application/gpx+xml' });
      const file2 = new File(['content2'], 'route2.gpx', { type: 'application/gpx+xml' });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;

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
      const zeroDistanceTelemetry: gpxWizardService.GPXTelemetry = {
        ...mockTelemetryWithoutElevation,
        distance_km: 0,
        suggested_title: 'Punto en Bicicleta',
      };

      mockAnalyzeGPXFile.mockResolvedValue(zeroDistanceTelemetry);

      const { container } = render(<Step1Upload onComplete={mockOnComplete} onFileRemove={mockOnFileRemove} />);

      const mockFile = new File(['content'], 'point.gpx', { type: 'application/gpx+xml' });

      const input = container.querySelector('input[type="file"]') as HTMLInputElement;
      fireEvent.change(input, { target: { files: [mockFile] } });

      // Should still call onComplete with zero-distance telemetry
      await waitFor(() => {
        expect(mockOnComplete).toHaveBeenCalledWith(mockFile, zeroDistanceTelemetry);
      });
    });
  });
});
