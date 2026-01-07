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

# Functions
function Print-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Print-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Print-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Print-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""
}

# Check if we're in the project root
function Check-Directory {
    if (!(Test-Path "backend")) {
        Print-Error "Must run from project root directory"
        exit 1
    }
}

# Check if poetry is installed
function Check-Poetry {
    if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
        Print-Error "Poetry not found. Install with: pip install poetry"
        exit 1
    }
}

# Setup environment
function Setup-Environment {
    Print-Header "First-Time Setup"

    Set-Location backend

    # Check if .env exists
    if (Test-Path ".env") {
        Print-Warning ".env already exists"
        $confirm = Read-Host "Overwrite with .env.dev.example? (y/N)"
        if ($confirm -ne "y") {
            Print-Info "Keeping existing .env"
        } else {
            Copy-Item .env.dev.example .env
            Print-Success "Created .env from template"
        }
    } else {
        Copy-Item .env.dev.example .env
        Print-Success "Created .env from template"
    }

    # Install dependencies
    Print-Info "Installing dependencies with Poetry..."
    poetry install

    # Generate SECRET_KEY
    Print-Info "Generating SECRET_KEY..."
    $SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"

    # Update .env with generated key
    $envContent = Get-Content .env
    $envContent = $envContent -replace "SECRET_KEY=.*", "SECRET_KEY=$SECRET_KEY"
    $envContent | Set-Content .env

    Print-Success "Generated and saved SECRET_KEY"

    # Run migrations
    Print-Info "Running database migrations..."
    poetry run alembic upgrade head
    Print-Success "Database ready!"

    # Create test user
    Print-Info "Creating test user..."
    poetry run python scripts/create_verified_user.py

    Set-Location ..

    Print-Success "Setup complete!"
    Write-Host ""
    Print-Info "Start development server with: .\run-local-dev.ps1"
}

# Reset database
function Reset-Database {
    Print-Header "Reset Database"

    Set-Location backend

    if (Test-Path "contravento_dev.db") {
        Print-Warning "This will delete all data!"
        $confirm = Read-Host "Continue? (y/N)"
        if ($confirm -ne "y") {
            Print-Info "Reset cancelled"
            Set-Location ..
            exit 0
        }

        Remove-Item contravento_dev.db
        Print-Success "Deleted database file"
    } else {
        Print-Info "Database file not found (already clean)"
    }

    # Recreate database
    Print-Info "Running migrations..."
    poetry run alembic upgrade head
    Print-Success "Database recreated!"

    # Create test user
    Print-Info "Creating test user..."
    poetry run python scripts/create_verified_user.py

    Set-Location ..

    Print-Success "Database reset complete!"
}

# Start server
function Start-Server {
    Print-Header "Starting Local Development Server"

    Set-Location backend

    # Check if .env exists
    if (!(Test-Path ".env")) {
        Print-Error ".env not found!"
        Print-Info "Run: .\run-local-dev.ps1 -Setup"
        Set-Location ..
        exit 1
    }

    # Check if database exists
    if (!(Test-Path "contravento_dev.db")) {
        Print-Warning "Database not found. Running migrations..."
        poetry run alembic upgrade head
        Print-Success "Database created!"
    }

    Print-Success "Starting server at http://localhost:8000"
    Print-Info "API Docs: http://localhost:8000/docs"
    Print-Info "Press Ctrl+C to stop"
    Write-Host ""

    # Start uvicorn with hot reload
    poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
}

# Show help
function Show-Help {
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
}

# Main
Check-Directory
Check-Poetry

if ($Help) {
    Show-Help
} elseif ($Setup) {
    Setup-Environment
} elseif ($Reset) {
    Reset-Database
} else {
    Start-Server
}
