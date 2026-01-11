# Quickstart: Reverse Geocoding Implementation

**Feature**: 010-reverse-geocoding
**Date**: 2026-01-11
**Prerequisites**: Feature 009 (GPS Coordinates) completed
**Estimated Time**: 3-4 days

## Overview

This guide walks developers through implementing reverse geocoding functionality that allows users to click a map to automatically select locations with GPS coordinates and place names.

**What You'll Build**:
1. Frontend geocoding service (Nominatim API client)
2. LRU cache for geocoding responses
3. Map click handler component
4. Location confirmation modal
5. Edit mode for draggable markers
6. Integration with existing TripForm

---

## Step 1: Install Dependencies

### Frontend

```bash
cd frontend
npm install lodash.debounce@^4.0.0
npm install --save-dev @types/lodash.debounce
```

**Why lodash.debounce?**
- Rate limiting: Prevent rapid map clicks from violating Nominatim's 1 req/sec limit
- UX: Avoid unnecessary API calls while user is still deciding where to click

---

## Step 2: Create Type Definitions

**File**: `frontend/src/types/geocoding.ts`

```typescript
/**
 * Nominatim reverse geocoding API response
 */
export interface NominatimAddress {
  leisure?: string;        // Park, garden
  amenity?: string;        // Restaurant, hospital
  tourism?: string;        // Museum, monument
  shop?: string;           // Store, mall
  road?: string;           // Street name
  city?: string;           // City name
  town?: string;           // Town name
  village?: string;        // Village name
  state?: string;          // State/region
  country?: string;        // Country name
  country_code?: string;   // ISO code (e.g., "es")
  postcode?: string;       // Postal code
}

export interface GeocodingResponse {
  display_name: string;
  address: NominatimAddress;
  lat: string;
  lon: string;
}

export interface GeocodingError {
  error: string;
}

/**
 * Pending location selection (before user confirms)
 */
export interface LocationSelection {
  latitude: number;
  longitude: number;
  suggestedName: string;
  fullAddress: string;
  editedName?: string;
  isLoading: boolean;
  hasError: boolean;
  errorMessage?: string;
}
```

---

## Step 3: Implement Geocoding Cache

**File**: `frontend/src/utils/geocodingCache.ts`

```typescript
import { GeocodingResponse } from '../types/geocoding';

interface CacheEntry {
  response: GeocodingResponse;
  timestamp: number;
  accessCount: number;
}

export class GeocodingCache {
  private cache: Map<string, CacheEntry>;
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  private getCacheKey(lat: number, lng: number): string {
    // Round to 3 decimals (~111m precision)
    return `${lat.toFixed(3)},${lng.toFixed(3)}`;
  }

  get(lat: number, lng: number): GeocodingResponse | null {
    const key = this.getCacheKey(lat, lng);
    const entry = this.cache.get(key);

    if (entry) {
      // Update LRU: move to end
      this.cache.delete(key);
      entry.timestamp = Date.now();
      entry.accessCount += 1;
      this.cache.set(key, entry);
      return entry.response;
    }

    return null;
  }

  set(lat: number, lng: number, response: GeocodingResponse): void {
    const key = this.getCacheKey(lat, lng);

    // Evict oldest if full
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

  clear(): void {
    this.cache.clear();
  }
}
```

**Usage**:
```typescript
const cache = new GeocodingCache(); // Singleton instance

// Check cache before API call
const cached = cache.get(40.416775, -3.703790);
if (cached) {
  // Instant response
} else {
  // Call API, then cache.set(lat, lng, response)
}
```

---

## Step 4: Create Geocoding Service

**File**: `frontend/src/services/geocodingService.ts`

```typescript
import axios, { AxiosError } from 'axios';
import { GeocodingResponse, GeocodingError } from '../types/geocoding';

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org';
const USER_AGENT = 'ContraVento/1.0 (contact@contravento.com)';

export async function reverseGeocode(
  lat: number,
  lng: number
): Promise<GeocodingResponse> {
  // Validate coordinates
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
    throw new Error('Coordenadas inválidas');
  }

  try {
    const response = await axios.get<GeocodingResponse | GeocodingError>(
      `${NOMINATIM_BASE_URL}/reverse`,
      {
        params: {
          lat,
          lon: lng,
          format: 'json',
          'accept-language': 'es',
          addressdetails: 1,
        },
        headers: { 'User-Agent': USER_AGENT },
        timeout: 5000,
      }
    );

    if ('error' in response.data) {
      throw new Error('No se pudo geocodificar la ubicación');
    }

    return response.data as GeocodingResponse;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response?.status === 429) {
        throw new Error('Demasiadas solicitudes. Espera un momento.');
      }
      if (axiosError.code === 'ECONNABORTED') {
        throw new Error('El servidor no responde. Verifica tu conexión.');
      }
    }
    throw new Error('Error al conectar con el servicio de mapas');
  }
}

export function extractLocationName(response: GeocodingResponse): string {
  const { address } = response;

  // Priority order: leisure > amenity > tourism > shop > road > city
  const name =
    address.leisure ||
    address.amenity ||
    address.tourism ||
    address.shop ||
    address.road ||
    address.city ||
    address.town ||
    address.village;

  if (name) return name;

  // Fallback to display_name (truncated)
  if (response.display_name) {
    return response.display_name.length > 50
      ? response.display_name.substring(0, 50) + '...'
      : response.display_name;
  }

  return 'Ubicación sin nombre';
}
```

---

## Step 5: Create Reverse Geocoding Hook

**File**: `frontend/src/hooks/useReverseGeocode.ts`

```typescript
import { useState, useRef, useCallback } from 'react';
import { debounce } from 'lodash';
import { reverseGeocode, extractLocationName } from '../services/geocodingService';
import { GeocodingCache } from '../utils/geocodingCache';

const cache = new GeocodingCache();

export function useReverseGeocode() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const geocode = useCallback(
    async (lat: number, lng: number): Promise<{ name: string; fullAddress: string }> => {
      setIsLoading(true);
      setError(null);

      // Check cache first
      const cached = cache.get(lat, lng);
      if (cached) {
        setIsLoading(false);
        return {
          name: extractLocationName(cached),
          fullAddress: cached.display_name,
        };
      }

      // Call API
      try {
        const response = await reverseGeocode(lat, lng);
        cache.set(lat, lng, response);

        setIsLoading(false);
        return {
          name: extractLocationName(response),
          fullAddress: response.display_name,
        };
      } catch (err: any) {
        setError(err.message || 'Error al geocodificar');
        setIsLoading(false);

        // Return default name on error
        return {
          name: 'Ubicación sin nombre',
          fullAddress: `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`,
        };
      }
    },
    []
  );

  // Debounced version (1 second delay)
  const debouncedGeocode = useRef(
    debounce(geocode, 1000, { leading: false, trailing: true })
  ).current;

  return {
    geocode,
    debouncedGeocode,
    isLoading,
    error,
  };
}
```

---

## Step 6: Create Map Click Handler Component

**File**: `frontend/src/components/trips/MapClickHandler.tsx`

```typescript
import React from 'react';
import { useMapEvents } from 'react-leaflet';

interface MapClickHandlerProps {
  enabled: boolean;
  onMapClick: (lat: number, lng: number) => void;
}

export const MapClickHandler: React.FC<MapClickHandlerProps> = ({
  enabled,
  onMapClick,
}) => {
  useMapEvents({
    click(e) {
      if (enabled) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });

  return null; // This component renders nothing
};
```

**Usage** (in TripMap.tsx):
```typescript
<MapContainer>
  <MapClickHandler
    enabled={isEditMode}
    onMapClick={(lat, lng) => handleMapClick(lat, lng)}
  />
  {/* Other map components */}
</MapContainer>
```

---

## Step 7: Create Location Confirmation Modal

**File**: `frontend/src/components/trips/LocationConfirmModal.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import './LocationConfirmModal.css';

interface LocationConfirmModalProps {
  isOpen: boolean;
  suggestedName: string;
  coordinates: { lat: number; lng: number };
  isLoading?: boolean;
  onConfirm: (name: string, lat: number, lng: number) => void;
  onCancel: () => void;
}

export const LocationConfirmModal: React.FC<LocationConfirmModalProps> = ({
  isOpen,
  suggestedName,
  coordinates,
  isLoading = false,
  onConfirm,
  onCancel,
}) => {
  const [editedName, setEditedName] = useState(suggestedName);

  useEffect(() => {
    setEditedName(suggestedName);
  }, [suggestedName]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm(editedName || suggestedName, coordinates.lat, coordinates.lng);
  };

  return (
    <div className="location-confirm-modal-overlay" onClick={onCancel}>
      <div className="location-confirm-modal" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal-title">Confirmar Ubicación</h3>

        {isLoading ? (
          <div className="modal-loading">
            <div className="spinner" />
            <p>Obteniendo nombre del lugar...</p>
          </div>
        ) : (
          <>
            <div className="modal-field">
              <label htmlFor="location-name">Nombre de la ubicación</label>
              <input
                id="location-name"
                type="text"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                placeholder="Nombre de la ubicación"
              />
            </div>

            <div className="modal-coordinates">
              <p>
                <strong>Coordenadas:</strong> {coordinates.lat.toFixed(6)},{' '}
                {coordinates.lng.toFixed(6)}
              </p>
            </div>

            <div className="modal-actions">
              <button className="btn-cancel" onClick={onCancel}>
                Cancelar
              </button>
              <button
                className="btn-confirm"
                onClick={handleConfirm}
                disabled={!editedName.trim()}
              >
                Confirmar
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
```

**Styles** (`LocationConfirmModal.css`): Create basic modal styles with overlay, centered box, and action buttons.

---

## Step 8: Update TripMap Component

**File**: `frontend/src/components/trips/TripMap.tsx`

**Add Props**:
```typescript
interface TripMapProps {
  locations: TripLocation[];
  tripTitle: string;
  isEditMode?: boolean;                    // NEW: Enable edit mode
  onMapClick?: (lat: number, lng: number) => void;  // NEW: Click handler
  onMarkerDrag?: (locationId: string, lat: number, lng: number) => void;  // NEW: Drag handler
}
```

**Add MapClickHandler**:
```typescript
import { MapClickHandler } from './MapClickHandler';

export const TripMap: React.FC<TripMapProps> = ({
  locations,
  tripTitle,
  isEditMode = false,
  onMapClick,
  onMarkerDrag,
}) => {
  // ... existing code ...

  return (
    <MapContainer>
      {/* NEW: Add click handler */}
      {isEditMode && onMapClick && (
        <MapClickHandler enabled={isEditMode} onMapClick={onMapClick} />
      )}

      <TileLayer ... />

      {validLocations.map((location) => (
        <Marker
          key={location.location_id}
          position={[location.latitude!, location.longitude!]}
          draggable={isEditMode}  // NEW: Enable dragging in edit mode
          eventHandlers={{
            dragend: (e) => {
              if (onMarkerDrag) {
                const pos = e.target.getLatLng();
                onMarkerDrag(location.location_id, pos.lat, pos.lng);
              }
            },
          }}
        >
          <Popup>{location.name}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};
```

---

## Step 9: Integrate with TripForm

**File**: `frontend/src/pages/TripEditPage.tsx` or `TripFormWizard.tsx`

```typescript
import { useState } from 'react';
import { useReverseGeocode } from '../hooks/useReverseGeocode';
import { LocationConfirmModal } from '../components/trips/LocationConfirmModal';

function TripEditPage() {
  const [isEditMode, setIsEditMode] = useState(false);
  const [locationSelection, setLocationSelection] = useState<LocationSelection | null>(null);
  const { debouncedGeocode, isLoading } = useReverseGeocode();

  const handleMapClick = async (lat: number, lng: number) => {
    setLocationSelection({
      latitude: lat,
      longitude: lng,
      suggestedName: '',
      fullAddress: '',
      isLoading: true,
      hasError: false,
    });

    const result = await debouncedGeocode(lat, lng);

    setLocationSelection(prev => ({
      ...prev!,
      suggestedName: result.name,
      fullAddress: result.fullAddress,
      isLoading: false,
    }));
  };

  const handleConfirmLocation = (name: string, lat: number, lng: number) => {
    // Add to locations array
    const newLocation = {
      location_id: `temp-${Date.now()}`,
      name,
      latitude: lat,
      longitude: lng,
      sequence: locations.length,
    };

    setLocations([...locations, newLocation]);
    setLocationSelection(null);
  };

  return (
    <>
      <button onClick={() => setIsEditMode(!isEditMode)}>
        {isEditMode ? 'Guardar Cambios' : 'Editar Ubicaciones en Mapa'}
      </button>

      <TripMap
        locations={locations}
        tripTitle={trip.title}
        isEditMode={isEditMode}
        onMapClick={handleMapClick}
        onMarkerDrag={handleMarkerDrag}
      />

      <LocationConfirmModal
        isOpen={!!locationSelection}
        suggestedName={locationSelection?.suggestedName || ''}
        coordinates={{
          lat: locationSelection?.latitude || 0,
          lng: locationSelection?.longitude || 0,
        }}
        isLoading={locationSelection?.isLoading || false}
        onConfirm={handleConfirmLocation}
        onCancel={() => setLocationSelection(null)}
      />
    </>
  );
}
```

---

## Step 10: Testing

### Unit Tests

**File**: `frontend/tests/unit/geocodingService.test.ts`

```typescript
import { reverseGeocode, extractLocationName } from '../../src/services/geocodingService';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

const mock = new MockAdapter(axios);

describe('Geocoding Service', () => {
  it('extracts leisure name from response', () => {
    const response = {
      display_name: 'Parque del Retiro, Madrid, España',
      address: { leisure: 'Parque del Retiro', city: 'Madrid' },
      lat: '40.416775',
      lon: '-3.703790',
    };

    expect(extractLocationName(response)).toBe('Parque del Retiro');
  });

  it('handles API success response', async () => {
    mock.onGet(/nominatim/).reply(200, {
      display_name: 'Madrid, España',
      address: { city: 'Madrid' },
      lat: '40.416775',
      lon: '-3.703790',
    });

    const result = await reverseGeocode(40.416775, -3.703790);
    expect(result.address.city).toBe('Madrid');
  });
});
```

### Integration Tests

**File**: `frontend/tests/integration/TripForm.geocoding.test.tsx`

```typescript
describe('Map Click to Add Location', () => {
  it('shows confirmation modal after map click', async () => {
    render(<TripEditPage />);

    // Enable edit mode
    fireEvent.click(screen.getByText('Editar Ubicaciones en Mapa'));

    // Simulate map click
    const map = screen.getByTestId('trip-map');
    fireEvent.click(map, { clientX: 100, clientY: 100 });

    // Wait for modal
    await waitFor(() => {
      expect(screen.getByText('Confirmar Ubicación')).toBeInTheDocument();
    });
  });
});
```

---

## Troubleshooting

### Issue: Rate limit 429 errors

**Solution**: Check debounce configuration. Ensure `debouncedGeocode` uses 1-second delay.

### Issue: Cache not working

**Solution**: Verify cache instance is singleton (not recreated on re-render). Use `useRef` or module-level instance.

### Issue: Modal not showing

**Solution**: Check `isOpen` prop is correctly set when `locationSelection` exists.

### Issue: Markers not draggable

**Solution**: Verify `isEditMode=true` and `draggable={isEditMode}` prop passed to Marker.

---

## Deployment Checklist

- [ ] `lodash.debounce` added to package.json
- [ ] All new TypeScript files have no type errors (`npm run type-check`)
- [ ] Unit tests pass (`npm run test`)
- [ ] Integration tests pass
- [ ] Cache hit rate >70% (verify in console logs)
- [ ] No Nominatim rate limit violations (check Network tab for 429)
- [ ] Modal accessible (keyboard navigation, ARIA labels)
- [ ] Works on mobile (touch events for map click and drag)
- [ ] Error messages in Spanish
- [ ] Loading states visible during geocoding

---

## Next Steps

After completing this implementation:
1. Run `/speckit.tasks` to generate task breakdown
2. Implement Phase 1 (map click + modal)
3. Implement Phase 2 (marker drag)
4. Implement Phase 3 (name editing)
5. Test on staging
6. Deploy to production

**Estimated Time**: 3-4 days (P1: 1-2 days, P2: 1 day, P3: 0.5 day, testing: 0.5 day)
