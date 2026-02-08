# ============================================================================
# ContraVento - Frontend Server Manager
# ============================================================================
# Manages the Vite frontend server (port 5173)
#
# Usage:
#   .\run_frontend.ps1          # Start frontend server (default)
#   .\run_frontend.ps1 start    # Start frontend server
#   .\run_frontend.ps1 stop     # Stop frontend server
#   .\run_frontend.ps1 restart  # Restart frontend server
#   .\run_frontend.ps1 verify   # Check frontend status
# ============================================================================

param(
    [Parameter(Position=0, Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "verify")]
    [string]$Command = "start"
)

$PORT = 5173
$SERVER_NAME = "Frontend"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Configure-BackendPort {
    $backendPort = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8000 }
    $frontendEnv = "frontend\.env.development"

    if (!(Test-Path $frontendEnv)) {
        return  # Will be created later in Start-Server
    }

    $backendUrl = "http://localhost:$backendPort"

    # Update VITE_API_URL with current backend port
    $content = Get-Content $frontendEnv
    $newContent = $content -replace 'VITE_API_URL=.*', "VITE_API_URL=$backendUrl"
    $newContent | Set-Content $frontendEnv

    Write-Host "[SUCCESS] Configured frontend to connect to backend at $backendUrl" -ForegroundColor Green
}

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
        Write-Host "[INFO] Run: .\frontend.ps1 stop" -ForegroundColor Blue
        exit 1
    }

    # Check if we're in project root
    if (!(Test-Path "frontend")) {
        Write-Host "[ERROR] Must run from project root directory" -ForegroundColor Red
        exit 1
    }

    # Ensure Node.js is in PATH
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

    Set-Location frontend

    # Check if .env.development exists
    if (!(Test-Path ".env.development")) {
        if (Test-Path ".env.development.example") {
            Write-Host "[WARNING] .env.development not found. Creating from example..." -ForegroundColor Yellow
            Copy-Item .env.development.example .env.development
            Write-Host "[SUCCESS] Created .env.development" -ForegroundColor Green
        }
        else {
            Write-Host "[ERROR] .env.development.example not found!" -ForegroundColor Red
            Set-Location ..
            exit 1
        }
    }

    Set-Location ..

    # Configure frontend to use correct backend port
    Configure-BackendPort

    Set-Location frontend

    # Check if node_modules exists
    if (!(Test-Path "node_modules")) {
        Write-Host "[WARNING] node_modules not found. Running npm install..." -ForegroundColor Yellow
        npm install
        Write-Host "[SUCCESS] Dependencies installed!" -ForegroundColor Green
    }

    Write-Host "[SUCCESS] Starting frontend at http://localhost:$PORT" -ForegroundColor Green
    Write-Host "[INFO] Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""

    # Start server in foreground
    npm run dev

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

        # Try HTTP check
        Write-Host ""
        Write-Host "HTTP check: " -NoNewline
        try {
            # Use shorter timeout for faster response
            $response = Invoke-WebRequest -Uri "http://localhost:$PORT" -Method Get -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            Write-Host "OK (HTTP $($response.StatusCode))" -ForegroundColor Green
        }
        catch [System.Net.WebException] {
            if ($_.Exception.Message -match "timed out") {
                Write-Host "TIMEOUT (Vite is running but slow to respond)" -ForegroundColor Yellow
            }
            else {
                Write-Host "NO RESPONSE (Vite dev server may be starting)" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "ERROR ($($_.Exception.Message))" -ForegroundColor Yellow
        }

        # Check config
        Write-Host ""
        Write-Host "Config: " -NoNewline
        if (Test-Path "frontend/.env.development") {
            Write-Host "EXISTS (.env.development)" -ForegroundColor Green
        }
        else {
            Write-Host "MISSING (.env.development)" -ForegroundColor Yellow
        }

        # Check node_modules
        Write-Host "Dependencies: " -NoNewline
        if (Test-Path "frontend/node_modules") {
            Write-Host "INSTALLED" -ForegroundColor Green
        }
        else {
            Write-Host "NOT INSTALLED" -ForegroundColor Yellow
        }

        Write-Host ""
        Write-Host "[SUCCESS] $SERVER_NAME is running!" -ForegroundColor Green
    }
    else {
        Write-Host "NOT RUNNING" -ForegroundColor Red
        Write-Host ""
        Write-Host "[INFO] Start with: .\frontend.ps1 start" -ForegroundColor Blue
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
