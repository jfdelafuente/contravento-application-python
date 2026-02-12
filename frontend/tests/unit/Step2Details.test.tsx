/**
 * Step2Details Component Unit Tests
 *
 * Tests for wizard Step 2 (Trip Details) component.
 * Tests form validation, auto-population, difficulty display, and user interactions.
 *
 * Feature: 017-gps-trip-wizard
 * Phase: 5 (US3)
 * Task: T051
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { Step2Details } from '../../src/components/wizard/Step2Details';
import type { GPXTelemetry } from '../../src/services/gpxWizardService';

describe('Step2Details (T051)', () => {
  const mockOnNext = vi.fn();
  const mockOnPrevious = vi.fn();
  const mockOnCancel = vi.fn();
  const mockOnRemoveGPX = vi.fn();

  const mockFile = new File(['content'], 'test-route.gpx', {
    type: 'application/gpx+xml',
  });

  const mockTelemetry: GPXTelemetry = {
    distance_km: 42.5,
    elevation_gain: 1250,
    elevation_loss: 1100,
    max_elevation: 1850,
    min_elevation: 450,
    has_elevation: true,
    has_timestamps: false,
    start_date: null,
    end_date: null,
    total_time_minutes: null,
    moving_time_minutes: null,
    difficulty: 'difficult',
    suggested_title: 'test-route',
    trackpoints: null,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Render', () => {
    it('should render step title', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      expect(screen.getByText(/detalles del viaje/i)).toBeInTheDocument();
    });

    it('should display all form fields', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      expect(screen.getByLabelText(/título/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/descripción/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/fecha de inicio/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/fecha de fin/i)).toBeInTheDocument();

      // Privacy field - check for radio group heading
      expect(screen.getByText(/privacidad/i)).toBeInTheDocument();

      // Verify privacy radio buttons exist
      expect(screen.getByLabelText(/público/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/privado/i)).toBeInTheDocument();
    });

    it('should display difficulty badge', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      expect(screen.getByText(/difícil/i)).toBeInTheDocument();
    });

    it('should display distance from telemetry', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      expect(screen.getByText(/42\.5\s*km/i)).toBeInTheDocument();
    });
  });

  describe('Auto-population', () => {
    it('should auto-populate title from GPX filename without extension', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const titleInput = screen.getByLabelText(/título/i) as HTMLInputElement;
      expect(titleInput.value).toBe('test-route');
    });

    it('should handle GPX filename with multiple dots', () => {
      const fileWithDots = new File(['content'], 'route.long.name.gpx', {
        type: 'application/gpx+xml',
      });

      const telemetryWithDots: GPXTelemetry = {
        ...mockTelemetry,
        suggested_title: 'route.long.name',
      };

      render(
        <Step2Details
          gpxFile={fileWithDots}
          telemetry={telemetryWithDots}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const titleInput = screen.getByLabelText(/título/i) as HTMLInputElement;
      expect(titleInput.value).toBe('route.long.name');
    });

    it('should allow user to edit auto-populated title', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const titleInput = screen.getByLabelText(/título/i) as HTMLInputElement;
      fireEvent.change(titleInput, { target: { value: 'Ruta Bikepacking Pirineos' } });

      expect(titleInput.value).toBe('Ruta Bikepacking Pirineos');
    });
  });

  describe('Form Validation', () => {
    it('should show error when title is empty', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const titleInput = screen.getByLabelText(/título/i);
      fireEvent.change(titleInput, { target: { value: '' } });
      fireEvent.blur(titleInput);

      await waitFor(() => {
        expect(screen.getByText(/el título es obligatorio/i)).toBeInTheDocument();
      });
    });

    it('should show error when title exceeds 200 characters', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const titleInput = screen.getByLabelText(/título/i);
      const longTitle = 'A'.repeat(201);
      fireEvent.change(titleInput, { target: { value: longTitle } });
      fireEvent.blur(titleInput);

      await waitFor(() => {
        expect(screen.getByText(/el título no puede superar 200 caracteres/i)).toBeInTheDocument();
      });
    });

    it('should show error when description is less than 50 characters', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const descriptionInput = screen.getByLabelText(/descripción/i);
      fireEvent.change(descriptionInput, { target: { value: 'Too short' } });
      fireEvent.blur(descriptionInput);

      await waitFor(() => {
        expect(
          screen.getByText(/la descripción debe tener al menos 50 caracteres/i)
        ).toBeInTheDocument();
      });
    });

    it('should show character count for description', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const descriptionInput = screen.getByLabelText(/descripción/i);
      fireEvent.change(descriptionInput, { target: { value: 'Short text' } });

      expect(screen.getByText(/10\s*\/\s*50/i)).toBeInTheDocument();
    });

    it('should accept valid description with 50+ characters', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const validDescription =
        'Viaje de 5 días por los Pirineos con más de 300km recorridos y 5000m de desnivel acumulado.';

      const descriptionInput = screen.getByLabelText(/descripción/i);
      fireEvent.change(descriptionInput, { target: { value: validDescription } });
      fireEvent.blur(descriptionInput);

      await waitFor(() => {
        expect(
          screen.queryByText(/la descripción debe tener al menos 50 caracteres/i)
        ).not.toBeInTheDocument();
      });
    });

    it('should show error when start date is empty', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      // First set a valid date, then clear it to trigger validation
      const startDateInput = screen.getByLabelText(/fecha de inicio/i);
      fireEvent.change(startDateInput, { target: { value: '2024-06-01' } });
      fireEvent.change(startDateInput, { target: { value: '' } });
      fireEvent.blur(startDateInput);

      await waitFor(() => {
        expect(screen.getByText(/la fecha de inicio es obligatoria/i)).toBeInTheDocument();
      });
    });
  });

  describe('Privacy Settings', () => {
    it('should default to public privacy', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const publicRadio = screen.getByRole('radio', { name: /público/i }) as HTMLInputElement;
      expect(publicRadio).toBeChecked();
    });

    it('should allow changing privacy to private', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const privateRadio = screen.getByRole('radio', { name: /privado/i });
      fireEvent.click(privateRadio);

      expect(privateRadio).toBeChecked();
    });
  });

  describe('Navigation', () => {
    it('should call onPrevious when Anterior button clicked', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      // Use more specific aria-label to avoid confusion with dialog buttons
      const previousButton = screen.getByRole('button', { name: /volver al paso anterior de carga/i });
      fireEvent.click(previousButton);

      expect(mockOnPrevious).toHaveBeenCalledTimes(1);
    });

    it('should not call onNext when form is invalid', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      // Clear required fields
      const titleInput = screen.getByLabelText(/título/i);
      fireEvent.change(titleInput, { target: { value: '' } });

      // Use aria-label query and include disabled state
      const nextButton = screen.getByRole('button', { name: /continuar al siguiente paso|completar el formulario/i });

      // Button should be disabled when form is invalid
      expect(nextButton).toBeDisabled();

      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(mockOnNext).not.toHaveBeenCalled();
      });
    });

    it('should call onNext with form data when valid', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      // Fill form with valid data
      const titleInput = screen.getByLabelText(/título/i);
      const descriptionInput = screen.getByLabelText(/descripción/i);
      const startDateInput = screen.getByLabelText(/fecha de inicio/i);
      const endDateInput = screen.getByLabelText(/fecha de fin/i);

      fireEvent.change(titleInput, { target: { value: 'Ruta Bikepacking Pirineos' } });
      fireEvent.change(descriptionInput, {
        target: {
          value:
            'Viaje de 5 días por los Pirineos con más de 300km recorridos y 5000m de desnivel acumulado.',
        },
      });
      fireEvent.change(startDateInput, { target: { value: '2024-06-01' } });
      fireEvent.change(endDateInput, { target: { value: '2024-06-05' } });

      // Wait for form validation to complete and button to be enabled
      await waitFor(() => {
        const nextButton = screen.getByRole('button', { name: /continuar al siguiente paso/i });
        expect(nextButton).not.toBeDisabled();
      });

      const nextButton = screen.getByRole('button', { name: /continuar al siguiente paso/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(mockOnNext).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Ruta Bikepacking Pirineos',
            description: expect.stringContaining('300km'),
            start_date: '2024-06-01',
            end_date: '2024-06-05',
            privacy: 'public',
          })
        );
      });
    });
  });

  describe('Cancel Functionality', () => {
    it('should show confirmation dialog when Cancel button clicked', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      expect(
        screen.getByText(/¿seguro que quieres cancelar el asistente\?/i)
      ).toBeInTheDocument();
    });

    it('should call onCancel when user confirms cancellation', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      const confirmButton = screen.getByRole('button', { name: /sí, cancelar/i });
      fireEvent.click(confirmButton);

      expect(mockOnCancel).toHaveBeenCalledTimes(1);
    });

    it('should not call onCancel when user declines cancellation', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      const declineButton = screen.getByRole('button', { name: /no, continuar/i });
      fireEvent.click(declineButton);

      expect(mockOnCancel).not.toHaveBeenCalled();
    });
  });

  describe('Remove GPX Functionality', () => {
    it('should show confirmation dialog when Eliminar GPX button clicked', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const removeButton = screen.getByRole('button', { name: /eliminar archivo gpx/i });
      fireEvent.click(removeButton);

      expect(screen.getByText(/¿eliminar archivo gpx\?/i)).toBeInTheDocument();
    });

    it('should call onRemoveGPX when user confirms removal', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const removeButton = screen.getByRole('button', { name: /eliminar archivo gpx/i });
      fireEvent.click(removeButton);

      const confirmButton = screen.getByRole('button', { name: /sí, eliminar/i });
      fireEvent.click(confirmButton);

      expect(mockOnRemoveGPX).toHaveBeenCalledTimes(1);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for form fields', () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      expect(screen.getByLabelText(/título/i)).toHaveAttribute('aria-required', 'true');
      expect(screen.getByLabelText(/descripción/i)).toHaveAttribute('aria-required', 'true');
      expect(screen.getByLabelText(/fecha de inicio/i)).toHaveAttribute('aria-required', 'true');
    });

    it('should announce validation errors to screen readers', async () => {
      render(
        <Step2Details
          gpxFile={mockFile}
          telemetry={mockTelemetry}
          onNext={mockOnNext}
          onPrevious={mockOnPrevious}
          onCancel={mockOnCancel}
          onRemoveGPX={mockOnRemoveGPX}
        />
      );

      const titleInput = screen.getByLabelText(/título/i);
      fireEvent.change(titleInput, { target: { value: '' } });
      fireEvent.blur(titleInput);

      await waitFor(() => {
        const errorMessage = screen.getByText(/el título es obligatorio/i);
        expect(errorMessage).toHaveAttribute('role', 'alert');
      });
    });
  });
});
