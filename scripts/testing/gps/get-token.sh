#!/bin/bash
# Script to get access token for ContraVento API testing
# Usage: ./get-token.sh

set -e

BASE_URL="${BACKEND_URL:-http://localhost:8000}"
USERNAME="testuser"
PASSWORD="TestPass123!"

echo "=== ContraVento - Getting Access Token ==="
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

# Login and get token
echo "Logging in as ${USERNAME}..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"login\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")

# Extract access token
TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed"
    echo ""
    echo "Response:"
    echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"
    echo ""
    echo "Make sure the test user exists. Create it with:"
    echo "  cd backend"
    echo "  poetry run python scripts/create_verified_user.py"
    exit 1
fi

echo "✅ Login successful"
echo ""
echo "Access Token (first 40 chars): ${TOKEN:0:40}..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "To use the token, run this command:"
echo ""
echo "  export ACCESS_TOKEN=\"${TOKEN}\""
echo ""
echo "Or copy this for convenience:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "export ACCESS_TOKEN=\"${TOKEN}\""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Token expires in 1 hour. Re-run this script to refresh."
echo ""
