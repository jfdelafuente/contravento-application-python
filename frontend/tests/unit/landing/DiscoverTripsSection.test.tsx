// frontend/tests/unit/landing/DiscoverTripsSection.test.tsx

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { DiscoverTripsSection } from '../../../src/components/landing/DiscoverTripsSection';
import * as tripsService from '../../../src/services/tripsService';

/**
 * Test Suite: DiscoverTripsSection Component
 *
 * Requirements:
 * - Display "Descubre nuevas rutas" section title
 * - Fetch and display 4 most recent public trips
 * - Show trip cards with: title, photo, username, date
 * - Handle loading state
 * - Handle empty state (no trips)
 * - Handle error state
 * - Responsive grid (2x2 desktop, stacked mobile)
 */

// Mock trips data (Feature 013 Public Feed format)
const mockTrips = [
  {
    trip_id: '1',
    title: 'Ruta por los Pirineos',
    start_date: '2024-06-01',
    distance_km: 320,
    author: {
      user_id: 'u1',
      username: 'ciclista1',
      profile_photo_url: null,
    },
    photo: {
      photo_url: '/photos/trip1.jpg',
      thumbnail_url: '/photos/trip1_thumb.jpg',
    },
    location: {
      name: 'Pirineos',
    },
    published_at: '2024-06-10T10:00:00Z',
  },
  {
    trip_id: '2',
    title: 'Camino de Santiago en bici',
    start_date: '2024-05-15',
    distance_km: 780,
    author: {
      user_id: 'u2',
      username: 'peregrino',
      profile_photo_url: null,
    },
    photo: null,
    location: {
      name: 'Santiago de Compostela',
    },
    published_at: '2024-06-09T15:30:00Z',
  },
  {
    trip_id: '3',
    title: 'Costa Brava bikepacking',
    start_date: '2024-06-05',
    distance_km: 150,
    author: {
      user_id: 'u3',
      username: 'aventurero',
      profile_photo_url: null,
    },
    photo: {
      photo_url: '/photos/trip3.jpg',
      thumbnail_url: '/photos/trip3_thumb.jpg',
    },
    location: {
      name: 'Costa Brava',
    },
    published_at: '2024-06-08T12:00:00Z',
  },
  {
    trip_id: '4',
    title: 'Transpirenaica MTB',
    start_date: '2024-05-20',
    distance_km: 850,
    author: {
      user_id: 'u4',
      username: 'montañero',
      profile_photo_url: null,
    },
    photo: {
      photo_url: '/photos/trip4.jpg',
      thumbnail_url: '/photos/trip4_thumb.jpg',
    },
    location: {
      name: 'Transpirenaica',
    },
    published_at: '2024-06-07T09:00:00Z',
  },
];

describe('DiscoverTripsSection Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderDiscoverTripsSection = () => {
    return render(
      <MemoryRouter>
        <DiscoverTripsSection />
      </MemoryRouter>
    );
  };

  describe('Section Structure', () => {
    it('should render as a section element', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
      });

      const { container } = renderDiscoverTripsSection();
      await waitFor(() => {
        const section = container.querySelector('section');
        expect(section).toBeInTheDocument();
      });
    });

    it('should have discover-trips-section CSS class', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
        
      });

      const { container } = renderDiscoverTripsSection();
      await waitFor(() => {
        const section = container.querySelector('.discover-trips-section');
        expect(section).toBeInTheDocument();
      });
    });

    it('should render section title "Descubre nuevas rutas"', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
        
      });

      renderDiscoverTripsSection();
      await waitFor(() => {
        const title = screen.getByRole('heading', { level: 2, name: /descubre nuevas rutas/i });
        expect(title).toBeInTheDocument();
      });
    });
  });

  describe('Data Fetching', () => {
    it('should fetch 4 most recent public trips on mount', async () => {
      const spy = vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
        
      });

      renderDiscoverTripsSection();

      await waitFor(() => {
        expect(spy).toHaveBeenCalledWith(1, 4);
      });
    });

    it('should display 4 trip cards when data loads', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
        
      });

      const { container } = renderDiscoverTripsSection();

      await waitFor(() => {
        const tripCards = container.querySelectorAll('.discover-trip-card');
        expect(tripCards).toHaveLength(4);
      });
    });
  });

  describe('Loading State', () => {
    it('should show loading spinner while fetching trips', () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderDiscoverTripsSection();
      const loading = screen.getByText(/cargando/i);
      expect(loading).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should show message when no trips are available', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: [],
        pagination: { total: 0, page: 1, limit: 4, total_pages: 0 },
      });

      renderDiscoverTripsSection();

      await waitFor(() => {
        const emptyMessage = screen.getByText(/no hay viajes disponibles/i);
        expect(emptyMessage).toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    it('should show error message when fetching fails', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        success: false,
        data: null,
        error: { code: 'FETCH_ERROR', message: 'Error al cargar viajes' },
      });

      renderDiscoverTripsSection();

      await waitFor(() => {
        const errorMessage = screen.getByText(/error al cargar/i);
        expect(errorMessage).toBeInTheDocument();
      });
    });
  });

  describe('Trip Card Content', () => {
    beforeEach(() => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
        
      });
    });

    it('should display trip title', async () => {
      renderDiscoverTripsSection();

      await waitFor(() => {
        const title = screen.getByText('Ruta por los Pirineos');
        expect(title).toBeInTheDocument();
      });
    });

    it('should display username', async () => {
      renderDiscoverTripsSection();

      await waitFor(() => {
        const username = screen.getByText(/ciclista1/i);
        expect(username).toBeInTheDocument();
      });
    });

    it('should display trip photo when available', async () => {
      const { container } = renderDiscoverTripsSection();

      await waitFor(() => {
        const image = container.querySelector('img[alt*="Ruta por los Pirineos"]');
        expect(image).toBeInTheDocument();
      });
    });

    it('should display placeholder when photo not available', async () => {
      const { container } = renderDiscoverTripsSection();

      await waitFor(() => {
        const placeholders = container.querySelectorAll('img[src*="placeholder"]');
        expect(placeholders.length).toBeGreaterThan(0);
      });
    });

    it('should link to trip detail page', async () => {
      renderDiscoverTripsSection();

      await waitFor(() => {
        const link = screen.getByRole('link', { name: /ruta por los pirineos/i });
        expect(link).toHaveAttribute('href', '/trips/1');
      });
    });
  });

  describe('Responsive Layout', () => {
    it('should render trips in grid container', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
        
      });

      const { container } = renderDiscoverTripsSection();

      await waitFor(() => {
        const grid = container.querySelector('.discover-trips-grid');
        expect(grid).toBeInTheDocument();
      });
    });
  });

  describe('Call to Action', () => {
    it('should display "Ver todos los viajes" link', async () => {
      vi.spyOn(tripsService, 'getPublicTrips').mockResolvedValue({
        trips: mockTrips,
        pagination: { total: 4, page: 1, limit: 4, total_pages: 1 },
        
      });

      renderDiscoverTripsSection();

      await waitFor(() => {
        const link = screen.getByRole('link', { name: /ver todos los viajes/i });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', '/trips/public');
      });
    });
  });
});
