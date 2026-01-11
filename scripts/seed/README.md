# Seed Scripts - Sample Data for Development

Scripts to populate the database with sample data for development and testing.

---

## 📋 Available Seed Scripts

### 1. Create Test Trips

**Files**:
- `create_test_trips.sh` (Linux/Mac)
- `create_test_trips.ps1` (Windows PowerShell)

**Purpose**: Creates 3 sample trips in the database for development/demo purposes

**Sample Trips Created**:
1. **Vía Verde del Aceite** (Jaén a Córdoba)
   - Difficulty: Moderate
   - Distance: 128.5 km
   - Tags: vías verdes, aceite, andalucía

2. **Ruta Bikepacking Pirineos** (Valle de Ordesa)
   - Difficulty: Difficult
   - Distance: 320 km
   - Tags: bikepacking, montaña, pirineos

3. **Camino de Santiago** (León a Astorga)
   - Difficulty: Easy
   - Distance: 52 km
   - Tags: camino de santiago, cultural

---

## 🚀 Usage

### Prerequisites

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

### Run Seed Script

**Linux/Mac**:
```bash
cd scripts/seed
./create_test_trips.sh
```

**Windows PowerShell**:
```powershell
cd scripts/seed
.\create_test_trips.ps1
```

**Expected Output**:
```
🔐 Iniciando sesión como testuser...
✅ Sesión iniciada

📝 Creando viaje 1: Vía Verde del Aceite...
{
  "success": true,
  "data": {
    "trip_id": "...",
    "title": "Vía Verde del Aceite - Jaén a Córdoba",
    ...
  }
}

📝 Creando viaje 2: Ruta Bikepacking Pirineos...
📝 Creando viaje 3: Camino de Santiago...

✅ Viajes creados exitosamente!
🌐 Ver en: http://localhost:3001/trips
```

---

## 🎯 When to Use

### ✅ Use seed scripts when:
- Setting up a new development environment
- Demonstrating features to stakeholders
- Testing frontend with realistic data
- Resetting database after tests
- Creating screenshots/documentation

### ❌ Don't use seed scripts for:
- Automated testing (use testing scripts in `scripts/testing/` instead)
- Production environments
- CI/CD pipelines (unless specifically for demo environments)

---

## 🔄 Reset and Re-seed

To clear existing data and re-seed:

```bash
# Option 1: Reset database (LOCAL-DEV with SQLite)
cd backend
rm contravento_dev.db  # Delete database
./run-local-dev.sh --setup  # Recreate with fresh data

# Option 2: Delete trips manually via API
# (See backend/docs/api/MANUAL_TESTING.md for DELETE endpoints)

# Then re-run seed script
cd ../scripts/seed
./create_test_trips.sh
```

---

## 📁 Directory Structure

```
scripts/
├── seed/                          # Sample data for development (you are here)
│   ├── README.md                  # This file
│   ├── create_test_trips.sh       # Create 3 sample trips (Linux/Mac)
│   └── create_test_trips.ps1      # Create 3 sample trips (Windows)
│
└── testing/                       # Automated testing scripts
    ├── README.md
    └── gps/
        ├── get-token.sh
        ├── test-gps-quick.sh
        └── ...
```

---

## 🆕 Adding New Seed Scripts

When creating new seed scripts, follow this naming convention:

```bash
create_<resource>_<description>.sh
create_<resource>_<description>.ps1
```

**Examples**:
- `create_test_users.sh` - Create sample users with different roles
- `create_test_photos.sh` - Upload sample photos to trips
- `create_test_tags.sh` - Create popular tags
- `create_full_dataset.sh` - Complete dataset (users + trips + photos)

**Template structure**:
```bash
#!/bin/bash
echo "🔐 Logging in..."
# Login and get session

echo "📝 Creating resource 1..."
# Create resource with curl

echo "✅ Resources created!"
```

---

## 🔗 Related Resources

### Testing Scripts
For automated testing (not seed data):
- [scripts/testing/README.md](../testing/README.md) - Testing scripts overview
- [scripts/testing/gps/](../testing/gps/) - GPS coordinates testing

### Backend Scripts
For user/admin creation:
- [backend/scripts/create_admin.py](../../backend/scripts/create_admin.py) - Create admin user
- [backend/scripts/create_verified_user.py](../../backend/scripts/create_verified_user.py) - Create test users

### API Documentation
For manual API operations:
- [backend/docs/api/MANUAL_TESTING.md](../../backend/docs/api/MANUAL_TESTING.md)
- [backend/docs/api/POSTMAN_COLLECTION.md](../../backend/docs/api/POSTMAN_COLLECTION.md)

---

## 💡 Tips

### Tip 1: Verify Data Created

After running seed scripts, verify via API:

```bash
# Get access token
cd ../testing/gps
./get-token.sh
export ACCESS_TOKEN="<token>"

# List all trips
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/users/testuser/trips | python -m json.tool
```

### Tip 2: Customize Trips

Edit the scripts to modify trip data:
- Change dates, distances, difficulty
- Add more locations
- Add different tags
- Include GPS coordinates (see GPS testing docs)

Example:
```bash
# Edit create_test_trips.sh
nano scripts/seed/create_test_trips.sh

# Modify trip 1 data
"title": "My Custom Trip",
"distance_km": 150.0,
"tags": ["custom", "modified"]
```

### Tip 3: Batch Operations

Create multiple trips quickly:

```bash
# Run seed script
./create_test_trips.sh

# Run again with different user (if you have multiple test users)
# Edit script to change username/password first
./create_test_trips.sh
```

---

## ⚠️ Important Notes

1. **User Authentication**: Scripts use `testuser` credentials by default
   - Change credentials in scripts if using different user
   - Ensure user exists before running

2. **Idempotency**: Scripts are NOT idempotent
   - Running multiple times creates duplicate trips
   - Use DELETE endpoints or reset database between runs

3. **Date Format**: Uses ISO 8601 format (`YYYY-MM-DD`)
   - Update dates if using old scripts
   - Backend validates dates cannot be in future

4. **Database Persistence**:
   - SQLite: Data persists in `backend/contravento_dev.db`
   - PostgreSQL: Data persists in Docker volume
   - Delete database file or volume to clear data

---

**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
