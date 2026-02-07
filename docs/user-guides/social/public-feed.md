# Public Feed - ContraVento

Discover cycling trips from the community and get inspired for your next adventure.

**Audience**: End-users, cyclists discovering routes
**Difficulty**: 🟢 Basic

---

## Table of Contents

- [Overview](#overview)
- [Accessing the Public Feed](#accessing-the-public-feed)
- [Feed Layout](#feed-layout)
- [Filtering Trips](#filtering-trips)
- [Search Functionality](#search-functionality)
- [Interacting with Trips](#interacting-with-trips)
- [Feed Algorithm](#feed-algorithm)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **Public Feed** displays published trips from all ContraVento users, allowing you to:

- 🔍 **Discover routes** in new locations
- 🏷️ **Filter by tags** (bikepacking, gravel, road, etc.)
- 🗺️ **Explore destinations** through trip photos and maps
- 💬 **Engage** with comments and likes
- 👥 **Follow users** whose trips inspire you
- 📊 **Find popular trips** by likes and comments

**Key Features**:
- Only shows **published trips** (drafts are private)
- Real-time updates as new trips are published
- Responsive grid layout (desktop, tablet, mobile)
- Infinite scroll for seamless browsing

---

## Accessing the Public Feed

### From Navigation Bar

**Steps**:

```
1. Click "Feed Público" in top navigation bar

2. Feed page loads with recent trips

3. Scroll to browse more trips
```

**Direct URL**: `https://contravento.com/feed` or `/feed`

---

### Default View

When you first access the feed, you see:

- **All published trips** (no filters applied)
- **Most recent first** (chronological order)
- **20 trips per page** (load more on scroll)

---

## Feed Layout

### Desktop Grid (3 columns)

```
┌─────────────┬─────────────┬─────────────┐
│  Trip Card  │  Trip Card  │  Trip Card  │
│  Photo      │  Photo      │  Photo      │
│  Title      │  Title      │  Title      │
│  Author     │  Author     │  Author     │
│  ❤️ 12 💬 5 │  ❤️ 8 💬 3  │  ❤️ 15 💬 7 │
│  #gravel    │  #bikep...  │  #road      │
└─────────────┴─────────────┴─────────────┘
┌─────────────┬─────────────┬─────────────┐
│  Trip Card  │  Trip Card  │  Trip Card  │
│  ...        │  ...        │  ...        │
└─────────────┴─────────────┴─────────────┘
```

### Tablet Grid (2 columns)

```
┌─────────────┬─────────────┐
│  Trip Card  │  Trip Card  │
│  ...        │  ...        │
└─────────────┴─────────────┘
```

### Mobile Grid (1 column)

```
┌─────────────┐
│  Trip Card  │
│  ...        │
└─────────────┘
┌─────────────┐
│  Trip Card  │
│  ...        │
└─────────────┘
```

---

### Trip Card Components

Each trip card displays:

```
┌───────────────────────────────────┐
│  📷 Cover Photo                    │ ← Clickable → trip detail
│                                    │
│  BORRADOR (if draft)               │ ← Draft badge (owner only)
│                                    │
│  Ruta Bikepacking Pirineos         │ ← Title
│  por maria_garcia                  │ ← Author (clickable → profile)
│  📍 España                          │ ← Country
│  📅 1-5 Jun 2024                   │ ← Date range
│  📏 285.5 km • ⛰️ Difícil          │ ← Distance & difficulty
│                                    │
│  ❤️ 24  💬 8                       │ ← Likes & comments count
│                                    │
│  #bikepacking #montaña #pirineos   │ ← Tags (max 3 visible)
│  [+2 more]                         │ ← Expandable for more tags
└───────────────────────────────────┘
```

**Clickable Elements**:
- **Cover photo**: Opens trip detail page
- **Title**: Opens trip detail page
- **Author name**: Opens author's profile
- **Tags**: Filters feed by that tag
- **❤️ icon**: Adds like to trip (if logged in)
- **💬 icon**: Opens trip detail page (shows comments)

---

## Filtering Trips

### Filter by Tag

**Method 1: Click Tag on Trip Card**

```
1. Browse feed

2. See interesting tag (e.g., "#bikepacking")

3. Click tag

4. Feed filters to show only trips with that tag

5. Tag badge appears at top:
   ┌──────────────────────────────────┐
   │  Filtrando por: #bikepacking  ✕  │ ← Click ✕ to remove filter
   └──────────────────────────────────┘
```

**Method 2: Search Tags in Filter Bar**

```
1. Click "Filtrar" button (top-right)

2. Filter panel appears:
   ┌──────────────────────────────────┐
   │  🔍 Buscar tags...                │
   │  [                          ]    │
   │                                   │
   │  Tags populares:                 │
   │  🏷️ bikepacking (142 trips)      │
   │  🏷️ gravel (89 trips)            │
   │  🏷️ road (67 trips)              │
   │  🏷️ montaña (54 trips)           │
   └──────────────────────────────────┘

3. Click tag to filter

4. Feed updates instantly
```

---

### Multiple Tag Filtering

**Combine Tags** (AND logic):

```
1. Click first tag (e.g., "#bikepacking")

2. Feed filters to bikepacking trips

3. Click second tag (e.g., "#pirineos")

4. Feed filters to trips with BOTH tags:
   ┌───────────────────────────────────────┐
   │  Filtrando por: #bikepacking #pirineos │
   │  ✕ bikepacking  ✕ pirineos             │
   └───────────────────────────────────────┘

5. Click ✕ on any tag to remove that filter
```

**Result**: Shows trips that have **all selected tags** (intersection).

---

### Popular Tags

**Most Used Tags**:

The feed displays popular tags with trip counts:

```
┌──────────────────────────────────┐
│  Tags más usados:                │
│                                   │
│  🏷️ bikepacking      (142 trips) │
│  🏷️ gravel          (89 trips)  │
│  🏷️ road            (67 trips)  │
│  🏷️ montaña         (54 trips)  │
│  🏷️ touring         (42 trips)  │
│  🏷️ vías-verdes     (38 trips)  │
│  🏷️ mtb             (31 trips)  │
│  🏷️ urban           (24 trips)  │
│  🏷️ costa           (19 trips)  │
│  🏷️ aventura        (17 trips)  │
│                                   │
│  [Ver todos los tags]             │
└──────────────────────────────────┘
```

**Click any tag**: Feed filters to show only trips with that tag.

---

### Filter by Country (Future Feature)

**Planned**:

```
┌──────────────────────────────────┐
│  🌍 País:                         │
│  [ Todos los países ▾ ]          │
│                                   │
│  🇪🇸 España (892 trips)           │
│  🇫🇷 Francia (247 trips)          │
│  🇮🇹 Italia (189 trips)           │
│  🇵🇹 Portugal (156 trips)         │
└──────────────────────────────────┘
```

---

## Search Functionality

### Search by Title or Description

**Steps**:

```
1. Click search bar at top of feed:
   ┌──────────────────────────────────┐
   │  🔍 Buscar viajes...              │
   └──────────────────────────────────┘

2. Type search query (e.g., "Camino de Santiago")

3. Feed filters as you type (live search)

4. Results show trips with matching:
   - Title
   - Description
   - Tags
```

**Example Search Queries**:

```
Search: "pirineos"
Results: Trips with "pirineos" in title, description, or tags

Search: "bikepacking 2024"
Results: Trips with both "bikepacking" AND "2024"

Search: "gravel españa"
Results: Trips with "gravel" and "españa" (location or description)
```

---

### Search Tips

**Do**:
- ✅ Use specific terms (e.g., "Col d'Aubisque" instead of "mountain")
- ✅ Include location names (e.g., "Mallorca", "Andalucía")
- ✅ Search by difficulty (e.g., "fácil", "difícil")
- ✅ Combine tags + keywords (e.g., "#gravel mallorca")

**Don't**:
- ❌ Use too many words (slower search)
- ❌ Search for author names (use filter by author instead)
- ❌ Include special characters (%, @, #) unless searching tags

---

## Interacting with Trips

### Liking Trips

**How to Like**:

```
1. Browse feed

2. Find trip you like

3. Click ❤️ icon on trip card

4. Heart turns red and count increments:
   ❤️ 24 → ❤️ 25

5. Click again to unlike:
   ❤️ 25 → ❤️ 24 (heart turns gray)
```

**Like Visibility**:
- Your likes are **public** (visible to everyone)
- Trip author sees who liked their trip
- Likes contribute to trip popularity

---

### Commenting on Trips

**How to Comment**:

```
1. Click on trip card (or title)

2. Trip detail page opens

3. Scroll to "Comentarios" section

4. Type comment in text box

5. Click "Comentar" button

6. Comment appears immediately
```

**See**: [Commenting Guide](commenting.md) for detailed comment usage.

---

### Following Trip Authors

**How to Follow**:

```
1. Click on author's username on trip card

2. Author's profile opens

3. Click "Seguir" button

4. You now follow that author

5. Their future trips appear in your feed
```

**See**: [Following Users Guide](following-users.md) for detailed follow usage.

---

## Feed Algorithm

### Chronological Order (Default)

**Current Algorithm**:
- **Most recent first** (newest trips at top)
- No algorithmic ranking or recommendations
- All published trips appear equally
- Fair visibility for all users

**Sorting**:

```
Trip published at 14:30  ← Top
Trip published at 12:00
Trip published at 09:15
Trip published at 08:00  ← Bottom (scroll to see)
```

---

### Planned Features (Future)

**1. Personalized Feed** (based on follows):
- Trips from users you follow appear first
- Toggle between "Following" and "Everyone" tabs

**2. Trending Trips**:
- Trips with most likes/comments in last 24h
- "Trending" badge on popular trips

**3. Recommended Trips**:
- Based on your cycling type (gravel, road, MTB)
- Based on tags you frequently interact with
- Based on locations you've visited

**4. Filter by Date**:
- This week, This month, This year
- Custom date range

**5. Sort Options**:
- Most recent (default)
- Most liked
- Most commented
- Longest distance
- Highest difficulty

---

## Troubleshooting

### Feed Doesn't Load

**Possible Causes**:

1. **Network error**:
   - Check internet connection
   - Refresh page (Ctrl+R or Cmd+R)

2. **Server error**:
   - Wait 1 minute and try again
   - Check ContraVento status page (future)

3. **Too many filters**:
   - Remove some tag filters
   - Clear search query

---

### No Trips Found

**Possible Causes**:

1. **Too specific filters**:
   - Remove some tag filters
   - Try broader search terms

**Example**:
```
Filter: #bikepacking #pirineos #invierno #extremo
Result: 0 trips (too specific)

Solution: Remove #invierno and #extremo
Result: 12 trips found
```

2. **No published trips yet**:
   - ContraVento is growing, more trips coming daily
   - Try removing filters to see all trips

---

### Feed Stuck on Loading

**Cause**: Infinite scroll not triggering

**Solution**:

1. **Scroll manually** to bottom of page

2. **Click "Cargar más"** button (if visible)

3. **Hard refresh**:
   - Windows: Ctrl+Shift+R
   - Mac: Cmd+Shift+R

4. **Clear browser cache**:
   - Chrome: Settings → Privacy → Clear browsing data

---

### Trip Card Displays Incorrectly

**Possible Issues**:

1. **Missing photo**:
   - Placeholder image shows (gray box)
   - Click trip to see full details

2. **Truncated title**:
   - Long titles are truncated with "..."
   - Click trip to see full title

3. **Tags not visible**:
   - Only 3 tags shown on card
   - Click "[+2 more]" to see all tags

---

### Cannot Like Trip

**Possible Causes**:

1. **Not logged in**:
   - Solution: Log in first

2. **Own trip**:
   - Cannot like your own trips
   - Like button disabled

3. **Network error**:
   - Solution: Check connection, try again

---

### Filters Don't Work

**Cause**: JavaScript error or cache issue

**Solution**:

1. **Hard refresh** page:
   - Windows: Ctrl+Shift+R
   - Mac: Cmd+Shift+R

2. **Clear browser cache**

3. **Try different browser**:
   - Chrome, Firefox, Safari, Edge

4. **Disable browser extensions**:
   - Some ad blockers may interfere

---

### Search Results Incorrect

**Possible Issues**:

1. **Case sensitivity**:
   - Search is case-insensitive (works correctly)

2. **Partial matches**:
   - "pirin" matches "pirineos" ✅
   - "pirin" does NOT match "aspirina" ❌ (only matches start of words)

3. **Tag search**:
   - Include "#" to search tags specifically
   - Without "#", searches title and description

**Example**:
```
Search: "gravel"        → Searches title, description, tags
Search: "#gravel"       → Searches tags only
```

---

## Related Guides

- **[Commenting](commenting.md)** - How to comment on trips
- **[Following Users](following-users.md)** - How to follow trip authors
- **[Creating Trips](../trips/creating-trips.md)** - Share your own trips
- **[Getting Started](../getting-started.md)** - Platform basics

---

## Related Documentation

- **[API: Social Endpoints](../../api/endpoints/social.md)** - Feed API for developers
- **[Manual Testing: Social Testing](../../testing/manual-qa/social-testing.md)** - QA for public feed
- **[Features: Public Feed](../../features/public-feed.md)** - Feature specification

---

**Last Updated**: 2026-02-07
**Difficulty**: 🟢 Basic
**Estimated Reading Time**: 9 minutes
