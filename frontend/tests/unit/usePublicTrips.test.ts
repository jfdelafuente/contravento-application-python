/**
 * Unit tests for usePublicTrips hook (Feature 013 - T033)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { usePublicTrips } from '../../src/hooks/usePublicTrips';
import * as tripService from '../../src/services/tripService';
import { PublicTripListResponse } from '../../src/types/trip';

// Mock the tripService
vi.mock('../../src/services/tripService');

describe('usePublicTrips', () => {
  const mockResponse: PublicTripListResponse = {
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
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it('fetches trips successfully on mount', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockResponse);

    const { result } = renderHook(() => usePublicTrips(1, 20));

    // Initially loading
    expect(result.current.isLoading).toBe(true);
    expect(result.current.trips).toEqual([]);
    expect(result.current.pagination).toBeNull();
    expect(result.current.error).toBeNull();

    // Wait for fetch to complete
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Check final state
    expect(result.current.trips).toEqual(mockResponse.trips);
    expect(result.current.pagination).toEqual(mockResponse.pagination);
    expect(result.current.error).toBeNull();
    expect(tripService.getPublicTrips).toHaveBeenCalledWith(1, 20);
  });

  it('handles fetch errors correctly', async () => {
    const errorMessage = 'Network error';
    vi.spyOn(tripService, 'getPublicTrips').mockRejectedValue({
      response: {
        data: {
          detail: {
            message: errorMessage,
          },
        },
      },
    });

    const { result } = renderHook(() => usePublicTrips(1, 20));

    // Wait for fetch to fail
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Check error state
    expect(result.current.trips).toEqual([]);
    expect(result.current.pagination).toBeNull();
    expect(result.current.error).toBe(errorMessage);
  });

  it('handles generic errors without detail message', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => usePublicTrips(1, 20));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Should use error.message if available
    expect(result.current.error).toBe('Network error');
  });

  it('refetches data when page changes', async () => {
    const getPublicTripsSpy = vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockResponse);

    const { result, rerender } = renderHook(
      ({ page, limit }) => usePublicTrips(page, limit),
      {
        initialProps: { page: 1, limit: 20 },
      }
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(getPublicTripsSpy).toHaveBeenCalledTimes(1);
    expect(getPublicTripsSpy).toHaveBeenCalledWith(1, 20);

    // Change page
    rerender({ page: 2, limit: 20 });

    await waitFor(() => {
      expect(getPublicTripsSpy).toHaveBeenCalledTimes(2);
    });

    expect(getPublicTripsSpy).toHaveBeenCalledWith(2, 20);
  });

  it('refetches data when limit changes', async () => {
    const getPublicTripsSpy = vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockResponse);

    const { result, rerender } = renderHook(
      ({ page, limit }) => usePublicTrips(page, limit),
      {
        initialProps: { page: 1, limit: 20 },
      }
    );

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Change limit
    rerender({ page: 1, limit: 10 });

    await waitFor(() => {
      expect(getPublicTripsSpy).toHaveBeenCalledTimes(2);
    });

    expect(getPublicTripsSpy).toHaveBeenCalledWith(1, 10);
  });

  it('provides refetch function', async () => {
    const getPublicTripsSpy = vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockResponse);

    const { result } = renderHook(() => usePublicTrips(1, 20));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(getPublicTripsSpy).toHaveBeenCalledTimes(1);

    // Call refetch
    await result.current.refetch();

    await waitFor(() => {
      expect(getPublicTripsSpy).toHaveBeenCalledTimes(2);
    });
  });

  it('clears previous data on refetch', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockResponse);

    const { result } = renderHook(() => usePublicTrips(1, 20));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.trips).toHaveLength(2);

    // Mock empty response for refetch
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue({
      trips: [],
      pagination: {
        total: 0,
        page: 1,
        limit: 20,
        total_pages: 0,
      },
    });

    await result.current.refetch();

    await waitFor(() => {
      expect(result.current.trips).toEqual([]);
    });

    expect(result.current.pagination?.total).toBe(0);
  });

  it('handles empty trips response', async () => {
    const emptyResponse: PublicTripListResponse = {
      trips: [],
      pagination: {
        total: 0,
        page: 1,
        limit: 20,
        total_pages: 0,
      },
    };

    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(emptyResponse);

    const { result } = renderHook(() => usePublicTrips(1, 20));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.trips).toEqual([]);
    expect(result.current.pagination?.total).toBe(0);
    expect(result.current.error).toBeNull();
  });

  it('uses default page and limit values', async () => {
    const getPublicTripsSpy = vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockResponse);

    renderHook(() => usePublicTrips());

    await waitFor(() => {
      expect(getPublicTripsSpy).toHaveBeenCalledWith(1, 20);
    });
  });

  it('sets loading state correctly during refetch', async () => {
    vi.spyOn(tripService, 'getPublicTrips').mockResolvedValue(mockResponse);

    const { result } = renderHook(() => usePublicTrips(1, 20));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Trigger refetch and wait for completion
    await result.current.refetch();

    // After refetch completes, should not be loading
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
  });

  it('preserves error state across refetches if error persists', async () => {
    const error = {
      response: {
        data: {
          detail: {
            message: 'Server error',
          },
        },
      },
    };

    vi.spyOn(tripService, 'getPublicTrips').mockRejectedValue(error);

    const { result } = renderHook(() => usePublicTrips(1, 20));

    await waitFor(() => {
      expect(result.current.error).toBe('Server error');
    });

    // Refetch with same error
    await result.current.refetch();

    await waitFor(() => {
      expect(result.current.error).toBe('Server error');
    });
  });

  it('clears error on successful refetch', async () => {
    const error = {
      response: {
        data: {
          detail: {
            message: 'Server error',
          },
        },
      },
    };

    const getPublicTripsSpy = vi.spyOn(tripService, 'getPublicTrips').mockRejectedValueOnce(error);

    const { result } = renderHook(() => usePublicTrips(1, 20));

    await waitFor(() => {
      expect(result.current.error).toBe('Server error');
    });

    // Mock successful response for refetch
    getPublicTripsSpy.mockResolvedValue(mockResponse);

    await result.current.refetch();

    await waitFor(() => {
      expect(result.current.error).toBeNull();
      expect(result.current.trips).toHaveLength(2);
    });
  });
});
