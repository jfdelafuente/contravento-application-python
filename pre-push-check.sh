#!/bin/bash
# pre-push-check.sh - Automated pre-push verification script
# Run this before pushing to ensure CI/CD will pass
# Usage: ./pre-push-check.sh

set -e  # Exit immediately if a command exits with a non-zero status

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   ContraVento - Pre-Push Quality Checks       ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Must run from project root directory${NC}"
    exit 1
fi

# Track overall status
BACKEND_FAILED=0
FRONTEND_FAILED=0

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🐍 BACKEND CHECKS (Python/FastAPI)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd backend

# 1. Black formatting
echo -e "${YELLOW}[1/4]${NC} Running Black formatter..."
if poetry run black src/ tests/ --check --quiet; then
    echo -e "${GREEN}  ✓ Black: Code formatting is correct${NC}"
else
    echo -e "${RED}  ✗ Black: Code needs formatting${NC}"
    echo -e "${YELLOW}  → Running auto-format...${NC}"
    poetry run black src/ tests/ --quiet
    echo -e "${GREEN}  ✓ Code formatted automatically${NC}"
fi

# 2. Ruff linting
echo -e "${YELLOW}[2/4]${NC} Running Ruff linter..."
if poetry run ruff check src/ tests/; then
    echo -e "${GREEN}  ✓ Ruff: No linting errors${NC}"
else
    echo -e "${RED}  ✗ Ruff: Linting errors found${NC}"
    BACKEND_FAILED=1
fi

# 3. Mypy type checking
echo -e "${YELLOW}[3/4]${NC} Running Mypy type checker..."
if poetry run mypy src/ > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Mypy: Type checking passed${NC}"
else
    echo -e "${YELLOW}  ⚠ Mypy: Type checking has warnings (non-blocking)${NC}"
fi

# 4. Pytest with coverage
echo -e "${YELLOW}[4/4]${NC} Running Pytest with coverage (≥90% required)..."
if poetry run pytest --cov=src --cov-fail-under=90 -q; then
    echo -e "${GREEN}  ✓ Pytest: All tests passed with ≥90% coverage${NC}"
else
    echo -e "${RED}  ✗ Pytest: Tests failed or coverage < 90%${NC}"
    BACKEND_FAILED=1
fi

cd ..
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}⚛️  FRONTEND CHECKS (React/TypeScript)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd frontend

# 1. ESLint
echo -e "${YELLOW}[1/3]${NC} Running ESLint..."
if npm run lint; then
    echo -e "${GREEN}  ✓ ESLint: No linting errors${NC}"
else
    echo -e "${RED}  ✗ ESLint: Linting errors found${NC}"
    FRONTEND_FAILED=1
fi

# 2. TypeScript type checking
echo -e "${YELLOW}[2/3]${NC} Running TypeScript type checker..."
if npm run type-check; then
    echo -e "${GREEN}  ✓ TypeScript: Type checking passed${NC}"
else
    echo -e "${RED}  ✗ TypeScript: Type errors found${NC}"
    FRONTEND_FAILED=1
fi

# 3. Vitest unit tests
echo -e "${YELLOW}[3/3]${NC} Running Vitest unit tests..."
if npm run test:unit -- --run; then
    echo -e "${GREEN}  ✓ Vitest: All unit tests passed${NC}"
else
    echo -e "${RED}  ✗ Vitest: Some tests failed${NC}"
    FRONTEND_FAILED=1
fi

cd ..
echo ""

# Final summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ $BACKEND_FAILED -eq 0 ] && [ $FRONTEND_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}   You can safely push your changes.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "  1. git add ."
    echo -e "  2. git commit -m \"your message\""
    echo -e "  3. git push origin <branch-name>"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    if [ $BACKEND_FAILED -eq 1 ]; then
        echo -e "${RED}  Backend: FAILED${NC}"
    else
        echo -e "${GREEN}  Backend: PASSED${NC}"
    fi
    if [ $FRONTEND_FAILED -eq 1 ]; then
        echo -e "${RED}  Frontend: FAILED${NC}"
    else
        echo -e "${GREEN}  Frontend: PASSED${NC}"
    fi
    echo ""
    echo -e "${YELLOW}Please fix the errors above before pushing.${NC}"
    echo ""
    exit 1
fi
