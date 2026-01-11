# GPS Coordinates Testing - Quick Reference

**Feature**: 009-gps-coordinates
**Scripts Location**: `scripts/testing/gps/`
**Documentation**: `backend/docs/api/`

---

## 🚀 Quick Start Scripts

### 1. Get Access Token

#### Linux/Mac:
```bash
./get-token.sh
```

#### Windows PowerShell:
```powershell
.\get-token.ps1
```

**What it does**:
- ✅ Checks if backend is running
- ✅ Logs in as `testuser`
- ✅ Extracts and displays access token
- ✅ (PowerShell) Auto-sets `$env:ACCESS_TOKEN`

**Output**:
```
✅ Backend server is running
✅ Login successful

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
To use the token, run this command:

  export ACCESS_TOKEN="eyJhbGc..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Token expires in 1 hour. Re-run this script to refresh.
```

**Usage after running**:
```bash
# Linux/Mac
export ACCESS_TOKEN="<token_from_output>"

# Windows PowerShell (auto-set, just verify)
echo $env:ACCESS_TOKEN
```

---

### 2. Quick GPS Test Suite

```bash
./test-gps-quick.sh
```

**What it does**:
- ✅ **Test 1**: Creates trip WITH GPS coordinates (validates storage + precision)
- ✅ **Test 2**: Creates trip WITHOUT GPS (validates backwards compatibility)
- ✅ **Test 3**: Tests invalid latitude > 90 (validates error handling)

**Output**:
```
╔════════════════════════════════════════════════════════════╗
║     GPS Coordinates - Quick Test Suite                    ║
╚════════════════════════════════════════════════════════════╝

✅ Backend server is running

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: Authentication
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Login successful

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 1: Creating trip with GPS coordinates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Trip created successfully
   Trip ID: ac935172-bc85-4845-acdd-889dd2cf0521
   Madrid coordinates: 40.416775, -3.70379
   ✅ Precision check: 6 decimals enforced

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 2: Creating trip WITHOUT GPS (backwards compatibility)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Trip created without GPS
   ✅ Coordinates are null (backwards compatible)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test 3: Testing validation (invalid latitude > 90)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Invalid latitude rejected (as expected)

╔════════════════════════════════════════════════════════════╗
║                    Test Summary                            ║
╚════════════════════════════════════════════════════════════╝

✅ Test 1: Trip with GPS coordinates       PASS
✅ Test 2: Trip without GPS (compat)       PASS
✅ Test 3: Invalid coordinate validation   PASS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All tests passed! ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Duration**: ~2-3 seconds

---

## 📁 Script Files in Root Directory

| File | Type | Purpose |
|------|------|---------|
| `get-token.sh` | Bash | Get access token (Linux/Mac) |
| `get-token.ps1` | PowerShell | Get access token (Windows) |
| `test-gps-quick.sh` | Bash | Quick 3-test validation |

---

## 📚 Complete Documentation

### Testing Guides

1. **Manual Testing (curl)**
   [backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md](backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md)
   - 11 detailed test scenarios
   - Complete curl examples
   - Validation checklists

2. **Postman Testing**
   [backend/docs/api/GPS_COORDINATES_POSTMAN_GUIDE.md](backend/docs/api/GPS_COORDINATES_POSTMAN_GUIDE.md)
   - 46 automated tests
   - Collection Runner guide
   - Newman CLI integration

3. **Quick Start Guide**
   [backend/docs/api/README_GPS_TESTING.md](backend/docs/api/README_GPS_TESTING.md)
   - Overview of all resources
   - Quick start for Postman & curl
   - Troubleshooting

### Importable Files

4. **Postman Collection**
   [backend/docs/api/ContraVento_GPS_Coordinates.postman_collection.json](backend/docs/api/ContraVento_GPS_Coordinates.postman_collection.json)
   - 46 tests with automated assertions
   - Import directly into Postman

5. **Postman Environment**
   [backend/docs/api/ContraVento-Local.postman_environment.json](backend/docs/api/ContraVento-Local.postman_environment.json)
   - Pre-configured variables
   - Import into Postman

### Test Results

6. **Manual Test Results**
   [GPS_COORDINATES_TEST_RESULTS.md](GPS_COORDINATES_TEST_RESULTS.md)
   - Results from manual execution
   - Validation evidence

---

## 🔧 Prerequisites

### 1. Backend Server Running

```bash
# Option 1: SQLite (fastest, recommended for testing)
cd backend
./run-local-dev.sh              # Linux/Mac
.\run-local-dev.ps1             # Windows PowerShell

# Option 2: Docker PostgreSQL
./deploy.sh local-minimal
```

Verify:
```bash
curl http://localhost:8000/docs
# Should return HTML (Swagger UI)
```

### 2. Test User Exists

Scripts use default test user:
- **Username**: `testuser`
- **Email**: `test@example.com`
- **Password**: `TestPass123!`

Create if missing:
```bash
cd backend
poetry run python scripts/create_verified_user.py
```

---

## 📊 Test Coverage

### Quick Test Suite (test-gps-quick.sh)
| Test | Validates | FR/SC |
|------|-----------|-------|
| Test 1 | GPS coordinates stored with 6 decimals | FR-001, FR-013 |
| Test 2 | Backwards compatibility (null coords) | FR-004, SC-005 |
| Test 3 | Latitude validation (-90 to 90) | FR-002, SC-002 |

### Complete Test Suite (Postman or Manual)
| Category | Tests | Coverage |
|----------|-------|----------|
| Valid GPS | 6 | Create, retrieve, precision |
| Backwards Compat | 3 | Null coordinates, existing trips |
| Validation | 12 | Invalid ranges, Spanish errors |
| Precision & Edge | 14 | Rounding, mixed, extremes |
| Update | 2 | Add GPS to existing |
| **TOTAL** | **46** | **All FR + SC** |

---

## 🐛 Troubleshooting

### Error: "Backend server is not running"

```bash
# Check if running
curl http://localhost:8000/docs

# If not running, start it
cd backend
./run-local-dev.sh
```

### Error: "Login failed"

```bash
# Verify test user exists
cd backend
poetry run python -c "from database import get_sync_db; from models import User; db = next(get_sync_db()); print(db.query(User).filter(User.username=='testuser').first())"

# If user doesn't exist, create it
poetry run python scripts/create_verified_user.py
```

### Error: "Permission denied: ./get-token.sh"

```bash
# Make script executable
chmod +x get-token.sh
chmod +x test-gps-quick.sh

# Then run again
./get-token.sh
```

### Windows: Scripts don't run

**Solution 1 - Use PowerShell**:
```powershell
.\get-token.ps1
```

**Solution 2 - Use Git Bash**:
```bash
bash get-token.sh
bash test-gps-quick.sh
```

---

## 💡 Usage Examples

### Example 1: Quick Validation

```bash
# Start backend (from project root)
cd backend && ./run-local-dev.sh &

# Run quick tests (from project root)
cd ../scripts/testing/gps
./test-gps-quick.sh
```

### Example 2: Manual Testing

```bash
# Get token
./get-token.sh
export ACCESS_TOKEN="<token>"

# Create trip with GPS
curl -X POST http://localhost:8000/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My GPS Trip",
    "description": "Testing GPS coordinates",
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

### Example 3: Postman Testing

1. Import collection and environment (see Postman guide)
2. Run "0. Authentication → Login"
3. Click "Run Collection" → 46 tests execute automatically
4. View results in Collection Runner

---

## 🔗 Related Resources

- **Feature Spec**: [specs/009-gps-coordinates/spec.md](../../../specs/009-gps-coordinates/spec.md)
- **Implementation Plan**: [specs/009-gps-coordinates/plan.md](../../../specs/009-gps-coordinates/plan.md)
- **Tasks**: [specs/009-gps-coordinates/tasks.md](../../../specs/009-gps-coordinates/tasks.md)
- **OpenAPI Contract**: [specs/009-gps-coordinates/contracts/trips-api.yaml](../../../specs/009-gps-coordinates/contracts/trips-api.yaml)
- **Manual Testing Guide**: [backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md](../../../backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md)
- **Postman Guide**: [backend/docs/api/GPS_COORDINATES_POSTMAN_GUIDE.md](../../../backend/docs/api/GPS_COORDINATES_POSTMAN_GUIDE.md)
- **Test Results**: [GPS_COORDINATES_TEST_RESULTS.md](../../../GPS_COORDINATES_TEST_RESULTS.md)

---

## ✅ Next Steps

After running tests successfully:

1. **Phase 3**: Implement User Story 1 (TDD workflow)
   - Write backend unit tests (T012-T015)
   - Write integration tests (T016-T017)
   - Write contract tests (T018-T019)

2. **Phase 4**: Implement User Story 2 (Frontend UI)
   - Create LocationInput component
   - Integrate into trip creation form

3. **Phase 5**: Implement User Story 3 (Edit workflow)
   - Update trip edit form
   - Enable coordinate backfilling

See [specs/009-gps-coordinates/tasks.md](../../../specs/009-gps-coordinates/tasks.md) for complete task list.

---

**Document Version**: 1.0
**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
