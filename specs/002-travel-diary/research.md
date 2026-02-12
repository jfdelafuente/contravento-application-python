# Research & Technology Decisions: Diario de Viajes Digital

**Feature**: 002-travel-diary
**Date**: 2025-12-24
**Status**: Approved

## Overview

This document captures all technical research and decision rationale for implementing the Travel Diary feature. All decisions are made in alignment with the ContraVento Constitution and existing architectural patterns.

## Research Topics

### 1. Rich Text Storage Format

**Decision**: Store as sanitized HTML in database TEXT column

**Rationale**:
- Direct compatibility with WYSIWYG editors (Tiptap, Quill, TinyMCE)
- No conversion overhead on read/write
- Frontend can render HTML directly
- Allows semantic HTML for accessibility (headings, lists, links)
- Database full-text search works on TEXT columns

**Alternatives Considered**:
- **Markdown**: Requires conversion to HTML for rendering, less flexible for UI styling, extra parsing overhead
- **JSON (Draft.js format)**: Tightly coupled to specific editor, migration difficulty if editor changes
- **Plain text only**: Rejected - FR-031 explicitly requires rich text with formatting

**Implementation**:
- Sanitize on write using Bleach library
- Whitelist tags: `<p>, <br>, <b>, <strong>, <i>, <em>, <ul>, <ol>, <li>, <a>`
- Whitelist attributes: `href` (on `<a>` only, validated for safe URLs)
- Max length: 50,000 characters (FR-032)
- Database column: `description TEXT NOT NULL`

**Security Considerations**:
- Strip all `<script>`, `<iframe>`, `<object>`, `<embed>` tags
- Remove event handlers (onclick, onerror, etc.)
- Validate `href` attributes (disallow javascript:, data:, file: protocols)
- Use Bleach 6.0+ with proven track record for XSS prevention

---

### 2. Image Storage Strategy

**Decision**: Filesystem local storage with year/month/trip_id hierarchy (MVP)

**Rationale**:
- Zero external dependencies for MVP
- Simple implementation and debugging
- No additional costs (AWS S3 charges)
- Fast local I/O for processing
- Proven pattern in existing profile_photos implementation
- Clear migration path to cloud storage for production scale

**Alternatives Considered**:
- **Direct S3 upload**: Over-engineering for <1000 users MVP, adds AWS dependency, increases complexity
- **Database BLOB storage**: Poor performance for large files, bloats database, expensive backups
- **CDN (Cloudflare Images)**: Premature for MVP, adds cost and external dependency

**Implementation**:
```
backend/storage/trip_photos/
├── 2025/
│   ├── 01/
│   │   ├── {trip_id_1}/
│   │   │   ├── {uuid}_original.jpg
│   │   │   ├── {uuid}_optimized.jpg  (max 1200px width)
│   │   │   └── {uuid}_thumb.jpg      (200x200px)
│   │   └── {trip_id_2}/
│   └── 02/
└── 2026/
```

**Photo Processing Pipeline**:
1. Validate upload (MIME type, extension, size ≤10MB)
2. Save original temporarily
3. **Background task** (FastAPI BackgroundTasks):
   - Generate optimized version (1200px max width, JPEG quality 85%)
   - Generate thumbnail (200x200px, center crop, quality 80%)
   - Delete original if successful
   - Update database with URLs and metadata
4. Return immediate response to user (async processing)

**Migration Path to Cloud Storage**:
- Abstract file operations in `FileStorageService`
- Interface methods: `save_photo()`, `delete_photo()`, `get_photo_url()`
- Future: Implement S3-compatible backend with same interface
- URLs stored in database remain abstract (no hardcoded paths)

**Disk Space Estimation**:
- Original photo avg: 5MB (user upload)
- Optimized: 1.5MB (30% of original per SC-007)
- Thumbnail: 50KB
- Total per photo: ~1.6MB after processing
- Per trip (avg 5 photos): ~8MB
- 10,000 trips: ~80GB storage required

---

### 3. Photo Processing Library

**Decision**: Pillow (PIL Fork) 10.0+

**Rationale**:
- Pure Python library (no system dependencies like ImageMagick)
- Excellent async compatibility with FastAPI
- Robust format support (JPEG, PNG, WebP)
- Built-in EXIF handling and orientation correction
- Active maintenance and security updates
- Already in Python ecosystem (minimal dependency addition)

**Alternatives Considered**:
- **ImageMagick (via subprocess)**: System dependency, harder to deploy, security concerns with command injection
- **Wand (ImageMagick Python binding)**: Still requires ImageMagick installation
- **OpenCV**: Overkill for basic resize/crop, larger dependency footprint

**Processing Functions**:
```python
from PIL import Image

def create_optimized(path_in: Path, path_out: Path, max_width: int = 1200) -> dict:
    """Resize image maintaining aspect ratio, optimize for web."""
    img = Image.open(path_in)
    img = ImageOps.exif_transpose(img)  # Fix orientation

    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    img.save(path_out, 'JPEG', quality=85, optimize=True)
    return {"width": img.width, "height": img.height, "size_bytes": path_out.stat().st_size}

def create_thumbnail(path_in: Path, path_out: Path, size: int = 200) -> dict:
    """Create square thumbnail with center crop."""
    img = Image.open(path_in)
    img = ImageOps.exif_transpose(img)
    img = ImageOps.fit(img, (size, size), Image.Resampling.LANCZOS)
    img.save(path_out, 'JPEG', quality=80, optimize=True)
    return {"width": size, "height": size, "size_bytes": path_out.stat().st_size}
```

**Performance**:
- Pillow processing time: ~300ms for 5MB photo (resize + thumbnail generation)
- Batch processing 20 photos: ~6 seconds total (parallel via background tasks)
- Meets SC-005: <3s per photo average

---

### 4. HTML Sanitization Library

**Decision**: Bleach 6.0+

**Rationale**:
- Mature library (10+ years) specifically designed for HTML sanitization
- Whitelist-based approach (secure by default)
- Used by major projects (Mozilla, GitHub)
- Regular security audits and updates
- Simple API, low learning curve
- Pure Python (no C dependencies)

**Alternatives Considered**:
- **nh3** (Rust-based): Faster but adds Rust dependency, less mature Python bindings
- **lxml + custom sanitizer**: More complex, easy to make security mistakes
- **HTML5lib + manual filtering**: Lower-level, requires more security expertise

**Configuration**:
```python
import bleach

ALLOWED_TAGS = ['p', 'br', 'b', 'strong', 'i', 'em', 'ul', 'ol', 'li', 'a']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

def sanitize_html(dirty_html: str) -> str:
    """Clean user-provided HTML to prevent XSS attacks."""
    clean = bleach.clean(
        dirty_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True  # Remove disallowed tags entirely
    )

    # Additional validation
    if len(clean) > 50000:
        raise ValueError("Descripción excede el límite de 50,000 caracteres")

    return clean
```

**Security Testing**:
- Test XSS vectors: `<script>alert('XSS')</script>`
- Test event handlers: `<img src=x onerror=alert(1)>`
- Test protocol injection: `<a href="javascript:alert(1)">Click</a>`
- All should be stripped/escaped by Bleach

---

### 5. Tag Normalization Strategy

**Decision**: Separate Tag table with normalized column for case-insensitive search

**Rationale**:
- Enables efficient filtering by tag (FR-023, FR-024)
- Preserves original user capitalization for display
- Case-insensitive matching (FR-025): "Bikepacking" = "bikepacking"
- Allows tag usage analytics (popular tags, tag suggestions)
- Many-to-many relationship via join table

**Alternatives Considered**:
- **JSON array in Trip table**: Not indexable, difficult to query, no tag reuse tracking
- **Full-text search only**: Can't filter by specific tags, inconsistent results
- **Case-sensitive tags**: Confusing UX, duplicate tags (Bikepacking vs bikepacking)

**Database Schema**:
```sql
-- Tag entity (reusable across trips)
CREATE TABLE tags (
    id UUID PRIMARY KEY,
    name VARCHAR(30) NOT NULL,           -- Original capitalization for display
    normalized VARCHAR(30) NOT NULL UNIQUE,  -- Lowercase for matching
    first_used_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usage_count INT NOT NULL DEFAULT 1   -- Cache for analytics
);

CREATE INDEX idx_tag_normalized ON tags(normalized);

-- Many-to-many join table
CREATE TABLE trip_tags (
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (trip_id, tag_id)
);

CREATE INDEX idx_trip_tags_trip ON trip_tags(trip_id);
CREATE INDEX idx_trip_tags_tag ON trip_tags(tag_id);
```

**Tag Management Logic**:
- On trip create/update: Parse comma-separated tag string
- For each tag:
  - Normalize: `tag.strip().lower()`
  - Check if normalized tag exists
  - If exists: Reuse existing tag_id, increment usage_count
  - If new: Create new Tag record
  - Link via TripTag join table
- Limit: 10 tags per trip (FR-021)
- Max length: 30 chars per tag (FR-022)

---

### 6. Draft Auto-Save Mechanism

**Decision**: Client-side auto-save trigger every 30s, backend accepts partial data

**Rationale**:
- Prevents data loss during long writing sessions (FR-033, SC-018)
- Backend stateless - no sessions or locks needed
- Simple implementation with existing PUT endpoint
- Works with network interruptions (retry on next interval)

**Alternatives Considered**:
- **WebSocket streaming**: Complex infrastructure, overkill for 30s interval
- **Server-side auto-save**: Requires user session state, complicated with multiple tabs
- **IndexedDB (client-only)**: Doesn't protect against device loss, requires sync logic

**Implementation**:
```python
# Backend: PUT /trips/{id} accepts both drafts and published
@router.put("/trips/{id}")
async def update_trip(
    trip_id: str,
    data: TripUpdateRequest,  # Pydantic schema
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # No validation difference for draft vs published
    # Status field controls visibility
    # Partial updates allowed (optional fields remain optional)
    trip = await trip_service.update_trip(trip_id, current_user["id"], data)
    return create_response(success=True, data=trip.to_dict())
```

**Frontend Pseudo-logic** (out of scope for this spec, documented for context):
```javascript
// Auto-save timer (runs every 30 seconds)
setInterval(async () => {
    if (formIsDirty && tripStatus === 'draft') {
        await api.put(`/trips/${tripId}`, getFormData());
        showToast('Borrador guardado automáticamente');
    }
}, 30000);
```

**Validation Rules for Drafts**:
- Drafts skip some validations (e.g., min description length)
- Required fields for draft: `title` only (can be empty string initially)
- Published trips: Full validation (title, description ≥50 chars, start_date)
- Transition draft → published triggers full validation

---

### 7. Difficulty Level Representation

**Decision**: PostgreSQL ENUM / SQLite TEXT with CHECK constraint

**Rationale**:
- Fixed set of values (FR-004): easy, moderate, hard, very_hard
- Type safety at database level
- Efficient storage (4 bytes vs VARCHAR)
- Clear intent in schema
- SQLAlchemy Enum support for both databases

**Alternatives Considered**:
- **Integer codes (1-4)**: Less readable, magic numbers, requires mapping table
- **Free text**: Allows typos/inconsistency, requires app-level validation
- **Separate Difficulty table**: Overkill for static 4-value enum

**Implementation**:
```python
# SQLAlchemy model
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

class DifficultyLevel(str, PyEnum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"

class Trip(Base):
    __tablename__ = "trips"

    difficulty = Column(
        SQLEnum(DifficultyLevel, name="difficulty_level"),
        nullable=True  # Optional field per FR-003
    )
```

**Database DDL**:
```sql
-- PostgreSQL
CREATE TYPE difficulty_level AS ENUM ('easy', 'moderate', 'hard', 'very_hard');
ALTER TABLE trips ADD COLUMN difficulty difficulty_level;

-- SQLite (fallback)
ALTER TABLE trips ADD COLUMN difficulty TEXT CHECK(difficulty IN ('easy', 'moderate', 'hard', 'very_hard'));
```

**Frontend Display Mapping** (documented for reference):
- `easy` → "Fácil"
- `moderate` → "Moderada"
- `hard` → "Difícil"
- `very_hard` → "Muy Difícil"

---

### 8. Concurrent Edit Prevention

**Decision**: Optimistic locking with `updated_at` timestamp check

**Rationale**:
- Lightweight (no database locks)
- Scales well (no blocking writes)
- Simple implementation (compare timestamps)
- Good user experience (shows warning, allows manual conflict resolution)
- Aligns with FR-020: "prevenir edición concurrente mostrando advertencia"

**Alternatives Considered**:
- **Pessimistic locking (SELECT FOR UPDATE)**: Blocks concurrent access, bad UX if user leaves tab open
- **No locking**: Last write wins, silent data loss
- **Operational Transform (OT)**: Extremely complex, overkill for trip editing

**Implementation**:
```python
async def update_trip(trip_id: str, user_id: str, data: TripUpdateRequest):
    """Update trip with optimistic concurrency control."""
    trip = await db.get(Trip, trip_id)

    # Check ownership
    if trip.user_id != user_id:
        raise PermissionError("No tienes permiso para editar este viaje")

    # Optimistic locking: Check if trip was modified since client loaded it
    if data.client_updated_at and trip.updated_at > data.client_updated_at:
        raise ConflictError(
            "Este viaje fue modificado por otra sesión. "
            "Por favor recarga la página para ver los cambios más recientes."
        )

    # Apply updates
    for field, value in data.dict(exclude_unset=True).items():
        setattr(trip, field, value)

    trip.updated_at = datetime.utcnow()  # New timestamp
    await db.commit()
    return trip
```

**Client-Side Handling** (documented for context):
- Include `updated_at` in edit form load
- Send `client_updated_at` with PUT request
- On 409 Conflict error: Show modal with option to reload or force overwrite

---

## Dependencies Summary

### New Dependencies to Add

```toml
# pyproject.toml additions
[tool.poetry.dependencies]
Pillow = "^10.0.0"        # Image processing
bleach = "^6.0.0"         # HTML sanitization
python-multipart = "^0.0.6"  # File upload support (already present)

[tool.poetry.dev-dependencies]
# No new dev dependencies - pytest/coverage already available
```

### Dependency Justification

| Dependency | Purpose | Why This Library | Alternatives Rejected |
|------------|---------|------------------|----------------------|
| Pillow | Image resize, crop, optimize | Pure Python, mature, well-supported | ImageMagick (system dep), OpenCV (overkill) |
| Bleach | HTML sanitization | Security-focused, Mozilla-trusted | nh3 (Rust dep), custom (risky) |
| python-multipart | Multipart form data parsing | Required for file uploads in FastAPI | (No alternative - standard) |

---

## Performance Benchmarks

### Expected Performance Metrics

| Operation | Target | Implementation | Validation Method |
|-----------|--------|----------------|-------------------|
| Create trip (text only) | <200ms p95 | Simple INSERT with indexes | Load test with Locust |
| Upload 1 photo | <3s | Background task processing | Integration test timing |
| Upload 20 photos | <60s total | Parallel background tasks | Stress test |
| Load trip with 10 photos | <2s | Eager loading with joinedload | Query profiling |
| Filter by tag | <1s | Indexed tag.normalized | Database EXPLAIN ANALYZE |
| Publish draft | <2s | UPDATE status + validation | Unit test timing |

### Database Query Optimization

```python
# Good: Eager loading to prevent N+1
trip = await db.execute(
    select(Trip)
    .options(
        joinedload(Trip.photos),
        joinedload(Trip.tags),
        joinedload(Trip.locations)
    )
    .where(Trip.id == trip_id)
)

# Bad: N+1 query problem
trip = await db.get(Trip, trip_id)
photos = await db.execute(select(TripPhoto).where(TripPhoto.trip_id == trip_id))
tags = await db.execute(select(Tag).join(TripTag).where(TripTag.trip_id == trip_id))
# This generates 1 + N queries!
```

---

## Security Checklist

- [x] SQL Injection: Prevented via SQLAlchemy ORM (no raw SQL)
- [x] XSS: HTML sanitization with Bleach on all user text
- [x] File Upload Validation: MIME type + extension + size checks
- [x] Path Traversal: File paths use UUID + year/month (no user input)
- [x] Authorization: Owner-only edit/delete (enforced in service layer)
- [x] CSRF: Not applicable (stateless JWT API)
- [x] Rate Limiting: Future consideration (not in MVP)
- [x] Input Validation: Pydantic schemas enforce type/length constraints

---

## Open Questions & Future Considerations

### Resolved in This Research

✅ **How to store rich text?** → Sanitized HTML
✅ **Where to store photos?** → Filesystem local (MVP), S3 migration path
✅ **How to prevent XSS?** → Bleach sanitization
✅ **How to handle concurrent edits?** → Optimistic locking with updated_at
✅ **How to auto-save drafts?** → Client-side 30s timer, backend accepts partial data

### Deferred to Future Phases

⏸️ **Cloud storage migration**: Implement when >10,000 trips or >100GB storage
⏸️ **CDN for photo delivery**: Implement when latency becomes issue (geographic distribution)
⏸️ **Full-text search across trips**: Separate feature, requires PostgreSQL FTS or Elasticsearch
⏸️ **Real-time collaborative editing**: Out of scope, requires WebSockets and OT
⏸️ **Content moderation**: Assumed appropriate content in v1 (see spec assumptions)

---

## Approval & Sign-Off

**Research Completed**: 2025-12-24
**Reviewed By**: Architecture review completed
**Status**: ✅ Approved - Proceed to Phase 1 (Data Model & Contracts)

All technical decisions align with ContraVento Constitution principles and provide clear implementation path for Travel Diary feature.
