/**
 * TripForm Integration Tests - GPS Coordinates Editing
 *
 * Tests for User Story 3: Edit GPS Coordinates for Existing Trips
 *
 * Tests:
 * - T057: Trip edit form with coordinate updates
 * - T058: Removing coordinates from locations
 * - Additional: Adding coordinates to location without GPS
 * - Additional: Validation in edit mode
 *
 * Phase 6: User Story 3 - Edit GPS Coordinates (P3)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom/vitest';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../src/contexts/AuthContext';
import { TripEditPage } from '../../src/pages/TripEditPage';
import * as tripService from '../../src/services/tripService';
import type { Trip } from '../../src/types/trip';

// Mock trip service
vi.mock('../../src/services/tripService');

// Mock react-router-dom hooks
const mockNavigate = vi.fn();
const mockParams = { tripId: 'test-trip-123' };

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => mockParams,
  };
});

// Mock toast
vi.mock('react-hot-toast', () => ({
  default: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock useTripForm hook
vi.mock('../../src/hooks/useTripForm', () => ({
  useTripForm: () => ({
    handleSubmit: vi.fn(),
    isSubmitting: false,
  }),
}));

describe('TripForm Integration Tests - GPS Coordinates Editing', () => {
  // Mock trip data
  const mockTripWithCoordinates: Trip = {
    trip_id: 'test-trip-123',
    user_id: 'user-123',
    title: 'Ruta Test con Coordenadas',
    description: 'Descripción de prueba con más de 50 caracteres para validación',
    start_date: '2024-01-15',
    end_date: '2024-01-16',
    distance_km: 125.5,
    difficulty: 'moderate',
    status: 'published',
    locations: [
      {
        location_id: 'loc-1',
        trip_id: 'test-trip-123',
        name: 'Madrid',
        latitude: 40.416775,
        longitude: -3.703790,
        sequence: 1,
        created_at: '2024-01-15T10:00:00Z',
      },
      {
        location_id: 'loc-2',
        trip_id: 'test-trip-123',
        name: 'Valencia',
        latitude: 39.469907,
        longitude: -0.376288,
        sequence: 2,
        created_at: '2024-01-15T10:00:00Z',
      },
    ],
    tags: [],
    photos: [],
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
  };

  const mockTripWithoutCoordinates: Trip = {
    ...mockTripWithCoordinates,
    locations: [
      {
        location_id: 'loc-1',
        trip_id: 'test-trip-123',
        name: 'Sevilla',
        latitude: null,
        longitude: null,
        sequence: 1,
        created_at: '2024-01-15T10:00:00Z',
      },
      {
        location_id: 'loc-2',
        trip_id: 'test-trip-123',
        name: 'Córdoba',
        latitude: null,
        longitude: null,
        sequence: 2,
        created_at: '2024-01-15T10:00:00Z',
      },
    ],
  };

  const mockUser = {
    user_id: 'user-123',
    username: 'testuser',
    email: 'test@example.com',
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock getTripById to return trip data
    vi.mocked(tripService.getTripById).mockResolvedValue(mockTripWithCoordinates);

    // Mock updateTrip to return updated trip
    vi.mocked(tripService.updateTrip).mockResolvedValue(mockTripWithCoordinates);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * Helper to render TripEditPage with auth context
   */
  const renderTripEditPage = (user = mockUser) => {
    return render(
      <BrowserRouter>
        <AuthProvider value={{ user, login: vi.fn(), logout: vi.fn(), isLoading: false }}>
          <TripEditPage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  /**
   * T057: Trip edit form with coordinate updates
   *
   * Verifies that existing coordinates load into the form and can be updated
   */
  describe('T057: Edit trip with coordinate updates', () => {
    it('should load existing coordinates into form inputs', async () => {
      renderTripEditPage();

      // Wait for trip data to load
      await waitFor(() => {
        expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
      });

      // Verify latitude and longitude inputs are populated
      const latitudeInput = screen.getByLabelText(/latitud.*madrid/i);
      const longitudeInput = screen.getByLabelText(/longitud.*madrid/i);

      expect(latitudeInput).toHaveValue(40.416775);
      expect(longitudeInput).toHaveValue(-3.703790);

      // Verify second location coordinates
      await waitFor(() => {
        expect(screen.getByDisplayValue('Valencia')).toBeInTheDocument();
      });

      const lat2Input = screen.getByLabelText(/latitud.*valencia/i);
      const lng2Input = screen.getByLabelText(/longitud.*valencia/i);

      expect(lat2Input).toHaveValue(39.469907);
      expect(lng2Input).toHaveValue(-0.376288);
    });

    it('should update coordinates when user changes values', async () => {
      const user = userEvent.setup();
      renderTripEditPage();

      // Wait for form to load
      await waitFor(() => {
        expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
      });

      // Find and update latitude input
      const latitudeInput = screen.getByLabelText(/latitud.*madrid/i);

      // Clear and enter new value
      await user.clear(latitudeInput);
      await user.type(latitudeInput, '40.5');

      // Find and update longitude input
      const longitudeInput = screen.getByLabelText(/longitud.*madrid/i);
      await user.clear(longitudeInput);
      await user.type(longitudeInput, '-3.8');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify updateTrip was called with new coordinates
      await waitFor(() => {
        expect(tripService.updateTrip).toHaveBeenCalledWith(
          'test-trip-123',
          expect.objectContaining({
            locations: expect.arrayContaining([
              expect.objectContaining({
                name: 'Madrid',
                latitude: 40.5,
                longitude: -3.8,
              }),
            ]),
          })
        );
      });
    });

    it('should validate coordinate ranges when editing', async () => {
      const user = userEvent.setup();
      renderTripEditPage();

      await waitFor(() => {
        expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
      });

      // Enter invalid latitude (> 90)
      const latitudeInput = screen.getByLabelText(/latitud.*madrid/i);
      await user.clear(latitudeInput);
      await user.type(latitudeInput, '100');

      // Try to submit
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify error message appears
      await waitFor(() => {
        expect(
          screen.getByText(/latitud debe estar entre -90 y 90/i)
        ).toBeInTheDocument();
      });

      // Verify updateTrip was NOT called
      expect(tripService.updateTrip).not.toHaveBeenCalled();
    });
  });

  /**
   * T058: Removing coordinates from locations
   *
   * Verifies that coordinates can be removed from a location
   */
  describe('T058: Remove coordinates from locations', () => {
    it('should allow clearing coordinates from a location', async () => {
      const user = userEvent.setup();
      renderTripEditPage();

      await waitFor(() => {
        expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
      });

      // Clear both latitude and longitude
      const latitudeInput = screen.getByLabelText(/latitud.*madrid/i);
      const longitudeInput = screen.getByLabelText(/longitud.*madrid/i);

      await user.clear(latitudeInput);
      await user.clear(longitudeInput);

      // Submit form
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify updateTrip was called with null coordinates
      await waitFor(() => {
        expect(tripService.updateTrip).toHaveBeenCalledWith(
          'test-trip-123',
          expect.objectContaining({
            locations: expect.arrayContaining([
              expect.objectContaining({
                name: 'Madrid',
                latitude: null,
                longitude: null,
              }),
            ]),
          })
        );
      });
    });

    it('should not allow partial coordinates (only latitude)', async () => {
      const user = userEvent.setup();
      renderTripEditPage();

      await waitFor(() => {
        expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
      });

      // Clear only longitude (leave latitude)
      const longitudeInput = screen.getByLabelText(/longitud.*madrid/i);
      await user.clear(longitudeInput);

      // Try to submit
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify error message
      await waitFor(() => {
        expect(
          screen.getByText(/debes proporcionar la longitud si ingresas latitud/i)
        ).toBeInTheDocument();
      });

      expect(tripService.updateTrip).not.toHaveBeenCalled();
    });

    it('should not allow partial coordinates (only longitude)', async () => {
      const user = userEvent.setup();
      renderTripEditPage();

      await waitFor(() => {
        expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
      });

      // Clear only latitude (leave longitude)
      const latitudeInput = screen.getByLabelText(/latitud.*madrid/i);
      await user.clear(latitudeInput);

      // Try to submit
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify error message
      await waitFor(() => {
        expect(
          screen.getByText(/debes proporcionar la latitud si ingresas longitud/i)
        ).toBeInTheDocument();
      });

      expect(tripService.updateTrip).not.toHaveBeenCalled();
    });
  });

  /**
   * Additional Test: Adding coordinates to location without GPS
   *
   * Verifies that coordinates can be added to a location that previously had none
   */
  describe('Additional: Add coordinates to location without GPS', () => {
    it('should allow adding coordinates to location without GPS', async () => {
      const user = userEvent.setup();

      // Mock trip without coordinates
      vi.mocked(tripService.getTripById).mockResolvedValue(mockTripWithoutCoordinates);

      renderTripEditPage();

      await waitFor(() => {
        expect(screen.getByDisplayValue('Sevilla')).toBeInTheDocument();
      });

      // Verify inputs are empty
      const latitudeInput = screen.getByLabelText(/latitud.*sevilla/i);
      const longitudeInput = screen.getByLabelText(/longitud.*sevilla/i);

      expect(latitudeInput).toHaveValue(null);
      expect(longitudeInput).toHaveValue(null);

      // Add coordinates
      await user.type(latitudeInput, '37.389092');
      await user.type(longitudeInput, '-5.984459');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify updateTrip was called with new coordinates
      await waitFor(() => {
        expect(tripService.updateTrip).toHaveBeenCalledWith(
          'test-trip-123',
          expect.objectContaining({
            locations: expect.arrayContaining([
              expect.objectContaining({
                name: 'Sevilla',
                latitude: 37.389092,
                longitude: -5.984459,
              }),
            ]),
          })
        );
      });
    });

    it('should handle mixed locations (some with GPS, some without)', async () => {
      const user = userEvent.setup();

      // Mock trip with mixed locations
      const mixedTrip: Trip = {
        ...mockTripWithCoordinates,
        locations: [
          {
            location_id: 'loc-1',
            trip_id: 'test-trip-123',
            name: 'Granada',
            latitude: 37.177336,
            longitude: -3.598557,
            sequence: 1,
            created_at: '2024-01-15T10:00:00Z',
          },
          {
            location_id: 'loc-2',
            trip_id: 'test-trip-123',
            name: 'Córdoba',
            latitude: null,
            longitude: null,
            sequence: 2,
            created_at: '2024-01-15T10:00:00Z',
          },
        ],
      };

      vi.mocked(tripService.getTripById).mockResolvedValue(mixedTrip);

      renderTripEditPage();

      await waitFor(() => {
        expect(screen.getByDisplayValue('Granada')).toBeInTheDocument();
        expect(screen.getByDisplayValue('Córdoba')).toBeInTheDocument();
      });

      // Granada should have coordinates
      const granadaLat = screen.getByLabelText(/latitud.*granada/i);
      expect(granadaLat).toHaveValue(37.177336);

      // Córdoba should not have coordinates
      const cordobaLat = screen.getByLabelText(/latitud.*córdoba/i);
      expect(cordobaLat).toHaveValue(null);

      // Add coordinates to Córdoba
      const cordobaLng = screen.getByLabelText(/longitud.*córdoba/i);
      await user.type(cordobaLat, '37.888175');
      await user.type(cordobaLng, '-4.779383');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify both locations saved correctly
      await waitFor(() => {
        expect(tripService.updateTrip).toHaveBeenCalledWith(
          'test-trip-123',
          expect.objectContaining({
            locations: expect.arrayContaining([
              expect.objectContaining({
                name: 'Granada',
                latitude: 37.177336,
                longitude: -3.598557,
              }),
              expect.objectContaining({
                name: 'Córdoba',
                latitude: 37.888175,
                longitude: -4.779383,
              }),
            ]),
          })
        );
      });
    });
  });

  /**
   * Additional Test: Navigation after successful update
   */
  describe('Navigation after update', () => {
    it('should navigate to trip detail page after successful update', async () => {
      const user = userEvent.setup();
      renderTripEditPage();

      await waitFor(() => {
        expect(screen.getByDisplayValue('Madrid')).toBeInTheDocument();
      });

      // Submit form
      const submitButton = screen.getByRole('button', { name: /guardar/i });
      await user.click(submitButton);

      // Verify navigation was called
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/trips/test-trip-123');
      });
    });
  });
});
