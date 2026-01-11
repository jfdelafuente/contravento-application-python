# Data Model: Reverse Geocoding

**Feature**: 010-reverse-geocoding
**Date**: 2026-01-11
**Database**: No new database tables (uses existing TripLocation model)

## Overview

Feature 010 (Reverse Geocoding) **does not require new database tables**. It extends the existing `trip_locations` table from Feature 009 by populating location names automatically via reverse geocoding when users click the map.

All geocoding data (API responses, cache) is **ephemeral** and lives in:
- **Frontend cache**: Browser memory (Map<string, GeocodingResponse>)
- **API responses**: Transient Nominatim API responses, not persisted

---

## Existing Data Model (No Changes)

### TripLocation Table

**Status**: ✅ Already exists (from Feature 009 - GPS Coordinates)

**Schema** (`backend/src/models/trip.py`):

```python
class TripLocation(Base):
    __tablename__ = "trip_locations"

    # Primary Key
    location_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign Key
    trip_id = Column(String(36), ForeignKey("trips.trip_id", ondelete="CASCADE"), nullable=False)

    # Location Data
    name = Column(String(200), nullable=False)     # POPULATED BY REVERSE GEOCODING
    latitude = Column(Float, nullable=True)        # User-clicked coordinate
    longitude = Column(Float, nullable=True)       # User-clicked coordinate
    sequence = Column(Integer, nullable=False)     # Order in route (0-based)

    # Audit Fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    trip: Mapped["Trip"] = relationship("Trip", back_populates="locations")
```

**Indexes** (already exist):
```sql
CREATE INDEX idx_location_trip ON trip_locations(trip_id);
CREATE INDEX idx_location_sequence ON trip_locations(trip_id, sequence);
```

**Usage in Feature 010**:
- `latitude`, `longitude`: Set from map click event (e.g., 40.416775, -3.703790)
- `name`: Populated from Nominatim reverse geocoding response (e.g., "Parque del Retiro")
- `sequence`: Auto-incremented based on existing locations count

**No schema changes needed** ✅

---

## Frontend Data Structures

### 1. GeocodingResponse (Nominatim API Response)

**Purpose**: Type definition for Nominatim reverse geocoding API response

**TypeScript Interface** (`frontend/src/types/geocoding.ts`):

```typescript
/**
 * Nominatim reverse geocoding API response structure
 *
 * Example response for lat=40.416775, lng=-3.703790:
 * {
 *   "display_name": "Parque del Retiro, Madrid, Comunidad de Madrid, España",
 *   "address": {
 *     "leisure": "Parque del Retiro",
 *     "suburb": "Retiro",
 *     "city": "Madrid",
 *     "state": "Comunidad de Madrid",
 *     "country": "España",
 *     "country_code": "es",
 *     "postcode": "28009"
 *   },
 *   "lat": "40.416775",
 *   "lon": "-3.703790"
 * }
 */
export interface NominatimAddress {
  // Place type (one of these will be present)
  leisure?: string;        // Park, attraction
  amenity?: string;        // Restaurant, cafe, hospital
  shop?: string;           // Store, mall
  tourism?: string;        // Museum, hotel, monument
  road?: string;           // Street name
  building?: string;       // Building name

  // Administrative divisions
  suburb?: string;         // Neighborhood
  city?: string;           // City name
  town?: string;           // Town name (alternative to city)
  village?: string;        // Village name (alternative to city)
  state?: string;          // State/region
  country?: string;        // Country name (localized)
  country_code?: string;   // ISO 3166-1 alpha-2 code (e.g., "es")
  postcode?: string;       // Postal code
}

export interface GeocodingResponse {
  display_name: string;    // Full address string (comma-separated)
  address: NominatimAddress;
  lat: string;             // Returned coordinate (may differ slightly from query)
  lon: string;             // Returned coordinate (may differ slightly from query)
}

/**
 * Error response from Nominatim (when no result found)
 */
export interface GeocodingError {
  error: string;           // Error message (e.g., "Unable to geocode")
}
```

**Field Priority for Location Name**:
1. `address.leisure` (parks, attractions)
2. `address.amenity` (POIs)
3. `address.tourism` (tourist sites)
4. `address.road` (street names)
5. `address.city` or `address.town` or `address.village`
6. `display_name` (full address as fallback)
7. `"Ubicación sin nombre"` (if all above null)

---

### 2. GeocodingCache (Frontend LRU Cache)

**Purpose**: Client-side cache to avoid duplicate Nominatim API calls (rate limit compliance)

**TypeScript Class** (`frontend/src/utils/geocodingCache.ts`):

```typescript
/**
 * Cache entry with timestamp for LRU eviction
 */
interface CacheEntry {
  response: GeocodingResponse;
  timestamp: number;        // Date.now() when cached
  accessCount: number;      // Number of times accessed (for analytics)
}

/**
 * LRU Cache for geocoding responses
 * - Max 100 entries
 * - Key = rounded coordinates (3 decimals → ~111m precision)
 * - Evicts least recently used when full
 */
export class GeocodingCache {
  private cache: Map<string, CacheEntry>;
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  /**
   * Generate cache key from coordinates
   * Rounds to 3 decimals (~111m precision) to group nearby clicks
   *
   * Example:
   *   lat=40.416775, lng=-3.703790 → "40.417,-3.704"
   *   lat=40.416812, lng=-3.703801 → "40.417,-3.704" (same key, cache hit)
   */
  private getCacheKey(lat: number, lng: number): string {
    return `${lat.toFixed(3)},${lng.toFixed(3)}`;
  }

  /**
   * Get cached response for coordinates
   * Updates access timestamp (LRU logic)
   */
  get(lat: number, lng: number): GeocodingResponse | null {
    const key = this.getCacheKey(lat, lng);
    const entry = this.cache.get(key);

    if (entry) {
      // Update access time (move to end of Map for LRU)
      this.cache.delete(key);
      entry.timestamp = Date.now();
      entry.accessCount += 1;
      this.cache.set(key, entry);
      return entry.response;
    }

    return null;
  }

  /**
   * Store geocoding response in cache
   * Evicts oldest entry if cache full
   */
  set(lat: number, lng: number, response: GeocodingResponse): void {
    const key = this.getCacheKey(lat, lng);

    // Evict oldest entry if cache full
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }

    this.cache.set(key, {
      response,
      timestamp: Date.now(),
      accessCount: 1,
    });
  }

  /**
   * Clear all cache entries (e.g., on logout)
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics (for debugging)
   */
  getStats(): { size: number; maxSize: number; hitRate?: number } {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
    };
  }
}
```

**Cache Behavior**:
- **Hit**: User clicks within 111m of previous click → instant response (no API call)
- **Miss**: User clicks >111m away → API call to Nominatim → cache result
- **Eviction**: When cache reaches 100 entries, oldest entry removed (FIFO/LRU)

**Cache Lifetime**: Survives component re-renders but cleared on page reload

---

### 3. LocationSelection (Temporary UI State)

**Purpose**: Represents a pending location being confirmed by user

**TypeScript Interface** (`frontend/src/types/geocoding.ts`):

```typescript
/**
 * Temporary state when user has clicked map but not yet confirmed location
 * Stored in React state until user confirms or cancels
 */
export interface LocationSelection {
  // Clicked coordinates
  latitude: number;
  longitude: number;

  // Geocoding result
  suggestedName: string;          // From Nominatim (e.g., "Parque del Retiro")
  fullAddress: string;            // display_name (e.g., "Parque del Retiro, Madrid, España")

  // User edits
  editedName?: string;            // If user manually edits suggested name

  // Status
  isLoading: boolean;             // True while geocoding API call in progress
  hasError: boolean;              // True if geocoding failed
  errorMessage?: string;          // Spanish error message
}
```

**Lifecycle**:
1. User clicks map → Create LocationSelection with `isLoading=true`
2. Geocoding API returns → Update with `suggestedName`, `isLoading=false`
3. User edits name → Update `editedName`
4. User confirms → Create TripLocation with final name, clear LocationSelection
5. User cancels → Clear LocationSelection

---

## Data Flow Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│ User Interaction                                                 │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ 1. User clicks map at (lat, lng)
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ MapClickHandler Component                                         │
│  - Capture click event via useMapEvents()                         │
│  - Extract coordinates: e.latlng.lat, e.latlng.lng                │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ 2. Call useReverseGeocode hook
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ useReverseGeocode Hook                                            │
│  - Check GeocodingCache for cached response                       │
│  - If cache hit → return instantly                                │
│  - If cache miss → call geocodingService.reverse()                │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ 3. Call Nominatim API (if cache miss)
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ Nominatim API                                                     │
│  GET https://nominatim.openstreetmap.org/reverse                 │
│  ?lat=40.416775&lon=-3.703790&format=json&accept-language=es     │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ 4. Return GeocodingResponse
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ useReverseGeocode Hook                                            │
│  - Parse response                                                 │
│  - Extract place name (leisure/amenity/road/city)                 │
│  - Store in GeocodingCache                                        │
│  - Return { suggestedName, fullAddress }                          │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ 5. Update LocationSelection state
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ LocationConfirmModal                                              │
│  - Show suggested name: "Parque del Retiro"                       │
│  - Show coordinates: (40.416775, -3.703790)                       │
│  - Allow editing name                                             │
│  - User clicks "Confirmar" or "Cancelar"                          │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ 6. User confirms → Call onConfirm(name, lat, lng)
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ TripForm / TripEditPage                                           │
│  - Add location to trip.locations array                           │
│  - Assign next sequence number                                    │
│  - Update form state                                              │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ 7. User saves trip → POST /trips or PUT /trips/:id
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ Backend API                                                       │
│  - Validate location data                                         │
│  - Create TripLocation record with name, lat, lng, sequence       │
│  - Save to trip_locations table                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## API Request/Response Examples

### Nominatim Reverse Geocoding Request

```http
GET https://nominatim.openstreetmap.org/reverse?lat=40.416775&lon=-3.703790&format=json&accept-language=es HTTP/1.1
User-Agent: ContraVento/1.0 (contact@contravento.com)
Accept: application/json
```

**Query Parameters**:
- `lat`: Latitude in decimal degrees (required)
- `lon`: Longitude in decimal degrees (required)
- `format=json`: Response format (required)
- `accept-language=es`: Prefer Spanish names (optional)

### Nominatim Response (Success)

```json
{
  "place_id": 123456789,
  "licence": "Data © OpenStreetMap contributors, ODbL 1.0",
  "osm_type": "way",
  "osm_id": 987654321,
  "lat": "40.416775",
  "lon": "-3.703790",
  "display_name": "Parque del Retiro, Retiro, Madrid, Comunidad de Madrid, 28009, España",
  "address": {
    "leisure": "Parque del Retiro",
    "suburb": "Retiro",
    "city": "Madrid",
    "state": "Comunidad de Madrid",
    "postcode": "28009",
    "country": "España",
    "country_code": "es"
  },
  "boundingbox": ["40.4089508", "40.4226627", "-3.6914111", "-3.6753464"]
}
```

**Extracted Location Name**: "Parque del Retiro" (from `address.leisure`)

### Nominatim Response (No Result Found)

```json
{
  "error": "Unable to geocode"
}
```

**Handling**: Use default name "Ubicación sin nombre" and allow user to edit

---

## Validation Rules

### Coordinate Validation (Frontend & Backend)

```typescript
// Already exists from Feature 009 (no changes needed)
function validateCoordinates(lat: number | null, lng: number | null): boolean {
  if (lat === null || lng === null) return true; // Allow null coordinates

  // Latitude bounds: -90 to 90
  if (lat < -90 || lat > 90) {
    throw new Error('La latitud debe estar entre -90 y 90 grados');
  }

  // Longitude bounds: -180 to 180
  if (lng < -180 || lng > 180) {
    throw new Error('La longitud debe estar entre -180 y 180 grados');
  }

  return true;
}
```

### Location Name Validation

```typescript
function validateLocationName(name: string): boolean {
  // Min length: 1 character
  if (name.trim().length === 0) {
    throw new Error('El nombre de la ubicación no puede estar vacío');
  }

  // Max length: 200 characters (matches DB column)
  if (name.length > 200) {
    throw new Error('El nombre de la ubicación no puede superar 200 caracteres');
  }

  return true;
}
```

---

## Database Migrations

**No migrations required** ✅

Feature 010 uses the existing `trip_locations` table without schema changes. All geocoding data is ephemeral (frontend cache + API responses).

---

## Performance Considerations

### Cache Hit Rate Target

- **Goal**: >70% cache hit rate (most location clicks within 111m of previous clicks)
- **Measurement**: Log cache hits/misses to console during development
- **Impact**: Cache hit = 0ms response time (vs 200-2000ms API call)

### Database Query Performance

- **No changes**: Existing indexes on `trip_id` and `(trip_id, sequence)` remain sufficient
- **Query pattern**: Same as Feature 009 (eager load locations with trip)

### API Response Time

- **Nominatim p95**: <2 seconds (measured via browser DevTools)
- **Timeout**: 5 seconds (fallback to default name if exceeded)
- **Retry**: No automatic retry (user can manually retry by clicking again)

---

## Summary

Feature 010 **does not modify the database schema**. It enhances the existing user workflow by:

1. **Frontend**: Populating `TripLocation.name` via Nominatim reverse geocoding API
2. **Cache**: Storing responses in browser memory (Map-based LRU cache)
3. **UX**: Allowing users to click map instead of manually entering names

**Zero database migrations** ✅
**Zero new tables** ✅
**Zero schema changes** ✅

**Next**: Proceed to Phase 1 (contracts/) and quickstart.md
