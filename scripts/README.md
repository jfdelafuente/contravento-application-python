# Scripts Directory

Utility scripts for ContraVento development and testing.

---

## 📁 Directory Structure

```
scripts/
├── seed/                          # Sample data for development
│   ├── README.md
│   ├── create_test_trips.sh       # Create 3 sample trips
│   └── create_test_trips.ps1
│
└── testing/                       # Automated testing scripts
    ├── README.md
    └── gps/                       # GPS Coordinates feature tests
        ├── get-token.sh
        ├── get-token.ps1
        ├── test-gps-coordinates.sh
        ├── test-gps-quick.sh
        └── README.md
```

---

## 🎯 Purpose of Each Directory

### 📦 `seed/` - Sample Data Scripts

**Purpose**: Populate database with realistic sample data for development and demos

**Use when**:
- ✅ Setting up new development environment
- ✅ Creating demo data for presentations
- ✅ Testing frontend with realistic content
- ✅ Generating screenshots/documentation

**Available scripts**:
- `create_test_trips.sh` / `.ps1` - Creates 3 sample trips

**Documentation**: [seed/README.md](seed/README.md)

---

### 🧪 `testing/` - Automated Testing Scripts

**Purpose**: Automated validation and testing of API endpoints and features

**Use when**:
- ✅ Running smoke tests before commit
- ✅ Validating API functionality
- ✅ Testing new features
- ✅ CI/CD pipelines

**Available test suites**:
- GPS Coordinates (009-gps-coordinates) - 3-6 automated tests

**Documentation**: [testing/README.md](testing/README.md)

---

## 🚀 Quick Start

### Create Sample Data

```bash
# Navigate to seed scripts
cd scripts/seed

# Run seed script
./create_test_trips.sh  # Linux/Mac
# or
.\create_test_trips.ps1  # Windows PowerShell
```

**Result**: 3 sample trips created in database

---

### Run Automated Tests

```bash
# Navigate to testing scripts
cd scripts/testing/gps

# Run quick test suite
./test-gps-quick.sh
```

**Result**: 3 tests executed, validation report

---

## 📊 Comparison: Seed vs Testing

| Aspect | Seed Scripts | Testing Scripts |
|--------|-------------|-----------------|
| **Purpose** | Create sample data | Validate functionality |
| **When to use** | Development setup | Before commit, CI/CD |
| **Idempotent** | ❌ No (creates duplicates) | ✅ Yes (read-only or cleanup) |
| **Output** | Database records | Pass/fail report |
| **Example** | `create_test_trips.sh` | `test-gps-quick.sh` |

---

## 🔗 Related Resources

### Backend Scripts

Python scripts for user/admin management:

```
backend/scripts/
├── create_admin.py              # Create admin user
├── create_verified_user.py      # Create test users
└── promote_to_admin.py          # Promote user to admin
```

See [backend/scripts/](../backend/scripts/) for backend-specific scripts.

---

### API Documentation

For manual API testing and Postman collections:

```
backend/docs/api/
├── GPS_COORDINATES_MANUAL_TESTING.md
├── GPS_COORDINATES_POSTMAN_GUIDE.md
├── ContraVento_GPS_Coordinates.postman_collection.json
└── ContraVento-Local.postman_environment.json
```

See [backend/docs/api/](../backend/docs/api/) for complete API documentation.

---

## 💡 Common Workflows

### Workflow 1: Fresh Development Environment

```bash
# 1. Start backend
cd backend
./run-local-dev.sh --setup

# 2. Create sample data
cd ../scripts/seed
./create_test_trips.sh

# 3. Verify data
cd ../testing/gps
./get-token.sh
export ACCESS_TOKEN="<token>"
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/users/testuser/trips
```

---

### Workflow 2: Test-Driven Development

```bash
# 1. Run tests before changes (should pass)
cd scripts/testing/gps
./test-gps-quick.sh

# 2. Make code changes
# ... edit code ...

# 3. Run tests after changes (verify still passing)
./test-gps-quick.sh

# 4. Commit if tests pass
git add .
git commit -m "feat: add new feature"
```

---

### Workflow 3: Demo Preparation

```bash
# 1. Reset database
cd backend
rm contravento_dev.db
./run-local-dev.sh --setup

# 2. Create sample data
cd ../scripts/seed
./create_test_trips.sh

# 3. Start frontend
cd ../../frontend
npm run dev

# 4. Demo at http://localhost:3001
```

---

## 📝 Script Naming Conventions

When adding new scripts, follow these conventions:

### Seed Scripts
```bash
scripts/seed/create_<resource>_<description>.<ext>

Examples:
- create_test_trips.sh           # Creates sample trips
- create_test_users.sh           # Creates sample users
- create_full_dataset.sh         # Complete seed dataset
```

### Testing Scripts
```bash
scripts/testing/<feature>/test-<feature>-<variant>.<ext>

Examples:
- testing/gps/test-gps-quick.sh       # Quick GPS tests
- testing/gps/test-gps-coordinates.sh # Complete GPS tests
- testing/auth/test-auth-quick.sh     # Quick auth tests
```

---

## 🛠️ Prerequisites

All scripts require:

1. **Backend server running**:
   ```bash
   cd backend
   ./run-local-dev.sh
   ```

2. **Test user exists**:
   ```bash
   cd backend
   poetry run python scripts/create_verified_user.py
   ```

3. **Bash or PowerShell** (depending on script extension)

---

## 🆕 Contributing New Scripts

### Adding Seed Scripts

1. Create script in `scripts/seed/`
2. Follow naming convention: `create_<resource>_<description>.sh`
3. Include both `.sh` (Linux/Mac) and `.ps1` (Windows) versions
4. Update `seed/README.md` with script description
5. Test on fresh database

### Adding Testing Scripts

1. Create feature directory: `scripts/testing/<feature>/`
2. Follow naming convention: `test-<feature>-<variant>.sh`
3. Include automated login (don't require manual token)
4. Add README.md explaining test scenarios
5. Update `testing/README.md` with new test suite

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| [scripts/README.md](README.md) | This file - overview of all scripts |
| [scripts/seed/README.md](seed/README.md) | Seed scripts documentation |
| [scripts/testing/README.md](testing/README.md) | Testing scripts overview |
| [scripts/testing/gps/README.md](testing/gps/README.md) | GPS testing documentation |
| [TESTING.md](../TESTING.md) | Root-level testing quick reference |

---

**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
