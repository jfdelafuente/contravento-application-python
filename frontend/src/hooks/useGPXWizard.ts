/**
 * useGPXWizard Hook - GPS Trip Creation Wizard State Management
 *
 * Central state management hook for the multi-step GPS Trip Creation Wizard.
 * Manages step navigation, file selection, telemetry data, and wizard lifecycle.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 4 (US2)
 * Task: T048
 *
 * @example
 * ```typescript
 * const {
 *   currentStep,
 *   selectedFile,
 *   telemetryData,
 *   nextStep,
 *   prevStep,
 *   setSelectedFile,
 *   setTelemetryData,
 * } = useGPXWizard();
 *
 * // Step 1: Upload GPX file
 * <GPXWizardUploader
 *   onFileSelect={setSelectedFile}
 *   selectedFile={selectedFile}
 * />
 *
 * // Navigate between steps
 * <button onClick={prevStep} disabled={isFirstStep}>
 *   Anterior
 * </button>
 * <button onClick={nextStep} disabled={isLastStep}>
 *   Siguiente
 * </button>
 * ```
 */

import { useState, useCallback } from 'react';
import type { GPXTelemetry } from '../services/gpxWizardService';

/**
 * Total number of wizard steps
 * Step 0: GPX Upload & Analysis
 * Step 1: Trip Details
 * Step 2: Map Visualization (Phase 7 - US4)
 * Step 3: Review & Publish
 */
const TOTAL_STEPS = 4;

/**
 * Return type for useGPXWizard hook
 */
export interface UseGPXWizardReturn {
  /** Current wizard step (0-indexed) */
  currentStep: number;

  /** Total number of steps in wizard */
  totalSteps: number;

  /** Selected GPX file (null if not selected) */
  selectedFile: File | null;

  /** Telemetry data from GPX analysis (null if not analyzed) */
  telemetryData: GPXTelemetry | null;

  /** Whether currently on first step */
  isFirstStep: boolean;

  /** Whether currently on last step */
  isLastStep: boolean;

  /** Wizard completion progress (0-100) */
  progressPercentage: number;

  /** Whether Step 1 (upload + analysis) is complete */
  isStep1Complete: boolean;

  /** Advance to next step (no-op if already on last step) */
  nextStep: () => void;

  /** Go back to previous step (no-op if already on first step) */
  prevStep: () => void;

  /** Jump to specific step (validates step bounds) */
  goToStep: (step: number) => void;

  /** Set selected GPX file */
  setSelectedFile: (file: File | null) => void;

  /** Set telemetry data from analysis */
  setTelemetryData: (data: GPXTelemetry | null) => void;

  /** Reset wizard to initial state */
  resetWizard: () => void;
}

/**
 * Hook for GPS Trip Creation Wizard state management.
 *
 * Manages multi-step wizard navigation, file selection, telemetry data,
 * and overall wizard lifecycle.
 *
 * @returns {UseGPXWizardReturn} Wizard state and control functions
 */
export function useGPXWizard(): UseGPXWizardReturn {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [telemetryData, setTelemetryData] = useState<GPXTelemetry | null>(null);

  /**
   * Advance to next step.
   * No-op if already on last step.
   */
  const nextStep = useCallback((): void => {
    setCurrentStep((prev) => Math.min(prev + 1, TOTAL_STEPS - 1));
  }, []);

  /**
   * Go back to previous step.
   * No-op if already on first step.
   */
  const prevStep = useCallback((): void => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, []);

  /**
   * Jump to specific step.
   * Validates step bounds (0 to TOTAL_STEPS - 1).
   *
   * @param step - Target step number (0-indexed)
   */
  const goToStep = useCallback((step: number): void => {
    if (step < 0 || step >= TOTAL_STEPS) {
      return;
    }
    setCurrentStep(step);
  }, []);

  /**
   * Reset wizard to initial state.
   * Clears all data and returns to step 0.
   */
  const resetWizard = useCallback((): void => {
    setCurrentStep(0);
    setSelectedFile(null);
    setTelemetryData(null);
  }, []);

  // Derived state
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === TOTAL_STEPS - 1;

  // Calculate progress percentage (0% at step 0, 100% at last step)
  const progressPercentage = Math.round((currentStep / (TOTAL_STEPS - 1)) * 100);

  // Step 1 is complete when both file and telemetry are available
  const isStep1Complete = selectedFile !== null && telemetryData !== null;

  return {
    currentStep,
    totalSteps: TOTAL_STEPS,
    selectedFile,
    telemetryData,
    isFirstStep,
    isLastStep,
    progressPercentage,
    isStep1Complete,
    nextStep,
    prevStep,
    goToStep,
    setSelectedFile,
    setTelemetryData,
    resetWizard,
  };
}
