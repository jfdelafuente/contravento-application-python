#!/bin/bash
# pre-push-check.sh - Automated pre-push verification script
# Run this before pushing to ensure CI/CD will pass
#
# Usage:
#   ./pre-push-check.sh              # Run all checks (default)
#   ./pre-push-check.sh --backend    # Run only backend checks
#   ./pre-push-check.sh --frontend   # Run only frontend checks
#   ./pre-push-check.sh --help       # Show help

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Show help
show_help() {
    echo ""
    echo -e "${BLUE}ContraVento - Pre-Push Quality Checks${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./pre-push-check.sh              Run all checks (default)"
    echo "  ./pre-push-check.sh --backend    Run only backend checks"
    echo "  ./pre-push-check.sh --frontend   Run only frontend checks"
    echo "  ./pre-push-check.sh --help       Show this help message"
    echo ""
    echo -e "${CYAN}Backend checks:${NC}"
    echo "  - Black formatter"
    echo "  - Ruff linter"
    echo "  - Mypy type checker"
    echo "  - Pytest with coverage (>=90%)"
    echo ""
    echo -e "${CYAN}Frontend checks:${NC}"
    echo "  - ESLint"
    echo "  - TypeScript type checker"
    echo "  - Vitest unit tests"
    echo ""
    exit 0
}

# Parse command line arguments
RUN_BACKEND=true
RUN_FRONTEND=true

if [ $# -gt 0 ]; then
    case "$1" in
        --help|-h)
            show_help
            ;;
        --backend|-b)
            RUN_BACKEND=true
            RUN_FRONTEND=false
            ;;
        --frontend|-f)
            RUN_BACKEND=false
            RUN_FRONTEND=true
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help to see available options"
            exit 1
            ;;
    esac
fi

echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   ContraVento - Pre-Push Quality Checks${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Save the root directory
ROOT_DIR=$(pwd)

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}ERROR: Must run from project root directory${NC}"
    exit 1
fi

# Track overall status
BACKEND_FAILED=false
FRONTEND_FAILED=false

# ============================================================================
# BACKEND CHECKS
# ============================================================================

if [ "$RUN_BACKEND" = true ]; then
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}BACKEND CHECKS (Python/FastAPI)${NC}"
    echo -e "${BLUE}==================================================${NC}"
    echo ""

    cd "$ROOT_DIR/backend" || exit 1

    # 1. Black formatting
    echo -e "${YELLOW}[1/4] Running Black formatter...${NC}"
    if poetry run black src/ tests/ --check --quiet > /dev/null 2>&1; then
        echo -e "${GREEN}  [OK] Black: Code formatting is correct${NC}"
    else
        echo -e "${RED}  [FAIL] Black: Code needs formatting${NC}"
        echo -e "${YELLOW}  -> Running auto-format...${NC}"
        poetry run black src/ tests/ --quiet
        echo -e "${GREEN}  [OK] Code formatted automatically${NC}"
    fi

    # 2. Ruff linting
    echo -e "${YELLOW}[2/4] Running Ruff linter...${NC}"
    if poetry run ruff check src/ tests/ > /dev/null 2>&1; then
        echo -e "${GREEN}  [OK] Ruff: No linting errors${NC}"
    else
        echo -e "${RED}  [FAIL] Ruff: Linting errors found${NC}"
        BACKEND_FAILED=true
    fi

    # 3. Mypy type checking
    echo -e "${YELLOW}[3/4] Running Mypy type checker...${NC}"
    if poetry run mypy src/ > /dev/null 2>&1; then
        echo -e "${GREEN}  [OK] Mypy: Type checking passed${NC}"
    else
        echo -e "${YELLOW}  [WARN] Mypy: Type checking has warnings (non-blocking)${NC}"
    fi

    # 4. Pytest with coverage
    echo -e "${YELLOW}[4/4] Running Pytest with coverage (>=90% required)...${NC}"
    if poetry run pytest --cov=src --cov-fail-under=90 -q > /dev/null 2>&1; then
        echo -e "${GREEN}  [OK] Pytest: All tests passed with >=90% coverage${NC}"
    else
        echo -e "${RED}  [FAIL] Pytest: Tests failed or coverage < 90%${NC}"
        BACKEND_FAILED=true
    fi

    cd "$ROOT_DIR" || exit 1
    echo ""
else
    echo -e "${YELLOW}Skipping backend checks (use --backend to run)${NC}"
    echo ""
fi

# ============================================================================
# FRONTEND CHECKS
# ============================================================================

if [ "$RUN_FRONTEND" = true ]; then
    echo -e "${BLUE}==================================================${NC}"
    echo -e "${BLUE}FRONTEND CHECKS (React/TypeScript)${NC}"
    echo -e "${BLUE}==================================================${NC}"
    echo ""

    cd "$ROOT_DIR/frontend" || exit 1

    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}  [ERROR] npm command not found. Is Node.js installed?${NC}"
        echo -e "${YELLOW}  Skipping frontend checks...${NC}"
        FRONTEND_FAILED=true
    else
        # 1. ESLint
        echo -e "${YELLOW}[1/3] Running ESLint...${NC}"
        if npm run lint > /dev/null 2>&1; then
            echo -e "${GREEN}  [OK] ESLint: No linting errors${NC}"
        else
            echo -e "${RED}  [FAIL] ESLint: Linting errors found${NC}"
            FRONTEND_FAILED=true
        fi

        # 2. TypeScript type checking
        echo -e "${YELLOW}[2/3] Running TypeScript type checker...${NC}"
        if npm run type-check > /dev/null 2>&1; then
            echo -e "${GREEN}  [OK] TypeScript: Type checking passed${NC}"
        else
            echo -e "${RED}  [FAIL] TypeScript: Type errors found${NC}"
            FRONTEND_FAILED=true
        fi

        # 3. Vitest unit tests
        echo -e "${YELLOW}[3/3] Running Vitest unit tests...${NC}"
        if npm run test:unit -- --run > /dev/null 2>&1; then
            echo -e "${GREEN}  [OK] Vitest: All unit tests passed${NC}"
        else
            echo -e "${RED}  [FAIL] Vitest: Some tests failed${NC}"
            FRONTEND_FAILED=true
        fi
    fi

    cd "$ROOT_DIR" || exit 1
    echo ""
else
    echo -e "${YELLOW}Skipping frontend checks (use --frontend to run)${NC}"
    echo ""
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}SUMMARY${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Determine overall result based on what was run
OVERALL_FAILED=false

if [ "$RUN_BACKEND" = true ] && [ "$BACKEND_FAILED" = true ]; then
    OVERALL_FAILED=true
fi

if [ "$RUN_FRONTEND" = true ] && [ "$FRONTEND_FAILED" = true ]; then
    OVERALL_FAILED=true
fi

if [ "$OVERALL_FAILED" = false ]; then
    echo -e "${GREEN}ALL CHECKS PASSED!${NC}"
    echo -e "${GREEN}You can safely push your changes.${NC}"
    echo ""

    if [ "$RUN_BACKEND" = true ]; then
        echo -e "${GREEN}  Backend: PASSED${NC}"
    fi

    if [ "$RUN_FRONTEND" = true ]; then
        echo -e "${GREEN}  Frontend: PASSED${NC}"
    fi

    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. git add ."
    echo "  2. git commit -m \"your message\""
    echo "  3. git push origin <branch-name>"
    echo ""
    exit 0
else
    echo -e "${RED}SOME CHECKS FAILED${NC}"
    echo ""

    if [ "$RUN_BACKEND" = true ]; then
        if [ "$BACKEND_FAILED" = true ]; then
            echo -e "${RED}  Backend: FAILED${NC}"
        else
            echo -e "${GREEN}  Backend: PASSED${NC}"
        fi
    fi

    if [ "$RUN_FRONTEND" = true ]; then
        if [ "$FRONTEND_FAILED" = true ]; then
            echo -e "${RED}  Frontend: FAILED${NC}"
        else
            echo -e "${GREEN}  Frontend: PASSED${NC}"
        fi
    fi

    echo ""
    echo -e "${YELLOW}Please fix the errors above before pushing.${NC}"
    echo ""
    exit 1
fi
