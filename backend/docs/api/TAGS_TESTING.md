# Manual Testing: Tags & Categorization (Phase 6)

**Feature**: 002-travel-diary - User Story 4
**Created**: 2025-12-30
**Endpoints**:
- `GET /users/{username}/trips` - List user trips with tag/status filtering
- `GET /tags` - Get all available tags

---

## Prerequisites

### 1. Start Development Server

```bash
cd backend
poetry run uvicorn src.main:app --reload
```

### 2. Create Test User and Login

```bash
# Create verified user
poetry run python scripts/create_verified_user.py --username tag_user --email tag@example.com --password "TagTest123!"

# Login to get token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "tag_user",
    "password": "TagTest123!"
  }'
```

**Save the access_token** from response:
```bash
export TOKEN="<your_access_token_here>"
```

---

## Test Flow: Complete Tag Scenario

### Step 1: Create Trips with Different Tags

**Trip 1: Bikepacking con tags "bikepacking" y "montaña"**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Bikepacking Pirineos",
    "description": "Viaje de 5 días por los Pirineos con acampada salvaje. Paisajes increíbles y senderos técnicos.",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "distance_km": 320.5,
    "tags": ["bikepacking", "montaña"]
  }'
```

Save `trip_id` as `TRIP1_ID`

**Trip 2: Gravel con tag "gravel"**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Gravel Costa Brava",
    "description": "Recorrido de 100km por caminos de tierra y carreteras secundarias de la Costa Brava.",
    "start_date": "2024-07-15",
    "distance_km": 102.3,
    "tags": ["gravel", "costa"]
  }'
```

Save `trip_id` as `TRIP2_ID`

**Trip 3: Montaña con tag "montaña" (como borrador)**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ascenso al Tourmalet",
    "description": "Clásica subida al Col du Tourmalet. Solo borrador por ahora.",
    "start_date": "2024-08-20",
    "distance_km": 45.0,
    "tags": ["montaña", "puerto"]
  }'
```

Save `trip_id` as `TRIP3_ID`

**Trip 4: Touring sin tags específicos**

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Camino de Santiago",
    "description": "Última etapa del Camino de Santiago en bicicleta desde Sarria hasta Santiago de Compostela.",
    "start_date": "2024-09-10",
    "end_date": "2024-09-15",
    "distance_km": 115.0,
    "tags": ["touring", "camino"]
  }'
```

Save `trip_id` as `TRIP4_ID`

---

### Step 2: Publish Some Trips

**Publish Trip 1 (Bikepacking)**

```bash
curl -X POST "http://localhost:8000/trips/$TRIP1_ID/publish" \
  -H "Authorization: Bearer $TOKEN"
```

**Publish Trip 2 (Gravel)**

```bash
curl -X POST "http://localhost:8000/trips/$TRIP2_ID/publish" \
  -H "Authorization: Bearer $TOKEN"
```

**Leave Trip 3 as DRAFT** (no publicar)

**Publish Trip 4 (Touring)**

```bash
curl -X POST "http://localhost:8000/trips/$TRIP4_ID/publish" \
  -H "Authorization: Bearer $TOKEN"
```

---

### Step 3: Test GET /tags Endpoint

**Get all available tags (ordered by usage count)**

```bash
curl -X GET "http://localhost:8000/tags" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "tags": [
      {
        "tag_id": "...",
        "name": "bikepacking",
        "normalized": "bikepacking",
        "usage_count": 1,
        "created_at": "2024-..."
      },
      {
        "tag_id": "...",
        "name": "montaña",
        "normalized": "montaña",
        "usage_count": 2,
        "created_at": "2024-..."
      },
      {
        "tag_id": "...",
        "name": "gravel",
        "normalized": "gravel",
        "usage_count": 1,
        "created_at": "2024-..."
      },
      // ... otros tags
    ],
    "count": 7
  },
  "error": null
}
```

**Validation:**
- ✅ "montaña" should have `usage_count: 2` (used in Trip1 and Trip3)
- ✅ Tags ordered by usage_count descending (most popular first)
- ✅ All 7 unique tags present

---

### Step 4: Test GET /users/{username}/trips - No Filters

**Get all trips for user (default: all statuses)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "...",
        "title": "Camino de Santiago",
        "status": "PUBLISHED",
        "tags": ["touring", "camino"],
        // ...
      },
      {
        "trip_id": "...",
        "title": "Ascenso al Tourmalet",
        "status": "DRAFT",
        "tags": ["montaña", "puerto"],
        // ...
      },
      {
        "trip_id": "...",
        "title": "Ruta Gravel Costa Brava",
        "status": "PUBLISHED",
        "tags": ["gravel", "costa"],
        // ...
      },
      {
        "trip_id": "...",
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED",
        "tags": ["bikepacking", "montaña"],
        // ...
      }
    ],
    "count": 4,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Validation:**
- ✅ All 4 trips returned (PUBLISHED + DRAFT)
- ✅ Ordered by `created_at` descending (newest first)
- ✅ Each trip includes `tags` array

---

### Step 5: Test Tag Filtering (Case-Insensitive)

**Filter by tag "montaña" (should return Trip1 and Trip3)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=montaña" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "trip_id": "...",
        "title": "Ascenso al Tourmalet",
        "status": "DRAFT",
        "tags": ["montaña", "puerto"]
      },
      {
        "trip_id": "...",
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED",
        "tags": ["bikepacking", "montaña"]
      }
    ],
    "count": 2,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Test case-insensitivity:**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=MONTAÑA" \
  -H "Authorization: Bearer $TOKEN"
```

Should return **same 2 trips** (case-insensitive match)

**Filter by tag "gravel" (should return only Trip2)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=gravel" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only 1 trip with tag "gravel"

**Filter by non-existent tag "carretera"**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=carretera" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Empty trips array `"count": 0`

---

### Step 6: Test Status Filtering

**Get only PUBLISHED trips**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?status=PUBLISHED" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "title": "Camino de Santiago",
        "status": "PUBLISHED"
      },
      {
        "title": "Ruta Gravel Costa Brava",
        "status": "PUBLISHED"
      },
      {
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED"
      }
    ],
    "count": 3,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Validation:**
- ✅ Only 3 trips (Trip1, Trip2, Trip4)
- ✅ Trip3 (DRAFT) not included

**Get only DRAFT trips**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?status=DRAFT" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only 1 trip (Trip3 - "Ascenso al Tourmalet")

---

### Step 7: Test Combined Filters (Tag + Status)

**Get PUBLISHED trips with tag "montaña"**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?tag=montaña&status=PUBLISHED" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "trips": [
      {
        "title": "Ruta Bikepacking Pirineos",
        "status": "PUBLISHED",
        "tags": ["bikepacking", "montaña"]
      }
    ],
    "count": 1,
    "limit": 50,
    "offset": 0
  },
  "error": null
}
```

**Validation:**
- ✅ Only Trip1 returned (PUBLISHED + has "montaña" tag)
- ✅ Trip3 excluded (has "montaña" but is DRAFT)

---

### Step 8: Test Pagination

**Get trips with limit=2**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?limit=2" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only 2 trips (first page)

**Get next page with offset=2**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?limit=2&offset=2" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Next 2 trips (second page)

---

### Step 9: Test Edge Cases

**Non-existent user**

```bash
curl -X GET "http://localhost:8000/users/nonexistent_user/trips" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "Usuario 'nonexistent_user' no encontrado"
  }
}
```

**Status Code:** 404

**Invalid limit (>100)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?limit=150" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Validation error (limit must be ≤ 100)

**Invalid offset (negative)**

```bash
curl -X GET "http://localhost:8000/users/tag_user/trips?offset=-5" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Validation error (offset must be ≥ 0)

---

## Automated Test Script

Save this as `backend/scripts/test_tags.sh`:

```bash
#!/bin/bash

# Phase 6: Tags & Categorization Testing Script

set -e

echo "🧪 Testing Phase 6: Tags & Categorization"
echo "=========================================="

# Configuration
BASE_URL="http://localhost:8000"
USERNAME="tag_user"
EMAIL="tag@example.com"
PASSWORD="TagTest123!"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Create user and login
echo -e "\n${YELLOW}Step 1: Creating test user and logging in${NC}"
poetry run python scripts/create_verified_user.py --username "$USERNAME" --email "$EMAIL" --password "$PASSWORD" 2>/dev/null || echo "User already exists"

LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"login\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.access_token')

if [ "$TOKEN" == "null" ]; then
  echo -e "${RED}❌ Login failed${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Logged in successfully${NC}"

# Step 2: Create trips with tags
echo -e "\n${YELLOW}Step 2: Creating trips with different tags${NC}"

# Trip 1: Bikepacking
TRIP1=$(curl -s -X POST "$BASE_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Bikepacking Pirineos",
    "description": "Viaje de 5 días por los Pirineos con acampada salvaje y senderos técnicos increíbles.",
    "start_date": "2024-06-01",
    "distance_km": 320.5,
    "tags": ["bikepacking", "montaña"]
  }')

TRIP1_ID=$(echo $TRIP1 | jq -r '.data.trip_id')
echo -e "${GREEN}✅ Trip 1 created (bikepacking + montaña)${NC}"

# Trip 2: Gravel
TRIP2=$(curl -s -X POST "$BASE_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Gravel Costa Brava",
    "description": "Recorrido de 100km por caminos de tierra y carreteras secundarias de la Costa Brava.",
    "start_date": "2024-07-15",
    "distance_km": 102.3,
    "tags": ["gravel", "costa"]
  }')

TRIP2_ID=$(echo $TRIP2 | jq -r '.data.trip_id')
echo -e "${GREEN}✅ Trip 2 created (gravel + costa)${NC}"

# Trip 3: Montaña (draft)
TRIP3=$(curl -s -X POST "$BASE_URL/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ascenso al Tourmalet",
    "description": "Clásica subida al Col du Tourmalet desde Luz-Saint-Sauveur. Solo borrador por ahora.",
    "start_date": "2024-08-20",
    "distance_km": 45.0,
    "tags": ["montaña", "puerto"]
  }')

TRIP3_ID=$(echo $TRIP3 | jq -r '.data.trip_id')
echo -e "${GREEN}✅ Trip 3 created (montaña + puerto - DRAFT)${NC}"

# Step 3: Publish trips 1 and 2
echo -e "\n${YELLOW}Step 3: Publishing trips 1 and 2${NC}"

curl -s -X POST "$BASE_URL/trips/$TRIP1_ID/publish" -H "Authorization: Bearer $TOKEN" > /dev/null
echo -e "${GREEN}✅ Trip 1 published${NC}"

curl -s -X POST "$BASE_URL/trips/$TRIP2_ID/publish" -H "Authorization: Bearer $TOKEN" > /dev/null
echo -e "${GREEN}✅ Trip 2 published${NC}"

# Step 4: Test GET /tags
echo -e "\n${YELLOW}Step 4: Testing GET /tags${NC}"

TAGS=$(curl -s -X GET "$BASE_URL/tags" -H "Authorization: Bearer $TOKEN")
TAGS_COUNT=$(echo $TAGS | jq -r '.data.count')

echo -e "${GREEN}✅ Retrieved $TAGS_COUNT tags${NC}"

# Step 5: Test GET /users/{username}/trips - No filters
echo -e "\n${YELLOW}Step 5: Testing GET /users/{username}/trips (no filters)${NC}"

ALL_TRIPS=$(curl -s -X GET "$BASE_URL/users/$USERNAME/trips" -H "Authorization: Bearer $TOKEN")
ALL_COUNT=$(echo $ALL_TRIPS | jq -r '.data.count')

echo -e "${GREEN}✅ Retrieved $ALL_COUNT trips (all statuses)${NC}"

# Step 6: Test tag filtering
echo -e "\n${YELLOW}Step 6: Testing tag filtering${NC}"

MOUNTAIN_TRIPS=$(curl -s -X GET "$BASE_URL/users/$USERNAME/trips?tag=montaña" -H "Authorization: Bearer $TOKEN")
MOUNTAIN_COUNT=$(echo $MOUNTAIN_TRIPS | jq -r '.data.count')

if [ "$MOUNTAIN_COUNT" -eq "2" ]; then
  echo -e "${GREEN}✅ Tag filter 'montaña' returned 2 trips${NC}"
else
  echo -e "${RED}❌ Expected 2 trips, got $MOUNTAIN_COUNT${NC}"
fi

# Step 7: Test status filtering
echo -e "\n${YELLOW}Step 7: Testing status filtering${NC}"

PUBLISHED_TRIPS=$(curl -s -X GET "$BASE_URL/users/$USERNAME/trips?status=PUBLISHED" -H "Authorization: Bearer $TOKEN")
PUBLISHED_COUNT=$(echo $PUBLISHED_TRIPS | jq -r '.data.count')

if [ "$PUBLISHED_COUNT" -eq "2" ]; then
  echo -e "${GREEN}✅ Status filter 'PUBLISHED' returned 2 trips${NC}"
else
  echo -e "${RED}❌ Expected 2 trips, got $PUBLISHED_COUNT${NC}"
fi

# Step 8: Test combined filters
echo -e "\n${YELLOW}Step 8: Testing combined filters (tag + status)${NC}"

COMBINED=$(curl -s -X GET "$BASE_URL/users/$USERNAME/trips?tag=montaña&status=PUBLISHED" -H "Authorization: Bearer $TOKEN")
COMBINED_COUNT=$(echo $COMBINED | jq -r '.data.count')

if [ "$COMBINED_COUNT" -eq "1" ]; then
  echo -e "${GREEN}✅ Combined filter returned 1 trip (montaña + PUBLISHED)${NC}"
else
  echo -e "${RED}❌ Expected 1 trip, got $COMBINED_COUNT${NC}"
fi

# Step 9: Test pagination
echo -e "\n${YELLOW}Step 9: Testing pagination${NC}"

PAGE1=$(curl -s -X GET "$BASE_URL/users/$USERNAME/trips?limit=2" -H "Authorization: Bearer $TOKEN")
PAGE1_COUNT=$(echo $PAGE1 | jq -r '.data.count')

if [ "$PAGE1_COUNT" -eq "2" ]; then
  echo -e "${GREEN}✅ Pagination limit=2 returned 2 trips${NC}"
else
  echo -e "${RED}❌ Expected 2 trips, got $PAGE1_COUNT${NC}"
fi

echo -e "\n${GREEN}=========================================="
echo -e "✅ All Phase 6 tests completed successfully!${NC}"
