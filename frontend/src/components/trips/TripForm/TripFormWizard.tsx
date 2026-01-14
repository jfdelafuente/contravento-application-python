/**
 * TripFormWizard Component
 *
 * Main multi-step wizard controller for creating/editing trips.
 * Uses React Hook Form for form state management.
 * Manages navigation between 4 steps with validation per step.
 *
 * Used in:
 * - TripCreatePage (create new trip)
 * - TripEditPage (edit existing trip) - Phase 7
 */

import React, { useState, useEffect } from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { FormStepIndicator } from './FormStepIndicator';
import { Step1BasicInfo } from './Step1BasicInfo';
import { Step2StoryTags } from './Step2StoryTags';
import { Step3Photos } from './Step3Photos';
import { Step4Review } from './Step4Review';
import { TripCreateInput, TripPhoto } from '../../../types/trip';
import toast from 'react-hot-toast';
import './TripFormWizard.css';

interface TripFormWizardProps {
  /** Initial form data (for editing existing trip) */
  initialData?: Partial<TripCreateInput>;

  /** Trip ID (only for editing) */
  tripId?: string;

  /** Existing photos from server (for edit mode) */
  existingPhotos?: TripPhoto[];

  /** Callback when form is submitted */
  onSubmit: (data: TripCreateInput, isDraft: boolean) => Promise<void>;

  /** Whether we're in edit mode */
  isEditMode?: boolean;

  /** Current trip status (for edit mode - determines if "Save Draft" button is shown) */
  currentStatus?: 'draft' | 'published';
}

// Step labels for the indicator
const STEP_LABELS = [
  'Información Básica',
  'Historia y Etiquetas',
  'Fotos',
  'Revisión',
];

export const TripFormWizard: React.FC<TripFormWizardProps> = ({
  initialData,
  tripId,
  existingPhotos = [],
  onSubmit,
  isEditMode = false,
  currentStatus,
}) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // React Hook Form setup
  const methods = useForm<TripCreateInput>({
    defaultValues: initialData || {
      title: '',
      description: '',
      start_date: '',
      end_date: null,
      distance_km: null,
      difficulty: null,
      tags: [],
    },
    mode: 'onChange', // Validate on change for better UX
  });

  const { handleSubmit, trigger, formState } = methods;
  const { isDirty } = formState;

  // Warn about unsaved changes when navigating away
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty && !isSubmitting) {
        e.preventDefault();
        e.returnValue = '';
        return '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isDirty, isSubmitting]);

  /**
   * Navigate to next step with validation
   */
  const handleNext = async () => {
    // Validate current step before advancing
    const fieldsToValidate = getFieldsForStep(currentStep);
    const isValid = await trigger(fieldsToValidate);

    if (!isValid) {
      toast.error('Por favor completa todos los campos requeridos', {
        duration: 3000,
        position: 'top-center',
      });
      return;
    }

    // Additional validation for Step 1 locations
    if (currentStep === 1) {
      const validateStep1Locations = (window as any).__validateStep1Locations;
      if (validateStep1Locations && !validateStep1Locations()) {
        toast.error('Por favor completa el nombre de todas las ubicaciones', {
          duration: 3000,
          position: 'top-center',
        });
        return;
      }
    }

    setCurrentStep((prev) => Math.min(prev + 1, 4));
  };

  /**
   * Navigate to previous step
   */
  const handlePrevious = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  /**
   * Save as draft (minimal validation)
   */
  const handleSaveDraft = async () => {
    setIsSubmitting(true);

    try {
      const formData = methods.getValues();
      await onSubmit(formData, true); // isDraft = true

      toast.success('Borrador guardado correctamente', {
        duration: 3000,
        position: 'top-center',
      });

      navigate('/trips');
    } catch (error: any) {
      console.error('Error saving draft:', error);

      const errorMessage =
        error.response?.data?.error?.message || 'Error al guardar el borrador. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Publish trip (full validation)
   */
  const handlePublish = handleSubmit(async (data) => {
    // Validate description length for publishing
    if (!data.description || data.description.length < 50) {
      toast.error('La descripción debe tener al menos 50 caracteres para publicar', {
        duration: 5000,
        position: 'top-center',
      });
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit(data, false); // isDraft = false

      toast.success(
        isEditMode ? 'Viaje actualizado correctamente' : 'Viaje publicado correctamente',
        {
          duration: 3000,
          position: 'top-center',
        }
      );

      navigate('/trips');
    } catch (error: any) {
      console.error('Error publishing trip:', error);

      const errorMessage =
        error.response?.data?.error?.message || 'Error al publicar el viaje. Intenta nuevamente.';

      toast.error(errorMessage, {
        duration: 5000,
        position: 'top-center',
      });
    } finally {
      setIsSubmitting(false);
    }
  });

  /**
   * Cancel and go back
   */
  const handleCancel = () => {
    if (isDirty) {
      const confirmDiscard = window.confirm(
        '¿Estás seguro de que quieres cancelar? Se perderán todos los cambios no guardados.'
      );

      if (!confirmDiscard) return;
    }

    navigate('/trips');
  };

  return (
    <FormProvider {...methods}>
      <div className="trip-form-wizard">
        {/* Loading Overlay - T079 */}
        {isSubmitting && (
          <div className="trip-form-wizard__loading-overlay">
            <div className="trip-form-wizard__loading-spinner">
              <div className="spinner"></div>
              <p className="trip-form-wizard__loading-text">
                {currentStep === 4 && methods.getValues().description?.length >= 50
                  ? 'Publicando viaje...'
                  : 'Guardando borrador...'}
              </p>
            </div>
          </div>
        )}

        {/* Step Indicator */}
        <FormStepIndicator
          currentStep={currentStep}
          totalSteps={4}
          stepLabels={STEP_LABELS}
        />

        {/* Form Content - Steps will be rendered here */}
        <div className="trip-form-wizard__content">
          {currentStep === 1 && (
            <div className="trip-form-wizard__step">
              <Step1BasicInfo />
            </div>
          )}

          {currentStep === 2 && (
            <div className="trip-form-wizard__step">
              <Step2StoryTags />
            </div>
          )}

          {currentStep === 3 && (
            <div className="trip-form-wizard__step">
              <Step3Photos tripId={tripId} existingPhotos={existingPhotos} />
            </div>
          )}

          {currentStep === 4 && (
            <div className="trip-form-wizard__step">
              <Step4Review />
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div className="trip-form-wizard__actions">
          {/* Cancel Button */}
          <button
            type="button"
            className="trip-form-wizard__button trip-form-wizard__button--secondary"
            onClick={handleCancel}
            disabled={isSubmitting}
          >
            Cancelar
          </button>

          {/* Previous Button */}
          {currentStep > 1 && (
            <button
              type="button"
              className="trip-form-wizard__button trip-form-wizard__button--secondary"
              onClick={handlePrevious}
              disabled={isSubmitting}
            >
              ← Anterior
            </button>
          )}

          {/* Next Button (steps 1-3) */}
          {currentStep < 4 && (
            <button
              type="button"
              className="trip-form-wizard__button trip-form-wizard__button--primary"
              onClick={handleNext}
              disabled={isSubmitting}
            >
              Siguiente →
            </button>
          )}

          {/* Final Step Actions (step 4) */}
          {currentStep === 4 && (
            <>
              {/* Save Draft Button - Only show if creating new trip OR editing a draft */}
              {(!isEditMode || currentStatus === 'draft') && (
                <button
                  type="button"
                  className="trip-form-wizard__button trip-form-wizard__button--secondary"
                  onClick={handleSaveDraft}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Guardando...' : 'Guardar Borrador'}
                </button>
              )}

              {/* Publish Button */}
              <button
                type="button"
                className="trip-form-wizard__button trip-form-wizard__button--success"
                onClick={handlePublish}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Publicando...' : isEditMode ? 'Actualizar' : 'Publicar'}
              </button>
            </>
          )}
        </div>
      </div>
    </FormProvider>
  );
};

/**
 * Get fields to validate for each step
 */
function getFieldsForStep(step: number): (keyof TripCreateInput)[] {
  switch (step) {
    case 1: // Basic Info
      return ['title', 'start_date'];
    case 2: // Story & Tags
      return ['description'];
    case 3: // Photos (optional, no validation required)
      return [];
    case 4: // Review (final validation happens on publish)
      return [];
    default:
      return [];
  }
}
