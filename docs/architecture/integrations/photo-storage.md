# Photo Storage - ContraVento

Comprehensive documentation of photo upload, processing, and storage integration for profile and trip photos.

**Audience**: Backend developers, DevOps engineers, frontend developers

---

## Table of Contents

- [Overview](#overview)
- [Profile Photos](#profile-photos)
- [Trip Photos](#trip-photos)
- [Storage Structure](#storage-structure)
- [Image Processing](#image-processing)
- [Validation](#validation)
- [Security](#security)
- [Performance](#performance)
- [Best Practices](#best-practices)

---

## Overview

ContraVento implements a file-based photo storage system for profile photos and trip photos with automatic image processing, validation, and optimization.

**Key Features**:
- **Profile Photos**: Square crop to 400x400px (FR-013)
- **Trip Photos**: Optimized version (max 1200px width) + thumbnail (400x400px)
- **Photo Limit**: Max 6 photos per trip (changed from 20 in Feature 017)
- **Validation**: MIME type, file size, image content verification
- **Security**: No executable uploads, server-side validation, path sanitization
- **Performance**: Async processing in thread pool, JPEG optimization

**Supported Formats**: JPEG, PNG, WebP (converted to JPEG for storage)

**Max File Size**: 5MB per photo (configurable via `UPLOAD_MAX_SIZE_MB`)

---

## Profile Photos

### Upload Workflow

1. **Validate**: Check MIME type, file size (max 5MB), image content
2. **Store Original**: Save to temporary location
3. **Resize**: Crop to square (center crop) and resize to 400x400px
4. **Optimize**: Save as JPEG with 85% quality
5. **Update Database**: Store photo URL in `UserProfile.profile_photo_url`
6. **Cleanup**: Delete old photo if exists

### Implementation

**Location**: `src/services/profile_service.py`

```python
async def upload_photo(self, username: str, photo_file: UploadFile) -> dict:
    """
    Upload and process profile photo.

    - Validates photo (size, format)
    - Resizes to 400x400px
    - Stores as JPEG with optimization
    - Returns absolute URL for frontend
    """
    # Read file content
    content = await photo_file.read()
    photo_bytes = BytesIO(content)

    # Validate photo
    validate_photo(photo_bytes, photo_file.content_type, max_size_mb=5)

    # Generate filename: user_id_{uuid}.jpg
    filename = generate_photo_filename(user.id, "jpg")

    # Storage path: storage/profile_photos/{year}/{month}/
    storage_dir = Path(settings.storage_path) / "profile_photos" / datetime.now(UTC).strftime("%Y/%m")
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Async processing in thread pool (T227 - non-blocking)
    def write_and_resize():
        with open(file_path, "wb") as f:
            f.write(content)
        return resize_photo(file_path, target_size=400)

    final_path = await asyncio.to_thread(write_and_resize)

    # Generate absolute URL
    photo_url = f"{settings.backend_url}/storage/profile_photos/{year}/{month}/{filename}"

    # Update profile
    profile.profile_photo_url = photo_url
    await self.db.commit()

    return {
        "photo_url": photo_url,
        "photo_width": 400,
        "photo_height": 400,
    }
```

### Storage Path

```
storage/
└── profile_photos/
    └── {year}/
        └── {month}/
            └── {user_id}_{uuid}.jpg
```

**Example**: `storage/profile_photos/2026/02/user123_a1b2c3d4.jpg`

### Resize Algorithm

**Location**: `src/utils/file_storage.py`

```python
def resize_photo(file_path: Path, target_size: int = 400) -> Path:
    """
    Resize photo to square dimensions (center crop).

    Process:
    1. Open image and convert to RGB
    2. Crop to square (center crop if not square)
    3. Resize to target_size x target_size
    4. Save as JPEG with 85% quality + optimize flag
    """
    image = Image.open(file_path)

    # Convert RGBA to RGB (for PNG with transparency)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Center crop to square
    width, height = image.size
    if width != height:
        min_dimension = min(width, height)
        left = (width - min_dimension) // 2
        top = (height - min_dimension) // 2
        right = left + min_dimension
        bottom = top + min_dimension
        image = image.crop((left, top, right, bottom))

    # Resize to target size
    image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)

    # Save optimized JPEG
    output_path = file_path.with_suffix(".jpg")
    image.save(output_path, "JPEG", quality=85, optimize=True)

    return output_path
```

**Key Parameters**:
- **Resampling**: `LANCZOS` (high-quality downsampling)
- **JPEG Quality**: 85% (good balance of quality vs file size)
- **Optimize Flag**: Enables JPEG optimizer for smaller files

---

## Trip Photos

### Upload Workflow

1. **Validate**: Check MIME type, file size (max 5MB), image content
2. **Check Limit**: Max 6 photos per trip (FR-009, FR-010)
3. **Convert RGBA to RGB**: Handle PNG with transparency
4. **Generate Two Versions**:
   - **Optimized**: Max 1200px width, 85% quality
   - **Thumbnail**: 400x400px, 80% quality
5. **Store Files**: Save to `storage/trip_photos/{year}/{month}/{trip_id}/`
6. **Update Database**: Create `TripPhoto` record with URLs and metadata
7. **Update Stats**: Increment photo count if trip is published

### Implementation

**Location**: `src/services/trip_service.py`

```python
async def upload_photo(
    self,
    trip_id: str,
    user_id: str,
    photo_file: BinaryIO,
    filename: str,
    content_type: str,
) -> TripPhoto:
    """
    Upload a photo to trip.

    Process:
    - Validates photo format
    - Checks photo limit (max 6)
    - Generates optimized (1200px) and thumbnail (400px) versions
    - Saves to storage/trip_photos/{year}/{month}/{trip_id}/
    - Updates user stats if trip is published
    """
    # Check photo limit
    if len(trip.photos) >= 6:
        raise ValueError("Has alcanzado el límite de 6 fotos por viaje")

    # Validate content type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if content_type not in allowed_types:
        raise ValueError("Formato de archivo no soportado. Usa JPG, PNG o WebP")

    # Open and verify image
    img = Image.open(photo_file)
    img.verify()
    photo_file.seek(0)
    img = Image.open(photo_file)

    # Convert RGBA to RGB (for PNG transparency)
    if img.mode == "RGBA":
        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
        rgb_img.paste(img, mask=img.split()[3])
        img = rgb_img

    # Generate unique filename
    file_uuid = str(uuid.uuid4())

    # Storage path: storage/trip_photos/{year}/{month}/{trip_id}/
    storage_dir = Path("storage/trip_photos") / year / month / trip_id
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Resize and save optimized version (max 1200px width)
    optimized_img = img.copy()
    if optimized_img.width > 1200:
        ratio = 1200 / optimized_img.width
        new_height = int(optimized_img.height * ratio)
        optimized_img = optimized_img.resize((1200, new_height), Image.Resampling.LANCZOS)

    optimized_path = storage_dir / f"{file_uuid}_optimized.jpg"
    optimized_img.save(optimized_path, format="JPEG", quality=85, optimize=True)

    # Create thumbnail (400x400px)
    thumb_img = img.copy()
    thumb_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
    thumb_path = storage_dir / f"{file_uuid}_thumb.jpg"
    thumb_img.save(thumb_path, format="JPEG", quality=80, optimize=True)

    # Calculate next order value
    result = await self.db.execute(
        select(func.max(TripPhoto.order)).where(TripPhoto.trip_id == trip_id)
    )
    max_order = result.scalar()
    next_order = (max_order + 1) if max_order is not None else 0

    # Create database record
    photo = TripPhoto(
        trip_id=trip_id,
        photo_url=f"/storage/trip_photos/{year}/{month}/{trip_id}/{file_uuid}_optimized.jpg",
        thumb_url=f"/storage/trip_photos/{year}/{month}/{trip_id}/{file_uuid}_thumb.jpg",
        order=next_order,
        file_size=optimized_path.stat().st_size,
        width=optimized_img.width,
        height=optimized_img.height,
    )

    self.db.add(photo)
    await self.db.commit()

    # Update user stats if trip is published
    if trip.status == TripStatus.PUBLISHED:
        await self._update_photo_count_in_stats(user_id, increment=1)

    return photo
```

### Storage Path

```
storage/
└── trip_photos/
    └── {year}/
        └── {month}/
            └── {trip_id}/
                ├── {uuid}_optimized.jpg  (max 1200px width)
                └── {uuid}_thumb.jpg      (400x400px)
```

**Example**:
```
storage/trip_photos/2026/02/trip-uuid-123/
├── a1b2c3d4_optimized.jpg  (1200x900px, ~450 KB)
└── a1b2c3d4_thumb.jpg      (400x300px, ~80 KB)
```

### Photo Reordering

Users can reorder trip photos via drag-and-drop in the frontend:

```python
async def reorder_photos(self, trip_id: str, user_id: str, photo_order: list[str]) -> dict:
    """
    Reorder photos in trip gallery.

    Args:
        photo_order: List of photo_ids in desired order

    Process:
    1. Validate all photo_ids belong to trip
    2. Update order field for each photo (0, 1, 2, ...)
    3. Commit transaction
    """
    # Validate photo_order contains all trip's photos
    trip_photo_ids = {photo.photo_id for photo in trip.photos}
    provided_photo_ids = set(photo_order)

    if trip_photo_ids != provided_photo_ids:
        raise ValueError("ID de foto inválido: la lista contiene fotos que no pertenecen a este viaje")

    # Update order for each photo
    for new_order, photo_id in enumerate(photo_order):
        photo = await self.db.execute(select(TripPhoto).where(TripPhoto.photo_id == photo_id))
        photo.scalar_one().order = new_order

    await self.db.commit()
```

### Photo Deletion

Deleting a photo removes files and reorders remaining photos:

```python
async def delete_photo(self, trip_id: str, photo_id: str, user_id: str) -> dict:
    """
    Delete a photo from trip.

    Process:
    1. Verify ownership
    2. Delete physical files (optimized + thumbnail)
    3. Delete database record
    4. Reorder remaining photos (no gaps in order)
    5. Update user stats if trip is published
    """
    # Delete physical files
    photo_path = Path(photo.photo_url.lstrip("/"))
    thumb_path = Path(photo.thumb_url.lstrip("/"))

    if photo_path.exists():
        photo_path.unlink()
    if thumb_path.exists():
        thumb_path.unlink()

    # Remember order of deleted photo
    deleted_order = photo.order

    # Delete from database
    await self.db.delete(photo)
    await self.db.flush()

    # Reorder remaining photos (close gaps)
    remaining_photos = await self.db.execute(
        select(TripPhoto)
        .where(TripPhoto.trip_id == trip_id, TripPhoto.order > deleted_order)
        .order_by(TripPhoto.order)
    )

    for remaining_photo in remaining_photos.scalars().all():
        remaining_photo.order -= 1

    await self.db.commit()
```

---

## Storage Structure

### Directory Layout

```
storage/
├── profile_photos/
│   ├── 2026/
│   │   ├── 01/
│   │   │   ├── user1_a1b2c3d4.jpg
│   │   │   └── user2_e5f6g7h8.jpg
│   │   └── 02/
│   │       └── user3_i9j0k1l2.jpg
│   └── 2025/
│       └── 12/
│           └── user4_m3n4o5p6.jpg
└── trip_photos/
    ├── 2026/
    │   ├── 01/
    │   │   └── trip-uuid-123/
    │   │       ├── a1b2c3d4_optimized.jpg
    │   │       ├── a1b2c3d4_thumb.jpg
    │   │       ├── e5f6g7h8_optimized.jpg
    │   │       └── e5f6g7h8_thumb.jpg
    │   └── 02/
    │       └── trip-uuid-456/
    │           ├── i9j0k1l2_optimized.jpg
    │           └── i9j0k1l2_thumb.jpg
    └── 2025/
        └── 12/
            └── trip-uuid-789/
                ├── m3n4o5p6_optimized.jpg
                └── m3n4o5p6_thumb.jpg
```

### Benefits

**Organization by Date**:
- Easy to locate files for debugging
- Efficient for backups (incremental by month)
- Natural archival strategy (old photos can be moved to cold storage)

**Trip-Based Folders**:
- All photos for a trip in one directory
- Simplifies batch operations (delete trip → delete folder)
- Isolated cleanup (orphaned files easily identified)

**Unique Filenames**:
- UUIDs prevent collisions
- User/trip prefix aids debugging
- Extension standardization (always `.jpg`)

---

## Image Processing

### Pillow Library

ContraVento uses **Pillow** (PIL Fork) for all image processing operations.

**Installation**: `poetry add pillow`

**Key Operations**:
1. **Open & Verify**: `Image.open()` + `verify()`
2. **Format Conversion**: `convert("RGB")` for RGBA images
3. **Crop**: `crop((left, top, right, bottom))`
4. **Resize**: `resize((width, height), Image.Resampling.LANCZOS)`
5. **Thumbnail**: `thumbnail((max_width, max_height), Image.Resampling.LANCZOS)`
6. **Save**: `save(path, format="JPEG", quality=85, optimize=True)`

### Resampling Filters

**LANCZOS** (default for ContraVento):
- Highest quality downsampling
- Best for photos with fine details
- Slightly slower than other filters

**Alternatives** (not used):
- `NEAREST`: Fastest, lowest quality (pixelated)
- `BILINEAR`: Fast, decent quality
- `BICUBIC`: Good quality, faster than LANCZOS
- `BOX`: Good for integer scaling

**Why LANCZOS?**:
- Profile photos are 400x400 (small) → quality matters
- Trip photos are display-critical → avoid artifacts
- Performance impact minimal (<100ms extra)

### JPEG Optimization

**Quality Settings**:
- **Profile Photos**: 85% (balance quality vs size)
- **Trip Photos (Optimized)**: 85% (display quality)
- **Trip Photos (Thumbnail)**: 80% (thumbnails tolerate more compression)

**Optimize Flag**: Enables Pillow's JPEG optimizer which:
- Uses multiple passes to find optimal encoding
- Reduces file size by ~10-20% with no quality loss
- Adds ~50-100ms processing time (acceptable)

**Example File Sizes**:
- Profile photo (400x400): ~60-80 KB
- Trip photo optimized (1200x900): ~300-500 KB
- Trip photo thumbnail (400x300): ~50-80 KB

### Format Conversion

All photos are stored as **JPEG** regardless of upload format:

**Why JPEG?**:
- Wide browser support (universal)
- Good compression for photos
- No transparency needed (profile/trip photos)
- Consistent storage format (simplifies processing)

**PNG → JPEG Conversion**:
```python
# Convert RGBA (PNG with transparency) to RGB
if img.mode == "RGBA":
    # Create white background
    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
    # Paste image using alpha channel as mask
    rgb_img.paste(img, mask=img.split()[3])
    img = rgb_img
```

**WebP → JPEG Conversion**:
```python
# Pillow handles WebP → JPEG automatically
image.save(output_path, format="JPEG", quality=85, optimize=True)
```

---

## Validation

### MIME Type Validation

**Allowed Types**:
```python
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp"}
```

**Validation**:
```python
if content_type not in ALLOWED_PHOTO_TYPES:
    raise ValueError("Solo se permiten archivos JPEG, PNG y WebP")
```

**Why These Formats?**:
- **JPEG**: Most common photo format
- **PNG**: Screenshots, graphics with transparency
- **WebP**: Modern format with good compression (Chrome, Firefox support)

**Not Allowed**:
- **GIF**: Animated images not needed for profiles/trips
- **BMP**: Uncompressed, too large
- **TIFF**: Professional format, overkill for web
- **SVG**: Vector format, security risk (can contain scripts)

### File Size Validation

**Limits**:
- **Profile Photos**: 5 MB (configurable via `UPLOAD_MAX_SIZE_MB`)
- **Trip Photos**: 5 MB (same limit)

**Validation**:
```python
max_size_bytes = max_size_mb * 1024 * 1024
if file_size > max_size_bytes:
    raise ValueError(f"El archivo no puede superar {max_size_mb}MB")

if file_size == 0:
    raise ValueError("El archivo está vacío")
```

**Why 5 MB?**:
- Modern phone cameras: 2-4 MB per photo (3000x4000px)
- Professional cameras: 5-10 MB per photo
- 5 MB is generous but prevents abuse (100 MB uploads)

### Image Content Validation

**Verification**:
```python
try:
    image = Image.open(photo_bytes)
    image.verify()  # Verifies it's a valid image
    photo_bytes.seek(0)  # Reset pointer after verify
except Exception as e:
    raise ValueError("El archivo no es una imagen válida")
```

**What `verify()` Checks**:
- File header matches declared format
- Image data is not corrupted
- Dimensions are valid
- Color mode is supported

**Why This Matters**:
- Prevents uploading renamed `.exe` files as `.jpg`
- Detects truncated/corrupted images
- Protects against malformed image exploits

---

## Security

### Upload Security Best Practices

**1. Never Trust Client Data**:
```python
# BAD - Trusting client's filename
filename = photo_file.filename  # Can be "../../../etc/passwd.jpg"

# GOOD - Generate server-side filename
filename = generate_photo_filename(user.id, "jpg")  # user123_a1b2c3d4.jpg
```

**2. Validate MIME Type AND Content**:
```python
# Check Content-Type header (can be spoofed)
if content_type not in ALLOWED_PHOTO_TYPES:
    raise ValueError("Formato no soportado")

# Also verify image content (Pillow validates)
image = Image.open(photo_bytes)
image.verify()
```

**3. Path Sanitization**:
```python
# Always use Path() to normalize paths
storage_dir = Path(settings.storage_path) / "profile_photos" / year / month
# Result: /app/storage/profile_photos/2026/02 (no directory traversal)
```

**4. Limit File Size**:
```python
# Prevent DoS via huge uploads
if file_size > 5 * 1024 * 1024:
    raise ValueError("Archivo demasiado grande")
```

**5. Convert to Safe Format**:
```python
# Always save as JPEG (no executable content)
image.save(output_path, format="JPEG", quality=85, optimize=True)
```

### Common Vulnerabilities (Prevented)

**Directory Traversal** (Prevented):
```python
# Attack: filename="../../../etc/passwd.jpg"
# Defense: Generate server-side filename (UUID-based)
filename = f"{user_id}_{uuid.uuid4().hex[:8]}.jpg"
```

**File Type Spoofing** (Prevented):
```python
# Attack: Rename malware.exe → malware.jpg, set MIME type
# Defense: Pillow verify() detects non-image content
image.verify()  # Raises exception if not a valid image
```

**XXE Attacks** (Not Applicable):
```python
# SVG files can contain XML External Entities
# Defense: We don't allow SVG uploads
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp"}
```

**DoS via Large Uploads** (Prevented):
```python
# Attack: Upload 500 MB image to exhaust memory
# Defense: FastAPI enforces max body size + validation
max_size_bytes = 5 * 1024 * 1024  # 5 MB limit
```

---

## Performance

### Async Processing Pattern

**Problem**: Image processing is CPU-intensive and blocks the event loop.

**Solution**: Use `asyncio.to_thread()` to run blocking operations in thread pool.

**Implementation**:
```python
async def upload_photo(self, username: str, photo_file: UploadFile) -> dict:
    # Read file (async I/O)
    content = await photo_file.read()

    # Define blocking operation
    def write_and_resize():
        """Write file and resize - runs in thread pool."""
        with open(file_path, "wb") as f:
            f.write(content)
        return resize_photo(file_path, target_size=400)

    # Run in thread pool (non-blocking)
    final_path = await asyncio.to_thread(write_and_resize)

    # Update database (async)
    profile.profile_photo_url = photo_url
    await self.db.commit()
```

**Why This Works**:
- `asyncio.to_thread()` runs function in default thread pool (ThreadPoolExecutor)
- Other requests continue processing during image resize
- No blocking of event loop (maintains <100ms p95 latency)

**Benchmarks**:
- Sync resize (blocking): 200-300ms (blocks all requests)
- Async resize (thread pool): 200-300ms (doesn't block other requests)
- Concurrent requests: 10+ requests/sec sustained

### File Size Optimization

**Techniques**:
1. **Resize Before Store**: Don't store 4000px originals
2. **JPEG Quality**: 85% is sweet spot (visual quality vs size)
3. **Optimize Flag**: Pillow optimizer reduces size 10-20%
4. **Format Conversion**: PNG → JPEG (alpha channel not needed)

**Results**:
- Original upload: 3.2 MB (3000x4000px)
- Profile photo: 65 KB (400x400px, 85% quality)
- Trip optimized: 420 KB (1200x1600px, 85% quality)
- Trip thumbnail: 58 KB (400x533px, 80% quality)

**Storage Savings**: ~80-95% reduction from original

### Cleanup Strategy

**Profile Photo Cleanup**:
```python
async def upload_photo(self, username: str, photo_file: UploadFile) -> dict:
    # ... upload new photo ...

    # Delete old photo if exists
    if profile.profile_photo_url:
        await self._delete_photo_file(profile.profile_photo_url)

    # Update profile with new photo URL
    profile.profile_photo_url = photo_url
```

**Trip Photo Cleanup** (on trip deletion):
```python
async def delete_trip(self, trip_id: str, user_id: str) -> dict:
    # Delete all physical photo files
    for photo in trip.photos:
        photo_path = Path(photo.photo_url.lstrip("/"))
        thumb_path = Path(photo.thumb_url.lstrip("/"))

        if photo_path.exists():
            photo_path.unlink()
        if thumb_path.exists():
            thumb_path.unlink()

    # Delete trip (cascade deletes TripPhoto records)
    await self.db.delete(trip)
```

**Orphaned File Detection**:
```bash
# Find photos not referenced in database
cd backend
poetry run python scripts/storage/find_orphaned_files.py

# Output: List of orphaned files for manual cleanup
# storage/trip_photos/2025/12/trip-uuid-789/orphaned.jpg
```

---

## Best Practices

### 1. Always Validate Before Processing

```python
# ✅ GOOD - Validate first
validate_photo(photo_bytes, content_type, max_size_mb=5)
image = Image.open(photo_bytes)

# ❌ BAD - Process without validation
image = Image.open(photo_bytes)  # Could be malware disguised as image
```

### 2. Use Thread Pool for CPU-Intensive Operations

```python
# ✅ GOOD - Async processing
final_path = await asyncio.to_thread(resize_photo, file_path, 400)

# ❌ BAD - Blocking event loop
final_path = resize_photo(file_path, 400)  # Blocks all requests for 200ms
```

### 3. Generate Server-Side Filenames

```python
# ✅ GOOD - Server-generated UUID
filename = generate_photo_filename(user.id, "jpg")  # user123_a1b2c3d4.jpg

# ❌ BAD - Client-provided filename
filename = photo_file.filename  # Can be malicious path
```

### 4. Delete Old Files When Updating

```python
# ✅ GOOD - Cleanup before update
if profile.profile_photo_url:
    await self._delete_photo_file(profile.profile_photo_url)
profile.profile_photo_url = new_photo_url

# ❌ BAD - Orphaned files accumulate
profile.profile_photo_url = new_photo_url  # Old file never deleted
```

### 5. Handle Errors Gracefully

```python
# ✅ GOOD - Cleanup on error
try:
    await save_photo(file_path)
except Exception as e:
    if file_path.exists():
        file_path.unlink()  # Cleanup partial upload
    raise

# ❌ BAD - Leave corrupted files
await save_photo(file_path)  # Error leaves corrupted file
```

### 6. Use Absolute URLs for Frontend

```python
# ✅ GOOD - Absolute URL with backend base URL
photo_url = f"{settings.backend_url}/storage/profile_photos/{year}/{month}/{filename}"

# ❌ BAD - Relative path (breaks with reverse proxy)
photo_url = f"/storage/profile_photos/{year}/{month}/{filename}"
```

### 7. Enforce Photo Limits

```python
# ✅ GOOD - Check limit before processing
if len(trip.photos) >= 6:
    raise ValueError("Has alcanzado el límite de 6 fotos por viaje")

# ❌ BAD - Allow unlimited uploads (DoS risk)
# No limit check
```

### 8. Optimize JPEG Settings

```python
# ✅ GOOD - Optimized JPEG with quality balance
image.save(path, format="JPEG", quality=85, optimize=True)

# ❌ BAD - Unoptimized or too high quality
image.save(path, format="JPEG", quality=100)  # Huge file size, no visual benefit
```

### 9. Convert RGBA to RGB

```python
# ✅ GOOD - Handle transparency before JPEG conversion
if img.mode == "RGBA":
    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
    rgb_img.paste(img, mask=img.split()[3])
    img = rgb_img

# ❌ BAD - JPEG doesn't support alpha (error or black background)
image.save(path, format="JPEG")  # Fails if RGBA mode
```

### 10. Log Operations for Debugging

```python
# ✅ GOOD - Log key operations
logger.info(f"Uploaded photo {photo.photo_id} to trip {trip_id}")
logger.info(f"Deleted photo file: {file_path}")

# ❌ BAD - Silent failures
# No logging, hard to debug orphaned files
```

---

## Related Documentation

- **[Backend Architecture](../backend/overview.md)** - Complete backend architecture guide
- **[Service Layer](../backend/services.md)** - Business logic patterns
- **[Security](../backend/security.md)** - Security best practices
- **[GPX Processing](gpx-processing.md)** - File upload patterns
- **[Deployment](../../deployment/README.md)** - Storage configuration in production

---

**Last Updated**: 2026-02-07
**Status**: ✅ Complete
**Photo Limits**: Profile (1 photo), Trip (6 photos)
**Supported Formats**: JPEG, PNG, WebP → JPEG
