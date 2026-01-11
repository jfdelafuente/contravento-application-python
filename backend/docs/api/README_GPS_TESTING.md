# GPS Coordinates Testing - Quick Start Guide

**Feature**: 009-gps-coordinates
**Documentation Created**: 2026-01-11

---

## 📋 Available Testing Guides

This directory contains comprehensive testing resources for the GPS Coordinates feature:

### 1. Manual Testing Guide (curl)
**File**: [GPS_COORDINATES_MANUAL_TESTING.md](./GPS_COORDINATES_MANUAL_TESTING.md)

Complete guide for testing GPS coordinates using curl commands.

**Best for**:
- ✅ Quick command-line testing
- ✅ CI/CD integration scripts
- ✅ Debugging specific endpoints
- ✅ Linux/Mac environments

**Includes**:
- 11 detailed test scenarios
- Setup instructions
- Troubleshooting guide
- Quick test script (automated bash)

### 2. Postman Testing Guide
**File**: [GPS_COORDINATES_POSTMAN_GUIDE.md](./GPS_COORDINATES_POSTMAN_GUIDE.md)

Complete guide for testing GPS coordinates using Postman.

**Best for**:
- ✅ Interactive API testing
- ✅ Visual test results
- ✅ Team collaboration
- ✅ Automated test execution (Collection Runner)

**Includes**:
- Importable collection (46 automated tests)
- Environment configuration
- Test scripts with assertions
- Newman CLI integration

### 3. Postman Collection (Importable)
**File**: [ContraVento_GPS_Coordinates.postman_collection.json](./ContraVento_GPS_Coordinates.postman_collection.json)

Ready-to-import Postman collection with 46 automated tests.

**Features**:
- 📦 Complete test suite
- 🤖 Automated assertions
- 💾 Auto-saves variables (trip IDs, tokens)
- 📊 Test result reporting

### 4. Postman Environment (Importable)
**File**: [ContraVento-Local.postman_environment.json](./ContraVento-Local.postman_environment.json)

Pre-configured environment for local development testing.

**Variables**:
- `base_url`: http://localhost:8000
- `username`: testuser
- `password`: TestPass123!
- Auto-filled: `access_token`, `trip_with_gps_id`, etc.

---

## 🚀 Quick Start

### Option A: Postman (Recommended for Interactive Testing)

**Step 1: Install Postman**
```bash
# Download from https://www.postman.com/downloads/
# Or use Postman Web: https://web.postman.com/
```

**Step 2: Import Collection & Environment**
1. Open Postman
2. Click **Import** (top-left)
3. Drag and drop both files:
   - `ContraVento_GPS_Coordinates.postman_collection.json`
   - `ContraVento-Local.postman_environment.json`
4. Click **Import**

**Step 3: Select Environment**
- Top-right dropdown: Select **"ContraVento - Local Development"**

**Step 4: Start Backend Server**
```bash
cd backend
./run-local-dev.sh  # or .\run-local-dev.ps1 on Windows
```

**Step 5: Run Tests**
1. Open collection: **ContraVento - GPS Coordinates Testing**
2. Run **"0. Authentication → Login"** first
3. Then run any other tests, or:
   - Click **Run** → **Run Collection** for all tests

**Expected Results**: 46/46 tests passed ✅

---

### Option B: curl (Recommended for CLI Testing)

**Step 1: Start Backend Server**
```bash
cd backend
./run-local-dev.sh  # or .\run-local-dev.ps1
```

**Step 2: Get Access Token**

**Linux/Mac**:
```bash
# Create token script
cat > get-token.sh <<'EOF'
#!/bin/bash
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}')

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    exit 1
fi

echo "✅ Login successful"
echo "export ACCESS_TOKEN=\"$TOKEN\""
EOF

chmod +x get-token.sh
./get-token.sh

# Copy the export command and run it
export ACCESS_TOKEN="<token_from_output>"
```

**Windows PowerShell**:
```powershell
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"login":"testuser","password":"TestPass123!"}'

$env:ACCESS_TOKEN = $response.data.access_token
Write-Host "✅ Token saved to `$env:ACCESS_TOKEN"
```

**Step 3: Run Test**

Example - Create trip with GPS:
```bash
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test GPS Trip",
    "description": "Testing GPS coordinates from curl",
    "start_date": "2024-06-01",
    "distance_km": 100,
    "locations": [
      {
        "name": "Madrid",
        "latitude": 40.416775,
        "longitude": -3.703790
      }
    ]
  }' | python -m json.tool
```

**Step 4: Run All Tests**

See [GPS_COORDINATES_MANUAL_TESTING.md](./GPS_COORDINATES_MANUAL_TESTING.md) for complete test scenarios.

---

## 📊 Test Coverage

| Category | Tests | Coverage |
|----------|-------|----------|
| Valid GPS Coordinates | 6 tests | Create, retrieve, verify precision |
| Backwards Compatibility | 3 tests | Trips without GPS, null coordinates |
| Validation Errors | 12 tests | Invalid lat/lon ranges, Spanish errors |
| Precision & Edge Cases | 14 tests | Rounding, mixed locations, boundaries |
| Update Operations | 2 tests | Add GPS to existing trips |
| **TOTAL** | **46 tests** | **Complete feature validation** |

---

## 🎯 Test Scenarios Covered

### ✅ Functional Requirements (FR)

- **FR-001**: Store latitude/longitude as optional decimal fields
- **FR-002**: Validate latitude range (-90 to 90)
- **FR-003**: Validate longitude range (-180 to 180)
- **FR-004**: Coordinates optional per location
- **FR-013**: Persist 6 decimal places precision

### ✅ Success Criteria (SC)

- **SC-002**: Coordinate validation with Spanish error messages
- **SC-005**: Existing trips without GPS work without modification
- **SC-008**: Coordinate precision limited to 6 decimals (~0.11m)

### ✅ Edge Cases

- Mixed locations (some with/without GPS)
- Extreme valid coordinates (poles, date line)
- Precision rounding (9 decimals → 6)
- Update operations (backfill GPS to historical trips)

---

## 🔧 Troubleshooting

### Postman: "Could not get any response"

**Solution**:
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/docs
   ```
2. Check `base_url` in environment: `http://localhost:8000`
3. Disable VPN/proxy if interfering

### Postman: "401 Unauthorized"

**Solution**:
1. Run **"0. Authentication → Login"** first
2. Check environment variables:
   - **Environments** → **ContraVento - Local Development**
   - Verify `access_token` has a value (auto-set after login)
3. Token expires after 1 hour - re-run login

### curl: "JSON decode error" (Windows)

**Solution**:
Use PowerShell `Invoke-RestMethod` instead of curl, or create JSON files:
```bash
echo '{"login":"testuser","password":"TestPass123!"}' > login.json
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  --data @login.json
```

### Backend: "Connection refused"

**Solution**:
Start backend server:
```bash
cd backend
./run-local-dev.sh  # or .\run-local-dev.ps1
```

---

## 📁 Directory Structure

```
backend/docs/api/
├── README_GPS_TESTING.md                           # This file
├── GPS_COORDINATES_MANUAL_TESTING.md               # curl testing guide
├── GPS_COORDINATES_POSTMAN_GUIDE.md                # Postman testing guide
├── ContraVento_GPS_Coordinates.postman_collection.json  # Postman collection
└── ContraVento-Local.postman_environment.json      # Postman environment
```

---

## 🔗 Related Documentation

- **Feature Specification**: [specs/009-gps-coordinates/spec.md](../../../specs/009-gps-coordinates/spec.md)
- **Implementation Plan**: [specs/009-gps-coordinates/plan.md](../../../specs/009-gps-coordinates/plan.md)
- **Test Results**: [GPS_COORDINATES_TEST_RESULTS.md](../../../GPS_COORDINATES_TEST_RESULTS.md)
- **OpenAPI Contract**: [specs/009-gps-coordinates/contracts/trips-api.yaml](../../../specs/009-gps-coordinates/contracts/trips-api.yaml)
- **Quick Start**: [specs/009-gps-coordinates/quickstart.md](../../../specs/009-gps-coordinates/quickstart.md)

---

## 🎓 Learning Resources

### For Postman Users
- **Postman Learning Center**: https://learning.postman.com/
- **Writing Tests**: https://learning.postman.com/docs/writing-scripts/test-scripts/
- **Collection Runner**: https://learning.postman.com/docs/collections/running-collections/intro-to-collection-runs/

### For curl Users
- **curl Manual**: https://curl.se/docs/manual.html
- **jq Tutorial** (JSON formatting): https://jqlang.github.io/jq/tutorial/

---

## 💡 Tips & Best Practices

### Postman Tips
1. **Use Collection Runner** for automated testing (all 46 tests in ~10 seconds)
2. **Check Console** (View → Show Postman Console) for detailed logs
3. **Save Responses** as examples for documentation
4. **Export Results** after runner completion for reports

### curl Tips
1. **Use jq** instead of `python -m json.tool` for better formatting:
   ```bash
   curl ... | jq '.'
   ```
2. **Save responses** to files for inspection:
   ```bash
   curl ... > response.json
   ```
3. **Use -v flag** for debugging:
   ```bash
   curl -v http://localhost:8000/trips
   ```

---

## 📞 Support

**Issues**: Report bugs at https://github.com/anthropics/claude-code/issues
**Documentation**: See [CLAUDE.md](../../../CLAUDE.md) for project overview

---

**Version**: 1.0
**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
