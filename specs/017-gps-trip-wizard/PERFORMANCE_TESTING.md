# GPS Trip Wizard - Performance Testing Guide

**Feature**: 017-gps-trip-wizard
**Phase**: 9 (Polish)
**Tasks**: T101, T102

---

## Overview

This guide provides instructions for validating the performance requirements of the GPS Trip Creation Wizard.

**Success Criteria**:
- **SC-002**: GPX processing completes in <2s for 10MB files
- **SC-001**: Full wizard completion takes <5 minutes

**Tools Provided**:
- ✅ `generate_xlarge_gpx.py` - Script to generate 10MB+ GPX files
- ✅ `long_route_10mb.gpx` - Pre-generated 10.4MB test file (85,000 trackpoints)
- ✅ Automated test commands with timing measurement

---

## T101: GPX Processing Performance Test

**Goal**: Verify that 10MB GPX files are analyzed in under 2 seconds.

### Prerequisites

1. Backend server running: `./run_backend.sh`
2. Valid authentication token
3. Test GPX file (10MB+)

### Generate Large GPX File

Use the provided generator script to create a 10MB+ GPX file:

```bash
cd backend/tests/fixtures/gpx

# Generate 10MB GPX file (85,000 trackpoints)
python3 generate_xlarge_gpx.py

# Output:
# ✓ Generated long_route_10mb.gpx
#   Size: 10,886,608 bytes (10.38 MB)
#   Trackpoints: 85,000
#   ✓ SUCCESS: File size ≥10 MB (required for T101)

# Verify file size
ls -lh long_route_10mb.gpx
```

**Note**: The file `long_route_10mb.gpx` is already included in the repository, but you can regenerate it if needed.

### Test Procedure

```bash
# 1. Ensure backend is running
./run_backend.sh
# Wait for "Application startup complete" message

# 2. Get authentication token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}' \
  | jq -r '.data.access_token')

echo "Token obtained: ${TOKEN:0:20}..."

# 3. Test GPX analysis with time measurement (10MB+ file)
echo "Testing GPX analysis with 10.4MB file (85,000 trackpoints)..."
time curl -X POST http://localhost:8000/gpx/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/tests/fixtures/gpx/long_route_10mb.gpx" \
  -o /dev/null -s -w "Response time: %{time_total}s\n"

# Expected: <2.000s for SC-002 compliance
```

**Alternative**: Use the convenience script included in the GPX file generator output:

```bash
# After running generate_xlarge_gpx.py, copy the test command from output:
time curl -X POST http://localhost:8000/gpx/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/tests/fixtures/gpx/long_route_10mb.gpx" \
  -o /dev/null -s -w '%{time_total}s\n'
```

### Validation

**✅ PASS**: Response time < 2.0 seconds
**❌ FAIL**: Response time >= 2.0 seconds

**Example Output**:
```
1.234s
```

### Troubleshooting

If test fails (>2s), check:

1. **File size**: Verify you're using the correct 10MB+ file
   ```bash
   ls -lh backend/tests/fixtures/gpx/long_route_10mb.gpx
   # Expected: ~10.4 MB (10,886,608 bytes)

   # If file is missing or incorrect size, regenerate:
   cd backend/tests/fixtures/gpx
   python3 generate_xlarge_gpx.py
   ```

2. **Server load**: Run test with no other processes
   ```bash
   top | grep python
   # Should show only uvicorn/FastAPI process
   ```

3. **RDP algorithm**: Verify RDP simplification is enabled
   ```python
   # In backend/src/services/gpx_service.py
   from rdp import rdp
   simplified = rdp(points, epsilon=0.0001)
   ```

4. **Database bottleneck**: Profile SQL queries
   ```bash
   # Enable SQL logging in backend/.env
   LOG_SQL=true

   # Check for slow queries in logs
   tail -f logs/app.log | grep "slow"
   ```

5. **Python version**: Ensure using Python 3.12+
   ```bash
   python3 --version
   # Expected: Python 3.12.x
   ```

---

## T102: Wizard Completion Time Test

**Goal**: Verify that a user can complete the full wizard flow in under 5 minutes.

### Prerequisites

1. Frontend server running: `./run_frontend.sh`
2. Backend server running: `./run_backend.sh`
3. Test GPX file: `backend/tests/fixtures/test-route.gpx`
4. Timer (phone, stopwatch, or browser dev tools)

### Test Procedure

**Start Timer** and perform the following steps:

1. **Navigate to wizard**
   - URL: http://localhost:5173/trips/new
   - Click "Crear Viaje con GPS"
   - Time: ~5 seconds

2. **Step 1: Upload GPX**
   - Drag `test-route.gpx` to upload area
   - Wait for telemetry preview
   - Click "Siguiente"
   - Time: ~15 seconds

3. **Step 2: Trip Details**
   - Title: Auto-populated (leave as-is)
   - Description: Type 50+ characters
     ```
     Viaje de prueba por la sierra. Ruta muy bonita con
     vistas espectaculares y buenos caminos para bikepacking.
     ```
   - Dates: Use date picker to select start/end
   - Privacy: Leave as "Público"
   - Click "Siguiente"
   - Time: ~60 seconds

4. **Step 3: Map Visualization**
   - Verify map displays route
   - Optionally zoom/pan
   - Click "Siguiente"
   - Time: ~10 seconds

5. **Step 4: POI Management**
   - Click "Añadir POI" (3 times)
   - For each POI:
     - Click map location
     - Enter name: "POI 1", "POI 2", "POI 3"
     - Select type: "Mirador"
     - Click "Guardar POI"
   - Click "Siguiente"
   - Time: ~90 seconds

6. **Step 5: Review & Publish**
   - Review summary
   - Click "Publicar Viaje"
   - Wait for success toast
   - Redirect to trip detail page
   - Time: ~20 seconds

**Stop Timer**

### Validation

**✅ PASS**: Total time < 5:00 minutes (300 seconds)
**❌ FAIL**: Total time >= 5:00 minutes

**Example Timing Breakdown**:
| Step | Expected Time | Notes |
|------|---------------|-------|
| Navigate | 5s | Initial page load |
| Step 1 (Upload) | 15s | GPX analysis |
| Step 2 (Details) | 60s | Form filling |
| Step 3 (Map) | 10s | Quick review |
| Step 4 (POIs) | 90s | 3 POIs @ 30s each |
| Step 5 (Review) | 20s | Publish + redirect |
| **Total** | **~200s** | **3:20** (well under 5min) |

### Performance Tips

1. **Use keyboard shortcuts**:
   - Tab: Navigate form fields
   - Enter: Submit forms
   - ESC: Close dialogs

2. **Skip optional steps**:
   - POI management is optional
   - End date is optional

3. **Auto-population**:
   - Title auto-filled from filename
   - Dates auto-filled from GPX timestamps

### Troubleshooting

If wizard feels slow:

1. **Check network tab** (F12 → Network):
   - GPX upload should be <1s for small files
   - API calls should be <500ms

2. **Check console errors** (F12 → Console):
   - No JavaScript errors
   - No failed API calls

3. **Check backend logs**:
   ```bash
   # In backend terminal, look for slow queries
   grep "slow" logs/app.log
   ```

4. **Disable browser extensions**:
   - Ad blockers can slow down React
   - Try incognito mode

---

## Performance Optimization Checklist

If tests fail, optimize:

### Backend
- [ ] Use RDP algorithm for trackpoint simplification
- [ ] Add database indexes on frequently queried columns
- [ ] Enable query result caching (Redis)
- [ ] Profile slow SQL queries with `EXPLAIN ANALYZE`
- [ ] Use async file I/O for GPX uploads

### Frontend
- [ ] Code-split wizard steps (lazy load)
- [ ] Memoize expensive computations (React.memo)
- [ ] Use virtual scrolling for large POI lists
- [ ] Optimize bundle size (tree-shaking)
- [ ] Use service worker for offline support

---

## CI/CD Integration

Add performance tests to GitHub Actions:

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [pull_request]

jobs:
  perf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Backend
        run: |
          cd backend
          poetry install
          poetry run alembic upgrade head

      - name: Start Backend
        run: |
          cd backend
          poetry run uvicorn src.main:app &
          sleep 5

      - name: Test GPX Processing (<2s)
        run: |
          time curl -X POST http://localhost:8000/gpx/analyze \
            -H "Authorization: Bearer $TOKEN" \
            -F "file=@backend/tests/fixtures/large-route.gpx" \
            -o /dev/null -s -w "%{time_total}\n" | \
            awk '{if ($1 > 2.0) exit 1}'
```

---

## GPX Generator Script Reference

### generate_xlarge_gpx.py

**Location**: `backend/tests/fixtures/gpx/generate_xlarge_gpx.py`

**Features**:
- Generates GPX files with configurable number of trackpoints
- Creates realistic elevation profiles (8 mountain passes)
- Simulates Trans Pyrenees route (Atlantic to Mediterranean)
- Progress indicators during generation
- Automatic file size validation
- Interactive overwrite prompt

**Default Configuration**:
```python
num_points = 85000      # 85,000 trackpoints
file_size = ~10.4 MB    # Final size
route = "Trans Pyrenees" # Simulated route
elevation_range = 200m - 2800m
```

**Basic Usage**:
```bash
cd backend/tests/fixtures/gpx
python3 generate_xlarge_gpx.py

# Output will be: long_route_10mb.gpx
```

**Programmatic Usage** (custom point count):
```python
from pathlib import Path
from generate_xlarge_gpx import generate_xlarge_gpx

# Generate file with custom size
output = Path("custom_route_15mb.gpx")
generate_xlarge_gpx(output, num_points=120000)  # ~15 MB
```

**Comparison of Available Generators**:

| Script | Points | Size | Use Case |
|--------|--------|------|----------|
| `generate_medium_gpx.py` | ~10,000 | ~1 MB | Basic functional tests |
| `generate_large_gpx.py` | 40,000 | ~5 MB | Integration tests |
| **`generate_xlarge_gpx.py`** | **85,000** | **~10.4 MB** | **Performance testing (SC-002)** |

**Performance Data**:

| Trackpoints | File Size | Generation Time | Analysis Time (target) |
|-------------|-----------|-----------------|------------------------|
| 10,000 | ~1 MB | <1s | <0.5s |
| 40,000 | ~5 MB | ~3s | <1.0s |
| 85,000 | ~10.4 MB | ~7s | <2.0s ✓ |
| 120,000 | ~15 MB | ~12s | <3.0s |

**Regeneration**:
```bash
# If file already exists, you'll be prompted:
# ⚠ File already exists: long_route_10mb.gpx (10.38 MB)
# Overwrite? (y/N): y

# Or use non-interactive mode:
yes y | python3 generate_xlarge_gpx.py
```

---

**Date**: 2026-02-01
**Feature**: 017-gps-trip-wizard
**Status**: Performance tests documented with automated tooling
**Last Updated**: 2026-02-01
