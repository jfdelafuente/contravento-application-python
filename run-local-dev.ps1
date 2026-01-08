# ============================================================================
# ContraVento - Local Development Startup Script (SQLite - No Docker)
# ============================================================================
# Quick start development server with SQLite database
# No Docker required - instant startup!
#
# Usage:
#   .\run-local-dev.ps1           # Start server
#   .\run-local-dev.ps1 -Setup    # First-time setup
#   .\run-local-dev.ps1 -Reset    # Reset database
# ============================================================================

param(
    [switch]$Setup,
    [switch]$Reset,
    [switch]$Help
)

# ============================================================================
# SHOW HELP
# ============================================================================
if ($Help) {
    Write-Host "Usage: .\run-local-dev.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  (none)     Start development server (default)"
    Write-Host "  -Setup     First-time setup (install deps, create .env, run migrations)"
    Write-Host "  -Reset     Reset database (delete and recreate)"
    Write-Host "  -Help      Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run-local-dev.ps1           # Start server"
    Write-Host "  .\run-local-dev.ps1 -Setup    # Initial setup"
    Write-Host "  .\run-local-dev.ps1 -Reset    # Reset DB"
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

        # Load achievements
        Write-Host "[INFO] Loading achievements..." -ForegroundColor Blue
        poetry run python scripts/seed_achievements.py

        Write-Host "[SUCCESS] Setup complete!" -ForegroundColor Green
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

        # Load achievements
        Write-Host "[INFO] Loading achievements..." -ForegroundColor Blue
        poetry run python scripts/seed_achievements.py

        Write-Host "[SUCCESS] Database reset complete!" -ForegroundColor Green
    }
    finally {
        Set-Location ..
    }
    exit 0
}

# ============================================================================
# START SERVER (default)
# ============================================================================
Write-Host ""
Write-Host "============================================" -ForegroundColor Blue
Write-Host "  Starting Local Development Server" -ForegroundColor Blue
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

    Write-Host "[SUCCESS] Starting server at http://localhost:8000" -ForegroundColor Green
    Write-Host "[INFO] API Docs: http://localhost:8000/docs" -ForegroundColor Blue
    Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Blue
    Write-Host ""

    # Start uvicorn with hot reload
    poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
}
finally {
    Set-Location ..
}
