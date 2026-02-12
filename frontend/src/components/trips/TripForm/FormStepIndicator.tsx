/**
 * FormStepIndicator Component
 *
 * Visual progress indicator for multi-step wizard form.
 * Shows current step number and completed/active/pending states.
 *
 * Used in:
 * - TripFormWizard (displays 1/4, 2/4, 3/4, 4/4 progress)
 */

import React from 'react';
import './FormStepIndicator.css';

interface FormStepIndicatorProps {
  /** Current step (1-based index) */
  currentStep: number;

  /** Total number of steps */
  totalSteps: number;

  /** Optional step labels */
  stepLabels?: string[];
}

export const FormStepIndicator: React.FC<FormStepIndicatorProps> = ({
  currentStep,
  totalSteps,
  stepLabels = [],
}) => {
  return (
    <div className="form-step-indicator">
      <div className="form-step-indicator__steps">
        {Array.from({ length: totalSteps }, (_, index) => {
          const stepNumber = index + 1;
          const isCompleted = stepNumber < currentStep;
          const isActive = stepNumber === currentStep;

          const stepClass = `form-step-indicator__step ${
            isCompleted
              ? 'form-step-indicator__step--completed'
              : isActive
              ? 'form-step-indicator__step--active'
              : 'form-step-indicator__step--pending'
          }`;

          return (
            <div key={stepNumber} className={stepClass}>
              {/* Step Circle */}
              <div className="form-step-indicator__circle">
                {isCompleted ? (
                  // Checkmark icon for completed steps
                  <svg
                    className="form-step-indicator__check-icon"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                ) : (
                  // Step number for active/pending
                  <span className="form-step-indicator__number">{stepNumber}</span>
                )}
              </div>

              {/* Step Label (optional) */}
              {stepLabels[index] && (
                <div className="form-step-indicator__label">{stepLabels[index]}</div>
              )}

              {/* Connector Line (not shown for last step) */}
              {stepNumber < totalSteps && (
                <div
                  className={`form-step-indicator__line ${
                    isCompleted ? 'form-step-indicator__line--completed' : ''
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Current Step Text */}
      <div className="form-step-indicator__text">
        Paso {currentStep} de {totalSteps}
      </div>
    </div>
  );
};
