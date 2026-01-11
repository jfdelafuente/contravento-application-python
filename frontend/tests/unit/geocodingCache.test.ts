/**
 * Unit tests for GeocodingCache
 * Feature: 010-reverse-geocoding
 * Test: T012
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { GeocodingCache } from '../../src/utils/geocodingCache';
import type { GeocodingResponse } from '../../src/types/geocoding';

describe('GeocodingCache', () => {
  let cache: GeocodingCache;

  const createMockResponse = (placeName: string): GeocodingResponse => ({
    place_id: Math.floor(Math.random() * 1000000),
    licence: 'Data © OpenStreetMap contributors',
    osm_type: 'way',
    osm_id: 12345,
    lat: '40.416775',
    lon: '-3.703790',
    display_name: placeName,
    address: {
      leisure: placeName,
      city: 'Madrid',
      country: 'España',
    },
    boundingbox: ['40.4', '40.5', '-3.8', '-3.7'],
  });

  beforeEach(() => {
    cache = new GeocodingCache(5); // Small cache for testing
  });

  describe('Cache Key Generation', () => {
    it('should round coordinates to 3 decimals for cache key', () => {
      // Arrange
      const response = createMockResponse('Test Location');

      // Act
      cache.set(40.416123, -3.703456, response);
      const result = cache.get(40.416999, -3.703111); // Should round to same key

      // Assert
      expect(result).toBeNull(); // Different rounded values
    });

    it('should match cache keys with same rounded coordinates', () => {
      // Arrange
      const response = createMockResponse('Test Location');

      // Act
      cache.set(40.416123, -3.703456, response); // Rounds to 40.416, -3.703
      const result = cache.get(40.416456, -3.703123); // Also rounds to 40.416, -3.703

      // Assert
      expect(result).toEqual(response);
    });
  });

  describe('Basic Cache Operations', () => {
    it('should store and retrieve a geocoding response', () => {
      // Arrange
      const lat = 40.416775;
      const lng = -3.70379;
      const response = createMockResponse('Parque del Retiro');

      // Act
      cache.set(lat, lng, response);
      const result = cache.get(lat, lng);

      // Assert
      expect(result).toEqual(response);
    });

    it('should return null for cache miss', () => {
      // Arrange
      const lat = 40.416775;
      const lng = -3.70379;

      // Act
      const result = cache.get(lat, lng);

      // Assert
      expect(result).toBeNull();
    });

    it('should update access count on cache hit', () => {
      // Arrange
      const lat = 40.416775;
      const lng = -3.70379;
      const response = createMockResponse('Test Location');
      cache.set(lat, lng, response);

      // Act
      cache.get(lat, lng); // First access
      cache.get(lat, lng); // Second access
      const stats = cache.getStats();

      // Assert
      const entry = stats.entries.find((e) =>
        e.key.includes('40.417')
      );
      expect(entry?.accessCount).toBeGreaterThan(1);
    });

    it('should overwrite existing entry with same coordinates', () => {
      // Arrange
      const lat = 40.416775;
      const lng = -3.70379;
      const response1 = createMockResponse('First Location');
      const response2 = createMockResponse('Second Location');

      // Act
      cache.set(lat, lng, response1);
      cache.set(lat, lng, response2);
      const result = cache.get(lat, lng);

      // Assert
      expect(result).toEqual(response2);
      expect(cache.size()).toBe(1); // Should not create duplicate entry
    });
  });

  describe('LRU Eviction', () => {
    it('should evict least recently used entry when cache is full', () => {
      // Arrange - Fill cache to max size (5)
      cache.set(40.0, -3.0, createMockResponse('Location 1'));
      cache.set(40.1, -3.1, createMockResponse('Location 2'));
      cache.set(40.2, -3.2, createMockResponse('Location 3'));
      cache.set(40.3, -3.3, createMockResponse('Location 4'));
      cache.set(40.4, -3.4, createMockResponse('Location 5'));

      // Act - Add 6th entry (should evict first)
      cache.set(40.5, -3.5, createMockResponse('Location 6'));

      // Assert
      expect(cache.size()).toBe(5); // Still at max
      expect(cache.get(40.0, -3.0)).toBeNull(); // First entry evicted
      expect(cache.get(40.5, -3.5)).not.toBeNull(); // New entry exists
    });

    it('should move accessed entry to end (LRU update)', () => {
      // Arrange - Fill cache
      cache.set(40.0, -3.0, createMockResponse('Location 1'));
      cache.set(40.1, -3.1, createMockResponse('Location 2'));
      cache.set(40.2, -3.2, createMockResponse('Location 3'));
      cache.set(40.3, -3.3, createMockResponse('Location 4'));
      cache.set(40.4, -3.4, createMockResponse('Location 5'));

      // Act - Access first entry (moves to end)
      cache.get(40.0, -3.0);
      // Add new entry (should evict second entry, not first)
      cache.set(40.5, -3.5, createMockResponse('Location 6'));

      // Assert
      expect(cache.get(40.0, -3.0)).not.toBeNull(); // First still exists
      expect(cache.get(40.1, -3.1)).toBeNull(); // Second was evicted
    });

    it('should not evict entry when updating existing key', () => {
      // Arrange - Fill cache
      cache.set(40.0, -3.0, createMockResponse('Location 1'));
      cache.set(40.1, -3.1, createMockResponse('Location 2'));
      cache.set(40.2, -3.2, createMockResponse('Location 3'));
      cache.set(40.3, -3.3, createMockResponse('Location 4'));
      cache.set(40.4, -3.4, createMockResponse('Location 5'));

      // Act - Update existing entry (should not trigger eviction)
      cache.set(40.0, -3.0, createMockResponse('Location 1 Updated'));

      // Assert
      expect(cache.size()).toBe(5); // Size unchanged
      expect(cache.get(40.0, -3.0)?.display_name).toBe('Location 1 Updated');
    });
  });

  describe('Cache Statistics', () => {
    it('should report correct cache size', () => {
      // Arrange
      cache.set(40.0, -3.0, createMockResponse('Location 1'));
      cache.set(40.1, -3.1, createMockResponse('Location 2'));

      // Act
      const size = cache.size();

      // Assert
      expect(size).toBe(2);
    });

    it('should report correct utilization percentage', () => {
      // Arrange - Fill 3 of 5 slots
      cache.set(40.0, -3.0, createMockResponse('Location 1'));
      cache.set(40.1, -3.1, createMockResponse('Location 2'));
      cache.set(40.2, -3.2, createMockResponse('Location 3'));

      // Act
      const stats = cache.getStats();

      // Assert
      expect(stats.utilizationPercent).toBe(60); // 3/5 * 100
    });

    it('should include timestamp and access count in stats', () => {
      // Arrange
      const before = Date.now();
      cache.set(40.0, -3.0, createMockResponse('Location 1'));
      const after = Date.now();

      // Act
      const stats = cache.getStats();

      // Assert
      expect(stats.entries).toHaveLength(1);
      expect(stats.entries[0].timestamp).toBeGreaterThanOrEqual(before);
      expect(stats.entries[0].timestamp).toBeLessThanOrEqual(after);
      expect(stats.entries[0].accessCount).toBe(1);
    });
  });

  describe('Cache Utilities', () => {
    it('should clear all entries', () => {
      // Arrange
      cache.set(40.0, -3.0, createMockResponse('Location 1'));
      cache.set(40.1, -3.1, createMockResponse('Location 2'));
      cache.set(40.2, -3.2, createMockResponse('Location 3'));

      // Act
      cache.clear();

      // Assert
      expect(cache.size()).toBe(0);
      expect(cache.get(40.0, -3.0)).toBeNull();
      expect(cache.get(40.1, -3.1)).toBeNull();
      expect(cache.get(40.2, -3.2)).toBeNull();
    });

    it('should check if coordinates are in cache', () => {
      // Arrange
      cache.set(40.416775, -3.70379, createMockResponse('Test Location'));

      // Act
      const exists = cache.has(40.416775, -3.70379);
      const notExists = cache.has(41.0, -4.0);

      // Assert
      expect(exists).toBe(true);
      expect(notExists).toBe(false);
    });

    it('should handle has() with rounded coordinates', () => {
      // Arrange
      cache.set(40.416123, -3.703456, createMockResponse('Test Location'));

      // Act - Different coords but same rounded value
      const exists = cache.has(40.416789, -3.703999);

      // Assert
      expect(exists).toBe(true);
    });
  });

  describe('Edge Cases', () => {
    it('should handle cache size of 1', () => {
      // Arrange
      const smallCache = new GeocodingCache(1);
      const response1 = createMockResponse('Location 1');
      const response2 = createMockResponse('Location 2');

      // Act
      smallCache.set(40.0, -3.0, response1);
      smallCache.set(40.1, -3.1, response2);

      // Assert
      expect(smallCache.size()).toBe(1);
      expect(smallCache.get(40.0, -3.0)).toBeNull(); // Evicted
      expect(smallCache.get(40.1, -3.1)).toEqual(response2); // Current
    });

    it('should handle boundary coordinates (-90, -180)', () => {
      // Arrange
      const response = createMockResponse('South Pole');

      // Act
      cache.set(-90, -180, response);
      const result = cache.get(-90, -180);

      // Assert
      expect(result).toEqual(response);
    });

    it('should handle boundary coordinates (90, 180)', () => {
      // Arrange
      const response = createMockResponse('North Pole');

      // Act
      cache.set(90, 180, response);
      const result = cache.get(90, 180);

      // Assert
      expect(result).toEqual(response);
    });

    it('should handle zero coordinates (0, 0)', () => {
      // Arrange
      const response = createMockResponse('Null Island');

      // Act
      cache.set(0, 0, response);
      const result = cache.get(0, 0);

      // Assert
      expect(result).toEqual(response);
    });
  });
});
