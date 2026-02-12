# GPX Routes Endpoints

API endpoints for GPS route management and GPX file processing.

**OpenAPI Contracts**:
- [gpx-api.yaml](../contracts/gpx-api.yaml)
- [gpx-wizard.yaml](../contracts/gpx-wizard.yaml)

---

## Table of Contents

- [POST /trips/{trip_id}/gpx](#post-tripstrip_idgpx)
- [GET /trips/{trip_id}/gpx](#get-tripstrip_idgpx)
- [DELETE /trips/{trip_id}/gpx](#delete-tripstrip_idgpx)
- [GET /trips/{trip_id}/gpx/trackpoints](#get-tripstrip_idgpxtrackpoints)
- [POST /trips/{trip_id}/pois](#post-tripstrip_idpois)
- [PUT /trips/{trip_id}/pois/{poi_id}](#put-tripstrip_idpoispoi_id)
- [DELETE /trips/{trip_id}/pois/{poi_id}](#delete-tripstrip_idpoispoi_id)

---

## POST /trips/{trip_id}/gpx

Upload GPX file to trip.

**Authentication**: Required (Bearer token, must be trip owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Request Body** (multipart/form-data):
- `gpx_file` (file): GPX file (.gpx)

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "gpx_file_id": "abc123-456def-789ghi",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "ruta_via_verde.gpx",
    "total_distance_km": 127.34,
    "total_ascent_m": 450.0,
    "total_descent_m": 480.0,
    "max_elevation_m": 850.0,
    "min_elevation_m": 320.0,
    "has_elevation": true,
    "trackpoint_count": 3542,
    "start_time": "2024-05-15T08:30:00Z",
    "end_time": "2024-05-15T16:45:00Z",
    "created_at": "2024-06-01T10:00:00Z"
  },
  "error": null
}
```

**Validation**:
- Max 10MB file size
- Must be valid GPX format (XML)
- Must contain at least one track with trackpoints

**Processing**:
- Extract metadata (distance, elevation, timestamps)
- Simplify trackpoints (Douglas-Peucker algorithm, ~200-500 points)
- Calculate gradients between points
- Detect start/end locations via reverse geocoding
- Store original file in storage

**Auto-Updates**:
- Trip `distance_km` updated from GPX data
- Trip start/end locations created if missing

**Errors**:
- `400` - Invalid GPX file (malformed XML, no tracks)
- `401` - Unauthorized
- `403` - Forbidden (not trip owner)
- `404` - Trip not found
- `409` - Trip already has GPX file (delete first)

---

## GET /trips/{trip_id}/gpx

Get GPX metadata for a trip.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "gpx_file_id": "abc123-456def-789ghi",
    "filename": "ruta_via_verde.gpx",
    "total_distance_km": 127.34,
    "total_ascent_m": 450.0,
    "total_descent_m": 480.0,
    "max_elevation_m": 850.0,
    "min_elevation_m": 320.0,
    "has_elevation": true,
    "trackpoint_count": 3542,
    "start_time": "2024-05-15T08:30:00Z",
    "end_time": "2024-05-15T16:45:00Z",
    "created_at": "2024-06-01T10:00:00Z"
  },
  "error": null
}
```

**Visibility**:
- Published trips: Visible to all
- Draft trips: Only visible to owner

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (draft trip, not owner)
- `404` - Trip not found or no GPX file

---

## DELETE /trips/{trip_id}/gpx

Delete GPX file from trip.

**Authentication**: Required (Bearer token, must be trip owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "Archivo GPX eliminado correctamente"
  },
  "error": null
}
```

**Cascading Deletes**:
- GPX file deleted from storage
- All trackpoints deleted
- Trip distance NOT reset (preserved)

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (not trip owner)
- `404` - Trip not found or no GPX file

---

## GET /trips/{trip_id}/gpx/trackpoints

Get simplified trackpoints for map visualization and elevation profile.

**Authentication**: Required (Bearer token)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "trackpoints": [
      {
        "latitude": 37.7749,
        "longitude": -3.7899,
        "elevation": 450.5,
        "distance_km": 0.0,
        "gradient": 0.0,
        "timestamp": "2024-05-15T08:30:00Z"
      },
      {
        "latitude": 37.7755,
        "longitude": -3.7905,
        "elevation": 455.0,
        "distance_km": 0.85,
        "gradient": 5.2,
        "timestamp": "2024-05-15T08:35:00Z"
      }
    ],
    "total_points": 342
  },
  "error": null
}
```

**Trackpoint Fields**:
- `latitude`, `longitude`: GPS coordinates
- `elevation`: Meters above sea level (null if not available)
- `distance_km`: Cumulative distance from start
- `gradient`: Percentage slope to next point (positive = uphill, negative = downhill)
- `timestamp`: ISO 8601 timestamp (null if not available)

**Simplification**:
- Original GPX: ~3000-5000 points
- Simplified: ~200-500 points (Douglas-Peucker)
- Preserves route shape while reducing data transfer

**Visibility**:
- Published trips: Visible to all
- Draft trips: Only visible to owner

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (draft trip, not owner)
- `404` - Trip not found or no GPX file

---

## POST /trips/{trip_id}/pois

Add Point of Interest (POI) to trip.

**Authentication**: Required (Bearer token, must be trip owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier

**Request Body**:
```json
{
  "name": "Mirador del Valle",
  "description": "Vista espectacular del valle. Parada obligatoria para fotos.",
  "latitude": 37.7750,
  "longitude": -3.7900,
  "poi_type": "viewpoint"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "poi_id": "def456-789ghi-012jkl",
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Mirador del Valle",
    "description": "Vista espectacular del valle. Parada obligatoria para fotos.",
    "latitude": 37.7750,
    "longitude": -3.7900,
    "poi_type": "viewpoint",
    "created_at": "2024-06-01T11:00:00Z"
  },
  "error": null
}
```

**POI Types**:
- `viewpoint`: Mirador, scenic viewpoint
- `water`: Fuente, water source
- `food`: Restaurante, bar, tienda
- `accommodation`: Hotel, refugio, camping
- `danger`: Peligro, road hazard
- `photo`: Photo spot
- `rest`: Área de descanso
- `other`: Otro

**Validation**:
- Name: Required, max 200 chars
- Description: Optional, max 1000 chars
- Latitude: -90 to 90
- Longitude: -180 to 180

**Errors**:
- `400` - Validation error
- `401` - Unauthorized
- `403` - Forbidden (not trip owner)
- `404` - Trip not found

---

## PUT /trips/{trip_id}/pois/{poi_id}

Update POI details.

**Authentication**: Required (Bearer token, must be trip owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier
- `poi_id` (UUID): POI identifier

**Request Body** (partial updates supported):
```json
{
  "name": "Mirador del Valle - Actualizado",
  "description": "Nueva descripción con más detalles"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "poi_id": "def456-789ghi-012jkl",
    "name": "Mirador del Valle - Actualizado",
    "description": "Nueva descripción con más detalles",
    ...
  },
  "error": null
}
```

**Errors**:
- `400` - Validation error
- `401` - Unauthorized
- `403` - Forbidden (not trip owner)
- `404` - POI not found

---

## DELETE /trips/{trip_id}/pois/{poi_id}

Delete POI from trip.

**Authentication**: Required (Bearer token, must be trip owner)

**Path Parameters**:
- `trip_id` (UUID): Trip identifier
- `poi_id` (UUID): POI identifier

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "message": "POI eliminado correctamente"
  },
  "error": null
}
```

**Errors**:
- `401` - Unauthorized
- `403` - Forbidden (not trip owner)
- `404` - POI not found

---

## Related Documentation

- **[OpenAPI Contracts](../contracts/)** - gpx-api.yaml, gpx-wizard.yaml
- **[User Guide: GPS Routes](../../user-guides/maps/gps-routes.md)** - End-user guide
- **[User Guide: Uploading GPX](../../user-guides/trips/uploading-gpx.md)** - GPX upload guide
- **[Feature: GPS Routes](../../features/gps-routes.md)** - Feature overview
- **[Feature: Elevation Profile](../../features/elevation-profile.md)** - Elevation chart
- **[Manual Testing](../testing/manual-testing.md)** - curl examples

---

**Last Updated**: 2026-02-06
**API Version**: 1.0.0
**GPX Processing**: Douglas-Peucker simplification, gradient calculation
