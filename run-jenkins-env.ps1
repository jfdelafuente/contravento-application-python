# ============================================================================
# ContraVento - Preproduction Environment Helper Script (PowerShell)
# ============================================================================
# Quick commands for managing the preproduction/Jenkins environment
#
# Usage:
#   .\run-jenkins-env.ps1 [command]
#
# Commands:
#   start     - Start all services
#   stop      - Stop all services
#   restart   - Restart all services
#   logs      - View all logs
#   status    - Check services status
#   pull      - Pull latest images from Docker Hub
#   clean     - Stop and remove volumes
#   help      - Show this help message
# ============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'pull', 'clean', 'help', '')]
    [string]$Command = 'help'
)

$ErrorActionPreference = "Stop"

# Constants
$COMPOSE_FILE = "docker-compose.preproduction.yml"

# Helper Functions
function Write-Header {
    param([string]$Message)
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Error-Msg {
    param([string]$Message)
    Write-Host "✗ " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host "→ " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Warning-Msg {
    param([string]$Message)
    Write-Host "⚠ " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

# Command Implementations
function Start-Environment {
    Write-Header "Starting Preproduction Environment"

    # Check if compose file exists
    if (-not (Test-Path $COMPOSE_FILE)) {
        Write-Error-Msg "Compose file not found: $COMPOSE_FILE"
        exit 1
    }

    Write-Info "Starting services..."
    docker-compose -f $COMPOSE_FILE up -d

    Write-Info "Waiting for services to be healthy (30s)..."
    Start-Sleep -Seconds 30

    Write-Success "Services started successfully!"
    Write-Host ""
    Write-Info "Access URLs:"
    Write-Host "  - Frontend:  http://localhost:5173"
    Write-Host "  - Backend:   http://localhost:8000"
    Write-Host "  - API Docs:  http://localhost:8000/docs"
    Write-Host "  - pgAdmin:   http://localhost:5050 (admin@example.com / jenkins)"
    Write-Host ""
    Write-Info "Database:"
    Write-Host "  - Host:      localhost:5432"
    Write-Host "  - Database:  contravento_jenkins"
    Write-Host "  - User:      postgres"
    Write-Host "  - Password:  jenkins_test_password"
    Write-Host ""
    Write-Warning-Msg "This environment uses PRE-BUILT images from Docker Hub"
    Write-Info "To update images, run: .\run-jenkins-env.ps1 pull"
}

function Stop-Environment {
    Write-Header "Stopping Preproduction Environment"
    docker-compose -f $COMPOSE_FILE down
    Write-Success "Services stopped"
}

function Restart-Environment {
    Write-Header "Restarting Preproduction Environment"
    Stop-Environment
    Write-Host ""
    Start-Environment
}

function Show-Logs {
    Write-Header "Viewing Service Logs"
    Write-Info "Press Ctrl+C to exit"
    Write-Host ""
    docker-compose -f $COMPOSE_FILE logs -f
}

function Show-Status {
    Write-Header "Service Status"
    docker-compose -f $COMPOSE_FILE ps
    Write-Host ""
    Write-Info "Health checks:"

    # Backend health check
    try {
        docker-compose -f $COMPOSE_FILE exec -T backend curl -f http://localhost:8000/health 2>$null | Out-Null
        Write-Success "Backend healthy"
    } catch {
        Write-Error-Msg "Backend unhealthy"
    }

    # Frontend check (nginx doesn't have curl, just check if container is running)
    try {
        $frontendStatus = docker-compose -f $COMPOSE_FILE ps frontend 2>$null | Select-String "Up"
        if ($frontendStatus) {
            Write-Success "Frontend running"
        } else {
            Write-Error-Msg "Frontend not running"
        }
    } catch {
        Write-Error-Msg "Frontend not running"
    }

    # Database health check
    try {
        docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U postgres -d contravento_jenkins 2>$null | Out-Null
        Write-Success "Database healthy"
    } catch {
        Write-Error-Msg "Database unhealthy"
    }

    # pgAdmin check
    try {
        $pgadminStatus = docker-compose -f $COMPOSE_FILE ps pgadmin 2>$null | Select-String "Up"
        if ($pgadminStatus) {
            Write-Success "pgAdmin running"
        } else {
            Write-Error-Msg "pgAdmin not running"
        }
    } catch {
        Write-Error-Msg "pgAdmin not running"
    }
}

function Pull-Images {
    Write-Header "Pulling Latest Images from Docker Hub"

    Write-Info "Pulling backend image..."
    docker-compose -f $COMPOSE_FILE pull backend

    Write-Info "Pulling frontend image..."
    docker-compose -f $COMPOSE_FILE pull frontend

    Write-Success "Images updated successfully!"
    Write-Host ""
    Write-Warning-Msg "To apply updates, restart the environment:"
    Write-Info "  .\run-jenkins-env.ps1 restart"
}

function Clean-Environment {
    Write-Header "Cleaning Preproduction Environment"
    Write-Warning-Msg "This will remove all containers and volumes"

    $confirmation = Read-Host "Are you sure? (y/N)"
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        docker-compose -f $COMPOSE_FILE down -v
        Write-Success "Environment cleaned"
    } else {
        Write-Info "Cancelled"
    }
}

function Show-Help {
    Write-Host @"
ContraVento - Preproduction Environment Helper

Usage:
  .\run-jenkins-env.ps1 [command]

Commands:
  start     - Start all services (postgres, backend, frontend, pgadmin)
  stop      - Stop all services
  restart   - Restart all services
  logs      - View all logs (follow mode)
  status    - Check services status and health
  pull      - Pull latest images from Docker Hub
  clean     - Stop and remove all volumes
  help      - Show this help message

Examples:
  .\run-jenkins-env.ps1 start         # Start environment
  .\run-jenkins-env.ps1 logs          # View logs
  .\run-jenkins-env.ps1 pull          # Update images
  .\run-jenkins-env.ps1 restart       # Restart with new images
  .\run-jenkins-env.ps1 clean         # Clean everything

Quick Workflow:
  1. .\run-jenkins-env.ps1 start      # Start services
  2. Test manually via browser
  3. .\run-jenkins-env.ps1 logs       # Check logs if needed
  4. .\run-jenkins-env.ps1 stop       # Stop services

Update Workflow:
  1. .\run-jenkins-env.ps1 pull       # Pull latest images from Docker Hub
  2. .\run-jenkins-env.ps1 restart    # Restart with new images

Access URLs:
  - Frontend:  http://localhost:5173
  - Backend:   http://localhost:8000
  - API Docs:  http://localhost:8000/docs
  - pgAdmin:   http://localhost:5050 (admin@example.com / jenkins)

Database Connection:
  - Host:      localhost:5432
  - Database:  contravento_jenkins
  - User:      postgres
  - Password:  jenkins_test_password

Notes:
  - This environment uses PRE-BUILT images from Docker Hub
  - Images are built by GitHub Actions or Jenkins
  - VITE_* variables are hardcoded at build-time (immutable)
  - For local development, use .\deploy.ps1 local instead
"@
}

# Main Script
switch ($Command) {
    'start' {
        Start-Environment
    }
    'stop' {
        Stop-Environment
    }
    'restart' {
        Restart-Environment
    }
    'logs' {
        Show-Logs
    }
    'status' {
        Show-Status
    }
    'pull' {
        Pull-Images
    }
    'clean' {
        Clean-Environment
    }
    'help' {
        Show-Help
    }
    default {
        Write-Error-Msg "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}
