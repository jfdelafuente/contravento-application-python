# Testing Scripts

Automated testing scripts for ContraVento features.

---

## 📁 Directory Structure

```
scripts/testing/
├── gps/                    # GPS Coordinates feature tests (009-gps-coordinates)
│   ├── get-token.sh        # Get access token (Linux/Mac)
│   ├── get-token.ps1       # Get access token (Windows PowerShell)
│   ├── test-gps-coordinates.sh   # Complete 6-test suite (manual token)
│   ├── test-gps-quick.sh   # Quick 3-test suite (automated)
│   └── README.md           # GPS testing documentation
└── README.md               # This file
```

---

## 🚀 Quick Start

### GPS Coordinates Testing

```bash
# Navigate to GPS testing scripts
cd scripts/testing/gps

# Option 1: Quick automated tests (recommended)
./test-gps-quick.sh

# Option 2: Complete test suite
./get-token.sh
# Copy token from output, edit test-gps-coordinates.sh line 9
./test-gps-coordinates.sh
```

See [gps/README.md](gps/README.md) for complete documentation.

---

## 📋 Available Test Suites

| Feature | Directory | Scripts | Tests | Documentation |
|---------|-----------|---------|-------|---------------|
| GPS Coordinates | [gps/](gps/) | 4 scripts | 3-6 tests | [gps/README.md](gps/README.md) |

---

## 🔧 Prerequisites

All test scripts require:

1. **Backend server running**:
   ```bash
   cd backend
   ./run-local-dev.sh  # or .\run-local-dev.ps1
   ```

2. **Test user exists** (`testuser` / `TestPass123!`):
   ```bash
   cd backend
   poetry run python scripts/create_verified_user.py
   ```

---

## 📚 Complete Documentation

For comprehensive testing guides including Postman collections and manual testing procedures:

- **GPS Coordinates**:
  - Quick Start: [gps/README.md](gps/README.md)
  - Manual Testing: [backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md](../../backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md)
  - Postman Guide: [backend/docs/api/GPS_COORDINATES_POSTMAN_GUIDE.md](../../backend/docs/api/GPS_COORDINATES_POSTMAN_GUIDE.md)
  - Test Results: [GPS_COORDINATES_TEST_RESULTS.md](../../GPS_COORDINATES_TEST_RESULTS.md)

---

## 💡 Tips

### Running from Project Root

If you prefer to run scripts from the project root:

```bash
# From project root
bash scripts/testing/gps/test-gps-quick.sh

# Or add to PATH temporarily
export PATH="$PATH:$(pwd)/scripts/testing/gps"
test-gps-quick.sh
```

### Windows Users

Use PowerShell for best compatibility:

```powershell
# PowerShell
.\scripts\testing\gps\get-token.ps1
```

Or Git Bash:

```bash
# Git Bash
bash scripts/testing/gps/test-gps-quick.sh
```

---

## 🔗 Related Resources

- **Feature Specifications**: [specs/](../../specs/)
- **API Documentation**: [backend/docs/api/](../../backend/docs/api/)
- **Backend Scripts**: [backend/scripts/](../../backend/scripts/)

---

**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
