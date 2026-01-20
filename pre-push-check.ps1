# pre-push-check.ps1 - Automated pre-push verification script for Windows
# Run this before pushing to ensure CI/CD will pass
# Usage: .\pre-push-check.ps1

# Enable strict mode (Continue to allow manual exit code checking)
$ErrorActionPreference = "Continue"

# Colors for output
function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host ""
Write-ColorOutput Blue "╔════════════════════════════════════════════════╗"
Write-ColorOutput Blue "║   ContraVento - Pre-Push Quality Checks       ║"
Write-ColorOutput Blue "╚════════════════════════════════════════════════╝"
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-ColorOutput Red "❌ Error: Must run from project root directory"
    exit 1
}

# Track overall status
$backendFailed = $false
$frontendFailed = $false

Write-ColorOutput Blue "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-ColorOutput Blue "🐍 BACKEND CHECKS (Python/FastAPI)"
Write-ColorOutput Blue "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

Set-Location backend

# 1. Black formatting
Write-ColorOutput Yellow "[1/4] Running Black formatter..."
$output = poetry run black src/ tests/ --check --quiet 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "  ✓ Black: Code formatting is correct"
} else {
    Write-ColorOutput Red "  ✗ Black: Code needs formatting"
    Write-ColorOutput Yellow "  → Running auto-format..."
    poetry run black src/ tests/ --quiet
    Write-ColorOutput Green "  ✓ Code formatted automatically"
}

# 2. Ruff linting
Write-ColorOutput Yellow "[2/4] Running Ruff linter..."
poetry run ruff check src/ tests/ 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "  ✓ Ruff: No linting errors"
} else {
    Write-ColorOutput Red "  ✗ Ruff: Linting errors found"
    $backendFailed = $true
}

# 3. Mypy type checking
Write-ColorOutput Yellow "[3/4] Running Mypy type checker..."
$output = poetry run mypy src/ 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "  ✓ Mypy: Type checking passed"
} else {
    Write-ColorOutput Yellow "  ⚠ Mypy: Type checking has warnings (non-blocking)"
}

# 4. Pytest with coverage
Write-ColorOutput Yellow "[4/4] Running Pytest with coverage (≥90% required)..."
poetry run pytest --cov=src --cov-fail-under=90 -q 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "  ✓ Pytest: All tests passed with ≥90% coverage"
} else {
    Write-ColorOutput Red "  ✗ Pytest: Tests failed or coverage < 90%"
    $backendFailed = $true
}

Set-Location ..
Write-Host ""

Write-ColorOutput Blue "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-ColorOutput Blue "⚛️  FRONTEND CHECKS (React/TypeScript)"
Write-ColorOutput Blue "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

Set-Location frontend

# 1. ESLint
Write-ColorOutput Yellow "[1/3] Running ESLint..."
npm run lint 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "  ✓ ESLint: No linting errors"
} else {
    Write-ColorOutput Red "  ✗ ESLint: Linting errors found"
    $frontendFailed = $true
}

# 2. TypeScript type checking
Write-ColorOutput Yellow "[2/3] Running TypeScript type checker..."
npm run type-check 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "  ✓ TypeScript: Type checking passed"
} else {
    Write-ColorOutput Red "  ✗ TypeScript: Type errors found"
    $frontendFailed = $true
}

# 3. Vitest unit tests
Write-ColorOutput Yellow "[3/3] Running Vitest unit tests..."
npm run test:unit -- --run 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-ColorOutput Green "  ✓ Vitest: All unit tests passed"
} else {
    Write-ColorOutput Red "  ✗ Vitest: Some tests failed"
    $frontendFailed = $true
}

Set-Location ..
Write-Host ""

# Final summary
Write-ColorOutput Blue "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-ColorOutput Blue "📊 SUMMARY"
Write-ColorOutput Blue "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host ""

if (-not $backendFailed -and -not $frontendFailed) {
    Write-ColorOutput Green "✅ ALL CHECKS PASSED!"
    Write-ColorOutput Green "   You can safely push your changes."
    Write-Host ""
    Write-ColorOutput Blue "Next steps:"
    Write-Host "  1. git add ."
    Write-Host "  2. git commit -m `"your message`""
    Write-Host "  3. git push origin <branch-name>"
    Write-Host ""
    exit 0
} else {
    Write-ColorOutput Red "❌ SOME CHECKS FAILED"
    Write-Host ""
    if ($backendFailed) {
        Write-ColorOutput Red "  Backend: FAILED"
    } else {
        Write-ColorOutput Green "  Backend: PASSED"
    }
    if ($frontendFailed) {
        Write-ColorOutput Red "  Frontend: FAILED"
    } else {
        Write-ColorOutput Green "  Frontend: PASSED"
    }
    Write-Host ""
    Write-ColorOutput Yellow "Please fix the errors above before pushing."
    Write-Host ""
    exit 1
}
