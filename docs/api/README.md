# API Reference - ContraVento

Complete API reference documentation for the ContraVento cycling social platform.

**Audience**: Frontend developers, mobile app developers, API consumers

**Base URL**: `http://localhost:8000` (development) | `https://api.contravento.com` (production)

---

## Quick Start

```bash
# Health check
curl http://localhost:8000/health

# Get API documentation (OpenAPI/Swagger)
open http://localhost:8000/docs

# Authenticate
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123!"}'
```

---

## Table of Contents

1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
3. [OpenAPI Contracts](#openapi-contracts)
4. [Testing](#testing)
5. [Postman Collections](#postman-collections)

---

## Authentication

ContraVento uses **JWT (JSON Web Tokens)** for authentication with access and refresh tokens.

📘 **[Complete Authentication Guide](authentication.md)**

### Quick Reference

**Login**:
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Use Access Token**:
```http
GET /trips
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Token Expiration**:
- Access Token: 15 minutes
- Refresh Token: 30 days

---

## API Endpoints

### Core Endpoints

| Category | Endpoint Documentation | Key Features |
|----------|----------------------|--------------|
| **Authentication** | [auth.md](endpoints/auth.md) | Login, register, refresh tokens, email verification |
| **Trips** | [trips.md](endpoints/trips.md) | Create, read, update, delete trips; photo upload |
| **Users** | [users.md](endpoints/users.md) | Profiles, stats, achievements, cycling types |
| **Social** | [social.md](endpoints/social.md) | Follow/unfollow, comments, likes, public feed |
| **GPX** | [gpx.md](endpoints/gpx.md) | GPX upload, parsing, route visualization, elevation |

### Endpoint Documentation Status

| Endpoint | Status | OpenAPI Contract | Last Updated |
|----------|--------|------------------|--------------|
| [auth.md](endpoints/auth.md) | ⏳ Planned | ✅ Available | - |
| [trips.md](endpoints/trips.md) | ⏳ Planned | ✅ Available | - |
| [users.md](endpoints/users.md) | ⏳ Planned | ✅ Available | - |
| [social.md](endpoints/social.md) | ⏳ Planned | ✅ Available | - |
| [gpx.md](endpoints/gpx.md) | ⏳ Planned | ⏳ In Progress | - |

**Note**: Endpoint documentation will be created in **Phase 2** (API Documentation) of the consolidation plan.

---

## OpenAPI Contracts

OpenAPI 3.0 specifications for all API endpoints.

### Available Contracts

```
contracts/
├── auth-api.yaml           # Authentication endpoints
├── trips-api.yaml          # Trip CRUD operations
├── users-api.yaml          # User profiles and stats
├── social-api.yaml         # Social features (follow, comments)
└── gpx-api.yaml           # GPX upload and processing
```

### Using Contracts

**View in Swagger UI**:
```bash
# Start development server
./run-local-dev.sh

# Open interactive docs
open http://localhost:8000/docs
```

**Validate Requests** (Contract Testing):
```bash
cd backend
poetry run pytest tests/contract/ -v
```

**Generate Client SDK**:
```bash
# From OpenAPI contract
openapi-generator-cli generate \
  -i docs/api/contracts/trips-api.yaml \
  -g typescript-axios \
  -o frontend/src/generated/api
```

**Related Documentation**:
- [Contract Testing Guide](../testing/backend/contract-tests.md)

---

## Testing

### Manual Testing

📘 **[Manual API Testing Guide](testing/manual-testing.md)**

Quick test with curl:
```bash
# Create trip
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Trip",
    "description": "A test trip for API validation",
    "start_date": "2026-02-01",
    "distance_km": 50.5
  }'
```

### Postman/Insomnia

📘 **[Postman Setup Guide](testing/postman-guide.md)**

**Collections Available**:
- `postman/collections/ContraVento_Auth.postman_collection.json`
- `postman/collections/ContraVento_Trips.postman_collection.json`
- `postman/collections/ContraVento_Social.postman_collection.json`

**Environments**:
- `postman/environments/Local_Development.postman_environment.json`
- `postman/environments/Staging.postman_environment.json`

---

## Postman Collections

Pre-built Postman collections for all API endpoints.

### Quick Setup

1. **Import Collections**:
   - Open Postman
   - Import → File → `docs/api/postman/collections/*.json`

2. **Import Environment**:
   - Import → File → `docs/api/postman/environments/Local_Development.postman_environment.json`

3. **Authenticate**:
   - Run "Auth → Login" request
   - Access token auto-saved to environment

4. **Test Endpoints**:
   - All authenticated requests use `{{access_token}}` variable

### Collection Status

| Collection | Status | Endpoints | Last Updated |
|------------|--------|-----------|--------------|
| ContraVento_Auth | ⏳ To be migrated | Login, Register, Refresh, Verify | - |
| ContraVento_Trips | ⏳ To be migrated | CRUD trips, Photos, Tags | - |
| ContraVento_Users | ⏳ To be migrated | Profiles, Stats, Achievements | - |
| ContraVento_Social | ⏳ To be migrated | Follow, Comments, Likes | - |
| ContraVento_GPX | ⏳ To be migrated | Upload, Parse, Routes | - |

**Note**: Postman collections will be migrated from `backend/docs/api/` in **Phase 2** (API Documentation).

---

## API Design Principles

ContraVento API follows these design principles:

1. **RESTful**: Resource-based URLs, standard HTTP methods
2. **JSON**: All requests and responses use JSON
3. **Versioned**: API version in URL path (future: `/api/v2/`)
4. **Paginated**: List endpoints support `limit` and `offset` parameters
5. **Validated**: Pydantic schemas validate all inputs
6. **Documented**: OpenAPI/Swagger documentation auto-generated
7. **Tested**: Contract tests validate OpenAPI compliance

---

## Response Format

All API responses follow a standardized format:

**Success Response**:
```json
{
  "success": true,
  "data": {
    "trip_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "My Trip",
    ...
  },
  "error": null
}
```

**Error Response**:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El email ya está registrado",
    "field": "email"
  }
}
```

---

## Rate Limiting

**Development**: No rate limits

**Production**:
- **Authentication**: 5 login attempts per 15 minutes
- **General API**: 1000 requests per hour per IP
- **File Upload**: 10 uploads per hour per user

---

## Error Codes

| HTTP Status | Error Code | Meaning |
|-------------|------------|---------|
| 400 | VALIDATION_ERROR | Invalid request data |
| 401 | UNAUTHORIZED | Missing or invalid authentication |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict (e.g., duplicate email) |
| 422 | UNPROCESSABLE_ENTITY | Semantic validation error |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_SERVER_ERROR | Server error |

---

## Migration from Old Documentation

This consolidated API reference replaces:

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `backend/docs/api/README.md` | `docs/api/README.md` | ⏳ To be migrated |
| `backend/docs/api/MANUAL_TESTING.md` | `docs/api/testing/manual-testing.md` | ⏳ To be migrated |
| `backend/docs/api/POSTMAN_COLLECTION.md` | `docs/api/testing/postman-guide.md` | ⏳ To be migrated |
| `specs/*/contracts/*.yaml` | `docs/api/contracts/` | ⏳ To be migrated |

Migration will occur in **Phase 2** (Week 2) of the documentation consolidation plan.

---

## Related Documentation

- **[User Guides](../user-guides/README.md)** - How to use ContraVento features
- **[Architecture](../architecture/README.md)** - Technical architecture and design
- **[Testing](../testing/README.md)** - Testing strategies and guides
- **[Development](../development/README.md)** - Developer workflows

---

## Contributing

Found an issue or want to improve API documentation? See [Documentation Contributing Guide](../CONTRIBUTING.md) (to be created in Phase 8).

---

**Last Updated**: 2026-02-06
**Consolidation Plan**: Phase 1 (Foundation) - Directory structure
**API Version**: v1
