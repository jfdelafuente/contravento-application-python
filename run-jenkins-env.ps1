# ============================================================================
# ContraVento - Jenkins CI/CD Environment Helper Script (PowerShell)
# ============================================================================
# Quick commands for managing the Jenkins CI/CD environment
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
#   test      - Run all tests (backend + frontend)
#   clean     - Stop and remove volumes
#   help      - Show this help message
# ============================================================================

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'status', 'test', 'clean', 'help', '')]
    [string]$Command = 'help'
)

$ErrorActionPreference = "Stop"

# Constants
$COMPOSE_FILE = "docker-compose-jenkins.yml"

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

# Command Implementations
function Start-Environment {
    Write-Header "Starting Jenkins CI/CD Environment"

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
    Write-Host "  - pgAdmin:   http://localhost:5050 (admin@jenkins.local / jenkins)"
    Write-Host ""
    Write-Info "Database:"
    Write-Host "  - Host:      localhost:5432"
    Write-Host "  - Database:  contravento_ci"
    Write-Host "  - User:      postgres"
    Write-Host "  - Password:  jenkins_test_password"
}

function Stop-Environment {
    Write-Header "Stopping Jenkins CI/CD Environment"
    docker-compose -f $COMPOSE_FILE down
    Write-Success "Services stopped"
}

function Restart-Environment {
    Write-Header "Restarting Jenkins CI/CD Environment"
    Stop-Environment
    Start-Environment
}

function Show-Logs {
    Write-Header "Viewing Service Logs"
    Write-Info "Press Ctrl+C to exit"
    docker-compose -f $COMPOSE_FILE logs -f
}

function Show-Status {
    Write-Header "Service Status"
    docker-compose -f $COMPOSE_FILE ps
    Write-Host ""
    Write-Info "Health checks:"

    try {
        docker-compose -f $COMPOSE_FILE exec -T backend curl -f http://localhost:8000/health 2>$null | Out-Null
        Write-Success "Backend healthy"
    } catch {
        Write-Error-Msg "Backend unhealthy"
    }

    try {
        docker-compose -f $COMPOSE_FILE exec -T frontend curl -f http://localhost:5173 2>$null | Out-Null
        Write-Success "Frontend healthy"
    } catch {
        Write-Error-Msg "Frontend unhealthy"
    }

    try {
        docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U postgres -d contravento_ci 2>$null | Out-Null
        Write-Success "Database healthy"
    } catch {
        Write-Error-Msg "Database unhealthy"
    }
}

function Run-Tests {
    Write-Header "Running All Tests"

    Write-Info "Running backend tests..."
    docker-compose -f $COMPOSE_FILE exec -T backend pytest --cov=src --cov-report=term

    Write-Host ""
    Write-Info "Running frontend tests..."
    docker-compose -f $COMPOSE_FILE exec -T frontend npm test

    Write-Success "All tests completed!"
}

function Clean-Environment {
    Write-Header "Cleaning Jenkins CI/CD Environment"
    Write-Warning "This will remove all containers and volumes"

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
ContraVento - Jenkins CI/CD Environment Helper

Usage:
  .\run-jenkins-env.ps1 [command]

Commands:
  start     - Start all services (postgres, backend, frontend, pgadmin)
  stop      - Stop all services
  restart   - Restart all services
  logs      - View all logs (follow mode)
  status    - Check services status and health
  test      - Run all tests (backend + frontend)
  clean     - Stop and remove all volumes
  help      - Show this help message

Examples:
  .\run-jenkins-env.ps1 start         # Start environment
  .\run-jenkins-env.ps1 logs          # View logs
  .\run-jenkins-env.ps1 test          # Run tests
  .\run-jenkins-env.ps1 clean         # Clean everything

Quick Testing Workflow:
  1. .\run-jenkins-env.ps1 start      # Start services
  2. .\run-jenkins-env.ps1 test       # Run tests
  3. .\run-jenkins-env.ps1 stop       # Stop services

Access URLs:
  - Frontend:  http://localhost:5173
  - Backend:   http://localhost:8000
  - API Docs:  http://localhost:8000/docs
  - pgAdmin:   http://localhost:5050 (admin@jenkins.local / jenkins)

Database Connection:
  - Host:      localhost:5432
  - Database:  contravento_ci
  - User:      postgres
  - Password:  jenkins_test_password
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
    'test' {
        Run-Tests
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
