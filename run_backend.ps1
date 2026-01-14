# ============================================================================
# ContraVento - Backend Server Manager
# ============================================================================
# Manages the FastAPI backend server (port 8000)
#
# Usage:
#   .\backend.ps1 start    # Start backend server
#   .\backend.ps1 stop     # Stop backend server
#   .\backend.ps1 restart  # Restart backend server
#   .\backend.ps1 verify   # Check backend status
# ============================================================================

param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "verify")]
    [string]$Command
)

$PORT = 8000
$SERVER_NAME = "Backend"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Test-Port {
    param([int]$Port)
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    return $null -ne $connection
}

function Get-ProcessOnPort {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        return $connection.OwningProcess
    }
    catch {
        return $null
    }
}

function Stop-Server {
    Write-Host ""
    Write-Host "Stopping $SERVER_NAME server (port $PORT)..." -ForegroundColor Cyan

    if (!(Test-Port -Port $PORT)) {
        Write-Host "[INFO] $SERVER_NAME is not running" -ForegroundColor Yellow
        return $true
    }

    $processId = Get-ProcessOnPort -Port $PORT
    if ($null -eq $processId) {
        Write-Host "[WARNING] Port $PORT is in use but cannot find process" -ForegroundColor Yellow
        return $false
    }

    try {
        Stop-Process -Id $processId -Force -ErrorAction Stop
        Start-Sleep -Seconds 2

        if (Test-Port -Port $PORT) {
            Write-Host "[ERROR] Failed to stop $SERVER_NAME (PID: $processId)" -ForegroundColor Red
            return $false
        }
        else {
            Write-Host "[SUCCESS] $SERVER_NAME stopped successfully" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "[ERROR] Failed to stop process: $_" -ForegroundColor Red
        return $false
    }
}

function Start-Server {
    Write-Host ""
    Write-Host "Starting $SERVER_NAME server..." -ForegroundColor Cyan

    # Check if already running
    if (Test-Port -Port $PORT) {
        Write-Host "[ERROR] Port $PORT is already in use!" -ForegroundColor Red
        Write-Host "[INFO] Run: .\backend.ps1 stop" -ForegroundColor Blue
        exit 1
    }

    # Check if we're in project root
    if (!(Test-Path "backend")) {
        Write-Host "[ERROR] Must run from project root directory" -ForegroundColor Red
        exit 1
    }

    # Check if poetry is installed
    if (!(Get-Command poetry -ErrorAction SilentlyContinue)) {
        Write-Host "[ERROR] Poetry not found. Install with: pip install poetry" -ForegroundColor Red
        exit 1
    }

    Set-Location backend

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

    Write-Host "[SUCCESS] Starting backend at http://localhost:$PORT" -ForegroundColor Green
    Write-Host "[INFO] API Docs: http://localhost:$PORT/docs" -ForegroundColor Blue
    Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""

    # Start server in foreground
    poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port $PORT

    Set-Location ..
}

function Verify-Server {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  $SERVER_NAME Server Status" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""

    Write-Host "Port ${PORT}: " -NoNewline
    if (Test-Port -Port $PORT) {
        Write-Host "LISTENING" -ForegroundColor Green

        # Try to get process info
        $processId = Get-ProcessOnPort -Port $PORT
        if ($processId) {
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  Process: $($process.ProcessName) (PID: $processId)" -ForegroundColor Gray
                Write-Host "  Started: $($process.StartTime)" -ForegroundColor Gray
            }
        }

        # Try health check
        Write-Host ""
        Write-Host "Health check: " -NoNewline
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$PORT/health" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            Write-Host "OK (HTTP $($response.StatusCode))" -ForegroundColor Green

            $health = $response.Content | ConvertFrom-Json
            Write-Host "  Status: $($health.status)" -ForegroundColor Gray
            Write-Host "  Environment: $($health.environment)" -ForegroundColor Gray
        }
        catch {
            Write-Host "FAILED" -ForegroundColor Red
            Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        }

        # Check API docs
        Write-Host ""
        Write-Host "API Docs: " -NoNewline
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$PORT/docs" -Method Get -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
            Write-Host "AVAILABLE (HTTP $($response.StatusCode))" -ForegroundColor Green
        }
        catch {
            Write-Host "NOT AVAILABLE" -ForegroundColor Yellow
        }

        # Check database
        Write-Host ""
        Write-Host "Database: " -NoNewline
        if (Test-Path "backend/contravento_dev.db") {
            $dbSize = (Get-Item "backend/contravento_dev.db").Length / 1KB
            Write-Host "EXISTS ($([math]::Round($dbSize, 0)) KB)" -ForegroundColor Green
        }
        else {
            Write-Host "NOT FOUND" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "[SUCCESS] $SERVER_NAME is running!" -ForegroundColor Green
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host ""
        Write-Host "[INFO] Start with: .\backend.ps1 start" -ForegroundColor Blue
    }

    Write-Host ""
}

function Restart-Server {
    Write-Host ""
    Write-Host "Restarting $SERVER_NAME server..." -ForegroundColor Cyan

    $stopped = Stop-Server

    if ($stopped -or !(Test-Port -Port $PORT)) {
        Start-Sleep -Seconds 1
        Start-Server
    }
    else {
        Write-Host "[ERROR] Cannot restart - failed to stop server" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# MAIN
# ============================================================================

switch ($Command) {
    "start" {
        Start-Server
    }
    "stop" {
        Stop-Server
        Write-Host ""
    }
    "verify" {
        Verify-Server
    }
    "restart" {
        Restart-Server
    }
}
