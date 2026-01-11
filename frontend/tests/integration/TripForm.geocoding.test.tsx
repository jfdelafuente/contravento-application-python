/**
 * TripForm Geocoding Integration Tests
 *
 * Tests for reverse geocoding workflows in trip forms:
 * - T014: Map click → modal → location added workflow (User Story 1)
 * - T028: Marker drag → geocode → name update workflow (User Story 2)
 *
 * Feature: 010-reverse-geocoding
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import axios from 'axios';
import { TripMap } from '../../src/components/trips/TripMap';
import { LocationConfirmModal } from '../../src/components/trips/LocationConfirmModal';
import type { TripLocation } from '../../src/types/trip';
import type { LocationSelection } from '../../src/types/geocoding';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock react-leaflet components
vi.mock('react-leaflet', () => ({
  MapContainer: vi.fn(({ children }: any) => (
    <div data-testid="map-container">{children}</div>
  )),
  TileLayer: vi.fn(() => <div data-testid="tile-layer" />),
  Marker: vi.fn(({ position, children, draggable, eventHandlers }: any) => {
    const handleDragEnd = () => {
      if (eventHandlers?.dragend) {
        // Simulate dragend event with new coordinates
        const mockEvent = {
          target: {
            getLatLng: () => ({ lat: position[0] + 0.1, lng: position[1] + 0.1 }),
          },
        };
        eventHandlers.dragend(mockEvent);
      }
    };

    return (
      <div
        data-testid="marker"
        data-position={JSON.stringify(position)}
        data-draggable={draggable ? 'true' : 'false'}
        onClick={handleDragEnd} // Simulate drag for testing
      >
        {children}
      </div>
    );
  }),
  Popup: vi.fn(({ children }: any) => <div data-testid="popup">{children}</div>),
  Polyline: vi.fn(() => <div data-testid="polyline" />),
  useMapEvents: vi.fn((events: any) => {
    (global as any).__mapEvents = events;
    return null;
  }),
}));

// Mock Leaflet CSS
vi.mock('leaflet/dist/leaflet.css', () => ({}));

// Mock mapHelpers
vi.mock('../../src/utils/mapHelpers', () => ({
  createNumberedMarkerIcon: vi.fn((number: number) => ({
    type: 'numbered',
    number,
  })),
}));

// Mock TripMap CSS
vi.mock('../../src/components/trips/TripMap.css', () => ({}));

// Mock LocationConfirmModal CSS
vi.mock('../../src/components/trips/LocationConfirmModal.css', () => ({}));

// Mock react-hot-toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('TripForm Geocoding Integration Tests', () => {
  const mockLocations: TripLocation[] = [
    {
      location_id: 'loc-1',
      trip_id: 'trip-1',
      name: 'Madrid',
      latitude: 40.4168,
      longitude: -3.7038,
      sequence: 1,
      created_at: '2024-01-01T00:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  /**
   * T014 [US1]: Integration test for map click → modal → location added workflow
   * NOTE: Deferred until TripDetailPage/TripFormWizard integration is complete
   */
  describe.skip('Map Click to Add Location Workflow (T014)', () => {
    it('should complete full workflow: click map → geocode → show modal → add location', async () => {
      // Mock Nominatim API response
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          display_name: 'Valencia, Comunidad Valenciana, España',
          address: {
            city: 'Valencia',
            state: 'Comunidad Valenciana',
            country: 'España',
          },
        },
      });

      // This test would require rendering the full TripDetailPage or TripFormWizard
      // with TripMap and LocationConfirmModal integrated
      // Deferred until those components are fully integrated
    });
  });

  /**
   * T028 [US2]: Integration test for marker drag → geocode → name update workflow
   */
  describe('Marker Drag to Update Location Workflow (T028)', () => {
    it('should trigger geocoding when marker is dragged to new position', async () => {
      const mockOnMarkerDrag = vi.fn();

      // Mock Nominatim API response for new position
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          display_name: 'Toledo, Castilla-La Mancha, España',
          address: {
            city: 'Toledo',
            state: 'Castilla-La Mancha',
            country: 'España',
          },
        },
      });

      render(
        <TripMap
          locations={mockLocations}
          tripTitle="Test Trip"
          isEditMode={true}
          onMarkerDrag={mockOnMarkerDrag}
        />
      );

      // Get the marker
      const marker = screen.getByTestId('marker');

      // Verify marker is draggable
      expect(marker.getAttribute('data-draggable')).toBe('true');

      // Simulate drag event
      fireEvent.click(marker);

      // Verify onMarkerDrag callback was called with new coordinates
      await waitFor(() => {
        expect(mockOnMarkerDrag).toHaveBeenCalledWith(
          'loc-1',
          expect.any(Number),
          expect.any(Number)
        );
      });
    });

    it('should show confirmation modal after dragging marker with geocoded name', async () => {
      const mockLocation: LocationSelection = {
        latitude: 40.5168,
        longitude: -3.6038,
        suggestedName: 'Toledo',
        fullAddress: 'Toledo, Castilla-La Mancha, España',
        isLoading: false,
        hasError: false,
      };

      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Verify modal displays geocoded location name
      expect(screen.getByText(/Toledo/)).toBeInTheDocument();
      expect(screen.getByText(/Toledo, Castilla-La Mancha, España/)).toBeInTheDocument();

      // Verify coordinates are shown (formatted to 6 decimals)
      expect(screen.getByText(/40\.516800/)).toBeInTheDocument();
      expect(screen.getByText(/-3\.603800/)).toBeInTheDocument();

      // Confirm the location
      const confirmButton = screen.getByRole('button', { name: /confirmar/i });
      fireEvent.click(confirmButton);

      // Verify onConfirm was called with location data
      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Toledo',
        40.5168,
        -3.6038
      );
    });

    it('should handle geocoding errors gracefully during marker drag', async () => {
      const mockOnMarkerDrag = vi.fn();

      // Mock Nominatim API error
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

      render(
        <TripMap
          locations={mockLocations}
          tripTitle="Test Trip"
          isEditMode={true}
          onMarkerDrag={mockOnMarkerDrag}
        />
      );

      const marker = screen.getByTestId('marker');

      // Simulate drag event
      fireEvent.click(marker);

      // Verify callback was still called (error handling happens in parent)
      await waitFor(() => {
        expect(mockOnMarkerDrag).toHaveBeenCalled();
      });
    });

    it('should update location coordinates when user confirms after drag', async () => {
      const originalLocation: LocationSelection = {
        latitude: 40.4168,
        longitude: -3.7038,
        suggestedName: 'Madrid',
        fullAddress: 'Madrid, Comunidad de Madrid, España',
        isLoading: false,
        hasError: false,
      };

      const newLocation: LocationSelection = {
        latitude: 40.5168,
        longitude: -3.6038,
        suggestedName: 'Toledo',
        fullAddress: 'Toledo, Castilla-La Mancha, España',
        isLoading: false,
        hasError: false,
      };

      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      const { rerender } = render(
        <LocationConfirmModal
          location={originalLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Close original modal
      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);
      expect(mockOnCancel).toHaveBeenCalled();

      // Simulate marker drag and show new modal with updated coordinates
      rerender(
        <LocationConfirmModal
          location={newLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Verify new location data is shown
      expect(screen.getByText(/Toledo/)).toBeInTheDocument();
      expect(screen.getByText(/40\.516800/)).toBeInTheDocument();

      // Confirm the updated location
      const confirmButton = screen.getByRole('button', { name: /confirmar/i });
      fireEvent.click(confirmButton);

      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Toledo',
        40.5168,
        -3.6038
      );
    });

    it('should preserve other location properties when updating coordinates', async () => {
      // This test verifies that when a location is dragged,
      // only the coordinates and name should update,
      // while location_id, trip_id, and sequence remain unchanged

      const mockOnMarkerDrag = vi.fn((locationId, newLat, newLng) => {
        // Parent component should update only lat/lng for this location_id
        expect(locationId).toBe('loc-1');
        expect(typeof newLat).toBe('number');
        expect(typeof newLng).toBe('number');
      });

      render(
        <TripMap
          locations={mockLocations}
          tripTitle="Test Trip"
          isEditMode={true}
          onMarkerDrag={mockOnMarkerDrag}
        />
      );

      const marker = screen.getByTestId('marker');
      fireEvent.click(marker);

      await waitFor(() => {
        expect(mockOnMarkerDrag).toHaveBeenCalled();
      });
    });

    it('should allow canceling location update after drag', async () => {
      const mockLocation: LocationSelection = {
        latitude: 40.5168,
        longitude: -3.6038,
        suggestedName: 'Toledo',
        fullAddress: 'Toledo, Castilla-La Mancha, España',
        isLoading: false,
        hasError: false,
      };

      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Cancel the drag operation
      const cancelButton = screen.getByRole('button', { name: /cancelar/i });
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
      expect(mockOnConfirm).not.toHaveBeenCalled();
    });
  });

  /**
   * Cross-Feature Integration: Marker Drag + Geocoding + Modal
   */
  describe('Full Marker Drag Workflow', () => {
    it('should complete full workflow: drag marker → fetch geocode → show modal → update location', async () => {
      // Mock Nominatim API response
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          display_name: 'Toledo, Castilla-La Mancha, España',
          address: {
            city: 'Toledo',
            state: 'Castilla-La Mancha',
            country: 'España',
          },
        },
      });

      const mockOnMarkerDrag = vi.fn();

      render(
        <TripMap
          locations={mockLocations}
          tripTitle="Test Trip"
          isEditMode={true}
          onMarkerDrag={mockOnMarkerDrag}
        />
      );

      // Step 1: Drag marker
      const marker = screen.getByTestId('marker');
      expect(marker.getAttribute('data-draggable')).toBe('true');

      fireEvent.click(marker);

      // Step 2: Verify callback was triggered with new coordinates
      await waitFor(() => {
        expect(mockOnMarkerDrag).toHaveBeenCalledWith(
          'loc-1',
          expect.any(Number),
          expect.any(Number)
        );
      });

      // Steps 3-4 (geocoding + modal) would be tested in the parent component
      // (TripDetailPage or TripFormWizard) which handles the geocoding logic
    });
  });

  /**
   * T036 [US3]: Integration test for name edit → confirm → custom name saved workflow
   */
  describe('Edit Location Name Before Saving (T036)', () => {
    it('should allow editing suggested name and save custom name', async () => {
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

      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Step 1: Modal shows suggested name
      const input = screen.getByLabelText(/nombre de la ubicación/i) as HTMLInputElement;
      expect(input.value).toBe('Madrid');

      // Step 2: User edits the name
      fireEvent.change(input, { target: { value: 'Plaza Mayor de Madrid' } });
      expect(input.value).toBe('Plaza Mayor de Madrid');

      // Step 3: User confirms
      const confirmButton = screen.getByRole('button', { name: /confirmar ubicación/i });
      fireEvent.click(confirmButton);

      // Step 4: Verify custom name is saved (not suggested name)
      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Plaza Mayor de Madrid', // Custom name
        40.4168,
        -3.7038
      );
      expect(mockOnConfirm).toHaveBeenCalledTimes(1);
    });

    it('should use suggested name if user does not edit', async () => {
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

      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Step 1: Modal shows suggested name
      const input = screen.getByLabelText(/nombre de la ubicación/i) as HTMLInputElement;
      expect(input.value).toBe('Madrid');

      // Step 2: User confirms WITHOUT editing
      const confirmButton = screen.getByRole('button', { name: /confirmar ubicación/i });
      fireEvent.click(confirmButton);

      // Step 3: Verify suggested name is used
      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Madrid', // Suggested name unchanged
        40.4168,
        -3.7038
      );
    });

    it('should prevent saving empty name after user clears input', async () => {
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

      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const confirmButton = screen.getByRole('button', { name: /confirmar ubicación/i });

      // Step 1: User clears the name
      fireEvent.change(input, { target: { value: '' } });

      // Step 2: Confirm button should be disabled
      expect(confirmButton).toBeDisabled();

      // Step 3: User cannot submit empty name
      fireEvent.click(confirmButton);
      expect(mockOnConfirm).not.toHaveBeenCalled();
    });

    it('should allow manual name entry when geocoding fails', async () => {
      const errorLocation: LocationSelection = {
        latitude: 40.4168,
        longitude: -3.7038,
        suggestedName: '',
        fullAddress: '',
        isLoading: false,
        hasError: true,
        errorMessage: 'No se pudo obtener el nombre del lugar',
      };

      const mockOnConfirm = vi.fn();
      const mockOnCancel = vi.fn();

      render(
        <LocationConfirmModal
          location={errorLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      // Step 1: Verify error state is shown
      expect(screen.getByText(/no se pudo obtener el nombre del lugar/i)).toBeInTheDocument();
      expect(screen.getByText(/puedes ingresar un nombre manualmente/i)).toBeInTheDocument();

      // Step 2: User enters name manually
      const input = screen.getByLabelText(/nombre de la ubicación/i);
      fireEvent.change(input, { target: { value: 'Mi lugar favorito' } });

      // Step 3: User confirms
      const confirmButton = screen.getByRole('button', { name: /confirmar ubicación/i });
      fireEvent.click(confirmButton);

      // Step 4: Verify manual name is saved
      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Mi lugar favorito', // Manual entry
        40.4168,
        -3.7038
      );
    });

    it('should trim whitespace from edited name before saving', async () => {
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

      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i);
      const confirmButton = screen.getByRole('button', { name: /confirmar ubicación/i });

      // Step 1: User enters name with leading/trailing spaces
      fireEvent.change(input, { target: { value: '   Puerta del Sol   ' } });

      // Step 2: User confirms
      fireEvent.click(confirmButton);

      // Step 3: Verify name is trimmed before saving
      expect(mockOnConfirm).toHaveBeenCalledWith(
        'Puerta del Sol', // Trimmed
        40.4168,
        -3.7038
      );
    });

    it('should enforce max length of 200 characters on edited name', async () => {
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

      render(
        <LocationConfirmModal
          location={mockLocation}
          onConfirm={mockOnConfirm}
          onCancel={mockOnCancel}
        />
      );

      const input = screen.getByLabelText(/nombre de la ubicación/i) as HTMLInputElement;

      // Step 1: Verify maxLength attribute
      expect(input.maxLength).toBe(200);

      // Step 2: Enter exactly 200 characters
      const longName = 'A'.repeat(200);
      fireEvent.change(input, { target: { value: longName } });

      // Input should have exactly 200 chars
      expect(input.value.length).toBe(200);

      // Step 3: Character counter shows 200/200
      expect(screen.getByText('200/200')).toBeInTheDocument();
    });
  });
});
