# Pre-commit Checks for ContraVento (PowerShell version)
#
# Runs all quality checks and tests locally before committing code.
# Ensures CI/CD pipeline will pass.
#
# Usage:
#   .\scripts\run_pre_commit_checks.ps1
#   .\scripts\run_pre_commit_checks.ps1 -Quick  # Skip slow tests

param(
    [switch]$Quick
)

# Initialize counters
$script:ChecksPassed = 0
$script:ChecksFailed = 0

# Helper functions
function Print-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  $Text" -ForegroundColor Blue
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host ""
}

function Print-Check {
    param([string]$Text)
    Write-Host "▶ $Text" -ForegroundColor Yellow
}

function Print-Pass {
    param([string]$Text)
    Write-Host "✅ PASS - $Text" -ForegroundColor Green
    $script:ChecksPassed++
}

function Print-Fail {
    param([string]$Text)
    Write-Host "❌ FAIL - $Text" -ForegroundColor Red
    $script:ChecksFailed++
}

function Print-Skip {
    param([string]$Text)
    Write-Host "⏭️  SKIP - $Text" -ForegroundColor Yellow
}

function Print-Summary {
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  Pre-commit Checks Summary" -ForegroundColor Blue
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host "  Total Passed: $script:ChecksPassed" -ForegroundColor Green
    Write-Host "  Total Failed: $script:ChecksFailed" -ForegroundColor Red
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Blue
    Write-Host ""
}

# Start
Print-Header "Pre-commit Checks for ContraVento"

if ($Quick) {
    Write-Host "⚡ Running in QUICK mode (skipping slow tests)" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================================================
# BACKEND CHECKS
# ============================================================================

Print-Header "Backend Quality Checks"

# Check 1: Black formatting
Print-Check "Checking Python code formatting (black)"
Push-Location backend
$blackOutput = poetry run black --check src/ tests/ 2>&1
if ($LASTEXITCODE -eq 0) {
    Print-Pass "Code is properly formatted"
} else {
    Print-Fail "Code formatting issues found. Run: poetry run black src/ tests/"
}

# Check 2: Ruff linting
Print-Check "Linting Python code (ruff)"
$ruffOutput = poetry run ruff check src/ tests/ 2>&1
if ($LASTEXITCODE -eq 0) {
    Print-Pass "No linting errors"
} else {
    Print-Fail "Linting errors found. Run: poetry run ruff check src/ tests/"
}

# Check 3: MyPy type checking
Print-Check "Type checking Python code (mypy)"
$mypyOutput = poetry run mypy src/ 2>&1
if ($LASTEXITCODE -eq 0) {
    Print-Pass "No type errors"
} else {
    Print-Fail "Type errors found. Run: poetry run mypy src/"
}

Pop-Location

# ============================================================================
# FRONTEND CHECKS
# ============================================================================

Print-Header "Frontend Quality Checks"

# Check 4: ESLint
Print-Check "Linting TypeScript code (ESLint)"
Push-Location frontend
$eslintOutput = npm run lint 2>&1
if ($LASTEXITCODE -eq 0) {
    Print-Pass "No linting errors"
} else {
    Print-Fail "Linting errors found. Run: npm run lint"
}

# Check 5: TypeScript type checking
Print-Check "Type checking TypeScript code"
$tscOutput = npm run type-check 2>&1
if ($LASTEXITCODE -eq 0) {
    Print-Pass "No type errors"
} else {
    Print-Fail "Type errors found. Run: npm run type-check"
}

Pop-Location

# ============================================================================
# BACKEND TESTS
# ============================================================================

if (-not $Quick) {
    Print-Header "Backend Tests"

    # Check 6: Backend unit tests
    Print-Check "Running backend unit tests"
    Push-Location backend
    $unitTestOutput = poetry run pytest tests/unit/ -v --tb=short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Pass "All unit tests passed"
    } else {
        Print-Fail "Unit tests failed. Run: poetry run pytest tests/unit/ -v"
    }

    # Check 7: Backend integration tests
    Print-Check "Running backend integration tests"
    $integrationTestOutput = poetry run pytest tests/integration/ -v --tb=short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Pass "All integration tests passed"
    } else {
        Print-Fail "Integration tests failed. Run: poetry run pytest tests/integration/ -v"
    }

    # Check 8: Coverage threshold
    Print-Check "Checking test coverage (≥90%)"
    $coverageOutput = poetry run pytest --cov=src --cov-fail-under=90 -q 2>&1
    if ($LASTEXITCODE -eq 0) {
        $coverageReport = poetry run coverage report | Select-String "TOTAL"
        $coverage = ($coverageReport -split '\s+')[3]
        Print-Pass "Coverage threshold met: $coverage"
    } else {
        $coverageReport = poetry run coverage report | Select-String "TOTAL"
        $coverage = ($coverageReport -split '\s+')[3]
        Print-Fail "Coverage below 90%: $coverage. Add more tests."
    }

    Pop-Location
} else {
    Print-Skip "Backend tests (use -Quick mode)"
}

# ============================================================================
# FRONTEND TESTS
# ============================================================================

if (-not $Quick) {
    Print-Header "Frontend Tests"

    # Check 9: Frontend unit tests
    Print-Check "Running frontend unit tests"
    Push-Location frontend
    $frontendTestOutput = npm run test:unit 2>&1
    if ($LASTEXITCODE -eq 0) {
        Print-Pass "All unit tests passed"
    } else {
        Print-Fail "Unit tests failed. Run: npm run test:unit"
    }

    Pop-Location
} else {
    Print-Skip "Frontend tests (use -Quick mode)"
}

# ============================================================================
# BUILD CHECKS
# ============================================================================

Print-Header "Build Validation"

# Check 10: Frontend build
Print-Check "Building frontend for production"
Push-Location frontend
$buildOutput = npm run build:prod 2>&1
if ($LASTEXITCODE -eq 0) {
    # Check bundle size
    $distSize = (Get-ChildItem -Recurse dist | Measure-Object -Property Length -Sum).Sum
    $distSizeMB = [math]::Round($distSize / 1MB, 2)

    Print-Pass "Frontend build successful (size: ${distSizeMB}MB)"

    # Warn if build is too large
    if ($distSize -gt 5242880) {
        Print-Fail "Build size exceeds 5MB (${distSizeMB}MB). Consider optimizing."
    } else {
        Print-Pass "Build size is acceptable (${distSizeMB}MB)"
    }
} else {
    Print-Fail "Frontend build failed. Run: npm run build:prod"
}

Pop-Location

# ============================================================================
# GIT CHECKS
# ============================================================================

Print-Header "Git Checks"

# Check 11: No uncommitted changes (warning only)
$gitStatus = git status --porcelain
if ($gitStatus.Length -eq 0) {
    Print-Pass "No uncommitted changes"
} else {
    Print-Fail "You have uncommitted changes. Commit or stash them."
}

# Check 12: Current branch
$currentBranch = git branch --show-current
if ($currentBranch -eq "main" -or $currentBranch -eq "develop") {
    Print-Fail "You are on $currentBranch branch. Consider using a feature branch."
} else {
    Print-Pass "Working on feature branch: $currentBranch"
}

# ============================================================================
# FINAL SUMMARY
# ============================================================================

Print-Summary

if ($script:ChecksFailed -eq 0) {
    Write-Host "🎉 All checks passed! Ready to commit." -ForegroundColor Green
    Write-Host ""
    exit 0
} else {
    Write-Host "💥 $script:ChecksFailed check(s) failed. Fix errors before committing." -ForegroundColor Red
    Write-Host ""
    exit 1
}
