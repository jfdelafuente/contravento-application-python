"""
Trip API endpoints - DEPRECATED (migrated to modular routers).

This file has been split into smaller, focused modules for better maintainability:

1. trip_crud_router.py - CRUD operations and public feed
   - GET /trips/public (public feed)
   - POST /trips (create trip)
   - GET /trips/{trip_id} (get trip)
   - POST /trips/{trip_id}/publish (publish trip)
   - PUT /trips/{trip_id} (update trip)
   - DELETE /trips/{trip_id} (delete trip)

2. trip_photos_router.py - Photo management
   - POST /trips/{trip_id}/photos (upload photo)
   - DELETE /trips/{trip_id}/photos/{photo_id} (delete photo)
   - PUT /trips/{trip_id}/photos/reorder (reorder photos)

3. trip_user_router.py - User trips and tags
   - GET /users/{username}/trips (get user trips with filters)
   - GET /tags (get all tags)

4. gpx_routes.py - GPX file management (Feature 003)
   - POST /trips/{trip_id}/gpx (upload GPX)
   - GET /trips/{trip_id}/gpx (get GPX metadata)
   - DELETE /trips/{trip_id}/gpx (delete GPX)
   - GET /gpx/{gpx_file_id}/status (processing status)
   - GET /gpx/{gpx_file_id}/track (track data)
   - GET /gpx/{gpx_file_id}/download (download original)

Migration History:
- 2026-01-28: Extracted GPX endpoints to gpx_routes.py (2,487 → 1,080 lines)
- 2026-01-28: Split remaining endpoints into trip_crud_router.py, trip_photos_router.py, trip_user_router.py

DO NOT add new endpoints here - use the appropriate modular router instead.
"""

# This file is intentionally left minimal to prevent future accumulation of code.
# All functionality has been migrated to the modular routers listed above.
