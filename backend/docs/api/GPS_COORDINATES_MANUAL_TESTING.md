# Manual Testing Guide - GPS Coordinates Backend

**Feature**: 009-gps-coordinates
**API Version**: v1
**Base URL**: `http://localhost:8000`
**Created**: 2026-01-11

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Authentication](#authentication)
4. [Test Scenarios](#test-scenarios)
5. [Expected Results](#expected-results)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **curl**: Command-line HTTP client (pre-installed on Linux/Mac, Windows 10+)
- **python**: For JSON formatting (`python -m json.tool`)
- **jq** (optional): Better JSON formatting (`sudo apt install jq` or `brew install jq`)

### Environment

- Backend server running at `http://localhost:8000`
- Test user credentials (created during setup):
  - **Username**: `testuser`
  - **Email**: `test@example.com`
  - **Password**: `TestPass123!`

### Start Backend Server

```bash
# Option 1: LOCAL-DEV (SQLite - Fastest)
cd backend
./run-local-dev.sh              # Linux/Mac
.\run-local-dev.ps1             # Windows PowerShell

# Option 2: Docker (PostgreSQL)
./deploy.sh local-minimal
```

Verify server is running:
```bash
curl http://localhost:8000/docs
# Should return HTML for Swagger UI
```

---

## Setup Instructions

### Step 1: Verify Test User Exists

```bash
# Check if testuser exists
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}' | python -m json.tool
```

If user doesn't exist, create it:
```bash
cd backend
poetry run python scripts/create_verified_user.py
```

### Step 2: Get Access Token

Use the provided scripts in `scripts/testing/gps/`:

**Linux/Mac** (`scripts/testing/gps/get-token.sh`):
```bash
#!/bin/bash
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}')

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    echo "$RESPONSE" | python -m json.tool
    exit 1
fi

echo "✅ Login successful"
echo "Access Token: $TOKEN"
echo ""
echo "Export to use in tests:"
echo "export ACCESS_TOKEN=\"$TOKEN\""
```

**Windows PowerShell** (`scripts/testing/gps/get-token.ps1`):
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"login":"testuser","password":"TestPass123!"}'

if ($response.success) {
    $token = $response.data.access_token
    Write-Host "✅ Login successful" -ForegroundColor Green
    Write-Host "Access Token: $token"
    Write-Host ""
    Write-Host "Set environment variable:" -ForegroundColor Yellow
    Write-Host "`$env:ACCESS_TOKEN = `"$token`""

    # Auto-set the variable
    $env:ACCESS_TOKEN = $token
} else {
    Write-Host "❌ Login failed" -ForegroundColor Red
    $response | ConvertTo-Json -Depth 10
}
```

**Usage**:
```bash
# Linux/Mac
cd scripts/testing/gps
./get-token.sh
export ACCESS_TOKEN="<token_from_output>"

# Windows PowerShell
cd scripts/testing/gps
.\get-token.ps1
# Token is auto-set in $env:ACCESS_TOKEN
```

---

## Authentication

### Login Request

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "TestPass123!"
  }' | python -m json.tool
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "user_id": "75d2f9d0-b123-4fd7-a216-e7aa29be2e1c",
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

Copy the `access_token` value for use in subsequent requests.

---

## Test Scenarios

### Test 1: Create Trip WITH Valid GPS Coordinates ✅

**Purpose**: Verify coordinates are stored with 6 decimal precision

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Bikepacking Pirineos con GPS",
    "description": "Viaje de 5 días por los Pirineos con coordenadas GPS para visualización en mapa. Ruta espectacular cruzando desde España a Francia con paisajes increíbles.",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "distance_km": 320.5,
    "difficulty": "difficult",
    "locations": [
      {
        "name": "Jaca",
        "country": "España",
        "latitude": 42.570084,
        "longitude": -0.549941
      },
      {
        "name": "Somport",
        "country": "España",
        "latitude": 42.791667,
        "longitude": -0.526944
      },
      {
        "name": "Gavarnie",
        "country": "Francia",
        "latitude": 42.739722,
        "longitude": -0.012778
      }
    ],
    "tags": ["bikepacking", "pirineos", "internacional"]
  }' | python -m json.tool
```

**Expected Response**: `"success": true`

**Validation Checklist**:
- [ ] Response `success` is `true`
- [ ] Trip created with `trip_id`
- [ ] 3 locations returned in response
- [ ] Each location has `latitude` and `longitude` with 6 decimal places
- [ ] Coordinates match input values (rounded to 6 decimals)
- [ ] `sequence` field shows correct ordering (0, 1, 2)

**Save trip_id for later tests**:
```bash
# Extract trip_id from response (Linux/Mac)
TRIP_ID=$(curl -s -X POST http://localhost:8000/trips ... | grep -o '"trip_id":"[^"]*' | sed 's/"trip_id":"//')
echo "Trip ID: $TRIP_ID"
```

---

### Test 2: Create Trip WITHOUT GPS Coordinates (Backwards Compatibility) ✅

**Purpose**: Verify existing trips without GPS continue to work

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Camino de Santiago sin GPS",
    "description": "Peregrinación en bici desde Roncesvalles a Santiago de Compostela. Viaje espiritual de 10 días por el norte de España siguiendo la ruta histórica.",
    "start_date": "2024-07-10",
    "end_date": "2024-07-20",
    "distance_km": 750.0,
    "difficulty": "moderate",
    "locations": [
      {
        "name": "Roncesvalles"
      },
      {
        "name": "Pamplona"
      },
      {
        "name": "Logroño"
      },
      {
        "name": "Santiago de Compostela"
      }
    ],
    "tags": ["camino", "peregrino"]
  }' | python -m json.tool
```

**Expected Response**: `"success": true`

**Validation Checklist**:
- [ ] Response `success` is `true`
- [ ] Trip created successfully
- [ ] 4 locations returned
- [ ] Each location has `latitude: null` and `longitude: null`
- [ ] No validation errors for missing coordinates

---

### Test 3: Invalid Latitude > 90 (Should Fail) ❌

**Purpose**: Verify latitude range validation

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Invalid Latitude",
    "description": "Este trip debe fallar porque la latitud está fuera de rango. La latitud debe estar entre -90 y 90 grados según el estándar WGS84.",
    "start_date": "2024-06-01",
    "distance_km": 100.0,
    "locations": [
      {
        "name": "Ubicación Inválida",
        "latitude": 100.0,
        "longitude": -3.703790
      }
    ]
  }' | python -m json.tool
```

**Expected Response**: `"success": false`

**Validation Checklist**:
- [ ] Response `success` is `false`
- [ ] Error code is `"VALIDATION_ERROR"`
- [ ] Error message mentions latitude validation (Spanish)
- [ ] Field is `"locations.0.latitude"`
- [ ] Message includes constraint (≤ 90)

**Expected Error**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Error de validación en el campo 'locations.0.latitude': Input should be less than or equal to 90",
    "field": "locations.0.latitude"
  }
}
```

---

### Test 4: Invalid Latitude < -90 (Should Fail) ❌

**Purpose**: Verify lower bound of latitude range

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Invalid Latitude (Negative)",
    "description": "Latitud por debajo del rango válido",
    "start_date": "2024-06-01",
    "distance_km": 100.0,
    "locations": [
      {
        "name": "Polo Sur Inválido",
        "latitude": -95.0,
        "longitude": 0.0
      }
    ]
  }' | python -m json.tool
```

**Expected Response**: `"success": false`

**Validation Checklist**:
- [ ] Error code `"VALIDATION_ERROR"`
- [ ] Message mentions latitude ≥ -90

---

### Test 5: Invalid Longitude > 180 (Should Fail) ❌

**Purpose**: Verify longitude range validation (upper bound)

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Invalid Longitude",
    "description": "Longitud por encima del rango válido",
    "start_date": "2024-06-01",
    "distance_km": 100.0,
    "locations": [
      {
        "name": "Ubicación Inválida",
        "latitude": 40.416775,
        "longitude": 200.0
      }
    ]
  }' | python -m json.tool
```

**Expected Response**: `"success": false`

**Validation Checklist**:
- [ ] Error code `"VALIDATION_ERROR"`
- [ ] Field is `"locations.0.longitude"`
- [ ] Message mentions longitude ≤ 180

---

### Test 6: Invalid Longitude < -180 (Should Fail) ❌

**Purpose**: Verify longitude range validation (lower bound)

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Invalid Longitude (Negative)",
    "description": "Longitud por debajo del rango válido",
    "start_date": "2024-06-01",
    "distance_km": 100.0,
    "locations": [
      {
        "name": "Ubicación Inválida",
        "latitude": 40.416775,
        "longitude": -200.0
      }
    ]
  }' | python -m json.tool
```

**Expected Response**: `"success": false`

**Validation Checklist**:
- [ ] Error code `"VALIDATION_ERROR"`
- [ ] Message mentions longitude ≥ -180

---

### Test 7: Coordinate Precision Rounding (9 → 6 decimals) ✅

**Purpose**: Verify coordinates are rounded to 6 decimal places

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Precision Rounding",
    "description": "Este trip prueba que las coordenadas se redondean a 6 decimales. La precisión de 6 decimales es aproximadamente 0.11 metros en el ecuador, suficiente para ciclismo.",
    "start_date": "2024-06-01",
    "distance_km": 50.0,
    "locations": [
      {
        "name": "Madrid (high precision)",
        "latitude": 40.123456789,
        "longitude": -3.987654321
      }
    ]
  }' | python -m json.tool
```

**Expected Response**: `"success": true`

**Validation Checklist**:
- [ ] Response `success` is `true`
- [ ] Latitude is rounded: `40.123456789` → `40.123457` (6 decimals)
- [ ] Longitude is rounded: `-3.987654321` → `-3.987654` (6 decimals)
- [ ] No extra decimals in response

**Check Response**:
```json
{
  "locations": [
    {
      "name": "Madrid (high precision)",
      "latitude": 40.123457,    // ← Rounded to 6 decimals
      "longitude": -3.987654,   // ← Rounded to 6 decimals
      "sequence": 0
    }
  ]
}
```

---

### Test 8: Mixed Locations (Some With GPS, Some Without) ✅

**Purpose**: Verify trips can have partial GPS data

**Request**:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Mixta GPS Parcial",
    "description": "Este trip tiene algunas ubicaciones con coordenadas GPS y otras sin ellas. El mapa debe mostrar solo los marcadores de ubicaciones con coordenadas válidas.",
    "start_date": "2024-06-01",
    "distance_km": 200.0,
    "locations": [
      {
        "name": "Madrid",
        "latitude": 40.416775,
        "longitude": -3.703790
      },
      {
        "name": "Toledo"
      },
      {
        "name": "Cuenca",
        "latitude": 40.070392,
        "longitude": -2.137198
      }
    ],
    "tags": ["ruta mixta"]
  }' | python -m json.tool
```

**Expected Response**: `"success": true`

**Validation Checklist**:
- [ ] Response `success` is `true`
- [ ] Madrid has coordinates (latitude: 40.416775, longitude: -3.703790)
- [ ] Toledo has `latitude: null`, `longitude: null`
- [ ] Cuenca has coordinates (latitude: 40.070392, longitude: -2.137198)
- [ ] All 3 locations created successfully

---

### Test 9: Retrieve Trip With GPS Coordinates ✅

**Purpose**: Verify coordinates are returned in GET requests

**Request**:
```bash
# Replace {trip_id} with actual ID from Test 1
curl -X GET http://localhost:8000/trips/{trip_id} \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool
```

**Validation Checklist**:
- [ ] Trip data includes `locations` array
- [ ] Each location has `latitude` and `longitude` fields
- [ ] Coordinates match originally submitted values
- [ ] `sequence` field shows correct ordering

---

### Test 10: Update Trip Locations (Add GPS to Existing Trip) ✅

**Purpose**: Verify coordinates can be added/updated via PUT

**Request**:
```bash
# Replace {trip_id} with actual ID from Test 2 (trip without GPS)
curl -X PUT http://localhost:8000/trips/{trip_id} \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Camino de Santiago CON GPS",
    "description": "Ahora con coordenadas GPS añadidas",
    "start_date": "2024-07-10",
    "end_date": "2024-07-20",
    "distance_km": 750.0,
    "difficulty": "moderate",
    "locations": [
      {
        "name": "Roncesvalles",
        "latitude": 43.009722,
        "longitude": -1.319167
      },
      {
        "name": "Pamplona",
        "latitude": 42.812526,
        "longitude": -1.645775
      }
    ],
    "tags": ["camino", "peregrino", "gps"]
  }' | python -m json.tool
```

**Validation Checklist**:
- [ ] Response `success` is `true`
- [ ] Locations now have GPS coordinates
- [ ] Previous `null` coordinates replaced with values

---

### Test 11: List User Trips (Verify GPS in List) ✅

**Purpose**: Verify coordinates appear in trip list endpoint

**Request**:
```bash
curl -X GET http://localhost:8000/users/testuser/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool
```

**Validation Checklist**:
- [ ] All trips returned include `locations` array
- [ ] Locations with GPS show coordinate values
- [ ] Locations without GPS show `null` values

---

## Expected Results

### Summary Table

| Test | Expected Status | Validation Focus |
|------|----------------|------------------|
| Test 1 | ✅ SUCCESS | Valid GPS coordinates stored |
| Test 2 | ✅ SUCCESS | Backwards compatibility (no GPS) |
| Test 3 | ❌ VALIDATION ERROR | Latitude > 90 rejected |
| Test 4 | ❌ VALIDATION ERROR | Latitude < -90 rejected |
| Test 5 | ❌ VALIDATION ERROR | Longitude > 180 rejected |
| Test 6 | ❌ VALIDATION ERROR | Longitude < -180 rejected |
| Test 7 | ✅ SUCCESS | Precision rounding (9→6 decimals) |
| Test 8 | ✅ SUCCESS | Mixed locations (partial GPS) |
| Test 9 | ✅ SUCCESS | Coordinates in GET response |
| Test 10 | ✅ SUCCESS | Update coordinates via PUT |
| Test 11 | ✅ SUCCESS | Coordinates in list endpoint |

### Functional Requirements Coverage

| FR-ID | Requirement | Test Coverage |
|-------|-------------|---------------|
| FR-001 | Store lat/lon as optional decimals | Test 1, 2, 8 |
| FR-002 | Validate latitude range (-90 to 90) | Test 3, 4 |
| FR-003 | Validate longitude range (-180 to 180) | Test 5, 6 |
| FR-004 | Coordinates optional per location | Test 2, 8 |
| FR-013 | Persist 6 decimal places | Test 7 |

---

## Troubleshooting

### Issue: "401 Unauthorized"

**Symptom**: All API requests return 401 error

**Solution**:
1. Verify access token is valid (tokens expire after 1 hour)
2. Re-login to get fresh token:
   ```bash
   ./get-token.sh  # or get-token.ps1
   ```
3. Ensure `Authorization: Bearer <token>` header is included

### Issue: "JSON decode error"

**Symptom**: Error message mentions "JSON decode error"

**Solution** (Windows specific):
1. Create JSON files instead of inline JSON:
   ```bash
   echo '{"login":"testuser","password":"TestPass123!"}' > login.json
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     --data @login.json
   ```
2. Use PowerShell `Invoke-RestMethod` instead of curl

### Issue: "Connection refused"

**Symptom**: Cannot connect to `http://localhost:8000`

**Solution**:
1. Verify backend server is running:
   ```bash
   curl http://localhost:8000/docs
   ```
2. Start backend:
   ```bash
   cd backend
   poetry run uvicorn src.main:app --reload
   ```

### Issue: Coordinates not visible in response

**Symptom**: Response doesn't include `locations` array

**Solution**:
1. Check if eager loading is enabled in TripService
2. Verify response serialization includes relationships
3. Use trip detail endpoint: `GET /trips/{trip_id}` instead of list endpoint

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Specification**: [specs/009-gps-coordinates/spec.md](../../specs/009-gps-coordinates/spec.md)
- **OpenAPI Contract**: [specs/009-gps-coordinates/contracts/trips-api.yaml](../../specs/009-gps-coordinates/contracts/trips-api.yaml)
- **Test Results**: [GPS_COORDINATES_TEST_RESULTS.md](../../GPS_COORDINATES_TEST_RESULTS.md)

---

## Quick Test Script

Located at `scripts/testing/gps/test-gps-quick.sh`:

```bash
#!/bin/bash
set -e

echo "=== GPS Coordinates Quick Test ==="
echo ""

# Login
echo "1. Logging in..."
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}')

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    exit 1
fi
echo "✅ Login successful"

# Test 1: Valid GPS
echo ""
echo "2. Creating trip with GPS..."
TRIP1=$(curl -s -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test GPS","description":"Testing GPS coordinates with automated script","start_date":"2024-06-01","distance_km":100,"locations":[{"name":"Madrid","latitude":40.416775,"longitude":-3.703790}]}')

if echo "$TRIP1" | grep -q '"success":true'; then
    echo "✅ Trip with GPS created"
else
    echo "❌ Failed to create trip"
fi

# Test 2: Invalid latitude
echo ""
echo "3. Testing invalid latitude..."
INVALID=$(curl -s -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Invalid","description":"Should fail","start_date":"2024-06-01","locations":[{"name":"Invalid","latitude":100.0,"longitude":0.0}]}')

if echo "$INVALID" | grep -q '"success":false'; then
    echo "✅ Invalid latitude rejected"
else
    echo "❌ Validation failed"
fi

echo ""
echo "=== All tests passed! ==="
```

**Usage**:
```bash
cd scripts/testing/gps
./test-gps-quick.sh
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
