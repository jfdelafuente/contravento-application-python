# ============================================================================
# ContraVento - Multi-Environment Deployment Script (PowerShell)
# ============================================================================
# Simplified deployment for all environments:
#   .\deploy.ps1 local       - Start local development
#   .\deploy.ps1 dev         - Start development/integration
#   .\deploy.ps1 staging     - Start staging/pre-production
#   .\deploy.ps1 prod        - Start production
#
# Additional commands:
#   .\deploy.ps1 <env> down  - Stop environment
#   .\deploy.ps1 <env> logs  - View logs
#   .\deploy.ps1 <env> ps    - View running containers
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Environment,

    [Parameter(Mandatory=$false)]
    [string]$Command = "up",

    [Parameter(Mandatory=$false)]
    [switch]$WithFrontend
)

# Functions
function Print-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Print-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Print-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "============================================" -ForegroundColor Blue
    Write-Host ""
}

# Check if docker-compose is installed
function Check-DockerCompose {
    if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Print-Error "docker-compose not found. Please install Docker Compose."
        exit 1
    }
}

# Validate environment
function Validate-Env {
    param([string]$Env)

    $validEnvs = @("local", "local-minimal", "dev", "staging", "prod")
    if ($validEnvs -notcontains $Env) {
        Print-Error "Invalid environment: $Env"
        Write-Host "Valid environments: local, local-minimal, dev, staging, prod"
        exit 1
    }
}

# Check if .env file exists
function Check-EnvFile {
    param([string]$Env)

    $envFile = ".env.$Env"

    if (!(Test-Path $envFile)) {
        Print-Warning ".env file not found: $envFile"
        Print-Info "Creating from example file..."

        $exampleFile = "$envFile.example"
        if (Test-Path $exampleFile) {
            Copy-Item $exampleFile $envFile
            Print-Warning "IMPORTANT: Edit $envFile and configure all variables!"
            Print-Warning "Generate strong SECRET_KEY with: python -c `"import secrets; print(secrets.token_urlsafe(64))`""
            Read-Host "Press Enter after configuring $envFile to continue..."
        } else {
            Print-Error "Example file not found: $exampleFile"
            exit 1
        }
    }
}

# Start environment
function Start-Env {
    param(
        [string]$Env,
        [bool]$WithFrontend
    )

    $composeFile = "docker-compose.$Env.yml"

    Print-Header "Starting $Env environment"

    Check-EnvFile $Env

    Print-Info "Using configuration:"
    Write-Host "  - Base: docker-compose.yml"
    Write-Host "  - Overlay: $composeFile"
    Write-Host "  - Env file: .env.$Env"
    if ($WithFrontend) {
        Write-Host "  - Frontend: ENABLED (Vite dev server)"
    }
    Write-Host ""

    # Confirmation for production
    if ($Env -eq "prod") {
        Print-Warning "You are about to deploy to PRODUCTION!"
        $confirm = Read-Host "Are you sure? (yes/no)"
        if ($confirm -ne "yes") {
            Print-Info "Deployment cancelled"
            exit 0
        }
    }

    # Pull latest images
    Print-Info "Pulling latest images..."
    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" pull

    # Build services
    Print-Info "Building services..."
    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" build

    # Start services (enable frontend if flag is set)
    Print-Info "Starting services..."
    if ($WithFrontend) {
        # Scale frontend to 1 replica to enable it
        docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" up -d --scale frontend=1
    } else {
        docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" up -d
    }

    # Wait for services to be healthy
    Print-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 10

    # Show status
    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" ps

    Print-Success "$Env environment started successfully!"

    # Environment-specific messages
    switch ($Env) {
        "local-minimal" {
            Write-Host ""
            Print-Info "Access your minimal local environment:"
            Write-Host "  Backend API:     http://localhost:8000"
            Write-Host "  API Docs:        http://localhost:8000/docs"
            if ($WithFrontend) {
                Write-Host "  Frontend:        http://localhost:5173"
            }
            Write-Host "  PostgreSQL:      localhost:5432 (use DBeaver, psql, etc.)"
            Write-Host ""
            if ($WithFrontend) {
                Print-Info "Frontend + Backend + PostgreSQL running"
            } else {
                Print-Warning "Minimal setup (PostgreSQL + Backend only)"
                Print-Info "Add frontend with: .\deploy.ps1 local-minimal -WithFrontend"
            }
            Print-Info "For MailHog, Redis, pgAdmin use: .\deploy.ps1 local"
        }
        "local" {
            Write-Host ""
            Print-Info "Access your full local environment:"
            Write-Host "  Backend API:     http://localhost:8000"
            Write-Host "  API Docs:        http://localhost:8000/docs"
            Write-Host "  MailHog UI:      http://localhost:8025"
            Write-Host "  pgAdmin:         http://localhost:5050"
            Write-Host "  PostgreSQL:      localhost:5432"
            Write-Host "  Redis:           localhost:6379"
            Write-Host ""
            Print-Info "For lighter setup use: .\deploy.ps1 local-minimal"
        }
        "dev" {
            Write-Host ""
            Print-Info "Access your dev environment:"
            Write-Host "  Backend API:     http://dev.contravento.local:8000"
            Write-Host "  API Docs:        http://dev.contravento.local:8000/docs"
        }
        "staging" {
            Write-Host ""
            Print-Info "Access your staging environment:"
            Write-Host "  Backend API:     https://staging.contravento.com"
            Write-Host "  Monitoring:      http://localhost:3000"
        }
        "prod" {
            Write-Host ""
            Print-Success "Production deployment complete!"
            Write-Host "  Backend API:     https://api.contravento.com"
            Write-Host "  Monitoring:      https://monitoring.contravento.com"
        }
    }

    Write-Host ""
    Print-Info "View logs with: .\deploy.ps1 $Env logs"
    Print-Info "Stop with: .\deploy.ps1 $Env down"
}

# Stop environment
function Stop-Env {
    param([string]$Env)

    $composeFile = "docker-compose.$Env.yml"

    Print-Header "Stopping $Env environment"

    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" down

    Print-Success "$Env environment stopped"
}

# View logs
function View-Logs {
    param([string]$Env)

    $composeFile = "docker-compose.$Env.yml"

    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" logs -f
}

# Show running containers
function Show-Ps {
    param([string]$Env)

    $composeFile = "docker-compose.$Env.yml"

    docker-compose -f docker-compose.yml -f $composeFile --env-file ".env.$Env" ps
}

# Restart environment
function Restart-Env {
    param(
        [string]$Env,
        [bool]$WithFrontend
    )

    Print-Header "Restarting $Env environment"

    Stop-Env $Env
    Start-Sleep -Seconds 2
    Start-Env $Env $WithFrontend
}

# Main
Check-DockerCompose
Validate-Env $Environment

switch ($Command.ToLower()) {
    {$_ -in "up", "start"} {
        Start-Env $Environment $WithFrontend.IsPresent
    }
    {$_ -in "down", "stop"} {
        Stop-Env $Environment
    }
    "logs" {
        View-Logs $Environment
    }
    {$_ -in "ps", "status"} {
        Show-Ps $Environment
    }
    "restart" {
        Restart-Env $Environment
    }
    default {
        Print-Error "Invalid command: $Command"
        Write-Host "Valid commands: up, down, logs, ps, restart"
        exit 1
    }
}
