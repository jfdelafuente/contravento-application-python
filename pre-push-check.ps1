# pre-push-check.ps1 - Automated pre-push verification script for Windows
# Run this before pushing to ensure CI/CD will pass
#
# Usage:
#   .\pre-push-check.ps1              # Run all checks (default)
#   .\pre-push-check.ps1 -Backend     # Run only backend checks
#   .\pre-push-check.ps1 -Frontend    # Run only frontend checks
#   .\pre-push-check.ps1 -Help        # Show help

param(
    [switch]$Backend,
    [switch]$Frontend,
    [switch]$Help
)

# Enable strict mode (Continue to allow manual exit code checking)
$ErrorActionPreference = "Continue"

# Colors for output
function Write-ColorOutput($ForegroundColor, $Message) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $fc
}

# Show help
if ($Help) {
    Write-Host ""
    Write-Host "ContraVento - Pre-Push Quality Checks" -ForegroundColor Blue
    Write-Host "=====================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\pre-push-check.ps1              Run all checks (default)"
    Write-Host "  .\pre-push-check.ps1 -Backend     Run only backend checks"
    Write-Host "  .\pre-push-check.ps1 -Frontend    Run only frontend checks"
    Write-Host "  .\pre-push-check.ps1 -Help        Show this help message"
    Write-Host ""
    Write-Host "Backend checks:" -ForegroundColor Cyan
    Write-Host "  - Black formatter"
    Write-Host "  - Ruff linter"
    Write-Host "  - Mypy type checker"
    Write-Host "  - Pytest with coverage (>=90%)"
    Write-Host ""
    Write-Host "Frontend checks:" -ForegroundColor Cyan
    Write-Host "  - ESLint"
    Write-Host "  - TypeScript type checker"
    Write-Host "  - Vitest unit tests"
    Write-Host ""
    exit 0
}

# Determine what to run
$RunBackend = $Backend -or (-not $Backend -and -not $Frontend)
$RunFrontend = $Frontend -or (-not $Backend -and -not $Frontend)

Write-Host ""
Write-ColorOutput Blue "=================================================="
Write-ColorOutput Blue "   ContraVento - Pre-Push Quality Checks"
Write-ColorOutput Blue "=================================================="
Write-Host ""

# Save the root directory
$RootDir = Get-Location

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-ColorOutput Red "ERROR: Must run from project root directory"
    exit 1
}

# Track overall status
$backendFailed = $false
$frontendFailed = $false

# ============================================================================
# BACKEND CHECKS
# ============================================================================

if ($RunBackend) {
    Write-ColorOutput Blue "=================================================="
    Write-ColorOutput Blue "BACKEND CHECKS (Python/FastAPI)"
    Write-ColorOutput Blue "=================================================="
    Write-Host ""

    # Navigate to backend directory
    Set-Location -Path (Join-Path $RootDir "backend")

    # 1. Black formatting
    Write-ColorOutput Yellow "[1/4] Running Black formatter..."
    poetry run black src/ tests/ --check --quiet 2>&1 | Out-Null
    $blackExitCode = $LASTEXITCODE

    if ($blackExitCode -eq 0) {
        Write-ColorOutput Green "  [OK] Black: Code formatting is correct"
    } else {
        Write-ColorOutput Red "  [FAIL] Black: Code needs formatting"
        Write-ColorOutput Yellow "  -> Running auto-format..."
        poetry run black src/ tests/ --quiet
        Write-ColorOutput Green "  [OK] Code formatted automatically"
    }

    # 2. Ruff linting
    Write-ColorOutput Yellow "[2/4] Running Ruff linter..."
    poetry run ruff check src/ tests/ 2>&1 | Out-Null
    $ruffExitCode = $LASTEXITCODE

    if ($ruffExitCode -eq 0) {
        Write-ColorOutput Green "  [OK] Ruff: No linting errors"
    } else {
        Write-ColorOutput Red "  [FAIL] Ruff: Linting errors found"
        $backendFailed = $true
    }

    # 3. Mypy type checking
    Write-ColorOutput Yellow "[3/4] Running Mypy type checker..."
    poetry run mypy src/ 2>&1 | Out-Null
    $mypyExitCode = $LASTEXITCODE

    if ($mypyExitCode -eq 0) {
        Write-ColorOutput Green "  [OK] Mypy: Type checking passed"
    } else {
        Write-ColorOutput Yellow "  [WARN] Mypy: Type checking has warnings (non-blocking)"
    }

    # 4. Pytest with coverage
    Write-ColorOutput Yellow "[4/4] Running Pytest with coverage (>=90% required)..."
    poetry run pytest --cov=src --cov-fail-under=90 -q 2>&1 | Out-Null
    $pytestExitCode = $LASTEXITCODE

    if ($pytestExitCode -eq 0) {
        Write-ColorOutput Green "  [OK] Pytest: All tests passed with >=90% coverage"
    } else {
        Write-ColorOutput Red "  [FAIL] Pytest: Tests failed or coverage < 90%"
        $backendFailed = $true
    }

    # Return to root
    Set-Location $RootDir
    Write-Host ""
} else {
    Write-ColorOutput Yellow "Skipping backend checks (use -Backend to run)"
    Write-Host ""
}

# ============================================================================
# FRONTEND CHECKS
# ============================================================================

if ($RunFrontend) {
    Write-ColorOutput Blue "=================================================="
    Write-ColorOutput Blue "FRONTEND CHECKS (React/TypeScript)"
    Write-ColorOutput Blue "=================================================="
    Write-Host ""

    # Navigate to frontend directory
    Set-Location -Path (Join-Path $RootDir "frontend")

    # Try to find npm (check common locations if not in PATH)
    $npmCommand = Get-Command npm -ErrorAction SilentlyContinue

    if (-not $npmCommand) {
        # Try common Node.js installation paths
        $commonPaths = @(
            "$env:USERPROFILE\nodejs\node20\npm.cmd",
            "$env:ProgramFiles\nodejs\npm.cmd",
            "${env:ProgramFiles(x86)}\nodejs\npm.cmd",
            "$env:APPDATA\npm\npm.cmd"
        )

        foreach ($path in $commonPaths) {
            if (Test-Path $path) {
                $npmCommand = $path
                Write-ColorOutput Cyan "  [INFO] Found npm at: $path"
                break
            }
        }
    }

    if (-not $npmCommand) {
        Write-ColorOutput Red "  [ERROR] npm command not found. Is Node.js installed?"
        Write-ColorOutput Yellow "  Skipping frontend checks..."
        $frontendFailed = $true
    } else {
        # Get npm executable path
        $npmExe = if ($npmCommand -is [string]) { $npmCommand } else { $npmCommand.Source }

        # Add Node.js directory to PATH temporarily
        $nodeDir = Split-Path -Parent $npmExe
        $env:PATH = "$nodeDir;$env:PATH"

        # 1. ESLint
        Write-ColorOutput Yellow "[1/3] Running ESLint..."
        $eslintOutput = & $npmExe run lint 2>&1
        $eslintExitCode = $LASTEXITCODE

        if ($eslintExitCode -eq 0) {
            Write-ColorOutput Green "  [OK] ESLint: No linting errors"
        } else {
            Write-ColorOutput Red "  [FAIL] ESLint: Linting errors found"
            Write-Host $eslintOutput
            $frontendFailed = $true
        }

        # 2. TypeScript type checking
        Write-ColorOutput Yellow "[2/3] Running TypeScript type checker..."
        $tscOutput = & $npmExe run type-check 2>&1
        $tscExitCode = $LASTEXITCODE

        if ($tscExitCode -eq 0) {
            Write-ColorOutput Green "  [OK] TypeScript: Type checking passed"
        } else {
            Write-ColorOutput Red "  [FAIL] TypeScript: Type errors found"
            Write-Host $tscOutput
            $frontendFailed = $true
        }

        # 3. Vitest unit tests
        Write-ColorOutput Yellow "[3/3] Running Vitest unit tests..."
        $vitestOutput = & $npmExe run test:unit -- --run 2>&1
        $vitestExitCode = $LASTEXITCODE

        if ($vitestExitCode -eq 0) {
            Write-ColorOutput Green "  [OK] Vitest: All unit tests passed"
        } else {
            Write-ColorOutput Red "  [FAIL] Vitest: Some tests failed"
            Write-Host $vitestOutput
            $frontendFailed = $true
        }
    }

    # Return to root
    Set-Location $RootDir
    Write-Host ""
} else {
    Write-ColorOutput Yellow "Skipping frontend checks (use -Frontend to run)"
    Write-Host ""
}

# ============================================================================
# SUMMARY
# ============================================================================

Write-ColorOutput Blue "=================================================="
Write-ColorOutput Blue "SUMMARY"
Write-ColorOutput Blue "=================================================="
Write-Host ""

# Determine overall result based on what was run
$overallFailed = $false

if ($RunBackend -and $backendFailed) {
    $overallFailed = $true
}

if ($RunFrontend -and $frontendFailed) {
    $overallFailed = $true
}

if (-not $overallFailed) {
    Write-ColorOutput Green "ALL CHECKS PASSED!"
    Write-ColorOutput Green "You can safely push your changes."
    Write-Host ""

    if ($RunBackend -and -not $backendFailed) {
        Write-ColorOutput Green "  Backend: PASSED"
    }

    if ($RunFrontend -and -not $frontendFailed) {
        Write-ColorOutput Green "  Frontend: PASSED"
    }

    Write-Host ""
    Write-ColorOutput Blue "Next steps:"
    Write-Host "  1. git add ."
    Write-Host '  2. git commit -m "your message"'
    Write-Host "  3. git push origin <branch-name>"
    Write-Host ""
    exit 0
} else {
    Write-ColorOutput Red "SOME CHECKS FAILED"
    Write-Host ""

    if ($RunBackend) {
        if ($backendFailed) {
            Write-ColorOutput Red "  Backend: FAILED"
        } else {
            Write-ColorOutput Green "  Backend: PASSED"
        }
    }

    if ($RunFrontend) {
        if ($frontendFailed) {
            Write-ColorOutput Red "  Frontend: FAILED"
        } else {
            Write-ColorOutput Green "  Frontend: PASSED"
        }
    }

    Write-Host ""
    Write-ColorOutput Yellow "Please fix the errors above before pushing."
    Write-Host ""
    exit 1
}
