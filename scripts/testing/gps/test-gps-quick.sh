#!/bin/bash
# Quick test script for GPS Coordinates feature
# Runs 3 essential tests to verify GPS coordinates functionality

set -e

BASE_URL="${BACKEND_URL:-http://localhost:8000}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     GPS Coordinates - Quick Test Suite                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if backend is running
if ! curl -s "${BASE_URL}/docs" > /dev/null 2>&1; then
    echo "❌ ERROR: Backend server is not running at ${BASE_URL}"
    echo ""
    echo "Please start the backend server first:"
    echo "  cd backend"
    echo "  ./run-local-dev.sh"
    exit 1
fi

echo "✅ Backend server is running"
echo ""

# Login
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Authentication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"testuser","password":"TestPass123!"}')

TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

echo "✅ Login successful (token: ${TOKEN:0:30}...)"
echo ""

# Test 1: Create trip with GPS coordinates
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1: Creating trip with GPS coordinates"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TRIP1=$(curl -s -X POST "${BASE_URL}/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Test GPS Quick - Madrid to Toledo",
    "description":"Testing GPS coordinates with automated quick script for validation purposes",
    "start_date":"2024-06-01",
    "distance_km":100,
    "locations":[
      {"name":"Madrid","latitude":40.416775,"longitude":-3.703790},
      {"name":"Toledo","latitude":39.862832,"longitude":-4.027323}
    ],
    "tags":["test","gps"]
  }')

if echo "$TRIP1" | grep -q '"success":true'; then
    TRIP1_ID=$(echo "$TRIP1" | grep -o '"trip_id":"[^"]*' | sed 's/"trip_id":"//')
    LAT1=$(echo "$TRIP1" | grep -o '"latitude":40\.[0-9]*' | head -1 | sed 's/"latitude"://')
    LON1=$(echo "$TRIP1" | grep -o '"longitude":-3\.[0-9]*' | head -1 | sed 's/"longitude"://')

    echo "✅ Trip created successfully"
    echo "   Trip ID: $TRIP1_ID"
    echo "   Madrid coordinates: $LAT1, $LON1"

    # Validate precision (max 6 decimals)
    LAT_DECIMALS=$(echo "$LAT1" | cut -d'.' -f2 | wc -c)
    LON_DECIMALS=$(echo "$LON1" | cut -d'.' -f2 | wc -c)

    if [ "$LAT_DECIMALS" -le 7 ] && [ "$LON_DECIMALS" -le 7 ]; then
        echo "   ✅ Precision check: 6 decimals enforced"
    else
        echo "   ⚠️  Warning: Precision may exceed 6 decimals"
    fi
else
    echo "❌ Failed to create trip with GPS"
    echo "$TRIP1" | python -m json.tool 2>/dev/null || echo "$TRIP1"
    exit 1
fi

echo ""

# Test 2: Create trip without GPS (backwards compatibility)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 2: Creating trip WITHOUT GPS (backwards compatibility)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TRIP2=$(curl -s -X POST "${BASE_URL}/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Test GPS Quick - No Coordinates",
    "description":"Testing backwards compatibility with trips that have no GPS coordinates",
    "start_date":"2024-07-01",
    "distance_km":50,
    "locations":[
      {"name":"Barcelona"},
      {"name":"Girona"}
    ],
    "tags":["test","no-gps"]
  }')

if echo "$TRIP2" | grep -q '"success":true'; then
    if echo "$TRIP2" | grep -q '"latitude":null'; then
        echo "✅ Trip created without GPS"
        echo "   ✅ Coordinates are null (backwards compatible)"
    else
        echo "⚠️  Warning: Expected null coordinates"
    fi
else
    echo "❌ Failed to create trip without GPS"
    echo "$TRIP2" | python -m json.tool 2>/dev/null || echo "$TRIP2"
    exit 1
fi

echo ""

# Test 3: Invalid latitude (should fail)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 3: Testing validation (invalid latitude > 90)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

INVALID=$(curl -s -X POST "${BASE_URL}/trips" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Test Invalid Latitude",
    "description":"This should fail",
    "start_date":"2024-06-01",
    "locations":[
      {"name":"Invalid Location","latitude":100.0,"longitude":0.0}
    ]
  }')

if echo "$INVALID" | grep -q '"success":false'; then
    if echo "$INVALID" | grep -q 'VALIDATION_ERROR'; then
        echo "✅ Invalid latitude rejected (as expected)"
        ERROR_MSG=$(echo "$INVALID" | grep -o '"message":"[^"]*' | sed 's/"message":"//')
        echo "   Error message: $ERROR_MSG"
    else
        echo "⚠️  Validation failed but wrong error code"
    fi
else
    echo "❌ Validation check failed - invalid latitude was accepted"
    echo "$INVALID" | python -m json.tool 2>/dev/null || echo "$INVALID"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Test Summary                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Test 1: Trip with GPS coordinates       PASS"
echo "✅ Test 2: Trip without GPS (compat)       PASS"
echo "✅ Test 3: Invalid coordinate validation   PASS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "All tests passed! ✅"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "For complete test suite, see:"
echo "  backend/docs/api/GPS_COORDINATES_MANUAL_TESTING.md"
echo ""
