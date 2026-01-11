# API Contracts: Reverse Geocoding

**Feature**: 010-reverse-geocoding
**Date**: 2026-01-11

## Overview

Feature 010 (Reverse Geocoding) **does not add new backend API endpoints**. Instead, it uses the **Nominatim OpenStreetMap API** directly from the frontend.

**Architecture Decision**:
- ✅ **Frontend → Nominatim** (direct calls via axios)
- ❌ **Frontend → Backend → Nominatim** (backend proxy not needed initially)

**Rationale**:
1. Nominatim supports CORS, allowing direct browser calls
2. Lower latency (no backend hop)
3. Simpler architecture (fewer moving parts)
4. Rate limiting enforced client-side (1 req/sec)
5. No sensitive data to protect (only coordinates sent)

**Future Consideration**: Add backend proxy if rate limiting or server-side caching needed across users.

---

## External API: Nominatim Reverse Geocoding

### Base URL

```
https://nominatim.openstreetmap.org
```

### Endpoint

**GET /reverse**

Reverse geocode a latitude/longitude coordinate to a human-readable address.

---

### Request

**HTTP Method**: `GET`

**Query Parameters**:

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `lat` | float | ✅ Yes | Latitude in decimal degrees (-90 to 90) | `40.416775` |
| `lon` | float | ✅ Yes | Longitude in decimal degrees (-180 to 180) | `-3.703790` |
| `format` | string | ✅ Yes | Response format (must be `json`) | `json` |
| `accept-language` | string | ⚪ Optional | Preferred language for place names (ISO 639-1) | `es` |
| `zoom` | int | ⚪ Optional | Detail level (3=country, 10=street, 18=building). Default: 18 | `18` |
| `addressdetails` | int | ⚪ Optional | Include address breakdown (0 or 1). Default: 1 | `1` |

**Required Headers**:

```http
User-Agent: ContraVento/1.0 (contact@contravento.com)
Accept: application/json
```

**Example Request**:

```http
GET /reverse?lat=40.416775&lon=-3.703790&format=json&accept-language=es HTTP/1.1
Host: nominatim.openstreetmap.org
User-Agent: ContraVento/1.0 (contact@contravento.com)
Accept: application/json
```

**cURL Example**:

```bash
curl -H "User-Agent: ContraVento/1.0 (contact@contravento.com)" \
     "https://nominatim.openstreetmap.org/reverse?lat=40.416775&lon=-3.703790&format=json&accept-language=es"
```

---

### Response

#### Success Response (200 OK)

**Content-Type**: `application/json`

**Schema**:

```json
{
  "place_id": integer,
  "licence": string,
  "osm_type": string,
  "osm_id": integer,
  "lat": string,
  "lon": string,
  "display_name": string,
  "address": {
    "leisure": string | undefined,
    "amenity": string | undefined,
    "shop": string | undefined,
    "tourism": string | undefined,
    "road": string | undefined,
    "suburb": string | undefined,
    "city": string | undefined,
    "town": string | undefined,
    "village": string | undefined,
    "state": string | undefined,
    "country": string | undefined,
    "country_code": string | undefined,
    "postcode": string | undefined
  },
  "boundingbox": [string, string, string, string]
}
```

**Example Response** (Madrid park):

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

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `place_id` | integer | Unique identifier for this place in OSM database |
| `osm_type` | string | OSM object type (`node`, `way`, `relation`) |
| `osm_id` | integer | OSM object ID |
| `lat`, `lon` | string | Returned coordinates (may differ slightly from query) |
| `display_name` | string | Full address as comma-separated string |
| `address` | object | Structured address components (see below) |
| `boundingbox` | array | Geographic bounds [min_lat, max_lat, min_lon, max_lon] |

**Address Object Fields** (all optional):

- `leisure`: Park, garden, playground
- `amenity`: Restaurant, cafe, hospital, school
- `shop`: Store, supermarket, mall
- `tourism`: Museum, hotel, monument, attraction
- `road`: Street name
- `suburb`: Neighborhood name
- `city` / `town` / `village`: Municipality name (mutually exclusive)
- `state`: State/region/province
- `country`: Country name (localized)
- `country_code`: ISO 3166-1 alpha-2 code (e.g., `es`)
- `postcode`: Postal code

---

#### Error Response (No Result Found)

**Status**: 200 OK (but with error field)

**Content-Type**: `application/json`

**Schema**:

```json
{
  "error": string
}
```

**Example**:

```json
{
  "error": "Unable to geocode"
}
```

**Common Causes**:
- Coordinates in middle of ocean
- Coordinates in uninhabited area (desert, mountains)
- Coordinates outside valid bounds (invalid lat/lng)

---

#### Rate Limit Response (429 Too Many Requests)

**Status**: 429 Too Many Requests

**Headers**:

```http
Retry-After: 1
```

**Body**: Plain text error message

```
Request blocked due to excessive use. Please reduce your request rate.
```

**Rate Limit Policy** (Nominatim free tier):
- Maximum **1 request per second**
- Based on IP address
- Violation may result in temporary or permanent IP ban

**Frontend Mitigation**:
- Debounce map clicks (1-second delay)
- Cache responses (avoid duplicate requests)
- Show user-friendly error if rate limit exceeded

---

### Response Parsing Strategy

**Goal**: Extract most relevant place name for location

**Priority Order**:

1. **`address.leisure`** → Parks, gardens, playgrounds
   - Example: "Parque del Retiro"

2. **`address.amenity`** → POIs (restaurants, cafes, hospitals)
   - Example: "Hospital Gregorio Marañón"

3. **`address.tourism`** → Tourist attractions
   - Example: "Museo del Prado"

4. **`address.shop`** → Retail locations
   - Example: "El Corte Inglés"

5. **`address.road`** → Street names
   - Example: "Calle de Alcalá"

6. **`address.city`** / `address.town`/ `address.village` → Municipality
   - Example: "Madrid"

7. **`display_name`** → Full address as fallback
   - Example: "Parque del Retiro, Retiro, Madrid, Comunidad de Madrid, 28009, España"
   - **Note**: Truncate if too long (>50 chars) and append "..."

8. **"Ubicación sin nombre"** → If all above are null
   - Allows user to manually enter name

**Implementation** (`frontend/src/services/geocodingService.ts`):

```typescript
function extractLocationName(response: GeocodingResponse): string {
  const { address } = response;

  // Priority 1-6: Check address components
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

  // Priority 7: Use display_name (truncated)
  if (response.display_name) {
    return response.display_name.length > 50
      ? response.display_name.substring(0, 50) + '...'
      : response.display_name;
  }

  // Priority 8: Default fallback
  return 'Ubicación sin nombre';
}
```

---

## Frontend Service Implementation

### File: `frontend/src/services/geocodingService.ts`

**API Client**:

```typescript
import axios, { AxiosError } from 'axios';
import { GeocodingResponse, GeocodingError } from '../types/geocoding';

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org';
const USER_AGENT = 'ContraVento/1.0 (contact@contravento.com)';

/**
 * Reverse geocode coordinates to place name
 *
 * @param lat - Latitude in decimal degrees (-90 to 90)
 * @param lng - Longitude in decimal degrees (-180 to 180)
 * @returns Geocoding response with place name and address
 * @throws Error if API call fails or coordinates invalid
 */
export async function reverseGeocode(
  lat: number,
  lng: number
): Promise<GeocodingResponse> {
  // Validate coordinates
  if (lat < -90 || lat > 90) {
    throw new Error('Latitud inválida: debe estar entre -90 y 90 grados');
  }
  if (lng < -180 || lng > 180) {
    throw new Error('Longitud inválida: debe estar entre -180 y 180 grados');
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
          zoom: 18,
        },
        headers: {
          'User-Agent': USER_AGENT,
        },
        timeout: 5000, // 5-second timeout
      }
    );

    // Check for error response
    if ('error' in response.data) {
      throw new Error(`Geocoding failed: ${response.data.error}`);
    }

    return response.data as GeocodingResponse;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;

      // Rate limit exceeded
      if (axiosError.response?.status === 429) {
        throw new Error(
          'Demasiadas solicitudes. Por favor, espera un momento e intenta de nuevo.'
        );
      }

      // Network timeout
      if (axiosError.code === 'ECONNABORTED') {
        throw new Error(
          'El servidor de mapas no responde. Verifica tu conexión a internet.'
        );
      }

      // Generic network error
      throw new Error(
        'No se pudo conectar con el servicio de mapas. Intenta nuevamente.'
      );
    }

    // Unknown error
    throw error;
  }
}

/**
 * Extract most relevant place name from geocoding response
 */
export function extractLocationName(response: GeocodingResponse): string {
  const { address } = response;

  // Priority: leisure > amenity > tourism > shop > road > city/town
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

  // Default
  return 'Ubicación sin nombre';
}
```

---

## Error Handling

### Frontend Error Scenarios

| Error | Detection | User Message (Spanish) | Recovery Action |
|-------|-----------|------------------------|-----------------|
| Invalid coordinates | Validate before API call | "Coordenadas inválidas" | Don't call API, log error |
| Network timeout (5s) | axios timeout | "El servidor de mapas no responde. Verifica tu conexión a internet." | Fallback to default name |
| Rate limit (429) | HTTP status code | "Demasiadas solicitudes. Por favor, espera un momento e intenta de nuevo." | Show retry button after 2s |
| No result found | `error` field in response | "No se pudo obtener el nombre del lugar" | Use "Ubicación sin nombre" |
| API error (500) | HTTP status code | "Error al conectar con el servicio de mapas" | Fallback to default name |

---

## Testing

### Manual Testing

```bash
# Test reverse geocoding (Madrid park)
curl -H "User-Agent: ContraVento/1.0 (test@example.com)" \
     "https://nominatim.openstreetmap.org/reverse?lat=40.416775&lon=-3.703790&format=json&accept-language=es"

# Test ocean location (should return error)
curl -H "User-Agent: ContraVento/1.0 (test@example.com)" \
     "https://nominatim.openstreetmap.org/reverse?lat=0&lon=0&format=json"

# Test invalid coordinates (should return 400 or error)
curl -H "User-Agent: ContraVento/1.0 (test@example.com)" \
     "https://nominatim.openstreetmap.org/reverse?lat=100&lon=200&format=json"
```

### Integration Tests

```typescript
// Mock axios for testing
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { reverseGeocode, extractLocationName } from './geocodingService';

const mock = new MockAdapter(axios);

// Success case
mock.onGet(/nominatim.*reverse/).reply(200, {
  display_name: 'Parque del Retiro, Madrid, España',
  address: {
    leisure: 'Parque del Retiro',
    city: 'Madrid',
    country: 'España',
  },
  lat: '40.416775',
  lon: '-3.703790',
});

test('returns place name from successful geocoding', async () => {
  const response = await reverseGeocode(40.416775, -3.703790);
  const name = extractLocationName(response);
  expect(name).toBe('Parque del Retiro');
});

// Error case
mock.onGet(/nominatim.*reverse/).reply(200, { error: 'Unable to geocode' });

test('throws error when geocoding fails', async () => {
  await expect(reverseGeocode(0, 0)).rejects.toThrow('Geocoding failed');
});
```

---

## Rate Limiting & Caching

### Rate Limit Compliance

**Nominatim Policy**: Maximum 1 request per second

**Frontend Implementation**:
1. **Debounce map clicks**: 1-second delay before triggering geocoding
2. **Cache responses**: Store in `GeocodingCache` to avoid duplicate calls
3. **Visual feedback**: Show loading spinner while API call in progress
4. **Error handling**: If 429 received, show retry button after 2 seconds

### Cache Strategy

See `data-model.md` for full `GeocodingCache` implementation.

**Cache Hit**: No API call, instant response (0ms)
**Cache Miss**: API call + cache store (200-2000ms)

---

## Summary

Feature 010 uses the **Nominatim Reverse Geocoding API** directly from the frontend:

- ✅ **No new backend endpoints** (direct frontend → Nominatim calls)
- ✅ **No authentication required** (public API, free tier)
- ✅ **CORS-enabled** (browser calls allowed)
- ✅ **Rate limit compliant** (1 req/sec enforced client-side)
- ✅ **Privacy-friendly** (no user tracking, only coordinates sent)

**Future Consideration**: Add backend proxy if rate limiting or analytics needed.
