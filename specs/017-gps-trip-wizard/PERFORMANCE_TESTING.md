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

---

## T101: GPX Processing Performance Test

**Goal**: Verify that 10MB GPX files are analyzed in under 2 seconds.

### Prerequisites

1. Backend server running: `./run_backend.sh`
2. Valid authentication token
3. Test GPX file (10MB+)

### Generate Large GPX File (Optional)

If you don't have a 10MB GPX file, you can create one:

```bash
cd backend/tests/fixtures

# Option 1: Duplicate trackpoints in existing GPX
python3 << 'PYTHON'
import xml.etree.ElementTree as ET

# Read existing GPX
tree = ET.parse('test-route.gpx')
root = tree.getroot()

# Find trackpoints
ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
trkseg = root.find('.//gpx:trkseg', ns)
trackpoints = list(trkseg.findall('gpx:trkpt', ns))

# Duplicate trackpoints to reach 10MB (~50,000 points)
target_points = 50000
while len(list(trkseg)) < target_points:
    for trkpt in trackpoints:
        trkseg.append(trkpt)
        if len(list(trkseg)) >= target_points:
            break

# Save
tree.write('large-route.gpx', encoding='utf-8', xml_declaration=True)
print(f"Created large-route.gpx with {len(list(trkseg))} trackpoints")
PYTHON

# Check file size
ls -lh large-route.gpx
```

### Test Procedure

```bash
# 1. Start backend
./run_backend.sh

# 2. Get authentication token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"AdminPass123!"}' \
  | jq -r '.access_token')

# 3. Test GPX analysis with time measurement
time curl -X POST http://localhost:8000/gpx/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/tests/fixtures/large-route.gpx" \
  -o /dev/null -s -w "%{time_total}s\n"

# Expected: <2.000s
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

1. **File size**: Ensure file is actually 10MB+
   ```bash
   ls -lh backend/tests/fixtures/large-route.gpx
   ```

2. **Server load**: Run test with no other processes
   ```bash
   top | grep python
   ```

3. **RDP algorithm**: Check if RDP is being used for simplification
   ```python
   # In backend/src/services/gpx_service.py
   from rdp import rdp
   simplified = rdp(points, epsilon=0.0001)
   ```

4. **Database bottleneck**: Profile SQL queries
   ```bash
   # Enable SQL logging in backend/.env
   LOG_SQL=true
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

**Date**: 2026-02-01
**Feature**: 017-gps-trip-wizard
**Status**: Performance tests documented
