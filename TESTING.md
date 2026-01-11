# Testing Guide - ContraVento

Quick reference for testing scripts and documentation.

---

## 🚀 Quick Start

### GPS Coordinates Feature Testing

```bash
# Navigate to GPS testing directory
cd scripts/testing/gps

# Run quick automated test suite (3 tests)
./test-gps-quick.sh
```

**Expected output**: All 3 tests pass ✅

---

## 📁 Scripts Location

### Testing Scripts

All testing scripts are located in `scripts/testing/`:

```
scripts/testing/
└── gps/                          # GPS Coordinates feature (009-gps-coordinates)
    ├── get-token.sh              # Get API access token (Linux/Mac)
    ├── get-token.ps1             # Get API access token (Windows)
    ├── test-gps-coordinates.sh   # Complete 6-test suite
    ├── test-gps-quick.sh         # Quick 3-test suite (automated)
    └── README.md                 # Complete GPS testing guide
```

See [scripts/testing/README.md](scripts/testing/README.md) for details.

### Seed Scripts (Sample Data)

Sample data creation scripts in `scripts/seed/`:

```
scripts/seed/
├── create_test_trips.sh          # Create 3 sample trips (Linux/Mac)
├── create_test_trips.ps1         # Create 3 sample trips (Windows)
└── README.md                     # Seed scripts documentation
```

See [scripts/seed/README.md](scripts/seed/README.md) for details.

---

### API Testing Documentation

Complete testing guides with curl examples and Postman collections:

```
backend/docs/api/
├── GPS_COORDINATES_MANUAL_TESTING.md          # curl testing guide (11 scenarios)
├── GPS_COORDINATES_POSTMAN_GUIDE.md           # Postman guide (46 tests)
├── ContraVento_GPS_Coordinates.postman_collection.json
└── ContraVento-Local.postman_environment.json
```

See [backend/docs/api/README_GPS_TESTING.md](backend/docs/api/README_GPS_TESTING.md) for overview.

---

### Test Results & Evidence

```
GPS_COORDINATES_TEST_RESULTS.md    # Manual test execution results
```

---

## 🎯 Testing Options

| Method | Location | Tests | Best For |
|--------|----------|-------|----------|
| **Quick Script** | `scripts/testing/gps/test-gps-quick.sh` | 3 tests | Smoke testing, CI/CD |
| **Complete Script** | `scripts/testing/gps/test-gps-coordinates.sh` | 6 tests | Full validation |
| **Postman** | `backend/docs/api/*.postman_collection.json` | 46 tests | Interactive, reporting |
| **Manual curl** | `backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md` | 11 scenarios | Learning, debugging |

---

## 📖 Documentation Hierarchy

```
1. Quick Start (You are here)
   ├─> TESTING.md                                    # This file
   └─> scripts/testing/README.md                     # Testing scripts overview

2. Feature-Specific Guides
   ├─> scripts/testing/gps/README.md                 # GPS quick reference
   ├─> backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md
   └─> backend/docs/api/GPS_COORDINATES_POSTMAN_GUIDE.md

3. Specifications & Plans
   ├─> specs/009-gps-coordinates/spec.md             # Feature specification
   ├─> specs/009-gps-coordinates/plan.md             # Implementation plan
   └─> specs/009-gps-coordinates/tasks.md            # Task breakdown

4. Results & Evidence
   └─> GPS_COORDINATES_TEST_RESULTS.md               # Test execution results
```

---

## 🔗 Quick Links

| Resource | Path |
|----------|------|
| **Testing Scripts** | [scripts/testing/](scripts/testing/) |
| **API Documentation** | [backend/docs/api/](backend/docs/api/) |
| **Feature Specs** | [specs/](specs/) |
| **Project Guide** | [CLAUDE.md](CLAUDE.md) |

---

**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
