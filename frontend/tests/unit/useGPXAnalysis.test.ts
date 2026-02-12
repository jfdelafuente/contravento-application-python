/**
 * useGPXAnalysis Hook Unit Tests
 *
 * Tests for GPX file analysis hook (Feature 017 - User Story 2).
 * Tests loading states, error handling, retry logic, and telemetry data.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T046
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useGPXAnalysis } from '../../src/hooks/useGPXAnalysis';
import * as gpxWizardService from '../../src/services/gpxWizardService';
import type { GPXTelemetry } from '../../src/services/gpxWizardService';

// Mock gpxWizardService
vi.mock('../../src/services/gpxWizardService', () => ({
  analyzeGPXFile: vi.fn(),
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

describe('useGPXAnalysis (T046)', () => {
  const mockAnalyzeGPXFile = vi.mocked(gpxWizardService.analyzeGPXFile);

  const mockTelemetryWithElevation: GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 850,
    elevation_loss: 820,
    max_elevation: 1250,
    min_elevation: 450,
    has_elevation: true,
    difficulty: 'moderate',
  };

  const mockTelemetryWithoutElevation: GPXTelemetry = {
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

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with idle state', () => {
      const { result } = renderHook(() => useGPXAnalysis());

      expect(result.current.isLoading).toBe(false);
      expect(result.current.telemetry).toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.isSuccess).toBe(false);
      expect(result.current.isError).toBe(false);
    });

    it('should provide analyzeFile function', () => {
      const { result } = renderHook(() => useGPXAnalysis());

      expect(result.current.analyzeFile).toBeInstanceOf(Function);
    });

    it('should provide reset function', () => {
      const { result } = renderHook(() => useGPXAnalysis());

      expect(result.current.reset).toBeInstanceOf(Function);
    });

    it('should provide retry function', () => {
      const { result } = renderHook(() => useGPXAnalysis());

      expect(result.current.retry).toBeInstanceOf(Function);
    });
  });

  describe('Successful Analysis', () => {
    it('should set loading state while analyzing file', async () => {
      mockAnalyzeGPXFile.mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => resolve(mockTelemetryWithElevation), 100);
          })
      );

      const mockFile = new File(['gpx content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const { result } = renderHook(() => useGPXAnalysis());

      // Start analysis
      result.current.analyzeFile(mockFile);

      // Should be loading immediately
      expect(result.current.isLoading).toBe(true);
      expect(result.current.telemetry).toBeNull();
      expect(result.current.error).toBeNull();
    });

    it('should return telemetry data on successful analysis', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const mockFile = new File(['gpx content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.telemetry).toEqual(mockTelemetryWithElevation);
        expect(result.current.error).toBeNull();
      });

      expect(mockAnalyzeGPXFile).toHaveBeenCalledWith(mockFile);
      expect(mockAnalyzeGPXFile).toHaveBeenCalledTimes(1);
    });

    it('should handle telemetry without elevation data', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithoutElevation);

      const mockFile = new File(['gpx content'], 'flat_route.gpx', {
        type: 'application/gpx+xml',
      });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.telemetry).toEqual(mockTelemetryWithoutElevation);
        expect(result.current.telemetry?.has_elevation).toBe(false);
        expect(result.current.telemetry?.elevation_gain).toBeNull();
      });
    });

    it('should clear previous errors on successful analysis', async () => {
      // First, fail with error
      mockAnalyzeGPXFile.mockRejectedValueOnce(
        new gpxWizardService.GPXAnalysisError('FILE_TOO_LARGE', 'File too large', 'file')
      );

      const { result } = renderHook(() => useGPXAnalysis());
      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      // Then, succeed
      mockAnalyzeGPXFile.mockResolvedValueOnce(mockTelemetryWithElevation);

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).toBeNull();
        expect(result.current.telemetry).toEqual(mockTelemetryWithElevation);
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle GPXAnalysisError correctly', async () => {
      const error = new gpxWizardService.GPXAnalysisError(
        'INVALID_FILE_TYPE',
        'Formato no válido. Solo se aceptan archivos .gpx',
        'file'
      );
      mockAnalyzeGPXFile.mockRejectedValue(error);

      const mockFile = new File(['content'], 'document.pdf', { type: 'application/pdf' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
        expect(result.current.isError).toBe(true);
        expect(result.current.error).toBe('Formato no válido. Solo se aceptan archivos .gpx');
        expect(result.current.telemetry).toBeNull();
      });
    });

    it('should handle file too large error', async () => {
      const error = new gpxWizardService.GPXAnalysisError(
        'FILE_TOO_LARGE',
        'El archivo GPX es demasiado grande. Tamaño máximo: 10MB',
        'file'
      );
      mockAnalyzeGPXFile.mockRejectedValue(error);

      const mockFile = new File(['x'.repeat(11 * 1024 * 1024)], 'huge.gpx', {
        type: 'application/gpx+xml',
      });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).toBe(
          'El archivo GPX es demasiado grande. Tamaño máximo: 10MB'
        );
      });
    });

    it('should handle invalid GPX file error', async () => {
      const error = new gpxWizardService.GPXAnalysisError(
        'INVALID_GPX_FILE',
        'No se pudo procesar el archivo GPX. Verifica que sea un archivo válido'
      );
      mockAnalyzeGPXFile.mockRejectedValue(error);

      const mockFile = new File(['corrupted content'], 'corrupted.gpx', {
        type: 'application/gpx+xml',
      });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).toBe(
          'No se pudo procesar el archivo GPX. Verifica que sea un archivo válido'
        );
      });
    });

    it('should handle processing timeout error', async () => {
      const error = new gpxWizardService.GPXAnalysisError(
        'PROCESSING_TIMEOUT',
        'El procesamiento del archivo GPX excedió el tiempo límite'
      );
      mockAnalyzeGPXFile.mockRejectedValue(error);

      const mockFile = new File(['content'], 'slow.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).toBe(
          'El procesamiento del archivo GPX excedió el tiempo límite'
        );
      });
    });

    it('should handle unauthorized error', async () => {
      const error = new gpxWizardService.GPXAnalysisError(
        'UNAUTHORIZED',
        'No autorizado. Inicia sesión para continuar'
      );
      mockAnalyzeGPXFile.mockRejectedValue(error);

      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).toBe('No autorizado. Inicia sesión para continuar');
      });
    });

    it('should handle generic errors with fallback message', async () => {
      const error = new Error('Network error');
      mockAnalyzeGPXFile.mockRejectedValue(error);

      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).toBe(
          'Error al analizar el archivo GPX. Intenta de nuevo.'
        );
      });
    });
  });

  describe('Reset Functionality', () => {
    it('should reset to initial state', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      // Analyze file
      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.telemetry).not.toBeNull();
      });

      // Reset
      result.current.reset();

      expect(result.current.isLoading).toBe(false);
      expect(result.current.telemetry).toBeNull();
      expect(result.current.error).toBeNull();
      expect(result.current.isSuccess).toBe(false);
      expect(result.current.isError).toBe(false);
    });

    it('should clear error state', async () => {
      const error = new gpxWizardService.GPXAnalysisError(
        'INVALID_FILE_TYPE',
        'Invalid file type',
        'file'
      );
      mockAnalyzeGPXFile.mockRejectedValue(error);

      const mockFile = new File(['content'], 'document.pdf', { type: 'application/pdf' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      // Reset
      result.current.reset();

      expect(result.current.error).toBeNull();
    });
  });

  describe('Retry Functionality', () => {
    it('should retry with last file on retry()', async () => {
      // First attempt fails
      mockAnalyzeGPXFile.mockRejectedValueOnce(
        new gpxWizardService.GPXAnalysisError('PROCESSING_TIMEOUT', 'Timeout', 'file')
      );

      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      // Second attempt succeeds
      mockAnalyzeGPXFile.mockResolvedValueOnce(mockTelemetryWithElevation);

      await result.current.retry();

      await waitFor(() => {
        expect(result.current.error).toBeNull();
        expect(result.current.telemetry).toEqual(mockTelemetryWithElevation);
      });

      // Should have been called twice (initial + retry)
      expect(mockAnalyzeGPXFile).toHaveBeenCalledTimes(2);
      expect(mockAnalyzeGPXFile).toHaveBeenCalledWith(mockFile);
    });

    it('should not retry if no previous file', async () => {
      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.retry();

      expect(mockAnalyzeGPXFile).not.toHaveBeenCalled();
    });

    it('should clear error on retry', async () => {
      mockAnalyzeGPXFile.mockRejectedValueOnce(
        new gpxWizardService.GPXAnalysisError('INVALID_GPX_FILE', 'Invalid GPX')
      );

      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.error).not.toBeNull();
      });

      // Retry (will succeed this time)
      mockAnalyzeGPXFile.mockResolvedValueOnce(mockTelemetryWithElevation);

      result.current.retry();

      // Error should be cleared immediately when retry starts
      expect(result.current.error).toBeNull();
    });
  });

  describe('Multiple Sequential Calls', () => {
    it('should handle analyzing different files sequentially', async () => {
      const file1 = new File(['content1'], 'route1.gpx', { type: 'application/gpx+xml' });
      const file2 = new File(['content2'], 'route2.gpx', { type: 'application/gpx+xml' });

      mockAnalyzeGPXFile
        .mockResolvedValueOnce(mockTelemetryWithElevation)
        .mockResolvedValueOnce(mockTelemetryWithoutElevation);

      const { result } = renderHook(() => useGPXAnalysis());

      // Analyze first file
      await result.current.analyzeFile(file1);

      await waitFor(() => {
        expect(result.current.telemetry).toEqual(mockTelemetryWithElevation);
      });

      // Analyze second file
      await result.current.analyzeFile(file2);

      await waitFor(() => {
        expect(result.current.telemetry).toEqual(mockTelemetryWithoutElevation);
      });

      expect(mockAnalyzeGPXFile).toHaveBeenCalledTimes(2);
    });
  });

  describe('Derived State', () => {
    it('should set isSuccess to true after successful analysis', async () => {
      mockAnalyzeGPXFile.mockResolvedValue(mockTelemetryWithElevation);

      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
        expect(result.current.isError).toBe(false);
      });
    });

    it('should set isError to true after failed analysis', async () => {
      mockAnalyzeGPXFile.mockRejectedValue(
        new gpxWizardService.GPXAnalysisError('INVALID_GPX_FILE', 'Invalid file')
      );

      const mockFile = new File(['content'], 'route.gpx', { type: 'application/gpx+xml' });

      const { result } = renderHook(() => useGPXAnalysis());

      await result.current.analyzeFile(mockFile);

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
        expect(result.current.isSuccess).toBe(false);
      });
    });
  });
});
