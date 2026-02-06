# API Reference - ContraVento

Complete API reference documentation for integrating with ContraVento.

**Audience**: Developers, API consumers, mobile app developers

**Migrated from**: `backend/docs/api/README.md` (Phase 2 consolidation)

---

## Quick Navigation

| I need to... | Go to |
|--------------|-------|
| Authenticate users | [authentication.md](authentication.md) |
| Manage trips | [endpoints/trips.md](endpoints/trips.md) |
| Handle user profiles | [endpoints/users.md](endpoints/users.md) |
| Build social features | [endpoints/social.md](endpoints/social.md) |
| Work with GPS routes | [endpoints/gpx.md](endpoints/gpx.md) |
| Test the API manually | [testing/manual-testing.md](testing/manual-testing.md) |
| Use Postman | [testing/postman-guide.md](testing/postman-guide.md) |

---

## Base URLs

| Environment | Base URL | Use When |
|-------------|----------|----------|
| **Local Development** | `http://localhost:8000` | Daily development |
| **Docker Local** | `http://localhost:8000` | Docker testing |
| **Development/Integration** | `http://dev.contravento.com` | Team integration |
| **Staging** | `https://staging.contravento.com` | Pre-production testing |
| **Production** | `https://api.contravento.com` | Live application |

---

## Quick Start

### 1. Authentication

```bash
# Login and get access token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Response
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

### 2. Make Authenticated Requests

```bash
# Use access token in Authorization header
curl -X GET "http://localhost:8000/trips" \
  -H "Authorization: Bearer {access_token}"
```

See [Authentication Guide](authentication.md) for complete JWT flow.

---

## Documentation

### Core Concepts

- **[Authentication](authentication.md)** - JWT token flow, refresh, logout, security best practices

### Endpoint Reference

- **[Auth Endpoints](endpoints/auth.md)** - Register, login, refresh, logout, email verification
- **[Trips Endpoints](endpoints/trips.md)** - CRUD trips, photos, tags, filtering, publishing
- **[Users Endpoints](endpoints/users.md)** - Profiles, stats, photo upload
- **[Social Endpoints](endpoints/social.md)** - Follow, comments, likes, public feed
- **[GPX Endpoints](endpoints/gpx.md)** - GPS routes, trackpoints, POIs, elevation data

### Testing & Integration

- **[Manual Testing](testing/manual-testing.md)** - curl command reference with complete examples
- **[Postman Guide](testing/postman-guide.md)** - Postman/Insomnia setup and workflow
- **[OpenAPI Contracts](contracts/)** - YAML schema definitions for all endpoints

---

## Features Documented

### Travel Diary - Trip Management (v0.4.0)

**Trip CRUD Endpoints:**
- `POST /trips` - Create trip (draft by default)
- `GET /trips/{trip_id}` - Get trip details
- `PUT /trips/{trip_id}` - Edit trip (owner only, optimistic locking)
- `DELETE /trips/{trip_id}` - Delete trip and cascading data
- `POST /trips/{trip_id}/publish` - Publish trip (makes visible to all)

**Photo Management Endpoints:**
- `POST /trips/{trip_id}/photos` - Upload photo (max 20 per trip, 10MB each)
- `DELETE /trips/{trip_id}/photos/{photo_id}` - Delete photo
- `PUT /trips/{trip_id}/photos/reorder` - Reorder photos

**Tags & Filtering Endpoints:**
- `GET /users/{username}/trips` - List trips with filters (tag, status, pagination)
- `GET /tags` - Get all tags (ordered by popularity)

**Characteristics:**
- Upload: Max 20 photos/trip, max 10MB/photo, formats JPG/PNG/WebP
- Processing: Resize to 1200px, thumbnail 400x400px
- Reordering: Automatic gap fill on deletion
- Validation: Owner-only operations
- Tags: Case-insensitive matching, many-to-many relationships
- Filtering: Tag + status combination, pagination (limit/offset)

**Functional Requirements:**
- FR-001, FR-002, FR-003: Trip creation
- FR-007, FR-008: Trip publication and visibility
- FR-009, FR-010, FR-011: Photo upload and processing
- FR-012: Photo reordering
- FR-013: Photo deletion
- FR-016, FR-020: Trip editing with optimistic locking
- FR-017, FR-018: Trip deletion with stats update
- FR-025: User trip listing with tag/status filtering
- FR-027: Tag browsing and popularity ranking

---

## OpenAPI Contracts

OpenAPI 3.0 specifications for all endpoints:

| Contract | Endpoints | Location |
|----------|-----------|----------|
| **auth.yaml** | Authentication | [contracts/auth.yaml](contracts/auth.yaml) |
| **trips.yaml** | Trip CRUD, photos, tags | [contracts/trips.yaml](contracts/trips.yaml) |
| **gpx-api.yaml** | GPX upload, trackpoints | [contracts/gpx-api.yaml](contracts/gpx-api.yaml) |
| **gpx-wizard.yaml** | GPX wizard workflow | [contracts/gpx-wizard.yaml](contracts/gpx-wizard.yaml) |
| **social.yaml** | Follow, user relationships | [contracts/social.yaml](contracts/social.yaml) |
| **social-network.yaml** | Comments, likes | [contracts/social-network.yaml](contracts/social-network.yaml) |
| **public-feed-api.yaml** | Public trips feed | [contracts/public-feed-api.yaml](contracts/public-feed-api.yaml) |
| **profile.yaml** | User profiles | [contracts/profile.yaml](contracts/profile.yaml) |
| **stats.yaml** | User statistics | [contracts/stats.yaml](contracts/stats.yaml) |

**All contracts migrated from**: `specs/*/contracts/*.yaml`

---

## Response Format

All API responses follow a standardized JSON format:

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "error": null
}
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensaje descriptivo en español",
    "field": "email"  // Optional: field that caused error
  }
}
```

---

## Error Codes

| HTTP Status | Error Code | Common Causes |
|-------------|------------|---------------|
| 400 | `VALIDATION_ERROR` | Invalid input, missing required field, weak password |
| 401 | `UNAUTHORIZED` | Invalid or expired token, wrong credentials |
| 403 | `FORBIDDEN` | Insufficient permissions, account not verified |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Duplicate resource, optimistic locking conflict |
| 422 | `UNPROCESSABLE_ENTITY` | Invalid request body structure |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests (login rate limit) |
| 500 | `INTERNAL_SERVER_ERROR` | Server error |

See [Authentication Guide](authentication.md#error-handling) for detailed error handling.

---

## Rate Limiting

| Endpoint | Limit | Window | Penalty |
|----------|-------|--------|---------|
| **Login** | 5 attempts | Per email | 15 min lockout |
| **Register** | 3 attempts | Per IP | 1 hour lockout |
| **General API** | 1000 requests | Per hour | 429 error |

---

## Postman Collections

Pre-configured collections for testing:

| Collection | Description | Location |
|------------|-------------|----------|
| **GPS Coordinates** | GPS trip creation, GPX upload, location management | [postman/collections/ContraVento_GPS_Coordinates.postman_collection.json](postman/collections/ContraVento_GPS_Coordinates.postman_collection.json) |
| **Environment (Local)** | Local development variables (base_url, tokens) | [postman/environments/ContraVento-Local.postman_environment.json](postman/environments/ContraVento-Local.postman_environment.json) |

**Auto-Update Scripts Included**:
- Login → Save access_token
- Create Trip → Save trip_id
- Upload Photo → Save photo1_id, photo2_id, photo3_id

See [Postman Guide](testing/postman-guide.md) for import instructions and workflow.

---

## API Documentation (Interactive)

When the backend server is running, access interactive API docs:

- **Swagger UI**: `http://localhost:8000/docs` (full OpenAPI interface)
- **ReDoc**: `http://localhost:8000/redoc` (alternative documentation viewer)

**Benefits**:
- Try endpoints directly from browser
- See request/response schemas
- Auto-generated from OpenAPI contracts
- Real-time validation

---

## Migration from Old Documentation

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `backend/docs/api/README.md` | `docs/api/README.md` (this file) | ✅ Migrated (Phase 2) |
| `backend/docs/api/MANUAL_TESTING.md` | `docs/api/testing/manual-testing.md` | ✅ Migrated (Phase 2) |
| `backend/docs/api/POSTMAN_COLLECTION.md` | `docs/api/testing/postman-guide.md` | ✅ Migrated (Phase 2) |
| `backend/docs/api/TAGS_TESTING.md` | `docs/api/testing/manual-testing.md` (consolidated) | ⏳ Pending |
| `backend/docs/api/USER_PROFILES_MANUAL.md` | `docs/api/endpoints/users.md` (consolidated) | ⏳ Pending |
| `backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md` | `docs/api/endpoints/gpx.md` (consolidated) | ⏳ Pending |
| `specs/001-user-profiles/contracts/*.yaml` | `docs/api/contracts/` | ✅ Migrated (Phase 2) |
| `specs/002-travel-diary/contracts/trips-api.yaml` | `docs/api/contracts/trips.yaml` | ✅ Migrated (Phase 2) |
| `specs/003-gps-routes/contracts/gpx-api.yaml` | `docs/api/contracts/gpx-api.yaml` | ✅ Migrated (Phase 2) |
| `specs/004-social-network/contracts/social-api.yaml` | `docs/api/contracts/social-network.yaml` | ✅ Migrated (Phase 2) |
| `specs/013-public-trips-feed/contracts/public-feed-api.yaml` | `docs/api/contracts/public-feed-api.yaml` | ✅ Migrated (Phase 2) |
| `specs/017-gps-trip-wizard/contracts/gpx-wizard.yaml` | `docs/api/contracts/gpx-wizard.yaml` | ✅ Migrated (Phase 2) |
| `backend/docs/api/*.postman_collection.json` | `docs/api/postman/collections/` | ✅ Migrated (Phase 2) |
| `backend/docs/api/*.postman_environment.json` | `docs/api/postman/environments/` | ✅ Migrated (Phase 2) |

**Note**: Additional backend/docs/api/ testing guides will be consolidated in future iterations.

---

## Related Documentation

- **[Deployment](../deployment/README.md)** - Running API in different environments
- **[User Guides](../user-guides/README.md)** - End-user feature documentation
- **[Architecture](../architecture/README.md)** - Technical design and patterns
- **[Testing](../testing/README.md)** - Testing strategies and test pyramid
- **[Features](../features/README.md)** - Feature-specific documentation

---

**Last Updated**: 2026-02-06
**Consolidation Plan**: Phase 2 (API Documentation) - ✅ Complete
**API Version**: 1.0.0 (Travel Diary 0.4.0 - Tags & Categorization)
