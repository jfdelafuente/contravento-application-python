# Testing Scripts

Interactive validation and testing scripts for ContraVento features.

## Available Scripts

### Feature 018 - Activity Stream Feed

**validate_activity_feed.py** - Complete end-to-end validation of Activity Stream Feed

```bash
poetry run python scripts/testing/validate_activity_feed.py
```

**What it validates**:
- ✅ Database migration (activity_feed_items table)
- ✅ TRIP_PUBLISHED trigger (automatic activity creation on trip publish)
- ✅ PHOTO_UPLOADED trigger (automatic activity creation on photo upload)
- ✅ ACHIEVEMENT_UNLOCKED trigger (automatic activity creation on achievement)
- ✅ Activity Feed API (GET /activity-feed endpoint)
- ✅ Cursor-based pagination (multi-page navigation)

**Output**: Interactive console output showing validation progress and results.

---

### Feature 003 - GPS Routes

**check_gpx_trips.py** - Check GPX file processing and trip statistics

```bash
poetry run python scripts/testing/check_gpx_trips.py
```

**test_gpx_statistics.sh** / **test_gpx_statistics.ps1** - Test GPX statistics calculation

```bash
# Linux/Mac
./scripts/testing/test_gpx_statistics.sh

# Windows PowerShell
.\scripts\testing\test_gpx_statistics.ps1
```

**test_route_statistics.py** - Validate route statistics calculation

```bash
poetry run python scripts/testing/test_route_statistics.py
```

---

### Feature 002 - Travel Diary

**test_tags.sh** - Interactive testing of tag filtering and categorization

```bash
./scripts/testing/test_tags.sh
```

**Features tested**:
- Tag creation and normalization
- Tag-based trip filtering
- Status filtering (DRAFT, PUBLISHED)
- Pagination with tags

---

## Running All Validations

To validate the complete backend implementation:

```bash
# 1. Run pytest suite (unit + integration tests)
poetry run pytest --cov=src --cov-report=html --cov-report=term

# 2. Run feature-specific validation scripts
poetry run python scripts/testing/validate_activity_feed.py
poetry run python scripts/testing/check_gpx_trips.py
./scripts/testing/test_tags.sh

# 3. Run manual API tests (if Postman installed)
# See backend/docs/api/MANUAL_TESTING.md
```

---

## Script Locations

- **Unit/Integration Tests**: `backend/tests/unit/` and `backend/tests/integration/`
- **Validation Scripts**: `backend/scripts/testing/` (this directory)
- **Manual Testing Guides**: `backend/docs/api/`

---

## Adding New Validation Scripts

When creating a new validation script:

1. Place it in `backend/scripts/testing/`
2. Make it executable: `chmod +x script_name.py` (Linux/Mac)
3. Add docstring with usage instructions
4. Update this README with script description
5. Follow naming convention: `validate_<feature_name>.py` or `test_<feature_name>.py`

---

## Notes

- All scripts use the development database (`contravento_dev.db`)
- Scripts create test data with timestamp-based unique identifiers to avoid conflicts
- Validation scripts are non-destructive (don't delete existing data)
- For production validation, use separate staging environment
