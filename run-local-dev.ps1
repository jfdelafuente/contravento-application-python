# ============================================================================
# ContraVento - Local Development Startup Script (SQLite - No Docker)
# ============================================================================
# Quick start development server with SQLite database
# No Docker required - instant startup!
#
# Usage:
#   .\run-local-dev.ps1                     # Start backend only
#   .\run-local-dev.ps1 -WithFrontend       # Start backend + frontend
#   .\run-local-dev.ps1 -Setup              # First-time setup
#   .\run-local-dev.ps1 -Reset              # Reset database
# ============================================================================

param(
    [switch]$Setup,
    [switch]$Reset,
    [switch]$Help,
    [switch]$WithFrontend
)

# ============================================================================
# SHOW HELP
# ============================================================================
if ($Help) {
    Write-Host "Usage: .\run-local-dev.ps1 [command] [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  (none)           Start backend only (default)"
    Write-Host "  -WithFrontend    Start backend + frontend together"
    Write-Host "  -Setup           First-time setup (install deps, create .env, run migrations)"
    Write-Host "  -Reset           Reset database (delete and recreate)"
    Write-Host "  -Help            Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run-local-dev.ps1                  # Start backend only"
    Write-Host "  .\run-local-dev.ps1 -WithFrontend    # Start backend + frontend"
    Write-Host "  .\run-local-dev.ps1 -Setup           # Initial setup"
    Write-Host "  .\run-local-dev.ps1 -Reset           # Reset DB"
    exit 0
}

# ============================================================================
# VALIDATION
# ============================================================================

# Check if we're in the project root
if (!(Test-Path "backend")) {
    Write-Host "[ERROR] Must run from project root directory" -ForegroundColor Red
    exit 1
}

# Check if poetry is installed
if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Poetry not found. Install with: pip install poetry" -ForegroundColor Red
    exit 1
}

# ============================================================================
# SETUP
# ============================================================================
if ($Setup) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  First-Time Setup" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""

    Set-Location backend

    try {
        # Check if .env exists
        if (Test-Path ".env") {
            Write-Host "[WARNING] .env already exists" -ForegroundColor Yellow
            $confirm = Read-Host "Overwrite with .env.dev.example? (y/N)"
            if ($confirm -ne "y") {
                Write-Host "[INFO] Keeping existing .env" -ForegroundColor Blue
            } else {
                Copy-Item .env.dev.example .env
                Write-Host "[SUCCESS] Created .env from template" -ForegroundColor Green
            }
        } else {
            Copy-Item .env.dev.example .env
            Write-Host "[SUCCESS] Created .env from template" -ForegroundColor Green
        }

        # Install dependencies
        Write-Host "[INFO] Installing dependencies with Poetry..." -ForegroundColor Blue
        poetry install

        # Generate SECRET_KEY
        Write-Host "[INFO] Generating SECRET_KEY..." -ForegroundColor Blue
        $SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"

        # Update .env with generated key
        $envContent = Get-Content .env
        $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$SECRET_KEY"
        $envContent | Set-Content .env

        Write-Host "[SUCCESS] Generated and saved SECRET_KEY" -ForegroundColor Green

        # Run migrations
        Write-Host "[INFO] Running database migrations..." -ForegroundColor Blue
        poetry run alembic upgrade head
        Write-Host "[SUCCESS] Database ready!" -ForegroundColor Green

        # Create test user
        Write-Host "[INFO] Creating test user..." -ForegroundColor Blue
        poetry run python scripts/create_verified_user.py

        # Create admin user
        Write-Host "[INFO] Creating admin user..." -ForegroundColor Blue
        poetry run python scripts/create_admin.py --force

        # Load achievements
        Write-Host "[INFO] Loading achievements..." -ForegroundColor Blue
        poetry run python scripts/seed_achievements.py

        # Load cycling types
        Write-Host "[INFO] Loading cycling types..." -ForegroundColor Blue
        poetry run python scripts/seed_cycling_types.py

        Write-Host "[SUCCESS] Setup complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "[INFO] Default credentials:" -ForegroundColor Blue
        Write-Host "  Admin:  admin / AdminPass123!" -ForegroundColor Blue
        Write-Host "  User:   testuser / TestPass123!" -ForegroundColor Blue
        Write-Host ""
        Write-Host "[INFO] Start development server with: .\run-local-dev.ps1" -ForegroundColor Blue
    }
    finally {
        Set-Location ..
    }
    exit 0
}

# ============================================================================
# RESET
# ============================================================================
if ($Reset) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  Reset Database" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""

    Set-Location backend

    try {
        if (Test-Path "contravento_dev.db") {
            Write-Host "[WARNING] This will delete all data!" -ForegroundColor Yellow
            $confirm = Read-Host "Continue? (y/N)"
            if ($confirm -ne "y") {
                Write-Host "[INFO] Reset cancelled" -ForegroundColor Blue
                Set-Location ..
                exit 0
            }

            Remove-Item contravento_dev.db
            Write-Host "[SUCCESS] Deleted database file" -ForegroundColor Green
        } else {
            Write-Host "[INFO] Database file not found (already clean)" -ForegroundColor Blue
        }

        # Recreate database
        Write-Host "[INFO] Running migrations..." -ForegroundColor Blue
        poetry run alembic upgrade head
        Write-Host "[SUCCESS] Database recreated!" -ForegroundColor Green

        # Create test user
        Write-Host "[INFO] Creating test user..." -ForegroundColor Blue
        poetry run python scripts/create_verified_user.py

        # Create admin user
        Write-Host "[INFO] Creating admin user..." -ForegroundColor Blue
        poetry run python scripts/create_admin.py --force

        # Load achievements
        Write-Host "[INFO] Loading achievements..." -ForegroundColor Blue
        poetry run python scripts/seed_achievements.py

        # Load cycling types
        Write-Host "[INFO] Loading cycling types..." -ForegroundColor Blue
        poetry run python scripts/seed_cycling_types.py

        Write-Host "[SUCCESS] Database reset complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "[INFO] Default credentials:" -ForegroundColor Blue
        Write-Host "  Admin:  admin / AdminPass123!" -ForegroundColor Blue
        Write-Host "  User:   testuser / TestPass123!" -ForegroundColor Blue
    }
    finally {
        Set-Location ..
    }
    exit 0
}

# ============================================================================
# START SERVER (default)
# ============================================================================

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connection
}

# Header
Write-Host ""
Write-Host "============================================" -ForegroundColor Blue
if ($WithFrontend) {
    Write-Host "  Starting Backend + Frontend (SQLite Local)" -ForegroundColor Blue
} else {
    Write-Host "  Starting Backend Only (SQLite Local)" -ForegroundColor Blue
}
Write-Host "============================================" -ForegroundColor Blue
Write-Host ""

Set-Location backend

try {
    # Check if .env exists
    if (!(Test-Path ".env")) {
        Write-Host "[ERROR] .env not found!" -ForegroundColor Red
        Write-Host "[INFO] Run: .\run-local-dev.ps1 -Setup" -ForegroundColor Blue
        Set-Location ..
        exit 1
    }

    # Check if database exists
    if (!(Test-Path "contravento_dev.db")) {
        Write-Host "[WARNING] Database not found. Running migrations..." -ForegroundColor Yellow
        poetry run alembic upgrade head
        Write-Host "[SUCCESS] Database created!" -ForegroundColor Green
    }

    # Check if backend port is in use
    if (Test-Port -Port 8000) {
        Write-Host "[ERROR] Port 8000 is already in use!" -ForegroundColor Red
        Write-Host "[INFO] Kill the process using port 8000:" -ForegroundColor Blue
        Write-Host "  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process" -ForegroundColor Blue
        Set-Location ..
        exit 1
    }

    Write-Host "[SUCCESS] Starting backend at http://localhost:8000" -ForegroundColor Green
    Write-Host "[INFO] API Docs: http://localhost:8000/docs" -ForegroundColor Blue

    # Start uvicorn with hot reload in background
    $BackendJob = Start-Job -ScriptBlock {
        param($BackendPath)
        Set-Location $BackendPath
        poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    } -ArgumentList (Get-Location).Path

    Set-Location ..

    # Start frontend if requested
    if ($WithFrontend) {
        # Check if frontend port is in use
        if (Test-Port -Port 5173) {
            Write-Host "[ERROR] Port 5173 is already in use!" -ForegroundColor Red
            Write-Host "[INFO] Kill the process using port 5173:" -ForegroundColor Blue
            Write-Host "  Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process" -ForegroundColor Blue
            Write-Host "[INFO] Stopping backend..." -ForegroundColor Blue
            Stop-Job $BackendJob
            Remove-Job $BackendJob
            exit 1
        }

        # Check if Node.js is installed
        if (!(Get-Command node -ErrorAction SilentlyContinue)) {
            Write-Host "[ERROR] Node.js not found. Install from: https://nodejs.org/" -ForegroundColor Red
            Write-Host "[INFO] Stopping backend..." -ForegroundColor Blue
            Stop-Job $BackendJob
            Remove-Job $BackendJob
            exit 1
        }

        # Check if npm is installed
        if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
            Write-Host "[ERROR] npm not found. Install Node.js from: https://nodejs.org/" -ForegroundColor Red
            Write-Host "[INFO] Stopping backend..." -ForegroundColor Blue
            Stop-Job $BackendJob
            Remove-Job $BackendJob
            exit 1
        }

        Set-Location frontend

        # Check if .env.development exists, create from example if not
        if (!(Test-Path ".env.development")) {
            if (Test-Path ".env.development.example") {
                Write-Host "[WARNING] .env.development not found. Creating from .env.development.example..." -ForegroundColor Yellow
                Copy-Item .env.development.example .env.development
                Write-Host "[SUCCESS] Created .env.development with default values" -ForegroundColor Green
            } else {
                Write-Host "[ERROR] .env.development.example not found!" -ForegroundColor Red
                Set-Location ..
                Stop-Job $BackendJob
                Remove-Job $BackendJob
                exit 1
            }
        }

        # Check if node_modules exists
        if (!(Test-Path "node_modules")) {
            Write-Host "[WARNING] node_modules not found. Running npm install..." -ForegroundColor Yellow
            npm install
            Write-Host "[SUCCESS] Dependencies installed!" -ForegroundColor Green
        }

        Write-Host "[SUCCESS] Starting frontend at http://localhost:5173" -ForegroundColor Green
        Write-Host "[INFO] Press Ctrl+C to stop both services" -ForegroundColor Blue
        Write-Host ""

        # Start Vite dev server in background
        $FrontendJob = Start-Job -ScriptBlock {
            param($FrontendPath)
            Set-Location $FrontendPath
            npm run dev
        } -ArgumentList (Get-Location).Path

        Set-Location ..

        # Setup cleanup handler
        Register-EngineEvent PowerShell.Exiting -Action {
            Write-Host ""
            Write-Host "[INFO] Stopping services..." -ForegroundColor Blue
            Stop-Job $BackendJob -ErrorAction SilentlyContinue
            Stop-Job $FrontendJob -ErrorAction SilentlyContinue
            Remove-Job $BackendJob -ErrorAction SilentlyContinue
            Remove-Job $FrontendJob -ErrorAction SilentlyContinue
            Write-Host "[SUCCESS] Services stopped" -ForegroundColor Green
        }

        # Wait for both jobs and show their output
        try {
            while ($true) {
                Receive-Job $BackendJob
                Receive-Job $FrontendJob
                Start-Sleep -Milliseconds 100

                # Check if jobs are still running
                if ($BackendJob.State -eq 'Completed' -or $FrontendJob.State -eq 'Completed') {
                    break
                }
            }
        }
        catch {
            Write-Host ""
            Write-Host "[INFO] Stopping services..." -ForegroundColor Blue
        }
        finally {
            Stop-Job $BackendJob -ErrorAction SilentlyContinue
            Stop-Job $FrontendJob -ErrorAction SilentlyContinue
            Remove-Job $BackendJob -ErrorAction SilentlyContinue
            Remove-Job $FrontendJob -ErrorAction SilentlyContinue
            Write-Host "[SUCCESS] Services stopped" -ForegroundColor Green
        }
    } else {
        Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Blue
        Write-Host ""

        # Setup cleanup handler for backend only
        Register-EngineEvent PowerShell.Exiting -Action {
            Write-Host ""
            Write-Host "[INFO] Stopping backend..." -ForegroundColor Blue
            Stop-Job $BackendJob -ErrorAction SilentlyContinue
            Remove-Job $BackendJob -ErrorAction SilentlyContinue
            Write-Host "[SUCCESS] Backend stopped" -ForegroundColor Green
        }

        # Wait for backend job and show its output
        try {
            while ($true) {
                Receive-Job $BackendJob
                Start-Sleep -Milliseconds 100

                if ($BackendJob.State -eq 'Completed') {
                    break
                }
            }
        }
        catch {
            Write-Host ""
            Write-Host "[INFO] Stopping backend..." -ForegroundColor Blue
        }
        finally {
            Stop-Job $BackendJob -ErrorAction SilentlyContinue
            Remove-Job $BackendJob -ErrorAction SilentlyContinue
            Write-Host "[SUCCESS] Backend stopped" -ForegroundColor Green
        }
    }
}
finally {
    Set-Location ..
}
