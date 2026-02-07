# Stats Integration - ContraVento

Automatic user statistics updates when trips are published, edited, or deleted.

**Audience**: Backend developers, product managers

---

## Table of Contents

- [Overview](#overview)
- [Stats Update Flow](#stats-update-flow)
- [Achievement System](#achievement-system)
- [Implementation](#implementation)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)

---

## Overview

ContraVento automatically updates user statistics (**UserStats**) when trip operations are performed. The integration connects `TripService` with `StatsService` to maintain metrics synchronized in real-time.

**Key Features**:
- **Automatic Updates**: No manual stats calculation required
- **Achievement Awards**: Milestones trigger automatic badge grants
- **Idempotent Operations**: Safe to retry without duplicating stats
- **Non-Negative Protection**: Stats never go below zero
- **Historical Preservation**: Countries visited never removed

**Stats Tracked**:
- `total_trips` - Number of published trips
- `total_kilometers` - Cumulative distance
- `total_photos` - Total photos in published trips
- `countries_visited` - Unique country codes (JSON array)
- `achievements_count` - Number of achievements earned
- `last_trip_date` - Most recent trip start date
- `longest_trip_km` - Maximum single trip distance

---

## Stats Update Flow

### 1. Publish Trip

**Trigger**: When a trip in state `DRAFT` is published (changes to `PUBLISHED`)

**Method**: `StatsService.update_stats_on_trip_publish()`

**Code**: [trip_service.py:226-311](../../backend/src/services/trip_service.py#L226-L311)

**Updates**:
```python
stats.total_trips += 1
stats.total_kilometers += trip.distance_km
stats.total_photos += len(trip.photos)

# Add country if new
if country_code not in stats.countries_visited:
    stats.countries_visited.append(country_code)

# Update last trip date (most recent)
stats.last_trip_date = max(stats.last_trip_date, trip.start_date)

# Update longest trip
if trip.distance_km > stats.longest_trip_km:
    stats.longest_trip_km = trip.distance_km
```

**Additional Actions**:
- ✅ Automatically checks achievement criteria
- ✅ Awards new achievements if applicable

**Example**:
```python
# User publishes first trip: 50km, 3 photos, Spain
await trip_service.publish_trip(trip_id="abc123", user_id="user123")

# Stats after:
# total_trips: 0 → 1
# total_kilometers: 0 → 50
# total_photos: 0 → 3
# countries_visited: [] → ["ES"]
# Achievements awarded: "first_trip" ✅
```

---

### 2. Upload Photo to Published Trip

**Trigger**: Upload photo to a trip with `status=PUBLISHED`

**Method**: `TripService._update_photo_count_in_stats(user_id, increment=1)`

**Code**: [trip_service.py:417-543](../../backend/src/services/trip_service.py#L417-L543)

**Updates**:
```python
stats.total_photos += 1
```

**Note**: Only updates if `trip.status == TripStatus.PUBLISHED`

---

### 3. Delete Photo from Published Trip

**Trigger**: Delete photo from a trip with `status=PUBLISHED`

**Method**: `TripService._update_photo_count_in_stats(user_id, increment=-1)`

**Code**: [trip_service.py:545-630](../../backend/src/services/trip_service.py#L545-L630)

**Updates**:
```python
stats.total_photos -= 1  # Protected: max(0, stats.total_photos - 1)
```

---

### 4. Edit Published Trip

**Trigger**: Edit fields of a trip with `status=PUBLISHED`

**Method**: `StatsService.update_stats_on_trip_edit()`

**Code**: [trip_service.py:691-800](../../backend/src/services/trip_service.py#L691-L800)

**Updates** (recalculates delta):
```python
# Distance
stats.total_kilometers = stats.total_kilometers - old_distance + new_distance

# Photos (if modified)
stats.total_photos = stats.total_photos - old_photos_count + new_photos_count

# Country (if changed and new)
if new_country not in stats.countries_visited:
    stats.countries_visited.append(new_country)

# Longest trip (recalculate from all trips if needed)
if old_distance == stats.longest_trip_km:
    # Old longest was edited, need to recalculate
    stats.longest_trip_km = await calculate_longest_trip(user_id)
```

**Note**: Countries are never removed (preserves historical data)

---

### 5. Delete Published Trip

**Trigger**: Delete a trip with `status=PUBLISHED`

**Method**: `StatsService.update_stats_on_trip_delete()`

**Code**: [trip_service.py:802-871](../../backend/src/services/trip_service.py#L802-L871)

**Updates**:
```python
stats.total_trips = max(0, stats.total_trips - 1)
stats.total_kilometers = max(0, stats.total_kilometers - trip.distance_km)
stats.total_photos = max(0, stats.total_photos - len(trip.photos))

# countries_visited NOT modified (preserves historical data)
```

**Protections**:
- Values never go negative (uses `max(0, ...)`)
- Countries visited are maintained (historical record)

---

## Achievement System

When trips are published or edited, the system **automatically**:

1. Verifies if user meets criteria for new achievements
2. Awards applicable achievements
3. Increments `achievements_count`

### Available Achievements

#### Distance Achievements (T175)
- `first_100km`: Accumulate 100km
- `cyclist_1000km`: Accumulate 1,000km
- `explorer_5000km`: Accumulate 5,000km

#### Trip Achievements (T176)
- `first_trip`: First published trip
- `traveler_10`: 10 published trips
- `veteran_25`: 25 published trips

#### Country Achievements (T177)
- `globetrotter_5`: Visit 5 countries
- `wanderer_10`: Visit 10 countries

#### Photo Achievements (T178)
- `photographer_50`: Upload 50 photos

### Verification Code

**File**: [stats_service.py:512-532](../../backend/src/services/stats_service.py#L512-L532)

**Method**: `StatsService.check_and_award_achievements(user_id)`

**Flow**:
1. Get current user stats
2. Get all available achievements
3. Filter out already awarded achievements
4. Check criteria one by one
5. Award new achievements automatically

**Example Criteria Check**:
```python
# Distance achievement
if achievement.code == "cyclist_1000km":
    if stats.total_kilometers >= 1000:
        await award_achievement(user_id, achievement.id)

# Country achievement
if achievement.code == "globetrotter_5":
    if len(stats.countries_visited) >= 5:
        await award_achievement(user_id, achievement.id)
```

---

## Implementation

### TripService Integration

**File**: `backend/src/services/trip_service.py`

**Methods with stats integration**:

```python
async def publish_trip(trip_id: str, user_id: str) -> Trip:
    """Publish trip and update statistics."""
    # ... validation ...

    if was_draft:
        # Capture data BEFORE commit (while relationships loaded)
        distance_km = trip.distance_km or 0.0
        photos_count = len(trip.photos)
        trip_date = trip.start_date
        country_code = "ES"  # TODO: Extract from geocoding

        # Update trip status
        trip.status = TripStatus.PUBLISHED
        trip.published_at = datetime.now(UTC)
        await self.db.commit()

        # Update stats
        stats_service = StatsService(self.db)
        await stats_service.update_stats_on_trip_publish(
            user_id=user_id,
            distance_km=distance_km,
            country_code=country_code,
            photos_count=photos_count,
            trip_date=trip_date,
        )

        logger.info(f"Published trip {trip_id} and updated user stats")

    return trip


async def upload_photo(...) -> TripPhoto:
    """Upload photo and update stats if trip published."""
    # ... upload logic ...

    # Update stats if trip is published
    if trip.status == TripStatus.PUBLISHED:
        await self._update_photo_count_in_stats(user_id, increment=1)
        logger.info(f"Incremented photo count in stats for user {user_id}")

    return photo


async def delete_photo(...) -> dict:
    """Delete photo and update stats if trip published."""
    # ... delete logic ...

    # Update stats if trip is published
    if trip.status == TripStatus.PUBLISHED:
        await self._update_photo_count_in_stats(user_id, increment=-1)
        logger.info(f"Decremented photo count in stats for user {user_id}")

    return {"message": "Foto eliminada correctamente"}


async def update_trip(...) -> Trip:
    """Edit trip and recalculate stats if published."""
    # Store old values for delta calculation
    was_published = trip.status == TripStatus.PUBLISHED
    old_distance_km = trip.distance_km or 0.0
    old_photos_count = len(trip.photos)
    old_country_code = "ES"

    # ... update logic ...

    # Update stats if trip is published
    if was_published:
        stats_service = StatsService(self.db)
        await stats_service.update_stats_on_trip_edit(
            user_id=user_id,
            old_distance_km=old_distance_km,
            new_distance_km=trip.distance_km or 0.0,
            old_country_code=old_country_code,
            new_country_code="ES",
            old_photos_count=old_photos_count,
            new_photos_count=len(trip.photos),
        )
        logger.info(f"Updated trip {trip_id} and user stats")

    return trip


async def delete_trip(...) -> dict:
    """Delete trip and revert stats if published."""
    # Capture data BEFORE deletion
    was_published = trip.status == TripStatus.PUBLISHED
    distance_km = trip.distance_km or 0.0
    photos_count = len(trip.photos)
    country_code = "ES"

    # ... delete logic ...

    # Update stats if trip was published
    if was_published:
        stats_service = StatsService(self.db)
        await stats_service.update_stats_on_trip_delete(
            user_id=user_id,
            distance_km=distance_km,
            country_code=country_code,
            photos_count=photos_count,
        )
        logger.info(f"Deleted trip {trip_id} and updated user stats")

    return {"message": "Viaje eliminado correctamente"}
```

### Helper Method

**File**: [trip_service.py:873-898](../../backend/src/services/trip_service.py#L873-L898)

```python
async def _update_photo_count_in_stats(self, user_id: str, increment: int) -> None:
    """
    Update total_photos count in user stats.

    More efficient than recalculating all stats.
    Used by upload_photo() and delete_photo() for published trips.
    """
    from src.models.stats import UserStats

    result = await self.db.execute(
        select(UserStats).where(UserStats.user_id == user_id)
    )
    stats = result.scalar_one_or_none()

    if stats:
        # Update with non-negative protection
        stats.total_photos = max(0, stats.total_photos + increment)
        stats.updated_at = datetime.now(UTC)
        await self.db.commit()
        logger.debug(f"Updated photo count for user {user_id}: {increment:+d}")
    else:
        logger.warning(f"Stats not found for user {user_id}, cannot update photo count")
```

---

## API Reference

### Get User Stats

**Endpoint**: `GET /users/{username}/stats`

**Authentication**: Optional (public endpoint)

**Response**:
```json
{
  "success": true,
  "data": {
    "total_trips": 5,
    "total_kilometers": 327.5,
    "total_photos": 12,
    "longest_trip_km": 120.0,
    "countries_visited": [
      {"code": "ES", "name": "España"},
      {"code": "FR", "name": "Francia"}
    ],
    "achievements_count": 2,
    "last_trip_date": "2024-05-20"
  }
}
```

### Verify Achievement Award

**Internal Method**: `StatsService.check_and_award_achievements(user_id)`

Called automatically after:
- `publish_trip()`
- `update_trip()` (if stats changed)

**Example**:
```python
# After publishing first trip
achievements = await stats_service.check_and_award_achievements(user_id)
# Returns: [Achievement(code="first_trip", ...)]
```

---

## Best Practices

### 1. Capture Data Before Commit

```python
# ✅ GOOD - Capture while relationships loaded
distance_km = trip.distance_km
photos_count = len(trip.photos)  # Relationship loaded
await self.db.commit()
await stats_service.update_stats(distance_km, photos_count)

# ❌ BAD - Lazy loading error after commit
await self.db.commit()
photos_count = len(trip.photos)  # Error: relationship not loaded
```

### 2. Use Delta Calculations for Edits

```python
# ✅ GOOD - Delta calculation (efficient)
old_distance = 100
new_distance = 150
stats.total_kilometers += (new_distance - old_distance)

# ❌ BAD - Recalculate all trips (slow)
stats.total_kilometers = sum(t.distance_km for t in all_trips)
```

### 3. Protect Against Negative Values

```python
# ✅ GOOD - Non-negative protection
stats.total_trips = max(0, stats.total_trips - 1)

# ❌ BAD - Can go negative
stats.total_trips -= 1  # Could become -1 if data inconsistent
```

### 4. Preserve Historical Data

```python
# ✅ GOOD - Countries never removed
if country_code not in stats.countries_visited:
    stats.countries_visited.append(country_code)

# ❌ BAD - Removing countries loses history
if trip_deleted:
    stats.countries_visited.remove(country_code)  # Don't do this
```

### 5. Only Update for Published Trips

```python
# ✅ GOOD - Check status before updating
if trip.status == TripStatus.PUBLISHED:
    await update_stats()

# ❌ BAD - Update for drafts (incorrect)
await update_stats()  # Updates even for drafts
```

---

## Known Limitations

### 1. Country Detection

**Current**: Hardcoded to `"ES"` (Spain)

**TODO**: Implement automatic extraction from trip locations when geocoding is complete

```python
# Current implementation
country_code = "ES"  # Hardcoded

# Future implementation
country_code = await extract_country_from_location(trip.locations[0])
```

### 2. Countries Never Removed

**Reason**: Preserves historical data (user visited a country even if trip deleted)

**Tradeoff**: `countries_visited` count may be higher than actual current trips

**Workaround**: For exact count, query all trip locations:
```python
current_countries = await get_countries_from_all_trips(user_id)
```

### 3. Only Published Trips Counted

**Design Decision**: Draft trips don't affect stats

**Rationale**:
- Drafts are incomplete/unvalidated
- Only public-facing trips should count
- Prevents gaming stats with unpublished content

---

## Related Documentation

- **[Backend Architecture](../architecture/backend/overview.md)** - Service Layer patterns
- **[Service Layer](../architecture/backend/services.md)** - StatsService implementation
- **[Travel Diary](travel-diary.md)** - Trip operations that trigger stats
- **[API Reference](../api/endpoints/trips.md)** - Trip API endpoints

---

**Last Updated**: 2026-02-07
**Status**: ✅ Complete
**Commit**: `92e3173` - feat: integrate user statistics updates with trip operations
