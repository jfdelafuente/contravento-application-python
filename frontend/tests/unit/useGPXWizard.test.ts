/**
 * useGPXWizard Hook Unit Tests
 *
 * Tests for GPS Trip Creation Wizard state management hook.
 * Tests multi-step navigation, form data persistence, and wizard lifecycle.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T048
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useGPXWizard } from '../../src/hooks/useGPXWizard';

describe('useGPXWizard (T048)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with step 0', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.currentStep).toBe(0);
    });

    it('should initialize with no selected file', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.selectedFile).toBeNull();
    });

    it('should initialize with no telemetry data', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.telemetryData).toBeNull();
    });

    it('should provide totalSteps constant', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.totalSteps).toBeGreaterThan(0);
      expect(typeof result.current.totalSteps).toBe('number');
    });

    it('should provide wizard control functions', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.nextStep).toBeInstanceOf(Function);
      expect(result.current.prevStep).toBeInstanceOf(Function);
      expect(result.current.goToStep).toBeInstanceOf(Function);
      expect(result.current.resetWizard).toBeInstanceOf(Function);
    });

    it('should provide file management functions', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.setSelectedFile).toBeInstanceOf(Function);
      expect(result.current.setTelemetryData).toBeInstanceOf(Function);
    });

    it('should indicate first step', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.isFirstStep).toBe(true);
      expect(result.current.isLastStep).toBe(false);
    });
  });

  describe('Step Navigation', () => {
    it('should advance to next step', () => {
      const { result } = renderHook(() => useGPXWizard());

      act(() => {
        result.current.nextStep();
      });

      expect(result.current.currentStep).toBe(1);
    });

    it('should go back to previous step', () => {
      const { result } = renderHook(() => useGPXWizard());

      // Go to step 2
      act(() => {
        result.current.nextStep();
        result.current.nextStep();
      });

      expect(result.current.currentStep).toBe(2);

      // Go back
      act(() => {
        result.current.prevStep();
      });

      expect(result.current.currentStep).toBe(1);
    });

    it('should not go below step 0', () => {
      const { result } = renderHook(() => useGPXWizard());

      // Try to go back from step 0
      act(() => {
        result.current.prevStep();
      });

      expect(result.current.currentStep).toBe(0);
    });

    it('should not exceed total steps', () => {
      const { result } = renderHook(() => useGPXWizard());

      const totalSteps = result.current.totalSteps;

      // Try to go beyond last step
      act(() => {
        for (let i = 0; i < totalSteps + 5; i++) {
          result.current.nextStep();
        }
      });

      expect(result.current.currentStep).toBeLessThan(totalSteps);
    });

    it('should jump to specific step', () => {
      const { result } = renderHook(() => useGPXWizard());

      act(() => {
        result.current.goToStep(2);
      });

      expect(result.current.currentStep).toBe(2);
    });

    it('should not allow invalid step numbers', () => {
      const { result } = renderHook(() => useGPXWizard());

      const initialStep = result.current.currentStep;

      // Try negative step
      act(() => {
        result.current.goToStep(-1);
      });

      expect(result.current.currentStep).toBe(initialStep);

      // Try step beyond total
      act(() => {
        result.current.goToStep(999);
      });

      expect(result.current.currentStep).toBe(initialStep);
    });

    it('should update isFirstStep flag', () => {
      const { result } = renderHook(() => useGPXWizard());

      expect(result.current.isFirstStep).toBe(true);

      act(() => {
        result.current.nextStep();
      });

      expect(result.current.isFirstStep).toBe(false);
    });

    it('should update isLastStep flag', () => {
      const { result } = renderHook(() => useGPXWizard());

      const totalSteps = result.current.totalSteps;

      expect(result.current.isLastStep).toBe(false);

      // Go to last step
      act(() => {
        result.current.goToStep(totalSteps - 1);
      });

      expect(result.current.isLastStep).toBe(true);
    });
  });

  describe('File Management', () => {
    it('should set selected file', () => {
      const { result } = renderHook(() => useGPXWizard());

      const mockFile = new File(['gpx content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      act(() => {
        result.current.setSelectedFile(mockFile);
      });

      expect(result.current.selectedFile).toBe(mockFile);
    });

    it('should clear selected file', () => {
      const { result } = renderHook(() => useGPXWizard());

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      act(() => {
        result.current.setSelectedFile(mockFile);
      });

      expect(result.current.selectedFile).not.toBeNull();

      act(() => {
        result.current.setSelectedFile(null);
      });

      expect(result.current.selectedFile).toBeNull();
    });

    it('should set telemetry data', () => {
      const { result } = renderHook(() => useGPXWizard());

      const mockTelemetry = {
        distance_km: 42.5,
        elevation_gain: 850,
        elevation_loss: 820,
        max_elevation: 1250,
        min_elevation: 450,
        has_elevation: true,
        difficulty: 'moderate' as const,
      };

      act(() => {
        result.current.setTelemetryData(mockTelemetry);
      });

      expect(result.current.telemetryData).toEqual(mockTelemetry);
    });

    it('should clear telemetry data', () => {
      const { result } = renderHook(() => useGPXWizard());

      const mockTelemetry = {
        distance_km: 15.0,
        elevation_gain: null,
        elevation_loss: null,
        max_elevation: null,
        min_elevation: null,
        has_elevation: false,
        difficulty: 'easy' as const,
      };

      act(() => {
        result.current.setTelemetryData(mockTelemetry);
      });

      expect(result.current.telemetryData).not.toBeNull();

      act(() => {
        result.current.setTelemetryData(null);
      });

      expect(result.current.telemetryData).toBeNull();
    });
  });

  describe('Wizard Lifecycle', () => {
    it('should reset wizard to initial state', () => {
      const { result } = renderHook(() => useGPXWizard());

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const mockTelemetry = {
        distance_km: 42.5,
        elevation_gain: 850,
        elevation_loss: 820,
        max_elevation: 1250,
        min_elevation: 450,
        has_elevation: true,
        difficulty: 'moderate' as const,
      };

      // Modify state
      act(() => {
        result.current.nextStep();
        result.current.nextStep();
        result.current.setSelectedFile(mockFile);
        result.current.setTelemetryData(mockTelemetry);
      });

      expect(result.current.currentStep).toBe(2);
      expect(result.current.selectedFile).not.toBeNull();
      expect(result.current.telemetryData).not.toBeNull();

      // Reset
      act(() => {
        result.current.resetWizard();
      });

      expect(result.current.currentStep).toBe(0);
      expect(result.current.selectedFile).toBeNull();
      expect(result.current.telemetryData).toBeNull();
    });

    it('should maintain file and telemetry across step navigation', () => {
      const { result } = renderHook(() => useGPXWizard());

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const mockTelemetry = {
        distance_km: 25.0,
        elevation_gain: 500,
        elevation_loss: 480,
        max_elevation: 800,
        min_elevation: 350,
        has_elevation: true,
        difficulty: 'easy' as const,
      };

      act(() => {
        result.current.setSelectedFile(mockFile);
        result.current.setTelemetryData(mockTelemetry);
      });

      // Navigate through steps
      act(() => {
        result.current.nextStep();
        result.current.nextStep();
        result.current.prevStep();
      });

      // File and telemetry should persist
      expect(result.current.selectedFile).toBe(mockFile);
      expect(result.current.telemetryData).toEqual(mockTelemetry);
    });
  });

  describe('Wizard Progress', () => {
    it('should calculate progress percentage', () => {
      const { result } = renderHook(() => useGPXWizard());

      // Step 0 of N steps
      const expectedInitialProgress = 0;
      expect(result.current.progressPercentage).toBe(expectedInitialProgress);

      // Advance to step 1
      act(() => {
        result.current.nextStep();
      });

      const totalSteps = result.current.totalSteps;
      const expectedProgress = Math.round((1 / (totalSteps - 1)) * 100);
      expect(result.current.progressPercentage).toBe(expectedProgress);
    });

    it('should show 100% progress on last step', () => {
      const { result } = renderHook(() => useGPXWizard());

      const totalSteps = result.current.totalSteps;

      // Go to last step
      act(() => {
        result.current.goToStep(totalSteps - 1);
      });

      expect(result.current.progressPercentage).toBe(100);
    });
  });

  describe('Step Validation Flags', () => {
    it('should validate Step 1 (file upload) completion', () => {
      const { result } = renderHook(() => useGPXWizard());

      // Initially not complete
      expect(result.current.isStep1Complete).toBe(false);

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      const mockTelemetry = {
        distance_km: 42.5,
        elevation_gain: 850,
        elevation_loss: 820,
        max_elevation: 1250,
        min_elevation: 450,
        has_elevation: true,
        difficulty: 'moderate' as const,
      };

      // Set file only (not complete without telemetry)
      act(() => {
        result.current.setSelectedFile(mockFile);
      });

      expect(result.current.isStep1Complete).toBe(false);

      // Set telemetry (now complete)
      act(() => {
        result.current.setTelemetryData(mockTelemetry);
      });

      expect(result.current.isStep1Complete).toBe(true);
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid step changes', () => {
      const { result } = renderHook(() => useGPXWizard());

      act(() => {
        result.current.nextStep();
        result.current.nextStep();
        result.current.prevStep();
        result.current.nextStep();
        result.current.goToStep(0);
      });

      expect(result.current.currentStep).toBe(0);
    });

    it('should handle setting same file multiple times', () => {
      const { result } = renderHook(() => useGPXWizard());

      const mockFile = new File(['content'], 'route.gpx', {
        type: 'application/gpx+xml',
      });

      act(() => {
        result.current.setSelectedFile(mockFile);
        result.current.setSelectedFile(mockFile);
        result.current.setSelectedFile(mockFile);
      });

      expect(result.current.selectedFile).toBe(mockFile);
    });

    it('should handle reset multiple times', () => {
      const { result } = renderHook(() => useGPXWizard());

      act(() => {
        result.current.resetWizard();
        result.current.resetWizard();
        result.current.resetWizard();
      });

      expect(result.current.currentStep).toBe(0);
      expect(result.current.selectedFile).toBeNull();
      expect(result.current.telemetryData).toBeNull();
    });
  });
});
