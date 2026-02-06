/**
 * useGPXAnalysis Hook - GPX File Analysis State Management
 *
 * Custom hook for managing GPX file analysis state, including loading,
 * error handling, and retry logic.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T046
 *
 * @example
 * ```typescript
 * const { analyzeFile, telemetry, isLoading, error, retry } = useGPXAnalysis();
 *
 * // Analyze file
 * await analyzeFile(gpxFile);
 *
 * // Check results
 * if (telemetry) {
 *   console.log(`Distance: ${telemetry.distance_km} km`);
 *   console.log(`Difficulty: ${telemetry.difficulty}`);
 * }
 *
 * // Retry on failure
 * if (error) {
 *   await retry();
 * }
 * ```
 */

import { useState, useCallback, useRef } from 'react';
import { analyzeGPXFile, GPXAnalysisError } from '../services/gpxWizardService';
import type { GPXTelemetry } from '../services/gpxWizardService';

/**
 * Return type for useGPXAnalysis hook
 */
export interface UseGPXAnalysisReturn {
  /** Whether file analysis is in progress */
  isLoading: boolean;

  /** Telemetry data from successful analysis (null if not analyzed or failed) */
  telemetry: GPXTelemetry | null;

  /** Error message from failed analysis (null if no error) */
  error: string | null;

  /** Derived state: true if analysis completed successfully */
  isSuccess: boolean;

  /** Derived state: true if analysis failed with error */
  isError: boolean;

  /** Analyze a GPX file and extract telemetry data */
  analyzeFile: (file: File) => Promise<void>;

  /** Reset hook to initial state (clears telemetry, error, loading) */
  reset: () => void;

  /** Retry analysis with the last file (no-op if no previous file) */
  retry: () => Promise<void>;
}

/**
 * Hook for GPX file analysis with state management.
 *
 * Provides loading states, error handling, telemetry data, and retry logic
 * for the GPX wizard file upload process.
 *
 * @returns {UseGPXAnalysisReturn} Analysis state and control functions
 */
export function useGPXAnalysis(): UseGPXAnalysisReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [telemetry, setTelemetry] = useState<GPXTelemetry | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Store last file for retry functionality
  const lastFileRef = useRef<File | null>(null);

  /**
   * Analyze a GPX file and update state with results.
   *
   * Clears previous telemetry and errors before starting analysis.
   * Handles GPXAnalysisError and generic errors with appropriate messages.
   *
   * @param file - GPX file to analyze
   */
  const analyzeFile = useCallback(async (file: File): Promise<void> => {
    // Clear previous state
    setError(null);
    setTelemetry(null);
    setIsLoading(true);

    // Store file for retry
    lastFileRef.current = file;

    try {
      const result = await analyzeGPXFile(file);
      setTelemetry(result);
    } catch (err: any) {
      // Handle GPXAnalysisError with specific message
      if (err instanceof GPXAnalysisError) {
        setError(err.message);
      }
      // Handle generic errors with fallback message
      else {
        setError('Error al analizar el archivo GPX. Intenta de nuevo.');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Reset hook to initial state.
   *
   * Clears telemetry, error, and loading states.
   * Does NOT clear lastFileRef (allows retry after reset).
   */
  const reset = useCallback((): void => {
    setIsLoading(false);
    setTelemetry(null);
    setError(null);
  }, []);

  /**
   * Retry analysis with the last file.
   *
   * No-op if no file has been analyzed yet.
   * Clears error before retrying.
   */
  const retry = useCallback(async (): Promise<void> => {
    if (!lastFileRef.current) {
      return;
    }

    setError(null);
    await analyzeFile(lastFileRef.current);
  }, [analyzeFile]);

  // Derived state
  const isSuccess = telemetry !== null && error === null;
  const isError = error !== null;

  return {
    isLoading,
    telemetry,
    error,
    isSuccess,
    isError,
    analyzeFile,
    reset,
    retry,
  };
}
