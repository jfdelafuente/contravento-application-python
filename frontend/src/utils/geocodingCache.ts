/**
 * LRU Cache for reverse geocoding API responses
 * Feature: 010-reverse-geocoding
 *
 * Implements Least Recently Used (LRU) eviction policy to cache Nominatim API responses
 * and reduce API calls. Cache key is based on rounded coordinates (~111m precision).
 */

import type { GeocodingResponse } from '../types/geocoding';

/**
 * Cache entry with metadata for LRU eviction
 */
interface CacheEntry {
  /** Geocoding API response */
  response: GeocodingResponse;
  /** Timestamp when entry was created or last accessed (for LRU) */
  timestamp: number;
  /** Number of times this entry has been accessed */
  accessCount: number;
}

/**
 * LRU Cache for geocoding responses
 *
 * Features:
 * - Maximum 100 entries (configurable)
 * - Coordinate rounding to 3 decimals (~111m precision) for cache key
 * - LRU eviction when cache is full
 * - Access count tracking for analytics
 *
 * Performance:
 * - get(): O(1) average case
 * - set(): O(1) average case (Map maintains insertion order in modern JS)
 * - Cache hit: 0ms (instant)
 * - Cache miss: ~200-2000ms (API call)
 */
export class GeocodingCache {
  private cache: Map<string, CacheEntry>;
  private maxSize: number;
  private hits: number = 0;
  private misses: number = 0;
  private enableLogging: boolean;

  /**
   * Initialize cache with maximum size
   * @param maxSize Maximum number of entries (default: 100)
   * @param enableLogging Enable development logging for cache hit/miss rates (default: false)
   */
  constructor(maxSize: number = 100, enableLogging: boolean = false) {
    this.cache = new Map();
    this.maxSize = maxSize;
    this.enableLogging = enableLogging;
  }

  /**
   * Generate cache key from coordinates
   * Rounds to 3 decimal places (~111m precision at equator)
   *
   * Examples:
   * - (40.416775, -3.703790) → "40.417,-3.704"
   * - (40.416123, -3.703456) → "40.416,-3.703"
   *
   * @param lat Latitude in decimal degrees
   * @param lng Longitude in decimal degrees
   * @returns Cache key string
   */
  private getCacheKey(lat: number, lng: number): string {
    return `${lat.toFixed(3)},${lng.toFixed(3)}`;
  }

  /**
   * Get cached geocoding response for coordinates
   *
   * On cache hit:
   * - Moves entry to end (LRU update)
   * - Updates timestamp and access count
   * - Returns cached response
   *
   * On cache miss:
   * - Returns null
   *
   * @param lat Latitude in decimal degrees
   * @param lng Longitude in decimal degrees
   * @returns Cached response or null if not found
   */
  get(lat: number, lng: number): GeocodingResponse | null {
    const key = this.getCacheKey(lat, lng);
    const entry = this.cache.get(key);

    if (entry) {
      // Cache HIT
      this.hits += 1;

      if (this.enableLogging) {
        const hitRate = ((this.hits / (this.hits + this.misses)) * 100).toFixed(1);
        console.log(`[GeoCoding Cache] HIT (${hitRate}% hit rate) - Key: ${key}, Access count: ${entry.accessCount + 1}`);
      }

      // Update LRU: delete and re-insert to move to end
      this.cache.delete(key);
      entry.timestamp = Date.now();
      entry.accessCount += 1;
      this.cache.set(key, entry);

      return entry.response;
    }

    // Cache MISS
    this.misses += 1;

    if (this.enableLogging) {
      const hitRate = ((this.hits / (this.hits + this.misses)) * 100).toFixed(1);
      console.log(`[GeoCoding Cache] MISS (${hitRate}% hit rate) - Key: ${key}`);
    }

    return null;
  }

  /**
   * Store geocoding response in cache
   *
   * If cache is full:
   * - Evicts least recently used entry (first entry in Map)
   * - Adds new entry at the end
   *
   * @param lat Latitude in decimal degrees
   * @param lng Longitude in decimal degrees
   * @param response Geocoding API response to cache
   */
  set(lat: number, lng: number, response: GeocodingResponse): void {
    const key = this.getCacheKey(lat, lng);

    // If cache is full, evict LRU entry (first entry)
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const firstKey = this.cache.keys().next().value;
      if (firstKey) {
        this.cache.delete(firstKey);
      }
    }

    // Add or update entry (moves to end if exists)
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }

    this.cache.set(key, {
      response,
      timestamp: Date.now(),
      accessCount: 1,
    });
  }

  /**
   * Clear all cached entries
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get current cache size
   * @returns Number of cached entries
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Check if coordinates are in cache
   * @param lat Latitude in decimal degrees
   * @param lng Longitude in decimal degrees
   * @returns True if cache contains entry for these coordinates
   */
  has(lat: number, lng: number): boolean {
    const key = this.getCacheKey(lat, lng);
    return this.cache.has(key);
  }

  /**
   * Get cache statistics for monitoring
   * Development-only feature for observing cache performance
   *
   * @returns Cache stats object
   */
  getStats(): {
    size: number;
    maxSize: number;
    utilizationPercent: number;
    hits: number;
    misses: number;
    hitRate: number;
    entries: Array<{
      key: string;
      timestamp: number;
      accessCount: number;
    }>;
  } {
    const entries = Array.from(this.cache.entries()).map(([key, entry]) => ({
      key,
      timestamp: entry.timestamp,
      accessCount: entry.accessCount,
    }));

    const totalRequests = this.hits + this.misses;
    const hitRate = totalRequests > 0 ? (this.hits / totalRequests) * 100 : 0;

    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      utilizationPercent: (this.cache.size / this.maxSize) * 100,
      hits: this.hits,
      misses: this.misses,
      hitRate,
      entries,
    };
  }

  /**
   * Enable or disable console logging for cache operations
   * @param enable True to enable logging, false to disable
   */
  setLogging(enable: boolean): void {
    this.enableLogging = enable;
  }
}

// Export singleton instance for application-wide use
// Enable logging in development mode (T047)
const isDevelopment = import.meta.env.MODE === 'development';
export const geocodingCache = new GeocodingCache(100, isDevelopment);
