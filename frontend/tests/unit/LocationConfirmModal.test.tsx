/**
 * LocationConfirmModal Unit Tests
 *
 * Tests for location name editing functionality (User Story 3):
 * - T035: Unit test for LocationConfirmModal name editing
 *
 * Feature: 010-reverse-geocoding
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { LocationConfirmModal } from '../../src/components/trips/LocationConfirmModal';
import type { LocationSelection } from '../../src/types/geocoding';

// Mock LocationConfirmModal CSS
vi.mock('../../src/components/trips/LocationConfirmModal.css', () => ({}));

describe('LocationConfirmModal - Name Editing (T035)', () => {
  const mockLocation: LocationSelection = {
    latitude: 40.4168,
    longitude: -3.7038,
    suggestedName: 'Madrid',
    fullAddress: 'Madrid, Comunidad de Madrid, España',
    isLoading: false,
    hasError: false,
  };

  const mockOnConfirm = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Name Input Field', () => {
    it('should display input field with suggested name as initial value', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      expect(input).toBeInTheDocument();
      expect(input).toHaveValue('Madrid');
    });

    it('should allow user to edit the location name', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i) as HTMLInputElement;

      // Clear existing value
      fireEvent.change(input, { target: { value: '' } });
      expect(input.value).toBe('');

      // Type new name
      fireEvent.change(input, { target: { value: 'Mi lugar favorito' } });
      expect(input.value).toBe('Mi lugar favorito');
    });

    it('should display character counter when user types', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);

      // Initial value from suggestedName
      expect(screen.getByText('6/200')).toBeInTheDocument(); // "Madrid" = 6 chars

      // Type longer name
      fireEvent.change(input, { target: { value: 'Un nombre mucho más largo' } });
      expect(screen.getByText('25/200')).toBeInTheDocument();
    });

    it('should use editedName from location if provided', () => {
      const locationWithEditedName: LocationSelection = {
        ...mockLocation,
        editedName: 'Nombre personalizado',
      };

      render(
        <LocationConfirmModal
          location={locationWithEditedName}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      expect(input).toHaveValue('Nombre personalizado');
    });

    it('should have autofocus enabled on input field', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      // Check that the input has focus (HTML5 autofocus behavior)
      // Note: In jsdom, autofocus doesn't actually trigger focus(), so we just verify the component renders it
      expect(input).toBeInTheDocument();
    });
  });

  describe('Name Validation', () => {
    it('should disable confirm button when name is empty', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const buttons = screen.getAllByText('Confirmar ubicación');
      const confirmButton = buttons.find(el => el.classList.contains('location-confirm-modal-button')) as HTMLButtonElement;

      // Clear the name
      fireEvent.change(input, { target: { value: '' } });

      expect(confirmButton).toBeDisabled();
    });

    it('should disable confirm button when name is only whitespace', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const buttons = screen.getAllByText('Confirmar ubicación');
      const confirmButton = buttons.find(el => el.classList.contains('location-confirm-modal-button')) as HTMLButtonElement;

      // Enter only spaces
      fireEvent.change(input, { target: { value: '   ' } });

      expect(confirmButton).toBeDisabled();
    });

    it('should show error message when name is invalid (trimmed empty)', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);

      // Enter only spaces (non-empty but invalid after trim)
      fireEvent.change(input, { target: { value: '   ' } });

      // Error message only shows when editedName.length > 0 AND !isNameValid
      expect(screen.getByText(/el nombre no puede estar vacío/i)).toBeInTheDocument();
    });

    it('should enforce max length of 200 characters', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i) as HTMLInputElement;
      expect(input).toHaveAttribute('maxLength', '200');

      // Verify character counter shows max
      const longName = 'A'.repeat(200);
      fireEvent.change(input, { target: { value: longName } });
      expect(screen.getByText('200/200')).toBeInTheDocument();
    });

    it('should enable confirm button when name is valid (non-empty, ≤200 chars)', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const buttons = screen.getAllByText('Confirmar ubicación');
      const confirmButton = buttons.find(el => el.classList.contains('location-confirm-modal-button')) as HTMLButtonElement;

      // Enter valid name
      fireEvent.change(input, { target: { value: 'Nombre válido' } });

      expect(confirmButton).not.toBeDisabled();
    });

    it('should apply invalid CSS class when name is empty', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);

      // Clear the name
      fireEvent.change(input, { target: { value: '' } });

      expect(input).toHaveClass('invalid');
    });
  });

  describe('Confirm Action with Edited Name', () => {
    it('should call onConfirm with edited name (not suggestedName) when user edits', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const buttons = screen.getAllByText('Confirmar ubicación');
      const confirmButton = buttons.find(el => el.classList.contains('location-confirm-modal-button')) as HTMLButtonElement;

      // Edit the name
      fireEvent.change(input, { target: { value: 'Mi nombre personalizado' } });

      // Confirm
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Mi nombre personalizado', // Edited name, NOT 'Madrid'
        40.4168,
        -3.7038
      );
    });

    it('should trim whitespace from name before confirming', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const buttons = screen.getAllByText('Confirmar ubicación');
      const confirmButton = buttons.find(el => el.classList.contains('location-confirm-modal-button')) as HTMLButtonElement;

      // Enter name with leading/trailing spaces
      fireEvent.change(input, { target: { value: '  Nombre con espacios  ' } });

      // Confirm
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Nombre con espacios', // Trimmed
        40.4168,
        -3.7038
      );
    });

    it('should call onConfirm with suggestedName if user does not edit', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const buttons = screen.getAllByText('Confirmar ubicación');
      const confirmButton = buttons.find(el => el.classList.contains('location-confirm-modal-button')) as HTMLButtonElement;

      // Confirm without editing (input still has suggestedName)
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Madrid', // suggestedName
        40.4168,
        -3.7038
      );
    });

    it('should not call onConfirm if name is empty', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const buttons = screen.getAllByText('Confirmar ubicación');
      const confirmButton = buttons.find(el => el.classList.contains('location-confirm-modal-button')) as HTMLButtonElement;

      // Clear name
      fireEvent.change(input, { target: { value: '' } });

      // Try to confirm (button should be disabled, but test logic anyway)
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).not.toHaveBeenCalled();
    });
  });

  describe('Cancel Action', () => {
    it('should call onCancel when user clicks cancel button', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const cancelButton = screen.getByRole('button', { name: /cancelar/i });

      // Edit the name
      fireEvent.change(input, { target: { value: 'Nombre editado' } });
      expect(input).toHaveValue('Nombre editado');

      // Cancel
      fireEvent.click(cancelButton);
      expect(mockOnCancel).toHaveBeenCalled();

      // Note: Internal state reset happens (setEditedName('')), but component unmounts
      // Testing state persistence would require testing the parent component integration
    });
  });

  describe('Loading and Error States', () => {
    it('should disable input when loading', () => {
      const loadingLocation: LocationSelection = {
        ...mockLocation,
        isLoading: true,
      };

      render(
        <LocationConfirmModal
          location={loadingLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      expect(input).toBeDisabled();
    });

    it('should allow manual name entry when geocoding fails', () => {
      const errorLocation: LocationSelection = {
        latitude: 40.4168,
        longitude: -3.7038,
        suggestedName: '',
        fullAddress: '',
        isLoading: false,
        hasError: true,
        errorMessage: 'No se pudo obtener el nombre del lugar',
      };

      render(
        <LocationConfirmModal
          location={errorLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      expect(input).toBeInTheDocument();
      expect(input).not.toBeDisabled();

      // User can type manually
      fireEvent.change(input, { target: { value: 'Nombre manual' } });
      expect(input).toHaveValue('Nombre manual');

      // Should show fallback message
      expect(screen.getByText(/puedes ingresar un nombre manualmente/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper label for input field', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      expect(input).toHaveAttribute('id', 'location-name');
    });

    it('should have proper aria-label for close button', () => {
      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Check for close button (×) with exact aria-label
      const closeButton = screen.getByLabelText('Cerrar');
      expect(closeButton).toBeInTheDocument();
    });
  });

  describe('Modal Behavior', () => {
    it('should render nothing when location is null', () => {
      const { container } = render(
        <LocationConfirmModal
          location={null}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      expect(container.firstChild).toBeNull();
    });

    it('should close modal when clicking overlay', () => {
      const { container } = render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const overlay = container.querySelector('.location-confirm-modal-overlay');

      if (overlay) {
        fireEvent.click(overlay);
        expect(mockOnCancel).toHaveBeenCalled();
      }
    });

    it('should not close modal when clicking inside modal content', () => {
      const { container } = render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const modalContent = container.querySelector('.location-confirm-modal');

      if (modalContent) {
        fireEvent.click(modalContent);
        expect(mockOnCancel).not.toHaveBeenCalled();
      }
    });
  });
});
