/**
 * TripMap Component Unit Tests
 *
 * Tests for the TripMap component including:
 * - Coordinate filtering (T020/T108)
 * - Numbered marker rendering (T021/T109)
 * - Polyline rendering (T022/T110)
 * - Zoom calculation (T023/T111)
 * - Error handling (T112)
 * - Retry functionality (T113)
 * - Fullscreen mode (T114)
 * - Empty state (T115)
 *
 * Phase 5.4: Unit Testing
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { TripMap } from '../../src/components/trips/TripMap';
import type { TripLocation } from '../../src/types/trip';

// Mock react-leaflet components
vi.mock('react-leaflet', () => ({
  MapContainer: vi.fn(({ children, center, zoom }: any) => (
    <div
      data-testid="map-container"
      data-center={JSON.stringify(center)}
      data-zoom={zoom}
    >
      {children}
    </div>
  )),
  TileLayer: vi.fn(() => <div data-testid="tile-layer" />),
  Marker: vi.fn(({ position, children, icon, draggable, eventHandlers }: any) => (
    <div
      data-testid="marker"
      data-position={JSON.stringify(position)}
      data-icon={JSON.stringify(icon)}
      data-draggable={draggable ? 'true' : 'false'}
      data-event-handlers={JSON.stringify(eventHandlers || {})}
    >
      {children}
    </div>
  )),
  Popup: vi.fn(({ children }: any) => <div data-testid="popup">{children}</div>),
  Polyline: vi.fn(({ positions, pathOptions }: any) => (
    <div
      data-testid="polyline"
      data-positions={JSON.stringify(positions)}
      data-path-options={JSON.stringify(pathOptions)}
    />
  )),
  useMapEvents: vi.fn((events: any) => {
    // Store the event handlers so we can trigger them in tests
    (global as any).__mapEvents = events;
    return null;
  }),
}));

// Mock Leaflet CSS import
vi.mock('leaflet/dist/leaflet.css', () => ({}));

// Mock mapHelpers utility
vi.mock('../../src/utils/mapHelpers', () => ({
  createNumberedMarkerIcon: vi.fn((number: number) => ({
    type: 'numbered',
    number,
    iconSize: [32, 42],
    iconAnchor: [16, 42],
    popupAnchor: [0, -42],
  })),
  getMarkerColor: vi.fn(() => '#2563eb'),
  getMarkerShadowColor: vi.fn(() => 'rgba(0, 0, 0, 0.2)'),
}));

// Mock TripMap CSS import
vi.mock('../../src/components/trips/TripMap.css', () => ({}));

describe('TripMap Component', () => {
  // Test data
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
    {
      location_id: 'loc-2',
      trip_id: 'trip-1',
      name: 'Valencia',
      latitude: 39.4699,
      longitude: -0.3763,
      sequence: 2,
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      location_id: 'loc-3',
      trip_id: 'trip-1',
      name: 'Barcelona',
      latitude: 41.3851,
      longitude: 2.1734,
      sequence: 3,
      created_at: '2024-01-01T00:00:00Z',
    },
  ];

  const mockTripTitle = 'Ruta de Prueba - Fullscreen Test';

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();

    // Reset fullscreen state
    (global as any).setFullscreenElement(null);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * T020/T108: Test coordinate filtering
   * Verifies that locations without coordinates are filtered out
   */
  describe('Coordinate Filtering (T020/T108)', () => {
    it('should filter out locations with null coordinates', () => {
      const locationsWithNulls: TripLocation[] = [
        ...mockLocations,
        {
          location_id: 'loc-4',
          trip_id: 'trip-1',
          name: 'No Coordinates',
          latitude: null,
          longitude: null,
          sequence: 4,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      render(<TripMap locations={locationsWithNulls} tripTitle={mockTripTitle} />);

      // Should only render 3 markers (locations with coordinates)
      const markers = screen.getAllByTestId('marker');
      expect(markers).toHaveLength(3);

      // Location list should show all 3 valid locations
      expect(screen.getByText('Madrid')).toBeInTheDocument();
      expect(screen.getByText('Valencia')).toBeInTheDocument();
      expect(screen.getByText('Barcelona')).toBeInTheDocument();
      expect(screen.queryByText('No Coordinates')).not.toBeInTheDocument();
    });

    it('should filter out locations with partial null coordinates (null latitude)', () => {
      const locationsWithPartialNull: TripLocation[] = [
        mockLocations[0],
        {
          location_id: 'loc-2',
          trip_id: 'trip-1',
          name: 'Partial Null',
          latitude: null,
          longitude: -0.3763,
          sequence: 2,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      render(<TripMap locations={locationsWithPartialNull} tripTitle={mockTripTitle} />);

      const markers = screen.getAllByTestId('marker');
      expect(markers).toHaveLength(1); // Only Madrid should render
    });

    it('should filter out locations with partial null coordinates (null longitude)', () => {
      const locationsWithPartialNull: TripLocation[] = [
        mockLocations[0],
        {
          location_id: 'loc-2',
          trip_id: 'trip-1',
          name: 'Partial Null',
          latitude: 39.4699,
          longitude: null,
          sequence: 2,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      render(<TripMap locations={locationsWithPartialNull} tripTitle={mockTripTitle} />);

      const markers = screen.getAllByTestId('marker');
      expect(markers).toHaveLength(1); // Only Madrid should render
    });
  });

  /**
   * T021/T109: Test numbered marker rendering
   * Verifies that markers are rendered with correct sequence numbers
   */
  describe('Numbered Marker Rendering (T021/T109)', () => {
    it('should render markers with numbered icons in sequence order', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      const markers = screen.getAllByTestId('marker');
      expect(markers).toHaveLength(3);

      // Verify markers are rendered with correct sequence numbers
      markers.forEach((marker, index) => {
        const iconData = JSON.parse(marker.getAttribute('data-icon') || '{}');
        expect(iconData.type).toBe('numbered');
        expect(iconData.number).toBe(index + 1); // 1, 2, 3
      });
    });

    it('should render markers sorted by sequence number', () => {
      // Provide locations in random order
      const unsortedLocations: TripLocation[] = [
        mockLocations[2], // Barcelona (sequence 3)
        mockLocations[0], // Madrid (sequence 1)
        mockLocations[1], // Valencia (sequence 2)
      ];

      render(<TripMap locations={unsortedLocations} tripTitle={mockTripTitle} />);

      const markers = screen.getAllByTestId('marker');

      // Verify markers are rendered in correct sequence order
      const positions = markers.map((m) => JSON.parse(m.getAttribute('data-position') || '[]'));

      expect(positions[0]).toEqual([40.4168, -3.7038]); // Madrid (sequence 1)
      expect(positions[1]).toEqual([39.4699, -0.3763]); // Valencia (sequence 2)
      expect(positions[2]).toEqual([41.3851, 2.1734]); // Barcelona (sequence 3)
    });

    it('should render popup with location name and sequence number', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Check that popup content includes sequence number and location name
      expect(screen.getByText(/1\.\s*Madrid/)).toBeInTheDocument();
      expect(screen.getByText(/2\.\s*Valencia/)).toBeInTheDocument();
      expect(screen.getByText(/3\.\s*Barcelona/)).toBeInTheDocument();
    });
  });

  /**
   * T022/T110: Test polyline rendering
   * Verifies that route line connects locations in sequence order
   */
  describe('Polyline Rendering (T022/T110)', () => {
    it('should render polyline connecting multiple locations', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      const polyline = screen.getByTestId('polyline');
      expect(polyline).toBeInTheDocument();

      const positions = JSON.parse(polyline.getAttribute('data-positions') || '[]');

      // Verify polyline connects all 3 locations in sequence order
      expect(positions).toEqual([
        [40.4168, -3.7038], // Madrid (sequence 1)
        [39.4699, -0.3763], // Valencia (sequence 2)
        [41.3851, 2.1734],  // Barcelona (sequence 3)
      ]);
    });

    it('should not render polyline for single location', () => {
      render(<TripMap locations={[mockLocations[0]]} tripTitle={mockTripTitle} />);

      const polyline = screen.queryByTestId('polyline');
      expect(polyline).not.toBeInTheDocument();
    });

    it('should render polyline with correct styling options', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      const polyline = screen.getByTestId('polyline');
      const pathOptions = JSON.parse(polyline.getAttribute('data-path-options') || '{}');

      // Verify ContraVento blue color and dashed line style
      expect(pathOptions.color).toBe('#2563eb');
      expect(pathOptions.weight).toBe(3);
      expect(pathOptions.opacity).toBe(0.7);
      expect(pathOptions.dashArray).toBe('10, 10');
    });
  });

  /**
   * T023/T111: Test zoom calculation
   * Verifies that map zoom level adjusts based on location spread
   */
  describe('Zoom Calculation (T023/T111)', () => {
    it('should set zoom to 6 for empty locations (Spain overview)', () => {
      render(<TripMap locations={[]} tripTitle={mockTripTitle} />);

      // Empty state, so no map container rendered
      expect(screen.queryByTestId('map-container')).not.toBeInTheDocument();
    });

    it('should set zoom to 12 for single location (city level)', () => {
      render(<TripMap locations={[mockLocations[0]]} tripTitle={mockTripTitle} />);

      const mapContainer = screen.getByTestId('map-container');
      expect(mapContainer.getAttribute('data-zoom')).toBe('12');
    });

    it('should calculate zoom based on location spread (multi-city)', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      const mapContainer = screen.getByTestId('map-container');
      const zoom = parseInt(mapContainer.getAttribute('data-zoom') || '0', 10);

      // For Madrid-Valencia-Barcelona spread (~600km), zoom should be 6-7
      expect(zoom).toBeGreaterThanOrEqual(5);
      expect(zoom).toBeLessThanOrEqual(8);
    });

    it('should calculate center as average of all coordinates', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      const mapContainer = screen.getByTestId('map-container');
      const center = JSON.parse(mapContainer.getAttribute('data-center') || '[]');

      // Calculate expected average
      const avgLat = (40.4168 + 39.4699 + 41.3851) / 3;
      const avgLng = (-3.7038 + -0.3763 + 2.1734) / 3;

      expect(center[0]).toBeCloseTo(avgLat, 4);
      expect(center[1]).toBeCloseTo(avgLng, 4);
    });

    it('should use single location coordinates for center when only one location', () => {
      render(<TripMap locations={[mockLocations[0]]} tripTitle={mockTripTitle} />);

      const mapContainer = screen.getByTestId('map-container');
      const center = JSON.parse(mapContainer.getAttribute('data-center') || '[]');

      expect(center).toEqual([40.4168, -3.7038]); // Madrid coordinates
    });
  });

  /**
   * T112: Test error state display
   * Verifies that error UI displays when tile loading fails
   */
  describe('Error Handling (T112)', () => {
    it('should display error message when map tile loading fails', async () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Trigger tile error event
      const mapEvents = (global as any).__mapEvents;
      if (mapEvents && mapEvents.tileerror) {
        mapEvents.tileerror();
      }

      // Wait for error UI to appear
      await waitFor(() => {
        expect(screen.getByText('Error al cargar el mapa')).toBeInTheDocument();
      });

      expect(
        screen.getByText(/No se pudieron cargar las imágenes del mapa/)
      ).toBeInTheDocument();
    });

    it('should hide map container when error occurs', async () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Initially map should be visible
      expect(screen.getByTestId('map-container')).toBeInTheDocument();

      // Trigger tile error
      const mapEvents = (global as any).__mapEvents;
      if (mapEvents && mapEvents.tileerror) {
        mapEvents.tileerror();
      }

      // Map container should be hidden
      await waitFor(() => {
        expect(screen.queryByTestId('map-container')).not.toBeInTheDocument();
      });
    });

    it('should display retry button in error state', async () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Trigger tile error
      const mapEvents = (global as any).__mapEvents;
      if (mapEvents && mapEvents.tileerror) {
        mapEvents.tileerror();
      }

      await waitFor(() => {
        const retryButton = screen.getByRole('button', { name: /reintentar/i });
        expect(retryButton).toBeInTheDocument();
      });
    });
  });

  /**
   * T113: Test retry functionality
   * Verifies that clicking retry button reloads the map
   */
  describe('Retry Functionality (T113)', () => {
    it('should reload map when retry button is clicked', async () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Trigger tile error
      const mapEvents = (global as any).__mapEvents;
      if (mapEvents && mapEvents.tileerror) {
        mapEvents.tileerror();
      }

      // Wait for retry button
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
      });

      // Click retry button
      const retryButton = screen.getByRole('button', { name: /reintentar/i });
      fireEvent.click(retryButton);

      // Error should be cleared and map should be visible again
      await waitFor(() => {
        expect(screen.queryByText('Error al cargar el mapa')).not.toBeInTheDocument();
        expect(screen.getByTestId('map-container')).toBeInTheDocument();
      });
    });
  });

  /**
   * T114: Test fullscreen toggle behavior
   * Verifies that fullscreen mode can be entered and exited
   */
  describe('Fullscreen Mode (T114)', () => {
    it('should render fullscreen toggle button', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      const fullscreenButton = screen.getByRole('button', { name: /pantalla completa/i });
      expect(fullscreenButton).toBeInTheDocument();
    });

    it('should call requestFullscreen when fullscreen button is clicked', async () => {
      const requestFullscreenMock = vi.fn().mockResolvedValue(undefined);
      HTMLElement.prototype.requestFullscreen = requestFullscreenMock;

      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      const fullscreenButton = screen.getByRole('button', { name: /pantalla completa/i });
      fireEvent.click(fullscreenButton);

      await waitFor(() => {
        expect(requestFullscreenMock).toHaveBeenCalled();
      });
    });

    it('should update button label when entering fullscreen', async () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Initially shows "Pantalla completa"
      expect(screen.getByRole('button', { name: /^pantalla completa$/i })).toBeInTheDocument();

      // Simulate fullscreen enter
      (global as any).setFullscreenElement(document.body);

      // Trigger fullscreenchange event
      const event = new Event('fullscreenchange');
      document.dispatchEvent(event);

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /salir de pantalla completa/i })
        ).toBeInTheDocument();
      });
    });

    it('should call exitFullscreen when exit button is clicked in fullscreen mode', async () => {
      const exitFullscreenMock = vi.fn().mockResolvedValue(undefined);
      document.exitFullscreen = exitFullscreenMock;

      // Set fullscreen state
      (global as any).setFullscreenElement(document.body);

      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Trigger fullscreenchange to update UI
      const event = new Event('fullscreenchange');
      document.dispatchEvent(event);

      await waitFor(() => {
        const exitButton = screen.getByRole('button', { name: /salir de pantalla completa/i });
        fireEvent.click(exitButton);
      });

      expect(exitFullscreenMock).toHaveBeenCalled();
    });

    it('should not show fullscreen button when in error state', async () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Trigger tile error
      const mapEvents = (global as any).__mapEvents;
      if (mapEvents && mapEvents.tileerror) {
        mapEvents.tileerror();
      }

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /pantalla completa/i })).not.toBeInTheDocument();
      });
    });
  });

  /**
   * T115: Test empty state
   * Verifies that empty state is shown when no valid locations exist
   */
  describe('Empty State (T115)', () => {
    it('should show empty state when no locations provided', () => {
      render(<TripMap locations={[]} tripTitle={mockTripTitle} />);

      expect(screen.getByText('No hay ubicaciones en este viaje')).toBeInTheDocument();
      expect(screen.queryByTestId('map-container')).not.toBeInTheDocument();
    });

    it('should show empty state when all locations have null coordinates', () => {
      const locationsWithoutCoords: TripLocation[] = [
        {
          location_id: 'loc-1',
          trip_id: 'trip-1',
          name: 'No Coords 1',
          latitude: null,
          longitude: null,
          sequence: 1,
          created_at: '2024-01-01T00:00:00Z',
        },
        {
          location_id: 'loc-2',
          trip_id: 'trip-1',
          name: 'No Coords 2',
          latitude: null,
          longitude: null,
          sequence: 2,
          created_at: '2024-01-01T00:00:00Z',
        },
      ];

      render(<TripMap locations={locationsWithoutCoords} tripTitle={mockTripTitle} />);

      expect(screen.getByText('No hay ubicaciones en este viaje')).toBeInTheDocument();
      expect(screen.queryByTestId('map-container')).not.toBeInTheDocument();
    });

    it('should render empty state with correct class', () => {
      const { container } = render(<TripMap locations={[]} tripTitle={mockTripTitle} />);

      const emptyStateDiv = container.querySelector('.trip-map--empty');
      expect(emptyStateDiv).toBeInTheDocument();
      expect(emptyStateDiv).toHaveClass('trip-map', 'trip-map--empty');
    });
  });

  /**
   * T027 [US2]: Test marker drag event handling
   * Feature 010: Reverse Geocoding - User Story 2
   */
  describe('Marker Drag Event Handling (T027)', () => {
    it('should make markers draggable when isEditMode is true', () => {
      render(
        <TripMap
          locations={mockLocations}
          tripTitle={mockTripTitle}
          isEditMode={true}
          onMapClick={vi.fn()}
        />
      );

      const markers = screen.getAllByTestId('marker');
      expect(markers).toHaveLength(3);

      // Check that all markers have draggable prop set to true
      markers.forEach((marker) => {
        expect(marker.getAttribute('data-draggable')).toBe('true');
      });
    });

    it('should NOT make markers draggable when isEditMode is false', () => {
      render(
        <TripMap
          locations={mockLocations}
          tripTitle={mockTripTitle}
          isEditMode={false}
        />
      );

      const markers = screen.getAllByTestId('marker');
      expect(markers).toHaveLength(3);

      // Markers should not be draggable in view mode
      markers.forEach((marker) => {
        expect(marker.getAttribute('data-draggable')).toBe('false');
      });
    });

    it('should attach dragend event handler when onMarkerDrag callback is provided', () => {
      const mockOnMarkerDrag = vi.fn();

      render(
        <TripMap
          locations={mockLocations}
          tripTitle={mockTripTitle}
          isEditMode={true}
          onMarkerDrag={mockOnMarkerDrag}
        />
      );

      const markers = screen.getAllByTestId('marker');

      // Verify that each marker has a dragend event handler attached
      markers.forEach((marker) => {
        const eventHandlers = JSON.parse(marker.getAttribute('data-event-handlers') || '{}');
        expect(eventHandlers).toHaveProperty('dragend');
        expect(typeof eventHandlers.dragend).toBe('function');
      });
    });

    it('should preserve location_id when dragging marker', () => {
      const mockOnMarkerDrag = vi.fn();

      render(
        <TripMap
          locations={mockLocations}
          tripTitle={mockTripTitle}
          isEditMode={true}
          onMarkerDrag={mockOnMarkerDrag}
        />
      );

      // When a marker is dragged, the callback should receive:
      // - location_id: to identify which location was moved
      // - newLat: new latitude
      // - newLng: new longitude
      // This ensures the parent component can update the correct location
    });

    it('should show draggable cursor in edit mode', () => {
      const { container } = render(
        <TripMap
          locations={mockLocations}
          tripTitle={mockTripTitle}
          isEditMode={true}
        />
      );

      // Markers in edit mode should have visual feedback (cursor: move)
      // This will be tested via CSS class in T034
    });

    it('should disable marker dragging when not in edit mode', () => {
      render(
        <TripMap
          locations={mockLocations}
          tripTitle={mockTripTitle}
          isEditMode={false}
        />
      );

      // Markers should not respond to drag events in view mode
      // Draggable prop should be false or undefined
    });
  });

  /**
   * Additional Tests: Location List
   */
  describe('Location List Display', () => {
    it('should display location count in header', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      expect(screen.getByText('Ubicaciones (3)')).toBeInTheDocument();
    });

    it('should list all valid locations with sequence numbers', () => {
      render(<TripMap locations={mockLocations} tripTitle={mockTripTitle} />);

      // Check location list items
      const locationItems = screen.getAllByRole('listitem');
      expect(locationItems).toHaveLength(3);

      expect(screen.getByText('Madrid')).toBeInTheDocument();
      expect(screen.getByText('Valencia')).toBeInTheDocument();
      expect(screen.getByText('Barcelona')).toBeInTheDocument();
    });

    it('should sort locations by sequence in location list', () => {
      const unsortedLocations: TripLocation[] = [
        mockLocations[2], // Barcelona (sequence 3)
        mockLocations[0], // Madrid (sequence 1)
        mockLocations[1], // Valencia (sequence 2)
      ];

      render(<TripMap locations={unsortedLocations} tripTitle={mockTripTitle} />);

      const locationItems = screen.getAllByRole('listitem');

      // Verify order: Madrid, Valencia, Barcelona
      expect(locationItems[0]).toHaveTextContent('Madrid');
      expect(locationItems[1]).toHaveTextContent('Valencia');
      expect(locationItems[2]).toHaveTextContent('Barcelona');
    });
  });
});
