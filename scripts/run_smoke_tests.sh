#!/bin/bash
#
# Smoke Tests for ContraVento Application
#
# Tests all 4 deployment modes to verify the application starts correctly
# and critical endpoints respond.
#
# Usage:
#   ./scripts/run_smoke_tests.sh <mode>
#
# Modes:
#   local-dev      - SQLite local development (http://localhost:8000)
#   local-minimal  - PostgreSQL minimal Docker (http://localhost:8000)
#   local-full     - Full Docker stack (http://localhost:8000)
#   staging        - Staging environment (https://staging.contravento.com)
#
# Exit codes:
#   0 - All tests passed
#   1 - One or more tests failed
#   2 - Invalid arguments or configuration

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Configuration
MODE="${1:-}"
BASE_URL=""
TIMEOUT=30

# Functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  ContraVento Smoke Tests - ${1}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_test() {
    echo -e "${YELLOW}▶${NC} Running: ${1}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS${NC} - ${1}"
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
}

print_fail() {
    echo -e "${RED}❌ FAIL${NC} - ${1}"
    echo -e "${RED}   Error: ${2}${NC}"
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
}

print_summary() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Test Summary${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  Total Tests: ${TESTS_TOTAL}"
    echo -e "  ${GREEN}Passed: ${TESTS_PASSED}${NC}"
    echo -e "  ${RED}Failed: ${TESTS_FAILED}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

usage() {
    echo "Usage: $0 <mode>"
    echo ""
    echo "Modes:"
    echo "  local-dev      - SQLite local development (http://localhost:8000)"
    echo "  local-minimal  - PostgreSQL minimal Docker (http://localhost:8000)"
    echo "  local-full     - Full Docker stack (http://localhost:8000)"
    echo "  staging        - Staging environment (https://staging.contravento.com)"
    echo ""
    echo "Examples:"
    echo "  $0 local-dev"
    echo "  $0 staging"
    exit 2
}

# Validate mode argument
if [ -z "$MODE" ]; then
    echo -e "${RED}Error: Missing deployment mode${NC}"
    echo ""
    usage
fi

# Set base URL based on mode
case "$MODE" in
    local-dev|local-minimal|local-full)
        BASE_URL="http://localhost:8000"
        ;;
    staging)
        BASE_URL="https://staging.contravento.com"
        ;;
    *)
        echo -e "${RED}Error: Invalid mode '${MODE}'${NC}"
        echo ""
        usage
        ;;
esac

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is not installed${NC}"
    echo "Please install curl to run smoke tests"
    exit 2
fi

# Start tests
START_TIME=$(date +%s)
print_header "Mode: ${MODE}"
echo "Base URL: ${BASE_URL}"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Disable exit-on-error for tests (we want all tests to run)
set +e

# Test 1: Health check endpoint
print_test "Health check - GET /health"
RESPONSE=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "${BASE_URL}/health" 2>&1) || true
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" = "200" ]; then
    # Verify response contains "status" field
    if echo "$BODY" | grep -q '"status"'; then
        print_pass "Health endpoint returned 200 OK"
    else
        print_fail "Health endpoint missing 'status' field" "Response: $BODY"
    fi
elif [ -n "$HTTP_CODE" ]; then
    print_fail "Health endpoint returned HTTP $HTTP_CODE" "Expected 200"
else
    print_fail "Health endpoint request failed" "Connection timeout or network error"
fi

# Test 2: Auth endpoint - Invalid login (should return 401)
print_test "Auth endpoint - POST /auth/login (invalid credentials)"
RESPONSE=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" \
    -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"login":"invalid_user","password":"wrong_password"}' 2>&1) || true
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" = "401" ]; then
    print_pass "Auth endpoint correctly rejects invalid credentials (401)"
elif [ -n "$HTTP_CODE" ]; then
    print_fail "Auth endpoint returned HTTP $HTTP_CODE" "Expected 401 for invalid credentials"
else
    print_fail "Auth endpoint request failed" "Connection timeout or network error"
fi

# Test 3: Protected endpoint - GET /auth/me without token (should return 401)
print_test "Protected endpoint - GET /auth/me (no token)"
RESPONSE=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" \
    "${BASE_URL}/auth/me" 2>&1) || true
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" = "401" ]; then
    print_pass "Protected endpoint correctly requires authentication (401)"
elif [ -n "$HTTP_CODE" ]; then
    print_fail "Protected endpoint returned HTTP $HTTP_CODE" "Expected 401 without token"
else
    print_fail "Protected endpoint request failed" "Connection timeout or network error"
fi

# Test 4: Database connectivity (via Python script)
print_test "Database connectivity check"
# Use Poetry to run Python script with correct dependencies
if command -v poetry &> /dev/null && [ -f "backend/pyproject.toml" ]; then
    DB_OUTPUT=$(cd backend && poetry run python ../scripts/check_db.py "$MODE" 2>&1) || true
else
    # Fallback to system Python if Poetry not available
    DB_OUTPUT=$(python scripts/check_db.py "$MODE" 2>&1) || true
fi

if echo "$DB_OUTPUT" | grep -q "Database connection successful"; then
    print_pass "Database connection verified"
else
    print_fail "Database connection failed" "See check_db.py output for details"
fi

# Test 5: Static files (only for full/staging with frontend)
if [ "$MODE" = "local-full" ] || [ "$MODE" = "staging" ]; then
    print_test "Static files - GET / (frontend)"
    RESPONSE=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" \
        "${BASE_URL}/" 2>&1) || true
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ -n "$HTTP_CODE" ] && [ "$HTTP_CODE" = "200" ]; then
        # Verify HTML response
        if echo "$BODY" | grep -q "<html"; then
            print_pass "Frontend static files served (200 OK)"
        else
            print_fail "Frontend returned 200 but no HTML" "Response may be malformed"
        fi
    elif [ -n "$HTTP_CODE" ]; then
        print_fail "Frontend returned HTTP $HTTP_CODE" "Expected 200"
    else
        print_fail "Frontend request failed" "Connection timeout or network error"
    fi
fi

# Re-enable exit-on-error
set -e

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Print summary
echo ""
print_summary
echo ""
echo "Duration: ${DURATION}s"
echo ""

# Exit with appropriate code
if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ All smoke tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ ${TESTS_FAILED} test(s) failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Verify the application is running for mode: ${MODE}"
    echo "  2. Check application logs for errors"
    echo "  3. Verify database is accessible"
    echo "  4. Check network connectivity to ${BASE_URL}"
    exit 1
fi
