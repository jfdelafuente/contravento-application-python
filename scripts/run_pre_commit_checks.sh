#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Pre-commit Checks for ContraVento
#
# Runs all quality checks and tests locally before committing code.
# Ensures CI/CD pipeline will pass.
#
# Usage:
#   ./scripts/run_pre_commit_checks.sh
#   ./scripts/run_pre_commit_checks.sh --quick  # Skip slow tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Parse arguments
QUICK_MODE=false
if [ "$1" == "--quick" ]; then
    QUICK_MODE=true
    echo -e "${YELLOW}⚡ Running in QUICK mode (skipping slow tests)${NC}\n"
fi

# Helper functions
print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_check() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS - $1${NC}"
    ((CHECKS_PASSED++))
}

print_fail() {
    echo -e "${RED}❌ FAIL - $1${NC}"
    ((CHECKS_FAILED++))
}

print_skip() {
    echo -e "${YELLOW}⏭️  SKIP - $1${NC}"
}

print_summary() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Pre-commit Checks Summary${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  Total Passed: ${GREEN}$CHECKS_PASSED${NC}"
    echo -e "  Total Failed: ${RED}$CHECKS_FAILED${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Trap errors and print summary
trap print_summary EXIT

print_header "Pre-commit Checks for ContraVento"

# ============================================================================
# BACKEND CHECKS
# ============================================================================

print_header "Backend Quality Checks"

# Check 1: Black formatting
print_check "Checking Python code formatting (black)"
cd backend
if poetry run black --check src/ tests/ > /dev/null 2>&1; then
    print_pass "Code is properly formatted"
else
    print_fail "Code formatting issues found. Run: poetry run black src/ tests/"
fi

# Check 2: Ruff linting
print_check "Linting Python code (ruff)"
if poetry run ruff check src/ tests/ > /dev/null 2>&1; then
    print_pass "No linting errors"
else
    print_fail "Linting errors found. Run: poetry run ruff check src/ tests/"
fi

# Check 3: MyPy type checking
print_check "Type checking Python code (mypy)"
if poetry run mypy src/ > /dev/null 2>&1; then
    print_pass "No type errors"
else
    print_fail "Type errors found. Run: poetry run mypy src/"
fi

cd ..

# ============================================================================
# FRONTEND CHECKS
# ============================================================================

print_header "Frontend Quality Checks"

# Check 4: ESLint
print_check "Linting TypeScript code (ESLint)"
cd frontend
if npm run lint > /dev/null 2>&1; then
    print_pass "No linting errors"
else
    print_fail "Linting errors found. Run: npm run lint"
fi

# Check 5: TypeScript type checking
print_check "Type checking TypeScript code"
if npm run type-check > /dev/null 2>&1; then
    print_pass "No type errors"
else
    print_fail "Type errors found. Run: npm run type-check"
fi

cd ..

# ============================================================================
# BACKEND TESTS
# ============================================================================

if [ "$QUICK_MODE" = false ]; then
    print_header "Backend Tests"

    # Check 6: Backend unit tests
    print_check "Running backend unit tests"
    cd backend
    if poetry run pytest tests/unit/ -v --tb=short > /dev/null 2>&1; then
        print_pass "All unit tests passed"
    else
        print_fail "Unit tests failed. Run: poetry run pytest tests/unit/ -v"
    fi

    # Check 7: Backend integration tests
    print_check "Running backend integration tests"
    if poetry run pytest tests/integration/ -v --tb=short > /dev/null 2>&1; then
        print_pass "All integration tests passed"
    else
        print_fail "Integration tests failed. Run: poetry run pytest tests/integration/ -v"
    fi

    # Check 8: Coverage threshold
    print_check "Checking test coverage (≥90%)"
    if poetry run pytest --cov=src --cov-fail-under=90 -q > /dev/null 2>&1; then
        COVERAGE=$(poetry run coverage report | grep TOTAL | awk '{print $4}')
        print_pass "Coverage threshold met: $COVERAGE"
    else
        COVERAGE=$(poetry run coverage report | grep TOTAL | awk '{print $4}')
        print_fail "Coverage below 90%: $COVERAGE. Add more tests."
    fi

    cd ..
else
    print_skip "Backend tests (use --quick mode)"
fi

# ============================================================================
# FRONTEND TESTS
# ============================================================================

if [ "$QUICK_MODE" = false ]; then
    print_header "Frontend Tests"

    # Check 9: Frontend unit tests
    print_check "Running frontend unit tests"
    cd frontend
    if npm run test:unit > /dev/null 2>&1; then
        print_pass "All unit tests passed"
    else
        print_fail "Unit tests failed. Run: npm run test:unit"
    fi

    cd ..
else
    print_skip "Frontend tests (use --quick mode)"
fi

# ============================================================================
# BUILD CHECKS
# ============================================================================

print_header "Build Validation"

# Check 10: Frontend build
print_check "Building frontend for production"
cd frontend
if npm run build:prod > /dev/null 2>&1; then
    # Check bundle size
    BUILD_SIZE=$(du -sh dist | awk '{print $1}')
    SIZE_BYTES=$(du -sb dist | awk '{print $1}')

    print_pass "Frontend build successful (size: $BUILD_SIZE)"

    # Warn if build is too large
    if [ $SIZE_BYTES -gt 5242880 ]; then
        print_fail "Build size exceeds 5MB ($BUILD_SIZE). Consider optimizing."
    else
        print_pass "Build size is acceptable ($BUILD_SIZE)"
    fi
else
    print_fail "Frontend build failed. Run: npm run build:prod"
fi

cd ..

# ============================================================================
# GIT CHECKS
# ============================================================================

print_header "Git Checks"

# Check 11: No uncommitted changes (warning only)
if git diff --quiet && git diff --cached --quiet; then
    print_pass "No uncommitted changes"
else
    print_fail "You have uncommitted changes. Commit or stash them."
fi

# Check 12: Current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" == "main" ] || [ "$CURRENT_BRANCH" == "develop" ]; then
    print_fail "You are on $CURRENT_BRANCH branch. Consider using a feature branch."
else
    print_pass "Working on feature branch: $CURRENT_BRANCH"
fi

# ============================================================================
# FINAL SUMMARY
# ============================================================================

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All checks passed! Ready to commit.${NC}\n"
    exit 0
else
    echo -e "\n${RED}💥 $CHECKS_FAILED check(s) failed. Fix errors before committing.${NC}\n"
    exit 1
fi
