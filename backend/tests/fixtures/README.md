# Test Fixtures

This directory contains sample data for testing ContraVento features.

## Directory Structure

```
fixtures/
├── README.md           # This file
├── users.json          # Sample user accounts
├── trips.json          # Sample trip data
├── tags.json           # Sample tags for trips
└── photos/             # Sample photos for testing uploads
    ├── sample_1.jpg    # ~500KB image
    ├── sample_2.jpg    # ~400KB image
    └── sample_large.jpg # ~5MB image (for upload limit testing)
```

## Adding Sample Photos

To complete the test setup, add sample photos to the `photos/` directory:

### Option 1: Download from internet

```bash
cd backend/tests/fixtures/photos

# Download sample images (adjust URLs as needed)
curl -o sample_1.jpg "https://picsum.photos/1200/800?random=1"
curl -o sample_2.jpg "https://picsum.photos/1200/800?random=2"
curl -o sample_large.jpg "https://picsum.photos/3000/2000?random=3"
```

### Option 2: Use existing photos

Copy any JPG photos you have available:

```bash
cp /path/to/your/photo1.jpg backend/tests/fixtures/photos/sample_1.jpg
cp /path/to/your/photo2.jpg backend/tests/fixtures/photos/sample_2.jpg
cp /path/to/your/large_photo.jpg backend/tests/fixtures/photos/sample_large.jpg
```

### Option 3: Create placeholder images (testing only)

If you don't have real images, you can create small placeholder files for basic testing:

```bash
cd backend/tests/fixtures/photos

# Create dummy files (NOT actual images, just for file size testing)
dd if=/dev/zero of=sample_1.jpg bs=1024 count=500      # 500KB
dd if=/dev/zero of=sample_2.jpg bs=1024 count=400      # 400KB
dd if=/dev/zero of=sample_large.jpg bs=1024 count=5000 # 5MB
```

**Note**: Option 3 creates non-image files. Use Option 1 or 2 for realistic testing.

## Expected File Sizes

- `sample_1.jpg`: ~500KB (within upload limits)
- `sample_2.jpg`: ~400KB (within upload limits)
- `sample_large.jpg`: ~5MB (tests upload size limit validation)

## Usage in Tests

Tests will load fixtures using pytest fixtures:

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_photo_path():
    return Path(__file__).parent / "fixtures" / "photos" / "sample_1.jpg"

async def test_photo_upload(client, sample_photo_path):
    with open(sample_photo_path, "rb") as f:
        response = await client.post("/trips/{trip_id}/photos", files={"file": f})
    assert response.status_code == 201
```

## JSON Fixtures

JSON fixtures (users.json, trips.json, tags.json) are created by Phase 2 (Foundational) tasks.
See `conftest.py` for fixture loading helpers.
