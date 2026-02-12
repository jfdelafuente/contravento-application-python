# Adding Photos - ContraVento

Learn how to upload, organize, and manage photos in your cycling trips.

**Audience**: End-users, cyclists documenting trips
**Difficulty**: 🟢 Basic

---

## Table of Contents

- [Overview](#overview)
- [Photo Requirements](#photo-requirements)
- [Uploading Photos](#uploading-photos)
- [Reordering Photos](#reordering-photos)
- [Adding Captions](#adding-captions)
- [Cover Photo](#cover-photo)
- [Deleting Photos](#deleting-photos)
- [Photo Gallery](#photo-gallery)
- [Troubleshooting](#troubleshooting)

---

## Overview

ContraVento allows you to document your trips visually with up to **20 photos per trip**.

**Key Features**:
- 📤 **Multiple upload methods** (drag & drop, file browser)
- 🔄 **Reorder photos** with drag and drop
- 📝 **Add captions** (optional, max 200 chars)
- 🖼️ **Cover photo** (first photo becomes trip thumbnail)
- 🗑️ **Delete photos** individually
- 🔍 **Gallery view** with lightbox for full-screen viewing
- 📱 **Automatic resizing** to 1200px width (preserves aspect ratio)

**Limits**:
- **Max photos per trip**: 20
- **Max file size**: 10MB per photo
- **Supported formats**: JPG, PNG, WebP

---

## Photo Requirements

### File Format

**Supported Formats**:
- ✅ **JPEG** (.jpg, .jpeg) - Recommended
- ✅ **PNG** (.png) - Good for screenshots
- ✅ **WebP** (.webp) - Modern format, smaller files

**Not Supported**:
- ❌ **HEIC** (.heic) - iPhone Live Photos (convert to JPG first)
- ❌ **RAW** (.cr2, .nef, .arw) - Export to JPG first
- ❌ **GIF** (.gif) - No animation support
- ❌ **BMP** (.bmp) - Too large

---

### File Size

**Maximum Size**: 10MB per photo

**Recommended Sizes**:
- **Best**: 1-3MB (balance quality and upload speed)
- **Good**: 500KB-1MB (fast upload, good quality)
- **Acceptable**: 3-10MB (slow upload, high quality)

**Tips to Reduce Size**:
1. Export at 80-90% JPEG quality (visually identical, 50% smaller)
2. Resize to 1920×1080px before upload (ContraVento resizes to 1200px anyway)
3. Use online tools: tinypng.com, compressor.io

---

### Image Dimensions

**Recommended**:
- **Landscape (horizontal)**: 1920×1080px or similar (16:9 ratio)
- **Portrait (vertical)**: 1080×1920px or similar (9:16 ratio)
- **Square**: 1080×1080px (1:1 ratio)

**Automatic Processing**:
- ContraVento resizes photos to **max 1200px width**
- Aspect ratio preserved (no cropping)
- Original file saved for potential re-processing

---

## Uploading Photos

### Option 1: During Trip Creation (Wizard)

**Step 3 of Wizard**:

```
1. Create trip (Steps 1-2)
2. Reach "Fotos" step (Step 3)
3. Upload photos using methods below
4. Continue to Step 4 (Review)
```

---

### Option 2: Add Photos to Existing Trip

**Edit Mode**:

```
1. Go to trip detail page
2. Click "Editar" button (owner only)
3. Scroll to "Fotos" section
4. Upload photos
5. Click "Guardar Cambios"
```

---

### Upload Method 1: Drag & Drop

**Steps**:

```
1. Locate photos on your computer (File Explorer / Finder)
2. Select 1-20 photos
3. Drag files to the dropzone on ContraVento
4. Drop files when dropzone highlights
5. Wait for upload progress bars
```

**Visual Feedback**:

```
Dropzone (idle):
┌─────────────────────────────────────────┐
│  📷                                      │
│  Arrastra fotos aquí                    │
│  o haz clic para seleccionar            │
│                                          │
│  Máximo 20 fotos • 10MB por foto        │
└─────────────────────────────────────────┘

Dropzone (dragging):
┌─────────────────────────────────────────┐
│  ✅                                      │
│  ¡Suelta las fotos aquí!                │
│                                          │
│  5 fotos seleccionadas                  │
└─────────────────────────────────────────┘

Uploading:
┌─────────────────────────────────────────┐
│  foto1.jpg  ████████████░░░░  75%       │
│  foto2.jpg  ████████████████  100% ✅   │
│  foto3.jpg  ██░░░░░░░░░░░░░░  15%       │
└─────────────────────────────────────────┘
```

---

### Upload Method 2: File Browser

**Steps**:

```
1. Click inside the dropzone
2. File browser opens
3. Navigate to photo folder
4. Select photos:
   - Single photo: Click once
   - Multiple photos: Ctrl+Click (Windows) or Cmd+Click (Mac)
   - Range: Shift+Click first and last
5. Click "Abrir" / "Open"
6. Photos upload automatically
```

**Keyboard Shortcuts**:
- **Ctrl+A** (Windows) / **Cmd+A** (Mac): Select all photos in folder
- **Ctrl+Click**: Add/remove individual photos from selection
- **Shift+Click**: Select range of photos

---

### Upload Progress

**Per-Photo Progress**:

```
Uploading 5 photos:
┌─────────────────────────────────────────┐
│  ✅ foto1.jpg (1.2MB) - Completado      │
│  ⏳ foto2.jpg (2.5MB) - 65% (1.6MB)     │
│  ⏳ foto3.jpg (800KB) - 12% (96KB)      │
│  ⏸️  foto4.jpg (3.1MB) - En cola        │
│  ⏸️  foto5.jpg (1.9MB) - En cola        │
└─────────────────────────────────────────┘
```

**Upload Speed**:
- Fast connection (100Mbps): ~5-10 seconds per 5MB photo
- Medium connection (20Mbps): ~20-30 seconds per 5MB photo
- Slow connection (5Mbps): ~1-2 minutes per 5MB photo

**Tip**: Upload photos one at a time on slow connections for better reliability.

---

## Reordering Photos

Photos are displayed in **order** on trip detail page and public feed. The first photo is the **cover photo** (thumbnail).

### How to Reorder

**Drag and Drop**:

```
1. Go to trip edit mode
2. Scroll to "Fotos" section
3. Hover over photo thumbnail
4. Click and hold
5. Drag to new position
6. Release to drop
7. Order updates immediately
8. Click "Guardar Cambios" to persist
```

**Visual Feedback**:

```
Before drag:
┌───────┬───────┬───────┬───────┐
│   1   │   2   │   3   │   4   │
│ Cover │       │       │       │
└───────┴───────┴───────┴───────┘

During drag (moving photo 3 to position 1):
┌───────┬───────┬┄┄┄┄┄┄┄┬───────┐
│   1   │   2   ┊   ░   ┊   4   │
│       │       ┊  drag ┊       │
└───────┴───────┴┄┄┄┄┄┄┄┴───────┘
              ↑ Drop here

After drop:
┌───────┬───────┬───────┬───────┐
│   3   │   1   │   2   │   4   │
│ Cover │       │       │       │
└───────┴───────┴───────┴───────┘
```

**Important**: First photo is always the **cover photo** (trip thumbnail on feed).

---

### Reordering Strategy

**Best Practices**:

1. **Cover Photo First**:
   - Choose your best landscape shot
   - Shows essence of the trip
   - Good lighting and composition

2. **Tell a Story**:
   - Chronological order (start → end)
   - Mix wide shots and details
   - Show terrain, views, people, food, camping

3. **End Strong**:
   - Memorable final image
   - Summit view, finish line, celebration

**Example Order**:

```
1. Cover: Wide landscape of mountain range
2. Starting point: Bike loaded with gear
3. Morning: Sunrise on trail
4. Midday: Lunch break at viewpoint
5. Afternoon: Steep climb action shot
6. Evening: Camping setup
7. Night: Starry sky timelapse
8. Morning: Sunrise from tent
... (continue chronologically)
20. Finish: Tired but happy selfie
```

---

## Adding Captions

Captions help describe what's happening in each photo.

### How to Add Captions

**In Edit Mode**:

```
1. Go to trip edit mode
2. Scroll to photo
3. Click "Añadir descripción" below thumbnail
4. Type caption (max 200 characters)
5. Click outside or press Enter to save
6. Caption appears below photo on trip page
```

**Example Captions**:

```
✅ Good captions (descriptive):
- "Col d'Aubisque - 2,115m elevation, 15% gradient 🥵"
- "Lunch break at mountain refuge, best tortilla ever!"
- "Wild camping spot near Gourette - sunrise view was epic"

❌ Generic captions (not helpful):
- "Nice view"
- "Day 3"
- "Bike"
```

**Tips**:
- Mention location names
- Include elevation/distance if relevant
- Describe weather or feelings
- Use emojis sparingly (⛰️ 🚴 ☀️ ❄️)

---

### Caption Character Limit

**Maximum**: 200 characters (including spaces)

**Character Counter**:

```
Caption input:
┌───────────────────────────────────────────┐
│ Col d'Aubisque - 2,115m elevation...      │
│                                            │
│ 67/200 caracteres                          │
└───────────────────────────────────────────┘

Approaching limit (180+ characters):
┌───────────────────────────────────────────┐
│ Col d'Aubisque climb was brutal! Started  │
│ at 8am, reached summit at 2pm. 15%        │
│ gradient sections, but views from top...  │
│                                            │
│ ⚠️ 195/200 caracteres                      │
└───────────────────────────────────────────┘

Over limit (will truncate):
┌───────────────────────────────────────────┐
│ This caption is way too long and will be  │
│ truncated because it exceeds the 200...   │
│                                            │
│ ❌ 215/200 caracteres - Demasiado largo    │
└───────────────────────────────────────────┘
```

---

## Cover Photo

The **first photo** in your trip is the **cover photo** (thumbnail).

### Cover Photo Usage

**Where It Appears**:
- 📋 **Trip list** (Mis Viajes) - main thumbnail
- 🔍 **Public feed** - trip card image
- 👤 **Profile page** - recent trips grid
- 🔗 **Social media** previews (Open Graph)

### Choosing a Good Cover Photo

**Characteristics**:
- **Landscape orientation** (horizontal) preferred
- **High quality** (sharp, well-lit, good composition)
- **Representative** of the trip
- **Visually striking** (stands out in feed)

**Examples**:

```
✅ Great cover photos:
- Panoramic mountain view with bike in foreground
- Drone shot of winding road through valley
- Action shot climbing steep mountain pass
- Scenic camping spot with tent and bike

❌ Poor cover photos:
- Blurry photo
- Random detail shot (e.g., bike chain close-up)
- Dark/underexposed photo
- Vertical photo (wasted space in thumbnail)
```

### Changing Cover Photo

**Method**:

```
1. Go to trip edit mode
2. Drag desired photo to first position
3. Photo becomes new cover
4. Click "Guardar Cambios"
```

**Instant Preview**: Cover photo updates immediately in trip list.

---

## Deleting Photos

You can delete individual photos from trips you own.

### How to Delete

**In Edit Mode**:

```
1. Go to trip edit mode
2. Scroll to photo
3. Hover over thumbnail → "✕" button appears in corner
4. Click "✕" button
5. Confirmation dialog:
   ┌─────────────────────────────────────┐
   │  ¿Eliminar esta foto?               │
   │                                      │
   │  Esta acción no se puede deshacer.  │
   │                                      │
   │  [Cancelar]  [Eliminar]             │
   └─────────────────────────────────────┘
6. Click "Eliminar" to confirm
7. Photo removed from trip (not deleted from server yet)
8. Click "Guardar Cambios" to persist deletion
```

**Important**:
- Deletion is **permanent** after saving
- Cannot undo after clicking "Guardar Cambios"
- Photo file is deleted from storage

---

### Delete Multiple Photos

**Batch Delete**:

```
1. Delete photos one by one (no bulk select yet)
2. Each deletion is immediate in UI
3. Click "Guardar Cambios" once to persist all deletions
```

**Future Feature**: Checkbox selection for bulk delete (planned).

---

## Photo Gallery

Trip detail page displays photos in a **responsive gallery** with lightbox.

### Gallery Layout

**Desktop (3 columns)**:

```
┌────────┬────────┬────────┐
│ Photo1 │ Photo2 │ Photo3 │
│        │        │        │
└────────┴────────┴────────┘
┌────────┬────────┬────────┐
│ Photo4 │ Photo5 │ Photo6 │
│        │        │        │
└────────┴────────┴────────┘
```

**Tablet (2 columns)**:

```
┌────────┬────────┐
│ Photo1 │ Photo2 │
│        │        │
└────────┴────────┘
┌────────┬────────┐
│ Photo3 │ Photo4 │
│        │        │
└────────┴────────┘
```

**Mobile (1 column)**:

```
┌────────┐
│ Photo1 │
│        │
└────────┘
┌────────┐
│ Photo2 │
│        │
└────────┘
```

---

### Lightbox View

**Click on Photo**:

```
Opens full-screen lightbox:
┌─────────────────────────────────────────┐
│ [←]              Photo 3/20         [✕] │
│                                          │
│                                          │
│         ┌──────────────────┐            │
│         │                  │            │
│         │   Full-size      │            │
│         │   Photo          │            │
│         │                  │            │
│         └──────────────────┘            │
│                                          │
│  Caption: Col d'Aubisque summit view    │
│                                          │
│ [←]                              [→]     │
└─────────────────────────────────────────┘
```

**Navigation**:
- **[←] [→]**: Previous/Next photo
- **[✕]**: Close lightbox
- **Keyboard**:
  - Left/Right arrows: Navigate
  - Esc: Close
  - Space: Next photo
- **Swipe** (mobile): Left/right to navigate

---

## Troubleshooting

### "File too large" Error (>10MB)

**Cause**: Photo exceeds 10MB limit

**Solution**:

1. **Compress photo** before upload:
   - Online: tinypng.com, compressor.io
   - Windows: Right-click → Send to → Compressed folder
   - Mac: Preview → Export → Reduce quality to 80%

2. **Resize photo**:
   - Recommended: 1920×1080px (Full HD)
   - Online: iloveimg.com/resize-image

3. **Change format**:
   - PNG → JPEG (often 50-70% smaller)

**Example**:
```
Before: photo.png - 15MB (4000×3000px)
After:  photo.jpg - 2.5MB (1920×1080px, 85% quality)
Result: Visually identical, 83% smaller
```

---

### "Invalid file format" Error

**Cause**: Uploaded file is not JPG/PNG/WebP

**Common Mistakes**:
- **HEIC** (iPhone Live Photos)
- **RAW** (camera raw files)
- **GIF** (animated images)

**Solution**:

1. **Convert to JPG**:
   - iPhone: Settings → Camera → Formats → "Most Compatible"
   - Online: cloudconvert.com (HEIC → JPG)
   - Photoshop/Lightroom: Export as JPEG

2. **Export from RAW**:
   - Lightroom: Export → JPEG (quality 80-90)
   - Camera software: Export as JPEG

---

### "Maximum 20 photos" Error

**Cause**: Trip already has 20 photos (limit reached)

**Solution**:

1. **Delete old photos**:
   - Edit trip
   - Delete photos you don't need
   - Save changes
   - Upload new photos

2. **Replace photos**:
   - Delete low-quality photos first
   - Upload better alternatives

**Why the Limit?**:
- Performance: Faster page loads
- Storage: Fair usage across users
- UX: 20 photos is enough to tell a story

**Future**: Limit may increase to 30-50 photos based on feedback.

---

### Photos Upload Slowly

**Cause**: Large files, slow connection, or server load

**Solution**:

1. **Compress photos** before upload (see above)

2. **Upload one at a time** instead of batch:
   - Select 1 photo
   - Wait for 100% upload
   - Select next photo
   - Repeat

3. **Check connection**:
   - Run speed test: fast.com
   - Close other apps using bandwidth
   - Try wired connection instead of WiFi

4. **Upload during off-peak hours**:
   - Morning/afternoon (weekdays) → Less traffic
   - Evening/weekend → More traffic

---

### Photos Appear Rotated/Sideways

**Cause**: EXIF orientation not preserved

**Solution**:

1. **Rotate before upload**:
   - Windows: Right-click → Rotate left/right
   - Mac: Preview → Tools → Rotate
   - Online: iloveimg.com/rotate-image

2. **Re-upload rotated photo**:
   - Delete incorrect photo
   - Upload rotated version

**Why This Happens**:
- Some cameras store orientation in EXIF metadata
- Web browsers may not respect EXIF orientation
- ContraVento preserves EXIF but not all browsers display correctly

---

### Photo Quality Looks Worse After Upload

**Expected Behavior**: ContraVento resizes photos to **1200px width** for performance.

**Solutions**:

1. **Upload high-quality originals**:
   - Start with 1920×1080px or higher
   - 85-95% JPEG quality

2. **Avoid pre-compression**:
   - Don't compress before upload
   - Let ContraVento resize automatically

3. **Check original**:
   - Download original GPX includes original photo metadata
   - Original photo stored on server (may add "Download original" feature later)

**Trade-off**: Smaller files = faster page loads, but slightly lower quality.

---

### Cover Photo Not Updating

**Cause**: Cache or not saved

**Solution**:

1. **Hard refresh** browser:
   - Windows: Ctrl+Shift+R
   - Mac: Cmd+Shift+R

2. **Clear browser cache**:
   - Chrome: Settings → Privacy → Clear browsing data
   - Select "Cached images and files"

3. **Verify saved**:
   - After reordering, click "Guardar Cambios"
   - Wait for success message

---

## Related Guides

- **[Creating Trips](creating-trips.md)** - Trip creation wizard
- **[Uploading GPX](uploading-gpx.md)** - Add GPS routes
- **[Public Feed](../social/public-feed.md)** - How photos appear in feed
- **[Editing Profile](../profile/editing-profile.md)** - Profile photo upload

---

## Related Documentation

- **[API: Trips Endpoints](../../api/endpoints/trips.md)** - Photo upload API
- **[Manual Testing: Trips Testing](../../testing/manual-qa/trips-testing.md)** - QA for photo gallery
- **[Frontend: Photo Components](../../architecture/frontend/patterns.md)** - Technical implementation

---

**Last Updated**: 2026-02-07
**Difficulty**: 🟢 Basic
**Estimated Reading Time**: 10 minutes
