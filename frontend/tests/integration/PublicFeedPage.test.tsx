/**
 * Integration tests for PublicFeedPage (Feature 013 - T034)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { PublicFeedPage } from '../../src/pages/PublicFeedPage';
import * as tripService from '../../src/services/tripService';
import { PublicTripListResponse } from '../../src/types/trip';

// Mock the tripService
vi.mock('../../src/services/tripService');

// Mock useNavigate from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

const RouterWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('PublicFeedPage Integration', () => {
  const mockTripsResponse: PublicTripListResponse = {
    trips: [
      {
        trip_id: '123e4567-e89b-12d3-a456-426614174000',
        title: 'Ruta Bikepacking Pirineos',
        start_date: '2024-06-01',
        distance_km: 320.5,
        photo: {
          photo_url: '/storage/trip_photos/2024/06/photo.jpg',
          thumbnail_url: '/storage/trip_photos/2024/06/photo_thumb.jpg',
        },
        location: {
          name: 'Jaca, España',
        },
        author: {
          user_id: '456e7890-e89b-12d3-a456-426614174001',
          username: 'maria_ciclista',
          profile_photo_url: '/storage/profile_photos/maria.jpg',
        },
        published_at: '2024-06-10T14:30:00Z',
      },
      {
        trip_id: '789e0123-e89b-12d3-a456-426614174002',
        title: 'Camino de Santiago',
        start_date: '2024-05-15',
        distance_km: 750.0,
        photo: null,
        location: {
          name: 'Santiago de Compostela',
        },
        author: {
          user_id: '012e3456-e89b-12d3-a456-426614174003',
          username: 'juan_peregrino',
          profile_photo_url: null,
        },
        published_at: '2024-05-20T10:15:00Z',
      },
    ],
    pagination: {
      total: 45,
      page: 1,
      limit: 20,
      total_pages: 3,
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('renders loading state initially', () => {
    vi.spyOn(tripService, 'getPublicTrips').mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    expect(screen.getByText(/Cargando viajes/i)).toBeInTheDocument();
  });

  it('renders trips grid after successful fetch', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    // Wait for trips to load
    await waitFor(() => {
      expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();
    });

    expect(screen.getByText('Camino de Santiago')).toBeInTheDocument();
    expect(screen.getByText(/45 viajes disponibles/i)).toBeInTheDocument();
  });

  it('renders error state on fetch failure', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockRejectedValue({
      response: {
        data: {
          detail: {
            message: 'Error del servidor',
          },
        },
      },
    });

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Error al cargar viajes/i)).toBeInTheDocument();
    });

    expect(screen.getByText('Error del servidor')).toBeInTheDocument();
    expect(screen.getByText(/Intentar de nuevo/i)).toBeInTheDocument();
  });

  it('renders empty state when no trips available', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue({
      trips: [],
      pagination: {
        total: 0,
        page: 1,
        limit: 20,
        total_pages: 0,
      },
    });

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Aún no hay viajes publicados/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Sé el primero en compartir/i)).toBeInTheDocument();
  });

  it('displays pagination controls when multiple pages exist', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Página 1 de 3/i)).toBeInTheDocument();
    });

    expect(screen.getByLabelText(/Anterior/i)).toBeDisabled();
    expect(screen.getByLabelText(/Siguiente/i)).not.toBeDisabled();
  });

  it('hides pagination when only one page exists', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue({
      trips: mockTripsResponse.trips,
      pagination: {
        total: 2,
        page: 1,
        limit: 20,
        total_pages: 1,
      },
    });

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();
    });

    // Pagination should not be visible
    expect(screen.queryByLabelText(/Anterior/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Siguiente/i)).not.toBeInTheDocument();
  });

  it('navigates to next page on next button click', async () => {
    const user = userEvent.setup();
    const getPublicTripsSpy = vi
      .spyOn(tripService, 'getPublicTrips')
      .mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();
    });

    const nextButton = screen.getByLabelText(/Siguiente/i);
    await user.click(nextButton);

    // Should call API with page 2
    await waitFor(() => {
      expect(getPublicTripsSpy).toHaveBeenCalledWith(2, 20);
    });
  });

  it('calls API with next page when next button clicked', async () => {
    const user = userEvent.setup();
    const getPublicTripsSpy = vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();
    });

    // Click next button
    const nextButton = screen.getByLabelText(/Siguiente/i);
    await user.click(nextButton);

    // Should call API with page 2
    await waitFor(() => {
      expect(getPublicTripsSpy).toHaveBeenCalledWith(2, 20);
    });
  });

  it('disables previous button on first page', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Página 1 de 3/i)).toBeInTheDocument();
    });

    const prevButton = screen.getByLabelText(/Anterior/i);
    expect(prevButton).toBeDisabled();
  });

  it('shows pagination controls with correct information', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Página 1 de 3/i)).toBeInTheDocument();
    });

    // Previous button should be disabled on first page
    const prevButton = screen.getByLabelText(/Anterior/i);
    expect(prevButton).toBeDisabled();

    // Next button should be enabled
    const nextButton = screen.getByLabelText(/Siguiente/i);
    expect(nextButton).not.toBeDisabled();
  });

  it('scrolls to top when changing pages', async () => {
    const user = userEvent.setup();
    const scrollToSpy = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});

    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();
    });

    const nextButton = screen.getByLabelText(/Siguiente/i);
    await user.click(nextButton);

    expect(scrollToSpy).toHaveBeenCalledWith({ top: 0, behavior: 'smooth' });
  });

  it('renders retry button on error', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockRejectedValueOnce(new Error('Network error'));

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText(/Error al cargar viajes/i)).toBeInTheDocument();
    });

    // Verify retry button exists
    const retryButton = screen.getByText(/Intentar de nuevo/i);
    expect(retryButton).toBeInTheDocument();
    expect(retryButton.tagName).toBe('BUTTON');
  });

  it('displays header with title and subtitle', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    expect(screen.getByText('Explora Viajes en Bicicleta')).toBeInTheDocument();
    expect(
      screen.getByText(/Descubre las últimas aventuras/i)
    ).toBeInTheDocument();
  });

  it('uses correct grid layout CSS class', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    const { container } = render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Ruta Bikepacking Pirineos')).toBeInTheDocument();
    });

    const grid = container.querySelector('.public-feed__grid');
    expect(grid).toBeInTheDocument();
  });

  it('renders correct trip count text', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockTripsResponse);

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/45 viajes disponibles/i)).toBeInTheDocument();
    });
  });

  it('uses singular form for one trip', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue({
      trips: [mockTripsResponse.trips[0]],
      pagination: {
        total: 1,
        page: 1,
        limit: 20,
        total_pages: 1,
      },
    });

    render(
      <RouterWrapper>
        <PublicFeedPage />
      </RouterWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/1 viaje disponible/i)).toBeInTheDocument();
    });
  });
});
