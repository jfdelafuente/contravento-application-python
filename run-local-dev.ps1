# ============================================================================
# ContraVento - Local Development Startup Script (SQLite - No Docker)
# ============================================================================
# Quick start development server with SQLite database
# No Docker required - instant startup!
#
# 📖 Documentation: docs/deployment/modes/local-dev.md
#    For complete guide with troubleshooting and configuration details
#
# Usage:
#   .\run-local-dev.ps1                     # Start backend only
#   .\run-local-dev.ps1 -WithFrontend       # Start backend + frontend
#   .\run-local-dev.ps1 -Setup              # First-time setup
#   .\run-local-dev.ps1 -Reset              # Reset database
#   .\run-local-dev.ps1 -Verify             # Check server status
#   .\run-local-dev.ps1 -Stop [target]      # Stop servers (all/backend/frontend)
# ============================================================================

param(
    [switch]$Setup,
    [switch]$Reset,
    [switch]$Help,
    [switch]$WithFrontend,
    [switch]$Verify,
    [switch]$Stop,
    [Parameter(Position=0)]
    [ValidateSet("all", "backend", "frontend", "", $null)]
    [string]$Target = "all"
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
    Write-Host "  -Verify          Check backend and frontend server status"
    Write-Host "  -Stop [target]   Stop running servers (all/backend/frontend, default: all)"
    Write-Host "  -Help            Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run-local-dev.ps1                  # Start backend only"
    Write-Host "  .\run-local-dev.ps1 -WithFrontend    # Start backend + frontend"
    Write-Host "  .\run-local-dev.ps1 -Setup           # Initial setup"
    Write-Host "  .\run-local-dev.ps1 -Reset           # Reset DB"
    Write-Host "  .\run-local-dev.ps1 -Verify          # Check server status"
    Write-Host "  .\run-local-dev.ps1 -Stop            # Stop all servers"
    Write-Host "  .\run-local-dev.ps1 -Stop backend    # Stop backend only"
    Write-Host "  .\run-local-dev.ps1 -Stop frontend   # Stop frontend only"
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

# Ensure Node.js is in PATH (if it exists in common locations)
$nodePaths = @(
    "C:\Users\jfdelafuente\nodejs\node20",
    "C:\Program Files\nodejs",
    "C:\Program Files (x86)\nodejs"
)

foreach ($nodePath in $nodePaths) {
    if ((Test-Path $nodePath) -and ($env:Path -notlike "*$nodePath*")) {
        $env:Path += ";$nodePath"
        break
    }
}

# Check if poetry is installed
if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Poetry not found. Install with: pip install poetry" -ForegroundColor Red
    exit 1
}

# ============================================================================
# VERIFY SERVER STATUS
# ============================================================================
if ($Verify) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  Server Status Check" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""

    # Function to test HTTP endpoint
    function Test-Endpoint {
        param(
            [string]$Url,
            [int]$TimeoutSec = 3
        )
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
            return @{
                Success = $true
                StatusCode = $response.StatusCode
                Content = $response.Content
            }
        }
        catch {
            return @{
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }

    # Function to check if port is in use
    function Test-Port {
        param([int]$Port)
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $null -ne $connection
    }

    # Check Backend (port 8000)
    Write-Host "Backend Server (http://localhost:8000)" -ForegroundColor Cyan
    Write-Host "  Port 8000: " -NoNewline
    if (Test-Port -Port 8000) {
        Write-Host "LISTENING" -ForegroundColor Green

        Write-Host "  Health check: " -NoNewline
        $healthResult = Test-Endpoint -Url "http://localhost:8000/health"
        if ($healthResult.Success) {
            Write-Host "OK (HTTP $($healthResult.StatusCode))" -ForegroundColor Green

            # Parse health response
            try {
                $healthData = $healthResult.Content | ConvertFrom-Json
                Write-Host "    Status: " -NoNewline
                Write-Host "$($healthData.data.status)" -ForegroundColor Green
                Write-Host "    Environment: " -NoNewline
                Write-Host "$($healthData.data.environment)" -ForegroundColor Cyan
                Write-Host "    Timestamp: " -NoNewline
                Write-Host "$($healthData.data.timestamp)" -ForegroundColor Gray
            }
            catch {
                Write-Host "    (Could not parse health data)" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "FAILED" -ForegroundColor Red
            Write-Host "    Error: $($healthResult.Error)" -ForegroundColor Red
        }

        Write-Host "  API Docs: " -NoNewline
        $docsResult = Test-Endpoint -Url "http://localhost:8000/docs"
        if ($docsResult.Success) {
            Write-Host "AVAILABLE (HTTP $($docsResult.StatusCode))" -ForegroundColor Green
        }
        else {
            Write-Host "NOT AVAILABLE" -ForegroundColor Yellow
        }

        Write-Host "  Database: " -NoNewline
        if (Test-Path "backend/contravento_dev.db") {
            $dbSize = (Get-Item "backend/contravento_dev.db").Length
            $dbSizeKB = [math]::Round($dbSize / 1KB, 2)
            Write-Host "EXISTS ($dbSizeKB KB)" -ForegroundColor Green
        }
        else {
            Write-Host "NOT FOUND" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host "    Start with: .\run-local-dev.ps1" -ForegroundColor Gray
    }

    Write-Host ""

    # Check Frontend (port 5173)
    Write-Host "Frontend Server (http://localhost:5173)" -ForegroundColor Cyan
    Write-Host "  Port 5173: " -NoNewline
    if (Test-Port -Port 5173) {
        Write-Host "LISTENING" -ForegroundColor Green

        Write-Host "  HTTP check: " -NoNewline
        $frontendResult = Test-Endpoint -Url "http://localhost:5173"
        if ($frontendResult.Success) {
            Write-Host "OK (HTTP $($frontendResult.StatusCode))" -ForegroundColor Green
        }
        else {
            Write-Host "FAILED" -ForegroundColor Red
            Write-Host "    Error: $($frontendResult.Error)" -ForegroundColor Red
        }

        Write-Host "  Config: " -NoNewline
        if (Test-Path "frontend/.env.development") {
            Write-Host "EXISTS" -ForegroundColor Green
        }
        else {
            Write-Host "MISSING (.env.development)" -ForegroundColor Yellow
        }

        Write-Host "  node_modules: " -NoNewline
        if (Test-Path "frontend/node_modules") {
            Write-Host "EXISTS" -ForegroundColor Green
        }
        else {
            Write-Host "NOT INSTALLED" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host "    Start with: .\run-local-dev.ps1 -WithFrontend" -ForegroundColor Gray
        Write-Host "    Or manually: cd frontend && npm run dev" -ForegroundColor Gray
    }

    Write-Host ""

    # Summary
    $backendRunning = Test-Port -Port 8000
    $frontendRunning = Test-Port -Port 5173

    Write-Host "Summary:" -ForegroundColor Blue
    Write-Host "  Backend:  " -NoNewline
    if ($backendRunning) {
        Write-Host "RUNNING" -ForegroundColor Green
    } else {
        Write-Host "STOPPED" -ForegroundColor Red
    }
    Write-Host "  Frontend: " -NoNewline
    if ($frontendRunning) {
        Write-Host "RUNNING" -ForegroundColor Green
    } else {
        Write-Host "STOPPED" -ForegroundColor Red
    }

    Write-Host ""

    # Exit with appropriate code
    if ($backendRunning -and $frontendRunning) {
        Write-Host "[SUCCESS] Both servers are running!" -ForegroundColor Green
        exit 0
    }
    elseif ($backendRunning -or $frontendRunning) {
        Write-Host "[WARNING] Only one server is running" -ForegroundColor Yellow
        exit 0
    }
    else {
        Write-Host "[INFO] No servers are currently running" -ForegroundColor Blue
        exit 0
    }
}

# ============================================================================
# STOP SERVERS
# ============================================================================
if ($Stop) {
    # Use Target parameter or default to "all"
    if ([string]::IsNullOrEmpty($Target)) {
        $Target = "all"
    }

    # Normalize target
    $target = $Target.ToLower()

    # Validate target
    if ($target -notin @("all", "backend", "frontend")) {
        Write-Host "[ERROR] Invalid target: $Target" -ForegroundColor Red
        Write-Host "[INFO] Valid targets: all, backend, frontend" -ForegroundColor Blue
        exit 1
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  Stop Servers" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""

    # Function to check if port is in use
    function Test-Port {
        param([int]$Port)
        $connection = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        return $null -ne $connection
    }

    # Function to stop process on port
    function Stop-ProcessOnPort {
        param(
            [int]$Port,
            [string]$ServerName
        )

        if (Test-Port -Port $Port) {
            try {
                # Get all processes LISTENING on this port
                $processes = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop |
                            Select-Object -ExpandProperty OwningProcess |
                            Where-Object { $_ -ne 0 } |
                            Select-Object -Unique

                if ($processes.Count -eq 0) {
                    Write-Host "[WARNING] No processes found listening on port $Port" -ForegroundColor Yellow
                }

                foreach ($processId in $processes) {
                    Write-Host "  Stopping process PID: $processId..." -ForegroundColor Gray
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                }

                # Wait a bit and verify
                Start-Sleep -Milliseconds 500

                if (!(Test-Port -Port $Port)) {
                    Write-Host "[SUCCESS] $ServerName stopped (port $Port)" -ForegroundColor Green
                    return $true
                } else {
                    Write-Host "[WARNING] $ServerName may still be running on port $Port" -ForegroundColor Yellow
                    return $false
                }
            }
            catch {
                Write-Host "[ERROR] Failed to stop $ServerName on port $Port" -ForegroundColor Red
                Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
                return $false
            }
        }
        else {
            Write-Host "[INFO] $ServerName is not running on port $Port" -ForegroundColor Blue
            return $true
        }
    }

    # Stop servers based on target
    $backendStopped = $true
    $frontendStopped = $true

    if ($target -eq "all" -or $target -eq "backend") {
        Write-Host "Stopping backend server..." -ForegroundColor Cyan
        $backendStopped = Stop-ProcessOnPort -Port 8000 -ServerName "Backend"
        Write-Host ""
    }

    if ($target -eq "all" -or $target -eq "frontend") {
        Write-Host "Stopping frontend server..." -ForegroundColor Cyan
        $frontendStopped = Stop-ProcessOnPort -Port 5173 -ServerName "Frontend"
        Write-Host ""
    }

    # Summary
    Write-Host "Summary:" -ForegroundColor Blue

    if ($target -eq "all" -or $target -eq "backend") {
        Write-Host "  Backend:  " -NoNewline
        if ($backendStopped) {
            Write-Host "STOPPED" -ForegroundColor Green
        } else {
            Write-Host "FAILED" -ForegroundColor Red
        }
    }

    if ($target -eq "all" -or $target -eq "frontend") {
        Write-Host "  Frontend: " -NoNewline
        if ($frontendStopped) {
            Write-Host "STOPPED" -ForegroundColor Green
        } else {
            Write-Host "FAILED" -ForegroundColor Red
        }
    }

    Write-Host ""

    # Exit with appropriate code
    if ($backendStopped -and $frontendStopped) {
        Write-Host "[SUCCESS] All requested servers stopped!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[WARNING] Some servers failed to stop" -ForegroundColor Yellow
        exit 1
    }
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

# Store absolute paths before changing directories
$projectRoot = (Get-Location).Path
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"

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

    # Start uvicorn with hot reload in separate window
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$backendPath'; Write-Host 'ContraVento Backend Server' -ForegroundColor Cyan; Write-Host 'Running at: http://localhost:8000' -ForegroundColor Green; Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Green; Write-Host ''; poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
    )

    # Start frontend if requested
    if ($WithFrontend) {
        # Check if frontend port is in use
        if (Test-Port -Port 5173) {
            Write-Host "[ERROR] Port 5173 is already in use!" -ForegroundColor Red
            Write-Host "[INFO] Kill the process using port 5173:" -ForegroundColor Blue
            Write-Host "  Get-Process -Id (Get-NetTCPConnection -LocalPort 5173).OwningProcess | Stop-Process" -ForegroundColor Blue
            exit 1
        }

        # Check if Node.js is installed
        if (!(Get-Command node -ErrorAction SilentlyContinue)) {
            Write-Host "[ERROR] Node.js not found. Install from: https://nodejs.org/" -ForegroundColor Red
            exit 1
        }

        # Check if npm is installed
        if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
            Write-Host "[ERROR] npm not found. Install Node.js from: https://nodejs.org/" -ForegroundColor Red
            exit 1
        }

        # Check if .env.development exists, create from example if not
        if (!(Test-Path "$frontendPath\.env.development")) {
            if (Test-Path "$frontendPath\.env.development.example") {
                Write-Host "[WARNING] .env.development not found. Creating from .env.development.example..." -ForegroundColor Yellow
                Copy-Item "$frontendPath\.env.development.example" "$frontendPath\.env.development"
                Write-Host "[SUCCESS] Created .env.development with default values" -ForegroundColor Green
            } else {
                Write-Host "[ERROR] .env.development.example not found!" -ForegroundColor Red
                exit 1
            }
        }

        # Check if node_modules exists
        if (!(Test-Path "$frontendPath\node_modules")) {
            Write-Host "[WARNING] node_modules not found. Running npm install..." -ForegroundColor Yellow
            Push-Location $frontendPath
            npm install
            Pop-Location
            Write-Host "[SUCCESS] Dependencies installed!" -ForegroundColor Green
        }

        Write-Host "[SUCCESS] Starting frontend at http://localhost:5173" -ForegroundColor Green
        Write-Host ""

        # Start Vite dev server in separate window
        Start-Process powershell -ArgumentList @(
            "-NoExit",
            "-Command",
            "cd '$frontendPath'; Write-Host 'ContraVento Frontend Server' -ForegroundColor Cyan; Write-Host 'Running at: http://localhost:5173' -ForegroundColor Green; Write-Host ''; npm run dev"
        )

        Write-Host "[INFO] Backend and Frontend started in separate windows" -ForegroundColor Blue
        Write-Host "[INFO] Close the terminal windows to stop the servers" -ForegroundColor Blue
        Write-Host ""
        Write-Host "[SUCCESS] Development environment ready!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[INFO] Backend started in a separate window" -ForegroundColor Blue
        Write-Host "[INFO] Close the terminal window to stop the server" -ForegroundColor Blue
        Write-Host ""
        Write-Host "[SUCCESS] Development environment ready!" -ForegroundColor Green
    }
}
finally {
    Set-Location ..
}
