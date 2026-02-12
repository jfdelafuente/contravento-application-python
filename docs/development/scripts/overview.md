# Utility Scripts - Overview

Complete catalog of utility scripts for ContraVento development, testing, and operations.

**Audience**: Developers, DevOps engineers

---

## Table of Contents

- [Script Categories](#script-categories)
- [Analysis Scripts](#analysis-scripts)
- [Development Tools](#development-tools)
- [Seeding Scripts](#seeding-scripts)
- [User Management](#user-management)
- [Testing Scripts](#testing-scripts)
- [Common Workflows](#common-workflows)

---

## Script Categories

ContraVento includes 20+ utility scripts organized by purpose:

| Category | Purpose | Location | Count |
|----------|---------|----------|-------|
| **Analysis** | GPX diagnostics, performance analysis | `scripts/analysis/` | 2 |
| **Dev-tools** | Data verification, cleanup utilities | `scripts/dev-tools/` | 4 |
| **Seeding** | Test data creation, database seeding | `scripts/seeding/` | 1 |
| **User Management** | Admin/user creation, role management | `scripts/user-mgmt/` | 3 |
| **Testing** | Verification scripts, test data checks | `scripts/testing/` | 5 |

---

## Analysis Scripts

**Location**: `backend/scripts/analysis/`

### analyze_gpx_segments.py

Analyzes segment speeds in GPX files to understand stop detection and route characteristics.

**Purpose**:
- Detects stops based on speed (<3 km/h) and duration (>2 min)
- Identifies slow segments, long segments, and stop segments
- Calculates total stop time
- Helps debug GPX processing issues

**Usage**:
```bash
cd backend

# Analyze GPX file from database
poetry run python scripts/analysis/analyze_gpx_segments.py GPX_FILE_ID

# Analyze GPX file from local filesystem
poetry run python scripts/analysis/analyze_gpx_segments.py --file-path /path/to/route.gpx

# Example with real GPX file ID
poetry run python scripts/analysis/analyze_gpx_segments.py 13e24f2f-f792-4873-b636-ad3568861514
```

**Sample Output**:
```
Analyzing 1234 GPS points
================================================================================

SEGMENT ANALYSIS
--------------------------------------------------------------------------------
Total segments:             1233
Slow segments (< 3 km/h):   45
Long segments (> 2.0 min):    12
STOP segments (both):       8

DETECTED STOPS (speed < 3.0 km/h, duration > 2.0 min):
--------------------------------------------------------------------------------
  Segment  123:   5.25 min,   1.20 km/h
  Segment  456:  12.80 min,   0.50 km/h
  Segment  789:   3.15 min,   2.10 km/h

Total stop time: 45.67 min (0.76 hours)
```

**When to Use**:
- ✅ Debugging stop detection in GPX processing
- ✅ Understanding route characteristics (stops, average speed)
- ✅ Validating moving time vs total time calculations
- ✅ Investigating performance issues with GPX parsing

**Related**:
- FR-013: Stop detection in `gpx_service.py`
- [GPX Processing](../../architecture/integrations/gpx-processing.md)

---

### diagnose_gpx_performance.py

Performance diagnostics for GPX file parsing and processing.

**Purpose**:
- Measures parsing time for large GPX files
- Identifies bottlenecks in track simplification
- Analyzes trackpoint density and memory usage
- Benchmarks Douglas-Peucker algorithm performance

**Usage**:
```bash
cd backend

# Diagnose GPX file from database
poetry run python scripts/analysis/diagnose_gpx_performance.py GPX_FILE_ID

# Diagnose local GPX file
poetry run python scripts/analysis/diagnose_gpx_performance.py --file-path /path/to/route.gpx

# Benchmark with multiple epsilon values
poetry run python scripts/analysis/diagnose_gpx_performance.py --file-path route.gpx --benchmark
```

**Sample Output**:
```
GPX Performance Diagnostics
================================================================================
File: pirineos_bikepacking.gpx
Original trackpoints: 5,234

Parsing Performance:
  Parse time: 1.23s
  Memory usage: 12.5 MB

Douglas-Peucker Simplification:
  Epsilon: 0.00005 (default)
  Simplified trackpoints: 423
  Reduction: 91.9%
  Simplification time: 0.45s

Distance Calculation:
  Total distance: 320.5 km
  Calculation time: 0.12s

Total processing time: 1.80s
```

**When to Use**:
- ✅ Investigating slow GPX uploads
- ✅ Optimizing Douglas-Peucker epsilon parameter
- ✅ Benchmarking performance improvements
- ✅ Debugging memory issues with large files (>10 MB)

**Related**:
- SC-013: Chart load time <2s for 1000 points
- [GPX Processing Architecture](../../architecture/integrations/gpx-processing.md#douglas-peucker-algorithm)

---

## Development Tools

**Location**: `backend/scripts/dev-tools/`

### check_stats.py

Verifies user statistics integrity and recalculates stats for debugging.

**Purpose**:
- Lists all user stats in database
- Verifies stats match actual trip data
- Recalculates stats from scratch for validation
- Identifies discrepancies (e.g., incorrect trip count)

**Usage**:
```bash
cd backend

# List all user stats
poetry run python scripts/dev-tools/check_stats.py

# Check specific user
poetry run python scripts/dev-tools/check_stats.py --username testuser

# Recalculate and compare (dry-run)
poetry run python scripts/dev-tools/check_stats.py --recalculate
```

**Sample Output**:
```
User Statistics Summary
================================================================================
Username: testuser
  Trip count: 12
  Total distance: 450.5 km
  Longest trip: 85.2 km
  Photo count: 156
  Countries: 3 (Spain, France, Italy)

Verification: ✅ All stats match trip data
```

**When to Use**:
- ✅ Debugging incorrect stats after trip edits
- ✅ Verifying stats integration after code changes
- ✅ Manual testing of stats recalculation
- ✅ Investigating achievement unlock issues

**Related**:
- [Stats Integration](../../features/stats-integration.md)
- StatsService (`src/services/stats_service.py`)

---

### check_latest_gpx.py

Displays metadata for the most recently uploaded GPX file.

**Purpose**:
- Quick verification after GPX upload
- Inspects GPX metadata (distance, elevation, trackpoints)
- Useful for manual testing during development

**Usage**:
```bash
cd backend

# Show latest GPX file
poetry run python scripts/dev-tools/check_latest_gpx.py
```

**Sample Output**:
```
Latest GPX File
================================================================================
GPX ID: 13e24f2f-f792-4873-b636-ad3568861514
Trip ID: 456
Trip title: Ruta Bikepacking Pirineos

Metadata:
  Total distance: 320.5 km
  Elevation gain: 4,250 m
  Has elevation: Yes
  Original trackpoints: 5,234
  Simplified trackpoints: 423
  Uploaded: 2026-02-07 14:30:00 UTC
```

**When to Use**:
- ✅ Quick verification after GPX upload via frontend
- ✅ Debugging GPX processing issues
- ✅ Testing GPX metadata extraction

---

### check_test_data.py

Verifies test data integrity and displays sample users/trips.

**Purpose**:
- Lists test users and their trips
- Verifies test data after seeding
- Checks database state during development
- Useful for manual testing workflows

**Usage**:
```bash
cd backend

# List all test users and trips
poetry run python scripts/dev-tools/check_test_data.py

# Check specific user
poetry run python scripts/dev-tools/check_test_data.py --username maria_garcia
```

**Sample Output**:
```
Test Users
================================================================================
1. admin (admin@contravento.com) - ADMIN
   Trips: 5 (3 published, 2 draft)
   Photos: 45

2. testuser (test@example.com) - USER
   Trips: 12 (10 published, 2 draft)
   Photos: 156
```

**When to Use**:
- ✅ Verifying test data after `./run-local-dev.sh --setup`
- ✅ Manual testing of trip workflows
- ✅ Debugging user-specific issues

---

### clean_trips.py

**Dangerous script** - Deletes all trips for a specific user or all users.

**Purpose**:
- Cleanup test data during development
- Reset database to clean state
- Useful for repetitive testing workflows

**Usage**:
```bash
cd backend

# Delete all trips for specific user
poetry run python scripts/dev-tools/clean_trips.py --username testuser

# Delete ALL trips (requires confirmation)
poetry run python scripts/dev-tools/clean_trips.py --all

# Dry-run mode (preview without deleting)
poetry run python scripts/dev-tools/clean_trips.py --username testuser --dry-run
```

**⚠️ Warning**: This script permanently deletes trips and associated photos. Use with caution.

**When to Use**:
- ✅ Resetting test data during development
- ✅ Cleaning up after manual testing
- ❌ **NEVER use in production**

---

## Seeding Scripts

**Location**: `backend/scripts/seeding/`

### seed_cycling_types.py

Loads cycling types from YAML configuration into database.

**Purpose**:
- Populates cycling_types table from `config/cycling_types.yaml`
- Supports both initial seeding and updates
- Idempotent (can run multiple times safely)
- Lists current cycling types in database

**Usage**:
```bash
cd backend

# Initial seed (skips existing types)
poetry run python scripts/seeding/seed_cycling_types.py

# Force update existing types from YAML
poetry run python scripts/seeding/seed_cycling_types.py --force

# List current types in database
poetry run python scripts/seeding/seed_cycling_types.py --list
```

**Sample Output**:
```
Loading cycling types from: backend/config/cycling_types.yaml
Found 6 cycling types in YAML
  + Created: bikepacking
  + Created: road
  + Created: mountain
  - Skipped (exists): gravel
  - Skipped (exists): urban
  - Skipped (exists): touring

==================================================
Cycling Types Seeding Complete
==================================================
Created:  3
Updated:  0
Skipped:  3
Total:    6
```

**Configuration**:

Edit `backend/config/cycling_types.yaml`:
```yaml
cycling_types:
  - code: bikepacking
    display_name: Bikepacking
    description: Viajes de varios días en bicicleta con equipaje completo
    is_active: true

  - code: cyclocross
    display_name: Ciclocross
    description: Carreras en circuitos mixtos
    is_active: true
```

**When to Use**:
- ✅ Initial database setup (run once after migrations)
- ✅ Adding new cycling types to the platform
- ✅ Updating descriptions for existing types
- ✅ Reactivating deactivated types

**Related**:
- [Cycling Types Feature](../../features/cycling-types.md)
- Admin API endpoints: `POST /admin/cycling-types`

---

## User Management

**Location**: `backend/scripts/user-mgmt/`

### create_admin.py

Creates an admin user with verified email and ADMIN role.

**Purpose**:
- Initial setup: Create first admin user
- Operational: Add additional admins
- Promotes existing users to admin role
- Displays credentials for first login

**Usage**:
```bash
cd backend

# Create default admin (admin / AdminPass123!)
poetry run python scripts/user-mgmt/create_admin.py

# Create custom admin
poetry run python scripts/user-mgmt/create_admin.py \
  --username myadmin \
  --email admin@mycompany.com \
  --password "MySecurePass123!"

# Force creation even if admins exist
poetry run python scripts/user-mgmt/create_admin.py --force
```

**Default Credentials**:
- **Username**: `admin`
- **Email**: `admin@contravento.com`
- **Password**: `AdminPass123!`
- **Role**: ADMIN (verified)

**Sample Output**:
```
==================================================
CREACION DE ADMINISTRADOR - CONTRAVENTO
==================================================

[INFO] Creando usuario administrador 'admin'...
[OK] Usuario registrado: admin
[OK] Email verificado automaticamente
[OK] Rol asignado: ADMIN

============================================================
ADMINISTRADOR CREADO EXITOSAMENTE
============================================================
Username: admin
Email: admin@contravento.com
Password: AdminPass123!
User ID: 13e24f2f-f792-4873-b636-ad3568861514
Rol: ADMIN
Verificado: Si
Activo: Si
============================================================

IMPORTANTE: Guarda estas credenciales en un lugar seguro.
   El password no se puede recuperar desde la base de datos.
```

**Security Notes**:
- Password requirements: ≥8 chars, uppercase, lowercase, number
- Email verified automatically (skips verification flow)
- Admin credentials displayed **once** during creation
- Store credentials securely (1Password, LastPass, etc.)

**When to Use**:
- ✅ Initial setup: Create first admin (run once)
- ✅ Adding additional admins for team members
- ✅ Promoting existing user to admin role
- ✅ Recovering admin access (create new admin)

**Related**:
- [Getting Started - User Management](../getting-started.md#user-management)
- Admin API endpoints: `/admin/*`

---

### create_verified_user.py

Creates regular users with verified email for testing.

**Purpose**:
- Create test users during development
- Seed database with sample users
- Verify existing users by email
- Optionally create users with ADMIN role

**Usage**:
```bash
cd backend

# Create default test users (testuser + maria_garcia)
poetry run python scripts/user-mgmt/create_verified_user.py

# Create custom verified user
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username john \
  --email john@example.com \
  --password "SecurePass123!"

# Create admin user
poetry run python scripts/user-mgmt/create_verified_user.py \
  --username myadmin \
  --email admin@mycompany.com \
  --password "AdminPass123!" \
  --role admin

# Verify existing user by email
poetry run python scripts/user-mgmt/create_verified_user.py --verify-email test@example.com
```

**Default Test Users**:

1. **testuser**:
   - Email: `test@example.com`
   - Password: `TestPass123!`
   - Role: USER

2. **maria_garcia**:
   - Email: `maria@example.com`
   - Password: `SecurePass456!`
   - Role: USER

**When to Use**:
- ✅ Initial setup: Create test users (automated in `./run-local-dev.sh --setup`)
- ✅ Manual testing: Create users with specific profiles
- ✅ Verifying email: Manually verify existing users
- ✅ Testing: Create multiple users for social features

**Related**:
- [Getting Started - User Management](../getting-started.md#user-management)

---

### promote_to_admin.py

Promotes existing user to ADMIN role or demotes admin to USER.

**Purpose**:
- Promote users to admin role
- Demote admins to regular users
- Update user roles dynamically
- Verify email during promotion

**Usage**:
```bash
cd backend

# Promote user to admin
poetry run python scripts/user-mgmt/promote_to_admin.py --username testuser

# Demote admin to user
poetry run python scripts/user-mgmt/promote_to_admin.py --username admin --demote
```

**Sample Output**:
```
Promoting user 'testuser' to ADMIN role...

User Details:
  Username: testuser
  Email: test@example.com
  Current role: USER

✓ Promoted to ADMIN
✓ Email verified

Updated User:
  Username: testuser
  Role: ADMIN
  Verified: Yes
```

**When to Use**:
- ✅ Promoting trusted users to admins
- ✅ Testing admin-only features
- ✅ Demoting admins (role change, offboarding)

**Related**:
- User roles: `src/models/user.py` (UserRole enum)

---

## Testing Scripts

**Location**: `backend/scripts/testing/`

### check_gpx_trips.py

Verifies GPX trip data in database for testing and validation.

**Purpose**:
- Lists trips with GPX files
- Displays sample trip metadata
- Provides test URLs for frontend verification
- Quick validation after GPX upload

**Usage**:
```bash
cd backend

# Check trips with GPX files
poetry run python scripts/testing/check_gpx_trips.py
```

**Sample Output**:
```
Trips with GPX: 8

Example GPX trip:
  ID: 13e24f2f-f792-4873-b636-ad3568861514
  Title: Ruta Bikepacking Pirineos
  Status: PUBLISHED
  Privacy: Public

Test URL: http://localhost:5173/trips/13e24f2f-f792-4873-b636-ad3568861514
```

**When to Use**:
- ✅ Verifying GPX uploads during testing
- ✅ Getting test URLs for frontend verification
- ✅ Checking database state after GPX processing

---

### test_route_statistics.py

Tests route statistics calculation and validation.

**Purpose**:
- Validates distance/elevation calculations
- Tests moving time vs total time
- Verifies stop detection accuracy
- Benchmarks statistics performance

**Usage**:
```bash
cd backend

# Test statistics for specific GPX file
poetry run python scripts/testing/test_route_statistics.py GPX_FILE_ID

# Test with custom epsilon for simplification
poetry run python scripts/testing/test_route_statistics.py --file-path route.gpx --epsilon 0.0001
```

**When to Use**:
- ✅ Validating GPX statistics after code changes
- ✅ Testing stop detection algorithms
- ✅ Benchmarking performance improvements

---

### test_tags.sh

Interactive script for testing tag filtering and categorization.

**Purpose**:
- Manual testing of tag filtering
- Tests case-insensitive tag matching
- Validates popular tags endpoint
- Tests pagination and status filtering

**Usage**:
```bash
cd backend

# Run interactive tag testing
bash scripts/testing/test_tags.sh
```

**Test Scenarios**:
1. Create trips with various tags
2. Test case-insensitive matching (bikepacking = Bikepacking = BIKEPACKING)
3. Filter trips by tag
4. Get popular tags by usage count
5. Test pagination (limit/offset)
6. Filter by status (DRAFT/PUBLISHED)

**When to Use**:
- ✅ Manual testing of travel diary tag features
- ✅ Validating tag normalization
- ✅ Testing tag API endpoints

**Related**:
- [Travel Diary Feature](../../features/travel-diary.md#tags-categorization)
- Tag API: `GET /users/{username}/trips?tag=bikepacking`

---

### test_gpx_statistics.sh / .ps1

Cross-platform scripts for testing GPX statistics calculation.

**Purpose**:
- Automated testing of GPX parsing
- Validates statistics accuracy
- Runs on Linux/Mac (bash) and Windows (PowerShell)

**Usage**:
```bash
# Linux/Mac
bash scripts/testing/test_gpx_statistics.sh

# Windows PowerShell
.\scripts\testing\test_gpx_statistics.ps1
```

**When to Use**:
- ✅ CI/CD integration for GPX testing
- ✅ Cross-platform validation
- ✅ Regression testing after GPX service changes

---

## Common Workflows

### Initial Setup Workflow

**Scenario**: Setting up ContraVento for the first time

```bash
# 1. Setup database and create admin + test users
./run-local-dev.sh --setup

# 2. Seed cycling types
cd backend
poetry run python scripts/seeding/seed_cycling_types.py

# 3. Verify setup
poetry run python scripts/dev-tools/check_test_data.py
poetry run python scripts/seeding/seed_cycling_types.py --list

# 4. Start development
cd ..
./run-local-dev.sh
```

**Result**: Database initialized with admin, test users, and cycling types.

---

### Testing GPX Upload Workflow

**Scenario**: Testing GPX upload feature during development

```bash
cd backend

# 1. Upload GPX file via frontend (http://localhost:5173/trips/new)

# 2. Verify upload
poetry run python scripts/dev-tools/check_latest_gpx.py

# 3. Check trips with GPX
poetry run python scripts/testing/check_gpx_trips.py

# 4. Analyze segments (optional)
poetry run python scripts/analysis/analyze_gpx_segments.py GPX_FILE_ID

# 5. Test frontend
# Open URL from check_gpx_trips.py output
```

**Result**: GPX file uploaded, verified, and ready for frontend testing.

---

### Debugging Stats Integration Workflow

**Scenario**: User reports incorrect trip count in profile

```bash
cd backend

# 1. Check current stats
poetry run python scripts/dev-tools/check_stats.py --username testuser

# 2. Recalculate stats (dry-run)
poetry run python scripts/dev-tools/check_stats.py --recalculate --username testuser

# 3. If discrepancy found, investigate trips
poetry run python scripts/dev-tools/check_test_data.py --username testuser

# 4. Fix data issue (if needed)

# 5. Trigger stats recalculation via API
curl -X POST http://localhost:8000/users/testuser/stats/recalculate \
  -H "Authorization: Bearer TOKEN"
```

**Result**: Stats verified and recalculated if needed.

---

### Adding New Cycling Type Workflow

**Scenario**: Adding "Cyclocross" as new cycling type

```bash
cd backend

# 1. Edit YAML configuration
nano config/cycling_types.yaml

# Add:
# - code: cyclocross
#   display_name: Ciclocross
#   description: Carreras en circuitos mixtos
#   is_active: true

# 2. Seed into database
poetry run python scripts/seeding/seed_cycling_types.py

# 3. Verify
poetry run python scripts/seeding/seed_cycling_types.py --list

# 4. Test API
curl http://localhost:8000/cycling-types
```

**Result**: New cycling type available in frontend dropdowns.

---

### Performance Analysis Workflow

**Scenario**: Investigating slow GPX upload for large files

```bash
cd backend

# 1. Diagnose performance
poetry run python scripts/analysis/diagnose_gpx_performance.py --file-path large_route.gpx

# 2. Analyze segments
poetry run python scripts/analysis/analyze_gpx_segments.py --file-path large_route.gpx

# 3. Benchmark different epsilon values
poetry run python scripts/analysis/diagnose_gpx_performance.py \
  --file-path large_route.gpx \
  --benchmark

# 4. Compare results and optimize gpx_service.py
```

**Result**: Performance bottleneck identified and optimized.

---

## Script Development Guidelines

### Creating New Scripts

**Best Practices**:

1. **Location**: Place in appropriate category (`analysis/`, `dev-tools/`, `seeding/`, `user-mgmt/`, `testing/`)
2. **Shebang**: Add `#!/usr/bin/env python3` for executable scripts
3. **Docstring**: Include module docstring with purpose, usage, requirements
4. **Arguments**: Use `argparse` for command-line arguments
5. **Async**: Use `asyncio` for database operations
6. **Error Handling**: Catch exceptions and display helpful errors
7. **Output**: Use clear, formatted output with section headers
8. **Documentation**: Update this file with new script details

**Template**:
```python
#!/usr/bin/env python3
"""
Brief description of script purpose.

Usage:
    poetry run python scripts/category/my_script.py

Requirements:
    - List any prerequisites

Output:
    - Describe expected output
"""

import asyncio
import argparse
from src.database import AsyncSessionLocal

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("--arg", help="Argument description")
    args = parser.parse_args()

    async with AsyncSessionLocal() as db:
        # Script logic here
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Related Documentation

- **[Getting Started](../getting-started.md)** - Developer onboarding
- **[TDD Workflow](../tdd-workflow.md)** - Test-driven development
- **[GPX Processing](../../architecture/integrations/gpx-processing.md)** - GPX architecture
- **[Stats Integration](../../features/stats-integration.md)** - Stats feature details
- **[Cycling Types](../../features/cycling-types.md)** - Cycling types management

---

**Last Updated**: 2026-02-07
**Script Count**: 20+
**Categories**: 5 (Analysis, Dev-tools, Seeding, User Management, Testing)
