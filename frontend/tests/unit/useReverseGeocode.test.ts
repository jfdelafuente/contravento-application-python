/**
 * Unit tests for useReverseGeocode hook
 * Feature: 010-reverse-geocoding
 * Test: T013
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { useReverseGeocode } from '../../src/hooks/useReverseGeocode';
import { geocodingCache } from '../../src/utils/geocodingCache';
import type { GeocodingResponse } from '../../src/types/geocoding';

describe('useReverseGeocode', () => {
  let mockAxios: MockAdapter;

  const mockResponse: GeocodingResponse = {
    place_id: 123456789,
    licence: 'Data © OpenStreetMap contributors',
    osm_type: 'way',
    osm_id: 987654321,
    lat: '40.416775',
    lon: '-3.703790',
    display_name: 'Parque del Retiro, Retiro, Madrid, España',
    address: {
      leisure: 'Parque del Retiro',
      city: 'Madrid',
      country: 'España',
    },
    boundingbox: ['40.4', '40.5', '-3.8', '-3.7'],
  };

  beforeEach(() => {
    mockAxios = new MockAdapter(axios);
    geocodingCache.clear(); // Clear cache before each test
    vi.useFakeTimers(); // For debounce testing
  });

  afterEach(() => {
    mockAxios.restore();
    geocodingCache.clear();
    vi.useRealTimers();
  });

  describe('Immediate Geocoding (geocode)', () => {
    it('should return geocoded name and full address on success', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());

      // Act
      let geocodeResult;
      await act(async () => {
        geocodeResult = await result.current.geocode(40.416775, -3.70379);
      });

      // Assert
      expect(geocodeResult).toEqual({
        name: 'Parque del Retiro',
        fullAddress: 'Parque del Retiro, Retiro, Madrid, España',
      });
    });

    it('should set isLoading to true during API call', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());

      // Act
      let loadingDuringCall = false;
      act(() => {
        result.current.geocode(40.416775, -3.70379);
        loadingDuringCall = result.current.isLoading;
      });

      // Assert
      expect(loadingDuringCall).toBe(true);
    });

    it('should set isLoading to false after API call completes', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());

      // Act
      await act(async () => {
        await result.current.geocode(40.416775, -3.70379);
      });

      // Assert
      expect(result.current.isLoading).toBe(false);
    });

    it('should set error state on API failure', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(500, 'Internal Server Error');
      const { result } = renderHook(() => useReverseGeocode());

      // Act
      await act(async () => {
        try {
          await result.current.geocode(40.416775, -3.70379);
        } catch (err) {
          // Expected error
        }
      });

      // Assert
      expect(result.current.error).toBeTruthy();
      expect(result.current.error).toContain('No se pudo conectar');
    });

    it('should clear error state on successful call after error', async () => {
      // Arrange
      mockAxios
        .onGet(/nominatim.*reverse/)
        .replyOnce(500, 'Error')
        .onGet(/nominatim.*reverse/)
        .replyOnce(200, mockResponse);

      const { result } = renderHook(() => useReverseGeocode());

      // Act - First call fails
      await act(async () => {
        try {
          await result.current.geocode(40.416775, -3.70379);
        } catch (err) {
          // Expected
        }
      });
      expect(result.current.error).toBeTruthy();

      // Act - Second call succeeds
      await act(async () => {
        await result.current.geocode(40.5, -3.8);
      });

      // Assert
      expect(result.current.error).toBeNull();
    });

    it('should clear error manually with clearError', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(500, 'Error');
      const { result } = renderHook(() => useReverseGeocode());

      // Act - Trigger error
      await act(async () => {
        try {
          await result.current.geocode(40.416775, -3.70379);
        } catch (err) {
          // Expected
        }
      });
      expect(result.current.error).toBeTruthy();

      // Act - Clear error
      act(() => {
        result.current.clearError();
      });

      // Assert
      expect(result.current.error).toBeNull();
    });
  });

  describe('Cache Integration', () => {
    it('should use cached response if available', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());

      // Act - First call (cache miss)
      await act(async () => {
        await result.current.geocode(40.416775, -3.70379);
      });

      // Reset mock to ensure second call doesn't hit API
      mockAxios.reset();
      mockAxios.onGet(/nominatim.*reverse/).reply(500, 'Should not be called');

      // Act - Second call (cache hit)
      let cachedResult;
      await act(async () => {
        cachedResult = await result.current.geocode(40.416775, -3.70379);
      });

      // Assert
      expect(cachedResult).toEqual({
        name: 'Parque del Retiro',
        fullAddress: 'Parque del Retiro, Retiro, Madrid, España',
      });
      // Verify API was not called (no 500 error)
      expect(result.current.error).toBeNull();
    });

    it('should set isLoading to false immediately on cache hit', async () => {
      // Arrange - Populate cache
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());
      await act(async () => {
        await result.current.geocode(40.416775, -3.70379);
      });

      // Act - Use cached value
      await act(async () => {
        await result.current.geocode(40.416775, -3.70379);
      });

      // Assert - isLoading should be false
      expect(result.current.isLoading).toBe(false);
    });

    it('should store response in cache after successful API call', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());

      // Act
      await act(async () => {
        await result.current.geocode(40.416775, -3.70379);
      });

      // Assert - Verify cache has entry
      expect(geocodingCache.has(40.416775, -3.70379)).toBe(true);
    });
  });

  describe('Debounced Geocoding (debouncedGeocode)', () => {
    it('should delay API call by 1 second', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());

      // Act - Call debounced function
      act(() => {
        result.current.debouncedGeocode(40.416775, -3.70379);
      });

      // Assert - No API call yet
      expect(mockAxios.history.get.length).toBe(0);

      // Act - Fast-forward 1 second
      await act(async () => {
        vi.advanceTimersByTime(1000);
        await waitFor(() => expect(mockAxios.history.get.length).toBe(1));
      });

      // Assert - API called after delay
      expect(mockAxios.history.get.length).toBe(1);
    });

    it('should cancel previous debounced call on rapid updates', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());

      // Act - Rapid calls
      act(() => {
        result.current.debouncedGeocode(40.0, -3.0);
        result.current.debouncedGeocode(40.1, -3.1);
        result.current.debouncedGeocode(40.2, -3.2);
      });

      // Fast-forward 1 second
      await act(async () => {
        vi.advanceTimersByTime(1000);
        await waitFor(() => expect(mockAxios.history.get.length).toBe(1));
      });

      // Assert - Only last call executed
      expect(mockAxios.history.get.length).toBe(1);
      const lastCall = mockAxios.history.get[0];
      expect(lastCall.params.lat).toBe(40.2);
      expect(lastCall.params.lon).toBe(-3.2);
    });

    it('should use cache if available (no debounce needed)', async () => {
      // Arrange - Populate cache
      mockAxios.onGet(/nominatim.*reverse/).reply(200, mockResponse);
      const { result } = renderHook(() => useReverseGeocode());
      await act(async () => {
        await result.current.geocode(40.416775, -3.70379);
      });

      // Reset mock
      mockAxios.reset();
      mockAxios.onGet(/nominatim.*reverse/).reply(500, 'Should not be called');

      // Act - Debounced call with cached coords
      let debouncedResult;
      await act(async () => {
        debouncedResult = await result.current.debouncedGeocode(40.416775, -3.70379);
      });

      // Fast-forward
      await act(async () => {
        vi.advanceTimersByTime(1000);
      });

      // Assert - Used cache, no API call
      expect(mockAxios.history.get.length).toBe(0);
    });
  });

  describe('Error Handling', () => {
    it('should throw error with Spanish message on validation failure', async () => {
      // Arrange
      const { result } = renderHook(() => useReverseGeocode());

      // Act & Assert - Invalid latitude
      await act(async () => {
        await expect(result.current.geocode(100, -3.7)).rejects.toThrow(
          'Latitud inválida'
        );
      });
    });

    it('should set Spanish error message on rate limit (429)', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(429, 'Too many requests');
      const { result } = renderHook(() => useReverseGeocode());

      // Act
      await act(async () => {
        try {
          await result.current.geocode(40.416775, -3.70379);
        } catch (err) {
          // Expected
        }
      });

      // Assert
      expect(result.current.error).toContain('Demasiadas solicitudes');
    });

    it('should set Spanish error message on network timeout', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).timeout();
      const { result } = renderHook(() => useReverseGeocode());

      // Act
      await act(async () => {
        try {
          await result.current.geocode(40.416775, -3.70379);
        } catch (err) {
          // Expected
        }
      });

      // Assert
      expect(result.current.error).toContain('servidor de mapas no responde');
    });

    it('should re-throw error for caller to handle', async () => {
      // Arrange
      mockAxios.onGet(/nominatim.*reverse/).reply(500, 'Error');
      const { result } = renderHook(() => useReverseGeocode());

      // Act & Assert
      await act(async () => {
        await expect(result.current.geocode(40.416775, -3.70379)).rejects.toThrow();
      });
    });
  });
});
